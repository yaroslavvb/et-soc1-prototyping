#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(x): M8's card scale per card from its cheap-read predictor, for blind pool 6, computed mechanically (nothing refitted).

    python3 card_scale_blind6.py <pool dir> <out.json>        (run from the top of the tree, with a python that has numpy)

The predictor is Q139(m)'s registration section 6, as fit_m8.py's loco() implements it: for a held-out card h and the two other
cards i, j, ln s_h = mean over r in (i, j) of [ln s_r + beta x ln(read_h / read_r)], with beta (a) the physical exponent (the 600 MHz
voltage: 2; idle board power, the fp32 zeros level, the leakage slope: 1) or (b) fitted on the other two cards,
beta = ln(s_i / s_j) / ln(read_i / read_j). loco() is called unchanged on m8.json's frozen card_scale_predictor.measured and .reads,
and its output must equal m8.json's frozen loco exactly. The registration quotes the predictor only for an unmeasured card: on
card 1 M8 keeps its measured card term (0.9616) and on aifoundry2 the D scale g of its burst relation; both are listed per card.

Per tile on aifoundry1 card 1, the file also gives D600 (M8's D on aifoundry3's footing, from predictions-blind6-aifoundry1c1.json)
times each predicted scale: what M8 would say for card 1 if card 1 were a card nobody had measured. No band is given for these:
M8 registered none for an unmeasured card.
"""
import hashlib
import json
import math
import os
import sys

TREE = os.getcwd()
M8D = os.path.join(TREE, "docs", "reports", "data", "2026-11-03-q139m-model")
M7J = os.path.join(TREE, "docs", "reports", "data", "2026-11-02-q138m-model", "m7.json")
M6J = os.path.join(TREE, "docs", "reports", "data", "2026-11-02-q137m-model", "m6.json")
sys.path.insert(0, M8D)
import fit_m8 as M8  # noqa: E402  (unchanged; its loco() is the registered predictor)

fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
CARD = {"a3": "aifoundry3", "c1": "aifoundry1c1", "a2": "aifoundry2"}
FAM_TYPES = {"floats": ("fp32", "fp16"), "int8": ("int8",)}


def main():
    pool, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    m8p = os.path.join(M8D, "m8.json")
    m8, m7, m6 = (json.load(open(p)) for p in (m8p, M7J, M6J))
    csp = m8["card_scale_predictor"]
    lc = M8.loco(csp["measured"], csp["reads"])
    same = json.loads(json.dumps(lc)) == csp["loco"]
    if not same:
        raise SystemExit("loco() on m8.json's frozen inputs does not reproduce m8.json's frozen loco: stop")
    reads = [r for r in ("V600_v", "idle_w", "zeros_level_fp32_w", "leak_w_per_c") if r in lc]
    cards = {}
    for cd, nm in CARD.items():
        fams = {}
        for fam in ("floats", "int8"):
            fk = "float" if fam == "floats" else "int8"
            t0 = FAM_TYPES[fam][0]
            applied = {
                "M8": (m8["families"][fk]["card1_scale_by_format"][t0] if cd == "c1" else
                       m8["aifoundry2"]["params"]["g"][t0] if cd == "a2" else 1.0),
                "M7": (m7["families"][fk]["card1_scale_by_format"][t0] if cd == "c1" else
                       1.0 / m7["aifoundry2"]["relation"]["xfer"] if cd == "a2" else 1.0),
                "M6": (m6["families"][fk]["card1_scale"] if cd == "c1" else
                       1.0 / m7["aifoundry2"]["relation"]["xfer"] if cd == "a2" else 1.0),
            }
            pred = {}
            for rd in reads:
                ho = lc[rd]["held_out"].get(f"{fam}|{cd}")
                if not ho:
                    continue
                for form in ("physical", "fitted_on_other_two"):
                    v = ho.get(form)
                    if v is None:
                        continue
                    pred[f"{rd}|{form}"] = {"beta": v["beta"], "pred_scale": v["pred_scale"],
                                            "train_meas_scale": v["meas_scale"], "train_rel_err": v["rel_err"],
                                            "train_within_1pct": v["within_1pct"]}
            fams[fam] = {"scale_applied_by_model": applied, "train_measured_scale": csp["measured"][cd][fam],
                         "cheap_read_predicted_scale": pred,
                         "reads_this_card": {rd: csp["reads"][rd][cd] for rd in reads}}
        cards[nm] = fams
    # per tile on card 1: D600 (aifoundry3's footing) x each predicted scale
    pc1 = os.path.join(pool, "predictions-blind6-aifoundry1c1.json")
    P = json.load(open(pc1))
    tiles = {}
    for name, rec in sorted(P["tiles"].items()):
        if "M8" not in rec:
            tiles[name] = {"error": rec.get("error", "no M8 prediction")}
            continue
        t = rec["type"]
        fam = "int8" if t == "int8" else "floats"
        d600 = rec["M8"]["D600_a3_footing_w"]
        cs = cards["aifoundry1c1"][fam]["cheap_read_predicted_scale"]
        tiles[name] = {"type": t, "priority": rec.get("priority"), "D600_a3_footing_w": d600,
                       "M8_D_w_measured_card1_scale": rec["M8"]["D_w"],
                       "D_w_if_card1_unmeasured": {k: round(d600 * v["pred_scale"], 4) for k, v in cs.items()}}
    res = {"_note": "Q139(x): M8's card scale per card from its cheap-read predictor (registration section 6; fit_m8.loco "
                    "unchanged on m8.json's frozen inputs); nothing refitted. The predictor FAILED its 1% rule for every read "
                    "and form on the training cards (m8.json card_scale_predictor); it is quoted for a card nobody has measured. "
                    "M8 itself applies the measured scales listed under scale_applied_by_model.",
           "formula": "ln s_h = 0.5 x sum over the two other cards r of [ln s_r + beta x ln(read_h / read_r)]; beta physical "
                      "(V600: 2; idle_w, zeros_level_fp32_w, leak_w_per_c: 1) or fitted on the other two "
                      "(ln(s_i/s_j) / ln(read_i/read_j)); s = D_card / D_aifoundry3 at 600 MHz on the same tiles",
           "loco_recomputed_equals_frozen": same, "m8_sha256": fsha(m8p), "fit_m8_sha256": fsha(os.path.join(M8D, "fit_m8.py")),
           "m7_sha256": fsha(M7J), "m6_sha256": fsha(M6J), "predictions_c1_sha256": fsha(pc1),
           "reads_sources": {rd: csp["reads"][rd].get("_src") for rd in reads},
           "what_pool6_measures": "E157's card 1 / E153's aifoundry3 median ratio of D on the same pool-6 tiles (floats with "
                                  "D >= 5 W, int8 with D >= 1 W, as m8's measured scale), and E160's (c_w - c_zeros) / D600 on "
                                  "aifoundry2's bursts pinned at 795-800 MHz; the 1% rule applies to each held-out card",
           "cards": cards, "tiles_aifoundry1c1": tiles}
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    for nm, fams in cards.items():
        for fam, v in fams.items():
            p = v["cheap_read_predicted_scale"]
            print(f"{nm:13s} {fam:6s} applied M8 {v['scale_applied_by_model']['M8']:.4f}  train-measured {v['train_measured_scale']:.4f}  "
                  + "  ".join(f"{k.replace('fitted_on_other_two', 'fit')}={q['pred_scale']:.4f}" for k, q in p.items()))
    print("loco recomputed equals frozen:", same, "; tiles on card 1:", len(tiles))


if __name__ == "__main__":
    main()
