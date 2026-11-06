#!/usr/bin/env python3
"""heat-q145a, Part 1: in-run slopes, in-pass rest slopes and a sensor test, re-derived by independent code (post hoc).

Reads committed lab files only; imports nothing from the lab repo. Written from the methods as the READMEs and reducers state
them (E60's leak_slope, E78's runs_of_pass, Q139(u)'s F1), not by calling them.

  in-run slope (E60 'leak auto', E78 'leak auto'): per run, board_w against temp_c.minshire[0] over the trace from
      max(t0 + 0.8 s, lo - 0.2 s) to the run's last launch record's end, lo = t0 + 1 s (pinned cards) or, on a governed card,
      max(t0 + 1 s, the first sample at the busy clock + 0.5 s); a straight line if the trace has > 10 samples and spans >= 1 C;
      the median over runs. Variants: the trace started at t0 + 1.5 s and t0 + 2.0 s.
  in-pass rests (Q139(u) F1): the 1 s idle bracket [t0 - 1.2, t0 - 0.2) s before each run, valid with >= 8 samples, >= 0.8 s
      after the previous device process, its mean die reading within 1.5 C of the launch reading; the run passing the gates
      that do not depend on k (one clock 600 MHz in its window, the voltage within 3 mV of the pass median, the launch on
      protocol within 0.5 C of the target, the quiet time, records ok, cycles per op within 0.5%, >= 15 window samples with
      no gap over 500 ms, duty >= 0.97). OLS of the bracket's board W on its die reading with one intercept per pass and one
      slope per card; the reverse regression; a bootstrap over passes. The board dips (E82 A2: a sample under the lower of
      its i-2 and i+2 neighbours by 4.0 W) are dropped first on the 600 MHz cards.
  sensor test (E97 Part A, the 34 raw codes): each 30 s kind half after its reference half: the rise of the firmware
      reading and of the 34-sensor mean over [1, 3) s against the bracket [-1.2, -0.2) s, and the in-run slope against
      each reading over [0.8, 4.5] s.

    python3 -B footing_inrun.py <lab repo top> <out.json>
"""
import gzip
import json
import os
import sys

import numpy as np

G_TS, H_TS, CAL5 = 57400, 249400, 4096       # E97's code_to_c, as smoke_gate_e176.py has it
CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
D = None


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def jl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def load_tel(d, nodips):
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    if not tel:
        return None
    t = np.array([s["t_ms"] for s in tel], float)
    P = np.array([s["board_w"] for s in tel], float)
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel], float)
    mhz = np.array([(s.get("mhz") or {}).get("minion", -1) for s in tel])
    mv = np.array([float((s.get("die_mv") or {}).get("minion", np.nan)) for s in tel])
    m34 = np.full(len(tel), np.nan)
    for i, s in enumerate(tel):
        pv = s.get("pvt") or {}
        cs = pv.get("c") or []
        if pv.get("st") == 0 and not pv.get("f") and len(cs) == 34:
            m34[i] = sum(code_to_c(x) for x in cs) / 34.0
    keep = np.ones(len(t), bool)
    if nodips:
        for i in range(2, len(P) - 2):
            if P[i] < min(P[i - 2], P[i + 2]) - 4.0:
                keep[i] = False
    return {"t": t[keep], "P": P[keep], "T": T[keep], "mhz": mhz[keep], "mv": mv[keep], "m34": m34[keep],
            "dropped": int((~keep).sum())}


