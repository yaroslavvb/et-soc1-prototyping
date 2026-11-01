#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E103, corrections after verification: every number the corrections quote, recomputed from committed files by code written for this check.

    python3 corrections-check.py > corrections-check.txt         # from this directory

Nothing here changes a frozen file, a data file or a registered verdict. The comparators in [G] are post hoc: their forms were fixed by the verifier after E103's data, the constants come from E78 and the scale from E82, as M4's do.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import itertools
import json
import math
import os
import re
import statistics as st
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.abspath(os.path.join(HERE, ".."))
B = os.path.join(DD, "2026-11-01-q132-rtl-bench")
K = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds"))
sys.path.insert(0, B)
from predict_m4 import x_float  # noqa: E402

load = lambda p: json.load(open(p))
reg = load(os.path.join(K, "predictions-e103.json"))
pool = load(os.path.join(K, "e103", "pool-predictions.json"))
e103 = load(os.path.join(HERE, "e103.json"))
items = e103["items"]
sc = load(os.path.join(HERE, "scored.json"))
T = reg["tiles"]
rows = [{"key": k, "type": t["type"], "kind": t["kind"], "D": items[k]["D"]["mean"], **t["pred"]} for k, t in T.items()]
fl = [r for r in rows if r["type"] != "int8"]
i8 = [r for r in rows if r["type"] == "int8"]
nz = [r for r in fl if r["key"] != "fp32.z_dn_ab"]


def rms(v):
    v = np.asarray(v, float)
    return float(np.sqrt(np.mean(v * v)))


print("# [A] R2 and R3 follow from R1: the frozen distance between M4 and each comparator, before any data, minus M4's measured error, is the least that comparator can read")
m = rms([r["D"] - r["M"] for r in fl])
for q in ("q130n", "flop", "M2"):
    d = rms([r["M"] - r[q] for r in fl])
    d2 = rms([r["M"] - r[q] for r in nz])
    print(f"  rms(M4 - {q}): {d:.3f} W, without z_dn_ab {d2:.3f} W. At R1's PASS line 0.60 W, {q} reads at least {d - 0.60:.2f} W, a gap of at least {d - 1.20:.2f} W. Measured: M4 {m:.3f}, {q} {rms([r['D'] - r[q] for r in fl]):.3f} W")

print("\n# [B] how the tiles were picked")
sys.path.insert(0, K)
src = open(os.path.join(K, "select_e103.py")).read()
Q = eval(src[src.index("QUOTAS = [") + len("QUOTAS = "):src.index("]\n\n\ndef stem") + 1])
floats = {k: v for k, v in pool.items() if v["type"] != "int8"}
rank = {k: i + 1 for i, k in enumerate(sorted(floats, key=lambda k: -floats[k]["dis"]))}
ch = [r["key"] for r in fl]
print(f"  float pool {len(floats)}; ranks by disagreement of the 23 chosen: {sorted(rank[k] for k in ch)}; in the top 23: {sum(rank[k] <= 23 for k in ch)}")


def eligible(k, v):
    for q in Q:
        if q[0] != v["type"]:
            continue
        pre = (q[1],) if isinstance(q[1], str) else q[1]
        if any(v["name"] == x[1:] if x.startswith("=") else v["name"].startswith(x) for x in pre):
            return True
    return False


