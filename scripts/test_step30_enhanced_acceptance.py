#!/usr/bin/env python3
"""Step30 enhanced acceptance orchestrator."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "step30_gate_results.json"


def run(cmd: str, cwd: Path | None = None, timeout: int = 1800) -> tuple[bool, str, float]:
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
    steps: list[dict[str, object]] = []
    commands = [
        ("step24_default_acceptance", "python3 scripts/test_step24_full_acceptance.py", ROOT),
        ("step26_raw_ingest_analytics", "python3 scripts/test_step26_raw_ingest_analytics.py", ROOT),
        ("frontend_typecheck", "npm run typecheck", ROOT / "apps" / "frontend"),
        ("frontend_build", "npm run build", ROOT / "apps" / "frontend"),
        ("step27_app_shell", "python3 scripts/test_step27_app_shell.py", ROOT),
        ("step28_navigation_map", "python3 scripts/test_step28_navigation_map.py", ROOT),
        ("step29_admin_charts", "python3 scripts/test_step29_admin_charts.py", ROOT),
        ("openapi_validation", "python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml", ROOT),
    ]

    for name, cmd, cwd in commands:
        ok, output, elapsed = run(cmd, cwd=cwd)
        steps.append(
            {
                "name": name,
                "command": cmd,
                "passed": ok,
                "elapsed_seconds": round(elapsed, 3),
                "output_tail": "\n".join(output.splitlines()[-10:]),
            }
        )
        if not ok:
            break

    overall_passed = all(bool(step["passed"]) for step in steps)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": overall_passed,
        "steps": steps,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if overall_passed:
        print(f"STEP30_GATE_PASS report={REPORT_PATH}")
    else:
        failed = next((str(step["name"]) for step in steps if not step["passed"]), "unknown")
        print(f"STEP30_GATE_FAIL failed={failed} report={REPORT_PATH}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
