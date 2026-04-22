#!/usr/bin/env python3
"""Step43 gate: login page, auth store and bearer token wiring exist."""

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
        "src/services/http.ts",
        "src/services/auth.ts",
        "src/stores/auth.ts",
        "src/pages/LoginPage.vue",
        "src/layouts/OwnerLayout.vue",
        "src/layouts/AdminLayout.vue",
    ]:
        assert_exists(FRONTEND / rel)

    pkg = json.loads((FRONTEND / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    for dependency in ["vue-router", "pinia"]:
        if dependency not in deps:
            raise AssertionError(f"package dependency missing: {dependency}")

    assert_contains(
        FRONTEND / "src" / "router.ts",
        ["/login", "requiresAuth", "guestOnly", "beforeEach", "restoreSession"],
    )
    assert_contains(
        FRONTEND / "src" / "services" / "http.ts",
        ["Authorization", "Bearer", "AUTH_TOKEN_STORAGE_KEY"],
    )
    assert_contains(
        FRONTEND / "src" / "services" / "auth.ts",
        ["/api/v1/auth/login", "/api/v1/auth/me", "/api/v1/auth/logout"],
    )
    assert_contains(
        FRONTEND / "src" / "stores" / "auth.ts",
        ["defineStore", "login", "logout", "restoreSession", "currentUser", "isAuthenticated"],
    )
    assert_contains(
        FRONTEND / "src" / "pages" / "LoginPage.vue",
        ["smart-login", "用户名", "密码", "立即登录", "owner_demo", "admin_demo"],
    )
    assert_contains(FRONTEND / "src" / "layouts" / "OwnerLayout.vue", ["currentUser", "logout"])
    assert_contains(FRONTEND / "src" / "layouts" / "AdminLayout.vue", ["currentUser", "logout"])

    print("STEP43_GATE_PASS")


if __name__ == "__main__":
    main()
