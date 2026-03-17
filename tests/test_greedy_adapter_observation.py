import numpy as np

from hpc_framework.greedy_adapter import run_greedy_observation


def test_run_greedy_observation_returns_labels_observed_k_and_cutsize(monkeypatch):
    def fake_run_greedy_adapter(inst, delta_v):
        assert delta_v == 0.25
        return np.array([0, 1, 0, 1], dtype=int)

    import hpc_framework.greedy_adapter as adapter_mod

    monkeypatch.setattr(adapter_mod, "run_greedy_adapter", fake_run_greedy_adapter, raising=False)

    inst = {
        "instance_id": "toy",
        "num_nodes": 4,
        "edges": [
            [0, 1],
            [1, 2],
            [2, 3],
        ],
    }

    obs = run_greedy_observation(inst, delta_v=0.25)

    assert isinstance(obs, dict)
    assert obs["labels"].tolist() == [0, 1, 0, 1]
    assert obs["observed_k"] == 2
    assert obs["cutsize_best"] == 3
