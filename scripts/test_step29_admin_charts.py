#!/usr/bin/env python3
"""Step29 gate: admin chart endpoints and ECharts UI."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"
GATEWAY = "http://localhost:8080"


def request(path: str, method: str = "GET", body: dict | None = None, headers: dict | None = None):
    data = None
    merged_headers = {"X-Trace-Id": f"step29-{uuid.uuid4().hex[:8]}"}
    if headers:
        merged_headers.update(headers)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        merged_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(GATEWAY + path, data=data, headers=merged_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except HTTPError as ex:
        try:
            payload = json.loads(ex.read().decode("utf-8"))
        except Exception:
            payload = {"error": "unknown"}
        return ex.code, payload


def wait_gateway() -> None:
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            status, payload = request("/actuator/health")
            if status == 200 and payload.get("status") == "UP":
                return
        except Exception:
            time.sleep(1)
    raise RuntimeError("gateway health timeout")


def seed_revenue() -> None:
    run_id = uuid.uuid4().hex[:8]
    shanghai_tz = timezone(timedelta(hours=8))
    start_dt = datetime.now(shanghai_tz).replace(second=0, microsecond=0) + timedelta(minutes=90)
    end_dt = start_dt + timedelta(minutes=45)
    preferred = f"{start_dt.isoformat()}/{end_dt.isoformat()}"
    query = urllib.parse.urlencode({"location": "R1", "preferred_window": preferred})
    status, rec_payload = request(f"/api/v1/owner/recommendations?{query}")
    assert status == 200, (status, rec_payload)
    results = rec_payload.get("results", [])
    assert results, rec_payload
    slot_id = results[0]["slot_id"]

    status, reserve_payload = request(
        "/api/v1/owner/reservations",
        method="POST",
        body={
            "user_id": f"owner-step29-{run_id}",
            "preferred_window": preferred,
            "location": "R1",
            "slot_id": slot_id,
        },
        headers={"Idempotency-Key": f"step29-reserve-{run_id}"},
    )
    assert status == 200, (status, reserve_payload)
    order_id = reserve_payload.get("order_id") or reserve_payload.get("reservation_id")
    assert order_id, reserve_payload

    status, complete_payload = request(
        f"/api/v1/owner/orders/{order_id}/complete",
        method="POST",
        body={"ended_at": end_dt.isoformat()},
        headers={"Idempotency-Key": f"step29-complete-{run_id}"},
    )
    assert status == 200, (status, complete_payload)
    assert complete_payload.get("billing_status") == "CONFIRMED", complete_payload


def main() -> None:
    wait_gateway()
    seed_revenue()

    for path in [
        "/api/v1/admin/revenue/trend?days=7",
        "/api/v1/admin/occupancy/trend?limit=12",
        "/api/v1/admin/forecast/compare?limit=12",
    ]:
        status, payload = request(path)
        assert status == 200, (path, payload)
        points = payload.get("points")
        assert isinstance(points, list) and points, (path, payload)

    status, dashboard_payload = request(f"/api/v1/admin/dashboard?date={datetime.now(timezone.utc).date().isoformat()}")
    assert status == 200, dashboard_payload
    assert isinstance(dashboard_payload.get("summary"), dict), dashboard_payload
    assert isinstance(dashboard_payload.get("highlights"), dict), dashboard_payload
    sections = dashboard_payload.get("sections")
    assert isinstance(sections, dict), dashboard_payload
    for key in ["revenue_summary", "revenue_trend", "occupancy_trend", "forecast_compare"]:
        assert isinstance(sections.get(key), list) and sections.get(key), (key, dashboard_payload)
    assert isinstance(dashboard_payload.get("degraded_metadata"), dict), dashboard_payload

    admin_page = (FRONTEND / "src" / "pages" / "AdminMonitor.vue").read_text(encoding="utf-8")
    admin_view_model = (FRONTEND / "src" / "composables" / "useAdminDashboardView.ts").read_text(encoding="utf-8")
    admin_service = (FRONTEND / "src" / "services" / "admin.ts").read_text(encoding="utf-8")
    chart_component = (FRONTEND / "src" / "components" / "EChartPanel.vue").read_text(encoding="utf-8")

    for token in ["useAdminDashboardView", "EChartPanel", "ViewStateNotice"]:
        if token not in admin_page:
            raise AssertionError(f"AdminMonitor.vue missing token: {token}")
    for token in ["fetchAdminDashboard", "useRealtimeChannel", "useViewState", "state.markDegraded"]:
        if token not in admin_view_model:
            raise AssertionError(f"useAdminDashboardView.ts missing token: {token}")
    for token in ["/api/v1/admin/dashboard"]:
        if token not in admin_service:
            raise AssertionError(f"admin.ts missing token: {token}")
    for token in ["echarts/core", "BarChart", "chart-canvas"]:
        if token not in chart_component:
            raise AssertionError(f"EChartPanel.vue missing token: {token}")
    print("STEP29_GATE_PASS")


if __name__ == "__main__":
    main()
