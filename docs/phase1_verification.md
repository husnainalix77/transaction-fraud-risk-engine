# Phase 1 Verification Log — Data Ingestion

**Date:** 2026-08-02

**Purpose:** Confirm that `train_transaction.csv` and `train_identity.csv` were loaded into MySQL (`raw_transactions`, `raw_identity`) without loss, corruption, or structural mismatch, before proceeding to Phase 2 (SQL Feature Engineering).

## Method
Data was loaded using a chunked ingestion script (`src/load_to_mysql.py`) — reading each CSV in 20,000-row chunks, downcasting numeric types to reduce memory footprint, and writing each chunk to MySQL via SQLAlchemy's `to_sql()`.

Verification was performed independently via `src/verify_load.py`, checking four dimensions: row counts, column names, null counts (on a representative column sample), and value-level accuracy on a random row sample.

## Results

### raw_transactions
| Check | Result |
|---|---|
| Row count | CSV: 590,540 — MySQL: 590,540 — **MATCH** |
| Column count | CSV: 394 — MySQL: 394 — **MATCH** |
| Null counts (sampled columns) | **MATCH** — no discrepancies |
| Value spot-check (10 random rows, all columns) | **MATCH** — all values identical |

### raw_identity
| Check | Result |
|---|---|
| Row count | CSV: 144,233 — MySQL: 144,233 — **MATCH** |
| Column count | CSV: 41 — MySQL: 41 — **MATCH** |
| Null counts (sampled columns) | **MATCH** — no discrepancies |
| Value spot-check (10 random rows, all columns) | **MATCH** — all values identical |

## Notable data characteristic confirmed during this phase
Roughly 75% of transactions have no matching row in `raw_identity` (144,233 identity rows vs. 590,540 total transactions). This is expected and will be treated as a usable signal (a `has_identity_data` flag) in Phase 2, via a `LEFT JOIN`, rather than as missing/corrupted data.

## Conclusion
All verification checks passed. The data in MySQL is confirmed to match the source CSVs exactly in structure and content. Phase 1 is complete — proceeding to Phase 2 (SQL Feature Engineering).