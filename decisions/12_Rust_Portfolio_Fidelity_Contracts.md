# 12_Rust_Portfolio_Fidelity_Contracts.md

## Purpose

This file freezes fidelity contracts for the planned Rust implementation-maturity layer of the stochastic metaheuristic portfolio. It covers `SA-Rust`, `ILS-Rust`, and `GRASP-Rust`. `TS-Rust` is already governed by `D-023` and the completed `EXP-TS-RUST-*` cycle.

This document is a contract, not an implementation report. It does not authorize performance claims, winner-diversity claims, CART claims, or full-portfolio claims by itself.

## Global contract

### Reference implementation

Each Rust implementation must mirror the canonical Python implementation in `src/heuristics`:

- `SA-Rust` mirrors `src/heuristics/sa.py`.
- `ILS-Rust` mirrors `src/heuristics/ils.py`.
- `GRASP-Rust` mirrors `src/heuristics/grasp.py`.

The common operator semantics come from `src/gpp_core/operator.py`.

### Frozen benchmark profiles

Evidence-bearing Rust runs must use the same frozen benchmark profiles as `D-012`:

| algorithm | profile | frozen parameters |
|---|---|---|
| `SA` | `sa_e_maxsteps_100000` | `initial_temp=1.0`, `cooling=0.997`, `min_temp=0.001`, `max_steps=100000`, `checkpoint_every_nfe=100` |
| `ILS` | `ils_b` | `max_iters=100`, `perturb_moves=4`, `checkpoint_every_iter=1` |
| `GRASP` | `grasp_b` | `alpha=0.30`, `max_iters=100`, `checkpoint_every_iter=1` |

Smoke tests may use smaller budgets or smaller iteration limits for speed, but smoke outputs cannot support performance or selector claims.

### Problem and artifact contract

All Rust implementations must preserve:

- simple undirected unweighted graph semantics;
- k-way vertex partitioning;
- unit vertex weights;
- cardinality balance using the same `beta` / `epsilon` interpretation;
- edge-cut minimization;
- zero-based block labels;
- `.part` output compatible with the existing validator;
- JSON payload compatible with `specs/jsonschema/solver_run.schema.v1.json` after framework wrapping;
- `elapsed_ms` as serialized elapsed time;
- `checkpoints[].time_ms`, `checkpoints[].cutsize_best`, and `checkpoints[].nfe`;
- final checkpoint consistency with the reported best cut and NFE;
- feasible output under the same `feasible_beta` validation surface.

### Allowed implementation differences

Rust may improve data structures, memory layout, parsing overhead, candidate enumeration efficiency, and low-level execution performance.

Rust is not required to reproduce Python's exact RNG stream or exact trajectory unless a later contract explicitly introduces an RNG-equivalence layer. Therefore, validation must not claim trajectory equivalence by default.

### Forbidden changes

The Rust fidelity layer must not introduce:

- multilevel coarsening or uncoarsening;
- METIS or KaHIP warm starts;
- memetic recombination;
- new neighborhoods;
- per-instance retuning;
- adaptive hyperparameter changes not present in the Python profile;
- different balance semantics;
- different objective semantics;
- post hoc instance selection based on observed winners;
- hidden solver variants disguised as fidelity implementations.

If any of these are introduced, the method becomes a new registered algorithmic variant and cannot be used as a fidelity implementation-maturity claim.

### Required validation before ablation

Before any Rust implementation-maturity ablation, each algorithm must pass a controlled validation surface including:

- at least three deterministic toy cases;
- independent recomputation of cut from labels;
- feasibility validation;
- checkpoint non-emptiness;
- checkpoint time monotonicity;
- best-so-far cut monotonicity;
- NFE monotonicity when NFE is exposed;
- final checkpoint matching the reported best cut and NFE;
- schema-compatible wrapped output through the framework;
- explicit claim boundary stating that validation is not trajectory equivalence and not performance evidence.

## SA-Rust fidelity contract

### Python reference

`SA-Rust` mirrors `run_sa_partition` and `SAConfig` from `src/heuristics/sa.py`.

### Frozen profile

Evidence-bearing `SA-Rust` runs use profile `sa_e_maxsteps_100000`:

- `initial_temp=1.0`;
- `cooling=0.997`;
- `min_temp=0.001`;
- `max_steps=100000`;
- `checkpoint_every_nfe=100`.

### Initial state

The initial state is the same balanced shuffled round-robin construction used by `build_initial_state`:

1. validate `k > 0`;
2. validate `k <= |V|`;
3. shuffle vertices using the algorithm seed;
4. assign vertices by round-robin to blocks;
5. compute the initial cut with the same edge-cut semantics;
6. recompute the boundary set.

Exact Python RNG stream equivalence is not required unless explicitly declared later.

### Move and acceptance semantics

Each SA step:

