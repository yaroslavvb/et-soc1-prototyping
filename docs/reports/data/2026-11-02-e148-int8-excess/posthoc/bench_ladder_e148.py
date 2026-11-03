#!/usr/bin/env python3
"""E148 post hoc (written after the run, deciding nothing): the TIMA bench's TenC read-address counts for int8 on zeros, nothing issued, at
A rows R = 1, 2, 3, 5, 6, 8 and 16 (K = 16), each at the card's predicted cycles (the bench's + 7.75), with fp32's partner cycles. It runs Q136(c)'s
binary (sha256 checked against its versions.txt) through Q136(c)'s run_streams.run and price.candidates, unchanged.

    python3 docs/reports/data/2026-11-02-e148-int8-excess/posthoc/bench_ladder_e148.py --bin <obj_q136c/Vtb> --out .../posthoc/bench-ladder.json
Standard library only. SPDX-License-Identifier: Apache-2.0"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "rtl-sim", "tima_bench"))
import run_streams as rs  # noqa: E402
import price as pr  # noqa: E402


def st(fmt, R, period):
    return {"set": "ladder", "name": f"r{R}.{fmt}", "fmt": fmt, "kind": "zeros", "arm": f"r{R}", "rows": R, "cols": 16, "mask": 0,
            "period": period, "pre": 0, "firstall": 0, "tile": rs.TILE[(fmt, "zeros")]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    bsha = hashlib.sha256(open(a.bin, "rb").read()).hexdigest()
    if bsha not in open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-q136c-tima-bench", "versions.txt")).read():
        raise SystemExit("not Q136(c)'s bench binary")
    out = {"binary_sha256": bsha, "rows": {}}
    for R in (1, 2, 3, 5, 6, 8, 16):
        pace = {f: rs.run(a.bin, st(f, R, 1))["cycles"] for f in ("fp32", "int8")}
        per = {f: int(round(pace[f] + 7.75)) for f in pace}
        c = pr.candidates(rs.run(a.bin, st("int8", R, per["int8"])))
        out["rows"][str(R)] = {"bench_cycles": pace, "card_cycles": per, "tenc_reads": c["tenc"]["reads"],
                               "tenc_newaddr": c["tenc"]["reads_newaddr"], "tenc_raddr_tog": c["tenc"]["raddr_tog"],
                               "tentmp_writes": c["scp"]["tentmp_writes"], "tima_ctrl_bits": c["tima_ctrl"]["int8_enabled_clocked"]}
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    print(json.dumps(out["rows"], indent=0))


if __name__ == "__main__":
    main()
