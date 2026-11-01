#!/usr/bin/env python3
"""E104's desk check, on the fixed RTL bench (rtl-sim/fma_toggle_v2, core-et's whole vpu_top built with -fno-dfg). Standard library only, so it runs
where the bench is built. Nothing here opens a card.

    desk_e104.py --bin obj_vpu/Vtb --unit obj_unit/Vtb --accum ./accum --tiles <dir with tiles/<type>/<kind>.bin> --out desk-e104.json [--jobs 8]

The question it answers before any card time: does the RTL's own accumulator do what E92's frozen reading says, or what the fault says?
Part A. One absorbed term and one zero term on an accumulator of 2^49, through the RTL's txfma_top (tb_unit.sv) and fp16_model.
Part B. A launch's real start: the first-pass op and the next ones, on vpu_top, from reset, against accum.c, all 256 words after every op.
Part C. The fault's own test: load C = fl((n-1) S), the sum E92's emulation assumes, at op index n, and let the RTL run ops. Frozen reading: every word
        moves only by its k-group-0 sum. Fault: the words that take a subtraction lose ulps. It prints what each column does, in ulps.
Part D. The same start from accum.c's sums at op index n: RTL against accum.c after 4 ops (mid-launch, all 256 words).
"""
import argparse
import json
import os
import struct
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction

MOVING_N = 199875


def words(path):
    raw = open(path, "rb").read()
    assert len(raw) == 2048, path
    return struct.unpack("<512I", raw)


