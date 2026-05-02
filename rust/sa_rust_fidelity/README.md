# SA-Rust-fidelity

`sa_rust_fidelity` is a faithful implementation-maturity target for the canonical Python simulated annealing implementation (`sa`).

It does not replace the Python SA implementation and must not be interpreted as performance evidence by itself. Its purpose is to provide an implementation surface that can later be validated and, only after validation, used in controlled ablation.

## Build

    cargo build --release --manifest-path rust/sa_rust_fidelity/Cargo.toml

## Run directly

    rust/sa_rust_fidelity/target/release/sa_rust_fidelity \
      --graph path/to/graph.graph \
      --k 8 \
      --beta 0.03 \
      --seed 42 \
      --budget-time-ms 5000 \
      --out-json path/to/sa_rust_result.json \
      --part path/to/sa_rust.part

Optional parameters:

    --initial-temp
    --cooling
    --min-temp
    --max-steps
    --checkpoint-every-nfe

## Claim boundary

This implementation may support SA implementation-maturity claims only after validation. It does not support claims about all metaheuristics, ILS, GRASP, CART, or full Rust portfolio maturity.
