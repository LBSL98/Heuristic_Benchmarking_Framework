from __future__ import annotations

from pathlib import Path

import yaml


def _load_yaml(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _enabled_solvers(plan: dict) -> set[str]:
    solvers = plan.get("solvers", {}) or {}
    return {
        name for name, cfg in solvers.items() if isinstance(cfg, dict) and cfg.get("enabled", False)
    }


def test_phase1_baselines_plan_contains_only_canonical_baselines():
    plan = _load_yaml("configs/plan_phase_1_baselines.yaml")
    assert _enabled_solvers(plan) == {"metis", "kahip"}
    assert (plan.get("rng", {}) or {}).get("seeds") == [42]


def test_phase1_metaheuristics_plan_contains_only_canonical_metaheuristics():
    plan = _load_yaml("configs/plan_phase_1_metaheuristics.yaml")
    assert _enabled_solvers(plan) == {"sa", "ils", "grasp", "ts"}
    assert (plan.get("rng", {}) or {}).get("seeds") == [42, 43, 44, 45, 46]


def test_phase1_pilot_baselines_plan_contains_only_canonical_baselines():
    plan = _load_yaml("configs/plan_phase_1_pilot_baselines.yaml")
    assert _enabled_solvers(plan) == {"metis", "kahip"}
    assert (plan.get("rng", {}) or {}).get("seeds") == [42]


def test_phase1_pilot_metaheuristics_plan_contains_only_canonical_metaheuristics():
    plan = _load_yaml("configs/plan_phase_1_pilot_metaheuristics.yaml")
    assert _enabled_solvers(plan) == {"sa", "ils", "grasp", "ts"}
    assert (plan.get("rng", {}) or {}).get("seeds") == [42, 43, 44]


def test_greedy_remains_outside_official_canonical_benchmark_plans():
    official_plans = [
        "configs/plan_phase_1_baselines.yaml",
        "configs/plan_phase_1_metaheuristics.yaml",
        "configs/plan_phase_1_pilot_baselines.yaml",
        "configs/plan_phase_1_pilot_metaheuristics.yaml",
    ]
    for path in official_plans:
        plan = _load_yaml(path)
        assert "greedy" not in _enabled_solvers(plan)
