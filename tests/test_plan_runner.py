import csv
import json
from pathlib import Path

import yaml

from hpc_framework.plan_runner import (
    _enabled_supported_solvers,
    _included_instances,
    _planned_runs,
    _rng_seeds,
    _solver_beta,
    _solver_budget_time_ms,
    _solver_k,
    run_plan,
)


def test_enabled_supported_solvers_returns_only_supported_enabled_solvers():
    plan = {
        "solvers": {
            "greedy": {"enabled": False},
            "metis": {"enabled": True},
            "kahip": {"enabled": False},
        }
    }

    assert _enabled_supported_solvers(plan) == ["metis"]


def test_enabled_supported_solvers_returns_both_supported_solvers_when_enabled():
    plan = {
        "solvers": {
            "greedy": {"enabled": False},
            "metis": {"enabled": True},
            "kahip": {"enabled": True},
        }
    }

    assert _enabled_supported_solvers(plan) == ["metis", "kahip"]


def test_included_instances_returns_declared_include_list():
    plan = {
        "instances": {
            "base_dir": "data/instances/synthetic",
            "include": ["a.json.gz", "b.json.gz"],
        }
    }

    assert _included_instances(plan) == ["a.json.gz", "b.json.gz"]


def test_rng_seeds_returns_declared_seed_list():
    plan = {"rng": {"seeds": [7, 42, 99]}}

    assert _rng_seeds(plan) == [7, 42, 99]


def test_solver_k_reads_solver_specific_k():
    plan = {
        "solvers": {
            "metis": {"enabled": True, "k": 8},
            "kahip": {"enabled": True, "k": 4},
        }
    }

    assert _solver_k(plan, "metis") == 8
    assert _solver_k(plan, "kahip") == 4


def test_solver_beta_reads_kahip_imbalance_and_defaults_metis():
    plan = {
        "solvers": {
            "metis": {"enabled": True},
            "kahip": {"enabled": True, "imbalance": 0.07},
        }
    }

    assert _solver_beta(plan, "metis") == 0.03
    assert _solver_beta(plan, "kahip") == 0.07


def test_solver_budget_time_ms_converts_seconds_to_ms():
    plan = {
        "solvers": {
            "metis": {"enabled": True, "budget": {"type": "time", "seconds": 5}},
        }
    }

    assert _solver_budget_time_ms(plan, "metis") == 5000


def test_planned_runs_builds_cartesian_product_with_solver_parameters():
    plan = {
        "solvers": {
            "greedy": {"enabled": False},
            "metis": {"enabled": True, "k": 8, "budget": {"type": "time", "seconds": 5}},
            "kahip": {
                "enabled": True,
                "k": 4,
                "imbalance": 0.07,
                "budget": {"type": "time", "seconds": 2},
            },
        },
        "instances": {
            "include": ["a.json.gz"],
        },
        "rng": {"seeds": [1, 2]},
    }

    runs = _planned_runs(plan)

    assert len(runs) == 4
    assert runs[0] == {
        "instance": "a.json.gz",
        "solver": "metis",
        "seed": 1,
        "k": 8,
        "beta": 0.03,
        "budget_time_ms": 5000,
    }
    assert runs[-1] == {
        "instance": "a.json.gz",
        "solver": "kahip",
        "seed": 2,
        "k": 4,
        "beta": 0.07,
        "budget_time_ms": 2000,
    }


