"""Tests for the canonical GRASP scaffold."""

from __future__ import annotations

import random

from gpp_core.operator import compute_cutsize_naive
from heuristics.grasp import GRASPConfig, construct_greedy_randomized_state, run_grasp_partition


def _path_adj(n: int) -> dict[int, set[int]]:
    adj = {i: set() for i in range(n)}
    for i in range(n - 1):
        adj[i].add(i + 1)
        adj[i + 1].add(i)
    return adj


def test_construct_greedy_randomized_state_is_deterministic_and_balanced():
    adj = _path_adj(10)

    s1 = construct_greedy_randomized_state(
        adj,
        k=2,
        epsilon=0.03,
        rng=random.Random(42),
        alpha=0.30,
    )
    s2 = construct_greedy_randomized_state(
        adj,
        k=2,
        epsilon=0.03,
        rng=random.Random(42),
        alpha=0.30,
    )

    assert s1.part_of == s2.part_of
    assert s1.block_size == s2.block_size
    assert s1.cutsize == compute_cutsize_naive(adj, s1.part_of)
    assert sorted(s1.block_size.values()) == [5, 5]


def test_run_grasp_partition_returns_valid_anytime_result():
    adj = _path_adj(14)
    initial = construct_greedy_randomized_state(
        adj,
        k=2,
        epsilon=0.10,
        rng=random.Random(11),
        alpha=0.30,
    )

    result = run_grasp_partition(
        adj,
        k=2,
        epsilon=0.10,
        config=GRASPConfig(
            seed=11,
            budget_time_ms=200,
            alpha=0.30,
            max_iters=40,
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


def test_run_grasp_partition_is_deterministic_with_fixed_seed_and_iters():
    adj = _path_adj(10)
    cfg = GRASPConfig(
        seed=123,
        budget_time_ms=10_000,
        alpha=0.25,
        max_iters=20,
        checkpoint_every_iter=1,
    )

    r1 = run_grasp_partition(adj, k=2, epsilon=0.10, config=cfg)
    r2 = run_grasp_partition(adj, k=2, epsilon=0.10, config=cfg)

    assert r1.best_part_of == r2.best_part_of
    assert r1.best_cutsize == r2.best_cutsize
    assert r1.nfe == r2.nfe
