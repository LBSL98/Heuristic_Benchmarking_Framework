from pathlib import Path

import yaml


def _load_yaml(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def test_phase1_plan_enables_greedy():
    plan = _load_yaml("configs/plan_phase_1.yaml")
    solvers = plan.get("solvers", {}) or {}
    greedy = solvers.get("greedy", {}) or {}

    assert greedy.get("enabled", False) is True


def test_phase1_pilot_plan_enables_greedy():
    plan = _load_yaml("configs/plan_phase_1_pilot.yaml")
    solvers = plan.get("solvers", {}) or {}
    greedy = solvers.get("greedy", {}) or {}

    assert greedy.get("enabled", False) is True
