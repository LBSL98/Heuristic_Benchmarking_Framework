"""Run the TS-Python versus TS-Rust implementation-maturity ablation.

The ablation is scoped to the canonical Tabu Search implementation only. It
does not support claims about all metaheuristics or main-portfolio superiority.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from hpc_framework.runner import run_one
from hpc_framework.ts_rust_adapter import ensure_ts_rust_binary


@dataclass(frozen=True)
class AblationCase:
    """One preregistered ablation case."""

    name: str
    instance: Path
    k: int
    beta: float


@dataclass(frozen=True)
class RunRecord:
    """Normalized run record."""

    case_name: str
    instance_id: str
    algo: str
    seed: int
    k: int
    beta: float
    budget_time_ms: int
    elapsed_ms: int
    cutsize_best: int
    feasible: bool
    nfe: int | None
    nfe_per_s: float | None
    status: str
    output_json: str


def _load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        obj = yaml.safe_load(f)
    if not isinstance(obj, dict):
        raise ValueError("Ablation config must be a mapping.")
    return obj


def _cases_from_config(config: dict[str, Any]) -> list[AblationCase]:
    cases: list[AblationCase] = []
    for item in config.get("cases", []):
        cases.append(
            AblationCase(
                name=str(item["name"]),
                instance=Path(item["instance"]),
                k=int(item["k"]),
                beta=float(item["beta"]),
            )
        )
    if not cases:
        raise ValueError("Ablation config produced no cases.")
    return cases


def _final_nfe(payload: dict[str, Any]) -> int | None:
    checkpoints = payload.get("checkpoints", [])
    if not checkpoints:
        return None
    nfe = checkpoints[-1].get("nfe")
    if nfe is None:
        return None
    return int(nfe)


def _nfe_per_s(nfe: int | None, elapsed_ms: int) -> float | None:
    if nfe is None or elapsed_ms <= 0:
        return None
    return float(nfe) / (float(elapsed_ms) / 1000.0)


def _throughput_ratio(
    *, python_nfe_per_s: float | None, rust_nfe_per_s: float | None
) -> float | None:
    if python_nfe_per_s is None or python_nfe_per_s == 0.0:
        return None
    if rust_nfe_per_s is None:
        return None
    return rust_nfe_per_s / python_nfe_per_s


def _first_time_to_target(checkpoints: list[dict[str, Any]], target_cut: int) -> int | None:
    for checkpoint in sorted(checkpoints, key=lambda cp: int(cp["time_ms"])):
        if int(checkpoint["cutsize_best"]) <= target_cut:
            return int(checkpoint["time_ms"])
    return None


def _cut_at_time(checkpoints: list[dict[str, Any]], time_ms: int) -> int | None:
    if not checkpoints:
        return None

    ordered = sorted(checkpoints, key=lambda cp: int(cp["time_ms"]))
    current = int(ordered[0]["cutsize_best"])
    for checkpoint in ordered:
        if int(checkpoint["time_ms"]) <= time_ms:
            current = int(checkpoint["cutsize_best"])
        else:
            break
    return current


def _run_single(
    *,
    case: AblationCase,
    algo: str,
    seed: int,
    budget_time_ms: int,
    raw_dir: Path,
) -> tuple[RunRecord, dict[str, Any]]:
    out_json = raw_dir / f"{case.name}__{algo}__k{case.k}__b{case.beta:.2f}__seed{seed}.json"
    workdir = raw_dir / "work" / f"{case.name}__{algo}__seed{seed}"

    artifact = run_one(
        instance_path=case.instance,
        algo=algo,
        k=case.k,
        beta=case.beta,
        seed=seed,
        budget_time_ms=budget_time_ms,
        out_json=out_json,
        workdir=workdir,
        kahip_preset="fast",
        log_level="info",
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    nfe = _final_nfe(payload)

    record = RunRecord(
        case_name=case.name,
        instance_id=str(payload["instance_id"]),
        algo=algo,
        seed=seed,
        k=case.k,
        beta=case.beta,
        budget_time_ms=budget_time_ms,
        elapsed_ms=int(payload["elapsed_ms"]),
        cutsize_best=int(payload["cutsize_best"]),
        feasible=bool(payload["feasible"]),
        nfe=nfe,
        nfe_per_s=_nfe_per_s(nfe, int(payload["elapsed_ms"])),
        status=str(artifact.status),
        output_json=str(out_json),
    )
    return record, payload


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_ablation(config_path: Path, out_dir: Path) -> dict[str, Any]:
    """Run the preregistered TS-Python vs TS-Rust ablation."""
    config = _load_config(config_path)
    cases = _cases_from_config(config)
    seeds = [int(seed) for seed in config.get("seeds", [])]
    if not seeds:
        raise ValueError("Ablation config must include at least one seed.")

    budget_time_ms = int(config["budget"]["budget_time_ms"])
    trajectory_grid_ms = [int(x) for x in config["trajectory_grid_ms"]]

    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    ensure_ts_rust_binary()

    records: list[RunRecord] = []
    payloads: dict[tuple[str, int, str], dict[str, Any]] = {}

    for case in cases:
        if not case.instance.exists():
            raise FileNotFoundError(f"Missing ablation instance: {case.instance}")
        for seed in seeds:
            for algo in ["ts", "ts_rust"]:
                record, payload = _run_single(
                    case=case,
                    algo=algo,
                    seed=seed,
                    budget_time_ms=budget_time_ms,
                    raw_dir=raw_dir,
                )
                records.append(record)
                payloads[(case.name, seed, algo)] = payload

    run_rows = [record.__dict__ for record in records]
    _write_csv(
        out_dir / "runs.csv",
        run_rows,
        [
            "case_name",
            "instance_id",
            "algo",
            "seed",
            "k",
            "beta",
            "budget_time_ms",
            "elapsed_ms",
            "cutsize_best",
            "feasible",
            "nfe",
            "nfe_per_s",
            "status",
            "output_json",
        ],
    )

    pair_rows: list[dict[str, Any]] = []
    trajectory_rows: list[dict[str, Any]] = []

    for case in cases:
        for seed in seeds:
            py_payload = payloads[(case.name, seed, "ts")]
            rs_payload = payloads[(case.name, seed, "ts_rust")]
            target_cut = int(py_payload["cutsize_best"])

            py_nfe = _final_nfe(py_payload)
            rs_nfe = _final_nfe(rs_payload)
            py_elapsed = int(py_payload["elapsed_ms"])
            rs_elapsed = int(rs_payload["elapsed_ms"])
            py_nfe_s = _nfe_per_s(py_nfe, py_elapsed)
            rs_nfe_s = _nfe_per_s(rs_nfe, rs_elapsed)

            pair_rows.append(
                {
                    "case_name": case.name,
                    "seed": seed,
                    "target_rule": "python_final",
                    "target_cut": target_cut,
                    "python_cut": int(py_payload["cutsize_best"]),
                    "rust_cut": int(rs_payload["cutsize_best"]),
                    "rust_minus_python_cut": int(rs_payload["cutsize_best"])
                    - int(py_payload["cutsize_best"]),
                    "python_elapsed_ms": py_elapsed,
                    "rust_elapsed_ms": rs_elapsed,
                    "python_nfe": py_nfe,
                    "rust_nfe": rs_nfe,
                    "python_nfe_per_s": py_nfe_s,
                    "rust_nfe_per_s": rs_nfe_s,
                    "rust_over_python_nfe_per_s": _throughput_ratio(
                        python_nfe_per_s=py_nfe_s,
                        rust_nfe_per_s=rs_nfe_s,
                    ),
                    "python_ttt_ms": _first_time_to_target(
                        py_payload.get("checkpoints", []), target_cut
                    ),
                    "rust_ttt_ms": _first_time_to_target(
                        rs_payload.get("checkpoints", []), target_cut
                    ),
                    "python_feasible": bool(py_payload["feasible"]),
                    "rust_feasible": bool(rs_payload["feasible"]),
                }
            )

            for algo, payload in [("ts", py_payload), ("ts_rust", rs_payload)]:
                for time_ms in trajectory_grid_ms:
                    trajectory_rows.append(
                        {
                            "case_name": case.name,
                            "seed": seed,
                            "algo": algo,
                            "time_ms": time_ms,
                            "cutsize_best_at_time": _cut_at_time(
                                payload.get("checkpoints", []), time_ms
                            ),
                        }
                    )

    _write_csv(
        out_dir / "paired_summary.csv",
        pair_rows,
        [
            "case_name",
            "seed",
            "target_rule",
            "target_cut",
            "python_cut",
            "rust_cut",
            "rust_minus_python_cut",
            "python_elapsed_ms",
            "rust_elapsed_ms",
            "python_nfe",
            "rust_nfe",
            "python_nfe_per_s",
            "rust_nfe_per_s",
            "rust_over_python_nfe_per_s",
            "python_ttt_ms",
            "rust_ttt_ms",
            "python_feasible",
            "rust_feasible",
        ],
    )

    _write_csv(
        out_dir / "trajectory_samples.csv",
        trajectory_rows,
        ["case_name", "seed", "algo", "time_ms", "cutsize_best_at_time"],
    )

    valid_pairs = [
        row for row in pair_rows if row["python_feasible"] is True and row["rust_feasible"] is True
    ]
    rust_better = sum(1 for row in valid_pairs if int(row["rust_minus_python_cut"]) < 0)
    rust_equal = sum(1 for row in valid_pairs if int(row["rust_minus_python_cut"]) == 0)
    rust_worse = sum(1 for row in valid_pairs if int(row["rust_minus_python_cut"]) > 0)

    throughput_ratios = [
        float(row["rust_over_python_nfe_per_s"])
        for row in valid_pairs
        if row["rust_over_python_nfe_per_s"] is not None
        and math.isfinite(float(row["rust_over_python_nfe_per_s"]))
    ]

    report = {
        "schema": "ts-rust-ablation-report-v1",
        "config_path": str(config_path),
        "out_dir": str(out_dir),
        "claim_boundary": config.get("claim_boundary", {}),
        "target_rule": config.get("target_rule", {}),
        "budget_time_ms": budget_time_ms,
        "cases": [case.__dict__ | {"instance": str(case.instance)} for case in cases],
        "seeds": seeds,
        "num_pairs": len(pair_rows),
        "num_valid_pairs": len(valid_pairs),
        "rust_better_pairs": rust_better,
        "rust_equal_pairs": rust_equal,
        "rust_worse_pairs": rust_worse,
        "median_rust_over_python_nfe_per_s": (
            None
            if not throughput_ratios
            else sorted(throughput_ratios)[len(throughput_ratios) // 2]
        ),
        "outputs": {
            "runs_csv": str(out_dir / "runs.csv"),
            "paired_summary_csv": str(out_dir / "paired_summary.csv"),
            "trajectory_samples_csv": str(out_dir / "trajectory_samples.csv"),
        },
    }

    (out_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/ts_rust_ablation_panel.yaml"))
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    report = run_ablation(args.config, args.out_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
