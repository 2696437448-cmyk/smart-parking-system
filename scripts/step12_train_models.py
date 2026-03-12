#!/usr/bin/env python3
"""Step 12: reproducible model training (LSTM-lite + baseline comparison).

No heavy ML dependency is required. The script trains a lightweight gated
recurrent model with deterministic random-search optimization and compares it
against a traditional last-value baseline.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


EPSILON = 1e-6


@dataclass
class SequenceSample:
    region_id: str
    ts: str
    sequence: list[float]
    target: float
    capacity: float


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _safe_float(raw: Any, default: float = 0.0) -> float:
    try:
        return float(raw)
    except Exception:
        return default


def _parse_ts(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


def load_region_series(feature_csv: Path) -> dict[str, list[tuple[datetime, float, float]]]:
    if not feature_csv.exists():
        raise FileNotFoundError(f"feature table not found: {feature_csv}")

    series: dict[str, list[tuple[datetime, float, float]]] = {}

    with feature_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            region_id = (row.get("region_id") or "").strip()
            ts_raw = row.get("ts") or ""
            dt = _parse_ts(ts_raw)
            if not region_id or dt is None:
                continue

            occupancy = _clamp01(_safe_float(row.get("occupancy_rate"), 0.0))
            capacity = max(1.0, _safe_float(row.get("capacity"), 1.0))
            series.setdefault(region_id, []).append((dt, occupancy, capacity))

    for region_id, values in series.items():
        values.sort(key=lambda item: item[0])
        if len(values) < 12:
            raise ValueError(f"insufficient history for region={region_id}, rows={len(values)}")

    if not series:
        raise ValueError("no valid training rows in feature table")

    return series


def build_samples(
    series: dict[str, list[tuple[datetime, float, float]]],
    sequence_len: int,
    train_ratio: float,
) -> tuple[list[SequenceSample], list[SequenceSample]]:
    if sequence_len < 2:
        raise ValueError("sequence_len must be >= 2")
    if not (0.5 <= train_ratio < 1.0):
        raise ValueError("train_ratio must be in [0.5, 1.0)")

    train_samples: list[SequenceSample] = []
    test_samples: list[SequenceSample] = []

    for region_id, rows in series.items():
        region_samples: list[SequenceSample] = []
        rates = [r[1] for r in rows]

        for idx in range(sequence_len, len(rows)):
            sequence = rates[idx - sequence_len : idx]
            target = rates[idx]
            ts = rows[idx][0].isoformat()
            capacity = rows[idx][2]
            region_samples.append(
                SequenceSample(
                    region_id=region_id,
                    ts=ts,
                    sequence=sequence,
                    target=target,
                    capacity=capacity,
                )
            )

        if len(region_samples) < 4:
            continue

        split = int(len(region_samples) * train_ratio)
        split = max(1, min(split, len(region_samples) - 1))

        train_samples.extend(region_samples[:split])
        test_samples.extend(region_samples[split:])

    if not train_samples or not test_samples:
        raise ValueError("failed to build train/test samples")

    return train_samples, test_samples


def baseline_predict_last_value(sample: SequenceSample) -> float:
    return _clamp01(sample.sequence[-1])


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(min(x, 35.0), -35.0)))


def lstm_lite_predict(weights: list[float], sample: SequenceSample) -> float:
    (
        w_ix,
        w_ih,
        b_i,
        w_fx,
        w_fh,
        b_f,
        w_ox,
        w_oh,
        b_o,
        w_gx,
        w_gh,
        b_g,
        w_y,
        b_y,
    ) = weights

    h = 0.0
    c = 0.0
    for x in sample.sequence:
        i_gate = _sigmoid(w_ix * x + w_ih * h + b_i)
        f_gate = _sigmoid(w_fx * x + w_fh * h + b_f)
        o_gate = _sigmoid(w_ox * x + w_oh * h + b_o)
        g_gate = math.tanh(w_gx * x + w_gh * h + b_g)
        c = f_gate * c + i_gate * g_gate
        h = o_gate * math.tanh(c)

    return _clamp01(_sigmoid(w_y * h + b_y))


def compute_metrics(y_true: list[float], y_pred: list[float]) -> dict[str, float]:
    if not y_true or len(y_true) != len(y_pred):
        raise ValueError("metric input must be non-empty and length-equal")

    n = float(len(y_true))
    abs_errors = [abs(t - p) for t, p in zip(y_true, y_pred)]
    sq_errors = [(t - p) ** 2 for t, p in zip(y_true, y_pred)]
    ape = [abs(t - p) / max(abs(t), EPSILON) for t, p in zip(y_true, y_pred)]

    mae = sum(abs_errors) / n
    rmse = math.sqrt(sum(sq_errors) / n)
    mape = (sum(ape) / n) * 100.0

    return {
        "mae": round(mae, 8),
        "rmse": round(rmse, 8),
        "mape": round(mape, 8),
        "sample_count": int(n),
    }


def evaluate_samples(samples: list[SequenceSample], predictor: Callable[[SequenceSample], float]) -> dict[str, float]:
    y_true = [s.target for s in samples]
    y_pred = [_clamp01(float(predictor(s))) for s in samples]
    return compute_metrics(y_true=y_true, y_pred=y_pred)


def _loss_mae(weights: list[float], samples: list[SequenceSample]) -> float:
    if not samples:
        return float("inf")
    total = 0.0
    for sample in samples:
        pred = lstm_lite_predict(weights, sample)
        total += abs(sample.target - pred)
    return total / float(len(samples))


def train_lstm_lite(samples: list[SequenceSample], seed: int, epochs: int) -> tuple[list[float], float]:
    # Start from Step 5 fixed small-weight priors for stability.
    best_weights = [
        0.9,
        0.3,
        -0.2,
        0.6,
        0.4,
        0.1,
        0.7,
        0.2,
        -0.05,
        0.8,
        0.35,
        0.0,
        1.8,
        0.5,
    ]

    rng = random.Random(seed)
    best_loss = _loss_mae(best_weights, samples)

    for epoch in range(max(1, epochs)):
        step_scale = max(0.0015, 0.08 * (0.9965 ** epoch))
        candidate = [w + rng.uniform(-step_scale, step_scale) for w in best_weights]
        candidate_loss = _loss_mae(candidate, samples)

        if candidate_loss <= best_loss:
            best_weights = candidate
            best_loss = candidate_loss

        # Periodic broader exploration to avoid local minima on tiny datasets.
        if (epoch + 1) % 120 == 0:
            jump = [w + rng.uniform(-0.03, 0.03) for w in best_weights]
            jump_loss = _loss_mae(jump, samples)
            if jump_loss < best_loss:
                best_weights = jump
                best_loss = jump_loss

    return best_weights, best_loss


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_md(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("# Step12 模型对比\n\n无数据。\n", encoding="utf-8")
        return

    headers = list(rows[0].keys())
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")

    content = "# Step12 模型对比结果\n\n" + "\n".join(lines) + "\n"
    path.write_text(content, encoding="utf-8")


def _weights_dict(weights: list[float]) -> dict[str, float]:
    names = [
        "w_ix",
        "w_ih",
        "b_i",
        "w_fx",
        "w_fh",
        "b_f",
        "w_ox",
        "w_oh",
        "b_o",
        "w_gx",
        "w_gh",
        "b_g",
        "w_y",
        "b_y",
    ]
    return {name: round(value, 10) for name, value in zip(names, weights)}


def _contract_preview(samples: list[SequenceSample], weights: list[float]) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []

    for sample in samples[:3]:
        occ_pred = lstm_lite_predict(weights, sample)
        demand = round(sample.capacity * occ_pred, 4)
        supply = round(max(0.0, sample.capacity - demand), 4)
        gap = round(supply - demand, 4)
        preview.append(
            {
                "region_id": sample.region_id,
                "ts": sample.ts,
                "supply": supply,
                "demand": demand,
                "gap": gap,
            }
        )

    return preview


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Step12 train LSTM-lite and baseline models")
    parser.add_argument(
        "--feature-input",
        default="data/processed/forecast_feature_table.csv",
        help="Step11 feature table path",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/models",
        help="model artifact output directory",
    )
    parser.add_argument(
        "--metrics-json",
        default="reports/step12_model_metrics.json",
        help="full metrics json output",
    )
    parser.add_argument(
        "--comparison-csv",
        default="reports/step12_model_comparison.csv",
        help="comparison csv output",
    )
    parser.add_argument(
        "--comparison-md",
        default="reports/step12_model_comparison.md",
        help="comparison markdown output",
    )
    parser.add_argument("--sequence-len", type=int, default=8, help="history length")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="train split ratio")
    parser.add_argument("--seed", type=int, default=20260312, help="deterministic seed")
    parser.add_argument("--epochs", type=int, default=900, help="lstm-lite optimization epochs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    feature_input = Path(args.feature_input)
    output_dir = Path(args.output_dir)
    metrics_json = Path(args.metrics_json)
    comparison_csv = Path(args.comparison_csv)
    comparison_md = Path(args.comparison_md)

    series = load_region_series(feature_input)
    train_samples, test_samples = build_samples(
        series=series,
        sequence_len=args.sequence_len,
        train_ratio=args.train_ratio,
    )

    baseline_train = evaluate_samples(train_samples, baseline_predict_last_value)
    baseline_test = evaluate_samples(test_samples, baseline_predict_last_value)

    lstm_weights, train_loss = train_lstm_lite(
        samples=train_samples,
        seed=args.seed,
        epochs=args.epochs,
    )

    lstm_train = evaluate_samples(train_samples, lambda sample: lstm_lite_predict(lstm_weights, sample))
    lstm_test = evaluate_samples(test_samples, lambda sample: lstm_lite_predict(lstm_weights, sample))

    comparison_rows = [
        {"model": "baseline_last_value", "split": "train", **baseline_train},
        {"model": "baseline_last_value", "split": "test", **baseline_test},
        {"model": "lstm_lite", "split": "train", **lstm_train},
        {"model": "lstm_lite", "split": "test", **lstm_test},
    ]

    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_artifact = {
        "model_name": "baseline_last_value",
        "model_version": "step12-baseline-v1",
        "trained_at": _now_iso(),
        "feature_input": str(feature_input),
        "sequence_len": args.sequence_len,
        "train_ratio": args.train_ratio,
        "train_metrics": baseline_train,
        "test_metrics": baseline_test,
        "params": {"strategy": "last_sequence_value"},
    }
    _write_json(output_dir / "baseline_last_value_v1.json", baseline_artifact)

    lstm_artifact = {
        "model_name": "lstm_lite",
        "model_version": "step12-lstm-lite-v1",
        "trained_at": _now_iso(),
        "feature_input": str(feature_input),
        "seed": args.seed,
        "epochs": args.epochs,
        "sequence_len": args.sequence_len,
        "train_ratio": args.train_ratio,
        "train_loss_mae": round(train_loss, 8),
        "train_metrics": lstm_train,
        "test_metrics": lstm_test,
        "weights": _weights_dict(lstm_weights),
    }
    _write_json(output_dir / "lstm_lite_v1.json", lstm_artifact)

    metrics_payload = {
        "generated_at": _now_iso(),
        "feature_input": str(feature_input),
        "seed": args.seed,
        "epochs": args.epochs,
        "sequence_len": args.sequence_len,
        "train_ratio": args.train_ratio,
        "train_samples": len(train_samples),
        "test_samples": len(test_samples),
        "models": {
            "baseline_last_value": {
                "type": "traditional_baseline",
                "train": baseline_train,
                "test": baseline_test,
                "model_version": "step12-baseline-v1",
            },
            "lstm_lite": {
                "type": "lightweight_lstm",
                "train": lstm_train,
                "test": lstm_test,
                "model_version": "step12-lstm-lite-v1",
                "train_loss_mae": round(train_loss, 8),
            },
        },
        "contract_preview": {
            "schema": "DemandGapRecord(region_id, ts, supply, demand, gap)",
            "records": _contract_preview(test_samples, lstm_weights),
        },
    }

    _write_json(metrics_json, metrics_payload)
    _write_csv(comparison_csv, comparison_rows)
    _write_md(comparison_md, comparison_rows)

    print(
        json.dumps(
            {
                "status": "ok",
                "train_samples": len(train_samples),
                "test_samples": len(test_samples),
                "lstm_test": lstm_test,
                "baseline_test": baseline_test,
                "metrics_json": str(metrics_json),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
