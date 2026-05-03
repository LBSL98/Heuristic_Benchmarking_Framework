import json
import shutil
from pathlib import Path

import pytest

from scripts.validate_grasp_rust_fidelity import run_validation


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo not installed")
def test_validate_grasp_rust_fidelity_script_passes(tmp_path: Path):
    out = tmp_path / "grasp_rust_validation_report.json"

    report = run_validation(out)

    assert out.exists()
    assert report["schema_version"] == "grasp-rust-validation-v1"
    assert report["passed"] is True
    assert len(report["cases"]) == 3
    assert all(case["passed"] for case in report["cases"])
    assert "performance" in report["claim_boundary"]

    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["passed"] is True
