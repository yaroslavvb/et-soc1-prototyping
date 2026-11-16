#!/usr/bin/env python3
"""E200's history check (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): E197's (rb/check_history_e197.py in
tools/claims-v3/e197, unchanged beside it) for what E200's day runs and reads: it has not changed since it was pinned, only been added to.

    /usr/bin/python3 -I -B tools/claims-v3/e200/rb/check_history_e200.py tree [--base 72514ce5]
    /usr/bin/python3 -I -B tools/claims-v3/e200/rb/check_history_e200.py names      (the shadow names, where they came from, the folders)

From the lab clone's top, it reads git only (no network, no write):
  1. on E200's paths (PATHS below: E200's registration and kit, E197's registration and kit (E200 runs E197's registered session and
     builds E197's proposal), E194's common module (step 7's config line), the device-command checker v2 and its table, the lab's
     firmware gate, k6's and v3.1's runbook files): no commit since the base (GitHub main when E200 was registered, 72514ce5) changed or
     removed a file: additions only (`git diff --name-status --no-renames <base> HEAD`);
  2. since E200's registration commit (found by its content: the commit that added tools/claims-v3/e200/E200.md, whose e200 subtree reads
     c479c271...: the registration as fixed before the land) nothing under tools/claims-v3/e200/ changed or went: additions only; and since the kit's commit (the one that added
     tools/claims-v3/e200/KIT.md) the same, when it exists; and since E197's registration commit (its e197 subtree da6c3e89...) and
     E197's kit commit, nothing under tools/claims-v3/e197/ changed or went;
  3. nothing untracked anywhere under those paths (git status --untracked-files=all);
  4. NO ADDED OR UNCOMMITTED FILE SHADOWS A MODULE the day's Python can import, in a folder the day's scripts put ahead of the standard
     library on sys.path (SYSPATH_DIRS, each with the script that puts it there), E197's rule unchanged.
Prints HISTORY OK: ... or HISTORY FAIL: ... (exit 0 or 16; 10 for a usage error). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

REG_SUBTREE = "c479c271a261633b83a2bb690130c1419a34be2d"        # E200's registration's tools/claims-v3/e200 (fixed before the land: fix-e200)
E197_REG_SUBTREE = "da6c3e89d6d91473643d869d6041e842b4708b89"   # E197's registration's tools/claims-v3/e197 (E200.md 2)
PATHS = ["tools/claims-v3/e200/", "tools/claims-v3/e197/", "tools/claims-v3/e194/e194_common.py", "tools/claims-v3/dmcmd_audit_v2.py",
         "tools/claims-v3/dmcmd_table_v2.json", "tools/claims-v3/fwgate/", "tools/claims-v3/q141k-runbook/k6/",
         "tools/claims-v3/q141k-runbook/v3.1/"]
# The folders the day's Python puts ahead of the standard library on sys.path, and what puts each there ("" is the lab clone's top;
# its pathspec is "."). A script run by its path without -I has its own folder first; one on stdin has "" first. Every Python file of
# this kit runs with -I (no script folder on sys.path); the folders whose scripts run without it are the first, second, sixth and
# seventh; the kit's own folders are read too.
SYSPATH_DIRS = [
    "",                                      # step 1, rb/s02_window_e200.sh: `"$RB_PY" -B - ...` from the top (time.strptime imports _strptime)
    "tools/claims-v3/",                      # preflight_e200.sh: `python3 tools/claims-v3/dmcmd_audit_v2.py` (no -I), at the desk and on the box
    "tools/claims-v3/e200/",                 # the kit's checker, watch, harness, collector, stand-ins and reduction (each run with -I)
    "tools/claims-v3/e197/proposal/src/",    # the reference session's stopwatch.py (python3 -B, no -I: its folder first on sys.path) and
                                             # E197's reducer (loaded by reduce_e200.py); make_images.py and check_elf.py at the build (-I)
    "tools/claims-v3/e197/lab/",             # E197's lab runner, from which E200's runner (run from the sitting's ref/ copy, python3 -B,
                                             # no -I) is made
    "tools/claims-v3/e200/rb/",              # this check (-I)
    "tools/claims-v3/fwgate/",               # fwgate.py (steps 4, 7 and 9; run with python3 -I -B)
    "tools/claims-v3/e194/",                 # e194_common.py --config-line (step 7 and the wrapper's end read, -I)
    "tools/claims-v3/q141k-runbook/v3.1/",   # k6's rb_common.sh: `"$RB_PY" -B rb_run.py` and `nopath_q142s.py` (no -I), every box call
    "tools/claims-v3/e200/desk/",            # the registration's desk checks and the kit's desk tests (-I)
]
MODULES = {"reduce_regfile", "run_trains", "stopwatch", "make_images", "check_elf", "check_e200", "collect_e200", "harness_e200",
           "watch_e200", "fake_card_e200", "reduce_e200", "compare_e200", "check_history_e200", "realpath_e200", "realbytes_e200",
           "rb_run", "nopath_q142s", "dmcmd_audit_v2", "fwgate", "e194_common", "checks_e200", "synth_session_e200", "synth_e200",
           "clock_window_e200", "climb_e200", "peaks_e200", "refs_e200"}
E = "tools/claims-v3/e200/"
E7 = "tools/claims-v3/e197/"
OWN = {E + "check_e200.py", E + "collect_e200.py", E + "harness_e200.py", E + "watch_e200.py", E + "fake_card_e200.py",
       E + "reduce_e200.py", E + "compare_e200.py", E + "desk/realpath_e200.py", E + "desk/realbytes_e200.py", E + "desk/checks_e200.py",
       E + "desk/synth_session_e200.py", E + "desk/synth_e200.py", E + "desk/clock_window_e200.py", E + "desk/climb_e200.py",
       E + "desk/peaks_e200.py", E + "desk/refs_e200.py", E + "rb/check_history_e200.py",
       E7 + "proposal/src/run_trains.py", E7 + "proposal/src/reduce_regfile.py", E7 + "proposal/src/stopwatch.py",
       E7 + "proposal/src/make_images.py", E7 + "proposal/src/check_elf.py", E7 + "lab/run_trains.py",
       "tools/claims-v3/fwgate/fwgate.py", "tools/claims-v3/e194/e194_common.py", "tools/claims-v3/dmcmd_audit_v2.py"}
IMPORT_SUFFIXES = (".py", ".pyc", ".pyw", ".so", ".pyd")


def stdlib_names():
    names = set(sys.builtin_module_names)
    if hasattr(sys, "stdlib_module_names") and os.environ.get("E200_HISTORY_NAMES") != "dirs":
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
    base = argv[argv.index("--base") + 1] if "--base" in argv else "72514ce5"
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
    for what, path, folder, want in (("E197's registration", E7 + "E197.md", E7, E197_REG_SUBTREE), ("E197's kit", E7 + "KIT.md", E7, None),
                                      ("the registration", E + "E200.md", E, REG_SUBTREE), ("the kit", E + "KIT.md", E, None)):
        _, o = git("log", "--diff-filter=A", "--format=%H", "--", path)
        c = o.split()[-1] if o.split() else ""
        if not c:
            (notes if what == "the kit" else bad).append(f"{what}'s commit not found ({path} never added)")
            continue
        if want:
            _, t = git("rev-parse", f"{c}:{folder.rstrip('/')}")
            if t.strip() != want:
                bad.append(f"{what} commit {c[:12]}'s {folder.rstrip('/').split('/')[-1]} subtree reads {t.strip()[:12]}, not {want[:12]}")
        _, o2 = git("diff", "--name-status", "--no-renames", c, "HEAD", "--", folder)
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
    print(f"HISTORY OK: {len(added)} files added since {base[:8]} on E200's paths, none changed or removed; {'; '.join(notes)}: "
          f"nothing under tools/claims-v3/e200 or tools/claims-v3/e197 changed since; nothing untracked; no shadowing addition or "
          f"uncommitted file in the "
          f"{len(SYSPATH_DIRS)} folders the day's Python puts first ({len(mod_added)} module files added there since {base[:8]}, "
          f"{len(mod_new)} uncommitted) ({len(names)} names: {src}, and the day's own)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
