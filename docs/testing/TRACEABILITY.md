# Testing traceability

This document provides a high-level view of how quality requirements, specifications and tests
are connected in the FORJA / HPC Framework project.

The goal is to make it clear **which artefacts support which claims** in the thesis and in the
repository documentation.

---

## 1. Artefact map

Key artefacts involved in testing and traceability:

- **Specifications and bounds**
  - `specs/bounds.json`
  - `specs/schema_input.json`
  - `specs/jsonschema/solver_run.schema.v1.json`
- **Configuration and contracts**
  - experiment plans in `configs/*.yaml` (e.g. `configs/plan_phase_1.yaml`);
  - instance-generation regimes in `configs/instances_to_generate.yaml`.
- **Code and modules**
  - core logic under `src/gpp_core/`, `src/heuristics/`, `src/hpc_framework/`, `src/generator/`.
- **Tests**
  - test modules under `tests/` (unit, regression, schema, smoke);
  - manual test-case descriptions under `docs/testing/testcases/TC_*.md`.
- **CI and QA**
  - GitHub Actions workflow: `.github/workflows/ci.yml`;
  - pre-commit configuration: `.pre-commit-config.yaml`.

---

## 2. From requirements to tests

The table below sketches the relationship between **requirements**, **specifications** and
**tests**. It is not exhaustive, but covers the most critical aspects.

### 2.1. Integrity of synthetic instances (LFS + gzip)

- **Requirement**
  Synthetic instances under `data/instances/synthetic/` must be valid gzip-compressed JSON
  payloads, not Git LFS pointers.

- **Implementation / spec**
  - instances tracked with Git LFS when appropriate;
  - filenames reflecting regimes (e.g. `n2000_p50.json.gz`).

- **Tests & checks**
  - CI step “Ensure Git LFS & materialize blobs” in `.github/workflows/ci.yml`;
  - CI step “GZIP sanity” (uses `gzip -t`) in the same workflow.

- **Test case doc**
  - `docs/testing/testcases/TC_005_perf_smoke.md` (includes integrity checks as part of smoke).

---

### 2.2. Instance schema and structural sanity

- **Requirement**
  All instance JSONs must conform to `specs/schema_input.json` and basic structural invariants.

- **Implementation / spec**
  - `specs/schema_input.json` (canonical input schema);
  - regimes defined in `configs/instances_to_generate.yaml`.

- **Tests**
  - `tests/test_instances_sanity.py` (general structural checks);
  - `tests/test_generator.py` (integration with the generator).

- **Test case doc**
  - `docs/testing/testcases/TC_002_cv_ceiling.md` (regime constraints);
  - `docs/testing/testcases/TC_001_modularity_gate.md` (additional structural gates via modularity).

---

### 2.3. Degree / “speed” heterogeneity (CV bands and ceilings)

- **Requirement**
  Synthetic instances must obey coefficient-of-variation (CV) bands and ceilings defined in
  the experimental design.

- **Implementation / spec**
  - CV-related bounds in `specs/bounds.json` (where applicable);
  - regimes in `configs/instances_to_generate.yaml`.

- **Tests**
  - `tests/test_degree_cv_bands.py` (CV bands);
  - `tests/test_degree_cv_cap.py` (CV ceilings).

- **Test case doc**
  - `docs/testing/testcases/TC_002_cv_ceiling.md`.

---

### 2.4. Modularity gate and regime classification

- **Requirement**
  Certain experiments rely on distinguishing instances by community structure / modularity.
  Changes to the generator or bounds must not break this classification.

- **Implementation / spec**
  - modularity-related thresholds in `specs/bounds.json` or related configuration files.

- **Tests**
  - `tests/test_modularity_gate_regression.py`.

- **Test case doc**
  - `docs/testing/testcases/TC_001_modularity_gate.md`.

---

### 2.5. Result schema and manifest contracts

- **Requirement**
  Solver outputs and manifests must conform to `specs/jsonschema/solver_run.schema.v1.json`,
  enabling consistent aggregation and external analysis.

- **Implementation / spec**
  - `specs/jsonschema/solver_run.schema.v1.json` (canonical result schema);
  - scripts:
    - `scripts/pack_manifest_v1.py`
    - `scripts/validate_manifest_v1.py`
    - `scripts/aggregate_manifests.py`.

- **Tests**
  - `tests/test_results_schema.py` (schema-level validation);
  - integration tests around manifest generation.

- **Test case doc**
  - `docs/testing/testcases/TC_003_schema_freeze.md`.

---

### 2.6. CLI contracts and examples

- **Requirement**
  Command-line interfaces (CLIs) for the generator and runner must behave consistently with the
  documented examples and plans.

- **Implementation / spec**
  - CLI modules:
    - `src/generator/cli.py`
    - `src/hpc_framework/cli.py`
  - experiment plans under `configs/`.

- **Tests**
  - `tests/test_entrypoints.py` (exposing and validating public entry points);
  - `tests/test_public_api.py` (public-facing API stability).

- **Test case doc**
  - `docs/testing/testcases/TC_004_cli_examples.md`.

---

### 2.7. Performance and smoke behaviour

- **Requirement**
  A minimal subset of tests must run quickly and reliably to support pre-commit hooks and CI
  smoke checks.

- **Implementation / spec**
  - `.pre-commit-config.yaml` (smoke pytest hook);
  - CI workflow (`.github/workflows/ci.yml`) with filtered pytest invocation.

- **Tests**
  - `tests/test_sanity.py`;
  - `tests/test_runner_smoke.py`;
  - `tests/test_solvers_smoke.py`.

- **Test case doc**
  - `docs/testing/testcases/TC_005_perf_smoke.md`.

---

## 3. Maintaining traceability

When changing any of the following:

- schemas under `specs/`;
- experiment plans under `configs/`;
- generator logic (`src/generator/`);
- CLI behaviour (`src/hpc_framework/cli.py`, `src/generator/cli.py`);
- CI configuration (`.github/workflows/ci.yml`),

developers should:

1. Identify which tests and `TC_00X` documents are affected.
2. Update tests and documentation together, keeping the mapping in this file accurate.
3. Run at least:
   - the full pytest suite locally (preferably via Poetry);
   - `poetry run pre-commit run -a` for style and basic QA.

This ensures that claims made in the thesis and in the documentation remain backed by executable
tests and verifiable artefacts.
