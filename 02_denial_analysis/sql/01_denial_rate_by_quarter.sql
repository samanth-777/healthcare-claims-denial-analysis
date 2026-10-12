-- ============================================================
-- 01_denial_rate_by_quarter.sql
-- Purpose: Reproduce quarterly denial rates 8.2% / 9.6% / 11.7%
-- Data: data/processed/quarterly_claims_summary.csv
-- ============================================================

SELECT
    Quarter,
    Claims_Submitted,
    Claims_Denied,
    ROUND(100.0 * Claims_Denied / Claims_Submitted, 1) AS Denial_Rate_Pct,
    Avg_Allowed_Amount,
    ROUND(Claims_Denied * Avg_Allowed_Amount, 2) AS Revenue_at_Risk
FROM quarterly_claims_summary
ORDER BY
    CASE Quarter
        WHEN 'Q3 2024' THEN 1
        WHEN 'Q4 2024' THEN 2
        WHEN 'Q1 2025' THEN 3
    END;
