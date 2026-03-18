#!/usr/bin/env python3
"""Step 4 gate: concurrency consistency and idempotency."""

from __future__ import annotations

import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError

GATEWAY = "http://localhost:8080"
PARKING_DIRECT = "http://localhost:8081"


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
            status, _, body = request("/actuator/health", method="GET")
            if status == 200 and body.get("status") == "UP":
                return
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    raise RuntimeError("gateway health timeout")


def _iso_no_tz(dt: datetime) -> str:
    return dt.replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S")


def main() -> None:
    wait_gateway()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    base = now + timedelta(minutes=30)
    oversell_start = _iso_no_tz(base)
    oversell_end = _iso_no_tz(base + timedelta(minutes=30))

    common = {
        "preferred_window": f"{oversell_start}/{oversell_end}",
        "location": "R1",
        "slot_id": "R1-S001",
    }

    # 1) Oversell prevention concurrency test
    futures = []
    with ThreadPoolExecutor(max_workers=24) as ex:
        for i in range(30):
            payload = {**common, "user_id": f"U{i:04d}"}
            headers = {"Idempotency-Key": f"step4-concurrent-{int(time.time())}-{i:03d}"}
            futures.append(ex.submit(request, "/api/v1/owner/reservations", "POST", payload, headers))

    results = [f.result() for f in as_completed(futures)]
    success = [r for r in results if r[0] == 200]
    conflicts = [r for r in results if r[0] == 409]
    lock_timeouts = [r for r in results if r[0] == 429]

    assert len(success) == 1, f"expected exactly 1 success, got {len(success)}"
    assert len(success) + len(conflicts) + len(lock_timeouts) == 30, (
        f"unexpected statuses: success={len(success)}, conflicts={len(conflicts)}, lock_timeouts={len(lock_timeouts)}"
    )
    assert len(conflicts) + len(lock_timeouts) >= 29, (
        f"expected all non-winning requests to be rejected, got conflicts={len(conflicts)}, lock_timeouts={len(lock_timeouts)}"
    )

    # 2) Idempotency replay test (same key, same payload => same reservation id)
    idem_start = _iso_no_tz(base + timedelta(minutes=60))
    idem_end = _iso_no_tz(base + timedelta(minutes=90))
    idem_payload = {
        "user_id": "U9000",
        "preferred_window": f"{idem_start}/{idem_end}",
        "location": "R2",
        "slot_id": "R2-S001",
    }
    idem_headers = {"Idempotency-Key": f"idem-fixed-{int(time.time())}"}

    s1, _, b1 = request("/api/v1/owner/reservations", "POST", idem_payload, idem_headers)
    s2, _, b2 = request("/api/v1/owner/reservations", "POST", idem_payload, idem_headers)

    assert s1 == 200 and s2 == 200, f"idempotency status unexpected: {s1}, {s2}"
    assert b1.get("reservation_id") == b2.get("reservation_id"), "idempotency replay returned different reservation_id"

    # 3) Debug endpoint verifies no duplicate active reservation for the oversell target window
    req = urllib.request.Request(
        PARKING_DIRECT
        + f"/internal/debug/reservations?slot_id=R1-S001&window_start={oversell_start}&window_end={oversell_end}",
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        status = resp.status
        debug_body = json.loads(resp.read().decode("utf-8"))
    assert status == 200, f"debug endpoint status unexpected: {status}"
    assert int(debug_body.get("count", -1)) == 1, f"expected one active reservation, got {debug_body}"

    print("STEP4_GATE_PASS")


if __name__ == "__main__":
    main()
