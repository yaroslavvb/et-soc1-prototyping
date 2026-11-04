#!/usr/bin/env python3
"""Q141(t2), fix pass of Wed 4 Nov 2026 (../REGISTRATION-step243.md.dated-note.md): the registration's planning look at C's
binade (REGISTRATION-step243.md section 4.2 item 1), re-run per tile and committed, with no new count.

The look as the lane ran it before the registration: each committed point's W of D at M9's frozen float prices
(recount_rule.point_w), grouped by an approximate binade of C, floor(log2(16 n w)), from the op index n and the tile's base word w.
That binade is the look's approximation, not accum.c's C: an F2 registration takes its strata from accum.c (condition 1).
It is reported per tile at the registration's 81 points and, for reference only, at the 243 points committed in 5e1bb309.
It binds nothing: F2's four conditions bind, and F1 stands.

    /usr/bin/python3 -B look_binades.py      # writes look-binades.json beside this file

Standard library plus what recount_rule.py imports. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import math
import os
import struct
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
RRD = os.path.join(REPO, "docs", "reports", "data", "2026-11-04-q140m-m9", "recount-rule")
sys.path.insert(0, RRD)
import recount_rule as RR  # noqa: E402

D = os.path.dirname(HERE)
FILES81 = [os.path.join(RR.M9D, "bench-check", "counts-cal.json"), os.path.join(RRD, "counts-pilot27.json")] + \
    sorted(glob.glob(os.path.join(D, "step81", "counts-cal81-[0-9].json")))
FILES243 = FILES81 + sorted(glob.glob(os.path.join(HERE, "counts-cal243-*-p[12].json")))
WORDS = {"third": 0x3EAAAAAB, "w79": 0x3FBD207C, "w67": 0x3FBBC9E4, "pi": 0x40490FDB}
TILES = ["fp32.cal_third_b21", "fp32.cal_pi_b21", "fp32.cal_third_b20", "fp32.cal_w67_b21", "fp32.cal_w79_b21",
         "fp32.cal_w67_b20", "fp32.cal_w79_b20", "fp32.cal_pi_b20"]
LOOKED = ["fp32.cal_third_b21", "fp32.cal_pi_b21", "fp32.cal_third_b20", "fp32.cal_pi_b20"]
NMIN = 6


def look(files, N):
    rows = RR.merged(files)
    pr = RR.prices()
    P = RR.points(N)
    res = {}
    for name in TILES:
        pts = rows[name]["points"]
        if any(n not in pts for n in P):
            res[name] = {"missing_points": sum(n not in pts for n in P)}
            continue
        ws = [(n, RR.point_w(pts[n], "fp32", pr)) for n in P]
        w = struct.unpack("<f", struct.pack("<I", WORDS[name.split("_")[1]]))[0]
        byb = {}
        for n, x in ws:
            byb.setdefault(math.floor(math.log2(16 * n * w)), []).append(x)
        allv = [x for _, x in ws]
        rec = {"n": len(allv), "mean_w": sum(allv) / len(allv), "sd_whole_launch_w": RR.sd(allv), "binades": {}}
        for b in sorted(byb):
            v = byb[b]
            rec["binades"][f"2^{b}"] = {"n": len(v), "mean_w": sum(v) / len(v), "sd_w": RR.sd(v) if len(v) > 1 else None}
        big = {k: x for k, x in rec["binades"].items() if x["n"] >= NMIN}
        lo = min(big, key=lambda k: big[k]["sd_w"])
        rec[f"binade_sd_range_n_ge_{NMIN}_w"] = [big[lo]["sd_w"], max(x["sd_w"] for x in big.values())]
        rec[f"tightest_binade_n_ge_{NMIN}"] = {"binade": lo, "n": big[lo]["n"], "sd_w": big[lo]["sd_w"],
                                              "ratio_to_whole_launch": big[lo]["sd_w"] / rec["sd_whole_launch_w"]}
        res[name] = rec
    return res


out = {"_note": "Q141(t2) fix pass, Wed 4 Nov 2026: REGISTRATION-step243.md section 4.2 item 1's binade look per tile, no new "
                "count; binade = floor(log2(16 n w)), the look's approximation of C's (strata for F2 come from accum.c); "
                "W of D at M9's frozen float prices; reported only, binds nothing",
       "looked_at_by_the_registration": LOOKED, "n_min_for_a_binade_range": NMIN,
       "files_81": [os.path.relpath(f, REPO) for f in FILES81],
       "at_81_points": look(FILES81, 81),
       "at_243_points_reference_only": look(FILES243, 243)}
json.dump(out, open(os.path.join(HERE, "look-binades.json"), "w"), indent=1, sort_keys=True)
for key in ("at_81_points", "at_243_points_reference_only"):
    print(key)
    for name, rec in out[key].items():
        r = rec[f"binade_sd_range_n_ge_{NMIN}_w"]
        t = rec[f"tightest_binade_n_ge_{NMIN}"]
        print(f"  {name:20s} whole launch sd {rec['sd_whole_launch_w']:.3f} W; binades with n >= {NMIN}: sd {r[0]:.3f}-{r[1]:.3f} W;"
              f" tightest {t['binade']} (n = {t['n']}) {t['sd_w']:.3f} W, x{t['ratio_to_whole_launch']:.2f}")
