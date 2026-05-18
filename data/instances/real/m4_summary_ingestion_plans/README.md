# M4 reduced summary ingestion plans

This directory stores plans for reduced, versioned summaries derived from reviewed real-graph execution records.

A plan in this directory does not itself ingest raw solver outputs, partition files, raw graph files, derived graph files, CART training tables, or monograph claims. It only defines the safe target schema and boundary for a later reduced-summary record.

## Current plans

- `ogbn_arxiv_1113_reduced_summary_ingestion_plan.yaml`: admits only a reduced YAML summary for the bounded `ogbn-arxiv` calibrated multilevel execution `1113`.
