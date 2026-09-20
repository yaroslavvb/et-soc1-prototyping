#!/usr/bin/env python3
"""Energy per load, per pattern and per power rail, from a run_power.py output folder.

Board power comes from power.csv (host log of DM_CMD_GET_MODULE_POWER). Rail power comes from the service
processor's stats trace (dev0_sp_stats_*.bin): one record per ~133 ms loop pass, each with a moving average of
the minion, SRAM and NoC rail power (mW) and of board power (10 mW units, "system"). The trace's clock (SP µs) is
aligned to wall time by matching its board power to the host log. For each pattern, power in the last part of
its launch window minus the power just before the process started, divided by the load rate, is energy per load.

    analyze_power.py build/memprobe-power6 [--json out.json]
"""
import argparse
import collections
import csv
import glob
import json
import os
import statistics as st
import struct

RAILS = ["minion", "sram", "noc", "system"]


def read_trace(folder):
    recs = {}
    for f in glob.glob(os.path.join(folder, "dev0_sp_stats*.bin")) + glob.glob(os.path.join(folder, "trace", "*.done")):
        d = open(f, "rb").read()
        for off in range(64, len(d) - 151, 152):
            cyc, = struct.unpack_from("<Q", d, off)
            avg = {}
            for i, name in enumerate(RAILS):
                a, _mn, _mx = struct.unpack_from("<HHH", d, off + 24 + i * 32 + 8)  # op_module.power
                avg[name] = a / 1000.0 if name != "system" else a / 100.0  # W
            recs[cyc] = avg
    return sorted(recs.items())


def align(trace, board):
    """Offset (ms) that maps SP µs / 1000 onto epoch ms, by least squares between trace board power and
    the host log (both smoothed differently, so this is good to ~100 ms)."""
    bt = [t for t, _ in board]
    bw = [w for _, w in board]
    import bisect

    def err(off):
        e, n = 0.0, 0
        for cyc, v in trace[::3]:
            t = cyc / 1000.0 + off
            i = bisect.bisect_left(bt, t)
            if 0 < i < len(bt):
                e += (bw[i] - v["system"]) ** 2
                n += 1
        return e / n if n > 20 else 1e18, n

    # Coarse: the trace clock is time since the SP booted; try offsets around the last record = last sample.
    base = board[-1][0] - trace[-1][0] / 1000.0
    best = min(((err(base + k * 50)[0], base + k * 50) for k in range(-2000, 2001, 4)))
    fine = min(((err(best[1] + k * 10)[0], best[1] + k * 10) for k in range(-40, 41)))
    return fine[1], fine[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--json")
    ap.add_argument("--settle", type=float, default=2.5, help="seconds after the first launch to skip (moving average)")
    args = ap.parse_args()
    board = [(int(r["epoch_ms"]), float(r["watts"])) for r in csv.DictReader(open(os.path.join(args.folder, "power.csv")))]
    runs = [json.loads(l) for l in open(os.path.join(args.folder, "runs.jsonl"))]
    trace = read_trace(args.folder)
    off, e2 = align(trace, board)
    rail = [(cyc / 1000.0 + off, v) for cyc, v in trace]

    win = collections.defaultdict(lambda: {"p0": 1e18, "s": 1e18, "e": 0, "loads": 0, "wall": 0.0, "cpl": [], "ghz": []})
    for r in runs:
        w = win[(r["pattern"], r["rep"])]
        w["p0"] = min(w["p0"], r["t_start_ms"])
        if r["launch"] < 0:
            continue
        w["s"] = min(w["s"], r["t_start_ms"])
        w["e"] = max(w["e"], r["t_end_ms"])
        w["loads"] += r["loads"]
        w["wall"] += r["wall_s"]
        w["cpl"].append(r["cycles_mean"] * r["minions"] / r["loads"])
        w["ghz"].append(r["cycles_max"] / r["wall_s"] / 1e9)

    def mean(series, a, b, key=None):
        v = [(x[key] if key else x) for t, x in series if a <= t <= b]
        return st.mean(v) if v else float("nan")

    out = collections.defaultdict(list)
    for (pat, rep), w in sorted(win.items(), key=lambda kv: kv[1]["s"]):
        a, b = w["s"] + args.settle * 1000, w["e"]
        rec = {"rep": rep, "rate": w["loads"] / w["wall"], "cycles_per_load": st.mean(w["cpl"]), "ghz": st.mean(w["ghz"])}
        rec["board_base"] = mean(board, w["p0"] - 1400, w["p0"] - 400)
        rec["board_run"] = mean(board, a, b)
        for k in RAILS:
            rec[k + "_base"] = mean(rail, w["p0"] - 1500, w["p0"] - 300, k)
            rec[k + "_run"] = mean(rail, a, b, k)
        out[pat].append(rec)

    print(f"trace aligned: offset {off:.0f} ms, rms {e2 ** 0.5:.2f} W; {len(trace)} records")
    print(f"{'pattern':10s} {'cyc/ld':>7s} {'loads/s':>9s} | {'board':>6s} {'minion':>6s} {'sram':>6s} {'noc':>6s} {'rest':>6s}  "
          f"(W above idle) | pJ/load: board minion sram noc rest")
    summary = {}
    for pat, recs in out.items():
        d = {}
        for k in ["board"] + RAILS:
            d[k] = st.mean(r[k + "_run"] - r[k + "_base"] for r in recs)
        d["rest"] = d["board"] - d["minion"] - d["sram"] - d["noc"]
        rate = st.mean(r["rate"] for r in recs)
        cpl = st.mean(r["cycles_per_load"] for r in recs)
        pj = {k: d[k] / rate * 1e12 for k in ["board", "minion", "sram", "noc", "rest"]}
        summary[pat] = {"watts": d, "rate": rate, "cycles_per_load": cpl, "pj_per_load": pj,
                        "reps": recs, "ghz": st.mean(r["ghz"] for r in recs)}
        print(f"{pat:10s} {cpl:7.1f} {rate:9.3e} | {d['board']:6.2f} {d['minion']:6.2f} {d['sram']:6.2f} {d['noc']:6.2f} "
              f"{d['rest']:6.2f} | {pj['board']:7.1f} {pj['minion']:7.1f} {pj['sram']:7.1f} {pj['noc']:7.1f} {pj['rest']:7.1f}")
    if args.json:
        json.dump({"offset_ms": off, "summary": summary}, open(args.json, "w"), indent=1)


if __name__ == "__main__":
    main()
