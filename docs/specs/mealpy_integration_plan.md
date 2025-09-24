# MEALPY Integration Plan (design-only, no code)

> Goal: add MEALPY-based metaheuristics to FORJA **without** breaking fairness or reproducibility. This is an adapter-level design — implementation comes later.

## 1) Problem ↔ MEALPY mapping
- **Representation:** solution is a vector of part labels in `{0, …, k-1}` of length `|V|` (k-balanced).
- **Feasibility:** enforce balance with **repair** after variation, or penalize infeasible solutions:
  - *Repair preferred:* move surplus nodes from oversized parts to undersized parts using a cost-aware heuristic.
  - *Penalty (fallback):* `fitness = cut(P) + λ · max(0, δ(P) - β)` with λ set large enough to enforce feasibility.
- **Objective:** minimize **edge-cut** (`cut(P)`); report `δ(P)` and time as secondary.

## 2) Adapter responsibilities
- Initialize a k-balanced random partition (cold start).
- Expose `fitness(x)` to MEALPY (returns scalar cut; optionally add penalty).
- Count **NFE** consistently (every fitness evaluation).
- Enforce `t_max` and **emit checkpoints** (NFE, cut, time_ms).
- Normalize labels to `0..k-1` on output; store remap.
- Log provenance (algo name, params, random_state, versions).

## 3) YAML contract (forja-exp-v1 snippet)
```yaml
schema: "forja-exp-v1"
solvers:
  mealpy:
    enabled: true
    algorithm: "PSO"          # e.g., PSO, DE, GA, GWO, WOA, MFO, ABC, BA
    params:
      population_size: 60
      inertia: 0.7            # algorithm-specific; fields vary per method
      cognitive: 1.5
      social: 1.5
      random_state: 42
    budget:
      nfe: "50*|E|"           # primary effort budget
      time: "0.5*|E| ms"      # secondary wall-time cap
    checkpoints:
      nfe: [1e2, 3e2, 1e3, 3e3, 1e4, 3e4]   # log-spaced
```

> **Note:** field names under `params` must mirror the MEALPY API actually used. Validate against the pinned version before release.

## 4) Priority algorithms (first wave)
- PSO (Particle Swarm Optimization)
- DE (Differential Evolution)
- GA (Genetic Algorithm)
- GWO (Grey Wolf Optimizer)
- WOA (Whale Optimization Algorithm)
- MFO (Moth-Flame Optimizer)
- ABC (Artificial Bee Colony)
- BA (Bat Algorithm)

(*Confirm availability and names in the pinned MEALPY version; adapt as needed.*)

## 5) Determinism & versions
- Set `random_state` for all MEALPY runs.
- Fix threads (`OMP/BLAS/MKL=1`).
- Log MEALPY package version + dependencies.

## 6) Testing plan (smoke-level)
1. **Budget compliance:** stop by `nfe` or `time` (whichever comes first).
2. **Determinism:** repeated runs with the same seed/plan produce identical cut and checkpoints.
3. **Contract:** outputs pass `solver_run.v1` validation and labels are contiguous `0..k-1`.

## 7) Risks & mitigations
- **API drift:** pin MEALPY version; keep a compatibility shim.
- **Balance handling:** prefer repair to avoid bias from penalties.
- **Cost of fitness:** cache cut contributions to keep fitness evaluation O(|∂P|) where possible.
- **Large graphs:** ensure memory-safe representation and streaming checkpoints.

**Status:** design ready • **Next step:** implement adapter behind a feature flag, add smoke tests, and document usage.
