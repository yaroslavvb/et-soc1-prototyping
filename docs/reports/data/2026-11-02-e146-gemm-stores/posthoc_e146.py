#!/usr/bin/env python3
"""E146, post hoc (written after the session, labelled; no rule reads it). Standard library only.

  (1) Where each model misses: per shape and format, the session's fit T = C/f + M (cycles that follow the clock, wait that does not) against each
      model's C and M.
  (2) The store's cost read straight from the pair that differs only in cadence (L4, L8: the same lines an op): sigma_meas(f) = (T(L8) - T(L4)) /
      ((192/128) (1/256 - 1/128)) at 800 MHz and at 600 MHz (from the fits), against MS's frozen sigma.
  (3) A refit on E146's own ladder (24 cells: L1-L8, D1-D8 in three formats) of the operand split with a store term (prices pA, pB, qA, qB and sigma per
      format, least squares at 800 MHz), scored on the fresh shape F6, which the refit never sees: the out-of-sample error after.
  (4) Energy per op e = (p800 - B(800)) T800 per cell, and the store's energy slope on L4/L8 and D4/D8.
  (5) The smoke's rest reading, card time, and the device commands counted from the session's own records.
  (6) The two stop-path tests, from the queue's records.
  (7) The share of the B lines the desk's strict-LRU L3 calls fresh that the L3 must have served, for MAB's frozen prices to give the measured T800.
  (8) The store's energy from each burst's whole-window mean power (first version: the pair's mean T800; superseded by 8b, kept as first printed).

  Added after verification (Mon 2 Nov 2026; the first sections' code and output are unchanged):
  (8b) (8) corrected: e = (burst_w - B) T with each shape's own time per op, as (4) and R4 put it, pooled per kind and pair.
  (9) The scores on the cells no frozen term was fitted on: L2 and D8 are E136's g2k and g4k, which MS's sigma, MAB's prices and PS's eps were fitted on.
  (10) The store's time per pass at 800 MHz, from the pair L4/L8.
  (11) MAB's frozen line prices as ratios, A line over B line, by place and clock.

    python3 docs/reports/data/2026-11-02-e146-gemm-stores/posthoc_e146.py > docs/reports/data/2026-11-02-e146-gemm-stores/posthoc.txt
"""
import glob
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/e146/predictions-e146.json")))
R = json.load(open(os.path.join(HERE, "results.json")))
A2 = os.path.join(HERE, "aifoundry2")
TYPES = ("fp32", "fp16", "int8")
LAD = list(P["ladders"]["L"]) + list(P["ladders"]["D"])
B800 = P["relation"]["B"]["800"]
out = {}


def T8(key):
    v = R["per_shape"].get(key) or {}
    if v.get("T800") is not None:
        return v["T800"]
    f = v.get("fit") or {}
    return None if f.get("C") is None else f["C"] / 800 + f["M"]


