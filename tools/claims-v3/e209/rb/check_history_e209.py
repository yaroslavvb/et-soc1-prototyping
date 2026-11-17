#!/usr/bin/env python3
"""E209's history check (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum; fix-e209, Q202c: the per-commit check and the amended
registration's subtree), E207's check_history_e207.py (landed in 117885d9; E206's
and E190's rules) for E209's paths, run by step 2 (rb/s03_desk_e209.sh) at the desk (/usr/bin/python3 -I -B; Python's own modules only):

    /usr/bin/python3 -I -B tools/claims-v3/e209/rb/check_history_e209.py tree [--reg <commit>]

  1. the registration commit is found by its CONTENT (the commit that added tools/claims-v3/e209/E209.md; it lands after this file is written,
     so no hash is pinned for it) and its tools/claims-v3/e209 subtree reads afaa6053... (reg-e209's registration with fix-e209's amendment A1:
     fix-e209's local commit cb14eae3, the folder tree its land dir names; reg-e209's own was 95479783...); HEAD descends from it;
  2. ADDITIONS ONLY under tools/claims-v3/e209 since the registration, in two ways: (a) between the registration and HEAD every path git
     reports is added (A), none modified, deleted, renamed or changed in type (the registration's 23 files stay as committed); (b) COMMIT BY
     COMMIT (fix-e209, verify-e209's finding 4): every commit after the registration that touches tools/claims-v3/e209 only adds files there
     (git log --full-history --name-status --no-renames), and no merge commit since it touches the folder - so a later commit that modifies a
     kit file, step 2 itself (rb/s03_desk_e209.sh, outside the kit's list) among them, fails here although (a), a net diff, reads it as an
     addition. A dated note or amendment is a new file. (b) runs only from an unmodified step 2: a step 2 changed to skip this check is caught
     by comparing its sha256 with the land's anchor before running it (the card-lane brief, step 2);
  3. NO SHADOWING ADDITION since the registration anywhere under tools/: a new module file (<name>.py, or an extension module) or package
     (<name>/__init__.py) whose name is a standard-library module's would be imported in its place by a kit or registration script that puts
     its own folder first on sys.path (sys.stdlib_module_names on Python 3.10 or later);
  4. nothing modified or untracked under the paths the box or the desk runs for E209 (git status --porcelain): E209's folder, MM1-v2's and
     MM1-v1's folders (the frozen forecasts and predictors the scorer pins), E208's folder (its registered kit: the runner, the reducer, the
     doubles, the tiles), rgm136's sources (E136), the reboot gate (fwgate and its records), the tiles (kinds), any sealed-forecast note for
     E209, the device-command checker v2 and its table, and E208's data directory whose checker the collection runs.
Prints "HISTORY OK: ..." (exit 0) or "HISTORY FAIL: ..." (exit 1). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REG_SUBTREE = "afaa6053e912724227097ff88383f8e440b3e052"   # fix-e209: tools/claims-v3/e209 in its local commit cb14eae3 (reg-e209's 95479783 with amendment A1)
E = "tools/claims-v3/e209"
RUN_PATHS = [E, "tools/matmul/mm1/v2", "tools/matmul/mm1/v1", "tools/claims-v3/e208", "tools/claims-v3/e136", "tools/claims-v3/fwgate",
             "tools/claims-v3/kinds", "tools/claims-v3/sealed-e209", "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json",
             "docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1"]
FALLBACK = {"argparse", "ast", "copy", "datetime", "fcntl", "gzip", "hashlib", "json", "math", "os", "pwd", "random", "re", "shutil",
            "signal", "socket", "statistics", "struct", "subprocess", "sys", "threading", "time", "zoneinfo", "collections", "functools",
            "itertools", "io", "pathlib", "string", "types", "typing", "warnings", "glob", "tempfile", "textwrap", "csv", "enum", "abc",
            "traceback", "bisect", "decimal", "runpy", "fractions", "operator", "heapq", "array", "base64", "binascii", "zlib"}


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
        rc, out = git("log", "--diff-filter=A", "--format=%H", "--", E + "/E209.md")
        reg = out.split()[-1] if out.split() else ""
    if not reg:
        print("HISTORY FAIL: no registration commit (no commit added tools/claims-v3/e209/E209.md)")
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
    rc, out = git("log", "--full-history", "--no-renames", "--name-status", "--format=COMMIT %H", f"{reg}..HEAD", "--", E)
    percommit, cur, ncommits = [], "", 0
    for ln in out.splitlines():
        if ln.startswith("COMMIT "):
            cur = ln.split()[1]
            ncommits += 1
        elif ln.strip() and not ln.startswith("A\t"):
            percommit.append(f"{cur[:12]} {ln.replace(chr(9), ' ')}")
    if rc != 0:
        bad.append(f"git log of the commits since the registration failed (rc {rc})")
    if percommit:
        bad.append("not an addition in a commit since the registration (commit by commit): " + "; ".join(percommit[:6]))
    rc, out = git("log", "--merges", "--format=%H", f"{reg}..HEAD", "--", E)
    if out.strip():
        bad.append("a merge commit since the registration touches " + E + ": " + ", ".join(x[:12] for x in out.split()[:3]))
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
        bad.append(f"{len(out.splitlines())} path(s) modified or untracked under E209's run paths ({out.splitlines()[0][:80]})")
    if bad:
        print("HISTORY FAIL: " + " | ".join(bad))
        return 1
    print(f"HISTORY OK: HEAD descends from the registration {reg[:12]} (subtree {REG_SUBTREE[:8]}); {len(added)} additions and nothing else "
          f"under {E} since it, and commit by commit ({ncommits} commit(s) touching it, each adding only; no merge); no shadowing addition "
          f"under tools/ ({'sys.stdlib_module_names' if hasattr(sys, 'stdlib_module_names') else 'the fixed list'}); E209's run paths clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
