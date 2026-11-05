#!/usr/bin/env python3
"""Q143(g): E175's lines at the planned n and each rule's power, before any E175 tile, count or prediction exists (E175.md, "Precision and
power, before the data"). Design only: it reads committed references and committed blind errors, never a pool tile or an E175 datum.

  * the bootstrap lines: Q142(p)'s frozen engine, predict_pool8.boot_range through predict_pool8_a2.P() (A2-3 (a)): seed 80,000 + the sum of the
    rule id's character codes, 20,000 draws, [vals[int(0.025 x 20000)], vals[int(0.975 x 20000) - 1]], at E175's planned n and at the
    governed minimum 8 and at 12;
  * the references (A2-3 (d)): tools/claims-v3/e165/predictions-e165.json > reference, through predict_pool8_a2.e165_refs(): Q140(l)'s 36
    governed and 42 pinned end-to-end held-out cells (clock and board errors, each cell's pair kept together) and the burst heat law's 112
    residuals;
  * the power: the share of 20,000 draws of n_g governed and n_p pinned cells (with replacement; each draw seeded
    Random("E175|power|<truth>|<n_g>|<n_p>")) in which each rule reads PASS, under five truths:
      e2e        the cells as they are (the bootstrap rules then pass about 97.5% by construction);
      e165       E165's blind errors of M9's part on pool 7 (results.json > score > reported > tiles: measured - primary), the only committed
                 blind governed errors on this card;
      e2e x1.5   every error 1.5 times as large;
      e2e level  the clock 3 MHz high on governed bursts (rank 2's mean line is 2.0), the board 0.5 W high on both groups;
      e2e x0.5   every error half as large (a model twice as good as held out);
    rank 2's fixed lines (G: rms <= 4.0 MHz and |mean| <= 2.0 MHz; Bg: |mean| <= 0.5 W; Bp: |mean| <= 0.5 W and rms <= 1.0 W; R2 all three), and
    the bootstrap rules (F1, W1 on governed; F2, W2 on pinned; H1 on all, from the 112 residuals and E165's 52 rise errors) read at their own
    line at that n.

    /usr/bin/python3 -B tools/claims-v3/e175/design_power_e175.py --out tools/claims-v3/e175/design-power-e175.json > tools/claims-v3/e175/design-power-e175.txt
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PD = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-q142p-pool8-predictor")
E165_RES = os.path.join(TOP, "docs", "reports", "data", "2026-11-04-e165-blind7-aifoundry2", "results.json")
sys.path.insert(0, PD)
import predict_pool8_a2 as A  # noqa: E402  (checks its own two lists before it imports the frozen predictor)

N_G, N_P = 16, 8                 # the planned design (E175.md): 16 governed, 8 pinned
N_ALL = N_G + N_P
N_G_SET = (8, 12, 16)            # the governed minimum, an intermediate, the planned
DRAWS = 20000
LINES = {"G_rms_max_mhz": 4.0, "G_abs_mean_max_mhz": 2.0, "Bg_abs_mean_max_w": 0.5, "Bp_abs_mean_max_w": 0.5, "Bp_rms_max_w": 1.0}
RULES = {"E175-A2-F1": ("gov_mhz", "rms", "MHz"), "E175-A2-W1": ("gov_w", "rms", "W"), "E175-A2-F2": ("pin_mhz", "rms", "MHz"),
         "E175-A2-W2": ("pin_w", "rms", "W"), "E175-A2-H1": ("heat_c", "rms", "C")}


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    return sum(v) / len(v) if v else None


def e165_blind():
    """E165's blind errors of M9's part (pool 7 on this card, 4 Nov 2026): per scored tile, measured - primary, by the frozen group"""
    r = json.load(open(E165_RES))
    tiles = r["score"]["reported"]["tiles"]
    gov, pin, heat = [], [], []
    for n, t in sorted(tiles.items()):
        p = t.get("primary") or {}
        if t.get("burst_mhz") is None or p.get("burst_mhz") is None or t.get("burst_w") is None:
            continue
        cell = (float(t["burst_mhz"]) - float(p["burst_mhz"]), float(t["burst_w"]) - float(p["burst_board_w"]))
        (gov if t.get("group") == "governed" else pin).append(cell)
        if t.get("rise_c") is not None and p.get("burst_die_rise_c") is not None:
            heat.append(float(t["rise_c"]) - float(p["burst_die_rise_c"]))
    return gov, pin, heat


def lines_at(R, n_by_rule):
    P = A.P()
    out = {}
    for rule, (key, stat, unit) in RULES.items():
        out[rule] = {}
        for n in n_by_rule[rule]:
            out[rule][str(n)] = {"range_95": P.boot_range(R[key], n, rule, stat), "seed": P.seed_of(rule), "ref_n": len(R[key]),
                                 "ref_rms": rms(R[key]), "unit": unit}
    return out


def power(truth, gov, pin, heat, n_g, n_p, L):
    """the share of draws in which each rule reads PASS; gov and pin are lists of (clock error, board error) cells, heat a list of rise errors"""
    rng = random.Random(f"E175|power|{truth}|{n_g}|{n_p}")
    keys = ("G_rms", "G_mean", "G", "Bg", "Bp_mean", "Bp_rms", "Bp", "R2", "F1", "W1", "F2", "W2", "H1")
    hit = {k: 0 for k in keys}
    f1, w1 = L["E175-A2-F1"][str(n_g)]["range_95"][1], L["E175-A2-W1"][str(n_g)]["range_95"][1]
    f2, w2 = L["E175-A2-F2"][str(n_p)]["range_95"][1], L["E175-A2-W2"][str(n_p)]["range_95"][1]
    h1 = L["E175-A2-H1"][str(n_g + n_p)]["range_95"][1]
    for _ in range(DRAWS):
        g = [gov[rng.randrange(len(gov))] for _ in range(n_g)]
        p = [pin[rng.randrange(len(pin))] for _ in range(n_p)]
        h = [heat[rng.randrange(len(heat))] for _ in range(n_g + n_p)]
        gm, gw = [x for x, _ in g], [y for _, y in g]
        pm, pw = [x for x, _ in p], [y for _, y in p]
        a = rms(gm) <= LINES["G_rms_max_mhz"]
        b = abs(mean(gm)) <= LINES["G_abs_mean_max_mhz"]
        c = abs(mean(gw)) <= LINES["Bg_abs_mean_max_w"]
        d = abs(mean(pw)) <= LINES["Bp_abs_mean_max_w"]
        e = rms(pw) <= LINES["Bp_rms_max_w"]
        for k, v in (("G_rms", a), ("G_mean", b), ("G", a and b), ("Bg", c), ("Bp_mean", d), ("Bp_rms", e), ("Bp", d and e),
                     ("R2", a and b and c and d and e), ("F1", rms(gm) <= f1), ("W1", rms(gw) <= w1), ("F2", rms(pm) <= f2),
                     ("W2", rms(pw) <= w2), ("H1", rms(h) <= h1)):
            hit[k] += int(v)
    return {k: round(100.0 * v / DRAWS, 1) for k, v in hit.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    lists = A.check_lists()
    R = A.e165_refs()
    gov_e2e = list(zip(R["gov_mhz"], R["gov_w"]))
    pin_e2e = list(zip(R["pin_mhz"], R["pin_w"]))
    g165, p165, h165 = e165_blind()
    n_by_rule = {"E175-A2-F1": N_G_SET, "E175-A2-W1": N_G_SET, "E175-A2-F2": (N_P,), "E175-A2-W2": (N_P,),
                 "E175-A2-H1": tuple(sorted({n + N_P for n in N_G_SET}))}
    L = lines_at(R, n_by_rule)
    truths = {
        "e2e": (gov_e2e, pin_e2e, R["heat_c"]),
        "e165": (g165, p165, h165),
        "e2e x1.5": ([(1.5 * x, 1.5 * y) for x, y in gov_e2e], [(1.5 * x, 1.5 * y) for x, y in pin_e2e], [1.5 * x for x in R["heat_c"]]),
        "e2e level": ([(x + 3.0, y + 0.5) for x, y in gov_e2e], [(x, y + 0.5) for x, y in pin_e2e], [x + 0.5 for x in R["heat_c"]]),
        "e2e x0.5": ([(0.5 * x, 0.5 * y) for x, y in gov_e2e], [(0.5 * x, 0.5 * y) for x, y in pin_e2e], [0.5 * x for x in R["heat_c"]]),
    }
    pw = {}
    for t, (g, p, h) in truths.items():
        pw[t] = {str(n): power(t, g, p, h, n, N_P, L) for n in N_G_SET}
    desc = {t: {"gov_n": len(g), "gov_rms_mhz": rms([x for x, _ in g]), "gov_mean_mhz": mean([x for x, _ in g]),
                "gov_rms_w": rms([y for _, y in g]), "gov_mean_w": mean([y for _, y in g]), "pin_n": len(p),
                "pin_rms_mhz": rms([x for x, _ in p]), "pin_rms_w": rms([y for _, y in p]), "pin_mean_w": mean([y for _, y in p]),
                "heat_n": len(h), "heat_rms_c": rms(h)} for t, (g, p, h) in truths.items()}
    out = {"_note": "Q143(g) design_power_e175.py: E175's lines at the planned n and each rule's power, design only, before any E175 tile",
           "planned": {"governed": N_G, "pinned": N_P, "all": N_ALL, "governed_minimum": 8, "all_minimum": 10},
           "rank2_lines": LINES, "draws": DRAWS, "predictor_lists": lists, "lines": L, "truths": desc, "power_pct": pw,
           "e165_results_sha256": A.fsha(E165_RES), "e165_predictions_sha256": A.fsha(A.E165_PRED)}
    s = json.dumps(out, indent=1, sort_keys=True)
    if a.out:
        open(a.out, "w").write(s + "\n")
    T = ["E175's lines at the planned n and each rule's power (design only; no E175 tile, count or prediction exists)", ""]
    T.append("Lines (the frozen engine, seed 80,000 + the rule id's character codes, 20,000 draws), PASS at or below the upper end:")
    for rule, by_n in L.items():
        for n, v in by_n.items():
            T.append(f"  {rule:12s} n {int(n):2d}: {v['range_95'][0]:.3f} to {v['range_95'][1]:.3f} {v['unit']} (reference n {v['ref_n']}, rms {v['ref_rms']:.4f})")
    T.append("")
    T.append("The truths (rms and mean of the errors drawn):")
    for t, d in desc.items():
        T.append(f"  {t:10s}: governed {d['gov_n']} cells, clock rms {d['gov_rms_mhz']:.3f} mean {d['gov_mean_mhz']:+.3f} MHz, board rms {d['gov_rms_w']:.3f} "
                 f"mean {d['gov_mean_w']:+.3f} W; pinned {d['pin_n']}, clock rms {d['pin_rms_mhz']:.3f} MHz, board rms {d['pin_rms_w']:.3f} mean "
                 f"{d['pin_mean_w']:+.3f} W; heat {d['heat_n']}, rms {d['heat_rms_c']:.4f} C")
    T.append("")
    T.append(f"Power: the share of {DRAWS:,} draws reading PASS (%), at n_g governed and {N_P} pinned:")
    hdr = ("G_rms", "G_mean", "G", "Bg", "Bp", "R2", "F1", "W1", "F2", "W2", "H1")
    T.append("  truth      n_g  " + "  ".join(f"{k:>6s}" for k in hdr))
    for t in truths:
        for n in N_G_SET:
            v = pw[t][str(n)]
            T.append(f"  {t:10s} {n:3d}  " + "  ".join(f"{v[k]:6.1f}" for k in hdr))
    print("\n".join(T))
    return 0


if __name__ == "__main__":
    sys.exit(main())