def runs_of(d, X, gov_free=False, busy=800):
    recs = jl(os.path.join(d, "runs.jsonl"))
    marks = sorted(jl(os.path.join(d, "marks.jsonl")), key=lambda m: m.get("t_start_ms", 0))
    try:
        cfg = json.load(open(os.path.join(d, "configs.json")))
    except (OSError, ValueError):
        cfg = {"args": {}}
    args = cfg.get("args", {})
    target = None if float(args.get("preheat", 1)) <= 0 else (float(args["target"]) if "target" in args else None)
    quiet_req = float(args.get("quiet_s", 0) or 0)
    grp = {}
    for r in recs:
        grp.setdefault((r.get("block"), r.get("item"), r.get("pos", 0), r.get("attempt", 1)), []).append(r)
    t, P, T, mhz, mv = X["t"], X["P"], X["T"], X["mhz"], X["mv"]
    out, prev_end = [], None
    for m in marks:
        if m.get("kind") == "run":
            rr = sorted(grp.get((m.get("block"), m.get("item"), m.get("pos", 0), m.get("attempt", 1)), []),
                        key=lambda r: r["t_start_ms"])
            pe = m.get("prev_end_ms", prev_end)
            if rr:
                t0 = rr[0]["t_start_ms"]
                tend = rr[-1]["t_end_ms"]
                lo = t0 + 1000
                if gov_free:
                    at = np.where((t >= t0) & (t <= t0 + 4000) & (mhz == busy))[0]
                    if len(at):
                        lo = max(t0 + 1000, t[at[0]] + 500)
                hi = lo + 2000
                w = (t >= lo) & (t < hi)
                br = (t >= t0 - 1200) & (t < t0 - 200)
                tw = t[w]
                gaps = np.diff(np.r_[lo, tw, hi]) if w.sum() else np.array([1e9])
                work = 0.0
                for r_ in rr:
                    dur = max(1.0, r_["t_end_ms"] - r_["t_start_ms"])
                    ov = max(0.0, min(r_["t_end_ms"], hi) - max(r_["t_start_ms"], lo))
                    work += r_.get("iters", 0) * r_.get("minions", 1024) * ov / dur
                typ = rr[0].get("type")
                cpo = CPO.get(typ)
                duty = (work / ((hi - lo) / 1000.0)) / (600e6 * 1024 / cpo) if cpo else None
                traces = {}
                for name, st in (("s08", max(t0 + 800, lo - 200)), ("s15", t0 + 1500), ("s20", t0 + 2000)):
                    q = (t >= st) & (t <= tend)
                    traces[name] = (T[q], P[q], X["m34"][q])
                out.append({"t0": t0, "tend": tend, "item": m.get("item"), "type": typ, "start_c": m.get("start_c"),
                            "on_protocol": m.get("on_protocol"), "quiet_s": m.get("quiet_s"), "prev_end": pe,
                            "target": target, "quiet_req": quiet_req,
                            "mhz_w": sorted(set(int(x) for x in mhz[w])), "mv_w": float(np.nanmean(mv[w])) if w.sum() else None,
                            "n_w": int(w.sum()), "gap_max": float(gaps.max()), "duty": duty,
                            "cpo_ok": (all(abs(r_["cycles_per_op"] / cpo - 1) <= 0.005 for r_ in rr if r_.get("cycles_per_op"))
                                       if cpo else True),
                            "ok_rec": all(r_.get("ok", False) for r_ in rr),
                            "p_idle": float(P[br].mean()) if br.sum() else None, "t_idle": float(T[br].mean()) if br.sum() else None,
                            "n_idle": int(br.sum()),
                            "dT_win": (float(T[w].mean()) - m["start_c"]) if (w.sum() and m.get("start_c") is not None) else None,
                            "traces": traces})
        if m.get("kind") in ("run", "heater", "burnin"):
            prev_end = m.get("t_end_ms", prev_end)
    return out


def inrun_slope(runs, which="s08", use="T"):
    ks = []
    for r in runs:
        T_, P_, M_ = r["traces"][which]
        x = T_ if use == "T" else M_
        if use != "T":
            ok = np.isfinite(x)
            x, P_ = x[ok], P_[ok]
        if len(x) > 10 and x.max() - x.min() >= (1.0 if use == "T" else 0.3):
            ks.append(float(np.polyfit(x, P_, 1)[0]))
    return {"median": float(np.median(ks)) if ks else None, "n_runs": len(ks),
            "q25": float(np.percentile(ks, 25)) if ks else None, "q75": float(np.percentile(ks, 75)) if ks else None}


