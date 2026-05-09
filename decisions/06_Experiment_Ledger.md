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

### EXP-SA-RUST-FIDELITY-001 — SA-Rust fidelity contract, implementation, validation, and ablation
- **Status:** Validated and ablated
- **Date:** 2026-05-03
- **Question answered:** Can `SA-Rust` be treated as an implemented, integrated, formally validated, and controlled-ablation-ready fidelity target?
- **Code reference / branch / commit:** Branch `experiment/rust-metaheuristic-ablation`; harness commit `55e8b0c`; mixed-panel ablation under `audit_reports/rust_metaheuristic_ablation/598_ablation_mixed_panel`.
- **Input instances:** Mixed morphology panel: `synthetic/modnull_n3000_p50.json.gz`, `real/snap/ca_hepth_gcc.json.gz`, and `real/roadnet/roadnet_ca_bfs_10000_seed42.json.gz`; seeds `42..46`.
- **Algorithms compared:** Python `SA` vs `SA-Rust` only. No comparison against METIS, KaHIP, selector, CART, or other metaheuristics is claimed in this entry.
- **Budget protocol:** `budget_time_ms=5000`; frozen profile `initial_temp=1.0`, `cooling=0.997`, `min_temp=0.001`, `max_steps=100000`, `checkpoint_every_nfe=100`.
- **Primary metrics:** Schema compatibility, feasibility, independent cut recomputation, checkpoint consistency, final checkpoint consistency, elapsed time, NFE, NFE/s ratio, and paired cut delta.
- **Outputs generated:** `scripts/run_rust_metaheuristic_ablation.py`, `tests/test_rust_metaheuristic_ablation_script.py`, and reports under `audit_reports/rust_metaheuristic_ablation/597_ablation_synthetic_panel` and `audit_reports/rust_metaheuristic_ablation/598_ablation_mixed_panel`.
- **Main finding:** On the mixed morphology panel, `SA-Rust` produced schema-valid artifacts with zero invalid rows/pairs and achieved higher NFE/s than Python `SA` in the paired comparison. Quality evidence is mixed: `SA-Rust` was better in 7/15 pairs and Python `SA` was better in 8/15 pairs, with median `delta_cut_rust_minus_python=5`.
- **Limitations / caveats:** This supports implementation-maturity and throughput-readiness, not quality superiority. It does not establish trajectory equivalence, RNG equivalence, benchmark-wide superiority, selector eligibility, CART usefulness, or multilevel competitiveness.
- **Can this support prose in the monograph?** Yes, with bounded implementation-maturity wording only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes
### EXP-ILS-RUST-FIDELITY-001 — ILS-Rust fidelity contract, implementation, validation, and ablation
- **Status:** Validated and ablated
- **Date:** 2026-05-03
- **Question answered:** Can `ILS-Rust` be treated as an implemented, integrated, formally validated, and controlled-ablation-ready fidelity target?
- **Code reference / branch / commit:** Branch `experiment/rust-metaheuristic-ablation`; harness commit `55e8b0c`; mixed-panel ablation under `audit_reports/rust_metaheuristic_ablation/598_ablation_mixed_panel`.
- **Input instances:** Mixed morphology panel: `synthetic/modnull_n3000_p50.json.gz`, `real/snap/ca_hepth_gcc.json.gz`, and `real/roadnet/roadnet_ca_bfs_10000_seed42.json.gz`; seeds `42..46`.
- **Algorithms compared:** Python `ILS` vs `ILS-Rust` only. No comparison against METIS, KaHIP, selector, CART, or other metaheuristics is claimed in this entry.
- **Budget protocol:** `budget_time_ms=5000`; frozen profile `max_iters=100`, `perturb_moves=4`, `checkpoint_every_iter=1`.
- **Primary metrics:** Schema compatibility, feasibility, independent cut recomputation, checkpoint consistency, final checkpoint consistency, elapsed time, NFE, NFE/s ratio, and paired cut delta.
- **Outputs generated:** `scripts/run_rust_metaheuristic_ablation.py`, `tests/test_rust_metaheuristic_ablation_script.py`, and reports under `audit_reports/rust_metaheuristic_ablation/597_ablation_synthetic_panel` and `audit_reports/rust_metaheuristic_ablation/598_ablation_mixed_panel`.
- **Main finding:** On the mixed morphology panel, `ILS-Rust` produced schema-valid artifacts with zero invalid rows/pairs, was better than Python `ILS` in 14/15 paired runs, and had median `delta_cut_rust_minus_python=-240`. The median NFE/s ratio was approximately `36.97x` in favor of `ILS-Rust`.
- **Limitations / caveats:** This supports implementation-maturity evidence for the controlled panel. It does not establish trajectory equivalence, RNG equivalence, benchmark-wide superiority, selector eligibility, CART usefulness, or multilevel competitiveness.
- **Can this support prose in the monograph?** Yes, with bounded implementation-maturity wording only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes
### EXP-GRASP-RUST-FIDELITY-001 — GRASP-Rust fidelity contract, implementation, validation, and ablation
- **Status:** Validated and ablated
- **Date:** 2026-05-03
- **Question answered:** Can `GRASP-Rust` be treated as an implemented, integrated, formally validated, and controlled-ablation-ready fidelity target?
- **Code reference / branch / commit:** Branch `experiment/rust-metaheuristic-ablation`; harness commit `55e8b0c`; mixed-panel ablation under `audit_reports/rust_metaheuristic_ablation/598_ablation_mixed_panel`.
- **Input instances:** Mixed morphology panel: `synthetic/modnull_n3000_p50.json.gz`, `real/snap/ca_hepth_gcc.json.gz`, and `real/roadnet/roadnet_ca_bfs_10000_seed42.json.gz`; seeds `42..46`.
- **Algorithms compared:** Python `GRASP` vs `GRASP-Rust` only. No comparison against METIS, KaHIP, selector, CART, or other metaheuristics is claimed in this entry.
- **Budget protocol:** `budget_time_ms=5000`; frozen profile `alpha=0.30`, `max_iters=100`, `checkpoint_every_iter=1`.
- **Primary metrics:** Schema compatibility, feasibility, independent cut recomputation, checkpoint consistency, final checkpoint consistency, elapsed time, NFE, NFE/s ratio, and paired cut delta.
- **Outputs generated:** `scripts/run_rust_metaheuristic_ablation.py`, `tests/test_rust_metaheuristic_ablation_script.py`, and reports under `audit_reports/rust_metaheuristic_ablation/597_ablation_synthetic_panel` and `audit_reports/rust_metaheuristic_ablation/598_ablation_mixed_panel`.
- **Main finding:** On the mixed morphology panel, `GRASP-Rust` produced schema-valid artifacts with zero invalid rows/pairs, was better than Python `GRASP` in 14/15 paired runs, and had median `delta_cut_rust_minus_python=-328`. The median NFE/s ratio was approximately `36.46x` in favor of `GRASP-Rust`.
- **Limitations / caveats:** This supports implementation-maturity evidence for the controlled panel. It does not establish trajectory equivalence, RNG equivalence, benchmark-wide superiority, selector eligibility, CART usefulness, or multilevel competitiveness.
- **Can this support prose in the monograph?** Yes, with bounded implementation-maturity wording only.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes
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

