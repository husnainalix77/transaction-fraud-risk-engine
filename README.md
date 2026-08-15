<div align="center">

# 🕵️ Transaction Fraud Risk Engine

### An end-to-end fraud detection system — SQL feature engineering, statistical validation, imbalance-aware modeling, calibration, explainability & an interactive dashboard

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-Modeling-blue?style=for-the-badge)](https://xgboost.readthedocs.io)
[![SciPy](https://img.shields.io/badge/SciPy-Statistical%20Testing-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org)
[![SHAP](https://img.shields.io/badge/SHAP-Explainability-purple?style=for-the-badge)](https://shap.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)]()

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
│  MySQL (chunked ingestion) │
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│  SQL Feature Engineering    │  ← + 65 Vesta V-columns
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Statistical Validation (EDA)│
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Time-Aware Train/Val Split  │
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
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│  Interactive Dashboard       │  ← Streamlit, 4 tabs, live threshold
│  (Streamlit)                 │    control, per-transaction SHAP
└───────────────────────────┘
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
| Dashboard | Streamlit | Interactive, deployed fraud risk explorer |
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
| 7 | Streamlit Dashboard & Final Docs | ✅ Complete |

**🎉 Project complete — all 7 phases finished.**

---

## 🗄️ Phase 1 — MySQL Ingestion & Verification

Chunked loading pipeline, fully verified. **Key finding:** ~75% of transactions have no matching identity record — carried forward as a deliberate feature (`has_identity_data`).

Log: [`docs/phase1_verification.md`](docs/phase1_verification.md)

---

## 🔍 Phase 2 — SQL Feature Engineering

Built in SQL using CTEs and window functions, later expanded with 65 low-missingness Vesta V-columns.

Logic: [`sql/feature_engineering.sql`](sql/feature_engineering.sql) · Log: [`docs/phase2_feature_engineering.md`](docs/phase2_feature_engineering.md)

---

## 📊 Phase 3 — Statistical Validation (EDA)

All 7 core features tested visually and statistically (chi-square, KS-test). All passed significance testing.

Notebook: [`notebooks/03_eda_statistical_validation.ipynb`](notebooks/03_eda_statistical_validation.ipynb) · Log: [`docs/phase3_eda_statistical_validation.md`](docs/phase3_eda_statistical_validation.md)

---

## ⏳ Phase 4 — Time-Aware Train/Validation Split

Split by `TransactionDT`. Zero overlap verified (train max 12,192,900 < test min 12,192,911).

Log: [`docs/phase4_time_aware_split.md`](docs/phase4_time_aware_split.md)

---

## 🎯 Phase 5 — Imbalance-Aware Modeling & Calibration

| Approach | PR-AUC | Decision |
|---|---|---|
| `scale_pos_weight` | 0.1907 | ✅ Adopted over SMOTE |
| SMOTE | 0.1837 | ❌ Rejected |
| Hyperparameter tuning | 0.1903 | ❌ Rejected — negligible gain |
| Engineered time/hour features | 0.1533–0.1809 | ❌ Rejected — hurt performance |
| +65 Vesta V-columns | **0.2857** | ✅ **Final model** |

**Final model:** XGBoost + `scale_pos_weight` + Platt calibration, 214 features, threshold = 0.16 → Precision 0.30, Recall 0.37, PR-AUC 0.2857.

Notebook: [`notebooks/05_modeling_and_calibration.ipynb`](notebooks/05_modeling_and_calibration.ipynb) · Log: [`docs/phase5_modeling_and_calibration.md`](docs/phase5_modeling_and_calibration.md)

---

## 🔬 Phase 6 — Explainability & Permutation Importance

SHAP and permutation importance independently confirm `TransactionAmt`, `V303`, `ProductCD_C`, `card1` as core drivers. Divergences (e.g., `card_avg_amt_so_far`) explained by Phase 5's known 0.81 feature correlation.

Notebook: [`notebooks/06_explainability.ipynb`](notebooks/06_explainability.ipynb) · Log: [`docs/phase6_explainability.md`](docs/phase6_explainability.md)

---

## 🖥️ Phase 7 — Interactive Streamlit Dashboard

A fully interactive, explainable deployment of the final model.

### 4 Tabs

| Tab | Description |
|---|---|
| 📊 Model Overview | Live-reactive precision/recall/F1/confusion matrix (updates with threshold slider) + full experimentation log |
| 🔍 Fraud Risk Predictor | Pick any transaction, get a live prediction + individual SHAP waterfall explanation |
| 📈 Explainability | Global SHAP summary + permutation importance, with divergence explained |
| 🧠 Project Journey | Phase-by-phase story, honest limitations, links |

### Key Features
- **Live decision threshold slider** — reactive across the entire app, not just one static chart
- **Custom-designed logo and dark navy/red theme**, matching the project's fraud-risk branding
- **Reuses the exact Phase 5/6 preprocessing pipeline** — dashboard predictions are guaranteed consistent with notebook-evaluated results, not a simplified approximation

Code: [`app/app.py`](app/app.py) · Log: [`docs/phase7_dashboard.md`](docs/phase7_dashboard.md)

### Run Locally
```bash
streamlit run app/app.py
```

---

## 📁 Repository Structure

```
transaction-fraud-risk-engine/
│
├── app/
│   ├── app.py                      # Streamlit dashboard
│   └── assets/
│       └── logo.png                # Custom-designed project logo
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
│   ├── phase6_explainability.md
│   └── phase7_dashboard.md
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔧 Problems Faced & How They Were Solved

*(See full details across all phases — kept as a transparent record since working through genuine problems is where most of the actual learning happened.)*

**Phases 1–2:** MySQL connection/typo issues, `SQLAlchemy` `text()` requirement, query timeouts traced to missing indexes and orphaned background queries (`SHOW FULL PROCESSLIST`), redundant window-function computation causing hangs, SQL/Python code duplication resolved.

**Phase 5:** Categorical encoding errors, 410-column explosion from high-cardinality one-hot encoding (fixed via rare-category grouping), `CalibratedClassifierCV`'s `cv="prefit"` deprecation, a stale-threshold bug after adding new features (diagnosed by regenerating the PR curve fresh per model version), and two rejected experiments (SMOTE, engineered time/hour features) documented honestly.

**Phase 6:** SHAP incompatibility with `CalibratedClassifierCV` wrappers (resolved by extracting internal estimators), missing preprocessing when regenerating SHAP input data (caught and fixed), rare-category grouping accidentally computed from test instead of training data (corrected).

**Phase 7:** Relative path errors between notebook and Streamlit execution contexts, `plt.show()` not rendering in Streamlit (fixed with `st.pyplot()`), dead sidebar code (variable assignment instead of `st.metric()` calls), variable shadowing risk.

---

## 🧠 Key Engineering Decisions

**Why SQL feature engineering over pandas-only?** Reflects production feature pipelines built against a live database.

**Why time-based validation, not random?** Prevents the model from implicitly accessing future information during training.

**Why PR-AUC over accuracy?** Proven directly — a trained model scored *below* a naive baseline on accuracy alone.

**Why calibrate before choosing a threshold?** `scale_pos_weight` distorts raw probabilities; calibration ensures the threshold decision rests on trustworthy numbers.

**Why test and reject SMOTE, tuning, and new features?** Each was a reasonable hypothesis, tested and judged on evidence — reporting negative results honestly demonstrates real experimentation.

**Why expand to V-columns, and why stop at 65?** Evidence pointed to a feature-scope limitation; diminishing returns and rising missingness justified stopping, balanced against real project time constraints.

**Why use two explainability methods?** SHAP and permutation importance measure fundamentally different things — using both, and explaining disagreements, produces a more defensible understanding than either alone.

**Why build an interactive dashboard rather than just notebooks?** Makes the project's results tangible and explorable for a non-technical reviewer — a live threshold slider and per-transaction explanations demonstrate genuine understanding of the precision/recall tradeoff, not just a static report.

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

⭐ **Star this repo if it helped you understand real-world fraud detection workflows** ⭐

*This is an independent learning/portfolio project — not affiliated with Kaggle, IEEE-CIS, or Vesta Corporation.*

</div>