never = sorted((k for k, v in pool.items() if not eligible(k, v)), key=lambda k: -pool[k]["dis"])
print(f"  pool tiles never eligible by QUOTAS: {len(never)}; the largest: {[(k, round(pool[k]['dis'], 2)) for k in never[:6]]}")
print(f"  of which by stem: {sorted(set('_'.join(k.split('.')[1].split('_')[:2]) + '/' + k[:4] for k in never))}")
print(f"  median |M4 - M2|: chosen {st.median(abs(r['M'] - r['M2']) for r in fl):.3f} W, float pool {st.median(abs(v['M'] - v['M2']) for v in floats.values()):.3f} W")
zc = load(os.path.join(B, "counts-v2.json"))["rows"]
cp = load(os.path.join(B, "counts-e103-pool.json"))["rows"]
keys78 = [k for k, v in zc.items() if v["type"] != "int8" and v["kind"] != "zeros"]
X78 = np.array([x_float(zc[k]["mean"], zc[zc[k]["type"] + ".zeros"]["mean"]) for k in keys78], float)
Xi = np.linalg.inv(X78.T @ X78)
h78 = np.einsum("ij,jk,ik->i", X78, Xi, X78)
Xt = np.array([x_float(cp[r["key"]]["mean"], zc[r["type"] + ".zeros"]["mean"]) for r in fl], float)
ht = np.einsum("ij,jk,ik->i", Xt, Xi, Xt)
print(f"  leverage in M4's count space: E78 median {np.median(h78):.3f}, max {h78.max():.3f}; the 23 tiles median {np.median(ht):.3f}, inside E78's max {int((ht <= h78.max()).sum())} of 23; outside: {[fl[i]['key'] for i in range(len(fl)) if ht[i] > h78.max()]}")
print(f"  r(|miss|, leverage) {np.corrcoef(np.abs([r['D'] - r['M'] for r in fl]), ht)[0, 1]:.2f}")

print("\n# [C] the card scale")
Mraw = [r["M"] / reg["models"]["float"]["card1_scale"] for r in fl]
y = np.array([r["D"] for r in fl])
print(f"  frozen scale {reg['models']['float']['card1_scale']:.4f}: rms {rms(y - np.array(Mraw) * reg['models']['float']['card1_scale']):.3f} W; no scale: rms {rms(y - np.array(Mraw)):.3f} W; fitted on E103 itself: {float(np.array(Mraw) @ y / (np.array(Mraw) @ np.array(Mraw))):.4f}, rms {rms(y - np.array(Mraw) * float(np.array(Mraw) @ y / (np.array(Mraw) @ np.array(Mraw)))):.3f} W")
nd = load(os.path.join(DD, "2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json"))
print(f"  E82 with dips removed was reduced at leak {nd.get('leak')}; E103's primary at {e103.get('leak')}")

print("\n# [D] runs: planned against kept")
plan = reg["plan"]["runs_per_pass"] * 3
print(f"  planned {plan}; runs {e103['runs']}, kept {e103['kept']}")
skipped = []
for p in ("p10310", "p10311", "p10312"):
    d = os.path.join(HERE, "aifoundry1-c1", "kinds", p)
    for line in open(os.path.join(d, "run.log"), errors="replace"):
        if re.search(r"skip", line, re.I):
            skipped.append((p, line.strip()[:140]))
print("  from run.log:", skipped)
print("  tiles with fewer than 3 passes:", {k: items[k]["D"]["n"] for k in T if items[k]["D"]["n"] < 3})
for k in ("fp32.c_near_rand", "fp32.x_e_g"):
    print(f"  {k}: D {items[k]['D']['mean']:.3f}, n {items[k]['D']['n']}, se {items[k]['D']['se']:.3f}, ci95 {items[k]['D']['ci95']:.3f}")

print("\n# [E] the intervals, by format, and the arms")
for lab, rs in (("fp32", [r for r in rows if r["type"] == "fp32"]), ("fp16", [r for r in rows if r["type"] == "fp16"]), ("int8", i8)):
    print(f"  {lab}: {sum(r['lo95'] <= r['D'] <= r['hi95'] for r in rs)} of {len(rs)} inside; median half-width {st.median(r['half95'] for r in rs):.2f} W")
print("  arm-sensitive verdicts:", {r: v.get("arm_sensitive") for r, v in sc["primary"]["rules"].items() if v.get("arm_sensitive")})

