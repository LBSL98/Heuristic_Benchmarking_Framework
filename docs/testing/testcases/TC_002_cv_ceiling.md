````markdown
# TC_002 – Degree / “speed” CV bands and ceilings

**ID:** TC_002
**Title:** Degree / “speed” coefficient-of-variation constraints
**Type:** Regime validation

---

## 1. Purpose

Verify that synthetic instances obey the **coefficient-of-variation (CV) bands and ceilings**
defined in the experimental design for degree or “speed” distributions.

This test case is linked to `tests/test_degree_cv_bands.py` and `tests/test_degree_cv_cap.py`.

---

## 2. Preconditions

- The project is installed and tests are runnable (via Poetry or a plain virtualenv).
- Synthetic instances have been generated according to `configs/instances_to_generate.yaml`.
- Bounds for CV bands / ceilings are defined in the appropriate specification files
  (e.g. `specs/bounds.json`).

---

## 3. Procedure

1. Ensure the development environment is set up:

   ```bash
   cd ~/MPP
   poetry install --with dev -E metrics
````

2. Run the CV-related tests:

   ```bash
   poetry run pytest tests/test_degree_cv_bands.py tests/test_degree_cv_cap.py
   ```

3. Inspect any failures or warnings, focusing on:

   * instances whose CV falls outside the intended bands;
   * violations of CV ceilings for specific regimes.

---

## 4. Expected results

* All tests in `test_degree_cv_bands.py` and `test_degree_cv_cap.py` **pass**.
* Reported CV values adhere to the bands and ceilings encoded in the tests and in the configuration.

If failures occur, investigate whether they are due to:

* changes in the generator algorithm;
* changes in `configs/instances_to_generate.yaml`;
* inconsistent bounds in `specs/bounds.json`.

Only adjust test expectations when there is a deliberate and documented change in the experimental
regimes.

---

## 5. Related artefacts

* **Code / tests**

  * `tests/test_degree_cv_bands.py`
  * `tests/test_degree_cv_cap.py`

* **Specs / configuration**

  * `specs/bounds.json`
  * `configs/instances_to_generate.yaml`

* **Documentation**

  * `docs/reports/01_instance_generator.md`
  * `docs/testing/TRACEABILITY.md` (CV-related section)

```
```
