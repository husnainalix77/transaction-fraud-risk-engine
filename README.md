# Transaction Fraud Risk Engine

End-to-end fraud detection pipeline built on real-world, imbalanced financial transaction data — combining SQL-based feature engineering, imbalance-aware machine learning, probability calibration, and model explainability to identify fraudulent transactions in a way that's both statistically rigorous and business-defensible.

![Status](https://img.shields.io/badge/status-in%20progress-yellow)
![Python](https://img.shields.io/badge/python-3.12-blue)
![MySQL](https://img.shields.io/badge/database-MySQL-orange)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Problem Statement

Card-not-present and online payment fraud costs the payments industry billions annually. A production fraud model has to solve a much harder problem than a typical classroom classifier:

- **Fraud is rare** (~3.5% of transactions in this dataset) — a model that predicts "not fraud" every time is already ~96% accurate and completely useless.
- **Errors are asymmetric** — missing a fraud case costs real money; flagging a legitimate customer costs trust. Accuracy alone can't capture this tradeoff.
- **Fraud patterns shift over time** — a model must be validated the way it will actually be used: trained on the past, tested on the future, never the reverse.
- **Decisions need to be explainable** — a black-box fraud score isn't enough for risk teams or regulators.

This project builds a fraud detection pipeline that addresses all four constraints directly, rather than optimizing for a misleading accuracy number.

---

## Dataset

- **Source:** [IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection/data) (Kaggle, in partnership with the IEEE Computational Intelligence Society and Vesta Corporation)
- **Files used:** `train_transaction.csv` (590,540 rows × 394 columns) and `train_identity.csv` (144,233 rows × 41 columns), joined on `TransactionID`
- **Target:** `isFraud` (binary)
- **Class balance:** ~3.5% fraud — genuinely imbalanced, not a toy split
- **Time structure:** transactions span roughly one year, enabling realistic time-based validation

**To reproduce:**
1. Create a free Kaggle account
2. Accept the competition rules at the link above
3. Download `train_transaction.csv` and `train_identity.csv`
4. Place both files in `data/raw/` (not committed to this repo — see `.gitignore`)

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data storage & engineering | MySQL, SQL (joins, CTEs, window functions) |
| Data manipulation | Python, Pandas, NumPy |
| Modeling | Scikit-learn, XGBoost, imbalanced-learn (SMOTE) |
| Model evaluation & calibration | Scikit-learn (CalibratedClassifierCV), precision-recall analysis |
| Explainability | SHAP, permutation importance |
| Visualization | Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Environment & workflow | Python venv, Git/GitHub, `.env`-based credential management |

---

## Architecture

```
train_transaction.csv ─┐
                        ├─► MySQL (raw_transactions, raw_identity)
train_identity.csv ────┘              │
                                       ▼
                        SQL feature engineering (joins, CTEs, window functions)
                                       │
                                       ▼
                    Time-aware train/validation split (no shuffling)
                                       │
                                       ▼
              XGBoost + class weighting/SMOTE + probability calibration
                                       │
                                       ▼
                  SHAP + permutation importance (explainability)
                                       │
                                       ▼
                      Streamlit dashboard (fraud risk scoring UI)
```

---

## Repository Structure

```
transaction-fraud-risk-engine/
├── data/
│   ├── raw/            # source CSVs (gitignored)
│   └── processed/      # engineered feature tables
├── sql/                 # feature engineering queries (CTEs, window functions)
├── notebooks/           # EDA and inspection notebooks/scripts
├── src/                 # reusable Python modules (ingestion, verification, modeling)
├── app/                 # Streamlit dashboard
├── docs/                # verification logs and written findings
├── requirements.txt
├── .env                 # local MySQL credentials (gitignored, not committed)
├── .gitignore
├── README.md
└── LICENSE
```

---

## Methodology

### 1. Data Ingestion & Verification (Complete)
Both CSVs were loaded into MySQL using a memory-safe, chunked pipeline (20,000 rows per chunk, with numeric type downcasting) rather than a single-pass load — necessary given the dataset's size relative to available memory. 

Every load was independently verified — not assumed — across four dimensions: row counts, column structure, null-value parity, and value-level spot-checks on randomly sampled rows. Full results are documented in [`docs/phase1_verification.md`](docs/phase1_verification.md); all checks passed with zero discrepancies.

A notable finding from this phase: ~75% of transactions have no matching identity record. Rather than treating this as missing data to discard, it's carried forward as a deliberate feature (`has_identity_data`) in the next phase.

### 2. SQL Feature Engineering *(in progress)*
Transaction and identity data are joined via `LEFT JOIN` on `TransactionID`. Behavioral features (e.g., rolling transaction counts per card, deviation from historical spend) are engineered directly in SQL using CTEs and window functions, rather than relying on pandas merges — reflecting how feature pipelines are built against production databases in practice.

### 3. Statistical Validation *(planned)*
Chi-square and Kolmogorov-Smirnov tests are used to confirm which features show a statistically significant relationship with fraud, rather than relying on visual inspection alone.

### 4. Time-Aware Validation *(planned)*
The dataset is split by `TransactionDT`, training on earlier transactions and validating on later, unseen-in-time transactions — avoiding the data leakage a random shuffle-split would introduce on time-ordered data.

### 5. Imbalance-Aware Modeling & Calibration *(planned)*
XGBoost is trained with class weighting and SMOTE, evaluated using precision, recall, F1, and PR-AUC (not accuracy, which is misleading under 3.5% class imbalance). Model probability outputs are checked for calibration (reliability diagrams, Platt/isotonic scaling) before any classification threshold is chosen — ensuring the final threshold decision rests on trustworthy probabilities.

### 6. Explainability & Feature Importance *(planned)*
SHAP provides per-prediction fraud driver explanations; permutation importance provides an independent, model-wide feature ranking. Both are compared to build a defensible, non-black-box account of what the model is actually doing.

### 7. Dashboard & Deployment *(planned)*
A Streamlit dashboard exposes fraud risk scoring with per-prediction explanations, alongside overall model performance metrics.

---

## Current Status

- [x] **Phase 1** — MySQL ingestion, fully verified
- [ ] **Phase 2** — SQL feature engineering
- [ ] **Phase 3** — Statistical validation (EDA)
- [ ] **Phase 4** — Time-aware train/validation split
- [ ] **Phase 5** — Imbalance-aware modeling & calibration
- [ ] **Phase 6** — Explainability & permutation importance
- [ ] **Phase 7** — Streamlit dashboard & final documentation

---

## Key Design Decisions

- **Why SQL feature engineering over pandas-only:** reflects how production feature pipelines are typically built against a live database, and forces genuine practice with joins, CTEs, and window functions at scale.
- **Why time-based validation, not random split:** this dataset is time-ordered; a random split would leak future transaction patterns into training, producing an inflated, untrustworthy validation score.
- **Why PR-AUC over accuracy/ROC-AUC as the primary metric:** with ~3.5% fraud prevalence, accuracy is trivially high and uninformative; PR-AUC better reflects performance on the minority class that actually matters here.
- **Why calibration before threshold selection:** imbalance-correction techniques like SMOTE and class weighting distort raw model probabilities — calibration ensures the final decision threshold is chosen against numbers that genuinely reflect real-world fraud likelihood.

---

## Author

**Husnain Maroof**
Mechatronics & Control Engineering, UET Lahore
[GitHub](https://github.com/husnainalix77)

---

## License
This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

*Note: this repository is an independent learning/portfolio project and is not affiliated with Kaggle, IEEE-CIS, or Vesta Corporation.*