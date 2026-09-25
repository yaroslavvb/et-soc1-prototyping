#!/usr/bin/env python3
"""V3-CAT reducer: the pre-registered items CAT-a, CAT-b, CAT-c, CAT-e, CAT-f of PLAN3 section 2 (V3-CAT).

    python3 tools/claims-v3/cat/reduce.py --data <dir with aifoundry2/ and aifoundry3/ laid out like DATA_ROOT>
                                          --out verdicts.json [--root <tree root>] [--committed <catalogue.json>]

Input: <data>/<card>/cat/p<N>/ as block.sh leaves it. A pass is used when its block.json status is "ok",
"offclock" (the off-clock bursts are dropped below) or "partial" (a few configurations without a launch) and it is
not a smoke pass; p<N>.attempt-*, "others" (stopped when another user appeared) and failed or unfinished blocks are
skipped (listed under "passes").
Bursts: workloads/enercat/analyze_catalogue.py bursts_of(), unchanged, one pass directory at a time (catlib.py);
value = pJ/B for byte configurations, pJ/op otherwise (the catalogue's own unit); drop rules in catlib.py
(aifoundry2 off-600 MHz bursts, R-clock implied clock; heater inside an idle bracket).
Unit = pass. Decisions use the new passes only; the committed 23 Sep catalogue is printed beside ("committed_23sep"),
never pooled. 99% two-sided intervals throughout. A card with fewer than 3 kept passes in a group an item needs
leaves the item INSUFFICIENT (R-both); with data on one card only, the item is INSUFFICIENT and that card's values are
still printed.

How each registered decision rule maps to the four outcomes (the rules themselves are PLAN3's, unchanged):
  CAT-a  per card: beta = (hot - cool)/dT (%/C); cool = W on aifoundry2, C on aifoundry3; hot - cool is the Welch
         99% interval on the pass values s_p = 100 x median over the panel of ln(value / config mean), config mean
         over the card's arm-A passes; dT = difference of the pass-mean busy die temperatures (taken as fixed).
         Interval excludes 0.21 -> "card"; else excludes 0 (and includes 0.21) -> "temperature"; else "not
         established". The item's claims hold on a card when the decision is "card". Both -> PASS, one -> CARD-
         DIFFERENT, none -> FAIL.
  CAT-b  cross-card: pass values m_p = 100 x median over the panel of ln(value / aifoundry2-W config mean); Welch
         99% of aifoundry3-C minus aifoundry2-W, as a ratio exp(). PASS when the interval excludes 1 and the ratio is
         inside 0.951 +- 0.015 (the plan's verification convention: interval excludes the null AND the estimate lies
         in the predicted range), else FAIL.
  CAT-c  per card and operand set: one-way ANOVA over dramrow2 seq / rowhit / rowmiss p > 0.01 AND the Welch 99%
         interval of rows (per pass, the mean of the three patterns) minus tload/dram excludes 0. Holds on a card
         when both operand sets pass. Both -> PASS (PROVEN-BOTH), one -> CARD-DIFFERENT, none -> FAIL. The
         prediction's bands (patterns within 15 pJ/B of each other; rows 13-26% above tload/dram) are reported as
         band_ok, not used for the outcome (the registered decision does not name them).
  CAT-e  Welch 99% of tstore/dram/random minus tload/dram/random per card. The band (+3.2 +- 3 pJ/B) is registered
         for aifoundry3 only: PASS when aifoundry3's interval excludes 0 and its estimate is in [0.2, 6.2]; else
         FAIL. aifoundry2's interval is reported beside (no band registered for it).
  CAT-f  per card: fill per byte = 2 x (l1fill/stride64 - l1fill/stride32, random, pJ per load, same pass) / 64;
         Welch 99% of fill per byte minus tload/scp/random (null: ratio 1); holds when the interval excludes 0 and
         the ratio mean(fill)/mean(tload) is inside 0.75 +- 0.10. Both -> PASS, one -> CARD-DIFFERENT, none -> FAIL.
         Reported beside, as registered "expected within noise": fence vs nop (energy-manual-44) per card; the
         stride-256 row (energy-manual-102) was dropped from arm B and is not measured.
"""
import argparse
import datetime
import json
import math
import os
import re
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import catlib as L  # noqa: E402

