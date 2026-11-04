#!/usr/bin/env python3
"""Q140(q), after verification (C11): every repo file score_e168.py's score path loads, found by running its self-test (which goes
through score()) under an import and file-open trace, against what `score_e168.py check` hashes (frozen-sha256-e168.json) and what
frozen-sha256-e168-scorer.txt hashes. Desk only; it opens no device and writes nothing in the tree.

    /usr/bin/python3 -B trace_scorer_e168.py > trace-scorer-e168.txt
SPDX-License-Identifier: Apache-2.0
"""
import contextlib
import io
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OPENED = set()


def hook(ev, args):
    if ev == "open" and args and isinstance(args[0], str):
        p = os.path.realpath(args[0])
        if p.startswith(LAB + os.sep) and os.path.isfile(p):
            OPENED.add(p)


def rel(p):
    return os.path.relpath(p, HERE)


def main():
    sys.addaudithook(hook)
    sys.path.insert(0, HERE)
    import score_e168 as S  # noqa: E402
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        S.selftest()
    last = buf.getvalue().strip().splitlines()[-1]
    # the --anchors path imports predict_m9_a2 (score() does it only when anchors are given); import it the same way
    sys.path.insert(0, os.path.join(S.LAB, "docs/reports/data/2026-11-04-q140l-a2-session-terms"))
    import predict_m9_a2  # noqa: E402,F401
    me = os.path.realpath(os.path.abspath(__file__))
    mods = {os.path.realpath(m.__file__) for m in list(sys.modules.values())
            if getattr(m, "__file__", None) and os.path.realpath(m.__file__).startswith(LAB + os.sep)} - {me}
    e159 = os.path.realpath(os.path.join(LAB, "docs/reports/data/2026-11-03-e159-gemm-sustained"))
    selftest_only = {p for p in OPENED if p.startswith(e159 + os.sep)} | {
        os.path.realpath(os.path.join(LAB, "docs/reports/data/2026-11-03-q139q-gemm-g3/predictions-e159.json")),
        os.path.realpath(os.path.join(HERE, "rows-g4.json"))}
    score_path = sorted((mods | OPENED) - selftest_only)
    checked = {os.path.realpath(os.path.join(HERE, p)) for p in json.load(open(os.path.join(HERE, "frozen-sha256-e168.json")))}
    sidecar = {os.path.realpath(os.path.join(HERE, ln.split(None, 1)[1].strip()))
               for ln in open(os.path.join(HERE, "frozen-sha256-e168-scorer.txt")) if ln.strip()}
    print(f"self-test: {last}")
    print(f"the score path, --anchors included, loads {len(score_path)} repo files (the self-test's own inputs, E159's session, "
          f"predictions-e159.json and rows-g4.json, left out; `check` also reads frozen-sha256-e168.json):")
    for p in score_path:
        print(f"  {rel(p):70s} {'check' if p in checked else '     '}  {'sidecar' if p in sidecar else 'NOT IN THE SIDECAR'}")
    missing = [rel(p) for p in score_path if p not in sidecar]
    print(f"hashed by `score_e168.py check`: {sum(p in checked for p in score_path)}; by neither before this pass: "
          f"{sum(p not in checked for p in score_path)}; in the sidecar: {sum(p in sidecar for p in score_path)} of {len(score_path)}"
          f" (the sidecar also holds frozen-sha256-e168.json, {len(sidecar)} files in all)")
    print("SIDECAR COVERS THE SCORE PATH" if not missing else f"SIDECAR MISSES {missing}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
