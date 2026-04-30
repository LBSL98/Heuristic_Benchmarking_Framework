# 01_Decision_Log.md

## Purpose

This file records frozen project decisions. A decision only becomes canonical after being written here.

## Status legend

- **Proposed**: discussed, not yet frozen.
- **Frozen**: accepted as current project truth.
- **Superseded**: replaced by a later decision.

## Decision entries

### D-001 — Project governance architecture
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** The project will use a multi-chat structure with role separation: Governance and Integrity, Theory and Evidence Audit, Writing Surgery, Code and Experiments, and Final Release Audit.
- **Rationale:** Prevent role collapse, reduce context drift, and force cross-audit between theory, writing, and code.
- **Impact:** No single chat is treated as authoritative by itself.
### D-002 — Canonical-source policy
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** Project truth will be maintained in canonical markdown files stored as project sources, not only in conversation history.
- **Rationale:** Chat continuity alone is not sufficient for a long and high-stakes academic project.
- **Impact:** All significant revisions must update the corresponding canonical file.
### D-003 — Dual storage policy for guidance documents
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** Normative project files must exist both in Drive and in the project sources whenever possible.
- **Rationale:** Drive works as durable repository; project sources work as active context.
- **Impact:** Editorial and methodological rules should not be kept only in external folders.
### D-004 — Writing feedback is normative
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** Committee and reviewer comments are treated as normative constraints until explicitly resolved.
- **Rationale:** The current stage is revision under committee scrutiny, not greenfield drafting.
- **Impact:** Rewriting must follow `04_Writing_Constraints.md` and `09_Committee_Issues_Log.md`.
### D-005 — Naming convention
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** File and artifact names used in project support files will remain in English.
- **Rationale:** Aligns with the project naming preference already adopted by the user.
- **Impact:** New support files should follow English names consistently.

## Template for new entries

