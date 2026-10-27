#!/usr/bin/env python3
"""The leakage slope this card actually shows, measured on E66 pass 11's cooling (Q128(b) correction pass).

The registered idle rule (reduce.py rule F / flip_thermal_model.py step 2a): no launch within 4.5 s, the first
20 s of the pass dropped, mhz.minion == 600. A straight line of board power against die temperature over a
band is what E68's correction term `p80 = p_raw - k*(t_win - t_launch)` needs.

E71 (Q129, 27 Oct 2026) added four **default-preserving** options so the same fit runs on the second card:

    python3 tools/claims-v3/idle/idle_slope.py [--data <idle dir>] [--bands 58-62,51-58] [--passes p13,p14]
                                              [--json <path>]

With no options every line of the output is what it was before: aifoundry2's idle directory, the bands
51-58, 51-67, 49-70, 51-70, every pass directory in name order. `--json` additionally writes the per-pass,
per-band fits and the per-degree dwell (seconds of kept idle samples per whole degree, the sampler's 10 Hz
period times the count) so a reduction can read them instead of the printed text. Nothing about the filter or
the fit changes: the rows that reach `np.polyfit` are selected by exactly the same three rules.
"""
import argparse
import gzip
import json
import os

import numpy as np

D = os.path.expanduser("~/claude/et-soc1-prototyping/build/claims-v3/aifoundry2/idle")
BANDS = ((51, 58), (51, 67), (49, 70), (51, 70))
SAMPLE_S = 0.1          # the sampler's period: --every-ms 100, block.sh "sampler_every_ms":100


def load(p):
    cool = None
    mk = os.path.join(p, "marks.jsonl")
    if not os.path.exists(mk):
        return None
    for l in open(mk):
        m = json.loads(l)
        if m["ev"] == "cool_start":
            cool = m["t_ms"]
    if cool is None:
        return None
    # a finished pass is gzipped; a killed one left .jsonl; a running one is still writing .jsonl.raw
    op = None
    for name in ("telemetry.jsonl.gz", "telemetry.jsonl", "telemetry.jsonl.raw"):
        f = os.path.join(p, name)
        if os.path.exists(f):
            op = (lambda f=f: gzip.open(f, "rt")) if f.endswith(".gz") else (lambda f=f: open(f))
            break
    if op is None:
        return None
    rows = []
    with op() as fh:
        for l in fh:
            l = l.strip()
            if not l.startswith("{") or not l.endswith("}"):
                continue
            try:
                d = json.loads(l)
            except Exception:
                continue
            t = d.get("t_ms")
            # rule F: 4.5 s after the last burst (cool_start is the last burst's end) and 20 s of settling
            if t is None or t < cool + 20000:
                continue
            if d.get("mhz", {}).get("minion") != 600:
                continue
            rows.append((d["temp_c"]["minshire"][0], d["board_w"]))
    return np.array(rows) if rows else None


def parse_bands(s):
    out = []
    for part in s.split(","):
        lo, _, hi = part.strip().partition("-")
        out.append((int(lo), int(hi)))
    return tuple(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=D, help="the idle directory holding the pass directories (default: aifoundry2's)")
    ap.add_argument("--bands", default=None, help="comma-separated lo-hi degree bands (default: 51-58,51-67,49-70,51-70)")
    ap.add_argument("--passes", default=None, help="comma-separated pass directory names; default every p* directory")
    ap.add_argument("--json", default=None, help="also write the per-pass fits and per-degree dwell here")
    a = ap.parse_args()
    bands = BANDS if a.bands is None else parse_bands(a.bands)
    want = None if a.passes is None else {x.strip() for x in a.passes.split(",") if x.strip()}
    out = {"data": a.data, "bands": [list(b) for b in bands], "passes": {}}
    for name in sorted(os.listdir(a.data)):
        p = os.path.join(a.data, name)
        if not os.path.isdir(p) or not name.startswith("p"):
            continue
        if want is not None and name not in want:
            continue
        arr = load(p)
        if arr is None or len(arr) < 100:
            print(f"{name}: no usable cooling")
            out["passes"][name] = {"usable": False}
            continue
        T, W = arr[:, 0], arr[:, 1]
        rec = {"usable": True, "n": int(len(T)), "t_min": float(T.min()), "t_max": float(T.max()), "fits": {}}
        print(f"\n=== {name}: {len(T)} idle samples at 600 MHz, {T.min():.0f}-{T.max():.0f} C ===")
        for lo, hi in bands:
            m = (T >= lo) & (T <= hi)
            if m.sum() < 50 or len(set(T[m])) < 3:
                print(f"  {lo}-{hi} C: too few ({m.sum()})")
                rec["fits"][f"{lo}-{hi}"] = {"ok": False, "n": int(m.sum())}
                continue
            k, b = np.polyfit(T[m], W[m], 1)
            r = W[m] - (k * T[m] + b)
            rms = float(np.sqrt(np.mean(r ** 2)))
            print(f"  {lo:2d}-{hi:2d} C: slope {k:7.4f} W/C   intercept {b:8.3f} W   "
                  f"rms {rms:.4f} W   n {m.sum():6d}   spanC {T[m].max()-T[m].min():.0f}")
            rec["fits"][f"{lo}-{hi}"] = {"ok": True, "slope_w_per_c": float(k), "intercept_w": float(b),
                                         "rms_w": rms, "n": int(m.sum()),
                                         "span_c": float(T[m].max() - T[m].min())}
        # per-degree means, the shape the exponential law is fitted to
        print("   per-degree mean board W:",
              " ".join(f"{int(t)}:{W[T == t].mean():.2f}" for t in sorted(set(T), reverse=True)))
        rec["per_degree_w"] = {str(int(t)): float(W[T == t].mean()) for t in sorted(set(T))}
        rec["per_degree_s"] = {str(int(t)): round(float((T == t).sum()) * SAMPLE_S, 1) for t in sorted(set(T))}
        out["passes"][name] = rec
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