def rest_ok(r, med_mv):
    if r["mhz_w"] != [600] or r["mv_w"] is None or abs(r["mv_w"] - med_mv) > 3.0:
        return False
    if r["target"] is not None:
        if r["start_c"] is None or not r["on_protocol"] or abs(r["start_c"] - r["target"]) > 0.5:
            return False
        if r["quiet_req"] and (r["quiet_s"] is None or r["quiet_s"] < r["quiet_req"] - 0.05):
            return False
    if not r["ok_rec"] or not r["cpo_ok"] or r["n_w"] < 15 or r["gap_max"] > 500:
        return False
    if r["duty"] is not None and r["duty"] < 0.97:
        return False
    if r["p_idle"] is None or r["n_idle"] < 8 or r["prev_end"] is None or (r["t0"] - 1200) - r["prev_end"] < 800:
        return False
    if r["start_c"] is None or abs(r["t_idle"] - r["start_c"]) > 1.5:
        return False
    return True


def pooled_slope(groups, draws=2000, seed=145):
    def one(gs):
        sxy = sxx = syy = 0.0
        for x, y in gs:
            if len(x) < 2:
                continue
            dx, dy = x - x.mean(), y - y.mean()
            sxy += float(dx @ dy)
            sxx += float(dx @ dx)
            syy += float(dy @ dy)
        return (sxy / sxx if sxx else None), (syy / sxy if sxy else None), sxx, syy, sxy
    k, krev, sxx, syy, sxy = one(groups)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(draws):
        idx = rng.integers(0, len(groups), len(groups))
        kk = one([groups[i] for i in idx])[0]
        if kk is not None:
            bs.append(kk)
    n = sum(len(x) for x, _ in groups)
    wsd = float(np.sqrt(sxx / max(n - len(groups), 1)))
    return {"k": k, "k_reverse": krev, "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None,
            "n_rests": int(n), "n_passes": len(groups), "within_pass_sd_T": wsd,
            "r2_within": (sxy * sxy / (sxx * syy)) if sxx and syy else None}


def pass_rests(d, nodips):
    X = load_tel(d, nodips)
    if X is None:
        return None, None
    runs = runs_of(d, X)
    mvs = [r["mv_w"] for r in runs if r["mv_w"] is not None]
    med = float(np.median(mvs)) if mvs else 0
    ok = [r for r in runs if rest_ok(r, med)]
    x = np.array([r["t_idle"] for r in ok])
    y = np.array([r["p_idle"] for r in ok])
    return (x, y), runs


