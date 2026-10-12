---
name: skills-kimwoct-patterns
description: "Use when working in skills-kimwoct — adding or refreshing skills, writing README rows or commit messages, validating skill frontmatter, or syncing skills/ and pushing to main — conventions measured from this repo's git history"
metadata:
  version: "1.0.0"
  source: local-git-analysis
  analyzed_commits: "17"
---

# Skills-kimwoct Patterns

Measured from the repository's git history (17 commits, October 2026). This is a curated
agent-skill collection, not a code project: the "source files" are Markdown skills and the
"build gate" is the pre-push validation loop.

## Commit Conventions

Conventional Commits with a skill-scoped scope when work is localized:

- `feat: <summary>` for new or refreshed skills; `feat(<scope>): <summary>` when one skill or
  batch dominates (`feat(pi-ship-pr):`, `feat(pstack):`, `feat(ui-fix/ui-logic/ui-verify):`).
- `docs: <summary>` for README-only changes (for example a row for a skill that landed
  concurrently).
- Body = bullet list, one per change, stating what and why. Multi-part work is split into
  logical commits, not one mega-commit: the ui-trio contract, the pstack imports, merge
  targets, and README rows were separate commits in one session.
- Scope names the skills touched, slash-separated when several, plural-silent for batches
  (`feat: refresh core engineering skills to latest upstream` when nine files change but the
  change is one kind).

## Code Architecture

- One directory per skill: `skills/<name>/SKILL.md` is the entrypoint; the directory name and
  frontmatter `name:` are always identical, lowercase hyphenated slugs.
- Supporting files are added by role, only when a skill needs them:
  - `scripts/` — Python helpers, stdlib only
  - `evals/` — `evals.json` + fixture builder + grader so evaluations are reproducible
    anywhere (`pi-ship-pr`)
  - `references/` — attribution and license files for imported content
    (`references/pstack-LICENSE.txt`)
  - `agents/openai.yaml` — invocation policy for cross-harness use
    (`allow_implicit_invocation: false` on imports)
- `README.md` is the index: an "Included skills" table sorted alphabetically, one row per
  skill directory, with trigger-first descriptions. Coverage is a gate: every `skills/*/`
  directory must have a row.
- `Attribution` section records provenance for imported/vendor skills (upstream repo, pinned
  commit, license).

## Workflows

Two recurring sequences appear in history:

1. **Gather and land a skill** (majority of commits): read the candidate in the live skills
   directory → review the full diff (direction matters: confirm nothing repo-side is lost;
   restore anything a rework dropped, e.g. `diagnosing-bugs`' post-mortem paragraph) → write
   into `skills/<name>/` → validate → commit (`feat:`) → `git fetch origin` before every push
   → rebase on `origin/main` if it moved (concurrent pushes happened twice) → push. Force-push
   is never used; a rejected push is integrated, not overwritten.
2. **Pre-push validation loop** (every landing, run together): frontmatter parses and
   `name:` == directory for every touched `SKILL.md`; relative links resolve against the
   skill's own dir; `git diff --check` (whitespace); secret scan of the staged diff; README
   row coverage check; `python3 -m py_compile` for any Python touched.

## Testing Patterns

No unit-test framework — the collection is Markdown, so validation is structural:

- Structural checks replace unit tests: frontmatter schema (name/description, quoted
  description when it contains special characters), link resolution, whitespace, README
  coverage.
- Python helpers are kept to the standard library and compiled (`py_compile`) as a gate;
  no third-party dependencies are introduced for tooling.
- Skills that carry behavior claims ship self-contained evals (`evals/make_fixture.py`,
  `check_fixture.py`, stub `gh` on `PATH`) so a benchmark is reproducible from the repo
  alone; eval-run artifacts (fixtures with nested git objects, timing/grading JSON) stay
  out of the repo.