# 06_Experiment_Ledger.md

## Purpose

This file is the canonical ledger for experiments, runs, outputs, and traceable empirical evidence. A result should not enter the monograph unless it can be traced here.

## Entry template

### EXP-XXX — Title
- **Status:** Planned | Running | Completed | Rejected
- **Date:** YYYY-MM-DD
- **Question answered:**
- **Code reference / branch / commit:**
- **Input instances:**
- **Algorithms compared:**
- **Budget protocol:**
- **Environment constraints:**
- **Primary metrics:**
- **Outputs generated:**
- **Main finding:**
- **Limitations / caveats:**
- **Can this support prose in the monograph?** Yes / No / Partial
- **Mapped in `08_Results_to_Text_Map.md`:** Yes / No

## Ledger policy

- No monograph claim should cite “results” that do not appear here.
- Negative, null, and inconclusive experiments must also be logged.
- If a run is exploratory and not publication-grade, say so explicitly.

### EXP-REPO-001 — Final repository stabilization and freeze validation
- **Status:** Completed
- **Date:** 2026-03-12
- **Question answered:** Is the final repository state auditable, merge-consistent, and safe to use as the project freeze baseline?
- **Code reference / branch / commit:** `main` after final integration from `stabilization/contracts`
- **Input instances:** N/A
- **Algorithms compared:** N/A
- **Budget protocol:** N/A
- **Environment constraints:** GitHub branch protection, repository ruleset, controlled merge sequence, clean-clone validation
- **Primary metrics:** PR integration status, main/stabilization diff status, ruleset consistency, clean-clone status
- **Outputs generated:** final freeze report, clean clone check, merged PR trail (#11, #12, #8)
- **Main finding:** The repository was stabilized and integrated into `main`, with code and minimal defensible documentation merged before final release integration.
- **Limitations / caveats:** This entry supports reproducibility/governance prose only, not algorithmic-performance claims.
- **Can this support prose in the monograph?** Partial
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-CALIB-001 — Bounded pre-benchmark hyperparameter calibration
- **Status:** Completed
- **Date:** 2026-04-25
- **Question answered:** Which single global hyperparameter profile should be frozen for each stochastic participant (`SA`, `TS`, `ILS`, `GRASP`) before the main benchmark campaign starts?
- **Code reference / branch / commit:** `chore-repo-canonical-alignment-sweep`; calibration scaffolds committed through `5c49e75`, `6e09433`, and `789d616`
- **Input instances:** Six-instance calibration panel declared in `configs/hyperparameter_calibration_matrix.yaml`
- **Algorithms compared:** `SA`, `TS`, `ILS`, `GRASP`, each evaluated against a bounded candidate-profile set. This experiment did not benchmark METIS or KaHIP.
- **Budget protocol:** Stage 1 coarse screening used six instances, seeds `[42, 43, 44]`, and 5-second wall-clock budgets. Because Stage 1 showed that SA was not saturating the temporal budget, an SA-only saturation micro-round was executed for `sa_d` and `sa_e` with increased `max_steps`. Stage 2 short confirmation then compared the final two candidates per algorithm under seeds `[42, 43, 44, 45, 46]`, the same 5-second budget, and the same validation/collapse rules.
- **Environment constraints:** Controlled mono-thread audited environment, same execution controls as the benchmark release candidate.
- **Primary metrics:** Per-instance collapsed validated quality across candidate profiles, with median final validated cutsize as primary aggregate and median `elapsed_ms` as tie-break.
- **Outputs generated:** Stage 1 coarse-screening artifacts, SA saturation artifacts, Stage 2 confirmation artifacts, collapsed per-instance summaries, candidate scoreboards, finalist-selection material, and the evidence required to freeze `D-012`.
- **Main finding:** The final frozen stochastic profiles for the benchmark release are `grasp_b`, `ils_b`, `sa_e_maxsteps_100000`, and `ts_c`.
- **Limitations / caveats:** This experiment supports only hyperparameter-freeze and benchmark-method prose. It does not by itself support claims of overall benchmark superiority.
- **Can this support prose in the monograph?** Partial
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-BENCH-PILOT-001 — Pilot benchmark campaign under frozen protocol
- **Status:** Completed
- **Date:** 2026-04-27
- **Question answered:** Does the fully frozen benchmark release candidate execute end-to-end under the canonical protocol with valid artifacts, manifests, and analysis-ready outputs?
- **Code reference / branch / commit:** `chore-repo-canonical-alignment-sweep`; pilot review completed at `a0c03fe1195d6e89c24f0d556bb2a53e281bb2d6`, after output-directory separation through `360683c` and KaHIP timeout-contract repair through `5b932a7`
- **Input instances:** Pilot slice defined by `configs/plan_phase_1_pilot_baselines.yaml` and `configs/plan_phase_1_pilot_metaheuristics.yaml`
- **Algorithms compared:** Canonical thesis portfolio (`SA`, `TS`, `ILS`, `GRASP`, `METIS`, `KaHIP`) under the frozen benchmark contract
- **Plan reference:** `configs/plan_phase_1_pilot_baselines.yaml` and `configs/plan_phase_1_pilot_metaheuristics.yaml`
- **Budget protocol:** Same wall-clock fairness semantics, same validation contract, same repeated-run collapse rules, same seed policy, and the frozen stochastic profiles from `D-012`
- **Environment constraints:** Audited controlled WSL2 release-candidate environment under the current benchmark contract
- **Primary metrics:** Expected-versus-actual artifact counts, schema-validation errors, per-plan completion, status admissibility, and clean combined pilot summary
- **Outputs generated:** Validated raw artifacts in `data/results_raw/pilot_baselines` and `data/results_raw/pilot_metaheuristics`, live execution logs, `317_final_clean_pilot_combined_summary.json`, and `317_pilot_review_gate.json`
- **Main finding:** The fully frozen benchmark release candidate executed end-to-end under the canonical protocol. The pilot review gate closed with `EXPECTED_TOTAL=112`, `ACTUAL_TOTAL=112`, `SCHEMA_ERRORS=0`, and `APPROVAL_CANDIDATE=1`.
- **Limitations / caveats:** This entry supports operational validation and execution-governance claims only. It does not by itself support the comparative scientific conclusions reserved for the main campaign.
- **Can this support prose in the monograph?** Partial
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-BENCH-MAIN-001 — Main comparative benchmark campaign
- **Status:** Completed — raw execution and post-campaign review completed; collapsed analysis still pending
- **Date:** 2026-04-30
- **Question answered:** Under the frozen benchmark protocol and the completed R1/R2/R3 panel gate, did the official main benchmark execute and produce reviewable raw artifacts for the canonical solver portfolio?
- **Code reference / branch / commit:** `feat/main-benchmark-r1-r2-r3-preflight`; `fd3d475824cbb9070310dfda1322f7f0ef988177`, aligned with `origin/main`.
- **Input instances:** 12-instance R1/R2/R3 panel from `data/instances/regime_panel_manifest.csv`: `R1=8`, `R2=2`, `R3=2`.
- **Algorithms compared:** Canonical thesis portfolio: `METIS`, `KaHIP`, `SA`, `ILS`, `GRASP`, and `TS`.
- **Plan reference:** `configs/plan_phase_1_baselines.yaml` and `configs/plan_phase_1_metaheuristics.yaml`.
- **Budget protocol:** Wall-clock fair(time) protocol with `budget_time_ms=5000`, `k=8`, `beta=0.03`; baselines single-run with seed `42`; stochastic participants repeated with seeds `[42, 43, 44, 45, 46]`.
- **Environment constraints:** Audited controlled WSL2 release-candidate environment under the current benchmark contract.
- **Primary metrics:** Expected-versus-actual raw artifact counts, JSON parseability, status distribution, feasibility, `elapsed_ms` presence, checkpoint timestamp contract, overshoot sensitivity, and raw artifact readiness for later collapse.
- **Outputs generated:** Archived stale output directories, active raw outputs in `data/results_raw/main_baselines` and `data/results_raw/main_metaheuristics`, live logs under `audit_reports/main_benchmark_preflight/374_*`, post-campaign review `375e_post_campaign_review_gate_final`, and overshoot audit `376_timeout_overshoot_and_tiebreak_audit`.
- **Main finding:** The campaign produced the expected 264 raw artifacts: 24 baseline artifacts and 240 metaheuristic artifacts. All artifacts parsed, all were feasible, `elapsed_ms` was present, checkpoint timestamps followed `time_ms`, and the review gate closed with `approval_candidate=true`.
- **Limitations / caveats:** Timeout overshoot occurred in 181 timeout-status metaheuristic runs, especially GRASP, ILS, and TS. The clipped-time sensitivity audit found no winner change under the audited tie-break comparison, so this caveat does not block the raw campaign, but it must be reported. The current evidence is raw/reviewed execution evidence; collapsed benchmark tables, statistical synthesis, selector-ready data, and final result claims remain pending. The small `R2=2` and `R3=2` slices support coverage and descriptive analysis, not strong per-regime inference.
- **Can this support prose in the monograph?** Partial
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-PANEL-REGIME-GATE-001 — R1/R2/R3 main-plan materialization gate
- **Status:** Completed
- **Date:** 2026-04-30
- **Question answered:** Do the official main benchmark plans materialize the three declared morphological regimes and preserve parity between baseline and metaheuristic executions?
- **Code reference / branch / commit:** `feat/main-benchmark-r1-r2-r3-preflight`; `fd3d475824cbb9070310dfda1322f7f0ef988177`
- **Input instances:** `data/instances/regime_panel_manifest.csv`, with 12 instances distributed as `R1=8`, `R2=2`, and `R3=2`.
- **Algorithms compared:** N/A — plan validation gate only. It did not produce algorithmic performance evidence.
- **Budget protocol:** The gate verified shared problem and execution parameters for the official baseline and metaheuristic plans, including `k=8`, `beta=0.03`, `budget_time_ms=5000`, seed policy, and artifact-contract compatibility.
- **Environment constraints:** Repository plan-validation environment at the cited commit.
- **Primary metrics:** Regime counts, instance-path existence, baseline/metaheuristic plan parity, shared problem parameters, budget consistency, and artifact-contract compatibility.
- **Outputs generated:** `audit_reports/regime_panel_gate/364_plan_gate_audit.json`, updated R1/R2/R3 manifest, updated official plan files, PR #46 materialization trail, and preflight artifacts under `audit_reports/main_benchmark_preflight/373_*`.
- **Main finding:** The official plans materialized a shared 12-instance R1/R2/R3 universe and passed the plan-level gate needed before the main benchmark execution.
- **Limitations / caveats:** This gate supports execution governance and claim eligibility only. It does not support performance conclusions.
- **Can this support prose in the monograph?** Partial, for methodology/governance prose only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes
