#!/usr/bin/env python3
"""Train the first bounded CART gatekeeper for srv-noctua evidence.

This script consumes the pretraining artifacts produced by
run_srv_noctua_cart_gatekeeper.py. It is intentionally claim-bounded:
it trains a fixed CART under the audited split and writes local audit reports;
it does not authorize universal selector claims or monograph prose.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

GRAPH_FEATURE_COLUMNS = [
    "num_vertices",
    "num_edges",
    "density",
    "degree_cv",
    "modularity",
    "connected_component_count",
    "largest_component_size",
]

CONTEXT_FEATURE_COLUMNS = [
    "budget_ms",
]

MODEL_FEATURE_COLUMNS = CONTEXT_FEATURE_COLUMNS + GRAPH_FEATURE_COLUMNS

TARGET_COLUMN = "target_multilevel_sufficiency"

CLASS_LABELS = [
    "multilevel_not_sufficient_or_not_decisively_dominant",
    "multilevel_sufficient",
]

FIXED_CART_PARAMETER_TUPLE = {
    "criterion": "gini",
    "max_depth": 3,
    "min_samples_leaf": 3,
    "min_samples_split": 6,
    "random_state": 20260516,
    "class_weight": None,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train fixed CART gatekeeper on srv-noctua audited split."
    )
    parser.add_argument("--feature-table", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--gate-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


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


def to_float(value: str) -> float | None:
    if value in ("", "None", "null", "NULL"):
        return None
    return float(value)


def load_dataset(
    feature_table: Path,
    split_manifest: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    feature_rows_raw = read_csv_dicts(feature_table)
    split_rows = read_csv_dicts(split_manifest)

    split_by_candidate = {row["candidate_id"]: row for row in split_rows}

    missing_split = sorted(
        {
            row["candidate_id"]
            for row in feature_rows_raw
            if row["candidate_id"] not in split_by_candidate
        }
    )
    if missing_split:
        raise ValueError(f"feature rows without split manifest entries: {missing_split[:20]}")

    rows: list[dict[str, Any]] = []
    for row in feature_rows_raw:
        candidate_id = row["candidate_id"]
        split_row = split_by_candidate[candidate_id]
        out: dict[str, Any] = {
            "candidate_id": candidate_id,
            "family": row["family"],
            "environment_target": row["environment_target"],
            "variant": row["variant"],
            "split": split_row["split"],
            TARGET_COLUMN: row[TARGET_COLUMN],
        }
        for column in MODEL_FEATURE_COLUMNS:
            out[column] = to_float(row[column])
        rows.append(out)

    split_summary = {
        "candidate_split_counts": dict(Counter(row["split"] for row in split_rows)),
        "row_split_counts": dict(Counter(row["split"] for row in rows)),
        "target_counts_by_split": {
            split: dict(Counter(row[TARGET_COLUMN] for row in rows if row["split"] == split))
            for split in sorted({row["split"] for row in rows})
        },
        "family_counts_by_split": {
            split: dict(Counter(row["family"] for row in rows if row["split"] == split))
            for split in sorted({row["split"] for row in rows})
        },
        "split_policy_values": sorted({row.get("split_policy", "") for row in split_rows}),
    }

    return rows, split_summary


def make_matrix(rows: list[dict[str, Any]]):
    import numpy as np

    x = np.array(
        [[row[column] for column in MODEL_FEATURE_COLUMNS] for row in rows],
        dtype=float,
    )
    y = np.array([row[TARGET_COLUMN] for row in rows], dtype=object)
    return x, y


def majority_baseline(
    train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]
) -> list[str]:
    counts = Counter(row[TARGET_COLUMN] for row in train_rows)
    majority = counts.most_common(1)[0][0]
    return [majority for _ in eval_rows]


def compute_metrics(y_true, y_pred) -> dict[str, Any]:
    from sklearn.metrics import (
        accuracy_score,
        balanced_accuracy_score,
        classification_report,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
    )

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "macro_precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "confusion_matrix_labels": CLASS_LABELS,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=CLASS_LABELS).tolist(),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=CLASS_LABELS,
            output_dict=True,
            zero_division=0,
        ),
        "prediction_counts": dict(Counter(str(label) for label in y_pred)),
        "true_counts": dict(Counter(str(label) for label in y_true)),
    }


def train_and_evaluate(
    rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.tree import DecisionTreeClassifier, export_text

    train_rows = [row for row in rows if row["split"] == "train"]
    test_rows = [row for row in rows if row["split"] == "test"]

    if not train_rows or not test_rows:
        raise ValueError("train/test split must both be non-empty")

    train_targets = Counter(row[TARGET_COLUMN] for row in train_rows)
    test_targets = Counter(row[TARGET_COLUMN] for row in test_rows)

    if len(train_targets) < 2 or len(test_targets) < 2:
        raise ValueError(
            f"train and test must both contain both target classes; "
            f"train={dict(train_targets)}, test={dict(test_targets)}"
        )

    x_train, y_train = make_matrix(train_rows)
    x_test, y_test = make_matrix(test_rows)

    pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("cart", DecisionTreeClassifier(**FIXED_CART_PARAMETER_TUPLE)),
        ]
    )
    pipeline.fit(x_train, y_train)

    train_pred = pipeline.predict(x_train)
    test_pred = pipeline.predict(x_test)

    baseline_train_pred = majority_baseline(train_rows, train_rows)
    baseline_test_pred = majority_baseline(train_rows, test_rows)

    model = pipeline.named_steps["cart"]
    tree_text = export_text(model, feature_names=MODEL_FEATURE_COLUMNS)

    feature_importances = {
        feature: float(importance)
        for feature, importance in zip(
            MODEL_FEATURE_COLUMNS, model.feature_importances_, strict=False
        )
    }

    predictions: list[dict[str, Any]] = []
    for source_rows, y_pred in [(train_rows, train_pred), (test_rows, test_pred)]:
        for row, pred in zip(source_rows, y_pred, strict=False):
            predictions.append(
                {
                    "candidate_id": row["candidate_id"],
                    "family": row["family"],
                    "environment_target": row["environment_target"],
                    "variant": row["variant"],
                    "budget_ms": int(row["budget_ms"]),
                    "split": row["split"],
                    "target": row[TARGET_COLUMN],
                    "prediction": str(pred),
                    "correct": str(row[TARGET_COLUMN] == str(pred)),
                }
            )

    report = {
        "training_executed": True,
        "claim_status": "bounded_first_cart_training_no_universal_selector_claim",
        "target": TARGET_COLUMN,
        "target_interpretation": "budget-row multilevel sufficiency/exception gate",
        "model_feature_columns": MODEL_FEATURE_COLUMNS,
        "graph_feature_columns": GRAPH_FEATURE_COLUMNS,
        "context_feature_columns": CONTEXT_FEATURE_COLUMNS,
        "fixed_cart_parameter_tuple": FIXED_CART_PARAMETER_TUPLE,
        "preprocessing": {
            "imputer": "SimpleImputer(strategy='median')",
            "reason": "modularity contains null values in part of the audited feature table",
        },
        "split_policy": "deterministic_family_holdout_F01_F05",
        "metrics": {
            "train": compute_metrics(y_train, train_pred),
            "test": compute_metrics(y_test, test_pred),
            "majority_baseline_train": compute_metrics(y_train, baseline_train_pred),
            "majority_baseline_test": compute_metrics(y_test, baseline_test_pred),
        },
        "feature_importances": feature_importances,
        "warnings": [
            "The target is highly imbalanced.",
            "The training split contains only 3 multilevel_sufficient rows.",
            "The test split contains 8 multilevel_sufficient rows, all from held-out F05.",
            "This is a bounded diagnostic gatekeeper model, not a universal solver selector.",
            "No monograph prose should be updated until results are mapped in decisions/08_Results_to_Text_Map.md.",
        ],
    }

    return report, predictions, tree_text


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# First srv-noctua CART gatekeeper training report")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Training executed: `{report['training_executed']}`")
    lines.append(f"- Claim status: `{report['claim_status']}`")
    lines.append(f"- Target: `{report['target']}`")
    lines.append(f"- Target interpretation: `{report['target_interpretation']}`")
    lines.append(f"- Split policy: `{report['split_policy']}`")
    lines.append("")
    lines.append("## Features and preprocessing")
    lines.append("")
    lines.append(f"- Model feature columns: `{report['model_feature_columns']}`")
    lines.append(f"- Graph feature columns: `{report['graph_feature_columns']}`")
    lines.append(f"- Context feature columns: `{report['context_feature_columns']}`")
    lines.append(f"- Fixed CART tuple: `{report['fixed_cart_parameter_tuple']}`")
    lines.append(f"- Preprocessing: `{report['preprocessing']}`")
    lines.append("")
    lines.append("## Test metrics")
    lines.append("")
    test = report["metrics"]["test"]
    baseline = report["metrics"]["majority_baseline_test"]
    lines.append(f"- CART accuracy: `{test['accuracy']}`")
    lines.append(f"- CART balanced accuracy: `{test['balanced_accuracy']}`")
    lines.append(f"- CART macro F1: `{test['macro_f1']}`")
    lines.append(f"- CART confusion matrix labels: `{test['confusion_matrix_labels']}`")
    lines.append(f"- CART confusion matrix: `{test['confusion_matrix']}`")
    lines.append(f"- Majority baseline accuracy: `{baseline['accuracy']}`")
    lines.append(f"- Majority baseline balanced accuracy: `{baseline['balanced_accuracy']}`")
    lines.append(f"- Majority baseline macro F1: `{baseline['macro_f1']}`")
    lines.append(f"- Majority baseline confusion matrix: `{baseline['confusion_matrix']}`")
    lines.append("")
    lines.append("## Feature importances")
    lines.append("")
    for feature, value in sorted(report["feature_importances"].items()):
        lines.append(f"- `{feature}`: `{value}`")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    for warning in report["warnings"]:
        lines.append(f"- {warning}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    gate_report = json.loads(args.gate_report.read_text(encoding="utf-8"))
    if gate_report.get("gate_result") != "pass_pretraining_feature_split_contract_ready":
        raise ValueError(
            "gate report is not ready for bounded training: " + repr(gate_report.get("gate_result"))
        )

    rows, split_summary = load_dataset(args.feature_table, args.split_manifest)
    training_report, predictions, tree_text = train_and_evaluate(rows)

    output = {
        "input_gate_report": str(args.gate_report),
        "feature_table": str(args.feature_table),
        "split_manifest": str(args.split_manifest),
        "split_summary": split_summary,
        **training_report,
    }

    write_json(args.output_dir / "cart_training_report.json", output)
    write_markdown(args.output_dir / "cart_training_report.md", output)
    (args.output_dir / "cart_tree.txt").write_text(tree_text, encoding="utf-8")
    write_csv(
        args.output_dir / "cart_predictions.csv",
        predictions,
        [
            "candidate_id",
            "family",
            "environment_target",
            "variant",
            "budget_ms",
            "split",
            "target",
            "prediction",
            "correct",
        ],
    )

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
