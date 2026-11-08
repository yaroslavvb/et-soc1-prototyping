#!/usr/bin/env python3
"""E184 (Q156), the data's dated notes 1 (README-arm-s.md.dated-note-1.md and README.md.dated-note-1.md): the figures they state, read after
the data verifier of Sun 8 Nov 2026. Post hoc: written after the data; it decides nothing, and no registered reading changes.

It reads only committed files, as JSON, and imports no lab module (it re-states the few formulas it needs, each named below):
  this directory's posthoc-arms-e184.json (arm S's smoke, read by the kit's readers), reduced-e184b-v4.json and scored-e184-v3.json (arm B);
  tools/claims-v3/e184/forecast-e184.json (the two noise models' quad sd; E184-M's bands), inputs-e184.json (8.256 mW a minion),
  a2-check-e184.json (A2-5's set-aside refreshes on E180's bursts) and power-e184-a3.json (A3-1's NO-GO table, for the check).
Sections:
  S1  the smoke's 16-shire n = 19 quad: the gate's and A2-5's readings recomputed from its kept refreshes; A2-5's reading over the registered
      step and its 95% interval under the registration's two quad sds (base, twice the noise); how far E178's 0.2865 and A3-1's long
      readings lie from it; the dip's share of the gate's excess; the block means' drift (and the same for the 32-shire n = 121 quad).
  S2  A3-1's NO-GO chance at that quad (one quad, Gaussian, kit note 1's band -0.15 to +0.30 W) with a dip term: A2's own contamination
      model (power_e184_a2.contam: a quad holds one uncaught dip with chance 1 - (1 - rate)^(4 n), its depth one of A2-5's five, in an A or
      a B block alike, moving the contrast by +- depth / 2n), at A2's 7 refreshes a block and at the quad's own 9; and, post hoc, with
      today's two set-aside refreshes pooled into the rate and the depths. The no-dip column is checked against power-e184-a3.json > K.
  S5  the minion rail's single-quad contrasts in posthoc-arms-e184.json, beside the board's, in the smoke's order.
  B6  E184-M's pooled f interval: the registered bootstrap (score_e184.score_b: the min/avg and the max/avg lists resampled with
      independent indexes, seed 18404, 2,000 draws), re-made here and checked against scored-e184-v3.json, beside a paired bootstrap that
      resamples samples (each sample's two ratios together), with the same seed and draws and with 20,000 draws of another seed.
Usage (from the top of the lab repository):
  D=docs/reports/data/2026-11-08-e184-sensor-validation
  /usr/bin/python3 -B $D/posthoc_note1_e184.py $D > $D/posthoc-note1-e184.json
Pure Python, seeded; the same bytes under /usr/bin/python3 3.9 and python3 3.13. It prints JSON only, with no path but committed names.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import random
import sys

D = sys.argv[1]
K = os.path.join("tools", "claims-v3", "e184")
ARMS = json.load(open(os.path.join(D, "posthoc-arms-e184.json")))
RED_B = json.load(open(os.path.join(D, "reduced-e184b-v4.json")))
SC = json.load(open(os.path.join(D, "scored-e184-v3.json")))
FC = json.load(open(os.path.join(K, "forecast-e184.json")))
INP = json.load(open(os.path.join(K, "inputs-e184.json")))
CHK = json.load(open(os.path.join(K, "a2-check-e184.json")))
P3 = json.load(open(os.path.join(K, "power-e184-a3.json")))

S_W = INP["e180_anchor"]["board_mw_per_minion"] / 1000.0      # E184.md section 5.1: 8.256 mW a minion on the board
QSD = {m: FC["models"][m]["quad_sd_w"] for m in ("base", "pess")}
BAND = (-0.15, 0.30)                                            # kit note 1 section 1, the 16-shire n = 19 quad
ROBUST_W = 0.5                                                  # A2-5: a kept refresh more than 0.5 W from its block's median
G_E178 = 0.2865                                                 # E178's int8 pair over M10's forecast, as A2-7 reads it (power_e184_a2 K)
Z95 = 1.959964


def r6(x):
    return None if x is None or x != x else float("%.6g" % x)


def phi(x):                                                     # power_e184_a2.phi's form
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def median(xs):                                                 # e184_common.median's rule
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return float("nan")
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def mean(xs):
    return math.fsum(xs) / len(xs)      # fsum: exactly rounded, so 3.9 and 3.12+ (whose sum() compensates) agree


# ---- S1 ---------------------------------------------------------------------------------------------------------------------------------------
def quad_read(q):
    """the gate's and A2-5's quad contrasts from the committed kept refreshes: mean(B blocks) - mean(A blocks), each block its refreshes'
    mean, with or without A2-5's set-aside"""
    blocks = q["blocks_refreshes"]
    out = {"orient": q["orient"], "blocks": []}
    for b in blocks:
        xs = b["refreshes_w"]
        m = median(xs)
        kept = [x for x in xs if abs(x - m) <= ROBUST_W]
        out["blocks"].append({"label": b["label"], "n": len(xs), "mean_all_w": r6(mean(xs)), "median_w": r6(m),
                              "set_aside_w": [x for x in xs if abs(x - m) > ROBUST_W], "mean_a2_5_w": r6(mean(kept)), "n_a2_5": len(kept)})
    for key, tag in (("mean_all_w", "y_gate_w"), ("mean_a2_5_w", "y_a2_5_w")):
        a = [b[key] for b in out["blocks"] if b["label"] == "A"]
        bb = [b[key] for b in out["blocks"] if b["label"] == "B"]
        out[tag + "_recomputed"] = r6(mean(bb) - mean(a))
    return out


