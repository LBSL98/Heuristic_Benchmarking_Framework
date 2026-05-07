#!/usr/bin/env python3
"""Materialize the exploratory exception-mining candidate pool."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from exception_mining.generation import family_defaults

CAMPAIGN_ID = "EXP-MULTILEVEL-EXCEPTION-MINING-001"
FAMILIES = ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08")
EnvironmentTarget = Literal["common", "wsl_local", "server_expanded", "holdout"]


@dataclass(frozen=True)
class CandidateSpec:
    """One deterministic candidate-pool generation attempt."""

    candidate_id: str
    family: str
    seed: int
    params: dict[str, Any]
    environment_target: EnvironmentTarget
    pool_role: str
    lifecycle_state: str
    variant: str
    intended_hypothesis: str


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate the issue #99 exploratory exception-mining candidate pool. "
            "This script only generates and validates graph bundles; it never runs solvers."
        )
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(
            "audit_reports/multilevel_exception_mining/candidate_pool/exploratory_pool_001"
        ),
        help="Directory where pool manifests and per-instance bundles will be written.",
    )
    parser.add_argument(
        "--profile",
        choices=["issue99", "smoke"],
        default="issue99",
        help="Candidate plan profile.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacing an existing output directory.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run candidate-pool materialization."""

    args = build_parser().parse_args(argv)
    output_root = args.output_root.resolve()

    if output_root.exists() and any(output_root.iterdir()) and not args.force:
        raise SystemExit(f"output root already exists and is not empty: {output_root}")

    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "bundles").mkdir(exist_ok=True)
    (output_root / "validation_reports").mkdir(exist_ok=True)

    plan = build_candidate_plan(args.profile)
    write_json(output_root / "candidate_pool_plan.json", [asdict(spec) for spec in plan])

    rows: list[dict[str, Any]] = []
    attempts_path = output_root / "generation_attempts.jsonl"

    for spec in plan:
        write_jsonl(attempts_path, attempt_event(spec, "attempt_started"))

        generation = run_generator(spec, output_root)
        if generation["returncode"] != 0:
            row = row_from_failed_generation(spec, output_root, generation)
            rows.append(row)
            write_jsonl(
                attempts_path,
                attempt_event(
                    spec,
                    "generation_failed",
                    returncode=generation["returncode"],
                    rejection_reason=row["rejection_reason"],
                ),
            )
            continue

        bundle_dir = Path(generation["bundle_dir"])
        rewrite_bundle_metadata(bundle_dir, spec)
        write_jsonl(attempts_path, attempt_event(spec, "bundle_metadata_annotated"))

        validation = validate_bundle(
            bundle_dir, output_root / "validation_reports" / f"{spec.candidate_id}.json"
        )
        if validation["returncode"] == 0:
            row = row_from_valid_candidate(spec, bundle_dir, validation)
            write_jsonl(attempts_path, attempt_event(spec, "validation_passed"))
        else:
            row = row_from_failed_validation(spec, bundle_dir, validation)
            write_jsonl(
                attempts_path,
                attempt_event(
                    spec,
                    "validation_failed",
                    returncode=validation["returncode"],
                    rejection_reason=row["rejection_reason"],
                ),
            )
        rows.append(row)

    write_manifest(output_root, rows)
    write_rejection_log(output_root / "rejection_log.md", rows)
    write_validation_summary(output_root, plan, rows)

    print(json.dumps(summary_payload(output_root, rows), ensure_ascii=False, indent=2))
    return 0


