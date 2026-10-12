"""ETL: simulate enterprise hospital claims and land raw CSV.

Generates ~12,500 synthetic claims calibrated to realistic RCM denial patterns.
**Claim-level data is synthetic** — no PHI.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.carc_taxonomy import CARC_TO_CATEGORY, RARC_BY_CARC
from src.schema import PAYERS, coerce_schema

SEED = 42
N_CLAIMS = 12_500
DEFAULT_RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw_claims.csv"

# Target denial rates by payer (Medicare FFS near 10.8% industry benchmark).
PAYER_DENIAL_RATES: dict[str, float] = {
    "Medicare FFS": 0.108,
    "Medicaid": 0.142,
    "BCBS": 0.125,
    "UnitedHealthcare": 0.158,
    "Aetna": 0.136,
}

PAYER_WEIGHTS = np.array([0.28, 0.18, 0.22, 0.18, 0.14])

# CARC mix among denied claims (must sum ≈ 1).
DENIED_CARC_WEIGHTS = {
    "CO-16": 0.28,
    "CO-18": 0.08,
    "CO-27": 0.12,
    "CO-50": 0.22,
    "CO-97": 0.18,
    "PR-1": 0.12,
}

# Category overrides for Prior Authorization / Timely Filing narrative coverage.
CATEGORY_OVERRIDE_PROBS = {
    "Prior Authorization": 0.14,  # re-label a slice of medical necessity / coding
    "Timely Filing": 0.06,  # re-label a slice of eligibility
}


def _assign_denial_category(carc: str, rng: np.random.Generator) -> str:
    base = CARC_TO_CATEGORY[carc]
    draw = rng.random()
    if base == "Medical Necessity" and draw < CATEGORY_OVERRIDE_PROBS["Prior Authorization"]:
        return "Prior Authorization"
    if base == "Coding & Billing" and draw < CATEGORY_OVERRIDE_PROBS["Prior Authorization"] * 0.5:
        return "Prior Authorization"
    if base == "Eligibility/Coverage" and draw < CATEGORY_OVERRIDE_PROBS["Timely Filing"]:
        return "Timely Filing"
    if carc == "CO-16" and draw > 0.85:
        return "Timely Filing"
    return base


def generate_claims(n_claims: int = N_CLAIMS, seed: int = SEED) -> pd.DataFrame:
    """Simulate an enterprise hospital claims extract."""
    rng = np.random.default_rng(seed)

    payers = rng.choice(list(PAYERS), size=n_claims, p=PAYER_WEIGHTS)
    claim_ids = [f"CLM-{seed:04d}-{i:06d}" for i in range(1, n_claims + 1)]
    patient_ids = [f"SYN-PT-{rng.integers(100000, 999999)}" for _ in range(n_claims)]

    # Service dates across a trailing 12-month window.
    start = np.datetime64("2024-10-01")
    day_offsets = rng.integers(0, 365, size=n_claims)
    service_dates = start + day_offsets.astype("timedelta64[D]")

    # Claim amounts: log-normal around hospital outpatient / professional mix.
    claim_amounts = np.round(rng.lognormal(mean=6.8, sigma=0.85, size=n_claims), 2)
    claim_amounts = np.clip(claim_amounts, 85.0, 85_000.0)

    # Documentation completeness — slightly left-skewed toward higher quality.
    doc_scores = np.clip(rng.beta(5.5, 2.2, size=n_claims), 0.05, 1.0)
    doc_scores = np.round(doc_scores, 3)

    # Denial flags driven by payer-specific rates + documentation risk.
    denial_flags = np.zeros(n_claims, dtype=bool)
    for payer, rate in PAYER_DENIAL_RATES.items():
        mask = payers == payer
        idx = np.where(mask)[0]
        # Lower documentation → higher denial probability.
        base = rate * (1.15 - 0.30 * doc_scores[idx])
        probs = np.clip(base, 0.04, 0.35)
        denial_flags[idx] = rng.random(len(idx)) < probs

    claim_status = np.where(denial_flags, "Denied", "Paid")

    carc_codes = np.full(n_claims, "", dtype=object)
    rarc_codes = np.full(n_claims, "", dtype=object)
    denial_categories = np.full(n_claims, "", dtype=object)
    appeal_status = np.full(n_claims, "Not Appealed", dtype=object)

    denied_idx = np.where(denial_flags)[0]
    carc_list = list(DENIED_CARC_WEIGHTS.keys())
    carc_probs = np.array(list(DENIED_CARC_WEIGHTS.values()))
    carc_probs = carc_probs / carc_probs.sum()

    chosen_carcs = rng.choice(carc_list, size=len(denied_idx), p=carc_probs)
    for i, carc in zip(denied_idx, chosen_carcs):
        carc_codes[i] = carc
        rarc_codes[i] = RARC_BY_CARC[carc][0]
        denial_categories[i] = _assign_denial_category(carc, rng)

        # Appeal propensity rises with amount and documentation quality;
        # PR-1 / duplicates rarely appealed.
        severity_penalty = {"PR-1": 0.15, "CO-18": 0.25, "CO-27": 0.35}.get(carc, 0.70)
        appeal_prob = severity_penalty * (
            0.35 + 0.40 * doc_scores[i] + 0.15 * min(claim_amounts[i] / 5000.0, 1.0)
        )
        if rng.random() < np.clip(appeal_prob, 0.08, 0.85):
            # Overturn odds rise with documentation and fall with severity.
            # Stronger feature→label coupling supports a realistic but learnable model.
            overturn_base = {
                "CO-16": 0.68,
                "CO-18": 0.10,
                "CO-27": 0.16,
                "CO-50": 0.52,
                "CO-97": 0.45,
                "PR-1": 0.06,
            }[carc]
            amount_boost = 0.08 * min(claim_amounts[i] / 8000.0, 1.0)
            overturn_p = np.clip(
                overturn_base * (0.35 + 1.05 * doc_scores[i]) + amount_boost,
                0.02,
                0.95,
            )
            # Commercial payers slightly harder; Medicare FFS slightly easier.
            if payers[i] in ("UnitedHealthcare", "Aetna"):
                overturn_p *= 0.82
            elif payers[i] == "Medicare FFS":
                overturn_p *= 1.12
            elif payers[i] == "Medicaid":
                overturn_p *= 0.92
            appeal_status[i] = (
                "Overturned/Recovered" if rng.random() < overturn_p else "Upheld"
            )

    # Paid claims: blank denial fields.
    paid_idx = np.where(~denial_flags)[0]
    carc_codes[paid_idx] = ""
    rarc_codes[paid_idx] = ""
    denial_categories[paid_idx] = ""
    appeal_status[paid_idx] = "Not Appealed"

    df = pd.DataFrame(
        {
            "claim_id": claim_ids,
            "patient_id": patient_ids,
            "service_date": service_dates,
            "claim_amount": claim_amounts,
            "payer_name": payers,
            "carc_code": carc_codes,
            "rarc_code": rarc_codes,
            "denial_category": denial_categories,
            "claim_status": claim_status,
            "documentation_completeness_score": doc_scores,
            "appeal_status": appeal_status,
        }
    )
    return coerce_schema(df)


def run_etl(output_path: Path | str | None = None, n_claims: int = N_CLAIMS) -> pd.DataFrame:
    """Generate claims and write ``data/raw_claims.csv``."""
    path = Path(output_path) if output_path else DEFAULT_RAW_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_claims(n_claims=n_claims)
    # Serialize dates as ISO strings for CSV portability.
    export = df.copy()
    export["service_date"] = export["service_date"].dt.strftime("%Y-%m-%d")
    export.to_csv(path, index=False)
    return df


if __name__ == "__main__":
    frame = run_etl()
    denied = (frame["claim_status"] == "Denied").sum()
    print(f"Wrote {len(frame):,} claims ({denied:,} denied) → {DEFAULT_RAW_PATH}")
