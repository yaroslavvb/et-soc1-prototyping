#!/usr/bin/env python3
# E186 (Q158, the kit): the history check and note M1's reader gate. A port of E185's day-2 check (tools/claims-v3/e185/rb/check_day2_v1.py,
# its kit note 3), which answers verify-d2b's faults 1-3 on the day-2 kits: a committed change to a file the day reads, made together
# with its list line (or under a copied line), passed a step 2 that holds a list at its count only; and note M1's reader ran behind a gate
# weaker than step 2's byte pin. E186's step 2 holds eleven lists at their own bytes, but its kit's list at its count only (it lists step 2
# itself), so E186's scorer, its brief and every kit file would sit behind that count alone without this check.
#
#   /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_history_e186.py tree [--anchor REV]
#   /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_history_e186.py m1 --data DIR [--anchor REV]
#   /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_history_e186.py paths [--anchor REV]
#
# Run from the lab's top (the runbook's rb_local runs it there). The anchor is E186's registration (a41408d9, RB_E186_BASE; the runbook's
# desk test passes its scratch repository's root).
# tree: every one of these, with the problems named, then HISTORY OK or HISTORY REFUSED:
#   1. HEAD descends from the anchor;
#   2. no commit since the anchor changed anything but an addition on E186's paths (git log -m --full-history --diff-filter=a, and the
#      tree diff from the anchor with the same filter; the filter a is everything but an addition: modified, deleted, renamed, type
#      changed): E186's paths are E186's, M12's, E182's, the k6/v3.1 runbook's and the workload's directories, plus every file outside
#      them that a list E186 reads or harness-e186.json names. A change to note M1's five files or its list is reported, never a gate here
#      (the M1 arm is a reported arm; step 11's M1 gate reads them);
#   3. no file added since the anchor in those directories is a Python module or package that shadows one the system python finds outside
#      the lab clone (the user site among them), or shares its module name with another of those modules, or is a byte-code or .pth file
#      (a planted json.py beside a script would be imported before the standard one);
#   4. no uncommitted change on E186's paths (git status, untracked files too).
# m1: note M1's reader gate, in step 11 after the score. Its list SHA256SUMS-e186-m1 at its count (5), at its own sha256 and with every
#   entry OK, and no change but an addition to its five files or the list since the anchor, and none uncommitted, and the scored file
#   there; on all of them it runs the reader by note M1's own run
#   line (M1-4: /usr/bin/python3 -B tools/claims-v3/e186/arm_m1_read_e186.py --scored <data>/scored-e186.json --out <data>/arm-m1-e186),
#   bounded at 50 s (inside the runbook's 60 s read), and checks that it wrote nothing in the data directory but its two outputs. It prints one of M1-READ, M1-NOT-RUN
#   <why> (the gate refused: the reader never ran), M1-READER-REFUSED rc <n> (the reader's own refusal) or M1-WROTE-OTHER <files>.
# paths: prints E186's paths, one a line.
#
# Exit codes (the runbooks'): 0 passed (tree: HISTORY OK; m1: M1-READ); 2 the reader's own refusal (m1); 10 usage; 16 a gate says stop
# (tree: HISTORY REFUSED; m1: M1-NOT-RUN or M1-WROTE-OTHER). Python's own modules only; it reads git and files and writes nothing but,
# in m1, what the reader writes.
# SPDX-License-Identifier: Apache-2.0
import argparse
import hashlib
import importlib.machinery
import json
import os
import subprocess
import sys

ANCHOR = "a41408d971c2bf9d5a9e5218ed27e304b1ddcf8b"   # E186: registration, alone (07:15:08 PST Sun 8 Nov 2026)
CORE_DIRS = ["tools/claims-v3/e186", "tools/claims-v3/m12", "tools/claims-v3/e182", "tools/claims-v3/q141k-runbook", "workloads/sparsity"]
# every list E186's step 2 reads (base "top": entries from the lab's top; "beside": from the list's own directory)
LISTS = [
    ("tools/claims-v3/e186/SHA256SUMS-e186-registration", "top"),
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
    ("tools/claims-v3/e186/SHA256SUMS-e186-kit", "top"),
]
HARNESS = "tools/claims-v3/e186/harness-e186.json"
M1_LIST = ("tools/claims-v3/e186/SHA256SUMS-e186-m1", 5, "06d278ddf41e5cd55cf210f1444a517312fc1a4a4a41a3bcffabd723dec426b3")
M1_FILES = ["tools/claims-v3/e186/E186.md.dated-note-M1.md", "tools/claims-v3/e186/m1-october-forecast-model-e186.json",
            "tools/claims-v3/e186/arm_m1_read_e186.py", "tools/claims-v3/e186/selftest_arm_m1_e186.py",
            "tools/claims-v3/e186/logs/selftest-arm-m1-e186.txt"]   # the list's five entries
M1_ALL = M1_FILES + [M1_LIST[0]]                                       # with the list itself: a change here is reported in tree, never a gate
M1_OUTPUTS = ("arm-m1-e186.json", "arm-m1-e186.txt")
READER_BOUND_S = 50                          # inside the runbook's 60 s read (rb_run.py's read class)


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


