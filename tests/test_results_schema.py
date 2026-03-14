import gzip
import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from hpc_framework.runner import run_one


def _write_instance_edges(tmp_path: Path, n: int = 6):
    edges = [[i, i + 1] for i in range(n - 1)]
    inst = {"instance_id": "toy", "num_nodes": n, "edges": edges}
    ipath = tmp_path / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


@pytest.mark.skipif(shutil.which("gpmetis") is None, reason="gpmetis não está no PATH")
def test_runner_output_with_checkpoints_matches_schema(tmp_path: Path):
    inst_path = _write_instance_edges(tmp_path, n=10)
    out_json = tmp_path / "out_metis.json"
    workdir = tmp_path / "work"

    run_one(
        instance_path=inst_path,
        algo="metis",
        k=2,
        beta=0.03,
        seed=42,
        budget_time_ms=5000,
        out_json=out_json,
        workdir=workdir,
        kahip_preset="fast",
        log_level="info",
    )

    schema_path = Path("specs/jsonschema/solver_run.schema.v1.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = json.loads(out_json.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    assert errors == [], [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
