import json
from pathlib import Path

from scripts.validate_ts_rust_fidelity import run_validation


def test_ts_rust_validation_script_produces_passing_report(tmp_path: Path):
    out = tmp_path / "ts_rust_validation_report.json"

    report = run_validation(out)

    assert out.exists()
    persisted = json.loads(out.read_text(encoding="utf-8"))
    assert persisted["passed"] is True
    assert report["passed"] is True
    assert len(report["cases"]) == 3

    for case in report["cases"]:
        assert case["passed"] is True
        assert case["checks"]["python_cut_matches_labels"] is True
        assert case["checks"]["rust_cut_matches_labels"] is True
        assert case["checks"]["python_feasible"] is True
        assert case["checks"]["rust_feasible"] is True
        assert case["checks"]["python_checkpoint_invariants"] is True
        assert case["checks"]["rust_checkpoint_invariants"] is True
