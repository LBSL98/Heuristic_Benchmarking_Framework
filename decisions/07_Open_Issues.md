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

### OI-026 — TS-Rust fidelity validation before ablation
- **Type:** Validation / implementation-maturity ablation
- **Severity:** High
- **Origin:** Issue #67, PR #71
- **Current status:** Resolved
- **Needed action:** Resolved by `EXP-TS-RUST-VALIDATION-001`. TS-Rust passed semantic and artifact-level invariant validation on three controlled toy cases. This authorizes proceeding to the implementation-maturity ablation but does not authorize speed, superiority, trajectory-equivalence, or general metaheuristic claims.

### OI-027 — TS-Rust implementation-maturity ablation
- **Type:** Experimental result / implementation-maturity ablation
- **Severity:** High
- **Origin:** Issue #68
- **Current status:** Resolved
- **Needed action:** Resolved by `EXP-TS-RUST-ABLATION-001`. The ablation supports TS-specific implementation-maturity claims only. It does not authorize trajectory-equivalence, full algorithmic-equivalence, all-metaheuristic, or main-portfolio claims. The Python budget overshoot caveat is mandatory in any prose derived from this result.

### OI-028 — Full Rust metaheuristic portfolio still needs implementation and validation
- **Type:** Methodology / implementation maturity / benchmark expansion
- **Severity:** High
- **Origin:** CART-validity-oriented scope expansion after completed TS-Rust ablation
- **Current status:** Open
- **Needed action:** The pre-implementation fidelity contracts for `SA-Rust`, `ILS-Rust`, and `GRASP-Rust` are frozen in `decisions/12_Rust_Portfolio_Fidelity_Contracts.md` and registered by `EXP-RUST-PORTFOLIO-CONTRACTS-001`. The remaining work is implementation, adapter integration, smoke execution, artifact validity, conformance validation, and only then any portfolio-level ablation. The Rust layer must still not add multilevel refinement, warm starts, new neighborhoods, or per-instance retuning unless registered as a new algorithmic variant.
- **Progress note 2026-05-02:** `SA-Rust` implementation is integrated through binary, adapter, single-run, CLI and plan-runner paths. Formal validation, ablation, `ILS-Rust`, and `GRASP-Rust` remain pending.
- **Progress note 2026-05-02:** `SA-Rust` formal validation is completed on the controlled invariant panel. `SA-Rust` ablation, `ILS-Rust`, `GRASP-Rust`, and full-portfolio validation remain pending.
- **Progress note 2026-05-02:** `ILS-Rust` implementation is integrated through binary, adapter, single-run, CLI and plan-runner paths. `ILS-Rust` formal validation, `SA-Rust` ablation, `GRASP-Rust`, and full-portfolio validation remain pending.
- **Progress note 2026-05-02:** `ILS-Rust` formal validation is completed on the controlled invariant panel. `SA-Rust` ablation, `ILS-Rust` ablation, `GRASP-Rust`, and full-portfolio validation remain pending.
- **Progress note 2026-05-02:** `GRASP-Rust` implementation is integrated through binary, adapter, single-run, CLI and plan-runner paths. `GRASP-Rust` formal validation, `SA-Rust` ablation, `ILS-Rust` ablation, `GRASP-Rust` ablation, and full-portfolio validation remain pending.
- **Progress note 2026-05-02:** `GRASP-Rust` formal validation is completed on the controlled invariant panel. `SA-Rust` ablation, `ILS-Rust` ablation, `GRASP-Rust` ablation, and full-portfolio validation remain pending.
- **Progress note 2026-05-03:** Controlled SA/ILS/GRASP-Rust ablations completed on synthetic and mixed panels. `SA-Rust` shows throughput evidence with mixed cut-quality evidence; `ILS-Rust` and `GRASP-Rust` show favorable paired cut and throughput evidence on the mixed panel. Full benchmark, multilevel comparison, selector/CART evidence, and final prose integration remain pending.
### OI-029 — CART-validity gate must precede selector training claims
- **Type:** Methodology / selector validity / ASP governance
- **Severity:** High
- **Origin:** Expanded design for morphology, budget, and implementation maturity
- **Current status:** Open
- **Needed action:** After validated benchmark and budget-aware tables exist, compute and register selector-eligibility diagnostics before training or claiming CART: `SBS`, `VBS`, oracle gap or regret-equivalent improvement, winner-label distribution, target entropy or equivalent degeneracy measure, exception counts against the multilevel reference, temporal winner transitions, and the admissible selector target. The gate must decide whether the evidence supports fixed-budget CART, budget-aware CART, multilevel-exception classification, or no substantive CART claim.
- **Progress note 2026-05-05:** Before any exception-mining generator is implemented, generated graph instances must follow `decisions/13_Exception_Mining_Instance_Generation_Contract.md`. This preserves seeds, parameters, metrics, lifecycle state, hashes, rejection logs, and visualization inputs for future graph images and audit.
- **Progress note 2026-05-05:** Issue #95 protocol freeze started by adding `decisions/14_Exception_Mining_Campaign_Protocol.md` and `configs/exception_mining/EXP-MULTILEVEL-EXCEPTION-MINING-001/protocol_snapshot.*`. This freezes topology families, seeds, budgets, portfolio, labels, candidate-selection rules, holdout policy, and CART/ASP boundaries before generation.
### OI-030 — Two-week strong-scope viability gate must prevent schedule collapse
- **Type:** Project management / scope control / delivery risk
- **Severity:** High
- **Origin:** Four-week delivery window and proposed full Rust portfolio expansion
- **Current status:** Open
- **Needed action:** Run a two-week viability gate for the strong scope. If `SA-Rust`, `ILS-Rust`, and `GRASP-Rust` do not reach sufficient contract, implementation, adapter, smoke, artifact-validity, and conformance-readiness status by the gate, defer the full Rust portfolio and proceed with the defensible thesis scope. Record the gate result before writing broad Rust or CART claims.

