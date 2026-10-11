#!/usr/bin/env python3
"""Load processed CSVs into DuckDB and run a SQL file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"


def split_statements(sql: str) -> list[str]:
    stmts: list[str] = []
    buf: list[str] = []
    for line in sql.splitlines():
        if not buf and line.strip().startswith("--"):
            continue
        buf.append(line)
        if line.strip().endswith(";"):
            text = "\n".join(buf).strip()
            if text:
                stmts.append(text)
            buf = []
    if buf and "".join(buf).strip():
        stmts.append("\n".join(buf).strip())
    return stmts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sql_file", type=Path)
    args = parser.parse_args()

    con = duckdb.connect()
    # Force HCPCS_Code to VARCHAR — numeric-looking codes otherwise bind as BIGINT.
    con.execute(
        f"CREATE OR REPLACE TABLE riverside_denial_log AS "
        f"SELECT * FROM read_csv_auto("
        f"'{PROCESSED / 'riverside_denial_log.csv'}', "
        f"types={{'HCPCS_Code': 'VARCHAR'}})"
    )
    con.execute(
        f"CREATE OR REPLACE TABLE quarterly_claims_summary AS "
        f"SELECT * FROM read_csv_auto('{PROCESSED / 'quarterly_claims_summary.csv'}')"
    )
    con.execute(
        f"CREATE OR REPLACE TABLE analysis_constants AS "
        f"SELECT * FROM read_csv_auto('{PROCESSED / 'analysis_constants.csv'}')"
    )

    for i, stmt in enumerate(split_statements(args.sql_file.read_text()), 1):
        clean = re.sub(r"^(?:\s*--[^\n]*\n)+", "", stmt).strip()
        if not clean:
            continue
        print(f"\n=== Statement {i} ===")
        print(con.execute(clean).fetchdf().to_string(index=False))


if __name__ == "__main__":
    main()
