#!/usr/bin/env python3
"""E99, the desk check behind README.md's "Corrections after verification" (C1-C10): every number those corrections cite, read from committed files and
recomputed here. Written Sun 1 Nov 2026 after an independent verifier's report. No card touched, nothing re-run, and no frozen or data file changed.
Run it from this directory with any python3 with numpy:   python3 corrections-check.py > corrections-check.txt

Registered primary arm: dm.json (dips removed, auto slope). Sensitivities: dm-leak0.2936.json, dm-leak0.3803.json. Unfiltered: dm-unfiltered.json. Rails, post hoc and labelled:
posthoc-rails.json, from tools/claims-v3/dm/posthoc_rails.py. Post-hoc account: posthoc-fit.json. Counts: gen/counts.json. Frozen predictions: tools/claims-v3/dm/predictions.json.
"""
import gzip
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))


def J(name):
    return json.load(open(os.path.join(HERE, name)))


A = {"primary": J("dm.json"), "0.2936": J("dm-leak0.2936.json"), "0.3803": J("dm-leak0.3803.json"), "unfiltered": J("dm-unfiltered.json")}
D = A["primary"]
H = D["headline"]
C = H["contrasts_W"]
R = J("posthoc-rails.json")
RC = R["contrasts_W"]
FIT = J("posthoc-fit.json")
N = J(os.path.join("gen", "counts.json"))
PRED = json.load(open(os.path.join(REPO, "tools", "claims-v3", "dm", "predictions.json")))
PASSES = [str(p) for p in D["passes_headline"]]
LR = H["lines_per_s"]
T = 2.7764  # t(0.975, 4)
pj = lambda w: w / LR * 1e12
watts = lambda p: p * 1e-12 * LR
COLS = ("board", "noc", "sram", "minion", "off")


def ci(v):
    v = np.array(v, float)
    m = v.mean()
    h = T * v.std(ddof=1) / math.sqrt(len(v))
    return m, m - h, m + h


def show(x):
    return "%+.3f [%+.3f, %+.3f]" % (x["mean"], x["lo"], x["hi"])


def rail_row(name):
    return "%-14s " % name + "  ".join("%s %s" % (c, show(RC[name][c])) for c in COLS)


def verdict(a, key):
    v = A[a]["verdicts"][key]
    return v if isinstance(v, str) else v.get("verdict", v.get("class"))


print("E99 corrections-check (desk only; committed files only); headline passes %s, %.5e lines/s, t(0.975, 4) = %.4f" % (PASSES, LR, T))
print("the scored verdicts, all four arms, unchanged by these corrections:")
for key in ("R2_hi_no_toggles", "R3_hi_same_toggles", "R4_tent", "R5_whole_byte_scatter", "R6_ties", "R7_encoded_toggles", "R8_raw_toggles", "R9_half", "R10_floor", "R11_period_ladder", "R12_closure", "overall_dbi"):
    print("  %-24s %s" % (key, " | ".join("%s: %s" % (a, verdict(a, key)) for a in A)))

print("\n== C1  Where a one pays: the rails (W, then per one)")
for nm, ones in (("tie18", 448), ("tie27", 320), ("tie45", 64)):
    print(rail_row(nm))
    print("    per one, pJ: " + "  ".join("%s %.2f" % (c, pj(RC[nm][c]["mean"]) / ones) for c in COLS))
print("the fit, floor + one + high over w1, u1, u2, u4, u5, u7, u8, l08, per pass:")
tf = R["tent_fit"]
for c in COLS:
    t = tf[c]
    print("  %-7s floor %+.3f +-%.3f W   one %.2f +-%.2f pJ   high %+.2f +-%.2f pJ" % (c, t["floor_W"], t["floor_half_W"], t["one_pJ"], t["one_half_pJ"], t["high_pJ"], t["high_half_pJ"]))
