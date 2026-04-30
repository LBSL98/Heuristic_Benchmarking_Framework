from __future__ import annotations

import csv
from pathlib import Path

import yaml

MANIFEST = Path("data/instances/regime_panel_manifest.csv")
BASE_PLAN = Path("configs/plan_phase_1_baselines.yaml")
META_PLAN = Path("configs/plan_phase_1_metaheuristics.yaml")
DATA_ROOT = Path("data/instances")


def _read_manifest():
    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _read_plan(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_regime_panel_manifest_has_r1_r2_r3_and_all_paths_exist():
    rows = _read_manifest()
    assert len(rows) == 12

    regime_counts = {}
    for row in rows:
        regime_counts[row["regime"]] = regime_counts.get(row["regime"], 0) + 1
        assert (DATA_ROOT / row["relative_path"]).exists(), row["relative_path"]

    assert regime_counts["R1"] >= 1
    assert regime_counts["R2"] >= 1
    assert regime_counts["R3"] >= 1


def test_official_phase1_plans_share_manifest_universe_and_base_dir():
    rows = _read_manifest()
    manifest_paths = [row["relative_path"] for row in rows]

    base = _read_plan(BASE_PLAN)
    meta = _read_plan(META_PLAN)

    assert base["instances"]["base_dir"] == "data/instances"
    assert meta["instances"]["base_dir"] == "data/instances"

    assert base["instances"]["include"] == manifest_paths
    assert meta["instances"]["include"] == manifest_paths


def test_official_phase1_budgets_remain_five_seconds():
    base = _read_plan(BASE_PLAN)
    meta = _read_plan(META_PLAN)

    for _solver_name, cfg in (base.get("solvers") or {}).items():
        if isinstance(cfg, dict) and cfg.get("enabled"):
            assert (((cfg or {}).get("budget") or {}).get("seconds")) == 5

    for _solver_name, cfg in (meta.get("solvers") or {}).items():
        if isinstance(cfg, dict) and cfg.get("enabled"):
            assert (((cfg or {}).get("budget") or {}).get("seconds")) == 5
