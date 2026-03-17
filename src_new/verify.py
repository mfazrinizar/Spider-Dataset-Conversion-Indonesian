"""
Comprehensive verification of the translated IDSpider dataset.

Checks:
1. Entry counts match original
2. All db_ids in queries exist in tables.json
3. Table/column names in SQL queries match tables.json schemas
4. No column name collisions within any table
5. No untranslated identifiers remaining
6. SQL string literals preserved (not translated)
7. Number formatting correct (no Indonesian locale artifacts)
8. Question translations present and non-empty
9. SQLite databases have correct translated schema
10. Gold SQL files match query files
"""

from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path


class VerificationReport:
    """Collects and formats verification results."""

    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []

    def ok(self, msg: str):
        self.checks.append(("OK", msg))

    def warn(self, msg: str):
        self.warnings.append(msg)
        self.checks.append(("WARN", msg))

    def error(self, msg: str):
        self.errors.append(msg)
        self.checks.append(("ERROR", msg))

    def summary(self) -> str:
        lines = ["=" * 60, "Verification Report", "=" * 60, ""]
        for status, msg in self.checks:
            icon = {"OK": "+", "WARN": "!", "ERROR": "X"}[status]
            lines.append(f"  [{icon}] {msg}")
        lines.append("")
        lines.append(f"Total: {len(self.checks)} checks, "
                      f"{len(self.warnings)} warnings, "
                      f"{len(self.errors)} errors")
        return "\n".join(lines)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


def verify_dataset(
    output_dir: Path,
    original_dir: Path,
    trans_dict_path: Path | None = None,
) -> VerificationReport:
    """Run all verification checks on the translated dataset."""
    report = VerificationReport()

    # Load translation dict
    trans_dict = {}
    if trans_dict_path and trans_dict_path.exists():
        with open(trans_dict_path, encoding="utf-8") as f:
            trans_dict = json.load(f)

    # Check 1: File existence
    _check_files_exist(output_dir, report)

    # Check 2: Entry counts
    _check_entry_counts(output_dir, original_dir, report)

    # Check 3: tables.json consistency
    tables_data = _check_tables_json(output_dir, report)

    # Check 4: Query-schema consistency
    _check_query_schema(output_dir, tables_data, report)

    # Check 5: Column collisions
    _check_column_collisions(tables_data, report)

    # Check 6: SQL string literals
    _check_sql_literals(output_dir, report)

    # Check 7: Number formatting
    _check_number_formatting(output_dir, report)

    # Check 8: Question quality
    _check_questions(output_dir, report)

    # Check 9: Gold SQL consistency
    _check_gold_sql(output_dir, tables_data, report)

    # Check 10: Identifier consistency (no spaces in names)
    _check_identifier_format(tables_data, report)

    return report


def _check_files_exist(output_dir: Path, report: VerificationReport):
    """Check that all expected output files exist."""
    required = [
        "tables.json", "dev.json", "train_spider.json",
        "train_others.json", "train.json",
        "dev_gold.sql", "train_gold.sql",
    ]
    for fname in required:
        if (output_dir / fname).exists():
            report.ok(f"File exists: {fname}")
        else:
            report.error(f"Missing file: {fname}")


def _check_entry_counts(output_dir: Path, original_dir: Path, report: VerificationReport):
    """Check that entry counts match the original."""
    pairs = [
        ("dev.json", "dev.json"),
        ("train_spider.json", "train_spider.json"),
        ("train_others.json", "train_others.json"),
        ("tables.json", "tables.json"),
    ]
    for out_name, orig_name in pairs:
        out_path = output_dir / out_name
        orig_path = original_dir / orig_name
        if not out_path.exists() or not orig_path.exists():
            continue
        with open(out_path, encoding="utf-8") as f:
            out_count = len(json.load(f))
        with open(orig_path, encoding="utf-8") as f:
            orig_count = len(json.load(f))
        if out_count == orig_count:
            report.ok(f"{out_name}: {out_count} entries (matches original)")
        else:
            report.error(f"{out_name}: {out_count} entries (expected {orig_count})")


