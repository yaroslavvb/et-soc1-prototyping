#!/usr/bin/env python3
"""E169 (Q141(s)): every repo file score_e169.py's score path loads, found by running that path (score_e169.load(), reduce_e169.reduce(),
score_e169.score()) on a session under an import and file-open trace, against frozen-sha256-e169.txt, which must cover all of them (the
check Q140(q)'s C11 asked of E168's scorer). Files of the session itself are data, not the score path, and are left out. Desk only: it
opens no device and writes nothing.

    nice -n 10 python3 -B tools/claims-v3/e169/trace_scorer_e169.py <RUNDIR> > tools/claims-v3/e169/trace-scorer-e169.txt
SPDX-License-Identifier: Apache-2.0
"""
import contextlib
import io
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OPENED = set()


def hook(ev, args):
    if ev == "open" and args and isinstance(args[0], str):
        p = os.path.realpath(args[0])
        if p.startswith(LAB + os.sep) and os.path.isfile(p):
            OPENED.add(p)


def main():
    rd = os.path.realpath(sys.argv[1])
    sys.addaudithook(hook)
    sys.path.insert(0, HERE)
    import score_e169 as SC  # noqa: E402
    import reduce_e169 as RE  # noqa: E402
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rule, pred, kit = SC.load()
        red = RE.reduce([rd], kit)
        res = SC.score(red, rule, pred, kit)
        SC.report(res, red)
    me = os.path.realpath(os.path.abspath(__file__))
    mods = {os.path.realpath(m.__file__) for m in list(sys.modules.values())
            if getattr(m, "__file__", None) and os.path.realpath(m.__file__).startswith(LAB + os.sep)} - {me}
    # bytecode caches (__pycache__) are derived from the sources beside them and are not inputs; the session's files are data
    path = sorted(p for p in (mods | OPENED) if not p.startswith(rd + os.sep) and "__pycache__" not in p.split(os.sep))
    side = {}
    for ln in open(os.path.join(HERE, "frozen-sha256-e169.txt")):
        if ln.strip():
            side[os.path.realpath(os.path.join(HERE, ln.split(None, 1)[1].strip()))] = ln.split(None, 1)[0]
    print(f"the score path, run on a session of {red['n_runs']} runs, loads {len(path)} repo files (the session's own files left out):")
    for p in path:
        print(f"  {os.path.relpath(p, HERE):78s} {'sidecar' if p in side else 'NOT IN THE SIDECAR'}")
    missing = [os.path.relpath(p, HERE) for p in path if p not in side]
    print(f"frozen-sha256-e169.txt holds {len(side)} files; it covers {len(path) - len(missing)} of the score path's {len(path)}")
    print("SIDECAR COVERS THE SCORE PATH" if not missing else f"SIDECAR MISSES {missing}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
