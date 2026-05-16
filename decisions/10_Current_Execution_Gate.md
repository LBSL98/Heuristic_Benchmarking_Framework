# 10_Current_Execution_Gate.md

<!-- canonical-map:confirmatory-phase-001:current-gate -->

## Current execution gate — CONFIRMATORY-PHASE-001 M0

The active repository gate is now `CONFIRMATORY-PHASE-001` milestone `#10`, starting with issue `#126` (`M0: canonical update and preregistered thesis reframing`).

This gate is confirmatory, not exploratory repair. Before any new execution in `M1`–`M8`, the repository must record the confirmatory framing in the canonical layer.

The previous `srv-noctua` Linux dedicated campaign for `EXP-MULTILEVEL-EXCEPTION-MINING-001` remains accepted as completed environment-specific evidence for the explicit stratum `srv_noctua_linux_8gb`. Its validated facts remain:

- Planned runs: `22400`.
- Raw results: `22400`.
- Valid results: `22400`.
- Invalid results: `0`.
- Missing artifacts: `0`.
- Schema errors: `0`.
- Raw status counts: `{'ok': 18760, 'timeout': 3640}`.
- Confirmation labels: `{'competitive_confirmed': 8, 'near_tie_confirmed': 227, 'non_exception_confirmed': 11, 'strong_exception_confirmed': 202}`.
- Evidence bundle: `audit_reports/multilevel_exception_mining/confirmation/srv_noctua_linux_dedicated_evidence_bundle_001`.

That evidence does not by itself close the new confirmatory phase. It becomes prior bounded evidence that informs, but does not replace, the real-graph-centered confirmatory plan.

## Confirmatory framing now active

The confirmatory phase is governed by the `tcc_confirmatory_plan_package.zip` summary recorded in the audit layer and materialized as GitHub milestone `#10`.

The working interpretation is:

1. previous benchmark and exception-mining outputs are exploratory or bounded environment-specific confirmation unless explicitly mapped otherwise;
2. real graphs are central to external validity;
3. synthetic instances remain useful as controlled morphology coverage, not as the sole basis for final claims;
4. `METIS` and `KaHIP` remain the multilevel reference/incumbent solvers, not strawman baselines;
5. CART is treated as an interpretable gatekeeper or exception detector, not as a universal multiclass solver selector;
6. fixed-target, TTT, ECDF, attainment, near-tie, exception and SBS/VBS gap diagnostics are required before substantive selector claims;
7. holdout boundaries must respect family, source and base-graph separation;
8. old CART models may be tested on holdout only without opportunistic retraining;
9. any new CART trained after inspecting holdout behavior is exploratory unless a new preregistered split is frozen first.

## Active issue sequence

The confirmatory milestone currently contains:

- `#126` — `M0`: canonical update and preregistered thesis reframing;
- `#127` — `M1`: curate real-graph confirmatory candidates;
- `#128` — `M2`: define confirmatory synthetic controls;
- `#129` — `M3`: smoke `srv-noctua` environment and active participants;
- `#130` — `M4`: run preregistered `srv-noctua` confirmatory campaign;
- `#131` — `M5`: compute fixed-target, TTT, ECDF, attainment and SBS/VBS diagnostics;
- `#132` — `M6`: evaluate CART gatekeeper admissibility;
- `#133` — `M7`: analyze Rust/Python implementation-maturity ablation;
- `#134` — `M8`: update claim ledger, result map and monograph-safe conclusion boundary.

## Active boundary

The only executable work allowed immediately after this gate update is M0 canonical alignment and then M1 planning.

Do not edit monograph prose now. Issue `#49` remains the residual writing blocker until the actual monograph source or final text surface is audited.

Do not version `audit_reports/`, local evidence bundles, extracted package contents or transient planning packets. They may be referenced as local audit evidence, but not committed unless a later issue explicitly defines a lightweight metadata artifact as versioned source.

## Do not proceed if

- a new empirical result is claimed before it appears in `06_Experiment_Ledger.md`;
- a result is used for prose before it is mapped in `08_Results_to_Text_Map.md`;
- final monograph wording is edited before `#49` is resolved or explicitly scoped;
- real-graph candidates are selected based on observed solver winners;
- synthetic controls are used as the sole basis for external-validity claims;
- `METIS` or `KaHIP` are described as weak strawman baselines;
- CART is described as validated merely because a tree can be trained;
- `srv-noctua`, WSL and Windows outputs are pooled as homogeneous timing evidence;
- `audit_reports/` is staged or committed.
