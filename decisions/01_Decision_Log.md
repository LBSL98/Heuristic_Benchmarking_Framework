# 01_Decision_Log.md

## Purpose

This file records frozen project decisions. A decision only becomes canonical after being written here.

## Status legend

- **Proposed**: discussed, not yet frozen.
- **Frozen**: accepted as current project truth.
- **Superseded**: replaced by a later decision.

## Decision entries

### D-001 — Project governance architecture
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** The project will use a multi-chat structure with role separation: Governance and Integrity, Theory and Evidence Audit, Writing Surgery, Code and Experiments, and Final Release Audit.
- **Rationale:** Prevent role collapse, reduce context drift, and force cross-audit between theory, writing, and code.
- **Impact:** No single chat is treated as authoritative by itself.

### D-002 — Canonical-source policy
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** Project truth will be maintained in canonical markdown files stored as project sources, not only in conversation history.
- **Rationale:** Chat continuity alone is not sufficient for a long and high-stakes academic project.
- **Impact:** All significant revisions must update the corresponding canonical file.

### D-003 — Dual storage policy for guidance documents
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** Normative project files must exist both in Drive and in the project sources whenever possible.
- **Rationale:** Drive works as durable repository; project sources work as active context.
- **Impact:** Editorial and methodological rules should not be kept only in external folders.

### D-004 — Writing feedback is normative
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** Committee and reviewer comments are treated as normative constraints until explicitly resolved.
- **Rationale:** The current stage is revision under committee scrutiny, not greenfield drafting.
- **Impact:** Rewriting must follow `04_Writing_Constraints.md` and `09_Committee_Issues_Log.md`.

### D-005 — Naming convention
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** File and artifact names used in project support files will remain in English.
- **Rationale:** Aligns with the project naming preference already adopted by the user.
- **Impact:** New support files should follow English names consistently.

## Template for new entries

### D-XXX — Title
- **Status:** Proposed | Frozen | Superseded
- **Date:** YYYY-MM-DD
- **Decision:**
- **Rationale:**
- **Impact:**
- **Supersedes / Superseded by:**

### D-006 — Final repository stabilization before monograph freeze
- **Status:** Frozen
- **Date:** 2026-03-12
- **Decision:** The final repository state was stabilized through a controlled integration sequence: code hardening first, minimal defensible documentation second, and final integration into `main` only after branch governance and required checks were aligned.
- **Rationale:** Prevented mixing implementation corrections with over-broad documentation claims and ensured that the final branch state matched the auditable project scope.
- **Impact:** The monograph and defense materials must describe only the repository state and documentation subset that survived this stabilization process.
- **Supersedes / Superseded by:**

### D-007 — Greedy demoted from official benchmark flow
- **Status:** Frozen
- **Date:** 2026-03-30
- **Decision:** The `greedy` baseline remains available in the repository only as an exploratory / engineering track and is not part of the official benchmark portfolio, official phase-1 plans, or the canonical selector label space.
- **Rationale:** The canonical monograph portfolio is currently frozen as SA, TS, ILS, GRASP, METIS, and KaHIP. Keeping `greedy` in the official flow would create scope drift between canon, pipeline, and prose.
- **Impact:** Official plans exclude `greedy`; exploratory plans may preserve it under separate filenames; no monograph claim may treat `greedy` as a canonical benchmark participant unless a later canonical decision supersedes this one.
- **Supersedes / Superseded by:**
