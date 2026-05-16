# M2 license snapshot manifests

This directory stores candidate-level M2 license/admissibility manifests for real-graph replacements.

These manifests are not execution whitelists.

A candidate may be promoted to M3 smoke only after a later issue records a final review decision, exact license scope, acquisition policy, transformation policy, hashes when applicable and holdout grouping.

## Current manifests

- `arxiv_metadata_hepth_astroph_reconstruction.yaml`
- `ogbn_arxiv_undirected_projection.yaml`

## Current status

Both scientific candidates are promising, but neither is admitted.

The `1016` srv-noctua probe found stronger evidence for the scientific candidates than for TIGER/Line:

- arXiv metadata: promising under CC0 for descriptive metadata only;
- ogbn-arxiv: promising because OGB documentation placed `License: CC-0` adjacent to the ogbn-arxiv entry;
- TIGER/Line: still needs manual review of the Census technical documentation chapter on legal disclaimer and citation.

## Guardrails

- Do not download raw datasets as part of this documentation patch.
- Do not commit raw datasets.
- Do not commit derived graphs unless a later admission issue explicitly permits it.
- Do not treat software licenses as dataset licenses.
- Do not admit M3/M4 execution from these manifests alone.
- Keep issue `#143` open until concrete replacements are admitted or rejected.
