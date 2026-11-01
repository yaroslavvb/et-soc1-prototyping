#!/usr/bin/env python3
"""E89, POST HOC and descriptive only (not registered; it changes nothing and scores nothing): what the per-sensor
reading looks like. Run from the data directory:
    python3 posthoc_e89.py aifoundry3/e89/p8910 aifoundry3/e89/p8911 > posthoc.txt

  - per-sensor noise at idle: the SD of each sensor's raw code over the pass's idle bracket (15 s, 10 Hz)
  - the 34-sensor mean's SD at idle (degC), and its resolution (one code of one sensor = 0.0609/34 degC)
  - the firmware integer mean against the codes' mean (the truncation the firmware applies)
  - the die's range over each pass (codes' mean, degC) and the board power range
"""
import gzip
import json
import sys

import numpy as np

G, H, C5 = 57400, 249400, 4096


def c2t(n):
    return (G + H * np.asarray(n, float) / C5 - H / 2) / 1000.0


for d in sys.argv[1:]:
    tel = [json.loads(l) for l in gzip.open(d + "/telemetry.jsonl.gz", "rt") if l.startswith("{")]
    marks = [json.loads(l) for l in open(d + "/marks.jsonl")]
    t = np.array([r["t_ms"] / 1000 for r in tel])
    codes = np.array([r["pvt"]["c"] if len(r.get("pvt", {}).get("c", [])) == 34 else [np.nan] * 34 for r in tel], float)
    fw = np.array([r["temp_c"]["minshire"][0] for r in tel], float)
    bw = np.array([r.get("board_w", np.nan) for r in tel], float)
    idle = [m for m in marks if m["kind"] == "idle"][0]
    mi = (t >= idle["t_start_ms"] / 1000) & (t < idle["t_end_ms"] / 1000)
    ci = codes[mi]
    sd = np.nanstd(ci, axis=0, ddof=1)
    mean34 = c2t(codes).mean(axis=1)
    print(f"== {d}")
    print(f"  idle bracket: {mi.sum()} samples; per-sensor code SD median {np.nanmedian(sd):.2f}, range {np.nanmin(sd):.2f}-{np.nanmax(sd):.2f} codes "
          f"({np.nanmedian(sd) * 0.0609:.3f} degC median); distinct codes per sensor median {np.median([len(np.unique(ci[:, s][np.isfinite(ci[:, s])])) for s in range(34)]):.0f}")
    print(f"  34-sensor mean at idle: SD {np.nanstd(mean34[mi], ddof=1):.4f} degC over {mi.sum()} samples; resolution of the mean 0.0609/34 = {0.0609 / 34:.4f} degC")
    print(f"  idle per-sensor spread: sensor means {c2t(np.nanmean(ci, axis=0)).min():.2f}-{c2t(np.nanmean(ci, axis=0)).max():.2f} degC")
    ok = np.isfinite(mean34)
    print(f"  codes' mean minus the firmware integer mean: median {np.median(mean34[ok] - fw[ok]):.3f} degC (range {np.min(mean34[ok] - fw[ok]):.3f}-{np.max(mean34[ok] - fw[ok]):.3f})")
    print(f"  die (codes' mean) over the pass: {np.nanmin(mean34):.2f}-{np.nanmax(mean34):.2f} degC; firmware {np.nanmin(fw):.0f}-{np.nanmax(fw):.0f}; board {np.nanmin(bw):.2f}-{np.nanmax(bw):.2f} W")
    dt = np.diff(t)
    print(f"  sampling: {len(t)} lines over {t[-1] - t[0]:.0f} s, median interval {np.median(dt) * 1000:.0f} ms, max {np.max(dt) * 1000:.0f} ms; "
          f"lines with an err field {sum(1 for r in tel if 'err' in r)}")


