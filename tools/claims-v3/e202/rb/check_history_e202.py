#!/usr/bin/env python3
"""E202's history check (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), E189's check_history_e189.py ported line for line
but its pins and paths: what the day runs and reads has not changed since it was pinned, only been added to.

    /usr/bin/python3 -I -B tools/claims-v3/e202/rb/check_history_e202.py tree [--base <commit>]
    /usr/bin/python3 -I -B tools/claims-v3/e202/rb/check_history_e202.py names      (the shadow names, where they came from, the folders)

From the lab clone's top, it reads git only (no network, no write):
  1. on E202's paths (PATHS below: the registration and the kit, the program and its records, the registration's inputs (the ledger v2,
     M10's held-out rows, the catalogue, the counter, the mesh map, sparse parity's cycle model, the kinds), the reducer and the stub, E128's
     guard, the device-command checker v2 and its table, k6's and v3.1's runbook files): no commit since the base changed or removed a
     file: additions only (`git diff --name-status --no-renames <base> HEAD`). The base is the PROGRAM COMMIT, found by its content (the
     commit that added workloads/mnistmlp/kernel/mnistmlp.c, whose workloads/mnistmlp subtree reads fb102551..., fix-mnist's land), unless
     --base names one;
  2. since E202's registration commit (found by its content: the commit that added tools/claims-v3/e202/E202.md, whose e202 subtree reads
     d95a19d9..., reg-e202's land) nothing under tools/claims-v3/e202/ changed or went: additions only; and since the kit's commit (the one
     that added tools/claims-v3/e202/KIT.md) the same, when it exists; since the program commit, nothing under workloads/mnistmlp/;
  3. nothing untracked anywhere under those paths (git status --untracked-files=all);
  4. NO ADDED OR UNCOMMITTED FILE SHADOWS A MODULE the day's Python can import, in a folder the day's scripts put ahead of the standard
     library on sys.path (SYSPATH_DIRS below, each with what puts it there): a module file or a regular package whose name is a
     standard-library module's (derived: sys.stdlib_module_names on Python 3.10 or later) or one of the kit's, the registration's, the
     ledger's, the counter's, the program's or numpy's (MODULES); the candidates read from those folders themselves (E189's fix-fix189).
Prints HISTORY OK: ... or HISTORY FAIL: ... (exit 0 or 16; 10 for a usage error). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

REG_SUBTREE = "d95a19d97256cce64cf0409a090ac51956bcc10e"
PROG_SUBTREE = "fb102551ccd95d615273372a42c7d64d141b0f00"
PATHS = ["tools/claims-v3/e202/", "workloads/mnistmlp/", "docs/reports/data/2026-11-16-q193-mnistmlp/", "tools/ledger/",
         "docs/reports/data/2026-11-12-q166-ledger-v2/", "docs/reports/data/2026-11-04-q142m-m10/",
         "docs/reports/data/2026-09-23-energy-manual/catalogue.json", "workloads/ledger/ledger_estimate.py", "tools/counter/",
         "workloads/nocroute/meshmap.py", "workloads/sparseparity/tools/cycle_model.py", "tools/claims-v3/kinds/",
         "workloads/sparseparity/tools/energy_reduce.py", "workloads/sparseparity/tools/energy_stub.py",
         "tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json",
         "tools/claims-v3/q141k-runbook/k6/", "tools/claims-v3/q141k-runbook/v3.1/"]
# The folders the day's Python on the desk puts ahead of the standard library on sys.path, and what puts each there ("" is the lab
# clone's top; its pathspec is "."). A script run by its path without -I has its own folder first; one on stdin or -c has "" (the
# current directory) first; sys.path.insert(0, ...) puts a folder first under any flags (E189's fix-fix189 added its first, second and fifth).
SYSPATH_DIRS = [
    "",                                      # step 1, rb/s02_window_e202.sh: `"$RB_PY" -I -B - ...` (kept: E189's rule)
    "tools/claims-v3/",                      # preflight_e202.sh: `python3 tools/claims-v3/dmcmd_audit_v2.py` (no -I)
    "tools/claims-v3/e202/",                 # session_e202.sh: `python3 -B tools/claims-v3/e202/run_e202.py` (no -I) on the box; its own
                                             # insert; step 11: collect_e202.py (-B, no -I); build_e202.sh's check and host check
    "tools/claims-v3/e202/desk/",            # the desk tests' stand-ins (-B)
    "tools/claims-v3/e202/rb/",              # this check (with -I)
    "tools/claims-v3/q141k-runbook/v3.1/",   # k6's rb_common.sh: `"$RB_PY" -B rb_run.py` and `nopath_q142s.py` (no -I), every box call
    "tools/ledger/",                         # the forecast's and the scorer's imports by path (their own imports)
    "workloads/sparseparity/tools/",         # collect_e202.py runs the reducer as [sys.executable, "-B", energy_reduce.py, ...] (no -I);
                                             # the dry pass's sampler double, energy_stub.py
]
MODULES = {"numpy", "e202_common", "run_e202", "fake_card_e202", "check_e202", "hostcheck_e202", "collect_e202", "selftest_run_e202",
           "standin_e202", "realpath_e202", "realbytes_e202", "plan_e202", "forecast_e202", "score_e202", "tiles_e202",
           "check_history_e202", "energy_reduce", "energy_stub", "ledger_v2", "freeze_ledger_v2", "ledger_estimate", "count_kernel",
           "meshmap", "cycle_model", "mnist_model", "make_kinds", "dmcmd_audit_v2", "rb_run", "nopath_q142s"}
OWN = {"tools/claims-v3/e202/" + f for f in ("e202_common.py", "run_e202.py", "fake_card_e202.py", "check_e202.py", "hostcheck_e202.py",
                                             "collect_e202.py", "selftest_run_e202.py", "plan_e202.py", "forecast_e202.py",
                                             "score_e202.py", "desk/standin_e202.py", "desk/realpath_e202.py", "desk/realbytes_e202.py",
                                             "desk/tiles_e202.py", "rb/check_history_e202.py")}   # the kit's and the registration's own
IMPORT_SUFFIXES = (".py", ".pyc", ".pyw", ".so", ".pyd")      # a file Python imports by the name before its first dot


def stdlib_names():
    """(the standard-library module names, where they came from): the module docstring's rule 4."""
    names = set(sys.builtin_module_names)
    if hasattr(sys, "stdlib_module_names"):
        return names | set(sys.stdlib_module_names), f"sys.stdlib_module_names (Python {sys.version.split()[0]})"
    import sysconfig
    # the frozen and built-in modules this interpreter has loaded (importlib's own two are frozen, in no directory)
    names |= {n.split(".")[0] for n, m in list(sys.modules.items())
              if getattr(getattr(m, "__spec__", None), "origin", None) in ("frozen", "built-in")}
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
    return names, (f"this interpreter's own standard-library directories, {len(seen)} of them (Python {sys.version.split()[0]}"
                   f"{': no sys.stdlib_module_names' if not hasattr(sys, 'stdlib_module_names') else ''})")


