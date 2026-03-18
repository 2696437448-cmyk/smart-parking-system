#!/usr/bin/env python3
"""Step24 full acceptance orchestrator."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "step24_gate_results.json"


def run(cmd: str, cwd: Path | None = None, timeout: int = 900) -> tuple[bool, str, float]:
    start = time.time()
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
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
        ("step18_legacy", "python3 scripts/test_step18_full_acceptance.py"),
        ("step19a_spark_strict", "python3 scripts/test_step19a_spark_strict.py"),
        ("step19b_hungarian", "python3 scripts/test_step19b_hungarian.py"),
        ("step20_22_billing_revenue", "python3 scripts/test_step20_billing_revenue.py"),
        ("step21_frontend_pages", "python3 scripts/test_step21_frontend_pages.py"),
        ("frontend_typecheck", "npm run typecheck"),
        ("frontend_build", "npm run build"),
        ("step23_demo_entry", "python3 scripts/test_step23_demo_entry.py"),
        ("openapi_validation", "python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml"),
    ]

    for name, cmd in commands:
        cwd = ROOT / "apps" / "frontend" if name.startswith("frontend_") else ROOT
        ok, output, elapsed = run(cmd, cwd=cwd)
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

    overall_passed = all(step["passed"] for step in steps)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": overall_passed,
        "steps": steps,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if overall_passed:
        print(f"STEP24_GATE_PASS report={REPORT_PATH}")
    else:
        failed = next((step["name"] for step in steps if not step["passed"]), "unknown")
        print(f"STEP24_GATE_FAIL failed={failed} report={REPORT_PATH}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