def lstsq(X, y):
    """normal equations, small n (Gauss-Jordan)"""
    n = len(X[0])
    A = [[sum(X[k][i] * X[k][j] for k in range(len(X))) for j in range(n)] + [sum(X[k][i] * y[k] for k in range(len(X)))] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        if abs(A[c][c]) < 1e-18:
            return None
        for r in range(n):
            if r != c:
                f = A[r][c] / A[c][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [A[i][n] / A[i][i] for i in range(n)]


print("(1) the session's fit T = C/f + M per shape and format (C cycles, M us), against each model's")
out["fits"] = {}
for s in list(P["shapes"]):
    for t in TYPES:
        v = (R["per_shape"].get(f"{s}.{t}") or {}).get("fit") or {}
        L = P["laws"][f"{s}.{t}"]
        if v.get("C") is None:
            continue
        rec = {"C": v["C"], "C_ci": v.get("C_ci"), "M": v["M"], "M_ci": v.get("M_ci"), "span_mhz": v.get("span_mhz"),
               **{m: {"C": L[m]["C_cycles"], "M": L[m]["M_us"]} for m in ("M0", "MS", "MAB")}}
        out["fits"][f"{s}.{t}"] = rec
        print(f"  {s}.{t}: C {v['C']:6.1f} +- {v.get('C_ci') or 0:4.1f}, M {v['M']:.4f} +- {v.get('M_ci') or 0:.4f} (span {v.get('span_mhz') or 0:.0f} MHz) | "
              + "  ".join(f"{m} C {L[m]['C_cycles']:6.1f} M {L[m]['M_us']:.4f}" for m in ("M0", "MS", "MAB")))

print("\n(2) the store's cost from the pair that differs only in cadence, L4 (every 128 ops) and L8 (every 256)")
out["sigma_meas"] = {}
for t in TYPES:
    a, b = T8(f"L4.{t}"), T8(f"L8.{t}")
    fa = (R["per_shape"].get(f"L4.{t}") or {}).get("fit") or {}
    fb = (R["per_shape"].get(f"L8.{t}") or {}).get("fit") or {}
    x = (192 / 128.0) * (1 / 256.0 - 1 / 128.0)
    rec = {}
    if a and b:
        rec["sigma800_us"] = round((b - a) / x, 3)
    if fa.get("C") is not None and fb.get("C") is not None:
        t6a, t6b = fa["C"] / 600 + fa["M"], fb["C"] / 600 + fb["M"]
        rec["sigma600_us"] = round((t6b - t6a) / x, 3)
    rec["frozen_sigma800_us"] = round(P["fitted"][t]["sigma"]["sigma800_us"], 3)
    rec["frozen_sigma600_us"] = round(P["fitted"][t]["sigma"]["sigma600_us"], 3)
    out["sigma_meas"][t] = rec
    print(f"  {t}: T800 L4 {a}, L8 {b}; sigma at 800 MHz {rec.get('sigma800_us')} us a store (frozen {rec['frozen_sigma800_us']}), at 600 {rec.get('sigma600_us')} (frozen {rec['frozen_sigma600_us']})")

print("\n(3) a refit on E146's ladder (operand split + store term, least squares at 800 MHz, per format), scored on F6, which it never sees")
out["refit"] = {}
D = json.load(open(os.path.join(ROOT, "tools/claims-v3/e146/desk/reuse_e146.json")))
R119 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e119-gemm-speed/results.json")))
for t in TYPES:
    c1 = R119["per_arm"][f"c1.{t}"]["fit"]
    T1 = c1["C"] / 800 + c1["M"]
    X, y, labs = [], [], []
    for s in LAD:
        m = T8(f"{s}.{t}")
        if m is None:
            continue
        d = D["shapes"][s]["lines"]["32MB"]
        N = D["shapes"][s]["store_every_ops"]
        X.append([d["A_L3"], d["B_L3"], d["A_F"], d["B_F"], (d["n_miss"] / 128.0) * (1.0 / N - 1.0 / 32.0)])
        y.append(m - T1)
        labs.append(s)
    for name, cols in (("split+store", [0, 1, 2, 3, 4]), ("split only", [0, 1, 2, 3]), ("lines+store (MS's form)", None)):
        if cols is None:
            Xs = [[r[0] + r[1], r[2] + r[3], r[4]] for r in X]
        else:
            Xs = [[r[i] for i in cols] for r in X]
        beta = lstsq(Xs, y) if len(Xs) >= len(Xs[0]) + 1 else None
        if beta is None:
            continue
        res = [yy - sum(b * xx for b, xx in zip(beta, row)) for row, yy in zip(Xs, y)]
        rms_in = math.sqrt(sum((r / (yy + T1)) ** 2 for r, yy in zip(res, y)) / len(res))
        d = D["shapes"]["F6"]["lines"]["32MB"]
        N = D["shapes"]["F6"]["store_every_ops"]
        rowF = [d["A_L3"], d["B_L3"], d["A_F"], d["B_F"], (d["n_miss"] / 128.0) * (1.0 / N - 1.0 / 32.0)]
        rowF = [rowF[0] + rowF[1], rowF[2] + rowF[3], rowF[4]] if cols is None else [rowF[i] for i in cols]
        predF = T1 + sum(b * xx for b, xx in zip(beta, rowF))
        mF = T8(f"F6.{t}")
        rec = {"beta": [round(b, 6) for b in beta], "rms_rel_in_sample": round(rms_in, 4), "F6_pred": round(predF, 4), "F6_meas": mF,
               "F6_rel": None if mF is None else round(mF / predF - 1, 4)}
        out["refit"][f"{t}.{name}"] = rec
        print(f"  {t} {name:24s}: in-sample rms {rms_in:.2%}; F6 predicted {predF:.4f} us, measured {mF}, error {rec['F6_rel']}; coefficients {rec['beta']}")

print("\n(4) energy per op over the base, e = (p800 - B(800)) T800, card uJ an op step, and the store's energy slope on the pairs")
out["energy"] = {}
for s in list(P["shapes"]):
    for t in TYPES:
        for k in ("zeros", P["top"][t]):
            c = R["cells"].get(f"{s}-{t}-{k}") or {}
            ps = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
            T = T8(f"{s}.{t}")
            if ps and T:
                out["energy"][f"{s}-{t}-{k}"] = round((sum(ps) / len(ps) - B800) * T, 3)
for lo, hi in (("L4", "L8"), ("D4", "D8"), ("L2", "L4"), ("D2", "D4")):
    for t in TYPES:
        for k in ("zeros", P["top"][t]):
            a, b = out["energy"].get(f"{lo}-{t}-{k}"), out["energy"].get(f"{hi}-{t}-{k}")
            if a is None or b is None:
                continue
            Na, Nb = P["laws"][f"{lo}.{t}"]["store_every_ops"], P["laws"][f"{hi}.{t}"]["store_every_ops"]
            print(f"  {lo}/{hi} {t} {k:6s}: e {a:7.3f} -> {b:7.3f}; slope (eps) {(b - a) / (1.0 / Nb - 1.0 / Na):8.1f} uJ a store step"
                  f" (fitted {P['fitted'][t]['eps']['zeros' if k == 'zeros' else 'top']['eps_uJ_per_store_step']})")

print("\n(5) the rest reading, card time, commands")
rest = None
for L in glob.glob(os.path.join(A2, "smoke/tel/*rest*.jsonl.gz")):
    rows = [json.loads(x) for x in gzip.open(L, "rt") if x.startswith("{")]
    ws = [r["board_w"] for r in rows][-300:]
    dies = [r["temp_c"]["minshire"][0] for r in rows][-300:]
    rest = {"board_w": round(sum(ws) / len(ws), 2), "die_c": round(sum(dies) / len(dies), 2), "n": len(ws)}
print("  the smoke's rest reading (last 30 s):", rest)
q = [json.loads(x) for x in open(os.path.join(A2, "queue.jsonl"))]
t0 = min(x["t_ms"] for x in q if x["kind"] == "session_start")
t1 = max(x["t_ms"] for x in q if x["kind"] == "session_end")
tel = sum(1 for p in glob.glob(os.path.join(A2, "*/tel/*.jsonl.gz")) for x in gzip.open(p, "rt") if x.startswith("{"))
nruns = sum(1 for p in glob.glob(os.path.join(A2, "*/runs.jsonl")) for _ in open(p))
nq = sum(1 for p in glob.glob(os.path.join(A2, "*/queries.jsonl")) for _ in open(p))
print(f"  card time, first session start to last session end: {(t1 - t0) / 60000:.2f} min; sampler lines {tel}; runs with an after-run config read {nruns}; "
      f"session start/end query records {nq}; queue snapshots 2")
out.update({"rest": rest, "card_min_sessions": round((t1 - t0) / 60000, 2), "sampler_lines": tel, "runs_incl_smoke": nruns, "session_queries": nq})

print("\n(6) the stop-path tests (the queue's records)")
for x in q:
    if x["kind"] in ("stoptest_detail", "stoptest_check"):
        print("  ", json.dumps({k: v for k, v in x.items() if k not in ("zone",)}))
out["stoptests"] = [x for x in q if x["kind"] in ("stoptest_detail", "stoptest_check")]
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)

print("\n(7) how many of the lines the desk's strict-LRU L3 calls fresh the L3 must have served, for MAB's frozen prices to give the measured T800 (B's fresh")
print("    lines turned into L3 lines; the reuse distance of a B panel from one row of C blocks to the next, C included)")
out["l3_share"] = {}
for s, dist in (("D2", 36), ("F6", 44), ("D4", 56), ("D8", 96)):
    d = D["shapes"][s]["lines"]["32MB"]
    for t in TYPES:
        m = T8(f"{s}.{t}")
        if m is None:
            continue
        mab = P["laws"][f"{s}.{t}"]["MAB"]["T800_us"]
        p = P["fitted"][t]["ab"]["800"]
        x = (mab - m) / (d["B_F"] * (p["qB_F"] - p["pB_L3"])) if d["B_F"] else None
        out["l3_share"][f"{s}.{t}"] = {"reuse_distance_MB": dist, "T800": round(m, 4), "MAB": mab, "share_of_fresh_B_served_by_L3": None if x is None else round(x, 3)}
        print(f"  {s}.{t}: B panel reuse distance {dist} MB; T800 {m:.4f} against MAB {mab:.4f}: share of the 'fresh' B lines the L3 served {x:.2f}")
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)

