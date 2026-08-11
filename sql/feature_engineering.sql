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
    amt_deviation_ratio,
    V279, V280, V284, V285, V286, V287, V290, V291,
    V293, V294, V295, V297, V298, V299, V302, V303,
    V304, V305, V306, V307, V308, V309, V310, V311, V312,
    V292, V316, V317, V318, V319, V320, V321,
    V95, V96, V97, V98, V99, V102, V103, V104,
    V105, V106, V107, V108, V109, V118, V119,
    V120, V121, V122, V123, V124, V125, V126,
    V127, V128, V129, V130, V131, V132, V133,
    V134, V135, V136, V137
FROM card_behaviour_final;