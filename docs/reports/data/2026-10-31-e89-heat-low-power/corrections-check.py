#!/usr/bin/env python3
"""E89, corrections after verification (Sat 31 Oct 2026): prints every number the README's section "Corrections after
verification" cites, from the committed files only. It changes nothing and scores nothing. Run from anywhere:

    python3 corrections-check.py > corrections-check.txt

Reads e89.json and posthoc.txt beside it, the raw passes aifoundry3/e89/p8910 and p8911, E78's e78.json and E85's
analysis/lockin.json, and runs the registered reducer (tools/claims-v3/e89/reduce_e89.py) three times into a temporary
directory with only its trend order changed (C5). Section tags in brackets match the README's C1-C9.
"""
import contextlib
import gzip
import importlib.util
import io
import json
import math
import os
import re
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_TOP = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E78_JSON = os.path.join(REPO_TOP, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")
E85_JSON = os.path.join(REPO_TOP, "docs/reports/data/2026-10-31-e85-camera-kinds/analysis/lockin.json")
REDUCER = os.path.join(REPO_TOP, "tools/claims-v3/e89/reduce_e89.py")
PRED = os.path.join(REPO_TOP, "tools/claims-v3/e89/predictions-e89.json")
PASSES = [os.path.join(HERE, "aifoundry3/e89/p8910"), os.path.join(HERE, "aifoundry3/e89/p8911")]
T1, T3 = 12.706, 3.182
LOW = ["i8full", "i8gauss", "i8small", "i8sp50", "i8neg1", "i8zero", "f32ones"]
REF = "f32randn"
ALL = LOW + [REF]
C78 = 0.118  # E78's resolved 2 s coefficient, degC per W of S (E78 README result 4)


def load_reducer():
    spec = importlib.util.spec_from_file_location("reduce_e89_check", REDUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ms(v):
    v = np.asarray(v, float)
    return float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v)))


def ratio(a, b, t):
    (ma, sa), (mb, sb) = ms(a), ms(b)
    r = ma / mb
    se = abs(r) * math.hypot(sa / ma, sb / mb)
    return r, r - t * se, r + t * se


def verdict(lo, hi, band):
    if lo >= band[0] and hi <= band[1]:
        return "PASS"
    if hi < band[0] or lo > band[1]:
        return "FAIL"
    return "INCONCLUSIVE"


def by_pass(items, key):
    d = {}
    for x in items:
        d.setdefault(x["pass"], []).append(key(x))
    return [float(np.mean(d[k])) for k in sorted(d)]


e = json.load(open(os.path.join(HERE, "e89.json")))
B = e["blocks"]
items78 = json.load(open(E78_JSON))["items"]
pred = json.load(open(PRED))
phi = math.radians(e["phi_ref_deg"])
W = {b: B[b]["denominator"]["w"] for b in ALL}
WHAT = {b: ("S" if B[b]["denominator"]["what"].startswith("S") else "D") for b in ALL}

# ---------------------------------------------------------------------------------------------------------------
print("[C1] coverage: E78's int8 kinds against E89's blocks")
i8_78 = sorted(k for k in items78 if k.startswith("int8."))
i8_89 = [B[b]["kind"] for b in ALL if B[b]["kind"].startswith("int8.")]
miss = [k for k in i8_78 if k not in i8_89]
print(f"  E78 int8 kinds: {len(i8_78)}; E89 int8 blocks: {len(i8_89)} ({', '.join(k[5:] for k in i8_89)})")
print(f"  not measured by E89 ({len(miss)}): {', '.join(k[5:] for k in miss)}")
c_i8 = [B[b]["step2_C_per_W_E78"]["mean"] for b in ALL if B[b]["kind"].startswith("int8.")]
print(f"  E89's 2 s coefficient on its six int8 blocks: {min(c_i8):.4f}-{max(c_i8):.4f} degC/W; reference {B[REF]['step2_C_per_W_E78']['mean']:.4f}")
print("  | int8 kind (not measured) | E78 S (W) | E78 D (W) | S x 0.118 (degC, E78's extrapolation) | S x E89's int8 coefficients (degC) |")
for k in miss:
    S = items78[k]["S"]["mean"]
    D = items78[k]["D"]["mean"]
    print(f"  | {k[5:]} | {S:.3f} | {D:.3f} | {S * C78:.2f} | {S * min(c_i8):.2f}-{S * max(c_i8):.2f} |")
