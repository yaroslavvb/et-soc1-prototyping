#!/usr/bin/env python3
"""Q139(q), corrections after verification (Tue 3 Nov 2026), POST HOC: the numbers the README's corrections C1-C7 cite.

Computed with G3's committed code (g3_model.py, unchanged) on the same 56 sustained runs of E119, E126, E136 and E146 (posthoc-g3-inputs.json,
posthoc-g3.json, fit-g3.json), and, for the leakage slope, the gap share and the sensitivities, on those sessions' committed telemetry read the
way posthoc_g3.py reads it. Nothing frozen for E159 is read differently and nothing is refitted: G3's constants stay 0.1 W per C and 65.5 C.

    python3 posthoc_fix_g3.py > posthoc-fix-g3.txt      (writes posthoc-fix-g3.json; about a minute)

  (1) every arm per run, and 95% bootstrap intervals on the rms (C6);
  (2) the subsets (the 14 large GEMMs, the 42 GEMM-pattern arms) and F6 out of sample (C2);
  (3) the chain on the measured trace: the count inside 1 C (C5);
  (4) P0's first-second bias, and G3 given each run's first second at both constant sets and on a k grid (C1);
  (5) the board's slope on the die inside runs at a fixed 800 MHz (C1);
  (6) the sensitivities to the choices no lane registered, and the gap share on the model's own kernel mask (C3);
  (7) E159's levels beside the shapes G3 was scored on (C7).
err = measured - predicted throughout.
"""
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g3_model as G  # noqa: E402
import posthoc_g3 as PH  # noqa: E402  (its session list, loaders and level rules; its main() is not run)

RULE = {"mhz": 15.0, "w": 2.0, "die": 1.0}
QS = ("mhz", "w", "die")
SESS = ("E119", "E126", "E136", "E146")
LARGE = ("E136", "E146")
NBOOT = 10000
SEED = 20261103
INP = json.load(open(os.path.join(HERE, "posthoc-g3-inputs.json")))
PHJ = json.load(open(os.path.join(HERE, "posthoc-g3.json")))
FIT = json.load(open(os.path.join(HERE, "fit-g3.json")))
PRED = json.load(open(os.path.join(HERE, "predictions-e159.json")))
ROWS = PHJ["runs"]
assert len(ROWS) == len(INP) == 56
assert all(r["run"] == c["run"] and r["session"] == c["session"] and r["cell"] == c["cell"] for r, c in zip(ROWS, INP))
K_FIN, TRIP_FIN = FIT["final"]["k_leak"], FIT["final"]["trip_C"]
assert (K_FIN, TRIP_FIN) == (G.K_LEAK_G3, G.TRIP_G3)
NESTED = {s: (FIT["nested"][s]["chosen_on_others"]["k_leak"], FIT["nested"][s]["chosen_on_others"]["trip_C"]) for s in SESS}


def lev_of(c):
    return {int(f): v for f, v in c["lev"].items()}


def sim(c, k, trip, p_scale=1.0, last_s=G.SUS_LAST_S):
    on = np.asarray(c["on"], bool)
    gg = c["gg0"] + np.arange(len(on)) * G.DT
    T, P, F = G.simulate(lev_of(c), on, np.asarray(c["x0"], float), c["anc"], T_start=c["T_start"], trip=trip, k_leak=k, p_scale=p_scale)
    return G.window_means(gg, on, T, P, F, c["t1"], last_s=last_s)


def err(meas, pred):
    return {q: meas[q] - pred[q] for q in pred if q in meas}


def stats(E, q):
    e = np.array([x[q] for x in E if x is not None and q in x], float)
    if not len(e):
        return None
    return {"n": int(len(e)), "rms": round(float(np.sqrt(np.mean(e ** 2))), 3), "mean": round(float(np.mean(e)), 3),
            "inside": int(np.sum(np.abs(e) <= RULE[q])), "max_abs": round(float(np.max(np.abs(e))), 3)}


def rms(a):
    return float(np.sqrt(np.mean(np.square(a))))


def pct(a):
    return [round(float(np.percentile(a, 2.5)), 3), round(float(np.percentile(a, 97.5)), 3)]


