import csv
import gzip
import json
import shutil
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

from hpc_framework.plan_runner import run_plan


def _write_instance_edges(tmp_path: Path, n: int = 10) -> Path:
    edges = [[i, i + 1] for i in range(n - 1)]
    inst = {"instance_id": "toy", "num_nodes": n, "edges": edges}
    ipath = tmp_path / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


def test_run_plan_full_canonical_portfolio_writes_manifest_and_valid_outputs(tmp_path: Path):
    instances_dir = tmp_path / "instances"
    instances_dir.mkdir()
    _write_instance_edges(instances_dir, n=12)

    raw_dir = tmp_path / "raw"
    manifest_out = raw_dir / "manifest_index.csv"
    kahip_available = shutil.which("kaffpa") is not None

    plan = {
        "schema": "forja-exp-v1",
        "experiment_id": "test-full-canonical-portfolio",
        "solvers": {
            "metis": {
                "enabled": True,
                "k": 2,
                "imbalance": 0.10,
                "budget": {"type": "time", "seconds": 5},
            },
            "kahip": {
                "enabled": kahip_available,
                "k": 2,
                "imbalance": 0.10,
                "budget": {"type": "time", "seconds": 5},
                "params": {"preset": "fast"},
            },
            "sa": {
                "enabled": True,
                "k": 2,
                "imbalance": 0.10,
                "budget": {"type": "time", "seconds": 5},
                "params": {
                    "initial_temp": 1.0,
                    "cooling": 0.995,
                    "min_temp": 1e-3,
                    "max_steps": 500,
                    "checkpoint_every_nfe": 10,
                },
            },
            "ils": {
                "enabled": True,
                "k": 2,
                "imbalance": 0.10,
                "budget": {"type": "time", "seconds": 5},
                "params": {
                    "max_iters": 30,
                    "perturb_moves": 2,
                    "checkpoint_every_iter": 1,
                },
            },
            "grasp": {
                "enabled": True,
                "k": 2,
                "imbalance": 0.10,
                "budget": {"type": "time", "seconds": 5},
                "params": {
                    "alpha": 0.30,
                    "max_iters": 30,
                    "checkpoint_every_iter": 1,
                },
            },
            "ts": {
                "enabled": True,
                "k": 2,
                "imbalance": 0.10,
                "budget": {"type": "time", "seconds": 5},
                "params": {
                    "max_steps": 300,
                    "min_tenure": 3,
                    "tenure_scale": 1.0,
                    "tenure_jitter": 2,
                    "checkpoint_every_nfe": 10,
                    "frequency_penalty": 0.01,
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

    schema_path = Path("specs/jsonschema/solver_run.schema.v1.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    kahip_available = shutil.which("kaffpa") is not None
    expected_algos = {"metis", "sa", "ils", "grasp", "ts"}
    if kahip_available:
        expected_algos.add("kahip")

    with manifest_out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == len(expected_algos)
    assert {row["algo"] for row in rows} == expected_algos
    assert {row["instance_id"] for row in rows} == {"toy"}

    for row in rows:
        algo = row["algo"]
        out_json = raw_dir / f"toy.json.gz__{algo}__k2__b0.10__seed42.json"
        assert out_json.exists()

        data = json.loads(out_json.read_text(encoding="utf-8"))
        assert data["algo"] in expected_algos
        assert data["instance_id"] == "toy"
        assert data["k"] == 2
        assert data["beta"] == 0.10
        assert data["seed"] == 42
        assert isinstance(data["elapsed_ms"], int)
        assert data["elapsed_ms"] >= 0
        assert Path(data["paths"]["workdir"]).exists()
        assert Path(data["paths"]["graph_path"]).exists()
        assert Path(data["paths"]["part_path"]).exists()

        errors = sorted(Draft7Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        assert errors == [], [
            f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
        ]

        if data["algo"] in {"sa", "ils", "grasp", "ts"}:
            assert len(data["checkpoints"]) >= 1
            assert data["checkpoints"][-1]["nfe"] >= 0
        else:
            assert len(data["checkpoints"]) >= 1
