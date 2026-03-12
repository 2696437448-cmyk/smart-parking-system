#!/usr/bin/env python3
"""Simple HTTP stub for step-3 route forwarding checks."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

SERVICE_NAME = os.getenv("SERVICE_NAME", "stub-service")
PORT = int(os.getenv("PORT", "8081"))


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if self.headers.get("X-Trace-Id"):
            self.send_header("X-Trace-Id", self.headers.get("X-Trace-Id"))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self) -> None:
        if self.path == "/actuator/health":
            self._json(200, {"status": "UP", "service": SERVICE_NAME})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length > 0 else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            body = {"_raw": raw.decode("utf-8", errors="ignore")}

        payload = {
            "service": SERVICE_NAME,
            "method": self.command,
            "path": self.path,
            "trace_id": self.headers.get("X-Trace-Id", ""),
            "idempotency_key": self.headers.get("Idempotency-Key", ""),
            "body": body,
        }
        self._json(200, payload)

    def do_GET(self) -> None:
        self._handle()

    def do_POST(self) -> None:
        self._handle()

    def do_PUT(self) -> None:
        self._handle()

    def do_DELETE(self) -> None:
        self._handle()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"{SERVICE_NAME} listening on {PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
