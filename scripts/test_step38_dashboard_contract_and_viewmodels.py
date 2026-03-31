#!/usr/bin/env python3
"""Step38 gate: dashboard OpenAPI contract and frontend page-level view models."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "apps" / "frontend"
REPORT_PATH = ROOT / "reports" / "step38_gate_results.json"


def run(cmd: str, cwd: Path | None = None, timeout: int = 900) -> tuple[bool, str, float]:
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, output, time.time() - started


def assert_tokens(path: Path, tokens: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise AssertionError(f"{path} missing token: {token}")


def main() -> None:
    steps: list[dict[str, object]] = []

    ok, output, elapsed = run("python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml")
    steps.append(
        {
            "name": "openapi_validation",
            "command": "python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml",
            "passed": ok,
            "elapsed_seconds": round(elapsed, 3),
            "output_tail": "\n".join(output.splitlines()[-10:]),
        }
    )
    if not ok:
        REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"STEP38_GATE_FAIL failed=openapi_validation report={REPORT_PATH}")
        raise SystemExit(1)

    spec = yaml.safe_load((ROOT / "openapi" / "smart-parking.yaml").read_text(encoding="utf-8"))
    owner_get = spec["paths"]["/api/v1/owner/dashboard"]["get"]
    admin_get = spec["paths"]["/api/v1/admin/dashboard"]["get"]

    owner_params = {item["name"] for item in owner_get["parameters"] if "$ref" not in item}
    admin_params = {item["name"] for item in admin_get["parameters"] if "$ref" not in item}
    owner_schema = owner_get["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    admin_schema = admin_get["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    owner_props = spec["components"]["schemas"]["OwnerDashboardResponse"]["properties"]
    admin_props = spec["components"]["schemas"]["AdminDashboardResponse"]["properties"]

    contract_checks = {
        "owner_dashboard_query_params": owner_params == {"location", "preferred_window", "user_id", "order_id"},
        "admin_dashboard_query_params": admin_params == {"date", "region_id", "trend_days", "trend_limit"},
        "owner_dashboard_schema_ref": owner_schema.endswith("/OwnerDashboardResponse"),
        "admin_dashboard_schema_ref": admin_schema.endswith("/AdminDashboardResponse"),
        "owner_dashboard_required_props": {"summary", "journey", "billing_rule", "recommendations", "trace_id", "service"}.issubset(owner_props.keys()),
        "admin_dashboard_required_props": {"summary", "highlights", "sections", "diagnostic_links", "degraded_metadata", "trace_id", "service"}.issubset(admin_props.keys()),
    }
    for name, passed in contract_checks.items():
        steps.append({"name": name, "passed": passed, "elapsed_seconds": 0.0})
        if not passed:
            REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"STEP38_GATE_FAIL failed={name} report={REPORT_PATH}")
            raise SystemExit(1)

    required_files = [
        FRONTEND / "src" / "components" / "ViewStateNotice.vue",
        FRONTEND / "src" / "composables" / "useViewState.ts",
        FRONTEND / "src" / "composables" / "useOrderContext.ts",
        FRONTEND / "src" / "composables" / "useOwnerDashboardView.ts",
        FRONTEND / "src" / "composables" / "useOwnerOrderView.ts",
        FRONTEND / "src" / "composables" / "useOwnerNavigationView.ts",
        FRONTEND / "src" / "composables" / "useAdminDashboardView.ts",
        FRONTEND / "src" / "pages" / "OwnerDashboard.vue",
        FRONTEND / "src" / "pages" / "OwnerOrders.vue",
        FRONTEND / "src" / "pages" / "OwnerNavigation.vue",
        FRONTEND / "src" / "pages" / "AdminMonitor.vue",
        FRONTEND / "src" / "types" / "dashboard.ts",
    ]
    for path in required_files:
        passed = path.exists()
        steps.append({"name": f"exists:{path.relative_to(ROOT)}", "passed": passed, "elapsed_seconds": 0.0})
        if not passed:
            REPORT_PATH.write_text(json.dumps({"overall_passed": False, "steps": steps}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"STEP38_GATE_FAIL failed=exists:{path.relative_to(ROOT)} report={REPORT_PATH}")
            raise SystemExit(1)

    assert_tokens(FRONTEND / "src" / "components" / "ViewStateNotice.vue", ["loading", "empty", "error", "degraded", "stale"])
    assert_tokens(FRONTEND / "src" / "composables" / "useViewState.ts", ["markLoading", "markReady", "markEmpty", "markError", "markDegraded", '"stale"'])
    assert_tokens(FRONTEND / "src" / "composables" / "useOrderContext.ts", ["rememberOrderId", "navigateWithOrder", "ensureRouteOrderId"])
    assert_tokens(FRONTEND / "src" / "composables" / "useOwnerDashboardView.ts", ["fetchOwnerDashboard", "reserveOwnerSlot", "useOrderContext", "useViewState"])
    assert_tokens(FRONTEND / "src" / "composables" / "useOwnerOrderView.ts", ["fetchOrderDetail", "completeOrder", "useOrderContext", "useViewState"])
    assert_tokens(FRONTEND / "src" / "composables" / "useOwnerNavigationView.ts", ["fetchNavigation", "useOrderContext", "useViewState"])
    assert_tokens(FRONTEND / "src" / "composables" / "useAdminDashboardView.ts", ["fetchAdminDashboard", "useRealtimeChannel", "useViewState", "state.markDegraded"])
    assert_tokens(FRONTEND / "src" / "pages" / "OwnerDashboard.vue", ["useOwnerDashboardView", "ViewStateNotice"])
    assert_tokens(FRONTEND / "src" / "pages" / "OwnerOrders.vue", ["useOwnerOrderView", "ViewStateNotice"])
    assert_tokens(FRONTEND / "src" / "pages" / "OwnerNavigation.vue", ["useOwnerNavigationView", "ViewStateNotice"])
    assert_tokens(FRONTEND / "src" / "pages" / "AdminMonitor.vue", ["useAdminDashboardView", "ViewStateNotice", "EChartPanel"])
    assert_tokens(
        FRONTEND / "src" / "types" / "dashboard.ts",
        ["trace_id", "service", "billing_rule", "latest_order", "highlights", "diagnostic_links", "degraded_metadata"],
    )
    steps.append({"name": "frontend_view_models_and_states", "passed": True, "elapsed_seconds": 0.0})

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": all(bool(step["passed"]) for step in steps),
        "steps": steps,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"STEP38_GATE_PASS report={REPORT_PATH}")


if __name__ == "__main__":
    main()