print("\n(8) the store's energy from each burst's whole-window mean power (burst_w, at the burst's own mean clock; L4 and L8 ran at the same clock and rate),")
print("    per pass: eps = (P(L8) - P(L4)) T / (1/256 - 1/128), T the pair's mean T800; the registered R4 reads the first second at 800 MHz instead")
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/e126"))
import reduce_e126 as R126  # noqa: E402
runs, _, _, _, _, _ = R126.collect([os.path.join(A2, "s1")], P)
PASS = {"A": 1, "B": 1, "C": 1, "D": 1, "E": 2}
bw = {}
for m in runs:
    if m["block"] == "BURST" and m.get("burst_w") is not None:
        bw.setdefault((m["cell"], PASS[m["block_orig"]]), []).append((m["burst_w"], m.get("burst_mhz")))
out["store_energy_burst_w"] = {}
for lo, hi in (("L4", "L8"), ("D4", "D8")):
    for t in TYPES:
        for k in ("zeros", P["top"][t]):
            Ta, Tb = T8(f"{lo}.{t}"), T8(f"{hi}.{t}")
            T = (Ta + Tb) / 2
            per = []
            for ps in (1, 2):
                a, b = bw.get((f"{lo}-{t}-{k}", ps)), bw.get((f"{hi}-{t}-{k}", ps))
                if a and b:
                    per.append(round((b[0][0] - a[0][0]) * T / (1 / 256.0 - 1 / 128.0), 1))
            rec = {"per_pass_eps_uJ": per, "mean": None if not per else round(sum(per) / len(per), 1),
                   "fitted": P["fitted"][t]["eps"]["zeros" if k == "zeros" else "top"]["eps_uJ_per_store_step"],
                   "P_lo_runs": bw.get((f"{lo}-{t}-{k}", 1), []) + bw.get((f"{lo}-{t}-{k}", 2), []),
                   "P_hi_runs": bw.get((f"{hi}-{t}-{k}", 1), []) + bw.get((f"{hi}-{t}-{k}", 2), [])}
            out["store_energy_burst_w"][f"{lo}/{hi}.{t}.{k}"] = rec
            print(f"  {lo}/{hi} {t} {k:6s}: eps per pass {per} uJ a store step (mean {rec['mean']}; fitted {rec['fitted']}); "
                  f"burst W {[round(x[0], 2) for x in rec['P_lo_runs']]} -> {[round(x[0], 2) for x in rec['P_hi_runs']]}")
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------
# Added after verification, Mon 2 Nov 2026 (sections 8b-11). Nothing above changed; posthoc.txt's sections (1)-(8) print exactly as first committed.


