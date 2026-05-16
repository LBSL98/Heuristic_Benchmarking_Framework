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

These rows remain deliberately conservative. Later sections record source URLs, download URLs, citations, raw-source hash metadata and morphology descriptors. The license field remains unresolved, and the rows are still not admitted to M3/M4 execution.

## Source-audit update: official SNAP dataset pages

The current four candidates are derived from official SNAP dataset pages:

- `roadnet_ca_bfs_10000_seed42` and `roadnet_ca_bfs_20000_seed43` use `https://snap.stanford.edu/data/roadNet-CA.html` and download file `https://snap.stanford.edu/data/roadNet-CA.txt.gz`.
- `ca_hepth_gcc` uses `https://snap.stanford.edu/data/ca-HepTh.html` and download file `https://snap.stanford.edu/data/ca-HepTh.txt.gz`.
- `ca_astroph_gcc` uses `https://snap.stanford.edu/data/ca-AstroPh.html` and download file `https://snap.stanford.edu/data/ca-AstroPh.txt.gz`.

The SNAP dataset pages provide source/citation information and describe these inputs as undirected graphs or graphs with undirected edges. The manifest therefore records dataset URL, download URL, citation and directedness status.

The license field remains intentionally conservative as `NO_EXPLICIT_LICENSE_FOUND_IN_SNAP_DATASET_PAGE_PENDING_REVIEW`. This means the candidates are still not admitted to M3/M4 execution. A later audit must decide whether the SNAP pages, source papers, repository policy or institutional/legal interpretation are sufficient for the intended benchmark use.

The raw-input field was later updated by the raw-source hash audit. The raw SNAP source archives are not versioned; only reproducible metadata are recorded.

## Anti-winner-conditioned selection rule

Real-graph candidates must not be selected, excluded, resized or promoted based on observed solver winners, exception labels, CART labels, cut quality or runtime outcomes.

Candidate inclusion must be justified by provenance, license, auditability, morphology coverage, size feasibility and holdout grouping.

## Repository storage policy for M1 source audits

Raw external source files must not be downloaded into `audit_reports/`.

For this project workflow, `audit_reports/` is limited to terminal logs, command outputs, action records and chat-interaction audit notes. It must not be used as a storage area for raw datasets, downloaded source archives, execution inputs, cache files or transformation scratch files.

When M1 source auditing requires local raw files, use an ignored local cache such as:

- `data/cache/external_sources/snap/`

When conversion or inspection requires disposable intermediates, use:

- `data/tmp/`

Curated benchmark instances and lightweight metadata manifests belong under `data/instances/` only after they are intentionally selected as versioned repository inputs.

This policy corrects the earlier workflow error in which raw SNAP files were temporarily downloaded under `audit_reports/`. Those files were removed and no metadata from that incorrect location is accepted as a source-of-truth manifest update.

## Raw source hash and connectivity audit

Probe `983` downloaded the raw SNAP source files only to the ignored local cache `data/cache/external_sources/snap/`. The raw files are not versioned.

The manifest records derived and reproducible raw-source metadata:

- raw source filename;
- raw source SHA-256;
- compressed file size;
- retrieval timestamp;
- HTTP `Last-Modified`, `ETag` and `Content-Length` metadata when available;
- raw edge-record counts;
- unique raw node counts;
- unique undirected raw edge counts after self-loop removal;
- raw self-loop counts;
- malformed raw-line counts.

The manifest also records an independent connectivity check over each already-curated `.json.gz` candidate. All four current candidates are connected under that check.

This audit resolves the local raw-source hash step but does not resolve the license field, does not complete morphology descriptors and does not promote candidates to M3/M4. The license field remains `NO_EXPLICIT_LICENSE_FOUND_IN_SNAP_DATASET_PAGE_PENDING_REVIEW`, and each candidate remains `candidate_confirmatory_pending`.

## Morphology descriptor audit

Probe `987` computed morphology descriptors for the four current real-graph candidates without modifying repository inputs or raw graph files.

The manifest records versioned descriptor metadata:

- node and edge counts;
- density;
- minimum, maximum and average degree;
- degree coefficient of variation;
- degree Gini coefficient;
- degree percentiles `p50`, `p90` and `p99`;
- leaf fraction;
- component count;
- largest component fraction;
- sampled average local clustering;
- sampled transitivity proxy;
- approximate BFS diameter;
- approximate mean BFS distance.

The clustering and distance descriptors are explicitly sampled or approximate descriptors. They are intended for curation, coverage and selector-feature traceability, not as exact graph-theoretic claims.

