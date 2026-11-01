"""E110 desk view, POST HOC on E75's committed passes, labelled: the DDR die rail (die_mv.ddr, mV), the board and the three rails per item,
raw means over [t0+2 s, t0+4 s), no leakage correction. Written to see whether E75's L3 level reads DRAM (it does: e75_levels.txt) and to
take the on-chip off-rail fraction from its L2 level for E110's frozen R6 prediction.

    python3 tools/claims-v3/e110/desk/e75_levels.py docs/reports/data/2026-10-28-e75-memory-flip-ladder/passes > tools/claims-v3/e110/desk/e75_levels.txt"""
import gzip, json, os, sys, collections
import numpy as np
root = sys.argv[1]
agg = collections.defaultdict(lambda: collections.defaultdict(list))
for p in sorted(os.listdir(root)):
    d = os.path.join(root, p)
    tel = [json.loads(l) for l in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") if l.startswith("{")]
    t = np.array([s["t_ms"] for s in tel], float)
    F = {"ddr_mv": np.array([s["die_mv"]["ddr"] for s in tel], float),
         "board": np.array([s["board_w"] for s in tel], float),
         "noc": np.array([s["sp"]["noc_w"][0] for s in tel], float),
         "sram": np.array([s["sp"]["sram_w"][0] for s in tel], float),
         "minion": np.array([s["sp"]["minion_w"][0] for s in tel], float)}
    first, last = {}, {}
    for l in open(os.path.join(d, "runs.jsonl")):
        r = json.loads(l)
        k = (r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))
        first[k] = min(first.get(k, 1e30), r["t_start_ms"]); last[k] = max(last.get(k, 0), r["t_end_ms"])
    for k in first:
        lo = first[k] + 2000
        w = (t >= lo) & (t < min(lo + 2000, last[k]))
        if w.sum() < 3: continue
        for f, A in F.items():
            agg[k[1]][f].append(float(A[w].mean()))
for it in sorted(agg):
    print("%-15s n=%d " % (it, len(agg[it]["board"])) + " ".join("%s=%.3f" % (f, np.mean(v)) for f, v in agg[it].items()))
