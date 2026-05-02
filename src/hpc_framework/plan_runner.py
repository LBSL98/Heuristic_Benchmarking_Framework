# mypy: disable-error-code=import-untyped
"""Executor declarativo mínimo para campanhas descritas em YAML."""

from __future__ import annotations

import csv
import gzip
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from heuristics.grasp import GRASPConfig, GRASPResult, run_grasp_partition
from heuristics.ils import ILSConfig, ILSResult, run_ils_partition
from heuristics.sa import SAConfig, SAResult, run_sa_partition
from heuristics.ts import TSConfig, TSResult, run_ts_partition

from .greedy_adapter import run_greedy_observation
from .runner import (
    _env_snapshot,
    _tool_version,
    _which,
    extract_graph_from_instance,
    feasible_beta,
    normalize_labels_zero_based,
    run_one,
)
from .solvers.common import write_metis_graph

SUPPORTED_SOLVERS = ("metis", "kahip", "sa", "sa_rust", "ils", "ils_rust", "grasp", "ts", "ts_rust")
MANIFEST_FIELDS = [
    "timestamp",
    "instance_id",
    "algo",
    "k",
    "beta",
    "seed",
    "budget_time_ms",
    "status",
    "returncode",
    "elapsed_ms",
    "metrics.cutsize_best",
    "metrics.imbalance_raw",
    "paths.workdir",
    "paths.graph_path",
    "paths.part_path",
    "env.python",
    "env.os",
    "env.os_release",
    "env.cpu.model",
    "env.cpu.cores_logical",
    "env.cpu.cores_physical",
    "env.cpu.freq_mhz",
    "tools.gpmetis.exists",
    "tools.gpmetis.version",
    "tools.kaffpa.exists",
    "tools.kaffpa.version",
]


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
    if "imbalance" in cfg:
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


def _get(d: dict[str, Any], dotted: str) -> Any:
    cur: Any = d
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _write_manifest_index(*, output_files: list[Path], manifest_out: Path) -> None:
    rows: list[dict[str, Any]] = []

    for path in sorted(output_files, key=lambda p: str(p)):
        obj = json.loads(path.read_text(encoding="utf-8"))
        row = {field: _get(obj, field) for field in MANIFEST_FIELDS}
        row["_file"] = str(path)
        rows.append(row)

    manifest_out.parent.mkdir(parents=True, exist_ok=True)
    with manifest_out.open("w", encoding="utf-8", newline="") as fo:
        writer = csv.DictWriter(fo, fieldnames=["_file"] + MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_greedy_result(
    *,
    raw_dir: Path,
    instance_name: str,
    instance_id: str,
    seed: int,
    delta_v: float,
    budget_time_ms: int,
    obs: dict,
    elapsed_ms: int,
) -> Path:
    delta_tag = f"{float(delta_v):.2f}"
    out_json = raw_dir / f"{Path(instance_name).name}__greedy__dv{delta_tag}__seed{seed}.json"

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
        "elapsed_ms": int(elapsed_ms),
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
                "time_ms": int(elapsed_ms),
                "cutsize_best": int(obs["cutsize_best"]),
                "nfe": None,
            }
        ],
        "schema_version": "1.0.0",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
        "cutsize_best": int(obs["cutsize_best"]),
        "observed_k": int(obs["observed_k"]),
        "labels": labels_json,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_json


def _adj_from_edges(n: int, edges: Any) -> dict[int, set[int]]:
    """Build an undirected adjacency map from an edge list."""
    adj: dict[int, set[int]] = {i: set() for i in range(int(n))}
    for u, v in edges:
        ui = int(u)
        vi = int(v)
        if ui == vi:
            continue
        adj[ui].add(vi)
        adj[vi].add(ui)
    return adj


def _labels_from_part_of(part_of: dict[int, int], n: int) -> list[int]:
    """Convert a part-of mapping into a dense 0..n-1 labels list."""
    return [int(part_of[i]) for i in range(int(n))]


