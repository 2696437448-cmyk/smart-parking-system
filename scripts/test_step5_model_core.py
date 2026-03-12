#!/usr/bin/env python3
"""Step 5 gate: model predict + optimize validity."""

from __future__ import annotations

import json
import time
import urllib.request
from urllib.error import HTTPError

GATEWAY = "http://localhost:8080"


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
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("gateway health timeout")


def main() -> None:
    wait_gateway()

    # activate model version
    s_act, _, b_act = request(
        "/internal/v1/model/activate",
        "POST",
        {"model_version": "v0.2-lstm-lite"},
        {"Idempotency-Key": "activate-001"},
    )
    assert s_act == 200 and b_act.get("status") == "active", f"activate failed: {s_act}, {b_act}"

    # predict
    s_pred, _, b_pred = request(
        "/internal/v1/model/predict",
        "POST",
        {"region_ids": ["R1", "R2", "R3"], "horizon_minutes": 30},
    )
    assert s_pred == 200, f"predict failed: {s_pred}, {b_pred}"
    records = b_pred.get("records", [])
    assert len(records) == 3, f"predict record count mismatch: {records}"
    for rec in records:
        for key in ("region_id", "ts", "supply", "demand", "gap"):
            assert key in rec, f"missing key in record: {key}, rec={rec}"
        assert isinstance(rec["supply"], (int, float))
        assert isinstance(rec["demand"], (int, float))
        assert isinstance(rec["gap"], (int, float))

    # optimize
    reqs = [
        {"order_id": "O-001", "user_id": "U-001", "preferred_window": "2026-03-12T09:00/09:30", "location": "R1", "constraints": {}},
        {"order_id": "O-002", "user_id": "U-002", "preferred_window": "2026-03-12T09:00/09:30", "location": "R2", "constraints": {}},
        {"order_id": "O-003", "user_id": "U-003", "preferred_window": "2026-03-12T09:00/09:30", "location": "R3", "constraints": {}},
    ]
    s_opt, _, b_opt = request("/internal/v1/dispatch/optimize", "POST", {"requests": reqs})
    assert s_opt == 200, f"optimize failed: {s_opt}, {b_opt}"

    results = b_opt.get("results", [])
    assert len(results) == len(reqs), f"optimize result count mismatch: {results}"

    slot_ids = []
    for res in results:
        for key in ("order_id", "slot_id", "score", "eta", "price", "strategy"):
            assert key in res, f"missing key {key} in {res}"
        assert isinstance(res["score"], (int, float))
        slot_ids.append(res["slot_id"])

    assert len(set(slot_ids)) == len(slot_ids), f"duplicate assigned slot_ids: {slot_ids}"

    print("STEP5_GATE_PASS")


if __name__ == "__main__":
    main()
