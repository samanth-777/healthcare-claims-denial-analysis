"""Visual analytics for RCM denial performance and appeal ROI."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.payer_variance import payer_denial_summary
from src.rcm_analytics import carc_pareto
from src.schema import MEDICARE_FFS_DENIAL_BENCHMARK

DEFAULT_FIG_DIR = Path(__file__).resolve().parents[1] / "reports" / "figures"

# Professional clinical / finance palette (avoid purple/indigo AI cliché).
COLORS = {
    "navy": "#0B3D5C",
    "teal": "#1A7A6D",
    "amber": "#C47B2C",
    "slate": "#4A5560",
    "muted": "#A8B0B8",
    "benchmark": "#B33A3A",
}


def _style_axes(ax: plt.Axes, title: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=13, fontweight="bold", color=COLORS["navy"], pad=12)
    ax.set_ylabel(ylabel, color=COLORS["slate"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=COLORS["slate"])
    ax.set_facecolor("#F7F9FA")


def plot_payer_denial_vs_benchmark(
    df: pd.DataFrame,
    fig_dir: Path | str | None = None,
) -> Path:
    """Bar chart: payer denial rates vs Medicare FFS industry benchmark."""
    out = Path(fig_dir) if fig_dir else DEFAULT_FIG_DIR
    out.mkdir(parents=True, exist_ok=True)

    summary = payer_denial_summary(df)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(summary))
    bars = ax.bar(
        x,
        summary["denial_rate_pct"],
        color=[
            COLORS["teal"] if p == "Medicare FFS" else COLORS["navy"]
            for p in summary["payer_name"]
        ],
        edgecolor="white",
        width=0.72,
    )
    bench_pct = MEDICARE_FFS_DENIAL_BENCHMARK * 100
    ax.axhline(
        bench_pct,
        color=COLORS["benchmark"],
        linestyle="--",
        linewidth=1.8,
        label=f"Medicare FFS benchmark ({bench_pct:.1f}%)",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(summary["payer_name"], rotation=20, ha="right")
    for bar, pct, var in zip(bars, summary["denial_rate_pct"], summary["variance_vs_benchmark_pp"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.25,
            f"{pct:.1f}%\n({var:+.1f} pp)",
            ha="center",
            va="bottom",
            fontsize=8,
            color=COLORS["slate"],
        )
    _style_axes(ax, "Payer Denial Rates vs Medicare FFS Benchmark", "Denial rate (%)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_ylim(0, max(summary["denial_rate_pct"].max() * 1.25, bench_pct * 1.4))
    fig.tight_layout()
    path = out / "payer_denial_rates_vs_benchmark.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_carc_rarc_pareto(
    df: pd.DataFrame,
    fig_dir: Path | str | None = None,
) -> Path:
    """Pareto chart of denied revenue by CARC (with RARC labels)."""
    out = Path(fig_dir) if fig_dir else DEFAULT_FIG_DIR
    out.mkdir(parents=True, exist_ok=True)

    pareto = carc_pareto(df)
    if pareto.empty:
        raise ValueError("No denied claims available for Pareto chart")

    labels = pareto.apply(lambda r: f"{r['carc_code']} / {r['rarc_code']}", axis=1)
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax1.bar(labels, pareto["denied_revenue"] / 1_000, color=COLORS["navy"], edgecolor="white")
    ax1.set_ylabel("Denied revenue ($000s)", color=COLORS["slate"])
    ax1.tick_params(axis="x", rotation=25, labelcolor=COLORS["slate"])

    ax2 = ax1.twinx()
    ax2.plot(
        labels,
        pareto["cumulative_pct"],
        color=COLORS["amber"],
        marker="o",
        linewidth=2,
        label="Cumulative % of denied $",
    )
    ax2.set_ylabel("Cumulative % of denied revenue", color=COLORS["amber"])
    ax2.set_ylim(0, 110)
    ax2.axhline(80, color=COLORS["muted"], linestyle=":", linewidth=1.2)

    _style_axes(ax1, "CARC / RARC Root-Cause Pareto (Denied Revenue)", "")
    ax1.set_ylabel("Denied revenue ($000s)", color=COLORS["slate"])
    ax2.spines["top"].set_visible(False)
    ax2.legend(frameon=False, loc="center right")
    fig.tight_layout()
    path = out / "carc_rarc_root_cause_pareto.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_cumulative_recovery_curve(
    worklist: pd.DataFrame,
    fig_dir: Path | str | None = None,
) -> Path:
    """ROI curve: cumulative expected recovery from prioritized appeals."""
    out = Path(fig_dir) if fig_dir else DEFAULT_FIG_DIR
    out.mkdir(parents=True, exist_ok=True)

    wl = worklist.sort_values("worklist_rank").copy()
    wl["cum_expected_recovery"] = wl["expected_recovery"].cumsum()
    wl["cum_claims"] = np.arange(1, len(wl) + 1)
    # Random-order baseline for contrast.
    rng = np.random.default_rng(42)
    shuffled = wl["expected_recovery"].to_numpy().copy()
    rng.shuffle(shuffled)
    random_cum = np.cumsum(shuffled)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(
        wl["cum_claims"],
        wl["cum_expected_recovery"] / 1_000,
        color=COLORS["teal"],
        linewidth=2.4,
        label="Model-prioritized worklist",
    )
    ax.plot(
        wl["cum_claims"],
        random_cum / 1_000,
        color=COLORS["muted"],
        linewidth=1.6,
        linestyle="--",
        label="Random appeal order (baseline)",
    )
    # Mark top-decile cadence.
    top10 = max(int(len(wl) * 0.10), 1)
    top10_val = wl["cum_expected_recovery"].iloc[top10 - 1] / 1_000
    ax.scatter([top10], [top10_val], color=COLORS["amber"], s=60, zorder=5)
    ax.annotate(
        f"Top 10% appeals\n${top10_val:,.0f}K expected",
        xy=(top10, top10_val),
        xytext=(top10 + len(wl) * 0.08, top10_val * 0.75),
        fontsize=9,
        color=COLORS["slate"],
        arrowprops=dict(arrowstyle="->", color=COLORS["amber"]),
    )
    _style_axes(
        ax,
        "Cumulative Revenue Recovery Curve (Prioritized Appeals)",
        "Cumulative expected recovery ($000s)",
    )
    ax.set_xlabel("Appeals worked (ranked order)", color=COLORS["slate"])
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    path = out / "cumulative_revenue_recovery_curve.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def generate_all_figures(
    df: pd.DataFrame,
    worklist: pd.DataFrame,
    fig_dir: Path | str | None = None,
) -> dict[str, Path]:
    """Render the three required RCM figures."""
    out = Path(fig_dir) if fig_dir else DEFAULT_FIG_DIR
    return {
        "payer_benchmark": plot_payer_denial_vs_benchmark(df, out),
        "carc_pareto": plot_carc_rarc_pareto(df, out),
        "recovery_curve": plot_cumulative_recovery_curve(worklist, out),
    }
