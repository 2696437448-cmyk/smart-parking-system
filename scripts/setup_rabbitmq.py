#!/usr/bin/env python3
"""Declare exchange/queues/bindings for step 7."""

from __future__ import annotations

import argparse
import base64
import json
import urllib.request


def call(base: str, user: str, pwd: str, method: str, path: str, payload: dict | None = None) -> dict:
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
    parser.add_argument("--api", default="http://localhost:15672/api")
    parser.add_argument("--user", default="guest")
    parser.add_argument("--password", default="guest")
    args = parser.parse_args()

    call(args.api, args.user, args.password, "PUT", "exchanges/%2F/dispatch.events", {"type": "direct", "durable": True})
    call(args.api, args.user, args.password, "PUT", "queues/%2F/dispatch.run", {"durable": True})
    call(args.api, args.user, args.password, "PUT", "queues/%2F/dispatch.dlq", {"durable": True})

    call(args.api, args.user, args.password, "POST", "bindings/%2F/e/dispatch.events/q/dispatch.run", {"routing_key": "dispatch.run"})
    call(args.api, args.user, args.password, "POST", "bindings/%2F/e/dispatch.events/q/dispatch.dlq", {"routing_key": "dispatch.dlq"})

    print("STEP7_RABBIT_SETUP_OK")


if __name__ == "__main__":
    main()
