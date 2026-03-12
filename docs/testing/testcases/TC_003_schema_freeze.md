````markdown
# TC_003 – Result schema freeze (`solver_run.schema.v1.json`)

**ID:** TC_003
**Title:** Result schema freeze for solver manifests
**Type:** Contract / integration

---

## 1. Purpose

Ensure that solver result manifests (`*.v1.json`) conform to the **frozen JSON schema**
`solver_run.schema.v1.json`, and that changes to this schema or to the manifest structure
are deliberate and traceable.

This test case is linked to `tests/test_results_schema.py` and to the helper scripts used
in the Phase 1 campaign.

---

## 2. Preconditions

- The project is installed and tests are runnable (via Poetry or a plain virtualenv).
- Some result manifests exist, for example:
  - `data/results_raw/smoke_metis.v1.json`
  - `data/results_raw/phase1/out_metis.v1.json`
  - `data/results_raw/phase1/out_kahip.v1.json`
- The schema file is present:

  ```text
  specs/jsonschema/solver_run.schema.v1.json
````

---

## 3. Procedure

1. Ensure the development environment is set up:

   ```bash
   cd ~/MPP
   poetry install --with dev -E metrics
   ```

2. Run the schema tests:

   ```bash
   poetry run pytest tests/test_results_schema.py
   ```

3. Optionally, validate specific manifests via the helper script:

   ```bash
   poetry run python scripts/validate_manifest_v1.py \
     --schema specs/jsonschema/solver_run.schema.v1.json \
     --in data/results_raw/smoke_metis.v1.json \
         data/results_raw/phase1/out_metis.v1.json \
         data/results_raw/phase1/out_kahip.v1.json
   ```

4. Inspect any failures, focusing on:

   * missing or renamed fields;
   * type mismatches;
   * structural changes (e.g., different nesting).

---

## 4. Expected results

* All tests in `test_results_schema.py` **pass**.
* `validate_manifest_v1.py` reports `[OK]` for all selected manifests.
* Any change to `solver_run.schema.v1.json` or to the manifest shape is:

  * reflected in tests;
  * documented in the specification and in the repository changelog.

---

## 5. Related artefacts

* **Code / tests**

  * `tests/test_results_schema.py`
  * `scripts/pack_manifest_v1.py`
  * `scripts/validate_manifest_v1.py`
  * `scripts/aggregate_manifests.py`

* **Specs**

  * `specs/jsonschema/solver_run.schema.v1.json`

* **Documentation**

  * `docs/reports/02_experimental_campaign.md`
  * `docs/testing/TRACEABILITY.md` (result schema section)

```
```
