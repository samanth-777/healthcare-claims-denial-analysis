-- ============================================================
-- Riverside Health System — Claims Denial Profiling Queries
-- Phase 2: Denial Analysis
-- Analyst: Samanth Madhesh
-- Data Source: riverside_denial_log (500 synthetic claims,
--              anchored to CMS Medicare Physician & Other
--              Practitioners PUF 2024, Wisconsin providers)
-- Period: Q3 2024 – Q1 2025
-- ============================================================


-- ------------------------------------------------------------
-- QUERY 1: Denial volume and dollar impact by reason code
-- Purpose: Confirm top denial drivers by claim count and
--          submitted charge amount across all quarters
-- Finding: CO-16 leads by volume (134 claims, $64.8K);
--          CO-4 and PR-96 follow. Top 3 codes = 74.8% of
--          all denials — confirms project scope is correct.
-- ------------------------------------------------------------

SELECT
    Denial_Code,
    Denial_Description,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted,
    ROUND(AVG(Submitted_Charge), 2) AS Avg_Claim_Value
FROM riverside_denial_log
GROUP BY Denial_Code, Denial_Description
ORDER BY Total_Claims DESC;


-- ------------------------------------------------------------
-- QUERY 2: Denial trend by quarter and reason code
-- Purpose: Show quarter-over-quarter spike for CO-4, CO-16,
--          PR-96 to identify when each problem started
-- Finding: CO-16 nearly 3x from Q3→Q1 (25→66 claims);
--          CO-4 doubles Q3→Q4 then holds; PR-96 flat then
--          doubles in Q1 2025. Each spike timing maps to a
--          distinct root cause event.
-- ------------------------------------------------------------

SELECT
    Quarter,
    Denial_Code,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted
FROM riverside_denial_log
WHERE Denial_Code IN ('CO-4', 'CO-16', 'PR-96')
GROUP BY Quarter, Denial_Code
ORDER BY Quarter ASC, Total_Claims DESC;


-- ------------------------------------------------------------
-- QUERY 3: Denial breakdown by payer and reason code
-- Purpose: Identify which payers are driving which denial
--          codes; test Sandra Kim's MA contract hypothesis
-- Finding: PR-96 concentrated in Humana Gold Plus (18),
--          Anthem MedicarePreferred (12), WellCare Alliant
--          (10) — all three MA contract renewals confirmed.
--          CO-16 spread across all payer types = systemic
--          submission issue, not payer-specific.
-- ------------------------------------------------------------

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


-- ------------------------------------------------------------
-- QUERY 4: Denial breakdown by clinic location
-- Purpose: Test Patricia Nguyen's hypothesis that West Allis
--          has disproportionately high denial concentration
-- Finding: West Allis shows 28 CO-4 denials — more than
--          half of Downtown's 52 despite being a fraction of
--          its size. CO-16 at 26 also elevated. Points to
--          training and workflow gaps at newly onboarded site.
-- ------------------------------------------------------------

SELECT
    Clinic_Location,
    Denial_Code,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted
FROM riverside_denial_log
WHERE Denial_Code IN ('CO-4', 'CO-16', 'PR-96')
GROUP BY Clinic_Location, Denial_Code
ORDER BY Clinic_Location ASC, Total_Claims DESC;


-- ------------------------------------------------------------
-- QUERY 5: Denial breakdown by procedure code family
-- Purpose: Test Marcus Webb's hypothesis that CO-4 is
--          concentrated in PT (97xxx), radiology (70-77xxx),
--          and E&M (99xxx) code families
-- Finding: 99xxx dominates all three denial codes (82 CO-4,
--          81 CO-16, 67 PR-96). 97xxx is clear second driver
--          with 20 CO-4 denials. Radiology fragmented but
--          adds ~30 CO-4 denials combined. Marcus confirmed.
-- ------------------------------------------------------------

SELECT
    SUBSTR(HCPCS_Code, 1, 2) AS Code_Family,
    Denial_Code,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted
FROM riverside_denial_log
WHERE Denial_Code IN ('CO-4', 'CO-16', 'PR-96')
GROUP BY Code_Family, Denial_Code
ORDER BY Total_Claims DESC;


-- ------------------------------------------------------------
-- QUERY 6: CO-16 trend by quarter and payer type
-- Purpose: Test James Tirado's hypothesis that the Nov 2024
--          Waystar upgrade caused NPI field drops specifically
--          on Medicare Advantage claims
-- Finding: MA CO-16 dropped Q3→Q4 then spiked Q1 (10→8→24),
--          suggesting interface issue materialized in Q1.
--          Commercial CO-16 climbs steadily (10→25→35) across
--          all quarters — points to a second CO-16 root cause:
--          West Allis registration workflow gap (not interface).
--          Two distinct CO-16 drivers confirmed.
-- ------------------------------------------------------------

SELECT
    Quarter,
    Denial_Code,
    Payer_Type,
    COUNT(*) AS Total_Claims,
    ROUND(SUM(Submitted_Charge), 2) AS Total_Submitted
FROM riverside_denial_log
WHERE Denial_Code = 'CO-16'
GROUP BY Quarter, Denial_Code, Payer_Type
ORDER BY Quarter ASC, Total_Claims DESC;
