#!/usr/bin/env python3
"""Step26 gate: raw ingest APIs and Spark ETL analytics outputs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATEWAY = "http://localhost:8080"
REPORTS = ROOT / "reports"
QUALITY = REPORTS / "step26_spark_quality.json"


def request(path: str, method: str = "GET", body: dict | None = None):
    data = None
    headers = {"X-Trace-Id": f"step26-{uuid.uuid4().hex[:8]}"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(GATEWAY + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=12) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def wait_gateway() -> None:
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(GATEWAY + "/actuator/health", timeout=4) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                if resp.status == 200 and payload.get("status") == "UP":
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError("gateway health timeout")


def spark_env() -> dict[str, str]:
    env = os.environ.copy()
    if env.get("JAVA_HOME"):
        return env

    candidates = [
        Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
        Path("/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"),
        Path("/opt/homebrew/opt/openjdk@17"),
        Path("/usr/local/opt/openjdk@17"),
    ]
    for candidate in candidates:
        java_bin = candidate / "bin" / "java"
        if java_bin.exists():
            env["JAVA_HOME"] = str(candidate)
            env["PATH"] = f"{candidate / 'bin'}:{env.get('PATH', '')}"
            return env
    return env


def main() -> None:
    wait_gateway()
    base_time = datetime.now(timezone.utc).replace(microsecond=0)
    run_id = uuid.uuid4().hex[:8]

    sensor_events = {
        "events": [
            {
                "event_id": f"sensor-{run_id}-1",
                "slot_id": "R1-S001",
                "region_id": "R1",
                "event_ts": (base_time - timedelta(minutes=15)).isoformat().replace("+00:00", "Z"),
                "occupied": 1,
                "sensor_source": "iot-sim",
                "quality_flag": "normal",
            },
            {
                "event_id": f"sensor-{run_id}-2",
                "slot_id": "R2-S001",
                "region_id": "R2",
                "event_ts": base_time.isoformat().replace("+00:00", "Z"),
                "occupied": 0,
                "sensor_source": "iot-sim",
                "quality_flag": "normal",
            },
        ]
    }
    lpr_events = {
        "events": [
            {
                "event_id": f"lpr-{run_id}-1",
                "plate": "沪A12345",
                "region_id": "R1",
                "event_type": "in",
                "event_ts": (base_time - timedelta(minutes=10)).isoformat().replace("+00:00", "Z"),
            },
            {
                "event_id": f"lpr-{run_id}-2",
                "plate": "沪B98765",
                "region_id": "R2",
                "event_type": "out",
                "event_ts": base_time.isoformat().replace("+00:00", "Z"),
            },
        ]
    }
    resident_events = {
        "events": [
            {
                "raw_id": f"resident-{run_id}-1",
                "resident_id": "owner-demo-r1",
                "home_region": "R1",
                "weekday": 3,
                "hour_bucket": 8,
                "trip_probability": 0.71,
            },
            {
                "raw_id": f"resident-{run_id}-2",
                "resident_id": "owner-demo-r2",
                "home_region": "R2",
                "weekday": 3,
                "hour_bucket": 18,
                "trip_probability": 0.62,
            },
        ]
    }

    for path, body in [
        ("/internal/v1/ingest/sensor-events", sensor_events),
        ("/internal/v1/ingest/lpr-events", lpr_events),
        ("/internal/v1/ingest/resident-patterns", resident_events),
    ]:
        status, payload = request(path, method="POST", body=body)
        assert status == 200, (path, status, payload)
        assert payload.get("accepted") is True, payload
        assert payload.get("inserted_count", 0) >= 1, payload

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "step11_etl.py"),
            "--engine",
            "spark",
            "--source-mode",
            "mysql",
            "--mysql-host",
            "127.0.0.1",
            "--mysql-port",
            "13306",
            "--mysql-user",
            "sp_user",
            "--mysql-password",
            "sp_pass",
            "--mysql-database",
            "smart_parking",
            "--quality-output",
            str(QUALITY),
        ],
        check=True,
        cwd=ROOT,
        env=spark_env(),
    )

    quality = json.loads(QUALITY.read_text(encoding="utf-8"))
    assert quality["engine"] == "spark", quality
    assert quality["source_mode"] == "mysql_raw", quality
    assert quality["feature_schema_version"] == "step26.v1", quality
    assert quality["quality"]["row_counts"]["forecast_feature_table"] > 0, quality
    assert quality["quality"]["row_counts"]["dispatch_input_table"] > 0, quality

    for rel in [
        "step26_occupancy_heatmap_summary.json",
        "step26_vehicle_flow_summary.json",
        "step26_resident_peak_summary.json",
    ]:
        payload = json.loads((REPORTS / rel).read_text(encoding="utf-8"))
        assert isinstance(payload, list) and payload, rel

    print("STEP26_GATE_PASS")


if __name__ == "__main__":
    main()
