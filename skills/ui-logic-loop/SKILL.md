---
name: ui-logic-loop
description: Loop-engineering workflow for LOGIC-visible changes — data flow, API orchestration, server actions, caching, aborts, background jobs. Use before implementing any change to how calls are sequenced, deduped, batched, or cancelled (changes invisible in pixels but visible in the request waterfall). Maintains an archify sequence diagram pair — CURRENT (as-traced, redundancies marked) and PREVIEW (intended end-state) — for user approval before real code is touched, then re-traces the live flow after implementation and loops until the as-shipped diagram matches deployed reality.
---

# UI Logic Loop

The logic-flow sibling of `ui-fix-loop`. Pixels get a canvas; **logic gets a sequence diagram**. One archify diagram pair accompanies the change through its whole lifecycle: **REVIEW → PREVIEW → IMPLEMENT → VERIFY → DEPLOY**, looping until the as-shipped diagram and the deployed system agree.

**Tradeoff:** for trivial one-line changes with no flow impact (a constant, a guard already covered by tests), keep this lightweight and use judgment — the loop is mandatory for anything where call ordering, request count, payload shape, or cancellation behavior changes.

**Division of labor:** UI-visible change → `ui-fix-loop` (canvas). Logic-visible change → this skill (diagrams). A change that moves both pixels and flow runs both loops — one canvas + one diagram pair, each gating its own surface.

## Coding-agent selection and Herdr sessions (global)

Apply `ui-fix-loop`'s **Coding-agent selection and Herdr sessions (global)** contract to coding work in every repository:

- Offer installed coding agents before dispatch, default a new decision to **Pi**, and preserve an explicitly saved selection. On diagram-only rounds, record the choice with the numbered approval answers; on combined UI/logic rounds, use the same canvas decision rather than launching a second worker.
- Run each dispatched coding run in its own uniquely named persistent **Herdr terminal session**, not merely a separate pane. A new retry run gets a new session; resuming the same run reuses its session. Honor the approved agent, preserve active-run deduplication, and report missing agent/repository configuration without silent fallback.
- Keep preview/reference approval and required answers as the execution gate. Record agent, dispatch state, run ID, and session ID with the flow evidence; verify the real session/process before reporting running. This requirement does not authorize runtime changes, deployment, or extra coding-agent launches by itself.

## The diagrams

- Invoke the `archify` skill and follow its authoring contract. Call chains / request lifecycles → type `sequence`; component-shape changes → `architecture`; state/retry machines → `lifecycle`.
- Path: `~/.agents/ui-logic-loop/<repo>/<issue-slug>-before.html` and `-after.html`, with the candidate JSONs beside them (`-before.sequence.json`, `-after.sequence.json`) — outside every repo, so nothing is committed by accident. `<repo>` is a lowercase-hyphen slug (e.g. `jckak-e-platform`).
- TWO candidates, one meaning each: **CURRENT** = the flow as it behaves today, built from evidence (live trace preferred, code reading as fallback); **PREVIEW** = the intended end-state. They are separate files — never fork phases into edits of one file, and never edit a candidate after its validation passes (the archify contract freezes it; re-author fresh instead).
- Mark flow facts as variants: redundant/duplicate calls → `variant: "dashed"` with a `note` starting `REDUNDANT — <why + file:line>`; slow/oversized calls → `variant: "emphasis"` with the measured number in the label (`— 7.8s`, `/ 4.3MB`). Numbers come from the trace, not from estimates.
- Sizing rules learned the hard way: keep a sequence to ≤ ~12 messages; push detail into `note` fields instead of labels; tall viewBoxes fail the desktop-fit visual check (scrollHeight overflow at 1920/2048) while narrow ones fail projected-font readability — target a near-square viewBox (~1040×540–850) and drop conclusion cards (the metrics table lives in chat/the ticket, not the diagram).

## Phase 1 — REVIEW (trace before theorizing)

