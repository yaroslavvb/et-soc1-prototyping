#!/usr/bin/env python3
"""Reduce run_catalogue.py output to per-configuration energies with their pass-to-pass spread, per card.

    analyze_catalogue.py <dir> [<dir> ...] --out catalogue.json

Per (configuration, pass): burst power over its bracketing idle, corrected for the extra leakage of a burst
that ran warmer than its brackets, divided by the rate. Per configuration: mean, standard deviation and
standard error over passes. Then the derived tables: the instruction catalogue, the cross-card ratios, the
wire cost against hop distance (a straight-line fit), the per-line and per-row costs (differences between
strides), the per-neighbourhood cost, and the SRAM rail's leakage against temperature.

Two records of the meters themselves ride along. Every burst carries the sampler's own latency over its busy
window (sampler_median_ms, sampler_max_ms, from each sample's took_ms): on aifoundry2 the tensor loads from DRAM
and the 1 KB-stride row walks slow the sampler to a median of 23-206 ms per burst (other bursts, aifoundry3's
included, stay at 21-22 ms), and those bursts are kept. And rail_filter measures how the PMIC's rail averages
follow a step: the fall of the minion rail 1 s and 2 s after the board's step-down, and a first-order time
constant, per card.
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
    took = np.array([s.get("took_ms", 0) for s in tel], float)   # the sampler's own latency, as analyze_reruns.py reads it
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
                    # The rail figures are first-order filtered with a time constant of about a second (measured by
                    # rail_filter() below and written to catalogue.json rail_filter; board power steps at once), so the
                    # split of a burst's power across the minion, SRAM and mesh rails is read from its last 0.6 s and
                    # divided by 0.94, the part of the step the filter is taken to have reached there, against an idle
                    # read 3 s or more after the previous burst. The measured fall (rail_filter median_fall) is 0.91-0.92
                    # at 2.6 s and 0.94 at 3.0 s after the board's step, and about 6% of the step remains at 3 s; the
                    # 0.94 is kept as published and the pages state its systematic.
                    "rails_over": {rk: float((v[(t >= hi - 0.6) & (t <= hi)].mean() - v[rail_idle].mean()) / 0.94)
                                   for rk, v in rails.items()},
                    "sram_idle_w": float(rails["sram_w"][rail_idle].mean()), "minion_idle_w": float(rails["minion_w"][rail_idle].mean()),
                    "noc_idle_w": float(rails["noc_w"][rail_idle].mean()), "die_c_before": float(T[rail_idle].mean()),
                    "t_lo": lo, "t_hi": hi,
                    "sampler_median_ms": float(np.median(took[busy])), "sampler_max_ms": float(took[busy].max())})
    return out, (t, w, T, rails), [(b[2], b[3]) for b in bl]


# The rail filter: bursts that put more than 8 W on the minion rail with at least 4 s of idle on each side.
# t0 is the first telemetry sample after the board's last reading above the midpoint of busy and idle (the
# board refreshes at once); the fall at s seconds is (rail(t0) - rail(t0 + s)) / (rail(t0) - idle before the
# burst), on the nearest sample, and the time constant is the least-squares fit of 1 - exp(-s/tau) to the
# median fall over 0.1-3 s.
RF_MIN_MINION_W, RF_MIN_IDLE_S, RF_S = 8.0, 4.0, np.round(np.arange(0.0, 3.001, 0.1), 1)


def rail_fall_curves(bursts, arrays, spans):
    t, w, _, rails = arrays
    m = rails["minion_w"]
    los = np.array([s[0] for s in spans]); his = np.array([s[1] for s in spans])
    curves = []
    for b in bursts:
        lo, hi = b["t_lo"], b["t_hi"]
        if b["rails_over"]["minion_w"] <= RF_MIN_MINION_W:
            continue
        i = int(np.searchsorted(los, lo))
        prev_hi = his[i - 1] if i > 0 else t[0]
        next_lo = los[i + 1] if i + 1 < len(los) else t[-1]
        if lo - prev_hi < RF_MIN_IDLE_S or next_lo - hi < RF_MIN_IDLE_S:
            continue
        mid = 0.5 * (b["p_busy_w"] + b["p_idle_w"])
        above = np.where((t <= hi + 1.0) & (w >= mid))[0]
        if not len(above) or above[-1] + 1 >= len(t):
            continue
        k = above[-1] + 1
        t0, r0, ref = t[k], m[k], b["minion_idle_w"]
        if r0 - ref <= 0:
            continue
        curves.append([float((r0 - m[np.argmin(np.abs(t - (t0 + s)))]) / (r0 - ref)) for s in RF_S])
    return curves


def rail_filter(curves):
    if not curves:
        return None
    c = np.median(np.array(curves), axis=0)
    taus = np.arange(0.5, 2.5001, 0.001)
    err = [float(np.sum((c[1:] - (1 - np.exp(-RF_S[1:] / tau))) ** 2)) for tau in taus]
    i1, i2 = int(np.argmin(np.abs(RF_S - 1.0))), int(np.argmin(np.abs(RF_S - 2.0)))
    return {"frac_1s": float(c[i1]), "frac_2s": float(c[i2]), "tau_s": float(round(taus[int(np.argmin(err))], 3)),
            "n": len(curves), "s": [float(x) for x in RF_S], "median_fall": [round(float(x), 4) for x in c],
            "rule": "minion rail over idle > 8 W, >= 4 s idle each side; fall after the board's step-down, "
                    "relative to the idle before the burst; median over bursts; tau fitted over 0.1-3 s"}


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
                         "all_600mhz": all(b["mhz_busy_all_600"] for b in bs),
                         "sampler_median_ms": stat("sampler_median_ms"), "sampler_max_ms": stat("sampler_max_ms")})
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
    fall = collections.OrderedDict()
    for d in a.dirs:
        tel, runs = load_dir(d)
        if not runs:
            continue
        host = runs[0]["host"]
        bursts, arrays, spans = bursts_of(tel, runs)
        per_host.setdefault(host, []).extend(bursts)
        fall.setdefault(host, []).extend(rail_fall_curves(bursts, arrays, spans))
    for host, bursts in per_host.items():
        result["bursts"][host] = bursts
        s = summarise(bursts)
        result["cards"][host] = {"summary": s,
                                 "wire": {o: wire_fit(s, o) for o in ("zeros", "random")},
                                 "sram_leakage": sram_leakage(bursts)}
    # Confidence bars: for every configuration measured on more than one card and more than once, pool every
    # burst from every card. The bar is the range those bursts span (every rerun on every card fell inside
    # it); the mean is over all of them; each card's own mean and pass-to-pass standard error are kept; and a
    # 95% interval for the pooled mean comes from the within-card scatter with (bursts - cards) degrees of
    # freedom, which is what the reruns alone say before the card-to-card difference is added.
    T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23}
    cards = list(result["cards"])
    combined = {}
    all_cfgs = set()
    for h in cards:
        all_cfgs |= set(result["cards"][h]["summary"])
    for cfg in sorted(all_cfgs):
        per_card, vals, within = {}, [], []
        for h in cards:
            bs = [b for b in result["bursts"][h] if b["cfg"] == cfg]
            if not bs:
                continue
            key = "pj_per_byte" if bs[0]["bytes"] else "pj_per_op"
            v = np.array([b[key] for b in bs if b.get(key) is not None], float)
            if not len(v):
                continue
            per_card[h] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                           "se": float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else 0.0, "n": int(len(v)),
                           "unit": "pJ/B" if key == "pj_per_byte" else "pJ/op"}
            vals += list(v)
            within += list(v - v.mean())
        if not vals:
            continue
        vals = np.array(vals)
        dfree = len(vals) - len(per_card)
        sd_within = float(np.sqrt(np.sum(np.square(within)) / dfree)) if dfree > 0 else 0.0
        combined[cfg] = {"mean": float(vals.mean()), "lo": float(vals.min()), "hi": float(vals.max()), "n": int(len(vals)),
                         "cards": len(per_card), "per_card": per_card, "sd_within": sd_within,
                         "ci95_half": T95.get(dfree, 1.96) * sd_within / math.sqrt(len(vals)) if dfree > 0 else None,
                         "card_diff": (max(c["mean"] for c in per_card.values()) - min(c["mean"] for c in per_card.values()))
                                      if len(per_card) > 1 else 0.0,
                         "unit": next(iter(per_card.values()))["unit"]}
    result["combined"] = combined
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
    result["rail_filter"] = {h: rail_filter(c) for h, c in fall.items()}
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
    for host, rf in result["rail_filter"].items():
        if rf:
            print(f"rail filter, {host}: the minion rail falls {100*rf['frac_1s']:.0f}% in 1 s and {100*rf['frac_2s']:.0f}% in 2 s "
                  f"after the board steps down (tau {rf['tau_s']:.2f} s, n={rf['n']})")
    for host, bursts in result["bursts"].items():
        slow = [b for b in bursts if b["sampler_median_ms"] > 60]
        med = [b["sampler_median_ms"] for b in bursts]
        print(f"sampler, {host}: median {np.median(med):.0f} ms per sample over a burst, up to {max(med):.0f}; "
              f"{len(slow)} of {len(bursts)} bursts over 60 ms (kept)")
    if "cross_card" in result:
        cc = result["cross_card"]
        print(f"\ncross-card {cc['pair']}: median {cc['median']:.3f}, 10-90% {cc['p10']:.3f}-{cc['p90']:.3f}, n={cc['n']}")
    hw = [(c["hi"] - c["lo"]) / 2 / c["mean"] for c in combined.values() if c["mean"] > 0 and c["cards"] > 1]
    if hw:
        print(f"confidence bars (half the range over all reruns on all cards): median {100*np.median(hw):.1f}% of the value, "
              f"90th percentile {100*np.percentile(hw, 90):.1f}%, over {len(hw)} entries")


if __name__ == "__main__":
    main()
