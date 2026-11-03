#!/usr/bin/env python3
"""Q139(q), POST HOC: G3 (g3_model.py) on every sustained run of the four GEMM-pattern sessions on aifoundry2 (E119, E126, E136, E146),
against E136's frozen sustained law (footing G2 on the same P0 levels, the old arm) and Q138(t)'s frozen chain on the measured board trace
(the heat path alone, die only). Nothing is refitted: every constant of G3 was frozen before these runs were scored here, but every run
here was committed before G3 was written, so this is a post hoc check, labelled as such.

P0's levels: E146 `cells.*.P0_w`, E136 `cells.*.P_w` (P1 for g4k), and for E119's and E126's arms E136's law in its arm form,
B(f) + c600 s(f) (600 T(600)) / (f T(f)), c600 from E107's pinned S of the arm (E119's rule) and T(f) the session's own fit of the arm
(results.json per_arm.*.fit: measured, so E119/E126 levels carry the session's own speed).

    python3 posthoc_g3.py > posthoc-g3.txt        (writes posthoc-g3.json)
"""
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g3_model as G  # noqa: E402

LAB = G.LAB
DATA = os.path.join(LAB, "docs/reports/data")
hm, M119 = G.hm, G.M119
SESS = {"E119": "2026-11-01-e119-gemm-speed", "E126": "2026-11-02-e126-gemm-arms", "E136": "2026-11-02-e136-large-gemm",
        "E146": "2026-11-02-e146-gemm-stores"}
P136 = json.load(open(os.path.join(LAB, "tools/claims-v3/e136/predictions-e136.json")))
P146 = json.load(open(os.path.join(LAB, "tools/claims-v3/e146/predictions-e146.json")))
B, SF = M119.B, M119.SF


def arm_levels(res, arm, t, kind):
    fit = res["per_arm"][f"{arm}.{t}"]["fit"]
    T = lambda f: fit["C"] / f + fit["M"]  # noqa: E731
    c = M119.c600(arm, t, kind)
    return {f: B[f] + c * SF[f] * (600.0 * T(600)) / (f * T(f)) for f in (600, 700, 800)}


def levels_for(name, res, cell):
    arm, t, kind = cell.split("-")[0], cell.split("-")[1], "-".join(cell.split("-")[2:])
    if name == "E146":
        return {int(k): v for k, v in P146["cells"][cell]["P0_w"].items()}
    if name == "E136":
        return {int(k): v for k, v in P136["cells"][cell]["P_w"].items()}
    return arm_levels(res, arm, t, kind)


def base_label(lab):
    return lab


CACHE = []


