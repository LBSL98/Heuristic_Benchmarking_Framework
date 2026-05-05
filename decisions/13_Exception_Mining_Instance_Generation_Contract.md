# Exception Mining Instance Generation Contract

## Scope

This contract governs every graph instance generated for `EXP-MULTILEVEL-EXCEPTION-MINING-001`.

The purpose of the campaign is to search for graph topologies where the multilevel reference (`METIS`, `KaHIP`) becomes non-dominant, near-tied, or competitive against the metaheuristic portfolio. Because this search is adversarial and exploratory by design, every generated instance must be reproducible, auditable, and visualizable after the fact.

This contract applies before any generated instance may be used in screening, confirmation, holdout validation, CART training, ASP labeling, figures, tables, or monograph claims.

## Core rule

No generated instance may enter the exception-mining campaign unless the repository records enough information to:

1. regenerate the same graph from configuration and seed;
2. audit why the graph was generated;
3. audit whether the graph was accepted, rejected, screened, confirmed, or held out;
4. recompute structural metrics;
5. rerun all solvers under the frozen protocol;
6. generate graph visualizations later without relying on local script state;
7. verify that no positive-only cherry-picking occurred.

## Required artifact bundle per generated instance

Each generated instance must have an artifact bundle with the following files.

### Required graph artifacts

- `instance.json.gz`
  - Canonical graph instance in the project schema.
  - Must include `nodes`, `edges`, `schema_version`, `epsilon`, `instance_id`, `generator`, `seed`, `created_at`, and `instance_metrics`.
- `graph_edges.edgelist`
  - Plain edge-list representation for external inspection.
- `graph_metis.graph`
  - METIS-compatible graph representation.
- `sha256sums.txt`
  - Hashes for all generated files in the bundle.

### Required generation artifacts

- `generator_config.json`
  - Complete generation configuration.
  - Must include generator family, all graph parameters, random seed, target regime, target morphology, intended hypothesis, `k`, balance tolerance, code commit, generator version, and environment metadata.
- `generator_log.jsonl`
  - Append-only generation log.
  - Must include successful and failed attempts.
  - Every rejected candidate must record the rejection reason.
- `README.md`
  - Human-readable description of the generated instance.
  - Must state why this topology was generated and which multilevel-failure hypothesis it probes.

### Required metric artifacts

- `graph_metrics.json`
  - Must include at minimum:
    - number of vertices `|V|`;
    - number of edges `|E|`;
    - density;
    - average degree;
    - degree minimum, maximum, mean, standard deviation, and coefficient of variation;
    - connected component count;
    - largest component size;
    - clustering coefficient if computationally feasible;
    - modularity or community-score proxy if available;
    - assortativity if computationally feasible;
    - approximate diameter or sampled shortest-path statistic if computationally feasible;
    - generator-specific metrics.
- `manifest_row.json`
  - Single-instance manifest row used by downstream scripts.
- `manifest_row.csv`
  - CSV-compatible version of the same metadata.

### Required visualization artifacts

- `graph_preview_layout.json`
  - Node-position data for later visualization.
  - Must record layout algorithm, layout seed, layout parameters, and whether the layout was computed on the full graph or a sample.
- `graph_preview_sample.json`
  - Sampled subgraph used for preview when the full graph is too large to render clearly.
  - Must record sampling policy, sampled node ids, sampled edges, and sample seed.
- `visualization_metadata.json`
  - Must list available visual encodings, including:
    - degree;
    - generated community or block id, if available;
    - planted partition id, if available;
    - connected component id;
    - future solver partition labels, when available.

The campaign may generate images later from these artifacts. Image generation must not require hidden state from the original generator process.

## Required campaign-level artifacts

The campaign must also maintain:

- `generated_instances_manifest.csv`
  - One row per generated instance, including accepted and rejected instances.
- `generated_instances_manifest.json`
  - JSON version of the manifest.
- `generation_attempts.jsonl`
  - Append-only log of every generation attempt.
- `screening_results.csv`
  - Exploratory screening results for all screened instances.
- `candidate_selection_log.md`
  - Human-readable justification for advancing any instance to confirmation.
- `rejection_log.md`
  - Human-readable summary of rejected or failed candidates.
- `holdout_manifest.csv`
  - Frozen list of holdout instances, if holdout validation is used.
- `protocol_snapshot.md`
  - Snapshot of solver portfolio, budgets, seeds, thresholds, and exception definitions used by the campaign.

## Instance lifecycle states

