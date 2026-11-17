#!/usr/bin/env python3
"""E211's history check (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum), E206's check_history_e206.py (landed in 906699ea; E190's
rules), as E207's kit ported it (Q199), for E211's paths, run by step 2 and after the collection, at the desk (/usr/bin/python3 -I -B; Python's own modules only):

    /usr/bin/python3 -I -B tools/claims-v3/e211/rb/check_history_e211.py tree [--reg <commit>]

  1. the registration commit is found by its CONTENT (the commit that added tools/claims-v3/e211/E211.md; it lands after this file is written,
     so no hash is pinned for it) and its tools/claims-v3/e211 subtree reads fa109d01... (reg-e211's land as fix-e211 amended it); HEAD descends from it;
  2. ADDITIONS ONLY under tools/claims-v3/e211 since the registration: every path git reports between the registration and HEAD is added (A);
     none modified, deleted, renamed or changed in type (so the registration's 39 files (38 at reg-e211's land; fix-e211 added power-a1-e211.json) and every kit file stay as first committed; a dated note
     is a new file);
  3. NO SHADOWING ADDITION since the registration anywhere under tools/: a new module file (<name>.py, or an extension module) or package
     (<name>/__init__.py) whose name is a standard-library module's would be imported in its place by a kit or registration script that puts
     its own folder first on sys.path (sys.stdlib_module_names on Python 3.10 or later);
  4. nothing modified or untracked under the paths the box or the desk runs for E211 (git status --porcelain): E211's folder (rgm211's tree
     in it), MM1-v1's folder and E101's committed data (the forecasts' inputs), rgm136, E128's guard (k6's step 7), E206's folder (the identity
     gate's check_e206.py, F1's and F2's route) and E190's and the ledger (F1's and F2's route), the tiles and their manifest, the k6 runbook,
     the device-command checker v2 and its table.
Prints "HISTORY OK: ..." (exit 0) or "HISTORY FAIL: ..." (exit 1). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REG_SUBTREE = "fa109d016f5e0497a5ee5d34a69806ad2b3be511"
E = "tools/claims-v3/e211"
RUN_PATHS = [E, "tools/matmul/mm1/v1", "tools/claims-v3/e136", "tools/claims-v3/e128", "tools/claims-v3/e206", "tools/claims-v3/e190",
             "docs/reports/data/2026-11-01-e101-real-matmul", "tools/claims-v3/kinds/tiles", "tools/claims-v3/kinds/kinds.json",
             "tools/ledger", "tools/claims-v3/q141k-runbook", "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json"]
FALLBACK = {"argparse", "ast", "copy", "datetime", "fcntl", "gzip", "hashlib", "json", "math", "os", "pwd", "random", "re", "shutil",
            "signal", "socket", "statistics", "struct", "subprocess", "sys", "threading", "time", "zoneinfo", "collections", "functools",
            "itertools", "io", "pathlib", "string", "types", "typing", "warnings", "glob", "tempfile", "textwrap", "csv", "enum", "abc",
            "traceback", "bisect", "decimal"}


def git(*a):
    r = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True)
    return r.returncode, r.stdout


def main(argv):
    if not argv or argv[0] != "tree":
        print(__doc__)
        return 2
    bad = []
    if "--reg" in argv:
        reg = argv[argv.index("--reg") + 1]
    else:
        rc, out = git("log", "--diff-filter=A", "--format=%H", "--", E + "/E211.md")
        reg = out.split()[-1] if out.split() else ""
    if not reg:
        print("HISTORY FAIL: no registration commit (no commit added tools/claims-v3/e211/E211.md)")
        return 1
    rc, _ = git("merge-base", "--is-ancestor", reg, "HEAD")
    if rc != 0:
        bad.append(f"HEAD does not descend from the registration {reg[:12]}")
    rc, st = git("rev-parse", f"{reg}:{E}")
    if st.strip() != REG_SUBTREE:
        bad.append(f"the registration's {E} subtree reads {st.strip()[:12] or 'nothing'}, not {REG_SUBTREE[:12]}")
    rc, out = git("diff", "--name-status", "--no-renames", reg, "HEAD", "--", E)
    changed = [ln for ln in out.splitlines() if ln and not ln.startswith("A\t")]
    added = [ln for ln in out.splitlines() if ln.startswith("A\t")]
    if changed:
        bad.append("not an addition under " + E + ": " + "; ".join(changed[:6]))
    names = getattr(sys, "stdlib_module_names", None) or FALLBACK
    rc, out = git("diff", "--name-only", "--diff-filter=A", reg, "HEAD", "--", "tools")
    shadow = []
    for p in out.splitlines():
        base = os.path.basename(p)
        stem = None
        if base.endswith(".py"):
            stem = base[:-3]
        elif ".cpython-" in base or base.endswith(".so"):
            stem = base.split(".")[0]
        if base == "__init__.py":
            stem = os.path.basename(os.path.dirname(p))
        if stem and stem in names:
            shadow.append(p)
    if shadow:
        bad.append("a shadowing addition (a standard-library module's name): " + ", ".join(shadow[:6]))
    rc, out = git("status", "--porcelain", "--untracked-files=all", "--", *RUN_PATHS)
    if out.strip():
        bad.append(f"{len(out.splitlines())} path(s) modified or untracked under E211's run paths")
    if bad:
        print("HISTORY FAIL: " + " | ".join(bad))
        return 1
    print(f"HISTORY OK: HEAD descends from the registration {reg[:12]} (subtree {REG_SUBTREE[:8]}); {len(added)} additions and nothing else "
          f"under {E} since it; no shadowing addition under tools/ ({'sys.stdlib_module_names' if hasattr(sys, 'stdlib_module_names') else 'the fixed list'}); "
          f"E211's run paths clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
