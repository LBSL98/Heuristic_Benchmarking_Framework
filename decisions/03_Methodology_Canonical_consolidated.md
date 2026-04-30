# 03_Methodology_Canonical_consolidated.md

## Purpose

This file stores the frozen methodological definitions, operational meanings, and protocol decisions used in the monograph, the execution runner, and the experiment analysis.

## Rule of use

If a methodological term appears in the monograph, code documentation, figure explanation, artifact schema description, or reviewer response, its meaning must be compatible with this file. When there is conflict between prose convenience and methodological precision, this file prevails.

## Current freeze status

This version freezes the core meanings of wall-clock time, fair(time), NFE, viability/feasibility, checkpoint policy, the benchmark-synthesis meanings of TTT, ECDF, and performance profiles, the frozen stochastic benchmark profiles, the WSL2 external-validity boundary, the selector outer holdout boundary, the fixed CART regime, and the active artifact contract. Selector regret is anchored to the frozen outer protocol, but its final operationalization remains pending until the selector layer is fully instantiated.

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

## Temporal field naming freeze for execution artifacts

The semantic policy of the project remains unchanged: wall-clock time is the universal effort axis for cross-solver comparison, and checkpoint data exist to reconstruct observed progress on that same external temporal axis.

This naming is now frozen at the artifact-contract level as follows:

- the canonical serialized execution-time field is `elapsed_ms`;
- the canonical serialized checkpoint timestamp field is `checkpoints[].time_ms`;
- `elapsed_wall_ms`, when present, is diagnostic wrapper time and must not replace `elapsed_ms` as the official comparison field;
- legacy summary labels such as `time_ms_best` must not be treated as the primary naming of the current contract;
- `time_ns` is not the canonical serialized checkpoint field of the current project contract.

Interpretation rule:

- `elapsed_ms` represents the official runner-measured elapsed solver time under the controlled protocol;
- `checkpoints[].time_ms` represents the temporal coordinate of each observed checkpoint on the same universal wall-clock axis;
- optional NFE in checkpoints remains diagnostic and intra-family, not the universal effort axis.

Editorial consequence:

No chapter, table, schema description, or artifact explanation may casually alternate between `time_ns` and `time_ms` for the same checkpoint role. If internal clock resolution in nanoseconds is mentioned for implementation detail, that mention must be clearly separated from the canonical serialized artifact naming.

## Methodological guardrails derived from the freeze

1. Do not claim cross-family effort equivalence through NFE.
2. Do not call a comparison fair unless the temporal budget, balance semantics, environment controls, and validation contract are all explicit.
3. Do not describe black-box baselines as lacking checkpoints in a pejorative sense; they are point-output methods under this protocol.
4. Do not confuse final-quality comparison at the timeout with anytime trajectory comparison.
5. Do not treat feasibility, target attainment, and execution success as the same event.

## Repetition policy for stochastic benchmarking

The benchmark release distinguishes between stochastic participants and point-output baselines.

- The stochastic participants of the canonical thesis portfolio are `SA`, `TS`, `ILS`, and `GRASP`.
- Their repetition unit is `(instance, algorithm, budget)`.
- Each such slice must be executed with `n_rep = 5` independent repetitions under the fixed seed set `[42, 43, 44, 45, 46]`.
- The multilevel baselines `METIS` and `KaHIP` remain single-run participants under the same wall-clock budget and validation contract, unless a later audit demonstrates material nondeterminism that requires revisiting this rule.

Interpretation rule:

- repetition exists to stabilize benchmark observations for stochastic participants;
- repetition is not defined by morphological regime, nor by portfolio-wide batch, but by the concrete `(instance, algorithm, budget)` slice;
- all repetitions remain subject to the same fair(time) contract, validation contract, and artifact contract.

## Aggregation rule before statistical analysis and ASP labeling

Repeated runs must be collapsed before cross-algorithm comparison and before constructing the ASP supervised target.

The collapse rule is frozen as follows:

1. only independently validated feasible runs may enter the quality aggregation;
2. the primary aggregated quality value is the median final validated edge-cut result for that `(instance, algorithm, budget)` slice;
3. ties in aggregated quality are broken by the median `elapsed_ms`;
4. if a tie still remains, the final fallback is the lexicographic order of the algorithm identifier, and the tied set must be logged explicitly;
5. if a participant has zero feasible runs on a slice, that participant is marked invalid for winner labeling on that slice, while the failure remains part of the benchmark diagnostics.

## ASP target construction from repeated runs

The supervised target `y_i*(T*)` is defined over the collapsed per-instance table, not over raw runs.

