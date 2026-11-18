#!/usr/bin/env python3
"""Keep your personal Artemis files (profile/, applications/, memory/, cvs/) in a separate data
folder, optionally a private git repository, so a cloud session or a second computer can continue
where the last one stopped. Stdlib only; needs `git` for pull and push.

  python tools/artemis_data.py where            show which data folder is in use
  python tools/artemis_data.py pull             get the latest data (clones it the first time)
  python tools/artemis_data.py push [-m "msg"]  save and upload the data
  python tools/artemis_data.py status           show what changed since the last push

Settings (environment variables):
  ARTEMIS_DATA_DIR   the data folder. Default: this repo's own folder (nothing to sync).
  ARTEMIS_DATA_REPO  git address of your private data repository, used to clone the first time,
                     for example https://github.com/you/artemis-data.git

The engine never uploads anything unless you run `push`, and `push` only touches the data folder.
"""
import argparse
import os
import subprocess
import sys

from common import DATA_DIR, ROOT, utf8_console

utf8_console()

REPO = os.environ.get("ARTEMIS_DATA_REPO", "")
SEPARATE = os.path.normcase(DATA_DIR) != os.path.normcase(ROOT)


def git(*args, check=True):
    r = subprocess.run(["git", "-C", DATA_DIR, *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        sys.exit(f"git {' '.join(args)} failed:\n{(r.stderr or r.stdout).strip()}")
    return r


def is_repo():
    return os.path.isdir(os.path.join(DATA_DIR, ".git"))


def need_separate():
    if not SEPARATE:
        sys.exit("ARTEMIS_DATA_DIR is not set, so your data is inside the engine folder and there is "
                 "nothing to sync. Set ARTEMIS_DATA_DIR to a separate folder first.")


def cmd_where(_):
    print(f"Data folder: {DATA_DIR}")
    print("Separate from the engine: " + ("yes" if SEPARATE else "no (default location)"))
    print("Git repository: " + ("yes" if is_repo() else "no"))
    for name in ("profile/knowledge.json", "applications/pipeline.md", "memory/MEMORY.md"):
        mark = "found" if os.path.exists(os.path.join(DATA_DIR, *name.split("/"))) else "missing"
        print(f"  {name}: {mark}")


def cmd_pull(_):
    need_separate()
    if not os.path.isdir(DATA_DIR) or not os.listdir(DATA_DIR):
        if not REPO:
            sys.exit("The data folder is empty or missing. Set ARTEMIS_DATA_REPO to your data repository "
                     "address so it can be cloned, or create the folder and run `artemis setup`.")
        os.makedirs(os.path.dirname(DATA_DIR) or ".", exist_ok=True)
        r = subprocess.run(["git", "clone", REPO, DATA_DIR], text=True)
        sys.exit(r.returncode)
    if not is_repo():
        sys.exit(f"{DATA_DIR} exists but is not a git repository, so it can't be pulled.")
    out = git("pull", "--rebase", "--autostash").stdout.strip()
    print(out or "Already up to date.")


def cmd_status(_):
    need_separate()
    if not is_repo():
        sys.exit(f"{DATA_DIR} is not a git repository.")
    print(git("status", "--short", "--branch").stdout.strip())


def cmd_push(a):
    need_separate()
    if not is_repo():
        sys.exit(f"{DATA_DIR} is not a git repository. Run `git init` there and add a remote first.")
    git("add", "-A")
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        print("Nothing new to save.")
    else:
        git("commit", "-m", a.message)
        print("Saved.")
    out = git("push").stdout.strip()
    print(out or "Uploaded.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("where").set_defaults(fn=cmd_where)
    sub.add_parser("pull").set_defaults(fn=cmd_pull)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    s = sub.add_parser("push")
    s.add_argument("-m", "--message", default="Update Artemis data")
    s.set_defaults(fn=cmd_push)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