### EXP-RUST-METAHEURISTIC-PORTFOLIO-001 — Rust metaheuristic portfolio maturity
- **Status:** Implementation-maturity evidence available; benchmark claims pending
- **Date:** 2026-05-03
- **Question answered:** Does the Rust metaheuristic portfolio have validated and ablated implementation-maturity evidence sufficient to proceed to benchmark-level use?
- **Code reference / branch / commit:** Branch `experiment/rust-metaheuristic-ablation`; harness commit `55e8b0c`.
- **Input instances:** Controlled mixed morphology ablation panel: `synthetic/modnull_n3000_p50.json.gz`, `real/snap/ca_hepth_gcc.json.gz`, and `real/roadnet/roadnet_ca_bfs_10000_seed42.json.gz`; seeds `42..46`.
- **Algorithms compared:** Python-vs-Rust comparisons within algorithm family only: `SA` vs `SA-Rust`, `ILS` vs `ILS-Rust`, and `GRASP` vs `GRASP-Rust`. `TS-Rust` had already been validated and ablated in its own prior entry.
- **Budget protocol:** `budget_time_ms=5000`; frozen D-012-compatible profiles for each family.
- **Primary metrics:** Validity of generated artifacts, feasibility, cut recomputation, checkpoint consistency, paired cut deltas, elapsed time, NFE, and NFE/s ratio.
- **Outputs generated:** `audit_reports/rust_metaheuristic_ablation/597_ablation_synthetic_panel` and `audit_reports/rust_metaheuristic_ablation/598_ablation_mixed_panel`.
- **Main finding:** The controlled mixed-panel ablation produced 90 runs and 45 Python-vs-Rust pairs with zero invalid rows and zero invalid pairs. `ILS-Rust` and `GRASP-Rust` showed favorable paired cut and throughput evidence on the mixed panel. `SA-Rust` showed favorable throughput evidence but mixed cut-quality evidence.
- **Limitations / caveats:** This is not a benchmark-wide performance result, not a multilevel comparison, not selector/CART evidence, and not proof of algorithmic or RNG equivalence. It supports proceeding with Rust metaheuristics as implementation-mature candidates under the frozen protocol.
- **Can this support prose in the monograph?** Yes, but only as bounded implementation-maturity evidence.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes

