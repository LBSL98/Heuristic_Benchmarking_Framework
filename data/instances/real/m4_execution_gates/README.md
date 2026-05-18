# M4 execution gates

This directory records explicit decisions about whether a real graph candidate may enter campaign execution.

An execution gate does not itself run the campaign. It defines what execution scope is admitted and what remains blocked.

## ogbn-arxiv

`ogbn-arxiv` is admitted to limited campaign pilot execution by:

- `data/instances/real/m4_execution_gates/ogbn_arxiv_undirected_projection_execution_gate.yaml`

Current boundary:

- limited campaign pilot admitted: true;
- full campaign execution admitted: false;
- full campaign execution requires later gate: true;
- solver invocation admitted for limited pilot: true;
- solver comparison admitted for limited pilot: true;
- CART training: blocked;
- redistribution: blocked;
- raw or derived file commit: blocked;
- monograph result claim: blocked.

The accepted representation is the versioned raw-CSV projection artifact identified by SHA256 `b6533424c1f0b226127130697c7effbab2c1dbfd07c8ed48f0468bbc46e290ba`.
