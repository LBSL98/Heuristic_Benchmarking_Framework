"""Tests for issue #100 exploratory exception screening."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_exception_mining_screening_smoke_profile_outputs_scope_and_labels(tmp_path: Path) -> None:
    """Smoke screening produces required outputs and keeps holdout out of screening."""

    pool_root = tmp_path / "pool"
    screening_root = tmp_path / "screening"
    env = os.environ.copy()
    env["PYTHONPATH"] = f"src{os.pathsep}{env.get('PYTHONPATH', '')}"

    subprocess.run(
        [
            sys.executable,
            "scripts/generate_exception_mining_candidate_pool.py",
            "--profile",
            "smoke",
            "--output-root",
            str(pool_root),
            "--force",
        ],
        text=True,
        capture_output=True,
        env=env,
        check=True,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_exception_mining_screening.py",
            "--profile",
            "smoke",
            "--pool-manifest",
            str(pool_root / "generated_instances_manifest.json"),
            "--output-root",
            str(screening_root),
            "--force",
        ],
        text=True,
        capture_output=True,
        env=env,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["classification"] == "exploratory_non_confirmatory"
    assert payload["cart_asp_claim_status"] == "not_allowed_from_screening"
    assert payload["holdout_reserved_count"] == 2
    assert payload["screened_candidate_count"] == 4
    assert payload["planned_run_count"] == 8

    required_files = [
        "screening_scope_manifest.json",
        "screening_run_plan.json",
        "screening_run_attempts.jsonl",
        "screening_raw_results.json",
        "screening_results.csv",
        "screening_results.json",
        "screening_results_collapsed.csv",
        "screening_summary.json",
        "screening_summary.md",
        "solver_artifact_inventory.json",
        "solver_artifact_inventory.md",
        "invalid_output_report.md",
        "preliminary_exception_labels.json",
        "preliminary_exception_labels.csv",
    ]
    for relative_path in required_files:
        assert (screening_root / relative_path).exists(), relative_path

    scope = json.loads(
        (screening_root / "screening_scope_manifest.json").read_text(encoding="utf-8")
    )
    assert scope["screened_count"] == 4
    assert scope["holdout_reserved_count"] == 2
    assert scope["non_screened_by_reason"]["holdout_reserved_by_protocol"] == 2
    assert all(row["environment_target"] != "holdout" for row in scope["screened_candidates"])

    raw_results = json.loads(
        (screening_root / "screening_raw_results.json").read_text(encoding="utf-8")
    )
    assert len(raw_results) == 8
    assert {row["algo"] for row in raw_results} == {"metis", "sa"}

    labels = json.loads(
        (screening_root / "preliminary_exception_labels.json").read_text(encoding="utf-8")
    )
    assert labels
    assert all(row["label_claim_status"] == "hypothesis_for_confirmation_only" for row in labels)


def test_exception_mining_screening_normalizer_reads_cutsize_best_contract() -> None:
    """Normalizer must consume the runner artifact field cutsize_best."""

    import runpy

    module = runpy.run_path("scripts/run_exception_mining_screening.py")
    normalize_successful_artifact = module["normalize_successful_artifact"]

    base = {
        "campaign_id": "EXP-MULTILEVEL-EXCEPTION-MINING-001",
        "screening_stage": "exploratory_non_confirmatory",
        "candidate_id": "candidate_x",
        "family": "F99",
        "environment_target": "common",
        "variant": "common_a",
        "bundle_path": "bundle",
        "instance_path": "bundle/instance.json.gz",
        "run_id": "candidate_x__metis__seed42__budget1000",
        "algo": "metis",
        "seed": 42,
        "budget_ms": 1000,
        "artifact_dir": "artifact",
        "artifact_json": "artifact/result.json",
        "workdir": "artifact/workdir",
        "error_type": "",
        "error_message": "",
    }
    artifact = {
        "status": "ok",
        "feasible": True,
        "cutsize_best": 63,
        "elapsed_ms": 4,
        "returncode": 0,
        "k": 2,
        "beta": 0.03,
        "metrics": {
            "n_nodes": 123,
            "n_edges": 654,
            "balance_tolerance": 0.03,
        },
        "checkpoints": [{"time_ms": 4, "cutsize": 63}],
    }

    row = normalize_successful_artifact(base, artifact)

    assert row["valid"] is True
    assert row["available_by_budget"] is True
    assert row["cutsize"] == 63
    assert row["elapsed_ms"] == 4
    assert row["epsilon"] == 0.03
    assert row["n"] == 123
    assert row["m"] == 654