### EXP-QUALITY-TIME-SURFACE-001 — Quality-by-wall-clock-time benchmark surface

- **Status:** Planned
- **Date:** 2026-05-06
- **Question answered:** For each instance and finite budget, which algorithm provides the best validated partition quality available by that wall-clock time?
- **Code reference / branch / commit:** To be declared when selector-ready quality-time table builders are committed.
- **Input instances:** Validated benchmark panel and/or preregistered exception-mining pool after bundle validation and screening. Instance selection must be based on morphological coverage, not observed winners.
- **Algorithms compared:** Active validated portfolio at analysis time, including `METIS`, `KaHIP`, Python metaheuristics, and validated Rust metaheuristics if in scope.
- **Budget protocol:** Finite preregistered wall-clock budget grid including the official `T*`. No post hoc budget insertion to improve CART label distribution.
- **Point-output treatment:** `METIS` and `KaHIP` are represented as unavailable before measured `elapsed_ms` and available afterward with their final validated cut.
- **Anytime treatment:** Metaheuristics are reconstructed from validated checkpoints and final artifacts.
- **Environment constraints:** Analysis-only step over validated benchmark artifacts; no new solver execution is implied by this table-building experiment.
- **Primary metrics:** Best validated cut by `(instance, algorithm, budget)`, availability/censoring by budget, elapsed time to availability, `SBS`, `VBS`, oracle gap or regret-equivalent improvement, winner-label distribution, entropy/degeneracy diagnostics, exception counts against the multilevel reference, and budget-dependent winner transitions.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** This surface does not replace the fixed-budget `T*` report. NFE-based views remain diagnostic unless every compared participant exposes compatible counters.
- **Can this support prose in the monograph?** No until completed, validated, and mapped.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.

### EXP-KAHIP-METIS-QUALITY-TIME-INTERPRETATION-001 — Multilevel baseline quality-time interpretation

- **Status:** Planned
- **Date:** 2026-05-06
- **Question answered:** Under the validated benchmark artifacts, when does the quality-oriented multilevel baseline justify its additional elapsed time relative to the fast multilevel baseline?
- **Code reference / branch / commit:** To be declared when analysis tables/figures are committed.
- **Input instances:** Same as `EXP-QUALITY-TIME-SURFACE-001`.
- **Algorithms compared:** `METIS` and `KaHIP`, optionally contextualized against other active participants.
- **Budget protocol:** Same finite budget grid and point-output step-function treatment.
- **Primary metrics:** `elapsed_ms`, final validated cut, availability by budget, cut improvement of `KaHIP` over `METIS` when both are available, budgets where only `METIS` is available, and budgets where `KaHIP` becomes preferable.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** This analysis must not claim that KaHIP is globally better or worse. It only characterizes the time-quality trade-off under the audited environment.
- **Can this support prose in the monograph?** No until completed, validated, and mapped.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.

