#!/usr/bin/env python3
"""E92, post hoc and labelled so: every number README.md quotes beyond scored.json, printed from committed files. No rule
depends on it. Standard library only; run it from this directory:   python3 posthoc-check.py > posthoc-check.txt
Tiles and counts: tools/claims-v3/kinds/e92/. Primary reduction: e92.json. Registered dips-removed arm: dips-arm/."""
import json
import math
import os
import statistics as st
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
e = json.load(open(os.path.join(HERE, "e92.json")))
n = json.load(open(os.path.join(HERE, "dips-arm", "e92-nodips.json")))
s = json.load(open(os.path.join(HERE, "scored.json")))
sn = json.load(open(os.path.join(HERE, "dips-arm", "scored-nodips.json")))
spec = json.load(open(os.path.join(K, "e92", "e92.json")))
reg = json.load(open(os.path.join(K, "predictions-e92.json")))
dips = json.load(open(os.path.join(HERE, "dips-arm", "dips.json")))
T = spec["tiles"]


def mc(v):
    m = st.fmean(v)
    return m, (st.stdev(v) / math.sqrt(len(v)) * T95.get(len(v) - 1, 1.96)) if len(v) > 1 else float("nan")


def pair(res, terms, key="D"):
    """A per-pass linear combination of items: [(coef, item), ...]."""
    out = []
    for p in res["passes"]:
        pp = res["per_pass"][str(p)]
        if all(i in pp and pp[i].get(key) is not None for _, i in terms):
            out.append(sum(c * pp[i][key] for c, i in terms))
    return out


def show(label, terms):
    a, b, c = pair(e, terms), pair(n, terms), pair(e, terms, "Drail")
    ma, ca = mc(a)
    mb, cb = mc(b)
    mr, cr = mc(c)
    print(f"{label:46s} primary {ma:+7.3f} +- {ca:5.3f}   dips-removed {mb:+7.3f} +- {cb:5.3f}   rail(primary) {mr:+7.3f} +- {cr:5.3f}   per pass {[round(x, 3) for x in a]}")
    return ma, mb, mr


print("# A. the core contrasts, board D paired per pass; the rail is Drail, the same reduction; primary n = 3, dips-removed n = 4")
for ty in ("fp32", "fp16"):
    for x, y in (("h_add", "c_abs"), ("h_sub", "h_add"), ("c_alt", "c_abs"), ("h_allsub", "h_add"), ("h_sub", "c_abs"), ("s_abs", "c_abs"), ("signs", "ones")):
        show(f"{ty}.{x} - {y}", [(1, f"{ty}.{x}"), (-1, f"{ty}.{y}")])
show("fp32.c_neg - c_abs", [(1, "fp32.c_neg"), (-1, "fp32.c_abs")])
show("fp32.k_only - c_abs", [(1, "fp32.k_only"), (-1, "fp32.c_abs")])
show("fp32.i_sub - i_add", [(1, "fp32.i_sub"), (-1, "fp32.i_add")])
show("fp32.i_add - c_abs", [(1, "fp32.i_add"), (-1, "fp32.c_abs")])
print()
print("# B. the alternation's premium by regime: always add against alternate, the same operands")
rate = e["items"]["fp32.h_sub"]["rate"]["mean"]
for label, hi, lo in (("frozen, magnitude 1", "fp32.h_sub", "fp32.h_add"), ("frozen, random magnitudes", "fp32.r_h_sub", "fp32.r_h_add"),
                      ("moving sums, magnitude 1", "fp32.w_h_sub", "fp32.w_h_add"), ("moving sums, random magnitudes", "fp32.wr_h_sub", "fp32.wr_h_add")):
    a = show(label, [(1, hi), (-1, lo)])
    print(f"    fJ per alternation (3,840 an op, {rate:.4g} ops/s): primary {1e15 * a[0] / 3840 / rate:.0f}, dips-removed {1e15 * a[1] / 3840 / rate:.0f}, rail {1e15 * a[2] / 3840 / rate:.0f}; dflops {T[hi]['sign']['flops'] - T[lo]['sign']['flops']:,.0f}")
