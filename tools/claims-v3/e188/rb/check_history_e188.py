#!/usr/bin/env python3
# E188 (Q165, the kit): the history check. E186's (tools/claims-v3/e186/rb/check_history_e186.py with its v2's wider perimeter, run on 9 Nov
# 2026; itself E185's day-2 check in E186's form) carried to E188: no committed change to a file E188 reads may pass step 2 or step 11
# together with its list line, and nothing may be uncommitted there. Its m1 mode is not carried: E188's october-forecast-model reader has
# its own gate (rb/check_arms_e188.py), run after the data commit.
#
#   /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_history_e188.py tree [--anchor REV]
#   /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_history_e188.py paths [--anchor REV]
#
# Run from the lab's top (the runbook's rb_local runs it there). The anchor is E188's registration (878b6f63, RB_E188_BASE; a desk test
# passes its scratch repository's root).
# tree: every one of these, with the problems named, then HISTORY OK or HISTORY REFUSED:
#   1. HEAD descends from the anchor;
#   2. no commit since the anchor changed anything but an addition on E188's paths (git log -m --full-history --diff-filter=a, and the
#      tree diff from the anchor with the same filter; the filter a is everything but an addition: modified, deleted, renamed, type
#      changed): E188's paths are E188's, E186's, M12's, E182's, the k6/v3.1 runbook's and the workload's directories, plus every file
#      outside them that a list E188 reads or harness-e188.json names (E186's data and its note 1, the scale route's six lists, M10's);
#   3. no file added since the anchor in those directories is a Python module or package that shadows one the system python finds outside
#      the lab clone (the user site among them), or shares its module name with another of those modules, or is a byte-code or .pth file;
#   4. no uncommitted change on E188's paths (git status, untracked files too).
# paths: prints E188's paths, one a line.
# Exit codes (the runbooks'): 0 HISTORY OK; 10 usage; 16 HISTORY REFUSED. Python's own modules only; it reads git and files, writes nothing.
# SPDX-License-Identifier: Apache-2.0
import argparse
import hashlib
import importlib.machinery
import json
import os
import subprocess
import sys

ANCHOR = "878b6f6302f4b40d57c9577e3cb46b00cd741592"   # E188: registration (git 12:53:42 PST Thu 12 Nov 2026)
CORE_DIRS = ["tools/claims-v3/e188", "tools/claims-v3/e186", "tools/claims-v3/m12", "tools/claims-v3/e182", "tools/claims-v3/q141k-runbook",
             "workloads/sparsity"]
# every list E186's step 2 reads (base "top": entries from the lab's top; "beside": from the list's own directory)
LISTS = [
    ("tools/claims-v3/e188/SHA256SUMS-e188-registration", "top"),
    ("tools/claims-v3/e188/SHA256SUMS-e188-kit", "top"),
    ("tools/claims-v3/m12/SHA256SUMS-m12", "beside"),
    ("tools/claims-v3/m12/SHA256SUMS-m12-e186", "beside"),
    ("tools/claims-v3/m12/SHA256SUMS-m12-rules", "beside"),
    ("tools/claims-v3/m12/SHA256SUMS-m12-note2", "beside"),
    ("tools/claims-v3/e182/SHA256SUMS-e182-registration", "top"),
    ("tools/claims-v3/e182/SHA256SUMS-e182-kit", "top"),
    ("tools/claims-v3/e182/SHA256SUMS-e182-note1", "top"),
    ("tools/claims-v3/e182/SHA256SUMS-e182-note2", "top"),
    ("tools/claims-v3/e182/SHA256SUMS-e182-note3", "top"),
    ("tools/claims-v3/e182/SHA256SUMS-e182-note4", "top"),
    ("tools/claims-v3/e186/SHA256SUMS-e186-registration", "top"),
    ("docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/SHA256SUMS", "beside"),
    ("docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/SHA256SUMS-note1", "beside"),
    ("tools/claims-v3/m10/POOL8-SHA256SUMS", "top"),
    ("docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS", "top"),
    ("docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS-a2", "top"),
    ("docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS", "beside"),
    ("docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS-a2", "beside"),
    ("docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS", "top"),
]
HARNESS = "tools/claims-v3/e188/harness-e188.json"
M1_ALL = []                                  # E188: no note M1 (its arms' gate is rb/check_arms_e188.py)


