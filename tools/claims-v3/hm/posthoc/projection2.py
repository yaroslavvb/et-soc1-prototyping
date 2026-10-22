"""E62, post hoc (chosen after seeing the shutter steps; reported beside the registered statistics, never instead of
them): per-lap half-patch contrasts along templates that come from the OTHER session, after removing the shutter
(FFC) jumps in the one-dimensional projected trace.

Templates. Session 2's blocks are read along session 1's E62-ORBIT corner maps: T_WE = (NW+SW)-(NE+SE),
T_NS = (NW+NE)-(SW+SE). Session 1's E62-ORBIT is read along session 2's E62-WE42 and E62-NS42 maps: T_WE = W12-E12,
T_NS = N12-S12. Maps are Gaussian-smoothed (sigma 6 binned px) and mean-free; a frame's projection is mean(frame over
template > 0) - mean(frame over template < 0), in mK.

Shutter jumps. At every event in RED/ffc.json the projected trace's jump is the difference at the event time of two
straight lines, fitted to the bins in [event - 4 s, event - 0.75 s] and [event + 0.75 s, event + 4 s], each window cut
short at the neighbouring events (a median when a side has fewer than 3 bins); every bin after the event is lowered by
it. Per-pixel noise is ~34 mK per frame, but the projection averages half the frame, so a jump is measured to a few mK.

Statistic. For each analysed lap (runner's warm-up flag off) and each arm, the mean of the cleaned trace over the last
40% of that arm's dwell; two-arm blocks: arm A minus arm B per lap; sequences: each position minus the lap's mean.
Usage: projection2.py <RED1> <ANA1> <RED2> <ANA2> <out.json> <trace.png>"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

red1, ana1, red2, ana2, outj, outp = sys.argv[1:7]
SIG, STEADY, W, G = 6.0, 0.4, 4.0, 0.75


def prep(m):
    m = gaussian_filter(np.asarray(m, dtype=np.float64), SIG)
    return m - m.mean()


def load(red):
    z = np.load(f"{red}/frames.npz")
    sess = json.load(open(f"{red}/session.json"))
    return {"ts": z["t_s"], "mk": z["mk"], "t0": sess["t_start_ms"],
            "ok": (~z["ffc"].astype(bool)) & (z["n"] >= MIN_N),
            "phases": [json.loads(l) for l in open(f"{red}/phases.jsonl")],
            "blocks": [json.loads(l) for l in open(f"{red}/blocks.jsonl")],
            "ffc": sorted(e["t_s"] for e in json.load(open(f"{red}/ffc.json")))}


def project(S, T):
    """raw projected traces for every bin, along each template"""
    out = {k: np.empty(len(S["ts"])) for k in T}
    pos = {k: T[k] > 0 for k in T}
    neg = {k: T[k] < 0 for k in T}
    for i in range(len(S["ts"])):
        D = gaussian_filter(S["mk"][i].astype(np.float64), SIG)
        for k in T:
            out[k][i] = D[pos[k]].mean() - D[neg[k]].mean()
    return out


sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from jumps import MIN_N, clusters, level, windows  # noqa: E402


def dejump(ts, p, events, ok):
    """remove each shutter cluster's jump from a 1-D trace (jumps.py); returns the cleaned trace and the jumps"""
    q = p.copy()
    jumps = []
    cl = clusters(events, ts[0], ts[-1])
    for i, (a, b) in enumerate(cl):
        pre, post = windows(ts, ok, cl, i)
        t_mid = 0.5 * (a + b)
        ya, yb = level(ts, q, pre, t_mid), level(ts, q, post, t_mid)
        if ya is None or yb is None:
            jumps.append((a, None))
            continue
        j = float(yb - ya)
        q[ts > a] -= j
        jumps.append((a, j))
    return q, jumps


def steady(S, p, trace):
    a, b = (p["t_first_start_ms"] - S["t0"]) / 1000, (p["t_last_end_ms"] - S["t0"]) / 1000
    w = (S["ts"] >= b - STEADY * (b - a)) & (S["ts"] <= b)
    return float(trace[w].mean()) if w.any() else None


