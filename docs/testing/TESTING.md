````markdown
# Testing strategy

This document summarises how tests are organised in the FORJA / MPP repository and how to run
them locally in a way that mirrors the CI pipeline.

The overall philosophy is:

- keep a **fast, always-green smoke subset**;
- maintain a **broader regression suite** (unit, schema, integration);
- keep external solver tests explicit (METIS / KaHIP), so the suite can still run in
  constrained environments.

---

## 1. Test types

Tests live under:

```text
tests/
```

and are organised roughly as follows:

* **Smoke and sanity layers**

  * `tests/test_sanity.py`
  * `tests/test_runner_smoke.py`
  * `tests/test_solvers_smoke.py`

* **Core functionality**

  * `tests/test_generator.py`
  * `tests/test_operator.py`
  * `tests/test_heuristics_metrics.py`
  * `tests/test_public_api.py`

* **Schema and contracts**

  * `tests/test_results_schema.py`
  * `tests/test_instances_sanity.py`

* **Plan governance**

  * `tests/test_plan_configs.py`
  * `tests/test_plan_greedy_scope_governance.py`
  * `tests/test_plan_runner_full_portfolio.py`

* **External solvers**

  * `tests/test_solvers_external.py`
  * tests filtered as `"kahip"` / external-solver coverage when appropriate.

Not all tests run in every environment. The CI configuration and some local commands use pytest
expressions to exclude slower or solver-specific tests when appropriate.

---

## 2. Running tests locally

The canonical local workflow uses the locked Poetry environment:

```bash
poetry install --with dev -E metrics
```

### 2.1. Minimal suite, mirroring CI

The minimal CI-oriented suite excludes KaHIP and heavier external-solver coverage:

```bash
poetry run pytest -q -k "not (kahip or solvers_external)"
```

### 2.2. Quick smoke subset

```bash
poetry run pytest -q tests/test_sanity.py tests/test_runner_smoke.py tests/test_solvers_smoke.py
```

### 2.3. Focused checks

```bash
poetry run pytest tests/test_plan_configs.py
poetry run pytest tests/test_results_schema.py
```

---

## 3. Running tests like CI (without Poetry)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -U pytest
pip install .
pytest -q -k "not (kahip or solvers_external)"
```

---

## 4. External solvers (METIS / KaHIP)

Some tests depend on external solvers:

* **METIS** via `gpmetis`
* **KaHIP** via `kaffpa`

The minimal CI workflow always installs `metis`, but does not install KaHIP. Therefore:

* KaHIP-dependent tests are skipped or excluded in the minimal job.
* Local full-solver validation may include KaHIP when `kaffpa` is installed and on `PATH`.

For local coverage with both solvers available:

```bash
poetry run pytest tests/test_solvers_smoke.py tests/test_solvers_external.py
```

Reproducibility note:

* record the runtime `kaffpa` version actually used in the experiment
* do not infer the experimental KaHIP version from the vendored `./KaHIP` tree alone

---

## 5. Contract expectations enforced by tests

The active result-artifact contract expects:

* total runtime serialized as `elapsed_ms`
* checkpoint timestamps serialized as `checkpoints[].time_ms`
* optional checkpoint `nfe` only for instrumented metaheuristics

Cross-family fairness claims are wall-clock based. Tests and docs should not describe NFE as the
universal comparison budget.

---

## 6. Schema and instance sanity tests

The suite includes tests that validate:

* result JSONs against `specs/jsonschema/solver_run.schema.v1.json`
* instance JSONs against `specs/schema_input.json`
* properties of the synthetic panel and plan governance

These checks are the main safety net when changing:

* the instance generator
* the plan YAML files under `configs/`
* the result schema and manifest helpers

---

## 7. Pre-commit integration

The repository ships with `.pre-commit-config.yaml` for whitespace, YAML/JSON validation,
formatting, linting, type checking, and smoke-oriented checks.

```bash
poetry run pre-commit install -f
poetry run pre-commit run -a
```

```
