"""Method B loader: bursts at the level of launches and samples (independent of analyze_wire.py)."""
import collections
import json
import os

import numpy as np

DATA = "/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data"
SETS = {("v1", "aifoundry2"): "2026-09-24-wire-aifoundry2", ("v1", "aifoundry3"): "2026-09-24-wire-aifoundry3",
        ("v2", "aifoundry2"): "2026-09-24-wire2-aifoundry2", ("v2", "aifoundry3"): "2026-09-24-wire2-aifoundry3"}
F_DEV = 600e6


def jl(p):
    return [json.loads(l) for l in open(p) if l.startswith("{")]


def load(d):
    d = os.path.join(DATA, d)
    tel, runs, marks = jl(d + "/telemetry.jsonl"), jl(d + "/runs.jsonl"), jl(d + "/marks.jsonl")
    T = {
        "t": np.array([s["t_ms"] for s in tel]) / 1000.0,
        "took": np.array([s["took_ms"] for s in tel], float),
        "board": np.array([s["board_w"] for s in tel], float),
        "noc": np.array([s["sp"]["noc_w"][0] for s in tel], float),
        "temp": np.array([s["temp_c"]["minshire"][0] for s in tel], float),
        "mhz": np.array([s["mhz"]["minion"] for s in tel], float),
    }
    g = collections.OrderedDict()
    for r in runs:
        g.setdefault((r["cfg"], r["pass"]), []).append(r)
    bursts = []
    for (cfg, p), rs in g.items():
        rs = sorted(rs, key=lambda r: r["t_start_ms"])
        L = np.array([[r["t_start_ms"] / 1000.0, r["t_end_ms"] / 1000.0] for r in rs])
        bursts.append({"cfg": cfg, "pass": p, "launches": L, "lo": L[0, 0], "hi": L[-1, 1],
                       "dev_s": sum(r["cycles_max"] for r in rs) / F_DEV, "bytes": sum(r["bytes"] for r in rs),
                       "hop": rs[0].get("hop_distance", 0), "mean_hops": rs[0].get("mean_hops", 0),
                       "participants": rs[0]["participants"], "operands": rs[0]["operands"]})
    bursts.sort(key=lambda b: b["lo"])
    mk = sorted([(m["t_start_ms"] / 1000.0, m["t_end_ms"] / 1000.0, m["kind"]) for m in marks])
    return T, bursts, mk


def in_marks(t, marks, pad_lo=0.0, pad_hi=0.0):
    m = np.zeros(len(t), bool)
    for a, b, _ in marks:
        m |= (t >= a - pad_lo) & (t <= b + pad_hi)
    return m


def indicator_response(ts, intervals, tau, delay):
    """First-order low-pass (time constant tau) response at times ts to a unit input that is on over the given
    intervals, each shifted by delay. Exact for piecewise-constant input."""
    y = np.zeros(len(ts))
    for a, b in intervals:
        a, b = a + delay, b + delay
        # response to a pulse [a, b]: 0 before a; 1 - exp(-(t-a)/tau) in [a, b]; (1-exp(-(b-a)/tau)) exp(-(t-b)/tau) after
        on = (ts >= a) & (ts < b)
        y[on] += 1.0 - np.exp(-(ts[on] - a) / tau)
        af = ts >= b
        y[af] += (1.0 - np.exp(-(b - a) / tau)) * np.exp(-(ts[af] - b) / tau)
    return y


def held_times(ts, ys):
    """The service processor updates its filtered average every ~0.27 s and a 10 Hz reader sees the held value:
    give each sample the time at which its value first appeared."""
    out = ts.copy()
    for i in range(1, len(ts)):
        if ys[i] == ys[i - 1]:
            out[i] = out[i - 1]
    return out
