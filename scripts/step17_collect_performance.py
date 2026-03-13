#!/usr/bin/env python3
"""Collect Step17 performance metrics (P95/P99/error rate/throughput)."""

from __future__ import annotations

import argparse
import json
import math
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError

GATEWAY = "http://localhost:8080"


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    seq = sorted(values)
    idx = max(0, min(len(seq) - 1, math.ceil((p / 100.0) * len(seq)) - 1))
    return float(seq[idx])


def request_predict(index: int, scenario: str, timeout_s: float = 8.0) -> dict:
    payload = {
        "region_ids": ["R1", "R2", "R3"],
        "horizon_minutes": 30,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Trace-Id": f"step17-{scenario}-{index}-{int(time.time() * 1000)}",
    }
    req = urllib.request.Request(
        GATEWAY + "/internal/v1/model/predict",
        data=body,
        headers=headers,
        method="POST",
    )

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            payload_obj = json.loads(raw) if raw else {}
            status = resp.status
    except HTTPError as ex:
        raw = ex.read().decode("utf-8")
        payload_obj = json.loads(raw) if raw else {}
        status = ex.code
    except (URLError, TimeoutError, ConnectionError) as ex:
        payload_obj = {"error": str(ex)}
        status = 599

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return {
        "status": status,
        "latency_ms": elapsed_ms,
        "fallback": payload_obj.get("fallback_reason") == "model_service_unavailable",
    }


def run_load(scenario: str, total_requests: int, concurrency: int, warmup: int) -> dict:
    for i in range(warmup):
        request_predict(i, scenario)

    started = time.perf_counter()
    records: list[dict] = []
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(request_predict, i, scenario) for i in range(total_requests)]
        for future in as_completed(futures):
            records.append(future.result())
    elapsed = max(0.001, time.perf_counter() - started)

    latencies = [float(r["latency_ms"]) for r in records]
    errors = [r for r in records if int(r["status"]) >= 400]
    fallback_hits = [r for r in records if r["fallback"]]

    summary = {
        "scenario": scenario,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_requests": len(records),
        "concurrency": concurrency,
        "warmup": warmup,
        "throughput_rps": round(len(records) / elapsed, 4),
        "error_count": len(errors),
        "error_rate": round(len(errors) / max(1, len(records)), 6),
        "fallback_count": len(fallback_hits),
        "fallback_rate": round(len(fallback_hits) / max(1, len(records)), 6),
        "latency_ms": {
            "min": round(min(latencies) if latencies else 0.0, 4),
            "avg": round(sum(latencies) / max(1, len(latencies)), 4),
            "p50": round(percentile(latencies, 50), 4),
            "p95": round(percentile(latencies, 95), 4),
            "p99": round(percentile(latencies, 99), 4),
            "max": round(max(latencies) if latencies else 0.0, 4),
        },
    }
    return summary


def wait_gateway(timeout: int = 120) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = urllib.request.Request(GATEWAY + "/actuator/health", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                if resp.status == 200 and body.get("status") == "UP":
                    return
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    raise RuntimeError("gateway health timeout")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=["baseline", "fault", "recovery"])
    parser.add_argument("--requests", type=int, default=300)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--output", default="reports/step17_perf_baseline.json")
    args = parser.parse_args()

    wait_gateway()
    summary = run_load(args.scenario, args.requests, args.concurrency, args.warmup)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"STEP17_PERF_{args.scenario.upper()}_PASS output={out_path}")


if __name__ == "__main__":
    main()
