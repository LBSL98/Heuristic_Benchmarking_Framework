# 756 frontier confirmation plan field mapping rebuild

- Runner: `scripts/run_exception_mining_confirmation.py`
- Old plan CSV: `/workspace/audit_reports/multilevel_exception_mining/frontier_pilot/srv_noctua_frontier_pilot_001/751_frontier_confirmation_run_plan.csv`
- New plan CSV: `/workspace/audit_reports/multilevel_exception_mining/frontier_pilot/srv_noctua_frontier_pilot_001/756_frontier_confirmation_run_plan_runner_schema.csv`
- Decision: `ready_to_restart_confirmation_service_with_756_schema_compatible_plan`
- Claim boundary: `field_mapping_plan_rebuild_only_no_confirmation_no_solver_no_service`

## Schema comparison

- PlanRow fields: `['campaign_id', 'confirmation_stage', 'environment_id', 'run_id', 'candidate_id', 'family', 'environment_target', 'variant', 'priority_label_from_screening', 'algo_label', 'algo', 'seed', 'budget_ms', 'bundle_path', 'instance_path']`
- Old columns: `['campaign_id', 'confirmation_campaign_id', 'confirmation_stage', 'run_id', 'candidate_id', 'family', 'environment_target', 'variant', 'pool_role', 'confirmation_bucket', 'selection_tier', 'confirmation_role', 'dominant_label', 'source_parent_candidate_id', 'scale_factor', 'bundle_path', 'instance_path', 'algo', 'seed', 'budget_ms', 'source_selection_plan', 'output_root']`
- Missing from old: `['environment_id', 'priority_label_from_screening', 'algo_label']`
- Extra old columns: `['confirmation_campaign_id', 'pool_role', 'confirmation_bucket', 'selection_tier', 'confirmation_role', 'dominant_label', 'source_parent_candidate_id', 'scale_factor', 'source_selection_plan', 'output_root']`

## Proven field mapping

- environment_id: `{'source': 'explicit_environment_slice_identifier', 'value': 'srv_noctua_frontier_pilot_001'}`
- priority_label_from_screening: `{'source': 'dominant_label from 750 selection plan, proven against historical priority_label_from_screening vocabulary', 'values': ['non_exception', 'strong_exception_candidate']}`
- algo_label: `{'source': 'historical confirmation_run_plan.csv algo -> algo_label mapping', 'mapping': {'grasp': 'GRASP', 'grasp_rust': 'GRASP-Rust', 'ils': 'ILS', 'ils_rust': 'ILS-Rust', 'kahip': 'KaHIP', 'metis': 'METIS', 'sa': 'SA', 'sa_rust': 'SA-Rust', 'ts': 'TS', 'ts_rust': 'TS-Rust'}}`

## Validation by official runner

- runner.read_run_plan ok: `True`
- Parsed rows: `4000`
- Parsed candidate count: `40`
- Parsed environment ids: `['srv_noctua_frontier_pilot_001']`
- Parsed algo counts: `{'grasp': 400, 'grasp_rust': 400, 'ils': 400, 'ils_rust': 400, 'kahip': 400, 'metis': 400, 'sa': 400, 'sa_rust': 400, 'ts': 400, 'ts_rust': 400}`
- Parsed algo-label counts: `{'GRASP': 400, 'GRASP-Rust': 400, 'ILS': 400, 'ILS-Rust': 400, 'KaHIP': 400, 'METIS': 400, 'SA': 400, 'SA-Rust': 400, 'TS': 400, 'TS-Rust': 400}`
- Parsed priority-label counts: `{'non_exception': 600, 'strong_exception_candidate': 3400}`
- Parsed budget counts: `{'1000': 2000, '5000': 2000}`
- Parsed seed counts: `{'42': 800, '43': 800, '44': 800, '45': 800, '46': 800}`
- Path error count: `0`

## Historical plan evidence

