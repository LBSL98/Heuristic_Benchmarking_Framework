# Probe evidence index for M2 scientific license snapshots

This file records the audit evidence used by the M2 scientific license snapshot manifests.

It is an index of audit artifacts, not a copy of raw source pages and not an execution whitelist.

This index does not admit any candidate to M3 or M4 execution.

## Source probe

The relevant probe is:

- `1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh`

Execution environment:

- host: `srv-noctua`;
- repository head during probe: `4b5dcd1c5688f20c4c987bb9d7a393de14b67021`;
- later synchronized validation head: `cdf7c0d96cd174554351263f78d920c293359da6`;
- issue tracker: `#143`, still open for concrete replacement curation.

## Audit artifacts on srv-noctua

The `1020` synchronization check confirmed that the following ignored audit artifacts remain available on `srv-noctua`:

| artifact | sha256 | role |
|---|---|---|
| `audit_reports/confirmatory_plan_956/1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh.remote.txt` | `0ffff170223b1f67f66fcd9eccc00055c698ae6c20f4c717489c64c5805fdd7b` | full terminal log of the remote probe |
| `audit_reports/confirmatory_plan_956/1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh.json` | `23742ed1bdde4a039ea7f317924c15d05a224c6c1eb9bcfeda6b97727b4d83a0` | structured probe evidence, page hashes and snippets |
| `audit_reports/confirmatory_plan_956/1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh.md` | `2c31426bdf71a354a844c2ebb74fe04a60ace1e94493d79d6ad373d0e5d568e2` | human-readable probe summary |

These artifacts are intentionally ignored by Git under `/audit_reports/`.

## Evidence used by current manifests

### `arxiv_metadata_hepth_astroph_reconstruction`

Current interpretation:

- promising M2 replacement path;
- evidence supports CC0 only for descriptive arXiv metadata;
- full text, PDFs, source files and e-prints remain out of scope;
- candidate remains pending M2 manifest review and is not admitted to M3/M4.

Manifest:

- `data/instances/real/m2_license_snapshots/arxiv_metadata_hepth_astroph_reconstruction.yaml`

### `ogbn_arxiv_undirected_projection`

Current interpretation:

- promising M2 replacement path;
- `1016` evidence found `License: CC-0` adjacent to the `ogbn-arxiv` dataset entry;
- previous ODC-BY expectation is treated as stale for this dataset;
- OGB software/package licensing remains separate from dataset licensing;
- directed-to-undirected projection must be explicitly recorded before any GPP use;
- candidate remains pending M2 manifest review and is not admitted to M3/M4.

Manifest:

- `data/instances/real/m2_license_snapshots/ogbn_arxiv_undirected_projection.yaml`

## Guardrails

This index does not:

- admit any candidate to M3 or M4;
- download raw datasets;
- derive graph files;
- compute raw or derived graph hashes;
- authorize repository redistribution of raw or derived datasets;
- edit monograph prose;
- add benchmark-result claims;
- modify `decisions/08_Results_to_Text_Map.md`.

A later issue must still record final admission or rejection, exact acquisition procedure, transformation procedure, hashes when applicable and holdout grouping before M3 smoke execution.
