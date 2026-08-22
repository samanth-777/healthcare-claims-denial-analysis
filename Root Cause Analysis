# Root Cause Analysis Document
## Claims Denial Root Cause Analysis and Revenue Cycle Process Improvement
### Riverside Health System

---

| Field | Details |
|---|---|
| **Project Name** | Claims Denial Root Cause Analysis and Revenue Cycle Process Improvement |
| **Client** | Riverside Health System |
| **Prepared By** | Samanth Madhesh, Business Analyst |
| **Date** | August 2025 |
| **Version** | 1.0 |
| **Phase** | Phase 3 of 5 |

---

## Purpose

This document presents the root cause analysis (RCA) findings for the three denial reason codes driving Riverside Health System's claim denial rate spike from 8.2% (Q3 2024) to 11.7% (Q1 2025): CO-4 (inconsistent modifier/procedure code), CO-16 (missing or incomplete information), and PR-96 (non-covered charge / payer ID mismatch). Together these three codes account for 71% of total denial volume and an estimated $1.42M in combined annual revenue impact.

Each denial driver is analyzed using the 5-Why methodology to trace the observable symptom back to its process, system, or governance root cause. Each section documents the current state workflow, the desired state, and remediation ownership -- inputs that will flow directly into the Business Requirements Document (Phase 4).

---

## Methodology

**5-Why Analysis** is a structured root cause technique that iteratively asks "why" a problem occurred until the underlying systemic cause -- rather than a surface-level symptom -- is identified. For this engagement, each 5-Why chain was constructed using:

- SQL denial profiling findings (Phase 2)
- Stakeholder interview notes (Week 1)
- CMS public use file benchmarking data
- Claim-level denial log (denial_log.xlsx)

Each chain terminates when the identified cause is one that, if addressed, would prevent recurrence -- not merely resolve the immediate instance.

---

## Summary of Root Causes

| Denial Code | Root Cause | Primary Owner | Est. Impact |
|---|---|---|---|
| CO-4 | No change management process for CMS modifier policy updates -- policy change not operationalized into provider documentation or billing system validation | Marcus Webb | ~$560K |
| CO-16 (Track A) | Epic-to-Waystar HL7 interface mapping failure post-November 2024 upgrade -- rendering provider NPI field dropped on ~62% of Medicare Advantage claims | James Tirado | ~$300K (est.) |
| CO-16 (Track B) | Registration workflow gap at West Allis clinic -- front desk staff not completing insurance verification at point of registration | Patricia Nguyen | ~$180K (est.) |
| PR-96 | Payer ID configuration not updated in Waystar before Q1 2025 billing cycle for three Medicare Advantage contract renewals | Sandra Kim / James Tirado | ~$380K |

---

# Section 1: CO-4 -- Inconsistent Modifier / Procedure Code

**Volume:** 28% of total denials
**Estimated Annual Impact:** ~$560K
**Primary Stakeholder:** Marcus Webb, Director of Coding and Compliance

---

## 1.1 Observation

CO-4 denial volume increased sharply beginning January 2025, doubling from Q3 2024 to Q4 2024 and continuing to climb through Q1 2025. Denials are concentrated in three high-volume procedure code families: E&M with ancillary services (99200s), physical therapy (97000s), and radiology (70000s). West Allis and Southside clinics account for a disproportionate share of volume relative to their claim counts. The denial spike correlates precisely with the January 1, 2025 effective date of a CMS modifier documentation policy change.

---

## 1.2 5-Why Analysis

**Why 1: Why are CO-4 denials spiking beginning January 2025?**

Claims are being submitted with modifier-procedure code combinations that payers are rejecting as inconsistent -- specifically, modifier 59 and the X-modifier family (XE, XS, XP, XU) applied to procedure codes without the required supporting documentation language in the claim record.

**Why 2: Why are modifiers being applied without required documentation?**

Coders are applying modifier 59/X-modifiers based on clinical context and prior practice, but the procedure notes submitted with the claim do not contain the specific documentation language now required under the CMS policy change effective January 1, 2025.

**Why 3: Why do the procedure notes not contain the required documentation?**