def _write_sa_result(
    *,
    raw_dir: Path,
    instance_name: str,
    instance_id: str,
    n: int,
    edges: Any,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    result: SAResult,
) -> Path:
    """Persist a canonical SA run in the same JSON contract used by the runner."""
    beta_tag = f"{float(beta):.2f}"
    out_json = raw_dir / f"{Path(instance_name).name}__sa__k{k}__b{beta_tag}__seed{seed}.json"
    workdir = raw_dir / f"run_sa__{Path(instance_name).name}__k{k}__b{beta_tag}__seed{seed}"
    workdir.mkdir(parents=True, exist_ok=True)

    graph_path = workdir / "graph.graph"
    write_metis_graph(graph_path, int(n), edges)

    labels = _labels_from_part_of(result.best_part_of, int(n))
    labels_np = np.asarray(labels, dtype=int)

    part_path = workdir / "sa.part"
    part_path.write_text("".join(f"{int(label)}\n" for label in labels), encoding="utf-8")

    feasible, validation = feasible_beta(
        normalize_labels_zero_based(labels_np), k=int(k), beta=float(beta)
    )

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "instance_id": instance_id,
        "algo": "sa",
        "k": int(k),
        "beta": float(beta),
        "seed": int(seed),
        "budget_time_ms": int(budget_time_ms),
        "status": result.status,
        "returncode": 0,
        "elapsed_ms": int(result.elapsed_ms),
        "stdout": "",
        "stderr": "",
        "metrics": {
            "cutsize_best": int(result.best_cutsize),
            "n_nodes": int(n),
            "balance_tolerance": float(beta),
            "imbalance_raw": None,
        },
        "paths": {
            "workdir": str(workdir),
            "graph_path": str(graph_path),
            "part_path": str(part_path),
        },
        "env": _env_snapshot(),
        "tools": _greedy_tools_snapshot(),
        "feasible": feasible,
        "validation": validation,
        "checkpoints": [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in result.checkpoints
        ],
        "schema_version": "1.0.0",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
        "cutsize_best": int(result.best_cutsize),
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_json


def _write_ils_result(
    *,
    raw_dir: Path,
    instance_name: str,
    instance_id: str,
    n: int,
    edges: Any,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    result: ILSResult,
) -> Path:
    """Persist a canonical ILS run in the same JSON contract used by the runner."""
    beta_tag = f"{float(beta):.2f}"
    out_json = raw_dir / f"{Path(instance_name).name}__ils__k{k}__b{beta_tag}__seed{seed}.json"
    workdir = raw_dir / f"run_ils__{Path(instance_name).name}__k{k}__b{beta_tag}__seed{seed}"
    workdir.mkdir(parents=True, exist_ok=True)

    graph_path = workdir / "graph.graph"
    write_metis_graph(graph_path, int(n), edges)

    labels = _labels_from_part_of(result.best_part_of, int(n))
    labels_np = np.asarray(labels, dtype=int)

    part_path = workdir / "ils.part"
    part_path.write_text("".join(f"{int(label)}\n" for label in labels), encoding="utf-8")

    feasible, validation = feasible_beta(
        normalize_labels_zero_based(labels_np),
        k=int(k),
        beta=float(beta),
    )

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "instance_id": instance_id,
        "algo": "ils",
        "k": int(k),
        "beta": float(beta),
        "seed": int(seed),
        "budget_time_ms": int(budget_time_ms),
        "status": result.status,
        "returncode": 0,
        "elapsed_ms": int(result.elapsed_ms),
        "stdout": "",
        "stderr": "",
        "metrics": {
            "cutsize_best": int(result.best_cutsize),
            "n_nodes": int(n),
            "balance_tolerance": float(beta),
            "imbalance_raw": None,
        },
        "paths": {
            "workdir": str(workdir),
            "graph_path": str(graph_path),
            "part_path": str(part_path),
        },
        "env": _env_snapshot(),
        "tools": _greedy_tools_snapshot(),
        "feasible": feasible,
        "validation": validation,
        "checkpoints": [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in result.checkpoints
        ],
        "schema_version": "1.0.0",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
        "cutsize_best": int(result.best_cutsize),
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_json


