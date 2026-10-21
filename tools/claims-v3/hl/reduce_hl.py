#!/usr/bin/env python3
"""V3-HL reduction: board (and minion-rail) power per run at a fixed launch reading, then the price of a bit flip.

    python3 tools/claims-v3/hl/reduce_hl.py <block dir> [<block dir> ...] --gen <make_hl.py dir>
        [--pred predictions.json] --out hl.json [--window 1,3]

Per run (one item in one block): t0 = the start of the process's first (calibration) launch, as
analyze_horace_strict.py does; P = mean board_w over [t0 + 1 s, t0 + 3 s] (--window); the minion rail over the
same window; the clock and voltage seen in it (a run with any sample off the block's main clock is flagged and left
out); the launch reading; the work done (ops per second from the runs' own records).
Per family, within each block, the power of every rung minus the block's zero-flip rung (lq_h0 for lq/ls/bit,
lb_h0 for lb, xin_h0 for the ec ladders; ord items against each other), so leakage and the card's offsets cancel.
Slopes (least squares through the block differences, with the block-to-block spread as the error):
  fma  dP / d(designed operand-bit flips per s)  -> J per flipped input bit, all-in (the cascade included)
       dP / d(RTL counted net toggles per s)     -> J per counted toggle
  ec   P = P0 + e_in * port bits/s + e_out * result bits/s   (xin, xio, ain jointly; block intercepts)
Each energy also as a capacitance C = 2E/V^2 at the run's mean voltage, and as electrons Q = C V / e.
"""
import argparse
import gzip
import json
import math
import os
from collections import defaultdict

import numpy as np

E_CHARGE = 1.602176634e-19
OPS_PER_S_PER_MINION = None   # taken from each run's own cycles_per_op and the clock