### OI-031 — CART/Rust canon update must remain reconciled with current `main` IDs
- **Type:** Governance / canonical consistency
- **Severity:** Medium
- **Origin:** Issue #74 and strong-scope source update
- **Current status:** Resolved
- **Needed action:** Resolved in this reconciliation by preserving `D-022`, `D-023`, and `EXP-TS-RUST-ABLATION-001`; using `D-024` and `D-025` for the new decisions; and assigning the new operational issues to `OI-028`, `OI-029`, and `OI-030` instead of reusing `OI-021` through `OI-024`.

## Notes

- The pilot benchmark review completed successfully on 2026-04-27 (`EXPECTED_TOTAL=112`, `ACTUAL_TOTAL=112`, `SCHEMA_ERRORS=0`, `APPROVAL_CANDIDATE=1`), but that operational milestone does not by itself close the remaining writing, figure-clearance, or publication-surface issues.

### OI-032 — Quality-time surface must be implemented before budget-aware CART claims

- **Type:** Methodology / analysis pipeline / selector validity
- **Severity:** High
- **Origin:** Need to avoid interpreting the benchmark as a raw speed ranking and to preserve KaHIP as a quality-oriented baseline.
- **Current status:** Open
- **Needed action:** Implement selector-ready quality-by-wall-clock-time tables. For each `(instance, algorithm, budget)` slice, record availability, best validated cut by budget, elapsed time, censoring/invalidity flags, and aggregation across stochastic repetitions. Treat `METIS` and `KaHIP` as point-output step functions and metaheuristics as checkpoint-based anytime trajectories.
- **Closure condition:** Closed only after the table builder is committed, tested, and validated against real artifacts from the benchmark/exception-mining campaign.

### OI-033 — KaHIP/METIS interpretation must distinguish speed from quality

- **Type:** Results interpretation / threat to validity / writing governance
- **Severity:** Medium
- **Origin:** KaHIP is expected to trade more elapsed time for higher quality, while METIS is expected to be faster.
- **Current status:** Open
- **Needed action:** Ensure monograph prose and result tables do not treat KaHIP as worse merely because it is slower. Report where `METIS` is preferable under small budgets, where `KaHIP` becomes preferable because of lower cut, and where neither materially changes the recommendation.
- **Closure condition:** Closed after result-writing templates and result-to-text mappings include explicit allowed/forbidden wording.

### OI-034 — Budget-aware CART target must be selected only after diagnostics

- **Type:** ASP governance / CART validity
- **Severity:** High
- **Origin:** Budget-aware quality-time surface creates possible selector targets beyond the fixed-budget winner.
- **Current status:** Open
- **Needed action:** After validated quality-time tables exist, compute `SBS`, `VBS`, oracle gap or regret-equivalent improvement, winner-label distribution, target entropy or degeneracy diagnostic, exception counts against the multilevel reference, and budget-dependent winner transitions. Decide whether the admissible target is fixed-budget winner, budget-aware winner, multilevel-exception classifier, or no substantive CART claim.
- **Closure condition:** Closed only after the selector-eligibility gate report is committed and mapped.

### OI-035 — Dual-environment campaign metadata must be captured before benchmark execution