def s1():
    out = {}
    for q in ARMS["quads"]:
        if (q["mask_m"], q["n"]) not in ((16, 19), (32, 121)):
            continue
        tag = "m%d_n%d" % (q["mask_m"], q["n"])
        step = q["registered_step_board_w"]
        rd = quad_read(q)
        g = q["y_a2_5_w"] / step
        e = {"seq": q["seq"], "orient": q["orient"], "registered_step_w": step, "y_gate_w": q["y_gate_w"], "y_a2_5_w": q["y_a2_5_w"],
             "recomputed_here": rd, "gain_gate": r6(q["y_gate_w"] / step), "gain_a2_5": r6(g),
             "gate_excess_over_step_w": r6(q["y_gate_w"] - step), "dip_part_w": r6(q["y_gate_w"] - q["y_a2_5_w"]),
             "dip_share_of_excess": r6((q["y_gate_w"] - q["y_a2_5_w"]) / (q["y_gate_w"] - step)) if q["y_gate_w"] != step else None,
             "a2_5_excess_over_step_w": r6(q["y_a2_5_w"] - step)}
        for b in rd["blocks"]:
            for x in b["set_aside_w"]:
                e.setdefault("dips", []).append({"block": b["label"], "refresh_w": x, "below_block_median_w": r6(b["median_w"] - x),
                                                 "block_refreshes": b["n"], "contrast_shift_w": r6((b["median_w"] - x) / (2.0 * b["n"]))})
        e["noise"] = {}
        for model in ("base", "pess"):
            sg = QSD[model] / step
            e["noise"][model] = {"quad_sd_w": r6(QSD[model]), "gain_sd": r6(sg), "gain_ci95": [r6(g - Z95 * sg), r6(g + Z95 * sg)],
                                 "z_of_1": r6((g - 1.0) / sg), "z_of_e178_0p2865": r6((g - G_E178) / sg),
                                 "z_of_a3_1_long_1p2": r6((g - 1.2) / sg), "z_of_a3_1_long_1p6": r6((g - 1.6) / sg)}
        b = rd["blocks"]
        e["drift"] = {"order": "".join(x["label"] for x in b),
                      "first_minus_last_same_label_w": r6(b[0]["mean_a2_5_w"] - b[3]["mean_a2_5_w"]),
                      "second_minus_third_w": r6(b[1]["mean_a2_5_w"] - b[2]["mean_a2_5_w"]),
                      "note": "with A2-5; a linear drift gives first - last = 3 x (second - third) in one quad; one quad cannot separate a "
                              "curved drift from its step (the registration cancels it across ABBA and BAAB quads)"}
        out[tag] = e
    return out


