---
name: whiteboard-agent-review
description: Two Whiteboard modes. (A) Review one named implementation agent's work (pi, codex, claude-code, cursor, ...) for one concrete task, using the agent/run metadata and an explicit diff rather than inferred provenance. (B) Author an architecture-sketch whiteboard of a repository — main data flows, access patterns, and code paths for a full architecture review — triggered by prompts like "Create a Whiteboard that sketches out the main data flows, access patterns, and code paths in this repo, so I can do a full architecture review of it. Open it in Whiteboard when you're done."
---

# Whiteboard Agent Review

Use this skill when a task needs an auditable Whiteboard review of a specific implementation agent, such as `pi`, `codex`, `claude-code`, `cursor`, or another supported target, or when the user wants an architecture-sketch whiteboard of the repo. The Mode A review is about the implementation attempt, not merely the repository's current state.

Two modes:

- **Mode A — agent-run review** (default): the full workflow below, auditing what one named implementation agent did for one task.
- **Mode B — architecture-sketch whiteboard**: a repo-wide sketch of data flows, access patterns, and code paths for an architecture review; see the Mode B section below. It is authoring, not an agent-run audit.

## Mode A — agent-run review

### Required inputs

Collect these values before authoring. Stop and request the missing value when it changes what is being reviewed:

- `repository_path`: absolute local Git or jj checkout path.
- `agent`: explicit agent identity. Use the exact implementation target (`pi`, `codex`, `claude`, `claude-code`, `cursor`, `opencode`, `omp`, `copilot`, or `all` when the run genuinely involved all agents).
- `task_id` and `task_summary`: stable task identifier plus the intended change.
- `base_revision`: branch, commit, or other revision used as the comparison base.
- `head_revision` or a worktree: the implementation output to inspect.
- `run_id` and `pane_id` when the dispatcher or Herdr supplies them; otherwise record them as unavailable, never invent them.
- `evidence_dir`: local directory for the review record and screenshots/log references.

Keep the review local or UAT-only when that is the surrounding workflow's constraint. Do not publish, share, or deploy a review unless the user explicitly asks for that action.

### Workflow

#### 1. Establish provenance

Write down the inputs in the evidence record before inspecting the diff. Confirm:

1. The repository path exists and is a Git/jj checkout.
2. The selected agent is explicit and matches the implementation run metadata.
3. The task scope is concrete enough to decide whether a changed file is in scope.
4. The base and head are stable enough to reproduce the comparison.

Use `git status --short`, `git rev-parse --show-toplevel`, and revision commands appropriate to the checkout. Treat untracked files as part of a worktree review only when they belong to this task; record unrelated files separately.

#### 2. Start an isolated Whiteboard authoring server

For headless or automated review, use a task-specific state directory so concurrent reviews cannot mix state:

```bash
whiteboard --version
whiteboard server start --state-dir "$WHITEBOARD_STATE_DIR" --port 0 --json
whiteboard server status --json
```

Use the installed CLI's `--help` and `whiteboard api tools --json` as the runtime source of truth if a command or schema differs. Register the checkout, then create a background review:

```bash
whiteboard --state-dir "$WHITEBOARD_STATE_DIR" api session_register_repository \
  '{"path":"/absolute/path/to/repository"}' --json

whiteboard --state-dir "$WHITEBOARD_STATE_DIR" api session_create \
  '{"title":"<task_id> — <agent> implementation review","target":{"kind":"worktree","repositoryId":"<repository_id>","base":"<base_revision>"},"open":false}' --json
```

Use a `commits` target with explicit `head` and `base` when reviewing an immutable commit range. Save the returned `repositoryId` and `sessionId` immediately.

#### 3. Read before writing

Acquire a document activity lease, then inspect the review and diff. At minimum, call `session_get`, `session_diff` in `files` format, and `session_diff` in `patch` format for the relevant paths. Read exact source ranges with `session_source` when a finding needs context. Do not author a conclusion from a status line, queued process, or agent claim alone.

The review must answer:

