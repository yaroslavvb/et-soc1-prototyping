#!/usr/bin/env python3
"""The 600 against 800 MHz operating points of the cool-start runs: vf.json for why-low-power and the DVFS report.

    D=docs/reports/data/2026-09-21-horace-aifoundry2
    python3 tools/ettelem/build_vf.py --cold $D/cold1 $D/cold2 --ablation $D/ablation.json --out $D/vf.json

From a cool die (62-64 C) the governor runs a kernel at 800 MHz / 0.62 V until the die reads above 65 C, then
hunts between 600, 700 and 800 MHz. Board power refreshes every ~133 ms and lags the clock field by 0.1-0.3 s,
so a reading is credited to a clock as follows (runs are the kernel processes in runs.jsonl, each starting with
launch -1):

  X800        the highest board reading from the first 800 MHz sample of a run of pattern X to 0.3 s after its
              last 800 MHz sample, highest over every run of X in both sessions. For random data the 800 MHz
              power shows only after the clock field has already left 800 MHz.
  X600        the mean board reading over seconds 2-7 of the runs of X, on samples at 600 MHz that the clock had
              held for at least 0.3 s.
  idle800     the mean board reading after a zeros run's last launch, while the governor still held 800 MHz
              (the first 800 MHz stretch starting within 1 s of the end), from 0.3 s after the clock reached 800.
  idle600     the mean board reading 0.5-2.5 s after each run's last launch (and before the next run), on
              samples at 600 MHz held for at least 0.3 s.
  zeros600_dyn  the 80 C ablation's fp32 zeros switching watts (from a cool start zeros stayed at 800 MHz).

Voltages are analyze_dvfs.py's operating points (the median on-die reading while a kernel runs).
"""
import argparse
import gzip
import importlib.util
import json
import os

import numpy as np

LAG_MS = 300
COLORS = {"zeros": "var(--c1)", "ones": "var(--c4)", "randn": "var(--bad)"}


def jsonl(path):
    op = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    return [json.loads(l) for l in op if l.strip().startswith("{")]