A2, A3 = L.A2, L.A3
CARDS = (A2, A3)
MIN_N = 3
USABLE = ("ok", "offclock", "partial")
PANEL = ["fadd.s/zeros/h2", "fadd.s/random/h2", "fmul.s/zeros/h2", "fmul.s/random/h2", "fmadd.s/random/h2",
         "fcvt.s.w/random/h2", "fadd.ps/random/h2", "fsub.ps/random/h2", "fmul.ps/random/h2", "fsgnj.ps/random/h2",
         "feq.ps/random/h2", "fadd.pi/random/h2", "fmul.pi/random/h2", "fxor.pi/random/h2", "fmadd.ps/zeros/h2",
         "fmadd.ps/random/h2", "fnmadd.ps/random/h2", "fexp.ps/random/h2", "flog.ps/random/h2", "frcp.ps/random/h2",
         "fround.ps/random/h2", "fsw.ps/random/h2", "tstore/dram/random", "tstore/scp/random", "tload/dram/random",
         "tload/scp/random", "st_stream/dram/random", "wire/hop2/random", "wire/hop4/random", "wire/hop6/random"]
BETA_T = 0.21              # %/C, the temperature alternative
CAT_A_BAND = 0.5           # %, card hypothesis hot - cool
CAT_B = (0.951, 0.015)
CAT_C_SPREAD, CAT_C_EXCESS = 15.0, (0.13, 0.26)
CAT_E = (3.2, 3.0)
CAT_F = (0.75, 0.10)
COOL = {A2: "W", A3: "C"}
CLAIMS = {
    "CAT-a": ["energy-manual-05", "energy-manual-09", "energy-manual-46", "energy-manual-154", "energy-manual-157", "hub-122"],
    "CAT-b": ["energy-manual-05"],
    "CAT-c": ["energy-manual-103", "energy-manual-104", "energy-manual-105", "energy-manual-108"],
    "CAT-e": ["energy-manual-75"],
    "CAT-f": ["energy-manual-100", "energy-manual-102"],
}
R = L.rnd


def excl(w, x):
    return w is not None and not (w["lo"] <= x <= w["hi"])


def mean(v):
    return float(np.mean(v)) if len(v) else None


# ---------------------------------------------------------------- loading
def load_card(data, card, root):
    base = os.path.join(data, card, "cat")
    used, listing = [], []
    if not os.path.isdir(base):
        return used, listing
    for name in sorted(os.listdir(base), key=lambda s: (len(s), s)):
        d = os.path.join(base, name)
        if not re.fullmatch(r"p\d+", name):
            if name.startswith("p"):
                listing.append({"dir": name, "used": False, "why": "not a pass directory (earlier attempt)"})
            continue
        bj, pj = L.load_block_json(os.path.join(d, "block.json")), L.jload(os.path.join(d, "pass.json"))
        if not bj or not pj:
            listing.append({"dir": name, "used": False, "why": "no block.json / pass.json (unfinished block)"})
            continue
        if pj.get("smoke"):
            listing.append({"dir": name, "used": False, "why": "smoke"})
            continue
        if bj.get("status") not in USABLE:
            listing.append({"dir": name, "used": False, "why": f"status {bj.get('status')}: {bj.get('note', '')}"})
            continue
        kept, dropped, expected, info = L.pass_bursts(d, card, root)
        p = {"pass": pj["pass"], "arm": pj["arm"], "cond": pj["cond"], "k": pj["k"], "seed": pj["seed"],
             "hold_c": pj.get("hold_c"), "status": bj["status"], "bursts": {b["cfg"]: b for b in kept}}
        used.append(p)
        listing.append({"dir": name, "used": True, "pass": pj["pass"], "arm": pj["arm"], "cond": pj["cond"], "k": pj["k"],
                        "status": bj["status"], "expected": len(expected), "kept": len(kept), "dropped": dropped,
                        "die_c_busy_mean": R(mean([b["die_c_busy"] for b in kept])) if kept else None,
                        "die_c_start": bj.get("die_c_start"),
                        "sampler_median_ms": R(float(np.median([b["sampler_median_ms"] for b in kept]))) if kept else None,
                        "heater_launches": info.get("heater_launches", 0)})
    return used, listing