def fmt(s):
    return "—" if s is None else f"{s['rms']:7.3f} ({s['mean']:+7.3f}) in {s['inside']:2d}/{s['n']}"


OUT = {"what": "Q139(q) corrections after verification, post hoc: the numbers C1-C7 cite (G3's committed code, unchanged)",
       "date": "2026-11-03", "constants": {"G3": [K_FIN, TRIP_FIN], "Q138t": [G.K_LEAK, G.T_TRIP], "nested_choices": {s: list(v) for s, v in NESTED.items()}},
       "bootstrap": {"n": NBOOT, "seed": SEED, "kind": "percentile, 95%"}}

# ---------------------------------------------------------------- (1) every arm per run, and the intervals (C6)
PR = []
for c, r in zip(INP, ROWS):
    m = c["meas"]
    kN, tN = NESTED[c["session"]]
    pred = {"G3_nested": sim(c, kN, tN), "G3_final": sim(c, K_FIN, TRIP_FIN), "G3_q138t": sim(c, G.K_LEAK, G.T_TRIP), "E136_law": r["E136_law"]}
    e = {a: err(m, p) for a, p in pred.items()}
    e["chain"] = {"die": m["die"] - r["chain_on_measured_die"]}
    PR.append({"session": c["session"], "run": c["run"], "cell": c["cell"], "meas": m, "pred": pred, "err": e})
ARMS = ("G3_nested", "G3_final", "G3_q138t", "E136_law", "chain")
chk = {q: stats([x["err"]["G3_nested"] for x in PR], q) for q in QS}
for q in QS:
    assert abs(chk[q]["rms"] - FIT["nested_pooled"][q]["rms"]) < 2e-3, (q, chk[q], FIT["nested_pooled"][q])
print("Q139(q) corrections after verification, POST HOC. G3's committed code, unchanged; err = measured - predicted.")
print(f"(0) G3 nested reproduces fit-g3.json nested_pooled: {[(q, chk[q]['rms']) for q in QS]}")

rng = np.random.default_rng(SEED)
n = len(PR)
ARR = {a: {q: np.array([x["err"][a][q] for x in PR if q in x["err"][a]], float) for q in QS} for a in ARMS}
I = rng.integers(0, n, size=(NBOOT, n))
iv = {}
for a in ("G3_nested", "G3_final", "G3_q138t", "E136_law"):
    iv[f"{a}.over_runs"] = {q: pct(np.sqrt(np.mean(ARR[a][q][I] ** 2, axis=1))) for q in QS}
iv["chain.over_runs"] = {"die": pct(np.sqrt(np.mean(ARR["chain"]["die"][I] ** 2, axis=1)))}
iv["E136_law_minus_G3_nested.paired_over_runs"] = {
    q: pct(np.sqrt(np.mean(ARR["E136_law"][q][I] ** 2, axis=1)) - np.sqrt(np.mean(ARR["G3_nested"][q][I] ** 2, axis=1))) for q in QS}
grp = [np.array([i for i, x in enumerate(PR) if x["session"] == s]) for s in SESS]
J = rng.integers(0, len(SESS), size=(NBOOT, len(SESS)))
for a in ("G3_nested", "E136_law"):
    vals = {q: np.empty(NBOOT) for q in QS}
    for b, j in enumerate(J):
        ii = np.concatenate([grp[k] for k in j])
        for q in QS:
            vals[q][b] = rms(ARR[a][q][ii])
    iv[f"{a}.over_sessions"] = {q: pct(vals[q]) for q in QS}
large_idx = np.array([i for i, x in enumerate(PR) if x["session"] in LARGE])
IL = rng.integers(0, len(large_idx), size=(NBOOT, len(large_idx)))
for a in ("G3_nested", "E136_law"):
    iv[f"{a}.large_gemms_over_runs"] = {q: pct(np.sqrt(np.mean(ARR[a][q][large_idx][IL] ** 2, axis=1))) for q in QS}
iv["E136_law_minus_G3_nested.paired_large_gemms_over_runs"] = {
    q: pct(np.sqrt(np.mean(ARR["E136_law"][q][large_idx][IL] ** 2, axis=1)) - np.sqrt(np.mean(ARR["G3_nested"][q][large_idx][IL] ** 2, axis=1))) for q in QS}
