#!/usr/bin/env python3
"""Step28 gate: enhanced navigation response and map preview."""

from __future__ import annotations

import json
import time
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"
GATEWAY = "http://localhost:8080"


def request(path: str, method: str = "GET", body: dict | None = None, headers: dict | None = None):
    data = None
    all_headers = {"X-Trace-Id": f"step28-{uuid.uuid4().hex[:8]}"}
    if headers:
        all_headers.update(headers)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        all_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(GATEWAY + path, data=data, headers=all_headers, method=method)
    with urllib.request.urlopen(req, timeout=12) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def wait_gateway() -> None:
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(GATEWAY + "/actuator/health", timeout=4) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                if resp.status == 200 and payload.get("status") == "UP":
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError("gateway health timeout")


def main() -> None:
    wait_gateway()
    base = datetime.now(timezone(timedelta(hours=8))).replace(second=0, microsecond=0) + timedelta(minutes=75)
    preferred = f"{base.isoformat()}/{(base + timedelta(minutes=45)).isoformat()}"
    order_suffix = uuid.uuid4().hex[:8]
    status, payload = request(
        "/api/v1/owner/reservations",
        method="POST",
        body={
            "user_id": f"owner-step28-{order_suffix}",
            "preferred_window": preferred,
            "location": "R1",
            "slot_id": "R1-S001",
        },
        headers={"Idempotency-Key": f"step28-{order_suffix}"},
    )
    assert status == 200, payload
    order_id = payload.get("order_id") or payload.get("reservation_id")
    status, nav = request(f"/api/v1/owner/navigation/{order_id}")
    assert status == 200, nav
    for key in ["map_url", "eta_minutes", "destination", "region_label", "slot_display_name", "route_summary"]:
        if key not in nav:
            raise AssertionError(f"navigation missing key: {key}")
    assert "openstreetmap.org" in str(nav["map_url"]), nav
    assert isinstance(nav["route_summary"], dict) and nav["route_summary"].get("summary"), nav

    page = (FRONTEND / "src" / "pages" / "OwnerNavigation.vue").read_text(encoding="utf-8")
    for token in ["MapPreview", "route_summary", "Leaflet + OSM"]:
        if token not in page:
            raise AssertionError(f"OwnerNavigation.vue missing token: {token}")
    print("STEP28_GATE_PASS")


if __name__ == "__main__":
    main()
