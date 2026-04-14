"""Tests for the canonical TS scaffold."""

from __future__ import annotations

from gpp_core.operator import compute_cutsize_naive
from heuristics.sa import build_initial_state
from heuristics.ts import TSConfig, run_ts_partition


def _path_adj(n: int) -> dict[int, set[int]]:
    adj = {i: set() for i in range(n)}
    for i in range(n - 1):
        adj[i].add(i + 1)
        adj[i + 1].add(i)
    return adj


def test_run_ts_partition_returns_valid_anytime_result():
    adj = _path_adj(12)
    initial = build_initial_state(adj, k=3, epsilon=0.10, seed=7)

    result = run_ts_partition(
        adj,
        k=3,
        epsilon=0.10,
        config=TSConfig(
            seed=7,
            budget_time_ms=200,
            max_steps=500,
            min_tenure=3,
            tenure_scale=1.0,
            tenure_jitter=2,
            checkpoint_every_nfe=10,
            frequency_penalty=0.01,
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


def test_run_ts_partition_is_deterministic_with_fixed_seed_and_steps():
    adj = _path_adj(10)
    cfg = TSConfig(
        seed=123,
        budget_time_ms=10_000,
        max_steps=50,
        min_tenure=3,
        tenure_scale=1.0,
        tenure_jitter=2,
        checkpoint_every_nfe=5,
        frequency_penalty=0.01,
    )

    r1 = run_ts_partition(adj, k=2, epsilon=0.10, config=cfg)
    r2 = run_ts_partition(adj, k=2, epsilon=0.10, config=cfg)

    assert r1.best_part_of == r2.best_part_of
    assert r1.best_cutsize == r2.best_cutsize
    assert r1.nfe == r2.nfe


def test_run_ts_partition_preserves_balance_contract():
    adj = _path_adj(14)

    result = run_ts_partition(
        adj,
        k=2,
        epsilon=0.10,
        config=TSConfig(
            seed=19,
            budget_time_ms=200,
            max_steps=100,
            min_tenure=3,
            tenure_scale=1.0,
            tenure_jitter=2,
            checkpoint_every_nfe=10,
            frequency_penalty=0.01,
        ),
    )

    block_counts: dict[int, int] = {}
    for block in result.best_part_of.values():
        block_counts[block] = block_counts.get(block, 0) + 1

    n = len(adj)
    max_allowed = int((1.0 + 0.10) * (n / 2)) + 1
    assert max(block_counts.values()) <= max_allowed
