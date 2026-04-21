#!/usr/bin/env python3
"""Step42 gate: shadcn-inspired product UI structure exists."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"

REQUIRED_TOKENS = {
    "src/layouts/AdminLayout.vue": ["admin-sidebar-shell", "admin-page-header", "admin-sidebar-footer"],
    "src/layouts/OwnerLayout.vue": ["owner-journey-header", "owner-nav-pill", "owner-mobile-dock"],
    "src/components/SectionHeader.vue": ["section-header-actions", "section-header-kicker"],
    "src/components/MetricCard.vue": ["metric-card-trend", "metric-card-meta"],
    "src/pages/AdminMonitor.vue": ["operations-primary-grid", "operations-secondary-grid", "primary-chart-card"],
}


def main() -> None:
    for rel, tokens in REQUIRED_TOKENS.items():
        text = (FRONTEND / rel).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                raise AssertionError(f"{rel} missing token: {token}")

    print("STEP42_SHADCN_UI_POLISH_PASS")


if __name__ == "__main__":
    main()
