#!/usr/bin/env python3
"""E111 (Q133): POST HOC and descriptive, written after the registration and run after the registered reduction; it decides nothing.

    /usr/bin/python3 posthoc_e111.py <this data dir> [--fig holds.png] > posthoc.txt

1. room: aifoundry2's idle board W and die over the afternoon (its own 5 s history, rows with the card free and under 26 W), in 10 min
   means, beside Q132(g)'s nine-day hour means (its README section (c) table, quoted), and the W-derived rest die of each probe.
2. holds: each hold in 60 s bins from its first process: die, board W, the fine W at the hold's clock, the clock; how much of the last
   bin's rise over the idle had arrived by 1, 2, 5, 10 and 20 minutes (from the hold's own start, which is not a rest).
3. the die at 0.005 Hz: in the camera block, the 10 Hz die and board W fitted per analysed lap by a sine and cosine at f0 with a quadratic
   trend over the block; the die's transfer (C per W of board fundamental) and its lag, beside the camera's.
4. refit: E73's 14 points and E111's camera points (f0 and its odd harmonics with the board at >= 5 SE) under their own gain, the four
   shapes of desk/fit_e73_models.py, chi2 and AIC (scipy).
"""
import argparse
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def jl(p):
    if not os.path.exists(p) and os.path.exists(p + ".gz"):
        p = p + ".gz"
    op = gzip.open if p.endswith(".gz") else open
    out = []
    with op(p, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def tel_rows(p):
    out = []
    for d in jl(p):
        try:
            t = d.get("temp_c", {})
            ms = t.get("minshire") or [None]
            out.append((int(d["t_ms"]), ms[0], d.get("board_w"), (d.get("mhz") or {}).get("minion")))
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    out.sort()
    return out


def history(d, box):
    rows = []
    hd = os.path.join(d, "history")
    for f in sorted(os.listdir(hd)) if os.path.isdir(hd) else []:
        if f.startswith(box + "-"):
            rows += jl(os.path.join(hd, f))
    rows.sort(key=lambda r: r.get("t", 0))
    return rows


def room(d, res):
    print("1. ROOM: aifoundry2's idle card over the afternoon (10 min means of free rows under 26 W)")
    rows = history(d, "aifoundry2")
    bins = {}
    for r in rows:
        c = (r.get("cards") or [{}])[0]
        if c.get("held") or c.get("w") is None or c["w"] > 26 or c.get("die") is None or c["die"] > 55:
            continue
        k = int(r["t"] // 600000)
        bins.setdefault(k, []).append((c["w"], c["die"], (r.get("temps") or {}).get("nic")))
    import time as T
    for k in sorted(bins):
        v = bins[k]
        if len(v) < 30:
            continue
        w = sum(x[0] for x in v) / len(v)
        die = sum(x[1] for x in v) / len(v)
        nic = [x[2] for x in v if x[2] is not None]
        print(f"   {T.strftime('%H:%M', T.localtime(k * 600))}  W {w:.3f}  die {die:.2f}  W-derived {w / 0.2315:.2f}  a2 NIC {sum(nic) / len(nic):.2f}  n {len(v)}")
    print("   Q132(g)'s nine-day hour means at rest (PDT): 11h 46.08 C / 21.94 W, 14h 47.93 / 22.36, 16h 49.54 / 22.76, 20h 49.59 / 22.77")


def holds(d, res, fig):
    print("\n2. HOLDS in 60 s bins from the first process (die whole-degree mean, board W, fine W at the hold's clock, clock)")
    # amendment A2: H-I8 is W1B's hold, from rest; H-F32 is W2's, which starts after E98's probe series and hold
    spec = {"H-I8": ("W1B", "HOLD-00-int8-neg_ones-hold-r1", 800), "H-F32": ("W2", "HOLDF-00-fp32-randn-hold-r1", 600)}
    curves = {}
    for h, (step, run, clock) in spec.items():
        pdir = os.path.join(d, step)
        runs = jl(os.path.join(pdir, "runs.jsonl"))
        r = next((x for x in runs if x["run"] == run), None)
        if r is None:
            print(f"   {h}: not run")
            continue
        tel = tel_rows(os.path.join(pdir, r["tel"]))
        t0 = r["t_first_ms"]
        t1 = r["t_last_ms"]
        A = res["A"].get(h, {})
        idle = None
        if A.get("idle_before") is not None and A.get("idle_after") is not None:
            idle = (A["idle_before"] + A["idle_after"]) / 2.0
        rowsb = []
        for m in range(0, int((t1 - t0) / 60000)):          # whole minutes inside the work only
            a, b = t0 + m * 60000, t0 + (m + 1) * 60000
            xs = [x for x in tel if a <= x[0] < b and x[1] is not None and x[2] is not None]
            if len(xs) < 300:
                continue
            fine = [x[2] for x in xs if x[3] == clock]
            rowsb.append((m + 0.5, sum(x[1] for x in xs) / len(xs), sum(x[2] for x in xs) / len(xs),
                          (sum(fine) / len(fine)) if len(fine) > 0.7 * len(xs) else None, sum(x[3] for x in xs) / len(xs)))
        curves[h] = rowsb
        print(f"   {h} from {step} ({len(rowsb)} bins; idle die, mean of before and after, {idle}):")
        for row in rowsb:
            if int(row[0]) in (0, 1, 2, 3, 5, 7, 10, 15, 20, 25) or row is rowsb[-1]:  # the bin's centre, minutes
                print(f"     min {row[0]:5.1f}  die {row[1]:6.2f}  W {row[2]:6.2f}  fine {row[3] if row[3] is None else round(row[3], 3)}  MHz {row[4]:.0f}")
        if idle is not None and rowsb:
            last = rowsb[-1][1] - idle
            plat = sum(r[1] for r in rowsb[-5:]) / len(rowsb[-5:]) - idle
            for mm in (1, 2, 5, 10, 20):
                v = next((row[1] for row in rowsb if row[0] >= mm), None)
                if v is not None and plat:
                    print(f"     rise over the idle by {mm:2d} min: {v - idle:6.2f} C, {100 * (v - idle) / plat:5.1f}% of the last 5 bins' {plat:.2f} C")
    curves = {k: v for k, v in curves.items() if v}
    if fig and curves:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        col = {"H-I8": "#2a78d6", "H-F32": "#eb6834"}
        lab = {"H-I8": "int8 neg_ones, 800 MHz", "H-F32": "fp32 randn, 600 MHz floor"}
        figr, ax = plt.subplots(1, 2, figsize=(10, 3.8), dpi=150)
        figr.patch.set_facecolor("#fcfcfb")
        for h, rowsb in curves.items():
            m = [r[0] for r in rowsb]
            ax[0].plot(m, [r[1] for r in rowsb], color=col[h], lw=2)
            ax[0].text(m[-1] + 0.4, rowsb[-1][1], lab[h], color="#0b0b0b", fontsize=8, va="center")
            ax[1].plot(m, [r[2] for r in rowsb], color=col[h], lw=2)
            ax[1].text(m[-1] + 0.4, rowsb[-1][2], lab[h], color="#0b0b0b", fontsize=8, va="center")
            A = res["A"].get(h, {})
            if A.get("idle_before") is not None:
                ax[0].axhline((A["idle_before"] + A["idle_after"]) / 2.0 if A.get("idle_after") is not None else A["idle_before"],
                              color=col[h], lw=1, ls=(0, (3, 3)))
        ax[0].set_ylabel("die, 34-sensor mean (°C)", color="#52514e")
        ax[1].set_ylabel("board power (W)", color="#52514e")
        for a in ax:
            a.set_xlabel("minutes from the hold's first process", color="#52514e")
            a.set_facecolor("#fcfcfb")
            a.grid(True, color="#e6e5e0", lw=0.6)
            for s in ("top", "right"):
                a.spines[s].set_visible(False)
            a.tick_params(colors="#52514e", labelsize=8)
            a.set_xlim(0, max(r[0] for rr in curves.values() for r in rr) + 12)
        ax[0].set_title("Die through each hold (dashed: its idle)", fontsize=9, color="#0b0b0b", loc="left")
        ax[1].set_title("Board power through each hold", fontsize=9, color="#0b0b0b", loc="left")
        figr.tight_layout()
        figr.savefig(fig, facecolor=figr.get_facecolor())
        print(f"   wrote {os.path.basename(fig)}")


def drift_check(d, res):
    print("\n5. THE DRIFT, W2 against E98's own frozen fits (E98's results.json: R1 and R2 on its four probes)")
    root = os.environ.get("E111_ROOT") or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    r98 = json.load(open(os.path.join(root, "docs/reports/data/2026-11-01-e98-heat-path-drift/results.json")))
    B = res["B"]
    x = B["rest_die"].get("W2")
    if x is None:
        print("   W2 not counted")
        return
    base = ["P3", "P6", "P7"]
    bx = sum(B["rest_die"][p] for p in base) / 3
    bl = sum(B["per_probe_line"][p] for p in base) / 3
    bh = sum(B["per_probe_hold"][p] for p in base) / 3
    for name, fitk, obs, bv in (("line", "R1", B["per_probe_line"].get("W2"), bl), ("hold die", "R2", B["per_probe_hold"].get("W2"), bh)):
        f = r98[fitk]["fit"]
        pred = f["icpt"] + f["slope"] * x
        print(f"   {name}: E98's fit (slope {f['slope']}) predicts {pred:.3f} C at W2's rest die; W2 read {obs:.3f}, residual {obs - pred:+.3f} C")
        for sl in (0.25, 1.12, 2.19):
            print(f"      from the mean of P3, P6, P7 at a slope of {sl}: {bv + sl * (x - bx):.3f} (W2 {obs - bv - sl * (x - bx):+.3f})")
    print(f"   W2's rest die is {x - bx:+.3f} C from the mean of P3, P6, P7 (W-derived)")


def die_lockin(d, res):
    print("\n3. THE DIE AT 0.005 Hz, in the camera block (lap model on the 10 Hz telemetry)")
    sess = os.path.join(d, "CAM")
    if not os.path.exists(os.path.join(sess, "phases.jsonl")) or not (os.path.exists(os.path.join(sess, "tel.jsonl")) or os.path.exists(os.path.join(sess, "tel.jsonl.gz"))):
        print("   no camera session")
        return
    phases = [p for p in jl(os.path.join(sess, "phases.jsonl")) if p.get("block") == "E111-F05"]
    tel = []
    for x in jl(os.path.join(sess, "tel.jsonl")):
        try:
            tel.append((int(x["t_ms"]), (x.get("temp_c") or {}).get("minshire", [None])[0], x.get("board_w")))
        except (KeyError, TypeError, ValueError):
            pass
    proto = json.load(open(os.path.join(sess, "protocol.json")))
    nph = 2 * int(next(b for b in proto["blocks"] if (b.get("id") or b.get("name")) == "E111-F05").get("n_per_arm") or 1)
    by = {}
    for p in phases:
        by.setdefault(int(p["cycle"]), []).append(p)
    laps = []
    for c in sorted(by):
        ps = by[c]
        if any(p.get("warmup") for p in ps) or len(ps) != nph:
            continue
        laps.append((min(p["planned_start_ms"] for p in ps), max(p["planned_end_ms"] for p in ps)))
    if not laps:
        print("   no analysed laps")
        return
    a0, a1 = laps[0][0], laps[-1][1]
    xs = [x for x in tel if a0 <= x[0] < a1 and x[1] is not None and x[2] is not None]
    t = np.array([x[0] for x in xs], float)
    T0 = laps[0][1] - laps[0][0]
    ph = 2 * math.pi * (t - a0) / T0
    tt = (t - a0) / (a1 - a0)
    X = np.column_stack([np.ones_like(t), tt, tt ** 2, np.sin(ph), -np.cos(ph)])
    out = {}
    for name, idx in (("die", 1), ("W", 2)):
        y = np.array([x[idx] for x in xs], float)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        out[name] = complex(beta[3], beta[4])
    H = out["die"] / out["W"]
    lag = math.degrees(math.atan2(H.imag, H.real))
    print(f"   {len(laps)} laps of {T0 / 1000:.0f} s: die fundamental {abs(out['die']):.3f} C, board {abs(out['W']):.3f} W, "
          f"H_die {abs(H):.3f} C/W at a lag of {lag:.1f} deg")
    C = res.get("C", {})
    if C.get("lag_0p005"):
        print(f"   the camera at the same frequency: {C['lag_0p005']['deg']} +- {C['lag_0p005']['se']} deg")


def refit(d, res):
    print("\n4. REFIT: E73's 14 points with E111's camera points under their own gain")
    try:
        from scipy.optimize import least_squares
    except ImportError:
        print("   scipy not available")
        return
    root = os.environ.get("E111_ROOT") or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    f73 = json.load(open(os.path.join(root, "docs/reports/data/2026-10-27-e73-camera-frequencies/analysis/fit.json")))
    pts = [(p["f_hz"], p["H_re_corr"], p["H_im_corr"], p["se_corr"] / math.sqrt(2), 0) for p in f73["points"] if p.get("included")]
    L = os.path.join(d, "CAM-ANA", "lockin.json")
    if not os.path.exists(L):
        print("   no lockin.json")
        return
    b = json.load(open(L))["blocks"]["E111-F05"]
    new = []
    for k, row in (b.get("transfer") or {}).items():
        sb = (row.get("board_w") or 0) / (row.get("se_board_w") or 1e9)
        if sb >= 5 and row.get("H_re") is not None:
            new.append((row["f_hz"], row["H_re"], row["H_im"], row["se_H"] / math.sqrt(2), 1))
    print(f"   E111 points kept (board >= 5 SE): {[(round(f, 4)) for f, *_ in new]}")
    allp = pts + new
    f = np.array([p[0] for p in allp]); re = np.array([p[1] for p in allp]); im = np.array([p[2] for p in allp])
    sg = np.array([p[3] for p in allp]); grp = np.array([p[4] for p in allp])

    def model(name, th, ff):
        s = 2j * math.pi * ff
        if name == "P1D":
            G, tau, Td = th[:3]; H = G / (1 + s * tau) * np.exp(-s * Td)
        elif name == "P2":
            G, t1, t2 = th[:3]; H = G / ((1 + s * t1) * (1 + s * t2))
        elif name == "P1D+slow":
            G, tau, Td, w, t3 = th[:5]; H = G * ((1 - w) / (1 + s * tau) + w / (1 + s * t3)) * np.exp(-s * Td)
        else:
            G, tau, Td, td = th[:4]; H = G / (1 + s * tau) / np.sqrt(1 + s * td) * np.exp(-s * Td)
        return np.conj(H)

    starts = {"P1D": [250, 16, 1], "P2": [250, 15, 1], "P1D+slow": [250, 14, 1, 0.3, 150], "P1D+diff": [250, 14, 0.8, 30]}
    bounds = {"P1D": ([0, 0.1, 0], [5000, 200, 10]), "P2": ([0, 0.1, 0.01], [5000, 200, 100]),
              "P1D+slow": ([0, 0.1, 0, 0, 20], [20000, 200, 10, 1, 5000]), "P1D+diff": ([0, 0.1, 0, 0.01], [20000, 200, 10, 50000])}
    for name in starts:
        lo = bounds[name][0] + [0.2]
        hi = bounds[name][1] + [5.0]

        def resid(th):
            g = np.where(grp == 1, th[-1], 1.0)
            H = model(name, th, f) * g
            return np.concatenate([(H.real - re) / sg, (H.imag - im) / sg])
        best = None
        for k in range(30):
            x0 = np.array(starts[name] + [1.0], float)
            if k:
                x0 = x0 * np.exp(np.random.default_rng(k).normal(0, 0.5, len(x0)))
            x0 = np.clip(x0, np.array(lo) + 1e-6, np.array(hi) - 1e-6)
            r = least_squares(resid, x0, bounds=(lo, hi))
            if best is None or r.cost < best.cost:
                best = r
        chi2 = 2 * best.cost
        npar = len(best.x)
        H5 = model(name, best.x, np.array([0.005]))[0]
        print(f"   {name:9s} chi2 {chi2:6.2f} on {2 * len(f) - npar} dof, AIC {chi2 + 2 * npar:6.2f}, params {np.round(best.x, 3)}, "
              f"lag at 0.005 Hz {math.degrees(math.atan2(H5.imag, H5.real)):.1f} deg")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--fig")
    a = ap.parse_args()
    res = json.load(open(os.path.join(a.data, "results.json")))
    room(a.data, res)
    holds(a.data, res, a.fig)
    die_lockin(a.data, res)
    refit(a.data, res)
    drift_check(a.data, res)


if __name__ == "__main__":
    main()
