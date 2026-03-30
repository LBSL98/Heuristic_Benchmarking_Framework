"""Canonical iterated local search scaffold for k-way graph partitioning.

This module keeps ILS local to the canonical GPP state representation. It does
not yet extend the official runner or CLI surfaces. The goal is to validate a
deterministic perturbation + descent kernel before wiring ILS into the
declarative execution flow.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

from gpp_core.operator import (
    Block,
    PartitionState,
    Vertex,
    apply_move,
    eval_move_delta_cut,
    is_move_feasible,
)
from heuristics.sa import SACheckpoint, build_initial_state


@dataclass(frozen=True)
class ILSConfig:
    """Configuration of the canonical ILS scaffold."""

    seed: int
    budget_time_ms: int
    max_iters: int = 100
    perturb_moves: int = 2
    checkpoint_every_iter: int = 1


@dataclass(frozen=True)
class ILSResult:
    """Structured result returned by the canonical ILS scaffold."""

    best_part_of: dict[Vertex, Block]
    best_cutsize: int
    elapsed_ms: int
    nfe: int
    checkpoints: list[SACheckpoint]
    status: str


def clone_state(state: PartitionState) -> PartitionState:
    """Return a detached copy of a partition state."""
    return PartitionState(
        adj=state.adj,
        part_of=dict(state.part_of),
        block_size=dict(state.block_size),
        k=state.k,
        epsilon=state.epsilon,
        cutsize=int(state.cutsize),
        boundary=set(state.boundary),
    )


def first_improvement_descent(
    state: PartitionState,
    *,
    rng: random.Random,
    nfe_start: int = 0,
) -> tuple[PartitionState, int]:
    """Run first-improvement local descent until no improving 1-move exists."""
    nfe = int(nfe_start)

    while True:
        improved = False
        vertices = list(state.boundary) if state.boundary else list(state.part_of.keys())
        rng.shuffle(vertices)

        for v in vertices:
            targets = list(range(state.k))
            rng.shuffle(targets)

            for target in targets:
                if target == state.part_of[v]:
                    continue
                if not is_move_feasible(state, v, target):
                    continue

                delta = eval_move_delta_cut(state, v, target)
                nfe += 1

                if delta < 0:
                    apply_move(state, v, target)
                    improved = True
                    break

            if improved:
                break

        if not improved:
            return state, nfe


def perturb_state(state: PartitionState, *, rng: random.Random, moves: int) -> None:
    """Apply a small number of feasible random moves in-place."""
    vertices = list(state.part_of.keys())

    for _ in range(max(1, int(moves))):
        rng.shuffle(vertices)
        moved = False

        for v in vertices:
            targets = list(range(state.k))
            rng.shuffle(targets)

            for target in targets:
                if target == state.part_of[v]:
                    continue
                if not is_move_feasible(state, v, target):
                    continue

                apply_move(state, v, target)
                moved = True
                break

            if moved:
                break


def run_ils_partition(
    adj: dict[Vertex, set[Vertex]],
    *,
    k: int,
    epsilon: float,
    config: ILSConfig,
) -> ILSResult:
    """Run a minimal deterministic ILS kernel over the canonical GPP state."""
    rng = random.Random(config.seed)

    current = build_initial_state(adj, k=k, epsilon=epsilon, seed=config.seed)
    current, nfe = first_improvement_descent(current, rng=rng, nfe_start=0)

    best = clone_state(current)
    best_cutsize = int(current.cutsize)
    checkpoints: list[SACheckpoint] = [SACheckpoint(time_ms=0, cutsize_best=best_cutsize, nfe=nfe)]

    t0 = time.perf_counter()
    status = "ok"

    for iteration in range(int(config.max_iters)):
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        if elapsed_ms >= int(config.budget_time_ms):
            status = "timeout"
            break

        candidate = clone_state(current)
        perturb_state(candidate, rng=rng, moves=config.perturb_moves)
        candidate, nfe = first_improvement_descent(candidate, rng=rng, nfe_start=nfe)

        if candidate.cutsize <= current.cutsize:
            current = clone_state(candidate)

        if candidate.cutsize < best_cutsize:
            best = clone_state(candidate)
            best_cutsize = int(candidate.cutsize)

        if (iteration + 1) % int(config.checkpoint_every_iter) == 0:
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

    return ILSResult(
        best_part_of=dict(best.part_of),
        best_cutsize=best_cutsize,
        elapsed_ms=elapsed_ms,
        nfe=nfe,
        checkpoints=checkpoints,
        status=status,
    )


__all__ = [
    "ILSConfig",
    "ILSResult",
    "clone_state",
    "first_improvement_descent",
    "perturb_state",
    "run_ils_partition",
]
