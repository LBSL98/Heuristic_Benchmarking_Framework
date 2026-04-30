# 07_Open_Issues.md

## Purpose

This file tracks unresolved project problems that can still affect coherence, correctness, or delivery quality.

## Open issues

### OI-001 — General objective is too long and overloaded
- **Type:** Writing / framing
- **Severity:** High
- **Origin:** Committee feedback
- **Current status:** Open
- **Needed action:** Rewrite the general objective into a shorter, title-aligned version.

### OI-002 — Specific objectives mix deliverables with workflow steps
- **Type:** Writing / structure
- **Severity:** High
- **Origin:** Committee feedback
- **Current status:** Open
- **Needed action:** Rewrite specific objectives as concrete deliverables or analytical commitments.

### OI-003 — Main prose is too coupled to file names and transient artifacts
- **Type:** Writing / reproducibility framing
- **Severity:** High
- **Origin:** Committee feedback
- **Current status:** Open
- **Needed action:** Sweep the text and replace file-name anchoring with representational descriptions.

### OI-004 — Figure legends are too long
- **Type:** Writing / figures
- **Severity:** Medium
- **Origin:** Committee feedback + current list of figures
- **Current status:** Open
- **Needed action:** Shorten captions and move interpretation into body text.

### OI-005 — Some benchmarking concepts may still be hard to digest
- **Type:** Theory / methodology / writing
- **Severity:** Medium
- **Origin:** Committee feedback
- **Current status:** Open
- **Needed action:** Add clearer first-use explanations for wall-clock time and related concepts.

### OI-006 — Official benchmark prose and final monograph text still require canonical cleanup
- **Type:** Writing / methodology alignment
- **Severity:** High
- **Origin:** Canon vs prose audit
- **Current status:** Open
- **Needed action:** Keep the official thesis narrative aligned with the canonical portfolio, artifact contract, and release-candidate documentation without reintroducing exploratory scope into benchmark claims.

### OI-007 — WSL2 external-validity boundary is still not frozen
- **Type:** Methodology / environment / validity
- **Severity:** Medium
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-009`. The audited WSL2 environment is accepted as the controlled benchmark surface for internal comparison, with explicit restriction against overgeneralizing absolute timing results to bare-metal or arbitrary external environments.

### OI-008 — Analytical benchmark synthesis metrics are still not frozen
- **Type:** Methodology / analysis
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-010` for the benchmark-synthesis layer. `TTT`, `ECDF`, and `performance profiles` now have canonical operational definitions. Selector regret was deliberately removed from this freeze and remains deferred to the selector-evaluation track under `D-011` / `D-015`.

### OI-009 — ASP outer validation protocol is still not frozen
- **Type:** Methodology / selector evaluation
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-011`. Selector evaluation now uses a deterministic external holdout at the instance level over the collapsed per-instance table, with an untouched-test rule. Selector regret is canonically anchored to this outer protocol, while the internal CART regime remains deferred to `D-015`.

### OI-010 — Final stochastic hyperparameter freeze is still provisional
- **Type:** Methodology / calibration / benchmark protocol
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-012` after completion of `EXP-CALIB-001`. The canonical release profiles are now `grasp_b`, `ils_b`, `sa_e_maxsteps_100000`, and `ts_c`, and no retuning is allowed in the main benchmark campaign.

### OI-011 — Final artifact-schema confirmation must be canonically closed
- **Type:** Artifact contract / schema / runner
- **Severity:** Medium
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Closed by `D-016`. The active release-candidate runner/schema/manifest contract is now treated as canonically confirmed. Timing fields, checkpoint naming, optional NFE semantics, status meanings, and manifest linkage must follow the confirmed active contract rather than remain described as pending.

### OI-012 — Benchmark pilot and main campaign preregistration are still placeholders
- **Type:** Governance / experiment registration
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-014` and materialized in `06_Experiment_Ledger.md` through real planned entries for `EXP-BENCH-PILOT-001` and `EXP-BENCH-MAIN-001`. The main campaign remained blocked until pilot review was complete.

### OI-013 — Conceptual benchmark figures still need final technical clearance
- **Type:** Figures / writing / methodology
- **Severity:** Medium
- **Origin:** Benchmark release preparation
- **Current status:** Open
- **Needed action:** Review benchmark figures and captions to ensure conceptual-only diagrams are clearly distinguished from empirical result figures.

### OI-014 — CART model-selection regime is still not frozen
- **Type:** Methodology / selector model selection
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-015`. The canonical selector track uses a fixed CART regime, not a searched regime. Any future selector implementation must declare one explicit deterministic CART configuration inside the already frozen outer holdout protocol of `D-011`.

