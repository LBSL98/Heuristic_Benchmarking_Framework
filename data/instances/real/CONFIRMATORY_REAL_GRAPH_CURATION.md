# Confirmatory real-graph curation

This file defines the lightweight M1 curation surface for `CONFIRMATORY-PHASE-001`.

The companion CSV is:

- `data/instances/real/confirmatory_real_graph_candidates.csv`

## Status of this manifest

This manifest is a curation register, not an execution whitelist.

All candidates initially receive `candidate_confirmatory_pending`. A row with that status is documented but is not yet admitted to M3 smoke or M4 confirmatory execution.

A candidate may move to `candidate_ready_for_smoke` only after the following fields are completed and audited:

- `source_dataset_url`;
- `source_download_url`;
- `source_license`;
- `source_citation`;
- `raw_input_availability`;
- `transformation_steps`;
- `sha256`;
- `size_bytes`;
- `morphology_descriptors_status`;
- `holdout_group_family`;
- `holdout_group_source`;
- `holdout_group_base_graph`;
- `anti_winner_conditioned_selection_statement`.

## Current candidates

The initial rows document four existing real-graph assets already present in the repository:

- `roadnet_ca_bfs_10000_seed42`;
- `roadnet_ca_bfs_20000_seed43`;
- `ca_hepth_gcc`;
- `ca_astroph_gcc`.

These rows are deliberately conservative. Source URLs, download URLs, licenses, citations and raw-input availability are marked as `TBD_SOURCE_AUDIT_REQUIRED` until a dedicated source audit is performed.

## Anti-winner-conditioned selection rule

Real-graph candidates must not be selected, excluded, resized or promoted based on observed solver winners, exception labels, CART labels, cut quality or runtime outcomes.

Candidate inclusion must be justified by provenance, license, auditability, morphology coverage, size feasibility and holdout grouping.

## Raw data policy

Do not add new raw graph archives or large downloaded datasets in M1 unless a later issue explicitly defines that artifact as versioned source.

Prefer lightweight metadata manifests. Existing real graph assets may remain as prior tracked assets, but their confirmatory admissibility depends on completing this manifest.

## Holdout grouping policy

The minimum grouping fields for later selector or gatekeeper use are:

- `holdout_group_family`;
- `holdout_group_source`;
- `holdout_group_base_graph`.

For the current initial assets, both RoadNet-derived slices share base graph `roadNet-CA`; the SNAP candidates use `ca-HepTh` and `ca-AstroPh` as distinct base graphs. These groupings prevent a later selector split from treating derived slices from the same source graph as independent evidence without an explicit decision.

## Claim boundary

This M1 manifest does not add an empirical result, does not authorize monograph prose, and does not modify `decisions/08_Results_to_Text_Map.md`.

Issue `#49` remains the residual writing blocker. Issue `#127` remains open until curation metadata is complete enough to decide whether candidates are excluded or ready for M3/M4.
