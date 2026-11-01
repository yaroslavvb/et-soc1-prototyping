#!/usr/bin/env python3
"""A dated addition to Q132(g), Sun 1 Nov 2026 (Q132(o)). POST HOC, desk only, no card: the same count as pmic_check.py, on aifoundry2's
sessions of that night, which came after this directory was written. Alarm lines, POWER_SAFE records and 300 MHz operating points in the
committed service-processor rings (tools/claims-v3/hpl/sptrace_full.py), and the telemetry's readings. Run from this directory; standard
library only. Output: rings-tonight.txt."""
import glob
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(DATA, "..", "..", "..", "tools/claims-v3/hpl"))
sys.path.insert(0, os.path.join(DATA, "..", "..", "..", "tools/claims-v3/dv2"))
import sptrace_full as spf  # noqa: E402

ALARM = re.compile(r"alarm set point")
SESS = [("E96 s1", "2026-11-01-e96-real-tensors-speed/s1"), ("E100 s1", "2026-11-01-e100-idle-reset/s1"),
        ("E101 s1", "2026-11-01-e101-real-matmul/aifoundry2/s1"), ("E105 s1", "2026-11-01-e105-gemm-layout/aifoundry2/s1"),
        ("E98 P1", "2026-11-01-e98-heat-path-drift/P1"), ("E98 P2", "2026-11-01-e98-heat-path-drift/P2"),
        ("E98 P3", "2026-11-01-e98-heat-path-drift/P3"), ("E98 P6", "2026-11-01-e98-heat-path-drift/P6"),
        ("E98 P7", "2026-11-01-e98-heat-path-drift/P7")]
tot = dict(rings=0, alarm=0, safe=0, op300=0, n=0, at300=0, ge75=0, ge85=0, ge100=0)
print("session  rings alarm  safe op300 | readings at300 >=75W >=85W >=100W  max board_w  at MHz")
for name, rel in SESS:
    d = os.path.join(DATA, rel)
    rings = alarm = safe = op300 = 0
    prev = None
    for p in sorted(glob.glob(os.path.join(d, "sp", "*.bin"))):
        cur = spf.scan(open(p, "rb").read()) or []
        rings += 1
        new = spf.since(prev, cur) if prev is not None else cur
        prev = cur
        for e in new:
            if ALARM.search(e.get("text") or ""):
                alarm += 1
            if e.get("kind") == "pstat" and e.get("throttle_state") == 3:
                safe += 1
            if e.get("kind") == "new_op" and e.get("mhz") == 300:
                op300 += 1
    n = at300 = ge75 = ge85 = ge100 = 0
    top = (0.0, None)
    for f in sorted(glob.glob(os.path.join(d, "tel", "*"))):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt") as fh:
            for line in fh:
                try:
                    j = json.loads(line)
                except ValueError:
                    continue
                m = (j.get("mhz") or {}).get("minion") if isinstance(j.get("mhz"), dict) else None
                w = j.get("board_w")
                if m is None:
                    continue
                n += 1
                at300 += m <= 300
                if w is not None:
                    ge75 += w >= 75
                    ge85 += w >= 85
                    ge100 += w >= 100
                    if w > top[0]:
                        top = (w, m)
    print(f"{name:8s} {rings:5d} {alarm:5d} {safe:5d} {op300:5d} | {n:8d} {at300:5d} {ge75:5d} {ge85:5d} {ge100:6d}  {top[0]:11.2f}  {top[1]}")
    for k, v in zip(("rings", "alarm", "safe", "op300", "n", "at300", "ge75", "ge85", "ge100"), (rings, alarm, safe, op300, n, at300, ge75, ge85, ge100)):
        tot[k] += v
print("in all:", json.dumps(tot))
