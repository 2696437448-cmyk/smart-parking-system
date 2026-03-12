#!/usr/bin/env python3
"""Step 5 model service: lightweight LSTM-like forecast + assignment optimization."""

from __future__ import annotations

import csv
import json
import math
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import combinations, permutations
from typing import Any

SERVICE_NAME = os.getenv("SERVICE_NAME", "model-service")
PORT = int(os.getenv("PORT", "8000"))
SLOT_STATUS_PATH = os.getenv("SLOT_STATUS_PATH", "/app/../data/raw/slot_status.csv")

ACTIVE_MODEL_VERSION = "v0.1-lstm-lite"

_metrics_guard = threading.Lock()
_http_requests_total = 0
_http_error_total = 0
_model_activate_total = 0


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(min(x, 30.0), -30.0)))


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
                try:
                    occ = float(occ_raw)
                except Exception:  # noqa: BLE001
                    occ = 0.0
                stats.setdefault(region, RegionStats(capacity=0, history=[])).history.append(occ)
                slot_sets.setdefault(region, set()).add(slot)
    except FileNotFoundError:
        # fallback small defaults
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


def _record_http_metrics(status_code: int) -> None:
    global _http_requests_total, _http_error_total
    with _metrics_guard:
        _http_requests_total += 1
        if status_code >= 400:
            _http_error_total += 1


def _metrics_text() -> str:
    with _metrics_guard:
        req_total = _http_requests_total
        err_total = _http_error_total
        activate_total = _model_activate_total

    lines = [
        "# HELP smart_parking_http_requests_total Total HTTP requests.",
        "# TYPE smart_parking_http_requests_total counter",
        f"smart_parking_http_requests_total{{service=\"{SERVICE_NAME}\"}} {req_total}",
        "# HELP smart_parking_http_errors_total Total HTTP error responses.",
        "# TYPE smart_parking_http_errors_total counter",
        f"smart_parking_http_errors_total{{service=\"{SERVICE_NAME}\"}} {err_total}",
        "# HELP smart_parking_model_activate_total Total model activation calls.",
        "# TYPE smart_parking_model_activate_total counter",
        f"smart_parking_model_activate_total{{service=\"{SERVICE_NAME}\"}} {activate_total}",
    ]
    return "\n".join(lines) + "\n"


def _predict_occupancy_ratio(history: list[float], horizon_minutes: int) -> float:
    # Lightweight LSTM-like recurrence with fixed small weights.
    h = 0.0
    c = 0.0
    for x in history[-16:]:
        i = _sigmoid(0.9 * x + 0.3 * h - 0.2)
        f = _sigmoid(0.6 * x + 0.4 * h + 0.1)
        o = _sigmoid(0.7 * x + 0.2 * h - 0.05)
        g = math.tanh(0.8 * x + 0.35 * h)
        c = f * c + i * g
        h = o * math.tanh(c)

    horizon_factor = min(0.2, horizon_minutes / 240.0)
    ratio = _sigmoid(1.8 * h + 0.5 * horizon_factor)
    return max(0.02, min(0.98, ratio))


def _forecast(region_id: str, horizon_minutes: int) -> dict[str, Any]:
    st = REGION_STATS.get(region_id) or RegionStats(capacity=20, history=[0.5] * 16)
    ratio = _predict_occupancy_ratio(st.history, horizon_minutes)

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
    # add fallback slots if n is big
    while len(pool) < len(requests):
        idx = len(pool) + 1
        pool.append(f"R1-S{idx:03d}")
    return pool


def _cost(req: dict[str, Any], slot_id: str) -> tuple[float, float, float]:
    order_id = str(req.get("order_id", ""))
    region = _location_to_region(str(req.get("location", "R1")))
    slot_region = slot_id.split("-")[0]
    region_penalty = 0.0 if region == slot_region else 4.0

    distance = (abs(hash(order_id + slot_id)) % 700) / 100.0 + region_penalty
    congestion = (abs(hash(slot_id + "cg")) % 500) / 100.0
    price = 5.0 + (abs(hash(slot_id + "pr")) % 400) / 100.0

    total = 0.5 * distance + 0.3 * congestion + 0.2 * price
    return total, distance, price


def _optimize(requests: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    n = len(requests)
    if n == 0:
        return [], "hungarian_bruteforce"

    pool = _slot_pool(requests)

    best_perm = None
    best_score = float("inf")

    strategy = "hungarian_bruteforce"
    if n <= 7:
        # brute-force assignment over combinations + permutations, suitable for demo scale.
        for chosen in combinations(pool, n):
            for perm in permutations(chosen):
                score = 0.0
                for req, slot in zip(requests, perm):
                    c, _, _ = _cost(req, slot)
                    score += c
                if score < best_score:
                    best_score = score
                    best_perm = perm
    else:
        # fallback for larger N
        strategy = "greedy_fallback"
        available = pool.copy()
        chosen = []
        for req in requests:
            available.sort(key=lambda s: _cost(req, s)[0])
            chosen_slot = available.pop(0)
            chosen.append(chosen_slot)
        best_perm = tuple(chosen)

    results: list[dict[str, Any]] = []
    assert best_perm is not None
    for req, slot in zip(requests, best_perm):
        total, distance, price = _cost(req, slot)
        eta = max(2.0, round(distance * 2.6, 2))
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
        return self.headers.get("X-Trace-Id", f"trace-{int(time.time()*1000)}")

    def _read_json(self) -> dict[str, Any]:
        cl = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(cl) if cl > 0 else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:  # noqa: BLE001
            return {}

    def do_GET(self) -> None:
        trace_id = self._trace_id()
        if self.path == "/metrics":
            self._text(200, _metrics_text(), trace_id)
            return
        if self.path == "/actuator/health":
            self._json(200, {"status": "UP", "service": SERVICE_NAME, "model_version": ACTIVE_MODEL_VERSION}, trace_id)
            return
        self._json(404, {"error": "route_not_found"}, trace_id)

    def do_POST(self) -> None:
        global ACTIVE_MODEL_VERSION
        trace_id = self._trace_id()
        body = self._read_json()

        if self.path == "/internal/v1/model/predict":
            region_ids = body.get("region_ids") or ["R1", "R2", "R3"]
            horizon = int(body.get("horizon_minutes", 30))
            records = [_forecast(str(r), horizon) for r in region_ids]
            self._json(200, {"records": records, "model_version": ACTIVE_MODEL_VERSION}, trace_id)
            return

        if self.path == "/internal/v1/dispatch/optimize":
            requests = body.get("requests") or []
            results, strategy = _optimize(requests)
            self._json(200, {"results": results, "strategy": strategy, "model_version": ACTIVE_MODEL_VERSION}, trace_id)
            return

        if self.path == "/internal/v1/model/activate":
            model_version = str(body.get("model_version", "")).strip()
            if not model_version:
                self._json(400, {"error": "missing_model_version"}, trace_id)
                return
            ACTIVE_MODEL_VERSION = model_version
            global _model_activate_total
            with _metrics_guard:
                _model_activate_total += 1
            self._json(200, {"model_version": ACTIVE_MODEL_VERSION, "status": "active"}, trace_id)
            return

        self._json(404, {"error": "route_not_found"}, trace_id)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"{SERVICE_NAME} listening on {PORT}, model={ACTIVE_MODEL_VERSION}")
    server.serve_forever()


if __name__ == "__main__":
    main()
