#!/usr/bin/env python3
"""E124 (Q134): which reduction carries the registered verdicts (the set-aside rule), E124's added rules Y1, Y2 and Z on it, the readings it reports
with no verdict, and every quantity beside E109's labelled three-pass value. Registered in E124.md; frozen in predictions-e124.json.

    python3 tools/claims-v3/e124/extras_e124.py --primary e124.json --relaxed e124-relaxed.json --scored scored.json \
        --scored-relaxed scored-relaxed.json --out extras.json --txt extras.txt

The set-aside rule (predictions-e124.json › set_aside_rule): the primary reduction (E78's gates unchanged) carries the verdicts if it keeps >= 3 passes;
else the relaxed one (random_range_w 99 W) if it keeps >= 3; else nothing is scored. Y1 uses posthoc_check_e109.reading() (E109's committed code,
unchanged) for N = S(m0.int8.zeros) - S(m0.fp32.zeros); Y2 reads score_e109.py's e_op; Z reads its R0-R3 verdicts. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/e109"))
import posthoc_check_e109 as phc  # noqa: E402  (E109's committed post-hoc reader, unchanged; its reading() takes any reduce_e78 output)

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}


def ci(v):
    v = [x for x in v if x is not None]
    n = len(v)
    if n == 0:
        return {"mean": None, "half": None, "n": 0, "per_pass": []}
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "half": None, "n": 1, "per_pass": v}
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return {"mean": m, "half": T95[n - 1] * sd / math.sqrt(n), "n": n, "per_pass": v}


def lohi(c):
    if c.get("mean") is None or c.get("half") is None:
        return None, None
    return c["mean"] - c["half"], c["mean"] + c["half"]


def three(c, line):
    lo, hi = lohi(c)
    if lo is None:
        return "NOT-SCORED"
    return "PASS" if lo >= line else "FAIL" if hi < line else "INCONCLUSIVE"


def f(c, k=3, unit=""):
    if c is None or c.get("mean") is None:
        return "—"
    return f"{c['mean']:+.{k}f}" + ("" if c.get("half") is None else f" ± {c['half']:.{k}f}") + (f" {unit}" if unit else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--relaxed", required=True)
    ap.add_argument("--scored", required=True)
    ap.add_argument("--scored-relaxed", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e124.json"))
    a = ap.parse_args()
    P = json.load(open(a.pred))
    prim, rel = json.load(open(a.primary)), json.load(open(a.relaxed))
    need = P["min_kept_passes"]
    if len(prim["passes"]) >= need:
        which, red, sc = "primary", a.primary, json.load(open(a.scored))
    elif len(rel["passes"]) >= need:
        which, red, sc = "relaxed (scored under the set-aside rule)", a.relaxed, json.load(open(a.scored_relaxed))
    else:
        which, red, sc = "none (NOT SCORED: fewer than 3 passes even under the set-aside rule)", None, None
    out = {"experiment": "E124", "which_reduction_scores": which,
           "kept_passes": {"primary": prim["passes"], "relaxed": rel["passes"],
                           "primary_set_aside": prim.get("passes_set_aside"), "relaxed_set_aside": rel.get("passes_set_aside")}}
    if red is None:
        json.dump(out, open(a.out, "w"), indent=1)
        print(json.dumps(out, indent=1))
        return
    R = phc.reading(red)                       # E109's reader, on the scored reduction
    passes = R["passes"]
    per = json.load(open(red))["per_pass"]
    ratio = []
    for p in passes:
        uf, ui = R["U_per_edge_fp32_fj"]["per_pass"][passes.index(p)], R["U_per_edge_int8_fj"]["per_pass"][passes.index(p)]
        ratio.append(ui / uf if uf else None)
    N = R["S_m0_gap"]
    N = {"mean": N["mean"], "half": N["half"], "n": N["n"], "per_pass": N["per_pass"]}
    y1 = P["added_rules"]["Y1"]
    ys = {"Y1": {"N": N, "line_w": y1["line_w"], "predicted_w": y1["predicted_w"], "verdict": three(N, y1["line_w"])}}
    line = P["added_rules"]["Y2"]["line_pj"]
    eo = {g: sc["quantities"][g]["e_op_pj"] for g in ("fp32", "int8")}
    if any(eo[g].get("hi") is None for g in eo):
        v2 = "NOT-SCORED"
    elif all(eo[g]["hi"] < line for g in eo):
        v2 = "PASS"
    elif any(eo[g]["lo"] >= line for g in eo):
        v2 = "FAIL"
    else:
        v2 = "INCONCLUSIVE"
    ys["Y2"] = {"e_op_pj": eo, "line_pj": line, "verdict": v2}
    rv = {k: sc["rules"].get(k, {}).get("verdict") for k in ("R0_answer", "R1_ops", "R2_lanes", "R3_per_time")}
    if rv["R0_answer"] == "PER-TIME" and rv["R1_ops"] == "FAIL" and rv["R2_lanes"] == "LANES-OPPOSE" and rv["R3_per_time"] == "PASS":
        z = "REPLICATES"
    elif ("PER-OP" in (rv["R0_answer"] or "")) or ("LANES" in (rv["R0_answer"] or "").replace("LANES-", "")) or rv["R1_ops"] == "PASS" \
            or rv["R2_lanes"] == "LANES-CARRY" or rv["R3_per_time"] == "FAIL":
        z = "CONTRADICTS"
    else:
        z = "PARTIAL"
    ys["Z"] = {"verdicts": rv, "verdict": z}
    out["added_rules"] = ys
    out["reported"] = {k: R[k] for k in ("S_zeros_fp32", "S_zeros_int8", "S_m0_fp32", "S_m0_int8", "S_m0_gap", "read_ceiling_fp32_pj", "read_ceiling_int8_pj",
                                         "extra_reads_at_fp32_ceiling_w", "U_fp32", "U_int8", "U_per_edge_fp32_fj", "U_per_edge_int8_fj",
                                         "U_per_clocked_fp32_fj", "U_per_clocked_int8_fj", "live_over_constant_w")}
    out["reported"]["U_per_edge_ratio_int8_over_fp32"] = ci(ratio)
    out["reported"]["bench_activity_per_s"] = R["bench_activity_per_s"]
    # each quantity beside E109's labelled three-pass value (aifoundry3) and that value x card 1's scale
    ref = P["e109_reference"]["quantities"]
    mine = {"G": sc["gap"]["G"], "G_lane": sc["gap"]["G_lane"], "G_op": sc["gap"]["G_op"], "G_rest": sc["gap"]["G_rest"],
            "U_fp32": sc["quantities"]["fp32"]["U"], "U_int8": sc["quantities"]["int8"]["U"], "e_op_fp32_pj": eo["fp32"], "e_op_int8_pj": eo["int8"],
            "r_B_fp32_pj": sc["quantities"]["fp32"]["r_B_pj"], "R7": sc["item15"]["R7"], "R8": sc["item15"]["R8"], "T_minus": sc["item15"]["T_minus"],
            "S_m0_gap": N, "S_m0_fp32": R["S_m0_fp32"], "S_m0_int8": R["S_m0_int8"], "U_per_edge_fp32_fj": R["U_per_edge_fp32_fj"],
            "U_per_edge_int8_fj": R["U_per_edge_int8_fj"], "read_ceiling_fp32_pj": R["read_ceiling_fp32_pj"],
            "read_ceiling_int8_pj": R["read_ceiling_int8_pj"], "live_over_constant_w": R["live_over_constant_w"]}
    s = P["e109_reference"]["card_scale"]
    tab = {}
    for k, c in mine.items():
        r = ref.get(k, {})
        rm, rh = r.get("mean"), r.get("half")
        mh = c.get("half")
        d = None if c.get("mean") is None or rm is None else c["mean"] - rm
        dh = None if mh is None or rh is None else math.sqrt(mh * mh + rh * rh)
        tab[k] = {"e124": {"mean": c.get("mean"), "half": mh, "n": c.get("n")}, "e109": {"mean": rm, "half": rh},
                  "e109_x_scale": None if rm is None else rm * s, "ratio_e124_over_e109": None if (rm in (None, 0) or c.get("mean") is None) else c["mean"] / rm,
                  "diff": d, "diff_half_combined": dh,
                  "intervals_overlap": None if dh is None else (abs(d) <= mh + rh)}
    out["beside_e109"] = tab
    out["passes"] = passes
    json.dump(out, open(a.out, "w"), indent=1)
    L = [f"E124 extras (extras_e124.py): the verdicts are carried by the {which} reduction, passes {', '.join(passes)}", "",
         f"Y1 the no-issue loop gap N = S(m0.int8.zeros) - S(m0.fp32.zeros): {f(N, 3, 'W')} (line {y1['line_w']} W, predicted {y1['predicted_w']:.3f}): {ys['Y1']['verdict']}",
         f"Y2 per-op price ceiling: e_op fp32 {f(eo['fp32'], 1, 'pJ')}, int8 {f(eo['int8'], 1, 'pJ')} (line {line:.1f} pJ): {v2}",
         f"Z  E109's answer on this card: {rv} -> {z}", "",
         "reported (posthoc_check_e109.reading on the scored reduction, no verdict):",
         f"  S over idle: zeros fp32 {f(R['S_zeros_fp32'])}, int8 {f(R['S_zeros_int8'])}; no-issue (m0) fp32 {f(R['S_m0_fp32'])}, int8 {f(R['S_m0_int8'])}",
         f"  per-read ceiling if all of m0's S were reads: fp32 {f(R['read_ceiling_fp32_pj'], 2, 'pJ')}, int8 {f(R['read_ceiling_int8_pj'], 2, 'pJ')}; int8's extra reads at fp32's ceiling {f(R['extra_reads_at_fp32_ceiling_w'])} W",
         f"  lanes U: fp32 {f(R['U_fp32'])}, int8 {f(R['U_int8'])}; per clock edge fp32 {f(R['U_per_edge_fp32_fj'], 3, 'fJ')}, int8 {f(R['U_per_edge_int8_fj'], 3, 'fJ')}, int8/fp32 paired {f(out['reported']['U_per_edge_ratio_int8_over_fp32'], 3)}",
         f"  per enabled bit: fp32 {f(R['U_per_clocked_fp32_fj'], 2, 'fJ')}, int8 {f(R['U_per_clocked_int8_fj'], 2, 'fJ')}",
         f"  item 15, a live -0 lane with random B over pi, transport out: {f(R['live_over_constant_w'])} W", "",
         "beside E109 (aifoundry3, three passes, post hoc; x0.970 card scale):"]
    for k, t in tab.items():
        L.append(f"  {k}: E124 {f(t['e124'])} | E109 {f(t['e109'])} | x scale {t['e109_x_scale'] if t['e109_x_scale'] is None else round(t['e109_x_scale'], 3)} | "
                 f"ratio {None if t['ratio_e124_over_e109'] is None else round(t['ratio_e124_over_e109'], 3)} | intervals overlap {t['intervals_overlap']}")
    if a.txt:
        open(a.txt, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
