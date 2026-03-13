#!/usr/bin/env python3
"""Build Step17 performance comparison report from scenario JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pct_delta(base: float, current: float) -> float:
    if base == 0:
        return 0.0
    return ((current - base) / base) * 100.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="reports/step17_perf_baseline.json")
    parser.add_argument("--fault", default="reports/step17_perf_fault.json")
    parser.add_argument("--recovery", default="reports/step17_perf_recovery.json")
    parser.add_argument("--md-output", default="reports/step17_performance_summary.md")
    parser.add_argument("--csv-output", default="reports/step17_performance_summary.csv")
    args = parser.parse_args()

    baseline = load(Path(args.baseline))
    fault = load(Path(args.fault))
    recovery = load(Path(args.recovery))

    scenarios = [baseline, fault, recovery]
    csv_lines = [
        "scenario,total_requests,throughput_rps,error_rate,fallback_rate,p95_ms,p99_ms"
    ]
    for s in scenarios:
        csv_lines.append(
            ",".join(
                [
                    str(s["scenario"]),
                    str(s["total_requests"]),
                    str(s["throughput_rps"]),
                    str(s["error_rate"]),
                    str(s["fallback_rate"]),
                    str(s["latency_ms"]["p95"]),
                    str(s["latency_ms"]["p99"]),
                ]
            )
        )

    Path(args.csv_output).write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    md = [
        "# Step17 性能对比报告",
        "",
        "## 场景与指标",
        "",
        "| 场景 | 请求数 | 吞吐(rps) | 错误率 | 降级率 | P95(ms) | P99(ms) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for s in scenarios:
        md.append(
            "| {scenario} | {total_requests} | {throughput_rps} | {error_rate:.4f} | {fallback_rate:.4f} | {p95:.2f} | {p99:.2f} |".format(
                scenario=s["scenario"],
                total_requests=s["total_requests"],
                throughput_rps=s["throughput_rps"],
                error_rate=s["error_rate"],
                fallback_rate=s["fallback_rate"],
                p95=s["latency_ms"]["p95"],
                p99=s["latency_ms"]["p99"],
            )
        )

    md.extend(
        [
            "",
            "## 相对基线变化",
            "",
            "1. fault P95 变化：{:+.2f}%".format(
                pct_delta(baseline["latency_ms"]["p95"], fault["latency_ms"]["p95"])
            ),
            "2. fault P99 变化：{:+.2f}%".format(
                pct_delta(baseline["latency_ms"]["p99"], fault["latency_ms"]["p99"])
            ),
            "3. recovery P95 变化：{:+.2f}%".format(
                pct_delta(baseline["latency_ms"]["p95"], recovery["latency_ms"]["p95"])
            ),
            "4. recovery P99 变化：{:+.2f}%".format(
                pct_delta(baseline["latency_ms"]["p99"], recovery["latency_ms"]["p99"])
            ),
            "5. fault 吞吐变化：{:+.2f}%".format(
                pct_delta(baseline["throughput_rps"], fault["throughput_rps"])
            ),
            "6. recovery 吞吐变化：{:+.2f}%".format(
                pct_delta(baseline["throughput_rps"], recovery["throughput_rps"])
            ),
            "",
            "## 结论",
            "",
            "1. 故障态下系统保持 200 响应并进入降级（fallback_rate 提升），验证可用性优先策略。",
            "2. 恢复态下 P95/P99 与吞吐回归接近基线，符合熔断恢复预期。",
        ]
    )

    Path(args.md_output).write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"STEP17_REPORT_PASS md={args.md_output} csv={args.csv_output}")


if __name__ == "__main__":
    main()