def run_tb(a, ty, A_B, c0, first, ops, tag, d):
    """-> {op: {(i, j): word}} from +printc=1; op counts from 1."""
    hexf = os.path.join(d, f"{tag}.hex")
    with open(hexf, "w") as f:
        f.write("\n".join(f"{w:08x}" for w in tuple(A_B) + tuple(c0)) + "\n")
    cov = os.path.join(d, f"{tag}.cov")
    cmd = [a.bin, f"+tiles={hexf}", f"+fmt={ty}", f"+warm=0", f"+first={1 if first else 0}", f"+loadc={0 if first else 1}", f"+ops={ops}", "+printc=1", f"+verilator+coverage+file+{cov}"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    res = {}
    for l in out.splitlines():
        if l.startswith("C "):
            _, op, i, j, v = l.split()
            res.setdefault(int(op), {})[(int(i), int(j))] = int(v, 16)
    return res


def accum_at(a, ty, path, ns, d):
    subprocess.run([os.path.abspath(a.accum), ty, os.path.abspath(path)] + [str(n) for n in sorted(ns)], check=True, cwd=d)
    return {n: struct.unpack("<256I", open(os.path.join(d, f"accum_{n}.bin"), "rb").read()) for n in ns}


def f16v(h):
    s = -1 if h >> 15 else 1
    e = (h >> 10) & 31
    m = h & 0x3FF
    if e == 0:
        return Fraction(0)
    return s * Fraction(0x400 | m, 1 << 10) * Fraction(2) ** (e - 15)


def f32v(w):
    s = -1 if w >> 31 else 1
    e = (w >> 23) & 255
    m = w & 0x7FFFFF
    if e == 0:
        return Fraction(0)
    return s * Fraction(0x800000 | m, 1 << 23) * Fraction(2) ** (e - 127)


def to_f32(x):
    """fl(x): a Fraction to the nearest fp32, ties to even (what numpy's float64 -> float32 of an exact sum gives on these tiles)."""
    if x == 0:
        return 0
    s = 0x80000000 if x < 0 else 0
    x = abs(x)
    e = 0
    while x >= 2:
        x /= 2
        e += 1
    while x < 1:
        x *= 2
        e -= 1
    m = x * (1 << 23)
    q = int(m)
    r = m - q
    if r > Fraction(1, 2) or (r == Fraction(1, 2) and q & 1):
        q += 1
    if q == 1 << 24:
        q >>= 1
        e += 1
    return s | ((e + 127) << 23) | (q & 0x7FFFFF)


def per_op_sum(ty, w):
    """S[i][j], exact, as make_e88.per_op_sum computes it: words with a zero raw A or B word are gated."""
    A, B = w[:256], w[256:]
    S = []
    for i in range(16):
        for j in range(16):
            t = Fraction(0)
            for k in range(16):
                aw, bw = A[i * 16 + k], B[k * 16 + j]
                if aw == 0 or bw == 0:
                    continue
                if ty == "fp32":
                    t += f32v(aw) * f32v(bw)
                else:
                    t += f16v(aw >> 16) * f16v(bw >> 16) + f16v(aw & 0xFFFF) * f16v(bw & 0xFFFF)
            S.append(t)
    return S


def ulps(a, b):
    """signed-magnitude distance in ulps of the larger word's binade, from a to b."""
    if a == b:
        return 0
    sign = -1 if (a >> 31) else 1
    ia = a & 0x7FFFFFFF
    ib = b & 0x7FFFFFFF
    if (a >> 31) != (b >> 31):
        return None
    return sign * (ib - ia)


def part_a(a):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(a.model)))
    import fp16_model as fm
    c = 0x58000000
    cases = [("(1,1) x (1,1): both add", 0x3C003C00, 0x3C003C00), ("(1,1) x (-1,-1): both subtract", 0x3C003C00, 0xBC00BC00),
             ("(1,1) x (lo 1, hi -1): high subtracts", 0x3C003C00, 0xBC003C00), ("(1,1) x (lo -1, hi 1): low subtracts", 0x3C003C00, 0x3C00BC00),
             ("(-0,-0) x (1,1): zero products, both eff_sub set", 0x80008000, 0x3C003C00), ("(-0,-0) x (-1,-1): zero products, both add", 0x80008000, 0xBC00BC00),
             ("(1,1) x (lo 1, hi -1) on a small C: the products cancel", 0x3C003C00, 0xBC003C00)]
    cs = [c] * 6 + [0x4B000000]
    with tempfile.TemporaryDirectory() as td:
        hexf = os.path.join(td, "vec.hex")
        with open(hexf, "w") as f:
            for (_, x, y), cc in zip(cases, cs):
                f.write(f"{x:08x}\n{y:08x}\n{cc:08x}\n")
        out = subprocess.run([a.unit, f"+vec={hexf}", f"+n={len(cases)}", "+fmt=fp16"], capture_output=True, text=True, check=True).stdout
    rtl = {int(l.split()[1]): int(l.split()[2], 16) for l in out.splitlines() if l.startswith("R ")}
    res = []
    for i, ((name, x, y), cc) in enumerate(zip(cases, cs)):
        m = fm.model(x, y, cc)
        res.append({"case": name, "c": f"0x{cc:08x}", "model": f"0x{m:08x}", "rtl": f"0x{rtl[i]:08x}", "rtl_ulps": rtl[i] - cc})
        print(f"A  {name:58s} C 0x{cc:08x} -> RTL 0x{rtl[i]:08x} ({rtl[i] - cc:+d} ulp), fp16_model 0x{m:08x}", flush=True)
    # the same on fp32: a -0 product, and an absorbed subtraction past the zap limit
    cases32 = [("1 x 1 on 2^100: adds", 0x3F800000, 0x3F800000), ("1 x -1 on 2^100: absorbed subtract, RNE", 0x3F800000, 0xBF800000), ("-0 x 1 on 2^100: zero product, eff_sub set", 0x80000000, 0x3F800000), ("-0 x -1 on 2^100: zero product, adds", 0x80000000, 0xBF800000)]
    c32 = 0x71800000
    with tempfile.TemporaryDirectory() as td:
        hexf = os.path.join(td, "vec.hex")
        with open(hexf, "w") as f:
            for _, x, y in cases32:
                f.write(f"{x:08x}\n{y:08x}\n{c32:08x}\n")
        out = subprocess.run([a.unit, f"+vec={hexf}", f"+n={len(cases32)}", "+fmt=fp32"], capture_output=True, text=True, check=True).stdout
    rtl = {int(l.split()[1]): int(l.split()[2], 16) for l in out.splitlines() if l.startswith("R ")}
    for i, (name, x, y) in enumerate(cases32):
        res.append({"case": "fp32 " + name, "c": f"0x{c32:08x}", "rtl": f"0x{rtl[i]:08x}", "rtl_ulps": rtl[i] - c32})
        print(f"A  fp32 {name:53s} C 0x{c32:08x} -> RTL 0x{rtl[i]:08x} ({rtl[i] - c32:+d} ulp)", flush=True)
    return res


