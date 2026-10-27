#!/usr/bin/env python3
"""Q129: E63's per-flip prices re-reduced with a leakage correction on the paired board step.

E63's price is board_step_w / flips_per_s, and board_step_w is a PAIRED same-lap difference: the median
board power in arm 0's steady window minus arm 1's (lockin_hlc.steady_steps, 2.0 s after a launch's start
to 0.3 s before its end). The two windows sit ~10 s apart in one 20 s lap and the die is hotter in the
hot arm, so part of the step is leakage. The correction is the same arithmetic E68 and E60 use:

    step_corrected = step - k * (T_arm0 - T_arm1)

with T the minion-shire reading in the SAME windows the medians are taken in, and k the card's idle
leakage slope. Reads only committed session records (launches.jsonl, tel.jsonl.gz) and lockin.json, and
identifies the analysed lap set by matching its own recomputed steps to lockin.json's per_lap list.

WHICH TEMPERATURE VARIABLE (raised by Q129's verifier, 27 Oct). `temp_c.minshire` is a list of three
integer-degree readings. E63's own analysis (`lockin_hlc.py`) reports their MEAN as the die column, but
the slope k this file multiplies by is defined on a SINGLE sensor: E66's `idle_slope.py` and the
registered `reduce_hl.py` both read `temp_c.minshire[0]`. A slope measured against sensor 0 times a dT
measured on the mean of three is not the leakage difference unless the die is isothermal, which in a
busy window it is not. So BOTH are computed for every lap and every slope:

  * `dT_c_mean` / `slopes`          — sensor 0, the variable k is defined on. THE PRIMARY COLUMN.
  * `dT_c_mean_s0` ... the fields are named by their sensor; `sensor` says which one `slopes` used, and
    `slopes_alt` carries the other, so the two can be read side by side.

The difference is a labelled sensitivity, not a correction to a correction: see the README.

  python3 posthoc_e63.py <session dir> <lockin.json> --out out.json [--slopes ...] [--die-sensor 0|mean]
"""
import argparse
import gzip
import json
import math
import os

import numpy as np

STEADY_FROM_S, STEADY_TO_END_S = 2.0, 0.3     # lockin_hlc.py
CYCLES_PER_OP = 546.0
FLIPS_PER_OP = {"E63-TOP": 94208, "E63-TOP2": 94208, "E63-MID": 32768, "E63-NULL": 0}


def read_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    op = gzip.open if path.endswith(".gz") else open
    out = []
    for line in op(path, "rt"):
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def tel_samples(path):
    """(host epoch s, board W, die mean C, minion MHz, die sensor-0 C).

    The first four columns are exactly `lockin_hlc.tel_samples`; the fifth is `minshire[0]`, the single
    sensor E66's slope and the registered reducer are both defined on."""
    rows = []
    for r in read_jsonl(path):
        L = r.get("line", r)
        if isinstance(L, str):
            try:
                L = json.loads(L)
            except ValueError:
                continue
        try:
            t = float(L.get("t_ms", r.get("host_ms"))) / 1000.0
            bw = float(L["board_w"])
        except (TypeError, ValueError, KeyError):
            continue
        die = mhz = die0 = np.nan
        try:
            ms = L["temp_c"]["minshire"]
            die = float(np.mean(ms)) if isinstance(ms, list) else float(ms)
            die0 = float(ms[0]) if isinstance(ms, list) else float(ms)
        except (KeyError, TypeError, ValueError, IndexError):
            pass
        try:
            mhz = float(L["mhz"]["minion"])
        except (KeyError, TypeError, ValueError):
            pass
        rows.append((t, bw, die, mhz, die0))
    return np.array(rows, float)


