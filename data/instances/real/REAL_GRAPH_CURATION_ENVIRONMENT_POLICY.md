# Real-graph curation environment policy

This file records the operational environment policy for the real-graph replacement path after the SNAP classic exclusion decision.

## Policy

The dedicated server `srv-noctua` is the preferred and normative execution environment for any real-graph curation step that may produce experimental or data-derived artifacts.

This includes:

- downloading raw external data;
- generating raw-source hashes;
- generating derived graph artifacts;
- validating graph structure at non-trivial scale;
- computing morphology descriptors;
- running M3 smoke tests;
- running M4 confirmatory benchmarks;
- running fixed-target, TTT, ECDF or attainment analyses;
- training or validating CART gatekeeper models from benchmark outputs.

The local WSL environment may be used for:

- documentation-only patches;
- Git and PR operations;
- issue management;
- reading audit logs;
- commands that do not download data, create derived graph artifacts, run benchmarks or train models.

## Rationale

The purpose is to reduce avoidable environmental noise from WSL, filesystem differences, dependency differences and local resource constraints.

The benchmark and any data-producing curation stages should therefore be aligned with the same dedicated environment used for confirmatory execution.

## Required guard

Any future script that downloads data, hashes raw artifacts, derives graphs, validates non-trivial graph structure, runs M3/M4 or trains CART should include an explicit environment guard.

The guard should either:

- require `hostname` to match `srv-noctua`; or
- require a deliberate override variable such as `ALLOW_NON_NOCTUA_REALGRAPH_EXECUTION=1`, with the override printed in the audit log.

The override should be exceptional and documented.

## Current M2 primary targets

The next M2 license/admissibility targets are:

1. `tigerline_roads_state_or_county`;
2. `arxiv_metadata_hepth_astroph_reconstruction`;
3. `ogbn_arxiv_undirected_projection`.

These targets are not admitted to M3 or M4 by this policy. Each still requires a candidate-level license snapshot, transformation record and review decision.

## Non-goals

This policy does not admit any replacement graph to execution.

It also does not:

- download any dataset;
- produce raw or derived graph artifacts;
- edit monograph prose;
- add benchmark-result claims;
- modify `decisions/08_Results_to_Text_Map.md`.

Issue `#143` remains open until concrete replacement candidates are curated and either admitted for M3 smoke or explicitly rejected.
