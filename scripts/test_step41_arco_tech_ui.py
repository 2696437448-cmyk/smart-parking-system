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

    assert_contains(FRONTEND / "src" / "main.ts", ["ArcoVue", "MotionPlugin", "createArcoTheme"])
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
    print("STEP41_ARCO_BOOTSTRAP_PASS")


if __name__ == "__main__":
    main()