print()
print("# C. fp16's two aligners")
show("fp16.hh_sub - c_abs", [(1, "fp16.hh_sub"), (-1, "fp16.c_abs")])
show("fp16.hl_sub - c_abs", [(1, "fp16.hl_sub"), (-1, "fp16.c_abs")])
show("fp16.hh_sub - hl_sub", [(1, "fp16.hh_sub"), (-1, "fp16.hl_sub")])
a = show("additivity: hh + hl - h_sub - c_abs", [(1, "fp16.hh_sub"), (1, "fp16.hl_sub"), (-1, "fp16.h_sub"), (-1, "fp16.c_abs")])
f = reg["models"]["f_fj_per_flop_bit"]
sc = reg["models"]["card_scale"]["fp16"]
fl = T["fp16.hh_sub"]["sign"]["flops"] + T["fp16.hl_sub"]["sign"]["flops"] - T["fp16.h_sub"]["sign"]["flops"] - T["fp16.c_abs"]["sign"]["flops"]
print(f"    flops say +{fl:,.0f} bits an op: e88+flops' price puts that at {sc * f * 1e-15 * fl * 600e6 / 546 * 1024:.2f} W")
for x in ("fp16.hh_sub", "fp16.hl_sub"):
    a0 = mc(pair(e, [(1, x), (-1, "fp16.c_abs")]))[0]
    b0 = mc(pair(e, [(1, "fp16.h_sub"), (-1, "fp16.c_abs")]))[0]
    a1 = mc(pair(n, [(1, x), (-1, "fp16.c_abs")]))[0]
    b1 = mc(pair(n, [(1, "fp16.h_sub"), (-1, "fp16.c_abs")]))[0]
    print(f"    {x} as a share of h_sub, each over c_abs: primary {a0 / b0:.3f}, dips-removed {a1 / b1:.3f}")


def words(name):
    raw = open(os.path.join(K, "e92", T[name]["file"]), "rb").read()
    w = struct.unpack("<512I", raw)
    return [list(w[i * 16:(i + 1) * 16]) for i in range(16)], [list(w[256 + i * 16:256 + (i + 1) * 16]) for i in range(16)]


def joint_events(name):
    """With every C positive (the frozen designs): per lane, against its previous micro-op, how often (eff_sub1, eff_sub2) changes."""
    A, B = words(name)
    prev = [None] * 8
    first, nany, n1, n2 = None, 0, 0, 0
    for _ in range(2):
        cnt = [0, 0, 0]
        for k in range(16):
            for i in range(16):
                for h in (0, 1):
                    for l in range(8):
                        a, b = A[i][k], B[k][8 * h + l]
                        e1, e2 = (a ^ b) >> 31 & 1, (a ^ b) >> 15 & 1
                        if prev[l] is not None:
                            cnt[0] += (e1, e2) != prev[l]
                            cnt[1] += e1 != prev[l][0]
                            cnt[2] += e2 != prev[l][1]
                        prev[l] = (e1, e2)
    return tuple(cnt)


print()
print("# D. fp16: alternation events with every C positive: (either changes, eff_sub1 changes, eff_sub2 changes) per op")
ev = {x: joint_events(x) for x in ("fp16.s_abs", "fp16.h_sub", "fp16.hh_sub", "fp16.hl_sub")}
for x, v in ev.items():
    print(f"    {x:12s} {v}")
