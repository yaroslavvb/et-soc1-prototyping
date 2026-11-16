#!/usr/bin/env python3
"""E196's history check (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), E192's form (tools/claims-v3/e192/rb/
check_history_e192.py): what the day runs and reads has not changed since it was pinned, only been added to; and no E196 datum exists
before the session.

    /usr/bin/python3 -I -B tools/claims-v3/e196/rb/check_history_e196.py tree
    /usr/bin/python3 -I -B tools/claims-v3/e196/rb/check_history_e196.py nodatum
    /usr/bin/python3 -I -B tools/claims-v3/e196/rb/check_history_e196.py names

From the lab clone's top, it reads git only (no network, no write).
  tree:
  1. E196's registration commit, found by its content (the commit that added tools/claims-v3/e196/E196.md, whose e196 subtree reads
     6f692709...: the registration with its freeze line, before any datum); since it, nothing under tools/claims-v3/e196/ changed or went:
     additions only; and since the kit's commit (the one that added tools/claims-v3/e196/KIT.md) the same, when it exists;
  2. on the other files E196's day reads (PATHS below: the audit and its table, E128's guard, the lab's unchanged sparsity workload, the
     five lab tiles, k6's and v3.1's runbook files, E183's desk-path gate): no commit since the registration changed or removed one:
     additions only;
  3. nothing untracked anywhere under those paths and tools/claims-v3/e196 (git status --untracked-files=all);
  4. NO ADDED OR UNCOMMITTED FILE SHADOWS A MODULE the day's Python can import, in a folder the day's scripts put ahead of the standard
     library on sys.path (SYSPATH_DIRS, each with the script that puts it there): a module file (.py, .pyc, .pyw, .so, .pyd) or a package
     (<name>/__init__.*) whose name is a standard-library module's (sys.stdlib_module_names and sys.builtin_module_names, Python 3.10
     or later; this interpreter's own standard-library directories on 3.9) or one of the day's own (MODULES). Candidates: every file
     added since the registration in those folders, and every file untracked or staged as new there.
  nodatum: no commit of any ref touches docs/reports/data/*e196*, and no ref's tip holds a docs/reports/data/<folder> whose name carries
     "-e196" as a word (true until E196's data commit). A gate stop's record (docs/reports/gate-stops/) is not a datum.
Prints HISTORY OK / HISTORY FAIL (tree), NO-DATUM OK / DATUM FOUND (nodatum); exit 0 or 16; 10 for a usage error.
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import subprocess
import sys

REG_SUBTREE = "6f692709e6446c49c61c16d62ad53fda82d685e3"
E = "tools/claims-v3/e196/"
PATHS = ["tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "tools/claims-v3/e128/ettelem_guard.sh",
         "workloads/sparsity/CMakeLists.txt", "workloads/sparsity/host/", "workloads/sparsity/kernel/", "workloads/sparsity/sparsity_args.h",
         "tools/claims-v3/kinds/tiles/fp32/", "tools/claims-v3/q141k-runbook/k6/", "tools/claims-v3/q141k-runbook/v3.1/",
         "tools/claims-v3/e183/rb/nopath_desk_e183.sh", "tools/claims-v3/e183/rb/nopath_spell_e183.py"]
# The folders the day's Python puts ahead of the standard library on sys.path, and what puts each there. A script run by its path without
# -I has its own folder first; sys.path.insert(0, ...) puts a folder first under any flags.
SYSPATH_DIRS = [
    "tools/claims-v3/",                      # preflight_e196.sh: `python3 tools/claims-v3/dmcmd_audit.py` (no -I), at the desk and on the box
    "tools/claims-v3/e196/",                 # run_session_e196.sh: `python3 -B run_block_e196.py`, `stops_e196.py` (no -I); run_block_e196.py's
                                             # sys.path.insert(0, HERE): e196_lines
    "tools/claims-v3/e196/proposal/src/",    # run_session_e196.sh: `python3 -B stopwatch.py`, `make_x14.py`; run_block_e196.py's sys.path.insert
    "tools/claims-v3/q141k-runbook/v3.1/",   # k6's rb_common.sh: `"$RB_PY" -B rb_run.py` and `nopath_q142s.py` (no -I), every call
]
MODULES = {"run_block_e196", "stops_e196", "e196_lines", "drycheck_e196", "check_e196", "collect_e196", "check_history_e196",
           "make_x14", "stopwatch", "reduce_e196", "reduce_x14", "run_block", "dmcmd_audit", "rb_run", "nopath_q142s", "ccdone_q142s",
           "nopath_spell_e183", "standin_e196", "realpath_e196", "realbytes_e196", "compare_arms_e196", "order_e196",
           "synth_session_e196", "synth_compare_e196"}
IMPORT_SUFFIXES = (".py", ".pyc", ".pyw", ".so", ".pyd")


def git(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def stdlib_names():
    names = set(sys.builtin_module_names)
    if hasattr(sys, "stdlib_module_names"):
        return names | set(sys.stdlib_module_names), "sys.stdlib_module_names (Python %s)" % sys.version.split()[0]
    import sysconfig
    seen = []
    for key in ("stdlib", "platstdlib"):
        d = sysconfig.get_paths().get(key)
        for sub in (d, os.path.join(d or "", "lib-dynload")):
            if not sub or not os.path.isdir(sub) or sub in seen:
                continue
            seen.append(sub)
            for n in os.listdir(sub):
                p = os.path.join(sub, n)
                if os.path.isdir(p):
                    if any(os.path.exists(os.path.join(p, "__init__" + s)) for s in (".py", ".pyc")):
                        names.add(n)
                elif n.endswith(IMPORT_SUFFIXES):
                    names.add(n.split(".", 1)[0])
    return names, "this interpreter's standard-library directories (Python %s)" % sys.version.split()[0]


def shadow_name(path):
    for d in SYSPATH_DIRS:
        if not path.startswith(d):
            continue
        parts = path[len(d):].split("/")
        if len(parts) == 1 and parts[0].endswith(IMPORT_SUFFIXES):
            return parts[0].split(".", 1)[0]
        if len(parts) == 2 and parts[1].split(".", 1)[0] == "__init__" and parts[1].endswith(IMPORT_SUFFIXES):
            return parts[0]
    return None


def registration():
    _, o = git("log", "--diff-filter=A", "--format=%H", "--", E + "E196.md")
    c = o.split()[-1] if o.split() else ""
    return c


def nodatum():
    _, o = git("log", "--all", "--format=%H", "--", "docs/reports/data/*e196*")
    commits = [x for x in o.split() if x]
    _, refs = git("for-each-ref", "--format=%(objectname) %(refname)")
    rx = re.compile(r"(^|-)e196(-|$)")
    hits, n = [], 0
    for ln in refs.splitlines():
        if not ln.strip():
            continue
        n += 1
        sha, name = ln.split(" ", 1)
        _, t = git("ls-tree", "--name-only", sha, "docs/reports/data/")
        for p in t.splitlines():
            if rx.search(p.split("/")[-1]):
                hits.append("%s:%s" % (name, p))
    if commits or hits:
        print("DATUM FOUND: %d commit(s) touching docs/reports/data/*e196*; tip paths %s" % (len(commits), hits[:5]))
        return 16
    print("NO-DATUM OK: %d refs read; 0 commits touch docs/reports/data/*e196*; no ref's tip holds an e196 data folder" % n)
    return 0


def main(argv):
    if argv and argv[0] == "nodatum":
        return nodatum()
    if argv and argv[0] == "names":
        names, src = stdlib_names()
        print("SHADOW NAMES: %d standard-library names from %s; with the day's own %d; json %s, re %s, subprocess %s, socket %s, random %s; "
              "read in %d folders: %s" % (len(names), src, len(MODULES), "json" in names, "re" in names, "subprocess" in names,
                                          "socket" in names, "random" in names, len(SYSPATH_DIRS), ", ".join(SYSPATH_DIRS)))
        return 0
    if not argv or argv[0] != "tree":
        print(__doc__)
        return 10
    bad, notes = [], []
    reg = registration()
    if not reg:
        print("HISTORY FAIL: the registration's commit was not found (tools/claims-v3/e196/E196.md never added)")
        return 16
    _, t = git("rev-parse", "%s:tools/claims-v3/e196" % reg)
    if t.strip() != REG_SUBTREE:
        bad.append("the registration commit %s's e196 subtree reads %s, not %s" % (reg[:12], t.strip()[:12], REG_SUBTREE[:12]))
    rc, _ = git("merge-base", "--is-ancestor", reg, "HEAD")
    if rc != 0:
        bad.append("the registration %s is not an ancestor of HEAD" % reg[:12])
    for what, path in (("the registration", E + "E196.md"), ("the kit", E + "KIT.md")):
        _, o = git("log", "--diff-filter=A", "--format=%H", "--", path)
        c = o.split()[-1] if o.split() else ""
        if not c:
            notes.append("%s's commit not yet made" % what)
            continue
        _, o2 = git("diff", "--name-status", "--no-renames", c, "HEAD", "--", E)
        ch = [ln for ln in o2.splitlines() if ln.strip() and not ln.startswith("A\t")]
        if ch:
            bad.append("changed or removed since %s's commit %s: %s" % (what, c[:12], ", ".join(ch[:8])))
        notes.append("%s %s" % (what, c[:12]))
    _, out = git("diff", "--name-status", "--no-renames", reg, "HEAD", "--", *PATHS)
    rows = [ln.split("\t") for ln in out.splitlines() if ln.strip()]
    changed = [r for r in rows if r[0] != "A"]
    if changed:
        bad.append("changed or removed since the registration on the files the day reads: " + ", ".join("%s %s" % (r[0], r[-1]) for r in changed[:8]))
    _, st = git("status", "--porcelain", "--untracked-files=all", "--", E, *PATHS)
    if st.strip():
        bad.append("uncommitted or untracked: " + ", ".join(ln[3:] for ln in st.splitlines()[:8]))
    names, src = stdlib_names()
    names |= MODULES
    _, o = git("diff", "--name-status", "--no-renames", "-z", reg, "HEAD", "--", *SYSPATH_DIRS)
    f = o.split("\0")
    added = {f[i + 1] for i in range(0, len(f) - 1, 2) if f[i] == "A"}
    _, st2 = git("status", "--porcelain", "-z", "--no-renames", "--untracked-files=all", "--", *SYSPATH_DIRS)
    new = {e[3:] for e in st2.split("\0") if len(e) > 3 and ("?" in e[:2] or "A" in e[:2])}
    own = {p for p in added | new if p.startswith(E) and not p.startswith(E + "proposal/")}
    sh = sorted(p for p in added if shadow_name(p) and shadow_name(p) in names and p not in own)
    shn = sorted(p for p in new if shadow_name(p) and shadow_name(p) in names and p not in own)
    if sh:
        bad.append("a shadowing addition: " + ", ".join("%s (as %s)" % (p, shadow_name(p)) for p in sh))
    if shn:
        bad.append("a shadowing file not committed: " + ", ".join("%s (as %s)" % (p, shadow_name(p)) for p in shn))
    if bad:
        print("HISTORY FAIL: " + "; ".join(bad))
        return 16
    print("HISTORY OK: %s: nothing under tools/claims-v3/e196 changed since; on the %d other paths the day reads %d files added since "
          "the registration, none changed or removed; nothing untracked; no shadowing addition or uncommitted file in the %d folders the "
          "day's Python puts first (%d names: %s, and the day's own)" % ("; ".join(notes), len(PATHS), len([r for r in rows if r[0] == "A"]),
                                                                       len(SYSPATH_DIRS), len(names), src))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
