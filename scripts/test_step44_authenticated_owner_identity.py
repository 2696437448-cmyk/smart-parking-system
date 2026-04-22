#!/usr/bin/env python3
"""Step44 gate: owner identity comes from auth session instead of editable user input."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"
PARKING = ROOT / "services" / "parking-service" / "src" / "main" / "java" / "com" / "smartparking" / "parking"


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing required file: {path}")


def assert_contains(path: Path, tokens: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{path} missing token: {token}")


def assert_not_contains(path: Path, tokens: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token in text:
            raise AssertionError(f"{path} should not contain token: {token}")


def main() -> None:
    for rel in [
        FRONTEND / "src" / "pages" / "OwnerDashboard.vue",
        FRONTEND / "src" / "composables" / "useOwnerDashboardView.ts",
        FRONTEND / "src" / "services" / "owner.ts",
        PARKING / "ParkingDashboardViewController.java",
        PARKING / "ParkingServiceApplication.java",
    ]:
        assert_exists(rel)

    assert_contains(
        FRONTEND / "src" / "composables" / "useOwnerDashboardView.ts",
        ["useAuthStore", "currentUser", "authenticatedUserId"],
    )
    assert_contains(
        FRONTEND / "src" / "pages" / "OwnerDashboard.vue",
        ["登录账号", "authenticatedUserId"],
    )
    assert_not_contains(
        FRONTEND / "src" / "pages" / "OwnerDashboard.vue",
        ['v-model="userId"', "owner-step40-demo"],
    )
    assert_not_contains(
        FRONTEND / "src" / "services" / "owner.ts",
        ['user_id: params.userId', 'user_id: payload.userId'],
    )
    assert_contains(
        PARKING / "ParkingDashboardViewController.java",
        ["X-Auth-User-Id", "effectiveUserId"],
    )
    assert_contains(
        PARKING / "ParkingServiceApplication.java",
        ["X-Auth-User-Id", "authenticatedUserId"],
    )

    print("STEP44_GATE_PASS")


if __name__ == "__main__":
    main()
