from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_exception_mining_bundle.py"


def load_validator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_exception_mining_bundle", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_instance(path: Path, payload: dict[str, Any]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def write_hashes(bundle: Path) -> None:
    filenames = [
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
    ]
    lines = [f"{sha256(bundle / filename)}  {filename}" for filename in filenames]
    (bundle / "sha256sums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_valid_bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / "valid_bundle"
    bundle.mkdir()

    instance = {
        "schema_version": "exception-mining-test-v1",
        "epsilon": 0.03,
        "instance_id": "F99_test_seed1001",
        "generator": "unit_test_generator",
        "seed": 1001,
        "created_at": "2026-05-05T00:00:00Z",
        "nodes": [0, 1, 2, 3],
        "edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
        "instance_metrics": {"num_vertices": 4, "num_edges": 4},
    }
    write_instance(bundle / "instance.json.gz", instance)

    write_json(
        bundle / "generator_config.json",
        {
            "generator_family": "F99_unit_test",
            "graph_parameters": {"n": 4, "m": 4},
            "seed": 1001,
            "target_regime": "unit",
            "target_morphology": "cycle",
            "intended_hypothesis": "validator smoke test",
            "k": 2,
            "balance_tolerance": 0.03,
            "code_commit": "deadbeef",
            "generator_version": "0.0-test",
            "environment": {"python": "test"},
        },
    )

    (bundle / "generator_log.jsonl").write_text(
        json.dumps({"event": "generated", "instance_id": "F99_test_seed1001"}) + "\n",
        encoding="utf-8",
    )

    (bundle / "README.md").write_text(
        "Generator unit_test_generator created this topology to test the validation hypothesis.\n",
        encoding="utf-8",
    )

    write_json(
        bundle / "graph_metrics.json",
        {
            "num_vertices": 4,
            "num_edges": 4,
            "density": 0.6666666667,
            "average_degree": 2.0,
            "degree_min": 2,
            "degree_max": 2,
            "degree_mean": 2.0,
            "degree_std": 0.0,
            "degree_cv": 0.0,
            "connected_component_count": 1,
            "largest_component_size": 4,
        },
    )

    write_json(
        bundle / "manifest_row.json",
        {
            "campaign_id": "EXP-MULTILEVEL-EXCEPTION-MINING-001",
            "instance_id": "F99_test_seed1001",
            "lifecycle_state": "generated",
            "bundle_path": str(bundle),
        },
    )

    (bundle / "manifest_row.csv").write_text(
        "campaign_id,instance_id,lifecycle_state,bundle_path\n"
        f"EXP-MULTILEVEL-EXCEPTION-MINING-001,F99_test_seed1001,generated,{bundle}\n",
        encoding="utf-8",
    )

    (bundle / "graph_edges.edgelist").write_text(
        "0 1\n1 2\n2 3\n3 0\n",
        encoding="utf-8",
    )

    (bundle / "graph_metis.graph").write_text(
        "4 4\n2 4\n1 3\n2 4\n1 3\n",
        encoding="utf-8",
    )

    write_json(
        bundle / "graph_preview_layout.json",
        {
            "layout_algorithm": "fixed_unit_square",
            "layout_seed": 1001,
            "layout_parameters": {"scale": 1.0},
            "layout_scope": "full",
            "node_positions": {
                "0": [0.0, 0.0],
                "1": [1.0, 0.0],
                "2": [1.0, 1.0],
                "3": [0.0, 1.0],
            },
        },
    )

    write_json(
        bundle / "graph_preview_sample.json",
        {
            "sampling_policy": "full_graph",
            "sample_seed": 1001,
            "sampled_nodes": [0, 1, 2, 3],
            "sampled_edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
        },
    )

    write_json(
        bundle / "visualization_metadata.json",
        {
            "available_encodings": ["degree", "connected_component_id"],
            "notes": "unit test visualization metadata",
        },
    )

    write_hashes(bundle)
    return bundle


def test_valid_bundle_passes(tmp_path: Path) -> None:
    validator = load_validator_module()
    bundle = make_valid_bundle(tmp_path)

    report = validator.validate_bundle(bundle)

    assert report["valid"] is True
    assert report["errors"] == []


def test_missing_required_visualization_file_fails(tmp_path: Path) -> None:
    validator = load_validator_module()
    bundle = make_valid_bundle(tmp_path)
    (bundle / "visualization_metadata.json").unlink()

    report = validator.validate_bundle(bundle)

    assert report["valid"] is False
    assert any(
        "missing required file: visualization_metadata.json" in error for error in report["errors"]
    )


def test_hash_mismatch_fails(tmp_path: Path) -> None:
    validator = load_validator_module()
    bundle = make_valid_bundle(tmp_path)
    (bundle / "README.md").write_text(
        "Generator unit_test_generator changed this topology after hashes were written.\n",
        encoding="utf-8",
    )

    report = validator.validate_bundle(bundle)

    assert report["valid"] is False
    assert any("hash mismatch for README.md" in error for error in report["errors"])


def test_cli_writes_report_and_returns_nonzero_on_invalid_bundle(tmp_path: Path) -> None:
    bundle = make_valid_bundle(tmp_path)
    (bundle / "graph_edges.edgelist").write_text("0 1\n", encoding="utf-8")
    output = tmp_path / "report.json"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(bundle), "--json-out", str(output), "--quiet"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["valid"] is False
    assert any("graph_edges.edgelist line count mismatch" in error for error in report["errors"])
