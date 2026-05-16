# Real graph preparation scripts

This directory contains versioned scripts for real-graph acquisition and transformation procedures.

## prepare_ogbn_arxiv_undirected_projection.py

This script prepares a local undirected projection of OGB ogbn-arxiv from the raw CSV files:

- edge.csv.gz
- num-node-list.csv.gz

The script intentionally avoids torch.load and does not use the OGB processed pickle cache for projection.

Default guardrails:

- requires srv-noctua unless an explicit override is provided;
- writes outputs only under ignored data/tmp;
- does not admit M4 benchmark execution;
- does not run benchmark campaigns;
- does not train CART;
- does not authorize raw or derived data redistribution.

Example validation run on srv-noctua:

    data/tmp/real_graph_m3_smoke/ogbn_arxiv/venv_1046/bin/python \
      scripts/real_graphs/prepare_ogbn_arxiv_undirected_projection.py \
      --root data/tmp/real_graph_m3_smoke/ogbn_arxiv/raw \
      --output-dir data/tmp/real_graph_m3_smoke/ogbn_arxiv/derived/1057_versioned_reproducer_probe

The output is still a local validation artifact. A later explicit M4 gate is required before using any projection as benchmark input.

## Post-merge validation status

PR `#153` merged this reproducer at commit `6cc45206994af72b0df7dbbeb8e9b90d21cbdfba`.

The `1064` post-merge validation on `srv-noctua` confirmed that the merged script is present, keeps Python 3.10-compatible timestamp handling, verifies the 14-file raw inventory, and reproduces the deterministic local projection artifact from the raw CSV inputs.
The validated deterministic reproducer projection SHA256 is `b6533424c1f0b226127130697c7effbab2c1dbfd07c8ed48f0468bbc46e290ba`.

This validation does not admit M4 benchmark execution. M4 benchmark execution remains blocked; the output remains a local ignored validation artifact until a later explicit M4 gate decision.