Providers were not operationally prepared for the January 2025 CMS modifier documentation requirement. A policy memo was distributed by the Coding and Compliance team in December 2024, but no mechanism existed to confirm readership, no provider training was conducted, and no update was made to Epic procedure note templates to prompt providers for the required fields at the point of documentation.

**Why 4: Why was no training conducted and no template update made?**

The policy change was treated as a communication task (memo distribution) rather than a workflow change requiring process redesign. The Coding and Compliance team had no formal change management protocol for CMS policy updates, and the EHR governance process for note template changes requires a separate IT change request that was never initiated.

**Why 5: Why is there no formal change management protocol for CMS policy updates affecting documentation requirements?**

Riverside has no structured mechanism to translate regulatory updates from CMS policy releases into operational workflow changes. Policy monitoring is handled informally by the Coding and Compliance team; there is no standing cross-functional process to assess downstream impact on provider documentation, coder behavior, or billing system validation logic when policy changes occur.

---

## 1.3 Root Cause Statement

The root cause of CO-4 denials is the absence of an operationalized change management process for CMS coding policy updates. The January 2025 modifier documentation requirement was identified by the Coding and Compliance team but was not translated into provider workflow changes, EHR template updates, or coder validation rules. As a result, coders continued to apply modifier 59/X-modifiers in good faith while procedure notes lacked the documentation required to support them under the new policy -- causing systematic payer rejection beginning the first billing cycle of 2025.

---

## 1.4 Current State -- Coding and Modifier Workflow

- CMS policy updates are monitored by Marcus Webb's team and communicated to providers via internal memo only
- No confirmation mechanism exists to verify that providers have read, understood, or applied policy memos
- Epic procedure note templates have not been updated to prompt providers for modifier-specific documentation (e.g., distinct procedure justification language required for modifier 59/XE/XS/XP/XU)
- Waystar has no pre-submission modifier validation rules -- claims with modifier-procedure mismatches pass through to payer submission without a system-level flag
- Coders perform manual review, but claim volume (~680,000/year) makes comprehensive modifier auditing infeasible without automation
- CO-4 denials are worked reactively by AR follow-up reps after payer rejection; no pre-submission catch exists

---

## 1.5 Desired State -- Coding and Modifier Workflow

- CMS policy changes affecting modifier or documentation requirements trigger a defined change management workflow: impact assessment, EHR template update request, provider communication with training, Waystar validation rule update, go-live verification
- Epic procedure note templates for high-volume service lines (E&M, physical therapy, radiology) include structured documentation prompts for modifier-sensitive scenarios -- coders cannot apply modifier 59/X-modifiers unless the procedure note contains the required supporting text
- Waystar is configured with pre-submission modifier validation rules that flag modifier-procedure mismatches before the claim leaves the billing queue, requiring coder review and sign-off before submission
- Coding and Compliance and IT establish a quarterly policy review cadence to assess upcoming CMS changes and initiate workflow updates proactively
- CO-4 denial rate returns to Q3 2024 baseline levels within two billing cycles of remediation go-live

---

## 1.6 Remediation Ownership

| Role | Owner | Responsibility |
|---|---|---|
| Primary | Marcus Webb | Policy workflow redesign, provider communication, Epic template change request |
| Supporting | James Tirado | Epic note template build, Waystar pre-submission validation rule configuration |
| Approver | Patricia Nguyen | Sign-off on BRD requirements, go-live authorization |

---

# Section 2: CO-16 -- Missing or Incomplete Claim Information

**Volume:** 24% of total denials
**Estimated Annual Impact:** ~$480K
**Primary Stakeholders:** James Tirado (Track A), Patricia Nguyen (Track B)

---

## 2.0 Dual Root Cause Note

Phase 2 SQL analysis revealed two statistically distinct CO-16 denial patterns that do not share a common cause and require separate remediation tracks:

- **Track A - Interface Failure:** CO-16 denials on Medicare Advantage claims, concentrated after November 14, 2024, characterized by missing rendering provider NPI. Root cause: Epic-to-Waystar HL7 interface mapping failure post-upgrade.
- **Track B - Registration Gap:** CO-16 denials on commercial claims at the West Allis clinic, distributed across the full analysis period, characterized by missing or incorrect insurance information at point of registration. Root cause: inadequate revenue cycle workflow training for West Allis front desk staff onboarded Q4 2024.

