#!/usr/bin/env python3
"""Step 15 gate: gateway governance alignment with fallback semantics."""

from __future__ import annotations

import json
import time
import urllib.request
from urllib.error import HTTPError

GATEWAY = "http://localhost:8080"


def _header_ci(headers: dict, key: str) -> str:
    target = key.lower()
    for k, v in headers.items():
        if k.lower() == target:
            return v
    return ""


def request(path: str, method: str = "GET", body: dict | None = None, headers: dict | None = None):
    data = None
    h = headers.copy() if headers else {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(GATEWAY + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = resp.read().decode("utf-8")
            return resp.status, dict(resp.headers), json.loads(payload) if payload else {}
    except HTTPError as ex:
        payload = ex.read().decode("utf-8")
        try:
            data = json.loads(payload) if payload else {}
        except Exception:  # noqa: BLE001
            data = {"error": payload[:120]}
        return ex.code, dict(ex.headers), data


def wait_gateway() -> None:
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            s, _, body = request("/actuator/health")
            if s == 200 and body.get("status") == "UP":
                return
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    raise RuntimeError("gateway health timeout")


def assert_fallback(payload: dict):
    assert payload.get("fallback_reason") == "model_service_unavailable", payload
    assert payload.get("fallback_strategy") == "default_rule", payload
    assert payload.get("trace_id"), payload


def main() -> None:
    wait_gateway()

    # model-service should be stopped externally before this script runs.
    s1, h1, p1 = request(
        "/internal/v1/model/predict",
        method="POST",
        body={"region_ids": ["R1"], "horizon_minutes": 30},
    )
    assert s1 == 200, (s1, p1)
    assert_fallback(p1)
    assert _header_ci(h1, "X-Trace-Id"), h1
    assert _header_ci(h1, "X-Trace-Id") == p1.get("trace_id"), (h1, p1)

    s2, h2, p2 = request(
        "/internal/v1/dispatch/optimize",
        method="POST",
        body={
            "requests": [
                {
                    "order_id": "O-step15-001",
                    "user_id": "U-step15-001",
                    "preferred_window": "2026-03-13T12:00/12:30",
                    "location": "R1",
                    "constraints": {},
                }
            ]
        },
    )
    assert s2 == 200, (s2, p2)
    assert_fallback(p2)
    assert _header_ci(h2, "X-Trace-Id"), h2
    assert _header_ci(h2, "X-Trace-Id") == p2.get("trace_id"), (h2, p2)

    s3, _, p3 = request("/actuator/circuitbreakers")
    assert s3 == 200, (s3, p3)
    names = set(p3.get("circuitBreakers", []))
    assert "modelServiceCb" in names, p3

    print("STEP15_GATE_PASS")


if __name__ == "__main__":
    main()
