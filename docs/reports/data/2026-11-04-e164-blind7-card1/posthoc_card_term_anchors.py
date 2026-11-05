#!/usr/bin/env python3
"""POST HOC, and labelled so: two readings of E163's and E164's committed per-tile rows that no rule registered.

Written Wed 4 Nov 2026 (week 45) by the card half's records (Q141(i)), porting the card half's critic's two desk checks so that
anyone can re-run them from this repository. Standard library only; it reads the two scored.json files and writes nothing.

1. The card term inside E164-U1. For each priority-1 tile scored on both 600 MHz cards,
       r = (M6 on card 1 / M9 on card 1) / (M6 on aifoundry3 / M9 on aifoundry3).
   On aifoundry3 every model's card term is 1, so r isolates the ratio of M6's card term on card 1 to M9's. Then M9's card-1
   error with M9 scaled by r, per family, over all priority-1 kinds and over the kinds aimed at none of the named classes (U).
2. A session scale per family from the session's own random anchors (pool 7's priority-2 anchors, never scored): for each card,
   s = the median over that family's random anchors (M9's D above 1 W, so the zeros anchors are left out) of measured D / M9's D;
   then every priority-1 tile's M9 prediction times s, scored over the 48 kinds as the registered set is.

Usage (from the repository root):
    python3 -I -B docs/reports/data/2026-11-04-e164-blind7-card1/posthoc_card_term_anchors.py \
        docs/reports/data/2026-11-04-e163-blind7-aifoundry3/scored.json \
        docs/reports/data/2026-11-04-e164-blind7-card1/scored.json

SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import statistics
import sys


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else float("nan")


def mean(v):
    return sum(v) / len(v) if v else float("nan")


def fam(t):
    return "int8" if t.startswith("int8") else "floats"


def priority1(rows):
    return {t: r for t, r in rows.items() if r.get("priority") == 1 and not r.get("pool_anchor")}


def unaimed(r):
    c = r.get("case", "")
    return "aimed at nothing" in c or c.startswith("U")


def main(a3_path, c1_path):
    a3_all = json.load(open(a3_path, encoding="utf-8"))["primary"]["primary"]
    c1_all = json.load(open(c1_path, encoding="utf-8"))["primary"]
    a3, c1 = a3_all["power_rows"], c1_all["power_rows"]

    print("POST HOC (no rule registered for either reading). E163 aifoundry3 and E164 aifoundry1 card 1, registered primary rows.")
    print()
    print("1. The card term inside E164-U1: M6's card term on card 1 over M9's, isolated per tile")
    rat = {"floats": [], "int8": []}
    for t, r9 in priority1(c1["M9"]).items():
        if t not in a3["M9"] or t not in c1["M6"] or t not in a3["M6"]:
            continue
        x = (c1["M6"][t]["pred"] / r9["pred"]) / (a3["M6"][t]["pred"] / a3["M9"][t]["pred"])
        rat[fam(t)].append(x)
    med = {}
    for k in ("floats", "int8"):
        v = sorted(rat[k])
        med[k] = v[len(v) // 2]
        print("   %s: n = %d, ratio median %.4f, range %.4f-%.4f" % (k, len(v), med[k], v[0], v[-1]))
    for k in ("floats", "int8"):
        e9, e9s, e6, u9, u9s, u6 = [], [], [], [], [], []
        for t, r9 in priority1(c1["M9"]).items():
            if fam(t) != k:
                continue
            meas = r9["measured"]
            e9.append(meas - r9["pred"])
            e9s.append(meas - r9["pred"] * med[k])
            e6.append(c1["M6"][t]["error"])
            if unaimed(r9):
                u9.append(meas - r9["pred"])
                u9s.append(meas - r9["pred"] * med[k])
                u6.append(c1["M6"][t]["error"])
        print("   %s, card 1, all priority 1 (%d): M9 as frozen rms %.3f bias %+.3f | M9 x %.4f rms %.3f bias %+.3f | M6 rms %.3f bias %+.3f"
              % (k, len(e9), rms(e9), mean(e9), med[k], rms(e9s), mean(e9s), rms(e6), mean(e6)))
        print("   %s, card 1, unaimed U (%d): M9 as frozen rms %.3f bias %+.3f | M9 x %.4f rms %.3f bias %+.3f | M6 rms %.3f bias %+.3f"
              % (k, len(u9), rms(u9), mean(u9), med[k], rms(u9s), mean(u9s), rms(u6), mean(u6)))
    print()
    print("2. A session scale per family from the session's own random anchors (M9 times s)")
    for name, pp in (("E163 aifoundry3", a3_all), ("E164 card 1", c1_all)):
        anc = pp["pool_anchors"]
        s = {}
        for k in ("floats", "int8"):
            r = [a["measured_D"] / a["M9_D"] for t, a in anc.items() if fam(t) == k and a["M9_D"] > 1.0]
            s[k] = statistics.median(r)
        rows = priority1(pp["power_rows"]["M9"])
        a0 = [r["error"] for r in rows.values()]
        a1 = [r["measured"] - r["pred"] * s[fam(t)] for t, r in rows.items()]
        nos = [r["measured"] - r["pred"] * s[fam(t)] for t, r in rows.items() if not r.get("case", "").startswith("S")]
        print("   %s, all %d: as frozen rms %.3f bias %+.3f -> scaled rms %.3f bias %+.3f; scaled without class S (%d) rms %.3f"
              % (name, len(a0), rms(a0), mean(a0), rms(a1), mean(a1), len(nos), rms(nos)))
        for k in ("floats", "int8"):
            e0 = [r["error"] for t, r in rows.items() if fam(t) == k]
            e1 = [r["measured"] - r["pred"] * s[k] for t, r in rows.items() if fam(t) == k]
            print("      %s s = %.4f: as frozen rms %.3f bias %+.3f -> scaled rms %.3f bias %+.3f"
                  % (k, s[k], rms(e0), mean(e0), rms(e1), mean(e1)))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: posthoc_card_term_anchors.py <E163 scored.json> <E164 scored.json>")
    main(sys.argv[1], sys.argv[2])
