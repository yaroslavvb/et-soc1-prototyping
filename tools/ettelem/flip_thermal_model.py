#!/usr/bin/env python3
"""A model that ties die temperature to switching activity ("transistor flips"), fitted to a telemetry session.

    flip_thermal_model.py <run-dir> [<run-dir> ...] --toggles toggles.json --out model.json

The chain, all in one closed loop:

  flips    F_j(t) = N_j(pattern) * ops/s * active minions, for four classes of event counted in the RTL
           simulation of the multiply-add units (rtl-sim/fma_toggle): register bits clocked, net toggles in the
           multiplier tree, net toggles in the rest of the unit, operand-word toggles outside the unit
  power    P(t) = P_fix + A * exp((T(t) - 80) / T_L) + p_sm * active + sum_j e_j * F_j(t)
           (fixed part, leakage growing exponentially with die temperature, the tensor state machines of the
           active minions, and an energy per flip of each class)
  heat     T(t) = T_amb + sum_k x_k(t),   tau_k * dx_k/dt = R_k * P(t) - x_k      (a Foster thermal network)

Fitting is in two open-loop steps, each a non-negative least squares: the network from measured power to the
sensor reading, then the power terms from the known flip schedule and the network's (continuous) temperature.
The closed loop is then simulated from the flip schedule alone, with no measurement of the session inside
it except the state at the first sample, and compared with the sensor.
"""
import argparse
import gzip
import json
import math
import os

import numpy as np

F_OP = 600e6 / 546.0          # TensorFMA ops per second on one minion at 600 MHz
TAUS = [1.5, 4, 10, 25, 60, 150, 400, 1000, 2500]
CLASSES = ["ffclk", "mult", "rest", "bus"]
MULT_BLOCKS = ("csa", "compressor", "wallace", "booth")
DT = 0.1


def norm_values(v):
    """'file:/path/kind.seed.bin' (custom tiles) -> 'kind'."""
    return os.path.basename(v[5:]).split(".")[0] if isinstance(v, str) and v.startswith("file:") else v


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    out = []
    for line in (gzip.open(path, "rt") if path.endswith(".gz") else open(path)):
        try:
            rec = json.loads(line)
            if "values" in rec:
                rec["values"] = norm_values(rec["values"])
            out.append(rec)
        except Exception:
            pass
    return out


def nnls(X, y, free=1, iters=200):
    """Lawson-Hanson non-negative least squares; the first `free` columns are unconstrained."""
    n = X.shape[1]
    G, h = X.T @ X, X.T @ y
    passive = list(range(free))
    coef = np.zeros(n)

    def solve(cols):
        c = np.zeros(n)
        c[cols] = np.linalg.lstsq(G[np.ix_(cols, cols)], h[cols], rcond=None)[0]
        return c

    coef = solve(passive)
    for _ in range(iters):
        w = h - G @ coef
        cand = [j for j in range(free, n) if j not in passive and w[j] > 1e-9]
        if not cand:
            break
        passive.append(max(cand, key=lambda j: w[j]))
        while True:
            c = solve(passive)
            neg = [j for j in passive if j >= free and c[j] <= 0]
            if not neg:
                coef = c
                break
            alpha = min(coef[j] / (coef[j] - c[j]) for j in neg if coef[j] - c[j] > 0) if any(coef[j] - c[j] > 0 for j in neg) else 0.0
            coef = coef + alpha * (c - coef)
            passive = [j for j in passive if j < free or coef[j] > 1e-12]
    return coef


def features(tog):
    m = tog["mean"]
    mult = sum(v for k, v in m["by_block"].items() if any(s in k for s in MULT_BLOCKS))
    return {"ffclk": m["ff_clocked"], "mult": mult, "rest": m["nets"] - mult, "bus": m["bus"]}


def lowpass(x, tau, x0=None):
    y = np.empty_like(x)
    al = 1.0 - math.exp(-DT / tau)
    acc = x[:50].mean() if x0 is None else x0
    for i, v in enumerate(x):
        acc += al * (v - acc)
        y[i] = acc
    return y


