#!/usr/bin/env python3
"""E81 POST HOC, labelled (not registered; written Sat 31 Oct 2026 after the verification of E81's README). It moves
no registered verdict: the registration says nothing about the minion rail.

    python3 tools/claims-v3/dp/posthoc_rail.py docs/reports/data/2026-10-31-e81-dram-pattern

Does any of E81's data-dependent DRAM read power show on the compute (minion) rail? The README first said "none of it
is on the compute rail", citing the 8.32-8.48 W span of `runs.csv` `rail` across the items. That span is the zeros
item alone (lowest) against every data item, so this script reads the rail the way the registered reducer reads the
board: per kept run, the mean minion-rail power over the run's power window (`runs.csv` `rail`, raw, no leakage
correction), each item's value per headline pass, every contrast a within-pass difference, the headline the mean
over the headline passes with a two-sided t interval (df = n - 1; `reduce_mf.ci`, the registered helper). Kept runs
and headline passes are dp.json's (`passes_healthy`, `passes_headline`, an empty `fails`).

Beside each rail contrast it prints the board contrast (dp.json) and the difference in the window's temperature rise
over the launch reading (`t_win - start_c`), so a reader can see whether a rail step follows the temperature.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
sys.path.insert(0, HERE)
from reduce_mf import ci  # noqa: E402
from reduce_dp import CONTRASTS  # noqa: E402

D = sys.argv[1] if len(sys.argv) > 1 else "docs/reports/data/2026-10-31-e81-dram-pattern"
dp = json.load(open(os.path.join(D, "dp.json")))
healthy, headline = set(dp["passes_healthy"]), list(dp["passes_headline"])
rows = [r for r in csv.DictReader(open(os.path.join(D, "runs.csv")))
        if int(r["pass"]) in healthy and not r["fails"] and r["arm"] == "dram"]


def per_pass(field):
    out = {}
    for p in headline:
        for name in {r["item"] for r in rows}:
            v = [float(r[field]) for r in rows if int(r["pass"]) == p and r["item"] == name]
            if v:
                out[(p, name)] = sum(v) / len(v)
    return out


rail = per_pass("rail")
rise = {}
for r in rows:
    if int(r["pass"]) in headline:
        rise.setdefault((int(r["pass"]), r["item"]), []).append(float(r["t_win"]) - float(r["start_c"]))
rise = {k: sum(v) / len(v) for k, v in rise.items()}
items = sorted({r["item"] for r in rows})

print("E81 post hoc: the minion rail (runs.csv rail, raw W), headline passes %s, %d kept DRAM runs in them"
      % (headline, sum(1 for r in rows if int(r["pass"]) in headline)))
print("\nper item, mean over the headline passes: rail W, rail over dp_zeros [95 %], window rise over launch C")
for n in items:
    a = ci([rail[(p, n)] for p in headline])
    o = ci([rail[(p, n)] - rail[(p, "dp_zeros")] for p in headline])
    t = ci([rise[(p, n)] for p in headline])
    print("  %-10s %.3f W   %+.3f [%+.3f, %+.3f]   rise %+.2f C" % (n, a["mean"], o["mean"], o["lo"] if o["lo"] is not
                                                                    None else 0.0, o["hi"] if o["hi"] is not None
                                                                    else 0.0, t["mean"]))
print("\nregistered contrasts on the rail (within-pass, df = %d), the board's (dp.json headline.contrasts_W), and the"
      " window-rise difference" % (len(headline) - 1))
for cn, (plus, minus, what) in CONTRASTS.items():
    c = ci([rail[(p, plus)] - rail[(p, minus)] for p in headline])
    dt = ci([rise[(p, plus)] - rise[(p, minus)] for p in headline])
    b = dp["headline"]["contrasts_W"][cn]
    print("  %-18s rail %+.4f W [%+.4f, %+.4f]   board %+.3f W   rail/board %5.1f %%   d(rise) %+.2f C"
          % (cn, c["mean"], c["lo"], c["hi"], b["mean"], 100.0 * c["mean"] / b["mean"] if b["mean"] else
             float("nan"), dt["mean"]))
