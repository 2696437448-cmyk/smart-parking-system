#!/usr/bin/env python3
"""Step14 gate: Java parking-service consistency chain validation."""

from __future__ import annotations

import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError

GATEWAY = "http://localhost:8080"
PARKING_DIRECT = "http://localhost:8081"


def _http(url: str, method: str = "GET", body: dict | None = None, headers: dict | None = None):
    data = None
    req_headers = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw else {}
            return resp.status, dict(resp.headers), payload
    except HTTPError as ex:
        raw = ex.read().decode("utf-8")
        payload = json.loads(raw) if raw else {}
        return ex.code, dict(ex.headers), payload


def wait_up() -> None:
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            s1, _, b1 = _http(GATEWAY + "/actuator/health")
            s2, _, b2 = _http(PARKING_DIRECT + "/actuator/health")
            if s1 == 200 and b1.get("status") == "UP" and s2 == 200 and b2.get("status") == "UP":
                return
        except (URLError, TimeoutError, ConnectionResetError):
            pass
        time.sleep(2)
    raise RuntimeError("gateway/parking health timeout")


def _reserve(payload: dict, idem_key: str):
    return _http(
        GATEWAY + "/api/v1/owner/reservations",
        method="POST",
        body=payload,
        headers={"Idempotency-Key": idem_key},
    )


def _iso_no_tz(dt: datetime) -> str:
    return dt.replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S")


def main() -> None:
    wait_up()

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    base = now + timedelta(minutes=90)
    oversell_start = _iso_no_tz(base)
    oversell_end = _iso_no_tz(base + timedelta(minutes=30))
    idem_start = _iso_no_tz(base + timedelta(minutes=60))
    idem_end = _iso_no_tz(base + timedelta(minutes=90))

    # 1) Validate consistency component chain is no longer in-memory.
    s_comp, _, b_comp = _http(PARKING_DIRECT + "/internal/debug/consistency/components")
    assert s_comp == 200, f"component endpoint failed: {s_comp} {b_comp}"
    assert b_comp.get("database") == "mysql", b_comp
    assert b_comp.get("idempotency_store") == "redis", b_comp
    assert b_comp.get("lock_provider") == "redisson", b_comp

    # 2) Concurrent oversell test.
    common = {
        "preferred_window": f"{oversell_start}/{oversell_end}",
        "location": "R1",
        "slot_id": "R1-S099",
    }

    futures = []
    with ThreadPoolExecutor(max_workers=30) as pool:
        for i in range(40):
            payload = {**common, "user_id": f"STEP14-U{i:03d}"}
            futures.append(pool.submit(_reserve, payload, f"step14-concurrent-{int(time.time())}-{i:03d}"))

    results = [f.result() for f in as_completed(futures)]
    success = [x for x in results if x[0] == 200]
    conflicts = [x for x in results if x[0] == 409]
    lock_timeouts = [x for x in results if x[0] == 429]

    assert len(success) == 1, f"expected 1 winner, got {len(success)}"
    assert len(success) + len(conflicts) + len(lock_timeouts) == 40, (
        f"unexpected statuses: success={len(success)} conflicts={len(conflicts)} lock={len(lock_timeouts)}"
    )

    # 3) Idempotency replay test backed by Redis.
    idem_payload = {
        "user_id": "STEP14-IDEM-USER",
        "preferred_window": f"{idem_start}/{idem_end}",
        "location": "R2",
        "slot_id": "R2-S088",
    }
    idem_key = f"step14-idem-fixed-{int(time.time())}"

    s1, _, b1 = _reserve(idem_payload, idem_key)
    s2, _, b2 = _reserve(idem_payload, idem_key)
    assert s1 == 200 and s2 == 200, f"idempotency status mismatch: {s1} {s2}"
    assert b1.get("reservation_id") == b2.get("reservation_id"), (b1, b2)
    assert b2.get("replayed") is True, b2

    s_idem, _, b_idem = _http(PARKING_DIRECT + f"/internal/debug/idempotency?key={idem_key}")
    assert s_idem == 200 and b_idem.get("exists") is True, b_idem
    assert int(b_idem.get("ttl_seconds", 0)) > 0, b_idem

    # 4) DB uniqueness proof via debug query.
    qs = f"slot_id=R1-S099&window_start={oversell_start}&window_end={oversell_end}"
    s_dbg, _, b_dbg = _http(PARKING_DIRECT + "/internal/debug/reservations?" + qs)
    assert s_dbg == 200, b_dbg
    assert int(b_dbg.get("count", -1)) == 1, b_dbg

    print("STEP14_GATE_PASS")


if __name__ == "__main__":
    main()
