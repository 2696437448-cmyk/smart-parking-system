#!/usr/bin/env python3
"""Step19B gate: deterministic Hungarian optimizer verification."""

from __future__ import annotations

import importlib.util
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "services" / "model_service.py"


def load_module():
    spec = importlib.util.spec_from_file_location("smart_model_service", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def brute_force_total(module, requests, slots):
    best = float("inf")
    for chosen in itertools.combinations(slots, len(requests)):
        for perm in itertools.permutations(chosen):
            total = 0.0
            for req, slot in zip(requests, perm):
                total += module._cost(req, slot)[0]
            best = min(best, total)
    return round(best, 6)


def assigned_total(module, requests, results):
    total = 0.0
    for req, item in zip(requests, results):
        total += module._cost(req, item["slot_id"])[0]
    return round(total, 6)


def main() -> None:
    module = load_module()

    requests = [
        {"order_id": "O-001", "user_id": "U-001", "preferred_window": "2026-03-12T09:00:00+08:00/2026-03-12T10:00:00+08:00", "location": "R1", "constraints": {}},
        {"order_id": "O-002", "user_id": "U-002", "preferred_window": "2026-03-12T09:00:00+08:00/2026-03-12T10:00:00+08:00", "location": "R2", "constraints": {}},
        {"order_id": "O-003", "user_id": "U-003", "preferred_window": "2026-03-12T09:00:00+08:00/2026-03-12T10:00:00+08:00", "location": "R3", "constraints": {}},
        {"order_id": "O-004", "user_id": "U-004", "preferred_window": "2026-03-12T09:00:00+08:00/2026-03-12T10:00:00+08:00", "location": "R1", "constraints": {}},
    ]

    results_a, strategy_a = module._optimize(requests)
    results_b, strategy_b = module._optimize(requests)

    if strategy_a != "hungarian_optimal" or strategy_b != "hungarian_optimal":
        raise AssertionError(f"unexpected strategy: {strategy_a}, {strategy_b}")
    if results_a != results_b:
        raise AssertionError("optimizer output is not deterministic")

    slots = module._slot_pool(requests)
    optimal_total = brute_force_total(module, requests, slots)
    hungarian_total = assigned_total(module, requests, results_a)
    if hungarian_total != optimal_total:
        raise AssertionError(f"hungarian total mismatch: got={hungarian_total} expected={optimal_total}")

    large_requests = [
        {"order_id": f"L-{idx:03d}", "user_id": f"U-{idx:03d}", "preferred_window": "2026-03-12T09:00:00+08:00/2026-03-12T10:00:00+08:00", "location": f"R{(idx % 3) + 1}", "constraints": {}}
        for idx in range(9)
    ]
    large_results, large_strategy = module._optimize(large_requests)
    if large_strategy != "hungarian_optimal":
        raise AssertionError(f"large strategy downgraded: {large_strategy}")
    if len({item["slot_id"] for item in large_results}) != len(large_results):
        raise AssertionError("large optimize assigned duplicate slots")

    print("STEP19B_GATE_PASS")


if __name__ == "__main__":
    main()
