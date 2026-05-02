import importlib.util
import sys
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = REPO_ROOT / "src" / "hpc_framework" / "ts_rust_adapter.py"


def _load_adapter_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ts_rust_adapter_under_test", ADAPTER_PATH)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_ts_rust_manifest_path_resolves_from_repo_cwd(monkeypatch):
    adapter = _load_adapter_module()
    expected = REPO_ROOT / "rust" / "ts_rust_fidelity" / "Cargo.toml"

    monkeypatch.delenv("TS_RUST_MANIFEST_PATH", raising=False)
    monkeypatch.delenv("TS_RUST_REPO_ROOT", raising=False)

    assert adapter.ts_rust_manifest_path() == expected
    assert adapter.ts_rust_manifest_path().exists()


def test_ts_rust_manifest_path_accepts_explicit_env_override(monkeypatch, tmp_path):
    adapter = _load_adapter_module()
    explicit = tmp_path / "Cargo.toml"
    explicit.write_text('[package]\nname = "dummy"\n', encoding="utf-8")

    monkeypatch.setenv("TS_RUST_MANIFEST_PATH", str(explicit))

    assert adapter.ts_rust_manifest_path() == explicit