# ---- POST HOC 2: is the reference's lower heat per board watt the share of board power that reaches the die? ----
# The registered reducer's own block fit, applied to the SP's minion-rail power (sp.minion_w[0], the PMIC's running
# average, tau ~1 s: at 1/60 Hz it lags ~6 deg and loses 0.5% of amplitude, ignored) and to the board power; the
# heat per watt of the minion rail, r on it, the rail's share of the board fundamental, and each block's mean die.
import importlib.util, math, os
_spec = importlib.util.spec_from_file_location("red", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                               "../../../../tools/claims-v3/e89/reduce_e89.py"))
red = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(red)
rows = {}
for d in sys.argv[1:]:
    tel = [json.loads(l) for l in gzip.open(d + "/telemetry.jsonl.gz", "rt") if l.startswith("{")]
    marks = [json.loads(l) for l in open(d + "/marks.jsonl")]
    t = np.array([r["t_ms"] / 1000 for r in tel])
    P = np.array([r.get("board_w", np.nan) for r in tel], float)
    Pm = np.array([(r.get("sp") or {}).get("minion_w", [np.nan])[0] for r in tel], float)
    Ps = np.array([(r.get("sp") or {}).get("sram_w", [np.nan])[0] for r in tel], float)
    Pn = np.array([(r.get("sp") or {}).get("noc_w", [np.nan])[0] for r in tel], float)
    T = np.array([c2t(r["pvt"]["c"]).mean() for r in tel], float)
    for mk in [m for m in marks if m["kind"] == "block"]:
        b = mk["block"]
        hk = sorted([h for h in marks if h["kind"] == "half" and h["block"] == b and h["role"] == "K"
                     and mk["t_start_ms"] - 1000 <= h["t_start_ms"] <= mk["t_end_ms"] + 1000], key=lambda h: h["half"])
        t0 = hk[0]["t_start_ms"] / 1000
        per = 2 * mk["half_s"]
        fT, fP, fM, fS, fN = (red.block_fit(t, y, t0, per, len(hk)) for y in (T, P, Pm, Ps, Pn))
        m = (t >= t0) & (t < t0 + per * len(hk))
        for c in range(len(hk)):
            rows.setdefault(b, []).append({"Hb": fT[c] / fP[c], "Hm": fT[c] / fM[c], "share_m": abs(fM[c]) / abs(fP[c]),
                                           "share_s": abs(fS[c]) / abs(fP[c]), "share_n": abs(fN[c]) / abs(fP[c]),
                                           "Tdc": float(np.nanmean(T[m]))})
phi = np.angle(np.mean([r["Hm"] for r in rows["f32randn"]]))
phib = np.angle(np.mean([r["Hb"] for r in rows["f32randn"]]))
ref_m = np.mean([(r["Hm"] * np.exp(-1j * phi)).real for r in rows["f32randn"]])
print()
print("== POST HOC 2: heat per W of the minion rail (SP running average), on the reference's phase")
print("| block | H per board W | H per minion-rail W | r on the minion rail [95%] | minion-rail share of the board fundamental | SRAM share | NoC share | mean die during the block (degC) |")
print("|---|---|---|---|---|---|---|---|")
for b in ["i8full", "i8gauss", "i8small", "i8sp50", "i8neg1", "i8zero", "f32ones", "f32randn"]:
    R_ = rows[b]
    hb = np.array([(r["Hb"] * np.exp(-1j * phib)).real for r in R_])
    hm = np.array([(r["Hm"] * np.exp(-1j * phi)).real for r in R_])
    rm = hm / ref_m
    n = len(rm)
    tq = red.t975(n - 1)
    sh = np.array([r["share_m"] for r in R_])
    print(f"| {b} | {hb.mean():.4f} | {hm.mean():.4f} | {rm.mean():.3f} [{rm.mean() - tq * rm.std(ddof=1) / math.sqrt(n):.3f}, {rm.mean() + tq * rm.std(ddof=1) / math.sqrt(n):.3f}] "
          f"| {sh.mean():.3f} | {np.mean([r['share_s'] for r in R_]):.3f} | {np.mean([r['share_n'] for r in R_]):.3f} | {np.mean([r['Tdc'] for r in R_]):.2f} |")
print("(the r interval here is over the block's 4 laps, against the reference's mean as a fixed number; descriptive)")
