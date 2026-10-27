#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""V3-HL reduction, as pre-registered in README.md ("Pre-registered analysis", amendment A1).

    python3 tools/claims-v3/hl/reduce_hl.py <pass dir> [<pass dir> ...] --gen <make_hl.py dir> --pred predictions.json
        --out hl.json [--csv runs.csv] [--leak auto|<W per C>]

Per run (one process of one item at one position of one pass): t0 = the start of its first launch record (the
calibration launch for fma); P = mean board_w over [t0+1 s, t0+3 s), corrected to the launch reading with the card's
leakage slope k (P80 = P - k (T_window - T_launch), as analyze_horace_strict.py's p80); raw [1,3) and [1,4) kept;
the minion rail over [t0+2, t0+4); the clock and voltage seen in the window; the work done inside the window (launch
records overlapping it, prorated), as a rate. Gates (every failure counted and reported): one clock, the card's own;
voltage within 3 mV of the pass median; an on-protocol launch within 0.5 C of the target; fma cycles per op within
0.5% of the family's zero rung in the pass. A pass is set aside when more than one of its runs fails a gate or its
anchor_pi drifts more than 0.3 W from first to last.
Per pass, every item minus its zero (lq_h0 for lq, ls and bit; lb_h0 for lb; ord_gray_<pos> for ord; xin_h0 for
xin, xio and xnz; ain_h0 for ain); slopes per pass over h >= 1 with a free intercept (fma) or over all rungs (ec), then
the mean over passes with the SE from their scatter (the unit of replication is the pass).
"""
import argparse
import csv
import gzip
import json
import math
import os
from collections import defaultdict

import numpy as np

E_CHARGE = 1.602176634e-19
ZERO = {"lq": "lq_h0", "lb": "lb_h0", "ls": "lq_h0", "bit": "lq_h0", "xin": "xin_h0", "xio": "xin_h0", "xnz": "xin_h0",
        "ain": "ain_h0", "bpi": "lb_h0",   # bpi (E65, A4): the single-bit flip with A = pi, against lb_h0
        "alq": "aq_h0"}                    # alq (E70, A19): the A-side multi-bit ladder, against the constant-A zero
IX_BITS = [0, 8, 16, 22]                   # E67 (Q128, A12): the interaction grid's positions


def item_zero(man, item, fam):
    """The item's own zero. E67 amendment A12: make_hl.py writes a per-item `zero` for the A-side families, whose
    zero is not one per family (bit 30's base is the exponent-64 one, and nrd_a / nrd_b sit on opposite sides), and
    that field wins when it is present. Every E60 and E65 item has no such field and keeps the family map."""
    it = man.get(item, {})
    if "zero" in it:
        return it["zero"]
    return f"ord_gray_{it['pos']}" if fam == "ord" else ZERO.get(fam)


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    for line in op(path, "rt"):
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def mean_se(v):
    v = [x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return None, None, 0
    m = float(np.mean(v))
    return m, (float(np.std(v, ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None), len(v)


def fit_line(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 2 or np.ptp(x) == 0:
        return None
    X = np.vstack([np.ones_like(x), x]).T
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(c[0]), float(c[1]), float(np.sqrt(np.mean((y - X @ c) ** 2)))


def units(e_j, v):
    if e_j is None:
        return {}
    c = 2 * e_j / v ** 2
    return {"fJ": e_j * 1e15, "C_fF": c * 1e15, "electrons": c * v / E_CHARGE}


def runs_of_pass(d, man, gov_free=False, busy_mhz=800):
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    if not tel:
        return [], None
    t = np.array([s["t_ms"] for s in tel], float)
    P = np.array([s["board_w"] for s in tel])
    rail = np.array([s["sp"]["minion_w"][0] for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    mv = np.array([s["die_mv"]["minion"] for s in tel])
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
    recs = load_jsonl(os.path.join(d, "runs.jsonl"))
    marks = [m for m in load_jsonl(os.path.join(d, "marks.jsonl")) if m.get("kind") == "run"]
    cfg = json.load(open(os.path.join(d, "configs.json")))
    target = cfg["args"]["target"]
    # E65 amendment A8: a pass run with no approach (--preheat 0, the sentinel --target 200 of E65 block D) has no
    # launch setpoint, so the "within 0.5 C of the target" gate cannot apply. Its launch reading is a covariate,
    # not a gate; target None switches the gate to "a reading was recorded". Every E60 pass keeps its setpoint.
    if float(cfg["args"].get("preheat", 1)) <= 0:
        target = None
    card = cfg.get("card") or os.path.basename(os.path.dirname(os.path.dirname(d)))
    by = defaultdict(list)
    for r in recs:
        by[(r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))].append(r)
    out = []
    for m in marks:
        key = (m["block"], m["item"], m.get("pos", 0), m.get("attempt", 1))
        rr = sorted(by.get(key, []), key=lambda r: r["t_start_ms"])
        if not rr:
            continue
        it = man.get(m["item"], {})
        t0 = rr[0]["t_start_ms"]
        lo = t0 + 1000
        ramp_ms = None
        if gov_free:   # amendment A2: start 0.5 s after the clock first reads the busy clock, never before second 1
            at = np.where((t >= t0) & (t <= t0 + 4000) & (mhz == busy_mhz))[0]
            if len(at):
                ramp_ms = float(t[at[0]] - t0)
                lo = max(t0 + 1000, t[at[0]] + 500)
        hi = lo + 2000
        w = (t >= lo) & (t < hi)
        w14 = (t >= t0 + 1000) & (t < t0 + 4000)
        wr = (t >= lo + 1000) & (t < min(lo + 3000, rr[-1]["t_end_ms"]))   # the rails are 1 s running averages; never past the run
        tr = (t >= max(t0 + 800, lo - 200)) & (t <= rr[-1]["t_end_ms"])
        if w.sum() < 5:
            continue
        body = [r for r in rr if r.get("launch", 0) >= 0] if rr[0]["kind"] == "fma" else rr
        work = 0.0
        for r in body:
            dur = max(1.0, r["t_end_ms"] - r["t_start_ms"])
            ov = max(0.0, min(r["t_end_ms"], hi) - max(r["t_start_ms"], lo))
            n = r["iters"] * r.get("minions", 1024) if rr[0]["kind"] == "fma" else r["ops"]
            work += n * ov / dur
        rec = {"card": card, "pass": m["block"], "item": m["item"], "pos": m.get("pos", 0), "attempt": m.get("attempt", 1),
               "kind": rr[0]["kind"], "family": it.get("family"), "dir": d,
               "start_c": m.get("start_c"), "on_protocol": m.get("on_protocol"), "target": target,
               "p_raw": float(P[w].mean()), "p_raw14": float(P[w14].mean()), "t_win": float(T[w].mean()),
               "rail": float(rail[wr].mean()) if wr.sum() else None,
               "mhz": sorted(set(int(x) for x in mhz[w])), "mv": float(mv[w].mean()),
               "rate": work / ((hi - lo) / 1000.0),     # fma: minion-ops/s; ec: instructions/s
               "ramp_ms": ramp_ms, "window_start_s": (lo - t0) / 1000.0,
               "cycles_per_op": float(np.mean([r["cycles_per_op"] for r in body])) if rr[0]["kind"] == "fma" and body else None,
               "ok_records": all(r.get("ok", False) for r in rr),
               "_tP": (T[tr].tolist(), P[tr].tolist())}
        out.append(rec)
    return out, card


def leak_slope(runs):
    """W per C from the within-run drift of runs whose reading rises >= 1 C after second 0.8 (21 Sep's method)."""
    ks = []
    for r in runs:
        T_, P_ = r["_tP"]
        if len(T_) > 10 and max(T_) - min(T_) >= 1:
            ks.append(float(np.polyfit(T_, P_, 1)[0]))
    return (float(np.median(ks)), len(ks)) if ks else (0.4, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--leak", default="auto")
    a = ap.parse_args()
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}
    pred = json.load(open(a.pred))["items"]
    allruns = []
    for d in a.dirs:
        card_ = json.load(open(os.path.join(d, "configs.json"))).get("card") or ""
        gov_free = not card_.startswith("aifoundry3")      # aifoundry3 is pinned at 600 MHz by its boot service
        rs, _ = runs_of_pass(d, man, gov_free=gov_free)
        allruns += rs
    # amendment A3: items a card cannot run at its clock (the governor's power threshold), excluded by name
    excluded = {"aifoundry2": {"ls_h8"}}
    dropped_a3 = [r for r in allruns if r["item"] in excluded.get(r["card"], set())]
    allruns = [r for r in allruns if r["item"] not in excluded.get(r["card"], set())]
    res = {"cards": {}, "gates": {}, "excluded_a3": sorted({(r["card"], r["item"]) for r in dropped_a3}), "excluded_a3_runs": len(dropped_a3)}
    rows_csv = []
    for card in sorted({r["card"] for r in allruns}):
        R = [r for r in allruns if r["card"] == card]
        k, nk = leak_slope(R) if a.leak == "auto" else (float(a.leak), -1)
        clock = int(np.median([r["mhz"][0] for r in R if len(r["mhz"]) == 1]))
        for r in R:
            r["p80"] = r["p_raw"] - k * (r["t_win"] - (r["start_c"] if r["start_c"] is not None else r["t_win"]))
        # ---- gates
        fails = defaultdict(list)
        med_mv = {p: float(np.median([r["mv"] for r in R if r["pass"] == p])) for p in {r["pass"] for r in R}}
        for r in R:
            why = []
            if r["mhz"] != [clock]:
                why.append(f"clock {r['mhz']}")
            if r.get("ramp_ms") is not None and r["ramp_ms"] > 1500:
                why.append(f"ramp {r['ramp_ms']:.0f} ms")
            if abs(r["mv"] - med_mv[r["pass"]]) > 3:
                why.append(f"mv {r['mv']:.1f}")
            if r["start_c"] is None or (r["target"] is not None
                                        and (not r["on_protocol"] or abs(r["start_c"] - r["target"]) > 0.5)):
                why.append(f"launch {r['start_c']}")
            if not r["ok_records"]:
                why.append("record not ok")
            r["fail"] = why
        for p in {r["pass"] for r in R}:   # cycles per op against the family zero in the pass
            zc = {r["item"]: r["cycles_per_op"] for r in R if r["pass"] == p and r["cycles_per_op"]}
            for r in R:
                if r["pass"] != p or not r["cycles_per_op"]:
                    continue
                z = item_zero(man, r["item"], r["family"])
                if z in zc and abs(r["cycles_per_op"] / zc[z] - 1) > 0.005:
                    r["fail"].append(f"cycles/op {r['cycles_per_op']:.2f} vs {zc[z]:.2f}")
        passes_out = []
        for p in sorted({r["pass"] for r in R}):
            rp = [r for r in R if r["pass"] == p]
            nf = sum(1 for r in rp if r["fail"])
            pis = sorted([r for r in rp if r["item"] == "anchor_pi" and not r["fail"]], key=lambda r: r["pos"])
            drift = pis[-1]["p80"] - pis[0]["p80"] if len(pis) >= 2 else None
            if nf > 1 or (drift is not None and abs(drift) > 0.3):
                passes_out.append({"pass": p, "failed_runs": nf, "pi_drift_W": drift})
        bad_passes = {x["pass"] for x in passes_out}
        G = [r for r in R if not r["fail"] and r["pass"] not in bad_passes]
        res["gates"][card] = {"runs": len(R), "kept": len(G), "clock_mhz": clock, "leak_W_per_C": k, "leak_runs": nk,
                              "failed": [(r["pass"], r["item"], r["pos"], r["fail"]) for r in R if r["fail"]],
                              "passes_set_aside": passes_out}
        v = float(np.mean([r["mv"] for r in G])) / 1000 if G else 0.52
        # ---- one value per (pass, item): mean of its runs (anchor_pi runs twice)
        val = defaultdict(dict)
        for p in sorted({r["pass"] for r in G}):
            for item in sorted({r["item"] for r in G if r["pass"] == p}):
                rr = [r for r in G if r["pass"] == p and r["item"] == item]
                val[p][item] = {key: float(np.mean([r[key] for r in rr if r[key] is not None])) if any(r[key] is not None for r in rr) else None
                                for key in ("p80", "p_raw", "p_raw14", "rail", "rate", "mv", "t_win")}
        passes = sorted(val)
        C = {"clock_mhz": clock, "v_mean": v, "passes": passes, "n_runs_kept": len(G)}
        # ---- items: mean over passes of (item - zero)
        items = defaultdict(dict)
        for item in sorted({i for p in passes for i in val[p]}):
            fam = man.get(item, {}).get("family")
            z = item_zero(man, item, fam)
            ent = {"family": fam}
            for key in ("p80", "p_raw", "rail"):
                m_, se, n = mean_se([val[p][item][key] for p in passes if item in val[p]])
                ent[key] = m_
                ent[key + "_se"] = se
                ent["n"] = n
                if z and z != item:
                    dm, dse, dn = mean_se([val[p][item][key] - val[p][z][key] for p in passes if item in val[p] and z in val[p]
                                           and val[p][item][key] is not None and val[p][z][key] is not None])
                    ent["d_" + key], ent["d_" + key + "_se"], ent["d_n"] = dm, dse, dn
            ent["zero"] = z
            ent["rate"] = mean_se([val[p][item]["rate"] for p in passes if item in val[p]])[0]
            items[item] = ent
        C["items"] = items
        # ---- fma ladders: per-pass slopes over h >= 1
        scale = (clock / 600.0) * (v / 0.517) ** 2   # the predictions' switching watts at this card's f and V

        def dpred(n, z_):
            """(predicted n - predicted z_) scaled to this card, or None when either has no RTL replay (A4)."""
            if n not in pred or z_ not in pred:
                return None
            return (pred[n]["p_switching_w"] - pred[z_]["p_switching_w"]) * scale

        for fam in ("lq", "lb"):
            z = ZERO[fam]
            names = [n for n, it in man.items() if it.get("family") == fam and it.get("h", 0) >= 1]
            out = {}
            for reg in ("designed", "bus", "nets"):
                slopes, slopes_rail, firsts = [], [], []
                for p in passes:
                    if z not in val[p]:
                        continue
                    xs, ys, yr = [], [], []
                    for n in names:
                        if n not in val[p]:
                            continue
                        if reg in ("bus", "nets") and n not in pred:
                            continue   # E70 (A19): a rung with no RTL replay (lq_h3, lq_h6) has no bus/nets regressor
                        rate = val[p][n]["rate"]
                        if reg == "designed":
                            x = man[n]["flips"]["b_all"] + man[n]["flips"]["a_all"]
                        elif reg == "bus":
                            x = pred[n]["flips_per_op"]["bus"] - pred[z]["flips_per_op"]["bus"]
                        else:
                            x = pred[n]["nets"] - pred[z]["nets"]
                        xs.append(x * rate)
                        ys.append(val[p][n]["p80"] - val[p][z]["p80"])
                        if val[p][n]["rail"] is not None and val[p][z]["rail"] is not None:
                            yr.append(val[p][n]["rail"] - val[p][z]["rail"])
                    f = fit_line(xs, ys)
                    if f:
                        slopes.append(f[1])
                    if len(yr) == len(xs):
                        fr = fit_line(xs, yr)
                        if fr:
                            slopes_rail.append(fr[1])
                    h1 = f"{fam}_h1"
                    if reg == "designed" and h1 in val[p]:
                        firsts.append(val[p][h1]["p80"] - val[p][z]["p80"])
                m_, se, n = mean_se(slopes)
                mr, ser, nr = mean_se(slopes_rail)
                out[reg] = {"J": m_, "se_J": se, "n_passes": n, **units(m_, v),
                            "rail_J": mr, "rail_se_J": ser, **{"rail_" + k_: v_ for k_, v_ in units(mr, v).items()}}
                if reg == "designed":
                    fm, fse, fn = mean_se(firsts)
                    out["first_flip_W"] = {"W": fm, "se": fse, "n": fn}
            # linearity on the pass-mean differences, and the RTL prediction of each rung (scaled to this card)
            pts = [(man[n]["h"], items[n]["d_p80"]) for n in names if n in items and items[n].get("d_p80") is not None]
            if len(pts) >= 3:
                f = fit_line([h for h, _ in pts], [y for _, y in pts])
                out["linear"] = {"W_per_h": f[1], "intercept_W": f[0], "residual_rms_W": f[2],
                                 "span_W": max(y for _, y in pts) - min(y for _, y in pts)}
            out["rungs"] = {n: {"h": man[n]["h"], "dW": items[n].get("d_p80"), "se": items[n].get("d_p80_se"),
                                "pred_dW": dpred(n, z)}
                            for n in [z] + names if n in items}
            C[fam] = out
        # ---- ls: paired equal-Hamming contrasts against lq
        C["ls_vs_lq"] = {}
        for h in (2, 3, 4, 6, 8, 12, 16):   # E70 (A19): h = 3 and 6 added; a rung that did not run writes no key
            a_, b_ = f"ls_h{h}", f"lq_h{h}"
            d = [val[p][a_]["p80"] - val[p][b_]["p80"] for p in passes if a_ in val[p] and b_ in val[p]]
            if d:
                m_, se, n = mean_se(d)
                C["ls_vs_lq"][h] = {"W": m_, "se": se, "n": n, "pred_W": dpred(a_, b_)}
        # ---- ord: max-flip minus Gray, and every order against Gray, per position
        C["ord"] = {}
        for pos in (0, 19):
            e = {}
            for o in ("binary", "shuffled", "maxflip"):
                a_, g_ = f"ord_{o}_{pos}", f"ord_gray_{pos}"
                d = [val[p][a_]["p80"] - val[p][g_]["p80"] for p in passes if a_ in val[p] and g_ in val[p]]
                draw = [val[p][a_]["p_raw"] - val[p][g_]["p_raw"] for p in passes if a_ in val[p] and g_ in val[p]]
                if d:
                    m_, se, n = mean_se(d)
                    mr_, ser_, _ = mean_se(draw)
                    extra = (man[a_]["flips"]["a_all"] - man[g_]["flips"]["a_all"])
                    rate = items[a_]["rate"] or 1
                    e[o] = {"W": m_, "se": se, "n": n, "raw_W": mr_, "raw_se": ser_, "extra_A_bits_per_op": extra,
                            "J_per_extra_A_bit": m_ / (extra * rate) if extra else None,
                            "pred_W": dpred(a_, g_)}
            if e:
                C["ord"][pos] = e
        # ---- bit scan: item minus its family's zero (a workload in which bit j alternates, against the constant
        # one). bit_<j> has the quiet partner A = 1.0 and lq_h0 as its zero; bpi_<j> has A = pi and lb_h0 (A4).
        for fam_, key_ in (("bit", "bits"), ("bpi", "bits_pi")):
            C[key_] = {}
            z_b = ZERO[fam_]
            for n, it in man.items():
                if it.get("family") == fam_ and n in items and items[n].get("d_p80") is not None:
                    rate = items[n]["rate"] or 1
                    C[key_][it["bit"]] = {"dW": items[n]["d_p80"], "se": items[n]["d_p80_se"], "n": items[n]["d_n"],
                                          "J_per_alternating_bit": items[n]["d_p80"] / (4096 * rate),
                                          "zero": z_b, "pred_dW": dpred(n, z_b)}
        # ---- E67 (Q128, A12): the A side. abit_<j> is A's bit j alternating with the quiet partner B = 1.0,
        # against its own constant-A zero; abp_<j> is the same with the busy partner B = pi, against ap_h0. The
        # per-bit price divides by the item's OWN designed A-bit count from the manifest (2,048 per multiply-add:
        # the issue order holds an A word for two micro-ops, so A can only flip every second cycle), never a
        # constant, so the A and B sides are per-flipped-bit numbers on one footing.
        for fam_, key_ in (("abit", "a_bits"), ("abp", "a_bits_pi")):
            C[key_] = {}
            for n, it in man.items():
                if it.get("family") != fam_ or n not in items or items[n].get("d_p80") is None:
                    continue
                rate = items[n]["rate"] or 1
                nb = it["flips"]["a_all"]
                C[key_][it["bit"]] = {"dW": items[n]["d_p80"], "se": items[n]["d_p80_se"], "n": items[n]["d_n"],
                                      "designed_A_bits_per_op": nb, "zero": items[n]["zero"], "rate": rate,
                                      "J_per_alternating_bit": items[n]["d_p80"] / (nb * rate),
                                      **{"e_" + k_: v_ for k_, v_ in units(items[n]["d_p80"] / (nb * rate), v).items()}}
        # the busy partner's premium at a shared position, paired per pass
        C["a_partner"] = {}
        for n, it in man.items():
            if it.get("family") != "abp":
                continue
            q_ = f"abit_{it['bit']}"
            d = [(val[p][n]["p80"] - val[p]["ap_h0"]["p80"]) - (val[p][q_]["p80"] - val[p][man[q_]["zero"]]["p80"])
                 for p in passes if all(x in val[p] for x in (n, q_, "ap_h0", man[q_]["zero"]))]
            if d:
                m_, se, n_ = mean_se(d)
                C["a_partner"][it["bit"]] = {"W": m_, "se": se, "n": n_}
        # ---- E67 (Q128, A12): the interaction grid. The cell's excess over the sum of its two margins is the
        # paired contrast (cell - A-only - B-only + base) per pass, which cancels the base and every pass offset.
        if "ix_z" in items:
            g = {"base_W": items["ix_z"].get("p80"), "cells": {}, "margins": {}}
            for b_ in IX_BITS:
                for side, nm in (("a", f"ix_a{b_}"), ("b", f"ix_b{b_}")):
                    if nm in items and items[nm].get("d_p80") is not None:
                        nbits = man[nm]["flips"]["a_all" if side == "a" else "b_all"]
                        rate = items[nm]["rate"] or 1
                        g["margins"][nm] = {"dW": items[nm]["d_p80"], "se": items[nm]["d_p80_se"],
                                            "side": side, "bit": b_, "designed_bits_per_op": nbits,
                                            "J_per_alternating_bit": items[nm]["d_p80"] / (nbits * rate)}
            for i_ in IX_BITS:
                for j_ in IX_BITS:
                    c_, a_, b2_ = f"ix_{i_}_{j_}", f"ix_a{i_}", f"ix_b{j_}"
                    if not all(x in items and items[x].get("d_p80") is not None for x in (c_, a_, b2_)):
                        continue
                    d = [val[p][c_]["p80"] - val[p][a_]["p80"] - val[p][b2_]["p80"] + val[p]["ix_z"]["p80"]
                         for p in passes if all(x in val[p] for x in (c_, a_, b2_, "ix_z"))]
                    m_, se, n_ = mean_se(d)
                    sum_ = items[a_]["d_p80"] + items[b2_]["d_p80"]
                    g["cells"][f"{i_}_{j_}"] = {"a_bit": i_, "b_bit": j_, "cell_dW": items[c_]["d_p80"],
                                                "cell_se": items[c_]["d_p80_se"], "a_dW": items[a_]["d_p80"],
                                                "b_dW": items[b2_]["d_p80"], "sum_dW": sum_,
                                                "excess_W": m_, "excess_se": se, "n": n_,
                                                "excess_frac_of_sum": (m_ / sum_) if sum_ else None}
            ex = [x["excess_W"] for x in g["cells"].values() if x["excess_W"] is not None]
            fr = [x["excess_frac_of_sum"] for x in g["cells"].values() if x["excess_frac_of_sum"] is not None]
            if ex:
                g["excess_mean_W"], g["excess_mean_se"], g["n_cells"] = mean_se(ex)
                g["excess_frac_mean"] = float(np.mean(fr)) if fr else None
                g["excess_abs_max_W"] = max(abs(x) for x in ex)
            C["ix"] = g
        # ---- E67 (Q128, A12): the anchors, and the one-side-random pair the closure test reads
        C["anchors"] = {n: {"p80": items[n].get("p80"), "se": items[n].get("p80_se"), "n": items[n].get("n"),
                            "p_raw": items[n].get("p_raw"), "rail": items[n].get("rail"),
                            "rate": items[n].get("rate"),
                            "A_bits_per_op": man.get(n, {}).get("flips", {}).get("a_all"),
                            "B_bits_per_op": man.get(n, {}).get("flips", {}).get("b_all"),
                            "dW_vs_zero": items[n].get("d_p80"), "dW_se": items[n].get("d_p80_se"),
                            "zero": items[n].get("zero")}
                        for n in sorted(items)
                        if man.get(n, {}).get("family") in ("anchor", "nrd")
                        or n in ("lq_h0", "lb_h0", "aq_h0", "aq_e64", "ap_h0", "ix_z")}
        # ---- ec: per-pass slopes, e_in from xin (and ain), e_out from xio and xnz
        ec = {}
        for fam, excl in (("xin", ()), ("ain", ("ain_h32",)), ("xio", ()), ("xnz", ())):
            z = ZERO[fam]
            names = [n for n, it in man.items() if it.get("family") == fam and n not in excl and n != z]
            sl, slr = [], []
            for p in passes:
                if z not in val[p]:
                    continue
                xs, ys, yr = [0.0], [0.0], [0.0]
                for n in names:
                    if n in val[p]:
                        po = man[n]["per_op"]
                        xs.append((po["in"] + po["out"]) * val[p][n]["rate"])
                        ys.append(val[p][n]["p80"] - val[p][z]["p80"])
                        yr.append((val[p][n]["rail"] or 0) - (val[p][z]["rail"] or 0))
                if len(xs) >= 3:
                    f, fr = fit_line(xs, ys), fit_line(xs, yr)
                    if f:
                        sl.append(f[1])
                        slr.append(fr[1] if fr else None)
                elif len(xs) == 2 and xs[1]:   # one rung besides the zero: the slope through the zero
                    sl.append(ys[1] / xs[1])
                    slr.append(yr[1] / xs[1])
            m_, se, n = mean_se(sl)
            mr, ser, _ = mean_se(slr)
            ec[fam] = {"J_per_bit": m_, "se_J": se, "n_passes": n, **units(m_, v), "rail_J_per_bit": mr, "rail_se_J": ser}
        if ec.get("xin", {}).get("J_per_bit") is not None:
            e_in, e_in_se = ec["xin"]["J_per_bit"], ec["xin"]["se_J"] or 0
            for fam in ("xio", "xnz"):
                if ec.get(fam, {}).get("J_per_bit") is not None:
                    s_ = ec[fam]["J_per_bit"]          # xio/xnz: (e_in + e_out) / 2 per (port + result) bit
                    e_out = 2 * s_ - e_in
                    ec[f"e_out_from_{fam}"] = {"J": e_out, "se_J": math.sqrt((2 * (ec[fam]["se_J"] or 0)) ** 2 + e_in_se ** 2), **units(e_out, v)}
            ec["e_in"] = {"J": e_in, "se_J": e_in_se, **units(e_in, v)}
            if "ain_h32" in items and items["ain_h32"].get("d_p80") is not None:
                ec["ain_h32_corner"] = {"dW": items["ain_h32"]["d_p80"], "se": items["ain_h32"]["d_p80_se"]}
        C["ec"] = ec
        # ---- RTL score: every fma item with a prediction, measured difference from its zero against predicted
        errs = []
        for n, it in man.items():
            if it["kind"] != "fma" or it["family"] in ("anchor",) or n not in items or items[n].get("d_p80") is None:
                continue
            z = items[n]["zero"]
            if n in pred and z in pred:
                errs.append((n, items[n]["d_p80"], (pred[n]["p_switching_w"] - pred[z]["p_switching_w"]) * scale))
        if errs:
            C["rtl_score"] = {"rms_W": float(math.sqrt(np.mean([(m_ - p_) ** 2 for _, m_, p_ in errs]))),
                              "ratio_measured_over_pred": float(np.sum([m_ * p_ for _, m_, p_ in errs]) / np.sum([p_ * p_ for _, m_, p_ in errs])),
                              "n_items": len(errs), "scale": scale,
                              "items": {n: {"measured_W": m_, "pred_W": p_} for n, m_, p_ in errs}}
        res["cards"][card] = C
        for r in R:
            rows_csv.append({k_: (json.dumps(r[k_]) if isinstance(r[k_], (list, dict)) else r[k_])
                             for k_ in ("card", "pass", "item", "pos", "attempt", "kind", "family", "start_c", "on_protocol", "p_raw",
                                        "p_raw14", "p80", "t_win", "rail", "mv", "mhz", "rate", "cycles_per_op", "fail")})
    # ---- V^2 across cards: per-flip energies relative to aifoundry3
    ref = res["cards"].get("aifoundry3")
    if ref:
        vr = {}
        for card, C in res["cards"].items():
            e = {"v": C["v_mean"], "v2_ratio": (C["v_mean"] / ref["v_mean"]) ** 2, "clock": C["clock_mhz"]}
            for name, get in (("xin_J", lambda c: c.get("ec", {}).get("xin", {}).get("J_per_bit")),
                              ("lq_h2_h8_J", lambda c: None)):
                pass
            # lq between h2 and h8 only (every card ran both): per-pass ratio of the difference to the designed flips
            def lq28(c):
                it = c["items"]
                if "lq_h8" in it and "lq_h2" in it and it["lq_h8"].get("d_p80") is not None and it["lq_h2"].get("d_p80") is not None:
                    rate = it["lq_h8"]["rate"]
                    return (it["lq_h8"]["d_p80"] - it["lq_h2"]["d_p80"]) / ((32768 - 8192) * rate)
                return None
            e["lq_h2_h8_J"] = lq28(C)
            e["xin_J"] = C.get("ec", {}).get("xin", {}).get("J_per_bit")
            # the same on the minion rail (the die's own supply; the board meter's scale differs card to card)
            def lq28r(c):
                it = c["items"]
                if all(n in it and it[n].get("d_rail") is not None for n in ("lq_h8", "lq_h2")):
                    return (it["lq_h8"]["d_rail"] - it["lq_h2"]["d_rail"]) / ((32768 - 8192) * it["lq_h8"]["rate"])
                return None
            e["lq_h2_h8_rail_J"] = lq28r(C)
            e["xin_rail_J"] = C.get("ec", {}).get("xin", {}).get("rail_J_per_bit")
            r0 = lq28r(ref)
            e["lq_h2_h8_rail_J_ratio"] = e["lq_h2_h8_rail_J"] / r0 if e["lq_h2_h8_rail_J"] and r0 else None
            r0 = ref.get("ec", {}).get("xin", {}).get("rail_J_per_bit")
            e["xin_rail_J_ratio"] = e["xin_rail_J"] / r0 if e["xin_rail_J"] and r0 else None
            for kk in ("lq_h2_h8_J", "xin_J"):
                r0 = (lq28(ref) if kk == "lq_h2_h8_J" else ref.get("ec", {}).get("xin", {}).get("J_per_bit"))
                e[kk + "_ratio"] = e[kk] / r0 if e[kk] and r0 else None
            vr[card] = e
        res["v2"] = vr
    for r in allruns:
        r.pop("_tP", None)
    res["runs"] = allruns
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    if a.csv and rows_csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows_csv[0]))
            w.writeheader()
            w.writerows(rows_csv)
    # ---- summary
    for card, C in res["cards"].items():
        g = res["gates"][card]
        print(f"== {card}: {C['clock_mhz']} MHz, {C['v_mean']*1000:.1f} mV, passes {C['passes']}, runs kept {g['kept']}/{g['runs']}, "
              f"leak {g['leak_W_per_C']:.3f} W/C ({g['leak_runs']} runs); passes set aside {g['passes_set_aside']}")
        for fam in ("lq", "lb"):
            if fam in C:
                o = C[fam]
                for reg in ("designed", "bus", "nets"):
                    q = o[reg]
                    if q.get("J") is not None:
                        print(f"  {fam} per {reg:8s}: {q['fJ']:8.3f} +- {(q['se_J'] or 0)*1e15:.3f} fJ  ({q['C_fF']:.1f} fF, {q['electrons']:.3g} e-), "
                              f"rail {q.get('rail_fJ', float('nan')):.3f} fJ, {q['n_passes']} passes")
                if o.get("first_flip_W", {}).get("W") is not None:
                    print(f"  {fam} first flip: {o['first_flip_W']['W']:.3f} +- {o['first_flip_W']['se'] or 0:.3f} W; linear: {o.get('linear')}")
        for pos, e in C.get("ord", {}).items():
            if "maxflip" in e:
                q = e["maxflip"]
                pr_ = "n/a" if q.get("pred_W") is None else f"{q['pred_W']:.3f}"
                print(f"  ord pos {pos}: max-flip - Gray = {q['W']:.3f} +- {q['se'] or 0:.3f} W (raw {q['raw_W']:.3f}), pred {pr_}, n {q['n']}")
        for key_, lbl_ in (("a_bits", "A bits (B=1.0)"), ("a_bits_pi", "A bits (B=pi)")):
            if C.get(key_):
                print(f"  {lbl_}: " + ", ".join(f"{b}:{x['dW']:.2f}W/{x['e_fJ']:.0f}fJ" for b, x in sorted(C[key_].items())))
        if C.get("ix"):
            g = C["ix"]
            print(f"  grid: base {g['base_W']:.2f} W, {g.get('n_cells')} cells, mean excess over the sum "
                  f"{g.get('excess_mean_W') if g.get('excess_mean_W') is None else round(g['excess_mean_W'], 3)} "
                  f"+- {g.get('excess_mean_se') if g.get('excess_mean_se') is None else round(g['excess_mean_se'], 3)} W, "
                  f"|max| {g.get('excess_abs_max_W') if g.get('excess_abs_max_W') is None else round(g['excess_abs_max_W'], 3)} W")
        if C.get("anchors"):
            print("  anchors: " + ", ".join(f"{n}:{a_['p80']:.2f}" for n, a_ in sorted(C["anchors"].items())
                                            if a_.get("p80") is not None))
        for key_, lbl_ in (("bits", "bits (A=1.0)"), ("bits_pi", "bits (A=pi)")):
            if C.get(key_):
                print(f"  {lbl_}: " + ", ".join(f"{b}:{x['dW']:.2f}" for b, x in sorted(C[key_].items())))
        ec = C.get("ec", {})
        for kk in ("e_in", "e_out_from_xio", "e_out_from_xnz"):
            if kk in ec:
                print(f"  {kk}: {ec[kk]['fJ']:.2f} +- {ec[kk]['se_J']*1e15:.2f} fJ ({ec[kk]['C_fF']:.1f} fF)")
        if "ain" in ec and ec["ain"].get("J_per_bit") is not None:
            print(f"  ain (fand.pi) per port bit: {ec['ain']['fJ']:.2f} +- {(ec['ain']['se_J'] or 0)*1e15:.2f} fJ")
        if "rtl_score" in C:
            print(f"  RTL predictions: rms {C['rtl_score']['rms_W']:.2f} W over {C['rtl_score']['n_items']} items; measured/predicted {C['rtl_score']['ratio_measured_over_pred']:.3f}")
    if "v2" in res:
        for card, e in res["v2"].items():
            print(f"  V2 {card}: V {e['v']*1000:.1f} mV, (V/V_a3)^2 {e['v2_ratio']:.3f}; board: lq h2-h8 {e['lq_h2_h8_J_ratio']}, xin {e['xin_J_ratio']}; "
                  f"rail: lq h2-h8 {e['lq_h2_h8_rail_J_ratio']}, xin {e['xin_rail_J_ratio']}")


if __name__ == "__main__":
    main()