1. Trace the CURRENT flow with evidence: live network capture in the browser (fetch logger via browser-use, or DevTools waterfall), curl replay of server actions, or server-side logs. Code reading supplements but does not replace observation — the same standard as ui-fix-loop's live-page rule.
2. Author the CURRENT diagram from that trace: every request in order, redundancies and costs marked per the variant rules above.
3. Write the **numbered change list**: one line per intended change, each with a measurable expected effect ("×3 → ×1 `users/me` per analytics pass", "4.3MB → ≤0.5MB", "~31 prefetch no-ops → 0").

## Phase 2 — PREVIEW (approval gate)

Author the AFTER diagram showing the **intended end-state flow** (same participants, same message ordering as it should behave after the change), keeping the numbered change list alongside.

**Mandatory question answers — silence never approves.** Every open decision (cache layer and TTL, abort scope, whether a fetch stays or goes — never deployment target or order) must be presented as a **numbered question** with the recommended answer stated. A chat reply approves only if it answers **every** numbered question in so many words; typing "OK" against a recommended default is fine, but it must be typed. A bare "approved" / "LGTM", or silence on any point, is NOT consent to a recommended default — re-ask, listing the unanswered numbers, and wait again.

Present both diagram paths (or open them) and state the intended end-state in one or two sentences with the headline metric. **Wait for the user's approval before touching real code.** A wrong flow preview is the cheapest possible failure — this gate exists because flow fixes built on wrong assumptions (traced symptom only, adjacent consumers unchecked) ship regressions: an "unused" call deleted that another view mounted, a cache that served stale scoped data to a different role.

## Phase 3 — IMPLEMENT, then VERIFY (the loop)

1. Implement the real change in project code.
2. Run the project's checks (typecheck, tests, build).
3. Re-trace the LIVE flow the same way as Phase 1 and capture per-change evidence: the before metric → after metric for every numbered item (request counts, payload bytes, durations, prefetch counts).
4. Author the as-shipped diagram from the fresh trace (new candidate files — `-shipped` or overwrite `-after` only by re-authoring) and check it against the PREVIEW: every intended change present, nothing else moved.
5. If any numbered change is not confirmed by the live evidence, loop back to step 1. Only report completion when the as-shipped diagram, the numbered change list, and the live trace all agree.

Finish Phase 3 by opening a PR from the round's new worktree branch into its parent branch (`develop` by default — ui-fix-loop **Worktree and PR**) and mark the round `IMPLEMENTED — PR <url> → <parent>`. Deploy order and target are not approval questions.

## Phase 4 — DEPLOY + E2E CONFIRMATION (later, after merge)

Run only after the PR is merged and the user asks to deploy. Borrowed from `ui-verify-loop` because logic changes lie about being fixed more often than pixel changes do:

1. Confirm the deployment target with the user and deploy — **both deployables when both moved** (e.g. Next.js app + Strapi backend in the same repo-pair), stating explicitly which side carries each numbered change.
2. Re-run the same trace ON the deployed environment (not localhost) and confirm every numbered metric there.
3. Only then mark the round `FIXED — deployed & flow-verified <env> <date>` with the before/after metric table inline. A round that only passes locally is `IMPLEMENTED`, never `FIXED`.

## Anti-patterns this skill exists to prevent

- Reading silence as consent — an unanswered approval question is an open question, not a default selected. No "silence on a point = take the default" phrasing, ever.
- Authoring the diagram from code reading alone and calling it "current" — untraced flows omit the calls that only fire at runtime (prefetches, internal re-auths, queue serialization).
- Assuming a client-side abort/cancel stops server-side work — server actions keep running past disconnect unless the server observes cancellation; verify with a probe before claiming the burn stops.
- Fixing the counted symptom while a shared consumer still calls the old path (the "different consumer" trap — e.g. a page-size constant shared by a table and an analytics loop).
- Declaring "fixed" from code review alone, without re-observing the live request waterfall.
- Treating local verification as shipped — logic only provably changed when the deployed environment's trace says so.
