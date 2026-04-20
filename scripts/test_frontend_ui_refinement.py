#!/usr/bin/env python3
"""Regression gate for the final-round frontend UI refinement work."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"

REQUIRED_FILES = [
    "src/components/ActionBar.vue",
    "src/components/KeyValueList.vue",
    "src/components/StatusBadge.vue",
    "src/presenters/format.ts",
    "src/presenters/owner.ts",
    "src/presenters/admin.ts",
]

REQUIRED_TOKENS = {
    "src/pages/OwnerDashboard.vue": ["ActionBar", "StatusBadge", "ownerDashboardHero"],
    "src/pages/OwnerOrders.vue": ["KeyValueList", "StatusBadge"],
    "src/pages/OwnerNavigation.vue": ["KeyValueList", "routeSummaryLines"],
    "src/pages/AdminMonitor.vue": ["ActionBar", "adminChartCards", "StatusBadge"],
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
