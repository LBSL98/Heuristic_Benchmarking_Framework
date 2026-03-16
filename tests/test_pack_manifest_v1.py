import json
import subprocess
import sys
from pathlib import Path


def test_pack_manifest_preserves_runner_observed_fields(tmp_path: Path):
    src = tmp_path / "runner.json"
    dst = tmp_path / "packed.v1.json"

    runner_obj = {
        "timestamp": "2026-03-16T00:00:00+00:00",
        "instance_id": "toy-instance",
        "algo": "metis",
        "k": 8,
        "beta": 0.03,
        "seed": 42,
        "budget_time_ms": 5000,
        "status": "ok",
        "returncode": 0,
        "elapsed_ms": 123,
        "stdout": "runner-stdout",
        "stderr": "runner-stderr",
        "metrics": {
            "cutsize_best": 111,
            "n_nodes": 10,
            "balance_tolerance": 0.03,
            "imbalance_raw": 30,
        },
        "env": {
            "hostname": "runner-host",
            "python": "3.11.0",
            "os": "Linux",
            "os_release": "6.0",
            "cpu": {
                "model": "runner-cpu",
                "cores_logical": 8,
                "cores_physical": 4,
                "freq_mhz": 3200.0,
            },
        },
        "tools": {
            "gpmetis": {"exists": True, "version": "gpmetis 5.1.0"},
            "kaffpa": {"exists": False, "version": ""},
        },
        "paths": {
            "workdir": "/tmp/runner-work",
            "graph_path": "/tmp/runner-work/graph.graph",
            "part_path": "/tmp/runner-work/graph.graph.part.8",
        },
        "checkpoints": [{"time_ms": 123, "cutsize_best": 111, "nfe": None}],
        "schema_version": "1.0.0",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
    }

    src.write_text(json.dumps(runner_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    subprocess.run(
        [sys.executable, "scripts/pack_manifest_v1.py", "--in", str(src), "--out", str(dst)],
        check=True,
    )

    packed = json.loads(dst.read_text(encoding="utf-8"))

    assert packed["env"] == runner_obj["env"]
    assert packed["tools"] == runner_obj["tools"]
    assert packed["metrics"] == runner_obj["metrics"]
    assert packed["paths"] == runner_obj["paths"]
    assert packed["checkpoints"] == runner_obj["checkpoints"]


def test_pack_manifest_backfills_missing_fields_for_legacy_input(tmp_path: Path):
    src = tmp_path / "legacy.json"
    dst = tmp_path / "packed.v1.json"

    legacy_obj = {
        "instance_id": "toy-instance",
        "algo": "metis",
        "k": 8,
        "beta": 0.03,
        "seed": 42,
        "budget_time_ms": 5000,
        "status": "ok",
        "returncode": 0,
        "elapsed_ms": 123,
        "stdout": "",
        "stderr": "",
        "cutsize_best": 111,
        "workdir": "/tmp/legacy-work",
        "graph_path": "/tmp/legacy-work/graph.graph",
        "part_path": "/tmp/legacy-work/graph.graph.part.8",
    }

    src.write_text(json.dumps(legacy_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    subprocess.run(
        [sys.executable, "scripts/pack_manifest_v1.py", "--in", str(src), "--out", str(dst)],
        check=True,
    )

    packed = json.loads(dst.read_text(encoding="utf-8"))

    assert "timestamp" in packed
    assert "metrics" in packed
    assert "env" in packed
    assert "tools" in packed
    assert "paths" in packed
    assert "checkpoints" in packed

    assert packed["metrics"]["cutsize_best"] == 111
    assert packed["paths"]["workdir"] == "/tmp/legacy-work"
    assert packed["paths"]["graph_path"] == "/tmp/legacy-work/graph.graph"
    assert packed["paths"]["part_path"] == "/tmp/legacy-work/graph.graph.part.8"
    assert packed["checkpoints"] == []
