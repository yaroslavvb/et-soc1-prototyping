#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""The size of a fault E102 found in make_e88.simulate and make_e92.sign_counts, on every float tile E88's fit and items, E90 and E92 rest on, and on E102's own all-in list. Desk compute; nothing opens a card. Run from the repo's root (FAULT_WORKERS sets the pool; the committed output ran on the mini with 8); output fault_fl_ns_e102.txt.

Both tools start an op from C = fl((n-1) S), S the exact sum of one op's products: the accumulator a launch would hold if it never rounded until the end. Their docstrings say that is exact for integer and absorbed designs. On any other tile a real
accumulation rounds at every step: a product is added to a sum and only the bits the sum still holds survive. So a real C is not fl((n-1) S). This compares, tile by tile, through one code path at the same op indices, the counts from that start with the counts from the
real sum (accum.c: the bench's own accumulators, FMADD with round-to-nearest-even in the RTL's order, the zero gate included), and those parts of the model in watts on the same coefficients: E88's frozen b per result-bus bit plus E92's frozen f per flop bit.

A first version compared simulate's count (gated, 16 op indices) with make_e102.exact_counts's (ungated, 4 op indices) and read +2.6 W on nn_like. That was the gate and the sample, not the start; it was corrected before anything cited it, and parts 2 and 3 of the output give each its own size."""
import hashlib
import json
import os
import struct
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "tools", "claims-v3", "rpath"), os.path.join(ROOT, "tools", "claims-v3", "hlp")]
import make_e102 as m102  # noqa: E402

K = "tools/claims-v3/kinds/"
R = "tools/claims-v3/rpath/"


def tiles():
    """Every float tile the three experiments rest on, found by each one's own folder and deduplicated by content: (name, path, who)."""
    e88 = json.load(open(os.path.join(ROOT, R, "e88.json")))
    e90 = json.load(open(os.path.join(ROOT, K, "e90", "e90.json")))["tiles"]
    e92 = json.load(open(os.path.join(ROOT, K, "e92", "e92.json")))["tiles"]
    src = [("E92", K + "e92/tiles/", e92), ("E90", K + "e90/tiles/", e90), ("E88 items", R + "tiles/", e88["items"]),
           ("E88 fit", K + "tiles/", [i["name"] for ty in ("fp32", "fp16") for i in e88["fit"][ty]["inputs"]])]
    seen, missing = {}, []
    for who, folder, names in src:
        for name in names:
            ty, kind = name.split(".", 1)
            if ty == "int8":          # integer sums: nothing rounds
                continue
            path = f"{folder}{ty}/{kind}.bin"
            full = os.path.join(ROOT, path)
            if not os.path.exists(full):
                missing.append(f"{who}: {name}")
                continue
            h = hashlib.sha256(open(full, "rb").read()).hexdigest()
            if h in seen:
                seen[h]["who"].append(who)
            else:
                seen[h] = {"name": name, "path": path, "who": [who]}
    return [(v["name"], v["path"], ", ".join(dict.fromkeys(v["who"]))) for v in seen.values()], missing


