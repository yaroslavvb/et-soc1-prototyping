#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""POST HOC, exploratory, no rule of E102's depends on it. Why E92's fp16 tiles are where C = fl((n-1) S) fails most, and whether E92's own measurements can tell the two starts apart. Run from the repo's root, after fault_refit_e102.py has written both fits:

    fault_e92_fp16_e102.py <fit from fl json> <fit from real json>

Part A: one absorbed fp16 addition and subtraction by fp16_model.py, the arithmetic fcheck_unit.py checks against the RTL's txfma_top (vpu_tensorfma.v:693, "FP1632 ops only support RTZ"), and by txfma_top itself where FAULT_VUNIT names a built tb_unit.sv; and what accum.c's accumulators then hold on E92's tiles.
Part B: E92's fp16 contrasts as measured (its primary and its dips-removed arm, per pass, its t intervals) against the two parts of the model the start moves, from each start, at fp32's own prices, neither fitted on fp16: E92's frozen 6.68 fJ per adder-flop bit and the
30.0 fJ per result bit E92 read from fp32's moving sums. Operand buses and products are left out, so a contrast whose operands differ reads low by their cost: E92's own h_add - c_abs, the same signs moving with no alternation, is 0.48 W in the dips arm. C was not read back on any card.
Part C: what the two counted ops change if they use fp16's own arithmetic rather than make_e88's ordinary addition."""
import json
import math
import os
import struct
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "tools", "claims-v3", "rpath"), os.path.join(ROOT, "tools", "claims-v3", "hlp"), os.path.join(ROOT, "rtl-sim", "fma_toggle_v2")]
import fault_fl_ns_e102 as ff      # noqa: E402
import fp16_model as fm            # noqa: E402
import make_e102 as m102           # noqa: E402
import make_e88 as me              # noqa: E402

E92 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-01-e92-sign-split")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
F_FJ, B_FJ = 6.68, 30.0
# name, the tiles added, the tiles taken away, whether the operands are the same on both sides
CONTRASTS = (("h_sub - h_add", ("h_sub",), ("h_add",), True), ("c_alt - c_abs", ("c_alt",), ("c_abs",), True), ("h_allsub - h_add", ("h_allsub",), ("h_add",), True), ("h_add - c_abs", ("h_add",), ("c_abs",), False),
             ("h_sub - c_abs", ("h_sub",), ("c_abs",), False), ("hh_sub - c_abs", ("hh_sub",), ("c_abs",), False), ("hl_sub - c_abs", ("hl_sub",), ("c_abs",), False), ("s_abs - c_abs", ("s_abs",), ("c_abs",), False),
             ("signs - s_abs", ("signs",), ("s_abs",), False), ("hh_sub + hl_sub - h_sub - c_abs", ("hh_sub", "hl_sub"), ("h_sub", "c_abs"), False))


def measured(path, plus, minus):
    d = json.load(open(path))["per_pass"]
    vals = []
    for p, items in sorted(d.items()):
        names = [f"fp16.{t}" for t in plus + minus]
        if all(n in items and items[n].get("D") is not None for n in names):
            vals.append(sum(items[f"fp16.{t}"]["D"] for t in plus) - sum(items[f"fp16.{t}"]["D"] for t in minus))
    m = sum(vals) / len(vals)
    ci = T95[len(vals) - 1] * math.sqrt(sum((x - m) ** 2 for x in vals) / (len(vals) - 1) / len(vals)) if len(vals) > 1 else float("nan")
    return m, ci, len(vals)


def main():
    print("Part A. One absorbed fp16 term on an accumulator of 2^49, by fp16_model.model (the RTL's rule):")
    c = 0x58000000
    a = (0x3C00 << 16) | 0x3C00
    cases = (("both products add", (0x3C00 << 16) | 0x3C00), ("both subtract", (0xBC00 << 16) | 0xBC00), ("only the high one subtracts", (0xBC00 << 16) | 0x3C00), ("only the low one subtracts", (0x3C00 << 16) | 0xBC00))
    rtl = {}
    if os.environ.get("FAULT_VUNIT"):           # a built tb_unit.sv (rtl-sim/fma_toggle_v2/Makefile, obj_unit/Vtb), as fcheck_unit.py runs it
        with tempfile.TemporaryDirectory() as td:
            hexf = os.path.join(td, "vec.hex")
            with open(hexf, "w") as f:
                for _, w in cases:
                    f.write(f"{a:08x}\n{w:08x}\n{c:08x}\n")
            out = subprocess.run([os.environ["FAULT_VUNIT"], f"+vec={hexf}", f"+n={len(cases)}", "+fmt=fp16"], capture_output=True, text=True, check=True).stdout
        for line in out.splitlines():
            if line.startswith("R "):
                rtl[int(line.split()[1])] = int(line.split()[2], 16)
    for i, (name, w) in enumerate(cases):
        r = fm.model(a, w, c)
        print(f"  a words (1, 1), {name:28s} C 0x{c:08x} -> 0x{r:08x}, {r - c:+d} ulp" + (f"; the RTL's txfma_top -> 0x{rtl[i]:08x}, {rtl[i] - c:+d} ulp" if i in rtl else ""))
    print("And what accum.c's accumulators hold after n ops, against fl(n S), on row 0 of E92's tiles (col 0 and col 8 are in different halves of h_add's and h_sub's B word):")
    acc = m102.accum_binary()
    flt = lambda w: struct.unpack("<f", struct.pack("<I", int(w)))[0]
    for t in ("c_abs", "h_add", "h_allsub", "h_sub", "hh_sub", "hl_sub", "s_abs"):
        p = os.path.join(HERE, "e92", "tiles", "fp16", t + ".bin")
        aw, bw = me.words_from_tile(open(p, "rb").read())
        A, B = me.elements("fp16", aw, bw)
        S = me.per_op_sum("fp16", A, B)
        with tempfile.TemporaryDirectory() as td:
            subprocess.run([acc, "fp16", p, "66624", "199874"], check=True, cwd=td)
            for n in (66624, 199874):
                C = np.frombuffer(open(os.path.join(td, f"accum_{n}.bin"), "rb").read(), dtype="<u4").reshape(16, 16)
                fl = me.fl("fp16", n * S).astype(np.float32).view(np.uint32)
                print(f"  {t:9s} n {n:6d}: real col 0 {flt(C[0, 0]):12.5e}, col 8 {flt(C[0, 8]):12.5e}; fl {flt(fl[0, 0]):12.5e}, {flt(fl[0, 8]):12.5e}; distinct words real {len(np.unique(C))}, fl {len(np.unique(fl))}; {int((C != fl).sum())} of 256 differ from fl")
    fits = {s: json.load(open(p)) for s, p in zip(("fl", "real"), sys.argv[1:3])}
    ops = fits["fl"]["ops_per_s"]
    rows = {s: {r["name"]: r for r in f["tiles"]["fp16"]} for s, f in fits.items()}

    def part(s, plus, minus):
        def w(t):
            r = rows[s][f"fp16.{t}"]
            return (B_FJ * r["res"] + F_FJ * r["flops"]) * 1e-15 * ops
        return sum(w(t) for t in plus) - sum(w(t) for t in minus)

    print(f"\nPart B. fp16, watts on aifoundry3. Parts of the model = {B_FJ} fJ x result bits + {F_FJ} fJ x flop bits, from each start, at make_e92's launch. * = the same operands on both sides.")
    print(f"{'contrast':34s} {'measured, primary':>20s} {'measured, dips removed':>23s} {'from fl':>8s} {'from real':>10s}")
    err = {"fl": [], "real": []}
    for name, plus, minus, same in CONTRASTS:
        m1, c1, n1 = measured(os.path.join(E92, "e92.json"), plus, minus)
        m2, c2, n2 = measured(os.path.join(E92, "dips-arm", "e92-nodips.json"), plus, minus)
        a, b = part("fl", plus, minus), part("real", plus, minus)
        print(f"{name + (' *' if same else ''):34s} {m1:7.3f} +- {c1:5.3f} ({n1}) {m2:12.3f} +- {c2:5.3f} ({n2}) {a:8.2f} {b:10.2f}")
        err["fl"].append(m2 - a)
        err["real"].append(m2 - b)
    print("rms, measured (dips removed) - parts, over these contrasts: from fl {:.2f} W, from real {:.2f} W".format(*(math.sqrt(sum(x * x for x in err[s]) / len(err[s])) for s in ("fl", "real"))))
    print("\nPart C. fp16, real sums, the two counted ops by make_e88's ordinary addition and by fp16_model.model:")
    for path in ("e92/tiles/fp16/h_sub.bin", "e92/tiles/fp16/s_abs.bin", "tiles/fp16/randn.bin"):
        raw = open(os.path.join(HERE, path), "rb").read()
        c0, c1 = ff.counts("fp16", raw, "real", acc), ff.counts("fp16", raw, "real", acc, step=fm.model)
        print(f"  {path:28s} res {c0['res']:8.0f} -> {c1['res']:8.0f}; flops {c0['flops']:8.0f} -> {c1['flops']:8.0f}", flush=True)
    print("\nCounts at the launch of part B: " + "; ".join(f"{t} res {rows['fl']['fp16.' + t]['res']:.0f} -> {rows['real']['fp16.' + t]['res']:.0f}, flops {rows['fl']['fp16.' + t]['flops']:.0f} -> {rows['real']['fp16.' + t]['flops']:.0f}" for t in ("c_abs", "h_add", "h_allsub", "h_sub", "c_alt", "hh_sub", "hl_sub", "s_abs", "signs")))


if __name__ == "__main__":
    main()
