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
