"""Adapter for the GRASP-Rust-fidelity binary.

The Rust implementation is kept as a fidelity target for implementation-maturity
analysis. It does not replace the canonical Python GRASP implementation.
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
class GRASPRustRun:
    """Result returned by the GRASP-Rust adapter."""

    payload: dict[str, Any]
    stdout: str
    stderr: str
    returncode: int


def _candidate_repo_roots() -> list[Path]:
    """Return candidate repository roots that may contain the Rust crate."""
    candidates: list[Path] = []

    explicit_root = os.environ.get("GRASP_RUST_REPO_ROOT")
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


def grasp_rust_manifest_path() -> Path:
    """Return the Cargo manifest path for GRASP-Rust-fidelity."""
    explicit_manifest = os.environ.get("GRASP_RUST_MANIFEST_PATH")
    if explicit_manifest:
        return Path(explicit_manifest)

    for root in _candidate_repo_roots():
        candidate = root / "rust" / "grasp_rust_fidelity" / "Cargo.toml"
        if candidate.exists():
            return candidate

    return Path.cwd() / "rust" / "grasp_rust_fidelity" / "Cargo.toml"


def grasp_rust_binary_path() -> Path:
    """Return the expected release binary path for GRASP-Rust-fidelity."""
    exe_name = "grasp_rust_fidelity.exe" if os.name == "nt" else "grasp_rust_fidelity"
    return grasp_rust_manifest_path().parent / "target" / "release" / exe_name


def grasp_rust_available() -> bool:
    """Return whether GRASP-Rust can be built or is already available."""
    return grasp_rust_manifest_path().exists() and (
        grasp_rust_binary_path().exists() or shutil.which("cargo") is not None
    )


def ensure_grasp_rust_binary() -> Path:
    """Build GRASP-Rust-fidelity when needed and return the release binary path."""
    manifest = grasp_rust_manifest_path()
    if not manifest.exists():
        raise RuntimeError(f"GRASP-Rust-fidelity Cargo.toml not found: {manifest}")

    binary = grasp_rust_binary_path()
    if binary.exists():
        return binary

    if shutil.which("cargo") is None:
        raise RuntimeError("cargo not found; GRASP-Rust-fidelity cannot be built")

    cp = subprocess.run(
        ["cargo", "build", "--release", "--manifest-path", str(manifest)],
        capture_output=True,
        text=True,
        check=False,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            "failed to build GRASP-Rust-fidelity with return code "
            f"{cp.returncode}: {cp.stderr.strip()}"
        )
    if not binary.exists():
        raise RuntimeError(f"GRASP-Rust-fidelity build did not produce binary: {binary}")

    return binary


def run_grasp_rust_binary(
    *,
    graph_path: Path,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    out_json: Path,
    part_path: Path,
    alpha: float = 0.30,
    max_iters: int = 100,
    checkpoint_every_iter: int = 1,
) -> GRASPRustRun:
    """Run GRASP-Rust-fidelity and load its JSON payload."""
    binary = ensure_grasp_rust_binary()

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
        "--alpha",
        str(float(alpha)),
        "--max-iters",
        str(int(max_iters)),
        "--checkpoint-every-iter",
        str(int(checkpoint_every_iter)),
    ]

    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if cp.returncode != 0:
        raise RuntimeError(
            f"GRASP-Rust-fidelity failed with return code {cp.returncode}: {cp.stderr.strip()}"
        )
    if not out_json.exists():
        raise RuntimeError(f"GRASP-Rust-fidelity did not write output JSON: {out_json}")

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    return GRASPRustRun(
        payload=payload, stdout=cp.stdout, stderr=cp.stderr, returncode=cp.returncode
    )
