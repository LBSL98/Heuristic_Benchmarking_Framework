import networkx as nx

from hpc_framework.greedy_adapter import instance_to_nx_graph


def test_instance_to_nx_graph_builds_graph_with_velocity_attributes():
    inst = {
        "instance_id": "toy",
        "nodes": [
            {"id": 0, "velocity": 1.5},
            {"id": 1, "velocity": 2.0},
            {"id": 2, "velocity": 2.5},
        ],
        "edges": [
            [0, 1],
            [1, 2],
        ],
    }

    g = instance_to_nx_graph(inst)

    assert isinstance(g, nx.Graph)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 2

    assert g.has_edge(0, 1)
    assert g.has_edge(1, 2)

    assert g.nodes[0]["velocity"] == 1.5
    assert g.nodes[1]["velocity"] == 2.0
    assert g.nodes[2]["velocity"] == 2.5
