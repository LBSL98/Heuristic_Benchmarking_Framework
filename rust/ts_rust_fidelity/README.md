# TS-Rust-fidelity

`ts_rust_fidelity` is a parallel implementation-maturity ablation for the canonical Python Tabu Search (`ts`).

It does not replace the Python TS implementation and must not be interpreted as a new main benchmark solver. Its purpose is to evaluate engineering/runtime effects under the frozen TS-Rust-fidelity contract.

## Build

    cargo build --release --manifest-path rust/ts_rust_fidelity/Cargo.toml

or:

    make ts-rust-build

## Run directly

The binary expects a METIS `.graph` file and writes a compact JSON payload plus a `.part` file.

    rust/ts_rust_fidelity/target/release/ts_rust_fidelity \
      --graph path/to/graph.graph \
      --k 8 \
      --beta 0.03 \
      --seed 42 \
      --budget-time-ms 5000 \
      --out-json path/to/ts_rust_result.json \
      --part path/to/ts_rust.part

Optional parameters:

    --max-steps
    --min-tenure
    --tenure-scale
    --tenure-jitter
    --checkpoint-every-nfe
    --frequency-penalty

## Run through the framework

    PYTHONPATH=src poetry run hpc-framework single-run \
      --instance data/instances/synthetic/n2000_p50.json.gz \
      --algo ts_rust \
      --k 8 \
      --beta 0.03 \
      --budget-time-ms 5000 \
      --seed 42 \
      --out data/results_raw/ts_rust_smoke.json \
      --workdir data/results_raw/ts_rust_smoke

## Claim boundary

This implementation may support claims about TS implementation maturity after validation. It does not support claims about all metaheuristics, ILS, GRASP, or SA.
