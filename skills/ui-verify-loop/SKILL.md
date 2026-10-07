---
name: ui-verify-loop
description: "Closing gate for UI-visible fixes and changes, paired with ui-fix-loop. Use after a UI fix is implemented, when it must be proven against a user-named REFERENCE and confirmed on the deployed environment before the round is called FIXED. Also runs when the evidence canvas is a Whiteboard board — e.g. one produced by a similar prompt like \"produce the architecture-sketch Whiteboard (data flows, access patterns, code paths) and open it\" (whiteboard-agent-review Mode B)."
---

# UI Verify Loop

The companion to `ui-fix-loop`. The fix loop proves the change renders; the verify loop proves the change is **right** (matches a reference the user names) and **shipped** (deployed, then re-checked end-to-end on the deployed environment). A round that only passes locally is `IMPLEMENTED`, never `FIXED`.

**Tradeoff:** for trivial one-line changes with no layout or logic impact, keep this lightweight and use judgment.

## Coding-agent selection and Herdr sessions (global)

Apply `ui-fix-loop`'s **Coding-agent selection and Herdr sessions (global)** contract to coding work in every repository, including Whiteboard-hosted rounds:

- Offer installed coding agents before dispatch, default a new decision to **Pi**, and retain the user's saved explicit choice. Reuse the fix/logic round's approved decision; verification does not independently dispatch a duplicate coding run. For a Whiteboard-only round, record the choice with its numbered approval answers.
- Each dispatched coding run uses its own uniquely named persistent **Herdr terminal session**, not a pane in a shared session. Continue verification in the existing run/session where applicable; a new coding retry run gets a new session and remains subject to the approval contract. Missing agent or repository configuration is a blocker, never permission to substitute an agent silently.
- Include selected/assigned agent, dispatch state, run ID, and session ID in the evidence when a coding run exists. Confirm the actual session/process before reporting running. Preserve reference approval, deployment confirmation, and deployed end-to-end proof: updating these instructions alone is not a deployed runtime fix.

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

Finish Phase 1 by opening a PR from the round's worktree branch into its parent branch (`develop` by default — ui-fix-loop **Worktree and PR**). Mark the round `IMPLEMENTED — PR <url> → <parent>` and stop there. Never ask about deployment before or during implementation.

## Phase 2 — DEPLOY + E2E CONFIRMATION (later, after merge)

Run this phase only after the PR is merged **and** the user asks to deploy. It is never part of the pre-implementation approval questions.

1. **Confirm the deployment target with the user** (which env: UAT / prod / school server) and deploy the change there — frontend and backend alike when both moved.
2. **Re-run the reference cross-check ON the deployed environment**, not localhost: exercise the real user path (upload the artifact, download it back, generate the export, click the flow) and compare the result against the same Phase-0 reference.
3. Update the canvas with the deployed-environment evidence (what was checked, what came back). Every numbered issue must show deployed-env proof, not localhost proof.
4. **Traceability closes with the round.** For a round tied to a Conductor card, close the two-way canvas↔card link by ui-fix-loop's **Traceability** check — confirm both directions on the live surface and record the two URLs and their results in the canvas evidence. A round with no knowable card id skips this (the clean-heading exception); a round whose canvas the board cannot open, or that does not name its card, is not traceable end-to-end.
5. Only when canvas evidence and the deployed environment agree: mark the round `FIXED — deployed & e2e-verified <env> <date>`, deliver screenshots inline, and update memory.

## Whiteboard-hosted rounds

When the evidence canvas is a Whiteboard board — typically produced by a similar prompt like **"produce the architecture-sketch Whiteboard (data flows, access patterns, code paths) and open it"** (whiteboard-agent-review Mode B) — run the same phases with these translations:

- **Canvas = a Whiteboard session.** Record the board's pins (`worktree`/`commits`, base, head) as Phase-0 provenance: they name the revision every `review-source:` link on the board resolves against.
- **Phase 0 unchanged in substance.** The user must still name the reference, and approval stays explicit and numbered with required answers. For sketch-hosted rounds the realistic reference candidates are: a named environment's live behavior (strongest), the deployed branch the environment actually runs (e.g. up-to-date `develop`), or the board itself for pure-render rounds only. A sketch that cites code is **not** its own reference.
- **Cross-check = per-claim verification.** Re-resolve every code link at the pinned revision (`session_source` / `session_file` / `session_diff`) and re-exercise the flows the board asserts against the reference environment; write a per-claim `Verification` section on the board (claim → observed → agrees/differs), never a batch verdict.
- **Phase 1: fix the board, not the repo.** If the sketch drifted from reality, update the board under a fresh document lease (repin → read → edit). Only if the *reference itself* (env/artifact) turns out wrong or drifted is this a repo fix — and that becomes a new ui-fix-loop round with its own canvas.
- **Phase 2 unchanged.** Deployed-environment proof still means exercising the real user path on the named env; traceability URLs are recorded as board evidence. The closing label for a verification board is `VERIFIED — deployed & e2e-verified <env> <date>` (`FIXED` stays reserved for fix rounds). End the lease (`session_activity_end`) before `session_open` so the board reads as ready.
- **Evidence record.** Persist the whiteboard-agent-review JSON format with `agent: null` and `verification` entries pointing at the board's Verification section.
- **Authoring details, schemas, recovery.** See skill: whiteboard-agent-review (§Schema notes learned on a live v0.2 run; Mode B authoring contract; instance-switch recovery).

## Anti-patterns this skill exists to prevent

- Declaring victory on localhost while the deployed env still runs the old build/template/backend list.
- "Verifying" by re-reading code or API status codes instead of exercising the real artifact path end-to-end.
- Fixing toward an assumed reference; the user's named artifact is the only oracle, and drift between stored and reference state must be *reported*, never silently normalized.
- Skipping the reference/approval ask because the fix seems obvious — that ask is the whole point.
- Treating a Whiteboard sketch's code citations as verification: citing code is provenance, not proof; sketch-hosted rounds still owe deployed-environment evidence before any `VERIFIED` label.
