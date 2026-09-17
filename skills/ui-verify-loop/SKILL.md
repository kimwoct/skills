---
name: ui-verify-loop
description: "Closing gate for UI-visible fixes and changes. Runs AFTER a fix is implemented (typically via ui-fix-loop) and proves it against a user-named REFERENCE: ask which reference to cross-check and get approval BEFORE fixing, then live-verify, then DEPLOY to the target environment and run an end-to-end confirmation against the same reference — with evidence on the review canvas — before a round may be called FIXED."
---

# UI Verify Loop

The companion to `ui-fix-loop`. The fix loop proves the change renders; the verify loop proves the change is **right** (matches a reference the user names) and **shipped** (deployed, then re-checked end-to-end on the deployed environment). A round that only passes locally is `IMPLEMENTED`, never `FIXED`.

**Tradeoff:** for trivial one-line changes with no layout or logic impact, keep this lightweight and use judgment.

## Phase 0 — REFERENCE (before any fix is applied)

A fix without a reference is guessing. Before touching code:

1. **Ask the user what the reference is** and record it on the canvas. Valid references, strongest first:
   - an official artifact the user supplies (a template file, a spec, a design export, a prod paste of expected data);
   - the approved canvas preview itself (for pure-visual rounds);
   - a named environment's live behavior (e.g. "prod wfjlps renders it this way").
2. **Cross-check the current state against that reference** and put the diff on the canvas — what differs, cell by cell / element by element. This diff, not the symptom, defines the work.
3. **Get explicit approval of the intended end state** (the ui-fix-loop PREVIEW gate) before implementing. The approval question must name the reference: "aligned to <file/env>, approve?" — and every open decision must be a numbered canvas question with a **required textbox answer** (ui-fix-loop Phase 2 mandatory-answer rule): the widget unlocks only when all boxes are filled, and a chat approval counts only if it answers every numbered question. Silence never selects a default, here or in any later round.

## Phase 1 — IMPLEMENT + LIVE VERIFY

Follow `ui-fix-loop` phases 3+: implement, run the project's checks, capture live-page evidence for every issue, update the canvas, loop until canvas and live page agree.

## Phase 2 — DEPLOY + E2E CONFIRMATION (the closing gate)

1. **Confirm the deployment target with the user** (which env: UAT / prod / school server) and deploy the change there — frontend and backend alike when both moved.
2. **Re-run the reference cross-check ON the deployed environment**, not localhost: exercise the real user path (upload the artifact, download it back, generate the export, click the flow) and compare the result against the same Phase-0 reference.
3. Update the canvas with the deployed-environment evidence (what was checked, what came back). Every numbered issue must show deployed-env proof, not localhost proof.
4. **Traceability closes with the round.** For rounds tied to a Conductor card (a round with no knowable card id skips this — the clean-heading exception), confirm the two-way canvas↔card link on the live/deployed surface before `FIXED`: `GET /requirement-canvas/<cardId>` returns 200 with the `t-<id8> · requirement canvas` chrome (the tailnet board URL authenticates via the tailnet identity; `localhost:8798` needs a session cookie), and the served canvas `<title>`/`<h1>` begin with `[t-<id8>]`. Record both checks (URL + result) in the canvas evidence section. A round whose canvas cannot be opened from the board, or whose canvas does not name its card, is not traceable end-to-end — the same standard as any other verification.
5. Only when canvas evidence and the deployed environment agree: mark the round `FIXED — deployed & e2e-verified <env> <date>`, deliver screenshots inline, and update memory.

## Anti-patterns this skill exists to prevent

- Declaring victory on localhost while the deployed env still runs the old build/template/backend list.
- "Verifying" by re-reading code or API status codes instead of exercising the real artifact path end-to-end.
- Fixing toward an assumed reference; the user's named artifact is the only oracle, and drift between stored and reference state must be *reported*, never silently normalized.
- Skipping the reference/approval ask because the fix seems obvious — that ask is the whole point.
