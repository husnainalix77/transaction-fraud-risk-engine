WITH joined_data AS(
    SELECT
        t.*,
        i.TransactionID AS identity_txn_id
    FROM raw_transactions t  
    LEFT JOIN raw_identity i
    ON t.TransactionID = i.TransactionID               
),


identity_flagged AS(
    SELECT
    *,
    CASE WHEN identity_txn_id IS NULL THEN 0 ELSE 1 END AS has_identity_data
    FROM joined_data
),

card_behaviour AS(
    SELECT
    *,
    COUNT(*) OVER(
        PARTITION BY card1
        ORDER BY TransactionDT
        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
    ) AS card_txn_count_so_far,
    AVG(TransactionAmt) OVER(
        PARTITION BY card1
        ORDER BY TransactionDT
        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
    ) AS card_avg_amt_so_far
    FROM identity_flagged
),

card_behaviour_final AS(
    SELECT
    *,
    CASE
        WHEN card_avg_amt_so_far IS NULL OR card_avg_amt_so_far = 0 THEN NULL
        ELSE TransactionAmt / card_avg_amt_so_far
    END AS amt_deviation_ratio
    FROM card_behaviour
)

SELECT
    TransactionID,
    isFraud,
    TransactionDT,
    TransactionAmt,
    ProductCD,
    card1,
    card4,
    card6,
    addr1,
    P_emaildomain,
    has_identity_data,
    card_txn_count_so_far,
    card_avg_amt_so_far,
    amt_deviation_ratio
FROM card_behaviour_final;