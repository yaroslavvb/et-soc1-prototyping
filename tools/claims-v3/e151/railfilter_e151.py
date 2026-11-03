#!/usr/bin/env python3
"""E151's registered minion-rail filter (Q139; README.md, "The rail filter"), written and committed before any E151 data. Standard
library only.

WHY. E145's registered primary on aifoundry1 card 1 read INCONCLUSIVE because that card's minion rail now and then reports the service
processor's running maximum (sp.minion_w[2], 34.50 W) as its current reading (sp.minion_w[0]) for one or two samples; four such samples
fell inside three B runs' rail windows and widened the interval six-fold (E145 README sections 3-4, posthoc/rail-spikes.json).

THE RULE. In each block's telemetry, taken as the sampler wrote it (one line a sample, in order), a sample i is a RAIL GLITCH when
  F1  its rail reading sp.minion_w[0] is more than 4.0 W above BOTH samples two steps away (i - 2 and i + 2): E82 amendment A2's
      board-dip rule mirrored onto the rail, E145's post-hoc definition unchanged (posthoc_e145.py, SPIKE_W 4.0); or
  F2  its rail reading equals, exactly, the running maximum the same sample reports (sp.minion_w[0] == sp.minion_w[2]): the value
      card 1's glitch reports. (On aifoundry3 the field has read a constant 38.375 W in every sample since 1 Nov, and no sample has
      equalled it; int8 trains draw about 9-15 W on the rail, so F2 cannot touch a real reading there.)
A glitch sample is removed from the block's telemetry before the reduction reads it, the whole line (its board reading too), exactly
as E82 A2's board dips are; the reducer (reduce_e151.py) applies both, dips and glitches, in E151's registered primary.

The rule reads only the telemetry samples, one block at a time: never an item, a run, a step, a price, B's odd - even contrast or any
other result. It was tested on E145's data before E151's first launch (selftest_e151.py): it marks the same 15 samples E145's post hoc
found, all 15 at the running maximum, in E145's 26,469 block samples (F1 15, F2 15, union 15), and none in E138's or E130's aifoundry3
blocks or in any committed aifoundry3 telemetry since 1 Nov 2026.

    python3 tools/claims-v3/e151/railfilter_e151.py <telemetry.jsonl[.gz] or a directory holding them> ...   # a census, JSON
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import os
import sys

SPIKE_W = 4.0          # F1's threshold, E145's post-hoc SPIKE_W (E82 A2's 4.0 W, mirrored)
STEP = 2               # F1 compares with the samples two steps away, as E82 A2


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def rail_and_max(rows):
    """Per sample: (sp.minion_w[0], sp.minion_w[2]) as floats, or None where the line has no such field."""
    R, M = [], []
    for r in rows:
        try:
            m = r["sp"]["minion_w"]
            R.append(_num(m[0]))
            M.append(_num(m[2]) if len(m) > 2 else None)
        except (KeyError, IndexError, TypeError):
            R.append(None)
            M.append(None)
    return R, M


def flags(rows):
    """The registered test on one block's telemetry rows: {"F1": set, "F2": set, "union": set} of sample indices."""
    R, M = rail_and_max(rows)
    f1, f2 = set(), set()
    for i in range(STEP, len(rows) - STEP):
        a, b, c = R[i], R[i - STEP], R[i + STEP]
        if None not in (a, b, c) and a > max(b, c) + SPIKE_W:
            f1.add(i)
    for i in range(len(rows)):
        if R[i] is not None and M[i] is not None and R[i] == M[i]:
            f2.add(i)
    return {"F1": f1, "F2": f2, "union": f1 | f2}


def drop(rows):
    """(kept rows, sorted removed indices) under the registered rule (F1 or F2)."""
    bad = flags(rows)["union"]
    return [r for i, r in enumerate(rows) if i not in bad], sorted(bad)


def load(path):
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for x in f:
            if x.startswith("{"):
                try:
                    out.append(json.loads(x))
                except ValueError:
                    pass
    return out


def census(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, "**", "telemetry.jsonl.gz"), recursive=True))
            files += sorted(glob.glob(os.path.join(p, "**", "telemetry.jsonl"), recursive=True))
        else:
            files.append(p)
    per, tot = {}, {"files": 0, "samples": 0, "F1": 0, "F2": 0, "union": 0}
    for f in files:
        rows = load(f)
        fl = flags(rows)
        R, M = rail_and_max(rows)
        key = os.path.relpath(f)
        per[key] = {"samples": len(rows), "F1": len(fl["F1"]), "F2": len(fl["F2"]), "union": len(fl["union"]),
                    "t_ms": [rows[i].get("t_ms") for i in sorted(fl["union"])][:50],
                    "values_w": sorted({R[i] for i in fl["union"]}),
                    "running_max_w": sorted({m for m in M if m is not None})[-3:]}
        tot["files"] += 1
        tot["samples"] += len(rows)
        for k in ("F1", "F2", "union"):
            tot[k] += len(fl[k])
    return {"rule": "F1: rail > max(rail[i-2], rail[i+2]) + 4.0 W; F2: rail == sp.minion_w[2]; a glitch is F1 or F2",
            "total": tot, "per_file": per}


if __name__ == "__main__":
    print(json.dumps(census(sys.argv[1:]), indent=1))
