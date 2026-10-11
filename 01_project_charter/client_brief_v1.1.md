# Client Brief v1.1
## Riverside Health System — Engagement Context

| Field | Details |
|---|---|
| **Prepared By** | Samanth Madhesh, Business Analyst |
| **Date** | August 2025 |
| **Version** | 1.1 |

---

## Organization (simulated)

Riverside Health System is a fictional regional nonprofit health network in Milwaukee, WI, submitting approximately **680,000** claims annually across five clinic locations.

## Problem Statement

Denial rate increased across three quarters:

| Quarter | Denial Rate | Source |
|---|---|---|
| Q3 2024 | 8.2% | `data/processed/quarterly_claims_summary.csv` / notebook |
| Q4 2024 | 9.6% | same |
| Q1 2025 | 11.7% | same |

Incremental annual revenue exposure above baseline: **$1,897,574.00** (see `05_revenue_at_risk.sql`).

## Stakeholder Interview Themes

1. **Patricia Nguyen (Revenue Cycle):** Suspects West Allis (onboarded Q4 2024) has registration/insurance verification gaps driving CO-16 on commercial claims.
2. **Marcus Webb (Coding):** Links CO-4 spike to January 2025 CMS modifier documentation policy change not operationalized in Epic templates.
3. **James Tirado (IT):** Notes November 2024 Waystar upgrade (23.4 → 24.1); possible Epic-to-Waystar NPI mapping regression on Medicare Advantage claims.
4. **Sandra Kim (Contracting):** Three MA contract renewals effective 1 Jan 2025 (Humana Gold Plus, WellCare Alliant, Anthem MedicarePreferred) required payer ID updates in Waystar.
5. **David Okafor (CFO):** Will not fund additional AR staff until root causes and a remediation plan with measurable denial-rate target are documented.

## Data Available for Analysis

- Synthetic denial log (500 rows) — `data/processed/riverside_denial_log.csv`
- Quarterly population summary — `data/processed/quarterly_claims_summary.csv`
- Analysis constants — `data/processed/analysis_constants.csv`
- CMS sample anchors — `data/raw/cms_puf_wi_hcpcs_sample.csv`
- CMS CARC definitions for CO-4, CO-16, PR-96

## Engagement Constraints

- No production PHI; all claim-level records are synthetic
- Five-week timeline
- Deliverables must be audit-friendly: every headline dollar figure must tie to a SQL output
