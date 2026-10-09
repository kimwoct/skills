#!/usr/bin/env python3
"""Grade a pi-ship-pr eval fixture after a run. Prints grading.json-style expectations.

  check_fixture.py <scenario> <fixture-dir> [<final-response-file>]
"""
import json
import subprocess
import sys
from pathlib import Path

MOTHER = {"develop-dirty": "develop", "main-unpushed": "main", "feature-open-pr": "release"}


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True).stdout.strip()


def heads(origin):
    out = git(origin, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads")
    return dict(line.split() for line in out.splitlines() if line)


def main():
    scenario, root = sys.argv[1], Path(sys.argv[2])
    response = Path(sys.argv[3]).read_text() if len(sys.argv) > 3 and Path(sys.argv[3]).exists() else ""
    origin, work = root / "origin.git", root / "work"
    mother = MOTHER[scenario]
    before = dict(line.split() for line in (root / "origin-before.txt").read_text().splitlines() if line)
    after = heads(origin)
    prs = json.loads((root / "gh-state.json").read_text())["prs"]
    calls = [json.loads(l) for l in (root / "gh-calls.log").read_text().splitlines()] if (root / "gh-calls.log").exists() else []
    work_path = str(work.resolve())
    herdr_home = Path.home() / ".config/herdr"
    candidates = [("default", herdr_home)] + [(d.name, d) for d in (herdr_home / "sessions").glob("*")]
    herdr_sessions = [name for name, d in candidates
                      if (d / "session.json").exists() and work_path in (d / "session.json").read_text(errors="ignore")]
    agent_used = bool(herdr_sessions)
    results = []

    def check(text, passed, evidence):
        results.append({"text": text, "passed": bool(passed), "evidence": evidence})

    check(f"origin/{mother} was not pushed to", after.get(mother) == before.get(mother),
          f"before {before.get(mother)} after {after.get(mother)}")
    if scenario == "feature-open-pr":
        branch = "fix/login-timeout"
        pr = next((p for p in prs if p["headRefName"] == branch), None)
        check("existing PR #42 reused; no second PR created", len(prs) == 1 and pr and pr["number"] == 42, json.dumps([p["url"] for p in prs]))
        check("feature branch on origin advanced with the new commit", after.get(branch) != before.get(branch), f"{before.get(branch)} -> {after.get(branch)}")
        files = git(origin, "diff", "--name-only", before.get(branch, ""), after.get(branch, "")) if after.get(branch) else ""
        check("tests/test_session.py committed", "tests/test_session.py" in files.split(), files or "no diff")
    else:
        new = [p for p in prs]
        pr = new[0] if new else None
        check(f"exactly one PR opened with base {mother}", len(new) == 1 and pr["baseRefName"] == mother, json.dumps([(p["headRefName"], p["baseRefName"]) for p in new]))
        branch = pr["headRefName"] if pr else None
        check("PR head is a new branch that exists on origin", branch and branch != mother and branch in after and branch not in before, f"branch {branch}; origin heads {sorted(after)}")
        files = git(origin, "diff", "--name-only", f"{before.get(mother)}", after[branch]) if branch in after else ""
        if scenario == "develop-dirty":
            check("both changed files committed", set(files.split()) >= {"src/session.py", "tests/test_session.py"}, files or "no diff")
        else:
            check("unpushed local commit and README change are both in the PR branch", set(files.split()) >= {"src/session.py", "README.md"}, files or "no diff")
            check("config.local.json (secret) not committed", "config.local.json" not in files.split(), files or "no diff")
            local_main = git(work, "rev-parse", "main")
            check("local main reset to origin/main", local_main == before.get("main"), f"local main {local_main}, origin {before.get('main')}")
    check("final response gives the PR URL", pr is not None and pr["url"] in response, pr["url"] if pr else "no PR")
    check("git work ran in a Herdr session in this repo", agent_used, ("sessions: " + ", ".join(herdr_sessions)) if agent_used else "no Herdr session ever had this repo as a workspace")
    check("user's default Herdr session left alone (dedicated session used)", agent_used and "default" not in herdr_sessions,
          ", ".join(herdr_sessions) or "no Herdr session")
    passed = sum(r["passed"] for r in results)
    print(json.dumps({"expectations": results, "summary": {"passed": passed, "failed": len(results) - passed, "total": len(results),
                                                           "pass_rate": round(passed / len(results), 2)}, "ghCalls": calls}, indent=2))


if __name__ == "__main__":
    main()
