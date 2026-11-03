#!/usr/bin/env python3
"""E148 desk (Q138): the TIMA bench's counts for E148's three arms, per TensorFMA op on one minion, with no micro-op issued (row mask 0x0000).

    python3 tools/claims-v3/e148/desk/bench_e148.py --bin <Q136(c)'s obj_q136c/Vtb> --out tools/claims-v3/e148/desk/bench-e148.json   # repo root

It runs Q136(c)'s bench (rtl-sim/tima_bench/, built by its build.sh; the binary's sha256 is checked against
docs/reports/data/2026-11-02-q136c-tima-bench/versions.txt) through Q136(c)'s own run_streams.run and price.candidates, unchanged, for:
  m0    16 A rows, K 16 (E109's and E129's arm)       int8 at 318 cycles a card op, fp32 at 544
  m0r1   1 A row,  K 16 (E129's arm)                  both at 62
  m0r2   2 A rows, K 16 (NEW in E148)                 int8 at round(86.25 + 7.75) = 94, fp32 at round(88.25 + 7.75) = 96
each int8 stream from reset and each fp32 stream both from reset (+pre=0) and in the card's order (+pre=2: two int8 ops before it, as on a card,
where TenC's read enable is left high by int8 work, Q136(c) result 3). The pace runs (+period=1) give the bench's own cycles; the card's are those
plus E109's 7.75 (R6, matched by E129 to the cycle at one A row). The m0 and m0r1 streams are compared field by field with Q136(c)'s committed
counts.json (they must be identical: the same binary, the same streams). Standard library only.
SPDX-License-Identifier: Apache-2.0"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "rtl-sim", "tima_bench"))
import run_streams as rs  # noqa: E402
import price as pr  # noqa: E402

Q136C = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-q136c-tima-bench")
SHAPES = {"m0": (16, 16), "m0r1": (1, 16), "m0r2": (2, 16)}
DELTA = 7.75


def stream(fmt, arm, period, pre=0):
    R, K = SHAPES[arm]
    return {"set": "e148", "name": f"{'pre.' if pre else ''}{arm}.{fmt}.zeros", "fmt": fmt, "kind": "zeros", "arm": arm, "rows": R, "cols": K,
            "mask": 0, "period": period, "pre": pre, "firstall": 0, "tile": rs.TILE[(fmt, "zeros")]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    bsha = hashlib.sha256(open(a.bin, "rb").read()).hexdigest()
    vers = open(os.path.join(Q136C, "versions.txt")).read()
    if bsha not in vers:
        raise SystemExit(f"the bench binary {bsha} is not Q136(c)'s (versions.txt)")
    pace = {}
    for arm in SHAPES:
        for fmt in ("fp32", "int8"):
            pace[(arm, fmt)] = rs.run(a.bin, stream(fmt, arm, 1))["cycles"]
    out = {"what": __doc__.split("\n")[0], "binary_sha256": bsha, "bench_cycles": {f"{k[0]}.{k[1]}": v for k, v in pace.items()},
           "card_cycles_predicted": {}, "streams": {}}
    for arm in SHAPES:
        for fmt in ("fp32", "int8"):
            per = int(round(pace[(arm, fmt)] + DELTA))
            out["card_cycles_predicted"][f"{arm}.{fmt}"] = per
            for pre in ((0, 2) if fmt == "fp32" else (0,)):
                s = stream(fmt, arm, per, pre)
                po = rs.run(a.bin, s)
                out["streams"][s["name"]] = {"arm": arm, "fmt": fmt, "pre": pre, "period": per, "per_op": po, "candidates": pr.candidates(po)}
    # identity with Q136(c)'s committed counts for the streams it already ran
    C = json.load(open(os.path.join(Q136C, "counts.json")))
    theirs = {}
    for s in C["streams"]:
        if s["set"] in ("design", "context", "arms", "context_arms"):
            theirs[s["name"]] = s["per_op"]
    chk = {}
    for mine, their in (("m0.int8.zeros", "m0.int8.zeros"), ("m0.fp32.zeros", "m0.fp32.zeros"), ("pre.m0.fp32.zeros", "pre.m0.fp32.zeros"),
                        ("m0r1.int8.zeros", "m0r1.int8.zeros"), ("m0r1.fp32.zeros", "m0r1.fp32.zeros"), ("pre.m0r1.fp32.zeros", "pre.m0r1.fp32.zeros")):
        x = pr.candidates(out["streams"][mine]["per_op"])
        y = pr.candidates(theirs[their]) if their in theirs else None
        chk[mine] = "identical" if y is not None and json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True) else (
            "absent in counts.json" if y is None else "DIFFERS")
    out["check_against_q136c_counts"] = chk
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    print(json.dumps({"bench_cycles": out["bench_cycles"], "card_cycles_predicted": out["card_cycles_predicted"], "check": chk}, indent=1))


if __name__ == "__main__":
    main()
