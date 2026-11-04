#!/usr/bin/env python3
"""Q141(k), go checklist step 22 (Q141(f)'s F9): write E165's zeros-anchor reads to a file for E167's E2 arm and E168's --anchors arm.

score_e165.py already writes them (score_e165.py:518, 526-527): results.json `score.anchors` in predict_m9_a2.session_delta's form
{type: [{burst_w, burst_mhz, die_start}, ...]}, and the session's delta at `score.anchor_delta`. This copies those two objects,
unchanged, into two files beside results.json:

    /usr/bin/python3 -B tools/claims-v3/q141k-runbook/anchors_e165.py <E165's data dir>

  <data dir>/anchors-for-e167-e168.json   score.anchors, the file passed to
        score_e167_x2.py --e165-anchors (its loader reads this form, or {"delta_w": ...}; score_e167.py:146-154) and to
        reduce_e168.py --anchors (session_delta's layout, README step 8);
  <data dir>/anchor-delta-e165.json       score.anchor_delta, kept beside for the record.

Both arms are reported only; the registered primaries do not read them. Exit 0 written; 3 if results.json has no score.anchors (the
session was NOT SCORED, or an older layout): E167's E2 and E168's anchors arm then run without it, as their kits allow; 2 usage.
Desk only: reads one file, writes two, sends nothing. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

TYPES = ("fp32", "fp16", "int8")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    d = sys.argv[1]
    res = json.load(open(os.path.join(d, "results.json")))
    sc = res.get("score") or {}
    anc = sc.get("anchors")
    if not isinstance(anc, dict) or not any(t in anc for t in TYPES):
        print(f"no score.anchors in {d}/results.json ({sc.get('note') or 'no anchors key'}): E167's E2 and E168's anchors arm are not computed")
        return 3
    json.dump(anc, open(os.path.join(d, "anchors-for-e167-e168.json"), "w"), indent=1, sort_keys=True)
    json.dump(sc.get("anchor_delta"), open(os.path.join(d, "anchor-delta-e165.json"), "w"), indent=1, sort_keys=True)
    n = {t: len(anc.get(t) or []) for t in TYPES}
    print(f"wrote {d}/anchors-for-e167-e168.json (anchor bursts per type {n}) and anchor-delta-e165.json "
          f"({json.dumps(sc.get('anchor_delta'))[:200]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