OUT["intervals"] = iv
print(f"\n(1) 95% bootstrap intervals on the rms ({NBOOT} resamples, seed {SEED}); over runs = the 56 runs resampled, over sessions = the four "
      "sessions resampled as clusters; paired = the law's rms minus G3 nested's on the same resample (positive: G3 better)")
for k, v in iv.items():
    print(f"   {k:46s} " + "  ".join(f"{q} [{v[q][0]:.3f}, {v[q][1]:.3f}]" for q in v))

# ---------------------------------------------------------------- (2) the subsets and F6 out of sample (C2)
GROUPS = {"all": PR, "large_gemms_E136_E146": [x for x in PR if x["session"] in LARGE],
          "gemm_pattern_arms_E119_E126": [x for x in PR if x["session"] not in LARGE]}
OUT["subsets"] = {}
print("\n(2) by subset: rms (mean) inside/n per quantity; the rules are 15 MHz, 2 W and 1 C")
for gname, rows in GROUPS.items():
    st = {a: {q: stats([x["err"][a] for x in rows], q) for q in QS} for a in ARMS}
    OUT["subsets"][gname] = {"n": len(rows), "stats": st}
    print(f"  {gname} (n {len(rows)})")
    for a in ARMS:
        print(f"    {a:10s} clock {fmt(st[a]['mhz'])}   board {fmt(st[a]['w'])}   die {fmt(st[a]['die'])}")
f6 = {}
print("  F6 (E146 R5's shape): measured | G3 nested (E146 held out: k %.1f, trip %.1f) | G3 final | G3 at Q138(t)'s constants | E136's law" % NESTED["E146"])
for x in PR:
    if x["cell"].startswith("F6"):
        f6[x["cell"]] = {"meas": x["meas"], **{a: {q: round(float(x["pred"][a][q]), 2) for q in QS} for a in ("G3_nested", "G3_final", "G3_q138t", "E136_law")},
                         "err_G3_nested": {q: round(float(x["err"]["G3_nested"][q]), 2) for q in QS},
                         "err_G3_final": {q: round(float(x["err"]["G3_final"][q]), 2) for q in QS}}
        d = f6[x["cell"]]
        print(f"    {x['cell']:14s} " + " | ".join(f"{d[a]['mhz']:6.1f} {d[a]['w']:6.2f} {d[a]['die']:6.2f}" for a in ("meas", "G3_nested", "G3_final", "G3_q138t", "E136_law"))
              + f"   err nested {d['err_G3_nested']}")
OUT["F6"] = f6
g2k = [x for x in PR if x["session"] == "E136" and x["cell"].startswith("g2k")]
OUT["g2k_in_fit_set"] = {x["cell"]: {"meas": x["meas"], "G3_final": {q: round(float(x["pred"]["G3_final"][q]), 2) for q in QS},
                                     "err_G3_final": {q: round(float(x["err"]["G3_final"][q]), 2) for q in QS}} for x in g2k}
for x in g2k:
    print(f"    E136 {x['cell']:14s} measured {x['meas']['mhz']:6.1f} MHz; G3 final {x['pred']['G3_final']['mhz']:6.1f} MHz (err {x['err']['G3_final']['mhz']:+.1f})")

# ---------------------------------------------------------------- (3) the chain's count (C5)
cs = OUT["subsets"]["all"]["stats"]["chain"]["die"]
OUT["chain_on_measured"] = {"anchor": "each run anchored on the measured die over the 20 s before its first process (G3's own anchor)", **cs}
print(f"\n(3) the chain on the measured trace, 20 s pre-run anchor: rms {cs['rms']} C, inside 1 C {cs['inside']} of {cs['n']}, largest |err| {cs['max_abs']} C")

# ---------------------------------------------------------------- (4) P0's first-second bias and the p800 diagnostic (C1)
bias = {}
for s in SESS + ("all",):
    b = np.array([r["p800_meas"] - lev_of(c)[800] for c, r in zip(INP, ROWS) if r["p800_meas"] is not None and (s == "all" or c["session"] == s)])
    bias[s] = {"n": int(len(b)), "mean": round(float(b.mean()), 3), "rms": round(rms(b), 3), "min": round(float(b.min()), 2), "max": round(float(b.max()), 2)}
