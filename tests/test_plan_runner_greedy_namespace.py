import gzip
import json
from pathlib import Path

import yaml

from hpc_framework.plan_runner import run_plan


def _write_instance_edges(instances_dir: Path, n: int = 6) -> Path:
    inst = {
        "instance_id": "toy",
        "nodes": [{"id": i, "velocity": 1.0 + 0.1 * i} for i in range(n)],
        "edges": [[i, i + 1] for i in range(n - 1)],
    }
    ipath = instances_dir / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


def test_run_plan_greedy_names_output_with_delta_v(monkeypatch, tmp_path: Path):
    def fake_run_greedy_observation(inst, delta_v):
        return {
            "labels": [0, 1, 0, 1, 0, 1],
            "observed_k": 2,
            "cutsize_best": 5,
        }

    import hpc_framework.plan_runner as plan_runner_mod

    monkeypatch.setattr(
        plan_runner_mod,
        "run_greedy_observation",
        fake_run_greedy_observation,
        raising=False,
    )

    instances_dir = tmp_path / "instances"
    instances_dir.mkdir()
    _write_instance_edges(instances_dir, n=6)

    raw_dir = tmp_path / "raw"
    tables_dir = tmp_path / "tables"

    plan = {
        "schema": "forja-exp-v1",
        "experiment_id": "greedy-namespace-test",
        "solvers": {
            "greedy": {
                "enabled": True,
                "params": {"delta_v": 0.25},
                "budget": {"type": "time", "seconds": 5},
            },
            "metis": {"enabled": False, "k": 2, "budget": {"type": "time", "seconds": 5}},
            "kahip": {"enabled": False, "k": 2, "budget": {"type": "time", "seconds": 5}},
        },
        "instances": {
            "base_dir": str(instances_dir),
            "include": ["toy.json.gz"],
        },
        "rng": {"seeds": [42]},
        "output": {
            "raw_dir": str(raw_dir),
            "tables_dir": str(tables_dir),
        },
    }

    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(plan), encoding="utf-8")

    run_plan(plan_path)

    json_files = sorted(raw_dir.glob("*.json"))
    assert len(json_files) == 1

    out_name = json_files[0].name
    assert "greedy" in out_name
    assert "dv0.25" in out_name
    assert "seed42" in out_name