print("  one, board less the three rails: %.2f pJ" % (tf["board"]["one_pJ"] - tf["noc"]["one_pJ"] - tf["sram"]["one_pJ"] - tf["minion"]["one_pJ"]))
print("NoC over zeros on the 256-one images, high pins 32 to 256:", {n: round(R["items_over_zeros_W"][n]["noc"], 3) for n in ("dm_l08", "dm_a08", "dm_a44", "dp_c1", "dm_u4")}, "| on dm_u8:", round(R["items_over_zeros_W"]["dm_u8"]["noc"], 3))
print("the same-ones arrangement contrasts, on the rails:")
for nm in ("hi_t0", "hi_ta", "t_both", "t_enc", "t_raw", "half", "arr_L2"):
    print(rail_row(nm))
for f, tau in (("noc", 1.04), ("sram", 1.01), ("minion", 1.06)):
    g = 1 - (tau / 2.0) * (math.exp(-2 / tau) - math.exp(-4 / tau))
    print("  lag: %-7s tau %.2f s reads %.1f %% over [2, 4) s; the one's price at a settled rail %.2f pJ" % (f, tau, 100 * g, tf[f]["one_pJ"] / g))
print("  E32 (docs/findings/03-experiments.md:946): 129 fJ per one per hop on the mesh rail, 192 on the board. NoC price / 129 fJ = %.1f hop-equivalents; x 192/129 = %.2f pJ at the board" % (tf["noc"]["one_pJ"] / 0.129, tf["noc"]["one_pJ"] * 192 / 129))

print("\n== C2  The ladder, split by rail (W over dm_L2, class of the off column by E81's rule)")
for n in (1, 3, 4, 8, 16, 17, 32, 256, 8192):
    nm = "L%d_over_L2" % n
    x = RC[nm]["off"]
    cls = "present" if (x["mean"] >= 0.25 and x["lo"] > 0) else "absent" if (x["lo"] >= -0.30 and x["hi"] <= 0.30) else "unresolved"
    print(rail_row(nm) + "   off is " + cls)
for nm in ("L8_minus_L4", "L16_minus_L8", "L16_minus_L4", "L32_minus_L16"):
    print(rail_row(nm))
share = lambda s: 100 * (s["noc"]["mean"] + s["sram"]["mean"]) / s["board"]["mean"]
print("SRAM + NoC share of the board: D %.1f %%, h16 %.1f %%" % (share(RC["L8192_over_L2"]), share(RC["L16_over_L2"])))
print("off: h3 / D %.0f %%, h32 / D %.0f %%" % (100 * RC["L3_over_L2"]["off"]["mean"] / RC["L8192_over_L2"]["off"]["mean"], 100 * RC["L32_over_L2"]["off"]["mean"] / RC["L8192_over_L2"]["off"]["mean"]))
print("path counts on the ten rungs, floor + one count, rms W by column:")
for c in COLS:
    f = R["ladder_fits"][c]
    print("  %-7s k_shire (8-way) %.3f   k_chan (16-way) %.3f   both %.3f" % (c, f["k_shire"]["rms_W"], f["k_chan"]["rms_W"], f["k_shire+k_chan"]["rms_W"]))
print("board, L16 - L8, by arm:")
for a, x in A.items():
    v = [x["per_pass"][p]["items_W"]["dm_L16"] - x["per_pass"][p]["items_W"]["dm_L8"] for p in PASSES]
    print("  %-10s %+.3f [%+.3f, %+.3f]" % ((a,) + ci(v)))
print("board, h8 and h16 by arm (mean, class):", {a: ("%+.3f %s" % (x["headline"]["contrasts_W"]["h8"]["mean"], x["classes"]["h8"]), "%+.3f %s" % (x["headline"]["contrasts_W"]["h16"]["mean"], x["classes"]["h16"])) for a, x in A.items()})
print("the reducer's named reading, as stored and unchanged:", D["verdicts"]["R11_period_ladder"]["reading"])

