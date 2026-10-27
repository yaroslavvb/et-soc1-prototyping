#!/usr/bin/env python3
"""E64-T1's frozen predictions for E69's own cells, so E69's data scores two models, not one.

E69 (`tools/claims-v3/knob/`) pre-registered its cells from E64's REGISTERED model: a governor with a power
limb only, a power curve referred to 58 C with one constant leakage slope, and — for the sustained cells —
a hand-built duty-cycle rule whose level is anchored on each pattern's OWN E64 sustained mean. E69's README
states that circularity itself as its honest limitation.

This file freezes the same cells under **E64-T1** (`tools/claims-v3/hpl/surface_hpl_t.py`), which carries
E66's measured leakage law, a die-temperature state and a thermal limb. Two differences matter for scoring:

  * the BURST cells get the same inputs E69 uses (each pattern's own E64 cool-die powers) plus the
    temperature term, so the two predictions differ only by that term; and
  * the SUSTAINED cells are produced by the SAME simulation as the burst ones, from the cool-die ladder and
    the law. No pattern's sustained mean is used as an anchor, so T1's sustained control cells are a genuine
    out-of-sample check where E69's are partly self-fitting.

No E69 measurement enters any number here. Frozen and committed before E69's results landed.

    python3 predict_knob_t1.py --results <E64 results.json> --figures-t1 <figures-t1.json> \
            --out predictions-t1-e69.json
"""
import argparse
import hashlib
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "hpl"))
import surface_hpl_t as T  # noqa: E402

PTS = [600, 700, 800]
BAND = 25.0            # MHz: E69's own registered half-width, kept so the two models are scored alike
BURST_LAUNCH_C = 55.0  # E69's protocol: a burst starts from a cool die at or below 55 C
BURST_S = 6.0          # E69's burst length
SUS_S, SUS_FROM = 72.0, 32.0   # nine back-to-back 8 s launches; the mean over the last 40 s
EXIT_MARGIN_W = 2.0    # E69's safety filter, reproduced verbatim so the same cells are dropped

BURST = [(65, "fp32", "zeros"), (65, "fp32", "ones"), (65, "fp32", "a_ones_b_randn"), (65, "fp32", "randn"),
         (55, "fp32", "zeros"), (55, "fp32", "ones"), (55, "fp32", "a_ones_b_randn"), (55, "fp32", "randn"),
         (45, "fp32", "zeros"), (45, "fp32", "ones"), (45, "fp32", "a_ones_b_randn"),
         (35, "fp32", "zeros"), (35, "fp32", "ones")]
SUS = [(65, 65, "fp32", "ones"), (65, 65, "fp32", "randn"),
       (65, 70, "fp32", "ones"), (65, 70, "fp32", "randn"),
       (65, 62, "fp32", "ones"),
       (50, 65, "fp32", "ones")]


