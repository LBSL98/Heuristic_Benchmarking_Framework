"""Orquestrador single-run para METIS/KaHIP/SA.
Usado pelos testes e pelo CLI para exportar .graph, invocar o solver e salvar artefatos/JSON.
"""

from __future__ import annotations

import gzip
import json
import logging
import math
import os
import platform
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from heuristics.grasp import GRASPConfig, run_grasp_partition
from heuristics.ils import ILSConfig, run_ils_partition
from heuristics.sa import SAConfig, run_sa_partition
from heuristics.ts import TSConfig, run_ts_partition
from hpc_framework.ils_rust_adapter import run_ils_rust_binary
from hpc_framework.sa_rust_adapter import run_sa_rust_binary
from hpc_framework.solvers.common import read_partition_labels, write_metis_graph
from hpc_framework.solvers.kahip import run_kaffpa
from hpc_framework.solvers.metis import run_gpmetis
from hpc_framework.ts_rust_adapter import run_ts_rust_binary, ts_rust_available


def compute_cutsize_edges_labels(edges: np.ndarray, labels: np.ndarray) -> int:
    """Cutsize: número de arestas que cruzam partições (labels diferentes)."""
    if edges.ndim != 2 or edges.shape[1] != 2:
        raise ValueError("edges must be an (m,2) array")
    u = labels[edges[:, 0]]
    v = labels[edges[:, 1]]
    return int(np.count_nonzero(u != v))


def normalize_labels_zero_based(labels: np.ndarray) -> np.ndarray:
    """Normaliza rótulos para começarem em 0 (mantendo o particionamento)."""
    lab_min = int(labels.min())
    return (labels - lab_min).astype(int, copy=False)


def feasible_beta(labels: np.ndarray, k: int, beta: float) -> tuple[bool, dict]:
    """Checa restrição de balanceamento para k-partições com folga β."""
    n = labels.shape[0]
    counts = np.bincount(labels, minlength=k)
    max_allowed = math.ceil((1.0 + beta) * n / k)
    ok = bool(np.all(counts <= max_allowed))
    return ok, {"counts": counts.tolist(), "max_allowed": max_allowed}


def extract_graph_from_instance(inst: dict[str, Any]) -> tuple[int, np.ndarray]:
    """Extrai (n, edges) de uma instância.

    Suporta tanto instâncias com campos na raiz quanto instâncias
    no formato sintético atual, com chaves:
      - schema_version, epsilon, instance_metrics, nodes, edges
    """
    # 1) Se existir um sub-bloco óbvio de grafo, usa ele; senão, usa a raiz.
    graph = inst.get("graph") or inst

    # 2) Descobrir n:
    #    (a) Se vier explícito (n, num_nodes, ...) usa.
    #    (b) Se não vier, mas houver 'nodes', usa len(nodes).
    n_raw: Any | None = (
        graph.get("n")
        or graph.get("num_nodes")
        or graph.get("numVertices")
        or graph.get("num_nodes_v1_1")
        or graph.get("n_vertices")
        or graph.get("nNodes")
    )

    if n_raw is not None:
        n = int(n_raw)
    elif "nodes" in graph:
        # Formato sintético atual: lista de nós + lista de arestas
        n = len(graph["nodes"])
    else:
        raise KeyError(
            f"instance missing 'n'/'num_nodes' and no 'nodes' array "
            f"(keys disponíveis: {list(graph.keys())})"
        )

    # 3) Arestras: no seu schema já existe 'edges'
    edges = (
        graph.get("edges")
        or graph.get("edge_list")
        or graph.get("edgeIndex")
        or graph.get("edge_index")
    )
    if edges is None:
        raise KeyError(f"instance missing 'edges' (keys disponíveis: {list(graph.keys())})")

    edges_arr = np.asarray(edges, dtype=np.int64)
    if edges_arr.ndim != 2 or edges_arr.shape[1] != 2:
        raise ValueError("edges must be an (m,2) list/array of endpoints")
    return n, edges_arr


def _adj_from_edges(n: int, edges: np.ndarray) -> dict[int, set[int]]:
    """Build an undirected adjacency map from an edge array."""
    adj: dict[int, set[int]] = {i: set() for i in range(int(n))}
    for u, v in edges:
        ui = int(u)
        vi = int(v)
        if ui == vi:
            continue
        adj[ui].add(vi)
        adj[vi].add(ui)
    return adj


def _labels_from_part_of(part_of: dict[int, int], n: int) -> np.ndarray:
    """Convert a part-of mapping into a dense labels array."""
    return np.asarray([int(part_of[i]) for i in range(int(n))], dtype=int)


