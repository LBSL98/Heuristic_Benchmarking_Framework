# 07_Open_Issues.md

## Purpose

This file tracks unresolved project problems that can affect coherence, correctness, or delivery quality.

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

### OI-006 — Executable official pipeline still does not materialize the canonical anytime portfolio
- **Type:** Code / methodology alignment
- **Severity:** High
- **Origin:** Canon vs pipeline audit
- **Current status:** Open
- **Needed action:** Keep `greedy` out of official plans and later align the executable official campaign with the canonical portfolio (SA, TS, ILS, GRASP, METIS, KaHIP) without allowing exploratory baselines to contaminate thesis claims.

### OI-007 — Canonical anytime portfolio is still not executable in the main runner
- **Type:** Code / methodology alignment
- **Severity:** High
- **Origin:** Canonical portfolio readiness audit
- **Current status:** Open
- **Needed action:** Integrate SA, ILS, and GRASP into the main runner one by one, keeping the official flow unchanged until each solver is validated against the current artifact schema and wall-clock protocol.

### OI-008 — Tabu Search implementation source is currently unavailable for porting
- **Type:** Code availability / portfolio completion
- **Severity:** High
- **Origin:** Legacy repository portability audit
- **Current status:** Open
- **Needed action:** Locate a valid TS implementation or implement it later under the same canonical runner contract. Until then, TS remains a documented portfolio gap rather than an implicit promise.
