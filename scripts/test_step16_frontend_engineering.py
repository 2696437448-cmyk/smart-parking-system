#!/usr/bin/env python3
"""Step16 gate: frontend projectization checks (Vue3 + TS + Pinia)."""

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
    required = [
      FRONTEND / "package.json",
      FRONTEND / "vite.config.ts",
      FRONTEND / "tsconfig.json",
      FRONTEND / "index.html",
      FRONTEND / "src" / "main.ts",
      FRONTEND / "src" / "App.vue",
      FRONTEND / "src" / "stores" / "realtime.ts",
      FRONTEND / "src" / "composables" / "useRealtimeChannel.ts",
      FRONTEND / "src" / "types" / "realtime.ts",
      FRONTEND / "realtime_dashboard_demo.html",
    ]
    for file in required:
        assert_exists(file)

    pkg = json.loads((FRONTEND / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    dev_deps = pkg.get("devDependencies", {})

    for dep in ("vue", "pinia"):
        if dep not in deps:
            raise AssertionError(f"package dependency missing: {dep}")

    for dep in ("typescript", "vite", "@vitejs/plugin-vue"):
        if dep not in dev_deps:
            raise AssertionError(f"package devDependency missing: {dep}")

    assert_contains(FRONTEND / "src" / "stores" / "realtime.ts", ["defineStore", "mode", "source", "degraded", "realtime"])
    assert_contains(FRONTEND / "src" / "composables" / "useRealtimeChannel.ts", ["new WebSocket", "startPolling", "setInterval", "markDegraded"])
    assert_contains(FRONTEND / "src" / "App.vue", ["Pinia", "WebSocket", "Polling", "手动重连"])

    print("STEP16_GATE_PASS")


if __name__ == "__main__":
    main()
