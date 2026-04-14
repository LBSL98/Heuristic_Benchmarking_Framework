"""Canonical Tabu Search scaffold for k-way graph partitioning.

This module keeps TS local to the canonical GPP state representation. It does
not yet extend the official runner or CLI surfaces. The goal is to validate a
deterministic tabu-based local search kernel before wiring TS into the
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
class TSConfig:
    """Configuration of the canonical TS scaffold."""

    seed: int
    budget_time_ms: int
    max_steps: int = 10_000
    min_tenure: int = 5
    tenure_scale: float = 1.0
    tenure_jitter: int = 4
    checkpoint_every_nfe: int = 100
    frequency_penalty: float = 0.01


@dataclass(frozen=True)
class TSResult:
    """Structured result returned by the canonical TS scaffold."""

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


def _compute_tenure(n: int, config: TSConfig, rng: random.Random) -> int:
    """Compute a short-term tabu tenure with mild random jitter."""
    base = max(int(config.min_tenure), int(round(float(config.tenure_scale) * (n**0.5))))
    jitter = rng.randint(0, max(0, int(config.tenure_jitter)))
    return base + jitter


def run_ts_partition(
    adj: dict[Vertex, set[Vertex]],
    *,
    k: int,
    epsilon: float,
    config: TSConfig,
) -> TSResult:
    """Run a minimal deterministic TS kernel over the canonical GPP state."""
    rng = random.Random(config.seed)
    current = build_initial_state(adj, k=k, epsilon=epsilon, seed=config.seed)

    best = clone_state(current)
    best_cutsize = int(current.cutsize)

    nfe = 0
    step = 0
    tabu_until: dict[tuple[Vertex, Block], int] = {}
    move_frequency: dict[tuple[Vertex, Block], int] = {}
    checkpoints: list[SACheckpoint] = [SACheckpoint(time_ms=0, cutsize_best=best_cutsize, nfe=0)]

    t0 = time.perf_counter()
    status = "ok"

    while step < int(config.max_steps):
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        if elapsed_ms >= int(config.budget_time_ms):
            status = "timeout"
            break

        vertices = list(current.boundary) if current.boundary else list(current.part_of.keys())
        rng.shuffle(vertices)

        best_move: tuple[float, int, int, Vertex, Block, Block] | None = None

        for v in vertices:
            source = current.part_of[v]
            targets = list(range(current.k))
            rng.shuffle(targets)

            for target in targets:
                if target == source:
                    continue
                if not is_move_feasible(current, v, target):
                    continue

                delta = eval_move_delta_cut(current, v, target)
                nfe += 1

                candidate_cut = int(current.cutsize + delta)
                tabu_key = (v, target)
                is_tabu = step < tabu_until.get(tabu_key, -1)
                aspiration = candidate_cut < best_cutsize

                if is_tabu and not aspiration:
                    continue

                freq = move_frequency.get((v, target), 0)
                score = float(candidate_cut) + float(config.frequency_penalty) * float(freq)

                candidate = (
                    score,
                    int(delta),
                    len(current.adj[v]),
                    int(v),
                    int(target),
                    int(source),
                )

                if best_move is None or candidate < best_move:
                    best_move = candidate

        if best_move is None:
            break

        _score, _delta, _deg, v_sel, target_sel, source_sel = best_move
        apply_move(current, v_sel, target_sel)

        move_frequency[(v_sel, target_sel)] = move_frequency.get((v_sel, target_sel), 0) + 1
        tabu_until[(v_sel, source_sel)] = step + _compute_tenure(len(adj), config, rng)

        if current.cutsize < best_cutsize:
            best = clone_state(current)
            best_cutsize = int(current.cutsize)

        step += 1

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

    return TSResult(
        best_part_of=dict(best.part_of),
        best_cutsize=best_cutsize,
        elapsed_ms=elapsed_ms,
        nfe=nfe,
        checkpoints=checkpoints,
        status=status,
    )


__all__ = [
    "TSConfig",
    "TSResult",
    "clone_state",
    "run_ts_partition",
]
