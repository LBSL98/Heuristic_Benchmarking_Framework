# Probe evidence index for M2 scientific license snapshots

This file records the audit evidence used by the M2 scientific license snapshot manifests.

It is an index of audit artifacts, not a copy of raw source pages and not an execution whitelist.

This index does not admit any candidate to M3 or M4 execution.

## Source probes

The relevant probes are:

- `1016_noctua_m2_primary_license_snapshot_probe_no_remote_gh`;
- `1025_noctua_focused_ogbn_arxiv_license_context_probe`;
- `1026_noctua_ogbn_arxiv_section_boundary_license_probe`;
- `1027_noctua_hash_ogbn_license_probe_artifacts`;
- `1032_noctua_odc_by_terms_snapshot_probe`;
- `1033_noctua_hash_odc_by_terms_probe_artifacts`.

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

### ODC-BY terms and OGB source snapshot

| artifact | sha256 | role |
|---|---|---|
| `audit_reports/confirmatory_plan_956/1032_noctua_odc_by_terms_snapshot_probe.remote.txt` | `c4ab03e8f3452f0fa9a15ff959f596f7a27eee48343a2735a827686ada34a436` | full terminal log of ODC-BY terms snapshot probe |
| `audit_reports/confirmatory_plan_956/1032_noctua_odc_by_terms_snapshot_probe.json` | `9c23e740c5a856a4c9d8f046320f1d851a347910bfb23521db9d8b1177353e24` | structured ODC-BY terms and OGB page snapshot evidence |
| `audit_reports/confirmatory_plan_956/1032_noctua_odc_by_terms_snapshot_probe.md` | `b4ddd59662c7830edc72f35674e21a350747b7ec810391623d3f6cd10d65340f` | human-readable ODC-BY terms snapshot summary |
| `audit_reports/confirmatory_plan_956/1033_noctua_hash_odc_by_terms_probe_artifacts.remote.txt` | `0dc25414aeaf3f8b63ec7303b91dcd8afe4342a1bdb45003feb46a29d9f58b94` | full terminal log of hash inventory for 1032 artifacts |
| `audit_reports/confirmatory_plan_956/1033_noctua_hash_odc_by_terms_probe_artifacts.json` | `1c1316fbb6a3eddfac6e60539807bf4080dd9a98ef6662b2c9d9f7a4bdc224f7` | structured hash inventory for 1032 artifacts |
| `audit_reports/confirmatory_plan_956/1033_noctua_hash_odc_by_terms_probe_artifacts.md` | `3661f3c549f098d3811246b485f4a9db4b3342e5cd30a9c7a1273d19c86e604c` | human-readable hash inventory for 1032 artifacts |

### Page snapshots from 1032

| URL | HTTP | SHA256 | text_length | role |
|---|---:|---|---:|---|
| `https://opendatacommons.org/licenses/by/1-0/` | `200` | `681a60875b4d6e125401054eb50d8968374268e808952b1ec640a73f85cfcf1d` | `21384` | authoritative ODC-BY terms page |
| `https://opendatacommons.org/licenses/by/1-0/index.html` | `200` | `681a60875b4d6e125401054eb50d8968374268e808952b1ec640a73f85cfcf1d` | `21384` | equivalent ODC-BY terms page |
| `https://ogb.stanford.edu/docs/nodeprop/#ogbn-arxiv` | `200` | `00c8d645665e0d2dc1c643872b46f9f34c9fd9c469736fdf3e54b34c881c1b2f` | `15005` | OGB node property dataset documentation snapshot |

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
- exact ODC-BY terms snapshot is recorded from `https://opendatacommons.org/licenses/by/1-0/`;
- exact OGB `ogbn-arxiv` documentation snapshot is recorded from `https://ogb.stanford.edu/docs/nodeprop/#ogbn-arxiv`;
- ODC-BY attribution obligations must be satisfied before any M3 promotion;
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

A later issue must still record final admission or rejection, exact acquisition procedure, transformation procedure, raw and derived hashes when applicable, exact ODC-BY attribution text, redistribution policy and holdout grouping before M3 smoke execution.
