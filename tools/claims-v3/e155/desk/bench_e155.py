#!/usr/bin/env python3
"""E155 desk (Q139): the TIMA bench's counts for E155's arms, per TensorFMA op on one minion, with no micro-op issued (row mask 0x0000).

    python3 tools/claims-v3/e155/desk/bench_e155.py --bin <Q136(c)'s obj_q136c/Vtb> --out tools/claims-v3/e155/desk/bench-e155.json   # repo root

A port of tools/claims-v3/e148/desk/bench_e148.py: it runs Q136(c)'s bench (rtl-sim/tima_bench/, built by its build.sh; the binary's sha256 is
checked against docs/reports/data/2026-11-02-q136c-tima-bench/versions.txt) through Q136(c)'s own run_streams.run and price.candidates,
unchanged, for:
  m0      16 A rows, K 16 (E109's, E129's and E148's arm; the sixteen-row reference the readings are scaled to)   int8 318, fp32 544
  m0r1     1 A row,  K 16 (E129's and E148's arm)                                                                 both at 62
  m0r3     3 A rows, K 16 (NEW in E155)                                                                           int8 110, fp32 128
  m0r3k8   3 A rows, K  8 (NEW in E155: m0r3's K = 8 partner, E109's m0k8 construction at three rows)            from the bench + 7.75
each int8 stream from reset and each fp32 stream both from reset (+pre=0) and in the card's order (+pre=2: two int8 ops before it, as on a card,
where TenC's read enable is left high by int8 work, Q136(c) result 3). The pace runs (+period=1) give the bench's own cycles; the card's are those
plus E109's 7.75 (R6, matched by E129 at one A row and by E148 at two to the cycle). The m0 and m0r1 streams are compared field by field with
Q136(c)'s committed counts.json, and m0r3's int8 counts with E148's post hoc bench ladder (docs/reports/data/2026-11-02-e148-int8-excess/posthoc/
bench-ladder.json, row 3): they must be identical. Standard library only.
SPDX-License-Identifier: Apache-2.0"""
import argparse
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "rtl-sim", "tima_bench"))
import run_streams as rs  # noqa: E402
import price as pr  # noqa: E402

Q136C = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-q136c-tima-bench")
LADDER = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e148-int8-excess", "posthoc", "bench-ladder.json")
SHAPES = {"m0": (16, 16), "m0r1": (1, 16), "m0r3": (3, 16), "m0r3k8": (3, 8)}
DELTA = 7.75


def stream(fmt, arm, period, pre=0):
    R, K = SHAPES[arm]
    return {"set": "e155", "name": f"{'pre.' if pre else ''}{arm}.{fmt}.zeros", "fmt": fmt, "kind": "zeros", "arm": arm, "rows": R, "cols": K,
            "mask": 0, "period": period, "pre": pre, "firstall": 0, "tile": rs.TILE[(fmt, "zeros")]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    bsha = hashlib.sha256(open(a.bin, "rb").read()).hexdigest()
    vers = open(os.path.join(Q136C, "versions.txt")).read()
    if bsha not in vers:
        raise SystemExit(f"the bench binary {bsha} is not Q136(c)'s (versions.txt)")
    keys = [(arm, fmt) for arm in SHAPES for fmt in ("fp32", "int8")]
    with ThreadPoolExecutor(a.jobs) as ex:
        paced = list(ex.map(lambda k: rs.run(a.bin, stream(k[1], k[0], 1))["cycles"], keys))
    pace = dict(zip(keys, paced))
    out = {"what": __doc__.split("\n")[0], "binary_sha256": bsha, "shapes": {k: list(v) for k, v in SHAPES.items()},
           "bench_cycles": {f"{k[0]}.{k[1]}": v for k, v in pace.items()}, "card_cycles_predicted": {}, "streams": {}}
    jobs = []
    for arm in SHAPES:
        for fmt in ("fp32", "int8"):
            per = int(round(pace[(arm, fmt)] + DELTA))
            out["card_cycles_predicted"][f"{arm}.{fmt}"] = per
            for pre in ((0, 2) if fmt == "fp32" else (0,)):
                jobs.append((arm, fmt, pre, per))
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda j: rs.run(a.bin, stream(j[1], j[0], j[3], j[2])), jobs))
    for (arm, fmt, pre, per), po in zip(jobs, res):
        s = stream(fmt, arm, per, pre)
        out["streams"][s["name"]] = {"arm": arm, "fmt": fmt, "pre": pre, "period": per, "per_op": po, "candidates": pr.candidates(po)}
    # identity with Q136(c)'s committed counts for the streams it already ran
    C = json.load(open(os.path.join(Q136C, "counts.json")))
    theirs = {s["name"]: s["per_op"] for s in C["streams"] if s["set"] in ("design", "context", "arms", "context_arms")}
    chk = {}
    for mine in ("m0.int8.zeros", "m0.fp32.zeros", "pre.m0.fp32.zeros", "m0r1.int8.zeros", "m0r1.fp32.zeros", "pre.m0r1.fp32.zeros"):
        x = pr.candidates(out["streams"][mine]["per_op"])
        y = pr.candidates(theirs[mine]) if mine in theirs else None
        chk[mine] = "identical" if y is not None and json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True) else (
            "absent in counts.json" if y is None else "DIFFERS")
    # identity of m0r3's int8 counts and both formats' card cycles with E148's post hoc ladder (row 3)
    L = json.load(open(LADDER))["rows"]["3"]
    c3 = out["streams"]["m0r3.int8.zeros"]["candidates"]
    mine3 = {"card_cycles": {"fp32": out["card_cycles_predicted"]["m0r3.fp32"], "int8": out["card_cycles_predicted"]["m0r3.int8"]},
             "tenc_reads": c3["tenc"]["reads"], "tenc_newaddr": c3["tenc"]["reads_newaddr"], "tenc_raddr_tog": c3["tenc"]["raddr_tog"],
             "tentmp_writes": c3["scp"]["tentmp_writes"], "tima_ctrl_bits": c3["tima_ctrl"]["int8_enabled_clocked"]}
    theirs3 = {k: L[k] for k in mine3}
    chk["m0r3 against E148's bench ladder row 3"] = "identical" if json.dumps(mine3, sort_keys=True) == json.dumps(theirs3, sort_keys=True) else (
        "DIFFERS: " + json.dumps({"mine": mine3, "ladder": theirs3}))
    out["check_against_committed_counts"] = chk
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    show = {}
    for arm in SHAPES:
        c = out["streams"][f"{arm}.int8.zeros"]["candidates"]
        show[arm] = {"card_cycles": {f: out["card_cycles_predicted"][f"{arm}.{f}"] for f in ("fp32", "int8")},
                     "int8_tenc_reads": c["tenc"]["reads"], "int8_tenc_newaddr": c["tenc"]["reads_newaddr"],
                     "int8_tenc_raddr_tog": c["tenc"]["raddr_tog"], "int8_tentmp_writes": c["scp"]["tentmp_writes"],
                     "int8_tima_ctrl_bits": c["tima_ctrl"]["int8_enabled_clocked"], "int8_tena_writes": c["scp"]["tena_writes"],
                     "int8_tenb_writes": c["tenb"]["writes"]}
    print(json.dumps({"bench_cycles": out["bench_cycles"], "per_op_int8": show, "check": chk}, indent=1))


if __name__ == "__main__":
    main()
