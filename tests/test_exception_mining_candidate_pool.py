"""Tests for issue #99 exploratory candidate-pool materialization."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_candidate_pool_smoke_profile_materializes_required_outputs(tmp_path: Path) -> None:
    """The smoke profile writes required pool-level artifacts without solver results."""

    output_root = tmp_path / "candidate_pool"
    env = os.environ.copy()
    env["PYTHONPATH"] = f"src{os.pathsep}{env.get('PYTHONPATH', '')}"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/generate_exception_mining_candidate_pool.py",
            "--profile",
            "smoke",
            "--output-root",
            str(output_root),
            "--force",
        ],
        text=True,
        capture_output=True,
        env=env,
        check=True,
    )

    cli_payload = json.loads(completed.stdout)
    assert cli_payload["accepted_count"] >= 6
    assert cli_payload["solver_results_used"] is False

    required_files = [
        "candidate_pool_plan.json",
        "generated_instances_manifest.csv",
        "generated_instances_manifest.json",
        "generation_attempts.jsonl",
        "rejection_log.md",
        "validation_summary.json",
        "validation_summary.md",
    ]
    for relative_path in required_files:
        assert (output_root / relative_path).exists(), relative_path

    manifest = json.loads(
        (output_root / "generated_instances_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest
    assert {row["family"] for row in manifest if row["accepted"]} == {"F01", "F02"}
    assert {row["environment_target"] for row in manifest if row["accepted"]} >= {
        "common",
        "holdout",
    }
    assert all(row["solver_results_used"] is False for row in manifest)

    attempts = (output_root / "generation_attempts.jsonl").read_text(encoding="utf-8").splitlines()
    assert attempts
    assert any('"event": "validation_passed"' in line for line in attempts)

    summary = json.loads((output_root / "validation_summary.json").read_text(encoding="utf-8"))
    assert summary["families_without_accepted_candidates"] == []
    assert summary["contains_solver_results"] is False

    for row in manifest:
        if row["accepted"]:
            bundle_path = Path(row["bundle_path"])
            assert bundle_path.exists()
            assert (bundle_path / "instance.json.gz").exists()
            assert (bundle_path / "sha256sums.txt").exists()
            assert row["validation_passed"] is True
