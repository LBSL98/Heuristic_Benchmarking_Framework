#!/usr/bin/env python3
"""Prepare the OGB ogbn-arxiv undirected projection from raw CSV files.

This script is intentionally conservative. It can acquire/cache OGB data only
when explicitly requested, but the projection itself reads the raw CSV files and
does not use torch.load or the OGB processed pickle cache.

The output is a local validation artifact and is not an M4 benchmark admission.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import platform
import socket
import time
import zipfile
from pathlib import Path
from typing import Any

FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def utc_now_iso() -> str:
    """Return a Python 3.10-compatible UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path) -> str:
    """Return the SHA256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a stable, human-readable JSON file."""
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def require_local_ignored_output(path: Path) -> None:
    """Reject outputs outside the repository local ignored data/tmp area."""
    resolved = path.resolve()
    data_tmp = Path("data/tmp").resolve()
    if data_tmp not in resolved.parents and resolved != data_tmp:
        raise SystemExit(f"ERROR: output path must be under ignored data/tmp, got: {path}")


def read_num_nodes(path: Path) -> int:
    """Read the single node-count value from OGB num-node-list.csv.gz."""
    values: list[int] = []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            for cell in row:
                cell = cell.strip()
                if cell:
                    values.append(int(cell))

    if len(values) != 1:
        raise SystemExit(f"ERROR: expected one num_nodes value in {path}, got {values}")
    return values[0]


def read_edges(path: Path):
    """Read directed edges from OGB edge.csv.gz as an int64 NumPy array."""
    import numpy as np

    rows: list[tuple[int, int]] = []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            if len(row) < 2:
                raise SystemExit(f"ERROR: malformed edge row: {row}")
            rows.append((int(row[0]), int(row[1])))

    if not rows:
        raise SystemExit(f"ERROR: no edges read from {path}")

    return np.asarray(rows, dtype=np.int64)


def deterministic_npz(path: Path, arrays: dict[str, Any]) -> None:
    """Write a deterministic NPZ-like ZIP file with fixed member timestamps."""
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(arrays):
            buffer = io.BytesIO()
            np.save(buffer, arrays[name], allow_pickle=False)

            info = zipfile.ZipInfo(filename=f"{name}.npy")
            info.date_time = FIXED_ZIP_TIMESTAMP
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, buffer.getvalue())


def acquire_if_missing(root: Path, edge_path: Path, num_nodes_path: Path) -> None:
    """Acquire OGB data only when explicitly requested by the caller."""
    if edge_path.exists() and num_nodes_path.exists():
        return

    from ogb.nodeproppred import NodePropPredDataset

    NodePropPredDataset(name="ogbn-arxiv", root=str(root))


