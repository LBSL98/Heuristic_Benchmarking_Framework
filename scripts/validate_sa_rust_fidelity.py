# ruff: noqa: E402
"""Validate SA-Rust-fidelity against the canonical Python SA implementation.

This script checks semantic and artifact-level invariants. It does not perform
an implementation-maturity ablation and must not be used as performance evidence
by itself.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import numpy as np
from jsonschema import Draft7Validator

from heuristics.sa import SAConfig, run_sa_partition
from hpc_framework.runner import (
    compute_cutsize_edges_labels,
    extract_graph_from_instance,
    feasible_beta,
    run_one,
)
from hpc_framework.solvers.common import read_partition_labels


@dataclass(frozen=True)
class ValidationCase:
    """Controlled validation case."""

    name: str
    n: int
    edges: list[list[int]]
    k: int
    beta: float
    seed: int
    budget_time_ms: int
    initial_temp: float = 1.0
    cooling: float = 0.997
    min_temp: float = 0.001
    max_steps: int = 200
    checkpoint_every_nfe: int = 10


def _path_case() -> ValidationCase:
    n = 12
    return ValidationCase(
        name="path12_k3_seed42",
        n=n,
        edges=[[i, i + 1] for i in range(n - 1)],
        k=3,
        beta=0.10,
        seed=42,
        budget_time_ms=1000,
    )


def _cycle_case() -> ValidationCase:
    n = 16
    edges = [[i, (i + 1) % n] for i in range(n)]
    return ValidationCase(
        name="cycle16_k4_seed7",
        n=n,
        edges=edges,
        k=4,
        beta=0.10,
        seed=7,
        budget_time_ms=1000,
    )


def _two_cliques_bridge_case() -> ValidationCase:
    n = 12
    edges: list[list[int]] = []
    for base in [0, 6]:
        for i in range(base, base + 6):
            for j in range(i + 1, base + 6):
                edges.append([i, j])
    edges.append([5, 6])
    return ValidationCase(
        name="two_cliques_bridge12_k2_seed123",
        n=n,
        edges=edges,
        k=2,
        beta=0.10,
        seed=123,
        budget_time_ms=1000,
    )


def default_cases() -> list[ValidationCase]:
    """Return deterministic controlled cases for validation."""
    return [_path_case(), _cycle_case(), _two_cliques_bridge_case()]


def _adj_from_edges(n: int, edges: list[list[int]]) -> dict[int, set[int]]:
    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    for u, v in edges:
        if u == v:
            continue
        adj[int(u)].add(int(v))
        adj[int(v)].add(int(u))
    return adj


def _labels_from_part_of(part_of: dict[int, int], n: int) -> np.ndarray:
    return np.asarray([int(part_of[i]) for i in range(n)], dtype=int)


def _write_instance(path: Path, case: ValidationCase) -> None:
    payload = {
        "instance_id": case.name,
        "num_nodes": case.n,
        "edges": case.edges,
    }
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(payload, f)


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


def _schema_errors(payload: dict[str, Any]) -> list[str]:
    schema_path = Path("specs/jsonschema/solver_run.schema.v1.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft7Validator(schema).iter_errors(payload), key=lambda e: list(e.path))
    return [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def _python_sa_payload(case: ValidationCase) -> dict[str, Any]:
    adj = _adj_from_edges(case.n, case.edges)
    result = run_sa_partition(
        adj,
        k=case.k,
        epsilon=case.beta,
        config=SAConfig(
            seed=case.seed,
            budget_time_ms=case.budget_time_ms,
            initial_temp=case.initial_temp,
            cooling=case.cooling,
            min_temp=case.min_temp,
            max_steps=case.max_steps,
            checkpoint_every_nfe=case.checkpoint_every_nfe,
        ),
    )
    labels = _labels_from_part_of(result.best_part_of, case.n)
    cut_from_labels = compute_cutsize_edges_labels(np.asarray(case.edges, dtype=int), labels)
    feasible, validation = feasible_beta(labels, k=case.k, beta=case.beta)

    return {
        "algo": "sa",
        "status": result.status,
        "elapsed_ms": int(result.elapsed_ms),
        "nfe": int(result.nfe),
        "cutsize_best": int(result.best_cutsize),
        "cut_from_labels": int(cut_from_labels),
        "labels": labels.tolist(),
        "feasible": bool(feasible),
        "validation": validation,
        "checkpoints": [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in result.checkpoints
        ],
    }


def _rust_sa_payload(case: ValidationCase, work_root: Path) -> dict[str, Any]:
    instance_path = work_root / f"{case.name}.json.gz"
    out_json = work_root / f"{case.name}__sa_rust.json"
    workdir = work_root / f"{case.name}__work"
    _write_instance(instance_path, case)

    run_one(
        instance_path=instance_path,
        algo="sa_rust",
        k=case.k,
        beta=case.beta,
        seed=case.seed,
        budget_time_ms=case.budget_time_ms,
        out_json=out_json,
        workdir=workdir,
        kahip_preset="fast",
        log_level="info",
    )

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    with gzip.open(instance_path, "rt", encoding="utf-8") as f:
        inst = json.load(f)
    _n, edges = extract_graph_from_instance(inst)

    part_path_value = payload.get("paths", {}).get("part_path")
    if part_path_value is None:
        raise KeyError("sa_rust canonical payload is missing paths.part_path")

    labels = read_partition_labels(Path(part_path_value))
    cut_from_labels = compute_cutsize_edges_labels(edges, labels)

    raw_json_path = Path(str(payload["paths"]["workdir"])) / "sa_rust_result.json"
    if not raw_json_path.exists():
        raise FileNotFoundError(f"SA-Rust raw JSON not found: {raw_json_path}")

    raw_payload = json.loads(raw_json_path.read_text(encoding="utf-8"))

    payload["labels_from_part"] = labels.tolist()
    payload["cut_from_labels"] = int(cut_from_labels)
    payload["schema_errors"] = _schema_errors(payload)
    payload["raw_sa_rust_json_path"] = str(raw_json_path)
    payload["raw_sa_rust_nfe"] = int(raw_payload["nfe"])
    payload["raw_sa_rust_cutsize_best"] = int(raw_payload["cutsize_best"])
    return payload


def validate_case(case: ValidationCase, work_root: Path) -> dict[str, Any]:
    """Validate one controlled case."""
    py = _python_sa_payload(case)
    rs = _rust_sa_payload(case, work_root)

    py_checkpoints = _checkpoint_invariants(py["checkpoints"])
    rs_checkpoints = _checkpoint_invariants(rs["checkpoints"])

    checks = {
        "python_cut_matches_labels": py["cutsize_best"] == py["cut_from_labels"],
        "rust_cut_matches_labels": rs["cutsize_best"] == rs["cut_from_labels"],
        "python_feasible": bool(py["feasible"]),
        "rust_feasible": bool(rs["feasible"]),
        "rust_schema_compatible": rs["schema_errors"] == [],
        "rust_part_path_exists": bool(rs.get("paths", {}).get("part_path"))
        and Path(str(rs["paths"]["part_path"])).exists(),
        "python_checkpoint_invariants": all(py_checkpoints.values()),
        "rust_checkpoint_invariants": all(rs_checkpoints.values()),
        "rust_final_checkpoint_matches_best": rs["checkpoints"][-1]["cutsize_best"]
        == rs["cutsize_best"],
        "rust_raw_json_exists": Path(str(rs["raw_sa_rust_json_path"])).exists(),
        "rust_final_checkpoint_matches_raw_best": rs["checkpoints"][-1]["cutsize_best"]
        == rs["raw_sa_rust_cutsize_best"],
        "rust_final_checkpoint_matches_nfe": rs["checkpoints"][-1]["nfe"] == rs["raw_sa_rust_nfe"],
        "python_final_checkpoint_matches_best": py["checkpoints"][-1]["cutsize_best"]
        == py["cutsize_best"],
        "python_final_checkpoint_matches_nfe": py["checkpoints"][-1]["nfe"] == py["nfe"],
    }

    return {
        "case": case.__dict__,
        "python_sa": py,
        "sa_rust": rs,
        "checkpoint_details": {
            "python_sa": py_checkpoints,
            "sa_rust": rs_checkpoints,
        },
        "checks": checks,
        "passed": all(checks.values()),
        "interpretation": (
            "Artifact and semantic invariant validation only; this does not establish "
            "trajectory equivalence, RNG equivalence, performance superiority, or ablation evidence."
        ),
    }


def run_validation(output: Path) -> dict[str, Any]:
    """Run all validation cases and write a JSON report."""
    with tempfile.TemporaryDirectory(prefix="sa_rust_validation_") as tmp:
        work_root = Path(tmp)
        cases = [validate_case(case, work_root) for case in default_cases()]

    report = {
        "schema_version": "sa-rust-validation-v1",
        "claim_boundary": (
            "This report validates artifact/semantic invariants for SA-Rust-fidelity. "
            "It does not support ablation, performance, selector, CART, or full-portfolio claims."
        ),
        "cases": cases,
        "passed": all(case["passed"] for case in cases),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("audit_reports/sa_rust_validation/sa_rust_validation_report.json"),
    )
    args = parser.parse_args()

    report = run_validation(args.out)
    print(json.dumps({"out": str(args.out), "passed": report["passed"]}, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