def committed_passes(path):
    """The 23 Sep catalogue (catalogue.json bursts) as pseudo-passes per card, for printing beside only."""
    c = L.jload(path) if path else None
    if not c:
        return None
    out = {}
    for card, bs in c.get("bursts", {}).items():
        by = {}
        for b in bs:
            v = L.value(b)
            if v is None:
                continue
            bb = dict(b, value=v)
            by.setdefault(b["pass"], {})[b["cfg"]] = bb
        out[card] = [{"pass": k, "arm": "committed", "cond": "23sep", "bursts": v} for k, v in sorted(by.items())]
    return out


def vals(P, cfg):
    return [p["bursts"][cfg]["value"] for p in P if cfg in p["bursts"]]


# ---------------------------------------------------------------- CAT-a
def pass_scale(p, ref):
    x = [math.log(p["bursts"][c]["value"] / ref[c]) for c in PANEL
         if c in p["bursts"] and ref.get(c) and ref[c] > 0 and p["bursts"][c]["value"] > 0]
    return (100 * float(np.median(x)) if x else None), len(x)


def pass_temp(p):
    t = [p["bursts"][c]["die_c_busy"] for c in PANEL if c in p["bursts"]]
    return mean(t)


def cat_a_card(card, P):
    A = [p for p in P if p["arm"] == "A"]
    ref = {c: mean(vals(A, c)) for c in PANEL if vals(A, c)}
    rows = {}
    for p in A:
        s, n = pass_scale(p, ref)
        if s is not None:
            rows.setdefault(p["cond"], []).append({"pass": p["pass"], "s_pct": s, "n_cfg": n, "die_c": pass_temp(p)})
    hot, cool = rows.get("H", []), rows.get(COOL[card], [])
    res = {"cool_cond": COOL[card], "n_hot": len(hot), "n_cool": len(cool),
           "hot": R(hot), "cool": R(cool)}
    if len(hot) < MIN_N or len(cool) < MIN_N:
        res["decision"] = "INSUFFICIENT"
        res["why"] = f"needs >= {MIN_N} kept passes per condition (design: a2 4 v 4, a3 3 v 3)"
        return res
    w = L.welch([h["s_pct"] for h in hot], [c["s_pct"] for c in cool])
    dT = mean([h["die_c"] for h in hot]) - mean([c["die_c"] for c in cool])
    res.update({"hot_minus_cool_pct": R(w), "dT_c": R(dT), "card_band_ok": abs(w["diff"]) <= CAT_A_BAND,
                "temperature_alternative_pct": R(BETA_T * dT)})
    if dT <= 0:
        res.update({"decision": "not established", "why": "hot passes not warmer than cool passes (dT <= 0)"})
        return res
    b = {"beta": w["diff"] / dT, "lo": w["lo"] / dT, "hi": w["hi"] / dT}
    res["beta_pct_per_c"] = R(b)
    if not (b["lo"] <= BETA_T <= b["hi"]):
        res["decision"] = "card"
        res["note"] = "interval below 0.21 %/C" if b["hi"] < BETA_T else "interval ABOVE 0.21 %/C (registered rule still reads 'card')"
    elif not (b["lo"] <= 0 <= b["hi"]):
        res["decision"] = "temperature"
    else:
        res["decision"] = "not established"
    return res


def outcome_per_card(per, holds):
    if any(per.get(c, {}).get("decision", "INSUFFICIENT") == "INSUFFICIENT" for c in CARDS):
        return "INSUFFICIENT"
    h = [holds(per[c]) for c in CARDS]
    return "PASS" if all(h) else ("CARD-DIFFERENT" if any(h) else "FAIL")


