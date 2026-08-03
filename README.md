<div align="center">

# 🕵️ Transaction Fraud Risk Engine

### An end-to-end fraud detection system — SQL feature engineering, imbalance-aware ML, calibration & explainability

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)](https://sqlalchemy.org)
[![Pandas](https://img.shields.io/badge/Pandas-Latest-blue?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)]()

</div>

---

## 📌 Problem Statement

Card-not-present and online payment fraud costs the payments industry **billions annually**. This project builds a fraud detection pipeline designed to handle the problem properly, not chase a misleading accuracy score:

- 🎯 Fraud is rare (**~3.5%** of transactions) — a model predicting "not fraud" every time is already ~96% accurate and useless
- ⏳ Fraud patterns shift over time — validation must respect chronological order, not random shuffling
- 🔍 A production fraud model needs to be explainable, not a black box

---

## 🏗️ System Architecture (built so far)

```
train_transaction.csv + train_identity.csv
                │
                ▼
┌───────────────────────────┐
│  MySQL (chunked ingestion) │  ← Memory-safe load, fully verified
│ raw_transactions/identity   │
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│  SQL Feature Engineering    │  ← LEFT JOIN, CTEs, window functions
│  (has_identity_data,         │
│   card_txn_count_so_far,     │
│   card_avg_amt_so_far,       │
│   amt_deviation_ratio)       │
└─────────────┬───────────────┘
              │
              ▼
      data/processed/engineered_features.csv
```

---

## ⚙️ Tech Stack (used so far)

| Layer | Technology | Purpose |
|---|---|---|
| Data storage | MySQL + SQLAlchemy | Structured storage, chunked ingestion |
| Feature engineering | SQL (CTEs, window functions) | Behavioral aggregates computed at the database layer |
| Processing | Pandas + NumPy | Chunked reading, type downcasting, final feature pull |
| Environment | Python venv, `.env` credentials | Reproducible, secure local setup |

---

## ✅ Project Progress

| Phase | Description | Status |
|---|---|---|
| 1 | MySQL Ingestion & Verification | ✅ Complete |
| 2 | SQL Feature Engineering | ✅ Complete |
| 3 | Statistical Validation (EDA) | ⏳ Not started |
| 4 | Time-Aware Train/Validation Split | ⏳ Not started |
| 5 | Imbalance-Aware Modeling & Calibration | ⏳ Not started |
| 6 | Explainability & Permutation Importance | ⏳ Not started |
| 7 | Streamlit Dashboard & Final Docs | ⏳ Not started |

---

## 🗄️ Phase 1 — MySQL Ingestion & Verification

- ✅ Chunked loading pipeline (20,000 rows/chunk) — memory-safe on 8GB RAM
- ✅ Numeric type downcasting to reduce memory footprint per chunk
- ✅ Full independent verification — row counts, columns, nulls, and values, all proven, not assumed

```
raw_transactions : CSV 590,540 rows  ↔  MySQL 590,540 rows   MATCH
raw_transactions : CSV 394 columns   ↔  MySQL 394 columns    MATCH
raw_identity      : CSV 144,233 rows ↔  MySQL 144,233 rows   MATCH
raw_identity      : CSV 41 columns   ↔  MySQL 41 columns     MATCH
Null-count parity (sampled columns)  : MATCH
Value-level spot-check (10 rows)     : MATCH
```

**Key finding:** ~75% of transactions have no matching identity record. This missingness was carried forward as a deliberate feature (`has_identity_data`) in Phase 2, rather than dropped.

Full verification log: [`docs/phase1_verification.md`](docs/phase1_verification.md)

---

## 🔍 Phase 2 — SQL Feature Engineering

Built entirely in SQL against the MySQL tables — no pandas merges — using CTEs to keep each stage of the logic readable and testable on its own.

**What was built:**
- **`LEFT JOIN`** on `TransactionID` — keeps all 590,540 transactions, whether or not identity data exists
- **`has_identity_data`** — 1/0 flag converting the join's NULL pattern into a usable model feature
- **`card_txn_count_so_far`** — rolling count of a card's prior transactions, computed via a window function partitioned by `card1` and ordered by `TransactionDT`
- **`card_avg_amt_so_far`** — rolling average of a card's prior transaction amounts, same time-respecting window
- **`amt_deviation_ratio`** — this transaction's amount divided by that card's historical average, surfacing "how unusual is this spend, for this specific card"

**Critical design detail:** every rolling feature uses `ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING` — meaning each row's calculation only ever looks at *earlier* transactions for that card, never the current or future ones. This avoids leaking future information into features describing the past.

**Verified output:**
```
Rows: 590,540 | Columns: 14
card_txn_count_so_far  → 0 nulls (every transaction gets a count)
card_avg_amt_so_far    → 13,553 nulls (each card's first transaction — no prior history)
amt_deviation_ratio    → 13,553 nulls (same rows, exactly — confirms internal consistency)
```

**Example — card `13926`'s transaction history:**

| TransactionAmt | card_txn_count_so_far | card_avg_amt_so_far | amt_deviation_ratio |
|---|---|---|---|
| 68.5 | 0 | NULL | NULL |
| 150.0 | 1 | 68.5 | 2.19 |
| 100.0 | 2 | 109.25 | 0.92 |
| 500.0 | 9 | 125.06 | 4.00 |

The last row shows exactly the kind of signal this feature is meant to surface: a transaction **4x** this card's historical average — a pattern a raw `TransactionAmt` column alone could never express.

Feature engineering logic: [`sql/feature_engineering.sql`](sql/feature_engineering.sql)

---

## 📁 Repository Structure

```
transaction-fraud-risk-engine/
│
├── data/
│   ├── raw/                       # source CSVs (gitignored)
│   └── processed/
│       └── engineered_features.csv
│
├── sql/
│   └── feature_engineering.sql    # join + CTEs + window functions
│
├── notebooks/
│   ├── 01_inspect_data.py         # baseline CSV shape/inspection
│   └── 02_verify_features.py      # engineered feature verification
│
├── src/
│   ├── load_to_mysql.py           # chunked, memory-safe ingestion
│   ├── verify_load.py             # row/column/null/value verification
│   └── build_features.py          # runs feature_engineering.sql, saves CSV
│
├── docs/
│   └── phase1_verification.md     # full ingestion verification log
│
├── .env                           # MySQL credentials (not in repo)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 Key Engineering Decisions

**Why chunked loading instead of `LOAD DATA INFILE`?**
`LOAD DATA INFILE` is faster but requires hand-writing a 394-column
`CREATE TABLE` statement and direct file-system access for MySQL.
Chunked `to_sql()` lets pandas infer the schema automatically and
keeps memory use safe on 8GB RAM — the right tradeoff for this
one-time ingestion job.

**Why verify the load instead of trusting it?**
Chunked loading can silently cause type-inference mismatches or
truncated values across chunk boundaries. Row counts alone don't
catch this — full verification (columns, nulls, value spot-checks)
does.

**Why SQL feature engineering over pandas-only?**
Reflects how production feature pipelines are typically built
against a live database, and forces genuine practice with joins,
CTEs, and window functions at real scale.

**Why time-respecting window functions specifically?**
A card's "rolling average" must only include transactions that
happened *before* the current one — otherwise the feature leaks
future information into a signal meant to describe the past, which
would silently inflate model performance later.

**Why split the average and ratio calculation into two separate CTEs?**
An earlier version recalculated the same `AVG(...) OVER(...)` window
function four times inside one query, which caused it to hang on the
full 590K-row dataset. Computing the average once and reusing it via
simple division fixed this — a real lesson in avoiding redundant
computation in SQL.

---

## 👨‍💻 About the Author

<div align="center">

**Husnain Maroof**

3rd Year Mechatronics & Control Engineering
University of Engineering & Technology (UET), Lahore

*Open to remote opportunities in Data Science & ML Engineering*

[![GitHub](https://img.shields.io/badge/GitHub-husnainalix77-black?style=for-the-badge&logo=github)](https://github.com/husnainalix77)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Husnain%20Maroof-blue?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/husnainalix77)

</div>

---

<div align="center">

⭐ **Star this repo to follow the build progress** ⭐

*This is an independent learning/portfolio project — not affiliated with Kaggle, IEEE-CIS, or Vesta Corporation.*

</div>