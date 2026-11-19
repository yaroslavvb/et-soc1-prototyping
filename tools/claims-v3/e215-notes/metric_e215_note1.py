#!/usr/bin/env python3
"""E215, dated note 1, section 3 (Q224, lane fix-e215, Thu 19 Nov 2026, before any E215 datum): the bands' basis metric against the rules'
metric, re-derived from MM1-v3.1's landed per-point held-out tables. Standard library only; reads only; prints the table of the note.

    /usr/bin/python3 -I -B tools/claims-v3/e215-notes/metric_e215_note1.py

MM1-v3.1's held-out record defines its error as forecast / measured - 1 (the basis of E215's bands, B1 and B2); E215's rules test
|measured / forecast - 1|. Over tools/matmul/mm1/v3.1/out/points_time_v31.csv and points_energy_v31.csv (MM1-v3.1's land 2c971828), leave one
experiment out, no configuration twin: the rms of each metric, and the share of the held-out points inside each registered band under each
metric (T1 10% on both cards; E1 13% on aifoundry3 card 0, 14% on aifoundry1 card 1; E3 6% and 5%), per card and over every point. E1 reads W
over idle given t (the J ratio given the measured seconds is the W ratio), on points measured at 3 W or more over idle (the rules' relative set;
under 3 W E1 reads watts); E3 reads the J with the card at rest given t, (W over idle + the row's rest) given t, on every point (E3 stays
relative). SPDX-License-Identifier: Apache-2.0
"""
import csv
import math
import os

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(REPO, "tools", "matmul", "mm1", "v3.1", "out")
CARDS = (None, "aifoundry3 card 0", "aifoundry1 card 1")
BANDS = {"T1": {None: 0.10, "aifoundry3 card 0": 0.10, "aifoundry1 card 1": 0.10},
         "E1": {None: None, "aifoundry3 card 0": 0.13, "aifoundry1 card 1": 0.14},
         "E3": {None: None, "aifoundry3 card 0": 0.06, "aifoundry1 card 1": 0.05}}


def rms(v):
    return 100.0 * math.sqrt(sum(x * x for x in v) / len(v)) if v else float("nan")


def share(pairs, band):
    if band is None or not pairs:
        return "-", "-"
    rule = sum(1 for f, m in pairs if abs(m / f - 1) <= band) / len(pairs)
    basis = sum(1 for f, m in pairs if abs(f / m - 1) <= band) / len(pairs)
    return f"{rule:.3f}", f"{basis:.3f}"


def line(q, c, p, band):
    s = share(p, band)
    tail = f" (band {band:.0%})" if band else ""
    return (f"| {q} | {c or 'every point'} | {len(p)} | {rms([f / m - 1 for f, m in p]):.3f} | {rms([m / f - 1 for f, m in p]):.3f} | {s[0]} | "
            f"{s[1]}{tail} |")


def main():
    T = [r for r in csv.DictReader(open(os.path.join(OUT, "points_time_v31.csv"), newline="")) if r["twin_LOEO"] == "0"]
    E = [r for r in csv.DictReader(open(os.path.join(OUT, "points_energy_v31.csv"), newline=""))
         if r["twin_LOEO"] == "0" and r["v31_LOEO_wg"] not in ("", "nan") and r["w_meas"] not in ("", "nan")]
    print("| quantity | card | n | rms of forecast / measured - 1, % (the bands' basis) | rms of measured / forecast - 1, % (the rules) "
          "| inside the band, the rules' metric | inside the band, the basis's metric |")
    print("|---|---|---|---|---|---|---|")
    for c in CARDS:
        p = [(float(r["v31_LOEO"]), float(r["meas_T_x_f"])) for r in T if c is None or r["card"] == c]
        print(line("T1: cycles an op, the wall", c, p, BANDS["T1"][c]))
    for c in CARDS:
        p = [(float(r["v31_LOEO_wg"]), float(r["w_meas"])) for r in E if c is None or r["card"] == c]
        print(line("E1: W over idle given t (>= 3 W)", c, [(f, m) for f, m in p if m >= 3 and f > 0], BANDS["E1"][c]))
    for c in CARDS:
        p = [(float(r["v31_LOEO_wg"]) + float(r["idle_w"]), float(r["w_meas"]) + float(r["idle_w"])) for r in E
             if (c is None or r["card"] == c) and r["idle_w"] not in ("", "nan")]
        print(line("E3: J at rest given t", c, p, BANDS["E3"][c]))
    print(f"arm B's T1 and T3 band: 2 x max(4.723, 4.998) = {2 * max(4.723, 4.998):.3f} %, rounded up to a whole percent: 10%")


if __name__ == "__main__":
    main()
