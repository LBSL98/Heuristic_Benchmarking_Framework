# 11_Hyperparameter_Calibration_Protocol.md

## Purpose

This file defines the bounded pre-benchmark calibration stage used to support the final hyperparameter freeze of the stochastic participants. Its role is to make the freeze of SA, TS, ILS, and GRASP auditable without turning the main benchmark campaign into a tuning exercise.

## Rule of use

This file does **not** by itself freeze the final hyperparameter values of the benchmark release. Final values become canonical only after:

1. the planned calibration experiment is executed and reviewed;
2. the resulting chosen profile for each stochastic participant is written into `01_Decision_Log.md` as the final version of `D-012`;
3. `03_Methodology_Canonical_consolidated.md`, the benchmark plans, and any monograph wording are updated to match that freeze.

## Frozen dependencies already inherited from the project

This calibration stage must remain compatible with the benchmark contract that is already frozen elsewhere:

- wall-clock time is the universal cross-family effort axis;
- fair(time) refers to equal wall-clock opportunity under matched balance semantics, execution controls, and validation;
- stochastic repetition in the benchmark release is defined at the `(instance, algorithm, budget)` level;
- repeated-run collapse uses feasible validated runs only, with median final validated quality as the primary aggregate and median `elapsed_ms` as the tie-break.

The calibration stage may use a lighter two-phase schedule than the main benchmark campaign, but its evaluation logic must remain compatible with the benchmark release.

## Scope

The calibration stage covers only the stochastic participants of the canonical thesis portfolio:

- SA
- TS
- ILS
- GRASP

It does not tune METIS or KaHIP.

It does not authorize per-instance retuning in the main campaign.

## Calibration philosophy

The calibration procedure is intentionally bounded and conservative.

It is **not** a full autotuning study.
It is **not** a nested model-selection benchmark.
It is **not** allowed to expand into an open-ended search.

Its sole function is to choose one global final profile per stochastic participant before the main campaign starts.

## Calibration design

### Stage 1 — coarse screening

- Goal: eliminate clearly weak candidate profiles with a short, controlled racing stage.
- Panel size: 6 calibration instances.
- Seeds: `[42, 43, 44]`.
- Budget policy: same wall-clock semantics as the benchmark release, using the calibration budget defined in the companion YAML matrix.
- Decision unit: `(instance, algorithm, candidate_profile, budget)`.
- Collapse rule within Stage 1: feasible validated runs only; median final validated quality per candidate on each instance; tie-break by median `elapsed_ms`.

### Stage 2 — short confirmation

- Goal: compare only the finalists of Stage 1 under the full benchmark-style seed policy.
- Finalists per algorithm: top 2 candidate profiles from Stage 1.
- Seeds: `[42, 43, 44, 45, 46]`.
- Same collapse and tie rules as Stage 1.
- Output: one recommended final profile per stochastic participant.

## Calibration panel policy

The calibration panel must remain small but heterogeneous enough to expose clearly different search behaviors.

The panel should cover:

- at least one smaller/moderate synthetic case;
- at least one modularity-null or structurally harder case;
- at least one higher-CV case;
- at least one lower-CV case;
- at least one larger sparse/tree-like case.

The concrete panel used by the project is declared in `configs/hyperparameter_calibration_matrix.yaml`.

## Candidate-profile policy

The candidate grid must remain deliberately small.

Guideline:
- SA: at most 6 candidate profiles
- TS: at most 6 candidate profiles
- ILS: at most 4 candidate profiles
- GRASP: at most 6 candidate profiles

The purpose is screening, not exhaustive search.

## Selection rule

For each stochastic participant:

1. rank candidate profiles by per-instance collapsed quality across the calibration panel;
2. prefer profiles with better median validated quality;
3. use median `elapsed_ms` as the formal tie-break;
4. reject profiles that show unstable or systematically infeasible behavior even if they occasionally produce strong single runs;
5. promote exactly 2 finalists to Stage 2;
6. after Stage 2, recommend exactly 1 final profile for freeze.

## Outputs required from calibration

The calibration stage must generate enough material to support later insertion into the monograph and the canons.

Required outputs:

- calibration audit trail;
- candidate-profile table;
- per-instance collapsed comparison table;
- finalist-selection summary per algorithm;
- final recommended profile per algorithm;
- explicit statement that the main campaign remains blocked until D-012 is updated.

## Prohibitions

The following are forbidden in the calibration stage:

- retuning during the main benchmark campaign;
- per-instance final hyperparameter selection;
- post hoc switching of the chosen profile after the main campaign starts;
- using calibration outcomes as if they were benchmark-performance results;
- presenting the calibration stage as proof of superiority rather than as a controlled freeze procedure.

## Canonical wording boundary for later prose

Allowed wording after successful completion:

> A bounded pre-benchmark calibration stage was used to select one global hyperparameter profile for each stochastic participant before the main campaign.

Forbidden wording before mapped empirical support exists:

- “automatic tuning proved the best algorithm”
- “the tuning process optimized the benchmark”
- “the selected profiles are universally optimal”
- “the calibration results are themselves benchmark evidence”

## Dependency on the experiment ledger

This protocol is operational only through the planned experiment entry `EXP-CALIB-001` in `06_Experiment_Ledger.md`.
