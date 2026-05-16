# License-clear replacement curation

This file defines the replacement-candidate shortlist after the SNAP classic exclusion decision.

The companion CSV is:

- `data/instances/real/license_clear_replacement_candidates.csv`

## Status

This shortlist is not an execution whitelist.

The original SNAP-derived M1 candidates were excluded from the public confirmatory real-graph sample because no explicit dataset-license basis was accepted for `roadNet-CA`, `ca-HepTh` or `ca-AstroPh`.

The replacement path must therefore use license-clear sources. No candidate family in this file is admitted to M3 smoke or M4 confirmatory execution yet.

## Environment policy

Real-graph replacement curation follows the `srv-noctua`-first policy recorded in:

- `data/instances/real/REAL_GRAPH_CURATION_ENVIRONMENT_POLICY.md`

Documentation-only changes may be prepared locally, but any step that downloads data, computes hashes, derives graphs, validates non-trivial graph structure, runs M3/M4 or trains CART should run on `srv-noctua` by default.

Future data-producing scripts should include an explicit environment guard requiring `srv-noctua`, unless an exceptional override is documented in the audit log.

## Current M2 primary targets

The current primary targets for the next M2 license/admissibility pass are:

1. `tigerline_roads_state_or_county`;
2. `arxiv_metadata_hepth_astroph_reconstruction`;
3. `ogbn_arxiv_undirected_projection`.

This priority follows the M2 probe result that kept every family non-admitted while identifying these three as the primary next targets for manual license snapshot and candidate-level review.

## Admission rule

A replacement graph may be promoted only after a later issue records:

- official source URL;
- exact license or terms URL;
- license scope, distinguishing data, metadata, software and documentation;
- attribution and citation obligations;
- redistribution and modification obligations;
- raw artifact hash, if downloaded locally;
- derived artifact hash, if a derived graph is produced;
- transformation steps;
- graph semantics before and after conversion;
- holdout grouping fields;
- risk level;
- reviewer and review date.

## Priority order

### High priority

1. TIGER/Line road graphs by state, county or metropolitan region.
2. OSM/Geofabrik road graphs with explicit ODbL compliance.
3. arXiv metadata reconstructions for HEP-TH and ASTRO-PH-like scientific graphs.
4. OGB datasets with explicit compatible dataset licenses, especially `ogbn-arxiv` after documented symmetrization.

### Medium priority

1. `ogbn-proteins`, if weighted or biological graph diversity is methodologically useful.
2. SuiteSparse mirrors of SNAP classic graphs only as controlled fallback candidates.

## Replacement mapping

- `roadnet_ca_bfs_10000_seed42` and `roadnet_ca_bfs_20000_seed43` should be replaced first by TIGER/Line or OSM/Geofabrik road graphs.
- `ca_hepth_gcc` and `ca_astroph_gcc` should be replaced first by arXiv metadata reconstructions or OGB scientific graph candidates.
- SuiteSparse versions of SNAP classic graphs preserve historical continuity but remain fallback options because they still inherit a provenance relationship with the original SNAP data.

## Repository policy

Default policy for all candidate families in this shortlist:

- do not commit raw source archives;
- prefer scripts, hashes, manifests and metadata snapshots;
- do not redistribute derived graphs until the license review explicitly permits it;
- preserve upstream metadata and citations;
- document all transformations;
- keep license review separate from benchmark results.

## Claim boundary

This shortlist does not add empirical benchmark results, does not authorize monograph prose and does not modify `decisions/08_Results_to_Text_Map.md`.

Issue `#143` remains open until concrete license-clear replacement candidates are curated and either admitted for M3 smoke or explicitly rejected.
