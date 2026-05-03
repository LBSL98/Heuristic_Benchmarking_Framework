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
- **Status:** Completed — raw execution, post-campaign review, and fixed-budget collapse completed; selector and expanded analyses still pending
- **Date:** 2026-04-30
- **Question answered:** Under the frozen benchmark protocol and the completed R1/R2/R3 panel gate, what fixed-budget result is obtained by the canonical solver portfolio at `T*=5000 ms`, and is the resulting label surface sufficient for immediate selector claims?
- **Code reference / branch / commit:** Raw campaign and review at `fd3d475824cbb9070310dfda1322f7f0ef988177`; canonical post-review governance merged into `main` at `0f3a742f2f50bb60a5058e0fbdc7988c456aa06c`; collapse generated on branch `feat/main-benchmark-collapse-r1-r2-r3`.
- **Input instances:** 12-instance R1/R2/R3 panel from `data/instances/regime_panel_manifest.csv`: `R1=8`, `R2=2`, `R3=2`.
- **Algorithms compared:** Canonical thesis portfolio: `METIS`, `KaHIP`, `SA`, `ILS`, `GRASP`, and `TS`.
- **Plan reference:** `configs/plan_phase_1_baselines.yaml` and `configs/plan_phase_1_metaheuristics.yaml`.
- **Budget protocol:** Wall-clock fair(time) protocol with `budget_time_ms=5000`, `k=8`, `beta=0.03`; baselines single-run with seed `42`; stochastic participants repeated with seeds `[42, 43, 44, 45, 46]`.
- **Environment constraints:** Audited controlled WSL2 release-candidate environment under the current benchmark contract.
- **Primary metrics:** Raw artifact validity, fixed-budget collapsed median edge cut, median `elapsed_ms` tie-break, common-feasible coverage, winner distribution, tie cases, and overshoot caveat preservation.
- **Outputs generated:** Active raw outputs in `data/results_raw/main_baselines` and `data/results_raw/main_metaheuristics`; post-campaign review `375e_post_campaign_review_gate_final`; overshoot audit `376_timeout_overshoot_and_tiebreak_audit`; fixed-budget collapse artifacts `393_main_r1r2r3_fixed_budget_*`; structural validation `394_validate_collapse_outputs`; independent collapse audit `395_independent_collapse_audit`.
- **Main finding:** The reviewed raw campaign produced the expected 264 artifacts and the fixed-budget collapse produced 72 `(instance, algorithm, budget)` rows and 12 winner rows. Under the frozen collapse rule, `METIS` won 11 instances and `KaHIP` won 1 instance; no stochastic metaheuristic won at `T*=5000 ms`. There were no tie cases in the winner table.
- **Limitations / caveats:** This result is best interpreted as a fixed-budget multilevel-dominance diagnostic for the current 12-instance panel, not as positive evidence that a selector is already useful. Timeout overshoot occurred in 181 timeout-status metaheuristic runs and must remain reported as a validity caveat; the clipped-time sensitivity audit did not change winner identities. The small `R2=2` and `R3=2` slices support coverage and descriptive analysis, not strong per-regime inference. Selector, budget-aware, TS-Rust, and expanded-panel analyses remain pending.
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

