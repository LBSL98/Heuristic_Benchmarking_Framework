#!/usr/bin/env python3
"""Validate exception-mining generated-instance artifact bundles.

The validator enforces the repository contract in
``decisions/13_Exception_Mining_Instance_Generation_Contract.md``.

It intentionally validates one generated-instance bundle at a time. Campaign-level
manifests are validated by later pipeline stages.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_FILES = [
    "instance.json.gz",
    "generator_config.json",
    "generator_log.jsonl",
    "README.md",
    "graph_metrics.json",
    "manifest_row.json",
    "manifest_row.csv",
    "graph_edges.edgelist",
    "graph_metis.graph",
    "graph_preview_layout.json",
    "graph_preview_sample.json",
    "visualization_metadata.json",
    "sha256sums.txt",
]

INSTANCE_REQUIRED_KEYS = [
    "nodes",
    "edges",
    "schema_version",
    "epsilon",
    "instance_id",
    "generator",
    "seed",
    "created_at",
    "instance_metrics",
]

GENERATOR_CONFIG_REQUIRED_KEYS = [
    "generator_family",
    "graph_parameters",
    "seed",
    "target_regime",
    "target_morphology",
    "intended_hypothesis",
    "k",
    "balance_tolerance",
    "code_commit",
    "generator_version",
    "environment",
]

VALID_LIFECYCLE_STATES = {
    "generated",
    "schema_validated",
    "metric_validated",
    "screened",
    "selected_candidate",
    "confirmation_running",
    "confirmed_exception",
    "confirmed_non_exception",
    "holdout_reserved",
    "holdout_validated",
    "rejected_schema",
    "rejected_metrics",
    "rejected_duplicate",
    "rejected_size",
    "rejected_runtime",
    "rejected_other",
}

METRIC_ALIASES = {
    "num_vertices": ["num_vertices", "num_nodes", "n", "|V|"],
    "num_edges": ["num_edges", "m", "|E|"],
    "density": ["density", "density_undirected"],
    "average_degree": ["average_degree", "avg_degree", "avg_degree_undirected"],
    "degree_min": ["degree_min", "min_degree"],
    "degree_max": ["degree_max", "max_degree"],
    "degree_mean": ["degree_mean", "mean_degree"],
    "degree_std": ["degree_std", "std_degree"],
    "degree_cv": ["degree_cv", "cv_degree", "degree_coefficient_of_variation"],
    "connected_component_count": ["connected_component_count", "num_components", "components"],
    "largest_component_size": ["largest_component_size", "gcc_size"],
}


def _new_report(bundle_path: Path) -> dict[str, Any]:
    return {
        "bundle_path": str(bundle_path),
        "valid": False,
        "errors": [],
        "warnings": [],
        "checked_files": [],
    }


def _error(report: dict[str, Any], message: str) -> None:
    report["errors"].append(message)


def _warning(report: dict[str, Any], message: str) -> None:
    report["warnings"].append(message)


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def _read_instance(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("instance.json.gz must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _parse_sha256sums(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"invalid sha256sums.txt line {line_no}: {raw_line!r}")
        digest, filename = parts[0], parts[-1]
        if len(digest) != 64 or any(char not in "0123456789abcdefABCDEF" for char in digest):
            raise ValueError(f"invalid sha256 digest at line {line_no}: {digest!r}")
        entries[filename] = digest.lower()
    return entries


def _find_metric(metrics: dict[str, Any], logical_name: str) -> Any:
    aliases = METRIC_ALIASES[logical_name]
    for alias in aliases:
        if alias in metrics and metrics[alias] not in (None, ""):
            return metrics[alias]
    return None


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _non_comment_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _validate_required_files(bundle_path: Path, report: dict[str, Any]) -> None:
    if not bundle_path.exists():
        _error(report, f"bundle path does not exist: {bundle_path}")
        return
    if not bundle_path.is_dir():
        _error(report, f"bundle path is not a directory: {bundle_path}")
        return

    for filename in REQUIRED_FILES:
        file_path = bundle_path / filename
        if file_path.exists():
            report["checked_files"].append(filename)
        else:
            _error(report, f"missing required file: {filename}")


def _validate_hashes(bundle_path: Path, report: dict[str, Any]) -> None:
    sums_path = bundle_path / "sha256sums.txt"
    if not sums_path.exists():
        return

    try:
        entries = _parse_sha256sums(sums_path)
    except ValueError as exc:
        _error(report, str(exc))
        return

    for filename in REQUIRED_FILES:
        if filename == "sha256sums.txt":
            continue
        file_path = bundle_path / filename
        if not file_path.exists():
            continue
        expected = entries.get(filename)
        if expected is None:
            _error(report, f"missing hash entry for required file: {filename}")
            continue
        actual = _sha256(file_path)
        if actual != expected:
            _error(report, f"hash mismatch for {filename}: expected {expected}, got {actual}")


def _validate_instance(
    bundle_path: Path, report: dict[str, Any]
) -> tuple[dict[str, Any] | None, int, int]:
    path = bundle_path / "instance.json.gz"
    if not path.exists():
        return None, 0, 0

    try:
        instance = _read_instance(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        _error(report, f"invalid instance.json.gz: {exc}")
        return None, 0, 0

    for key in INSTANCE_REQUIRED_KEYS:
        if key not in instance:
            _error(report, f"instance.json.gz missing key: {key}")

    nodes = instance.get("nodes")
    edges = instance.get("edges")
    if not isinstance(nodes, list):
        _error(report, "instance.json.gz key 'nodes' must be a list")
        nodes = []
    if not isinstance(edges, list):
        _error(report, "instance.json.gz key 'edges' must be a list")
        edges = []

    node_count = len(nodes)
    edge_count = len(edges)

    for index, edge in enumerate(edges):
        if not isinstance(edge, list) or len(edge) < 2:
            _error(report, f"edge at index {index} must be a list with at least two endpoints")
            continue
        if not isinstance(edge[0], int) or not isinstance(edge[1], int):
            _error(report, f"edge at index {index} endpoints must be integers")

    metrics = instance.get("instance_metrics")
    if metrics is not None and not isinstance(metrics, dict):
        _error(report, "instance.json.gz key 'instance_metrics' must be an object")

    return instance, node_count, edge_count


def _validate_generator_config(
    bundle_path: Path, report: dict[str, Any], instance: dict[str, Any] | None
) -> None:
    path = bundle_path / "generator_config.json"
    if not path.exists():
        return

    try:
        config = _read_json(path)
    except (json.JSONDecodeError, ValueError) as exc:
        _error(report, f"invalid generator_config.json: {exc}")
        return

    for key in GENERATOR_CONFIG_REQUIRED_KEYS:
        if key not in config:
            _error(report, f"generator_config.json missing key: {key}")

    if not isinstance(config.get("graph_parameters", {}), dict):
        _error(report, "generator_config.json key 'graph_parameters' must be an object")
    if not isinstance(config.get("environment", {}), dict):
        _error(report, "generator_config.json key 'environment' must be an object")

    if (
        instance is not None
        and "seed" in instance
        and "seed" in config
        and str(instance["seed"]) != str(config["seed"])
    ):
        _error(report, "seed mismatch between instance.json.gz and generator_config.json")


def _validate_generator_log(bundle_path: Path, report: dict[str, Any]) -> None:
    path = bundle_path / "generator_log.jsonl"
    if not path.exists():
        return

    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        _error(report, "generator_log.jsonl must contain at least one JSON line")
        return

    for line_no, line in enumerate(lines, start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            _error(report, f"invalid generator_log.jsonl line {line_no}: {exc}")
            continue
        if not isinstance(entry, dict):
            _error(report, f"generator_log.jsonl line {line_no} must be a JSON object")
            continue
        if not any(key in entry for key in ("event", "status", "lifecycle_state")):
            _error(report, f"generator_log.jsonl line {line_no} lacks event/status/lifecycle_state")


def _validate_graph_metrics(
    bundle_path: Path, report: dict[str, Any], node_count: int, edge_count: int
) -> None:
    path = bundle_path / "graph_metrics.json"
    if not path.exists():
        return

    try:
        metrics = _read_json(path)
    except (json.JSONDecodeError, ValueError) as exc:
        _error(report, f"invalid graph_metrics.json: {exc}")
        return

    for logical_name in METRIC_ALIASES:
        if _find_metric(metrics, logical_name) is None:
            _error(report, f"graph_metrics.json missing metric or alias: {logical_name}")

    metric_nodes = _as_int(_find_metric(metrics, "num_vertices"))
    metric_edges = _as_int(_find_metric(metrics, "num_edges"))

    if metric_nodes is not None and node_count and metric_nodes != node_count:
        _error(report, f"graph_metrics vertex count mismatch: {metric_nodes} != {node_count}")
    if metric_edges is not None and metric_edges != edge_count:
        _error(report, f"graph_metrics edge count mismatch: {metric_edges} != {edge_count}")


def _validate_manifest(
    bundle_path: Path, report: dict[str, Any], instance: dict[str, Any] | None
) -> None:
    json_path = bundle_path / "manifest_row.json"
    csv_path = bundle_path / "manifest_row.csv"

    manifest_json: dict[str, Any] | None = None
    if json_path.exists():
        try:
            manifest_json = _read_json(json_path)
        except (json.JSONDecodeError, ValueError) as exc:
            _error(report, f"invalid manifest_row.json: {exc}")

    if manifest_json is not None:
        for key in ("campaign_id", "instance_id", "lifecycle_state", "bundle_path"):
            if key not in manifest_json:
                _error(report, f"manifest_row.json missing key: {key}")

        state = manifest_json.get("lifecycle_state")
        if state not in VALID_LIFECYCLE_STATES:
            _error(report, f"invalid lifecycle_state in manifest_row.json: {state!r}")

        if instance is not None and manifest_json.get("instance_id") != instance.get("instance_id"):
            _error(report, "instance_id mismatch between instance.json.gz and manifest_row.json")

    if csv_path.exists():
        try:
            with csv_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        except csv.Error as exc:
            _error(report, f"invalid manifest_row.csv: {exc}")
            rows = []

        if len(rows) != 1:
            _error(report, f"manifest_row.csv must contain exactly one data row, found {len(rows)}")
        elif manifest_json is not None:
            row = rows[0]
            for key in ("campaign_id", "instance_id", "lifecycle_state"):
                if row.get(key) != str(manifest_json.get(key)):
                    _error(report, f"manifest_row.csv mismatch for {key}")


def _validate_edgelist(bundle_path: Path, report: dict[str, Any], edge_count: int) -> None:
    path = bundle_path / "graph_edges.edgelist"
    if not path.exists():
        return

    lines = _non_comment_lines(path)
    if len(lines) != edge_count:
        _error(report, f"graph_edges.edgelist line count mismatch: {len(lines)} != {edge_count}")

    for line_no, line in enumerate(lines, start=1):
        parts = line.split()
        if len(parts) < 2:
            _error(report, f"graph_edges.edgelist line {line_no} has fewer than two columns")
            continue
        try:
            int(parts[0])
            int(parts[1])
        except ValueError:
            _error(report, f"graph_edges.edgelist line {line_no} endpoints must be integers")


def _validate_metis_graph(
    bundle_path: Path, report: dict[str, Any], node_count: int, edge_count: int
) -> None:
    path = bundle_path / "graph_metis.graph"
    if not path.exists():
        return

    lines = _non_comment_lines(path)
    if not lines:
        _error(report, "graph_metis.graph is empty")
        return

    header = lines[0].split()
    if len(header) < 2:
        _error(report, "graph_metis.graph header must contain at least n and m")
        return

    try:
        metis_n = int(header[0])
        metis_m = int(header[1])
    except ValueError:
        _error(report, "graph_metis.graph header n and m must be integers")
        return

    if metis_n != node_count:
        _error(report, f"graph_metis.graph vertex count mismatch: {metis_n} != {node_count}")
    if metis_m != edge_count:
        _error(report, f"graph_metis.graph edge count mismatch: {metis_m} != {edge_count}")


def _validate_visualization(bundle_path: Path, report: dict[str, Any]) -> None:
    layout_path = bundle_path / "graph_preview_layout.json"
    sample_path = bundle_path / "graph_preview_sample.json"
    metadata_path = bundle_path / "visualization_metadata.json"

    if layout_path.exists():
        try:
            layout = _read_json(layout_path)
        except (json.JSONDecodeError, ValueError) as exc:
            _error(report, f"invalid graph_preview_layout.json: {exc}")
            layout = {}
        for key in (
            "layout_algorithm",
            "layout_seed",
            "layout_parameters",
            "layout_scope",
            "node_positions",
        ):
            if key not in layout:
                _error(report, f"graph_preview_layout.json missing key: {key}")
        if "node_positions" in layout and not isinstance(layout["node_positions"], dict | list):
            _error(
                report, "graph_preview_layout.json key 'node_positions' must be an object or list"
            )

    if sample_path.exists():
        try:
            sample = _read_json(sample_path)
        except (json.JSONDecodeError, ValueError) as exc:
            _error(report, f"invalid graph_preview_sample.json: {exc}")
            sample = {}
        for key in ("sampling_policy", "sample_seed", "sampled_nodes", "sampled_edges"):
            if key not in sample:
                _error(report, f"graph_preview_sample.json missing key: {key}")
        if "sampled_nodes" in sample and not isinstance(sample["sampled_nodes"], list):
            _error(report, "graph_preview_sample.json key 'sampled_nodes' must be a list")
        if "sampled_edges" in sample and not isinstance(sample["sampled_edges"], list):
            _error(report, "graph_preview_sample.json key 'sampled_edges' must be a list")

    if metadata_path.exists():
        try:
            metadata = _read_json(metadata_path)
        except (json.JSONDecodeError, ValueError) as exc:
            _error(report, f"invalid visualization_metadata.json: {exc}")
            metadata = {}
        encodings = metadata.get("available_encodings")
        if not isinstance(encodings, list):
            _error(report, "visualization_metadata.json key 'available_encodings' must be a list")
        elif "degree" not in encodings:
            _error(
                report, "visualization_metadata.json must include 'degree' in available_encodings"
            )


def _validate_readme(bundle_path: Path, report: dict[str, Any]) -> None:
    path = bundle_path / "README.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8").strip()
    if len(text) < 40:
        _error(report, "README.md is too short to explain the generated instance")
    for needle in ("hypothesis", "generator", "topology"):
        if needle not in text.lower():
            _warning(report, f"README.md does not mention {needle!r}")


def validate_bundle(bundle_path: Path) -> dict[str, Any]:
    """Validate a generated-instance bundle and return a machine-readable report."""
    bundle_path = bundle_path.resolve()
    report = _new_report(bundle_path)

    _validate_required_files(bundle_path, report)
    instance, node_count, edge_count = _validate_instance(bundle_path, report)
    _validate_generator_config(bundle_path, report, instance)
    _validate_generator_log(bundle_path, report)
    _validate_graph_metrics(bundle_path, report, node_count, edge_count)
    _validate_manifest(bundle_path, report, instance)
    _validate_edgelist(bundle_path, report, edge_count)
    _validate_metis_graph(bundle_path, report, node_count, edge_count)
    _validate_visualization(bundle_path, report)
    _validate_readme(bundle_path, report)
    _validate_hashes(bundle_path, report)

    report["valid"] = len(report["errors"]) == 0
    return report


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bundle",
        type=Path,
        help="Path to one generated exception-mining instance bundle.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path where the validation report should be written as JSON.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Do not print the validation report to stdout.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    report = validate_bundle(args.bundle)

    report_json = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(report_json + "\n", encoding="utf-8")

    if not args.quiet:
        print(report_json)

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
