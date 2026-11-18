#!/usr/bin/env python3
"""verify-v31trace (Q217) v02: from v31-trace's check.json files (read only), list the stray (unselected) harts by shire, minion and
thread, and the shire-31 harts. /usr/bin/python3 3.12.3, standard library."""
import collections
import glob
import json
import os

RUNS = "<W>/out/v31-trace/traces/runs"
for d in sorted(glob.glob(os.path.join(RUNS, "t*"))):
    name = os.path.basename(d)
    c = json.load(open(os.path.join(d, "check.json")))
    # check.json keeps only counts of strays; re-derive the ids from the summary's hart keys against the selection
    import gzip
    s = json.load(gzip.open(os.path.join(d, "summary.json.gz"), "rt"))
    sel = set()
    for x in s["meta"]["log_sel"]:
        sh, m = x.split(",")
        sel |= {64 * int(sh) + t for t in range(64) if (int(m, 16) >> t) & 1}
    stray = sorted(int(h) for h in s["harts"] if int(h) not in sel)
    by = collections.Counter()
    kinds = collections.Counter()
    for h in stray:
        by[h // 64] += 1
        kinds["thread%d" % (h % 2)] += 1
    mask = int(s["meta"]["mask"], 16)
    act = [x for x in range(32) if (mask >> x) & 1]
    in_act = sum(1 for h in stray if h // 64 in act)
    print(name, "strays", len(stray), "by shire", dict(sorted(by.items())), kinds, "in active shires", in_act,
          "examples", stray[:12], "killed lines", sum(s["harts"][str(h)]["killed"] for h in stray),
          "instr", sum(sum(s["harts"][str(h)]["instr_by_mode"].values()) for h in stray))