This audit completes the M1 morphology-descriptor step for the current four candidates, but it does not resolve the license field and does not promote candidates to M3/M4. The license field remains `NO_EXPLICIT_LICENSE_FOUND_IN_SNAP_DATASET_PAGE_PENDING_REVIEW`, and each candidate remains `candidate_confirmatory_pending`.

## License and admissibility audit

Probe `991` fetched the official SNAP dataset pages, the SNAP data index, the SNAP home page and the SNAP software page.

The dataset pages for `roadNet-CA`, `ca-HepTh` and `ca-AstroPh` were reachable and provided file/citation evidence, but the automated audit did not find an explicit dataset license grant on those dataset pages. A `BSD license` keyword was found on the SNAP software page, but that evidence refers to the SNAP/GLib software code and is not treated as a license for the dataset files.

Therefore, this manifest records the license/admissibility state as unresolved:

- `source_license = NO_EXPLICIT_LICENSE_FOUND_IN_SNAP_DATASET_PAGE_PENDING_REVIEW`;
- `license_admissibility_status = m1_license_unresolved_human_or_institutional_review_required`;
- `candidate_status = candidate_confirmatory_pending`.

This is a conservative research-data governance boundary, not an empirical benchmark result. Public availability, citation metadata and downloadable files are not treated as sufficient evidence of reuse permission. A later human or institutional review must either provide an explicit accepted license basis or decide to exclude/replace these candidates before M3/M4 execution.

## M1 gate outcome

The current M1 curation metadata is complete enough to state the gate outcome for the four documented real-graph candidates.

The outcome is blocked, not approved:

- provenance, source URLs, citations and directedness were recorded;
- local raw-source hash metadata was recorded;
- independent connectivity was checked;
- morphology descriptors were recorded;
- holdout grouping fields are present;
- license/admissibility remains unresolved.

Therefore, the current candidates remain documented M1 candidates only. They are not an execution whitelist and are not admitted to M3 smoke or M4 confirmatory execution.

The original blocking condition was:

- `license_admissibility_status = m1_license_unresolved_human_or_institutional_review_required`;
- `license_admissibility_decision = not_ready_for_m3_m4_until_explicit_license_basis_or_exclusion_decision`;
- `candidate_status = candidate_confirmatory_pending`.

Issue `#143` then resolved this decision path conservatively by excluding these SNAP classic candidates from the public confirmatory sample and requiring license-clear replacements before any M3/M4 real-graph execution. No benchmark claim may rely on these candidates as confirmatory real-graph evidence.

## SNAP classic exclusion decision

The successor license/admissibility review in issue `#143`, together with the deeper probe `998` and the external admissibility research, changes the final treatment of the current SNAP-derived candidates.

The current candidates are no longer merely pending. They are excluded from the public confirmatory real-graph sample unless a later issue reopens them with an explicit accepted dataset-license basis.

The excluded SNAP classic candidates are:

- `roadnet_ca_bfs_10000_seed42`;
- `roadnet_ca_bfs_20000_seed43`;
- `ca_astroph_gcc`;
- `ca_hepth_gcc`.

The exclusion rationale is:

- the official SNAP pages for `roadNet-CA`, `ca-HepTh` and `ca-AstroPh` did not provide an explicit dataset license in the project audits;
- the SNAP BSD license is treated as a software license for SNAP/GLib, not as a license for the dataset files;
- the SNAP `telecom-graph` control case shows that some SNAP datasets expose a dataset-specific `LICENSE`, so dataset licensing must be handled dataset by dataset;
- public availability, citation metadata and downloadable files are not sufficient to admit a dataset to the public confirmatory sample.

The manifest records this as:

- `snap_classic_exclusion_status = excluded_from_confirmatory_public_sample`;
- `replacement_required = true`;
- `candidate_status = candidate_excluded_license_unresolved_replacement_required`;
- `license_admissibility_decision = excluded_from_m3_m4_until_license_clear_replacement_is_curated`.

Replacement should prioritize license-clear sources:

- TIGER/Line or OSM/Geofabrik for road graphs;
- arXiv metadata under CC0 for scientific collaboration/citation reconstructions;
- OGB datasets with explicit compatible dataset licenses;
- SuiteSparse only as a controlled fallback, preferably without redistributing raw or derived graph files by default.

This decision does not remove the historical audit value of the four candidates. It records that they are documented negative/admissibility cases, not M3/M4 execution inputs.

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

Issue `#49` remains the residual writing blocker. Issue `#127` was closed after the M1 curation/audit scope reached a documented blocked gate. Issue `#143` tracks the remaining license-clear replacement path.
