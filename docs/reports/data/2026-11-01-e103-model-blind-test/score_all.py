#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Step 3 of Q132's item 6: every experiment the bench's models have a frozen prediction for, then everything else they can be set beside, each labelled by what the clock allows.

    python3 score_all.py > score_all.txt       # from this directory; writes score_all.json

Blind means the predictions were committed before that experiment's data reached main, and I read none of it first. "Constants first" means the model's constants were committed before the data
and the counts came from a run that predates it, but the arithmetic was done afterwards; nothing in it is free. Post hoc means the form was chosen after that data was read.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.abspath(os.path.join(HERE, ".."))
B = os.path.join(DD, "2026-11-01-q132-rtl-bench")
sys.path.insert(0, B)
from analyze import ladder  # noqa: E402
from predict_m4 import fit, x_float, x_int8  # noqa: E402

K = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds"))
load = lambda p: json.load(open(p))
reg = load(os.path.join(K, "predictions-e103.json"))
bF = np.array([reg["models"]["float"]["coef_fJ"][q] for q in ("k_core", "k_bus", "k_rest", "a_clocked")]) * 1e-15
bI = np.array([reg["models"]["int8"]["coef_fJ"][q] for q in ("k_nets", "k_bus", "a_clocked")]) * 1e-15
sF, sI = reg["models"]["float"]["card1_scale"], reg["models"]["int8"]["card1_scale"]
CPO = {"fp32": 546, "fp16": 546, "int8": 318}
RATE = {t: 600e6 / c * 1024 * 0.9963 for t, c in CPO.items()}
zc = load(os.path.join(B, "counts-v2.json"))["rows"]


def s(rows, q="p"):
    """rows have D and a prediction"""
    y = np.array([r["D"] for r in rows])
    p = np.array([r[q] for r in rows])
    return {"n": len(y), "rms_w": float(np.sqrt(np.mean((y - p) ** 2))), "bias_w": float(np.mean(p - y)), "worst_w": float(np.max(np.abs(y - p))),
            "r": float(np.corrcoef(y, p)[0, 1]) if len(y) > 2 and np.std(p) > 0 else None}


def m4(m, z, t, rate=None, card1=False):
    rate = rate or RATE[t]
    if t == "int8":
        return float((np.array(x_int8(m, z), float) * rate) @ bI) * (sI if card1 else 1.0)
    return float((np.array(x_float(m, z), float) * rate) @ bF) * (sF if card1 else 1.0)


def fmt_split(rows, q="p"):
    o = {}
    for lab, f in (("floats", lambda r: r["type"] != "int8"), ("fp32", lambda r: r["type"] == "fp32"), ("fp16", lambda r: r["type"] == "fp16"), ("int8", lambda r: r["type"] == "int8")):
        sel = [r for r in rows if f(r) and r.get(q) is not None]
        if len(sel) >= 2:
            o[lab] = s(sel, q)
    return o


def kinds_rows(counts, items, card1=False):
    out = []
    for k, v in counts.items():
        t, name = v["type"], v["kind"]
        it = items.get(k) or items.get(f"{t}.real_{name}")
        if name == "zeros" or not it or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
            continue
        rate = it["rate"]["mean"] if isinstance(it.get("rate"), dict) else None
        out.append({"key": k, "type": t, "D": it["D"]["mean"], "p": m4(v["mean"], zc[t + ".zeros"]["mean"], t, rate, card1)})
    return out


res = {"blind": {}, "constants_first": {}, "post_hoc": {}, "clock": {}}
# ---- E92: the two-term model on hier2, frozen de545f0c, data 4e8eb836
e92 = load(os.path.join(DD, "2026-11-01-e92-sign-split", "e92.json"))["items"]
fz = load(os.path.join(B, "e92-bench-prediction-frozen.json"))["variants"]["nets_hier2"]["tiles_D_over_zeros_w"]
rows = [{"key": k, "type": k.split(".")[0], "D": e92[k]["D"]["mean"], "p": v} for k, v in fz.items() if k in e92 and isinstance(e92[k].get("D"), dict)]
res["blind"]["E92, two terms (hier2)"] = {"frozen": "de545f0c", "data": "4e8eb836", "card": "aifoundry3", "by_format": fmt_split(rows)}
# ---- E95: M2 2b7ece4a, M4 and I3 b995463e, data ab23b1aa
sf = load(os.path.join(B, "scored-frozen.json"))
r95 = [r for r in sf["e95"]["rows"] if r["blind"]]
for r in r95:
    r["p"] = r["M4"]
