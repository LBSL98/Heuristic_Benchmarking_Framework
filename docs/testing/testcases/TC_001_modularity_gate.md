````markdown
# TC_001 – Modularity gate regression

**ID:** TC_001
**Title:** Modularity gate regression
**Type:** Regression / regime validation

---

## 1. Purpose

Ensure that changes to the instance generator, bounds or configuration do **not** break the
modularity-based gate used to classify or filter instances by community structure.

This test case is linked to the regression test in `tests/test_modularity_gate_regression.py`.

---

## 2. Preconditions

- The project is installed (via Poetry or a plain virtualenv).
- Synthetic instances have been generated according to `configs/instances_to_generate.yaml`.
- Python tests can be executed (see `docs/testing/TESTING.md`).

---

## 3. Procedure

1. Ensure the development environment is set up (Poetry recommended):

   ```bash
   cd ~/MPP
   poetry install --with dev -E metrics
````

2. Run the modularity gate regression test:

   ```bash
   poetry run pytest tests/test_modularity_gate_regression.py
   ```

3. Observe the output, paying attention to:

   * any failures related to modularity thresholds or regime classification;
   * any new warnings that indicate borderline cases.

---

## 4. Expected results

* All tests in `test_modularity_gate_regression.py` **pass**.
* Reported modularity values stay within the expected ranges encoded in the test and in
  the supporting specifications (e.g. `specs/bounds.json`).

If a failure occurs, the change that triggered it (in the generator, bounds or configuration)
must be reviewed. The test expectations should only be updated when there is a deliberate and
documented change to the experimental design.

---

## 5. Related artefacts

* **Code / tests**

  * `tests/test_modularity_gate_regression.py`

* **Specs / configuration**

  * `specs/bounds.json` (where applicable)
  * `configs/instances_to_generate.yaml`

* **Documentation**

  * `docs/reports/01_instance_generator.md`
  * `docs/testing/TRACEABILITY.md` (section on modularity gate)

```
```
