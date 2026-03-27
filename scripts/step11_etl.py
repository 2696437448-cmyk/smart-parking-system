#!/usr/bin/env python3
"""Step 11 ETL: multi-source alignment and feature table generation.

Engine policy:
- Prefer PySpark when available.
- Fallback to built-in Python processing when PySpark is unavailable.

Source policy:
- Prefer external CSV datasets when explicitly provided.
- Support raw ingestion tables from MySQL for near-real Step26 replay.
- Fallback to built-in CSV samples for reproducibility.
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

FEATURE_SCHEMA_VERSION = "step26.v1"


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
    from pyspark.sql import SparkSession  # type: ignore

    spark = SparkSession.builder.master("local[*]").appName("step11-etl").getOrCreate()
    try:
        df = spark.read.option("header", "true").csv(str(path))
        return [
            {str(k): "" if v is None else str(v) for k, v in row.asDict().items()}
            for row in df.collect()
        ]
    finally:
        spark.stop()


def _spark_materialize(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    if not rows:
        return []

    from pyspark.sql import SparkSession  # type: ignore

    spark = SparkSession.builder.master("local[*]").appName("step11-etl-materialize").getOrCreate()
    try:
        df = spark.createDataFrame(rows)
        return [
            {str(k): "" if v is None else str(v) for k, v in row.asDict().items()}
            for row in df.collect()
        ]
    finally:
        spark.stop()


def _load_pymysql():
    import pymysql  # type: ignore

    return pymysql


def _read_mysql_rows(args: argparse.Namespace, engine: str) -> tuple[dict[str, list[dict[str, str]]], str]:
    pymysql = _load_pymysql()
    conn = pymysql.connect(
        host=args.mysql_host,
        port=int(args.mysql_port),
        user=args.mysql_user,
        password=args.mysql_password,
        database=args.mysql_database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=3,
        read_timeout=8,
        write_timeout=8,
    )
    try:
        with conn.cursor() as cursor:
            tables = ["sensor_event_raw", "lpr_event_raw", "resident_trip_raw"]
            for table in tables:
                cursor.execute(f"SHOW TABLES LIKE %s", (table,))
                if cursor.fetchone() is None:
                    raise RuntimeError(f"missing mysql raw table: {table}")

            cursor.execute(
                """
                SELECT slot_id, region_id, event_ts AS ts, occupied, sensor_source, quality_flag
                FROM sensor_event_raw
                ORDER BY created_at ASC
                """
            )
            slot_rows = list(cursor.fetchall())

            cursor.execute(
                """
                SELECT event_id, plate_hash, region_id, event_type, event_ts
                FROM lpr_event_raw
                ORDER BY created_at ASC
                """
            )
            vehicle_rows = list(cursor.fetchall())

            cursor.execute(
                """
                SELECT resident_id, home_region, weekday, hour_bucket, trip_probability
                FROM resident_trip_raw
                ORDER BY created_at ASC
                """
            )
            resident_rows = list(cursor.fetchall())
    finally:
        conn.close()

    if not slot_rows or not vehicle_rows or not resident_rows:
        raise RuntimeError("mysql raw tables are present but do not contain all required raw rows")

    if engine == "spark":
        slot_rows = _spark_materialize(slot_rows)
        vehicle_rows = _spark_materialize(vehicle_rows)
        resident_rows = _spark_materialize(resident_rows)
    else:
        slot_rows = [{str(k): "" if v is None else str(v) for k, v in row.items()} for row in slot_rows]
        vehicle_rows = [{str(k): "" if v is None else str(v) for k, v in row.items()} for row in vehicle_rows]
        resident_rows = [{str(k): "" if v is None else str(v) for k, v in row.items()} for row in resident_rows]

    return {
        "slot_status": slot_rows,
        "vehicle_event": vehicle_rows,
        "resident_pattern": resident_rows,
    }, "mysql_raw"


def _resolve_file_source(raw_dir: Path, external_dir: Path | None) -> tuple[dict[str, Path], str]:
    if external_dir is not None:
        ext_paths = {k: external_dir / v for k, v in REQUIRED_FILES.items()}
        if all(p.exists() for p in ext_paths.values()):
            return ext_paths, "external"

    raw_paths = {k: raw_dir / v for k, v in REQUIRED_FILES.items()}
    missing = [str(p) for p in raw_paths.values() if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing input files: {missing}")
    return raw_paths, "fallback_raw"


def _read_file_source(args: argparse.Namespace, engine: str) -> tuple[dict[str, list[dict[str, str]]], str, dict[str, str]]:
    raw_dir = Path(args.raw_dir)
    external_dir = Path(args.external_dir) if args.external_dir else None
    paths, source_mode = _resolve_file_source(raw_dir=raw_dir, external_dir=external_dir)
    read_fn = _read_csv_spark if engine == "spark" else _read_csv_python
    rows = {name: read_fn(path) for name, path in paths.items()}
    return rows, source_mode, {k: str(v) for k, v in paths.items()}


def _build_feature_tables(
    slot_rows: list[dict[str, str]],
    vehicle_rows: list[dict[str, str]],
    resident_rows: list[dict[str, str]],
    source_mode: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    region_slots: dict[str, set[str]] = defaultdict(set)
    slot_agg: dict[tuple[str, datetime], dict[str, float]] = defaultdict(
        lambda: {"slot_samples": 0.0, "occupied_count": 0.0}
    )

    ts_slot_total = 0
    ts_slot_ok = 0

    for row in slot_rows:
        region = (row.get("region_id") or "").strip()
        slot_id = (row.get("slot_id") or "").strip()
        dt = _parse_ts(row.get("ts") or row.get("event_ts") or "")
        ts_slot_total += 1
        if not region or not slot_id or dt is None:
            continue
        ts_slot_ok += 1
        dtb = _floor_15m(dt)
        region_slots[region].add(slot_id)
        key = (region, dtb)
        slot_agg[key]["slot_samples"] += 1.0
        slot_agg[key]["occupied_count"] += float(_safe_int(row.get("occupied"), 0))

    veh_agg: dict[tuple[str, datetime], dict[str, int]] = defaultdict(lambda: {"in": 0, "out": 0})
    ts_veh_total = 0
    ts_veh_ok = 0

    for row in vehicle_rows:
        region = (row.get("region_id") or "").strip()
        event_type = (row.get("event_type") or "").strip().lower()
        dt = _parse_ts(row.get("event_ts") or row.get("ts") or "")
        ts_veh_total += 1
        if not region or dt is None or event_type not in {"in", "out"}:
            continue
        ts_veh_ok += 1
        key = (region, _floor_15m(dt))
        veh_agg[key][event_type] += 1

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


def _build_analytics(
    forecast_rows: list[dict[str, Any]],
    vehicle_rows: list[dict[str, str]],
    resident_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    heatmap: dict[tuple[str, int], dict[str, float]] = defaultdict(lambda: {"occupancy_sum": 0.0, "count": 0.0})
    for row in forecast_rows:
        key = (str(row["region_id"]), int(row["hour_bucket"]))
        heatmap[key]["occupancy_sum"] += float(row["occupancy_rate"])
        heatmap[key]["count"] += 1.0

    occupancy_heatmap = []
    for (region, hour_bucket), agg in sorted(heatmap.items()):
        occupancy_heatmap.append(
            {
                "region_id": region,
                "hour_bucket": hour_bucket,
                "avg_occupancy_rate": round(agg["occupancy_sum"] / max(agg["count"], 1.0), 6),
                "sample_count": int(agg["count"]),
            }
        )

    vehicle_flow: dict[str, dict[str, int]] = defaultdict(lambda: {"in": 0, "out": 0})
    for row in vehicle_rows:
        region = (row.get("region_id") or "").strip()
        event_type = (row.get("event_type") or "").strip().lower()
        if region and event_type in {"in", "out"}:
            vehicle_flow[region][event_type] += 1

    vehicle_flow_summary = []
    for region, agg in sorted(vehicle_flow.items()):
        vehicle_flow_summary.append(
            {
                "region_id": region,
                "vehicle_in_count": agg["in"],
                "vehicle_out_count": agg["out"],
                "net_vehicle_flow": agg["in"] - agg["out"],
            }
        )

    resident_hour: dict[tuple[str, int], tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    for row in resident_rows:
        region = (row.get("home_region") or row.get("region_id") or "").strip()
        hour = _safe_int(row.get("hour_bucket"), -1)
        probability = _safe_float(row.get("trip_probability"), -1.0)
        if region and 0 <= hour <= 23 and probability >= 0.0:
            prev_sum, prev_count = resident_hour[(region, hour)]
            resident_hour[(region, hour)] = (prev_sum + probability, prev_count + 1)

    region_peak: dict[str, dict[str, Any]] = {}
    for (region, hour), (prob_sum, count) in resident_hour.items():
        avg = prob_sum / max(count, 1)
        current = region_peak.get(region)
        candidate = {
            "region_id": region,
            "peak_hour_bucket": hour,
            "avg_trip_probability": round(avg, 6),
            "sample_count": count,
        }
        if current is None or candidate["avg_trip_probability"] > current["avg_trip_probability"]:
            region_peak[region] = candidate

    resident_peak_summary = [region_peak[key] for key in sorted(region_peak)]
    return occupancy_heatmap, vehicle_flow_summary, resident_peak_summary


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


def _write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _detect_engine(requested: str) -> str:
    if requested in {"spark", "auto"}:
        try:
            import pyspark  # type: ignore  # noqa: F401

            return "spark"
        except Exception:
            if requested == "spark":
                raise
    return "python"


def _run(args: argparse.Namespace) -> dict[str, Any]:
    engine = _detect_engine(args.engine)
    inputs: dict[str, str] = {}

    source_mode = args.source_mode
    rows: dict[str, list[dict[str, str]]]

    if source_mode in {"mysql", "auto"}:
        try:
            rows, resolved_mode = _read_mysql_rows(args, engine)
            source_mode = resolved_mode
            inputs = {
                "slot_status": "mysql://sensor_event_raw",
                "vehicle_event": "mysql://lpr_event_raw",
                "resident_pattern": "mysql://resident_trip_raw",
            }
        except Exception:
            if args.source_mode == "mysql":
                raise
            rows, source_mode, inputs = _read_file_source(args, engine)
    else:
        rows, source_mode, inputs = _read_file_source(args, engine)

    forecast_rows, dispatch_rows, quality = _build_feature_tables(
        slot_rows=rows["slot_status"],
        vehicle_rows=rows["vehicle_event"],
        resident_rows=rows["resident_pattern"],
        source_mode=source_mode,
    )
    occupancy_heatmap, vehicle_flow_summary, resident_peak_summary = _build_analytics(
        forecast_rows,
        rows["vehicle_event"],
        rows["resident_pattern"],
    )

    forecast_output = Path(args.forecast_output)
    dispatch_output = Path(args.dispatch_output)
    quality_output = Path(args.quality_output)
    occupancy_output = Path(args.occupancy_output)
    vehicle_flow_output = Path(args.vehicle_flow_output)
    resident_peak_output = Path(args.resident_peak_output)

    _write_csv(forecast_output, forecast_rows)
    _write_csv(dispatch_output, dispatch_rows)
    _write_json(occupancy_output, occupancy_heatmap)
    _write_json(vehicle_flow_output, vehicle_flow_summary)
    _write_json(resident_peak_output, resident_peak_summary)

    report = {
        "generated_at": _now_iso(),
        "engine": engine,
        "source_mode": source_mode,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "inputs": inputs,
        "outputs": {
            "forecast_feature_table": str(forecast_output),
            "dispatch_input_table": str(dispatch_output),
            "occupancy_heatmap_summary": str(occupancy_output),
            "vehicle_flow_summary": str(vehicle_flow_output),
            "resident_peak_summary": str(resident_peak_output),
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
    parser.add_argument("--source-mode", choices=["auto", "files", "mysql"], default="auto")
    parser.add_argument("--mysql-host", default=os.getenv("STEP11_MYSQL_HOST", "127.0.0.1"))
    parser.add_argument("--mysql-port", type=int, default=int(os.getenv("STEP11_MYSQL_PORT", "13306")))
    parser.add_argument("--mysql-user", default=os.getenv("STEP11_MYSQL_USER", "sp_user"))
    parser.add_argument("--mysql-password", default=os.getenv("STEP11_MYSQL_PASSWORD", "sp_pass"))
    parser.add_argument("--mysql-database", default=os.getenv("STEP11_MYSQL_DATABASE", "smart_parking"))
    parser.add_argument("--forecast-output", default="data/processed/forecast_feature_table.csv")
    parser.add_argument("--dispatch-output", default="data/processed/dispatch_input_table.csv")
    parser.add_argument("--quality-output", default="reports/step11_etl_quality.json")
    parser.add_argument("--occupancy-output", default="reports/step26_occupancy_heatmap_summary.json")
    parser.add_argument("--vehicle-flow-output", default="reports/step26_vehicle_flow_summary.json")
    parser.add_argument("--resident-peak-output", default="reports/step26_resident_peak_summary.json")
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
