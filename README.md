# skills

Essential agent skills collection: engineering workflow, UI, research, and writing
skills for AI coding agents (Claude Code, Codex, ZCode, …).

Each skill is a self-contained folder (`skills/<name>/SKILL.md` plus any supporting
files) that you drop into your agent's skills directory. The companion loop skills
`ui-fix-loop`, `ui-logic-loop`, and `ui-verify-loop` are included here; the first and
last are also maintained in their own repos
([ui-fix-loop](https://github.com/kimwoct/ui-fix-loop),
[ui-verify-loop](https://github.com/kimwoct/ui-verify-loop)).

## Included skills

| Skill | What it does |
|---|---|
| `code-review` | Reviews changes since a fixed point along two axes — Standards and quality — with agent-ready briefs |
| `codebase-design` | Shared vocabulary for designing deep modules: interface design, deepening opportunities |
| `conductor-board` | Drive work through the Conductor kanban board (localhost:8798): routed task cards, state machine, G0–G5 TDD-first work tickets, verify contract with evidence |
| `diagnosing-bugs` | Diagnosis loop for hard bugs and performance regressions |
| `domain-modeling` | Build and sharpen a project's domain model / ubiquitous language |
| `frontend-design` | Create distinctive, production-grade frontend interfaces |
| `handoff` | Compact the current conversation into a handoff document for another agent |
| `implement` | Implement a piece of work from a spec or set of tickets |
| `karpathy-guidelines` | Behavioral guidelines that reduce common LLM coding mistakes |
| `orchestration` | Coordinate supervised Orca workers: threaded messages, blocking ask/reply, task dispatch, worker_done/escalation waits, task DAGs, decision gates (full ownership handoffs use `orca-cli`) |
| `pstack-benchmark-checklist` | Validate a runtime performance measurement — limiter, comparable tuning, error counting, completed work, physical limits, repetitions, end-to-end relevance — before reporting a speedup or technology choice |
| `pstack-blast-radius` | Review what a change could break beyond its diff and prove the load-bearing safety fact (evidence levels: hypothesis → source-backed → executed proof → app reproduction) |
| `pstack-correct` | Prevent recurring agent mistakes with proportionate guards (structure/types/lint/regression checks) proven to reject a real past failure |
| `pstack-create-verification-skill` | Generate a project-local verification skill that launches and drives the real UI/CLI/service, checks instance ownership, retains evidence, and cleans up |
| `prototype` | Build a throwaway prototype to answer a design question |
| `research` | Investigate a question against high-trust primary sources |
| `resolving-merge-conflicts` | Resolve an in-progress git merge/rebase conflict |
| `tdd` | Test-driven development — red-green-refactor and integration testing |
| `triage` | Move issues and external PRs through a state machine of triage roles |
| `ui-fix-loop` | Loop-engineering workflow for UI bug fixes: REVIEW → PREVIEW (approval gate) → IMPLEMENT → VERIFY on one HTML canvas |
| `ui-logic-loop` | Loop-engineering workflow for logic-visible changes (data flow, API orchestration, caching, jobs): an archify sequence-diagram pair — CURRENT → PREVIEW (approval gate) → IMPLEMENT → VERIFY on the deployed flow |
| `ui-verify-loop` | Closing gate after a UI fix: proves the change matches a named REFERENCE and is deployed + e2e-verified; also runs Whiteboard-hosted verification rounds (whiteboard-agent-review Mode B) |
| `vercel-react-best-practices` | React and Next.js performance optimization guidelines from Vercel Engineering |
| `writing-great-skills` | Reference for writing and editing skills well |

## Install

Clone (or copy) the whole collection into your agent skills directory:

```sh
git clone https://github.com/kimwoct/skills.git ~/.agents/skills
```

or copy individual skills:

```sh
mkdir -p ~/.agents/skills
cp -R skills/code-review skills/tdd ~/.agents/skills/
```

Each skill folder is self-contained — no cross-skill dependencies. The external pieces are `ui-fix-loop`'s canvas tooling (`server.py` + `canvas-approval.js`), installed from the [ui-fix-loop repo](https://github.com/kimwoct/ui-fix-loop), the `archify` diagram skill (plus its Node CLI) that `ui-logic-loop` delegates its diagrams to, and the Orca runtime (`orca` CLI, version-matched) that `orchestration` depends on; see each skill's README.

## Attribution

The `pstack-*` skills are adapted imports from [cursor/plugins](https://github.com/cursor/plugins) `pstack` 0.15.15 (MIT License, Copyright (c) 2026 Lauren Tan), pinned at commit `d0ef80d86795816da932a153458c5dbe192d294e`; each carries the upstream MIT `LICENSE`. Principle excerpts merged into `conductor-board`, `orchestration`, and `diagnosing-bugs` are attributed inline and in each skill's `references/pstack-LICENSE.txt`.

## License

MIT
