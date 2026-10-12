"""Validation and HIPAA-oriented sanitization for synthetic claims extracts."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.schema import (
    APPEAL_STATUSES,
    CARC_CODES,
    CLAIM_STATUSES,
    DENIAL_CATEGORIES,
    PAYERS,
    REQUIRED_COLUMNS,
    coerce_schema,
)

# Patterns that must never appear in a sanitized extract.
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
_MRN_RE = re.compile(r"\b(?:MRN|SSN|DOB)[:\s=]", re.IGNORECASE)


@dataclass
class ValidationReport:
    """Structured result of schema + PHI checks."""

    is_valid: bool
    row_count: int
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sanitization_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "row_count": self.row_count,
            "issues": self.issues,
            "warnings": self.warnings,
            "sanitization_actions": self.sanitization_actions,
        }


def _scan_phi_strings(series: pd.Series) -> list[str]:
    hits: list[str] = []
    sample = series.dropna().astype(str).head(5000)
    for val in sample:
        if _SSN_RE.search(val):
            hits.append("SSN-like pattern detected")
        if _EMAIL_RE.search(val):
            hits.append("Email address detected")
        if _PHONE_RE.search(val):
            hits.append("Phone number detected")
        if _MRN_RE.search(val):
            hits.append("MRN/SSN/DOB label detected")
    return sorted(set(hits))


def sanitize_for_hipaa(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Hash patient identifiers and strip accidental PHI-like tokens.

    Patient IDs are already synthetic (``SYN-PT-*``); we re-hash them to a
    stable, non-reversible token so downstream artifacts never carry raw IDs.
    """
    out = df.copy()
    actions: list[str] = []

    def _hash_pid(pid: str) -> str:
        digest = hashlib.sha256(f"rcm-synth|{pid}".encode("utf-8")).hexdigest()[:12]
        return f"HPT-{digest.upper()}"

    if "patient_id" in out.columns:
        out["patient_id"] = out["patient_id"].astype(str).map(_hash_pid)
        actions.append("Hashed patient_id → HPT-<sha256-12> (synthetic, non-PHI)")

    # Blank any free-text cells that look like contact info (defensive).
    for col in out.select_dtypes(include=["object", "string"]).columns:
        if col == "patient_id":
            continue
        series = out[col].astype(str)
        mask = series.map(
            lambda v: bool(_SSN_RE.search(v) or _EMAIL_RE.search(v) or _PHONE_RE.search(v))
        )
        if mask.any():
            out.loc[mask, col] = ""
            actions.append(f"Cleared PHI-like tokens in column '{col}' ({int(mask.sum())} rows)")

    return out, actions


def validate_claims(df: pd.DataFrame) -> ValidationReport:
    """Validate schema, domain values, and cross-field business rules."""
    issues: list[str] = []
    warnings: list[str] = []

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return ValidationReport(
            is_valid=False,
            row_count=len(df),
            issues=[f"Missing columns: {missing}"],
        )

    work = coerce_schema(df)

    if work["claim_id"].duplicated().any():
        issues.append("Duplicate claim_id values found")
    if work["claim_id"].isna().any():
        issues.append("Null claim_id values found")

    if (work["claim_amount"] <= 0).any() or work["claim_amount"].isna().any():
        issues.append("claim_amount must be positive and non-null")

    score = work["documentation_completeness_score"]
    if score.isna().any() or (score < 0).any() or (score > 1).any():
        issues.append("documentation_completeness_score must be in [0.0, 1.0]")

    bad_payers = set(work["payer_name"].dropna().unique()) - set(PAYERS)
    if bad_payers:
        issues.append(f"Unexpected payer_name values: {sorted(bad_payers)}")

    bad_status = set(work["claim_status"].dropna().unique()) - set(CLAIM_STATUSES)
    if bad_status:
        issues.append(f"Unexpected claim_status values: {sorted(bad_status)}")

    bad_appeal = set(work["appeal_status"].dropna().unique()) - set(APPEAL_STATUSES)
    if bad_appeal:
        issues.append(f"Unexpected appeal_status values: {sorted(bad_appeal)}")

    denied = work["claim_status"] == "Denied"
    paid = work["claim_status"] == "Paid"

    denied_missing_carc = denied & (work["carc_code"].fillna("") == "")
    if denied_missing_carc.any():
        issues.append(f"Denied claims missing carc_code: {int(denied_missing_carc.sum())}")

    denied_bad_carc = denied & ~work["carc_code"].isin(CARC_CODES)
    # Empty already caught above; only flag non-empty invalids
    denied_bad_carc = denied & work["carc_code"].fillna("").ne("") & ~work["carc_code"].isin(
        CARC_CODES
    )
    if denied_bad_carc.any():
        issues.append(f"Denied claims with invalid carc_code: {int(denied_bad_carc.sum())}")

    denied_bad_cat = denied & ~work["denial_category"].isin(DENIAL_CATEGORIES)
    if denied_bad_cat.any():
        issues.append(
            f"Denied claims with invalid denial_category: {int(denied_bad_cat.sum())}"
        )

    paid_with_denial = paid & work["carc_code"].fillna("").ne("")
    if paid_with_denial.any():
        warnings.append(
            f"Paid claims unexpectedly have carc_code populated: {int(paid_with_denial.sum())}"
        )

    paid_appealed = paid & work["appeal_status"].isin(
        ["Overturned/Recovered", "Upheld"]
    )
    if paid_appealed.any():
        issues.append("Paid claims must not have appeal outcomes")

    # PHI scan on string columns.
    for col in ("claim_id", "patient_id", "payer_name", "rarc_code"):
        phi_hits = _scan_phi_strings(work[col])
        for hit in phi_hits:
            issues.append(f"PHI risk in {col}: {hit}")

    if len(work) < 10_000:
        warnings.append(f"Row count {len(work):,} is below enterprise target (~12,500)")

    return ValidationReport(
        is_valid=len(issues) == 0,
        row_count=len(work),
        issues=issues,
        warnings=warnings,
    )


def validate_and_sanitize(df: pd.DataFrame) -> tuple[pd.DataFrame, ValidationReport]:
    """Sanitize first, then validate the sanitized frame."""
    cleaned, actions = sanitize_for_hipaa(df)
    report = validate_claims(cleaned)
    report.sanitization_actions = actions
    return cleaned, report
