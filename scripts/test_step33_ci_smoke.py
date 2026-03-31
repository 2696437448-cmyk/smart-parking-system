#!/usr/bin/env python3
"""Step33 lightweight CI smoke gate."""

from __future__ import annotations

import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "step33_ci_smoke.json"


def run(cmd: str, cwd: Path | None = None, timeout: int = 300) -> tuple[bool, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, output


def assert_text(path: Path, pattern: str, description: str) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    matched = re.search(pattern, text, flags=re.MULTILINE) is not None
    if not matched:
        raise AssertionError(f"{description} missing in {path}")
    return {"name": description, "passed": True, "path": str(path)}


def main() -> None:
    checks: list[dict[str, object]] = []
    started = time.time()

    required_files = [
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".env.example",
        ROOT / "Makefile",
        ROOT / "scripts" / "preflight_check.sh",
        ROOT / "scripts" / "defense_demo.sh",
        ROOT / "scripts" / "test_step38_dashboard_contract_and_viewmodels.py",
        ROOT / "scripts" / "test_step39_dashboard_hardening.py",
        ROOT / "scripts" / "test_step40_release_acceptance.py",
        ROOT / "reports" / "step30_gate_results.json",
        ROOT / "apps" / "frontend" / "package.json",
    ]
    for path in required_files:
        exists = path.exists()
        checks.append({"name": f"exists:{path.relative_to(ROOT)}", "passed": exists})
        if not exists:
            raise AssertionError(f"required file missing: {path}")

    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
    jobs = workflow.get("jobs", {})
    for job in ("repo-smoke", "frontend-quality"):
        present = job in jobs
        checks.append({"name": f"workflow_job:{job}", "passed": present})
        if not present:
            raise AssertionError(f"workflow job missing: {job}")

    workflow_text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    for token in ["make step38-check", "make step39-check", "make step40-check"]:
        present = token in workflow_text
        checks.append({"name": f"workflow_token:{token}", "passed": present})
        if not present:
            raise AssertionError(f"workflow missing token: {token}")

    checks.append(assert_text(ROOT / "Makefile", r"^preflight-static:", "make target preflight-static"))
    checks.append(assert_text(ROOT / "Makefile", r"^ci-smoke:", "make target ci-smoke"))
    checks.append(assert_text(ROOT / "Makefile", r"^step38-check:", "make target step38-check"))
    checks.append(assert_text(ROOT / "Makefile", r"^step39-check:", "make target step39-check"))
    checks.append(assert_text(ROOT / "Makefile", r"^step40-check:", "make target step40-check"))
    checks.append(assert_text(ROOT / "scripts" / "defense_demo.sh", r"acceptance-step36", "demo script acceptance-step36 command"))
    checks.append(assert_text(ROOT / "README.md", r"Step25~40", "README Step25~40 roadmap"))
    checks.append(assert_text(ROOT / "README.md", r"make step38-check", "README step38 command"))
    checks.append(assert_text(ROOT / "README.md", r"python3 scripts/test_step40_release_acceptance.py", "README step40 command"))

    package = json.loads((ROOT / "apps" / "frontend" / "package.json").read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    for script_name in ("typecheck", "build"):
        present = script_name in scripts
        checks.append({"name": f"frontend_script:{script_name}", "passed": present})
        if not present:
            raise AssertionError(f"frontend script missing: {script_name}")

    step30_report = json.loads((ROOT / "reports" / "step30_gate_results.json").read_text(encoding="utf-8"))
    step30_ok = bool(step30_report.get("overall_passed"))
    checks.append({"name": "step30_report_overall_passed", "passed": step30_ok})
    if not step30_ok:
        raise AssertionError("step30 gate report must remain overall_passed=true")

    ok, output = run("bash -n scripts/defense_demo.sh scripts/preflight_check.sh scripts/create_release_bundle.sh")
    checks.append({"name": "bash_syntax_check", "passed": ok, "output_tail": "\n".join(output.splitlines()[-10:])})
    if not ok:
        raise AssertionError("bash syntax check failed")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.time() - started, 3),
        "overall_passed": all(bool(item["passed"]) for item in checks),
        "checks": checks,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"STEP33_GATE_PASS report={REPORT_PATH}")


if __name__ == "__main__":
    main()
