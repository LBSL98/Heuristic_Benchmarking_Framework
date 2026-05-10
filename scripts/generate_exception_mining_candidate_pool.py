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
    source_parent_candidate_id: str = ""
    scale_factor: float | None = None
    frontier_profile: str = ""


FRONTIER_PROFILE = "srv_noctua_frontier_pilot_001"
FRONTIER_PARENT_CANDIDATE_IDS: tuple[str, ...] = (
    "f04_common_a_seed990401",
    "f04_common_b_seed990402",
    "f04_common_c_seed990403",
    "f04_common_scaled_seed990404",
    "f04_server_a_seed990405",
    "f04_server_b_seed990406",
    "f04_server_scaled_seed990407",
    "f07_common_a_seed990701",
    "f07_common_b_seed990702",
    "f07_common_c_seed990703",
    "f07_common_scaled_seed990704",
    "f07_server_a_seed990705",
    "f07_server_b_seed990706",
    "f07_server_scaled_seed990707",
    "f01_common_scaled_seed990104",
    "f01_server_scaled_seed990107",
    "f05_common_b_seed990502",
    "f05_common_scaled_seed990504",
    "f05_server_scaled_seed990507",
    "f06_server_scaled_seed990607",
    "f08_common_b_seed990802",
    "f08_server_b_seed990806",
    "f08_server_scaled_seed990807",
)
FRONTIER_NEGATIVE_CONTROL_PARENT_IDS: tuple[str, ...] = (
    "f02_common_b_seed990202",
    "f02_common_scaled_seed990204",
    "f02_server_scaled_seed990207",
    "f03_common_b_seed990302",
    "f03_common_scaled_seed990304",
    "f03_server_scaled_seed990307",
)
FRONTIER_SCALE_FACTORS: tuple[float, ...] = (2.0, 4.0)

FRONTIER_EXPANSION_002_PROFILE = "frontier_expansion_002"