res["blind"]["E95, M4 and I3"] = {"frozen": "b995463e", "data": "ab23b1aa", "card": "aifoundry3", "by_format": fmt_split(r95)}
for r in r95:
    r["p2"] = r["M2"]
res["blind"]["E95, M2"] = {"frozen": "2b7ece4a", "data": "ab23b1aa", "card": "aifoundry3", "by_format": fmt_split(r95, "p2")}
res["blind"]["E95, Q130(n)'s (a), the null"] = {"frozen": "6ae4c3d5", "data": "ab23b1aa", "card": "aifoundry3", "by_format": fmt_split(r95, "q130n")}
# ---- E103: all frozen b5f1e5d7
e103 = load(os.path.join(HERE, "e103.json"))["items"]
r103 = [{"key": k, "type": t["type"], "D": e103[k]["D"]["mean"], "p": t["pred"]["M"], "M2": t["pred"]["M2"], "q130n": t["pred"]["q130n"], "flop": t["pred"]["flop"], "gate": t["pred"]["gate"], "group": t["group"], "lo": t["pred"]["lo95"], "hi": t["pred"]["hi95"], "T": t["pred"]["terms_w"][-1]} for k, t in reg["tiles"].items()]
res["blind"]["E103, M4 and I3"] = {"frozen": "b5f1e5d7 (the constants b995463e)", "card": "aifoundry1 card 1, E82's scale", "by_format": fmt_split(r103)}
res["blind"]["E103, M2"] = {"frozen": "b5f1e5d7", "card": "aifoundry1 card 1, E82's scale", "by_format": fmt_split(r103, "M2")}
res["blind"]["E103, Q130(n), the null"] = {"frozen": "b5f1e5d7", "card": "aifoundry1 card 1, E82's scale", "by_format": fmt_split(r103, "q130n")}
res["blind"]["E103, E92's flop price"] = {"frozen": "b5f1e5d7", "card": "aifoundry1 card 1, E82's scale", "by_format": fmt_split([r for r in r103 if r["flop"] is not None], "flop")}
pool = [dict(r, card="a3") for r in r95] + [dict(r, card="c1") for r in r103]
res["blind"]["E95 + E103 pooled, M4 and I3"] = {"by_format": fmt_split(pool), "null_q130n": fmt_split(pool, "q130n"), "M2": fmt_split([dict(r, M2x=r["M2"]) for r in pool], "M2x")}
# ---- E102: M2 frozen in its registration (47060961), data 1e76be87; M4's constants first
e102d = os.path.join(DD, "2026-11-01-e102-balanced-bit-prices")
sc = load(os.path.join(e102d, "scored.json"))["primary"]
c102 = load(os.path.join(e102d, "bench", "counts-e102.json"))["rows"]
t102 = load(os.path.join(K, "e102", "e102.json"))["tiles"]
GROUPS = {"fp32 B balanced": lambda e: e["type"] == "fp32" and e["layout"] == "bp", "fp32 B all-in": lambda e: e["type"] == "fp32" and e["layout"] == "bj", "fp32 A balanced": lambda e: e["type"] == "fp32" and e["layout"] == "ap",
          "fp32 A all-in": lambda e: e["type"] == "fp32" and e["layout"] == "aj", "fp16 balanced": lambda e: e["type"] == "fp16" and e["layout"] in ("bp", "ap"), "fp16 all-in": lambda e: e["type"] == "fp16" and e["layout"] in ("bj", "aj"), "int8 B": lambda e: e["type"] == "int8"}
