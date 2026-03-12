````markdown
# TC_005 – Smoke and performance sanity

**ID:** TC_005
**Title:** Smoke and performance sanity
**Type:** Smoke / performance

---

## 1. Purpose

Ensure that a **minimal, fast subset** of tests can be run:

- locally (for quick developer feedback),
- via pre-commit hooks,
- and in CI,

without depending on heavy external solvers or long-running experiments.

This test case is associated with the smoke-related tests and with the CI configuration.

---

## 2. Preconditions

- The project is installed (via Poetry or a plain virtualenv).
- External solvers are optional for this test case; the smoke subset must not require KaHIP.

---

## 3. Procedure

1. Run the smoke subset locally via pytest (example patterns):

   ```bash
   cd ~/MPP
   poetry install --with dev -E metrics

   # Marker-based smoke (if configured)
   poetry run pytest -q -m smoke

   # Or file-based smoke
   poetry run pytest -q tests/test_sanity.py tests/test_runner_smoke.py tests/test_solvers_smoke.py
````

2. Run the minimal CI-equivalent test selection:

   ```bash
   poetry run pytest -q -k "not (kahip or solvers_external)"
   ```

3. Optionally, test pre-commit integration:

   ```bash
   poetry run pre-commit run -a
   ```

   Verify that the pytest hook (if present) completes quickly.

4. Observe total runtime and verify that it is suitable for frequent local runs and CI.

---

## 4. Expected results

* Smoke-related tests (`test_sanity.py`, `test_runner_smoke.py`, `test_solvers_smoke.py`)
  pass consistently.
* The CI-equivalent selection (`-k "not (kahip or solvers_external)"`) completes within a
  reasonable time on a typical development machine and in the GitHub-hosted runner.
* Pre-commit hooks complete without unexpected timeouts.

If any smoke test becomes too slow or flaky, it should be:

* refactored or moved to a slower test group; and
* documented accordingly in `docs/testing/TESTING.md` and this file.

---

## 5. Related artefacts

* **Tests**

  * `tests/test_sanity.py`
  * `tests/test_runner_smoke.py`
  * `tests/test_solvers_smoke.py`

* **CI**

  * `.github/workflows/ci.yml`

* **Pre-commit**

  * `.pre-commit-config.yaml`

* **Docs**

  * `docs/testing/TESTING.md`
  * `docs/testing/CI.md`
  * `docs/testing/TRACEABILITY.md`

```
```