### `audit_reports/multilevel_exception_mining/confirmation/confirmation_plan_srv_noctua_001/confirmation_run_plan.csv`
- row_count: `22400`
- columns: `['campaign_id', 'confirmation_stage', 'environment_id', 'run_id', 'candidate_id', 'family', 'environment_target', 'variant', 'priority_label_from_screening', 'algo_label', 'algo', 'seed', 'budget_ms', 'bundle_path', 'instance_path', 'graph_metis_path', 'graph_edges_path', 'manifest_row_path', 'sha256sums_path', 'artifact_dir', 'artifact_json', 'workdir', 'claim_boundary']`
- environment_id values sample: `['srv_noctua_linux_8gb']`
- priority label values sample: `['competitive_candidate', 'near_tie_candidate', 'non_exception', 'strong_exception_candidate']`
- algo_label map: `{'grasp': ['GRASP'], 'grasp_rust': ['GRASP-Rust'], 'ils': ['ILS'], 'ils_rust': ['ILS-Rust'], 'kahip': ['KaHIP'], 'metis': ['METIS'], 'sa': ['SA'], 'sa_rust': ['SA-Rust'], 'ts': ['TS'], 'ts_rust': ['TS-Rust']}`

### `audit_reports/multilevel_exception_mining/confirmation/confirmation_plan_srv_noctua_campaign_image_001/confirmation_run_plan.csv`
- row_count: `22400`
- columns: `['campaign_id', 'confirmation_stage', 'environment_id', 'run_id', 'candidate_id', 'family', 'environment_target', 'variant', 'priority_label_from_screening', 'algo_label', 'algo', 'seed', 'budget_ms', 'bundle_path', 'instance_path', 'graph_metis_path', 'graph_edges_path', 'manifest_row_path', 'sha256sums_path', 'artifact_dir', 'artifact_json', 'workdir', 'claim_boundary']`
- environment_id values sample: `['srv_noctua_linux_8gb']`
- priority label values sample: `['competitive_candidate', 'near_tie_candidate', 'non_exception', 'strong_exception_candidate']`
- algo_label map: `{'grasp': ['GRASP'], 'grasp_rust': ['GRASP-Rust'], 'ils': ['ILS'], 'ils_rust': ['ILS-Rust'], 'kahip': ['KaHIP'], 'metis': ['METIS'], 'sa': ['SA'], 'sa_rust': ['SA-Rust'], 'ts': ['TS'], 'ts_rust': ['TS-Rust']}`

### `audit_reports/multilevel_exception_mining/confirmation/confirmation_plan_srv_noctua_final_image_001/confirmation_run_plan.csv`
- row_count: `22400`
- columns: `['campaign_id', 'confirmation_stage', 'environment_id', 'run_id', 'candidate_id', 'family', 'environment_target', 'variant', 'priority_label_from_screening', 'algo_label', 'algo', 'seed', 'budget_ms', 'bundle_path', 'instance_path', 'graph_metis_path', 'graph_edges_path', 'manifest_row_path', 'sha256sums_path', 'artifact_dir', 'artifact_json', 'workdir', 'claim_boundary']`
- environment_id values sample: `['srv_noctua_linux_8gb']`
- priority label values sample: `['competitive_candidate', 'near_tie_candidate', 'non_exception', 'strong_exception_candidate']`
- algo_label map: `{'grasp': ['GRASP'], 'grasp_rust': ['GRASP-Rust'], 'ils': ['ILS'], 'ils_rust': ['ILS-Rust'], 'kahip': ['KaHIP'], 'metis': ['METIS'], 'sa': ['SA'], 'sa_rust': ['SA-Rust'], 'ts': ['TS'], 'ts_rust': ['TS-Rust']}`

