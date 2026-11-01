#!/usr/bin/env python3
"""Functional check of the whole VPU: does a real TensorFMA leave the right C, op after op?

    fcheck_vpu.py --bin obj_vpu/Vtb --out fcheck-vpu.json [--ops 4] [--seed 1] [--jobs 8]

Runs tiles built to reach the corners through tb_vpu.sv, which instantiates vpu_top whole, and replays each one in
software: for k, for row i, for column j, in the RTL's order, the first A column of a first-pass op multiplies and every
later micro-op multiply-adds, unless the zero gate takes the lane. C is compared bit for bit after every op, and so is the
RTL's own count of valid column slots against the gate rule. fp32 and int8 are compared with exact arithmetic; fp16 with
the fixed-point window of fp16_model.py, and with exact arithmetic beside it.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import json
import os
import random
import struct
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

import fcheck_unit as F
import fp16_model as M


def fw(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def hw(x):
    return struct.unpack("<H", struct.pack("<e", x))[0]


def word(fmt, rng, style):
    """One 32-bit lane word of the tile, by style."""
    if fmt == "fp32":
        if style == "random":
            return fw(rng.gauss(0, 1))
        if style == "range":
            return (rng.getrandbits(1) << 31) | (rng.randint(100, 150) << 23) | rng.getrandbits(23)
        if style == "gated":
            return 0 if rng.random() < 0.5 else fw(rng.gauss(0, 1))
        if style == "corners":
            return rng.choice([0, 0x80000000, 0x00000001, 0x80000001, 0x007FFFFF, 0x00800000, 0x80800000, 0x3F800000,
                               0xBF800000, 0x7F7FFFFF, 0xFF7FFFFF, 0x40490FDB, fw(rng.gauss(0, 1)), fw(rng.gauss(0, 1))])
        if style == "special":
            return rng.choice([0x7F800000, 0xFF800000, 0x7FC00000, 0x7F800001, 0, 0x3F800000, fw(rng.gauss(0, 1))])
    if fmt == "fp16":
        def half():
            if style == "random":
                return hw(rng.gauss(0, 1))
            if style == "range":
                return (rng.getrandbits(1) << 15) | (rng.randint(8, 22) << 10) | rng.getrandbits(10)
            if style == "gated":
                return 0 if rng.random() < 0.5 else hw(rng.gauss(0, 1))
            if style == "corners":
                return rng.choice([0, 0x8000, 0x0001, 0x8001, 0x03FF, 0x0400, 0x8400, 0x3C00, 0xBC00, 0x7BFF, 0xFBFF, hw(rng.gauss(0, 1))])
            if style == "special":
                return rng.choice([0x7C00, 0xFC00, 0x7E00, 0x7C01, 0, 0x3C00, hw(rng.gauss(0, 1))])
        if style == "gated":
            return 0 if rng.random() < 0.5 else (half() << 16) | half()
        return (half() << 16) | half()
    if fmt == "int8":
        def b():
            if style == "random" or style == "range":
                return rng.getrandbits(8)
            if style == "gated":
                return 0 if rng.random() < 0.5 else rng.getrandbits(8)
            return rng.choice([0, 1, 0xFF, 0x7F, 0x80, rng.getrandbits(8)])
        if style == "gated":
            return 0 if rng.random() < 0.6 else b() | (b() << 8) | (b() << 16) | (b() << 24)
        return b() | (b() << 8) | (b() << 16) | (b() << 24)
    raise ValueError(style)


def s8(w, e):
    x = (w >> (8 * e)) & 0xFF
    return x - 256 if x > 127 else x


def ref_mul32(a, b):
    ka, sa, va = F.f32_val(a)
    kb, sb, vb = F.f32_val(b)
    if "nan" in (ka, kb):
        return F.QNAN
    if ka == "inf" or kb == "inf":
        if ka == "zero" or kb == "zero":
            return F.QNAN
        return ((sa ^ sb) << 31) | 0x7F800000
    p = va * vb
    if p == 0:
        return (sa ^ sb) << 31
    return F.round_f32(p, "rne")


def ref16(a, b, c, mul):
    ops = [F.f16_val(a >> 16)[0], F.f16_val(a & 0xFFFF)[0], F.f16_val(b >> 16)[0], F.f16_val(b & 0xFFFF)[0]]
    if not mul:
        ops.append(F.f32_val(c)[0])
    if "nan" in ops or "inf" in ops:
        return F.ref_fp16(a, b, 0 if mul else c)
    # a multiply has no C: -0 is the neutral term for the sign of a sum of zeros
    return M.model(a, b, 0x80000000 if mul else c, 3)


class Replay:
    """The RTL's order and zero gate, in software."""

    def __init__(self, fmt, A, B, C0):
        self.fmt, self.A, self.B = fmt, A, B
        self.C = [row[:] for row in C0]
        self.valid = 0

    def op(self, first):
        A, B, C, fmt = self.A, self.B, self.C, self.fmt
        if fmt == "int8":
            for p in range(16):
                mul = first and p == 0
                for i in range(16):
                    aw = A[i][p]
                    for l in range(8):
                        gate = (aw == 0) or (B[p][l] == 0 and B[p][l + 8] == 0)
                        for s in (l, l + 8):
                            if mul or not gate:
                                self.valid += 1
                                x = sum(s8(aw, e) * s8(B[p][s], e) for e in range(4))
                                C[i][s] = (x + (0 if mul else C[i][s])) & 0xFFFFFFFF
            return
        for k in range(16):
            mul = first and k == 0
            for i in range(16):
                aw = A[i][k]
                for h in range(2):
                    for l in range(8):
                        j = 8 * h + l
                        bw = B[k][j]
                        if mul:
                            self.valid += 1
                            C[i][j] = ref_mul32(aw, bw) if fmt == "fp32" else ref16(aw, bw, 0, True)
                        elif aw != 0 and bw != 0:
                            self.valid += 1
                            C[i][j] = F.ref_fp32(aw, bw, C[i][j]) if fmt == "fp32" else ref16(aw, bw, C[i][j], False)


