---
name: ui-fix-loop
description: Loop-engineering workflow for UI-visible bug fixes and UI changes. Use before drilling into or implementing any frontend/UI fix that changes what the user sees. Maintains a single review HTML canvas that (1) lists and highlights the parts to be fixed, (2) previews the intended end result for user approval before real code is touched, and (3) is updated with live-page evidence after implementation, looping fix → verify until the canvas matches the live result.
---

# UI Fix Loop

A standing workflow for UI bug fixes, usable in any project. One HTML canvas accompanies the fix through its whole lifecycle: **REVIEW → PREVIEW → IMPLEMENT → VERIFY**, looping until the canvas and the live page agree.

**Tradeoff:** for trivial one-line changes with no layout or logic impact, keep this lightweight and use judgment — the loop is mandatory for anything where pixels or interaction change.

## The canvas

- Path: `~/.agents/ui-fix-canvas/<repo>/<issue-slug>.html` — outside every repo, so scratch files are never committed and no per-project setup is needed. The `<repo>` segment must be a lowercase-hyphen slug (`ai-leave-management-frontend`, never the GitHub-cased name) and, when the canvas should dispatch work, a key in the dispatch-watcher's `REPOS` map; root-level pages (`/<slug>.html`) are rejected too. A non-conforming segment makes every Approve POST 404 "unknown canvas" with no other symptom.
- ONE file per issue, updated in place through the phases. Never fork it into per-phase copies.
- Plain hand-written HTML/CSS replicating the relevant UI region — no framework, no build step.
- Every canvas includes the approval widget: add `<script src="/canvas-approval.js"></script>` before `</body>`. It renders a floating panel with a **required answer box per open question**, a comment input, and Approve / Request-changes buttons that POST to the server's decision API. The gate keys off the questions declared as `approval-answer` fields (Phase 2) — a canvas with the script but no such fields has a widget with nothing to gate.
- **The heading carries the board task no.** When the work has a Conductor card — a canvas dispatch, or any request that can be tied to a card — begin both `<h1>` and `<title>` with `[t-<id8>]` (e.g. `<h1>[t-3ecb9f12] 前後測活動報告 …</h1>`), taken from the card's `display_id`. The raw `:8791` URL has no board chrome, so the heading is the only place the id can appear. When no card id is knowable, leave the heading clean rather than guessing — a wrong prefix is worse than none.
- **Traceability is two-way and is part of the deliverable:**
  - canvas → card: the `[t-<id8>]` heading above. A canvas opened from its bare tailnet URL is anonymous without it.
  - card → canvas: the card's `canvas` field must be `<repo>/<slug>` — that field is what the board card modal, the Inbox rows, and the `/requirement-canvas/<cardId>` board route render as the review link. Canvas dispatches write it at intake; for any other origin (interactive rounds, card created before/without the canvas), set it at canvas-creation time, not when the user goes looking for it. Setting it needs conductor tooling — `conductor.kanban_update` from a session that has it, or the dashboard card edit — so a session without conductor access must ask the conductor session to write the link rather than skip it.
  - Verify both directions before presenting: `GET /requirement-canvas/<cardId>` → 200 with `<title>t-<id8> · requirement canvas</title>`, and the served canvas `<title>` begins with `[t-<id8>]`. Query the tailnet board URL (the tailnet identity authenticates); on `localhost:8798` a session cookie is required or the GET redirects to `/login`. If either direction fails, the round is not reviewable end-to-end and must not be presented as ready.

## Serving the canvas (server.py + Tailscale)

- The canvas server normally runs under launchd (`com.kxxwxxg.canvas.server`, port 8791, localhost) — start `python3 ~/.agents/ui-fix-canvas/server.py` by hand only if it is down (a manual start while launchd holds the port just fails to bind). It extends a static server with a decision API: `POST /api/decision {canvas, status, comment}` writes `<repo>/<slug>.decision.json`; `GET /api/decision?canvas=...` reads it back (`status` is `pending` | `approved` | `changes-requested`). Do NOT use bare `python3 -m http.server` — it has no decision API.
- Before handing the URL to the user, prove the canvas is wired: `GET /api/decision?canvas=<repo>/<slug>` → `{"status":"pending"}`. That one request catches an unwired Approve button, a non-conforming repo segment, and a mistyped id — a 404 "unknown canvas" here means the widget would silently do nothing for the user too.
- Browsers in agent sessions can only open http(s) pages: open `http://localhost:8791/<repo>/<issue-slug>.html`. Screenshot it for the user when presenting.
- Expose the same server to the user's tailnet so they can review on any of their devices: `tailscale serve --bg 8791` → `https://<machine>.<tailnet>.ts.net/<repo>/<issue-slug>.html` (this machine: `mk1a3zpmacbook-pro.tail490654.ts.net`). If serve reports "not enabled on your tailnet", print the enable link it returns and ask the user to open it once, then run the serve command again.
- The agent learns the decision by reading the `.decision.json` file or GET-ing the API on localhost. A chat reply approving is equally valid — the widget is a convenience, not the only channel.
- Driving the dashboard API by curl (e.g. to check `/requirement-canvas/<cardId>`): `POST /login` wants a JSON body (`-H 'Content-Type: application/json' -d '{"token":"…"}'`, token in `~/.conductor/dashboard-token`) plus an `Origin` header — form-encoded bodies get 415. On the tailnet board URL (`:8443`) no token is needed: the tailnet identity authenticates.

## Phase 1 — REVIEW (before drilling down)

Before reading implementation code in depth, build the canvas in its REVIEW state:

- A mock of the **broken** UI region as it currently renders (replicate the defect faithfully — e.g. the duplicated rail rows).
- A numbered **issue list**: one line per defect, each with a concrete expected behavior.
- Numbered **highlight markers** on the mock, one per issue, so list ↔ region mapping is visible at a glance.

**Done when:** every defect the review found is a numbered issue with a matching marker on the mock, and the canvas opens in a browser.

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
