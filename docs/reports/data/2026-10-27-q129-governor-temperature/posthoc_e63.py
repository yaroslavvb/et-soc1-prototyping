#!/usr/bin/env python3
"""Q129: E63's per-flip prices re-reduced with a leakage correction on the paired board step.

E63's price is board_step_w / flips_per_s, and board_step_w is a PAIRED same-lap difference: the median
board power in arm 0's steady window minus arm 1's (lockin_hlc.steady_steps, 2.0 s after a launch's start
to 0.3 s before its end). The two windows sit ~10 s apart in one 20 s lap and the die is hotter in the
hot arm, so part of the step is leakage. The correction is the same arithmetic E68 and E60 use:

    step_corrected = step - k * (T_arm0 - T_arm1)

with T the mean minion-shire reading in the SAME windows the medians are taken in, and k the card's idle
leakage slope. Reads only committed session records (launches.jsonl, tel.jsonl.gz) and lockin.json, and
identifies the analysed lap set by matching its own recomputed steps to lockin.json's per_lap list.

  python3 posthoc_e63.py <session dir> <lockin.json> --out out.json [--slopes ...]
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
    """(host epoch s, board W, die mean C, minion MHz), exactly lockin_hlc.tel_samples."""
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
        die = mhz = np.nan
        try:
            ms = L["temp_c"]["minshire"]
            die = float(np.mean(ms)) if isinstance(ms, list) else float(ms)
        except (KeyError, TypeError, ValueError):
            pass
        try:
            mhz = float(L["mhz"]["minion"])
        except (KeyError, TypeError, ValueError):
            pass
        rows.append((t, bw, die, mhz))
    return np.array(rows, float)


def per_cycle(launches, tel, block):
    """Per cycle: (board step W, die step C, n samples) from the two arms' steady windows."""
    by = {}
    for L in launches:
        if L.get("block") == block:
            by.setdefault(int(L["cycle"]), {})[int(L["phase"])] = L
    ts = tel[:, 0]
    out = {}
    for c, arms in sorted(by.items()):
        w, d, n = [], [], []
        for ph in (0, 1):
            L = arms.get(ph)
            if not L:
                w.append(np.nan); d.append(np.nan); n.append(0); continue
            a = L["t_start_ms"] / 1000.0 + STEADY_FROM_S
            b = L["t_end_ms"] / 1000.0 - STEADY_TO_END_S
            m = (ts >= a) & (ts <= b)
            w.append(float(np.median(tel[m, 1])) if m.any() else np.nan)
            dv = tel[m, 2]
            dv = dv[np.isfinite(dv)]
            d.append(float(dv.mean()) if len(dv) else np.nan)
            n.append(int(m.sum()))
        out[c] = {"step_w": w[0] - w[1], "dT_c": d[0] - d[1], "w": w, "die": d, "n": n}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("lockin")
    ap.add_argument("--out", required=True)
    ap.add_argument("--slopes", default="0.0,0.2936,0.327,0.442,1.508")
    a = ap.parse_args()
    launches = read_jsonl(os.path.join(a.session, "launches.jsonl"))
    tel = tel_samples(os.path.join(a.session, "tel.jsonl"))
    LK = json.load(open(a.lockin))
    # a repo-relative label, never the absolute path: this file is committed to a public repo
    parts = os.path.normpath(os.path.abspath(a.session)).split(os.sep)
    label = "/".join(parts[-5:]) if len(parts) >= 5 else os.path.basename(a.session)
    res = {"session": label, "tel_samples": int(len(tel)), "blocks": {}}
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
        dTs = np.array([pc[c]["dT_c"] for c in laps], float)
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
               "committed_step_w": r["board_step_w"], "dT_c_mean": float(np.nanmean(dTs)),
               "dT_c_sd": float(np.nanstd(dTs)), "slopes": {}}
        for s in a.slopes.split(","):
            k = float(s)
            corr = steps - k * dTs
            m = float(np.nanmean(corr))
            sd = float(np.nanstd(corr))
            n = int(np.isfinite(corr).sum())
            ent["slopes"][s] = {"step_w": m, "sd": sd, "se": sd / math.sqrt(max(1, n)), "n": n,
                                "fj_per_flip": (m / flips_s * 1e15) if flips_s else None,
                                "fj_se": (sd / math.sqrt(max(1, n)) / flips_s * 1e15) if flips_s else None}
        res["blocks"][block] = ent
    json.dump(res, open(a.out, "w"), indent=1)
    for b, e in res["blocks"].items():
        print("%-10s laps %2d (matched %s)  dT %+.3f +- %.3f C   minions %d at %.0f MHz"
              % (b, e["n_laps"], e["laps_matched_exactly"], e["dT_c_mean"], e["dT_c_sd"],
                 e["minions"], e["mhz_median"]))
        for s, v in e["slopes"].items():
            fj = ("%8.2f +- %.2f fJ" % (v["fj_per_flip"], v["fj_se"])) if v["fj_per_flip"] else "       -"
            print("    k %-7s step %+8.4f +- %.4f W   %s" % (s, v["step_w"], v["se"], fj))
    return 0


if __name__ == "__main__":
    main()
