#!/usr/bin/env python3
"""Build portable full-portfolio confirmation run plans for exception mining.

This script is a pre-execution planning gate for Issue #102. It reads the
candidate-freeze confirmation manifest, expands the frozen candidate,
algorithm, budget, and seed grid, and writes an auditable run plan. It does not
execute solvers and does not produce evidence-bearing confirmation results.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CAMPAIGN_ID = "EXP-MULTILEVEL-EXCEPTION-MINING-001"
DEFAULT_CONFIRMATION_MANIFEST = Path(
    "audit_reports/multilevel_exception_mining/candidate_freeze/confirmation_manifest.json"
)
DEFAULT_OUTPUT_ROOT = Path(
    "audit_reports/multilevel_exception_mining/confirmation/confirmation_plan_001"
)

ALGO_NORMALIZATION = {
    "METIS": "metis",
    "KaHIP": "kahip",
    "SA": "sa",
    "ILS": "ils",
    "GRASP": "grasp",
    "TS": "ts",
    "SA-Rust": "sa_rust",
    "ILS-Rust": "ils_rust",
    "GRASP-Rust": "grasp_rust",
    "TS-Rust": "ts_rust",
}

REQUIRED_BUNDLE_FILES = (
    "instance.json.gz",
    "graph_metis.graph",
    "graph_edges.edgelist",
    "manifest_row.json",
    "sha256sums.txt",
)


@dataclass(frozen=True)
class ConfirmationRunSpec:
    """One planned full-portfolio confirmation run."""

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
    bundle_path: str
    instance_path: str
    graph_metis_path: str
    graph_edges_path: str
    manifest_row_path: str
    sha256sums_path: str
    artifact_dir: str
    artifact_json: str
    workdir: str
    claim_boundary: str


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirmation-manifest",
        type=Path,
        default=DEFAULT_CONFIRMATION_MANIFEST,
        help="Path to candidate_freeze/confirmation_manifest.json.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where the confirmation run plan will be written.",
    )
    parser.add_argument(
        "--environment-id",
        default="unassigned_environment",
        help=(
            "Explicit execution environment identifier, for example "
            "windows11_16gb_docker_linux, wsl_notebook_8gb, or linux_server_8gb."
        ),
    )
    parser.add_argument(
        "--bundle-root-override",
        type=Path,
        default=None,
        help=(
            "Optional portable root for generated bundles. When provided, each "
            "candidate bundle is resolved as root / family / candidate_id."
        ),
    )
    parser.add_argument(
        "--profile",
        choices=["issue102", "smoke"],
        default="issue102",
        help="issue102 expands the full frozen matrix; smoke emits a tiny non-execution plan.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacing an existing output directory.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Create a full-portfolio confirmation run plan."""

    args = build_parser().parse_args(argv)
    manifest_path = args.confirmation_manifest.resolve()
    output_root = args.output_root.resolve()

    if output_root.exists() and any(output_root.iterdir()) and not args.force:
        raise SystemExit(f"output root already exists and is not empty: {output_root}")

    if output_root.exists() and args.force:
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    manifest = read_json_object(manifest_path)
    candidates = read_candidates(manifest)

    if args.profile == "smoke":
        candidates = candidates[:2]

    specs = build_run_plan(
        candidates,
        output_root=output_root,
        environment_id=str(args.environment_id),
        bundle_root_override=args.bundle_root_override,
        profile=str(args.profile),
    )

    write_json(
        output_root / "confirmation_scope_manifest.json", build_scope(manifest, candidates, args)
    )
    write_json(output_root / "confirmation_run_plan.json", [asdict(spec) for spec in specs])
    write_csv(output_root / "confirmation_run_plan.csv", [asdict(spec) for spec in specs])

    validation_report = validate_run_plan(specs)
    write_json(output_root / "confirmation_plan_validation_report.json", validation_report)

    summary = build_summary(manifest, candidates, specs, validation_report, args)
    write_json(output_root / "confirmation_plan_summary.json", summary)
    write_summary_md(output_root / "confirmation_plan_summary.md", summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def read_json_object(path: Path) -> dict[str, Any]:
    """Read a JSON object."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def read_candidates(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Read frozen confirmation candidates."""

    candidates = manifest.get("candidates")
    if not isinstance(candidates, list) or not all(isinstance(row, dict) for row in candidates):
        raise ValueError("confirmation_manifest.json must contain a list field named 'candidates'")
    return list(candidates)


def build_run_plan(
    candidates: list[dict[str, Any]],
    *,
    output_root: Path,
    environment_id: str,
    bundle_root_override: Path | None,
    profile: str,
) -> list[ConfirmationRunSpec]:
    """Expand candidates into the confirmation Cartesian product."""

    specs: list[ConfirmationRunSpec] = []
    for candidate in candidates:
        candidate_id = require_str(candidate, "candidate_id")
        family = require_str(candidate, "family")
        bundle_path = resolve_bundle_path(candidate, bundle_root_override=bundle_root_override)
        paths = derive_bundle_paths(bundle_path)

        algos = parse_algorithms(require_str(candidate, "confirmation_portfolio"))
        budgets = parse_int_list(require_str(candidate, "confirmation_budgets_ms"))
        seeds = parse_int_list(require_str(candidate, "confirmation_seeds"))

        if profile == "smoke":
            algos = algos[:2]
            budgets = budgets[:2]
            seeds = seeds[:2]

        for algo_label, algo in algos:
            for budget_ms in budgets:
                for seed in seeds:
                    run_id = (
                        f"{candidate_id}__{algo}__seed{seed}__budget{budget_ms}"
                        f"__env_{environment_id}"
                    )
                    artifact_dir = output_root / "solver_artifacts" / family / candidate_id / run_id
                    specs.append(
                        ConfirmationRunSpec(
                            campaign_id=CAMPAIGN_ID,
                            confirmation_stage="full_portfolio_confirmation_plan",
                            environment_id=environment_id,
                            run_id=run_id,
                            candidate_id=candidate_id,
                            family=family,
                            environment_target=str(candidate.get("environment_target", "")),
                            variant=str(candidate.get("variant", "")),
                            priority_label_from_screening=str(
                                candidate.get("priority_label_from_screening", "")
                            ),
                            algo_label=algo_label,
                            algo=algo,
                            seed=seed,
                            budget_ms=budget_ms,
                            bundle_path=str(bundle_path),
                            instance_path=str(paths["instance_path"]),
                            graph_metis_path=str(paths["graph_metis_path"]),
                            graph_edges_path=str(paths["graph_edges_path"]),
                            manifest_row_path=str(paths["manifest_row_path"]),
                            sha256sums_path=str(paths["sha256sums_path"]),
                            artifact_dir=str(artifact_dir),
                            artifact_json=str(artifact_dir / "result.json"),
                            workdir=str(artifact_dir / "workdir"),
                            claim_boundary="run_plan_only_not_confirmation_result",
                        )
                    )

    return specs


def resolve_bundle_path(
    candidate: dict[str, Any],
    *,
    bundle_root_override: Path | None,
) -> Path:
    """Resolve a candidate bundle path, supporting portable repo relocation."""

    candidate_id = require_str(candidate, "candidate_id")
    family = require_str(candidate, "family")

    if bundle_root_override is not None:
        return (bundle_root_override / family / candidate_id).resolve()

    raw = require_str(candidate, "bundle_path")
    path = Path(raw)

    if path.exists():
        return path.resolve()

    repo_root = Path.cwd().resolve()

    if path.is_absolute():
        parts = path.parts
        if "audit_reports" in parts:
            idx = parts.index("audit_reports")
            relocated = repo_root.joinpath(*parts[idx:])
            if relocated.exists():
                return relocated.resolve()

        fallback = (
            repo_root
            / "audit_reports"
            / "multilevel_exception_mining"
            / "candidate_pool"
            / "exploratory_pool_001"
            / "bundles"
            / family
            / candidate_id
        )
        if fallback.exists():
            return fallback.resolve()

    relative = (repo_root / path).resolve()
    if relative.exists():
        return relative

    raise FileNotFoundError(
        f"Could not resolve bundle for candidate {candidate_id!r}; raw bundle_path={raw!r}"
    )


def derive_bundle_paths(bundle_path: Path) -> dict[str, Path]:
    """Derive required per-bundle paths from a resolved bundle directory."""

    paths = {
        "instance_path": bundle_path / "instance.json.gz",
        "graph_metis_path": bundle_path / "graph_metis.graph",
        "graph_edges_path": bundle_path / "graph_edges.edgelist",
        "manifest_row_path": bundle_path / "manifest_row.json",
        "sha256sums_path": bundle_path / "sha256sums.txt",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Bundle is missing required files: " + "; ".join(missing))
    return paths


def parse_algorithms(raw: str) -> list[tuple[str, str]]:
    """Parse semicolon-separated algorithm labels into normalized runner ids."""

    labels = [part.strip() for part in raw.split(";") if part.strip()]
    if not labels:
        raise ValueError("confirmation_portfolio is empty")

    parsed: list[tuple[str, str]] = []
    for label in labels:
        if label not in ALGO_NORMALIZATION:
            raise ValueError(f"Unknown confirmation algorithm label: {label!r}")
        parsed.append((label, ALGO_NORMALIZATION[label]))
    return parsed


def parse_int_list(raw: str) -> list[int]:
    """Parse semicolon-separated integers."""

    values = [int(part.strip()) for part in raw.split(";") if part.strip()]
    if not values:
        raise ValueError(f"empty integer list: {raw!r}")
    return values


def require_str(row: dict[str, Any], key: str) -> str:
    """Read a required non-empty string field."""

    value = row.get(key)
    if value in (None, ""):
        raise ValueError(f"missing required field: {key}")
    return str(value)


def validate_run_plan(specs: list[ConfirmationRunSpec]) -> dict[str, Any]:
    """Validate run-plan integrity without executing solvers."""

    errors: list[str] = []
    run_ids = [spec.run_id for spec in specs]
    duplicate_run_ids = sorted([run_id for run_id, count in Counter(run_ids).items() if count > 1])

    if duplicate_run_ids:
        errors.append(f"duplicate run_id values: {duplicate_run_ids[:10]}")

    for spec in specs:
        for attr in (
            "bundle_path",
            "instance_path",
            "graph_metis_path",
            "graph_edges_path",
            "manifest_row_path",
            "sha256sums_path",
        ):
            path = Path(getattr(spec, attr))
            if not path.exists():
                errors.append(f"{spec.run_id}: missing {attr}: {path}")

    return {
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors[:200],
        "checked_run_count": len(specs),
        "duplicate_run_id_count": len(duplicate_run_ids),
        "required_bundle_files": list(REQUIRED_BUNDLE_FILES),
        "claim_boundary": "plan_validation_only_no_solver_execution",
    }


def build_scope(
    manifest: dict[str, Any],
    candidates: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Build scope manifest."""

    return {
        "campaign_id": CAMPAIGN_ID,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "confirmation_manifest": str(args.confirmation_manifest),
        "profile": args.profile,
        "environment_id": args.environment_id,
        "bundle_root_override": (
            "" if args.bundle_root_override is None else str(args.bundle_root_override)
        ),
        "candidate_count": len(candidates),
        "source_freeze_id": manifest.get("metadata", {}).get("freeze_id", ""),
        "source_selection_policy": manifest.get("metadata", {}).get("selection_policy", ""),
        "claim_boundary": "scope_manifest_only_no_solver_execution",
    }


def build_summary(
    manifest: dict[str, Any],
    candidates: list[dict[str, Any]],
    specs: list[ConfirmationRunSpec],
    validation_report: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Build run-plan summary."""

    algorithm_counts = Counter(spec.algo for spec in specs)
    budget_counts = Counter(spec.budget_ms for spec in specs)
    seed_counts = Counter(spec.seed for spec in specs)
    family_counts = Counter(spec.family for spec in specs)
    environment_target_counts = Counter(spec.environment_target for spec in specs)
    label_counts = Counter(spec.priority_label_from_screening for spec in specs)

    candidate_ids = {spec.candidate_id for spec in specs}

    return {
        "campaign_id": CAMPAIGN_ID,
        "issue": 102,
        "classification": "confirmation_run_plan_only",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "profile": args.profile,
        "environment_id": args.environment_id,
        "source_freeze_id": manifest.get("metadata", {}).get("freeze_id", ""),
        "source_selection_policy": manifest.get("metadata", {}).get("selection_policy", ""),
        "candidate_count": len(candidates),
        "planned_candidate_count": len(candidate_ids),
        "planned_run_count": len(specs),
        "algorithm_count": len(algorithm_counts),
        "budget_count": len(budget_counts),
        "seed_count": len(seed_counts),
        "algorithms": sorted(algorithm_counts),
        "budgets_ms": sorted(budget_counts),
        "seeds": sorted(seed_counts),
        "family_counts": dict(sorted(family_counts.items())),
        "environment_target_counts": dict(sorted(environment_target_counts.items())),
        "priority_label_counts_by_run": dict(sorted(label_counts.items())),
        "validation": validation_report,
        "claim_boundary": (
            "This artifact is a confirmation run plan. It does not contain solver "
            "outputs and cannot support solver-superiority, CART, ASP, or monograph claims."
        ),
    }


def write_json(path: Path, payload: Any) -> None:
    """Write JSON payload."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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
    """Write compact Markdown summary."""

    lines = [
        "# Confirmation run-plan summary",
        "",
        f"- Campaign: `{summary['campaign_id']}`",
        f"- Issue: `#{summary['issue']}`",
        f"- Classification: `{summary['classification']}`",
        f"- Environment id: `{summary['environment_id']}`",
        f"- Profile: `{summary['profile']}`",
        f"- Candidate count: `{summary['planned_candidate_count']}`",
        f"- Planned runs: `{summary['planned_run_count']}`",
        f"- Algorithms: `{', '.join(summary['algorithms'])}`",
        f"- Budgets ms: `{', '.join(str(item) for item in summary['budgets_ms'])}`",
        f"- Seeds: `{', '.join(str(item) for item in summary['seeds'])}`",
        f"- Plan validation: `{'valid' if summary['validation']['valid'] else 'invalid'}`",
        "",
        "## Claim boundary",
        "",
        summary["claim_boundary"],
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