def git(*args, timeout=120):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C", GIT_PAGER="cat")
    try:
        p = subprocess.run(["git"] + list(args), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout, env=env)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"(killed at its {timeout} s bound)"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_list(rel, base):
    """[(hash, entry path from the lab's top)] for every non-empty line; None if the list cannot be read."""
    try:
        text = open(rel, "rb").read().decode("utf-8", "replace")
    except OSError:
        return None
    out, d = [], os.path.dirname(rel)
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            out.append(("", "<unreadable line>"))
            continue
        h, p = parts[0], parts[1].strip()
        if p.startswith("*"):
            p = p[1:]
        out.append((h, os.path.normpath(os.path.join(d, p)) if base == "beside" else os.path.normpath(p)))
    return out


def e188_paths():
    """(paths, dirs, unreadable lists): the core directories, plus every file a list or the harness names outside them."""
    named, bad = set(), []
    for rel, base in LISTS:
        ent = read_list(rel, base)
        if ent is None:
            bad.append(rel)
            continue
        named.add(rel)
        named |= {p for _, p in ent if p != "<unreadable line>"}
    try:
        hj = json.load(open(HARNESS))
        for k, v in hj.items():
            if isinstance(v, dict):
                named |= {p for p in v if isinstance(p, str) and "/" in p and not p.startswith("build/")}
    except (OSError, ValueError):
        bad.append(HARNESS)
    outside = sorted(p for p in named if not any(p == d or p.startswith(d + "/") for d in CORE_DIRS))
    dirs = sorted(set(CORE_DIRS) | {os.path.dirname(p) for p in outside})
    return list(CORE_DIRS) + outside, dirs, bad


def parse_name_status(text):
    out, cur = [], ""
    for line in text.splitlines():
        if line.startswith("@@"):
            cur = line[2:].strip()
            continue
        if line.strip():
            parts = line.split("\t")
            out.append((cur, parts[0], parts[1:]))
    return out


def history(anchor, paths):
    """Non-additions since the anchor on the paths: (gating changes, M1 changes), each as 'X path (commit)'."""
    gate, m1 = [], []
    rc, so, se = git("log", "-m", "--full-history", "--diff-filter=a", "--name-status", "--format=@@%H", f"{anchor}..HEAD", "--", *paths)
    if rc != 0:
        return [f"git log failed (rc {rc}): {se.strip()[:200]}"], m1
    rc2, so2, se2 = git("diff", "--diff-filter=a", "--name-status", anchor, "HEAD", "--", *paths)
    if rc2 != 0:
        return [f"git diff failed (rc {rc2}): {se2.strip()[:200]}"], m1
    seen = set()
    for commit, st, ps in parse_name_status(so) + [("tree diff", s, p) for _, s, p in parse_name_status(so2)]:
        key = (st[:1], tuple(ps))
        if key in seen:
            continue
        seen.add(key)
        item = f"{st[:1]} {' -> '.join(ps)} ({commit[:8] if commit != 'tree diff' else 'the tree diff from ' + anchor[:8]})"
        (m1 if all(p in M1_ALL for p in ps) else gate).append(item)
    return gate, m1


