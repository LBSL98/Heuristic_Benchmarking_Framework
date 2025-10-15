# `src/generator/cli.py`
::: generator.cli

## Public API (frozen)
`build_graph(rng, num_nodes, density) -> networkx.Graph`

- Conectividade garantida (árvore base + arestas extras).
- Densidade final, quando necessário: `2m/(n*(n-1))`.
- Modularidade pode ser `null` em grafos grandes (política de performance).
