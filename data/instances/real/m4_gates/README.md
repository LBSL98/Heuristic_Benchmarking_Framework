# M4 real-graph gates

This directory records explicit gate decisions for real graph candidates after M3 smoke validation.

A gate file may admit a candidate only to the scope stated in that file. M4 smoke admission does not imply admission to a full benchmark campaign, CART training, redistribution or monograph result claims.

## ogbn-arxiv

`ogbn-arxiv` is admitted only to M4 smoke validation through:

- `data/instances/real/m4_gates/ogbn_arxiv_undirected_projection_m4_gate.yaml`

Current boundary:

- M4 smoke validation: admitted;
- confirmatory benchmark campaign: blocked;
- CART training: blocked;
- raw or derived data redistribution: blocked;
- raw or derived file commit: blocked;
- monograph result claim: blocked.

The accepted representation for smoke validation is the versioned raw-CSV projection procedure, with raw and derived artifacts remaining local-only under ignored `data/tmp`.
