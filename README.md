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

Card-not-present and online payment fraud costs the payments industry **billions annually**. This project builds a fraud detection pipeline designed to handle the problem properly:

- 🎯 Fraud is rare (**~3.5%** of transactions) — accuracy alone is a meaningless metric here
- ⏳ Fraud patterns shift over time — validation must respect chronological order
- 🔍 A production fraud model needs to be explainable, not a black box
- 📊 Every decision is backed by tested evidence — including a genuine methodological correction discovered and fixed mid-project, documented transparently below

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
│ Time-Aware Train/Val/Test    │  ← 3-way split (corrected)
│         Split                 │
└─────────────┬───────────────┘
              │
              ▼
┌───────────────────────────┐
│ Imbalance-Aware Modeling &   │  ← Val PR-AUC: 0.3406
│      Calibration             │    TEST PR-AUC: 0.2565
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
└───────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data storage | MySQL + SQLAlchemy | Structured storage, chunked ingestion |
| Feature engineering | SQL (CTEs, window functions) | Behavioral aggregates + 65 V-columns |
| Processing | Pandas + NumPy | Chunked reading, downcasting, imputation |
| Statistical testing | SciPy (chi2_contingency, ks_2samp) | Formal significance testing |
| Modeling | XGBoost, scikit-learn | Imbalance-aware classification |
| Calibration | CalibratedClassifierCV (Platt scaling) | Trustworthy probability outputs |
| Explainability | SHAP, permutation_importance | Model interpretability |
| Dashboard | Streamlit | Interactive, deployed fraud risk explorer |
| Visualization | Matplotlib + Seaborn | EDA, PR curves, reliability diagrams |
| Environment | Python venv, Jupyter notebooks, `.env` | Reproducible workflow |

---

## ✅ Project Progress

| Phase | Description | Status |
|---|---|---|
| 1 | MySQL Ingestion & Verification | ✅ Complete |
| 2 | SQL Feature Engineering | ✅ Complete |
| 3 | Statistical Validation (EDA) | ✅ Complete |
| 4 | Time-Aware Train/Validation/Test Split | ✅ Complete (corrected) |
| 5 | Imbalance-Aware Modeling & Calibration | ✅ Complete (corrected) |
| 6 | Explainability & Permutation Importance | ✅ Complete |
| 7 | Streamlit Dashboard & Final Docs | ✅ Complete |

**🎉 Project complete — all 7 phases finished, including a genuine mid-project methodological correction.**

---

## ⚠️ A Note on Methodology: What Changed and Why

Partway through this project, after completing all 7 phases once, a real methodological flaw was identified: **the test set had been used repeatedly throughout Phase 5's development** — every comparison (scale_pos_weight vs. SMOTE, hyperparameter tuning, threshold selection, feature-set changes) was evaluated directly against the test set, with each result informing the next decision. This is a well-known form of leakage — not of data rows, but of *information about the test set's answers* — that produces optimistically biased final results.

**The fix:** the original 80/20 time-aware split was extended into a proper 3-way split — **64% train / 16% validation / 20% test** — all chronologically ordered with zero overlap. Every development decision (imbalance handling, calibration, tuning, threshold) was redone using only the validation set. The test set was touched **exactly once**, at the very end, for a single, final, honest evaluation.

**The result of this correction, reported transparently:**

| Metric | Original (flawed) | Corrected — Validation | Corrected — Test (final, honest) |
|---|---|---|---|
| PR-AUC | 0.2857 | 0.3406 | **0.2565** |

The gap between the corrected validation PR-AUC (0.3406) and the corrected test PR-AUC (0.2565) is expected and informative — it's the honest, measured evidence of how much the original, flawed process had been implicitly overfitting to test-set feedback. **0.2565 is the number that should be trusted as this model's real-world performance estimate.**

---

## 🗄️ Phase 1 — MySQL Ingestion & Verification

Chunked loading pipeline, fully verified. **Key finding:** ~75% of transactions have no matching identity record — carried forward as a deliberate feature (`has_identity_data`).

Log: [`docs/phase1_verification.md`](docs/phase1_verification.md)

---

## 🔍 Phase 2 — SQL Feature Engineering

Built in SQL using CTEs and window functions, expanded with 65 low-missingness Vesta V-columns from the start.

Logic: [`sql/feature_engineering.sql`](sql/feature_engineering.sql) · Log: [`docs/phase2_feature_engineering.md`](docs/phase2_feature_engineering.md)

---

## 📊 Phase 3 — Statistical Validation (EDA)

All 7 core features tested visually and statistically (chi-square, KS-test). All passed significance testing.

Notebook: [`notebooks/03_eda_statistical_validation.ipynb`](notebooks/03_eda_statistical_validation.ipynb) · Log: [`docs/phase3_eda_statistical_validation.md`](docs/phase3_eda_statistical_validation.md)

---

## ⏳ Phase 4 — Time-Aware Train/Validation/Test Split (Corrected)

Split chronologically into three non-overlapping sets, correcting the original 2-way split that allowed test-set leakage during development.

| Set | Approx. % | Purpose |
|---|---|---|
| Train | 64% | Model fitting only |
| Validation | 16% | All development decisions |
| Test | 20% | One-time, final evaluation only |

Zero overlap verified at both boundaries directly from the data.

Log: [`docs/phase4_time_aware_split.md`](docs/phase4_time_aware_split.md)

