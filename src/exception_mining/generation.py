"""Auditable graph generation for multilevel exception mining.

This module implements the code side of
``EXP-MULTILEVEL-EXCEPTION-MINING-001``. It generates graph instances and
writes validator-compliant bundles, but it does not run solvers or make
performance claims.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import platform
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np

from hpc_framework.solvers.common import write_metis_graph

CAMPAIGN_ID = "EXP-MULTILEVEL-EXCEPTION-MINING-001"
SCHEMA_VERSION = "exception-mining-1.0"
GENERATOR_VERSION = "0.1.0"

REQUIRED_HASH_FILES = [
    "instance.json.gz",
    "generator_config.json",
    "generator_log.jsonl",
    "README.md",
    "graph_metrics.json",
    "manifest_row.json",
    "manifest_row.csv",
    "graph_edges.edgelist",
    "graph_metis.graph",
    "graph_preview_layout.json",
    "graph_preview_sample.json",
    "visualization_metadata.json",
]


@dataclass(frozen=True)
class GeneratedGraph:
    """In-memory representation of one generated exception-mining graph."""

    family: str
    graph: nx.Graph
    parameters: dict[str, Any]
    seed: int
    hypothesis: str
    generator_name: str
    planted_partition: dict[int, int] | None = None


def family_defaults(family: str) -> dict[str, Any]:
    """Return conservative default parameters for one topology family."""
    defaults: dict[str, dict[str, Any]] = {
        "F01": {
            "n": 160,
            "communities": 4,
            "target_avg_degree": 8,
            "mixing_mu": 0.15,
            "community_size_mode": "balanced",
            "epsilon": 0.03,
            "k": 8,
        },
        "F02": {
            "module_count": 8,
            "module_size": 20,
            "topology": "chain",
            "inter_module_edges": 2,
            "intra_module_density": 0.8,
            "epsilon": 0.03,
            "k": 8,
        },
        "F03": {
            "left_core_size": 80,
            "right_core_size": 80,
            "bridge_length": 12,
            "bridge_width": 2,
            "core_density": 0.3,
            "epsilon": 0.03,
            "k": 8,
        },
        "F04": {
            "n": 200,
            "attachment_m": 3,
            "hub_noise_edges": 0.03,
            "hub_bridge_mode": "single_hub_bridge",
            "epsilon": 0.03,
            "k": 8,
        },
        "F05": {
            "n": 200,
            "core_fraction": 0.25,
            "core_density": 0.3,
            "tree_attachment_mode": "hub_biased",
            "epsilon": 0.03,
            "k": 8,
        },
        "F06": {
            "grid_shape": "rectangular",
            "n_approx": 225,
            "shortcut_rate": 0.01,
            "perturbation_rate": 0.05,
            "epsilon": 0.03,
            "k": 8,
        },
        "F07": {
            "n": 160,
            "edge_density": 0.05,
            "planted_signal": 0.05,
            "noise_mode": "block_weak",
            "epsilon": 0.03,
            "k": 8,
        },
        "F08": {
            "n": 180,
            "planted_blocks": 5,
            "target_partition_k": 8,
            "block_size_skew": 0.25,
            "inter_block_noise": 0.15,
            "epsilon": 0.03,
            "k": 8,
        },
    }
    try:
        return dict(defaults[family])
    except KeyError as exc:
        known = ", ".join(sorted(defaults))
        raise ValueError(f"unknown family {family!r}; expected one of {known}") from exc


def generate_graph(
    family: str, seed: int, parameters: dict[str, Any] | None = None
) -> GeneratedGraph:
    """Generate a graph for one preregistered topology family."""
    merged = family_defaults(family)
    if parameters:
        merged.update(parameters)

    rng = np.random.default_rng(seed)

    generators = {
        "F01": _generate_modular_noise,
        "F02": _generate_chain_ring_modules,
        "F03": _generate_barbell_lollipop_bottleneck,
        "F04": _generate_hub_powerlaw,
        "F05": _generate_tree_dense_core,
        "F06": _generate_road_like_sparse,
        "F07": _generate_dense_weak_signal,
        "F08": _generate_balance_hard_planted,
    }

    graph = generators[family](rng, merged)
    graph = _canonical_graph(graph)
    planted = _extract_partition(graph)

    return GeneratedGraph(
        family=family,
        graph=graph,
        parameters=merged,
        seed=seed,
        hypothesis=_family_hypothesis(family),
        generator_name=f"exception_mining_{family.lower()}",
        planted_partition=planted,
    )


def write_bundle(
    generated: GeneratedGraph,
    output_root: Path,
    *,
    instance_id: str | None = None,
    campaign_id: str = CAMPAIGN_ID,
) -> Path:
    """Write a validator-compliant generated-instance bundle."""
    graph = _canonical_graph(generated.graph)
    n = graph.number_of_nodes()
    edges = _canonical_edges(graph)
    epsilon = float(generated.parameters.get("epsilon", 0.03))
    k = int(generated.parameters.get("k", generated.parameters.get("target_partition_k", 8)))

    final_instance_id = instance_id or _make_instance_id(
        generated.family, generated.seed, generated.parameters
    )
    bundle_dir = output_root / generated.family / final_instance_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).isoformat()
    metrics = _graph_metrics(graph)
    nodes = _node_payload(graph, generated.seed)

    instance_payload = {
        "schema_version": SCHEMA_VERSION,
        "epsilon": epsilon,
        "instance_id": final_instance_id,
        "generator": generated.generator_name,
        "seed": generated.seed,
        "created_at": now,
        "nodes": nodes,
        "edges": [list(edge) for edge in edges],
        "instance_metrics": metrics,
    }
    if generated.planted_partition is not None:
        instance_payload["planted_partition"] = {
            str(node): block for node, block in sorted(generated.planted_partition.items())
        }

    _write_json_gz(bundle_dir / "instance.json.gz", instance_payload)

    config = {
        "campaign_id": campaign_id,
        "instance_id": final_instance_id,
        "generator_family": generated.family,
        "generator_name": generated.generator_name,
        "graph_parameters": generated.parameters,
        "seed": generated.seed,
        "target_regime": "exception_mining",
        "target_morphology": generated.family,
        "intended_hypothesis": generated.hypothesis,
        "k": k,
        "balance_tolerance": epsilon,
        "code_commit": _git_commit(),
        "generator_version": GENERATOR_VERSION,
        "environment": _environment(),
        "created_at": now,
    }
    _write_json(bundle_dir / "generator_config.json", config)

    _write_generator_log(bundle_dir / "generator_log.jsonl", final_instance_id, generated, now)
    _write_readme(bundle_dir / "README.md", final_instance_id, generated, n, len(edges))
    _write_json(bundle_dir / "graph_metrics.json", metrics)
    _write_manifest(bundle_dir, campaign_id, final_instance_id, generated, now)
    _write_edgelist(bundle_dir / "graph_edges.edgelist", edges)
    write_metis_graph(bundle_dir / "graph_metis.graph", n, np.asarray(edges, dtype=np.int64))
    _write_preview_files(bundle_dir, graph, generated.seed)
    _write_hashes(bundle_dir)

    return bundle_dir


def generate_bundle(
    family: str,
    seed: int,
    output_root: Path,
    parameters: dict[str, Any] | None = None,
    *,
    instance_id: str | None = None,
) -> Path:
    """Generate one family graph and write its audit bundle."""
    generated = generate_graph(family=family, seed=seed, parameters=parameters)
    return write_bundle(generated, output_root, instance_id=instance_id)


def _canonical_graph(graph: nx.Graph) -> nx.Graph:
    graph = nx.Graph(graph)
    graph.remove_edges_from(nx.selfloop_edges(graph))
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    _connect_components(graph)
    return graph


def _canonical_edges(graph: nx.Graph) -> list[tuple[int, int]]:
    return sorted((min(int(u), int(v)), max(int(u), int(v))) for u, v in graph.edges())


def _connect_components(graph: nx.Graph) -> None:
    components = [sorted(component) for component in nx.connected_components(graph)]
    if len(components) <= 1:
        return
    reps = [component[0] for component in components]
    for left, right in zip(reps, reps[1:], strict=False):
        graph.add_edge(left, right)


def _family_hypothesis(family: str) -> str:
    hypotheses = {
        "F01": "Controlled modular signal with inter-community noise may stress multilevel coarsening.",
        "F02": "Dense modules linked by narrow boundaries may create many near-equivalent cuts.",
        "F03": "Asymmetric dense cores and bottlenecks may stress balance constraints.",
        "F04": "High-degree hubs may dominate contraction and refinement decisions.",
        "F05": "Dense cores with tree appendages may create cut/balance tension.",
        "F06": "Sparse road-like structure may expose low-density balance edge cases.",
        "F07": "Dense weak-signal graphs may reduce structural advantage for multilevel solvers.",
        "F08": "Planted structures conflicting with balance may make community recovery misleading.",
    }
    return hypotheses[family]


def _extract_partition(graph: nx.Graph) -> dict[int, int] | None:
    values = nx.get_node_attributes(graph, "planted_block")
    if not values:
        return None
    if set(values) != set(graph.nodes):
        return None
    return {int(node): int(block) for node, block in values.items()}


def _generate_modular_noise(rng: np.random.Generator, params: dict[str, Any]) -> nx.Graph:
    n = int(params["n"])
    communities = int(params["communities"])
    target_avg_degree = float(params["target_avg_degree"])
    mixing_mu = float(params["mixing_mu"])
    size_mode = str(params["community_size_mode"])

    sizes = _community_sizes(n, communities, size_mode, rng)
    avg_size = max(1.0, float(np.mean(sizes)))
    p_in = min(1.0, max(0.001, (1.0 - mixing_mu) * target_avg_degree / avg_size))
    p_out = min(1.0, max(0.0001, mixing_mu * target_avg_degree / max(1.0, n - avg_size)))

    probs = [
        [p_in if row == col else p_out for col in range(communities)] for row in range(communities)
    ]
    graph = nx.stochastic_block_model(sizes, probs, seed=int(rng.integers(0, 2**31 - 1)))
    _tag_blocks_by_sizes(graph, sizes)
    return graph


def _generate_chain_ring_modules(rng: np.random.Generator, params: dict[str, Any]) -> nx.Graph:
    module_count = int(params["module_count"])
    module_size = int(params["module_size"])
    topology = str(params["topology"])
    inter_edges = int(params["inter_module_edges"])
    density = float(params["intra_module_density"])

    graph = nx.Graph()
    for module in range(module_count):
        offset = module * module_size
        nodes = list(range(offset, offset + module_size))
        graph.add_nodes_from(nodes)
        local = nx.gnp_random_graph(
            module_size,
            min(1.0, max(0.0, density)),
            seed=int(rng.integers(0, 2**31 - 1)),
        )
        local = nx.convert_node_labels_to_integers(local, first_label=offset)
        graph.add_edges_from(local.edges())
        if module_size > 1:
            for left, right in zip(nodes, nodes[1:], strict=False):
                graph.add_edge(left, right)
        for node in nodes:
            graph.nodes[node]["planted_block"] = module

    pairs = [(i, i + 1) for i in range(module_count - 1)]
    if topology == "ring" and module_count > 2:
        pairs.append((module_count - 1, 0))

    for left_module, right_module in pairs:
        for index in range(inter_edges):
            left = left_module * module_size + index % module_size
            right = right_module * module_size + (index * 7) % module_size
            graph.add_edge(left, right)

    return graph


def _generate_barbell_lollipop_bottleneck(
    rng: np.random.Generator, params: dict[str, Any]
) -> nx.Graph:
    left_size = int(params["left_core_size"])
    right_size = int(params["right_core_size"])
    bridge_length = int(params["bridge_length"])
    bridge_width = int(params["bridge_width"])
    density = float(params["core_density"])

    graph = nx.Graph()
    left = nx.gnp_random_graph(left_size, density, seed=int(rng.integers(0, 2**31 - 1)))
    right = nx.gnp_random_graph(right_size, density, seed=int(rng.integers(0, 2**31 - 1)))
    right = nx.convert_node_labels_to_integers(right, first_label=left_size)

    graph.add_edges_from(left.edges())
    graph.add_edges_from(right.edges())
    graph.add_nodes_from(range(left_size + right_size + bridge_width * bridge_length))

    bridge_start = left_size + right_size
    for width in range(bridge_width):
        previous = width % left_size
        for step in range(bridge_length):
            current = bridge_start + width * bridge_length + step
            graph.add_edge(previous, current)
            previous = current
        graph.add_edge(previous, left_size + (width % right_size))

    for node in range(left_size):
        graph.nodes[node]["planted_block"] = 0
    for node in range(left_size, left_size + right_size):
        graph.nodes[node]["planted_block"] = 1

    return graph


def _generate_hub_powerlaw(rng: np.random.Generator, params: dict[str, Any]) -> nx.Graph:
    n = int(params["n"])
    attachment_m = max(1, int(params["attachment_m"]))
    noise_fraction = float(params["hub_noise_edges"])
    bridge_mode = str(params["hub_bridge_mode"])

    graph = nx.barabasi_albert_graph(
        n, min(attachment_m, n - 1), seed=int(rng.integers(0, 2**31 - 1))
    )
    _add_random_edges(graph, int(noise_fraction * n), rng)

    hubs = [
        node for node, _degree in sorted(graph.degree, key=lambda item: item[1], reverse=True)[:4]
    ]
    if bridge_mode == "single_hub_bridge" and len(hubs) >= 2:
        graph.add_edge(hubs[0], hubs[1])
    elif bridge_mode == "multi_hub_bridge":
        for left, right in zip(hubs, hubs[1:], strict=False):
            graph.add_edge(left, right)

    return graph


def _generate_tree_dense_core(rng: np.random.Generator, params: dict[str, Any]) -> nx.Graph:
    n = int(params["n"])
    core_fraction = float(params["core_fraction"])
    core_density = float(params["core_density"])
    attachment_mode = str(params["tree_attachment_mode"])
    core_n = max(2, min(n - 1, int(round(n * core_fraction))))

    graph = nx.gnp_random_graph(core_n, core_density, seed=int(rng.integers(0, 2**31 - 1)))
    if graph.number_of_edges() == 0:
        for left, right in zip(range(core_n - 1), range(1, core_n), strict=False):
            graph.add_edge(left, right)

    for node in range(core_n, n):
        if attachment_mode == "hub_biased":
            degrees = np.array([graph.degree[target] + 1 for target in graph.nodes], dtype=float)
            probs = degrees / degrees.sum()
            parent = int(rng.choice(list(graph.nodes), p=probs))
        else:
            parent = int(rng.choice(list(graph.nodes)))
        graph.add_node(node)
        graph.add_edge(parent, node)

    for node in range(core_n):
        graph.nodes[node]["planted_block"] = 0
    return graph


def _generate_road_like_sparse(rng: np.random.Generator, params: dict[str, Any]) -> nx.Graph:
    n_approx = int(params["n_approx"])
    shape = str(params["grid_shape"])
    shortcut_rate = float(params["shortcut_rate"])
    perturbation_rate = float(params["perturbation_rate"])

    rows, cols = _grid_dimensions(n_approx, shape)
    graph = nx.grid_2d_graph(rows, cols)
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    target_n = min(n_approx, graph.number_of_nodes())
    if target_n < graph.number_of_nodes():
        graph = graph.subgraph(range(target_n)).copy()

    _add_random_edges(graph, int(shortcut_rate * max(1, graph.number_of_edges())), rng)

    removable = list(graph.edges())
    rng.shuffle(removable)
    remove_target = int(perturbation_rate * len(removable))
    removed = 0
    for edge in removable:
        if removed >= remove_target:
            break
        graph.remove_edge(*edge)
        if nx.is_connected(graph):
            removed += 1
        else:
            graph.add_edge(*edge)

    return graph


def _generate_dense_weak_signal(rng: np.random.Generator, params: dict[str, Any]) -> nx.Graph:
    n = int(params["n"])
    density = float(params["edge_density"])
    signal = float(params["planted_signal"])
    mode = str(params["noise_mode"])

    if mode == "block_weak" and signal > 0:
        blocks = 4
        sizes = _community_sizes(n, blocks, "balanced", rng)
        p_in = min(1.0, density + signal)
        p_out = max(0.0001, density - signal / 2.0)
        probs = [[p_in if i == j else p_out for j in range(blocks)] for i in range(blocks)]
        graph = nx.stochastic_block_model(sizes, probs, seed=int(rng.integers(0, 2**31 - 1)))
        _tag_blocks_by_sizes(graph, sizes)
        return graph

    return nx.gnp_random_graph(n, density, seed=int(rng.integers(0, 2**31 - 1)))


def _generate_balance_hard_planted(rng: np.random.Generator, params: dict[str, Any]) -> nx.Graph:
    n = int(params["n"])
    blocks = int(params["planted_blocks"])
    skew = float(params["block_size_skew"])
    noise = float(params["inter_block_noise"])

    sizes = _skewed_sizes(n, blocks, skew)
    avg_size = max(1.0, float(np.mean(sizes)))
    p_in = min(1.0, 8.0 / avg_size)
    p_out = min(1.0, max(0.0001, noise * 8.0 / max(1.0, n - avg_size)))
    probs = [[p_in if i == j else p_out for j in range(blocks)] for i in range(blocks)]

    graph = nx.stochastic_block_model(sizes, probs, seed=int(rng.integers(0, 2**31 - 1)))
    _tag_blocks_by_sizes(graph, sizes)
    return graph


def _community_sizes(n: int, communities: int, mode: str, rng: np.random.Generator) -> list[int]:
    if communities <= 0:
        raise ValueError("communities must be positive")
    if mode == "mildly_imbalanced":
        weights = rng.uniform(0.75, 1.25, size=communities)
        raw = weights / weights.sum() * n
        sizes = [max(1, int(round(value))) for value in raw]
        return _fix_sizes(sizes, n)

    base = n // communities
    sizes = [base for _ in range(communities)]
    for index in range(n - sum(sizes)):
        sizes[index % communities] += 1
    return sizes


def _skewed_sizes(n: int, blocks: int, skew: float) -> list[int]:
    if blocks <= 0:
        raise ValueError("blocks must be positive")
    weights = np.array([(1.0 + skew) ** index for index in range(blocks)], dtype=float)
    raw = weights / weights.sum() * n
    sizes = [max(1, int(round(value))) for value in raw]
    return _fix_sizes(sizes, n)


def _fix_sizes(sizes: list[int], target: int) -> list[int]:
    while sum(sizes) < target:
        sizes[int(np.argmin(sizes))] += 1
    while sum(sizes) > target:
        index = int(np.argmax(sizes))
        if sizes[index] <= 1:
            break
        sizes[index] -= 1
    return sizes


def _tag_blocks_by_sizes(graph: nx.Graph, sizes: list[int]) -> None:
    offset = 0
    for block, size in enumerate(sizes):
        for node in range(offset, offset + size):
            graph.nodes[node]["planted_block"] = block
        offset += size


def _grid_dimensions(n_approx: int, shape: str) -> tuple[int, int]:
    side = max(2, int(round(math.sqrt(n_approx))))
    if shape == "square":
        return side, side
    if shape == "corridor":
        rows = max(2, side // 3)
        cols = max(2, math.ceil(n_approx / rows))
        return rows, cols
    rows = max(2, int(round(math.sqrt(n_approx / 2))))
    cols = max(2, math.ceil(n_approx / rows))
    return rows, cols


def _add_random_edges(graph: nx.Graph, count: int, rng: np.random.Generator) -> None:
    nodes = list(graph.nodes)
    if len(nodes) < 2 or count <= 0:
        return
    added = 0
    attempts = 0
    max_attempts = max(100, count * 50)
    while added < count and attempts < max_attempts:
        u, v = rng.choice(nodes, size=2, replace=False)
        left = int(u)
        right = int(v)
        attempts += 1
        if left == right or graph.has_edge(left, right):
            continue
        graph.add_edge(left, right)
        added += 1


def _graph_metrics(graph: nx.Graph) -> dict[str, Any]:
    n = graph.number_of_nodes()
    m = graph.number_of_edges()
    degrees = np.array([degree for _node, degree in graph.degree()], dtype=float)
    degree_mean = float(degrees.mean()) if n else 0.0
    degree_std = float(degrees.std()) if n else 0.0
    components = [len(component) for component in nx.connected_components(graph)]

    density = 0.0 if n <= 1 else float((2.0 * m) / (n * (n - 1)))
    degree_cv = 0.0 if degree_mean == 0 else degree_std / degree_mean

    metrics = {
        "num_vertices": n,
        "num_edges": m,
        "density": density,
        "average_degree": degree_mean,
        "degree_min": int(degrees.min()) if n else 0,
        "degree_max": int(degrees.max()) if n else 0,
        "degree_mean": degree_mean,
        "degree_std": degree_std,
        "degree_cv": degree_cv,
        "connected_component_count": len(components),
        "largest_component_size": max(components) if components else 0,
        "nodes_final": n,
        "nodes_requested": n,
        "density_final": density,
        "density_requested": density,
        "cv_vel_final": 0.0,
        "cv_vel_requested": 0.0,
        "modularity": _safe_modularity(graph),
    }
    return metrics


def _safe_modularity(graph: nx.Graph) -> float | None:
    planted = _extract_partition(graph)
    if not planted:
        return None
    communities: dict[int, set[int]] = {}
    for node, block in planted.items():
        communities.setdefault(block, set()).add(node)
    try:
        return float(nx.algorithms.community.quality.modularity(graph, communities.values()))
    except ZeroDivisionError:
        return None


def _node_payload(graph: nx.Graph, seed: int) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    n = graph.number_of_nodes()
    payload = []
    for node in range(n):
        angle = (2.0 * math.pi * node) / max(1, n)
        payload.append(
            {
                "id": node,
                "velocity": float(8.0 + rng.random() * 8.0),
                "pos": [float(math.cos(angle)), float(math.sin(angle))],
            }
        )
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_json_gz(path: Path, payload: dict[str, Any]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, sort_keys=True)


def _write_generator_log(
    path: Path, instance_id: str, generated: GeneratedGraph, created_at: str
) -> None:
    entries = [
        {
            "event": "generated",
            "status": "ok",
            "lifecycle_state": "generated",
            "instance_id": instance_id,
            "family": generated.family,
            "seed": generated.seed,
            "created_at": created_at,
        },
        {
            "event": "bundle_written",
            "status": "ok",
            "lifecycle_state": "generated",
            "instance_id": instance_id,
            "required_files": REQUIRED_HASH_FILES,
        },
    ]
    path.write_text(
        "\n".join(json.dumps(entry, ensure_ascii=False, sort_keys=True) for entry in entries)
        + "\n",
        encoding="utf-8",
    )


def _write_readme(path: Path, instance_id: str, generated: GeneratedGraph, n: int, m: int) -> None:
    path.write_text(
        "\n".join(
            [
                f"# {instance_id}",
                "",
                f"Generator: `{generated.generator_name}`.",
                f"Topology family: `{generated.family}`.",
                f"Seed: `{generated.seed}`.",
                f"Graph size: `{n}` vertices and `{m}` undirected edges.",
                "",
                "Hypothesis:",
                generated.hypothesis,
                "",
                "This bundle is an auditable generated instance for exception mining. It is not a solver result.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_manifest(
    bundle_dir: Path,
    campaign_id: str,
    instance_id: str,
    generated: GeneratedGraph,
    created_at: str,
) -> None:
    row = {
        "campaign_id": campaign_id,
        "instance_id": instance_id,
        "family": generated.family,
        "seed": str(generated.seed),
        "lifecycle_state": "generated",
        "bundle_path": str(bundle_dir),
        "created_at": created_at,
    }
    _write_json(bundle_dir / "manifest_row.json", row)

    with (bundle_dir / "manifest_row.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


def _write_edgelist(path: Path, edges: list[tuple[int, int]]) -> None:
    path.write_text("".join(f"{u} {v}\n" for u, v in edges), encoding="utf-8")


def _write_preview_files(
    bundle_dir: Path, graph: nx.Graph, seed: int, max_nodes: int = 500
) -> None:
    n = graph.number_of_nodes()
    rng = np.random.default_rng(seed)
    if n <= max_nodes:
        sampled_nodes = list(range(n))
        policy = "full_graph"
    else:
        sampled_nodes = sorted(
            int(node) for node in rng.choice(list(graph.nodes), size=max_nodes, replace=False)
        )
        policy = "uniform_node_sample"

    sampled_set = set(sampled_nodes)
    sampled_edges = [
        [int(u), int(v)]
        for u, v in _canonical_edges(graph)
        if u in sampled_set and v in sampled_set
    ]

    positions = {}
    for index, node in enumerate(sampled_nodes):
        angle = (2.0 * math.pi * index) / max(1, len(sampled_nodes))
        positions[str(node)] = [float(math.cos(angle)), float(math.sin(angle))]

    _write_json(
        bundle_dir / "graph_preview_layout.json",
        {
            "layout_algorithm": "deterministic_circle",
            "layout_seed": seed,
            "layout_parameters": {"max_nodes": max_nodes},
            "layout_scope": "full" if n <= max_nodes else "sample",
            "node_positions": positions,
        },
    )
    _write_json(
        bundle_dir / "graph_preview_sample.json",
        {
            "sampling_policy": policy,
            "sample_seed": seed,
            "sampled_nodes": sampled_nodes,
            "sampled_edges": sampled_edges,
        },
    )
    _write_json(
        bundle_dir / "visualization_metadata.json",
        {
            "available_encodings": [
                "degree",
                "connected_component_id",
                "planted_block",
                "solver_partition",
            ],
            "layout_file": "graph_preview_layout.json",
            "sample_file": "graph_preview_sample.json",
            "notes": "Preview artifacts are illustrative inputs for the later visualization pipeline.",
        },
    )


def _write_hashes(bundle_dir: Path) -> None:
    lines = []
    for filename in REQUIRED_HASH_FILES:
        path = bundle_dir / filename
        lines.append(f"{_sha256(path)}  {filename}")
    (bundle_dir / "sha256sums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _make_instance_id(family: str, seed: int, parameters: dict[str, Any]) -> str:
    relevant = {
        key: parameters[key]
        for key in sorted(parameters)
        if key not in {"epsilon", "k", "target_partition_k"}
    }
    digest = hashlib.sha256(json.dumps(relevant, sort_keys=True).encode("utf-8")).hexdigest()[:10]
    return f"{family.lower()}_seed{seed}_{digest}"


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _environment() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "networkx": nx.__version__,
        "numpy": np.__version__,
    }
