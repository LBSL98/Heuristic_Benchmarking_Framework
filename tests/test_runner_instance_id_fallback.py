import gzip
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import hpc_framework.runner as runner_mod
from hpc_framework.runner import run_one


def _write_instance_without_instance_id(tmp_path: Path) -> Path:
    inst = {
        "num_nodes": 4,
        "edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
    }
    ipath = tmp_path / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


@pytest.mark.parametrize("algo", ["metis", "kahip"])
def test_runner_falls_back_to_instance_stem_when_instance_id_missing(
    monkeypatch, tmp_path: Path, algo: str
):
    inst_path = _write_instance_without_instance_id(tmp_path)
    out_json = tmp_path / f"out_{algo}.json"
    workdir = tmp_path / f"work_{algo}"
    part_path = tmp_path / f"{algo}.part"
    part_path.write_text("0\n0\n1\n1\n", encoding="utf-8")

    def fake_solver(*args, **kwargs):
        return SimpleNamespace(
            part_path=part_path,
            elapsed_ms=123,
            status="ok",
            returncode=0,
            stdout="",
            stderr="",
        )

    if algo == "metis":
        monkeypatch.setattr(runner_mod, "run_gpmetis", fake_solver)
    else:
        monkeypatch.setattr(runner_mod, "run_kaffpa", fake_solver)

    monkeypatch.setattr(
        runner_mod,
        "read_partition_labels",
        lambda path: np.array([0, 0, 1, 1], dtype=int),
    )

    run_one(
        instance_path=inst_path,
        algo=algo,
        k=2,
        beta=0.03,
        seed=42,
        budget_time_ms=5000,
        out_json=out_json,
        workdir=workdir,
        kahip_preset="fast",
        log_level="info",
    )

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["instance_id"] == "toy.json"
