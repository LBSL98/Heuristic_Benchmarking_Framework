# 08_Results_to_Text_Map.md

## Purpose

This file maps empirical results to the exact claims they are allowed to support in the monograph. Its purpose is to prevent overclaim and to make every conclusion auditable.

## Mapping template

| Claim ID | Monograph claim | Supported by experiment(s) | Supported by figure/table | Support strength | Allowed wording | Forbidden wording | Notes |
|---|---|---|---|---|---|---|---|
| C-XXX |  |  |  | Strong / Partial / Weak |  |  |  |

## Rules

1. If a claim has no mapped support, it should not survive final revision.
2. “Strong support” means the evidence directly matches the claim scope.
3. “Partial support” requires narrower wording in the monograph.
4. “Forbidden wording” is mandatory whenever results are easy to overstate.

| Claim ID | Monograph claim | Supported by experiment(s) | Supported by figure/table | Support strength | Allowed wording | Forbidden wording | Notes |
|---|---|---|---|---|---|---|---|
| C-REPO-001 | The final repository state used in the monograph was stabilized through a controlled integration process, with code and documentation merged separately before final release integration. | EXP-REPO-001 | None | Strong | “the final repository state was stabilized through a controlled integration sequence” | “the repository is fully reproducible in every respect” / “all experimental claims are validated by this alone” | Governance/reproducibility support only; not performance evidence. |

| C-GREEDY-001 | The repository contains an exploratory greedy baseline used for engineering validation outside the official thesis benchmark portfolio. | EXP-GREEDY-001 | None | Strong | “an exploratory greedy baseline exists in the repository for engineering validation” | “greedy is part of the canonical benchmark portfolio” / “greedy is one of the official selector labels of the thesis” | Governance/engineering only; not benchmark-scope evidence. |