- **Type:** Reproducibility / environment governance
- **Severity:** High
- **Origin:** Decision to run the benchmark both under WSL/local notebook and under a dedicated machine/server.
- **Current status:** Open
- **Needed action:** Record complete hardware/software metadata for both environments, including CPU, RAM, OS, WSL version and memory limits when applicable, Docker/Poetry/Python versions, solver versions, storage context, thread-control variables, and exclusivity/shared-load policy.
- **Closure condition:** Closed only after environment metadata artifacts are committed or archived with the campaign and linked from the experiment ledger.

### OI-036 — WSL and server results must not be pooled as one homogeneous benchmark

- **Type:** Methodology / validity threat
- **Severity:** High
- **Origin:** Changing environment changes CPU, RAM, memory pressure, scheduler behavior, storage, operating system layer, and possibly solver/runtime behavior.
- **Current status:** Open
- **Needed action:** Ensure all analysis tables include an explicit environment identifier and distinguish WSL-local, dedicated-server, and common-intersection rows. Prevent scripts and prose from aggregating both environments without stratification.
- **Closure condition:** Closed only after analysis scripts and result-to-text mappings enforce environment stratification.

### OI-037 — Common WSL/server intersection must be defined before environmental sensitivity claims

- **Type:** Analysis protocol / robustness
- **Severity:** Medium
- **Origin:** Cross-environment comparison is valid only on matched instances, budgets, seeds/repetitions, portfolio members, and solver settings.
- **Current status:** Open
- **Needed action:** Define and freeze the common intersection between WSL and server campaigns. Use only this subset for environmental sensitivity analysis.
- **Closure condition:** Closed after the common-intersection manifest is committed and validated.

### OI-038 — CART must not learn environment identity instead of graph morphology

- **Type:** ASP governance / leakage risk
- **Severity:** High
- **Origin:** Dual-environment data may introduce an environment shortcut if machine identity is used naively as a predictive feature.
- **Current status:** Open
- **Needed action:** Decide whether CART is trained within one environment or explicitly as an environmental-sensitivity model. If environment is included as a feature, the modeling question must state that it is analyzing environment-conditioned recommendations.
- **Closure condition:** Closed only after the selector-eligibility gate specifies the allowed treatment of environment variables and verifies no leakage across common-intersection or train/test splits.

<!-- canonical-map:srv-noctua-linux-dedicated-campaign:open-issues -->

### OI-EXP-102 — Map validated srv-noctua confirmation evidence into claims
- **Status:** Partially resolved / still open.
- **Linked GitHub issue:** #102.
- **Current state:** The Linux dedicated `srv-noctua` execution of `EXP-MULTILEVEL-EXCEPTION-MINING-001` is complete and validated with `22400` valid results, `0` invalid results, `0` missing artifacts, and `0` schema errors.
- **Evidence bundle:** `audit_reports/multilevel_exception_mining/confirmation/srv_noctua_linux_dedicated_evidence_bundle_001`.
- **Open work:** Decide which environment-specific results enter the monograph, update result tables/figures if needed, preserve the single-environment boundary, and define the next execution gate for Windows 11 Docker portability or cross-environment sensitivity.
- **Blocked claims:** Do not claim cross-environment robustness, Windows portability, hardware-independent timing, or final selector validity from this server-only evidence.

<!-- HBF-FRONTIER-CONFIRMATION-001:OPEN_ISSUES:START -->
## Frontier confirmation evidence slice: srv_noctua_frontier_pilot_001

This block records a validated exception-mining confirmation slice. It is evidence-bearing only for the explicit environment slice `srv_noctua_frontier_pilot_001`; it is not, by itself, the final benchmark campaign and does not finalize monograph-level claims.

Source chain: `screening_short_001` → selection plan `750` → schema-compatible confirmation plan `756` → `confirmation_001` → validation report `758` → evidence map `759`.

Issue status update:

- Operationally resolved: frontier confirmation was executed and validated for `srv_noctua_frontier_pilot_001`.
- Still open analytically: decide how this evidence affects final benchmark scope, result narrative and CART/instance-selection discussion.
- Still open methodologically: decide whether additional confirmation or a broader final campaign is necessary before the monograph text uses these results as central evidence.

Observed transitions requiring interpretation:

- Transition classes: `{"downgraded_in_confirmation": 4, "negative_control_changed": 4, "same_tier": 1, "stable_negative_control": 9, "stable_strong": 62}`.
- Preliminary-to-confirmed matrix: `{"competitive_candidate": {"competitive_confirmed": 1}, "non_exception": {"competitive_confirmed": 4, "non_exception_confirmed": 9}, "strong_exception_candidate": {"near_tie_confirmed": 3, "non_exception_confirmed": 1, "strong_exception_confirmed": 62}}`.
<!-- HBF-FRONTIER-CONFIRMATION-001:OPEN_ISSUES:END -->