def session(d):
    tel = jsonl(os.path.join(d, "telemetry.jsonl.gz"))
    tms = np.array([s["t_ms"] for s in tel], dtype=np.int64)
    f = np.array([s["mhz"]["minion"] for s in tel])
    held = np.zeros(len(tms), dtype=np.int64)   # ms since the clock field last changed
    j = 0
    for i in range(len(tms)):
        if i and f[i] != f[i - 1]:
            j = i
        held[i] = tms[i] - tms[j]
    procs = []
    for r in jsonl(os.path.join(d, "runs.jsonl")):
        if r["launch"] == -1:
            procs.append([])
        procs[-1].append(r)
    return {"name": os.path.basename(os.path.normpath(d)), "tms": tms, "f": f, "held": held,
            "w": np.array([s["board_w"] for s in tel]), "T": np.array([s["temp_c"]["minshire"][0] for s in tel]),
            "runs": [(p[0]["values"], p[0]["t_start_ms"], p[-1]["t_end_ms"],
                      procs[k + 1][0]["t_start_ms"] if k + 1 < len(procs) else None) for k, p in enumerate(procs)]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cold", nargs="+", required=True)
    ap.add_argument("--ablation", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    S = [session(d) for d in a.cold]

    peak, s600, idle800, idle600 = {}, {}, [], []
    for s in S:
        tms, f, held, w, T = s["tms"], s["f"], s["held"], s["w"], s["T"]
        for k, (v, t0, t1, nxt) in enumerate(s["runs"]):
            inrun = (tms >= t0) & (tms <= t1)
            i800 = np.where(inrun & (f == 800))[0]
            if len(i800):
                sel = np.where((tms >= tms[i800[0]]) & (tms <= tms[i800[-1]] + LAG_MS))[0]
                j = sel[int(np.argmax(w[sel]))]
                if v not in peak or w[j] > peak[v]["w"]:
                    peak[v] = {"w": float(w[j]), "session": s["name"], "run": k, "t_s": round((tms[j] - t0) / 1000, 2),
                               "die_c": int(T[j]), "mhz_at_reading": int(f[j])}
            sel = (tms >= t0 + 2000) & (tms <= min(t0 + 7000, t1)) & (f == 600) & (held >= LAG_MS)
            s600.setdefault(v, []).extend(w[sel].tolist())
            end = nxt if nxt is not None else tms[-1] + 1
            sel = (tms >= t1 + 500) & (tms <= min(t1 + 2500, end - 1)) & (f == 600) & (held >= LAG_MS)
            idle600.extend(zip(w[sel].tolist(), T[sel].tolist()))
            if v == "zeros":
                # the first 800 MHz stretch that starts within 1 s of the last launch's end (the governor may step
                # up once more after the kernel has finished), until the clock leaves 800 MHz
                seen = False
                for i in np.where((tms > t1) & (tms < end))[0]:
                    if f[i] != 800:
                        if seen or tms[i] > t1 + 1000:
                            break
                        continue
                    seen = True
                    if held[i] >= LAG_MS:
                        idle800.append((float(w[i]), int(T[i])))

    ab = json.load(open(a.ablation))["configs"]
    spec = importlib.util.spec_from_file_location("analyze_dvfs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "analyze_dvfs.py"))
    dv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dv)
    volts, _ = dv.volts(a.cold)
    r1 = lambda x: round(float(x), 1)  # noqa: E731
    i8w, i8T = [x[0] for x in idle800], [x[1] for x in idle800]
    i6w, i6T = [x[0] for x in idle600], [x[1] for x in idle600]
    out = {
        "note": f"from the cool-start runs ({', '.join(s['name'] for s in S)}): the governor's 800 MHz / {volts[800]:.2f} V point "
                f"against 600 MHz / {volts[600]:.2f} V at {min(i6T + [p['die_c'] for p in peak.values()])} to "
                f"{max(i6T + [p['die_c'] for p in peak.values()])} C; built by tools/ettelem/build_vf.py",
        "idle600": r1(np.mean(i6w)), "idle800": r1(np.mean(i8w)),
        "zeros800": r1(peak["zeros"]["w"]), "zeros600_dyn": r1(ab["fp32_zeros"]["dyn"]),
        "ones800": r1(peak["ones"]["w"]), "ones600": r1(np.mean(s600["ones"])),
        "randn800_peak": r1(peak["randn"]["w"]), "randn600": r1(np.mean(s600["randn"])),
        "points": [[volts[800], r1(peak[v]["w"]), f"{lab}, 800 MHz, {peak[v]['die_c']} °C{extra}", COLORS[v]]
                   for v, lab, extra in (("zeros", "zeros", ""), ("ones", "ones", ""),
                                         ("randn", "random fp32", ", peak before the governor stepped down"))],
        "peaks_at": peak,
        "samples": {"idle600": len(i6w), "idle800": len(i8w), "ones600": len(s600["ones"]), "randn600": len(s600["randn"])},
        "die_c": {"idle600": [min(i6T), max(i6T)], "idle800": [min(i8T), max(i8T)]},
        "rules": {
            "X800": "highest board reading from the first 800 MHz sample of a run to 0.3 s after its last one, over every run of X",
            "X600": "mean board reading over seconds 2-7 of the runs of X, at 600 MHz held for at least 0.3 s",
            "idle800": "mean board reading after a zeros run's last launch while the clock stays at 800 MHz, from 0.3 s after it reached 800",
            "idle600": "mean board reading 0.5-2.5 s after each run's last launch (before the next run), at 600 MHz held for at least 0.3 s",
            "zeros600_dyn": "the 80 C ablation's fp32 zeros switching watts (analyze_ablation.py dyn): from a cool start zeros stayed at 800 MHz",
        },
    }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"800 MHz: zeros {out['zeros800']} W, ones {out['ones800']} W, random {out['randn800_peak']} W (peak); idle {out['idle800']} W")
    print(f"600 MHz: ones {out['ones600']} W, random {out['randn600']} W; idle {out['idle600']} W; zeros switching (80 C) {out['zeros600_dyn']} W")
    for v, p in peak.items():
        print(f"  {v} 800 MHz reading: {p['session']} run {p['run']} at {p['t_s']} s, {p['die_c']} C, clock field {p['mhz_at_reading']} MHz")


if __name__ == "__main__":
    main()
