# Phase 5 Log — Imbalance-Aware Modeling & Calibration

**Date:** 2026-08-06 to 2026-08-09
**Purpose:** Build a fraud classifier trained on the Phase 4 time-aware split, correctly handling severe class imbalance (~3.5% fraud), with calibrated probability outputs and a deliberately justified decision threshold — evaluated using PR-AUC, precision, and recall rather than accuracy.

## Method Summary

1. **Missing value audit & imputation** (fit on training data only): categorical gaps (`card4`, `card6`, `addr1`, `P_emaildomain`) filled with an explicit `"Missing"` category; engineered numeric gaps (`card_avg_amt_so_far`, `amt_deviation_ratio`) filled with `-1`, preserving "no prior card history" as a distinct, learnable signal.
2. **Multicollinearity check:** `TransactionAmt`/`amt_deviation_ratio` correlated at 0.81 (expected, since one is derived from the other); both retained, flagged for review in Phase 6.
3. **X/y separation and one-hot encoding**, with rare-category grouping (`addr1` 329→69, `P_emaildomain` 60→59 unique values) to avoid an unwieldy 410-column feature space.
4. **Baseline model:** default XGBoost scored 0.9648 accuracy — *below* a naive "always predict not-fraud" baseline (0.9656) — direct proof accuracy is the wrong metric here.
5. **Imbalance handling comparison** (judged by PR-AUC): `scale_pos_weight` (0.1907) outperformed SMOTE (0.1837); `scale_pos_weight` adopted.
6. **Calibration:** `scale_pos_weight` produced severely over-confident probabilities (predicted ~0.91 corresponded to only ~0.60 actual fraud rate). Platt scaling (`CalibratedClassifierCV`, 5-fold internal CV) corrected this.
7. **Hyperparameter tuning:** GridSearchCV (36 combinations, 108 fits) found no meaningful improvement (0.1903 vs. 0.1907) — original settings kept.
8. **Feature engineering attempt (rejected):** `time_since_last_txn` and `transaction_hour` were added and tested; PR-AUC dropped (0.1809 uncalibrated, 0.1533 calibrated) — reverted.
9. **V-column expansion (adopted):** 25 low-missingness Vesta V-columns added first (PR-AUC → 0.2532 calibrated), then 40 more (65 total, PR-AUC → 0.2857 calibrated) — the only intervention that produced a substantial, sustained improvement.
10. **Final threshold selection:** 0.16, chosen just below the precision/recall crossing point (~0.17–0.18), deliberately favoring recall per the reasoning that missed fraud costs more than a false alarm in this domain.

## Full Experimentation Log

| Approach | PR-AUC | Decision |
|---|---|---|
| Baseline (default XGBoost) | Accuracy 0.9648 (< naive 0.9656) | Proved accuracy is misleading |
| `scale_pos_weight` | 0.1907 | ✅ Adopted over SMOTE |
| SMOTE | 0.1837 | ❌ Rejected — empirically worse |
| Hyperparameter tuning | 0.1903 | ❌ Rejected — negligible gain |
| Engineered time/hour features | 0.1533–0.1809 | ❌ Rejected — hurt performance |
| +25 V-columns | 0.2532 | ✅ Adopted — first real gain |
| +40 more V-columns (65 total) | **0.2857** | ✅ **Final model** |

## Final Model

**XGBoost + `scale_pos_weight` + Platt calibration, 214 features (65 V-columns + 11 original engineered/raw features), threshold = 0.16**

| Metric | Value |
|---|---|
| Precision (Fraud) | 0.30 |
| Recall (Fraud) | 0.37 |
| F1-score (Fraud) | 0.33 |
| PR-AUC | 0.2857 |
| Fraud caught | 1,504 / 4,063 |
| Fraud missed | 2,559 |
| False alarms | 3,578 |

**Overall improvement: 0.1907 → 0.2857 PR-AUC (~50% relative gain)**, achieved through evidence-based feature expansion, not model tuning or resampling.

## Why V-Column Expansion Stopped at 65

- Marginal gain per batch roughly halved between round 1 (+0.0625 PR-AUC from 25 columns) and round 2 (+0.0325 PR-AUC from 40 columns) — a measurable diminishing-returns trend.
- Remaining unused V-columns have meaningfully higher missingness, requiring more complex imputation with uncertain benefit.
- Balanced against real project time constraints (Phase 5 spanned 4+ days against an original ~3-week whole-project estimate), continuing further risked scope creep without proportionate value.

## Honest Limitations

- Recall of 37% means nearly two-thirds of fraud still goes undetected — a genuine ceiling given the current feature set and single-model approach.
- The threshold reflects a default cost assumption (missed fraud > false alarm), not an actual calculated business cost ratio.
- Matching industry-standard performance (70-90%+ recall with manageable false alarms) would require substantially more features, ensemble modeling, and continuously updated production data — outside this project's scope.

## Artifacts Saved
- `models/fraud_model_final.pkl` — calibrated final model
- `models/feature_columns_final.pkl` — exact feature column order/names
- `models/decision_threshold.pkl` — chosen threshold (0.16)

## Conclusion
Phase 5 is complete. The final model represents a genuine, evidence-driven improvement over every simpler alternative tested, with honest documentation of both successful and unsuccessful approaches. Proceeding to Phase 6 (Explainability & Permutation Importance).