def lad_powers(runs, gamma):
    """{(type, values): ({f: raw W}, {f: referred W}, c)} from the cool-die LAD runs, as E69 reads them."""
    g = {}
    for m in runs:
        if m["block"] == "LAD" and m.get("minions") == 1024 and m.get("trace"):
            g.setdefault((m["type"], m["values"]), []).append(m)
    out = {}
    for k, ms in g.items():
        raw, ref = {}, {}
        for f in PTS:
            a = [T.powers(m, gamma, "law", ref=False)[0].get(f) for m in ms]
            b = [T.powers(m, gamma, "law", ref=True)[0].get(f) for m in ms]
            a = [x for x in a if x is not None]
            b = [x for x in b if x is not None]
            raw[f] = round(st.mean(a), 2) if a else None
            ref[f] = round(st.mean(b), 2) if b else None
        if all(raw[f] is not None for f in PTS):
            out[k] = (raw, ref)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--figures-t1", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gamma", default="0.0,2.0,3.0")
    a = ap.parse_args()
    runs = json.load(open(a.results))["runs"]
    F = json.load(open(a.figures_t1))
    sha = hashlib.sha256(open(a.results, "rb").read()).hexdigest()
    out = {"experiment": "E69 (scored against model E64-T1, not E69's registered model)", "request": "Q129",
           "card": "aifoundry2 card 0", "model_id": T.MODEL_ID, "frozen_before_e69_results": True,
           "source": {"e64_results_sha256": sha, "figures_t1": os.path.basename(a.figures_t1),
                      "leak_law": T.E66, "t_ref_c": T.T_REF, "t_trip_c": F["t_trip_c"],
                      "note": "no E69 measurement enters any number here"},
           "burst_launch_c": BURST_LAUNCH_C, "burst_s": BURST_S, "sus_s": SUS_S, "sus_from_s": SUS_FROM,
           "band_mhz": BAND, "variants": {}}
    for gs in a.gamma.split(","):
        g = float(gs)
        V = F["variants"][gs]
        gov, dl, tth = V["governor"], V["die_line"], V["tau_th"]["tau_th_s"]
        B = {int(k): v for k, v in V["B"].items()}
        lad = lad_powers(runs, g)
        ent = {"gamma": g, "governor": gov, "die_line": dl, "tau_th_s": tth,
               "burst": [], "sustained": [], "dropped": []}
        for tdp, t, v in BURST:
            got = lad.get((t, v))
            if not got:
                ent["dropped"].append({"cell": f"B-tdp{tdp}-{t}-{v}", "why": "no E64 power ladder"})
                continue
            raw, ref = got
            if raw[600] > 1.05 * tdp - EXIT_MARGIN_W:
                ent["dropped"].append({"cell": f"B-tdp{tdp}-{t}-{v}", "why": "power-loop exit unreachable",
                                       "p600_w": raw[600]})
                continue
            sim = T.simulate(T.p_from_measured(raw, g, BURST_LAUNCH_C), float(tdp), gov["tau_s"],
                             gov["pass_s"], t_end=BURST_S, T0=BURST_LAUNCH_C, therm=dl, tau_th=tth,
                             trip=F["t_trip_c"])
            mhz = round(sim["mhz"], 1)
            lo, hi = ((775.0, 800.0) if mhz >= 799 else
                      ((600.0, 625.0) if mhz <= 601 else (mhz - BAND, mhz + BAND)))
            ent["burst"].append({"cell": f"B-tdp{tdp}-{t}-{v}", "block": "BURST", "tdp_w": tdp,
                                 "threshold_c": 65, "type": t, "values": v, "control": tdp == 65,
                                 "p_w_raw": raw, "p_w_referred_58c": ref,
                                 "pred_mhz_mean": mhz, "band_mhz": [round(lo, 1), round(hi, 1)],
                                 "pred_die_c": round(sim["die_c"], 2), "pred_board_w": round(sim["w"], 2),
                                 "pred_tflops": round(T.rate_t(t, sim["mhz"]), 2),
                                 "pred_throttles": mhz < 799.0})
        for tdp, thr, t, v in SUS:
            got = lad.get((t, v))
            if not got:
                ent["dropped"].append({"cell": f"S-tdp{tdp}-thr{thr}-{t}-{v}", "why": "no E64 power ladder"})
                continue
            raw, ref = got
            # the sustained power at 600 MHz carries the leakage at the threshold, which is where it settles
            p600_hot = raw[600] + T.lam(float(thr), T.V[600], g) - T.lam(BURST_LAUNCH_C, T.V[600], g)
            if p600_hot > 1.05 * tdp - EXIT_MARGIN_W:
                ent["dropped"].append({"cell": f"S-tdp{tdp}-thr{thr}-{t}-{v}",
                                       "why": "power-loop exit unreachable at the hot 600 MHz power",
                                       "p600_hot_w": round(p600_hot, 2)})
                continue
            if thr < 65 and (dl["a_c"] + dl["k_c_per_w"] * p600_hot) > thr:
                ent["dropped"].append({"cell": f"S-tdp{tdp}-thr{thr}-{t}-{v}",
                                       "why": "a lowered threshold would put the thermal loop's exit "
                                              "out of reach",
                                       "die600_c": round(dl["a_c"] + dl["k_c_per_w"] * p600_hot, 1)})
                continue
            sim = T.simulate(T.p_from_measured(raw, g, BURST_LAUNCH_C), float(tdp), gov["tau_s"],
                             gov["pass_s"], t_end=SUS_S, t_from=SUS_FROM, T0=BURST_LAUNCH_C,
                             therm=dl, tau_th=tth, trip=float(thr))
            mhz = round(sim["mhz"], 1)
            lo, hi = ((775.0, 800.0) if mhz >= 799 else
                      ((600.0, 625.0) if mhz <= 601 else (mhz - BAND, mhz + BAND)))
            ent["sustained"].append({"cell": f"S-tdp{tdp}-thr{thr}-{t}-{v}", "block": "SUS", "tdp_w": tdp,
                                     "threshold_c": thr, "type": t, "values": v,
                                     "control": tdp == 65 and thr == 65,
                                     "p_w_raw": raw, "pred_mhz_mean": mhz,
                                     "band_mhz": [round(lo, 1), round(hi, 1)],
                                     "pred_die_c": round(sim["die_c"], 2),
                                     "pred_board_w": round(sim["w"], 2),
                                     "share_of_time": {str(k): round(x, 3) for k, x in sim["share"].items()},
                                     "pred_tflops": round(T.rate_t(t, sim["mhz"]), 2),
                                     "anchored_on_own_sustained_mean": False})
        out["variants"][gs] = ent
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    for gs, ent in out["variants"].items():
        print(f"=== gamma {gs}  (governor tau {ent['governor']['tau_s']} s, pass {ent['governor']['pass_s']} s, "
              f"tau_th {ent['tau_th_s']} s)")
        print("  BURST   %-34s %6s %-14s %7s %7s" % ("cell", "MHz", "band", "die C", "board W"))
        for x in ent["burst"]:
            print("          %-34s %6.1f %-14s %7.2f %7.2f"
                  % (x["cell"], x["pred_mhz_mean"], "%.0f-%.0f" % tuple(x["band_mhz"]),
                     x["pred_die_c"], x["pred_board_w"]))
        print("  SUS     %-34s %6s %-14s %7s %7s  %s" % ("cell", "MHz", "band", "die C", "board W", "share"))
        for x in ent["sustained"]:
            print("          %-34s %6.1f %-14s %7.2f %7.2f  %s"
                  % (x["cell"], x["pred_mhz_mean"], "%.0f-%.0f" % tuple(x["band_mhz"]),
                     x["pred_die_c"], x["pred_board_w"], x["share_of_time"]))
        for x in ent["dropped"]:
            print("  DROP    %-34s %s" % (x["cell"], x["why"]))
    return 0


if __name__ == "__main__":
    main()
