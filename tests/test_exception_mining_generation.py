from __future__ import annotations

import gzip
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from exception_mining.generation import generate_bundle, generate_graph

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_exception_mining_bundle.py"
CLI_PATH = REPO_ROOT / "scripts" / "generate_exception_mining_instances.py"


def load_validator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "validate_exception_mining_bundle", VALIDATOR_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SMALL_PARAMS: dict[str, dict[str, Any]] = {
    "F01": {"n": 48, "communities": 4, "target_avg_degree": 6},
    "F02": {"module_count": 4, "module_size": 12, "inter_module_edges": 1},
    "F03": {"left_core_size": 20, "right_core_size": 20, "bridge_length": 5, "bridge_width": 1},
    "F04": {"n": 60, "attachment_m": 2, "hub_noise_edges": 0.02},
    "F05": {"n": 60, "core_fraction": 0.25},
    "F06": {"n_approx": 64, "grid_shape": "square", "shortcut_rate": 0.02},
    "F07": {"n": 50, "edge_density": 0.08, "planted_signal": 0.02},
    "F08": {"n": 60, "planted_blocks": 5, "block_size_skew": 0.2},
}


def test_all_exception_mining_families_generate_connected_graphs() -> None:
    for index, (family, params) in enumerate(SMALL_PARAMS.items(), start=1):
        generated = generate_graph(family=family, seed=1000 + index, parameters=params)
        assert generated.graph.number_of_nodes() > 0
        assert generated.graph.number_of_edges() > 0
        assert generated.family == family


def test_generated_bundle_passes_validator_for_all_families(tmp_path: Path) -> None:
    validator = load_validator_module()

    for index, (family, params) in enumerate(SMALL_PARAMS.items(), start=1):
        bundle = generate_bundle(
            family=family,
            seed=1000 + index,
            output_root=tmp_path,
            parameters=params,
            instance_id=f"{family.lower()}_unit_test",
        )
        report = validator.validate_bundle(bundle)

        assert report["valid"] is True, report["errors"]
        assert (bundle / "instance.json.gz").exists()
        assert (bundle / "graph_metis.graph").exists()
        assert (bundle / "sha256sums.txt").exists()


def test_bundle_instance_payload_remains_runner_compatible(tmp_path: Path) -> None:
    bundle = generate_bundle(
        family="F01",
        seed=1001,
        output_root=tmp_path,
        parameters=SMALL_PARAMS["F01"],
        instance_id="runner_compatible",
    )

    with gzip.open(bundle / "instance.json.gz", "rt", encoding="utf-8") as handle:
        payload = json.load(handle)

    assert isinstance(payload["nodes"], list)
    assert isinstance(payload["edges"], list)
    assert payload["instance_id"] == "runner_compatible"
    assert payload["generator"] == "exception_mining_f01"
    assert payload["seed"] == 1001
    assert "num_vertices" in payload["instance_metrics"]
    assert "num_edges" in payload["instance_metrics"]


def test_cli_generates_and_validates_bundle(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "--family",
            "F02",
            "--seed",
            "1002",
            "--output-root",
            str(tmp_path),
            "--instance-id",
            "cli_smoke",
            "--params-json",
            json.dumps(SMALL_PARAMS["F02"]),
            "--validate",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    bundle = Path(payload["bundle_dir"])
    assert bundle.exists()
    assert (bundle / "manifest_row.json").exists()