print("\n== C3  The floor")
print("floor_w1, board, by arm:", {a: "%s %s" % (show(x["headline"]["contrasts_W"]["floor_w1"]), x["classes"]["floor_w1"]) for a, x in A.items()})
print(rail_row("floor_w1"))
items = (("dm_w1", 1, 1), ("dm_u1", 64, 64), ("dm_u2", 128, 128), ("dm_u4", 256, 256), ("dm_u5", 320, 256), ("dm_u7", 448, 128), ("dm_u8", 512, 64), ("dm_l08", 256, 32))
X = np.array([[1.0, w, h] for _, w, h in items])
for a, x in A.items():
    per = np.array([np.linalg.lstsq(X, np.array([x["per_pass"][p]["items_W"][n] - x["per_pass"][p]["items_W"]["dp_zeros"] for n, _, _ in items]), rcond=None)[0] for p in PASSES])
    m = per.mean(axis=0)
    h = T * per.std(axis=0, ddof=1) / math.sqrt(len(PASSES))
    print("  fit, board, %-10s floor %+.3f [%+.3f, %+.3f]   one %.2f +-%.2f pJ   high %.2f +-%.2f pJ" % (a, m[0], m[0] - h[0], m[0] + h[0], pj(m[1]), pj(h[1]), pj(m[2]), pj(h[2])))
print("one bit and one high pin at 3.3 and 1.7 pJ: %.4f W; floor_w1 is %.0f times that" % (watts(5.0), C["floor_w1"]["mean"] / watts(5.0)))
print("the six frozen floors, W:", {m: round(v["floor_W"], 3) for m, v in PRED["fits"].items()})

print("\n== C4  The three rails on E81's step and on the top of the ladder")
print(rail_row("tie_total"))
print(rail_row("L8192_over_L2"))
print("SRAM + NoC share: tie_total %.1f %%, D %.1f %%" % (share(RC["tie_total"]), share(RC["L8192_over_L2"])))

print("\n== C5  R12's parts")
for a, x in A.items():
    v = x["verdicts"]["R12_closure"]
    p = v["parts_W"]
    two = p["high"] + p["encoded"]
    print("  %-10s high %+.3f encoded %+.3f raw %+.3f = %+.3f; measured arr_L2 %+.3f, short by %.3f; high + encoded %+.3f, %.0f %% of it, miss %.3f; verdict %s" % (a, p["high"], p["encoded"], p["raw"], sum(p.values()), v["measured_arr_L2_W"], v["measured_arr_L2_W"] - sum(p.values()), two, 100 * two / v["measured_arr_L2_W"], v["measured_arr_L2_W"] - two, v["verdict"]))
per = []
for p in PASSES:
    c = D["per_pass"][p]["contrasts_W"]
    ph = c["hi_ta"] / 192
    pe = (c["t_enc"] - 32 * ph) / 434
    per.append(pj((c["t_raw"] - 62 * pe) / 496))
print("  the raw price, per pass, pJ: %.3f [%.3f, %.3f]" % ci(per))

print("\n== C6  High pins' share of E81's 1.636 W (177 high pins, dp_bern - dp_c2)")
for pjv in (1.04, 1.47, 1.71, 1.86, 2.57):
    print("  at %.2f pJ: %.3f W, %.1f %%" % (pjv, watts(177 * pjv), 100 * watts(177 * pjv) / 1.636))
print("  the three direct prices [95 %%], pJ: hi_t0/224 %.2f [%.2f, %.2f], hi_ta/192 %.2f [%.2f, %.2f], tent_S/256 %.2f [%.2f, %.2f]" % (
    pj(C["hi_t0"]["mean"]) / 224, pj(C["hi_t0"]["lo"]) / 224, pj(C["hi_t0"]["hi"]) / 224, pj(C["hi_ta"]["mean"]) / 192, pj(C["hi_ta"]["lo"]) / 192, pj(C["hi_ta"]["hi"]) / 192,
    pj(C["tent_S"]["mean"]) / 256, pj(C["tent_S"]["lo"]) / 256, pj(C["tent_S"]["hi"]) / 256))

