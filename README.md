# skills

Essential agent skills collection: engineering workflow, UI, research, and writing
skills for AI coding agents (Claude Code, Codex, ZCode, …).

Each skill is a self-contained folder (`skills/<name>/SKILL.md` plus any supporting
files) that you drop into your agent's skills directory. Companion loop skills
[`ui-fix-loop`](https://github.com/kimwoct/ui-fix-loop) and
[`ui-verify-loop`](https://github.com/kimwoct/ui-verify-loop) live in their own repos.

## Included skills

| Skill | What it does |
|---|---|
| `code-review` | Reviews changes since a fixed point along two axes — Standards and quality — with agent-ready briefs |
| `codebase-design` | Shared vocabulary for designing deep modules: interface design, deepening opportunities |
| `diagnosing-bugs` | Diagnosis loop for hard bugs and performance regressions |
| `domain-modeling` | Build and sharpen a project's domain model / ubiquitous language |
| `frontend-design` | Create distinctive, production-grade frontend interfaces |
| `handoff` | Compact the current conversation into a handoff document for another agent |
| `implement` | Implement a piece of work from a spec or set of tickets |
| `karpathy-guidelines` | Behavioral guidelines that reduce common LLM coding mistakes |
| `prototype` | Build a throwaway prototype to answer a design question |
| `research` | Investigate a question against high-trust primary sources |
| `resolving-merge-conflicts` | Resolve an in-progress git merge/rebase conflict |
| `tdd` | Test-driven development — red-green-refactor and integration testing |
| `triage` | Move issues and external PRs through a state machine of triage roles |
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

Each skill folder is standalone — no cross-skill dependencies.

## License

MIT
