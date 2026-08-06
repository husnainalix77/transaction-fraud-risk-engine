<div align="center">

# 🕵️ Transaction Fraud Risk Engine

### An end-to-end fraud detection system — SQL feature engineering, statistical validation, time-aware modeling, calibration & explainability

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)](https://sqlalchemy.org)
[![Pandas](https://img.shields.io/badge/Pandas-Latest-blue?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![SciPy](https://img.shields.io/badge/SciPy-Statistical%20Testing-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org)
[![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)]()

</div>

---

## 📌 Problem Statement

Card-not-present and online payment fraud costs the payments industry **billions annually**. This project builds a fraud detection pipeline designed to handle the problem properly, not chase a misleading accuracy score:

- 🎯 Fraud is rare (**~3.5%** of transactions) — accuracy alone is a meaningless metric here
- ⏳ Fraud patterns shift over time — validation must respect chronological order
- 🔍 A production fraud model needs to be explainable, not a black box
- 📊 Every feature used must be backed by statistical evidence, not assumption

---

## 🏗️ System Architecture (built so far)

```
train_transaction.csv + train_identity.csv
                │
                ▼
┌───────────────────────────┐
│  MySQL (chunked ingestion) │  ← Memory-safe load, fully verified
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│  SQL Feature Engineering    │  ← LEFT JOIN, CTEs, window functions
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Statistical Validation (EDA)│  ← Chi-square + KS-tests
│  7/7 features confirmed      │
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Time-Aware Train/Val Split  │  ← Sorted by TransactionDT
│  Train: 472,433 (80%)        │    Zero-overlap verified
│  Test:  118,107 (20%)        │
└─────────────┬───────────────┘
              │
              ▼
        Ready for Phase 5:
   Imbalance-Aware Modeling & Calibration
```

---

## ⚙️ Tech Stack (used so far)

| Layer | Technology | Purpose |
|---|---|---|
| Data storage | MySQL + SQLAlchemy | Structured storage, chunked ingestion |
| Feature engineering | SQL (CTEs, window functions) | Behavioral aggregates at the database layer |
| Processing | Pandas + NumPy | Chunked reading, downcasting, splitting |
| Statistical testing | SciPy (chi2_contingency, ks_2samp) | Formal significance testing |
| Visualization | Matplotlib + Seaborn | Bar charts, histograms, box plots |
| Environment | Python venv, Jupyter notebooks, `.env` | Reproducible, secure, iterative workflow |

---

## ✅ Project Progress

| Phase | Description | Status |
|---|---|---|
| 1 | MySQL Ingestion & Verification | ✅ Complete |
| 2 | SQL Feature Engineering | ✅ Complete |
| 3 | Statistical Validation (EDA) | ✅ Complete |
| 4 | Time-Aware Train/Validation Split | ✅ Complete |
| 5 | Imbalance-Aware Modeling & Calibration | ⏳ Not started |
| 6 | Explainability & Permutation Importance | ⏳ Not started |
| 7 | Streamlit Dashboard & Final Docs | ⏳ Not started |

---

## 🗄️ Phase 1 — MySQL Ingestion & Verification

- ✅ Chunked loading pipeline (20,000 rows/chunk) — memory-safe on 8GB RAM
- ✅ Full independent verification — row counts, columns, nulls, and values

```
raw_transactions : CSV 590,540 rows  ↔  MySQL 590,540 rows   MATCH
raw_identity      : CSV 144,233 rows ↔  MySQL 144,233 rows   MATCH
```

**Key finding:** ~75% of transactions have no matching identity record — carried forward as a deliberate feature (`has_identity_data`).

Full log: [`docs/phase1_verification.md`](docs/phase1_verification.md)

---

## 🔍 Phase 2 — SQL Feature Engineering

Built entirely in SQL using CTEs and window functions.

**Features built:** `has_identity_data`, `card_txn_count_so_far`, `card_avg_amt_so_far`, `amt_deviation_ratio` — all rolling features use `ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING`, preventing future-data leakage.

Logic: [`sql/feature_engineering.sql`](sql/feature_engineering.sql) · Log: [`docs/phase2_feature_engineering.md`](docs/phase2_feature_engineering.md)

---

## 📊 Phase 3 — Statistical Validation (EDA)

All 7 features (4 categorical, 3 numeric) tested visually and statistically.

| Feature | Test | Result |
|---|---|---|
| ProductCD | Chi-square | ✅ χ²=16,742 |
| card4, card6 | Chi-square | ✅ χ²=365 / 5,957 |
| has_identity_data | Chi-square | ✅ χ²=10,684 |
| TransactionAmt | KS-test | ✅ D=0.076 |
| amt_deviation_ratio | KS-test | ✅ D=0.099 (strongest predictor) |
| card_txn_count_so_far | KS-test | ✅ D=0.059 |

Notebook: [`notebooks/03_eda_statistical_validation.ipynb`](notebooks/03_eda_statistical_validation.ipynb) · Log: [`docs/phase3_eda_statistical_validation.md`](docs/phase3_eda_statistical_validation.md)

---

## ⏳ Phase 4 — Time-Aware Train/Validation Split

Split the dataset by `TransactionDT` (chronological order) rather than randomly, to prevent the model from ever training on data that occurred after what it's evaluated on.

| Set | Rows | % | TransactionDT Range |
|---|---|---|---|
| Train | 472,433 | 80.0% | 86,400 – 12,192,900 |
| Test | 118,107 | 20.0% | 12,192,911 – 15,811,131 |

**Leakage verification:**
```
Train max TransactionDT: 12,192,900
Test min TransactionDT:  12,192,911   →  zero overlap, 11-second gap
```

**Why this matters:** a random split would let the model implicitly "see the future" relative to transactions it's tested on — since our rolling features (`card_avg_amt_so_far`, etc.) are built entirely on chronological history, this would silently invalidate the model's real-world reliability. This split mirrors exactly how the model would be used in production: trained on the past, evaluated only on data it has never seen.

Notebook: [`notebooks/04_time_aware_split.ipynb`](notebooks/04_time_aware_split.ipynb) · Log: [`docs/phase4_time_aware_split.md`](docs/phase4_time_aware_split.md)

---

## 📁 Repository Structure

```
transaction-fraud-risk-engine/
│
├── data/
│   ├── raw/                       # source CSVs (gitignored)
│   └── processed/
│       ├── engineered_features.csv
│       ├── train_set.csv
│       └── test_set.csv
│
├── sql/
│   └── feature_engineering.sql
│
├── notebooks/
│   ├── 01_inspect_data.py
│   ├── 02_verify_features.py
│   ├── 03_eda_statistical_validation.ipynb
│   └── 04_time_aware_split.ipynb
│
├── src/
│   ├── load_to_mysql.py
│   ├── verify_load.py
│   └── build_features.py
│
├── docs/
│   ├── phase1_verification.md
│   ├── phase2_feature_engineering.md
│   ├── phase3_eda_statistical_validation.md
│   └── phase4_time_aware_split.md
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 Key Engineering Decisions

**Why chunked loading instead of `LOAD DATA INFILE`?**
Avoided hand-writing a 394-column `CREATE TABLE` statement while keeping memory use safe on 8GB RAM.

**Why SQL feature engineering over pandas-only?**
Reflects production feature pipelines built against a live database; forces genuine practice with joins, CTEs, and window functions at scale.

**Why statistically test every feature before modeling?**
Visual patterns can be misleading — a striking chart can rest on a tiny sample size. Chi-square and KS-tests give an objective, quantified answer that accounts for sample size.

**Why a time-based split instead of random?**
This dataset is time-ordered, and several engineered features are built explicitly from chronological history. A random split would let the model implicitly access future information during training — inflating validation performance in a way that wouldn't hold up in real deployment. Splitting by `TransactionDT` and verifying zero overlap directly guarantees this can't happen.

**Why defer imputation and X/y separation to Phase 5?**
Keeps each phase narrowly scoped and independently provable. Imputation values must be calculated only from the training set (never the validation set) to avoid leaking validation-period statistics — this is only possible to do correctly *after* the split exists.

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