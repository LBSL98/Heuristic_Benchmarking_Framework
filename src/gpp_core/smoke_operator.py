"""Smoke helpers for the ``gpp_core`` operator module."""

# src/gpp_core/smoke_operator.py

from gpp_core.operator import compute_cutsize_naive


def build_toy_graph():
    # mesmo exemplo ilustrativo do texto, não precisa ser bonito
    adj = {
        0: {1, 2},
        1: {0, 2},
        2: {0, 1, 3},
        3: {2, 4, 5},
        4: {3, 5},
        5: {3, 4},
    }
    return adj


def main():
    adj = build_toy_graph()

    # blocos: {0,1,2} em 0, {3,4,5} em 1
    part = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1}

    cut = compute_cutsize_naive(adj, part)  # ⚠️ só 2 argumentos
    print("Cutsize naive no grafo de brinquedo:", cut)


if __name__ == "__main__":
    main()
