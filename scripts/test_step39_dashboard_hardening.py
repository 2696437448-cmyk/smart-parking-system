#!/usr/bin/env python3
"""Step39 gate: dashboard backend modularization and frontend hardening."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"
REPORT_PATH = ROOT / "reports" / "step39_gate_results.json"
GATEWAY = "http://localhost:8080"


def run(cmd: str, cwd: Path | None = None, timeout: int = 1800) -> tuple[bool, str, float]:
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, output, time.time() - started


def assert_tokens(path: Path, tokens: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{path} missing token: {token}")


def request(path: str):
    req = urllib.request.Request(GATEWAY + path, headers={"X-Trace-Id": f"step39-{uuid.uuid4().hex[:8]}"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return resp.status, payload, dict(resp.headers.items())
    except HTTPError as ex:
        payload = json.loads(ex.read().decode("utf-8"))
        return ex.code, payload, dict(ex.headers.items())


def gateway_ready() -> bool:
    try:
        with urllib.request.urlopen(GATEWAY + "/actuator/health", timeout=4) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return resp.status == 200 and payload.get("status") == "UP"
    except (URLError, OSError, json.JSONDecodeError):
        return False


def runtime_owner_query() -> str:
    shanghai = timezone(timedelta(hours=8))
    start_dt = datetime.now(shanghai).replace(second=0, microsecond=0) + timedelta(minutes=60)
    end_dt = start_dt + timedelta(minutes=30)
    return urllib.parse.urlencode(
        {
            "location": "R1",
            "preferred_window": f"{start_dt.isoformat()}/{end_dt.isoformat()}",
            "user_id": "owner-step39-smoke",
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-runtime", action="store_true", help="Fail if the gateway runtime smoke cannot be executed.")
    args = parser.parse_args()

    steps: list[dict[str, object]] = []

    ok, output, elapsed = run("python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml")
    steps.append(
        {
            "name": "openapi_validation",
            "command": "python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml",
            "passed": ok,
            "elapsed_seconds": round(elapsed, 3),
            "output_tail": "\n".join(output.splitlines()[-10:]),
        }
    )
    if not ok:
        REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"STEP39_GATE_FAIL failed=openapi_validation report={REPORT_PATH}")
        raise SystemExit(1)

    backend_files = [
        ROOT / "services" / "parking-service" / "src" / "main" / "java" / "com" / "smartparking" / "parking" / "ParkingDashboardViewController.java",
        ROOT / "services" / "parking-service" / "src" / "main" / "java" / "com" / "smartparking" / "parking" / "ParkingDashboardViewModules.java",
    ]
    for path in backend_files:
        exists = path.exists()
        steps.append({"name": f"exists:{path.relative_to(ROOT)}", "passed": exists, "elapsed_seconds": 0.0})
        if not exists:
            REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"STEP39_GATE_FAIL failed=exists:{path.relative_to(ROOT)} report={REPORT_PATH}")
            raise SystemExit(1)

    assert_tokens(
        backend_files[0],
        ["/api/v1/owner/dashboard", "/api/v1/admin/dashboard", "DashboardViewService", "trace_id", "service"],
    )
    assert_tokens(
        backend_files[1],
        ["class DashboardQueryService", "class OwnerDashboardAssembler", "class AdminDashboardAssembler", "class DashboardViewService"],
    )
    steps.append({"name": "backend_dashboard_modules", "passed": True, "elapsed_seconds": 0.0})

    ok, output, elapsed = run("npm run typecheck", cwd=FRONTEND, timeout=1200)
    steps.append(
        {
            "name": "frontend_typecheck",
            "command": "npm run typecheck",
            "passed": ok,
            "elapsed_seconds": round(elapsed, 3),
            "output_tail": "\n".join(output.splitlines()[-10:]),
        }
    )
    if not ok:
        REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"STEP39_GATE_FAIL failed=frontend_typecheck report={REPORT_PATH}")
        raise SystemExit(1)

    ok, output, elapsed = run("npm run build", cwd=FRONTEND, timeout=1800)
    warning_free = ok and "Some chunks are larger than 500 kB" not in output
    steps.append(
        {
            "name": "frontend_build_warning_free",
            "command": "npm run build",
            "passed": warning_free,
            "elapsed_seconds": round(elapsed, 3),
            "output_tail": "\n".join(output.splitlines()[-14:]),
        }
    )
    if not warning_free:
        REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"STEP39_GATE_FAIL failed=frontend_build_warning_free report={REPORT_PATH}")
        raise SystemExit(1)

    assert_tokens(FRONTEND / "src" / "services" / "http.ts", ["HttpRequestError", "traceId", "invalid_json_response"])
    assert_tokens(FRONTEND / "src" / "composables" / "useRealtimeChannel.ts", ["pollInFlight", "scheduleReconnect", "stopPolling"])
    assert_tokens(FRONTEND / "vite.config.ts", ["vendor-zrender", "vendor-echarts", "vendor-leaflet", "vendor-vue"])
    steps.append({"name": "frontend_hardening_sources", "passed": True, "elapsed_seconds": 0.0})

    if gateway_ready():
        owner_status, owner_payload, owner_headers = request(f"/api/v1/owner/dashboard?{runtime_owner_query()}")
        owner_ok = owner_status == 200 and isinstance(owner_payload.get("summary"), dict) and isinstance(owner_payload.get("recommendations"), list)
        owner_ok = owner_ok and isinstance(owner_payload.get("trace_id"), str) and isinstance(owner_payload.get("service"), str)
        owner_ok = owner_ok and bool(owner_headers.get("X-Trace-Id"))
        steps.append(
            {
                "name": "owner_dashboard_runtime_smoke",
                "command": "GET /api/v1/owner/dashboard",
                "passed": owner_ok,
                "elapsed_seconds": 0.0,
                "output_tail": json.dumps({"status": owner_status, "trace": owner_payload.get("trace_id")}, ensure_ascii=False),
            }
        )
        if not owner_ok:
            REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"STEP39_GATE_FAIL failed=owner_dashboard_runtime_smoke report={REPORT_PATH}")
            raise SystemExit(1)

        admin_status, admin_payload, admin_headers = request(f"/api/v1/admin/dashboard?date={datetime.now(timezone.utc).date().isoformat()}")
        admin_ok = admin_status == 200 and isinstance(admin_payload.get("summary"), dict) and isinstance(admin_payload.get("sections"), dict)
        admin_ok = admin_ok and isinstance(admin_payload.get("degraded_metadata"), dict) and isinstance(admin_payload.get("diagnostic_links"), dict)
        admin_ok = admin_ok and isinstance(admin_payload.get("trace_id"), str) and isinstance(admin_payload.get("service"), str)
        admin_ok = admin_ok and bool(admin_headers.get("X-Trace-Id"))
        steps.append(
            {
                "name": "admin_dashboard_runtime_smoke",
                "command": "GET /api/v1/admin/dashboard",
                "passed": admin_ok,
                "elapsed_seconds": 0.0,
                "output_tail": json.dumps({"status": admin_status, "trace": admin_payload.get("trace_id")}, ensure_ascii=False),
            }
        )
        if not admin_ok:
            REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"STEP39_GATE_FAIL failed=admin_dashboard_runtime_smoke report={REPORT_PATH}")
            raise SystemExit(1)
    elif args.require_runtime:
        steps.append({"name": "runtime_gateway_unavailable", "passed": False, "elapsed_seconds": 0.0, "output_tail": GATEWAY})
        REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"STEP39_GATE_FAIL failed=runtime_gateway_unavailable report={REPORT_PATH}")
        raise SystemExit(1)
    else:
        steps.append(
            {
                "name": "runtime_gateway_unavailable",
                "passed": True,
                "skipped": True,
                "elapsed_seconds": 0.0,
                "output_tail": f"skip runtime smoke because {GATEWAY} is unavailable",
            }
        )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": all(bool(step["passed"]) for step in steps),
        "steps": steps,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"STEP39_GATE_PASS report={REPORT_PATH}")


if __name__ == "__main__":
    main()
