#!/usr/bin/env python3
"""E104: the desk check behind "Corrections after verification": every number they cite, from committed files, standard library only. Run it in this directory.

    python3 corrections-check.py > corrections-check.txt

Sections are named for the corrections they back. Nothing here is a registered test; no rule, verdict or frozen file depends on it.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
P = json.load(open(os.path.join(HERE, "e104.json")))
G = json.load(open(os.path.join(HERE, "e104-gatesoff.json")))
L0 = json.load(open(os.path.join(HERE, "e104-leak0.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
REG = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/predictions-e104.json")))
SPEC = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/e104/e104.json")))
BENCH = os.path.join(ROOT, "docs/reports/data/2026-11-01-q132-rtl-bench/counts-e92.json")
rows = {}
for f in (BENCH, os.path.join(HERE, "desk/counts-e104.json"), os.path.join(HERE, "desk/counts-e104b.json"), os.path.join(HERE, "desk/counts-e104c.json")):
    rows.update(json.load(open(f))["rows"])
RATE = P["items"]["fp16.randn"]["rate"]["mean"]
SCALE = 0.9722


def pp(res, a, b):
    return {p: it[a]["D"] - it[b]["D"] for p, it in sorted(res["per_pass"].items()) if a in it and b in it and it[a].get("D") is not None and it[b].get("D") is not None}


def mci(v):
    v = list(v)
    if len(v) < 2:
        return (v[0] if v else float("nan")), float("nan"), len(v)
    return sum(v) / len(v), T975[len(v) - 1] * statistics.stdev(v) / math.sqrt(len(v)), len(v)


print("C1. Where the bench puts fp16's h_sub - u_sub (by_block_cov, net toggles an op on one minion; the grouping is E104's verifier's)")
GROUPS = (("adder and normaliser", ("txfma_f3", "txfma_lxd", "txfma_adder", "txfma_csa", "txfma_trz2", "txfma_f4", "txfma_f5", "txfma_norm_shf", "txfma_c4", "txfma_c5", "txfma_rnd_adder", "txfma_f6", "txfma_e5")),
          ("the FMA's fraction, exponent, control and early stages", ("txfmafrac_top", "txfmaexp_top", "txfmactl_top", "txfma_top", "txfma_c0", "txfma_c1", "txfma_c2", "txfma_c3", "txfma_frac_zero_detect", "txfma_f0", "txfma_f1", "txfma_f2")),
          ("VPU lane, bypass, register file, top", ("vpu_lane", "vpu_bypass", "vpu_rf", "vpu_top", "vpu_ctrl", "vpu_tensorfma", "vpu_64x32_3r2w_vpurf", "vpu_ml", "rf_latch_1r_1w", "vpu_sh_sw", "vpu_trans", "vpu_txfma_trans_top", "trans_top")))
for a, b in (("fp16.h_sub", "fp16.u_sub"), ("fp32.h_sub", "fp32.u_sub")):
    x, y = rows[a]["mean"]["by_block_cov"], rows[b]["mean"]["by_block_cov"]
    d = {k: x.get(k, 0) - y.get(k, 0) for k in set(x) | set(y)}
    tot = sum(d.values())
    print(f"  {a} - {b}: net toggles {tot / 1e6:+.2f} M; flop toggles all {rows[a]['mean']['ff']['all']['toggles'] - rows[b]['mean']['ff']['all']['toggles']:+.0f}, in the FMA {rows[a]['mean']['ff']['txfma']['toggles'] - rows[b]['mean']['ff']['txfma']['toggles']:+.0f}")
    seen = set()
    for g, names in GROUPS:
        s = sum(d.get(n, 0) for n in names)
        seen |= set(names)
        print(f"    {g:56s} {s / 1e3:8.0f} k {100 * s / tot:6.1f} %")
    o = sum(v for k, v in d.items() if k not in seen)
    print(f"    {'the rest':56s} {o / 1e3:8.0f} k {100 * o / tot:6.1f} %")
t = {n: REG["tiles"][n]["pred"]["terms_w"] for n in ("fp16.h_sub", "fp16.u_sub")}
print("  M4's frozen terms for the contrast, W: core %+.2f, operand bus %+.2f, rest %+.2f, clock %+.2f; total %+.2f" % (*[a - b for a, b in zip(t["fp16.h_sub"], t["fp16.u_sub"])], sum(t["fp16.h_sub"]) - sum(t["fp16.u_sub"])))

print("C3. 28.5 fJ is a lump. E92's 29.7 fJ takes 7 fJ per adder bit off first; on the same accounting h_sub - u_sub less fp32's has nothing left to price")
db = 0.0
k = lambda n: SPEC["tiles"][n]["counts_real"]
bits = lambda n: k(n)["cbus"] + k(n)["rbus"] + k(n)["store"]
db = bits("fp16.h_sub") - bits("fp16.u_sub")
a = {p: pp(P, "fp16.h_sub", "fp16.u_sub")[p] - pp(P, "fp32.h_sub", "fp32.u_sub")[p] for p in pp(P, "fp16.h_sub", "fp16.u_sub")}
m, c, n = mci(a.values())
print(f"  fp16 h_sub - u_sub less fp32's: {m:.3f} +- {c:.3f} W over {db:.0f} result bits: {m / (db * RATE) * 1e15:.1f} fJ a bit, nothing taken off")
fl = (rows["fp16.h_sub"]["mean"]["ff"]["txfma"]["toggles"] - rows["fp16.u_sub"]["mean"]["ff"]["txfma"]["toggles"]) - (rows["fp32.h_sub"]["mean"]["ff"]["txfma"]["toggles"] - rows["fp32.u_sub"]["mean"]["ff"]["txfma"]["toggles"])
print(f"  FMA flop toggles it adds: {fl:.0f} an op (one minion, the bench). On E92's accounting, 7 fJ each at {RATE / 1e9:.3f}e9 ops/s: {fl * 7e-15 * RATE:.2f} W, more than the {m:.2f} W there is")
print(f"  E92's w_c - c_abs: 3.987 W, 98,780 result bits, 88,500 adder bits: raw {3.987 / (98780 * 1.1208e9) * 1e15:.1f} fJ a result bit, {(3.987 - 88500 * 7e-15 * 1.1208e9) / (98780 * 1.1208e9) * 1e15:.1f} after 7 fJ per adder bit")
for t_ in ("fp32", "fp16"):
    x = pp(P, f"{t_}.w_h_add", f"{t_}.h_add")
    y = pp(G, f"{t_}.w_h_add", f"{t_}.h_add")
    mx, cx, _ = mci(x.values())
    my, cy, _ = mci(y.values())
    d_ = bits(f"{t_}.w_h_add") - bits(f"{t_}.h_add")
    print(f"  {t_} w_h_add - h_add, the same bits in both formats ({d_:.0f}): {mx:.3f} +- {cx:.3f} W (all three {my:.3f} +- {cy:.3f}), {mx / (d_ * RATE) * 1e15:.1f} fJ a bit, raw: alike, and the primary cannot separate them")

print("C4. u_sub's alternations against h_sub's")
for t_ in ("fp32", "fp16"):
    print(f"  {t_}: u_sub alternations {k(t_ + '.u_sub')['alt1']:.0f}, h_sub {k(t_ + '.h_sub')['alt1']:.0f}: {k(t_ + '.u_sub')['alt1'] / k(t_ + '.h_sub')['alt1']:.3f}; subtracting lane-micro-ops {k(t_ + '.u_sub')['sub1'] * k(t_ + '.u_sub')['live']:.0f} against {k(t_ + '.h_sub')['sub1'] * k(t_ + '.h_sub')['live']:.0f}: {k(t_ + '.u_sub')['sub1'] / k(t_ + '.h_sub')['sub1']:.3f}")
fz = REG["contrasts"]["fp16.h_premium"]["frozen_reading_w"]
print(f"  the frozen reading at 0.904 of the alternations: u_sub - h_add {fz * 3472 / 3840:.2f} W (registered at 14/15: {fz * 14 / 15:.2f}), h_sub - u_sub {fz * (1 - 3472 / 3840):.2f} W (registered: {fz / 15:.2f}). The frozen file stays; R4's +-1 W band holds either way")
pu, ph = mci(pp(P, "fp16.u_sub", "fp16.h_add").values())[0], mci(pp(P, "fp16.h_sub", "fp16.u_sub").values())[0]
c32 = mci(pp(P, "fp32.h_sub", "fp32.u_sub").values())[0]
own = pu / 3472 * 368
print(f"  the split at h_sub's own alternations: the 368 alternations u_sub lacks are {c32:.3f} W by fp32's control, {own:.3f} W at fp16's own price. Adder {pu + c32:.2f}-{pu + own:.2f} W, halves {ph - own:.2f}-{ph - c32:.2f} W; as run {pu:.3f} and {ph:.3f} W")

print("C5. C has been read off the card before, on tiles the host checks: results in docs/reports/data/2026-09-18-sparsity-aifoundry3/")
import collections  # noqa: E402
for f in ("fma-fp16-elem.jsonl", "fma-fp32-elem-all.jsonl", "fma-int8-elem.jsonl"):
    c_ = collections.Counter()
    p = os.path.join(ROOT, "docs/reports/data/2026-09-18-sparsity-aifoundry3", f)
    if os.path.exists(p):
        for line in open(p):
            if '"result"' in line:
                try:
                    c_[json.loads(line[line.find("{"):]).get("result")] += 1
                except ValueError:
                    pass
    print(f"  {f}: {dict(c_)}")

print("C6. The denominators of 110")
R = SC["readback"]["rows"]
allthree = [r for r in R if r["words_off"]["rtl"] == 0 and r["words_off"]["fl"] == 0 and r["words_off"]["manual"] == 0]
ff = [r for r in R if r["words_off"]["fl"] > 0]
mm = [r for r in R if r["words_off"]["manual"] > 0]
both = [r for r in R if r["words_off"]["fl"] > 0 and r["words_off"]["manual"] > 0 and SPEC["tiles"][r["tile"]]["read"][str(r["n"])]["words_fl_vs_manual"] > 0]
print(f"  {len(R)} reads on {len({r['tile'] for r in R})} tiles. Agree with all three: {len(allthree)} reads on {len({r['tile'] for r in allthree})} tiles. Separate frozen from the RTL: {len(ff)} reads on {len({r['tile'] for r in ff})} tiles: {sorted({r['tile'] for r in ff})}. Separate the manual from the RTL: {len(mm)} reads on {len({r['tile'] for r in mm})} tiles: {sorted({r['tile'] for r in mm})}. All three different: {len(both)} reads")

print("C7. The two formats' budgets are similar, not shown equal: z_s - c_abs, fp16 over fp32, per pass; shares are posthoc-check.txt E")
for lab, res in (("primary", P), ("all three", G)):
    x, y = pp(res, "fp16.z_s", "fp16.c_abs"), pp(res, "fp32.z_s", "fp32.c_abs")
    m_, c_2, n_ = mci([x[p] / y[p] for p in x if p in y])
    print(f"  {lab}: {m_:.3f} +- {c_2:.3f} (n={n_})")

print("C8. fJ per lane alternation with intervals, and against E92's 1,099 fJ. The 1,099 is gamma, with beta (the C sign term) added back, on aifoundry3. E104's premium is over h_add, whose sums swing in sign on every lane micro-op")
for t_, beta, alpha, gamma in (("fp32", 0.332, 0.206, 1092), ("fp16", 0.223, 0.259, 1617)):
    for lab, res in (("primary", P), ("all three", G)):
        m_, c_2, n_ = mci(pp(res, f"{t_}.u_sub", f"{t_}.h_add").values())
        add = beta * SCALE + alpha * SCALE * (1 - 3472 / 4096)
        print(f"  {t_} u_sub - h_add {lab:9s}: {m_ / (3472 * RATE) * 1e15:5.0f} +- {c_2 / (3472 * RATE) * 1e15:4.0f} fJ; with E92's dips-arm beta and the B flips it lacks x {SCALE} (+{add:.3f} W): {(m_ + add) / (3472 * RATE) * 1e15:5.0f} fJ")
    print(f"    E92's gamma, dips arm, {gamma} fJ x {SCALE}: {gamma * SCALE:.0f} fJ" + ("" if t_ == "fp32" else ": fp16's gamma held the parting halves too (E92 C14)"))
m_, c_2, n_ = mci(pp(P, "fp32.h_sub", "fp32.h_add").values())
print(f"  like against like, fp32 h_sub - h_add here: {m_ / (3840 * RATE) * 1e15:.0f} +- {c_2 / (3840 * RATE) * 1e15:.0f} fJ; E92's 4.425 and 4.396 W x {SCALE} at the same count: {4.425 * SCALE / (3840 * RATE) * 1e15:.0f}, {4.396 * SCALE / (3840 * RATE) * 1e15:.0f} fJ")
for t_ in ("fp32", "fp16"):
    m_, _, _ = mci(pp(G, f"{t_}.m_h_sub", f"{t_}.w_h_add").values())
    print(f"  moving sums at magnitude 1, {t_}, all three: {m_ / (3840 * RATE) * 1e15:.0f} fJ")

print("C11. Small statements. u_sub's result bits; Drail's temperature term")
for t_ in ("fp16", "fp32"):
    print(f"  {t_}.u_sub: result bits {bits(t_ + '.u_sub'):.0f} an op (C bus {k(t_ + '.u_sub')['cbus']:.0f}, result bus {k(t_ + '.u_sub')['rbus']:.0f}, store {k(t_ + '.u_sub')['store']:.0f})")
print(f"  Drail on fp16.h_sub, pass 10411: {P['per_pass']['10411']['fp16.h_sub']['Drail']:.3f} W at the primary's slope, {L0['per_pass']['10411']['fp16.h_sub']['Drail']:.3f} W at leak 0: the rail's D does carry a temperature term, 0.81 k")

print("The carry by 0.9722, for result 5: E92's dips arm x 0.9722 against E104's all-three means, the contrasts both ran")
E92 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e92-sign-split/dips-arm/e92-nodips.json")))
for a_, b_ in (("fp32.h_sub", "fp32.h_add"), ("fp32.h_add", "fp32.c_abs"), ("fp16.h_sub", "fp16.h_add"), ("fp16.c_alt", "fp16.c_abs"), ("fp16.s_abs", "fp16.c_abs"), ("fp16.h_add", "fp16.c_abs")):
    x = mci(pp(E92, a_, b_).values())[0] * SCALE
    y = mci(pp(G, a_, b_).values())[0]
    print(f"  {a_} - {b_.split('.')[1]}: carried {x:.3f}, here {y:.3f}, ratio {y / x:.3f}")
