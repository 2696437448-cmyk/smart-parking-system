#!/usr/bin/env python3
"""Step41 gate: Arco-based tech UI bootstrap exists."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"


def assert_contains(path: Path, tokens: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{path} missing token: {token}")


def main() -> None:
    pkg = json.loads((FRONTEND / "package.json").read_text(encoding="utf-8"))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    for dependency in ["@arco-design/web-vue", "@vueuse/motion"]:
        if dependency not in deps:
            raise AssertionError(f"missing dependency: {dependency}")

    assert_contains(FRONTEND / "src" / "main.ts", ["MotionPlugin", "createArcoTheme", "arcoComponents", "app.use(component, arcoTheme)"])
    assert_contains(FRONTEND / "src" / "theme" / "arco.ts", ["componentConfig", "dark", "primaryColor"])
    assert_contains(FRONTEND / "src" / "theme" / "motion.ts", ["MotionPlugin"])
    assert_contains(
        FRONTEND / "src" / "styles" / "tokens.css",
        ["--color-bg-main", "--color-bg-elevated", "--color-accent-cyan", "--color-panel-glow", "--font-display"],
    )
    assert_contains(
        FRONTEND / "src" / "styles" / "base.css",
        ["radial-gradient", ".tech-theme-root", ".app-grid-glow", "backdrop-filter"],
    )
    assert_contains(FRONTEND / "src" / "layouts" / "OwnerLayout.vue", ["a-tag", "owner-command-bar", "Journey Status"])
    assert_contains(FRONTEND / "src" / "layouts" / "AdminLayout.vue", ["a-tag", "admin-control-rail", "Operations Grid"])
    assert_contains(FRONTEND / "src" / "styles" / "layout.css", [".owner-command-bar", ".admin-control-rail", ".shell-status-strip"])
    assert_contains(FRONTEND / "src" / "components" / "MetricCard.vue", ["a-statistic", "metric-card-shell"])
    assert_contains(FRONTEND / "src" / "components" / "SectionHeader.vue", ["a-tag", "section-header-side"])
    assert_contains(FRONTEND / "src" / "components" / "ViewStateNotice.vue", ["a-alert", "state-notice", "toneLabel"])
    assert_contains(FRONTEND / "src" / "styles" / "components.css", [".metric-card-shell", ".section-header-side", ".state-notice"])
    assert_contains(FRONTEND / "src" / "pages" / "OwnerDashboard.vue", ["a-form", "a-button", "owner-smart-grid"])
    assert_contains(FRONTEND / "src" / "pages" / "OwnerOrders.vue", ["order-task-flow", "a-button", "ViewStateNotice"])
    assert_contains(FRONTEND / "src" / "pages" / "OwnerNavigation.vue", ["navigation-task-panel", "a-tag", "MapPreview"])
    assert_contains(FRONTEND / "src" / "styles" / "pages.css", [".owner-smart-grid", ".order-task-flow", ".navigation-task-panel"])
    assert_contains(FRONTEND / "src" / "pages" / "AdminMonitor.vue", ["operations-cockpit", "a-button", "a-tag", "EChartPanel"])
    assert_contains(FRONTEND / "src" / "styles" / "pages.css", [".operations-cockpit", ".kpi-signal-grid", ".chart-cluster"])
    assert_contains(FRONTEND / "src" / "components" / "EChartPanel.vue", ["chart-panel-shell", "a-tag", "v-motion"])
    assert_contains(FRONTEND / "src" / "components" / "MapPreview.vue", ["map-preview-shell", "目标车位", "leaflet-container"])
    print("STEP41_ARCO_BOOTSTRAP_PASS")


if __name__ == "__main__":
    main()
