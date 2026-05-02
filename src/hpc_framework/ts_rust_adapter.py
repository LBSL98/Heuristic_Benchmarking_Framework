"""Adapter for the TS-Rust-fidelity binary.

The Rust implementation is kept as a parallel ablation target. It does not
replace the canonical Python TS implementation.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TSRustRun:
    """Result returned by the TS-Rust adapter."""

    payload: dict[str, Any]
    stdout: str
    stderr: str
    returncode: int


def _candidate_repo_roots() -> list[Path]:
    """Return candidate repository roots that may contain the Rust crate."""
    candidates: list[Path] = []

    explicit_root = os.environ.get("TS_RUST_REPO_ROOT")
    if explicit_root:
        candidates.append(Path(explicit_root))

    candidates.append(Path.cwd())

    source_path = Path(__file__).resolve()
    candidates.extend(source_path.parents)

    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def ts_rust_manifest_path() -> Path:
    """Return the Cargo manifest path for the TS-Rust-fidelity crate."""
    explicit_manifest = os.environ.get("TS_RUST_MANIFEST_PATH")
    if explicit_manifest:
        return Path(explicit_manifest)

    for root in _candidate_repo_roots():
        candidate = root / "rust" / "ts_rust_fidelity" / "Cargo.toml"
        if candidate.exists():
            return candidate

    return Path.cwd() / "rust" / "ts_rust_fidelity" / "Cargo.toml"


def ts_rust_binary_path() -> Path:
    """Return the expected release binary path for TS-Rust-fidelity."""
    exe_name = "ts_rust_fidelity.exe" if os.name == "nt" else "ts_rust_fidelity"
    return ts_rust_manifest_path().parent / "target" / "release" / exe_name


def ts_rust_available() -> bool:
    """Return whether TS-Rust can be built or is already available."""
    return ts_rust_manifest_path().exists() and (
        ts_rust_binary_path().exists() or shutil.which("cargo") is not None
    )


def ensure_ts_rust_binary() -> Path:
    """Build TS-Rust-fidelity when needed and return the release binary path."""
    manifest = ts_rust_manifest_path()
    if not manifest.exists():
        raise RuntimeError(f"TS-Rust-fidelity Cargo.toml not found: {manifest}")

    binary = ts_rust_binary_path()
    if binary.exists():
        return binary

    if shutil.which("cargo") is None:
        raise RuntimeError("cargo not found; TS-Rust-fidelity cannot be built")

    cp = subprocess.run(
        ["cargo", "build", "--release", "--manifest-path", str(manifest)],
        capture_output=True,
        text=True,
        check=False,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            "failed to build TS-Rust-fidelity with return code "
            f"{cp.returncode}: {cp.stderr.strip()}"
        )
    if not binary.exists():
        raise RuntimeError(f"TS-Rust-fidelity build did not produce binary: {binary}")

    return binary


def run_ts_rust_binary(
    *,
    graph_path: Path,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    out_json: Path,
    part_path: Path,
    max_steps: int = 10_000,
    min_tenure: int = 5,
    tenure_scale: float = 1.0,
    tenure_jitter: int = 4,
    checkpoint_every_nfe: int = 100,
    frequency_penalty: float = 0.01,
) -> TSRustRun:
    """Run TS-Rust-fidelity and load its JSON payload."""
    binary = ensure_ts_rust_binary()

    out_json.parent.mkdir(parents=True, exist_ok=True)
    part_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(binary),
        "--graph",
        str(graph_path),
        "--k",
        str(int(k)),
        "--beta",
        str(float(beta)),
        "--seed",
        str(int(seed)),
        "--budget-time-ms",
        str(int(budget_time_ms)),
        "--out-json",
        str(out_json),
        "--part",
        str(part_path),
        "--max-steps",
        str(int(max_steps)),
        "--min-tenure",
        str(int(min_tenure)),
        "--tenure-scale",
        str(float(tenure_scale)),
        "--tenure-jitter",
        str(int(tenure_jitter)),
        "--checkpoint-every-nfe",
        str(int(checkpoint_every_nfe)),
        "--frequency-penalty",
        str(float(frequency_penalty)),
    ]

    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if cp.returncode != 0:
        raise RuntimeError(
            f"TS-Rust-fidelity failed with return code {cp.returncode}: {cp.stderr.strip()}"
        )
    if not out_json.exists():
        raise RuntimeError(f"TS-Rust-fidelity did not write output JSON: {out_json}")

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    return TSRustRun(payload=payload, stdout=cp.stdout, stderr=cp.stderr, returncode=cp.returncode)
