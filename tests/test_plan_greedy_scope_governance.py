from pathlib import Path

import yaml


def _load(path_str: str) -> dict:
    return yaml.safe_load(Path(path_str).read_text(encoding="utf-8"))


def test_official_plans_do_not_include_greedy():
    for path_str in [
        "configs/plan_phase_1.yaml",
        "configs/plan_phase_1_pilot.yaml",
    ]:
        plan = _load(path_str)
        solvers = plan.get("solvers") or {}
        assert "greedy" not in solvers, path_str


def test_exploratory_plans_preserve_greedy():
    for path_str in [
        "configs/plan_phase_1_greedy_exploratory.yaml",
        "configs/plan_phase_1_pilot_greedy_exploratory.yaml",
    ]:
        plan = _load(path_str)
        solvers = plan.get("solvers") or {}
        assert solvers.get("greedy", {}).get("enabled", False) is True, path_str
