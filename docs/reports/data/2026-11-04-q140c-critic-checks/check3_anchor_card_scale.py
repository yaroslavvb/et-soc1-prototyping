#!/usr/bin/env python3
"""Q140(c) check 3 (post hoc, desk only; nothing registered): card 1's scale against aifoundry3 from the random anchors that
ran on both 600 MHz cards, against pool 6's own per-tile ratios and M8's card term.

    python3 -I -B check3_anchor_card_scale.py <lab repo root> --out check3-anchor-card-scale.json > check3-anchor-card-scale.txt

Standard library only. Inputs (committed, read only): E153's scored.json (aifoundry3, primary.primary) and E157's scored.json
(card 1, primary): e78_anchors_D (E78's fp32 randn, fp16 randn and int8 full tiles, every pass) and pool_anchors (pool 6's
fp32.anchor6_randn, fp16.anchor6_randn, int8.anchor6_full; their pass means), and both cards' power_rows (measured D);
E157's scored-e153.json E157-X1 / E157-X2 (the registered card-term rules: the median of D(card 1) / D(aifoundry3) over
non-anchor float tiles with D >= 5 W on both cards, int8 tiles with D >= 1 W) and M8's card term (0.9616). Each card's D is
its primary reduction on Q139(u)'s footing.

What it computes:
  * each random anchor's ratio, card 1 over aifoundry3, and the float and int8 scales two ways: the median of the anchors'
    ratios (rank 4's proposed rule, "a card's scale is the median of its anchors' ratios to aifoundry3's") and their mean;
    each against X1's / X2's pool median and against M8's 0.9616;
  * the anchor ratios' own standard error from the passes (each card's sd over passes / sqrt(n), combined in quadrature
    on the ratio): E78's anchors carry per-pass values; pool 6's anchors carry only pass means, so their SE is taken as
    the same relative SE as E78's tile of the same format on that card (stated as an assumption);
  * the per-tile card transfer: X1's 25 float and X2's 16 int8 tiles, ratios recomputed from both cards' measured D and
    checked against the committed ratios; their relative rms about M8's 0.9616, about the pool's own median, and about
    the anchors' scale;
  * whether rank 4's proposed rule ("within 1% of the pool's median ratio for floats and within 2% for int8") is met here.
"""
import argparse
import json
import math
import os
import statistics as st

E153 = "docs/reports/data/2026-11-03-e153-blind6-aifoundry3/scored.json"
E157 = "docs/reports/data/2026-11-03-e157-blind6-card1/scored.json"
E157X = "docs/reports/data/2026-11-03-e157-blind6-card1/scored-e153.json"
M8_CARD = 0.9615998850616304
ANCH = {"fp32": ("fp32.randn", "fp32.anchor6_randn"), "fp16": ("fp16.randn", "fp16.anchor6_randn"), "int8": ("int8.full", "int8.anchor6_full")}


