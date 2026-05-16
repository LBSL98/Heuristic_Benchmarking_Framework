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
