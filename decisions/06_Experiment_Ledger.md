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
- **Status:** Planned — blocked until `EXP-PANEL-REGIME-GATE-001` is completed
- **Date:** 2026-04-25
- **Question answered:** Under the fully frozen benchmark protocol, how do the canonical solver families compare on the declared benchmark slices and analysis surfaces?
- **Code reference / branch / commit:** `chore-repo-canonical-alignment-sweep`; execution was preregistered under `D-014` and became admissible after the successful pilot review recorded in `EXP-BENCH-PILOT-001`
- **Input instances:** Main benchmark slices defined by the official main plans currently tracked in the repository
- **Algorithms compared:** Canonical thesis portfolio (`SA`, `TS`, `ILS`, `GRASP`, `METIS`, `KaHIP`) under the frozen benchmark contract
- **Plan reference:** `configs/plan_phase_1_baselines.yaml` and `configs/plan_phase_1_metaheuristics.yaml`
- **Budget protocol:** Same wall-clock fairness semantics, same validation contract, same repeated-run collapse rules, same seed policy, and the frozen stochastic profiles from `D-012`
- **Environment constraints:** Audited controlled WSL2 release-candidate environment under the current benchmark contract
- **Primary metrics:** Validated main artifacts, manifests, collapsed benchmark tables, benchmark-analysis inputs, and selector-ready collapsed dataset inputs
- **Outputs generated:** N/A — planned main campaign entry only
- **Main finding:** N/A — planned main campaign entry only
- **Limitations / caveats:** Although pilot review no longer blocks execution, any protocol-relevant change discovered before or during the main campaign still requires explicit canon reopening or updated preregistration rather than silent continuation.
- **Can this support prose in the monograph?** No
- **Mapped in `08_Results_to_Text_Map.md`:** No

### EXP-PANEL-REGIME-GATE-001 — R1/R2/R3 main-plan materialization gate
- **Status:** Planned
- **Date:** 2026-04-30
- **Question answered:** Do the official main benchmark plans materialize the three declared morphological regimes and preserve parity between baseline and metaheuristic executions?
- **Code reference / branch / commit:** To be declared when the updated plans are committed.
- **Input instances:** The planned R1/R2/R3 instance manifest to be used by the main benchmark. The manifest must label each instance as `R1`, `R2`, or `R3` and must be shared by the baseline and metaheuristic plans.
- **Algorithms compared:** N/A — plan validation gate only. It does not produce algorithmic performance evidence.
- **Budget protocol:** N/A for performance; the gate checks that budget semantics, `k`, balance tolerance, validation settings, and artifact contract are aligned across the official plans.
- **Environment constraints:** Repository and plan-validation environment used to inspect plan files, instance paths, metadata, and schema compatibility.
- **Primary metrics:** Counts per regime, path-existence checks, plan parity between baseline and metaheuristic plans, shared problem-parameter checks, and compatibility with the active artifact contract.
- **Outputs generated:** An updated R1/R2/R3 plan manifest and a plan-gate report before main execution.
- **Main finding:** N/A — planned gate entry only.
- **Limitations / caveats:** This gate supports execution governance and claim eligibility only. It does not support performance conclusions.
- **Can this support prose in the monograph?** Partial, for methodology/governance prose only after completion.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.