Bs, Bh = reg["contrasts"]["fp16.s_abs-c_abs"]["bits_w"], reg["contrasts"]["fp16.h_sub-c_abs"]["bits_w"]
for res, nm in ((e, "primary"), (n, "dips-removed")):
    a = mc(pair(res, [(1, "fp16.s_abs"), (-1, "fp16.c_abs")]))[0] - Bs
    b = mc(pair(res, [(1, "fp16.h_sub"), (-1, "fp16.c_abs")]))[0] - Bh
    print(f"    {nm}: (s_abs - c_abs - bits) / (h_sub - c_abs - bits) = {a / b:.3f}; the eff_sub1 + eff_sub2 count says {(ev['fp16.s_abs'][1] + ev['fp16.s_abs'][2]) / (ev['fp16.h_sub'][1] + ev['fp16.h_sub'][2]):.3f}, the either-changes count {ev['fp16.s_abs'][0] / ev['fp16.h_sub'][0]:.3f}")
Bs, Bh = reg["contrasts"]["fp32.s_abs-c_abs"]["bits_w"], reg["contrasts"]["fp32.h_sub-c_abs"]["bits_w"]
for res, nm in ((e, "primary"), (n, "dips-removed")):
    a = mc(pair(res, [(1, "fp32.s_abs"), (-1, "fp32.c_abs")]))[0] - Bs
    b = mc(pair(res, [(1, "fp32.h_sub"), (-1, "fp32.c_abs")]))[0] - Bh
    print(f"    fp32 {nm}: (s_abs - c_abs - bits) / (h_sub - c_abs - bits) = {a / b:.3f}; the alternation count says {T['fp32.s_abs']['sign']['N_alt1'] / T['fp32.h_sub']['sign']['N_alt1']:.3f}")
print()
print("# E. where the signs' ~5 W goes, in fp32, two readings of the alternation's share")
for res, nm in ((e, "primary"), (n, "dips-removed")):
    tot = mc(pair(res, [(1, "fp32.signs"), (-1, "fp32.ones")]))[0]
    froz = mc(pair(res, [(1, "fp32.s_abs"), (-1, "fp32.c_abs")]))[0]
    wp = mc(pair(res, [(1, "fp32.w_h_sub"), (-1, "fp32.w_h_add")]))[0]
    r = T["fp32.signs"]["sign"]["N_alt1"] / T["fp32.w_h_sub"]["sign"]["N_alt1"]
    bits = reg["contrasts"]["fp32.signs-ones"]["bits_w"]
    bs = reg["contrasts"]["fp32.s_abs-c_abs"]["bits_w"]
    print(f"    {nm}: signs - ones {tot:.3f} W. (a) frozen: bits {bs:.3f} + the rest of s_abs - c_abs {froz - bs:.3f} = {froz:.3f}, moving sums {tot - froz:.3f}. "
          f"(b) the moving-sum price of an alternation x signs' rate {r:.3f}: {wp * r:.3f}; bits {bits:.3f}; left {tot - bits - wp * r:.3f}")
print()
print("# F. the dips")
print("   ", dips["totals"], "by pass:", {p: (v["dips"], v["in_runs"], v["in_power_windows"]) for p, v in dips["passes"].items()})
print("    in power windows:", [(p, r["where"].replace("run ", ""), round(r["board_w"] - min(r["neighbours_w"]), 1)) for p, v in dips["passes"].items() for r in v["rows"] if r["in_power_window"]])
print("    set aside by E78's gates, primary:", e["passes_set_aside"], "; dips-removed:", n["passes_set_aside"])
print()
print("# G. the session's ties and checks")
for k, v in s["rules"]["E92-S1"]["cells"].items():
    print(f"    {k:12s} D {v['D_w']:.3f}; minus E78 {v.get('diff_e78_w')}; minus E90 {v.get('diff_e90_w')}; band {v['band_w']}; inside {v['inside']}")
