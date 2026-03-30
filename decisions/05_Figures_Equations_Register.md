# 05_Figures_Equations_Register.md

## Purpose

This file tracks every figure and equation that matters to the monograph. Its job is to prevent explanatory drift, overlong legends, symbolic inconsistency, and unsupported formal statements.

## How to use

For each figure or equation, register what it is, why it exists, where it is interpreted, and whether the current wording is approved.

## Figures register

| ID | Type | Current title / description | Function in argument | Where interpreted in text | Caption status | Technical validation | Notes |
|---|---|---|---|---|---|---|---|
| Fig. 6 | Figure | 1-move operator illustration | Explain local move semantics and delta-eval intuition | To confirm | Needs shortening | Pending | Caption currently explains too much in the list of figures. |
| Fig. 7 | Figure | Pilot validation and crossover behavior | Motivate ASP timing window concept | To confirm | Needs shortening | Pending | Caption likely over-explains conceptual meaning. |
| Fig. 8 | Figure | Conceptual performance profile | Explain Dolan–Moré profile intuition | To confirm | Needs shortening | Pending | Keep interpretation in body text, not caption. |
| Fig. 9 | Figure | Conceptual TTT distribution | Explain ECDF / time-to-target intuition | To confirm | Needs shortening | Pending | Same issue as above. |
| Fig. 10 | Figure | Morphological domain map | Summarize qualitative domain preference idea | To confirm | Needs shortening | Pending | Check if wording promises more than conceptual illustration. |
| Fig. 11 | Figure | CART decision tree example | Explain interpretable selector logic | To confirm | Needs shortening | Pending | Ensure no confusion between conceptual tree and trained final model. |

## Equations register

| ID | Current role | Symbols defined? | Motivated before use? | Linked to code/analysis? | Status | Notes |
|---|---|---|---|---|---|---|
| Eq. (1) | Formalize edge cut | Partially confirmed | Confirmed in introduction | Pending cross-check | Review | Verify symbol definitions and downstream consistency. |

## Validation rules

1. A caption identifies and orients; it does not replace the discussion.
2. Every equation must be motivated, symbol-defined, and tied to the surrounding argument.
3. No conceptual figure may be mistaken for an empirical result.
4. If the body text does not interpret the element, the element is not ready.
