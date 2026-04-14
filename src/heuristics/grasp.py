"""Canonical GRASP scaffold for k-way graph partitioning.

This module keeps GRASP local to the canonical GPP state representation. It
does not yet extend the official runner or CLI surfaces. The goal is to
validate a deterministic greedy-randomized construction + local descent kernel
before wiring GRASP into the declarative execution flow.
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
    compute_cutsize_naive,
    recompute_boundary,
)
from heuristics.ils import first_improvement_descent
from heuristics.sa import SACheckpoint


@dataclass(frozen=True)
class GRASPConfig:
    """Configuration of the canonical GRASP scaffold."""

    seed: int
    budget_time_ms: int
    alpha: float = 0.30
    max_iters: int = 100
    checkpoint_every_iter: int = 1


@dataclass(frozen=True)
class GRASPResult:
    """Structured result returned by the canonical GRASP scaffold."""

    best_part_of: dict[Vertex, Block]
    best_cutsize: int
    elapsed_ms: int
    nfe: int
    checkpoints: list[SACheckpoint]
    status: str


def construct_greedy_randomized_state(
    adj: dict[Vertex, set[Vertex]],
    *,
    k: int,
    epsilon: float,
    rng: random.Random,
    alpha: float,
) -> PartitionState:
    """Build a balanced greedy-randomized initial partition."""
    if k <= 0:
        raise ValueError("k must be positive")
    if k > len(adj):
        raise ValueError("k cannot exceed the number of vertices")
    if not 0.0 <= float(alpha) <= 1.0:
        raise ValueError("alpha must be in [0,1]")

    vertices = list(adj.keys())
    rng.shuffle(vertices)

    n = len(vertices)
    max_block_size = math.ceil((1.0 + epsilon) * n / k)

    # Target quotas keep the constructor balanced whenever exact balancing is
    # possible. This is stricter than the feasibility cap and matches the
    # deterministic scaffold contract used in the tests.
    base_quota = n // k
    remainder = n % k
    target_size: dict[Block, int] = {b: base_quota + (1 if b < remainder else 0) for b in range(k)}

    part_of: dict[Vertex, Block] = {}
    block_size: dict[Block, int] = dict.fromkeys(range(k), 0)

    # Seed one vertex per block so every block starts non-empty.
    for block, v in enumerate(vertices[:k]):
        part_of[v] = block
        block_size[block] += 1

    for v in vertices[k:]:
        candidates: list[tuple[int, Block]] = []

        for block in range(k):
            if block_size[block] >= max_block_size:
                continue
            if block_size[block] >= target_size[block]:
                continue

            # Greedy score: number of already-assigned incident edges that would
            # become cut edges if v were placed in this block.
            score = sum(1 for u in adj[v] if u in part_of and part_of[u] != block)
            candidates.append((score, block))

        if not candidates:
            remaining_capacity = {
                block: target_size[block] - block_size[block] for block in range(k)
            }
            positive_blocks = [block for block, cap in remaining_capacity.items() if cap > 0]
            if positive_blocks:
                min_size = min(block_size[block] for block in positive_blocks)
                tied = [block for block in positive_blocks if block_size[block] == min_size]
            else:
                min_size = min(block_size.values())
                tied = [block for block, size in block_size.items() if size == min_size]
            chosen = rng.choice(tied)
        else:
            scores = [score for score, _block in candidates]
            s_min = min(scores)
            s_max = max(scores)
            threshold = s_min + float(alpha) * (s_max - s_min)
            rcl = [block for score, block in candidates if score <= threshold + 1e-12]
            chosen = rng.choice(rcl)

        part_of[v] = chosen
        block_size[chosen] += 1

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


def run_grasp_partition(
    adj: dict[Vertex, set[Vertex]],
    *,
    k: int,
    epsilon: float,
    config: GRASPConfig,
) -> GRASPResult:
    """Run a minimal deterministic GRASP kernel over the canonical GPP state."""
    rng = random.Random(config.seed)
    t0 = time.perf_counter()

    initial = construct_greedy_randomized_state(
        adj,
        k=k,
        epsilon=epsilon,
        rng=rng,
        alpha=float(config.alpha),
    )
    initial, nfe = first_improvement_descent(initial, rng=rng, nfe_start=0)

    best_part_of = dict(initial.part_of)
    best_cutsize = int(initial.cutsize)
    checkpoints: list[SACheckpoint] = [SACheckpoint(time_ms=0, cutsize_best=best_cutsize, nfe=nfe)]
    status = "ok"

    for iteration in range(1, int(config.max_iters)):
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        if elapsed_ms >= int(config.budget_time_ms):
            status = "timeout"
            break

        candidate = construct_greedy_randomized_state(
            adj,
            k=k,
            epsilon=epsilon,
            rng=rng,
            alpha=float(config.alpha),
        )
        candidate, nfe = first_improvement_descent(candidate, rng=rng, nfe_start=nfe)

        if candidate.cutsize < best_cutsize:
            best_part_of = dict(candidate.part_of)
            best_cutsize = int(candidate.cutsize)

        if iteration % int(config.checkpoint_every_iter) == 0:
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

    return GRASPResult(
        best_part_of=best_part_of,
        best_cutsize=best_cutsize,
        elapsed_ms=elapsed_ms,
        nfe=nfe,
        checkpoints=checkpoints,
        status=status,
    )


__all__ = [
    "GRASPConfig",
    "GRASPResult",
    "construct_greedy_randomized_state",
    "run_grasp_partition",
]
