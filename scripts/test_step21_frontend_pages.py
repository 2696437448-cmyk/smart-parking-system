#!/usr/bin/env python3
"""Step21 gate: routed owner/admin frontend pages and page-level view models exist."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing required file: {path}")


def assert_contains(path: Path, tokens: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{path} missing token: {token}")


def main() -> None:
    for rel in [
        "src/router.ts",
        "src/layouts/OwnerLayout.vue",
        "src/layouts/AdminLayout.vue",
        "src/pages/OwnerDashboard.vue",
        "src/pages/OwnerOrders.vue",
        "src/pages/OwnerNavigation.vue",
        "src/pages/AdminMonitor.vue",
        "src/services/owner.ts",
        "src/services/admin.ts",
        "src/components/ViewStateNotice.vue",
        "src/composables/useViewState.ts",
        "src/composables/useOrderContext.ts",
        "src/composables/useOwnerDashboardView.ts",
        "src/composables/useOwnerOrderView.ts",
        "src/composables/useOwnerNavigationView.ts",
        "src/composables/useAdminDashboardView.ts",
    ]:
        assert_exists(FRONTEND / rel)

    pkg = json.loads((FRONTEND / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    for dependency in ["vue-router", "pinia"]:
        if dependency not in deps:
            raise AssertionError(f"package dependency missing: {dependency}")

    assert_contains(
        FRONTEND / "src" / "router.ts",
        ["/owner", '"dashboard"', '"orders"', '"navigation"', "/admin", '"monitor"'],
    )
    assert_contains(
        FRONTEND / "src" / "services" / "owner.ts",
        ["/api/v1/owner/dashboard", "/api/v1/owner/reservations", "/api/v1/owner/orders/", "/api/v1/owner/navigation/"],
    )
    assert_contains(FRONTEND / "src" / "services" / "admin.ts", ["/api/v1/admin/dashboard"])

    assert_contains(FRONTEND / "src" / "pages" / "OwnerDashboard.vue", ["useOwnerDashboardView", "ViewStateNotice"])
    assert_contains(FRONTEND / "src" / "pages" / "OwnerOrders.vue", ["useOwnerOrderView", "ViewStateNotice"])
    assert_contains(FRONTEND / "src" / "pages" / "OwnerNavigation.vue", ["useOwnerNavigationView", "ViewStateNotice"])
    assert_contains(FRONTEND / "src" / "pages" / "AdminMonitor.vue", ["useAdminDashboardView", "EChartPanel", "ViewStateNotice"])

    assert_contains(
        FRONTEND / "src" / "composables" / "useOwnerDashboardView.ts",
        ["fetchOwnerDashboard", "reserveOwnerSlot", "useOrderContext", "useViewState"],
    )
    assert_contains(
        FRONTEND / "src" / "composables" / "useOwnerOrderView.ts",
        ["fetchOrderDetail", "completeOrder", "useOrderContext", "useViewState"],
    )
    assert_contains(
        FRONTEND / "src" / "composables" / "useOwnerNavigationView.ts",
        ["fetchNavigation", "useOrderContext", "useViewState"],
    )
    assert_contains(
        FRONTEND / "src" / "composables" / "useAdminDashboardView.ts",
        ["fetchAdminDashboard", "useRealtimeChannel", "useViewState"],
    )
    assert_contains(
        FRONTEND / "src" / "composables" / "useViewState.ts",
        ['"loading"', '"ready"', '"empty"', '"error"', '"degraded"', '"stale"'],
    )

    print("STEP21_GATE_PASS")


if __name__ == "__main__":
    main()
