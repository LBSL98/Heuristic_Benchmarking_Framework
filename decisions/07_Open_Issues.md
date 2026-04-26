# 07_Open_Issues.md

## Purpose

This file tracks unresolved project problems that can still affect coherence, correctness, methodological validity, or delivery quality.

## Open issues

### OI-001 — General objective is too long and overloaded
- **Type:** Writing / framing
- **Severity:** High
- **Origin:** Committee feedback
- **Current status:** Open
- **Needed action:** Rewrite the general objective into a shorter, title-aligned version.

### OI-002 — Specific objectives mix deliverables with workflow steps
- **Type:** Writing / structure
- **Severity:** High
- **Origin:** Committee feedback
- **Current status:** Open
- **Needed action:** Rewrite specific objectives as concrete deliverables or analytical commitments.

### OI-003 — Main prose is too coupled to file names and transient artifacts
- **Type:** Writing / reproducibility framing
- **Severity:** High
- **Origin:** Committee feedback
- **Current status:** Open
- **Needed action:** Sweep the text and replace file-name anchoring with representational descriptions.

### OI-004 — Figure legends are too long
- **Type:** Writing / figures
- **Severity:** Medium
- **Origin:** Committee feedback + current list of figures
- **Current status:** Open
- **Needed action:** Shorten captions and move interpretation into body text.

### OI-005 — Some benchmarking concepts may still be hard to digest
- **Type:** Theory / methodology / writing
- **Severity:** Medium
- **Origin:** Committee feedback
- **Current status:** Open
- **Needed action:** Add clearer first-use explanations for wall-clock time and related concepts.

### OI-006 — Official benchmark prose and final monograph text still require canonical cleanup
- **Type:** Writing / methodology alignment
- **Severity:** High
- **Origin:** Canon vs prose audit
- **Current status:** Open
- **Needed action:** Keep the official thesis narrative aligned with the canonical portfolio, artifact contract, and release-candidate documentation without reintroducing exploratory scope into benchmark claims.

### OI-007 — WSL2 external-validity boundary is still not frozen
- **Type:** Methodology / environment / validity
- **Severity:** Medium
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-009`. The audited WSL2 environment is accepted as the controlled benchmark surface for internal comparison, with explicit restriction against overgeneralizing absolute timing results to bare-metal or arbitrary external environments.

### OI-008 — Analytical benchmark synthesis metrics are still not frozen
- **Type:** Methodology / analysis
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-010` for the benchmark-synthesis layer. `TTT`, `ECDF`, and `performance profiles` now have canonical operational definitions. Selector regret was deliberately removed from this freeze and remains deferred to the selector-evaluation track under `D-011` / `D-015`.
### OI-009 — ASP outer validation protocol is still not frozen
- **Type:** Methodology / selector evaluation
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Open
- **Needed action:** Freeze the outer validation protocol used to evaluate the selector so that selector claims are not left under multiple admissible interpretations.
- **Clarifying note:** This freeze also becomes the canonical anchor for selector regret, which is intentionally deferred from `D-010` until the outer-validation protocol is uniquely frozen.
### OI-010 — Final stochastic hyperparameter freeze is still provisional
- **Type:** Methodology / calibration / benchmark protocol
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Resolved
- **Needed action:** Frozen by `D-012` after completion of `EXP-CALIB-001`. The canonical release profiles are now `grasp_b`, `ils_b`, `sa_e_maxsteps_100000`, and `ts_c`, and no retuning is allowed in the main benchmark campaign.

### OI-011 — Final artifact-schema confirmation must be canonically closed
- **Type:** Artifact contract / schema / runner
- **Severity:** Medium
- **Origin:** Benchmark release preparation
- **Current status:** Open
- **Needed action:** Promote the already completed runner/schema confirmation into the canonical record so that the release no longer treats artifact-contract confirmation as a pending blocker.

### OI-012 — Benchmark pilot and main campaign preregistration are still placeholders
- **Type:** Governance / experiment registration
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Open
- **Needed action:** Replace placeholder benchmark ledger entries with execution-authorizing planned entries before pilot and main campaign execution.

### OI-013 — Conceptual benchmark figures still need final technical clearance
- **Type:** Figures / writing / methodology
- **Severity:** Medium
- **Origin:** Benchmark release preparation
- **Current status:** Open
- **Needed action:** Review benchmark figures and captions to ensure conceptual-only diagrams are clearly distinguished from empirical result figures.

### OI-014 — CART model-selection regime is still not frozen
- **Type:** Methodology / selector model selection
- **Severity:** High
- **Origin:** Benchmark release preparation
- **Current status:** Open
- **Needed action:** Freeze whether the canonical selector evaluation uses a fixed CART configuration or a searched regime, and define its relation to the outer validation protocol.

### OI-015 — MkDocs navigation still leaves one active page outside nav
- **Type:** Documentation / publication surface
- **Severity:** Low
- **Origin:** MkDocs audit
- **Current status:** Open
- **Needed action:** Decide whether `docs/specs/mealpy_integration_plan.md` should enter the active nav or remain intentionally unlisted and documented as such.

## Notes

- This file tracks what is still unresolved.
- Resolved matters should move to the canonical decision, ledger, methodology, or release-checklist layers rather than remain here indefinitely.