def load_session(run_dir, tog):
    until = None
    if "@" in run_dir:   # <dir>@<seconds>: use only the first <seconds> of the session
        run_dir, until = run_dir.rsplit("@", 1)
        until = float(until)
    tel = load_jsonl(f"{run_dir}/telemetry.jsonl")
    if until is not None:
        tel = [s for s in tel if s["t_ms"] / 1000.0 <= tel[0]["t_ms"] / 1000.0 + until]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    tt = np.arange(t[0], t[-1], DT)
    P = np.interp(tt, t, np.array([s["board_w"] for s in tel]))
    idx = np.clip(np.searchsorted(t, tt, side="right") - 1, 0, len(t) - 1)
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])[idx]
    mhz = np.array([s["mhz"]["minion"] for s in tel])[idx]
    act = np.zeros(len(tt))                      # active minions
    F = np.zeros((len(CLASSES), len(tt)))        # events per op per minion of the running pattern
    known = np.ones(len(tt), bool)
    blocks = {}
    for r in load_jsonl(f"{run_dir}/runs.jsonl"):
        b = r.get("block", r.get("round", -1))
        if b is not None and b >= 0 and "values" in r:
            key = (b, r["values"])
            blk = blocks.setdefault(key, {"t0": r["t_start_ms"] / 1000.0, "values": r["values"], "minions": r["minions"]})
            blk["t1"] = r["t_end_ms"] / 1000.0
        i0, i1 = np.searchsorted(tt, [r["t_start_ms"] / 1000.0, r["t_end_ms"] / 1000.0])
        act[i0:i1] = r["minions"]
        if r["values"] in tog:
            f = features(tog[r["values"]])
            for j, c in enumerate(CLASSES):
                F[j, i0:i1] = f[c]
        else:
            known[i0:i1] = False
    return {"dir": run_dir, "t": tt, "P": P, "T": T, "mhz": mhz, "act": act, "F": F, "known": known,
            "blocks": sorted(blocks.values(), key=lambda b: b["t0"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", nargs="+")
    ap.add_argument("--toggles", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip", type=float, default=180.0, help="seconds at the start of each session left out of the fits")
    ap.add_argument("--evaluate", help="a model.json from an earlier fit: keep its network, leakage and flip energies, and only test them on these sessions")
    ap.add_argument("--anchor", help="T:P of a known long idle equilibrium under the first session's ambient, e.g. 62:26.7")
    ap.add_argument("--anchor-weight", type=float, default=36000.0, help="how many 10 Hz samples the anchor counts for")
    ap.add_argument("--leak-only", nargs="*", default=[], help="extra sessions used only for the idle power against temperature fit")
    a = ap.parse_args()
    tog = json.load(open(a.toggles))
    sessions = [load_session(d, tog) for d in a.run_dirs]

    # ---- 1. thermal network, open loop: measured power -> reading
    # One intercept per session: whatever is slower than a session (the chassis, the room) is a constant within it.
    # The slow stages also start each session in an unknown state, which decays as exp(-t/tau): one free
    # coefficient per session and slow stage.
    ns = len(sessions)
    slow = [k for k, tau in enumerate(TAUS) if tau >= 60]
    Xs, ys = [], []
    for si, s in enumerate(sessions):
        s["lp"] = [lowpass(s["P"], tau, x0=float(s["P"][0])) for tau in TAUS]
        k = int(a.skip / DT)
        n = len(s["t"])
        free_cols = []
        for sj in range(ns):
            free_cols.append(np.full(n, 1.0 if sj == si else 0.0))
            for kk in slow:
                free_cols.append(np.exp(-(s["t"] - s["t"][0]) / TAUS[kk]) if sj == si else np.zeros(n))
        s["free_cols"] = free_cols
        Xs.append(np.column_stack(free_cols + s["lp"])[k:])
        ys.append(s["T"][k:])
    X, y = np.vstack(Xs), np.concatenate(ys)
    nfree = ns * (1 + len(slow))
    if a.anchor:   # hours at constant idle power: every stage has settled, so T = T_amb + P * sum(R)
        Ta, Pa = [float(v) for v in a.anchor.split(":")]
        row = np.zeros(X.shape[1]); row[0] = 1.0; row[nfree:] = Pa
        w = math.sqrt(a.anchor_weight)
        X, y = np.vstack([X, w * row]), np.concatenate([y, [w * Ta]])
    if a.evaluate:
        fixed = json.load(open(a.evaluate))
        assert fixed["taus"] == TAUS
        R = np.array(fixed["R"])
        th_free = np.linalg.lstsq(X[:, :nfree], y - X[:, nfree:] @ R, rcond=None)[0]   # per session: intercept and starting state only
        th = np.concatenate([th_free, R])
    else:
        th = nnls(X, y, free=nfree)
    R = th[nfree:]
    for si, s in enumerate(sessions):
        s["T_amb"] = float(th[si * (1 + len(slow))])
        s["init"] = th[si * (1 + len(slow)) + 1:(si + 1) * (1 + len(slow))]
        s["T_fit"] = np.column_stack(s["free_cols"]) @ th[:nfree] + np.column_stack(s["lp"]) @ R
    nobs = len(y) - (1 if a.anchor else 0)
    th_rms = float(np.sqrt(np.mean((X[:nobs] @ th - y[:nobs]) ** 2)))
    T_amb = float(th[0])

    # ---- 2. power terms, open loop
    # 2a. leakage from idle samples only (no launch within 3 s before or 6 s after, 600 MHz), all sessions, against
    #     the reading smoothed over 3 s:   P_idle = P_fix + A * exp((T - 80) / T_L)
    def smooth(x, half=15):
        pad = np.concatenate([np.full(half, x[0]), x, np.full(half, x[-1])])
        return np.convolve(pad, np.ones(2 * half + 1) / (2 * half + 1), mode="valid")
    idle_T, idle_P = [], []
    for s in sessions + [load_session(d, tog) for d in a.leak_only]:
        busy = np.convolve((s["act"] > 0).astype(float), np.ones(91), mode="same") > 0   # +-4.5 s around any launch
        ok = ~busy & (s["mhz"] == 600)
        ok[:int(20 / DT)] = False
        idle_T.append(smooth(s["T"])[ok]); idle_P.append(s["P"][ok])
    idle_T, idle_P = np.concatenate(idle_T), np.concatenate(idle_P)
    best = None
    for T_L in [16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 45, 50, 60, 80]:
        Xl = np.column_stack([np.ones(len(idle_T)), np.exp((idle_T - 80.0) / T_L)])
        cl = nnls(Xl, idle_P, free=1)
        rms = float(np.sqrt(np.mean((Xl @ cl - idle_P) ** 2)))
        if best is None or rms < best["rms_idle"]:
            best = {"T_L": float(T_L), "P_fix": float(cl[0]), "A": float(cl[1]), "rms_idle": rms}
    if a.evaluate:
        fp = fixed["power"]
        best.update({"T_L": fp["T_L"], "P_fix": fp["P_fix"], "A": fp["A_leak_at_80"]})
    P_fix, A_leak = best["P_fix"], best["A"]
    bins = {}
    for Tv, Pv in zip(np.round(idle_T), idle_P):
        bins.setdefault(int(Tv), []).append(Pv)
    idle_curve = [{"T": k, "P": float(np.mean(v)), "n": len(v)} for k, v in sorted(bins.items()) if len(v) >= 30]
    # 2b. switching terms from busy samples, leakage fixed: events per second, chip-wide, in units of 1e15
    Xp, yp = [], []
    for s in sessions:
        k = int(a.skip / DT)
        ok = s["known"].copy(); ok[:k] = False
        ok &= (s["mhz"] == 600) & (s["act"] > 0)
        edge = np.abs(np.diff(s["act"], prepend=s["act"][0])) > 0          # launches starting or ending:
        ok &= ~(np.convolve(edge.astype(float), np.ones(7), mode="same") > 0)  # drop 0.3 s either side
        rate = s["F"] * s["act"] * F_OP / 1e15
        Ts = smooth(s["T"])
        cols = [s["act"] / 1024.0] + [rate[j] for j in range(len(CLASSES))]
        Xp.append(np.column_stack(cols)[ok]); yp.append((s["P"] - P_fix - A_leak * np.exp((Ts - 80.0) / best["T_L"]))[ok])
    Xp, yp = np.vstack(Xp), np.concatenate(yp)
    c = nnls(Xp, yp, free=0)
    if a.evaluate:
        c = np.array([fp["p_sm_full_chip"]] + [fp["e_fJ"][k] for k in CLASSES])
    best["rms"] = float(np.sqrt(np.mean((Xp @ c - yp) ** 2)))
    p_sm, e = float(c[0]), c[1:]

    # ---- 3. closed loop from the flip schedule alone
    alphas = [1.0 - math.exp(-DT / tau) for tau in TAUS]
    closed = []
    for s in sessions:
        n = len(s["t"])
        rate = s["F"] * s["act"] * F_OP / 1e15
        pdyn = p_sm * s["act"] / 1024.0 + e @ rate
        # initial state: what the measured power history had left in each stage at the first kept sample
        k0 = int(a.skip / DT)
        x = np.array([Rk * lp[k0] for Rk, lp in zip(R, s["lp"])])
        for kk, c0 in zip(slow, s["init"]):   # the fitted left-over of each slow stage's unknown starting state
            x[kk] += c0 * math.exp(-(s["t"][k0] - s["t"][0]) / TAUS[kk])
        Tsim, Psim = np.full(n, np.nan), np.full(n, np.nan)
        Tc = s["T_amb"] + x.sum()
        for i in range(k0, n):
            p = P_fix + A_leak * math.exp((min(Tc, 100.0) - 80.0) / best["T_L"]) + pdyn[i]
            x += np.array(alphas) * (R * p - x)
            Tc = s["T_amb"] + x.sum()
            Tsim[i], Psim[i] = Tc, p
        ok = ~np.isnan(Tsim) & s["known"] & (s["mhz"] == 600)
        closed.append({"rms_T": float(np.sqrt(np.mean((Tsim[ok] - s["T"][ok]) ** 2))),
                       "rms_P": float(np.sqrt(np.mean((Psim[ok] - s["P"][ok]) ** 2))),
                       "bias_T": float(np.mean(Tsim[ok] - s["T"][ok]))})
        s["T_sim"], s["P_sim"] = Tsim, Psim

    # ---- 3b. each long run on its own: start the network from the state the measured history left at launch,
    #          then drive it with the flip schedule alone and ask when it reaches the cap
    def stage_state(s, i):
        x = np.array([Rk * lp[i] for Rk, lp in zip(R, s["lp"])])
        for kk, c0 in zip(slow, s["init"]):
            x[kk] += c0 * math.exp(-(s["t"][i] - s["t"][0]) / TAUS[kk])
        return x
    per_run = []
    for s in sessions:
        act = s["act"]
        for blk in s["blocks"]:
            i0, j = np.searchsorted(s["t"], [blk["t0"], blk["t1"]])
            i0 += 2   # two samples into the first launch
            dur = blk["t1"] - blk["t0"]
            if j >= len(s["t"]) - 1:
                continue   # the run lies beyond the part of the session in use
            if dur < 15 or blk["values"] not in tog or s["t"][i0] - s["t"][0] < a.skip:
                continue
            rate = s["F"][:, i0] * act[i0] * F_OP / 1e15
            pdyn_run = p_sm * act[i0] / 1024.0 + float(e @ rate)
            x = stage_state(s, i0)
            T0 = s["T_amb"] + x.sum()
            Tc, t_cap, horizon = T0, None, int(max(dur, 600) / DT)
            T_end_pred = None
            curve = []
            for n in range(horizon):
                pw = P_fix + A_leak * math.exp((Tc - 80.0) / best["T_L"]) + pdyn_run
                x += np.array(alphas) * (R * pw - x)
                Tc = s["T_amb"] + x.sum()
                if n % 10 == 9 and n < int(dur / DT):
                    curve.append(round(float(Tc), 2))     # 1 Hz, while the real run lasted
                if t_cap is None and Tc >= 89.5:
                    t_cap = (n + 1) * DT
                if n == int(dur / DT) - 1:
                    T_end_pred = Tc
                if Tc >= 95.0:       # past the cap the real run has stopped; the model would run away
                    if T_end_pred is None:
                        T_end_pred = Tc
                    break
            T_end_meas = float(s["T"][max(i0, j - 20):j].mean())
            per_run.append({"session": s["dir"], "values": blk["values"], "t0": float(s["t"][i0] - s["t"][0]), "dur": dur, "active": int(act[i0]),
                            "p_dyn_flips": pdyn_run, "T_launch_model": float(T0), "T_end_meas": T_end_meas,
                            "T_end_pred": float(T_end_pred) if T_end_pred is not None else None,
                            "capped": bool(T_end_meas >= 88.5), "t_cap_pred": t_cap, "curve_pred": curve})

    capped = [r for r in per_run if r["capped"] and r["t_cap_pred"]]
    ratios = np.array([r["t_cap_pred"] / r["dur"] for r in capped]) if capped else np.array([1.0])
    uncapped = [r for r in per_run if not r["capped"] and r["T_end_pred"] is not None and r["dur"] > 300]
    per_run_summary = {"n_capped": len(capped), "median_abs_pct": float(np.median(np.abs(ratios - 1.0)) * 100),
                       "worst_pct": float(np.max(np.abs(ratios - 1.0)) * 100),
                       "log_rms": float(np.sqrt(np.mean(np.log(ratios) ** 2))),
                       "n_uncapped": len(uncapped),
                       "end_T_rms_uncapped": float(np.sqrt(np.mean([(r["T_end_pred"] - r["T_end_meas"]) ** 2 for r in uncapped]))) if uncapped else None}

    # ---- step responses, open loop and with leakage feedback (linearised at 80 C)
    lam = A_leak / best["T_L"]
    hor = [1, 3, 10, 30, 60, 120, 300, 600, 1800, 3600]
    def step(feedback, watts=1.0, seconds=3600):
        x = np.zeros(len(TAUS)); out = {}
        for i in range(int(seconds / DT) + 1):
            p = watts + (lam * x.sum() if feedback else 0.0)
            x += np.array(alphas) * (R * p - x)
            tnow = (i + 1) * DT
            for hsec in hor:
                if abs(tnow - hsec) < DT / 2:
                    out[hsec] = float(x.sum() / watts)
        return out
    out = {
        "taus": TAUS, "R": [float(v) for v in R], "T_amb": T_amb, "thermal_rms": th_rms, "R_total": float(R.sum()),
        "power": {"P_fix": P_fix, "A_leak_at_80": A_leak, "T_L": best["T_L"], "lambda_at_80": lam, "p_sm_full_chip": p_sm,
                  "e_fJ": {cname: float(v) for cname, v in zip(CLASSES, e)}, "rms": best["rms"], "rms_idle": best["rms_idle"],
                  "idle_curve": idle_curve},
        "loop_gain_at_80": float(lam * R.sum()),
        "step_open": step(False), "step_closed": step(True),
        "closed_loop": closed, "per_run": per_run, "per_run_summary": per_run_summary,
        "sessions": [{"dir": s["dir"], "T_amb": s["T_amb"], "minutes": float((s["t"][-1] - s["t"][0]) / 60),
                      "trace": [{"t": round(float(tv - s["t"][0]), 1), "T": float(Tv), "sim": (None if np.isnan(sv) else round(float(sv), 2)),
                                 "fit": round(float(fv), 2), "P": round(float(pv), 1), "Psim": (None if np.isnan(qv) else round(float(qv), 1)),
                                 "act": int(av)}
                                for tv, Tv, sv, fv, pv, qv, av in zip(s["t"][::20], s["T"][::20], s["T_sim"][::20], s["T_fit"][::20],
                                                                      s["P"][::20], s["P_sim"][::20], s["act"][::20])]} for s in sessions],
    }
    json.dump(out, open(a.out, "w"))
    print("session intercepts", [round(s["T_amb"], 1) for s in sessions])
    print(f"thermal: T_amb' {T_amb:.1f} C, R {np.round(R, 4)} (sum {R.sum():.3f} C/W), rms {th_rms:.2f} C")
    print(f"power: P_fix {P_fix:.2f} W, leakage {A_leak:.2f} W at 80 C with T_L {best['T_L']:.0f} C (slope {lam:.2f} W/C), state machines {p_sm:.2f} W, "
          f"e (fJ) {dict(zip(CLASSES, np.round(e, 3)))}, rms busy {best['rms']:.2f} W, idle {best['rms_idle']:.2f} W")
    print(f"loop gain at 80 C: {lam * R.sum():.2f}; step response C/W open {out['step_open']} closed {out['step_closed']}")
    for r in per_run:
        print(f"  run at {r['t0']:7.0f} s  {r['values']:14s} {r['active']:4d} minions  flips {r['p_dyn_flips']:5.1f} W  lasted {r['dur']:6.1f} s"
              f"  end T meas {r['T_end_meas']:.1f} pred {r['T_end_pred']:.1f}  cap pred at {r['t_cap_pred']}")
    print("per-run summary", per_run_summary)
    for s, cl in zip(sessions, closed):
        print(f"closed loop from flips alone, {s['dir']}: temperature rms {cl['rms_T']:.2f} C (bias {cl['bias_T']:+.2f}), power rms {cl['rms_P']:.2f} W")


if __name__ == "__main__":
    main()
