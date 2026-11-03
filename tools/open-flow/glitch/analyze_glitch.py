#!/usr/bin/env python3
"""Q138(g): glitch-aware single-bit prices for E130's and E138's tiles, per netlist, against the card's intervals.

    analyze_glitch.py --sims <dir of run_tile.py outputs> --point 471698 --out <json> [--tables <md>]

Per item (item minus its own zero, per designed flip), for the unit (the 16 tima_top instances of the VPU):
  zero-delay toggles (the bench VCD's own settled samples, bench-method; equals settle_count's `ids` for the unit),
  timed toggles (the event simulation with liberty delays, inertial), and the excess (timed - zero-delay): the glitches.
The glitch-aware price in Q136(a)'s frozen frame: the frozen whole-VPU `nets_map` per flip at this launch point, plus the unit's
excess per flip, times each netlist's frozen k. Shapes (ratios) carry no k.
"""
import argparse, json, math, os, sys
LAB = os.environ.get("LAB") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PRED = f"{LAB}/docs/reports/data/2026-11-02-q136a-int8-netlist-predictions/predictions.json"
E130 = f"{LAB}/tools/claims-v3/kinds/e130/e130.json"
ARMS = ["booth_tree", "booth", "booth_swap", "plain"]
# the card's intervals (95%), as committed:
CARD = {
    # E138 scored.json primary (rail, board-equivalent fJ at c_rb 0.81; the ratio has no unit); E130 scored.json
    "B_odd_over_even": {"E138_rail": (1.91, 1.71, 2.16), "E130_rail": (1.79, 1.68, 1.92), "E130_board": (2.41, 1.26, 38.2)},
    "B_odd_minus_even_fJ": {"E138_rail_boardeq": (35.9, 30.5, 41.4), "E130_board": (33.8, 11.0, 56.7)},
    "A_odd_over_even": {"E130_board": (0.98, 0.92, 1.04)},
    "A_odd_minus_even_fJ": {"E130_board": (-1.7, -6.6, 3.2)},
    "A_sign_dense_over_one": {"E130_board": (1.43, 1.36, 1.51)},
    "A_sign_w2_over_w1": {"E130_board": (1.02, 0.98, 1.07)},
    "B_sign_dense_over_one": {"E130_board": (1.18, 0.78, 1.75)},
    "A_sign_dense_minus_one_fJ": {"E130_board": (67.8, 58.8, 76.8)},
    "B_mean_bits0to6_fJ": {"E130_board": (41.9, 28.3, 55.6)},
    "A_mean_bits0to6_fJ": {"E130_board": (79.8, 75.9, 83.8)},
}
E138_RAIL_BITS = [17.9, 56.2, 31.2, 65.4, 46.8, 61.6, 47.4, 82.7]          # E138 README section 3, rail fJ, bits 0..7
E130_A_BOARD = [83.0, 77.2, 71.8, 78.0, 87.7, 82.3, 78.7, 156.7]          # E130 README section 4, board fJ, a1_0..a1_7


def load_card():
    """the card's intervals and per-bit prices read from the committed scored.json files (the rounded values above are their
    READMEs' and agree to the printed digits)"""
    e138 = json.load(open(f"{LAB}/docs/reports/data/2026-11-02-e138-int8-b-rail/scored.json"))["primary"]
    e130 = json.load(open(f"{LAB}/docs/reports/data/2026-11-02-e130-int8-netlists/scored.json"))["primary"]
    st = e130["statistics"]
    r = lambda d: (d["ratio"], d["lo"], d["hi"])
    m = lambda d: (d["mean"], d["lo"], d["hi"])
    CARD["B_odd_over_even"]["E138_rail"] = r(e138["B_odd_over_even"])
    CARD["B_odd_minus_even_fJ"]["E138_rail_boardeq"] = m(e138["B_odd_minus_even_board_equivalent_fJ"])
    CARD["B_odd_over_even"]["E130_board"] = r(st["B_odd_over_even"])
    for k in ("A_odd_over_even", "A_sign_dense_over_one", "A_sign_w2_over_w1", "B_sign_dense_over_one"):
        CARD[k]["E130_board"] = r(st[k])
    for k in ("B_odd_minus_even_fJ", "A_odd_minus_even_fJ", "A_sign_dense_minus_one_fJ", "B_mean_bits0to6_fJ", "A_mean_bits0to6_fJ"):
        CARD[k]["E130_board"] = m(st[k])
    E138_RAIL_BITS[:] = [e138["prices_book_fJ"][f"b1_{i}"]["fJ"]["mean"] for i in range(8)]
    E130_A_BOARD[:] = [e130["prices"][f"a1_{i}"]["fJ"]["mean"] for i in range(8)]


