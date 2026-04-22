#!/usr/bin/env python3
"""Step43 gate: simplified bright Chinese UI structure exists."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"

REQUIRED_TOKENS = {
    "src/layouts/OwnerLayout.vue": ["owner-sidebar", "首页", "订单", "导航"],
    "src/layouts/AdminLayout.vue": ["admin-header", "物业监管"],
    "src/pages/AdminMonitor.vue": ["admin-summary-board", "admin-main-chart", "admin-side-cards"],
    "src/styles/tokens.css": ["--color-surface-card", "--color-brand-primary", "--color-brand-success"],
}


def main() -> None:
    for rel, tokens in REQUIRED_TOKENS.items():
        text = (FRONTEND / rel).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                raise AssertionError(f"{rel} missing token: {token}")

    print("STEP43_SIMPLE_BRIGHT_UI_PASS")


if __name__ == "__main__":
    main()