print("\n== C7  What `half` moves besides half (dp_c1 - dm_l08)")
FC = FIT["counts"]
print("  ", {k: FC["e99:dp_c1"][k] - FC["e99:dm_l08"][k] for k in ("w", "hi", "t_enc", "t_raw", "r32", "r64", "r128", "half", "k")})
c1 = np.frombuffer(open(os.path.join(HERE, "gen", "srcs", "dp_c1.bin"), "rb").read(), dtype=np.uint8).reshape(-1, 64)
l8 = np.frombuffer(open(os.path.join(HERE, "gen", "srcs", "dm_l08.bin"), "rb").read(), dtype=np.uint8).reshape(-1, 64)
pop = np.array([bin(i).count("1") for i in range(256)])
print("   ones in the first 32 B: dp_c1 %d, dm_l08 %d" % (pop[c1[0, :32]].sum(), pop[l8[0, :32]].sum()))
print("   half/256: %.2f pJ [%.2f, %.2f]; the post-hoc fit's half: %.2f +-%.2f pJ" % (pj(C["half"]["mean"]) / 256, pj(C["half"]["lo"]) / 256, pj(C["half"]["hi"]) / 256, FIT["chosen"]["prices_pJ"]["half"], FIT["chosen"]["prices_half_pJ"]["half"]))
print(rail_row("half"))

print("\n== C8  The 18 points")
ro = FIT["chosen"]["residuals_old_W"]
same = {"e81:dp_c1", "e81:dp_c2", "e81:dp_bern", "e75:mf_k0", "e75:mf_k256"}
a_ = [v for k, v in ro.items() if k not in same]
b_ = [v for k, v in ro.items() if k in same]
rms = lambda v: math.sqrt(sum(x * x for x in v) / len(v))
print("   all %d: %.3f W; the %d whose images it never fitted: %.3f W; the %d byte-identical to fitted items: %.3f W" % (len(ro), rms(list(ro.values())), len(a_), rms(a_), len(b_), rms(b_)))
print("   dp_random and mf_random are one image (the same counts: %s)" % (FC["e81:dp_random"] == FC["e75:mf_random"]))
print("   the search, lowest out of sample:", sorted((round(v["rms_out_of_sample_W"], 3), k) for k, v in FIT["search"].items())[:4])
print("   the search, lowest in sample:", sorted((round(v["rms_W"], 3), k) for k, v in FIT["search"].items())[:4])
r64 = {n: FC["e99:dm_L%d" % n]["r64"] for n in (1, 2, 3, 4, 8, 16, 17, 32, 256, 8192)}
print("   r64 across the ladder: %s; span %.1f, %.3f W at the fit's %.2f pJ" % ({k: round(v, 1) for k, v in r64.items()}, max(r64.values()) - min(r64.values()), watts((max(r64.values()) - min(r64.values())) * FIT["chosen"]["prices_pJ"]["r64"]), FIT["chosen"]["prices_pJ"]["r64"]))

print("\n== C9  Sources")
with gzip.open(os.path.join(HERE, "passes", "p9911", "telemetry.jsonl.gz"), "rt") as fh:
    for line in fh:
        if line.startswith("{"):
            s = json.loads(line)
            print("   telemetry reg_mv.vddqlp %s mV, reg_mv.vddq %s mV, reg_mv.ddr %s mV" % (s["reg_mv"]["vddqlp"], s["reg_mv"]["vddq"], s["reg_mv"]["ddr"]))
            break
for V in (0.60, 0.64):
    print("   half of %.2f V across 40 ohm: %.1f mA, %.2f mW; per beat at 3,733 MT/s: %.2f pJ at the pad" % (V, V / 2 / 40 * 1e3, V * V / 2 / 40 * 1e3, V * V / 2 / 40 / 3.733e9 * 1e12))