- What was the agent asked to implement?
- Which files changed, and why is each in or out of scope?
- Does the implementation satisfy the task's acceptance criteria?
- What tests, browser checks, screenshots, or artifact checks actually ran?
- Which findings remain, ordered by severity?
- Is the agent identity and run provenance sufficient to reproduce the review?

#### 4. Author the review canvas

Use `session_edit` with the lease to add a concise Markdown review. Include these sections in this order:

1. **Task and provenance** — task ID, summary, agent, run ID, pane ID, repository, base, head/worktree, environment, and review timestamp.
2. **Scope** — included files and explicit exclusions.
3. **Implementation evidence** — diff observations, relevant source links, and the agent's completion evidence.
4. **Verification** — exact commands/scenarios, pass/fail result, and evidence paths.
5. **Findings** — severity (`blocker`, `high`, `medium`, `low`, or `note`), file/line, impact, and required action. Write `No findings after inspecting ...` only after the diff and relevant source have been read.
6. **Decision** — `approved`, `changes requested`, or `unable to review`, with the reason.

Prefer Whiteboard source links and code peeks over copied source. Keep the review factual: distinguish observed behavior, agent-reported claims, and reviewer inference.

#### 5. Persist machine-readable evidence

Write one JSON record under `evidence_dir`, for example `whiteboard-agent-review.json`:

```json
{
  "schemaVersion": 1,
  "reviewedAt": "2026-10-05T00:00:00Z",
  "task": {"id": "...", "summary": "..."},
  "agent": {"name": "pi", "runId": "...", "paneId": "..."},
  "repository": {
    "path": "/absolute/path",
    "repositoryId": "...",
    "base": "...",
    "head": "...",
    "worktree": true
  },
  "whiteboard": {
    "stateDir": "/absolute/state-dir",
    "sessionId": "..."
  },
  "environment": "local",
  "verification": [{"command": "...", "result": "passed", "evidence": "..."}],
  "findings": [],
  "decision": "approved"
}
```

Use the actual timestamp and values. If a field is unavailable, use `null` and explain why in the canvas; never use a guessed identifier. Store screenshots and logs beneath the evidence directory and reference them from the JSON record.

#### 6. Close and report

End the activity lease only after the review content and evidence record are saved. Report:

- task and agent reviewed;
- Whiteboard `sessionId`, state directory, and evidence path;
- findings by severity and decision;
- tests and scenarios run;
- unresolved limitations, including missing run metadata or unavailable artifacts.

## Mode B — architecture-sketch whiteboard

Trigger prompts read like:

> "Create a Whiteboard that sketches out the main data flows, access patterns, and code paths in this repo, so I can do a full architecture review of it. Open it in Whiteboard when you're done."

This mode authors a sketch of the repository itself. It is **not** an agent-run review: no `agent`, `task_id`, or run metadata is required, and Mode A's agent-identity and task-scope gates do not apply.

### Required inputs

- `repository_path`: absolute local Git/jj checkout path. Stop and ask only for this.
- Optional: a commit range to pin; otherwise pin the checkout as a `worktree` target with no `base` (reviews the checkout against the default branch).

### Workflow

1. **Provenance-light.** Confirm the checkout and record the pins (`git rev-parse --show-toplevel`, branch, clean/dirty state) and the timestamp. A dirty worktree may include uncommitted work by design — note what is included.
2. **Register and create.** `session_register_repository {path}`, then `session_create {title: "Architecture sketch — <repo>", target: {kind: "worktree", repositoryId, base?}, open: false}`. Call `session_get_instructions` for the authoring flow, and `session_get_instructions({topic: "file-lenses"})` when authoring lenses; follow their ordering rules (register → create → lease → read diff → write immediately).
3. **Read the repo before writing.** Trace real entry points (app routes/actions, background jobs, API controllers) with `session_tree`, `session_file`, and `session_source`, plus the repo's own navigation aids (AGENTS.md, graphify-out/wiki, ARCHITECTURE docs) before any claim reaches the canvas. Every `review-source:` link must cite a verified line number.
4. **Author the sketch, one section per edit** under a `session_activity_begin` document lease (each accepted write or update extends the 3-minute window):
   - *what/why* — one paragraph: system boundaries, transport, principal actors;
   - *main data flows* — `sequence` lenses (client → server API/actions → controllers → stores), one per principal flow;
   - *access patterns* — `database_lens` (stores, collections, key fields, read/write use cases);
   - *code paths* — `call_stack_diff` (or `flow_diagram` for branchy flows) rooted at user/agent entry points;
   - *review hooks* — hot spots, god nodes, risky seams, and an open-questions list where the architecture reviewer should start. Mode A's Findings/Decision sections do **not** apply here; do not paste audit verdicts onto a sketch.
   - Link code as `[label](review-source:head/path#L10-L24)` with repository-relative paths and verified numbers; prefer `code_peek` for the few mechanism-carrying ranges.
