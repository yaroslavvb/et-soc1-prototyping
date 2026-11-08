#!/usr/bin/env python3
"""E183 (Q155): the per-launch noise of the board meter inside E180's committed bursts, read launch by launch as an A B B A train would
read it, and the train-sizing rule that rests on it (E183.md section 6). Standard library only; reads committed files only; no card.

    /usr/bin/python3 -B noise_e183.py <lab repo root> [<out.json>]     # default: noise-e183.json beside this file

THE READING OF ONE LAUNCH (E182's rule, e182_stats.launch_reading and dips_kept, used here unchanged):
  - its window is [t_start_ms + 170 ms, t_end_ms] of the launch's ENERCAT record (about 0.23 s of a 0.400 s launch);
  - the samples are the block sampler's 10 Hz telemetry lines (`board_w`, t_ms), with E82 amendment A2's dip rule applied over the
    pass's whole sample sequence first (board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W drops sample i);
  - the reading is the mean of the kept samples in the window; fewer than 2 kept samples: no reading.
A QUAD of a burst of one kind (E180's bursts: launches 0..7 of 0.400 s, in one process) is launches (1, 2, 3, 4), launch 0 being the
settle launch: c = (L2 + L3 - L1 - L4) / 2. In a train the four launches are X Y Y X; here all four are one kind, so c has mean 0 and its
scatter is the noise a train's quad meets from the meter and the chip in one thermal state. Launches (4, 5, 6, 7) give a second quad that
shares launch 4 with the first; it is reported beside (its sd is a check of the first's), never the sizing input.
The figures are POST HOC readings of committed data (E180, Fri 6 Nov 2026), used as the registration's noise model; nothing here is a
measurement of E183.
SPDX-License-Identifier: Apache-2.0
"""
import bisect
import gzip
import hashlib
import json
import math
import os
import statistics as st
import sys

sys.dont_write_bytecode = True
E180 = "docs/reports/data/2026-11-06-e180-vector-add-aifoundry3"
PASSES = ("p18010", "p18011", "p18012", "p18013", "p18014", "p18015")
LAG_MS = 170
DIP_W = 4.0
QUAD = (1, 2, 3, 4)
QUAD2 = (4, 5, 6, 7)
TARGET_HW_W = 0.005          # the sizing rule's half-width a train (E182.md section 6's)
Z = 1.96


def klass(kind):
    mode, name = kind.split("/", 1)
    if mode != "fadd.ps":
        return "acc" if mode.endswith(".acc") else "fadd_pi"
    if name == "zeros":
        return "fadd_ps_zeros"
    if name == "random":
        return "fadd_ps_random"
    return "fadd_ps_one_number"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_tel(p):
    tel = []
    with gzip.open(p, "rt") as f:
        for line in f:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if isinstance(o.get("board_w"), (int, float)) and isinstance(o.get("t_ms"), (int, float)):
                tel.append((int(o["t_ms"]), float(o["board_w"])))
    tel.sort()
    v = [w for _, w in tel]
    keep = [True] * len(tel)
    for i in range(2, len(tel) - 2):
        if v[i] < min(v[i - 2], v[i + 2]) - DIP_W:
            keep[i] = False
    return [x for x, k in zip(tel, keep) if k], len(tel) - sum(keep)


def launch_reading(ts, tel, t0, t1):
    i0 = bisect.bisect_left(ts, t0 + LAG_MS)
    i1 = bisect.bisect_right(ts, t1)
    w = [tel[i][1] for i in range(i0, i1)]
    return (sum(w) / len(w), len(w)) if len(w) >= 2 else (None, len(w))


def mean_between(ts, tel, t0, t1):
    i0 = bisect.bisect_left(ts, t0)
    i1 = bisect.bisect_right(ts, t1)
    w = [tel[i][1] for i in range(i0, i1)]
    return sum(w) / len(w) if w else None


def robust_sd(x):
    m = st.median(x)
    return 1.4826 * st.median([abs(v - m) for v in x])


def summ(x):
    x = [v for v in x if v is not None]
    if len(x) < 3:
        return {"n": len(x)}
    return {"n": len(x), "mean_w": round(st.mean(x), 5), "sd_w": round(st.stdev(x), 5), "robust_sd_w": round(robust_sd(x), 5),
            "se_of_sd_w": round(st.stdev(x) / math.sqrt(2 * (len(x) - 1)), 5)}


