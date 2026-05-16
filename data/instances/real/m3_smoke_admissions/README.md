# M3 smoke admissions

This directory records explicit real-graph candidate admissions from M2 documentation review into M3 smoke-only acquisition and validation.

An admission here is not an M4 benchmark admission.

## Current admissions

- `ogbn_arxiv_undirected_projection_m3_smoke_admission.yaml`

## Guardrails

- M3 smoke may prepare acquisition and validation scripts.
- M3 smoke may download raw data only into ignored local paths.
- M3 smoke may compute raw and derived hashes.
- M3 smoke may derive a graph only as a local validation artifact unless later explicitly admitted.
- M3 smoke must not commit raw datasets.
- M3 smoke must not commit derived graph files unless a later explicit issue permits it.
- M3 smoke must not run benchmark campaigns.
- M3 smoke must not train CART.
- M3 smoke must not edit monograph result claims.
- M4 remains blocked until a later explicit gate decision.

## ogbn-arxiv M3 smoke evidence after 1050

The `ogbn-arxiv` M3 smoke chain completed on `srv-noctua`.

Recorded evidence:

- environment bootstrap: `1046`;
- controlled OGB acquisition/cache smoke: `1047`;
- failed processed-cache projection attempt: `1048`;
- successful raw-CSV undirected projection smoke: `1049`;
- artifact hash inventory: `1050`.

The versioned evidence manifest is:

- `data/instances/real/m3_smoke_admissions/ogbn_arxiv_undirected_projection_m3_smoke_evidence.yaml`.

M3 smoke results:

- raw file count: `14`;
- raw total size: `191275959` bytes;
- nodes: `169343`;
- directed edges: `1166243`;
- self-loops removed: `0`;
- undirected union edges: `1157799`;
- connected components: `1`;
- largest component size: `169343`;
- projection SHA256: `5e3a7c7eea2ef66c46ca9091fc707c27bfd8f0844bacea29d427299d8e3fcf8c`.

Boundary:

- the projection is local-only under ignored `data/tmp`;
- the projection is not committed;
- the projection is not admitted to M4;
- no benchmark campaign was run;
- no CART training was run;
- no monograph result claim is supported.

## ogbn-arxiv versioned reproducer after PR 153

The raw-CSV projection reproducer for `ogbn-arxiv` was merged through PR `#153` at commit `6cc45206994af72b0df7dbbeb8e9b90d21cbdfba`.

Post-merge validation `1064` confirmed on `srv-noctua` that:

- the merged reproducer is present;
- the Python 3.10-compatible timestamp guard is present;
- the 14-file raw inventory remains verified;
- the legacy M3 projection hash remains `5e3a7c7eea2ef66c46ca9091fc707c27bfd8f0844bacea29d427299d8e3fcf8c`;
- the versioned reproducer projection hash is `b6533424c1f0b226127130697c7effbab2c1dbfd07c8ed48f0468bbc46e290ba`;
- the repeated reproducer projection hash matches the first reproducer run;
- M4 benchmark, benchmark campaigns, CART training and monograph result claims remain blocked.

This record documents reproducibility of the M3 validation procedure. It does not admit `ogbn-arxiv` to M4.
