#!/usr/bin/env python3
"""Which operand of `x * y` yosys's booth pass recodes: a 9x9 signed multiply alone, both operand orders.

    python3 booth_operand.py --yosys $SCRATCH/oss-cad-suite/bin/yosys --work <dir> > recoded_operand.txt

Q133(a). tima_top.v:89 writes `$signed(f2_in1_part[i]) * $signed(f2_in2_part[i])`, in1 from TenA (A), in2 from TenB (B)
(vpu_lane_tima.v: f1_in1 = tena_rd_data, f1_in2 = tenb_out). The radix-4 Booth recoder reads overlapping 3-bit windows of one
operand, so an odd bit of that operand enters two digits and an even bit one. This finds which operand feeds the encoder
cells (`bur_enc` in the pass's cell names) right after the pass, before any technology mapping.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import json
import os
import subprocess


def probe(yosys, work, expr, tag):
    v = os.path.join(work, f"m_{tag}.v")
    j = os.path.join(work, f"m_{tag}.json")
    ys = os.path.join(work, f"m_{tag}.ys")
    open(v, "w").write(f"module m(input signed [8:0] a, input signed [8:0] b, output signed [17:0] p);\n  assign p = {expr};\nendmodule\n")
    open(ys, "w").write(f"read_verilog {v}\nhierarchy -top m\nproc; opt; wreduce\nbooth\nopt_clean\nwrite_json {j}\n")
    subprocess.run([yosys, "-q", "-s", ys], check=True, capture_output=True)
    m = json.load(open(j))["modules"]["m"]
    bits = {}
    for pn, p in m["ports"].items():
        for i, b in enumerate(p["bits"]):
            bits[b] = pn
    enc, other = collections.Counter(), collections.Counter()
    for cn, c in m["cells"].items():
        for pin, bl in c["connections"].items():
            if c.get("port_directions", {}).get(pin) != "input":
                continue
            for b in bl:
                if b in bits and bits[b] in ("a", "b"):
                    (enc if "enc" in cn else other)[bits[b]] += 1
    return dict(enc), dict(other)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yosys", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    ver = subprocess.run([a.yosys, "-V"], capture_output=True, text=True).stdout.strip()
    print(f"# {ver}")
    print("# input pins of the cells the booth pass creates, by operand: encoder cells (bur_enc*) and the rest")
    for expr, tag in (("a * b", "ab"), ("b * a", "ba")):
        enc, other = probe(a.yosys, a.work, expr, tag)
        recoded = ", ".join(sorted(enc)) or "none"
        print(f"p = {expr}: encoder cells read {enc}; other cells read {other}; recoded operand: {recoded}")
    print("# so `x * y` recodes y, the second operand: in tima_top.v as written that is f2_in2_part, the B operand (booth,")
    print("# booth_tree), and in the swapped copy (booth_swap) it is f2_in1_part, the A operand.")


if __name__ == "__main__":
    main()
