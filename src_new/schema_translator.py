"""
Schema translation: extract identifiers, translate words, build dict, detect/fix collisions.

This module implements Phase 0 of the IDSpider1 translation pipeline.
It extracts all database identifiers from Spider's tables.json,
translates individual words via Google Translate, and builds a
comprehensive identifier-level translation dictionary with collision handling.
"""
from __future__ import annotations

import json
import re
import time
import asyncio
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm

from .config import (
    SQL_KEYWORDS,
    NEVER_TRANSLATE_TOKENS,
    KNOWN_DISAMBIGUATIONS,
    PREFERRED_TRANSLATIONS,
)


#  Identifier Splitting & Reassembly 

def split_identifier(name: str) -> list[str]:
    """Split an identifier into component words.

    Handles snake_case, camelCase, PascalCase, and UPPER_CASE.
    Examples:
        'concert_singer' → ['concert', 'singer']
        'Perpetrator_ID' → ['perpetrator', 'id']
        'channelGrouping' → ['channel', 'grouping']
        'CAR_MAKERS' → ['car', 'makers']
    """
    # First split on underscores
    parts = name.split("_")
    words = []
    for part in parts:
        if not part:
            continue
        # Split camelCase/PascalCase
        tokens = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\b)|[A-Z]+|\d+", part)
        if tokens:
            words.extend(t.lower() for t in tokens)
        else:
            words.append(part.lower())
    return words


def detect_naming_style(name: str) -> str:
    """Detect the naming convention of an identifier."""
    if "_" in name:
        if name == name.upper():
            return "UPPER_CASE"
        return "snake_case"
    if name[0].isupper():
        return "PascalCase"
    return "camelCase"


def reassemble_identifier(tokens: list[str], style: str) -> str:
    """Reassemble tokens into an identifier matching the given naming style."""
    if not tokens:
        return ""
    if style == "snake_case":
        return "_".join(tokens)
    elif style == "UPPER_CASE":
        return "_".join(t.upper() for t in tokens)
    elif style == "PascalCase":
        return "".join(t.capitalize() for t in tokens)
    elif style == "camelCase":
        return tokens[0] + "".join(t.capitalize() for t in tokens[1:])
    return "_".join(tokens)


#  Identifier Extraction 

def extract_identifiers_from_tables_json(tables_json_path: Path) -> dict:
    """Extract all unique identifiers from Spider tables.json.

    Returns dict with keys:
        'db_ids': set of db_id strings
        'table_names': set of table name strings
        'column_names': set of column name strings
        'all_identifiers': dict mapping identifier → set of contexts
    """
    with open(tables_json_path, encoding="utf-8") as f:
        tables = json.load(f)

    db_ids = set()
    table_names = set()
    column_names = set()
    all_identifiers = defaultdict(set)  # identifier → {context description}

    for db in tables:
        db_id = db["db_id"]
        db_ids.add(db_id)
        all_identifiers[db_id].add("db_id")

        for tname in db.get("table_names_original", []):
            if tname and tname != "*":
                table_names.add(tname)
                all_identifiers[tname].add(f"table:{db_id}")

        for col_entry in db.get("column_names_original", []):
            if isinstance(col_entry, list) and len(col_entry) == 2:
                col_name = col_entry[1]
                if col_name and col_name != "*":
                    column_names.add(col_name)
                    all_identifiers[col_name].add(f"column:{db_id}")

    return {
        "db_ids": db_ids,
        "table_names": table_names,
        "column_names": column_names,
        "all_identifiers": all_identifiers,
    }


def build_word_set(identifiers: set[str]) -> set[str]:
    """Extract unique translatable words from a set of identifiers.

    Filters out SQL keywords, technical abbreviations, single characters,
    and pure digits.
    """
    words = set()
    for ident in identifiers:
        for word in split_identifier(ident):
            if (
                len(word) > 1
                and word.upper() not in SQL_KEYWORDS
                and word.lower() not in NEVER_TRANSLATE_TOKENS
                and not word.isdigit()
            ):
                words.add(word.lower())
    return words


