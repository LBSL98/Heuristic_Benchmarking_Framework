import gzip
import json
import shutil
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from hpc_framework.cli import main


def _write_instance_edges(tmp_path: Path, n: int = 10) -> Path:
    edges = [[i, i + 1] for i in range(n - 1)]
    inst = {"instance_id": "toy", "num_nodes": n, "edges": edges}
    ipath = tmp_path / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo not installed")
def test_cli_single_run_accepts_ts_rust_and_writes_output(tmp_path: Path):
    inst_path = _write_instance_edges(tmp_path, n=10)
    out_json = tmp_path / "out_ts_rust.json"
    workdir = tmp_path / "work"

    buf = StringIO()
    with redirect_stdout(buf):
        main(
            [
                "single-run",
                "--instance",
                str(inst_path),
                "--algo",
                "ts_rust",
                "--k",
                "2",
                "--beta",
                "0.10",
                "--budget-time-ms",
                "1000",
                "--seed",
                "42",
                "--out",
                str(out_json),
                "--workdir",
                str(workdir),
            ]
        )

    cli_obj = json.loads(buf.getvalue())
    assert cli_obj["algo"] == "ts_rust"
    assert cli_obj["status"] in {"ok", "timeout"}
    assert out_json.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["algo"] == "ts_rust"
    assert data["seed"] == 42
    assert data["checkpoints"][-1]["cutsize_best"] == data["cutsize_best"]
