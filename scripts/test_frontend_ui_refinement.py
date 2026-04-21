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
    "src/pages/OwnerDashboard.vue": ["owner-smart-grid", "a-form", "a-button", "智能预约中枢"],
    "src/pages/OwnerOrders.vue": ["order-task-flow", "a-button", "订单与账单任务流"],
    "src/pages/OwnerNavigation.vue": ["navigation-task-panel", "MapPreview", "目标车位导航"],
    "src/pages/AdminMonitor.vue": ["operations-cockpit", "EChartPanel", "停车运营驾驶舱"],
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
