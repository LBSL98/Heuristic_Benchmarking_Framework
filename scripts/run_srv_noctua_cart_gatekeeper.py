#!/usr/bin/env python3
"""Build a pre-training gate report for srv-noctua CART gatekeeper analysis.

This script validates the input contract, joins graph morphology features, and
materializes split/feature/parameter manifests. It intentionally does not train
CART yet. Model training is allowed only after this gate report is inspected.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXPECTED_ENVIRONMENT_ID = "srv_noctua_linux_8gb"
EXPECTED_CAMPAIGN_ID = "EXP-MULTILEVEL-EXCEPTION-MINING-001"

ALLOWED_FEATURE_COLUMNS = [
    "num_vertices",
    "num_edges",
    "density",
    "degree_cv",
    "modularity",
    "connected_component_count",
    "largest_component_size",
]

FIXED_CART_PARAMETER_TUPLE = {
    "criterion": "gini",
    "max_depth": 3,
    "min_samples_leaf": 3,
    "min_samples_split": 6,
    "random_state": 20260516,
    "class_weight": None,
}

FORBIDDEN_FEATURE_COLUMNS = [
    "algorithm winner",
    "best_multilevel_algo",
    "best_multilevel_cut",
    "best_meta_python_algo",
    "best_meta_python_cut",
    "best_meta_rust_algo",
    "best_meta_rust_cut",
    "best_meta_all_algo",
    "best_meta_all_cut",
    "relative_gap_meta_all_vs_multilevel",
    "confirmation_exception_label",
    "label_claim_status",
    "median_valid_cut_by_budget",
    "median_elapsed_ms",
    "median_seed",
    "best_valid_cut_by_budget",
    "best_elapsed_ms",
    "best_seed",
    "available_by_budget",
    "status_set",
    "environment_id as predictive feature",
    "file path",
    "solver-derived columns",
]

REQUIRED_FILES = {
    "final_validation": "checks/final_validation_summary.json",
    "confirmation_summary": "core/confirmation_summary.json",
    "collapsed": "derived/confirmation_collapsed.csv",
    "labels": "derived/confirmation_exception_labels.csv",
    "per_instance": "derived/per_instance_result_summary.csv",
    "oracle": "derived/sbs_vbs_oracle_gap.csv",
}

EXPECTED_LABEL_COLUMNS = [
    "campaign_id",
    "confirmation_stage",
    "environment_id",
    "candidate_id",
    "family",
    "environment_target",
    "variant",
    "budget_ms",
    "best_multilevel_algo",
    "best_multilevel_cut",
    "best_meta_python_algo",
    "best_meta_python_cut",
    "best_meta_rust_algo",
    "best_meta_rust_cut",
    "best_meta_all_algo",
    "best_meta_all_cut",
    "relative_gap_meta_all_vs_multilevel",
    "confirmation_exception_label",
    "label_claim_status",
]

EXPECTED_ORACLE_COLUMNS = [
    "campaign_id",
    "diagnostic",
    "algo",
    "available_slice_count",
    "mean_median_cut",
    "vbs_mean_median_cut",
    "oracle_gap_vs_vbs",
]


@dataclass(frozen=True)
class CsvProfile:
    """Minimal profile for an input CSV artifact."""

    path: str
    row_count: int
    columns: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit a pre-training gate report for srv-noctua CART."
    )
    parser.add_argument(
        "--bundle",
        type=Path,
        required=True,
        help="Path to srv-noctua evidence bundle.",
    )
    parser.add_argument(
        "--candidate-pool-root",
        type=Path,
        required=True,
        help="Path to exploratory_pool_001 containing candidate bundles.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Local audit output directory. Should be under audit_reports/.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload


def profile_csv(path: Path) -> CsvProfile:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        columns = list(reader.fieldnames or [])
        row_count = sum(1 for _ in reader)
    return CsvProfile(path=str(path), row_count=row_count, columns=columns)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def entropy(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    value = 0.0
    for count in counts.values():
        if count:
            p = count / total
            value -= p * math.log2(p)
    return value


def require_columns(actual: list[str], expected: list[str]) -> list[str]:
    actual_set = set(actual)
    return [column for column in expected if column not in actual_set]


def build_multilevel_sufficiency_target(label: str) -> str:
    if label in {"strong_exception_confirmed", "near_tie_confirmed", "competitive_confirmed"}:
        return "multilevel_not_sufficient_or_not_decisively_dominant"
    if label == "non_exception_confirmed":
        return "multilevel_sufficient"
    return "unknown_or_insufficient"


def to_float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except Exception:
        return None


def discover_graph_metrics(candidate_pool_root: Path) -> dict[str, dict[str, Any]]:
    metrics_by_candidate: dict[str, dict[str, Any]] = {}
    for path in sorted(candidate_pool_root.glob("bundles/*/*/graph_metrics.json")):
        candidate_id = path.parent.name
        metrics = read_json(path)
        metrics_by_candidate[candidate_id] = {
            "metrics_path": str(path),
            **metrics,
        }
    return metrics_by_candidate


def build_feature_table(
    label_rows: list[dict[str, str]],
    metrics_by_candidate: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    missing_metrics: list[str] = []
    missing_features: dict[str, list[str]] = {}
    non_numeric_features: dict[str, dict[str, Any]] = {}
    null_feature_counts: Counter[str] = Counter()

    for label_row in label_rows:
        candidate_id = label_row["candidate_id"]
        metrics = metrics_by_candidate.get(candidate_id)
        if metrics is None:
            missing_metrics.append(candidate_id)
            continue

        out: dict[str, Any] = {
            "candidate_id": candidate_id,
            "family": label_row["family"],
            "environment_target": label_row["environment_target"],
            "variant": label_row["variant"],
            "budget_ms": int(label_row["budget_ms"]),
            "target_multilevel_sufficiency": build_multilevel_sufficiency_target(
                label_row["confirmation_exception_label"]
            ),
        }

        missing_here: list[str] = []
        bad_here: dict[str, Any] = {}

        for column in ALLOWED_FEATURE_COLUMNS:
            raw = metrics.get(column)
            value = to_float_or_none(raw)
            if value is None:
                missing_here.append(column)
                null_feature_counts[column] += 1
            elif raw not in (None, "") and not isinstance(raw, (int, float)):
                try:
                    float(raw)
                except Exception:
                    bad_here[column] = raw
            out[column] = value

        if missing_here:
            missing_features[candidate_id] = missing_here
        if bad_here:
            non_numeric_features[candidate_id] = bad_here

        rows.append(out)

    diagnostics = {
        "row_count": len(rows),
        "candidate_count": len({row["candidate_id"] for row in rows}),
        "missing_metrics_for_label_rows": sorted(set(missing_metrics)),
        "candidates_with_missing_features": missing_features,
        "non_numeric_features": non_numeric_features,
        "null_feature_counts": dict(sorted(null_feature_counts.items())),
    }
    return rows, diagnostics


def build_split_manifest(feature_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build deterministic family-holdout split manifest.

    This is a conservative pretraining split contract, not yet a performance
    claim. Families F01 and F05 are held out based on the audited split-support probe
    927. This deterministic family holdout preserves both target classes in
    train and test while maintaining a family-level leakage boundary. The target
    remains highly imbalanced and any future classifier metric must report that
    limitation explicitly.
    """

    test_families = {"F01", "F05"}
    by_candidate: dict[str, dict[str, Any]] = {}

    for row in feature_rows:
        candidate_id = str(row["candidate_id"])
        family = str(row["family"])
        by_candidate.setdefault(
            candidate_id,
            {
                "candidate_id": candidate_id,
                "family": family,
                "environment_target": str(row["environment_target"]),
                "variant": str(row["variant"]),
                "split": "test" if family in test_families else "train",
                "split_policy": "deterministic_family_holdout_F01_F05",
            },
        )

    return [by_candidate[key] for key in sorted(by_candidate)]