def main():
    out = {"what": "Q139(q) post hoc: G3 against E136's law and the chain on the measured trace, every sustained run of E119, E126, E136, E146",
           "constants": {"trip_C": G.T_TRIP, "k_leak_W_per_C": G.K_LEAK, "burst_cap": [G.WB, G.SB], "off_share": G.OFF_SHARE,
                         "anchor_s": G.ANCHOR_S, "window_s": G.SUS_LAST_S, "chain": "model-q138t.json a2"}, "runs": [], "sessions": {}}
    print("Q139(q) POST HOC: G3 = P0 + Q138(t)'s frozen chain + leakage 0.442 W/C + the burst cap + the trip at 65.9 C; sustained window = in-kernel "
          "samples of the last 40 s. err = measured - predicted.")
    print(f"{'session':6s} {'run':34s} {'meas MHz':>8s} {'W':>6s} {'die':>5s} | {'G3 MHz':>6s} {'W':>6s} {'die':>5s} | {'E136law':>7s} {'W':>6s} {'die':>5s} | "
          f"{'chain':>5s} | p800 P0(800)")
    for name, d in SESS.items():
        S = os.path.join(DATA, d, "aifoundry2", "s1")
        res = json.load(open(os.path.join(DATA, d, "results.json")))
        runs = [json.loads(x) for x in open(os.path.join(S, "runs.jsonl"))]
        L = [json.loads(x) for x in gzip.open(os.path.join(S, "launches.jsonl.gz"), "rt")]
        paths = sorted(os.path.join(S, "tel", f) for f in os.listdir(os.path.join(S, "tel")) if f.endswith(".jsonl.gz"))
        tel = hm.load_tel(paths, sensor="fw")
        t = tel["t"]
        ok = np.isfinite(tel["T"]) & np.isfinite(tel["P"])
        g = np.arange(t[ok][0], t[ok][-1], G.DT)
        Pm = np.interp(g, t[ok], tel["P"][ok])
        Tm = np.interp(g, t[ok], tel["T"][ok])
        Xm = G.chain_open(Pm)
        rows = []
        for r in runs:
            if r.get("processes", 1) < 2:
                continue
            procs = [p for p in L if p["run"] == r["run"] and p.get("role") == "work"]
            if not procs:
                continue
            t0 = min(p["t_start_ms"] for p in procs) / 1000.0
            t1 = max(p["t_end_ms"] for p in procs) / 1000.0
            kw = [(k["t_start_ms"] / 1000.0, k["t_end_ms"] / 1000.0) for p in procs for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
            i0 = int(np.searchsorted(g, t0))
            i1 = int(np.searchsorted(g, t1))
            gg = g[i0:i1 + 1]
            on = np.zeros(len(gg), bool)
            for a, b in kw:
                on |= (gg >= a) & (gg <= b)
            # the anchor: measured die minus the chain's open-loop die over the 20 s before the start
            ma = (g >= t0 - G.ANCHOR_S) & (g < t0)
            anc = float(np.mean(Tm[ma] - Xm[ma] @ G.R))
            x0 = Xm[i0 - 1]
            T_start = anc + float(G.R @ x0)
            cell = r["label"]
            lev = levels_for(name, res, cell)
            CACHE.append({"session": name, "run": r["run"], "cell": cell, "lev": lev, "on": on.tolist(), "gg0": float(gg[0]), "t1": t1, "x0": x0.tolist(), "anc": anc, "T_start": T_start})
            Tg, Pg, Fg = G.simulate(lev, on, x0, anc, T_start=T_start)
            pred = G.window_means(gg, on, Tg, Pg, Fg, t1)
            # measured, as reduce_hpl reads it: telemetry samples inside kernel windows, last 40 s
            inw = np.zeros(len(t), bool)
            for a, b in kw:
                inw |= (t >= a) & (t <= b)
            mw = inw & (t >= t1 - G.SUS_LAST_S) & (t <= t1)
            meas = {"mhz": float(np.nanmean(tel["mhz"][mw])), "w": float(np.mean(tel["P"][mw])), "die": float(np.mean(tel["T"][mw]))}
            dies = tel["T"][inw & (t >= t0)]
            die_start = float(dies[0])
            law = G.e136_law(lev, die_start)
            # the chain on the measured trace, same anchor (die only)
            Tc = anc + Xm[i0:i1 + 1] @ G.R
            mm = on & (gg >= t1 - G.SUS_LAST_S) & (gg <= t1)
            chain_die = float(np.mean(Tc[mm]))
            # the run's own first second at 800 MHz (p800, reduce_hpl's), for P0's level
            first = [i for i in range(len(t)) if inw[i] and t[i] >= t0 and tel["mhz"][i] == 800]
            p800 = None
            if first:
                tf = t[first[0]]
                e = [tel["P"][i] for i in first if t[i] <= tf + 1.0]
                p800 = float(np.median(e)) if e else None
            # G3 given the run's own first second (P0's level scaled to p800): the dynamic path alone
            g3p = None
            if p800:
                sc = p800 / lev[800]
                Tq, Pq, Fq = G.simulate(lev, on, x0, anc, T_start=T_start, p_scale=sc)
                g3p = G.window_means(gg, on, Tq, Pq, Fq, t1)
            cl = (res.get("cells") or {}).get(cell, {})
            row = {"session": name, "run": r["run"], "cell": cell, "die_start": die_start, "anchor_C": round(anc, 2), "T_start_chain": round(T_start, 2),
                   "levels_P0": {str(k): round(v, 2) for k, v in lev.items()}, "p800_meas": None if p800 is None else round(p800, 2),
                   "meas": {k: round(v, 2) for k, v in meas.items()}, "results_cell": {"sus_mhz": cl.get("sus_mhz"), "sus_w": cl.get("sus_w"), "sus_die": cl.get("sus_die")},
                   "G3": {k: round(v, 2) for k, v in pred.items()}, "E136_law": {k: round(v, 2) for k, v in law.items()},
                   "chain_on_measured_die": round(chain_die, 2), "G3_given_p800": None if g3p is None else {k: round(v, 2) for k, v in g3p.items()},
                   "peak_pred_w": round(float(np.max(Pg)), 2), "peak_meas_w": round(float(np.max(tel["P"][(t >= t0) & (t <= t1)])), 2),
                   "regime_pred": "trip" if np.nanmean(Fg[on & (gg >= t1 - G.SUS_LAST_S)]) < 795 else "800"}
            rows.append(row)
            print(f"{name:6s} {r['run']:34s} {meas['mhz']:8.1f} {meas['w']:6.2f} {meas['die']:5.1f} | {pred['mhz']:6.1f} {pred['w']:6.2f} {pred['die']:5.1f} | "
                  f"{law['mhz']:7.1f} {law['w']:6.2f} {law['die']:5.1f} | {chain_die:5.1f} | {p800 if p800 is None else round(p800, 1)} {lev[800]:.1f}")
        out["runs"] += rows

    def stats(rows, arm, q):
        e = []
        for x in rows:
            if arm == "chain":
                if q != "die":
                    continue
                e.append(x["meas"]["die"] - x["chain_on_measured_die"])
            else:
                v = x[arm]
                if v is None:
                    continue
                e.append(x["meas"][q] - v[q])
        if not e:
            return None
        e = np.array(e)
        return {"n": int(len(e)), "rms": round(float(np.sqrt(np.mean(e ** 2))), 3), "mean": round(float(np.mean(e)), 3), "max_abs": round(float(np.max(np.abs(e))), 3)}

    groups = {s: [x for x in out["runs"] if x["session"] == s] for s in SESS}
    groups["all"] = out["runs"]
    groups["trip (G3 says held)"] = [x for x in out["runs"] if x["regime_pred"] == "trip"]
    groups["800 (G3 says not held)"] = [x for x in out["runs"] if x["regime_pred"] == "800"]
    groups["fp32/fp16 random"] = [x for x in out["runs"] if x["cell"].endswith("randn")]
    groups["int8 full"] = [x for x in out["runs"] if x["cell"].endswith("full")]
    groups["zeros"] = [x for x in out["runs"] if x["cell"].endswith("zeros")]
    print()
    print("error = measured - predicted, rms (mean) [max |e|] over the sustained runs; rules (the critic's): clock 15 MHz, board 2 W, window die 1 C")
    for gname, rows in groups.items():
        st = {}
        for arm in ("G3", "E136_law", "chain", "G3_given_p800"):
            for q in ("mhz", "w", "die"):
                s_ = stats(rows, arm, q)
                if s_:
                    st[f"{arm}.{q}"] = s_
        within = {q: sum(1 for x in rows if abs(x["meas"][q] - x["G3"][q]) <= {"mhz": 15, "w": 2, "die": 1}[q]) for q in ("mhz", "w", "die")}
        within_law = {q: sum(1 for x in rows if abs(x["meas"][q] - x["E136_law"][q]) <= {"mhz": 15, "w": 2, "die": 1}[q]) for q in ("mhz", "w", "die")}
        out["sessions"][gname] = {"n": len(rows), "stats": st, "G3_within_rule": within, "E136_law_within_rule": within_law}
        print(f"\n{gname} (n {len(rows)}):  G3 within the rules: clock {within['mhz']}, board {within['w']}, die {within['die']};  E136's law: "
              f"{within_law['mhz']}, {within_law['w']}, {within_law['die']}")
        for k, v in st.items():
            print(f"   {k:20s} rms {v['rms']:7.3f}  mean {v['mean']:+7.3f}  max {v['max_abs']:7.3f}  (n {v['n']})")
    json.dump(out, open(os.path.join(HERE, "posthoc-g3.json"), "w"), indent=1)
    for c, rw in zip(CACHE, out["runs"]):
        c["meas"] = rw["meas"]
    json.dump(CACHE, open(os.path.join(HERE, "posthoc-g3-inputs.json"), "w"))


if __name__ == "__main__":
    main()
