#!/usr/bin/env python3
"""E96 (Q132): the FROZEN predictions E96 scores, for Q132(r)'s real2 tiles on aifoundry2 card 0 under the card's own
governor (65 W static TDP, 65 C threshold: read, never changed), and the numbers of the int8 arm, E87's three real int8
tiles against int8 full. No E96 data exists when this runs. Nothing here is a new model: every predicted clock is
Q132(r)'s, frozen in predictions-real2.json, and this script gathers, checks and tabulates; the arm's expected numbers
are E83's relation on E87's measured c, labelled as such.

    python3 predict_e96.py [--out predictions.json] > predictions.txt

THE INPUTS, each refused unless its sha256 is the one frozen here:
  * Q132(r) predictions-real2.json (commit 6ae4c3d5): per tile the switching term c on aifoundry2's basis, the burst and
    sustained clocks, the shares, limits and scoring intervals (b_aifoundry2_governor), the gate law's clock (c_gate_law),
    and claims.E96, the rules S1-S5, copied here verbatim.
  * Q132(r) real2.json: every tile's sha256.
  * Q130(n) predictions-real.json and real.json: the three int8 tiles of the arm.
  * E87's predictions.json (E64's B_f and s_f, E80's die line, E83's one-run uncertainties, E80's and E83's anchor cells).
  * E87's results.json: its anchor cells, part of each anchor's tie cell, and the arm's c and sustained readings.
  * kinds.json (Q130(s) revision 2): the anchor tiles.

THE CHECK: E83's relation (predict_e83.Rel, imported unchanged) applied to each tile's frozen c must reproduce the frozen burst
and sustained points to 0.05 MHz, or the script refuses.

THE POWER TABLE of the arm's rule: a seeded simulation (no data) of the registered partition, at a few values of one run's sigma
and of the true difference, with the 800 MHz clamp, for three and four rounds.
"""
import argparse
import hashlib
import json
import math
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "e83"))
import predict_e83 as PE  # noqa: E402

R2P = "tools/claims-v3/kinds/real2/predictions-real2.json"
R2J = "tools/claims-v3/kinds/real2/real2.json"
R1P = "tools/claims-v3/kinds/real/predictions-real.json"
R1J = "tools/claims-v3/kinds/real/real.json"
E87P = "tools/claims-v3/kspeed/e87/predictions.json"
E87R = "docs/reports/data/2026-10-31-e87-real-tensors-speed/results.json"
KINDS = "tools/claims-v3/kinds/kinds.json"
FROZEN_SHA = {
    R2P: "0957e0c295990ac95cded56430697fb0683c9cf451d90f6943c8ff8d6a0b021a",
    R2J: "6e259fd2e9edaa3d4fdeb663461ec39389ec8c24436c114719536a51d26c8715",
    R1P: "bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941",
    R1J: "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0",
    E87P: "025f4e15950e75c3b21ea405ea15f04487cd1e56db4a7b308b19aa2ab7565ae8",
    E87R: "274750b3a21011cb44af52c0535ba891bf76c489038e78b32d9acbf04c631f04",
    KINDS: "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
}
ANCHORS = [("fp32", "randn"), ("fp32", "zeros"), ("fp16", "randn"), ("fp16", "zeros"), ("int8", "full"), ("int8", "zeros")]
ARM = ["int8/l0_mlp_up", "int8/l6_mlp_down", "int8/l6_attn_qk"]
ARM_REF = "int8/full"
REF_KIND = {"fp32": "fp32/randn", "fp16": "fp16/randn", "int8": "int8/full"}
K_LINE = 0.4573        # E98's frozen slope for the 76 s line, die - k W (the desk's pooled within-session slope)
LINE_KINDS = ["fp16/zeros", "int8/zeros", "int8/full", "fp32/randn"]   # the kinds E96's anchors share with E98's gated line
BARS = {"S1_pass_share": 0.8, "S1_fail_share": 0.6, "S2_pass_mhz": 40.0, "S2_fail_mhz": 15.0, "S2b_pass_mhz": 50.0,
        "S2b_fail_mhz": 15.0, "S3_mhz": 15.0, "S4_pass_share": 0.8, "S4_fail_share": 0.6, "S5_pass_rms_mhz": 15.0,
        "S5_fail_rms_mhz": 25.0, "T_mhz": 25.0, "I1_bar_mhz": 15.0}