def rms(e):
    return math.sqrt(sum(x * x for x in e) / len(e)) if e else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    A = json.load(open(os.path.join(root, E153)))["primary"]["primary"]
    C = json.load(open(os.path.join(root, E157)))["primary"]
    X = json.load(open(os.path.join(root, E157X)))["primary"]["rules"]
    out = {"_note": "Q140(c) check 3: post hoc desk check, nothing registered. Card 1 / aifoundry3 from the random anchors run on both cards.",
           "inputs": {"aifoundry3": E153 + " primary.primary", "aifoundry1c1": E157 + " primary", "X1_X2": E157X + " primary.rules"},
           "M8_card_term": M8_CARD}
    L = ["CHECK 3. CARD 1 / aifoundry3 FROM THE RANDOM ANCHORS RUN ON BOTH CARDS (post hoc)"]
    anchors = {}
    for t, (e78, p6) in ANCH.items():
        ea, ec = A["e78_anchors_D"][e78], C["e78_anchors_D"][e78]
        pa, pc = A["pool_anchors"][p6], C["pool_anchors"][p6]
        r78 = ec["mean"] / ea["mean"]
        rel_se = lambda d: st.stdev(d["per_pass"]) / math.sqrt(len(d["per_pass"])) / d["mean"]
        se78 = r78 * math.hypot(rel_se(ea), rel_se(ec))
        rp6 = pc["measured_D"] / pa["measured_D"]
        sep6 = rp6 * math.hypot(rel_se(ea), rel_se(ec))   # assumption: the same relative SE as E78's tile of this format, per card
        anchors[t] = {"E78": {"tile": e78, "aifoundry3_D": ea["mean"], "card1_D": ec["mean"], "ratio": r78, "ratio_se": se78,
                              "passes": [len(ea["per_pass"]), len(ec["per_pass"])], "rel_sd_per_pass": [st.stdev(ea["per_pass"]) / ea["mean"], st.stdev(ec["per_pass"]) / ec["mean"]]},
                      "pool6": {"tile": p6, "aifoundry3_D": pa["measured_D"], "card1_D": pc["measured_D"], "ratio": rp6, "ratio_se_assumed": sep6}}
        L.append(f"  {t}: E78 {e78} {ea['mean']:.3f} / {ec['mean']:.3f} W -> {r78:.4f} +- {se78:.4f} (per-pass sd {100 * anchors[t]['E78']['rel_sd_per_pass'][0]:.2f}% / "
                 f"{100 * anchors[t]['E78']['rel_sd_per_pass'][1]:.2f}% of D, {len(ea['per_pass'])} / {len(ec['per_pass'])} passes); pool 6 {p6} {pa['measured_D']:.3f} / {pc['measured_D']:.3f} W -> {rp6:.4f} (+- {sep6:.4f} assumed)")
    out["anchors"] = anchors
    fl = [anchors[t][k]["ratio"] for t in ("fp32", "fp16") for k in ("E78", "pool6")]
    i8 = [anchors["int8"][k]["ratio"] for k in ("E78", "pool6")]
    x1, x2 = X["E157-X1"], X["E157-X2"]
    sc = {"floats": {"anchor_ratios": fl, "median": st.median(fl), "mean": st.mean(fl), "pool_median_X1": x1["median_ratio"],
                     "X1_95": [x1["lo95"], x1["hi95"]]},
          "int8": {"anchor_ratios": i8, "median": st.median(i8), "mean": st.mean(i8), "pool_median_X2": x2["median_ratio"],
                   "X2_95": [x2["lo95"], x2["hi95"]]}}
    for k, q in sc.items():
        pm = q["pool_median_X1"] if k == "floats" else q["pool_median_X2"]
        q["median_vs_pool_rel"] = q["median"] / pm - 1
        q["mean_vs_pool_rel"] = q["mean"] / pm - 1
        q["median_vs_M8_rel"] = q["median"] / M8_CARD - 1
        q["pool_vs_M8_rel"] = pm / M8_CARD - 1
        q["rank4_rule_line"] = 0.01 if k == "floats" else 0.02
        q["rank4_rule_met"] = abs(q["median_vs_pool_rel"]) <= q["rank4_rule_line"]
        q["each_anchor_vs_pool_rel"] = [r / pm - 1 for r in q["anchor_ratios"]]
    # the scale's own uncertainty from the anchors (independent ratios, combined)
    se_f = [anchors[t]["E78"]["ratio_se"] for t in ("fp32", "fp16")] + [anchors[t]["pool6"]["ratio_se_assumed"] for t in ("fp32", "fp16")]
    se_i = [anchors["int8"]["E78"]["ratio_se"], anchors["int8"]["pool6"]["ratio_se_assumed"]]
    sc["floats"]["mean_se_from_passes"] = math.sqrt(sum(s * s for s in se_f)) / len(se_f)
    sc["int8"]["mean_se_from_passes"] = math.sqrt(sum(s * s for s in se_i)) / len(se_i)
    out["scale"] = sc
    L.append("")
    for k, q in sc.items():
        pm = q["pool_median_X1"] if k == "floats" else q["pool_median_X2"]
        lo, hi = q["X1_95"] if k == "floats" else q["X2_95"]
        L.append(f"  {k}: anchors {', '.join(f'{r:.4f}' for r in q['anchor_ratios'])} -> median {q['median']:.4f} ({100 * q['median_vs_pool_rel']:+.2f}% vs the pool's {pm:.4f} "
                 f"[{lo:.4f}, {hi:.4f}]), mean {q['mean']:.4f} ({100 * q['mean_vs_pool_rel']:+.2f}%), each anchor {', '.join(f'{100 * x:+.2f}%' for x in q['each_anchor_vs_pool_rel'])}; "
                 f"the anchors' mean +- {q['mean_se_from_passes']:.4f} from their passes ({100 * q['mean_se_from_passes'] / q['mean']:.2f}%); "
                 f"median vs M8's {M8_CARD:.4f}: {100 * q['median_vs_M8_rel']:+.2f}%; pool vs M8: {100 * q['pool_vs_M8_rel']:+.2f}%; "
                 f"rank 4's line ({100 * q['rank4_rule_line']:.0f}%) met: {q['rank4_rule_met']}")
    # per-tile transfer
    pa, pc = A["power_rows"]["M8"], C["power_rows"]["M8"]
    tr = {}
    for k, rule, line in (("floats", x1, 5.0), ("int8", x2, 1.0)):
        names = sorted(rule["ratios"])
        sel = sorted(n for n, v in pa.items() if not v["pool_anchor"] and n.split(".")[0] in (("fp32", "fp16") if k == "floats" else ("int8",))
                     and v["measured"] >= line and pc[n]["measured"] >= line)
        mine = {n: pc[n]["measured"] / pa[n]["measured"] for n in sel}
        dev = max(abs(mine[n] - rule["ratios"][n]) for n in names) if set(sel) == set(names) else None
        pm = rule["median_ratio"]
        ref_anchor = sc[k]["median"]
        rel_m8 = [mine[n] / M8_CARD - 1 for n in sel]
        rel_pool = [mine[n] / pm - 1 for n in sel]
        rel_anchor = [mine[n] / ref_anchor - 1 for n in sel]
        tr[k] = {"n": len(sel), "same_tiles_as_registered": set(sel) == set(names), "max_abs_ratio_vs_committed": dev,
                 "rel_rms_about_M8": rms(rel_m8), "rel_rms_about_pool_median": rms(rel_pool), "rel_rms_about_anchor_scale": rms(rel_anchor),
                 "rel_mean_about_M8": st.mean(rel_m8), "worst": sorted(((n, mine[n] / M8_CARD - 1) for n in sel), key=lambda x: -abs(x[1]))[:4]}
        q = tr[k]
        L.append(f"  per tile, {k} ({q['n']} tiles with D >= {line:g} W on both; the registered set: {q['same_tiles_as_registered']}; ratios vs committed max |d| {q['max_abs_ratio_vs_committed']:.1e}): "
                 f"relative rms about M8's 0.9616 {100 * q['rel_rms_about_M8']:.2f}% (mean {100 * q['rel_mean_about_M8']:+.2f}%), about the pool median {100 * q['rel_rms_about_pool_median']:.2f}%, "
                 f"about the anchors' scale {100 * q['rel_rms_about_anchor_scale']:.2f}%; worst {', '.join(f'{n} {100 * v:+.1f}%' for n, v in q['worst'])}")
    out["per_tile_transfer"] = tr
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    print("\n".join(L))


if __name__ == "__main__":
    main()