print("   t_raw's power over the byte order: at most 62 DMI toggles x %.2f pJ = %.3f W, against an interval half-width %.3f W" % (pj(C["t_both"]["mean"]) / 496, watts(62 * pj(C["t_both"]["mean"]) / 496), (C["t_raw"]["hi"] - C["t_raw"]["lo"]) / 2))
print("   the inversion rule, against the eleven images with no line change and half 0 (u1..u8, l08, a08..a44), floor-free fit of one + high + encoded toggle on the board, and what each rule predicts for tie45, measured %s:" % show(C["tie45"]))
names = ("dm_u1", "dm_u2", "dm_u4", "dm_u5", "dm_u7", "dm_u8", "dm_l08", "dm_a08", "dm_a26", "dm_a35", "dm_a44")
y = np.array([H["items_over_zeros_W"][n]["mean"] for n in names])
P9 = np.array([bin(i).count("1") for i in range(512)])


def table(rule):
    out = []
    for b in range(256):
        p = pop[b]
        inv = ((~b) & 0xFF)
        if rule == "standard":
            out.append(inv | 0x100 if p > 4 else b)
        elif rule == "no inversion":
            out.append(b)
        elif rule == "inverts at p >= 4":
            out.append(inv | 0x100 if p >= 4 else b)
        elif rule == "DMI level reversed":
            out.append(inv if p > 4 else b | 0x100)
        elif rule == "DMI pin free":
            out.append(inv if p > 4 else b)
    return np.array(out)


for rule in ("standard", "no inversion", "inverts at p >= 4", "DMI level reversed", "DMI pin free"):
    E = table(rule)
    base = P9[E[0]] * 64

    def feat(n):
        L = np.frombuffer(open(os.path.join(HERE, "gen", "srcs", n + ".bin"), "rb").read(), dtype=np.uint8).reshape(-1, 64)
        e = E[L]
        return [pop[L].sum(axis=1).mean(), P9[e].sum(axis=1).mean() - base, P9[e[:, 2:] ^ e[:, :-2]].sum(axis=1).mean()]

    XX = np.array([feat(n) for n in names])
    coef = np.linalg.lstsq(XX, y, rcond=None)[0]
    r = y - XX @ coef
    t45 = (np.array(feat("dm_u5")) - np.array(feat("dm_u4"))) @ coef
    print("     %-20s rms %.3f W   one %.2f high %.2f toggle %.2f pJ   tie45 %+.3f W" % (rule, math.sqrt(np.mean(r ** 2)), pj(coef[0]), pj(coef[1]), pj(coef[2]), t45))

print("\n== C10  Wording")
print("the frozen models against every registered contrast: outside the 95 % prediction interval")
for m in PRED["fits"]:
    out = []
    for c, sp in PRED["contrasts"].items():
        q = sp["pred"][m]
        if abs(C[c]["mean"] - q["pred_W"]) > q["pi95_W"]:
            out.append("%s (%+.2f against %+.2f +-%.2f)" % (c, C[c]["mean"], q["pred_W"], q["pi95_W"]))
    print("  %-12s %d: %s" % (m, len(out), "; ".join(out[:9])))
print("h1 on the board %s; L2 - L1 on the SRAM rail %.3f; dp_c2 - dp_c1 on the SRAM rail %s" % (show(C["h1"]), -RC["L1_over_L2"]["sram"]["mean"], show(RC["c2_vs_c1"]["sram"])))
readme = open(os.path.join(HERE, "README.md")).read()
print("the note on the floor appears in Step 1: %d time(s)" % readme.count("*(It did, Sun 1 Nov 2026"))
print("sensitivity range of the price of a one by pair and arm, pJ:", {a: [round(pj(x["headline"]["contrasts_W"][c]["mean"]) / n, 2) for c, n in (("tie27", 320), ("tie18", 448), ("tie45", 64))] for a, x in A.items()})