def cat_a(P):
    per = {c: cat_a_card(c, P.get(c, [])) for c in CARDS}
    out = outcome_per_card(per, lambda r: r["decision"] == "card")

    def one(c):
        r = per[c]
        if r["decision"] == "INSUFFICIENT":
            return f"{c[-1]}: insufficient ({r['n_hot']} hot v {r['n_cool']} {r['cool_cond']})"
        if "beta_pct_per_c" not in r:
            return f"{c[-1]}: {r['decision']} ({r.get('why', '')})"
        b = r["beta_pct_per_c"]
        return f"{c[-1]}: beta {b['beta']:+.3f} %/C [{b['lo']:+.3f}, {b['hi']:+.3f}] over dT {r['dT_c']:.1f} C -> {r['decision']}"
    return {"item": "CAT-a", "claims": CLAIMS["CAT-a"], "per_card": per,
            "test": "beta = (hot - cool)/dT per card, Welch 99% on pass values (a2 4 v 4, a3 3 v 3): excludes 0.21 %/C -> "
                    "'the scale is the card'; excludes 0 and includes 0.21 -> temperature explains it; else not established. "
                    "Prediction (card hypothesis): hot - cool = 0 +- 0.5%.",
            "outcome": out, "reading": "; ".join(one(c) for c in CARDS)}


# ---------------------------------------------------------------- CAT-b
def cat_b(P, committed):
    W2 = [p for p in P.get(A2, []) if p["arm"] == "A" and p["cond"] == "W"]
    C3 = [p for p in P.get(A3, []) if p["arm"] == "A" and p["cond"] == "C"]

    def run(g2, g3):
        ref = {c: mean(vals(g2, c)) for c in PANEL if vals(g2, c)}
        m2 = [x for x in (pass_scale(p, ref)[0] for p in g2) if x is not None]
        m3 = [x for x in (pass_scale(p, ref)[0] for p in g3) if x is not None]
        r = {A2: {"cond": "W", "m_pct": R(m2), "n": len(m2)}, A3: {"cond": "C", "m_pct": R(m3), "n": len(m3)}}
        ratios = [mean(vals(g3, c)) / ref[c] for c in PANEL if c in ref and vals(g3, c)]
        r["config_ratio_median"] = R(float(np.median(ratios))) if ratios else None
        w = L.welch(m3, m2)
        if w:
            r["ratio"] = R({"ratio": math.exp(w["diff"] / 100), "lo": math.exp(w["lo"] / 100), "hi": math.exp(w["hi"] / 100),
                            "p": w["p"], "df": w["df"]})
        return r, w, len(m2), len(m3)
    per, w, n2, n3 = run(W2, C3)
    lo, hi = CAT_B[0] - CAT_B[1], CAT_B[0] + CAT_B[1]
    if n2 < MIN_N or n3 < MIN_N:
        out = "INSUFFICIENT"
        reading = f"needs >= {MIN_N} aifoundry2-W and aifoundry3-C passes (have {n2}, {n3})"
    else:
        rt = math.exp(w["diff"] / 100)
        ok = excl(w, 0.0) and lo <= rt <= hi
        out = "PASS" if ok else "FAIL"
        reading = (f"cool a3 / warm a2 = {rt:.3f} [{math.exp(w['lo'] / 100):.3f}, {math.exp(w['hi'] / 100):.3f}] "
                   f"(predicted {CAT_B[0]} +- {CAT_B[1]}); " + ("interval excludes 1" if excl(w, 0.0) else "interval includes 1")
                   + ("; estimate outside the predicted range (sign only: the page takes the measured value)"
                      if excl(w, 0.0) and not ok else ""))
    res = {"item": "CAT-b", "claims": CLAIMS["CAT-b"], "per_card": per,
           "test": "Welch 99% on pass-level medians (panel, ln(value / aifoundry2-W config mean)); PASS when the interval "
                   "excludes 1 and the ratio is in 0.951 +- 0.015.", "outcome": out, "reading": reading}
    if committed and A2 in committed and A3 in committed:
        cr, _, _, _ = run(committed[A2], committed[A3])
        res["committed_23sep"] = {"ratio": cr.get("ratio"), "config_ratio_median": cr.get("config_ratio_median"),
                                  "note": "23 Sep, 3 v 3 passes at the cards' own temperatures; printed beside, not pooled"}
    return res


