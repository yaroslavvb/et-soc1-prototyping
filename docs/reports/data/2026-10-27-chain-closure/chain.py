#!/usr/bin/env python3
"""Q128(f) — close the chain from the card's side: a flipped operand bit to the TFLOPS gap.

Reads ONLY committed data in the public lab repo (E38/21 Sep, E60, E64, E65, E67).
Fits nothing on anything measured tonight. Writes chain.json and prints the report.

  usage: /usr/local/bin/python3.12 chain.py <repo-root> <out-dir>
"""
import json, math, os, re, sys

REPO, OUT = sys.argv[1], sys.argv[2]
D = os.path.join(REPO, "docs/reports/data")
os.makedirs(OUT, exist_ok=True)
R = {}
say = print


def load(p):
    with open(os.path.join(D, p)) as f:
        return json.load(f)


# ───────────────────────────────────────────────────────── inputs
E65 = load("2026-10-26-e65-bit-prices-hart-ladder/hl.json")["cards"]["aifoundry3"]
LAD = load("2026-10-26-e65-bit-prices-hart-ladder/ladder.json")
E67H = load("2026-10-27-e67-a-side-bit-prices/hl.json")["cards"]["aifoundry3"]
E67C = load("2026-10-27-e67-a-side-bit-prices/closure.json")
E67S = load("2026-10-27-e67-a-side-bit-prices/scored.json")
E60 = load("2026-10-20-bitflip-ladder/hl.json")["cards"]

LANES, B_PRES, A_PRES = 4096, 4096, 2048
PEAK_TFLOPS = 12.3            # E64, fp32, 1,024 harts, 800 MHz

# E64's descriptive surface, parsed from its committed surface.txt
SURF = open(os.path.join(D, "2026-10-23-e64-horace-power-limit/surface.txt")).read()
Bf = {int(k): float(v) for k, v in re.findall(r"(\d+): ([\d.]+)", SURF.split("\n")[0])}
GOV = eval(re.search(r"governor (\{[^}]*\})", SURF).group(1))
THERM = {k: float(v) for k, v in re.findall(r"'(k_c_per_w|a_c|cap_w_at_65_5)': ([\d.]+)", SURF)}
E64P = {}                     # workload -> {600,700,800} board W, averaged over its repeats
for lab, trip in re.findall(r"fp32-([a-z0-9_]+)-1024\s+p (\{[^}]*\})", SURF):
    d = eval(trip)
    E64P.setdefault(lab, []).append(d)
E64P = {k: {f: sum(d[f] for d in v) / len(v) for f in (600, 700, 800)} for k, v in E64P.items()}

# ═════════════════════════════════════ 1. the price list
pB = {int(k): v for k, v in E65["bits"].items()}
pA = {int(k): v for k, v in E67H["a_bits"].items()}
pBpi = {int(k): v for k, v in E65["bits_pi"].items()}
pB_fJ = {j: v["J_per_alternating_bit"] * 1e15 for j, v in pB.items()}
pA_fJ = {j: v["J_per_alternating_bit"] * 1e15 for j, v in pA.items()}
pB_se = {j: v["se"] / v["dW"] * pB_fJ[j] for j, v in pB.items()}
pA_se = {j: v["se"] / v["dW"] * pA_fJ[j] for j, v in pA.items()}
rate65, rate67, v600 = E65["items"]["lq_h0"]["rate"], E67H["anchors"]["anchor_zeros"]["rate"], E65["v_mean"]

say("=" * 86)
say("1. THE PRICE LAW — one flipped operand bit, aifoundry3, 600 MHz, %.1f mV" % (v600 * 1000))
say("=" * 86)
say("  B side (E65 block A, quiet partner A=1.0): 32 positions, %.0f-%.0f fJ, span %.1fx"
    % (min(pB_fJ.values()), max(pB_fJ.values()), max(pB_fJ.values()) / min(pB_fJ.values())))