def stats(b, a, extra):
    """b, a: per-bit lists (bits 0..7) for B (base word 1, A=1) and A (A1, B=1); extra: sign variants."""
    odd_b = (b[1] + b[3] + b[5]) / 3
    even_b = (b[0] + b[2] + b[4]) / 3
    odd_a = (a[1] + a[3] + a[5]) / 3
    even_a = (a[0] + a[2] + a[4]) / 3
    return {"B_odd_over_even": odd_b / even_b if even_b else float("nan"), "B_odd_minus_even": odd_b - even_b,
            "A_odd_over_even": odd_a / even_a if even_a else float("nan"), "A_odd_minus_even": odd_a - even_a,
            "A_sign_dense_over_one": extra["a1d_7"] / a[7] if a[7] else float("nan"), "A_sign_dense_minus_one": extra["a1d_7"] - a[7],
            "B_sign_dense_over_one": extra["b1d_7"] / b[7] if b[7] else float("nan"), "B_sign_dense_minus_one": extra["b1d_7"] - b[7],
            "A_sign_w2_over_w1": extra["a2_7"] / a[7] if a[7] else float("nan"), "B_sign_w2_over_w1": extra["b2_7"] / b[7] if b[7] else float("nan"),
            "B_mean_bits0to6": sum(b[:7]) / 7, "A_mean_bits0to6": sum(a[:7]) / 7, "B_list": b, "A_list": a}


def inside(v, iv):
    return iv[1] <= v <= iv[2]


