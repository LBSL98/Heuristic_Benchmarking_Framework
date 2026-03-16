from pathlib import Path

import pytest

from hpc_framework import cli as cli_mod


def test_cli_run_help_exposes_plan_argument(capsys):
    """O CLI deve expor um subcomando 'run' com argumento --plan."""
    with pytest.raises(SystemExit) as excinfo:
        cli_mod.main(["run", "--help"])

    assert excinfo.value.code == 0

    captured = capsys.readouterr()
    assert "--plan" in captured.out


def test_cli_run_delegates_to_plan_runner(monkeypatch):
    calls = []

    def fake_run_plan(plan_path: Path) -> None:
        calls.append(plan_path)

    monkeypatch.setattr(cli_mod, "run_plan", fake_run_plan)

    cli_mod.main(["run", "--plan", "configs/plan_phase_1.yaml"])

    assert len(calls) == 1
    assert calls[0] == Path("configs/plan_phase_1.yaml")
