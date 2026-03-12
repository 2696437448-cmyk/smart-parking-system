#!/usr/bin/env python3
"""Step 12 gate: verify model training reproducibility and outputs."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_SCRIPT = PROJECT_ROOT / "scripts/step12_train_models.py"
BASELINE_SCRIPT = PROJECT_ROOT / "scripts/step12_baseline_model.py"
OPENAPI_VALIDATOR = PROJECT_ROOT / "scripts/validate_openapi.py"
SPEC_PATH = PROJECT_ROOT / "openapi/smart-parking.yaml"

TMP_DIR = Path("/tmp/smart_parking_step12_tmp")


def _run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc.stdout


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_metrics_shape(payload: dict) -> None:
    models = payload.get("models", {})
    for model_name in ("baseline_last_value", "lstm_lite"):
        if model_name not in models:
            raise AssertionError(f"missing model in metrics: {model_name}")

        for split in ("train", "test"):
            metric = models[model_name].get(split, {})
            for key in ("mae", "rmse", "mape", "sample_count"):
                if key not in metric:
                    raise AssertionError(f"missing metric field model={model_name} split={split} key={key}")
                if key == "sample_count":
                    if int(metric[key]) <= 0:
                        raise AssertionError(f"invalid sample_count in {model_name}/{split}: {metric[key]}")
                else:
                    if float(metric[key]) < 0:
                        raise AssertionError(f"invalid metric in {model_name}/{split}: {key}={metric[key]}")


def _assert_comparison_csv(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)

    required = {"model", "split", "mae", "rmse", "mape", "sample_count"}
    if not required.issubset(set(headers)):
        raise AssertionError(f"comparison csv missing columns: {sorted(required - set(headers))}")

    if len(rows) < 4:
        raise AssertionError(f"comparison csv row count too small: {len(rows)}")


def _assert_reproducible(metric_a: dict, metric_b: dict) -> None:
    keys = [
        ("baseline_last_value", "test", "mae"),
        ("baseline_last_value", "test", "rmse"),
        ("baseline_last_value", "test", "mape"),
        ("lstm_lite", "test", "mae"),
        ("lstm_lite", "test", "rmse"),
        ("lstm_lite", "test", "mape"),
    ]

    for model, split, metric in keys:
        a = float(metric_a["models"][model][split][metric])
        b = float(metric_b["models"][model][split][metric])
        if abs(a - b) > 1e-10:
            raise AssertionError(
                f"non-reproducible metric {model}/{split}/{metric}: runA={a}, runB={b}"
            )


def main() -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    run_a = {
        "output_dir": TMP_DIR / "artifacts_a",
        "metrics_json": TMP_DIR / "metrics_a.json",
        "comparison_csv": TMP_DIR / "comparison_a.csv",
        "comparison_md": TMP_DIR / "comparison_a.md",
    }
    run_b = {
        "output_dir": TMP_DIR / "artifacts_b",
        "metrics_json": TMP_DIR / "metrics_b.json",
        "comparison_csv": TMP_DIR / "comparison_b.csv",
        "comparison_md": TMP_DIR / "comparison_b.md",
    }

    base_cmd = [
        sys.executable,
        str(TRAIN_SCRIPT),
        "--feature-input",
        str(PROJECT_ROOT / "data/processed/forecast_feature_table.csv"),
        "--seed",
        "20260312",
        "--epochs",
        "350",
        "--sequence-len",
        "8",
        "--train-ratio",
        "0.8",
    ]

    _run(
        base_cmd
        + [
            "--output-dir",
            str(run_a["output_dir"]),
            "--metrics-json",
            str(run_a["metrics_json"]),
            "--comparison-csv",
            str(run_a["comparison_csv"]),
            "--comparison-md",
            str(run_a["comparison_md"]),
        ]
    )
    _run(
        base_cmd
        + [
            "--output-dir",
            str(run_b["output_dir"]),
            "--metrics-json",
            str(run_b["metrics_json"]),
            "--comparison-csv",
            str(run_b["comparison_csv"]),
            "--comparison-md",
            str(run_b["comparison_md"]),
        ]
    )

    # Dedicated baseline script should also be executable.
    _run(
        [
            sys.executable,
            str(BASELINE_SCRIPT),
            "--feature-input",
            str(PROJECT_ROOT / "data/processed/forecast_feature_table.csv"),
            "--output",
            str(TMP_DIR / "baseline_only.json"),
        ]
    )

    metric_a = _load_json(run_a["metrics_json"])
    metric_b = _load_json(run_b["metrics_json"])

    _assert_metrics_shape(metric_a)
    _assert_metrics_shape(metric_b)
    _assert_comparison_csv(run_a["comparison_csv"])
    _assert_comparison_csv(run_b["comparison_csv"])
    _assert_reproducible(metric_a, metric_b)

    preview = metric_a.get("contract_preview", {}).get("records", [])
    if not preview:
        raise AssertionError("missing contract preview records")
    for rec in preview:
        for key in ("region_id", "ts", "supply", "demand", "gap"):
            if key not in rec:
                raise AssertionError(f"missing contract field in preview: {key}")

    # Validate OpenAPI contract still passes after Step12 changes.
    _run([sys.executable, str(OPENAPI_VALIDATOR), "--spec", str(SPEC_PATH)])

    print("STEP12_GATE_PASS")


if __name__ == "__main__":
    main()