def raw_inventory(root: Path) -> list[dict[str, Any]]:
    """Build a SHA256 inventory for files under the OGB root."""
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        records.append(
            {
                "relative_path": path.relative_to(root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return records


def project_edges(edges, num_nodes: int) -> dict[str, Any]:
    """Convert directed edges into an undirected simple graph by union."""
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    if edges.ndim != 2 or edges.shape[1] != 2:
        raise SystemExit(f"ERROR: unexpected edge array shape: {edges.shape}")

    src = edges[:, 0]
    dst = edges[:, 1]

    if int(src.min()) < 0 or int(dst.min()) < 0:
        raise SystemExit("ERROR: negative node id found")
    if int(src.max()) >= num_nodes or int(dst.max()) >= num_nodes:
        raise SystemExit("ERROR: node id exceeds num_nodes")

    directed_edge_count = int(edges.shape[0])
    self_loop_mask = src == dst
    self_loop_count = int(self_loop_mask.sum())

    src2 = src[~self_loop_mask]
    dst2 = dst[~self_loop_mask]

    u = np.minimum(src2, dst2)
    v = np.maximum(src2, dst2)
    pairs = np.stack([u, v], axis=1)

    order = np.lexsort((pairs[:, 1], pairs[:, 0]))
    pairs_sorted = pairs[order]
    pairs_unique = np.unique(pairs_sorted, axis=0)

    if pairs_unique.ndim != 2 or pairs_unique.shape[1] != 2:
        raise SystemExit("ERROR: unexpected projected edge array shape")
    if pairs_unique.size and not np.all(pairs_unique[:, 0] < pairs_unique[:, 1]):
        raise SystemExit("ERROR: projected edges must satisfy u < v")

    undirected_edge_count = int(pairs_unique.shape[0])
    duplicate_or_reciprocal_removed = int(pairs.shape[0] - undirected_edge_count)

    if undirected_edge_count:
        row = np.concatenate([pairs_unique[:, 0], pairs_unique[:, 1]])
        col = np.concatenate([pairs_unique[:, 1], pairs_unique[:, 0]])
    else:
        row = np.array([], dtype=np.int64)
        col = np.array([], dtype=np.int64)

    data = np.ones(row.shape[0], dtype=np.int8)
    adjacency = coo_matrix((data, (row, col)), shape=(num_nodes, num_nodes)).tocsr()
    n_components, labels = connected_components(adjacency, directed=False, return_labels=True)
    component_sizes = np.bincount(labels, minlength=n_components)
    largest_component_size = int(component_sizes.max()) if component_sizes.size else 0
    isolated_vertices = int((component_sizes[labels] == 1).sum()) if labels.size else 0

    return {
        "edges": pairs_unique.astype(np.int64, copy=False),
        "counts": {
            "num_nodes": num_nodes,
            "directed_edge_count": directed_edge_count,
            "self_loop_count_removed": self_loop_count,
            "directed_edges_after_self_loop_removal": int(pairs.shape[0]),
            "undirected_union_edge_count": undirected_edge_count,
            "duplicate_or_reciprocal_directed_edges_removed_by_projection": (
                duplicate_or_reciprocal_removed
            ),
            "connected_components": int(n_components),
            "largest_component_size": largest_component_size,
            "isolated_vertices": isolated_vertices,
        },
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Prepare ogbn-arxiv undirected projection from raw CSV files."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/tmp/real_graph_m3_smoke/ogbn_arxiv/raw"),
        help="OGB root used for the controlled local cache.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Local ignored output directory under data/tmp.",
    )
    parser.add_argument(
        "--acquire-if-missing",
        action="store_true",
        help="Instantiate OGB only if raw CSV files are missing.",
    )
    parser.add_argument(
        "--require-host",
        default="srv-noctua",
        help="Host required for real-graph preparation.",
    )
    parser.add_argument(
        "--allow-non-noctua",
        action="store_true",
        help="Allow non-srv-noctua execution for explicitly documented exceptions.",
    )
    parser.add_argument("--expected-num-nodes", type=int, default=169343)
    parser.add_argument("--expected-directed-edges", type=int, default=1166243)
    parser.add_argument("--expected-undirected-edges", type=int, default=1157799)
    parser.add_argument("--expected-connected-components", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    """Run the conservative raw-CSV projection workflow."""
    import numpy as np

    args = parse_args()

    host = socket.gethostname()
    if (
        host != args.require_host
        and not args.allow_non_noctua
        and os.environ.get("ALLOW_NON_NOCTUA_REALGRAPH_EXECUTION") != "1"
    ):
        raise SystemExit(f"ERROR: expected host {args.require_host}, got {host}")

    require_local_ignored_output(args.output_dir)

    edge_path = args.root / "ogbn_arxiv/raw/edge.csv.gz"
    num_nodes_path = args.root / "ogbn_arxiv/raw/num-node-list.csv.gz"

    if args.acquire_if_missing:
        acquire_if_missing(args.root, edge_path, num_nodes_path)

    if not edge_path.exists():
        raise SystemExit(f"ERROR: missing raw edge file: {edge_path}")
    if not num_nodes_path.exists():
        raise SystemExit(f"ERROR: missing raw num-node file: {num_nodes_path}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    num_nodes = read_num_nodes(num_nodes_path)
    edges = read_edges(edge_path)
    projection = project_edges(edges, num_nodes)
    counts = projection["counts"]

    expected = {
        "num_nodes": args.expected_num_nodes,
        "directed_edge_count": args.expected_directed_edges,
        "undirected_union_edge_count": args.expected_undirected_edges,
        "connected_components": args.expected_connected_components,
    }
    for key, expected_value in expected.items():
        actual = counts[key]
        if actual != expected_value:
            raise SystemExit(f"ERROR: unexpected {key}: expected {expected_value}, got {actual}")

    artifact_path = args.output_dir / "ogbn_arxiv_undirected_union_edges_raw_csv_deterministic.npz"
    metadata_path = args.output_dir / "ogbn_arxiv_projection_metadata.json"
    raw_inventory_path = args.output_dir / "ogbn_arxiv_raw_inventory.json"

    deterministic_npz(
        artifact_path,
        {
            "edges": projection["edges"],
            "num_nodes": np.asarray([num_nodes], dtype=np.int64),
        },
    )

    inventory = raw_inventory(args.root)
    write_json(raw_inventory_path, {"root": str(args.root), "files": inventory})

    metadata = {
        "dataset_id": "ogbn_arxiv_undirected_projection",
        "prepared_at_utc": utc_now_iso(),
        "host": host,
        "platform": platform.platform(),
        "raw_root": str(args.root),
        "edge_source": str(edge_path),
        "num_nodes_source": str(num_nodes_path),
        "edge_source_sha256": sha256_file(edge_path),
        "num_nodes_source_sha256": sha256_file(num_nodes_path),
        "artifact_path": str(artifact_path),
        "artifact_sha256": sha256_file(artifact_path),
        "raw_inventory_path": str(raw_inventory_path),
        "raw_inventory_sha256": sha256_file(raw_inventory_path),
        "projection_from_raw_csv": True,
        "used_torch_load": False,
        "used_ogb_processed_cache_for_projection": False,
        "m4_benchmark_admitted": False,
        "benchmark_run": False,
        "cart_training_run": False,
        "redistribution_allowed": False,
        "derived_graph_scope": "local_ignored_validation_artifact_not_benchmark_input",
        "counts": counts,
        "guardrails": [
            "The output is local-only under ignored data/tmp.",
            "The output is not admitted to M4 benchmark execution.",
            "No benchmark campaign is run by this script.",
            "No CART training is run by this script.",
            "No raw or derived data redistribution is authorized.",
        ],
    }
    write_json(metadata_path, metadata)

    print(
        json.dumps(
            {
                "artifact_path": str(artifact_path),
                "artifact_sha256": metadata["artifact_sha256"],
                "metadata_path": str(metadata_path),
                "counts": counts,
                "projection_from_raw_csv": True,
                "used_torch_load": False,
                "m4_benchmark_admitted": False,
                "benchmark_run": False,
                "cart_training_run": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
