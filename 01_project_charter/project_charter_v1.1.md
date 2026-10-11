# Project Charter v1.1
## Claims Denial Root Cause Analysis and Revenue Cycle Process Improvement

| Field | Details |
|---|---|
| **Client** | Riverside Health System (simulated) |
| **Prepared By** | Samanth Madhesh, Business Analyst |
| **Date** | August 2025 |
| **Version** | 1.1 |
| **Status** | Approved for portfolio simulation |

---

## 1. Business Need

Riverside Health System’s claim denial rate rose from **8.2%** (Q3 2024) to **11.7%** (Q1 2025). Using the CMS-calibrated average allowed amount of **$79.73**, incremental annual revenue exposure above the Q3 baseline is **$1,897,574.00** (`02_denial_analysis/sql/05_revenue_at_risk.sql`, statement 5B).

The CFO declined additional billing headcount until root causes and a remediation plan were documented.

## 2. Objectives

1. Profile denial volume by reason code, payer, clinic, and service line.
2. Identify root causes for the top three denial drivers (CO-4, CO-16, PR-96).
3. Author BRD requirements with acceptance criteria and owners.
4. Define UAT cases mapped to BRD requirements.
5. Deliver a CFO-ready executive summary with projected post-remediation denial rate.

## 3. In Scope

- Denial codes CO-4, CO-16, and PR-96 (71% of the synthetic denial-log sample)
- Clinics: Downtown Milwaukee, West Allis, Southside, Wauwatosa, Brookfield
- Period: Q3 2024 – Q1 2025
- Workflows: registration/insurance verification, coding/modifiers, payer configuration

## 4. Out of Scope

- Contract renegotiation with payers
- Full EHR replacement
- Production PHI or live payer connectivity
- Implementation build beyond requirements and UAT design

## 5. Stakeholders

| Name | Role | Interest |
|---|---|---|
| David Okafor | CFO | Revenue exposure, remediation ROI |
| Patricia Nguyen | Revenue Cycle Director | Registration workflow, UAT approval |
| Marcus Webb | Director, Coding & Compliance | CO-4 / modifier policy |
| James Tirado | IT Systems Manager | Epic–Waystar interface, payer config |
| Sandra Kim | Payer Contracting | MA contract renewals / payer IDs |

## 6. Timeline (5-week simulation)

| Week | Phase | Deliverable |
|---|---|---|
| 1 | Discovery | Charter, client brief, interviews |
| 2 | Denial analysis | SQL profiling + denial log |
| 3 | Root cause | RCA document |
| 4 | Requirements | BRD + workflow diagrams |
| 5 | Validation & close | UAT plan, traceability matrix, executive summary |

## 7. Success Criteria

- Quarterly denial rates reproduced at 8.2% / 9.6% / 11.7%
- Revenue-at-risk headline reconciles in SQL
- Top-3 denial share quantified from the denial log
- Every BRD requirement mapped to at least one UAT case
- Projected post-remediation denial rate ≤ 8.5% target

## 8. Assumptions & Constraints

- Claim-level data is synthetic and CMS-calibrated (no PHI).
- Population quarterly volumes are engagement inputs stored in `data/quarterly_claims_summary.csv`.
- Average allowed amount fixed at $79.73 for all revenue-at-risk calculations.
- Processed datasets live under `data/processed/`; CMS sample anchors under `data/raw/`.
