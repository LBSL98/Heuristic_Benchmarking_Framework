#!/usr/bin/env python3
"""Execute and summarize evidence-bearing exception-mining confirmation runs.

This runner consumes a confirmation run plan produced by
``plan_exception_mining_confirmation.py``. It executes solver runs through the
canonical ``hpc_framework.runner.run_one`` function, writes confirmation-specific
raw rows, validates solver artifacts, collapses repeated seeds by a median-quality
rule, and computes confirmation labels plus SBS/VBS/oracle-gap diagnostics.

The script can run a filtered smoke subset or the full Issue #102 matrix. It does
not update monograph claims; those remain pending until mapped in the project
canon.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import traceback
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hpc_framework.runner import run_one

try:
    from jsonschema import Draft7Validator
except Exception:  # pragma: no cover - dependency is available in project env
    Draft7Validator = None


CAMPAIGN_ID = "EXP-MULTILEVEL-EXCEPTION-MINING-001"
DEFAULT_RUN_PLAN = Path(
    "audit_reports/multilevel_exception_mining/confirmation/confirmation_plan_001/"
    "confirmation_run_plan.csv"
)
DEFAULT_OUTPUT_ROOT = Path(
    "audit_reports/multilevel_exception_mining/confirmation/full_confirmation_001"
)
SOLVER_SCHEMA = Path("specs/jsonschema/solver_run.schema.v1.json")

MULTILEVEL_ALGOS = {"metis", "kahip"}
PYTHON_META_ALGOS = {"sa", "ils", "grasp", "ts"}
RUST_META_ALGOS = {"sa_rust", "ils_rust", "grasp_rust", "ts_rust"}
ALL_META_ALGOS = PYTHON_META_ALGOS | RUST_META_ALGOS

NEAR_TIE_THRESHOLD = 0.02
COMPETITIVE_THRESHOLD = 0.10


@dataclass(frozen=True)
class PlanRow:
    """One executable row from the confirmation run plan."""

    campaign_id: str
    confirmation_stage: str
    environment_id: str
    run_id: str
    candidate_id: str
    family: str
    environment_target: str
    variant: str
    priority_label_from_screening: str
    algo_label: str
    algo: str
    seed: int
    budget_ms: int
    bundle_path: Path
    instance_path: Path


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-plan", type=Path, default=DEFAULT_RUN_PLAN)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--only-algo", action="append", default=[])
    parser.add_argument("--only-family", action="append", default=[])
    parser.add_argument("--only-candidate", action="append", default=[])
    parser.add_argument("--only-budget", action="append", type=int, default=[])
    parser.add_argument("--only-seed", action="append", type=int, default=[])
    parser.add_argument(
        "--smoke-first-candidate",
        action="store_true",
        help="After other filters, keep only the first candidate id present in the plan.",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--fail-on-invalid",
        action="store_true",
        help="Exit non-zero when any planned row is invalid after execution.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute confirmation rows and write aggregate outputs."""

    args = build_parser().parse_args(argv)
    output_root = args.output_root.resolve()

    if output_root.exists() and any(output_root.iterdir()) and args.force:
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    plan_rows = read_run_plan(args.run_plan)
    selected = filter_plan_rows(
        plan_rows,
        only_algo=set(args.only_algo),
        only_family=set(args.only_family),
        only_candidate=set(args.only_candidate),
        only_budget=set(args.only_budget),
        only_seed=set(args.only_seed),
        smoke_first_candidate=bool(args.smoke_first_candidate),
        offset=int(args.offset),
        limit=args.limit,
    )

    raw_results = [
        execute_one_confirmation_run(row, output_root, force=bool(args.force)) for row in selected
    ]
    validation_report = build_validation_report(selected, raw_results)
    collapsed = collapse_confirmation_results(raw_results)
    labels = compute_confirmation_labels(collapsed)
    oracle = compute_sbs_vbs_oracle_gap(collapsed)
    per_instance = build_per_instance_summary(labels, collapsed)
    summary = build_summary(selected, raw_results, collapsed, labels, oracle, validation_report)

    write_json(output_root / "confirmation_results.json", raw_results)
    write_csv(output_root / "confirmation_results.csv", raw_results)
    write_json(output_root / "confirmation_validation_report.json", validation_report)
    write_json(output_root / "confirmation_collapsed.json", collapsed)
    write_csv(output_root / "confirmation_collapsed.csv", collapsed)
    write_json(output_root / "confirmation_exception_labels.json", labels)
    write_csv(output_root / "confirmation_exception_labels.csv", labels)
    write_json(output_root / "sbs_vbs_oracle_gap.json", oracle)
    write_csv(output_root / "sbs_vbs_oracle_gap.csv", oracle["oracle_gap_by_algo"])
    write_json(output_root / "per_instance_result_summary.json", per_instance)
    write_csv(output_root / "per_instance_result_summary.csv", per_instance)
    write_json(output_root / "confirmation_summary.json", summary)
    write_summary_md(output_root / "confirmation_summary.md", summary)
    write_invalid_output_report(output_root / "invalid_output_report.md", raw_results)

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))

    if args.fail_on_invalid and int(summary["invalid_result_count"]) > 0:
        return 2
    return 0


