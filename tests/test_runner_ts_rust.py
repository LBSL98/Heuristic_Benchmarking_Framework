import gzip
import json
import shutil
from pathlib import Path

import numpy as np
import pytest
from jsonschema import Draft7Validator

from hpc_framework.runner import compute_cutsize_edges_labels, run_one
from hpc_framework.solvers.common import read_partition_labels


def _write_instance_edges(tmp_path: Path, n: int = 12) -> Path:
    edges = [[i, i + 1] for i in range(n - 1)]
    inst = {"instance_id": "toy", "num_nodes": n, "edges": edges}
    ipath = tmp_path / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo not installed")
def test_runner_ts_rust_single_run_emits_schema_compatible_output(tmp_path: Path):
    inst_path = _write_instance_edges(tmp_path, n=12)
    out_json = tmp_path / "out_ts_rust.json"
    workdir = tmp_path / "work"

    run_one(
        instance_path=inst_path,
        algo="ts_rust",
        k=3,
        beta=0.10,
        seed=42,
        budget_time_ms=1000,
        out_json=out_json,
        workdir=workdir,
        kahip_preset="fast",
        log_level="info",
    )

    assert out_json.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))

    assert data["algo"] == "ts_rust"
    assert data["instance_id"] == "toy"
    assert data["k"] == 3
    assert data["beta"] == 0.10
    assert data["seed"] == 42
    assert data["status"] in {"ok", "timeout"}
    assert isinstance(data["elapsed_ms"], int)
    assert data["elapsed_ms"] >= 0
    assert data["feasible"] is True
    assert Path(data["paths"]["workdir"]).exists()
    assert Path(data["paths"]["graph_path"]).exists()
    assert Path(data["paths"]["part_path"]).exists()
    assert len(data["checkpoints"]) >= 1
    assert data["checkpoints"][-1]["nfe"] >= 0
    assert data["checkpoints"][-1]["cutsize_best"] == data["cutsize_best"]

    labels = read_partition_labels(Path(data["paths"]["part_path"]))
    expected_cut = compute_cutsize_edges_labels(
        np.asarray([[i, i + 1] for i in range(11)], dtype=int),
        labels,
    )
    assert expected_cut == data["cutsize_best"]

    schema_path = Path("specs/jsonschema/solver_run.schema.v1.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft7Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    assert errors == [], [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