### EXP-DUAL-ENVIRONMENT-METADATA-001 — Execution-environment metadata capture

- **Status:** Planned
- **Date:** 2026-05-06
- **Question answered:** Are the WSL/local and dedicated/server environments sufficiently documented to support stratified benchmark interpretation?
- **Code reference / branch / commit:** To be declared when metadata capture scripts or manifests are committed.
- **Input instances:** N/A — metadata and environment audit only.
- **Algorithms compared:** N/A.
- **Environment protocol:** Capture WSL/local and dedicated/server hardware/software metadata before campaign execution.
- **Primary metrics:** CPU, RAM, OS, WSL version when applicable, Docker version, Poetry version, Python version, solver versions, thread-control variables, storage context, exclusivity/shared-load policy, and memory limits.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** Metadata capture does not prove performance equivalence; it only makes the environment auditable.
- **Can this support prose in the monograph?** No until completed and mapped.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.

### EXP-WSL-LOCAL-CAMPAIGN-001 — Restricted local WSL benchmark layer

- **Status:** Planned
- **Date:** 2026-05-06
- **Question answered:** Under the originally planned WSL/local notebook environment, what benchmark behavior is observed within the feasible resource envelope?
- **Code reference / branch / commit:** To be declared when campaign artifacts are produced.
- **Input instances:** Local feasible subset of the validated panel and/or exception-mining candidates.
- **Algorithms compared:** Active validated portfolio feasible under WSL constraints.
- **Budget protocol:** Declared local budget grid compatible with WSL memory and runtime constraints.
- **Primary metrics:** Validated cut, elapsed wall-clock time, availability by budget, checkpoint trajectories where available, invalid/censored runs, memory-related failures when captured.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** This layer is a restricted-resource baseline. It must not be pooled with the server campaign as one homogeneous benchmark.
- **Can this support prose in the monograph?** No until completed and mapped.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.

### EXP-DEDICATED-SERVER-CAMPAIGN-001 — Expanded dedicated-environment benchmark layer

- **Status:** Planned
- **Date:** 2026-05-06
- **Question answered:** Under a higher-capacity dedicated environment, what benchmark behavior is observed when the instance pool, budgets, repetitions, or exception-mining search are expanded?
- **Code reference / branch / commit:** To be declared when campaign artifacts are produced.
- **Input instances:** Expanded validated panel and/or generated exception-mining candidate pool.
- **Algorithms compared:** Active validated portfolio, including METIS, KaHIP, Python metaheuristics, and validated Rust metaheuristics if in scope.
- **Budget protocol:** Declared dedicated-environment budget grid, including the common intersection with WSL where applicable and any server-only expanded budgets.
- **Primary metrics:** Validated cut, elapsed wall-clock time, availability by budget, checkpoint trajectories where available, invalid/censored runs, quality-time winners, exception counts, and selector diagnostics.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** Server-only rows support dedicated-environment conclusions, not direct pooled claims with WSL.
- **Can this support prose in the monograph?** No until completed and mapped.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.

### EXP-ENVIRONMENT-SENSITIVITY-001 — WSL/server common-intersection sensitivity analysis

- **Status:** Planned
- **Date:** 2026-05-06
- **Question answered:** On the common intersection of instances, budgets, seeds/repetitions, portfolio members, and protocol settings, are algorithm rankings, quality-time winners, or CART-relevant labels stable across WSL and dedicated environments?
- **Code reference / branch / commit:** To be declared when analysis tables are committed.
- **Input instances:** Only the common intersection executed in both environments.
- **Algorithms compared:** Only portfolio members executed under equivalent settings in both environments.
- **Budget protocol:** Only budgets present in both environments.
- **Primary metrics:** Winner agreement, rank correlation where appropriate, cut differences, elapsed-time differences, availability/censoring changes, budget-transition stability, and selector-label stability.
- **Outputs generated:** N/A — planned entry only.
- **Main finding:** N/A — planned entry only.
- **Limitations / caveats:** This analysis evaluates environmental sensitivity. It does not prove machine-independent algorithm superiority.
- **Can this support prose in the monograph?** No until completed and mapped.
- **Mapped in `08_Results_to_Text_Map.md`:** Yes as prospective guardrail only.

