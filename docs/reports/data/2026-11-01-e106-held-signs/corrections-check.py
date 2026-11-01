#!/usr/bin/env python3
"""E106: the desk check behind "Corrections after verification": every number they cite, from committed files, standard library only. Run it in this directory.

    python3 corrections-check.py > corrections-check.txt

Sections are named for the corrections they back. Nothing here is a registered test; no rule, verdict or frozen file depends on it. The "bench" is the fixed RTL bench's counts, modelled, not measured. Everything marked post hoc was chosen after the data.
"""
import collections
import gzip
import json
import math
import os
import statistics
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K = os.path.join(ROOT, "tools/claims-v3/kinds")
E104D = os.path.join(DATA, "2026-11-01-e104-c-readback")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
KLEAK = 0.2414
PASSES = ("10610", "10611", "10612")
P = json.load(open(os.path.join(HERE, "e106.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
E104 = json.load(open(os.path.join(E104D, "e104.json")))
E104G = json.load(open(os.path.join(E104D, "e104-gatesoff.json")))
PRED104 = json.load(open(os.path.join(K, "predictions-e104.json")))
PRED = json.load(open(os.path.join(K, "predictions-e106.json")))
SPEC = json.load(open(os.path.join(K, "e106", "e106.json")))
rows = {}
for f in ("2026-11-01-q132-rtl-bench/counts-v2.json", "2026-11-01-q132-rtl-bench/counts-e92.json", "2026-11-01-e104-c-readback/desk/counts-e104.json", "2026-11-01-e104-c-readback/desk/counts-e104b.json", "2026-11-01-e106-held-signs/desk/counts-e106.json"):
    rows.update(json.load(open(os.path.join(DATA, f)))["rows"])


def mci(v):
    v = list(v)
    if len(v) < 2:
        return (v[0] if v else float("nan")), float("nan"), len(v)
    return sum(v) / len(v), T975[len(v) - 1] * statistics.stdev(v) / math.sqrt(len(v)), len(v)


def pp(res, plus, minus, key="D"):
    out = {}
    for p, it in sorted(res["per_pass"].items()):
        if all(n in it and it[n].get(key) is not None for n in list(plus) + list(minus)):
            out[p] = sum(it[n][key] for n in plus) - sum(it[n][key] for n in minus)
    return out


def show(lab, v):
    m, h, n = mci(v)
    print(f"  {lab:62s} {m:7.3f} ± {h:6.3f} (n={n})")
    return m, h


step32, step16 = pp(P, ["fp32.signs"], ["fp32.ones"]), pp(P, ["fp16.signs"], ["fp16.ones"])
hz, hx, h32 = pp(P, ["fp16.z_ss"], ["fp16.c_abs"]), pp(P, ["fp16.x_s"], ["fp16.x_c"]), pp(P, ["fp32.s_abs"], ["fp32.c_abs"])
GROUPS = (
    ("front", ("txfma_f0", "txfma_f1", "txfma_f2", "txfma_c0", "txfma_c1", "txfma_c2", "txfma_c3", "txfmaexp_top", "txfmactl_top", "txfmafrac_top", "txfma_top")),
    ("aligner, CSA", ("txfma_f3", "txfma_lxd", "txfma_csa")),
    ("adder", ("txfma_adder", "txfma_trz2", "txfma_f4", "txfma_frac_zero_detect")),
    ("normaliser, rounding", ("txfma_f5", "txfma_norm_shf", "txfma_c4", "txfma_c5", "txfma_rnd_adder", "txfma_f6", "txfma_e5")),
    ("lane, bypass, rf", ("vpu_lane", "vpu_bypass", "vpu_rf", "vpu_top", "vpu_ctrl", "vpu_tensorfma", "vpu_64x32_3r2w_vpurf", "vpu_ml", "rf_latch_1r_1w", "vpu_sh_sw", "vpu_trans", "vpu_txfma_trans_top", "trans_top")),
)
ALN = GROUPS[1][1]
ADD = GROUPS[2][1] + GROUPS[3][1]


def bl(n):
    return rows[n]["mean"]["by_block_cov"]


def dif(a, b):
    x, y = bl(a), bl(b)
    return {q: x.get(q, 0) - y.get(q, 0) for q in set(x) | set(y)}


s16, s32 = dif("fp16.signs", "fp16.ones"), dif("fp32.signs", "fp32.ones")

print("C1. A bracket, by the registration's own R5 row (E106.md: 'a LITTLE here ... would make the held part a bracket, not a number')")
show("fp16 (z_ss - c_abs) less (x_s - x_c), W, paired, each over its baseline", [hz[p] - hx[p] for p in hz])
show("fp16 z_ss - x_s, W, directly, baselines left in", pp(P, ["fp16.z_ss"], ["fp16.x_s"]).values())
print("  share of the step per pass: z_ss", [round(hz[p] / step16[p], 3) for p in hz], "x_s", [round(hx[p] / step16[p], 3) for p in hx], "z_ss / x_s", [round(hz[p] / hx[p], 2) for p in hz])
show("share difference, z_ss - x_s", [hz[p] / step16[p] - hx[p] / step16[p] for p in hz])
m1, h1, _ = mci(hx[p] / step16[p] for p in hx)
m2, h2, _ = mci(hz[p] / step16[p] for p in hz)
print(f"  outer interval of the two shares: {m1 - h1:.3f} to {m2 + h2:.3f}")
print("  The bench, net toggles an op over the tile's baseline, k (modelled)")
print(f"    {'contrast':19s}" + "".join(f"{g:>21s}" for g, _ in GROUPS) + f"{'other':>8s}{'all':>8s}{'of step':>9s}")
for lab, a, b, s in (
    ("fp16 signs-ones", "fp16.signs", "fp16.ones", s16),
    ("fp16 z_ss-c_abs", "fp16.z_ss", "fp16.c_abs", s16),
    ("fp16 x_s-x_c", "fp16.x_s", "fp16.x_c", s16),
    ("fp16 z_s-c_abs", "fp16.z_s", "fp16.c_abs", s16),
    ("fp32 signs-ones", "fp32.signs", "fp32.ones", s32),
    ("fp32 s_abs-c_abs", "fp32.s_abs", "fp32.c_abs", s32),
    ("fp32 z_s-c_abs", "fp32.z_s", "fp32.c_abs", s32),
):
    d = dif(a, b)
    g = [sum(d.get(q, 0) for q in n) / 1e3 for _, n in GROUPS]
    seen = {q for _, n in GROUPS for q in n}
    oth = sum(v for q, v in d.items() if q not in seen) / 1e3
    print(f"    {lab:19s}" + "".join(f"{x:21.0f}" for x in g) + f"{oth:8.0f}{sum(d.values()) / 1e3:8.0f}{sum(d.values()) / sum(s.values()):9.3f}")
for lab, a, b, s in (("fp16 z_ss", "fp16.z_ss", "fp16.c_abs", s16), ("fp16 x_s", "fp16.x_s", "fp16.x_c", s16), ("fp32 s_abs", "fp32.s_abs", "fp32.c_abs", s32), ("fp32 z_s", "fp32.z_s", "fp32.c_abs", s32)):
    H = dif(a, b)
    al, sal = sum(H.get(q, 0) for q in ALN) / 1e3, sum(s.get(q, 0) for q in ALN) / 1e3
    ad, sad = sum(H.get(q, 0) for q in ADD) / 1e3, sum(s.get(q, 0) for q in ADD) / 1e3
    print(f"    {lab:11s} aligner and CSA {al:5.0f} of {sal:5.0f} ({al / sal:.2f}); adder through normaliser {ad:5.0f} of {sad:5.0f} ({ad / sad:.2f}); the adder block alone {H.get('txfma_adder', 0) / 1e3:4.0f} of {s.get('txfma_adder', 0) / 1e3:4.0f}")
print("  x_s is a floor by construction: with equal magnitudes in opposite phase, x ^ ~x = 1...1 and maj(c, x, ~x) = c, so the carry-save outputs do not change when the operands swap")

print("\nC3. Like for like: zero products in both, B's signs moving, A's still (E104, the same card, earlier that morning), over E106's steps, across sessions, post hoc")
ms32, hs32, _ = mci(step32.values())
ms16, hs16, _ = mci(step16.values())
for lab, res in (("two kept", E104), ("all three", E104G)):
    a, b = pp(res, ["fp32.z_s"], ["fp32.c_abs"]), pp(res, ["fp16.z_s"], ["fp16.c_abs"])
    ma, ha, _ = mci(a.values())
    mb, hb, _ = mci(b.values())
    md, hd, _ = mci(b[p] - a[p] for p in a if p in b)
    mr, hr, _ = mci(b[p] / a[p] for p in a if p in b)
    sa, sb = ma / ms32, mb / ms16
    qa, qb = math.hypot(ha / ms32, sa * hs32 / ms32), math.hypot(hb / ms16, sb * hs16 / ms16)
    print(f"  E104 {lab:9s}: fp32 z_s - c_abs {ma:.3f} ± {ha:.3f}; fp16 {mb:.3f} ± {hb:.3f}; fp16 less fp32 {md:.3f} ± {hd:.3f}; ratio {mr:.3f} ± {hr:.3f}")
    print(f"       over E106's steps: fp32 {sa:.3f}, fp16 {sb:.3f}, difference {sb - sa:+.3f}, about ± {math.hypot(qa, qb):.3f} (quadrature of the contrasts' and the steps' half-widths, rough)")
a, b = pp(E104G, ["fp32.z_s"], ["fp32.c_abs"], "Drail"), pp(E104G, ["fp16.z_s"], ["fp16.c_abs"], "Drail")
rs32, rs16 = mci(pp(P, ["fp32.signs"], ["fp32.ones"], "Drail").values())[0], mci(pp(P, ["fp16.signs"], ["fp16.ones"], "Drail").values())[0]
print(f"  rail, all three: fp32 {mci(a.values())[0]:.3f} ± {mci(a.values())[1]:.3f}, fp16 {mci(b.values())[0]:.3f} ± {mci(b.values())[1]:.3f}; over E106's rail steps {mci(a.values())[0] / rs32:.3f}, {mci(b.values())[0] / rs16:.3f}, difference {mci(b.values())[0] / rs16 - mci(a.values())[0] / rs32:+.3f}")
c = PRED104["contrasts"]
print(f"  M4 frozen, over M4's steps here: fp32 z_s {c['fp32.z_s - c_abs']['M'] / PRED['contrasts']['fp32.step']['M']:.3f}, fp16 z_s {c['fp16.z_s - c_abs']['M'] / PRED['contrasts']['fp16.step']['M']:.3f}, fp16 z_ss {PRED['contrasts']['fp16.held_z']['M'] / PRED['contrasts']['fp16.step']['M']:.3f}")
print(f"  the bench's toggles over the step: fp32 z_s {sum(dif('fp32.z_s', 'fp32.c_abs').values()) / sum(s32.values()):.3f}, fp16 z_s {sum(dif('fp16.z_s', 'fp16.c_abs').values()) / sum(s16.values()):.3f}, fp16 z_ss {sum(dif('fp16.z_ss', 'fp16.c_abs').values()) / sum(s16.values()):.3f}")
print("  R6 as registered is absorbed (fp32) against zero products (fp16):")
show("fp16 z_ss share less fp32 s_abs share", [hz[p] / step16[p] - h32[p] / step32[p] for p in hz])
print("  No like for like on absorbed products: fp16's s_abs walks")
show("fp16 s_abs - c_abs, E104, two kept", pp(E104, ["fp16.s_abs"], ["fp16.c_abs"]).values())
show("fp16 s_abs - c_abs, E104, all three", pp(E104G, ["fp16.s_abs"], ["fp16.c_abs"]).values())
reads104 = {}
for line in open(os.path.join(E104D, "aifoundry1-c1", "kinds", "readback-p10402", "readback.jsonl")):
    r = json.loads(line)
    reads104[(r["tile"], r["n"])] = r


def units(n, S=2.0 ** 31):
    """The sum over ops m = 1..n of ulp(m S): what one unit an op, at the magnitude C has when the op runs, comes to by op n."""
    tot, m = 0.0, 1
    while m <= n:
        e = math.floor(math.log2(m * S))
        hi = min(n, math.ceil(2.0 ** (e + 1) / S) - 1)
        tot += (hi - m + 1) * 2.0 ** (e - 23)
        m = hi + 1
    return tot


for n in (199874, 541999):
    r = reads104[("fp16.s_abs", n)]
    w = struct.unpack("<256f", bytes.fromhex(list(r["groups"].values())[0]["hex"]))
    off = [(n * 2.0 ** 31 - x) / units(n) for x in w]
    print(f"    read back at n = {n}: {len(set(w))} distinct words; below n x 2^31 by {min(off):.1f} to {max(off):.1f} units an op, mean over the 256 words {statistics.fmean(off):.1f} (a unit is the ulp C has when the op runs)")
cnt = {t: SPEC["tiles"][t]["counts_real"] for t in ("fp32.s_abs", "fp32.signs", "fp16.z_ss", "fp16.signs", "fp16.x_s")}
sh32, shz, shx = mci(h32[p] / step32[p] for p in h32)[0], mci(hz[p] / step16[p] for p in hz)[0], mci(hx[p] / step16[p] for p in hx)[0]
print(f"  alternations an op, the draws differ: s_abs {cnt['fp32.s_abs']['alt1']:.0f} against signs {cnt['fp32.signs']['alt1']:.0f}; z_ss {cnt['fp16.z_ss']['alt1'] + cnt['fp16.z_ss']['alt2']:.0f} against signs {cnt['fp16.signs']['alt1'] + cnt['fp16.signs']['alt2']:.0f}")
sc32 = sh32 * cnt["fp32.signs"]["alt1"] / cnt["fp32.s_abs"]["alt1"]
scz = shz * (cnt["fp16.signs"]["alt1"] + cnt["fp16.signs"]["alt2"]) / (cnt["fp16.z_ss"]["alt1"] + cnt["fp16.z_ss"]["alt2"])
print(f"  scaled to signs' rate (rough, only the alternation-priced part scales): s_abs {sc32:.3f}, z_ss {scz:.3f}, R6 {scz - sc32:+.3f}")

print("\nC4. The rest is what each held tile lacks, and not the same thing in the two formats. Bench, k toggles: step less held tile, and the part in adder through normaliser")
show("fp16 rest against z_ss, W", [step16[p] - hz[p] for p in hz])
show("fp16 rest against x_s, W", [step16[p] - hx[p] for p in hx])
show("fp32 rest against s_abs, W", [step32[p] - h32[p] for p in h32])
for lab, s, H in (("fp16 against z_ss", s16, dif("fp16.z_ss", "fp16.c_abs")), ("fp32 against s_abs", s32, dif("fp32.s_abs", "fp32.c_abs"))):
    tot = sum(s.values()) - sum(H.values())
    ad = sum(s.get(q, 0) - H.get(q, 0) for q in ADD)
    print(f"  {lab}: rest {tot / 1e3:.0f} k, adder through normaliser {ad / 1e3:.0f} k, {ad / tot:.3f}")
H = dif("fp32.s_abs", "fp32.c_abs")
print("  fp32 s_abs above signs - ones, k:", {q: round((H.get(q, 0) - s32.get(q, 0)) / 1e3) for q in ("txfma_f4", "txfma_f5", "txfma_norm_shf")})


def f16(h):
    s = -1.0 if h >> 15 else 1.0
    e, m = (h >> 10) & 31, h & 1023
    return s * m * 2.0 ** -24 if e == 0 else s * (1 + m / 1024) * 2.0 ** (e - 15)


def f32(w):
    return struct.unpack("<f", struct.pack("<I", w))[0]


def words(t):
    w = struct.unpack("<512I", open(os.path.join(K, "e106", SPEC["tiles"][t]["file"]), "rb").read())
    return [w[i * 16 : i * 16 + 16] for i in range(16)], [w[256 + i * 16 : 256 + i * 16 + 16] for i in range(16)]


def sbit(x):
    return 1 if math.copysign(1.0, x) < 0 else 0


def stream(t, n0):
    """eff_sub per lane-micro-op over one op, from the tile's bytes and the order for k, for i, half 0 then half 1, 8 lanes; C by the exact running sum in float64, from n0 x S. The op before it sets each lane's last eff_sub. A sign-stream count: where C is small the RTL's operand order can change it."""
    A, B = words(t)
    fp16 = SPEC["tiles"][t]["type"] == "fp16"

    def prods(a, b):
        return (f16(a >> 16) * f16(b >> 16), f16(a & 0xffff) * f16(b & 0xffff)) if fp16 else (f32(a) * f32(b),)

    S = [[sum(sum(prods(A[i][k], B[k][j])) for k in range(16)) for j in range(16)] for i in range(16)]
    C = [[n0 * S[i][j] for j in range(16)] for i in range(16)]
    last = [None] * 8
    st = collections.Counter()
    for op in (0, 1):
        for k in range(16):
            for i in range(16):
                for h in (0, 1):
                    for lane in range(8):
                        j = lane + 8 * h
                        a, b = A[i][k], B[k][j]
                        c0 = C[i][j]
                        e1 = ((a ^ b) >> 31) ^ sbit(c0)
                        e2 = (((a ^ b) >> 15) & 1) ^ sbit(c0) if fp16 else 0
                        p = prods(a, b)
                        C[i][j] = c0 + sum(p)
                        if op == 1:
                            st["slots"] += 1
                            st["e1"] += e1
                            st["e2"] += e2
                            st["e12"] += e1 & e2
                            st["changes_C"] += C[i][j] != c0
                            st["zero"] += p[0] == 0
                            if last[lane] is not None:
                                f1, f2 = e1 != last[lane][0], e2 != last[lane][1]
                                st["alt1"] += f1
                                st["alt2"] += f2
                                st["both"] += f1 and f2
                                st["one"] += f1 != f2
                                if f1 and f2:
                                    st["same"] += e1 == e2
                                    st["opp"] += e1 != e2
                        last[lane] = (e1, e2)
    n = st["slots"]
    p1, p2, p12 = st["e1"] / n, st["e2"] / n, st["e12"] / n
    den = math.sqrt(p1 * (1 - p1) * p2 * (1 - p2))
    st["phi"] = (p12 - p1 * p2) / den if den else 0.0
    return st


print("\nC5. What 'eff_sub flips as signs' does' means. One lane-micro-op stream, an op at index 136,000 (406,000 gives the same counts). The flips are the same kind on z_ss; the aligned operands are not")
print(f"  {'tile':11s} {'alt1':>5s} {'alt2':>5s} {'bench':>11s} {'both':>5s} {'one':>5s} {'same':>5s} {'opp':>5s} {'phi':>6s} {'empty aligned':>14s} {'change C':>9s}")
EMU = {}
for t in ("fp16.signs", "fp16.z_ss", "fp16.x_s", "fp16.x_c", "fp32.signs", "fp32.s_abs"):
    a, b = stream(t, 136000), stream(t, 406000)
    assert all(a[q] == b[q] for q in ("alt1", "alt2", "both", "one"))
    EMU[t] = a
    bc = SPEC["tiles"][t]["counts_real"]
    print(f"  {t:11s} {a['alt1']:5d} {a['alt2']:5d} {bc['alt1']:5.0f},{bc['alt2']:5.0f} {a['both']:5d} {a['one']:5d} {a['same']:5d} {a['opp']:5d} {a['phi']:6.3f} {a['zero']:9d}/{a['slots']} {a['changes_C']:4d}/{a['slots']}")

print("\nC6. What the reads see: op ends, at four lengths. R1 passes on tiles that do not hold")
reads = {}
for line in open(os.path.join(HERE, "aifoundry1-c1", "kinds", "readback-p10602", "readback.jsonl")):
    r = json.loads(line)
    reads[(r["tile"], r["n"])] = r


def read_words(t, n):
    return struct.unpack("<256I", bytes.fromhex(list(reads[(t, n)]["groups"].values())[0]["hex"]))


print(f"  reads {len(reads)}; on one value across all 1,024 minions: {sum(len(r['groups']) == 1 and list(r['groups'].values())[0]['minions'] == 1024 for r in reads.values())}")
for t in ("fp32.signs",):
    print(f"  {t}: C08 at n = 2, 1,000, 199,874, 541,999:", [f"{read_words(t, n)[8]:08x}" for n in (2, 1000, 199874, 541999)], f"while {EMU[t]['changes_C']} of {EMU[t]['slots']} lane-micro-ops an op move C")
for t in ("fp16.z_ss", "fp16.x_s", "fp32.s_abs"):
    print(f"  {t}: lane-micro-ops an op that leave C unchanged, by the emulation above: {EMU[t]['slots'] - EMU[t]['changes_C']} of {EMU[t]['slots']}; k = 0 moves it, as in the baseline")
for t in ("fp16.signs", "fp32.signs"):
    print(f"  {t}: words with S = 0: {sum(x & 0x7fffffff == 0 for x in read_words(t, 199874))} of 256")


def load(p):
    op = gzip.open if p.endswith(".gz") else open
    return [json.loads(x) for x in op(p, "rt") if x.startswith("{")]


def interp(x, xp, fp):
    if x <= xp[0]:
        return fp[0]
    for a, b, c_, d in zip(xp, xp[1:], fp, fp[1:]):
        if a <= x <= b:
            return c_ + (d - c_) * (x - a) / (b - a)
    return fp[-1]


def reduction(th):
    """The registered reduction at a dip threshold of th watts: first launch of each run, t0 + 1 s to t0 + 3 s, a sample goes if B[i] < min(B[i-2], B[i+2]) - th; p80 = mean B less 0.2414 (mean T - start_c); D over the type's zeros line. Also a median of the same window, no temperature term."""
    per, meds, caught, series = {}, {}, [], {}
    for p in PASSES:
        d = os.path.join(HERE, "aifoundry1-c1", "kinds", "p" + p)
        tel = load(os.path.join(d, "telemetry.jsonl.gz"))
        recs = load(os.path.join(d, "runs.jsonl"))
        marks = sorted(load(os.path.join(d, "marks.jsonl")), key=lambda m: m["t_start_ms"])
        B, t = [s["board_w"] for s in tel], [s["t_ms"] for s in tel]
        Tm = [float(s["temp_c"]["minshire"][0]) for s in tel]
        drop = {i for i in range(2, len(B) - 2) if B[i] < min(B[i - 2], B[i + 2]) - th}
        grp = collections.defaultdict(list)
        for r in recs:
            grp[(r["item"], r.get("pos", 0))].append(r)
        rs = []
        for m in marks:
            if m["kind"] != "run":
                continue
            t0 = min(r["t_start_ms"] for r in grp[(m["item"], m.get("pos", 0))])
            idx = [i for i, x in enumerate(t) if t0 + 1000 <= x < t0 + 3000]
            keep = [i for i in idx if i not in drop]
            rs.append((m["item"], t0, statistics.fmean(B[i] for i in keep) - KLEAK * (statistics.fmean(Tm[i] for i in keep) - m["start_c"]), statistics.median(B[i] for i in keep)))
            if len(keep) < len(idx):
                caught.append((p, m["item"], len(idx) - len(keep)))
            if p == "10610" and m["item"] == "fp16.signs":
                series = [B[i] for i in idx]
        z = collections.defaultdict(list)
        for it, t0, v, md in rs:
            if it.endswith(".zeros"):
                z[it.split(".")[0]].append((t0, v, md))
        per[p], meds[p] = collections.defaultdict(list), collections.defaultdict(list)
        for it, t0, v, md in rs:
            ty = "fp32" if it == "anchor_pi" else it.split(".")[0]
            zz = sorted(z[ty])
            per[p][it].append(v - interp(t0, [a[0] for a in zz], [a[1] for a in zz]))
            meds[p][it].append(md - interp(t0, [a[0] for a in zz], [a[2] for a in zz]))
    f = lambda q: {p: {k: statistics.fmean(v) for k, v in q[p].items()} for p in q}
    return f(per), f(meds), caught, series


CONTRAST = ("fp16.signs", "fp16.ones", "fp16.z_ss", "fp16.c_abs", "fp16.x_s", "fp16.x_c", "fp32.signs", "fp32.ones", "fp32.s_abs", "fp32.c_abs")


def contrasts(per):
    return {
        "s16": [per[p]["fp16.signs"] - per[p]["fp16.ones"] for p in PASSES],
        "s32": [per[p]["fp32.signs"] - per[p]["fp32.ones"] for p in PASSES],
        "z": [per[p]["fp16.z_ss"] - per[p]["fp16.c_abs"] for p in PASSES],
        "x": [per[p]["fp16.x_s"] - per[p]["fp16.x_c"] for p in PASSES],
        "h32": [per[p]["fp32.s_abs"] - per[p]["fp32.c_abs"] for p in PASSES],
    }


print("\nC7. The kept dip: the registered test against thresholds of 3 and 2 W, post hoc")
for th in (4.0, 3.0, 2.0):
    per, med, caught, series = reduction(th)
    if th == 4.0:
        worst = max(abs(per[p][it] - P["per_pass"][p][it]["D"]) for p in PASSES for it in CONTRAST)
        base = {p: per[p]["fp16.signs"] for p in PASSES}
        print(f"  at the registered 4 W this reduction equals e106.json's D on the contrast tiles: largest difference {worst:.6f} W")
        print("  fp16.signs in pass 10610, the window's 20 samples:", series)
        i = series.index(min(series))
        print(f"  the first low sample's neighbours two away: {series[i - 2]} and {series[i + 2]}; the second's: {series[i - 1]} and {series[i + 3]}; the registered test wants below min of the two less 4.0")
    new = [x for x in caught if x[1] in CONTRAST]
    print(f"  threshold {th:.0f} W: samples caught on contrast tiles: {new}")
    if th < 4.0:
        q = contrasts(per)
        print(f"    effect on fp16.signs in pass 10610: {per['10610']['fp16.signs'] - base['10610']:+.3f} W")
        print(f"    fp16 step per pass {[round(v, 3) for v in q['s16']]}, {mci(q['s16'])[0]:.3f} ± {mci(q['s16'])[1]:.3f}")
        show("  z_ss share", [a / b for a, b in zip(q["z"], q["s16"])])
        show("  x_s share", [a / b for a, b in zip(q["x"], q["s16"])])
        show("  R6's difference", [a / b - c_ / d for a, b, c_, d in zip(q["z"], q["s16"], q["h32"], q["s32"])])
q = contrasts(reduction(4.0)[1])
print("  on window medians, no temperature term:")
show("  z_ss share", [a / b for a, b in zip(q["z"], q["s16"])])

print("\nC8. R4's band against R3's")
m, h, _ = mci(hz[p] / step16[p] for p in hz)
print(f"  R4's interval [{m - h:.3f}, {m + h:.3f}]; R4's band [0.30, 0.70]: ABOUT HALF; R3's band [0.35, 0.65]: it would read INCONCLUSIVE")

print("\nC9. The pass the budget rule cost")
sd = statistics.stdev(hz[p] / step16[p] - h32[p] / step32[p] for p in hz)
print(f"  t(2) / sqrt(3) against t(3) / sqrt(4): {(T975[2] / math.sqrt(3)) / (T975[3] / 2):.3f}x wider; R6 at n = 4 with the same sd: -0.112 ± {T975[3] * sd / 2:.3f}: neither inside ±0.15 nor outside it")

print("\nC10. A's signs: z_ss - c_abs here against E104's z_s - c_abs, across sessions")
show("z_ss - c_abs, E106", hz.values())
show("z_s - c_abs, E104 two kept", pp(E104, ["fp16.z_s"], ["fp16.c_abs"]).values())
show("z_s - c_abs, E104 all three", pp(E104G, ["fp16.z_s"], ["fp16.c_abs"]).values())
print(f"  M4 expected {PRED['contrasts']['fp16.held_z']['M'] - c['fp16.z_s - c_abs']['M']:+.3f} W; the bench {(sum(dif('fp16.z_ss', 'fp16.c_abs').values()) - sum(dif('fp16.z_s', 'fp16.c_abs').values())) / 1e3:+.0f} k of {sum(dif('fp16.z_s', 'fp16.c_abs').values()) / 1e3:.0f} k toggles")

print("\nC11. R7 over the tiles that toggle")
tb = SC["primary"]["table"]
tog = ("fp16.signs", "fp16.z_ss", "fp16.x_s", "fp32.signs", "fp32.s_abs")
print(f"  rms over the five that toggle {math.sqrt(sum((tb[t]['D'] - tb[t]['M']) ** 2 for t in tog) / 5):.3f} W; over all ten {SC['primary']['rules']['E106-R7']['rms_w']:.3f} W; the other five (fp16 c_abs, ones, x_c; fp32 c_abs, ones) are baselines")
