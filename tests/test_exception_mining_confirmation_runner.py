from __future__ import annotations

import csv
import json
import runpy
from pathlib import Path


def test_confirmation_filters_keep_first_candidate_budget_seed() -> None:
    module = runpy.run_path("scripts/run_exception_mining_confirmation.py")
    PlanRow = module["PlanRow"]
    filter_plan_rows = module["filter_plan_rows"]

    rows = [
        PlanRow(
            campaign_id="c",
            confirmation_stage="s",
            environment_id="env",
            run_id=f"candidate_{candidate}__{algo}",
            candidate_id=f"candidate_{candidate}",
            family="F01",
            environment_target="common",
            variant="v",
            priority_label_from_screening="near_tie_candidate",
            algo_label=algo.upper(),
            algo=algo,
            seed=seed,
            budget_ms=budget,
            bundle_path=Path("bundle"),
            instance_path=Path("instance.json.gz"),
        )
        for candidate in [1, 2]
        for algo in ["metis", "sa"]
        for budget in [100, 250]
        for seed in [42, 43]
    ]

    selected = filter_plan_rows(
        rows,
        only_algo=set(),
        only_family=set(),
        only_candidate=set(),
        only_budget={250},
        only_seed={42},
        smoke_first_candidate=True,
        offset=0,
        limit=None,
    )

    assert len(selected) == 2
    assert {row.candidate_id for row in selected} == {"candidate_1"}
    assert {row.algo for row in selected} == {"metis", "sa"}
    assert {row.budget_ms for row in selected} == {250}
    assert {row.seed for row in selected} == {42}


def test_collapse_uses_median_quality_cut_then_elapsed_then_seed() -> None:
    module = runpy.run_path("scripts/run_exception_mining_confirmation.py")
    collapse_confirmation_results = module["collapse_confirmation_results"]

    rows = []
    for seed, cut, elapsed in [(42, 10, 3), (43, 30, 2), (44, 20, 1)]:
        rows.append(
            {
                "campaign_id": "c",
                "confirmation_stage": "full_portfolio_confirmation",
                "environment_id": "env",
                "candidate_id": "candidate",
                "family": "F01",
                "environment_target": "common",
                "variant": "v",
                "priority_label_from_screening": "near_tie_candidate",
                "algo_label": "SA",
                "algo": "sa",
                "seed": seed,
                "budget_ms": 100,
                "status": "ok",
                "valid": True,
                "available_by_budget": True,
                "cutsize": cut,
                "elapsed_ms": elapsed,
            }
        )

    collapsed = collapse_confirmation_results(rows)

    assert len(collapsed) == 1
    assert collapsed[0]["median_valid_cut_by_budget"] == 20
    assert collapsed[0]["best_valid_cut_by_budget"] == 10
    assert collapsed[0]["median_seed"] == 44
    assert collapsed[0]["collapse_rule"] == "median_quality_cut_then_elapsed_then_seed"


def test_confirmation_labels_separate_python_rust_and_all_meta() -> None:
    module = runpy.run_path("scripts/run_exception_mining_confirmation.py")
    compute_confirmation_labels = module["compute_confirmation_labels"]

    base = {
        "campaign_id": "c",
        "confirmation_stage": "full_portfolio_confirmation_collapsed",
        "environment_id": "env",
        "candidate_id": "candidate",
        "family": "F01",
        "environment_target": "common",
        "variant": "v",
        "priority_label_from_screening": "strong_exception_candidate",
        "budget_ms": 100,
        "available_by_budget": True,
        "median_elapsed_ms": 1,
    }
    rows = [
        base | {"algo": "metis", "median_valid_cut_by_budget": 100},
        base | {"algo": "kahip", "median_valid_cut_by_budget": 105},
        base | {"algo": "sa", "median_valid_cut_by_budget": 99},
        base | {"algo": "sa_rust", "median_valid_cut_by_budget": 97},
    ]

    labels = compute_confirmation_labels(rows)

    assert len(labels) == 1
    assert labels[0]["best_multilevel_algo"] == "metis"
    assert labels[0]["best_meta_python_algo"] == "sa"
    assert labels[0]["best_meta_rust_algo"] == "sa_rust"
    assert labels[0]["best_meta_all_algo"] == "sa_rust"
    assert labels[0]["confirmation_exception_label"] == "strong_exception_confirmed"


