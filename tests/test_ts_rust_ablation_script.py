import gzip
import json
from pathlib import Path

import yaml

from scripts.run_ts_rust_ablation import run_ablation


def _write_instance(path: Path, n: int) -> None:
    payload = {
        "instance_id": path.stem.replace(".json", ""),
        "num_nodes": n,
        "edges": [[i, i + 1] for i in range(n - 1)],
    }
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(payload, f)


def test_run_ts_rust_ablation_smoke(tmp_path: Path):
    inst = tmp_path / "toy.json.gz"
    _write_instance(inst, n=12)

    config = {
        "schema": "ts-rust-ablation-v1",
        "experiment_id": "test-ts-rust-ablation",
        "claim_boundary": {"allowed": "test only", "forbidden": []},
        "budget": {"type": "wall_clock", "budget_time_ms": 300},
        "target_rule": {"name": "python_final"},
        "trajectory_grid_ms": [0, 100, 300],
        "seeds": [42],
        "cases": [{"name": "toy", "instance": str(inst), "k": 3, "beta": 0.10}],
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    out_dir = tmp_path / "ablation"
    report = run_ablation(config_path, out_dir)

    assert report["num_pairs"] == 1
    assert report["num_valid_pairs"] == 1
    assert Path(report["outputs"]["runs_csv"]).exists()
    assert Path(report["outputs"]["paired_summary_csv"]).exists()
    assert Path(report["outputs"]["trajectory_samples_csv"]).exists()

    pair_text = Path(report["outputs"]["paired_summary_csv"]).read_text(encoding="utf-8")
    assert "rust_minus_python_cut" in pair_text
    assert "python_ttt_ms" in pair_text
    assert "rust_ttt_ms" in pair_text