def shadow_name(path):
    """The module name an added file would be imported as from one of SYSPATH_DIRS, or None."""
    for d in SYSPATH_DIRS:
        if not path.startswith(d):
            continue
        parts = path[len(d):].split("/")
        if len(parts) == 1 and parts[0].endswith(IMPORT_SUFFIXES):
            return parts[0].split(".", 1)[0]
        if len(parts) == 2 and parts[1].split(".", 1)[0] == "__init__" and parts[1].endswith(IMPORT_SUFFIXES):
            return parts[0]
    return None


def git(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def syspath_candidates(base):
    """(added, uncommitted): the files in SYSPATH_DIRS added since the base, and those untracked or staged as new there (rule 4). Read
    with -z, so a name comes as git stores it, never quoted."""
    specs = [d or "." for d in SYSPATH_DIRS]
    _, out = git("diff", "--name-status", "--no-renames", "-z", base, "HEAD", "--", *specs)
    f = out.split("\0")
    added = {f[i + 1] for i in range(0, len(f) - 1, 2) if f[i] == "A"}
    _, st = git("status", "--porcelain", "-z", "--no-renames", "--untracked-files=all", "--", *specs)
    new = {e[3:] for e in st.split("\0") if len(e) > 3 and ("?" in e[:2] or "A" in e[:2])}
    return added, new


def main(argv):
    if argv and argv[0] == "names":
        names, src = stdlib_names()
        print(f"SHADOW NAMES: {len(names)} standard-library names from {src}; with the day's own {len(MODULES)}; "
              f"struct {'struct' in names}, ast {'ast' in names}, copy {'copy' in names}, gzip {'gzip' in names}, json {'json' in names}, "
              f"re {'re' in names}, subprocess {'subprocess' in names}, _strptime {'_strptime' in names}; read in {len(SYSPATH_DIRS)} "
              f"folders: " + ", ".join(d or "(the top)" for d in SYSPATH_DIRS))
        return 0
    if not argv or argv[0] != "tree":
        print(__doc__)
        return 10
    base = argv[argv.index("--base") + 1] if "--base" in argv else ""
    if not base:
        _, o = git("log", "--diff-filter=A", "--format=%H", "--", "workloads/mnistmlp/kernel/mnistmlp.c")
        base = o.split()[-1] if o.split() else ""
        if not base:
            print("HISTORY FAIL: the program commit was not found (workloads/mnistmlp/kernel/mnistmlp.c never added)")
            return 16
        _, t = git("rev-parse", f"{base}:workloads/mnistmlp")
        if t.strip() != PROG_SUBTREE:
            print(f"HISTORY FAIL: the program commit {base[:12]}'s workloads/mnistmlp subtree reads {t.strip()[:12]}, not {PROG_SUBTREE[:12]}")
            return 16
    bad, notes = [], []
    rc, _ = git("merge-base", "--is-ancestor", base, "HEAD")
    if rc != 0:
        print(f"HISTORY FAIL: the base {base} is not an ancestor of HEAD")
        return 16
    _, out = git("diff", "--name-status", "--no-renames", base, "HEAD", "--", *PATHS)
    rows = [ln.split("\t") for ln in out.splitlines() if ln.strip()]
    changed = [r for r in rows if r[0] != "A"]
    added = [r[1] for r in rows if r[0] == "A"]
    if changed:
        bad.append(f"changed or removed since {base[:8]}: " + ", ".join(f"{r[0]} {r[-1]}" for r in changed[:8]))
    for what, path in (("the registration", "tools/claims-v3/e202/E202.md"), ("the kit", "tools/claims-v3/e202/KIT.md")):
        _, o = git("log", "--diff-filter=A", "--format=%H", "--", path)
        c = o.split()[-1] if o.split() else ""
        if not c:
            (bad if what == "the registration" else notes).append(f"{what}'s commit not found ({path} never added)")
            continue
        if what == "the registration":
            _, t = git("rev-parse", f"{c}:tools/claims-v3/e202")
            if t.strip() != REG_SUBTREE:
                bad.append(f"the registration commit {c[:12]}'s e202 subtree reads {t.strip()[:12]}, not {REG_SUBTREE[:12]}")
        _, o2 = git("diff", "--name-status", "--no-renames", c, "HEAD", "--", "tools/claims-v3/e202/")
        ch = [ln for ln in o2.splitlines() if ln.strip() and not ln.startswith("A\t")]
        if ch:
            bad.append(f"changed or removed since {what}'s commit {c[:12]}: " + ", ".join(ch[:8]))
        notes.append(f"{what} {c[:12]}")
    _, o3 = git("diff", "--name-status", "--no-renames", base, "HEAD", "--", "workloads/mnistmlp/")
    ch3 = [ln for ln in o3.splitlines() if ln.strip()]
    if ch3:
        bad.append(f"workloads/mnistmlp changed since the program commit {base[:12]}: " + ", ".join(ch3[:8]))
    _, st = git("status", "--porcelain", "--untracked-files=all", "--", *PATHS)
    if st.strip():
        bad.append("uncommitted or untracked: " + ", ".join(ln[3:] for ln in st.splitlines()[:8]))
    names, src = stdlib_names()
    names |= MODULES
    sp_added, sp_new = syspath_candidates(base)
    mod_added = sorted(p for p in sp_added | set(added) if shadow_name(p))      # the files an import could find, by their place
    mod_new = sorted(p for p in sp_new if shadow_name(p))
    sh = [p for p in mod_added if p not in OWN and shadow_name(p) in names]
    if sh:
        bad.append("a shadowing addition: " + ", ".join(f"{p} (as {shadow_name(p)})" for p in sh))
    shn = [p for p in mod_new if p not in OWN and shadow_name(p) in names]
    if shn:
        bad.append("a shadowing file not committed: " + ", ".join(f"{p} (as {shadow_name(p)})" for p in shn))
    if bad:
        print("HISTORY FAIL: " + "; ".join(bad))
        return 16
    print(f"HISTORY OK: {len(added)} files added since the program commit {base[:8]} on E202's paths, none changed or removed, "
          f"workloads/mnistmlp unchanged; {'; '.join(notes)}: nothing under tools/claims-v3/e202 changed since; nothing untracked; "
          f"no shadowing addition or "
          f"uncommitted file in the {len(SYSPATH_DIRS)} folders the day's Python puts first ({len(mod_added)} module files added there "
          f"since {base[:8]}, {len(mod_new)} uncommitted) ({len(names)} names: {src}, and the day's own)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
