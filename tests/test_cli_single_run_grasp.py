import gzip
import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from hpc_framework.cli import main


def _write_instance_edges(tmp_path: Path, n: int = 10) -> Path:
    edges = [[i, i + 1] for i in range(n - 1)]
    inst = {"instance_id": "toy", "num_nodes": n, "edges": edges}
    ipath = tmp_path / "toy.json.gz"
    with gzip.open(ipath, "wt", encoding="utf-8") as f:
        json.dump(inst, f)
    return ipath


def test_cli_single_run_accepts_grasp_and_writes_output(tmp_path: Path):
    inst_path = _write_instance_edges(tmp_path, n=10)
    out_json = tmp_path / "out_grasp.json"
    workdir = tmp_path / "work"

    buf = StringIO()
    with redirect_stdout(buf):
        main(
            [
                "single-run",
                "--instance",
                str(inst_path),
                "--algo",
                "grasp",
                "--k",
                "2",
                "--beta",
                "0.10",
                "--budget-time-ms",
                "5000",
                "--seed",
                "42",
                "--out",
                str(out_json),
                "--workdir",
                str(workdir),
            ]
        )

    cli_obj = json.loads(buf.getvalue())
    assert cli_obj["algo"] == "grasp"
    assert cli_obj["status"] == "ok"
    assert out_json.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["algo"] == "grasp"
    assert data["seed"] == 42
