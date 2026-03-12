#!/usr/bin/env python3
"""Step 6 gate: fallback response when model-service is down."""

from __future__ import annotations

import json
import time
import urllib.request
from urllib.error import HTTPError

GATEWAY = "http://localhost:8080"


def request(path: str, method: str = "POST", body: dict | None = None, headers: dict | None = None):
    data = None
    h = headers.copy() if headers else {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(GATEWAY + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, dict(resp.headers), json.loads(resp.read().decode("utf-8"))
    except HTTPError as ex:
        try:
            payload = json.loads(ex.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            payload = {"error": "unknown"}
        return ex.code, dict(ex.headers), payload


def wait_gateway() -> None:
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            s, _, body = request("/actuator/health", "GET")
            if s == 200 and body.get("status") == "UP":
                return
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    raise RuntimeError("gateway health timeout")


def assert_fallback(payload: dict):
    assert payload.get("fallback_reason") == "model_service_unavailable", f"missing fallback_reason: {payload}"
    assert payload.get("fallback_strategy") == "default_rule", f"missing fallback_strategy: {payload}"
    assert payload.get("trace_id"), f"missing trace_id: {payload}"


def main() -> None:
    wait_gateway()

    # model-service is expected to be stopped externally before running this script.
    s1, _, p1 = request(
        "/internal/v1/model/predict",
        "POST",
        {"region_ids": ["R1"], "horizon_minutes": 30},
    )
    assert s1 == 200, f"fallback predict status unexpected: {s1}, {p1}"
    assert_fallback(p1)

    s2, _, p2 = request(
        "/internal/v1/dispatch/optimize",
        "POST",
        {
            "requests": [
                {"order_id": "O-100", "user_id": "U-100", "preferred_window": "2026-03-12T12:00/12:30", "location": "R1", "constraints": {}},
            ]
        },
    )
    assert s2 == 200, f"fallback optimize status unexpected: {s2}, {p2}"
    assert_fallback(p2)

    print("STEP6_GATE_PASS")


if __name__ == "__main__":
    main()
