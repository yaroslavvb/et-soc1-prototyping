#!/usr/bin/env python3
"""E178 (Q146): which RTL signals toggle in one TensorFMA op of a one-number tile, signal by signal (pure Python, no numpy).

For each (type, kind, n0): the accumulators after n0 ops by accum.c, written into the RF/TenC by the bench's back door, one warm
op, then a VCD of one whole op (the bench's own +dump window, as run_kinds.py takes it). Every value change of every VCD id is
counted as the Hamming distance from that id's previous value (x and z read as 0; the first dumped value is not a change), and
credited to the id's first name with every array index replaced by '*' (so the 8 lanes, the 2 TIMA slots and every RF entry of
one signal add up). Clock nets are left out, as settle_count does. The stage of a name is settle_count.cpp's stage_of(), ported.

    vcd_signals_e178.py --bin Vtb --accum accum --tiles <dir with <type>/<name>.bin> --jobs <type:name:n0,...> --out <json>

This is a reading of the bench's structure for the registration's flip model (E178.md section 3), not a count M10 uses: M10's
counts come from run_kinds.py's settle_count (nets_map, merged and settled once per cycle), which this script does not replace.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import re
import struct
import subprocess
import tempfile
from collections import defaultdict

IDX = re.compile(r"\[\d+\]|\(\d+\)")


def stage_of(full):
    has = lambda p: p in full  # noqa: E731
    nm = full.rsplit(".", 1)[-1]
    if has(".lane_tima.tima."):
        if has(".comb_adder"):
            return "adder_norm"
        if nm.startswith(("f1_in1_signed", "f1_in2_signed", "f1_mul_en")):
            return "control"
        if nm.startswith("f1_") or nm.startswith("f2_in"):
            return "operand"
        if nm.startswith("f2_prod") or nm.startswith("f3_prod"):
            return "multiplier"
        if nm.startswith("f3_out"):
            return "result"
        if nm.startswith("f3_"):
            return "adder_norm"
        return "control"
    if has(".txfmactl0_top"):
        return "control"
    if has(".txfmaexp0_top"):
        return "exponent"
    if has(".txfma0_f0"):
        return "operand"
    if has(".txfma0_f1") or has(".txfma0_f2"):
        return "multiplier"
    if has(".txfma0_f3") or has(".txfma0_f4") or has(".txfma0_f5"):
        return "adder_norm"
    if has(".txfma0_f6"):
        return "result"
    if has(".txfma."):
        if has(".F6_"):
            return "result"
        if has(".E1A_") or has(".E2_FF") or has(".E3_FF") or has(".E4_FF"):
            return "exponent"
        return "other"
    if has(".lane.rf"):
        return "c_regfile"
    if has(".lane_tima.tenb_rf") or has(".lane_tima.") or has(".lane.bypass") or has(".lane.txfma_trans_top") or has(".lane."):
        return "lane_operand_bus"
    if has(".dut.ctrl") or has(".dut."):
        return "vpu_sequencer"
    return "other"


def parse_vcd(path):
    names, width = {}, {}
    scope = []
    tog = defaultdict(int)
    last = {}
    in_defs = True
    with open(path, "r", errors="replace") as f:
        for line in f:
            if in_defs:
                s = line.split()
                if not s:
                    continue
                if s[0] == "$scope":
                    scope.append(s[2])
                elif s[0] == "$upscope":
                    scope.pop()
                elif s[0] == "$var":
                    w, i, ref = int(s[2]), s[3], s[4]
                    if i not in names:
                        names[i] = ".".join(scope + [ref])
                        width[i] = w
                elif s[0] == "$enddefinitions":
                    in_defs = False
                continue
            c = line[0]
            if c in "#$\n":
                continue
            if c in "01xzXZ":
                v, i = c, line[1:].strip()
            elif c in "bB":
                v, i = line[1:].split()
            else:
                continue
            bits = int(v.replace("x", "0").replace("z", "0").replace("X", "0").replace("Z", "0"), 2) if v not in "xzXZ" else 0
            if i in last:
                tog[i] += bin(bits ^ last[i]).count("1")
            last[i] = bits
    agg = defaultdict(int)
    for i, n in tog.items():
        nm = names[i]
        if re.search(r"clk|clock", nm.rsplit(".", 1)[-1]):
            continue
        agg[IDX.sub("[*]", nm)] += n
    return agg


def one(a, typ, name, n0):
    with tempfile.TemporaryDirectory(dir=a.tmp) as d:
        path = os.path.join(a.tiles, typ, name + ".bin")
        pts = [n0, n0 + 1] if n0 else [1]
        subprocess.run([os.path.abspath(a.accum), typ, os.path.abspath(path)] + [str(p) for p in pts], check=True, cwd=d)
        c0 = open(os.path.join(d, f"accum_{n0}.bin"), "rb").read() if n0 else b"\0" * 1024
        words = struct.unpack("<512I", open(path, "rb").read()) + struct.unpack("<256I", c0)
        hexf = os.path.join(d, "t.hex")
        open(hexf, "w").write("\n".join(f"{w:08x}" for w in words) + "\n")
        vcd = os.path.join(d, "t.vcd")
        subprocess.run([a.bin, f"+tiles={hexf}", f"+fmt={typ}", "+warm=1", f"+first={0 if n0 else 1}", f"+loadc={1 if n0 else 0}",
                        "+ops=1", f"+dump={vcd}", "+dump_ops=1"], capture_output=True, text=True, check=True)
        agg = parse_vcd(vcd)
    by_stage = defaultdict(int)
    for nm, n in agg.items():
        by_stage[stage_of(nm)] += n
    return {"type": typ, "kind": name, "n0": n0, "total": sum(agg.values()), "by_stage": dict(by_stage),
            "signals": dict(sorted(agg.items(), key=lambda kv: -kv[1]))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--accum", required=True)
    ap.add_argument("--tiles", required=True)
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tmp", default=None)
    a = ap.parse_args()
    res = []
    for j in a.jobs.split(","):
        typ, name, n0 = j.split(":")
        r = one(a, typ, name, int(n0))
        print(typ, name, n0, r["total"], json.dumps(r["by_stage"]), flush=True)
        res.append(r)
    json.dump({"_what": "per-signal toggles (Hamming distance per change), one op, the bench's VCD window", "rows": res},
              open(a.out, "w"), indent=0)


if __name__ == "__main__":
    main()
