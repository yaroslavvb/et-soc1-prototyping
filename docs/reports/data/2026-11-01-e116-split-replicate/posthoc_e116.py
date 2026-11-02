#!/usr/bin/env python3
"""E116, POST HOC (labelled; not registered): numbers the README quotes beyond scored.json. Standard library only; reads
committed files in this directory and E88's.

    python3 posthoc_e116.py > posthoc.txt      (writes posthoc.json beside it)

1. The split on the minion rail (Drail: deconvolved, the reducer's own), per pass, as E88's README C4 reported it.
2. The observed card ratio E116 / E88 for each part, total and random anchor (board D).
3. The read-back's clock and cycles per op per launch.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
E88 = os.path.join(HERE, "..", "2026-10-31-e88-result-path")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
DESIGN = {"fp32": ("fp32.c_abs", "fp32.r_abs", "fp32.r_walk", "fp32.randn"),
          "fp16": ("fp16.c_cancel", "fp16.r_cancel", "fp16.r_walk", "fp16.randn"),
          "int8": ("int8.c_cancel", "int8.r_cancel", "int8.r_walk", "int8.full")}


def stat(v):
    v = [x for x in v if x is not None]
    if len(v) < 2:
        return {"mean": v[0] if v else None, "ci95": None, "n": len(v)}
    se = statistics.stdev(v) / math.sqrt(len(v))
    return {"mean": round(statistics.fmean(v), 4), "ci95": round(se * T95.get(len(v) - 1, 1.96), 4), "n": len(v)}


def split(red, key):
    out = {}
    for f, (c, r, w, a) in DESIGN.items():
        rows = [v for v in red["per_pass"].values() if all(v.get(k) and v[k].get(key) is not None for k in (c, r, w))]
        P = {"i": [v[c][key] for v in rows], "iii": [v[r][key] - v[c][key] for v in rows], "ii": [v[w][key] - v[r][key] for v in rows]}
        T = [v[w][key] for v in rows]
        out[f] = {"total": stat(T), **{p: stat(P[p]) for p in P}, **{"share_" + p: stat([x / t for x, t in zip(P[p], T)]) for p in P}}
    return out


def main():
    e116 = json.load(open(os.path.join(HERE, "e116.json")))
    e88 = json.load(open(os.path.join(E88, "e88.json")))
    res = {"what": "POST HOC, labelled: not registered", "rail_e116": split(e116, "Drail"), "rail_e88": split(e88, "Drail"),
           "board_e116": split(e116, "D"), "board_e88": split(e88, "D")}
    ratio = {}
    for f, (c, r, w, a) in DESIGN.items():
        b6, b8 = res["board_e116"][f], res["board_e88"][f]
        ratio[f] = {p: round(b6[p]["mean"] / b8[p]["mean"], 4) for p in ("i", "iii", "ii", "total")}
        A6 = stat([v[a]["D"] for v in e116["per_pass"].values() if v.get(a)])
        A8 = stat([v[a]["D"] for v in e88["per_pass"].values() if v.get(a)])
        ratio[f]["anchor"] = round(A6["mean"] / A8["mean"], 4)
        ratio[f]["anchor_W"] = [A6, A8]
    res["ratio_e116_over_e88_board"] = ratio
    rb = [json.loads(l) for l in open(os.path.join(HERE, "aifoundry3", "rpath", "rpath-readback-p11602", "readback.jsonl"))]
    res["readback_launches"] = {"n": len(rb), "cycles_per_op": sorted({(x["sparsity"] or {}).get("cycles_per_op") for x in rb}),
                                "ghz": [min((x["sparsity"] or {}).get("ghz") for x in rb), max((x["sparsity"] or {}).get("ghz") for x in rb)],
                                "iters": sorted({(x["sparsity"] or {}).get("iters") for x in rb}), "ok": all((x["sparsity"] or {}).get("ok") for x in rb),
                                "wall_s": [min(x["wall_s"] for x in rb), max(x["wall_s"] for x in rb)], "results": sorted({(x["sparsity"] or {}).get("result") for x in rb})}
    json.dump(res, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
    for f in DESIGN:
        r6, r8 = res["rail_e116"][f], res["rail_e88"][f]
        print(f"{f} rail E116: i {r6['i']['mean']} iii {r6['iii']['mean']} ii {r6['ii']['mean']} of {r6['total']['mean']} W; shares "
              f"{r6['share_i']['mean']} / {r6['share_iii']['mean']} / {r6['share_ii']['mean']} (n {r6['total']['n']}) | E88 rail shares "
              f"{r8['share_i']['mean']} / {r8['share_iii']['mean']} / {r8['share_ii']['mean']}")
        print(f"{f} board ratio E116/E88: {ratio[f]}")
    print("read-back launches:", res["readback_launches"])


if __name__ == "__main__":
    main()
