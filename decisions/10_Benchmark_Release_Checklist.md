# 10_Benchmark_Release_Checklist.md

## Purpose

This file is a decision-ready scaffold for the benchmark release. It exists to organize what must be closed before the benchmark campaign starts, without prematurely freezing methodological choices that remain open.

## Rule of use

This file does **not** freeze new methodology by itself. It only:
- lists the current release blockers;
- records where future frozen decisions must be inserted;
- organizes the operational pre-release sequence; and
- prevents benchmark execution from starting under ambiguous protocol conditions.

Any final methodological choice referenced here becomes canonical only after being frozen in `01_Decision_Log.md` and mirrored in `03_Methodology_Canonical_consolidated.md`.

## Stable inputs already frozen before this checklist

The following project truths are already frozen and may be used as stable dependencies of the release process:

- canonical serialized time fields: `elapsed_ms` and `checkpoints[].time_ms`;
- stochastic repetition unit: `(instance, algorithm, budget)`;
- stochastic repetition count and seed policy: `n_rep = 5`, seeds `[42, 43, 44, 45, 46]`;
- repeated-run collapse before comparison and ASP labeling;
- ASP target `y_i*(T*)` defined over the collapsed per-instance table rather than raw runs.

These items are treated here as prerequisites, not as open design questions.

## Benchmark-release blockers that still require final decisions

| Blocker | Current source | What is still missing | Canonical insertion target |
|---|---|---|---|
| External-validity boundary of WSL2 environment | OI-007 / D-009 | Final wording and explicit methodological caveat | `01_Decision_Log.md`, `03_Methodology_Canonical_consolidated.md`, monograph threats-to-validity section |
| Analytical benchmark synthesis metrics | OI-008 / D-010 | Exact operational definitions of TTT, ECDF, performance profiles, and regret | `01_Decision_Log.md`, `03_Methodology_Canonical_consolidated.md`, analysis scripts |
| ASP outer validation protocol | OI-009 / D-011 | Final external split policy | `01_Decision_Log.md`, `03_Methodology_Canonical_consolidated.md`, selector evaluation scripts |
| Final stochastic hyperparameter profiles | OI-010 / D-012 | Frozen final values for SA, TS, ILS, GRASP | `01_Decision_Log.md`, `03_Methodology_Canonical_consolidated.md`, plans/configs |
| Final artifact-schema confirmation | OI-011 | Final cross-check of runner/manifest/schema contract | `03_Methodology_Canonical_consolidated.md`, docs/specs, audit report |
| Campaign preregistration | OI-012 / D-014 | Final planned ledger entries for pilot and main campaign | `06_Experiment_Ledger.md` |
| Conceptual benchmark figures clearance | OI-013 | Final technical clearance and conceptual-only wording where required | `05_Figures_Equations_Register.md`, monograph figure captions/body |
| CART model-selection regime | OI-014 / D-015 | Final choice between fixed configuration and searched regime | `01_Decision_Log.md`, `03_Methodology_Canonical_consolidated.md`, selector scripts |

## Operational release gates

The benchmark release is considered decision-ready only after the following gates are prepared.

### Gate A — Repository and documentation readiness
- [ ] Active documentation aligned to the current canon
- [ ] Legacy/quarantine material clearly marked
- [ ] MkDocs build checked and remaining nav loose ends reviewed
- [ ] README / protocol / reproducibility docs checked for benchmark-release coherence

### Gate B — Execution surface readiness
- [ ] Runner and artifact schema revalidated against current outputs
- [ ] Split benchmark plans tracked and executable
- [ ] Docker image and execution environment revalidated
- [ ] Branch hygiene reviewed before release cut

### Gate C — Methodological freeze insertion
- [x] D-009 finalized or superseded
- [ ] D-010 finalized or superseded
- [ ] D-011 finalized or superseded
- [x] EXP-CALIB-001 completed and reviewed
- [x] D-012 finalized or superseded
- [ ] D-014 finalized or superseded
- [ ] D-015 finalized or superseded

### Gate D — Campaign preregistration
- [ ] `EXP-BENCH-PILOT-001` completed as a real planned entry
- [ ] `EXP-BENCH-MAIN-001` completed as a real planned entry
- [ ] The pilot campaign is blocked from execution until its preregistration is complete
- [ ] The main campaign is blocked from execution until pilot review is complete

## Decision insertion sheet

This section exists only to make final freeze insertion short and local later.

### D-009 — WSL2 external-validity boundary
- Final status:
- Final wording:
- Files to update:
- Notes:

### D-010 — TTT / ECDF / performance profiles / regret
- Final status:
- Final wording:
- Files to update:
- Notes:

### D-011 — ASP outer validation protocol
- Final status:
- Final wording:
- Files to update:
- Notes:

### D-012 — Final stochastic hyperparameter freeze
- Final status:
- Final wording:
- Files to update:
- Notes:

### D-014 — Benchmark campaign preregistration policy
- Final status:
- Final wording:
- Files to update:
- Notes:

### D-015 — CART model-selection regime
- Final status:
- Final wording:
- Files to update:
- Notes:

## Canonical preregistration placeholders required before execution

The benchmark campaign should eventually appear in the ledger as at least two distinct entries:

1. `EXP-BENCH-PILOT-001`
   - role: dry-run / pilot validation under the frozen protocol
   - current state here: placeholder only, not execution-authorizing

2. `EXP-BENCH-MAIN-001`
   - role: main comparative benchmark campaign
   - current state here: placeholder only, not execution-authorizing

## Stop rule

The benchmark main campaign must **not** start while any of the following remain true:

- one or more high-severity benchmark blockers remain open;
- the canonical methodology still leaves central analysis terms underdefined;
- the pilot and main campaign are not preregistered in `06_Experiment_Ledger.md`;
- the current execution surface has not been revalidated under the release candidate state.
