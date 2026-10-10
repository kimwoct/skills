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
| `ask-matt` | Ask which skill or flow fits your situation — a router over the skills in this collection |
| `chief-of-staff` | Pursue a long-running goal in a single session by coordinating subagents |
| `claude-handoff` | Hand the current conversation to a fresh background agent that picks up the work immediately |
| `code-review` | Reviews changes since a fixed point along two axes — Standards and Spec — with agent-ready briefs |
| `codebase-design` | Shared vocabulary for designing deep modules: interface design, deepening opportunities |
| `conductor-board` | Drive work through the Conductor kanban board (localhost:8798): routed task cards, state machine, G0–G5 TDD-first work tickets, verify contract with evidence |
| `diagnosing-bugs` | Diagnosis loop for hard bugs and performance regressions |
| `domain-modeling` | Build and sharpen a project's domain model: `GLOSSARY.md` vocabulary and ADRs |
| `frontend-design` | Create distinctive, production-grade frontend interfaces |
| `git-guardrails-claude-code` | Set up Claude Code hooks that block dangerous git commands (push, reset --hard, clean, branch -D, …) before they execute |
| `grill-me` | A relentless interview to sharpen a plan or design |
| `grill-with-docs` | Relentless interview to sharpen a plan or design, writing ADRs and glossary as you go |
| `grilling` | Grill the user relentlessly about a plan, decision, or idea to stress-test their thinking |
| `handoff` | Compact the current conversation into a handoff document for another agent |
| `implement` | Implement a piece of work from a spec or set of tickets |
| `implement-spec` | Implement the result of `/to-spec` and `/to-tickets` in code |
| `improve-codebase-architecture` | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through the one you pick |
| `karpathy-guidelines` | Behavioral guidelines that reduce common LLM coding mistakes |
| `loop-me` | Grill you about specs for workflows you want to build, within the workspace |
| `migrate-to-shoehorn` | Migrate test files from `as` type assertions to @total-typescript/shoehorn |
| `monid` | Discover data tools via the `monid` CLI (web scraping, enrichment, search, monitoring, API access) before building from scratch — runs spend the configured Monid balance |
| `orchestration` | Coordinate supervised Orca workers: threaded messages, blocking ask/reply, task dispatch, worker_done/escalation waits, task DAGs, decision gates (full ownership handoffs use `orca-cli`) |
| `pi-ship-pr` | Delegate commit, push, and PR-into-the-mother-branch to a Pi agent in its own Herdr session; independently verifies branch-on-origin, PR base, and untouched mother branch, then writes the recap (eval-validated on 3 scenarios) |
| `pr` | Use when writing a PR body |
| `prototype` | Build a throwaway prototype to answer a design question |
| `pstack-benchmark-checklist` | Validate a runtime performance measurement — limiter, comparable tuning, error counting, completed work, physical limits, repetitions, end-to-end relevance — before reporting a speedup or technology choice |
| `pstack-blast-radius` | Review what a change could break beyond its diff and prove the load-bearing safety fact (evidence levels: hypothesis → source-backed → executed proof → app reproduction) |
| `pstack-correct` | Prevent recurring agent mistakes with proportionate guards (structure/types/lint/regression checks) proven to reject a real past failure |
| `pstack-create-verification-skill` | Generate a project-local verification skill that launches and drives the real UI/CLI/service, checks instance ownership, retains evidence, and cleans up |
| `research` | Investigate a question against high-trust primary sources |
| `resolving-merge-conflicts` | Resolve an in-progress git merge/rebase conflict |
| `retro` | Conduct a retrospective on a coding session |
| `scaffold-exercises` | Create exercise directory structures with sections, problems, solutions, and explainers |
| `setup-matt-pocock-skills` | Configure a repo for the engineering skills: issue tracker, triage labels, and domain-doc layout; run once before first use |
| `setup-pre-commit` | Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests |
| `setup-ts-deep-modules` | Wire dependency-cruiser into a TypeScript repo so each package is a deep module behind a small entry-point API |
| `tdd` | Test-driven development — red-green-refactor and integration testing |
| `teach` | Teach the user a new skill or concept within this workspace |
| `to-questionnaire` | Turn a decision you can't fully answer into a questionnaire for someone else to fill in |
| `to-spec` | Turn the current conversation into a spec and publish it to the project's issue tracker |
| `to-tickets` | Break a plan, spec, or conversation into tracer-bullet tickets with blocking edges, published to the tracker |
| `triage` | Move issues and external PRs through a state machine of triage roles |
| `typesafe-ai` | Build AI-powered software with TypeSafe: System One models (Jev) turn natural language and app state into typed judgments and probabilities; read the live docs |
| `ui-fix-loop` | Loop-engineering workflow for UI bug fixes: REVIEW → PREVIEW (approval gate) → IMPLEMENT → VERIFY on one HTML canvas |
| `ui-logic-loop` | Loop-engineering workflow for logic-visible changes (data flow, API orchestration, caching, jobs): an archify sequence-diagram pair — CURRENT → PREVIEW (approval gate) → IMPLEMENT → VERIFY on the deployed flow |
| `ui-verify-loop` | Closing gate after a UI fix: proves the change matches a named REFERENCE and is deployed + e2e-verified; also runs Whiteboard-hosted verification rounds (whiteboard-agent-review Mode B) |
| `vercel-react-best-practices` | React and Next.js performance optimization guidelines from Vercel Engineering |
| `wait-what` | Stop — that last message did not land; re-pitch it |
| `wayfinder` | Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on the tracker and resolve them one at a time |
| `whiteboard-agent-review` | Review one implementation agent's work with agent/run metadata and an explicit diff (Mode A), or author an architecture-sketch Whiteboard of the repo's data flows and code paths (Mode B) |
| `wizard` | Generate an interactive bash wizard that walks a human through steps only they can perform |
| `writing-beats` | Writing: assemble raw material into a journey of beats, grounding terms before beats lean on them |
| `writing-for-agents` | Write documents for agents: skills, AGENTS.md, CLAUDE.md |
| `writing-fragments` | Writing: mine raw fragments, no structure yet |
| `writing-great-skills` | Reference for writing and editing skills well |
| `writing-shape` | Writing: shape raw material into an article, paragraph by paragraph |

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

