# Phase 6 Log — Explainability & Permutation Importance (Updated for Corrected Model)

**Original date:** 2026-08-10

**Updated date:** 2026-08-17 (reflects the Phase 4/5 methodology correction)

**Purpose:** Explain the corrected Phase 5 final model's predictions using SHAP and permutation importance, confirming the model's behavior is interpretable and consistent with prior project findings.

## What Changed From the Original Version

This phase's methodology is unchanged — SHAP and permutation importance are explanatory tools, not decision-making steps, so they carry no test-set leakage risk regardless of which model is explained. However, the **underlying model changed** following Phase 5's correction:

| | Original | Corrected |
|---|---|---|
| Features | 214 | 212 |
| Threshold | 0.16 | 0.15 |
| TransactionAmt/amt_deviation_ratio correlation | 0.81 | 0.79 |
| Reference PR-AUC | 0.2857 (flawed) | 0.2565 (honest, test-set) |

All SHAP and permutation importance computations were rerun against the corrected model and corrected `test_set_v2.csv`, with category-grouping thresholds reused from the corrected `train_final_v2.csv`.

## Method

1. Loaded the corrected final model artifacts.
2. Reapplied Phase 5's exact preprocessing to the test set (imputation, rare-category grouping fit on `train_final_v2.csv`, encoding).
3. Extracted the 5 internal XGBoost estimators from the `CalibratedClassifierCV` wrapper for SHAP's `TreeExplainer`.
4. Computed global SHAP summary (2,000–5,000 row sample), 3 individual case studies (true positive, false positive, false negative), and permutation importance (scikit-learn, PR-AUC scoring).
5. Compared SHAP and permutation rankings directly.

## Key Findings

1. `TransactionAmt`, `V303`, `ProductCD_C`, and `card1` remain the model's core drivers, confirmed independently by both methods — consistent with the original analysis.
2. The Phase 5 V-column expansion is validated again: multiple V-columns (`V303`, `V310`, `V294`, `V302`, others) rank highly by both explainability methods.
3. `card_avg_amt_so_far`'s large SHAP-vs-permutation rank gap is explained by its 0.79 correlation with `TransactionAmt` (updated from the original 0.81, matching the corrected multicollinearity check) — permutation importance measures marginal necessity, not standalone value.
4. Individual case studies re-run against the corrected model (threshold 0.15) show the same qualitative pattern as before: explainable, traceable reasoning per prediction, including borderline missed-fraud cases illustrating the model's honest recall ceiling.

## Conclusion
The corrected model's behavior remains fully explainable and consistent with domain intuition and prior project findings. Updating this phase for the corrected model required no methodological changes — only rerunning against updated artifacts — confirming that Phase 6's explainability approach was itself sound and unaffected by the Phase 5 correction.

**Phase 6 status: Complete (updated for corrected model).**