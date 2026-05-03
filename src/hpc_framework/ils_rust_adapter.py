"""Adapter for the ILS-Rust-fidelity binary.

The Rust implementation is kept as a fidelity target for implementation-maturity
analysis. It does not replace the canonical Python ILS implementation.
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
class ILSRustRun:
    """Result returned by the ILS-Rust adapter."""

    payload: dict[str, Any]
    stdout: str
    stderr: str
    returncode: int


def _candidate_repo_roots() -> list[Path]:
    """Return candidate repository roots that may contain the Rust crate."""
    candidates: list[Path] = []

    explicit_root = os.environ.get("ILS_RUST_REPO_ROOT")
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


def ils_rust_manifest_path() -> Path:
    """Return the Cargo manifest path for ILS-Rust-fidelity."""
    explicit_manifest = os.environ.get("ILS_RUST_MANIFEST_PATH")
    if explicit_manifest:
        return Path(explicit_manifest)

    for root in _candidate_repo_roots():
        candidate = root / "rust" / "ils_rust_fidelity" / "Cargo.toml"
        if candidate.exists():
            return candidate

    return Path.cwd() / "rust" / "ils_rust_fidelity" / "Cargo.toml"


def ils_rust_binary_path() -> Path:
    """Return the expected release binary path for ILS-Rust-fidelity."""
    exe_name = "ils_rust_fidelity.exe" if os.name == "nt" else "ils_rust_fidelity"
    return ils_rust_manifest_path().parent / "target" / "release" / exe_name


def ils_rust_available() -> bool:
    """Return whether ILS-Rust can be built or is already available."""
    return ils_rust_manifest_path().exists() and (
        ils_rust_binary_path().exists() or shutil.which("cargo") is not None
    )


def ensure_ils_rust_binary() -> Path:
    """Build ILS-Rust-fidelity when needed and return the release binary path."""
    manifest = ils_rust_manifest_path()
    if not manifest.exists():
        raise RuntimeError(f"ILS-Rust-fidelity Cargo.toml not found: {manifest}")

    binary = ils_rust_binary_path()
    if binary.exists():
        return binary

    if shutil.which("cargo") is None:
        raise RuntimeError("cargo not found; ILS-Rust-fidelity cannot be built")

    cp = subprocess.run(
        ["cargo", "build", "--release", "--manifest-path", str(manifest)],
        capture_output=True,
        text=True,
        check=False,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            "failed to build ILS-Rust-fidelity with return code "
            f"{cp.returncode}: {cp.stderr.strip()}"
        )
    if not binary.exists():
        raise RuntimeError(f"ILS-Rust-fidelity build did not produce binary: {binary}")

    return binary


def run_ils_rust_binary(
    *,
    graph_path: Path,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    out_json: Path,
    part_path: Path,
    max_iters: int = 100,
    perturb_moves: int = 4,
    checkpoint_every_iter: int = 1,
) -> ILSRustRun:
    """Run ILS-Rust-fidelity and load its JSON payload."""
    binary = ensure_ils_rust_binary()

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
        "--max-iters",
        str(int(max_iters)),
        "--perturb-moves",
        str(int(perturb_moves)),
        "--checkpoint-every-iter",
        str(int(checkpoint_every_iter)),
    ]

    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if cp.returncode != 0:
        raise RuntimeError(
            f"ILS-Rust-fidelity failed with return code {cp.returncode}: {cp.stderr.strip()}"
        )
    if not out_json.exists():
        raise RuntimeError(f"ILS-Rust-fidelity did not write output JSON: {out_json}")

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    return ILSRustRun(payload=payload, stdout=cp.stdout, stderr=cp.stderr, returncode=cp.returncode)
