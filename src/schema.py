"""Canonical schema for enterprise claims denial analytics.

All claim-level fields are synthetic. Column contract is enforced by the ETL
pipeline and ``data_validator``.
"""

from __future__ import annotations

from typing import Final

import pandas as pd

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

PAYERS: Final[tuple[str, ...]] = (
    "Medicare FFS",
    "Medicaid",
    "BCBS",
    "UnitedHealthcare",
    "Aetna",
)

CARC_CODES: Final[tuple[str, ...]] = (
    "CO-16",
    "CO-18",
    "CO-27",
    "CO-50",
    "CO-97",
    "PR-1",
)

DENIAL_CATEGORIES: Final[tuple[str, ...]] = (
    "Prior Authorization",
    "Medical Necessity",
    "Eligibility/Coverage",
    "Timely Filing",
    "Coding & Billing",
)

CLAIM_STATUSES: Final[tuple[str, ...]] = ("Paid", "Denied")

APPEAL_STATUSES: Final[tuple[str, ...]] = (
    "Overturned/Recovered",
    "Upheld",
    "Not Appealed",
)

# Medicare Fee-for-Service industry denial-rate benchmark used for variance.
MEDICARE_FFS_DENIAL_BENCHMARK: Final[float] = 0.108

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "claim_id",
    "patient_id",
    "service_date",
    "claim_amount",
    "payer_name",
    "carc_code",
    "rarc_code",
    "denial_category",
    "claim_status",
    "documentation_completeness_score",
    "appeal_status",
)

COLUMN_DTYPES: Final[dict[str, str]] = {
    "claim_id": "string",
    "patient_id": "string",
    "service_date": "datetime64[ns]",
    "claim_amount": "float64",
    "payer_name": "string",
    "carc_code": "string",
    "rarc_code": "string",
    "denial_category": "string",
    "claim_status": "string",
    "documentation_completeness_score": "float64",
    "appeal_status": "string",
}


def empty_claims_frame() -> pd.DataFrame:
    """Return an empty DataFrame with the canonical claims schema."""
    return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in COLUMN_DTYPES.items()})


def coerce_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns to the canonical schema and order them."""
    out = df.copy()
    missing = [c for c in REQUIRED_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = out[list(REQUIRED_COLUMNS)].copy()
    out["service_date"] = pd.to_datetime(out["service_date"], errors="coerce")
    out["claim_amount"] = pd.to_numeric(out["claim_amount"], errors="coerce")
    out["documentation_completeness_score"] = pd.to_numeric(
        out["documentation_completeness_score"], errors="coerce"
    )
    for col in (
        "claim_id",
        "patient_id",
        "payer_name",
        "carc_code",
        "rarc_code",
        "denial_category",
        "claim_status",
        "appeal_status",
    ):
        out[col] = out[col].astype("string")
    return out
