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
