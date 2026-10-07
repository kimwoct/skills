---
name: pstack-create-verification-skill
description: Create or narrowly update a project-local verification skill that launches and drives the real UI, CLI, or service, checks instance ownership, and retains evidence after cleanup. Use when a repository lacks reusable app-verification instructions, not for grading untrusted agent candidates.
license: MIT
metadata:
  source: cursor/plugins/pstack/skills/create-verification-skill
  upstream-commit: d0ef80d86795816da932a153458c5dbe192d294e
---

# Create a project verification skill

Generate instructions another agent can execute cold: launch the real app, confirm the instance, exercise a user path, retain proof, and clean up only what the run owns. Reuse an existing app harness; this complements agent-evaluation frameworks rather than replacing their graders or containment gates.

## Discover the repository's actual contract

Read project instructions, documented startup commands, package/build scripts, tests, and routes or command help. Determine:

- **Surface:** the primary UI, CLI/TUI, desktop/mobile app, service API, or library entry point, plus any relevant secondary surface.
- **Launch and readiness:** exact supported command, build prerequisites, environment variable names, ports, disposable data, auth requirements, and an observable readiness signal. Do not copy secret values into the skill.
- **Drive:** existing browser tests, HTTP scripts, PTY helpers, debug interfaces, or library fixtures. Use tools available in this environment; do not assume a particular browser, shell, operating system, or installed control CLI.
- **Observe:** action traces, response bodies, screenshots, logs, exit codes, persisted state, and other side effects needed to prove behavior.
- **Isolate:** per-run ports, data directories, profiles, and process/session identities. If the app cannot isolate instances, document that limit and require explicit permission before driving a shared one.

Ask only for material facts that cannot be observed. Check the current build/start path before teaching it. If it fails, report the exact blocker; do not expand a documentation-generation task into product repairs. A skill that cannot yet be exercised remains a draft. Any verification scaffolding must be clearly identified, run-owned, and removable without touching user data.

## Preserve approval and isolation gates

Generated instructions must carry forward the repository's authorization and verification requirements, including any existing harness refusal. Do not bypass a disabled candidate-execution or containment gate with a different launcher.

For UI-visible fixes or changes, preserve the user's UI fix/verify loops: ask which reference to compare, prepare the review canvas and intended end state, require answers to every numbered approval question, and wait for approval before real code changes. After local checks, only deploy to the confirmed target when that deployment is authorized, then repeat the reference cross-check end to end and retain inline screenshot evidence. Local PASS is not FIXED until the required deployed checks pass. Generating this skill does not itself authorize deployment.

## Generate a scoped entry point

Use the repository's existing project-local skill root; otherwise use `.agents/skills/verify-<app>/`. Choose a valid lowercase-hyphen name. If a matching skill exists, update only the stale contract rather than creating a duplicate or overwriting unrelated guidance. Do not install the generated project skill globally unless requested.

Write `SKILL.md` with valid `name` and `description` frontmatter, real discovered values, and these sections:

- **Launch:** exact build/start invocation, readiness check, and teardown. For a short-lived CLI, build once and execute each drive in its own isolated fixture or PTY rather than inventing a long-running server.
- **Doctor:** a read-only check of readiness, expected build/version, auth, endpoint, and instance ownership. Use it first when behavior is unexpected. A live port alone does not prove it is this run's instance.
- **Drive:** the available harness and real commands/selectors, favoring stable semantic handles over coordinates. Run through the production user path, not internal state setters or test-only shortcuts.
- **Evidence:** capture both the action and resulting state, plus relevant persisted files, rows, or external effects. State where artifacts go and how secrets are redacted. Mocks may isolate an existing external boundary, but do not count them as live boundary verification. Inspect and observe a dry-run's actual effects rather than trusting its name; do not probe unauthorized external writes.
- **Cleanup:** retain process/session IDs and remove only instances and scratch state created by this run. Never kill by process name or remove proof artifacts. Keep evidence outside disposable data directories.
- **Helpers, if needed:** include their invocation and dependencies; run each helper, and make scripts executable where applicable. Do not add a new harness when the existing one suffices.

## Seed a user-facing feature map

Write `features/README.md` as an index with shared preconditions, proof conventions, and links to the relevant feature files. Start with the main requested features or a small representative set, not a speculative full-app inventory.

Use the layout in [the illustrative feature-map index](references/feature-map-example/README.md) when useful. Its Notes app, control CLI, ports, paths, and selectors are fictional examples, not dependencies or commands to copy into this repository.

Each feature file describes the user's behavior and uses these four sections:

1. **Sub-features:** stable IDs for observable behaviors.
2. **How to get to it (user POV):** supported menu, route, keyboard, API, or CLI entry points.
3. **Driving it with the actual harness:** preconditions and action-command-result pairs, including negative states when relevant.
4. **Gotchas:** focus, timing, auth, persistence, or other traps that can invalidate proof.

Record which entry points a run covers. Passing one convenient path does not verify a different mapped path. Maintain the map when startup or user paths change.

## Execute the generated contract

Run launch, doctor, a mapped feature, evidence capture, and cleanup end to end once within the authorized environment. Run cleanup after failed attempts too. After cleanup, confirm the evidence still exists. Validate frontmatter and local references, and check that commands use the repository's actual scripts and the available tools.

Deliver the generated paths, executed command/results, covered feature and entry point, surviving evidence paths, and untested paths or blockers. Do not label a never-executed skill verified or imply that a one-feature smoke test proves every feature. Stop after the requested reusable contract is generated and demonstrated; deployment and broader feature testing remain governed by the user's task.

Adapted from pstack `create-verification-skill` at the commit above. Copyright (c) 2026 Lauren Tan; see [LICENSE](LICENSE).
