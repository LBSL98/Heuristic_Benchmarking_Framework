# Reproducibility Checklist — FORJA

> Use this checklist before a pilot run, benchmark batch, or audit bundle handoff.

## 1. Canonical scope

- [ ] Official benchmark claims are restricted to `SA`, `TS`, `ILS`, `GRASP`, `METIS`, and `KaHIP`.
- [ ] Any `greedy` run kept in the repository is labeled exploratory and excluded from official benchmark tables, manifests, and selector-label claims.

## 2. Environment

- [ ] OS, kernel, CPU, and thread controls are recorded.
- [ ] Any report using this release states that the benchmark ran in an audited WSL2 environment and does not overclaim bare-metal timing equivalence.
- [ ] Python environment is pinned and archived (`poetry.lock`, `pip list`, or equivalent).
- [ ] `gpmetis` is available when METIS runs are expected, and its runtime-reported version is recorded.
- [ ] `kaffpa` is available when KaHIP runs are expected, and its runtime-reported version is recorded.
- [ ] The active experimental narrative treats KaHIP 3.17 as the official repository reference.
- [ ] If a vendored `./KaHIP` tree is present, it is logged separately as auxiliary repository material rather than assumed to match the runtime binary.

## 3. Plans and fairness

- [ ] The archived plan YAML uses `schema: forja-exp-v1`.
- [ ] All compared solvers receive the same per-instance wall-clock budget.
- [ ] The same balance semantics are enforced across all compared families.
- [ ] Hyperparameters were frozen in the pilot before the main benchmark claim was made.
- [ ] Metaheuristic benchmark plans use the D-012 frozen profiles for `SA`, `TS`, `ILS`, and `GRASP`.
- [ ] Outputs are validated independently after execution.

## 4. Result artifacts

- [ ] Artifacts validate against `specs/jsonschema/solver_run.schema.v1.json`.
- [ ] Total serialized runtime is stored as `elapsed_ms`.
- [ ] Checkpoint timestamps are stored as `checkpoints[].time_ms`.
- [ ] `time_ns` does not appear as an official serialized checkpoint field.
- [ ] Legacy names such as `runtime_ms` and `elapsed_wall_ms` are absent from current benchmark artifacts.
- [ ] When NFE is emitted by a metaheuristic, it is treated as diagnostic instrumentation rather than as the universal cross-family budget.

## 5. Execution trace

- [ ] Instance identifiers and hashes are archived.
- [ ] Commit SHA, hostname, solver name, `k`, `beta`, seed, and budget are preserved per run.
- [ ] `stdout` / `stderr` are kept when relevant to diagnose external-solver behaviour.
- [ ] Output locations match the selected plan `output.raw_dir`.

- [ ] If TTT or ECDF is reported, the target rule, censoring rule, and wall-clock interpretation follow D-010.
- [ ] If performance profiles are reported, the ratio definition and the common-feasible instance set are stated explicitly.

- [ ] Selector evaluation, when reported, uses an instance-level preregistered outer holdout over the collapsed per-instance table.
- [ ] No selector preprocessing or model choice touches the outer test partition.

- [ ] Selector claims do not rely on hyperparameter search or nested model selection unless the canon is explicitly reopened.
- [ ] The instantiated CART parameter tuple is recorded before selector evaluation is reported.

## 6. Reporting

- [ ] Tables and plots cite the commit, plan, and dataset slice used.
- [ ] Any legacy material consulted during the analysis is identified as such.
- [ ] Any deviation from the canonical contract is documented explicitly before the result is reused in prose.
