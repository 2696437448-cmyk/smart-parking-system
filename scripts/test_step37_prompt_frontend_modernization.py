#!/usr/bin/env python3
"""Step37 gate: prompt-library memory upgrade and front/back dashboard modernization."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"
GATEWAY = "http://localhost:8080"


def request(path: str, method: str = "GET", body: dict | None = None, headers: dict | None = None):
    data = None
    merged_headers = {"X-Trace-Id": f"step37-{uuid.uuid4().hex[:8]}"}
    if headers:
        merged_headers.update(headers)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        merged_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(GATEWAY + path, data=data, headers=merged_headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def wait_gateway() -> None:
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(GATEWAY + "/actuator/health", timeout=4) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                if resp.status == 200 and payload.get("status") == "UP":
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError("gateway health timeout")


def assert_text(path: Path, tokens: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{path} missing token: {token}")


def seed_owner_order() -> str:
    base = datetime.now(timezone(timedelta(hours=8))).replace(second=0, microsecond=0) + timedelta(minutes=90)
    preferred = f"{base.isoformat()}/{(base + timedelta(minutes=45)).isoformat()}"
    suffix = uuid.uuid4().hex[:8]
    for slot_index in range(1, 13):
        slot_id = f"R1-S{slot_index:03d}"
        try:
            status, payload = request(
                "/api/v1/owner/reservations",
                method="POST",
                body={
                    "user_id": f"owner-step37-{suffix}",
                    "preferred_window": preferred,
                    "location": "R1",
                    "slot_id": slot_id,
                },
                headers={"Idempotency-Key": f"step37-{suffix}-{slot_index}"},
            )
        except Exception:
            continue
        if status == 200:
            return str(payload.get("order_id") or payload.get("reservation_id") or "")
    raise AssertionError("failed to seed a unique owner reservation for Step37")


def main() -> None:
    prompt_library = ROOT / "memory-bank" / "project-prompt-library.md"
    assert prompt_library.exists(), prompt_library
    assert_text(
        prompt_library,
        [
            "## 1. Product",
            "## 2. Data Science",
            "## 3. AI",
            "## 4. Algorithm",
            "## 5. Frontend / UI",
            "## 6. Backend",
            "### When to use",
            "### Read first",
            "### Project constraints",
            "### Expected output",
            "### Common anti-patterns",
            "### Repo-specific checklist",
        ],
    )
    assert_text(ROOT / "memory-bank" / "prompt-templates.md", ["project-prompt-library.md", "Task routing guide"])
    assert_text(ROOT / "memory-bank" / "implementation-plan.md", ["Step37 - 提示词驱动的现代化优化入口"])

    for rel in [
        "src/layouts/OwnerLayout.vue",
        "src/layouts/AdminLayout.vue",
        "src/services/owner.ts",
        "src/services/admin.ts",
        "src/services/http.ts",
        "src/styles/tokens.css",
        "src/styles/base.css",
        "src/styles/layout.css",
        "src/styles/components.css",
        "src/styles/pages.css",
    ]:
        if not (FRONTEND / rel).exists():
            raise AssertionError(f"missing Step37 frontend asset: {rel}")

    assert_text(FRONTEND / "src" / "router.ts", ['import("./layouts/OwnerLayout.vue")', 'import("./layouts/AdminLayout.vue")'])

    wait_gateway()
    order_id = seed_owner_order()
    owner_query = urllib.parse.urlencode(
        {
            "location": "R1",
            "preferred_window": f"{datetime.now(timezone(timedelta(hours=8))).replace(second=0, microsecond=0).isoformat()}/{(datetime.now(timezone(timedelta(hours=8))).replace(second=0, microsecond=0) + timedelta(minutes=30)).isoformat()}",
            "user_id": "owner-app-001",
            "order_id": order_id,
        }
    )
    status, owner_payload = request(f"/api/v1/owner/dashboard?{owner_query}")
    assert status == 200, owner_payload
    assert isinstance(owner_payload.get("summary"), dict), owner_payload
    assert isinstance(owner_payload.get("recommendations"), list) and owner_payload.get("recommendations"), owner_payload

    status, admin_payload = request(f"/api/v1/admin/dashboard?date={datetime.now(timezone.utc).date().isoformat()}")
    assert status == 200, admin_payload
    assert isinstance(admin_payload.get("summary"), dict), admin_payload
    assert isinstance(admin_payload.get("sections"), dict), admin_payload
    for key in ["revenue_summary", "revenue_trend", "occupancy_trend", "forecast_compare"]:
        if not isinstance(admin_payload["sections"].get(key), list):
            raise AssertionError(f"admin dashboard sections missing key: {key}")

    print("STEP37_GATE_PASS")


if __name__ == "__main__":
    main()
