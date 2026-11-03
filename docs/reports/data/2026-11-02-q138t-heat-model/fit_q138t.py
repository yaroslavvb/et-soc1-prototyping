#!/usr/bin/env python3
"""Q138(t) desk fit (no card): the board-W -> die chains for aifoundry3 card 0 and aifoundry2 card 0, their out-of-sample
scores on the committed long holds, and the frozen model file E144 is scored against.

    python3 docs/reports/data/2026-11-02-q138t-heat-model/fit_q138t.py > docs/reports/data/2026-11-02-q138t-heat-model/fit.txt

writes model-q138t.json and cv-q138t.json beside itself. Inputs, all committed raw telemetry (10 Hz):
  aifoundry3: E89 p8910+p8911 (31 Oct, 1/60 Hz square waves), E97 p9710+p9711+p9720 (1 Nov, Part A square waves, then
              Part B: R0, H1 int8 full 30 min, H2 fp32 ones chained 15 min, R1, H3 fp32 randn natural->stop->reduced, R2)
  aifoundry2: E111 W2 + W1B (1 Nov), E133 W2 + W1B (2 Nov): REST, E98's probe series, its hold of 39, H-F32 (governed fp32
              randn), and REST + H-I8 (int8 -1s at 800 MHz from rest)
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heat_q138t as hm  # noqa: E402

TAU = [1.0, 3.0, 10.0, 30.0, 60.0, 120.0, 250.0, 500.0, 1000.0]
D = hm.DATA


def p(*a):
    return os.path.join(D, *a)


def a3_sessions():
    e89 = hm.load_tel([p("2026-10-31-e89-heat-low-power/aifoundry3/e89", x, "telemetry.jsonl.gz") for x in ("p8910", "p8911")], "codes")
    e97 = hm.load_tel([p("2026-11-01-e97-heat-low-power-steady/aifoundry3/e97", x, "telemetry.jsonl.gz") for x in ("p9710", "p9711", "p9720")], "codes")
    marks = [json.loads(x) for x in open(p("2026-11-01-e97-heat-low-power-steady/aifoundry3/e97/p9720/marks.jsonl"))]
    holds, rests = [], []
    for m in marks:
        if m.get("kind") == "rest" and "t_end_ms" in m:
            rests.append({"name": m["name"], "t0": m["t_start_ms"] / 1e3, "t1": m["t_end_ms"] / 1e3})
        if m.get("kind") == "hold_start":
            holds.append({"name": m["name"], "item": m["item"], "t0": m["t_start_ms"] / 1e3, "chained": m.get("chained", False)})
    for h in holds:
        later = [r for r in rests if r["t0"] >= h["t0"]] + [x for x in holds if x["t0"] > h["t0"]]
        h["t1"] = min(x["t0"] for x in later)
        before = [r for r in rests if r["t1"] <= h["t0"] + 1e-3]
        h["anchor_end"] = max(r["t1"] for r in before)          # the last rest that ended before the hold (H2: R0)
        after = [r for r in rests if r["t0"] >= h["t1"] - 1e-3]
        h["rest_after"] = (after[0]["t0"], after[0]["t1"]) if (after and not [x for x in holds if x["t0"] == h["t1"]]) else None
    out = []
    for name, tel, burn in (("E89", e89, 300.0), ("E97", e97, 600.0)):
        g, P, T = hm.grid(tel)
        Pref = float(np.percentile(P, 2))
        s = {"name": name, "g": g, "P": P, "T": T, "Pref": Pref, "dP": P - Pref, "use": g >= g[0] + burn, "holds": [], "rests": []}
        if name == "E97":
            s["holds"], s["rests"] = holds, rests
        out.append(s)
    return out


def a2_sessions():
    out = []
    for lab, d, files in (("E111-W2", "2026-11-01-e111-heat-steady/W2", None), ("E111-W1B", "2026-11-01-e111-heat-steady/W1B", None),
                          ("E133-W2", "2026-11-02-e133-heat-holds/W2", None), ("E133-W1B", "2026-11-02-e133-heat-holds/W1B", None)):
        fs = sorted(os.listdir(p(d, "tel")))
        paths = [p(d, "tel", f) for f in fs]
        spans = []
        for f, path in zip(fs, paths):
            t = hm.load_tel([path], "fw")["t"]
            spans.append({"file": f, "t0": float(t[0]), "t1": float(t[-1])})
        spans.sort(key=lambda x: x["t0"])
        tel = hm.load_tel(paths, "fw")
        g, P, T = hm.grid(tel)
        rest = [x for x in spans if x["file"].startswith("REST")][0]
        m = (g >= rest["t0"]) & (g <= rest["t1"])
        Pref = float(np.median(P[m]))
        holds = []
        for x in spans:
            if x["file"].startswith(("HOLD", "SUS")):
                holds.append({"name": x["file"].split("-r1")[0], "t0": x["t0"], "t1": x["t1"], "anchor_end": rest["t1"]})
        out.append({"name": lab, "g": g, "P": P, "T": T, "Pref": Pref, "dP": P - Pref, "use": g > rest["t1"] - 60.0,
                    "holds": holds, "rests": [{"name": "REST", "t0": rest["t0"], "t1": rest["t1"]}], "mhz": np.interp(g, tel["t"], tel["mhz"])})
    return out


def predict_session(s, tau, R):
    X = hm.states(s["dP"], tau)
    return X @ np.asarray(R, float)


def score_hold(s, pred, h, plateau_s=300.0):
    g, T = s["g"], s["T"]
    a = hm.anchor_value(g, T, pred, h["anchor_end"])
    m = (g >= h["t0"]) & (g < h["t1"])
    e = T[m] - (pred[m] + a)
    mp = (g >= h["t1"] - plateau_s) & (g < h["t1"])
    out = {"hold": h["name"], "dur_s": float(h["t1"] - h["t0"]), "rms_C": float(np.sqrt(np.mean(e ** 2))), "mean_C": float(np.mean(e)),
           "max_abs_C": float(np.max(np.abs(e))), "plateau_err_C": float(np.mean(T[mp] - pred[mp] - a)),
           "rise_meas_C": float(np.mean(T[mp]) - (a + float(np.mean(pred[(g >= h["anchor_end"] - hm.ANCHOR_S) & (g < h["anchor_end"])])))),
           "anchor_C": a}
    for sec in (60, 120, 300, 600):
        k = (g >= h["t0"] + sec - 5) & (g < h["t0"] + sec + 5)
        if k.any() and h["t0"] + sec < h["t1"]:
            out[f"err_at_{sec}s"] = float(np.mean(T[k] - pred[k] - a))
    if h.get("rest_after"):
        r0, r1 = h["rest_after"]
        k = (g >= r0) & (g < min(r1, r0 + 540.0))
        out["cooldown_rms_C"] = float(np.sqrt(np.mean((T[k] - pred[k] - a) ** 2)))
    return out


def fit_on(sessions, exclude=None, tau=TAU):
    """exclude: list of (session name, t0, t1) windows left out of the fit"""
    ss = []
    for s in sessions:
        u = s["use"].copy()
        for (nm, t0, t1) in (exclude or []):
            if nm == s["name"]:
                u &= ~((s["g"] >= t0) & (s["g"] < t1))
        ss.append({"dP": s["dP"], "T": s["T"], "use": u})
    R, c, rms = hm.fit_chain(ss, tau)
    return R, c, rms


def summarize(name, tau, R):
    tau, R = np.asarray(tau), np.asarray(R)
    nz = R > 1e-6
    sh = {str(x): round(hm.step_share(tau, R, x), 3) for x in (2, 10, 30, 60, 120, 300, 600, 900)}
    return {"name": name, "tau_s": tau[nz].tolist(), "R_C_per_W": [round(float(x), 5) for x in R[nz]], "R_total": round(float(R.sum()), 4),
            "t63_s": round(hm.effective_tau(tau, R), 1), "t90_s": round(hm.effective_tau(tau, R, 0.9), 1), "share_by_s": sh}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = {"tau_grid_s": TAU, "a3": {}, "a2": {}}
    cv = {"a3": {}, "a2": {}}
    print("Q138(t) desk fit: board W -> die, open loop, NNLS on the tau grid", TAU)

    # ------------------------------------------------------------ aifoundry3
    A3 = a3_sessions()
    e97 = [s for s in A3 if s["name"] == "E97"][0]
    print("\n== aifoundry3 card 0, 600 MHz: sessions", [(s["name"], round(s["g"][-1] - s["g"][0]), round(s["Pref"], 2)) for s in A3])
    before = json.load(open(os.path.join(hm.ROOT, "tools/claims-v3/e97/desk/chain_e89.json")))["fits"]["lab_grid"]
    arms = {}
    arms["before: plateau only, 0.90 C per board W, no dynamics (M6's quote)"] = ("inst", 0.90)
    arms["before: E89's frozen chain (E97's registration, lab grid)"] = ("chain", (before["tau"], before["R"]))
    R89, _, rms89 = fit_on([s for s in A3 if s["name"] == "E89"])
    arms["E89 only, this grid"] = ("chain", (TAU, R89.tolist()))
    RA, _, rmsA = fit_on(A3, exclude=[("E97", e97["holds"][0]["t0"] - 1, e97["g"][-1] + 1)])
    arms["E89 + E97 Part A (every hold left out)"] = ("chain", (TAU, RA.tolist()))
    for arm, (kind, par) in arms.items():
        rows = []
        if kind == "inst":
            pred = par * e97["dP"]
        else:
            pred = predict_session(e97, *par)
        for h in e97["holds"]:
            rows.append(score_hold(e97, pred, h))
        cv["a3"][arm] = rows
    # leave one hold out: the hold and its cool-down left out of the fit
    loho = []
    for h in e97["holds"]:
        t1 = h["rest_after"][1] if h.get("rest_after") else h["t1"]
        R, _, _ = fit_on(A3, exclude=[("E97", h["t0"], t1)])
        pred = predict_session(e97, TAU, R)
        r = score_hold(e97, pred, h)
        r["R_total_fit"] = float(R.sum())
        loho.append(r)
    cv["a3"]["leave one hold out (E89 + E97, the hold and its cool-down left out)"] = loho
    Rf, cf, rmsf = fit_on(A3)
    out["a3"] = summarize("aifoundry3 card 0 (600 MHz), fitted on E89 + E97 (A and B)", TAU, Rf)
    out["a3"].update({"R_full_grid": Rf.tolist(), "fit_rms_C": rmsf, "intercepts_C": cf.tolist(), "sensor": "34-sensor mean of the raw codes",
                      "Pref_W": {s["name"]: s["Pref"] for s in A3}})
    pred = predict_session(e97, TAU, Rf)
    out["a3"]["in_sample"] = [score_hold(e97, pred, h) for h in e97["holds"]]
    for arm, rows in cv["a3"].items():
        print(f"\n  {arm}")
        for r in rows:
            print(f"    {r['hold']:3s} {r['dur_s']:6.0f}s rms {r['rms_C']:5.2f} mean {r['mean_C']:+5.2f} max {r['max_abs_C']:5.2f} plateau err {r['plateau_err_C']:+5.2f} "
                  f"(rise {r['rise_meas_C']:5.2f}) @60s {r.get('err_at_60s', float('nan')):+5.2f} @300s {r.get('err_at_300s', float('nan')):+5.2f}"
                  f" cool-down rms {r.get('cooldown_rms_C', float('nan')):5.2f}")
    print("\n  frozen aifoundry3 chain:", json.dumps({k: out["a3"][k] for k in ("tau_s", "R_C_per_W", "R_total", "t63_s", "t90_s", "share_by_s")}))
    print("  in sample:", [(r["hold"], round(r["rms_C"], 3), round(r["plateau_err_C"], 3)) for r in out["a3"]["in_sample"]])

    # ------------------------------------------------------------ aifoundry2
    A2 = a2_sessions()
    print("\n== aifoundry2 card 0, governed: sessions", [(s["name"], round(s["g"][-1] - s["g"][0]), round(s["Pref"], 2)) for s in A2])
    folds = {"fit E111, predict E133": (["E111-W2", "E111-W1B"], ["E133-W2", "E133-W1B"]),
             "fit E133, predict E111": (["E133-W2", "E133-W1B"], ["E111-W2", "E111-W1B"])}
    for fold, (tr, te) in folds.items():
        R, _, _ = fit_on([s for s in A2 if s["name"] in tr])
        rows = []
        for s in A2:
            if s["name"] in te:
                pred = predict_session(s, TAU, R)
                for h in s["holds"]:
                    if h["name"].startswith("HOLD"):
                        r = score_hold(s, pred, h)
                        r["session"] = s["name"]
                        rows.append(r)
        cv["a2"][fold] = {"R_total": float(R.sum()), "rows": rows, "chain": summarize(fold, TAU, R)}
    for arm, c in (("before: plateau only, 0.673 C per board W, no dynamics (M6's quote)", ("inst", 0.673)),
                   ("before: one pole, tau 89 s, 0.673 C per board W (E111's asymptote beside)", ("chain", ([89.0], [0.673])))):
        rows = []
        for s in A2:
            pred = c[1] * s["dP"] if c[0] == "inst" else predict_session(s, *c[1])
            for h in s["holds"]:
                if h["name"].startswith("HOLD"):
                    r = score_hold(s, pred, h)
                    r["session"] = s["name"]
                    rows.append(r)
        cv["a2"][arm] = {"rows": rows}
    for arm, c in cv["a2"].items():
        print(f"\n  {arm}" + (f"  (R_total {c['R_total']:.3f})" if "R_total" in c else ""))
        for r in c["rows"]:
            print(f"    {r['session']:9s} {r['hold']:32s} {r['dur_s']:6.0f}s rms {r['rms_C']:5.2f} mean {r['mean_C']:+5.2f} max {r['max_abs_C']:5.2f} "
                  f"plateau err {r['plateau_err_C']:+5.2f} (rise {r['rise_meas_C']:5.2f}) @60s {r.get('err_at_60s', float('nan')):+5.2f}")
    R2f, c2f, rms2f = fit_on(A2)
    out["a2"] = summarize("aifoundry2 card 0 (governed), fitted on E111 + E133", TAU, R2f)
    out["a2"].update({"R_full_grid": R2f.tolist(), "fit_rms_C": rms2f, "intercepts_C": c2f.tolist(), "sensor": "the firmware's whole-degree minshire[0]",
                      "Pref_W": {s["name"]: s["Pref"] for s in A2}})
    print("\n  frozen aifoundry2 chain:", json.dumps({k: out["a2"][k] for k in ("tau_s", "R_C_per_W", "R_total", "t63_s", "t90_s", "share_by_s")}))
    for fold in folds:
        print(f"  {fold} chain:", json.dumps({k: cv['a2'][fold]['chain'][k] for k in ('tau_s', 'R_C_per_W', 'R_total', 't63_s')}))

    # switching power of the aifoundry2 kinds, from the training holds (what (b) plans with)
    s2 = {}
    for s in A2:
        for h in s["holds"]:
            if not h["name"].startswith("HOLD"):
                continue
            g = s["g"]
            m = (g >= h["t0"] + 30) & (g < h["t1"])
            Trest = float(np.mean(s["T"][(g >= h["anchor_end"] - 120) & (g < h["anchor_end"])]))
            leak = hm.law_a2(s["T"][m]) - hm.law_a2(Trest)
            S_eff = float(np.mean(s["P"][m] - s["Pref"] - leak))
            mh = s["mhz"][m]
            s2.setdefault(h["name"], []).append({"session": s["name"], "S_eff_W": S_eff, "share_800": float(np.mean(mh >= 790)),
                                                 "share_600": float(np.mean(mh <= 610)), "T_rest": Trest, "P_ref": s["Pref"]})
    out["a2"]["S_eff_from_holds"] = s2
    print("\n  aifoundry2 switching power over the hold, board - P_ref - leakage at 0.442 W/C:")
    for k, v in s2.items():
        for x in v:
            print(f"    {k:32s} {x['session']:9s} S_eff {x['S_eff_W']:6.2f} W  share at 800 MHz {x['share_800']:.3f}, at 600 {x['share_600']:.3f}, rest die {x['T_rest']:.2f}")
    json.dump(out, open(os.path.join(here, "model-q138t.json"), "w"), indent=1)
    json.dump(cv, open(os.path.join(here, "cv-q138t.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