def read_run_plan(path: Path) -> list[PlanRow]:
    """Read confirmation run-plan rows."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    return [plan_row_from_csv(row) for row in rows]


def plan_row_from_csv(row: dict[str, str]) -> PlanRow:
    """Convert one CSV row into a typed plan row."""

    return PlanRow(
        campaign_id=row["campaign_id"],
        confirmation_stage=row["confirmation_stage"],
        environment_id=row["environment_id"],
        run_id=row["run_id"],
        candidate_id=row["candidate_id"],
        family=row["family"],
        environment_target=row["environment_target"],
        variant=row["variant"],
        priority_label_from_screening=row["priority_label_from_screening"],
        algo_label=row["algo_label"],
        algo=row["algo"],
        seed=int(row["seed"]),
        budget_ms=int(row["budget_ms"]),
        bundle_path=Path(row["bundle_path"]),
        instance_path=Path(row["instance_path"]),
    )


def filter_plan_rows(
    rows: list[PlanRow],
    *,
    only_algo: set[str],
    only_family: set[str],
    only_candidate: set[str],
    only_budget: set[int],
    only_seed: set[int],
    smoke_first_candidate: bool,
    offset: int,
    limit: int | None,
) -> list[PlanRow]:
    """Apply deterministic execution filters."""

    selected = [
        row
        for row in rows
        if (not only_algo or row.algo in only_algo or row.algo_label in only_algo)
        and (not only_family or row.family in only_family)
        and (not only_candidate or row.candidate_id in only_candidate)
        and (not only_budget or row.budget_ms in only_budget)
        and (not only_seed or row.seed in only_seed)
    ]

    if smoke_first_candidate and selected:
        first_candidate = selected[0].candidate_id
        selected = [row for row in selected if row.candidate_id == first_candidate]

    if offset < 0:
        raise ValueError("offset must be non-negative")
    selected = selected[offset:]

    if limit is not None:
        if limit < 0:
            raise ValueError("limit must be non-negative")
        selected = selected[:limit]

    return selected


def execute_one_confirmation_run(row: PlanRow, output_root: Path, *, force: bool) -> dict[str, Any]:
    """Execute or resume one confirmation run."""

    artifact_dir = output_root / "solver_artifacts" / row.family / row.candidate_id / row.run_id
    artifact_dir.mkdir(parents=True, exist_ok=True)

    out_json = artifact_dir / "result.json"
    workdir = artifact_dir / "workdir"
    row_json = artifact_dir / "confirmation_row.json"

    if row_json.exists() and out_json.exists() and not force:
        return read_json_object(row_json)

    base = base_confirmation_row(row, artifact_dir, out_json, workdir)

    try:
        run_one(
            instance_path=row.instance_path,
            algo=row.algo,
            k=2,
            beta=0.03,
            seed=row.seed,
            budget_time_ms=row.budget_ms,
            out_json=out_json,
            workdir=workdir,
            kahip_preset="fast",
            log_level="info",
        )
        artifact = read_json_object(out_json)
        normalized = normalize_confirmation_artifact(base, artifact)
        write_json(row_json, normalized)
        return normalized
    except Exception as exc:  # noqa: BLE001
        error_path = artifact_dir / "error.txt"
        error_path.write_text(
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            encoding="utf-8",
        )
        failed = base | {
            "status": "error",
            "valid": False,
            "feasible": False,
            "schema_valid": False,
            "schema_error_count": "",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "error_traceback": str(error_path),
        }
        write_json(row_json, failed)
        return failed


def base_confirmation_row(
    row: PlanRow, artifact_dir: Path, out_json: Path, workdir: Path
) -> dict[str, Any]:
    """Build the common row fields for confirmation outputs."""

    return {
        "campaign_id": CAMPAIGN_ID,
        "confirmation_stage": "full_portfolio_confirmation",
        "environment_id": row.environment_id,
        "run_id": row.run_id,
        "candidate_id": row.candidate_id,
        "family": row.family,
        "environment_target": row.environment_target,
        "variant": row.variant,
        "priority_label_from_screening": row.priority_label_from_screening,
        "algo_label": row.algo_label,
        "algo": row.algo,
        "seed": row.seed,
        "budget_ms": row.budget_ms,
        "bundle_path": str(row.bundle_path),
        "instance_path": str(row.instance_path),
        "artifact_dir": str(artifact_dir),
        "artifact_json": str(out_json),
        "workdir": str(workdir),
        "status": "unknown",
        "valid": False,
        "feasible": False,
        "schema_valid": False,
        "schema_error_count": "",
        "cutsize": "",
        "elapsed_ms": "",
        "available_by_budget": False,
        "timeout": False,
        "returncode": "",
        "error_type": "",
        "error_message": "",
        "monograph_claim_status": "pending_mapping_until_canon_update",
        "claim_boundary": "confirmation_row_requires_aggregate_validation_before_monograph_use",
    }


def normalize_confirmation_artifact(
    base: dict[str, Any], artifact: dict[str, Any]
) -> dict[str, Any]:
    """Normalize one solver artifact into one confirmation row."""

    status = str(artifact.get("status", "unknown"))
    feasible = bool(artifact.get("feasible", False))
    cutsize_raw = artifact.get("cutsize_best", artifact.get("cutsize", ""))
    elapsed_raw = artifact.get("elapsed_ms", "")
    metrics_obj = artifact.get("metrics", {})
    metrics: dict[str, Any] = metrics_obj if isinstance(metrics_obj, dict) else {}

    schema_report = validate_solver_artifact(artifact)
    valid_cut = isinstance(cutsize_raw, int | float) and not isinstance(cutsize_raw, bool)
    valid_elapsed = isinstance(elapsed_raw, int | float) and not isinstance(elapsed_raw, bool)
    valid = (
        status in {"ok", "timeout"}
        and feasible
        and valid_cut
        and valid_elapsed
        and bool(schema_report["valid"])
    )

    cutsize: int | str = int(cutsize_raw) if valid_cut else ""
    elapsed_ms: int | str = int(elapsed_raw) if valid_elapsed else ""
    available_by_budget = bool(
        valid and isinstance(elapsed_ms, int) and elapsed_ms <= int(base["budget_ms"])
    )

    return base | {
        "status": status,
        "valid": valid,
        "feasible": feasible,
        "schema_valid": bool(schema_report["valid"]),
        "schema_error_count": int(schema_report["error_count"]),
        "schema_errors": "; ".join(str(item) for item in schema_report["errors"][:5]),
        "cutsize": cutsize,
        "elapsed_ms": elapsed_ms,
        "available_by_budget": available_by_budget,
        "timeout": status == "timeout",
        "returncode": artifact.get("returncode", ""),
        "k": artifact.get("k", ""),
        "beta": artifact.get("beta", ""),
        "epsilon": artifact.get(
            "epsilon",
            metrics.get("balance_tolerance", artifact.get("beta", "")),
        ),
        "n": artifact.get("n", metrics.get("n_nodes", metrics.get("n", ""))),
        "m": artifact.get("m", metrics.get("n_edges", metrics.get("m", ""))),
        "checkpoint_count": len(artifact.get("checkpoints", []) or []),
        "raw_status": status,
    }


def validate_solver_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate the solver artifact against the project schema when available."""

    if Draft7Validator is None or not SOLVER_SCHEMA.exists():
        return {
            "valid": True,
            "error_count": 0,
            "errors": [],
            "schema_path": str(SOLVER_SCHEMA),
            "validation_mode": "schema_unavailable_skipped",
        }

    schema = read_json_object(SOLVER_SCHEMA)
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(artifact), key=lambda err: list(err.path))
    return {
        "valid": not errors,
        "error_count": len(errors),
        "errors": [error.message for error in errors[:20]],
        "schema_path": str(SOLVER_SCHEMA),
        "validation_mode": "jsonschema_draft7",
    }


