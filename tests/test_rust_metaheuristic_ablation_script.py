import gzip
import json
import shutil
from pathlib import Path

import pytest

from scripts.run_rust_metaheuristic_ablation import default_profiles, run_ablation


def _write_instance(path: Path, n: int) -> None:
    edges = [[i, i + 1] for i in range(n - 1)]
    payload = {"instance_id": path.name.removesuffix(".json.gz"), "num_nodes": n, "edges": edges}
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(payload, f)


def test_default_profiles_use_frozen_d012_values():
    profiles = {profile.family: profile for profile in default_profiles()}

    assert profiles["sa"].params == {
        "initial_temp": 1.0,
        "cooling": 0.997,
        "min_temp": 0.001,
        "max_steps": 100_000,
        "checkpoint_every_nfe": 100,
    }
    assert profiles["ils"].params == {
        "max_iters": 100,
        "perturb_moves": 4,
        "checkpoint_every_iter": 1,
    }
    assert profiles["grasp"].params == {
        "alpha": 0.30,
        "max_iters": 100,
        "checkpoint_every_iter": 1,
    }


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo not installed")
def test_rust_metaheuristic_ablation_smoke_panel_passes(tmp_path: Path):
    instances = tmp_path / "instances"
    instances.mkdir()
    _write_instance(instances / "toy_path12.json.gz", 12)

    out_dir = tmp_path / "ablation"
    report = run_ablation(
        instances_dir=instances,
        include=["toy_path12.json.gz"],
        output_dir=out_dir,
        seeds=[42],
        budget_time_ms=1000,
    )

    assert report["schema_version"] == "rust-metaheuristic-ablation-v1"
    assert report["passed"] is True
    assert report["pairs"] == 3
    assert report["runs"] == 6
    assert report["invalid_rows"] == 0
    assert report["invalid_pairs"] == 0
    assert set(report["by_family"]) == {"sa", "ils", "grasp"}

    assert (out_dir / "report.json").exists()
    assert (out_dir / "runs.csv").exists()
    assert (out_dir / "paired_summary.csv").exists()