# ---------------------------------------------------------------- CAT-c
def rows_card(P):
    B = [p for p in P if p["arm"] in ("B", "committed")]
    res, holds, insufficient = {}, True, False
    for o in ("zeros", "random"):
        g = {pat: vals(B, f"dramrow2/{pat}/{o}") for pat in ("seq", "rowhit", "rowmiss")}
        rows = [np.mean([p["bursts"][f"dramrow2/{pat}/{o}"]["value"] for pat in g]) for p in B
                if all(f"dramrow2/{pat}/{o}" in p["bursts"] for pat in g)]
        tl = vals(B, f"tload/dram/{o}")
        r = {"n": {k: len(v) for k, v in g.items()}, "means": R({k: mean(v) for k, v in g.items()}),
             "rows_n": len(rows), "tload_n": len(tl), "tload_mean": R(mean(tl))}
        if min(len(v) for v in g.values()) < MIN_N or len(rows) < MIN_N or len(tl) < MIN_N:
            r["decision"] = "INSUFFICIENT"
            insufficient = True
        else:
            a = L.anova1(list(g.values()))
            w = L.welch(rows, tl)
            spread = max(mean(v) for v in g.values()) - min(mean(v) for v in g.values())
            ex = mean(rows) / mean(tl) - 1
            ok = a["p"] > 0.01 and excl(w, 0.0)
            r.update({"anova": R(a), "rows_minus_tload": R(w), "rows_mean": R(mean(rows)), "spread_pj_b": R(spread),
                      "excess_over_tload": R(ex),
                      "band_ok": {"spread_le_15": spread <= CAT_C_SPREAD, "excess_13_26pct": CAT_C_EXCESS[0] <= ex <= CAT_C_EXCESS[1]},
                      "decision": "holds" if ok else "fails"})
            holds = holds and ok
        res[o] = r
    res["decision"] = "INSUFFICIENT" if insufficient else ("holds" if holds else "fails")
    return res


def cat_c(P, committed):
    per = {c: rows_card(P.get(c, [])) for c in CARDS}
    out = outcome_per_card(per, lambda r: r["decision"] == "holds")

    def one(c):
        r = per[c]
        if r["decision"] == "INSUFFICIENT":
            return f"{c[-1]}: insufficient"
        return f"{c[-1]}: " + ", ".join(
            f"{o} ANOVA p {r[o]['anova']['p']:.3g}, rows - tload {r[o]['rows_minus_tload']['diff']:+.1f} "
            f"[{r[o]['rows_minus_tload']['lo']:+.1f}, {r[o]['rows_minus_tload']['hi']:+.1f}] pJ/B ({100 * r[o]['excess_over_tload']:+.0f}%)"
            for o in ("zeros", "random")) + f" -> {r['decision']}" + (band(r) if c == A3 else "")

    def band(r):
        bad = [f"{o} {k}" for o in ("zeros", "random") for k, v in r[o]["band_ok"].items() if not v]
        return " (a3 prediction bands: " + ("met" if not bad else "missed " + ", ".join(bad) + "; the page takes the measured value") + ")"
    res = {"item": "CAT-c", "claims": CLAIMS["CAT-c"], "per_card": per,
           "test": "per card and operand set: one-way ANOVA p > 0.01 over seq/rowhit/rowmiss AND Welch 99% of rows - "
                   "tload/dram excludes 0 -> PROVEN-BOTH. Prediction bands (within 15 pJ/B; 13-26% above tload/dram) "
                   "reported as band_ok.", "outcome": out, "reading": "; ".join(one(c) for c in CARDS)}
    if committed and A2 in committed:
        res["committed_23sep"] = {A2: rows_card(committed[A2]), "note": "aifoundry2 23 Sep main + rows sessions; printed beside"}
    return res


