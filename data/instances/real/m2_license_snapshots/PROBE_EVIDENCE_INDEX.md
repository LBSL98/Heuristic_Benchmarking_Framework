# Probe evidence index for M2 scientific license snapshots

This file records the audit evidence used by the M2 scientific license snapshot manifests.

It is an index of audit artifacts, not a copy of raw source pages and not an execution whitelist.

This index does not admit any candidate to M3 or M4 execution.

## Source probes

The relevant probes are:

- `1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh`;
- `1025_noctua_focused_ogbn_arxiv_license_context_probe`;
- `1026_noctua_ogbn_arxiv_section_boundary_license_probe`;
- `1027_noctua_hash_ogbn_license_probe_artifacts`.

Execution environment:

- host: `srv-noctua`;
- repository head for 1016/1020 validation: `cdf7c0d96cd174554351263f78d920c293359da6`;
- repository head for 1025/1026/1027: `e6f647a50ae0c4d6ece42b725c6d712f6fa2f40b`;
- issue tracker: `#143`, still open for concrete replacement curation.

## Audit artifacts on srv-noctua

The following ignored audit artifacts remain outside Git under `/audit_reports/`.

### General 1016 M2 probe

| artifact | sha256 | role |
|---|---|---|
| `audit_reports/confirmatory_plan_956/1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh.remote.txt` | `0ffff170223b1f67f66fcd9eccc00055c698ae6c20f4c717489c64c5805fdd7b` | full terminal log of the remote probe |
| `audit_reports/confirmatory_plan_956/1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh.json` | `23742ed1bdde4a039ea7f317924c15d05a224c6c1eb9bcfeda6b97727b4d83a0` | structured probe evidence, page hashes and snippets |
| `audit_reports/confirmatory_plan_956/1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh.md` | `2c31426bdf71a354a844c2ebb74fe04a60ace1e94493d79d6ad373d0e5d568e2` | human-readable probe summary |

### Focused ogbn-arxiv probes

| artifact | sha256 | role |
|---|---|---|
| `audit_reports/confirmatory_plan_956/1025_noctua_focused_ogbn_arxiv_license_context_probe.remote.txt` | `711849c59fd2e8bc703bce57ecc3f020627e8aa9824d51c80abfefc958e9d445` | full terminal log of focused context probe |
| `audit_reports/confirmatory_plan_956/1025_noctua_focused_ogbn_arxiv_license_context_probe.json` | `cc4448512afa1ab35a8c1c04183c86c149f88e22cf7d60e20e72609f996cca97` | structured focused-context evidence |
| `audit_reports/confirmatory_plan_956/1025_noctua_focused_ogbn_arxiv_license_context_probe.md` | `a9dd9a4e7193ea7a8be53815dca640f2934536e937b5ec74b3d38f24e3a6b1a3` | human-readable focused-context summary |
| `audit_reports/confirmatory_plan_956/1026_noctua_ogbn_arxiv_section_boundary_license_probe.remote.txt` | `ec78a190aff5b83f882fbb166cd9aac3228fe9ca8ec78b304de3e335ea09fcb2` | full terminal log of section-boundary probe |
| `audit_reports/confirmatory_plan_956/1026_noctua_ogbn_arxiv_section_boundary_license_probe.json` | `cd80159f05c5c7d7aa31ef4e5df59c40af5f7a05b39dea995bcdd162e119806d` | structured section-boundary evidence |
| `audit_reports/confirmatory_plan_956/1026_noctua_ogbn_arxiv_section_boundary_license_probe.md` | `1e850a8a5dc7b738bb1e1b2afa7cd3fbff3b9f2fc37b6fd3f8ce3accf571d639` | human-readable section-boundary summary |

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
- current license expectation is ODC-BY;
- the earlier CC0 interpretation was superseded by the `1026` section-boundary probe;
- `1025` found mixed context requiring manual review;
- `1026` isolated the section from `Dataset ogbn-arxiv` to the next dataset heading and inferred `License: ODC-BY`;
- OGB software/package licensing remains separate from dataset licensing;
- neighboring OGB dataset licenses must not be transferred to `ogbn-arxiv`;
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

A later issue must still record final admission or rejection, exact acquisition procedure, transformation procedure, hashes when applicable, ODC-BY attribution handling and holdout grouping before M3 smoke execution.
