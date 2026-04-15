# MEALPY Integration Plan (design-only, no code)

> Goal: add MEALPY-based metaheuristics to FORJA without breaking the active wall-clock protocol or the repository artifact contract.

## 1. Problem ↔ MEALPY mapping

- **Representation:** solution is a vector of part labels in `{0, ..., k-1}` of length `|V|`.
- **Feasibility:** enforce balance via repair after variation, or apply a penalty only as a fallback.
- **Objective:** minimize edge-cut; report balance diagnostics and wall-clock progress under the same contract used by the existing solvers.

## 2. Adapter responsibilities

- Initialize a balanced random partition (cold start).
- Expose `fitness(x)` to MEALPY.
- Track **NFE** consistently when instrumentation is available.
- Enforce the same wall-clock budget contract used by the rest of the benchmark.
- Emit checkpoints using the active artifact names: `checkpoints[].time_ms` plus optional `nfe`.
- Normalize labels to `0..k-1` on output.
- Log provenance (algorithm, params, random state, package versions).

## 3. YAML contract sketch

```yaml
schema: "forja-exp-v1"
solvers:
  mealpy:
    enabled: true
    algorithm: "PSO"
    params:
      population_size: 60
      inertia: 0.7
      cognitive: 1.5
      social: 1.5
      random_state: 42
    budget:
      type: "time"
      seconds: 5
    checkpoints:
      include_nfe: true   # diagnostic only
```

Notes:

- the universal comparison budget remains wall-clock time
- any emitted NFE field is diagnostic and must not be used to claim cross-family fairness
- field names under `params` must mirror the pinned MEALPY API actually adopted

## 4. Priority algorithms (first wave)

- PSO
- DE
- GA
- GWO
- WOA
- MFO
- ABC
- BA

## 5. Determinism and versions

- Set `random_state` for all MEALPY runs.
- Fix `OMP`, `OPENBLAS`, and `MKL` threads to `1`.
- Record MEALPY version and dependency set.

## 6. Testing plan

1. Budget compliance under the wall-clock contract.
2. Determinism for repeated runs with the same seed and plan.
3. Output compatibility with `solver_run.v1`.
4. Correct checkpoint serialization using `elapsed_ms` and `checkpoints[].time_ms`.

## 7. Risks and mitigations

- **API drift:** pin the MEALPY version and keep a compatibility shim if needed.
- **Balance handling:** prefer repair to avoid bias from penalties.
- **Fitness cost:** cache contributions where possible.
- **Large graphs:** keep checkpointing lightweight and memory-safe.

**Status:** design-only. Any implementation must remain compatible with the current benchmark
contract before it can participate in official claims.