def build_candidate_plan(profile: str) -> list[CandidateSpec]:
    """Build the deterministic candidate generation plan."""

    if profile == "smoke":
        families: tuple[str, ...] = ("F01", "F02")
        slots = [
            ("common_a", "common", "exploratory_candidate", "generated"),
            ("common_b", "common", "exploratory_candidate", "generated"),
            ("holdout_a", "holdout", "reserved_holdout", "holdout_reserved"),
        ]
        base_seed = 990000
    else:
        families = FAMILIES
        slots = [
            ("common_a", "common", "exploratory_candidate", "generated"),
            ("common_b", "common", "exploratory_candidate", "generated"),
            ("common_c", "common", "exploratory_candidate", "generated"),
            ("common_scaled", "common", "exploratory_candidate", "generated"),
            ("server_a", "server_expanded", "exploratory_candidate", "generated"),
            ("server_b", "server_expanded", "exploratory_candidate", "generated"),
            ("server_scaled", "server_expanded", "exploratory_candidate", "generated"),
            ("holdout_a", "holdout", "reserved_holdout", "holdout_reserved"),
        ]
        base_seed = 990000

    plan: list[CandidateSpec] = []
    for family_index, family in enumerate(families, start=1):
        for slot_index, (variant, environment_target, pool_role, lifecycle_state) in enumerate(
            slots, start=1
        ):
            seed = base_seed + family_index * 100 + slot_index
            candidate_id = f"{family.lower()}_{variant}_seed{seed}"
            plan.append(
                CandidateSpec(
                    candidate_id=candidate_id,
                    family=family,
                    seed=seed,
                    params=variant_parameters(family, variant),
                    environment_target=environment_target,  # type: ignore[arg-type]
                    pool_role=pool_role,
                    lifecycle_state=lifecycle_state,
                    variant=variant,
                    intended_hypothesis=family_hypothesis(family, environment_target),
                )
            )
    return plan


def variant_parameters(family: str, variant: str) -> dict[str, Any]:
    """Return deterministic parameter overrides for one candidate variant.

    Empty overrides intentionally rely on the frozen family defaults already used by the
    low-level generator. Scaled variants only alter keys that exist in those defaults.
    If a scaled variant is invalid for a family, the attempt remains logged as rejected.
    """

    if variant not in {"common_scaled", "server_scaled"}:
        return {}

    defaults = family_defaults(family)
    params: dict[str, Any] = {}

    for key, value in defaults.items():
        if isinstance(value, bool):
            continue

        lower_key = key.lower()

        if isinstance(value, int):
            if (
                any(token in lower_key for token in ("nodes", "node_count", "n_vertices"))
                or lower_key == "n"
            ):
                params[key] = max(
                    value + 1, int(value * (1.35 if variant == "common_scaled" else 1.75))
                )
            elif any(
                token in lower_key for token in ("module_size", "block_size", "community_size")
            ):
                params[key] = max(
                    value + 1, int(value * (1.25 if variant == "common_scaled" else 1.6))
                )
            elif any(token in lower_key for token in ("module_count", "communities", "blocks")):
                params[key] = max(value, value + (1 if variant == "common_scaled" else 2))
            elif any(
                token in lower_key
                for token in ("inter_module_edges", "bridge_edges", "bottleneck_edges")
            ):
                params[key] = max(1, value + 1)
            elif any(token in lower_key for token in ("width", "height", "rows", "cols", "length")):
                params[key] = max(
                    value + 1, int(value * (1.2 if variant == "common_scaled" else 1.5))
                )

        elif isinstance(value, float):
            if any(token in lower_key for token in ("density", "prob", "p_", "p")):
                factor = 1.1 if variant == "common_scaled" else 1.2
                params[key] = min(0.95, max(0.0, value * factor))
            elif "skew" in lower_key or "imbalance" in lower_key:
                params[key] = min(0.95, max(0.0, value * 1.1))

    return params


def family_hypothesis(family: str, environment_target: str) -> str:
    """Describe why this family enters the exploratory candidate pool."""

    base = {
        "F01": "modular-noise stress case for multilevel coarsening and quality-time behavior",
        "F02": "chain/ring module topology with narrow inter-module cuts",
        "F03": "barbell/lollipop bottleneck topology with separator sensitivity",
        "F04": "hub or power-law topology with degree heterogeneity",
        "F05": "tree plus dense-core topology with mixed local/global structure",
        "F06": "road-like sparse topology for spatial/local separator behavior",
        "F07": "dense weak-signal topology for noisy cut structure",
        "F08": "balance-hard planted topology for feasibility and balance stress",
    }.get(family, "preregistered exception-mining topology family")

    return f"{base}; intended environment stratum: {environment_target}"


