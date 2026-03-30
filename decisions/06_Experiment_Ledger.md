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
