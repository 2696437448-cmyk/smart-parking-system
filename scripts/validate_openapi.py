#!/usr/bin/env python3
"""Lightweight OpenAPI validator for Step24 contract."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

REQUIRED_PATHS = [
    "/api/v1/owner/reservations",
    "/api/v1/owner/recommendations",
    "/api/v1/owner/orders/{order_id}",
    "/api/v1/owner/orders/{order_id}/complete",
    "/api/v1/owner/navigation/{order_id}",
    "/api/v1/admin/dispatch/run",
    "/api/v1/admin/revenue/summary",
    "/api/v1/admin/monitor/summary",
    "/internal/v1/model/predict",
    "/internal/v1/dispatch/optimize",
    "/internal/v1/model/activate",
]
REQUIRED_SCHEMAS = [
    "DemandGapRecord",
    "DispatchRequest",
    "DispatchResult",
    "GeoPoint",
    "BillingRule",
    "BillingRecord",
    "RegionRevenueSummary",
    "NavigationTarget",
]
REQUIRED_PARAMETERS = ["XTraceId", "IdempotencyKey"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate OpenAPI contract")
    parser.add_argument("--spec", default="openapi/smart-parking.yaml", help="OpenAPI yaml path")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    doc = yaml.safe_load(spec_path.read_text(encoding="utf-8"))

    assert isinstance(doc, dict), "OpenAPI doc must be a mapping"
    assert str(doc.get("openapi", "")).startswith("3."), "openapi version must start with 3."

    paths = doc.get("paths", {})
    for endpoint in REQUIRED_PATHS:
        assert endpoint in paths, f"missing path: {endpoint}"

    components = doc.get("components", {})
    schemas = components.get("schemas", {})
    for schema_name in REQUIRED_SCHEMAS:
        assert schema_name in schemas, f"missing schema: {schema_name}"

    params = components.get("parameters", {})
    for p in REQUIRED_PARAMETERS:
        assert p in params, f"missing parameter component: {p}"

    print(f"openapi_validation_passed spec={spec_path}")


if __name__ == "__main__":
    main()