low78 = sorted(k for k in items78 if "." in k and items78[k]["S"]["mean"] <= 12.0)  # anchor_pi, the built-in pi tie, is not a kind
meas = {B[b]["kind"] for b in LOW}
rest = [k for k in low78 if k not in meas]
print(f"  E78 kinds at or below 12 W of S (the built-in pi tie left out): {len(low78)}; measured by E89: {len([k for k in low78 if k in meas])}; "
      f"still extrapolated: {len(rest)} ({sum(1 for k in rest if k.startswith('int8.'))} int8, {sum(1 for k in rest if not k.startswith('int8.'))} fp32/fp16)")
print(f"  the fp32/fp16 kinds still extrapolated: {', '.join(k for k in rest if not k.startswith('int8.'))}")
print()

# ---------------------------------------------------------------------------------------------------------------
print("[C2] the 2 s rise: over the type's zeros (D) as measured, against E78's over-idle (S) cells")
s0 = B["i8zero"]["step2_C"]
S_f32z = items78["fp32.zeros"]["S"]["mean"]
c_ref = B[REF]["step2_C_per_W_E78"]["mean"]
c_zero = B["i8zero"]["step2_C_per_W_E78"]["mean"]
f32z_lo, f32z_hi = S_f32z * c_ref, S_f32z * c_zero
print(f"  int8 zeros over idle, measured: {s0['mean']:.3f} +- {s0['ci95']:.3f} degC")
print(f"  fp32 zeros over idle, not measured by E89: E78 S {S_f32z:.3f} W x {c_ref:.4f}-{c_zero:.4f} degC/W "
      f"(the reference's and int8 zeros' 2 s coefficients) = {f32z_lo:.3f}-{f32z_hi:.3f} degC")
print("  | block | over | E78 D (W) | E78 S (W) | step2 measured (degC) | E78 coefficient x this step's W (degC) | "
      "over idle, derived (degC) | E78's over-idle S x 0.118 (degC) | derived / (S x 0.118) |")
for b in ALL:
    k = B[b]["kind"]
    D, S = items78[k]["D"]["mean"], items78[k]["S"]["mean"]
    st = B[b]["step2_C"]
    over = "idle" if WHAT[b] == "S" else ("int8 zeros" if k.startswith("int8.") else "fp32 zeros")
    if b == "i8zero":
        der, derlo, derhi, ci = st["mean"], st["mean"], st["mean"], st["ci95"]
        ders = f"{der:.3f} +- {ci:.3f} (measured)"
    elif k.startswith("int8."):
        der = st["mean"] + s0["mean"]
        ci = math.hypot(st["ci95"], s0["ci95"])
        derlo = derhi = der
        ders = f"{der:.3f} +- {ci:.3f} (sum; +- in quadrature)"
    else:
        derlo, derhi = st["mean"] + f32z_lo, st["mean"] + f32z_hi
        ders = f"{derlo:.3f}-{derhi:.3f} (plus fp32 zeros' {f32z_lo:.3f}-{f32z_hi:.3f})"
    ex = S * C78
    print(f"  | {b} | {over} | {D:.3f} | {S:.3f} | {st['mean']:.3f} +- {st['ci95']:.3f} | {W[b] * C78:.3f} ({WHAT[b]}) | {ders} | "
          f"{ex:.3f} | {derlo / ex:.3f}" + (f"-{derhi / ex:.3f}" if derhi != derlo else "") + " |")
