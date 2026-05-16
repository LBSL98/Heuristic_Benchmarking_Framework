# M2 license snapshot manifests

This directory stores candidate-level M2 license/admissibility manifests for real-graph replacements.

These manifests are not execution whitelists.

A candidate may be promoted to M3 smoke only after a later issue records a final review decision, exact license scope, acquisition policy, transformation policy, hashes when applicable and holdout grouping.

## Current manifests

- `arxiv_metadata_hepth_astroph_reconstruction.yaml`
- `ogbn_arxiv_undirected_projection.yaml`

## Current status

The arXiv metadata candidate remains promising but not admitted. The `ogbn-arxiv` candidate is admitted only to M3 smoke acquisition and validation, not to M4 benchmark.

The current interpretation is:

- arXiv metadata: promising under CC0 for descriptive metadata only;
- `ogbn-arxiv`: admitted only to M3 smoke acquisition and validation; current license expectation is ODC-BY, not CC0; M4 benchmark remains blocked;
- TIGER/Line: still needs manual review of the Census legal disclaimer and citation documentation.

The `ogbn-arxiv` CC0 interpretation recorded after the `1016` probe was superseded by the `1026` section-boundary probe. That later probe isolated the `ogbn-arxiv` section and inferred `License: ODC-BY` for the candidate.

## Probe evidence index

The audit evidence used by these manifests is indexed in:

- `PROBE_EVIDENCE_INDEX.md`

The index records the `1016`, `1025`, `1026`, `1027`, `1032` and `1033` srv-noctua audit evidence. It does not by itself admit any candidate to execution; `ogbn-arxiv` has a separate M3 smoke-only admission record.

## Guardrails

- Do not download raw datasets as part of documentation patches.
- Do not commit raw datasets.
- Do not commit derived graphs unless a later admission issue explicitly permits it.
- Do not treat software licenses as dataset licenses.
- Do not treat neighboring dataset licenses as applying to `ogbn-arxiv`.
- Do not admit M3/M4 execution from these manifests alone.
- Keep issue `#143` open until concrete replacements are admitted or rejected.
