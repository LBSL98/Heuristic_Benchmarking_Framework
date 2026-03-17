"""Adaptadores para integrar o baseline guloso ao fluxo declarativo do framework."""

from __future__ import annotations

import networkx as nx
import numpy as np

from heuristics.greedy import run_greedy_heuristic
from hpc_framework.runner import compute_cutsize_edges_labels, extract_graph_from_instance


def clusters_to_labels(clusters: list[set[int]], n: int) -> np.ndarray:
    """Converte clusters (list[set[int]]) em vetor de rótulos zero-based."""
    labels = np.full(n, -1, dtype=int)

    for cluster_id, cluster in enumerate(clusters):
        for v in cluster:
            if labels[v] != -1:
                raise ValueError("Some vertices were assigned more than once.")
            labels[v] = cluster_id

    if np.any(labels < 0):
        raise ValueError("Some vertices were not assigned to any cluster.")

    return labels


def observed_k_from_labels(labels: np.ndarray) -> int:
    """Retorna o número de blocos distintos observados em um vetor de rótulos."""
    if labels.ndim != 1:
        raise ValueError("labels must be a 1D array")
    return int(np.unique(labels).size)


def instance_to_nx_graph(inst: dict) -> nx.Graph:
    """Converte uma instância JSON para networkx.Graph."""
    g = nx.Graph()

    for node in inst.get("nodes", []):
        node_id = int(node["id"])
        attrs = {k: v for k, v in node.items() if k != "id"}
        g.add_node(node_id, **attrs)

    for edge in inst.get("edges", []):
        u, v = int(edge[0]), int(edge[1])
        g.add_edge(u, v)

    return g


def run_greedy_adapter(inst: dict, delta_v: float) -> np.ndarray:
    """Executa a heurística gulosa sobre a instância e devolve labels zero-based."""
    graph = instance_to_nx_graph(inst)
    clusters = run_greedy_heuristic(graph, delta_v=delta_v)
    n = graph.number_of_nodes()
    return clusters_to_labels(clusters, n=n)


def run_greedy_observation(inst: dict, delta_v: float) -> dict:
    """Produz a observação mínima auditável do baseline guloso."""
    labels = run_greedy_adapter(inst, delta_v=delta_v)
    _, edges = extract_graph_from_instance(inst)
    return {
        "labels": labels,
        "observed_k": observed_k_from_labels(labels),
        "cutsize_best": compute_cutsize_edges_labels(edges, labels),
    }
