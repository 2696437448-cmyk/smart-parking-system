#!/usr/bin/env python3
"""Step21 gate: routed owner/admin frontend pages exist."""

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
        "src/pages/OwnerDashboard.vue",
        "src/pages/OwnerNavigation.vue",
        "src/pages/AdminMonitor.vue",
    ]:
        assert_exists(FRONTEND / rel)

    pkg = json.loads((FRONTEND / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    if "vue-router" not in deps:
        raise AssertionError("package dependency missing: vue-router")

    assert_contains(FRONTEND / "src" / "router.ts", ["/owner/dashboard", "/owner/navigation", "/admin/monitor"])
    assert_contains(FRONTEND / "src" / "pages" / "OwnerDashboard.vue", ["/api/v1/owner/recommendations", "/api/v1/owner/reservations", "/api/v1/owner/orders/"])
    assert_contains(FRONTEND / "src" / "pages" / "OwnerNavigation.vue", ["/api/v1/owner/navigation/"])
    assert_contains(FRONTEND / "src" / "pages" / "AdminMonitor.vue", ["/api/v1/admin/monitor/summary", "/api/v1/admin/revenue/summary"])

    print("STEP21_GATE_PASS")


if __name__ == "__main__":
    main()
