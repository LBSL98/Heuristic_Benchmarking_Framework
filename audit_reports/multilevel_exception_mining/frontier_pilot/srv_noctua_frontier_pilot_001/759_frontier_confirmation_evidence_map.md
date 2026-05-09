# 759 frontier confirmation evidence map

## Scope and boundary

- Evidence chain: screening_short_001 → selection plan 750 → confirmation_001 → validation 758.
- Confirmation pipeline valid: `True`
- Planned/raw/valid results: `4000` / `4000` / `4000`
- Invalid results: `0`
- Candidate count: `40`
- Label rows: `80`
- Claim boundary: `evidence_mapping_only_no_canonical_files_modified_no_monograph_claim_finalized`

## Label transitions

- Transition classes: `{'downgraded_in_confirmation': 4, 'negative_control_changed': 4, 'same_tier': 1, 'stable_negative_control': 9, 'stable_strong': 62}`
- Preliminary → confirmed matrix: `{'competitive_candidate': {'competitive_confirmed': 1}, 'non_exception': {'competitive_confirmed': 4, 'non_exception_confirmed': 9}, 'strong_exception_candidate': {'near_tie_confirmed': 3, 'non_exception_confirmed': 1, 'strong_exception_confirmed': 62}}`

## Confirmed labels

- By family: `{'F01': {'competitive_confirmed': 1, 'strong_exception_confirmed': 5}, 'F02': {'strong_exception_confirmed': 6}, 'F04': {'strong_exception_confirmed': 28}, 'F05': {'competitive_confirmed': 2, 'non_exception_confirmed': 10}, 'F06': {'strong_exception_confirmed': 4}, 'F07': {'near_tie_confirmed': 3, 'strong_exception_confirmed': 15}, 'F08': {'competitive_confirmed': 2, 'strong_exception_confirmed': 4}}`
- By environment target: `{'common': {'competitive_confirmed': 4, 'near_tie_confirmed': 2, 'non_exception_confirmed': 6, 'strong_exception_confirmed': 30}, 'server_expanded': {'competitive_confirmed': 1, 'near_tie_confirmed': 1, 'non_exception_confirmed': 4, 'strong_exception_confirmed': 32}}`
- By selected bucket: `{'confirmation_core': {'competitive_confirmed': 1, 'near_tie_confirmed': 3, 'non_exception_confirmed': 2, 'strong_exception_confirmed': 62}, 'negative_control': {'competitive_confirmed': 4, 'non_exception_confirmed': 8}}`
- By selection tier: `{'negative_control_stable_non_exception': {'competitive_confirmed': 4, 'non_exception_confirmed': 8}, 'primary_budget_sensitive_strong_exception': {'competitive_confirmed': 1, 'non_exception_confirmed': 2, 'strong_exception_confirmed': 1}, 'primary_stable_strong_exception': {'near_tie_confirmed': 3, 'strong_exception_confirmed': 61}}`

## Candidate-level interpretation

- Candidate-level status counts: `{'confirmed_budget_sensitive_strong_exception': 2, 'confirmed_competitive_or_mixed': 2, 'confirmed_near_tie_or_mixed': 1, 'confirmed_stable_non_exception_control': 5, 'confirmed_stable_strong_exception': 30}`
- Candidate-level status by family: `{'F01': {'confirmed_budget_sensitive_strong_exception': 1, 'confirmed_stable_strong_exception': 2}, 'F02': {'confirmed_stable_strong_exception': 3}, 'F04': {'confirmed_stable_strong_exception': 14}, 'F05': {'confirmed_competitive_or_mixed': 1, 'confirmed_stable_non_exception_control': 5}, 'F06': {'confirmed_stable_strong_exception': 2}, 'F07': {'confirmed_budget_sensitive_strong_exception': 1, 'confirmed_near_tie_or_mixed': 1, 'confirmed_stable_strong_exception': 7}, 'F08': {'confirmed_competitive_or_mixed': 1, 'confirmed_stable_strong_exception': 2}}`
- Confirmation core outcomes: `{'confirmed_budget_sensitive_strong_exception': 2, 'confirmed_near_tie_or_mixed': 1, 'confirmed_stable_non_exception_control': 1, 'confirmed_stable_strong_exception': 30}`
- Negative control outcomes: `{'confirmed_competitive_or_mixed': 2, 'confirmed_stable_non_exception_control': 4}`

## Stable strong candidates

