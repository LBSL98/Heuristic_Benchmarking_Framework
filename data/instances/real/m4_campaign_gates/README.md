# M4 campaign gates

This directory records explicit decisions about whether a real graph candidate may enter confirmatory campaign scope.

A campaign gate does not run the campaign. It defines whether a candidate may proceed to a bounded campaign setup/smoke stage or must remain blocked.

## ogbn-arxiv

`ogbn-arxiv` is admitted as a campaign input by:

- `data/instances/real/m4_campaign_gates/ogbn_arxiv_undirected_projection_campaign_gate.yaml`

Current boundary:

- campaign input admission: true;
- full benchmark campaign run admitted by this gate: false;
- bounded campaign setup/smoke required before full run: true;
- solver comparison run: blocked;
- CART training: blocked;
- redistribution: blocked;
- raw or derived file commit: blocked;
- monograph result claim: blocked.

The accepted representation is the versioned raw-CSV projection artifact identified by SHA256 `b6533424c1f0b226127130697c7effbab2c1dbfd07c8ed48f0468bbc46e290ba`.
