-- ============================================================
-- 02_top_reason_codes.sql
-- Purpose: Rank denial reason codes by volume and share
-- Data: data/processed/riverside_denial_log.csv
-- ============================================================

SELECT
    Denial_Code,
    Denial_Description,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted,
    ROUND(AVG(Submitted_Charge), 2) AS Avg_Claim_Value,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS Share_Pct
FROM riverside_denial_log
GROUP BY Denial_Code, Denial_Description
ORDER BY Total_Claims DESC;
