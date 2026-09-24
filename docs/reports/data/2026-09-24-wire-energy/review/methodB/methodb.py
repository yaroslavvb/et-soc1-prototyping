"""Method B: per-burst energies from launch-level timing and sample medians, the NoC rail by an explicit
first-order filter model; per-hop slopes by Theil-Sen. Writes bursts_b.json and prints the summary."""
import collections
import itertools
import json
import sys

import numpy as np

from load import SETS, load, in_marks, indicator_response, held_times

# calibrated in calib.py (grid search over all bursts of each card, held-value timing)
FILT = {"aifoundry2": (1.06, 0.175), "aifoundry3": (1.02, 0.300)}
BOARD_LAT = {"aifoundry2": 0.14, "aifoundry3": 0.18}      # median first-sample-above-half-step latency
DPDT = {}                                                    # W per C of idle board power, fitted per card below
TAU_SCALE, DELAY_ADD = 1.0, 0.0   # sensitivity: set from the command line in main


def burst_energies(st, host, d):
    T, B, M = load(d)
    t = T["t"]
    tau, delay = FILT[host]
    tau *= TAU_SCALE
    delay += DELAY_ADD
    lat = BOARD_LAT[host]
    marked = in_marks(t, M, 0.2, 0.6)
    # idle power vs die temperature over all pre-burst idle windows: the card's own leakage coefficient
    P, Tm = [], []
    for b in B:
        w = (t >= b["lo"] - 3) & (t < b["lo"]) & ~marked
        if w.sum() >= 5:
            P.append(np.median(T["board"][w])); Tm.append(T["temp"][w].mean())
    k = np.polyfit(Tm, P, 1)[0]
    DPDT[(st, host)] = k
    out, dropped = [], []
    for b in B:
        busy = (t >= b["lo"] + lat) & (t <= b["hi"] + lat)
        idle = (t >= b["lo"] - 3.0) & (t < b["lo"]) & ~marked
        why = None
        if busy.sum() < 15 or idle.sum() < 10:
            why = f"too few samples (busy {busy.sum()}, idle {idle.sum()})"
        elif np.median(T["took"][busy]) > 60:
            why = "service processor starved"
        elif not (T["mhz"][busy | idle] == 600).all():
            why = "clock left 600 MHz"
        if why:
            dropped.append({"cfg": b["cfg"], "pass": b["pass"], "why": why})
            continue
        dP = float(np.median(T["board"][busy]) - np.median(T["board"][idle]))
        dT = float(T["temp"][busy].mean() - T["temp"][idle].mean())
        dev, by = b["dev_s"], b["bytes"]
        duty = dev / (b["hi"] - b["lo"])
        # median power is the power while launches run (gaps are <1% of the samples); energy = dP * device time
        e_board = dP * dev / by * 1e12
        e_board_tc = (dP - k * dT) * dev / by * 1e12
        # NoC rail: y(t) = base + step * lowpass(launch indicator) + fill * lowpass(preceding fill), on held times
        nxt = [a for a, _, _ in M if a > b["hi"]]
        end = min(b["hi"] + 3.8, (nxt[0] - 0.05) if nxt else 1e18)
        w = (t >= b["lo"] - 3.0) & (t <= end)
        ts = held_times(t[w], T["noc"][w]); ys = T["noc"][w]
        pf = [(a, e) for a, e, _ in M if b["lo"] - 12 < e < b["lo"]]
        X = [np.ones_like(ts), indicator_response(ts, b["launches"], tau, delay)]
        if pf:
            X.append(indicator_response(ts, pf, tau, delay))
        X = np.vstack(X).T
        c, *_ = np.linalg.lstsq(X, ys, rcond=None)
        rms = float(np.sqrt(((X @ c - ys) ** 2).mean()))
        # the step is the rail's power while launches run; the fitted response already accounts for the 1 ms gaps
        step = float(c[1])
        e_noc = step * dev / by * 1e12
        hop = b["hop"] or int(round(b["mean_hops"]))
        out.append({"set": st, "host": host, "cfg": b["cfg"], "pass": b["pass"], "hop": hop, "mean_hops": b["mean_hops"],
                    "participants": b["participants"], "bytes": by, "dev_s": dev, "duty": duty,
                    "dP_board_w": dP, "dT_c": dT, "noc_step_w": step, "noc_fit_rms_w": rms,
                    "e_board": e_board, "e_board_tc": e_board_tc, "e_noc": e_noc})
    return out, dropped


def theil_sen(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    sl = [(y[j] - y[i]) / (x[j] - x[i]) for i, j in itertools.combinations(range(len(x)), 2) if x[j] != x[i]]
    s = float(np.median(sl))
    return s, float(np.median(y - s * x))


def main():
    global TAU_SCALE, DELAY_ADD
    TAU_SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    DELAY_ADD = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    allb, drops = [], {}
    for (st, host), d in SETS.items():
        o, dr = burst_energies(st, host, d)
        allb += o
        drops[f"{st}/{host}"] = dr
    json.dump({"bursts": allb, "dropped": drops, "dpdt": {f"{a}/{b}": v for (a, b), v in DPDT.items()},
               "filter": FILT, "tau_scale": TAU_SCALE, "delay_add": DELAY_ADD},
              open(f"bursts_b_{TAU_SCALE}_{DELAY_ADD}.json", "w"), indent=1)
    print("bursts", len(allb), "dropped", {k: len(v) for k, v in drops.items()}, "dP/dT", {f"{a}/{b}": round(v, 3) for (a, b), v in DPDT.items()})
    for k, v in drops.items():
        for x in v:
            print("  drop", k, x)


if __name__ == "__main__":
    main()
