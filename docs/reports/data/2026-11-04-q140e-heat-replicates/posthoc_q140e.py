#!/usr/bin/env python3
"""Q140(e), POST HOC (registered as such in REGISTRATION.md R7.5; never a verdict): the duty convention, the windows and aifoundry2's
level read on sessions already seen, E154 (aifoundry3) and E161 (aifoundry2), with the critic's rank-3 rules as they would have read
there. E161's kernel duty is its own (the same session), so these readings are in sample for the duty; M9's level (Q140(l)) never saw
E161 or E154. Desk only.

    /usr/bin/python3 docs/reports/data/2026-11-04-q140e-heat-replicates/posthoc_q140e.py > .../posthoc.txt
writes posthoc.json beside itself. It imports predict_q140e.py (which checks its frozen inputs' sha256) and E161's registered reducer,
unchanged. numpy 1.26.4, Python 3.9.
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import predict_q140e as P  # noqa: E402  (checks its 26 frozen inputs on import)

sys.path.insert(0, os.path.join(P.REPO, "tools", "claims-v3", "e161"))
import reduce_e161 as R  # noqa: E402  E161's registered reducer, unchanged (checks its own 13 frozen inputs on import)

SE, FT, hm, PQ = P.SE, P.FT, P.hm, P.PQ
r3, rms = P.r3, P.rms


def e154():
    sess = SE.a3_load([P.E154P])
    g, T = sess["g"], sess["T"]
    r0 = sess["rests"][0]
    room = SE.wmean(g, T, r0["t1"] - hm.ANCHOR_S, r0["t1"])
    k0 = g >= r0["t0"]
    preds = {}
    for model in ("M8", "M7", "M6", "E153"):
        S_of = P.s_table(model)
        S_t = SE.s_on_grid(g, [(a, b, S_of[it]) for (a, b, it) in sess["recs"]])
        pb = np.full(len(g), np.nan)
        pb[k0], _ = SE.closed_on_grid(S_t[k0], PQ.TAU, PQ.R3, room, hm.law_a3)
        preds[model] = pb
    pred_a = FT.predict_session(sess, PQ.TAU, PQ.R3)
    _, recs = P.a3_records(P.E154P)
    sc = json.load(open(os.path.join(P.E154D, "scored.json")))
    out = {"room_R0_C": r3(room, 4), "holds": {}}
    for h in sess["holds"]:
        nm = h["name"]
        b = recs[nm]["b"]
        w = (h["launch_period_s"] or 7.0) if h["share"] < 0.9 else 5.0
        row = {"item": h["item"], "kernel_duty": r3(recs[nm]["kernel_duty"], 4), "window_end_moved_s": r3(b - h["t1"], 3)}
        for label, t1 in (("registered_window", h["t1"]), ("convention_window", b)):
            me = P.a3_read(g, T, h["t0"], t1, h["anchor_end"], w, P.CHECK_A3)
            rr = {"measured_rise_C": r3(me["plateau_rise_C"])}
            for model, pb in preds.items():
                pr = P.a3_read(g, pb, h["t0"], t1, h["anchor_end"], w, P.CHECK_A3)
                errs = [me["rise_C_by_s"][k] - pr["rise_C_by_s"][k] for k in pr["rise_C_by_s"] if k == "end" or int(k) >= 60]
                rr[f"E_{model}"] = {"plateau_err_C": r3(me["plateau_rise_C"] - pr["plateau_rise_C"]), "checkpoints_rms_C": r3(rms(errs))}
            a = hm.anchor_value(g, T, pred_a, h["anchor_end"])
            e = T - (pred_a + a)
            rr["A_plateau_err_C"] = r3(SE.wmean(g, e, t1 - 300.0, t1))
            rr["A_frac_of_rise"] = r3(SE.wmean(g, e, t1 - 300.0, t1) / me["plateau_rise_C"], 4)
            row[label] = rr
        if nm in P.POOL6:
            row["registered_scored_json"] = {"E_plateau_err_C": sc["holds"][nm]["E_end_to_end"]["plateau_err_C"],
                                             "E_checkpoint_rms_C": sc["holds"][nm]["E_end_to_end"]["checkpoint_rms_C"],
                                             "A_plateau_err_C": sc["holds"][nm]["A_given_watts"]["plateau_err_C"]}
        out["holds"][nm] = row
    # the critic's rank-3 rules, as they would have read on E154 (post hoc)
    rk = {}
    for label in ("registered_window", "convention_window"):
        inside = []
        for nm in ("K_S", "K_Q", "K_L", "K_O"):
            x = out["holds"][nm][label]["E_M8"]
            sc_ = P.FZ[nm]["critic_scale_C"]
            inside.append({"hold": nm, "scale_C": sc_, "plateau_err_C": x["plateau_err_C"], "rms_C": x["checkpoints_rms_C"],
                           "inside": bool(abs(x["plateau_err_C"]) <= sc_ and x["checkpoints_rms_C"] <= sc_)})
        large = [{"hold": nm, "measured_rise_C": out["holds"][nm][label]["measured_rise_C"], "A_frac": out["holds"][nm][label]["A_frac_of_rise"],
                  "inside": bool(abs(out["holds"][nm][label]["A_frac_of_rise"]) <= P.RK3C_FRAC)}
                 for nm in out["holds"] if out["holds"][nm][label]["measured_rise_C"] >= P.LARGE_RISE_C]
        rk[label] = {"RK3_a": {"holds": inside, "n_inside": sum(x["inside"] for x in inside), "pass": sum(x["inside"] for x in inside) >= 3},
                     "RK3_c_aifoundry3": {"holds": large, "pass": all(x["inside"] for x in large)},
                     "session_rms_E_M8_C": r3(rms([out["holds"][nm][label]["E_M8"]["plateau_err_C"] for nm in P.POOL6]))}
    out["rank3_rules_posthoc"] = rk
    return out


def e161():
    steps, sess = R.load(P.E161D)
    res = json.load(open(os.path.join(P.E161D, "results.json")))
    out = {}
    for st, s in zip(steps, sess):
        item = P.A2_HOLDS[st]
        sd = os.path.join(P.E161D, st)
        h = s["holds"][0]
        procs, recs, d = P.a2_records(sd)
        T_rest, P_ref, n_rest = R.rest_reading(sd)
        t0, b = procs[0][0], procs[-1][1]
        span = b - t0
        g, T = s["g"], s["T"]
        meas_pl = SE.wmean(g, T, b - 300.0, b)
        mcp = {}
        for sec in P.CHECK_A2:
            if sec + 2.5 <= span:
                mcp[str(sec)] = SE.wmean(g, T, t0 + sec - 2.5, t0 + sec + 2.5) - T_rest
        mcp["end"] = SE.wmean(g, T, b - 5.5, b - 0.5) - T_rest
        kr = (s["t_raw"] >= b - 300.0) & (s["t_raw"] <= b)
        f_meas = float(np.mean(s["mhz_raw"][kr]))
        share790 = float(np.mean(s["mhz_raw"][kr] >= 790.0))
        row = {"item": item, "d_own": r3(d, 4), "T_rest_C": r3(T_rest), "P_ref_W": r3(P_ref), "span_s": r3(span, 2),
               "window_end_moved_s": r3(b - h["t1"], 2), "measured_plateau_C": r3(meas_pl), "measured_rise_C": r3(meas_pl - T_rest),
               "measured_clock_MHz_window": r3(f_meas, 1), "measured_share_ge790_window": r3(share790, 4),
               "registered_E161": {k: res["holds"][st]["E_end_to_end"].get(k) for k in ("plateau_err_C", "checkpoints_rms_C", "clock_err_MHz",
                                                                                         "verdict", "clock_verdict")}}

        def score(pred):
            pe = meas_pl - pred["plateau_C_predicted"]
            errs = [mcp[k] - pred["checkpoint_rise_C"][k] for k in pred["checkpoint_rise_C"] if k in mcp]
            o = {"plateau_predicted_C": pred["plateau_C_predicted"], "plateau_err_C": r3(pe), "checkpoints_rms_C": r3(rms(errs)),
                 "checkpoint_err_C": {k: r3(mcp[k] - pred["checkpoint_rise_C"][k]) for k in pred["checkpoint_rise_C"] if k in mcp}}
            if pred["regime"] == "trip":
                o["clock_predicted_MHz"] = pred["clock_MHz_trip_rule"]
                o["clock_err_MHz"] = r3(f_meas - pred["clock_MHz_trip_rule"], 1)
            return o
        for arm, (dd, lvl) in {"primary_M9a_at_own_d": (d, "M9a"), "M8_at_own_d": (d, "M8"), "M8_continuous": (1.0, "M8")}.items():
            row[arm] = score(P.a2_hold(item, T_rest, P_ref, span, dd, lvl))
        row["primary_over_anchor_pm0p5"] = {f"{dT:+.1f}": score(P.a2_hold(item, T_rest + dT, P_ref, span, d, "M9a"))
                                            for dT in (-0.5, 0.5)}
        # arm A on the convention's window (score_e144's arm (a) form)
        pred_a = FT.predict_session(s, PQ.TAU, PQ.R2)
        a = hm.anchor_value(g, T, pred_a, h["anchor_end"])
        e = T - (pred_a + a)
        rise_grid = SE.wmean(g, T, b - 300.0, b) - SE.wmean(g, T, h["anchor_end"] - hm.ANCHOR_S, h["anchor_end"])
        row["A_plateau_err_C"] = r3(SE.wmean(g, e, b - 300.0, b))
        row["A_frac_of_rise"] = r3(SE.wmean(g, e, b - 300.0, b) / rise_grid, 4)
        row["A_registered_E161"] = res["holds"][st]["A_given_watts"].get("plateau_err_C")
        # the readout note (R4): arm A's anchor is the REST's whole-degree die; over +-0.5 C its plateau error moves by -+0.5 C
        row["A_frac_over_anchor_pm0p5"] = {f"{dT:+.1f}": r3((SE.wmean(g, e, b - 300.0, b) - dT) / (rise_grid - dT), 4) for dT in (-0.5, 0.5)}
        out[st] = row
    g1 = out.get("G1Q", {}).get("primary_M9a_at_own_d", {})
    out["rank3_rules_posthoc"] = {
        "RK3_b_G1Q": {"plateau_err_C": g1.get("plateau_err_C"), "rms_C": g1.get("checkpoints_rms_C"),
                      "pass": bool(g1 and abs(g1["plateau_err_C"]) <= P.RK3B_C and g1["checkpoints_rms_C"] <= P.RK3B_C),
                      "over_anchor_pm0p5": {k: {"plateau_err_C": v["plateau_err_C"], "rms_C": v["checkpoints_rms_C"],
                                                "pass": bool(abs(v["plateau_err_C"]) <= P.RK3B_C and v["checkpoints_rms_C"] <= P.RK3B_C)}
                                            for k, v in out["G1Q"]["primary_over_anchor_pm0p5"].items()}},
        "RK3_c_aifoundry2": {st: {"measured_rise_C": out[st]["measured_rise_C"], "A_frac": out[st]["A_frac_of_rise"],
                                  "inside": bool(abs(out[st]["A_frac_of_rise"]) <= P.RK3C_FRAC)} for st in P.A2_HOLDS if st in out}}
    return out


def main():
    res = {"_note": "Q140(e) POST HOC: the convention, windows and level on E154 and E161 (sessions already seen); never a verdict",
           "E154": e154(), "E161": e161()}
    json.dump(res, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
    p = print
    p("Q140(e) post hoc (never a verdict): the duty convention, the windows and the level on E154 and E161")
    a = res["E154"]
    p(f"E154 (aifoundry3), room {a['room_R0_C']} C")
    for nm, r in a["holds"].items():
        cw, rw = r["convention_window"], r["registered_window"]
        p(f"  {nm:4s} d {r['kernel_duty']}  window end moved {r['window_end_moved_s']} s | rise {cw['measured_rise_C']} | E(M8) {rw['E_M8']['plateau_err_C']:+.3f} -> {cw['E_M8']['plateau_err_C']:+.3f} C, "
          f"rms {rw['E_M8']['checkpoints_rms_C']} -> {cw['E_M8']['checkpoints_rms_C']} | A {rw['A_plateau_err_C']:+.3f} -> {cw['A_plateau_err_C']:+.3f} C ({100 * cw['A_frac_of_rise']:+.2f}% of the rise)"
          + (f" | registered {r['registered_scored_json']}" if "registered_scored_json" in r else ""))
    for label, rk in a["rank3_rules_posthoc"].items():
        p(f"  {label}: RK3-a {rk['RK3_a']['n_inside']} of 4 inside the critic scale ({'PASS' if rk['RK3_a']['pass'] else 'FAIL'}): "
          + "; ".join(f"{x['hold']} {x['plateau_err_C']:+.3f}/{x['rms_C']} vs {x['scale_C']}" for x in rk["RK3_a"]["holds"])
          + f" | RK3-c {'PASS' if rk['RK3_c_aifoundry3']['pass'] else 'FAIL'}: "
          + "; ".join(f"{x['hold']} {100 * x['A_frac']:+.2f}%" for x in rk["RK3_c_aifoundry3"]["holds"])
          + f" | session rms {rk['session_rms_E_M8_C']} C")
    b = res["E161"]
    p("E161 (aifoundry2), its own kernel duty (in sample for d), M9's level from Q140(l) (never fitted on E161)")
    for st in P.A2_HOLDS:
        r = b[st]
        p(f"  {st} d {r['d_own']} anchor {r['T_rest_C']} C / {r['P_ref_W']} W; window end moved {r['window_end_moved_s']} s; measured plateau {r['measured_plateau_C']} "
          f"(rise {r['measured_rise_C']}), clock {r['measured_clock_MHz_window']} MHz, share>=790 {r['measured_share_ge790_window']}; registered {r['registered_E161']}")
        for arm in ("primary_M9a_at_own_d", "M8_at_own_d", "M8_continuous"):
            x = r[arm]
            p(f"    {arm:21s} predicted {x['plateau_predicted_C']} -> plateau err {x['plateau_err_C']:+.3f} C, checkpoints rms {x['checkpoints_rms_C']}"
              + (f", clock err {x['clock_err_MHz']:+.1f} MHz (predicted {x['clock_predicted_MHz']})" if "clock_err_MHz" in x else "")
              + f"  {x['checkpoint_err_C']}")
        p(f"    primary over the anchor's +-0.5 C: " + "; ".join(f"{k}: {v['plateau_err_C']:+.3f} / {v['checkpoints_rms_C']}" + (f" / {v['clock_err_MHz']:+.1f} MHz" if 'clock_err_MHz' in v else "")
                                                             for k, v in r["primary_over_anchor_pm0p5"].items()))
        p(f"    arm A on the convention's window {r['A_plateau_err_C']:+.3f} C ({100 * r['A_frac_of_rise']:+.2f}% of the rise; over the anchor's +-0.5 C {r['A_frac_over_anchor_pm0p5']}; registered {r['A_registered_E161']})")
    rk = b["rank3_rules_posthoc"]
    p(f"  RK3-b G1Q: {rk['RK3_b_G1Q']}")
    p(f"  RK3-c aifoundry2: {rk['RK3_c_aifoundry2']}")


if __name__ == "__main__":
    main()