---

## 🎯 Phase 5 — Imbalance-Aware Modeling & Calibration (Corrected)

Every technique tested empirically on the **validation set**, judged on PR-AUC. A default XGBoost model scored *lower* accuracy than a naive baseline, proving accuracy is the wrong metric here.

| Approach | Validation PR-AUC | Decision |
|---|---|---|
| `scale_pos_weight` | 0.3406 | ✅ Adopted over SMOTE |
| SMOTE | 0.2900 | ❌ Rejected — worse |
| Hyperparameter tuning | 0.3457 | ❌ Rejected — negligible gain (~1.5%) |

**Final model:** XGBoost + `scale_pos_weight` (27.31) + Platt calibration, 212 features, threshold = 0.15

| Metric | Validation | **Test (final, one-time)** |
|---|---|---|
| PR-AUC | 0.3406 | **0.2565** |
| Precision | 0.31 | 0.30 |
| Recall | 0.43 | 0.30 |
| F1-score | 0.36 | 0.30 |

Notebook: [`notebooks/05_modeling_and_calibration.ipynb`](notebooks/05_modeling_and_calibration.ipynb) · Log: [`docs/phase5_modeling_and_calibration.md`](docs/phase5_modeling_and_calibration.md)

---

## 🔬 Phase 6 — Explainability & Permutation Importance

SHAP and permutation importance independently confirm `TransactionAmt`, `V303`, `ProductCD_C`, `card1` as core drivers. Divergences (e.g., `card_avg_amt_so_far`) explained by a known 0.79 feature correlation.

Notebook: [`notebooks/06_explainability.ipynb`](notebooks/06_explainability.ipynb) · Log: [`docs/phase6_explainability.md`](docs/phase6_explainability.md)

---

## 🖥️ Phase 7 — Interactive Streamlit Dashboard

A fully interactive deployment of the final, corrected model, reflecting the honest test-set PR-AUC (0.2565), not the earlier flawed number.

### 4 Tabs

| Tab | Description |
|---|---|
| 📊 Model Overview | Live-reactive precision/recall/F1/confusion matrix + full validation-based experimentation log |
| 🔍 Fraud Risk Predictor | Pick any transaction, get a live prediction + individual SHAP waterfall explanation |
| 📈 Explainability | Global SHAP summary + permutation importance |
| 🧠 Project Journey | Phase-by-phase story, including the methodology correction, honest limitations |

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
│   ├── app.py
│   └── assets/
│       ├── logo.png
│       └── screenshots/
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── engineered_features.csv
│       ├── train_final_v2.csv      # corrected: 64% train
│       ├── val_set_v2.csv          # corrected: 16% validation
│       └── test_set_v2.csv         # corrected: 20% test (untouched)
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
│   ├── phase7_dashboard.md
│   └── AI_USAGE.md
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔧 Problems Faced & How They Were Solved

**Phases 1–2:** MySQL connection/typo issues, `SQLAlchemy` `text()` requirement, query timeouts traced to missing indexes and orphaned background queries, redundant window-function computation, SQL/Python code duplication resolved.

**Phase 5 (original attempt):** Categorical encoding errors, 410-column explosion (fixed via rare-category grouping), `CalibratedClassifierCV`'s `cv="prefit"` deprecation, a stale-threshold bug after feature changes, two rejected experiments (SMOTE, engineered time/hour features).

**Phase 5 (methodological correction):** **The most significant issue found in this project** — the test set was being used repeatedly to guide development decisions rather than held out for a single, final evaluation. Identified through careful self-review, corrected by extending the split into train/validation/test, redoing all of Phase 5's development against validation only, and reporting both the validation and honest, single-evaluation test numbers transparently.

**Phase 6:** SHAP incompatibility with `CalibratedClassifierCV` wrappers (resolved via internal estimator extraction), preprocessing consistency issues when reapplying Phase 5's pipeline to the test set.

**Phase 7:** Relative path handling between notebook and Streamlit execution contexts, `plt.show()` not rendering in Streamlit, dashboard updated to reflect the corrected model, data files, and final honest metrics.

---

## 🧠 Key Engineering Decisions

**Why SQL feature engineering over pandas-only?** Reflects production feature pipelines built against a live database.

**Why time-based validation, not random?** Prevents the model from implicitly accessing future information during training.

**Why PR-AUC over accuracy?** Proven directly — a trained model scored *below* a naive baseline on accuracy alone.

**Why calibrate before choosing a threshold?** `scale_pos_weight` distorts raw probabilities; calibration ensures the threshold decision rests on trustworthy numbers.

**Why a train/validation/test split instead of train/test?** Discovered mid-project that repeatedly evaluating development decisions against a single held-out set produces optimistically biased results. Separating validation (used for every decision) from test (touched once) gives an honest, defensible final performance estimate — and the gap between the two numbers is itself valuable, disclosed evidence of how much the earlier process had overfit to feedback.

**Why report the flawed original results at all, rather than just fixing and moving on?** Transparency about mistakes and corrections is more credible than a seamless narrative that hides them — this is real evidence of methodological rigor and self-critical engineering judgment, which matters more to a reviewer than a single clean number.

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

⭐ **Star this repo — including for the honest methodological correction documented above** ⭐

*This is an independent learning/portfolio project — not affiliated with Kaggle, IEEE-CIS, or Vesta Corporation.*

</div>