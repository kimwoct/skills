#!/usr/bin/env python3
"""Build a disposable repo for a pi-ship-pr eval: bare local origin + working clone + stub gh.

  make_fixture.py <scenario> <dir>     scenarios: develop-dirty, main-unpushed, feature-open-pr

Put <dir>/bin first on PATH so `gh` is the stub. PRs are recorded in <dir>/gh-state.json.
"""
import json
import subprocess
import sys
from pathlib import Path

GH_STUB = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
state_path = Path(__file__).resolve().parent.parent / "gh-state.json"
state = json.loads(state_path.read_text())
args = sys.argv[1:]
with open(state_path.parent / "gh-calls.log", "a") as log:
    log.write(json.dumps(args) + "\n")
def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default
def emit(obj):
    q = opt("-q") or opt("--jq")
    if q == ".defaultBranchRef.name":
        print(obj["defaultBranchRef"]["name"]); return
    fields = opt("--json")
    if fields:
        obj = {k: obj.get(k) for k in fields.split(",")}
    print(json.dumps(obj))
def find(ref):
    for pr in state["prs"]:
        if ref in (pr["url"], pr["headRefName"], str(pr["number"])):
            return pr
    return None
if args[:2] == ["repo", "view"]:
    emit({"defaultBranchRef": {"name": state["default"]}, "nameWithOwner": "acme/demo"}); sys.exit(0)
if args[:2] == ["auth", "status"]:
    print("Logged in to github.com as stub"); sys.exit(0)
if args[:2] == ["pr", "create"]:
    head = opt("--head") or os.popen("git branch --show-current").read().strip()
    if find(head):
        print("a pull request for branch \"%s\" already exists: %s" % (head, find(head)["url"]), file=sys.stderr); sys.exit(1)
    number = 100 + len(state["prs"]) + 1
    pr = {"number": number, "url": "https://github.com/acme/demo/pull/%d" % number, "state": "OPEN",
          "baseRefName": opt("--base") or state["default"], "headRefName": head,
          "title": opt("--title") or opt("-t") or "", "body": opt("--body") or opt("-b") or ""}
    state["prs"].append(pr); state_path.write_text(json.dumps(state, indent=2))
    print(pr["url"]); sys.exit(0)
if args[:2] in (["pr", "view"], ["pr", "edit"]):
    ref = args[2] if len(args) > 2 and not args[2].startswith("-") else os.popen("git branch --show-current").read().strip()
    pr = find(ref)
    if not pr:
        print("no pull requests found for branch \"%s\"" % ref, file=sys.stderr); sys.exit(1)
    if args[1] == "edit":
        print(pr["url"]); sys.exit(0)
    emit(pr); sys.exit(0)
if args[:2] == ["pr", "list"]:
    head = opt("--head")
    prs = [p for p in state["prs"] if not head or p["headRefName"] == head]
    fields = opt("--json")
    print(json.dumps([{k: p.get(k) for k in fields.split(",")} for p in prs] if fields else prs)); sys.exit(0)
print("gh stub: unsupported " + " ".join(args), file=sys.stderr); sys.exit(1)
'''


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    scenario, root = sys.argv[1], Path(sys.argv[2]).resolve()
    root.mkdir(parents=True, exist_ok=True)
    origin, work = root / "origin.git", root / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], check=True, capture_output=True)
    for key, value in [("user.email", "dev@example.com"), ("user.name", "Dev"), ("commit.gpgsign", "false")]:
        git(work, "config", key, value)
    git(work, "checkout", "-q", "-b", "main")
    write(work / "README.md", "# demo\n")
    write(work / "src/session.py", "TIMEOUT = 30\n\n\ndef expired(age):\n    return age > TIMEOUT\n")
    write(work / ".gitignore", "*.log\n")
    git(work, "add", ".")
    git(work, "commit", "-q", "-m", "chore: seed demo app")
    git(work, "push", "-q", "-u", "origin", "main")
    prs = []
    if scenario == "develop-dirty":
        git(work, "checkout", "-q", "-b", "develop")
        git(work, "push", "-q", "-u", "origin", "develop")
        write(work / "src/session.py", "TIMEOUT = 30\n\n\ndef expired(age):\n    return age >= TIMEOUT  # boundary counts as expired\n")
        write(work / "tests/test_session.py", "from src.session import expired\n\n\ndef test_boundary():\n    assert expired(30)\n")
    elif scenario == "main-unpushed":
        write(work / "src/session.py", "TIMEOUT = 45\n\n\ndef expired(age):\n    return age > TIMEOUT\n")
        git(work, "commit", "-q", "-am", "feat: raise session timeout to 45s")
        write(work / "README.md", "# demo\n\nSessions expire after 45 seconds.\n")
        write(work / "config.local.json", '{"apiKey": "sk-local-do-not-commit"}\n')
    elif scenario == "feature-open-pr":
        git(work, "checkout", "-q", "-b", "release")
        git(work, "push", "-q", "-u", "origin", "release")
        git(work, "checkout", "-q", "-b", "fix/login-timeout")
        write(work / "src/session.py", "TIMEOUT = 30\n\n\ndef expired(age):\n    return age is not None and age > TIMEOUT\n")
        git(work, "commit", "-q", "-am", "fix: treat missing session age as not expired")
        git(work, "push", "-q", "-u", "origin", "fix/login-timeout")
        prs.append({"number": 42, "url": "https://github.com/acme/demo/pull/42", "state": "OPEN", "baseRefName": "release",
                    "headRefName": "fix/login-timeout", "title": "fix: login timeout", "body": ""})
        write(work / "tests/test_session.py", "from src.session import expired\n\n\ndef test_missing_age():\n    assert not expired(None)\n")
    else:
        sys.exit("unknown scenario " + scenario)
    write(root / "gh-state.json", json.dumps({"default": "main", "prs": prs}, indent=2))
    stub = root / "bin/gh"
    write(stub, GH_STUB)
    stub.chmod(0o755)
    heads = subprocess.run(["git", "-C", str(origin), "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads"],
                           check=True, capture_output=True, text=True).stdout
    write(root / "origin-before.txt", heads)
    print(json.dumps({"work": str(work), "origin": str(origin), "bin": str(root / "bin")}))


if __name__ == "__main__":
    main()
