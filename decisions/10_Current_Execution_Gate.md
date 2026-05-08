# 10_Current_Execution_Gate.md

<!-- canonical-map:srv-noctua-linux-dedicated-campaign:current-gate -->

## Current execution gate after srv-noctua Linux dedicated validation

The `srv-noctua` Linux dedicated campaign for `EXP-MULTILEVEL-EXCEPTION-MINING-001` has completed and passed final validation for the explicit environment stratum `srv_noctua_linux_8gb`.

Validated evidence summary:

- Repository head: `354447be68b5f7361afd245897d91bea7329020f`.
- Planned runs: `22400`.
- Raw results: `22400`.
- Valid results: `22400`.
- Invalid results: `0`.
- Missing artifacts: `0`.
- Schema errors: `0`.
- Raw status counts: `{'ok': 18760, 'timeout': 3640}`.
- Confirmation labels: `{'competitive_confirmed': 8, 'near_tie_confirmed': 227, 'non_exception_confirmed': 11, 'strong_exception_confirmed': 202}`.
- Evidence bundle: `audit_reports/multilevel_exception_mining/confirmation/srv_noctua_linux_dedicated_evidence_bundle_001`.

## Active boundary

This server evidence is valid for `srv_noctua_linux_8gb` only. It must not be pooled with WSL or Windows host results as homogeneous timing evidence. The next methodological gate is one of the following:

1. map the validated server evidence into monograph-safe tables and prose;
2. execute the Windows 11 Docker portability gate before any Windows-host campaign;
3. define a matched common-intersection analysis before any cross-environment robustness claim.

## Do not proceed if

- a result statement omits the environment identifier;
- a text claim treats timeout rows as invalid artifacts;
- a selector or CART claim is made before the result-to-text mapping accepts it;
- Windows or WSL behavior is inferred from the `srv-noctua` campaign without a matched gate.
