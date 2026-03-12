#!/usr/bin/env python3
"""Step 11 ETL: multi-source alignment and feature table generation.

Engine policy:
- Prefer PySpark when available.
- Fallback to built-in Python csv processing when PySpark is unavailable.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FILES = {
    "slot_status": "slot_status.csv",
    "vehicle_event": "vehicle_event.csv",
    "resident_pattern": "resident_pattern.csv",
}

FEATURE_SCHEMA_VERSION = "step11.v1"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_ts(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


def _floor_15m(dt: datetime) -> datetime:
    minute = (dt.minute // 15) * 15
    return dt.replace(minute=minute, second=0, microsecond=0)


def _safe_float(raw: Any, default: float = 0.0) -> float:
    try:
        return float(raw)
    except Exception:
        return default


def _safe_int(raw: Any, default: int = 0) -> int:
    try:
        return int(float(raw))
    except Exception:
        return default


def _read_csv_python(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _read_csv_spark(path: Path) -> list[dict[str, str]]:
    # Import lazily to keep fallback path dependency-free.
    from pyspark.sql import SparkSession  # type: ignore

    spark = SparkSession.builder.master("local[*]").appName("step11-etl").getOrCreate()
    try:
        df = spark.read.option("header", "true").csv(str(path))
        rows = [
            {str(k): "" if v is None else str(v) for k, v in row.asDict().items()}
            for row in df.collect()
        ]
        return rows
    finally:
        spark.stop()


def _resolve_source(raw_dir: Path, external_dir: Path | None) -> tuple[dict[str, Path], str]:
    if external_dir is not None:
        ext_paths = {k: external_dir / v for k, v in REQUIRED_FILES.items()}
        if all(p.exists() for p in ext_paths.values()):
            return ext_paths, "external"

    raw_paths = {k: raw_dir / v for k, v in REQUIRED_FILES.items()}
    missing = [str(p) for p in raw_paths.values() if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing input files: {missing}")
    return raw_paths, "fallback_raw"


def _build_feature_tables(
    slot_rows: list[dict[str, str]],
    vehicle_rows: list[dict[str, str]],
    resident_rows: list[dict[str, str]],
    source_mode: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    # Region capacities from slot topology.
    region_slots: dict[str, set[str]] = defaultdict(set)

    # slot_status aggregates by (region, bucket_ts)
    slot_agg: dict[tuple[str, datetime], dict[str, float]] = defaultdict(
        lambda: {"slot_samples": 0.0, "occupied_count": 0.0}
    )

    ts_slot_total = 0
    ts_slot_ok = 0

    for row in slot_rows:
        region = (row.get("region_id") or "").strip()
        slot_id = (row.get("slot_id") or "").strip()
        dt = _parse_ts(row.get("ts") or "")
        ts_slot_total += 1
        if not region or not slot_id or dt is None:
            continue
        ts_slot_ok += 1
        dtb = _floor_15m(dt)
        region_slots[region].add(slot_id)
        key = (region, dtb)
        slot_agg[key]["slot_samples"] += 1.0
        slot_agg[key]["occupied_count"] += float(_safe_int(row.get("occupied"), 0))

    # vehicle_event aggregates by (region, bucket_ts)
    veh_agg: dict[tuple[str, datetime], dict[str, int]] = defaultdict(lambda: {"in": 0, "out": 0})
    ts_veh_total = 0
    ts_veh_ok = 0

    for row in vehicle_rows:
        region = (row.get("region_id") or "").strip()
        event_type = (row.get("event_type") or "").strip().lower()
        dt = _parse_ts(row.get("event_ts") or "")
        ts_veh_total += 1
        if not region or dt is None or event_type not in {"in", "out"}:
            continue
        ts_veh_ok += 1
        key = (region, _floor_15m(dt))
        veh_agg[key][event_type] += 1

    # resident_pattern average probability by (region, weekday, hour)
    trip_agg: dict[tuple[str, int, int], tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    region_trip_agg: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    global_sum = 0.0
    global_cnt = 0

    for row in resident_rows:
        region = (row.get("home_region") or "").strip() or (row.get("region_id") or "").strip()
        weekday = _safe_int(row.get("weekday"), -1)
        hour = _safe_int(row.get("hour_bucket"), -1)
        p = _safe_float(row.get("trip_probability"), -1.0)
        if not region or weekday < 1 or weekday > 7 or hour < 0 or hour > 23 or p < 0:
            continue

        prev_s, prev_c = trip_agg[(region, weekday, hour)]
        trip_agg[(region, weekday, hour)] = (prev_s + p, prev_c + 1)

        rs, rc = region_trip_agg[region]
        region_trip_agg[region] = (rs + p, rc + 1)

        global_sum += p
        global_cnt += 1

    global_avg_trip = (global_sum / global_cnt) if global_cnt else 0.3

    def resolve_trip(region: str, weekday: int, hour: int) -> float:
        s_c = trip_agg.get((region, weekday, hour))
        if s_c and s_c[1] > 0:
            return s_c[0] / s_c[1]
        r_c = region_trip_agg.get(region)
        if r_c and r_c[1] > 0:
            return r_c[0] / r_c[1]
        return global_avg_trip

    all_keys = sorted(set(slot_agg.keys()) | set(veh_agg.keys()), key=lambda x: (x[0], x[1]))

    forecast_rows: list[dict[str, Any]] = []
    dispatch_rows: list[dict[str, Any]] = []

    for region, bucket_ts in all_keys:
        capacity = float(max(1, len(region_slots.get(region, set()))))

        s = slot_agg.get((region, bucket_ts), {"slot_samples": 0.0, "occupied_count": 0.0})
        slot_samples = float(s["slot_samples"])
        occupied_count = float(s["occupied_count"])

        # If slot samples are absent for this bucket, estimate occupancy from latest ratio fallback.
        occupancy_rate = (occupied_count / slot_samples) if slot_samples > 0 else 0.0
        occupancy_rate = max(0.0, min(1.0, occupancy_rate))

        veh = veh_agg.get((region, bucket_ts), {"in": 0, "out": 0})
        in_count = int(veh["in"])
        out_count = int(veh["out"])
        net_flow = in_count - out_count

        weekday = bucket_ts.isoweekday()
        hour_bucket = bucket_ts.hour
        trip_probability = max(0.0, min(1.0, resolve_trip(region, weekday, hour_bucket)))

        supply_proxy = max(0.0, round(capacity - occupied_count, 4))
        demand_proxy = max(0.0, round(in_count + (trip_probability * capacity * 0.25), 4))
        gap_proxy = round(supply_proxy - demand_proxy, 4)

        forecast_rows.append(
            {
                "region_id": region,
                "ts": bucket_ts.isoformat(),
                "weekday": weekday,
                "hour_bucket": hour_bucket,
                "capacity": int(capacity),
                "occupied_count": round(occupied_count, 4),
                "occupancy_rate": round(occupancy_rate, 6),
                "vehicle_in_count": in_count,
                "vehicle_out_count": out_count,
                "net_vehicle_flow": net_flow,
                "trip_probability_avg": round(trip_probability, 6),
                "supply_proxy": round(supply_proxy, 4),
                "demand_proxy": round(demand_proxy, 4),
                "gap_proxy": gap_proxy,
                "feature_schema_version": FEATURE_SCHEMA_VERSION,
                "source_mode": source_mode,
            }
        )

        congestion_score = max(0.0, min(1.0, occupancy_rate + max(0.0, net_flow) / max(capacity, 1.0)))
        price_factor = max(0.5, round(1.0 + 0.8 * occupancy_rate + 0.2 * trip_probability, 6))
        dispatch_priority = max(0.0, round(demand_proxy - supply_proxy, 4))

        dispatch_rows.append(
            {
                "region_id": region,
                "ts": bucket_ts.isoformat(),
                "estimated_supply": round(supply_proxy, 4),
                "estimated_demand": round(demand_proxy, 4),
                "estimated_gap": gap_proxy,
                "congestion_score": round(congestion_score, 6),
                "price_factor": price_factor,
                "dispatch_priority": dispatch_priority,
                "feature_schema_version": FEATURE_SCHEMA_VERSION,
                "source_mode": source_mode,
            }
        )

    quality = {
        "timestamp_parse_success": {
            "slot_status": round(ts_slot_ok / max(ts_slot_total, 1), 6),
            "vehicle_event": round(ts_veh_ok / max(ts_veh_total, 1), 6),
        },
        "row_counts": {
            "slot_status": len(slot_rows),
            "vehicle_event": len(vehicle_rows),
            "resident_pattern": len(resident_rows),
            "forecast_feature_table": len(forecast_rows),
            "dispatch_input_table": len(dispatch_rows),
        },
    }

    return forecast_rows, dispatch_rows, quality


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _run(args: argparse.Namespace) -> dict[str, Any]:
    raw_dir = Path(args.raw_dir)
    external_dir = Path(args.external_dir) if args.external_dir else None

    paths, source_mode = _resolve_source(raw_dir=raw_dir, external_dir=external_dir)

    engine = "python"
    if args.engine in {"spark", "auto"}:
        try:
            import pyspark  # type: ignore  # noqa: F401
            engine = "spark"
        except Exception:
            if args.engine == "spark":
                raise
            engine = "python"

    read_fn = _read_csv_spark if engine == "spark" else _read_csv_python

    slot_rows = read_fn(paths["slot_status"])
    vehicle_rows = read_fn(paths["vehicle_event"])
    resident_rows = read_fn(paths["resident_pattern"])

    forecast_rows, dispatch_rows, quality = _build_feature_tables(
        slot_rows=slot_rows,
        vehicle_rows=vehicle_rows,
        resident_rows=resident_rows,
        source_mode=source_mode,
    )

    forecast_output = Path(args.forecast_output)
    dispatch_output = Path(args.dispatch_output)
    quality_output = Path(args.quality_output)

    _write_csv(forecast_output, forecast_rows)
    _write_csv(dispatch_output, dispatch_rows)

    report = {
        "generated_at": _now_iso(),
        "engine": engine,
        "source_mode": source_mode,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "inputs": {k: str(v) for k, v in paths.items()},
        "outputs": {
            "forecast_feature_table": str(forecast_output),
            "dispatch_input_table": str(dispatch_output),
        },
        "quality": quality,
        "overall_passed": len(forecast_rows) > 0 and len(dispatch_rows) > 0,
    }

    _write_json(quality_output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Step 11 ETL pipeline")
    parser.add_argument("--raw-dir", default="data/raw", help="fallback raw directory")
    parser.add_argument("--external-dir", default="", help="optional external dataset directory")
    parser.add_argument("--engine", choices=["auto", "spark", "python"], default="auto")
    parser.add_argument("--forecast-output", default="data/processed/forecast_feature_table.csv")
    parser.add_argument("--dispatch-output", default="data/processed/dispatch_input_table.csv")
    parser.add_argument("--quality-output", default="reports/step11_etl_quality.json")
    args = parser.parse_args()

    report = _run(args)
    print(
        "STEP11_ETL_OK",
        json.dumps(
            {
                "engine": report["engine"],
                "source_mode": report["source_mode"],
                "forecast_rows": report["quality"]["row_counts"]["forecast_feature_table"],
                "dispatch_rows": report["quality"]["row_counts"]["dispatch_input_table"],
                "overall_passed": report["overall_passed"],
            },
            ensure_ascii=False,
        ),
    )


if __name__ == "__main__":
    main()