def p_at(Pl, f):
    """E136's frozen interpolation of a level table at a mean clock (tools/claims-v3/e136/make_predictions_e136.py p_at), copied"""
    if f >= 800:
        return Pl[800]
    if f >= 700:
        return Pl[700] + (Pl[800] - Pl[700]) * (f - 700) / 100.0
    if f >= 600:
        return Pl[600] + (Pl[700] - Pl[600]) * (f - 600) / 100.0
    return Pl[600]


def mse(xs):
    """mean, one standard error, n"""
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else float("nan")
    return m, sd / math.sqrt(n), n


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def Tfit(key, f):
    v = (R["per_shape"].get(key) or {}).get("fit") or {}
    return v["C"] / f + v["M"]


BL = {int(k): v for k, v in P["relation"]["B"].items()}
XS = 1 / 256.0 - 1 / 128.0
print("\n(8b) corrected after verification (Mon 2 Nov 2026): (8)'s store energy with each shape at its own time per op")
print("    (8) multiplied each pair's power difference by the pair's mean T800. That holds for L4/L8 (T800 within 0.3%) but not for D4/D8: D8 runs")
print("    3.4% slower per op than D4 (fp32 2.1762 against 2.1040 us), so (8) read D8's lower power at its slower rate as a store saving; (8)'s note that")
print("    the pairs ran at the same clock and rate is true of L4/L8 only. Here, as (4) and R4 put it, each burst's e = (burst_w - B) T, and per pass")
print("    eps = (e(hi) - e(lo)) / (1/256 - 1/128). PRIMARY: T at the burst's own mean clock f from the session's fit (C/f + M), B = B(800).")
print("    Checks: [T800] each shape's T800 with B(800); [B(f)] T at f with the base at f too (E136's p_at). Pooled: mean +- one standard error")
print("    over the per-pass contrasts (random = fp32/fp16 randn and int8 full). uJ for one store step: every minion storing one 1 KB tile, 1 MiB of C.")
var = {"primary": {}, "T800": {}, "B(f)": {}, "first (8)": {}}
out["store_energy_8b"] = {"per_cell": {}, "pooled": {}}
for key, rec in out["store_energy_burst_w"].items():
    pair, t, k = key.split(".")
    lo, hi = pair.split("/")
    kk = "zeros" if k == "zeros" else "random"
    vals = {n: [] for n in var}
    for i in range(min(len(rec["P_lo_runs"]), len(rec["P_hi_runs"]))):
        (pa, fa), (pb, fb) = rec["P_lo_runs"][i], rec["P_hi_runs"][i]
        vals["primary"].append(((pb - B800) * Tfit(f"{hi}.{t}", fb) - (pa - B800) * Tfit(f"{lo}.{t}", fa)) / XS)
        vals["T800"].append(((pb - B800) * T8(f"{hi}.{t}") - (pa - B800) * T8(f"{lo}.{t}")) / XS)
        vals["B(f)"].append(((pb - p_at(BL, fb)) * Tfit(f"{hi}.{t}", fb) - (pa - p_at(BL, fa)) * Tfit(f"{lo}.{t}", fa)) / XS)
        vals["first (8)"].append(rec["per_pass_eps_uJ"][i])
    for n, v in vals.items():
        for sel in ((kk, "all"), (kk, lo), (kk, t)):
            var[n].setdefault(sel, []).extend(v)
    out["store_energy_8b"]["per_cell"][key] = {n: [round(x, 1) for x in v] for n, v in vals.items()}
    print(f"  {lo}/{hi} {t} {k:6s}: eps per pass {[round(x, 1) for x in vals['primary']]} uJ (mean {sum(vals['primary']) / len(vals['primary']):7.1f}); "
          f"[T800] {[round(x, 1) for x in vals['T800']]}; [B(f)] {[round(x, 1) for x in vals['B(f)']]}; first (8) {vals['first (8)']}")
