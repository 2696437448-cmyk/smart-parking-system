#!/usr/bin/env python3
"""Step 13: build/sync model registry from model artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LSTM_WEIGHT_NAMES = [
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_lstm_weights() -> list[float]:
    return [0.9, 0.3, -0.2, 0.6, 0.4, 0.1, 0.7, 0.2, -0.05, 0.8, 0.35, 0.0, 1.8, 0.5]


def _canonical_lstm_weights(raw: Any) -> list[float] | None:
    if isinstance(raw, list) and len(raw) == len(LSTM_WEIGHT_NAMES):
        return [float(v) for v in raw]
    if isinstance(raw, dict):
        vals: list[float] = []
        for k in LSTM_WEIGHT_NAMES:
            if k not in raw:
                return None
            vals.append(float(raw[k]))
        return vals
    return None


def _build_builtin_models() -> dict[str, dict[str, Any]]:
    weights = _default_lstm_weights()
    ts = _now_iso()
    return {
        "v0.1-lstm-lite": {
            "model_version": "v0.1-lstm-lite",
            "model_name": "lstm_lite",
            "predictor": "lstm_lite",
            "weights": weights,
            "source": "builtin",
            "created_at": ts,
        },
        "v0.2-lstm-lite": {
            "model_version": "v0.2-lstm-lite",
            "model_name": "lstm_lite",
            "predictor": "lstm_lite",
            "weights": weights,
            "source": "builtin",
            "created_at": ts,
        },
    }


def _read_artifact_models(artifact_dir: Path) -> dict[str, dict[str, Any]]:
    models: dict[str, dict[str, Any]] = {}
    if not artifact_dir.exists():
        return models

    for path in sorted(artifact_dir.glob("*.json")):
        if path.name == "model_registry.json":
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        model_version = str(payload.get("model_version", "")).strip()
        model_name = str(payload.get("model_name", "")).strip()

        if not model_version or not model_name:
            continue

        if model_name == "lstm_lite":
            weights = _canonical_lstm_weights(payload.get("weights"))
            if weights is None:
                continue
            models[model_version] = {
                "model_version": model_version,
                "model_name": "lstm_lite",
                "predictor": "lstm_lite",
                "weights": weights,
                "source": f"artifact:{path.name}",
                "created_at": str(payload.get("trained_at") or _now_iso()),
            }
        elif model_name == "baseline_last_value":
            models[model_version] = {
                "model_version": model_version,
                "model_name": "baseline_last_value",
                "predictor": "baseline_last_value",
                "source": f"artifact:{path.name}",
                "created_at": str(payload.get("trained_at") or _now_iso()),
            }

    return models


def _select_active(models: dict[str, dict[str, Any]], preferred: str) -> str:
    if preferred and preferred in models:
        return preferred
    if "step12-lstm-lite-v1" in models:
        return "step12-lstm-lite-v1"
    if "v0.2-lstm-lite" in models:
        return "v0.2-lstm-lite"
    return sorted(models.keys())[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync model registry for Step13")
    parser.add_argument("--artifact-dir", default="artifacts/models")
    parser.add_argument("--output", default="artifacts/models/model_registry.json")
    parser.add_argument("--active-model", default="step12-lstm-lite-v1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    artifact_dir = Path(args.artifact_dir)
    output = Path(args.output)

    models = _build_builtin_models()
    models.update(_read_artifact_models(artifact_dir))

    if not models:
        raise RuntimeError("no models found for registry")

    active = _select_active(models, args.active_model)

    existing_history = []
    if output.exists():
        try:
            existing = json.loads(output.read_text(encoding="utf-8"))
            hist = existing.get("activation_history", [])
            if isinstance(hist, list):
                existing_history = hist[-200:]
        except Exception:
            existing_history = []

    payload = {
        "registry_version": "step13.v1",
        "generated_at": _now_iso(),
        "active_version": active,
        "models": models,
        "activation_history": existing_history,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "output": str(output),
                "active_version": active,
                "model_count": len(models),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