def run_generator(spec: CandidateSpec, output_root: Path) -> dict[str, Any]:
    """Run the existing per-bundle generator CLI for one candidate."""

    cmd = [
        sys.executable,
        "scripts/generate_exception_mining_instances.py",
        "--family",
        spec.family,
        "--seed",
        str(spec.seed),
        "--output-root",
        str(output_root / "bundles"),
        "--instance-id",
        spec.candidate_id,
        "--params-json",
        json.dumps(spec.params, ensure_ascii=False, sort_keys=True),
        "--validate",
    ]
    completed = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        env=pythonpath_env(),
        check=False,
    )

    result: dict[str, Any] = {
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

    if completed.returncode == 0:
        payload = json.loads(completed.stdout)
        result["bundle_dir"] = payload["bundle_dir"]

    return result


def validate_bundle(bundle_dir: Path, report_path: Path) -> dict[str, Any]:
    """Validate one generated candidate bundle."""

    cmd = [
        sys.executable,
        "scripts/validate_exception_mining_bundle.py",
        str(bundle_dir),
        "--json-out",
        str(report_path),
        "--quiet",
    ]
    completed = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        env=pythonpath_env(),
        check=False,
    )
    return {
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "report_path": str(report_path),
    }


def rewrite_bundle_metadata(bundle_dir: Path, spec: CandidateSpec) -> None:
    """Annotate generated bundle metadata with pool-level fields and recompute hashes."""

    manifest_path = bundle_dir / "manifest_row.json"
    manifest = read_json_object(manifest_path)
    manifest.update(
        {
            "candidate_id": spec.candidate_id,
            "environment_target": spec.environment_target,
            "pool_role": spec.pool_role,
            "lifecycle_state": spec.lifecycle_state,
            "variant": spec.variant,
            "intended_hypothesis": spec.intended_hypothesis,
            "solver_results_used": False,
        }
    )
    write_json(manifest_path, manifest)
    write_manifest_row_csv(bundle_dir / "manifest_row.csv", manifest)

    config_path = bundle_dir / "generator_config.json"
    config = read_json_object(config_path)
    config.update(
        {
            "candidate_id": spec.candidate_id,
            "environment_target": spec.environment_target,
            "pool_role": spec.pool_role,
            "lifecycle_state": spec.lifecycle_state,
            "variant": spec.variant,
            "intended_hypothesis": spec.intended_hypothesis,
            "solver_results_used": False,
        }
    )
    write_json(config_path, config)

    write_jsonl(
        bundle_dir / "generator_log.jsonl",
        {
            "event": "candidate_pool_annotation",
            "timestamp": utc_now(),
            "candidate_id": spec.candidate_id,
            "environment_target": spec.environment_target,
            "pool_role": spec.pool_role,
            "lifecycle_state": spec.lifecycle_state,
            "variant": spec.variant,
        },
    )
    write_hashes(bundle_dir)


def row_from_valid_candidate(
    spec: CandidateSpec, bundle_dir: Path, validation: dict[str, Any]
) -> dict[str, Any]:
    """Build a manifest row for an accepted candidate."""

    metrics = read_json_object(bundle_dir / "graph_metrics.json")
    return base_row(spec) | {
        "accepted": True,
        "rejection_reason": "",
        "bundle_path": str(bundle_dir),
        "validation_passed": True,
        "validation_report_path": validation["report_path"],
        "num_vertices": metrics.get("num_vertices"),
        "num_edges": metrics.get("num_edges"),
        "density": metrics.get("density"),
        "degree_cv": metrics.get("degree_cv"),
        "modularity": metrics.get("modularity"),
        "connected_component_count": metrics.get("connected_component_count"),
        "largest_component_size": metrics.get("largest_component_size"),
    }


