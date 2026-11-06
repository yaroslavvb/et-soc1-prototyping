#!/usr/bin/env python3
"""The bench's issue rate against the energy catalogue's measured one (catalogue.json, 26 Sep 2026, ops_per_cycle_per_hart),
and the loop's gaps, over loop layouts, hart start skews and icache contention (runs on the bench host; no numpy).

    python3 validate_e180.py --bin obj_min/Vtb --asm asm_e180.py --out validation-e180.jsonl [--jobs 4]

Each line: mode, layout, harts (+enabled 3 = both, 1 = hart 0), hart 1's start delay, the icache's grant period, the
bench's E180 line and gap histogram. No coverage is taken (rates and gaps only). The word is 4.0 (0x40800000) throughout:
the loop's timing does not depend on the operand values (the bench's own counts show equal rates for every kind).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

CASES = []
for mode in ("fadd.ps",):
    CASES += [(mode, "A", 3, d, 1) for d in (0, 7, 23, 50, 101, 137)]
    CASES += [(mode, "A", 1, 0, 1)]
    CASES += [(mode, f"o{k}{r}", e, 50 if e == 3 else 0, 1) for k in range(0, 32, 4) for r in ("", "r") for e in (3, 1)]
    CASES += [(mode, "A", 3, 50, q) for q in (2, 3, 4, 8)] + [(mode, "A", 1, 0, 2)]
CASES += [("fadd.pi", "A", 3, 50, 1), ("fadd.pi", "A", 3, 0, 1), ("fadd.ps.acc", "A", 3, 50, 1), ("fadd.pi.acc", "A", 3, 50, 1)]
for mode in ("add", "nop", "spin"):
    CASES += [(mode, "A", 3, 0, 1), (mode, "A", 3, 50, 1), (mode, "A", 1, 0, 1)]
CASES += [("add", "A", 1, 0, 2)]


def run(a, case, d):
    mode, layout, en, delay, icq = case
    tag = f"{mode}_{layout}_e{en}_d{delay}_q{icq}"
    hexf = os.path.join(d, tag + ".hex")
    subprocess.run([sys.executable, a.asm, "--mode", mode, "--word", "0x40800000", "--layout", layout, "--out", hexf],
                   check=True, capture_output=True)
    r = subprocess.run([a.bin, f"+prog={hexf}", f"+enabled={en}", f"+t1_delay={delay}", f"+icq={icq}", "+warm=6000",
                        "+win=40000"], capture_output=True, text=True, timeout=1800)
    line = [l for l in r.stdout.splitlines() if l.startswith("E180 ")]
    gaps = [l for l in r.stdout.splitlines() if l.startswith("E180GAPS ")]
    b = json.loads(line[0][5:]) if line else None
    return {"mode": mode, "layout": layout, "enabled": en, "t1_delay": delay, "icq": icq, "bench": b,
            "rate_per_hart": [64 * i / b["cycles"] for i in b["iters"]] if b else None,
            "gap_hist": json.loads(gaps[0].split(" ", 1)[1].replace(" ", "")) if gaps else None,
            "rc": r.returncode}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--asm", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(dir=".") as d, ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda c: run(a, c, d), CASES))
    with open(a.out, "w") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")
    print(f"{len(res)} cases, {sum(1 for r in res if r['rc'] or not r['bench'])} failed")


if __name__ == "__main__":
    main()
