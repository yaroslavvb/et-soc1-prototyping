#!/usr/bin/env python3
"""E224 ARM A's history check (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum), E215's check_history_e215.py (landed in 8bde0182;
E206's rules, E190's behind them) for E224's paths, run by arm A's step 2 and after the collection, at the desk (/usr/bin/python3 -I -B; Python's
own modules only):

    /usr/bin/python3 -I -B tools/claims-v3/e224/rb/check_history_e224a.py tree [--reg <commit>]

  1. the registration commit is found by its CONTENT (the commit that added tools/claims-v3/e224/E224.md; it lands after this file is written,
     so no hash is pinned for it) and its tools/claims-v3/e224 subtree reads a46c1682... (reg-e224's registration: its local commit f8e90613);
     HEAD descends from it;
  2. ADDITIONS ONLY under tools/claims-v3/e224 since the registration: every path git reports between the registration and HEAD is added (A);
     none modified, deleted, renamed or changed in type (so the registration's files and every kit file stay as first committed; a dated note
     is a new file);
  3. NO SHADOWING ADDITION since the registration anywhere under tools/: a new module file (<name>.py, or an extension module) or package
     (<name>/__init__.py) whose name is a standard-library module's would be imported in its place by a kit or registration script that puts
     its own folder first on sys.path (sys.stdlib_module_names on Python 3.10 or later);
  4. nothing modified or untracked under the paths the box or the desk runs for E224's arm A (git status --porcelain): E224's folder, the
     sealed-forecast note's folder, MM1's folders (tools/matmul/mm1), E136's (rgm136), E211's (rgm211 and its kernel record), E128's, E206's
     (the identity gate's check), E208's, E209's, E213's, E215's, E216's and E218's folders (the registration's helpers, scanners and frozen
     inputs at their pins), fwgate, the tiles and their manifest, the committed data directories the scorer's real-bytes self-test, the timeout
     table and the desk tests read (E215 arm B's and E213 arm B's on aifoundry1 card 1, E215 arm A's, E213 arm A's and E218's on aifoundry3,
     E216's and E209's on aifoundry2), the k6 runbook, the device-command checker v2 and its table.
Prints "HISTORY OK: ..." (exit 0) or "HISTORY FAIL: ..." (exit 1). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REG_SUBTREE = "a46c16828d696f2936aa087ffb3cec94acb35f6c"   # reg-e224 (Q237): tools/claims-v3/e224 in its local commit f8e90613
E = "tools/claims-v3/e224"
RUN_PATHS = [E, "tools/claims-v3/sealed-e224", "tools/matmul/mm1", "tools/claims-v3/e136", "tools/claims-v3/e211", "tools/claims-v3/e128",
             "tools/claims-v3/e206", "tools/claims-v3/e208", "tools/claims-v3/e209", "tools/claims-v3/e213", "tools/claims-v3/e215",
             "tools/claims-v3/e216", "tools/claims-v3/e218", "tools/claims-v3/fwgate", "tools/claims-v3/kinds/tiles",
             "tools/claims-v3/kinds/kinds.json", "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1",
             "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1", "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3",
             "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3", "docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3",
             "docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2", "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2",
             "workloads/nocbench/analyze.py", "tools/claims-v3/q141k-runbook", "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json",
             "tools/claims-v3/e212/proposal/src/tiles", "tools/claims-v3/e212/proposal/src/SRC-SHA256SUMS", "tools/claims-v3/e217/proposal/src/tiles",
             "tools/claims-v3/e217/proposal/src/SRC-SHA256SUMS", "tools/claims-v3/e220", "tools/claims-v3/e220-notes",
             "docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry1-c1", "docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry2"]
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
        rc, out = git("log", "--diff-filter=A", "--format=%H", "--", E + "/E224.md")
        reg = out.split()[-1] if out.split() else ""
    if not reg:
        print("HISTORY FAIL: no registration commit (no commit added tools/claims-v3/e224/E224.md)")
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
        bad.append(f"{len(out.splitlines())} path(s) modified or untracked under E224's run paths")
    if bad:
        print("HISTORY FAIL: " + " | ".join(bad))
        return 1
    print(f"HISTORY OK: HEAD descends from the registration {reg[:12]} (subtree {REG_SUBTREE[:8]}); {len(added)} additions and nothing else "
          f"under {E} since it; no shadowing addition under tools/ ({'sys.stdlib_module_names' if hasattr(sys, 'stdlib_module_names') else 'the fixed list'}); "
          f"E224's run paths clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