#  Word Translation 

async def _translate_single_word(translator, word: str) -> str:
    """Translate a single word using googletrans."""
    try:
        result = await translator.translate(word, src="en", dest="id")
        translated = result.text.strip().lower()
        # Clean: only keep alphanumeric and underscores
        translated = re.sub(r"[^a-z0-9]", "_", translated)
        translated = re.sub(r"_+", "_", translated).strip("_")
        return translated if translated else word
    except Exception:
        return word


def translate_words(words: set[str], translator) -> dict[str, str]:
    """Translate a set of words using Google Translate.

    Args:
        words: Set of English words to translate
        translator: googletrans.Translator instance (or async-compatible)

    Returns:
        Dict mapping english_word → indonesian_word
    """
    word_map = {}
    word_list = sorted(words)

    # Apply preferred translations first (no API call needed)
    remaining = []
    for word in word_list:
        if word in PREFERRED_TRANSLATIONS:
            word_map[word] = PREFERRED_TRANSLATIONS[word]
        else:
            remaining.append(word)

    if not remaining:
        return word_map

    # Translate remaining words via Google Translate
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass

    print(f"Translating {len(remaining)} words via Google Translate...")
    for i, word in enumerate(tqdm(remaining, desc="Translating words")):
        translated = loop.run_until_complete(
            _translate_single_word(translator, word)
        )
        word_map[word] = translated

        # Rate limit: brief sleep between calls
        if (i + 1) % 10 == 0:
            time.sleep(1.0)
        else:
            time.sleep(0.2)

    return word_map


def translate_words_sync(words: set[str]) -> dict[str, str]:
    """Synchronous word translation using googletrans."""
    from googletrans import Translator

    word_map = {}
    word_list = sorted(words)

    # Apply preferred translations first
    remaining = []
    for word in word_list:
        if word in PREFERRED_TRANSLATIONS:
            word_map[word] = PREFERRED_TRANSLATIONS[word]
        else:
            remaining.append(word)

    if not remaining:
        return word_map

    translator = Translator()
    print(f"Translating {len(remaining)} words via Google Translate...")

    for i, word in enumerate(tqdm(remaining, desc="Translating words")):
        try:
            result = translator.translate(word, src="en", dest="id")
            translated = result.text.strip().lower()
            translated = re.sub(r"[^a-z0-9]", "_", translated)
            translated = re.sub(r"_+", "_", translated).strip("_")
            word_map[word] = translated if translated else word
        except Exception:
            word_map[word] = word

        # Rate limit
        if (i + 1) % 10 == 0:
            time.sleep(2.0)
        else:
            time.sleep(0.3)

    return word_map


#  Identifier Translation Dict Building 

def build_identifier_translation_dict(
    identifiers: set[str],
    word_map: dict[str, str],
) -> dict[str, str]:
    """Build a full identifier translation dictionary from word-level translations.

    For each identifier:
    1. Split into words
    2. Translate each word using word_map
    3. Reassemble using original naming style
    4. If all words are untranslatable (SQL keywords etc), keep original

    Returns dict mapping english_identifier → indonesian_identifier.
    """
    trans_dict = {}

    for ident in sorted(identifiers):
        words = split_identifier(ident)
        if not words:
            trans_dict[ident] = ident
            continue

        style = detect_naming_style(ident)
        translated_words = []
        any_translated = False

        for word in words:
            low = word.lower()
            if low.upper() in SQL_KEYWORDS or low in NEVER_TRANSLATE_TOKENS or low.isdigit():
                translated_words.append(low)
            elif low in word_map:
                translated_words.append(word_map[low])
                if word_map[low] != low:
                    any_translated = True
            else:
                translated_words.append(low)

        if any_translated:
            result = reassemble_identifier(translated_words, "snake_case")
        else:
            result = ident

        trans_dict[ident] = result

    return trans_dict


#  Collision Detection 

