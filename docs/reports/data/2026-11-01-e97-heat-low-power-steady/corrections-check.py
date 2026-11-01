#!/usr/bin/env python3
"""E97, corrections after verification (Sun 1 Nov 2026): prints every number the README's section "Corrections after verification" cites, from the committed files only. It changes
nothing and scores nothing. Run from anywhere, numpy only:

    python3 corrections-check.py > corrections-check.txt

Reads e97.json and scored.json beside it, the raw passes aifoundry3/e97/p9710, p9711 and p9720, the boxes' history excerpts room/, E78's e78*.json and E89's e89.json. Section tags in brackets
match the README's C1-C9. Times are PST on 1 Nov 2026.
"""
import datetime as dt
import gzip
import json
import math
import os
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, ".."))
G, H_, C5 = 57400, 249400, 4096
C78 = 0.118
T1 = 12.706


def c2t(n):
    return (G + H_ * np.asarray(n, float) / C5 - H_ / 2) / 1000.0


def ep(h, m, s=0):
    return dt.datetime(2026, 11, 1, h + 8, m, s, tzinfo=dt.timezone.utc).timestamp()


def clock(x):
    return (dt.datetime.fromtimestamp(x, dt.timezone.utc) - dt.timedelta(hours=8)).strftime("%H:%M:%S")


