#!/usr/bin/env python3
"""V3-SM (E68) reduction: per-item DeltaP against its own zero, the stage fit, and P1-P7.

    python3 tools/claims-v3/sm/reduce_sm.py --data build/claims-v3/aifoundry2/sm --gen build/sm-gen \
        --pred docs/reports/data/2026-10-27-e68-stage-map/predictions.json --out sm.json [--csv runs.csv]

Power extraction and the run gates are E60's, imported from `hl/reduce_hl.py` (`runs_of_pass`, `leak_slope`):
P = mean board power over [t0+1 s, t0+3 s) corrected to the launch reading with the card's leakage slope. The
one change is **amendment A1**: the slope is fitted on the gate-passing runs, because this card's clock ramps
600 -> 800 MHz inside the first second and a slope fitted across the ramp measures the ramp (see `apply_leak`).
On top of them, the registered gates of this experiment (README "Pre-registered analysis"):

  * every sample in the run's window at 800 MHz (P7), voltage within 3 mV of the pass median,
    `on_protocol`, all records ok, and fma cycles per op within 0.5 % of the family's zero in the same pass;
  * DeltaP = item - the zero named by the item's manifest entry, within one pass;
  * the unit of replication is the pass; SE is the between-pass standard error.

The stage fit is weighted least squares with no intercept over the nine masked items,
DeltaP_i = b_mul * MUL_i + b_back * BACK_i, MUL and BACK in millions of RTL-name toggles per op.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hl")
sys.path.insert(0, os.path.abspath(HL))
from reduce_hl import runs_of_pass, leak_slope, mean_se  # noqa: E402

BUSY_MHZ = 800
GROUPS_BACK = ("align", "add", "norm", "round")


def gather(data, man):
    passes = sorted((p for p in os.listdir(data) if p.startswith("p") and p[1:].isdigit()),
                    key=lambda p: int(p[1:]))
    allruns, card = [], None
    for p in passes:
        d = os.path.join(data, p)
        bj = os.path.join(d, "block.json")
        if not os.path.exists(bj) or '"status":"ok"' not in open(bj).read().replace(" ", ""):
            continue
        rr, c = runs_of_pass(d, man, gov_free=False, busy_mhz=BUSY_MHZ)
        card = card or c
        allruns += rr
    return allruns, card


def apply_leak(allruns, kept, leak_arg="auto"):
    """Amendment A1: the leakage slope comes from the gate-passing runs, whose window holds no clock ramp.

    This card idles at 600 MHz and the governor raises it to 800 during the launch, so a slope fitted across a
    run that still holds the ramp measures the ramp (4.91 W/C on passes 1-3), not leakage (0.456 W/C on the
    steady runs; E44 measured this card's idle rails at 0.5-0.6 W/C)."""
    k, nk = leak_slope(kept) if leak_arg == "auto" else (float(leak_arg), -1)
    for r in allruns:
        r["p80"] = r["p_raw"] - k * (r["t_win"] - (r["start_c"] if r["start_c"] is not None else r["t_win"]))
    return k, nk


def gate(runs):
    """The registered gates. Returns (kept, dropped-with-reason)."""
    kept, dropped = [], []
    bypass = {}
    for r in runs:
        bypass.setdefault(r["pass"], []).append(r)
    for p, rr in bypass.items():
        mvs = [r["mv"] for r in rr if r["mv"] is not None]
        med = float(np.median(mvs)) if mvs else None
        zc = {}
        for r in rr:
            if r["item"] in ("smz_q", "smz_b") and r["cycles_per_op"]:
                zc[r["item"]] = r["cycles_per_op"]
        for r in rr:
            why = []
            if r["mhz"] != [BUSY_MHZ]:
                why.append(f"clock {r['mhz']}")
            if med is not None and r["mv"] is not None and abs(r["mv"] - med) > 3:
                why.append(f"mv {r['mv']:.1f} vs {med:.1f}")
            if not r["on_protocol"]:
                why.append("off protocol")
            if not r["ok_records"]:
                why.append("record not ok")
            z = zc.get("smz_b" if r["item"] in ("smz_b", "sm_pi_sgn") else "smz_q")
            if r["kind"] == "fma" and r["cycles_per_op"] and z and abs(r["cycles_per_op"] / z - 1) > 0.005:
                why.append(f"cycles/op {r['cycles_per_op']:.1f} vs zero {z:.1f}")
            (dropped if why else kept).append(dict(r, _why="; ".join(why)) if why else r)
    return kept, dropped


def per_item(kept, man):
    """DeltaP per item per pass, then mean +- SE over passes.

    dP_W is the registered quantity (leakage-corrected p80). dP_raw_W is the same difference on the
    uncorrected board power, reported beside it because the correction's coefficient is the one number here
    that is not measured on this experiment's own data: a busier item heats more inside its own window, so a
    wrong slope moves the busy items most. E66 measures this card's idle leakage slope over 51-67 C tonight."""
    byp, byr = {}, {}
    for r in kept:
        byp.setdefault(r["pass"], {}).setdefault(r["item"], []).append(r["p80"])
        byr.setdefault(r["pass"], {}).setdefault(r["item"], []).append(r["p_raw"])
    out = {}
    for name, it in man.items():
        z = it.get("zero")
        if not z or name in ("smz_q", "smz_b"):
            continue
        ds, dr, pw = [], [], []
        for p, items in sorted(byp.items()):
            if name in items and z in items:
                ds.append(float(np.mean(items[name])) - float(np.mean(items[z])))
                dr.append(float(np.mean(byr[p][name])) - float(np.mean(byr[p][z])))
                pw.append(p)
        m, se, n = mean_se(ds)
        mr, ser, _ = mean_se(dr)
        out[name] = {"dP_W": m, "se_W": se, "passes": n, "dP_raw_W": mr, "se_raw_W": ser,
                     "per_pass": dict(zip(pw, ds)), "zero": z}
    return out


def fit_stages(items, pred):
    """Weighted LS, no intercept: dP = b_mul * MUL + b_back * BACK (millions of toggles per op)."""
    X, y, w, names = [], [], [], []
    for n, v in items.items():
        if v["dP_W"] is None or n not in pred:
            continue
        p = pred[n]
        back = sum(p[g] for g in GROUPS_BACK)
        X.append([p["mul"] / 1e6, back / 1e6])
        y.append(v["dP_W"])
        se = v["se_W"] or (0.1 * abs(v["dP_W"]) or 1.0)
        w.append(1.0 / se ** 2)
        names.append(n)
    if len(X) < 3:
        return None
    X, y, w = np.array(X), np.array(y), np.array(w)
    W = np.diag(w)
    XtWX = X.T @ W @ X
    beta = np.linalg.solve(XtWX, X.T @ W @ y)
    resid = y - X @ beta
    dof = max(1, len(y) - 2)
    s2 = float(resid @ W @ resid) / dof
    cov = s2 * np.linalg.inv(XtWX)
    se = np.sqrt(np.diag(cov))
    return {"items": names, "beta_mul_W_per_Mtoggle": float(beta[0]), "se_mul": float(se[0]),
            "beta_back_W_per_Mtoggle": float(beta[1]), "se_back": float(se[1]),
            "ratio_back_over_mul": float(beta[1] / beta[0]) if beta[0] else None,
            "resid_W": dict(zip(names, (float(v) for v in resid))),
            "resid_rms_W": float(np.sqrt(np.mean(resid ** 2))), "dof": dof,
            "pred_W": dict(zip(names, (float(v) for v in X @ beta)))}


def verdicts(items, fit, pred, gates):
    def g(n, k="dP_W"):
        return items.get(n, {}).get(k)

    V = {}

    def put(key, outcome, reading, **kw):
        V[key] = dict({"outcome": outcome, "reading": reading}, **kw)

    # P1 the multiplier's share for sm_lo12
    if fit and "sm_lo12" in pred:
        p = pred["sm_lo12"]
        back = sum(p[x] for x in GROUPS_BACK)
        a = fit["beta_mul_W_per_Mtoggle"] * p["mul"] / 1e6
        b = fit["beta_back_W_per_Mtoggle"] * back / 1e6
        s = a / (a + b) if (a + b) else None
        put("P1", "PASS" if s is not None and 0.35 <= s <= 0.85 else ("UNDECIDED" if s is None else "FAIL"),
            f"s_mul = {s:.3f}" if s is not None else "no fit", s_mul=s, band=[0.35, 0.85])
    else:
        put("P1", "UNDECIDED", "no fit")

    # P2 additivity
    a, b, c = g("sm_lo12"), g("sm_sgn"), g("sm_sgnlo")
    if None not in (a, b, c):
        ses = [items[n]["se_W"] or 0 for n in ("sm_lo12", "sm_sgn", "sm_sgnlo")]
        comb = math.sqrt(sum(s ** 2 for s in ses))
        tol = max(2 * comb, 0.10 * abs(c))
        d = (a + b) - c
        put("P2", "PASS" if abs(d) <= tol else "FAIL",
            f"sm_lo12 + sm_sgn = {a + b:.3f} W vs sm_sgnlo {c:.3f} W; difference {d:+.3f} W, tolerance {tol:.3f} W",
            sum_W=a + b, both_W=c, diff_W=d, tol_W=tol)
    else:
        put("P2", "UNDECIDED", "an item is missing")

    # P3 the frozen-multiplier floor
    s, se = g("sm_sgn"), g("sm_sgn", "se_W")
    lo = g("sm_lo12")
    if s is not None and se:
        r = s / lo if lo else None
        ok = s > 3 * se and r is not None and 0.02 <= r <= 0.25
        put("P3", "PASS" if ok else ("FAIL" if s <= 3 * se or r is None else "FAIL"),
            f"sm_sgn {s:.3f} +- {se:.3f} W ({s / se:.1f} SE); share of sm_lo12 {r:.3f}" if r else f"{s:.3f} W",
            dP_W=s, se_W=se, share_of_lo12=r, band=[0.02, 0.25])
    else:
        put("P3", "UNDECIDED", "sm_sgn has no SE (needs >= 2 passes)")

    # P4 the partner buys nothing when the tree is frozen
    a, b = g("sm_pi_sgn"), g("sm_sgn")
    if None not in (a, b):
        d = abs(a - b)
        ok = d < 0.5 and (b == 0 or d < 0.25 * abs(b))
        put("P4", "PASS" if ok else "FAIL",
            f"sm_pi_sgn {a:.3f} W vs sm_sgn {b:.3f} W; |difference| {d:.3f} W", diff_W=d, band_W=0.5)
    else:
        put("P4", "UNDECIDED", "an item is missing")

    # P5 the aligner ladder
    e1, e16, e64 = g("sm_e1"), g("sm_e16"), g("sm_e64")
    if None not in (e1, e16, e64):
        ses = {n: items[n]["se_W"] or 0 for n in ("sm_e1", "sm_e16", "sm_e64")}
        g1 = e16 - e1 >= math.hypot(ses["sm_e16"], ses["sm_e1"])
        g2 = e64 - e16 >= math.hypot(ses["sm_e64"], ses["sm_e16"])
        ratio = e64 / e1 if e1 else None
        ok = g1 and g2 and ratio is not None and 1.2 <= ratio <= 2.2
        put("P5", "PASS" if ok else "FAIL",
            f"e1 {e1:.3f}, e16 {e16:.3f}, e64 {e64:.3f} W; e64/e1 = {ratio:.2f}" if ratio else "e1 is zero",
            monotone=bool(g1 and g2), ratio=ratio, band=[1.2, 2.2])
    else:
        put("P5", "UNDECIDED", "an item is missing")

    # P6 position inside the mantissa
    lo, sp, hi = g("sm_lo12"), g("sm_sp12"), g("sm_hi12")
    if None not in (lo, sp, hi):
        se2 = math.hypot(items["sm_sp12"]["se_W"] or 0, items["sm_lo12"]["se_W"] or 0)
        ok = sp - lo >= 2 * se2 and hi > lo
        put("P6", "PASS" if ok else "FAIL",
            f"lo12 {lo:.3f}, hi12 {hi:.3f}, sp12 {sp:.3f} W; sp12 - lo12 = {sp - lo:+.3f} W ({se2:.3f} SE)",
            sp_minus_lo_W=sp - lo, hi_minus_lo_W=hi - lo)
    else:
        put("P6", "UNDECIDED", "an item is missing")

    # P7 the clock held. As registered: "every KEPT run is at 800 MHz throughout its window and every item's
    # board maximum is below 60 W. Runs that are not are dropped, counted, and named in the results." So the
    # runs the gate dropped are information, not a failure -- the gate is what makes the statement true.
    off = [r for r in gates["dropped"] if "clock" in r.get("_why", "")]
    hot = gates.get("max_board_w_kept")
    bad = [r for r in gates.get("kept", []) if r["mhz"] != [BUSY_MHZ]]
    ok = not bad and (hot is None or hot < 60)
    put("P7", "PASS" if ok else "FAIL",
        f"every kept run at {BUSY_MHZ} MHz ({len(bad)} not); highest kept board reading {hot:.1f} W; "
        f"{len(off)} of {gates['runs']} runs dropped for a clock ramp in the window"
        if hot else f"{len(off)} off-clock runs",
        off_clock_runs_dropped=len(off), kept_off_clock=len(bad), max_board_w_kept=hot)
    return V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="$DATA_ROOT/sm (one p<N> directory per pass)")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--leak", default="auto")
    a = ap.parse_args()
    man = {i["name"]: i for i in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}
    pred = json.load(open(a.pred))["minus_zero"]
    runs, card = gather(a.data, man)
    kept, dropped = gate(runs)          # the gates read no corrected power, so they run before the correction
    k, nk = apply_leak(runs, kept, a.leak)
    maxw = max((r["p_raw"] for r in runs), default=None)
    maxk = max((r["p_raw"] for r in kept), default=None)
    gates = {"runs": len(runs), "kept": kept, "n_kept": len(kept), "dropped": dropped, "leak_W_per_C": k,
             "leak_runs": nk, "max_board_w": maxw, "max_board_w_kept": maxk, "card": card}
    items = per_item(kept, man)
    fit = fit_stages(items, pred)
    V = verdicts(items, fit, pred, gates)
    out = {"card": card, "gates": {x: gates[x] for x in ("runs", "n_kept", "leak_W_per_C", "leak_runs",
                                                         "max_board_w", "max_board_w_kept")},
           "dropped": [{x: r[x] for x in ("pass", "item", "_why", "mhz", "mv", "start_c")} for r in dropped],
           "items": items, "fit": fit, "verdicts": V}
    json.dump(out, open(a.out, "w"), indent=1, default=float)
    if a.csv:
        with open(a.csv, "w") as f:
            f.write("card,pass,item,p_raw_W,p80_W,start_c,t_win_c,mhz,mv,cycles_per_op,rate\n")
            for r in sorted(runs, key=lambda r: (r["pass"], r["item"])):
                f.write(f"{r['card']},{r['pass']},{r['item']},{r['p_raw']:.3f},{r['p80']:.3f},{r['start_c']},"
                        f"{r['t_win']:.2f},{'|'.join(str(x) for x in r['mhz'])},{r['mv']:.1f},"
                        f"{r['cycles_per_op'] or ''},{r['rate']:.0f}\n")
    print(f"card {card}: {len(runs)} runs, {len(kept)} kept, leak {k:.3f} W/C ({nk} kept runs), "
          f"highest board {maxw:.1f} W (kept {maxk:.1f} W)" if maxw else f"card {card}: no runs")
    print(f"\n{'item':12s} {'dP (W)':>9s} {'SE':>7s} {'passes':>7s} {'dP raw':>9s} {'SE raw':>7s}")
    for n, v in items.items():
        if v["dP_W"] is None:
            continue
        print(f"{n:12s} {v['dP_W']:9.3f} {(v['se_W'] or float('nan')):7.3f} {v['passes']:7d} "
              f"{v['dP_raw_W']:9.3f} {(v['se_raw_W'] or float('nan')):7.3f}")
    if fit:
        print(f"\nfit over {len(fit['items'])} items: b_mul {fit['beta_mul_W_per_Mtoggle']:.4f} +- {fit['se_mul']:.4f}, "
              f"b_back {fit['beta_back_W_per_Mtoggle']:.4f} +- {fit['se_back']:.4f} W per million toggles/op; "
              f"back/mul {fit['ratio_back_over_mul']:.2f}; residual rms {fit['resid_rms_W']:.3f} W")
    print()
    for kk, v in V.items():
        print(f"{kk}  {v['outcome']:9s} {v['reading']}")


if __name__ == "__main__":
    main()