Both tracks are analyzed separately below.

---

## Track A: Epic-to-Waystar Interface Mapping Failure

**Estimated Impact:** ~$300K (est. 62% of CO-16 volume)
**Primary Owner:** James Tirado, IT Systems Manager

### 2A.1 Observation

Beginning in mid-November 2024, CO-16 denials on Medicare Advantage claims increased sharply. A sample review of 50 CO-16 denials from January 2025 found that 31 of 50 (62%) were missing the rendering provider NPI field on the submitted claim -- a required field for all Medicare Advantage payers. The onset of this pattern correlates precisely with the Waystar platform upgrade completed November 14, 2024 (version 23.4 to 24.1). Commercial payer CO-16 denials did not show the same NPI-missing pattern, consistent with Medicare Advantage-specific field mapping requirements.

### 2A.2 5-Why Analysis

**Why 1: Why are Medicare Advantage CO-16 denials spiking after November 2024?**

Claims submitted after November 14, 2024 are missing the rendering provider NPI field -- a required field for Medicare Advantage claim adjudication -- causing payers to reject the claim as incomplete.

**Why 2: Why is the rendering provider NPI missing from claims submitted after November 14?**

The Epic-to-Waystar HL7 interface is not correctly mapping the rendering provider NPI from Epic to the corresponding field in Waystar's claim output. The field is populated in Epic but is not appearing on the submitted claim.

**Why 3: Why is the HL7 interface failing to map the rendering provider NPI correctly?**

The Waystar platform upgrade on November 14, 2024 (version 23.4 to 24.1) changed the field mapping specification for the rendering provider NPI -- the upgrade altered how required provider fields are structured in the outbound claim format. The interface was not re-validated after the upgrade.

**Why 4: Why was the interface not re-validated after the upgrade?**

James Tirado's team assumed backward compatibility for the Waystar upgrade and did not initiate a post-upgrade interface validation. There was no change management checklist or upgrade protocol that required interface re-validation as a standard step before the upgraded system went live with claim submissions.

**Why 5: Why is there no required interface re-validation step in the upgrade protocol?**

Riverside has no formal change management protocol for billing platform upgrades that includes downstream impact assessment on EHR-to-billing interface specifications. Upgrade decisions are executed by IT without a structured cross-functional review involving revenue cycle operations or billing compliance.

### 2A.3 Root Cause Statement

The root cause of CO-16 Track A denials is a field mapping failure in the Epic-to-Waystar HL7 interface introduced by the November 2024 Waystar platform upgrade, compounded by the absence of a post-upgrade interface validation protocol. The rendering provider NPI -- required for Medicare Advantage claim adjudication -- is populated correctly in Epic but is dropped in transmission to Waystar due to a specification change in version 24.1 that was never identified or corrected. Approximately 62% of CO-16 denial volume is attributable to this single mapping failure.

### 2A.4 Current State -- EHR-to-Billing Interface

- Epic-to-Waystar data exchange operates via HL7 interface with field mappings defined in an interface specification document
- The interface specification document was last validated in Q2 2024 and has not been reviewed since the November 2024 Waystar upgrade
- No post-upgrade validation checklist exists; upgrade go-live decisions rest with IT without revenue cycle sign-off
- The rendering provider NPI and referring provider taxonomy code fields are confirmed as affected; the full scope of impacted fields has not been audited
- CO-16 denials attributed to missing NPI are currently identified only after payer rejection -- there is no pre-submission validation that confirms required fields are populated before claim transmission

### 2A.5 Desired State -- EHR-to-Billing Interface

- All billing platform upgrades trigger a mandatory interface re-validation step before go-live, with revenue cycle and coding compliance sign-off required
- Interface specification document is maintained as a version-controlled artifact and reviewed following any Waystar or Epic upgrade
- Pre-submission claim scrubbing in Waystar includes a validation rule confirming rendering provider NPI is populated on all Medicare Advantage claims before transmission
- James Tirado's team completes full interface re-validation and NPI field mapping patch within two weeks of RCA sign-off
- CO-16 denials attributable to missing NPI drop to zero within one billing cycle of the interface patch going live

