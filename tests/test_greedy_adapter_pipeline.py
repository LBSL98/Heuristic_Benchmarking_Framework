import numpy as np

from hpc_framework.greedy_adapter import run_greedy_adapter


def test_run_greedy_adapter_converts_instance_and_clusters_to_labels(monkeypatch):
    calls = {}

    def fake_run_greedy_heuristic(graph, delta_v):
        calls["n_nodes"] = graph.number_of_nodes()
        calls["n_edges"] = graph.number_of_edges()
        calls["delta_v"] = delta_v
        return [{0, 2}, {1, 3}]

    import hpc_framework.greedy_adapter as adapter_mod

    monkeypatch.setattr(
        adapter_mod, "run_greedy_heuristic", fake_run_greedy_heuristic, raising=False
    )

    inst = {
        "instance_id": "toy",
        "nodes": [
            {"id": 0, "velocity": 1.0},
            {"id": 1, "velocity": 1.1},
            {"id": 2, "velocity": 1.2},
            {"id": 3, "velocity": 1.3},
        ],
        "edges": [
            [0, 1],
            [1, 2],
            [2, 3],
        ],
    }

    labels = run_greedy_adapter(inst, delta_v=0.25)

    assert isinstance(labels, np.ndarray)
    assert labels.tolist() == [0, 1, 0, 1]

    assert calls["n_nodes"] == 4
    assert calls["n_edges"] == 3
    assert calls["delta_v"] == 0.25
