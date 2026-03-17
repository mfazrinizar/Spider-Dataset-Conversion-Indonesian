# IDSpider — Indonesian Text-to-SQL Dataset

**IDSpider** is a linguistically corrected, fully Indonesian-translated version of the [Spider](https://yale-sea-lab.github.io/spider/) cross-domain Text-to-SQL benchmark. It provides natural-language questions, SQL queries, and database schemas entirely in Bahasa Indonesia, enabling research on Indonesian semantic parsing and Text-to-SQL. Available on [Harvard Dataverse](https://doi.org/10.7910/DVN/C5AO0A).

---

## Dataset Statistics

| Split               | Questions | Source                   |
| ------------------- | --------- | ------------------------ |
| `train_spider.json` | 7,000     | Spider training set      |
| `train_others.json` | 1,659     | SParC, CoSQL, and others |
| `train.json`        | 8,659     | Combined training set    |
| `dev.json`          | 1,034     | Spider development set   |

| Schemas                           | Count |
| --------------------------------- | ----- |
| Main databases (`database/`)      | 166   |
| Test databases (`test_database/`) | 206   |
| Total tables                      | 876   |
| Total columns                     | 4,503 |

**Translation coverage:** 3,250 / 3,530 schema identifiers translated (91.6%); remaining 8.4% are valid loanwords, proper nouns, and database-specific abbreviations.

---

## Enhancements over the Original IDSpider Paper

This release builds directly upon the IDSpider dataset introduced in [Abdiansah et al. (2024)](#citation) and the Harvard Dataverse release [Nizar & Abdiansah (2026)](#citation), adding a comprehensive manual-correction pipeline to address linguistic issues found in the machine-translated baseline:

### 1. Indonesian Word-Order Compliance (DM — _Diterangkan–Menerangkan_)

Indonesian grammar requires the head noun to precede its modifier. The pipeline automatically enforces this:

| English (Spider)      | Old (Wrong)              | Corrected                  |
| --------------------- | ------------------------ | -------------------------- |
| `school_id`           | `sekolah_id`             | `id_sekolah`               |
| `flight_company`      | `perusahaan_penerbangan` | `perusahaan_penerbangan` ✓ |
| `university_rank`     | `universitas_peringkat`  | `peringkat_universitas`    |
| `customer_first_name` | `pelanggan_nama_depan`   | `nama_depan_pelanggan`     |
| `email_address`       | `email_alamat`           | `alamat_email`             |
| `Date_of_Birth`       | `tanggal_dari_lahir`     | `tanggal_lahir`            |

All `xxx_id` → `id_xxx` transformations are applied systematically across all 460 ID-bearing identifiers.

### 2. English Connector Removal

English prepositions and conjunctions embedded in compound identifiers are replaced with their Indonesian equivalents or removed:

| Pattern | Replacement                     |
| ------- | ------------------------------- |
| `_of_`  | removed (e.g., `tanggal_lahir`) |
| `_and_` | `_dan_`                         |
| `_in_`  | `_dalam_`                       |
| `_for_` | `_untuk_`                       |
| `_to_`  | `_ke_` / `_hingga_`             |

### 3. Manual Word-Fix Dictionary (1,602 entries)

A curated word-level translation dictionary maps over 1,600 domain-specific English terms to correct Bahasa Indonesia equivalents, covering:

- Database/technical terminology
- Academic, medical, financial, and sports domains
- SQL keyword conflicts (`date`, `order`, `time`, `count`, `end`, etc.)

### 4. Identifier Override Dictionary (530+ entries)

Direct overrides for identifiers that cannot be handled compositionally, including:

- Semantic disambiguation (e.g., `performance` → `penampilan` in orchestra contexts)
- Proper loanword preservation (`email`, `total`, `radio`, `hotel`, `studio`)
- Database-specific proper names kept intact

### 5. Database Name (db_id) Corrections

All 166 database identifiers translated with correct Indonesian word order:

| Original               | Corrected           |
| ---------------------- | ------------------- |
| `tvshow`               | `acara_tv`          |
| `tv_shows`             | `tayangan_tv`       |
| `advertising_agencies` | `agensi_periklanan` |
| `e_commerce`           | `e_niaga`           |
| `bike_racing`          | `balap_sepeda`      |
| `concert_singer`       | `penyanyi_konser`   |
| `video_game`           | `permainan_video`   |
| `online_exams`         | `ujian_daring`      |

### 6. Collision Detection & Automatic Resolution

The pipeline detects and auto-resolves:

- Per-table column name collisions
- Table name collisions within a database
- Database ID collisions across the dataset

**Result: 0 collisions, 0 schema mismatches, 0 formatting errors.**

---

## File Structure

```
idspider/
├── tables.json              # 166 database schemas (Indonesian)
├── dev.json                 # 1,034 dev questions + SQL queries
├── train_spider.json        # 7,000 Spider training questions + SQL
├── train_others.json        # 1,659 SParC/CoSQL questions + SQL
├── train.json               # Combined 8,659 training entries
├── dev_gold.sql             # Gold SQL for dev set (one per line)
├── train_gold.sql           # Gold SQL for train set (one per line)
├── database/                # 166 translated SQLite databases
│   ├── penyanyi/
│   ├── bisbol_1/
│   └── ...
└── test_database/           # 206 translated test SQLite databases
```

### Entry Format

Each entry in `dev.json` / `train_spider.json` / `train_others.json`:

```json
{
  "db_id": "penyanyi",
  "question": "Berapa banyak penyanyi yang kita miliki?",
  "question_toks": ["Berapa", "banyak", "penyanyi", "yang", "kita", "miliki", "?"],
  "query": "SELECT count(*) FROM penyanyi",
  "query_toks": ["SELECT", "count", "(", "*", ")", "FROM", "penyanyi"],
  "query_toks_no_value": ["SELECT", "count", "(", "*", ")", "FROM", "penyanyi"],
  "sql": { ... },
  "question_en": "How many singers do we have?"
}
```

> **Note:** `train_others.json` entries include the `question_en` field with the original English question for reference.

---

## Usage

### Loading the Dataset

```python
import json
import sqlite3
from pathlib import Path

DATA_DIR = Path("path/to/idspider")

# Load schemas
with open(DATA_DIR / "tables.json", encoding="utf-8") as f:
    tables = json.load(f)

# Load dev split
with open(DATA_DIR / "dev.json", encoding="utf-8") as f:
    dev_data = json.load(f)

# Connect to a translated database
db_path = DATA_DIR / "database" / "penyanyi" / "penyanyi.sqlite"
conn = sqlite3.connect(db_path)
```

### Using with a Text-to-SQL Model

The dataset follows the same schema as the original Spider benchmark. Any Spider-compatible model can be adapted by:

1. **Replacing the data directory** with this dataset's path.
2. **Using `tables.json`** as the schema source — all table and column names are in Bahasa Indonesia.
3. **Using `dev.json` / `train.json`** as question-query pairs — questions are in Bahasa Indonesia.
4. **Connecting to SQLite databases** under `database/` for execution-accuracy evaluation.

#### Example: PICARD / T5 / RESDSQL

```python
# Point model data loader to this directory
config = {
    "data_dir": "path/to/idspider",
    "db_dir": "path/to/idspider/database",
    "tables_path": "path/to/idspider/tables.json",
    "train_file": "train.json",
    "dev_file": "dev.json",
}
```

#### Evaluating with Gold SQL

```bash
# Execution accuracy evaluation
python evaluation.py \
  --gold dev_gold.sql \
  --pred predictions.sql \
  --db path/to/idspider/database \
  --etype exec
```

### Schema Linking Note

When building schema-linking models, note that:

- Table and column names are **snake_case Bahasa Indonesia**
- All `id` fields follow the `id_<noun>` prefix convention (e.g., `id_mahasiswa`, `id_penerbangan`)
- SQL keywords (`SELECT`, `FROM`, `WHERE`, etc.) remain in **English** in the gold queries

---

## Quality Metrics

| Metric                                       | Value                 |
| -------------------------------------------- | --------------------- |
| Schema identifier translation rate           | 91.6% (3,250 / 3,530) |
| English connector fragments remaining        | 0                     |
| Wrong `_id` suffix entries                   | 0                     |
| Formatting errors (double underscores, etc.) | 0                     |
| Table/column name collisions                 | 0                     |
| Schema mismatches (tables.json ↔ SQLite)     | 0                     |
| Total verification checks passed             | 21 / 21               |

---

## How to Cite

If you use IDSpider in your research, please cite both the original paper and the dataset release:

### Original IDSpider Paper (IEEE ICIC 2024)

```bibtex
@inproceedings{abdiansah2024idspider,
  author    = {Abdiansah, A. and Yusliani, N. and Fathoni, F. and Nizar, M. F. and Salsabella, A. and Davi, A. A.},
  title     = {{IDSpider}: Indonesian Standard Dataset for Text-to-SQL},
  booktitle = {2024 Ninth International Conference on Informatics and Computing (ICIC)},
  year      = {2024},
  pages     = {1--6},
  address   = {Medan, Indonesia},
  doi       = {10.1109/ICIC64337.2024.10956918},
  keywords  = {Bridges; Structured Query Language; Translation; Accuracy; Semantics;
               Benchmark testing; Syntactics; Natural language processing; Cleaning;
               Standards; Text-to-SQL; Spider; IDSpider; SQL Query Generation; Dataset Translation}
}
```

### Dataset Release (Harvard Dataverse)

```bibtex
@data{nizar2026indonesian,
  author    = {Nizar, M. Fazri and Abdiansah, Abdiansah},
  title     = {Indonesian Cross-Domain Benchmarks for Semantic Parsing and Text-to-SQL},
  year      = {2026},
  publisher = {Harvard Dataverse},
  doi       = {10.7910/DVN/C5AO0A},
  url       = {https://doi.org/10.7910/DVN/C5AO0A}
}
```

**IEEE Citation:**

> A. Abdiansah, N. Yusliani, F. Fathoni, M. F. Nizar, A. Salsabella and A. A. Davi, "IDSpider: Indonesian Standard Dataset for Text-to-SQL," _2024 Ninth International Conference on Informatics and Computing (ICIC)_, Medan, Indonesia, 2024, pp. 1-6, doi: 10.1109/ICIC64337.2024.10956918.

> M. F. Nizar and A. Abdiansah, "Indonesian Cross-Domain Benchmarks for Semantic Parsing and Text-to-SQL," Harvard Dataverse, 2026. [Online]. Available: https://doi.org/10.7910/DVN/C5AO0A.

---

## Original Spider Benchmark

This dataset is derived from the Spider benchmark:

```bibtex
@inproceedings{yu2018spider,
  title     = {Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain
               Semantic Parsing and Text-to-SQL Task},
  author    = {Yu, Tao and Zhang, Rui and Yang, Kai and Yasunaga, Michihiro and Wang,
               Dongxu and Li, James and Ma, James and Li, Irene and Yao, Qingning and
               Roman, Shanelle and Zhang, Zilin and Radev, Dragomir},
  booktitle = {Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing},
  year      = {2018},
  pages     = {3911--3921}
}
```

---

## License

This dataset inherits the license of the original Spider benchmark. Please refer to the [Spider dataset page](https://yale-sea-lab.github.io/spider/) for licensing terms.
