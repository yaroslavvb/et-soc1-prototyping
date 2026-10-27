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

# E38's per-multiply-add energies. Read from the committed sparsity page's own data block, which
# is the source docs/findings/05-claims.md line 486 ("The Sparse compute page's power figures")
# cites for the registered V3-ABL-A values — four 7 s runs per card, operands -3..3, over idle.
_sp = open(os.path.join(REPO, "docs/reports/2026-09-18-et-soc1-sparsity.html"), encoding="utf-8").read()
_m = re.search(r'id="sparsity-data"[^>]*>', _sp)
_ops = json.loads(_sp[_m.end():_sp.index("</script>", _m.end())].strip())["v3"]["operands"]
E38 = {c: {p: _ops[c]["patterns"][p]["pj_mac"]["mean"] for p in ("zeros", "ones", "randn")}
       for c in _ops}

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
say("  Along this ladder the position premium does not add when bits flip together. It is NOT\n"
    "  gone in general: at a fixed m = 2 it is paid in full (position.py), so the compression is\n"
    "  a function of m, and this ladder always takes the lowest bits.")

# three candidate laws, scored on the same seven rungs
C_FLAT = sum(r["meas_J"] for r in lq_rows) / sum(r["flips"] for r in lq_rows) * 1e15     # fJ/bit, flat
# E60's own reading of the same ladder: a line with an intercept. Its marginal slope is the
# registered lq.designed figure, and forcing the intercept to zero is exactly what drops it to C_FLAT.
C_LIN = a3["lq"]["linear"]["W_per_h"] / rate60 / B_PRES * 1e15
say("")
say("  two defensible flat prices from this same ladder:")
say("    zero-intercept pooled (used below)      %.1f fJ per flipped bit" % C_FLAT)
say("    E60's own marginal slope %.4f W per h  %.1f fJ  (registered lq.designed %.1f fJ;"
    % (a3["lq"]["linear"]["W_per_h"], C_LIN, a3["lq"]["designed"]["fJ"]))
say("      its intercept is %+.3f W, %.0f%% of the m=1 rung, which is the whole difference)"
    % (a3["lq"]["linear"]["intercept_W"], 100 * abs(a3["lq"]["linear"]["intercept_W"]) / lq_rows[0]["dW"]))
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
say("  three candidate laws, FITTED ON AND SCORED ON these same seven rungs (in-sample, not a test):")
for nm, _, (rms_, mx_) in laws:
    say("    %-46s rms %5.1f%%   worst %5.1f%%" % (nm, rms_, mx_))
