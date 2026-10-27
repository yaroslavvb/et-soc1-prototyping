#!/usr/bin/env python3
"""Q129: E60's aifoundry2 per-bit prices re-reduced at a chosen leakage slope, post hoc by arithmetic.

Mirrors tools/claims-v3/hl/reduce_hl.py exactly for the families aifoundry2 ran (lq, xin/e_in, ord),
reading only its own committed runs.csv + manifest + predictions, so the leakage slope can be moved and
the registered pass gate can be either RE-APPLIED at the new slope ("live", what reduce_hl.py does) or
HELD at the registered reduction's pass set ("frozen", the correction-only sensitivity).

  python3 posthoc_e60.py <runs.csv> <manifest.json> <predictions.json> --card aifoundry2 --out out.json
"""
import argparse
import ast
import csv
import json
import math

import numpy as np

E_CHARGE = 1.602176634e-19
ZERO = {"lq": "lq_h0", "lb": "lb_h0", "ls": "lq_h0", "bit": "lq_h0",
        "xin": "xin_h0", "xio": "xin_h0", "xnz": "xin_h0", "ain": "ain_h0", "bpi": "lb_h0"}
PI_DRIFT_W = 0.3     # reduce_hl.py's pass set-aside threshold on anchor_pi's p80 drift
EXCLUDED = {"aifoundry2": {"ls_h8"}}   # amendment A3


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


def item_zero(man, item, fam):
    it = man.get(item, {})
    if "zero" in it:
        return it["zero"]
    return f"ord_gray_{it['pos']}" if fam == "ord" else ZERO.get(fam)


def load_runs(path, card):
    out = []
    for r in csv.DictReader(open(path)):
        if r["card"] != card or r["item"] in EXCLUDED.get(card, set()):
            continue
        g = lambda k: (None if r[k] in ("", "None") else float(r[k]))
        out.append({"pass": int(r["pass"]), "item": r["item"], "pos": int(r["pos"]),
                    "family": r["family"] or None, "p_raw": g("p_raw"), "t_win": g("t_win"),
                    "start_c": g("start_c"), "rail": g("rail"), "mv": g("mv"), "rate": g("rate"),
                    "fail": ast.literal_eval(r["fail"])})
    return out