# ---------------------------------------------------------------- CAT-e
def store_load(P):
    B = [p for p in P if p["arm"] in ("B", "committed")]
    ts, tl = vals(B, "tstore/dram/random"), vals(B, "tload/dram/random")
    r = {"tstore_n": len(ts), "tload_n": len(tl), "tstore_mean": R(mean(ts)), "tload_mean": R(mean(tl))}
    if len(ts) < MIN_N or len(tl) < MIN_N:
        r["decision"] = "INSUFFICIENT"
        return r, None
    w = L.welch(ts, tl)
    r.update({"tstore_minus_tload": R(w), "pct": R(100 * (mean(ts) / mean(tl) - 1))})
    return r, w


def cat_e(P, committed):
    per = {}
    ws = {}
    for c in CARDS:
        per[c], ws[c] = store_load(P.get(c, []))
    lo, hi = CAT_E[0] - CAT_E[1], CAT_E[0] + CAT_E[1]
    w3 = ws[A3]
    if w3 is None:
        out, reading = "INSUFFICIENT", f"needs >= {MIN_N} aifoundry3 arm-B passes"
    else:
        ok = excl(w3, 0.0) and lo <= w3["diff"] <= hi
        per[A3]["decision"] = "holds" if ok else "fails"
        out = "PASS" if ok else "FAIL"
        reading = (f"a3 (the card the band is registered for): {w3['diff']:+.2f} [{w3['lo']:+.2f}, {w3['hi']:+.2f}] pJ/B "
                   f"(predicted +3.2 +- 3)" + ("; interval includes 0" if not excl(w3, 0.0) else
                                               "" if ok else "; excludes 0 but outside the band (sign only)"))
    if ws[A2] is not None:
        per[A2]["decision"] = "reported (no band registered for aifoundry2)"
        reading += f"; a2: {ws[A2]['diff']:+.2f} [{ws[A2]['lo']:+.2f}, {ws[A2]['hi']:+.2f}] pJ/B ({per[A2]['pct']:+.1f}%)"
    res = {"item": "CAT-e", "claims": CLAIMS["CAT-e"], "per_card": per,
           "test": "Welch 99% of tstore/dram/random - tload/dram/random per card; the band +3.2 +- 3 pJ/B is registered for "
                   "aifoundry3: PASS when its interval excludes 0 and the estimate is in the band (PASS = holds on "
                   "aifoundry3, the only card with a registered band; aifoundry2 is reported beside).",
           "outcome": out, "reading": reading}
    if committed:
        res["committed_23sep"] = {c: store_load(committed[c])[0] for c in CARDS if c in committed}
    return res


# ---------------------------------------------------------------- CAT-f
def fill_card(P, o="random"):
    B = [p for p in P if p["arm"] in ("B", "committed")]
    # l1fill's unit is one 32 B flw.ps load: its pJ per load (pj_per_op), not the catalogue's pJ/B, enters the fill
    f = [2 * (p["bursts"][f"l1fill/stride64/{o}"]["pj_per_op"] - p["bursts"][f"l1fill/stride32/{o}"]["pj_per_op"]) / 64 for p in B
         if f"l1fill/stride64/{o}" in p["bursts"] and f"l1fill/stride32/{o}" in p["bursts"]]
    tl = vals(B, f"tload/scp/{o}")
    r = {"fill_pj_per_byte": R(f), "tload_scp_pj_per_byte": R(tl), "n": [len(f), len(tl)]}
    if len(f) < MIN_N or len(tl) < MIN_N:
        r["decision"] = "INSUFFICIENT"
        return r
    w = L.welch(f, tl)
    rt = mean(f) / mean(tl)
    ok = excl(w, 0.0) and CAT_F[0] - CAT_F[1] <= rt <= CAT_F[0] + CAT_F[1]
    r.update({"fill_minus_tload": R(w), "ratio": R(rt), "ratio_ci99_approx": R([1 + w["lo"] / mean(tl), 1 + w["hi"] / mean(tl)]),
              "decision": "holds" if ok else "fails"})
    return r


