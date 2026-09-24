"""Calibrate the meters: board-power latency, and the NoC rail filter's time constant and delay (grid search)."""
import sys
import numpy as np
from load import SETS, load, in_marks, indicator_response, held_times

for key, d in SETS.items():
    T, B, M = load(d)
    t = T["t"]
    # ---- board latency: first sample at > half the step after lo, last sample > half after hi
    on_lat, off_lat = [], []
    for b in B:
        idle = np.median(T["board"][(t >= b["lo"] - 3) & (t < b["lo"])])
        mid = np.median(T["board"][(t >= b["lo"] + 1) & (t <= b["hi"] - 0.5)])
        if mid - idle < 3:
            continue
        thr = idle + 0.5 * (mid - idle)
        w = (t >= b["lo"] - 0.5) & (t <= b["lo"] + 1.5)
        ts, vs = t[w], T["board"][w]
        k = np.argmax(vs > thr)
        on_lat.append(ts[k] - b["lo"])
        w = (t >= b["hi"] - 0.5) & (t <= b["hi"] + 1.5)
        ts, vs = t[w], T["board"][w]
        k = np.argmax(vs < thr)
        off_lat.append(ts[k] - b["hi"])
    print(key, "board: first sample above half-step at lo +", np.percentile(on_lat, [10, 50, 90]).round(3),
          " first below after hi +", np.percentile(off_lat, [10, 50, 90]).round(3))
    # ---- NoC filter: grid over tau, delay
    wins = []
    for i, b in enumerate(B):
        nxt = [a for a, _, _ in M if a > b["hi"]]
        end = min(b["hi"] + 3.8, (nxt[0] - 0.05) if nxt else 1e18)
        w = (t >= b["lo"] - 3.0) & (t <= end)
        if T["took"][w].max() > 200:
            continue
        prev_fill = [(a, e) for a, e, k in M if e < b["lo"] and e > b["lo"] - 12]
        wins.append((held_times(t[w], T["noc"][w]), T["noc"][w], b["launches"], prev_fill))
    best = None
    res = {}
    for tau in np.arange(0.90, 1.20, 0.02):
        for delay in np.arange(0.15, 0.50, 0.025):
            sse = 0.0
            for ts, ys, L, pf in wins:
                X = [np.ones_like(ts), indicator_response(ts, L, tau, delay)]
                if pf:
                    X.append(indicator_response(ts, pf, tau, delay))
                X = np.vstack(X).T
                c, *_ = np.linalg.lstsq(X, ys, rcond=None)
                sse += float(((X @ c - ys) ** 2).sum())
            res[(round(tau, 3), round(delay, 3))] = sse
            if best is None or sse < best[0]:
                best = (sse, tau, delay)
    n = sum(len(w[0]) for w in wins)
    print(key, f"NoC filter best tau {best[1]:.2f} s delay {best[2]:.3f} s  rms {np.sqrt(best[0]/n)*1000:.1f} mW over {len(wins)} bursts")
    # profile: best sse at each tau
    prof = {}
    for (ta, de), s in res.items():
        prof[ta] = min(prof.get(ta, 1e30), s)
    print("   profile tau->rms mW:", {k: round(np.sqrt(v / n) * 1000, 1) for k, v in sorted(prof.items())[::4]})
    sys.stdout.flush()
