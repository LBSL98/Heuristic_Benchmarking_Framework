# Repository Alignment Sweep Report

## 1. Purpose

- Perform a conservative repository sweep to align active documentation and plan wording with the current canonical benchmark contract.
- Separate legacy material from the active documentation flow without blind removal and without rewriting history.
- Preserve an auditable trail for later human review.

Scope covered in this sweep:

- `README.md`
- active documentation under `docs/`
- repository-facing methodological notes under `decisions/`
- tracked phase-1 plan YAML files under `configs/`
- legacy documentation artifacts that were still exposed as if current

Limitations:

- no algorithmic reimplementation
- no KaHIP rebuild or `PATH` change
- no runner / solver logic change
- no blind cleanup of vendored or data artifacts
- no attempt to silently adopt pre-existing untracked workspace files into the audited branch

## 2. Canonical truths used in this sweep

- Official thesis portfolio: `SA`, `TS`, `ILS`, `GRASP`, `METIS`, `KaHIP`.
- `greedy` remains only as an exploratory / engineering track and is outside the official benchmark flow and selector label space.
- KaHIP 3.17 is the official experimental reference for active documentation.
- The universal comparison axis across solver families is wall-clock time.
- `fair(time)` means equal wall-clock budget per instance, same balance semantics, same controlled environment, pilot-frozen hyperparameters, and independent validation.
- The canonical serialized time fields are `elapsed_ms` and `checkpoints[].time_ms`.
- `time_ns` is not the active serialized checkpoint field.
- Auditability and traceability take priority over cosmetic cleanup.

## 3. Inventory and classification table