MINS = {"S1_burst": 20, "S1_sus": 7, "S4": 7, "S5_burst": 20, "S5_sus": 7, "T_rows": 9, "I_rounds": 3}
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def sha(path):
    return hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()


def rnd(x, n=1):
    return None if x is None else round(x, n)


def partition(lo, hi, bar):
    """E96-I1's partition of an interval against 0 and +-bar."""
    if lo > bar or hi < -bar:
        return "DIFFERENT_BEYOND_BAR"
    holds0 = lo <= 0 <= hi
    inside = -bar <= lo and hi <= bar
    if holds0:
        return "SAME_WITHIN_BAR" if inside else "INCONCLUSIVE"
    return "DIFFERENT_SMALL" if inside else "DIFFERENT"


def power_table(seed=96, draws=8000):
    """How often each verdict comes up: full ~ min(800, N(mu, s)), each real tile ~ min(800, N(mu + delta, s)), independent, paired by round."""
    rng = random.Random(seed)
    out = []
    for n in (3, 4):
        for sigma in (5.6, 9.2, 15.6):
            for delta in (0.0, 12.0, 21.0):
                c = {}
                hw = []
                for _ in range(draws):
                    ds = []
                    for _r in range(n):
                        f = min(800.0, rng.gauss(785.0, sigma))
                        rs = [min(800.0, rng.gauss(785.0 + delta, sigma)) for _t in range(3)]
                        ds.append(sum(rs) / 3.0 - f)
                    m = sum(ds) / n
                    h = T975[n - 1] * st.stdev(ds) / math.sqrt(n)
                    hw.append(h)
                    v = partition(m - h, m + h, BARS["I1_bar_mhz"])
                    c[v] = c.get(v, 0) + 1
                out.append({"rounds": n, "sigma_mhz": sigma, "true_delta_mhz": delta, "median_halfwidth_mhz": round(st.median(hw), 1),
                            "share": {k: round(v / draws, 3) for k, v in sorted(c.items())}})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "predictions.json"))
    a = ap.parse_args()
    for p, want in FROZEN_SHA.items():
        got = sha(p)
        if got != want:
            raise SystemExit(f"refused: {p} sha256 {got}, frozen {want}")
    r2 = json.load(open(os.path.join(ROOT, R2P)))
    r2j = json.load(open(os.path.join(ROOT, R2J)))
    r1 = json.load(open(os.path.join(ROOT, R1P)))
    r1j = json.load(open(os.path.join(ROOT, R1J)))
    p87 = json.load(open(os.path.join(ROOT, E87P)))
    r87 = json.load(open(os.path.join(ROOT, E87R)))
    K = json.load(open(os.path.join(ROOT, KINDS)))["kinds"]
    proto = json.load(open(os.path.join(HERE, "protocol.json")))
    C = p87["constants"]
    B = {int(k): v for k, v in C["B_registered_w"].items()}
    rel = PE.Rel(B)
    R = r2["relation_e83"]
    Wb, sb, Ws, ss = R["burst"]["W_star_w"], R["burst"]["sigma_w"], R["sustained"]["W_star_w"], R["sustained"]["sigma_w"]
    if (Wb, sb, Ws, ss) != (p87["relation"]["burst"]["W_star_w"], p87["relation"]["burst"]["sigma_w"],
                            p87["relation"]["sustained"]["W_star_w"], p87["relation"]["sustained"]["sigma_w"]):
        raise SystemExit("refused: Q132(r)'s relation is not E87's")
    sus_core = list(proto["sustained_first_kept"])
    sus_cut = list(proto["sustained_first_cut"])
    if sus_core + sus_cut != r2["e96_suggested"]["sustained_first"]:
        raise SystemExit("refused: the sustained list is not sustained_first cut from its tail")

    tiles = {}
    for k, e in r2["tiles"].items():
        if e["tier"] != 1:
            continue
        t, n = k.split("/")
        b = e["b_aifoundry2_governor"]
        rj = r2j["tiles"][t][n]
        if rj["sha256"] != e["tile_sha256"]:
            raise SystemExit(f"refused: {k} sha256 differs between real2.json and predictions-real2.json")
        chk_b, sh_b = rel.f(b["c_w"], Wb, sb)
        chk_s, sh_s = rel.f(b["c_w"], Ws, ss)
        if abs(chk_b - b["burst_mhz"]) > 0.05 or abs(chk_s - b["sus_mhz"]) > 0.05:
            raise SystemExit(f"refused: E83's relation on {k}'s c gives {chk_b:.2f} / {chk_s:.2f} MHz, frozen {b['burst_mhz']} / {b['sus_mhz']}")
        A = e["a_aifoundry3_600mhz"]
        G = e.get("c_gate_law")
        tiles[k] = {
            "type": t, "name": n, "role": "real2", "tile": e["tile"], "tile_sha256": e["tile_sha256"], "group": e["group"],
            "tier": e["tier"], "gated_lane_frac": e["gated_lane_frac"], "bus_bits_per_op": e["bus_bits_per_op"],
            "a_zero_elem_frac": e.get("a_zero_elem_frac"), "in_sustained": k in sus_core,
            "frozen": {kk: b[kk] for kk in ("c_w", "burst_mhz", "burst_share800", "burst_limit", "burst_rate",
                                            "burst_scoring_interval_mhz", "burst_D_propagated_range_mhz", "sus_mhz", "sus_share800",
                                            "sus_limit", "sus_rate", "sus_scoring_interval_mhz", "sus_D_propagated_range_mhz",
                                            "rate_unit")},
            "D_w": A["D_w"], "D_scoring_interval_w": A["scoring_interval_w"], "ratio_to_ref_measured_e78": A["ratio_to_ref_measured_e78"],
            "ref_kind": REF_KIND[t],
            "gate_law": ({"g": G["g"], "D_w": G["D_w"], "c_w": round(R["c_zeros_w"][t] + G["D_w"] / R["xfer"], 3), "burst_mhz": G["burst_mhz"],
                          "sus_mhz": G["sus_mhz"]} if G else None),
            "check_relation_on_frozen_c": {"burst_mhz": rnd(chk_b, 2), "burst_share800": rnd(sh_b, 3), "sus_mhz": rnd(chk_s, 2),
                                           "sus_share800": rnd(sh_s, 3)},
            "c_dry_w": b["c_w"],
        }
    if len(tiles) != 25:
        raise SystemExit(f"refused: {len(tiles)} tier-1 tiles, expected 25")
    for k in sus_core:
        if k not in tiles:
            raise SystemExit(f"refused: {k} of the sustained list is not tier 1")
    for rule in ("S2_gate_buys_speed", "S2b_gate_buys_sustained_clock"):
        for k in r2["claims"]["E96"][rule]["tiles"]:
            if k not in sus_core:
                raise SystemExit(f"refused: {k} of {rule} does not run sustained")

    # -- the arm: E87's three real int8 tiles against int8 full
    arm = {}
    full87 = r87["cells"][ARM_REF]
    for k in ARM:
        P, c = p87["tiles"][k], r87["cells"][k]
        n = k.split("/")[1]
        if r1["tiles"][k]["tile_sha256"] != P["tile_sha256"] or r1j["tiles"]["int8"][n]["sha256"] != P["tile_sha256"]:
            raise SystemExit(f"refused: {k} sha256 differs between Q130(n)'s files and E87's")
        arm[k] = {"type": "int8", "name": n, "role": "arm", "tile": P["tile"], "tile_sha256": P["tile_sha256"], "c_dry_w": P["c_dry_w"],
                  "q130n_frozen_sus_mhz": P["frozen"]["sus_mhz"], "e87": {x: c[x] for x in ("c_w", "burst_mhz", "sus_mhz", "sus_w", "sus_die", "sus_limit")},
                  "rel_on_e87_c_sus_mhz": rnd(rel.f(c["c_w"], Ws, ss)[0]), "rel_on_e87_c_sus_share800": rnd(rel.f(c["c_w"], Ws, ss)[1], 3)}
    wadj87 = r87["posthoc"]["a_adj_e87"]["W_star_adj_w"]
    rel_full = rel.f(full87["c_w"], Ws, ss)[0]
    rel_real = st.mean([rel.f(arm[k]["e87"]["c_w"], Ws, ss)[0] for k in ARM])
    rel_full_adj = rel.f(full87["c_w"], wadj87, ss)[0]
    rel_real_adj = st.mean([rel.f(arm[k]["e87"]["c_w"], wadj87, ss)[0] for k in ARM])
    s800 = C["s_f"]["800"]
    dc = st.mean([arm[k]["e87"]["c_w"] for k in ARM]) - full87["c_w"]
    full_runs_e80_e83_e87 = [796.7, 790.0, 786.5, full87["sus_mhz"]]   # E87 predictions anchors int8/full e80, e83; E87 results cells int8/full
    arm_block = {
        "ref": ARM_REF, "tiles": arm, "rounds_planned": 4, "min_rounds": MINS["I_rounds"],
        "bar_mhz": BARS["I1_bar_mhz"],
        "bar_why": "E87-S2's and claims.E96.S3's bar: about 2% of 800 MHz, and smaller than E87's single-run +21 MHz, the thing at issue",
        "e87_full": {x: full87[x] for x in ("c_w", "burst_mhz", "sus_mhz", "sus_w", "sus_die", "sus_limit")},
        "expected": {
            "clock_difference_relation_mhz": rnd(rel_real - rel_full), "clock_relation_real_mhz": rnd(rel_real), "clock_relation_full_mhz": rnd(rel_full),
            "clock_difference_relation_at_e87_w_star_mhz": rnd(rel_real_adj - rel_full_adj), "w_star_e87_w": wadj87,
            "board_w_difference_at_fixed_800_w": rnd(s800 * dc, 2), "die_difference_at_fixed_800_c": rnd(s800 * dc * K_LINE, 2),
            "how": "E83's relation on E87's measured c (the switching term measured in E87's bursts); s_800 x the mean c difference; x E98's 0.4573 C/W. "
                   "Labelled expectations, not a rule: a colder room moves the whole int8 row toward the cap, and the clock difference toward 0",
        },
        "one_run_sigma_mhz": {"clamp": 5.6, "slope": 15.6, "source": "E83 corrections-check C3",
                              "int8_full_across_sessions": round(st.stdev(full_runs_e80_e83_e87), 1), "int8_full_runs": full_runs_e80_e83_e87},
        "power": power_table(),
    }

    # -- the anchors, tied to the mean of the earlier sessions' cells: single sustained runs land either side of the trip whatever the
    # data (E87's correction C3), so one session's single-run cell, E87's 774.7 for int8 full, is no reference to hold a session to
    anchors = {}
    for t, n in ANCHORS:
        k = f"{t}/{n}"
        P, c = p87["anchors"][k], r87["cells"][k]
        if P["tile_sha256"] != K[t][n]["sha256"]:
            raise SystemExit(f"refused: {k} sha256 differs between kinds.json and E87's predictions")
        e80 = P["e80"] or {}
        bs = [x for x in (e80.get("e80_burst_mhz"), P["e83"]["burst_mhz"], c["burst_mhz"]) if x is not None]
        ss_ = [x for x in (e80.get("e80_sus_mhz"), P["e83"]["sus_mhz"], c["sus_mhz"]) if x is not None]
        anchors[k] = {"type": t, "kind": n, "role": "anchor", "tile": P["tile"], "tile_sha256": P["tile_sha256"],
                      "tie_to": "the mean of the earlier sessions' cells (E80 where it ran, E83, E87)", "tie_burst_mhz": rnd(st.mean(bs)), "tie_sus_mhz": rnd(st.mean(ss_)),
                      "e87_burst_mhz": c["burst_mhz"], "e87_sus_mhz": c["sus_mhz"], "e87_c_w": c["c_w"],
                      "e87_sus_w": c["sus_w"], "e87_sus_die": c["sus_die"], "e87_limit": c["sus_limit"], "e80": P["e80"], "e83": P["e83"],
                      "c_dry_w": c["c_w"]}

    # -- the line of E87's session at E98's k, over the kinds E96 shares with E98's gated line, so a reader can set E96's beside it
    line87 = []
    for k in LINE_KINDS:
        xs = [m["sus_die_mean"] - K_LINE * m["sus_w_mean"] for m in r87["runs"] if m["block"] == "SUS" and m.get("kind") == k]
        line87.append(st.mean(xs))
    out = {
        "experiment": "E96", "request": "Q132", "card": "aifoundry2", "date": "2026-11-01",
        "what": "FROZEN before E96's first launch: Q132(r)'s burst and sustained clocks for the 25 tier-1 real2 tiles (E83's relation on Q132(r)'s predicted power), "
                "claims.E96 verbatim, the anchors' tie cells, and the int8 arm's rule and labelled expectations. No E96 data existed when this was written.",
        "inputs_sha256": FROZEN_SHA,
        "inputs_commits": {R2P: "6ae4c3d5", R1P: "7d5b99af", E87P: "7f84f454"},
        "constants": dict(C, c_zeros_w_real2=R["c_zeros_w"], xfer_real2=R["xfer"], k_line_e98=K_LINE),
        "relation": {"source": R2P + " relation_e83", "burst": {"W_star_w": Wb, "sigma_w": sb}, "sustained": {"W_star_w": Ws, "sigma_w": ss},
                     "random_kind_from_relation_mhz": R["random_kind_from_relation_mhz"], "relation_rms_mhz": R["relation_rms_mhz"]},
        "claims_e96": r2["claims"]["E96"], "claims_conventions": r2["claims"]["conventions"], "e96_suggested": r2["e96_suggested"],
        "bars": BARS, "minimum_population": MINS, "t975": T975, "uncertainty_e83": p87["uncertainty_e83"],
        "sus_core": sus_core, "sus_cut": sus_cut,
        "line": {"k_c_per_w": K_LINE, "kinds": LINE_KINDS, "e87_mean_c": round(st.mean(line87), 3),
                 "e87_die_line": r87["posthoc"]["die_line_e87"], "e80_die_line": C["e80_die_line"]},
        "tiles": tiles, "arm": arm_block, "anchors": anchors,
    }
    json.dump(out, open(a.out, "w"), indent=1)

    print("E96 frozen predictions: Q132(r)'s points and scoring intervals (predictions-real2.json sha256 " + FROZEN_SHA[R2P][:12] + "...)")
    print("%-34s %-2s %5s %7s %7s %16s %-7s %7s %16s %-8s %6s" % ("tile", "gp", "gate", "c W", "burst", "scoring", "b lim", "sus", "scoring", "s lim", "s run"))
    for k, e in tiles.items():
        f = e["frozen"]
        print("%-34s %-2s %5.3f %7.3f %7.1f %16s %-7s %7.1f %16s %-8s %6s" % (
            k, e["group"], e["gated_lane_frac"], f["c_w"], f["burst_mhz"], f["burst_scoring_interval_mhz"], f["burst_limit"], f["sus_mhz"],
            f["sus_scoring_interval_mhz"], f["sus_limit"], "yes" if e["in_sustained"] else "no"))
    print()
    print("sustained_first kept:", sus_core)
    print("sustained_first cut, burst only:", sus_cut)
    print()
    print("the arm: E87's three real int8 tiles against int8 full; bar +-%g MHz; at least %d whole rounds" % (BARS["I1_bar_mhz"], MINS["I_rounds"]))
    for k, e in arm.items():
        print(f"  {k:20s} E87 c {e['e87']['c_w']} sus {e['e87']['sus_mhz']} W {e['e87']['sus_w']} die {e['e87']['sus_die']} {e['e87']['sus_limit']}; relation on E87's c {e['rel_on_e87_c_sus_mhz']} (share {e['rel_on_e87_c_sus_share800']})")
    print(f"  {ARM_REF:20s} E87 c {full87['c_w']} sus {full87['sus_mhz']} W {full87['sus_w']} die {full87['sus_die']} {full87['sus_limit']}; relation on E87's c {rnd(rel_full)}")
    print("  expected:", json.dumps({k: v for k, v in arm_block["expected"].items() if k != "how"}))
    print("  one run's sigma:", json.dumps(arm_block["one_run_sigma_mhz"]))
    print()
    print("the arm's rule, how often each verdict comes up (simulation, seed 96; a full run ~ N(785, s) clamped at 800, a real tile the same + delta)")
    for row in arm_block["power"]:
        print(f"  rounds {row['rounds']} sigma {row['sigma_mhz']:5.1f} true delta {row['true_delta_mhz']:5.1f}: median half-width {row['median_halfwidth_mhz']:5.1f} MHz {json.dumps(row['share'])}")
    print()
    print("anchors (E96-T): the tie cell, the mean of the earlier sessions' cells; each session beside it")
    for k, e in anchors.items():
        print(f"  {k:12s} tie burst {e['tie_burst_mhz']} sustained {e['tie_sus_mhz']} | E87 {e['e87_burst_mhz']} {e['e87_sus_mhz']} | E80 {e['e80'].get('e80_burst_mhz') if e['e80'] else None} {e['e80'].get('e80_sus_mhz') if e['e80'] else None} | E83 {e['e83']['burst_mhz']} {e['e83']['sus_mhz']}")
    print()
    print("the line die - %g W, E87's session, kinds %s: %.3f C" % (K_LINE, LINE_KINDS, st.mean(line87)))
    print("bars", json.dumps(BARS))
    print("populations", json.dumps(MINS))
    print("relation", json.dumps(out["relation"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