# ---- S2 ---------------------------------------------------------------------------------------------------------------------------------------
def ng0(mu, sq):
    return phi((BAND[0] - mu) / sq) + 1.0 - phi((BAND[1] - mu) / sq)


def ng_dip(mu, sq, rate, depths, n):
    """A2's contamination model on one quad of 4 blocks of n refreshes: one dip at most, chance 1 - (1 - rate)^(4n); its depth uniform over
    `depths`; an A block (+depth / 2n) or a B block (-depth / 2n) alike"""
    pq = 1.0 - (1.0 - rate) ** (4 * n)
    dd = math.fsum((ng0(mu + d / (2.0 * n), sq) + ng0(mu - d / (2.0 * n), sq)) / 2.0 for d in depths) / len(depths)
    return (1.0 - pq) * ng0(mu, sq) + pq * dd, pq


def s2():
    e = CHK["e180_fadd_bursts"]
    rate, depths = e["rate_set_aside_per_block_refresh"], list(e["depths_w"])
    today = []
    nref_today = 0
    for q in ARMS["quads"]:
        for b in q["blocks_refreshes"]:
            nref_today += len(b["refreshes_w"])
            m = b["median_w"]
            today += [r6(m - x) for x in b["a2_5_set_aside_w"]]
    pooled_rate = (len(depths) + len(today)) / float(e["block_refreshes"] + nref_today)
    y19 = S_W * 19
    gains = [1.0 + k / 10.0 for k in range(11)] + [G_E178]
    variants = [("A2's model as written (7 refreshes a block; A2-5's E180 rate and five depths)", rate, depths, 7),
                ("the same at the quad's own 9 refreshes a block", rate, depths, 9),
                ("post hoc: today's smoke's set-aside refreshes pooled into the rate and the depths, 9 refreshes a block",
                 pooled_rate, depths + today, 9)]
    out = {"expected_w_if_linear": r6(y19), "band_w": list(BAND),
           "e180_rate_per_block_refresh": rate, "e180_depths_w": depths, "e180_block_refreshes": e["block_refreshes"],
           "today_set_aside_depths_w": today, "today_smoke_kept_refreshes": nref_today,
           "today_rate_per_block_refresh": r6(len(today) / float(nref_today)), "pooled_rate_per_block_refresh": r6(pooled_rate),
           "depth_alone_past_0p30_w": {"n %d" % n: r6(2.0 * n * (BAND[1] - y19)) for n in (7, 8, 9)}, "models": {}}
    for model in ("base", "pess"):
        sq = QSD[model]
        rows = {}
        for g in gains:
            mu = g * y19
            row = {"no dip (A3-1)": r6(ng0(mu, sq))}
            for name, rt, dp, n in variants:
                p, pq = ng_dip(mu, sq, rt, dp, n)
                row[name] = r6(p)
            rows["small steps read %s" % ("%.1f" % g if g != G_E178 else "0.2865")] = row
        quads_with_dip = {name: r6(1.0 - (1.0 - rt) ** (4 * n)) for name, rt, dp, n in variants}
        a3 = P3["K"][model]["no_go"]
        check = all(r6(ng0((1.0 + k / 10.0) * y19, sq)) == a3["small steps read %.1f" % (1.0 + k / 10.0)] for k in range(11))
        out["models"][model] = {"quad_sd_w": r6(sq), "no_go": rows, "quads_with_a_dip": quads_with_dip,
                                "no_dip_column_equals_power_e184_a3_K": check}
    return out


