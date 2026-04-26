# 03_Methodology_Canonical.md

## Purpose

This file stores the frozen methodological definitions, operational meanings, and protocol decisions used in the monograph, the execution runner, and the experiment analysis.

## Rule of use

If a methodological term appears in the monograph, code documentation, figure explanation, artifact schema description, or reviewer response, its meaning must be compatible with this file. When there is conflict between prose convenience and methodological precision, this file prevails.

## Current freeze status

This version freezes the core meanings of wall-clock time, fair(time), NFE, viability/feasibility, checkpoint policy, the benchmark-synthesis meanings of TTT, ECDF, and performance profiles, the frozen stochastic benchmark profiles, and the WSL2 external-validity boundary. Selector regret remains unfrozen until the selector-evaluation layer is canonically closed.

## Frozen methodological definitions

### 1. Wall-clock time

Wall-clock time is the official universal effort metric of the project for cross-solver comparison. It is the externally visible elapsed execution time measured by the runner with a monotonic clock under the controlled execution environment defined by the project. Its methodological role is to equalize effort across heterogeneous solver families when no common internal counter can be imposed on black-box baselines.

Operational consequences:

- Cross-solver comparisons must be stated in terms of equal wall-clock budgets, not in terms of equal internal work.
- The official solver time is the runner-measured elapsed time associated with solver execution under the protocol.
- Post-run activities such as validation, repair bookkeeping, export handling, and auxiliary I/O must not be silently mixed into the official effort budget when the text is claiming fair(time) comparison.
- Any statement that uses the word "fair", "equalized", or "comparable" must make clear that the equality is temporal and external, not internal and algorithmic.

Canonical short wording for prose:

> The project uses controlled wall-clock time, measured by the runner with a monotonic clock, as the universal effort budget for comparing heterogeneous solvers.

### 2. fair(time)

The project-specific meaning of fair(time) is narrow and operational. A comparison is fair(time) only when all compared methods satisfy the following conditions simultaneously:

1. the same problem definition and objective are used;
2. the same balance tolerance semantic is enforced, with equivalent parameter mapping when tool interfaces differ;
3. the same per-instance wall-clock budget is applied;
4. executions occur under the same controlled mono-thread environment and audit policy;
5. hyperparameters are frozen according to the pilot policy rather than re-tuned per instance in the main campaign; and
6. outputs are subjected to the same independent validation contract.

fair(time) does **not** mean:

- identical internal operations;
- identical neighborhood structure across black-box baselines and instrumented metaheuristics;
- identical NFE counts across families; or
- identical anytime observability.

Therefore, fair(time) is a claim about equalized external temporal opportunity under matched constraints, not a claim that solver internals are commensurate.

Canonical short wording for prose:

> In this work, fair(time) means equal wall-clock budget per instance under the same balance semantics, execution controls, and validation protocol.

### 3. NFE

NFE is a diagnostic internal effort metric, not the universal cross-solver metric of the project. It is recorded only when the participant exposes compatible instrumentation, which in the current design means the instrumented Python metaheuristics. NFE may be used to analyze intra-family search behavior, efficiency, and improvement trajectories, but it must not be used to claim globally fair effort equivalence between metaheuristics and black-box multilevel baselines.

Operational consequences:

- NFE may appear in checkpoints and best-known records only when instrumentation exists.
- Absence of NFE for METIS/KaHIP is methodological, not a missing-data defect.
- NFE-based plots or conclusions must be labeled as diagnostic or intra-family unless every compared method exposes a compatible counter.
- The main cross-family ranking basis remains wall-clock time.

Canonical short wording for prose:

> NFE is used only as an internal diagnostic counter for instrumented metaheuristics; the universal comparison budget across solver families is wall-clock time.

### 4. Viability, feasibility, and failure status

The project must not use "viable", "feasible", "valid", and "successful" as if they were interchangeable. Their meanings are frozen separately.

#### 4.1 Move viability

Within the common Python anytime core, a candidate 1-move is viable if and only if applying the move keeps the partition within the allowed balance tolerance. Move viability is therefore a local operator property.

