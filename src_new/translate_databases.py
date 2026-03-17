"""
Translate SQLite database files: rename tables and columns.

This module handles Phase 3 of the pipeline: creating translated copies
of all SQLite databases with renamed schema elements.

For each database:
1. Copy the original .sqlite file
2. Rename columns using ALTER TABLE RENAME COLUMN (SQLite 3.25+)
3. Rename tables using ALTER TABLE RENAME TO
4. Rename the folder and file to match the translated db_id

Data values are NOT modified — only schema identifiers change.
"""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm


_IDENT_TOKEN_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)")
_SQL_STRING_LITERAL_RE = re.compile(r"'(?:[^'\\]|\\.)*'")
_SQL_KEYWORDS = {
    "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "BETWEEN",
    "LIKE", "IS", "NULL", "EXISTS", "HAVING", "GROUP", "BY", "ORDER",
    "ASC", "DESC", "LIMIT", "OFFSET", "JOIN", "INNER", "LEFT", "RIGHT",
    "OUTER", "CROSS", "ON", "AS", "DISTINCT", "ALL", "UNION",
    "INTERSECT", "EXCEPT", "COUNT", "SUM", "AVG", "MIN", "MAX",
    "CASE", "WHEN", "THEN", "ELSE", "END", "CAST", "CREATE", "TABLE",
    "VIEW", "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "INSERT", "INTO",
    "VALUES", "UPDATE", "SET", "DELETE", "ALTER", "ADD", "DROP",
}


