#!/usr/bin/env python3
"""E80 (Q130): the FROZEN predictions -- each kind's burst and sustained clock on aifoundry2 card 0, under the card's
own governor, from Q130(c)'s predicted powers through E64's registered governor (surface_hpl.py) and E64-T1
(surface_hpl_t.py). No E80 data exists when this runs; nothing here is a measurement.

    python3 predict_kspeed.py [--out predictions.json] > predictions.txt

THE INPUTS, each refused unless its sha256 is the one the brief froze:
  * Q130(c) predictions.json (commit 2bbe03dd, sha256 c5a66cb6...): per kind the switching W over the type's own
    zero-data level on aifoundry3 at 600 MHz / 521.8 mV, its 95% interval, and `c_w_a2_600mhz` -- the model's own
    conversion back to aifoundry2 (model.py rules 7 and 8):  c = c_E64(type, zeros) + W / 1.01865,
    1.01865 = (0.5218 / 0.517)^2. That c is the switching term at 600 MHz and 517 mV in E64's power curve
    P_f = B_f + c * s_f, s_f = (V_f / 0.517)^2 * f / 600, which carries it to 700 and 800 MHz (V^2 f).
  * Q130(c) amendment-a1.json (commit 320f3fdd, sha256 6ffc701b...): only for the labelled int8 U arm (E79's
    measured constant-to-zeros step, 1.834 W, against the frozen U_int8 0.571 W).
  * kinds.json (Q130(s) revision 2, commit 7d9c0d9e): each tile's file, sha256, tier and gated fraction.
  * E64's results.json and figures.json (docs/reports/data/2026-10-23-e64-horace-power-limit): the registered B_f
    and governor (tau 1.3 s, pass 0.24 s), and E64-T1's own build on E64's runs (B_f under E66's leakage law,
    governor, die line 41.88 + 0.4696 C/W, tau_th 14 s) -- exactly the call Q130(c) made.

THE PREDICTIONS, per kind (the protocol's own windows, so a prediction and its measurement score the same span):
  * burst, PRIMARY: E64's registered governor (surface_hpl.simulate) on P_f = B_f + c*s_f at the card's 65 W, mean
    clock from 1.5 s to 6.5 s -- the window E64 calibrated that governor on (its LAD runs: one 6 s process, work
    6.23-6.66 s, mean 6.5). No die state: the registered model refers every power to a 58 C die.
  * burst, SECONDARY: E64-T1 at gamma 3 over the same window, from the run's own launch die reading T0 (a
    boundary condition, E64-T1's own convention), tabulated for T0 = 40..60 C.
  * Q130(c)'s own frozen burst (mean clock 4-12 s) is reproduced here as a check and is what R7 scores.
  * sustained: E64-T1 at gamma 3 (arms gamma 2 and 0), the E80 SUS shape: nine 8 s processes, the mean clock over
    the last 40 s of the work (E64's SUS work 75.2-77.3 s, mean 76.2: window 36.2-76.2 s), from T0 = 40..60 C.
    Q130(c)'s own frozen sustained (40-80 s from 58 C) is reproduced as a check and is what R8 scores.
  * the limit, three-way: `none` when the sustained simulation spends >= 90% of the window at 800 MHz; else
    `thermal` when its mean die is >= the trip - 0.5 C (Q130(c)'s own criterion); else `power`.
  * the rate: the kernel's work per cycle (546 / 546 / 318 cycles for 8,192 / 16,384 / 32,768 operations per op,
    1,024 minions) at the predicted clock, in TFLOPS (fp32, fp16) or TOPS (int8).
"""
import argparse
import hashlib
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "hpl"))
import surface_hpl as SH  # noqa: E402
import surface_hpl_t as ST  # noqa: E402

