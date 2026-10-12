"""RCM financial & performance analytics and executive exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.carc_taxonomy import enrich_with_taxonomy, taxonomy_frame
from src.payer_variance import medicare_ffs_observed_rate, payer_denial_summary
from src.schema import MEDICARE_FFS_DENIAL_BENCHMARK

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"


def compute_executive_kpis(df: pd.DataFrame) -> dict[str, float | int | str]:
    """Core portfolio KPIs for the executive summary."""
    n = len(df)
    denied_mask = df["claim_status"] == "Denied"
    denied = df.loc[denied_mask]
    paid = df.loc[~denied_mask]

    gross_denial_rate = float(denied_mask.mean())
    # Initial Clean Claim Rate = share of claims paid on first adjudication.
    initial_clean_claim_rate = float((~denied_mask).mean())

    total_billed = float(df["claim_amount"].sum())
    denied_revenue = float(denied["claim_amount"].sum()) if len(denied) else 0.0
    paid_revenue = float(paid["claim_amount"].sum()) if len(paid) else 0.0

    appealed = denied[denied["appeal_status"].isin(["Overturned/Recovered", "Upheld"])]
    overturned = denied[denied["appeal_status"] == "Overturned/Recovered"]
    recovered_revenue = float(overturned["claim_amount"].sum()) if len(overturned) else 0.0

    # Recoverable revenue by root cause (taxonomy weight × denied $).
    enriched = enrich_with_taxonomy(denied) if len(denied) else denied
    if len(enriched):
        enriched = enriched.copy()
        enriched["estimated_recoverable"] = (
            enriched["claim_amount"] * enriched["recoverability_weight"]
        )
        recoverable_total = float(enriched["estimated_recoverable"].sum())
    else:
        recoverable_total = 0.0

    return {
        "total_claims": int(n),
        "denied_claims": int(denied_mask.sum()),
        "paid_claims": int((~denied_mask).sum()),
        "gross_denial_rate": round(gross_denial_rate, 6),
        "gross_denial_rate_pct": round(gross_denial_rate * 100, 2),
        "initial_clean_claim_rate": round(initial_clean_claim_rate, 6),
        "initial_clean_claim_rate_pct": round(initial_clean_claim_rate * 100, 2),
        "total_billed_amount": round(total_billed, 2),
        "denied_revenue": round(denied_revenue, 2),
        "paid_revenue": round(paid_revenue, 2),
        "appealed_claims": int(len(appealed)),
        "overturned_claims": int(len(overturned)),
        "appeal_overturn_rate_pct": round(
            (len(overturned) / len(appealed) * 100) if len(appealed) else 0.0, 2
        ),
        "recovered_revenue_actual": round(recovered_revenue, 2),
        "estimated_recoverable_revenue": round(recoverable_total, 2),
        "medicare_ffs_benchmark_pct": round(MEDICARE_FFS_DENIAL_BENCHMARK * 100, 2),
        "medicare_ffs_observed_denial_rate_pct": round(
            medicare_ffs_observed_rate(df) * 100, 2
        ),
    }


def recoverable_by_root_cause(df: pd.DataFrame) -> pd.DataFrame:
    """Denied revenue and estimated recoverable $ by denial_category / CARC."""
    denied = df[df["claim_status"] == "Denied"].copy()
    if denied.empty:
        return pd.DataFrame(
            columns=[
                "denial_category",
                "carc_code",
                "denied_claims",
                "denied_revenue",
                "recoverability_weight",
                "estimated_recoverable_revenue",
            ]
        )
    denied = enrich_with_taxonomy(denied)
    denied["estimated_recoverable_revenue"] = (
        denied["claim_amount"] * denied["recoverability_weight"]
    )
    out = (
        denied.groupby(["denial_category", "carc_code"], dropna=False)
        .agg(
            denied_claims=("claim_id", "count"),
            denied_revenue=("claim_amount", "sum"),
            recoverability_weight=("recoverability_weight", "first"),
            estimated_recoverable_revenue=("estimated_recoverable_revenue", "sum"),
        )
        .reset_index()
        .sort_values("denied_revenue", ascending=False)
    )
    for col in ("denied_revenue", "estimated_recoverable_revenue"):
        out[col] = out[col].round(2)
    return out


def carc_pareto(df: pd.DataFrame) -> pd.DataFrame:
    """CARC volume/revenue Pareto table for denied claims."""
    denied = df[df["claim_status"] == "Denied"]
    if denied.empty:
        return pd.DataFrame()
    g = (
        denied.groupby(["carc_code", "rarc_code", "denial_category"], dropna=False)
        .agg(denial_count=("claim_id", "count"), denied_revenue=("claim_amount", "sum"))
        .reset_index()
        .sort_values("denied_revenue", ascending=False)
    )
    g["pct_of_denied_revenue"] = (
        g["denied_revenue"] / g["denied_revenue"].sum() * 100
    ).round(2)
    g["cumulative_pct"] = g["pct_of_denied_revenue"].cumsum().round(2)
    g["denied_revenue"] = g["denied_revenue"].round(2)
    return g


def kpi_summary_frame(kpis: dict) -> pd.DataFrame:
    """Long-form KPI table for CSV export."""
    rows = [{"metric": k, "value": v} for k, v in kpis.items()]
    return pd.DataFrame(rows)


def export_rcm_outputs(
    df: pd.DataFrame,
    output_dir: Path | str | None = None,
) -> tuple[dict[str, float | int | str], dict[str, Path]]:
    """Write KPI CSV and multi-tab executive Excel workbook.

    Returns ``(kpis, paths)``.
    """
    out = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    kpis = compute_executive_kpis(df)
    kpi_df = kpi_summary_frame(kpis)
    payer_df = payer_denial_summary(df)
    root_cause_df = recoverable_by_root_cause(df)
    pareto_df = carc_pareto(df)
    taxonomy = taxonomy_frame()

    kpi_csv = out / "claims_denial_kpi_summary.csv"
    xlsx_path = out / "rcm_executive_metrics.xlsx"

    kpi_df.to_csv(kpi_csv, index=False)

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        kpi_df.to_excel(writer, sheet_name="Executive_KPIs", index=False)
        payer_df.to_excel(writer, sheet_name="Payer_Variance", index=False)
        root_cause_df.to_excel(writer, sheet_name="Recoverable_by_RootCause", index=False)
        pareto_df.to_excel(writer, sheet_name="CARC_Pareto", index=False)
        taxonomy.to_excel(writer, sheet_name="CARC_Taxonomy", index=False)

    return kpis, {"kpi_csv": kpi_csv, "executive_xlsx": xlsx_path}
