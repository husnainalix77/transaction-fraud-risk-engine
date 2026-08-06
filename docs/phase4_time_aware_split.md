# Phase 4 Log — Time-Aware Train/Validation Split

**Date:** 2026-08-05
**Purpose:** Split the Phase 2 engineered feature dataset into training and validation sets using a strict chronological cutoff, avoiding the data leakage a random split would introduce given this dataset's time-ordered structure and rolling window-function features.

## Method
1. Loaded `data/processed/engineered_features.csv` (590,540 rows, 14 columns).
2. Sorted all transactions by `TransactionDT` (a time-delta field, in seconds from an undisclosed reference point) to establish true chronological order.
3. Calculated an 80% split index and used the `TransactionDT` value at that position as a threshold.
4. Split the dataset using that threshold: `train_df` = all transactions with `TransactionDT <= threshold`, `test_df` = all transactions with `TransactionDT > threshold`.
5. Verified zero time overlap by comparing `train_df`'s maximum `TransactionDT` against `test_df`'s minimum.
6. Saved both sets to `data/processed/train_set.csv` and `data/processed/test_set.csv`.

## Results

| Set | Rows | % of Total | TransactionDT Range |
|---|---|---|---|
| Train | 472,433 | 80.0% | 86,400 – 12,192,900 |
| Test | 118,107 | 20.0% | 12,192,911 – 15,811,131 |

**Leakage verification:**

Train max TransactionDT: 12,192,900
Test min TransactionDT: 12,192,911

An 11-second gap separates the two sets with zero overlap — confirming no transaction in the validation set could have influenced or been influenced by any transaction in the training set.

## Notes
- The 1-row deviation from an exact 80.000% split (472,433 vs. theoretical 472,432) occurred because multiple transactions shared the exact threshold `TransactionDT` value; all were retained in the training set via a `<=` comparison. This is the safer direction — it never allows a boundary-sharing row to leak into validation — and has no meaningful effect on split integrity.
- Missing value imputation was deliberately deferred to Phase 5, to be fit only on the training set and then applied to both sets — avoiding leakage of validation-period statistics into imputed values.
- `X`/`y` feature-target separation was also deferred to Phase 5, keeping this phase scoped strictly to the split itself.

## Conclusion
Phase 4 is complete. The train/validation split is verified leakage-free and saved to disk, ready for Phase 5's imbalance-aware modeling.
