"""Módulo com operadores para particionamento k-way."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

Vertex = int
Block = int


@dataclass
class PartitionState:
    """Estado mínimo para suportar o operador 1-move e cálculo incremental de cutsize.

    Suposições:
      - Grafo simples, não direcionado, não ponderado.
      - Particionamento k-way por cardinalidade (todos os vértices têm peso 1).
    """

    # Grafo como lista de adjacência
    adj: dict[Vertex, set[Vertex]]

    # Bloco atual de cada vértice: part_of[v] = b
    part_of: dict[Vertex, Block]

    # Tamanho (número de vértices) de cada bloco
    block_size: dict[Block, int]

    # Número de blocos
    k: int

    # Tolerância de desequilíbrio: (1 + epsilon) * |V| / k
    epsilon: float

    # Cut atual (número de arestas que cruzam blocos)
    cutsize: int

    # Conjunto de vértices de fronteira (opcional, mas útil)
    boundary: set[Vertex] = field(default_factory=set)

    @property
    def n(self) -> int:
        """Retorna o número de vértices da partição atual."""
        return len(self.part_of)


def compute_cutsize_naive(adj: dict[Vertex, set[Vertex]], part_of: dict[Vertex, Block]) -> int:
    """Computa o cutsize do zero em O(|E|). Útil para testes de sanidade.

    Conta cada aresta (u,v) com u < v apenas uma vez.
    """
    cut = 0
    for u, neighbors in adj.items():
        pu = part_of[u]
        for v in neighbors:
            if v <= u:
                continue  # evita contar duas vezes
            if part_of[v] != pu:
                cut += 1
    return cut


def recompute_boundary(adj: dict[Vertex, set[Vertex]], part_of: dict[Vertex, Block]) -> set[Vertex]:
    """Recalcula o conjunto de vértices de fronteira do zero.
    Útil para testes / depuração.
    """
    boundary: set[Vertex] = set()
    for v, neighbors in adj.items():
        pv = part_of[v]
        if any(part_of[u] != pv for u in neighbors):
            boundary.add(v)
    return boundary


def is_move_feasible(state: PartitionState, v: Vertex, target_block: Block) -> bool:
    """Verifica se mover v do bloco atual a -> target_block respeita (1 + epsilon).

    Restrição: todos os vértices têm peso 1.
    """
    a = state.part_of[v]
    b = target_block
    if a == b:
        return False  # não faz sentido "mover" para o mesmo bloco

    n = state.n
    k = state.k
    max_block_size = math.ceil((1.0 + state.epsilon) * n / k)

    size_a = state.block_size[a]
    size_b = state.block_size[b]

    # Após o movimento: bloco a perde 1, bloco b ganha 1
    new_size_a = size_a - 1
    new_size_b = size_b + 1

    # Nunca aceitar bloco vazio
    if new_size_a <= 0:
        return False

    if new_size_a > max_block_size:
        return False
    return not (new_size_b > max_block_size)


def eval_move_delta_cut(state: PartitionState, v: Vertex, target_block: Block) -> int:
    """Calcula o delta de cutsize ao mover v: a -> target_block.

    Usa apenas a vizinhança de v:
        delta = sum_{u vizinho} [is_cut_after - is_cut_before]

    Onde uma aresta (v,u) contribui 1 para o cut se part_of[v] != part_of[u].
    """
    a = state.part_of[v]
    b = target_block
    if a == b:
        return 0

    delta = 0
    for u in state.adj[v]:
        part_u = state.part_of[u]

        # Antes do movimento
        is_cut_before = 1 if (a != part_u) else 0
        # Depois do movimento
        is_cut_after = 1 if (b != part_u) else 0

        delta += is_cut_after - is_cut_before

    return delta


def apply_move(state: PartitionState, v: Vertex, target_block: Block) -> None:
    """Aplica o movimento v: a -> target_block, assumindo:
      - já foi verificada a viabilidade (is_move_feasible),
      - o delta foi calculado por eval_move_delta_cut.

    Atualiza:
      - part_of
      - block_size
      - cutsize
      - boundary (v e vizinhos)
    """
    a = state.part_of[v]
    b = target_block
    if a == b:
        return

    # 1) delta do cut
    delta = eval_move_delta_cut(state, v, b)
    state.cutsize += delta

    # 2) atualiza blocos
    state.part_of[v] = b
    state.block_size[a] -= 1
    state.block_size[b] += 1

    # 3) atualiza fronteira: v e seus vizinhos
    _update_boundary_after_move(state, v)


def _update_boundary_after_move(state: PartitionState, v: Vertex) -> None:
    """Atualiza o conjunto de vértices de fronteira para v e seus vizinhos.

    Regra: um vértice x está na fronteira se existe pelo menos um vizinho
    com bloco diferente de part_of[x].
    """
    # Reavalia v
    _refresh_boundary_flag(state, v)

    # Reavalia vizinhos de v (eles podem ter mudado de status)
    for u in state.adj[v]:
        _refresh_boundary_flag(state, u)


def _refresh_boundary_flag(state: PartitionState, x: Vertex) -> None:
    """Recalcula se x é fronteira e atualiza o set state.boundary."""
    px = state.part_of[x]
    is_boundary = any(state.part_of[u] != px for u in state.adj[x])

    if is_boundary:
        state.boundary.add(x)
    else:
        state.boundary.discard(x)