# ---- S5 ---------------------------------------------------------------------------------------------------------------------------------------
def s5():
    rows = []
    for q in ARMS["quads"]:
        rows.append({"seq": q["seq"], "quad": "m%d n%d" % (q["mask_m"], q["n"]), "orient": q["orient"],
                     "board_y_gate_w": q["y_gate_w"], "board_over_step": q["reading_over_step"],
                     "rail_y_w": q["y_rail_w"], "rail_registered_step_w": q["registered_step_rail_w"], "rail_over_step": q["rail_over_step"]})
    return {"quads_in_smoke_order": rows,
            "label": "the minion rail's quad contrasts: the rail's PMIC average filters over about 1.06 s, longer than half a 1.6 s block "
                     "(A2-3), so one quad's rail contrast carries the transient of the quad before it; reported, never a power reading"}


# ---- B6 ---------------------------------------------------------------------------------------------------------------------------------------
def pct(fs, reps):
    fs = sorted(fs)
    return fs[int(math.floor(0.025 * (reps - 1)))], fs[int(math.ceil(0.975 * (reps - 1)))]


def b6():
    lv = [x for x in RED_B["passes"]["18441"]["levels"] if x["sram_w"]["n"] >= 10]
    pm = [v for x in lv for v in x["sram_w"]["min_over_avg_all"]]
    pM = [v for x in lv for v in x["sram_w"]["max_over_avg_all"]]
    paired_lists = all(len(x["sram_w"]["min_over_avg_all"]) == len(x["sram_w"]["max_over_avg_all"]) == x["sram_w"]["n"] for x in lv)
    N = len(pm)

    def unpaired(seed, reps):
        r = random.Random(seed)
        fs = []
        for _ in range(reps):
            mm = median([pm[r.randrange(len(pm))] for _ in pm])
            MM = median([pM[r.randrange(len(pM))] for _ in pM])
            fs.append((mm / MM + 1) / 2)
        return pct(fs, reps)

    def paired(seed, reps):
        r = random.Random(seed)
        fs = []
        for _ in range(reps):
            ix = [r.randrange(N) for _ in range(N)]
            fs.append((median([pm[i] for i in ix]) / median([pM[i] for i in ix]) + 1) / 2)
        return pct(fs, reps)

    f = (median(pm) / median(pM) + 1) / 2
    u = unpaired(18404, 2000)
    p = paired(18404, 2000)
    u2 = unpaired(20261108, 20000)
    p2 = paired(20261108, 20000)
    m = SC["arm_B"]["E184-M"]
    hm = FC["forecasts"]["card1_sram"]["H-MIX"]
    return {"levels": len(lv), "pooled_samples": N, "lists_paired_by_sample": paired_lists, "f": r6(f), "committed_f": m["f"],
            "registered_unpaired_seed18404_2000": [r6(u[0]), r6(u[1])], "committed_f_ci95": m["f_ci95"],
            "registered_remade_equals_committed": [r6(u[0]), r6(u[1])] == m["f_ci95"],
            "paired_seed18404_2000": [r6(p[0]), r6(p[1])],
            "unpaired_seed20261108_20000": [r6(u2[0]), r6(u2[1])], "paired_seed20261108_20000": [r6(p2[0]), r6(p2[1])],
            "band_f": hm["band_f"], "both_inside_band_f": all(hm["band_f"][0] <= a <= hm["band_f"][1] for a in (u[0], u[1], p[0], p[1])),
            "spread_min_over_avg": m["spread_min_over_avg"], "level_spread_max": hm["level_spread_max"], "verdict": m["verdict"],
            "label": "the verdict turns on the levels' min/avg span (0.081 against 0.06), which no bootstrap of f touches"}


out = {"what": "E184's data, dated notes 1: post hoc figures (written after the data; deciding nothing)", "S1": s1(), "S2": s2(), "S5": s5(),
       "B6": b6()}
json.dump(out, sys.stdout, indent=1, sort_keys=True)
sys.stdout.write("\n")