print("  pooled, mean +- SE (n):")
for kk in ("random", "zeros"):
    for sel in ("all", "L4", "D4", "fp32", "fp16", "int8"):
        line = {}
        for n in var:
            m, se, nn = mse(var[n][(kk, sel)])
            line[n] = [round(m, 1), round(se, 1), nn]
        out["store_energy_8b"]["pooled"][f"{kk}.{sel}"] = line
        lab = {"all": "every pair", "L4": "L4/L8 only", "D4": "D4/D8 only"}.get(sel, sel)
        print(f"    {kk:6s} {lab:11s}: primary {line['primary'][0]:7.1f} +- {line['primary'][1]:6.1f} ({line['primary'][2]:2d}); [T800] {line['T800'][0]:7.1f} +- "
              f"{line['T800'][1]:6.1f}; [B(f)] {line['B(f)'][0]:7.1f} +- {line['B(f)'][1]:6.1f}; first (8) {line['first (8)'][0]:7.1f} +- {line['first (8)'][1]:6.1f}")
m, se, nn = mse(var["primary"][("random", "all")])
TL8 = sum(T8(f"L8.{t}") for t in TYPES) / 3
TL1 = sum(T8(f"L1.{t}") for t in TYPES) / 3
imp = {"per_byte_nJ": [round(m * 1e-6 / 1048576 * 1e9, 3), round((m + 2 * se) * 1e-6 / 1048576 * 1e9, 3)],
       "pJ_per_bit": [round(m * 1e-6 / 1048576 / 8 * 1e12, 1), round((m + 2 * se) * 1e-6 / 1048576 / 8 * 1e12, 1)],
       "W_every_256": [round(m / 256 / TL8, 2), round((m + 2 * se) / 256 / TL8, 2)], "W_every_32": [round(m / 32 / TL1, 2), round((m + 2 * se) / 32 / TL1, 2)],
       "t": round(m / se, 2)}