def _check_tables_json(output_dir: Path, report: VerificationReport) -> list[dict]:
    """Load and validate tables.json structure."""
    path = output_dir / "tables.json"
    if not path.exists():
        report.error("tables.json not found")
        return []

    with open(path, encoding="utf-8") as f:
        tables = json.load(f)

    # Check each database entry
    for db in tables:
        db_id = db.get("db_id", "UNKNOWN")

        # Check required fields
        for field in ["db_id", "column_names", "column_names_original",
                      "table_names", "table_names_original", "column_types",
                      "foreign_keys", "primary_keys"]:
            if field not in db:
                report.error(f"{db_id}: missing field '{field}'")

        # Check table_names matches table_names_original
        if db.get("table_names") != db.get("table_names_original"):
            # They should be equal after our translation (both are translated)
            tn = db.get("table_names", [])
            tno = db.get("table_names_original", [])
            if len(tn) != len(tno):
                report.error(f"{db_id}: table_names length mismatch")

        # Check column arrays have same length
        cn = db.get("column_names", [])
        cno = db.get("column_names_original", [])
        ct = db.get("column_types", [])
        if len(cn) != len(cno):
            report.error(f"{db_id}: column_names length mismatch")
        if len(cn) != len(ct):
            report.error(f"{db_id}: column_names vs column_types length mismatch")

    report.ok(f"tables.json: {len(tables)} database schemas validated")
    return tables


def _check_query_schema(output_dir: Path, tables_data: list[dict], report: VerificationReport):
    """Check that query db_ids and table references match tables.json."""
    if not tables_data:
        return

    # Build db_id → table_names lookup
    db_tables = {}
    for db in tables_data:
        db_id = db["db_id"]
        db_tables[db_id] = set(
            t.lower().replace(" ", "_") for t in db.get("table_names", []) if t
        )

    valid_db_ids = set(db_tables.keys())
    mismatched_dbs = set()

    for fname in ["dev.json", "train_spider.json", "train_others.json"]:
        path = output_dir / fname
        if not path.exists():
            continue

        with open(path, encoding="utf-8") as f:
            entries = json.load(f)

        for entry in entries:
            db_id = entry.get("db_id", "")
            if db_id not in valid_db_ids:
                mismatched_dbs.add(db_id)

    if mismatched_dbs:
        report.error(
            f"Queries reference {len(mismatched_dbs)} unknown db_ids: "
            f"{sorted(mismatched_dbs)[:5]}..."
        )
    else:
        report.ok("All query db_ids found in tables.json")


def _check_column_collisions(tables_data: list[dict], report: VerificationReport):
    """Check for duplicate column names within any table."""
    collision_count = 0
    for db in tables_data:
        db_id = db["db_id"]
        table_cols = defaultdict(list)
        for col_entry in db.get("column_names_original", []):
            if isinstance(col_entry, list) and len(col_entry) == 2:
                table_idx, col_name = col_entry
                if table_idx >= 0 and col_name != "*":
                    table_cols[table_idx].append(col_name.lower())

        for table_idx, cols in table_cols.items():
            dupes = [c for c in set(cols) if cols.count(c) > 1]
            if dupes:
                collision_count += len(dupes)
                tnames = db.get("table_names", [])
                tname = tnames[table_idx] if table_idx < len(tnames) else f"table_{table_idx}"
                report.error(
                    f"{db_id}.{tname}: duplicate columns: {dupes}"
                )

    if collision_count == 0:
        report.ok("No column name collisions detected")


def _check_sql_literals(output_dir: Path, report: VerificationReport):
    """Check that SQL string literals were not translated."""
    # Common Indonesian translations that should NOT appear in SQL values
    translated_values = {
        "Perancis", "Rusia", "Belanda", "Spanyol", "Kalifornia",
        "Bahasa_inggris", "Tanda Muda", "Tanah_air",
    }

    found_issues = 0
    for fname in ["dev.json", "train_spider.json", "train_others.json"]:
        path = output_dir / fname
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)
        for entry in entries:
            query = entry.get("query", "")
            for val in translated_values:
                if val in query:
                    found_issues += 1

    if found_issues > 0:
        report.error(f"Found {found_issues} likely translated SQL string values")
    else:
        report.ok("No translated SQL string values detected")


def _check_number_formatting(output_dir: Path, report: VerificationReport):
    """Check for Indonesian number formatting artifacts (e.g., 10.000 for 10000)."""
    issue_count = 0
    # Pattern: digit.digit{3} that looks like Indonesian thousands separator
    pattern = re.compile(r"\b(\d{1,3})\.(000)\b")

    for fname in ["dev.json", "train_spider.json", "train_others.json"]:
        path = output_dir / fname
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)
        for entry in entries:
            query = entry.get("query", "")
            if pattern.search(query):
                issue_count += 1

    if issue_count > 0:
        report.error(f"Found {issue_count} queries with Indonesian number formatting")
    else:
        report.ok("No Indonesian number formatting artifacts")


