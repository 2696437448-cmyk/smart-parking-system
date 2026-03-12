#!/usr/bin/env python3
"""Step 13 gate: model registry activation + rollback without restart."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_SERVICE = PROJECT_ROOT / "services/model_service.py"
SYNC_SCRIPT = PROJECT_ROOT / "scripts/step13_sync_model_registry.py"
OPENAPI_VALIDATOR = PROJECT_ROOT / "scripts/validate_openapi.py"
OPENAPI_SPEC = PROJECT_ROOT / "openapi/smart-parking.yaml"

PORT = 18080
BASE = f"http://127.0.0.1:{PORT}"
REGISTRY_PATH = Path("/tmp/smart_parking_step13_registry.json")


def _request(path: str, method: str = "GET", body: dict | None = None, headers: dict | None = None) -> tuple[int, dict, dict]:
    payload = None
    request_headers = dict(headers or {})
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(BASE + path, data=payload, headers=request_headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode("utf-8")
            parsed = json.loads(data) if data else {}
            return resp.status, dict(resp.headers), parsed
    except HTTPError as ex:
        data = ex.read().decode("utf-8")
        parsed = json.loads(data) if data else {}
        return ex.code, dict(ex.headers), parsed


def _wait_health(timeout_seconds: int = 40) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            status, _, body = _request("/actuator/health", "GET")
            if status == 200 and body.get("status") == "UP":
                return
        except URLError:
            pass
        time.sleep(0.8)
    raise RuntimeError("model_service health check timeout")


def _run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return proc.stdout.strip()


def _assert_predict_version(expected: str) -> None:
    status, _, body = _request(
        "/internal/v1/model/predict",
        "POST",
        {"region_ids": ["R1", "R2", "R3"], "horizon_minutes": 30},
    )
    if status != 200:
        raise AssertionError(f"predict status={status}, body={body}")
    got = str(body.get("model_version", ""))
    if got != expected:
        raise AssertionError(f"predict model mismatch expected={expected}, got={got}, body={body}")



def main() -> None:
    REGISTRY_PATH.unlink(missing_ok=True)

    _run(
        [
            sys.executable,
            str(SYNC_SCRIPT),
            "--artifact-dir",
            str(PROJECT_ROOT / "artifacts/models"),
            "--output",
            str(REGISTRY_PATH),
            "--active-model",
            "step12-lstm-lite-v1",
        ]
    )

    env = os.environ.copy()
    env["PORT"] = str(PORT)
    env["SLOT_STATUS_PATH"] = str(PROJECT_ROOT / "data/raw/slot_status.csv")
    env["MODEL_REGISTRY_PATH"] = str(REGISTRY_PATH)
    env["MODEL_ARTIFACT_DIR"] = str(PROJECT_ROOT / "artifacts/models")

    proc = subprocess.Popen(
        [sys.executable, str(MODEL_SERVICE)],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _wait_health()

        status, _, reg = _request("/internal/v1/model/registry", "GET")
        if status != 200:
            raise AssertionError(f"registry query failed: status={status}, body={reg}")

        versions = set(reg.get("available_versions", []))
        required = {"step12-lstm-lite-v1", "step12-baseline-v1", "v0.2-lstm-lite"}
        if not required.issubset(versions):
            raise AssertionError(f"registry missing versions: {sorted(required - versions)}")

        if reg.get("active_version") != "step12-lstm-lite-v1":
            raise AssertionError(f"unexpected initial active version: {reg}")

        _assert_predict_version("step12-lstm-lite-v1")

        s1, _, b1 = _request(
            "/internal/v1/model/activate",
            "POST",
            {
                "model_version": "step12-baseline-v1",
                "reason": "step13_gate_switch_to_baseline",
            },
            {"Idempotency-Key": "step13-activate-1"},
        )
        if s1 != 200 or b1.get("status") != "active":
            raise AssertionError(f"activate baseline failed: status={s1}, body={b1}")

        _assert_predict_version("step12-baseline-v1")

        s2, _, b2 = _request(
            "/internal/v1/model/activate",
            "POST",
            {
                "model_version": "step12-lstm-lite-v1",
                "reason": "step13_gate_switch_back_to_lstm",
            },
            {"Idempotency-Key": "step13-activate-2"},
        )
        if s2 != 200 or b2.get("status") != "active":
            raise AssertionError(f"activate lstm failed: status={s2}, body={b2}")

        _assert_predict_version("step12-lstm-lite-v1")

        s3, _, b3 = _request(
            "/internal/v1/model/activate",
            "POST",
            {
                "model_version": "step12-lstm-lite-v1",
                "rollback": True,
                "reason": "step13_gate_auto_rollback",
            },
            {"Idempotency-Key": "step13-rollback-1"},
        )
        if s3 != 200 or b3.get("status") != "rolled_back":
            raise AssertionError(f"rollback failed: status={s3}, body={b3}")

        _assert_predict_version("step12-baseline-v1")

        if proc.poll() is not None:
            raise AssertionError("model_service exited during hot-switch test")

        registry_payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        if registry_payload.get("active_version") != "step12-baseline-v1":
            raise AssertionError(f"registry active version mismatch after rollback: {registry_payload}")

        history = registry_payload.get("activation_history", [])
        if not isinstance(history, list) or len(history) < 3:
            raise AssertionError("activation history not recorded as expected")

        _run([sys.executable, str(OPENAPI_VALIDATOR), "--spec", str(OPENAPI_SPEC)])

        print("STEP13_GATE_PASS")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


if __name__ == "__main__":
    main()
