#!/usr/bin/env python3
"""Reduce run_catalogue.py output to per-configuration energies with their pass-to-pass spread, per card.

    analyze_catalogue.py <dir> [<dir> ...] --out catalogue.json

Per (configuration, pass): burst power over its bracketing idle, corrected for the extra leakage of a burst
that ran warmer than its brackets, divided by the rate. Per configuration: mean, standard deviation and
standard error over passes. Then the derived tables: the instruction catalogue, the cross-card ratios, the
wire cost against hop distance (a straight-line fit), the per-line and per-row costs (differences between
strides), the per-neighbourhood cost, and the SRAM rail's leakage against temperature.
"""
import argparse
import collections
import gzip
import json
import math
import os

import numpy as np

A_LEAK_80, T_L = 23.257, 36.0


def leak_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def load_dir(d):
    tp = os.path.join(d, "telemetry.jsonl")
    op = (lambda p: gzip.open(p + ".gz", "rt")) if os.path.exists(tp + ".gz") else open
    tel = [json.loads(l) for l in op(tp) if l.startswith("{")]
    rp = os.path.join(d, "runs.jsonl")
    ro = (lambda p: gzip.open(p + ".gz", "rt")) if os.path.exists(rp + ".gz") else open
    runs = [json.loads(l) for l in ro(rp) if l.strip()]
    return tel, runs


def bursts_of(tel, runs):
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    w = np.array([s["board_w"] for s in tel])
    T = np.array([s["temp_c"]["minshire"][0] for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    rails = {k: np.array([s["sp"][k][0] for s in tel]) for k in ("minion_w", "sram_w", "noc_w")}   # [avg, min, max]: the average
    groups = collections.OrderedDict()
    for r in runs:
        groups.setdefault((r["cfg"], r["pass"]), []).append(r)
    bl = sorted(((k, rs, min(r["t_start_ms"] for r in rs) / 1000.0, max(r["t_end_ms"] for r in rs) / 1000.0)
                 for k, rs in groups.items()), key=lambda b: b[2])
    out = []
    for i, (k, rs, lo, hi) in enumerate(bl):
        busy = (t >= lo + 0.5) & (t <= hi)
        prev_hi = bl[i - 1][3] if i else t[0]
        next_lo = bl[i + 1][2] if i + 1 < len(bl) else t[-1]
        before = (t >= max(prev_hi + 2.3, lo - 3.5)) & (t <= lo - 0.3)
        after = (t >= hi + 2.3) & (t <= min(next_lo - 0.3, hi + 5.5))
        rail_idle = (t >= max(prev_hi + 3.0, lo - 3.5)) & (t <= lo - 0.3)
        if busy.sum() < 5 or before.sum() < 4 or rail_idle.sum() < 3:
            continue
        idle_b = float(w[before].mean())
        idle_a = float(w[after].mean()) if after.sum() >= 4 else float("nan")
        idle = idle_b if np.isnan(idle_a) else 0.5 * (idle_b + idle_a)
        Tb = float(T[busy].mean())
        Ti = float(np.concatenate([T[before], T[after]]).mean()) if after.sum() >= 4 else float(T[before].mean())
        p = float(w[busy].mean())
        over_raw = p - idle
        over = over_raw - leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti)
        wall = hi - lo
        ops = sum(r["ops"] for r in rs)
        by = sum(r["bytes"] for r in rs)
        devs = sum(r["cycles_max"] for r in rs) / 0.6e9
        r0 = rs[0]
        out.append({"cfg": k[0], "pass": k[1], "pattern": r0["pattern"], "unit": r0["unit"], "operands": r0["operands"],
                    "harts": r0["harts"], "scp": r0["scp"], "participants": r0["participants"], "shires": r0["shires"],
                    "hop_distance": r0.get("hop_distance", 0), "mean_hops": r0.get("mean_hops", 0),
                    "stride": r0.get("stride", 0), "access_bytes": r0.get("access_bytes", 0), "minion_mask": r0.get("minion_mask", "0x0"),
                    "launches": len(rs), "wall_s": wall, "device_s": devs, "ops": ops, "bytes": by,
                    "ops_per_s": ops / devs if devs else 0, "bytes_per_s": by / devs if devs else 0,
                    "ops_per_cycle_per_hart": float(np.mean([r["ops_per_cycle_per_hart"] for r in rs])),
                    "p_busy_w": p, "p_idle_w": idle, "over_idle_w": over, "over_idle_raw_w": over_raw,
                    "leak_correction_w": over_raw - over, "die_c_busy": Tb, "die_c_idle": Ti,
                    "mhz_busy_all_600": bool((mhz[busy] == 600).all()), "n_busy": int(busy.sum()),
                    "pj_per_op": over * wall / ops * 1e12 if ops else None,
                    "pj_per_byte": over * wall / by * 1e12 if by else None,
                    # The rail figures are first-order filtered with a time constant of about a second (a step on the
                    # minion rail reaches 61% after 1 s and 88% after 2 s while board power steps at once), so the
                    # split of a burst's power across the minion, SRAM and mesh rails is read from its last 0.6 s and
                    # divided by the 0.94 of the step the filter has reached there, against an idle read 3 s or more
                    # after the previous burst, where 5% of that burst's step remains.
                    "rails_over": {rk: float((v[(t >= hi - 0.6) & (t <= hi)].mean() - v[rail_idle].mean()) / 0.94)
                                   for rk, v in rails.items()},
                    "sram_idle_w": float(rails["sram_w"][rail_idle].mean()), "minion_idle_w": float(rails["minion_w"][rail_idle].mean()),
                    "noc_idle_w": float(rails["noc_w"][rail_idle].mean()), "die_c_before": float(T[rail_idle].mean()),
                    "t_lo": lo, "t_hi": hi})
    return out, (t, w, T, rails)


def summarise(bursts):
    by = collections.OrderedDict()
    for b in bursts:
        by.setdefault(b["cfg"], []).append(b)
    out = {}
    for cfg, bs in by.items():
        def stat(key):
            v = np.array([b[key] for b in bs if b.get(key) is not None], float)
            if not len(v):
                return None
            return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                    "se": float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else 0.0,
                    "min": float(v.min()), "max": float(v.max()), "n": int(len(v))}
        b0 = bs[0]
        out[cfg] = {k: b0[k] for k in ("pattern", "unit", "operands", "harts", "scp", "participants", "shires",
                                        "hop_distance", "mean_hops", "stride", "access_bytes", "minion_mask")}
        for rk in ("minion_w", "sram_w", "noc_w"):
            for b in bs:
                b["rail_" + rk] = b["rails_over"][rk]
        out[cfg].update({"rails_over_w": {rk: stat("rail_" + rk) for rk in ("minion_w", "sram_w", "noc_w")}})
        out[cfg].update({"passes": len(bs), "pj_per_op": stat("pj_per_op"), "pj_per_byte": stat("pj_per_byte"),
                         "over_idle_w": stat("over_idle_w"), "leak_correction_w": stat("leak_correction_w"),
                         "die_c_busy": stat("die_c_busy"), "ops_per_s": stat("ops_per_s"), "bytes_per_s": stat("bytes_per_s"),
                         "ops_per_cycle_per_hart": stat("ops_per_cycle_per_hart"),
                         "all_600mhz": all(b["mhz_busy_all_600"] for b in bs)})
    return out


