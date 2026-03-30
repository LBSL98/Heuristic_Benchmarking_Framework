import gzip
import json
from pathlib import Path

import yaml

from hpc_framework.plan_runner import run_plan


def test_run_plan_greedy_records_elapsed_ms_and_checkpoint_time(monkeypatch, tmp_path: Path):
    import hpc_framework.plan_runner as plan_runner_mod

    def fake_obs(inst: dict, delta_v: float) -> dict:
        return {
            "labels": [0, 0, 1, 1],
            "observed_k": 2,
            "cutsize_best": 5,
        }

    ticks = iter([10.0, 10.25])

    monkeypatch.setattr(plan_runner_mod, "run_greedy_observation", fake_obs, raising=False)
    monkeypatch.setattr(
        plan_runner_mod.time,
        "perf_counter",
        lambda: next(ticks),
        raising=True,
    )

    instances_dir = tmp_path / "instances"
    instances_dir.mkdir()

    inst = {
        "num_nodes": 4,
        "edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
    }

    inst_path = instances_dir / "toy.json.gz"
    with gzip.open(inst_path, "wt", encoding="utf-8") as f:
        json.dump(inst, f)

    raw_dir = tmp_path / "raw"

    plan = {
        "schema": "forja-exp-v1",
        "experiment_id": "test-greedy-elapsed",
        "solvers": {
            "greedy": {
                "enabled": True,
                "params": {"delta_v": 0.10},
                "budget": {"type": "time", "seconds": 5},
            },
            "metis": {"enabled": False},
            "kahip": {"enabled": False},
        },
        "instances": {"base_dir": str(instances_dir), "include": ["toy.json.gz"]},
        "rng": {"seeds": [42]},
        "output": {"raw_dir": str(raw_dir)},
    }

    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(plan), encoding="utf-8")

    run_plan(plan_path)

    out_json = raw_dir / "toy.json.gz__greedy__dv0.10__seed42.json"
    data = json.loads(out_json.read_text(encoding="utf-8"))

    assert data["elapsed_ms"] == 250
    assert len(data["checkpoints"]) == 1
    assert data["checkpoints"][0]["time_ms"] == 250
    assert data["checkpoints"][0]["cutsize_best"] == 5
