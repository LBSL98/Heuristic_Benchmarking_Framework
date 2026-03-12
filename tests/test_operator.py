from gpp_core.operator import (
    PartitionState,
    apply_move,
    compute_cutsize_naive,
    is_move_feasible,
    recompute_boundary,
)


def make_simple_graph():
    # Um quadrado: 0-1-2-3-0
    adj = {
        0: {1, 3},
        1: {0, 2},
        2: {1, 3},
        3: {0, 2},
    }
    return adj


def test_cutsize_and_boundary_consistency():
    adj = make_simple_graph()
    # Partição inicial: {0,1} no bloco 0; {2,3} no bloco 1
    part_of = {0: 0, 1: 0, 2: 1, 3: 1}
    block_size = {0: 2, 1: 2}

    cut_naive = compute_cutsize_naive(adj, part_of)
    boundary = recompute_boundary(adj, part_of)

    state = PartitionState(
        adj=adj,
        part_of=dict(part_of),
        block_size=dict(block_size),
        k=2,
        epsilon=0.0,
        cutsize=cut_naive,
        boundary=set(boundary),
    )

    # Tenta mover 1 do bloco 0 para o 1 (se for viável)
    v = 1
    target_block = 1
    if is_move_feasible(state, v, target_block):
        apply_move(state, v, target_block)

        # Verifica cutsize incremental vs recomputado
        cut_after_naive = compute_cutsize_naive(state.adj, state.part_of)
        assert state.cutsize == cut_after_naive

        # Verifica fronteira incremental vs recomputada
        boundary_naive = recompute_boundary(state.adj, state.part_of)
        assert state.boundary == boundary_naive
