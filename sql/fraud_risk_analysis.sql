
-- =====================================================
-- FRAUD RISK ANALYSIS
-- =====================================================


-- 1. FRAUD AMOUNT SUMMARY

SELECT
    COUNT(*) AS fraud_count,
    ROUND(SUM(amount), 2) AS total_fraud_labelled_amount,
    ROUND(AVG(amount), 2) AS average_fraud_amount,
    ROUND(AVG(amount) FILTER (WHERE amount > 0), 2)
        AS average_positive_fraud_amount
FROM transactions
WHERE class = 1;


-- 2. TRANSACTION AMOUNT SEGMENTS

SELECT
    CASE
        WHEN amount < 25 THEN 'Under $25'
        WHEN amount < 100 THEN '$25–$99.99'
        WHEN amount < 500 THEN '$100–$499.99'
        ELSE '$500 and above'
    END AS amount_segment,

    COUNT(*) AS total_transactions,

    SUM(CASE WHEN class = 1 THEN 1 ELSE 0 END)
        AS fraud_transactions,

    ROUND(
        100.0 * SUM(CASE WHEN class = 1 THEN 1 ELSE 0 END)
        / COUNT(*),
        4
    ) AS fraud_rate_percentage

FROM transactions
GROUP BY amount_segment
ORDER BY MIN(amount);


-- 3. FRAUD SHARE OF TOTAL TRANSACTION VALUE

SELECT
    ROUND(
        100.0 * SUM(amount) FILTER (WHERE class = 1)
        / NULLIF(SUM(amount), 0),
        4
    ) AS fraud_labelled_amount_share_percentage
FROM transactions;
