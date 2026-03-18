#!/usr/bin/env python3
"""Step23 gate: demo entry points must target business pages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    targets = [
        ROOT / "scripts" / "defense_demo.sh",
        ROOT / "README.md",
        ROOT / "docs" / "defense_demo_runbook.md",
    ]
    required_tokens = [
        "http://localhost:4173/owner/dashboard",
        "http://localhost:4173/admin/monitor",
    ]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                raise AssertionError(f"{path} missing token: {token}")
    script_text = (ROOT / "scripts" / "defense_demo.sh").read_text(encoding="utf-8")
    for token in ["npm run build", "npm run preview", "RabbitMQ UI (ops)"]:
        if token not in script_text:
            raise AssertionError(f"demo script missing token: {token}")
    print("STEP23_GATE_PASS")


if __name__ == "__main__":
    main()
