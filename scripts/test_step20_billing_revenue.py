#!/usr/bin/env python3
"""Step20/22 gate: billing, navigation, and revenue summary verification."""

from __future__ import annotations

import json
import time
import urllib.parse
import uuid
from datetime import datetime, timedelta, timezone
import urllib.request
from urllib.error import HTTPError

GATEWAY = "http://localhost:8080"


def request(path: str, method: str = "GET", body: dict | None = None, headers: dict | None = None):
    data = None
    h = headers.copy() if headers else {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(GATEWAY + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.status, dict(resp.headers), json.loads(resp.read().decode("utf-8"))
    except HTTPError as ex:
        try:
            payload = json.loads(ex.read().decode("utf-8"))
        except Exception:
            payload = {"error": "unknown"}
        return ex.code, dict(ex.headers), payload


def wait_gateway() -> None:
    deadline = time.time() + 90
    while time.time() < deadline:
        try:
            status, _, body = request("/actuator/health")
            if status == 200 and body.get("status") == "UP":
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("gateway health timeout")


def main() -> None:
    wait_gateway()
    run_id = uuid.uuid4().hex[:8]
    shanghai_tz = timezone(timedelta(hours=8))
    offset_minutes = (int(run_id[:2], 16) % 180) + 60
    start_dt = datetime.now(shanghai_tz).replace(second=0, microsecond=0) + timedelta(minutes=offset_minutes)
    end_dt = start_dt + timedelta(minutes=60)
    preferred = f"{start_dt.isoformat()}/{end_dt.isoformat()}"
    revenue_date = end_dt.date().isoformat()
    query = urllib.parse.urlencode({"location": "R1", "preferred_window": preferred})
    s_rec, _, b_rec = request(f"/api/v1/owner/recommendations?{query}")
    assert s_rec == 200, f"recommendations failed: {s_rec}, {b_rec}"
    results = b_rec.get("results", [])
    assert len(results) >= 1, f"no recommendations: {b_rec}"
    slot_id = results[0]["slot_id"]

    s_res, _, b_res = request(
        "/api/v1/owner/reservations",
        method="POST",
        body={
            "user_id": f"owner-step20-{run_id}",
            "preferred_window": preferred,
            "location": "R1",
            "slot_id": slot_id,
        },
        headers={"Idempotency-Key": f"step20-reserve-{run_id}", "X-Trace-Id": f"step20-trace-{run_id}"},
    )
    assert s_res == 200, f"reservation failed: {s_res}, {b_res}"
    order_id = b_res.get("order_id") or b_res.get("reservation_id")
    assert order_id, f"missing order id: {b_res}"
    assert b_res.get("estimated_amount", 0) > 0, f"missing estimate: {b_res}"

    s_order, _, b_order = request(f"/api/v1/owner/orders/{order_id}")
    assert s_order == 200, f"order detail failed: {s_order}, {b_order}"
    assert b_order.get("billing_status") == "ESTIMATED", f"unexpected billing status: {b_order}"

    s_nav, _, b_nav = request(f"/api/v1/owner/navigation/{order_id}")
    assert s_nav == 200 and b_nav.get("map_url"), f"navigation failed: {s_nav}, {b_nav}"

    s_complete, _, b_complete = request(
        f"/api/v1/owner/orders/{order_id}/complete",
        method="POST",
        body={"ended_at": end_dt.isoformat()},
        headers={"Idempotency-Key": f"complete-{order_id}-{run_id}", "X-Trace-Id": f"step20-complete-{run_id}"},
    )
    assert s_complete == 200, f"complete failed: {s_complete}, {b_complete}"
    assert b_complete.get("billing_status") == "CONFIRMED", f"not confirmed: {b_complete}"
    assert b_complete.get("final_amount", 0) > 0, f"missing final amount: {b_complete}"

    s_rev, _, b_rev = request(f"/api/v1/admin/revenue/summary?date={revenue_date}")
    assert s_rev == 200, f"revenue summary failed: {s_rev}, {b_rev}"
    summaries = b_rev.get("summaries", [])
    assert any(item.get("region_id") == "R1" for item in summaries), f"missing R1 revenue: {b_rev}"

    s_monitor, _, b_monitor = request(f"/api/v1/admin/monitor/summary?date={revenue_date}")
    assert s_monitor == 200, f"monitor summary failed: {s_monitor}, {b_monitor}"
    assert b_monitor.get("business_view") is True, f"unexpected monitor view: {b_monitor}"

    print("STEP20_22_GATE_PASS")


if __name__ == "__main__":
    main()
