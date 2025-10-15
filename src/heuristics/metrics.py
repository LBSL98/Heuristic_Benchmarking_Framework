"""Helpers estáveis para calcular métricas a partir de clusters (sem efeitos colaterais)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import networkx as nx
import numpy as np


def compute_metrics(
    graph: nx.Graph,
    clusters: Iterable[set[int]],
    speeds: np.ndarray,
    *,
    delta_v: float | None = None,
) -> dict[str, Any]:
    cl_list: list[set[int]] = [set(c) for c in clusters if c]
    if len(speeds) < graph.number_of_nodes():
        raise ValueError("speeds length does not match number of nodes")
    mins, stds = [], []
    for C in cl_list:
        vals = speeds[list(C)]
        mins.append(float(np.min(vals)))
        stds.append(float(np.std(vals)) if len(C) > 1 else 0.0)
    return {
        "fo1": float(np.sum(mins)) if mins else 0.0,
        "num_clusters": len(cl_list),
        "avg_std_dev": float(np.mean(stds)) if stds else 0.0,
        "delta_v": delta_v,
    }