- `f01_common_scaled_frontier_x4p0_seed991152` family=`F01` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f01_server_scaled_frontier_x2p0_seed991161` family=`F01` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f02_common_b_frontier_x2p0_seed991241` family=`F02` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f02_common_scaled_frontier_x4p0_seed991252` family=`F02` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f02_server_scaled_frontier_x2p0_seed991261` family=`F02` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_common_a_frontier_x2p0_seed991011` family=`F04` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_common_a_frontier_x4p0_seed991012` family=`F04` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_common_b_frontier_x2p0_seed991021` family=`F04` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_common_b_frontier_x4p0_seed991022` family=`F04` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_common_c_frontier_x2p0_seed991031` family=`F04` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_common_c_frontier_x4p0_seed991032` family=`F04` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_common_scaled_frontier_x2p0_seed991041` family=`F04` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_common_scaled_frontier_x4p0_seed991042` family=`F04` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_server_a_frontier_x2p0_seed991051` family=`F04` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_server_a_frontier_x4p0_seed991052` family=`F04` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_server_b_frontier_x2p0_seed991061` family=`F04` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_server_b_frontier_x4p0_seed991062` family=`F04` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_server_scaled_frontier_x2p0_seed991071` family=`F04` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f04_server_scaled_frontier_x4p0_seed991072` family=`F04` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f06_server_scaled_frontier_x2p0_seed991201` family=`F06` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f06_server_scaled_frontier_x4p0_seed991202` family=`F06` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f07_common_a_frontier_x2p0_seed991081` family=`F07` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f07_common_a_frontier_x4p0_seed991082` family=`F07` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f07_common_b_frontier_x2p0_seed991091` family=`F07` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f07_common_c_frontier_x2p0_seed991101` family=`F07` env=`common` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f07_server_a_frontier_x2p0_seed991121` family=`F07` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f07_server_a_frontier_x4p0_seed991122` family=`F07` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f07_server_b_frontier_x2p0_seed991131` family=`F07` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f08_server_b_frontier_x2p0_seed991221` family=`F08` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`
- `f08_server_scaled_frontier_x2p0_seed991231` family=`F08` env=`server_expanded` bucket=`confirmation_core` screening=`{'strong_exception_candidate': 2}` confirmed=`{'strong_exception_confirmed': 2}`

## Budget-sensitive strong candidates

- `f01_server_scaled_frontier_x4p0_seed991162` family=`F01` env=`server_expanded` bucket=`confirmation_core` 1000=`competitive_candidate→competitive_confirmed` 5000=`strong_exception_candidate→strong_exception_confirmed`
- `f07_server_scaled_frontier_x4p0_seed991142` family=`F07` env=`server_expanded` bucket=`confirmation_core` 1000=`strong_exception_candidate→near_tie_confirmed` 5000=`strong_exception_candidate→strong_exception_confirmed`

## Stable non-exception controls

- `f05_common_b_frontier_x2p0_seed991171` family=`F05` env=`common` screening=`{'non_exception': 1, 'strong_exception_candidate': 1}` confirmed=`{'non_exception_confirmed': 2}`
- `f05_common_b_frontier_x4p0_seed991172` family=`F05` env=`common` screening=`{'non_exception': 2}` confirmed=`{'non_exception_confirmed': 2}`
- `f05_common_scaled_frontier_x4p0_seed991182` family=`F05` env=`common` screening=`{'non_exception': 2}` confirmed=`{'non_exception_confirmed': 2}`
- `f05_server_scaled_frontier_x2p0_seed991191` family=`F05` env=`server_expanded` screening=`{'non_exception': 2}` confirmed=`{'non_exception_confirmed': 2}`
- `f05_server_scaled_frontier_x4p0_seed991192` family=`F05` env=`server_expanded` screening=`{'non_exception': 2}` confirmed=`{'non_exception_confirmed': 2}`

## Oracle/SBS/VBS diagnostic

- SBS algo: `grasp`
- SBS mean median cut: `658.9583333333334`
- VBS mean median cut: `730.0875`
- Slice count: `80`
- Oracle claim boundary: `diagnostic_pending_canon_mapping`

## Candidate canonical updates

### `08_Results_to_Text_Map.md`
- Add a frontier-confirmation evidence section with explicit boundary: srv_noctua_frontier_pilot_001 only.
- Record counts: 4000 planned/raw/valid results, 0 invalid, 800 collapsed rows, 80 label rows.
- Record confirmed labels: 62 strong_exception_confirmed, 5 competitive_confirmed, 3 near_tie_confirmed, 10 non_exception_confirmed.
- Record family concentration: F04 has 28 strong confirmations; F07 has 15 strong and 3 near-tie confirmations; F05 contains all 10 non-exception confirmations plus 2 competitive confirmations.

### `06_Experiment_Ledger.md`
- Register screening_short_001 and confirmation_001 as srv-noctua frontier pilot evidence chain.
- Include run counts, service execution status, environment id, plan file 756, and validation report 758.

### `03_Methodology_Canonical.md`
- Do not change benchmark methodology yet; add only a note that this is an exception-mining confirmation slice, not the final benchmark campaign.
- Clarify that monograph-level claims require canon mapping and cannot pool environments unless explicitly stated.

### `07_Open_Issues.md`
- Close the operational issue of frontier confirmation execution if desired, but open/keep analytical issues for mapping to text and deciding whether to expand confirmation or final benchmark scope.

### `09_Committee_Issues_Log.md`
- Record that these results support the value of instance-level selection/CART motivation, but do not yet establish final thesis conclusions.

## Outputs

- Transition CSV: `/home/brunno/MPP/audit_reports/multilevel_exception_mining/frontier_pilot/srv_noctua_frontier_pilot_001/759_screening_to_confirmation_label_transitions.csv`
- Candidate summary CSV: `/home/brunno/MPP/audit_reports/multilevel_exception_mining/frontier_pilot/srv_noctua_frontier_pilot_001/759_candidate_level_confirmation_summary.csv`
- Report JSON: `/home/brunno/MPP/audit_reports/multilevel_exception_mining/frontier_pilot/srv_noctua_frontier_pilot_001/759_frontier_confirmation_evidence_map.json`
- Canonical update candidate Markdown: `/home/brunno/MPP/audit_reports/multilevel_exception_mining/frontier_pilot/srv_noctua_frontier_pilot_001/759_canonical_update_candidates.md`

## Boundary

This report maps evidence only. It does not modify canonical files and does not finalize monograph claims.
