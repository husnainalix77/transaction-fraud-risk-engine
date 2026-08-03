# Phase 2 Log — SQL Feature Engineering

**Date:** 2026-08-03
**Purpose:** Build engineered features from the verified raw MySQL tables (`raw_transactions`, `raw_identity`) entirely in SQL, then pull the result into pandas for use in Phase 3 onward.

## Method
All feature engineering was written as a single reproducible SQL script (`sql/feature_engineering.sql`), structured as a chain of CTEs:

1. **`joined_data`** — `LEFT JOIN` of `raw_transactions` and `raw_identity` on `TransactionID`, preserving all transactions regardless of identity match.
2. **`identity_flagged`** — adds `has_identity_data` (1/0), converting the join's NULL pattern into an explicit, model-usable feature.
3. **`card_behaviour`** — adds two rolling window-function features per card: `card_txn_count_so_far` and `card_avg_amt_so_far`, both partitioned by `card1`, ordered by `TransactionDT`, and restricted to `ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING` (only prior transactions, never current/future).
4. **`card_behaviour_final`** — adds `amt_deviation_ratio` (`TransactionAmt / card_avg_amt_so_far`), reusing the already-computed average rather than recalculating it.

The final result was pulled into pandas via `src/build_features.py` (which reads `feature_engineering.sql` directly — no duplicated query logic) and saved to `data/processed/engineered_features.csv`.

## Engineered Features

| Feature | Description |
|---|---|
| `has_identity_data` | 1 if the transaction has a matching identity record, 0 otherwise |
| `card_txn_count_so_far` | Count of this card's transactions prior to the current one |
| `card_avg_amt_so_far` | Average transaction amount for this card, prior to the current one |
| `amt_deviation_ratio` | `TransactionAmt ÷ card_avg_amt_so_far` — how unusual this transaction is relative to the card's own history |

## Verification

Rows: 590,540 | Columns: 14

card_txn_count_so_far → 0 nulls (every transaction gets a count, including 0 for first-ever)
card_avg_amt_so_far → 13,553 nulls (each card's first transaction — no prior history)
amt_deviation_ratio → 13,553 nulls (identical rows to above — confirms internal consistency)

**Worked example — card `13926`:**

| TransactionAmt | card_txn_count_so_far | card_avg_amt_so_far | amt_deviation_ratio |
|---|---|---|---|
| 68.5 | 0 | NULL | NULL |
| 150.0 | 1 | 68.5 | 2.19 |
| 100.0 | 2 | 109.25 | 0.92 |
| 500.0 | 9 | 125.06 | 4.00 |

Each rolling value was manually checked against a hand calculation from prior rows only — confirmed correct at every step.

## Issues Encountered & Resolved

1. **Query timeouts (`Lost connection to MySQL server`)** — root-caused to two separate issues:
   - No index existed on `card1`/`TransactionDT`, the columns used for partitioning and ordering. Fixed with `ALTER TABLE raw_transactions ADD INDEX idx_card_time (card1, TransactionDT);`
   - Multiple earlier query attempts were left running in the background after being interrupted client-side (confirmed via `SHOW FULL PROCESSLIST`), competing for resources with new attempts. Fixed with `KILL <process_id>` on each stuck query.
2. **Redundant computation** — the original query recalculated the same `AVG(TransactionAmt) OVER(...)` window function four separate times within one `CASE` block, causing it to hang at scale. Fixed by splitting into two CTEs: compute the average once (`card_behaviour`), then reuse it via simple division (`card_behaviour_final`).
3. **Code duplication** — `build_features.py` initially contained a hardcoded copy of the SQL query. Refactored to read directly from `sql/feature_engineering.sql`, making the `.sql` file the single source of truth.

## Conclusion
All engineered features were verified correct via null-pattern consistency checks and manual worked-example validation. Phase 2 is complete — proceeding to Phase 3 (Statistical Validation / EDA).