#!/usr/bin/env python3
"""Step 8/9 realtime channel service: websocket push + metrics."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

SERVICE_NAME = os.getenv("SERVICE_NAME", "realtime-service")
PORT = int(os.getenv("PORT", "8090"))
PUSH_INTERVAL_SECONDS = float(os.getenv("PUSH_INTERVAL_SECONDS", "1.0"))
_WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

_metrics_guard = threading.Lock()
_http_requests_total = 0
_http_error_total = 0
_ws_messages_total = 0
_ws_active_connections = 0


def _record_http(status_code: int) -> None:
    global _http_requests_total, _http_error_total
    with _metrics_guard:
        _http_requests_total += 1
        if status_code >= 400:
            _http_error_total += 1


def _metrics_text() -> str:
    with _metrics_guard:
        req_total = _http_requests_total
        err_total = _http_error_total
        ws_total = _ws_messages_total
        ws_active = _ws_active_connections

    lines = [
        "# HELP smart_parking_http_requests_total Total HTTP requests.",
        "# TYPE smart_parking_http_requests_total counter",
        f"smart_parking_http_requests_total{{service=\"{SERVICE_NAME}\"}} {req_total}",
        "# HELP smart_parking_http_errors_total Total HTTP error responses.",
        "# TYPE smart_parking_http_errors_total counter",
        f"smart_parking_http_errors_total{{service=\"{SERVICE_NAME}\"}} {err_total}",
        "# HELP smart_parking_ws_messages_total Total websocket messages sent.",
        "# TYPE smart_parking_ws_messages_total counter",
        f"smart_parking_ws_messages_total{{service=\"{SERVICE_NAME}\"}} {ws_total}",
        "# HELP smart_parking_ws_active_connections Active websocket connections.",
        "# TYPE smart_parking_ws_active_connections gauge",
        f"smart_parking_ws_active_connections{{service=\"{SERVICE_NAME}\"}} {ws_active}",
    ]
    return "\n".join(lines) + "\n"


def _ws_accept(sec_key: str) -> str:
    digest = hashlib.sha1((sec_key + _WS_MAGIC).encode("utf-8")).digest()
    return base64.b64encode(digest).decode("utf-8")


def _ws_text_frame(payload: str) -> bytes:
    data = payload.encode("utf-8")
    header = bytearray([0x81])
    length = len(data)
    if length < 126:
        header.append(length)
    elif length <= 65535:
        header.append(126)
        header.extend(length.to_bytes(2, "big"))
    else:
        header.append(127)
        header.extend(length.to_bytes(8, "big"))
    return bytes(header) + data


class Handler(BaseHTTPRequestHandler):
    def _trace_id(self) -> str:
        return self.headers.get("X-Trace-Id") or str(uuid.uuid4())

    def _json(self, code: int, payload: dict, trace_id: str) -> None:
        _record_http(code)
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

    def _text(self, code: int, payload: str, trace_id: str) -> None:
        _record_http(code)
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
        body = payload.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Trace-Id", trace_id)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        trace_id = self._trace_id()
        parsed = urlparse(self.path)

        if parsed.path == "/metrics":
            self._text(200, _metrics_text(), trace_id)
            return

        if parsed.path == "/actuator/health":
            self._json(200, {"status": "UP", "service": SERVICE_NAME}, trace_id)
            return

        if parsed.path != "/ws/status":
            self._json(404, {"error": "route_not_found"}, trace_id)
            return

        upgrade = self.headers.get("Upgrade", "").lower()
        sec_key = self.headers.get("Sec-WebSocket-Key", "")
        if upgrade != "websocket" or not sec_key:
            self._json(426, {"error": "websocket_upgrade_required"}, trace_id)
            return

        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", _ws_accept(sec_key))
        self.end_headers()

        global _ws_active_connections, _ws_messages_total
        with _metrics_guard:
            _ws_active_connections += 1

        sequence = 0
        try:
            while True:
                sequence += 1
                occupancy = round(0.45 + (sequence % 7) * 0.03, 4)
                payload = json.dumps(
                    {
                        "channel": "websocket",
                        "mode": "realtime",
                        "sequence": sequence,
                        "occupancy_rate": occupancy,
                        "updated_at": time.time(),
                        "trace_id": trace_id,
                    },
                    ensure_ascii=False,
                )
                with _metrics_guard:
                    _ws_messages_total += 1
                self.connection.sendall(_ws_text_frame(payload))
                time.sleep(PUSH_INTERVAL_SECONDS)
        except OSError:
            return
        finally:
            with _metrics_guard:
                _ws_active_connections = max(0, _ws_active_connections - 1)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"{SERVICE_NAME} listening on {PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