### D-XXX — Title
- **Status:** Proposed | Frozen | Superseded
- **Date:** YYYY-MM-DD
- **Decision:**
- **Rationale:**
- **Impact:**
- **Supersedes / Superseded by:**
### D-006 — Final repository stabilization before monograph freeze
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** The final repository state was stabilized through a controlled integration sequence: code hardening first, minimal defensible documentation second, and final integration into `main` only after branch governance and required checks were aligned.
- **Rationale:** Prevented mixing implementation corrections with over-broad documentation claims and ensured that the final branch state matched the auditable project scope.
- **Impact:** The monograph and defense materials must describe only the repository state and documentation subset that survived this stabilization process.
- **Supersedes / Superseded by:**
### D-007 — Canonical temporal field naming for execution artifacts
- **Status:** Frozen
- **Date:** 2026-04-15
- **Decision:** The canonical serialized execution-time field of the project is `elapsed_ms`, and the canonical serialized checkpoint timestamp field is `checkpoints[].time_ms`. The label `time_ns` is not the canonical artifact field for checkpoint serialization in the current project contract.
- **Rationale:** The methodological semantics were already frozen around runner-measured wall-clock time as the universal effort budget, but the monograph draft still contained unresolved wording conflict between `time_ns` and `time_ms` for checkpoint representation. Cross-audit of the project documentation, current implementation, and artifact history indicates that the implemented and auditable contract is millisecond-based in the serialized artifacts. Freezing the canonical field names prevents further drift between methodology, monograph prose, schema language, and artifact interpretation.
- **Impact:** All monograph passages, schema descriptions, artifact tables, and reproducibility-oriented prose must align to `elapsed_ms` and `checkpoints[].time_ms`. Any remaining mention of `time_ns` must be restricted to internal clock-resolution discussion when strictly necessary, not to the canonical serialized checkpoint field.
- **Supersedes / Superseded by:** Clarifies the open schema wording caveat previously noted in `03_Methodology_Canonical.md`.
### D-008 — Benchmark repetition policy for stochastic participants
- **Status:** Frozen
- **Date:** 2026-04-15
- **Decision:** In the main benchmark campaign, the repetition unit for stochastic benchmarking is `(instance, algorithm, budget)`. The stochastic participants `SA`, `TS`, `ILS`, and `GRASP` must be executed with `n_rep = 5` independent repetitions under the fixed seed set `[42, 43, 44, 45, 46]`. The multilevel baselines `METIS` and `KaHIP` remain single-run participants under the same per-instance wall-clock budget and validation contract, unless a later audit demonstrates material nondeterminism that justifies extending the repetition policy to them.
- **Rationale:** The project already recognizes that non-fully-deterministic participants require repetition, but leaving the repetition unit, repetition count, and seed policy undefined would make the benchmark release non-auditable and would propagate ambiguity into both statistical analysis and ASP supervision targets.
- **Impact:** No main benchmark campaign may start without using this repetition unit, repetition count, and seed policy. Plan files, execution scripts, benchmark tables, and methodological prose must use the same rule.
- **Supersedes / Superseded by:** Freezes the policy previously left open in OI-007.
### D-009 — WSL2 external-validity boundary for the benchmark release
- **Status:** Frozen
- **Date:** 2026-04-25
- **Decision:** The benchmark release is allowed to run in the audited WSL2 release-candidate environment, provided that all compared solvers execute under the same controlled mono-thread conditions, the same validation contract, and the same runtime-governance surface. Comparative claims inside the project are therefore valid as controlled within-environment claims, not as hardware-agnostic absolute performance claims.
- **Rationale:** The repository execution surface, Docker/compose path, and benchmark tooling were revalidated in the actual WSL2 environment used by the project. The remaining methodological risk is not internal unfairness between participants, but overclaiming external generality from a virtualized host-dependent environment.
- **Impact:** The monograph, defense, and repository documentation must state that the benchmark results are valid for the audited controlled environment used in the campaign. They must not claim that absolute timings automatically generalize to native bare-metal Linux or to arbitrary external hardware/software stacks without additional confirmation.
- **Supersedes / Superseded by:** Freezes the policy previously left open in OI-007.
### D-010 — Benchmark synthesis metrics freeze (TTT / ECDF / performance profiles)
- **Status:** Frozen
- **Date:** 2026-04-25
- **Decision:** The benchmark-synthesis layer of the project is frozen as follows:

  1. `TTT` belongs to the benchmark layer and is defined on the universal wall-clock axis.
     - For instrumented anytime solvers, per-run attainment time is the first recorded checkpoint time at which the validated quality satisfies the declared target rule.
     - For point-output baselines, attainment is only observable at the final recorded `elapsed_ms`; if the final validated output satisfies the target, the attainment time is that final time, otherwise the observation is right-censored at the budget boundary.
     - For stochastic participants, run-level attainment observations are first converted to wall-clock times with right-censoring at the budget. The project-level per-instance slice is then collapsed to a single representative time by the median rule; if the collapsed value sits at the budget boundary because attainment was not achieved early enough across repetitions, the slice is treated as right-censored at the budget.

  2. `ECDF` belongs to the benchmark layer and is reported over wall-clock budgets for a declared target rule.
     - For each algorithm and budget value `t`, the ECDF value is the fraction of instances whose collapsed attainment time is less than or equal to `t`.
     - Right-censored slices count as non-attained up to the censoring point.
     - ECDF is therefore an attainment-over-time summary built from the same collapsed per-instance target-attainment surface used by TTT.

  3. `Performance profiles` are admissible in the project only on the collapsed final-quality table at a fixed budget.
     - For each instance `i` and algorithm `a`, let `q_{a,i}` be the collapsed final validated cutsize at the fixed budget.
     - The profile ratio is `r_{a,i} = q_{a,i} / min_b q_{b,i}` because the project minimizes edge cut.
     - Performance profiles are computed only on the common-feasible set of instances for which every compared algorithm has a feasible collapsed final observation.
     - Any excluded instances due to infeasibility or missing valid collapsed output must be reported separately and must not be silently absorbed into the profile.

  4. `Selector regret` is **not** frozen by `D-010`.
     - Regret is removed from the benchmark-synthesis freeze and is deferred to the selector-evaluation layer.
     - Its canonical definition must be frozen later together with the outer ASP validation protocol and the CART model-selection regime under `D-011` / `D-015`.

