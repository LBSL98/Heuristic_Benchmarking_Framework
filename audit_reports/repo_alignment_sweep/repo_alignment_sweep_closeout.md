# Repository Alignment Sweep Closeout

## Branch

- `chore-repo-canonical-alignment-sweep`

## Commits

- `97f0299` `docs: align active benchmark contract and artifact time fields`
- `bdbe637` `configs: relabel phase-1 plans by official and exploratory scope`
- `1014b46` `chore: quarantine legacy documentation artifacts`
- `35dfef1` `docs: add repository alignment sweep report`

## Full report

- Main report: `audit_reports/repo_alignment_sweep/repo_alignment_sweep_report.md`

## Summarized diff

Overall diff produced by the sweep:

- `22 files changed`
- `643 insertions`
- `488 deletions`

Main change areas:

1. Active benchmark contract and front-door docs
- Rewrote `README.md` to reflect the canonical portfolio, wall-clock / `fair(time)`, `elapsed_ms`, `checkpoints[].time_ms`, and KaHIP 3.17 as the active experimental reference.
- Reworked `docs/index.md` and `mkdocs.yml` so the site now separates active documentation from legacy/quarantine material.
- Added `docs/protocol/current_benchmark_contract.md` as the active protocol summary page.
- Aligned `decisions/03_Methodology_Canonical_consolidated.md` with the actual serialized time fields.

2. Active operational docs and testing docs
- Rewrote `docs/specs/reproducibility_checklist.md` around the current contract.
- Reframed `docs/specs/mealpy_integration_plan.md` so wall-clock remains the universal budget and NFE stays diagnostic only.
- Updated `docs/testing/TESTING.md`, `docs/testing/testcases/TC_003_schema_freeze.md`, and `docs/testing/testcases/TC_004_cli_examples.md` to point to the active contract and current artifact schema.
- Updated `docs/reports/01_instance_generator.md` to reference the active benchmark contract instead of the archived protocol.

3. Plan-scope clarification
- Relabeled `configs/plan_phase_1.yaml` and `configs/plan_phase_1_pilot.yaml` as baseline-only executable slices, without pretending they encode the full canonical portfolio.
- Strengthened the exploratory disclaimers in `configs/plan_phase_1_greedy_exploratory.yaml` and `configs/plan_phase_1_pilot_greedy_exploratory.yaml`.

4. Legacy / quarantine treatment
- Marked the following as legacy/quarantine instead of deleting them:
  - `docs/protocol/proto_v3.1.1.md`
  - `docs/reports/02_experimental_campaign.md`
  - `docs/01_project_plan_and_workflow.md`
  - `docs/00_architectural_overview.md`
  - `docs/decisions/003_metodologia_gerador_e_analise.md`
  - `docs/specs/baseline_evolutive_v1.md`

5. Audit trail
- Added the full classification and validation report in `audit_reports/repo_alignment_sweep/repo_alignment_sweep_report.md`.

## Validation snapshot

- `python -m mkdocs build --strict --site-dir /tmp/forja-mkdocs` passed
- `.venv/bin/python -m pytest -q tests/test_plan_configs.py tests/test_plan_greedy_scope_governance.py` passed
- `.venv/bin/python -m pytest -q tests/test_results_schema.py` passed
- `poetry run pytest -q tests/test_plan_configs.py tests/test_plan_greedy_scope_governance.py` passed

## Notes

- No merge was performed.
- No blind removal was performed.
- Vendored `KaHIP/` was preserved and documented as traceability material rather than treated as automatic experimental truth.