### 2A.6 Remediation Ownership

| Role | Owner | Responsibility |
|---|---|---|
| Primary | James Tirado | Interface re-validation, NPI field mapping patch, upgrade protocol redesign |
| Supporting | Marcus Webb | Compliance review of field requirements for Medicare Advantage claim types |
| Approver | Patricia Nguyen | Revenue cycle sign-off on interface validation before patch go-live |

---

## Track B: West Allis Registration Workflow Gap

**Estimated Impact:** ~$180K (est. 38% of CO-16 volume)
**Primary Owner:** Patricia Nguyen, Revenue Cycle Director

### 2B.1 Observation

CO-16 denials on commercial payer claims are disproportionately concentrated at the West Allis clinic relative to its claim volume. The West Allis clinic was onboarded in Q4 2024 following a recent acquisition. Phase 2 SQL analysis confirmed that West Allis generates a higher CO-16 denial rate than any other Riverside location for commercial claims -- consistent with Patricia Nguyen's hypothesis that registration workflow gaps at the new location are contributing to incomplete claim submissions.

### 2B.2 5-Why Analysis

**Why 1: Why are commercial CO-16 denials disproportionately concentrated at West Allis?**

Claims originating from West Allis are being submitted with missing or incorrect insurance information -- including incomplete subscriber IDs, missing group numbers, and unverified coverage -- causing payers to reject claims as incomplete.

**Why 2: Why is insurance information missing or incorrect on West Allis claims?**

Front desk staff at West Allis are not consistently completing insurance verification at the point of registration. Required fields are being left blank or populated with unverified patient-reported information rather than confirmed payer data.

**Why 3: Why are West Allis staff not completing insurance verification correctly?**

West Allis front desk staff received a two-day Epic system training upon clinic onboarding in Q4 2024 but received no revenue cycle-specific training on insurance verification workflows, eligibility check procedures, or the downstream impact of registration errors on claim adjudication.

**Why 4: Why was revenue cycle workflow training not included in the West Allis onboarding?**

The West Allis onboarding plan was scoped and executed by the IT and clinic operations teams, with training focused on Epic system navigation. Revenue cycle workflow training was not included in the onboarding checklist because there was no standard onboarding protocol that mandated it for new or acquired clinic locations.

**Why 5: Why is there no standard onboarding protocol requiring revenue cycle training for new locations?**

Riverside has no enterprise-level clinic onboarding standard that includes revenue cycle workflow requirements. Each clinic acquisition or expansion has been managed as a discrete operational project without a centralized onboarding checklist governing training requirements across departments.

### 2B.3 Root Cause Statement

The root cause of CO-16 Track B denials is the absence of a standardized clinic onboarding protocol that includes revenue cycle workflow training for front desk and registration staff. West Allis clinic staff were onboarded on Epic system navigation but were not trained on insurance verification procedures, eligibility check requirements, or how registration errors translate into claim denials -- resulting in systematic submission of incomplete insurance information on commercial claims from the time of clinic onboarding.

### 2B.4 Current State -- Registration and Insurance Verification Workflow

- Insurance verification at point of registration is completed manually by front desk staff using patient-reported information and payer portal lookups
- No standardized registration workflow or checklist exists across Riverside clinic locations -- each clinic operates its own process
- Epic registration workflow does not include a hard stop or eligibility check requirement before a patient encounter can be opened
- West Allis staff have not received training on revenue cycle workflows, denial consequences of registration errors, or required insurance verification steps
- CO-16 denials from registration gaps are identified reactively after payer rejection; no pre-submission audit catches missing registration fields

### 2B.5 Desired State -- Registration and Insurance Verification Workflow

