#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""V3-HLP reduction (E79), as pre-registered in README.md § "Pre-registered analysis".

    python3 tools/claims-v3/hlp/reduce_hlp.py <pass dir> [<pass dir> ...] --gen <make_hlp.py dir>
        --out hlp.json [--csv runs.csv] [--txt reduce.txt] [--leak auto|<W per C>]

The recipe is E60/E65/E67/E70's (tools/claims-v3/hl/reduce_hl.py), with the two additions E79 registers: an
**idle bracket** taken from the second before each launch, and prices quoted with a 95% interval from the
between-pass scatter (Student t, n-1 df) instead of a bare SE.

Per run (one process of one item at one position of one pass):
  t0        the start of its first launch record (the calibration launch);
  P         mean board_w over [t0+1 s, t0+3 s);  raw [1,4) kept as a check;
  rail      mean minion rail over [t0+2 s, t0+4 s) (the rails are 1 s running averages);
  P_idle    mean board_w over [t0-1.2 s, t0-0.2 s) - the card idle at the launch reading, after the approach
            has waited for it, before this run's first launch;
  p80       P - k (T_window - T_launch), the 21 Sep leakage correction, k = the card's slope;
  rate      the work completed inside the power window (launch records overlapping it, prorated), minion-ops/s.
Gates, every failure counted and reported: one clock, the card's own; the rail voltage within 3 mV of the pass
median; an on-protocol launch within 0.5 C of the target; `cycles_per_op` within 0.5% of the item's OWN zero rung
in the same pass (so fp16's 546 is never compared with int8's 318); every launch record `ok`. A pass is set aside
when more than one of its runs fails a gate or its anchor_pi drifts more than 0.3 W from first to last.
Per pass, every item minus its own zero (manifest `zero`). The price of a position is
    e = (P(item) - P(zero)) / (designed flips per op x ops per second)
computed per pass and then averaged over passes; the interval is t(0.975, n-1) x the between-pass SE. The unit of
replication is the pass, never samples inside one burst.
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
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def t95(n):
    if n < 2:
        return None
    return T95.get(n - 1, 1.96 + 2.0 / max(n - 1, 1))


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


def mean_ci(v):
    """mean, SE, n, half-width of the 95% interval (Student t, n-1 df)."""
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return None, None, 0, None
    m = float(np.mean(v))
    if len(v) < 2:
        return m, None, 1, None
    se = float(np.std(v, ddof=1) / math.sqrt(len(v)))
    return m, se, len(v), se * t95(len(v))


def spearman(xs, ys):
    def rank(a):
        order = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and a[order[j + 1]] == a[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    if len(xs) < 3:
        return None
    rx, ry = rank(list(xs)), rank(list(ys))
    mx, my = float(np.mean(rx)), float(np.mean(ry))
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return None if den == 0 else num / den


def units(e_j, v):
    if e_j is None:
        return {}
    c = 2 * e_j / v ** 2
    return {"fJ": e_j * 1e15, "C_fF": c * 1e15, "electrons": c * v / E_CHARGE}


def runs_of_pass(d, man):
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    if not tel:
        return [], None
    t = np.array([s["t_ms"] for s in tel], float)
    P = np.array([s["board_w"] for s in tel], float)
    rail = np.array([s["sp"]["minion_w"][0] for s in tel], float)
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    mv = np.array([s["die_mv"]["minion"] for s in tel], float)
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel], float)
    recs = load_jsonl(os.path.join(d, "runs.jsonl"))
    marks = [m for m in load_jsonl(os.path.join(d, "marks.jsonl")) if m.get("kind") == "run"]
    cfg = json.load(open(os.path.join(d, "configs.json")))
    target = cfg["args"]["target"]
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
        lo, hi = t0 + 1000, t0 + 3000
        w = (t >= lo) & (t < hi)
        w14 = (t >= t0 + 1000) & (t < t0 + 4000)
        wr = (t >= lo + 1000) & (t < min(lo + 3000, rr[-1]["t_end_ms"]))
        wi = (t >= t0 - 1200) & (t < t0 - 200)            # E79: the idle bracket, before this run's first launch
        tr = (t >= max(t0 + 800, lo - 200)) & (t <= rr[-1]["t_end_ms"])
        if w.sum() < 5:
            continue
        work = 0.0
        for r in rr:
            dur = max(1.0, r["t_end_ms"] - r["t_start_ms"])
            ov = max(0.0, min(r["t_end_ms"], hi) - max(r["t_start_ms"], lo))
            work += r["iters"] * r.get("minions", 1024) * ov / dur
        out.append({
            "card": card, "pass": m["block"], "item": m["item"], "pos": m.get("pos", 0),
            "attempt": m.get("attempt", 1), "type": it.get("type"), "family": it.get("family"),
            "zero": it.get("zero"), "dir": d,
            "start_c": m.get("start_c"), "on_protocol": m.get("on_protocol"), "target": target,
            "p_raw": float(P[w].mean()), "p_raw14": float(P[w14].mean()), "t_win": float(T[w].mean()),
            "rail": float(rail[wr].mean()) if wr.sum() else None,
            "p_idle": float(P[wi].mean()) if wi.sum() >= 5 else None,
            "t_idle": float(T[wi].mean()) if wi.sum() >= 5 else None,
            "n_idle": int(wi.sum()),
            "mhz": sorted(set(int(x) for x in mhz[w])), "mv": float(mv[w].mean()),
            "rate": work / ((hi - lo) / 1000.0),
            "cycles_per_op": float(np.mean([r["cycles_per_op"] for r in rr])) if rr else None,
            "ok_records": all(r.get("ok", False) for r in rr),
            "_tP": (T[tr].tolist(), P[tr].tolist()),
        })
    return out, card