FRONTIER_EXPANSION_002_PARENT_SPECS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (
        "f01_common_scaled_frontier_x4p0_seed991152",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
    (
        "f01_server_scaled_frontier_x2p0_seed991161",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
    (
        "f01_server_scaled_frontier_x4p0_seed991162",
        ("budget_boundary_variant_if_supported", "scale_up_next"),
        "budget_sensitivity_probe",
    ),
    (
        "f02_common_b_frontier_x2p0_seed991241",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
    (
        "f02_common_scaled_frontier_x4p0_seed991252",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
    (
        "f02_server_scaled_frontier_x2p0_seed991261",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
    (
        "f04_common_a_frontier_x2p0_seed991011",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_common_a_frontier_x4p0_seed991012",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_common_b_frontier_x2p0_seed991021",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_common_b_frontier_x4p0_seed991022",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_common_c_frontier_x2p0_seed991031",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_common_c_frontier_x4p0_seed991032",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_common_scaled_frontier_x2p0_seed991041",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_common_scaled_frontier_x4p0_seed991042",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_server_a_frontier_x2p0_seed991051",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_server_a_frontier_x4p0_seed991052",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_server_b_frontier_x2p0_seed991061",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_server_b_frontier_x4p0_seed991062",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_server_scaled_frontier_x2p0_seed991071",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f04_server_scaled_frontier_x4p0_seed991072",
        ("scale_up_next", "scale_up_high", "morphology_neighbor_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f05_common_b_frontier_x2p0_seed991171",
        ("scale_up_next", "control_neighbor_if_supported"),
        "negative_control_anchor",
    ),
    (
        "f05_common_b_frontier_x4p0_seed991172",
        ("scale_up_next", "control_neighbor_if_supported"),
        "negative_control_anchor",
    ),
    (
        "f05_common_scaled_frontier_x2p0_seed991181",
        ("near_boundary_variant_if_supported", "scale_up_next"),
        "decision_boundary_probe",
    ),
    (
        "f05_common_scaled_frontier_x4p0_seed991182",
        ("scale_up_next", "control_neighbor_if_supported"),
        "negative_control_anchor",
    ),
    (
        "f05_server_scaled_frontier_x2p0_seed991191",
        ("scale_up_next", "control_neighbor_if_supported"),
        "negative_control_anchor",
    ),
    (
        "f05_server_scaled_frontier_x4p0_seed991192",
        ("scale_up_next", "control_neighbor_if_supported"),
        "negative_control_anchor",
    ),
    (
        "f06_server_scaled_frontier_x2p0_seed991201",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
    (
        "f06_server_scaled_frontier_x4p0_seed991202",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
    (
        "f07_common_a_frontier_x2p0_seed991081",
        ("scale_up_next", "budget_boundary_variant_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f07_common_a_frontier_x4p0_seed991082",
        ("scale_up_next", "budget_boundary_variant_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f07_common_b_frontier_x2p0_seed991091",
        ("scale_up_next", "budget_boundary_variant_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f07_common_b_frontier_x4p0_seed991092",
        ("near_boundary_variant_if_supported", "scale_up_next"),
        "decision_boundary_probe",
    ),
    (
        "f07_common_c_frontier_x2p0_seed991101",
        ("scale_up_next", "budget_boundary_variant_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f07_server_a_frontier_x2p0_seed991121",
        ("scale_up_next", "budget_boundary_variant_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f07_server_a_frontier_x4p0_seed991122",
        ("scale_up_next", "budget_boundary_variant_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f07_server_b_frontier_x2p0_seed991131",
        ("scale_up_next", "budget_boundary_variant_if_supported"),
        "primary_expansion_anchor",
    ),
    (
        "f07_server_scaled_frontier_x4p0_seed991142",
        ("budget_boundary_variant_if_supported", "scale_up_next"),
        "budget_sensitivity_probe",
    ),
    (
        "f08_common_b_frontier_x4p0_seed991212",
        ("near_boundary_variant_if_supported", "scale_up_next"),
        "decision_boundary_probe",
    ),
    (
        "f08_server_b_frontier_x2p0_seed991221",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
    (
        "f08_server_scaled_frontier_x2p0_seed991231",
        ("scale_up_next",),
        "supporting_strong_diversity_anchor",
    ),
)


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
        choices=["issue99", "smoke", FRONTIER_PROFILE, FRONTIER_EXPANSION_002_PROFILE],
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


def _family_from_candidate_id(candidate_id: str) -> str:
    """Infer topology family from a frozen candidate id."""

    prefix = candidate_id.split("_", maxsplit=1)[0]
    if len(prefix) != 3 or not prefix.startswith("f") or not prefix[1:].isdigit():
        raise ValueError(f"cannot infer family from candidate id: {candidate_id}")
    return prefix.upper()


def _variant_from_candidate_id(candidate_id: str) -> str:
    """Infer candidate variant from a frozen candidate id."""

    stem = candidate_id.split("_seed", maxsplit=1)[0]
    parts = stem.split("_")
    if len(parts) < 2:
        raise ValueError(f"cannot infer variant from candidate id: {candidate_id}")
    return "_".join(parts[1:])


def _environment_target_from_variant(variant: str) -> EnvironmentTarget:
    """Infer environment target from a candidate variant name."""

    if variant.startswith("server_"):
        return "server_expanded"
    if variant.startswith("common_"):
        return "common"
    if variant.startswith("holdout_"):
        return "holdout"
    raise ValueError(f"cannot infer environment target from variant: {variant}")


def frontier_scaled_parameters(
    family: str, parent_variant: str, scale_factor: float
) -> dict[str, Any]:
    """Return graph-parameter overrides for a frontier scaled successor.

    The srv-noctua frontier pilot expands graph size while preserving or slightly
    reducing density-like parameters. This follows the validated campaign audit:
    confirmed exceptions were concentrated in lower-density regimes, so increasing
    density is not the default expansion direction.
    """

    defaults = family_defaults(family)
    parent_overrides = variant_parameters(family, parent_variant)
    merged = defaults | parent_overrides
    params = dict(parent_overrides)

    size_exact = {
        "n",
        "n_approx",
        "module_size",
        "left_core_size",
        "right_core_size",
        "bridge_length",
    }
    size_tokens = ("node", "nodes", "vertices", "size")
    density_tokens = (
        "density",
        "prob",
        "mixing_mu",
        "hub_noise_edges",
        "inter_block_noise",
    )

    for key, value in merged.items():
        lower_key = key.lower()

        if isinstance(value, bool):
            continue

        if isinstance(value, int):
            if key in {"k", "target_partition_k"}:
                continue
            if lower_key in size_exact or any(token in lower_key for token in size_tokens):
                params[key] = max(value + 1, int(round(value * scale_factor)))
            elif lower_key in {"communities", "module_count", "planted_blocks"}:
                increment = 1 if scale_factor <= 2.0 else 2
                params[key] = max(value, value + increment)

        elif isinstance(value, float):
            if lower_key == "epsilon":
                continue
            if lower_key == "planted_signal":
                params[key] = value
            elif any(token in lower_key for token in density_tokens):
                factor = 0.95 if scale_factor <= 2.0 else 0.90
                params[key] = max(0.0, min(value, value * factor))
            elif "skew" in lower_key or "imbalance" in lower_key:
                params[key] = min(0.95, max(0.0, value * 1.05))

    return params


def build_frontier_candidate_plan() -> list[CandidateSpec]:
    """Build the deterministic srv-noctua frontier pilot candidate plan."""

    plan: list[CandidateSpec] = []
    parent_ids = FRONTIER_PARENT_CANDIDATE_IDS + FRONTIER_NEGATIVE_CONTROL_PARENT_IDS

    for parent_index, source_parent_candidate_id in enumerate(parent_ids, start=1):
        family = _family_from_candidate_id(source_parent_candidate_id)
        parent_variant = _variant_from_candidate_id(source_parent_candidate_id)
        environment_target = _environment_target_from_variant(parent_variant)
        is_negative_control = source_parent_candidate_id in FRONTIER_NEGATIVE_CONTROL_PARENT_IDS

        for scale_index, scale_factor in enumerate(FRONTIER_SCALE_FACTORS, start=1):
            scale_label = str(scale_factor).replace(".", "p")
            seed = 991000 + parent_index * 10 + scale_index
            candidate_id = f"{family.lower()}_{parent_variant}_frontier_x{scale_label}_seed{seed}"

            pool_role = (
                "frontier_negative_control" if is_negative_control else "frontier_pilot_candidate"
            )
            lifecycle_state = "generated"

            plan.append(
                CandidateSpec(
                    candidate_id=candidate_id,
                    family=family,
                    seed=seed,
                    params=frontier_scaled_parameters(family, parent_variant, scale_factor),
                    environment_target=environment_target,
                    pool_role=pool_role,
                    lifecycle_state=lifecycle_state,
                    variant=f"{parent_variant}_frontier_x{scale_label}",
                    intended_hypothesis=(
                        f"frontier scaled successor of {source_parent_candidate_id}; "
                        f"{family_hypothesis(family, environment_target)}"
                    ),
                    source_parent_candidate_id=source_parent_candidate_id,
                    scale_factor=scale_factor,
                    frontier_profile=FRONTIER_PROFILE,
                )
            )

    return plan


def _frontier_expansion_002_base_variant_and_scale(parent_variant: str) -> tuple[str, float]:
    """Return the original base variant and cumulative frontier scale.

    Expansion 002 uses confirmed frontier candidates as parents. Their variants
    already contain a suffix such as ``_frontier_x2p0``. The new expansion keeps
    scale cumulative relative to the original candidate variant instead of
    treating the frontier suffix as a native generator variant.
    """

    marker = "_frontier_x"
    if marker not in parent_variant:
        return parent_variant, 1.0

    base_variant, scale_token = parent_variant.rsplit(marker, 1)
    try:
        return base_variant, float(scale_token.replace("p", "."))
    except ValueError:
        return base_variant, 1.0


def _frontier_expansion_002_mode_multiplier(mode: str) -> float:
    """Return the cumulative scale multiplier for an expansion mode."""

    if mode == "scale_up_next":
        return 1.5
    if mode == "scale_up_high":
        return 2.0
    return 1.0


def _frontier_expansion_002_scale_label(scale_factor: float) -> str:
    """Encode a scale factor in candidate-id form."""

    return str(round(scale_factor, 2)).replace(".", "p")


def _frontier_expansion_002_pool_role(expansion_role: str) -> str:
    """Map evidence-map expansion roles to manifest pool roles."""

    if expansion_role == "negative_control_anchor":
        return "frontier_expansion_negative_control"
    if expansion_role == "budget_sensitivity_probe":
        return "frontier_expansion_budget_probe"
    if expansion_role == "decision_boundary_probe":
        return "frontier_expansion_boundary_candidate"
    return "frontier_expansion_candidate"


def build_frontier_expansion_002_candidate_plan() -> list[CandidateSpec]:
    """Build the deterministic second frontier expansion candidate plan."""

    plan: list[CandidateSpec] = []

    for parent_index, (
        source_parent_candidate_id,
        expansion_modes,
        expansion_role,
    ) in enumerate(FRONTIER_EXPANSION_002_PARENT_SPECS, start=1):
        family = _family_from_candidate_id(source_parent_candidate_id)
        parent_variant = _variant_from_candidate_id(source_parent_candidate_id)
        base_variant, parent_scale = _frontier_expansion_002_base_variant_and_scale(parent_variant)
        environment_target = _environment_target_from_variant(base_variant)

        for mode_index, mode in enumerate(expansion_modes, start=1):
            multiplier = _frontier_expansion_002_mode_multiplier(mode)
            scale_factor = round(parent_scale * multiplier, 2)
            scale_label = _frontier_expansion_002_scale_label(scale_factor)
            seed = 992000 + parent_index * 10 + mode_index
            variant = f"{base_variant}_frontier_exp002_{mode}_{scale_label}"
            candidate_id = f"{family.lower()}_{variant}_seed{seed}"

            plan.append(
                CandidateSpec(
                    candidate_id=candidate_id,
                    family=family,
                    seed=seed,
                    params=frontier_scaled_parameters(family, base_variant, scale_factor),
                    environment_target=environment_target,
                    pool_role=_frontier_expansion_002_pool_role(expansion_role),
                    lifecycle_state="generated",
                    variant=variant,
                    intended_hypothesis=(
                        f"frontier expansion 002 successor of "
                        f"{source_parent_candidate_id}; "
                        f"{family_hypothesis(family, environment_target)}"
                    ),
                    source_parent_candidate_id=source_parent_candidate_id,
                    scale_factor=scale_factor,
                    frontier_profile=FRONTIER_EXPANSION_002_PROFILE,
                )
            )

    return plan


def build_candidate_plan(profile: str) -> list[CandidateSpec]:
    """Build the deterministic candidate generation plan."""

    if profile == FRONTIER_PROFILE:
        return build_frontier_candidate_plan()

    if profile == FRONTIER_EXPANSION_002_PROFILE:
        return build_frontier_expansion_002_candidate_plan()

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
            "source_parent_candidate_id": spec.source_parent_candidate_id,
            "scale_factor": spec.scale_factor,
            "frontier_profile": spec.frontier_profile,
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
            "source_parent_candidate_id": spec.source_parent_candidate_id,
            "scale_factor": spec.scale_factor,
            "frontier_profile": spec.frontier_profile,
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
            "source_parent_candidate_id": spec.source_parent_candidate_id,
            "scale_factor": spec.scale_factor,
            "frontier_profile": spec.frontier_profile,
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
        "source_parent_candidate_id": spec.source_parent_candidate_id,
        "scale_factor": spec.scale_factor,
        "frontier_profile": spec.frontier_profile,
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
