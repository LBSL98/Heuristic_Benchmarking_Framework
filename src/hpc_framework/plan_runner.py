"""Executor declarativo mínimo para campanhas descritas em YAML."""

from __future__ import annotations

import gzip
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from .greedy_adapter import run_greedy_observation
from .runner import _env_snapshot, _tool_version, _which, run_one

SUPPORTED_SOLVERS = ("metis", "kahip")


def _load_plan(plan_path: Path) -> dict:
    with Path(plan_path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _greedy_enabled(plan: dict) -> bool:
    solvers = plan.get("solvers", {}) or {}
    greedy_cfg = solvers.get("greedy", {}) or {}
    return bool(greedy_cfg.get("enabled", False))


def _enabled_supported_solvers(plan: dict) -> list[str]:
    solvers = plan.get("solvers", {}) or {}

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


def _greedy_budget_time_ms(plan: dict) -> int:
    cfg = (plan.get("solvers", {}) or {}).get("greedy", {}) or {}
    budget = cfg.get("budget", {}) or {}
    seconds = budget.get("seconds", 1)
    return int(float(seconds) * 1000)


def _planned_runs(plan: dict) -> list[dict]:
    runs: list[dict] = []

    if _greedy_enabled(plan):
        greedy_cfg = (plan.get("solvers", {}) or {}).get("greedy", {}) or {}
        greedy_params = greedy_cfg.get("params", {}) or {}
        delta_v = float(greedy_params.get("delta_v", 0.1))

        for instance in _included_instances(plan):
            for seed in _rng_seeds(plan):
                runs.append(
                    {
                        "instance": instance,
                        "solver": "greedy",
                        "seed": seed,
                        "delta_v": delta_v,
                        "budget_time_ms": _greedy_budget_time_ms(plan),
                    }
                )

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


def _read_instance_json(path: Path) -> dict[str, Any]:
    if str(path).endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(path.read_text(encoding="utf-8"))


def _greedy_tools_snapshot() -> dict:
    return {
        "gpmetis": {
            "exists": bool(_which("gpmetis")),
            "version": _tool_version(["gpmetis"]) if _which("gpmetis") else "",
        },
        "kaffpa": {
            "exists": bool(_which("kaffpa")),
            "version": _tool_version(["kaffpa"]) if _which("kaffpa") else "",
        },
    }


def _write_greedy_result(
    *,
    raw_dir: Path,
    instance_name: str,
    instance_id: str,
    seed: int,
    delta_v: float,
    budget_time_ms: int,
    obs: dict,
) -> None:
    out_json = raw_dir / f"{Path(instance_name).name}__greedy__seed{seed}.json"

    labels = obs["labels"]
    labels_json = labels.tolist() if hasattr(labels, "tolist") else list(labels)

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "instance_id": instance_id,
        "algo": "greedy",
        "k": int(obs["observed_k"]),
        "beta": float(delta_v),
        "seed": int(seed),
        "budget_time_ms": int(budget_time_ms),
        "status": "ok",
        "returncode": 0,
        "elapsed_ms": 0,
        "stdout": "",
        "stderr": "",
        "metrics": {
            "cutsize_best": int(obs["cutsize_best"]),
            "n_nodes": len(labels_json),
            "balance_tolerance": float(delta_v),
            "imbalance_raw": None,
        },
        "env": _env_snapshot(),
        "tools": _greedy_tools_snapshot(),
        "paths": {
            "workdir": "",
            "graph_path": "",
            "part_path": None,
        },
        "checkpoints": [
            {
                "time_ms": 0,
                "cutsize_best": int(obs["cutsize_best"]),
                "nfe": None,
            }
        ],
        "schema_version": "1.0.0",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
        # compat legado
        "cutsize_best": int(obs["cutsize_best"]),
        "observed_k": int(obs["observed_k"]),
        "labels": labels_json,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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

        if run["solver"] == "greedy":
            inst = _read_instance_json(instance_path)
            obs = run_greedy_observation(inst, delta_v=float(run["delta_v"]))
            _write_greedy_result(
                raw_dir=raw_dir,
                instance_name=run["instance"],
                instance_id=str(inst.get("instance_id", Path(run["instance"]).stem)),
                seed=int(run["seed"]),
                delta_v=float(run["delta_v"]),
                budget_time_ms=int(run["budget_time_ms"]),
                obs=obs,
            )
            continue

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
