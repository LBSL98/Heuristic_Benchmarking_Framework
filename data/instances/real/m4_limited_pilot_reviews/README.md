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

## ogbn-arxiv after 1106 KaHIP ramp

The 1106 KaHIP budget ramp completed with:

- `30000 ms`: `status=ok`, `feasible=true`, `elapsed_ms=9334`, `cutsize_best=361338`;
- `120000 ms`: `status=ok`, `feasible=true`, `elapsed_ms=9326`, `cutsize_best=361338`;
- `300000 ms`: `status=ok`, `feasible=true`, `elapsed_ms=9333`, `cutsize_best=361338`.

Review decision:

- admit an ogbn-arxiv calibrated campaign command-plan gate: true;
- recommended KaHIP budget for the next command plan: `30000 ms`;
- full campaign execution admitted: false;
- full campaign execution requires later gate: true;
- CART training admitted: false;
- monograph result claims supported: false;
- redistribution allowed: false;
- raw/derived/output commits allowed: false.

The next step is a separate bounded command-plan issue. This review does not itself start execution.
