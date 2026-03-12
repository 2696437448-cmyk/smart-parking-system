#!/usr/bin/env python3
"""Step 8 gate: websocket realtime + polling fallback."""

from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import urllib.request


def _read_exact(sock: socket.socket, n: int) -> bytes:
    out = b""
    while len(out) < n:
        chunk = sock.recv(n - len(out))
        if not chunk:
            raise RuntimeError("socket closed while reading")
        out += chunk
    return out


def ws_receive_once(host: str, port: int, path: str, timeout: float = 3.0) -> dict:
    sock = socket.create_connection((host, port), timeout=timeout)
    sock.settimeout(timeout)
    try:
        sec_key = base64.b64encode(os.urandom(16)).decode("utf-8")
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {sec_key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        sock.sendall(handshake.encode("utf-8"))

        response = b""
        while b"\r\n\r\n" not in response:
            response += sock.recv(1024)
        if b"101" not in response.split(b"\r\n", 1)[0]:
            raise RuntimeError(f"websocket handshake failed: {response!r}")

        hdr = _read_exact(sock, 2)
        payload_len = hdr[1] & 0x7F

        if payload_len == 126:
            payload_len = int.from_bytes(_read_exact(sock, 2), "big")
        elif payload_len == 127:
            payload_len = int.from_bytes(_read_exact(sock, 8), "big")

        payload = _read_exact(sock, payload_len)
        return json.loads(payload.decode("utf-8"))
    finally:
        sock.close()


def poll_status(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, method="GET", headers={"X-Trace-Id": "step8-polling-trace"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["realtime", "fallback"], required=True)
    parser.add_argument("--ws-host", default="localhost")
    parser.add_argument("--ws-port", type=int, default=8090)
    parser.add_argument("--ws-path", default="/ws/status")
    parser.add_argument("--poll-url", default="http://localhost:8080/api/v1/admin/realtime/status")
    args = parser.parse_args()

    if args.mode == "realtime":
        msg = ws_receive_once(args.ws_host, args.ws_port, args.ws_path)
        assert msg.get("channel") == "websocket", msg
        assert msg.get("mode") == "realtime", msg
        assert "occupancy_rate" in msg, msg
        print("STEP8_WEBSOCKET_OK")
        return

    # fallback mode: websocket endpoint should be unavailable.
    try:
        ws_receive_once(args.ws_host, args.ws_port, args.ws_path, timeout=1.2)
        raise RuntimeError("websocket still available; stop realtime-service before fallback gate")
    except Exception:
        status, payload = poll_status(args.poll_url)
        assert status == 200, (status, payload)
        assert payload.get("channel") == "polling", payload
        assert payload.get("mode") == "degraded", payload
        assert "occupancy_rate" in payload, payload
        print("STEP8_GATE_PASS")


if __name__ == "__main__":
    main()