OUT["P0_first_second_bias_W"] = bias
rise = np.array([r["meas"]["die"] - c["T_start"] for c, r in zip(INP, ROWS)])
OUT["die_rise_start_to_window_C"] = {"mean": round(float(rise.mean()), 3), "median": round(float(np.median(rise)), 3),
                                     "level_gap_at_window_W": round(float((G.K_LEAK - K_FIN) * rise.mean()), 3),
                                     "what": "measured window die minus the chain's die at the run's start; (0.442 - 0.1) x the mean is how far G3's raised "
                                             "level sits under P0 + 0.442 x the rise at the window"}
print("\n(4) P0's first-second level bias, p800 (the run's own first second at 800 MHz, reduce_hpl's) - P0(800), W:")
for s, v in bias.items():
    print(f"   {s:5s} n {v['n']:2d}  mean {v['mean']:+.2f}  rms {v['rms']:.2f}  min {v['min']:+.2f}  max {v['max']:+.2f}")
dr = OUT["die_rise_start_to_window_C"]
print(f"   the die's rise from the run's start to its window: mean {dr['mean']:.2f} C (median {dr['median']:.2f}); at k 0.1 instead of 0.442 the raised "
      f"level sits {dr['level_gap_at_window_W']:.2f} W under P0 + 0.442 x the rise there, against P0's {bias['all']['mean']:+.2f} W mean over-read")
GRID = ((0.0, 65.5), (0.1, 65.5), (0.2, 65.5), (0.3, 65.5), (0.442, 65.5), (0.1, 65.9), (0.2, 65.9), (0.3, 65.9), (0.442, 65.9))
p8 = {}
print("   G3 with P0's level as given (no p800) against G3 given each run's first second (levels scaled to p800), all 56 runs, in sample:")
for k, tr in GRID:
    Eg = [err(c["meas"], sim(c, k, tr)) for c in INP]
    Ep = [err(c["meas"], sim(c, k, tr, p_scale=r["p800_meas"] / lev_of(c)[800])) for c, r in zip(INP, ROWS) if r["p800_meas"]]
    p8[f"{k}|{tr}"] = {"G3": {q: stats(Eg, q) for q in QS}, "G3_given_p800": {q: stats(Ep, q) for q in QS}}
    a, b = p8[f"{k}|{tr}"]["G3"], p8[f"{k}|{tr}"]["G3_given_p800"]
    print(f"   k {k:5.3f} trip {tr:4.1f}: as given clock {a['mhz']['rms']:6.2f} ({a['mhz']['mean']:+6.2f}) board {a['w']['rms']:5.2f} ({a['w']['mean']:+5.2f}) "
          f"die {a['die']['rms']:5.2f} ({a['die']['mean']:+5.2f}) | given p800 clock {b['mhz']['rms']:6.2f} ({b['mhz']['mean']:+6.2f}) board {b['w']['rms']:5.2f} "
          f"({b['w']['mean']:+5.2f}) die {b['die']['rms']:5.2f} ({b['die']['mean']:+5.2f})  n {b['mhz']['n']}")
ref = PHJ["sessions"]["all"]["stats"]
for q in QS:
    assert abs(p8["0.442|65.9"]["G3_given_p800"][q]["rms"] - ref[f"G3_given_p800.{q}"]["rms"]) < 2e-3, q
print("   (the 0.442 / 65.9 row is posthoc-g3.json's G3_given_p800, the README's first diagnostic row; 0.1 / 65.5 is G3's own constants)")
OUT["p800_diagnostic"] = p8

# ---------------------------------------------------------------- telemetry, read as posthoc_g3.py reads it
SD = {}
for s in SESS:
    d = PH.SESS[s]
    S = os.path.join(PH.DATA, d, "aifoundry2", "s1")
    paths = sorted(os.path.join(S, "tel", f) for f in os.listdir(os.path.join(S, "tel")) if f.endswith(".jsonl.gz"))
    SD[s] = {"res": json.load(open(os.path.join(PH.DATA, d, "results.json"))), "runs": [json.loads(x) for x in open(os.path.join(S, "runs.jsonl"))],
             "L": [json.loads(x) for x in gzip.open(os.path.join(S, "launches.jsonl.gz"), "rt")], "tel": G.hm.load_tel(paths, sensor="fw")}


