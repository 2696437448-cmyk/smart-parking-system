#!/usr/bin/env python3
"""Step35 security and config hardening gate."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "step35_gate_results.json"


def run(cmd: list[str]) -> tuple[bool, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, output


def require_regex(path: Path, pattern: str, description: str, checks: list[dict[str, object]]) -> None:
    text = path.read_text(encoding="utf-8")
    matched = re.search(pattern, text, flags=re.MULTILINE) is not None
    checks.append({"name": description, "passed": matched, "path": str(path.relative_to(ROOT))})
    if not matched:
        raise AssertionError(f"{description} missing in {path}")


def require_absent(path: Path, pattern: str, description: str, checks: list[dict[str, object]]) -> None:
    text = path.read_text(encoding="utf-8")
    absent = re.search(pattern, text, flags=re.MULTILINE) is None
    checks.append({"name": description, "passed": absent, "path": str(path.relative_to(ROOT))})
    if not absent:
        raise AssertionError(f"{description} still present in {path}")


def main() -> None:
    checks: list[dict[str, object]] = []

    required = [
        ROOT / ".env.secure.example",
        ROOT / "docs" / "security_hardening.md",
        ROOT / "scripts" / "security_scan.py",
        ROOT / "scripts" / "test_step35_security_config.py",
    ]
    for path in required:
        exists = path.exists()
        checks.append({"name": f"exists:{path.relative_to(ROOT)}", "passed": exists})
        if not exists:
            raise AssertionError(f"required file missing: {path}")

    require_regex(ROOT / ".env.example", r"Demo/local defaults only", "root env warns about demo defaults", checks)
    require_regex(ROOT / ".env.secure.example", r"CHANGE_ME_", "secure env uses rotate-me placeholders", checks)
    require_regex(ROOT / ".env.secure.example", r"GF_ADMIN_PASSWORD", "secure env includes grafana credentials", checks)
    require_regex(ROOT / ".env.secure.example", r"RABBITMQ_DEFAULT_PASS", "secure env includes rabbitmq credentials", checks)
    require_regex(ROOT / "infra" / "docker-compose.yml", r"RABBITMQ_DEFAULT_USER: \$\{RABBITMQ_DEFAULT_USER:-guest\}", "compose parameterizes rabbit user", checks)
    require_regex(ROOT / "infra" / "docker-compose.yml", r"RABBITMQ_DEFAULT_PASS: \$\{RABBITMQ_DEFAULT_PASS:-guest\}", "compose parameterizes rabbit password", checks)
    require_regex(ROOT / "infra" / "docker-compose.yml", r"GF_SECURITY_ADMIN_USER: \$\{GF_ADMIN_USER:-admin\}", "compose parameterizes grafana user", checks)
    require_regex(ROOT / "infra" / "docker-compose.yml", r"GF_SECURITY_ADMIN_PASSWORD: \$\{GF_ADMIN_PASSWORD:-admin\}", "compose parameterizes grafana password", checks)
    require_absent(ROOT / "scripts" / "defense_demo.sh", r"guest/guest|admin/admin", "demo script no longer prints default passwords", checks)
    require_regex(ROOT / ".gitignore", r"^\.env$", "gitignore protects root .env", checks)
    require_regex(ROOT / ".gitignore", r"^apps/frontend/\.env\.local$", "gitignore protects frontend env local", checks)
    require_regex(ROOT / "README.md", r"\.env\.secure\.example", "README mentions secure env template", checks)
    require_regex(ROOT / "README.md", r"security-scan", "README mentions security scan command", checks)
    require_regex(ROOT / "docs" / "security_hardening.md", r"凭证轮换", "security doc includes rotation guidance", checks)
    require_regex(ROOT / "docs" / "security_hardening.md", r"恢复建议", "security doc includes recovery guidance", checks)

    ok, output = run(["python3", "scripts/security_scan.py"])
    checks.append({"name": "security_scan", "passed": ok, "output_tail": "\n".join(output.splitlines()[-10:])})
    if not ok:
        raise AssertionError("security scan failed")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": all(bool(item["passed"]) for item in checks),
        "checks": checks,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"STEP35_GATE_PASS report={REPORT_PATH}")


if __name__ == "__main__":
    main()
