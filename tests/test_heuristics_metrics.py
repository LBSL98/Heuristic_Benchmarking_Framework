import networkx as nx
import numpy as np

from heuristics.metrics import compute_metrics


def test_compute_metrics_basic():
    G = nx.path_graph(4)  # 0-1-2-3
    speeds = np.array([10.0, 11.0, 12.0, 13.0])
    clusters = [{0, 1}, {2, 3}]
    m = compute_metrics(G, clusters, speeds, delta_v=5.0)
    assert m["num_clusters"] == 2
    assert m["fo1"] == 10.0 + 12.0
    assert m["avg_std_dev"] >= 0.0
