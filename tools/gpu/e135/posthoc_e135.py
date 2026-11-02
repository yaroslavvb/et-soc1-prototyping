#!/usr/bin/env python3
"""E135, POST HOC (written after the registration; it adds views, never verdicts).

    python3 posthoc_e135.py <run_dir> [--json posthoc.json] > posthoc.txt

1. The A100's cool-die ladder, E64's table on the GPU: each bf16 kind's sustained power, clock and limit, and the
   clock it keeps against the power it would draw.
2. The first second of every burst: does the power controller let a kind run over the cap before it clamps?
3. Inside the sustained window: the clock against the die temperature for kinds held by the cap (leakage).
4. The exponent the two caps imply, n = ln((L1 - P0) / (L2 - P0)) / ln(f1 / f2), for kinds held at both caps.
5. Energy per multiply-add (2 FLOP), at the board and over idle, beside the ET-SoC-1's.
Standard library only; it reuses reduce_e135.py's loading and windows."""
import argparse
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reduce_e135 as R  # noqa: E402


def linfit(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        return None
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    a = my - b * mx
    res = [c - (a + b * t) for t, c in zip(x, y)]
    se = math.sqrt(sum(r * r for r in res) / (n - 2) / sxx) if n > 2 else None
    return {"slope": b, "intercept": a, "se": se, "n": n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--preds", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions-e135.json"))
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    preds = json.load(open(a.preds))
    names = sorted(d for d in os.listdir(a.run_dir) if os.path.isdir(os.path.join(a.run_dir, d)) and d in ("A", "B"))
    units = {u: R.load_unit(os.path.join(a.run_dir, u)) for u in names}
    cells, protos, lowcaps, gaps, rules = R.score(units, preds)
    out = {"label": "POST HOC"}
    P = print
    P("# E135 post hoc (not registered; no verdict here)")
    idle = {}
    for u, U in units.items():
        i0 = U["idle0"]
        if i0:
            w = R.wstats(U["samples"], i0["t_a"], i0["t_b"])
            idle[u] = w.get("power_w")
    out["idle_w"] = idle
    P(f"idle power: {idle}")

    # 1. the ladder
    P("\n## 1. The A100's cool-die ladder (default cap, 8192^3, sustained window; pass 1)")
    P("| unit | format | kind | sustained W | W / limit | MHz | MHz / max | SW cap share | T/s | burst MHz | early MHz |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    lad = []
    for (u, cap, size, dt, kind, p), c in sorted(cells.items(), key=lambda kv: (kv[0][0], kv[0][3], -((kv[1]["w"].get("sus") or {}).get("power_w") or 0))):
        if cap != "default" or size != 8192 or p != 1:
            continue
        s, b, e = c["w"].get("sus") or {}, c["w"].get("burst") or {}, c["w"].get("early") or {}
        fmax = units[u]["static"].get("max_clock_sm")
        if not s.get("power_w") or not s.get("plim_w"):
            continue
        row = {"unit": u, "dtype": dt, "kind": kind, "w": s["power_w"], "w_over_limit": s["power_w"] / s["plim_w"],
               "mhz": s.get("sm_mean"), "mhz_over_max": (s["sm_mean"] / fmax) if fmax and s.get("sm_mean") else None,
               "sw": (s.get("frac") or {}).get("sw_power"), "tflops": s["tflops"], "burst_mhz": b.get("sm_mean"),
               "early_mhz": e.get("sm_mean")}
        lad.append(row)
        P(f"| {u} | {dt} | {kind} | {row['w']:.1f} | {row['w_over_limit']:.3f} | {row['mhz']:.0f} | "
          f"{(row['mhz_over_max'] or 0):.3f} | {(row['sw'] or 0):.2f} | {row['tflops']:.1f} | "
          f"{(row['burst_mhz'] or 0):.0f} | {(row['early_mhz'] or 0):.0f} |")
    out["ladder"] = lad

    # 2. the first second
    P("\n## 2. The first second of each burst: samples at 0-1 s (t from the first call, SM MHz, W, instant W, reasons)")
    first = {}
    for (u, cap, size, dt, kind, p), c in sorted(cells.items()):
        if size != 8192 or p != 1 or dt != "bf16":
            continue
        t0 = c["rec"]["run"]["t0"]
        S = [r for r in units[u]["samples"] if t0 - 0.2 <= R.tmid(r) < t0 + 1.0]
        rows = [[round(R.tmid(r) - t0, 2), r.get("sm"), r.get("p_mw") and round(r["p_mw"] / 1000, 1),
                 r.get("p_inst_mw") and round(r["p_inst_mw"] / 1000, 1), r.get("rsn")] for r in S]
        first[f"{u}|{cap}|{kind}"] = rows
        P(f"{u} {cap} bf16 {kind}: " + "; ".join(f"{x[0]:+.2f}s {x[1]} MHz {x[2]} W i{x[3]} r{x[4]}" for x in rows))
    out["first_second"] = first

    # 3. clock against die temperature, inside the sustained window, kinds held by the cap
    P("\n## 3. Inside the sustained window: SM MHz against die C for kinds held by the cap (fit over 100 ms samples)")
    drift = []
    for (u, cap, size, dt, kind, p), c in sorted(cells.items()):
        s = c["w"].get("sus") or {}
        if size != 8192 or not s.get("frac") or s["frac"]["sw_power"] < 0.5:
            continue
        t0 = c["rec"]["run"]["t0"]
        lo, hi = R.windows_of(c["rec"]["step"])["sus"]
        S = [r for r in units[u]["samples"] if t0 + lo <= R.tmid(r) < t0 + hi and r.get("sm") and r.get("temp") is not None]
        fit = linfit([r["temp"] for r in S], [r["sm"] for r in S])
        tf = linfit([R.tmid(r) - t0 for r in S], [r["sm"] for r in S])
        d = {"unit": u, "cap": cap, "dtype": dt, "kind": kind, "pass": p, "temp_first": S[0]["temp"] if S else None,
             "temp_last": S[-1]["temp"] if S else None, "mhz_per_c": fit and fit["slope"], "se": fit and fit["se"],
             "mhz_per_s": tf and tf["slope"]}
        drift.append(d)
        P(f"{u} {cap} {dt} {kind} p{p}: die {d['temp_first']}->{d['temp_last']} C, "
          f"{(d['mhz_per_c'] or 0):+.2f} MHz/C (se {(d['se'] or 0):.2f}), {(d['mhz_per_s'] or 0):+.3f} MHz/s")
    out["drift"] = drift

    # 4. the exponent from the two caps
    P("\n## 4. The exponent two caps imply (unit A), n = ln((L1 - P0)/(L2 - P0)) / ln(f1/f2)")
    lc = lowcaps.get("A")
    expo = []
    if lc and lc.get("applied"):
        capl = f"{lc['target_w']:g}W"
        for kind in ("randn", "rand", "twos", "zeros"):
            c1, c2 = cells.get(("A", "default", 8192, "bf16", kind, 1)), cells.get(("A", capl, 8192, "bf16", kind, 1))
            if not c1 or not c2:
                continue
            s1, s2 = c1["w"]["sus"], c2["w"]["sus"]
            for P0 in (idle.get("A"), 88.0, 0.0):
                if P0 is None:
                    continue
                if s1["sm_mean"] > s2["sm_mean"] and s1["power_w"] > s2["power_w"] > P0:
                    n = math.log((s1["power_w"] - P0) / (s2["power_w"] - P0)) / math.log(s1["sm_mean"] / s2["sm_mean"])
                else:
                    n = None
                expo.append({"kind": kind, "P0": P0, "w1": s1["power_w"], "w2": s2["power_w"], "f1": s1["sm_mean"],
                             "f2": s2["sm_mean"], "n": n})
                P(f"{kind}, P0 {P0:.1f} W: {s1['power_w']:.1f} W at {s1['sm_mean']:.0f} MHz, {s2['power_w']:.1f} W at "
                  f"{s2['sm_mean']:.0f} MHz -> n = {n if n is None else round(n, 2)}")
    else:
        P("the lower cap was not applied, so there is no second operating point")
    out["exponent"] = expo

    # 5. energy per multiply-add
    P("\n## 5. Energy per multiply-add (2 FLOP; int8: 2 ops), sustained window, pass 1, default cap")
    P("| unit | format | kind | pJ per MAC, board | pJ per MAC, over idle |")
    P("|---|---|---|---|---|")
    epm = []
    for (u, cap, size, dt, kind, p), c in sorted(cells.items()):
        s = c["w"].get("sus") or {}
        if cap != "default" or size != 8192 or p != 1 or not s.get("power_w"):
            continue
        macs = s["tflops"] * 1e12 / 2.0
        board = s["power_w"] / macs * 1e12
        over = (s["power_w"] - idle[u]) / macs * 1e12 if idle.get(u) else None
        epm.append({"unit": u, "dtype": dt, "kind": kind, "pj_mac_board": board, "pj_mac_over_idle": over})
        P(f"| {u} | {dt} | {kind} | {board:.3f} | {over if over is None else round(over, 3)} |")
    out["pj_per_mac"] = epm

    # 6. the overshoot, from the pre-boost readings: every burst starts loaded at the idle application clock (1095 MHz
    # on these boards) for 0.1-0.3 s before the boost, so each kind's power at that clock is read; the kinds that stay
    # under the cap also read their power at 1410 MHz, which fits the exponent n of P - P_idle ~ f^n; with that n each
    # capped kind's power at 1410 MHz (its demand) and the clock at which it would draw the limit follow.
    P("\n## 6. The overshoot from the pre-boost readings (bf16, fp16, tf32, int8; default cap; pass 1)")
    two = []
    for (u, cap, size, dt, kind, p), c in sorted(cells.items()):
        if cap != "default" or size != 8192 or p != 1:
            continue
        t0 = c["rec"]["run"]["t0"]
        app = units[u]["static"].get("app_clock_sm") or 1095
        S = [r for r in units[u]["samples"] if t0 - 0.05 <= R.tmid(r) < t0 + 0.8]
        # a sample reads the clock first and the instantaneous field about 6 ms later, so a boost between the two reads
        # puts a post-boost watt beside a pre-boost clock. Kept: the power-usage reading (read right after the clock) of
        # a sample at the application clock, and its instantaneous field only if the next sample still reads that clock.
        cand = []
        for i, r in enumerate(S):
            if r.get("sm") is None or r["sm"] > app + 30:
                continue
            if r.get("p_mw") is not None:
                cand.append((r["p_mw"] / 1000.0, r["sm"]))
            nxt = S[i + 1] if i + 1 < len(S) else None
            if r.get("p_inst_mw") is not None and nxt and nxt.get("sm") is not None and nxt["sm"] <= app + 30:
                cand.append((r["p_inst_mw"] / 1000.0, r["sm"]))
        cand = [x for x in cand if x[0] > (idle.get(u) or 60) + 60]
        s = c["w"].get("sus") or {}
        e = R.wstats(units[u]["samples"], t0 + 0.6, t0 + 1.6)
        if not cand or not s:
            continue
        p_app, f_app = max(cand)
        two.append({"unit": u, "dtype": dt, "kind": kind, "f_app": f_app, "p_app": p_app, "n_pre": len(cand),
                    "f_early": e.get("sm_mean"), "p_early": e.get("power_w"), "sw_early": (e.get("frac") or {}).get("sw_power"),
                    "f_sus": s.get("sm_mean"), "p_sus": s.get("power_w"), "sw_sus": (s.get("frac") or {}).get("sw_power"),
                    "limit": s.get("plim_w")})
    # the exponent from kinds under the cap at 1410 MHz in the early window
    ns = []
    for d in two:
        P0 = idle.get(d["unit"])
        if P0 and d["sw_early"] is not None and d["sw_early"] <= 0.1 and d["f_early"] and d["f_early"] >= 1400 and d["p_app"] > P0:
            n = math.log((d["p_early"] - P0) / (d["p_app"] - P0)) / math.log(d["f_early"] / d["f_app"])
            d["n_fit"] = n
            ns.append(n)
    n_med = statistics.median(ns) if ns else None
    out["exponent_from_uncapped"] = {"values": ns, "median": n_med}
    P(f"exponent n from the kinds under the cap (P_early - P_idle)/(P_app - P_idle) = (f_early/f_app)^n: "
      f"{[round(x, 2) for x in ns]}, median {n_med if n_med is None else round(n_med, 2)}")
    P("| unit | format | kind | MHz, W before the boost | early MHz, W | sustained MHz, W, SW share | demand at 1410 MHz (n med) | "
      "clock that draws the limit (n med) | measured early / sustained MHz |")
    P("|---|---|---|---|---|---|---|---|---|")
    for d in two:
        P0 = idle.get(d["unit"])
        dem = f_lim = None
        if n_med and P0 and d["p_app"] > P0 and d["limit"]:
            dem = P0 + (d["p_app"] - P0) * (1410.0 / d["f_app"]) ** n_med
            f_lim = d["f_app"] * ((d["limit"] - P0) / (d["p_app"] - P0)) ** (1.0 / n_med)
            f_lim = min(f_lim, 1410.0)
        d["demand_1410_w"], d["clock_at_limit"] = dem, f_lim
        P(f"| {d['unit']} | {d['dtype']} | {d['kind']} | {d['f_app']}, {d['p_app']:.1f} | {(d['f_early'] or 0):.0f}, "
          f"{(d['p_early'] or 0):.1f} | {(d['f_sus'] or 0):.0f}, {(d['p_sus'] or 0):.1f}, {(d['sw_sus'] or 0):.2f} | "
          f"{'—' if dem is None else f'{dem:.0f}'} | {'—' if f_lim is None else f'{f_lim:.0f}'} | "
          f"{(d['f_early'] or 0):.0f} / {(d['f_sus'] or 0):.0f} |")
    out["overshoot"] = two

    # 7. what the same relation predicts at Horace's 330 W (the lower cap could not be set: nvidia-smi -pl rc 4), beside
    # its own error at the 400 W the units ran: per format, the random kind's clock where P_idle + (P_app - P_idle)
    # (f / f_app)^n reaches the limit, against zeros' (1410 MHz where its demand stays under), so the gap is the
    # clock ratio, as R2 found the rate to follow the clock.
    P("\n## 7. The relation of section 6 at a 330 W limit (Horace's), against its own error at 400 W")
    pred = []
    for d in two:
        if d["kind"] != R.RANDOM_OF[d["dtype"]]:
            continue
        P0 = idle.get(d["unit"])
        z = next((x for x in two if x["unit"] == d["unit"] and x["dtype"] == d["dtype"] and x["kind"] == "zeros"), None)
        if not (n_med and P0 and z and z.get("demand_1410_w")):
            continue
        row = {"unit": d["unit"], "dtype": d["dtype"], "random": d["kind"]}
        for L in (400.0, 330.0):
            fr = min(1410.0, d["f_app"] * ((L - P0) / (d["p_app"] - P0)) ** (1.0 / n_med))
            fz = 1410.0 if z["demand_1410_w"] <= L else min(1410.0, z["f_app"] * ((L - P0) / (z["p_app"] - P0)) ** (1.0 / n_med))
            row[f"gap_{L:g}"] = fz / fr
        g = [x for x in gaps if x["unit"] == d["unit"] and x["dtype"] == d["dtype"] and x["window"] == "sus"
             and x["cap"] == "default" and x["size"] == 8192 and x["pass"] == 1]
        row["measured_400"] = g[0]["gap_rate"] if g else None
        row["model_error_400"] = (row["gap_400"] - row["measured_400"]) if row["measured_400"] else None
        row["gap_330_less_error"] = (row["gap_330"] - row["model_error_400"]) if row["model_error_400"] is not None else None
        pred.append(row)
        P(f"{d['unit']} {d['dtype']} {d['kind']}: at 400 W predicted {row['gap_400']:.3f}, measured "
          f"{(row['measured_400'] or 0):.3f} (error {(row['model_error_400'] or 0):+.3f}); at 330 W predicted {row['gap_330']:.3f}, "
          f"less the 400 W error {(row['gap_330_less_error'] or 0):.3f}")
    out["at_330"] = pred
    if a.json:
        with open(a.json, "w") as f:
            json.dump(out, f, indent=1, default=str)


if __name__ == "__main__":
    main()