def job(args):
    a, ty, kind, path = args
    w = words(path)
    S = per_op_sum(ty, w)
    res = {"tile": f"{ty}.{kind}"}
    with tempfile.TemporaryDirectory(dir=a.tmp) as d:
        # B: a launch's real start
        ops = a.start_ops
        tb = run_tb(a, ty, w, [0] * 256, True, ops, "b", d)
        acc = accum_at(a, ty, path, list(range(1, ops + 1)), d)
        miss = {n: sum(1 for i in range(16) for j in range(16) if tb[n][(i, j)] != acc[n][16 * i + j]) for n in acc}
        res["start_ops"] = ops
        res["start_mismatch_words"] = sum(miss.values())
        # C: from the emulation's C = fl((n-1) S)
        n = MOVING_N
        c0 = [to_f32(s * (n - 1)) for s in S]
        tc = run_tb(a, ty, w, c0, False, 4, "c", d)
        fl_after = [[to_f32(s * (n - 1 + o)) for s in S] for o in range(1, 5)]
        moved_vs_fl = [sum(1 for i in range(16) for j in range(16) if tc[o + 1][(i, j)] != fl_after[o][16 * i + j]) for o in range(4)]
        res["from_fl_words_off_fl_after_op"] = moved_vs_fl
        res["from_fl_ulps_c00"] = [ulps(fl_after[o][0], tc[o + 1][(0, 0)]) for o in range(4)]
        res["from_fl_ulps_c08"] = [ulps(fl_after[o][8], tc[o + 1][(0, 8)]) for o in range(4)]
        # D: from accum.c's sums at the same op index
        acc2 = accum_at(a, ty, path, [n - 1] + [n - 1 + o for o in range(1, 5)], d)
        td_ = run_tb(a, ty, w, acc2[n - 1], False, 4, "d", d)
        res["from_real_mismatch_after_op"] = [sum(1 for i in range(16) for j in range(16) if td_[o][(i, j)] != acc2[n - 1 + o][16 * i + j]) for o in range(1, 5)]
        res["real_words_off_fl_at_n"] = sum(1 for x, y in zip(acc2[n - 1], c0) if x != y)
        res["real_c00"] = acc2[n - 1][0]
        res["real_c08"] = acc2[n - 1][8]
        res["fl_c00"] = c0[0]
        res["fl_c08"] = c0[8]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--unit", required=True)
    ap.add_argument("--accum", required=True)
    ap.add_argument("--model", required=True, help="path of fp16_model.py")
    ap.add_argument("--tiles", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--start-ops", type=int, default=6)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--tmp", default=None)
    a = ap.parse_args()
    res = {"_bench": "rtl-sim/fma_toggle_v2 (vpu_top, -fno-dfg)", "part_a": part_a(a), "tiles": {}}
    only = set(x for x in a.only.split(",") if x)
    work = []
    for ty in ("fp16", "fp32"):
        d = os.path.join(a.tiles, ty)
        for f in sorted(os.listdir(d)):
            if f.endswith(".bin") and (not only or f"{ty}.{f[:-4]}" in only):
                work.append((a, ty, f[:-4], os.path.join(d, f)))
    with ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(job, work):
            res["tiles"][r["tile"]] = r
            print(f"{r['tile']:14s} start: {r['start_mismatch_words']:4d} of {r['start_ops'] * 256} words off accum | from fl: words off fl after op 1-4 {r['from_fl_words_off_fl_after_op']} "
                  f"C[0][0] ulps {r['from_fl_ulps_c00']} C[0][8] ulps {r['from_fl_ulps_c08']} | from real: off accum {r['from_real_mismatch_after_op']} | real != fl at n: {r['real_words_off_fl_at_n']} words", flush=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
