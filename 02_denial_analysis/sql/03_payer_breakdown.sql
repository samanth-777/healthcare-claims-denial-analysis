-- ============================================================
-- 03_payer_breakdown.sql
-- Purpose: Denial volume by payer / payer type for top codes
-- Data: data/processed/riverside_denial_log.csv
-- ============================================================

SELECT
    Payer_Name,
    Payer_Type,
    Denial_Code,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted
FROM riverside_denial_log
WHERE Denial_Code IN ('CO-4', 'CO-16', 'PR-96')
GROUP BY Payer_Name, Payer_Type, Denial_Code
ORDER BY Total_Claims DESC;