def sram_leakage(bursts):
    """The SRAM rail during the settled idle stretch before every burst (2.3 s or more after the previous
    burst, so the rail's ~2 s average has let go of it), against die temperature: the leakage of the 128 MB
    of on-chip SRAM, with the same shape as the idle law."""
    bins = collections.defaultdict(list)
    for b in bursts:
        bins[int(round(b["die_c_before"]))].append(b["sram_idle_w"])
    curve = [{"T": k, "sram_w": float(np.mean(v)), "n": len(v)} for k, v in sorted(bins.items()) if len(v) >= 3]
    fit = None
    if len(curve) >= 3:
        x = np.array([c["T"] for c in curve], float); y = np.array([c["sram_w"] for c in curve])
        wts = np.array([c["n"] for c in curve], float)
        A = np.vstack([np.ones_like(x), np.exp((x - 80.0) / T_L)]).T * np.sqrt(wts)[:, None]
        coef, *_ = np.linalg.lstsq(A, y * np.sqrt(wts), rcond=None)
        pred = np.vstack([np.ones_like(x), np.exp((x - 80.0) / T_L)]).T @ coef
        fit = {"P_fix_w": float(coef[0]), "A_leak_80_w": float(coef[1]), "T_L": T_L,
               "mw_per_mb_at_80": float(coef[1]) / 128 * 1e3, "slope_80_mw_per_c": float(coef[1]) / T_L * 1e3,
               "rms_w": float(np.sqrt(np.average((y - pred) ** 2, weights=wts)))}
    return {"curve": curve, "fit": fit, "sram_mb": 128}


