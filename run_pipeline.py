#!/usr/bin/env python3
"""End-to-end Healthcare RCM & Claims Denial Analytics pipeline.

Usage (from repo root)::

    python run_pipeline.py

Steps:
  1. Generate ~12,500 synthetic enterprise claims → data/raw_claims.csv
  2. Validate + HIPAA-sanitize
  3. Compute RCM KPIs / payer variance / recoverable revenue
  4. Train appeal overturn model and export prioritized worklist
  5. Render visual analytics → reports/figures/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.appeal_prediction import train_and_prioritize
from src.data_validator import validate_and_sanitize
from src.etl_pipeline import run_etl
from src.rcm_analytics import export_rcm_outputs
from src.visualize_rcm import generate_all_figures

OUTPUT_DIR = ROOT / "output"
FIG_DIR = ROOT / "reports" / "figures"
RAW_PATH = ROOT / "data" / "raw_claims.csv"
METRICS_JSON = OUTPUT_DIR / "pipeline_run_summary.json"


def main() -> int:
    print("=" * 64)
    print("Healthcare RCM & Claims Denial Analytics Pipeline")
    print("=" * 64)

    print("\n[1/5] ETL — generating synthetic enterprise claims …")
    claims = run_etl(output_path=RAW_PATH)
    print(f"      Wrote {len(claims):,} claims → {RAW_PATH.relative_to(ROOT)}")

    print("\n[2/5] Validation + HIPAA sanitization …")
    clean, report = validate_and_sanitize(claims)
    for action in report.sanitization_actions:
        print(f"      • {action}")
    for warn in report.warnings:
        print(f"      ! warning: {warn}")
    if not report.is_valid:
        print("      VALIDATION FAILED:")
        for issue in report.issues:
            print(f"        - {issue}")
        return 1
    print(f"      Validation OK ({report.row_count:,} rows)")

    # Persist sanitized extract alongside raw for audit trail.
    clean_path = ROOT / "data" / "processed_claims_sanitized.csv"
    export = clean.copy()
    export["service_date"] = export["service_date"].dt.strftime("%Y-%m-%d")
    export.to_csv(clean_path, index=False)
    print(f"      Sanitized extract → {clean_path.relative_to(ROOT)}")

    print("\n[3/5] RCM financial & performance analytics …")
    kpis, paths = export_rcm_outputs(clean, output_dir=OUTPUT_DIR)
    print(f"      Gross Denial Rate:          {kpis['gross_denial_rate_pct']}%")
    print(f"      Initial Clean Claim Rate:   {kpis['initial_clean_claim_rate_pct']}%")
    print(f"      Denied revenue:             ${kpis['denied_revenue']:,.2f}")
    print(f"      Est. recoverable revenue:   ${kpis['estimated_recoverable_revenue']:,.2f}")
    print(f"      KPI summary → {paths['kpi_csv'].relative_to(ROOT)}")
    print(f"      Executive workbook → {paths['executive_xlsx'].relative_to(ROOT)}")

    print("\n[4/5] Predictive appeal prioritization …")
    model_result = train_and_prioritize(clean, output_dir=OUTPUT_DIR)
    ev = model_result["evaluation"]
    print(f"      Model: {model_result['model_name']}")
    print(f"      ROC-AUC={ev.roc_auc:.4f}  Precision={ev.precision:.4f}  Recall={ev.recall:.4f}")
    print(
        f"      Worklist ({model_result['n_denied_scored']:,} denied) → "
        f"{model_result['worklist_path'].relative_to(ROOT)}"
    )

    print("\n[5/5] Visual analytics …")
    figures = generate_all_figures(
        clean, model_result["worklist"], fig_dir=FIG_DIR
    )
    for name, path in figures.items():
        print(f"      {name}: {path.relative_to(ROOT)}")

    summary = {
        "kpis": kpis,
        "model": {
            "name": model_result["model_name"],
            "n_train": model_result["n_train"],
            "n_appealed": model_result["n_appealed"],
            "metrics": ev.to_dict(),
        },
        "outputs": {
            "raw_claims": str(RAW_PATH.relative_to(ROOT)),
            "sanitized_claims": str(clean_path.relative_to(ROOT)),
            "kpi_csv": str(paths["kpi_csv"].relative_to(ROOT)),
            "executive_xlsx": str(paths["executive_xlsx"].relative_to(ROOT)),
            "appeal_worklist": str(model_result["worklist_path"].relative_to(ROOT)),
            "figures": {k: str(v.relative_to(ROOT)) for k, v in figures.items()},
        },
        "data_disclaimer": (
            "Claim-level data is synthetic. No PHI. Generated for portfolio "
            "demonstration and calibrated to industry denial-rate benchmarks."
        ),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_JSON.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nRun summary → {METRICS_JSON.relative_to(ROOT)}")
    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
