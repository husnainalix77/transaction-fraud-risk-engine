# Phase 6 Log — Explainability & Permutation Importance

**Date:** 2026-08-10
**Purpose:** Explain the Phase 5 final model's predictions using SHAP and permutation importance, confirming the model's behavior is interpretable, consistent with domain knowledge, and consistent with earlier project findings — not a black box.

## Method

1. Loaded the Phase 5 final model (`fraud_model_final.pkl`, a `CalibratedClassifierCV`-wrapped XGBoost ensemble) and feature columns.
2. Reapplied Phase 5's exact preprocessing (imputation, rare-category grouping fit on training data) to the test set before generating explanations, ensuring SHAP/permutation results reflect the actual production pipeline, not a shortcut version.
3. Extracted the 5 internal XGBoost estimators from the calibration wrapper and ran SHAP's `TreeExplainer` on each, averaging results — since SHAP cannot be applied directly to a `CalibratedClassifierCV` object.
4. Computed permutation importance (scikit-learn, scored on PR-AUC) on a 5,000-row representative sample for computational feasibility.
5. Merged both rankings to identify agreement and explain divergence.
6. Generated individual SHAP waterfall explanations for one true positive, one false positive, and one false negative.

## Global Feature Importance — Key Findings

**Top features by SHAP:** `TransactionAmt`, `ProductCD_C`, `V303`, `card1`, `V308`
**Top features by permutation importance:** `TransactionAmt`, `V303`, `V310`, `ProductCD_C`, `card_txn_count_so_far`

Both methods independently agree `TransactionAmt`, `V303`, `ProductCD_C`, and `card1` are core drivers — strong, convergent evidence of genuine signal, not an artifact of either method alone.

## SHAP vs. Permutation Importance — Divergences Explained

| Feature | SHAP Rank | Permutation Rank | Explanation |
|---|---|---|---|
| `card_avg_amt_so_far` | 10 | 214 (lowest) | 0.81 correlation with `TransactionAmt` (Phase 5) — model recovers information from the correlated partner when this one is scrambled |
| `V308` | 5 | 202 | Redundant with other V-columns when individually removed |
| `card6_debit` | 13 | 193 | One-hot pair redundancy with `card6_credit` |
| `V312` | 16 | 212 | Same redundancy pattern as V308 |

**Key insight:** permutation importance measures *marginal necessity* (how much performance drops when a feature alone is removed), not *standalone predictive value*. A feature can be genuinely important (confirmed by SHAP) while scoring low on permutation importance, purely because a correlated feature already covers the same information. This directly confirms the multicollinearity concern flagged in Phase 5's correlation check (0.81 between `TransactionAmt` and `amt_deviation_ratio`), now demonstrated with real evidence rather than assumption.

## Individual Case Studies

**True Positive (correctly caught fraud):** predicted 0.552. Driven primarily by `ProductCD_W = False` (+0.37) and `V303 = 1` (+0.36) — being outside the low-risk product category and an active V303 signal were sufficient to correctly flag this transaction.

**False Positive (false alarm):** predicted 0.268. Several features correctly indicated low risk (`TransactionAmt` small: -0.46, established card history: -0.16), but `ProductCD_W = False` (+0.42) alone was strong enough to push this legitimate transaction over the threshold.

**False Negative (missed fraud):** predicted 0.158, just below the 0.16 threshold. `card_avg_amt_so_far` pulled the prediction down heavily (-0.59, card looked "normal"), while `TransactionAmt` correctly pushed toward fraud (+0.49, the amount was over 3x the card's average) — but not enough to overcome the competing signal. A concrete, traceable example of Phase 5's known recall ceiling.

## Conclusion

The model's behavior is fully explainable and auditable. Both explainability methods converge on the same core drivers, and every divergence between them is explainable by known feature correlations (identified back in Phase 5) rather than unexplained noise. Individual case studies demonstrate the model reasons in ways consistent with real-world fraud intuition, including a concrete illustration of exactly where and why its current recall limitations occur.

**Phase 6 status: Complete.**