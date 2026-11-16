#!/usr/bin/env python3
"""E198's history check (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum), E193's form (rb/check_history_e193.py, unchanged
beside it): what the day runs and reads has not changed since it was pinned, only been added to. E198 runs E193's registered files by
reference (its runner, host, kernel, reducer, checker and listings), E191's guard, identity module, ET_DEVICES reading and rest rule, so
those paths are E198's too. THE SEALED CARD-1 NOTE: tools/claims-v3/sealed-card1/ (a later dated note, CONTEXT 122) is on the list, so an
addition there is accepted and a change to a committed note is refused.

    /usr/bin/python3 -I -B tools/claims-v3/e198/rb/check_history_e198.py tree [--base f74c81e3]
    /usr/bin/python3 -I -B tools/claims-v3/e198/rb/check_history_e198.py names      (the shadow names, where they came from, the folders)

From the lab clone's top, it reads git only (no network, no write):
  1. on E198's paths (PATHS below: E198's registration and kit, E193's registered files and kit, E191's guard, identity module, ET_DEVICES
     reading and rest rule, the device-command checker and its table, k6's and v3.1's runbook files, E183 note 5's desk-path gate, the
     sealed card-1 notes): no commit since the base (GitHub main when E198 was registered, f74c81e3)
     changed or removed a file: additions only, read two ways: the net change (`git diff --name-status --no-renames <base> HEAD`) and
     EVERY COMMIT on its own (`git log --format= --name-status --no-renames --full-history --diff-merges=first-parent <base>..HEAD`),
     so a file added after the base and changed or removed by a later commit (a committed sealed note edited, an amendment rewritten)
     is refused although the net change lists it only as added (fix-e198, Q191, before any datum: verify-e198's finding 2);
  2. since E198's registration commit (found by its content: the commit that added tools/claims-v3/e198/E198.md, whose e198 subtree reads
     5434394b...) nothing under tools/claims-v3/e198/ changed or went: additions only, by the net change and by every commit on its own;
     and since the kit's commit (the one that added tools/claims-v3/e198/KIT.md) the same, when it exists;
  3. nothing untracked anywhere under those paths (git status --untracked-files=all);
  4. NO ADDED OR UNCOMMITTED FILE SHADOWS A MODULE the day's Python can import, in a folder the day's scripts put ahead of the standard
     library on sys.path (SYSPATH_DIRS, each with the script that puts it there): a module file (.py, .pyc, .pyw, .so, .pyd) or a regular
     package (<name>/__init__.*) whose name is a standard-library module's or one of the day's own (MODULES). The candidates are read from
     those folders themselves: every file a second `git diff --name-status --no-renames <base> HEAD -- <SYSPATH_DIRS>` lists as added,
     and every file `git status --porcelain --untracked-files=all -- <SYSPATH_DIRS>` lists as untracked or staged as new. The
     standard-library names are derived: on Python 3.10 or later sys.stdlib_module_names and sys.builtin_module_names; on 3.9 this
     interpreter's own standard-library directories (E189's rule; E198_HISTORY_NAMES=dirs takes that way on any Python).
Prints HISTORY OK: ... or HISTORY FAIL: ... (exit 0 or 16; 10 for a usage error). SPDX-License-Identifier: Apache-2.0
"""
import os
import subprocess
import sys

REG_SUBTREE = "5434394b27bb98ae433b05df3e30f372461c518b"
PATHS = ["tools/claims-v3/e198/", "tools/claims-v3/e193/", "tools/claims-v3/e191/ettelem_guard_e191.sh", "tools/claims-v3/e191/e191_ident.py",
         "tools/claims-v3/e191/etdevices_e191.sh", "tools/claims-v3/e191/rb/rest_rule_e191.sh", "tools/claims-v3/dmcmd_audit.py",
         "tools/claims-v3/dmcmd_table.json", "tools/claims-v3/q141k-runbook/k6/", "tools/claims-v3/q141k-runbook/v3.1/",
         "tools/claims-v3/e183/rb/nopath_desk_e183.sh", "tools/claims-v3/e183/rb/nopath_spell_e183.py", "tools/claims-v3/sealed-card1/"]
# The folders the day's Python puts ahead of the standard library on sys.path, and what puts each there ("" is the lab clone's top;
# its pathspec is "."). A script run by its path without -I has its own folder first; one on stdin has "" first. Every Python file of
# this kit runs with -I (no script folder on sys.path); the folders whose scripts run without it are the first, second, sixth and
# seventh; the kit's own folders are read too.
SYSPATH_DIRS = [
    "",                                      # step 1, rb/s02_window_e198.sh: `"$RB_PY" -I -B - ...` from the top
    "tools/claims-v3/",                      # preflight_e198.sh: `python3 -B tools/claims-v3/dmcmd_audit.py` (no -I), at the desk and on the box
    "tools/claims-v3/e198/",                 # the kit's own Python (each run with -I)
    "tools/claims-v3/e198/rb/",              # this check (-I)
    "tools/claims-v3/e198/desk/",            # the desk tests (-I)
    "tools/claims-v3/e193/",                 # E193's checker and stand-ins (-I; imported by path)
    "tools/claims-v3/e193/proposal/src/",    # the registered runner and reducer (run with -I)
    "tools/claims-v3/e193/desk/",            # E193's bodies check (run on the box at the build, with -I)
    "tools/claims-v3/e191/",                 # E191's identity module (imported by path)
    "tools/claims-v3/q141k-runbook/v3.1/",   # k6's rb_common.sh: `"$RB_PY" -B rb_run.py` and `nopath_q142s.py` (no -I), every box call
    "tools/claims-v3/e183/rb/",              # E183 note 5's gate runs `"$RB_PY" -B nopath_spell_e183.py` (no -I) at the collection
]
MODULES = {"numpy", "reduce_x04", "run_x04", "gen_blocks", "check_e193", "fake_card_e193", "bodies_e193", "e191_ident", "rb_run",
           "nopath_q142s", "nopath_spell_e183", "dmcmd_audit", "check_e198", "collect_e198", "harness_e198", "fake_card_e198",
           "dropruntime_e198", "ident_e198", "warden_e198", "score_e198", "forecast_e198", "check_history_e198",
           "desktest_realpath_e198", "realbytes_e198", "scale_e198", "peaks_e198"}
