#!/usr/bin/env python3
"""Step18 full acceptance orchestrator.

Runs Step4~Step10 baseline gates and Step11~Step17 alignment gates, then
writes a machine-readable result summary to reports/step18_gate_results.json.
"""

from __future__ import annotations

import json
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "step18_gate_results.json"


def run(cmd: str, timeout: int = 600) -> tuple[bool, str, float]:
    start = time.time()
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = time.time() - start
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, output.strip(), elapsed


def main() -> None:
    steps: list[dict] = []

    commands = [
        ("compose_config", "docker compose -f infra/docker-compose.yml config >/tmp/spt_step18_compose_config_check.txt"),
        ("step3_gateway", "python3 scripts/test_step3_gateway.py"),
        ("step4_consistency", "python3 scripts/test_step4_consistency.py"),
        ("step5_model_core", "python3 scripts/test_step5_model_core.py"),
        ("step11_etl", "python3 scripts/test_step11_etl.py"),
        ("step12_training", "python3 scripts/test_step12_model_training.py"),
        ("step13_registry", "python3 scripts/test_step13_model_registry.py"),
        ("step14_java_consistency", "python3 scripts/test_step14_java_consistency.py"),
        ("step16_frontend_engineering", "python3 scripts/test_step16_frontend_engineering.py"),
        ("step17_observability_performance", "python3 scripts/test_step17_observability_performance.py"),
        ("openapi_validation", "python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml"),
    ]

    for name, cmd in commands:
        ok, output, elapsed = run(cmd)
        steps.append(
            {
                "name": name,
                "command": cmd,
                "passed": ok,
                "elapsed_seconds": round(elapsed, 3),
                "output_tail": "\n".join(output.splitlines()[-8:]),
            }
        )
        if not ok:
            break

    # Scenario-specific gates that require service state toggles.
    if all(s["passed"] for s in steps):
        extra = [
            (
                "step8_realtime",
                "python3 scripts/test_step8_realtime_channel.py --mode realtime --ws-host localhost --ws-port 8090 --ws-path /ws/status --poll-url http://localhost:8080/api/v1/admin/realtime/status",
            ),
            (
                "step9_baseline",
                "python3 scripts/test_step9_observability.py --mode baseline",
            ),
            (
                "stop_model_for_step6_15",
                "docker compose -f infra/docker-compose.yml stop model-service",
            ),
            (
                "step6_resilience",
                "python3 scripts/test_step6_resilience.py",
            ),
            (
                "step15_governance",
                "python3 scripts/test_step15_gateway_governance.py",
            ),
            (
                "start_model_after_step6_15",
                "docker compose -f infra/docker-compose.yml start model-service",
            ),
            (
                "step9_fault",
                "docker compose -f infra/docker-compose.yml stop model-service && python3 scripts/test_step9_observability.py --mode fault && docker compose -f infra/docker-compose.yml start model-service",
            ),
            (
                "step7_reliability",
                "python3 scripts/setup_rabbitmq.py --api http://localhost:15672/api --user guest --password guest >/tmp/spt_step18_setup_rabbitmq.log && python3 services/dispatch_worker.py --api http://localhost:15672/api --user guest --password guest --max-retry 2 --max-cycles 240 >/tmp/spt_step18_worker.log 2>&1 & WORKER_PID=$!; sleep 1; python3 scripts/test_step7_mq_reliability.py --rabbit-api http://localhost:15672/api --user guest --password guest --gateway http://localhost:8080; kill $WORKER_PID >/dev/null 2>&1 || true; wait $WORKER_PID 2>/dev/null || true",
            ),
            (
                "step8_fallback",
                "docker compose -f infra/docker-compose.yml stop realtime-service && python3 scripts/test_step8_realtime_channel.py --mode fallback --ws-host localhost --ws-port 8090 --ws-path /ws/status --poll-url http://localhost:8080/api/v1/admin/realtime/status && docker compose -f infra/docker-compose.yml start realtime-service",
            ),
        ]

        for name, cmd in extra:
            ok, output, elapsed = run(cmd)
            steps.append(
                {
                    "name": name,
                    "command": cmd,
                    "passed": ok,
                    "elapsed_seconds": round(elapsed, 3),
                    "output_tail": "\n".join(output.splitlines()[-8:]),
                }
            )
            if not ok:
                break

    overall_passed = all(s["passed"] for s in steps)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": overall_passed,
        "steps": steps,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if overall_passed:
        print(f"STEP18_GATE_PASS report={REPORT_PATH}")
    else:
        failed = next((s["name"] for s in steps if not s["passed"]), "unknown")
        print(f"STEP18_GATE_FAIL failed={failed} report={REPORT_PATH}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
