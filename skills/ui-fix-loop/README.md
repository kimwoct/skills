# ui-fix-loop

An agent skill: loop-engineering workflow for UI-visible bug fixes and UI changes, usable in any project. One review canvas accompanies the fix through its whole lifecycle: **REVIEW → PREVIEW → IMPLEMENT → VERIFY**, looping until the canvas and the live page agree.

Approval questions are **mandatory**: every open decision is rendered as a numbered question with a required textbox — the approval widget keeps Approve / Request-changes disabled until every box is filled (typing `OK` for a recommended default is fine, but it must be typed). Silence never selects a default, and a chat approval counts only if it answers every numbered question.

Pair with [ui-verify-loop](https://github.com/kimwoct/ui-verify-loop): the fix loop proves the change renders; the verify loop proves it is *right* (matches a user-named reference) and *shipped* (deployed, then re-checked end-to-end) before a round may be called FIXED.

## Repo contents

- `SKILL.md` — the skill body (phases, serving instructions, anti-patterns).
- `ui-fix-canvas/canvas-approval.js` — the approval widget included by every canvas; enforces the mandatory per-question answers and posts the decision.
- `ui-fix-canvas/server.py` — canvas server (stdlib-only): serves the canvas directory and provides the `/api/decision` API that records `approved` / `changes-requested` + per-question answers to `<canvas>.decision.json`.

## Install

```sh
git clone https://github.com/kimwoct/ui-fix-loop.git /tmp/ui-fix-loop
mkdir -p ~/.agents/skills/ui-fix-loop ~/.agents/ui-fix-canvas
cp /tmp/ui-fix-loop/skills/ui-fix-loop/SKILL.md /tmp/ui-fix-loop/skills/ui-fix-loop/README.md ~/.agents/skills/ui-fix-loop/
cp /tmp/ui-fix-loop/ui-fix-canvas/canvas-approval.js /tmp/ui-fix-loop/ui-fix-canvas/server.py ~/.agents/ui-fix-canvas/
```

Run the canvas server and expose it to your tailnet for review on other devices:

```sh
python3 ~/.agents/ui-fix-canvas/server.py        # http://localhost:8791
tailscale serve --bg 8791                        # first run prints a one-time enable link
```

Then pair it with a standing rule in your `AGENTS.md`, e.g.:

> When fixing a UI-visible bug or making a UI change, apply the `ui-fix-loop` skill: build/update the review canvas, preview the intended end result, and wait for approval — answering every numbered approval question — before touching real code; after implementing, live-verify every listed issue and loop until the canvas matches the live page.
