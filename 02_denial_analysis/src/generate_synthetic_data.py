#!/usr/bin/env python3
"""
Generate synthetic Riverside Health System claims denial datasets.

Outputs under data/processed/:
  - quarterly_claims_summary.csv
  - riverside_denial_log.csv
  - analysis_constants.csv

Claim-level rows are synthetic and calibrated to CMS Medicare Physician & Other
Practitioners PUF 2024 (Wisconsin) allowed-amount benchmarks. Population
quarterly volumes are engagement-level inputs used to reproduce the documented
denial-rate trend (8.2% / 9.6% / 11.7%).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_DENIALS = 500
AVG_ALLOWED_AMOUNT = 79.73  # CMS PUF 2024 WI calibration constant
ANNUAL_CLAIMS = 680_000

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "data" / "processed"
RAW_CMS_SAMPLE = ROOT / "data" / "raw" / "cms_puf_wi_hcpcs_sample.csv"

QUARTERS = [
    {"Quarter": "Q3 2024", "Claims_Submitted": 168_000, "Denial_Rate_Target": 0.082},
    {"Quarter": "Q4 2024", "Claims_Submitted": 172_000, "Denial_Rate_Target": 0.096},
    {"Quarter": "Q1 2025", "Claims_Submitted": 171_000, "Denial_Rate_Target": 0.117},
]

DENIAL_CODES = {
    "CO-4": "Inconsistent modifier / procedure code",
    "CO-16": "Missing or incomplete claim information",
    "PR-96": "Non-covered charge / payer ID mismatch",
    "CO-29": "The time limit for filing has expired",
    "CO-50": "Non-covered services — not deemed medically necessary",
    "CO-97": "Benefit for this service is included in payment for another service",
    "PR-1": "Deductible amount",
    "OA-23": "Impact of prior payer adjudication",
}

CODE_TARGETS = {
    "CO-4": 0.28,
    "CO-16": 0.24,
    "PR-96": 0.19,
    "CO-29": 0.08,
    "CO-50": 0.07,
    "CO-97": 0.06,
    "PR-1": 0.05,
    "OA-23": 0.03,
}

PAYERS = [
    ("Humana Gold Plus", "Medicare Advantage"),
    ("WellCare Alliant", "Medicare Advantage"),
    ("Anthem MedicarePreferred", "Medicare Advantage"),
    ("UnitedHealthcare", "Commercial"),
    ("Blue Cross Blue Shield WI", "Commercial"),
    ("Aetna", "Commercial"),
    ("Wisconsin Medicaid", "Medicaid"),
    ("Medicare Part B", "Traditional Medicare"),
]

CLINICS = [
    "Downtown Milwaukee",
    "West Allis",
    "Southside",
    "Wauwatosa",
    "Brookfield",
]

# Fallback CMS-calibrated HCPCS pool if raw sample is absent
DEFAULT_HCPCS_POOL = [
    ("99213", "Office/outpatient visit est", 110.50, 79.20),
    ("99214", "Office/outpatient visit est", 165.00, 112.40),
    ("99215", "Office/outpatient visit est", 220.00, 158.10),
    ("97110", "Therapeutic exercises", 95.00, 68.40),
    ("97140", "Manual therapy", 88.00, 62.10),
    ("97530", "Therapeutic activities", 102.00, 73.50),
    ("70450", "CT head/brain w/o contrast", 285.00, 142.80),
    ("72148", "MRI lumbar spine w/o dye", 620.00, 298.40),
    ("73721", "MRI joint of lower extremity", 540.00, 265.00),
    ("93000", "Electrocardiogram complete", 55.00, 28.90),
]


def _allocate_counts(n: int, weights: dict[str, float]) -> dict[str, int]:
    keys = list(weights)
    raw = np.array([weights[k] for k in keys], dtype=float)
    raw = raw / raw.sum()
    counts = np.floor(raw * n).astype(int)
    remainder = n - int(counts.sum())
    frac = (raw * n) - counts
    order = np.argsort(-frac)
    for i in range(remainder):
        counts[order[i]] += 1
    return {keys[i]: int(counts[i]) for i in range(len(keys))}


def load_hcpcs_pool() -> list[tuple[str, str, float, float]]:
    if RAW_CMS_SAMPLE.exists():
        sample = pd.read_csv(RAW_CMS_SAMPLE)
        pool = []
        for _, row in sample.iterrows():
            pool.append(
                (
                    str(row["HCPCS_Code"]),
                    str(row["Procedure_Description"]),
                    float(row["Avg_Submitted_Charge"]),
                    float(row["Avg_Allowed_Amount"]),
                )
            )
        if pool:
            return pool
    return DEFAULT_HCPCS_POOL


def build_quarterly_summary() -> pd.DataFrame:
    rows = []
    for q in QUARTERS:
        submitted = q["Claims_Submitted"]
        denied = int(round(submitted * q["Denial_Rate_Target"]))
        rate = denied / submitted
        rows.append(
            {
                "Quarter": q["Quarter"],
                "Claims_Submitted": submitted,
                "Claims_Denied": denied,
                "Denial_Rate": round(rate, 4),
                "Denial_Rate_Pct": round(rate * 100, 1),
                "Avg_Allowed_Amount": AVG_ALLOWED_AMOUNT,
                "Revenue_at_Risk": round(denied * AVG_ALLOWED_AMOUNT, 2),
            }
        )
    return pd.DataFrame(rows)


def build_constants(quarterly: pd.DataFrame) -> pd.DataFrame:
    baseline_rate = quarterly.loc[
        quarterly["Quarter"] == "Q3 2024", "Denial_Rate"
    ].iloc[0]
    latest_rate = quarterly.loc[
        quarterly["Quarter"] == "Q1 2025", "Denial_Rate"
    ].iloc[0]
    incremental_annual = round(
        ANNUAL_CLAIMS * (latest_rate - baseline_rate) * AVG_ALLOWED_AMOUNT, 2
    )
    return pd.DataFrame(
        [
            {"Constant": "AVG_ALLOWED_AMOUNT", "Value": AVG_ALLOWED_AMOUNT},
            {"Constant": "ANNUAL_CLAIMS", "Value": ANNUAL_CLAIMS},
            {"Constant": "BASELINE_DENIAL_RATE", "Value": baseline_rate},
            {"Constant": "LATEST_DENIAL_RATE", "Value": latest_rate},
            {
                "Constant": "BASELINE_ANNUAL_REVENUE_AT_RISK",
                "Value": round(
                    ANNUAL_CLAIMS * baseline_rate * AVG_ALLOWED_AMOUNT, 2
                ),
            },
            {
                "Constant": "LATEST_ANNUAL_REVENUE_AT_RISK",
                "Value": round(
                    ANNUAL_CLAIMS * latest_rate * AVG_ALLOWED_AMOUNT, 2
                ),
            },
            {
                "Constant": "INCREMENTAL_ANNUAL_REVENUE_EXPOSURE",
                "Value": incremental_annual,
            },
            {"Constant": "DENIAL_LOG_ROW_COUNT", "Value": N_DENIALS},
            {"Constant": "RANDOM_SEED", "Value": SEED},
        ]
    )


def build_denial_log(rng: np.random.Generator) -> pd.DataFrame:
    hcpcs_pool = load_hcpcs_pool()
    code_counts = _allocate_counts(N_DENIALS, CODE_TARGETS)
    quarter_counts = _allocate_counts(
        N_DENIALS, {"Q3 2024": 0.26, "Q4 2024": 0.32, "Q1 2025": 0.42}
    )

    code_list: list[str] = []
    for code, n in code_counts.items():
        code_list.extend([code] * n)
    rng.shuffle(code_list)

    quarter_list: list[str] = []
    for q, n in quarter_counts.items():
        quarter_list.extend([q] * n)
    rng.shuffle(quarter_list)

    rows = []
    claim_id = 100000
    for i in range(N_DENIALS):
        code = code_list[i]
        quarter = quarter_list[i]
        hcpcs, desc, charge, allowed = hcpcs_pool[
            int(rng.integers(0, len(hcpcs_pool)))
        ]

        if code == "PR-96":
            payer_idx = int(rng.choice([0, 1, 2], p=[0.40, 0.30, 0.30]))
        elif code == "CO-16" and quarter in ("Q4 2024", "Q1 2025"):
            payer_idx = int(
                rng.choice(
                    [0, 1, 2, 3, 4, 5],
                    p=[0.18, 0.14, 0.14, 0.20, 0.18, 0.16],
                )
            )
        else:
            payer_idx = int(rng.integers(0, len(PAYERS)))
        payer_name, payer_type = PAYERS[payer_idx]

        if code in ("CO-4", "CO-16"):
            clinic = str(
                rng.choice(CLINICS, p=[0.28, 0.30, 0.18, 0.12, 0.12])
            )
        else:
            clinic = str(
                rng.choice(CLINICS, p=[0.34, 0.16, 0.18, 0.16, 0.16])
            )

        charge_n = round(float(charge * rng.uniform(0.92, 1.08)), 2)
        allowed_n = round(float(allowed * rng.uniform(0.95, 1.05)), 2)

        if hcpcs.startswith("992"):
            service_line = "E&M"
        elif hcpcs.startswith("97"):
            service_line = "Physical Therapy"
        elif hcpcs.startswith(("70", "72", "73")):
            service_line = "Radiology"
        else:
            service_line = "Other"

        rows.append(
            {
                "Claim_ID": f"RHS-{claim_id + i}",
                "Quarter": quarter,
                "Denial_Code": code,
                "Denial_Description": DENIAL_CODES[code],
                "Payer_Name": payer_name,
                "Payer_Type": payer_type,
                "Clinic_Location": clinic,
                "HCPCS_Code": hcpcs,
                "Procedure_Description": desc,
                "Submitted_Charge": charge_n,
                "Allowed_Amount": allowed_n,
                "Service_Line": service_line,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(["Quarter", "Denial_Code", "Claim_ID"])
        .reset_index(drop=True)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out: Path = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(SEED)
    quarterly = build_quarterly_summary()
    constants = build_constants(quarterly)
    denial_log = build_denial_log(rng)

    quarterly.to_csv(out / "quarterly_claims_summary.csv", index=False)
    constants.to_csv(out / "analysis_constants.csv", index=False)
    denial_log.to_csv(out / "riverside_denial_log.csv", index=False)

    print("Wrote:", out / "quarterly_claims_summary.csv")
    print(quarterly.to_string(index=False))
    print("Wrote:", out / "analysis_constants.csv")
    print(constants.to_string(index=False))
    print("Wrote:", out / "riverside_denial_log.csv", f"({len(denial_log)} rows)")
    share = (
        denial_log["Denial_Code"]
        .value_counts(normalize=True)
        .rename("Share")
        .mul(100)
        .round(1)
    )
    print(share.to_string())
    print(f"Top 3 share: {share.loc[['CO-4', 'CO-16', 'PR-96']].sum():.1f}%")


if __name__ == "__main__":
    main()
