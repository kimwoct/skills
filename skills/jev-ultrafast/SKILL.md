---
name: jev-ultrafast
description: Drive browser automation and agent loops with Jev (browser-use/jev-ultrafast) — indexed-element web agent on Browser Harness. Use when the user says "jev", asks to run the Jev agent, or wants browser actions (click/type/select/scroll) executed through Jev or its browser-harness layer, including clicking download buttons and verifying downloads.
---

# Jev Ultrafast

Fast, indexed-action browser agent. One goal → the TypeSafe policy picks an
operation (CLICK / TYPE_TEXT / SELECT / SCROLL_UP / SCROLL_DOWN / WAIT / DONE /
BLOCKED) and one indexed element per decision cycle.

Working repo: `~/tools/jev-ultrafast` (clone of github.com/browser-use/jev-ultrafast).
Run everything from that directory with `uv run`.

## Requirements

- `TYPESAFE_API_KEY` (required — hosted policy at api.typesafe.ai; stored in `<repo>/.env`)
- `TEXT_MODEL_API_KEY` (only needed for TYPE_TEXT text generation; clicks work without it)
- Chrome + Browser Harness (auto-installed by `uv sync`; check with `uv run browser-harness --doctor`)

## Run the agent

```bash
cd ~/tools/jev-ultrafast
uv run --env-file .env python - <<'PY'
from jev_ultrafast import Agent

with Agent("https://example.com", "Goal in one sentence. Stop when the result is visible.") as agent:
    for state in agent.run():
        print(state["elapsed_ms"], state["status"])
PY
```

Demo inspector: `uv run jev` → open http://127.0.0.1:8766.
If Chrome needs connecting: `uv run browser-harness --doctor`; macOS permission
sheet: `uv run browser-harness mac-approve`.

## Browser-only mode (no API key)

Jev's browser layer is Browser Harness; it works without keys for direct control:

```bash
cd ~/tools/jev-ultrafast && uv run browser-harness <<'PY'
ensure_real_tab()
print(page_info())
PY
```

Key helpers: `new_tab(url)` (first nav), `goto_url`, `wait_for_load`,
`page_info()`, `js(...)`, `cdp("Accessibility.getFullAXTree")["nodes"]`
(filter in Python — thousands of nodes), `DOM.getBoxModel` → `click_at_xy(x, y)`,
`current_tab()`, `list_tabs()`, `switch_tab()`, `activate_tab(target)`.
Close tabs you created; never close the user's own tabs.

## Verified download-button test recipe

For a page with download buttons: attach one tab, wait until the target content is RENDERED (not merely hydrated — a loading skeleton also has body text), find the visible button copies
(print containers duplicate DOM off-screen — only click the copy whose box has
positive size), snapshot the download dir before/after each click, and diff.

Two hard-won gotchas:
1. **Keep the tab open AFTER the loop `done`s.** Closing immediately kills any
   in-flight async fetch that produces the download (Jev clicks at ~900ms; a
   PDF may land 1–3s later). Poll the download dir first, close the tab last.
2. **Warm-up on content, not words.** Wait for a marker that only exists once
   data loaded (e.g. a table row or a known label), not `body.innerText.length`.

```bash
cd ~/tools/jev-ultrafast && uv run --env-file .env python - <<'PY'
import time
from pathlib import Path
from jev_ultrafast import Agent

DL = Path("/tmp/jev-downloads")
before = {(p.name, p.stat().st_mtime) for p in DL.glob("*")}
agent = Agent("http://localhost:7899/zh-Hant/survey-management/report/<docId>?type=individual&responseSetId=<id>",
              "Click the button named '<button text>' once it is visible, then stop.")
try:
    for i in range(60):  # wait for DATA, not just hydration
        try:
            ok = agent.browser.evaluate("[...document.querySelectorAll('button')].some(b => b.innerText.trim() === '<button text>') && document.body.innerText.includes('<data marker>')")
            if ok: break
        except Exception: pass
        time.sleep(0.5)
    agent.state["page"] = agent.browser.observe(screenshot=False)
    for state in agent.run(): pass
    for i in range(20):  # tab STAYS OPEN while the async fetch completes
        time.sleep(1)
        new = {(p.name, p.stat().st_mtime) for p in DL.glob("*")} - before
        if new: print("download:", sorted(n for n,_ in new)); break
finally:
    agent.close()
PY
```

Arm/restore controlled downloads around the run (browser-level, from any session):

```bash
browser-use <<'PY'
cdp("Browser.setDownloadBehavior", behavior="allow", downloadPath="/tmp/jev-downloads", eventsEnabled=True)
# ... run ... then restore:
cdp("Browser.setDownloadBehavior", behavior="default", eventsEnabled=False)
PY
```

`behavior="allowAndName"` saves as UUIDs; `"allow"` keeps real filenames.

## Notes / limits

- Shadow roots, frames, canvas, uploads, popup tabs are outside the Jev MVP.
- A `DONE` from the policy still requires independent outcome verification by you.
- `scripts/check_guards.py` runs offline (real controls, no model calls) for harness sanity checks.