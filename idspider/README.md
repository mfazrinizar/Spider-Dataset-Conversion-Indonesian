# IDSpider — Indonesian Spider Evaluation Baseline

Evaluation framework for the IDSpider dataset, adapted from the
[Spider](https://yale-lily.github.io/spider) Text-to-SQL benchmark.

## Overview

IDSpider is the Indonesian translation of the Spider Text-to-SQL dataset.
This directory provides evaluation tools that work with the translated dataset.

The evaluation logic is **identical** to the original Spider eval framework —
it uses component matching, exact set matching, and execution accuracy.
The only difference is that paths default to the IDSpider dataset.

## Usage

```bash
# Evaluate on dev set
python evaluation.py --gold ../data/idspider/dev_gold.sql \
                     --pred your_predictions.sql \
                     --db ../data/idspider/database \
                     --table ../data/idspider/tables.json \
                     --etype all
```

### Arguments

| Argument  | Default                      | Description               |
| --------- | ---------------------------- | ------------------------- |
| `--gold`  | `data/idspider/dev_gold.sql` | Gold SQL file             |
| `--pred`  | (required)                   | Predicted SQL file        |
| `--db`    | `data/idspider/database`     | Database directory        |
| `--table` | `data/idspider/tables.json`  | Schema file               |
| `--etype` | `all`                        | `all`, `exec`, or `match` |

### Prediction Format

One SQL query per line (no db_id, just the SQL):

```
SELECT count(*) FROM penyanyi
SELECT nama, negara, usia FROM penyanyi ORDER BY usia DESC
...
```

Or with db_id (tab-separated):

```
SELECT count(*) FROM penyanyi	konser_penyanyi
```

## Evaluation Metrics

- **Exact Set Match**: Compares parsed SQL components
- **Execution Accuracy**: Compares query execution results
- **Partial Matching**: Per-component accuracy (select, where, group, order, etc.)
- **Hardness**: Classifies queries as easy/medium/hard/extra hard
