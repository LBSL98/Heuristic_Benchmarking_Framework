from __future__ import annotations

import json
import runpy
from pathlib import Path


def test_confirmation_plan_expands_manifest_matrix(tmp_path: Path) -> None:
    module = runpy.run_path("scripts/plan_exception_mining_confirmation.py")

    bundle = tmp_path / "bundles" / "F01" / "candidate_a"
    bundle.mkdir(parents=True)
    for name in [
        "instance.json.gz",
        "graph_metis.graph",
        "graph_edges.edgelist",
        "manifest_row.json",
        "sha256sums.txt",
    ]:
        (bundle / name).write_text("x\n", encoding="utf-8")

    candidate = {
        "candidate_id": "candidate_a",
        "family": "F01",
        "environment_target": "common",
        "variant": "common_a",
        "priority_label_from_screening": "near_tie_candidate",
        "confirmation_portfolio": "METIS;SA-Rust",
        "confirmation_budgets_ms": "100;500",
        "confirmation_seeds": "42;43",
        "bundle_path": str(bundle),
    }

    specs = module["build_run_plan"](
        [candidate],
        output_root=tmp_path / "out",
        environment_id="test_env",
        bundle_root_override=None,
        profile="issue102",
    )

    assert len(specs) == 8
    assert {spec.algo for spec in specs} == {"metis", "sa_rust"}
    assert {spec.budget_ms for spec in specs} == {100, 500}
    assert {spec.seed for spec in specs} == {42, 43}
    assert all(spec.environment_id == "test_env" for spec in specs)
    assert all(spec.claim_boundary == "run_plan_only_not_confirmation_result" for spec in specs)

    report = module["validate_run_plan"](specs)
    assert report["valid"] is True
    assert report["checked_run_count"] == 8


def test_confirmation_plan_bundle_root_override(tmp_path: Path) -> None:
    module = runpy.run_path("scripts/plan_exception_mining_confirmation.py")

    root = tmp_path / "portable_bundles"
    bundle = root / "F02" / "candidate_b"
    bundle.mkdir(parents=True)
    for name in [
        "instance.json.gz",
        "graph_metis.graph",
        "graph_edges.edgelist",
        "manifest_row.json",
        "sha256sums.txt",
    ]:
        (bundle / name).write_text("x\n", encoding="utf-8")

    candidate = {
        "candidate_id": "candidate_b",
        "family": "F02",
        "environment_target": "server_expanded",
        "variant": "server_a",
        "priority_label_from_screening": "strong_exception_candidate",
        "confirmation_portfolio": "KaHIP;TS-Rust",
        "confirmation_budgets_ms": "1000",
        "confirmation_seeds": "46",
        "bundle_path": "/nonportable/old/path/candidate_b",
    }

    specs = module["build_run_plan"](
        [candidate],
        output_root=tmp_path / "out",
        environment_id="portable_env",
        bundle_root_override=root,
        profile="issue102",
    )

    assert len(specs) == 2
    assert {spec.algo for spec in specs} == {"kahip", "ts_rust"}
    assert all(Path(spec.bundle_path) == bundle.resolve() for spec in specs)
    assert all(Path(spec.instance_path).name == "instance.json.gz" for spec in specs)


def test_confirmation_plan_cli_smoke_writes_outputs(tmp_path: Path) -> None:
    module = runpy.run_path("scripts/plan_exception_mining_confirmation.py")
    main = module["main"]

    root = tmp_path / "bundles"
    candidates = []
    for idx in range(2):
        candidate_id = f"candidate_{idx}"
        family = "F01"
        bundle = root / family / candidate_id
        bundle.mkdir(parents=True)
        for name in [
            "instance.json.gz",
            "graph_metis.graph",
            "graph_edges.edgelist",
            "manifest_row.json",
            "sha256sums.txt",
        ]:
            (bundle / name).write_text("x\n", encoding="utf-8")

        candidates.append(
            {
                "candidate_id": candidate_id,
                "family": family,
                "environment_target": "common",
                "variant": "common_a",
                "priority_label_from_screening": "near_tie_candidate",
                "confirmation_portfolio": "METIS;KaHIP;SA",
                "confirmation_budgets_ms": "100;250;500",
                "confirmation_seeds": "42;43;44",
                "bundle_path": str(bundle),
            }
        )

    manifest = {
        "metadata": {
            "freeze_id": "candidate_freeze_test",
            "selection_policy": "test_policy",
        },
        "candidates": candidates,
    }
    manifest_path = tmp_path / "confirmation_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    output_root = tmp_path / "plan"
    rc = main(
        [
            "--confirmation-manifest",
            str(manifest_path),
            "--output-root",
            str(output_root),
            "--environment-id",
            "smoke_env",
            "--profile",
            "smoke",
        ]
    )

    assert rc == 0
    summary = json.loads((output_root / "confirmation_plan_summary.json").read_text())
    assert summary["classification"] == "confirmation_run_plan_only"
    assert summary["environment_id"] == "smoke_env"
    assert summary["planned_candidate_count"] == 2
    assert summary["planned_run_count"] == 16
    assert summary["validation"]["valid"] is True
