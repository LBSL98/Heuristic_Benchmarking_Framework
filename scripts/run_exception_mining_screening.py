#!/usr/bin/env python3
"""Run exploratory exception-mining screening on generated candidate bundles."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import traceback
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hpc_framework.runner import run_one

CAMPAIGN_ID = "EXP-MULTILEVEL-EXCEPTION-MINING-001"
DEFAULT_POOL_MANIFEST = Path(
    "audit_reports/multilevel_exception_mining/candidate_pool/exploratory_pool_001/"
    "generated_instances_manifest.json"
)
DEFAULT_OUTPUT_ROOT = Path(
    "audit_reports/multilevel_exception_mining/screening/exploratory_screening_001"
)

SCREENING_ALGOS = (
    "metis",
    "kahip",
    "sa",
    "ils",
    "grasp",
    "ts",
    "sa_rust",
    "ils_rust",
    "grasp_rust",
    "ts_rust",
)
SCREENING_BUDGETS_MS = (1000, 5000)
SCREENING_SEEDS = (42,)

NEAR_TIE_THRESHOLD = 0.01
COMPETITIVE_THRESHOLD = 0.05


@dataclass(frozen=True)
class ScreeningRunSpec:
    """One exploratory screening run specification."""

    candidate_id: str
    family: str
    environment_target: str
    variant: str
    bundle_path: Path
    instance_path: Path
    algo: str
    seed: int
    budget_ms: int


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Run issue #100 exploratory screening over accepted non-holdout "
            "exception-mining candidates. Results are exploratory only."
        )
    )
    parser.add_argument(
        "--pool-manifest",
        type=Path,
        default=DEFAULT_POOL_MANIFEST,
        help="Path to generated_instances_manifest.json from issue #99.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where screening results and artifacts will be written.",
    )
    parser.add_argument(
        "--profile",
        choices=["issue100", "smoke"],
        default="issue100",
        help="Execution profile. smoke runs a tiny subset for tests.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacing an existing output directory.",
    )
    parser.add_argument(
        "--include-server-expanded",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include server_expanded candidates in exploratory screening.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run exploratory screening."""

    args = build_parser().parse_args(argv)

    pool_manifest = args.pool_manifest.resolve()
    output_root = args.output_root.resolve()

    if output_root.exists() and any(output_root.iterdir()) and not args.force:
        raise SystemExit(f"output root already exists and is not empty: {output_root}")

    if output_root.exists() and args.force:
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "solver_artifacts").mkdir(exist_ok=True)
    (output_root / "run_logs").mkdir(exist_ok=True)

    pool_rows = read_json_list(pool_manifest)
    scope = build_screening_scope(
        pool_rows,
        profile=args.profile,
        include_server_expanded=args.include_server_expanded,
    )
    write_json(output_root / "screening_scope_manifest.json", scope)

    specs = build_run_specs(scope["screened_candidates"], args.profile)
    write_json(output_root / "screening_run_plan.json", [run_spec_to_json(spec) for spec in specs])

    results: list[dict[str, Any]] = []
    run_attempts_path = output_root / "screening_run_attempts.jsonl"

    for spec in specs:
        write_jsonl(run_attempts_path, run_event(spec, "attempt_started"))
        result = execute_one_screening_run(spec, output_root)
        results.append(result)
        write_jsonl(
            run_attempts_path,
            run_event(
                spec,
                "attempt_finished",
                status=result["status"],
                valid=result["valid"],
                returncode=result.get("returncode", ""),
                artifact_json=result.get("artifact_json", ""),
            ),
        )

    write_json(output_root / "screening_raw_results.json", results)
    write_csv(output_root / "screening_results.csv", results)

    collapsed = collapse_quality_by_budget(results)
    write_json(output_root / "screening_results.json", collapsed)
    write_csv(output_root / "screening_results_collapsed.csv", collapsed)

    labels = compute_exception_labels(collapsed)
    write_json(output_root / "preliminary_exception_labels.json", labels)
    write_csv(output_root / "preliminary_exception_labels.csv", labels)

    write_invalid_output_report(output_root / "invalid_output_report.md", results)
    write_solver_artifact_inventory(output_root / "solver_artifact_inventory.json", results)
    write_solver_artifact_inventory_md(output_root / "solver_artifact_inventory.md", results)

    summary = build_summary(scope, specs, results, collapsed, labels)
    write_json(output_root / "screening_summary.json", summary)
    write_summary_md(output_root / "screening_summary.md", summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_screening_scope(
    pool_rows: list[dict[str, Any]],
    *,
    profile: str,
    include_server_expanded: bool,
) -> dict[str, Any]:
    """Build screening scope while preserving holdout."""

    accepted = [row for row in pool_rows if bool(row.get("accepted"))]
    holdout = [row for row in accepted if row.get("environment_target") == "holdout"]

    eligible_targets = {"common"}
    if include_server_expanded:
        eligible_targets.add("server_expanded")

    screened = [
        row
        for row in accepted
        if row.get("environment_target") in eligible_targets
        and row.get("lifecycle_state") != "holdout_reserved"
    ]

    if profile == "smoke":
        screened = [
            row
            for row in screened
            if row.get("family") in {"F01", "F02"}
            and row.get("variant") in {"common_a", "common_b"}
        ]

    non_screened = []
    for row in accepted:
        reason = ""
        if row.get("environment_target") == "holdout":
            reason = "holdout_reserved_by_protocol"
        elif row not in screened:
            reason = "not_in_smoke_subset" if profile == "smoke" else "outside_screening_scope"

        if reason:
            non_screened.append(scope_row(row, reason=reason))

    return {
        "campaign_id": CAMPAIGN_ID,
        "created_at_utc": utc_now(),
        "profile": profile,
        "screening_classification": "exploratory_non_confirmatory",
        "holdout_policy": "holdout_reserved_candidates_are_not_screened_in_issue100",
        "accepted_count": len(accepted),
        "screened_count": len(screened),
        "non_screened_count": len(non_screened),
        "screened_by_environment_target": dict(
            Counter(row["environment_target"] for row in screened)
        ),
        "non_screened_by_reason": dict(
            Counter(row["non_screening_reason"] for row in non_screened)
        ),
        "screened_candidates": [scope_row(row, reason="screened") for row in screened],
        "non_screened_candidates": non_screened,
        "holdout_reserved_count": len(holdout),
    }


def scope_row(row: dict[str, Any], *, reason: str) -> dict[str, Any]:
    """Return candidate scope row."""

    return {
        "campaign_id": row.get("campaign_id", CAMPAIGN_ID),
        "candidate_id": row["candidate_id"],
        "family": row["family"],
        "environment_target": row["environment_target"],
        "variant": row["variant"],
        "bundle_path": row["bundle_path"],
        "instance_path": str(Path(row["bundle_path"]) / "instance.json.gz"),
        "lifecycle_state": row.get("lifecycle_state", ""),
        "pool_role": row.get("pool_role", ""),
        "screening_scope": reason == "screened",
        "non_screening_reason": "" if reason == "screened" else reason,
    }


def build_run_specs(
    screened_candidates: list[dict[str, Any]], profile: str
) -> list[ScreeningRunSpec]:
    """Build deterministic screening run specs."""

    algos: tuple[str, ...]
    budgets: tuple[int, ...]
    if profile == "smoke":
        algos = ("metis", "sa")
        budgets = (1000,)
    else:
        algos = SCREENING_ALGOS
        budgets = SCREENING_BUDGETS_MS

    specs: list[ScreeningRunSpec] = []
    for candidate in screened_candidates:
        for budget_ms in budgets:
            for algo in algos:
                for seed in SCREENING_SEEDS:
                    specs.append(
                        ScreeningRunSpec(
                            candidate_id=str(candidate["candidate_id"]),
                            family=str(candidate["family"]),
                            environment_target=str(candidate["environment_target"]),
                            variant=str(candidate["variant"]),
                            bundle_path=Path(str(candidate["bundle_path"])),
                            instance_path=Path(str(candidate["instance_path"])),
                            algo=algo,
                            seed=int(seed),
                            budget_ms=int(budget_ms),
                        )
                    )

    return specs


def execute_one_screening_run(spec: ScreeningRunSpec, output_root: Path) -> dict[str, Any]:
    """Execute one solver run and normalize the artifact into a screening row."""

    run_id = f"{spec.candidate_id}__{spec.algo}__seed{spec.seed}__budget{spec.budget_ms}"
    artifacts_dir = output_root / "solver_artifacts" / spec.family / spec.candidate_id / run_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    out_json = artifacts_dir / "result.json"
    workdir = artifacts_dir / "workdir"

    base = {
        "campaign_id": CAMPAIGN_ID,
        "screening_stage": "exploratory_non_confirmatory",
        "run_id": run_id,
        "candidate_id": spec.candidate_id,
        "family": spec.family,
        "environment_target": spec.environment_target,
        "variant": spec.variant,
        "bundle_path": str(spec.bundle_path),
        "instance_path": str(spec.instance_path),
        "algo": spec.algo,
        "seed": spec.seed,
        "budget_ms": spec.budget_ms,
        "artifact_dir": str(artifacts_dir),
        "artifact_json": str(out_json),
        "workdir": str(workdir),
        "status": "unknown",
        "valid": False,
        "feasible": False,
        "cutsize": "",
        "elapsed_ms": "",
        "available_by_budget": False,
        "timeout": False,
        "returncode": "",
        "error_type": "",
        "error_message": "",
    }

    try:
        run_one(
            instance_path=spec.instance_path,
            algo=spec.algo,
            k=2,
            beta=0.03,
            seed=spec.seed,
            budget_time_ms=spec.budget_ms,
            out_json=out_json,
            workdir=workdir,
            kahip_preset="fast",
            log_level="info",
        )
        artifact = read_json_object(out_json)
        normalized = normalize_successful_artifact(base, artifact)
        write_json(artifacts_dir / "screening_row.json", normalized)
        return normalized

    except Exception as exc:  # noqa: BLE001
        error_path = artifacts_dir / "error.txt"
        error_path.write_text(
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            encoding="utf-8",
        )
        failed = base | {
            "status": "error",
            "valid": False,
            "feasible": False,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "error_traceback": str(error_path),
        }
        write_json(artifacts_dir / "screening_row.json", failed)
        return failed


def normalize_successful_artifact(base: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    """Normalize runner artifact fields into one screening row.

    Runner artifacts in the current contract serialize the final/best cut as
    ``cutsize_best``. The screening table keeps the normalized column named
    ``cutsize`` because downstream collapse code consumes that internal name.
    """

    status = str(artifact.get("status", "unknown"))
    feasible = bool(artifact.get("feasible", False))
    cutsize_raw = artifact.get("cutsize_best", artifact.get("cutsize", ""))
    elapsed_raw = artifact.get("elapsed_ms", "")

    metrics_obj = artifact.get("metrics", {})
    metrics: dict[str, Any] = metrics_obj if isinstance(metrics_obj, dict) else {}

    valid_cut = isinstance(cutsize_raw, int | float) and not isinstance(cutsize_raw, bool)
    valid_elapsed = isinstance(elapsed_raw, int | float) and not isinstance(elapsed_raw, bool)
    valid = status in {"ok", "timeout"} and feasible and valid_cut and valid_elapsed

    cutsize: int | str = int(cutsize_raw) if valid_cut else ""
    elapsed_ms: int | str = int(elapsed_raw) if valid_elapsed else ""
    available_by_budget = bool(
        valid and isinstance(elapsed_ms, int) and elapsed_ms <= int(base["budget_ms"])
    )

    return base | {
        "status": status,
        "valid": valid,
        "feasible": feasible,
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


def collapse_quality_by_budget(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse raw run rows into quality-by-budget rows.

    Screening uses one seed by protocol. This function still uses a grouped collapse so the
    same shape can later support repeated confirmation.
    """

    grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        grouped[(str(row["candidate_id"]), str(row["algo"]), int(row["budget_ms"]))].append(row)

    collapsed: list[dict[str, Any]] = []
    for (candidate_id, algo, budget_ms), group in sorted(grouped.items()):
        valid_rows = [row for row in group if bool(row.get("valid"))]
        available_rows = [row for row in valid_rows if bool(row.get("available_by_budget"))]

        source_rows = available_rows
        best = min(source_rows, key=lambda row: int(row["cutsize"])) if source_rows else None

        first = group[0]
        collapsed.append(
            {
                "campaign_id": CAMPAIGN_ID,
                "screening_stage": "exploratory_non_confirmatory",
                "candidate_id": candidate_id,
                "family": first["family"],
                "environment_target": first["environment_target"],
                "variant": first["variant"],
                "algo": algo,
                "budget_ms": budget_ms,
                "attempt_count": len(group),
                "valid_count": len(valid_rows),
                "available_count": len(available_rows),
                "invalid_count": len(group) - len(valid_rows),
                "best_valid_cut_by_budget": "" if best is None else int(best["cutsize"]),
                "best_elapsed_ms": "" if best is None else int(best["elapsed_ms"]),
                "available_by_budget": best is not None,
                "status_set": sorted({str(row.get("status", "")) for row in group}),
            }
        )

    return collapsed


def compute_exception_labels(collapsed: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute preliminary diagnostic labels against the multilevel reference."""

    by_slice: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in collapsed:
        by_slice[(str(row["candidate_id"]), int(row["budget_ms"]))].append(row)

    labels: list[dict[str, Any]] = []
    for (candidate_id, budget_ms), rows in sorted(by_slice.items()):
        first = rows[0]
        available = [row for row in rows if bool(row["available_by_budget"])]
        multilevel = [row for row in available if row["algo"] in {"metis", "kahip"}]
        meta = [row for row in available if row["algo"] not in {"metis", "kahip"}]

        best_multilevel = min(
            (int(row["best_valid_cut_by_budget"]) for row in multilevel),
            default=None,
        )
        best_meta = min((int(row["best_valid_cut_by_budget"]) for row in meta), default=None)
        best_meta_algo = ""
        if best_meta is not None:
            best_meta_rows = [
                row for row in meta if int(row["best_valid_cut_by_budget"]) == best_meta
            ]
            best_meta_algo = sorted(str(row["algo"]) for row in best_meta_rows)[0]

        gap: float | str = ""
        if best_multilevel is None and best_meta is not None:
            label = "availability_only_candidate"
        elif best_multilevel is None and best_meta is None:
            label = "no_available_solution"
        elif best_meta is None:
            label = "non_exception"
        else:
            assert best_multilevel is not None
            assert best_meta is not None
            best_multilevel_value: int = best_multilevel
            best_meta_value: int = best_meta
            gap_value = (best_meta_value - best_multilevel_value) / max(1, best_multilevel_value)
            gap = gap_value
            if best_meta_value < best_multilevel_value:
                label = "strong_exception_candidate"
            elif gap_value <= NEAR_TIE_THRESHOLD:
                label = "near_tie_candidate"
            elif gap_value <= COMPETITIVE_THRESHOLD:
                label = "competitive_candidate"
            else:
                label = "non_exception"

        labels.append(
            {
                "campaign_id": CAMPAIGN_ID,
                "screening_stage": "exploratory_non_confirmatory",
                "candidate_id": candidate_id,
                "family": first["family"],
                "environment_target": first["environment_target"],
                "variant": first["variant"],
                "budget_ms": budget_ms,
                "best_multilevel_cut": "" if best_multilevel is None else best_multilevel,
                "best_meta_cut": "" if best_meta is None else best_meta,
                "best_meta_algo": best_meta_algo,
                "relative_gap_meta_vs_multilevel": gap,
                "preliminary_exception_label": label,
                "label_claim_status": "hypothesis_for_confirmation_only",
            }
        )

    return labels


def build_summary(
    scope: dict[str, Any],
    specs: list[ScreeningRunSpec],
    results: list[dict[str, Any]],
    collapsed: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build screening summary."""

    valid = [row for row in results if bool(row.get("valid"))]
    invalid = [row for row in results if not bool(row.get("valid"))]

    return {
        "campaign_id": CAMPAIGN_ID,
        "created_at_utc": utc_now(),
        "classification": "exploratory_non_confirmatory",
        "monograph_claim_status": "not_evidence_bearing",
        "cart_asp_claim_status": "not_allowed_from_screening",
        "autotuning_status": "not_used",
        "screened_candidate_count": scope["screened_count"],
        "non_screened_candidate_count": scope["non_screened_count"],
        "holdout_reserved_count": scope["holdout_reserved_count"],
        "screened_by_environment_target": scope["screened_by_environment_target"],
        "non_screened_by_reason": scope["non_screened_by_reason"],
        "planned_run_count": len(specs),
        "raw_result_count": len(results),
        "valid_result_count": len(valid),
        "invalid_result_count": len(invalid),
        "collapsed_row_count": len(collapsed),
        "label_row_count": len(labels),
        "algorithms": sorted({spec.algo for spec in specs}),
        "budgets_ms": sorted({spec.budget_ms for spec in specs}),
        "seeds": sorted({spec.seed for spec in specs}),
        "raw_status_counts": dict(Counter(str(row.get("status", "")) for row in results)),
        "valid_by_algo": dict(Counter(str(row["algo"]) for row in valid)),
        "invalid_by_algo": dict(Counter(str(row["algo"]) for row in invalid)),
        "preliminary_label_counts": dict(
            Counter(str(row["preliminary_exception_label"]) for row in labels)
        ),
        "strong_exception_candidate_count": sum(
            1
            for row in labels
            if row["preliminary_exception_label"] == "strong_exception_candidate"
        ),
        "near_tie_candidate_count": sum(
            1 for row in labels if row["preliminary_exception_label"] == "near_tie_candidate"
        ),
        "competitive_candidate_count": sum(
            1 for row in labels if row["preliminary_exception_label"] == "competitive_candidate"
        ),
        "availability_only_candidate_count": sum(
            1
            for row in labels
            if row["preliminary_exception_label"] == "availability_only_candidate"
        ),
    }


def write_invalid_output_report(path: Path, results: list[dict[str, Any]]) -> None:
    """Write invalid-output report."""

    invalid = [row for row in results if not bool(row.get("valid"))]
    lines = [
        "# Invalid output report — exploratory exception screening",
        "",
        f"- Generated at: `{utc_now()}`",
        f"- Total raw results: `{len(results)}`",
        f"- Invalid results: `{len(invalid)}`",
        "- Claim status: `exploratory_non_confirmatory`",
        "",
    ]

    if not invalid:
        lines.append("No invalid solver outputs were observed.")
    else:
        lines.extend(
            [
                "| run_id | candidate_id | algo | budget_ms | status | error_type | error_message |",
                "|---|---|---:|---:|---|---|---|",
            ]
        )
        for row in invalid:
            lines.append(
                "| {run_id} | {candidate_id} | {algo} | {budget_ms} | {status} | {error_type} | {error_message} |".format(
                    **{key: str(value).replace("|", "\\|") for key, value in row.items()}
                )
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_solver_artifact_inventory(path: Path, results: list[dict[str, Any]]) -> None:
    """Write solver artifact inventory JSON."""

    inventory = []
    for row in results:
        artifact_dir = Path(str(row["artifact_dir"]))
        files = sorted(
            str(file.relative_to(artifact_dir))
            for file in artifact_dir.rglob("*")
            if file.is_file()
        )
        inventory.append(
            {
                "run_id": row["run_id"],
                "candidate_id": row["candidate_id"],
                "algo": row["algo"],
                "budget_ms": row["budget_ms"],
                "status": row["status"],
                "valid": row["valid"],
                "artifact_dir": row["artifact_dir"],
                "files": files,
            }
        )
    write_json(path, inventory)


def write_solver_artifact_inventory_md(path: Path, results: list[dict[str, Any]]) -> None:
    """Write compact solver artifact inventory markdown."""

    by_algo = Counter(str(row["algo"]) for row in results)
    by_status = Counter(str(row["status"]) for row in results)
    lines = [
        "# Solver artifact inventory — exploratory exception screening",
        "",
        f"- Generated at: `{utc_now()}`",
        f"- Total runs: `{len(results)}`",
        "- Claim status: `exploratory_non_confirmatory`",
        "",
        "## Runs by algorithm",
        "",
    ]
    for algo, count in sorted(by_algo.items()):
        lines.append(f"- `{algo}`: `{count}`")

    lines.extend(["", "## Runs by status", ""])
    for status, count in sorted(by_status.items()):
        lines.append(f"- `{status}`: `{count}`")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    """Write human-readable summary."""

    lines = [
        "# Screening summary — exploratory exception mining",
        "",
        f"- Campaign: `{summary['campaign_id']}`",
        f"- Classification: `{summary['classification']}`",
        f"- Monograph claim status: `{summary['monograph_claim_status']}`",
        f"- CART/ASP claim status: `{summary['cart_asp_claim_status']}`",
        f"- Autotuning status: `{summary['autotuning_status']}`",
        f"- Screened candidates: `{summary['screened_candidate_count']}`",
        f"- Non-screened candidates: `{summary['non_screened_candidate_count']}`",
        f"- Holdout reserved: `{summary['holdout_reserved_count']}`",
        f"- Planned runs: `{summary['planned_run_count']}`",
        f"- Raw results: `{summary['raw_result_count']}`",
        f"- Valid results: `{summary['valid_result_count']}`",
        f"- Invalid results: `{summary['invalid_result_count']}`",
        "",
        "## Screened by environment target",
        "",
    ]

    for target, count in sorted(summary["screened_by_environment_target"].items()):
        lines.append(f"- `{target}`: `{count}`")

    lines.extend(["", "## Preliminary label counts", ""])
    for label, count in sorted(summary["preliminary_label_counts"].items()):
        lines.append(f"- `{label}`: `{count}`")

    lines.extend(
        [
            "",
            "These labels are exploratory hypotheses for confirmation only. They do not support final algorithm-superiority, CART, or ASP claims.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def run_spec_to_json(spec: ScreeningRunSpec) -> dict[str, Any]:
    """Serialize run spec."""

    payload = asdict(spec)
    payload["bundle_path"] = str(spec.bundle_path)
    payload["instance_path"] = str(spec.instance_path)
    return payload


def run_event(spec: ScreeningRunSpec, event: str, **extra: Any) -> dict[str, Any]:
    """Build one run-attempt event."""

    return {
        "event": event,
        "timestamp": utc_now(),
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": spec.candidate_id,
        "family": spec.family,
        "environment_target": spec.environment_target,
        "variant": spec.variant,
        "algo": spec.algo,
        "seed": spec.seed,
        "budget_ms": spec.budget_ms,
        "claim_status": "exploratory_non_confirmatory",
        **extra,
    }


def read_json_object(path: Path) -> dict[str, Any]:
    """Read JSON object."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def read_json_list(path: Path) -> list[dict[str, Any]]:
    """Read JSON list of objects."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"{path} must contain only JSON objects")
    return data


def write_json(path: Path, payload: Any) -> None:
    """Write deterministic JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_jsonl(path: Path, payload: dict[str, Any]) -> None:
    """Append one JSONL record."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write CSV rows."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row}) if rows else ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: normalize_csv_value(row.get(key, "")) for key in fieldnames})


def normalize_csv_value(value: Any) -> Any:
    """Normalize CSV values."""

    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return ""
    if isinstance(value, list | dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def utc_now() -> str:
    """Return current UTC timestamp."""

    return datetime.now(UTC).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
