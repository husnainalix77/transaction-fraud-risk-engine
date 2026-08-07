# Phase 5 Progress Log — Imbalance-Aware Modeling & Calibration (In Progress)

**Date started:** 2026-08-06
**Status:** In progress — paused after imbalance handling comparison, before calibration

## Completed So Far

### 5.1–5.2 Missing Value Audit & Imputation
- Audited missing values separately in train/test sets.
- Imputed `card4`, `card6`, `addr1`, `P_emaildomain` with an explicit `"Missing"` category.
- Imputed `card_avg_amt_so_far`, `amt_deviation_ratio` with `-1` (a deliberately impossible value, preserving "no prior card history" as a distinct, learnable signal rather than disguising it as an average).
- Both are fixed constants, applied identically to train and test — no leakage risk.

### 5.3 Multicollinearity Check
- Pearson correlation among numeric features calculated on training data only.
- `TransactionAmt` and `amt_deviation_ratio` correlated at 0.81 (expected, since the latter is derived from the former). Both retained — XGBoost is robust to multicollinearity; revisit if Phase 6 permutation importance shows true redundancy.

### 5.4 X/y Separation
- Dropped `isFraud` (target), `TransactionID`, `TransactionDT` from features.
- `X_train`: (472,433, 11), `X_test`: (118,107, 11).

### 5.5–5.6 Encoding
- One-hot encoding on raw categoricals produced an unwieldy 410 columns, driven by `addr1` (329 unique values) and `P_emaildomain` (60 unique values).
- Rare categories grouped into `"Other"` (threshold fit on training data only): `addr1` 329→69, `P_emaildomain` 60→59.
- Re-encoded: final feature set = **149 columns**, aligned identically between train/test.

### 5.7 Baseline Model
- Default XGBoost, no imbalance correction.
- **Accuracy: 0.9648** vs. **naive "always predict not-fraud": 0.9656** — the trained model scored *lower* than doing nothing, direct proof accuracy is the wrong metric for this problem.

### 5.8–5.9 Imbalance Handling — scale_pos_weight
- `scale_pos_weight = 27.46` (ratio of non-fraud to fraud in training data).
- Precision (fraud): 0.12, Recall (fraud): 0.62, F1: 0.20.
- **PR-AUC: 0.1907**

### 5.10–5.11 Imbalance Handling — SMOTE
- Training set resampled from 472,433 → 911,666 rows (synthetic fraud examples added; test set untouched).
- **PR-AUC: 0.1837** — slightly *worse* than `scale_pos_weight`.
- **Decision: `scale_pos_weight` chosen as the primary imbalance-handling approach**, based on empirical PR-AUC comparison, not assumption. SMOTE is documented as a properly tested alternative, not a rejected shortcut.

## Remaining Work
- Calibration check (reliability diagram) on the `scale_pos_weight` model's probability outputs.
- Apply calibration correction if needed (Platt scaling / isotonic regression).
- Precision-recall curve and deliberate threshold selection, with written justification.
- Hyperparameter tuning (GridSearchCV or manual sweep).
- Final model artifact + metrics summary.

## Conclusion (interim)
Core imbalance-handling comparison is complete and evidence-based: `scale_pos_weight` outperforms SMOTE on this dataset by PR-AUC. Calibration and threshold selection remain before Phase 5 can be considered closed.