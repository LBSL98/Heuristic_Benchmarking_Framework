"""Orquestrador single-run para METIS/KaHIP.
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
from pathlib import Path
from typing import Any

import numpy as np

from hpc_framework.solvers.common import read_partition_labels, write_metis_graph
from hpc_framework.solvers.kahip import run_kaffpa
from hpc_framework.solvers.metis import run_gpmetis


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
    tool_info = {}
    if algo == "metis":
        tool_info["gpmetis"] = _tool_version(["gpmetis"])
    elif algo == "kahip":
        tool_info["kaffpa"] = _tool_version(["kaffpa"])

    workdir.mkdir(parents=True, exist_ok=True)
    graph_path = workdir / "graph.graph"
    write_metis_graph(graph_path, n, edges)

    # Medição de parede local (overhead do Python incluído) para debug
    t0_wall = time.perf_counter()

    if algo == "metis":
        res = run_gpmetis(graph_path, k=k, beta=beta, seed=seed, timeout_s=budget_time_ms / 1000.0)
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
        raise ValueError("algo must be 'metis' or 'kahip'")

    elapsed_wall = int((time.perf_counter() - t0_wall) * 1000)
    solver_elapsed_ms = int(res.elapsed_ms) if res.elapsed_ms is not None else elapsed_wall

    labels = (
        read_partition_labels(res.part_path) if res.part_path and res.part_path.exists() else None
    )
    cut = compute_cutsize_edges_labels(edges, labels) if labels is not None else None

    # Mapeia status do solver para o status esperado pelos testes de runner
    status_json = res.status if res.status in {"ok", "timeout"} else "solver_failed"

    # Persistência do JSON (apenas tipos nativos)
    out = {
        "instance_id": inst.get("instance_id", ""),
        "algo": algo,
        "k": k,
        "beta": beta,
        "seed": seed,
        "budget_time_ms": budget_time_ms,
        "workdir": str(workdir),
        "graph_path": str(graph_path),
        "status": status_json,
        "returncode": res.returncode,
        "elapsed_ms": solver_elapsed_ms,  # Tempo oficial do solver; fallback para wall se ausente
        "elapsed_wall_ms": elapsed_wall,  # Tempo total com overhead Python (debug)
        "stdout": res.stdout,
        "stderr": res.stderr,
        "part_path": str(res.part_path) if res.part_path else None,
        "cutsize_best": int(cut) if cut is not None else None,
        "env": env_info,  # Telemetria de hardware/OS
        "tools": tool_info,  # Versões dos binários
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    return RunArtifact(
        run_id=f"{algo}-{int(time.time())}",
        algo=algo,
        status=status_json,
        cut=cut,
        elapsed_ms=solver_elapsed_ms,  # Prioriza o tempo do solver; fallback controlado
        part_file=res.part_path if res.part_path and res.part_path.exists() else None,
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
