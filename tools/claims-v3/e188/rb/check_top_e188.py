#!/usr/bin/env python3
"""E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md section 14; written by the lane fix-port188 on verify-port188's finding 1,
Sun 15 Nov 2026, before any E188 datum): THE LAB'S TOP, the one folder that E188's day's desk Python puts ahead of the standard library
and that the history check (rb/check_history_e188.py) does not read at all, and E183's rb/ folder, the one such folder note 2 adds to the
day (step 11 v2 runs E183's nopath_spell_e183.py there with -B, so the folder comes first), where the history check reads committed
additions but no untracked file.

    /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_top_e188.py        # TOP OK or TOP REFUSED; exit 0 or 16 (10: usage)

Run from the lab's top: step 2 v3 runs it there before any box step, step 11 v2 before any scoring, and the card lane's brief (its dated
note 2) reads it right before step 1. Why the top: four of the day's desk Python processes run with the lab's top (the current
directory) first on sys.path, so a module file there named as a module they import is imported in its place:
  - step 1's window script (rb/s02_window_e188.sh: `"$RB_PY" -B -` on stdin; time.strptime imports _strptime);
  - the collector's two scripts on stdin (collect_e188.sh, in step 11: reduce_footing's and ccsessions_e188's imports, after the folder
    each puts first);
  - step 11's reading of a failed pairing (`python3 -B -c 'import json, sys'`; step 11 v2 gives it -I, so from note 2 on it is three).
verify-port188 showed a _strptime.py and a json.py added at the top pass the history check (HISTORY OK) and run there. Every other folder
the day's desk Python puts first is one the history check reads for committed additions (fix-port188's coverage reading, the kit's
note 2, section 14); untracked files beside the named files of the non-core folders it does not read (the kit's note 2, section 10, item 9): of those
folders this check reads E183's rb/, because note 2's step 11 v2 brings it into the day.

It reads each folder AS IT IS ON DISK, committed or not, ignored or not (Python reads the disk), and refuses (16) when one holds:
  1. a module file (.py, .pyw, .so, .pyd, .dylib; its name is the part before the first dot) or a regular package (a folder holding an
     __init__ file with one of those suffixes or .pyc) whose name is one the system python finds outside the lab clone: a built-in
     module, or one PathFinder finds on this interpreter's sys.path outside the lab clone, the user site among them (the history
     check's rule 3, the same test);
  2. byte-code Python would import by a module's name: a sourceless .pyc or .pyo file in the folder itself (and, at the top only, any
     __pycache__ folder: no source lives there, so none belongs there);
  3. a .pth file (rule 3 refuses one too).
Python's own modules only; it lists the two folders and reads this interpreter's paths, writes nothing and imports nothing from the tree.
SPDX-License-Identifier: Apache-2.0
"""
import importlib.machinery
import os
import sys

MOD_SUFFIXES = (".py", ".pyw", ".so", ".pyd", ".dylib")
BYTE_SUFFIXES = (".pyc", ".pyo")
FOLDERS = [("", "the lab's top", True),                                       # (folder from the top, its name, __pycache__ refused)
           ("tools/claims-v3/e183/rb", "tools/claims-v3/e183/rb/", False)]     # step 11 v2: nopath_spell_e183.py, by path, -B only


def outside(path, real_top):
    return not (os.path.realpath(path) + os.sep).startswith(real_top + os.sep)


def system_search(top):
    """this interpreter's module folders outside the lab clone, the user site among them (rule 3's search)"""
    real = os.path.realpath(top)
    search = [p for p in sys.path if p and outside(p, real)]
    try:
        import site
        us = site.getusersitepackages()
        if us and os.path.isdir(us) and us not in search and outside(us, real):
            search.append(us)
    except Exception:
        pass
    return search


def system_finds(name, search):
    if not name.isidentifier():
        return False
    if name in sys.builtin_module_names:
        return True
    try:
        return importlib.machinery.PathFinder.find_spec(name, search) is not None
    except (ImportError, ValueError):
        return False


def read_folder(top, rel, label, no_pycache, search):
    """(entries, module files and packages, problems) for one folder, as on disk"""
    d = os.path.join(top, rel) if rel else top
    if not os.path.isdir(d):
        return 0, [], [f"{label} is not a folder here"]
    entries = sorted(os.listdir(d))
    probs, mods = [], []
    for n in entries:
        p = os.path.join(d, n)
        where = f"{rel}/{n}" if rel else n
        if n == "__pycache__":
            if no_pycache:
                probs.append(f"{where}/ (byte-code at the top)")
            continue
        if os.path.isdir(p):
            if any(os.path.isfile(os.path.join(p, "__init__" + s)) for s in MOD_SUFFIXES + BYTE_SUFFIXES):
                mods.append(n + "/")
                if system_finds(n, search):
                    probs.append(f"{where}/ (a package named as the module '{n}' the system python finds)")
            continue
        if n.endswith(BYTE_SUFFIXES):
            probs.append(f"{where} (byte-code that imports as '{n.split('.', 1)[0]}')")
            continue
        if n.endswith(".pth"):
            probs.append(f"{where} (a .pth file)")
            continue
        if n.endswith(MOD_SUFFIXES):
            mods.append(n)
            name = n.split(".", 1)[0]
            if system_finds(name, search):
                probs.append(f"{where} (shadows the module '{name}' the system python finds)")
    return len(entries), mods, probs


def main(argv):
    if argv:
        print(__doc__)
        return 10
    top = os.getcwd()
    if not os.path.isfile(os.path.join(top, "tools", "claims-v3", "e188", "E188.md")):
        print("run from the lab's top (no tools/claims-v3/e188/E188.md here)")
        return 10
    search = system_search(top)
    parts, probs = [], []
    for rel, label, no_pycache in FOLDERS:
        n, mods, pr = read_folder(top, rel, label, no_pycache, search)
        probs += pr
        parts.append(f"{label}: {n} entries, {len(mods)} module files or packages"
                     f"{' (' + ', '.join(mods[:6]) + ')' if mods else ''}")
    where = (f"the names {sys.executable} {sys.version.split()[0]} finds: its built-in modules and {len(search)} folders outside the "
             f"lab clone")
    if probs:
        print("TOP REFUSED: " + "; ".join(probs[:8]) + (" ..." if len(probs) > 8 else "") + f" ({'; '.join(parts)}; {where})")
        return 16
    print(f"TOP OK: {'; '.join(parts)}; none named as a module the system python finds; no byte-code a module's name imports, no .pth "
          f"file ({where})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
