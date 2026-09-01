---
name: ui-fix-loop
description: Loop-engineering workflow for UI-visible bug fixes and UI changes. Use before drilling into or implementing any frontend/UI fix that changes what the user sees. Maintains a single review HTML canvas that (1) lists and highlights the parts to be fixed, (2) previews the intended end result for user approval before real code is touched, and (3) is updated with live-page evidence after implementation, looping fix → verify until the canvas matches the live result.
---

# UI Fix Loop

A standing workflow for UI bug fixes, usable in any project. One HTML canvas accompanies the fix through its whole lifecycle: **REVIEW → PREVIEW → IMPLEMENT → VERIFY**, looping until the canvas and the live page agree.

**Tradeoff:** for trivial one-line changes with no layout or logic impact, keep this lightweight and use judgment — the loop is mandatory for anything where pixels or interaction change.

## The canvas

- Path: `~/.agents/ui-fix-canvas/<repo>/<issue-slug>.html` — outside every repo, so scratch files are never committed and no per-project setup is needed.
- ONE file per issue, updated in place through the phases. Never fork it into per-phase copies.
- Plain hand-written HTML/CSS replicating the relevant UI region — no framework, no build step.
- Every canvas includes the approval widget: add `<script src="/canvas-approval.js"></script>` before `</body>`. It renders a floating panel with a **required answer box per open question**, a comment input, and Approve / Request-changes buttons that POST to the server's decision API.

## Serving the canvas (server.py + Tailscale)

- Serve with `python3 ~/.agents/ui-fix-canvas/server.py` (port 8791, localhost). It extends a static server with a decision API: `POST /api/decision {canvas, status, comment}` writes `<repo>/<slug>.decision.json`; `GET /api/decision?canvas=...` reads it back (`status` is `pending` | `approved` | `changes-requested`). Do NOT use bare `python3 -m http.server` — it has no decision API.
- Browsers in agent sessions can only open http(s) pages: open `http://localhost:8791/<repo>/<issue-slug>.html`. Screenshot it for the user when presenting.
- Expose the same server to the user's tailnet so they can review on any of their devices: `tailscale serve --bg 8791` → `https://<machine>.<tailnet>.ts.net/<repo>/<issue-slug>.html` (this machine: `mk1a3zpmacbook-pro.tail490654.ts.net`). If serve reports "not enabled on your tailnet", print the enable link it returns and ask the user to open it once, then run the serve command again.
- The agent learns the decision by reading the `.decision.json` file or GET-ing the API on localhost. A chat reply approving is equally valid — the widget is a convenience, not the only channel.

## Phase 1 — REVIEW (before drilling down)

Before reading implementation code in depth, build the canvas in its REVIEW state:

- A mock of the **broken** UI region as it currently renders (replicate the defect faithfully — e.g. the duplicated rail rows).
- A numbered **issue list**: one line per defect, each with a concrete expected behavior.
- Numbered **highlight markers** on the mock, one per issue, so list ↔ region mapping is visible at a glance.

## Phase 2 — PREVIEW (approval gate)

Update the same file to show the **intended end result** (the same region as it should render after the fix), keeping the issue list with each item marked "pending fix".

**Mandatory question answers — silence never approves.** Every open decision (template vs alternative, keep/drop a category, code numbers, deploy scope …) must be rendered on the canvas as a numbered question with its own required textbox:

`<textarea class="approval-answer" data-question="① <short question>" placeholder="recommended: … (type OK, or your answer)"></textarea>`

The widget moves these into its panel and keeps Approve / Request-changes **disabled until every box is filled** — typing `OK` on a recommended default is fine, but it must be typed. The answers are stored in the decision record (`answers` + composed `comment`). A chat reply approves only if it answers **every** numbered question in so many words; a bare "approved" / "looks good", or silence on any point, is NOT consent to a recommended default — re-ask, listing the unanswered numbers, and wait again.

Present the canvas to the user and state the intended end result in one or two sentences. **Wait for the user's approval before touching real code** — given either as a chat reply that answers every question, or via the canvas approval widget (check the decision API: only `approved` with all answers present opens the gate; `changes-requested` means fold the comment into the preview and re-present). A wrong preview is the cheapest possible failure — this gate exists because fixes built on wrong assumptions (verified symptom area only, adjacent behavior unbroken-checked) ship regressions.

## Phase 3 — IMPLEMENT, then VERIFY (the loop)

1. Implement the real fix in the project code.
2. Run the project's checks (typecheck, tests, build).
3. Load the **live page** and capture evidence (DOM facts and/or screenshot) for every numbered issue.
4. Update the same canvas: mark each issue fixed or still-broken from the live evidence, with an after-rendering beside the original mock.
5. If any issue is not confirmed fixed on the live page, loop back to step 1. Only report completion when the canvas's fixed state and the live page match.

## Anti-patterns this skill exists to prevent

- Reading silence as consent — an unanswered approval question is an open question, not a default selected. No "silence on a point = take the default" phrasing, ever.
- Verifying only the region the user pointed at while the change alters a shared predicate consumed by other regions.
- Declaring "fixed" from code reading alone, without re-observing the live rendered page.
- Patching the same visual bug repeatedly because each fix is validated against the symptom, not against the full grid of affected states.
