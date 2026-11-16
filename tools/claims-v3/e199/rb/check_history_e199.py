#!/usr/bin/env python3
"""E199's history check (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): E192's (rb/check_history_e192.py, a6fe5c20,
unchanged beside it) with E199's paths: what the day runs and reads has not changed since it was pinned, only been added to; and no E199
datum exists before the session.

    /usr/bin/python3 -I -B tools/claims-v3/e199/rb/check_history_e199.py tree
    /usr/bin/python3 -I -B tools/claims-v3/e199/rb/check_history_e199.py nodatum
    /usr/bin/python3 -I -B tools/claims-v3/e199/rb/check_history_e199.py names

From the lab clone's top, it reads git only (no network, no write).
  tree:
  1. E199's registration commit, found by its content (the commit that added tools/claims-v3/e199/E199.md, whose e199 subtree reads
     070b4e2d...: the registration, fixed before any datum); since it, nothing under tools/claims-v3/e199/ changed or went: additions only; and
     since the kit's commit (the one that added tools/claims-v3/e199/KIT.md) the same, when it exists;
  2. on the other files E199's day reads (PATHS below: E192's whole folder, whose proposal, desk files and checker E199 runs; E191's
     identity module; E151's rail filter; the audit and its two tables; E89's per-sensor sampler; the heater's source; k6's and v3.1's
     runbook files; E183's desk-path gate; E178's scrub and E164's patterns it imports; and THE SEALED CARD-1 FOLDER,
     tools/claims-v3/sealed-card1/, where a dated note of E199's freeze lines may be ADDED after the land: additions are accepted there as
     everywhere): no commit since the registration changed or removed one: additions only;
  3. nothing untracked anywhere under those paths and tools/claims-v3/e199 (git status --untracked-files=all);
  4. NO ADDED OR UNCOMMITTED FILE SHADOWS A MODULE the day's Python can import, in a folder the day's scripts put ahead of the standard
     library on sys.path (SYSPATH_DIRS, each with the script that puts it there): a module file (.py, .pyc, .pyw, .so, .pyd) or a package
     (<name>/__init__.*) whose name is a standard-library module's or one of the day's own (MODULES). Candidates: every file added since
     the registration in those folders, and every file untracked or staged as new there.
  nodatum: no commit of any ref touches docs/reports/data/*e199*, and no ref's tip holds a docs/reports/data/<folder> whose name carries
     "-e199" as a word (true until E199's data commit). A note under tools/claims-v3/sealed-card1/ is not a datum.
Prints HISTORY OK / HISTORY FAIL (tree), NO-DATUM OK / DATUM FOUND (nodatum); exit 0 or 16; 10 for a usage error.
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import subprocess
import sys

REG_SUBTREE = "070b4e2d9135c952cac0dcf61e212efd732ada8e"
E = "tools/claims-v3/e199/"
PATHS = ["tools/claims-v3/e192/", "tools/claims-v3/e191/e191_ident.py", "tools/claims-v3/e151/railfilter_e151.py",
         "tools/claims-v3/sealed-card1/",
         "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "tools/claims-v3/e144/dmcmd_table_e144.json",
         "tools/claims-v3/e89/pvt_sample.py", "workloads/sparsity/host/main.cpp",
         "tools/claims-v3/q141k-runbook/k6/", "tools/claims-v3/q141k-runbook/v3.1/", "tools/claims-v3/e183/rb/nopath_desk_e183.sh",
         "tools/claims-v3/e183/rb/nopath_spell_e183.py", "tools/claims-v3/e178/scrub_tree_e178.py", "tools/claims-v3/e164/scrub_etwho_e164.py"]
# The folders the day's Python puts ahead of the standard library on sys.path, and what puts each there. A script run by its path without
# -I has its own folder first; sys.path.insert(0, ...) puts a folder first under any flags. Every E199 script itself runs with -I.
SYSPATH_DIRS = [
    "tools/claims-v3/",                      # preflight_e199.sh: `python3 tools/claims-v3/dmcmd_audit.py` (no -I), at the desk and on the box
    "tools/claims-v3/e199/",                 # gate_e199.py: sys.path.insert(0, its own folder) for ident_e199
    "tools/claims-v3/e191/",                 # gate_e199.py and ident_e199.py: sys.path.insert(0, ../e191) for e191_ident
    "tools/claims-v3/e151/",                 # prefilter_e199.py imports railfilter_e151 from its folder (step 13)
    "tools/claims-v3/e192/proposal/src/",    # run_session.sh: `python3 -B run_block.py`, `python3 -B stopwatch.py` (no -I), on the box
    "tools/claims-v3/e89/",                  # run_session.sh: `python3 -B "$PVT_SAMPLE"` (no -I), on the box
    "tools/claims-v3/q141k-runbook/v3.1/",   # k6's rb_common.sh: `"$RB_PY" -B rb_run.py` and `nopath_q142s.py` (no -I), every call
    "tools/claims-v3/e178/",                 # step 11: `python3 -B scrub_tree_e178.py` (no -I)
    "tools/claims-v3/e164/",                 # scrub_tree_e178.py's own sys.path.insert(0, ../e164)
]
MODULES = {"numpy", "gate_e199", "ident_e199", "e191_ident", "drycheck_e199", "standin_e199", "realpath_e199", "collect_e199",
           "check_history_e199", "realbytes_e199", "dryaudit_e199", "score_e199", "prefilter_e199", "forecast_e199", "plan_e199",
           "railfilter_e151", "check_e192", "gate_e192", "drycheck_e192", "standin_e192", "realpath_e192", "collect_e192", "check_history_e192",
           "run_block", "stopwatch", "reduce_intbits", "check_elf", "dmcmd_audit", "pvt_sample", "rb_run", "nopath_q142s",
           "ccdone_q142s", "scrub_tree_e178", "scrub_etwho_e164", "nopath_spell_e183", "compare_arms_e192", "order_e192",
           "synth_session_e192", "synth_compare_e192", "loop_order_e192"}
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
    _, o = git("log", "--diff-filter=A", "--format=%H", "--", E + "E199.md")
    c = o.split()[-1] if o.split() else ""
    return c


def nodatum():
    _, o = git("log", "--all", "--format=%H", "--", "docs/reports/data/*e199*")
    commits = [x for x in o.split() if x]
    _, refs = git("for-each-ref", "--format=%(objectname) %(refname)")
    rx = re.compile(r"(^|-)e199(-|$)")
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
        print("DATUM FOUND: %d commit(s) touching docs/reports/data/*e199*; tip paths %s" % (len(commits), hits[:5]))
        return 16
    print("NO-DATUM OK: %d refs read; 0 commits touch docs/reports/data/*e199*; no ref's tip holds an e199 data folder" % n)
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
        print("HISTORY FAIL: the registration's commit was not found (tools/claims-v3/e199/E199.md never added)")
        return 16
    _, t = git("rev-parse", "%s:tools/claims-v3/e199" % reg)
    if t.strip() != REG_SUBTREE:
        bad.append("the registration commit %s's e199 subtree reads %s, not %s" % (reg[:12], t.strip()[:12], REG_SUBTREE[:12]))
    rc, _ = git("merge-base", "--is-ancestor", reg, "HEAD")
    if rc != 0:
        bad.append("the registration %s is not an ancestor of HEAD" % reg[:12])
    for what, path in (("the registration", E + "E199.md"), ("the kit", E + "KIT.md")):
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
    print("HISTORY OK: %s: nothing under tools/claims-v3/e199 changed since; on the %d other paths the day reads %d files added since "
          "the registration, none changed or removed; nothing untracked; no shadowing addition or uncommitted file in the %d folders the "
          "day's Python puts first (%d names: %s, and the day's own)" % ("; ".join(notes), len(PATHS), len([r for r in rows if r[0] == "A"]),
                                                                       len(SYSPATH_DIRS), len(names), src))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
