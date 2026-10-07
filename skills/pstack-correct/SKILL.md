---
name: pstack-correct
description: Prevent recurring agent mistakes in a repository with architecture, types, lint, or regression checks, and prove the guard rejects a real past failure. Use for repeated corrections or an explicitly requested prevention pass, not ordinary one-off bug fixing.
license: MIT
metadata:
  source: cursor/plugins/pstack/skills/correct
  upstream-commit: d0ef80d86795816da932a153458c5dbe192d294e
---

# Prevent recurring mistakes

Turn an observed recurring mistake into an enforceable constraint, rather than another instruction an agent can miss.

## Establish the mistake and scope

Read the relevant corrections, commits, reverts, tests, and available review history. Group concrete failures by mechanism; distinguish a repeated class from a one-off. Two observed occurrences are useful evidence of recurrence, not permission to harden the entire repository. State the requested classes, evidence locations, and acceptance check before editing. If recurrence evidence is unavailable, say so rather than inventing a history.

A prevention review returns findings and a proposal. Implement guards only when the user has authorized those changes. A correction does not authorize unrelated cleanup, architecture changes, commits, or pull requests. For UI-visible changes, follow the repository's reference, preview, required-answer approval, and deployed-verification gates before changing real code.

## Choose the strongest proportionate mechanism

Consider these in order, keeping the change within the authorized scope:

1. **Structure:** remove duplicate ownership or hand-synchronized sources of truth; expose a supported boundary so the wrong path is unavailable. Prefer a small ownership or API change over a large speculative redesign. Remove alternate paths only when their callers and purpose are understood and removal is in scope.
2. **Types:** make the invalid combination or unsupported access unrepresentable at the relevant boundary.
3. **Lint or CI:** reject the dangerous pattern and name the supported replacement in the diagnostic. If legacy violations cannot be migrated in this task, guard against newly introduced violations without silently blessing the old ones.
4. **Behavioral regression check:** exercise the real failure at a seam that reaches its actual callers and side effects. Keep useful negative, structural, and mock-boundary tests; do not delete tests based on their assertion vocabulary.
5. **Guidance:** retain a concise instruction with a failure example when the choice requires judgment or no proportionate automatic guard exists.

When an instruction already exists but recurrence continues, identify the missing enforcement rather than appending the same wording. Explain why a stronger mechanism would not fit this case.

## Prove the guard

- Recreate a real past bad case in an isolated fixture or temporary worktree, without reverting the user's checkout or introducing unsafe live side effects.
- Run the supported check and show it rejects that case for the intended reason.
- Run the same check on the corrected case and on a nearby legitimate case to detect an overbroad guard.
- Run relevant existing checks. Distinguish local results from CI results; claim CI execution only if it actually ran.

A check that has only passed good code has not yet demonstrated prevention. If the bad case cannot be exercised, label the guard's effectiveness unproven and explain what evidence is missing.

If maintaining repository guidance is part of the request, keep a short rule-to-enforcement table with the mechanism and command. Replace redundant wording only after confirming the mechanism covers its intent; retain judgment rules and operational context. Preserve the project's exception and approval policy rather than creating automatic exemptions.

## Report and stop

For each requested class, give the observed failures, chosen mechanism, reason for not choosing a stronger one, changed paths, and bad-case / corrected-case / legitimate-case results. Stop when those classes are addressed and checked, or when a specific evidence or authorization gap prevents the next step. Do not turn the correction into a recurring background task.

Adapted from pstack `correct` and `principle-encode-lessons-in-structure` at the commit above. Copyright (c) 2026 Lauren Tan; see [LICENSE](LICENSE).
