# 08_Results_to_Text_Map.md

## Purpose

This file maps empirical results to the exact claims they are allowed to support in the monograph. Its purpose is to prevent overclaim and to make every conclusion auditable.

## Mapping template

| Claim ID | Monograph claim | Supported by experiment(s) | Supported by figure/table | Support strength | Allowed wording | Forbidden wording | Notes |
|---|---|---|---|---|---|---|---|
| C-XXX |  |  |  | Strong / Partial / Weak |  |  |  |

## Rules

1. If a claim has no mapped support, it should not survive final revision.
2. “Strong support” means the evidence directly matches the claim scope.
3. “Partial support” requires narrower wording in the monograph.
4. “Forbidden wording” is mandatory whenever results are easy to overstate.

| Claim ID | Monograph claim | Supported by experiment(s) | Supported by figure/table | Support strength | Allowed wording | Forbidden wording | Notes |
|---|---|---|---|---|---|---|---|
| C-REPO-001 | The final repository state used in the monograph was stabilized through a controlled integration process, with code and documentation merged separately before final release integration. | EXP-REPO-001 | None | Strong | “the final repository state was stabilized through a controlled integration sequence” | “the repository is fully reproducible in every respect” / “all experimental claims are validated by this alone” | Governance/reproducibility support only; not performance evidence. |
| C-CALIB-001 | The benchmark release froze one global hyperparameter profile per stochastic participant after a bounded calibration stage. | EXP-CALIB-001 | None | Strong | “the benchmark release froze the stochastic profiles `grasp_b`, `ils_b`, `sa_e_maxsteps_100000`, and `ts_c` after bounded calibration” | “these are universally optimal hyperparameters” / “the calibration proves global superiority of any algorithm” | Supports calibration/methodology prose only. |
| C-PILOT-001 | The pilot executed the fully frozen benchmark protocol end-to-end and validated the artifact chain and schema-conformant outputs. | EXP-BENCH-PILOT-001 | None | Strong | “the pilot validated executability, artifact generation, and schema-conformant outputs under the frozen protocol” | “the pilot already establishes the comparative conclusions of the main benchmark” | Operational validation only. |
| C-PILOT-002 | The pilot review gate closed with full expected coverage and no schema errors. | EXP-BENCH-PILOT-001 | None | Strong | “the pilot review gate closed with 112 expected artifacts, 112 actual artifacts, and zero schema errors” | “the pilot proves algorithmic robustness in every scenario” | Supports audit/protocol prose only. |
| C-PILOT-003 | After successful pilot review, the main benchmark campaign became admissible under the same frozen protocol. | EXP-BENCH-PILOT-001 | None | Strong | “after successful pilot review, the main campaign became admissible under the same frozen protocol” | “the main campaign no longer needs methodological caution” / “future protocol changes are impossible” | Governance/transition claim only. |

| C-PANEL-REGIME-GATE-001 | The main benchmark requires an executable R1/R2/R3 instance panel before it can support three-regime or topology-conditioned selector claims. | EXP-PANEL-REGIME-GATE-001 (planned only) | None | Prospective only | “the main campaign is gated on a validated R1/R2/R3 plan manifest; synthetic-only plans can support only pilot or controlled-slice claims” | “synthetic-only results establish conclusions for all three regimes” / “the selector is trained on a morphologically diverse panel if only R1 is present” / “R2/R3 are promised by prose even if absent from plans” | This is a planning/guardrail row. Empirical claims require completed main benchmark outputs from the validated R1/R2/R3 panel and later mapped result rows. |