Q130C_DIR = "docs/reports/data/2026-10-31-q130-kinds-model"
E64_DIR = "docs/reports/data/2026-10-23-e64-horace-power-limit"
KINDS_DIR = "tools/claims-v3/kinds"
FROZEN_SHA = {
    f"{Q130C_DIR}/predictions.json": "c5a66cb6d5f07a35d783d7db4be0f94a69482cf123defd2eccfda04fb6320a2c",
    f"{Q130C_DIR}/amendment-a1.json": "6ffc701b07d41f7ffbde9958bf44a03081cc82f784ff17202ebafbdc442c6d54",
    f"{KINDS_DIR}/kinds.json": "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
    f"{E64_DIR}/results.json": "f6bdb19f67fd4656e3c876c66ec0c7092a5f4e411d73480494a4cb985f434b76",
    f"{E64_DIR}/figures.json": "d430bfabd8f142d8fbb29b6f3f4ede71ff909d491b4de06526826d415828f9cb",
}
XFER = (0.5218 / 0.517) ** 2
PTS = (600, 700, 800)
TDP_W = 65.0
TRIP_C = 66.0                 # E64's R3 reading; Q130(c)'s declared trip
GAMMA = 3.0                   # Q130(c)'s declared voltage exponent (E64-T1's best out-of-sample sustained rms)
GAMMA_ARMS = (2.0, 0.0)
BURST_WIN = (1.5, 6.5)        # E64's governor calibration window on its 6 s LAD runs
SUS_WORK_S = 76.2             # E64's SUS runs: nine 8 s processes, work 75.2-77.3 s
SUS_WIN = (SUS_WORK_S - 40.0, SUS_WORK_S)
T0_GRID = list(range(40, 61))
LIMIT_NONE_SHARE = 0.9
U_INT8_FROZEN, U_INT8_E79 = 0.571, 1.834

# the E80 cells (the brief's list: fp16 7, int8 6, fp32 5)
KINDS = {"fp16": ["zeros", "ones", "randn", "sparse50", "smallint", "fp8grid", "nn_like"],
         "int8": ["zeros", "neg_ones", "full", "smallint", "gauss_q", "sparse50"],
         "fp32": ["randn", "bf16trunc", "sparse90", "smallint", "nn_like"]}
# E64's own measurements of the same cells on the same card (23 Oct 2026), for the anchor rule
E64_ANCHORS = {
    "burst": {"fp32/randn": {"runs": [706.0, 713.5], "source": f"{E64_DIR}/surface.txt (fp32-randn-1024 meas)"}},
    "sustained": {"fp32/randn": 600.0, "fp16/zeros": 794.4, "fp16/ones": 737.1, "fp16/randn": 600.5,
                  "int8/zeros": 800.0, "int8/full": 763.2},
    "sustained_source": f"{E64_DIR}/README.md, Sustained (SUS) table, MHz column (int8 `full` = E64's int8 randn)",
}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rate_t(typ, mhz):
    return SH.rate_t(typ, mhz)


