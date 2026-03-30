from pathlib import Path

import yaml


def _load_yaml(path_str: str) -> dict:
    return yaml.safe_load(Path(path_str).read_text(encoding="utf-8"))


def test_phase1_plan_excludes_greedy_from_official_flow():
    plan = _load_yaml("configs/plan_phase_1.yaml")
    solvers = plan.get("solvers", {}) or {}

    assert "greedy" not in solvers
    assert solvers.get("metis", {}).get("enabled", False) is True
    assert solvers.get("kahip", {}).get("enabled", False) is True


def test_phase1_pilot_plan_excludes_greedy_from_official_flow():
    plan = _load_yaml("configs/plan_phase_1_pilot.yaml")
    solvers = plan.get("solvers", {}) or {}

    assert "greedy" not in solvers
    assert solvers.get("metis", {}).get("enabled", False) is True
    assert solvers.get("kahip", {}).get("enabled", False) is True


def test_phase1_exploratory_plan_preserves_greedy():
    plan = _load_yaml("configs/plan_phase_1_greedy_exploratory.yaml")
    solvers = plan.get("solvers", {}) or {}
    greedy = solvers.get("greedy", {}) or {}

    assert greedy.get("enabled", False) is True
    assert solvers.get("metis", {}).get("enabled", False) is True
    assert solvers.get("kahip", {}).get("enabled", False) is True


def test_phase1_pilot_exploratory_plan_preserves_greedy():
    plan = _load_yaml("configs/plan_phase_1_pilot_greedy_exploratory.yaml")
    solvers = plan.get("solvers", {}) or {}
    greedy = solvers.get("greedy", {}) or {}

    assert greedy.get("enabled", False) is True
    assert solvers.get("metis", {}).get("enabled", False) is True
    assert solvers.get("kahip", {}).get("enabled", False) is True
