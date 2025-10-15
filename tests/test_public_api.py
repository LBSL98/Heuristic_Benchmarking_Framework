import importlib
import inspect


def test_build_graph_signature_stable():
    m = importlib.import_module("generator.cli")
    sig = inspect.signature(m.build_graph)
    params = list(sig.parameters.values())
    assert [p.name for p in params] == ["rng", "num_nodes", "density"]
