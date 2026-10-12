# Power BI DAX Measures

Model sources (Import mode):

- `data/processed/quarterly_claims_summary.csv`
- `data/processed/riverside_denial_log.csv`
- `data/processed/analysis_constants.csv`

All dollar measures use the CMS-calibrated allowed amount **$79.73** from `analysis_constants[AVG_ALLOWED_AMOUNT]` (or the `Avg_Allowed_Amount` column on the quarterly table). Values below match `02_denial_analysis/sql/05_revenue_at_risk.sql`.

## Measures

```dax
Denial Rate % =
DIVIDE(
    SUM ( quarterly_claims_summary[Claims_Denied] ),
    SUM ( quarterly_claims_summary[Claims_Submitted] )
)

Revenue at Risk =
SUMX (
    quarterly_claims_summary,
    quarterly_claims_summary[Claims_Denied] * quarterly_claims_summary[Avg_Allowed_Amount]
)

Avg Allowed Amount =
LOOKUPVALUE (
    analysis_constants[Value],
    analysis_constants[Constant], "AVG_ALLOWED_AMOUNT"
)

Baseline Denial Rate =
LOOKUPVALUE (
    analysis_constants[Value],
    analysis_constants[Constant], "BASELINE_DENIAL_RATE"
)

Latest Denial Rate =
LOOKUPVALUE (
    analysis_constants[Value],
    analysis_constants[Constant], "LATEST_DENIAL_RATE"
)

Annual Claims =
LOOKUPVALUE (
    analysis_constants[Value],
    analysis_constants[Constant], "ANNUAL_CLAIMS"
)

Incremental Annual Revenue Exposure =
[Annual Claims] * ( [Latest Denial Rate] - [Baseline Denial Rate] ) * [Avg Allowed Amount]

Top Code Share % =
DIVIDE (
    COUNTROWS ( riverside_denial_log ),
    CALCULATE ( COUNTROWS ( riverside_denial_log ), ALL ( riverside_denial_log[Denial_Code] ) )
)

Est Impact Top Code =
VAR Q1RAR =
    CALCULATE (
        [Revenue at Risk],
        quarterly_claims_summary[Quarter] = "Q1 2025"
    )
RETURN
    Q1RAR * [Top Code Share %]
```

## Verified outputs (from SQL / notebook)

| Measure | Value | Source |
|---|---|---|
| Q3 2024 Denial Rate % | 8.2% | `01_denial_rate_by_quarter.sql` |
| Q4 2024 Denial Rate % | 9.6% | same |
| Q1 2025 Denial Rate % | 11.7% | same |
| Q3 Revenue at Risk | $1,098,360.48 | `05_revenue_at_risk.sql` 5A |
| Q4 Revenue at Risk | $1,316,501.76 | same |
| Q1 Revenue at Risk | $1,595,158.11 | same |
| Incremental Annual Revenue Exposure | $1,897,574.00 | `05_revenue_at_risk.sql` 5B (RECONCILED) |
| CO-4 Est Impact | $446,644.27 | `05_revenue_at_risk.sql` 5C |
| CO-16 Est Impact | $382,837.95 | same |
| PR-96 Est Impact | $303,080.04 | same |

## Screenshots

See `07_power_bi_dashboard/screenshots/` for chart exports generated from the same processed datasets.

## `.pbix` package note

`denial_dashboard.pbix` is a portable zip package with rebuild instructions (`README.txt` inside the archive). Open Power BI Desktop, import the three `data/processed/*.csv` files, paste the measures above, and recreate visuals to match `screenshots/`. Verified dollar/rate values must match this file and `05_revenue_at_risk.sql` — do not hard-code alternate figures.
