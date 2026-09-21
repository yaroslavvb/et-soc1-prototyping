#!/usr/bin/env python3
"""Analysis of run_horace_strict.sh output: heating per pattern, per FLOP, and the flips -> power -> heat model.

    analyze_horace_strict.py <run-dir> --toggles toggles.json --out horace3.json [--predictions pred.json]

Per run: the 10 Hz temperature and power traces aligned at kernel launch, FLOPs done, power early in the run,
temperature rise. Per pattern: means and spreads, heating per FLOP. Two models:

  power    board W (seconds 1-3 of a run, all runs started at the same temperature) regressed on the RTL
           switching activity of the multiply-add units (rtl-sim/fma_toggle), non-negative coefficients
  thermal  a Foster network fitted to the whole session: T(t) = T0 + sum_k R_k (P * h_k)(t), with
           h_k(t) = exp(-t/tau_k)/tau_k on a fixed grid of time constants, non-negative R_k, P = board power

and their chain: activity -> predicted power -> predicted temperature rise, compared with the measured rise.
"""
import argparse
import gzip
import os
import collections
import itertools
import json
import math

import numpy as np

MINIONS = 1024
MAC_PER_OP = 4096
FLOP_PER_MAC = 2
TAUS = [1.5, 4, 10, 25, 60, 150, 400, 1000]
MULT_BLOCKS = ("csa", "compressor", "wallace", "booth")


def load_jsonl(path):
    out = []
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    for line in (gzip.open(path, "rt") if path.endswith(".gz") else open(path)):
        try:
            out.append(json.loads(line))
        except Exception:
            pass  # the sampler's last line is cut when it is killed
    return out


def nnls(X, y, free=1):
    """Least squares with non-negative coefficients (the first `free` columns unconstrained), by subset search."""
    n = X.shape[1]
    best = None
    for k in range(n - free + 1):
        for sub in itertools.combinations(range(free, n), k):
            cols = list(range(free)) + list(sub)
            c = np.linalg.lstsq(X[:, cols], y, rcond=None)[0]
            if (c[free:] < 0).any():
                continue
            full = np.zeros(n)
            full[cols] = c
            err = float(np.sum((X @ full - y) ** 2))
            if best is None or err < best[0] - 1e-12:
                best = (err, full)
    return best[1]


def processes(runs):
    """Groups runs.jsonl lines into host processes (each starts with its calibration launch, launch -1)."""
    procs = []
    for r in runs:
        if r["launch"] == -1 or not procs:
            procs.append([])
        procs[-1].append(r)
    return procs


