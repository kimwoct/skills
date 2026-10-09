#!/usr/bin/env python3
"""Delegate commit + push + PR-into-the-mother-branch to a Pi agent in its own Herdr session.

Usage:
  delegate_pr.py --repo PATH [--base BRANCH] [--branch NAME] [--context-file FILE]
                 [--agent pi] [--timeout-min 30] [--dry-plan]

Prints one JSON object on stdout (the facts for the recap). Exit 0 = PR opened and
verified, 2 = Pi is blocked on a question/approval (session left running), 1 = failure.
Stdlib only.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERDR = os.environ.get("HERDR_BIN") or str(Path.home() / ".local/bin/herdr")
GH = os.environ.get("PI_SHIP_PR_GH") or "gh"  # evals point this at a stub; named in the prompt so Pi uses it too
STATE_ROOT = Path(os.environ.get("PI_SHIP_PR_STATE", Path.home() / ".agents/pi-ship-pr"))
CANVAS_CONFIG = Path.home() / ".agents/ui-fix-canvas/dispatch-config.json"
PR_TEMPLATE = Path.home() / ".agents/skills/pr/SKILL.md"
# Branch names that are feature work rather than a long-lived "mother" branch.
FEATURE_RE = re.compile(r"^(feat|feature|fix|bugfix|hotfix|chore|docs|refactor|test|perf|ci|ui-fix|wip|claude|pi)[/-]")


def git(repo, *args, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and result.returncode:
        raise RuntimeError("git " + " ".join(args) + ": " + (result.stderr or result.stdout).strip())
    return result.stdout.strip()


def gh(repo, *args):
    result = subprocess.run([GH, *args], cwd=repo, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def remote_sha(repo, branch):
    out = git(repo, "ls-remote", "origin", "refs/heads/" + branch, check=False)
    return out.split()[0] if out else None


def resolve_base(repo, current, explicit):
    """Return (mother_branch, mode, why). mode is 'new-branch' or 'existing-branch'."""
    if explicit:
        mode = "new-branch" if current == explicit else ("existing-branch" if current else "new-branch")
        return explicit, mode, "given explicitly"
    if not current:
        raise RuntimeError("detached HEAD: check out the mother branch or pass --base")
    pr = gh(repo, "pr", "view", current, "--json", "baseRefName")
    if pr:
        return json.loads(pr)["baseRefName"], "existing-branch", "base of the open PR for " + current
    if FEATURE_RE.match(current):
        default = gh(repo, "repo", "view", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name")
        hint = canvas_parent(repo)
        base = hint or default or "main"
        return base, "existing-branch", current + " looks like a feature branch; PR into " + base + (" (canvas parentBranches)" if hint else " (repo default)")
    return current, "new-branch", "currently checked out long-lived branch"


def canvas_parent(repo):
    try:
        config = json.loads(CANVAS_CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    for alias, path in config.get("repositories", {}).items():
        if Path(path).expanduser().resolve() == Path(repo).resolve():
            return config.get("parentBranches", {}).get(alias)
    return None


def herdr(*args, session, timeout=45):
    result = subprocess.run([HERDR, "--session", session, *args], capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError("herdr " + " ".join(args[:2]) + ": " + (result.stderr or result.stdout).strip()[:1500])
    response = json.loads(result.stdout or "{}")
    if response.get("error"):
        raise RuntimeError("herdr " + " ".join(args[:2]) + ": " + json.dumps(response["error"]))
    return response.get("result", response)


def start_session(session, log_path):
    with open(log_path, "ab") as log:
        process = subprocess.Popen([HERDR, "--session", session, "server"], stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=log, start_new_session=True)
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError("Herdr session failed to start; see " + str(log_path))
        try:
            herdr("workspace", "list", session=session, timeout=3)
            return
        except (RuntimeError, subprocess.TimeoutExpired, ValueError):
            time.sleep(0.1)
    process.terminate()
    raise RuntimeError("Herdr session startup timed out")


def build_prompt(repo, base, mode, current, branch, result_path, context):
    template = ("Write the PR body with the template in " + str(PR_TEMPLATE) + ". ") if PR_TEMPLATE.exists() else ""
    if mode == "new-branch":
        branching = (f"You are on the mother branch {base}. Create a new branch "
                     + (f"named {branch}" if branch else "named <type>/<short-kebab-slug> (type from the change: feat, fix, chore, docs, refactor)")
                     + f" from the current HEAD so uncommitted changes and any local commits on {base} come with it. "
                     f"If local {base} had commits that are not on origin/{base}, they now belong to the new branch: "
                     f"after switching, run `git branch -f {base} origin/{base}` so local {base} matches origin again. ")
    else:
        branching = f"Stay on the existing feature branch {current}; do not create another branch. "
    return (
        f"Ship already-finished work as a pull request. Repository: {repo}. Mother branch: {base}. "
        "The work is done and was verified by the requester; do not change, refactor or reformat code. "
        "Steps: (1) Inspect `git status`, `git diff` and `git log -10 --oneline` to understand the change and the repo's commit style. "
        "(2) " + branching +
        "(3) Stage only files that belong to this change. Never stage secrets, .env files, local config that is gitignored or meant to be (for example dispatch-config.json), logs, or build output; list anything you left out. "
        "Commit with a message in the repo's style that says what changed and why. "
        "(4) Push with `git push -u origin <branch>`. Never push to " + base + ", never force-push, never merge. "
        "(5) Open the PR with `" + GH + " pr create --base " + base + " --head <branch>`, a concise title and a body. " + template +
        "If a PR for this branch already exists, push to it and reuse its URL. "
        "(6) Write the file " + str(result_path) + " as JSON with keys: branch, base, commits (list of {sha, subject}), "
        "files (list of committed paths), excluded (paths you deliberately left out, with reason), prUrl, checks (anything you ran and its result), notes. "
        "Use `" + GH + "` for every GitHub command. Then stop. If anything is ambiguous or a command fails, stop and explain instead of guessing. "
        + ("Context from the requester (what changed, why, how it was verified): " + context if context else "")
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base")
    parser.add_argument("--branch")
    parser.add_argument("--context-file")
    parser.add_argument("--agent", default="pi")
    parser.add_argument("--timeout-min", type=float, default=30)
    parser.add_argument("--dry-plan", action="store_true", help="resolve and print the plan; start nothing")
    args = parser.parse_args()

    out = {"ok": False}
    try:
        repo = Path(git(args.repo, "rev-parse", "--show-toplevel"))
        current = git(repo, "branch", "--show-current", check=False)
        base, mode, why = resolve_base(repo, current, args.base)
        git(repo, "fetch", "origin", base, check=False)
        dirty = git(repo, "status", "--porcelain")
        ahead = git(repo, "rev-list", "--count", f"origin/{base}..HEAD", check=False) or "0"
        if not dirty and ahead == "0":
            raise RuntimeError(f"nothing to ship: working tree clean and HEAD has no commits beyond origin/{base}")
        context = Path(args.context_file).read_text(encoding="utf-8").strip() if args.context_file else ""
        run_id = "pi-pr-" + uuid.uuid4().hex[:8]
        state = STATE_ROOT / run_id
        result_path = state / "result.json"
        out.update(runId=run_id, session=run_id, repo=str(repo), base=base, baseReason=why, mode=mode,
                   startBranch=current, dirtyFiles=len(dirty.splitlines()), localCommitsAhead=int(ahead),
                   baseShaBefore=remote_sha(repo, base), stateDir=str(state))
        prompt = build_prompt(repo, base, mode, current, args.branch, result_path, context)
        if args.dry_plan:
            out.update(ok=True, dryPlan=True, prompt=prompt)
            return 0
        state.mkdir(parents=True, exist_ok=True)
        (state / "prompt.txt").write_text(prompt, encoding="utf-8")

        start_session(run_id, state / "herdr-server.log")
        workspace = herdr("workspace", "create", "--cwd", str(repo), "--label", run_id,
                          "--env", "PATH=" + os.environ.get("PATH", ""), "--no-focus", session=run_id)
        pane = workspace["root_pane"]["pane_id"]
        out["pane"] = pane
        herdr("agent", "start", "shipper", "--kind", args.agent, "--pane", pane, "--timeout", "60000", session=run_id, timeout=70)
        time.sleep(2)
        herdr("agent", "prompt", "shipper", prompt, "--wait", "--until", "working", "--until", "done",
              "--timeout", "15000", session=run_id, timeout=20)
        deadline_ms = str(int(args.timeout_min * 60000))
        herdr("agent", "wait", "shipper", "--timeout", deadline_ms, session=run_id, timeout=args.timeout_min * 60 + 30)
        info = herdr("agent", "get", "shipper", session=run_id)
        info = info["agent"] if isinstance(info.get("agent"), dict) else info
        status = info.get("agent_status")
        out["agentStatus"] = status
        tail = subprocess.run([HERDR, "--session", run_id, "agent", "read", "shipper"], capture_output=True, text=True)
        (state / "agent-output.txt").write_text(tail.stdout, encoding="utf-8")
        out["agentOutput"] = str(state / "agent-output.txt")
        if status == "blocked":
            out["error"] = "Pi is waiting on a question or approval; attach with: herdr session attach " + run_id
            return 2

        result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else None
        out["result"] = result
        out["baseShaAfter"] = remote_sha(repo, base)
        out["baseUntouched"] = out["baseShaAfter"] == out["baseShaBefore"]
        if not result:
            out["error"] = "Pi finished without writing " + str(result_path) + "; read " + out["agentOutput"]
            return 1
        branch = result.get("branch")
        out["branchOnOrigin"] = bool(branch and remote_sha(repo, branch))
        pr = gh(repo, "pr", "view", result.get("prUrl") or branch or "", "--json", "url,state,baseRefName,headRefName,title")
        out["pr"] = json.loads(pr) if pr else None
        problems = []
        if not out["baseUntouched"]:
            problems.append(f"origin/{base} moved during the run")
        if not out["branchOnOrigin"]:
            problems.append("branch is not on origin")
        if not out["pr"]:
            problems.append("PR could not be confirmed with gh")
        elif out["pr"].get("baseRefName") != base:
            problems.append("PR base is " + str(out["pr"].get("baseRefName")) + ", expected " + base)
        out["problems"] = problems
        out["ok"] = not problems
        if out["ok"]:
            subprocess.run([HERDR, "--session", run_id, "server", "stop"], capture_output=True)
            out["sessionStopped"] = True
        return 0 if out["ok"] else 1
    except Exception as error:  # report every failure as data for the recap
        out["error"] = str(error)
        return 1
    finally:
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
