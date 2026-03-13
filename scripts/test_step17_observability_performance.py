#!/usr/bin/env python3
"""Step17 gate: verify observability three views and performance evidence outputs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")


def main() -> None:
    dashboards = [
        ROOT / "infra" / "grafana" / "dashboards" / "step17-normal-state.json",
        ROOT / "infra" / "grafana" / "dashboards" / "step17-fault-state.json",
        ROOT / "infra" / "grafana" / "dashboards" / "step17-recovery-state.json",
    ]
    for d in dashboards:
        assert_exists(d)
        payload = load_json(d)
        if "Step17" not in payload.get("title", ""):
            raise AssertionError(f"dashboard title not aligned: {d}")

    baseline = load_json(ROOT / "reports" / "step17_perf_baseline.json")
    fault = load_json(ROOT / "reports" / "step17_perf_fault.json")
    recovery = load_json(ROOT / "reports" / "step17_perf_recovery.json")

    for report in (baseline, fault, recovery):
        if report.get("total_requests", 0) < 100:
            raise AssertionError(f"insufficient requests in scenario: {report.get('scenario')} -> {report.get('total_requests')}")
        if report.get("throughput_rps", 0) <= 0:
            raise AssertionError(f"invalid throughput for scenario: {report.get('scenario')}")
        for key in ("p95", "p99"):
            if report.get("latency_ms", {}).get(key, 0) <= 0:
                raise AssertionError(f"invalid {key} for scenario: {report.get('scenario')}")

    if fault.get("fallback_rate", 0) <= 0.2:
        raise AssertionError(f"fault scenario fallback rate too low: {fault.get('fallback_rate')}")

    assert_exists(ROOT / "reports" / "step17_performance_summary.md")
    assert_exists(ROOT / "reports" / "step17_performance_summary.csv")

    print("STEP17_GATE_PASS")


if __name__ == "__main__":
    main()
