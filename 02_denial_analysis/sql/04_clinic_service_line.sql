-- ============================================================
-- 04_clinic_service_line.sql
-- Purpose: Denial concentration by clinic and service line
-- Data: data/processed/riverside_denial_log.csv
-- ============================================================

-- 4A. By clinic
SELECT
    Clinic_Location,
    Denial_Code,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted
FROM riverside_denial_log
WHERE Denial_Code IN ('CO-4', 'CO-16', 'PR-96')
GROUP BY Clinic_Location, Denial_Code
ORDER BY Clinic_Location ASC, Total_Claims DESC;

-- 4B. By service line
SELECT
    Service_Line,
    Denial_Code,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted
FROM riverside_denial_log
WHERE Denial_Code IN ('CO-4', 'CO-16', 'PR-96')
GROUP BY Service_Line, Denial_Code
ORDER BY Total_Claims DESC;

-- 4C. By HCPCS family (first two characters)
-- Cast: DuckDB may infer numeric HCPCS codes as BIGINT from CSV.
SELECT
    SUBSTR(CAST(HCPCS_Code AS VARCHAR), 1, 2) AS Code_Family,
    Denial_Code,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted
FROM riverside_denial_log
WHERE Denial_Code IN ('CO-4', 'CO-16', 'PR-96')
GROUP BY Code_Family, Denial_Code
ORDER BY Total_Claims DESC;
