# 759 canonical update candidates

This file proposes canonical updates based on the validated frontier confirmation.
It does not itself modify the canonical files.

## Evidence boundary

- Environment slice: `srv_noctua_frontier_pilot_001`.
- Confirmation output: `confirmation_001`.
- Validation report: `758_frontier_confirmation_validation_report.json`.
- Claim status: evidence-bearing for this explicit slice only; monograph claims remain pending canonical mapping.

## Core evidence to carry forward

- `4000` planned runs, `4000` raw results, `4000` valid results, `0` invalid results.
- `800` collapsed rows and `80` confirmation label rows.
- Confirmation labels: `62` strong exceptions, `5` competitive confirmations, `3` near-tie confirmations, `10` non-exceptions.
- Family concentration: `F04` produced `28` strong confirmations; `F07` produced `15` strong confirmations and `3` near-tie confirmations; `F05` produced all `10` non-exception confirmations and `2` competitive confirmations.

## 08_Results_to_Text_Map.md
- Add a frontier-confirmation evidence section with explicit boundary: srv_noctua_frontier_pilot_001 only.
- Record counts: 4000 planned/raw/valid results, 0 invalid, 800 collapsed rows, 80 label rows.
- Record confirmed labels: 62 strong_exception_confirmed, 5 competitive_confirmed, 3 near_tie_confirmed, 10 non_exception_confirmed.
- Record family concentration: F04 has 28 strong confirmations; F07 has 15 strong and 3 near-tie confirmations; F05 contains all 10 non-exception confirmations plus 2 competitive confirmations.

## 06_Experiment_Ledger.md
- Register screening_short_001 and confirmation_001 as srv-noctua frontier pilot evidence chain.
- Include run counts, service execution status, environment id, plan file 756, and validation report 758.

## 03_Methodology_Canonical.md
- Do not change benchmark methodology yet; add only a note that this is an exception-mining confirmation slice, not the final benchmark campaign.
- Clarify that monograph-level claims require canon mapping and cannot pool environments unless explicitly stated.

## 07_Open_Issues.md
- Close the operational issue of frontier confirmation execution if desired, but open/keep analytical issues for mapping to text and deciding whether to expand confirmation or final benchmark scope.

## 09_Committee_Issues_Log.md
- Record that these results support the value of instance-level selection/CART motivation, but do not yet establish final thesis conclusions.