def row_from_failed_generation(
    spec: CandidateSpec, output_root: Path, generation: dict[str, Any]
) -> dict[str, Any]:
    """Build a manifest row for a failed generation attempt."""

    failure_path = output_root / "failed_attempts"
    failure_path.mkdir(exist_ok=True)
    stderr_path = failure_path / f"{spec.candidate_id}_stderr.txt"
    stdout_path = failure_path / f"{spec.candidate_id}_stdout.txt"
    stderr_path.write_text(str(generation.get("stderr", "")), encoding="utf-8")
    stdout_path.write_text(str(generation.get("stdout", "")), encoding="utf-8")

    return base_row(spec) | {
        "accepted": False,
        "rejection_reason": "rejected_runtime:generation_cli_failed",
        "bundle_path": "",
        "validation_passed": False,
        "validation_report_path": "",
        "num_vertices": "",
        "num_edges": "",
        "density": "",
        "degree_cv": "",
        "modularity": "",
        "connected_component_count": "",
        "largest_component_size": "",
        "generation_stderr_path": str(stderr_path),
        "generation_stdout_path": str(stdout_path),
    }


def row_from_failed_validation(
    spec: CandidateSpec, bundle_dir: Path, validation: dict[str, Any]
) -> dict[str, Any]:
    """Build a manifest row for a generated but invalid candidate bundle."""

    return base_row(spec) | {
        "accepted": False,
        "rejection_reason": "rejected_schema:bundle_validation_failed",
        "bundle_path": str(bundle_dir),
        "validation_passed": False,
        "validation_report_path": validation["report_path"],
        "num_vertices": "",
        "num_edges": "",
        "density": "",
        "degree_cv": "",
        "modularity": "",
        "connected_component_count": "",
        "largest_component_size": "",
        "validation_stderr": validation.get("stderr", ""),
    }


def base_row(spec: CandidateSpec) -> dict[str, Any]:
    """Build fields common to all campaign manifest rows."""

    return {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": spec.candidate_id,
        "family": spec.family,
        "instance_id": spec.candidate_id,
        "seed": spec.seed,
        "params_json": json.dumps(spec.params, ensure_ascii=False, sort_keys=True),
        "environment_target": spec.environment_target,
        "pool_role": spec.pool_role,
        "lifecycle_state": spec.lifecycle_state,
        "variant": spec.variant,
        "intended_hypothesis": spec.intended_hypothesis,
        "solver_results_used": False,
        "created_at_utc": utc_now(),
        "code_commit": git_commit(),
    }


