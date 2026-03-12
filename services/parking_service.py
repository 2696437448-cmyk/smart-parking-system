#!/usr/bin/env python3
"""Step 4 parking service: idempotency + lock + DB uniqueness."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import threading
import time
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

SERVICE_NAME = os.getenv("SERVICE_NAME", "parking-service")
PORT = int(os.getenv("PORT", "8081"))
DB_PATH = os.getenv("PARKING_DB_PATH", "/tmp/parking_service.db")
IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "7200"))
LOCK_WAIT_SECONDS = float(os.getenv("LOCK_WAIT_SECONDS", "0.1"))
LOCK_LEASE_SECONDS = float(os.getenv("LOCK_LEASE_SECONDS", "3.0"))  # reserved for future extension

RABBIT_API_URL = os.getenv("RABBIT_API_URL", "http://rabbitmq:15672/api")
RABBIT_USER = os.getenv("RABBIT_USER", "guest")
RABBIT_PASS = os.getenv("RABBIT_PASS", "guest")
ENABLE_MQ = os.getenv("ENABLE_MQ", "true").lower() in {"1", "true", "yes", "y"}

_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.execute(
    """
    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        slot_id TEXT NOT NULL,
        window_start TEXT NOT NULL,
        window_end TEXT NOT NULL,
        location TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at REAL NOT NULL,
        UNIQUE(slot_id, window_start, window_end)
    )
    """
)
_conn.commit()

_db_lock = threading.Lock()
_locks_guard = threading.Lock()
_slot_window_locks: dict[str, threading.Lock] = {}

_idempotency_guard = threading.Lock()
_idempotency_store: dict[str, dict[str, Any]] = {}

_metrics_guard = threading.Lock()
_http_requests_total = 0
_http_error_total = 0


def _trace(headers: dict[str, str]) -> str:
    return headers.get("X-Trace-Id") or str(uuid.uuid4())


def _json_hash(payload: dict[str, Any]) -> str:
    b = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def _cleanup_idempotency() -> None:
    now = time.time()
    expired = []
    with _idempotency_guard:
        for k, v in _idempotency_store.items():
            if now - float(v["created_at"]) > IDEMPOTENCY_TTL_SECONDS:
                expired.append(k)
        for k in expired:
            _idempotency_store.pop(k, None)


def _get_lock(lock_key: str) -> threading.Lock:
    with _locks_guard:
        if lock_key not in _slot_window_locks:
            _slot_window_locks[lock_key] = threading.Lock()
        return _slot_window_locks[lock_key]




def _rabbit_request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{RABBIT_API_URL}/{path.lstrip('/')}"
    data = None
    headers = {"Content-Type": "application/json"}
    token = base64.b64encode(f"{RABBIT_USER}:{RABBIT_PASS}".encode("utf-8")).decode("utf-8")
    headers["Authorization"] = f"Basic {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _publish_dispatch_event(event_payload: dict[str, Any]) -> bool:
    body = {
        "properties": {
            "delivery_mode": 2,
            "headers": {
                "event_id": event_payload.get("event_id", ""),
                "retry_count": 0,
            },
        },
        "routing_key": "dispatch.run",
        "payload": json.dumps(event_payload, ensure_ascii=False),
        "payload_encoding": "string",
    }
    try:
        resp = _rabbit_request("POST", "exchanges/%2F/dispatch.events/publish", body)
        return bool(resp.get("routed", False))
    except Exception:  # noqa: BLE001
        return False

def _split_window(preferred_window: str) -> tuple[str, str]:
    if "/" in preferred_window:
        start, end = preferred_window.split("/", 1)
        return start.strip(), end.strip()
    return preferred_window.strip(), preferred_window.strip()


def _realtime_snapshot(trace_id: str) -> dict[str, Any]:
    with _db_lock:
        cur = _conn.execute("SELECT COUNT(*) FROM reservations WHERE status = 'RESERVED'")
        active = int((cur.fetchone() or [0])[0])

    # Demo occupancy indicator for polling fallback mode.
    estimated_capacity = 60
    occupancy = round(min(0.98, max(0.05, active / max(estimated_capacity, 1))), 4)

    return {
        "channel": "polling",
        "mode": "degraded",
        "occupancy_rate": occupancy,
        "active_reservations": active,
        "updated_at": time.time(),
        "trace_id": trace_id,
    }


def _record_http_metrics(status_code: int) -> None:
    global _http_requests_total, _http_error_total
    with _metrics_guard:
        _http_requests_total += 1
        if status_code >= 400:
            _http_error_total += 1


def _metrics_text() -> str:
    with _db_lock:
        cur = _conn.execute("SELECT COUNT(*) FROM reservations WHERE status = 'RESERVED'")
        active = int((cur.fetchone() or [0])[0])

    with _metrics_guard:
        req_total = _http_requests_total
        err_total = _http_error_total

    lines = [
        "# HELP smart_parking_http_requests_total Total HTTP requests.",
        "# TYPE smart_parking_http_requests_total counter",
        f"smart_parking_http_requests_total{{service=\"{SERVICE_NAME}\"}} {req_total}",
        "# HELP smart_parking_http_errors_total Total HTTP error responses.",
        "# TYPE smart_parking_http_errors_total counter",
        f"smart_parking_http_errors_total{{service=\"{SERVICE_NAME}\"}} {err_total}",
        "# HELP smart_parking_active_reservations Active reservation count.",
        "# TYPE smart_parking_active_reservations gauge",
        f"smart_parking_active_reservations{{service=\"{SERVICE_NAME}\"}} {active}",
    ]
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def _response(self, code: int, payload: dict[str, Any], trace_id: str) -> None:
        _record_http_metrics(code)
        print(
            json.dumps(
                {
                    "service": SERVICE_NAME,
                    "path": self.path,
                    "status": code,
                    "trace_id": trace_id,
                    "ts": time.time(),
                },
                ensure_ascii=False,
            )
        )
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Trace-Id", trace_id)
        self.end_headers()
        self.wfile.write(body)

    def _text_response(self, code: int, body_text: str, trace_id: str) -> None:
        _record_http_metrics(code)
        print(
            json.dumps(
                {
                    "service": SERVICE_NAME,
                    "path": self.path,
                    "status": code,
                    "trace_id": trace_id,
                    "ts": time.time(),
                },
                ensure_ascii=False,
            )
        )
        body = body_text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Trace-Id", trace_id)
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length)
        return json.loads(raw.decode("utf-8"))

    def _headers_map(self) -> dict[str, str]:
        return {k: v for k, v in self.headers.items()}

    def do_GET(self) -> None:
        trace_id = _trace(self._headers_map())
        parsed = urlparse(self.path)

        if parsed.path == "/metrics":
            self._text_response(200, _metrics_text(), trace_id)
            return

        if parsed.path == "/actuator/health":
            self._response(200, {"status": "UP", "service": SERVICE_NAME}, trace_id)
            return

        if parsed.path == "/api/v1/admin/realtime/status":
            self._response(200, _realtime_snapshot(trace_id), trace_id)
            return

        if parsed.path == "/internal/debug/reservations":
            q = parse_qs(parsed.query)
            slot_id = (q.get("slot_id") or [""])[0]
            window_start = (q.get("window_start") or [""])[0]
            window_end = (q.get("window_end") or [""])[0]
            with _db_lock:
                cur = _conn.execute(
                    "SELECT reservation_id, user_id, slot_id, window_start, window_end, status FROM reservations "
                    "WHERE (? = '' OR slot_id = ?) AND (? = '' OR window_start = ?) AND (? = '' OR window_end = ?)",
                    (slot_id, slot_id, window_start, window_start, window_end, window_end),
                )
                rows = [
                    {
                        "reservation_id": r[0],
                        "user_id": r[1],
                        "slot_id": r[2],
                        "window_start": r[3],
                        "window_end": r[4],
                        "status": r[5],
                    }
                    for r in cur.fetchall()
                ]
            self._response(200, {"count": len(rows), "items": rows}, trace_id)
            return

        self._response(404, {"error": "route_not_found"}, trace_id)

    def do_POST(self) -> None:
        trace_id = _trace(self._headers_map())
        _cleanup_idempotency()
        path = urlparse(self.path).path

        if path == "/api/v1/admin/dispatch/run":
            payload = self._read_json()
            event_payload = {
                "event_id": f"evt-{uuid.uuid4().hex[:16]}",
                "trigger_reason": payload.get("trigger_reason", "manual"),
                "force_fail": bool(payload.get("force_fail", False)),
                "created_at": time.time(),
            }
            routed = _publish_dispatch_event(event_payload) if ENABLE_MQ else False
            self._response(
                200,
                {
                    "job_id": f"job-{uuid.uuid4().hex[:12]}",
                    "accepted": bool(routed or not ENABLE_MQ),
                    "trace_id": trace_id,
                    "trigger_reason": payload.get("trigger_reason", "manual"),
                    "event_id": event_payload["event_id"],
                    "mq_routed": bool(routed),
                },
                trace_id,
            )
            return

        if path != "/api/v1/owner/reservations":
            self._response(404, {"error": "route_not_found"}, trace_id)
            return

        try:
            payload = self._read_json()
        except Exception as ex:  # noqa: BLE001
            self._response(400, {"error": "invalid_json", "message": str(ex)}, trace_id)
            return

        for field in ("user_id", "preferred_window", "location"):
            if not payload.get(field):
                self._response(400, {"error": "missing_field", "field": field}, trace_id)
                return

        idem_key = self.headers.get("Idempotency-Key", "").strip()
        payload_hash = _json_hash(payload)

        if idem_key:
            with _idempotency_guard:
                cached = _idempotency_store.get(idem_key)
                if cached and cached.get("payload_hash") == payload_hash:
                    self._response(
                        int(cached["status_code"]),
                        dict(cached["response_body"]) | {"replayed": True},
                        trace_id,
                    )
                    return

        user_id = payload["user_id"]
        location = payload["location"]
        preferred_window = payload["preferred_window"]
        slot_id = payload.get("slot_id") or f"{location}-S001"
        window_start, window_end = _split_window(preferred_window)

        lock_key = f"lock:slot:{slot_id}:window:{window_start}|{window_end}"
        slot_lock = _get_lock(lock_key)

        acquired = slot_lock.acquire(timeout=LOCK_WAIT_SECONDS)
        if not acquired:
            self._response(
                429,
                {
                    "error": "lock_acquire_timeout",
                    "message": "reservation busy, retry later",
                    "slot_id": slot_id,
                    "window_start": window_start,
                    "window_end": window_end,
                    "trace_id": trace_id,
                },
                trace_id,
            )
            return

        try:
            with _db_lock:
                cur = _conn.execute(
                    "SELECT reservation_id, user_id FROM reservations WHERE slot_id = ? AND window_start = ? AND window_end = ?",
                    (slot_id, window_start, window_end),
                )
                row = cur.fetchone()
                if row:
                    existing_id, existing_user = row
                    body = {
                        "error": "oversell_prevented",
                        "reservation_id": existing_id,
                        "existing_user_id": existing_user,
                        "slot_id": slot_id,
                        "window_start": window_start,
                        "window_end": window_end,
                        "trace_id": trace_id,
                    }
                    status_code = 409
                else:
                    reservation_id = f"res-{uuid.uuid4().hex[:16]}"
                    _conn.execute(
                        "INSERT INTO reservations (reservation_id, user_id, slot_id, window_start, window_end, location, status, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            reservation_id,
                            user_id,
                            slot_id,
                            window_start,
                            window_end,
                            location,
                            "RESERVED",
                            time.time(),
                        ),
                    )
                    _conn.commit()
                    body = {
                        "reservation_id": reservation_id,
                        "status": "RESERVED",
                        "trace_id": trace_id,
                        "slot_id": slot_id,
                        "window_start": window_start,
                        "window_end": window_end,
                    }
                    status_code = 200

            if idem_key:
                with _idempotency_guard:
                    _idempotency_store[idem_key] = {
                        "created_at": time.time(),
                        "payload_hash": payload_hash,
                        "status_code": status_code,
                        "response_body": body,
                    }

            self._response(status_code, body, trace_id)
        except sqlite3.IntegrityError:
            self._response(
                409,
                {
                    "error": "oversell_prevented",
                    "message": "db uniqueness guard triggered",
                    "slot_id": slot_id,
                    "window_start": window_start,
                    "window_end": window_end,
                    "trace_id": trace_id,
                },
                trace_id,
            )
        finally:
            slot_lock.release()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"{SERVICE_NAME} listening on {PORT}, db={DB_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    main()