def collapse_confirmation_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse repeated seeds at candidate/algo/budget by median quality."""

    grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        grouped[(str(row["candidate_id"]), str(row["algo"]), int(row["budget_ms"]))].append(row)

    collapsed: list[dict[str, Any]] = []
    for (candidate_id, algo, budget_ms), group in sorted(grouped.items()):
        valid_rows = [row for row in group if bool(row.get("valid"))]
        available_rows = [row for row in valid_rows if bool(row.get("available_by_budget"))]
        ordered = sorted(
            available_rows,
            key=lambda row: (int(row["cutsize"]), int(row["elapsed_ms"]), int(row["seed"])),
        )
        median = ordered[(len(ordered) - 1) // 2] if ordered else None
        best = ordered[0] if ordered else None
        first = group[0]

        collapsed.append(
            {
                "campaign_id": CAMPAIGN_ID,
                "confirmation_stage": "full_portfolio_confirmation_collapsed",
                "environment_id": first["environment_id"],
                "candidate_id": candidate_id,
                "family": first["family"],
                "environment_target": first["environment_target"],
                "variant": first["variant"],
                "priority_label_from_screening": first["priority_label_from_screening"],
                "algo_label": first["algo_label"],
                "algo": algo,
                "budget_ms": budget_ms,
                "attempt_count": len(group),
                "valid_count": len(valid_rows),
                "available_count": len(available_rows),
                "invalid_count": len(group) - len(valid_rows),
                "median_valid_cut_by_budget": "" if median is None else int(median["cutsize"]),
                "median_elapsed_ms": "" if median is None else int(median["elapsed_ms"]),
                "median_seed": "" if median is None else int(median["seed"]),
                "best_valid_cut_by_budget": "" if best is None else int(best["cutsize"]),
                "best_elapsed_ms": "" if best is None else int(best["elapsed_ms"]),
                "best_seed": "" if best is None else int(best["seed"]),
                "available_by_budget": median is not None,
                "status_set": ";".join(sorted({str(row.get("status", "")) for row in group})),
                "collapse_rule": "median_quality_cut_then_elapsed_then_seed",
            }
        )

    return collapsed


def compute_confirmation_labels(collapsed: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute confirmation labels and separated metaheuristic categories."""

    by_slice: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in collapsed:
        by_slice[(str(row["candidate_id"]), int(row["budget_ms"]))].append(row)

    labels: list[dict[str, Any]] = []
    for (candidate_id, budget_ms), rows in sorted(by_slice.items()):
        first = rows[0]
        available = [row for row in rows if bool(row["available_by_budget"])]

        best_multilevel = best_group(available, MULTILEVEL_ALGOS)
        best_meta_python = best_group(available, PYTHON_META_ALGOS)
        best_meta_rust = best_group(available, RUST_META_ALGOS)
        best_meta_all = best_group(available, ALL_META_ALGOS)

        best_multilevel_cut = cut_or_none(best_multilevel)
        best_meta_all_cut = cut_or_none(best_meta_all)

        if best_multilevel_cut is None or best_meta_all_cut is None:
            label = "insufficient_participants"
            gap: float | str = ""
        else:
            gap_value = (best_meta_all_cut - best_multilevel_cut) / max(1, best_multilevel_cut)
            gap = gap_value
            if best_meta_all_cut < best_multilevel_cut:
                label = "strong_exception_confirmed"
            elif gap_value <= NEAR_TIE_THRESHOLD:
                label = "near_tie_confirmed"
            elif gap_value <= COMPETITIVE_THRESHOLD:
                label = "competitive_confirmed"
            else:
                label = "non_exception_confirmed"

        labels.append(
            {
                "campaign_id": CAMPAIGN_ID,
                "confirmation_stage": "full_portfolio_confirmation_labels",
                "environment_id": first["environment_id"],
                "candidate_id": candidate_id,
                "family": first["family"],
                "environment_target": first["environment_target"],
                "variant": first["variant"],
                "budget_ms": budget_ms,
                "best_multilevel_algo": "" if best_multilevel is None else best_multilevel["algo"],
                "best_multilevel_cut": "" if best_multilevel_cut is None else best_multilevel_cut,
                "best_meta_python_algo": (
                    "" if best_meta_python is None else best_meta_python["algo"]
                ),
                "best_meta_python_cut": (
                    ""
                    if best_meta_python is None
                    else int(best_meta_python["median_valid_cut_by_budget"])
                ),
                "best_meta_rust_algo": "" if best_meta_rust is None else best_meta_rust["algo"],
                "best_meta_rust_cut": (
                    ""
                    if best_meta_rust is None
                    else int(best_meta_rust["median_valid_cut_by_budget"])
                ),
                "best_meta_all_algo": "" if best_meta_all is None else best_meta_all["algo"],
                "best_meta_all_cut": "" if best_meta_all_cut is None else best_meta_all_cut,
                "relative_gap_meta_all_vs_multilevel": gap,
                "confirmation_exception_label": label,
                "label_claim_status": "confirmation_evidence_pending_canon_mapping",
            }
        )

    return labels