def windows(L, r, desk_mask=False):
    procs = [p for p in L if p["run"] == r["run"] and p.get("role") == "work"]
    if not procs:
        return None
    t0, t1 = min(p["t_start_ms"] for p in procs) / 1000.0, max(p["t_end_ms"] for p in procs) / 1000.0
    kw = [(k["t_start_ms"] / 1000.0, k["t_end_ms"] / 1000.0) for p in procs for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")
          and (not desk_mask or (k.get("test") == "fma" and k.get("launch", 0) >= 0))]
    return t0, t1, kw


def mask(x, kw):
    m = np.zeros(len(x), bool)
    for a, b in kw:
        m |= (x >= a) & (x <= b)
    return m


MEAS_MHZ = {(c["session"], c["run"]): c["meas"]["mhz"] for c in INP}

# ---------------------------------------------------------------- (5) the board's slope on the die at a fixed 800 MHz (C1)
sl = []
for s in SESS:
    tel = SD[s]["tel"]
    t, P, T, F = tel["t"], tel["P"], tel["T"], tel["mhz"]
    for r in SD[s]["runs"]:
        if r.get("processes", 1) < 2:
            continue
        w = windows(SD[s]["L"], r)
        if not w:
            continue
        t0, t1, kw = w
        m = mask(t, kw) & (t >= t0 + 2.0) & (t <= t1) & (F == 800) & np.isfinite(P) & np.isfinite(T)
        if m.sum() < 100 or np.ptp(T[m]) < 3:
            continue
        k = float(np.polyfit(T[m], P[m], 1)[0])
        sl.append({"session": s, "cell": r["label"], "slope_W_per_C": round(k, 3), "n": int(m.sum()), "die_span_C": round(float(np.ptp(T[m])), 1),
                   "window_mhz": round(MEAS_MHZ[(s, r["run"])], 1), "unheld": MEAS_MHZ[(s, r["run"])] >= 799.0})
ks = np.array([x["slope_W_per_C"] for x in sl])
ku = np.array([x["slope_W_per_C"] for x in sl if x["unheld"]])
OUT["leakage_slope_at_800MHz"] = {
    "rule": "in-kernel samples at 800 MHz from 2 s after the run's first process to its end; runs with at least 100 such samples and a die span of at least 3 C; "
            "least squares slope of board W on the die reading",
    "all": {"n": int(len(ks)), "median": round(float(np.median(ks)), 3), "iqr": [round(float(np.percentile(ks, 25)), 3), round(float(np.percentile(ks, 75)), 3)],
            "mean": round(float(ks.mean()), 3)},
    "unheld_in_window": {"n": int(len(ku)), "median": round(float(np.median(ku)), 3), "min": round(float(ku.min()), 3), "max": round(float(ku.max()), 3),
                         "runs": [x for x in sl if x["unheld"]]},
    "idle_slope_Q138t": G.K_LEAK, "runs": sl}
uh = OUT["leakage_slope_at_800MHz"]["unheld_in_window"]
print(f"\n(5) the board's slope on the die inside runs at a fixed 800 MHz: {len(ks)} runs (>= 100 samples, die span >= 3 C), median {np.median(ks):.3f} W/C, "
      f"IQR [{np.percentile(ks, 25):.3f}, {np.percentile(ks, 75):.3f}]; the {uh['n']} runs whose window clock stays at 800 MHz (>= 799): "
      f"{', '.join(str(x['slope_W_per_C']) for x in uh['runs'])} W/C (median {uh['median']:.3f}); Q138(t)'s idle slope {G.K_LEAK}")
for x in uh["runs"]:
    print(f"    unheld: {x['session']} {x['cell']:18s} slope {x['slope_W_per_C']:+.3f} W/C over {x['die_span_C']} C, {x['n']} samples")


