#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Desk compute behind E102's corrections after verification; nothing opens a card. Run from the repo's root; writes corrections-counts.json beside this file, which corrections-check.py reads. FAULT_WORKERS sets the pool (the committed file ran on the mini with 8).

For E92's 34 fp16 fit tiles (posthoc-fit.json's list and D) and E86's three real fp16 tiles, the counts by fault_fl_ns_e102.counts over make_e92's launch of 542,000 ops: from the start C = fl((n-1) S) ("start"), from accum.c's sums ("real"), and from accum.c's sums with
fp16_model.model in the two counted ops as well ("rtl"), at 4 and 16 op indices. For every fp16 tile of fault_fl_ns_e102.tiles(), "rtl" at make_e88's launch of 533,000 and 4 indices, beside that file's table. The words each reading holds at n = 2, 16, 1,000: the start, accum.c
(the RTL's window), and this file's own emulator of the manual's sentence (PRM 9.3.3, TensorFMA16A32: "added with no intermediate rounding. The final sum is calculated using round towards zero"): the exact three-way sum, truncated once. make_e88.emulate_launch's words at n = 2, which make_e92.self_check read as proof of the freeze."""
import json
import os
import struct
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
RP = os.path.join(ROOT, "tools", "claims-v3", "rpath")
sys.path[:0] = [K, RP, os.path.join(ROOT, "tools", "claims-v3", "hlp"), os.path.join(ROOT, "rtl-sim", "fma_toggle_v2")]
import fault_fl_ns_e102 as ff      # noqa: E402
import fp16_model as fm            # noqa: E402
import make_e102 as m102           # noqa: E402
import make_e88 as me              # noqa: E402
import make_e92 as m92             # noqa: E402

D = os.path.join(ROOT, "docs", "reports", "data")


def fit_row(a):
    path, arm, samples, accum = a
    raw = open(path, "rb").read()
    aw, bw = me.words_from_tile(raw)
    sim = me.simulate("fp16", aw, bw, launch_ops=m92.LAUNCH_OPS)
    bus, _, _ = me.bus_bits("fp16", aw, bw)
    c = ff.counts("fp16", raw, "fl" if arm == "start" else "real", accum, launch=m92.LAUNCH_OPS, samples=samples, step=fm.model if arm == "rtl" else None)
    return {"live": sim["live_frac"], "bus": bus, "prod": sim["prod"], "res": c["res"], "alt": c["alt"], "flops": c["flops"]}


def rtl_row(a):
    path, accum = a
    c = ff.counts("fp16", open(path, "rb").read(), "real", accum, step=fm.model)
    return {"res": c["res"], "flops": c["flops"]}


def one_index(a):
    path, n, launch, accum = a
    return ff.counts("fp16", open(path, "rb").read(), "real", accum, launch=launch, ns=[n])["res"]


def rtl128(a):
    path, accum = a
    return ff.counts("fp16", open(path, "rb").read(), "real", accum, launch=m92.LAUNCH_OPS, samples=128, step=fm.model)["res"]


def prod(a, b):
    """One fp16 product as an integer with LSB 2^-64; denormals read as zero."""
    s = ((a ^ b) >> 15) & 1
    ea, eb = (a >> 10) & 31, (b >> 10) & 31
    if not ea or not eb:
        return 0
    v = ((0x400 | (a & 0x3FF)) * (0x400 | (b & 0x3FF))) << (ea + eb + 14)
    return -v if s else v


def step(c, p):
    """C' = the exact C + p, truncated toward zero to fp32; denormal results flushed."""
    e = (c >> 23) & 0xFF
    v = 0
    if e:
        sh = e - 86
        m = 0x800000 | (c & 0x7FFFFF)
        v = m << sh if sh >= 0 else m >> -sh
        if c >> 31:
            v = -v
    v += p
    if v == 0:
        return 0
    s = 1 if v < 0 else 0
    a = -v if s else v
    msb = a.bit_length() - 1
    be = msb - 64 + 127
    if be <= 0:
        return s << 31
    if be >= 255:
        return (s << 31) | 0x7F7FFFFF
    mant = a >> (msb - 23) if msb >= 23 else a << (23 - msb)
    return (s << 31) | (be << 23) | (mant & 0x7FFFFF)


def words(a):
    """The words each reading holds at each n: [C00, C08, distinct words]."""
    name, path, ns, accum = a
    raw = open(path, "rb").read()
    w = struct.unpack("<512I", raw)
    A = [w[i * 16:i * 16 + 16] for i in range(16)]
    B = [w[256 + i * 16:256 + i * 16 + 16] for i in range(16)]
    P = [[[prod(A[i][k] >> 16, B[k][j] >> 16) + prod(A[i][k] & 0xFFFF, B[k][j] & 0xFFFF) for j in range(16)] for i in range(16)] for k in range(16)]
    G = [[[A[i][k] == 0 or B[k][j] == 0 for j in range(16)] for i in range(16)] for k in range(16)]
    C = [[0] * 16 for _ in range(16)]
    man = {}
    for op in range(max(ns) + 1):
        if op in ns:
            flat = [x for r in C for x in r]
            man[op] = [C[0][0], C[0][8], len(set(flat))]
        if op == max(ns):
            break
        for k in range(16):
            for i in range(16):
                ci, pk, gk = C[i], P[k][i], G[k][i]
                if op == 0 and k == 0:
                    for j in range(16):
                        ci[j] = step(0, pk[j])
                else:
                    for j in range(16):
                        if not gk[j]:
                            ci[j] = step(ci[j], pk[j])
    aw, bw = me.words_from_tile(raw)
    AA, BB = me.elements("fp16", aw, bw)
    S = me.per_op_sum("fp16", AA, BB)
    out = {}
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([accum, "fp16", path] + [str(n) for n in ns], check=True, cwd=td)
        for n in ns:
            c = struct.unpack("<256I", open(os.path.join(td, f"accum_{n}.bin"), "rb").read())
            fl = me.fl("fp16", n * S).astype(np.float32).view(np.uint32)
            out[str(n)] = {"start": [int(fl[0, 0]), int(fl[0, 8]), len(np.unique(fl))], "manual": man[n], "accum": [c[0], c[8], len(set(c))]}
    hist = me.emulate_launch("fp16", aw, bw, 4)[1].astype(np.float32).view(np.uint32)
    return name, out, [int(hist[0, 0]), int(hist[0, 8]), len(np.unique(hist))]


def late(a):
    name, path, n, accum = a
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([accum, "fp16", path, str(n)], check=True, cwd=td)
        c = struct.unpack("<256I", open(os.path.join(td, f"accum_{n}.bin"), "rb").read())
    return name, [c[0], c[8], len(set(c))]


def main():
    accum = m102.accum_binary()
    pf = json.load(open(os.path.join(D, "2026-11-01-e92-sign-split", "posthoc-fit.json")))["tiles"]["fp16"]
    e92 = json.load(open(os.path.join(K, "e92", "e92.json")))["tiles"]
    e90 = json.load(open(os.path.join(K, "e90", "e90.json")))["tiles"]
    kinds = json.load(open(os.path.join(K, "kinds.json")))["kinds"]["fp16"]

    def path_of(name):
        if name in e92:
            return os.path.join(K, "e92", e92[name]["file"])
        if name in e90:
            return os.path.join(K, "e90", e90[name]["file"])
        return os.path.join(K, kinds[name.split(".", 1)[1]]["file"])

    names = [r["name"] for r in pf]
    e86 = json.load(open(os.path.join(D, "2026-10-31-e86-real-tensors-energy", "e86.json")))["items"]
    held = {n: os.path.join(K, "real", "tiles", "fp16", n.split("real_", 1)[1] + ".bin") for n in e86 if n.startswith("fp16.real_")}
    out = {"label": "desk compute, post hoc; corrections-check.py reads it", "launch_fit": m92.LAUNCH_OPS, "launch_table": me.LAUNCH_OPS["fp16"],
           "fit_D": {r["name"]: {"D": r["D"], "session": r["session"]} for r in pf}, "e86_D": {n: e86[n]["D"]["mean"] for n in held}}
    arms = (("start", 4), ("real", 4), ("start", 16), ("real", 16), ("rtl", 16))
    with ProcessPoolExecutor(int(os.environ.get("FAULT_WORKERS", "3"))) as ex:
        jobs = [(path_of(n), a, s, accum) for a, s in arms for n in names]
        got = list(ex.map(fit_row, jobs))
        i = 0
        out["fit"] = {}
        for a, s in arms:
            out["fit"][f"{a}{s}"] = dict(zip(names, got[i:i + len(names)]))
            i += len(names)
        print("fit done", flush=True)
        hn = sorted(held)
        got = list(ex.map(fit_row, [(held[n], a, s, accum) for a, s in arms for n in hn]))
        i = 0
        out["e86"] = {}
        for a, s in arms:
            out["e86"][f"{a}{s}"] = dict(zip(hn, got[i:i + len(hn)]))
            i += len(hn)
        print("e86 done", flush=True)
        rows = [(n, os.path.join(ROOT, p)) for n, p, _ in ff.tiles()[0] if n.startswith("fp16.")]
        out["table_rtl"] = dict(zip([n for n, _ in rows], ex.map(rtl_row, [(p, accum) for _, p in rows])))
        print("table done", flush=True)
        hs = os.path.join(K, "e92", "tiles", "fp16", "h_sub.bin")
        grids = {"533000/4": (533000, 4), "542000/4": (542000, 4), "542000/16": (542000, 16)}
        out["h_sub_by_index"] = {}
        for g, (la, s) in grids.items():
            ns = [max(2, int((x + 0.5) / s * la)) for x in range(s)]
            out["h_sub_by_index"][g] = dict(zip([str(n) for n in ns], ex.map(one_index, [(hs, n, la, accum) for n in ns])))
        out["h_sub_rtl_128"] = list(ex.map(rtl128, [(hs, accum)]))[0]
        print("spread done", flush=True)
        ws = [(t, os.path.join(K, "e92", "tiles", "fp16", t + ".bin")) for t in ("c_abs", "h_add", "h_allsub", "h_sub", "c_alt", "hh_sub", "hl_sub", "s_abs")] + [("r_abs", os.path.join(RP, "tiles", "fp16", "r_abs.bin")), ("r_cancel", os.path.join(RP, "tiles", "fp16", "r_cancel.bin"))]
        got = list(ex.map(words, [(t, p, [2, 16, 1000], accum) for t, p in ws]))
        out["words"] = {t: o for t, o, _ in got}
        out["emulate_launch_n2"] = {t: h for t, _, h in got}
        out["late_541999"] = dict(ex.map(late, [(t, p, 541999, accum) for t, p in ws]))
    json.dump(out, open(os.path.join(HERE, "corrections-counts.json"), "w"), indent=0)
    print("written", flush=True)


if __name__ == "__main__":
    main()
