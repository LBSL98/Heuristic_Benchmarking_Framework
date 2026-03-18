from pathlib import Path

import yaml

from hpc_framework.plan_runner import run_plan


def test_run_plan_metis_names_out_json_and_workdir_with_k_and_beta(monkeypatch, tmp_path: Path):
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
        "experiment_id": "namespace-test",
        "solvers": {
            "greedy": {"enabled": False},
            "metis": {"enabled": True, "k": 8, "budget": {"type": "time", "seconds": 5}},
            "kahip": {"enabled": False, "k": 8, "budget": {"type": "time", "seconds": 5}},
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

    assert len(calls) == 1
    call = calls[0]

    out_name = call["out_json"].name
    work_name = call["workdir"].name

    assert "k8" in out_name
    assert "b0.03" in out_name
    assert "k8" in work_name
    assert "b0.03" in work_name
