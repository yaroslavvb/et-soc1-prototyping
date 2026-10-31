#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E78's desk checks on E79's committed raw passes, run BEFORE any E78 data exist. They set two parts of E78's
registered protocol (tools/claims-v3/kinds/E78.md): the quiet rule in front of the idle bracket, and the minion
rail's deconvolution. Output: e78_desk_checks.txt beside this file.

    python3 tools/claims-v3/kinds/e78_desk_checks.py docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/aifoundry3/hlp

[1] how fast board power and the minion rail fall back after a run or a heater ends (100 ms bins);
[2] the gaps E79's approach left before each run, and how many of its idle brackets ([t0-1.2 s, t0-0.2 s)) held
    the previous process;
[3] the minion rail as a first-order lag of board power: rail = a + c x IIR_tau(board(t - d)), per pass;
[4] the built-in pi anchor's drift, first to last in a pass, in E79's and E70's committed runs.csv;
[5] how far each kind of run heats the die inside the power window, in E67's and E70's committed runs.csv.
"""
import gzip
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np


def load(d):
    tel = [json.loads(l) for l in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") if l.startswith("{")]
    marks = sorted((json.loads(l) for l in open(os.path.join(d, "marks.jsonl")) if l.startswith("{")),
                   key=lambda m: m["t_start_ms"])
    recs = defaultdict(list)
    for l in open(os.path.join(d, "runs.jsonl")):
        r = json.loads(l)
        recs[(r["block"], r["item"], r["pos"], r.get("attempt", 1))].append(r)
    return tel, marks, recs


def main():
    D = sys.argv[1]
    passes = sorted(p for p in os.listdir(D) if p.startswith("p79"))
    prof = defaultdict(lambda: defaultdict(list))
    gaps, contaminated, n_runs = [], 0, 0
    fits = []
    for p in passes:
        tel, marks, recs = load(os.path.join(D, p))
        t = np.array([s["t_ms"] for s in tel], float)
        B = np.array([s["board_w"] for s in tel], float)
        R = np.array([s["sp"]["minion_w"][0] for s in tel], float)
        T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel], float)
        procs = [m for m in marks if m["kind"] in ("run", "heater", "burnin")]
        for i, m in enumerate(procs[:-1]):
            nxt = procs[i + 1]
            sel = (t >= m["t_end_ms"] - 500) & (t < nxt["t_start_ms"])
            for tt, b, r, T_ in zip(t[sel], B[sel], R[sel], T[sel]):
                k = int((tt - m["t_end_ms"]) // 100)
                prof[m["kind"]][k].append((b, r, T_))
            if nxt["kind"] == "run":
                rr = sorted(recs.get((nxt["block"], nxt["item"], nxt.get("pos", 0), nxt.get("attempt", 1)), []),
                            key=lambda r: r["t_start_ms"])
                if rr:
                    n_runs += 1
                    gaps.append(nxt["t_start_ms"] - m["t_end_ms"])
                    if rr[0]["t_start_ms"] - 1200 < m["t_end_ms"]:
                        contaminated += 1
        # [3] the rail's lag
        ts = t / 1000.0
        g = np.arange(ts[0], ts[-1], 0.1)
        Bg, Rg = np.interp(g, ts, B), np.interp(g, ts, R)
        best = None
        for tau in np.arange(0.2, 3.01, 0.05):
            al = 1 - math.exp(-0.1 / tau)
            f = np.empty_like(Bg)
            acc = Bg[0]
            for i, x in enumerate(Bg):
                acc += al * (x - acc)
                f[i] = acc
            for dn in range(0, 8):
                x = np.r_[np.full(dn, f[0]), f[:len(f) - dn]]
                A = np.c_[np.ones_like(x), x]
                coef, *_ = np.linalg.lstsq(A, Rg, rcond=None)
                rms = float(np.sqrt(np.mean((A @ coef - Rg) ** 2)))
                if best is None or rms < best[0]:
                    best = (rms, float(tau), dn * 0.1, float(coef[0]), float(coef[1]))
        A = np.c_[np.ones_like(Bg), Bg]
        c0, *_ = np.linalg.lstsq(A, Rg, rcond=None)
        rms0 = float(np.sqrt(np.mean((A @ c0 - Rg) ** 2)))
        fits.append((p, best, rms0))
    out = ["E78 desk checks on E79's committed passes " + ", ".join(passes), ""]
    for kind in ("run", "heater"):
        out.append(f"[1] after a {kind} ends: mean board W, minion rail W, minshire reading C (100 ms bins)")
        for k in range(-5, 31):
            v = prof[kind].get(k, [])
            if len(v) >= 5:
                a = np.array(v)
                out.append(f"    {k * 100:+6d} ms  board {a[:, 0].mean():7.2f}  rail {a[:, 1].mean():6.2f}  "
                           f"T {a[:, 2].mean():5.1f}  n={len(v)}")
    G = np.array(gaps, float)
    out += ["", f"[2] gap from the previous device process's end to a run's spawn: n {len(G)}, median {np.median(G):.0f} ms,"
            f" p10 {np.percentile(G, 10):.0f} ms, p25 {np.percentile(G, 25):.0f} ms, p90 {np.percentile(G, 90):.0f} ms;"
            f" share under 2.0 s {np.mean(G < 2000):.3f}",
            f"    runs whose idle bracket [t0-1.2 s, t0-0.2 s) began before the previous process ended: "
            f"{contaminated} of {n_runs} ({contaminated / max(n_runs, 1):.3f})",
            f"    a 2.0 s quiet rule would have added {np.mean(np.clip(2000 - G, 0, None)):.0f} ms a run on average "
            f"(it extends {np.mean(G < 2000):.3f} of the runs)", ""]
    out.append("[3] rail = a + c x IIR_tau(board(t - d)), best fit per pass (grid tau 0.20-3.00 s, d 0-0.7 s)")
    for p, (rms, tau, d, a0, c), r0 in fits:
        out.append(f"    {p}: tau {tau:.2f} s, d {d:.1f} s, c {c:.3f}, a {a0:.2f} W; rms {rms:.3f} W (no lag: {r0:.3f} W)")
    taus = [b[1] for _, b, _ in fits]
    cs = [b[4] for _, b, _ in fits]
    out.append(f"    tau median {np.median(taus):.3f} s (range {min(taus):.2f}-{max(taus):.2f}), delay "
               f"{sorted(set(b[2] for _, b, _ in fits))} s, c median {np.median(cs):.3f} (range {min(cs):.3f}-"
               f"{max(cs):.3f}); rms {min(b[0] for _, b, _ in fits):.3f}-{max(b[0] for _, b, _ in fits):.3f} W against "
               f"{min(x for _, _, x in fits):.3f}-{max(x for _, _, x in fits):.3f} W with no lag")
    # [4] the drift of the built-in pi anchor, first to last in a pass, in E79's and E70's committed runs.csv
    import csv
    repo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    out += ["", "[4] anchor_pi p80, last minus first in each pass (W)"]
    for lab, f in (("E79", "docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/runs.csv"),
                   ("E70", "docs/reports/data/2026-10-27-e70-saturation-ladder/runs.csv")):
        by = defaultdict(list)
        for r in csv.DictReader(open(os.path.join(repo, f))):
            if r["item"] == "anchor_pi":
                by[r["pass"]].append((int(r["pos"]), float(r["p80"])))
        dr = [(p_, v[-1][1] - v[0][1]) for p_, v in sorted((k_, sorted(v_)) for k_, v_ in by.items()) if len(v) >= 2]
        out.append(f"    {lab} ({f}): " + ", ".join(f"{p_} {d:+.3f}" for p_, d in dr)
                   + f"; |drift| {min(abs(d) for _, d in dr):.3f}-{max(abs(d) for _, d in dr):.3f}")
    # [5] how far each kind of run heats the die inside the power window: mean(t_win - start_c) by item
    out += ["", "[5] the die reading's rise over the power window, t_win - start_c, by item (C)"]
    for lab, f in (("E67", "docs/reports/data/2026-10-27-e67-a-side-bit-prices/runs.csv"),
                   ("E70", "docs/reports/data/2026-10-27-e70-saturation-ladder/runs.csv")):
        by = defaultdict(list)
        for r in csv.DictReader(open(os.path.join(repo, f))):
            try:
                by[r["item"]].append(float(r["t_win"]) - float(r["start_c"]))
            except (KeyError, ValueError):
                pass
        sel = [i for i in ("anchor_zeros", "anchor_ones", "anchor_pi", "anchor_randn", "nrd_a", "nrd_b", "lq_h23") if i in by]
        out.append(f"    {lab} ({f}): " + ", ".join(f"{i} {np.mean(by[i]):.2f} (n {len(by[i])})" for i in sel))
    txt = "\n".join(out) + "\n"
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "e78_desk_checks.txt"), "w").write(txt)
    print(txt, end="")


if __name__ == "__main__":
    main()
