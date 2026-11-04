#!/usr/bin/env python3
"""E167 (Q141(h), the fix pass): the box step before E167's claim (E167.md.dated-note-2.md, the latch). It reads the hottest-sensor field
and refuses E167 if it reads 72 C or more. That field, minshire[2] in a sampler line, is the maximum of the minion shires' smpl_hilo HIGH
LATCHES (firmware 836a4ab, pvt_controller.c: pvt_get_minion_avg_low_high_temperature takes MAX(sample.high), and
pvt_get_min_shire_ts_sample reads sample.high from smpl_hilo's SMPL_HI), not a live hottest sensor: on aifoundry2 it read 70 C on all
50,594 committed lines of E159, E160 and E161, at idle and under load. run_hpl.py's watcher applies E167's 72 C die line to it on every
live line, so at 72 C or more every E167 step would end at its first sample.

A file read only: no device is opened and no command is sent (dmcmd_audit: 0 send sites).

    python3 tools/claims-v3/e167/latch_check_e167.py --history <the box's 5 s history file> [--minutes 10] [--card 0] [--max-age-min 15]
    python3 tools/claims-v3/e167/latch_check_e167.py <sampler telemetry file or directory> [--lines 50]
--history: the box monitor's own file (~/live/history/<UTC day>.jsonl, E98's history, one line every 5 s); card <n>'s "max" is the same
  field (it read 70 C wherever minshire[2] did, E161's window); the lines of the last --minutes before the newest line are read, and the
  newest line must be at most --max-age-min old (0 turns the age check off, for a copied file at the desk).
<telemetry>: tel/*.jsonl[.gz] sampler lines (temp_c.minshire); the last --lines lines of the newest file.
Exit: 0 GO (every value read is under 72 C), 3 NO-GO (any at 72 C or more), 2 nothing readable (or the history is stale).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import gzip
import json
import os
import sys
import time

LINE_C = 72.0     # E167's die line (protocol-g1q.json / protocol-g2q.json safety.abs_stop_c), applied by run_hpl.py to minshire[0] and [2]


def lines_of(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        for ln in f:
            if ln.startswith("{"):
                try:
                    yield json.loads(ln)
                except ValueError:
                    pass


def from_history(path, minutes, card, max_age_min):
    rows = []
    for d in lines_of(path):
        for c in d.get("cards") or []:
            if c.get("n") == card and c.get("max") is not None and d.get("t") is not None:
                rows.append((int(d["t"]) / 1e3, float(c["max"]), c.get("die")))
    if not rows:
        return None, {"source": path, "why": f"no card {card} line with a max field"}
    rows.sort()
    t_new = rows[-1][0]
    age_min = (time.time() - t_new) / 60.0
    use = [r for r in rows if r[0] >= t_new - 60.0 * minutes]
    info = {"source": path, "kind": "the box's 5 s history, card %d's max" % card, "lines": len(use), "minutes": minutes,
            "newest_age_min": round(age_min, 1), "max_C": max(r[1] for r in use), "values_C": sorted(set(r[1] for r in use)),
            "die_C_range": [min(r[2] for r in use if r[2] is not None), max(r[2] for r in use if r[2] is not None)]
            if any(r[2] is not None for r in use) else None}
    if max_age_min > 0 and age_min > max_age_min:
        info["why"] = f"the history's newest line is {age_min:.1f} min old (> {max_age_min} min): the monitor may be down"
        return None, info
    return info["max_C"], info


def from_telemetry(path, n_last):
    fs = sorted(glob.glob(os.path.join(path, "**", "*.jsonl*"), recursive=True)) if os.path.isdir(path) else [path]
    fs = [f for f in fs if os.path.isfile(f)]
    if not fs:
        return None, {"source": path, "why": "no telemetry file"}
    newest = max(fs, key=os.path.getmtime)
    vals = []
    for d in lines_of(newest):
        ms = (d.get("temp_c") or {}).get("minshire") or []
        if len(ms) > 2 and ms[2] is not None:
            vals.append((d.get("t_ms"), float(ms[2]), ms[0]))
    vals = vals[-n_last:]
    if not vals:
        return None, {"source": newest, "why": "no sampler line with temp_c.minshire[2]"}
    return max(v[1] for v in vals), {"source": newest, "kind": "sampler lines, temp_c.minshire[2]", "lines": len(vals),
                                     "max_C": max(v[1] for v in vals), "values_C": sorted(set(v[1] for v in vals)),
                                     "mean_C_range": [min(v[2] for v in vals), max(v[2] for v in vals)]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--history", action="append", default=[])
    ap.add_argument("--minutes", type=float, default=10.0)
    ap.add_argument("--card", type=int, default=0)
    ap.add_argument("--max-age-min", type=float, default=15.0)
    ap.add_argument("--lines", type=int, default=50)
    a = ap.parse_args()
    if not a.paths and not a.history:
        ap.error("give --history <file> or a telemetry file or directory")
    worst, infos, unreadable = None, [], 0
    for h in a.history:
        v, info = from_history(h, a.minutes, a.card, a.max_age_min)
        infos.append(info)
        unreadable += v is None
        worst = v if (v is not None and (worst is None or v > worst)) else worst
    for p in a.paths:
        v, info = from_telemetry(p, a.lines)
        infos.append(info)
        unreadable += v is None
        worst = v if (v is not None and (worst is None or v > worst)) else worst
    if worst is None:
        verdict, code = "UNREADABLE: the latch could not be read (the smoke's first samples are then the check: at 72 C or more the queue ends there, before any hold)", 2
    elif worst >= LINE_C:
        verdict, code = (f"NO-GO: the hottest-sensor field reads {worst:g} C, at or over E167's {LINE_C:g} C die line: every E167 step would end at "
                         "its first sample; do not claim or start E167 (resetting the latch is a write, outside the round's rules)"), 3
    else:
        verdict, code = f"GO: the hottest-sensor field reads {worst:g} C, under E167's {LINE_C:g} C die line", 0
    if code == 0 and unreadable:
        verdict += f" ({unreadable} source(s) unreadable)"
    print(json.dumps({"latch_check": verdict, "max_C": worst, "sources": infos}, indent=1))
    sys.exit(code)


if __name__ == "__main__":
    main()
