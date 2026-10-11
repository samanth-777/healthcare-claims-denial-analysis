-- ============================================================
-- 05_revenue_at_risk.sql
-- Purpose: Compute quarterly revenue at risk and reconcile the
--          headline incremental annual revenue exposure.
--
-- Formulae:
--   Revenue_at_Risk = Claims_Denied * Avg_Allowed_Amount
--   Incremental_Annual =
--       ANNUAL_CLAIMS * (LATEST_DENIAL_RATE - BASELINE_DENIAL_RATE)
--       * AVG_ALLOWED_AMOUNT
--
-- Top-3 Est_Impact =
--       denial-log share × Q1 2025 Revenue_at_Risk
--
-- Data:
--   data/processed/quarterly_claims_summary.csv
--   data/processed/analysis_constants.csv
--   data/processed/riverside_denial_log.csv
-- ============================================================

-- 5A. Quarterly revenue at risk
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


-- 5B. Headline incremental annual exposure + reconcile flag
WITH consts AS (
    SELECT
        MAX(CASE WHEN Constant = 'AVG_ALLOWED_AMOUNT' THEN Value END) AS avg_allowed,
        MAX(CASE WHEN Constant = 'ANNUAL_CLAIMS' THEN Value END) AS annual_claims,
        MAX(CASE WHEN Constant = 'BASELINE_DENIAL_RATE' THEN Value END) AS baseline_rate,
        MAX(CASE WHEN Constant = 'LATEST_DENIAL_RATE' THEN Value END) AS latest_rate,
        MAX(CASE WHEN Constant = 'INCREMENTAL_ANNUAL_REVENUE_EXPOSURE' THEN Value END) AS headline
    FROM analysis_constants
),
calc AS (
    SELECT
        annual_claims,
        baseline_rate,
        latest_rate,
        avg_allowed,
        ROUND(annual_claims * (latest_rate - baseline_rate) * avg_allowed, 2)
            AS computed_incremental_annual_exposure,
        headline AS stored_headline
    FROM consts
)
SELECT
    *,
    CASE
        WHEN computed_incremental_annual_exposure = stored_headline THEN 'RECONCILED'
        ELSE 'MISMATCH'
    END AS reconcile_status
FROM calc;


-- 5C. Top-3 denial driver estimated impact
WITH q1 AS (
    SELECT ROUND(Claims_Denied * Avg_Allowed_Amount, 2) AS q1_revenue_at_risk
    FROM quarterly_claims_summary
    WHERE Quarter = 'Q1 2025'
),
mix AS (
    SELECT
        Denial_Code,
        Denial_Description,
        COUNT(*) AS sample_claims,
        COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS share
    FROM riverside_denial_log
    GROUP BY Denial_Code, Denial_Description
)
SELECT
    m.Denial_Code,
    m.Denial_Description,
    m.sample_claims,
    ROUND(100.0 * m.share, 1) AS Share_Pct,
    q1.q1_revenue_at_risk,
    ROUND(q1.q1_revenue_at_risk * m.share, 2) AS Est_Impact
FROM mix m
CROSS JOIN q1
WHERE m.Denial_Code IN ('CO-4', 'CO-16', 'PR-96')
ORDER BY Est_Impact DESC;
