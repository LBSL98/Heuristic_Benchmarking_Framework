# Data directory policy

This directory separates versioned curated inputs from local-only execution, cache and temporary material.

## Versioned data

`data/instances/` is the versioned location for curated benchmark instances and lightweight metadata manifests.

Files under `data/instances/` may be committed only when they are intentionally curated project inputs or lightweight documentation/metadata needed to reproduce the benchmark protocol.

The current real-graph confirmatory curation manifest is:

- `data/instances/real/confirmatory_real_graph_candidates.csv`

## Local-only data

The following paths are local-only and ignored by Git:

- `data/cache/`
- `data/tmp/`
- `data/results_raw/`
- `data/results_parquet/`

Use `data/cache/external_sources/` for downloaded external source archives such as SNAP `.txt.gz` files when a source audit requires local raw inputs.

Use `data/tmp/` for scratch transformations, intermediate conversion products and disposable working files.

Use `data/results_raw/` and `data/results_parquet/` for execution outputs and derived result tables, not for external source inputs.

## audit_reports boundary

`audit_reports/` is not a data cache.

Use `audit_reports/` only for terminal logs, command outputs, action records and chat-interaction audit notes. Do not store raw datasets, downloaded source archives, execution inputs, cache files or transformation scratch files there.

A command log may mention paths, checksums and summaries, but the raw files themselves must live outside `audit_reports/`.

## Raw external sources

Raw external source files must not be committed unless a later issue explicitly defines a specific file as a versioned source artifact and records why that is necessary.

For M1 real-graph curation, raw SNAP files may be downloaded only to a local ignored cache such as:

- `data/cache/external_sources/snap/`

Any versioned metadata derived from those files must avoid relying on a private absolute path. It should record stable public source information, checksum, file size, retrieval date or HTTP metadata when available, and the command or script used to reproduce the audit.

## Current M1 boundary

The M1 real-graph manifest documents candidates. It does not admit candidates to M3 smoke or M4 execution while license, raw-source audit, morphology descriptors or holdout policy remain incomplete.