def get_sqlite_tables(conn: sqlite3.Connection) -> list[str]:
    """Get all table names from a SQLite database."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    return [row[0] for row in cursor.fetchall()]


def get_sqlite_views(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    """Get all views as (name, sql) pairs."""
    cursor = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='view'"
    )
    return [(row[0], row[1]) for row in cursor.fetchall() if row[1]]


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> list[str]:
    """Get column names for a table."""
    cursor = conn.execute(f'PRAGMA table_info("{table_name}")')
    return [row[1] for row in cursor.fetchall()]


def translate_single_database(
    src_sqlite: Path,
    dst_sqlite: Path,
    trans_dict: dict[str, str],
) -> list[str]:
    """Translate a single SQLite database.

    1. Copy source to destination
    2. Drop all views (they reference old names)
    3. Rename columns in each table
    4. Rename tables
    5. Recreate views with translated SQL

    Returns list of error messages (empty if successful).
    """
    errors = []

    # Copy source to destination
    dst_sqlite.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_sqlite, dst_sqlite)

    # Build case-insensitive lookup
    lower_dict = {}
    for k, v in trans_dict.items():
        lower_dict[k.lower()] = v.lower().replace(" ", "_")

    try:
        conn = sqlite3.connect(str(dst_sqlite))
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA foreign_keys=OFF")

        # Step 1: Drop all views
        views = get_sqlite_views(conn)
        for view_name, _ in views:
            try:
                conn.execute(f'DROP VIEW IF EXISTS "{view_name}"')
            except sqlite3.Error as e:
                errors.append(f"Drop view '{view_name}': {e}")
        conn.commit()

        # Step 2: Rename columns in each table
        tables = get_sqlite_tables(conn)
        for table_name in tables:
            columns = get_table_columns(conn, table_name)
            seen_columns = set()

            for col_name in columns:
                new_col = lower_dict.get(col_name.lower(), col_name)
                new_col = new_col.replace(" ", "_")

                if new_col == col_name:
                    seen_columns.add(new_col.lower())
                    continue

                # Check for duplicate column name in this table
                if new_col.lower() in seen_columns:
                    errors.append(
                        f"Column collision in '{table_name}': "
                        f"'{col_name}' → '{new_col}' (already exists)"
                    )
                    seen_columns.add(col_name.lower())
                    continue

                try:
                    # SQLite is case-insensitive, so renaming case-only
                    # differences requires an intermediate name
                    if new_col.lower() == col_name.lower():
                        temp_col = f"_tmp_rename_{col_name}"
                        conn.execute(
                            f'ALTER TABLE "{table_name}" RENAME COLUMN "{col_name}" TO "{temp_col}"'
                        )
                        conn.execute(
                            f'ALTER TABLE "{table_name}" RENAME COLUMN "{temp_col}" TO "{new_col}"'
                        )
                    else:
                        conn.execute(
                            f'ALTER TABLE "{table_name}" RENAME COLUMN "{col_name}" TO "{new_col}"'
                        )
                    seen_columns.add(new_col.lower())
                except sqlite3.Error as e:
                    errors.append(f"Rename column '{table_name}'.'{col_name}' → '{new_col}': {e}")
                    seen_columns.add(col_name.lower())

            conn.commit()

        # Step 3: Rename tables
        tables = get_sqlite_tables(conn)  # refresh after column renames
        renamed_tables = {}  # old_name → new_name
        for table_name in tables:
            new_table = lower_dict.get(table_name.lower(), table_name)
            new_table = new_table.replace(" ", "_")

            if new_table == table_name:
                renamed_tables[table_name] = table_name
                continue

            try:
                # SQLite is case-insensitive for table names, so renaming
                # "Genre" to "genre" requires an intermediate name
                if new_table.lower() == table_name.lower():
                    temp_name = f"_tmp_rename_{table_name}"
                    conn.execute(f'ALTER TABLE "{table_name}" RENAME TO "{temp_name}"')
                    conn.execute(f'ALTER TABLE "{temp_name}" RENAME TO "{new_table}"')
                else:
                    conn.execute(f'ALTER TABLE "{table_name}" RENAME TO "{new_table}"')
                renamed_tables[table_name] = new_table
            except sqlite3.Error as e:
                errors.append(f"Rename table '{table_name}' → '{new_table}': {e}")
                renamed_tables[table_name] = table_name

        conn.commit()

        # Step 4: Recreate views with translated SQL
        for view_name, view_sql in views:
            if not view_sql:
                continue
            translated_sql = _translate_view_sql(view_sql, lower_dict, renamed_tables)
            try:
                conn.execute(translated_sql)
            except sqlite3.Error as e:
                errors.append(f"Recreate view '{view_name}': {e}")

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        errors.append(f"Database error: {e}")

    return errors


def _translate_view_sql(
    view_sql: str,
    lower_dict: dict[str, str],
    renamed_tables: dict[str, str],
) -> str:
    """Translate identifiers in a view's CREATE statement."""
    # Replace table names in the SQL
    result = view_sql
    for old_name, new_name in sorted(renamed_tables.items(), key=lambda x: len(x[0]), reverse=True):
        if old_name != new_name:
            result = re.sub(
                rf"\b{re.escape(old_name)}\b",
                new_name,
                result,
                flags=re.IGNORECASE,
            )

    # Replace the view name itself
    # Pattern: CREATE VIEW "name" / CREATE VIEW name
    match = re.match(r'(CREATE\s+VIEW\s+)(?:"([^"]+)"|(\S+))', result, re.IGNORECASE)
    if match:
        prefix = match.group(1)
        view_name = match.group(2) or match.group(3)
        new_view_name = lower_dict.get(view_name.lower(), view_name)
        result = f'{prefix}"{new_view_name}"{result[match.end():]}'

    return result


def translate_all_databases(
    src_database_dir: Path,
    dst_database_dir: Path,
    trans_dict: dict[str, str],
    checkpoint_path: Path | None = None,
) -> dict:
    """Translate all SQLite databases in a directory.

    For each database folder:
    1. Map old folder/file name to translated name
    2. Copy and translate the .sqlite file
    3. Copy schema.sql if present (translated)
    4. Track errors per database

    Returns summary dict with stats and errors.
    """
    if not src_database_dir.exists():
        print(f"  Source directory not found: {src_database_dir}")
        return {"skipped": True}

    # Build case-insensitive lookup
    lower_dict = {}
    for k, v in trans_dict.items():
        lower_dict[k.lower()] = v.lower().replace(" ", "_")

    # Load checkpoint if available
    completed = set()
    if checkpoint_path and checkpoint_path.exists():
        with open(checkpoint_path, encoding="utf-8") as f:
            completed = set(json.load(f).get("completed", []))

    # Get all database directories
    db_dirs = sorted([
        d for d in src_database_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])

    all_errors = {}
    dst_database_dir.mkdir(parents=True, exist_ok=True)

    for db_dir in tqdm(db_dirs, desc="Translating databases"):
        db_name = db_dir.name
        if db_name in completed:
            continue

        # Translated folder/file name
        new_db_name = lower_dict.get(db_name.lower(), db_name)
        new_db_name = new_db_name.replace(" ", "_")

        dst_dir = dst_database_dir / new_db_name
        dst_dir.mkdir(parents=True, exist_ok=True)

        # Find .sqlite file
        sqlite_files = list(db_dir.glob("*.sqlite"))
        if not sqlite_files:
            all_errors[db_name] = ["No .sqlite file found"]
            continue

        src_sqlite = sqlite_files[0]
        dst_sqlite = dst_dir / f"{new_db_name}.sqlite"

        # Translate the database
        errors = translate_single_database(src_sqlite, dst_sqlite, trans_dict)
        if errors:
            all_errors[db_name] = errors

        # Copy schema.sql if present (translate identifiers in it)
        schema_sql = db_dir / "schema.sql"
        if schema_sql.exists():
            _translate_schema_sql_file(schema_sql, dst_dir / "schema.sql", trans_dict)

        # Update checkpoint
        completed.add(db_name)
        if checkpoint_path:
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump({"completed": sorted(completed)}, f)

    return {
        "total": len(db_dirs),
        "completed": len(completed),
        "errors": all_errors,
    }