def reduce_at(R, man, pred, k, frozen_passes=None):
    """One reduction of card rows R at leakage slope k. frozen_passes: keep exactly this pass set."""
    for r in R:
        base = r["start_c"] if r["start_c"] is not None else r["t_win"]
        r["p80"] = r["p_raw"] - k * (r["t_win"] - base)
    all_p = sorted({r["pass"] for r in R})
    set_aside = []
    for p in all_p:
        rp = [r for r in R if r["pass"] == p]
        nf = sum(1 for r in rp if r["fail"])
        pis = sorted([r for r in rp if r["item"] == "anchor_pi" and not r["fail"]], key=lambda r: r["pos"])
        drift = pis[-1]["p80"] - pis[0]["p80"] if len(pis) >= 2 else None
        if nf > 1 or (drift is not None and abs(drift) > PI_DRIFT_W):
            set_aside.append({"pass": p, "failed_runs": nf, "pi_drift_W": drift})
    bad = {x["pass"] for x in set_aside}
    if frozen_passes is not None:
        bad = {p for p in all_p if p not in frozen_passes}
    G = [r for r in R if not r["fail"] and r["pass"] not in bad]
    v = float(np.mean([r["mv"] for r in G])) / 1000 if G else 0.52
    clock = 800
    passes = sorted({r["pass"] for r in G})
    val = {p: {} for p in passes}
    for p in passes:
        for item in sorted({r["item"] for r in G if r["pass"] == p}):
            rr = [r for r in G if r["pass"] == p and r["item"] == item]
            val[p][item] = {key: (float(np.mean([r[key] for r in rr if r[key] is not None]))
                                  if any(r[key] is not None for r in rr) else None)
                            for key in ("p80", "p_raw", "rail", "rate", "mv", "t_win")}
    items = {}
    for item in sorted({i for p in passes for i in val[p]}):
        fam = man.get(item, {}).get("family")
        z = item_zero(man, item, fam)
        ent = {"family": fam}
        for key in ("p80", "p_raw", "rail"):
            m_, se, n = mean_se([val[p][item][key] for p in passes if item in val[p]])
            ent[key], ent[key + "_se"], ent["n"] = m_, se, n
            if z and z != item:
                dm, dse, dn = mean_se([val[p][item][key] - val[p][z][key] for p in passes
                                       if item in val[p] and z in val[p]
                                       and val[p][item][key] is not None and val[p][z][key] is not None])
                ent["d_" + key], ent["d_" + key + "_se"], ent["d_n"] = dm, dse, dn
        ent["zero"] = z
        ent["rate"] = mean_se([val[p][item]["rate"] for p in passes if item in val[p]])[0]
        items[item] = ent
    out = {"leak_W_per_C": k, "passes": passes, "n_runs_kept": len(G), "n_runs": len(R),
           "v_mean": v, "clock_mhz": clock, "passes_set_aside": set_aside,
           "gate": "frozen" if frozen_passes is not None else "live"}
    # ---- lq ladder: per-pass slopes over h >= 1, free intercept
    for fam in ("lq",):
        z = ZERO[fam]
        names = [n for n, it in man.items() if it.get("family") == fam and it.get("h", 0) >= 1]
        res = {}
        for reg in ("designed", "bus", "nets"):
            slopes, slopes_rail, firsts = [], [], []
            for p in passes:
                if z not in val[p]:
                    continue
                xs, ys, yr = [], [], []
                for n in names:
                    if n not in val[p]:
                        continue
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
            mr, ser, _ = mean_se(slopes_rail)
            res[reg] = {"J": m_, "se_J": se, "n_passes": n, **units(m_, v),
                        "rail_J": mr, "rail_se_J": ser, **{"rail_" + a: b for a, b in units(mr, v).items()}}
        out[fam] = res
    # ---- ec: e_in from xin
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
            elif len(xs) == 2 and xs[1]:
                sl.append(ys[1] / xs[1])
                slr.append(yr[1] / xs[1])
        m_, se, n = mean_se(sl)
        mr, ser, _ = mean_se(slr)
        ec[fam] = {"J_per_bit": m_, "se_J": se, "n_passes": n, **units(m_, v),
                   "rail_J_per_bit": mr, "rail_se_J": ser}
    if ec.get("xin", {}).get("J_per_bit") is not None:
        ec["e_in"] = {"J": ec["xin"]["J_per_bit"], "se_J": ec["xin"]["se_J"] or 0,
                      **units(ec["xin"]["J_per_bit"], v)}
    out["ec"] = ec
    # ---- ord: every order against Gray, per position
    out["ord"] = {}
    for pos in (0, 19):
        e = {}
        for o in ("binary", "shuffled", "maxflip"):
            a_, g_ = f"ord_{o}_{pos}", f"ord_gray_{pos}"
            d = [val[p][a_]["p80"] - val[p][g_]["p80"] for p in passes if a_ in val[p] and g_ in val[p]]
            draw = [val[p][a_]["p_raw"] - val[p][g_]["p_raw"] for p in passes if a_ in val[p] and g_ in val[p]]
            if d:
                m_, se, n = mean_se(d)
                mr_, ser_, _ = mean_se(draw)
                extra = man[a_]["flips"]["a_all"] - man[g_]["flips"]["a_all"]
                rate = items[a_]["rate"] or 1
                e[o] = {"W": m_, "se": se, "n": n, "raw_W": mr_, "raw_se": ser_,
                        "extra_A_bits_per_op": extra,
                        "J_per_extra_A_bit": m_ / (extra * rate) if extra else None,
                        "fJ_per_extra_A_bit": (m_ / (extra * rate) * 1e15) if extra else None}
        if e:
            out["ord"][pos] = e
    out["anchors"] = {n: items[n].get("p80") for n in ("anchor_ones", "anchor_pi", "lq_h0") if n in items}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs_csv")
    ap.add_argument("manifest")
    ap.add_argument("predictions")
    ap.add_argument("--card", default="aifoundry2")
    ap.add_argument("--out", required=True)
    ap.add_argument("--frozen", default="", help="comma list of passes to hold as the registered set")
    ap.add_argument("--slopes", default="0.0,0.2917,0.2936,0.2961,0.294,0.327,0.360,0.442,0.456,1.0,1.508")
    a = ap.parse_args()
    man = {it["name"]: it for it in json.load(open(a.manifest))["items"]}
    pred = json.load(open(a.predictions))["items"]
    R = load_runs(a.runs_csv, a.card)
    froz = [int(x) for x in a.frozen.split(",") if x.strip()] or None
    res = {"card": a.card, "live": {}, "frozen": {}, "frozen_pass_set": froz}
    for s in a.slopes.split(","):
        k = float(s)
        res["live"][s] = reduce_at(R, man, pred, k)
        if froz:
            res["frozen"][s] = reduce_at(R, man, pred, k, frozen_passes=froz)
    json.dump(res, open(a.out, "w"), indent=1)
    hdr = "%-28s" % "slope W/C" + "".join("%12s" % s for s in res["live"])
    for mode in ("live", "frozen"):
        if not res[mode]:
            continue
        print(f"=== gate {mode} ===")
        print(hdr)
        rows = [("lq designed fJ", lambda d: d["lq"]["designed"]["fJ"], lambda d: d["lq"]["designed"]["se_J"] * 1e15),
                ("lq bus fJ", lambda d: d["lq"]["bus"]["fJ"], lambda d: d["lq"]["bus"]["se_J"] * 1e15),
                ("lq nets fJ", lambda d: d["lq"]["nets"]["fJ"], lambda d: d["lq"]["nets"]["se_J"] * 1e15),
                ("e_in fJ", lambda d: d["ec"]["e_in"]["fJ"], lambda d: d["ec"]["e_in"]["se_J"] * 1e15),
                ("ord0 maxflip-Gray W", lambda d: d["ord"][0]["maxflip"]["W"], lambda d: d["ord"][0]["maxflip"]["se"]),
                ("ord19 maxflip-Gray W", lambda d: d["ord"][19]["maxflip"]["W"], lambda d: d["ord"][19]["maxflip"]["se"])]
        for name, f, fse in rows:
            cells = []
            for s in res[mode]:
                d = res[mode][s]
                try:
                    cells.append("%7.3f+-%.3f" % (f(d), fse(d)))
                except (KeyError, TypeError, IndexError):
                    cells.append("%12s" % "-")
            print("%-28s" % name + "".join("%12s" % c for c in cells))
        print("%-28s" % "passes kept" + "".join("%12s" % len(res[mode][s]["passes"]) for s in res[mode]))
        print("%-28s" % "runs kept" + "".join("%12s" % res[mode][s]["n_runs_kept"] for s in res[mode]))
        print()
    return 0


if __name__ == "__main__":
    main()