out["store_energy_8b"]["random_implied_mean_and_mean_plus_2se"] = imp
print(f"  random C, primary, every pair: t = {imp['t']}; mean and mean + 2 SE: {imp['per_byte_nJ']} nJ a byte of C ({imp['pJ_per_bit']} pJ a bit); "
      f"at a store every 256 ops (L8's T800, {TL8:.3f} us) {imp['W_every_256']} W; every 32 (L1's, {TL1:.3f} us) {imp['W_every_32']} W")
fr = {t: P["fitted"][t]["eps"]["top"]["eps_uJ_per_store_step"] for t in TYPES}
fz = {t: P["fitted"][t]["eps"]["zeros"]["eps_uJ_per_store_step"] for t in TYPES}
mz = out["store_energy_8b"]["pooled"]["zeros.all"]["primary"][0]
print(f"  against the fit: random {m:.1f} / {fr} = {min(m / x for x in fr.values()):.2f}-{max(m / x for x in fr.values()):.2f}; "
      f"zeros {mz:.1f} / {fz} = {min(mz / x for x in fz.values()):.2f}-{max(mz / x for x in fz.values()):.2f}")
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)

print("\n(9) added after verification (Mon 2 Nov 2026): the scores on the cells no frozen term was fitted on")
print("    MS's sigma (least squares at each clock), MAB's prices (solved exactly from c8s, g2k, c16 and g4k) and PS's eps were fitted on E136's g2k and g4k,")
print(f"    which are E146's {P['e136_as']['g2k']} and {P['e136_as']['g4k']} (predictions-e146.json e136_as, fitted.*.e136_check); M0 and P0 (E136's laws, from E107 and E119) and the")
print("    heat law (E119 and E126) saw neither. So L2 and D8 are R0's replicate of the fit shapes, in sample for MS, MAB and PS; the other cells are out of")
print("    sample for every model, and F6 is the blind one. Time: (measured - predicted) / predicted at 800 MHz; power and die: measured - predicted.")
FITS = set(P["e136_as"].values())
r2 = R["rules"]["R2"]["cells"]
out["out_of_sample"] = {"fit_shapes": sorted(FITS), "time_rel": {}, "burst_p800_w": {}, "die_burst_c": {}}
for name, shapes in (("18 ladder cells outside the fit shapes", ["L1", "L4", "L8", "D1", "D2", "D4"]), ("  of them, the L3-held 9 (L1, L4, L8)", ["L1", "L4", "L8"]),
                     ("  of them, the DRAM 9 (D1, D2, D4)", ["D1", "D2", "D4"]), ("the fit shapes L2 and D8 (in sample)", ["L2", "D8"]),
                     ("all 24, as R2 registered", ["L1", "L2", "L4", "L8", "D1", "D2", "D4", "D8"])):
    rec = {}
    for mo in ("M0", "MS", "MAB"):   # unrounded: per_shape T800 against the frozen T800_us, as results.json errors
        e = [T8(f"{s}.{t}") / P["laws"][f"{s}.{t}"][mo]["T800_us"] - 1 for s in shapes for t in TYPES]
        rec[mo] = {"rms": round(rms(e), 5), "mean": round(sum(e) / len(e), 5), "n": len(e)}
    rec["within_5pct_of_MS"] = sum(1 for s in shapes for t in TYPES if r2[f"{s}.{t}"]["point"] == "PASS")
    rec["X_pass"] = sum(1 for s in shapes for t in TYPES if r2[f"{s}.{t}"]["x"] == "PASS")
    out["out_of_sample"]["time_rel"][name.strip()] = rec
    print(f"  time per op, {name:40s}: " + "; ".join(f"{mo} {rec[mo]['rms']:.1%} rms (mean {rec[mo]['mean']:+.1%})" for mo in ("M0", "MS", "MAB"))
          + f"; within 5% of MS {rec['within_5pct_of_MS']} of {rec['MS']['n']}; X {rec['X_pass']} of {rec['MS']['n']}")
