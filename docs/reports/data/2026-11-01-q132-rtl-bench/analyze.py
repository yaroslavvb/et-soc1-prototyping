#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Set the bench's counts beside the card's watts: E78 first, a plain fit, then out of sample.

    analyze.py --counts <dir with counts-*.json> --data <docs/reports/data> --out analysis.json

The model has two terms, and they are the two things the bench now counts:

    D(kind) = rate * ( k * (nets(kind) - nets(zeros)) + a * (clocked(kind) - clocked(zeros)) )

D is switching power over the type's own zeros, `rate` the card's ops a second over all 1,024 minions (E78's own, per item),
nets the merged-net toggles per op, clocked the register bits that get a clock edge with their enable high per op. k and a are in
joules per toggle and per clocked bit, at 600 MHz and 522 mV. Everything is a difference from zeros, so a gauge cannot enter.
Measured numbers come from the committed JSON of each experiment: E78, E90, E86 (aifoundry3); E88 (aifoundry1 card 1, 499 mV: its
predictions are scaled by (V/V_E78)^2); E65, E67 (aifoundry3, single-bit prices).
"""
import argparse
import json
import math
import os

import numpy as np

CPO = {"fp32": 546, "fp16": 546, "int8": 318}
V_E78 = None


def load(p):
    return json.load(open(p))


def rows_from(counts_path, measured, zeros_counts, rate_fallback=None):
    """-> list of dicts with D, dnets*, dclk*, rate"""
    c = load(counts_path)["rows"]
    out = []
    for k, v in c.items():
        t, name = v["type"], v["kind"]
        m = v["mean"]
        z = zeros_counts[t + ".zeros"]["mean"]
        item = measured.get(k) if measured else None
        D = item["D"]["mean"] if item and isinstance(item.get("D"), dict) else None
        se = item["D"].get("se") if item and isinstance(item.get("D"), dict) else None
        rate = item["rate"]["mean"] if item and isinstance(item.get("rate"), dict) else 600e6 / CPO[t] * 1024 * 0.9963
        out.append({
            "key": k, "type": t, "kind": name, "D": D, "D_se": se, "rate": rate,
            "nets_unit": m["unit"]["nets_hier"], "nets2_unit": m["unit"]["nets_hier2"],
            "nets_vpu": m["vpu"]["nets_hier"], "nets2_vpu": m["vpu"]["nets_hier2"],
            "clk": m["ff"]["all"]["clocked"], "ff_tog": m["ff"]["all"]["toggles"],
            "by_stage_vpu": m["vpu"]["by_stage"], "by_stage_unit": m["unit"]["by_stage"],
            "dnets_unit": m["unit"]["nets_hier"] - z["unit"]["nets_hier"],
            "dnets2_unit": m["unit"]["nets_hier2"] - z["unit"]["nets_hier2"],
            "dnets_vpu": m["vpu"]["nets_hier"] - z["vpu"]["nets_hier"],
            "dnets2_vpu": m["vpu"]["nets_hier2"] - z["vpu"]["nets_hier2"],
            "dclk": m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"],
            "dclk_unit": (m["ff"]["txfma"]["clocked"] + m["ff"]["tima"]["clocked"]) - (z["ff"]["txfma"]["clocked"] + z["ff"]["tima"]["clocked"]),
            "dtog": m["ff"]["all"]["toggles"] - z["ff"]["all"]["toggles"],
            "valid": m["valid_slots"], "miss": m["check_mismatch"], "cycles": m["cycles"],
        })
    return out


def design(rows, cols):
    return np.array([[r[c] * r["rate"] for c in cols] for r in rows], float)


def lstsq(rows, cols):
    X = design(rows, cols)
    y = np.array([r["D"] for r in rows], float)
    sc = np.where(X.max(axis=0) > 0, X.max(axis=0), 1.0)
    b, *_ = np.linalg.lstsq(X / sc, y, rcond=None)
    return b / sc


def stats(y, p):
    y, p = np.array(y, float), np.array(p, float)
    r = float(np.corrcoef(y, p)[0, 1]) if len(y) > 2 and np.std(p) > 0 else None
    def rank(a):
        o = a.argsort()
        rk = np.empty(len(a))
        rk[o] = np.arange(len(a))
        return rk
    rho = float(np.corrcoef(rank(y), rank(p))[0, 1]) if len(y) > 2 else None
    return {"n": len(y), "rms_w": float(np.sqrt(((y - p) ** 2).mean())), "bias_w": float((p - y).mean()), "worst_w": float(np.abs(y - p).max()), "pearson_r": r, "spearman_rho": rho}


def fit_report(rows, cols):
    b = lstsq(rows, cols)
    p = design(rows, cols) @ b
    y = [r["D"] for r in rows]
    res = stats(y, p)
    res["coef_fJ"] = {c: float(x) * 1e15 for c, x in zip(cols, b)}
    loo = []
    for i in range(len(rows)):
        tr = rows[:i] + rows[i + 1:]
        bi = lstsq(tr, cols)
        loo.append(float((design([rows[i]], cols) @ bi)[0]))
    res["loo"] = stats(y, loo)
    res["resid"] = {r["key"]: float(r["D"] - q) for r, q in zip(rows, p)}
    return res


def apply_frozen(rows, cols, b, vscale=1.0):
    rows = [r for r in rows if r["D"] is not None]
    p = (design(rows, cols) @ b) * vscale
    res = stats([r["D"] for r in rows], p)
    res["pred"] = {r["key"]: {"D": r["D"], "pred": float(q)} for r, q in zip(rows, p)}
    return res


def ladder(hl_path, base, items, passes=None):
    """Price of each item over its zero in E65/E67's raw runs: per-pass mean difference of p80, then the mean over passes."""
    h = load(hl_path)
    runs = [r for r in h["runs"] if not r.get("fail") and r.get("on_protocol", True) and r.get("p80") is not None]
    byp = {}
    for r in runs:
        byp.setdefault(r["pass"], {}).setdefault(r["item"], []).append(r["p80"])
    out = {}
    for it in items:
        b = base(it) if callable(base) else base
        d = []
        for p, x in byp.items():
            if it in x and b in x:
                d.append(sum(x[it]) / len(x[it]) - sum(x[b]) / len(x[b]))
        if d:
            out[it] = {"D": float(np.mean(d)), "n": len(d), "se": float(np.std(d, ddof=1) / math.sqrt(len(d))) if len(d) > 1 else None}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cd, dd = a.counts, a.data
    e78 = load(f"{dd}/2026-10-31-e78-kinds-energy-matrix/e78.json")
    zc = load(f"{cd}/counts-v2.json")["rows"]
    k78 = rows_from(f"{cd}/counts-v2.json", e78["items"], zc)
    res = {"e78_v_mean": e78["v_mean"]}
    res["functional"] = {"kinds": len(k78), "points_with_mismatch": sum(1 for r in zc.values() for p in r["points"] if p["check_mismatch"]),
                         "words_checked": sum(p["check_words"] for r in zc.values() for p in r["points"])}
    res["cycles"] = {t: sorted({round(r["cycles"], 1) for r in k78 if r["type"] == t}) for t in CPO}

    float_rows = [r for r in k78 if r["type"] in ("fp32", "fp16")]
    variants = {"vpu_hier": ["dnets_vpu", "dclk"], "vpu_hier2": ["dnets2_vpu", "dclk"], "unit_hier": ["dnets_unit", "dclk"], "unit_hier2": ["dnets2_unit", "dclk"],
                "vpu_hier_only": ["dnets_vpu"], "clk_only": ["dclk"], "ff_toggles_clk": ["dtog", "dclk"]}
    res["fit_e78"] = {}
    for scope, sel in (("fp32", "fp32"), ("fp16", "fp16"), ("int8", "int8"), ("fp32+fp16", None)):
        rows = float_rows if sel is None else [r for r in k78 if r["type"] == sel]
        rows = [r for r in rows if r["kind"] != "zeros"]
        res["fit_e78"][scope] = {n: fit_report(rows, c) for n, c in variants.items()}
    # across formats
    fp32 = [r for r in k78 if r["type"] == "fp32" and r["kind"] != "zeros"]
    fp16 = [r for r in k78 if r["type"] == "fp16" and r["kind"] != "zeros"]
    int8 = [r for r in k78 if r["type"] == "int8" and r["kind"] != "zeros"]
    res["across_formats"] = {}
    for n, c in variants.items():
        res["across_formats"][n] = {
            "fp32_to_fp16": {kk: vv for kk, vv in apply_frozen(fp16, c, lstsq(fp32, c)).items() if kk != "pred"},
            "fp16_to_fp32": {kk: vv for kk, vv in apply_frozen(fp32, c, lstsq(fp16, c)).items() if kk != "pred"},
            "float_to_int8": {kk: vv for kk, vv in apply_frozen(int8, c, lstsq(fp32 + fp16, c)).items() if kk != "pred"},
        }
    # frozen coefficients from E78's float kinds, applied to other experiments
    res["other_experiments"] = {}
    for var in ("vpu_hier", "vpu_hier2"):
        cols = variants[var]
        b = lstsq([r for r in float_rows if r["kind"] != "zeros"], cols)
        b8 = lstsq(int8, cols)
        res.setdefault("frozen_coef_fJ", {})[var] = {"float": {c: float(x) * 1e15 for c, x in zip(cols, b)}, "int8": {c: float(x) * 1e15 for c, x in zip(cols, b8)}}
        out = {}
        for name, jf, vs in (("e90", "2026-10-31-e90-signs-spread/e90.json", None), ("e86", "2026-10-31-e86-real-tensors-energy/e86.json", None),
                             ("e88", "2026-10-31-e88-result-path/e88.json", None), ("e82", None, None)):
            if name == "e82":
                j = load(f"{dd}/2026-10-31-e82-kinds-aifoundry1/e82.json")
                rows = rows_from(f"{cd}/counts-v2.json", j["items"], zc)
            else:
                if not os.path.exists(f"{cd}/counts-{name}.json"):
                    continue
                j = load(f"{dd}/{jf}")
                rows = rows_from(f"{cd}/counts-{name}.json", j["items"], zc)
            scale = (j["v_mean"] / e78["v_mean"]) ** 2
            rows = [r for r in rows if r["D"] is not None and r["kind"] != "zeros"]
            fl = [r for r in rows if r["type"] != "int8"]
            i8 = [r for r in rows if r["type"] == "int8"]
            o = {"v_mean": j["v_mean"], "scale": scale}
            if fl:
                o["float"] = apply_frozen(fl, cols, b, scale)
            if i8:
                o["int8"] = apply_frozen(i8, cols, b8, scale)
            out[name] = o
        # E65 and E67: prices of one flipped bit, over a zero that clocks the same bits
        if os.path.exists(f"{cd}/counts-hl.json"):
            hl = load(f"{cd}/counts-hl.json")["rows"]
            lad = {}
            e65 = ladder(f"{dd}/2026-10-26-e65-bit-prices-hart-ladder/hl.json", "lq_h0", [f"bit_{j}" for j in range(32)])
            e65pi = ladder(f"{dd}/2026-10-26-e65-bit-prices-hart-ladder/hl.json", "lb_h0", [f"bpi_{j}" for j in (0, 8, 11, 16, 22)])
            e67 = ladder(f"{dd}/2026-10-27-e67-a-side-bit-prices/hl-clean.json", lambda it: "aq_e64" if it == "abit_30" else "aq_h0", [f"abit_{j}" for j in range(32)])
            knet = b[0]
            for nm, tbl, bases in (("e65_bit", e65, lambda it: "lq_h0"), ("e65_bpi", e65pi, lambda it: "lb_h0"), ("e67_abit", e67, lambda it: "aq_e64" if it == "abit_30" else "aq_h0")):
                ys, ps, keep = [], [], {}
                nk = "nets_hier" if var == "vpu_hier" else "nets_hier2"
                for it, v in tbl.items():
                    kk = "fp32." + it
                    if kk not in hl:
                        continue
                    z = hl["fp32." + bases(it)]["mean"]
                    m = hl[kk]["mean"]
                    d = m["vpu"][nk] - z["vpu"][nk]
                    p = d * knet * (600e6 / 546 * 1024 * 0.9963)
                    ys.append(v["D"]); ps.append(p)
                    keep[it] = {"D": v["D"], "se": v["se"], "pred": float(p), "dnets_per_mac": d / 4096,
                                "stage": {s: (m["vpu"]["by_stage"][s] - z["vpu"]["by_stage"][s]) / 4096 for s in m["vpu"]["by_stage"]},
                                "ffclk": (m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"]) / 4096,
                                "fftog": (m["ff"]["all"]["toggles"] - z["ff"]["all"]["toggles"]) / 4096}
                st = stats(ys, ps)
                st["items"] = keep
                # a free slope, to say whether shape and scale are separately right
                A = np.array(ps)[:, None]
                sl = float(np.linalg.lstsq(A, np.array(ys), rcond=None)[0][0])
                st["slope_measured_over_pred"] = sl
                lad[nm] = st
            out["ladder"] = lad
        res["other_experiments"][var] = out
    # the split of random data's watts, by the model
    def split(key, var="vpu_hier"):
        cols = variants[var]
        b = lstsq([r for r in float_rows if r["kind"] != "zeros"], cols) if key.split(".")[0] != "int8" else lstsq(int8, cols)
        r = next(x for x in k78 if x["key"] == key)
        out = {"D": r["D"], "clocked_W": float(r["dclk"] * r["rate"] * b[1]), "nets_W": float(r[cols[0]] * r["rate"] * b[0]),
               "stages_W": {s: float(v * r["rate"] * b[0]) for s, v in r["by_stage_vpu"].items() if v}, "stage_nets_per_op": {s: v for s, v in r["by_stage_vpu"].items() if v},
               "clocked_bits_per_op": r["clk"]}
        return out
    res["split"] = {k: split(k) for k in ("fp32.randn", "fp16.randn", "int8.full", "fp32.ones")}
    # the table of all kinds
    res["kinds"] = [{kk: r[kk] for kk in ("key", "D", "D_se", "rate", "nets_unit", "nets2_unit", "nets_vpu", "nets2_vpu", "clk", "ff_tog", "valid", "miss", "by_stage_vpu", "by_stage_unit")} for r in k78]
    json.dump(res, open(a.out, "w"), indent=1)
    # a readable digest
    for scope, d in res["fit_e78"].items():
        print(scope)
        for n, f in d.items():
            print(f"   {n:16s} rms {f['rms_w']:.3f}  loo {f['loo']['rms_w']:.3f}  r {f['pearson_r']:.4f} rho {f['spearman_rho']:.4f}  worst {f['worst_w']:.2f}  coef {({c: round(v, 3) for c, v in f['coef_fJ'].items()})}")
    print(json.dumps(res["across_formats"], indent=0)[:1400])
    for var, o in res["other_experiments"].items():
        for name, x in o.items():
            if name == "ladder":
                for nm, st in x.items():
                    print(var, nm, {kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in st.items() if kk != "items"})
                continue
            for t in ("float", "int8"):
                if t in x:
                    print(var, name, t, {kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in x[t].items() if kk != "pred"})
    print(json.dumps(res["split"], indent=0)[:1800])


if __name__ == "__main__":
    main()