def best_group(rows: list[dict[str, Any]], algos: set[str]) -> dict[str, Any] | None:
    """Return the best collapsed row among a group of algorithms."""

    eligible = [
        row
        for row in rows
        if row["algo"] in algos and row.get("median_valid_cut_by_budget") not in ("", None)
    ]
    if not eligible:
        return None
    return min(
        eligible,
        key=lambda row: (
            int(row["median_valid_cut_by_budget"]),
            int(row["median_elapsed_ms"]),
            str(row["algo"]),
        ),
    )


def cut_or_none(row: dict[str, Any] | None) -> int | None:
    """Read a median cut value or return None."""

    if row is None:
        return None
    value = row.get("median_valid_cut_by_budget")
    if value in ("", None):
        return None
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        return None
    return int(value)


def compute_sbs_vbs_oracle_gap(collapsed: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute SBS, VBS, and oracle-gap diagnostics from collapsed rows."""

    by_slice: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in collapsed:
        if bool(row.get("available_by_budget")):
            by_slice[(str(row["candidate_id"]), int(row["budget_ms"]))].append(row)

    slice_best: dict[tuple[str, int], int] = {}
    algo_values: dict[str, list[int]] = defaultdict(list)

    for key, rows in by_slice.items():
        cuts = [int(row["median_valid_cut_by_budget"]) for row in rows]
        if not cuts:
            continue
        slice_best[key] = min(cuts)
        for row in rows:
            algo_values[str(row["algo"])].append(int(row["median_valid_cut_by_budget"]))

    vbs_mean = mean_ints(slice_best.values())
    oracle_rows: list[dict[str, Any]] = []
    for algo, values in sorted(algo_values.items()):
        algo_mean = mean_ints(values)
        gap = (
            ""
            if vbs_mean is None or algo_mean is None
            else (algo_mean - vbs_mean) / max(1.0, vbs_mean)
        )
        oracle_rows.append(
            {
                "campaign_id": CAMPAIGN_ID,
                "diagnostic": "sbs_vbs_oracle_gap",
                "algo": algo,
                "available_slice_count": len(values),
                "mean_median_cut": "" if algo_mean is None else algo_mean,
                "vbs_mean_median_cut": "" if vbs_mean is None else vbs_mean,
                "oracle_gap_vs_vbs": gap,
            }
        )

    sbs = min(
        oracle_rows,
        key=lambda row: (
            float(row["mean_median_cut"]) if row["mean_median_cut"] != "" else float("inf")
        ),
        default=None,
    )

    return {
        "campaign_id": CAMPAIGN_ID,
        "diagnostic": "sbs_vbs_oracle_gap",
        "slice_count": len(slice_best),
        "vbs_mean_median_cut": "" if vbs_mean is None else vbs_mean,
        "sbs_algo": "" if sbs is None else sbs["algo"],
        "sbs_mean_median_cut": "" if sbs is None else sbs["mean_median_cut"],
        "oracle_gap_by_algo": oracle_rows,
        "claim_boundary": "diagnostic_pending_canon_mapping",
    }


def build_per_instance_summary(
    labels: list[dict[str, Any]],
    collapsed: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Summarize confirmation labels by candidate instance."""

    collapsed_by_candidate = Counter(str(row["candidate_id"]) for row in collapsed)
    label_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in labels:
        label_rows[str(row["candidate_id"])].append(row)

    summaries: list[dict[str, Any]] = []
    for candidate_id, rows in sorted(label_rows.items()):
        first = rows[0]
        label_counts = Counter(str(row["confirmation_exception_label"]) for row in rows)
        summaries.append(
            {
                "campaign_id": CAMPAIGN_ID,
                "confirmation_stage": "per_instance_result_summary",
                "environment_id": first["environment_id"],
                "candidate_id": candidate_id,
                "family": first["family"],
                "environment_target": first["environment_target"],
                "variant": first["variant"],
                "budget_label_row_count": len(rows),
                "collapsed_algo_budget_row_count": collapsed_by_candidate[candidate_id],
                "label_counts": json.dumps(dict(label_counts), sort_keys=True),
                "strong_exception_confirmed_count": label_counts.get(
                    "strong_exception_confirmed", 0
                ),
                "near_tie_confirmed_count": label_counts.get("near_tie_confirmed", 0),
                "competitive_confirmed_count": label_counts.get("competitive_confirmed", 0),
                "non_exception_confirmed_count": label_counts.get("non_exception_confirmed", 0),
                "insufficient_participants_count": label_counts.get("insufficient_participants", 0),
            }
        )

    return summaries


def build_validation_report(
    selected: list[PlanRow],
    raw_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build validation report for executed confirmation rows."""

    invalid = [row for row in raw_results if not bool(row.get("valid"))]
    missing_artifacts = [
        row["run_id"]
        for row in raw_results
        if row.get("artifact_json") and not Path(str(row["artifact_json"])).exists()
    ]
    return {
        "campaign_id": CAMPAIGN_ID,
        "confirmation_stage": "full_portfolio_confirmation_validation",
        "planned_run_count": len(selected),
        "raw_result_count": len(raw_results),
        "valid_result_count": len(raw_results) - len(invalid),
        "invalid_result_count": len(invalid),
        "missing_artifact_count": len(missing_artifacts),
        "missing_artifacts": missing_artifacts,
        "invalid_rows": [
            {
                "run_id": row.get("run_id"),
                "algo": row.get("algo"),
                "status": row.get("status"),
                "error_type": row.get("error_type"),
                "error_message": row.get("error_message"),
            }
            for row in invalid[:200]
        ],
        "schema_error_count_total": sum(
            int(row.get("schema_error_count") or 0)
            for row in raw_results
            if str(row.get("schema_error_count", "")).isdigit()
        ),
        "claim_boundary": "validation_report_required_before_evidence_use",
    }


def build_summary(
    selected: list[PlanRow],
    raw_results: list[dict[str, Any]],
    collapsed: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    oracle: dict[str, Any],
    validation_report: dict[str, Any],
) -> dict[str, Any]:
    """Build the top-level confirmation summary."""

    valid = [row for row in raw_results if bool(row.get("valid"))]
    invalid = [row for row in raw_results if not bool(row.get("valid"))]
    environment_ids = sorted({row.environment_id for row in selected})
    label_counts = Counter(str(row["confirmation_exception_label"]) for row in labels)

    return {
        "campaign_id": CAMPAIGN_ID,
        "issue": 102,
        "classification": "full_portfolio_confirmation",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "environment_ids": environment_ids,
        "environment_pooling_status": "forbidden_single_environment_or_explicit_slice_only",
        "monograph_claim_status": "pending_mapping_until_canon_update",
        "planned_run_count": len(selected),
        "raw_result_count": len(raw_results),
        "valid_result_count": len(valid),
        "invalid_result_count": len(invalid),
        "collapsed_row_count": len(collapsed),
        "label_row_count": len(labels),
        "candidate_count": len({row.candidate_id for row in selected}),
        "algorithm_count": len({row.algo for row in selected}),
        "budget_count": len({row.budget_ms for row in selected}),
        "seed_count": len({row.seed for row in selected}),
        "algorithms": sorted({row.algo for row in selected}),
        "budgets_ms": sorted({row.budget_ms for row in selected}),
        "seeds": sorted({row.seed for row in selected}),
        "raw_status_counts": dict(Counter(str(row.get("status", "")) for row in raw_results)),
        "valid_by_algo": dict(Counter(str(row["algo"]) for row in valid)),
        "invalid_by_algo": dict(Counter(str(row["algo"]) for row in invalid)),
        "confirmation_label_counts": dict(label_counts),
        "strong_exception_confirmed_count": label_counts.get("strong_exception_confirmed", 0),
        "near_tie_confirmed_count": label_counts.get("near_tie_confirmed", 0),
        "competitive_confirmed_count": label_counts.get("competitive_confirmed", 0),
        "non_exception_confirmed_count": label_counts.get("non_exception_confirmed", 0),
        "insufficient_participants_count": label_counts.get("insufficient_participants", 0),
        "sbs_algo": oracle.get("sbs_algo", ""),
        "vbs_mean_median_cut": oracle.get("vbs_mean_median_cut", ""),
        "validation": validation_report,
        "claim_boundary": (
            "Confirmation outputs are evidence-bearing only for this explicit environment slice "
            "after validation. Monograph claims remain pending until canon mapping."
        ),
    }


def mean_ints(values: Iterable[int]) -> float | None:
    """Return arithmetic mean for integer values."""

    data = list(values)
    if not data:
        return None
    return float(sum(data)) / float(len(data))


def read_json_object(path: Path) -> dict[str, Any]:
    """Read a JSON object."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    """Write JSON with deterministic formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write CSV rows."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    """Write a compact Markdown confirmation summary."""

    lines = [
        "# Confirmation summary",
        "",
        f"- Campaign: `{summary['campaign_id']}`",
        f"- Issue: `#{summary['issue']}`",
        f"- Classification: `{summary['classification']}`",
        f"- Environment ids: `{', '.join(summary['environment_ids'])}`",
        f"- Planned runs: `{summary['planned_run_count']}`",
        f"- Valid results: `{summary['valid_result_count']}`",
        f"- Invalid results: `{summary['invalid_result_count']}`",
        f"- Collapsed rows: `{summary['collapsed_row_count']}`",
        f"- Label rows: `{summary['label_row_count']}`",
        f"- Label counts: `{summary['confirmation_label_counts']}`",
        f"- SBS algo: `{summary['sbs_algo']}`",
        "",
        "## Claim boundary",
        "",
        summary["claim_boundary"],
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_invalid_output_report(path: Path, raw_results: list[dict[str, Any]]) -> None:
    """Write invalid output report."""

    invalid = [row for row in raw_results if not bool(row.get("valid"))]
    lines = [
        "# Invalid confirmation output report",
        "",
        f"- Invalid rows: `{len(invalid)}`",
        "",
    ]
    if invalid:
        for row in invalid:
            lines.append(
                f"- `{row.get('run_id')}`: `{row.get('status')}` "
                f"`{row.get('error_type')}` {row.get('error_message')}"
            )
    else:
        lines.append("No invalid confirmation outputs were observed.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