dT78 = items78["fp32.randn"]["dT_win"]
print(f"  E78's measured over-idle 2 s rise for fp32 randn (resolved): {dT78['mean']:.2f} +- {dT78.get('ci95', float('nan')):.2f} degC "
      f"(e78.json items.fp32.randn.dT_win); E89 derived {B[REF]['step2_C']['mean'] + f32z_lo:.3f}-{B[REF]['step2_C']['mean'] + f32z_hi:.3f}")
r4 = [B[b]["step2_C_per_W_E78"]["mean"] / C78 - 1 for b in LOW]
print(f"  each kind's 2 s coefficient against E78's 0.118: {100 * min(r4):+.1f}% to {100 * max(r4):+.1f}%")
print()

# ---------------------------------------------------------------------------------------------------------------
print("[C3] registered per board W against the post hoc per minion-rail W")
ex1 = []
for b in LOW:
    r = B[b]["r_H"]
    x = r["lo"] > 1 or r["hi"] < 1
    ex1.append(x)
    print(f"  {b}: r_H {r['r']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}] (registered, lap unit){'  excludes 1' if x else ''}")
print(f"  registered: r {min(B[b]['r_H']['r'] for b in LOW):.3f}-{max(B[b]['r_H']['r'] for b in LOW):.3f}; intervals excluding 1: {sum(ex1)} of {len(LOW)}")
ph = {}
rowre = re.compile(r"^\| (\w+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \[([\d.]+), ([\d.]+)\] \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|$")
for line in open(os.path.join(HERE, "posthoc.txt")):
    m = rowre.match(line.strip())
    if m:
        g = m.groups()
        ph[g[0]] = {"Hb": float(g[1]), "Hm": float(g[2]), "rm": float(g[3]), "lo": float(g[4]), "hi": float(g[5]),
                    "minion": float(g[6]), "sram": float(g[7]), "noc": float(g[8])}
for b in LOW:
    p = ph[b]
    x = p["lo"] > 1 or p["hi"] < 1
    print(f"  {b}: per minion-rail W r {p['rm']:.3f} [{p['lo']:.3f}, {p['hi']:.3f}] (posthoc.txt POST HOC 2, descriptive){'  excludes 1' if x else ''}")
print(f"  post hoc: r {min(ph[b]['rm'] for b in LOW):.3f}-{max(ph[b]['rm'] for b in LOW):.3f}; intervals excluding 1: "
      f"{sum(1 for b in LOW if ph[b]['lo'] > 1 or ph[b]['hi'] < 1)} of {len(LOW)} (their intervals take the reference as a fixed number)")
print()

# ---------------------------------------------------------------------------------------------------------------
print("[C4] E85's camera and E89's die sensors on random int8: the conditions")
l85 = json.load(open(E85_JSON))["blocks"]["E85-I8"]
print(f"  E85 (aifoundry2; 192 minions at 800 MHz, the camera on the back of the board, E85 README): ROI amplitude "
      f"{l85['roi']['amp']:.1f} mK at {l85['f_hz']:.4f} Hz, board step {l85['board_step_w']['mean']:.3f} W, board fundamental "
      f"{l85['power']['amp']:.3f} W; not detected (E85-R1 FAIL)")
i8 = B["i8full"]
step_w = i8["P_fund_W"]["mean"] * math.pi / 2
print(f"  E89 (aifoundry3; 1,024 minions at 600 MHz, the 34 on-die sensors): the temperature fundamental's amplitude "
      f"{i8['T_fund_C']['mean']:.3f} +- {i8['T_fund_C']['ci95']:.3f} degC at {1 / 60:.4f} Hz, board fundamental "
      f"{i8['P_fund_W']['mean']:.3f} W (a square wave of about {step_w:.2f} W peak to peak)")
print(f"  frequency ratio {l85['f_hz'] * 60:.2f}x; drive ratio (board fundamentals) {i8['P_fund_W']['mean'] / l85['power']['amp']:.2f}x")
print()

# ---------------------------------------------------------------------------------------------------------------
print("[C5] the unit of replication: the rules scored with the pass as the unit (n = 2, t(0.975, 1) = 12.706)")