def summarize_split(
    split_manifest: list[dict[str, Any]], feature_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    candidate_split = {row["candidate_id"]: row["split"] for row in split_manifest}
    candidate_family = {row["candidate_id"]: row["family"] for row in split_manifest}

    split_counts = Counter(row["split"] for row in split_manifest)
    family_by_split: dict[str, Counter[str]] = defaultdict(Counter)
    target_by_split: dict[str, Counter[str]] = defaultdict(Counter)

    for row in feature_rows:
        split = candidate_split[str(row["candidate_id"])]
        family_by_split[split][candidate_family[str(row["candidate_id"])]] += 1
        target_by_split[split][str(row["target_multilevel_sufficiency"])] += 1

    return {
        "split_policy": "deterministic_family_holdout_F01_F05",
        "split_unit": "candidate_id",
        "test_families": ["F01", "F05"],
        "candidate_split_counts": dict(sorted(split_counts.items())),
        "family_row_counts_by_split": {
            split: dict(sorted(counter.items()))
            for split, counter in sorted(family_by_split.items())
        },
        "target_row_counts_by_split": {
            split: dict(sorted(counter.items()))
            for split, counter in sorted(target_by_split.items())
        },
        "budget_rows_stay_with_candidate": True,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# srv-noctua CART gatekeeper pretraining report")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Gate result: `{report['gate_result']}`")
    lines.append(f"- Training executed: `{report['training_executed']}`")
    lines.append(f"- Claim status: `{report['claim_status']}`")
    lines.append("")
    lines.append("## Evidence boundary")
    lines.append("")
    for key, value in report["evidence_boundary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Feature contract")
    lines.append("")
    fc = report["feature_contract"]
    lines.append(f"- Feature joining implemented: `{fc['graph_feature_joining_implemented']}`")
    lines.append(f"- Allowed feature columns: `{fc['allowed_feature_columns']}`")
    lines.append(
        f"- Null feature counts: `{fc['feature_join_diagnostics']['null_feature_counts']}`"
    )
    lines.append(
        f"- Missing metrics: `{fc['feature_join_diagnostics']['missing_metrics_for_label_rows']}`"
    )
    lines.append(
        f"- Missing feature candidates: `{fc['feature_join_diagnostics']['candidates_with_missing_features']}`"
    )
    lines.append("")
    lines.append("## Split contract")
    lines.append("")
    split = report["split_contract"]
    lines.append(f"- Split implemented: `{split['split_implemented']}`")
    lines.append(f"- Split policy: `{split['split_summary']['split_policy']}`")
    lines.append(f"- Candidate split counts: `{split['split_summary']['candidate_split_counts']}`")
    lines.append(
        f"- Target row counts by split: `{split['split_summary']['target_row_counts_by_split']}`"
    )
    lines.append("")
    lines.append("## Fixed CART tuple")
    lines.append("")
    lines.append(f"- Parameters: `{report['fixed_cart_parameter_tuple']}`")
    lines.append("")
    lines.append("## Label diagnostics")
    lines.append("")
    label_diag = report["label_diagnostics"]
    lines.append(f"- Label counts: `{label_diag['label_counts']}`")
    lines.append(f"- Candidate target counts: `{label_diag['candidate_target_counts']}`")
    lines.append(f"- Label entropy bits: `{label_diag['label_entropy_bits']}`")
    lines.append("")
    lines.append("## Blocking items before training")
    lines.append("")
    for item in report["blocking_items_before_training"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Explicit non-claims")
    lines.append("")
    for item in report["explicit_non_claims"]:
        lines.append(f"- {item}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    bundle = args.bundle
    output_dir = args.output_dir

    resolved = {name: bundle / rel for name, rel in REQUIRED_FILES.items()}
    missing_files = [str(path) for path in resolved.values() if not path.exists()]

    output_dir.mkdir(parents=True, exist_ok=True)

    if missing_files:
        failure = {
            "gate_result": "fail_missing_required_files",
            "missing_files": missing_files,
            "training_executed": False,
        }
        write_json(output_dir / "gate_report.json", failure)
        return 2

    final_validation = read_json(resolved["final_validation"])
    confirmation_summary = read_json(resolved["confirmation_summary"])

    csv_profiles = {
        name: profile_csv(path).__dict__ for name, path in resolved.items() if path.suffix == ".csv"
    }

    missing_expected_columns = {
        "labels": require_columns(csv_profiles["labels"]["columns"], EXPECTED_LABEL_COLUMNS),
        "oracle": require_columns(csv_profiles["oracle"]["columns"], EXPECTED_ORACLE_COLUMNS),
    }

    label_rows = read_csv_rows(resolved["labels"])
    label_counts = Counter(row.get("confirmation_exception_label", "") for row in label_rows)
    target_counts = Counter(
        build_multilevel_sufficiency_target(row.get("confirmation_exception_label", ""))
        for row in label_rows
    )

    oracle_rows = read_csv_rows(resolved["oracle"])
    metrics_by_candidate = discover_graph_metrics(args.candidate_pool_root)
    feature_rows, feature_join_diagnostics = build_feature_table(label_rows, metrics_by_candidate)
    split_manifest = build_split_manifest(feature_rows)
    split_summary = summarize_split(split_manifest, feature_rows)

    environment_id = str(final_validation.get("environment_id", ""))
    campaign_id = str(final_validation.get("campaign_id", ""))

    blocking_items: list[str] = []
    if environment_id != EXPECTED_ENVIRONMENT_ID:
        blocking_items.append(
            f"Unexpected environment_id: {environment_id!r}; expected {EXPECTED_ENVIRONMENT_ID!r}."
        )
    if campaign_id != EXPECTED_CAMPAIGN_ID:
        blocking_items.append(
            f"Unexpected campaign_id: {campaign_id!r}; expected {EXPECTED_CAMPAIGN_ID!r}."
        )
    if missing_expected_columns["labels"]:
        blocking_items.append("Missing expected columns in confirmation_exception_labels.csv.")
    if missing_expected_columns["oracle"]:
        blocking_items.append("Missing expected columns in sbs_vbs_oracle_gap.csv.")
    if feature_join_diagnostics["missing_metrics_for_label_rows"]:
        blocking_items.append("Some label rows have no graph_metrics.json join.")
    if feature_join_diagnostics["non_numeric_features"]:
        blocking_items.append("Some allowed features are non-numeric.")

    blocking_items.extend(
        [
            "CART training has not yet been executed in this script version.",
            "Any future model result must be interpreted against the deterministic family-holdout split contract.",
            "The current target is highly imbalanced; any classifier metric must report this explicitly.",
        ]
    )

    gate_result = (
        "pass_pretraining_feature_split_contract_ready"
        if not missing_expected_columns["labels"]
        and not missing_expected_columns["oracle"]
        and environment_id == EXPECTED_ENVIRONMENT_ID
        and campaign_id == EXPECTED_CAMPAIGN_ID
        and not feature_join_diagnostics["missing_metrics_for_label_rows"]
        and not feature_join_diagnostics["non_numeric_features"]
        else "fail_pretraining_feature_split_contract"
    )

    report: dict[str, Any] = {
        "gate_result": gate_result,
        "training_executed": False,
        "claim_status": "pretraining_feature_split_contract_only_no_cart_performance_claim",
        "evidence_boundary": {
            "campaign_id": campaign_id,
            "environment_id": environment_id,
            "environment_pooling_status": "forbidden_single_environment_slice_only",
            "bundle": str(bundle),
            "candidate_pool_root": str(args.candidate_pool_root),
            "versioning_boundary": "audit_reports_local_only_not_versioned",
        },
        "validation_summary": {
            "planned_run_count": final_validation.get("planned_run_count"),
            "raw_result_count": final_validation.get("raw_result_count"),
            "valid_result_count": final_validation.get("valid_result_count"),
            "invalid_result_count": final_validation.get("invalid_result_count"),
            "missing_artifact_count": final_validation.get("missing_artifact_count"),
            "schema_error_count_total": final_validation.get("schema_error_count_total"),
            "collapsed_row_count": final_validation.get("collapsed_row_count"),
            "label_row_count": final_validation.get("label_row_count"),
            "monograph_claim_status": final_validation.get("monograph_claim_status"),
        },
        "csv_profiles": csv_profiles,
        "missing_expected_columns": missing_expected_columns,
        "label_diagnostics": {
            "label_row_count": len(label_rows),
            "label_counts": dict(sorted(label_counts.items())),
            "label_entropy_bits": round(entropy(label_counts), 6),
            "candidate_target_name": "multilevel_sufficiency_or_exception",
            "candidate_target_counts": dict(sorted(target_counts.items())),
        },
        "oracle_diagnostics": {
            "sbs_algo": confirmation_summary.get("sbs_algo"),
            "vbs_mean_median_cut": confirmation_summary.get("vbs_mean_median_cut"),
            "oracle_row_count": len(oracle_rows),
        },
        "feature_contract": {
            "graph_feature_joining_implemented": True,
            "allowed_feature_source": "graph_metrics.json from candidate bundles",
            "allowed_feature_columns": ALLOWED_FEATURE_COLUMNS,
            "forbidden_feature_columns": FORBIDDEN_FEATURE_COLUMNS,
            "feature_join_diagnostics": feature_join_diagnostics,
        },
        "split_contract": {
            "split_implemented": True,
            "split_summary": split_summary,
        },
        "fixed_cart_parameter_tuple": FIXED_CART_PARAMETER_TUPLE,
        "blocking_items_before_training": blocking_items,
        "explicit_non_claims": [
            "This report does not train CART.",
            "This report does not authorize a universal solver selector claim.",
            "This report does not authorize environment-pooled conclusions.",
            "This report does not update monograph prose.",
            "This report does not version audit_reports artifacts.",
        ],
    }

    feature_fieldnames = [
        "candidate_id",
        "family",
        "environment_target",
        "variant",
        "budget_ms",
        *ALLOWED_FEATURE_COLUMNS,
        "target_multilevel_sufficiency",
    ]
    split_fieldnames = [
        "candidate_id",
        "family",
        "environment_target",
        "variant",
        "split",
        "split_policy",
    ]

    write_json(output_dir / "gate_report.json", report)
    write_markdown(output_dir / "gate_report.md", report)
    write_csv(output_dir / "cart_feature_table.csv", feature_rows, feature_fieldnames)
    write_json(output_dir / "cart_feature_table.json", feature_rows)
    write_csv(output_dir / "split_manifest.csv", split_manifest, split_fieldnames)
    write_json(output_dir / "split_manifest.json", split_manifest)
    write_json(
        output_dir / "allowed_feature_manifest.json",
        {
            "allowed_feature_columns": ALLOWED_FEATURE_COLUMNS,
            "forbidden_feature_columns": FORBIDDEN_FEATURE_COLUMNS,
            "fixed_cart_parameter_tuple": FIXED_CART_PARAMETER_TUPLE,
            "target": "multilevel_sufficiency_or_exception",
        },
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
