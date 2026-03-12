#!/usr/bin/env python3
"""Step 9 gate: verify observability baseline and fault transitions."""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request


def http_json(url: str, method: str = "GET", body: dict | None = None) -> tuple[int, dict]:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=8) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def prom_query(prom_url: str, expr: str) -> list[dict]:
    query = urllib.parse.urlencode({"query": expr})
    url = f"{prom_url.rstrip('/')}/api/v1/query?{query}"
    with urllib.request.urlopen(url, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("status") != "success":
        raise RuntimeError(f"prom query failed: {payload}")
    return payload.get("data", {}).get("result", [])


def metric_value(results: list[dict], match_labels: dict[str, str]) -> float | None:
    for item in results:
        labels = item.get("metric", {})
        if all(labels.get(k) == v for k, v in match_labels.items()):
            value = item.get("value", [None, None])[1]
            if value is None:
                return None
            return float(value)
    return None


def wait_for_prometheus(prom_url: str, timeout: int = 60) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{prom_url.rstrip('/')}/-/ready", timeout=5) as resp:
                if resp.status == 200:
                    return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("prometheus not ready within timeout")


def wait_up_state(prom_url: str, job: str, expected: float, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        results = prom_query(prom_url, f'up{{job="{job}"}}')
        val = metric_value(results, {"job": job})
        if val is not None and val == expected:
            return
        time.sleep(1)
    raise RuntimeError(f"up metric not reaching expected state: job={job}, expected={expected}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["baseline", "fault"], required=True)
    parser.add_argument("--prom-url", default="http://localhost:9090")
    parser.add_argument("--gateway-url", default="http://localhost:8080")
    args = parser.parse_args()

    wait_for_prometheus(args.prom_url)

    if args.mode == "baseline":
        # Generate a small amount of runtime traffic first.
        status, _ = http_json(
            args.gateway_url.rstrip("/") + "/internal/v1/model/predict",
            method="POST",
            body={"region_ids": ["R1", "R2"], "horizon_minutes": 30},
        )
        if status != 200:
            raise RuntimeError(f"baseline traffic generation failed: status={status}")

        wait_up_state(args.prom_url, "parking-service", 1.0)
        wait_up_state(args.prom_url, "model-service", 1.0)
        wait_up_state(args.prom_url, "realtime-service", 1.0)
        print("STEP9_BASELINE_OK")
        return

    # fault mode: model-service is expected to be stopped externally.
    wait_up_state(args.prom_url, "model-service", 0.0)
    wait_up_state(args.prom_url, "parking-service", 1.0)

    results = prom_query(args.prom_url, 'smart_parking_http_requests_total{service="parking-service"}')
    if not results:
        raise RuntimeError("parking-service request metric missing")
    print("STEP9_GATE_PASS")


if __name__ == "__main__":
    main()