def counts(ty, raw, start, accum, launch=None, samples=None, step=None, ns=None):
    """The C read, result bus, store and adder-flop counts of make_e88.simulate and make_e92.sign_counts, by lane, gate included, at FLOP_SAMPLES op indices spread over make_e88's launch, from one start: "fl" C = fl((n-1) S), or "real" the sum accum.c
    reaches. One code path, so the difference between the two columns is the start and nothing else. The two counted ops add as make_e88 does, in ordinary rounding, unless `step` gives the arithmetic to use instead (fault_e92_fp16_e102.py prints what that changes in fp16)."""
    import subprocess
    import tempfile
    import make_e88 as me
    import make_e92 as m92
    aw, bw = me.words_from_tile(raw)
    A, B = me.elements(ty, aw, bw)
    seq = me.stream(ty)
    launch = launch or me.LAUNCH_OPS[ty]
    samples = samples or m92.FLOP_SAMPLES
    ns = ns or [max(2, int((s_ + 0.5) / samples * launch)) for s_ in range(samples)]
    samples = len(ns)
    dp = m92.dp_fp32 if ty == "fp32" else m92.dp_fp16
    states = {}
    if start == "real":
        with tempfile.TemporaryDirectory() as td:
            tile = os.path.join(td, "t.bin")
            open(tile, "wb").write(raw)
            subprocess.run([accum, ty, tile] + [str(n - 1) for n in ns], check=True, cwd=td)
            for n in ns:
                states[n] = np.frombuffer(open(os.path.join(td, f"accum_{n - 1}.bin"), "rb").read(), dtype="<u4").reshape(16, 16).copy().view(np.float32)
    else:
        S = me.per_op_sum(ty, A, B)
        for n in ns:
            states[n] = me.fl(ty, (n - 1) * S).astype(np.float32)
    keys = ("cbus", "rbus", "store", "csa3", "csa2", "comb_s", "comb_c", "comb_add", "alt", "other")
    tot = dict.fromkeys(keys, 0.0)
    for n in ns:
        C = states[n].copy()
        prev = [None] * 8
        for op in (0, 1):
            for (k, i, cols) in seq:
                live = me.gate_live(ty, aw, bw, k, i, cols)
                for lane, j in enumerate(cols):
                    if not live[lane]:
                        continue
                    cw = m92.f32_words(C[i, j])
                    e1, e2, csa3, csa2, cs, cc, ca, oth = dp(cw, aw[i, k], bw[k, j])
                    pr = float(A[i, k]) * float(B[k, j]) if ty == "fp32" else float((A[i, k] * B[k, j]).sum())
                    if step:
                        rw = int(step(int(aw[i, k]), int(bw[k, j]), int(cw)))
                        r = np.frombuffer(struct.pack("<I", rw), dtype="<f4")[0]
                    else:
                        r = np.float32(float(C[i, j]) + pr)
                        rw = int(m92.f32_words(r))
                    cwi = int(cw)
                    now = dict(e1=e1, e2=e2, csa3=csa3, csa2=csa2, cs=cs, cc=cc, ca=ca, c=cwi, r=rw)
                    if op == 1:
                        tot["store"] += bin(rw ^ cwi).count("1")
                        q = prev[lane]
                        if q is not None:
                            tot["cbus"] += bin(cwi ^ q["c"]).count("1")
                            tot["rbus"] += bin(rw ^ q["r"]).count("1")
                            tot["csa3"] += bin(csa3 ^ q["csa3"]).count("1")
                            tot["csa2"] += bin(csa2 ^ q["csa2"]).count("1")
                            tot["comb_s"] += bin(cs ^ q["cs"]).count("1")
                            tot["comb_c"] += bin(cc ^ q["cc"]).count("1")
                            tot["comb_add"] += bin(ca ^ q["ca"]).count("1")
                            tot["alt"] += (e1 != q["e1"]) + (e2 != q["e2"])
                            tot["other"] += oth
                    prev[lane] = now
                    C[i, j] = r
    res = {k: v / samples for k, v in tot.items()}
    return {"res": res["cbus"] + res["rbus"] + res["store"], "cbus": res["cbus"], "flops": res["csa3"] + res["csa2"] + res["comb_s"] + res["comb_c"] + res["comb_add"], "alt": res["alt"], "other_frac": res["other"] / 4096.0}


def job(a):
    name, path, who, accum = a
    raw = open(os.path.join(ROOT, path), "rb").read()
    ty = name.split(".")[0]
    return name, who, ty, counts(ty, raw, "fl", accum), counts(ty, raw, "real", accum)


def sample_job(path):
    """make_e88.simulate's result-bus count of one tile at its own 16 op indices and at 4, at each of the two launch lengths in the repo (make_e88's and make_e92's)."""
    import make_e88 as me
    import make_e92 as m92
    aw, bw = me.words_from_tile(open(os.path.join(ROOT, path), "rb").read())
    out = {}
    for launch in (me.LAUNCH_OPS["fp32"], m92.LAUNCH_OPS):
        for samples in (16, 4):
            out[f"{launch}/{samples}"] = me.simulate("fp32", aw, bw, launch_ops=launch, samples=samples)["res_bits_per_op"]
    return path, out


def gate_job(path):
    """make_e92.sign_counts as shipped (it ignores the zero gate) on a tile with zero words: its flops at make_e88's launch."""
    import make_e88 as me
    import make_e92 as m92
    ty = path.split("/")[-2]
    aw, bw = me.words_from_tile(open(os.path.join(ROOT, path), "rb").read())
    c, _ = m92.sign_counts(ty, aw, bw, launch_ops=me.LAUNCH_OPS[ty])
    return path, c["flops"]