1. checks elapsed wall-clock time against `budget_time_ms`;
2. selects candidates from the boundary set, or all vertices if the boundary is empty;
3. chooses one candidate vertex;
4. shuffles target blocks;
5. skips infeasible moves and same-block moves through the shared operator semantics;
6. evaluates `delta` for feasible target moves and increments `nfe` per evaluated feasible move;
7. accepts if `delta <= 0`;
8. otherwise accepts with probability `exp(-delta / temp)`;
9. applies the first accepted move and exits the target-loop;
10. updates the best-so-far partition only when the current cut strictly improves the best cut;
11. updates temperature as `max(min_temp, temp * cooling)`;
12. emits checkpoints when `nfe > 0` and `nfe % checkpoint_every_nfe == 0`;
13. appends a final checkpoint if the last checkpoint does not match final best cut or final NFE.

### Known caveats

Because RNG stream equivalence is not required, `SA-Rust` validation may compare invariants, feasibility, cut recomputation, monotonicity, and artifact structure, but must not claim identical trajectories.

## ILS-Rust fidelity contract

### Python reference

`ILS-Rust` mirrors `run_ils_partition`, `first_improvement_descent`, `perturb_state`, and `ILSConfig` from `src/heuristics/ils.py`.

### Frozen profile

Evidence-bearing `ILS-Rust` runs use profile `ils_b`:

- `max_iters=100`;
- `perturb_moves=4`;
- `checkpoint_every_iter=1`.

### Initial state and descent

ILS starts from the same `build_initial_state` used by SA, then applies first-improvement local descent.

The first-improvement descent:

1. chooses vertices from the boundary set, or all vertices if the boundary is empty;
2. shuffles vertices;
3. shuffles target blocks for each vertex;
4. skips same-block and infeasible moves;
5. evaluates `delta` and increments `nfe` per evaluated feasible move;
6. applies the first strictly improving move with `delta < 0`;
7. restarts the search after an improvement;
8. stops when no improving 1-move exists.

### Perturbation and acceptance semantics

Each ILS iteration:

1. checks elapsed wall-clock time against `budget_time_ms`;
2. clones the current state;
3. applies `perturb_moves` feasible random moves in-place;
4. applies first-improvement descent to the perturbed candidate;
5. replaces the current state if `candidate.cutsize <= current.cutsize`;
6. updates the global best only if `candidate.cutsize < best_cutsize`;
7. emits checkpoints when `(iteration + 1) % checkpoint_every_iter == 0`;
8. appends a final checkpoint if the last checkpoint does not match final best cut or final NFE.

### Known caveats

Exact perturbation trajectory equivalence is not required unless a later RNG-compatibility contract is introduced. Fidelity is defined by preserving the ILS control logic, feasibility contract, acceptance rule, NFE semantics, and artifact invariants.

## GRASP-Rust fidelity contract

### Python reference

`GRASP-Rust` mirrors `run_grasp_partition`, `construct_greedy_randomized_state`, and `GRASPConfig` from `src/heuristics/grasp.py`. Its local search phase mirrors `first_improvement_descent` from `src/heuristics/ils.py`.

### Frozen profile

Evidence-bearing `GRASP-Rust` runs use profile `grasp_b`:

- `alpha=0.30`;
- `max_iters=100`;
- `checkpoint_every_iter=1`.

### Greedy-randomized construction

The constructor:

1. validates `k > 0`;
2. validates `k <= |V|`;
3. validates `alpha in [0,1]`;
4. shuffles vertices;
5. computes the feasibility cap `ceil((1 + epsilon) * |V| / k)`;
6. computes target quotas using `base_quota = |V| // k` and remainder allocation to lower-indexed blocks;
7. seeds one vertex per block from the first `k` shuffled vertices;
8. for each remaining vertex, builds candidate blocks that satisfy both feasibility cap and target quota;
9. scores candidates by the number of already-assigned incident edges that would become cut edges;
10. builds the RCL using `threshold = s_min + alpha * (s_max - s_min)`;
11. selects uniformly from the RCL;
12. if no candidate satisfies the quota path, selects among blocks with remaining quota and minimum current size, or among globally minimum-size blocks if quotas are exhausted;
13. computes cut and boundary from the completed partition.

### Iterative GRASP semantics

`run_grasp_partition`:

1. builds one greedy-randomized initial solution;
2. applies first-improvement descent;
3. initializes the global best from that descended solution;
4. emits an initial checkpoint at `time_ms=0`;
5. for iterations `1` through `max_iters - 1`, checks wall-clock budget at the top of the loop;
6. constructs a new greedy-randomized solution;
7. applies first-improvement descent;
8. updates the best only on strict improvement;
9. emits checkpoints when `iteration % checkpoint_every_iter == 0`;
10. appends a final checkpoint if the last checkpoint does not match final best cut or final NFE.

### Known caveats

Exact RCL tie-breaking and RNG stream equivalence are not required by this contract. Fidelity is defined by preserving construction rules, alpha semantics, descent semantics, feasibility, NFE accounting, and artifact invariants.

## Claim boundary

These contracts support only the following claim:

> The project preregistered explicit fidelity contracts for `SA-Rust`, `ILS-Rust`, and `GRASP-Rust` before implementation.

They do not support claims that:

- Rust implementations are faster;
- Rust implementations produce better cuts;
- the full Rust portfolio is complete;
- metaheuristics are competitive with METIS or KaHIP;
- CART is empirically justified;
- Python benchmark results are invalid;
- Rust makes the benchmark fair for the first time.
