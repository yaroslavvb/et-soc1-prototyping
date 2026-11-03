#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q138(m), after verification (Mon 2 Nov 2026): post hoc checks of how M7's out-of-kind numbers are reported.

Nothing frozen changes. m7.json, fit_m7.py, predict_blind5.py and the committed loko-m7.json, rows-m7.json and
heat-rows-m7.json are read, never written, and no file of blind pool 5 is read.

    python3 posthoc_m7.py > posthoc-m7.txt      # writes posthoc-m7.json beside it (a few minutes)

1. aifoundry2's end-to-end burst score, split: the bursts the governor acts on (measured below 795 MHz) against the bursts
   pinned at 800 MHz; and the same score with the cap refitted leaving each kind out (the frozen score uses the cap that
   was fitted on all 56 bursts it scores).
2. The random-like kinds' burst clocks, measured and predicted.
3. glive against clk: their collinearity on the rows, the clk and gtr prices by form, and the rows that tell them apart.
4. Where the gains sit: the 50 rows of blind pools 3 and 4 (E115, E140) against the other rows, bootstrap over kinds.
5. The band's k: the pool rows' standardized residuals, where np.quantile lands, leave-one-pool-row-out coverage.
6. Heat at the measured run length: H2's ST term at each card's T_run, against the 4.5 s that predict_blind5.py uses.
7. zeros_S: the predictor's zeros S (M6's experiment list) against the list with E137 and E140 added.
8. Provenance: sha256 of every file in the tree that predict_blind5.py imports or reads apart from the pool's own files.
SPDX-License-Identifier: Apache-2.0
"""
import builtins
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# ---- 8 (first): record every file opened while predict_blind5's imports load and while its pool-independent reads run
OPENED = []
_open = builtins.open


def _rec_open(file, *a, **k):
    if isinstance(file, (str, os.PathLike)):
        OPENED.append(os.path.abspath(os.fspath(file)))
    return _open(file, *a, **k)


builtins.open = _rec_open
sys.path.insert(0, HERE)
import predict_blind5 as PB  # noqa: E402  (imports fit_m7, which imports fit_m6, m6_rows, fit_m5, make_kinds)
M7 = PB.M7
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e119"))
import make_predictions_e119 as M119  # noqa: E402  (imports predict_e83, surface_hpl, surface_hpl_t)
m7p = os.path.join(HERE, "m7.json")
m6p = os.path.join(M7.M6D, "m6.json")
m5p = os.path.join(M7.M5D, "m5.json")
m7, m6, m5 = (json.load(open(p)) for p in (m7p, m6p, m5p))
M7.zeros_counts()
ZS_FROZEN = {cc: PB.zeros_S(pref) for cc, pref in (("a3", "aifoundry3"), ("c1", "aifoundry1"))}
builtins.open = _open

sha = lambda p: hashlib.sha256(_open(p, "rb").read()).hexdigest()
load = lambda p: json.load(_open(p))
L = load(os.path.join(HERE, "loko-m7.json"))
ROWS = load(os.path.join(HERE, "rows-m7.json"))
HR = load(os.path.join(HERE, "heat-rows-m7.json"))
rng = np.random.default_rng(20261102)
OUT = {"_note": "Q138(m) posthoc_m7.py, after verification: post hoc, reported; nothing frozen changes; no pool-5 file read. "
                "Errors are measured - predicted unless a key says otherwise."}


def rms(v):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    return float(np.sqrt(np.mean(v ** 2))) if len(v) else float("nan")


def q95(v):
    v = np.sort(np.abs(np.asarray(v, float)))
    return float(np.quantile(v, 0.95)) if len(v) else None


def boot_diff(rows, a, b, n=4000):
    """rms(a) - rms(b) over rows, and its 95% interval resampling kinds with replacement"""
    kinds = sorted({r["kind"] for r in rows})
    byk = {k: [r for r in rows if r["kind"] == k] for k in kinds}
    d = []
    for _ in range(n):
        pick = rng.integers(0, len(kinds), len(kinds))
        rr = [r for i in pick for r in byk[kinds[i]]]
        d.append(rms([r[a] for r in rr]) - rms([r[b] for r in rr]))
    lo, hi = np.quantile(d, [0.025, 0.975])
    return {"n_rows": len(rows), "n_kinds": len(kinds), "rms_a_w": rms([r[a] for r in rows]), "rms_b_w": rms([r[b] for r in rows]),
            "diff_w": rms([r[a] for r in rows]) - rms([r[b] for r in rows]), "ci95_over_kinds_w": [float(lo), float(hi)]}


# ------------------------------------------------------------------ 1, 2: aifoundry2
A2 = L["aifoundry2"]
E2E = A2["end_to_end_from_M7_nested_D"]
BAND_MHZ, BAND_W = m7["aifoundry2"]["end_to_end_band"]["q95_abs_mhz"], m7["aifoundry2"]["end_to_end_band"]["q95_abs_board_w"]
GOVERNED_BELOW = 795.0


def score(rows):
    em = [r["mhz_meas"] - r["mhz_pred"] for r in rows]
    ew = [r["w_meas"] - r["w_pred"] for r in rows]
    return {"n": len(rows), "rms_mhz": rms(em), "q95_abs_mhz": q95(em), "rms_board_w": rms(ew), "q95_abs_board_w": q95(ew),
            "bias_board_pred_minus_meas_w": -float(np.mean(ew)), "inside_frozen_mhz_band": int(sum(abs(e) <= BAND_MHZ for e in em)),
            "inside_frozen_board_band": int(sum(abs(e) <= BAND_W for e in ew))}


P136 = load(os.path.join(ROOT, "tools", "claims-v3", "e136", "predictions-e136.json"))
rel = P136["relation"]
B = {int(k): v for k, v in rel["B"].items()}
SF = {int(k): v for k, v in rel["s_f"].items()}
CZ, XFER = rel["c_zeros_w"], rel["xfer"]
WB, SB = rel["burst"]
DD = M7.DD
cells = []
for d in ("2026-10-31-e80-kinds-speed", "2026-10-31-e83-kinds-speed-rest"):
    for lab, c in load(os.path.join(DD, d, "results.json"))["cells"].items():
        if c.get("burst_mhz") is None or c.get("c_w") is None:
            continue
        t, n = lab.split("/")
        cells.append({"exp": d.split("-")[3].upper(), "type": t, "kind": n, "burst_mhz": float(c["burst_mhz"]), "burst_w": float(c["burst_w"]),
                      "c_w": float(c["c_w"])})


def levels(c):
    return {f: B[f] + c * SF[f] for f in (600, 700, 800)}


def p_at(P, f):
    if f >= 800:
        return P[800]
    if f >= 700:
        return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
    return P[600] + (P[700] - P[600]) * (f - 600) / 100.0 if f >= 600 else P[600]


def clock(c, W, sig=SB):
    return M119.dither(levels(c), W, sig)[0]


def fitW(sub):  # fit_m7.a2_governor's golden-section fit, unchanged
    lo, hi = 50.0, 90.0
    e = lambda W: sum((clock(x["c_w"], W) - x["burst_mhz"]) ** 2 for x in sub)
    for _ in range(60):
        a, b = lo + (hi - lo) * 0.382, lo + (hi - lo) * 0.618
        if e(a) < e(b):
            hi = b
        else:
            lo = a
    return (lo + hi) / 2


nested_pred = {}
for fam in ("float", "int8"):
    for r in L["families"][fam]["row_errors"]:
        if r["exp"] == "E78" and r["card"] == "a3":
            nested_pred[r["key"]] = r["D"] - r["M7_nested_err_w"]


def e2e_rows(cap_of):
    out = []
    for x in cells:
        key = f"{x['type']}.{x['kind']}"
        Dp = 0.0 if x["kind"] == "zeros" else nested_pred.get(key)
        if Dp is None:
            continue
        c = CZ[x["type"]] + Dp / XFER
        W = cap_of(x)
        f = clock(c, W)
        out.append({"cell": f"{x['exp']}:{key}", "mhz_meas": x["burst_mhz"], "mhz_pred": f, "w_meas": x["burst_w"], "w_pred": p_at(levels(c), f), "cap_w": W})
    return out


W_all = fitW(cells)
full = e2e_rows(lambda x: W_all)
frozen_rows = {r["cell"]: r for r in E2E["rows"]}
check = max(max(abs(round(r["mhz_pred"], 1) - frozen_rows[r["cell"]]["mhz_pred"]), abs(round(r["w_pred"], 2) - frozen_rows[r["cell"]]["w_pred"])) for r in full)
caps = {}
for kk in sorted({(x["type"], x["kind"]) for x in cells}):
    caps[kk] = fitW([x for x in cells if (x["type"], x["kind"]) != kk])
loko_cap = e2e_rows(lambda x: caps[(x["type"], x["kind"])])
gov = lambda rows: [r for r in rows if r["mhz_meas"] < GOVERNED_BELOW]
pin = lambda rows: [r for r in rows if r["mhz_meas"] >= GOVERNED_BELOW]
fr = E2E["rows"]
OUT["aifoundry2_split"] = {
    "definition": f"governed = a burst measured below {GOVERNED_BELOW:.0f} MHz (no burst is predicted below 795 MHz and measured above it); "
                  "pinned = measured at 795-800 MHz. Frozen bands: +-%.1f MHz, +-%.2f W (m7.json aifoundry2.end_to_end_band)" % (BAND_MHZ, BAND_W),
    "frozen_cap_W_star_w": A2["burst_cap"]["W_star_used_w"], "refit_here_w": W_all, "reproduces_frozen_rows_max_abs_diff": check,
    "frozen_cap": {"all": score(fr), "governed": score(gov(fr)), "pinned": score(pin(fr))},
    "cap_refitted_leaving_each_kind_out": {"all": score(loko_cap), "governed": score(gov(loko_cap)), "pinned": score(pin(loko_cap)),
                                           "cap_range_w": [min(caps.values()), max(caps.values())], "n_kinds": len(caps)},
    "governed_rows": sorted([{"cell": r["cell"], "mhz_meas": r["mhz_meas"], "mhz_pred": r["mhz_pred"], "mhz_err": round(r["mhz_meas"] - r["mhz_pred"], 1),
                              "w_meas": r["w_meas"], "w_pred": r["w_pred"], "w_err": round(r["w_meas"] - r["w_pred"], 2)} for r in gov(fr)], key=lambda r: r["mhz_meas"]),
    "predicted_800_but_governed": [r["cell"] for r in gov(fr) if r["mhz_pred"] >= GOVERNED_BELOW],
}


def kind_of(cell):
    return cell.split(":", 1)[1]


RANDOM_LIKE = {"fp32 randn": lambda k: k.startswith("fp32.randn"), "fp32 uniform01": lambda k: k == "fp32.uniform01",
               "fp16 randn": lambda k: k.startswith("fp16.randn"), "fp16 uniform01": lambda k: k == "fp16.uniform01",
               "int8 full (uniform over the range)": lambda k: k == "int8.full", "int8 gauss_q": lambda k: k == "int8.gauss_q"}
rl = {}
for lab, f in RANDOM_LIKE.items():
    rr = [r for r in fr if f(kind_of(r["cell"]))]
    rl[lab] = {"cells": [r["cell"] for r in rr], "mhz_meas_range": [min(r["mhz_meas"] for r in rr), max(r["mhz_meas"] for r in rr)],
               "mhz_pred_range": [min(r["mhz_pred"] for r in rr), max(r["mhz_pred"] for r in rr)],
               "board_err_w_range": [round(min(r["w_meas"] - r["w_pred"] for r in rr), 2), round(max(r["w_meas"] - r["w_pred"] for r in rr), 2)]}
OUT["aifoundry2_random_like"] = rl

# ------------------------------------------------------------------ 3: glive against clk
fl = [r for r in ROWS if r["type"] != "int8"]
i8 = [r for r in ROWS if r["type"] == "int8"]
xc = np.array([r["rate"] * r["f"]["clk"] for r in fl])
xg = np.array([r["rate"] * r["f"]["glive"] for r in fl])
r2_centered = float(np.corrcoef(xc, xg)[0, 1] ** 2)
bo = float(xc @ xg / (xc @ xc))
r2_origin = float(1 - np.sum((xg - bo * xc) ** 2) / np.sum(xg ** 2))
G8 = M7.FORMS["float"]["G8_gtr_glive"]
Xo = np.array([[r["rate"] * r["f"][q] for q in G8 if q != "glive"] for r in fl])
bb = np.linalg.lstsq(Xo, xg, rcond=None)[0]
r2_multi_origin = float(1 - np.sum((xg - Xo @ bb) ** 2) / np.sum(xg ** 2))
Xc = np.column_stack([Xo, np.ones(len(fl))])
bc = np.linalg.lstsq(Xc, xg, rcond=None)[0]
r2_multi_centered = float(1 - np.sum((xg - Xc @ bc) ** 2) / np.sum((xg - xg.mean()) ** 2))
# rows with glive = 0 and clk = 0 (fully gated) agree with proportionality and cannot separate the two; a row with glive = 0 and
# clk > 0 would (none exists)
both0 = [r for r in fl if r["f"]["glive"] <= 0 and r["f"]["clk"] == 0]
gl0_clk = [r for r in fl if r["f"]["glive"] <= 0 and r["f"]["clk"] != 0]
ratio = np.array([r["f"]["clk"] / r["f"]["glive"] if r["f"]["glive"] > 0 else np.nan for r in fl])
med = float(np.nanmedian(ratio))
dep = [r for r, q in zip(fl, ratio) if (np.isfinite(q) and abs(q / med - 1) > 0.10)] + gl0_clk
ri8 = np.array([r["f"]["clk"] / r["f"]["glive"] for r in i8 if r["f"]["glive"] > 0])
fam = M7.Fam(fl, M7.FORMS["float"], "C0_M5_E78E82_family")
prices = {}
for fn in ("G0_M5", "G1_gtr", "G8_gtr_glive", "G6_M6"):
    b, s = fam.fit_all(fn, [])
    cj = fam.coef_J(fn, b)
    prices[fn] = {q: float(v) * 1e15 for q, v in zip(M7.FORMS["float"][fn], cj) if q in ("clk", "gtr", "glive")}
m6f = m6["families"]["float"]
prices["M6_frozen"] = {q: float(v) for q, v in zip(m6f["terms"], m6f["coef_fJ"]) if q in ("clk", "gtr")}
chk = max(abs(prices["G8_gtr_glive"][q] - v) / abs(v) for q, v in zip(m7["families"]["float"]["terms"], m7["families"]["float"]["coef_fJ"]) if q in prices["G8_gtr_glive"])
OUT["glive_vs_clk"] = {
    "float_rows": len(fl), "r2_glive_on_clk_centered": r2_centered, "r2_glive_on_clk_through_origin": r2_origin,
    "r2_glive_on_the_other_G8_terms_through_origin": r2_multi_origin, "r2_glive_on_the_other_G8_terms_with_intercept": r2_multi_centered,
    "clk_over_glive_median_float": med, "rows_glive_and_clk_both_zero": len(both0), "kinds_glive_and_clk_both_zero": len({r["kind"] for r in both0}),
    "rows_glive_zero_clk_nonzero": len(gl0_clk),
    "rows_departing_over_10pct": len(dep), "kinds_departing_over_10pct": len({r["kind"] for r in dep}),
    "departing_by_experiment": {e: sum(1 for r in dep if r["exp"] == e) for e in sorted({r["exp"] for r in dep})},
    "int8_clk_over_glive": {"min": float(ri8.min()), "max": float(ri8.max()), "n": int(len(ri8))},
    "int8_J9_glive_vs_J0_M5_plain_loko_w": [L["families"]["int8"]["plain_loko_by_form"]["J9_glive"]["all"], L["families"]["int8"]["plain_loko_by_form"]["J0_M5"]["all"]],
    "prices_fJ_fitted_on_all_rows": prices, "G8_matches_m7json_max_rel": chk,
}

# ------------------------------------------------------------------ 4: where the gains sit
gains = {}
for famn, others in (("float", ("M6_form_loko_err_w", "M5_form_loko_err_w")), ("int8", ("M5_form_loko_err_w", "M6_form_loko_err_w"))):
    re_ = L["families"][famn]["row_errors"]
    pool = [r for r in re_ if r["exp"] in ("E115", "E140")]
    rest = [r for r in re_ if r["exp"] not in ("E115", "E140")]
    gains[famn] = {f"M7_nested_minus_{o[:-6]}": {"pool_rows_E115_E140": boot_diff(pool, "M7_nested_err_w", o), "other_rows": boot_diff(rest, "M7_nested_err_w", o),
                                                 "all_rows": boot_diff(re_, "M7_nested_err_w", o)} for o in others}
    e140 = [r for r in re_ if r["exp"] == "E140"]
    gains[famn]["E140_rows_blind_and_out_of_kind_w"] = {c: rms([r[c] for r in e140]) for c in ("M5_frozen_err_w", "M6_frozen_err_w", "M7_nested_err_w")}
OUT["gains_split"] = gains

# ------------------------------------------------------------------ 5: the band's k
band = {}
for famn in ("float", "int8"):
    v = L["families"][famn]
    pools = v["band_calibration"]["pools"]
    re_ = v["row_errors"]
    z = lambda r: abs(r["M7_nested_err_w"]) / pools[f"{r['type']}|{r['card']}"]["rms_w"]
    zall = [z(r) for r in re_ if not math.isnan(r["M7_nested_err_w"])]
    zp_rows = [r for r in re_ if r["exp"] in ("E115", "E140")]
    zp = sorted([z(r) for r in zp_rows], reverse=True)
    k = max(float(np.quantile(zall, 0.95)), float(np.quantile(zp, 0.95)))
    n = len(zp)
    pos = 0.95 * (n - 1)
    lo_i = int(math.floor(pos))
    asc = sorted(zp)
    loo_in = 0
    for i, r in enumerate(zp_rows):
        zi = z(r)
        za = [z(q) for j, q in enumerate(re_) if q is not r and not math.isnan(q["M7_nested_err_w"])]
        zpo = [z(q) for q in zp_rows if q is not r]
        loo_in += int(zi <= max(float(np.quantile(za, 0.95)), float(np.quantile(zpo, 0.95))))
    band[famn] = {"n_pool_rows": n, "pool_z_top5": zp[:5], "k_recomputed": k, "k_frozen": m7["families"][famn]["band_k"],
                  "quantile_position_ascending_0based": pos, "between_ascending": [asc[lo_i], asc[lo_i + 1]],
                  "between_rank_from_top": [n - lo_i, n - lo_i - 1], "pool_rows_outside_k": int(sum(q > k for q in zp)),
                  "leave_one_pool_row_out_inside": [loo_in, n]}
OUT["band_k"] = band

# ------------------------------------------------------------------ 6: heat at the measured run length
H = m7["heat"]
heat = {}
for card in sorted({r["card"] for r in HR}):
    rr = [r for r in HR if r["card"] == card]
    T = [r["T_run"] for r in rr]
    gst = H["coef"][f"ST|{card}"]
    tm = statistics.median(T)
    per_w = gst * (tm - 4.5)
    o = {"n": len(rr), "T_run_median_s": tm, "T_run_min_s": min(T), "T_run_max_s": max(T), "T_run_range_s": max(T) - min(T),
         "ST_coef_c_per_w_per_s": gst, "H2_offset_at_median_T_c_per_board_w": per_w, "by_type": {}}
    for t in ("fp32", "fp16", "int8"):
        st = [r["S"] for r in rr if r["type"] == t]
        if not st:
            continue
        hw = H["band_k"] * H["interval_pool_by_format_card_c"][f"{t}|{card}"]["rms_c"]
        o["by_type"][t] = {"n": len(st), "S_median_w": statistics.median(st), "S_max_w": max(st), "offset_at_median_S_c": per_w * statistics.median(st),
                           "offset_at_max_S_c": per_w * max(st), "band_half_width_c": hw, "offset_at_median_S_over_band": per_w * statistics.median(st) / hw}
    heat[card] = o
OUT["heat_run_length"] = heat

# ------------------------------------------------------------------ 7: zeros_S with E137 and E140
expd = dict(M7.M6.EXPDIR)
expd2 = dict(expd, E137="2026-11-02-e137-fp16-sign-rest", E140="2026-11-02-e140-blind4")


def zeros_S(prefix, ed):
    out = {}
    for t in ("fp32", "fp16", "int8"):
        v = []
        for e, d in ed.items():
            j = load(os.path.join(DD, d, f"{e.lower()}.json"))
            zz = j["items"].get(f"{t}.zeros")
            if j.get("card", "").startswith(prefix) and zz and isinstance(zz.get("S"), dict) and zz["S"].get("mean") is not None:
                v.append(float(zz["S"]["mean"]))
        out[t] = {"mean": statistics.mean(v), "n": len(v)}
    return out


zs = {}
for cc, pref in (("a3", "aifoundry3"), ("c1", "aifoundry1")):
    a, b = zeros_S(pref, expd), zeros_S(pref, expd2)
    g = H["coef"][f"S|{PB.HEAT_CARD[cc]}"]
    zs[cc] = {t: {"frozen_list": a[t], "with_E137_E140": b[t], "delta_w": b[t]["mean"] - a[t]["mean"], "delta_dT_c": g * (b[t]["mean"] - a[t]["mean"]),
                  "matches_predict_blind5": abs(a[t]["mean"] - ZS_FROZEN[cc][t]["mean"]) < 1e-12} for t in a}
OUT["zeros_S"] = {"experiments_in_frozen_list": sorted(expd), "by_card": zs}

# ------------------------------------------------------------------ 8: provenance
mods = sorted({os.path.abspath(m.__file__) for m in list(sys.modules.values())
               if getattr(m, "__file__", None) and os.path.abspath(m.__file__).startswith(ROOT + os.sep)
               and os.path.abspath(m.__file__) != os.path.abspath(__file__)})
reads = sorted({p for p in OPENED if p.startswith(ROOT + os.sep) and os.path.isfile(p)})
OUT["provenance"] = {"modules": {os.path.relpath(p, ROOT): sha(p) for p in mods},
                     "files_read_by_imports_and_pool_independent_reads": {os.path.relpath(p, ROOT): sha(p) for p in reads}}

json.dump(OUT, _open(os.path.join(HERE, "posthoc-m7.json"), "w"), indent=1, default=float)

# ------------------------------------------------------------------ summary
s = OUT["aifoundry2_split"]
print(f"== 1. aifoundry2 end to end ({s['definition']}); my refit of the cap {W_all:.5f} W (frozen {s['frozen_cap_W_star_w']:.5f}); "
      f"rows reproduced to {check:.3g}")
for lab in ("frozen_cap", "cap_refitted_leaving_each_kind_out"):
    for sub in ("all", "governed", "pinned"):
        x = s[lab][sub]
        print(f"  {lab:36s} {sub:9s} n {x['n']:2d}  rms {x['rms_mhz']:5.2f} MHz (q95 {x['q95_abs_mhz']:5.1f}, inside {x['inside_frozen_mhz_band']}/{x['n']})  "
              f"board rms {x['rms_board_w']:4.2f} W (q95 {x['q95_abs_board_w']:4.2f}, inside {x['inside_frozen_board_band']}/{x['n']}, bias pred-meas {x['bias_board_pred_minus_meas_w']:+.2f})")
print(f"  LOKO caps {s['cap_refitted_leaving_each_kind_out']['cap_range_w'][0]:.2f}-{s['cap_refitted_leaving_each_kind_out']['cap_range_w'][1]:.2f} W over {len(caps)} kinds")
print("  governed bursts (meas, pred MHz; meas - pred W):")
for r in s["governed_rows"]:
    print(f"    {r['cell']:28s} {r['mhz_meas']:6.1f} {r['mhz_pred']:6.1f} ({r['mhz_err']:+6.1f})  {r['w_meas']:6.2f} {r['w_pred']:6.2f} ({r['w_err']:+5.2f})")
print("  predicted at 800 MHz but governed:", s["predicted_800_but_governed"])
print("== 2. random-like kinds' bursts (measured / predicted MHz; board meas - pred W)")
for lab, x in rl.items():
    print(f"  {lab:36s} meas {x['mhz_meas_range']}  pred {x['mhz_pred_range']}  board err {x['board_err_w_range']}  {x['cells']}")
g = OUT["glive_vs_clk"]
print(f"== 3. glive vs clk (floats, {g['float_rows']} rows): R^2 glive on clk {g['r2_glive_on_clk_centered']:.4f} centered, {g['r2_glive_on_clk_through_origin']:.4f} "
      f"through the origin; on the other G8 terms {g['r2_glive_on_the_other_G8_terms_with_intercept']:.4f} / {g['r2_glive_on_the_other_G8_terms_through_origin']:.4f}")
print(f"  clk/glive median {g['clk_over_glive_median_float']:.1f} (rows with glive > 0); glive = clk = 0 on {g['rows_glive_and_clk_both_zero']} rows "
      f"({g['kinds_glive_and_clk_both_zero']} kinds), glive = 0 with clk > 0 on {g['rows_glive_zero_clk_nonzero']}; "
      f"rows departing > 10%: {g['rows_departing_over_10pct']} ({g['kinds_departing_over_10pct']} kinds) {g['departing_by_experiment']}")
print(f"  int8 clk/glive {g['int8_clk_over_glive']}; J9_glive vs J0_M5 plain LOKO {g['int8_J9_glive_vs_J0_M5_plain_loko_w']}")
print("  prices fJ (all rows):", json.dumps({k: {q: round(v, 3) for q, v in p.items()} for k, p in g["prices_fJ_fitted_on_all_rows"].items()}), f"G8 vs m7.json {g['G8_matches_m7json_max_rel']:.2e}")
print("== 4. where the gains sit (rms M7 nested - rms other; 95% over kinds)")
for famn, v in gains.items():
    for k_, x in v.items():
        if k_.startswith("M7"):
            for sub, y in x.items():
                print(f"  {famn:5s} {k_:34s} {sub:20s} n {y['n_rows']:3d} ({y['n_kinds']:3d} kinds): {y['rms_a_w']:.3f} vs {y['rms_b_w']:.3f} = {y['diff_w']:+.4f} [{y['ci95_over_kinds_w'][0]:+.4f}, {y['ci95_over_kinds_w'][1]:+.4f}]")
    print(f"  {famn:5s} E140 rows: {json.dumps({c: round(x, 3) for c, x in v['E140_rows_blind_and_out_of_kind_w'].items()})}")
print("== 5. band k")
for famn, x in band.items():
    print(f"  {famn}: {json.dumps(x)}")
print("== 6. heat at the measured run length")
for card, x in heat.items():
    print(f"  {card}: T_run median {x['T_run_median_s']:.3f} s ({x['T_run_min_s']:.3f}-{x['T_run_max_s']:.3f}, range {x['T_run_range_s']:.3f}); ST {x['ST_coef_c_per_w_per_s']:+.4f}; "
          f"offset {x['H2_offset_at_median_T_c_per_board_w']:+.5f} C/W")
    for t, y in x["by_type"].items():
        print(f"    {t}: S median {y['S_median_w']:.2f} W (max {y['S_max_w']:.2f}): offset {y['offset_at_median_S_c']:+.3f} C ({y['offset_at_max_S_c']:+.3f} at max) "
              f"against a band of +-{y['band_half_width_c']:.3f} C ({100 * y['offset_at_median_S_over_band']:.0f}%)")
print("== 7. zeros_S, frozen list", OUT["zeros_S"]["experiments_in_frozen_list"])
for cc, v in zs.items():
    print(f"  {cc}: " + "; ".join(f"{t} {x['frozen_list']['mean']:.4f} (n {x['frozen_list']['n']}) -> {x['with_E137_E140']['mean']:.4f} (n {x['with_E137_E140']['n']}), "
                                  f"dT {x['delta_dT_c']:+.4f} C, predictor match {x['matches_predict_blind5']}" for t, x in v.items()))
print("== 8. provenance (sha256)")
for k_, v in OUT["provenance"].items():
    print(f"  {k_}:")
    for p, h in v.items():
        print(f"    {h}  {p}")