say("  >>> the finding is the free exponent, %.3f, which is 1.00 within its scatter; the two" % BETA)
say("      one-parameter-equivalent laws (flat, and c x m^beta) are indistinguishable on seven")
say("      in-sample rungs and neither 'wins'. Only the price-list law is clearly worse.")
say("      Along THIS ladder, board power counts flipped bits and all but ignores which ones.")
say("      The out-of-sample test is nrd_a / nrd_b in part 4, and both laws miss there.")
R["saturation"] = {
    "lq_rows": lq_rows,
    "flat_fJ_per_bit": C_FLAT, "alpha": ALPHA, "beta": BETA, "c_pow_W": C_POW,
    "flat_fJ_per_bit_marginal": C_LIN,
    "e60_lq_linear": a3["lq"]["linear"], "e60_lq_designed_fJ": a3["lq"]["designed"]["fJ"],
    "law_scores_pct": {"in_sample": True,
                       "flat": {"rms": laws[0][2][0], "worst": laws[0][2][1]},
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
# the low arm is not one number: it depends on two choices neither of which the data settles.
AB_MEAN = sum(pA_fJ[j] / pB_fJ[j] for j in pA_fJ) / len(pA_fJ)
say("")
say("  the low arm's own sensitivity — the flat law needs a per-bit price and an A-side carry-over,")
say("  and the data settles neither. All four combinations, x kappa %.3f:" % KAPPA)
LOW = {}
for cf, cfn in ((C_FLAT, "%.1f fJ zero-intercept" % C_FLAT), (C_LIN, "%.1f fJ E60 marginal" % C_LIN)):
    for ab, abn in ((AB, "A/B %.3f sum-weighted" % AB), (AB_MEAN, "A/B %.3f position mean" % AB_MEAN)):
        t = KAPPA * (cf * ab * 1e-15 * sum(Ah) * na["rate_ops_s"] + cf * 1e-15 * sum(Bh) * nb["rate_ops_s"])
        LOW["%s | %s" % (cfn, abn)] = t
        say("    %-26s %-28s  %6.3f W   %+.0f%%" % (cfn, abn, t, 100 * (t / both_meas - 1)))
say("    A law that says position stops mattering in company arguably should not then import a")
say("    position-weighted A/B ratio, and E60's own fit of this ladder keeps an intercept. So the")
say("    low arm is %.1f-%.1f W, %+.0f%% to %+.0f%%, and the bracket is %+.0f%%/%+.0f%% to %+.0f%%."
    % (min(LOW.values()), max(LOW.values()), 100 * (min(LOW.values()) / both_meas - 1),
       100 * (max(LOW.values()) / both_meas - 1), 100 * (min(LOW.values()) / both_meas - 1),
       100 * (max(LOW.values()) / both_meas - 1), 100 * (both_pred / both_meas - 1)))
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
                      "A_over_B_position_mean": AB_MEAN,
                      "low_arm_sensitivity_W": LOW,
                      "low_arm_range_W": [min(LOW.values()), max(LOW.values())],
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
say("  E38 (V3-ABL-A, 21 Sep, four 7 s runs per card, 600 MHz boot clock) measured the same three")
say("  terms per multiply-add over idle. REGISTERED values, docs/findings/05-claims.md line 486,")
say("  read here from the sparsity page's own data block:")
e38 = {}
for c in ("aifoundry2", "aifoundry3", "aifoundry1-c1"):
    z, o, rn = E38[c]["zeros"], E38[c]["ones"], E38[c]["randn"]
    e38[c] = {"zeros": z, "ones": o, "random": rn, "clocking": o - z, "data": rn - o}
    say("    %-14s zeros %.2f  ones %.2f  random %.2f pJ  ->  clocking %.2f, data %.2f"
        % (c, z, o, rn, o - z, rn - o))
say("    this work (aifoundry3, 600 MHz, E67's anchors):                 clocking %.2f, data %.2f"
    % (pj(clocking), pj(data_meas)))
for c in ("aifoundry2", "aifoundry3"):
    say("      against %-14s (%s): %3.0f%% and %3.0f%%"
        % (c, "the other card, five weeks" if c == "aifoundry2" else "the SAME card, five weeks",
           100 * pj(clocking) / e38[c]["clocking"], 100 * pj(data_meas) / e38[c]["data"]))
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
                   "e38_pJ_registered_per_card": e38,
                   "e38_source": "docs/reports/2026-09-18-et-soc1-sparsity.html <script id=sparsity-data> "
                                 ".v3.operands.<card>.patterns.<p>.pj_mac.mean; registered in "
                                 "docs/findings/05-claims.md line 486 (V3-ABL-A, E38)"}

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
say("  NOT INDEPENDENT: B(f) is E64's own joint fit over 103 points, and those points include the")
say("  fp32 zeros/ones/randn LAD runs whose clocks this section then predicts. So the absolute-power")
say("  agreement below is partly in-sample; the step comparison above it is the independent one.")
# the two caps, both sourced, neither fitted here:
#   P_CAP  — the TDP the card reads back (E64 README: "TDP 65 W and threshold 65 C read back after
#            every run"), and the literal E64's own surface_hpl.py passes to simulate().
#   W_SUS  — E64's REGISTERED thermal reading cap_w_at_65_5: the board power at which its die line
#            reads 65.5 C. Parsed above, and used here instead of a 66 C trip: E64's own sustained
#            fp32 randn point sits at 67.1 C and 54.4 W, so 66 C is not a hard trip.
P_CAP = 65.0
W_SUS = THERM["cap_w_at_65_5"]


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
sr = {}
for f in (600, 700, 800):
    pm = tabs[f]["randn"] - tabs[f]["zeros"]; em = E64P["randn"][f] - E64P["zeros"][f]
    sr[f] = pm / em
    say("    %3d MHz  predicted %6.2f W   measured %6.2f W   ratio %.3f" % (f, pm, em, pm / em))
DRIFT = sr[800] / sr[600]
say("    At 600 MHz NOTHING IS REFERRED — the model simply uses E67's own measured anchors — so")
say("    %+.0f%% there is the pure aifoundry3-against-aifoundry2 card offset, not a referral error."
    % (100 * (sr[600] - 1)))
say("    The referral's own error is the DRIFT off that anchor: %.3f / %.3f = %.3f, i.e. %+.0f%% over"
    % (sr[800], sr[600], DRIFT, 100 * (DRIFT - 1)))
say("    200 MHz, and it is monotone, not scatter. %+.0f%% is what propagates into the clocks below."
    % (100 * (DRIFT - 1)))
say("")
say("  governor: the ~%.1f s average of board power is held to %.0f W (the TDP the card reads back,"
    % (GOV["tau_s"], P_CAP))
say("  and the literal E64's own surface_hpl.py simulates with); the sustained cap is E64's")
say("  registered cap_w_at_65_5 = %.1f W, the board power at which its die line reads 65.5 C." % W_SUS)
say("  (E64's sustained fp32 randn point sits at 67.1 C and 54.4 W, so there is no hard 66 C trip,")
say("  and its three measured sustained board powers are 36.4 / 49.4 / 54.4 W — not one cap.)")
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

# ───────────────────── how much of that agreement is real: three things to disclose
say("")
say("  " + "-" * 82)
say("  (a) THE SUSTAINED RATIO IS A CLAMP, NOT A FIT. settle() returns an endpoint when the cap")
lo_e, hi_e = P_of(800, dynM["zeros"]), P_of(600, dynM["randn"])
say("      lies outside [600, 800]. Zeros at 800 MHz draws %.2f W and random at 600 MHz draws %.2f W,"
    % (lo_e, hi_e))
say("      so ANY sustained cap in a %.1f W window, %.1f to %.1f W, returns exactly 800/600 = %.4f."
    % (hi_e - lo_e, lo_e, hi_e, 800 / 600))
CAND = {"E64 registered cap_w_at_65_5": W_SUS, "a 66 C trip on the die line": (66.0 - THERM["a_c"]) / THERM["k_c_per_w"],
        "E64 measured sustained ones": 49.4, "E64 measured sustained randn": 54.4}
for nm, c in CAND.items():
    say("        cap %5.2f W (%-28s) -> zeros %5.1f / random %5.1f MHz, ratio %.4f"
        % (c, nm, settle(dynM["zeros"], c), settle(dynM["randn"], c),
           settle(dynM["zeros"], c) / settle(dynM["randn"], c)))
say("      And the measurement is the same number: E64 reports sustained 800 and 600 MHz, and its")
say("      12.3 / 9.2 TFLOPS is 12.3 x 600/800 = %.3f rounded to 9.2. Unrounded the" % (12.3 * 600 / 800))
say("      measured ratio is %.4f — identical to the prediction. The published '0.3%%' was E64's" % (800 / 600))
say("      rounding, not an agreement. The sustained result carries ONE bit: random reaches the")
say("      floor and zeros does not. That is ordinal, and it is still a real prediction.")
say("")
say("  (b) THE BURST CAP MATTERS, and E64 offers four measured comparators, not one.")
CAPS = (64.0, 65.0, 65.5, 66.0, 67.0)
say("      predicted burst ratio against the power cap:")
say("        " + "   ".join("%.1f W: %.4f" % (c, settle(dynM["zeros"], c) / settle(dynM["randn"], c)) for c in CAPS))
COMP = {"SUS 'cool die, first 8 s' TFLOPS 12.3/10.7": 12.3 / 10.7,
        "LAD whole-run TFLOPS 12.11/10.61": 12.11 / 10.61,
        "surface.txt burst clocks 800/706": 800 / 706,
        "LAD mean MHz after 1.5 s 800/710": 800 / 710}
rb_M = res["zeros"]["burst_tflops"] / res["randn_M"]["burst_tflops"]
for nm, v in COMP.items():
    say("        measured %-44s %.4f   predicted/measured %+.1f%%" % (nm, v, 100 * (rb_M / v - 1)))
say("      The published 0.3%% is the smallest of those four. Honest range: predicted %.3f against" % rb_M)
say("      measured %.3f-%.3f depending on whether you read TFLOPS or clocks."
    % (min(COMP.values()), max(COMP.values())))
say("")
say("  (c) THE REFERRAL BAND, carried through. The referral's own error is the %+.0f%% drift from 600"
    % (100 * (DRIFT - 1)))
say("      to 800 MHz, so put a band of that size on the random dynamic term and re-settle:")
BAND = {}
for s, nm in ((1 / DRIFT, "random costs %+.0f%% more" % (100 * (1 / DRIFT - 1))), (1.0, "as published"),
              (DRIFT, "random costs %+.0f%% less" % (100 * (DRIFT - 1)))):
    fb2 = settle(dynM["randn"] * s, P_CAP)
    BAND[nm] = {"scale": s, "burst_mhz": fb2, "ratio": res["zeros"]["burst_mhz"] / fb2}
    say("        x %.3f (%-22s) burst %5.1f MHz   ratio %.4f" % (s, nm, fb2, res["zeros"]["burst_mhz"] / fb2))
bb = sorted(v["ratio"] for v in BAND.values())
say("      So the burst prediction with the referral's own error carried is %.3f-%.3f, which" % (bb[0], bb[-1]))
say("      contains every measured comparator above. The point estimate agrees with the headline")
say("      comparator to 0.2%, but the model's resolution cannot tell the four measurements apart.")
R["chain"] = {"v600": v600, "v800_mean": v800, "v800_cards": {"aifoundry1-c0": v800a, "aifoundry2": v800b},
              "v2_scale": vv, "e60_price_ratio_800_over_600": dict(zip(sh, r8)),
              "e60_price_ratio_mean": sum(r8) / len(r8), "B_f_W": Bf, "governor": GOV, "die_line": THERM,
              "power_cap_W": P_CAP,
              "power_cap_source": "the TDP the card reads back (E64 README); the literal E64's own "
                                  "surface_hpl.py passes to simulate(). Not fitted here.",
              "sustained_cap_W": W_SUS,
              "sustained_cap_source": "E64's registered thermal cap_w_at_65_5 (surface.txt), the board "
                                      "power at which its die line reads 65.5 C. E64's own sustained "
                                      "fp32 randn point is 67.1 C at 54.4 W, so 66 C is not a hard trip.",
              "sustained_is_a_clamp": {
                  "clamp_window_W": [P_of(800, dynM["zeros"]), P_of(600, dynM["randn"])],
                  "window_width_W": P_of(600, dynM["randn"]) - P_of(800, dynM["zeros"]),
                  "ratio_anywhere_in_window": 800 / 600,
                  "candidate_caps_W": CAND,
                  "measured_sustained_ratio_unrounded": 800 / 600,
                  "note": "Three of the four candidate caps are inside the window; for those, zeros "
                          "clamps high and random clamps low, so the ratio is 800/600 by construction and "
                          "the 0.3% residual is E64's rounding of 12.3 x 600/800 = 9.225 to 9.2. The fourth, "
                          "E64's own measured sustained randn point at 54.4 W, is ABOVE the window: at that "
                          "cap random would settle above the 600 MHz floor and the ratio would fall to about "
                          "1.30. The prediction that survives either way is ordinal."},
              "burst_cap_sensitivity": {str(c): settle(dynM["zeros"], c) / settle(dynM["randn"], c) for c in CAPS},
              "burst_measured_comparators": COMP,
              "referral_step_ratio": {str(f): sr[f] for f in sr},
              "referral_drift_600_to_800": DRIFT,
              "burst_referral_band": BAND,
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