### OI-015 — MkDocs navigation still leaves one active page outside nav
- **Type:** Documentation / publication surface
- **Severity:** Low
- **Origin:** MkDocs audit
- **Current status:** Open
- **Needed action:** Decide whether `docs/specs/mealpy_integration_plan.md` should enter the active nav or remain intentionally unlisted and documented as such.

### OI-019 — Main benchmark plans must materialize R1/R2/R3
- **Type:** Methodology / experiment registration / validity
- **Severity:** High
- **Origin:** Instance-panel coverage audit before main campaign
- **Current status:** Resolved
- **Needed action:** Resolved by the R1/R2/R3 materialization gate and PR #46. The official baseline and metaheuristic plans now share the same 12-instance R1/R2/R3 universe, and the gate was validated through `364_plan_gate_audit.json`, `373_preflight_summary.json`, and `375e_post_campaign_review_gate_final.json`. Synthetic-only outputs remain superseded for three-regime claims.

### OI-020 — Timeout overshoot caveat must be preserved in analysis and prose
- **Type:** Methodology / analysis / validity
- **Severity:** Medium
- **Origin:** `376_timeout_overshoot_and_tiebreak_audit`
- **Current status:** Open
- **Needed action:** When producing collapsed tables, figures, and monograph prose, preserve the caveat that 181 timeout-status metaheuristic runs exceeded the nominal 5-second wall-clock budget. The audited clipped-time sensitivity check did not alter winner identities, so the raw campaign is not blocked, but result prose must not claim exact hard-stop behavior for those runs.

### OI-021 — Fixed-budget collapse must be classified before selector claims
- **Type:** Results governance / selector validity
- **Severity:** High
- **Origin:** Fixed-budget collapse `393` and independent audit `395`
- **Current status:** Resolved
- **Needed action:** Resolved by classifying the current fixed-budget result as a multilevel-dominance diagnostic. The result may support fixed-budget dominance prose for the evaluated panel, but it does not authorize strong ASP or selector-utility claims.

### OI-022 — Fixed-budget exception diagnostics must decide selector eligibility
- **Type:** Results governance / selector validity
- **Severity:** High
- **Origin:** Milestone 3 fixed-budget exception diagnostics
- **Current status:** Resolved
- **Needed action:** Resolved by `EXP-FIXED-BUDGET-EXCEPTION-DIAGNOSTICS-001`. The current fixed-budget table has negligible SBS-VBS gap and nearly degenerate winner labels, so a strong multiclass fixed-budget selector claim is blocked. Limited exception/competitiveness detection remains admissible as exploratory analysis.

### OI-023 — Budget-aware temporal grid must be preregistered
- **Type:** Methodology / budget-aware analysis
- **Severity:** High
- **Origin:** Milestone 4 budget-aware exception analysis
- **Current status:** Resolved
- **Needed action:** Resolved by `D-022` and `EXP-BUDGET-AWARE-PROTOCOL-001`. The first budget-aware analysis is restricted to the preregistered grid `[100, 250, 500, 1000, 2000, 3000, 4000, 5000]` ms, with hard cap `T*=5000 ms`, checkpoint-derived metaheuristic observations, and point-output baseline observations only after observed `elapsed_ms`.

### OI-024 — Budget-aware temporal labels must be interpreted through availability
- **Type:** Results governance / budget-aware analysis
- **Severity:** High
- **Origin:** `442_budget_aware_yit_table` and `444_budget_aware_temporal_exception_synthesis`
- **Current status:** Resolved
- **Needed action:** Resolved by `EXP-BUDGET-AWARE-YIT-001`. The budget-aware table contains temporal winner transitions, but the non-multilevel wins at `100 ms` are availability-driven because the multilevel reference is often unavailable. Budget-aware selector claims remain limited to exploratory availability/competitiveness analysis unless superseded by later evidence.

### OI-025 — TS-Rust fidelity contract must precede implementation
- **Type:** Methodology / implementation-maturity ablation
- **Severity:** High
- **Origin:** Milestone TS-Rust fidelity and implementation-maturity ablation
- **Current status:** Resolved
- **Needed action:** Resolved by `D-023` and `EXP-TS-RUST-CONTRACT-001`. TS-Rust is authorized only as a faithful TS implementation-maturity ablation. Implementation, validation, and performance claims remain blocked until later issues are completed.

## Notes

- The pilot benchmark review completed successfully on 2026-04-27 (`EXPECTED_TOTAL=112`, `ACTUAL_TOTAL=112`, `SCHEMA_ERRORS=0`, `APPROVAL_CANDIDATE=1`), but that operational milestone does not by itself close the remaining writing, figure-clearance, or publication-surface issues.
