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

remain valid and behave as described in the documentation.

---

## 2. Preconditions

- The project is installed (via Poetry or an equivalent virtual environment).
- External solvers (METIS, KaHIP) are installed and on `PATH` if full experiments are to be run.
- The documentation pages are up to date:
  - `docs/api/generator_cli.md`
  - `docs/api/hpc_framework_cli.md`
  - `docs/reports/02_experimental_campaign.md`

---

## 3. Procedure

1. Inspect the current CLI help for the generator:

   ```bash
   cd ~/MPP
   poetry run python -m generator.cli --help
````

Compare the available subcommands and options with the description in
`docs/api/generator_cli.md`.

2. Inspect the current CLI help for the runner:

   ```bash
   poetry run python -m hpc_framework.cli --help
   ```

   Compare the output against `docs/api/hpc_framework_cli.md`.

3. Execute the Phase 1 plan using the documented command:

   ```bash
   ./scripts/run_phase_1.sh
   ```

   Confirm that:

   * the output paths match the description in
     `docs/reports/02_experimental_campaign.md`;
   * raw JSON files under `data/results_raw/phase1/` are generated as expected.

4. If relevant, test a minimal generator invocation (single instance), following the
   high-level pattern in `docs/api/generator_cli.md`, and verify that the output file
   adheres to `specs/schema_input.json`.

---

## 4. Expected results

* CLI help output for both modules is consistent with the documentation.
* The Phase 1 plan runs successfully and writes results to the locations documented
  in `02_experimental_campaign.md`.
* Any discrepancies (missing flags, renamed commands, changed defaults) are either:

  * corrected in the code to restore the documented behaviour, or
  * documented explicitly and propagated to the relevant pages.

---

## 5. Related artefacts

* **Code**

  * `src/generator/cli.py`
  * `src/hpc_framework/cli.py`

* **Docs**

  * `docs/api/generator_cli.md`
  * `docs/api/hpc_framework_cli.md`
  * `docs/reports/02_experimental_campaign.md`

* **Specs**

  * `specs/schema_input.json`
  * `configs/plan_phase_1.yaml`

```
```
