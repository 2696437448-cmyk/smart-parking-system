#!/usr/bin/env python3
"""Step35 repository security scan."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "step35_security_scan.json"

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    ("github_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("github_token", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
]

TEXT_SUFFIX_ALLOWLIST = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".sh",
    ".ts",
    ".js",
    ".vue",
    ".xml",
    ".properties",
    ".gradle",
    ".conf",
    ".sql",
    ".env",
    "",
}


def tracked_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    files: list[Path] = []
    for raw in proc.stdout.splitlines():
        rel = Path(raw)
        if any(part in {"apps/frontend/node_modules", "apps/frontend/dist", "deliverables/bundles"} for part in rel.parts):
            continue
        files.append(ROOT / rel)
    return files


def scan() -> dict[str, object]:
    findings: list[dict[str, object]] = []
    tracked = tracked_files()

    for path in tracked:
        rel = path.relative_to(ROOT)
        name = path.name
        if name in {".env", ".env.local", ".env.secure.local"}:
            findings.append({"type": "tracked_local_env", "path": str(rel), "detail": "local override file must not be tracked"})
            continue

        suffix = path.suffix.lower()
        if suffix not in TEXT_SUFFIX_ALLOWLIST and name not in {".gitignore", ".env.example", ".env.secure.example"}:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for finding_type, pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append(
                    {
                        "type": finding_type,
                        "path": str(rel),
                        "detail": match.group(0)[:80],
                    }
                )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": not findings,
        "finding_count": len(findings),
        "findings": findings,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    report = scan()
    if report["overall_passed"]:
        print(f"STEP35_SECURITY_SCAN_PASS report={REPORT_PATH}")
        return
    print(f"STEP35_SECURITY_SCAN_FAIL report={REPORT_PATH}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
