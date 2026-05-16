# License-clear replacement curation

This file defines the replacement-candidate shortlist after the SNAP classic exclusion decision.

The companion CSV is:

- `data/instances/real/license_clear_replacement_candidates.csv`

## Status

This shortlist is not an execution whitelist.

The original SNAP-derived M1 candidates were excluded from the public confirmatory real-graph sample because no explicit dataset-license basis was accepted for `roadNet-CA`, `ca-HepTh` or `ca-AstroPh`.

The replacement path must therefore use license-clear sources. No candidate family in this file is admitted to M3 smoke or M4 confirmatory execution yet.

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
