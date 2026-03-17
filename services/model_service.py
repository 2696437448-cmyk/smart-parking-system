#!/usr/bin/env python3
"""Model service with registry, hot activation, and rollback support (Step 13)."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import combinations, permutations
from pathlib import Path
from typing import Any

SERVICE_NAME = os.getenv("SERVICE_NAME", "model-service")
PORT = int(os.getenv("PORT", "8000"))
SLOT_STATUS_PATH = os.getenv("SLOT_STATUS_PATH", "/app/../data/raw/slot_status.csv")
MODEL_ARTIFACT_DIR = os.getenv("MODEL_ARTIFACT_DIR", "/app/../artifacts/models")
MODEL_REGISTRY_PATH = os.getenv("MODEL_REGISTRY_PATH", "/app/../artifacts/models/model_registry.json")
MODEL_ACTIVE_DEFAULT = os.getenv("MODEL_ACTIVE_DEFAULT", "step12-lstm-lite-v1")

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


def _default_lstm_weights() -> list[float]:
    # Step 5 fixed small-weight priors.
    return [
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(raw: Any, default: float = 0.0) -> float:
    try:
        return float(raw)
    except Exception:
        return default


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(min(x, 35.0), -35.0)))


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def _canonicalize_lstm_weights(raw: Any) -> list[float] | None:
    if isinstance(raw, list) and len(raw) == len(LSTM_WEIGHT_NAMES):
        return [_safe_float(x) for x in raw]

    if isinstance(raw, dict):
        vals = []
        for key in LSTM_WEIGHT_NAMES:
            if key not in raw:
                return None
            vals.append(_safe_float(raw[key]))
        return vals

    return None


def _weights_to_dict(weights: list[float]) -> dict[str, float]:
    return {k: float(v) for k, v in zip(LSTM_WEIGHT_NAMES, weights)}


@dataclass
class RegionStats:
    capacity: int
    history: list[float]


def _load_region_stats(path: str) -> dict[str, RegionStats]:
    stats: dict[str, RegionStats] = {}
    slot_sets: dict[str, set[str]] = {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                region = row.get("region_id", "")
                slot = row.get("slot_id", "")
                occ_raw = row.get("occupied", "0")
                if not region:
                    continue
                occ = _safe_float(occ_raw, 0.0)
                stats.setdefault(region, RegionStats(capacity=0, history=[])).history.append(occ)
                slot_sets.setdefault(region, set()).add(slot)
    except FileNotFoundError:
        for region in ("R1", "R2", "R3"):
            stats[region] = RegionStats(capacity=20, history=[0.45, 0.52, 0.61, 0.58, 0.48, 0.42, 0.39, 0.44])
        return stats

    for region, st in stats.items():
        st.capacity = max(1, len(slot_sets.get(region, set())))
        if len(st.history) < 8:
            st.history = (st.history + [0.5] * 8)[:8]
        else:
            st.history = st.history[-64:]
    return stats


REGION_STATS = _load_region_stats(SLOT_STATUS_PATH)

_metrics_guard = threading.Lock()
_http_requests_total = 0
_http_error_total = 0
_model_activate_total = 0
_model_rollback_total = 0

_model_guard = threading.Lock()
_MODEL_REGISTRY: dict[str, dict[str, Any]] = {}
_ACTIVE_MODEL_VERSION = "v0.1-lstm-lite"
_MODEL_ACTIVATION_HISTORY: list[dict[str, Any]] = []


def _record_http_metrics(status_code: int) -> None:
    global _http_requests_total, _http_error_total
    with _metrics_guard:
        _http_requests_total += 1
        if status_code >= 400:
            _http_error_total += 1


def _increment_model_switch_metrics(operation: str) -> None:
    global _model_activate_total, _model_rollback_total
    with _metrics_guard:
        if operation == "rollback":
            _model_rollback_total += 1
        else:
            _model_activate_total += 1


def _metrics_text() -> str:
    with _metrics_guard:
        req_total = _http_requests_total
        err_total = _http_error_total
        activate_total = _model_activate_total
        rollback_total = _model_rollback_total

    with _model_guard:
        active_version = _ACTIVE_MODEL_VERSION

    lines = [
        "# HELP smart_parking_http_requests_total Total HTTP requests.",
        "# TYPE smart_parking_http_requests_total counter",
        f'smart_parking_http_requests_total{{service="{SERVICE_NAME}"}} {req_total}',
        "# HELP smart_parking_http_errors_total Total HTTP error responses.",
        "# TYPE smart_parking_http_errors_total counter",
        f'smart_parking_http_errors_total{{service="{SERVICE_NAME}"}} {err_total}',
        "# HELP smart_parking_model_activate_total Total model activate operations.",
        "# TYPE smart_parking_model_activate_total counter",
        f'smart_parking_model_activate_total{{service="{SERVICE_NAME}"}} {activate_total}',
        "# HELP smart_parking_model_rollback_total Total model rollback operations.",
        "# TYPE smart_parking_model_rollback_total counter",
        f'smart_parking_model_rollback_total{{service="{SERVICE_NAME}"}} {rollback_total}',
        "# HELP smart_parking_active_model_info Active model marker.",
        "# TYPE smart_parking_active_model_info gauge",
        f'smart_parking_active_model_info{{service="{SERVICE_NAME}",model_version="{active_version}"}} 1',
    ]
    return "\n".join(lines) + "\n"


def _predict_lstm(weights: list[float], history: list[float], horizon_minutes: int) -> float:
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
    for x in history[-16:]:
        i_gate = _sigmoid(w_ix * x + w_ih * h + b_i)
        f_gate = _sigmoid(w_fx * x + w_fh * h + b_f)
        o_gate = _sigmoid(w_ox * x + w_oh * h + b_o)
        g_gate = math.tanh(w_gx * x + w_gh * h + b_g)
        c = f_gate * c + i_gate * g_gate
        h = o_gate * math.tanh(c)

    horizon_factor = min(0.2, horizon_minutes / 240.0)
    ratio = _sigmoid(w_y * h + b_y + horizon_factor)
    return _clamp01(ratio)


def _predict_baseline(history: list[float], horizon_minutes: int) -> float:
    if not history:
        return 0.5
    base = history[-1]
    trend = (history[-1] - history[-2]) if len(history) > 1 else 0.0
    horizon_adjust = min(0.05, horizon_minutes / 1600.0)
    ratio = base + 0.2 * trend + horizon_adjust
    return _clamp01(ratio)


def _build_builtin_registry() -> dict[str, dict[str, Any]]:
    default_weights = _default_lstm_weights()
    return {
        "v0.1-lstm-lite": {
            "model_version": "v0.1-lstm-lite",
            "model_name": "lstm_lite",
            "predictor": "lstm_lite",
            "weights": default_weights,
            "source": "builtin",
            "created_at": _now_iso(),
        },
        "v0.2-lstm-lite": {
            "model_version": "v0.2-lstm-lite",
            "model_name": "lstm_lite",
            "predictor": "lstm_lite",
            "weights": default_weights,
            "source": "builtin",
            "created_at": _now_iso(),
        },
    }


def _discover_artifact_models(artifact_dir: Path) -> dict[str, dict[str, Any]]:
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
            weights = _canonicalize_lstm_weights(payload.get("weights"))
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


def _select_default_active(models: dict[str, dict[str, Any]]) -> str:
    if MODEL_ACTIVE_DEFAULT in models:
        return MODEL_ACTIVE_DEFAULT
    if "step12-lstm-lite-v1" in models:
        return "step12-lstm-lite-v1"
    if "v0.2-lstm-lite" in models:
        return "v0.2-lstm-lite"
    return sorted(models.keys())[0]


def _canonicalize_registry_payload(raw: dict[str, Any]) -> dict[str, Any]:
    models = _build_builtin_registry()
    models.update(_discover_artifact_models(Path(MODEL_ARTIFACT_DIR)))

    user_models = raw.get("models", {}) if isinstance(raw, dict) else {}
    if isinstance(user_models, dict):
        for version, spec in user_models.items():
            if not isinstance(spec, dict):
                continue
            version_str = str(version).strip() or str(spec.get("model_version", "")).strip()
            predictor = str(spec.get("predictor") or "").strip()
            model_name = str(spec.get("model_name") or "").strip()
            if not version_str:
                continue

            if not predictor:
                if model_name == "lstm_lite":
                    predictor = "lstm_lite"
                elif model_name == "baseline_last_value":
                    predictor = "baseline_last_value"

            if predictor == "lstm_lite":
                weights = _canonicalize_lstm_weights(spec.get("weights")) or _default_lstm_weights()
                models[version_str] = {
                    "model_version": version_str,
                    "model_name": "lstm_lite",
                    "predictor": "lstm_lite",
                    "weights": weights,
                    "source": str(spec.get("source") or "registry"),
                    "created_at": str(spec.get("created_at") or _now_iso()),
                }
            elif predictor == "baseline_last_value":
                models[version_str] = {
                    "model_version": version_str,
                    "model_name": "baseline_last_value",
                    "predictor": "baseline_last_value",
                    "source": str(spec.get("source") or "registry"),
                    "created_at": str(spec.get("created_at") or _now_iso()),
                }

    active = str(raw.get("active_version", "")).strip() if isinstance(raw, dict) else ""
    if active not in models:
        active = _select_default_active(models)

    history = raw.get("activation_history", []) if isinstance(raw, dict) else []
    if not isinstance(history, list):
        history = []
    history = history[-200:]

    return {
        "registry_version": "step13.v1",
        "generated_at": _now_iso(),
        "active_version": active,
        "models": models,
        "activation_history": history,
    }


def _persist_registry(payload: dict[str, Any]) -> None:
    out_path = Path(MODEL_REGISTRY_PATH)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(out_path)


def _snapshot_registry_payload() -> dict[str, Any]:
    with _model_guard:
        models: dict[str, dict[str, Any]] = {}
        for version, spec in _MODEL_REGISTRY.items():
            cloned = dict(spec)
            if cloned.get("predictor") == "lstm_lite":
                weights = _canonicalize_lstm_weights(cloned.get("weights")) or _default_lstm_weights()
                cloned["weights"] = weights
            models[version] = cloned

        return {
            "registry_version": "step13.v1",
            "generated_at": _now_iso(),
            "active_version": _ACTIVE_MODEL_VERSION,
            "models": models,
            "activation_history": list(_MODEL_ACTIVATION_HISTORY),
        }


def _initialize_registry() -> None:
    global _MODEL_REGISTRY, _ACTIVE_MODEL_VERSION, _MODEL_ACTIVATION_HISTORY

    payload: dict[str, Any] = {}
    registry_path = Path(MODEL_REGISTRY_PATH)
    if registry_path.exists():
        try:
            payload = json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}

    canonical = _canonicalize_registry_payload(payload)

    with _model_guard:
        _MODEL_REGISTRY = canonical["models"]
        _ACTIVE_MODEL_VERSION = canonical["active_version"]
        _MODEL_ACTIVATION_HISTORY = list(canonical["activation_history"])

    _persist_registry(canonical)


def _active_model() -> tuple[str, dict[str, Any], list[str]]:
    with _model_guard:
        if not _MODEL_REGISTRY:
            _MODEL_REGISTRY.update(_build_builtin_registry())
        active = _ACTIVE_MODEL_VERSION
        if active not in _MODEL_REGISTRY:
            active = _select_default_active(_MODEL_REGISTRY)
        spec = dict(_MODEL_REGISTRY[active])
        versions = sorted(_MODEL_REGISTRY.keys())
    return active, spec, versions


def _resolve_rollback_target() -> str | None:
    with _model_guard:
        current = _ACTIVE_MODEL_VERSION
        for event in reversed(_MODEL_ACTIVATION_HISTORY):
            from_v = str(event.get("from", "")).strip()
            to_v = str(event.get("to", "")).strip()
            if to_v == current and from_v in _MODEL_REGISTRY and from_v != current:
                return from_v
    return None


def _switch_model(target_version: str, trace_id: str, reason: str, operation: str) -> tuple[dict[str, Any] | None, str | None]:
    global _ACTIVE_MODEL_VERSION

    target = target_version.strip()
    if not target:
        return None, "missing_model_version"

    with _model_guard:
        if target not in _MODEL_REGISTRY:
            return None, "unknown_model_version"

        previous = _ACTIVE_MODEL_VERSION
        _ACTIVE_MODEL_VERSION = target

        _MODEL_ACTIVATION_HISTORY.append(
            {
                "ts": _now_iso(),
                "from": previous,
                "to": target,
                "operation": operation,
                "reason": reason,
                "trace_id": trace_id,
            }
        )
        if len(_MODEL_ACTIVATION_HISTORY) > 200:
            _MODEL_ACTIVATION_HISTORY[:] = _MODEL_ACTIVATION_HISTORY[-200:]

        available = sorted(_MODEL_REGISTRY.keys())

    _increment_model_switch_metrics(operation)
    _persist_registry(_snapshot_registry_payload())

    return (
        {
            "model_version": target,
            "previous_version": previous,
            "available_versions": available,
            "operation": operation,
            "switched_at": _now_iso(),
            "trace_id": trace_id,
        },
        None,
    )


def _predict_ratio(history: list[float], horizon_minutes: int, model_spec: dict[str, Any]) -> float:
    predictor = str(model_spec.get("predictor", "lstm_lite"))

    if predictor == "baseline_last_value":
        return _predict_baseline(history, horizon_minutes)

    weights = _canonicalize_lstm_weights(model_spec.get("weights")) or _default_lstm_weights()
    return _predict_lstm(weights, history, horizon_minutes)


def _forecast(region_id: str, horizon_minutes: int) -> dict[str, Any]:
    st = REGION_STATS.get(region_id) or RegionStats(capacity=20, history=[0.5] * 16)
    active_version, model_spec, _ = _active_model()

    ratio = _predict_ratio(st.history, horizon_minutes, model_spec)

    demand = float(round(st.capacity * ratio, 4))
    supply = float(round(max(0.0, st.capacity - demand), 4))
    gap = float(round(supply - demand, 4))

    ts = datetime.now(timezone.utc) + timedelta(minutes=horizon_minutes)
    return {
        "region_id": region_id,
        "ts": ts.isoformat(),
        "supply": supply,
        "demand": demand,
        "gap": gap,
        "model_version": active_version,
    }


def _location_to_region(location: str) -> str:
    if not location:
        return "R1"
    token = location.split("-")[0].strip().upper()
    return token if token else "R1"


def _slot_pool(requests: list[dict[str, Any]]) -> list[str]:
    regions = []
    for req in requests:
        r = _location_to_region(str(req.get("location", "R1")))
        if r not in regions:
            regions.append(r)
    if not regions:
        regions = ["R1", "R2", "R3"]

    pool = []
    for r in regions:
        for i in range(1, 7):
            pool.append(f"{r}-S{i:03d}")

    while len(pool) < len(requests):
        idx = len(pool) + 1
        pool.append(f"R1-S{idx:03d}")
    return pool


def _stable_unit(seed: str) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big")
    return value / float((1 << 64) - 1)


def _slot_index(slot_id: str) -> int:
    try:
        suffix = slot_id.split("-S", 1)[1]
        return max(1, int(suffix))
    except Exception:
        return 1


def _region_factor(region: str) -> float:
    return {"R1": 1.18, "R2": 1.0, "R3": 0.92}.get(region, 1.0)


def _cost(req: dict[str, Any], slot_id: str) -> tuple[float, float, float]:
    order_id = str(req.get("order_id", ""))
    region = _location_to_region(str(req.get("location", "R1")))
    slot_region = slot_id.split("-")[0]
    region_penalty = 0.0 if region == slot_region else 3.6
    slot_idx = _slot_index(slot_id)

    distance = round(0.9 + region_penalty + (slot_idx % 11) * 0.17 + 0.8 * _stable_unit(f"{order_id}|{slot_id}|distance"), 4)
    congestion = round(0.2 + 0.65 * _stable_unit(f"{slot_id}|congestion"), 4)
    price = round((5.2 + (slot_idx % 5) * 0.55 + 0.45 * _stable_unit(f"{slot_id}|price")) * _region_factor(slot_region), 2)

    total = round(0.55 * distance + 1.8 * congestion + 0.2 * price, 6)
    return total, distance, price


def _hungarian_assign(cost_matrix: list[list[float]]) -> list[int]:
    if not cost_matrix:
        return []

    row_count = len(cost_matrix)
    col_count = len(cost_matrix[0]) if cost_matrix[0] else 0
    if col_count == 0:
        return [-1] * row_count

    size = max(row_count, col_count)
    padded = [[0.0] * (size + 1) for _ in range(size + 1)]
    for i in range(row_count):
        for j in range(col_count):
            padded[i + 1][j + 1] = cost_matrix[i][j]

    u = [0.0] * (size + 1)
    v = [0.0] * (size + 1)
    p = [0] * (size + 1)
    way = [0] * (size + 1)

    for i in range(1, size + 1):
        p[0] = i
        j0 = 0
        minv = [float("inf")] * (size + 1)
        used = [False] * (size + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = float("inf")
            j1 = 0
            for j in range(1, size + 1):
                if used[j]:
                    continue
                cur = padded[i0][j] - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j] = cur
                    way[j] = j0
                if minv[j] < delta:
                    delta = minv[j]
                    j1 = j
            for j in range(size + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    assignment = [-1] * row_count
    for j in range(1, size + 1):
        if 1 <= p[j] <= row_count and j <= col_count:
            assignment[p[j] - 1] = j - 1
    return assignment


def _optimize(requests: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    if not requests:
        return [], "hungarian_optimal"

    pool = _slot_pool(requests)
    cost_matrix = [[_cost(req, slot)[0] for slot in pool] for req in requests]
    assignment = _hungarian_assign(cost_matrix)
    strategy = "hungarian_optimal"

    results: list[dict[str, Any]] = []
    for idx, req in enumerate(requests):
        slot_idx = assignment[idx]
        if slot_idx < 0 or slot_idx >= len(pool):
            raise RuntimeError("hungarian assignment incomplete")
        slot = pool[slot_idx]
        total, distance, price = _cost(req, slot)
        eta = max(2.0, round(distance * 2.35, 2))
        score = round(1.0 / (1.0 + total), 6)
        results.append(
            {
                "order_id": str(req.get("order_id", "")),
                "slot_id": slot,
                "score": score,
                "eta": eta,
                "price": round(price, 2),
                "strategy": strategy,
            }
        )

    return results, strategy


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict[str, Any], trace_id: str) -> None:
        _record_http_metrics(code)
        print(
            json.dumps(
                {
                    "service": SERVICE_NAME,
                    "path": self.path,
                    "status": code,
                    "trace_id": trace_id,
                    "ts": time.time(),
                },
                ensure_ascii=False,
            )
        )
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Trace-Id", trace_id)
        self.end_headers()
        self.wfile.write(body)

    def _text(self, code: int, payload: str, trace_id: str) -> None:
        _record_http_metrics(code)
        print(
            json.dumps(
                {
                    "service": SERVICE_NAME,
                    "path": self.path,
                    "status": code,
                    "trace_id": trace_id,
                    "ts": time.time(),
                },
                ensure_ascii=False,
            )
        )
        body = payload.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Trace-Id", trace_id)
        self.end_headers()
        self.wfile.write(body)

    def _trace_id(self) -> str:
        return self.headers.get("X-Trace-Id", f"trace-{int(time.time() * 1000)}")

    def _read_json(self) -> dict[str, Any]:
        cl = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(cl) if cl > 0 else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self) -> None:
        trace_id = self._trace_id()

        if self.path == "/metrics":
            self._text(200, _metrics_text(), trace_id)
            return

        if self.path == "/actuator/health":
            active_version, _, versions = _active_model()
            self._json(
                200,
                {
                    "status": "UP",
                    "service": SERVICE_NAME,
                    "model_version": active_version,
                    "registry_size": len(versions),
                },
                trace_id,
            )
            return

        if self.path == "/internal/v1/model/registry":
            payload = _snapshot_registry_payload()
            models_summary = [
                {
                    "model_version": v,
                    "predictor": str(spec.get("predictor", "unknown")),
                    "source": str(spec.get("source", "")),
                }
                for v, spec in sorted(payload["models"].items())
            ]
            self._json(
                200,
                {
                    "active_version": payload["active_version"],
                    "available_versions": [m["model_version"] for m in models_summary],
                    "models": models_summary,
                    "activation_history_size": len(payload.get("activation_history", [])),
                },
                trace_id,
            )
            return

        self._json(404, {"error": "route_not_found"}, trace_id)

    def do_POST(self) -> None:
        trace_id = self._trace_id()
        body = self._read_json()

        if self.path == "/internal/v1/model/predict":
            region_ids = body.get("region_ids") or ["R1", "R2", "R3"]
            horizon = int(body.get("horizon_minutes", 30))
            records = []
            for region in region_ids:
                rec = _forecast(str(region), horizon)
                rec.pop("model_version", None)
                records.append(rec)
            active_version, _, _ = _active_model()
            self._json(200, {"records": records, "model_version": active_version}, trace_id)
            return

        if self.path == "/internal/v1/dispatch/optimize":
            requests = body.get("requests") or []
            results, strategy = _optimize(requests)
            active_version, _, _ = _active_model()
            self._json(200, {"results": results, "strategy": strategy, "model_version": active_version}, trace_id)
            return

        if self.path == "/internal/v1/model/activate":
            action = str(body.get("action", "")).strip().lower()
            rollback = bool(body.get("rollback", False)) or action == "rollback"
            reason = str(body.get("reason", "")).strip()

            if rollback:
                target = str(body.get("rollback_to", "")).strip()
                if not target:
                    target = _resolve_rollback_target() or ""
                if not target:
                    self._json(409, {"error": "no_rollback_target"}, trace_id)
                    return
                payload, err = _switch_model(target, trace_id, reason or "rollback", "rollback")
                if err:
                    _, _, versions = _active_model()
                    self._json(400, {"error": err, "available_versions": versions}, trace_id)
                    return
                assert payload is not None
                payload["status"] = "rolled_back"
                self._json(200, payload, trace_id)
                return

            model_version = str(body.get("model_version", "")).strip()
            if not model_version:
                self._json(400, {"error": "missing_model_version"}, trace_id)
                return

            payload, err = _switch_model(model_version, trace_id, reason or "activate", "activate")
            if err:
                _, _, versions = _active_model()
                self._json(400, {"error": err, "available_versions": versions}, trace_id)
                return
            assert payload is not None
            payload["status"] = "active"
            self._json(200, payload, trace_id)
            return

        self._json(404, {"error": "route_not_found"}, trace_id)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    _initialize_registry()
    active_version, _, versions = _active_model()
    print(
        f"{SERVICE_NAME} listening on {PORT}, active_model={active_version}, "
        f"registry_size={len(versions)}, registry_path={MODEL_REGISTRY_PATH}"
    )
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