def load_jsonl(path):
    out = []
    op = gzip.open if path.endswith(".gz") else open
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path, op = path + ".gz", gzip.open
    if not os.path.exists(path):
        return out
    for line in op(path, "rt"):
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def runs_of_block(d, window):
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    t = np.array([s["t_ms"] for s in tel], dtype=float)
    P = np.array([s["board_w"] for s in tel])
    rail = np.array([s["sp"]["minion_w"][0] for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    mv = np.array([s["die_mv"]["minion"] for s in tel])
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
    recs = load_jsonl(os.path.join(d, "runs.jsonl"))
    card = recs[0]["card"] if recs else os.path.basename(os.path.dirname(os.path.dirname(d)))
    by = defaultdict(list)
    for r in recs:
        by[(r["block"], r["item"])].append(r)
    out = []
    for (blk, item), rr in by.items():
        rr.sort(key=lambda r: r["t_start_ms"])
        t0, t1 = rr[0]["t_start_ms"], rr[-1]["t_end_ms"]
        lo, hi = t0 + window[0] * 1000, t0 + window[1] * 1000
        sel = (t >= lo) & (t <= hi)
        pre = (t >= t0 - 2000) & (t <= t0 - 300)
        if sel.sum() < 5:
            continue
        rec = {"card": card, "dir": d, "block": blk, "item": item, "kind": rr[0]["kind"], "start_c": rr[0].get("start_c"),
               "p": float(P[sel].mean()), "p_sd": float(P[sel].std()), "n": int(sel.sum()),
               "rail": float(rail[sel].mean()), "p_before": float(P[pre].mean()) if pre.any() else None,
               "mhz": sorted(set(int(x) for x in mhz[sel])), "mv": float(mv[sel].mean()),
               "t_start_c": float(T[(t <= t0)][-1]) if (t <= t0).any() else None, "dur_s": (t1 - t0) / 1000}
        if rr[0]["kind"] == "fma":
            body = [r for r in rr if r.get("launch", 0) >= 0]
            rec["cycles_per_op"] = float(np.mean([r["cycles_per_op"] for r in body])) if body else None
            rec["ok"] = all(r.get("ok", False) for r in rr)
        else:
            body = [r for r in rr if r.get("ops")]
            # enercat's own ops_per_s assumes 600 MHz (cycles / 0.6e9): take the rate from ops per cycle and the clock seen
            rec["ops_per_cycle_per_hart"] = float(np.mean([r["ops_per_cycle_per_hart"] for r in body])) if body else None
            rec["participants"] = body[0].get("participants", 1024) if body else None
            clk = rec["mhz"][0] if len(rec["mhz"]) == 1 else None
            rec["ops_per_s"] = rec["ops_per_cycle_per_hart"] * rec["participants"] * clk * 1e6 if body and clk else None
            rec["ok"] = all(r.get("ok", False) for r in rr)
        out.append(rec)
    return out


def line_fit(x, y, w=None):
    """y = a + b x by least squares; returns a, b, se(b), rms."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    X = np.vstack([np.ones_like(x), x]).T
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ c
    dof = max(1, len(y) - 2)
    s2 = float(res @ res) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(c[0]), float(c[1]), float(math.sqrt(cov[1, 1])), float(math.sqrt(np.mean(res ** 2)))


def as_units(e_j, v):
    c = 2 * e_j / v ** 2
    return {"J": e_j, "fJ": e_j * 1e15, "aJ": e_j * 1e18, "C_fF": c * 1e15, "electrons": c * v / E_CHARGE}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred")
    ap.add_argument("--out", required=True)
    ap.add_argument("--window", default="1,3")
    ap.add_argument("--mhz", type=int, default=600, help="keep runs whose window saw only this clock")
    a = ap.parse_args()
    window = tuple(float(x) for x in a.window.split(","))
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}
    pred = json.load(open(a.pred))["items"] if a.pred else {}
    runs = []
    for d in a.dirs:
        runs += runs_of_block(d, window)
    kept = [r for r in runs if r["mhz"] == [a.mhz] and r["ok"]]
    dropped = [r for r in runs if r not in kept]
    res = {"window_s": window, "mhz": a.mhz, "runs": runs, "dropped": [(r["card"], r["block"], r["item"], r["mhz"]) for r in dropped],
           "cards": {}}
    for card in sorted({r["card"] for r in kept}):
        R = [r for r in kept if r["card"] == card]
        cres = {}
        blocks = sorted({(r["dir"], r["block"]) for r in R})
        P = {(r["dir"], r["block"], r["item"]): r for r in R}
        v = float(np.mean([r["mv"] for r in R])) / 1000
        # ---- fma ladders: per block, rung minus the block's h0 rung
        for fam, zero in (("lq", "lq_h0"), ("lb", "lb_h0"), ("ls", "lq_h0"), ("bit", "lq_h0")):
            xs, ys, xt, groups = [], [], [], []
            for (d, b) in blocks:
                if (d, b, zero) not in P:
                    continue
                p0 = P[(d, b, zero)]
                for name, it in man.items():
                    if it.get("family") != fam or (d, b, name) not in P:
                        continue
                    r = P[(d, b, name)]
                    ops_s = 1024 * a.mhz * 1e6 / (r["cycles_per_op"] or 546.0)
                    xs.append(it["flips"]["b_all"] * ops_s)
                    ys.append(r["p"] - p0["p"])
                    if name in pred and zero in pred:
                        xt.append((pred[name]["nets"] - pred[zero]["nets"]) * ops_s)
                    groups.append(name)
            if len(xs) < 3:
                continue
            fam_res = {"n_runs": len(xs), "items": sorted(set(groups))}
            if fam in ("lq", "lb", "ls"):
                a0, b, se, rms = line_fit(xs, ys)
                fam_res["per_input_bit"] = {"slope_J": b, "se_J": se, "intercept_W": a0, "rms_W": rms, **as_units(b, v)}
                if len(xt) == len(xs):
                    a1, b1, se1, rms1 = line_fit(xt, ys)
                    fam_res["per_counted_toggle"] = {"slope_J": b1, "se_J": se1, "intercept_W": a1, "rms_W": rms1, **as_units(b1, v)}
                # per rung means and the per-bit price at each rung
                rung = defaultdict(list)
                for g, x, y in zip(groups, xs, ys):
                    rung[g].append((x, y))
                fam_res["rungs"] = {g: {"dP_W": float(np.mean([y for _, y in vv])), "sd_W": float(np.std([y for _, y in vv], ddof=1)) if len(vv) > 1 else None,
                                        "n": len(vv), "J_per_input_bit": float(np.mean([y for _, y in vv]) / vv[0][0]) if vv[0][0] else None,
                                        "pred_dP_W": (pred[g]["p_board_80c_w"] - pred[zero]["p_board_80c_w"]) if g in pred and zero in pred else None}
                                    for g, vv in rung.items()}
            else:   # bit scan: one price per bit position
                rung = defaultdict(list)
                for g, x, y in zip(groups, xs, ys):
                    rung[g].append((x, y))
                fam_res["bits"] = {g: {"dP_W": float(np.mean([y for _, y in vv])), "sd_W": float(np.std([y for _, y in vv], ddof=1)) if len(vv) > 1 else None,
                                       "n": len(vv), **as_units(float(np.mean([y for _, y in vv]) / vv[0][0]), v),
                                       "pred_dP_W": (pred[g]["p_board_80c_w"] - pred[zero]["p_board_80c_w"]) if g in pred and zero in pred else None}
                                   for g, vv in rung.items()}
            cres[fam] = fam_res
        # ---- order family: max-flip minus Gray, per block and position
        for pos in (0, 19):
            diffs = []
            for (d, b) in blocks:
                g, m = (d, b, f"ord_gray_{pos}"), (d, b, f"ord_maxflip_{pos}")
                if g in P and m in P:
                    diffs.append(P[m]["p"] - P[g]["p"])
            if diffs:
                orders = {}
                for o in ("gray", "binary", "shuffled", "maxflip"):
                    vals = [P[(d, b, f"ord_{o}_{pos}")]["p"] - P[(d, b, f"ord_gray_{pos}")]["p"] for (d, b) in blocks
                            if (d, b, f"ord_{o}_{pos}") in P and (d, b, f"ord_gray_{pos}") in P]
                    if vals:
                        orders[o] = {"dP_vs_gray_W": float(np.mean(vals)), "se_W": float(np.std(vals, ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else None,
                                     "n": len(vals), "flips_per_op": man[f"ord_{o}_{pos}"]["flips"]["a_all"],
                                     "pred_dP_W": (pred[f"ord_{o}_{pos}"]["p_board_80c_w"] - pred[f"ord_gray_{pos}"]["p_board_80c_w"]) if pred else None}
                cres[f"ord_{pos}"] = {"maxflip_minus_gray_W": float(np.mean(diffs)),
                                      "se_W": float(np.std(diffs, ddof=1) / math.sqrt(len(diffs))) if len(diffs) > 1 else None,
                                      "n_blocks": len(diffs), "orders": orders}
        # ---- ec: joint fit with block intercepts
        rows = []
        for (d, b) in blocks:
            for name, it in man.items():
                if it["kind"] != "ec" or (d, b, name) not in P:
                    continue
                r = P[(d, b, name)]
                if not r.get("ops_per_s"):
                    continue
                rows.append((f"{d}:{b}:{it['op']}", it["per_op"]["in"] * r["ops_per_s"], it["per_op"]["out"] * r["ops_per_s"], r["p"], name, it["op"]))
        if len(rows) >= 4:
            keys = sorted({k for k, *_ in rows})
            X = np.zeros((len(rows), len(keys) + 2))
            y = np.zeros(len(rows))
            for i, (k, xin, xout, p, name, op) in enumerate(rows):
                X[i, keys.index(k)] = 1
                X[i, -2], X[i, -1] = xin, xout
                y[i] = p
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            r_ = y - X @ c
            dof = max(1, len(y) - X.shape[1])
            cov = float(r_ @ r_) / dof * np.linalg.pinv(X.T @ X)
            ec = {"n_runs": len(rows), "e_in": {**as_units(float(c[-2]), v), "se_J": float(math.sqrt(cov[-2, -2]))},
                  "e_out": {**as_units(float(c[-1]), v), "se_J": float(math.sqrt(cov[-1, -1]))},
                  "rms_W": float(math.sqrt(np.mean(r_ ** 2)))}
            # per-ladder slopes too
            for fam in ("xin", "xio", "ain"):
                xs, ys = [], []
                for (d, b) in blocks:
                    z = (d, b, "xin_h0")
                    if z not in P:
                        continue
                    for name, it in man.items():
                        if it.get("family") == fam and (d, b, name) in P and P[(d, b, name)].get("ops_per_s"):
                            rr = P[(d, b, name)]
                            xs.append(it["per_op"]["in"] * rr["ops_per_s"])
                            ys.append(rr["p"] - P[z]["p"])
                if len(xs) >= 3:
                    a0, bb, se, rms = line_fit(xs, ys)
                    ec[f"{fam}_slope_per_port_bit"] = {**as_units(bb, v), "se_J": se, "intercept_W": a0, "rms_W": rms, "n": len(xs)}
            cres["ec"] = ec
        # ---- RTL predictions scored: every fma item against its block's lq_h0, measured minus predicted
        if pred:
            errs = []
            for (d, b) in blocks:
                if (d, b, "lq_h0") not in P or "lq_h0" not in pred:
                    continue
                for name in pred:
                    if (d, b, name) in P:
                        errs.append((name, P[(d, b, name)]["p"] - P[(d, b, "lq_h0")]["p"] - (pred[name]["p_board_80c_w"] - pred["lq_h0"]["p_board_80c_w"])))
            by_item = defaultdict(list)
            for n_, e in errs:
                by_item[n_].append(e)
            cres["rtl_score"] = {"rms_W": float(math.sqrt(np.mean([np.mean(v_) ** 2 for v_ in by_item.values()]))) if by_item else None,
                                 "by_item_W": {k: float(np.mean(v_)) for k, v_ in sorted(by_item.items())}}
        cres["v_mean"] = v
        cres["n_runs"] = len(R)
        res["cards"][card] = cres
    json.dump(res, open(a.out, "w"), indent=1)
    for card, cr in res["cards"].items():
        print(f"== {card}: {cr['n_runs']} runs at {a.mhz} MHz, {cr['v_mean']*1000:.0f} mV")
        for fam in ("lq", "lb", "ls"):
            if fam in cr and "per_input_bit" in cr[fam]:
                q = cr[fam]["per_input_bit"]
                print(f"  {fam}: {q['fJ']:.1f} +- {q['se_J']*1e15:.1f} fJ per flipped input bit ({q['C_fF']:.0f} fF, {q['electrons']:.3g} e-), rms {q['rms_W']:.2f} W")
                if "per_counted_toggle" in cr[fam]:
                    t_ = cr[fam]["per_counted_toggle"]
                    print(f"      {t_['aJ']:.1f} +- {t_['se_J']*1e18:.1f} aJ per counted RTL toggle ({t_['C_fF']:.3f} fF)")
        for pos in (0, 19):
            k = f"ord_{pos}"
            if k in cr:
                print(f"  {k}: max-flip - Gray = {cr[k]['maxflip_minus_gray_W']:.3f} +- {cr[k]['se_W'] or float('nan'):.3f} W over {cr[k]['n_blocks']} blocks")
        if "ec" in cr:
            e = cr["ec"]
            print(f"  ec: e_in {e['e_in']['fJ']:.2f} +- {e['e_in']['se_J']*1e15:.2f} fJ per port bit; e_out {e['e_out']['fJ']:.2f} +- {e['e_out']['se_J']*1e15:.2f} fJ per result bit; rms {e['rms_W']:.3f} W")
        if "rtl_score" in cr and cr["rtl_score"]["rms_W"] is not None:
            print(f"  RTL prediction rms (differences from lq_h0): {cr['rtl_score']['rms_W']:.2f} W")


if __name__ == "__main__":
    main()