def leak_slope(runs):
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
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--txt")
    ap.add_argument("--leak", default="auto")
    a = ap.parse_args()
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}
    allruns = []
    for d in a.dirs:
        rs, _ = runs_of_pass(d, man)
        allruns += rs
    res = {"experiment": "E79", "dirs": a.dirs, "cards": {}}
    rows_csv = []
    for card in sorted({r["card"] for r in allruns}):
        R = [r for r in allruns if r["card"] == card]
        k, nk = leak_slope(R) if a.leak == "auto" else (float(a.leak), -1)
        clock = int(np.median([r["mhz"][0] for r in R if len(r["mhz"]) == 1]))
        for r in R:
            base_c = r["start_c"] if r["start_c"] is not None else r["t_win"]
            r["p80"] = r["p_raw"] - k * (r["t_win"] - base_c)
            r["idle80"] = None if r["p_idle"] is None else r["p_idle"] - k * (r["t_idle"] - base_c)
        # ---- gates
        med_mv = {p: float(np.median([r["mv"] for r in R if r["pass"] == p])) for p in {r["pass"] for r in R}}
        for r in R:
            why = []
            if r["mhz"] != [clock]:
                why.append(f"clock {r['mhz']}")
            if abs(r["mv"] - med_mv[r["pass"]]) > 3:
                why.append(f"mv {r['mv']:.1f}")
            if r["start_c"] is None or (r["target"] is not None
                                        and (not r["on_protocol"] or abs(r["start_c"] - r["target"]) > 0.5)):
                why.append(f"launch {r['start_c']}")
            if not r["ok_records"]:
                why.append("record not ok")
            r["fail"] = why
        for p in {r["pass"] for r in R}:
            zc = {r["item"]: r["cycles_per_op"] for r in R if r["pass"] == p and r["cycles_per_op"]}
            for r in R:
                if r["pass"] != p or not r["cycles_per_op"]:
                    continue
                z = r["zero"]
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
        bad = {x["pass"] for x in passes_out}
        G = [r for r in R if not r["fail"] and r["pass"] not in bad]
        res["cards"][card] = C = {
            "clock_mhz": clock, "leak_W_per_C": k, "leak_runs": nk, "runs": len(R), "kept": len(G),
            "failed": [(r["pass"], r["item"], r["pos"], r["fail"]) for r in R if r["fail"]],
            "passes_set_aside": passes_out, "passes": sorted({r["pass"] for r in G}),
        }
        v = float(np.mean([r["mv"] for r in G])) / 1000 if G else 0.523
        C["v_mean"] = v
        C["cycles_per_op"] = {ty: float(np.median([r["cycles_per_op"] for r in G
                                                   if r["type"] == ty and r["cycles_per_op"]]))
                              for ty in sorted({r["type"] for r in G if r["type"]})
                              if any(r["type"] == ty and r["cycles_per_op"] for r in G)}
        # ---- one value per (pass, item)
        val = defaultdict(dict)
        for r in G:
            val[r["pass"]].setdefault(r["item"], []).append(r)
        per = defaultdict(dict)
        for p, d_ in val.items():
            for item, rr in d_.items():
                per[p][item] = {key: (float(np.mean([x[key] for x in rr if x[key] is not None]))
                                      if any(x[key] is not None for x in rr) else None)
                                for key in ("p80", "p_raw", "p_raw14", "rail", "rate", "mv", "t_win",
                                            "idle80", "p_idle")}
        passes = sorted(per)
        C["n_passes"] = len(passes)
        # ---- items: the difference from its own zero, per pass, then over passes
        items = {}
        for item in sorted({i for p in passes for i in per[p]}):
            it = man.get(item, {})
            z = it.get("zero")
            ent = {"type": it.get("type"), "family": it.get("family"), "zero": z,
                   "bit": it.get("bit"), "bits": it.get("bits"), "side": it.get("side")}
            for key in ("p80", "rail", "rate", "idle80"):
                m_, se, n, hw = mean_ci([per[p][item][key] for p in passes if item in per[p]])
                ent[key], ent[key + "_se"], ent[key + "_n"], ent[key + "_ci95"] = m_, se, n, hw
            if z:
                for key in ("p80", "rail"):
                    dv = [per[p][item][key] - per[p][z][key] for p in passes
                          if item in per[p] and z in per[p]
                          and per[p][item][key] is not None and per[p][z][key] is not None]
                    m_, se, n, hw = mean_ci(dv)
                    ent["d_" + key], ent["d_" + key + "_se"] = m_, se
                    ent["d_" + key + "_n"], ent["d_" + key + "_ci95"] = n, hw
            nb = it.get("flips", {}).get(f"{it.get('side')}_all") if it.get("side") else None
            ent["designed_bits_per_op"] = nb
            if nb and z:
                ev = []
                for p in passes:
                    if item in per[p] and z in per[p] and per[p][item]["rate"]:
                        ev.append((per[p][item]["p80"] - per[p][z]["p80"]) / (nb * per[p][item]["rate"]))
                m_, se, n, hw = mean_ci(ev)
                ent["e_J"], ent["e_se_J"], ent["e_n"], ent["e_ci95_J"] = m_, se, n, hw
                if m_ is not None:
                    ent.update({"e_" + kk: vv for kk, vv in units(m_, v).items()})
                    ent["e_fJ_ci95"] = (hw or 0) * 1e15
                    ent["e_fJ_lo"] = (m_ - (hw or 0)) * 1e15
                    ent["e_fJ_hi"] = (m_ + (hw or 0)) * 1e15
                evr = []
                for p in passes:
                    if (item in per[p] and z in per[p] and per[p][item]["rate"]
                            and per[p][item]["rail"] is not None and per[p][z]["rail"] is not None):
                        evr.append((per[p][item]["rail"] - per[p][z]["rail"]) / (nb * per[p][item]["rate"]))
                m_, se, n, hw = mean_ci(evr)
                ent["e_rail_J"], ent["e_rail_ci95_J"], ent["e_rail_n"] = m_, hw, n
                if m_ is not None:
                    ent["e_rail_fJ"] = m_ * 1e15
                    ent["e_rail_fJ_ci95"] = (hw or 0) * 1e15
            items[item] = ent
        C["items"] = items
        # ---- the price lists, per format and side
        C["prices"] = {}
        for fmt, side, fam in (("fp16", "b", "b16"), ("fp16", "a", "a16"), ("int8", "b", "b8"),
                               ("int8", "a", "a8"), ("fp32", "b", "b32"),
                               # amendment A4: the order probe's own lists, each divided by its own count
                               ("fp16", "b_kg", "b16k"), ("int8", "b_kg", "b8k"), ("fp32", "b_kg", "b32k"),
                               ("fp16", "b_jgp", "b16p"), ("int8", "b_jgp", "b8p"), ("fp32", "b_jgp", "b32p")):
            lst = {}
            for n_, it in man.items():
                if it.get("family") != fam or n_ not in items or items[n_].get("e_fJ") is None:
                    continue
                e = items[n_]
                lst[it["bit"]] = {"item": n_, "field": it.get("field"), "zero": it["zero"],
                                  "designed_bits_per_op": e["designed_bits_per_op"],
                                  "dW": e["d_p80"], "dW_se": e["d_p80_se"], "dW_ci95": e["d_p80_ci95"],
                                  "n_passes": e["e_n"], "rate_ops_s": e["rate"],
                                  "fJ": e["e_fJ"], "fJ_ci95": e["e_fJ_ci95"],
                                  "fJ_lo": e["e_fJ_lo"], "fJ_hi": e["e_fJ_hi"],
                                  "C_fF": e.get("e_C_fF"), "electrons": e.get("e_electrons"),
                                  "rail_fJ": e.get("e_rail_fJ"), "rail_fJ_ci95": e.get("e_rail_fJ_ci95")}
            if lst:
                C["prices"][f"{fmt}_{side}"] = lst
        # ---- the idle bracket, the zeros rung and the h0 switching
        C["switching"] = {}
        for fmt, z in (("fp16", "h16q"), ("int8", "h8q"), ("fp32", "h32q")):
            zz = [(per[p][z]["p80"], per[p][z]["idle80"]) for p in passes
                  if z in per[p] and per[p][z]["idle80"] is not None]
            m_, se, n, hw = mean_ci([x - y for x, y in zz])
            C["switching"][fmt] = {"h0_item": z, "h0_switching_W": m_, "ci95": hw, "n_passes": n,
                                   "idle_W": mean_ci([y for _, y in zz])[0],
                                   "h0_W": mean_ci([x for x, _ in zz])[0]}
        for fmt, zitem, h0 in (("fp16", "z16", "h16q"), ("int8", "z8", "h8q")):
            zs = [(per[p][zitem]["p80"], per[p][zitem]["idle80"], per[p][h0]["p80"], per[p][h0]["idle80"])
                  for p in passes if zitem in per[p] and h0 in per[p]
                  and per[p][zitem]["idle80"] is not None and per[p][h0]["idle80"] is not None]
            sw = [a_ - b_ for a_, b_, _, _ in zs]
            rt = [(a_ - b_) / (c_ - d_) for a_, b_, c_, d_ in zs if (c_ - d_) > 0.05]
            m_, se, n, hw = mean_ci(sw)
            rm, rse, rn, rhw = mean_ci(rt)
            C["switching"][fmt]["zeros_switching_W"] = m_
            C["switching"][fmt]["zeros_ci95"] = hw
            C["switching"][fmt]["zeros_over_h0"] = rm
            C["switching"][fmt]["zeros_over_h0_ci95"] = rhw
            C["switching"][fmt]["zeros_over_h0_n"] = rn
            # amendment A7: the idle-free quantity. P(zeros) - P(h0) is paired per pass and needs no idle
            # bracket, so it is the robust statement of what zeros buy in this format; the idle-bracketed
            # ratio above is kept because P4 is registered on it, with its own spread reported beside it.
            zm, zse, zn, zhw = mean_ci([a_ - c_ for a_, _, c_, _ in zs])
            C["switching"][fmt]["zeros_minus_h0_W"] = zm
            C["switching"][fmt]["zeros_minus_h0_ci95"] = zhw
            C["switching"][fmt]["zeros_minus_h0_n"] = zn
            im, ise, iN, ihw = mean_ci([b_ for _, b_, _, _ in zs])
            C["switching"][fmt]["idle_bracket_W"] = im
            C["switching"][fmt]["idle_bracket_ci95"] = ihw
        # ---- additivity: the multi-bit rungs against the sum of their own single-bit rungs
        C["additivity"] = {}
        for fmt, fam_m, fam_b in (("fp16", "b16m", "b16"), ("int8", "b8m", "b8")):
            for n_, it in man.items():
                if it.get("family") != fam_m or n_ not in items:
                    continue
                singles = [nm for nm, i2 in man.items() if i2.get("family") == fam_b and i2.get("bit") in it["bits"]]
                if len(singles) != len(it["bits"]) or any(nm not in items for nm in singles):
                    continue
                rr = []
                for p in passes:
                    z = it["zero"]
                    if n_ not in per[p] or z not in per[p]:
                        continue
                    got = per[p][n_]["p80"] - per[p][z]["p80"]
                    tot = 0.0
                    ok = True
                    for nm in singles:
                        zs_ = man[nm]["zero"]
                        if nm not in per[p] or zs_ not in per[p]:
                            ok = False
                            break
                        tot += per[p][nm]["p80"] - per[p][zs_]["p80"]
                    if ok and tot > 0.05:
                        rr.append(got / tot)
                m_, se, n, hw = mean_ci(rr)
                C["additivity"][n_] = {"bits": it["bits"], "n_bits": len(it["bits"]), "ratio": m_,
                                       "ci95": hw, "n_passes": n,
                                       "dW": items[n_].get("d_p80"), "dW_ci95": items[n_].get("d_p80_ci95"),
                                       "fJ_per_bit": items[n_].get("e_fJ"), "fJ_ci95": items[n_].get("e_fJ_ci95")}
        # ---- amendment A4: the order probe. For each format, the raw dW of the same single-bit flip in the three
        # layouts at the probe position. These dW ratios are ORDER-FREE - they divide by no designed count - and
        # they are what says which index the operand stream actually alternates on.
        C["order_probe"] = {}
        for fmt, jg, jgp, kg in (("fp16", "b16_9", "b16p_9", "b16k_9"), ("int8", "b8_6", "b8p_6", "b8k_6"),
                                 ("fp32", "b32_22", "b32p_22", "b32k_22")):
            ent = {}
            for lbl, nm in (("jg", jg), ("jgp", jgp), ("kg", kg)):
                if nm not in items:
                    continue
                e = items[nm]
                ent[lbl] = {"item": nm, "dW": e.get("d_p80"), "dW_ci95": e.get("d_p80_ci95"),
                            "n_passes": e.get("d_p80_n"), "designed_bits_per_op": e["designed_bits_per_op"],
                            "fJ": e.get("e_fJ"), "fJ_ci95": e.get("e_fJ_ci95")}
            for lbl in ("jgp", "kg"):
                if lbl in ent and "jg" in ent:
                    rr = []
                    for pp in passes:
                        a_, b_ = ent[lbl]["item"], ent["jg"]["item"]
                        za, zb = man[a_]["zero"], man[b_]["zero"]
                        if all(x in per[pp] for x in (a_, b_, za, zb)):
                            d0 = per[pp][b_]["p80"] - per[pp][zb]["p80"]
                            if abs(d0) > 0.05:
                                rr.append((per[pp][a_]["p80"] - per[pp][za]["p80"]) / d0)
                    m_, se, n, hw = mean_ci(rr)
                    ent[f"dW_{lbl}_over_jg"] = m_
                    ent[f"dW_{lbl}_over_jg_ci95"] = hw
                    ent[f"dW_{lbl}_over_jg_n"] = n
            C["order_probe"][fmt] = ent
        # ---- amendment A4: the MARGINAL price of a flipped bit, from the multi-bit rungs. A single-bit rung
        # against a constant-operand zero measures T + e.n.rate (E67's A13): with the response as saturated as it
        # is here, most of that step is the turn-on T. The marginal price is the slope between the 2-bit and the
        # 4-bit rung, which carries no T at all.
        C["marginal"] = {}
        for fmt, n2, n4 in (("fp16", "b16m2", "b16m4"), ("int8", "b8m2", "b8m4")):
            if n2 not in man or n4 not in man:
                continue
            per_bit = man[n2]["flips"]["b_all"] // len(man[n2]["bits"])
            ev, dv = [], []
            for pp in passes:
                z = man[n2]["zero"]
                if not all(x in per[pp] for x in (n2, n4, z)):
                    continue
                d2 = per[pp][n2]["p80"] - per[pp][z]["p80"]
                d4 = per[pp][n4]["p80"] - per[pp][z]["p80"]
                nb = len(man[n4]["bits"]) - len(man[n2]["bits"])
                dv.append((d4 - d2) / nb)
                if per[pp][n4]["rate"]:
                    ev.append((d4 - d2) / (nb * per_bit * per[pp][n4]["rate"]))
            m_, se, n, hw = mean_ci(ev)
            dm, dse, dn, dhw = mean_ci(dv)
            C["marginal"][fmt] = {"from": [n2, n4], "per_bit_count": per_bit, "dW_per_extra_bit": dm,
                                  "dW_ci95": dhw, "n_passes": n, "fJ": None if m_ is None else m_ * 1e15,
                                  "fJ_ci95": None if hw is None else hw * 1e15}
        # ---- the layout control: the same position in the group-parity layout
        C["layout_control"] = {}
        for n_, it in man.items():
            if not str(it.get("family", "")).endswith("p") or n_ not in items:
                continue
            prim = n_.replace("p_", "_")
            if prim not in items or items[prim].get("e_fJ") is None or items[n_].get("e_fJ") is None:
                continue
            rr = []
            for p in passes:
                z = it["zero"]
                if n_ in per[p] and prim in per[p] and z in per[p] and per[p][n_]["rate"]:
                    e1 = (per[p][n_]["p80"] - per[p][z]["p80"]) / (it["flips"]["b_all"] * per[p][n_]["rate"])
                    e0 = (per[p][prim]["p80"] - per[p][z]["p80"]) / (man[prim]["flips"]["b_all"] * per[p][prim]["rate"])
                    if e0 > 0:
                        rr.append(e1 / e0)
            m_, se, n, hw = mean_ci(rr)
            C["layout_control"][n_] = {"primary": prim, "bit": it.get("bit"), "ratio": m_, "ci95": hw,
                                       "n_passes": n, "fJ_control": items[n_]["e_fJ"],
                                       "fJ_primary": items[prim]["e_fJ"]}
        for r in R:
            rows_csv.append({kk: (vv if kk != "mhz" else "/".join(str(x) for x in vv))
                             for kk, vv in r.items() if kk not in ("_tP",)} | {"fail": ";".join(r["fail"])})
    json.dump(res, open(a.out, "w"), indent=1, default=lambda o: None)
    if a.csv and rows_csv:
        keys = sorted({k for row in rows_csv for k in row})
        with open(a.csv, "w", newline="") as f:
            w_ = csv.DictWriter(f, fieldnames=keys)
            w_.writeheader()
            w_.writerows(rows_csv)
    lines = []
    for card, C in res["cards"].items():
        lines.append(f"{card}: {C['clock_mhz']} MHz, {C['v_mean']*1000:.1f} mV, leak {C['leak_W_per_C']:.3f} W/C "
                     f"({C['leak_runs']} runs), runs kept {C['kept']}/{C['runs']}, passes {C['passes']}")
        if C["passes_set_aside"]:
            lines.append(f"  passes set aside: {C['passes_set_aside']}")
        lines.append(f"  cycles per op: {C['cycles_per_op']}")
        for key, lst in C["prices"].items():
            lines.append(f"  {key}: " + ", ".join(
                f"{b}:{x['fJ']:.0f}+-{(x['fJ_ci95'] or 0):.0f}" for b, x in sorted(lst.items())))
        for fmt, s in C["switching"].items():
            lines.append(f"  {fmt} switching over idle: h0 {s['h0_switching_W']} W, zeros "
                         f"{s.get('zeros_switching_W')} W, zeros/h0 {s.get('zeros_over_h0')}")
        if C["additivity"]:
            lines.append("  additivity: " + ", ".join(
                f"{n}({x['n_bits']}b) {x['ratio']:.3f}+-{(x['ci95'] or 0):.3f}" for n, x in C["additivity"].items()
                if x["ratio"] is not None))
        for fmt, e in C.get("order_probe", {}).items():
            lines.append(f"  order probe {fmt}: " + ", ".join(
                f"{k} dW {e[k]['dW']:.3f} ({e[k]['designed_bits_per_op']} bits, {(e[k]['fJ'] or 0):.0f} fJ)"
                for k in ("jg", "jgp", "kg") if k in e and e[k]["dW"] is not None)
                + "  ratios jgp/jg " + f"{e.get('dW_jgp_over_jg')}" + ", kg/jg " + f"{e.get('dW_kg_over_jg')}")
        for fmt, e in C.get("marginal", {}).items():
            lines.append(f"  marginal {fmt}: {('%.1f' % e['fJ']) if e['fJ'] is not None else '-'} fJ per extra "
                         f"flipped bit ({('%.3f' % e['dW_per_extra_bit']) if e['dW_per_extra_bit'] is not None else '-'} W), "
                         f"{e['n_passes']} passes")
        if C["layout_control"]:
            lines.append("  layout control: " + ", ".join(
                f"{n} {x['ratio']:.3f}+-{(x['ci95'] or 0):.3f}" for n, x in C["layout_control"].items()
                if x["ratio"] is not None))
    txt = "\n".join(lines) + "\n"
    print(txt, end="")
    if a.txt:
        open(a.txt, "w").write(txt)


if __name__ == "__main__":
    main()
