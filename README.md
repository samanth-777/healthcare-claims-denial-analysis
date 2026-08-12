# Riverside Health System — Claims Denial Root Cause Analysis

**Role:** Business Analyst (Simulated Client Engagement)  
**Tools:** SQL, Python, Excel, Power BI, Lucidchart  
**Timeline:** August – September 2025 (5-week engagement simulation)  
**Domain:** Healthcare Revenue Cycle / Claims Management

---

## Project Overview

Riverside Health System, a regional nonprofit health network in Milwaukee, WI submitting ~680,000 claims annually, engaged a Business Analyst to investigate a claim denial rate spike from 8.2% to 11.7% over three quarters — representing an estimated $2.1M in incremental annual revenue exposure above baseline.

The audit focused on the top three denial reason codes by volume (CO-4, CO-16, PR-96), which together accounted for 71% of all denials. Root causes were traced across three workflows: patient registration and insurance verification, medical coding and modifier application, and payer configuration management.

**Note:** This is a simulated engagement. All stakeholders, clinic names, and organizational details are fictional and constructed for portfolio demonstration purposes. Claim-level data was generated synthetically and calibrated to real CMS and industry benchmarks — see Data Sources below.

---

## The Business Problem

| Quarter | Denial Rate | Claims Submitted | Claims Denied | Est. Revenue at Risk |
|---|---|---|---|---|
| Q3 2024 | 8.2% | 168,000 | 13,776 | ~$1.10M |
| Q4 2024 | 9.6% | 172,000 | 16,512 | ~$1.32M |
| Q1 2025 | 11.7% | 171,000 | 20,007 | ~$1.60M |

Revenue at risk calculated using average Medicare-allowed amount of $79.73 per claim — sourced from CMS Medicare Physician & Other Practitioners PUF 2024 (Wisconsin providers). This is consistent with the 2025 Experian Health State of Claims Report, which found 41% of providers now report denial rates of 10% or more, up from 30% in 2022.

CFO declined to approve additional billing staff until root causes were documented and a remediation plan was approved.

---

## Top Denial Drivers

| Code | Description | Share of Denials | Est. Impact |
|---|---|---|---|
| CO-4 | Inconsistent modifier / procedure code | 28% | ~$448K |
| CO-16 | Missing or incomplete claim information | 24% | ~$384K |
| PR-96 | Non-covered charge / payer ID mismatch | 19% | ~$304K |

---

## Repository Structure

```
healthcare-claims-denial-analysis/
├── README.md
├── 01_project_charter/
│   ├── project_charter_v1.1.md     ← Scope, stakeholders, timeline, approvals
│   └── client_brief_v1.1.md        ← Engagement context, stakeholder interviews, denial data
├── 02_denial_analysis/
│   ├── denial_profiling.sql        ← SQL queries by reason code, payer, clinic, service line
│   └── riverside_denial_log.csv   ← 500-row denial dataset (CMS-calibrated synthetic records)
├── 03_root_cause_analysis/
│   └── rca_document.md             ← 5-Why analysis per denial driver; current state documentation
├── 04_brd/
│   └── brd.md                      ← Business Requirements Document (top 3 denial drivers)
├── 05_workflow_diagrams/
│   ├── current_state_claims_submission.png
│   └── future_state_claims_submission.png
├── 06_uat_plan/
│   └── uat_test_plan.xlsx          ← Test cases mapped to BRD requirements
└── 07_executive_summary/
    └── executive_summary.md        ← CFO-ready 1-page findings and recommendations
```

---

## Key Findings

- **3 root causes identified** across registration, coding, and payer configuration workflows
- **Primary driver of CO-16:** Epic-to-Waystar interface mapping failure post-November 2024 upgrade — rendering provider NPI field dropped on ~62% of Medicare Advantage claims
- **Primary driver of CO-4:** CMS modifier policy change (Jan 2025) not operationalized in coding workflow — modifier 59/X-modifier family applied without required procedure note documentation
- **Primary driver of PR-96:** Payer ID updates for 3 Medicare Advantage contract renewals (Humana Gold Plus, WellCare Alliant, Anthem MedicarePreferred) not fully loaded into Waystar before Q1 2025 billing cycle opened
- **Projected denial rate post-remediation:** 8.3% (within target of 8.5%) if all three root causes are addressed

---

## Skills Demonstrated

- Python scripting for large dataset extraction and synthetic data generation (3.1GB CMS PUF file)
- SQL-based denial data profiling and segmentation by reason code, payer, clinic, and service line
- Root cause analysis (5-Why methodology)
- Business Requirements Document (BRD) authoring with acceptance criteria and stakeholder ownership
- UAT test plan design mapped to BRD requirements
- Workflow diagramming — current state and future state
- Power BI dashboard development for revenue cycle KPI monitoring
- Executive communication and CFO-ready findings presentation
- Healthcare revenue cycle domain knowledge (denial reason codes, payer configuration, EHR-to-billing interfaces, Medicare Advantage)

---

## Data Sources

| Source | How It Was Used |
|---|---|
| CMS Medicare Physician & Other Practitioners PUF 2024 | Real procedure code utilization, submitted charges, and allowed amounts for Wisconsin providers. Filtered to 88,574 rows across procedure families 97000s (PT), 70000s (radiology), and 99200s (E&M). Used to calibrate claim values in the denial log. Average allowed amount: $79.73. |
| Experian Health 2025 State of Claims Report | Industry benchmarks for denial rate trends, top denial triggers by rank, and staffing context. Survey of 250 healthcare professionals, June–July 2025. |
| Synthetic denial log (riverside_denial_log.csv) | 500 claim-level denial records generated in Python. Denial outcomes, clinic assignments, payer assignments, and reason codes are synthetic — calibrated to CMS and Experian benchmarks. HCPCS codes, procedure descriptions, and charge amounts are real CMS data. |
| CMS ANSI Claim Adjustment Reason Codes (CARC) | Official definitions for CO-4, CO-16, PR-96, and all other denial reason codes used in this engagement. |