<!-- canonical-map:srv-noctua-linux-dedicated-campaign:ledger -->

## EXP-MULTILEVEL-EXCEPTION-MINING-001 — srv-noctua Linux dedicated confirmation

- **Status:** Completed and validated for the explicit environment stratum `srv_noctua_linux_8gb`.
- **Date:** 2026-05-08.
- **Repository head:** `354447be68b5f7361afd245897d91bea7329020f`.
- **Environment:** `srv-noctua`, Linux dedicated campaign image `hbf-confirmation:srv-noctua-campaign-main`.
- **Execution scope:** 56 candidates, 10 algorithms, 8 budgets, 5 seeds, `22400` planned runs.
- **Validated counts:** `22400` raw results, `22400` valid results, `0` invalid results, `0` missing artifacts, `0` schema errors, `22400` row artifacts.
- **Raw status counts:** `{'ok': 18760, 'timeout': 3640}`.
- **Confirmed labels:** `{'competitive_confirmed': 8, 'near_tie_confirmed': 227, 'non_exception_confirmed': 11, 'strong_exception_confirmed': 202}`.
- **Digest fields:** SBS algorithm `ts_rust`; VBS mean median cut `80.77678571428571`.
- **Execution time:** 8782 seconds in the service state record.
- **Evidence:** `audit_reports/multilevel_exception_mining/confirmation/srv_noctua_linux_dedicated_evidence_bundle_001` and matching local tarball `srv_noctua_linux_dedicated_evidence_bundle_001.tar.gz`.
- **Validation gate:** `712_validate_srv_noctua_completed_campaign.txt` reported `GATE_RESULT=PASS`.
- **Issue record:** GitHub Issue #102 received the validated-evidence comment and remains open for canonical mapping and downstream claim decisions.
- **Claim boundary:** Validated evidence for `srv_noctua_linux_8gb` only. This entry does not authorize final monograph prose, hardware-independent timing generalization, or pooled cross-environment conclusions.

<!-- HBF-FRONTIER-CONFIRMATION-001:EXPERIMENT_LEDGER:START -->
## Frontier confirmation evidence slice: srv_noctua_frontier_pilot_001

This block records a validated exception-mining confirmation slice. It is evidence-bearing only for the explicit environment slice `srv_noctua_frontier_pilot_001`; it is not, by itself, the final benchmark campaign and does not finalize monograph-level claims.

Source chain: `screening_short_001` → selection plan `750` → schema-compatible confirmation plan `756` → `confirmation_001` → validation report `758` → evidence map `759`.

Execution ledger entry:

- Environment slice: `srv_noctua_frontier_pilot_001`.
- Screening artifact: `audit_reports/multilevel_exception_mining/frontier_pilot/srv_noctua_frontier_pilot_001/screening_short_001`.
- Selection plan: `750_frontier_confirmation_selection_plan.*`.
- Schema-compatible confirmation plan: `756_frontier_confirmation_run_plan_runner_schema.csv`.
- Confirmation output: `confirmation_001`.
- Validation report: `758_frontier_confirmation_validation_report.*`.
- Evidence map: `759_frontier_confirmation_evidence_map.*`.
- Service start log: `757_restart_frontier_confirmation_service_with_plan756.txt`.

Validated execution counts:

- Planned/raw/valid results: `4000` / `4000` / `4000`.
- Invalid results: `0`.
- Solver result artifacts: `4000` `result.json` files.
- Confirmation row artifacts: `4000` `confirmation_row.json` files.
- Error artifacts: `0` `error.txt` files.
- Raw status counts: `{"ok": 3170, "timeout": 830}`.
- Confirmation labels: `{"competitive_confirmed": 5, "near_tie_confirmed": 3, "non_exception_confirmed": 10, "strong_exception_confirmed": 62}`.
<!-- HBF-FRONTIER-CONFIRMATION-001:EXPERIMENT_LEDGER:END -->