def fit_scale(pred, card):
    """least-squares scale s minimising |card - s*pred|; rms after; and Pearson r"""
    num = sum(p * c for p, c in zip(pred, card))
    den = sum(p * p for p in pred)
    s = num / den if den else float("nan")
    rms = math.sqrt(sum((c - s * p) ** 2 for p, c in zip(pred, card)) / len(card))
    mp, mc = sum(pred) / len(pred), sum(card) / len(card)
    cov = sum((p - mp) * (c - mc) for p, c in zip(pred, card))
    vp = sum((p - mp) ** 2 for p in pred)
    vc = sum((c - mc) ** 2 for c in card)
    r = cov / math.sqrt(vp * vc) if vp and vc else float("nan")
    return s, rms, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", required=True, help="a directory of run_tile.py outputs, or a committed sims/<run>.json")
    ap.add_argument("--point", default="471698", help="one launch point, or several comma-separated (their mean)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--arms", default=",".join(ARMS))
    a = ap.parse_args()
    load_card()
    pred = json.load(open(PRED))
    man = {it["kind"]: it for it in json.load(open(E130))["items"]}
    items = [k for k, it in man.items() if it["zero"]]
    res = {"_what": "Q138(g) glitch-aware single-bit counts and prices, item minus its own zero, per designed flip; "
                    "'_mid' keys hold the mean over the launch points named in 'points'",
           "points": [int(x) for x in a.point.split(",")], "sims": os.path.basename(os.path.normpath(a.sims)), "arms": {}, "card": CARD,
           "card_bits": {"E138_rail_B": E138_RAIL_BITS, "E130_board_A": E130_A_BOARD}}
    for arm in a.arms.split(","):
        k = pred["inputs"]["k_fJ_per_net_toggle"][arm]
        pts = [int(x) for x in a.point.split(",")]
        lp = pred["inputs"]["launch_points_ops"]
        simsp = {}
        packed = json.load(open(a.sims)) if a.sims.endswith(".json") else None     # a committed sims/<run>.json
        for pt in pts:
            for t in man:
                key = f"{arm}__{t}__{pt}"
                if packed is not None:
                    if key in packed:
                        simsp[(t, pt)] = packed[key]
                    continue
                f = os.path.join(a.sims, key + ".json")
                if os.path.exists(f):
                    simsp[(t, pt)] = json.load(open(f))
        sims = {t: simsp[(t, pts[0])] for t in man if all((t, pt) in simsp for pt in pts)}
        if not sims:
            continue
        per = {}
        checks = {"mismatch": 0, "late": 0}
        for (t, pt), sv in simsp.items():
            checks["mismatch"] += sv["total"]["mismatch"]
            checks["late"] += sv["total"]["late"]
        for it in items:
            z = man[it]["zero"]
            if it not in sims or z not in sims:
                continue
            fl = man[it]["designed_flips_per_op"]
            d_timed = sum(simsp[(it, pt)]["total"]["timed"] - simsp[(z, pt)]["total"]["timed"] for pt in pts) / fl / len(pts)
            d_zero = sum(simsp[(it, pt)]["total"]["zero"] - simsp[(z, pt)]["total"]["zero"] for pt in pts) / fl / len(pts)
            stage = {}
            for s in set(sims[it]["by_stage"]) | set(sims[z]["by_stage"]):
                acc = {"timed": 0.0, "zero": 0.0}
                for pt in pts:
                    si = simsp[(it, pt)]["by_stage"].get(s, {"timed": 0, "zero": 0})
                    sz = simsp[(z, pt)]["by_stage"].get(s, {"timed": 0, "zero": 0})
                    acc["timed"] += (si["timed"] - sz["timed"]) / fl / len(pts)
                    acc["zero"] += (si["zero"] - sz["zero"]) / fl / len(pts)
                stage[s] = acc
            fr = pred["arms"][arm]["items"][it]
            fz = sum(fr["fJ_map_by_point"][lp.index(pt)] for pt in pts) / len(pts)
            frozen_mid_nets = fz / k
            per[it] = {"flips_per_op": fl, "unit_zero_per_flip": d_zero, "unit_timed_per_flip": d_timed,
                       "unit_excess_per_flip": d_timed - d_zero, "unit_timed_over_zero": d_timed / d_zero if d_zero else None,
                       "frozen_vpu_map_per_flip_mid": frozen_mid_nets, "frozen_unit_map_per_flip": fr["unit_map_per_flip"],
                       "glitch_vpu_map_per_flip_mid": frozen_mid_nets + d_timed - d_zero,
                       "fJ_zero_mid": fz, "fJ_glitch_mid": k * (frozen_mid_nets + d_timed - d_zero),
                       "by_stage": stage}
        def lists(key):
            b = [per[f"b1_{i}"][key] for i in range(8)]
            aa = [per[f"a1_{i}"][key] for i in range(8)]
            ex = {x: per[x][key] for x in ("a1d_7", "a2_7", "b1d_7", "b2_7")}
            return b, aa, ex
        out = {"k_fJ": k, "checks": checks, "items": per}
        if all(x in per for x in [f"b1_{i}" for i in range(8)] + [f"a1_{i}" for i in range(8)] + ["a1d_7", "a2_7", "b1d_7", "b2_7"]):
            for key, lab in (("fJ_zero_mid", "zero_delay_fJ"), ("fJ_glitch_mid", "glitch_fJ"), ("unit_zero_per_flip", "unit_zero_nets"),
                             ("unit_timed_per_flip", "unit_timed_nets")):
                out[lab] = stats(*lists(key))
            g = out["glitch_fJ"]
            verdict = {}
            for stat, ivs in CARD.items():
                key = stat.replace("_fJ", "")
                v = g[key]
                verdict[stat] = {"glitch": v, "zero_delay": out["zero_delay_fJ"][key],
                                 "inside": {n: inside(v, iv) for n, iv in ivs.items()},
                                 "zero_delay_inside": {n: inside(out["zero_delay_fJ"][key], iv) for n, iv in ivs.items()}}
            out["vs_card"] = verdict
            # glitch weight w: counts = zero-delay + w x excess (w = 0 zero delay, w = 1 every inertial glitch a full toggle);
            # the k-free shapes against the card's intervals at each w
            zl = out["zero_delay_fJ"]
            scan = []
            for wi in range(0, 201):
                w = wi / 100.0
                b = [zl["B_list"][i] + w * (g["B_list"][i] - zl["B_list"][i]) for i in range(8)]
                aa = [zl["A_list"][i] + w * (g["A_list"][i] - zl["A_list"][i]) for i in range(8)]
                ex = {}
                for x in ("a1d_7", "a2_7", "b1d_7", "b2_7"):
                    ex[x] = per[x]["fJ_zero_mid"] + w * (per[x]["fJ_glitch_mid"] - per[x]["fJ_zero_mid"])
                st_ = stats(b, aa, ex)
                scan.append({"w": w, "B_odd_over_even": st_["B_odd_over_even"], "A_odd_over_even": st_["A_odd_over_even"],
                             "A_sign_dense_over_one": st_["A_sign_dense_over_one"], "A_sign_w2_over_w1": st_["A_sign_w2_over_w1"],
                             "in_Aw2": inside(st_["A_sign_w2_over_w1"], CARD["A_sign_w2_over_w1"]["E130_board"]),
                             "in_B": inside(st_["B_odd_over_even"], CARD["B_odd_over_even"]["E138_rail"]),
                             "in_A": inside(st_["A_odd_over_even"], CARD["A_odd_over_even"]["E130_board"]),
                             "in_Asign": inside(st_["A_sign_dense_over_one"], CARD["A_sign_dense_over_one"]["E130_board"])})
            def wr(key):
                ws = [x["w"] for x in scan if x[key]]
                return [min(ws), max(ws)] if ws else None
            exB = [per[f"b1_{i}"]["unit_excess_per_flip"] for i in range(8)]
            exA = [per[f"a1_{i}"]["unit_excess_per_flip"] for i in range(8)]
            out["glitch_weight_scan"] = {"B_ratio_as_w_grows_without_bound": (exB[1] + exB[3] + exB[5]) / (exB[0] + exB[2] + exB[4]),
                                         "A_ratio_as_w_grows_without_bound": (exA[1] + exA[3] + exA[5]) / (exA[0] + exA[2] + exA[4]),
                                         "A_sign_ratio_as_w_grows_without_bound": per["a1d_7"]["unit_excess_per_flip"] / per["a1_7"]["unit_excess_per_flip"],
                                         "w_range_B_ratio_in_E138": wr("in_B"), "w_range_A_ratio_in_E130": wr("in_A"),
                                         "w_range_A_sign_ratio_in_E130": wr("in_Asign"),
                                         "w_all_three": [x["w"] for x in scan if x["in_B"] and x["in_A"] and x["in_Asign"]],
                                         "w_range_A_sign_w2_ratio_in_E130": wr("in_Aw2"),
                                         "w_A_side_all_three": [x["w"] for x in scan if x["in_A"] and x["in_Asign"] and x["in_Aw2"]],
                                         "w_all_four": [x["w"] for x in scan if x["in_B"] and x["in_A"] and x["in_Asign"] and x["in_Aw2"]],
                                         "B_ratio_at": {str(w): next(x["B_odd_over_even"] for x in scan if abs(x["w"] - w) < 1e-9) for w in (0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)},
                                         "A_sign_ratio_at": {str(w): next(x["A_sign_dense_over_one"] for x in scan if abs(x["w"] - w) < 1e-9) for w in (0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)},
                                         "A_ratio_at": {str(w): next(x["A_odd_over_even"] for x in scan if abs(x["w"] - w) < 1e-9) for w in (0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)}}
            # shape against the card's per-bit lists, bits 0..6 (magnitude) and 0..7
            for lab, src in (("glitch_fJ", g), ("zero_delay_fJ", out["zero_delay_fJ"])):
                sB = fit_scale(src["B_list"][:7], E138_RAIL_BITS[:7])
                sA = fit_scale(src["A_list"][:7], E130_A_BOARD[:7])
                out.setdefault("shape", {})[lab] = {"B_vs_E138_rail_bits0to6": {"scale": sB[0], "rms_rail_fJ": sB[1], "r": sB[2]},
                                                    "A_vs_E130_board_bits0to6": {"scale": sA[0], "rms_board_fJ": sA[1], "r": sA[2]}}
        res["arms"][arm] = out
    json.dump(res, open(a.out, "w"), indent=1)
    # print a summary
    for arm, out in res["arms"].items():
        if "glitch_fJ" not in out:
            print(arm, "incomplete", len(out["items"]))
            continue
        g, z = out["glitch_fJ"], out["zero_delay_fJ"]
        print(f"== {arm} (k {out['k_fJ']:.3f}; checks {out['checks']})")
        print("  B list fJ zero :", " ".join(f"{x:6.1f}" for x in z["B_list"]))
        print("  B list fJ glit :", " ".join(f"{x:6.1f}" for x in g["B_list"]))
        print("  A list fJ zero :", " ".join(f"{x:6.1f}" for x in z["A_list"]))
        print("  A list fJ glit :", " ".join(f"{x:6.1f}" for x in g["A_list"]))
        for stat, v in out["vs_card"].items():
            print(f"  {stat:28s} zero {v['zero_delay']:8.3f}  glitch {v['glitch']:8.3f}  inside {v['inside']}")
        print("  shape", json.dumps(out["shape"]))
        print("  w-scan", json.dumps(out["glitch_weight_scan"]))


if __name__ == "__main__":
    main()