res["constants_first"]["E102"] = {}
for g, f in GROUPS.items():
    rows = []
    for name, e in sc["prices"].items():
        if not f(e) or e["board"]["W"]["mean"] is None:
            continue
        kind = f"{e['type']}.{name.split('@')[0].split('.', 1)[1]}"
        z = t102[kind].get("zero")
        if z is None or kind not in c102:
            continue
        zk = z if "." in z else f"{e['type']}.{z}"
        if zk not in c102:
            continue
        rows.append({"key": name, "type": e["type"], "D": e["board"]["W"]["mean"], "p": m4(c102[kind]["mean"], c102[zk]["mean"], e["type"], None, True), "M2": (e.get("predictions") or {}).get("bench_map")})
    if len(rows) >= 2:
        res["constants_first"]["E102"][g] = {"M4 or I3": s(rows), "M2, frozen in E102's registration": s([r for r in rows if r["M2"] is not None], "M2") if sum(1 for r in rows if r["M2"] is not None) >= 2 else None}
# ---- post hoc: M4's form was chosen after these were read
for name, j, c, card1 in (("E86", "2026-10-31-e86-real-tensors-energy/e86.json", "counts-e86.json", False), ("E90", "2026-10-31-e90-signs-spread/e90.json", "counts-e90.json", False), ("E92", "2026-11-01-e92-sign-split/e92.json", "counts-e92.json", False),
                          ("E82, with its own scale", "2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json", "counts-v2.json", True), ("E88", "2026-10-31-e88-result-path/e88.json", "counts-e88.json", True)):
    rows = kinds_rows(load(os.path.join(B, c))["rows"], load(os.path.join(DD, j))["items"], card1)
    res["post_hoc"][name] = fmt_split(rows)
c94 = {k: v for k, v in load(os.path.join(B, "counts-e94e95.json"))["rows"].items() if not v["kind"].startswith(("r2_", "real_"))}
res["post_hoc"]["E94"] = fmt_split(kinds_rows(c94, load(os.path.join(DD, "2026-11-01-e94-tile-spread", "e94.json"))["items"], True))
hl = load(os.path.join(B, "counts-hl.json"))["rows"]
e65f = os.path.join(DD, "2026-10-26-e65-bit-prices-hart-ladder/hl.json")
e67f = os.path.join(DD, "2026-10-27-e67-a-side-bit-prices/hl-clean.json")
e70f = os.path.join(DD, "2026-10-27-e70-saturation-ladder/hl.json")
e60f = os.path.join(DD, "2026-10-20-bitflip-ladder/hl.json")
LAD = [("E65, one B bit, A = 1", e65f, lambda it: "lq_h0", [f"bit_{j}" for j in range(32)]), ("E65, one B bit, A = pi", e65f, lambda it: "lb_h0", [f"bpi_{j}" for j in (0, 8, 11, 16, 22)]),
       ("E67, one A bit, B = 1", e67f, lambda it: "aq_e64" if it == "abit_30" else "aq_h0", [f"abit_{j}" for j in range(32)]), ("E67, one A bit, B = pi", e67f, lambda it: "ap_h0", [f"abp_{j}" for j in (0, 8, 11, 16, 22)]),
       ("E67, the two-flip grid", e67f, lambda it: "ix_z", [f"ix_{i}_{j}" for i in (0, 8, 16, 22) for j in (0, 8, 16, 22)] + [f"ix_a{i}" for i in (0, 8, 16, 22)] + [f"ix_b{j}" for j in (0, 8, 16, 22)]),
       ("E70, low bits", e70f, lambda it: "lq_h0", [f"lq_h{h}" for h in (1, 2, 3, 4, 6, 8, 12, 16, 23)]), ("E70, spread bits", e70f, lambda it: "lq_h0", [f"ls_h{h}" for h in (2, 3, 4, 6, 8, 12, 16)]),
       ("E70, A low bits", e70f, lambda it: "aq_h0", [f"alq_h{h}" for h in (1, 2, 4, 8, 12, 16, 23)]), ("E60, low bits, A = pi", e60f, lambda it: "lb_h0", [f"lb_h{h}" for h in (1, 2, 4, 8, 12, 16, 23)]),
       ("E60, A's order", e60f, lambda it: "lq_h0", [f"ord_{o}_{p}" for o in ("gray", "binary", "shuffled", "maxflip") for p in (0, 19)])]