Each skill folder is self-contained — no cross-skill dependencies. The external pieces are `ui-fix-loop`'s canvas tooling (`server.py` + `canvas-approval.js`), installed from the [ui-fix-loop repo](https://github.com/kimwoct/ui-fix-loop), the `archify` diagram skill (plus its Node CLI) that `ui-logic-loop` delegates its diagrams to, and the Orca runtime (`orca` CLI, version-matched) that `orchestration` depends on, and the Herdr terminal app + Pi coding agent + GitHub `gh` CLI that `pi-ship-pr` delegates and verifies through; see each skill's README.

## Attribution

The `pstack-*` skills are adapted imports from [cursor/plugins](https://github.com/cursor/plugins) `pstack` 0.15.15 (MIT License, Copyright (c) 2026 Lauren Tan), pinned at commit `d0ef80d86795816da932a153458c5dbe192d294e`; each carries the upstream MIT `LICENSE`. Principle excerpts merged into `conductor-board`, `orchestration`, and `diagnosing-bugs` are attributed inline and in each skill's `references/pstack-LICENSE.txt`.

The engineering skills (`ask-matt`, `chief-of-staff`, `claude-handoff`, `code-review`, `codebase-design`, `domain-modeling`, `grill-*`, `grilling`, `implement`, `implement-spec`, `improve-codebase-architecture`, `loop-me`, `pr`, `prototype`, `research`, `retro`, `scaffold-exercises`, `setup-*`, `teach`, `to-*`, `triage`, `tdd`, `wayfinder`, `writing-*`, …) come from the Matt Pocock skills collection, installed and refreshed via the `setup-matt-pocock-skills` skill; several carry their own in-file credits (for example `pr`, credited to Humanlayer's `show-me` by Dex Horthy). `monid` is a vendor skill that self-updates from [monid.ai](https://monid.ai/SKILL.md); it has no local license file and its API runs are billable.

## License

MIT
