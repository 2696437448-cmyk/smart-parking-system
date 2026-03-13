#!/usr/bin/env python3
"""Step 3 gate tests: health and route forwarding via gateway."""

from __future__ import annotations

import json
import time
import urllib.request
from urllib.error import URLError, HTTPError




def _header_ci(headers: dict, key: str) -> str:
    target = key.lower()
    for k, v in headers.items():
        if k.lower() == target:
            return v
    return ""

def request(url: str, method: str = "GET", body: dict | None = None, headers: dict | None = None):
    data = None
    req_headers = headers or {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers = {**req_headers, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, dict(resp.headers), resp.read().decode("utf-8")


def wait_gateway() -> None:
    deadline = time.time() + 60
    last = None
    while time.time() < deadline:
        try:
            status, _, body = request("http://localhost:8080/actuator/health")
            if status == 200 and '"status":"UP"' in body:
                return
        except (URLError, HTTPError) as ex:
            last = ex
        time.sleep(1)
    raise RuntimeError(f"gateway health check timeout, last={last}")


def main() -> None:
    wait_gateway()

    s1, h1, b1 = request(
        "http://localhost:8080/api/v1/owner/reservations",
        method="POST",
        body={"user_id": "U0001", "preferred_window": "2026-03-11T09:00/09:30", "location": "R1"},
        headers={"Idempotency-Key": "idem-001"},
    )
    j1 = json.loads(b1)
    assert s1 == 200, f"owner route status invalid: {s1}"
    assert j1.get("service") == "parking-service", f"owner route not forwarded to parking-service: {j1}"
    assert _header_ci(h1, "X-Trace-Id"), "missing X-Trace-Id in owner route response"

    s2, h2, b2 = request(
        "http://localhost:8080/internal/v1/model/predict",
        method="POST",
        body={"region_ids": ["R1", "R2"], "horizon_minutes": 30},
    )
    j2 = json.loads(b2)
    assert s2 == 200, f"model route status invalid: {s2}"
    assert isinstance(j2.get("records"), list), f"model route payload invalid: {j2}"
    assert j2.get("model_version"), f"model route missing model_version: {j2}"
    assert _header_ci(h2, "X-Trace-Id"), "missing X-Trace-Id in model route response"

    print("STEP3_GATE_PASS")


if __name__ == "__main__":
    main()
