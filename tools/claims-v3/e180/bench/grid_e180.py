#!/usr/bin/env python3
"""Run E180's kinds through the whole-minion bench and collect the counts (runs on the bench host; no numpy).

    python3 grid_e180.py --bin obj_min/Vtb --kinds kinds-e180.json --asm asm_e180.py --out counts.jsonl
        [--layout A] [--delay 50] [--warm 6000] [--win 40000] [--jobs 3] [--only name,name] [--tag primary]

For every kind: the program (asm_e180.py; the random anchor's two harts get the catalogue's own words, kinds-e180.json
random_hart0 / random_hart1), the bench run with toggle coverage over the window, the bench's JSON line, the coverage
summed by hierarchy (cov_e180.py), and one line of counts.jsonl.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import struct
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cov_e180  # noqa: E402


def one(a, k, d):
    name = k["name"]
    tag = name.replace("/", "__")
    img0 = os.path.join(d, f"{tag}.img0")
    img1 = os.path.join(d, f"{tag}.img1")
    mode = k["mode"]
    if k["operands"] == "random":
        w0 = [int(x, 16) for x in a.doc["random_hart0"]]
        w1 = [int(x, 16) for x in a.doc["random_hart1"]]
    elif k["operands"] == "zeros":
        w0 = w1 = [0] * 64
    else:
        w0 = w1 = [int(k["word"], 16)] * 64
    open(img0, "wb").write(struct.pack("<64I", *w0))
    open(img1, "wb").write(struct.pack("<64I", *w1))
    hexf = os.path.join(d, f"{tag}.hex")
    c0 = a.c0.get(name, "0") if a.c0 else "0"
    info = json.loads(subprocess.run([sys.executable, a.asm, "--mode", mode, "--img0", img0, "--img1", img1, "--layout",
                                      a.layout, "--out", hexf, "--c0", c0], check=True, capture_output=True, text=True).stdout)
    cov = os.path.join(d, f"{tag}.cov")
    r = subprocess.run([a.bin, f"+prog={hexf}", f"+enabled={a.enabled}", f"+t1_delay={a.delay}", f"+warm={a.warm}",
                        f"+win={a.win}", f"+icq={a.icq}", f"+verilator+coverage+file+{cov}"],
                       capture_output=True, text=True, timeout=1800)
    line = [l for l in r.stdout.splitlines() if l.startswith("E180 ")]
    gaps = [l for l in r.stdout.splitlines() if l.startswith("E180GAPS ")]
    if r.returncode or not line:
        return {"name": name, "error": f"rc {r.returncode}: {r.stdout[-400:]} {r.stderr[-400:]}"}
    b = json.loads(line[0][5:])
    c = cov_e180.parse(cov)
    os.remove(cov)
    return {"name": name, "mode": mode, "tag": a.tag, "c0": c0, "layout": a.layout, "delay": a.delay, "enabled": a.enabled,
            "icq": a.icq, "warm": a.warm, "win": a.win, "prog": info, "bench": b,
            "gap_hist": json.loads(gaps[0].split(" ", 1)[1].replace(" ", "")) if gaps else None, "cov": c}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--kinds", required=True)
    ap.add_argument("--asm", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--layout", default="A")
    ap.add_argument("--delay", type=int, default=50)
    ap.add_argument("--enabled", type=int, default=3)
    ap.add_argument("--icq", type=int, default=1)
    ap.add_argument("--warm", type=int, default=6000)
    ap.add_argument("--win", type=int, default=40000)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--only", default="")
    ap.add_argument("--tag", default="primary")
    ap.add_argument("--c0", default="", help="accumulating kinds' starting sums: name=word,name=word")
    a = ap.parse_args()
    a.c0 = dict(x.split("=") for x in a.c0.split(",") if x) if a.c0 else {}
    a.doc = json.load(open(a.kinds))
    ks = [k for k in a.doc["kinds"] if not a.only or k["name"] in a.only.split(",")]
    with tempfile.TemporaryDirectory(dir=".") as d, ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda k: one(a, k, d), ks))
    with open(a.out, "a") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")
    bad = [r["name"] for r in res if "error" in r]
    print(f"{len(res)} kinds, {len(bad)} errors {bad[:5]}")


if __name__ == "__main__":
    main()