5. **Read back and open.** `session_get` the whole canvas, fix contradictions and unverified claims, `session_activity_end` the lease, then `session_open {sessionId}` — the trigger contract is that the board is open at the end.
6. **Report.** Give the `sessionId`, what each lens should be used for during the review, and which repo areas were left unsketched.
7. **Evidence (optional).** The Mode A JSON evidence record is not required here. Write one only on request, with `agent: null` and the same no-guessing rule.

### Mode B gates

- Sketch what **is**: every architecture claim carries code evidence (verified line ranges). No code link, no claim.
- Do not convert the sketch into a findings report or a merge/deploy verdict; the review hooks section is the handoff to the human reviewer.
- Editing an existing sketch: repin it, read the existing document and the diff since it was authored (per the authoring instructions' "updating existing whiteboard" flow) before updating.

## Hard gates

- Mode A: agent identity is explicit. Never infer it from the current shell, process name, or a generic “implementation agent” label. (Mode B binds the repository pins instead.)
- A queued, dispatched, or approved status is not implementation evidence. Read the actual diff and verify the artifact.
- Review only the named task's changes. Flag unrelated changes instead of silently including them.
- A clean diff is not proof of correctness; check the task acceptance criteria and relevant runtime behavior.
- Keep authorization and review separate: Whiteboard review does not approve dispatch, deployment, merge, or external sharing.
- If the repository, task, agent, or comparison cannot be bound unambiguously, mark the review `unable to review` and state the missing binding.

## Useful CLI discovery

When the installed Whiteboard version changes, discover exact schemas instead of relying on memory:

```bash
whiteboard --help
whiteboard api tools --json
whiteboard connect --help
```

Relevant API tools normally include `session_register_repository`, `session_create`, `session_get`, `session_diff`, `session_source`, `session_edit`, `session_environment`, `session_activity_begin`, `session_activity_update`, and `session_activity_end`.

Over MCP the same tools surface as `mcp__whiteboard__<tool>` (e.g. from pi's codemode: `describeTool("mcp__whiteboard__session_edit")` prints the full schema — the runtime source of truth when the CLI is not installed).

### Schema notes learned on a live v0.2 run

- `session_edit`'s `edit` is a typed union, and component fields never sit directly on `edit`: insert is `{type:"insert", content:<component>, parentId?, afterId?}`; in-place forms are `{type:"replace", targetId, content}`, `{type:"update", targetId, changes}`, `{type:"move", targetId, parentId?, afterId?}`, `{type:"remove", targetId}`.
- `session_activity_begin` takes `focus: {description, targetId?}`; `session_activity_update`'s optional fields differ (a `description` key is rejected) — check its schema before use. Either an accepted write or an update extends the lease's 3-minute window; end it with `session_activity_end` so readers see the document as ready.
- Markdown links must use `[label](review-source:head|base/path#L10-L24)` with repository-relative paths; paths containing brackets (Next.js `app/[locale]/…`) work in `source.file` fields of `code_peek`/`call_stack_diff`/`sequence`, but percent-encode them in markdown link URLs.
- Direct tool results over ~20 KB are middle-truncated for the model (full text saved to a temp file); codemode scripts receive the complete result and can trim before returning output.
