---
name: pstack-blast-radius
description: Review what a change could break beyond its diff and test the critical fact that makes it safe. Use for blast-radius analysis, downstream compatibility concerns, or a small diff whose hidden effects need proof.
license: MIT
metadata:
  source: cursor/plugins/pstack/skills/blast-radius
  upstream-commit: d0ef80d86795816da932a153458c5dbe192d294e
---

# Prove a change's blast radius

A caller list is a starting point. The useful result is the critical safety fact, its evidence, and concrete downstream risks the diff alone hides.

## Establish the boundary

Read the requested diff, changed symbols, relevant callers, and the actual pinned dependency versions and local patches. Check repository guidance and use an existing code graph if present before falling back to source search. Keep a review read-only: do not silently edit product code or dependencies. A small disposable proof harness is appropriate only within the task's permitted local operations.

## Find the load-bearing fact

State the one or two facts on which safety depends, such as a cleanup operation touching only expired entries. Trace beyond symbol references where relevant:

- lifecycle and ordering: asynchronous scheduling, callbacks, teardown, unmount, retries;
- contracts: API payloads, database columns, serialized bytes, other-language consumers;
- configuration: flags, caching, version differences, patched dependencies;
- indirect effects: event subscribers, reflection, generated clients, and callers several hops away.

Read the implementation the application actually uses, not just a convenient latest version. Do not invent a caller or treat a failed search as proof that none exists; record what was searched and its limits.

## Make evidence distinguishable

For each safety fact, state the strongest level actually reached:

1. **Hypothesis:** an assertion without independent evidence.
2. **Source-backed:** a concrete file and line or pinned library implementation.
3. **Path analysis:** a traced bad case cannot reach the dangerous operation under stated assumptions.
4. **Executed proof:** a script or test calls the real implementation and fails if the safety fact is false.
5. **Application reproduction:** the actual running application exercises the relevant path.

Prefer an inexpensive executed proof for the central fact. Use the shipped library/function and the real failure condition; a mock that merely repeats the assumption cannot prove it. Show the invocation, exit status, observed output, and asserted behavior. Keep evidence from static reasoning separate from execution.

Use an owned disposable instance for application reproduction. Existing authorization, isolation/refusal, and UI reference/approval gates still apply; do not drive a shared session or bypass a harness restriction to get a stronger evidence label. If execution requires unavailable access or unauthorized effects, mark the fact unproven and give the smallest safe next check.

## Report and stop

Lead with severity-ranked confirmed findings and file:line references. Then provide:

- what changed, including hidden behavior;
- the central safety fact, evidence level, proof result, and assumptions;
- remaining credible risks: mechanism, consequence, confidence, and a targeted check;
- cleared risks and the evidence clearing them;
- the smallest regression check needed before merge, and any unproven fact.

Do not manufacture numeric risk probabilities or a long list of remote hypotheticals. Stop once the central facts and credible downstream paths are assessed. The review does not authorize a merge, commit, external post, or unrelated repair.

Adapted from pstack `blast-radius` at the commit above. Copyright (c) 2026 Lauren Tan; see [LICENSE](LICENSE).