- A standardized insurance verification workflow is implemented across all Riverside clinic locations, including a mandatory real-time eligibility check integrated into the Epic registration workflow before encounter opening
- West Allis front desk staff complete a structured revenue cycle onboarding training covering insurance verification requirements, common registration errors, and their downstream impact on claims
- A standard clinic onboarding protocol is established that mandates revenue cycle workflow training for all new or acquired locations before go-live
- Epic registration workflow includes a pre-encounter eligibility verification step that flags incomplete or unconfirmed insurance fields and prevents encounter opening until resolved
- CO-16 denial rate at West Allis returns to system average within two billing cycles of training completion and workflow implementation

### 2B.6 Remediation Ownership

| Role | Owner | Responsibility |
|---|---|---|
| Primary | Patricia Nguyen | Training program design, standardized workflow rollout, onboarding protocol |
| Supporting | James Tirado | Epic registration workflow update, eligibility check integration |
| Approver | David Okafor | Budget approval for training program development if external resources required |

---

# Section 3: PR-96 -- Non-Covered Charge / Payer ID Mismatch

**Volume:** 19% of total denials
**Estimated Annual Impact:** ~$380K
**Primary Stakeholders:** Sandra Kim (Payer Contracting), James Tirado (IT Systems)

---

## 3.1 Observation

PR-96 denials are concentrated on Medicare Advantage claims across three specific payers: Humana Gold Plus, WellCare Alliant, and Anthem MedicarePreferred. The pattern emerged sharply at the start of Q1 2025 -- January 1, 2025, the effective date of renegotiated contracts for all three payers. Phase 2 SQL analysis validated Sandra Kim's hypothesis: PR-96 volume is heavily skewed toward these three Medicare Advantage plans, while commercial and Medicaid payers show no comparable spike. A secondary PR-96 driver -- non-covered procedure codes billed under WellCare Alliant -- was also identified.

---

## 3.2 5-Why Analysis

**Why 1: Why are PR-96 denials concentrated on Humana Gold Plus, WellCare Alliant, and Anthem MedicarePreferred beginning January 2025?**

Claims submitted to these three Medicare Advantage payers beginning January 2025 are failing payer ID validation or routing to incorrect contract terms -- causing payers to reject claims as non-covered or misrouted.

**Why 2: Why are claims failing payer ID validation or routing incorrectly?**

Waystar's payer configuration for all three Medicare Advantage plans was not updated to reflect the new payer IDs and contract terms effective January 1, 2025. Claims are being submitted using the prior payer IDs, which are either invalid under the renewed contracts or routing to superseded fee schedule terms.

**Why 3: Why was Waystar's payer configuration not updated before January 1, 2025?**

Sandra Kim's contracting team submitted payer ID update requests to James Tirado's IT team in December 2024, but the updates were not confirmed as loaded into Waystar before the January billing cycle opened. Specifically, the Humana Gold Plus payer ID format changed from a 5-digit to a 9-digit format -- a structural change requiring a configuration update, not just a value swap -- and this was not completed in time.

**Why 4: Why were the payer ID updates not confirmed as loaded before the billing cycle opened?**

There was no formal handoff or confirmation protocol between the Payer Contracting team and IT for payer configuration updates. Sandra Kim submitted the update requests via email; no ticketing system, deadline, or verification step existed to confirm that all three updates were completed and validated before claims began submitting under the new contract terms.

**Why 5: Why is there no formal handoff protocol between Payer Contracting and IT for payer configuration updates?**

Payer configuration management at Riverside is split across two teams -- contracting (Sandra Kim) owns the contract terms; IT (James Tirado) owns the Waystar configuration -- with no shared process, shared system, or shared accountability for ensuring configuration changes are completed before billing cycle go-live. Contract renewal timelines and billing system update timelines are managed independently with no integration or cross-functional checkpoint.

---

## 3.3 Root Cause Statement

The root cause of PR-96 denials is the absence of a formal payer configuration management process that connects contract renewal timelines to billing system update requirements with shared accountability and verification. Three Medicare Advantage contract renewals effective January 1, 2025 required Waystar payer ID configuration updates that were requested but not confirmed as completed before the billing cycle opened. Claims submitted under the new contract terms were rejected because Waystar was still routing them using prior-cycle payer IDs -- causing systematic PR-96 denials across all three plans from the first day of Q1 2025.