def e186_paths():
    """(paths, dirs, unreadable lists): the core directories, plus every file a list or the harness names outside them."""
    named, bad = set(), []
    for rel, base in LISTS + [(M1_LIST[0], "top")]:
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
    paths, dirs, bad = e186_paths()
    if bad:
        problems.append("unreadable: " + ", ".join(bad))
    hg, hm = history(anchor, paths)
    if hg:
        problems.append(f"history: {len(hg)} change(s) other than an addition since {anchor[:8]} on E186's paths: " +
                        "; ".join(hg[:6]) + (" ..." if len(hg) > 6 else ""))
    print(f"note M1's files: {len(hm)} changed since {anchor[:8]} (reported, never a gate here; step 11's M1 gate reads them)"
          + (": " + "; ".join(hm[:6]) if hm else ""))
    nadd, sp = shadows(anchor, dirs)
    if sp:
        problems.append("additions: " + "; ".join(sp[:6]) + (" ..." if len(sp) > 6 else ""))
    st = status(paths)
    if st:
        problems.append(f"status: {len(st)} uncommitted change(s) on E186's paths: " + "; ".join(s.strip() for s in st[:6]))
    summary = (f"E186's paths: {len(CORE_DIRS)} directories and {len(paths) - len(CORE_DIRS)} named files outside them; "
               f"{nadd} file(s) added since {anchor[:8]}")
    if problems:
        print(f"HISTORY REFUSED: {summary}; " + " | ".join(problems))
        return 16
    print(f"HISTORY OK: {summary}, none a shadowing module; no change but an addition since {anchor[:8]}; no uncommitted change")
    return 0


def snapshot(d):
    out = {}
    for root, _, files in os.walk(d):
        for f in files:
            p = os.path.join(root, f)
            try:
                out[os.path.relpath(p, d)] = sha256_file(p)
            except OSError:
                out[os.path.relpath(p, d)] = "<unreadable>"
    return out


def m1(anchor, data):
    why = []
    rel, count, own = M1_LIST
    ent = read_list(rel, "top")
    if ent is None:
        why.append(f"{rel} unreadable")
    else:
        if len(ent) != count:
            why.append(f"{os.path.basename(rel)} holds {len(ent)} entries, pinned {count}")
        if sha256_file(rel) != own:
            why.append(f"{os.path.basename(rel)}'s own bytes differ from the pin")
        badent = [p for h, p in ent if not os.path.isfile(p) or sha256_file(p) != h]
        if badent:
            why.append(f"{len(badent)} entr(ies) not OK: " + ", ".join(badent[:3]))
        if sorted(p for _, p in ent) != sorted(M1_FILES):
            why.append("its entries are not note M1's five files")
    rc, so, se = git("log", "-m", "--full-history", "--diff-filter=a", "--name-status", "--format=@@%H", f"{anchor}..HEAD", "--", *M1_ALL)
    if rc != 0:
        why.append(f"git log failed (rc {rc})")
    elif [x for x in parse_name_status(so) if x[1]]:
        why.append("a change other than an addition to note M1's files or list since " + anchor[:8])
    st = status(M1_ALL)
    if st:
        why.append(f"{len(st)} uncommitted change(s) to note M1's files")
    scored = os.path.join(data, "scored-e186.json")
    if not os.path.isfile(scored):
        why.append(f"no {scored}")
    if why:
        print("M1-NOT-RUN " + "; ".join(why) + " (the reader never ran; recorded for the data README, never a stop)")
        return 16
    before = snapshot(data)
    cmd = ["/usr/bin/python3", "-B", "tools/claims-v3/e186/arm_m1_read_e186.py", "--scored", scored, "--out", os.path.join(data, "arm-m1-e186")]
    try:
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=READER_BOUND_S)
        rrc, out = p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        rrc, out = 124, f"(killed at its {READER_BOUND_S} s bound)"
    sys.stdout.write(out[-4000:])
    after = snapshot(data)
    other = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k) and k not in M1_OUTPUTS)
    if other:
        print("M1-WROTE-OTHER " + ", ".join(other[:8]) + f" (the reader, rc {rrc}, changed files beside its two outputs)")
        return 16
    if rrc != 0:
        print(f"M1-READER-REFUSED rc {rrc} (the reader's own refusal; recorded for the data README, never a stop)")
        return 2
    print("M1-READ " + " and ".join(o for o in M1_OUTPUTS if o in after))
    return 0


def main():
    ap = argparse.ArgumentParser(description="E186's history check and note M1's reader gate (run from the lab's top)")
    ap.add_argument("mode", choices=["tree", "m1", "paths"])
    ap.add_argument("--anchor", default=ANCHOR)
    ap.add_argument("--data")
    a = ap.parse_args()
    if not os.path.isfile("tools/claims-v3/e186/E186.md"):
        print("run from the lab's top (no tools/claims-v3/e186/E186.md here)")
        return 10
    anchor = resolve(a.anchor)
    if not anchor:
        print(f"HISTORY REFUSED: the anchor {a.anchor} is not a commit here" if a.mode != "m1" else f"M1-NOT-RUN the anchor {a.anchor} is not a commit here")
        return 16
    if a.mode == "paths":
        for p in e186_paths()[0]:
            print(p)
        return 0
    if a.mode == "tree":
        return tree(anchor)
    if not a.data:
        print("m1 needs --data <the data directory>")
        return 10
    return m1(anchor, a.data)


if __name__ == "__main__":
    sys.exit(main())
