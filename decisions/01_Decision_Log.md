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

### D-007 — Greedy demoted from official benchmark flow
- **Status:** Frozen
- **Date:** 2026-03-30
- **Decision:** The `greedy` baseline remains available in the repository only as an exploratory / engineering track and is not part of the official benchmark portfolio, official phase-1 plans, or the canonical selector label space.
- **Rationale:** The canonical monograph portfolio is currently frozen as SA, TS, ILS, GRASP, METIS, and KaHIP. Keeping `greedy` in the official flow would create scope drift between canon, pipeline, and prose.
- **Impact:** Official plans exclude `greedy`; exploratory plans may preserve it under separate filenames; no monograph claim may treat `greedy` as a canonical benchmark participant unless a later canonical decision supersedes this one.
- **Supersedes / Superseded by:**

### D-008 — Canonical anytime integration sequence
- **Status:** Frozen
- **Date:** 2026-03-30
- **Decision:** Canonical anytime integration will proceed one solver at a time in the sequence SA, then ILS, then GRASP, with TS last.
- **Rationale:** The legacy repository provides reusable structural references for SA, ILS, and GRASP, but no Tabu Search implementation. Integrating one solver at a time minimizes regression ambiguity and keeps each adapter auditable against the current runner and schema.
- **Impact:** No official plan expansion occurs until each solver passes its own local integration gate. TS remains an explicit pending gap until a valid source implementation is located or written.
- **Supersedes / Superseded by:**

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
