#!/usr/bin/env python3
"""E190's history check (Q169, the kit, Fri 13 Nov 2026, before any E190 datum), E189's check_history_e189.py's rules for E190's paths, run
by step 2 and after the collection, at the desk (/usr/bin/python3 -I -B; Python's own modules only):

    /usr/bin/python3 -I -B tools/claims-v3/e190/rb/check_history_e190.py tree [--reg <commit>]

  1. HEAD descends from the registration commit (508d48d9 by default), whose tools/claims-v3/e190 subtree reads 4d4f7440...;
  2. ADDITIONS ONLY under tools/claims-v3/e190 since the registration: every path git reports between the registration and HEAD is added
     (A); none modified, deleted, renamed or changed in type (so the registration's 17 files and every kit file stay as first committed;
     a dated note is a new file);
  3. NO SHADOWING ADDITION since the registration anywhere under tools/: a new module file (<name>.py, or an extension module) or package
     (<name>/__init__.py) whose name is a standard-library module's would be imported in its place by a kit or registration script that
     puts its own folder first on sys.path (sys.stdlib_module_names on Python 3.10 or later; else a fixed list of the modules E190's
     scripts import);
  4. nothing modified or untracked under the paths the box or the desk runs for E190 (git status --porcelain).
Prints "HISTORY OK: ..." (exit 0) or "HISTORY FAIL: ..." (exit 1). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REG = "508d48d9a889ee91a9ff41140a906d103594978a"
REG_SUBTREE = "4d4f74406dd09a454ec105244f07a433555109d0"
E = "tools/claims-v3/e190"
RUN_PATHS = [E, "tools/claims-v3/e136", "tools/claims-v3/e119", "tools/claims-v3/e128", "tools/claims-v3/kinds/tiles", "tools/ledger",
             "tools/claims-v3/q141k-runbook", "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json"]
FALLBACK = {"argparse", "ast", "copy", "datetime", "fcntl", "gzip", "hashlib", "json", "math", "os", "pwd", "random", "re", "shutil",
            "signal", "socket", "statistics", "struct", "subprocess", "sys", "threading", "time", "zoneinfo", "collections", "functools",
            "itertools", "io", "pathlib", "string", "types", "typing", "warnings", "glob", "tempfile", "textwrap", "csv", "enum", "abc"}


def git(*a):
    r = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout


def main(argv):
    if not argv or argv[0] != "tree":
        print(__doc__)
        return 2
    reg = argv[argv.index("--reg") + 1] if "--reg" in argv else REG
    bad = []
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
        bad.append(f"{len(out.splitlines())} path(s) modified or untracked under E190's run paths")
    if bad:
        print("HISTORY FAIL: " + " | ".join(bad))
        return 1
    print(f"HISTORY OK: HEAD descends from the registration {reg[:12]} (subtree {REG_SUBTREE[:8]}); {len(added)} additions and nothing else "
          f"under {E} since it; no shadowing addition under tools/ ({'sys.stdlib_module_names' if hasattr(sys, 'stdlib_module_names') else 'the fixed list'}); "
          f"E190's run paths clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