- **Rationale:** The audit showed that the benchmark-synthesis layer and the selector-evaluation layer were being mixed in the same open item. Freezing `TTT`, `ECDF`, and `performance profiles` now closes the comparative benchmark semantics without prematurely freezing selector regret before the outer-validation and CART-regime decisions exist.
- **Impact:** Benchmark figures, tables, scripts, and prose that claim comparative synthesis must use only these definitions. Any use of regret remains non-canonical until the selector track is frozen separately.
- **Supersedes / Superseded by:** Narrows and freezes the part of the earlier open analytical block that belongs strictly to comparative benchmark synthesis; selector regret is explicitly deferred to `D-011` / `D-015`.
### D-011 — Outer validation protocol for selector evaluation
- **Status:** Frozen
- **Date:** 2026-04-25
- **Decision:** The canonical selector-evaluation protocol uses a single external holdout split defined over the collapsed per-instance table.

  1. **Unit of separation**
     - The outer split unit is the **instance**.
     - Raw runs, seeds, checkpoints, and per-run rows must never be split independently across train and test.
     - Selector training and evaluation must use one collapsed row per instance, derived from the canonical repeated-run collapse rules already frozen by the benchmark contract.

  2. **Outer evaluation boundary**
     - A deterministic, preregistered outer holdout manifest must be created before selector training begins.
     - The outer test partition remains untouched until the final selector evaluation.
     - No model choice, threshold choice, feature filtering, missing-data handling decision, or post hoc heuristic adjustment may use outer-test information.

  3. **Training-side freedom**
     - All preprocessing, feature engineering, class handling, and any later CART model-selection procedure must operate strictly inside the training partition.
     - If `D-015` later chooses a searched CART regime, that search is restricted to the training side only.
     - If `D-015` later chooses a fixed CART regime, the fixed model is trained once on the training partition and then evaluated once on the untouched outer test partition.

  4. **Selector target and reporting consequence**
     - The selector target remains defined on the collapsed benchmark table, not on raw repeated runs.
     - Final selector claims must be reported on the outer test split only.
     - Selector regret is anchored to this outer protocol and remains canonically meaningful only under this external holdout boundary.

- **Rationale:** The repository currently has governance text for selector evaluation but no live implementation surface that would justify inferring a split protocol from code. Freezing the outer protocol now prevents leakage and multiple admissible interpretations while keeping the internal CART regime open for `D-015`.
- **Impact:** Any future selector pipeline, dataset builder, training script, regret computation, or monograph prose must respect instance-level external separation and the untouched-test rule. No selector claim is canonical if it violates this split boundary.
- **Supersedes / Superseded by:** Freezes the policy previously left open in OI-009. Constrains the meaning of selector regret and sets the external boundary within which D-015 may later choose a fixed or searched CART regime.
### D-012 — Final stochastic hyperparameter freeze for the benchmark release
- **Status:** Frozen
- **Date:** 2026-04-25
- **Decision:** The canonical benchmark release freezes one global hyperparameter profile per stochastic participant as follows:

  - `GRASP`: `grasp_b`
    - `alpha = 0.30`
    - `max_iters = 100`
    - `checkpoint_every_iter = 1`

  - `ILS`: `ils_b`
    - `max_iters = 100`
    - `perturb_moves = 4`
    - `checkpoint_every_iter = 1`

  - `SA`: `sa_e_maxsteps_100000`
    - `initial_temp = 1.0`
    - `cooling = 0.997`
    - `min_temp = 0.001`
    - `max_steps = 100000`
    - `checkpoint_every_nfe = 100`

  - `TS`: `ts_c`
    - `max_steps = 10000`
    - `min_tenure = 7`
    - `tenure_scale = 1.0`
    - `tenure_jitter = 4`
    - `checkpoint_every_nfe = 100`
    - `frequency_penalty = 0.01`

