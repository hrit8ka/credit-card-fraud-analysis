
-- =====================================================
-- CREDIT CARD FRAUD ANALYSIS
-- Database: fraud_detection
-- Table: transactions
-- =====================================================


-- 1. DATASET OVERVIEW
-- Check the total number of transactions.

SELECT
    COUNT(*) AS total_transactions
FROM transactions;


-- 2. TRANSACTION DISTRIBUTION
-- Compare legitimate and fraudulent transactions.

SELECT
    CASE
        WHEN class = 0 THEN 'Legitimate'
        WHEN class = 1 THEN 'Fraud'
    END AS transaction_type,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY class
ORDER BY class;


-- 3. OVERALL FRAUD RATE
-- Calculate the percentage of fraudulent transactions.

SELECT
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN class = 1 THEN 1 ELSE 0 END)
        AS fraud_transactions,
    ROUND(
        100.0 * SUM(CASE WHEN class = 1 THEN 1 ELSE 0 END)
        / COUNT(*),
        4
    ) AS fraud_rate_percentage
FROM transactions;


-- 4. TRANSACTION AMOUNT ANALYSIS
-- Compare transaction amounts by class.

SELECT
    CASE
        WHEN class = 0 THEN 'Legitimate'
        WHEN class = 1 THEN 'Fraud'
    END AS transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(AVG(amount), 2) AS average_amount,
    ROUND(MIN(amount), 2) AS minimum_amount,
    ROUND(MAX(amount), 2) AS maximum_amount,
    ROUND(SUM(amount), 2) AS total_amount
FROM transactions
GROUP BY class
ORDER BY class;


-- 5. TOP 10 HIGHEST-VALUE FRAUD TRANSACTIONS

SELECT
    transaction_id,
    transaction_time,
    amount
FROM transactions
WHERE class = 1
ORDER BY amount DESC
LIMIT 10;
