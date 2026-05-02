# gpp_fidelity_core

Shared Rust foundation for fidelity implementations of graph partitioning metaheuristics.

This crate is infrastructure only. It does not implement SA-Rust, ILS-Rust, GRASP-Rust, or any evidence-bearing benchmark algorithm by itself.

## Scope

The crate provides the shared low-level surface required by future Rust fidelity implementations:

- METIS `.graph` parsing for simple undirected unweighted graphs;
- adjacency representation;
- partition state;
- balanced shuffled round-robin initial state;
- cut recomputation;
- boundary recomputation;
- move feasibility;
- delta-cut evaluation;
- move application;
- lightweight deterministic RNG;
- checkpoint/result helper structs.

## Claim boundary

This crate supports implementation readiness only. It does not support performance claims, selector claims, algorithmic superiority claims, or claims about the completed Rust portfolio.