# ---------------------------------------------------------------- (6) sensitivities, and the gap share on the model's own mask (C3)
def collect(anchor_s=G.ANCHOR_S, window_s=G.SUS_LAST_S):
    """posthoc_g3.py's per-run inputs at another anchor or window; G.P_REF as set by the caller"""
    out = []
    for s in SESS:
        tel = SD[s]["tel"]
        t = tel["t"]
        ok = np.isfinite(tel["T"]) & np.isfinite(tel["P"])
        g = np.arange(t[ok][0], t[ok][-1], G.DT)
        Pm, Tm = np.interp(g, t[ok], tel["P"][ok]), np.interp(g, t[ok], tel["T"][ok])
        Xm = G.chain_open(Pm)
        for r in SD[s]["runs"]:
            if r.get("processes", 1) < 2:
                continue
            w = windows(SD[s]["L"], r)
            if not w:
                continue
            t0, t1, kw = w
            i0, i1 = int(np.searchsorted(g, t0)), int(np.searchsorted(g, t1))
            gg = g[i0:i1 + 1]
            ma = (g >= t0 - anchor_s) & (g < t0)
            anc = float(np.mean(Tm[ma] - Xm[ma] @ G.R))
            x0 = Xm[i0 - 1]
            mw = mask(t, kw) & (t >= t1 - window_s) & (t <= t1)
            out.append({"session": s, "run": r["run"], "lev": PH.levels_for(s, SD[s]["res"], r["label"]), "on": mask(gg, kw), "gg0": float(gg[0]), "t1": t1,
                        "x0": x0, "anc": anc, "T_start": anc + float(G.R @ x0),
                        "meas": {"mhz": float(np.nanmean(tel["mhz"][mw])), "w": float(np.mean(tel["P"][mw])), "die": float(np.mean(tel["T"][mw]))}})
    return out


def score_at(C, k=K_FIN, trip=TRIP_FIN, last_s=G.SUS_LAST_S):
    E = [err(c["meas"], sim(c, k, trip, last_s=last_s)) for c in C]
    return {q: stats(E, q) for q in QS}


sens = {}
base = collect()
assert len(base) == 56 and max(abs(b["meas"][q] - c["meas"][q]) for b, c in zip(base, INP) for q in QS) < 0.006
sens["as committed (gap share 0.5, P_REF 22 W, anchor 20 s, window 40 s)"] = score_at(base)
for share in (0.0, 1.0):
    G.OFF_SHARE = share
    sens[f"gap share {share}"] = score_at(base)
    G.OFF_SHARE = 0.5
for pref in (21.5, 22.5):
    G.P_REF = pref
    sens[f"P_REF {pref} W"] = score_at(collect())
    G.P_REF = 22.0
for an in (5.0, 60.0):
    sens[f"anchor {an:.0f} s"] = score_at(collect(anchor_s=an))
sens["window 30 s"] = score_at(collect(window_s=30.0), last_s=30.0)
assert (G.OFF_SHARE, G.P_REF) == (0.5, 22.0)
rng_s = {q: [min(v[q]["rms"] for v in sens.values()), max(v[q]["rms"] for v in sens.values())] for q in QS}
OUT["sensitivities_final_constants_in_sample"] = {"variants": sens, "rms_range": rng_s}
print("\n(6) sensitivities to the choices no lane registered, G3 at its final constants (0.1, 65.5), in sample, all 56 runs:")
for k, v in sens.items():
    print(f"    {k:66s} clock {v['mhz']['rms']:6.2f} ({v['mhz']['mean']:+6.2f})  board {v['w']['rms']:5.2f} ({v['w']['mean']:+5.2f})  die {v['die']['rms']:5.2f} ({v['die']['mean']:+5.2f})")
print(f"    range of the rms: clock {rng_s['mhz']}, board {rng_s['w']}, die {rng_s['die']}")
gs = {}
tel = SD["E146"]["tel"]
for r in SD["E146"]["runs"]:
    if r.get("processes", 1) < 2:
        continue
    row = {}
    for name, dm in (("model_mask", False), ("desk_mask", True)):
        t0, t1, kw = windows(SD["E146"]["L"], r, desk_mask=dm)
        span = (tel["t"] >= t0) & (tel["t"] <= t1) & np.isfinite(tel["P"])
        on = mask(tel["t"], kw)
        pon, poff = float(np.mean(tel["P"][span & on])), float(np.mean(tel["P"][span & ~on]))
        row[name] = {"P_on_W": round(pon, 2), "P_off_W": round(poff, 2), "off_share": round((poff - G.P_REF) / (pon - G.P_REF), 3),
                     "off_time_share": round(float(np.mean(~on[span])), 3)}
    gs[r["label"]] = row