def per_cycle(launches, tel, block):
    """Per cycle: the paired board step, and the arms' die difference in BOTH temperature variables
    (column 2 = the mean of the three minion-shire sensors, column 4 = sensor 0 alone)."""
    by = {}
    for L in launches:
        if L.get("block") == block:
            by.setdefault(int(L["cycle"]), {})[int(L["phase"])] = L
    ts = tel[:, 0]
    out = {}
    for c, arms in sorted(by.items()):
        w, d, d0, n = [], [], [], []
        for ph in (0, 1):
            L = arms.get(ph)
            if not L:
                w.append(np.nan); d.append(np.nan); d0.append(np.nan); n.append(0); continue
            a = L["t_start_ms"] / 1000.0 + STEADY_FROM_S
            b = L["t_end_ms"] / 1000.0 - STEADY_TO_END_S
            m = (ts >= a) & (ts <= b)
            w.append(float(np.median(tel[m, 1])) if m.any() else np.nan)
            for col, dst in ((2, d), (4, d0)):
                dv = tel[m, col]
                dv = dv[np.isfinite(dv)]
                dst.append(float(dv.mean()) if len(dv) else np.nan)
            n.append(int(m.sum()))
        out[c] = {"step_w": w[0] - w[1], "dT_c": d0[0] - d0[1], "dT_c_sensor_mean": d[0] - d[1],
                  "w": w, "die_s0": d0, "die_mean": d, "n": n}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("lockin")
    ap.add_argument("--out", required=True)
    ap.add_argument("--slopes", default="0.0,0.2936,0.327,0.442,1.508")
    ap.add_argument("--die-sensor", default="0", choices=("0", "mean"),
                    help="which minion-shire variable the dT is measured in: 0 = sensor 0, the variable "
                         "E66's slope and the registered reducer are defined on (default); mean = the "
                         "mean of the three, which is E63's own die column. Both are always reported.")
    a = ap.parse_args()
    launches = read_jsonl(os.path.join(a.session, "launches.jsonl"))
    tel = tel_samples(os.path.join(a.session, "tel.jsonl"))
    LK = json.load(open(a.lockin))
    # a repo-relative label, never the absolute path: this file is committed to a public repo
    parts = os.path.normpath(os.path.abspath(a.session)).split(os.sep)
    label = "/".join(parts[-5:]) if len(parts) >= 5 else os.path.basename(a.session)
    res = {"session": label, "tel_samples": int(len(tel)), "die_sensor": a.die_sensor,
           "die_sensor_note": ("the dT in `slopes` is measured on minshire[%s]; `slopes_alt` is the same "
                               "arithmetic on the other variable. E66's slope and reduce_hl.py are both "
                               "defined on minshire[0]; lockin_hlc.py's die column is the mean of three."
                               % a.die_sensor),
           "blocks": {}}
    for block, r in LK["blocks"].items():
        if "per_lap" not in r:
            continue
        committed = [round(x, 6) for x in r["per_lap"]["board_step_w"]]
        pc = per_cycle(launches, tel, block)
        # identify the analysed lap set: the cycles whose recomputed step matches the committed list, in order
        matched, used = [], set()
        for want in committed:
            hit = None
            for c, v in pc.items():
                if c in used or not np.isfinite(v["step_w"]):
                    continue
                if abs(v["step_w"] - want) < 1e-6:
                    hit = c
                    break
            if hit is not None:
                used.add(hit)
                matched.append(hit)
        ok = len(matched) == len(committed)
        laps = matched if ok else [c for c in pc if np.isfinite(pc[c]["step_w"])]
        steps = np.array([pc[c]["step_w"] for c in laps], float)
        dT_s0 = np.array([pc[c]["dT_c"] for c in laps], float)
        dT_mean = np.array([pc[c]["dT_c_sensor_mean"] for c in laps], float)
        dTs, dTs_alt = ((dT_s0, dT_mean) if a.die_sensor == "0" else (dT_mean, dT_s0))
        minions = max({int(L["harts"]) for L in launches
                       if L.get("block") == block and L.get("harts")} or {0})
        # the clock exactly as summary_hlc.py reads it: median minion MHz over the same steady windows
        mhz = []
        for L in launches:
            if L.get("block") != block or int(L["cycle"]) not in set(laps):
                continue
            A = L["t_start_ms"] / 1000.0 + STEADY_FROM_S
            B = L["t_end_ms"] / 1000.0 - STEADY_TO_END_S
            m = (tel[:, 0] >= A) & (tel[:, 0] <= B)
            v = tel[m, 3]
            mhz += list(v[np.isfinite(v)])
        med_mhz = float(np.median(mhz)) if mhz else 0.0
        flips_s = minions * med_mhz * 1e6 / CYCLES_PER_OP * FLIPS_PER_OP.get(block, 0)
        ent = {"laps_matched_exactly": ok, "n_laps": len(laps), "cycles": laps,
               "minions": minions, "mhz_median": med_mhz, "flips_per_s": flips_s,
               "committed_step_w": r["board_step_w"],
               "die_sensor": a.die_sensor,
               "dT_c_mean": float(np.nanmean(dTs)), "dT_c_sd": float(np.nanstd(dTs)),
               "dT_c_mean_sensor0": float(np.nanmean(dT_s0)), "dT_c_sd_sensor0": float(np.nanstd(dT_s0)),
               "dT_c_mean_sensormean": float(np.nanmean(dT_mean)),
               "dT_c_sd_sensormean": float(np.nanstd(dT_mean)),
               "slopes": {}, "slopes_alt": {}}

        def column(dT):
            col = {}
            for s in a.slopes.split(","):
                k = float(s)
                corr = steps - k * dT
                m = float(np.nanmean(corr))
                sd = float(np.nanstd(corr))
                n = int(np.isfinite(corr).sum())
                col[s] = {"step_w": m, "sd": sd, "se": sd / math.sqrt(max(1, n)), "n": n,
                          "fj_per_flip": (m / flips_s * 1e15) if flips_s else None,
                          "fj_se": (sd / math.sqrt(max(1, n)) / flips_s * 1e15) if flips_s else None}
            return col

        ent["slopes"] = column(dTs)
        ent["slopes_alt"] = column(dTs_alt)
        res["blocks"][block] = ent
    json.dump(res, open(a.out, "w"), indent=1)
    print("# dT on minshire[%s] (E66's slope and reduce_hl.py are defined on minshire[0]; E63's own "
          "die column is the mean of three). Both variables are printed." % a.die_sensor)
    for b, e in res["blocks"].items():
        print("%-10s laps %2d (matched %s)  dT %+.3f +- %.3f C  [sensor0 %+.3f, mean-of-3 %+.3f]   "
              "minions %d at %.0f MHz"
              % (b, e["n_laps"], e["laps_matched_exactly"], e["dT_c_mean"], e["dT_c_sd"],
                 e["dT_c_mean_sensor0"], e["dT_c_mean_sensormean"], e["minions"], e["mhz_median"]))
        for s, v in e["slopes"].items():
            fj = ("%8.2f +- %.2f fJ" % (v["fj_per_flip"], v["fj_se"])) if v["fj_per_flip"] else "       -"
            w = e["slopes_alt"][s]
            alt = ("%8.2f fJ" % w["fj_per_flip"]) if w["fj_per_flip"] else "       -"
            print("    k %-7s step %+8.4f +- %.4f W   %s   [other sensor variable: %s]"
                  % (s, v["step_w"], v["se"], fj, alt))
    return 0


if __name__ == "__main__":
    main()
