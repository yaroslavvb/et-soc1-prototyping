#!/usr/bin/env python3
"""E193's history check (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum), E189's form (rb/check_history_e189.py, b42dc95c,
with its fixes of Fri 13 Nov 2026): what the day runs and reads has not changed since it was pinned, only been added to.

    /usr/bin/python3 -I -B tools/claims-v3/e193/rb/check_history_e193.py tree [--base 49a4152e]
    /usr/bin/python3 -I -B tools/claims-v3/e193/rb/check_history_e193.py names      (the shadow names, where they came from, the folders)

From the lab clone's top, it reads git only (no network, no write):
  1. on E193's paths (PATHS below: the registration and the kit, E128's guard, the device-command checker and its table, k6's and
     v3.1's runbook files, E183 note 5's desk-path gate): no commit since the base (GitHub main when E193 was registered, 49a4152e)
     changed or removed a file: additions only (`git diff --name-status --no-renames <base> HEAD`);
  2. since E193's registration commit (found by its content: the commit that added tools/claims-v3/e193/E193.md, whose e193 subtree reads
     03ae7f5a...) nothing under tools/claims-v3/e193/ changed or went: additions only; and since the kit's commit (the one that added
     tools/claims-v3/e193/KIT.md) the same, when it exists;
  3. nothing untracked anywhere under those paths (git status --untracked-files=all);
  4. NO ADDED OR UNCOMMITTED FILE SHADOWS A MODULE the day's Python can import, in a folder the day's scripts put ahead of the standard
     library on sys.path (SYSPATH_DIRS, each with the script that puts it there): a module file (.py, .pyc, .pyw, .so, .pyd) or a regular
     package (<name>/__init__.*) whose name is a standard-library module's or one of the day's own (MODULES). The candidates are read from
     those folders themselves: every file a second `git diff --name-status --no-renames <base> HEAD -- <SYSPATH_DIRS>` lists as added,
     and every file `git status --porcelain --untracked-files=all -- <SYSPATH_DIRS>` lists as untracked or staged as new. The
     standard-library names are derived: on Python 3.10 or later sys.stdlib_module_names and sys.builtin_module_names; on 3.9 this
     interpreter's own standard-library directories (E189's rule; E193_HISTORY_NAMES=dirs takes that way on any Python).
Prints HISTORY OK: ... or HISTORY FAIL: ... (exit 0 or 16; 10 for a usage error). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

REG_SUBTREE = "03ae7f5acae03784d228738755f4dd9ff725e947"
PATHS = ["tools/claims-v3/e193/", "tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit.py",
         "tools/claims-v3/dmcmd_table.json", "tools/claims-v3/q141k-runbook/k6/", "tools/claims-v3/q141k-runbook/v3.1/",
         "tools/claims-v3/e183/rb/nopath_desk_e183.sh", "tools/claims-v3/e183/rb/nopath_spell_e183.py"]
# The folders the day's Python puts ahead of the standard library on sys.path, and what puts each there ("" is the lab clone's top;
# its pathspec is "."). A script run by its path without -I has its own folder first; one on stdin has "" first. Every Python file of
# this kit runs with -I (no script folder on sys.path); the folders whose scripts run without it are the first, second, sixth and
# seventh; the kit's own folders are read too.
SYSPATH_DIRS = [
    "",                                      # step 1, rb/s02_window_e193.sh: `"$RB_PY" -B - ...` from the top (time.strptime imports _strptime)
    "tools/claims-v3/",                      # preflight_e193.sh: `python3 -B tools/claims-v3/dmcmd_audit.py` (no -I), at the desk and on the box
    "tools/claims-v3/e193/",                 # the kit's checker, harness, collector and stand-ins (each run with -I)
    "tools/claims-v3/e193/proposal/src/",    # the registered runner and reducer (run with -I; check_e193.py imports the reducer by its path)
    "tools/claims-v3/e193/rb/",              # this check (-I)
    "tools/claims-v3/q141k-runbook/v3.1/",   # k6's rb_common.sh: `"$RB_PY" -B rb_run.py` and `nopath_q142s.py` (no -I), every box call
    "tools/claims-v3/e183/rb/",              # E183 note 5's gate runs `"$RB_PY" -B nopath_spell_e183.py` (no -I) at the collection
    "tools/claims-v3/e193/desk/",            # the registration's desk checks (bodies_e193.py runs on the box at the build, with -I)
]
MODULES = {"numpy", "reduce_x04", "run_x04", "gen_blocks", "check_e193", "collect_e193", "harness_e193", "fake_card_e193",
           "bodies_e193", "compare_arms_e193", "synth_session_e193", "synth_compare_e193", "check_history_e193", "rb_run",
           "nopath_q142s", "nopath_spell_e183", "dmcmd_audit", "reduce_x04_registered"}
E = "tools/claims-v3/e193/"
OWN = {E + "check_e193.py", E + "collect_e193.py", E + "harness_e193.py", E + "fake_card_e193.py", E + "proposal/src/run_x04.py",
       E + "proposal/src/reduce_x04.py", E + "proposal/src/gen_blocks.py", E + "desk/bodies_e193.py", E + "desk/compare_arms_e193.py",
       E + "desk/synth_session_e193.py", E + "desk/synth_compare_e193.py", E + "rb/check_history_e193.py"}
IMPORT_SUFFIXES = (".py", ".pyc", ".pyw", ".so", ".pyd")


def stdlib_names():
    names = set(sys.builtin_module_names)
    if hasattr(sys, "stdlib_module_names") and os.environ.get("E193_HISTORY_NAMES") != "dirs":
        return names | set(sys.stdlib_module_names), f"sys.stdlib_module_names (Python {sys.version.split()[0]})"
    import sysconfig
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
    return names, f"this interpreter's own standard-library directories, {len(seen)} of them (Python {sys.version.split()[0]})"


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


def git(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def syspath_candidates(base):
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
        print(f"SHADOW NAMES: {len(names)} standard-library names from {src}; with the day's own {len(MODULES)}; json "
              f"{'json' in names}, re {'re' in names}, subprocess {'subprocess' in names}, _strptime {'_strptime' in names}; read in "
              f"{len(SYSPATH_DIRS)} folders: " + ", ".join(d or "(the top)" for d in SYSPATH_DIRS))
        return 0
    if not argv or argv[0] != "tree":
        print(__doc__)
        return 10
    base = argv[argv.index("--base") + 1] if "--base" in argv else "49a4152e"
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
    for what, path in (("the registration", E + "E193.md"), ("the kit", E + "KIT.md")):
        _, o = git("log", "--diff-filter=A", "--format=%H", "--", path)
        c = o.split()[-1] if o.split() else ""
        if not c:
            (bad if what == "the registration" else notes).append(f"{what}'s commit not found ({path} never added)")
            continue
        if what == "the registration":
            _, t = git("rev-parse", f"{c}:tools/claims-v3/e193")
            if t.strip() != REG_SUBTREE:
                bad.append(f"the registration commit {c[:12]}'s e193 subtree reads {t.strip()[:12]}, not {REG_SUBTREE[:12]}")
        _, o2 = git("diff", "--name-status", "--no-renames", c, "HEAD", "--", E)
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
    mod_added = sorted(p for p in sp_added | set(added) if shadow_name(p))
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
    print(f"HISTORY OK: {len(added)} files added since {base[:8]} on E193's paths, none changed or removed; {'; '.join(notes)}: "
          f"nothing under tools/claims-v3/e193 changed since; nothing untracked; no shadowing addition or uncommitted file in the "
          f"{len(SYSPATH_DIRS)} folders the day's Python puts first ({len(mod_added)} module files added there since {base[:8]}, "
          f"{len(mod_new)} uncommitted) ({len(names)} names: {src}, and the day's own)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