def quad(rd, q):
    if all(i in rd for i in q):
        return (rd[q[1]] + rd[q[2]] - rd[q[0]] - rd[q[3]]) / 2
    return None


def main():
    root = os.path.abspath(sys.argv[1])
    d = os.path.join(root, E180)
    inputs = {}
    quads, quads2, settle, carry, resid_lag1, nsamp, gaps, launch_s, nlaunch = {}, {}, {}, {}, [], [], [], [], []
    per_pass, qq_pairs = {}, {}
    proc_wall = []
    dips_dropped = 0
    for p in PASSES:
        pd = os.path.join(d, "raw", "e180", p)
        for f in ("telemetry.jsonl.gz", "runs.jsonl.gz", "run.log"):
            inputs[f"{E180}/raw/e180/{p}/{f}"] = sha(os.path.join(pd, f))
        tel, nd = load_tel(os.path.join(pd, "telemetry.jsonl.gz"))
        dips_dropped += nd
        ts = [t for t, _ in tel]
        recs = []
        with gzip.open(os.path.join(pd, "runs.jsonl.gz"), "rt") as f:
            for line in f:
                line = line.strip()
                if line:
                    recs.append(json.loads(line))
        for line in open(os.path.join(pd, "run.log")):
            # "pass 18010 e180/fadd.ps/f_m5/h2: 8 launches in 3.5 s (rc 0)": the runner's wall time of one burst's process
            if " launches in " in line and line.rstrip().endswith("(rc 0)"):
                try:
                    proc_wall.append((int(line.split(": ")[1].split()[0]), float(line.split(" launches in ")[1].split()[0])))
                except (IndexError, ValueError):
                    pass
        runs = {}
        for r in recs:
            if not r.get("ok", True):
                continue
            runs.setdefault(r["cfg"], []).append(r)
        for cfg, L in runs.items():
            L.sort(key=lambda r: r["t_start_ms"])
            nlaunch.append(len(L))
            k = klass(L[0]["kind"])
            for a, b in zip(L, L[1:]):
                gaps.append(b["t_start_ms"] - a["t_end_ms"])
            launch_s.extend(r["wall_s"] for r in L)
            rd = {}
            for i, r in enumerate(L):
                v, n = launch_reading(ts, tel, r["t_start_ms"], r["t_end_ms"])
                nsamp.append(n)
                if v is not None:
                    rd[i] = v
            c1, c2 = quad(rd, QUAD), quad(rd, QUAD2)
            if c1 is not None:
                quads.setdefault(k, []).append(c1)
                per_pass.setdefault((p, k), []).append(c1)
            if c2 is not None:
                quads2.setdefault(k, []).append(c2)
            if c1 is not None and c2 is not None:
                qq_pairs.setdefault(k, []).append((c1, c2))
            later = [rd[i] for i in range(1, len(L)) if i in rd]
            if 0 in rd and len(later) >= 5:
                mu = sum(later) / len(later)
                settle.setdefault(k, []).append(rd[0] - mu)
                pre = mean_between(ts, tel, L[0]["t_start_ms"] - 1200, L[0]["t_start_ms"] - 200)
                if pre is not None and mu - pre > 2.0:
                    # the burst's step over the samples just before it: the share launch 0's window still misses
                    carry.setdefault(k, []).append((mu - rd[0]) / (mu - pre))
            if len(later) >= 5:
                mu = sum(later) / len(later)
                e = [rd[i] - mu for i in range(1, len(L)) if i in rd]
                for x, y in zip(e, e[1:]):
                    resid_lag1.append((x, y))
    out = {"_what": "E183's noise model: E180's committed board telemetry read launch by launch as an A B B A train would read it "
                    "(noise_e183.py; POST HOC readings of committed data, the registration's input)",
           "rule": {"window": "[t_start_ms + 170 ms, t_end_ms] of each launch", "dips": "E82 A2: board_w[i] < min(board_w[i-2], "
                    "board_w[i+2]) - 4.0 W, over the pass's samples", "min_samples": 2, "quad": "launches (1,2,3,4) of each burst, "
                    "launch 0 the settle; c = (L2 + L3 - L1 - L4) / 2", "quad2_reported": "launches (4,5,6,7), sharing launch 4",
                    "unit": "W at the board"},
           "inputs_sha256": inputs, "dips_dropped": dips_dropped}
    out["quads_by_class"] = {k: summ(v) for k, v in sorted(quads.items())}
    out["quads2_by_class_reported"] = {k: summ(v) for k, v in sorted(quads2.items())}
    out["quads_by_pass_and_class"] = {f"{p}|{k}": summ(v) for (p, k), v in sorted(per_pass.items())}

    def corr(pairs):
        xs, ys = [x for x, _ in pairs], [y for _, y in pairs]
        mx, my = st.mean(xs), st.mean(ys)
        cv = sum((x - mx) * (y - my) for x, y in pairs) / (len(pairs) - 1)
        return round(cv / (st.stdev(xs) * st.stdev(ys)), 4)

    out["corr_of_a_bursts_two_quads_by_class"] = {k: {"n_bursts": len(v), "r": corr(v)} for k, v in sorted(qq_pairs.items())
                                                  if len(v) > 3}
    out["settle_launch0_minus_later_by_class"] = {k: summ(v) for k, v in sorted(settle.items())}
    out["launch0_missed_share_of_the_step_by_class"] = {k: summ(v) for k, v in sorted(carry.items())}
    if resid_lag1:
        xs = [x for x, _ in resid_lag1]
        ys = [y for _, y in resid_lag1]
        mx, my = st.mean(xs), st.mean(ys)
        cov = sum((x - mx) * (y - my) for x, y in resid_lag1) / (len(xs) - 1)
        out["lag1_corr_of_launch_readings_within_bursts"] = round(cov / (st.stdev(xs) * st.stdev(ys)), 4)
    out["samples_per_launch_window"] = {"median": st.median(nsamp), "min": min(nsamp), "max": max(nsamp),
                                        "share_with_fewer_than_2": round(sum(1 for n in nsamp if n < 2) / len(nsamp), 5),
                                        "histogram": {str(n): nsamp.count(n) for n in sorted(set(nsamp))}}
    period = st.median(launch_s) + st.median(gaps) / 1000.0      # a launch's start to the next's (wall + gap)
    over = [w - n * period for n, w in proc_wall if n == 8]       # a burst's process: spawn, device open, close (run.log's wall, 0.1 s)
    out["timing"] = {"launch_wall_s_median": round(st.median(launch_s), 4), "launch_period_s": round(period, 4),
                     "gap_between_launches_ms_median": st.median(gaps), "gap_between_launches_ms_p95": sorted(gaps)[int(0.95 * len(gaps))],
                     "launches_per_burst": {str(n): nlaunch.count(n) for n in sorted(set(nlaunch))},
                     "burst_process_wall_s_median": st.median([w for _, w in proc_wall]) if proc_wall else None,
                     "burst_process_wall_s_max": max([w for _, w in proc_wall]) if proc_wall else None,
                     "process_overhead_s_median": round(st.median(over), 3) if over else None,
                     "process_overhead_s_max": round(max(over), 3) if over else None,
                     "bursts": len(proc_wall)}
    sq = out["quads_by_class"]["fadd_ps_one_number"]["sd_w"]
    n_q = math.ceil((Z * sq / TARGET_HW_W) ** 2)
    procs = int(math.ceil(n_q / 3.0))
    procs += procs % 2
    out["sigma_q_w"] = sq
    out["sizing"] = {"rule": "n_q = ceil((1.96 sigma_q / 0.005 W)^2); processes = the next even number at or above n_q / 3 "
                             "(three quads a process: launches 1-4, 5-8, 9-12 of 13 after the settle)",
                     "sigma_q_w": sq, "target_half_width_w": TARGET_HW_W, "n_quads": n_q, "processes": procs,
                     "half_width_base_w": round(Z * sq / math.sqrt(3 * procs), 5),
                     "half_width_doubled_w": round(Z * 2 * sq / math.sqrt(3 * procs), 5)}
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "noise-e183.json")
    open(dst, "w").write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("wrote", dst)


if __name__ == "__main__":
    main()
