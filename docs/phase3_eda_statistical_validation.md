# Phase 3 Log — Statistical Validation & Exploratory Data Analysis

**Date:** 2026-08-06
**Purpose:** Determine which raw and Phase 2 engineered features carry genuine, statistically defensible signal for fraud detection, before using them in modeling (Phase 5).

## Method
Every candidate feature was examined in two stages:
1. **Visual EDA** — bar charts for categorical features, density-normalized histograms and box plots for numeric features, comparing fraud vs. non-fraud.
2. **Formal statistical testing** — chi-square test of independence for categorical features, Kolmogorov-Smirnov (KS) test for numeric feature distributions — to confirm visual patterns weren't due to chance or small sample sizes.

All work performed in [`notebooks/03_eda_statistical_validation.ipynb`](../notebooks/03_eda_statistical_validation.ipynb).

## Categorical Features — Chi-Square Test Results

| Feature | Fraud Rate Range | Chi-Square Statistic | p-value | Result |
|---|---|---|---|---|
| ProductCD | 2.0% – 11.7% | 16,742.17 | ~0.0000 | ✅ Significant |
| card4 (network) | 2.9% – 7.7% | 364.87 | ~8.97e-79 | ✅ Significant |
| card6 (type) | 2.5% – 6.7% | 5,957.03 | ~0.0000 | ✅ Significant |
| has_identity_data | 2.1% – 7.8% | 10,683.64 | ~0.0000 | ✅ Significant |

## Numeric Features — Kolmogorov-Smirnov Test Results

| Feature | KS Statistic (D) | p-value | Result |
|---|---|---|---|
| TransactionAmt | 0.0756 | ~1.09e-99 | ✅ Significant |
| amt_deviation_ratio | 0.0986 | ~3.22e-166 | ✅ Significant |
| card_txn_count_so_far | 0.0587 | ~3.72e-60 | ✅ Significant |

## Key Findings

1. **All 7 features tested passed statistical significance testing** — every p-value fell far below the 0.05 threshold.
2. **`amt_deviation_ratio` (Phase 2 engineered feature) was the strongest individual predictor found in this phase**, outperforming raw `TransactionAmt` on both visual separation and KS statistic — direct evidence that the Phase 2 feature engineering effort added real value, not just complexity.
3. **`has_identity_data` produced the most striking finding**: transactions with identity data show a fraud rate over 3.7x higher than those without (~7.8% vs. ~2.1%) — a genuinely useful, counter-intuitive signal.
4. **Volume checks corrected two potentially misleading visual findings:**
   - `ProductCD = W` has a low fraud rate (~2.0%) but represents ~75% of all transactions — meaning it likely still contributes substantial absolute fraud volume.
   - Two `card6` categories (`"debit or credit"`, `"charge card"`) showed 0% fraud rate, but this was due to near-zero transaction counts, not a genuine safe pattern — excluded from meaningful interpretation.
5. **Missing values in `amt_deviation_ratio` and `card_avg_amt_so_far`** (13,553 rows each, corresponding to each card's first transaction) were excluded from the KS-test via `.dropna()`, since the feature is undefined — not missing by error — for rows with no prior card history. This exclusion affects ~2.3% of the dataset and does not materially change the test's conclusions.

## Features Carried Forward to Phase 4/5
All 7 tested features, with statistical justification: `ProductCD`, `card4`, `card6`, `has_identity_data`, `TransactionAmt`, `amt_deviation_ratio`, `card_txn_count_so_far`.

## Conclusion
Phase 3 is complete. Every feature entering the modeling phase is backed by both visual and statistical evidence, not assumption. Missing value imputation was deliberately deferred to after Phase 4's time-aware split, to avoid leaking validation-period statistics into training data.