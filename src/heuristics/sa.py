"""Canonical simulated annealing scaffold for k-way graph partitioning.

This module is intentionally local and pure-Python. It does not yet modify the
official HPC runner surface. The goal is to validate a deterministic anytime
search kernel over the canonical GPP state representation before wiring SA into
plans, CLI, and JSON artifacts.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from gpp_core.operator import (
    Block,
    PartitionState,
    Vertex,
    apply_move,
    compute_cutsize_naive,
    eval_move_delta_cut,
    is_move_feasible,
    recompute_boundary,
)


@dataclass(frozen=True)
class SACheckpoint:
    """Anytime checkpoint emitted by the SA kernel."""

    time_ms: int
    cutsize_best: int
    nfe: int


@dataclass(frozen=True)
class SAConfig:
    """Configuration of the canonical SA scaffold."""

    seed: int
    budget_time_ms: int
    initial_temp: float = 1.0
    cooling: float = 0.995
    min_temp: float = 1e-3
    max_steps: int = 10_000
    checkpoint_every_nfe: int = 100


@dataclass(frozen=True)
class SAResult:
    """Structured result returned by the canonical SA scaffold."""

    best_part_of: dict[Vertex, Block]
    best_cutsize: int
    elapsed_ms: int
    nfe: int
    checkpoints: list[SACheckpoint]
    status: str


def build_initial_state(
    adj: dict[Vertex, set[Vertex]],
    *,
    k: int,
    epsilon: float,
    seed: int,
) -> PartitionState:
    """Build a balanced initial partition using shuffled round-robin assignment."""
    if k <= 0:
        raise ValueError("k must be positive")
    if k > len(adj):
        raise ValueError("k cannot exceed the number of vertices")

    rng = random.Random(seed)
    vertices = list(adj.keys())
    rng.shuffle(vertices)

    part_of: dict[Vertex, Block] = {}
    block_size: dict[Block, int] = dict.fromkeys(range(k), 0)

    for i, v in enumerate(vertices):
        block = i % k
        part_of[v] = block
        block_size[block] += 1

    cutsize = compute_cutsize_naive(adj, part_of)
    boundary = recompute_boundary(adj, part_of)

    return PartitionState(
        adj=adj,
        part_of=part_of,
        block_size=block_size,
        k=k,
        epsilon=epsilon,
        cutsize=cutsize,
        boundary=boundary,
    )


def run_sa_partition(
    adj: dict[Vertex, set[Vertex]],
    *,
    k: int,
    epsilon: float,
    config: SAConfig,
) -> SAResult:
    """Run a minimal deterministic anytime SA kernel over the canonical GPP state."""
    state = build_initial_state(adj, k=k, epsilon=epsilon, seed=config.seed)

    rng = random.Random(config.seed)
    best_part_of = dict(state.part_of)
    best_cutsize = state.cutsize
    nfe = 0
    checkpoints: list[SACheckpoint] = [SACheckpoint(time_ms=0, cutsize_best=best_cutsize, nfe=0)]

    temp = max(float(config.initial_temp), 1e-12)
    t0 = time.perf_counter()
    status = "ok"

    for _step in range(int(config.max_steps)):
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        if elapsed_ms >= int(config.budget_time_ms):
            status = "timeout"
            break

        candidates = list(state.boundary) if state.boundary else list(state.part_of.keys())
        if not candidates:
            break

        v = rng.choice(candidates)
        target_blocks = list(range(k))
        rng.shuffle(target_blocks)

        for target in target_blocks:
            if not is_move_feasible(state, v, target):
                continue

            delta = eval_move_delta_cut(state, v, target)
            nfe += 1

            accept = delta <= 0
            if not accept:
                accept_prob = math.exp(-float(delta) / max(temp, 1e-12))
                accept = rng.random() < accept_prob

            if accept:
                apply_move(state, v, target)
                if state.cutsize < best_cutsize:
                    best_cutsize = state.cutsize
                    best_part_of = dict(state.part_of)
                break

        temp = max(float(config.min_temp), temp * float(config.cooling))

        if nfe > 0 and nfe % int(config.checkpoint_every_nfe) == 0:
            checkpoints.append(
                SACheckpoint(
                    time_ms=int((time.perf_counter() - t0) * 1000),
                    cutsize_best=best_cutsize,
                    nfe=nfe,
                )
            )

    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    if checkpoints[-1].nfe != nfe or checkpoints[-1].cutsize_best != best_cutsize:
        checkpoints.append(
            SACheckpoint(
                time_ms=elapsed_ms,
                cutsize_best=best_cutsize,
                nfe=nfe,
            )
        )

    return SAResult(
        best_part_of=best_part_of,
        best_cutsize=best_cutsize,
        elapsed_ms=elapsed_ms,
        nfe=nfe,
        checkpoints=checkpoints,
        status=status,
    )