A secondary PR-96 driver -- two non-covered procedure codes (99417 and 99418, prolonged services) billed to WellCare Alliant after a provider began using them post-January -- is attributable to inadequate contract-level coverage validation at the point of charge capture and is noted as a contributing factor.

---

## 3.4 Current State -- Payer Configuration and Contract Management

- Payer contract terms are owned and maintained by Sandra Kim's Payer Contracting team
- Waystar payer configuration (payer IDs, fee schedules, contract effective dates) is maintained by James Tirado's IT team
- Payer ID update requests are submitted from Contracting to IT via email with no formal ticketing, deadline, or confirmation step
- No pre-billing cycle audit exists to verify that Waystar configuration matches current contract terms before a new billing period opens
- Non-covered procedure code restrictions from payer contracts are not systematically loaded into Waystar's charge capture or claim scrubbing rules -- providers may bill codes that are contractually excluded without a system-level warning
- PR-96 denials are worked reactively after payer rejection; payer configuration errors may persist across multiple billing cycles before being identified

---

## 3.5 Desired State -- Payer Configuration and Contract Management

- A formal payer configuration management workflow connects each contract renewal event to a required Waystar configuration update with a defined completion deadline, assigned owner, and verification step before the contract effective date
- A pre-billing cycle configuration audit is conducted before each quarter opens, confirming that all active payer IDs, fee schedules, and contract terms in Waystar match current executed contract terms
- Payer configuration update requests are tracked in a shared ticketing system visible to both the Contracting team and IT -- eliminating email-only handoffs
- Non-covered procedure code restrictions for each active payer contract are loaded into Waystar's claim scrubbing rules, generating a pre-submission flag when a provider bills a contractually excluded code
- Humana Gold Plus, WellCare Alliant, and Anthem MedicarePreferred payer ID configurations are corrected in Waystar immediately following RCA sign-off; Sandra Kim and James Tirado confirm all three are validated before the next billing cycle opens
- PR-96 denials attributable to payer ID mismatch drop to zero within one billing cycle of configuration correction

---

## 3.6 Remediation Ownership

| Role | Owner | Responsibility |
|---|---|---|
| Primary | Sandra Kim | Payer configuration update requests, contract coverage restriction documentation |
| Primary | James Tirado | Waystar payer ID updates, pre-billing cycle audit, ticketing system setup |
| Approver | Patricia Nguyen | Revenue cycle sign-off on configuration validation before billing cycle opens |

---

# Section 4: Cross-Cutting Observations

The following observations apply across all three denial drivers and should inform the BRD requirements and executive summary.

**1. No Pre-Submission Validation Layer**

All three denial drivers share a common gap: claims with detectable errors (missing NPI, modifier mismatch, wrong payer ID) are reaching payer submission without being caught. A pre-submission claim scrubbing layer in Waystar -- configured with rules for each root cause -- would convert reactive denial management into proactive denial prevention.

**2. Change Events Without Cross-Functional Checkpoints**

All three root causes were triggered or worsened by change events (CMS policy change, Waystar upgrade, contract renewals) that were managed in functional silos without cross-functional review. A lightweight cross-functional change review cadence -- quarterly at minimum -- would have caught each of these before they hit the billing cycle.

**3. Reactive Denial Management as Default**

Riverside's current revenue cycle operations are optimized for denial remediation (AR follow-up after rejection) rather than denial prevention (pre-submission validation and workflow controls). Shifting the operational model toward prevention -- through system-level validation, workflow guardrails, and proactive auditing -- is the structural change required to sustainably reduce the denial rate.

---

# Section 5: Projected Impact of Remediation

| Denial Code | Current Denial Rate Contribution | Projected Post-Remediation Contribution | Est. Recovery |
|---|---|---|---|
| CO-4 | 28% of denials | ~10% (residual modifier complexity) | ~$390K |
| CO-16 | 24% of denials | ~8% (residual registration variability) | ~$330K |
| PR-96 | 19% of denials | ~2% (configuration corrected) | ~$350K |
| **Total** | **71% of denials** | **~20% combined** | **~$1.07M** |

If remediation is fully implemented before Q4 2025 billing cycle, projected overall denial rate: **~8.3%** -- within the CFO target of 8.5%.

---
