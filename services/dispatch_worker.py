#!/usr/bin/env python3
"""Step 7 worker with retry and DLQ semantics via RabbitMQ HTTP API."""

from __future__ import annotations

import argparse
import base64
import json
import time
import urllib.request
from typing import Any


def call(base: str, user: str, pwd: str, method: str, path: str, payload: dict | None = None) -> Any:
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


def publish(base: str, user: str, pwd: str, routing_key: str, payload: dict, event_id: str, retry_count: int) -> bool:
    body = {
        "properties": {
            "delivery_mode": 2,
            "headers": {"event_id": event_id, "retry_count": retry_count},
        },
        "routing_key": routing_key,
        "payload": json.dumps(payload, ensure_ascii=False),
        "payload_encoding": "string",
    }
    out = call(base, user, pwd, "POST", "exchanges/%2F/dispatch.events/publish", body)
    return bool(out.get("routed", False))


def consume_once(base: str, user: str, pwd: str, max_retry: int) -> bool:
    msgs = call(
        base,
        user,
        pwd,
        "POST",
        "queues/%2F/dispatch.run/get",
        {"count": 1, "ackmode": "ack_requeue_false", "encoding": "auto", "truncate": 50000},
    )
    if not msgs:
        return False

    msg = msgs[0]
    headers = ((msg.get("properties") or {}).get("headers") or {})
    retry_count = int(headers.get("retry_count", 0))
    event_id = str(headers.get("event_id") or "evt-unknown")

    payload = json.loads(msg.get("payload") or "{}")
    force_fail = bool(payload.get("force_fail", False))

    if force_fail:
        if retry_count < max_retry:
            publish(base, user, pwd, "dispatch.run", payload, event_id, retry_count + 1)
        else:
            publish(base, user, pwd, "dispatch.dlq", payload, event_id, retry_count)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:15672/api")
    parser.add_argument("--user", default="guest")
    parser.add_argument("--password", default="guest")
    parser.add_argument("--max-retry", type=int, default=2)
    parser.add_argument("--max-cycles", type=int, default=20)
    args = parser.parse_args()

    for _ in range(args.max_cycles):
        found = consume_once(args.api, args.user, args.password, args.max_retry)
        if not found:
            time.sleep(0.2)

    print("STEP7_WORKER_RUN_DONE")


if __name__ == "__main__":
    main()
