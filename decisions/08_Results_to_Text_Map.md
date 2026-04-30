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
| C-PILOT-003 | After successful pilot review, the benchmark tooling became admissible under the frozen protocol, but the main campaign still required any later gates such as the R1/R2/R3 panel-materialization gate. | EXP-BENCH-PILOT-001 | None | Strong for pilot-tooling transition; not sufficient for R1/R2/R3 claims | “after successful pilot review, the benchmark tooling became admissible under the same frozen protocol, subject to later gates such as the R1/R2/R3 panel-materialization gate” | “the main campaign no longer needs methodological caution” / “future protocol changes are impossible” / “pilot success alone proves three-regime coverage” | Governance/transition claim only. After `D-019`, main execution also required `EXP-PANEL-REGIME-GATE-001`. |

| C-PANEL-REGIME-GATE-001 | The main benchmark used an executable R1/R2/R3 instance panel before generating the official raw campaign. | EXP-PANEL-REGIME-GATE-001 | `364_plan_gate_audit.json`; `373_preflight_summary.json`; `375e_post_campaign_review_gate_final.json` | Strong for execution-governance and panel-coverage claims | “the official main benchmark was gated on and executed over a validated 12-instance panel with `R1=8`, `R2=2`, and `R3=2`” | “the panel size is sufficient for strong per-regime statistical inference” / “synthetic-only results establish conclusions for all regimes” | Supports panel eligibility and coverage, not performance conclusions by itself. |
| C-BENCH-MAIN-RAW-001 | The official R1/R2/R3 main campaign produced the expected reviewed raw artifact set under the frozen protocol. | EXP-BENCH-MAIN-001 | `375e_post_campaign_review_gate_final.json` | Strong for raw execution/artifact-readiness claims; not yet a final comparative-result claim | “the reviewed raw campaign produced 264 expected artifacts, all parseable and feasible, with `elapsed_ms` and `checkpoints[].time_ms` present” | “the final benchmark conclusions are already established” / “the selector dataset is already ready” / “collapsed statistical analysis is complete” | Collapse, statistical synthesis, and selector-ready construction remain pending. |
| C-BENCH-MAIN-OVERSHOOT-001 | Timeout overshoot occurred in timeout-status metaheuristic runs, but the audited clipped-time sensitivity check did not change winner identities under the gate comparison. | EXP-BENCH-MAIN-001 | `376_timeout_overshoot_and_tiebreak_audit.json` | Partial: supports caveat and non-blocking gate decision, not a claim that hard time limits were exact | “timeout overshoot was observed and is reported as a validity caveat; in the audited clipped-time sensitivity check, winner identities did not change” | “all algorithms stopped exactly at 5 seconds” / “overshoot is irrelevant” / “overshoot proves the benchmark is invalid” | Must be preserved in analysis prose and limitations. |
