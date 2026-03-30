# 04_Writing_Constraints.md

## Purpose

This document defines the non-negotiable writing constraints for the monograph. Its function is to keep the text clear, technically disciplined, stylistically consistent, and aligned with the committee feedback. These constraints apply to all future revisions, rewrites, insertions of new text, figure legends, equation explanations, and final editorial passes.

## Order of precedence

When there is conflict between possible writing choices, use this order of precedence:

1. Factual correctness and methodological fidelity.
2. Explicit committee and reviewer feedback.
3. Clarity and readability for an informed academic reader.
4. Stylistic consistency with the monograph as a whole.
5. Brevity, as long as precision is preserved.

## Core editorial objective

The monograph must become clearer, more readable, more direct, and easier to understand without losing technical rigor. Simplification is not permission to become vague. Every simplification must preserve the exact technical meaning.

## Global writing rules

The text must privilege precise claims over inflated phrasing. Avoid generic academic padding, ornamental intensity, and rhetorical overstatement. Do not claim robustness, superiority, relevance, fairness, reproducibility, explainability, efficiency, scalability, or generality unless the claim is explicitly supported by the methodology, the literature, or the reported results. Distinguish observed result, interpretation, design choice, and hypothesis.

Each paragraph must have a clear function. A paragraph should either define a concept, justify a decision, describe a method, interpret an outcome, delimit scope, or connect two ideas. Paragraphs that try to do too many things at once must be split.

Sentences must prefer explicit syntax over stacked qualifications. Avoid long chains of dashes, parentheses, and embedded subordinate clauses when the same idea can be expressed in two cleaner sentences.

## Objectives section rules

The general objective must be shorter, closer to the title, and centered on the real research goal rather than on a compressed list of methodological details. Material that describes operational means, implementation choices, or secondary deliverables should be moved out of the general objective and, when appropriate, absorbed into specific objectives or later methodological sections.

Each specific objective must describe a real deliverable or analytical commitment. A specific objective must not be merely a workflow step, an execution detail, or a low-level operational action. If an item answers “how the work will be done” rather than “what concrete objective will be achieved,” it probably belongs in methodology, not in the objectives list.

The objectives must be written in cleaner, less truncated language. Prefer direct verbal constructions with one main action per bullet. Avoid overloading each objective with metrics, implementation details, and multiple nested justifications.

## Rule for file names, versions, and implementation artifacts

Do not hard-code file names, version labels, local artifact names, or transient implementation details in the running prose unless they are genuinely essential for scientific reproducibility. Prefer describing what the artifact represents rather than naming the file itself. For example, instead of anchoring the explanation in a specific file name, describe it as the system report, the execution manifest, the validation schema, the experiment contract, or the generated audit artifact.

When a concrete filename or version string is necessary, place it where it belongs: appendix, repository documentation, artifact table, footnote, or reproducibility subsection. The main body should remain stable even if file names or versions change.

## Emphasis, typography, and visual cleanliness

Do not use bold or emphasis for argumentative force inside the body text. Technical precision must carry the emphasis, not formatting. Use capitalization with restraint. Avoid unnecessary uppercase forms inside the prose.

## Figure, table, and code listing rules

Figure legends must be shorter and must not try to replace the surrounding explanation. A legend should identify what the figure is, what is being shown, and what the reader should notice at first glance. The full interpretation belongs in the body text, not in the legend.

Tables and code listings must follow the same principle. Their captions should identify purpose and scope, but not absorb the entire analytical discussion.

Every figure, table, and listing included in the monograph must satisfy three questions before remaining in the document: what exactly it shows, why it is necessary for the argument, and where its interpretation is completed in the text.

## Concepts and didactic clarity

Potentially unfamiliar technical expressions must be explained at first use in language that is academically correct but easier to digest. If a term is central and may be obscure to a non-specialist committee member, add a compact explanation in the prose or use a footnote when that improves flow.

This applies especially to concepts whose operational meaning matters for the method, such as wall-clock time, fairness protocol, NFE, performance profiles, ECDF, TTT, regret, and related benchmarking terminology.

## Chapter-level coherence

The introduction must not accumulate all conceptual burden alone. If a concrete motivating problem appears in the introduction, at least one such problem should be unpacked more carefully in Chapter 2 so that the reader sees the bridge between motivation, related work, and methodological choices.

The structure of the introduction may be preserved if it still serves the argument, but the prose inside it must be simplified, clarified, and de-densified. Structural preservation is not an excuse to preserve opaque wording.

Sublevel numbering and hierarchical subdivision must be used only when they increase navigability. If a subsection exists only to hold a very short or weakly differentiated fragment, merge it.

## Equations and formal statements

Every equation introduced in the text must satisfy four conditions: it must be motivated before appearing, its symbols must be defined, its role in the argument must be explicit, and its connection to the implementation or analysis must be recoverable.

Do not insert equations merely to increase formal appearance. Conversely, do not rely on prose alone when an equation is necessary to remove ambiguity.

When the text states equivalence, implication, fairness, comparability, dominance, or statistical support, the wording must match the exact methodological meaning used in the document.

## Claims and evidence discipline

No strong claim may remain in the final text without an identifiable support source. Support can come from one of three places: literature, formal methodological definition, or reported experiment. If a sentence cannot be tied to one of these three, it must be weakened, moved, or removed.

The monograph must not promise future empirical findings in sections that precede execution unless the wording is explicitly prospective. Proposal-like language must be kept separate from result-like language.

## LLM-specific prohibitions

Do not use inflated transitions, repetitive “this work” constructions, empty summary phrases, mechanical contrast formulas, or generic statements that sound polished but add no content. Avoid the typical pattern of repeating the same idea in three synonymous ways. Avoid pseudo-precision and decorative abstraction.

When rewriting, prefer subtraction over embellishment. The revision should remove noise, not add verbal mass.

## Operational revision protocol

Any future rewrite must be checked against this document before being accepted. The reviewer must verify at least the following:

- the passage is clearer than before;
- no technical meaning was lost;
- no unsupported claim was introduced;
- no file name or transient artifact was unnecessarily fixed in the prose;
- no bold or emphasis remained in the body text;
- legends remain concise;
- the paragraph has one dominant rhetorical function;
- the wording sounds written by a careful human researcher, not by a generic text generator.

## Immediate priority actions

1. Rewrite the general objective into a shorter and more title-aligned form.
2. Rewrite the specific objectives so that each one is a real deliverable.
3. Sweep the monograph for file names, versions, and transient artifact references in the main prose.
4. Remove boldface and emphasis from the running text.
5. Shorten figure legends that are currently over-explanatory.
6. Add clearer first-use explanations for central benchmarking concepts.
7. Revisit the introduction and Chapter 2 connection so that at least one motivating application is unpacked with more explanatory depth.
8. Perform a final anti-LLM editorial pass focused on rhythm, redundancy, and artificial phrasing.

## Status note

This file is normative. If future committee feedback contradicts any rule here, update this file first and only then revise the text.
