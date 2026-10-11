# Riverside Health System — Claims Denial Root Cause Analysis

**Role:** Business Analyst (simulated client engagement)  
**Tools:** SQL, Python, Excel, Power BI, Lucidchart  
**Timeline:** August – September 2025 (5-week engagement simulation)  
**Domain:** Healthcare revenue cycle / claims management

> **Data disclaimer:** Claim-level data in this repository is **synthetic**, generated for portfolio demonstration and **calibrated to CMS** Medicare Physician & Other Practitioners PUF 2024 (Wisconsin) allowed-amount benchmarks. Stakeholders, clinic names, and organizational details are fictional. See [Data Sources](#data-sources) and `data/data_dictionary.md`.

---

## Project overview

Riverside Health System, a regional nonprofit health network in Milwaukee, WI submitting **680,000** claims annually, engaged a Business Analyst to investigate a claim denial rate spike from **8.2%** to **11.7%** over three quarters.

Using the CMS-calibrated average allowed amount of **$79.73**, incremental annual revenue exposure above the Q3 2024 baseline is **$1,897,574.00** — reconciled in `02_denial_analysis/sql/05_revenue_at_risk.sql` (statement 5B → `RECONCILED`).

The audit focused on denial reason codes **CO-4**, **CO-16**, and **PR-96**, which together account for **71.0%** of the synthetic denial-log sample (`02_top_reason_codes.sql`).

![Quarterly denial rates](docs/images/quarterly_denial_rates.png)

---

## The business problem

| Quarter | Denial Rate | Claims Submitted | Claims Denied | Revenue at Risk |
|---|---|---|---|---|
| Q3 2024 | 8.2% | 168,000 | 13,776 | $1,098,360.48 |
| Q4 2024 | 9.6% | 172,000 | 16,512 | $1,316,501.76 |
| Q1 2025 | 11.7% | 171,000 | 20,007 | $1,595,158.11 |

**Source:** `02_denial_analysis/sql/01_denial_rate_by_quarter.sql` and `05_revenue_at_risk.sql` (5A).  
**Formula:** `Revenue_at_Risk = Claims_Denied × Avg_Allowed_Amount ($79.73)`.

Reproduce rates in `02_denial_analysis/notebooks/02_denial_eda.ipynb`.

![Revenue at risk by quarter](docs/images/revenue_at_risk.png)

CFO declined additional billing staff until root causes were documented and a remediation plan was approved.

---

## Top denial drivers

| Code | Description | Share of Denials | Est. Impact |
|---|---|---|---|
| CO-4 | Inconsistent modifier / procedure code | 28.0% | $446,644.27 |
| CO-16 | Missing or incomplete claim information | 24.0% | $382,837.95 |
| PR-96 | Non-covered charge / payer ID mismatch | 19.0% | $303,080.04 |

**Source:** `02_denial_analysis/sql/05_revenue_at_risk.sql` (5C).  
**Formula:** `Est_Impact = denial-log share × Q1 2025 Revenue_at_Risk ($1,595,158.11)`.

![Top denial codes](docs/images/top_denial_codes.png)

---

## Repository structure

```
healthcare-claims-denial-analysis/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/                      # CMS PUF filtered sample + download notes
│   ├── processed/riverside_denial_log.csv
│   └── data_dictionary.md
├── 01_project_charter/
│   ├── project_charter_v1.1.md
│   └── client_brief_v1.1.md
├── 02_denial_analysis/
│   ├── sql/
│   │   ├── 01_denial_rate_by_quarter.sql
│   │   ├── 02_top_reason_codes.sql
│   │   ├── 03_payer_breakdown.sql
│   │   ├── 04_clinic_service_line.sql
│   │   └── 05_revenue_at_risk.sql
│   ├── notebooks/
│   │   ├── 01_synthetic_data_generation.ipynb
│   │   └── 02_denial_eda.ipynb
│   └── src/generate_synthetic_data.py
├── 03_root_cause_analysis/
│   └── rca_document.md
├── 04_brd/
│   └── brd.md
├── 05_workflow_diagrams/
│   ├── current_state_claims_submission.png
│   └── future_state_claims_submission.png
├── 06_uat_plan/
│   ├── uat_test_plan.xlsx
│   └── requirements_traceability_matrix.md
├── 07_power_bi_dashboard/
│   ├── denial_dashboard.pbix
│   ├── dax_measures.md
│   └── screenshots/
├── 08_executive_summary/
│   └── executive_summary.md
└── docs/images/
```

---

## Key findings

- **3 root causes** across registration, coding, and payer configuration (`03_root_cause_analysis/rca_document.md`)
- **CO-16 primary system driver:** Epic-to-Waystar interface mapping failure post-November 2024 upgrade — rendering provider NPI dropped on ~62% of sampled Medicare Advantage CO-16 claims (stakeholder sample review in RCA)
- **CO-4 primary driver:** CMS modifier policy change (Jan 2025) not operationalized in coding workflow
- **PR-96 primary driver:** Payer ID updates for Humana Gold Plus, WellCare Alliant, and Anthem MedicarePreferred not fully loaded into Waystar before Q1 2025
- **Projected denial rate post-remediation:** ~8.3% (within CFO target of 8.5%) if all three root causes are addressed

---

## How to reproduce numbers

```bash
python -m pip install -r requirements.txt
python 02_denial_analysis/src/generate_synthetic_data.py
python 02_denial_analysis/src/run_sql.py 02_denial_analysis/sql/01_denial_rate_by_quarter.sql
python 02_denial_analysis/src/run_sql.py 02_denial_analysis/sql/05_revenue_at_risk.sql
```

Or open:

1. `02_denial_analysis/notebooks/01_synthetic_data_generation.ipynb`
2. `02_denial_analysis/notebooks/02_denial_eda.ipynb`

### Dollar figure → query map

| README figure | Value | Query output |
|---|---|---|
| Avg allowed amount | $79.73 | `analysis_constants.csv` / all RAR queries |
| Q3 / Q4 / Q1 revenue at risk | $1,098,360.48 / $1,316,501.76 / $1,595,158.11 | `05_revenue_at_risk.sql` 5A |
| Incremental annual exposure | $1,897,574.00 | `05_revenue_at_risk.sql` 5B |
| CO-4 / CO-16 / PR-96 est. impact | $446,644.27 / $382,837.95 / $303,080.04 | `05_revenue_at_risk.sql` 5C |

---

## Skills demonstrated

- Python synthetic data generation calibrated to CMS PUF anchors
- SQL denial profiling (reason code, payer, clinic, service line)
- Revenue-at-risk modeling with explicit headline reconciliation
- Root cause analysis (5-Why)
- BRD authoring with acceptance criteria
- UAT design + requirements traceability matrix (BRD ↔ UAT)
- Workflow current/future state diagramming
- Power BI measure design for revenue-cycle KPIs
- Executive communication for CFO stakeholders

---

## Data sources

| Source | How it was used |
|---|---|
| CMS Medicare Physician & Other Practitioners PUF 2024 | WI provider charge/allowed anchors in `data/raw/cms_puf_wi_hcpcs_sample.csv`; average allowed amount **$79.73** |
| Experian Health 2025 State of Claims Report | Industry context for elevated denial-rate trends (qualitative benchmark only; not used for dollar maths) |
| Synthetic denial log (`data/processed/riverside_denial_log.csv`) | 500 claim-level denial records from `02_denial_analysis/src/generate_synthetic_data.py` |
| CMS ANSI CARC | Official definitions for CO-4, CO-16, PR-96 and other codes |

---

## License

MIT — see `LICENSE`.
