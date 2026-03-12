#!/usr/bin/env python3
"""Generate fallback sample datasets for Step 0."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta
from pathlib import Path


def _write_slot_status(path: Path) -> None:
    regions = ["R1", "R2", "R3"]
    slots = [f"{region}-S{idx:03d}" for region in regions for idx in range(1, 21)]  # 60 slots
    start = datetime(2026, 1, 1, 0, 0, 0)
    end = start + timedelta(days=3)
    step = timedelta(minutes=15)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["slot_id", "region_id", "ts", "occupied", "sensor_source", "quality_flag"],
        )
        writer.writeheader()
        cur = start
        while cur < end:
            ts_str = cur.isoformat()
            for slot_id in slots:
                region_id = slot_id.split("-")[0]
                occupied = 1 if (hash(slot_id + ts_str) % 100) < 58 else 0
                writer.writerow(
                    {
                        "slot_id": slot_id,
                        "region_id": region_id,
                        "ts": ts_str,
                        "occupied": occupied,
                        "sensor_source": "iot_sensor",
                        "quality_flag": "OK",
                    }
                )
            cur += step


def _write_vehicle_event(path: Path) -> None:
    regions = ["R1", "R2", "R3"]
    start = datetime(2026, 1, 1, 0, 0, 0)
    end = start + timedelta(days=3)
    step = timedelta(minutes=15)
    event_id = 1

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["event_id", "plate_hash", "region_id", "event_type", "event_ts"],
        )
        writer.writeheader()
        cur = start
        while cur < end:
            for region in regions:
                for k in range(2):
                    writer.writerow(
                        {
                            "event_id": f"EVT-{event_id:08d}",
                            "plate_hash": f"plate_{region}_{(event_id % 997):03d}",
                            "region_id": region,
                            "event_type": "in" if (event_id + k) % 2 == 0 else "out",
                            "event_ts": cur.isoformat(),
                        }
                    )
                    event_id += 1
            cur += step


def _write_resident_pattern(path: Path) -> None:
    residents = [f"U{idx:04d}" for idx in range(1, 31)]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["resident_id", "home_region", "weekday", "hour_bucket", "trip_probability"],
        )
        writer.writeheader()
        for resident_id in residents:
            region = ["R1", "R2", "R3"][hash(resident_id) % 3]
            for weekday in range(1, 8):
                for hour in range(24):
                    if 7 <= hour <= 9 or 17 <= hour <= 19:
                        base = 0.72
                    elif 10 <= hour <= 16:
                        base = 0.34
                    else:
                        base = 0.12
                    weekend_bias = 0.08 if weekday in (6, 7) else -0.03
                    p = min(1.0, max(0.0, base + weekend_bias + ((hash((resident_id, weekday, hour)) % 11) - 5) * 0.01))
                    writer.writerow(
                        {
                            "resident_id": resident_id,
                            "home_region": region,
                            "weekday": weekday,
                            "hour_bucket": hour,
                            "trip_probability": round(p, 4),
                        }
                    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fallback sample data")
    parser.add_argument("--output-dir", default="data/raw", help="output directory")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    _write_slot_status(out / "slot_status.csv")
    _write_vehicle_event(out / "vehicle_event.csv")
    _write_resident_pattern(out / "resident_pattern.csv")

    print(f"generated={out}")


if __name__ == "__main__":
    main()
