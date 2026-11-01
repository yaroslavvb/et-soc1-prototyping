#!/usr/bin/env python3
"""E110: the numbers behind the corrections after verification (Sun 1 Nov 2026), from committed files only (standard library).

    python3 docs/reports/data/2026-11-01-e110-memory-width/corrections-check.py > .../corrections-check.txt

Post hoc and deciding nothing: no registered file, reduction, measured number or scored verdict changes. It reads `runs.csv` (the
registered primary arm, one row per run), `e110.json`, `ew-readme-formula.json`, `gen/counts.json` and the frozen
`tools/claims-v3/e110/predictions.json`. Sections follow the verifier's faults:
  C1 the rails' settling: R6 with every rail read as is and divided by E99's 0.935 (its README: a rail read over [t0+2 s, t0+4 s)
     holds about 93.5 % of a settled step);
  C2 the encoded side: the board's E_w by the registration's formula, and the DDR die rail on the six W and V rungs beside their
     raw and encoded 64-bit toggle counts, classed by R5's rule;
  C3 how far R3's and R4's readings sit from their class boundaries, every arm;
  C4 the registered price solve done pass by pass, so each price has its own interval;
  C5 the frozen L2 prediction against the measurement (reported, not scored);
  C7 the conditions under the blog's prices: line edges counted, and the first ones over zeros.
(C6 and C8 are sources and wording; they have no numbers.)
"""
import csv
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T5 = 2.570581835636314           # t(0.975, df = 5): six headline passes
HEAD = [11011, 11012, 11013, 11014, 11015, 11016]
SETTLE = 0.935                   # E99's README: a rail over [t0+2 s, t0+4 s) reads about 93.5 % of a settled step
N = {16: 31, 32: 15, 64: 7, 128: 3, 256: 1}          # within-line block edges of a rung (registration)
WR = {16: "dm_a08", 32: "wl_32", 64: "wl_64", 128: "wl_128", 256: "wl_256"}
VR = {16: "dm_a44", 32: "vl_32", 64: "vl_64", 128: "vl_128", 256: "vl_256"}
RAILS = ("noc", "sram", "minion")


def load(*p):
    return json.load(open(os.path.join(*p)))


def ci(xs):
    m = statistics.mean(xs)
    h = T5 * statistics.stdev(xs) / math.sqrt(len(xs))
    return m, m - h, m + h


