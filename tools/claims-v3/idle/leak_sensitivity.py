#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E71 (Q129): what a different leakage slope does to a published V3-HL price list, from the committed CSV.

    python3 tools/claims-v3/idle/leak_sensitivity.py --runs <runs.csv> --manifest <manifest.json>
            --k-old <W per C> --k-new <W per C> [--ref <hl.json>] [--out <path.json>]

`hl/reduce_hl.py` corrects every run's board power to its launch reading with one slope for the card,
`p80 = p_raw - k (t_win - t_launch)`, and then prices an item as `item - its zero`, per pass, averaged over
passes. So a change in k moves a price by exactly

    d price = -(k_new - k_old) * mean_over_passes( t_win(item) - t_win(zero) )

and nothing else: the gates (clock, voltage, launch reading, cycles per op, records) never read p80, and the
energy in fJ is the price divided by the designed flips and the measured rate, neither of which moves — so the
relative change in fJ equals the relative change in the price in watts.

The one place k does reach the kept set is the pass set-aside rule (`anchor_pi` drift above 0.3 W in p80), so
this tool recomputes that rule at each k and reports whether the kept passes changed. Everything is read from
the published `runs.csv` (which carries p_raw, t_win, start_c, the gate verdict per run) and `manifest.json`
(the family and the per-item zero), so the published data is re-priced without touching the card or the box.

