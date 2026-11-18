#!/usr/bin/env python3
"""v31-trace (Q217): the chip-level numbers read from a traced run alone (no walk): per op step, the distinct A and B tiles the traced harts
read chip-wide and how many active shires read each (from every traced hart 0, whose neighbourhood and position cover every tile its shire
reads when the selection is the diagonal one or all harts), the pass footprint by pool, the C tiles stored (complete only when every minion
is traced), and per traced hart its op count and its first and last op step. Desk; standard library; /usr/bin/python3 3.12.3.

    python3 -I -B traced_numbers.py --summary RUN/summary.json.gz --check RUN/check.json --out RUN/traced_numbers.json
"""
import argparse
import collections
import gzip
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--check", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s = json.load(gzip.open(a.summary, "rt"))
    c = json.load(open(a.check))
    base = {k: int(v, 16) for k, v in c["bases"].items()}
    sel = set()
    for x in s["meta"]["log_sel"]:
        sh, m = x.split(",")
        sel |= {64 * int(sh) + t for t in range(64) if (int(m, 16) >> t) & 1}
    stepA = collections.defaultdict(lambda: collections.defaultdict(set))   # op -> tile -> shires
    stepB = collections.defaultdict(lambda: collections.defaultdict(set))
    footA, footB, footC = set(), set(), set()
    harts = {}
    for hs, v in s["harts"].items():
        h = int(hs)
        if h not in sel or h % 2 or not v["events"]:
            continue
        shire = h // 64
        op = 0
        first = last = None
        for e in v["events"]:
            if e[0] == "LA":
                t = (e[2] - base["A"]) >> 10
                stepA[op][t].add(shire)
                footA.add(t)
                first = e[1] if first is None else first
                last = e[1]
            elif e[0] == "LB":
                t = (e[2] - base["B"]) >> 10
                stepB[op][t].add(shire)
                footB.add(t)
            elif e[0] == "S":
                footC.add((e[2] - base["C"]) >> 10)
            elif e[0] == "F":
                op += 1
        harts[hs] = {"ops": op, "first_load_step": first, "last_load_step": last}
    distA = collections.Counter(len(stepA[o]) for o in stepA)
    distB = collections.Counter(len(stepB[o]) for o in stepB)
    shareA = collections.Counter(len(w) for o in stepA for w in stepA[o].values())
    shareB = collections.Counter(len(w) for o in stepB for w in stepB[o].values())
    res = {"run": s["meta"].get("name"), "op_steps": len(stepA),
           "distinct_A_tiles_per_step": {str(k): v for k, v in sorted(distA.items())},
           "distinct_B_tiles_per_step": {str(k): v for k, v in sorted(distB.items())},
           "A_tile_sharing_shires_hist_over_steps": {str(k): v for k, v in sorted(shareA.items())},
           "B_tile_sharing_shires_hist_over_steps": {str(k): v for k, v in sorted(shareB.items())},
           "footprint_tiles": {"A": len(footA), "B": len(footB), "C_stored_by_traced_harts": len(footC)},
           "traced_working_harts": len(harts), "ops_per_traced_hart": dict(collections.Counter(x["ops"] for x in harts.values()))}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