def test_run_plan_delegates_all_planned_runs_to_runner(monkeypatch, tmp_path: Path):
    calls = []

    def fake_run_one(**kwargs):
        calls.append(kwargs)
        return object()

    import hpc_framework.plan_runner as plan_runner_mod

    monkeypatch.setattr(plan_runner_mod, "run_one", fake_run_one, raising=False)

    instances_dir = tmp_path / "instances"
    instances_dir.mkdir()
    (instances_dir / "toy.json.gz").write_text("placeholder", encoding="utf-8")

    raw_dir = tmp_path / "raw"
    tables_dir = tmp_path / "tables"

    plan = {
        "schema": "forja-exp-v1",
        "experiment_id": "test-plan",
        "solvers": {
            "greedy": {"enabled": False},
            "metis": {"enabled": True, "k": 8, "budget": {"type": "time", "seconds": 5}},
            "kahip": {
                "enabled": True,
                "k": 4,
                "imbalance": 0.07,
                "budget": {"type": "time", "seconds": 2},
            },
        },
        "instances": {"base_dir": str(instances_dir), "include": ["toy.json.gz"]},
        "rng": {"seeds": [1, 2]},
        "output": {"raw_dir": str(raw_dir), "tables_dir": str(tables_dir)},
    }

    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(plan), encoding="utf-8")

    run_plan(plan_path)

    assert len(calls) == 4

    assert calls[0]["algo"] == "metis"
    assert calls[0]["seed"] == 1
    assert calls[0]["k"] == 8
    assert calls[0]["beta"] == 0.03
    assert calls[0]["budget_time_ms"] == 5000

    assert calls[-1]["algo"] == "kahip"
    assert calls[-1]["seed"] == 2
    assert calls[-1]["k"] == 4
    assert calls[-1]["beta"] == 0.07
    assert calls[-1]["budget_time_ms"] == 2000

    for call in calls:
        assert call["instance_path"] == instances_dir / "toy.json.gz"
        assert call["out_json"].suffix == ".json"


def test_run_plan_writes_manifest_index_when_declared(monkeypatch, tmp_path: Path):
    calls = []

    def fake_run_one(**kwargs):
        calls.append(kwargs)
        payload = {
            "timestamp": "2026-03-23T00:00:00+00:00",
            "instance_id": "toy",
            "algo": kwargs["algo"],
            "k": kwargs["k"],
            "beta": kwargs["beta"],
            "seed": kwargs["seed"],
            "budget_time_ms": kwargs["budget_time_ms"],
            "status": "ok",
            "returncode": 0,
            "elapsed_ms": 1,
            "metrics": {
                "cutsize_best": 10,
                "imbalance_raw": 0.0,
            },
            "paths": {
                "workdir": str(kwargs["workdir"]),
                "graph_path": "",
                "part_path": None,
            },
        }
        kwargs["out_json"].parent.mkdir(parents=True, exist_ok=True)
        kwargs["out_json"].write_text(json.dumps(payload), encoding="utf-8")
        return object()

    import hpc_framework.plan_runner as plan_runner_mod

    monkeypatch.setattr(plan_runner_mod, "run_one", fake_run_one, raising=False)

    instances_dir = tmp_path / "instances"
    instances_dir.mkdir()
    (instances_dir / "toy.json.gz").write_text("placeholder", encoding="utf-8")

    raw_dir = tmp_path / "raw"
    tables_dir = tmp_path / "tables"
    manifest_out = raw_dir / "manifest_index.csv"

    plan = {
        "schema": "forja-exp-v1",
        "experiment_id": "test-plan-manifest",
        "solvers": {
            "greedy": {"enabled": False},
            "metis": {"enabled": True, "k": 8, "budget": {"type": "time", "seconds": 5}},
            "kahip": {
                "enabled": True,
                "k": 4,
                "imbalance": 0.07,
                "budget": {"type": "time", "seconds": 2},
            },
        },
        "instances": {
            "base_dir": str(instances_dir),
            "include": ["toy.json.gz"],
            "manifest_out": str(manifest_out),
        },
        "rng": {"seeds": [1, 2]},
        "output": {"raw_dir": str(raw_dir), "tables_dir": str(tables_dir)},
    }

    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(plan), encoding="utf-8")

    run_plan(plan_path)

    assert manifest_out.exists()

    with manifest_out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 4
    assert {row["_file"] for row in rows} == {str(call["out_json"]) for call in calls}
    assert sorted(row["algo"] for row in rows) == ["kahip", "kahip", "metis", "metis"]
