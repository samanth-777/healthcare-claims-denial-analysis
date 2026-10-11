# Requirements Traceability Matrix
## BRD Requirements ↔ UAT Test Cases

| BRD ID | Requirement (short) | UAT Case ID | UAT Case Title | Priority |
|---|---|---|---|---|
| BR-01 | CMS modifier change management | UAT-01 | Epic modifier documentation prompts present for E&M/PT/radiology | High |
| BR-01 | CMS modifier change management | UAT-02 | Waystar blocks unsupported modifier 59/X-modifier without note language | High |
| BR-02 | Post-upgrade interface re-validation | UAT-03 | MA test claim retains rendering provider NPI after mapping patch | Critical |
| BR-02 | Post-upgrade interface re-validation | UAT-04 | Upgrade checklist requires revenue-cycle sign-off before go-live | Critical |
| BR-03 | Registration eligibility hard stop | UAT-05 | Encounter open blocked when subscriber/group fields incomplete | High |
| BR-03 | Registration eligibility hard stop | UAT-06 | West Allis staff training completion recorded before clinic go-live | High |
| BR-04 | Payer configuration gate | UAT-07 | Humana / WellCare / Anthem payer IDs validated in Waystar | Critical |
| BR-04 | Payer configuration gate | UAT-08 | Billing cycle open blocked when config audit incomplete | Critical |
| BR-05 | Pre-submission claim scrubbing | UAT-09 | Scrub rules catch missing NPI, modifier mismatch, invalid payer ID | High |
| BR-05 | Pre-submission claim scrubbing | UAT-10 | Failed scrubs route to workqueue (not payer) | High |
| BR-06 | Denial rate KPI monitoring | UAT-11 | Dashboard denial rate matches quarterly summary calculation | Medium |
| BR-06 | Denial rate KPI monitoring | UAT-12 | Revenue-at-risk widget equals `Claims_Denied × $79.73` | Medium |
| NFR-01 | No PHI in demo evidence | UAT-13 | UAT evidence pack uses synthetic denial log only | Medium |
| NFR-02 | Dollar figures reconcile to SQL | UAT-14 | Executive $ figures match `05_revenue_at_risk.sql` outputs | High |

**Coverage:** Every BRD requirement (BR-01–BR-06, NFR-01–NFR-02) maps to ≥1 UAT case. Detailed steps live in `uat_test_plan.xlsx`.
