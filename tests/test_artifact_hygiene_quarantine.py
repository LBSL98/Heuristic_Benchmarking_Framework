from pathlib import Path

from hpc_framework.artifact_hygiene import quarantine_legacy_artifacts


def test_quarantine_legacy_artifacts_moves_only_legacy_entries(tmp_path: Path):
    raw_dir = tmp_path / "results_raw"
    raw_dir.mkdir()

    legacy_json = raw_dir / "n2000_p50.json.gz__metis__seed42.json"
    legacy_workdir = raw_dir / "run_metis__n2000_p50.json.gz__seed42"
    new_json = raw_dir / "n2000_p50.json.gz__metis__k8__b0.03__seed42.json"
    new_workdir = raw_dir / "run_metis__n2000_p50.json.gz__k8__b0.03__seed42"

    legacy_json.write_text("legacy", encoding="utf-8")
    legacy_workdir.mkdir()
    (legacy_workdir / "graph.graph.part.8").write_text("part", encoding="utf-8")

    new_json.write_text("new", encoding="utf-8")
    new_workdir.mkdir()
    (new_workdir / "graph.graph.part.8").write_text("part", encoding="utf-8")

    moved = quarantine_legacy_artifacts(raw_dir)

    archive_dir = raw_dir / "_legacy_quarantine"

    assert archive_dir.exists()
    assert legacy_json.exists() is False
    assert legacy_workdir.exists() is False

    assert (archive_dir / legacy_json.name).exists()
    assert (archive_dir / legacy_workdir.name).exists()

    assert new_json.exists() is True
    assert new_workdir.exists() is True

    assert sorted(moved) == sorted([legacy_json.name, legacy_workdir.name])
