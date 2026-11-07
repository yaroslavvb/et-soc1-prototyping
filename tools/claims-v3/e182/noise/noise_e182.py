#!/usr/bin/env python3
"""E182 (Q153): the per-launch noise of the board meter inside E178's committed runs, read as an A B B A train would read it, and
the train-sizing rule that rests on it (E182.md section 6). Standard library only; reads committed files only; no card.

    /usr/bin/python3 -B noise_e182.py <lab repo root> [<out.json>]     # default: noise-e182.json beside this file

THE READING OF ONE LAUNCH (registered for E182's trains, E182.md section 5.2, and used here unchanged):
  - its window is [t_start_ms + 170 ms, t_end_ms] of the launch's SPARSITY record (about 0.32 s of a 0.49 s launch);
  - the samples are the session sampler's 10 Hz telemetry lines (`board_w`, t_ms), with E82 amendment A2's dip rule applied over the
    pass's whole sample sequence first (board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W drops sample i);
  - the reading is the mean of the kept samples in the window; fewer than 2 kept samples: no reading.
A QUAD of a run of one kind (E178's runs: a calibration launch, then launches 0..8 of about 0.49 s) is launches (1, 2, 3, 4) or
(5, 6, 7, 8), launch 0 being the settle launch: c = (L2 + L3 - L1 - L4) / 2. In a train the four launches would be X Y Y X; here all
four are one kind, so c has mean 0 and its scatter is the noise a train's quad meets from the meter and the chip in one thermal state.
The figures are POST HOC readings of committed data (E178, Fri 6 Nov 2026), used as the registration's noise model; nothing here is a
measurement of E182.
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
E178 = "docs/reports/data/2026-11-06-e178-one-number-aifoundry3"
PASSES = ("p17810", "p17811", "p17812", "p17813")
LAG_MS = 170
DIP_W = 4.0
QUADS = ((1, 2, 3, 4), (5, 6, 7, 8))


def klass(item):
    if item.endswith(".zeros"):
        return "zeros"
    if item in ("fp32.randn", "fp16.randn", "int8.full", "anchor_pi"):
        return "random_anchor"
    if item.startswith("int8."):
        return "int8_one_number"
    return "float_one_number"


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


def robust_sd(x):
    m = st.median(x)
    return 1.4826 * st.median([abs(v - m) for v in x])


def summ(x):
    x = [v for v in x if v is not None]
    if len(x) < 3:
        return {"n": len(x)}
    return {"n": len(x), "mean_w": round(st.mean(x), 5), "sd_w": round(st.stdev(x), 5), "robust_sd_w": round(robust_sd(x), 5),
            "se_of_sd_w": round(st.stdev(x) / math.sqrt(2 * (len(x) - 1)), 5)}


def main():
    root = os.path.abspath(sys.argv[1])
    d = os.path.join(root, E178)
    inputs = {}
    quads, settle, resid_lag1, nsamp, gaps, launch_s, spawn_ms, tail_ms = {}, {}, [], [], [], [], [], []
    per_pass, qq_pairs, proc_means = {}, {}, {}
    dips_dropped = 0
    for p in PASSES:
        pd = os.path.join(d, "aifoundry3", "e178", p)
        for f in ("telemetry.jsonl.gz", "runs.jsonl", "marks.jsonl"):
            inputs[f"{E178}/aifoundry3/e178/{p}/{f}"] = sha(os.path.join(pd, f))
        tel, nd = load_tel(os.path.join(pd, "telemetry.jsonl.gz"))
        dips_dropped += nd
        ts = [t for t, _ in tel]
        recs = [json.loads(x) for x in open(os.path.join(pd, "runs.jsonl"))]
        marks = [json.loads(x) for x in open(os.path.join(pd, "marks.jsonl"))]
        runmark = {(m["pos"], m["item"]): m for m in marks if m.get("kind") == "run"}
        runs = {}
        for r in recs:
            if not r.get("ok", True):
                continue
            runs.setdefault((r["pos"], r["item"]), []).append(r)
        for (pos, item), L in runs.items():
            L.sort(key=lambda r: r["launch"])
            k = klass(item)
            real = [r for r in L if r["launch"] >= 0]
            m = runmark.get((pos, item))
            if m and real:
                cal = [r for r in L if r["launch"] < 0]
                spawn_ms.append((cal[0]["t_start_ms"] if cal else real[0]["t_start_ms"]) - m["t_start_ms"])
                tail_ms.append(m["t_end_ms"] - real[-1]["t_end_ms"])
            for a, b in zip(real, real[1:]):
                gaps.append(b["t_start_ms"] - a["t_end_ms"])
            launch_s.extend(r["wall_s"] for r in real)
            rd = {}
            for r in real:
                v, n = launch_reading(ts, tel, r["t_start_ms"], r["t_end_ms"])
                nsamp.append(n)
                if v is not None:
                    rd[r["launch"]] = v
            cs = []
            for q in QUADS:
                if all(i in rd for i in q):
                    c = (rd[q[1]] + rd[q[2]] - rd[q[0]] - rd[q[3]]) / 2
                    quads.setdefault(k, []).append(c)
                    per_pass.setdefault((p, k), []).append(c)
                    cs.append(c)
            if len(cs) == 2:
                qq_pairs.setdefault(k, []).append(tuple(cs))
                proc_means.setdefault(k, []).append(sum(cs) / 2)
            later = [rd[i] for i in range(1, 9) if i in rd]
            if 0 in rd and len(later) >= 6:
                settle.setdefault(k, []).append(rd[0] - sum(later) / len(later))
            if len(later) >= 6:
                mu = sum(later) / len(later)
                e = [rd[i] - mu for i in range(1, 9) if i in rd]
                for x, y in zip(e, e[1:]):
                    resid_lag1.append((x, y))
    out = {"_what": "E182's noise model: E178's committed board telemetry read launch by launch as an A B B A train would read it "
                    "(noise_e182.py; POST HOC readings of committed data, the registration's input)",
           "rule": {"window": "[t_start_ms + 170 ms, t_end_ms] of each launch", "dips": "E82 A2: board_w[i] < min(board_w[i-2], "
                    "board_w[i+2]) - 4.0 W, over the pass's samples", "min_samples": 2, "quads": "launches (1,2,3,4) and (5,6,7,8) of "
                    "each run, launch 0 the settle; c = (L2 + L3 - L1 - L4) / 2", "unit": "W at the board"},
           "inputs_sha256": inputs, "dips_dropped": dips_dropped}
    out["quads_by_class"] = {k: summ(v) for k, v in sorted(quads.items())}
    one = quads.get("int8_one_number", []) + quads.get("float_one_number", [])
    out["quads_one_number_pooled"] = summ(one)
    out["quads_by_pass_and_class"] = {f"{p}|{k}": summ(v) for (p, k), v in sorted(per_pass.items())}
    def corr(pairs):
        xs, ys = [x for x, _ in pairs], [y for _, y in pairs]
        mx, my = st.mean(xs), st.mean(ys)
        cv = sum((x - mx) * (y - my) for x, y in pairs) / (len(pairs) - 1)
        return round(cv / (st.stdev(xs) * st.stdev(ys)), 4)
    out["corr_of_a_runs_two_quads_by_class"] = {k: {"n_runs": len(v), "r": corr(v)} for k, v in sorted(qq_pairs.items()) if len(v) > 3}
    out["run_mean_of_two_quads_by_class"] = {k: summ(v) for k, v in sorted(proc_means.items())}
    out["settle_launch0_minus_later_by_class"] = {k: summ(v) for k, v in sorted(settle.items())}
    if resid_lag1:
        xs = [x for x, _ in resid_lag1]
        ys = [y for _, y in resid_lag1]
        mx, my = st.mean(xs), st.mean(ys)
        cov = sum((x - mx) * (y - my) for x, y in resid_lag1) / (len(xs) - 1)
        out["lag1_corr_of_launch_readings_within_runs"] = round(cov / (st.stdev(xs) * st.stdev(ys)), 4)
    out["samples_per_launch_window"] = {"median": st.median(nsamp), "min": min(nsamp), "max": max(nsamp),
                                        "share_with_fewer_than_2": round(sum(1 for n in nsamp if n < 2) / len(nsamp), 5)}
    out["timing"] = {"launch_wall_s_median": round(st.median(launch_s), 4),
                     "gap_between_launches_ms_median": st.median(gaps), "gap_between_launches_ms_p95": sorted(gaps)[int(0.95 * len(gaps))],
                     "spawn_to_first_launch_ms_median": st.median(spawn_ms), "spawn_to_first_launch_ms_max": max(spawn_ms),
                     "last_launch_end_to_process_end_ms_median": st.median(tail_ms), "last_launch_end_to_process_end_ms_max": max(tail_ms),
                     "runs": len(spawn_ms)}
    # the sizing rule (E182.md section 6): base noise sigma_q = the int8 (or float) one-number quads' sd; twice it for the doubled case
    out["sigma_q_w"] = {"int8": out["quads_by_class"]["int8_one_number"]["sd_w"],
                        "float": out["quads_by_class"]["float_one_number"]["sd_w"]}
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "noise-e182.json")
    open(dst, "w").write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("wrote", dst)


if __name__ == "__main__":
    main()