def test_confirmation_runner_writes_expected_outputs_with_fake_run_one(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = runpy.run_path("scripts/run_exception_mining_confirmation.py")
    PlanRow = module["PlanRow"]
    write_csv = module["write_csv"]
    main = module["main"]

    bundle = tmp_path / "bundle"
    bundle.mkdir()
    instance_path = bundle / "instance.json.gz"
    instance_path.write_bytes(b"fake")

    plan_csv = tmp_path / "run_plan.csv"
    plan_rows = []
    for algo in ["metis", "kahip", "sa", "sa_rust"]:
        row = PlanRow(
            campaign_id="EXP-MULTILEVEL-EXCEPTION-MINING-001",
            confirmation_stage="full_portfolio_confirmation_plan",
            environment_id="test_env",
            run_id=f"candidate__{algo}__seed42__budget100__env_test_env",
            candidate_id="candidate",
            family="F01",
            environment_target="common",
            variant="v",
            priority_label_from_screening="near_tie_candidate",
            algo_label=algo,
            algo=algo,
            seed=42,
            budget_ms=100,
            bundle_path=bundle,
            instance_path=instance_path,
        )
        plan_rows.append(
            {
                "campaign_id": row.campaign_id,
                "confirmation_stage": row.confirmation_stage,
                "environment_id": row.environment_id,
                "run_id": row.run_id,
                "candidate_id": row.candidate_id,
                "family": row.family,
                "environment_target": row.environment_target,
                "variant": row.variant,
                "priority_label_from_screening": row.priority_label_from_screening,
                "algo_label": row.algo_label,
                "algo": row.algo,
                "seed": row.seed,
                "budget_ms": row.budget_ms,
                "bundle_path": str(row.bundle_path),
                "instance_path": str(row.instance_path),
            }
        )

    write_csv(plan_csv, plan_rows)

    def fake_run_one(**kwargs) -> None:
        out_json = Path(kwargs["out_json"])
        algo = str(kwargs["algo"])
        cut = {"metis": 100, "kahip": 101, "sa": 99, "sa_rust": 98}[algo]
        artifact = {
            "timestamp": "2026-01-01T00:00:00Z",
            "instance_id": "candidate",
            "algo": algo,
            "k": 2,
            "beta": 0.03,
            "seed": int(kwargs["seed"]),
            "budget_time_ms": int(kwargs["budget_time_ms"]),
            "status": "ok",
            "returncode": 0,
            "elapsed_ms": 1,
            "stdout": "",
            "stderr": "",
            "metrics": {
                "cutsize_best": cut,
                "n_nodes": 4,
                "balance_tolerance": 0.03,
            },
            "env": {"python": "test", "os": "test", "cpu": {}},
            "tools": {},
            "paths": {"workdir": str(kwargs["workdir"]), "graph_path": "graph.graph"},
            "checkpoints": [{"time_ms": 1, "cutsize_best": cut}],
            "cutsize_best": cut,
            "feasible": True,
            "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
            "schema_version": "1.0.0",
            "validation": {"counts": [2, 2], "max_allowed": 3},
        }
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(artifact), encoding="utf-8")

    monkeypatch.setitem(main.__globals__, "run_one", fake_run_one)

    output_root = tmp_path / "out"
    rc = main(
        [
            "--run-plan",
            str(plan_csv),
            "--output-root",
            str(output_root),
            "--force",
            "--fail-on-invalid",
        ]
    )

    assert rc == 0

    summary = json.loads((output_root / "confirmation_summary.json").read_text())
    assert summary["classification"] == "full_portfolio_confirmation"
    assert summary["planned_run_count"] == 4
    assert summary["valid_result_count"] == 4
    assert summary["confirmation_label_counts"] == {"strong_exception_confirmed": 1}

    results_path = output_root / "confirmation_results.csv"
    with results_path.open("r", encoding="utf-8", newline="") as handle:
        results = list(csv.DictReader(handle))
    assert "screening_stage" not in results[0]
    assert results[0]["confirmation_stage"] == "full_portfolio_confirmation"


def test_write_csv_accepts_heterogeneous_confirmation_rows(tmp_path: Path) -> None:
    module = runpy.run_path("scripts/run_exception_mining_confirmation.py")
    write_csv = module["write_csv"]

    rows = [
        {
            "run_id": "error_first",
            "algo": "metis",
            "status": "error",
            "error_type": "RuntimeError",
        },
        {
            "run_id": "success_second",
            "algo": "sa",
            "status": "ok",
            "cutsize": 10,
            "elapsed_ms": 1,
            "beta": 0.03,
            "checkpoint_count": 1,
        },
    ]

    out_csv = tmp_path / "heterogeneous.csv"
    write_csv(out_csv, rows)

    with out_csv.open("r", encoding="utf-8", newline="") as handle:
        loaded = list(csv.DictReader(handle))

    assert len(loaded) == 2
    assert "error_type" in loaded[0]
    assert "beta" in loaded[0]
    assert "checkpoint_count" in loaded[0]
    assert loaded[0]["run_id"] == "error_first"
    assert loaded[0]["beta"] == ""
    assert loaded[1]["run_id"] == "success_second"
    assert loaded[1]["beta"] == "0.03"
    assert loaded[1]["checkpoint_count"] == "1"
