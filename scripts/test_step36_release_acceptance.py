#!/usr/bin/env python3
"""Step36 release acceptance orchestrator."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "step36_gate_results.json"


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
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, output, elapsed


def latest_bundle() -> tuple[str | None, str | None]:
    bundles = sorted((ROOT / "deliverables" / "bundles").glob("*.tar.gz"), reverse=True)
    if not bundles:
        return None, None
    bundle = bundles[0]
    manifest = bundle.with_suffix("").with_suffix(".manifest.txt")
    return str(bundle), str(manifest) if manifest.exists() else None


def main() -> None:
    steps: list[dict[str, object]] = []

    step30_report = json.loads((ROOT / "reports" / "step30_gate_results.json").read_text(encoding="utf-8"))
    step30_ok = bool(step30_report.get("overall_passed"))
    steps.append(
        {
            "name": "step30_report_still_passed",
            "command": "validate reports/step30_gate_results.json",
            "passed": step30_ok,
            "elapsed_seconds": 0.0,
            "output_tail": f"overall_passed={step30_ok}",
        }
    )
    if not step30_ok:
        REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"STEP36_GATE_FAIL failed=step30_report_still_passed report={REPORT_PATH}")
        raise SystemExit(1)

    commands = [
        ("step33_ci_smoke", "make ci-smoke", ROOT),
        ("step35_security_scan", "make security-scan", ROOT),
        ("step34_release_bundle", "make release-bundle", ROOT),
    ]

    for name, cmd, cwd in commands:
        ok, output, elapsed = run(cmd, cwd=cwd)
        steps.append(
            {
                "name": name,
                "command": cmd,
                "passed": ok,
                "elapsed_seconds": round(elapsed, 3),
                "output_tail": "\n".join(output.splitlines()[-12:]),
            }
        )
        if not ok:
            break

    if all(bool(step["passed"]) for step in steps):
        bundle_path, manifest_path = latest_bundle()
        bundle_ok = bool(bundle_path and manifest_path)
        steps.append(
            {
                "name": "latest_release_bundle_present",
                "command": "inspect deliverables/bundles",
                "passed": bundle_ok,
                "elapsed_seconds": 0.0,
                "output_tail": f"bundle={bundle_path} manifest={manifest_path}",
            }
        )

    overall_passed = all(bool(step["passed"]) for step in steps)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": overall_passed,
        "steps": steps,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if overall_passed:
        print(f"STEP36_GATE_PASS report={REPORT_PATH}")
    else:
        failed = next((str(step["name"]) for step in steps if not step["passed"]), "unknown")
        print(f"STEP36_GATE_FAIL failed={failed} report={REPORT_PATH}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