- **Rationale:** The bounded pre-benchmark calibration stage `EXP-CALIB-001` was completed with a two-stage protocol: coarse screening, an SA-only saturation micro-round to ensure budget-compatible SA behavior, and short confirmation with the full seed policy. The selected profiles are the winners of the confirmation stage under the project collapse and tie rules. No per-instance retuning is allowed in the main benchmark campaign.
- **Impact:** The benchmark pilot, the main campaign, the selector layer, and all benchmark-release claims must use exactly these frozen profiles unless a later canonical decision explicitly supersedes them.
- **Supersedes / Superseded by:** Freezes the policy previously left open in OI-010.
### D-013 — Repeated-run aggregation and ASP label construction
- **Status:** Frozen
- **Date:** 2026-04-15
- **Decision:** Repeated runs must be collapsed at the `(instance, algorithm, budget)` level before statistical comparison and before ASP target construction. Only independently validated feasible runs may enter the aggregation of quality. For the current benchmark contract, the primary aggregated quality value is the median final validated edge-cut result of the participant on that instance-budget slice. Ties in aggregated quality must be broken by the median `elapsed_ms`; if a tie still remains, the final fallback is the lexicographic order of the algorithm identifier, and the tied set must be logged explicitly. If a participant produces zero feasible runs for a given `(instance, algorithm, budget)` slice, that participant is marked invalid for winner labeling on that slice, while the failure itself remains part of the benchmark diagnostics. The ASP target label `y_i*(T*)`, as well as SBS/VBS calculations, must be derived from this same collapsed per-instance table rather than from raw repeated runs.
- **Rationale:** Repetition without a single collapse rule would leave both the statistical benchmark layer and the ASP supervision layer underdefined. Freezing aggregation and winner construction together prevents drift between comparison, labeling, and selector evaluation.
- **Impact:** The benchmark campaign, ASP dataset construction, SBS/VBS baselines, and later selector claims must all use the same collapsed per-instance representation. Instances with no feasible participant after validation must be reported separately and excluded from supervised winner labeling.
- **Supersedes / Superseded by:** Freezes the policy previously left open in OI-012.
### D-014 — Benchmark campaign preregistration policy
- **Status:** Frozen
- **Date:** 2026-04-25
- **Decision:** The benchmark campaign becomes execution-authorizing only through two distinct preregistered ledger entries:

  1. **`EXP-BENCH-PILOT-001`**
     - Role: dry-run / pilot validation under the fully frozen benchmark protocol.
     - Purpose: validate executability, artifact chain integrity, manifest generation, validation surface, and basic analysis readiness under the release-candidate state.
     - It is allowed to run only after its planned ledger entry is complete.

  2. **`EXP-BENCH-MAIN-001`**
     - Role: main comparative benchmark campaign.
     - Purpose: generate the canonical comparative evidence under the already frozen protocol.
     - It must not start until the pilot has been executed and reviewed.

  3. **Mutation rule**
     - If the pilot reveals a protocol-relevant change, the canon must be explicitly reopened before the main campaign.
     - The main campaign must not silently inherit altered assumptions from pilot execution.
     - Any material change after pilot review requires updated preregistration rather than quiet overwrite of the original plan.

- **Rationale:** The benchmark release now has the central methodological freezes in place, so the remaining governance requirement is to ensure that pilot execution and the main campaign are separately registered and that the main campaign cannot begin under an implicitly modified protocol.
- **Impact:** `06_Experiment_Ledger.md` must contain real planned entries for `EXP-BENCH-PILOT-001` and `EXP-BENCH-MAIN-001`. The checklist must treat preregistration as complete only after those entries are populated. The main campaign remains blocked until pilot review is complete.
- **Supersedes / Superseded by:** Freezes the policy previously left open in OI-012.
### D-015 — CART model-selection regime for the canonical selector track
- **Status:** Frozen
- **Date:** 2026-04-25
- **Decision:** The canonical selector track adopts a **fixed CART regime**, not a searched regime.

  1. **No hyperparameter search**
     - The canonical selector evaluation must not use grid search, random search, Bayesian optimization, nested model selection, or post hoc model-family comparison.
     - The selector track uses one explicit deterministic CART configuration when implementation begins.

  2. **Relation to D-011**
     - The fixed CART model operates strictly inside the outer validation boundary frozen by `D-011`.
     - The outer test split remains untouched until final evaluation.
     - No choice of CART configuration may be justified using outer-test performance.

  3. **Operational consequence**
     - When the selector implementation is added, it must instantiate a single declared CART configuration and train it on the training partition only.
     - The exact instantiated parameter tuple must be recorded in the selector preregistration and implementation-facing documentation before any selector result is claimed.
     - The canonical regime choice itself is already frozen now: fixed, not searched.

  4. **Interpretive consequence**
     - Selector claims should be presented as evidence for a controlled interpretable baseline selector under a fixed CART regime, not as evidence of having optimized the selector family exhaustively.

