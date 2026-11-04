#!/usr/bin/env python3
"""Q141(t2): compare bench points counted by two builds, field by field (every counted field of run_kinds.py's point record).

    python3 -B compare_points.py <out.json> <counts.json> [--ref <counts.json> ...]

Each point of <counts.json> (run_kinds.py's own JSON) is looked up by tile and n0 in the --ref files (default: the committed
Intel-built counts of the 16 calibration tiles at 9, 27 and 81 points). A point is identical when its whole record, every field
and sub-field, equals the reference's (compared as canonical JSON). Writes <out.json> and prints a summary; exits 1 if any
point differs or has no reference. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
M9D = os.path.abspath(os.path.join(D, "..", "2026-11-04-q140m-m9"))
DEFAULT_REF = [os.path.join(M9D, "bench-check", "counts-cal.json"), os.path.join(M9D, "recount-rule", "counts-pilot27.json")] + sorted(
    glob.glob(os.path.join(D, "step81", "counts-cal81-[0-9].json")))
canon = lambda o: json.dumps(o, sort_keys=True)  # noqa: E731


def diff(a, b, p=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += diff(a.get(k), b.get(k), f"{p}.{k}")
        return out
    return [] if canon(a) == canon(b) else [f"{p}: {a} vs {b}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("counts")
    ap.add_argument("--ref", action="append", default=None)
    a = ap.parse_args()
    refs = a.ref or DEFAULT_REF
    ref = {}
    for f in refs:
        for k, r in json.load(open(f))["rows"].items():
            for p in r["points"]:
                ref.setdefault((k, p["n0"]), p)
    res = {"_note": "Q141(t2): bench points of two builds compared field by field", "counts": os.path.basename(a.counts),
           "refs": [os.path.relpath(f, D) for f in refs], "points": {}}
    for k, r in json.load(open(a.counts))["rows"].items():
        for p in r["points"]:
            want = ref.get((k, p["n0"]))
            if want is None:
                res["points"][f"{k}:{p['n0']}"] = {"identical": False, "why": "no reference point"}
                continue
            d = diff(p, want)
            res["points"][f"{k}:{p['n0']}"] = {"identical": not d, "n_fields_differ": len(d), "first": d[:4],
                                               "check_mismatch": p["check_mismatch"]}
    n = len(res["points"])
    same = sum(1 for v in res["points"].values() if v["identical"])
    res["n_points"], res["n_identical"] = n, same
    json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
    print(f"{same} of {n} points identical in every field ({os.path.basename(a.counts)} against {len(refs)} reference files)")
    sys.exit(0 if n and same == n else 1)


if __name__ == "__main__":
    main()