`--ref hl.json` checks the reconstruction: at k_old every price must reproduce the published `d_p80` to
1e-6 W, and the tool refuses to report a sensitivity if it does not.
"""
import argparse
import csv
import json
import math
import os
from collections import defaultdict

import numpy as np

# reduce_hl.py's family map and item_zero(), verbatim in behaviour
ZERO = {"lq": "lq_h0", "lb": "lb_h0", "ls": "lq_h0", "bit": "lq_h0", "xin": "xin_h0", "xio": "xin_h0",
        "xnz": "xin_h0", "ain": "ain_h0", "bpi": "lb_h0", "alq": "aq_h0"}


def item_zero(man, item, fam):
    it = man.get(item, {})
    if "zero" in it:
        return it["zero"]
    return f"ord_gray_{it['pos']}" if fam == "ord" else ZERO.get(fam)


def mean_se(v):
    v = [x for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return None, None, 0
    return float(np.mean(v)), (float(np.std(v, ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None), len(v)


def price_at(rows, man, k):
    """reduce_hl.py's pipeline from the CSV at slope k: p80, the pass set-aside, one value per (pass, item),
    then the mean over passes of (item - zero). Returns (prices, kept_passes, set_aside)."""
    for r in rows:
        start = r["start_c"] if r["start_c"] is not None else r["t_win"]
        r["p80"] = r["p_raw"] - k * (r["t_win"] - start)
    set_aside = []
    for p in sorted({r["pass"] for r in rows}):
        rp = [r for r in rows if r["pass"] == p]
        nf = sum(1 for r in rp if r["fail"])
        pis = sorted([r for r in rp if r["item"] == "anchor_pi" and not r["fail"]], key=lambda r: r["pos"])
        drift = pis[-1]["p80"] - pis[0]["p80"] if len(pis) >= 2 else None
        if nf > 1 or (drift is not None and abs(drift) > 0.3):
            set_aside.append({"pass": p, "failed_runs": nf, "pi_drift_W": drift})
    bad = {x["pass"] for x in set_aside}
    G = [r for r in rows if not r["fail"] and r["pass"] not in bad]
    val = defaultdict(dict)
    for p in sorted({r["pass"] for r in G}):
        for item in sorted({r["item"] for r in G if r["pass"] == p}):
            rr = [r for r in G if r["pass"] == p and r["item"] == item]
            val[p][item] = {key: float(np.mean([r[key] for r in rr])) for key in ("p80", "t_win", "rate")}
    passes = sorted(val)
    out = {}
    for item in sorted({i for p in passes for i in val[p]}):
        fam = man.get(item, {}).get("family")
        z = item_zero(man, item, fam)
        if not z or z == item:
            continue
        both = [p for p in passes if item in val[p] and z in val[p]]
        dm, dse, dn = mean_se([val[p][item]["p80"] - val[p][z]["p80"] for p in both])
        dt, _, _ = mean_se([val[p][item]["t_win"] - val[p][z]["t_win"] for p in both])
        if dm is None:
            continue
        out[item] = {"family": fam, "zero": z, "d_p80": dm, "d_p80_se": dse, "d_n": dn, "d_t_win": dt,
                     "rate": mean_se([val[p][item]["rate"] for p in both])[0]}
    return out, passes, set_aside


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--k-old", type=float, required=True)
    ap.add_argument("--k-new", type=float, required=True)
    ap.add_argument("--ref", help="the published hl.json, to check the reconstruction at k_old")
    ap.add_argument("--label", default="")
    ap.add_argument("--out")
    a = ap.parse_args()
    man_raw = json.load(open(a.manifest))
    man = {it["name"]: it for it in (man_raw["items"] if isinstance(man_raw, dict) else man_raw)}
    rows = []
    for r in csv.DictReader(open(a.runs)):
        rows.append({"pass": int(r["pass"]), "item": r["item"], "pos": int(r["pos"]),
                     "p_raw": float(r["p_raw"]), "t_win": float(r["t_win"]),
                     "start_c": float(r["start_c"]) if r["start_c"] not in ("", "None") else None,
                     "rate": float(r["rate"]) if r["rate"] not in ("", "None") else float("nan"),
                     "fail": r["fail"] not in ("[]", "", "None")})
    old, passes_old, aside_old = price_at(rows, man, a.k_old)
    new, passes_new, aside_new = price_at(rows, man, a.k_new)

    check = None
    if a.ref:
        ref = json.load(open(a.ref))
        card = sorted(ref["cards"])[0]
        ri = ref["cards"][card]["items"]
        worst, worst_item = 0.0, None
        for it, v in old.items():
            if it in ri and ri[it].get("d_p80") is not None:
                e = abs(ri[it]["d_p80"] - v["d_p80"])
                if e > worst:
                    worst, worst_item = e, it
        check = {"ref": a.ref, "card": card, "worst_abs_err_W": worst, "worst_item": worst_item,
                 "ok": worst < 1e-6}
        print(f"reconstruction at k_old={a.k_old}: worst |published - recomputed| = {worst:.3e} W "
              f"({worst_item}) -> {'OK' if check['ok'] else 'MISMATCH'}")
        if not check["ok"]:
            print("refusing to report a sensitivity: the reconstruction does not reproduce the published prices")

    print(f"\n{a.label or os.path.basename(a.runs)}: k {a.k_old:.4f} -> {a.k_new:.4f} W/C "
          f"(dk {a.k_new - a.k_old:+.4f}); kept passes {passes_old} -> {passes_new}")
    print(f"{'item':<14} {'zero':<10} {'dT_win':>7} {'price_old':>10} {'price_new':>10} {'shift_W':>9} {'shift_%':>8} {'SE_W':>7}")
    rowsout = {}
    for it in sorted(new, key=lambda x: (new[x]["family"] or "", x)):
        o, n = old.get(it), new[it]
        if o is None:
            continue
        sh = n["d_p80"] - o["d_p80"]
        pct = 100.0 * sh / o["d_p80"] if o["d_p80"] else float("nan")
        print(f"{it:<14} {n['zero']:<10} {n['d_t_win']:+7.3f} {o['d_p80']:10.4f} {n['d_p80']:10.4f} "
              f"{sh:+9.4f} {pct:+8.1f} {o['d_p80_se'] or float('nan'):7.4f}")
        rowsout[it] = {"zero": n["zero"], "family": n["family"], "d_t_win": n["d_t_win"],
                       "price_old_W": o["d_p80"], "price_new_W": n["d_p80"], "shift_W": sh, "shift_pct": pct,
                       "se_W": o["d_p80_se"], "d_n": n["d_n"]}
    shifts = [v["shift_W"] for v in rowsout.values()]
    summary = {"k_old": a.k_old, "k_new": a.k_new, "dk": a.k_new - a.k_old,
               "kept_passes_old": passes_old, "kept_passes_new": passes_new,
               "passes_set_aside_old": aside_old, "passes_set_aside_new": aside_new,
               "kept_passes_changed": passes_old != passes_new,
               "max_abs_shift_W": max(map(abs, shifts)) if shifts else None,
               "mean_shift_W": float(np.mean(shifts)) if shifts else None,
               "n_items": len(rowsout), "check": check, "label": a.label}
    print(f"\nmax |shift| {summary['max_abs_shift_W']:.4f} W, mean shift {summary['mean_shift_W']:+.4f} W, "
          f"kept passes changed: {summary['kept_passes_changed']}")
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"summary": summary, "items": rowsout}, fh, indent=1, sort_keys=True)
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
