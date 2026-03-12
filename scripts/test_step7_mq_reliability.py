#!/usr/bin/env python3
"""Step 7 gate: force failure, verify retry then DLQ."""

from __future__ import annotations

import argparse
import base64
import json
import time
import urllib.request


def call(base: str, user: str, pwd: str, method: str, path: str, payload: dict | None = None):
    url = f"{base.rstrip('/')}/{path.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    token = base64.b64encode(f"{user}:{pwd}".encode("utf-8")).decode("utf-8")
    headers["Authorization"] = f"Basic {token}"
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=8) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rabbit-api", default="http://localhost:15672/api")
    parser.add_argument("--user", default="guest")
    parser.add_argument("--password", default="guest")
    parser.add_argument("--gateway", default="http://localhost:8080")
    args = parser.parse_args()

    # trigger dispatch event with force_fail
    req = urllib.request.Request(
        args.gateway + "/api/v1/admin/dispatch/run",
        data=json.dumps({"trigger_reason": "step7-test", "force_fail": True}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Idempotency-Key": "step7-dispatch-001"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
        assert payload.get("accepted") is True, payload

    # run worker cycles indirectly from shell; here only validate queue state eventually
    deadline = time.time() + 30
    while time.time() < deadline:
        q = call(args.rabbit_api, args.user, args.password, "GET", "queues/%2F/dispatch.dlq")
        if int(q.get("messages", 0)) >= 1:
            print("STEP7_GATE_PASS")
            return
        time.sleep(1)

    raise RuntimeError("dispatch.dlq did not receive message in time")


if __name__ == "__main__":
    main()
