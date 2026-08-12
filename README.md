<div align="center">

# 🕵️ Transaction Fraud Risk Engine

### An end-to-end fraud detection system — SQL feature engineering, statistical validation, imbalance-aware modeling, calibration & explainability

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-Modeling-blue?style=for-the-badge)](https://xgboost.readthedocs.io)
[![SciPy](https://img.shields.io/badge/SciPy-Statistical%20Testing-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org)
[![SHAP](https://img.shields.io/badge/SHAP-Explainability-purple?style=for-the-badge)](https://shap.readthedocs.io)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Calibration-orange?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)]()

</div>

---

## 📌 Problem Statement

Card-not-present and online payment fraud costs the payments industry **billions annually**. This project builds a fraud detection pipeline designed to handle the problem properly, not chase a misleading accuracy score:

- 🎯 Fraud is rare (**~3.5%** of transactions) — accuracy alone is a meaningless metric here
- ⏳ Fraud patterns shift over time — validation must respect chronological order
- 🔍 A production fraud model needs to be explainable, not a black box
- 📊 Every decision is backed by tested evidence, including honest documentation of approaches that didn't work

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
│  + 65 Vesta V-columns        │
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Statistical Validation (EDA)│  ← Chi-square + KS-tests
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Time-Aware Train/Val Split  │  ← Zero-overlap verified
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Imbalance-Aware Modeling &   │  ← Final PR-AUC: 0.2857
│      Calibration             │
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│  Explainability             │  ← SHAP + Permutation Importance
│  (SHAP + Permutation)        │    converge on same core drivers
└─────────────┬───────────────┘
              │
              ▼
        Ready for Phase 7:
      Streamlit Dashboard
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
| Explainability | SHAP, permutation_importance | Model interpretability, per-prediction and global |
| Visualization | Matplotlib + Seaborn | EDA, PR curves, reliability diagrams, SHAP plots |
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
| 6 | Explainability & Permutation Importance | ✅ Complete |
| 7 | Streamlit Dashboard & Final Docs | ⏳ Not started |

---

## 🗄️ Phase 1 — MySQL Ingestion & Verification

Chunked loading pipeline, fully verified — row counts, columns, nulls, and values all confirmed matching. **Key finding:** ~75% of transactions have no matching identity record — carried forward as a deliberate feature (`has_identity_data`).

Log: [`docs/phase1_verification.md`](docs/phase1_verification.md)

---

## 🔍 Phase 2 — SQL Feature Engineering

Built in SQL using CTEs and window functions: `has_identity_data`, `card_txn_count_so_far`, `card_avg_amt_so_far`, `amt_deviation_ratio`. Later expanded (during Phase 5) with 65 raw Vesta V-columns, selected for low missingness.

Logic: [`sql/feature_engineering.sql`](sql/feature_engineering.sql) · Log: [`docs/phase2_feature_engineering.md`](docs/phase2_feature_engineering.md)

---

## 📊 Phase 3 — Statistical Validation (EDA)

All 7 core features tested visually and statistically (chi-square, KS-test). All passed significance testing. `amt_deviation_ratio` was the strongest single predictor found.

Notebook: [`notebooks/03_eda_statistical_validation.ipynb`](notebooks/03_eda_statistical_validation.ipynb) · Log: [`docs/phase3_eda_statistical_validation.md`](docs/phase3_eda_statistical_validation.md)

---

## ⏳ Phase 4 — Time-Aware Train/Validation Split

Split by `TransactionDT`, not randomly. Zero overlap verified (train max 12,192,900 < test min 12,192,911).

Log: [`docs/phase4_time_aware_split.md`](docs/phase4_time_aware_split.md)

---

## 🎯 Phase 5 — Imbalance-Aware Modeling & Calibration

Every technique tested empirically, judged on PR-AUC, not accuracy — a default model actually scored *lower* accuracy (0.9648) than a naive baseline (0.9656), proving accuracy is the wrong metric here.

| Approach | PR-AUC | Decision |
|---|---|---|
| `scale_pos_weight` | 0.1907 | ✅ Adopted over SMOTE |
| SMOTE | 0.1837 | ❌ Rejected |
| Hyperparameter tuning | 0.1903 | ❌ Rejected — negligible gain |
| Engineered time/hour features | 0.1533–0.1809 | ❌ Rejected — hurt performance |
| +65 Vesta V-columns (two rounds) | **0.2857** | ✅ **Final model** |

**Final model:** XGBoost + `scale_pos_weight` + Platt calibration, 214 features, threshold = 0.16 → Precision 0.30, Recall 0.37, PR-AUC 0.2857 (~50% relative improvement over the original feature set).

Notebook: [`notebooks/05_modeling_and_calibration.ipynb`](notebooks/05_modeling_and_calibration.ipynb) · Log: [`docs/phase5_modeling_and_calibration.md`](docs/phase5_modeling_and_calibration.md)

---

## 🔬 Phase 6 — Explainability & Permutation Importance

Two independent explainability methods — SHAP and permutation importance — applied to confirm the model's behavior is interpretable and consistent with real-world fraud intuition, not a black box.

**Global findings:** both methods independently agree `TransactionAmt`, `V303`, `ProductCD_C`, and `card1` are the model's core drivers — strong convergent evidence. The Phase 5 V-column expansion is validated: multiple V-columns rank highly by both methods.

**Divergence, fully explained:** `card_avg_amt_so_far` ranks #10 by SHAP but dead last (#214) by permutation importance — directly confirming the 0.81 correlation with `TransactionAmt` flagged in Phase 5. Permutation importance measures *marginal necessity* (does the model need this specific feature, given everything else), not *standalone value* — a genuinely predictive feature can score low here if a correlated feature already covers the same ground.

**Individual case studies:**
- **True positive** (predicted 0.552): driven by non-`W` product category and an active V303 signal.
- **False positive** (predicted 0.268): several "looks safe" signals were outweighed by one strong risk signal (non-`W` category).
- **False negative** (predicted 0.158, just below the 0.16 threshold): a real fraud case where `TransactionAmt` correctly signaled risk (transaction was 3x the card's average), but the card's "normal-looking" history pulled the prediction just short of the threshold — a concrete illustration of Phase 5's recall ceiling.

Notebook: [`notebooks/06_explainability.ipynb`](notebooks/06_explainability.ipynb) · Log: [`docs/phase6_explainability.md`](docs/phase6_explainability.md)

---

## 📁 Repository Structure

```
transaction-fraud-risk-engine/
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── engineered_features.csv
│       ├── train_set.csv / test_set.csv
│       └── train_set_v2.csv / test_set_v2.csv
│
├── sql/
│   └── feature_engineering.sql
│
├── notebooks/
│   ├── 01_inspect_data.py
│   ├── 02_verify_features.py
│   ├── 03_eda_statistical_validation.ipynb
│   ├── 04_time_aware_split.ipynb
│   ├── 05_modeling_and_calibration.ipynb
│   └── 06_explainability.ipynb
│
├── src/
│   ├── load_to_mysql.py
│   ├── verify_load.py
│   └── build_features.py
│
├── models/
│   ├── fraud_model_final.pkl
│   ├── feature_columns_final.pkl
│   └── decision_threshold.pkl
│
├── docs/
│   ├── phase1_verification.md
│   ├── phase2_feature_engineering.md
│   ├── phase3_eda_statistical_validation.md
│   ├── phase4_time_aware_split.md
│   ├── phase5_modeling_and_calibration.md
│   └── phase6_explainability.md
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 Key Engineering Decisions

**Why SQL feature engineering over pandas-only?** Reflects production feature pipelines built against a live database.

**Why time-based validation, not random?** Prevents the model from implicitly accessing future information during training.

**Why PR-AUC over accuracy?** Proven directly — a trained model scored *below* a naive baseline on accuracy alone.

**Why calibrate before choosing a threshold?** `scale_pos_weight` distorts raw probabilities; calibration ensures the threshold decision rests on trustworthy numbers.

**Why test and reject SMOTE, tuning, and new features?** Each was a reasonable hypothesis, tested and judged on evidence — reporting negative results honestly demonstrates real experimentation.

**Why expand to V-columns, and why stop at 65?** Evidence (a persistent PR-AUC plateau) pointed to a feature-scope limitation. Two rounds of low-missingness columns produced comparable gains each; a third round would face rising missingness and diminishing returns, balanced against real project time constraints.

**Why use two explainability methods instead of one?** SHAP and permutation importance measure fundamentally different things (per-prediction contribution vs. marginal necessity). Using both, and explaining their disagreements, produces a more defensible, audit-ready understanding of the model than either alone — and directly confirms the Phase 5 multicollinearity finding with real evidence.

---

## 🔧 Problems Faced & How They Were Solved

A transparent record of the real technical obstacles encountered throughout this project — kept deliberately, since working through genuine problems is where most of the actual learning happened.

### Phase 1 — Data Ingestion
- **Database name typo** (`fraud_detection` vs. actual `fraude_detection`) caused a "database not found" connection error. Fixed by verifying the real name via `SHOW DATABASES;` and correcting `.env`.
- **`SQLAlchemy` `text()` requirement**: newer SQLAlchemy versions rejected raw SQL strings passed directly to `conn.execute()`. Fixed by wrapping every raw query in `text(...)`.
- **Low disk space warning** during MySQL Workbench autosave — investigated via `Get-PSDrive C` before proceeding, confirmed sufficient space to continue safely.

### Phase 2 — SQL Feature Engineering
- **Repeated query timeouts** ("Lost connection to MySQL server") on the full-scale feature engineering query. Root-caused two ways:
  1. Missing index on `card1`/`TransactionDT` — fixed with `ALTER TABLE ... ADD INDEX`.
  2. Multiple earlier, interrupted query attempts left running in the background (discovered via `SHOW FULL PROCESSLIST`), competing for server resources — fixed with `KILL <process_id>` on each stuck process.
- **Redundant computation bug**: the original query recalculated the same `AVG(TransactionAmt) OVER(...)` window function four times inside one `CASE` block, causing it to hang at full scale. Fixed by splitting into two CTEs — compute the average once, reuse it via simple division.
- **Code duplication**: the SQL logic existed both in `feature_engineering.sql` and hardcoded inside the Python loading script. Resolved by having the Python script read the `.sql` file directly, making it the single source of truth.

### Phase 5 — Modeling
- **`ValueError: DataFrame.dtypes for data must be int, float, bool or category`**: XGBoost rejected raw text/categorical columns. Solved by one-hot encoding.
- **410-column explosion** from naive one-hot encoding of high-cardinality columns (`addr1`: 329 unique values, `P_emaildomain`: 60). Solved by grouping rare categories (below a frequency threshold, fit on training data only) into an `"Other"` bucket before encoding — reduced to 149 columns.
- **`CalibratedClassifierCV`'s `cv="prefit"` deprecated** in the installed scikit-learn version — threw `InvalidParameterError`. Fixed by switching to `cv=5`, letting the calibrator train and calibrate internally via cross-validation instead of reusing already-seen training data.
- **Calibration accidentally fit on already-trained-on data** in an early attempt — recognized as a subtle leakage-into-calibration risk and corrected before trusting any calibration results.
- **Reused an old decision threshold on a new model** after adding new features — caused a nonsensical classification report (89% recall, 4% precision) because the new model's calibrated probability distribution had shifted. Diagnosed by regenerating the precision-recall curve fresh for each new model version, rather than assuming a threshold transfers.
- **Two engineered features (`time_since_last_txn`, `transaction_hour`) tested and found to hurt performance** (PR-AUC dropped from 0.1907 to 0.1533–0.1809) — reverted rather than kept, with the negative result documented honestly.
- **SMOTE and hyperparameter tuning both tested and found not to outperform simpler baselines** — both documented as legitimate, evidence-based rejections rather than omitted from the record.

### Phase 6 — Explainability
- **SHAP's `TreeExplainer` cannot be applied directly to a `CalibratedClassifierCV`-wrapped model** — solved by extracting the 5 internal base XGBoost estimators and averaging their SHAP values.
- **Missing preprocessing when regenerating features for SHAP**: an early attempt skipped imputation and rare-category grouping entirely when rebuilding the SHAP input data from raw CSVs, which would have silently produced wrong explanations. Caught and fixed by re-applying Phase 5's exact preprocessing steps (fit on training data) before running SHAP.
- **Rare-category grouping accidentally recalculated from test data** in one draft, rather than reusing training-derived category thresholds — corrected to preserve the leakage-prevention principle used everywhere else in the project.

**Common thread across all of these:** nearly every problem was caught through active verification — checking row counts, re-running with a fresh kernel, comparing outputs against expected values — rather than assuming code worked because it didn't throw an error. That verification discipline, established in Phase 1, is what made catching these issues possible throughout the rest of the project.

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