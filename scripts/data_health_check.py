#!/usr/bin/env python3
"""Data health checker for Step 0 baseline."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


@dataclass
class SourceConfig:
    name: str
    path: str
    required_columns: list[str]
    key_columns: list[str]
    ts_columns: list[str]
    critical_columns: list[str]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_frame(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported format: {path}")


def _safe_rate(numerator: int, denominator: int) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def _analyze_source(cfg: SourceConfig, base_dir: Path) -> dict[str, Any]:
    source_path = (base_dir / cfg.path).resolve()
    result: dict[str, Any] = {
        "name": cfg.name,
        "path": str(source_path),
        "exists": source_path.exists(),
    }
    if not source_path.exists():
        result["error"] = "source file missing"
        return result

    df = _load_frame(source_path)
    row_count = len(df)
    columns = set(df.columns.tolist())
    required_set = set(cfg.required_columns)
    missing_required = sorted(required_set - columns)
    required_completeness = _safe_rate(
        len(cfg.required_columns) - len(missing_required),
        len(cfg.required_columns),
    )

    duplicate_count = int(df.duplicated(subset=cfg.key_columns).sum()) if cfg.key_columns else 0
    duplicate_rate = _safe_rate(duplicate_count, row_count)

    critical_present = [c for c in cfg.critical_columns if c in df.columns]
    if critical_present and row_count:
        critical_null_rate = float(df[critical_present].isna().any(axis=1).mean())
    else:
        critical_null_rate = 0.0

    ts_parse_success = {}
    for col in cfg.ts_columns:
        if col not in df.columns:
            ts_parse_success[col] = 0.0
            continue
        parsed = pd.to_datetime(df[col], errors="coerce")
        non_null = int(df[col].notna().sum())
        ok = int(parsed.notna().sum())
        ts_parse_success[col] = _safe_rate(ok, non_null) if non_null else 1.0

    result.update(
        {
            "row_count": row_count,
            "column_count": len(df.columns),
            "missing_required_columns": missing_required,
            "required_completeness": required_completeness,
            "duplicate_count": duplicate_count,
            "duplicate_rate": duplicate_rate,
            "critical_null_rate": critical_null_rate,
            "timestamp_parse_success": ts_parse_success,
        }
    )
    return result


def _evaluate_thresholds(
    source_result: dict[str, Any],
    thresholds: dict[str, float],
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not source_result.get("exists", False):
        reasons.append("source_missing")
        return False, reasons

    if source_result["required_completeness"] < thresholds["required_completeness_min"]:
        reasons.append("required_completeness_below_threshold")
    if source_result["duplicate_rate"] > thresholds["duplicate_rate_max"]:
        reasons.append("duplicate_rate_above_threshold")
    if source_result["critical_null_rate"] > thresholds["critical_null_rate_max"]:
        reasons.append("critical_null_rate_above_threshold")

    ts_stats = source_result.get("timestamp_parse_success", {})
    for col, score in ts_stats.items():
        if score < thresholds["timestamp_parse_success_min"]:
            reasons.append(f"timestamp_parse_rate_low:{col}")
    return len(reasons) == 0, reasons


def _render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Data Health Report",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- overall_passed: {report['overall_passed']}",
        "",
        "## Thresholds",
        "",
        f"- required_completeness_min: {report['thresholds']['required_completeness_min']}",
        f"- duplicate_rate_max: {report['thresholds']['duplicate_rate_max']}",
        f"- critical_null_rate_max: {report['thresholds']['critical_null_rate_max']}",
        f"- timestamp_parse_success_min: {report['thresholds']['timestamp_parse_success_min']}",
        "",
        "## Source Results",
        "",
    ]
    for src in report["sources"]:
        lines.extend(
            [
                f"### {src['name']}",
                "",
                f"- exists: {src.get('exists', False)}",
                f"- path: {src.get('path', '')}",
            ]
        )
        if not src.get("exists", False):
            lines.append(f"- error: {src.get('error', 'unknown')}")
            lines.append("")
            continue

        lines.extend(
            [
                f"- row_count: {src['row_count']}",
                f"- column_count: {src['column_count']}",
                f"- required_completeness: {src['required_completeness']:.4f}",
                f"- duplicate_rate: {src['duplicate_rate']:.4f}",
                f"- critical_null_rate: {src['critical_null_rate']:.4f}",
                f"- timestamp_parse_success: {json.dumps(src['timestamp_parse_success'], ensure_ascii=False)}",
                f"- passed: {src['passed']}",
                f"- failed_reasons: {', '.join(src['failed_reasons']) if src['failed_reasons'] else 'none'}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run data health baseline checks.")
    parser.add_argument(
        "--schema-config",
        default="config/data_health_schema.yaml",
        help="Path to YAML config that defines sources and thresholds.",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root for resolving relative source paths.",
    )
    parser.add_argument(
        "--json-output",
        default="reports/data_health_report.json",
        help="JSON report output path.",
    )
    parser.add_argument(
        "--md-output",
        default="reports/data_health_report.md",
        help="Markdown report output path.",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    schema_path = (root / args.schema_config).resolve()
    cfg = _load_yaml(schema_path)

    sources = [
        SourceConfig(
            name=item["name"],
            path=item["path"],
            required_columns=item.get("required_columns", []),
            key_columns=item.get("key_columns", []),
            ts_columns=item.get("ts_columns", []),
            critical_columns=item.get("critical_columns", []),
        )
        for item in cfg.get("sources", [])
    ]
    thresholds = cfg.get("thresholds", {})

    report_sources = []
    overall_passed = True
    for src_cfg in sources:
        result = _analyze_source(src_cfg, root)
        passed, reasons = _evaluate_thresholds(result, thresholds)
        result["passed"] = passed
        result["failed_reasons"] = reasons
        overall_passed = overall_passed and passed
        report_sources.append(result)

    report = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "overall_passed": overall_passed,
        "thresholds": thresholds,
        "sources": report_sources,
    }

    json_output = (root / args.json_output).resolve()
    md_output = (root / args.md_output).resolve()
    json_output.parent.mkdir(parents=True, exist_ok=True)
    md_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_output.write_text(_render_markdown(report), encoding="utf-8")

    print(f"overall_passed={overall_passed}")
    print(f"json_report={json_output}")
    print(f"md_report={md_output}")


if __name__ == "__main__":
    main()

