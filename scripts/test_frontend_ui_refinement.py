#!/usr/bin/env python3
"""Regression gate for the final-round frontend UI refinement work."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"

REQUIRED_FILES = [
    "src/components/MetricCard.vue",
    "src/components/SectionHeader.vue",
    "src/components/ViewStateNotice.vue",
    "src/presenters/format.ts",
    "src/presenters/owner.ts",
    "src/presenters/admin.ts",
]

REQUIRED_TOKENS = {
    "src/pages/OwnerDashboard.vue": ["dashboard-grid", "form-panel", "recommendation-panel", "首页"],
    "src/pages/OwnerOrders.vue": ["orders-grid", "order-status-card", "billing-panel", "订单"],
    "src/pages/OwnerNavigation.vue": ["navigation-grid", "route-panel", "map-panel", "导航"],
    "src/pages/AdminMonitor.vue": ["admin-summary-board", "admin-main-chart", "admin-side-cards", "物业监管"],
}


def main() -> None:
    for rel in REQUIRED_FILES:
        path = FRONTEND / rel
        if not path.exists():
            raise AssertionError(f"missing required refinement file: {path}")

    for rel, tokens in REQUIRED_TOKENS.items():
        text = (FRONTEND / rel).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                raise AssertionError(f"{rel} missing token: {token}")

    print("FRONTEND_UI_REFINEMENT_PASS")


if __name__ == "__main__":
    main()