def _read_instance(p: Path) -> dict[str, Any]:
    """Lê JSON (possivelmente .gz) de instância."""
    if str(p).endswith(".gz"):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            return json.load(f)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class RunArtifact:
    """Resumo estruturado de um run único (para consumo programático)."""

    run_id: str
    algo: str
    status: str
    cut: int | None
    elapsed_ms: int
    part_file: Path | None


def run(
    *,
    instance_path: Path,
    algo: str,
    k: int,
    beta: float,
    seed: int,
    budget_time_ms: int,
    out_json: Path,
    workdir: Path,
    kahip_preset: str = "fast",
    log_level: str = "info",
) -> RunArtifact:
    """Executa um único run end-to-end e persiste JSON de saída."""
    # logging mínimo (compat)
    level = getattr(logging, (log_level or "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level, stream=sys.stdout, format="[%(levelname)s] %(message)s")

    inst = _read_instance(instance_path)
    n, edges = extract_graph_from_instance(inst)

    # Snapshot do ambiente e versões para auditoria
    env_info = _env_snapshot()
    tool_info = {
        "gpmetis": {
            "exists": bool(_which("gpmetis")),
            "version": _tool_version(["gpmetis"]) if _which("gpmetis") else "",
        },
        "kaffpa": {
            "exists": bool(_which("kaffpa")),
            "version": _tool_version(["kaffpa"]) if _which("kaffpa") else "",
        },
        "ts_rust": {
            "exists": bool(ts_rust_available()),
            "version": _tool_version(["cargo"]) if _which("cargo") else "",
        },
    }

    workdir.mkdir(parents=True, exist_ok=True)
    graph_path = workdir / "graph.graph"
    write_metis_graph(graph_path, n, edges)

    # Medição de parede local (overhead do Python incluído) para debug
    t0_wall = time.perf_counter()

    stdout = ""
    stderr = ""
    returncode: int | None = 0
    part_file: Path | None = None
    labels: np.ndarray | None = None
    checkpoints: list[dict[str, int | None]] = []
    cut: int | None = None
    feasible = None
    validation = None

    if algo == "sa":
        adj = _adj_from_edges(n, edges)
        sa_result = run_sa_partition(
            adj,
            k=k,
            epsilon=beta,
            config=SAConfig(
                seed=seed,
                budget_time_ms=budget_time_ms,
            ),
        )
        elapsed_wall = int((time.perf_counter() - t0_wall) * 1000)
        solver_elapsed_ms = (
            int(sa_result.elapsed_ms) if sa_result.elapsed_ms is not None else elapsed_wall
        )

        labels = _labels_from_part_of(sa_result.best_part_of, n)
        cut = int(sa_result.best_cutsize)

        part_file = workdir / "sa.part"
        part_file.write_text(
            "".join(f"{int(label)}\n" for label in labels.tolist()), encoding="utf-8"
        )

        labels_norm = normalize_labels_zero_based(labels)
        feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)
        status_json = sa_result.status
        checkpoints = [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in sa_result.checkpoints
        ]
    elif algo == "sa_rust":
        rust_json = workdir / "sa_rust_result.json"
        part_file = workdir / "sa_rust.part"
        sa_rust_result = run_sa_rust_binary(
            graph_path=graph_path,
            k=k,
            beta=beta,
            seed=seed,
            budget_time_ms=budget_time_ms,
            out_json=rust_json,
            part_path=part_file,
        )
        sa_payload = sa_rust_result.payload

        stdout = sa_rust_result.stdout
        stderr = sa_rust_result.stderr
        returncode = sa_rust_result.returncode
        solver_elapsed_ms = int(sa_payload["elapsed_ms"])

        labels = np.asarray(sa_payload["labels"], dtype=int)
        cut = int(sa_payload["cutsize_best"])

        labels_norm = normalize_labels_zero_based(labels)
        feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)
        status_json = str(sa_payload.get("status", "ok"))
        checkpoints = [
            {
                "time_ms": int(cp["time_ms"]),
                "cutsize_best": int(cp["cutsize_best"]),
                "nfe": int(cp["nfe"]) if cp.get("nfe") is not None else None,
            }
            for cp in sa_payload.get("checkpoints", [])
        ]
    elif algo == "grasp":
        adj = _adj_from_edges(n, edges)
        grasp_result = run_grasp_partition(
            adj,
            k=k,
            epsilon=beta,
            config=GRASPConfig(
                seed=seed,
                budget_time_ms=budget_time_ms,
            ),
        )
        elapsed_wall = int((time.perf_counter() - t0_wall) * 1000)
        solver_elapsed_ms = (
            int(grasp_result.elapsed_ms) if grasp_result.elapsed_ms is not None else elapsed_wall
        )

        labels = _labels_from_part_of(grasp_result.best_part_of, n)
        cut = int(grasp_result.best_cutsize)

        part_file = workdir / "grasp.part"
        part_file.write_text(
            "".join(f"{int(label)}\n" for label in labels.tolist()), encoding="utf-8"
        )

        labels_norm = normalize_labels_zero_based(labels)
        feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)
        status_json = grasp_result.status
        checkpoints = [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in grasp_result.checkpoints
        ]
    elif algo == "ts":
        adj = _adj_from_edges(n, edges)
        ts_result = run_ts_partition(
            adj,
            k=k,
            epsilon=beta,
            config=TSConfig(
                seed=seed,
                budget_time_ms=budget_time_ms,
            ),
        )
        elapsed_wall = int((time.perf_counter() - t0_wall) * 1000)
        solver_elapsed_ms = (
            int(ts_result.elapsed_ms) if ts_result.elapsed_ms is not None else elapsed_wall
        )

        labels = _labels_from_part_of(ts_result.best_part_of, n)
        cut = int(ts_result.best_cutsize)

        part_file = workdir / "ts.part"
        part_file.write_text(
            "".join(f"{int(label)}\n" for label in labels.tolist()), encoding="utf-8"
        )

        labels_norm = normalize_labels_zero_based(labels)
        feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)
        status_json = ts_result.status
        checkpoints = [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in ts_result.checkpoints
        ]
    elif algo == "ts_rust":
        rust_json = workdir / "ts_rust_result.json"
        part_file = workdir / "ts_rust.part"
        rust_result = run_ts_rust_binary(
            graph_path=graph_path,
            k=k,
            beta=beta,
            seed=seed,
            budget_time_ms=budget_time_ms,
            out_json=rust_json,
            part_path=part_file,
        )
        payload = rust_result.payload

        stdout = rust_result.stdout
        stderr = rust_result.stderr
        returncode = rust_result.returncode
        solver_elapsed_ms = int(payload["elapsed_ms"])

        labels = np.asarray(payload["labels"], dtype=int)
        cut = int(payload["cutsize_best"])

        labels_norm = normalize_labels_zero_based(labels)
        feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)
        status_json = str(payload.get("status", "ok"))
        checkpoints = [
            {
                "time_ms": int(cp["time_ms"]),
                "cutsize_best": int(cp["cutsize_best"]),
                "nfe": int(cp["nfe"]) if cp.get("nfe") is not None else None,
            }
            for cp in payload.get("checkpoints", [])
        ]
    elif algo == "ils_rust":
        rust_json = workdir / "ils_rust_result.json"
        part_file = workdir / "ils_rust.part"
        ils_rust_result = run_ils_rust_binary(
            graph_path=graph_path,
            k=k,
            beta=beta,
            seed=seed,
            budget_time_ms=budget_time_ms,
            out_json=rust_json,
            part_path=part_file,
        )
        ils_payload = ils_rust_result.payload

        stdout = ils_rust_result.stdout
        stderr = ils_rust_result.stderr
        returncode = ils_rust_result.returncode
        solver_elapsed_ms = int(ils_payload["elapsed_ms"])

        labels = np.asarray(ils_payload["labels"], dtype=int)
        cut = int(ils_payload["cutsize_best"])

        labels_norm = normalize_labels_zero_based(labels)
        feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)
        status_json = str(ils_payload.get("status", "ok"))
        checkpoints = [
            {
                "time_ms": int(cp["time_ms"]),
                "cutsize_best": int(cp["cutsize_best"]),
                "nfe": int(cp["nfe"]) if cp.get("nfe") is not None else None,
            }
            for cp in ils_payload.get("checkpoints", [])
        ]
    elif algo == "ils":
        adj = _adj_from_edges(n, edges)
        ils_result = run_ils_partition(
            adj,
            k=k,
            epsilon=beta,
            config=ILSConfig(
                seed=seed,
                budget_time_ms=budget_time_ms,
            ),
        )
        elapsed_wall = int((time.perf_counter() - t0_wall) * 1000)
        solver_elapsed_ms = (
            int(ils_result.elapsed_ms) if ils_result.elapsed_ms is not None else elapsed_wall
        )

        labels = _labels_from_part_of(ils_result.best_part_of, n)
        cut = int(ils_result.best_cutsize)

        part_file = workdir / "ils.part"
        part_file.write_text(
            "".join(f"{int(label)}\n" for label in labels.tolist()), encoding="utf-8"
        )

        labels_norm = normalize_labels_zero_based(labels)
        feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)
        status_json = ils_result.status
        checkpoints = [
            {
                "time_ms": int(cp.time_ms),
                "cutsize_best": int(cp.cutsize_best),
                "nfe": int(cp.nfe),
            }
            for cp in ils_result.checkpoints
        ]
    else:
        if algo == "metis":
            res = run_gpmetis(
                graph_path, k=k, beta=beta, seed=seed, timeout_s=budget_time_ms / 1000.0
            )
        elif algo == "kahip":
            res = run_kaffpa(
                graph_path,
                k=k,
                beta=beta,
                seed=seed,
                timeout_s=budget_time_ms / 1000.0,
                preset=kahip_preset,
            )
        else:
            raise ValueError(
                "algo must be 'metis', 'kahip', 'sa', 'ils', 'grasp', 'ts' or 'ts_rust'"
            )

        elapsed_wall = int((time.perf_counter() - t0_wall) * 1000)
        solver_elapsed_ms = int(res.elapsed_ms) if res.elapsed_ms is not None else elapsed_wall

        stdout = res.stdout
        stderr = res.stderr
        returncode = res.returncode

        labels = (
            read_partition_labels(res.part_path)
            if res.part_path and res.part_path.exists()
            else None
        )
        cut = compute_cutsize_edges_labels(edges, labels) if labels is not None else None

        if labels is not None:
            labels_norm = normalize_labels_zero_based(labels)
            feasible, validation = feasible_beta(labels_norm, k=k, beta=beta)

        status_json = res.status if res.status in {"ok", "timeout"} else "solver_failed"
        part_file = res.part_path if res.part_path and res.part_path.exists() else None
        checkpoints = (
            [
                {
                    "time_ms": solver_elapsed_ms,
                    "cutsize_best": int(cut),
                    "nfe": None,
                }
            ]
            if cut is not None
            else []
        )

    # Persistência do JSON (apenas tipos nativos)
    out = {
        "timestamp": datetime.now(UTC).isoformat(),
        "instance_id": str(inst.get("instance_id") or Path(instance_path).stem),
        "algo": algo,
        "k": k,
        "beta": beta,
        "seed": seed,
        "budget_time_ms": budget_time_ms,
        "status": status_json,
        "returncode": returncode,
        "elapsed_ms": solver_elapsed_ms,
        "stdout": stdout,
        "stderr": stderr,
        "metrics": {
            "cutsize_best": int(cut) if cut is not None else None,
            "n_nodes": int(n),
            "balance_tolerance": float(beta),
            "imbalance_raw": None,
        },
        "paths": {
            "workdir": str(workdir),
            "graph_path": str(graph_path),
            "part_path": str(part_file) if part_file else None,
        },
        "env": env_info,
        "tools": tool_info,
        "feasible": bool(feasible) if cut is not None else False,
        "validation": validation if cut is not None else {},
        "checkpoints": checkpoints,
        "schema_version": "1.0.0",
        "schema_path": "specs/jsonschema/solver_run.schema.v1.json",
    }
    if cut is not None:
        out["cutsize_best"] = int(cut)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    return RunArtifact(
        run_id=f"{algo}-{int(time.time())}",
        algo=algo,
        status=status_json,
        cut=cut,
        elapsed_ms=solver_elapsed_ms,
        part_file=part_file,
    )


