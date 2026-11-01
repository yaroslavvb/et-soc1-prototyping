#!/usr/bin/env python3
"""E97, reported and never a verdict: the room across each hold. The boxes log ~/live/history/<UTC date>.jsonl every 5 s (tools/lab/live/live-collector.py): the host's own sensors, and each card's
die reading and board power when nobody holds that machine's cards. An idle card on another box, or a box's NIC and NVMe sensors, stand in for the room; this box's own sensors also feel the card it hosts.

    python3 tools/claims-v3/e97/room_e97.py <dir with aifoundry1/, aifoundry2/, aifoundry3/ history files> <pass dir 9720> > room.txt
"""
import glob
import json
import os
import sys

import numpy as np


def load(d):
    rows = []
    for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
        for line in open(f):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    return rows


def slope_of(t, y):
    if len(t) < 10 or np.ptp(t) < 60:
        return None
    return float(np.polyfit((t - t[0]) / 3600.0, y, 1)[0])


def main():
    hist, p = sys.argv[1], sys.argv[2]
    marks = [json.loads(x) for x in open(os.path.join(p, "marks.jsonl"))]
    spans = [(m["name"], m["t_start_ms"], m["t_end_ms"]) for m in marks if m["kind"] in ("hold", "rest")]
    if spans:
        spans.append(("all of Part B", min(s[1] for s in spans), max(s[2] for s in spans)))
    for host in ("aifoundry3", "aifoundry1", "aifoundry2"):
        rows = load(os.path.join(hist, host))
        if not rows:
            print(f"{host}: no history copied")
            continue
        t = np.array([r["t"] for r in rows], float)
        print(f"== {host}: the slope over each span, degC per hour (W per hour for board power); n = samples; a card's die and power only while no card on that box was held")
        for name, a, b in spans:
            m = (t >= a) & (t < b)
            row = []
            for key in ("nic", "nvme", "cpu"):
                v = [(r["t"], r["temps"][key]) for r, q in zip(rows, m) if q and r.get("temps", {}).get(key) is not None]
                if v:
                    tv = np.array(v, float)
                    s = slope_of(tv[:, 0] / 1000.0, tv[:, 1])
                    row.append(f"{key} {tv[:, 1].mean():.2f}" + ("" if s is None else f" ({s:+.2f}/h)"))
            for n in (0, 1):
                v = [(r["t"], c["die"], c.get("w", np.nan)) for r, q in zip(rows, m) if q for c in r.get("cards", []) if c.get("n") == n and c.get("die") is not None]
                if len(v) > 10:
                    tv = np.array(v, float)
                    s = slope_of(tv[:, 0] / 1000.0, tv[:, 2])
                    row.append(f"card {n} free n={len(v)}: die {tv[:, 1].mean():.2f} C, {np.nanmean(tv[:, 2]):.2f} W" + ("" if s is None else f" ({s:+.3f} W/h)"))
            print(f"  {name:>14s} [{(b - a) / 60000:6.1f} min]: " + "; ".join(row))


if __name__ == "__main__":
    main()