def detect_dict_collisions(trans_dict: dict[str, str]) -> dict[str, list[str]]:
    """Find all cases where multiple English identifiers map to the same Indonesian.

    Returns dict mapping indonesian → [english1, english2, ...].
    Only includes entries with 2+ English sources.
    """
    reverse_map = defaultdict(list)
    for en, idn in trans_dict.items():
        reverse_map[idn.lower()].append(en)

    return {
        idn: sorted(en_list)
        for idn, en_list in reverse_map.items()
        if len(en_list) > 1
    }


def detect_per_table_collisions(tables_json_path: Path, trans_dict: dict[str, str]) -> list[dict]:
    """Detect column name collisions within each table after translation.

    Returns list of collision records with db_id, table, columns involved.
    """
    with open(tables_json_path, encoding="utf-8") as f:
        tables = json.load(f)

    collisions = []
    for db in tables:
        db_id = db["db_id"]
        col_names_orig = db.get("column_names_original", [])
        table_names_orig = db.get("table_names_original", [])

        # Group columns by table
        table_columns = defaultdict(list)  # table_idx → [(orig_col, translated_col)]
        for col_entry in col_names_orig:
            if isinstance(col_entry, list) and len(col_entry) == 2:
                table_idx, col_name = col_entry
                if table_idx < 0 or col_name == "*":
                    continue
                translated = trans_dict.get(col_name, col_name).lower()
                table_columns[table_idx].append((col_name, translated))

        # Check for duplicates within each table
        for table_idx, cols in table_columns.items():
            seen = defaultdict(list)
            for orig, translated in cols:
                seen[translated].append(orig)

            for translated_name, orig_names in seen.items():
                if len(orig_names) > 1:
                    table_name = (
                        table_names_orig[table_idx]
                        if table_idx < len(table_names_orig)
                        else f"table_{table_idx}"
                    )
                    collisions.append({
                        "db_id": db_id,
                        "table": table_name,
                        "translated_column": translated_name,
                        "original_columns": orig_names,
                    })

    return collisions


def detect_table_name_collisions(tables_json_path: Path, trans_dict: dict[str, str]) -> list[dict]:
    """Detect table name collisions within each database after translation."""
    with open(tables_json_path, encoding="utf-8") as f:
        tables = json.load(f)

    collisions = []
    for db in tables:
        db_id = db["db_id"]
        table_names_orig = db.get("table_names_original", [])

        seen = defaultdict(list)
        for tname in table_names_orig:
            if tname:
                translated = trans_dict.get(tname, tname).lower()
                seen[translated].append(tname)

        for translated_name, orig_names in seen.items():
            if len(orig_names) > 1:
                collisions.append({
                    "db_id": db_id,
                    "translated_table": translated_name,
                    "original_tables": orig_names,
                })

    return collisions


def detect_db_id_collisions(tables_json_path: Path, trans_dict: dict[str, str]) -> list[dict]:
    """Detect db_id collisions after translation."""
    with open(tables_json_path, encoding="utf-8") as f:
        tables = json.load(f)

    seen = defaultdict(list)
    for db in tables:
        db_id = db["db_id"]
        translated = trans_dict.get(db_id, db_id).lower()
        seen[translated].append(db_id)

    return [
        {"translated_db_id": tid, "original_db_ids": orig_list}
        for tid, orig_list in seen.items()
        if len(orig_list) > 1
    ]


#  Collision Resolution 