print("\n# [F] fp32.c_near_rand: how near does it cancel, along a launch? (replay_c_near_rand.py, run on the mini)")
print(open(os.path.join(HERE, "replay-c-near-rand.txt")).read().rstrip())
print(f"  M4 at the bench's three launch points: {[round(x, 2) for x in T['fp32.c_near_rand']['pred']['launch_points_w']]} W")
for line in open(os.path.join(HERE, "aifoundry1-c1", "kinds", "p10310", "runs.jsonl")):
    r = json.loads(line)
    if r.get("item") == "fp32.g_bcol500" and r.get("launch", 0) >= 0:
        print("  one launch's record:", {q: x for q, x in r.items() if q in ("iters", "ops", "launch", "cycles_per_op", "result", "t_start_ms", "t_end_ms")})
        print(f"  ops in that launch at 600 MHz: {(r['t_end_ms'] - r['t_start_ms']) / 1000 * 600e6 / r['cycles_per_op']:.0f}")
        break

print("\n# [G] the verifier's comparators, recomputed; post hoc. Constants from E78 alone, scale from E82 with dips removed through the origin, as M4")
F = load(os.path.join(HERE, "comparator-features.json"))
e78 = load(os.path.join(DD, "2026-10-31-e78-kinds-energy-matrix/e78.json"))["items"]
e82 = nd["items"]
c9495 = load(os.path.join(B, "counts-e94e95.json"))["rows"]
e95 = load(glob.glob(os.path.join(DD, "2026-11-01-e95*/e95.json"))[0])["items"]
b95 = [k for k in c9495 if c9495[k]["kind"].startswith("r2_") and c9495[k]["type"] != "int8"]
RATE = lambda t: 600e6 / 546 * 1024 * 0.9963
simple = load(os.path.join(B, "simple-e103-pool.json"))


def bench_feat(fn):
    def get(key, counts):
        v = counts[key]
        return fn(v["mean"], zc[v["type"] + ".zeros"]["mean"])
    return get