def shadows(anchor, dirs):
    """Files added since the anchor in the directories (the core ones in full; any other only its own files and packages): (count, problems)."""
    specs = []
    for d in dirs:
        if d in CORE_DIRS:
            specs.append(d)
        else:
            specs += [f":(glob){d}/*", f":(glob){d}/*/__init__.py", f":(glob){d}/__pycache__/*"]
    rc, so, se = git("diff", "--diff-filter=A", "--name-only", anchor, "HEAD", "--", *specs)
    if rc != 0:
        return 0, [f"git diff (additions) failed (rc {rc}): {se.strip()[:200]}"]
    added = [l for l in so.splitlines() if l.strip()]
    real = os.path.realpath(os.getcwd())
    search = [p for p in sys.path if p and not (os.path.realpath(p) + os.sep).startswith(real + os.sep)]
    try:
        import site
        us = site.getusersitepackages()
        if us and os.path.isdir(us) and us not in search and not (os.path.realpath(us) + os.sep).startswith(real + os.sep):
            search.append(us)
    except Exception:
        pass

    def modname(p):
        b = os.path.basename(p)
        if b == "__init__.py":
            return os.path.basename(os.path.dirname(p))
        if b.endswith(".py"):
            return b[:-3]
        if b.endswith((".so", ".dylib")):
            return b.split(".")[0]
        return None
    rc, so, _ = git("ls-files", "--", *specs)
    names = {}
    for p in so.splitlines():
        n = modname(p)
        if n:
            names.setdefault(n, []).append(p)
    probs = []
    for p in added:
        b = os.path.basename(p)
        if "/__pycache__/" in "/" + p or b.endswith((".pyc", ".pyo", ".pth")):
            probs.append(f"{p} (a byte-code or .pth file)")
            continue
        name = modname(p)
        if not name:
            continue
        if name in sys.builtin_module_names or importlib.machinery.PathFinder.find_spec(name, search) is not None:
            probs.append(f"{p} (shadows the module '{name}' the system python finds)")
        else:
            others = [q for q in names.get(name, []) if q != p]
            if others:
                probs.append(f"{p} (its module name '{name}' is also {others[0]}'s)")
    return len(added), probs


def status(paths):
    rc, so, se = git("status", "--porcelain=v1", "--untracked-files=all", "--", *paths)
    if rc != 0:
        return [f"git status failed (rc {rc}): {se.strip()[:200]}"]
    return [l for l in so.splitlines() if l.strip()]


def resolve(anchor):
    rc, so, _ = git("rev-parse", "--verify", "-q", anchor + "^{commit}")
    return so.strip() if rc == 0 else None


def tree(anchor):
    problems = []
    if git("merge-base", "--is-ancestor", anchor, "HEAD")[0] != 0:
        problems.append(f"ancestry (HEAD does not descend from {anchor[:8]})")
    paths, dirs, bad = e188_paths()
    if bad:
        problems.append("unreadable: " + ", ".join(bad))
    hg, hm = history(anchor, paths)
    if hg:
        problems.append(f"history: {len(hg)} change(s) other than an addition since {anchor[:8]} on E188's paths: " +
                        "; ".join(hg[:6]) + (" ..." if len(hg) > 6 else ""))
    nadd, sp = shadows(anchor, dirs)
    if sp:
        problems.append("additions: " + "; ".join(sp[:6]) + (" ..." if len(sp) > 6 else ""))
    st = status(paths)
    if st:
        problems.append(f"status: {len(st)} uncommitted change(s) on E188's paths: " + "; ".join(s.strip() for s in st[:6]))
    summary = (f"E188's paths: {len(CORE_DIRS)} directories and {len(paths) - len(CORE_DIRS)} named files outside them; "
               f"{nadd} file(s) added since {anchor[:8]}")
    if problems:
        print(f"HISTORY REFUSED: {summary}; " + " | ".join(problems))
        return 16
    print(f"HISTORY OK: {summary}, none a shadowing module; no change but an addition since {anchor[:8]}; no uncommitted change")
    return 0


def main():
    ap = argparse.ArgumentParser(description="E188's history check (run from the lab's top)")
    ap.add_argument("mode", choices=["tree", "paths"])
    ap.add_argument("--anchor", default=ANCHOR)
    a = ap.parse_args()
    if not os.path.isfile("tools/claims-v3/e188/E188.md"):
        print("run from the lab's top (no tools/claims-v3/e188/E188.md here)")
        return 10
    anchor = resolve(a.anchor)
    if not anchor:
        print(f"HISTORY REFUSED: the anchor {a.anchor} is not a commit here")
        return 16
    if a.mode == "paths":
        for p in e188_paths()[0]:
            print(p)
        return 0
    return tree(anchor)


if __name__ == "__main__":
    sys.exit(main())