def fmt(t, d=3, sign=True):
    f = ("%+." if sign else "%.") + str(d) + "f"
    return (f + " [" + f + ", " + f + "]") % t


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "runs.csv"))) if not r["fails"]]
    acc, rate = {}, {}
    for r in rows:
        p = int(r["pass"])
        if p not in HEAD:
            continue
        for c in ("p80",) + RAILS + ("off", "ddr_mv"):
            if r[c] != "":
                acc.setdefault((p, r["item"], c), []).append(float(r[c]))
        if r["ops_per_s"]:
            rate.setdefault((p, r["level"]), []).append(float(r["ops_per_s"]))

    def I(p, item, c="p80"):
        return statistics.mean(acc[(p, item, c)])

    def L(p, lvl):
        return statistics.mean(rate[(p, lvl)])

    E = load(HERE, "e110.json")
    V = E["verdicts"]
    EW = load(HERE, "ew-readme-formula.json")
    CNT = load(HERE, "gen", "counts.json")
    PR = load(REPO, "tools", "claims-v3", "e110", "predictions.json")
    DEC = PR["decision"]
    print("E110 corrections after verification: post hoc, deciding nothing (95 %% t over the six headline passes %s)" % HEAD)

    # C1 ------------------------------------------------------------------------------------------------------------------
    print("\nC1  R6 with the rails as read and at E99's settling (rails / %.3f; the board is not a rail and is unchanged)" % SETTLE)
    r6 = V["R6_one_off_rail"]
    print("    e110.json as reduced: X %.3f [%.3f, %.3f]  regulators %.3f [%.3f, %.3f]  f %.3f [%.3f, %.3f]  off %.3f [%.3f, %.3f] pJ" % (
        r6["remainder_X_pJ"]["mean"], r6["remainder_X_pJ"]["lo"], r6["remainder_X_pJ"]["hi"],
        r6["regulator_share_pJ"]["mean"], r6["regulator_share_pJ"]["lo"], r6["regulator_share_pJ"]["hi"],
        r6["f_on_chip_off_fraction"]["mean"], r6["f_on_chip_off_fraction"]["lo"], r6["f_on_chip_off_fraction"]["hi"],
        r6["dram_pJ_per_one"]["off"]["mean"], r6["dram_pJ_per_one"]["off"]["lo"], r6["dram_pJ_per_one"]["off"]["hi"]))
    for s in (1.0, SETTLE):
        cols = {k: [] for k in ("board", "noc", "sram", "minion", "rails", "off", "l2_board", "l2_rails", "f", "R", "X")}
        for p in HEAD:
            kd = 1e12 / (448 * L(p, "dram"))
            kl = 1e12 / (448 * L(p, "l2"))
            b = (I(p, "dm_u8") - I(p, "dm_u1")) * kd
            rails = {c: (I(p, "dm_u8", c) - I(p, "dm_u1", c)) / s * kd for c in RAILS}
            rs = sum(rails.values())
            lb = (I(p, "l2_u8") - I(p, "l2_u1")) * kl
            lr = sum(I(p, "l2_u8", c) - I(p, "l2_u1", c) for c in RAILS) / s * kl
            f = (lb - lr) / lb
            R = rs * f / (1 - f)
            for k, x in (("board", b), ("noc", rails["noc"]), ("sram", rails["sram"]), ("minion", rails["minion"]), ("rails", rs),
                         ("off", b - rs), ("l2_board", lb), ("l2_rails", lr), ("f", f), ("R", R), ("X", b - rs - R)):
                cols[k].append(x)
        print("    rails / %.3f:" % s)
        print("      DRAM one, pJ: board %s  NoC %s  SRAM %s  minion %s  off %s" % (
            fmt(ci(cols["board"]), 2, False), fmt(ci(cols["noc"]), 2, False), fmt(ci(cols["sram"]), 2, False),
            fmt(ci(cols["minion"]), 2, False), fmt(ci(cols["off"]), 2, False)))
        print("      L2 one, pJ: board %s, rails %s;  f (off/board at L2) %s" % (
            fmt(ci(cols["l2_board"]), 3, False), fmt(ci(cols["l2_rails"]), 3, False), fmt(ci(cols["f"]), 3, False)))
        print("      regulators' share R %s pJ   remainder X %s pJ   R + X = off %.3f" % (
            fmt(ci(cols["R"]), 2, False), fmt(ci(cols["X"]), 2, False), ci(cols["R"])[0] + ci(cols["X"])[0]))
    print("    X = board_DRAM - rails_DRAM * board_L2 / rails_L2, so one factor on every rail cancels in X; R and off move with it.")
    hc = E["headline"]["contrasts"]
    d_b, d_n, d_s = hc["board"]["D"]["mean"], hc["noc"]["D"]["mean"], hc["sram"]["D"]["mean"]
    print("    reading 6, D's share on the NoC and SRAM rails (headline means): %.1f %% as read, %.1f %% at rails / %.3f" % (
        100 * (d_n + d_s) / d_b, 100 * (d_n + d_s) / SETTLE / d_b, SETTLE))

    # C2 ------------------------------------------------------------------------------------------------------------------
    print("\nC2  The encoded side")
    print("    the board, E_w by the registration's formula (ew-readme-formula.json), primary arm:")
    for k in ("E32", "E64", "E128", "E256"):
        x = EW["e110.json"][k]["readme_formula"]
        print("      %-5s %s  %s" % (k, fmt((x["mean"], x["lo"], x["hi"])), x["class"]))
    dd = E["headline"]["contrasts"]["ddr_mv"]

    def ddr_cls(c):
        mv, st = DEC["ddr_moves_mV"], DEC["ddr_still_half_mV"]
        if c["mean"] <= -mv and c["hi"] < 0:
            return "moves"
        if c["lo"] >= -st and c["hi"] <= st:
            return "still"
        return "unresolved"

    print("    the DDR die rail (e110.json headline.contrasts.ddr_mv, mV; R5's rule: moves at <= -%.2f with the interval below 0, "
          "still inside +-%.2f), with each contrast's 64-bit toggles a line over its base (gen/counts.json):" % (
              DEC["ddr_moves_mV"], DEC["ddr_still_half_mV"]))
    rung = []
    for w in (64, 128, 256):
        for fam, items, base in (("S", WR, "dm_l08"), ("V", VR, "dm_u4")):
            nm = "%s%d" % (fam, w)
            r64 = CNT[items[w]]["r64"] - CNT[base]["r64"]
            e64 = CNT[items[w]]["e64"] - CNT[base]["e64"]
            c = dd[nm]
            board = E["headline"]["contrasts"]["board"][nm]["mean"]
            rung.append((nm, r64, e64, ddr_cls(c)))
            print("      %-5s %s mV  %-10s board %+.3f W   r64 %3d  e64 %3d  r64+e64 %3d" % (
                nm, fmt((c["mean"], c["lo"], c["hi"]), 2), ddr_cls(c), board, r64, e64, r64 + e64))
    mov = [x for x in rung if x[3] == "moves"]
    sti = [x for x in rung if x[3] == "still"]
    print("    moves: %s;  still: %s" % (", ".join("%s %d" % (x[0], x[1] + x[2]) for x in sorted(mov, key=lambda x: -(x[1] + x[2]))),
                                         ", ".join("%s %d" % (x[0], x[1] + x[2]) for x in sorted(sti, key=lambda x: -(x[1] + x[2])))))
    # for which weights k does r64 + k*e64 put every moving rung above every still one?
    ks = [k / 100.0 for k in range(0, 10001)]
    ok = [k for k in ks if min(m[1] + k * m[2] for m in mov) > max(s_[1] + k * s_[2] for s_ in sti)]
    print("    r64 + k*e64 orders them (every moving rung above every still one) for k in (%.2f, %.2f) on a 0.01 grid, "
          "open at both ends: k = 0 (raw only) ties V128 with S128, k = 48 ties S64 with V256" % (min(ok), max(ok)))
    e128 = []
    for p in HEAD:
        g = lambda n: I(p, n, "ddr_mv")
        k = N[128] / 31.0
        e128.append((g(VR[128]) - g("dm_u4")) - (g(WR[128]) - g("dm_l08")) - k * ((g("dm_a44") - g("dm_u4")) - (g("dm_a08") - g("dm_l08"))))
    print("    the die rail's E128 by the registration's formula: %s mV (the frozen code's, e110.json ddr_mv.E128: %s)" % (
        fmt(ci(e128), 2), fmt((dd["E128"]["mean"], dd["E128"]["lo"], dd["E128"]["hi"]), 2)))
    print("    the die rail is read raw (reduce_e110.py: die_mv.ddr over [t0+1 s, t0+3 s)); the leakage slope corrects board power only")

    # C3 ------------------------------------------------------------------------------------------------------------------
    print("\nC3  Margins to the class boundaries (E81's rule: present at mean >= %.2f W with the interval excluding 0; absent inside "
          "+-%.2f W)" % (DEC["present_min_W"], DEC["absent_half_W"]))
    for arm in ("e110.json", "e110-leak0.2936.json", "e110-leak0.3803.json", "e110-unfiltered.json"):
        a = EW[arm]
        for form in ("readme_formula", "frozen_code"):
            e64, e256 = a["E64"][form], a["E256"][form]
            print("    %-22s %-15s E64 hi %+.3f (0.30 - hi = %+.3f W)   E256 mean %+.3f (0.25 - mean = %+.3f W)   R3 %s, R4 %s" % (
                arm, form, e64["hi"], DEC["absent_half_W"] - e64["hi"], e256["mean"], DEC["present_min_W"] - e256["mean"],
                a["R3_" + form], a["R4_" + form]))
    print("    A positive 0.30 - hi keeps E64 absent; past the band (its mean below 0.25 W) R3 would read UNRESOLVED, as it does at both "
          "sensitivities. A negative 0.25 - mean, with E256's interval above 0, would make R4 read ENCODED256, a FAIL.")

    # C4 ------------------------------------------------------------------------------------------------------------------
    print("\nC4  The registered price solve, pass by pass: c_w = [S_w/n_w - S_(w/2)/n_(w/2)] / w / line rate, pJ a toggled bit")
    for cnt, nn in (("within-line edges (registered)", N), ("line edges counted too (n = 512/w)", {w: 512 // w for w in N})):
        key = "W_within" if nn is N else "W_cyclic"
        out = []
        for w in (16, 32, 64, 128, 256):
            xs = []
            for p in HEAD:
                S = lambda ww: I(p, WR[ww]) - I(p, "dm_l08")
                prev = S(w // 2) / nn[w // 2] if w > 16 else 0.0
                xs.append((S(w) / nn[w] - prev) / w / L(p, "dram") * 1e12)
            out.append("%d: %s (e110.json %.3f)" % (w, fmt(ci(xs), 3), V["prices_pJ_per_toggled_bit"][key][str(w)]))
        print("    %s\n      %s" % (cnt, "\n      ".join(out)))

    # C5 ------------------------------------------------------------------------------------------------------------------
    print("\nC5  The frozen L2 prediction (predictions.json prediction.l2), reported, not scored: no rule uses it")
    l2p = PR["prediction"]["l2"]
    l2w = E["headline"]["contrasts"]["board"]["l2_ones"]
    l2pj = r6["l2_pJ_per_one"]["board"]
    print("    frozen: l2_ones %.2f W, %.2f pJ a one;  measured: l2_ones %s W, %s pJ a one;  measured/frozen %.2f (W), %.2f (pJ)" % (
        l2p["l2_ones_board_W"], l2p["per_one_pJ_board"], fmt((l2w["mean"], l2w["lo"], l2w["hi"]), 3, False),
        fmt((l2pj["mean"], l2pj["lo"], l2pj["hi"]), 3, False), l2w["mean"] / l2p["l2_ones_board_W"], l2pj["mean"] / l2p["per_one_pJ_board"]))
    print("    frozen value outside the measured interval: %s" % (not (l2w["lo"] <= l2p["l2_ones_board_W"] <= l2w["hi"])))
    oz = E["headline"]["over_zeros"]["board"]
    print("    the first ones over zeros (headline.over_zeros.board): l2_u1 %s W over l2_zeros, dm_u1 %s W over dp_zeros" % (
        fmt((oz["l2_u1"]["mean"], oz["l2_u1"]["lo"], oz["l2_u1"]["hi"])), fmt((oz["dm_u1"]["mean"], oz["dm_u1"]["lo"], oz["dm_u1"]["hi"]))))
    lr_l2 = statistics.mean([L(p, "l2") for p in HEAD])
    print("    as a price over zeros: l2_u1's 64 ones %.2f pJ a one, against the marginal %.3f" % (
        oz["l2_u1"]["mean"] / (64 * lr_l2) * 1e12, l2pj["mean"]))
    e75 = {}
    for line in open(os.path.join(REPO, "tools", "claims-v3", "e110", "desk", "e75_levels.txt")):
        f_ = line.split()
        if f_ and f_[0] in ("mf_l2_k0", "mf_l2_zeros"):
            e75[f_[0]] = float([x for x in f_ if x.startswith("board=")][0].split("=")[1])
    step = e75["mf_l2_k0"] - e75["mf_l2_zeros"]
    print("    E75's L2 k = 0 rung (256 ones, no changes) over its zeros (desk/e75_levels.txt): %+.3f W, %.2f pJ a one at E75's %.4g lines/s;"
          " x 448 ones at that price: %.2f W" % (step, step / (256 * PR["line_rate_l2_e75"]) * 1e12, PR["line_rate_l2_e75"],
                                                step / 256 * 448))
    print("    (the registration's text does not derive prediction.l2; these only show that a price over zeros runs high)")

    # C7 ------------------------------------------------------------------------------------------------------------------
    print("\nC7  Conditions under the blog's prices")
    pw, pc = V["prices_pJ_per_toggled_bit"]["W_within"], V["prices_pJ_per_toggled_bit"]["W_cyclic"]
    print("    within-line edges: 64-bit %.2f pJ, 256-bit %.2f pJ;  with each path's line edge counted: 64-bit %.2f pJ, 256-bit %.2f pJ" % (
        pw["64"], pw["256"], pc["64"], pc["256"]))
    for lvl, hi_, lo_, note in (("DRAM", "dm_u8", "dm_u1", "high pins %d on both: held equal" % CNT["dm_u8"]["hi"]),
                                ("L2", "l2_u8", "l2_u1", "no pins at this level")):
        w_hi, w_lo = CNT[hi_]["w"], CNT[lo_]["w"]
        print("    %s: the price of a one is marginal, from %d to %d ones a line (%s - %s, %d ones; %s)" % (
            lvl, w_lo, w_hi, hi_, lo_, w_hi - w_lo, note))
    print("    the first ones over zeros cost more: see C5's over_zeros line (dm_u1 also carries 64 high pins a line)")


if __name__ == "__main__":
    main()
