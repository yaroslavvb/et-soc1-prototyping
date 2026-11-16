"""E194's history check (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): E191's
(tools/claims-v3/e191/rb/check_history_e191.py, unchanged beside it; E189's form) with E194's paths: what the day runs and reads has not
changed since it was pinned, only been added to.

    /usr/bin/python3 -I -B tools/claims-v3/e194/rb/check_history_e194.py tree [--base 46a16bd0]
    /usr/bin/python3 -I -B tools/claims-v3/e194/rb/check_history_e194.py names      (the shadow names, where they came from, the folders)

From the lab clone's top, it reads git only (no network, no write):
  1. on E194's paths (PATHS below: E194's registration and kit; E191's and E189's registrations and kits, whose frozen forecasts E194's
     REPORTED readings read and whose host check, its frozen lines and its plan E194's build runs unchanged; the two programs; the ledger v2
     and the counter E194's forecast and scorer import; Q166's three data folders, the catalogue, E59's records and the load model's scores
     the scorer's self-test reads; E136's relation (a REPORTED reading); the committed records the kit's desk tests read (E190's data, the
     climb and the identity forms on this card; E189's and E191's data, the hosts' real stdout bytes the parser is tested on); the
     device-command checker and its table; k6's and v3.1's runbook files): no commit since the base (Q166's programs, 46a16bd0) changed or
     removed a file: additions only;
  2. since E194's registration commit (found by its content: the commit that added tools/claims-v3/e194/E194.md) nothing under
     tools/claims-v3/e194/ changed or went: additions only; the same since the kit's commit (the one that added tools/claims-v3/e194/KIT.md),
     when it exists; and since E191's registration (300d76e4, its subtree 766e2463...), note 1 and kit, and E189's registration (c86940c1,
     993e549a...) and kit, nothing under tools/claims-v3/e191/ or e189/ changed or went;
  3. nothing untracked anywhere under those paths (git status --untracked-files=all);
  4. NO ADDED OR UNCOMMITTED FILE SHADOWS A MODULE the day's Python can import, in a folder the day's scripts put ahead of the standard
     library on sys.path (SYSPATH_DIRS below), E189's rule 4 unchanged, with E194's folders and module names added.
Prints HISTORY OK: ... or HISTORY FAIL: ... (exit 0 or 16; 10 for a usage error). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

REG_SUBTREE = "766e24631138fdac09c3dd247d504b138c4a2ded"          # E191's registration (300d76e4)
E189_REG_SUBTREE = "993e549a675e36edd049cd82e3e73c455bcf77a3"     # E189's registration as re-made before any datum (c86940c1)
PATHS = ["tools/claims-v3/e194/", "tools/claims-v3/e191/", "tools/claims-v3/e189/", "workloads/ledger/", "workloads/sparseparity/host/", "workloads/sparseparity/kernel/",
         "workloads/sparseparity/CMakeLists.txt", "workloads/sparseparity/sparseparity_args.h", "workloads/sparseparity/cpu/sp.h",
         "workloads/sparseparity/tools/energy_reduce.py", "workloads/sparseparity/tools/energy_stub.py", "tools/ledger/", "tools/counter/",
         "docs/reports/data/2026-11-12-q166-progs/", "docs/reports/data/2026-11-12-q166-ledger-v2/",
         "docs/reports/data/2026-11-12-q166-counter-sparseparity/", "docs/reports/data/2026-09-23-energy-manual/catalogue.json",
         "docs/reports/data/2026-10-26-load-model/scores.json", "workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/",
         "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
         "tools/claims-v3/q141k-runbook/k6/", "tools/claims-v3/q141k-runbook/v3.1/", "tools/claims-v3/e136/predictions-e136.json",
         "docs/reports/data/2026-11-13-e190-large-gemm/", "docs/reports/data/2026-11-14-e189-blind-day-aifoundry3/",
         "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/"]
# The folders the day's Python on the desk or the box puts ahead of the standard library on sys.path, and what puts each there ("" is the
# lab clone's top; its pathspec is "."). A script run by its path without -I has its own folder first; one on stdin or -c has "" first.
SYSPATH_DIRS = [
    "",                                      # step 1, rb/s02_window_e194.sh: `"$RB_PY" -B - ...` from the top (time.strptime imports _strptime)
    "tools/claims-v3/",                      # preflight_e194.sh: `python3 tools/claims-v3/dmcmd_audit.py` (no -I)
    "tools/claims-v3/e194/",                 # step 11: collect_e194.py (-B, no -I); run_e194.py's own insert; the doubles
    "tools/claims-v3/e194/rb/",              # this check and the runbook desk tests' Python
    "tools/claims-v3/e194/desk/",            # the real-path desk test, the dry audit, the parser and identity tests (-B)
    "tools/claims-v3/e189/",                 # build_e194.sh runs E189's hostcheck_e189.py with -B (no -I) on the box
    "tools/claims-v3/q141k-runbook/v3.1/",   # k6's rb_common.sh: `"$RB_PY" -B rb_run.py` and `nopath_q142s.py` (no -I), every box call
    "tools/ledger/",                         # forecast_e194.py and score_e194.py insert it
    "workloads/ledger/",                     # step 2 runs spp_never_ran.py from it (with -I)
    "workloads/sparseparity/tools/",         # collect_e194.py runs the reducer as [sys.executable, "-B", energy_reduce.py, ...] (no -I)
]
MODULES = {"e194_common", "e194_ident", "forecast_e194", "score_e194", "stub_e194", "plan_e194", "check_history_e194",
           "fake_card_e194", "run_e194", "collect_e194", "check_e194", "selftest_run_e194", "realpath_e194", "dryaudit_e194",
           "selftest_wait_e194", "parser_e194", "identity_e194", "drylisting_check_e194", "readme_check_e194", "climb_e190",
           "roundtrip_e194", "rederive_e194", "numpy", "e191_common", "e191_ident", "forecast_e191", "score_e191", "stub_e191", "plan_e191", "check_history_e191",
           "fake_card_e191", "run_e191", "collect_e191", "check_e191", "selftest_run_e191", "note1_checks_e191", "realpath_e191",
           "dryaudit_e191", "selftest_wait_e191", "e189_common", "forecast_e189", "ledger_v2", "ledger_estimate", "energy_reduce",
           "energy_stub", "loads_ledger_v2", "card_compare_sparseparity", "count_kernel", "score_e189", "stub_e189", "plan_e189",
           "check_history_e189", "fake_card_e189", "run_e189", "collect_e189", "check_e189", "hostcheck_e189", "selftest_run_e189",
           "spp_never_ran", "ledger_desk"}
OWN = {"tools/claims-v3/e194/" + f for f in ("e194_common.py", "e194_ident.py", "forecast_e194.py", "score_e194.py", "stub_e194.py",
                                             "plan_e194.py", "run_e194.py", "fake_card_e194.py", "collect_e194.py", "check_e194.py",
                                             "selftest_run_e194.py", "rb/check_history_e194.py", "rb/selftest_wait_e194.py",
                                             "rb/readme_check_e194.py", "desk/realpath_e194.py", "desk/dryaudit_e194.py",
                                             "desk/parser_e194.py", "desk/identity_e194.py", "desk/drylisting_check_e194.py",
                                             "desk/climb_e190.py", "desk/roundtrip_e194.py", "desk/rederive_e194.py")} | {
       "tools/claims-v3/e191/" + f for f in ("e191_common.py", "e191_ident.py", "forecast_e191.py", "score_e191.py", "stub_e191.py",
                                             "plan_e191.py", "run_e191.py", "fake_card_e191.py", "collect_e191.py", "check_e191.py",
                                             "selftest_run_e191.py", "note1_checks_e191.py", "rb/check_history_e191.py",
                                             "rb/selftest_wait_e191.py", "desk/realpath_e191.py", "desk/dryaudit_e191.py")} | {
       "tools/claims-v3/e189/" + f for f in ("e189_common.py", "forecast_e189.py", "score_e189.py", "stub_e189.py", "plan_e189.py",
                                             "run_e189.py", "fake_card_e189.py", "collect_e189.py", "check_e189.py", "hostcheck_e189.py",
                                             "selftest_run_e189.py", "rb/check_history_e189.py")}   # the kits' and registrations' own modules
IMPORT_SUFFIXES = (".py", ".pyc", ".pyw", ".so", ".pyd")      # a file Python imports by the name before its first dot


def stdlib_names():
    """(the standard-library module names, where they came from): the module docstring's rule 4."""
    names = set(sys.builtin_module_names)
    if hasattr(sys, "stdlib_module_names") and os.environ.get("E194_HISTORY_NAMES") != "dirs":
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
    for what, path, sub, folder in (("E194's registration", "tools/claims-v3/e194/E194.md", None, "tools/claims-v3/e194"),
                                    ("E194's kit", "tools/claims-v3/e194/KIT.md", None, "tools/claims-v3/e194"),
                                    ("E191's registration", "tools/claims-v3/e191/E191.md", REG_SUBTREE, "tools/claims-v3/e191"),
                                    ("E191's note 1", "tools/claims-v3/e191/E191.md.dated-note-1.md", None, "tools/claims-v3/e191"),
                                    ("E191's kit", "tools/claims-v3/e191/KIT.md", None, "tools/claims-v3/e191"),
                                    ("E189's registration", "tools/claims-v3/e189/E189.md", E189_REG_SUBTREE, "tools/claims-v3/e189"),
                                    ("E189's kit", "tools/claims-v3/e189/KIT.md", None, "tools/claims-v3/e189")):
        _, o = git("log", "--diff-filter=A", "--format=%H", "--", path)
        c = o.split()[-1] if o.split() else ""
        if not c:
            (notes if what == "E194's kit" else bad).append(f"{what}'s commit not found ({path} never added)")
            continue
        if sub:
            _, t = git("rev-parse", f"{c}:{folder}")
            if t.strip() != sub:
                bad.append(f"{what} commit {c[:12]}'s subtree reads {t.strip()[:12]}, not {sub[:12]}")
        _, o2 = git("diff", "--name-status", "--no-renames", c, "HEAD", "--", folder + "/")
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
    print(f"HISTORY OK: {len(added)} files added since {base[:8]} on E194's paths, none changed or removed; "
          f"{'; '.join(notes)}: nothing under tools/claims-v3/e194, e191 or e189 changed since; nothing untracked; no shadowing addition or "
          f"uncommitted file in the {len(SYSPATH_DIRS)} folders the day's Python puts first ({len(mod_added)} module files added there "
          f"since {base[:8]}, {len(mod_new)} uncommitted) ({len(names)} names: {src}, and the day's own)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
