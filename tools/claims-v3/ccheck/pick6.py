#!/usr/bin/env python3
"""Q139(k): the 6 pool-5 tiles E153 and E157 re-run with C checked (critic rank 14), picked mechanically. Standard library.

    python3 tools/claims-v3/ccheck/pick6.py [--json]

Rule (written before any C-checked launch): pool 5's non-anchor tiles; per format the two whose D was measured most
tightly on both cards, smallest sqrt(ci95_E141^2 + ci95_E142^2), ties by name. The D comparison it sets up is per card
(E153 on aifoundry3 against E141, E157 on aifoundry1 card 1 against E142), because the two cards' D differ by 0.3-0.5 W on
most tiles. Sources: docs/reports/data/2026-11-02-e141-blind5-aifoundry3/e141.json and
2026-11-02-e142-blind5-card1/e142.json, items.<tile>.D {mean, ci95, n}; tools/claims-v3/kinds/blind5/blind5.json.
"""
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
E141 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e141-blind5-aifoundry3/e141.json")
E142 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e142-blind5-card1/e142.json")
POOL = os.path.join(ROOT, "tools/claims-v3/kinds/blind5/blind5.json")


def main():
    a = json.load(open(E141))["items"]
    b = json.load(open(E142))["items"]
    pool = json.load(open(POOL))["tiles"]
    rows = []
    for t in pool:
        if t.get("anchor"):
            continue
        nm = t["name"]
        k = nm if nm in a else nm.split(".", 1)[1]
        da, db = a[k]["D"], b[k]["D"]
        rows.append({"tile": nm, "type": t["type"], "file": "tools/claims-v3/kinds/blind5/" + t["file"],
                     "sha256": t["sha256"]["whole"], "E141_D": round(da["mean"], 3), "E141_ci95": round(da["ci95"], 3),
                     "E141_n": da["n"], "E142_D": round(db["mean"], 3), "E142_ci95": round(db["ci95"], 3),
                     "E142_n": db["n"], "combined_ci95": round(math.hypot(da["ci95"], db["ci95"]), 3)})
    pick = []
    for typ in ("fp32", "fp16", "int8"):
        pick += sorted((r for r in rows if r["type"] == typ), key=lambda r: (r["combined_ci95"], r["tile"]))[:2]
    narrow = min(min(r["E141_ci95"], r["E142_ci95"]) for r in rows)
    if "--json" in sys.argv:
        print(json.dumps({"pick": pick, "narrowest_committed_ci95_W": narrow}, indent=1))
        return 0
    for r in pick:
        print("%-28s %s  E141 D %.3f +-%.3f (n=%d)  E142 D %.3f +-%.3f (n=%d)  combined +-%.3f  %s" % (
            r["tile"], r["type"], r["E141_D"], r["E141_ci95"], r["E141_n"], r["E142_D"], r["E142_ci95"], r["E142_n"],
            r["combined_ci95"], r["file"]))
    print("narrowest committed pool-5 D interval on either card: +-%.3f W (the critic's flat +-0.05 W is narrower than "
          "every other)" % narrow)
    return 0


if __name__ == "__main__":
    sys.exit(main())