def fence_nop(P):
    B = [p for p in P if p["arm"] in ("B", "committed")]
    out = {}
    for o in ("zeros", "random"):
        a, b = vals(B, f"fence/{o}/h2"), vals(B, f"nop/{o}/h2")
        if len(a) >= 2 and len(b) >= 2:
            w = L.welch(a, b)
            out[o] = {"fence_minus_nop_pj": R(w), "within_noise": not excl(w, 0.0), "n": [len(a), len(b)]}
        else:
            out[o] = {"n": [len(a), len(b)]}
    return out


def cat_f(P, committed):
    per = {}
    for c in CARDS:
        per[c] = fill_card(P.get(c, []))
        per[c]["zeros_descriptive"] = fill_card(P.get(c, []), "zeros")
        per[c]["fence_vs_nop_expected_within_noise"] = fence_nop(P.get(c, []))
    out = outcome_per_card(per, lambda r: r["decision"] == "holds")

    def one(c):
        r = per[c]
        if r["decision"] == "INSUFFICIENT":
            return f"{c[-1]}: insufficient"
        lo, hi = r["ratio_ci99_approx"]
        why = ("" if r["decision"] == "holds" else " (interval includes 1)" if not excl(r["fill_minus_tload"], 0.0)
               else " (excludes 1, ratio outside 0.65-0.85: sign only)")
        return f"{c[-1]}: fill/tload {r['ratio']:.2f} [~{lo:.2f}, {hi:.2f}] -> {r['decision']}{why}"
    res = {"item": "CAT-f", "claims": CLAIMS["CAT-f"], "per_card": per,
           "test": "per card: Welch 99% of L1 fill per byte (2 x (stride64 - stride32) / 64, random) - tload/scp/random; holds "
                   "when the interval excludes 0 (ratio 1) and the ratio is in 0.75 +- 0.10. Registered as underpowered and "
                   "expected within noise: fence vs nop (reported); stride-256 (not run: dropped from arm B).",
           "outcome": out, "reading": "; ".join(one(c) for c in CARDS) + "; stride-256 not measured (energy-manual-102 stays as it is)"}
    if committed:
        res["committed_23sep"] = {c: fill_card(committed[c]) for c in CARDS if c in committed}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--committed", default=None, help="23 Sep catalogue.json (default: the tree's; 'none' to skip)")
    a = ap.parse_args()
    cpath = a.committed or os.path.join(a.root, "docs", "reports", "data", "2026-09-23-energy-manual", "catalogue.json")
    committed = None if cpath == "none" else committed_passes(cpath)
    P, listing = {}, {}
    for c in CARDS:
        P[c], listing[c] = load_card(a.data, c, a.root)
    items = [cat_a(P), cat_b(P, committed), cat_c(P, committed), cat_e(P, committed), cat_f(P, committed)]
    res = {"exp": "V3-CAT", "plan": "PLAN3 section 2 V3-CAT (CAT-a, b, c, e, f)", "data": os.path.abspath(a.data),
           "generated": datetime.datetime.now().isoformat(timespec="seconds"),
           "rules": {"unit": "pass", "min_kept_passes": MIN_N, "conf": 0.99,
                     "drops": "aifoundry2: bursts with mhz_busy_all_600 false or a launch's implied clock outside "
                              "0.595-0.605 GHz; any card: heater launch inside a burst's idle brackets"},
           "passes": listing, "items": R(items)}
    json.dump(res, open(a.out, "w"), indent=1)
    for it in res["items"]:
        print(f"{it['item']:6s} {it['outcome']:14s} {it['reading']}")


if __name__ == "__main__":
    main()
