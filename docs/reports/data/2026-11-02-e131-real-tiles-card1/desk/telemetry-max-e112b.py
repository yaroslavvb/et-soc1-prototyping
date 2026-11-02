#!/usr/bin/env python3
"""E131 desk (before the registration): the board power and die maxima of committed passes, from their raw telemetry (board_w; the
hottest of temp_c.minshire; temp_c.pmic). Used for the margin of E131's stops on E112b's three passes of the same 53-run pass on this card.

    python3 telemetry-max-e112b.py <pass dir> ... > telemetry-max-e112b.txt
SPDX-License-Identifier: Apache-2.0
"""
import gzip, json, sys, glob, os
for d in sys.argv[1:]:
    f = os.path.join(d, "telemetry.jsonl.gz")
    if not os.path.exists(f):
        f = os.path.join(d, "telemetry.jsonl")
        op = open
    else:
        op = gzip.open
    bw, tc, pm, n = [], [], [], 0
    for line in op(f, "rt"):
        try:
            s = json.loads(line)
        except Exception:
            continue
        n += 1
        w = s.get("board_w")
        if isinstance(w, (int, float)):
            bw.append(w)
        t = s.get("temp_c") or {}
        ms = t.get("minshire")
        if ms:
            tc.append(max(ms) if isinstance(ms, list) else ms)
        if isinstance(t.get("pmic"), (int, float)):
            pm.append(t["pmic"])
    bw.sort()
    print(os.path.basename(d), "samples", n, "board max %.2f p999 %.2f" % (bw[-1], bw[int(0.999 * len(bw))]), "die max", max(tc) if tc else None, "pmic max", max(pm) if pm else None)
