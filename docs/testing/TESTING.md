````markdown
# Testing strategy

This document summarises how tests are organised in the FORJA / HPC Framework project and how to
run them locally in a way that mirrors the CI pipeline.

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
````

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

* **Regime-specific constraints**

  * `tests/test_degree_cv_bands.py`
  * `tests/test_degree_cv_cap.py`
  * `tests/test_modularity_gate_regression.py`

* **External solvers**

  * `tests/test_solvers_external.py`
  * tests tagged or filtered as `"kahip"` in the CI selection.

Not all tests run in every environment. The CI configuration and some local commands use pytest
expressions to **exclude slower or solver-specific tests** when appropriate.

---

## 2. Running tests locally (Poetry environment)

The canonical way to run tests locally is via **Poetry**, using the locked environment
(`poetry.lock`).

From the repository root:

```bash
poetry install --with dev -E metrics
```

### 2.1. Full (local) suite, mirroring CI selection

The minimal suite used in CI excludes KaHIP and external-solver tests:

```bash
poetry run pytest -q -k "not (kahip or solvers_external)"
```

This command is equivalent to the final step in `.github/workflows/ci.yml`, with the difference
that Poetry manages the environment instead of `pip install .` directly.

### 2.2. Quick smoke subset

For a fast feedback loop, a smoke subset can be selected via pytest markers and/or file names.
A typical pattern is:

```bash
# Example: smoke-only, if markers are available
poetry run pytest -q -m smoke

# Or restrict to smoke-related files
poetry run pytest -q tests/test_sanity.py tests/test_runner_smoke.py tests/test_solvers_smoke.py
```

The exact markers used may evolve over time; refer to test files and `pytest.ini` for the
current configuration.

### 2.3. Focusing on a single module or test

Pytest allows selecting individual modules or tests for debugging:

```bash
# Single module
poetry run pytest tests/test_generator.py

# Single test function (example name)
poetry run pytest tests/test_generator.py -k "test_n2000_panel_regime"
```

Replace `"test_n2000_panel_regime"` with the actual test name of interest.

---

## 3. Running tests like CI (without Poetry)

The CI pipeline uses a **plain virtual environment** with `pip`:

1. create and activate a venv;
2. `pip install .` plus `pytest`;
3. run the filtered suite.

Equivalent steps locally:

```bash
python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -U pytest
pip install .
```

Then:

```bash
pytest -q -k "not (kahip or solvers_external)"
```

This matches the `Install Python deps (pip only)` and `Run tests` steps in the CI workflow.

---

## 4. External solvers (METIS / KaHIP)

Some tests depend on external solvers:

* **METIS** via `gpmetis` (installed from the `metis` package on Ubuntu);
* **KaHIP** via `kaffpa` (built and installed separately).

The CI workflow always installs `metis`:

```bash
sudo apt-get install -y metis
gpmetis -h | head -n1 || true
```

KaHIP is currently optional in the minimal CI job, but is required for the **full experimental
baseline**. Tests that depend on KaHIP are either:

* marked so they can be skipped when `kaffpa` is missing, or
* excluded by the `-k "not (kahip or solvers_external)"` expression.

To run **all** solver tests locally, once both solvers are installed and on `PATH`:

```bash
poetry run pytest tests/test_solvers_smoke.py tests/test_solvers_external.py
```

---

## 5. Schema and instance sanity tests

The suite includes tests that validate:

* result JSONs against the schema in
  `specs/jsonschema/solver_run.schema.v1.json` (`tests/test_results_schema.py`);
* instance JSONs against the input schema in `specs/schema_input.json`
  (`tests/test_instances_sanity.py`);
* properties of the synthetic panel, such as:

  * degree / “speed” coefficient-of-variation bands (`tests/test_degree_cv_bands.py`);
  * CV ceilings and other constraints (`tests/test_degree_cv_cap.py`);
  * modularity gates and related thresholds (`tests/test_modularity_gate_regression.py`).

These tests act as a safety net when changing:

* the instance generator;
* the definitions of regimes in `configs/instances_to_generate.yaml`;
* the experiment plans in `configs/plan_phase_1*.yaml`.

If any of these tests fail, the new code or configuration should be considered incompatible with
the existing experimental protocol until investigated.

---

## 6. Pre-commit integration

The repository ships with a `.pre-commit-config.yaml` that includes, among other checks:

* trailing whitespace and end-of-file (EOF) fixes;
* YAML / JSON validation;
* code formatting (Black);
* linting (Ruff);
* type checking (Mypy);
* a smoke subset of tests (via pytest).

After installing development dependencies with Poetry, you can enable pre-commit hooks with:

```bash
poetry run pre-commit install -f
```

Then, to run all hooks on the current tree:

```bash
poetry run pre-commit run -a
```

Pre-commit is not required to run the test suite, but it helps enforce consistent style and
basic correctness before opening a pull request.

```
```