E = "tools/claims-v3/e198/"
OWN = {E + x for x in ("check_e198.py", "collect_e198.py", "harness_e198.py", "fake_card_e198.py", "dropruntime_e198.py", "ident_e198.py",
                       "warden_e198.py", "score_e198.py", "forecast_e198.py", "rb/check_history_e198.py", "desk/desktest_realpath_e198.py",
                       "desk/realbytes_e198.py", "desk/scale_e198.py", "desk/peaks_e198.py")}
IMPORT_SUFFIXES = (".py", ".pyc", ".pyw", ".so", ".pyd")


def stdlib_names():
    names = set(sys.builtin_module_names)
    if hasattr(sys, "stdlib_module_names") and os.environ.get("E198_HISTORY_NAMES") != "dirs":
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


def per_commit_rows(rev_range, paths):
    """(commit, status, path) for every commit's own change on paths in rev_range (a merge diffed against its first parent), or
    None if git could not read it; a status other than A is a change or a removal (fix-e198: verify-e198's finding 2)"""
    rc, out = git("log", "-z", "--format=C %H", "--name-status", "--no-renames", "--full-history", "--diff-merges=first-parent",
                  rev_range, "--", *paths)
    if rc != 0:
        return None
    rows, commit, toks, i = [], "", out.split("\0"), 0
    while i < len(toks):
        t = toks[i].lstrip("\n")
        if t.startswith("C ") and len(t) in (42, 66) and all(ch in "0123456789abcdef" for ch in t[2:]):
            commit = t[2:]
        elif t:
            rows.append((commit, t, toks[i + 1] if i + 1 < len(toks) else ""))
            i += 1
        i += 1
    return rows


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
    base = argv[argv.index("--base") + 1] if "--base" in argv else "f74c81e3"
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
    pc = per_commit_rows(f"{base}..HEAD", PATHS)
    if pc is None:
        bad.append(f"the commits since {base[:8]} could not be read one by one")
        pc = []
    pch = [r for r in pc if r[1] != "A"]
    if pch:
        bad.append(f"changed or removed by a commit since {base[:8]}: " + ", ".join(f"{r[1]} {r[2]} ({r[0][:12]})" for r in pch[:8]))
    for what, path in (("the registration", E + "E198.md"), ("the kit", E + "KIT.md")):
        _, o = git("log", "--diff-filter=A", "--format=%H", "--", path)
        c = o.split()[-1] if o.split() else ""
        if not c:
            (bad if what == "the registration" else notes).append(f"{what}'s commit not found ({path} never added)")
            continue
        if what == "the registration":
            _, t = git("rev-parse", f"{c}:tools/claims-v3/e198")
            if t.strip() != REG_SUBTREE:
                bad.append(f"the registration commit {c[:12]}'s e198 subtree reads {t.strip()[:12]}, not {REG_SUBTREE[:12]}")
        _, o2 = git("diff", "--name-status", "--no-renames", c, "HEAD", "--", E)
        ch = [ln for ln in o2.splitlines() if ln.strip() and not ln.startswith("A\t")]
        if ch:
            bad.append(f"changed or removed since {what}'s commit {c[:12]}: " + ", ".join(ch[:8]))
        pc2 = per_commit_rows(f"{c}..HEAD", [E])
        ch2 = [r for r in (pc2 if pc2 is not None else [("", "unread", E)]) if r[1] != "A"]
        if ch2:
            bad.append(f"changed or removed by a commit since {what}'s commit {c[:12]}: "
                       + ", ".join(f"{r[1]} {r[2]} ({r[0][:12]})" for r in ch2[:8]))
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
    print(f"HISTORY OK: {len(added)} files added since {base[:8]} on E198's paths, none changed or removed (by the net change, and by "
          f"each of the {len({r[0] for r in pc})} commits that touch them, read one by one: {len(pc)} rows, all additions); "
          f"{'; '.join(notes)}: "
          f"nothing under tools/claims-v3/e198 changed since; nothing untracked; no shadowing addition or uncommitted file in the "
          f"{len(SYSPATH_DIRS)} folders the day's Python puts first ({len(mod_added)} module files added there since {base[:8]}, "
          f"{len(mod_new)} uncommitted) ({len(names)} names: {src}, and the day's own)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
