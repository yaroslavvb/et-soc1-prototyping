#!/usr/bin/env python3
"""heat-q145a, Part 1: the numbers the footing law rule fixes, computed mechanically from committed files (post hoc reads; no fit to
any model error).

  1. the law per card at its idle operating point: a weighted quadratic over the pooled per-degree means of every committed dedicated
     idle cycle on that card (the firmware's whole-degree reading, rule F), and its slope at 55-62 C;
  2. the check against E97's pooled law (aifoundry3, the 34-sensor mean) at the same temperatures;
  3. each pool-8 session's referral temperature T_mid = the median, over the runs that pass every per-run gate, of
     (launch reading + window reading) / 2, from the committed reduction's runs.csv (both columns are independent of k);
  4. the session scale against k from the committed arms (scored.json > arms): s(k) / s(0) = 1 - c1 k;
  5. E97's steady heat balance closed with each slope: (board rise - leakage part) / (S x compute share);
  6. the heat chain's loop gain R x L'(T) (R = 0.8695 C per board W, model-q138t.json a3);
  7. the ensemble in-run slope from profile.json (this lane's), over [1, 4], [1.5, 4] and [2, 4] s.

    python3 -B law_rule.py <lab repo top> <idle.json> <profile.json> <out.json>
"""
import csv
import json
import os
import sys

import numpy as np

A97, B97, C97 = 0.006175439291277969, -0.3665903970069978, 25.998917638611008
R_A3 = 0.8695