def limit_of(sim):
    if sim is None:
        return None
    if sim["share"][800] >= LIMIT_NONE_SHARE:
        return "none"
    return "thermal" if sim["die_c"] >= TRIP_C - 0.5 else "power"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "predictions.json"))
    a = ap.parse_args()
    shas = {}
    for p, want in FROZEN_SHA.items():
        got = sha(os.path.join(ROOT, p))
        if got != want:
            sys.exit(f"refused: {p} sha256 {got} is not the frozen {want}")
        shas[p] = got
    P = json.load(open(os.path.join(ROOT, Q130C_DIR, "predictions.json")))
    A1 = json.load(open(os.path.join(ROOT, Q130C_DIR, "amendment-a1.json")))
    K = json.load(open(os.path.join(ROOT, KINDS_DIR, "kinds.json")))
    E64R = json.load(open(os.path.join(ROOT, E64_DIR, "results.json")))
    E64F = json.load(open(os.path.join(ROOT, E64_DIR, "figures.json")))
    B = {int(k): v for k, v in E64F["fit"]["B"].items()}
    S = {f: SH.S[f] for f in PTS}
    gov = E64F["governor"]
    assert (gov["tau_s"], gov["pass_s"]) == (1.3, 0.24), gov
    u_e79 = A1["score_u_post_data"]["int8"]["e79_const_minus_zeros_w"]
    u_frz = A1["score_u_post_data"]["int8"]["model_u_w"]
    assert abs(u_e79 - U_INT8_E79) < 1e-9 and abs(u_frz - U_INT8_FROZEN) < 1e-9

    # E64-T1's build on E64's own runs, as Q130(c) made it (model.py section 5), at the declared gamma and the arms
    t1 = {}
    for g in (GAMMA,) + GAMMA_ARMS:
        f = ST.build(E64R["runs"], g)
        t1[g] = {"B": f["B"], "governor": f["governor"], "die_line": f["die_line"], "tau_th": f["tau_th"]}

    def t1_sim(c, g, T0, win):
        f = t1[g]
        return ST.simulate(ST.p_maker(f["B"], c, g), TDP_W, f["governor"]["tau_s"], f["governor"]["pass_s"],
                           t_end=win[1], t_from=win[0], T0=float(T0), therm=f["die_line"],
                           tau_th=f["tau_th"]["tau_th_s"], trip=TRIP_C)

    def pack(sim):
        return None if sim is None else {"mhz": round(sim["mhz"], 1), "die_c": round(sim["die_c"], 2),
                                         "w": round(sim["w"], 2),
                                         "share": {str(k): round(v, 3) for k, v in sim["share"].items()},
                                         "limit": limit_of(sim)}

    out = {"experiment": "E80", "request": "Q130", "card": "aifoundry2 card 0", "date": "2026-10-31",
           "what": ("FROZEN predictions for E80, made before the #community-lab claim and before any E80 launch: "
                    "each kind's burst and sustained clock under the card's own governor (65 W static TDP, 65 C "
                    "threshold, read and never changed), from Q130(c)'s predicted powers"),
           "inputs_sha256": shas,
           "inputs_commits": {"q130c_freeze": "2bbe03dd", "q130c_amendment_a1": "320f3fdd",
                              "kinds_spec_revision_2": "7d9c0d9e"},
           "constants": {"xfer_a3_over_a2": XFER, "B_registered_w": B, "s_f": S, "governor_registered": gov,
                         "tdp_w": TDP_W, "trip_c": TRIP_C, "gamma": GAMMA, "gamma_arms": list(GAMMA_ARMS),
                         "burst_window_s": BURST_WIN, "sus_work_s": SUS_WORK_S, "sus_window_s": SUS_WIN,
                         "t0_grid_c": T0_GRID, "limit_none_share_800": LIMIT_NONE_SHARE,
                         "u_int8_frozen_w": U_INT8_FROZEN, "u_int8_e79_w": U_INT8_E79},
           "t1_build": {str(g): v for g, v in t1.items()},
           "e64_anchors": E64_ANCHORS, "kinds": {}, "checks": {}}
    chk_burst, chk_sus, chk_c = [], [], []
    c0 = {t: P["predictions"][f"{t}/zeros"]["c_w_a2_600mhz"] for t in KINDS}
    for t, ks in KINDS.items():
        for k in ks:
            q = P["predictions"][f"{t}/{k}"]
            rec = K["kinds"][t][k]
            tile = os.path.join(KINDS_DIR, rec["file"])
            tsha = sha(os.path.join(ROOT, tile))
            if tsha != rec["sha256"] or tsha != q["tile_sha256"]:
                sys.exit(f"refused: tile {tile} sha256 {tsha} disagrees with kinds.json / Q130(c)")
            W = q["switching_w_600mhz_a3"]
            c = q["c_w_a2_600mhz"]
            c_re = c0[t] + W / XFER
            chk_c.append(abs(c - c_re))
            lo, hi = q["switching_w_ci95"]
            c_lo, c_hi = c0[t] + lo / XFER, c0[t] + hi / XFER
            pw = {f: B[f] + c * S[f] for f in PTS}
            burst = SH.simulate(pw, TDP_W, gov["tau_s"], gov["pass_s"], t_end=BURST_WIN[1], t_from=BURST_WIN[0])
            b_lo = SH.simulate({f: B[f] + c_hi * S[f] for f in PTS}, TDP_W, gov["tau_s"], gov["pass_s"],
                               t_end=BURST_WIN[1], t_from=BURST_WIN[0])
            b_hi = SH.simulate({f: B[f] + c_lo * S[f] for f in PTS}, TDP_W, gov["tau_s"], gov["pass_s"],
                               t_end=BURST_WIN[1], t_from=BURST_WIN[0])
            b412 = SH.simulate(pw, TDP_W, gov["tau_s"], gov["pass_s"], t_end=12.0, t_from=4.0)
            chk_burst.append(round(b412, 0) == q["burst_mhz_65w"])
            q_sus = t1_sim(c, GAMMA, 58.0, (40.0, 80.0))
            chk_sus.append(round(q_sus["mhz"], 0) == q["sustained_mhz"])
            ent = {"type": t, "kind": k, "tier": rec["tier"], "rule": rec["rule"], "tile": tile,
                   "tile_sha256": tsha, "gated_lane_frac": rec["stats"]["gated_lane_frac"],
                   "bus_bits_per_op": rec["stats"]["bus_bits_per_op"],
                   "provisional": t == "int8",
                   "q130c": {"switching_w_600mhz_a3": W, "switching_w_ci95": [lo, hi],
                             "c_w_a2_600mhz": c, "burst_mhz_65w_4_12s": q["burst_mhz_65w"],
                             "burst_mhz_t1_1p5_6p5s_from58": q["burst_mhz_t1"],
                             "sustained_mhz_40_80s_from58": q["sustained_mhz"],
                             "sustained_die_c": q["sustained_die_c"], "sustained_board_w": q["sustained_board_w"],
                             "sustained_limit": q["sustained_limit"],
                             "calibration_status": q["calibration_status"]},
                   "c_pred_w": round(c, 3), "c_ci95_w": [round(c_lo, 3), round(c_hi, 3)],
                   "p_pred_w_at_58c": {str(f): round(pw[f], 2) for f in PTS},
                   "burst_reg_mhz": round(burst, 1),
                   "burst_reg_mhz_from_c_ci95": [round(b_lo, 1), round(b_hi, 1)],
                   "burst_reg_limit": "power" if burst < 799.0 else "none",
                   "burst_reg_rate": round(rate_t(t, burst), 3),
                   "burst_t1_by_t0": {}, "sus_t1_by_t0": {}, "sus_arms_by_t0": {}}
            for T0 in T0_GRID:
                ent["burst_t1_by_t0"][str(T0)] = pack(t1_sim(c, GAMMA, T0, BURST_WIN))
                s3 = t1_sim(c, GAMMA, T0, SUS_WIN)
                ent["sus_t1_by_t0"][str(T0)] = dict(pack(s3), rate=round(rate_t(t, s3["mhz"]), 3))
                ent["sus_arms_by_t0"][str(T0)] = {str(g): pack(t1_sim(c, g, T0, SUS_WIN)) for g in GAMMA_ARMS}
            # the spread a sustained prediction inherits from the power interval (at the 57 C gate)
            ent["sus_t1_57c_from_c_ci95"] = [pack(t1_sim(c_hi, GAMMA, 57, SUS_WIN))["mhz"],
                                             pack(t1_sim(c_lo, GAMMA, 57, SUS_WIN))["mhz"]]
            if t == "int8":
                # a LABELLED ARM, not the prediction: U_int8 at E79's measured 1.834 W instead of the frozen 0.571 W
                g = rec["stats"]["gated_lane_frac"]
                cu = c + (U_INT8_E79 - U_INT8_FROZEN) * (1.0 - g) / XFER
                ent["u_int8_arm"] = {"c_w": round(cu, 3),
                                     "burst_reg_mhz": round(SH.simulate({f: B[f] + cu * S[f] for f in PTS}, TDP_W,
                                                                        gov["tau_s"], gov["pass_s"],
                                                                        t_end=BURST_WIN[1],
                                                                        t_from=BURST_WIN[0]), 1),
                                     "sus_t1_by_t0": {str(T0): pack(t1_sim(cu, GAMMA, T0, SUS_WIN))
                                                      for T0 in T0_GRID}}
            out["kinds"][f"{t}/{k}"] = ent
    out["checks"] = {
        "c_reproduced_from_W_max_abs_w": round(max(chk_c), 4),
        "q130c_burst_4_12s_reproduced": f"{sum(chk_burst)}/{len(chk_burst)}",
        "q130c_sustained_40_80s_from58_reproduced": f"{sum(chk_sus)}/{len(chk_sus)}",
        "what": ("c = c_E64(type, zeros) + W/1.01865 recomputed from Q130(c)'s W; Q130(c)'s frozen burst (4-12 s) and "
                 "sustained (40-80 s from 58 C) re-simulated from its c with the same two models")}
    json.dump(out, open(a.out, "w"), indent=1)

    # the console table (predictions.txt)
    print("E80 frozen predictions (aifoundry2 card 0, 65 W / 65 C as found).  c: switching W at 600 MHz/517 mV "
          "(Q130(c), c_E64 zeros + W/1.01865)")
    print("checks:", json.dumps(out["checks"]))
    print("T1 build gamma 3: B %s governor %s die line %s tau_th %s" % (
        {k2: round(v, 3) for k2, v in t1[GAMMA]["B"].items()}, t1[GAMMA]["governor"],
        {k2: round(v, 4) for k2, v in t1[GAMMA]["die_line"].items() if isinstance(v, float)},
        t1[GAMMA]["tau_th"]))
    hdr = ("%-15s %4s %7s %-15s %7s %-13s %6s %8s %8s %8s %9s %8s %-8s %7s" %
           ("kind", "tier", "c W", "c ci95", "p800", "burst reg", "lim", "Q130c b", "T1 b@50", "sus@57",
            "sus ci95", "Q130c s", "limit", "rate s"))
    print(hdr)
    for key, e in out["kinds"].items():
        s57 = e["sus_t1_by_t0"]["57"]
        print("%-15s %4d %7.2f %-15s %7.1f %-13s %6s %8.0f %8.1f %8.1f %9s %8.0f %-8s %7.2f" % (
            key, e["tier"], e["c_pred_w"], "%.2f-%.2f" % tuple(e["c_ci95_w"]), float(e["p_pred_w_at_58c"]["800"]),
            "%.1f [%.0f-%.0f]" % (e["burst_reg_mhz"], *e["burst_reg_mhz_from_c_ci95"]), e["burst_reg_limit"],
            e["q130c"]["burst_mhz_65w_4_12s"], e["burst_t1_by_t0"]["50"]["mhz"], s57["mhz"],
            "%.0f-%.0f" % tuple(e["sus_t1_57c_from_c_ci95"]), e["q130c"]["sustained_mhz_40_80s_from58"],
            s57["limit"], s57["rate"]))
    print("sustained at other launch readings (gamma 3; die C in brackets), and the gamma 2 / 0 arms at 57 C:")
    for key, e in out["kinds"].items():
        row = "  ".join("%d:%.0f(%.1f)" % (T0, e["sus_t1_by_t0"][str(T0)]["mhz"], e["sus_t1_by_t0"][str(T0)]["die_c"])
                        for T0 in (46, 50, 54, 57))
        arms = e["sus_arms_by_t0"]["57"]
        extra = ""
        if "u_int8_arm" in e:
            extra = "  U_int8 arm: c %.2f burst %.0f sus@57 %.0f" % (
                e["u_int8_arm"]["c_w"], e["u_int8_arm"]["burst_reg_mhz"], e["u_int8_arm"]["sus_t1_by_t0"]["57"]["mhz"])
        print("  %-15s %s   g2 %.0f g0 %.0f%s" % (key, row, arms["2.0"]["mhz"], arms["0.0"]["mhz"], extra))
    return 0


if __name__ == "__main__":
    sys.exit(main())
