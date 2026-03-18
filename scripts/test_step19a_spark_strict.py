#!/usr/bin/env python3
"""Step19A gate: Spark strict ETL and OpenAPI dependency verification."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY = ROOT / "reports" / "step19a_spark_quality.json"
FORECAST = ROOT / "data" / "processed" / "forecast_feature_table.csv"
DISPATCH = ROOT / "data" / "processed" / "dispatch_input_table.csv"


def spark_env() -> dict[str, str]:
    env = os.environ.copy()
    if env.get("JAVA_HOME"):
        return env

    candidates = [
        Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
        Path("/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
        Path("/opt/homebrew/opt/openjdk@17"),
        Path("/usr/local/opt/openjdk@17"),
    ]
    for candidate in candidates:
        java_bin = candidate / "bin" / "java"
        if java_bin.exists():
            env["JAVA_HOME"] = str(candidate)
            env["PATH"] = f"{candidate / 'bin'}:{env.get('PATH', '')}"
            return env
    return env


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, cwd=ROOT, env=spark_env(), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed: {cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")


def main() -> None:
    run([
        sys.executable,
        "scripts/step11_etl.py",
        "--engine",
        "spark",
        "--raw-dir",
        "data/raw",
        "--forecast-output",
        str(FORECAST),
        "--dispatch-output",
        str(DISPATCH),
        "--quality-output",
        str(QUALITY),
    ])
    payload = json.loads(QUALITY.read_text(encoding="utf-8"))
    if payload.get("engine") != "spark":
        raise AssertionError(f"engine is not spark: {payload.get('engine')}")
    if not payload.get("overall_passed"):
        raise AssertionError("spark strict ETL did not pass")

    run([sys.executable, "scripts/validate_openapi.py", "--spec", "openapi/smart-parking.yaml"])
    print("STEP19A_GATE_PASS")


if __name__ == "__main__":
    main()
