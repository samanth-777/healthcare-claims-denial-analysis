# Business Requirements Document (BRD)
## Claims Denial Remediation — Top Three Denial Drivers

| Field | Details |
|---|---|
| **Client** | Riverside Health System (simulated) |
| **Prepared By** | Samanth Madhesh, Business Analyst |
| **Date** | September 2025 |
| **Version** | 1.0 |
| **Source RCA** | `03_root_cause_analysis/rca_document.md` |

---

## 1. Purpose

Define business and system requirements to remediate root causes for denial codes **CO-4**, **CO-16**, and **PR-96**, which represent **71.0%** of the synthetic denial-log sample (`02_top_reason_codes.sql`).

## 2. Current-State Summary

| Code | Root Cause (RCA) | Primary Owner |
|---|---|---|
| CO-4 | No change-management process for CMS modifier policy updates | Marcus Webb |
| CO-16 Track A | Epic–Waystar HL7 mapping drop of rendering provider NPI post-upgrade | James Tirado |
| CO-16 Track B | West Allis registration / insurance verification gap | Patricia Nguyen |
| PR-96 | MA payer ID configuration not loaded before Q1 2025 billing cycle | Sandra Kim / James Tirado |

## 3. Requirements

### BR-01 — CMS Modifier Change Management (CO-4)

| Attribute | Detail |
|---|---|
| **ID** | BR-01 |
| **Statement** | Riverside shall maintain a documented change-management workflow that translates CMS modifier/documentation policy updates into Epic template changes, coder guidance, and Waystar pre-submission validation rules before the policy effective date. |
| **Acceptance Criteria** | (a) Workflow SOP approved by Coding & Compliance; (b) Epic templates for E&M, PT, and radiology include modifier documentation prompts; (c) Waystar flags unsupported modifier-59/X-modifier combinations pre-submission. |
| **Owner** | Marcus Webb |
| **Priority** | High |

### BR-02 — Post-Upgrade Interface Re-Validation (CO-16 Track A)

| Attribute | Detail |
|---|---|
| **ID** | BR-02 |
| **Statement** | All Waystar (or Epic) upgrades that affect outbound claim mappings shall require interface re-validation with revenue-cycle sign-off before go-live. |
| **Acceptance Criteria** | (a) Rendering provider NPI present on 100% of sampled MA test claims; (b) Interface specification versioned and updated; (c) Sign-off recorded by IT and Revenue Cycle. |
| **Owner** | James Tirado |
| **Priority** | Critical |

### BR-03 — Registration Eligibility Hard Stop (CO-16 Track B)

| Attribute | Detail |
|---|---|
| **ID** | BR-03 |
| **Statement** | Epic registration shall enforce real-time eligibility verification before encounter open at all clinics, including newly onboarded sites. |
| **Acceptance Criteria** | (a) Incomplete subscriber/group fields block encounter open; (b) West Allis staff complete revenue-cycle onboarding training; (c) Clinic onboarding checklist mandates revenue-cycle training. |
| **Owner** | Patricia Nguyen |
| **Priority** | High |

### BR-04 — Payer Configuration Gate (PR-96)

| Attribute | Detail |
|---|---|
| **ID** | BR-04 |
| **Statement** | Contract renewals that change payer IDs or coverage terms shall not open a billing cycle until Waystar configuration is updated and verified. |
| **Acceptance Criteria** | (a) Ticketing handoff from Contracting to IT; (b) Pre-quarter configuration audit completed; (c) Humana Gold Plus, WellCare Alliant, and Anthem MedicarePreferred IDs validated before billing. |
| **Owner** | Sandra Kim / James Tirado |
| **Priority** | Critical |

### BR-05 — Pre-Submission Claim Scrubbing Layer

| Attribute | Detail |
|---|---|
| **ID** | BR-05 |
| **Statement** | Waystar shall apply pre-submission scrubbing rules covering missing NPI (MA), modifier/documentation mismatches, and payer ID validity. |
| **Acceptance Criteria** | (a) Rules enabled for CO-4, CO-16, and PR-96 patterns; (b) Scrub failures route to workqueue before payer submission; (c) Rule coverage documented in UAT evidence. |
| **Owner** | James Tirado |
| **Priority** | High |

### BR-06 — Denial Rate KPI Monitoring

| Attribute | Detail |
|---|---|
| **ID** | BR-06 |
| **Statement** | Revenue Cycle shall monitor quarterly denial rate with a target of ≤ 8.5% after remediation. |
| **Acceptance Criteria** | (a) Dashboard shows quarterly denial rate and revenue at risk using `Claims_Denied × $79.73`; (b) Top-3 code shares refreshed monthly; (c) CFO review packet produced each quarter. |
| **Owner** | Patricia Nguyen |
| **Priority** | Medium |

## 4. Non-Functional Requirements

| ID | Statement |
|---|---|
| NFR-01 | Requirements and test evidence shall not rely on PHI; synthetic datasets are acceptable for UAT design demonstration. |
| NFR-02 | All dollar figures cited in executive materials shall reconcile to SQL outputs in `02_denial_analysis/sql/` (especially `05_revenue_at_risk.sql`). |

## 5. Traceability

See `06_uat_plan/requirements_traceability_matrix.md` for BRD ↔ UAT mapping.
