#!/usr/bin/env python3
"""Energy per operation from run_enercat.sh: board power over idle, divided by the rate.

    analyze_enercat.py <dir> [<dir> ...] --out enercat.json

Each configuration is a burst of back-to-back launches with idle on both sides. Its power is the mean of the
10 Hz board-power samples inside the burst after the first half second; its idle is the mean of the two
bracketing idle stretches (the last 3 s of the gap before, the last 3 s of the gap after), which takes out
the drift of idle power with die temperature to first order. Energy per operation is

    e = (P_burst - P_idle) * T_burst / N_ops

where N_ops counts every operation the harts reported completing during the burst, so the gaps between
launches inside the burst (a few percent) are in both numerator and denominator. Nothing is fitted.
"""
import argparse
import collections
import gzip
import json
import math
import os

import numpy as np


def load_dir(d):
    tp = os.path.join(d, "telemetry.jsonl")
    op = (lambda p: gzip.open(p + ".gz", "rt")) if os.path.exists(tp + ".gz") else open
    tel = [json.loads(l) for l in op(tp) if l.startswith("{")]
    runs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl")) if l.strip()]
    return tel, runs


def key(r):
    return (r["pattern"], r["operands"], r["harts"], r["scp"], r["slice_bytes"] if r["pattern"] in ("st_stream", "tstore", "tload") else 0)


# Leakage slope from the model fitted on aifoundry2 (docs/findings/11-thermal-model.md): the derivative of
# P_idle(T) = P_fix + A exp((T - 80) / T_L). A burst runs a little hotter than the idle that brackets it, and
# this takes that extra leakage out of the "over idle" power. It is a correction of a few percent.
A_LEAK_80, T_L = 23.257, 36.0


def leak_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def analyze(tel, runs):
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    w = np.array([s["board_w"] for s in tel])
    T = np.array([s["temp_c"]["minshire"][0] for s in tel])
    rails = {k: np.array([s["sp"][k] for s in tel]) for k in ("minion_w", "sram_w", "noc_w")}
    groups = collections.OrderedDict()
    for r in runs:
        groups.setdefault(key(r), []).append(r)
    bursts = []
    for k, rs in groups.items():
        lo = min(r["t_start_ms"] for r in rs) / 1000.0
        hi = max(r["t_end_ms"] for r in rs) / 1000.0
        bursts.append((k, rs, lo, hi))
    bursts.sort(key=lambda b: b[2])
    out = []
    for i, (k, rs, lo, hi) in enumerate(bursts):
        busy = (t >= lo + 0.5) & (t <= hi)
        prev_hi = bursts[i - 1][3] if i else t[0]
        next_lo = bursts[i + 1][2] if i + 1 < len(bursts) else t[-1]
        before = (t >= max(prev_hi + 2.5, lo - 3.5)) & (t <= lo - 0.3)
        after = (t >= hi + 2.5) & (t <= min(next_lo - 0.3, hi + 6.0))
        if busy.sum() < 5 or before.sum() < 5:
            continue
        idle_b, idle_a = float(w[before].mean()), float(w[after].mean()) if after.sum() >= 5 else float("nan")
        idle = idle_b if np.isnan(idle_a) else 0.5 * (idle_b + idle_a)
        p = float(w[busy].mean())
        Tb, Ti = float(T[busy].mean()), float(np.concatenate([T[before], T[after]]).mean())
        over_raw = p - idle
        over = over_raw - leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti)   # extra leakage of the warmer burst
        wall = hi - lo
        ops = sum(r["ops"] for r in rs)
        bytes_ = sum(r["bytes"] for r in rs)
        devs = sum(r["cycles_max"] for r in rs) / 0.6e9
        rec = {"pattern": k[0], "unit": rs[0]["unit"], "operands": k[1], "harts": k[2], "scp": k[3],
               "slice_bytes": k[4], "participants": rs[0]["participants"], "launches": len(rs),
               "wall_s": wall, "device_s": devs, "duty": devs / wall,
               "ops": ops, "bytes": bytes_,
               "ops_per_s": ops / devs if devs else 0, "bytes_per_s": bytes_ / devs if devs else 0,
               "ops_per_cycle_per_hart": float(np.mean([r["ops_per_cycle_per_hart"] for r in rs])),
               "p_busy_w": p, "p_idle_w": idle, "idle_before_w": idle_b, "idle_after_w": idle_a,
               "over_idle_w": over, "over_idle_raw_w": over_raw, "leak_correction_w": over_raw - over,
               "die_c_busy": Tb, "die_c_idle": Ti,
               "pj_per_op": over * wall / ops * 1e12 if ops else None,
               "pj_per_byte": over * wall / bytes_ * 1e12 if bytes_ else None,
               "rails_busy": {r: float(v[busy].mean()) for r, v in rails.items()},
               "rails_idle": {r: float(v[before].mean()) for r, v in rails.items()},
               "n_busy": int(busy.sum()), "n_idle": int(before.sum() + after.sum())}
        out.append(rec)
    # marginal cost against the awake-core baseline with the same hart count
    spin = {r["harts"]: r for r in out if r["pattern"] == "spin"}
    for r in out:
        s = spin.get(r["harts"])
        if s and r["pattern"] != "spin" and r["ops"]:
            r["pj_per_op_vs_spin"] = (r["over_idle_w"] - s["over_idle_w"]) * r["wall_s"] / r["ops"] * 1e12
            r["spin_over_idle_w"] = s["over_idle_w"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    result = {"cards": {}}
    for d in a.dirs:
        tel, runs = load_dir(d)
        if not runs:
            continue
        host = runs[0].get("host", os.path.basename(d))
        result["cards"][host] = analyze(tel, runs)
    json.dump(result, open(a.out, "w"), indent=1)
    for host, rows in result["cards"].items():
        print(f"\n=== {host} ===")
        print(f"{'pattern':10s} {'operands':7s} {'h':>1s} {'over idle W':>11s} {'ops/s':>10s} {'pJ/op':>8s} "
              f"{'vs spin':>8s} {'pJ/B':>7s} {'die C':>6s} {'idle W':>7s}")
        for r in rows:
            tag = r["pattern"] + ("@scp" if r["scp"] else "")
            print(f"{tag:10s} {r['operands']:7s} {r['harts']:1d} {r['over_idle_w']:11.2f} {r['ops_per_s']:10.2e} "
                  f"{(r['pj_per_op'] or 0):8.2f} {(r.get('pj_per_op_vs_spin') or 0):8.2f} "
                  f"{(r['pj_per_byte'] or 0):7.2f} {r['die_c_busy']:6.1f} {r['p_idle_w']:7.2f}")


if __name__ == "__main__":
    main()