| path | item summary | classification (a/b/c/d) | evidence | pipeline risk | traceability risk | recommended action | action taken | commit hash (if changed) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` | Front-door documentation still described a stale greedy-vs-baseline flow and lacked the active timing contract. | b | Example plan text described greedy against METIS/KaHIP and omitted `elapsed_ms` / `checkpoints[].time_ms`. | Low | Medium | Rewrite as active contract summary. | Rewritten around canonical scope, wall-clock, artifact fields, KaHIP note, and plan-role summary. | `97f0299` |
| `docs/index.md` | Site landing page did not distinguish active docs from historical material. | b | Old home page was generic and did not warn about legacy pages. | Low | Medium | Turn home page into active-vs-legacy entry point. | Rewritten to route readers to active contract pages and away from legacy material. | `97f0299` |
| `mkdocs.yml` | Active MkDocs nav exposed `proto_v3.1.1` as the protocol page. | b | Navigation pointed directly to `protocol/proto_v3.1.1.md`. | Low | High | Replace active nav with current contract page and move historical pages under legacy. | Nav rewritten into `Active Contract` and `Legacy / Quarantine` sections. | `97f0299` |
| `docs/protocol/current_benchmark_contract.md` | New active protocol summary page. | a | Needed because the site had no active benchmark-contract page. | Low | Low | Add current operational contract page. | Added. | `97f0299` |
| `decisions/03_Methodology_Canonical_consolidated.md` | Canonical methodology file still treated artifact field naming as open wording conflict. | b | It said checkpoint field naming still needed final alignment. | Low | High | Close the wording gap in repository docs and state exact canonical field names. | Added explicit `elapsed_ms` / `checkpoints[].time_ms` rules and removed pending schema-name item. | `97f0299` |
| `docs/specs/reproducibility_checklist.md` | Reproducibility checklist still relied on NFE-first and formula-heavy wording from an older protocol. | b | Checklist centered on `NFE_max`, `t_max`, and NFE-based checkpoints. | Low | Medium | Rewrite around wall-clock fairness, active artifact fields, and KaHIP runtime-version logging. | Rewritten. | `97f0299` |
| `docs/specs/mealpy_integration_plan.md` | Exploratory integration plan still framed NFE as primary budget. | b | YAML sketch used `budget.nfe` as primary and time as secondary. | Low | Medium | Align to wall-clock as universal budget and keep NFE diagnostic only. | Rewritten. | `97f0299` |
| `docs/testing/TESTING.md` | Testing guide lacked the active artifact-field wording and KaHIP provenance nuance. | b | It described KaHIP broadly but did not tie tests to `elapsed_ms` / `checkpoints[].time_ms` or runtime-version logging. | Low | Medium | Align testing guide with current contract. | Rewritten. | `97f0299` |
| `docs/testing/testcases/TC_003_schema_freeze.md` | Schema test case still pointed readers toward older campaign-report context. | b | Related-doc references were stale for current benchmark docs. | Low | Low | Point schema freeze case to active contract docs. | Rewritten. | `97f0299` |
| `docs/testing/testcases/TC_004_cli_examples.md` | CLI test case still depended on the legacy campaign report and old output assumptions. | b | Preconditions and expected results referenced `docs/reports/02_experimental_campaign.md`. | Low | Medium | Retarget to active docs and active result contract. | Rewritten. | `97f0299` |
| `docs/reports/01_instance_generator.md` | Instance-generator report still referenced the old protocol page as active. | b | Section 6 pointed to `docs/protocol/proto_v3.1.1.md`. | Low | Medium | Retarget protocol references to active contract docs. | Updated section 6. | `97f0299` |
| `configs/plan_phase_1.yaml` | Tracked plan claimed to be the official canonical scope while actually encoding only the baseline slice. | b | `experiment_id` and description presented it as official canonical scope. | Low | Medium | Relabel as baseline-only executable slice, not full canonical portfolio. | Description and experiment id updated. | `bdbe637` |
| `configs/plan_phase_1_pilot.yaml` | Same issue as the main phase-1 tracked plan. | b | Pilot plan claimed official canonical scope while being baseline-only. | Low | Medium | Relabel as pilot baseline slice. | Description and experiment id updated. | `bdbe637` |
| `configs/plan_phase_1_greedy_exploratory.yaml` | Exploratory plan was broadly correct but benefited from stronger scope labeling. | a | Greedy was already separated, but wording did not explicitly mention selector-label exclusion. | Low | Low | Strengthen exploratory disclaimer. | Description tightened. | `bdbe637` |
| `configs/plan_phase_1_pilot_greedy_exploratory.yaml` | Pilot exploratory plan needed the same stronger disclaimer. | a | Same as above. | Low | Low | Strengthen exploratory disclaimer. | Description tightened. | `bdbe637` |
| `docs/protocol/proto_v3.1.1.md` | Historical protocol page described a different multi-objective / hypervolume problem as if it were the protocol. | c | Mentions `Hypervolume`, `runtime_ms`, and a vehicle-clustering protocol. | Low | High | Preserve for history but label as legacy and remove from active nav. | Legacy/quarantine banner added and page moved to legacy nav. | `1014b46` |
| `docs/reports/02_experimental_campaign.md` | Historical campaign report still looked like current phase-1 guidance. | c | Describes hypervolume-driven design and old factor grid. | Low | Medium | Preserve but label as legacy. | Legacy/quarantine banner added and page moved to legacy nav. | `1014b46` |
| `docs/01_project_plan_and_workflow.md` | Historical workflow plan still described static-solution exchange and SUMO/ROS2 coupling. | c | Mentions `solution.csv`, `SUMO`, `ROS2`, and static solution exchange. | Low | Medium | Preserve but label as legacy. | Legacy/quarantine banner added and page moved to legacy nav. | `1014b46` |
| `docs/00_architectural_overview.md` | Historical architecture overview still mixed old MPP framing and environment assumptions. | c | Mentions older MPP framing and specific past execution setup. | Low | Medium | Preserve but label as legacy. | Legacy/quarantine banner added and page moved to legacy nav. | `1014b46` |
| `docs/decisions/003_metodologia_gerador_e_analise.md` | Historical ADR was still discoverable without warning despite predating the active benchmark contract. | c | Contains older methodological framing and exploratory analysis language. | Low | Medium | Preserve but label as legacy. | Legacy/quarantine banner added and page moved to legacy nav. | `1014b46` |
| `docs/specs/baseline_evolutive_v1.md` | Historical baseline note contained superseded KaHIP, greedy, and budgeting assumptions. | c | Explicitly mentions `KaHIP 3.14`, greedy inside the baseline, and NFE-first budgeting. | Low | High | Preserve but label as legacy rather than deleting. | Legacy/quarantine banner added and page moved to legacy nav. | `1014b46` |
| `specs/schema_output.json` | Historical output schema for the old protocol still exists in the repository root specs layer. | c | Uses `frente_pareto_final`, `hypervolume`, `runtime_ms`, `evaluations_total`. | Medium | Medium | Keep unchanged for now; evaluate later whether to move into a dedicated legacy specs area. | Left unchanged. | `n/a` |
| `KaHIP/` | Vendored KaHIP tree contains mixed version markers and cannot be treated as automatic experimental truth. | c | `KaHIP/README.md` announces `v3.19`, while `KaHIP/lib/version.h` exposes `v3.17`. | High | High | Preserve tree, but stop documentation from inferring runtime truth from it. | Left unchanged; active docs now state it is auxiliary, not automatic source of truth. | `n/a` |

## 4. Active documentation corrected

- `README.md`
  The README still suggested a stale greedy-vs-baseline framing and did not state the active wall-clock and artifact-field contract. It was rewritten to declare the canonical portfolio, the exploratory status of `greedy`, the active time-field names, and the KaHIP 3.17 / vendored-tree nuance.

- `docs/index.md` and `mkdocs.yml`
  The documentation front door exposed legacy pages as if they were current protocol pages. The landing page and navigation were rewritten so that active guidance is explicit and legacy content is visibly quarantined.

- `docs/protocol/current_benchmark_contract.md`
  Added as the active site-level summary of the benchmark contract so readers no longer land first on a legacy protocol.

- `decisions/03_Methodology_Canonical_consolidated.md`
  The repository’s methodological freeze file still described the checkpoint-field wording as unresolved. It now explicitly names `elapsed_ms` and `checkpoints[].time_ms` as the canonical serialized fields and demotes `time_ns` to implementation-detail-only status.

- `docs/specs/reproducibility_checklist.md`
  Rewritten around the frozen wall-clock protocol, active artifact fields, and runtime KaHIP provenance logging, instead of older NFE-first defaults.

- `docs/specs/mealpy_integration_plan.md`
  Reframed so any future MEALPY integration stays under the same wall-clock contract and treats NFE only as diagnostic instrumentation.

- `docs/testing/TESTING.md`, `docs/testing/testcases/TC_003_schema_freeze.md`, and `docs/testing/testcases/TC_004_cli_examples.md`
  Updated to reference the active contract docs rather than the archived campaign report, and to reinforce the active artifact-field naming.

- `docs/reports/01_instance_generator.md`
  The generator report now points to the active benchmark contract and active result schema instead of the archived protocol page.

- `configs/plan_phase_1.yaml` and `configs/plan_phase_1_pilot.yaml`
  Their wording previously overstated them as if they encoded the full canonical portfolio. They were relabeled as conservative baseline-only executable slices, which matches the actual tracked contents without silently expanding pipeline semantics.

- `configs/plan_phase_1_greedy_exploratory.yaml` and `configs/plan_phase_1_pilot_greedy_exploratory.yaml`
  Wording was strengthened so the exploratory status of `greedy` is unmistakable.

## 5. Legacy / quarantine decisions

- `docs/protocol/proto_v3.1.1.md`
  This page could not remain the active protocol entry point because it documents a different, older problem framing. It was not deleted because it may still matter for historical reconstruction and authorship traceability. The treatment was explicit legacy labeling plus removal from active navigation.

- `docs/reports/02_experimental_campaign.md`
  Preserved because it captures a historical experimental design, but quarantined because its metrics and protocol are not current.

- `docs/01_project_plan_and_workflow.md`
  Preserved because it documents an older architectural split and integration idea, but quarantined because it no longer governs the repository.

- `docs/00_architectural_overview.md`
  Preserved for historical context around earlier project framing, but not allowed to stand as active architecture guidance.

- `docs/decisions/003_metodologia_gerador_e_analise.md`
  Preserved as historical reasoning, but explicitly downgraded from active methodology guidance.

- `docs/specs/baseline_evolutive_v1.md`
  Preserved because it captures the earlier baseline concept and could still be useful during retrospective analysis; quarantined because it contains superseded assumptions about KaHIP version, greedy scope, and budgeting semantics.

## 6. Removals performed

- No removals were performed.
- No directories, vendored material, schemas, or data artifacts were deleted.
- This was intentional: the sweep prioritized classification, relabeling, and navigation hygiene over destructive cleanup.

## 7. Items intentionally left unchanged

- `KaHIP/`
  The vendored tree was left untouched. Removing, rebuilding, or “fixing” it would risk breaking unknown local workflows and would destroy a useful traceability witness. The repository documentation was instead corrected to stop treating the tree as automatic experimental truth.

- `specs/schema_output.json`
  This file clearly belongs to the historical protocol family, but it was left in place because it is a machine-readable artifact and unknown out-of-tree consumers may still rely on the path. Recommended future action is a dedicated human review before moving it under an explicit legacy specs area.

- The tracked `configs/plan_phase_1*.yaml` contents
  I did not silently expand the baseline-only tracked plans to include `SA`, `TS`, `ILS`, and `GRASP`, even though the canonical portfolio is broader. That would change executable pipeline semantics rather than just documentation. The wording was corrected instead, leaving the normative structural decision for a separate human-reviewed step.

- Canonical split benchmark plans
  The split-plan files `configs/plan_phase_1_baselines.yaml`, `configs/plan_phase_1_metaheuristics.yaml`, `configs/plan_phase_1_pilot_baselines.yaml`, `configs/plan_phase_1_pilot_metaheuristics.yaml`, plus `tests/test_canonical_benchmark_plans.py`, were later validated as executable under the current `plan_runner` flow and adopted into this branch explicitly rather than left as ambiguous local-only material.


- `configs/plan_phase_1_baselines.yaml`, `configs/plan_phase_1_metaheuristics.yaml`, `configs/plan_phase_1_pilot_baselines.yaml`, `configs/plan_phase_1_pilot_metaheuristics.yaml`, and `tests/test_canonical_benchmark_plans.py`
  These files were initially left untracked during the conservative documentation sweep, but were later validated for executability and governance consistency and then adopted explicitly into the branch.

## 8. Validation performed

Commands executed:

- `rg -n -S "KaHIP|kaffpa|3.14|3.17|3.19|time_ns|time_ms|elapsed_ms|checkpoint|checkpoints|elapsed_wall_ms|wall-clock|fair(time)|greedy|exploratory|official|canonical|phase_1|pilot|benchmark" README.md CHANGELOG.md docs configs specs src tests scripts decisions`
- `python -m mkdocs build --strict --site-dir /tmp/forja-mkdocs`
- `.venv/bin/python -m pytest -q tests/test_plan_configs.py tests/test_plan_greedy_scope_governance.py`
- `.venv/bin/python -m pytest -q tests/test_results_schema.py`
- `poetry run pytest -q tests/test_plan_configs.py tests/test_plan_greedy_scope_governance.py`
- targeted `rg` follow-up checks against active docs to verify that stale `KaHIP 3.14`, `proto_v3.1.1`, and stale greedy-official wording no longer survived in the active documentation layer

Result summary:

- MkDocs strict build passed successfully to `/tmp/forja-mkdocs`.
- `tests/test_plan_configs.py` plus `tests/test_plan_greedy_scope_governance.py` passed in both `.venv` and Poetry environments.
- `tests/test_results_schema.py` passed in `.venv`.
- Initial validation using system `python` failed only because that interpreter lacked `pytest`; validation was rerun in the project environment instead.

## 9. Final human-review recommendations

Ready for review / likely acceptable now:

- the active documentation layer
- the active timing-field wording
- the legacy/quarantine labeling
- the plan-scope wording clarifications

Still requires normative human decision:

- whether the tracked `plan_phase_1*.yaml` files should remain baseline-only slices or be superseded by tracked split plans / full canonical plans
- whether `specs/schema_output.json` should be moved into an explicit legacy specs area
- whether the vendored `KaHIP/` tree should later receive a stronger archival treatment once downstream local dependencies are audited

No merge was performed. The branch is left in a review-ready state with small thematic commits.