OUT["gap_share_E146"] = {"what": "the board between kernels over P_REF, as a share of the board inside kernels over P_REF, over each sustained run's span; "
                                 "model_mask = every recorded launch counts as on (the mask G3 runs on); desk_mask = only the fma launches with launch >= 0 "
                                 "(calibration dispatches counted as off), the mask the frozen 0.5 was read from", "runs": gs}
print("    E146's two sustained runs, the gap share (board off kernels over 22 W / board on kernels over 22 W):")
for lab, v in gs.items():
    print(f"      {lab:14s} model's mask: on {v['model_mask']['P_on_W']} W, off {v['model_mask']['P_off_W']} W, share {v['model_mask']['off_share']} "
          f"(off {v['model_mask']['off_time_share']:.1%} of the time) | the desk's mask: on {v['desk_mask']['P_on_W']} W, off {v['desk_mask']['P_off_W']} W, "
          f"share {v['desk_mask']['off_share']}")

# ---------------------------------------------------------------- (7) E159's levels beside the shapes G3 was scored on (C7)
P136, P146 = PH.P136, PH.P146
fitcells = sorted({(c["session"], c["cell"]) for c in INP})
twins = {}
print("\n(7) E159's P0 levels (600/700/800 MHz, W) beside the shapes in G3's fit set:")
for e159, kind, others in (("H3-fp32-randn", "fp32-randn", (("E136", "g2k"), ("E146", "L2"))), ("H3-int8-full", "int8-full", (("E136", "g2k"), ("E146", "L2"))),
                           ("H3-fp32-zeros", "fp32-zeros", (("E136", "g2k"), ("E146", "L2"))),
                           ("H1-fp32-randn", "fp32-randn", (("E146", "D8"), ("E136", "g4k"), ("E146", "F6"))),
                           ("H1-int8-full", "int8-full", (("E146", "D8"), ("E136", "g4k"), ("E146", "F6"))),
                           ("H2-fp32-randn", "fp32-randn", (("E146", "D8"), ("E146", "F6"), ("E136", "g2k"))), ("H2-int8-full", "int8-full", (("E146", "F6"), ("E136", "g2k")))):
    mine = PRED["cells"][e159]["P0_w"]
    row = {"E159": mine, "beside": {}}
    for src, shape in others:
        cell = f"{shape}-{kind}"
        lv = (P136["cells"][cell]["P_w"] if src == "E136" else P146["cells"][cell]["P0_w"])
        row["beside"][f"{src} {cell}"] = {"P0_w": lv, "equal": all(abs(float(lv[f]) - float(mine[f])) < 0.006 for f in ("600", "700", "800")),
                                          "sustained_run_in_G3_fit_set": (src, cell) in fitcells}
    twins[e159] = row
    print(f"   {e159:14s} {mine['600']:6.2f}/{mine['700']:6.2f}/{mine['800']:6.2f}  beside " + "; ".join(
        f"{k} {v['P0_w']['600']}/{v['P0_w']['700']}/{v['P0_w']['800']}{' (equal)' if v['equal'] else ''}{' [a sustained run in the fit set]' if v['sustained_run_in_G3_fit_set'] else ''}"
        for k, v in row["beside"].items()))
splits = {s: {"n_L3": round(v["lines_32MB"]["n_L3"], 3), "n_F": round(v["lines_32MB"]["n_F"], 3)} for s, v in PRED["design"]["shapes"].items()}
OUT["E159_levels_beside_fit_set"] = {"cells": twins, "line_splits_32MB": splits,
                                     "fit_set_sustained_cells": [f"{s} {c}" for s, c in fitcells if s in LARGE]}
print(f"   line splits at 32 MB (lines an op missing the L2, L3 / fresh): {splits}")
json.dump(OUT, open(os.path.join(HERE, "posthoc-fix-g3.json"), "w"), indent=1)
print("\nwrote posthoc-fix-g3.json")