def run_case(job):
    label, fmt, style, seed, ops, first, c0kind, a = job
    rng = random.Random(seed)
    words = [word(fmt, rng, style) for _ in range(512)]
    A = [words[16 * i:16 * i + 16] for i in range(16)]
    B = [words[256 + 16 * i:256 + 16 * i + 16] for i in range(16)]
    if style == "ones5":
        pass
    if c0kind == "five":
        c0 = 5 if fmt == "int8" else 0x40A00000
        C0 = [[c0] * 16 for _ in range(16)]
    elif c0kind == "random":
        C0 = [[(rng.getrandbits(32) if fmt == "int8" else fw(rng.gauss(0, 8))) for _ in range(16)] for _ in range(16)]
    else:
        C0 = [[0] * 16 for _ in range(16)]
    with tempfile.TemporaryDirectory() as d:
        hexf = os.path.join(d, "t.hex")
        with open(hexf, "w") as f:
            for w in words + [x for row in C0 for x in row]:
                f.write(f"{w:08x}\n")
        cmd = [a.bin, f"+tiles={hexf}", f"+fmt={fmt}", "+warm=0", f"+ops={ops}", f"+first={first}",
               f"+loadc={0 if c0kind == 'none' else 1}", "+printc=1", f"+verilator+coverage+file+{os.path.join(d, 'c.dat')}"]
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    got = collections.defaultdict(dict)
    acct = None
    for l in out.splitlines():
        if l.startswith("C "):
            _, op, i, j, v = l.split()
            got[int(op)][(int(i), int(j))] = int(v, 16)
        elif l.startswith("ACCT "):
            acct = json.loads(l[5:])
    rep = Replay(fmt, A, B, C0)
    tally = collections.Counter()
    ex = []
    for n in range(1, ops + 1):
        rep.op(first != 0 and n == 1)
        g = got.get(n, {})
        for i in range(16):
            for j in range(16):
                r, w = g.get((i, j)), rep.C[i][j]
                if r == w:
                    tally["exact"] += 1
                else:
                    # after a mismatch, follow the RTL so one difference is counted once
                    if r is not None:
                        rep.C[i][j] = r
                    tally["mismatch"] += 1
                    if len(ex) < 5:
                        ex.append({"op": n, "i": i, "j": j, "rtl": f"{r:08x}" if r is not None else None, "ref": f"{w:08x}"})
    valid_rtl = acct["tima_valid" if fmt == "int8" else "txfma_valid"]
    return {"label": label, "fmt": fmt, "style": style, "seed": seed, "ops": ops, "first": first, "c0": c0kind,
            "tally": dict(tally), "valid_slots_rtl": valid_rtl, "valid_slots_gate_rule": rep.valid,
            "cycles_per_op": acct["cycles"] / max(1, acct["ops"]), "examples": ex}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ops", type=int, default=4)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    jobs = []
    for fmt in ("fp32", "fp16", "int8"):
        for style in ("random", "range", "gated", "corners", "special"):
            if fmt == "int8" and style == "special":
                continue
            for s in range(1, a.seeds + 1):
                jobs.append((f"{fmt}-{style}-launch-{s}", fmt, style, 100 * s + 1, a.ops, 1, "none", a))
        for s in range(1, a.seeds + 1):
            jobs.append((f"{fmt}-random-allmadd-{s}", fmt, "random", 200 * s + 2, a.ops, 0, "random", a))
            jobs.append((f"{fmt}-gated-allmadd-{s}", fmt, "gated", 300 * s + 3, a.ops, 0, "random", a))
    with ThreadPoolExecutor(a.jobs) as ex:
        rows = list(ex.map(run_case, jobs))
    tot = collections.defaultdict(collections.Counter)
    bad_valid = 0
    for r in rows:
        for k, v in r["tally"].items():
            tot[r["fmt"]][k] += v
            tot[r["fmt"] + ":" + r["style"]][k] += v
        if r["valid_slots_rtl"] != r["valid_slots_gate_rule"]:
            bad_valid += 1
    summary = {"totals": {k: dict(v) for k, v in sorted(tot.items())}, "cases": len(rows),
               "cases_where_valid_slots_differ": bad_valid}
    json.dump({"summary": summary, "rows": rows}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    for r in rows:
        if r["tally"].get("mismatch") or r["valid_slots_rtl"] != r["valid_slots_gate_rule"]:
            print(r["label"], r["tally"], r["valid_slots_rtl"], r["valid_slots_gate_rule"], r["examples"][:2])


if __name__ == "__main__":
    main()
