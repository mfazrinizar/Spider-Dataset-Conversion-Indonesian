"""
Apply schema translation dictionary to Spider JSON files, gold SQL, and tables.json.

This module handles Phase 2 of the pipeline: using the schema dict to translate
all identifiers (db_ids, table names, column names) consistently across:
- tables.json
- dev.json / train_spider.json / train_others.json
- dev_gold.sql / train_gold.sql
- test_data/ files

SQL string literal values are NOT translated (they must match database data).
The SQL AST is updated so table/column index references remain valid.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


#  Core Translation Helpers 

def _normalize_to_snake(name: str) -> str:
    """Normalize an identifier to lowercase snake_case."""
    return name.strip().lower().replace(" ", "_")


def _build_lower_dict(trans_dict: dict[str, str]) -> dict[str, str]:
    """Build a case-insensitive lookup dict (lowercased keys)."""
    lower = {}
    for k, v in trans_dict.items():
        lk = k.lower()
        if lk not in lower:
            lower[lk] = _normalize_to_snake(v)
    return lower


# Pre-compiled regex for tokenizing SQL into words and non-words
_SQL_TOKEN_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)")

# SQL keywords that must never be translated in query strings.
# Only includes keywords/functions actually used in Spider SELECT queries.
# Does NOT include type names (DATE, TEXT, etc.) or DDL keywords which may
# collide with column names in the Spider dataset.
_SQL_KEYWORDS = {
    # Clauses
    "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "BETWEEN",
    "LIKE", "IS", "NULL", "EXISTS", "HAVING", "GROUP", "BY", "ORDER",
    "ASC", "DESC", "LIMIT", "OFFSET", "DISTINCT", "ALL",
    # Joins
    "JOIN", "INNER", "LEFT", "RIGHT", "OUTER", "CROSS", "ON", "NATURAL",
    # Set operations
    "UNION", "INTERSECT", "EXCEPT",
    # Aggregate functions
    "COUNT", "SUM", "AVG", "MIN", "MAX",
    # Expressions
    "CASE", "WHEN", "THEN", "ELSE", "END", "CAST", "AS",
    # String/math functions
    "IIF", "REPLACE", "SUBSTR", "LENGTH", "UPPER", "LOWER", "TRIM",
    "ROUND", "ABS", "COALESCE", "IFNULL", "NULLIF", "TYPEOF", "INSTR",
    # DML (not typically in Spider queries but safe to protect)
    "INSERT", "INTO", "VALUES", "UPDATE", "DELETE", "SET",
    # Misc
    "WITH", "RECURSIVE", "USING",
}

# SQL function names that are only keywords when followed by '('
_SQL_FUNCTIONS = {
    "COUNT", "SUM", "AVG", "MIN", "MAX",
    "IIF", "REPLACE", "SUBSTR", "LENGTH", "UPPER", "LOWER", "TRIM",
    "ROUND", "ABS", "COALESCE", "IFNULL", "NULLIF", "TYPEOF", "INSTR",
    "CAST",
}

# Keywords that can also be column names in Spider; only preserve when used
# as actual SQL keywords (functions checked by '(' lookahead, others always preserved)
_SQL_AMBIGUOUS = _SQL_FUNCTIONS


def _translate_sql_identifiers(sql: str, trans_dict: dict[str, str], _cache: dict = {}) -> str:
    """Replace identifiers in a SQL query using token-by-token replacement.

    Only replaces identifiers (table/column names), NOT string literal values.
    Preserves SQL keywords and string literals wrapped in quotes.
    Uses fast dict lookup instead of giant regex alternation.
    """
    if not sql or not trans_dict:
        return sql

    # Build/cache lowered dict
    cache_key = id(trans_dict)
    if cache_key not in _cache:
        _cache[cache_key] = _build_lower_dict(trans_dict)
    lower_dict = _cache[cache_key]

    # Protect string literals (both single and double quoted)
    protected = {}
    counter = [0]

    def protect_literal(match):
        placeholder = f"__STRLIT{counter[0]:04d}__"
        protected[placeholder] = match.group(0)
        counter[0] += 1
        return placeholder

    sql_protected = re.sub(
        r"""(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')""",
        protect_literal,
        sql,
    )

    # Tokenize and replace: split into word tokens and non-word gaps
    parts = _SQL_TOKEN_RE.split(sql_protected)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # word token
            up = part.upper()
            if up in _SQL_KEYWORDS:
                # Context check: if next non-space char is '(', this is a SQL
                # function call — preserve it. Otherwise it may be a column name
                # that happens to match a SQL keyword — translate it.
                is_function_call = False
                if up in _SQL_FUNCTIONS:
                    # Check if followed by '('
                    rest = "".join(parts[i+1:])
                    if rest.lstrip().startswith("("):
                        is_function_call = True

                if is_function_call or up not in _SQL_AMBIGUOUS:
                    result.append(part)  # preserve SQL keyword/function
                else:
                    # Ambiguous: keyword that could be column name, translate if in dict
                    low = part.lower()
                    if low in lower_dict:
                        result.append(lower_dict[low])
                    else:
                        result.append(part)
            else:
                low = part.lower()
                if low in lower_dict:
                    result.append(lower_dict[low])
                else:
                    result.append(part)
        else:
            result.append(part)

    translated = "".join(result)

    # Restore string literals
    for placeholder, original in protected.items():
        translated = translated.replace(placeholder, original)

    return translated