def _write_grasp_result(
    *,
    raw_dir: Path,
    instance_name: str,
    instance_id: str,
    n: int,
    edges: Any,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    result: GRASPResult,
) -> Path:
    """Persist a canonical GRASP run in the same JSON contract used by the runner."""
    beta_tag = f"{float(beta):.2f}"
    out_json = raw_dir / f"{Path(instance_name).name}__grasp__k{k}__b{beta_tag}__seed{seed}.json"
    workdir = raw_dir / f"run_grasp__{Path(instance_name).name}__k{k}__b{beta_tag}__seed{seed}"
    workdir.mkdir(parents=True, exist_ok=True)

    graph_path = workdir / "graph.graph"
    write_metis_graph(graph_path, int(n), edges)

    labels = _labels_from_part_of(result.best_part_of, int(n))
    labels_np = np.asarray(labels, dtype=int)

    part_path = workdir / "grasp.part"
    part_path.write_text("".join(f"{int(label)}\n" for label in labels), encoding="utf-8")

    feasible, validation = feasible_beta(
        normalize_labels_zero_based(labels_np),
        k=int(k),
        beta=float(beta),
    )

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "instance_id": instance_id,
        "algo": "grasp",
        "k": int(k),
        "beta": float(beta),
        "seed": int(seed),
        "budget_time_ms": int(budget_time_ms),
        "status": result.status,
        "returncode": 0,
        "elapsed_ms": int(result.elapsed_ms),
        "stdout": "",
        "stderr": "",
        "metrics": {
            "cutsize_best": int(result.best_cutsize),
            "n_nodes": int(n),
            "balance_tolerance": float(beta),
            "imbalance_raw": None,
        },
        "paths": {
            "workdir": str(workdir),
            "graph_path": str(graph_path),
            "part_path": str(part_path),
        },
        "env": _env_snapshot(),
        "tools": _greedy_tools_snapshot(),
        "feasible": feasible,
        "validation": validation,
        "checkpoints": [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in result.checkpoints
        ],
        "schema_version": "1.0.0",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
        "cutsize_best": int(result.best_cutsize),
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_json


def _write_ts_result(
    *,
    raw_dir: Path,
    instance_name: str,
    instance_id: str,
    n: int,
    edges: Any,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    result: TSResult,
) -> Path:
    """Persist a canonical TS run in the same JSON contract used by the runner."""
    beta_tag = f"{float(beta):.2f}"
    out_json = raw_dir / f"{Path(instance_name).name}__ts__k{k}__b{beta_tag}__seed{seed}.json"
    workdir = raw_dir / f"run_ts__{Path(instance_name).name}__k{k}__b{beta_tag}__seed{seed}"
    workdir.mkdir(parents=True, exist_ok=True)

    graph_path = workdir / "graph.graph"
    write_metis_graph(graph_path, int(n), edges)

    labels = _labels_from_part_of(result.best_part_of, int(n))
    labels_np = np.asarray(labels, dtype=int)

    part_path = workdir / "ts.part"
    part_path.write_text("".join(f"{int(label)}\n" for label in labels), encoding="utf-8")

    feasible, validation = feasible_beta(
        normalize_labels_zero_based(labels_np),
        k=int(k),
        beta=float(beta),
    )

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "instance_id": instance_id,
        "algo": "ts",
        "k": int(k),
        "beta": float(beta),
        "seed": int(seed),
        "budget_time_ms": int(budget_time_ms),
        "status": result.status,
        "returncode": 0,
        "elapsed_ms": int(result.elapsed_ms),
        "stdout": "",
        "stderr": "",
        "metrics": {
            "cutsize_best": int(result.best_cutsize),
            "n_nodes": int(n),
            "balance_tolerance": float(beta),
            "imbalance_raw": None,
        },
        "paths": {
            "workdir": str(workdir),
            "graph_path": str(graph_path),
            "part_path": str(part_path),
        },
        "env": _env_snapshot(),
        "tools": _greedy_tools_snapshot(),
        "feasible": feasible,
        "validation": validation,
        "checkpoints": [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in result.checkpoints
        ],
        "schema_version": "1.0.0",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
        "cutsize_best": int(result.best_cutsize),
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_json