def main():
    accum = m102.accum_binary()
    fit = json.load(open(os.path.join(ROOT, R, "e88.json")))["fit"]
    f_w = json.load(open(os.path.join(ROOT, K, "predictions-e92.json")))["models"]["f_w_per_flop_bit_per_op"]
    rows, missing = tiles()
    bj = (0, 6, 11, 16, 20, 22)
    e102 = [(f"fp32.{n}", f"{K}e102/tiles/fp32/{n}.bin", "E102", accum) for n in ["hq"] + [f"bj_{j}" for j in bj]]
    with ProcessPoolExecutor(int(os.environ.get("FAULT_WORKERS", "3"))) as ex:
        print("Part 1. E102's all-in fp32 B list over its zero, through the same code path as part 4: the near-identical operands where the start overcounts.", flush=True)
        got = {r[0]: r for r in ex.map(job, e102)}
        z = got["fp32.hq"]
        coef = fit["fp32"]["coef"]
        e65 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json")))["cards"]["aifoundry3"]["bits"]
        for j in bj:
            e = got[f"fp32.bj_{j}"]
            rf, rr = e[3]["res"] - z[3]["res"], e[4]["res"] - z[4]["res"]
            ff, fr = e[3]["flops"] - z[3]["flops"], e[4]["flops"] - z[4]["flops"]
            print(f"  bit {j:2d}: res bits fl {rf:7.0f}, real {rr:7.0f}; flops fl {ff:7.0f}, real {fr:7.0f}; those parts of the model, fl {coef[3] * rf + f_w * ff:5.2f} W, real {coef[3] * rr + f_w * fr:5.2f} W; E65 measured the whole step at {e65[str(j)]['dW']:.2f} W", flush=True)
        print("\nPart 2. make_e88.simulate's result-bus count on E92's integer-sum tiles, the same start, by launch length and how many op indices it samples: the sample alone moves it.", flush=True)
        for path, out in ex.map(sample_job, (K + "e92/tiles/fp32/w_h_sub.bin", K + "e92/tiles/fp32/w_h_add.bin", K + "e92/tiles/fp32/wr_h_sub.bin", K + "e92/tiles/fp32/wr_h_add.bin")):
            print(f"  {os.path.basename(path)[:-4]:10s} " + "  ".join(f"launch/samples {k}: {v:9.1f}" for k, v in out.items()), flush=True)
        print("\nPart 3. make_e92.sign_counts as shipped ignores the zero gate; its flops on two tiles with zero words (part 4's fl column is the same start with the gate).", flush=True)
        for path, flops in ex.map(gate_job, (K + "tiles/fp32/nn_like.bin", K + "tiles/fp16/nn_like.bin")):
            print(f"  {path.split('/')[-2]}.{os.path.basename(path)[:-4]}: {flops:9.0f}", flush=True)
        print(f"\nPart 4. {len(rows)} float tiles, every one E88's fit and items, E90 and E92 rest on, deduplicated by content. Per op, at four op indices over make_e88's launch, gate included, one code path (fl: C = fl((n-1) S); real: accum.c). res = C read + result bus + store. watts: E88's b x res + E92's f x flops, which is the part of the model the start moves.", flush=True)
        if missing:
            print("  no file for: " + "; ".join(missing), flush=True)
        print(f"{'tile':26s} {'res fl':>8s} {'res real':>8s} {'flops fl':>8s} {'flops real':>10s} {'model W fl':>10s} {'model W real':>12s} {'moved W':>8s}  who rests on it", flush=True)
        for name, who, ty, fl_, re_ in ex.map(job, [(n, p, w, accum) for n, p, w in rows]):
            coef = fit[ty]["coef"]
            res_f, res_r = fl_["res"], re_["res"]
            fl_f, fl_r = fl_["flops"], re_["flops"]
            wf = coef[3] * res_f + f_w * fl_f
            wr = coef[3] * res_r + f_w * fl_r
            print(f"{name:26s} {res_f:8.0f} {res_r:8.0f} {fl_f:8.0f} {fl_r:10.0f} {wf:10.2f} {wr:12.2f} {wr - wf:+8.2f}  {who}", flush=True)


if __name__ == "__main__":
    main()
