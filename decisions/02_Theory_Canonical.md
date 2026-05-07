# 02_Theory_Canonical.md

## Purpose

This file stores the theoretical canon of the monograph: definitions, conceptual boundaries, and literature-grounded formulations that should remain stable across revisions.

## Scope of the theoretical canon

This project studies graph partitioning and algorithm selection under a benchmarking-driven methodology. The canon here should state what the work is conceptually about before implementation details are discussed.

## Core conceptual pillars

### Graph Partitioning Problem (GPP)
The project adopts the graph partitioning problem in its classical form: partitioning a graph into `k` balanced parts while minimizing inter-block cut-related cost. The exact formal restrictions and metric choices used in the work must be mirrored in `03_Methodology_Canonical.md`, but the theoretical positioning belongs here.

### Algorithm Selection Problem (ASP)
The project treats solver choice as an algorithm selection problem. The relevant conceptual claim is not that one universal solver exists, but that instance characteristics may inform a rule for selecting among competing approaches.

### Portfolio perspective
The work is grounded in the idea that different algorithms may dominate in different regions of instance space. Claims about dominance must remain conditional, not universal.

### Benchmarking discipline
The project depends on fair and controlled comparison. Theoretical references used to justify benchmarking choices must be recorded here before they are operationalized in methodology.

## Terminology guardrails

- Do not use "best" without scope, metric, and budget.
- Do not use "fair" without an explicit fairness protocol.
- Do not use "reproducible" unless the required artifact chain exists.
- Do not use "interpretable" as decoration; state what is interpretable and to whom.
- Do not state cross-instance superiority unless the evidence supports that breadth.

## Current theory checkpoints to preserve

1. The monograph frames GPP as a trade-off between balanced partitions and low communication/cut cost.
2. The work does not assume a universally dominant algorithm.
3. The monograph motivates algorithm selection as a practical response to heterogeneous instance behavior.
4. Any application-domain motivation used in the introduction must remain consistent with the literature framing in Chapter 2.

## Items to populate and freeze later

- Formal definition wording adopted for GPP.
- Theoretical framing of multilevel methods.
- Theoretical framing of anytime metaheuristics.
- Canonical statement of the ASP perspective.
- Literature-grounded explanation of instance-space reasoning.

### Dominance-conditioned selector framing
The selector is not theoretically motivated by an assumption that all paradigms should win equally often. Multilevel graph partitioners are treated as strong reference solvers in the GPP literature and in practical engineering use. Therefore, one legitimate and often stronger ASP framing is exception-oriented: identify when the multilevel default is not dominant, not merely which paradigm wins most often.

The canonical question may be read in two layers:

- fixed-budget exception question: given instance features, is the best multilevel reference solver still the best choice at the official `T*`?
- budget-aware exception question: given instance features and an available wall-clock budget, when does the best multilevel reference solver stop being dominant or become only marginally better?

This framing does not assume that exceptions exist. A benchmark may validly conclude that the multilevel baseline dominates the evaluated slice and that selector usefulness is limited under that condition. If exceptions are observed, they must be described by their scope: strong wins, near ties, competitive gaps, temporal reversals, implementation-maturity shifts, or selector-level oracle gaps.

No-Free-Lunch is therefore used as a theoretical motivation for conditional behavior, not as a result to be proven by the benchmark. The project must not inflate isolated exceptions into a universal claim that metaheuristics dominate multilevel methods.

### Quality-by-time selector interpretation

The benchmark theory must distinguish speed, quality, and availability within a time budget. A solver that finishes quickly with a moderate cut and a solver that finishes later with a better cut answer different user needs. Therefore, the relevant selection question is not simply which algorithm is fastest, nor only which algorithm has the best final cut. The decision-relevant question is which algorithm delivers the best validated solution within a declared wall-clock budget.

This distinction is especially important for the multilevel baselines. `METIS` is primarily useful as a fast reference. `KaHIP` is primarily useful as a quality-oriented reference. It is expected that KaHIP may lose to METIS in elapsed time while still being relevant because it can produce lower edge cuts. Such a result is not a methodological failure; it is part of the time-quality trade-off that the benchmark is meant to expose.

For budget-aware analysis, point-output solvers and anytime solvers can be represented on a common wall-clock axis:

- point-output solvers are unavailable before their measured completion time and available afterward with their final validated solution;
- anytime solvers are represented by their validated checkpoint trajectory;
- the common effort axis is wall-clock time, not NFE;
- NFE remains an internal diagnostic for instrumented metaheuristics and implementation-maturity analysis.

This framing supports three admissible selector targets, depending on evidence:

1. fixed-budget winner: `x_i -> y_i^*(T*)`;
2. budget-aware winner: `(x_i, t) -> y_i^*(t)`;
3. multilevel-sufficiency or exception classifier: `(x_i, t) -> whether the multilevel reference is sufficient`.

None of these targets is automatically valid. Selector usefulness requires empirical diagnostics: winner diversity, target entropy, `SBS`/`VBS`, oracle gap or regret-equivalent improvement, exception counts, and budget-dependent winner transitions. If those diagnostics show a degenerate target, the correct theoretical conclusion is that CART is limited or not substantively supported by the observed benchmark surface.

### CART validity under expanded controlled variation
The selector is a product only if the validated data show a nontrivial selection problem. The project may therefore expand the experimental design to test selector validity under controlled variation in three dimensions: graph morphology, available wall-clock budget, and implementation maturity of the metaheuristic portfolio.

This expansion is not a license to force a positive CART result. It reduces the risk that a negative selector result is merely an artifact of a narrow instance panel, a single budget slice, or a slow reference implementation of a metaheuristic. The admissible question is whether the expanded, preregistered evidence contains enough winner diversity, exception structure, or oracle gap to justify an interpretable selector.

The completed TS-Rust ablation can be used as TS-specific evidence that implementation maturity affects wall-clock behavior. It cannot by itself justify claims about all metaheuristics. A full Rust metaheuristic portfolio may support broader implementation-maturity claims only after `SA`, `TS`, `ILS`, and `GRASP` Rust implementations are each validated under explicit fidelity contracts and mapped to result claims.

The project may attempt the full Rust portfolio as a strong-scope extension, but this attempt is schedule-conditioned. If the two-week viability gate is not satisfied, the full Rust portfolio must be deferred and the monograph must preserve the narrower defensible interpretation.
