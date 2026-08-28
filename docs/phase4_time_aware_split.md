# Phase 4 Log — Time-Aware Train/Validation/Test Split (Corrected)

**Original date:** 2026-08-05

**Correction date:** 2026-08-16

**Purpose:** Split the engineered feature dataset into training, validation, and test sets using strict chronological cutoffs, avoiding data leakage — and, following a mid-project methodological review, correcting an original 2-way split into a proper 3-way split.

## Why This Phase Was Revisited

The original Phase 4 produced a standard 80% train / 20% test split. During Phase 5 development, it was identified that this 20% test set was being repeatedly consulted to guide modeling decisions (imbalance handling comparisons, hyperparameter tuning, threshold selection) — a genuine methodological flaw, since a test set consulted more than once for decisions is no longer a fair, unbiased estimate of real-world performance. See [`docs/phase5_modeling_and_calibration.md`](phase5_modeling_and_calibration.md) for the full discovery and correction story.

## Method (Corrected)

1. Loaded `data/processed/engineered_features.csv` — now including all 79 columns (14 core + 65 Vesta V-columns; see V-column selection story in the Phase 5 doc).
2. Sorted all transactions by `TransactionDT`.
3. **First cut (80/20):** split into an 80% "development" portion and a 20% test portion.
4. **Second cut (80/20 of the development portion):** split the development portion further into 80% final training and 20% validation.
5. Verified zero overlap at **both** boundaries: train-max < validation-min, and validation-max < test-min.
6. Saved three files: `train_final_v2.csv` (~64% of total), `val_set_v2.csv` (~16% of total), `test_set_v2.csv` (~20% of total, held out and touched only once in Phase 5's final evaluation).

## Results

| Set | Approx. Rows | Approx. % of Total | Role |
|---|---|---|---|
| Train | ~377,947 | 64% | Model fitting only |
| Validation | ~94,486 | 16% | All development decisions (imbalance handling, tuning, threshold selection) |
| Test | ~118,107 | 20% | One-time, final evaluation only |

**Leakage verification:** confirmed strictly increasing, non-overlapping `TransactionDT` ranges across all three sets, checked directly from the data at both boundaries.

## Conclusion

Phase 4 (corrected) produces three chronologically ordered, non-overlapping datasets. This structural fix is what enables Phase 5's corrected methodology — every development decision made on validation, with the test set reserved exclusively for a single, final, honest performance evaluation.