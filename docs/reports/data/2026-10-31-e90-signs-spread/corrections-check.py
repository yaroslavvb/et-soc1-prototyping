#!/usr/bin/env python3
"""E90: the desk check behind 'Corrections after verification' (Sat 31 Oct 2026). Written after an independent
verifier's report, at the desk: no card touched, nothing re-run. Every number is read from committed files; none is
a registered rule, and none changes a registered number or verdict. Standard library only.

    python3 corrections-check.py > corrections-check.txt

C1  Q130(n)'s predictor. What E90-R5 scores (each draw's offset from E78's committed tile of the same rule, against
    the frozen predicted offset) beside the predictor's absolute price of each tile (scored.json rules.E90-S2.tiles:
    D_w - q130n_point_w); a no-model baseline for the offsets (every draw costs its committed tile); each E90 tile's
    margin inside the predictor's 95% interval.
C2  E90-R4 with the draw as the unit. Per rule, the three draws' paired D(draw) - D(committed) (scored.json draws),
    their mean and t(0.975, 2) interval, beside R4's registered interval over passes; the verdict either would give
    against +-0.5 W; the committed tile's and the draws' statistics against the rule's 400-draw band (kinds.json
    replicates, as copied into e90/e90.json before the run).
C3  How far one re-draw moved the cost: every draw's paired move, each rule's range.
C4  Heat. dT_win is the mean whole-degree die reading 1-3 s after launch minus the launch reading (reduce_e78.py,
    unchanged). Per pass for the sign kinds and their references, and the paired differences.
C5  fp16 against fp32. The sign-bit prices behind the bits model (predictions-e90.json sign_bit_prices) in fJ and their
    ratios, and the two +-1 steps paired per pass, against the bits model's ratio of the two steps.
C6  The verdict count (scored.json rules).
"""
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
KINDS_DIR = os.path.join(REPO_DIR, "tools", "claims-v3", "kinds")
E = json.load(open(os.path.join(HERE, "e90.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
P = json.load(open(os.path.join(KINDS_DIR, "predictions-e90.json")))
T = json.load(open(os.path.join(KINDS_DIR, "e90", "e90.json")))
K = json.load(open(os.path.join(KINDS_DIR, "kinds.json")))

PASSES = [str(p) for p in E["passes"]]
# two-sided 95% Student t, by degrees of freedom
T975 = {1: 12.7062, 2: 4.3027, 3: 3.1824, 4: 2.7764, 5: 2.5706, 6: 2.4469, 7: 2.3646, 8: 2.3060, 9: 2.2622}
RULES = (("fp32", "sparse50"), ("fp16", "nn_like"), ("fp16", "uniform01"))


def mci(v):
    """mean and 95% half-width over the values"""
    n = len(v)
    m = st.mean(v)
    h = T975[n - 1] * st.stdev(v) / math.sqrt(n) if n > 1 else float("nan")
    return m, h


def pp(p, item, key):
    return E["per_pass"][p][item][key]


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def band_word(lo_hi, x):
    lo, hi = lo_hi
    if x < lo:
        return "BELOW p2.5"
    if x > hi:
        return "ABOVE p97.5"
    return "inside"


print("E90 corrections-check (desk only; committed files only)")
print("kept passes %s (n = %d, t(0.975, %d) = %.4f)" % (PASSES, len(PASSES), len(PASSES) - 1, T975[len(PASSES) - 1]))

# ---------------------------------------------------------------- C1
print()
print("== C1 Q130(n)'s predictor: the offsets R5 scores against the absolute prices of the same tiles")
s2 = SC["rules"]["E90-S2"]["tiles"]
r5 = SC["rules"]["E90-R5"]
draws = [d for d in SC["draws"]]
abs_miss, off_err, off_meas = [], [], []
print("draw                  D (W)    predictor point  absolute miss D-point | offset measured  predicted  error")
for d in draws:
    dd = SC["draws"][d]
    D = s2[d]["D_w"]
    pt = s2[d]["q130n_point_w"]
    m = dd["minus_committed_w"]["mean"]
    q = dd["q130n_delta_w"]
    abs_miss.append(D - pt)
    off_err.append(m - q)
    off_meas.append(m)
    print("%-20s  %7.3f  %7.3f          %+7.3f                | %+7.3f          %+7.3f    %+7.3f"
          % (d, D, pt, D - pt, m, q, m - q))
am = [abs(x) for x in abs_miss]
print("absolute prices of the nine draws: |miss| %.3f-%.3f W, rms %.4f W" % (min(am), max(am), rms(abs_miss)))
for kind in ("fp32.sparse50", "fp16.nn_like", "fp16.uniform01"):
    v = [abs_miss[i] for i, d in enumerate(draws) if d.startswith(kind + "_")]
    print("   %-15s misses %s W (%s)" % (kind, ", ".join("%+.3f" % x for x in v),
                                        "measured above the point: underpriced" if v[0] > 0
                                        else "measured below the point: overpriced"))
print("offsets (R5): rms error %.4f W (scored.json rules.E90-R5: %s); no-model baseline 'every draw costs its "
      "committed tile' (offset 0): rms %.4f W" % (rms(off_err), json.dumps({k: r5[k] for k in r5 if k in
                                                                              ("rms_w", "verdict")}),
                                                  rms(off_meas)))
print("every E90 tile against the predictor's frozen 95% interval (scored.json rules.E90-S2.tiles):")
one_sign = []
for t, v in s2.items():
    lo, hi = v["pi95_w"]
    margin = min(v["D_w"] - lo, hi - v["D_w"])
    print("   %-20s D %7.3f  point %7.3f  miss %+7.3f  interval [%.3f, %.3f]  %s by %.3f W"
          % (t, v["D_w"], v["q130n_point_w"], v["D_w"] - v["q130n_point_w"], lo, hi,
             "inside" if v["inside"] else "OUTSIDE", abs(margin)))
    if "abs_randn" in t or "uniform01" in t:
        one_sign.append((t, v["q130n_point_w"] - v["D_w"]))
print("random data of one sign (abs_randn, negabs_randn, uniform01 draws), priced high by: "
      + ", ".join("%s %.3f" % x for x in one_sign) + " W")
print("inside count %d of %d (registered: >= 14)" % (SC["rules"]["E90-S2"]["inside"], SC["rules"]["E90-S2"]["of"]))

# ---------------------------------------------------------------- C2, C3
print()
print("== C2 R4 with the draw as the unit; C3 how far one re-draw moved")
for typ, kind in RULES:
    name = "%s.%s" % (typ, kind)
    ds = ["%s_d%d" % (name, r) for r in (1, 2, 3)]
    moves = [SC["draws"][d]["minus_committed_w"]["mean"] for d in ds]
    m, h = mci(moves)
    reg = SC["spread"][name]["draws_minus_committed_mean_w"]
    sp = SC["spread"][name]
    v_draw = "PASS" if abs(m) + h <= 0.5 else ("FAIL" if abs(m) - h > 0.5 else "INCONCLUSIVE")
    print("%s: per-draw paired moves %s W (range %.3f-%.3f in size)"
          % (name, ", ".join("%+.3f" % x for x in moves), min(abs(x) for x in moves), max(abs(x) for x in moves)))
    print("   R4 as registered (over passes, these three draws): %+.3f +- %.3f W -> %s"
          % (reg["mean"], reg["ci95"], sp["verdict_R4"]))
    print("   the draw as the unit (t(0.975, 2) = %.4f): %+.3f +- %.3f W [%+.3f, %+.3f] -> %s against +-0.5 W"
          % (T975[2], m, h, m - h, m + h, v_draw))
    print("   sd between the four tiles %.3f W; one tile's between-pass sd %.3f W (ratio %.1f); range %.3f W"
          % (sp["sd_between_tiles_w"], sp["sd_between_passes_one_tile_w"],
             sp["sd_between_tiles_w"] / sp["sd_between_passes_one_tile_w"], sp["range_w"]))
    rec = T["tiles"][ds[0]]
    ct = rec["committed_tile"]
    band = rec["rule_band"]
    rep = K["kinds"][typ][kind]["replicates"]
    for stat in ("gated_lane_frac", "bus_bits_per_op"):
        lo, hi = band[stat]["p2.5"], band[stat]["p97.5"]
        sd = rep[stat]["sd"]
        z = "z %+.2f" % ((ct[stat] - rep[stat]["mean"]) / sd) if sd > 0 else "every re-draw the same"
        dv = [T["tiles"][d]["stats"][stat] for d in ds]
        print("   %-16s band [%s, %s] (n = %d re-draws, kinds.json); committed %s (%s, %s); draws %s (%s)"
              % (stat, lo, hi, rep[stat]["n"], ct[stat], band_word((lo, hi), ct[stat]), z,
                 ", ".join(str(x) for x in dv), ", ".join(band_word((lo, hi), x) for x in dv)))
big = max(((d, SC["draws"][d]["minus_committed_w"]) for d in SC["draws"]), key=lambda x: abs(x[1]["mean"]))
print("largest single move: %s %+.3f +- %.3f W" % (big[0], big[1]["mean"], big[1]["ci95"]))

# ---------------------------------------------------------------- C4
print()
print("== C4 heat: dT_win per pass (C over the launch reading; whole-degree die reading) and paired differences")
for it in ("fp32.signs", "fp32.ones", "fp16.signs", "fp16.ones", "int8.signs", "int8.full", "fp32.pm_pi",
           "anchor_pi", "fp32.randn", "fp16.randn"):
    v = [pp(p, it, "dT_win") for p in PASSES]
    n_runs = [pp(p, it, "n_runs") for p in PASSES]
    m, h = mci(v)
    note = "  <- three identical readings; the reading resolves 1 C" if len(set(round(x, 6) for x in v)) == 1 else ""
    print("   %-11s per pass %s (runs a pass %s) -> %.2f +- %.2f%s"
          % (it, ["%.3f" % x for x in v], n_runs, m, h, note))
for hi_, lo_ in (("fp32.signs", "fp32.ones"), ("fp16.signs", "fp16.ones"), ("int8.signs", "int8.full"),
                 ("fp32.pm_pi", "anchor_pi")):
    v = [pp(p, hi_, "dT_win") - pp(p, lo_, "dT_win") for p in PASSES]
    m, h = mci(v)
    print("   %s - %s paired per pass %s -> %+.2f +- %.2f C" % (hi_, lo_, ["%+.3f" % x for x in v], m, h))
print("   S (W over idle): int8.signs %.3f, fp32.signs %.3f, fp16.signs %.3f, fp32.pm_pi %.3f (e90.json items.*.S)"
      % tuple(E["items"][k]["S"]["mean"] for k in ("int8.signs", "fp32.signs", "fp16.signs", "fp32.pm_pi")))

# ---------------------------------------------------------------- C5
print()
print("== C5 fp16 against fp32: the sign-bit prices and the two +-1 steps")
rate32 = st.mean(pp(p, "fp32.ones", "rate") for p in PASSES)
rate16 = st.mean(pp(p, "fp16.ones", "rate") for p in PASSES)
fl = P["item_flips"]
pr = P["sign_bit_prices"]
fj = {}
for fmt, rate in (("fp32", rate32), ("fp16", rate16)):
    for side in ("B", "A"):
        x = pr[fmt][side]
        f = x["dW"] / (fl[fmt][side] * rate) * 1e15
        fj[(fmt, side)] = f
        if "se" in x:
            ci = "se %.4f W (n = %d) as frozen; its own README states its interval" % (x["se"], x["n"])
        else:
            ci = "ci95 %s fJ as frozen" % (x.get("fJ_ci95"),)
        print("   %s %s: dW %.4f W at %d flips/op, op rate %.4e /s -> %.1f fJ, %s; source %s"
              % (fmt, side, x["dW"], fl[fmt][side], rate, f, ci, x["source"].split(" ")[0]))
print("   price ratio fp32/fp16, A side: %.2f (from dW and flips; the op rate cancels: %.2f); the README's own fJ "
      "values, E67 247 / E79 71: %.2f" % (fj[("fp32", "A")] / fj[("fp16", "A")],
                                         (pr["fp32"]["A"]["dW"] / fl["fp32"]["A"]) / (pr["fp16"]["A"]["dW"] / fl["fp16"]["A"]),
                                         247 / 71))
print("   price ratio fp32/fp16, B side: %.2f at the point, but fp16 B is a bound (ci95 %s fJ spans 0): at its upper "
      "end the ratio is %.2f, and above it there is no ratio" % (fj[("fp32", "B")] / fj[("fp16", "B")],
                                                                pr["fp16"]["B"]["fJ_ci95"],
                                                                fj[("fp32", "B")] / pr["fp16"]["B"]["fJ_ci95"][1]))
s32 = [pp(p, "fp32.signs", "D") - pp(p, "fp32.ones", "D") for p in PASSES]
s16 = [pp(p, "fp16.signs", "D") - pp(p, "fp16.ones", "D") for p in PASSES]
d = [b - a for a, b in zip(s32, s16)]
m32, h32 = mci(s32)
m16, h16 = mci(s16)
md, hd = mci(d)
rat = [b / a for a, b in zip(s32, s16)]
mr, hr = mci(rat)
pb32 = P["steps"]["fp32.signs-fp32.ones"]["P_bits_w"]
pb16 = P["steps"]["fp16.signs-fp16.ones"]["P_bits_w"]
print("   fp32 +-1 step per pass %s -> %.3f +- %.3f W (scored.json: %.3f +- %.3f)"
      % (["%.3f" % x for x in s32], m32, h32, SC["steps"]["fp32.signs-fp32.ones"]["step_w"]["mean"],
         SC["steps"]["fp32.signs-fp32.ones"]["step_w"]["ci95"]))
print("   fp16 +-1 step per pass %s -> %.3f +- %.3f W (scored.json: %.3f +- %.3f)"
      % (["%.3f" % x for x in s16], m16, h16, SC["steps"]["fp16.signs-fp16.ones"]["step_w"]["mean"],
         SC["steps"]["fp16.signs-fp16.ones"]["step_w"]["ci95"]))
print("   fp16 step minus fp32 step, paired per pass %s -> %+.3f +- %.3f W [%+.3f, %+.3f]"
      % (["%+.3f" % x for x in d], md, hd, md - hd, md + hd))
print("   fp16 step / fp32 step per pass %s -> %.3f +- %.3f" % (["%.3f" % x for x in rat], mr, hr))
print("   the bits model's ratio P_bits(fp16) / P_bits(fp32) = %.3f / %.3f = %.3f: fp16's step would be %.3f W, "
      "%+.3f W from fp32's (%s the paired interval)"
      % (pb16, pb32, pb16 / pb32, pb16 / pb32 * m32, pb16 / pb32 * m32 - m32,
         "outside" if not (md - hd <= pb16 / pb32 * m32 - m32 <= md + hd) else "inside"))
print("   sign flips per op (e90/e90.json tiles.*.stats): fp32.signs A %d + B %d = %d; fp16.signs A %d + B %d = %d"
      % (T["tiles"]["fp32.signs"]["stats"]["sign_flips_per_op_a"], T["tiles"]["fp32.signs"]["stats"]["sign_flips_per_op_b"],
         T["tiles"]["fp32.signs"]["stats"]["sign_flips_per_op_a"] + T["tiles"]["fp32.signs"]["stats"]["sign_flips_per_op_b"],
         T["tiles"]["fp16.signs"]["stats"]["sign_flips_per_op_a"], T["tiles"]["fp16.signs"]["stats"]["sign_flips_per_op_b"],
         T["tiles"]["fp16.signs"]["stats"]["sign_flips_per_op_a"] + T["tiles"]["fp16.signs"]["stats"]["sign_flips_per_op_b"]))

# ---------------------------------------------------------------- C6
print()
print("== C6 the verdict count (scored.json rules, primary leakage slope)")
prim = {r: SC["rules"][r]["verdict"] for r in ("E90-R1", "E90-R2", "E90-R3", "E90-R4", "E90-R5")}
chk = {r: SC["rules"][r]["verdict"] for r in ("E90-S1", "E90-S2")}
print("   primary rules: %s" % prim)
for v in ("PASS", "FAIL", "INCONCLUSIVE"):
    print("      %s: %d (%s)" % (v, sum(1 for x in prim.values() if x == v),
                                ", ".join(k for k, x in prim.items() if x == v) or "none"))
print("   checks: %s" % chk)