def disambiguate_collision(english_names: list[str], indonesian_name: str, word_map: dict[str, str]) -> dict[str, str]:
    """Resolve a collision where multiple English names map to the same Indonesian.

    Strategy:
    1. Check KNOWN_DISAMBIGUATIONS for exact match
    2. For compound identifiers, find differing token and disambiguate that
    3. Fallback: append English suffix for disambiguation

    Returns dict mapping english_name → disambiguated_indonesian_name.
    """
    en_words = {name: split_identifier(name) for name in english_names}

    # Strategy 1: Check known disambiguations
    # Try matching just the base words (last meaningful word of each identifier)
    base_words = set()
    for name in english_names:
        words = en_words[name]
        # Find the most meaningful word (skip 'id', 'name', etc.)
        for w in reversed(words):
            if w.lower() not in NEVER_TRANSLATE_TOKENS:
                base_words.add(w.lower())
                break

    for known_set, disambig in KNOWN_DISAMBIGUATIONS.items():
        if base_words.issubset(known_set) or base_words == known_set:
            result = {}
            for name in english_names:
                words = en_words[name]
                for w in reversed(words):
                    if w.lower() in disambig:
                        # Replace the colliding word with the disambiguated version
                        new_words = []
                        for orig_w in words:
                            if orig_w.lower() == w.lower():
                                new_words.append(disambig[w.lower()])
                            elif orig_w.lower() in word_map:
                                new_words.append(word_map[orig_w.lower()])
                            else:
                                new_words.append(orig_w.lower())
                        result[name] = "_".join(new_words)
                        break
                else:
                    result[name] = indonesian_name
            if len(set(result.values())) == len(result):
                return result

    # Strategy 2: For compound identifiers, find differing tokens
    if all(len(en_words[n]) > 1 for n in english_names):
        # Find positions where tokens differ
        max_len = max(len(en_words[n]) for n in english_names)
        result = {}
        for name in english_names:
            words = en_words[name]
            translated_words = []
            for w in words:
                low = w.lower()
                if low in word_map:
                    translated_words.append(word_map[low])
                elif low in PREFERRED_TRANSLATIONS:
                    translated_words.append(PREFERRED_TRANSLATIONS[low])
                else:
                    translated_words.append(low)
            result[name] = "_".join(translated_words)

        if len(set(result.values())) == len(result):
            return result

    # Strategy 3: Fallback - append English suffix
    result = {}
    for i, name in enumerate(sorted(english_names)):
        if i == 0:
            result[name] = indonesian_name
        else:
            words = en_words[name]
            # Find the most distinctive English word to use as suffix
            suffix = words[-1] if words else name
            result[name] = f"{indonesian_name}_{suffix}"
    return result


def build_collision_fixes(
    trans_dict: dict[str, str],
    tables_json_path: Path,
    word_map: dict[str, str],
) -> dict[str, str]:
    """Build fixes for all detected collisions.

    Returns dict mapping english_identifier → fixed_indonesian with no collisions.
    """
    fixes = {}

    # Fix per-table column collisions
    col_collisions = detect_per_table_collisions(tables_json_path, trans_dict)
    for collision in col_collisions:
        en_names = collision["original_columns"]
        id_name = collision["translated_column"]
        disambig = disambiguate_collision(en_names, id_name, word_map)
        fixes.update(disambig)

    # Fix table name collisions
    table_collisions = detect_table_name_collisions(tables_json_path, trans_dict)
    for collision in table_collisions:
        en_names = collision["original_tables"]
        id_name = collision["translated_table"]
        disambig = disambiguate_collision(en_names, id_name, word_map)
        fixes.update(disambig)

    # Fix db_id collisions
    db_collisions = detect_db_id_collisions(tables_json_path, trans_dict)
    for collision in db_collisions:
        en_names = collision["original_db_ids"]
        id_name = collision["translated_db_id"]
        disambig = disambiguate_collision(en_names, id_name, word_map)
        fixes.update(disambig)

    return fixes


#  Full Pipeline 