def main():
    top, outp = sys.argv[1], sys.argv[2]
    global D
    D = os.path.join(top, "docs/reports/data")
    res = {"what": __doc__.strip().splitlines()[0]}
    # ---- (1) E60's in-run slopes, three cards
    e60 = os.path.join(D, "2026-10-20-bitflip-ladder")
    res["E60"] = {}
    for card, gov, passes in (("aifoundry3", False, range(1, 9)), ("aifoundry2", True, range(1, 11)),
                              ("aifoundry1-c0", True, range(1, 11))):
        allr = []
        for p in passes:
            d = os.path.join(e60, card, "hl", f"p{p}")
            X = load_tel(d, nodips=False)
            if X is None:
                continue
            rs = runs_of(d, X, gov_free=gov)
            if card == "aifoundry2":
                rs = [r for r in rs if r["item"] != "ls_h8"]        # E60's amendment A3: excluded by name before the fit
            allr += rs
        res["E60"][card] = {"runs": len(allr), "s08": inrun_slope(allr, "s08"), "s15": inrun_slope(allr, "s15"),
                            "s20": inrun_slope(allr, "s20"),
                            "median_dT_win": float(np.median([r["dT_win"] for r in allr if r["dT_win"] is not None]))}
        print("E60", card, res["E60"][card]["runs"], res["E60"][card]["s08"], res["E60"][card]["s15"]["median"],
              res["E60"][card]["s20"]["median"], flush=True)
    # ---- (2) E171 and E172: the session's own in-run slope, dips kept and removed; the session's rests
    for name, base, card in (("E171", "2026-11-05-e171-blind8-aifoundry3/aifoundry3/e171", "a3"),
                             ("E172", "2026-11-05-e172-blind8-card1/aifoundry1-c1/e172", "c1")):
        dd = sorted(os.path.join(D, base, x) for x in os.listdir(os.path.join(D, base)) if x.startswith("p"))
        rec = {}
        for nod in (False, True):
            allr, groups = [], []
            for d in dd:
                X = load_tel(d, nodips=nod)
                rs = runs_of(d, X)
                allr += rs
                mvs = [r["mv_w"] for r in rs if r["mv_w"] is not None]
                med = float(np.median(mvs))
                ok = [r for r in rs if rest_ok(r, med)]
                groups.append((np.array([r["t_idle"] for r in ok]), np.array([r["p_idle"] for r in ok])))
            key = "dips_removed" if nod else "dips_kept"
            rec[key] = {"runs": len(allr), "inrun_s08": inrun_slope(allr, "s08"), "inrun_s15": inrun_slope(allr, "s15"),
                        "inrun_s20": inrun_slope(allr, "s20"), "rests": pooled_slope(groups),
                        "median_dT_win": float(np.median([r["dT_win"] for r in allr if r["dT_win"] is not None])),
                        "rest_T_range": [float(min(g[0].min() for g in groups if len(g[0]))),
                                         float(max(g[0].max() for g in groups if len(g[0])))]}
            print(name, key, rec[key]["inrun_s08"], rec[key]["inrun_s15"]["median"], rec[key]["inrun_s20"]["median"],
                  {k: rec[key]["rests"][k] for k in ("k", "k_reverse", "ci95", "n_rests", "within_pass_sd_T")}, flush=True)
        res[name] = rec
    # ---- (3) Q139(u)'s footing re-derived: its 123 passes, rests by F1 (dips dropped on both 600 MHz cards)
    fdir = os.path.join(D, "2026-11-03-q139u-footing/reduced")
    exps_a3 = ["e78", "e86", "e90", "e92", "e95", "e115", "e121", "e122", "e123", "e127", "e140", "e141"]
    exps_c1 = ["e82", "e88", "e91", "e93", "e94", "e102", "e103", "e104", "e106", "e108", "e128", "e131", "e137", "e142"]
    datadir = {"e78": "2026-10-31-e78-kinds-energy-matrix/aifoundry3/kinds", "e86": "2026-10-31-e86-real-tensors-energy/aifoundry3/kinds",
               "e90": "2026-10-31-e90-signs-spread/aifoundry3/kinds", "e92": "2026-11-01-e92-sign-split/aifoundry3/kinds",
               "e95": "2026-11-01-e95-real-tensors-energy/aifoundry3/kinds", "e82": "2026-10-31-e82-kinds-aifoundry1/aifoundry1-c1/kinds"}
    res["footing"] = {}
    for card, exps in (("a3", exps_a3), ("c1", exps_c1)):
        groups, per_exp, missing = [], {}, []
        for e in exps:
            j = json.load(open(os.path.join(fdir, f"{e}-footing.json")))
            dirs = []
            for x in j["dirs"]:
                if x.startswith("<"):
                    tail = x.split("/")[-1]
                    dirs.append(os.path.join(D, datadir[e], tail))
                else:
                    dirs.append(os.path.join(top, x))
            eg = []
            for d in dirs:
                if not os.path.isdir(d):
                    missing.append(d.replace(top + "/", ""))
                    continue
                g, _ = pass_rests(d, nodips=True)
                if g is not None and len(g[0]) >= 2:
                    eg.append(g)
            groups += eg
            per_exp[e] = pooled_slope(eg, draws=200)["k"] if eg else None
        ps = pooled_slope(groups)
        res["footing"][card] = {"pooled": ps, "per_experiment": per_exp, "missing_dirs": missing,
                                "T_range": [float(min(g[0].min() for g in groups)), float(max(g[0].max() for g in groups))]}
        print("footing", card, {k: ps[k] for k in ("k", "k_reverse", "ci95", "n_rests", "n_passes", "within_pass_sd_T", "r2_within")},
              "missing", len(missing), flush=True)
    # ---- (4) the sensor test on E97 Part A (the 34 raw codes)
    sens = []
    for p in ("p9710", "p9711"):
        d = os.path.join(D, "2026-11-01-e97-heat-low-power-steady/aifoundry3/e97", p)
        X = load_tel(d, nodips=False)
        marks = jl(os.path.join(d, "marks.jsonl"))
        blocks = {m["block"]: m for m in marks if m.get("kind") == "block"}
        halves = sorted([m for m in marks if m.get("kind") == "half"], key=lambda m: m["t_start_ms"])
        t, P, T, M = X["t"], X["P"], X["T"], X["m34"]
        for h in halves:
            if h.get("role") != "K":
                continue
            s0 = h["t_start_ms"]
            br = (t >= s0 - 1200) & (t < s0 - 200)
            w = (t >= s0 + 1000) & (t < s0 + 3000)
            tr = (t >= s0 + 800) & (t <= s0 + 4500)
            if br.sum() < 8 or w.sum() < 15 or not np.isfinite(M[br]).all() or not np.isfinite(M[w]).all():
                continue
            dTf = float(T[w].mean() - T[br].mean())
            dTm = float(M[w].mean() - M[br].mean())
            dP = float(P[w].mean() - P[br].mean())
            kf = float(np.polyfit(T[tr], P[tr], 1)[0]) if np.ptp(T[tr]) >= 1 else None
            km = float(np.polyfit(M[tr], P[tr], 1)[0]) if np.ptp(M[tr]) >= 0.3 else None
            sens.append({"pass": p, "block": h["block"], "item": h["item"], "ref": blocks.get(h["block"], {}).get("ref"),
                         "dP_w": dP, "dT_fw": dTf, "dT_m34": dTm, "k_inrun_fw": kf, "k_inrun_m34": km,
                         "T_m34_bracket": float(M[br].mean()), "T_fw_bracket": float(T[br].mean())})
    big = [s for s in sens if s["dP_w"] >= 15]
    res["sensor_test"] = {"halves": len(sens), "big_halves_dP_ge_15W": len(big),
                          "big": {"median_dT_fw": float(np.median([s["dT_fw"] for s in big])) if big else None,
                                  "median_dT_m34": float(np.median([s["dT_m34"] for s in big])) if big else None,
                                  "median_ratio_m34_over_fw": float(np.median([s["dT_m34"] / s["dT_fw"] for s in big if s["dT_fw"] > 0.2])) if big else None,
                                  "median_k_inrun_fw": float(np.median([s["k_inrun_fw"] for s in big if s["k_inrun_fw"] is not None])) if any(s["k_inrun_fw"] is not None for s in big) else None,
                                  "median_k_inrun_m34": float(np.median([s["k_inrun_m34"] for s in big if s["k_inrun_m34"] is not None])) if any(s["k_inrun_m34"] is not None for s in big) else None,
                                  "items": sorted(set(s["item"] for s in big))},
                          "all_ratio_median": float(np.median([s["dT_m34"] / s["dT_fw"] for s in sens if s["dT_fw"] > 0.2])) if sens else None,
                          "rows": sens}
    print("sensor", {k: v for k, v in res["sensor_test"].items() if k != "rows"}, flush=True)
    json.dump(res, open(outp, "w"), indent=1, sort_keys=True, default=lambda o: None)


if __name__ == "__main__":
    main()