def run_one(**kwargs):
    """Backcompat: alias para `run` (mantém assinatura esperada pelos testes/CLI)."""
    return run(**kwargs)


def _tool_version(cmd: list[str]) -> str:
    """Tenta extrair versão do tool via '--version' ou '-v'."""
    candidates = [cmd + ["--version"], cmd + ["-v"], cmd + ["-V"], cmd + ["-h"]]
    for c in candidates:
        try:
            cp = subprocess.run(c, capture_output=True, text=True, timeout=2.0, check=False)
            out = (cp.stdout or cp.stderr or "").strip()
            # heurística simples: primeira linha
            if out:
                return out.splitlines()[0][:200]
        except Exception:
            pass
    return ""


def _env_snapshot() -> dict:
    """Snapshot leve do ambiente — útil para logs/diagnóstico ad hoc."""
    py = platform.python_version()
    os_name = platform.system()
    os_rel = platform.release()
    cpu_model = platform.processor() or ""
    try:
        import psutil  # opcional

        phys = psutil.cpu_count(logical=False)
        logi = psutil.cpu_count(logical=True)
        freq = getattr(psutil.cpu_freq(), "current", None)
    except Exception:
        phys = None
        logi = os.cpu_count()
        freq = None
    return {
        "hostname": socket.gethostname(),
        "python": py,
        "os": os_name,
        "os_release": os_rel,
        "cpu": {
            "model": cpu_model,
            "cores_logical": logi,
            "cores_physical": phys,
            "freq_mhz": freq,
        },
    }


def _which(x: str) -> bool:
    """Wrapper fininho de shutil.which, mantendo assinatura antiga em alguns testes."""
    from shutil import which

    return which(x) is not None
