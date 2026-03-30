"""Tests for the canonical ILS scaffold."""

from __future__ import annotations

import random

from gpp_core.operator import compute_cutsize_naive
from heuristics.ils import (
    ILSConfig,
    clone_state,
    first_improvement_descent,
    perturb_state,
    run_ils_partition,
)
from heuristics.sa import build_initial_state


def _path_adj(n: int) -> dict[int, set[int]]:
    adj = {i: set() for i in range(n)}
    for i in range(n - 1):
        adj[i].add(i + 1)
        adj[i + 1].add(i)
    return adj


def test_first_improvement_descent_never_worsens_cut():
    adj = _path_adj(12)
    state = build_initial_state(adj, k=3, epsilon=0.10, seed=42)
    initial_cut = state.cutsize

    result_state, nfe = first_improvement_descent(
        clone_state(state),
        rng=random.Random(42),
        nfe_start=0,
    )

    assert nfe >= 0
    assert result_state.cutsize <= initial_cut
    assert result_state.cutsize == compute_cutsize_naive(adj, result_state.part_of)


def test_perturb_state_keeps_partition_defined():
    adj = _path_adj(10)
    state = build_initial_state(adj, k=2, epsilon=0.10, seed=7)

    perturb_state(state, rng=random.Random(7), moves=3)

    assert len(state.part_of) == 10
    assert sum(state.block_size.values()) == 10
    assert state.cutsize == compute_cutsize_naive(adj, state.part_of)


def test_run_ils_partition_returns_valid_anytime_result():
    adj = _path_adj(14)
    initial = build_initial_state(adj, k=2, epsilon=0.10, seed=11)

    result = run_ils_partition(
        adj,
        k=2,
        epsilon=0.10,
        config=ILSConfig(
            seed=11,
            budget_time_ms=200,
            max_iters=40,
            perturb_moves=2,
            checkpoint_every_iter=2,
        ),
    )

    assert result.status in {"ok", "timeout"}
    assert result.best_cutsize <= initial.cutsize
    assert result.best_cutsize == compute_cutsize_naive(adj, result.best_part_of)
    assert result.nfe >= 0
    assert len(result.checkpoints) >= 1

    times = [cp.time_ms for cp in result.checkpoints]
    nfes = [cp.nfe for cp in result.checkpoints]

    assert times == sorted(times)
    assert nfes == sorted(nfes)
    assert result.checkpoints[-1].cutsize_best == result.best_cutsize
    assert result.checkpoints[-1].nfe == result.nfe


def test_run_ils_partition_is_deterministic_with_fixed_seed_and_iters():
    adj = _path_adj(10)
    cfg = ILSConfig(
        seed=123,
        budget_time_ms=10_000,
        max_iters=20,
        perturb_moves=2,
        checkpoint_every_iter=1,
    )

    r1 = run_ils_partition(adj, k=2, epsilon=0.10, config=cfg)
    r2 = run_ils_partition(adj, k=2, epsilon=0.10, config=cfg)

    assert r1.best_part_of == r2.best_part_of
    assert r1.best_cutsize == r2.best_cutsize
    assert r1.nfe == r2.nfe