def wire_fit(summary, operands):
    pts = [(v["hop_distance"], v["pj_per_byte"]["mean"], v["pj_per_byte"]["se"], v["shires"])
           for k, v in summary.items() if k.startswith("wire/") and v["operands"] == operands and v["pj_per_byte"]]
    local = next((v["pj_per_byte"]["mean"] for k, v in summary.items() if k == f"tload/scp/{operands}"), None)
    pts.sort()
    if len(pts) < 3:
        return None
    x = np.array([p[0] for p in pts], float); y = np.array([p[1] for p in pts])
    A = np.vstack([np.ones_like(x), x]).T
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    return {"points": [{"hops": p[0], "pj_per_byte": p[1], "se": p[2], "shires": p[3]} for p in pts],
            "intercept_pj_per_byte": float(coef[0]), "slope_pj_per_byte_per_hop": float(coef[1]),
            "rms_pj_per_byte": float(np.sqrt(np.mean((y - pred) ** 2))), "local_pj_per_byte": local}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    result = {"cards": {}, "bursts": {}}
    # Directories from the same card (a main session and a follow-up) are analysed separately, so each has
    # its own idle brackets, and their bursts are then pooled per card.
    per_host = collections.OrderedDict()
    for d in a.dirs:
        tel, runs = load_dir(d)
        if not runs:
            continue
        host = runs[0]["host"]
        bursts, _ = bursts_of(tel, runs)
        per_host.setdefault(host, []).extend(bursts)
    for host, bursts in per_host.items():
        result["bursts"][host] = bursts
        s = summarise(bursts)
        result["cards"][host] = {"summary": s,
                                 "wire": {o: wire_fit(s, o) for o in ("zeros", "random")},
                                 "sram_leakage": sram_leakage(bursts)}
    cards = list(result["cards"])
    if len(cards) >= 2:
        a2, a3 = result["cards"][cards[0]]["summary"], result["cards"][cards[1]]["summary"]
        ratios = {}
        for k in a2:
            if k in a3:
                v2 = a2[k]["pj_per_byte"] or a2[k]["pj_per_op"]; v3 = a3[k]["pj_per_byte"] or a3[k]["pj_per_op"]
                if v2 and v3 and v2["mean"]:
                    ratios[k] = v3["mean"] / v2["mean"]
        rv = np.array(sorted(ratios.values()))
        result["cross_card"] = {"pair": cards[:2], "ratios": ratios, "median": float(np.median(rv)) if len(rv) else None,
                                "p10": float(np.percentile(rv, 10)) if len(rv) else None,
                                "p90": float(np.percentile(rv, 90)) if len(rv) else None, "n": int(len(rv))}
    json.dump(result, open(a.out, "w"), indent=1)
    for host, c in result["cards"].items():
        s = c["summary"]
        print(f"\n=== {host}: {len(s)} configurations, {sum(v['passes'] for v in s.values())} bursts ===")
        rel = [v["pj_per_op"]["se"] / v["pj_per_op"]["mean"] for v in s.values() if v["pj_per_op"] and v["pj_per_op"]["mean"] > 0 and v["passes"] > 1]
        if rel:
            print(f"  pass-to-pass standard error: median {100*np.median(rel):.1f}%, 90th percentile {100*np.percentile(rel,90):.1f}%")
        for o in ("zeros", "random"):
            wf = c["wire"][o]
            if wf:
                print(f"  wire, {o}: {wf['intercept_pj_per_byte']:.2f} pJ/B + {wf['slope_pj_per_byte_per_hop']:.3f} pJ/B/hop (rms {wf['rms_pj_per_byte']:.2f}); local {wf['local_pj_per_byte']}")
        sl = c["sram_leakage"]["fit"]
        if sl:
            print(f"  SRAM rail: {sl['P_fix_w']:.2f} W + {sl['A_leak_80_w']:.2f} W e^((T-80)/36): {sl['mw_per_mb_at_80']:.1f} mW/MB at 80 C")
    if "cross_card" in result:
        cc = result["cross_card"]
        print(f"\ncross-card {cc['pair']}: median {cc['median']:.3f}, 10-90% {cc['p10']:.3f}-{cc['p90']:.3f}, n={cc['n']}")


if __name__ == "__main__":
    main()