### EXP-FIXED-BUDGET-EXCEPTION-DIAGNOSTICS-001 — Fixed-budget multilevel exception diagnostics
- **Status:** Completed
- **Date:** 2026-04-30
- **Question answered:** Under the validated R1/R2/R3 fixed-budget collapse at `T*=5000 ms`, are there strong, near-tie, or competitive exceptions to the multilevel reference, and is the winner-label surface sufficient for a positive fixed-budget selector claim?
- **Code reference / branch / commit:** Branch `feat/fixed-budget-exception-diagnostics` from `b4e4a983b593958dfcaf361cfd5a2cf23628d7dd`; diagnostics generated before commit.
- **Input instances:** Same 12-instance R1/R2/R3 panel used by `EXP-BENCH-MAIN-001`.
- **Algorithms compared:** Multilevel reference (`METIS`, `KaHIP`) versus stochastic metaheuristics (`SA`, `ILS`, `GRASP`, `TS`) under the collapsed fixed-budget table.
- **Budget protocol:** Official fixed budget `T*=5000 ms`; exception gaps computed from collapsed validated quality. Competitive-case overshoot was audited using checkpoints at or before `T*`.
- **Environment constraints:** Same audited WSL2 benchmark environment and artifact contract as the main campaign.
- **Primary metrics:** SBS, VBS, SBS-VBS gap, winner-label entropy, best multilevel versus best metaheuristic relative gap, strong exceptions, near ties, competitive cases, and overshoot sensitivity for competitive cases.
- **Outputs generated:** `421_fixed_budget_exception_diagnostics_*`, `422_validate_fixed_budget_exception_diagnostics`, `423_competitive_overshoot_audit_*`, and `424_fixed_budget_exception_diagnostics_corrected_*`.
- **Main finding:** `METIS` is the SBS and the winner labels are nearly degenerate (`METIS=11`, `KaHIP=1`). The SBS-VBS gap is only `0.001216%`, so multiclass fixed-budget winner selection has essentially no oracle gain. There are no strong non-multilevel exceptions, but there are 5 near ties within 1% and 7 competitive cases within 5%, all in R1 and all involving `ILS` as the best metaheuristic. The competitive-case overshoot audit showed that all 35 audited raw ILS runs were already competitive before `T*=5000 ms` according to checkpoints.
- **Limitations / caveats:** R1 contains the competitive cases; R2 and R3 contain only two instances each and show no near-tie or competitive cases. The competitive cases do not justify a strong winner-selector claim, but they support a limited exception/competitiveness-detector framing. Overshoot remains a caveat and is handled here through checkpoint-before-budget validation.
- **Can this support prose in the monograph?** Partial
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-BUDGET-AWARE-PROTOCOL-001 — Budget-aware temporal protocol preregistration
- **Status:** Completed
- **Date:** 2026-04-30
- **Question answered:** What temporal grid and labeling protocol must be used before constructing the budget-aware `y_i*(t)` table from the reviewed R1/R2/R3 main benchmark artifacts?
- **Code reference / branch / commit:** Branch `feat/budget-aware-exception-analysis` from `0dc8c34b37f8a0511718846b676edfd19e102967`; preregistration generated before commit.
- **Input instances:** Same 12-instance R1/R2/R3 panel used by `EXP-BENCH-MAIN-001`.
- **Algorithms compared:** No comparison performed in this protocol entry. The later budget-aware analysis will use `METIS`, `KaHIP`, `SA`, `ILS`, `GRASP`, and `TS`.
- **Budget protocol:** Frozen grid `[100, 250, 500, 1000, 2000, 3000, 4000, 5000]` ms, with hard cap `T*=5000 ms`.
- **Environment constraints:** Uses already reviewed raw artifacts from the controlled WSL2 main benchmark campaign; no rerun is authorized by this entry.
- **Primary metrics:** N/A for result claims; this entry freezes temporal construction rules.
- **Outputs generated:** Canonical preregistration in `D-022` and methodology updates.
- **Main finding:** N/A — protocol preregistration only.
- **Limitations / caveats:** This entry does not support temporal performance conclusions. It only authorizes later construction of `y_i*(t)` under the frozen grid and hard cap.
- **Can this support prose in the monograph?** Partial, for methodology/protocol prose only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-BUDGET-AWARE-YIT-001 — Budget-aware `y_i*(t)` table and temporal exception synthesis
- **Status:** Completed
- **Date:** 2026-04-30
- **Question answered:** Under the preregistered budget-aware grid and hard cap, does the recommended algorithm change with wall-clock budget, and do temporal exceptions justify a strong budget-aware selector claim?
- **Code reference / branch / commit:** Branch `feat/budget-aware-yit-table` from `fecbadd00c9e5c443962b85372067e617a586e7d`; table and synthesis generated before commit.
- **Input instances:** Same 12-instance R1/R2/R3 panel used by `EXP-BENCH-MAIN-001`.
- **Algorithms compared:** `METIS`, `KaHIP`, `SA`, `ILS`, `GRASP`, and `TS`.
- **Budget protocol:** Preregistered grid `[100, 250, 500, 1000, 2000, 3000, 4000, 5000]` ms, hard cap `T*=5000 ms`; metaheuristics use best checkpoint with `time_ms <= t`; point-output baselines are available only when `elapsed_ms <= t`.
- **Environment constraints:** Uses already reviewed main benchmark artifacts; no rerun.
- **Primary metrics:** `y_i*(t)` winner labels, availability by budget, winner transitions, strong exceptions, near ties, competitive cases, and budget-aware selector eligibility.
- **Outputs generated:** `442_budget_aware_yit_*`, `443_validate_budget_aware_yit_table`, and `444_budget_aware_temporal_exception_synthesis_*`.
- **Main finding:** The budget-aware table contains 96 winner labels. At `100 ms`, winners are `METIS=5`, `GRASP=4`, and `ILS=3`, but these non-multilevel wins occur when the multilevel reference is often unavailable. From `250 ms` through `3000 ms`, `METIS` wins all 12 labeled instances. At `4000 ms` and `5000 ms`, the table matches the fixed-budget winner distribution, with `METIS=11` and `KaHIP=1`. No strong non-multilevel exception was observed at any preregistered budget.
- **Limitations / caveats:** The `100 ms` diversity must be interpreted as early availability, not as proof that GRASP or ILS outperform available multilevel solvers. Near-tie and competitive cases persist where the multilevel reference is available, but they remain non-winning competitiveness diagnostics. Budget-aware CART is therefore limited to exploratory availability/competitiveness analysis and must not be framed as a strong selector result.
- **Can this support prose in the monograph?** Partial
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-TS-RUST-CONTRACT-001 — TS-Rust-fidelity contract preregistration
- **Status:** Completed
- **Date:** 2026-04-30
- **Question answered:** What constraints must govern the TS-Rust implementation before it can be used as an implementation-maturity ablation?
- **Code reference / branch / commit:** Branch `feat/ts-rust-fidelity` from `d24d2d70a502134aa35e40244901a8b6211a7b35`; contract preregistered before implementation.
- **Input instances:** N/A — protocol/contract entry only.
- **Algorithms compared:** N/A — implementation not yet executed.
- **Budget protocol:** Future TS-Rust runs must preserve the same wall-clock budget and checkpoint semantics used by the canonical TS benchmark.
- **Environment constraints:** Future Rust build and run environment must be recorded before performance claims.
- **Primary metrics:** N/A for results; this entry freezes the fidelity contract and claim boundaries.
- **Outputs generated:** `D-023`, methodology contract text, claim-governance rows, and resolved `OI-025`.
- **Main finding:** N/A — contract preregistration only.
- **Limitations / caveats:** This entry does not implement TS-Rust, validate it, or support performance claims. It only defines what future TS-Rust evidence may mean.
- **Can this support prose in the monograph?** Partial, for methodology/protocol prose only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-TS-RUST-VALIDATION-001 — TS-Rust-fidelity semantic/artifact validation
- **Status:** Completed
- **Date:** 2026-05-02
- **Question answered:** Does `ts_rust` satisfy basic semantic and artifact-level invariants before any implementation-maturity ablation?
- **Code reference / branch / commit:** Merged in PR #71; main at `69a602f3f851fe0835ec2abbebb352704bed1d59`.
- **Input instances:** Three controlled toy cases: `path12_k3_seed42`, `cycle16_k4_seed7`, and `two_cliques_bridge12_k2_seed123`.
- **Algorithms compared:** Canonical Python `ts` and `ts_rust`.
- **Budget protocol:** `1000 ms` wall-clock budget per controlled case.
- **Primary checks:** cutsize consistency against labels / `.part`, balance feasibility, checkpoint non-emptiness, checkpoint time monotonicity, best-so-far cut monotonicity, NFE monotonicity, and final checkpoint consistency with best cut.
- **Outputs generated:** `scripts/validate_ts_rust_fidelity.py`, `tests/test_ts_rust_validation_script.py`; local validation reports under `audit_reports/ts_rust_fidelity/`.
- **Main finding:** All three controlled cases passed the invariant checks. The observed best cuts matched between Python TS and TS-Rust on the controlled cases: `path12_k3_seed42` = 2/2, `cycle16_k4_seed7` = 4/4, and `two_cliques_bridge12_k2_seed123` = 1/1.
- **Limitations / caveats:** This validation does not prove trajectory equivalence, RNG equivalence, full algorithmic equivalence on all instances, or performance superiority. It only authorizes proceeding to a controlled implementation-maturity ablation.
- **Can this support prose in the monograph?** Yes, but only as validation/protocol prose. It cannot support claims about speed, superiority, or general metaheuristic competitiveness.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-TS-RUST-ABLATION-001 — TS-Python versus TS-Rust implementation-maturity ablation
- **Status:** Completed
- **Date:** 2026-05-02
- **Question answered:** Does the Rust implementation of canonical Tabu Search exhibit implementation-maturity advantages over the Python implementation under the frozen TS-Rust-fidelity contract?
- **Code reference / branch / commit:** `feat/ts-rust-ablation`, commit `5bb12acd33f08b7684749f5898840d63ac285607`; final merge to `main` through PR `#73` at merge commit `42cee484bd44f0c53d944f556e45486ed6bccb9c`.
- **Input instances:** `synthetic_modnull_n3000_p50`, `snap_ca_hepth_gcc`, and `roadnet_ca_bfs_10000_seed42`.
- **Algorithms compared:** Python `TS` and `TS-Rust-fidelity`. This experiment did not compare a multilevel TS, a memetic TS, or a retuned TS variant.
- **Budget protocol:** Nominal `5000 ms` wall-clock budget, seeds `[42, 43, 44, 45, 46]`, same validation surface, paired comparison by instance and seed.
- **Environment constraints:** Controlled benchmark environment with Rust binary execution recorded by the ablation harness; artifact validity audited after execution.
- **Primary metrics:** Final validated edge cut, NFE/s, elapsed time, overshoot relative to nominal budget, trajectory/checkpoint integrity, paired Rust-versus-Python comparison, and TTT on preregistered references when available.
- **Outputs generated:** `audit_reports/ts_rust_fidelity/509_ts_rust_ablation/report.json`, raw artifacts, `runs.csv`, `paired_summary.csv`, `trajectory_samples.csv`, `510_audit_ts_rust_ablation_artifact_validity.txt`, and `511_ts_rust_ablation_audited_summary.json`.
- **Main finding:** The ablation produced `15/15` valid pairs. `TS-Rust-fidelity` obtained lower final validated cuts than Python `TS` in `15/15` pairs. The median Rust/Python NFE/s ratio was `38.316x`. Per-case median delta cuts were `-5275` for `roadnet_ca_bfs_10000_seed42`, `-11202` for `snap_ca_hepth_gcc`, and `-9952` for `synthetic_modnull_n3000_p50`.
- **Limitations / caveats:** The result is TS-specific. It does not prove trajectory equivalence, RNG equivalence, full algorithmic equivalence, or generalization to `SA`, `ILS`, `GRASP`, or all metaheuristics. Python `TS` exceeded the nominal `5000 ms` budget in all runs, with median overshoot `58 ms` and maximum overshoot `1582 ms`; this favors Python in final-cut comparison and must be disclosed.
- **Can this support prose in the monograph?** Partial. It supports implementation-maturity and validity-of-construct prose for TS only, not general superiority claims.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-SA-RUST-FIDELITY-001 — SA-Rust fidelity contract, implementation, and validation
- **Status:** Validated; ablation pending
- **Date:** 2026-05-02
- **Question answered:** Can `SA-Rust` be implemented, integrated and formally validated as a fidelity target following the frozen SA-Rust contract?
- **Code reference / branch / commit:** Branch `test/sa-rust-fidelity-validation`; implementation merged in PR #81; validation commit `cb7aa76` before PR merge.
- **Input instances:** Controlled deterministic validation cases: `path12_k3_seed42`, `cycle16_k4_seed7`, and `two_cliques_bridge12_k2_seed123`.
- **Algorithms compared:** Python `SA` and `SA-Rust` are compared only at the level of semantic and artifact invariants. No trajectory-equivalence, RNG-equivalence, performance, quality, or ablation comparison is performed in this entry.
- **Budget protocol:** Validation uses bounded toy-case settings for speed and reproducibility. Evidence-bearing ablation runs must still use the frozen `D-012` profile `sa_e_maxsteps_100000`: `initial_temp=1.0`, `cooling=0.997`, `min_temp=0.001`, `max_steps=100000`, `checkpoint_every_nfe=100`.
- **Primary metrics:** Independent cut recomputation from labels, beta-feasibility, schema compatibility, `.part` path existence, checkpoint non-emptiness, checkpoint time monotonicity, best-so-far cut monotonicity, NFE monotonicity, final checkpoint best-cut consistency, and final checkpoint NFE consistency against the raw `SA-Rust` JSON payload.
- **Outputs generated:** `scripts/validate_sa_rust_fidelity.py`, `tests/test_sa_rust_validation_script.py`, and validation reports under `audit_reports/sa_rust_validation/`.
- **Main finding:** `SA-Rust` passed formal artifact/semantic invariant validation on the controlled validation panel. It is now an implemented, integrated and validated fidelity target, but it has not yet been used in an implementation-maturity ablation.
- **Limitations / caveats:** This entry does not establish trajectory equivalence, RNG equivalence, performance superiority, quality superiority, selector eligibility, CART usefulness, or full Rust portfolio maturity.
- **Can this support prose in the monograph?** Partial, for methodology/validation-readiness prose only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes
### EXP-ILS-RUST-FIDELITY-001 — ILS-Rust fidelity contract, implementation, and validation
- **Status:** Validated; ablation pending
- **Date:** 2026-05-02
- **Question answered:** Can `ILS-Rust` be implemented, integrated and formally validated as a fidelity target following the frozen ILS-Rust contract?
- **Code reference / branch / commit:** Branch `test/ils-rust-fidelity-validation`; implementation merged in PR #85; validation commit `ff05bd1` before PR merge.
- **Input instances:** Controlled deterministic validation cases: `path12_k3_seed42`, `cycle16_k4_seed7`, and `two_cliques_bridge12_k2_seed123`.
- **Algorithms compared:** Python `ILS` and `ILS-Rust` are compared only at the level of semantic and artifact invariants. No trajectory-equivalence, RNG-equivalence, performance, quality, or ablation comparison is performed in this entry.
- **Budget protocol:** Validation uses bounded toy-case settings for speed and reproducibility. Evidence-bearing ablation runs must still use the frozen `D-012` profile for ILS-Rust: `max_iters=100`, `perturb_moves=4`, `checkpoint_every_iter=1`.
- **Primary metrics:** Independent cut recomputation from labels, beta-feasibility, schema compatibility, `.part` path existence, checkpoint non-emptiness, checkpoint time monotonicity, best-so-far cut monotonicity, NFE monotonicity, final checkpoint best-cut consistency, and final checkpoint NFE consistency against the raw `ILS-Rust` JSON payload.
- **Outputs generated:** `scripts/validate_ils_rust_fidelity.py`, `tests/test_ils_rust_validation_script.py`, and validation reports under `audit_reports/ils_rust_validation/`.
- **Main finding:** `ILS-Rust` passed formal artifact/semantic invariant validation on the controlled validation panel. It is now an implemented, integrated and validated fidelity target, but it has not yet been used in an implementation-maturity ablation.
- **Limitations / caveats:** This entry does not establish trajectory equivalence, RNG equivalence, performance superiority, quality superiority, selector eligibility, CART usefulness, or full Rust portfolio maturity.
- **Can this support prose in the monograph?** Partial, for methodology/validation-readiness prose only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes
### EXP-GRASP-RUST-FIDELITY-001 — GRASP-Rust fidelity contract, implementation, and validation
- **Status:** Implementation integrated; formal validation pending
- **Date:** 2026-05-02
- **Question answered:** Can `GRASP-Rust` be implemented and integrated as a runnable fidelity target following the frozen GRASP-Rust contract?
- **Code reference / branch / commit:** Branch `feat/grasp-rust-fidelity`; commit `4134cda` before PR merge.
- **Input instances:** Deterministic toy instances in focused unit, runner, CLI, and plan-runner tests.
- **Algorithms compared:** Python `GRASP` and `GRASP-Rust` are not yet compared for performance or quality in this entry. This entry covers implementation/integration readiness only.
- **Budget protocol:** Smoke tests use small budgets or small iteration caps for speed. Evidence-bearing runs must use the frozen `D-012` profile for GRASP-Rust: `alpha=0.30`, `max_iters=100`, `checkpoint_every_iter=1`.
- **Primary metrics:** Build success, unit-test pass, runner artifact validity, CLI execution, declarative plan execution, schema compatibility, final checkpoint consistency, `.part` output, and cut recomputation from labels in focused tests.
- **Outputs generated:** `rust/grasp_rust_fidelity/`, `src/hpc_framework/grasp_rust_adapter.py`, `tests/test_grasp_rust_adapter_paths.py`, `tests/test_runner_grasp_rust.py`, `tests/test_cli_single_run_grasp_rust.py`, and `tests/test_plan_runner_grasp_rust.py`.
- **Main finding:** `GRASP-Rust` is now a runnable integrated fidelity target through binary, adapter, `single-run`, CLI, and plan-runner paths. The integration preserves the declared artifact surface and passes focused smoke/schema tests.
- **Limitations / caveats:** This entry is not formal validation and not an ablation. It does not establish trajectory equivalence, RNG equivalence, performance superiority, quality superiority, selector eligibility, CART usefulness, or full Rust portfolio maturity.
- **Can this support prose in the monograph?** Partial, for methodology/implementation-readiness prose only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes
### EXP-RUST-METAHEURISTIC-PORTFOLIO-001 — Full Rust metaheuristic implementation-maturity layer
- **Status:** Planned
- **Date:** 2026-05-02
- **Question answered:** Does extending faithful Rust reimplementations from TS to the full metaheuristic portfolio change throughput, anytime curves, winner diversity, exception counts, or selector eligibility relative to the Python metaheuristic portfolio and multilevel baselines?
- **Code reference / branch / commit:** To be declared separately for `SA-Rust`, `ILS-Rust`, and `GRASP-Rust`; `TS-Rust` already has completed evidence under `EXP-TS-RUST-ABLATION-001`.
- **Input instances:** To be derived from the validated `R1`/`R2`/`R3` panel or a preregistered stratified subset. Instance selection must be based on morphological coverage, not observed winners.
- **Algorithms compared:** `SA-Python`, `TS-Python`, `ILS-Python`, `GRASP-Python`; `SA-Rust`, `TS-Rust`, `ILS-Rust`, `GRASP-Rust`; and, when used for contextual comparison, `METIS` and `KaHIP`.
- **Budget protocol:** Same wall-clock semantics, finite budget grid when used in the budget-aware surface, same validation contract, same repeated-run policy for stochastic participants, and no per-instance retuning.
- **Primary metrics:** NFE/s, final validated edge cut by budget, quality by NFE, quality by wall-clock, TTT against preregistered references, exception counts relative to the multilevel reference, and selector-eligibility diagnostics.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** This layer is not a claim that the Python benchmark was invalid or unfair. It estimates implementation-maturity effects. Broader metaheuristic claims require all relevant Rust implementations to be validated and mapped.
- **Can this support prose in the monograph?** No until completed, validated, and mapped.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.

