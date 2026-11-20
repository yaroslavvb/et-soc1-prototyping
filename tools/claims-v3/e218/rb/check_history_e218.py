#!/usr/bin/env python3
"""E218's history check (Q230, lane kit-e218, Thu 19 Nov 2026, before any E218 datum), E215 arm A's check_history_e215.py (landed in 8bde0182;
E206's rules, E190's behind them) for E218's paths, run by step 2 and after the collection, at the desk (/usr/bin/python3 -I -B; Python's own
modules only):

    /usr/bin/python3 -I -B tools/claims-v3/e218/rb/check_history_e218.py tree [--reg <commit>]

  1. the registration commit is found by its CONTENT (the commit that added tools/claims-v3/e218/E218.md; it lands after this file is written,
     so no hash is pinned for it) and its tools/claims-v3/e218 subtree reads deb6726f... (reg-e218's land); HEAD descends from it;
  2. ADDITIONS ONLY under tools/claims-v3/e218 since the registration: every path git reports between the registration and HEAD is added (A);
     none modified, deleted, renamed or changed in type (so the registration's files and every kit file stay as first committed; a dated note
     is a new file);
  3. NO SHADOWING ADDITION since the registration anywhere under tools/: a new module file (<name>.py, or an extension module) or package
     (<name>/__init__.py) whose name is a standard-library module's would be imported in its place by a kit or registration script that puts
     its own folder first on sys.path (sys.stdlib_module_names on Python 3.10 or later);
  4. nothing modified or untracked under the paths the box or the desk runs for E218 (git status --porcelain): E218's folder, the sealed-forecast
     note's folder, MM1's folders (tools/matmul/mm1: MM1-v3.2's land with E218's frozen points and forecasts, the predictors MM1-v3.1, MM1-v3 and
     MM1-v2, and the two frozen terms the registration's checks and the scorer read), E136's folder (rgm136), E211's folder (rgm211 and its kernel
     record), E128's guard (k6's step 7), E206's folder (the identity gate's check_e206.py), E213's and E215's folders (the never-run scanners and
     the points and rules helpers the registration imports at their pins; E215's points-e215.json the scorer's real-bytes self-test reads), the
     tiles (kinds/tiles) and their manifest, the two committed data directories the scorer's real-bytes self-test and the desk tests read (E215 arm
     A's and E213 arm A's on aifoundry3), the k6 runbook, the device-command checker v2 and its table.
Prints "HISTORY OK: ..." (exit 0) or "HISTORY FAIL: ..." (exit 1). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REG_SUBTREE = "deb6726f8823b6dd08a10d72ddd68837862c2a92"
E = "tools/claims-v3/e218"
RUN_PATHS = [E, "tools/claims-v3/sealed-e218", "tools/matmul/mm1", "tools/claims-v3/e136", "tools/claims-v3/e211", "tools/claims-v3/e128",
             "tools/claims-v3/e206", "tools/claims-v3/e213", "tools/claims-v3/e215", "tools/claims-v3/kinds/tiles", "tools/claims-v3/kinds/kinds.json",
             "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3", "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3",
             "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1", "workloads/nocbench/analyze.py",
             "tools/claims-v3/q141k-runbook", "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json"]
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
        rc, out = git("log", "--diff-filter=A", "--format=%H", "--", E + "/E218.md")
        reg = out.split()[-1] if out.split() else ""
    if not reg:
        print("HISTORY FAIL: no registration commit (no commit added tools/claims-v3/e218/E218.md)")
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
        bad.append(f"{len(out.splitlines())} path(s) modified or untracked under E218's run paths")
    if bad:
        print("HISTORY FAIL: " + " | ".join(bad))
        return 1
    print(f"HISTORY OK: HEAD descends from the registration {reg[:12]} (subtree {REG_SUBTREE[:8]}); {len(added)} additions and nothing else "
          f"under {E} since it; no shadowing addition under tools/ ({'sys.stdlib_module_names' if hasattr(sys, 'stdlib_module_names') else 'the fixed list'}); "
          f"E218's run paths clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
