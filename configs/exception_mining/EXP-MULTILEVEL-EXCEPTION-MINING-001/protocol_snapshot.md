
# Protocol Snapshot — EXP-MULTILEVEL-EXCEPTION-MINING-001

This snapshot mirrors `decisions/14_Exception_Mining_Campaign_Protocol.md`.

Status: frozen for issue `#95`.

## Full confirmation portfolio

* `METIS`
* `KaHIP`
* `SA`
* `ILS`
* `GRASP`
* `TS`
* `SA-Rust`
* `ILS-Rust`
* `GRASP-Rust`
* `TS-Rust`

## Topology families

* `F01_modular_noise_sbm_like`
* `F02_chain_ring_cliques_modules`
* `F03_barbell_lollipop_bottleneck`
* `F04_hub_powerlaw`
* `F05_tree_dense_core_hybrid`
* `F06_road_like_sparse`
* `F07_dense_weak_signal`
* `F08_balance_hard_planted`

## Generator seeds

`1001, 1002, 1003, 1004, 1005`

## Solver seeds

* screening: `42`
* confirmation: `42, 43, 44, 45, 46`

## Budgets

* screening: `1000, 5000` ms
* confirmation: `100, 250, 500, 1000, 2000, 3000, 4000, 5000` ms

## Main labels

* `strong_exception_candidate`
* `robust_strong_exception_candidate`
* `near_tie_candidate`
* `competitive_candidate`
* `availability_only_candidate`
* `non_exception`

## Contract dependency

All generated instances must satisfy `decisions/13_Exception_Mining_Instance_Generation_Contract.md`.