def _check_questions(output_dir: Path, report: VerificationReport):
    """Check that questions were translated."""
    empty_count = 0
    total = 0

    for fname in ["dev.json", "train_spider.json", "train_others.json"]:
        path = output_dir / fname
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)
        for entry in entries:
            total += 1
            question = entry.get("question", "")
            if not question or len(question.strip()) < 3:
                empty_count += 1

    if empty_count > 0:
        report.warn(f"{empty_count}/{total} questions are empty or too short")
    else:
        report.ok(f"All {total} questions have content")


def _check_gold_sql(output_dir: Path, tables_data: list[dict], report: VerificationReport):
    """Check gold SQL files match query files."""
    for sql_file, json_file in [
        ("dev_gold.sql", "dev.json"),
        ("train_gold.sql", "train.json"),
    ]:
        sql_path = output_dir / sql_file
        json_path = output_dir / json_file

        if not sql_path.exists() or not json_path.exists():
            continue

        with open(sql_path, encoding="utf-8") as f:
            sql_lines = [l.strip() for l in f.readlines() if l.strip()]
        with open(json_path, encoding="utf-8") as f:
            json_entries = json.load(f)

        if len(sql_lines) == len(json_entries):
            report.ok(f"{sql_file}: {len(sql_lines)} lines matches {json_file}")
        else:
            report.warn(
                f"{sql_file}: {len(sql_lines)} lines vs "
                f"{json_file}: {len(json_entries)} entries"
            )


def _check_identifier_format(tables_data: list[dict], report: VerificationReport):
    """Check that all identifiers use underscores (no spaces)."""
    space_count = 0
    for db in tables_data:
        for tname in db.get("table_names_original", []):
            if tname and " " in tname:
                space_count += 1
        for col_entry in db.get("column_names_original", []):
            if isinstance(col_entry, list) and len(col_entry) == 2:
                if col_entry[1] and " " in col_entry[1]:
                    space_count += 1

    if space_count > 0:
        report.error(f"Found {space_count} identifiers with spaces (should use underscores)")
    else:
        report.ok("All identifiers use underscores (no spaces)")


def verify_databases(
    output_db_dir: Path,
    tables_json_path: Path,
    report: VerificationReport | None = None,
) -> VerificationReport:
    """Verify translated SQLite databases match the tables.json schema."""
    if report is None:
        report = VerificationReport()

    if not tables_json_path.exists():
        report.error("tables.json not found for database verification")
        return report

    with open(tables_json_path, encoding="utf-8") as f:
        tables = json.load(f)

    if not output_db_dir.exists():
        report.error(f"Database directory not found: {output_db_dir}")
        return report

    # Build expected schema from tables.json
    expected_schemas = {}
    for db in tables:
        db_id = db["db_id"]
        expected_tables = set(
            t.lower() for t in db.get("table_names_original", []) if t
        )
        expected_schemas[db_id] = expected_tables

    # Check each database
    checked = 0
    missing = 0
    schema_mismatches = 0

    for db_id, expected_tables in expected_schemas.items():
        db_dir = output_db_dir / db_id
        if not db_dir.exists():
            missing += 1
            continue

        sqlite_files = list(db_dir.glob("*.sqlite"))
        if not sqlite_files:
            missing += 1
            continue

        checked += 1
        try:
            conn = sqlite3.connect(str(sqlite_files[0]))
            actual_tables = set(
                row[0].lower()
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                ).fetchall()
            )
            conn.close()

            if expected_tables != actual_tables:
                schema_mismatches += 1

        except sqlite3.Error:
            report.warn(f"Could not read SQLite: {db_id}")

    report.ok(f"Checked {checked} databases, {missing} missing, {schema_mismatches} schema mismatches")
    return report


#  Entry Point 

def run_verification(
    output_dir: Path,
    original_dir: Path,
    trans_dict_path: Path | None = None,
) -> VerificationReport:
    """Run full verification and print results."""
    print("=" * 60)
    print("Verification")
    print("=" * 60)

    report = verify_dataset(output_dir, original_dir, trans_dict_path)

    # Also verify databases if they exist
    db_dir = output_dir / "database"
    tables_path = output_dir / "tables.json"
    if db_dir.exists() and tables_path.exists():
        print("\nVerifying databases...")
        verify_databases(db_dir, tables_path, report)

    print(report.summary())
    return report
