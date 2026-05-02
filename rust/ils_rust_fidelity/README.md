# ILS-Rust-fidelity

`ils_rust_fidelity` is a faithful implementation-maturity target for the canonical Python iterated local search implementation (`ils`).

It does not replace the Python ILS implementation and must not be interpreted as performance evidence by itself. Its purpose is to provide an implementation surface that can later be validated and, only after validation, used in controlled ablation.

## Build

    cargo build --release --manifest-path rust/ils_rust_fidelity/Cargo.toml

## Run directly

    rust/ils_rust_fidelity/target/release/ils_rust_fidelity \
      --graph path/to/graph.graph \
      --k 8 \
      --beta 0.03 \
      --seed 42 \
      --budget-time-ms 5000 \
      --out-json path/to/ils_rust_result.json \
      --part path/to/ils_rust.part

Optional parameters:

    --max-iters
    --perturb-moves
    --checkpoint-every-iter

## Claim boundary

This implementation may support ILS implementation-maturity claims only after formal validation. It does not support claims about SA, GRASP, CART, performance, ablation, selector behavior, or full Rust portfolio maturity.
