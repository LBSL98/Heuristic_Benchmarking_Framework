````markdown
# TC_004 – CLI examples and contracts

**ID:** TC_004
**Title:** CLI examples and contracts (generator and runner)
**Type:** Usability / integration

---

## 1. Purpose

Verify that the documented CLI examples for:

- the **instance generator** (`generator.cli`), and
- the **experiment runner** (`hpc_framework.cli`)

remain valid and behave as described in the active documentation.

---

## 2. Preconditions

- The project is installed.
- External solvers are installed and on `PATH` when the selected plan requires them.
- The active docs are up to date:
  - `docs/api/generator_cli.md`
  - `docs/api/hpc_framework_cli.md`
  - `docs/protocol/current_benchmark_contract.md`
  - `README.md`

---

## 3. Procedure

1. Inspect the generator help:

   ```bash
   cd ~/MPP
   poetry run python -m generator.cli --help
   ```

2. Inspect the runner help:

   ```bash
   poetry run python -m hpc_framework.cli --help
   ```

3. Execute a documented plan:

   ```bash
   ./scripts/run_phase_1.sh
   ```

   Confirm that:

   * the selected plan file matches the intended scope
   * output files are written under the plan `output.raw_dir`
   * generated artifacts validate against `specs/jsonschema/solver_run.schema.v1.json`

4. If relevant, execute a small generator invocation and confirm that the output respects
   `specs/schema_input.json`.

---

## 4. Expected results

* CLI help output is consistent with the documentation.
* The selected plan runs with the documented command.
* Official tracked plans keep `greedy` out of official scope.
* Exploratory greedy plans remain visibly separated from official benchmark claims.
* Result artifacts use `elapsed_ms` and `checkpoints[].time_ms`.

---

## 5. Related artefacts

* **Code**

  * `src/generator/cli.py`
  * `src/hpc_framework/cli.py`

* **Docs**

  * `docs/api/generator_cli.md`
  * `docs/api/hpc_framework_cli.md`
  * `docs/protocol/current_benchmark_contract.md`
  * `README.md`

* **Specs / configs**

  * `specs/schema_input.json`
  * `specs/jsonschema/solver_run.schema.v1.json`
  * `configs/plan_phase_1.yaml`
  * `configs/plan_phase_1_pilot.yaml`

```