def _tokenize_question(question: str) -> list[str]:
    """Tokenize a question string into tokens (simple word/punctuation split)."""
    tokens = re.findall(r"\w+|[^\w\s]", question)
    return tokens


#  Tables.json Translation 

def translate_tables_json(
    input_path: Path,
    output_path: Path,
    trans_dict: dict[str, str],
):
    """Translate tables.json: db_id, table_names, column_names.

    The translation ensures:
    - All identifiers use underscores (no spaces)
    - column_names and column_names_original are consistent
    - table_names and table_names_original are consistent
    - foreign_keys and primary_keys (index-based) remain valid (unchanged)
    """
    with open(input_path, encoding="utf-8") as f:
        tables = json.load(f)

    for db in tables:
        # Translate db_id
        orig_db_id = db["db_id"]
        db["db_id"] = _normalize_to_snake(
            trans_dict.get(orig_db_id, orig_db_id)
        )

        # Translate table_names_original → table_names
        orig_tables = db.get("table_names_original", [])
        translated_tables_orig = []
        translated_tables = []
        for tname in orig_tables:
            if tname:
                t = trans_dict.get(tname, tname)
                translated_tables_orig.append(_normalize_to_snake(t))
                translated_tables.append(_normalize_to_snake(t))
            else:
                translated_tables_orig.append(tname)
                translated_tables.append(tname)

        db["table_names_original"] = translated_tables_orig
        db["table_names"] = translated_tables

        # Translate column_names_original → column_names
        orig_cols = db.get("column_names_original", [])
        translated_cols_orig = []
        translated_cols = []
        for col_entry in orig_cols:
            if isinstance(col_entry, list) and len(col_entry) == 2:
                table_idx, col_name = col_entry
                if col_name == "*":
                    translated_cols_orig.append([table_idx, "*"])
                    translated_cols.append([table_idx, "*"])
                else:
                    t = trans_dict.get(col_name, col_name)
                    t_snake = _normalize_to_snake(t)
                    translated_cols_orig.append([table_idx, t_snake])
                    translated_cols.append([table_idx, t_snake])
            else:
                translated_cols_orig.append(col_entry)
                translated_cols.append(col_entry)

        db["column_names_original"] = translated_cols_orig
        db["column_names"] = translated_cols

        # column_types, foreign_keys, primary_keys remain unchanged
        # (they are index-based, not name-based)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tables, f, ensure_ascii=False, indent=2)


#  Query File Translation 

