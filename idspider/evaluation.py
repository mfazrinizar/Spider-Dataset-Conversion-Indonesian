"""
IDSpider Evaluation — Adapted from Spider evaluation framework.

This is a wrapper around the original Spider evaluation code
that defaults to IDSpider (Indonesian) dataset paths.

The evaluation logic is identical to the original Spider eval:
- Component matching (select, where, group, order, etc.)
- Exact set matching  
- Execution accuracy

Usage:
    python evaluation.py --gold ../data/idspider/dev_gold.sql \\
                         --pred predictions.sql \\
                         --db ../data/idspider/database \\
                         --table ../data/idspider/tables.json \\
                         --etype all
"""

from __future__ import print_function
import os
import sys
import argparse

# Add parent spider/ directory to path for process_sql import
SPIDER_DIR = os.path.join(os.path.dirname(__file__), '..', 'spider')
sys.path.insert(0, SPIDER_DIR)

from evaluation import evaluate, build_foreign_key_map_from_json, print_scores


# Default IDSpider paths (relative to this script)
DEFAULT_DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'idspider', 'database')
DEFAULT_TABLE = os.path.join(os.path.dirname(__file__), '..', 'data', 'idspider', 'tables.json')
DEFAULT_GOLD = os.path.join(os.path.dirname(__file__), '..', 'data', 'idspider', 'dev_gold.sql')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="IDSpider Evaluation — evaluate Text-to-SQL on Indonesian Spider dataset"
    )
    parser.add_argument('--gold', type=str, default=DEFAULT_GOLD,
                        help='Path to gold SQL file (default: data/idspider/dev_gold.sql)')
    parser.add_argument('--pred', type=str, required=True,
                        help='Path to predicted SQL file')
    parser.add_argument('--db', type=str, default=DEFAULT_DB_DIR,
                        help='Path to database directory (default: data/idspider/database)')
    parser.add_argument('--table', type=str, default=DEFAULT_TABLE,
                        help='Path to tables.json (default: data/idspider/tables.json)')
    parser.add_argument('--etype', type=str, default='all',
                        choices=['all', 'exec', 'match'],
                        help='Evaluation type (default: all)')
    args = parser.parse_args()

    assert os.path.exists(args.gold), f"Gold file not found: {args.gold}"
    assert os.path.exists(args.pred), f"Prediction file not found: {args.pred}"
    assert os.path.exists(args.db), f"Database directory not found: {args.db}"
    assert os.path.exists(args.table), f"Table file not found: {args.table}"

    kmaps = build_foreign_key_map_from_json(args.table)
    evaluate(args.gold, args.pred, args.db, args.etype, kmaps)
