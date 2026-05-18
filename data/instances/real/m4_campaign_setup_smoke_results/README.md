# M4 campaign setup smoke results

This directory records bounded campaign setup/smoke outcomes for real graph candidates.

A setup/smoke result is not a benchmark campaign result. It may validate campaign wiring, artifact references, hash stability, graph counts and attribution propagation, but it does not support solver performance claims.

## ogbn-arxiv

`ogbn-arxiv` completed bounded campaign setup/smoke validation in probe `1086B_noctua_run_ogbn_arxiv_campaign_setup_smoke_with_venv`.

Recorded result:

- `data/instances/real/m4_campaign_setup_smoke_results/ogbn_arxiv_undirected_projection_1086B_setup_smoke_result.yaml`

Confirmed boundary:

- campaign setup smoke completed: true;
- campaign input manifest check passed: true;
- projection hash verified: true;
- graph counts verified: true;
- attribution metadata propagated: true;
- full benchmark campaign run: false;
- solver comparison run: false;
- solver invoked: false;
- CART training run: false;
- redistribution allowed: false;
- raw or derived files committed: false;
- monograph result claim supported: false.

Full campaign execution remains blocked until a separate execution gate is versioned.
