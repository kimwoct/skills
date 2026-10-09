---
name: pi-ship-pr
description: Delegate committing, pushing and opening a pull request into the mother (parent) branch to a Pi agent running in its own Herdr session, then recap what shipped. Use whenever the user asks to have Pi (or "the agent in Herdr") commit/push/open a PR, says "ship this", "hand this off to Pi", "PR it into develop/main/eevent/the mother branch", or wants finished local changes turned into a PR instead of being committed straight to the base branch — even if they don't name Herdr or this skill.
---

# Pi ship PR

Finished, verified changes sit in a checkout. Instead of committing them yourself (and risking a
direct push to `main`), hand the git work to a Pi agent in a dedicated Herdr session: it cuts a
branch off the mother branch, commits, pushes, and opens a PR back into the mother branch. You
stay the supervisor: you resolve the plan, pass context, wait, verify, and write the recap.

The point of the delegation is that the mother branch never receives a direct commit. Every
step below protects that.

## 1. Check there is something to ship

Run the repo's own checks first if you changed code in this conversation and haven't run them
since — Pi is told the work is already verified and will not fix failures.

## 2. Resolve the plan

```bash
python3 ~/.agents/skills/pi-ship-pr/scripts/delegate_pr.py --repo <repo> --dry-plan
```

The script decides the mother branch:
- an explicit `--base` the user named always wins;
- on a long-lived branch (`main`, `develop`, `eevent`, …) that branch is the mother, and Pi cuts a
  new branch from it, carrying uncommitted changes and any unpushed local commits;
- on a feature branch (open PR, or a `fix/`, `feat/`, `ui-fix/`… name) Pi stays on it and the PR
  targets the open PR's base, else the ui-fix-canvas `parentBranches` mapping, else the repo default.

Tell the user the mother branch, the reason, and the mode in one line. If it looks wrong (for
example a repo whose mother is `eevent` while you're on `main`), rerun with `--base`.
"nothing to ship" means clean tree and no unpushed commits — report it and stop.

## 3. Write the context file

Pi only sees the diff. Write a short file (in your scratchpad or `/tmp`) giving what changed, why,
and how it was verified (commands and results), plus any files that must not be committed
(gitignored local config, backups). This becomes the commit message and PR body, so it is
worth a few precise lines. Pass a branch name with `--branch` if the user asked for one.

## 4. Delegate

Run in the background — Pi can take several minutes:

```bash
python3 ~/.agents/skills/pi-ship-pr/scripts/delegate_pr.py --repo <repo> \
  --context-file <file> [--base <mother>] [--branch <name>] [--timeout-min 30]
```

It starts session `pi-pr-<id>`, opens a workspace in the repo, starts Pi as agent `shipper`,
submits the prompt, waits for it to settle, then verifies independently: the branch exists on
origin, `gh` sees a PR whose base is the mother branch, and `origin/<mother>` did not move. It
prints one JSON object. The prompt, Pi's terminal output and Pi's `result.json` are kept under
`~/.agents/pi-ship-pr/<id>/`.

Tell the user it's running and which session to attach to (`herdr session attach <id>`) if they
want to watch. Don't poll; you'll be notified when the script exits.

## 5. Handle the outcome

- **exit 0, `ok: true`** — write the recap (below). The Herdr session was stopped.
- **exit 2, Pi blocked** — Pi is waiting on a question or approval. Read
  `agent-output.txt`, show the user the question, and let them decide; don't answer it for them.
  The session stays running.
- **exit 1** — report `error` / `problems` plainly with the evidence (agent output path, which
  check failed). If `baseUntouched` is false, say so first: something pushed to the mother
  branch, and the user needs to know before anything else. Don't retry silently.

## Recap format

Lead with the outcome and the PR link, then the facts from `result` and the verification
fields, not from memory:

```
PR opened: <prUrl>  (<branch> → <base>)

Commit — <subject>
- <path> — <what changed there>
- ...

Verification
- Pi's checks: <checks from result.json, or "none run">
- Branch on origin: yes · PR base confirmed: <base> · origin/<base> untouched: yes
- Left uncommitted: <excluded, with reason> (omit the line if none)

Your checkout is now on <branch>.  (or: still on <branch>)
```

Keep it as short as the change allows; the PR body holds the detail.
