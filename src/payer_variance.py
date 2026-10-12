"""Payer denial-rate variance analysis vs Medicare FFS benchmark."""

from __future__ import annotations

import pandas as pd

from src.schema import MEDICARE_FFS_DENIAL_BENCHMARK, PAYERS


def payer_denial_summary(
    df: pd.DataFrame,
    benchmark: float = MEDICARE_FFS_DENIAL_BENCHMARK,
) -> pd.DataFrame:
    """Compute denial rates, revenue denied, and variance vs Medicare FFS."""
    denied = df["claim_status"] == "Denied"
    grouped = (
        df.assign(is_denied=denied.astype(int))
        .groupby("payer_name", dropna=False)
        .agg(
            claims=("claim_id", "count"),
            denied_claims=("is_denied", "sum"),
            total_billed=("claim_amount", "sum"),
            denied_revenue=("claim_amount", lambda s: s[denied.loc[s.index]].sum()),
        )
        .reset_index()
    )
    grouped["denial_rate"] = grouped["denied_claims"] / grouped["claims"]
    grouped["denial_rate_pct"] = (grouped["denial_rate"] * 100).round(2)
    grouped["benchmark_rate"] = benchmark
    grouped["benchmark_pct"] = round(benchmark * 100, 2)
    grouped["variance_vs_benchmark_pp"] = (
        (grouped["denial_rate"] - benchmark) * 100
    ).round(2)
    grouped["variance_flag"] = grouped["variance_vs_benchmark_pp"].apply(
        lambda x: "Above Benchmark" if x > 0 else ("At/Below Benchmark" if x <= 0 else "n/a")
    )

    # Stable payer order matching schema.
    order = {p: i for i, p in enumerate(PAYERS)}
    grouped["_ord"] = grouped["payer_name"].map(order).fillna(99)
    grouped = grouped.sort_values("_ord").drop(columns="_ord").reset_index(drop=True)
    return grouped


def medicare_ffs_observed_rate(df: pd.DataFrame) -> float:
    """Observed Medicare FFS denial rate in the extract."""
    subset = df[df["payer_name"] == "Medicare FFS"]
    if subset.empty:
        return float("nan")
    return float((subset["claim_status"] == "Denied").mean())
