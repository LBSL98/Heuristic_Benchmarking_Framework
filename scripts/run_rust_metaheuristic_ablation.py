# ruff: noqa: E402
"""Run controlled Python-vs-Rust implementation-maturity ablations.

This harness compares each validated Rust metaheuristic only against its
canonical Python counterpart:

- SA vs SA-Rust
- ILS vs ILS-Rust
- GRASP vs GRASP-Rust

It is implementation-maturity evidence, not a main benchmark, not a selector
experiment, and not a CART-validity claim.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import platform
import shutil
import socket
import statistics
import sys
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import numpy as np
from jsonschema import Draft7Validator

from heuristics.grasp import GRASPConfig, run_grasp_partition
from heuristics.ils import ILSConfig, run_ils_partition
from heuristics.sa import SAConfig, run_sa_partition
from hpc_framework.grasp_rust_adapter import run_grasp_rust_binary
from hpc_framework.ils_rust_adapter import run_ils_rust_binary
from hpc_framework.runner import compute_cutsize_edges_labels, feasible_beta
from hpc_framework.sa_rust_adapter import run_sa_rust_binary
from hpc_framework.solvers.common import read_partition_labels, write_metis_graph


@dataclass(frozen=True)
class AblationCase:
    """Controlled ablation instance."""

    name: str
    n: int
    edges: list[list[int]]
    k: int
    beta: float
    budget_time_ms: int = 5000


@dataclass(frozen=True)
class AlgorithmProfile:
    """Frozen profile used for one Python/Rust algorithm family."""

    family: str
    python_algo: str
    rust_algo: str
    params: dict[str, Any]


def default_profiles() -> list[AlgorithmProfile]:
    """Return frozen D-012-compatible ablation profiles."""
    return [
        AlgorithmProfile(
            family="sa",
            python_algo="sa",
            rust_algo="sa_rust",
            params={
                "initial_temp": 1.0,
                "cooling": 0.997,
                "min_temp": 0.001,
                "max_steps": 100_000,
                "checkpoint_every_nfe": 100,
            },
        ),
        AlgorithmProfile(
            family="ils",
            python_algo="ils",
            rust_algo="ils_rust",
            params={
                "max_iters": 100,
                "perturb_moves": 4,
                "checkpoint_every_iter": 1,
            },
        ),
        AlgorithmProfile(
            family="grasp",
            python_algo="grasp",
            rust_algo="grasp_rust",
            params={
                "alpha": 0.30,
                "max_iters": 100,
                "checkpoint_every_iter": 1,
            },
        ),
    ]


def default_cases() -> list[AblationCase]:
    """Return the preregistered controlled implementation-maturity panel.

    The panel mirrors the TS-Rust ablation scale and keeps one synthetic,
    one social/snapshot-like, and one road-like morphology from the audited
    instance set whenever the files are present.
    """
    return [
        AblationCase(
            name="synthetic_modnull_n3000_p50",
            n=3000,
            edges=[],
            k=8,
            beta=0.03,
        ),
        AblationCase(
            name="snap_ca_hepth_gcc",
            n=0,
            edges=[],
            k=8,
            beta=0.03,
        ),
        AblationCase(
            name="roadnet_ca_bfs_10000_seed42",
            n=0,
            edges=[],
            k=8,
            beta=0.03,
        ),
    ]


def _load_instance_payload(path: Path) -> dict[str, Any]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_graph(inst: dict[str, Any]) -> tuple[int, np.ndarray]:
    graph = inst.get("graph") or inst
    n_raw = (
        graph.get("n")
        or graph.get("num_nodes")
        or graph.get("numVertices")
        or graph.get("num_nodes_v1_1")
        or graph.get("n_vertices")
        or graph.get("nNodes")
    )
    if n_raw is not None:
        n = int(n_raw)
    elif "nodes" in graph:
        n = len(graph["nodes"])
    else:
        raise KeyError(f"instance missing node count; keys={list(graph.keys())}")

    edges = (
        graph.get("edges")
        or graph.get("edge_list")
        or graph.get("edgeIndex")
        or graph.get("edge_index")
    )
    if edges is None:
        raise KeyError(f"instance missing edges; keys={list(graph.keys())}")

    edges_arr = np.asarray(edges, dtype=np.int64)
    if edges_arr.ndim != 2 or edges_arr.shape[1] != 2:
        raise ValueError("edges must be an (m,2) endpoint array")
    return n, edges_arr


def _adj_from_edges(n: int, edges: np.ndarray) -> dict[int, set[int]]:
    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    for u, v in edges:
        ui = int(u)
        vi = int(v)
        if ui == vi:
            continue
        adj[ui].add(vi)
        adj[vi].add(ui)
    return adj


def _labels_from_part_of(part_of: dict[int, int], n: int) -> np.ndarray:
    return np.asarray([int(part_of[i]) for i in range(n)], dtype=int)


def _schema_errors(payload: dict[str, Any]) -> list[str]:
    schema_path = Path("specs/jsonschema/solver_run.schema.v1.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft7Validator(schema).iter_errors(payload), key=lambda e: list(e.path))
    return [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def _checkpoint_invariants(checkpoints: list[dict[str, Any]]) -> dict[str, bool]:
    if not checkpoints:
        return {
            "non_empty": False,
            "time_non_decreasing": False,
            "cut_non_increasing": False,
            "nfe_non_decreasing": False,
        }
    times = [int(cp["time_ms"]) for cp in checkpoints]
    cuts = [int(cp["cutsize_best"]) for cp in checkpoints]
    nfes = [int(cp["nfe"]) for cp in checkpoints if cp.get("nfe") is not None]
    return {
        "non_empty": True,
        "time_non_decreasing": all(a <= b for a, b in zip(times, times[1:], strict=False)),
        "cut_non_increasing": all(a >= b for a, b in zip(cuts, cuts[1:], strict=False)),
        "nfe_non_decreasing": all(a <= b for a, b in zip(nfes, nfes[1:], strict=False)),
    }


def _instance_id_from_path(path: Path) -> str:
    name = path.name
    if name.endswith(".json.gz"):
        return name.removesuffix(".json.gz")
    if name.endswith(".json"):
        return name.removesuffix(".json")
    return path.stem


def _resolve_case_paths(instances_dir: Path, include: list[str] | None) -> list[Path]:
    if include:
        paths = [instances_dir / item for item in include]
    else:
        preferred = [
            "synthetic_modnull_n3000_p50.json.gz",
            "snap_ca_hepth_gcc.json.gz",
            "roadnet_ca_bfs_10000_seed42.json.gz",
        ]
        paths = [instances_dir / item for item in preferred]

    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "missing ablation instance files: "
            + ", ".join(missing)
            + ". Pass --include with existing files or run from the repository with data/instances populated."
        )
    return paths


def _canonical_payload(
    *,
    instance_id: str,
    algo: str,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    status: str,
    elapsed_ms: int,
    nfe: int,
    cutsize_best: int,
    labels: np.ndarray,
    edges: np.ndarray,
    checkpoints: list[dict[str, Any]],
    workdir: Path,
    graph_path: Path,
    part_path: Path,
    stdout: str = "",
    stderr: str = "",
    returncode: int | None = 0,
) -> dict[str, Any]:
    labels_norm = labels.astype(int, copy=False)
    cut_from_labels = compute_cutsize_edges_labels(edges, labels_norm)
    feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)
    n_nodes = int(labels_norm.shape[0])
    checkpoint_payloads = [
        {
            "time_ms": int(cp["time_ms"]),
            "cutsize_best": int(cp["cutsize_best"]),
            "nfe": int(cp["nfe"]) if cp.get("nfe") is not None else None,
        }
        for cp in checkpoints
    ]
    payload: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "schema_version": "solver-run-v1",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
        "run_id": f"{instance_id}__{algo}__k{k}__b{beta:.2f}__seed{seed}",
        "instance_id": instance_id,
        "algo": algo,
        "k": int(k),
        "beta": float(beta),
        "seed": int(seed),
        "budget_time_ms": int(budget_time_ms),
        "status": str(status),
        "elapsed_ms": int(elapsed_ms),
        "cutsize_best": int(cutsize_best),
        "metrics": {
            "cutsize_best": int(cutsize_best),
            "n_nodes": n_nodes,
            "balance_tolerance": float(beta),
            "imbalance_raw": None,
        },
        "env": {
            "hostname": socket.gethostname(),
            "python": platform.python_version(),
            "os": platform.system(),
            "os_release": platform.release(),
            "cpu": {
                "model": platform.machine(),
                "cores_logical": int(os.cpu_count() or 0),
                "cores_physical": None,
                "freq_mhz": None,
            },
            "harness": "scripts/run_rust_metaheuristic_ablation.py",
        },
        "tools": {
            "gpmetis": {"exists": shutil.which("gpmetis") is not None, "version": ""},
            "kaffpa": {"exists": shutil.which("kaffpa") is not None, "version": ""},
            "rust_fidelity_binary": {"exists": True, "version": ""},
        },
        "feasible": bool(feasible),
        "validation": validation,
        "nfe": int(nfe),
        "checkpoints": checkpoint_payloads,
        "paths": {
            "workdir": str(workdir),
            "graph_path": str(graph_path),
            "part_path": str(part_path),
        },
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
        "environment": {
            "harness": "scripts/run_rust_metaheuristic_ablation.py",
        },
    }
    payload["ablation_checks"] = {
        "cut_matches_labels": int(cut_from_labels) == int(cutsize_best),
        "schema_compatible": _schema_errors(payload) == [],
        "checkpoint_invariants": all(_checkpoint_invariants(checkpoint_payloads).values()),
        "final_checkpoint_matches_best": bool(checkpoint_payloads)
        and checkpoint_payloads[-1]["cutsize_best"] == int(cutsize_best),
        "final_checkpoint_matches_nfe": bool(checkpoint_payloads)
        and checkpoint_payloads[-1]["nfe"] == int(nfe),
        "feasible": bool(feasible),
    }
    payload["schema_errors"] = _schema_errors(payload)
    return payload


def _write_part(path: Path, labels: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{int(x)}\n" for x in labels.tolist()), encoding="utf-8")


def _run_python_family(
    *,
    family: str,
    adj: dict[int, set[int]],
    edges: np.ndarray,
    instance_id: str,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    params: dict[str, Any],
    workdir: Path,
    graph_path: Path,
) -> dict[str, Any]:
    result: Any
    if family == "sa":
        result = run_sa_partition(
            adj,
            k=k,
            epsilon=beta,
            config=SAConfig(seed=seed, budget_time_ms=budget_time_ms, **params),
        )
        labels = _labels_from_part_of(result.best_part_of, len(adj))
        checkpoints = [
            {"time_ms": cp.time_ms, "cutsize_best": cp.cutsize_best, "nfe": cp.nfe}
            for cp in result.checkpoints
        ]
        algo = "sa"
    elif family == "ils":
        result = run_ils_partition(
            adj,
            k=k,
            epsilon=beta,
            config=ILSConfig(seed=seed, budget_time_ms=budget_time_ms, **params),
        )
        labels = _labels_from_part_of(result.best_part_of, len(adj))
        checkpoints = [
            {"time_ms": cp.time_ms, "cutsize_best": cp.cutsize_best, "nfe": cp.nfe}
            for cp in result.checkpoints
        ]
        algo = "ils"
    elif family == "grasp":
        result = run_grasp_partition(
            adj,
            k=k,
            epsilon=beta,
            config=GRASPConfig(seed=seed, budget_time_ms=budget_time_ms, **params),
        )
        labels = _labels_from_part_of(result.best_part_of, len(adj))
        checkpoints = [
            {"time_ms": cp.time_ms, "cutsize_best": cp.cutsize_best, "nfe": cp.nfe}
            for cp in result.checkpoints
        ]
        algo = "grasp"
    else:
        raise ValueError(f"unsupported family: {family}")

    part_path = workdir / f"{algo}.part"
    _write_part(part_path, labels)

    return _canonical_payload(
        instance_id=instance_id,
        algo=algo,
        k=k,
        beta=beta,
        seed=seed,
        budget_time_ms=budget_time_ms,
        status=result.status,
        elapsed_ms=int(result.elapsed_ms),
        nfe=int(result.nfe),
        cutsize_best=int(result.best_cutsize),
        labels=labels,
        edges=edges,
        checkpoints=checkpoints,
        workdir=workdir,
        graph_path=graph_path,
        part_path=part_path,
    )


def _run_rust_family(
    *,
    family: str,
    graph_path: Path,
    edges: np.ndarray,
    instance_id: str,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    params: dict[str, Any],
    workdir: Path,
) -> dict[str, Any]:
    run: Any
    if family == "sa":
        algo = "sa_rust"
        raw_json = workdir / "sa_rust_result.json"
        part_path = workdir / "sa_rust.part"
        run = run_sa_rust_binary(
            graph_path=graph_path,
            k=k,
            beta=beta,
            seed=seed,
            budget_time_ms=budget_time_ms,
            out_json=raw_json,
            part_path=part_path,
            **params,
        )
    elif family == "ils":
        algo = "ils_rust"
        raw_json = workdir / "ils_rust_result.json"
        part_path = workdir / "ils_rust.part"
        run = run_ils_rust_binary(
            graph_path=graph_path,
            k=k,
            beta=beta,
            seed=seed,
            budget_time_ms=budget_time_ms,
            out_json=raw_json,
            part_path=part_path,
            **params,
        )
    elif family == "grasp":
        algo = "grasp_rust"
        raw_json = workdir / "grasp_rust_result.json"
        part_path = workdir / "grasp_rust.part"
        run = run_grasp_rust_binary(
            graph_path=graph_path,
            k=k,
            beta=beta,
            seed=seed,
            budget_time_ms=budget_time_ms,
            out_json=raw_json,
            part_path=part_path,
            **params,
        )
    else:
        raise ValueError(f"unsupported family: {family}")

    raw = run.payload
    labels = read_partition_labels(part_path)

    payload = _canonical_payload(
        instance_id=instance_id,
        algo=algo,
        k=k,
        beta=beta,
        seed=seed,
        budget_time_ms=budget_time_ms,
        status=str(raw["status"]),
        elapsed_ms=int(raw["elapsed_ms"]),
        nfe=int(raw["nfe"]),
        cutsize_best=int(raw["cutsize_best"]),
        labels=labels,
        edges=edges,
        checkpoints=list(raw["checkpoints"]),
        workdir=workdir,
        graph_path=graph_path,
        part_path=part_path,
        stdout=run.stdout,
        stderr=run.stderr,
        returncode=run.returncode,
    )
    payload["raw_json_path"] = str(raw_json)
    return payload


def _nfe_per_second(row: dict[str, Any]) -> float | None:
    elapsed_ms = int(row["elapsed_ms"])
    nfe = int(row["nfe"])
    if elapsed_ms <= 0:
        return None
    return nfe / (elapsed_ms / 1000.0)


def _format_ratio(*, numerator: float | None, denominator: float | None) -> str:
    if numerator is None or denominator is None or denominator == 0:
        return ""
    return f"{(numerator / denominator):.6f}"


def _load_or_prepare_instance(path: Path, raw_dir: Path) -> tuple[str, int, np.ndarray, Path]:
    instance_id = _instance_id_from_path(path)
    inst = _load_instance_payload(path)
    n, edges = _extract_graph(inst)

    graph_path = raw_dir / "_graphs" / f"{instance_id}.graph"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    write_metis_graph(graph_path, n, edges)
    return instance_id, n, edges, graph_path


def run_ablation(
    *,
    instances_dir: Path,
    include: list[str] | None,
    output_dir: Path,
    seeds: list[int],
    budget_time_ms: int,
) -> dict[str, Any]:
    """Run the controlled ablation and persist report artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    profiles = default_profiles()
    instance_paths = _resolve_case_paths(instances_dir, include)

    rows: list[dict[str, Any]] = []
    paired_rows: list[dict[str, Any]] = []

    started = time.perf_counter()
    for instance_path in instance_paths:
        instance_id, n, edges, graph_path = _load_or_prepare_instance(instance_path, raw_dir)
        adj = _adj_from_edges(n, edges)

        for seed in seeds:
            for profile in profiles:
                pair: dict[str, Any] = {
                    "instance_id": instance_id,
                    "family": profile.family,
                    "seed": seed,
                    "k": 8,
                    "beta": 0.03,
                    "budget_time_ms": budget_time_ms,
                    "params": json.dumps(profile.params, sort_keys=True),
                }

                py_workdir = raw_dir / f"{instance_id}__{profile.python_algo}__seed{seed}"
                rs_workdir = raw_dir / f"{instance_id}__{profile.rust_algo}__seed{seed}"
                py_workdir.mkdir(parents=True, exist_ok=True)
                rs_workdir.mkdir(parents=True, exist_ok=True)

                py_payload = _run_python_family(
                    family=profile.family,
                    adj=adj,
                    edges=edges,
                    instance_id=instance_id,
                    k=8,
                    beta=0.03,
                    seed=seed,
                    budget_time_ms=budget_time_ms,
                    params=profile.params,
                    workdir=py_workdir,
                    graph_path=graph_path,
                )
                rs_payload = _run_rust_family(
                    family=profile.family,
                    graph_path=graph_path,
                    edges=edges,
                    instance_id=instance_id,
                    k=8,
                    beta=0.03,
                    seed=seed,
                    budget_time_ms=budget_time_ms,
                    params=profile.params,
                    workdir=rs_workdir,
                )

                for payload in [py_payload, rs_payload]:
                    out_path = raw_dir / f"{payload['run_id']}.json"
                    out_path.write_text(
                        json.dumps(payload, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    nfe_s = _nfe_per_second(payload)
                    rows.append(
                        {
                            "instance_id": instance_id,
                            "family": profile.family,
                            "algo": payload["algo"],
                            "seed": seed,
                            "status": payload["status"],
                            "elapsed_ms": payload["elapsed_ms"],
                            "budget_time_ms": payload["budget_time_ms"],
                            "overshoot_ms": int(payload["elapsed_ms"]) - budget_time_ms,
                            "nfe": payload["nfe"],
                            "nfe_per_second": "" if nfe_s is None else f"{nfe_s:.6f}",
                            "cutsize_best": payload["cutsize_best"],
                            "feasible": payload["feasible"],
                            "cut_matches_labels": payload["ablation_checks"]["cut_matches_labels"],
                            "schema_compatible": payload["ablation_checks"]["schema_compatible"],
                            "checkpoint_invariants": payload["ablation_checks"][
                                "checkpoint_invariants"
                            ],
                            "final_checkpoint_matches_best": payload["ablation_checks"][
                                "final_checkpoint_matches_best"
                            ],
                            "final_checkpoint_matches_nfe": payload["ablation_checks"][
                                "final_checkpoint_matches_nfe"
                            ],
                            "artifact_path": str(out_path),
                        }
                    )

                py_nfe_s = _nfe_per_second(py_payload)
                rs_nfe_s = _nfe_per_second(rs_payload)
                pair.update(
                    {
                        "python_algo": py_payload["algo"],
                        "rust_algo": rs_payload["algo"],
                        "python_cut": py_payload["cutsize_best"],
                        "rust_cut": rs_payload["cutsize_best"],
                        "delta_cut_rust_minus_python": int(rs_payload["cutsize_best"])
                        - int(py_payload["cutsize_best"]),
                        "rust_better_cut": int(rs_payload["cutsize_best"])
                        < int(py_payload["cutsize_best"]),
                        "same_cut": int(rs_payload["cutsize_best"])
                        == int(py_payload["cutsize_best"]),
                        "python_elapsed_ms": py_payload["elapsed_ms"],
                        "rust_elapsed_ms": rs_payload["elapsed_ms"],
                        "python_overshoot_ms": int(py_payload["elapsed_ms"]) - budget_time_ms,
                        "rust_overshoot_ms": int(rs_payload["elapsed_ms"]) - budget_time_ms,
                        "python_nfe": py_payload["nfe"],
                        "rust_nfe": rs_payload["nfe"],
                        "python_nfe_per_second": "" if py_nfe_s is None else f"{py_nfe_s:.6f}",
                        "rust_nfe_per_second": "" if rs_nfe_s is None else f"{rs_nfe_s:.6f}",
                        "nfe_per_second_ratio_rust_over_python": _format_ratio(
                            numerator=rs_nfe_s,
                            denominator=py_nfe_s,
                        ),
                        "both_feasible": bool(py_payload["feasible"])
                        and bool(rs_payload["feasible"]),
                        "both_schema_compatible": py_payload["ablation_checks"]["schema_compatible"]
                        and rs_payload["ablation_checks"]["schema_compatible"],
                        "both_cut_consistent": py_payload["ablation_checks"]["cut_matches_labels"]
                        and rs_payload["ablation_checks"]["cut_matches_labels"],
                        "both_checkpoint_consistent": py_payload["ablation_checks"][
                            "checkpoint_invariants"
                        ]
                        and rs_payload["ablation_checks"]["checkpoint_invariants"],
                    }
                )
                paired_rows.append(pair)

    _write_csv(output_dir / "runs.csv", rows)
    _write_csv(output_dir / "paired_summary.csv", paired_rows)

    report = _summarize(
        rows=rows,
        paired_rows=paired_rows,
        profiles=profiles,
        seeds=seeds,
        budget_time_ms=budget_time_ms,
        elapsed_wall_s=time.perf_counter() - started,
    )
    (output_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _float_values(rows: Iterable[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(key, "")
        if value == "" or value is None:
            continue
        values.append(float(value))
    return values


def _summarize(
    *,
    rows: list[dict[str, Any]],
    paired_rows: list[dict[str, Any]],
    profiles: list[AlgorithmProfile],
    seeds: list[int],
    budget_time_ms: int,
    elapsed_wall_s: float,
) -> dict[str, Any]:
    families = [profile.family for profile in profiles]
    expected_pairs = len(paired_rows)

    invalid_rows = [
        row
        for row in rows
        if not (
            bool(row["feasible"])
            and bool(row["cut_matches_labels"])
            and bool(row["schema_compatible"])
            and bool(row["checkpoint_invariants"])
            and bool(row["final_checkpoint_matches_best"])
            and bool(row["final_checkpoint_matches_nfe"])
        )
    ]
    invalid_pairs = [
        row
        for row in paired_rows
        if not (
            bool(row["both_feasible"])
            and bool(row["both_schema_compatible"])
            and bool(row["both_cut_consistent"])
            and bool(row["both_checkpoint_consistent"])
        )
    ]

    by_family: dict[str, dict[str, Any]] = {}
    for family in families:
        fam_pairs = [row for row in paired_rows if row["family"] == family]
        deltas = [int(row["delta_cut_rust_minus_python"]) for row in fam_pairs]
        ratios = _float_values(fam_pairs, "nfe_per_second_ratio_rust_over_python")
        by_family[family] = {
            "pairs": len(fam_pairs),
            "rust_better_cut_pairs": sum(1 for row in fam_pairs if row["rust_better_cut"]),
            "same_cut_pairs": sum(1 for row in fam_pairs if row["same_cut"]),
            "python_better_cut_pairs": sum(
                1 for row in fam_pairs if not row["rust_better_cut"] and not row["same_cut"]
            ),
            "median_delta_cut_rust_minus_python": statistics.median(deltas) if deltas else None,
            "median_nfe_per_second_ratio_rust_over_python": (
                statistics.median(ratios) if ratios else None
            ),
            "max_python_overshoot_ms": (
                max(int(row["python_overshoot_ms"]) for row in fam_pairs) if fam_pairs else None
            ),
            "max_rust_overshoot_ms": (
                max(int(row["rust_overshoot_ms"]) for row in fam_pairs) if fam_pairs else None
            ),
        }

    return {
        "schema_version": "rust-metaheuristic-ablation-v1",
        "claim_boundary": (
            "Controlled implementation-maturity ablation only. Results compare each Rust "
            "metaheuristic only with its Python counterpart. This does not establish "
            "trajectory equivalence, full algorithmic equivalence, multilevel competitiveness, "
            "selector usefulness, CART validity, or benchmark-wide superiority."
        ),
        "budget_time_ms": int(budget_time_ms),
        "seeds": seeds,
        "profiles": [asdict(profile) for profile in profiles],
        "pairs": expected_pairs,
        "runs": len(rows),
        "invalid_rows": len(invalid_rows),
        "invalid_pairs": len(invalid_pairs),
        "passed": len(invalid_rows) == 0 and len(invalid_pairs) == 0,
        "by_family": by_family,
        "elapsed_wall_s": elapsed_wall_s,
    }


def _parse_include(raw: list[str] | None) -> list[str] | None:
    if not raw:
        return None
    out: list[str] = []
    for item in raw:
        out.extend([part for part in item.split(",") if part])
    return out


def _parse_seeds(raw: str) -> list[int]:
    seeds = [int(part.strip()) for part in raw.split(",") if part.strip()]
    if not seeds:
        raise ValueError("at least one seed is required")
    return seeds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances-dir", type=Path, default=Path("data/instances"))
    parser.add_argument("--include", action="append", default=None)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seeds", default="42,43,44,45,46")
    parser.add_argument("--budget-time-ms", type=int, default=5000)
    args = parser.parse_args()

    report = run_ablation(
        instances_dir=args.instances_dir,
        include=_parse_include(args.include),
        output_dir=args.out_dir,
        seeds=_parse_seeds(args.seeds),
        budget_time_ms=args.budget_time_ms,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