res["post_hoc_ladders"] = {}
for name, f_, base, items in LAD:
    tbl = {}
    for b_ in sorted({base(i) for i in items}):
        tbl.update(ladder(f_, b_, [i for i in items if base(i) == b_]))
    rows = [{"key": it, "type": "fp32", "D": v["D"], "p": m4(hl["fp32." + it]["mean"], hl["fp32." + base(it)]["mean"], "fp32")} for it, v in tbl.items() if "fp32." + it in hl]
    st_ = s(rows)
    P = np.array([r["p"] for r in rows])
    st_["measured_over_predicted"] = float(P @ np.array([r["D"] for r in rows]) / (P @ P))
    res["post_hoc_ladders"][name] = st_
# ---- the fit
Xf, yf = [], []
for k, v in zc.items():
    t = v["type"]
    if t == "int8" or v["kind"] == "zeros":
        continue
    it = load(os.path.join(DD, "2026-10-31-e78-kinds-energy-matrix/e78.json"))["items"][k]
    Xf.append([c * it["rate"]["mean"] for c in x_float(v["mean"], zc[t + ".zeros"]["mean"])])
    yf.append(it["D"]["mean"])
Xf, yf = np.array(Xf), np.array(yf)
res["fit_on_e78"] = {"float": {"rms_w": reg["models"]["float"]["fit_rms_w"], "loo_rms_w": reg["models"]["float"]["loo_rms_w"], "n": reg["models"]["float"]["n_fit"]}, "int8": {"rms_w": reg["models"]["int8"]["fit_rms_w"], "loo_rms_w": reg["models"]["int8"]["loo_rms_w"], "n": reg["models"]["int8"]["n_fit"]}}
# ---- how far the constants move with everything in the fit: reported, nothing depends on it
def rows_x(counts, items, f, want):
    X, y = [], []
    for k, v in counts.items():
        t, name = v["type"], v["kind"]
        it = items.get(k) or items.get(f"{t}.real_{name}")
        if not want(t) or name == "zeros" or not it or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
            continue
        rate = it["rate"]["mean"] if isinstance(it.get("rate"), dict) else RATE[t]
        X.append([c * rate for c in f(v["mean"], zc[t + ".zeros"]["mean"])])
        y.append(it["D"]["mean"])
    return X, y


ce = load(os.path.join(B, "counts-e94e95.json"))["rows"]
cp = load(os.path.join(B, "counts-e103-pool.json"))["rows"]
SETS = [(zc, "2026-10-31-e78-kinds-energy-matrix/e78.json", 1.0), (load(os.path.join(B, "counts-e86.json"))["rows"], "2026-10-31-e86-real-tensors-energy/e86.json", 1.0), (load(os.path.join(B, "counts-e90.json"))["rows"], "2026-10-31-e90-signs-spread/e90.json", 1.0),
        (load(os.path.join(B, "counts-e92.json"))["rows"], "2026-11-01-e92-sign-split/e92.json", 1.0), ({k: v for k, v in ce.items() if v["kind"].startswith(("r2_", "real_"))}, "2026-11-01-e95-real-tensors-energy/e95.json", 1.0)]
res["refit_reported"] = {}
for fam, f, want, sc1, names in (("float", x_float, lambda t: t != "int8", sF, ["k_core", "k_bus", "k_rest", "a"]), ("int8", x_int8, lambda t: t == "int8", sI, ["k_nets", "k_bus", "a"])):
    X, y = [], []
    for c, j, sc_ in SETS:
        a, b_ = rows_x(c, load(os.path.join(DD, j))["items"], f, want)
        X += a
        y += b_
    n_a3 = len(y)
    b3 = fit(np.array(X, float), np.array(y, float))
    res["refit_reported"][fam] = {"aifoundry3 tiles (E78, E86, E90, E92, E95)": {"n": n_a3, "coef_fJ": dict(zip(names, [float(v) * 1e15 for v in b3])), "rms_w": float(np.sqrt(np.mean((np.array(y) - np.array(X) @ b3) ** 2)))}}
    # with card 1's tiles too, divided by the frozen scale
    Xa, ya = list(X), list(y)
    for c, j in ((zc, "2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json"), (load(os.path.join(B, "counts-e88.json"))["rows"], "2026-10-31-e88-result-path/e88.json"), (c94, "2026-11-01-e94-tile-spread/e94.json")):
        a, b_ = rows_x(c, load(os.path.join(DD, j))["items"], f, want)
        Xa += a
        ya += [v / sc1 for v in b_]
    for k, t in reg["tiles"].items():
        if want(t["type"]):
            Xa.append([c_ * RATE[t["type"]] for c_ in f(cp[k]["mean"], zc[t["type"] + ".zeros"]["mean"])])
            ya.append(e103[k]["D"]["mean"] / sc1)
    bA = fit(np.array(Xa, float), np.array(ya, float))
    res["refit_reported"][fam]["both cards, card 1 over the frozen scale, E103 included"] = {"n": len(ya), "coef_fJ": dict(zip(names, [float(v) * 1e15 for v in bA])), "rms_w": float(np.sqrt(np.mean((np.array(ya) - np.array(Xa) @ bA) ** 2)))}
