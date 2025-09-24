# Reproducibility Checklist — FORJA

> Use this one-pager before each experiment round. Attach it as an appendix to the thesis.

## Environment
- [ ] OS & kernel recorded (e.g., Ubuntu 22.04; `uname -a`)
- [ ] CPU/GPU noted (`lscpu`; governor consistent if applicable)
- [ ] Python 3.11.x; `pip list` / `poetry.lock` archived
- [ ] `gpmetis` on `PATH`; METIS **version** recorded
- [ ] `kaffpa` on `PATH` (for final experiments); CI may skip it
- [ ] FORJA package installed from the target commit/tag

## Determinism & threads
- [ ] `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`
- [ ] Master seed set; deterministic derivation scheme documented for replicas

## Data & plans
- [ ] Instances under `data/instances/synthetic/` with **canonical names**
- [ ] Instance **hashes** recorded (and index saved)
- [ ] Plan YAML uses `schema: forja-exp-v1` and is archived with the commit
- [ ] `k` and `β` chosen from the baseline (or deviations documented)

## Budgets & checkpoints
- [ ] `NFE_max = 50 · |E|` applied
- [ ] `t_max = 0.5 · |E| ms` applied
- [ ] Anytime checkpoints by NFE recorded: `{1e2, 3e2, 1e3, 3e3, 1e4, 3e4, ...}`

## Execution artifacts
- [ ] `manifest.json` per run with: `git_sha`, host, time bounds, `k`, `β`, budgets, seed, cmdline, exit_code
- [ ] `stdout.log` and `stderr.log` saved
- [ ] Labels normalized to `0..k-1` and **remap** stored if applied
- [ ] Partition files (METIS format) written if enabled

## Analysis & reporting
- [ ] Aggregation script produced tables (parquet/csv)
- [ ] Plots: performance profiles, anytime curves, TTT (targets: 0/1/2/5%)
- [ ] Statistical tests: Friedman+Nemenyi; Wilcoxon (paired); correction: Holm
- [ ] Stratification by density, Q, |V|, CV
- [ ] All figures/tables list **commit id**, **plan id**, **dataset hash index**

**Date:** 2025-09-24 • **Operator:** ____________________