Operationally:

- for each instance `i` and benchmark budget `T*`, each candidate algorithm contributes one collapsed observation after the repetition rule above;
- `y_i*(T*)` is the algorithm that wins under the frozen aggregation and tie rule;
- SBS and VBS comparisons must use the same collapsed per-instance representation;
- an instance for which no participant yields a feasible validated observation is excluded from supervised winner labeling and must be reported separately as an unlabeled benchmark failure case.

Methodological guardrail:

No chapter, script, figure, or selector dataset may alternate between raw repeated runs and collapsed per-instance winners without stating that change explicitly. The canonical benchmark comparison layer and the ASP labeling layer must use the same collapsed rule.

## Still pending freeze items

- Exact instantiated CART parameter tuple and the final selector-regret operationalization inside the frozen outer protocol.

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

## Frozen outer validation boundary for selector evaluation

The selector-evaluation layer now freezes its outer validation boundary independently of the later CART-regime choice.

### Outer split unit

The external split unit is the **instance**, using the collapsed per-instance benchmark table as the selector dataset surface.

Operational consequence:

- raw repeated runs, seeds, checkpoints, and per-run observations must not be split independently across train and test;
- selector evaluation is defined only after the repeated-run collapse and benchmark-label construction stages are complete.

### Untouched external holdout

The canonical selector protocol uses a single deterministic preregistered external holdout manifest.

Operational consequence:

- the outer test partition must remain untouched until the final selector evaluation;
- no preprocessing, feature decision, hyperparameter choice, model choice, threshold choice, or class-handling adjustment may use outer-test information;
- final selector claims are reported on the outer test split only.

### Relation to D-015

The outer boundary is frozen now; the internal CART regime is not.

Operational consequence:

- if D-015 later adopts a searched CART regime, the search must occur only inside the training partition;
- if D-015 later adopts a fixed CART regime, that fixed model is trained on the training side and evaluated once on the untouched outer test side;
- selector regret is canonically interpretable only inside this outer holdout protocol.

## Frozen CART regime for selector evaluation

The canonical selector track adopts a fixed CART regime rather than a searched regime.

Operational rule:

- no grid search, random search, Bayesian optimization, nested model selection, or cross-family model search is allowed in the canonical selector track;
- one explicit deterministic CART configuration must be declared when the selector implementation is instantiated;
- this fixed CART operates strictly inside the outer holdout protocol already frozen by D-011.

Interpretive consequence:

Selector results, when eventually produced, must be interpreted as evidence for a controlled interpretable baseline selector under a fixed CART regime, not as evidence that the selector family was exhaustively optimized.

## Active artifact contract confirmation

The benchmark-release artifact contract is now treated as confirmed against the current runner, JSON schema, and manifest chain.

Confirmed contract points:

- `elapsed_ms` is the official serialized elapsed-time field;
- `checkpoints[].time_ms` is the official serialized checkpoint time field;
- optional NFE remains diagnostic and restricted to instrumented participants;
- point-output baselines remain valid single-point final observations under the same wall-clock contract;
- run status, feasibility, and validation semantics follow the already frozen methodological definitions.

Operational consequence:

No active release-candidate document should continue to describe runner/schema/manifest alignment as a pending methodological blocker.

## Instance-panel coverage gate for the main benchmark

The main benchmark has an instance-panel coverage gate. Executable plans must materialize `R1`, `R2`, and `R3` before benchmark results can support the monograph's three-regime or topology-conditioned selector claims.

Operational rule:

- the official main plans must include explicitly labeled instances from `R1`, `R2`, and `R3`;
- a synthetic-only plan may remain valid as a pilot, smoke test, calibration slice, or controlled sub-study, but it is not sufficient for the main three-regime benchmark;
- the baseline plan and the metaheuristic plan must share the same instance universe;
- the instance identifiers, `k`, balance tolerance, budget protocol, and validation contract must match across the baseline and metaheuristic plans;
- the main campaign remains blocked until a plan-level gate verifies instance existence, regime labels, plan parity, shared problem parameters, budget consistency, and compatibility with the active artifact contract.

Interpretation boundary:

- non-empty coverage of `R1`, `R2`, and `R3` is necessary for three-regime claims, but it is not automatically sufficient for strong per-regime statistical inference;
- if a regime has a small sample, regime-level conclusions must be described as descriptive or exploratory;
- synthetic-only results may support calibration, smoke testing, controlled validation, or exploratory analysis, but they must not be used as evidence for three-regime claims unless `R2` and `R3` are also present in the validated benchmark evidence.