Each generated instance must be assigned exactly one current lifecycle state:

- `generated`
- `schema_validated`
- `metric_validated`
- `screened`
- `selected_candidate`
- `confirmation_running`
- `confirmed_exception`
- `confirmed_non_exception`
- `holdout_reserved`
- `holdout_validated`
- `rejected_schema`
- `rejected_metrics`
- `rejected_duplicate`
- `rejected_size`
- `rejected_runtime`
- `rejected_other`

State transitions must be logged. An instance may not skip directly from `generated` to `confirmed_exception`.

## Exception-mining labels

The generation and screening layer may compute diagnostic labels, but these labels are not automatically monograph claims.

The allowed diagnostic labels are:

- `strong_exception_candidate`
  - A non-multilevel participant appears to beat the multilevel reference.
- `robust_strong_exception_candidate`
  - The candidate remains favorable under repeated seeds or generated variants.
- `near_tie_candidate`
  - Best non-multilevel result is within 1% of the multilevel reference.
- `competitive_candidate`
  - Best non-multilevel result is within 5% of the multilevel reference.
- `availability_only_candidate`
  - A non-multilevel participant wins only because the multilevel reference is unavailable at that budget.
- `non_exception`
  - The multilevel reference remains clearly dominant.

Only confirmation or holdout stages may support evidence-bearing claims.

## Required solver portfolio for evidence-bearing confirmation

Exploratory screening may use a reduced portfolio if explicitly marked as exploratory. Evidence-bearing confirmation must use the full active portfolio:

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

If any participant is unavailable, the run must state whether the slice is exploratory only or invalid for full-portfolio confirmation.

## Separation between exploratory search and confirmatory evidence

The campaign must separate:

1. exploratory generation and screening;
2. candidate confirmation;
3. holdout validation, if used;
4. CART/ASP target construction.

Exploratory wins are not evidence-bearing claims. They are hypotheses for confirmation.

## Anti-cherry-picking requirements

These anti-cherry-picking controls are mandatory for the exception-mining campaign.

The campaign must:

- record all generated candidates, not only successful exceptions;
- record all solver failures and invalid outputs;
- report negative results;
- preserve rejected instances and rejection reasons;
- freeze exception thresholds before confirmation;
- keep confirmation and holdout evaluation separate from exploratory selection;
- never change the panel after observing winners without recording the decision.

## CART/ASP boundary

Generated instances may be used to test whether a nontrivial CART/ASP target exists only after:

1. the instance lifecycle and solver results are auditable;
2. the target label is explicitly declared;
3. SBS/VBS, oracle gap, entropy, exception counts, and multilevel-reference gaps are recomputed;
4. train/test or holdout separation is frozen at the instance level;
5. the claim boundary is mapped in `08_Results_to_Text_Map.md`.

Until those conditions are satisfied, CART remains a pending diagnostic hypothesis, not a validated product claim.

## Visualization boundary

Graph visualizations produced from this campaign must state:

- whether the image shows the full graph or a sampled subgraph;
- the layout algorithm and seed;
- the node/edge sampling policy, if any;
- the coloring rule;
- whether solver partitions are shown;
- whether the image is illustrative or evidence-bearing.

Images must not be used as proof of performance. They may support interpretability, explanation of topology, and qualitative discussion.

## Minimum acceptance checklist

Before a generated instance enters screening:

- [ ] `instance.json.gz` exists.
- [ ] `generator_config.json` exists.
- [ ] `generator_log.jsonl` includes the generation attempt.
- [ ] `graph_metrics.json` exists.
- [ ] `graph_edges.edgelist` exists.
- [ ] `graph_metis.graph` exists.
- [ ] `graph_preview_layout.json` exists.
- [ ] `graph_preview_sample.json` exists.
- [ ] `visualization_metadata.json` exists.
- [ ] `sha256sums.txt` exists.
- [ ] the instance appears in `generated_instances_manifest.csv`.
- [ ] schema validation passed.
- [ ] connectivity/component policy was evaluated.
- [ ] lifecycle state was recorded.

Before a generated instance supports any result claim:

- [ ] all full-portfolio solver artifacts are present or missingness is explicitly justified;
- [ ] all solver outputs passed independent feasibility and cut validation;
- [ ] the multilevel reference is computed;
- [ ] exception labels are computed from collapsed validated results;
- [ ] candidate selection was logged before confirmation;
- [ ] confirmation or holdout status is recorded;
- [ ] claim boundary is explicit.