def pooled_law(tabs, lo, hi):
    acc = {}
    for pdw, pds in tabs:
        for t, w in pdw.items():
            ti = int(t)
            if lo <= ti <= hi:
                n = round(pds[t] / 0.1)
                s = acc.setdefault(ti, [0.0, 0])
                s[0] += w * n
                s[1] += n
    Ts = sorted(t for t in acc if acc[t][1] >= 100)
    T = np.array(Ts, float)
    W = np.array([acc[t][0] / acc[t][1] for t in Ts])
    n = np.array([acc[t][1] for t in Ts], float)
    A = np.c_[T * T, T, np.ones_like(T)] * np.sqrt(n)[:, None]
    c, *_ = np.linalg.lstsq(A, W * np.sqrt(n), rcond=None)
    resid = W - (c[0] * T * T + c[1] * T + c[2])
    # a bootstrap over cycles for the slope's spread
    rng = np.random.default_rng(145)
    bs = {x: [] for x in (55, 56, 57, 58, 59, 60, 61, 62)}
    for _ in range(2000):
        idx = rng.integers(0, len(tabs), len(tabs))
        acc2 = {}
        for i in idx:
            pdw, pds = tabs[i]
            for t, w in pdw.items():
                ti = int(t)
                if lo <= ti <= hi:
                    nn = round(pds[t] / 0.1)
                    s = acc2.setdefault(ti, [0.0, 0])
                    s[0] += w * nn
                    s[1] += nn
        T2 = np.array(sorted(t for t in acc2 if acc2[t][1] >= 100), float)
        if len(T2) < 4:
            continue
        W2 = np.array([acc2[int(t)][0] / acc2[int(t)][1] for t in T2])
        n2 = np.array([acc2[int(t)][1] for t in T2], float)
        A2 = np.c_[T2 * T2, T2, np.ones_like(T2)] * np.sqrt(n2)[:, None]
        c2, *_ = np.linalg.lstsq(A2, W2 * np.sqrt(n2), rcond=None)
        for x in bs:
            bs[x].append(2 * c2[0] * x + c2[1])
    return {"quad_w": [float(x) for x in c], "T_degrees": [int(T.min()), int(T.max())], "cycles": len(tabs), "rms_w": float(np.sqrt(np.mean(resid ** 2))),
            "slope": {str(x): float(2 * c[0] * x + c[1]) for x in bs},
            "slope_ci95": {str(x): [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for x, v in bs.items() if v}}


def tables(path, keep=None):
    j = json.load(open(path))
    out = []
    for p, rec in sorted(j["passes"].items()):
        if rec.get("usable") and (keep is None or p in keep):
            out.append((rec["per_degree_w"], rec["per_degree_s"]))
    return out


def raw_tables(idle_json, card):
    """per-degree tables of E44's raw cycles, recomputed from the telemetry by rederive_idle.py is not stored per degree; re-read here"""
    return None


def tmid(runs_csv):
    vals, dts = [], []
    for r in csv.DictReader(open(runs_csv)):
        if (r.get("fail") or "0") not in ("0", "", "[]"):
            continue
        try:
            sc, tw = float(r["start_c"]), float(r["t_win"])
        except (TypeError, ValueError):
            continue
        vals.append((sc + tw) / 2.0)
        dts.append(tw - sc)
    return float(np.median(vals)), len(vals), float(np.median(dts)), float(np.percentile(vals, 10)), float(np.percentile(vals, 90))


def main():
    top, idlep, profp, outp = sys.argv[1:5]
    D = os.path.join(top, "docs/reports/data")
    res = {"what": __doc__.strip().splitlines()[0]}
    e71 = os.path.join(D, "2026-10-27-e71-idle-slope-aifoundry3")
    # 1. laws. aifoundry3: E44's 3 + E71's 6 cycles (firmware reading); aifoundry2 idle: E66's 18; card 1: E44's 3 (raw, re-read)
    a3 = tables(os.path.join(e71, "sep-p1p3.json")) + tables(os.path.join(e71, "slopes.json"))
    a2 = tables(os.path.join(e71, "aifoundry2-58-62.json"))
    # card 1's per-degree tables from E44's raw telemetry (the same rule F as rederive_idle.py)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rederive_idle as RI
    c1 = []
    for p in ("p1", "p2", "p3"):
        a = RI.raw_cycle(os.path.join(D, "2026-09-25-claims-v3/raw/aifoundry1-c1/idle", p))
        T, W = a[:, 0], a[:, 1]
        c1.append(({str(int(t)): float(W[T == t].mean()) for t in sorted(set(T.tolist()))},
                   {str(int(t)): round(float((T == t).sum()) * 0.1, 1) for t in sorted(set(T.tolist()))}))
    res["law"] = {"aifoundry3": dict(pooled_law(a3, 52, 66), sources="E44 p1-p3 (25-26 Sep) + E71 p21-p26 (27 Oct), 600 MHz, 522-523 mV"),
                  "aifoundry1c1": dict(pooled_law(c1, 56, 70), sources="E44 p1-p3 on card 1 (25-26 Sep), 600 MHz, 499 mV"),
                  "aifoundry2_idle": dict(pooled_law(a2, 49, 66), sources="E66 p13-p30 (26-27 Oct), 600 MHz, 519 mV")}
    res["law"]["aifoundry3"]["E71_only"] = pooled_law(tables(os.path.join(e71, "slopes.json")), 52, 66)["slope"]
    res["law"]["aifoundry3"]["E44_only"] = pooled_law(tables(os.path.join(e71, "sep-p1p3.json")), 54, 66)["slope"]
    # 2. E97's law at the same temperatures
    res["E97_law_slope"] = {str(x): 2 * A97 * x + B97 for x in (55, 56, 57, 58, 59, 60, 61, 62)}
    res["check_a3_vs_E97"] = {x: res["law"]["aifoundry3"]["slope"][x] - res["E97_law_slope"][x] for x in res["E97_law_slope"]}
    # 3. the sessions' referral temperatures and the rule's k
    def lawk(card, T):
        q = res["law"][card]["quad_w"]
        return 2 * q[0] * T + q[1]
    res["sessions"] = {}
    for run, rel, card in (("E171", "2026-11-05-e171-blind8-aifoundry3", "aifoundry3"), ("E172", "2026-11-05-e172-blind8-card1", "aifoundry1c1")):
        tm, n, dtw, p10, p90 = tmid(os.path.join(D, rel, "runs.csv"))
        res["sessions"][run] = {"card": card, "T_mid": tm, "runs": n, "median_dT_win": dtw, "T_mid_p10_p90": [p10, p90],
                                "k_rule": lawk(card, tm), "k_rule_at_p10_p90": [lawk(card, p10), lawk(card, p90)]}
    # 4. s against k from the committed arms
    res["s_vs_k"] = {}
    for run, rel, armk in (("E171", "2026-11-05-e171-blind8-aifoundry3", {"primary": 0.20563713796102187, "leak0.1994": 0.1994,
                                                                            "leak0.3803": 0.3803, "leak0": 0.0, "auto_dips_removed": 0.2850}),
                           ("E172", "2026-11-05-e172-blind8-card1", {"primary": 0.3134106532552718, "leak0.2955": 0.2955,
                                                                      "leak0.3320": 0.3320, "session_own_slope": 0.4030})):
        sc = json.load(open(os.path.join(D, rel, "scored.json")))
        pts = []
        for nm, k in armk.items():
            if nm == "primary":
                s = sc["primary"]["scale"]["s_float"]
                kp = sc["primary"].get("kept_passes")
            else:
                a = sc["arms"].get(nm) or {}
                if "s_float" not in a:
                    continue
                s, kp = a["s_float"], a.get("kept_passes")
            pts.append({"arm": nm, "k": k, "s": float(s), "kept_passes": kp})
        ks = np.array([p["k"] for p in pts])
        ss = np.array([p["s"] for p in pts])
        same = [p for p in pts]
        c, i0 = np.polyfit(ks, ss, 1)
        res["s_vs_k"][run] = {"points": pts, "fit_s0": float(i0), "fit_c1": float(-c / i0)}
    # 5. E97's closure with each slope
    e97 = json.load(open(os.path.join(D, "2026-11-01-e97-heat-low-power-steady/e97.json")))["holds"]["holds"]
    res["E97_closure"] = {}
    for h in ("H1", "H2", "H3"):
        st, lk = e97[h]["steady"], e97[h]["leak"]
        dP, dT, Seff = st["dP"], st["dT"], st["S_eff_W"]
        row = {"dT_C": dT, "dP_W": dP, "S_eff_W": Seff, "law_dP_leak_W": lk["dP_leak_W"], "closure_law": lk["closure"]}
        for nm, k in (("footing_0.2056", 0.20563713796102187), ("E171_auto_0.2850", 0.2850), ("E60_a3_0.203", 0.203)):
            row[f"closure_{nm}"] = (dP - k * dT) / Seff
        res["E97_closure"][h] = row
    # 6. loop gains
    res["loop_gain_a3"] = {str(x): R_A3 * (2 * A97 * x + B97) for x in (52, 55, 58, 60, 62, 66)}
    res["loop_gain_a3_footing"] = R_A3 * 0.20563713796102187
    # 7. ensemble in-run slopes
    prof = json.load(open(profp))
    res["ensemble_inrun"] = {}
    for k, rows in prof.items():
        out = {}
        for lo in (1.0, 1.5, 2.0):
            sel = [r for r in rows if r["t_s"] >= lo and r["dP_w"] is not None]
            x = np.array([r["dT_fw"] for r in sel])
            y = np.array([r["dP_w"] for r in sel])
            out[f"from_{lo}s"] = float(np.polyfit(x, y, 1)[0])
        res["ensemble_inrun"][k] = out
    json.dump(res, open(outp, "w"), indent=1, sort_keys=True)
    L = res["law"]
    for c in L:
        print("law", c, L[c]["cycles"], L[c]["T_degrees"], {x: round(v, 4) for x, v in L[c]["slope"].items()}, "rms", round(L[c]["rms_w"], 4))
        print("     ci95 58-60", {x: [round(a, 4) for a in L[c]["slope_ci95"][x]] for x in ("58", "59", "60")})
    print("E71 only", {x: round(v, 4) for x, v in L["aifoundry3"]["E71_only"].items()})
    print("E44 only", {x: round(v, 4) for x, v in L["aifoundry3"]["E44_only"].items()})
    print("a3 - E97", {x: round(v, 4) for x, v in res["check_a3_vs_E97"].items()})
    for r, v in res["sessions"].items():
        print("session", r, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.items()})
    for r, v in res["s_vs_k"].items():
        print("s vs k", r, round(v["fit_s0"], 5), "c1", round(v["fit_c1"], 4), [(p["arm"], p["k"], round(p["s"], 5), p["kept_passes"]) for p in v["points"]])
    for h, v in res["E97_closure"].items():
        print("closure", h, {k: round(x, 4) for k, x in v.items()})
    print("loop", {k: round(v, 4) for k, v in res["loop_gain_a3"].items()}, "footing", round(res["loop_gain_a3_footing"], 4))
    print("ensemble", res["ensemble_inrun"])


if __name__ == "__main__":
    main()
