# Exception Mining Campaign Protocol

## Scope

This protocol governs `EXP-MULTILEVEL-EXCEPTION-MINING-001`.

The campaign searches for graph topologies where the multilevel reference (`METIS`, `KaHIP`) becomes non-dominant, near-tied, or competitive against the full metaheuristic portfolio.

This protocol does not claim that such topologies exist. It defines a controlled way to search for them without turning the campaign into positive-only cherry-picking.

## Precondition

All generated graph instances must satisfy `decisions/13_Exception_Mining_Instance_Generation_Contract.md`.

No generated instance may enter screening, confirmation, holdout validation, CART/ASP labeling, figures, tables, or monograph claims unless its generation seed, parameters, metrics, hashes, lifecycle state, rejection/acceptance logs, and visualization inputs are recorded.

## Active solver portfolio

Evidence-bearing confirmation must use the full active portfolio:

- `METIS`
- `KaHIP`
- `SA`
- `ILS`
- `GRASP`
- `TS`
- `SA-Rust`
- `ILS-Rust`
- `GRASP-Rust`
- `TS-Rust`

Exploratory screening should also use the full portfolio whenever computationally feasible. If a reduced portfolio is used for a preliminary smoke pass, that pass must be explicitly marked as non-evidence-bearing and cannot support CART/ASP or monograph claims.

## Multilevel reference

For each instance and budget slice, the multilevel reference is:

```text
best_multilevel = min(cut_METIS, cut_KaHIP)
```

A metaheuristic result may only be compared against the multilevel reference when feasibility and cut values have been independently validated.

## Metaheuristic groups

The analysis must preserve the following groups:

```text
best_meta_python = min(SA, ILS, GRASP, TS)
best_meta_rust = min(SA-Rust, ILS-Rust, GRASP-Rust, TS-Rust)
best_meta_all = min(best_meta_python, best_meta_rust)
```

This separation is required because Rust variants provide implementation-maturity evidence and may change the wall-clock trajectory without constituting a new algorithmic paradigm.

## Campaign phases

### Phase A — protocol and generator readiness

Goal:

* freeze topology families, parameter grids, budgets, seeds, labels, and artifact locations;
* implement bundle validation;
* implement visualization-preview pipeline;
* implement topology generators and bundle writer.

Claim status:

* no performance claim;
* no CART/ASP claim.

### Phase B — exploratory candidate generation and screening

Goal:

* generate a broad, auditable candidate pool;
* screen all accepted generated instances;
* identify strong-exception, near-tie, competitive, availability-only, and non-exception candidates.

Claim status:

* exploratory only;
* screening wins are hypotheses for confirmation.

### Phase C — candidate freeze and full-portfolio confirmation

Goal:

* freeze candidate, rejection, and holdout manifests before confirmation;
* run full active portfolio;
* independently validate all solver artifacts;
* compute exception labels from collapsed validated results.

Claim status:

* eligible for internal evidence;
* monograph claims still require Results-to-Text mapping.

### Phase D — CART/ASP gate

Goal:

* decide whether confirmed evidence supports a nontrivial CART/ASP target;
* admissible targets are:

  * fixed-budget winner;
  * budget-aware winner;
  * multilevel-exception classifier;
  * competitive/near-tie detector;
  * no substantive CART claim.

Claim status:

* CART/ASP remains pending until this gate is completed.

## Topology families

The first exception-mining campaign must cover the following families unless a family is explicitly rejected for implementation or runtime reasons.

### F01 — modular noise / SBM-like graphs

Hypothesis:

* multilevel coarsening may become sensitive when community signal exists but is degraded by controlled inter-community noise.

Parameters:

* `n`: `[1000, 2000, 4000]`
* `communities`: `[4, 8, 16]`
* `target_avg_degree`: `[8, 16, 32]`
* `mixing_mu`: `[0.05, 0.15, 0.30, 0.45]`
* `community_size_mode`: `["balanced", "mildly_imbalanced"]`

### F02 — chain/ring of cliques or modules

Hypothesis:

* many locally dense regions linked by narrow boundaries may create multiple near-equivalent cuts and sensitivity to contraction choices.

Parameters:

* `module_count`: `[8, 16, 32]`
* `module_size`: `[20, 40, 80]`
* `topology`: `["chain", "ring"]`
* `inter_module_edges`: `[1, 2, 4]`
* `intra_module_density`: `[0.50, 0.80, 1.00]`

### F03 — barbell, lollipop, and bottleneck hybrids

Hypothesis:

* extreme bottlenecks and asymmetric dense/sparse regions may stress balance constraints and produce misleading early coarse structures.

Parameters:

* `left_core_size`: `[250, 500, 1000]`
* `right_core_size`: `[250, 500, 1000]`
* `bridge_length`: `[5, 25, 100]`
* `bridge_width`: `[1, 2, 4]`
* `core_density`: `[0.10, 0.30, 0.60]`

### F04 — hub-dominated / power-law graphs

Hypothesis:

* hubs may dominate contraction and refinement decisions, potentially making the best balanced cut sensitive to a small number of high-degree vertices.

Parameters:

* `n`: `[1000, 3000, 5000]`
* `attachment_m`: `[2, 4, 8]`
* `hub_noise_edges`: `[0, 0.05, 0.10]`
* `hub_bridge_mode`: `["none", "single_hub_bridge", "multi_hub_bridge"]`

### F05 — tree-plus-dense-core hybrids

Hypothesis:

* a dense core with tree-like appendages may create tension between cut minimization and balance feasibility.

Parameters:

* `n`: `[1000, 3000, 5000]`
* `core_fraction`: `[0.10, 0.25, 0.50]`
* `core_density`: `[0.10, 0.30, 0.60]`
* `tree_attachment_mode`: `["uniform", "hub_biased"]`

### F06 — road-like sparse synthetic graphs

Hypothesis:

* low-density geometric or grid-like graphs may differ from dense synthetic regimes and may expose balance/cut edge cases.

Parameters:

* `grid_shape`: `["square", "rectangular", "corridor"]`
* `n_approx`: `[1000, 3000, 5000]`
* `shortcut_rate`: `[0.00, 0.01, 0.05]`
* `perturbation_rate`: `[0.00, 0.05, 0.10]`

### F07 — dense weak-signal graphs

Hypothesis:

* when many cuts have similar costs, local search may become competitive because the multilevel reference has little structural signal to exploit.

Parameters:

* `n`: `[800, 1500, 2500]`
* `edge_density`: `[0.02, 0.05, 0.10]`
* `planted_signal`: `[0.00, 0.05, 0.10]`
* `noise_mode`: `["uniform", "block_weak"]`

### F08 — balance-hard planted partition graphs

Hypothesis:

* planted structures that conflict with the balance tolerance may create cases where straightforward community recovery is not equivalent to the best feasible balanced partition.

Parameters:

* `n`: `[1000, 2000, 4000]`
* `planted_blocks`: `[3, 5, 7]`
* `target_partition_k`: project default unless explicitly overridden
* `block_size_skew`: `[0.00, 0.25, 0.50]`
* `inter_block_noise`: `[0.05, 0.15, 0.30]`

## Parameter-grid policy

The full Cartesian product is not mandatory in the first exploratory wave.

The first wave should use a capped stratified design:

* at least 5 accepted instances per topology family if feasible;
* at least 3 generator seeds per family;
* at least one sparse, one medium, and one dense/large case where applicable;
* rejected attempts must remain logged.

If a family cannot produce valid instances, the rejection reason must be recorded in `rejection_log.md`.

## Generator seeds

Generator seeds must be independent from solver seeds.

Default generator seed pool:

```text
1001, 1002, 1003, 1004, 1005
```

Additional generator seeds may be added only if logged in the campaign manifest.

## Solver seeds

Exploratory screening:

```text
42
```

Confirmation:

```text
42, 43, 44, 45, 46
```

If deterministic solvers ignore seeds, this must be recorded rather than hidden.

## Budgets

The campaign preserves the existing hard cap:

```text
T* = 5000 ms
```

Exploratory screening must record at least:

```text
1000 ms, 5000 ms
```

Confirmation must use the budget-aware grid:

```text
100, 250, 500, 1000, 2000, 3000, 4000, 5000 ms
```

Fixed-budget claims use `T* = 5000 ms`.

