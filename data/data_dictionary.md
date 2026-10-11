# Data Dictionary

**Claim-level data is synthetic**, calibrated to CMS Medicare Physician & Other Practitioners PUF 2024 (Wisconsin) allowed-amount benchmarks. Population quarterly volumes are engagement inputs used to reproduce the documented denial-rate trend.

## `data/raw/`

| File | Description |
|---|---|
| `CMS_PUF_DOWNLOAD.md` | Link and notes for the official CMS PUF download |
| `cms_puf_wi_hcpcs_sample.csv` | Filtered WI HCPCS anchors used by the generator |

### `cms_puf_wi_hcpcs_sample.csv`

| Column | Type | Description |
|---|---|---|
| HCPCS_Code | string | Procedure code |
| Procedure_Description | string | Short CMS-style description |
| Code_Family | string | E&M / Physical Therapy / Radiology / Other |
| Avg_Submitted_Charge | float | Calibration anchor for submitted charge |
| Avg_Allowed_Amount | float | Calibration anchor for allowed amount |
| State | string | WI |
| Source_Note | string | Provenance note |

## `data/processed/quarterly_claims_summary.csv`

| Column | Type | Description |
|---|---|---|
| Quarter | string | `Q3 2024`, `Q4 2024`, `Q1 2025` |
| Claims_Submitted | integer | Population claims submitted |
| Claims_Denied | integer | `round(submitted × target rate)` |
| Denial_Rate | float | Denied ÷ submitted |
| Denial_Rate_Pct | float | Denial rate × 100 (1 decimal) |
| Avg_Allowed_Amount | float | CMS-calibrated constant ($79.73) |
| Revenue_at_Risk | float | `Claims_Denied × Avg_Allowed_Amount` |

## `data/processed/analysis_constants.csv`

| Constant | Meaning |
|---|---|
| AVG_ALLOWED_AMOUNT | $79.73 |
| ANNUAL_CLAIMS | 680,000 |
| BASELINE_DENIAL_RATE | Q3 2024 rate |
| LATEST_DENIAL_RATE | Q1 2025 rate |
| BASELINE_ANNUAL_REVENUE_AT_RISK | Annual RAR at baseline rate |
| LATEST_ANNUAL_REVENUE_AT_RISK | Annual RAR at latest rate |
| INCREMENTAL_ANNUAL_REVENUE_EXPOSURE | Headline: latest − baseline annual RAR |
| DENIAL_LOG_ROW_COUNT | 500 |
| RANDOM_SEED | 42 |

## `data/processed/riverside_denial_log.csv`

500 synthetic denied-claim rows for profiling.

| Column | Type | Description |
|---|---|---|
| Claim_ID | string | Synthetic id (`RHS-######`) |
| Quarter | string | Denial quarter |
| Denial_Code | string | ANSI CARC code |
| Denial_Description | string | Reason text |
| Payer_Name | string | Synthetic payer |
| Payer_Type | string | MA / Commercial / Medicaid / Traditional Medicare |
| Clinic_Location | string | Synthetic clinic |
| HCPCS_Code | string | From CMS sample pool |
| Procedure_Description | string | Procedure text |
| Submitted_Charge | float | Synthetic charge near CMS anchor |
| Allowed_Amount | float | Synthetic allowed near CMS anchor |
| Service_Line | string | Derived service line |

## Regeneration

```bash
python 02_denial_analysis/src/generate_synthetic_data.py
```
