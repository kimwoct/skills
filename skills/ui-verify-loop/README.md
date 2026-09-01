# ui-verify-loop

An agent skill: the closing gate for UI-visible fixes and changes. Companion to `ui-fix-loop`.

The fix loop proves a change *renders*; this skill proves the change is **right** (matches a user-named REFERENCE) and **shipped** (deployed, then re-checked end-to-end on the deployed environment) — with evidence on the review canvas — before a round may be called `FIXED`.

## Phases

- **Phase 0 — REFERENCE**: ask which reference to cross-check (official artifact, approved canvas preview, or a named environment's live behavior) and get approval of the intended end state *before* fixing. The approval question must name the reference.
- **Phase 1 — IMPLEMENT + LIVE VERIFY**: follow `ui-fix-loop` phases 3+; live-page evidence for every issue, loop until canvas and live page agree.
- **Phase 2 — DEPLOY + E2E CONFIRMATION**: deploy to the confirmed target env (FE and BE alike when both moved), re-run the reference cross-check *on the deployed environment* through the real user path, put the evidence on the canvas, and only then mark `FIXED — deployed & e2e-verified <env> <date>`.

See [SKILL.md](SKILL.md) for the full skill body, including the anti-patterns it exists to prevent.

## Install

Clone (or copy) this folder into your agent skills directory, e.g.:

```sh
git clone https://github.com/kimwoct/ui-verify-loop.git ~/.agents/skills/ui-verify-loop
```

Then pair it with a standing rule in your `AGENTS.md`, e.g.:

> When fixing a UI-visible bug or making a UI change, after the `ui-fix-loop` approval, apply `ui-verify-loop`: confirm the REFERENCE, and only call a round FIXED after deploying and re-verifying end-to-end on the deployed environment.