print("    S3", s["rules"]["E92-S3"])
print("    leak", e["leak"], "tie drift", e["tie_drift_w"], "idle consistency", e["checks"]["idle_consistency"]["median_abs_w"], "carry-over", e["checks"]["carryover"], "duty", min(e["checks"]["duty"].values()), max(e["checks"]["duty"].values()), "cpo", e["cycles_per_op"], "v", e["v_mean"], "clock", e["clock_mhz"], "runs", e["runs"], "kept", e["kept"])
print()
print("# H. per lane alternation against the sign bit's own flip")
for ty, cc in (("fp32", "fp32.h_add-c_abs"), ("fp16", "fp16.h_add-c_abs")):
    for r, nm in ((s, "primary"), (sn, "dips-removed")):
        f_ = r["factorial"][ty]
        rt = f_["rate_ops_per_s"]
        fl_ = (T[f"{ty}.h_add"]["stats"]["sign_flips_per_op_a"] + T[f"{ty}.h_add"]["stats"]["sign_flips_per_op_b"])
        d = r["contrasts"][cc]["D_w"]["mean"]
        print(f"    {ty} {nm}: an alternation {f_['gamma_fj_per_lane_alternation']:.0f} fJ; h_add - c_abs per flipped sign bit {1e15 * d / fl_ / rt:.0f} fJ ({fl_} flips an op); per lane-micro-op {1e15 * d / 4096 / rt:.0f} fJ")
print()
print("# I. the alternation's premium over its flop bits, across fp32's regimes and fp16's designs (registered f: %.2f fJ per flop bit, calibrated on E88's M32s)" % reg["models"]["f_fj_per_flop_bit"])
for label, hi, lo in (("frozen, magnitude 1", "fp32.h_sub", "fp32.h_add"), ("frozen, random magnitudes", "fp32.r_h_sub", "fp32.r_h_add"),
                      ("moving sums, magnitude 1", "fp32.w_h_sub", "fp32.w_h_add"), ("moving sums, random magnitudes", "fp32.wr_h_sub", "fp32.wr_h_add"),
                      ("fp32 frozen, random signs", "fp32.s_abs", "fp32.c_abs"), ("fp32 frozen, sum signs only", "fp32.c_alt", "fp32.c_abs"), ("fp16 frozen, both", "fp16.h_sub", "fp16.h_add"), ("fp16 frozen, sum signs only", "fp16.c_alt", "fp16.c_abs"),
                      ("fp16 frozen, high product", "fp16.hh_sub", "fp16.c_abs"), ("fp16 frozen, low product", "fp16.hl_sub", "fp16.c_abs"), ("fp16 frozen, random signs", "fp16.s_abs", "fp16.c_abs")):
    df = T[hi]["sign"]["flops"] - T[lo]["sign"]["flops"]
    a = mc(pair(e, [(1, hi), (-1, lo)]))[0]
    b = mc(pair(n, [(1, hi), (-1, lo)]))[0]
    rt = e["items"][hi]["rate"]["mean"]
    print(f"    {label:32s} dflops {df:9,.0f}  W primary {a:6.3f}, dips-removed {b:6.3f}  fJ per flop bit primary {1e15 * a / df / rt:5.2f}, dips-removed {1e15 * b / df / rt:5.2f}")
print()
print("# J. the frozen models over the contrasts with a rule, by format")
for r, nm in ((s, "primary"), (sn, "dips-removed")):
    for ty in ("fp32", "fp16"):
        cc = {k: v for k, v in r["contrasts"].items() if v["rule"] and k.startswith(ty)}
        e1 = [v["D_w"]["mean"] - v["e88_flops_w"] for v in cc.values()]
        e2 = [v["D_w"]["mean"] - v["e88_mu_w"] for v in cc.values()]
        inside = sum(1 for v in cc.values() if v["e88_inside"])
        print(f"    {nm} {ty}: n {len(cc)}, e88+flops rms {math.sqrt(st.fmean(x * x for x in e1)):.3f} W, e88 rms {math.sqrt(st.fmean(x * x for x in e2)):.3f} W, inside e88's band {inside} of {len(cc)}")
