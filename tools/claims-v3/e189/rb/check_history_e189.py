#!/usr/bin/env python3
"""E189's history check (Q167, the kit, Thu 12 Nov 2026, before any E189 datum; fixed Fri 13 Nov 2026, fix-e189b, and again the same
day, fix-fix189), E188's form (rb/check_history_e188.py): what the day runs and reads has not changed since it was pinned, only been
added to.

    /usr/bin/python3 -I -B tools/claims-v3/e189/rb/check_history_e189.py tree [--base 46a16bd0]
    /usr/bin/python3 -I -B tools/claims-v3/e189/rb/check_history_e189.py names      (the shadow names, where they came from, the folders)

From the lab clone's top, it reads git only (no network, no write):
  1. on E189's paths (PATHS below: the registration and the kit, the two programs, the ledger v2, the counter, Q166's three data folders,
     the catalogue, E59's records and the load model's scores the scorer's self-test reads, E128's guard, the device-command checker and
     its table, k6's and v3.1's runbook files): no commit since the base (Q166's programs, 46a16bd0) changed or removed a file: additions
     only (`git diff --name-status --no-renames <base> HEAD`);
  2. since E189's registration commit (found by its content: the commit that added tools/claims-v3/e189/E189.md, whose e189 subtree reads
     993e549a..., the registration as re-made on Fri 13 Nov 2026 before any datum) nothing under tools/claims-v3/e189/ changed or went:
     additions only; and since the kit's commit (the one that added tools/claims-v3/e189/KIT.md) the same, when it exists;
  3. nothing untracked anywhere under those paths (git status --untracked-files=all);
  4. NO ADDED OR UNCOMMITTED FILE SHADOWS A MODULE the day's Python can import, in a folder the day's scripts put ahead of the standard
     library on sys.path (SYSPATH_DIRS below, each with the script that puts it there): a module file (.py, .pyc, or an extension module,
     .so or .pyd, any tag) or a regular package (<name>/__init__.*) whose name is a standard-library module's, or one of the kit's, the
     ledger's, the counter's or numpy's (MODULES). The candidates are read from those folders themselves (fixed Fri 13 Nov 2026,
     fix-fix189, verify-fix189's finding 1 and nit 2: they were the additions on PATHS alone, which names two files of the reducer's
     folder and not the folder, so an added workloads/sparseparity/tools/json.py read HISTORY OK while energy_reduce.py imported it;
     and SYSPATH_DIRS lacked tools/claims-v3/ and v3.1/, and the lab clone's top, where step 1 runs its window script on stdin, found
     beside them): every file a second `git diff --name-status --no-renames <base> HEAD -- <SYSPATH_DIRS>` lists as added, and every
     file `git status --porcelain --untracked-files=all -- <SYSPATH_DIRS>` lists as untracked or staged as new. The standard-library names are DERIVED, not listed by hand (fixed Fri 13 Nov 2026, verify-e189's nit: a hand list
     missed struct, ast and copy, and an added tools/ledger/struct.py read HISTORY OK while forecast --check imported it): on Python 3.10
     or later, sys.stdlib_module_names (every standard-library module, the other platforms' among them) and sys.builtin_module_names; on
     Python 3.9 (the Intel's /usr/bin/python3 3.9.6, which has no sys.stdlib_module_names), every module file and regular package in this
     interpreter's own standard-library directories (sysconfig's stdlib and platstdlib, and their lib-dynload), with
     sys.builtin_module_names: every standard-library module this interpreter can import, so every one the forecast path imports.
Prints HISTORY OK: ... or HISTORY FAIL: ... (exit 0 or 16; 10 for a usage error). E189_HISTORY_NAMES=dirs takes 3.9's way on any
Python (the runbook's desk test, which cannot run 3.9 on every desk). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

REG_SUBTREE = "993e549a675e36edd049cd82e3e73c455bcf77a3"
PATHS = ["tools/claims-v3/e189/", "workloads/ledger/", "workloads/sparseparity/host/", "workloads/sparseparity/kernel/",
         "workloads/sparseparity/CMakeLists.txt", "workloads/sparseparity/sparseparity_args.h",
         "workloads/sparseparity/tools/energy_reduce.py", "workloads/sparseparity/tools/energy_stub.py", "tools/ledger/", "tools/counter/",
         "docs/reports/data/2026-11-12-q166-progs/", "docs/reports/data/2026-11-12-q166-ledger-v2/",
         "docs/reports/data/2026-11-12-q166-counter-sparseparity/", "docs/reports/data/2026-09-23-energy-manual/catalogue.json",
         "docs/reports/data/2026-10-26-load-model/scores.json", "workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/",
         "tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
         "tools/claims-v3/q141k-runbook/k6/", "tools/claims-v3/q141k-runbook/v3.1/"]
# The folders the day's Python on the desk puts ahead of the standard library on sys.path, and what puts each there ("" is the lab
# clone's top; its pathspec is "."). A script run by its path without -I has its own folder first; one on stdin or -c has "" (the
# current directory) first; sys.path.insert(0, ...) puts a folder first under any flags. fix-fix189 added the first, second and fifth.
SYSPATH_DIRS = [
    "",                                      # step 1, rb/s02_window_e189.sh: `"$RB_PY" -B - ...` from the top (time.strptime imports _strptime)
    "tools/claims-v3/",                      # preflight_e189.sh: `python3 tools/claims-v3/dmcmd_audit.py` (no -I)
    "tools/claims-v3/e189/",                 # step 11: collect_e189.py (-B, no -I); run_e189.py's own insert
    "tools/claims-v3/e189/rb/",              # kept from the first kit (its one Python script, this check, runs with -I)
    "tools/claims-v3/q141k-runbook/v3.1/",   # k6's rb_common.sh: `"$RB_PY" -B rb_run.py` and `nopath_q142s.py` (no -I), every box call
    "tools/ledger/",                         # forecast_e189.py and score_e189.py insert it
    "workloads/ledger/",                     # kept from the first kit (step 2 runs spp_never_ran.py from it, with -I)
    "workloads/sparseparity/tools/",         # collect_e189.py runs the reducer as [sys.executable, "-B", energy_reduce.py, ...] (no -I)
]
MODULES = {"numpy", "e189_common", "forecast_e189", "ledger_v2", "ledger_estimate", "energy_reduce", "energy_stub", "loads_ledger_v2",
           "card_compare_sparseparity", "count_kernel", "score_e189", "stub_e189", "plan_e189", "check_history_e189", "fake_card_e189",
           "run_e189", "collect_e189", "check_e189", "hostcheck_e189", "selftest_run_e189", "spp_never_ran", "ledger_desk"}
OWN = {"tools/claims-v3/e189/e189_common.py", "tools/claims-v3/e189/forecast_e189.py", "tools/claims-v3/e189/score_e189.py",
       "tools/claims-v3/e189/stub_e189.py", "tools/claims-v3/e189/plan_e189.py", "tools/claims-v3/e189/run_e189.py",
       "tools/claims-v3/e189/fake_card_e189.py", "tools/claims-v3/e189/collect_e189.py", "tools/claims-v3/e189/check_e189.py",
       "tools/claims-v3/e189/hostcheck_e189.py", "tools/claims-v3/e189/selftest_run_e189.py",
       "tools/claims-v3/e189/rb/check_history_e189.py"}         # the kit's and the registration's own modules, added where they belong
IMPORT_SUFFIXES = (".py", ".pyc", ".pyw", ".so", ".pyd")      # a file Python imports by the name before its first dot


def stdlib_names():
    """(the standard-library module names, where they came from): the module docstring's rule 4."""
    names = set(sys.builtin_module_names)
    if hasattr(sys, "stdlib_module_names") and os.environ.get("E189_HISTORY_NAMES") != "dirs":
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
    base = argv[argv.index("--base") + 1] if "--base" in argv else "46a16bd0"
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
    for what, path in (("the registration", "tools/claims-v3/e189/E189.md"), ("the kit", "tools/claims-v3/e189/KIT.md")):
        _, o = git("log", "--diff-filter=A", "--format=%H", "--", path)
        c = o.split()[-1] if o.split() else ""
        if not c:
            (bad if what == "the registration" else notes).append(f"{what}'s commit not found ({path} never added)")
            continue
        if what == "the registration":
            _, t = git("rev-parse", f"{c}:tools/claims-v3/e189")
            if t.strip() != REG_SUBTREE:
                bad.append(f"the registration commit {c[:12]}'s e189 subtree reads {t.strip()[:12]}, not {REG_SUBTREE[:12]}")
        _, o2 = git("diff", "--name-status", "--no-renames", c, "HEAD", "--", "tools/claims-v3/e189/")
        ch = [ln for ln in o2.splitlines() if ln.strip() and not ln.startswith("A\t")]
        if ch:
            bad.append(f"changed or removed since {what}'s commit {c[:12]}: " + ", ".join(ch[:8]))
        notes.append(f"{what} {c[:12]}")
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
    print(f"HISTORY OK: {len(added)} files added since {base[:8]} on E189's paths, none changed or removed; "
          f"{'; '.join(notes)}: nothing under tools/claims-v3/e189 changed since; nothing untracked; no shadowing addition or "
          f"uncommitted file in the {len(SYSPATH_DIRS)} folders the day's Python puts first ({len(mod_added)} module files added there "
          f"since {base[:8]}, {len(mod_new)} uncommitted) ({len(names)} names: {src}, and the day's own)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