- **Rationale:** The current repository does not yet contain a live selector-evaluation implementation surface that would justify a more ambitious searched regime. Freezing a fixed CART regime now minimizes leakage risk, avoids hidden multiplicity, reduces implementation burden, and remains compatible with the already frozen outer holdout protocol of `D-011`.
- **Impact:** Any later selector script, dataset builder, regret computation, and monograph wording must treat CART as a fixed interpretable selector baseline inside the frozen outer holdout. Searched-regime claims are non-canonical unless the canon is explicitly reopened.
- **Supersedes / Superseded by:** Freezes the choice previously left open in OI-014 and completes the selector-governance pair begun by D-011.
### D-016 — Active artifact contract confirmed against runner, schema, and manifest chain
- **Status:** Frozen
- **Date:** 2026-04-25
- **Decision:** The active benchmark-release artifact contract is canonically confirmed against the current runner behavior, the JSON schema, and the manifest chain.

  1. **Timing fields**
     - The official serialized elapsed-time field is `elapsed_ms`.
     - The official serialized checkpoint timestamp field is `checkpoints[].time_ms`.
     - Optional wall-wrapper diagnostics, when present, do not replace `elapsed_ms` as the official comparison field.

  2. **Checkpoint and instrumentation semantics**
     - Instrumented anytime participants may expose checkpoint progress plus optional NFE diagnostics.
     - Point-output baselines remain single-point final observations under the same wall-clock contract.
     - Missing NFE for black-box baselines is methodological, not a defect.

  3. **Status and validation semantics**
     - Run status, feasibility, and validation outcomes must keep the meanings already frozen in the methodological canon.
     - The schema, runner output, and artifact descriptions must not drift into alternate naming or mixed status semantics.

  4. **Manifest-chain consequence**
     - The manifest and raw-artifact chain currently used by the release candidate is accepted as the active auditable contract for benchmark execution and later analysis reconstruction.

- **Rationale:** Benchmark-release preparation already aligned the active runner, schema, and documentation surface. The remaining problem was canonical housekeeping: the project still carried a stale open issue and residual wording that treated this confirmation as pending. Freezing it now removes avoidable ambiguity before pilot execution.
- **Impact:** Monograph prose, repository documentation, tables of artifact fields, and benchmark-analysis tooling must treat the current runner/schema/manifest surface as the confirmed active contract. No release-candidate text should continue to describe this confirmation as open.
- **Supersedes / Superseded by:** Closes the pending confirmation previously tracked as OI-011.

### D-019 — R1/R2/R3 instance-panel gate for the main benchmark
- **Status:** Frozen
- **Date:** 2026-04-30
- **Decision:** The official main benchmark plans must include explicitly labeled instances from `R1`, `R2`, and `R3`. A synthetic-only plan may remain valid as a pilot, smoke test, calibration slice, or controlled sub-study, but it is not sufficient for the main three-regime benchmark. The baseline and metaheuristic plans must share the same instance universe. The instance identifiers, `k`, balance tolerance, budget protocol, and validation contract must match across the baseline and metaheuristic plans. The main benchmark campaign remains blocked until the R1/R2/R3 panel is declared in the official plans and checked by a plan-level gate that verifies instance existence, regime labels, plan parity, shared problem parameters, budget consistency, and compatibility with the artifact contract.
- **Rationale:** The monograph's research questions, hypotheses, validity argument, and selector motivation depend on morphological diversity. A campaign restricted to synthetic instances supports only a controlled synthetic-slice analysis and does not substantiate claims about R1/R2/R3 behavior, external validity across graph families, or topology-conditioned selection beyond the synthetic regime.
- **Impact:** `03_Methodology_Canonical_consolidated.md` must state the R1/R2/R3 plan gate. `06_Experiment_Ledger.md` must mark the main campaign as blocked until the panel gate is closed and must register the panel-validation gate. `07_Open_Issues.md` must track the concrete instance-list and plan update. `08_Results_to_Text_Map.md` must forbid three-regime or selector-generalization claims from synthetic-only results.
- **Supersedes / Superseded by:** Extends `D-014` by adding an instance-panel execution gate for the main campaign. Does not supersede `D-008`, `D-012`, `D-013`, `D-016`, `D-017`, or `D-018`.

