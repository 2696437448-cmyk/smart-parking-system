#!/usr/bin/env python3
"""Step 12 baseline model runner.

Provides an explicit traditional baseline script for thesis comparison.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from step12_train_models import (
    baseline_predict_last_value,
    build_samples,
    evaluate_samples,
    load_region_series,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Step12 baseline model")
    parser.add_argument("--feature-input", default="data/processed/forecast_feature_table.csv")
    parser.add_argument("--output", default="artifacts/models/baseline_last_value_v1.json")
    parser.add_argument("--sequence-len", type=int, default=8)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    series = load_region_series(Path(args.feature_input))
    train_samples, test_samples = build_samples(series, args.sequence_len, args.train_ratio)

    payload = {
        "model_name": "baseline_last_value",
        "model_version": "step12-baseline-v1",
        "feature_input": args.feature_input,
        "sequence_len": args.sequence_len,
        "train_ratio": args.train_ratio,
        "train_metrics": evaluate_samples(train_samples, baseline_predict_last_value),
        "test_metrics": evaluate_samples(test_samples, baseline_predict_last_value),
        "params": {"strategy": "last_sequence_value"},
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"status": "ok", "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