#### 4.2 Solution feasibility

A produced partition is feasible if it satisfies the project constraint contract after independent verification, especially the agreed balance condition and any associated integrity checks on the reported partition/cut information. Feasibility is therefore a property of a candidate solution, not of the run narrative.

#### 4.3 Run status

Run status is an execution-outcome label assigned by the runner. Status distinguishes at least the following classes described in the current monograph draft: success, budget exhausted / target not reached in budget, input error, internal error, and contract- or cache-related failure conditions.

#### 4.4 Orthogonality rule

Feasibility and status are not synonyms. A run may end without hitting an external target and still yield a feasible final solution. Conversely, a run may terminate with an execution problem or contract violation and should not be treated as a valid benchmark observation merely because some partial output exists. Any analysis or prose that mixes these notions must be corrected.

Canonical short wording for prose:

> Feasibility refers to whether the reported partition satisfies the solution contract after validation; status refers to how the execution ended.

### 5. Checkpoint policy

The checkpoint policy is frozen at the semantic level as follows:

- The universal budget is wall-clock time.
- Instrumented anytime solvers may emit up to 50 log-spaced checkpoints across the allocated timeout.
- Each checkpoint stores the minimal information required to reconstruct progress under the universal effort axis: time stamp plus current quality, with optional NFE when instrumentation exists.
- Checkpoint collection must not alter the algorithmic flow in a way that creates hidden extra work for one family but not another.
- Black-box multilevel baselines that do not expose anytime trajectories are represented as single-point final observations under the same reference clock.
- Checkpoint data and single-point baseline outputs must enter the same artifact chain so that later curves and analyses are reconstructed from the recorded execution trace rather than from informal summaries.
- The canonical serialized total-time field is `elapsed_ms`.
- The canonical serialized checkpoint timestamp field is `checkpoints[].time_ms`.
- `time_ns` may exist only as an internal clock-resolution detail and must not be described as the benchmark artifact field.
- Legacy names such as `runtime_ms` and `elapsed_wall_ms` are not the active `solver_run.v1` time contract.

## Traceability note for repository documentation

Repository documentation should now use the runner-aligned field names above. Historical prose that still alternates between `time_ns`, `runtime_ms`, `elapsed_wall_ms`, and `time_ms` must be treated as legacy wording and corrected before being reused in active documents.

## Methodological guardrails derived from the freeze

1. Do not claim cross-family effort equivalence through NFE.
2. Do not call a comparison fair unless the temporal budget, balance semantics, environment controls, and validation contract are all explicit.
3. Do not describe black-box baselines as lacking checkpoints in a pejorative sense; they are point-output methods under this protocol.
4. Do not confuse final-quality comparison at the timeout with anytime trajectory comparison.
5. Do not treat feasibility, target attainment, and execution success as the same event.

## Still pending freeze items

- Exact operational definition of selector regret after the outer ASP validation protocol and the CART regime are frozen.

### 6. Portfolio scope boundary

The current canonical thesis portfolio is limited to the four anytime metaheuristics SA, TS, ILS, and GRASP, plus the multilevel baselines METIS and KaHIP.

Operational consequences:

- Any `greedy` baseline present in the repository is exploratory and must not be treated as a canonical benchmark participant.
- Official phase plans, official manifests, and the selector label space must not include `greedy` unless this file is explicitly updated first.
- Engineering validation of `greedy` may remain in the repository, but its outputs cannot support central benchmark claims in the monograph.

Canonical short wording for prose:

> The canonical thesis portfolio comprises SA, TS, ILS, GRASP, METIS, and KaHIP; any greedy baseline retained in the repository is exploratory and outside the official benchmark flow.


## Frozen stochastic hyperparameter profiles for the benchmark release

The bounded pre-benchmark calibration stage `EXP-CALIB-001` is now complete, and the current benchmark release freezes one global profile per stochastic participant.

The frozen profiles are:

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

Methodological rule:

- these are global release-level profiles, not instance-specific profiles;
- they were selected through the bounded calibration protocol rather than through retuning inside the main campaign;
- no post hoc profile switching is allowed after the benchmark release starts unless the canon is explicitly reopened.

Operational consequence:

The official metaheuristic benchmark plans and their pilot counterparts must use these same profiles.


## External-validity boundary of the audited WSL2 environment

The benchmark release uses a controlled WSL2 execution environment that was explicitly revalidated during release preparation.

Methodological interpretation:

- comparative benchmark claims remain admissible inside this audited environment because all compared solvers are exposed to the same execution surface, wall-clock budget semantics, validation contract, and mono-thread controls;
- the project therefore treats the environment as a valid controlled benchmark surface for internal comparison;
- however, absolute timing results must not be overgeneralized as if they were automatically identical to native bare-metal Linux or to arbitrary external machines.

Operational wording rule:

- the text may say that the benchmark was executed in an audited controlled WSL2 environment;
- the text may say that cross-solver comparisons are valid under this shared environment;
- the text must not claim hardware-independent absolute timing equivalence beyond the audited environment unless a separate confirmation is produced.

Threat-to-validity consequence:

Any monograph section discussing validity should separate:
1. internal fairness under the controlled environment; and
2. external generalization of absolute runtime magnitudes beyond that environment.


## Frozen benchmark-synthesis metrics

The benchmark-synthesis layer of the project is now frozen for `TTT`, `ECDF`, and `performance profiles`.

### TTT

The project-specific meaning of `TTT` is a wall-clock target-attainment quantity.

Operational rule:

- a target rule must be declared explicitly in the corresponding benchmark analysis batch or preregistration;
- for instrumented anytime solvers, attainment time is the first checkpoint time at which the validated quality satisfies the target;
- for point-output baselines, attainment is only observed at the final `elapsed_ms`; if the final validated output satisfies the target, attainment time equals that final time, otherwise the observation is right-censored at the budget boundary;
- for stochastic participants, run-level attainment observations are first expressed on the same wall-clock axis with right-censoring at the budget, then collapsed to a single per-instance representative time by the median rule; if the collapsed value lands at the budget boundary because attainment was not achieved early enough across repetitions, the slice is treated as right-censored.

Interpretive consequence:

`TTT` is admissible in this project even with point-output baselines, but their contribution is degenerate at the final observation time rather than a full anytime trajectory.

### ECDF

The project-specific meaning of `ECDF` is an attainment-over-time summary on the wall-clock axis.

Operational rule:

- for a declared target rule and a wall-clock budget `t`, `ECDF_a(t)` is the fraction of instances whose collapsed attainment time for algorithm `a` is less than or equal to `t`;
- right-censored slices count as non-attained up to their censoring point;
- the ECDF therefore summarizes the same collapsed target-attainment surface used by TTT rather than a separate ad hoc construction.

Interpretive consequence:

ECDF is an admissible cross-family summary because the effort axis remains wall-clock time, but its meaning must remain target-attainment over time, not final-quality-at-timeout.

### Performance profiles

The project-specific meaning of `performance profiles` is restricted to collapsed final-quality comparison at a fixed budget.

Operational rule:

- let `q_{a,i}` denote the collapsed final validated cutsize of algorithm `a` on instance `i` at the fixed budget;
- since the project minimizes edge cut, the profile ratio is `r_{a,i} = q_{a,i} / min_b q_{b,i}`;
- performance profiles are admissible only on the common-feasible set where every compared algorithm has a feasible collapsed final observation on the instance;
- excluded instances caused by infeasibility or missing valid collapsed outputs must be reported separately and must not be silently hidden.

Interpretive consequence:

In this project, performance profiles summarize endpoint relative quality, not anytime attainment behavior.

### Scope boundary

Selector regret is not part of the present benchmark-synthesis freeze.

Its canonical definition is deferred to the selector-evaluation layer and must be frozen only after the outer ASP validation protocol and the CART model-selection regime are frozen.
