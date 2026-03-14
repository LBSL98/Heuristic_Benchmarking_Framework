"""Executor declarativo mínimo para campanhas descritas em YAML."""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from .runner import run_one

SUPPORTED_SOLVERS = ("metis", "kahip")


def _load_plan(plan_path: Path) -> dict:
    with Path(plan_path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _enabled_supported_solvers(plan: dict) -> list[str]:
    solvers = plan.get("solvers", {}) or {}

    greedy_cfg = solvers.get("greedy", {}) or {}
    if bool(greedy_cfg.get("enabled", False)):
        raise NotImplementedError("greedy is enabled in the plan, but no adapter exists yet")

    enabled: list[str] = []
    for name in SUPPORTED_SOLVERS:
        cfg = solvers.get(name, {}) or {}
        if bool(cfg.get("enabled", False)):
            enabled.append(name)

    return enabled


def _included_instances(plan: dict) -> list[str]:
    instances = plan.get("instances", {}) or {}
    include = instances.get("include", []) or []
    return [str(x) for x in include]


def _rng_seeds(plan: dict) -> list[int]:
    rng = plan.get("rng", {}) or {}
    seeds = rng.get("seeds", []) or []
    return [int(x) for x in seeds]


def _solver_k(plan: dict, solver: str) -> int:
    cfg = (plan.get("solvers", {}) or {}).get(solver, {}) or {}
    return int(cfg.get("k", 2))


def _solver_beta(plan: dict, solver: str) -> float:
    cfg = (plan.get("solvers", {}) or {}).get(solver, {}) or {}
    if solver == "kahip":
        return float(cfg.get("imbalance", 0.03))
    return 0.03


def _solver_budget_time_ms(plan: dict, solver: str) -> int:
    cfg = (plan.get("solvers", {}) or {}).get(solver, {}) or {}
    budget = cfg.get("budget", {}) or {}
    seconds = budget.get("seconds", 1)
    return int(float(seconds) * 1000)


def _planned_runs(plan: dict) -> list[dict]:
    runs: list[dict] = []
    for instance in _included_instances(plan):
        for solver in _enabled_supported_solvers(plan):
            for seed in _rng_seeds(plan):
                runs.append(
                    {
                        "instance": instance,
                        "solver": solver,
                        "seed": seed,
                        "k": _solver_k(plan, solver),
                        "beta": _solver_beta(plan, solver),
                        "budget_time_ms": _solver_budget_time_ms(plan, solver),
                    }
                )
    return runs


def run_plan(plan_path: Path) -> None:
    """Executa uma campanha mínima a partir de um plano YAML."""
    plan = _load_plan(plan_path)
    runs = _planned_runs(plan)

    if not runs:
        raise ValueError("Plan produced no runnable entries.")

    instances_cfg = plan.get("instances", {}) or {}
    output_cfg = plan.get("output", {}) or {}

    base_dir = Path(instances_cfg.get("base_dir", "."))
    raw_dir = Path(output_cfg.get("raw_dir", "data/results_raw"))
    raw_dir.mkdir(parents=True, exist_ok=True)

    for run in runs:
        instance_path = base_dir / run["instance"]

        stem = Path(run["instance"]).name
        out_json = raw_dir / f"{stem}__{run['solver']}__seed{run['seed']}.json"
        workdir = raw_dir / f"run_{run['solver']}__{stem}__seed{run['seed']}"

        run_one(
            instance_path=instance_path,
            algo=run["solver"],
            k=run["k"],
            beta=run["beta"],
            seed=run["seed"],
            budget_time_ms=run["budget_time_ms"],
            out_json=out_json,
            workdir=workdir,
            kahip_preset="fast",
            log_level="info",
        )