S1, S2 = load(red1), load(red2)
am1 = np.load(f"{ana1}/E62-ORBIT/arm_maps.npz")
NW, NE, SE, SW = (prep(am1[k]) for k in ("B4NW", "B4NE", "B4SE", "B4SW"))
T1 = {"WE": prep((NW + SW) - (NE + SE)), "NS": prep((NW + NE) - (SW + SE))}       # for session 2
we2, ns2 = np.load(f"{ana2}/E62-WE42/arm_maps.npz"), np.load(f"{ana2}/E62-NS42/arm_maps.npz")
T2 = {"WE": prep(we2["W12"] - we2["E12"]), "NS": prep(ns2["N12"] - ns2["S12"])}  # for session 1
res = {"post_hoc": True, "templates_cos": {
    "orbit_WE_vs_halves_WE": float((T1["WE"] * T2["WE"]).sum() / np.sqrt((T1["WE"] ** 2).sum() * (T2["WE"] ** 2).sum())),
    "orbit_NS_vs_halves_NS": float((T1["NS"] * T2["NS"]).sum() / np.sqrt((T1["NS"] ** 2).sum() * (T2["NS"] ** 2).sum()))},
    "blocks": {}, "jumps": {}}

P1, P2 = project(S1, T2), project(S2, T1)
C1 = {k: dejump(S1["ts"], P1[k], S1["ffc"], S1["ok"]) for k in P1}
C2 = {k: dejump(S2["ts"], P2[k], S2["ffc"], S2["ok"]) for k in P2}
for k in ("WE", "NS"):
    res["jumps"][f"s1_{k}"] = {"n": len(C1[k][1]), "abs_median_mk": float(np.median([abs(j) for _, j in C1[k][1] if j is not None]))}
    res["jumps"][f"s2_{k}"] = {"n": len(C2[k][1]), "abs_median_mk": float(np.median([abs(j) for _, j in C2[k][1] if j is not None])),
                                "abs_max_mk": float(max(abs(j) for _, j in C2[k][1] if j is not None))}

TWO = {"E62-WE42": ("W12", "E12", "WE"), "E62-NS42": ("N12", "S12", "NS"), "E62-W8BE8B": ("W8B", "E8B", "WE"),
       "E62-NULLAA": ("W12_A", "W12_B", "WE"), "E62-NULLGEO": ("NULLP12", "NULLQ12", "WE")}
for blk, (aa, bb, tk) in TWO.items():
    ph = [p for p in S2["phases"] if p["block"] == blk and not p.get("warmup")]
    rows = []
    for c in sorted({p["cycle"] for p in ph}):
        pa = next((p for p in ph if p["cycle"] == c and p["set"] == aa), None)
        pb = next((p for p in ph if p["cycle"] == c and p["set"] == bb), None)
        if not pa or not pb:
            continue
        v = {k: steady(S2, pa, C2[k][0]) - steady(S2, pb, C2[k][0]) for k in ("WE", "NS")}
        rows.append({"lap": c, "order": "AB" if pa["t_first_start_ms"] < pb["t_first_start_ms"] else "BA",
                     "on_template_mk": round(v[tk], 1), "on_other_mk": round(v["NS" if tk == "WE" else "WE"], 1)})
    x = np.array([r["on_template_mk"] for r in rows])
    y = np.array([r["on_other_mk"] for r in rows])
    e = {"arms": [aa, bb], "template": tk, "laps": rows, "n": len(rows),
         "mean_mk": round(float(x.mean()), 1), "other_axis_mean_mk": round(float(y.mean()), 1)}
    if len(x) > 1:
        e["se_mk"] = round(float(x.std(ddof=1) / np.sqrt(len(x))), 1)
        e["other_axis_se_mk"] = round(float(y.std(ddof=1) / np.sqrt(len(y))), 1)
        e["t"] = round(float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))), 2) if x.std(ddof=1) > 0 else None
    res["blocks"][blk] = e


