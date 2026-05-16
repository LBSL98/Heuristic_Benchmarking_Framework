# License-clear replacement curation

This file defines the replacement-candidate shortlist after the SNAP classic exclusion decision.

The companion CSV is:

- `data/instances/real/license_clear_replacement_candidates.csv`

## Status

This shortlist is not an execution whitelist.

The original SNAP-derived M1 candidates were excluded from the public confirmatory real-graph sample because no explicit dataset-license basis was accepted for `roadNet-CA`, `ca-HepTh` or `ca-AstroPh`.

The replacement path must therefore use license-clear sources. At this point, `ogbn-arxiv` is admitted only to M3 smoke acquisition and validation; no candidate family is admitted to M4 confirmatory execution.

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

## M2 scientific license snapshot manifests

Candidate-level M2 manifests exist for the two strongest scientific targets:

- `data/instances/real/m2_license_snapshots/arxiv_metadata_hepth_astroph_reconstruction.yaml`;
- `data/instances/real/m2_license_snapshots/ogbn_arxiv_undirected_projection.yaml`.

These manifests are not execution whitelists.

The arXiv metadata path is treated as promising only for descriptive metadata under CC0. Full text, PDFs, source files and e-prints remain out of scope unless separately licensed.

The `ogbn-arxiv` path remains promising, but its license expectation was corrected back to ODC-BY after the focused `1025` and section-boundary `1026` srv-noctua probes. The earlier CC0 interpretation from the broad `1016` probe is superseded. The `1026` probe isolated the `ogbn-arxiv` section and inferred `License: ODC-BY` for that candidate.

The OGB software/package MIT license remains separate from dataset licensing. Neighboring OGB dataset licenses must not be transferred to `ogbn-arxiv`.

TIGER/Line remains a primary target, but it still needs manual review of the Census legal disclaimer and citation documentation before a candidate-level admission decision.

## M3 smoke-only admission for ogbn-arxiv

The `ogbn-arxiv` candidate is admitted only to M3 smoke acquisition and validation.

This is not an M4 benchmark admission.

The decision is recorded in:

- `data/instances/real/m3_smoke_admissions/ogbn_arxiv_undirected_projection_m3_smoke_admission.yaml`.

Allowed M3 smoke work is limited to controlled acquisition on `srv-noctua`, local ignored raw-data storage, hash inventory, attribution metadata, directed-to-undirected transformation review, projected graph counts and local validation artifacts.

Blocked until a later explicit gate decision:

- benchmark campaign;
- CART training;
- raw or derived data redistribution;
- monograph result claims;
- M4 use of the candidate.

The basis for this restricted admission is the ODC-BY evidence chain already recorded in `PROBE_EVIDENCE_INDEX.md`, especially the `1026` section-boundary probe, the `1032` ODC-BY terms snapshot and the `1033` artifact hash inventory.

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
