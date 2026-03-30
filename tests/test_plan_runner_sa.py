import csv
import gzip
import json
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

from hpc_framework.plan_runner import _enabled_supported_solvers, run_plan


def _write_instance_edges(tmp_path: Path, n: int = 8) -> Path:
    edges = [[i, i + 1] for i in range(n - 1)]
    inst = {"instance_id": "toy", "num_nodes": n, "edges": edges}
    ipath = tmp_path / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


def test_enabled_supported_solvers_includes_sa_when_enabled():
    plan = {
        "solvers": {
            "metis": {"enabled": False},
            "kahip": {"enabled": False},
            "sa": {"enabled": True},
        }
    }

    assert _enabled_supported_solvers(plan) == ["sa"]


def test_run_plan_sa_writes_schema_compatible_output_and_manifest(tmp_path: Path):
    instances_dir = tmp_path / "instances"
    instances_dir.mkdir()
    _write_instance_edges(instances_dir, n=10)

    raw_dir = tmp_path / "raw"
    manifest_out = raw_dir / "manifest_index.csv"

    plan = {
        "schema": "forja-exp-v1",
        "experiment_id": "test-sa-plan",
        "solvers": {
            "metis": {"enabled": False},
            "kahip": {"enabled": False},
            "sa": {
                "enabled": True,
                "k": 2,
                "imbalance": 0.10,
                "budget": {"type": "time", "seconds": 10},
                "params": {
                    "initial_temp": 1.0,
                    "cooling": 0.99,
                    "min_temp": 1e-3,
                    "max_steps": 50,
                    "checkpoint_every_nfe": 5,
                },
            },
        },
        "instances": {
            "base_dir": str(instances_dir),
            "include": ["toy.json.gz"],
            "manifest_out": str(manifest_out),
        },
        "rng": {"seeds": [42]},
        "output": {"raw_dir": str(raw_dir)},
    }

    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(plan), encoding="utf-8")

    run_plan(plan_path)

    out_json = raw_dir / "toy.json.gz__sa__k2__b0.10__seed42.json"
    assert out_json.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["algo"] == "sa"
    assert data["instance_id"] == "toy"
    assert data["k"] == 2
    assert data["beta"] == 0.10
    assert data["seed"] == 42
    assert data["status"] == "ok"
    assert isinstance(data["elapsed_ms"], int)
    assert data["elapsed_ms"] >= 0
    assert len(data["checkpoints"]) >= 1
    assert data["checkpoints"][-1]["nfe"] >= 0
    assert data["checkpoints"][-1]["cutsize_best"] == data["cutsize_best"]
    assert Path(data["paths"]["workdir"]).exists()
    assert Path(data["paths"]["graph_path"]).exists()
    assert Path(data["paths"]["part_path"]).exists()

    schema_path = Path("specs/jsonschema/solver_run.schema.v1.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft7Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    assert errors == [], [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]

    with manifest_out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    assert rows[0]["algo"] == "sa"
    assert rows[0]["instance_id"] == "toy"