### D-020 — Acceptance of reviewed R1/R2/R3 raw main benchmark evidence
- **Status:** Frozen
- **Date:** 2026-04-30
- **Decision:** The official R1/R2/R3 main benchmark execution at commit `fd3d475824cbb9070310dfda1322f7f0ef988177` is accepted as reviewed raw benchmark evidence after `375e_post_campaign_review_gate_final` and `376_timeout_overshoot_and_tiebreak_audit`. This decision authorizes proceeding to collapsed fixed-budget tables and benchmark analysis, but does not by itself authorize final comparative claims in the monograph.
- **Rationale:** The post-campaign review gate validated 264 expected raw artifacts, with 24 baseline artifacts and 240 metaheuristic artifacts, correct R1/R2/R3 coverage, correct seeds, `k=8`, `beta=0.03`, `budget_time_ms=5000`, parseable JSON artifacts, feasible outputs, `elapsed_ms` present, and checkpoint timestamps using `time_ms`. The timeout/overshoot audit found overshoot in timeout-status metaheuristic runs, but the clipped-time sensitivity check did not change winner identities under the audited tie-break comparison.
- **Impact:** `06_Experiment_Ledger.md`, `07_Open_Issues.md`, and `08_Results_to_Text_Map.md` must be updated to reflect that the panel gate and raw main execution are complete. Any result prose must still report timeout overshoot as a caveat and must not overstate per-regime inference from `R2=2` and `R3=2`.
- **Supersedes / Superseded by:** Completes the execution-governance consequence of `D-019`; does not supersede the fixed-budget aggregation, selector, or claim-mapping rules.

### D-021 — Dominance-conditioned selector framing
- **Status:** Frozen
- **Date:** 2026-04-30
- **Decision:** The selector track is framed as an exception-detection problem relative to a strong multilevel reference baseline. The project will not assume that all paradigms should win with similar frequency, and it will not claim selector usefulness merely because a CART can be trained. Selector usefulness must be supported by mapped evidence of strong exceptions, near ties, competitive gaps, temporal reversals, implementation-maturity shifts, or a meaningful SBS/VBS gap.
- **Rationale:** The validated R1/R2/R3 fixed-budget collapse produced a nearly degenerate winner surface, with `METIS` winning 11 of 12 instances and `KaHIP` winning 1 of 12. Treating this surface as positive evidence for a multiclass selector would overclaim. A dominance-conditioned framing preserves the scientific value of the result by asking whether and where the multilevel default ceases to be dominant or becomes only marginally better.
- **Impact:** Fixed-budget, budget-aware, TS-Rust, expanded-panel, and selector analyses must report whether they identify exceptions to the multilevel reference. If no meaningful exceptions or oracle gap appear, the selector result must be reported as limited, trivial, or negative under the evaluated slice.
- **Supersedes / Superseded by:** Extends `D-020` by converting the fixed-budget dominance diagnostic into a selector-governance rule.

### D-022 — Budget-aware temporal grid and labeling protocol
- **Status:** Frozen
- **Date:** 2026-04-30
- **Decision:** The first budget-aware exception analysis will be constructed from the already reviewed R1/R2/R3 main benchmark artifacts without rerunning solvers. The preregistered temporal grid is `[100, 250, 500, 1000, 2000, 3000, 4000, 5000]` milliseconds. The maximum considered budget is the official `T*=5000 ms`; post-budget improvements are excluded from `y_i*(t)` construction and may be used only for caveat or sensitivity discussion. Instrumented metaheuristics contribute the best validated checkpoint with `checkpoints[].time_ms <= t`. Point-output baselines (`METIS`, `KaHIP`) contribute only at budgets `t` for which their observed `elapsed_ms <= t`. Repeated stochastic observations are collapsed at `(instance, algorithm, t)` using the frozen median-quality rule, with median observed time and lexicographic fallback as tie-breakers.
- **Rationale:** The project needs to test whether algorithm recommendation changes with available wall-clock budget while avoiding post-hoc temporal thresholds and avoiding artificial anytime trajectories for point-output baselines. Restricting the first analysis to the official `T*` hard cap preserves the fixed-budget campaign boundary and prevents post-timeout overshoot from becoming the source of budget-aware labels.
- **Impact:** No budget-aware winner table, temporal exception claim, or budget-aware selector claim is canonical unless it uses this grid and labeling protocol, or unless this decision is explicitly superseded before analysis.
- **Supersedes / Superseded by:** Instantiates the budget-aware layer previously left concrete-pending in the methodology and open issues.
