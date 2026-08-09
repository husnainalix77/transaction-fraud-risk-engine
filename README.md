<div align="center">

# 🕵️ Transaction Fraud Risk Engine

### An end-to-end fraud detection system — SQL feature engineering, statistical validation, imbalance-aware modeling, calibration & explainability

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-Modeling-blue?style=for-the-badge)](https://xgboost.readthedocs.io)
[![SciPy](https://img.shields.io/badge/SciPy-Statistical%20Testing-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Calibration-orange?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)]()

</div>

---

## 📌 Problem Statement

Card-not-present and online payment fraud costs the payments industry **billions annually**. This project builds a fraud detection pipeline designed to handle the problem properly, not chase a misleading accuracy score:

- 🎯 Fraud is rare (**~3.5%** of transactions) — accuracy alone is a meaningless metric here
- ⏳ Fraud patterns shift over time — validation must respect chronological order
- 🔍 A production fraud model needs to be explainable, not a black box
- 📊 Every feature and modeling decision is backed by tested evidence, not assumption — including honest documentation of approaches that didn't work

---

## 🏗️ System Architecture

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
│  + 65 Vesta V-columns        │    (added after evidence-based
│    (low missingness)         │     model expansion in Phase 5)
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
│ Time-Aware Train/Val Split  │  ← Zero-overlap verified
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Imbalance-Aware Modeling &   │  ← scale_pos_weight + Platt
│      Calibration             │    calibration, 5 approaches
│  Final PR-AUC: 0.2857        │    tested, best one kept
└─────────────┬───────────────┘
              │
              ▼
        Ready for Phase 6:
   Explainability & Permutation Importance
```

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data storage | MySQL + SQLAlchemy | Structured storage, chunked ingestion |
| Feature engineering | SQL (CTEs, window functions) | Behavioral aggregates at the database layer |
| Processing | Pandas + NumPy | Chunked reading, downcasting, imputation |
| Statistical testing | SciPy (chi2_contingency, ks_2samp) | Formal significance testing |
| Modeling | XGBoost, scikit-learn | Imbalance-aware classification |
| Calibration | CalibratedClassifierCV (Platt scaling) | Trustworthy probability outputs |
| Visualization | Matplotlib + Seaborn | EDA, PR curves, reliability diagrams |
| Environment | Python venv, Jupyter notebooks, `.env` | Reproducible, secure, iterative workflow |

---

## ✅ Project Progress

| Phase | Description | Status |
|---|---|---|
| 1 | MySQL Ingestion & Verification | ✅ Complete |
| 2 | SQL Feature Engineering | ✅ Complete |
| 3 | Statistical Validation (EDA) | ✅ Complete |
| 4 | Time-Aware Train/Validation Split | ✅ Complete |
| 5 | Imbalance-Aware Modeling & Calibration | ✅ Complete |
| 6 | Explainability & Permutation Importance | ⏳ Not started |
| 7 | Streamlit Dashboard & Final Docs | ⏳ Not started |

---

## 🗄️ Phase 1 — MySQL Ingestion & Verification

Chunked loading pipeline (20,000 rows/chunk, memory-safe on 8GB RAM), fully verified — row counts, columns, nulls, and values all confirmed matching between source CSVs and MySQL.

**Key finding:** ~75% of transactions have no matching identity record — carried forward as a deliberate feature (`has_identity_data`).

Log: [`docs/phase1_verification.md`](docs/phase1_verification.md)

---

## 🔍 Phase 2 — SQL Feature Engineering

Built entirely in SQL using CTEs and window functions: `has_identity_data`, `card_txn_count_so_far`, `card_avg_amt_so_far`, `amt_deviation_ratio` — all rolling features respect time order (no future-data leakage).

**Later expanded (during Phase 5)** with 65 raw Vesta V-columns, selected specifically for low missingness (<0.06%), after simpler improvement attempts plateaued.

Logic: [`sql/feature_engineering.sql`](sql/feature_engineering.sql) · Log: [`docs/phase2_feature_engineering.md`](docs/phase2_feature_engineering.md)

---

## 📊 Phase 3 — Statistical Validation (EDA)

All 7 core features (4 categorical, 3 numeric) tested visually and statistically — chi-square for categorical, KS-test for numeric. All passed significance testing. `amt_deviation_ratio` (engineered) was the strongest single predictor found.

Notebook: [`notebooks/03_eda_statistical_validation.ipynb`](notebooks/03_eda_statistical_validation.ipynb) · Log: [`docs/phase3_eda_statistical_validation.md`](docs/phase3_eda_statistical_validation.md)

---

## ⏳ Phase 4 — Time-Aware Train/Validation Split

Split by `TransactionDT` (chronological order), not randomly — train on the past, test on the future, exactly as the model would be used in production.

| Set | Rows | % |
|---|---|---|
| Train | 472,433 | 80.0% |
| Test | 118,107 | 20.0% |

**Zero overlap verified:** train max `TransactionDT` (12,192,900) < test min (12,192,911).

Log: [`docs/phase4_time_aware_split.md`](docs/phase4_time_aware_split.md)

---

## 🎯 Phase 5 — Imbalance-Aware Modeling & Calibration

The core modeling phase. Every technique was tested empirically and judged on **PR-AUC**, not accuracy — a default XGBoost model actually scored *lower* accuracy (0.9648) than a naive "always predict not-fraud" baseline (0.9656), concrete proof accuracy is the wrong metric under ~3.5% class imbalance.

### Full Experimentation Log

| Approach | Result | Decision |
|---|---|---|
| Baseline (default XGBoost) | Accuracy 0.9648 (< naive 0.9656) | Proved accuracy is misleading here |
| `scale_pos_weight` | PR-AUC 0.1907 | ✅ Adopted over SMOTE |
| SMOTE (synthetic oversampling) | PR-AUC 0.1837 | ❌ Rejected — empirically worse |
| Hyperparameter tuning (GridSearchCV, 108 fits) | PR-AUC 0.1903 | ❌ Rejected — negligible improvement |
| Engineered `time_since_last_txn` + `transaction_hour` | PR-AUC 0.1533–0.1809 | ❌ Rejected — made the model worse |
| **+65 Vesta V-columns** (low missingness, added in two evidence-based rounds) | **PR-AUC 0.2857** | ✅ **Final model** |

### Calibration

`scale_pos_weight` produced a severely over-confident model (predicted ~0.91 probability corresponded to only ~0.60 actual fraud rate). **Platt scaling** (via `CalibratedClassifierCV`, 5-fold internal CV to avoid calibrating on already-seen training data) corrected this, meaningfully improving reliability and PR-AUC.

### Final Model & Threshold

**Final model:** XGBoost + `scale_pos_weight` + Platt calibration, 214 features (65 raw V-columns + original 11 engineered/raw features), **threshold = 0.16**

| Metric | Value |
|---|---|
| Precision (Fraud) | 0.30 |
| Recall (Fraud) | 0.37 |
| F1-score (Fraud) | 0.33 |
| PR-AUC | **0.2857** |
| Fraud caught | 1,504 / 4,063 |
| Fraud missed | 2,559 |
| False alarms | 3,578 |

**Threshold justification:** in fraud detection, a missed fraud case (direct financial loss) is generally costlier than a false alarm (a flagged transaction for review). The threshold is chosen just below the precision/recall crossing point (~0.17–0.18), deliberately leaning toward recall.

**Honest limitations:**
- Recall of 37% means nearly two-thirds of fraud still goes undetected — a genuine ceiling given the current feature set and single-model approach, not an unexplored optimization.
- The threshold reflects a default cost assumption (missed fraud > false alarm), not an actual calculated cost ratio — a real deployment would need true business cost figures to set this optimally.
- Matching industry-standard performance (70–90%+ recall with manageable false alarms) would require substantially more features, ensemble modeling, and continuously updated production data — outside this project's scope.

Notebook: [`notebooks/05_modeling_and_calibration.ipynb`](notebooks/05_modeling_and_calibration.ipynb) · Log: [`docs/phase5_progress_so_far.md`](docs/phase5_progress_so_far.md)

---

## 📁 Repository Structure

```
transaction-fraud-risk-engine/
│
├── data/
│   ├── raw/                       # source CSVs (gitignored)
│   └── processed/
│       ├── engineered_features.csv
│       ├── train_set.csv / test_set.csv
│       └── train_set_v2.csv / test_set_v2.csv  # with V-columns
│
├── sql/
│   └── feature_engineering.sql
│
├── notebooks/
│   ├── 01_inspect_data.py
│   ├── 02_verify_features.py
│   ├── 03_eda_statistical_validation.ipynb
│   ├── 04_time_aware_split.ipynb
│   └── 05_modeling_and_calibration.ipynb
│
├── src/
│   ├── load_to_mysql.py
│   ├── verify_load.py
│   └── build_features.py
│
├── models/
│   ├── fraud_model_final.pkl
│   └── feature_columns_final.pkl
│
├── docs/
│   ├── phase1_verification.md
│   ├── phase2_feature_engineering.md
│   ├── phase3_eda_statistical_validation.md
│   ├── phase4_time_aware_split.md
│   └── phase5_progress_so_far.md
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 Key Engineering Decisions

**Why SQL feature engineering over pandas-only?**
Reflects production feature pipelines built against a live database; forces genuine practice with joins, CTEs, and window functions at scale.

**Why time-based validation, not random?**
This dataset is time-ordered, with rolling features built from chronological history. A random split would let the model implicitly access future information — inflating results in a way that wouldn't hold in real deployment.

**Why PR-AUC over accuracy as the primary metric?**
With ~3.5% fraud prevalence, accuracy is trivially high and uninformative — proven directly when a trained model scored *below* a naive baseline.

**Why calibrate before choosing a threshold?**
`scale_pos_weight` distorts raw probability outputs. Calibration ensures the final threshold decision rests on numbers that genuinely reflect real-world fraud likelihood, not artificially inflated confidence.

**Why test SMOTE, tuning, and new features — and reject all three?**
Each was a reasonable, well-motivated hypothesis, tested properly and judged on PR-AUC rather than assumed superior for being more sophisticated. Two of three genuinely helped nothing; one made results worse. Reporting negative results honestly is as valuable as reporting positive ones — it demonstrates real experimentation, not a curated success story.

**Why expand to V-columns instead of continuing to hand-engineer features?**
After exhausting reasonable hand-engineered features from the base dataset, the evidence (persistent PR-AUC plateau despite tuning and new feature attempts) pointed to a feature *scope* limitation, not a technique limitation. Vesta's own engineered V-columns — previously unused — were the correct, evidence-based next lever, and testing confirmed this (0.1907 → 0.2857 PR-AUC).

**Why stop at 65 V-columns instead of adding more or all 339?**
Diminishing returns and rising missingness/complexity in further columns, balanced against real project scope discipline. Two rounds of clean, low-missingness columns each produced comparable gains; a third round would introduce meaningfully higher missingness and imputation complexity for uncertain additional benefit — a reasonable stopping point, documented as such rather than pursued indefinitely.

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