def lap_vals(b):
    out = []
    for L in e["laps"][b]:
        P = complex(*L["P"])
        T = complex(*L["Tm"])
        out.append({"pass": L["pass"], "h": ((T / P) * complex(math.cos(-phi), math.sin(-phi))).real,
                    "tf": (T * np.exp(-1j * (np.angle(P) + phi))).real})
    return out


tally = {"PASS": 1}  # E89-R0 is a share of samples: the same at any unit
print("  E89-R0: PASS (a share of samples; the unit does not enter)")
b2, b3, b4 = pred["rules"]["E89-R2"]["band"], pred["rules"]["E89-R3"]["band"], pred["rules"]["E89-R4"]["band"]
for b in ALL:
    m, s = ms(by_pass(lap_vals(b), lambda x: x["tf"]))
    lo, hi = m - T1 * s, m + T1 * s
    v = "PASS" if lo > 0 else ("FAIL" if hi < 0 else "INCONCLUSIVE")
    tally[v] = tally.get(v, 0) + 1
    print(f"  E89-R1 {b}: T_fund {m:.3f} [{lo:.3f}, {hi:.3f}] -> {v}")
href = by_pass(lap_vals(REF), lambda x: x["h"])
for b in LOW:
    r, lo, hi = ratio(by_pass(lap_vals(b), lambda x: x["h"]), href, T1)
    v = verdict(lo, hi, b2)
    tally[v] = tally.get(v, 0) + 1
    print(f"  E89-R2 {b}: r {r:.3f} [{lo:.3f}, {hi:.3f}] band {b2} -> {v}{'  (excludes 1)' if lo > 1 or hi < 1 else ''}")
m, s = ms(href)
v = "PASS" if (m + T1 * s >= b3[0] and m - T1 * s <= b3[1]) else "FAIL"
tally[v] = tally.get(v, 0) + 1
print(f"  E89-R3 {REF}: H {m:.4f} +- {T1 * s:.4f} overlaps {b3} -> {v}")
sref = by_pass(e["steps"][REF], lambda x: x["dT"] / W[REF])
for b in LOW:
    r, lo, hi = ratio(by_pass(e["steps"][b], lambda x, b=b: x["dT"] / W[b]), sref, T1)
    v = verdict(lo, hi, b4)
    tally[v] = tally.get(v, 0) + 1
    print(f"  E89-R4 {b}: r {r:.3f} [{lo:.3f}, {hi:.3f}] band {b4} -> {v}")
print(f"  pass-unit tally: {tally} (registered, lap unit: {e['tally']})")
print()
print("[C5] the trend model: the registered reducer re-run with only its trend's polynomial order changed")


def make_fit(order):
    def block_fit(t, y, t0, period, ncyc):
        span = ncyc * period
        m = np.isfinite(y) & (t >= t0) & (t < t0 + span)
        out = [None] * ncyc
        if m.sum() < 0.3 * span * 10:
            return out
        tau = t[m] - t0
        u = tau / span - 0.5
        w = 2 * math.pi / period
        cols = [np.ones_like(u)] + [u ** k for k in range(1, order + 1)]
        okc = []
        for c in range(ncyc):
            ind = ((tau >= c * period) & (tau < (c + 1) * period)).astype(float)
            if ind.sum() < 0.3 * period * 10:
                continue
            okc.append(c)
            cols += [np.cos(w * tau) * ind, np.sin(w * tau) * ind]
        X = np.column_stack(cols)
        coef, *_ = np.linalg.lstsq(X, y[m], rcond=None)
        for j, c in enumerate(okc):
            out[c] = complex(coef[order + 1 + 2 * j], -coef[order + 2 + 2 * j])
        return out
    return block_fit


def run_reducer(order):
    red = load_reducer()
    red.block_fit = make_fit(order)
    argv = sys.argv
    with tempfile.TemporaryDirectory() as td:
        sys.argv = ["reduce_e89.py"] + PASSES + ["--out", td, "--e78", E78_JSON, "--pred", PRED]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                red.main()
        finally:
            sys.argv = argv
        return json.load(open(os.path.join(td, "e89.json")))