def write_manifest(output_root: Path, rows: list[dict[str, Any]]) -> None:
    """Write JSON and CSV campaign-level manifests."""

    json_path = output_root / "generated_instances_manifest.json"
    csv_path = output_root / "generated_instances_manifest.csv"

    write_json(json_path, rows)

    fieldnames = sorted({key for row in rows for key in row})
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_rejection_log(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write the human-readable rejection log."""

    rejected = [row for row in rows if not row.get("accepted")]
    lines = [
        "# Rejection log — exploratory exception-mining candidate pool",
        "",
        f"- Generated at: `{utc_now()}`",
        f"- Total attempts: `{len(rows)}`",
        f"- Rejected attempts: `{len(rejected)}`",
        "- Solver results used for filtering: `false`",
        "",
    ]

    if not rejected:
        lines.append("No candidates were rejected in this materialization run.")
    else:
        lines.extend(
            [
                "| candidate_id | family | environment_target | reason |",
                "|---|---|---|---|",
            ]
        )
        for row in rejected:
            lines.append(
                "| {candidate_id} | {family} | {environment_target} | {rejection_reason} |".format(
                    **row
                )
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_validation_summary(
    output_root: Path, plan: list[CandidateSpec], rows: list[dict[str, Any]]
) -> None:
    """Write machine-readable and human-readable validation summaries."""

    summary = summary_payload(output_root, rows)
    summary["planned_attempt_count"] = len(plan)
    summary["families_planned"] = sorted({spec.family for spec in plan})
    summary["families_with_accepted_candidates"] = sorted(
        {str(row["family"]) for row in rows if row.get("accepted")}
    )
    summary["families_without_accepted_candidates"] = sorted(
        set(summary["families_planned"]) - set(summary["families_with_accepted_candidates"])
    )

    write_json(output_root / "validation_summary.json", summary)

    lines = [
        "# Validation summary — exploratory exception-mining candidate pool",
        "",
        f"- Campaign: `{CAMPAIGN_ID}`",
        f"- Output root: `{output_root}`",
        f"- Planned attempts: `{summary['planned_attempt_count']}`",
        f"- Accepted candidates: `{summary['accepted_count']}`",
        f"- Rejected candidates: `{summary['rejected_count']}`",
        f"- Solver results used for filtering: `{str(summary['solver_results_used']).lower()}`",
        "",
        "## Accepted by family",
        "",
    ]
    for family, count in sorted(summary["accepted_by_family"].items()):
        lines.append(f"- `{family}`: `{count}`")

    lines.extend(["", "## Accepted by environment target", ""])
    for target, count in sorted(summary["accepted_by_environment_target"].items()):
        lines.append(f"- `{target}`: `{count}`")

    if summary["families_without_accepted_candidates"]:
        lines.extend(["", "## Families without accepted candidates", ""])
        for family in summary["families_without_accepted_candidates"]:
            lines.append(f"- `{family}`")

    (output_root / "validation_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def summary_payload(output_root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the pool summary payload."""

    accepted = [row for row in rows if row.get("accepted")]
    rejected = [row for row in rows if not row.get("accepted")]

    return {
        "campaign_id": CAMPAIGN_ID,
        "output_root": str(output_root),
        "generated_at_utc": utc_now(),
        "attempt_count": len(rows),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted_by_family": dict(Counter(str(row["family"]) for row in accepted)),
        "accepted_by_environment_target": dict(
            Counter(str(row["environment_target"]) for row in accepted)
        ),
        "rejected_by_reason": dict(Counter(str(row["rejection_reason"]) for row in rejected)),
        "solver_results_used": any(bool(row.get("solver_results_used")) for row in rows),
        "contains_solver_results": False,
        "issue_scope": "generate exploratory candidate pool only; no solver execution",
    }


def attempt_event(spec: CandidateSpec, event: str, **extra: Any) -> dict[str, Any]:
    """Build one append-only generation attempt event."""

    return {
        "event": event,
        "timestamp": utc_now(),
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": spec.candidate_id,
        "family": spec.family,
        "seed": spec.seed,
        "params": spec.params,
        "environment_target": spec.environment_target,
        "pool_role": spec.pool_role,
        "lifecycle_state": spec.lifecycle_state,
        "variant": spec.variant,
        "solver_results_used": False,
        **extra,
    }


def read_json_object(path: Path) -> dict[str, Any]:
    """Read a JSON object."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, payload: Any) -> None:
    """Write deterministic JSON."""

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_jsonl(path: Path, payload: dict[str, Any]) -> None:
    """Append one JSONL record."""

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def write_manifest_row_csv(path: Path, row: dict[str, Any]) -> None:
    """Rewrite a single-row CSV bundle manifest."""

    fieldnames = sorted(row)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)


def write_hashes(bundle_dir: Path) -> None:
    """Rewrite bundle hashes after metadata annotation."""

    lines = []
    for path in sorted(bundle_dir.iterdir()):
        if not path.is_file() or path.name == "sha256sums.txt":
            continue
        lines.append(f"{sha256(path)}  {path.name}")
    (bundle_dir / "sha256sums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    """Compute SHA-256 for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pythonpath_env() -> dict[str, str]:
    """Return an environment with repository src available."""

    env = os.environ.copy()
    current = env.get("PYTHONPATH")
    env["PYTHONPATH"] = "src" if not current else f"src{os.pathsep}{current}"
    return env


def git_commit() -> str:
    """Return current git commit or unknown."""

    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip()


def utc_now() -> str:
    """Return current UTC timestamp."""

    return datetime.now(UTC).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