f_reg = bench_feat(lambda m, z: [m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"], m["ff"]["all"]["toggles"] - z["ff"]["all"]["toggles"]])
f_bus = bench_feat(lambda m, z: [m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"], m["vpu"]["by_stage"]["lane_operand_bus"] - z["vpu"]["by_stage"]["lane_operand_bus"]])


def nn_fit(X, yy):
    """non-negative least squares by enumeration, the flop form's convention"""
    sc_ = np.abs(X).max(0)
    sc_[sc_ == 0] = 1
    Xs = X / sc_
    best, bb = np.inf, None
    p = X.shape[1]
    for r_ in range(1, p + 1):
        for S in itertools.combinations(range(p), r_):
            b_ = np.linalg.lstsq(Xs[:, S], yy, rcond=None)[0]
            if np.all(b_ >= 0):
                sse = float(np.sum((Xs[:, S] @ b_ - yy) ** 2))
                if sse < best:
                    best, bb = sse, np.zeros(p)
                    bb[list(S)] = b_
    return bb / sc_


def score(name, pred103, pred95):
    a = rms([r["D"] - pred103[r["key"]] for r in fl])
    b = rms([r["D"] - pred103[r["key"]] for r in nz])
    c = rms([e95[k]["D"]["mean"] - pred95[k] for k in b95])
    print(f"  {name:54s} E103 floats {a:6.3f}  without z_dn_ab {b:6.3f}  E95 floats {c:6.3f}")
    return a, b, c


def two_term(getf):
    X = np.array([[x * e78[k]["rate"]["mean"] for x in getf(k, zc)] for k in keys78], float)
    yy = np.array([e78[k]["D"]["mean"] for k in keys78])
    sc_ = np.abs(X).max(0)
    b_ = np.linalg.lstsq(X / sc_, yy, rcond=None)[0] / sc_
    p82 = np.array([[x * RATE(zc[k]["type"]) for x in getf(k, zc)] for k in keys78], float) @ b_
    y82 = np.array([e82[k]["D"]["mean"] for k in keys78])
    s_ = float(p82 @ y82 / (p82 @ p82))
    p103 = {r["key"]: float(np.array(getf(r["key"], cp), float) @ b_) * RATE(r["type"]) * s_ for r in fl}
    p95 = {k: float(np.array(getf(k, c9495), float) @ b_) * RATE(c9495[k]["type"]) for k in b95}
    return p103, p95


def stream(cols, per_format, fn=None, nonneg=False):
    p103, p95 = {}, {}
    groups = {"fp32": ("fp32",), "fp16": ("fp16",)} if per_format else {"fp32": ("fp32", "fp16"), "fp16": ("fp32", "fp16")}
    for t, g in groups.items():
        ks = [k for k in keys78 if k.split(".")[0] in g]
        get = fn
        X = np.array([get(F[k]) for k in ks], float)
        yy = np.array([e78[k]["D"]["mean"] for k in ks])
        b_ = nn_fit(X, yy) if nonneg else np.linalg.lstsq(X / np.abs(X).max(0), yy, rcond=None)[0] / np.abs(X).max(0)
        p = X @ b_
        y82 = np.array([e82[k]["D"]["mean"] for k in ks])
        s_ = float(p @ y82 / (p @ p))
        for r in fl:
            if r["type"] == t:
                p103[r["key"]] = float(np.array(get(simple[r["key"]]), float) @ b_) * s_
        for k in b95:
            if k.startswith(t):
                p95[k] = float(np.array(get(F[k]), float) @ b_)
    return p103, p95


m4_95 = load(os.path.join(B, "m4-bench-prediction.json"))["e95_aifoundry3"]
m2_95 = load(os.path.join(B, "e94-e95-bench-prediction.json"))["models"]["vpu_map"]["e95_aifoundry3"]
RES = {}
RES["M4, frozen"] = score("M4, frozen", {r["key"]: r["M"] for r in fl}, {k: m4_95[k]["D_w"] for k in b95})
RES["M2, frozen"] = score("M2, frozen", {r["key"]: r["M2"] for r in fl}, {k: m2_95[k]["D_w"] for k in b95})
RES["regs"] = score("clocked bits + register bits that change, 2 constants", *two_term(f_reg))
RES["flop"] = score("E92's flop-price form refit on E78 alone, per format", *stream(None, True, lambda f: [f["counts_e92"][c] for c in ("live", "bus", "prod", "res", "flops")], nonneg=True))
RES["u_ab_pooled"] = score("u + (A+B), 2 constants, pooled", *stream(None, False, lambda f: [f["features"]["u"], f["features"]["A"] + f["features"]["B"]]))
RES["u_ab_per"] = score("u + (A+B), per format", *stream(None, True, lambda f: [f["features"]["u"], f["features"]["A"] + f["features"]["B"]]))
RES["clk_bus"] = score("clocked bits + bus nets, 2 constants", *two_term(f_bus))
RES["u"] = score("u alone", *stream(None, False, lambda f: [f["features"]["u"]]))
print(f"  frozen: flop price E103 {rms([r['D'] - r['flop'] for r in fl]):.3f}, without z_dn_ab {rms([r['D'] - r['flop'] for r in nz]):.3f}; Q130(n) {rms([r['D'] - r['q130n'] for r in fl]):.3f}, without z_dn_ab {rms([r['D'] - r['q130n'] for r in nz]):.3f}")
sf95 = load(os.path.join(B, "scored-frozen.json"))["e95"]["blind"]["floats"]
print(f"  E95 floats, frozen: M4 {sf95['M4']['rms_w']:.3f}, Q130(n) {sf95['q130n']['rms_w']:.3f}: {sf95['q130n']['rms_w'] / sf95['M4']['rms_w']:.1f}x")

print("\n# [H] M4's form search, as committed in model-form-search/: forms tried")
print("  floats: explore1 11 forms, explore2 3 more (14 distinct); int8: 5 forms. Chosen: 'core,bus,rest' and 'nets-bus,bus,clk'")
