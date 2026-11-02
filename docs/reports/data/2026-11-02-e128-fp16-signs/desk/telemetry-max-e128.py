#!/usr/bin/env python3
"""E128 (Q136): the session's maxima, for the stops disclosure (E128.md N3: report E128's own maxima against the firmware's PMIC alarm at 75 W
and 75 C). Reads every ettelem sample line in the blocks' telemetry.jsonl.gz (the smoke and both passes; the read-back block runs no sampler).
Standard library only. POST HOC: no rule depends on it. A port of the E128 verifier's tel_max.py.

Corrected Mon 2 Nov 2026, after the second verification (README C6): the PMIC's 75 C alarm reads the PMIC's own temperature, which no field
here reads (temp_c.pmic is the minion-shire mean again), so the last line no longer prints a die reading's distance below 75 C. It prints the
board's margin to the 75 W over-power alarm and the die's maxima beside it. Every number and the JSON are unchanged.

    python3 desk/telemetry-max-e128.py aifoundry1-c1/e128/e128-smoke-p12801 aifoundry1-c1/e128/p12810 aifoundry1-c1/e128/p12811 \
        > desk/telemetry-max-e128.txt     # run in the data directory

SPDX-License-Identifier: Apache-2.0
"""
import collections
import gzip
import json
import os
import sys

KEYS = ("board_w", "sp_board_max_w", "minshire_mean", "minshire_high", "ioshire", "pmic_field")


def scan(path):
    mx = {k: (float("-inf"), None) for k in KEYS}
    mn = {k: float("inf") for k in KEYS}
    first = None
    mhz, n, bad = collections.Counter(), 0, 0
    f = os.path.join(path, "telemetry.jsonl.gz")
    t0 = t1 = None
    for line in gzip.open(f, "rt"):
        if not line.startswith("{"):
            continue
        try:
            s = json.loads(line)
        except ValueError:
            bad += 1
            continue
        n += 1
        ts = s.get("t_ms") or s.get("ts_ms")
        if ts is not None:
            t0 = ts if t0 is None else min(t0, ts)
            t1 = ts if t1 is None else max(t1, ts)
        temp = s.get("temp_c") or {}
        ms = temp.get("minshire") or [None, None, None]
        io = temp.get("ioshire") or [None]
        vals = {"board_w": s.get("board_w"), "sp_board_max_w": (s.get("sp") or {}).get("board_max_w"),
                "minshire_mean": ms[0], "minshire_high": ms[2] if len(ms) > 2 else None, "ioshire": io[0], "pmic_field": temp.get("pmic")}
        if first is None:
            first = dict(vals)
        for k, v in vals.items():
            if v is not None and v > mx[k][0]:
                mx[k] = (v, ts)
            if v is not None and v < mn[k]:
                mn[k] = v
        m = (s.get("mhz") or {}).get("minion")
        if m is not None:
            mhz[m] += 1
    return {"samples": n, "bad": bad, "max": {k: v[0] for k, v in mx.items()}, "min": mn, "first": first, "minion_mhz": dict(mhz)}


out, allmax = {}, {k: float("-inf") for k in KEYS}
tot, mhz = 0, collections.Counter()
for p in sys.argv[1:]:
    r = scan(p)
    out[os.path.basename(p.rstrip("/"))] = r
    tot += r["samples"]
    mhz.update(r["minion_mhz"])
    for k in KEYS:
        allmax[k] = max(allmax[k], r["max"][k])
print("E128 telemetry maxima (post hoc; for E128.md N3's stops disclosure; the PMIC alarm is 75 W of board power or 75 C of the PMIC's own "
      "temperature)")
for name, r in out.items():
    m = r["max"]
    print(f"  {name:20s} samples {r['samples']:6d} (bad {r['bad']}) | board {m['board_w']:.2f} W, SP running max {m['sp_board_max_w']:.2f} W | "
          f"die: minion shires' mean {m['minshire_mean']:.1f} C, hottest shire {m['minshire_high']:.1f} C, I/O shire {m['ioshire']:.1f} C, "
          f"temp_c.pmic {m['pmic_field']:.1f} C | minion MHz {r['minion_mhz']}")
print(f"  {'all':20s} samples {tot:6d} | board {allmax['board_w']:.2f} W, SP running max {allmax['sp_board_max_w']:.2f} W | die: mean "
      f"{allmax['minshire_mean']:.1f} C, hottest shire {allmax['minshire_high']:.1f} C, I/O shire {allmax['ioshire']:.1f} C, temp_c.pmic "
      f"{allmax['pmic_field']:.1f} C | minion MHz {dict(mhz)}")
for k in ("sp_board_max_w", "minshire_high"):
    carried = all(r["min"][k] == r["max"][k] == r["first"][k] for r in out.values())
    what = ("the same value in every sample from the first (idle) one, so a running maximum carried from before the session, not E128's own"
            if carried else "changes within the session")
    per = []
    for nm, r in out.items():
        per.append("%s first %s, min %s, max %s" % (nm, r["first"][k], r["min"][k], r["max"][k]))
    print("  %s: %s (%s)" % (k, what, "; ".join(per)))
high_carried = all(r["min"]["minshire_high"] == r["max"]["minshire_high"] == r["first"]["minshire_high"] for r in out.values())
heat = (f"no shire above {allmax['minshire_high']:.1f} C (the PVT's running high, the same in every sample)" if high_carried
        else f"the shires' running high at most {allmax['minshire_high']:.1f} C")
print(f"  margin to the PMIC's 75 W over-power alarm: board {75 - allmax['board_w']:.2f} W (SP running max {75 - allmax['sp_board_max_w']:.2f} W); "
      f"die, beside the alarm and not a margin to it: minion shires' mean at most {allmax['minshire_mean']:.1f} C, {heat}; the 75 C alarm "
      f"reads the PMIC's own temperature, which no field here reads (temp_c.pmic is the shire mean again)")
print(json.dumps({"blocks": out, "all": {"samples": tot, "max": allmax, "minion_mhz": dict(mhz)}}, indent=1))