# ---- the misses
res["largest_misses_blind"] = sorted([{"key": r["key"], "experiment": "E95" if r["card"] == "a3" else "E103", "D": r["D"], "p": r["p"], "miss_w": r["D"] - r["p"], "group": r.get("group")} for r in pool], key=lambda x: -abs(x["miss_w"]))[:14]
# ---- the A side under M2, on E103's tiles, for R8's context
a_side = [r for r in r103 if r["key"].split(".")[1].startswith(("h_a_", "o_a_"))]
res["a_side_M2_vs_M4_E103"] = {"M4_D_over_M": sum(r["D"] / r["p"] for r in a_side) / len(a_side), "M2_D_over_M": sum(r["D"] / r["M2"] for r in a_side) / len(a_side), "M4_bias_w": sum(r["p"] - r["D"] for r in a_side) / len(a_side), "M2_bias_w": sum(r["M2"] - r["D"] for r in a_side) / len(a_side)}
# ---- arms of E103's rules
sc103 = load(os.path.join(HERE, "scored.json"))
res["e103_arms_rms"] = {n: {"floats_rms_w": a["rules"]["E103-R1"].get("rms_w"), "int8_rms_w": a["rules"]["E103-R4"].get("rms_w")} for n, a in sc103["arms"].items()}
json.dump(res, open(os.path.join(HERE, "score_all.json"), "w"), indent=1)


def line(name, o):
    return f"{name:44s} " + "  ".join(f"{lab} n{x['n']} {x['rms_w']:.3f} ({x['bias_w']:+.2f})" for lab, x in o.items())


print("# BLIND: rms in W (bias, predicted minus measured)")
for n, v in res["blind"].items():
    print(line(n, v["by_format"]))
print("E95 + E103 null Q130(n):", {k: round(x["rms_w"], 3) for k, x in res["blind"]["E95 + E103 pooled, M4 and I3"]["null_q130n"].items()}, "M2:", {k: round(x["rms_w"], 3) for k, x in res["blind"]["E95 + E103 pooled, M4 and I3"]["M2"].items()})
print("# CONSTANTS FIRST: E102, board, over each item's own zero")
for g, v in res["constants_first"]["E102"].items():
    print(f"{g:20s} M4/I3 n{v['M4 or I3']['n']} {v['M4 or I3']['rms_w']:.3f} ({v['M4 or I3']['bias_w']:+.2f})" + (f"   M2 {v['M2, frozen in E102' + chr(39) + 's registration']['rms_w']:.3f}" if v["M2, frozen in E102's registration"] else ""))
print("# POST HOC: M4 and I3, form chosen after these")
for n, v in res["post_hoc"].items():
    print(line(n, v))
for n, v in res["post_hoc_ladders"].items():
    print(f"{n:30s} n{v['n']} rms {v['rms_w']:.3f} bias {v['bias_w']:+.2f} r {v['r']:.4f} measured/predicted {v['measured_over_predicted']:.3f}")
print("# refit, reported")
print(json.dumps(res["refit_reported"]))
print("# largest misses, blind")
for x in res["largest_misses_blind"]:
    print(f"{x['experiment']:5s} {x['key']:38s} D {x['D']:6.2f} predicted {x['p']:6.2f} miss {x['miss_w']:+.2f}  {x['group'] or ''}")
print(res["a_side_M2_vs_M4_E103"])
print(res["e103_arms_rms"])
