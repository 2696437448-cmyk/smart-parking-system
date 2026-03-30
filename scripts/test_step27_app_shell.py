#!/usr/bin/env python3
"""Step27 gate: Capacitor app shell and mobile-first frontend assets."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"


def main() -> None:
    pkg = json.loads((FRONTEND / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    dev_deps = pkg.get("devDependencies", {})
    for token in ["@capacitor/core", "@capacitor/android", "leaflet", "echarts"]:
        if token not in deps:
            raise AssertionError(f"missing dependency: {token}")
    if "@capacitor/cli" not in dev_deps:
        raise AssertionError("missing dev dependency: @capacitor/cli")

    for rel in [
        "capacitor.config.ts",
        "android/app/build.gradle",
        "android/app/src/main/assets/capacitor.config.json",
        "src/pages/OwnerOrders.vue",
    ]:
        path = FRONTEND / rel
        if not path.exists():
            raise AssertionError(f"missing app shell file: {path}")

    router_text = (FRONTEND / "src" / "router.ts").read_text(encoding="utf-8")
    for token in ["/owner", '"dashboard"', '"orders"', '"navigation"', "/admin", '"monitor"']:
        if token not in router_text:
            raise AssertionError(f"router missing token: {token}")

    app_text = (FRONTEND / "src" / "App.vue").read_text(encoding="utf-8")
    for token in ["bottom-nav", "Capacitor", "Leaflet", "ECharts"]:
        if token not in app_text:
            raise AssertionError(f"App.vue missing token: {token}")

    print("STEP27_GATE_PASS")


if __name__ == "__main__":
    main()