widths = {}
for order, name in ((2, "quadratic (registered)"), (1, "linear"), (3, "cubic")):
    x = run_reducer(order)
    XB = x["blocks"]
    if order == 2:
        dev = max(abs(XB[b]["r_H"]["r"] - B[b]["r_H"]["r"]) for b in LOW)
        print("  check: the quadratic re-run reproduces the committed r_H " + ("to within 1e-12" if dev < 1e-12 else f"only to {dev:.1e}"))
    rr = [XB[b]["r_H"] for b in LOW]
    n_ex = sum(1 for r in rr if r["lo"] > 1 or r["hi"] < 1)
    vs = [verdict(r["lo"], r["hi"], b2) for r in rr]
    widths[order] = [r["hi"] - r["lo"] for r in rr]
    vtxt = ", ".join(f"{b} {v}" for b, v in zip(LOW, vs) if v != "PASS") or "PASS x7"
    print(f"  {name}: r {min(r['r'] for r in rr):.3f}-{max(r['r'] for r in rr):.3f}; H_ref {XB[REF]['H_proj_ref_phase']['mean']:.4f} "
          f"+- {XB[REF]['H_proj_ref_phase']['ci95']:.4f}; intervals excluding 1: {n_ex} of 7; R2 on this fit: {vtxt}")
    for b, r in zip(LOW, rr):
        print(f"    {b}: {r['r']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]")
for order in (1, 3):
    q = [a / b for a, b in zip(widths[order], widths[2])]
    print(f"  interval width against the quadratic, order {order}: {min(q):.1f}-{max(q):.1f}x")
print()

# ---------------------------------------------------------------------------------------------------------------
print("[C6] the 2 s step by cycle (cycle 0 follows the 20 s lead-in; cycle 1 follows a 30 s reference half)")
n_up = 0
for b in ALL:
    st = e["steps"][b]
    c0 = {x["pass"]: x["dT"] for x in st if x["cycle"] == 0}
    c1 = {x["pass"]: x["dT"] for x in st if x["cycle"] == 1}
    both = all(c1[p] > c0[p] for p in c0)
    n_up += both
    m0, m1 = np.mean(list(c0.values())), np.mean(list(c1.values()))
    print(f"  {b}: cycle 0 {', '.join(f'{c0[p]:.3f}' for p in sorted(c0))} | cycle 1 {', '.join(f'{c1[p]:.3f}' for p in sorted(c1))} degC; "
          f"mean c1/c0 {m1 / m0:.3f}; per W of E78's {WHAT[b]}: c0 {m0 / W[b]:.4f}, c1 {m1 / W[b]:.4f}{'  (c1 > c0 in both passes)' if both else ''}")
print(f"  blocks with cycle 1 above cycle 0 in both passes: {n_up} of {len(ALL)}")
st = e["steps"][REF]
k0 = np.mean([x["dT"] for x in st if x["cycle"] == 0]) / W[REF]
k1 = np.mean([x["dT"] for x in st if x["cycle"] == 1]) / W[REF]
print(f"  reference's 2 s coefficient: cycle 0 {k0:.4f}, cycle 1 {k1:.4f}, mean {(k0 + k1) / 2:.4f} degC/W; against E78's 0.118: "
      f"{100 * (k0 / C78 - 1):+.1f}% and {100 * (k1 / C78 - 1):+.1f}%")
print()

