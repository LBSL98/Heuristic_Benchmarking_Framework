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
