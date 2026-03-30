"""Tests for the canonical SA scaffold."""

from __future__ import annotations

from gpp_core.operator import compute_cutsize_naive, recompute_boundary
from heuristics.sa import SAConfig, build_initial_state, run_sa_partition


def _path_adj(n: int) -> dict[int, set[int]]:
    adj = {i: set() for i in range(n)}
    for i in range(n - 1):
        adj[i].add(i + 1)
        adj[i + 1].add(i)
    return adj


def test_build_initial_state_is_deterministic_and_balanced():
    adj = _path_adj(10)

    s1 = build_initial_state(adj, k=2, epsilon=0.03, seed=42)
    s2 = build_initial_state(adj, k=2, epsilon=0.03, seed=42)

    assert s1.part_of == s2.part_of
    assert s1.block_size == s2.block_size
    assert s1.cutsize == compute_cutsize_naive(adj, s1.part_of)
    assert s1.boundary == recompute_boundary(adj, s1.part_of)
    assert sorted(s1.block_size.values()) == [5, 5]


def test_run_sa_partition_returns_valid_anytime_result():
    adj = _path_adj(12)
    initial = build_initial_state(adj, k=3, epsilon=0.10, seed=7)

    result = run_sa_partition(
        adj,
        k=3,
        epsilon=0.10,
        config=SAConfig(
            seed=7,
            budget_time_ms=200,
            initial_temp=1.0,
            cooling=0.99,
            min_temp=1e-3,
            max_steps=500,
            checkpoint_every_nfe=10,
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


def test_run_sa_partition_is_deterministic_with_fixed_seed_and_steps():
    adj = _path_adj(10)
    cfg = SAConfig(
        seed=123,
        budget_time_ms=10_000,
        initial_temp=1.0,
        cooling=0.99,
        min_temp=1e-3,
        max_steps=50,
        checkpoint_every_nfe=5,
    )

    r1 = run_sa_partition(adj, k=2, epsilon=0.10, config=cfg)
    r2 = run_sa_partition(adj, k=2, epsilon=0.10, config=cfg)

    assert r1.best_part_of == r2.best_part_of
    assert r1.best_cutsize == r2.best_cutsize
    assert r1.nfe == r2.nfe
