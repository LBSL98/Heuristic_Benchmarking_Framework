````markdown
# TC_003 – Result schema freeze (`solver_run.schema.v1.json`)

**ID:** TC_003
**Title:** Result schema freeze for solver manifests
**Type:** Contract / integration

---

## 1. Purpose

Ensure that benchmark result artifacts conform to the frozen JSON schema
`specs/jsonschema/solver_run.schema.v1.json`, and that changes to the manifest structure remain
deliberate and traceable.

This test case is linked to `tests/test_results_schema.py` and to the helper scripts used by the
repository result pipeline.

---

## 2. Preconditions

- The project is installed and tests are runnable.
- At least one result artifact exists, or fixture-based schema tests can be executed.
- The active contract uses:
  - `elapsed_ms`
  - `checkpoints[].time_ms`

---

## 3. Procedure

1. Set up the development environment:

   ```bash
   cd ~/MPP
   poetry install --with dev -E metrics
   ```

2. Run the schema tests:

   ```bash
   poetry run pytest tests/test_results_schema.py
   ```

3. Optionally validate specific artifacts:

   ```bash
   poetry run python scripts/validate_manifest_v1.py \
     --schema specs/jsonschema/solver_run.schema.v1.json \
     --in data/results_raw/<artifact>.json
   ```

4. Inspect failures for:

   * missing or renamed fields
   * type mismatches
   * regressions in checkpoint serialization

---

## 4. Expected results

* `tests/test_results_schema.py` passes.
* Checked artifacts satisfy the active schema.
* No active benchmark artifact serializes checkpoint time as `time_ns`.
* Any contract change is reflected simultaneously in schema, tests, and active documentation.

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

  * `docs/protocol/current_benchmark_contract.md`
  * `docs/testing/TRACEABILITY.md`

```
