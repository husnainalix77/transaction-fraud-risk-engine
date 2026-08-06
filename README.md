<div align="center">

# 🕵️ Transaction Fraud Risk Engine

### An end-to-end fraud detection system — SQL feature engineering, statistical validation, imbalance-aware ML, calibration & explainability

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
┌───────────────────────────┐
│ Statistical Validation (EDA)│  ← Chi-square + KS-tests confirm
│  7/7 features confirmed      │    every feature statistically
│  statistically significant   │
└─────────────┬───────────────┘
              │
              ▼
        Ready for Phase 4:
    Time-Aware Train/Validation Split
```

---

## ⚙️ Tech Stack (used so far)

| Layer | Technology | Purpose |
|---|---|---|
| Data storage | MySQL + SQLAlchemy | Structured storage, chunked ingestion |
| Feature engineering | SQL (CTEs, window functions) | Behavioral aggregates computed at the database layer |
| Processing | Pandas + NumPy | Chunked reading, type downcasting, feature pull |
| Statistical testing | SciPy (chi2_contingency, ks_2samp) | Formal significance testing of every candidate feature |
| Visualization | Matplotlib + Seaborn | EDA bar charts, histograms, box plots |
| Environment | Python venv, Jupyter notebooks, `.env` credentials | Reproducible, secure, iterative analysis setup |

---

## ✅ Project Progress

| Phase | Description | Status |
|---|---|---|
| 1 | MySQL Ingestion & Verification | ✅ Complete |
| 2 | SQL Feature Engineering | ✅ Complete |
| 3 | Statistical Validation (EDA) | ✅ Complete |
| 4 | Time-Aware Train/Validation Split | ⏳ Not started |
| 5 | Imbalance-Aware Modeling & Calibration | ⏳ Not started |
| 6 | Explainability & Permutation Importance | ⏳ Not started |
| 7 | Streamlit Dashboard & Final Docs | ⏳ Not started |

---

## 🗄️ Phase 1 — MySQL Ingestion & Verification

- ✅ Chunked loading pipeline (20,000 rows/chunk) — memory-safe on 8GB RAM
- ✅ Numeric type downcasting to reduce memory footprint per chunk
- ✅ Full independent verification — row counts, columns, nulls, and values, all proven

```
raw_transactions : CSV 590,540 rows  ↔  MySQL 590,540 rows   MATCH
raw_identity      : CSV 144,233 rows ↔  MySQL 144,233 rows   MATCH
Null-count parity (sampled columns)  : MATCH
Value-level spot-check (10 rows)     : MATCH
```

**Key finding:** ~75% of transactions have no matching identity record — carried forward as a deliberate feature (`has_identity_data`) rather than dropped.

Full log: [`docs/phase1_verification.md`](docs/phase1_verification.md)

---

## 🔍 Phase 2 — SQL Feature Engineering

Built entirely in SQL using CTEs and window functions — no pandas merges.

**Features built:**
- **`has_identity_data`** — 1/0 flag for identity match
- **`card_txn_count_so_far`** — rolling, time-respecting count of a card's prior transactions
- **`card_avg_amt_so_far`** — rolling, time-respecting average transaction amount per card
- **`amt_deviation_ratio`** — this transaction's amount ÷ that card's historical average

**Critical design detail:** every rolling feature uses `ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING` — only prior transactions are used, preventing future-data leakage.

Logic: [`sql/feature_engineering.sql`](sql/feature_engineering.sql) · Log: [`docs/phase2_feature_engineering.md`](docs/phase2_feature_engineering.md)

---

## 📊 Phase 3 — Statistical Validation (EDA)

Every raw and engineered feature was tested visually (bar charts, histograms, box plots) **and** statistically (chi-square for categorical, KS-test for numeric) before being trusted for modeling.

### Categorical Features (Chi-Square Test)

| Feature | Fraud Rate Range | Chi-Square Statistic | p-value | Result |
|---|---|---|---|---|
| ProductCD | 2.0% – 11.7% | 16,742.17 | ~0.0000 | ✅ Significant |
| card4 (network) | 2.9% – 7.7% | 364.87 | ~8.97e-79 | ✅ Significant |
| card6 (type) | 2.5% – 6.7% | 5,957.03 | ~0.0000 | ✅ Significant |
| has_identity_data | 2.1% – 7.8% | 10,683.64 | ~0.0000 | ✅ Significant |

### Numeric Features (Kolmogorov-Smirnov Test)

| Feature | KS Statistic (D) | p-value | Result |
|---|---|---|---|
| TransactionAmt | 0.0756 | ~1.09e-99 | ✅ Significant |
| amt_deviation_ratio | 0.0986 | ~3.22e-166 | ✅ Significant |
| card_txn_count_so_far | 0.0587 | ~3.72e-60 | ✅ Significant |

**Key findings:**
- **All 7 features tested — raw and engineered — passed statistical significance testing.**
- **`amt_deviation_ratio` (Phase 2 engineered feature) was the strongest individual predictor found**, outperforming raw `TransactionAmt` on both visual separation and KS statistic — directly validating the Phase 2 feature engineering effort.
- **`has_identity_data` produced the most striking result**: a 3.7x higher fraud rate for transactions with identity data (7.8%) vs. without (2.1%).
- **Volume checks mattered** — confirmed `ProductCD = W`'s low fraud rate still represents large absolute fraud volume (75% of all transactions), and exposed two `card6` categories with statistically meaningless 0% rates due to near-zero sample size.

Full notebook: [`notebooks/03_eda_statistical_validation.ipynb`](notebooks/03_eda_statistical_validation.ipynb)

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
│   └── feature_engineering.sql
│
├── notebooks/
│   ├── 01_inspect_data.py
│   ├── 02_verify_features.py
│   └── 03_eda_statistical_validation.ipynb
│
├── src/
│   ├── load_to_mysql.py
│   ├── verify_load.py
│   └── build_features.py
│
├── docs/
│   ├── phase1_verification.md
│   └── phase2_feature_engineering.md
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 Key Engineering Decisions

**Why chunked loading instead of `LOAD DATA INFILE`?**
Avoided hand-writing a 394-column `CREATE TABLE` statement while keeping
memory use safe on 8GB RAM.

**Why SQL feature engineering over pandas-only?**
Reflects production feature pipelines built against a live database;
forces genuine practice with joins, CTEs, and window functions at scale.

**Why time-respecting window functions?**
Rolling features must only use transactions prior to the current one,
preventing future-data leakage into a signal meant to describe the past.

**Why statistically test every feature before modeling, not just visualize?**
Visual patterns can be misleading — a striking chart can rest on a tiny
sample size (as seen with `card6`'s 0%-fraud categories). Chi-square and
KS-tests give an objective, quantified answer that accounts for sample
size, rather than relying on subjective visual impression.

**Why check transaction volume alongside fraud rate?**
A low fraud rate on a high-volume category (`ProductCD = W`, 75% of all
transactions) can represent more absolute fraud than a high rate on a
small category — rate alone can be misleading without volume context.

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