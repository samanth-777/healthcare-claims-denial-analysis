"""CARC / RARC taxonomy and severity scoring for denial root-cause analytics."""

from __future__ import annotations

from typing import Final

import pandas as pd

# Official ANSI CARC descriptions (subset used in this project).
CARC_DEFINITIONS: Final[dict[str, str]] = {
    "CO-16": "Claim/service lacks information or has submission/billing error(s)",
    "CO-18": "Exact duplicate claim/service",
    "CO-27": "Expenses incurred after coverage terminated",
    "CO-50": "These are non-covered services because this is not deemed a "
    "'medical necessity' by the payer",
    "CO-97": "The benefit for this service is included in the payment/"
    "allowance for another service/procedure that has already been adjudicated",
    "PR-1": "Deductible amount",
}

# Remark Adjustment Reason Codes paired to each CARC for narrative context.
RARC_BY_CARC: Final[dict[str, tuple[str, str]]] = {
    "CO-16": ("N29", "Missing documentation/notes for this service"),
    "CO-18": ("N111", "No appeal right because the claim was a duplicate"),
    "CO-27": ("N30", "Patient ineligible for this service on the date of service"),
    "CO-50": ("N115", "This decision was based on a Local Coverage Determination"),
    "CO-97": ("N19", "Procedure code incidental to primary procedure"),
    "PR-1": ("N130", "Consult plan benefit documents for deductible details"),
}

# Map CARC → denial root-cause category used in executive reporting.
CARC_TO_CATEGORY: Final[dict[str, str]] = {
    "CO-16": "Coding & Billing",
    "CO-18": "Coding & Billing",
    "CO-27": "Eligibility/Coverage",
    "CO-50": "Medical Necessity",
    "CO-97": "Coding & Billing",
    "PR-1": "Eligibility/Coverage",
}

# Prior-auth denials are simulated via CO-50 / CO-16 mix with category override.
# Severity (1–5) informs ML feature engineering — higher = harder to overturn.
CARC_SEVERITY: Final[dict[str, int]] = {
    "CO-16": 2,  # documentation / info gaps — often recoverable
    "CO-18": 4,  # duplicates — low overturn odds
    "CO-27": 4,  # coverage terminated — low overturn odds
    "CO-50": 3,  # medical necessity — recoverable with clinical docs
    "CO-97": 3,  # bundling — moderate with coding review
    "PR-1": 5,  # patient responsibility — not typically recoverable via appeal
}

# Recoverability weight (0–1) used for recoverable-revenue estimates.
CARC_RECOVERABILITY: Final[dict[str, float]] = {
    "CO-16": 0.72,
    "CO-18": 0.15,
    "CO-27": 0.18,
    "CO-50": 0.55,
    "CO-97": 0.48,
    "PR-1": 0.05,
}


def taxonomy_frame() -> pd.DataFrame:
    """Return a tidy taxonomy table for Excel export / documentation."""
    rows = []
    for carc, definition in CARC_DEFINITIONS.items():
        rarc, rarc_desc = RARC_BY_CARC[carc]
        rows.append(
            {
                "carc_code": carc,
                "carc_definition": definition,
                "rarc_code": rarc,
                "rarc_description": rarc_desc,
                "default_denial_category": CARC_TO_CATEGORY[carc],
                "severity_score": CARC_SEVERITY[carc],
                "recoverability_weight": CARC_RECOVERABILITY[carc],
            }
        )
    return pd.DataFrame(rows)


def enrich_with_taxonomy(df: pd.DataFrame) -> pd.DataFrame:
    """Attach severity and recoverability columns from CARC taxonomy."""
    out = df.copy()
    out["carc_severity"] = out["carc_code"].map(CARC_SEVERITY).fillna(3).astype(int)
    out["recoverability_weight"] = (
        out["carc_code"].map(CARC_RECOVERABILITY).fillna(0.3).astype(float)
    )
    out["carc_definition"] = out["carc_code"].map(CARC_DEFINITIONS)
    return out
