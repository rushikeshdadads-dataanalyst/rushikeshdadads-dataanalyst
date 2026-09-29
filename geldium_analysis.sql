-- Geldium Delinquency Risk Analytics
-- MySQL 8+
-- Load the CSV into table `geldium` before running.

CREATE DATABASE IF NOT EXISTS geldium_analytics;
USE geldium_analytics;

-- Basic checks
SELECT COUNT(*) AS total_customers FROM geldium;

SELECT
    SUM(Delinquent_Account = 1) AS delinquent_customers,
    SUM(Delinquent_Account = 0) AS non_delinquent_customers,
    ROUND(100 * AVG(Delinquent_Account), 2) AS delinquency_rate_pct
FROM geldium;

-- Data quality
SELECT
    SUM(Customer_ID IS NULL) AS missing_customer_id,
    SUM(Income IS NULL) AS missing_income,
    SUM(Loan_Balance IS NULL) AS missing_loan_balance,
    SUM(Credit_Score IS NULL) AS missing_credit_score
FROM geldium;

SELECT COUNT(*) AS duplicate_customer_ids
FROM (
    SELECT Customer_ID
    FROM geldium
    GROUP BY Customer_ID
    HAVING COUNT(*) > 1
) d;

-- Delinquency by age group
SELECT
    Age_Group,
    COUNT(*) AS customers,
    SUM(Delinquent_Account = 1) AS delinquent_customers,
    ROUND(100 * AVG(Delinquent_Account), 2) AS delinquency_rate_pct
FROM geldium
GROUP BY Age_Group
ORDER BY delinquency_rate_pct DESC;

-- Credit score band
SELECT
    Credit_Score_Band,
    COUNT(*) AS customers,
    SUM(Delinquent_Account = 1) AS delinquent_customers,
    ROUND(100 * AVG(Delinquent_Account), 2) AS delinquency_rate_pct
FROM geldium
GROUP BY Credit_Score_Band
ORDER BY delinquency_rate_pct DESC;

-- Employment status
SELECT
    Employment_Status,
    COUNT(*) AS customers,
    ROUND(100 * AVG(Delinquent_Account), 2) AS delinquency_rate_pct
FROM geldium
GROUP BY Employment_Status
ORDER BY delinquency_rate_pct DESC;

-- Card type
SELECT
    Credit_Card_Type,
    COUNT(*) AS customers,
    ROUND(100 * AVG(Delinquent_Account), 2) AS delinquency_rate_pct
FROM geldium
GROUP BY Credit_Card_Type
ORDER BY delinquency_rate_pct DESC;

-- Location
SELECT
    Location,
    COUNT(*) AS customers,
    ROUND(100 * AVG(Delinquent_Account), 2) AS delinquency_rate_pct
FROM geldium
GROUP BY Location
ORDER BY delinquency_rate_pct DESC;

-- High-risk flag effectiveness
SELECT
    High_Risk_Flag,
    Delinquent_Account,
    COUNT(*) AS customers
FROM geldium
GROUP BY High_Risk_Flag, Delinquent_Account
ORDER BY High_Risk_Flag, Delinquent_Account;

-- Precision / recall diagnostic
SELECT
    SUM(High_Risk_Flag = 1 AND Delinquent_Account = 1) AS true_positives,
    SUM(High_Risk_Flag = 1 AND Delinquent_Account = 0) AS false_positives,
    SUM(High_Risk_Flag = 0 AND Delinquent_Account = 1) AS false_negatives,
    ROUND(
        100 * SUM(High_Risk_Flag = 1 AND Delinquent_Account = 1) /
        NULLIF(SUM(High_Risk_Flag = 1),0), 2
    ) AS precision_pct,
    ROUND(
        100 * SUM(High_Risk_Flag = 1 AND Delinquent_Account = 1) /
        NULLIF(SUM(Delinquent_Account = 1),0), 2
    ) AS recall_pct
FROM geldium;

-- Numeric relationship with delinquency
SELECT
    ROUND(CORR(Age, Delinquent_Account), 4) AS age_corr,
    ROUND(CORR(Income, Delinquent_Account), 4) AS income_corr,
    ROUND(CORR(Credit_Score, Delinquent_Account), 4) AS credit_score_corr,
    ROUND(CORR(Credit_Utilization, Delinquent_Account), 4) AS utilization_corr,
    ROUND(CORR(Missed_Payments, Delinquent_Account), 4) AS missed_payments_corr,
    ROUND(CORR(Loan_Balance, Delinquent_Account), 4) AS loan_balance_corr,
    ROUND(CORR(Debt_to_Income_Ratio, Delinquent_Account), 4) AS dti_corr,
    ROUND(CORR(Account_Tenure, Delinquent_Account), 4) AS tenure_corr
FROM geldium;