# ---------------------------------------------------------------------------------------------------------------
print("[C7] the idle brackets (the 34-sensor mean, the firmware's conversion)")
red = load_reducer()
ends = {}
for d in PASSES:
    ps = red.load_pass(d)
    A = red.arrays(ps["tel"])
    t, Tm, S = A["t"], A["Tm"], A["S"]
    idle = [m for m in ps["marks"] if m["kind"] == "idle"][0]
    blocks = [m for m in ps["marks"] if m["kind"] == "block"]
    ends[os.path.basename(d)] = (idle["t_start_ms"] / 1000, max(m["t_end_ms"] for m in blocks) / 1000, blocks[-1]["block"])
    mi = (t >= idle["t_start_ms"] / 1000) & (t < idle["t_end_ms"] / 1000) & np.isfinite(Tm)
    ti, yi = t[mi] - t[mi][0], Tm[mi]
    sl, ic = np.polyfit(ti, yi, 1)
    res = yi - (sl * ti + ic)
    Si = S[mi]
    rsd = []
    for s in range(34):
        q = np.polyfit(ti, Si[:, s], 1)
        rsd.append(np.std(Si[:, s] - np.polyval(q, ti), ddof=2) / 0.060889)
    print(f"  {os.path.basename(d)}: {mi.sum()} samples over {ti[-1]:.1f} s; mean {yi.mean():.2f} degC; SD {np.std(yi, ddof=1):.4f} degC; "
          f"slope {sl * 60:+.3f} degC/min (a {sl * ti[-1]:+.3f} degC drift over the bracket); SD about a straight line "
          f"{np.std(res, ddof=2):.4f} degC; per-sensor SD about a straight line, median {np.median(rsd):.2f} codes")
p10, p11 = ends["p8910"], ends["p8911"]
print(f"  pass 8911's idle bracket began {p11[0] - p10[1]:.1f} s after pass 8910's last block ({p10[2]}) ended")
print()

# ---------------------------------------------------------------------------------------------------------------
print("[C8] wording")
print(f"  one code = {red.H_TS / red.CAL5 / 1000:.6f} degC (G/H/CAL5 = {red.G_TS}/{red.H_TS}/{red.CAL5}, one set of constants for every sensor); "
      f"the 34-sensor mean's step = {red.H_TS / red.CAL5 / 1000 / 34:.4f} degC")
print("  board swing outside the three metered rails (1 - minion - SRAM - NoC shares, posthoc.txt POST HOC 2):")
for b in ALL:
    p = ph[b]
    print(f"    {b}: minion {p['minion']:.3f}, SRAM {p['sram']:.3f}, NoC {p['noc']:.3f}; SRAM + NoC {p['sram'] + p['noc']:.3f}; outside {1 - p['minion'] - p['sram'] - p['noc']:.3f}")
masks = {}
for d in PASSES:
    for line in open(os.path.join(d, "runs.jsonl")):
        r = json.loads(line)
        masks[(r.get("shire_mask"), r.get("minions"))] = masks.get((r.get("shire_mask"), r.get("minions")), 0) + 1
print(f"  launch records by (shire_mask, minions), both passes: {masks}")
print()

# ---------------------------------------------------------------------------------------------------------------
print("[C9] command 74: the sensors' latches, the firmware's peak-holds and fault bits over both passes")
nhi = drops_hi = rises_lo = nf = 0
hmax = 0
holds = set()
for d in PASSES:
    prev_hi = prev_lo = None
    for line in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt"):
        if not line.startswith("{"):
            continue
        r = json.loads(line)
        ms_ = r.get("temp_c", {}).get("minshire")
        if ms_:
            holds.add(tuple(ms_[1:]))
        pv = r.get("pvt") or {}
        if pv.get("f"):
            nf += 1
        if "hi" in pv:
            nhi += 1
            hmax = max(hmax, max(pv["hi"]))
            if prev_hi is not None:
                drops_hi += sum(1 for a, b in zip(pv["hi"], prev_hi) if a < b)
                rises_lo += sum(1 for a, b in zip(pv["lo"], prev_lo) if a > b)
            prev_hi, prev_lo = pv["hi"], pv["lo"]
print(f"  latch reads {nhi}; a high latch below its previous read: {drops_hi}; a low latch above its previous read: {rises_lo}; "
      f"highest latch code {hmax} ({red.code_to_c(hmax):.1f} degC)")
print(f"  the firmware's minshire [min, max] holds seen: {sorted(holds)}; samples with a fault bit: {nf}")