def features(tog):
    m = tog["mean"]
    mult = sum(v for k, v in m["by_block"].items() if any(s in k for s in MULT_BLOCKS))
    return {"mult": mult / 1e6, "rest": (m["nets"] - mult) / 1e6, "nets": m["nets"] / 1e6,
            "ffclk": m["ff_clocked"] / 1e6, "fftog": m["ff_toggles"] / 1e6, "bus": m["bus"] / 1e6,
            "valid": m["lane_valid"] / 4096}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--toggles")
    ap.add_argument("--predictions")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tel = load_jsonl(f"{a.run_dir}/telemetry.jsonl")
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    P = np.array([s["board_w"] for s in tel])
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
    Tpmic = np.array([float(s["temp_c"]["pmic"]) for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    mv = np.array([s["die_mv"]["minion"] for s in tel])
    rail = {k: np.array([s["sp"][k + "_w"][0] for s in tel]) for k in ("minion", "sram", "noc")}
    t_origin = t[0]

    grid = np.round(np.arange(-2.0, 10.01, 0.1), 1)
    runs = []
    for proc in processes(load_jsonl(f"{a.run_dir}/runs.jsonl")):
        blk = proc[0].get("block", proc[0].get("round"))
        if blk is None or blk < 0:
            continue
        t0, t1 = proc[0]["t_start_ms"] / 1000.0, proc[-1]["t_end_ms"] / 1000.0
        ops = sum(r["iters"] for r in proc)
        sel = lambda lo, hi: (t >= t0 + lo) & (t <= t0 + hi)
        run_sel = (t >= t0 + 0.3) & (t <= t1)
        i0 = int(np.searchsorted(t, t0))
        curve_T = np.interp(t0 + grid, t, T)  # 10 Hz samples of an integer reading; interp only re-grids
        curve_T = T[np.clip(np.searchsorted(t, t0 + grid, side="right") - 1, 0, len(T) - 1)]
        curve_P = P[np.clip(np.searchsorted(t, t0 + grid, side="right") - 1, 0, len(P) - 1)]
        dur = t1 - t0
        runs.append({
            "values": proc[0]["values"], "block": blk, "t0": t0 - t_origin, "dur": dur, "ops": ops,
            "flops": ops * MAC_PER_OP * FLOP_PER_MAC * MINIONS, "tflops": ops * MAC_PER_OP * FLOP_PER_MAC * MINIONS / dur / 1e12,
            "cycles_per_op": float(np.mean([r["cycles_per_op"] for r in proc[1:]])),
            "start_temp": float(T[i0 - 1]), "pmic_start": float(Tpmic[i0 - 1]),
            "p_before": float(P[sel(-2.0, -0.3)].mean()),
            "p_early": float(P[sel(1.0, 3.0)].mean()), "p_late": float(P[sel(dur - 2.0, dur)].mean()),
            "p_mean": float(P[run_sel].mean()), "energy_j": float(P[run_sel].mean() * dur),
            "rails_late": {k: float(v[sel(dur - 1.0, dur)].mean()) for k, v in rail.items()},
            "mhz_min": int(mhz[run_sel].min()), "mhz_max": int(mhz[run_sel].max()), "mv": float(mv[run_sel].mean()),
            "t_end": float(T[sel(dur - 0.5, dur)].mean()),
            "dT_end": 0.0,  # filled in once the thermal model has placed the start temperature
            "curve_T": [float(x) for x in curve_T], "curve_P": [round(float(x), 2) for x in curve_P],
        })

    # ---- leakage: within-run drift of power against temperature, in runs that heat the die by 3 C or more
    lam = []
    for r in runs:
        cT, cP = np.array(r["curve_T"]), np.array(r["curve_P"])
        g = (grid >= 1.0) & (grid <= r["dur"] - 0.2)
        if cT[g].max() - cT[g].min() >= 3:
            lam.append(float(np.polyfit(cT[g], cP[g], 1)[0]))
    leak = float(np.mean(lam)) if lam else 0.78
    for r in runs:
        cT = np.array(r["curve_T"])
        g = (grid >= 1.0) & (grid <= 3.0)
        r["t_early"] = float(cT[g].mean())
        r["p80"] = r["p_early"] - leak * (r["t_early"] - r["start_temp"])  # power at the start temperature

    starts = {(s.get("block", s.get("round")), s["values"]): s for s in load_jsonl(f"{a.run_dir}/starts.jsonl")}
    for r in runs:
        s = starts.get((r["block"], r["values"]))
        if s:
            r["approach_s"] = s.get("approach_ms", 0) / 1000.0
            r["seed"] = s.get("seed")

    # ---- thermal model: Foster network on the whole session
    dt = float(np.median(np.diff(t)))
    tt = np.arange(t[0], t[-1], 0.1)
    Pu = np.interp(tt, t, P)
    Tu = np.interp(tt, t, T)
    def filt(x, tau, delay):
        k = int(round(delay / 0.1))
        xs = np.concatenate([np.full(k, x[0]), x[:len(x) - k]]) if k else x
        y = np.empty_like(xs)
        al = 1.0 - math.exp(-0.1 / tau)
        acc = xs[:50].mean()
        for i, v in enumerate(xs):
            acc += al * (v - acc)
            y[i] = acc
        return y
    skip = int(180 / 0.1)  # let the slow filters forget their start
    best = None
    for delay in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        cols = [filt(Pu, tau, delay) for tau in TAUS]
        X = np.column_stack([np.ones(len(tt))] + cols)[skip:]
        coef = nnls(X, Tu[skip:])
        rms = float(np.sqrt(np.mean((X @ coef - Tu[skip:]) ** 2)))
        if best is None or rms < best["rms"]:
            best = {"delay": delay, "coef": coef, "rms": rms, "cols": cols}
    coef = best["coef"]
    Tfit = np.column_stack([np.ones(len(tt))] + best["cols"]) @ coef
    thermal_out = {"taus": TAUS, "R": [float(x) for x in coef[1:]], "T0": float(coef[0]), "delay": best["delay"], "rms": best["rms"],
                      "R_total": float(coef[1:].sum()),
                      "trace": [{"t": round(float(x - t[0]), 1), "T": float(y), "fit": round(float(f), 2), "P": round(float(p), 1)}
                                for x, y, f, p in zip(tt[::10], Tu[::10], Tfit[::10], Pu[::10])]}

    launch_model_T = [float(Tfit[int(round(r["t0"] / 0.1))]) for r in runs if int(round(r["t0"] / 0.1)) < len(Tfit)]
    thermal_out["model_T_at_launch"] = {"mean": float(np.mean(launch_model_T)), "sd": float(np.std(launch_model_T))}

    # step response g(t): degrees per watt of extra power, t seconds after the power steps up
    gt = np.array([sum(R * (1 - math.exp(-max(0.0, s - best["delay"]) / tau)) for R, tau in zip(coef[1:], TAUS)) for s in grid])
    thermal_out["step"] = [round(float(x), 5) for x in gt]

    # Runs launch as the reading first drops to the target, while it still flickers between target and target+1.
    # The thermal model's temperature at the launch instants (in the units the integer sensor averages to) is the
    # common start temperature; rises are measured from it.
    t_launch = thermal_out["model_T_at_launch"]["mean"]
    thermal_out["start_offset"] = t_launch - float(a_target) if (a_target := min(r["start_temp"] for r in runs)) else 0.0
    for r in runs:
        r["dT_end"] = r["t_end"] - t_launch

    # ---- per pattern
    pats = collections.OrderedDict()
    for v in sorted({r["values"] for r in runs}, key=lambda v: np.mean([r["p_early"] for r in runs if r["values"] == v])):
        rs = [r for r in runs if r["values"] == v]
        cT = np.array([r["curve_T"] for r in rs])
        rise = cT - t_launch
        mean_rise = rise.mean(axis=0)
        g = (grid >= 0.5) & (grid <= 3.5)
        slope = float(np.polyfit(grid[g], mean_rise[g], 1)[0])
        slopes = [float(np.polyfit(grid[g], x[g], 1)[0]) for x in rise]
        at = lambda sec: float(mean_rise[int(np.argmin(np.abs(grid - sec)))])
        flops = float(np.mean([r["flops"] for r in rs]))
        dur = float(np.mean([r["dur"] for r in rs]))
        pats[v] = {
            "n": len(rs), "p_early": float(np.mean([r["p_early"] for r in rs])), "p_early_sd": float(np.std([r["p_early"] for r in rs])),
            "p_late": float(np.mean([r["p_late"] for r in rs])), "p_mean": float(np.mean([r["p_mean"] for r in rs])),
            "p_before": float(np.mean([r["p_before"] for r in rs])),
            "p80": float(np.mean([r["p80"] for r in rs])), "p80_sd": float(np.std([r["p80"] for r in rs])),
            "rails_late": {k: float(np.mean([r["rails_late"][k] for r in rs])) for k in ("minion", "sram", "noc")},
            "tflops": float(np.mean([r["tflops"] for r in rs])), "dur": dur, "flops": flops,
            "rise_3s": at(3.0), "rise_6s": at(6.0), "rise_end": float(np.mean([r["dT_end"] for r in rs])),
            "rise_end_sd": float(np.std([r["dT_end"] for r in rs])),
            "slope": slope, "slope_sd": float(np.std(slopes)),
            "mC_per_tflop": 1000.0 * float(np.mean([r["dT_end"] for r in rs])) / (flops / 1e12),
            "onset_mC_per_tflop": 1000.0 * slope / float(np.mean([r["tflops"] for r in rs])),
            "pj_per_flop": float(np.mean([r["p_mean"] for r in rs])) / float(np.mean([r["tflops"] for r in rs])),
            "pj_per_flop_over_idle": (float(np.mean([r["p_mean"] for r in rs])) - float(np.mean([r["p_before"] for r in rs])))
                                     / float(np.mean([r["tflops"] for r in rs])),
            "start_temp": float(np.mean([r["start_temp"] for r in rs])),
            "mhz": [int(min(r["mhz_min"] for r in rs)), int(max(r["mhz_max"] for r in rs))],
            "mv": float(np.mean([r["mv"] for r in rs])),
            "mean_rise": [round(float(x), 3) for x in mean_rise], "mean_power": [round(float(x), 2) for x in np.array([r["curve_P"] for r in rs]).mean(axis=0)],
        }

    out = {"grid": [float(x) for x in grid], "runs": runs, "patterns": pats, "leak_w_per_c": leak, "thermal": thermal_out,
           "session": {"minutes": float((t[-1] - t[0]) / 60), "runs": len(runs)}}

    # ---- heating power inferred from the temperature trace alone
    # The sensor reads whole degrees, so a run's rise is only known to about half a degree. The time at which each
    # degree is crossed is known much better. So for every run, fit one number A: the extra power (W over the
    # pre-launch level) which, put through the thermal network from the launch state and rounded like the sensor,
    # best reproduces the run's readings. A uses no power measurement from the run itself; comparing it with the
    # measured electrical power and with the power predicted from RTL activity is the test of "heat follows flips".
    R, T0c = coef[1:], coef[0]
    alphas = [1.0 - math.exp(-0.1 / tau) for tau in TAUS]
    kd = int(round(best["delay"] / 0.1))

    def simulate(i0, n_steps, power):
        x = [c[i0] for c in best["cols"]]
        outc = []
        for n in range(n_steps):
            pin = Pu[i0 + n - kd] if n < kd else power
            x = [xk + al * (pin - xk) for xk, al in zip(x, alphas)]
            outc.append(T0c + sum(Rk * xk for Rk, xk in zip(R, x)))
        return np.array(outc)

    def box(y, half=5):
        pad = np.concatenate([np.full(half, y[0]), y, np.full(half, y[-1])])
        return np.convolve(pad, np.ones(2 * half + 1) / (2 * half + 1), mode="valid")

    a_grid = np.arange(-6.0, 45.01, 0.1)
    for r in runs:
        i0 = int(round(r["t0"] / 0.1))
        n_steps = int(r["dur"] / 0.1)
        if i0 + n_steps >= len(tt):
            continue
        base = simulate(i0, n_steps, r["p_before"])
        g = simulate(i0, n_steps, r["p_before"] + 1.0) - base
        read = box(Tu[i0 + 1:i0 + 1 + n_steps])
        cost = np.array([float(np.sum((box(np.round(base + A * g)) - read) ** 2)) for A in a_grid])
        A = float(a_grid[cost <= cost.min() + 1e-9].mean())  # a flat run fits a whole interval of A: take its middle
        r["a_thermal"] = A
        r["a_electrical"] = r["p_mean"] - r["p_before"]
        r["rise_fit"] = float((base + A * g)[-1] - base[0])      # de-quantised rise at the end of the run
        r["rise_base"] = float(base[-1] - base[0])                # what the die would have done with no kernel
        r["g_end"] = float(g[-1])
        r["curve_fit"] = [round(float(x), 3) for x in (base + A * g)]  # de-quantised temperature, 0.1 s steps from launch
        # power at the launch temperature: seconds 1-3, less the leakage the run's own heating has added by then
        r["t_early"] = float((base + A * g)[10:30].mean())
        r["p80"] = r["p_early"] - leak * (r["t_early"] - t_launch)
    for v, pinfo in pats.items():
        rs = [r for r in runs if r["values"] == v and "a_thermal" in r]
        if not rs:
            continue
        pinfo["p80"] = float(np.mean([r["p80"] for r in rs]))
        pinfo["p80_sd"] = float(np.std([r["p80"] for r in rs]))
        pinfo["a_thermal"] = float(np.mean([r["a_thermal"] for r in rs]))
        pinfo["a_thermal_sd"] = float(np.std([r["a_thermal"] for r in rs]))
        pinfo["a_electrical"] = float(np.mean([r["a_electrical"] for r in rs]))
        pinfo["rise_fit"] = float(np.mean([r["rise_fit"] for r in rs]))
        pinfo["rise_fit_sd"] = float(np.std([r["rise_fit"] for r in rs]))
        pinfo["mC_per_tflop_fit"] = 1000.0 * pinfo["rise_fit"] / (pinfo["flops"] / 1e12)
    ae = np.array([[p["a_electrical"], p["a_thermal"]] for p in pats.values() if "a_thermal" in p])
    if len(ae) >= 3:
        k = float(np.sum(ae[:, 0] * ae[:, 1]) / np.sum(ae[:, 0] ** 2))
        out["thermal"]["inferred_vs_electrical"] = {"slope": k, "rms": float(np.sqrt(np.mean((ae[:, 1] - ae[:, 0]) ** 2)))}

    # ---- power model on RTL activity
    if a.toggles:
        tog = json.load(open(a.toggles))
        rows = [dict(features(tog[v]), values=v, y=p["p80"], n=p["n"]) for v, p in pats.items() if v in tog]
        y = np.array([r["y"] for r in rows])
        models = {}
        for names in (["ffclk", "nets"], ["ffclk", "mult", "rest"], ["ffclk", "mult", "rest", "bus"]):
            X = np.column_stack([np.ones(len(rows))] + [np.array([r[c] for r in rows]) for c in names])
            c = nnls(X, y)
            pred = X @ c
            # leave-one-out
            loo = []
            for i in range(len(rows)):
                keep = [j for j in range(len(rows)) if j != i]
                ci = nnls(X[keep], y[keep])
                loo.append(float(X[i] @ ci))
            models["+".join(names)] = {"names": names, "coef": [float(x) for x in c],
                                       "rms": float(np.sqrt(np.mean((pred - y) ** 2))),
                                       "loo_rms": float(np.sqrt(np.mean((np.array(loo) - y) ** 2))),
                                       "pred": {r["values"]: float(p) for r, p in zip(rows, pred)},
                                       "loo": {r["values"]: float(p) for r, p in zip(rows, loo)}}
        out["power_model"] = {"rows": rows, "models": models}
        if a.predictions:
            out["power_model"]["before"] = json.load(open(a.predictions))

    # ---- the chain: switching activity -> power -> temperature rise, per pattern
    # For each run the thermal network starts from the state the measured power history left it in; from launch
    # on, the measured power is replaced by the activity model's power for that pattern (leave-one-out, so a
    # pattern's own measurement never feeds its prediction) plus leakage growing with the simulated rise.
    if "power_model" in out:
        primary = min(out["power_model"]["models"].values(), key=lambda m: m["loo_rms"])
        out["power_model"]["primary"] = "+".join(primary["names"])
        chain = {}
        for v, pinfo in pats.items():
            if v not in primary["loo"]:
                continue
            sims, therm, pins = [], [], []
            for r in [r for r in runs if r["values"] == v]:
                i0 = int(round(r["t0"] / 0.1))
                n_steps = int(r["dur"] / 0.1)
                if i0 + n_steps >= len(tt):
                    continue
                x = [c[i0] for c in best["cols"]]
                base = T0c + sum(Rk * xk for Rk, xk in zip(R, x))
                cur, sim, pin_sum = base, [], 0.0
                for n in range(n_steps):
                    pin = Pu[i0 + n - kd] if n < kd else primary["loo"][v] + leak * (cur - base)
                    pin_sum += primary["loo"][v] + leak * (cur - base)
                    x = [xk + al * (pin - xk) for xk, al in zip(x, alphas)]
                    cur = T0c + sum(Rk * xk for Rk, xk in zip(R, x))
                    sim.append(cur - base)
                sims.append(sim)
                pins.append(pin_sum / n_steps - r["p_before"])
                therm.append(list(Tfit[i0:i0 + n_steps] - Tfit[i0]))
            if not sims:
                continue
            n_min = min(len(x) for x in sims)
            sim_mean = np.mean([x[:n_min] for x in sims], axis=0)
            th_mean = np.mean([x[:n_min] for x in therm], axis=0)
            meas = np.array(pinfo["mean_rise"])[(grid >= 0.0)][:n_min]
            chain[v] = {"p_pred": primary["loo"][v], "p_meas": pinfo["p80"], "a_flips": float(np.mean(pins)),
                        "a_thermal": pinfo.get("a_thermal"), "a_electrical": pinfo.get("a_electrical"), "rise_fit": pinfo.get("rise_fit"),
                        "rise_pred": float(sim_mean[-5:].mean()), "rise_thermal": float(th_mean[-5:].mean()), "rise_meas": float(meas[-5:].mean()),
                        "curve_pred": [round(float(x), 3) for x in sim_mean], "curve_thermal": [round(float(x), 3) for x in th_mean]}
        out["chain"] = chain
        e = np.array([c["rise_pred"] - c["rise_meas"] for c in chain.values()])
        e2 = np.array([c["rise_thermal"] - c["rise_meas"] for c in chain.values()])
        out["chain_rms"] = {"flips_to_rise": float(np.sqrt(np.mean(e ** 2))), "power_to_rise": float(np.sqrt(np.mean(e2 ** 2)))}


    json.dump(out, open(a.out, "w"))
    print(f"{len(runs)} runs, {len(pats)} patterns, thermal rms {out['thermal']['rms']:.2f} C, delay {best['delay']} s, R {np.round(coef[1:], 4)}")
    print(f"{'pattern':16s} n   W(1-3s)  sd    rise_end  slope C/s   TFLOPS  mhz")
    for v, p in pats.items():
        print(f"{v:16s} {p['n']}  {p['p_early']:7.2f} {p['p_early_sd']:5.2f}  {p['rise_end']:6.2f}   {p['slope']:6.3f}     {p['tflops']:6.2f}  {p['mhz']}")
    if "power_model" in out:
        for k, m in out["power_model"]["models"].items():
            print(k, "coef", np.round(m["coef"], 3), "rms", round(m["rms"], 2), "loo", round(m["loo_rms"], 2))
        print("model temperature at launch", out["thermal"]["model_T_at_launch"])
        print("primary", out["power_model"]["primary"], "leak", round(leak, 3), "W/C; chain rms", out["chain_rms"])
        print("inferred vs electrical", out["thermal"].get("inferred_vs_electrical"))
        for v, c in out["chain"].items():
            print(f"  {v:16s} P pred {c['p_pred']:6.2f} meas {c['p_meas']:6.2f} | W over idle: flips {c['a_flips']:5.1f} electrical {c['a_electrical']:5.1f} "
                  f"thermal {c['a_thermal']:5.1f} | rise pred {c['rise_pred']:5.2f} fit {c['rise_fit']:5.2f} raw {c['rise_meas']:5.2f}")


if __name__ == "__main__":
    main()