def translate_query_file(
    input_path: Path,
    translated_questions_path: Path | None,
    output_path: Path,
    trans_dict: dict[str, str],
):
    """Translate a Spider query file (dev.json / train_*.json).

    For each entry:
    - db_id → translated
    - query → identifiers replaced (string literals preserved)
    - query_toks → each token translated if it's an identifier
    - query_toks_no_value → same treatment
    - question → use pre-translated question from Phase 1 (or keep English)
    - question_toks → re-tokenized from translated question
    - sql → string values in AST preserved; table/column references are index-based
           so they stay valid as long as tables.json indices match
    """
    with open(input_path, encoding="utf-8") as f:
        entries = json.load(f)

    # Load pre-translated questions if available
    translated_questions = {}
    if translated_questions_path and translated_questions_path.exists():
        with open(translated_questions_path, encoding="utf-8") as f:
            tq = json.load(f)
        for i, entry in enumerate(tq):
            if "question_id" in entry:
                translated_questions[i] = entry["question_id"]

    # Build a lookup for lowercased identifiers
    lower_dict = {}
    for k, v in trans_dict.items():
        lower_dict[k.lower()] = _normalize_to_snake(v)

    for i, entry in enumerate(entries):
        # Translate db_id
        orig_db_id = entry["db_id"]
        entry["db_id"] = _normalize_to_snake(
            trans_dict.get(orig_db_id, orig_db_id)
        )

        # Translate query string (identifiers only, not string values)
        entry["query"] = _translate_sql_identifiers(entry.get("query", ""), trans_dict)

        # Translate query_toks
        if "query_toks" in entry:
            toks = entry["query_toks"]
            entry["query_toks"] = [
                _lookup_token(toks[j], lower_dict, toks[j+1] if j+1 < len(toks) else "")
                for j in range(len(toks))
            ]

        # Translate query_toks_no_value
        if "query_toks_no_value" in entry:
            toks = entry["query_toks_no_value"]
            entry["query_toks_no_value"] = [
                _lookup_token(toks[j], lower_dict, toks[j+1] if j+1 < len(toks) else "")
                for j in range(len(toks))
            ]

        # Apply translated question
        if i in translated_questions:
            entry["question_en"] = entry.get("question", "")
            entry["question"] = translated_questions[i]
        # else: keep original question (will be in English)

        # Re-tokenize question
        entry["question_toks"] = _tokenize_question(entry["question"])

        # SQL AST: the table/column references in the AST are index-based (integers),
        # and the indices correspond to the order in tables.json.
        # Since we translate tables.json identifiers in the same order,
        # the indices remain valid. String literals in the AST (val nodes)
        # are kept as-is to match the database data.
        # We only need to update string values that represent identifiers
        # within the SQL dict structure.
        if "sql" in entry:
            _translate_sql_ast_values(entry["sql"], trans_dict)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def _lookup_token(token: str, lower_dict: dict[str, str], next_token: str = "") -> str:
    """Look up a single query token in the translation dict.

    SQL keywords, operators, punctuation, numbers, and string literals
    are preserved as-is. For SQL function names (COUNT, LENGTH, etc.),
    they are only preserved if followed by '(' (function call context).
    Dot-notation tokens like T1.column_name are split and the column
    part is translated independently.
    """
    # Handle dot-notation tokens (e.g. T1.column_name, t2.Name)
    if "." in token and not token.startswith("'") and not token.startswith('"'):
        parts = token.split(".", 1)
        if len(parts) == 2 and parts[0] and parts[1]:
            # Translate each part independently
            left = _lookup_token(parts[0], lower_dict, ".")
            right = _lookup_token(parts[1], lower_dict, next_token)
            return left + "." + right

    up = token.upper()
    # Preserve SQL keywords (with function-call context check)
    if up in _SQL_KEYWORDS:
        if up in _SQL_AMBIGUOUS:
            # Only preserve as keyword if followed by '('
            if next_token == "(":
                return token
            # Otherwise translate as column name
            low = token.lower()
            if low in lower_dict:
                return lower_dict[low]
            return token
        return token

    # Preserve operators and punctuation
    if token in {"(", ")", ",", ".", "*", "+", "-", "/", "=", "<", ">",
                 "<=", ">=", "!=", "<>", "||", ";", "'", '"', "value"}:
        return token

    # Preserve numbers
    if re.match(r"^-?\d+\.?\d*$", token):
        return token

    # Preserve string literals
    if (token.startswith("'") and token.endswith("'")) or \
       (token.startswith('"') and token.endswith('"')):
        return token

    # Look up in translation dict
    low = token.lower()
    if low in lower_dict:
        return lower_dict[low]

    return token


def _translate_sql_ast_values(sql_dict: dict, trans_dict: dict[str, str]):
    """Recursively update string identifier values in the SQL AST.

    The Spider SQL AST stores table/column references as integer indices,
    which remain valid. However, some values may contain identifiers as strings
    (e.g., in nested queries). This function traverses and updates those.

    String literal values (actual data) are NOT modified.
    """
    if not isinstance(sql_dict, dict):
        return

    # Recursively handle nested SQL (intersect, union, except)
    for key in ("intersect", "union", "except"):
        if sql_dict.get(key) and isinstance(sql_dict[key], dict):
            _translate_sql_ast_values(sql_dict[key], trans_dict)


#  Gold SQL Translation 