### `audit_reports/multilevel_exception_mining/confirmation/confirmation_plan_srv_noctua_linux_dedicated_001/confirmation_run_plan.csv`
- row_count: `22400`
- columns: `['campaign_id', 'confirmation_stage', 'environment_id', 'run_id', 'candidate_id', 'family', 'environment_target', 'variant', 'priority_label_from_screening', 'algo_label', 'algo', 'seed', 'budget_ms', 'bundle_path', 'instance_path', 'graph_metis_path', 'graph_edges_path', 'manifest_row_path', 'sha256sums_path', 'artifact_dir', 'artifact_json', 'workdir', 'claim_boundary']`
- environment_id values sample: `['srv_noctua_linux_8gb']`
- priority label values sample: `['competitive_candidate', 'near_tie_candidate', 'non_exception', 'strong_exception_candidate']`
- algo_label map: `{'grasp': ['GRASP'], 'grasp_rust': ['GRASP-Rust'], 'ils': ['ILS'], 'ils_rust': ['ILS-Rust'], 'kahip': ['KaHIP'], 'metis': ['METIS'], 'sa': ['SA'], 'sa_rust': ['SA-Rust'], 'ts': ['TS'], 'ts_rust': ['TS-Rust']}`

### `audit_reports/multilevel_exception_mining/confirmation/confirmation_plan_srv_noctua_poetrypath_001/confirmation_run_plan.csv`
- row_count: `22400`
- columns: `['campaign_id', 'confirmation_stage', 'environment_id', 'run_id', 'candidate_id', 'family', 'environment_target', 'variant', 'priority_label_from_screening', 'algo_label', 'algo', 'seed', 'budget_ms', 'bundle_path', 'instance_path', 'graph_metis_path', 'graph_edges_path', 'manifest_row_path', 'sha256sums_path', 'artifact_dir', 'artifact_json', 'workdir', 'claim_boundary']`
- environment_id values sample: `['srv_noctua_linux_8gb']`
- priority label values sample: `['competitive_candidate', 'near_tie_candidate', 'non_exception', 'strong_exception_candidate']`
- algo_label map: `{'grasp': ['GRASP'], 'grasp_rust': ['GRASP-Rust'], 'ils': ['ILS'], 'ils_rust': ['ILS-Rust'], 'kahip': ['KaHIP'], 'metis': ['METIS'], 'sa': ['SA'], 'sa_rust': ['SA-Rust'], 'ts': ['TS'], 'ts_rust': ['TS-Rust']}`

### `audit_reports/multilevel_exception_mining/confirmation/confirmation_plan_srv_noctua_precampaign_slice_001/confirmation_run_plan.csv`
- row_count: `22400`
- columns: `['campaign_id', 'confirmation_stage', 'environment_id', 'run_id', 'candidate_id', 'family', 'environment_target', 'variant', 'priority_label_from_screening', 'algo_label', 'algo', 'seed', 'budget_ms', 'bundle_path', 'instance_path', 'graph_metis_path', 'graph_edges_path', 'manifest_row_path', 'sha256sums_path', 'artifact_dir', 'artifact_json', 'workdir', 'claim_boundary']`
- environment_id values sample: `['srv_noctua_linux_8gb']`
- priority label values sample: `['competitive_candidate', 'near_tie_candidate', 'non_exception', 'strong_exception_candidate']`
- algo_label map: `{'grasp': ['GRASP'], 'grasp_rust': ['GRASP-Rust'], 'ils': ['ILS'], 'ils_rust': ['ILS-Rust'], 'kahip': ['KaHIP'], 'metis': ['METIS'], 'sa': ['SA'], 'sa_rust': ['SA-Rust'], 'ts': ['TS'], 'ts_rust': ['TS-Rust']}`

## plan_row_from_csv source

```python
def plan_row_from_csv(row: dict[str, str]) -> PlanRow:
    """Convert one CSV row into a typed plan row."""

    return PlanRow(
        campaign_id=row["campaign_id"],
        confirmation_stage=row["confirmation_stage"],
        environment_id=row["environment_id"],
        run_id=row["run_id"],
        candidate_id=row["candidate_id"],
        family=row["family"],
        environment_target=row["environment_target"],
        variant=row["variant"],
        priority_label_from_screening=row["priority_label_from_screening"],
        algo_label=row["algo_label"],
        algo=row["algo"],
        seed=int(row["seed"]),
        budget_ms=int(row["budget_ms"]),
        bundle_path=Path(row["bundle_path"]),
        instance_path=Path(row["instance_path"]),
    )

```

## Boundary

This command only rebuilds and validates the confirmation plan. It does not run confirmation, solvers, or a service.