def run_plan(plan_path: Path) -> None:
    """Executa uma campanha mínima a partir de um plano YAML."""
    plan = _load_plan(plan_path)
    runs = _planned_runs(plan)

    if not runs:
        raise ValueError("Plan produced no runnable entries.")

    instances_cfg = plan.get("instances", {}) or {}
    output_cfg = plan.get("output", {}) or {}

    base_dir = Path(instances_cfg.get("base_dir", "."))
    manifest_out_value = instances_cfg.get("manifest_out")
    manifest_out = Path(manifest_out_value) if manifest_out_value else None
    raw_dir = Path(output_cfg.get("raw_dir", "data/results_raw"))
    raw_dir.mkdir(parents=True, exist_ok=True)

    produced_outputs: list[Path] = []

    for run in runs:
        instance_path = base_dir / run["instance"]

        if run["solver"] == "greedy":
            inst = _read_instance_json(instance_path)
            t0 = time.perf_counter()
            obs = run_greedy_observation(inst, delta_v=float(run["delta_v"]))
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            out_json = _write_greedy_result(
                raw_dir=raw_dir,
                instance_name=run["instance"],
                instance_id=str(inst.get("instance_id", Path(run["instance"]).stem)),
                seed=int(run["seed"]),
                delta_v=float(run["delta_v"]),
                budget_time_ms=int(run["budget_time_ms"]),
                obs=obs,
                elapsed_ms=elapsed_ms,
            )
            produced_outputs.append(out_json)
            continue

        if run["solver"] == "sa":
            inst = _read_instance_json(instance_path)
            n, edges = extract_graph_from_instance(inst)
            adj = _adj_from_edges(n, edges)

            sa_cfg = (plan.get("solvers", {}) or {}).get("sa", {}) or {}
            sa_params = sa_cfg.get("params", {}) or {}

            sa_result = run_sa_partition(
                adj,
                k=int(run["k"]),
                epsilon=float(run["beta"]),
                config=SAConfig(
                    seed=int(run["seed"]),
                    budget_time_ms=int(run["budget_time_ms"]),
                    initial_temp=float(sa_params.get("initial_temp", 1.0)),
                    cooling=float(sa_params.get("cooling", 0.995)),
                    min_temp=float(sa_params.get("min_temp", 1e-3)),
                    max_steps=int(sa_params.get("max_steps", 10_000)),
                    checkpoint_every_nfe=int(sa_params.get("checkpoint_every_nfe", 100)),
                ),
            )

            out_json = _write_sa_result(
                raw_dir=raw_dir,
                instance_name=run["instance"],
                instance_id=str(inst.get("instance_id", Path(run["instance"]).stem)),
                n=int(n),
                edges=edges,
                k=int(run["k"]),
                beta=float(run["beta"]),
                seed=int(run["seed"]),
                budget_time_ms=int(run["budget_time_ms"]),
                result=sa_result,
            )
            produced_outputs.append(out_json)
            continue

        if run["solver"] == "ils":
            inst = _read_instance_json(instance_path)
            n, edges = extract_graph_from_instance(inst)
            adj = _adj_from_edges(n, edges)

            ils_cfg = (plan.get("solvers", {}) or {}).get("ils", {}) or {}
            ils_params = ils_cfg.get("params", {}) or {}

            ils_result = run_ils_partition(
                adj,
                k=int(run["k"]),
                epsilon=float(run["beta"]),
                config=ILSConfig(
                    seed=int(run["seed"]),
                    budget_time_ms=int(run["budget_time_ms"]),
                    max_iters=int(ils_params.get("max_iters", 100)),
                    perturb_moves=int(ils_params.get("perturb_moves", 2)),
                    checkpoint_every_iter=int(ils_params.get("checkpoint_every_iter", 1)),
                ),
            )

            out_json = _write_ils_result(
                raw_dir=raw_dir,
                instance_name=run["instance"],
                instance_id=str(inst.get("instance_id", Path(run["instance"]).stem)),
                n=int(n),
                edges=edges,
                k=int(run["k"]),
                beta=float(run["beta"]),
                seed=int(run["seed"]),
                budget_time_ms=int(run["budget_time_ms"]),
                result=ils_result,
            )
            produced_outputs.append(out_json)
            continue
        if run["solver"] == "grasp":
            inst = _read_instance_json(instance_path)
            n, edges = extract_graph_from_instance(inst)
            adj = _adj_from_edges(n, edges)

            grasp_cfg = (plan.get("solvers", {}) or {}).get("grasp", {}) or {}
            grasp_params = grasp_cfg.get("params", {}) or {}

            grasp_result = run_grasp_partition(
                adj,
                k=int(run["k"]),
                epsilon=float(run["beta"]),
                config=GRASPConfig(
                    seed=int(run["seed"]),
                    budget_time_ms=int(run["budget_time_ms"]),
                    alpha=float(grasp_params.get("alpha", 0.30)),
                    max_iters=int(grasp_params.get("max_iters", 100)),
                    checkpoint_every_iter=int(grasp_params.get("checkpoint_every_iter", 1)),
                ),
            )

            out_json = _write_grasp_result(
                raw_dir=raw_dir,
                instance_name=run["instance"],
                instance_id=str(inst.get("instance_id", Path(run["instance"]).stem)),
                n=int(n),
                edges=edges,
                k=int(run["k"]),
                beta=float(run["beta"]),
                seed=int(run["seed"]),
                budget_time_ms=int(run["budget_time_ms"]),
                result=grasp_result,
            )
            produced_outputs.append(out_json)
            continue
        if run["solver"] == "ts":
            inst = _read_instance_json(instance_path)
            n, edges = extract_graph_from_instance(inst)
            adj = _adj_from_edges(n, edges)

            ts_cfg = (plan.get("solvers", {}) or {}).get("ts", {}) or {}
            ts_params = ts_cfg.get("params", {}) or {}

            ts_result = run_ts_partition(
                adj,
                k=int(run["k"]),
                epsilon=float(run["beta"]),
                config=TSConfig(
                    seed=int(run["seed"]),
                    budget_time_ms=int(run["budget_time_ms"]),
                    max_steps=int(ts_params.get("max_steps", 10_000)),
                    min_tenure=int(ts_params.get("min_tenure", 5)),
                    tenure_scale=float(ts_params.get("tenure_scale", 1.0)),
                    tenure_jitter=int(ts_params.get("tenure_jitter", 4)),
                    checkpoint_every_nfe=int(ts_params.get("checkpoint_every_nfe", 100)),
                    frequency_penalty=float(ts_params.get("frequency_penalty", 0.01)),
                ),
            )

            out_json = _write_ts_result(
                raw_dir=raw_dir,
                instance_name=run["instance"],
                instance_id=str(inst.get("instance_id", Path(run["instance"]).stem)),
                n=int(n),
                edges=edges,
                k=int(run["k"]),
                beta=float(run["beta"]),
                seed=int(run["seed"]),
                budget_time_ms=int(run["budget_time_ms"]),
                result=ts_result,
            )
            produced_outputs.append(out_json)
            continue
        stem = Path(run["instance"]).name
        beta_tag = f"{float(run['beta']):.2f}"
        out_json = raw_dir / (
            f"{stem}__{run['solver']}__k{run['k']}__b{beta_tag}__seed{run['seed']}.json"
        )
        workdir = raw_dir / (
            f"run_{run['solver']}__{stem}__k{run['k']}__b{beta_tag}__seed{run['seed']}"
        )

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
        produced_outputs.append(out_json)

    if manifest_out is not None:
        _write_manifest_index(output_files=produced_outputs, manifest_out=manifest_out)
