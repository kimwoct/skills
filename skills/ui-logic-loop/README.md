# ui-logic-loop

An agent skill: the logic-flow sibling of `ui-fix-loop`. Pixels get a canvas; **logic gets a sequence diagram**.

One archify diagram pair accompanies the change through its whole lifecycle — **REVIEW → PREVIEW → IMPLEMENT → VERIFY → DEPLOY** — looping until the as-shipped diagram and the deployed system agree.

Approval questions are **mandatory**: every open decision (cache layer and TTL, abort scope, deploy order, whether a fetch stays or goes) is presented as a numbered question with the recommended answer stated. A chat approval counts only if it answers **every** numbered question in so many words — typing `OK` against a recommended default is fine, but it must be typed. Silence never selects a default.

**Division of labor:** a UI-visible change goes to `ui-fix-loop` (canvas); a logic-visible change goes here (diagrams). A change that moves both runs both loops — one canvas + one diagram pair, each gating its own surface.

## Phases

- **Phase 1 — REVIEW**: trace the CURRENT flow with evidence (live network capture, curl replay of server actions, or server logs — code reading supplements but does not replace observation), author the CURRENT diagram from that trace with redundancies and measured costs marked, and write the numbered change list with a measurable expected effect per item.
- **Phase 2 — PREVIEW**: author the AFTER diagram for the intended end state, ask every open decision as a numbered question, and **wait for approval before touching real code**.
- **Phase 3 — IMPLEMENT + VERIFY**: implement, run the project's checks, re-trace the live flow, author the as-shipped diagram from the fresh trace, and loop until the as-shipped diagram, the numbered change list, and the live trace all agree.
- **Phase 4 — DEPLOY + E2E CONFIRMATION**: deploy to the confirmed target (both deployables when both moved), re-run the same trace *on the deployed environment*, and only then mark the round `FIXED — deployed & flow-verified <env> <date>`. A round that only passes locally is `IMPLEMENTED`, never `FIXED`.

See [SKILL.md](SKILL.md) for the full skill body, including the diagram-sizing rules and the anti-patterns it exists to prevent.

## What it ships with

- `SKILL.md` — the skill body (phases, diagram rules, anti-patterns).

Diagram authoring is delegated to the separate **`archify`** skill (MIT, not part of this collection) and its Node CLI — this folder does not bundle it. Diagram candidates and their JSON specs are written outside every repo, under `~/.agents/ui-logic-loop/<repo>/`, so nothing is committed by accident.

## Install

Clone (or copy) this folder into your agent skills directory, e.g.:

```sh
git clone https://github.com/kimwoct/skills.git /tmp/skills
cp -R /tmp/skills/skills/ui-logic-loop ~/.agents/skills/ui-logic-loop
```

Then pair it with a standing rule in your `AGENTS.md`, e.g.:

> When fixing a logic-visible bug or making a change to data flow, API orchestration, server actions, caching, or background jobs, apply the `ui-logic-loop` skill.
>
> - Before implementing: trace the current flow, build the archify sequence diagram pair (CURRENT with redundancies marked, PREVIEW of the intended end-state), and number every open decision as a required question.
> - A chat approval must answer every numbered question — silence never picks a default.
> - Wait for the user's approval of the PREVIEW diagram before touching real code.
> - After implementing: re-trace the live flow, author the as-shipped diagram from the fresh trace, and loop until the diagrams match the observed behavior. Mark the round FIXED only after the same trace passes on the deployed environment.