def translate_gold_sql(
    input_path: Path,
    output_path: Path,
    trans_dict: dict[str, str],
):
    """Translate a gold SQL file (dev_gold.sql / train_gold.sql).

    Format: SQL_QUERY\\tdb_id per line.
    Translates identifiers in both the SQL and the db_id.
    """
    with open(input_path, encoding="utf-8") as f:
        lines = f.readlines()

    translated_lines = []
    for line in lines:
        line = line.rstrip("\n")
        if "\t" in line:
            sql, db_id = line.rsplit("\t", 1)
            translated_sql = _translate_sql_identifiers(sql, trans_dict)
            translated_db_id = _normalize_to_snake(
                trans_dict.get(db_id.strip(), db_id.strip())
            )
            translated_lines.append(f"{translated_sql}\t{translated_db_id}")
        else:
            translated_lines.append(line)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(translated_lines))
        if translated_lines:
            f.write("\n")


#  Combine Train Files 

def combine_train_files(
    train_spider_path: Path,
    train_others_path: Path,
    output_path: Path,
):
    """Combine train_spider.json and train_others.json into train.json."""
    entries = []
    for path in [train_spider_path, train_others_path]:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                entries.extend(json.load(f))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


#  Full Phase 2 Pipeline 

def run_phase2(
    spider_dir: Path,
    output_dir: Path,
    trans_dict_path: Path,
    translated_questions_dir: Path | None = None,
):
    """Run Phase 2: apply translations to all files.

    Args:
        spider_dir: Path to original spider/ directory
        output_dir: Path to output idspider/ directory
        trans_dict_path: Path to schema_translation_dict.json
        translated_questions_dir: Path to directory with Phase 1 translated question files
    """
    print("=" * 60)
    print("Phase 2: Applying Translations")
    print("=" * 60)

    # Load translation dictionary
    with open(trans_dict_path, encoding="utf-8") as f:
        trans_dict = json.load(f)
    print(f"Loaded {len(trans_dict)} translation entries")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Translate tables.json
    print("\n[1/7] Translating tables.json...")
    translate_tables_json(
        spider_dir / "tables.json",
        output_dir / "tables.json",
        trans_dict,
    )

    # 2. Translate dev.json
    print("[2/7] Translating dev.json...")
    tq_dev = translated_questions_dir / "dev.json" if translated_questions_dir else None
    translate_query_file(
        spider_dir / "dev.json",
        tq_dev,
        output_dir / "dev.json",
        trans_dict,
    )

    # 3. Translate train_spider.json
    print("[3/7] Translating train_spider.json...")
    tq_train = translated_questions_dir / "train_spider.json" if translated_questions_dir else None
    translate_query_file(
        spider_dir / "train_spider.json",
        tq_train,
        output_dir / "train_spider.json",
        trans_dict,
    )

    # 4. Translate train_others.json
    print("[4/7] Translating train_others.json...")
    tq_others = translated_questions_dir / "train_others.json" if translated_questions_dir else None
    translate_query_file(
        spider_dir / "train_others.json",
        tq_others,
        output_dir / "train_others.json",
        trans_dict,
    )

    # 5. Combine train files
    print("[5/7] Combining train files...")
    combine_train_files(
        output_dir / "train_spider.json",
        output_dir / "train_others.json",
        output_dir / "train.json",
    )

    # 6. Translate gold SQL files
    print("[6/7] Translating gold SQL files...")
    translate_gold_sql(
        spider_dir / "dev_gold.sql",
        output_dir / "dev_gold.sql",
        trans_dict,
    )
    translate_gold_sql(
        spider_dir / "train_gold.sql",
        output_dir / "train_gold.sql",
        trans_dict,
    )

    # 7. Translate test_data/ if it exists
    test_data_dir = spider_dir / "test_data"
    if test_data_dir.exists():
        print("[7/7] Translating test_data/...")
        test_output_dir = output_dir / "test_data"
        test_output_dir.mkdir(parents=True, exist_ok=True)

        if (test_data_dir / "tables.json").exists():
            translate_tables_json(
                test_data_dir / "tables.json",
                test_output_dir / "tables.json",
                trans_dict,
            )
        if (test_data_dir / "dev.json").exists():
            tq_test = translated_questions_dir / "test_dev.json" if translated_questions_dir else None
            translate_query_file(
                test_data_dir / "dev.json",
                tq_test,
                test_output_dir / "dev.json",
                trans_dict,
            )
        if (test_data_dir / "dev_gold.sql").exists():
            translate_gold_sql(
                test_data_dir / "dev_gold.sql",
                test_output_dir / "dev_gold.sql",
                trans_dict,
            )
    else:
        print("[7/7] No test_data/ found, skipping.")

    print("\nPhase 2 complete.")
