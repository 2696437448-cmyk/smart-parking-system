#!/usr/bin/env python3
"""Step 11 gate: verify ETL outputs and schema quality."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORECAST = PROJECT_ROOT / "data/processed/forecast_feature_table.csv"
DISPATCH = PROJECT_ROOT / "data/processed/dispatch_input_table.csv"
QUALITY = PROJECT_ROOT / "reports/step11_etl_quality.json"


FORECAST_REQUIRED = {
    "region_id",
    "ts",
    "capacity",
    "occupancy_rate",
    "vehicle_in_count",
    "vehicle_out_count",
    "trip_probability_avg",
    "supply_proxy",
    "demand_proxy",
    "gap_proxy",
    "feature_schema_version",
    "source_mode",
}

DISPATCH_REQUIRED = {
    "region_id",
    "ts",
    "estimated_supply",
    "estimated_demand",
    "estimated_gap",
    "congestion_score",
    "price_factor",
    "dispatch_priority",
    "feature_schema_version",
    "source_mode",
}


def _run_etl() -> None:
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts/step11_etl.py"),
        "--source-mode",
        "files",
        "--raw-dir",
        str(PROJECT_ROOT / "data/raw"),
        "--forecast-output",
        str(FORECAST),
        "--dispatch-output",
        str(DISPATCH),
        "--quality-output",
        str(QUALITY),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"step11 etl failed\nstdout={proc.stdout}\nstderr={proc.stderr}")



def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
    return headers, rows



def _assert_ts(rows: list[dict[str, str]], field: str = "ts") -> None:
    for idx, row in enumerate(rows[:200]):
        raw = row.get(field, "")
        try:
            datetime.fromisoformat(raw)
        except Exception as ex:
            raise AssertionError(f"invalid ts at row {idx}: {raw}; err={ex}")



def main() -> None:
    _run_etl()

    f_headers, f_rows = _read_csv(FORECAST)
    d_headers, d_rows = _read_csv(DISPATCH)

    if not f_rows:
        raise AssertionError("forecast_feature_table is empty")
    if not d_rows:
        raise AssertionError("dispatch_input_table is empty")

    missing_f = sorted(FORECAST_REQUIRED - set(f_headers))
    missing_d = sorted(DISPATCH_REQUIRED - set(d_headers))

    if missing_f:
        raise AssertionError(f"forecast missing columns: {missing_f}")
    if missing_d:
        raise AssertionError(f"dispatch missing columns: {missing_d}")

    _assert_ts(f_rows, "ts")
    _assert_ts(d_rows, "ts")

    source_modes = {r.get("source_mode", "") for r in f_rows[:100]}
    if not source_modes.issubset({"external", "fallback_raw", "mysql_raw"}):
        raise AssertionError(f"unexpected source_mode values: {source_modes}")

    with QUALITY.open("r", encoding="utf-8") as f:
        quality = json.load(f)

    if not quality.get("overall_passed"):
        raise AssertionError("quality report overall_passed is false")

    print("STEP11_GATE_PASS")


if __name__ == "__main__":
    main()