def _translate_schema_sql_file(
    src_path: Path,
    dst_path: Path,
    trans_dict: dict[str, str],
):
    """Translate identifiers in a schema.sql file."""
    try:
        with open(src_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return

    # Build case-insensitive lookup once
    lower_dict = {}
    for k, v in trans_dict.items():
        lower_dict[k.lower()] = v.lower().replace(" ", "_")

    def translate_segment(segment: str) -> str:
        parts = _IDENT_TOKEN_RE.split(segment)
        out = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                if part.upper() in _SQL_KEYWORDS:
                    out.append(part)
                else:
                    out.append(lower_dict.get(part.lower(), part))
            else:
                out.append(part)
        return "".join(out)

    # Translate only non-literal segments and keep single-quoted strings intact.
    chunks = []
    last_end = 0
    for m in _SQL_STRING_LITERAL_RE.finditer(content):
        if m.start() > last_end:
            chunks.append(translate_segment(content[last_end:m.start()]))
        chunks.append(m.group(0))
        last_end = m.end()
    if last_end < len(content):
        chunks.append(translate_segment(content[last_end:]))

    translated = "".join(chunks)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(translated)


#  Phase 3 Entry Point 

def run_phase3(
    spider_dir: Path,
    output_dir: Path,
    trans_dict_path: Path,
):
    """Run Phase 3: translate all SQLite databases.

    Translates both database/ and test_database/ directories.
    """
    print("=" * 60)
    print("Phase 3: Translating SQLite Databases")
    print("=" * 60)

    with open(trans_dict_path, encoding="utf-8") as f:
        trans_dict = json.load(f)
    print(f"Loaded {len(trans_dict)} translation entries")

    # Translate main databases
    print("\nTranslating database/ ...")
    checkpoint = output_dir / "database" / "_checkpoint.json"
    result = translate_all_databases(
        spider_dir / "database",
        output_dir / "database",
        trans_dict,
        checkpoint,
    )
    if result.get("errors"):
        print(f"  {len(result['errors'])} databases had errors")
        for db, errs in list(result["errors"].items())[:5]:
            print(f"    {db}: {errs[0]}")
    else:
        print(f"  All {result.get('total', 0)} databases translated successfully")

    # Translate test databases
    test_db_dir = spider_dir / "test_database"
    if test_db_dir.exists():
        print("\nTranslating test_database/ ...")
        checkpoint = output_dir / "test_database" / "_checkpoint.json"
        result = translate_all_databases(
            test_db_dir,
            output_dir / "test_database",
            trans_dict,
            checkpoint,
        )
        if result.get("errors"):
            print(f"  {len(result['errors'])} databases had errors")
        else:
            print(f"  All {result.get('total', 0)} databases translated successfully")
    else:
        print("\nNo test_database/ found, skipping.")

    # Clean up checkpoint files
    for ck in [output_dir / "database" / "_checkpoint.json",
               output_dir / "test_database" / "_checkpoint.json"]:
        if ck.exists():
            ck.unlink()

    print("\nPhase 3 complete.")