def run_phase0(
    tables_json_path: Path,
    output_dict_path: Path,
    output_words_path: Path,
    collision_report_path: Path | None = None,
    use_sync: bool = True,
) -> dict[str, str]:
    """Run Phase 0: build schema translation dictionary.

    1. Extract all identifiers from tables.json
    2. Build word set
    3. Translate words (via Google Translate or preferred translations)
    4. Build identifier dict
    5. Detect and fix collisions
    6. Save results

    Returns the final translation dictionary.
    """
    print("=" * 60)
    print("Phase 0: Building Schema Translation Dictionary")
    print("=" * 60)

    # Ensure output directories exist
    output_dict_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Extract identifiers
    print("\n[1/5] Extracting identifiers from tables.json...")
    extracted = extract_identifiers_from_tables_json(tables_json_path)
    all_idents = set(extracted["all_identifiers"].keys())
    print(f"  Found {len(extracted['db_ids'])} db_ids, "
          f"{len(extracted['table_names'])} table names, "
          f"{len(extracted['column_names'])} column names")
    print(f"  Total unique identifiers: {len(all_idents)}")

    # Also extract from test tables.json if it exists
    test_tables = tables_json_path.parent / "test_data" / "tables.json"
    if test_tables.exists():
        print("  Also extracting from test_data/tables.json...")
        test_extracted = extract_identifiers_from_tables_json(test_tables)
        for k in ["db_ids", "table_names", "column_names"]:
            extracted[k] |= test_extracted[k]
        all_idents |= set(test_extracted["all_identifiers"].keys())
        print(f"  Combined: {len(all_idents)} unique identifiers")

    # Step 2: Build word set
    print("\n[2/5] Building translatable word set...")
    words = build_word_set(all_idents)
    print(f"  {len(words)} unique translatable words")

    # Step 3: Translate words
    print("\n[3/5] Translating words...")
    if use_sync:
        word_map = translate_words_sync(words)
    else:
        from googletrans import Translator
        translator = Translator()
        word_map = translate_words(words, translator)

    # Save word map
    with open(output_words_path, "w", encoding="utf-8") as f:
        json.dump(word_map, f, ensure_ascii=False, indent=2)
    print(f"  Saved word map to {output_words_path}")

    # Step 4: Build identifier dict
    print("\n[4/5] Building identifier translation dictionary...")
    trans_dict = build_identifier_translation_dict(all_idents, word_map)

    # Count changes
    changed = sum(1 for k, v in trans_dict.items() if k != v)
    print(f"  {changed}/{len(trans_dict)} identifiers will be translated")

    # Step 5: Detect and fix collisions
    print("\n[5/5] Detecting and fixing collisions...")
    col_collisions = detect_per_table_collisions(tables_json_path, trans_dict)
    table_collisions = detect_table_name_collisions(tables_json_path, trans_dict)
    db_collisions = detect_db_id_collisions(tables_json_path, trans_dict)

    print(f"  Column collisions: {len(col_collisions)}")
    print(f"  Table name collisions: {len(table_collisions)}")
    print(f"  DB ID collisions: {len(db_collisions)}")

    if col_collisions or table_collisions or db_collisions:
        fixes = build_collision_fixes(trans_dict, tables_json_path, word_map)
        print(f"  Applying {len(fixes)} disambiguation fixes...")
        for en, fixed_id in fixes.items():
            trans_dict[en] = fixed_id

        # Verify fixes resolved collisions
        remaining_col = detect_per_table_collisions(tables_json_path, trans_dict)
        remaining_table = detect_table_name_collisions(tables_json_path, trans_dict)
        remaining_db = detect_db_id_collisions(tables_json_path, trans_dict)
        print(f"  After fix — column: {len(remaining_col)}, "
              f"table: {len(remaining_table)}, db_id: {len(remaining_db)}")

    # Save collision report
    if collision_report_path:
        report = {
            "column_collisions": col_collisions,
            "table_name_collisions": table_collisions,
            "db_id_collisions": db_collisions,
            "total_fixes_applied": len(fixes) if (col_collisions or table_collisions or db_collisions) else 0,
        }
        collision_report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(collision_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"  Saved collision report to {collision_report_path}")

    # Save final dictionary
    with open(output_dict_path, "w", encoding="utf-8") as f:
        json.dump(trans_dict, f, ensure_ascii=False, indent=2)
    print(f"\nSaved translation dictionary ({len(trans_dict)} entries) to {output_dict_path}")

    return trans_dict