def load(p):
    d = os.path.join(HERE, "aifoundry3/e97", p)
    tel = [json.loads(x) for x in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") if x.startswith("{")]
    tel = [r for r in tel if "board_w" in r and len(r.get("pvt", {}).get("c", [])) == 34]
    t = np.array([r["t_ms"] / 1000 for r in tel])
    S = c2t(np.array([r["pvt"]["c"] for r in tel], float))
    A = {"t": t, "S": S, "T": S.mean(axis=1), "P": np.array([r["board_w"] for r in tel], float),
         "Pm": np.array([r["sp"]["minion_w"][0] for r in tel], float), "Ps": np.array([r["sp"]["sram_w"][0] for r in tel], float),
         "Pn": np.array([r["sp"]["noc_w"][0] for r in tel], float)}
    A["marks"] = [json.loads(x) for x in open(os.path.join(d, "marks.jsonl"))]
    A["runs"] = [json.loads(x) for x in open(os.path.join(d, "runs.jsonl"))]
    return A


e = json.load(open(os.path.join(HERE, "e97.json")))
sc = json.load(open(os.path.join(HERE, "scored.json")))
B = e["blocks"]
Hs = e["holds"]["holds"]
C = e["cells_over_idle"]
LOW = [b for b in B if b != "f32randn"]
A = load("p9720")
t, T, S, P, Pm, Ps, Pn, marks, runs = A["t"], A["T"], A["S"], A["P"], A["Pm"], A["Ps"], A["Pn"], A["marks"], A["runs"]
hold = {m["name"]: m for m in marks if m["kind"] == "hold"}
rest = {m["name"]: m for m in marks if m["kind"] == "rest"}
law = np.array(e["holds"]["idle_law_pooled"]["poly"])


def baseline(name):
    """the reducer's: a straight line between the idle before and the idle after, for T and P"""
    x = Hs[name]
    tb = rest[x["idle"]["before"]["rest"]]["t_end_ms"] / 1000
    ta = rest[x["idle"]["after"]["rest"]]["t_end_ms"] / 1000 - 60
    Tb, Ta = x["idle"]["before"]["T"], x["idle"]["after_used"]["T"]
    Pb, Pa = x["idle"]["before"]["P"], x["idle"]["after_used"]["P"]
    return (lambda s: Tb + (Ta - Tb) * (s - tb) / (ta - tb)), (lambda s: Pb + (Pa - Pb) * (s - tb) / (ta - tb))


def wm(y, a, b):
    q = (t >= a) & (t < b)
    return float(np.nanmean(y[q]))


print("[C1] the holds: not steady by the registered test; the plateau, the asymptotes, the range")
for name in Hs:
    x = Hs[name]
    t1 = hold[name]["t_end_ms"] / 1000
    w = x["slope_window_s"]
    bT, bP = baseline(name)
    bt, by = [], []
    for s in np.arange(t1 - w, t1 - 29, 30):
        q = (t >= s) & (t < s + 30)
        bt.append(t[q].mean())
        by.append(T[q].mean() - bT(t[q].mean()))
    bt, by = np.array(bt), np.array(by)
    c, cov = np.polyfit(bt - bt[0], by, 1, cov=True)
    print(f"  {name}: slope over the last {w:.0f} s {c[0] * 60:+.4f} C/min, OLS se {math.sqrt(cov[0, 0]) * 60:.4f} (registered reading {x['slope_C_per_min']:+.4f}; band |0.02|); verdict " +
          [v for v in sc["verdicts"] if v["rule"] == "E97-B1" and v["cell"] == name][0]["verdict"])
a = hold["H1"]["t_end_ms"] / 1000
q = (t >= a - 300) & (t < a)
cw = np.polyfit(t[q] - a, T[q], 1)
print(f"  H1's reading window, its last 300 s: slope {cw[0] * 60:+.4f} C/min, {abs(cw[0]) * 300:.2f} C across the window")
for name, first in (("H1", 600), ("H2", 300), ("H3", 600)):
    x = Hs[name]
    t0 = hold[name]["t_start_ms"] / 1000
    t1 = hold[name]["t_end_ms"] / 1000
    bT, bP = baseline(name)
    vals = []
    for s in np.arange(t0 + first, t1 - 299, 60):
        vals.append((wm(T, s, s + 300) - bT(s + 150)) / (wm(P, s, s + 300) - bP(s + 150)))
    st = x["steady"]
    lo, hi = (st["dT"] - 0.4) / st["dP"], (st["dT"] + 0.4) / st["dP"]
    print(f"  {name}: rolling 300 s windows from {first} s on: rise per board W {min(vals):.3f}-{max(vals):.3f}; registered {st['R_ol']:.3f}; with +-0.4 C on its rise [{lo:.3f}, {hi:.3f}]; registered asymptote {x['asymptote']['dT_C']:.2f} C (tau {x['asymptote']['tau_s']:.0f} s, rms {x['asymptote']['rms']:.2f} C), per board W {x['asymptote']['dT_C'] / st['dP']:.3f}; 'bound' {st['eT']:.3f} C")
lo = min((Hs[n]["steady"]["dT"] - 0.4) / Hs[n]["steady"]["dP"] for n in Hs)
hi = max((Hs[n]["steady"]["dT"] + 0.4) / Hs[n]["steady"]["dP"] for n in Hs)
print(f"  the three together with +-0.4 C: {lo:.2f}-{hi:.2f}")
t0 = hold["H1"]["t_start_ms"] / 1000
bT, bP = baseline("H1")
b60 = [wm(T, s, s + 60) - bT(s + 30) for s in np.arange(t0 + 600, t0 + 1799, 60)]
print(f"  H1's plateau from minute 10, 60 s bins: {min(b60):.2f}-{max(b60):.2f} C (+-{(max(b60) - min(b60)) / 2:.2f})")
for name, (w0, w1), lab in (("H1", (600, 900), "before its move"), ("H1", (1080, 1200), "at its peak"), ("H1", (1500, 1800), "the registered window"), ("H2", (240, 480), "before its move"), ("H2", (600, 900), "the registered window, after its move"), ("H3", (900, 1200), "before its move"), ("H3", (1500, 1800), "the registered window, after its move")):
    s0 = hold[name]["t_start_ms"] / 1000
    bT, bP = baseline(name)
    print(f"  {name} {w0}-{w1} s, {lab}: rise {wm(T, s0 + w0, s0 + w1) - bT(s0 + (w0 + w1) / 2):.2f} C, per board W {(wm(T, s0 + w0, s0 + w1) - bT(s0 + (w0 + w1) / 2)) / (wm(P, s0 + w0, s0 + w1) - bP(s0 + (w0 + w1) / 2)):.3f}")
for r in ("R0", "R1", "R2"):
    b = rest[r]["t_end_ms"] / 1000
    row = [round(wm(T, s, s + 60), 3) for s in np.arange(b - 360, b - 1, 60)]
    q = (t >= b - 300) & (t < b)
    print(f"  {r}: the last six 60 s means {row}; slope over its last 300 s {np.polyfit(t[q] - b, T[q], 1)[0] * 60:+.3f} C/min")
print()

print("[C2] the plateau's moves: every sensor, all boxes, each with windows either side")
rooms = {h: [json.loads(x) for x in gzip.open(os.path.join(HERE, "room", h + ".jsonl.gz"), "rt")] for h in ("aifoundry1", "aifoundry2", "aifoundry3")}
R = {}
for h, rows in rooms.items():
    R[h] = {"t": np.array([r["t"] / 1000 for r in rows]), "cpu": np.array([r.get("cpu", np.nan) for r in rows], float),
            "nic": np.array([r["temps"].get("nic", np.nan) for r in rows], float), "nvme": np.array([r["temps"].get("nvme", np.nan) for r in rows], float),
            "die0": np.array([(r["cards"][0].get("die") if r["cards"][0].get("die") is not None else np.nan) for r in rows], float),
            "die1": np.array([((r["cards"][1].get("die") if r["cards"][1].get("die") is not None else np.nan) if len(r["cards"]) > 1 else np.nan) for r in rows], float),
            "held": np.array([any(c.get("held") for c in r["cards"]) for r in rows], float)}


def rm(h, k, a, b):
    q = (R[h]["t"] >= a) & (R[h]["t"] < b) & np.isfinite(R[h][k])
    return float(R[h][k][q].mean()) if q.any() else float("nan")


EV = (("the first, in H1", ep(5, 15), ep(5, 19), ep(5, 22), ep(5, 24)), ("the second, in H2", ep(5, 39), ep(5, 41), ep(5, 44), ep(5, 46)), ("the third, in H3's reduced phase", ep(6, 17), ep(6, 20), ep(6, 22), ep(6, 25)))
for nm, a0, a1, b0, b1 in EV:
    qa, qb = (t >= a0) & (t < a1), (t >= b0) & (t < b1)
    dS = S[qb].mean(axis=0) - S[qa].mean(axis=0)
    print(f"  {nm}, {clock(a0)[:5]}-{clock(a1)[:5]} to {clock(b0)[:5]}-{clock(b1)[:5]}: per sensor mean {dS.mean():+.3f} C, sd {dS.std(ddof=1):.3f}, {dS.min():+.3f} to {dS.max():+.3f}; board {P[qb].mean() - P[qa].mean():+.3f} W, the idle law's slope there x the move {np.polyval(np.polyder(law), T[qa].mean()) * dS.mean():.3f} W")
    for h in R:
        print(f"    {h}: CPU use {rm(h, 'cpu', a0, b1):.1f}% mean; NIC {rm(h, 'nic', b0, b1) - rm(h, 'nic', a0, a1):+.2f} C; NVMe {rm(h, 'nvme', b0, b1) - rm(h, 'nvme', a0, a1):+.2f} C; card 0 reading {rm(h, 'die0', b0, b1) - rm(h, 'die0', a0, a1):+.2f} C; held share {rm(h, 'held', a0, b1):.2f}")
q = (t >= ep(5, 14)) & (t < ep(5, 19))
sl, ic = np.polyfit(t[q] - ep(5, 14), T[q], 1)
print("  the first move's timing, 30 s bins: the die over a straight line through 05:14-05:19; aifoundry1's CPU use; the NICs")
for s in np.arange(ep(5, 19), ep(5, 24), 30):
    qq = (t >= s) & (t < s + 30)
    print(f"    {clock(s)} die {(T[qq] - (sl * (t[qq] - ep(5, 14)) + ic)).mean():+.3f} C; aifoundry1 CPU {rm('aifoundry1', 'cpu', s, s + 30):5.1f}%; NIC aifoundry1 {rm('aifoundry1', 'nic', s, s + 30):.2f} aifoundry2 {rm('aifoundry2', 'nic', s, s + 30):.2f} aifoundry3 {rm('aifoundry3', 'nic', s, s + 30):.2f}")
d = R["aifoundry1"]
qq = (d["t"] > ep(5, 15)) & (d["t"] < ep(5, 25))
print(f"  aifoundry1's burst: above 30% CPU {clock(d['t'][qq][d['cpu'][qq] > 30][0])}-{clock(d['t'][qq][d['cpu'][qq] > 30][-1])}, mean {d['cpu'][qq][d['cpu'][qq] > 30].mean():.1f}% ({d['cpu'][qq][d['cpu'][qq] > 30].mean() * 16 / 100:.1f} of 16 threads). Elsewhere in the session no minute reaches 10%: E97 README [bursts]; E104's README, item 5, says its accumulators ran on aifoundry1's CPU before its 05:37 claim")
for nm, a0, b0 in (("R0", rest["R0"]["t_end_ms"] / 1000 - 300, rest["R0"]["t_end_ms"] / 1000), ("R1", rest["R1"]["t_end_ms"] / 1000 - 300, rest["R1"]["t_end_ms"] / 1000), ("R2", rest["R2"]["t_end_ms"] / 1000 - 300, rest["R2"]["t_end_ms"] / 1000)):
    print(f"  the idle at the end of {nm}: {rest[nm]['idle_c']:.2f} C; a card held on aifoundry1 for {rm('aifoundry1', 'held', a0, b0):.2f} of its last 5 minutes, on aifoundry2 for {rm('aifoundry2', 'held', a0, b0):.2f}")
print(f"  aifoundry2's NIC at the first move, to its peak: {rm('aifoundry2', 'nic', ep(5, 15), ep(5, 19)):.2f} C at 05:15-05:19, {rm('aifoundry2', 'nic', ep(5, 25), ep(5, 27)):.2f} C at 05:25-05:27, {rm('aifoundry2', 'nic', ep(5, 25), ep(5, 27)) - rm('aifoundry2', 'nic', ep(5, 15), ep(5, 19)):+.2f} C")
qh = (R["aifoundry2"]["t"] >= ep(6, 0)) & (R["aifoundry2"]["t"] < ep(6, 22)) & (R["aifoundry2"]["held"] > 0)
print(f"  aifoundry2's card at the third move: held until {clock(R['aifoundry2']['t'][qh][-1])}, so its reading was falling from its own session and says nothing; at the first two nobody held it")
print("  three onsets in about 55 minutes of plateau (H1 from minute 10, H2, H3 from minute 10): one per about 18-22 minutes; a chance match within +-1 minute of a given time is about 2/20, roughly 1 in 10")
print()

print("[C3] the extrapolation by baseline: the 2 s rise over idle over S x 0.118")
z = {"fp32": B["f32zero"], "fp16": B["f16zero"]}
Z = {"line": {t_: z[t_]["step2"]["mean"] for t_ in z}, "quad": {t_: z[t_]["step2_quadratic_baseline"]["mean"] for t_ in z}, "gap": {t_: z[t_]["step2_gapfree_baseline"]["mean"] for t_ in z},
     "c0": {t_: z[t_]["step2"]["cycle0"] for t_ in z}}
for k in Z:
    Z[k]["int8"] = e["zeros_over_idle"]["int8"]["mean"]
rows = []
for b in LOW:
    x = B[b]
    ty = x["item"].split(".")[0]
    Sv = C[x["item"]]["S_W"]
    direct = x["ref"] == "idle"
    v = {"line": x["step2"]["mean"], "quad": x["step2_quadratic_baseline"]["mean"], "gap": x["step2_gapfree_baseline"]["mean"], "c0": x["step2"]["cycle0"]}
    r_ = {k: (v[k] + (0.0 if direct else Z[k][ty])) / (Sv * C78) for k in v}
    rows.append({"b": b, "ty": ty, "direct": direct, "real": x["item"].startswith("int8.real"), "S": Sv, **r_, "cell": {k: v[k] + (0.0 if direct else Z[k][ty]) for k in v}})
SEL = (("25 kinds", lambda r: not r["real"]), ("direct 14", lambda r: r["direct"]), ("float sums 6", lambda r: not r["direct"] and r["ty"] != "int8"), ("int8 sums 5", lambda r: not r["direct"] and r["ty"] == "int8" and not r["real"]), ("tiles 3", lambda r: r["real"]))
print("  | cells | E89's line, median (range) | quadratic | line over [-8, -2) s | cycle 0 on E89's line |")
for nm, sel in SEL:
    cells = []
    for k in ("line", "quad", "gap", "c0"):
        vals = [r[k] for r in rows if sel(r)]
        cells.append(f"{statistics.median(vals):.3f} ({min(vals):.3f}-{max(vals):.3f})")
    print(f"  | {nm} | " + " | ".join(cells) + " |")
for k in ("line", "quad", "gap", "c0"):
    vals = [r[k] for r in rows if not r["real"]]
    print(f"  E97-R7 on baseline {k}: median {statistics.median(vals):.3f} inside [1.00, 1.20]: {1.0 <= statistics.median(vals) <= 1.2}; share in [0.85, 1.30] {np.mean([0.85 <= v <= 1.30 for v in vals]):.2f}")
qq = [B[b]["step2_quadratic_baseline"]["mean"] / B[b]["step2"]["mean"] for b in LOW if B[b]["ref"] == "idle"]
fs = [r for r in rows if not r["direct"] and r["ty"] != "int8"]
print("  float sums, E89's line over the other baselines, median: " + ", ".join(f"{k} {statistics.median([r['line'] / r[k] for r in fs]):.3f}" for k in ("quad", "gap", "c0")))
print(f"  direct cells, the quadratic over E89's line: {min(qq):.3f}-{max(qq):.3f}, mean {np.mean(qq):.3f}")
print("  the nulls: the first launch of a block's lead-in, on all three baselines, where the zeros on both sides of the boundary are the same; and idle to zeros, the zeros' rise over idle")
P_A = {p: load(p) for p in ("p9710", "p9711")}
tr = []
for p, a_ in P_A.items():
    tt, TT = a_["t"], a_["T"]
    bl = [m for m in a_["marks"] if m["kind"] == "block"]
    byh = {}
    for r in a_["runs"]:
        byh.setdefault((r["block"], r["half"]), []).append(r)
    for i in range(1, len(bl)):
        u, v = bl[i - 1], bl[i]
        if v["ref"] == "idle":
            continue
        hl = [h for h in a_["marks"] if h["kind"] == "half" and h["block"] == v["block"] and h["role"] == "lead" and v["t_start_ms"] - 1000 <= h["t_start_ms"] <= v["t_end_ms"]]
        qr = byh.get((v["block"], hl[0]["half"])) if hl else None
        if not qr:
            continue
        s0 = min(r["t_start_ms"] for r in qr) / 1000
        post = TT[(tt >= s0 + 1) & (tt < s0 + 3)].mean()
        m1 = (tt >= s0 - 5) & (tt < s0 - 0.2)
        m2 = (tt >= s0 - 20) & (tt < s0 - 0.2)
        m3 = (tt >= s0 - 8) & (tt < s0 - 2)
        tr.append({"prev": u["ref"], "cur": v["ref"], "line": post - np.polyfit(tt[m1] - (s0 + 2), TT[m1], 1)[1], "quad": post - np.polyfit(tt[m2] - (s0 + 2), TT[m2], 2)[2], "gap": post - np.polyfit(tt[m3] - (s0 + 2), TT[m3], 1)[1]})
agg = {}
for x in tr:
    agg.setdefault((x["prev"], x["cur"]), []).append(x)
for k, v in sorted(agg.items()):
    if k[0] == k[1] or k[0] == "idle":
        print(f"    {k[0]} to {k[1]}, n = {len(v)}: E89's line {np.mean([y['line'] for y in v]):+.3f} C, quadratic {np.mean([y['quad'] for y in v]):+.3f}, line over [-8, -2) s {np.mean([y['gap'] for y in v]):+.3f}" +
              (f"; sd of E89's line {np.std([y['line'] for y in v], ddof=1):.3f}, 95% +-{2.447 * np.std([y['line'] for y in v], ddof=1) / math.sqrt(len(v)):.3f}" if len(v) > 2 else ""))
print(f"    the zeros' rises over idle measured in blocks: fp32 {B['f32zero']['step2']['mean']:.3f}, fp16 {B['f16zero']['step2']['mean']:.3f} C (this run); int8 {e['zeros_over_idle']['int8']['mean']:.3f} +- {e['zeros_over_idle']['int8']['ci95']:.3f} (E89)")
print("  the hold starts: a direct 2 s rise from a rested die, by the registered method")
for name, Sv in (("H1", Hs["H1"]["steady"]["S_E78_W"]), ("H3", Hs["H3"]["steady"]["S_E78_W"])):
    rr = sorted([r for r in runs if r["block"] == name], key=lambda r: r["t_start_ms"])
    s0 = rr[0]["t_start_ms"] / 1000
    post = T[(t >= s0 + 1) & (t < s0 + 3)].mean()
    m1 = (t >= s0 - 5) & (t < s0 - 0.2)
    m2 = (t >= s0 - 20) & (t < s0 - 0.2)
    ln = post - np.polyfit(t[m1] - (s0 + 2), T[m1], 1)[1]
    qd = post - np.polyfit(t[m2] - (s0 + 2), T[m2], 2)[2]
    print(f"    {name} {Hs[name]['item']}: E89's line {ln:.3f} C, quadratic {qd:.3f} C, S x 0.118 {Sv * C78:.3f} C, ratio {ln / (Sv * C78):.3f}")
b = rest["R0"]["t_end_ms"] / 1000
vals = []
for s in np.arange(b - 300, b - 4, 3.0):
    m1 = (t >= s - 5) & (t < s - 0.2)
    vals.append(T[(t >= s + 1) & (t < s + 3)].mean() - np.polyfit(t[m1] - (s + 2), T[m1], 1)[1])
print(f"    the method's null at rest, the last 5 minutes of R0, {len(vals)} starts with no launch: mean {np.mean(vals):+.3f} C, sd {np.std(vals):.3f}")
print(f"    E89's int8 full, a sum: {e['zeros_over_idle']['int8']['mean'] + 0.8630:.2f} C (0.863 + 0.340, E89 README); this run's fp32 random, a sum on E89's line: {B['f32randn']['step2']['mean'] + B['f32zero']['step2']['mean']:.3f} C, on the quadratic {B['f32randn']['step2_quadratic_baseline']['mean'] + B['f32zero']['step2_quadratic_baseline']['mean']:.3f} C; E78 measured 3.16 +- 0.08 C")
for k, lab in (("line", "E89's line"), ("c0", "cycle 0"), ("quad", "quadratic")):
    Sx = np.array([r["S"] for r in rows if not r["real"]])
    yy = np.array([r["cell"][k] for r in rows if not r["real"]])
    cf = np.polyfit(Sx, yy, 1)
    print(f"  cell against S over the 25 kinds, {lab}: {cf[1]:+.3f} C + {cf[0]:.4f} per W of S")
print(f"  additivity at low S: int8 ones, direct, {B['i8ones']['step2']['mean']:.3f} C at S {C['int8.ones']['S_W']:.2f} W; E89's int8 -1, a sum, 0.56 C at S 4.18 W (E89 README)")
print()

print("[C4] E97-B5 against the wander")
s1_, s3_ = Hs["H1"]["steady"], Hs["H3"]["steady"]
r_ = s3_["rise_per_S_eff"] / s1_["rise_per_S_eff"]
rel = math.hypot(0.4 / s1_["dT"], 0.4 / s3_["dT"])
print(f"  rise per W of S x share, H3 over H1: {r_:.3f}; at +-0.4 C on each rise [{r_ * (1 - rel):.3f}, {r_ * (1 + rel):.3f}] (band [1.02, 1.25]); from the leak shares alone {(1 / (1 - Hs['H3']['leak']['share_of_dP'])) / (1 / (1 - Hs['H1']['leak']['share_of_dP'])):.3f}")
print()

print("[C5] what E97-R2 can say with the pass as the unit")
Hr = B["f32randn"]["H_by_pass"]
se = abs(Hr[0] - Hr[1]) / 2 / np.mean(Hr)
hw = T1 * se
print(f"  H_ref by pass {Hr[0]:.4f}, {Hr[1]:.4f}: relative half-width at t = 12.706 alone {hw:.3f}; so a cell can PASS only if r <= {1.25 / (1 + hw):.3f}, FAIL only if r > {1.25 / (1 - hw):.3f} or r < {0.80 / (1 + hw):.3f}")
ps = [(v["cell"], v["measured"]["r"]) for v in sc["verdicts"] if v["rule"] == "E97-R2" and v["unit"] == "pass" and v["verdict"] == "PASS"]
inc = [(v["cell"], v["measured"]["r"]) for v in sc["verdicts"] if v["rule"] == "E97-R2" and v["unit"] == "pass" and v["verdict"] == "INCONCLUSIVE"]
print(f"  the six PASS cells: {[(a_, round(b_, 3)) for a_, b_ in ps]}, frames {sorted(set(B[a_]['ref'] for a_, _ in ps))}; every against-idle cell: {sorted(set(v for a_, v_ in inc for v in [('INCONCLUSIVE' if B[a_]['ref'] == 'idle' else None)] if v))}, r {min(B[b_]['r_board_pass']['r'] for b_ in LOW if B[b_]['ref'] == 'idle'):.3f}-{max(B[b_]['r_board_pass']['r'] for b_ in LOW if B[b_]['ref'] == 'idle'):.3f}")
print(f"  the reference on the minion rail by pass: {B['f32randn']['Hm_by_pass'][0]:.4f}, {B['f32randn']['Hm_by_pass'][1]:.4f}")
print()

print("[C6] leakage's labels, and the law's form")
rail = Pm + Ps + Pn
qr = np.zeros(len(t), bool)
for r in rest.values():
    qr |= (t >= r["t_start_ms"] / 1000 + 20) & (t < r["t_end_ms"] / 1000)
bins = np.floor(T[qr] / 0.5).astype(int)
bx, bp, br = [], [], []
for i in np.unique(bins):
    q = bins == i
    if q.sum() >= 20:
        bx.append(T[qr][q].mean())
        bp.append(P[qr][q].mean())
        br.append(rail[qr][q].mean())
bx, bp, br = np.array(bx), np.array(bp), np.array(br)
print(f"  reproduces the pooled law: quadratic coefficients {np.round(np.polyfit(bx, bp, 2), 5).tolist()} against e97.json {np.round(law, 5).tolist()}; top bin {bx.max():.2f} C")
lr = np.polyfit(bx, br, 2)
for name in Hs:
    st = Hs[name]["steady"]
    bT, _ = baseline(name)
    Tid = bT(hold[name]["t_end_ms"] / 1000 - 150)
    dl = np.polyval(law, st["T_mean"]) - np.polyval(law, Tid)
    drl = np.polyval(lr, st["T_mean"]) - np.polyval(lr, Tid)
    print(f"  {name}: leakage's part {dl:.2f} W of the board's {st['dP']:.2f} W rise over idle (share {dl / st['dP']:.3f}); on the three die rails {drl:.2f} W, off them {dl - drl:.2f} W")


def form_slope(x):
    out = {}
    out["quadratic, pooled"] = np.polyval(np.polyder(law), x)
    out["cubic, pooled"] = np.polyval(np.polyder(np.polyfit(bx, bp, 3)), x)
    best = None
    for th in np.arange(14, 80, 1.0):
        X = np.column_stack([np.ones_like(bx), np.exp(bx / th)])
        co, *_ = np.linalg.lstsq(X, bp, rcond=None)
        res = float(np.sum((bp - X @ co) ** 2))
        if best is None or res < best[0]:
            best = (res, th, co)
    out["exponential, pooled"] = best[2][1] / best[1] * math.exp(x / best[1])
    for rn in rest:
        qq_ = (t >= rest[rn]["t_start_ms"] / 1000 + 20) & (t < rest[rn]["t_end_ms"] / 1000)
        b_ = np.floor(T[qq_] / 0.5).astype(int)
        xs = np.array([T[qq_][b_ == i].mean() for i in np.unique(b_) if (b_ == i).sum() >= 20])
        ys = np.array([P[qq_][b_ == i].mean() for i in np.unique(b_) if (b_ == i).sum() >= 20])
        out[f"quadratic, {rn} alone"] = np.polyval(np.polyder(np.polyfit(xs, ys, 2)), x)
    out["straight line, pooled"] = np.polyfit(bx, bp, 1)[0]
    return out


for name in Hs:
    st = Hs[name]["steady"]
    f = form_slope(st["T_mean"])
    print(f"  {name} at {st['T_mean']:.1f} C: loop gain by the law's form: " + ", ".join(f"{k} {v * st['R_ol']:.2f}" for k, v in f.items()))
f = form_slope(65.5)
print(f"  at 65.5 C on 0.90 C per board W: " + ", ".join(f"{k} {v * 0.90:.2f}" for k, v in f.items()))
best = None
for th in np.arange(14, 80, 1.0):
    X = np.column_stack([np.ones_like(bx), np.exp(bx / th)])
    co, *_ = np.linalg.lstsq(X, bp, rcond=None)
    res = float(np.sum((bp - X @ co) ** 2))
    if best is None or res < best[0]:
        best = (res, th, co)
for R_ in (0.87, 0.90, 0.92):
    Tq = (1 / R_ - law[1]) / (2 * law[0])
    Te = best[1] * math.log((1 / R_) * best[1] / best[2][1])
    print(f"  loop gain 1 at {R_:.2f} C per board W: {Tq:.0f} C on the quadratic law, {Te:.0f} C on the exponential (scale {best[1]:.0f} C); no idle reading above {bx.max():.1f} C, none under load above {T.max():.1f} C")
print(f"  the idle law's slope: {np.polyval(np.polyder(law), 62.0):.3f} W/C at 62 C, {np.polyval(np.polyder(law), 65.5):.3f} at 65.5 C, {np.polyval(np.polyder(law), 70.0):.3f} at 70 C (carried past the top bin)")
for name in Hs:
    x = Hs[name]
    t0, t1_ = hold[name]["t_start_ms"] / 1000, hold[name]["t_end_ms"] / 1000
    rr = [r for r in runs if r["block"] == name]
    row = []
    start = t0 if name != "H3" else t0 + 300
    for s in np.arange(start, t1_ - 299, 300):
        on = sum(max(0, min(r["t_end_ms"] / 1000, s + 300) - max(r["t_start_ms"] / 1000, s)) for r in rr) / 300
        q = (t >= s) & (t < s + 300)
        row.append((P[q] - np.polyval(law, T[q])).mean() / (x["steady"]["S_E78_W"] * on))
    print(f"  {name}: closure in each 300 s window {min(row):.3f}-{max(row):.3f}; the registered {x['leak']['closure']:.3f}")
t0 = hold["H1"]["t_start_ms"] / 1000
q = (t >= t0 + 600) & (t < t0 + 1800)
tb = np.floor((t[q] - t0) / 30)
xs = np.array([T[q][tb == i].mean() for i in np.unique(tb)])
ys = np.array([P[q][tb == i].mean() for i in np.unique(tb)])
cf, cv = np.polyfit(xs, ys, 1, cov=True)
print(f"  k under load, from H1's own wander (30 s bins, 600-1800 s): {cf[0]:.3f} +- {math.sqrt(cv[0, 0]):.3f} W/C (se) over {xs.max() - xs.min():.2f} C; the idle law at 62.8 C {np.polyval(np.polyder(law), 62.8):.3f}")
ph = [m for m in marks if m["kind"] == "phase" and m["hold"] == "H3" and m["phase"] == "reduced"][0]["t_ms"] / 1000
ls = sorted([m for m in marks if m["kind"] == "launch" and m["block"] == "H3" and m["t_start_ms"] / 1000 >= ph + 300], key=lambda m: m["t_start_ms"])
on_, gap_, gapT = [], [], []
for u, v in zip(ls, ls[1:]):
    qo = (t >= u["t_start_ms"] / 1000 + 1.5) & (t < u["t_end_ms"] / 1000 - 0.3)
    qg = (t >= v["t_start_ms"] / 1000 - 1.5) & (t < v["t_start_ms"] / 1000)
    if qo.sum() >= 5:
        on_.append((P[qo] - np.polyval(law, T[qo])).mean())
    if qg.sum() >= 5:
        gap_.append((P[qg] - np.polyval(law, T[qg])).mean())
        gapT.append(T[qg].mean())
print(f"  H3's reduced phase from 5 minutes in, {len(on_)} launches: board minus the idle law while a kernel runs {np.mean(on_):.2f} W, against E78's S {Hs['H3']['steady']['S_E78_W']:.2f} W; in the gaps' last 1.5 s {np.mean(gap_):+.3f} W at a die of {min(gapT):.1f}-{max(gapT):.1f} C")
for nm in ("e78.json", "e78-leak0.3803.json", "e78-leak0.json"):
    j = json.load(open(os.path.join(DATA, "2026-10-31-e78-kinds-energy-matrix", nm)))
    print(f"  E78's fp32 random S in {nm}: {j['items']['fp32.randn']['S']['mean']:.2f} W (slope {j.get('leak', {}).get('k_w_per_c')})")
print()

print("[C7] H3 is another operating point; per die-rail W")
t1_ = hold["H3"]["t_end_ms"] / 1000
q = (t >= t1_ - 300) & (t < t1_)
print(f"  H3's last 300 s: a 7 s square wave: board {P[q].min():.1f}-{P[q].max():.1f} W, die mean {T[q].min():.1f}-{T[q].max():.1f} C, compute share {Hs['H3']['steady']['compute_share']:.2f}, after a peak of {T[(t >= hold['H3']['t_start_ms'] / 1000) & (t < t1_)].max():.2f} C; {Hs['H3']['steady']['T_mean'] - Hs['H1']['steady']['T_mean']:.1f} C above H1's window")
for name in Hs:
    st = Hs[name]["steady"]
    die = st["dPm"] + st["dPs"] + st["dPn"]
    print(f"  {name}: die rails {die:.2f} W of {st['dP']:.2f} W; off the rails {st['dP'] - die:.2f} W ({(st['dP'] - die) / st['dP']:.3f}); rise per board W {st['R_ol']:.3f}, per die-rail W {st['dT'] / die:.3f}")
print()

print("[C8] smaller items")
print("  the three int8 tiles, 2 s rise over idle per W of S, E89's line: " + ", ".join(f"{k[10:]} {C[k]['per_W_of_S']:.3f}" for k in C if k.startswith("int8.real")))
pre = wm(T, t0 + 660, t0 + 930) - baseline("H1")[0](t0 + 795)
print(f"  H1 at 10 min: {Hs['H1']['curve']['600']['dT']:.2f} C, {Hs['H1']['curve']['600']['dT'] / pre:.3f} of the plateau before its first move ({pre:.2f} C)")
rm_ = sorted((B[b]["r_minion_pass"]["r"], b) for b in LOW)
print(f"  r per minion-rail W, points: {rm_[0][0]:.4f}-{rm_[-1][0]:.4f}; beyond +-5%: {[(b, round(v, 4)) for v, b in rm_ if abs(v - 1) > 0.05]}; beyond +-7%: {[(b, round(v, 4)) for v, b in rm_ if abs(v - 1) > 0.07]}")
E89 = json.load(open(os.path.join(DATA, "2026-10-31-e89-heat-low-power", "e89.json")))["blocks"]
s89 = {b: E89[b]["step2_C"]["mean"] for b in ("i8full", "i8gauss", "i8small", "i8sp50", "i8neg1", "f32ones")}
sums89 = {b: v + (e["zeros_over_idle"]["int8"]["mean"] if b.startswith("i8") else B["f32zero"]["step2"]["mean"]) for b, v in s89.items()}
d_all = [C[B[b]["item"]]["cell_C"] for b in LOW if B[b]["ref"] == "idle"] + [e["zeros_over_idle"]["int8"]["mean"]]
s_all = [C[B[b]["item"]]["cell_C"] for b in LOW if B[b]["ref"] != "idle" and not B[b]["item"].startswith("int8.real")] + list(sums89.values())
print(f"  all 32 kinds below 12 W: {len(d_all)} read directly, {min(d_all):.2f}-{max(d_all):.2f} C; {len(s_all)} sums, {min(s_all):.2f}-{max(s_all):.2f} C; E89's sums on this run's zeros: " + ", ".join(f"{b} {v:.2f}" for b, v in sums89.items()))
rat = sorted((B[b]["step2"]["ci95_pass"] / B[b]["step2"]["ci95_lap"], b) for b in LOW)
print(f"  the rise's pass-level +- over its lap-level +-: {rat[0][0]:.2f} ({rat[0][1]}) to {rat[-1][0]:.2f} ({rat[-1][1]}), median {statistics.median([x[0] for x in rat]):.2f}; int8 wsparse50 lap {B['i8wsp50']['step2']['ci95_lap']:.3f}, pass {B['i8wsp50']['step2']['ci95_pass']:.3f}")
print("  the board's total at the stop: 63.1-63.4 W, 40 W above idle; H3's reduced phase, 22.49 W over idle")
print("  the heat column's lap-unit +- against the pass-unit: largest pass-unit half-widths " + ", ".join(f"{b} {B[b]['step2']['ci95_pass']:.3f}" for b in sorted(LOW, key=lambda b: -B[b]["step2"]["ci95_pass"])[:4]) + f"; int8 sorted lap {B['i8sort']['step2']['ci95_lap']:.3f}, pass {B['i8sort']['step2']['ci95_pass']:.3f}")
print()

print("[C9] the die's arrival and the frames")
sh = Hs["H1"]["shares"]
print("  H1, shares of its registered rise: " + ", ".join(f"{k} s {sh[k]:.2f}" for k in ("10", "30", "60", "120", "300", "600")))
print(f"  E73's 0.25-0.30 C/W against about 0.9 on the die: {0.25 / 0.9:.2f}-{0.30 / 0.9:.2f}. S x 0.9 on int8 full gives {Hs['H1']['steady']['S_E78_W'] * 0.9:.1f} C for {Hs['H1']['steady']['dT']:.1f}: per board W has the leakage in its denominator; per W of S x share is {Hs['H1']['steady']['rise_per_S_eff']:.2f}-{Hs['H2']['steady']['rise_per_S_eff']:.2f}")
print(f"  at 60 s, rise per board W: H1 {Hs['H1']['curve']['60']['dT'] / Hs['H1']['curve']['60']['dP']:.3f}, H3 natural {Hs['H3']['curve']['60']['dT'] / Hs['H3']['curve']['60']['dP']:.3f}")