### EXP-CART-VALIDITY-GATE-001 — Selector-eligibility diagnostics under expanded evidence
- **Status:** Planned
- **Date:** 2026-05-02
- **Question answered:** Does the validated evidence support a nontrivial selector target for CART, and if so, which target is admissible?
- **Code reference / branch / commit:** To be declared before result claim.
- **Input instances:** Validated `R1`/`R2`/`R3` panel and any preregistered expanded panel admitted before analysis.
- **Algorithms compared:** The active validated portfolio at gate time.
- **Budget protocol:** Fixed-budget and/or budget-aware surfaces already frozen in the methodology.
- **Primary metrics:** `SBS`, `VBS`, oracle gap, winner-label distribution, entropy or equivalent degeneracy diagnostic, temporal winner transitions, and exception counts against the multilevel reference.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** CART is not a product claim until this gate identifies a nontrivial and valid supervised target.
- **Can this support prose in the monograph?** No while planned, except as governance.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.

### EXP-STRONG-SCOPE-VIABILITY-GATE-001 — Two-week strong-scope viability gate
- **Status:** Planned
- **Date:** 2026-05-02
- **Question answered:** Should the full Rust metaheuristic portfolio remain inside the monograph scope after the two-week implementation and validation sprint?
- **Code reference / branch / commit:** To be declared at gate review.
- **Input instances:** N/A — project-management and evidence-readiness gate.
- **Algorithms compared:** N/A — evaluates readiness of `SA-Rust`, `ILS-Rust`, and `GRASP-Rust`.
- **Budget protocol:** N/A for direct performance claims.
- **Primary metrics:** Contract completion, compilation/integration status, runner/adapter readiness, smoke execution, artifact validity, conformance tests, and remaining schedule risk.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** This gate supports scope control, not empirical algorithm claims.
- **Can this support prose in the monograph?** No, except as project governance if needed.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as governance only.

