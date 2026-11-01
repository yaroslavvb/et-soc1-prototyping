#!/usr/bin/env python3
"""E87 (Q130): the FROZEN predictions E87 scores, for Q130(n)'s nine real GPT-2 tiles on aifoundry2 card 0 under the
card's own governor (65 W static TDP, 65 C threshold: read, never changed). No E87 data exists when this runs.
Nothing here is a new model: every predicted clock is Q130(n)'s, and this script only gathers, checks and tabulates.

    python3 predict_e87.py [--out predictions.json] > predictions.txt

THE INPUTS, each refused unless its sha256 is the one frozen here:
  * Q130(n) predictions-real.json (commit 7d5b99af, unchanged since): per real tile the switching term c on
    aifoundry2's basis (`b_aifoundry2_governor.c_w`, E83's conversion of the predicted D) and the burst and sustained
    clocks, shares and limits that E83's registered relation gives for it. These are the frozen points.
  * Q130(n) amendment-1.json (commit 99620cc2, written before any card ran a real tile): the scoring intervals
    (`b_aifoundry2_governor.burst_scoring_interval_mhz`, `sus_scoring_interval_mhz`), the D scoring intervals and the
    like-with-like reference (`like_with_like`). E87 scores against these, and reports the frozen D-propagated
    ranges (`burst_mhz_pi95`, `sus_mhz_pi95` of predictions-real.json) beside them.
  * Q130(n) real.json: every tile's sha256 (the runner checks the files against it).
  * E83's predictions.json (commit c253bd1c): E64's registered B_f and s_f, E83's relation (burst W* 66.15 W sigma
    2.75; sustained W* 49.75 W sigma 1.95), E80's die line and E80's anchor cells.
  * E83's results.json (commit 734e997f): E83's anchor cells (fp32 zeros's tie) and its same-day heat-path view
    (posthoc.a_adj.W_star_adj_w 49.724 W), used only for the labelled arm (a-adj E83).
  * kinds.json (Q130(s) revision 2): the anchor tiles.

THE CHECK: E83's relation (predict_e83.Rel, imported unchanged) applied to each tile's frozen c must reproduce
Q130(n)'s frozen burst and sustained points to 0.05 MHz, or the script refuses.
LABELLED ARM (tabulated, never a verdict): (a-adj E83), the sustained relation with W* moved to E83's same-day value
49.724 W (Q130(n)'s open issue: "E87 may add that as a labelled arm"). The in-session arm (a-adj E87), from E87's
own anchors, is defined in README.md and computed by reduce_e87.py.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "e83"))
import predict_e83 as PE  # noqa: E402

QN_PRED = "tools/claims-v3/kinds/real/predictions-real.json"
QN_AMEND = "tools/claims-v3/kinds/real/amendment-1.json"
QN_REAL = "tools/claims-v3/kinds/real/real.json"
E83P = "tools/claims-v3/kspeed/e83/predictions.json"
E83R = "docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json"
KINDS = "tools/claims-v3/kinds/kinds.json"
FROZEN_SHA = {
    QN_PRED: "bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941",
    QN_AMEND: "f32e8a9087a9cf3bf60f29ff623c1a375537b43696df0dca24972ba220bc0d9e",
    QN_REAL: "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0",
    E83P: "97f58c89344dc867b66e28c4ea9e969c4c610865700ea91221fed9c8f4f78cec",
    E83R: "3717f1767bdb76f536b7af8dbedf01865984638e649f892c2893e47d59676b3e",
    KINDS: "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
}
REAL = ["l0_mlp_up", "l6_mlp_down", "l6_attn_qk"]
TYPES = ["fp32", "fp16", "int8"]
# E80's anchors, repeated (the brief, as E83 named them): fp32 randn, fp16 randn, int8 full and one zeros per type.
# fp32 zeros was never run by E80; its tie is to E83's cell. The other five tie to E80's cells (E83's beside them).
ANCHORS = [("fp32", "randn", "E80"), ("fp32", "zeros", "E83"), ("fp16", "randn", "E80"), ("fp16", "zeros", "E80"),
           ("int8", "full", "E80"), ("int8", "zeros", "E80")]
REF_KIND = {"fp32": "fp32/randn", "fp16": "fp16/randn", "int8": "int8/full"}   # the like-with-like reference
ZERO_KIND = {t: f"{t}/zeros" for t in TYPES}
BARS = {"R1_rms_mhz": 25.0, "R2_right_of_9": 7, "R3_rms_mhz": 25.0, "R4_inside_of_9": 7, "R5_mhz": 25.0,
        "S1_rms_mhz": 15.0, "S2_mhz": 15.0, "S3_inside_of_9": 7,
        "S4_ratio_below": {"fp32": 1.0, "fp16": 1.0, "int8": 0.9}}
MINS = {"R1": 7, "R2": 7, "R3": 7, "R4": 7, "S1": 7, "S3": 7, "R5_rows": 9}
# E83's corrected uncertainties (docs/reports/data/2026-10-31-e83-kinds-speed-rest/corrections-check.txt C3, C6):
UNC = {"sus_one_run_sigma_mhz_slope": 15.6, "sus_one_run_sigma_mhz_clamp": 5.6, "sus_board_w_sigma": 0.82,
       "sus_die_c_sigma": 0.81, "burst_pass_random_sigma_mhz": 7.5, "burst_cell_random_sigma_mhz": 5.3,
       "slope_rule": "a sustained cell takes the slope sigma when it is thermal-held above 615 MHz, else the clamp",
       "source": "docs/reports/data/2026-10-31-e83-kinds-speed-rest/corrections-check.txt C3, C6"}


def sha(path):
    return hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()


def r(x, n=1):
    return None if x is None else round(x, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "predictions.json"))
    a = ap.parse_args()
    for p, want in FROZEN_SHA.items():
        got = sha(p)
        if got != want:
            raise SystemExit(f"refused: {p} sha256 {got}, frozen {want}")
    qn = json.load(open(os.path.join(ROOT, QN_PRED)))
    am = json.load(open(os.path.join(ROOT, QN_AMEND)))
    rj = json.load(open(os.path.join(ROOT, QN_REAL)))
    p83 = json.load(open(os.path.join(ROOT, E83P)))
    r83 = json.load(open(os.path.join(ROOT, E83R)))
    K = json.load(open(os.path.join(ROOT, KINDS)))["kinds"]
    C = p83["constants"]
    B = {int(k): v for k, v in C["B_registered_w"].items()}
    rel = PE.Rel(B)
    Wb, sb = p83["relation"]["burst"]["W_star_w"], p83["relation"]["burst"]["sigma_w"]
    Ws, ss = p83["relation"]["sustained"]["W_star_w"], p83["relation"]["sustained"]["sigma_w"]
    if (Wb, sb, Ws, ss) != (qn["relation_e83"]["burst"]["W_star_w"], qn["relation_e83"]["burst"]["sigma_w"],
                            qn["relation_e83"]["sustained"]["W_star_w"], qn["relation_e83"]["sustained"]["sigma_w"]):
        raise SystemExit("refused: Q130(n)'s relation is not E83's")
    w_adj83 = r83["posthoc"]["a_adj"]["W_star_adj_w"]
    czero = qn["relation_e83"]["c_zeros_w"]
    xfer = qn["relation_e83"]["xfer"]

    tiles = {}
    for t in TYPES:
        for n in REAL:
            k = f"{t}/{n}"
            P, A = qn["tiles"][k], am["tiles"][k]
            b, ab = P["b_aifoundry2_governor"], A["b_aifoundry2_governor"]
            if rj["tiles"][t][n]["sha256"] != P["tile_sha256"]:
                raise SystemExit(f"refused: {k} sha256 differs between real.json and predictions-real.json")
            chk_b, sh_b = rel.f(b["c_w"], Wb, sb)
            chk_s, sh_s = rel.f(b["c_w"], Ws, ss)
            if abs(chk_b - b["burst_mhz"]) > 0.05 or abs(chk_s - b["sus_mhz"]) > 0.05:
                raise SystemExit(f"refused: E83's relation on {k}'s c gives {chk_b:.2f} / {chk_s:.2f} MHz, "
                                 f"Q130(n) froze {b['burst_mhz']} / {b['sus_mhz']}")
            D = A["a_aifoundry3_600mhz"]
            L = A["like_with_like"]
            ref = L["ref_measured_w"]
            tiles[k] = {
                "type": t, "name": n, "role": "real", "tile": P["tile"], "tile_sha256": P["tile_sha256"],
                "gated_lane_frac": P["gated_lane_frac"], "bus_bits_per_op": P["bus_bits_per_op"],
                "frozen": {kk: b[kk] for kk in ("c_w", "c_pi95_w", "burst_mhz", "burst_mhz_pi95", "burst_share800",
                                                "burst_limit", "burst_rate", "sus_mhz", "sus_mhz_pi95",
                                                "sus_share800", "sus_limit", "sus_rate", "rate_unit")},
                "amended": {kk: ab[kk] for kk in ("burst_scoring_interval_mhz", "sus_scoring_interval_mhz",
                                                  "burst_D_propagated_range_amended_mhz",
                                                  "sus_D_propagated_range_amended_mhz")},
                "D_w": D["D_w"], "D_frozen_pi95_w": D["frozen_pi95_w"], "D_scoring_interval_w": D["scoring_interval_w"],
                "c_amended_interval_w": [round(czero[t] + D["scoring_interval_w"][0] / xfer, 3),
                                         round(czero[t] + D["scoring_interval_w"][1] / xfer, 3)],
                "like_with_like": {"ref_kind": REF_KIND[t], "ref_measured_D_w_e78": ref,
                                   "ratio_to_ref_measured": L["ratio_to_ref_measured"],
                                   "ratio_to_ref_model_fit": L["ratio_to_ref_model_fit"],
                                   "S3_ratio_interval": [round(D["scoring_interval_w"][0] / ref, 4),
                                                         round(D["scoring_interval_w"][1] / ref, 4)],
                                   "frozen_ratio_interval": [round(D["frozen_pi95_w"][0] / ref, 4),
                                                             round(D["frozen_pi95_w"][1] / ref, 4)]},
                "check_relation_on_frozen_c": {"burst_mhz": r(chk_b, 2), "burst_share800": r(sh_b, 3),
                                               "sus_mhz": r(chk_s, 2), "sus_share800": r(sh_s, 3)},
                "arm_a_adj_e83_sus_mhz": r(rel.f(b["c_w"], w_adj83, ss)[0]),
                "c_dry_w": b["c_w"],
            }

    anchors = {}
    for t, kname, tie in ANCHORS:
        k = f"{t}/{kname}"
        e80 = p83["anchors"].get(k)
        c83 = r83["cells"][k]
        e83 = {kk: c83.get(kk) for kk in ("burst_mhz", "burst_mhz_runs", "burst_mhz_without", "sus_mhz", "sus_mhz_runs",
                                          "c_w", "c_w_runs", "burst_rate", "sus_rate", "sus_w", "sus_die",
                                          "sus_limit", "burst_p800_w")}
        ref_b = e80["e80_burst_mhz"] if tie == "E80" else e83["burst_mhz"]
        ref_s = e80["e80_sus_mhz"] if tie == "E80" else e83["sus_mhz"]
        anchors[k] = {"type": t, "kind": kname, "role": "anchor", "tile": f"tools/claims-v3/kinds/{K[t][kname]['file']}",
                      "tile_sha256": K[t][kname]["sha256"], "tie_to": tie, "tie_burst_mhz": ref_b,
                      "tie_sus_mhz": ref_s, "e80": e80, "e83": e83, "c_dry_w": p83["kinds"][k]["c_pred_w"]}

    out = {
        "experiment": "E87", "request": "Q130", "card": "aifoundry2", "date": "2026-10-31",
        "what": "FROZEN before E87's claim and first launch: Q130(n)'s burst and sustained clocks for the nine real "
                "GPT-2 tiles (E83's relation on Q130(n)'s predicted power), Amendment 1's scoring intervals, E80's "
                "and E83's anchor cells, and the labelled arm (a-adj E83). No E87 data existed when this was written.",
        "inputs_sha256": FROZEN_SHA,
        "inputs_commits": {QN_PRED: "7d5b99af", QN_AMEND: "99620cc2", E83P: "c253bd1c", E83R: "734e997f"},
        "constants": dict(C, c_zeros_w_q130n=czero, xfer_q130n=xfer),
        "relation": {"source": E83P, "burst": {"W_star_w": Wb, "sigma_w": sb},
                     "sustained": {"W_star_w": Ws, "sigma_w": ss},
                     "a_adj_e83": {"W_star_sus_adj_w": w_adj83, "source": E83R + " posthoc.a_adj.W_star_adj_w"}},
        "bars": BARS, "minimum_population": MINS, "uncertainty_e83": UNC,
        "tiles": tiles, "anchors": anchors,
    }
    json.dump(out, open(a.out, "w"), indent=1)

    print("E87 frozen predictions (Q130(n)'s points; Amendment 1's scoring intervals; frozen D-propagated ranges)")
    print("%-18s %7s %16s %-6s %7s %16s %16s %-8s %6s | %7s %16s" % (
        "tile", "c W", "c amended", "burst", "MHz", "scoring", "frozen", "sus lim", "share", "sus MHz", "scoring"))
    for k, e in tiles.items():
        f_, am_ = e["frozen"], e["amended"]
        print("%-18s %7.3f %16s %-6s %7.1f %16s %16s %-8s %6.3f | %7.1f %16s  frozen %s  a-adj(E83) %s" % (
            k, f_["c_w"], e["c_amended_interval_w"], f_["burst_limit"], f_["burst_mhz"],
            am_["burst_scoring_interval_mhz"], f_["burst_mhz_pi95"], f_["sus_limit"], f_["sus_share800"],
            f_["sus_mhz"], am_["sus_scoring_interval_mhz"], f_["sus_mhz_pi95"], e["arm_a_adj_e83_sus_mhz"]))
    print()
    print("like with like (S3, S4): ratio of (c - c_zeros) to the same-session reference's")
    for k, e in tiles.items():
        L = e["like_with_like"]
        print(f"  {k:18s} ref {L['ref_kind']:10s} predicted {L['ratio_to_ref_measured']:.4f} (model-fit ref "
              f"{L['ratio_to_ref_model_fit']:.4f}); S3 interval {L['S3_ratio_interval']}; frozen {L['frozen_ratio_interval']}")
    print()
    print("anchors (R5): tie cell, E80 and E83 beside it")
    for k, e in anchors.items():
        print(f"  {k:12s} tie {e['tie_to']}: burst {e['tie_burst_mhz']} sustained {e['tie_sus_mhz']} | E83 burst "
              f"{e['e83']['burst_mhz']} sus {e['e83']['sus_mhz']} c {e['e83']['c_w']}")
    print()
    print("bars", json.dumps(BARS))
    print("relation", json.dumps(out["relation"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
