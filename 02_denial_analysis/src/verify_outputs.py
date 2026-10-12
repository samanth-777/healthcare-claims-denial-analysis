#!/usr/bin/env python3
"""Assert regenerated datasets and SQL headline figures match portfolio README."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
SQL_DIR = ROOT / "02_denial_analysis" / "sql"

EXPECTED_RATES = {"Q3 2024": 8.2, "Q4 2024": 9.6, "Q1 2025": 11.7}
EXPECTED_RAR = {
    "Q3 2024": 1098360.48,
    "Q4 2024": 1316501.76,
    "Q1 2025": 1595158.11,
}
EXPECTED_IMPACTS = {
    "CO-4": 446644.27,
    "CO-16": 382837.95,
    "PR-96": 303080.04,
}
HEADLINE = 1897574.0


def main() -> int:
    gen = ROOT / "02_denial_analysis" / "src" / "generate_synthetic_data.py"
    subprocess.run([sys.executable, str(gen)], check=True, cwd=ROOT)

    quarterly = pd.read_csv(PROCESSED / "quarterly_claims_summary.csv")
    constants = pd.read_csv(PROCESSED / "analysis_constants.csv")
    denials = pd.read_csv(PROCESSED / "riverside_denial_log.csv")
    consts = dict(zip(constants["Constant"], constants["Value"]))

    rates = dict(zip(quarterly["Quarter"], quarterly["Denial_Rate_Pct"]))
    rar = dict(zip(quarterly["Quarter"], quarterly["Revenue_at_Risk"].round(2)))
    assert rates == EXPECTED_RATES, rates
    assert rar == EXPECTED_RAR, rar
    assert consts["INCREMENTAL_ANNUAL_REVENUE_EXPOSURE"] == HEADLINE
    assert len(denials) == 500

    shares = (denials["Denial_Code"].value_counts(normalize=True) * 100).round(1)
    assert float(shares["CO-4"]) == 28.0
    assert float(shares["CO-16"]) == 24.0
    assert float(shares["PR-96"]) == 19.0

    q1 = EXPECTED_RAR["Q1 2025"]
    for code, share in [("CO-4", 0.28), ("CO-16", 0.24), ("PR-96", 0.19)]:
        assert round(q1 * share, 2) == EXPECTED_IMPACTS[code]

    runner = ROOT / "02_denial_analysis" / "src" / "run_sql.py"
    for sql in sorted(SQL_DIR.glob("*.sql")):
        result = subprocess.run(
            [sys.executable, str(runner), str(sql)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stderr)
            return result.returncode
        if sql.name == "05_revenue_at_risk.sql":
            assert "RECONCILED" in result.stdout
            assert "1897574.0" in result.stdout or "1897574.00" in result.stdout

    print("verify_outputs: OK")
    print(f"  rates={rates}")
    print(f"  headline=${HEADLINE:,.2f}")
    print(f"  impacts={EXPECTED_IMPACTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
