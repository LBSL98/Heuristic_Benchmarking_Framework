# M4 limited pilot reviews

This directory records review decisions after bounded real-graph pilot executions.

A limited pilot review may admit a follow-up bounded pilot, such as a solver-specific budget ramp. It does not itself authorize full campaign execution, CART training, monograph result claims, redistribution, or committing local raw/derived/output artifacts.

## ogbn-arxiv after 1099B

The 1099B limited pilot completed with:

- METIS: `status=ok`, `feasible=true`, `elapsed_ms=1197`, `cutsize_best=223376`;
- KaHIP: `status=timeout`, `feasible=false`, `elapsed_ms=5021`, `cutsize_best=null`.

Review decision:

- admit KaHIP-only budget ramp pilot: true;
- full campaign execution admitted: false;
- CART training admitted: false;
- monograph result claims supported: false;
- redistribution allowed: false;
- raw/derived/output commits allowed: false.

The next step is a separate bounded command-plan issue for the KaHIP budget ramp.
