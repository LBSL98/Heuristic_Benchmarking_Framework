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

### EXP-GREEDY-001 — Exploratory greedy engineering hardening
- **Status:** Completed
- **Date:** 2026-03-30
- **Question answered:** Can the repository sustain an exploratory greedy baseline with auditable outputs without making it part of the canonical thesis benchmark?
- **Code reference / branch / commit:** `main` through PR #23 and exploratory branch work around `fix/greedy-artifact-paths`
- **Input instances:** Phase-1 synthetic panel and pilot subsets
- **Algorithms compared:** greedy, METIS, KaHIP (exploratory engineering flow only)
- **Budget protocol:** Equal wall-clock budget per instance under mono-thread execution
- **Environment constraints:** Controlled runner, plan-scoped manifest, contract-clean JSON outputs, traced artifact paths
- **Primary metrics:** Artifact schema validity, manifest scope, instance_id completeness, path traceability, elapsed_ms/checkpoint consistency
- **Outputs generated:** Audit reports 208–215 and related hardening patches
- **Main finding:** The greedy exploratory track was technically integrated and hardened, but it remains non-canonical relative to the thesis portfolio.
- **Limitations / caveats:** This entry supports engineering/governance discussion only. It does not authorize monograph claims treating greedy as an official benchmark participant.
- **Can this support prose in the monograph?** No
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-PORT-001 — Legacy SA/ILS/GRASP portability audit
- **Status:** Completed
- **Date:** 2026-03-30
- **Question answered:** Can the legacy PA-Novo repository be ported directly into the canonical FORJA runner for SA, ILS, GRASP, and TS?
- **Code reference / branch / commit:** `main` after PR #24 plus legacy repository snapshot used in PR17 bootstrap audit
- **Input instances:** N/A (static code and structure audit)
- **Algorithms compared:** SA, ILS, GRASP, greedy/improvement auxiliaries, TS availability check
- **Budget protocol:** N/A
- **Environment constraints:** Static portability inspection against the current FORJA runner contract
- **Primary metrics:** Dependency structure, objective compatibility, instance-format compatibility, TS file availability
- **Outputs generated:** `audit_reports/pr17_sa_bootstrap/225_sa_portability_summary.md`
- **Main finding:** The legacy repository provides structural references for SA, ILS, and GRASP, but it solves a different clustering/FO1 problem and does not contain Tabu Search. Direct porting is not safe.
- **Limitations / caveats:** Supports integration planning only; it does not validate any canonical solver implementation yet.
- **Can this support prose in the monograph?** No
- **Mapped in `08_Results_to_Text_Map.md`:** No


### EXP-BENCH-PILOT-001 — Benchmark pilot preregistration placeholder
- **Status:** Planned
- **Date:** 2026-04-16
- **Question answered:** To be finalized after the remaining benchmark-release methodological blockers are frozen.
- **Code reference / branch / commit:** Release-candidate branch/commit to be filled after final benchmark-release preparation.
- **Input instances:** Canonical pilot panel to be finalized after benchmark-release checklist closure.
- **Algorithms compared:** Canonical benchmark portfolio (METIS, KaHIP, SA, TS, ILS, GRASP), subject to the currently frozen execution and aggregation rules.
- **Budget protocol:** To be copied from the final frozen benchmark protocol after closure of the still-open benchmark-release blockers.
- **Environment constraints:** Controlled mono-thread audited environment; final external-validity wording still pending the relevant benchmark-release decision.
- **Primary metrics:** To be finalized after the analytical benchmark synthesis freeze.
- **Outputs generated:** Validated raw artifacts, manifest, aggregated per-instance table, selector-ready dataset inputs, pilot audit trail.
- **Main finding:** N/A — preregistration placeholder only.
- **Limitations / caveats:** This entry is a scaffolding placeholder and does not authorize pilot execution while the benchmark-release blockers remain open.
- **Can this support prose in the monograph?** No
- **Mapped in `08_Results_to_Text_Map.md`:** No


### EXP-BENCH-MAIN-001 — Main benchmark campaign preregistration placeholder
- **Status:** Planned
- **Date:** 2026-04-16
- **Question answered:** To be finalized after the benchmark-release protocol is fully frozen and the pilot review is completed.
- **Code reference / branch / commit:** Release-candidate branch/commit to be filled before campaign start.
- **Input instances:** Canonical main campaign panel to be filled after final release approval.
- **Algorithms compared:** Canonical benchmark portfolio (METIS, KaHIP, SA, TS, ILS, GRASP), subject to the final frozen campaign contract.
- **Budget protocol:** To be copied from the final frozen benchmark protocol after closure of the still-open benchmark-release blockers.
- **Environment constraints:** Controlled mono-thread audited environment with final caveats to be filled from the canonical methodology at release time.
- **Primary metrics:** To be finalized after the analytical benchmark synthesis freeze.
- **Outputs generated:** Main raw artifacts, validated manifests, aggregated benchmark tables, selector training/evaluation inputs, campaign audit trail.
- **Main finding:** N/A — preregistration placeholder only.
- **Limitations / caveats:** This entry is a scaffolding placeholder and does not authorize the main campaign before pilot review and final methodological freeze.
- **Can this support prose in the monograph?** No
- **Mapped in `08_Results_to_Text_Map.md`:** No


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
- **Mapped in `08_Results_to_Text_Map.md`:** No
