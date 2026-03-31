#!/usr/bin/env python3
"""Step40 release acceptance orchestrator."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "step40_gate_results.json"


def run(cmd: str, cwd: Path | None = None, timeout: int = 2400) -> tuple[bool, str, float]:
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, output, time.time() - started


def latest_bundle() -> tuple[str | None, str | None, str]:
    bundles = sorted((ROOT / "deliverables" / "bundles").glob("*.tar.gz"), reverse=True)
    if not bundles:
        return None, None, ""
    bundle = bundles[0]
    manifest = bundle.with_suffix("").with_suffix(".manifest.txt")
    manifest_text = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
    return str(bundle), str(manifest) if manifest.exists() else None, manifest_text


def assert_tokens(path: Path, tokens: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{path} missing token: {token}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static-only", action="store_true", help="Skip runtime-dependent Step37/39 smoke checks.")
    args = parser.parse_args()

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
        print(f"STEP40_GATE_FAIL failed=step30_report_still_passed report={REPORT_PATH}")
        raise SystemExit(1)

    commands: list[tuple[str, str, Path]] = [
        ("step36_release_acceptance", "python3 scripts/test_step36_release_acceptance.py", ROOT),
        ("step38_dashboard_contract_and_viewmodels", "python3 scripts/test_step38_dashboard_contract_and_viewmodels.py", ROOT),
        (
            "step39_dashboard_hardening",
            "python3 scripts/test_step39_dashboard_hardening.py --require-runtime" if not args.static_only else "python3 scripts/test_step39_dashboard_hardening.py",
            ROOT,
        ),
        ("step40_release_bundle", "./scripts/create_release_bundle.sh step40", ROOT),
    ]
    if not args.static_only:
        commands.insert(1, ("step37_prompt_frontend_modernization", "python3 scripts/test_step37_prompt_frontend_modernization.py", ROOT))

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
            REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"STEP40_GATE_FAIL failed={name} report={REPORT_PATH}")
            raise SystemExit(1)

    if args.static_only:
        for path in [
            ROOT / "memory-bank" / "project-prompt-library.md",
            ROOT / "memory-bank" / "prompt-templates.md",
            ROOT / "reports" / "step37_execution.md",
            ROOT / "scripts" / "test_step37_prompt_frontend_modernization.py",
        ]:
            passed = path.exists()
            steps.append({"name": f"exists:{path.relative_to(ROOT)}", "passed": passed, "elapsed_seconds": 0.0})
            if not passed:
                REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"STEP40_GATE_FAIL failed=exists:{path.relative_to(ROOT)} report={REPORT_PATH}")
                raise SystemExit(1)

    doc_expectations = {
        ROOT / "README.md": ["当前稳定默认完成态：`Step40`", "Step25~40 完成情况", "make step38-check", "python3 scripts/test_step40_release_acceptance.py"],
        ROOT / "docs" / "defense_demo_runbook.md": ["Step40 默认完成态", "acceptance-step36", "python3 scripts/test_step40_release_acceptance.py"],
        ROOT / "deliverables" / "README.md": ["Step40", "make release-bundle"],
        ROOT / "memory-bank" / "implementation-plan.md": ["Step40 定义为“当前默认完成态”", "## Step38", "## Step39", "## Step40"],
        ROOT / "memory-bank" / "acceptance.md": ["Step40 默认完成态", "## 17. Step38", "## 18. Step39", "## 19. Step40"],
        ROOT / "memory-bank" / "architecture.md": ["Step40 默认完成态", "## 10. Step38 合同与体验收敛层", "## 11. Step39 聚合层与性能硬化", "## 12. 默认完成态升级规则"],
        ROOT / "memory-bank" / "gap-matrix.md": ["Step40 默认完成态", "### 5.7 Step38", "### 5.8 Step39", "### 5.9 Step40"],
        ROOT / "memory-bank" / "project-prompt-library.md": ["Step40", "Post-Step40"],
        ROOT / "memory-bank" / "prompt-templates.md": ["Step40", "Step40-approved"],
        ROOT / "memory-bank" / "progress.md": ["Step 38", "Step 39", "Step 40"],
        ROOT / "reports" / "step38_execution.md": ["Step38", "OpenAPI", "ViewStateNotice"],
        ROOT / "reports" / "step39_execution.md": ["Step39", "vendor-echarts", "ParkingDashboardViewModules.java"],
        ROOT / "reports" / "step40_technical_acceptance.md": ["Step40", "默认完成态升级到 Step40", "step40_gate_results.json"],
    }
    for path, tokens in doc_expectations.items():
        assert_tokens(path, tokens)
        steps.append({"name": f"doc_alignment:{path.relative_to(ROOT)}", "passed": True, "elapsed_seconds": 0.0})

    bundle_path, manifest_path, manifest_text = latest_bundle()
    bundle_ok = bool(bundle_path and manifest_path and "step40" in Path(bundle_path).name and "reports/step40_technical_acceptance.md" in manifest_text)
    steps.append(
        {
            "name": "latest_release_bundle_is_step40",
            "command": "inspect deliverables/bundles",
            "passed": bundle_ok,
            "elapsed_seconds": 0.0,
            "output_tail": f"bundle={bundle_path} manifest={manifest_path}",
        }
    )
    if not bundle_ok:
        REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"STEP40_GATE_FAIL failed=latest_release_bundle_is_step40 report={REPORT_PATH}")
        raise SystemExit(1)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": all(bool(step["passed"]) for step in steps),
        "mode": "static-only" if args.static_only else "full",
        "steps": steps,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"STEP40_GATE_PASS report={REPORT_PATH}")


if __name__ == "__main__":
    main()