def sequence(S, C, blk, sets):
    ph = [p for p in S["phases"] if p["block"] == blk and not p.get("warmup")]
    out = {s: {"WE": [], "NS": []} for s in sets}
    for c in sorted({p["cycle"] for p in ph}):
        lap = {p["set"]: p for p in ph if p["cycle"] == c}
        if set(lap) != set(sets):
            continue
        for k in ("WE", "NS"):
            vals = {s: steady(S, lap[s], C[k][0]) for s in sets}
            m = np.mean(list(vals.values()))
            for s in sets:
                out[s][k].append(vals[s] - m)
    summ = {}
    for s in sets:
        summ[s] = {}
        for k in ("WE", "NS"):
            a = np.array(out[s][k])
            summ[s][k] = {"mean_mk": round(float(a.mean()), 1),
                          "se_mk": round(float(a.std(ddof=1) / np.sqrt(len(a))), 1) if len(a) > 1 else None,
                          "laps": [round(float(v), 1) for v in a]}
    return summ


res["blocks"]["E62-ORBIT"] = {"templates": "session 2's W12-E12 and N12-S12 maps",
                              "positions": sequence(S1, C1, "E62-ORBIT", ["B4NW", "B4NE", "B4SE", "B4SW", "B4C"])}
res["blocks"]["E62-SWEEP"] = {"templates": "session 1's ORBIT corner maps",
                              "positions": sequence(S2, C2, "E62-SWEEP", ["SCAN1", "SCAN2", "CEN8", "SCAN4", "SCAN5"])}
json.dump(res, open(outj, "w"), indent=1)

# the figure: raw and cleaned west-minus-east traces through session 2's two-arm blocks
show = ["E62-WE42", "E62-NS42", "E62-NULLAA", "E62-NULLGEO", "E62-W8BE8B", "E62-SWEEP"]
fig, axs = plt.subplots(len(show), 1, figsize=(13, 2.5 * len(show)))
for ax, blk in zip(axs, show):
    b = next(x for x in S2["blocks"] if x["block"] == blk)
    a_, e_ = (b["t_start_ms"] - S2["t0"]) / 1000, (b["t_end_ms"] - S2["t0"]) / 1000
    w = (S2["ts"] >= a_) & (S2["ts"] <= e_)
    tk = TWO.get(blk, (None, None, "WE"))[2]
    for p in S2["phases"]:
        if p["block"] == blk and p["t_first_start_ms"]:
            ax.axvspan((p["t_first_start_ms"] - S2["t0"]) / 1000, (p["t_last_end_ms"] - S2["t0"]) / 1000,
                       color=("#f3d9cf" if p["set"] in ("W12", "N12", "W8B", "W12_A", "NULLP12", "SCAN1", "SCAN2") else "#d6e4f0"),
                       alpha=0.6, lw=0)
    raw, cl = P2[tk][w], C2[tk][0][w]
    ax.plot(S2["ts"][w], raw - np.median(raw), lw=0.7, color="#bbbbbb", label="raw projection")
    ax.plot(S2["ts"][w], cl - np.median(cl), lw=0.9, color="#a63f1c", label="shutter jumps removed")
    ax.set_title(f"{blk}  (along T_{tk})", fontsize=10, loc="left")
    ax.set_ylabel("mK")
    ax.legend(fontsize=7, loc="lower right")
axs[-1].set_xlabel("seconds since session 2 start")
fig.tight_layout()
fig.savefig(outp, dpi=80)
print(json.dumps(res["templates_cos"]), json.dumps(res["jumps"]))
for blk, e in res["blocks"].items():
    if "laps" in e:
        print(f"{blk:12s} {e['arms'][0]}-{e['arms'][1]} on T_{e['template']}: {e['mean_mk']} +- {e.get('se_mk')} mK "
              f"(t {e.get('t')}, n {e['n']}); other axis {e['other_axis_mean_mk']} +- {e.get('other_axis_se_mk')}; "
              f"laps {[(r['order'], r['on_template_mk']) for r in e['laps']]}")
    else:
        print(blk, e["templates"])
        for s, v in e["positions"].items():
            print(f"   {s:6s} WE {v['WE']['mean_mk']:7.1f} +- {v['WE']['se_mk']}   NS {v['NS']['mean_mk']:7.1f} +- {v['NS']['se_mk']}")
