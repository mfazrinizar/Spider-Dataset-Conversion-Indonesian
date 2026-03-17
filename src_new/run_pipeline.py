"""
Main pipeline orchestrator for IDSpider1 translation.

Usage:
    python -m src_new.run_pipeline --phase all
    python -m src_new.run_pipeline --phase 0    # Schema dict only
    python -m src_new.run_pipeline --phase 1    # Translate questions only
    python -m src_new.run_pipeline --phase 2    # Apply translations only
    python -m src_new.run_pipeline --phase 3    # Translate databases only
    python -m src_new.run_pipeline --phase verify
"""

import argparse
import json
import sys
import time
from pathlib import Path

from .config import (
    SPIDER_DIR,
    SPIDER_TABLES_JSON,
    OUTPUT_DIR,
    INTERMEDIATE_DIR,
    SCHEMA_DICT_PATH,
    SCHEMA_DICT_WORDS_PATH,
    COLLISION_REPORT_PATH,
    TRANSLATED_QUESTIONS_DIR,
)


def run_phase0():
    """Phase 0: Build schema translation dictionary."""
    from .schema_translator import run_phase0 as _run_phase0

    return _run_phase0(
        tables_json_path=SPIDER_TABLES_JSON,
        output_dict_path=SCHEMA_DICT_PATH,
        output_words_path=SCHEMA_DICT_WORDS_PATH,
        collision_report_path=COLLISION_REPORT_PATH,
        use_sync=True,
    )


def run_phase1():
    """Phase 1: Translate questions via Google Translate."""
    from .translate_questions import run_phase1 as _run_phase1

    _run_phase1(
        spider_dir=SPIDER_DIR,
        output_dir=TRANSLATED_QUESTIONS_DIR,
        delay=0.3,
        batch_pause=2.0,
    )


def run_phase2():
    """Phase 2: Apply translations to all JSON/SQL files."""
    from .apply_translation import run_phase2 as _run_phase2

    _run_phase2(
        spider_dir=SPIDER_DIR,
        output_dir=OUTPUT_DIR,
        trans_dict_path=SCHEMA_DICT_PATH,
        translated_questions_dir=TRANSLATED_QUESTIONS_DIR,
    )


def run_fix():
    """Phase fix: Apply manual corrections to the translation dictionary."""
    from .manual_corrections import run_manual_corrections

    return run_manual_corrections(
        dict_path=SCHEMA_DICT_PATH,
        words_path=SCHEMA_DICT_WORDS_PATH,
        tables_json_path=SPIDER_TABLES_JSON,
    )


def run_phase3():
    """Phase 3: Translate SQLite databases."""
    from .translate_databases import run_phase3 as _run_phase3

    _run_phase3(
        spider_dir=SPIDER_DIR,
        output_dir=OUTPUT_DIR,
        trans_dict_path=SCHEMA_DICT_PATH,
    )


def run_verification():
    """Run comprehensive verification."""
    from .verify import run_verification as _run_verification

    report = _run_verification(
        output_dir=OUTPUT_DIR,
        original_dir=SPIDER_DIR,
        trans_dict_path=SCHEMA_DICT_PATH,
    )
    return report.passed


def main():
    parser = argparse.ArgumentParser(description="IDSpider1 Translation Pipeline")
    parser.add_argument(
        "--phase",
        choices=["0", "1", "2", "3", "verify", "all"],
        default="all",
        help="Which phase to run (default: all)",
    )
    parser.add_argument(
        "--spider-dir",
        type=Path,
        default=None,
        help="Override path to spider/ directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override path to output idspider/ directory",
    )
    args = parser.parse_args()

    # Override paths if provided
    if args.spider_dir:
        import src_new.config as cfg
        cfg.SPIDER_DIR = args.spider_dir
        cfg.SPIDER_TABLES_JSON = args.spider_dir / "tables.json"

    if args.output_dir:
        import src_new.config as cfg
        cfg.OUTPUT_DIR = args.output_dir

    start = time.time()

    if args.phase in ("0", "all"):
        run_phase0()
        print()

    if args.phase in ("1", "all"):
        run_phase1()
        print()

    if args.phase in ("2", "all"):
        run_phase2()
        print()

    if args.phase in ("3", "all"):
        run_phase3()
        print()

    if args.phase in ("verify", "all"):
        passed = run_verification()
        if not passed:
            print("\n⚠ Verification found errors. Review the report above.")
        print()

    elapsed = time.time() - start
    print(f"Total elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