### EXP-RUST-PORTFOLIO-CONTRACTS-001 — SA/ILS/GRASP Rust fidelity contracts
- **Status:** Completed
- **Date:** 2026-05-02
- **Question answered:** What fidelity contracts must govern `SA-Rust`, `ILS-Rust`, and `GRASP-Rust` before implementation?
- **Code reference / branch / commit:** Branch `governance/rust-portfolio-fidelity-contracts`; commit to be recorded after merge.
- **Input instances:** N/A — contract/governance entry only.
- **Algorithms compared:** N/A — no solver comparison is performed in this entry.
- **Budget protocol:** Evidence-bearing future Rust runs must preserve the benchmark profiles frozen in `D-012`: `sa_e_maxsteps_100000`, `ils_b`, and `grasp_b`, with the same wall-clock budget semantics and artifact contract.
- **Environment constraints:** Future implementation entries must record Rust compiler version, build flags, binary paths, and runtime metadata before any performance claim.
- **Primary metrics:** N/A for performance. The contract freezes reference implementation, frozen profile, operator semantics, RNG/trajectory caveats, checkpoint/NFE contract, artifact mapping, forbidden changes, validation-panel requirements, and conformance-test requirements.
- **Outputs generated:** `decisions/12_Rust_Portfolio_Fidelity_Contracts.md`.
- **Main finding:** The repository now has explicit pre-implementation fidelity contracts for `SA-Rust`, `ILS-Rust`, and `GRASP-Rust`. This authorizes implementation work under issue #76 but does not authorize performance, selector, or full-portfolio result claims.
- **Limitations / caveats:** These contracts do not require Python RNG stream equivalence and do not establish trajectory equivalence. Validation and ablation remain separate future steps.
- **Can this support prose in the monograph?** Partial, for methodology/governance prose only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-RUST-FOUNDATION-001 — Shared Rust GPP fidelity foundation
- **Status:** Completed
- **Date:** 2026-05-02
- **Question answered:** Is there a tested shared Rust foundation for future `SA-Rust`, `ILS-Rust`, and `GRASP-Rust` fidelity implementations?
- **Code reference / branch / commit:** Branch `feat/rust-metaheuristic-foundation`; commit to be recorded after merge.
- **Input instances:** Deterministic in-crate toy graphs only.
- **Algorithms compared:** N/A — this is infrastructure, not an algorithm implementation or benchmark comparison.
- **Budget protocol:** N/A for performance claims. Future algorithms must still use the contracts in `decisions/12_Rust_Portfolio_Fidelity_Contracts.md`.
- **Environment constraints:** Rust crate `rust/gpp_fidelity_core`; no dependency on changing the already validated `TS-Rust` binary.
- **Primary metrics:** Unit-test coverage of METIS parsing, cut recomputation, boundary recomputation, balance feasibility, delta-cut evaluation, move application, fallback boundary vertex selection, deterministic initial-state construction, and `.part` writing.
- **Outputs generated:** `rust/gpp_fidelity_core/`.
- **Main finding:** A shared Rust infrastructure crate exists and passes its unit tests. It does not expose `SA-Rust`, `ILS-Rust`, or `GRASP-Rust` as runnable algorithms.
- **Limitations / caveats:** This entry supports implementation readiness only. It does not support performance, quality, selector, or full-portfolio claims.
- **Can this support prose in the monograph?** Usually no, except as repository engineering/governance detail if needed.
- **Mapped in `08_Results_to_Text_Map.md`:** No result claim mapped.
