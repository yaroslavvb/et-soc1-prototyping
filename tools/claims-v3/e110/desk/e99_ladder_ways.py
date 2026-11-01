"""E110 desk view, POST HOC on E99's committed data, labelled: which N-way interleave's line-change count fits each rail's period ladder
best (rails per pass from E99's posthoc_rails windows; counts from dm_enc.path_distance; seven rungs). Written to see whether a per-rail
interleave test could be registered for E110. It could not: on the NoC rail, the SRAM rail and off them the two best interleaves fit within 0.4 %, 2.6 % and
9 % of each other in rms (on the board 8-way beats 16-way by 25 %, E99's own reading; the minion rail has no ladder effect; e99_ladder_ways.txt),
so E110 registers no interleave reading and keeps only the ladder's two ends.

    python3 tools/claims-v3/e110/desk/e99_ladder_ways.py <lab repo root> > tools/claims-v3/e110/desk/e99_ladder_ways.txt"""
import json, os, sys
import numpy as np
LAB = sys.argv[1]
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/dm"))
from dm_enc import lines_of, path_distance
from posthoc_rails import pass_rails
D = os.path.join(LAB, "docs/reports/data/2026-11-01-e99-dram-mechanism")
d = json.load(open(os.path.join(D, "dm.json")))
passes = [str(p) for p in d["passes_headline"]]
LAD = ["dm_L2", "dm_L4", "dm_L8", "dm_L16", "dm_L32", "dm_L256", "dm_L8192"]
K = {}
for nm in LAD:
    L = lines_of(open(os.path.join(D, "gen/srcs", nm + ".bin"), "rb").read())
    K[nm] = {w: path_distance(L, w)[0] for w in (2, 4, 8, 16, 32, 64, 128, 256)}
    print(nm, {w: round(v, 1) for w, v in K[nm].items()})
R = {}
for p in passes:
    rails = pass_rails(os.path.join(D, "passes", "p" + p))
    R[p] = {}
    for it in LAD:
        b = d["per_pass"][p]["items_W"][it]
        r = rails[it]
        R[p][it] = dict(r, board=b, off=b - r["noc"] - r["sram"] - r["minion"])
for col in ("board", "noc", "sram", "minion", "off"):
    out = []
    for w in (2, 4, 8, 16, 32, 64, 128, 256):
        x = np.array([K[n][w] for n in LAD])
        rms, slope = [], []
        for p in passes:
            y = np.array([R[p][n][col] for n in LAD])
            A = np.vstack([np.ones_like(x), x]).T
            c, *_ = np.linalg.lstsq(A, y, rcond=None)
            rms.append(float(np.sqrt(np.mean((A @ c - y) ** 2))))
            slope.append(c[1] / 1.17294e9 * 1e12)
        out.append((float(np.mean(rms)), w, float(np.mean(slope))))
    out.sort()
    print(col, " ".join("%d-way rms %.4f slope %.2f pJ" % (w, r, s) for r, w, s in out))
    # steps
    st = []
    for a_, b_ in (("dm_L2", "dm_L4"), ("dm_L4", "dm_L8"), ("dm_L8", "dm_L16"), ("dm_L16", "dm_L32"), ("dm_L32", "dm_L8192")):
        v = [R[p][b_][col] - R[p][a_][col] for p in passes]
        st.append("%s-%s %+.3f±%.3f" % (b_[3:], a_[3:], np.mean(v), 2.776 * np.std(v, ddof=1) / np.sqrt(len(v))))
    print("   steps:", " ".join(st))