say("  A side (E67 block 1, quiet partner B=1.0): 32 positions, %.0f-%.0f fJ, span %.1fx"
    % (min(pA_fJ.values()), max(pA_fJ.values()), max(pA_fJ.values()) / min(pA_fJ.values())))
e60b = {int(k): v["J_per_alternating_bit"] * 1e15 for k, v in E60["aifoundry3"]["bits"].items()}
rr = sorted(pB_fJ[j] / e60b[j] for j in e60b)
say("  independent check — E60's 6 B positions, same card and clock, six days earlier:")
say("    " + "  ".join("bit %d: %.0f vs %.0f" % (j, e60b[j], pB_fJ[j]) for j in sorted(e60b)))
say("    E65/E60 ratio: median %.3f, range %.3f-%.3f" % (rr[len(rr) // 2], rr[0], rr[-1]))


def regimes(p):
    return dict(low_mantissa_mean=sum(p[j] for j in range(10)) / 10, bit22=p[22],
                exponent_mean=sum(p[j] for j in range(23, 31)) / 8, sign=p[31])


R["price_list"] = {"card": "aifoundry3", "clock_mhz": 600, "v_mean": v600,
                   "B_fJ": pB_fJ, "B_se_fJ": pB_se, "A_fJ": pA_fJ, "A_se_fJ": pA_se,
                   "B_pi_fJ": {j: v["J_per_alternating_bit"] * 1e15 for j, v in pBpi.items()},
                   "shape": {"B": regimes(pB_fJ), "A": regimes(pA_fJ)},
                   "e60_check": {"e60_fJ": e60b, "ratio_median": rr[len(rr) // 2],
                                 "ratio_min": rr[0], "ratio_max": rr[-1]},
                   "source": {"B": "E65 hl.json cards.aifoundry3.bits",
                              "A": "E67 hl.json cards.aifoundry3.a_bits (registered passes)"}}
say("  shape  B: low-mantissa mean %3.0f fJ, bit 22 %4.0f fJ, exponent mean %3.0f fJ, sign %3.0f fJ"
    % tuple(regimes(pB_fJ)[k] for k in ("low_mantissa_mean", "bit22", "exponent_mean", "sign")))
say("         A: low-mantissa mean %3.0f fJ, bit 22 %4.0f fJ, exponent mean %3.0f fJ, sign %3.0f fJ"
    % tuple(regimes(pA_fJ)[k] for k in ("low_mantissa_mean", "bit22", "exponent_mean", "sign")))

# ═════════════════════════════════════ 2. within-word saturation
say("")
say("=" * 86)
say("2. SATURATION — E60's lq ladder: the h low mantissa bits of B flipping in one word")
say("=" * 86)
a3, rate60 = E60["aifoundry3"], E60["aifoundry3"]["items"]["lq_h0"]["rate"]
lq_rows = []
for _, rung in sorted(a3["lq"]["rungs"].items(), key=lambda kv: kv[1]["h"]):
    h = rung["h"]
    if h == 0 or rung["dW"] is None:
        continue
    flips = h * B_PRES                       # manifest b_all for lq_h<h>; re-derived here
    meas_J = rung["dW"] / rate60
    nv = sum(pB_fJ[j] for j in range(h)) * 1e-15 * B_PRES
    lq_rows.append(dict(h=h, dW=rung["dW"], se=rung["se"], flips=flips, meas_J=meas_J, naive_J=nv,
                        ratio=meas_J / nv, meas_fJ_per_bit=meas_J / flips * 1e15,
                        naive_fJ_per_bit=nv / flips * 1e15))
say("   m   measured W     SE    measured fJ/bit   price-list fJ/bit   measured/list")
for r in lq_rows:
    say("  %2d    %8.3f  %6.3f         %7.1f             %7.1f            %.3f"
        % (r["h"], r["dW"], r["se"], r["meas_fJ_per_bit"], r["naive_fJ_per_bit"], r["ratio"]))
say("")
say("  The measured price per flipped bit barely moves — %.0f to %.0f fJ over m = 1 to 23 — while the"
    % (min(r["meas_fJ_per_bit"] for r in lq_rows), max(r["meas_fJ_per_bit"] for r in lq_rows)))
say("  single-bit price list says it should run from %.0f to %.0f fJ per bit over the same masks."
    % (min(r["naive_fJ_per_bit"] for r in lq_rows), max(r["naive_fJ_per_bit"] for r in lq_rows)))
say("  The position premium is a SINGLE-BIT effect: it does not add when bits flip together.")

# three candidate laws, scored on the same seven rungs
C_FLAT = sum(r["meas_J"] for r in lq_rows) / sum(r["flips"] for r in lq_rows) * 1e15     # fJ/bit, flat
pred_flat = [C_FLAT * 1e-15 * r["flips"] * rate60 for r in lq_rows]
pts = [(math.log(r["h"]), math.log(r["ratio"])) for r in lq_rows if r["h"] > 1]
slope = sum(x * y for x, y in pts) / sum(x * x for x, _ in pts)
ALPHA = 1 + slope
pred_pos = [r["naive_J"] * r["h"] ** (ALPHA - 1) * rate60 for r in lq_rows]
xs = [math.log(r["h"]) for r in lq_rows]; ys = [math.log(r["dW"]) for r in lq_rows]
nn = len(xs); mx = sum(xs) / nn; my = sum(ys) / nn
BETA = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
C_POW = math.exp(my - BETA * mx)
pred_pow = [C_POW * r["h"] ** BETA for r in lq_rows]


def score(p):
    e = [(q - r["dW"]) / r["dW"] for q, r in zip(p, lq_rows)]
    return 100 * math.sqrt(sum(x * x for x in e) / len(e)), 100 * max(abs(x) for x in e)


laws = [("flat, %.0f fJ per flipped bit, position ignored" % C_FLAT, pred_flat, score(pred_flat)),
        ("price list x m^(alpha-1), alpha = %.3f" % ALPHA, pred_pos, score(pred_pos)),
        ("free power law, %.3f W x m^%.3f" % (C_POW, BETA), pred_pow, score(pred_pow))]
say("")
say("  three candidate laws on these seven rungs:")
for nm, _, (rms_, mx_) in laws:
    say("    %-46s rms %5.1f%%   worst %5.1f%%" % (nm, rms_, mx_))
say("  >>> the flat law wins, and the free power law's exponent %.3f is 1.00 within its scatter:" % BETA)
say("      inside one word, board power counts flipped bits and all but ignores which ones.")
R["saturation"] = {
    "lq_rows": lq_rows,
    "flat_fJ_per_bit": C_FLAT, "alpha": ALPHA, "beta": BETA, "c_pow_W": C_POW,
    "law_scores_pct": {"flat": {"rms": laws[0][2][0], "worst": laws[0][2][1]},
                       "price_list_compressed": {"rms": laws[1][2][0], "worst": laws[1][2][1]},
                       "free_power": {"rms": laws[2][2][0], "worst": laws[2][2][1]}},
    "finding": "within one word the per-bit price is flat (87-129 fJ) while the single-bit list "
               "predicts 106-382 fJ per bit for the same masks; the position premium does not add",
    "source": "E60 lq rungs, aifoundry3 600 MHz; single-bit prices from E65 block A"}


def g(m):
    """the compressed-price-list law, kept for the bracket in part 4"""
    return m ** (ALPHA - 1) if m > 0 else 1.0

# ═════════════════════════════════════ 3. cross-operand
say("")
say("=" * 86)
say("3. CROSS-OPERAND — E67's 4x4 grid (one A bit AND one B bit flipping at once)")
say("=" * 86)
cells = E67H["ix"]["cells"]
n = len(cells)
rt = sorted(c["cell_dW"] / c["sum_dW"] for c in cells.values())
pooled = sum(c["cell_dW"] for c in cells.values()) / sum(c["sum_dW"] for c in cells.values())
sx = sum(c["sum_dW"] for c in cells.values()); sy = sum(c["cell_dW"] for c in cells.values())
sxx = sum(c["sum_dW"] ** 2 for c in cells.values()); sxy = sum(c["sum_dW"] * c["cell_dW"] for c in cells.values())
sl = (n * sxy - sx * sy) / (n * sxx - sx * sx); ic = (sy - sl * sx) / n
rmsc = math.sqrt(sum((c["cell_dW"] - (ic + sl * c["sum_dW"])) ** 2 for c in cells.values()) / n)
wo = E67S["whole_operand_additivity"]
say("  16 cells: cell/sum median %.3f, range %.3f-%.3f, pooled %.3f" % (rt[n // 2], rt[0], rt[-1], pooled))
say("  affine fit  cell = %.3f W + %.3f x sum  (rms %.3f W)" % (ic, sl, rmsc))
say("  whole-operand test (E67, ~13.5 + ~13.9 bits): both random %.3f W, one side + the other %.3f W, ratio %.3f"
    % (wo["both_random_W"], wo["sum_of_one_sided_W"], wo["ratio"]))
say("  >>> cross-operand sub-additivity is about the same size at 1+1 bits (%.2f) and at 13.5+13.9 (%.2f)."
    % (pooled, wo["ratio"]))
KAPPA = wo["ratio"]
R["cross_operand"] = {"grid_pooled": pooled, "grid_median": rt[n // 2], "grid_min": rt[0], "grid_max": rt[-1],
                      "grid_affine": {"intercept_W": ic, "slope": sl, "rms_W": rmsc},
                      "whole_operand_ratio": wo["ratio"], "kappa_used": KAPPA}

# ═════════════════════════════════════ 4. superposition
say("")
say("=" * 86)
say("4. SUPERPOSITION — do the per-bit prices add up to the Horace step?")
say("=" * 86)
na, nb = E67C["items"]["nrd_a"], E67C["items"]["nrd_b"]
Ah, Bh = na["A_hist"], nb["B_hist"]
mA, mB = sum(Ah) / A_PRES, sum(Bh) / B_PRES
say("  flipped bits of a random normal operand, counted on the committed tiles (seed 20261020):")
say("    A stream %d flips / %d transitions = %.2f bits each; B stream %d / %d = %.2f bits each"
    % (sum(Ah), A_PRES, mA, sum(Bh), B_PRES, mB))
say("    sign and mantissa flip on about half the transitions; the exponent's top bits almost never:")
say("      A bits 23..30 %s   B bits 23..30 %s" % (Ah[23:31], Bh[23:31]))
S_A = sum(Ah[j] * pA_fJ[j] * 1e-15 for j in range(32)) * na["rate_ops_s"]
S_B = sum(Bh[j] * pB_fJ[j] * 1e-15 for j in range(32)) * nb["rate_ops_s"]
assert abs(S_A - na["predicted_W"]) < 1e-6 and abs(S_B - nb["predicted_W"]) < 1e-6
pa_, pb_ = S_A * g(mA), S_B * g(mB)
# the other end of the bracket: the flat in-company price. The ladder measured it on the B side;
# the A side has no ladder, so it is carried over by the A/B ratio of the single-bit lists.
AB = sum(pA_fJ.values()) / sum(pB_fJ.values())
fa_ = C_FLAT * AB * 1e-15 * sum(Ah) * na["rate_ops_s"]
fb_ = C_FLAT * 1e-15 * sum(Bh) * nb["rate_ops_s"]
say("")
say("  one side random, the other constant — the two measured stimuli that can be counted exactly:")
for nm, S, hi, lo, it in (("nrd_a (A random, B=1.0)", S_A, pa_, fa_, na),
                          ("nrd_b (A=1.0, B random)", S_B, pb_, fb_, nb)):
    say("    %-24s naive %6.3f W  compressed list %6.3f  flat law %6.3f   measured %6.3f +- %.3f"
        % (nm, S, hi, lo, it["measured_W"], it["measured_se"]))
    say("    %24s                       (%.2fx)            (%.2fx)"
        % ("", hi / it["measured_W"], lo / it["measured_W"]))
both_meas = wo["both_random_W"]
both_pred = KAPPA * (pa_ + pb_)
both_flat = KAPPA * (fa_ + fb_)
say("  both operands random (anchor_randn above the constant-operand level):")
say("    naive sum of the two price lists      %6.3f W   %.2fx measured" % (S_A + S_B, (S_A + S_B) / both_meas))
say("    compressed list, x g(m) then x %.3f   %6.3f W   %.2fx" % (KAPPA, both_pred, both_pred / both_meas))
say("    flat in-company price, x %.3f         %6.3f W   %.2fx" % (KAPPA, both_flat, both_flat / both_meas))
say("    measured                              %6.3f W" % both_meas)
say("  >>> the two laws BRACKET the measurement: %.1f W to %.1f W against %.1f W measured (%+.0f%% / %+.0f%%)."
    % (both_flat, both_pred, both_meas, 100 * (both_flat / both_meas - 1), 100 * (both_pred / both_meas - 1)))
say("      Neither is right. The flat law is fitted on contiguous LOW mantissa bits; random operands")
say("      also flip the dear high-mantissa bits, which the flat law prices at the floor. The")
say("      compressed list keeps too much of the single-bit premium. The missing experiment is below.")
anch = {k: v["p80"] for k, v in E67H["anchors"].items()}
ase = {k: v["se"] for k, v in E67H["anchors"].items()}
zeros_W, ones_W, randn_W = anch["anchor_zeros"], anch["anchor_ones"], anch["anchor_randn"]
clocking, data_meas = ones_W - zeros_W, randn_W - ones_W
step_meas = randn_W - zeros_W
say("")
say("  E67's registered anchors (aifoundry3, 600 MHz, board W): zeros %.3f, ones %.3f, pi %.3f, randn %.3f"
    % (zeros_W, ones_W, anch["anchor_pi"], randn_W))
say("    the Horace step (random - zeros) %.3f W = clocking (ones - zeros) %.3f + data (random - ones) %.3f"
    % (step_meas, clocking, data_meas))
say("    price list predicts the data term  %.3f W = %.0f%% of it; the whole step to %.0f%%."
    % (both_pred, 100 * both_pred / data_meas, 100 * (clocking + both_pred) / step_meas))
R["superposition"] = {"flat_law_W": {"A": fa_, "B": fb_, "both": both_flat},
                      "A_over_B_single_bit_ratio": AB,
                      "bracket_both_random_W": [both_flat, both_pred],
                      "m_A": mA, "m_B": mB, "A_hist": Ah, "B_hist": Bh,
                      "naive_W": {"A": S_A, "B": S_B, "both": S_A + S_B},
                      "within_word_W": {"A": pa_, "B": pb_, "both": pa_ + pb_},
                      "cross_operand_W": both_pred,
                      "measured_W": {"nrd_a": na["measured_W"], "nrd_b": nb["measured_W"], "both_random": both_meas},
                      "pred_over_meas": {"nrd_a": pa_ / na["measured_W"], "nrd_b": pb_ / nb["measured_W"],
                                         "both_random": both_pred / both_meas},
                      "anchors_W": anch, "anchors_se_W": ase, "step_W": step_meas,
                      "clocking_W": clocking, "data_W": data_meas}

# ═════════════════════════════════════ 5. the budget
say("")
say("=" * 86)
say("5. THE PER-MULTIPLY-ADD BUDGET — aifoundry3, 600 MHz, 1,024 harts")
say("=" * 86)
mac_s = LANES * rate67
pj = lambda w: w / mac_s * 1e12
rn_s, zr_s = LAD["sessions"]["randn"], LAD["sessions"]["zeros"]
b_rn = sum(f["b_W_per_hart"] for f in rn_s["fits_per_lap"]["deleaked"]) / 3
b_zr = sum(f["b_W_per_hart"] for f in zr_s["fits_per_lap"]["deleaked"]) / 3
idle = (rn_s["pre_idle_board_w"] + zr_s["pre_idle_board_w"]) / 2
say("  %.4g minion-ops/s x %d lanes = %.4g multiply-adds/s = %.2f TFLOP/s at 600 MHz"
    % (rate67, LANES, mac_s, 2 * mac_s / 1e12))
say("")
say("  term                                             board W    pJ per multiply-add   source")
say("  ------------------------------------------------ -------    -------------------   ------")
LEAK = load("2026-10-26-e65-bit-prices-hart-ladder/hl.json")["gates"]["aifoundry3"]["leak_W_per_C"]
say("  card idle, no kernel                              %6.2f          -               E65 hart ladder" % idle)
say("  leakage slope                                     %6.3f W/C     -               E65 gates" % LEAK)
say("  per hart, zeros                                   %6.3f mW      -               E65 hart ladder" % (b_zr * 1000))
say("  per hart, random normal                           %6.3f mW      -               E65 hart ladder" % (b_rn * 1000))
say("  zeros, whole board at 1,024 harts                 %6.2f       %6.3f           E67 anchor" % (zeros_W, pj(zeros_W)))
say("  clocking (ones - zeros)                           %6.2f       %6.3f           E67 anchors" % (clocking, pj(clocking)))
say("  data (random - ones)                              %6.2f       %6.3f           E67 anchors" % (data_meas, pj(data_meas)))
say("  random normal, whole board                        %6.2f       %6.3f           E67 anchor" % (randn_W, pj(randn_W)))
say("")
say("  E38 (21 Sep, aifoundry2) measured the same three terms per multiply-add over idle:")
say("    zeros 0.27 pJ, ones 2.13 pJ, random 5.78 pJ -> clocking 1.86 pJ, data 3.65 pJ")
say("    this work, on the other card five weeks later: clocking %.2f pJ, data %.2f pJ  (%.0f%% and %.0f%%)"
    % (pj(clocking), pj(data_meas), 100 * pj(clocking) / 1.86, 100 * pj(data_meas) / 3.65))
say("  and the hart ladder says the data term is linear in harts: %.1f mW/hart random against %.1f zeros,"
    % (b_rn * 1000, b_zr * 1000))
say("  intercept %.2f W, i.e. no fixed per-kernel offset (E65 C1/C2: 'neither band')."
    % (sum(f["a_W"] for f in rn_s["fits_per_lap"]["deleaked"]) / 3))
R["budget_600"] = {"leak_W_per_C": LEAK, "rate_minion_ops_s": rate67, "mac_per_s": mac_s, "tflops_600": 2 * mac_s / 1e12,
                   "idle_board_W": idle, "mW_per_hart_zeros": b_zr * 1000, "mW_per_hart_randn": b_rn * 1000,
                   "zeros_W": zeros_W, "ones_W": ones_W, "randn_W": randn_W,
                   "clocking_W": clocking, "data_W": data_meas,
                   "pJ_per_mac": {"zeros_board": pj(zeros_W), "clocking": pj(clocking),
                                  "data": pj(data_meas), "randn_board": pj(randn_W)},
                   "e38_pJ": {"zeros": 0.27, "ones": 2.13, "random": 5.78, "clocking": 1.86, "data": 3.65}}

# ═════════════════════════════════════ 6. the chain end to end
say("")
say("=" * 86)
say("6. END TO END — 600 MHz board power -> 800 MHz -> E64's governor -> clock -> TFLOPS")
say("=" * 86)
v800a, v800b = E60["aifoundry1-c0"]["v_mean"], E60["aifoundry2"]["v_mean"]
v800 = (v800a + v800b) / 2
vv = (v800 / v600) ** 2
sh = sorted(set(E60["aifoundry1-c0"]["bits"]) & set(E60["aifoundry3"]["bits"]), key=int)
r8 = [E60["aifoundry1-c0"]["bits"][k]["J_per_alternating_bit"] / E60["aifoundry3"]["bits"][k]["J_per_alternating_bit"]
      for k in sh]
say("  operating points (E60): 600 MHz %.4f V; 800 MHz %.4f V (aifoundry1-c0), %.4f V (aifoundry2), mean %.4f"
    % (v600, v800a, v800b, v800))
say("  so a flip's energy should scale by V^2 = %.3f; the six bit prices measured at both clocks give"
    % vv)
say("  %s, mean %.3f (a cross-card comparison, hence the spread)." % (", ".join("%.2f" % x for x in r8), sum(r8) / len(r8)))
say("  E64's static board line B(f) = %s W; die line T = %.2f + %.4f x W; governor %s"
    % (Bf, THERM["a_c"], THERM["k_c_per_w"], GOV))
P_CAP, T_TRIP = 65.0, 66.0
W_SUS = (T_TRIP - THERM["a_c"]) / THERM["k_c_per_w"]


def vlin(f):
    return v600 + (v800 - v600) * (f - 600) / 200.0


def B_at(f):
    k = sorted(Bf)
    if f <= k[0]:
        return Bf[k[0]]
    for a, b in zip(k, k[1:]):
        if f <= b:
            return Bf[a] + (Bf[b] - Bf[a]) * (f - a) / (b - a)
    return Bf[k[-1]]


def P_of(f, dyn600):
    """Board W at f: E64's static line plus the 600 MHz dynamic part scaled by f and V(f)^2."""
    return B_at(f) + dyn600 * (f / 600.0) * ((vlin(f) / v600) ** 2)


def settle(dyn600, cap):
    lo, hi = 600.0, 800.0
    if P_of(hi, dyn600) <= cap:
        return hi
    if P_of(lo, dyn600) >= cap:
        return lo
    for _ in range(90):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if P_of(m, dyn600) <= cap else (lo, m)
    return lo


# two variants: (M) the 600 MHz board levels as MEASURED by E67; (P) the random level rebuilt
# from the PRICE LIST (zeros + clocking + the predicted data term).
dynM = {"zeros": zeros_W - Bf[600], "ones": ones_W - Bf[600], "randn": randn_W - Bf[600]}
dynP = dict(dynM, randn=(zeros_W + clocking + both_pred) - Bf[600])
dynF = dict(dynM, randn=(zeros_W + clocking + both_flat) - Bf[600])
say("")
say("  predicted board power (W), aifoundry3 levels on E64's static line:")
say("    f     zeros   ones   randn(M)  randn(P)  randn(F)   E64 measured, aifoundry2: zeros/ones/randn")
tabs = {}
for f in (600, 700, 800):
    row = {k: P_of(f, dynM[k]) for k in dynM}
    row["randn_P"] = P_of(f, dynP["randn"]); row["randn_F"] = P_of(f, dynF["randn"])
    tabs[f] = row
    say("   %3d   %6.2f %6.2f   %6.2f    %6.2f    %6.2f    %6.2f / %6.2f / %6.2f"
        % (f, row["zeros"], row["ones"], row["randn"], row["randn_P"], row["randn_F"],
           E64P["zeros"][f], E64P["ones"][f], E64P["randn"][f]))
say("  the card-independent quantity is the step; predicted vs E64 measured (random - zeros):")
for f in (600, 700, 800):
    pm = tabs[f]["randn"] - tabs[f]["zeros"]; em = E64P["randn"][f] - E64P["zeros"][f]
    say("    %3d MHz  predicted %6.2f W   measured %6.2f W   ratio %.3f" % (f, pm, em, pm / em))
say("")
say("  governor: the ~%.1f s average of board power is held to %.0f W; the die trips at %.0f C,"
    % (GOV["tau_s"], P_CAP, T_TRIP))
say("  so the sustained board cap is (%.0f - %.2f)/%.4f = %.1f W." % (T_TRIP, THERM["a_c"], THERM["k_c_per_w"], W_SUS))
say("")
say("  workload                burst MHz   burst TFLOPS   sustained MHz   sustained TFLOPS")
res = {}
for lab, key, dyn in (("zeros", "zeros", dynM["zeros"]), ("ones", "ones", dynM["ones"]),
                      ("random (measured 600 level)", "randn_M", dynM["randn"]),
                      ("random, compressed price list", "randn_P", dynP["randn"]),
                      ("random, flat in-company price", "randn_F", dynF["randn"])):
    fb, fs = settle(dyn, P_CAP), settle(dyn, W_SUS)
    res[key] = dict(burst_mhz=fb, sustained_mhz=fs, burst_tflops=PEAK_TFLOPS * fb / 800,
                    sustained_tflops=PEAK_TFLOPS * fs / 800)
    say("  %-28s %6.1f       %5.2f          %6.1f          %5.2f"
        % (lab, fb, PEAK_TFLOPS * fb / 800, fs, PEAK_TFLOPS * fs / 800))
say("")
say("  E64 measured, fp32, 1,024 harts: zeros 800 MHz 12.3/12.3 TFLOPS; ones 738 MHz 12.3/11.1;")
say("                                   random 706 MHz burst, 600 MHz sustained, 10.7/9.2 TFLOPS")
say("")
for key, lab in (("randn_M", "from E67's measured 600 MHz anchors"),
                 ("randn_P", "bit prices only, compressed list"),
                 ("randn_F", "bit prices only, flat in-company")):
    rb = res["zeros"]["burst_tflops"] / res[key]["burst_tflops"]
    rs = res["zeros"]["sustained_tflops"] / res[key]["sustained_tflops"]
    say("  ZEROS / RANDOM speed ratio, %-36s burst %.3f (%+.0f%%), sustained %.3f (%+.0f%%)"
        % (lab, rb, 100 * (rb - 1), rs, 100 * (rs - 1)))
say("  MEASURED (E64)                                                     "
    "burst %.3f (+15%%), sustained %.3f (+34%%)" % (12.3 / 10.7, 12.3 / 9.2))
R["chain"] = {"v600": v600, "v800_mean": v800, "v800_cards": {"aifoundry1-c0": v800a, "aifoundry2": v800b},
              "v2_scale": vv, "e60_price_ratio_800_over_600": dict(zip(sh, r8)),
              "e60_price_ratio_mean": sum(r8) / len(r8), "B_f_W": Bf, "governor": GOV, "die_line": THERM,
              "power_cap_W": P_CAP, "trip_C": T_TRIP, "sustained_cap_W": W_SUS,
              "predicted_board_W": {str(f): tabs[f] for f in tabs},
              "e64_measured_board_W": {k: {str(f): v[f] for f in v} for k, v in E64P.items()},
              "results": res,
              "predicted_ratio": {
                  "from_measured_anchors": {"burst": res["zeros"]["burst_tflops"] / res["randn_M"]["burst_tflops"],
                                            "sustained": res["zeros"]["sustained_tflops"] / res["randn_M"]["sustained_tflops"]},
                  "from_price_list_compressed": {"burst": res["zeros"]["burst_tflops"] / res["randn_P"]["burst_tflops"],
                                      "sustained": res["zeros"]["sustained_tflops"] / res["randn_P"]["sustained_tflops"]},
                  "from_price_list_flat": {"burst": res["zeros"]["burst_tflops"] / res["randn_F"]["burst_tflops"],
                                      "sustained": res["zeros"]["sustained_tflops"] / res["randn_F"]["sustained_tflops"]}},
              "measured_ratio": {"burst": 12.3 / 10.7, "sustained": 12.3 / 9.2},
              "measured_tflops": {"zeros": [12.3, 12.3], "ones": [12.3, 11.1], "randn": [10.7, 9.2]},
              "measured_mhz": {"zeros": 800, "ones": 738, "randn_burst": 706, "randn_sustained": 600}}

with open(os.path.join(OUT, "chain.json"), "w") as f:
    json.dump(R, f, indent=1)
say("")
say("wrote chain.json")
