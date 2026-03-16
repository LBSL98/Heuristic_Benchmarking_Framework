import gzip
import json
import shutil
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator

from hpc_framework import cli as cli_mod


def _write_instance_edges(instances_dir: Path, n: int = 10) -> Path:
    edges = [[i, i + 1] for i in range(n - 1)]
    inst = {"instance_id": "toy", "num_nodes": n, "edges": edges}
    ipath = instances_dir / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


@pytest.mark.skipif(shutil.which("gpmetis") is None, reason="gpmetis não está no PATH")
def test_cli_run_plan_emits_schema_valid_json(tmp_path: Path):
    instances_dir = tmp_path / "instances"
    instances_dir.mkdir()

    _write_instance_edges(instances_dir, n=10)

    raw_dir = tmp_path / "raw"
    tables_dir = tmp_path / "tables"

    plan = {
        "schema": "forja-exp-v1",
        "experiment_id": "cli-integration-plan",
        "solvers": {
            "greedy": {"enabled": False},
            "metis": {"enabled": True, "k": 2, "budget": {"type": "time", "seconds": 5}},
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

    cli_mod.main(["run", "--plan", str(plan_path)])

    json_files = sorted(raw_dir.glob("*.json"))
    assert len(json_files) == 1

    schema = json.loads(
        Path("specs/jsonschema/solver_run.schema.v1.json").read_text(encoding="utf-8")
    )
    data = json.loads(json_files[0].read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    assert errors == [], [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
    assert data["algo"] == "metis"
    assert data["seed"] == 42
    assert data["k"] == 2
    assert "checkpoints" in data
    assert len(data["checkpoints"]) == 1
