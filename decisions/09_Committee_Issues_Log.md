# 09_Committee_Issues_Log.md

## Purpose

This file converts committee and reviewer comments into a trackable issue log. Each item should eventually be marked as resolved, revised, or intentionally deferred with justification.

## Status legend

- **Open**: not yet addressed
- **In progress**: currently being revised
- **Resolved**: revised and checked
- **Deferred**: intentionally postponed with reason

## Issues

### CI-001 — General objective is too large and too far from the title
- **Status:** Open
- **Source:** Committee notes
- **Problem:** The current general objective is overloaded and should be more similar to the title.
- **Derived rule:** Keep the general objective short, central, and free of compressed methodological detail.
- **Affected section:** 1.2 Objective general
- **Action owner:** Writing Surgery + Governance and Integrity

### CI-002 — Specific objectives are not all true objectives
- **Status:** Open
- **Source:** Committee notes
- **Problem:** Some specific objectives read as workflow steps rather than deliverables.
- **Derived rule:** Rewrite each specific objective as a real delivery or analytical commitment.
- **Affected section:** 1.3 Specific objectives
- **Action owner:** Writing Surgery

### CI-003 — File names are fixed too directly in the running prose
- **Status:** Open
- **Source:** Committee notes
- **Problem:** The text names files too explicitly in places where the representation matters more than the file label.
- **Derived rule:** Prefer describing what an artifact represents; move concrete file names to appendix or reproducibility sections when necessary.
- **Affected section:** Cross-document sweep
- **Action owner:** Writing Surgery + Governance and Integrity

### CI-004 — Bold and emphasis should be removed
- **Status:** Open
- **Source:** Committee notes
- **Problem:** Body-text emphasis is stylistically discouraged.
- **Derived rule:** Remove bold and emphatic formatting from the running prose.
- **Affected section:** Whole document
- **Action owner:** Writing Surgery

### CI-005 — Figure legends should be shorter
- **Status:** Open
- **Source:** Committee notes
- **Problem:** Legends are explaining too much.
- **Derived rule:** Captions identify and orient; interpretation belongs in the body.
- **Affected section:** Figures and list of figures
- **Action owner:** Writing Surgery + Final Release Audit

### CI-006 — Objectives are truncated and hard to digest
- **Status:** Open
- **Source:** Committee notes
- **Problem:** Objective wording is too dense and less clear than the oral presentation version.
- **Derived rule:** Prefer cleaner syntax and one dominant action per objective.
- **Affected section:** 1.2 and 1.3
- **Action owner:** Writing Surgery

### CI-007 — Concepts need more explanatory care
- **Status:** Open
- **Source:** Committee notes
- **Problem:** Terms such as wall-clock time may require more didactic explanation.
- **Derived rule:** Explain core benchmarking terms at first use; use footnotes when that improves readability.
- **Affected section:** Introduction / methodology first-use points
- **Action owner:** Theory and Evidence Audit + Writing Surgery

### CI-008 — The text should become clearer and easier to understand
- **Status:** Open
- **Source:** Committee notes
- **Problem:** Global clarity is below the desired level.
- **Derived rule:** Simplify aggressively without losing technical precision.
- **Affected section:** Whole document
- **Action owner:** Writing Surgery

### CI-009 — A motivating problem from the introduction should be unpacked in Chapter 2
- **Status:** Open
- **Source:** Committee notes
- **Problem:** The bridge between motivation and related work needs stronger didactic continuity.
- **Derived rule:** Take at least one motivating problem from the introduction and dissect it more clearly in Chapter 2.
- **Affected section:** Chapters 1 and 2 interface
- **Action owner:** Theory and Evidence Audit + Writing Surgery

### CI-010 — Exploratory baselines must not contaminate the official thesis portfolio
- **Status:** Open
- **Source:** Governance and integrity audit
- **Problem:** The executable repository flow allowed an exploratory greedy baseline to enter the official phase-1 plans, conflicting with the frozen monograph portfolio.
- **Derived rule:** Exploratory baselines may remain in the repository, but they must stay outside official plans, official manifests, and the selector label space unless canon is updated first.
- **Affected section:** Methodology / portfolio scope / experimental governance
- **Action owner:** Governance and Integrity + Code and Experiments

<!-- HBF-FRONTIER-CONFIRMATION-001:COMMITTEE_ISSUES:START -->
## Frontier confirmation evidence slice: srv_noctua_frontier_pilot_001

This block records a validated exception-mining confirmation slice. It is evidence-bearing only for the explicit environment slice `srv_noctua_frontier_pilot_001`; it is not, by itself, the final benchmark campaign and does not finalize monograph-level claims.

Source chain: `screening_short_001` → selection plan `750` → schema-compatible confirmation plan `756` → `confirmation_001` → validation report `758` → evidence map `759`.

Committee-facing interpretation:

- The confirmed frontier slice strengthens the motivation for instance-level analysis: many candidates selected by screening remained strong after confirmation.
- The result should be presented cautiously: it demonstrates that the framework can mine and confirm exception regimes under a controlled slice, not that the final benchmark conclusions are already settled.
- The negative controls are informative: `5` candidates remained stable non-exception controls, while `2` negative-control candidates became competitive or mixed.
- This supports a clearer argument for selection-by-instance and explanatory modeling, but the monograph should keep the distinction between exploratory evidence, confirmed slice evidence and final benchmark evidence.
<!-- HBF-FRONTIER-CONFIRMATION-001:COMMITTEE_ISSUES:END -->

## Frontier expansion 002 — committee-facing evidence note (2026-05-11)

The second frontier expansion produced a validated confirmation slice with `4000` planned runs, `4000` valid results and `0` invalid results in `wsl_local_frontier_expansion_002`.

Committee-safe framing:

- The result strengthens the methodological claim that the benchmark can discover and then confirm exception regimes under a controlled protocol.
- The result does not finalize cross-environment claims; environment pooling remains forbidden unless explicitly justified.
- The result supports a clearer discussion of why confirmation is necessary after screening: several candidates changed status between screening hypotheses and confirmation labels.
- The evidence remains bounded to the explicit environment slice until mapped into the broader experimental synthesis.