e = R["errors"]["fresh_T800_rel"]
print("  time per op, the blind shape F6 (results.json errors)   : " + "; ".join(f"{mo} {e[mo]['rms']:.2%} rms" for mo in ("M0", "MS", "MAB")))
r3 = R["rules"]["R3"]["cells"]
for name, sel in (("36 ladder cells outside the fit shapes", lambda c: c.split("-")[0] not in FITS), ("the fit shapes L2 and D8 (12)", lambda c: c.split("-")[0] in FITS),
                  ("all 48, as R3 registered", lambda c: True)):
    cs = [c for c in r3 if sel(c)]
    eS, e0 = [r3[c]["err_S"] for c in cs], [r3[c]["err_0"] for c in cs]
    rec = {"PS": {"rms": round(rms(eS), 2), "mean": round(sum(eS) / len(eS), 2)}, "P0": {"rms": round(rms(e0), 2), "mean": round(sum(e0) / len(e0), 2)}, "n": len(cs),
           "within_4W_of_PS": sum(1 for c in cs if r3[c]["verdict"] == "PASS")}
    out["out_of_sample"]["burst_p800_w"][name] = rec
    print(f"  burst board power at 800 MHz, {name:38s}: P0 {rec['P0']['rms']:.2f} W rms (mean {rec['P0']['mean']:+.2f}); PS {rec['PS']['rms']:.2f} W (mean {rec['PS']['mean']:+.2f}); "
          f"within 4 W of PS {rec['within_4W_of_PS']} of {rec['n']}")
r5p = R["rules"]["R5"]["power"]
f6 = {c: {"PS": round(v["err_S"], 2), "P0": round(v["p800_w"] - v["P0_w"], 2), "verdict": v["verdict"]} for c, v in sorted(r5p.items())}
out["out_of_sample"]["F6_burst_p800_w"] = f6
print("  burst board power at 800 MHz, the blind shape F6 (PS, P0): " + "; ".join(f"{c[3:]} {v['PS']:+.2f}, {v['P0']:+.2f}" for c, v in f6.items())
      + f"; rms PS {rms([v['PS'] for v in f6.values()]):.2f}, P0 {rms([v['P0'] for v in f6.values()]):.2f} W")
r6 = R["rules"]["R6"]["cells"]
for name, sel in (("78 bursts outside the fit shapes", lambda c: c.split("-")[0] not in FITS), ("the fit shapes' 24 bursts", lambda c: c.split("-")[0] in FITS),
                  ("all 102", lambda c: True)):
    eS = [x["err_S"] for c, v in r6.items() if sel(c) for x in v]
    e0 = [x["die_max"] - x["pred_0"] for c, v in r6.items() if sel(c) for x in v]
    ok = sum(1 for c, v in r6.items() if sel(c) for x in v if x["verdict"] == "PASS")
    rec = {"S": round(rms(eS), 3), "P0": round(rms(e0), 3), "n": len(eS), "within_3C": ok}
    out["out_of_sample"]["die_burst_c"][name] = rec
    print(f"  burst die maximum, {name:34s}: with PS's power {rec['S']:.2f} C rms, with P0's {rec['P0']:.2f}; within 3 C {ok} of {len(eS)}")
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)

print("\n(10) added after verification (Mon 2 Nov 2026): the store's time per pass at 800 MHz, sigma = (T(L8) - T(L4)) / ((192/128) (1/256 - 1/128)),")
print("     from results.json t800_by_pass (pass 1 = blocks A-D, pass 2 = E), us a store; (2) gives the pooled value")
out["sigma_per_pass_us"] = {}
for t in TYPES:
    x = (192 / 128.0) * (1 / 256.0 - 1 / 128.0)
    v = [round((R["t800_by_pass"][f"{p}|L8.{t}"] - R["t800_by_pass"][f"{p}|L4.{t}"]) / x, 2) for p in (1, 2)]
    out["sigma_per_pass_us"][t] = v
    print(f"  {t}: pass 1 {v[0]:+.2f}, pass 2 {v[1]:+.2f} (pooled {out['sigma_meas'][t]['sigma800_us']}; frozen {out['sigma_meas'][t]['frozen_sigma800_us']})")

print("\n(11) added after verification (Mon 2 Nov 2026): MAB's frozen line prices as ratios, an A line over a B line (predictions-e146.json fitted.*.ab;")
print("     solved exactly from c8s, g2k, c16 and g4k, so model parameters, not measurements)")
out["mab_ab_ratio"] = {}
for t in TYPES:
    ab = P["fitted"][t]["ab"]
    v = {f: {"L3": round(ab[f]["pA_L3"] / ab[f]["pB_L3"], 2), "fresh": round(ab[f]["qA_F"] / ab[f]["qB_F"], 2)} for f in ("800", "600")}
    out["mab_ab_ratio"][t] = v
    print(f"  {t}: from the L3 {v['800']['L3']} at 800 MHz, {v['600']['L3']} at 600; fresh {v['800']['fresh']} at 800, {v['600']['fresh']} at 600")
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
