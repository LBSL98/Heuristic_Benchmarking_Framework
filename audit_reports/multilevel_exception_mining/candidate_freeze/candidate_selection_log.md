# Candidate selection log — exception mining confirmation freeze

- Campaign: `EXP-MULTILEVEL-EXCEPTION-MINING-001`
- Freeze id: `candidate_freeze_001`
- Created at UTC: `2026-05-08T11:08:09.970182+00:00`
- Stage: candidate freeze before confirmation
- Selection policy: broad near-exhaustive confirmation

## Decision

All screened non-holdout candidates advance to full-portfolio confirmation.

The rationale is methodological: the exploratory hypothesis may not survive confirmation easily, so the confirmation set intentionally avoids aggressive pruning. This reduces cherry-picking risk and preserves positive, near-tie, competitive, and negative/control cases.

The 8 pre-existing holdout candidates remain reserved and are not moved into confirmation.

## Counts

- Confirmation candidates: `56`
- Holdout candidates: `8`
- Additional rejections at freeze stage: `0`
- Original rejected candidates preserved from generation: `0`

## Confirmation label distribution from exploratory screening

- `competitive_candidate`: `1`
- `near_tie_candidate`: `26`
- `non_exception`: `2`
- `strong_exception_candidate`: `27`

## Family distribution

- `F01`: `7`
- `F02`: `7`
- `F03`: `7`
- `F04`: `7`
- `F05`: `7`
- `F06`: `7`
- `F07`: `7`
- `F08`: `7`

## Environment-target distribution

- `common`: `32`
- `server_expanded`: `24`

## Execution-environment interpretation

The confirmation manifest is designed against the expanded Windows 11 16 GB Docker Linux host as the target matrix. The WSL 8 GB notebook and Linux 8 GB server may attempt the same matrix or a compatible stress ladder, with incomplete slices recorded as failure-frontier observations rather than silently removed.

## Claim boundary

This file freezes which instances are allowed to enter confirmation. It does not report confirmation results. It does not support final solver-superiority, CART, ASP, or monograph-result claims by itself.
