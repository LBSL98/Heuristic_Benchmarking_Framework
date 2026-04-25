# Current Benchmark Contract

This page summarises the active benchmark contract of the FORJA / MPP repository. It is the
operational documentation layer for contributors who need the current repository truth without
trawling through historical material.

## Canonical portfolio

The official thesis portfolio is:

- `SA`
- `TS`
- `ILS`
- `GRASP`
- `METIS`
- `KaHIP`

`greedy` may remain in the repository only as an exploratory / engineering track. It is not part
of:

- the official thesis benchmark
- the official campaign flow
- the canonical selector label space

## Official effort metric

Cross-family comparison is governed by wall-clock time.

`fair(time)` in this repository means:

1. the same per-instance wall-clock budget
2. the same balance semantics
3. the same controlled execution environment
4. hyperparameters frozen from the pilot before the main campaign
5. the same independent validation contract

NFE may still be recorded for instrumented metaheuristics, but only as a diagnostic internal
counter. It is not the universal comparison axis across solver families.

## Artifact time fields

The active serialized names are:

- total runtime: `elapsed_ms`
- checkpoint timestamp: `checkpoints[].time_ms`

Repository documentation must not describe `time_ns` as the official serialized checkpoint field.
If nanoseconds are mentioned at all, the text must make clear that they refer only to an internal
clock-resolution detail rather than to the result-artifact contract.

Legacy names such as `runtime_ms` and `elapsed_wall_ms` are not the active `solver_run.v1`
contract for benchmark artifacts.

## KaHIP status

For active documentation and experimental narrative, the official KaHIP reference is **KaHIP 3.17**.

Operationally:

- record the version reported by the runtime `kaffpa` binary used in the experiment
- do not infer the experimental version from the vendored `./KaHIP` tree alone
- keep the vendored tree for traceability unless a separate review concludes it is safe to move
  or archive it

This caution is important because the repository already contains mixed version markers inside
`./KaHIP`, so the tree is not a reliable standalone witness of the executable used in a run.

## Active plan scope in the repository

The tracked `configs/plan_phase_1.yaml` and `configs/plan_phase_1_pilot.yaml` are conservative
baseline-only executable slices. They preserve the wall-clock benchmark contract and keep
`greedy` out of official scope, but they should not be read as redefining the full canonical
portfolio.

Exploratory greedy plans remain separated under their own filenames and must stay outside official
benchmark claims.


## Frozen stochastic profiles for the current release candidate

The current release-candidate benchmark profiles are frozen as follows:

- `GRASP` → `grasp_b`
  - `alpha = 0.30`
  - `max_iters = 100`
  - `checkpoint_every_iter = 1`

- `ILS` → `ils_b`
  - `max_iters = 100`
  - `perturb_moves = 4`
  - `checkpoint_every_iter = 1`

- `SA` → `sa_e_maxsteps_100000`
  - `initial_temp = 1.0`
  - `cooling = 0.997`
  - `min_temp = 0.001`
  - `max_steps = 100000`
  - `checkpoint_every_nfe = 100`

- `TS` → `ts_c`
  - `max_steps = 10000`
  - `min_tenure = 7`
  - `tenure_scale = 1.0`
  - `tenure_jitter = 4`
  - `checkpoint_every_nfe = 100`
  - `frequency_penalty = 0.01`

These are global benchmark-release profiles. They must not be retuned per instance inside the main campaign.

## Source-of-truth pointers

When wording must be exact, consult:

- `decisions/03_Methodology_Canonical_consolidated.md`
- `specs/jsonschema/solver_run.schema.v1.json`
- `docs/specs/reproducibility_checklist.md`