Budget-aware claims use the full grid and must distinguish true superiority from availability-only cases.

## Exception labels

For a validated collapsed result:

```text
gap_meta_vs_multilevel = (best_meta_all - best_multilevel) / best_multilevel
```

Lower cut is better.

### `strong_exception_candidate`

```text
best_meta_all < best_multilevel
```

### `robust_strong_exception_candidate`

```text
median(best_meta_all) <= 0.99 * median(best_multilevel)
```

over confirmation seeds or generated variants.

### `near_tie_candidate`

```text
0 <= gap_meta_vs_multilevel <= 0.01
```

### `competitive_candidate`

```text
0.01 < gap_meta_vs_multilevel <= 0.05
```

### `availability_only_candidate`

A metaheuristic wins at budget `t` only because no multilevel result is available at that budget.

This label must not be interpreted as multilevel failure.

### `non_exception`

```text
gap_meta_vs_multilevel > 0.05
```

or multilevel remains clearly dominant under the relevant confirmed comparison.

## Candidate-selection rules

After exploratory screening, candidates advance to confirmation in this order:

1. all strong exception candidates;
2. all robust-looking strong exception candidates, if repeated exploratory evidence exists;
3. top near-tie candidates per family;
4. top competitive candidates per family;
5. negative controls from each family where multilevel remains dominant.

The selection must be written to `candidate_selection_log.md` before confirmation starts.

## Holdout policy

If enough generated instances exist, at least 20% of accepted instances per family should be reserved as holdout for CART/ASP or generalization checks.

Holdout membership must be assigned before using those instances for CART/ASP evaluation.

If the pool is too small for holdout, the report must state that CART/ASP is limited to exploratory diagnostics.

## Required artifact locations

Generated instance bundles:

```text
data/instances/exception_mining/EXP-MULTILEVEL-EXCEPTION-MINING-001/<family>/<instance_id>/
```

Campaign-level generation artifacts:

```text
audit_reports/multilevel_exception_mining/generated_pool/
```

Screening outputs:

```text
audit_reports/multilevel_exception_mining/screening/
```

Candidate freeze outputs:

```text
audit_reports/multilevel_exception_mining/candidate_freeze/
```

Confirmation outputs:

```text
audit_reports/multilevel_exception_mining/confirmation/
```

CART/ASP gate outputs:

```text
audit_reports/multilevel_exception_mining/cart_asp_gate/
```

## Required campaign artifacts

The campaign must produce:

* `protocol_snapshot.md`
* `protocol_snapshot.json`
* `generated_instances_manifest.csv`
* `generated_instances_manifest.json`
* `generation_attempts.jsonl`
* `rejection_log.md`
* `screening_results.csv`
* `screening_results.json`
* `screening_summary.json`
* `candidate_selection_log.md`
* `confirmation_manifest.csv`
* `confirmation_manifest.json`
* `holdout_manifest.csv`, if holdout is used
* `holdout_manifest.json`, if holdout is used
* `confirmation_summary.json`
* `cart_asp_gate_report.md`, if CART/ASP proceeds

## Anti-cherry-picking controls

The campaign must:

* record all generated candidates;
* record rejected candidates;
* record failed generator attempts;
* record solver failures;
* record invalid solver outputs;
* freeze candidate selection before confirmation;
* separate exploratory and confirmatory stages;
* report negative results;
* avoid modifying topology grids after observing winners unless the change is logged as a new exploratory wave.

## CART/ASP boundary

CART/ASP must not be trained or claimed from exploratory screening alone.

Before any CART/ASP claim, the project must compute:

* winner-label distribution;
* target entropy or equivalent degeneracy metric;
* `SBS`;
* `VBS`;
* oracle gap or regret-equivalent improvement;
* exception counts;
* multilevel-reference gaps;
* train/test or holdout split at instance level;
* claim boundary in `08_Results_to_Text_Map.md`.

If the target remains degenerate, CART must be rejected, deferred, or presented only as a diagnostic illustration.

## Auto-tuning boundary

Auto-tuning is not active in the default campaign.

It may only proceed through the separate contingency issue after the default portfolio mining result is known.

Tuned metaheuristics must not be mixed with default metaheuristic claims.
