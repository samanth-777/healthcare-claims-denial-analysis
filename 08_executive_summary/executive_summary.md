# Executive Summary
## Riverside Health System — Claims Denial Root Cause Analysis

| Field | Details |
|---|---|
| **Prepared For** | David Okafor, CFO |
| **Prepared By** | Samanth Madhesh, Business Analyst |
| **Date** | September 2025 |
| **Data note** | Claim-level data is synthetic, CMS-calibrated |

---

## Headline

Denial rate rose from **8.2%** (Q3 2024) to **11.7%** (Q1 2025). Incremental annual revenue exposure above the Q3 baseline is **$1,897,574.00**.

| Metric | Value | Query |
|---|---|---|
| Q3 2024 denial rate | 8.2% | `01_denial_rate_by_quarter.sql` |
| Q4 2024 denial rate | 9.6% | same |
| Q1 2025 denial rate | 11.7% | same |
| Q3 revenue at risk | $1,098,360.48 | `05_revenue_at_risk.sql` 5A |
| Q4 revenue at risk | $1,316,501.76 | same |
| Q1 revenue at risk | $1,595,158.11 | same |
| Incremental annual exposure | $1,897,574.00 | `05_revenue_at_risk.sql` 5B (RECONCILED) |

Formula: `Claims_Denied × $79.73`; headline = `680,000 × (0.117 − 0.082) × $79.73`.

## Top drivers (71.0% of denial-log sample)

| Code | Share | Est. Impact (share × Q1 RAR) | Query |
|---|---|---|---|
| CO-4 | 28.0% | $446,644.27 | `05_revenue_at_risk.sql` 5C |
| CO-16 | 24.0% | $382,837.95 | same |
| PR-96 | 19.0% | $303,080.04 | same |

## Root causes (summary)

1. **CO-4:** CMS modifier policy change (Jan 2025) not operationalized into documentation templates or pre-submission validation.
2. **CO-16:** Dual track — Epic–Waystar NPI mapping failure on Medicare Advantage after Nov 2024 upgrade; West Allis registration/eligibility gap.
3. **PR-96:** Three MA payer ID updates not confirmed in Waystar before Q1 2025 billing cycle.

## Recommendation

Approve remediation requirements BR-01–BR-06 (`04_brd/brd.md`) and UAT pack (`06_uat_plan/`) before adding billing FTEs. Target post-remediation denial rate **≤ 8.5%** (projected ~8.3% if all three root causes are addressed).
