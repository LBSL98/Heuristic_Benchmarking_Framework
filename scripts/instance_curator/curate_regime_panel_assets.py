"""Curate executable R2/R3 assets for the regime-panel benchmark gate."""

from __future__ import annotations

import argparse
import gzip
import json
import random
from collections import deque
from pathlib import Path

SCHEMA_VERSION = "1.1"
EPSILON = 50.0


def read_raw_undirected_graph(path: Path):
    nodes = set()
    edges = set()
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            u = int(parts[0])
            v = int(parts[1])
            if u == v:
                continue
            a, b = (u, v) if u < v else (v, u)
            edges.add((a, b))
            nodes.add(a)
            nodes.add(b)

    adj = {u: set() for u in nodes}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return nodes, edges, adj


def connected_components(adj: dict[int, set[int]]):
    seen = set()
    comps: list[list[int]] = []
    for s in sorted(adj):
        if s in seen:
            continue
        q = deque([s])
        seen.add(s)
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for v in sorted(adj[u]):
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    return comps


def induced_subgraph_from_nodes(node_list: list[int], adj: dict[int, set[int]]):
    chosen = set(node_list)
    old_to_new = {u: i for i, u in enumerate(node_list)}
    new_edges = []
    for u in node_list:
        for v in adj[u]:
            if v in chosen and u < v:
                new_edges.append([old_to_new[u], old_to_new[v]])
    new_edges.sort()
    return old_to_new, new_edges


def make_nodes_payload(n: int):
    nodes = []
    # deterministic compatibility attributes to satisfy the active input schema
    for i in range(n):
        velocity = 12.0
        pos = [float(i % 1000), float((i // 1000) % 1000)]
        nodes.append({"id": i, "velocity": velocity, "pos": pos})
    return nodes


def density(n: int, m: int) -> float:
    if n <= 1:
        return 0.0
    return (2.0 * m) / (n * (n - 1))


def write_instance(
    path: Path,
    *,
    n_req: int,
    n_final: int,
    edge_count: int,
    seed: int | None,
    edges: list[list[int]],
):
    d = density(n_final, edge_count)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "epsilon": EPSILON,
        "instance_metrics": {
            "nodes_requested": int(n_req),
            "nodes_final": int(n_final),
            "density_requested": float(d),
            "density_final": float(d),
            "cv_vel_requested": 0.0,
            "cv_vel_final": 0.0,
            "modularity": None,
            "seed": seed,
        },
        "nodes": make_nodes_payload(n_final),
        "edges": edges,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))


def bfs_slice_from_component(
    component: list[int], adj: dict[int, set[int]], *, target_n: int, seed: int
):
    if target_n > len(component):
        raise ValueError(f"target_n={target_n} exceeds component size={len(component)}")

    rng = random.Random(seed)
    ordered = sorted(component)
    root = ordered[rng.randrange(len(ordered))]

    seen = {root}
    q = deque([root])
    order = []

    while q and len(order) < target_n:
        u = q.popleft()
        order.append(u)
        for v in sorted(adj[u]):
            if v in seen:
                continue
            if v not in adj:
                continue
            seen.add(v)
            q.append(v)
            if len(order) + len(q) >= target_n and len(order) >= target_n:
                break

    if len(order) < target_n:
        raise RuntimeError(f"BFS slice stopped early: got {len(order)} < {target_n}")

    return order[:target_n], root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roadnet-raw", required=True)
    ap.add_argument("--hepth-raw", required=True)
    ap.add_argument("--astroph-raw", required=True)
    ap.add_argument("--roadnet-outdir", required=True)
    ap.add_argument("--snap-outdir", required=True)
    args = ap.parse_args()

    road_nodes, road_edges, road_adj = read_raw_undirected_graph(Path(args.roadnet_raw))
    road_comps = connected_components(road_adj)
    road_gcc = road_comps[0]

    hep_nodes, hep_edges, hep_adj = read_raw_undirected_graph(Path(args.hepth_raw))
    hep_comps = connected_components(hep_adj)
    hep_gcc = hep_comps[0]

    astro_nodes, astro_edges, astro_adj = read_raw_undirected_graph(Path(args.astroph_raw))
    astro_comps = connected_components(astro_adj)
    astro_gcc = astro_comps[0]

    road_out = Path(args.roadnet_outdir)
    snap_out = Path(args.snap_outdir)

    # R2 assets
    for target_n, seed, fname in [
        (10000, 42, "roadnet_ca_bfs_10000_seed42.json.gz"),
        (20000, 43, "roadnet_ca_bfs_20000_seed43.json.gz"),
    ]:
        subset, root = bfs_slice_from_component(road_gcc, road_adj, target_n=target_n, seed=seed)
        _, edges = induced_subgraph_from_nodes(subset, road_adj)
        write_instance(
            road_out / fname,
            n_req=target_n,
            n_final=len(subset),
            edge_count=len(edges),
            seed=seed,
            edges=edges,
        )
        print(
            json.dumps(
                {
                    "asset": fname,
                    "policy": "bfs_induced",
                    "seed": seed,
                    "root_original_id": root,
                    "n_final": len(subset),
                    "m_final": len(edges),
                },
                ensure_ascii=False,
            )
        )

    # R3 assets
    for component, fname, outdir in [
        (hep_gcc, "ca_hepth_gcc.json.gz", snap_out),
        (astro_gcc, "ca_astroph_gcc.json.gz", snap_out),
    ]:
        _, edges = induced_subgraph_from_nodes(
            sorted(component), hep_adj if "hepth" in fname else astro_adj
        )
        write_instance(
            outdir / fname,
            n_req=len(component),
            n_final=len(component),
            edge_count=len(edges),
            seed=None,
            edges=edges,
        )
        print(
            json.dumps(
                {
                    "asset": fname,
                    "policy": "gcc",
                    "n_final": len(component),
                    "m_final": len(edges),
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
