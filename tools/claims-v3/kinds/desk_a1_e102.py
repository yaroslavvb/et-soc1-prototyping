#!/usr/bin/env python3
"""E102 amendment A1: the desk evidence for a fix to the float trains, from E102's committed passes, written before any A1 data. Run from the repo's root; its output is desk_a1_e102.txt.

  [1] What a run reads about its neighbours: zero reads of different tiles stand next to each other in T's clusters at nearly the same power, so the difference of two neighbours, offsets removed, has no warm-up and no memory of a
      different step in it. That is the noise a dense design can reach. Against it: the scatter of the same reads about straight lines through the same tile's reads, 62 s apart, as the registered interpolation uses them.
  [2] How much of a read's departure is memory of the previous run's step: on the rail and the board, each T item's step minus that item's mean over passes, regressed on the previous run's step.
  [3] The warm-up curve the registered interpolation cuts across, and the error of a chord at T's spacing and at A1's.
"""
import csv
import json
import math
import statistics as st

D = "docs/reports/data/2026-11-01-e102-balanced-bit-prices/"
tiles = json.load(open("tools/claims-v3/kinds/e102/e102.json"))["tiles"]
rows = list(csv.DictReader(open(D + "runs.csv")))
for r in rows:
    r["pass"] = int(r["pass"])
    r["pos"] = int(float(r["pos"]))
    r["t0"] = float(r["t0_ms"])
    r["segment"] = int(float(r["segment"]))
    r["rail"] = float(r["rail_raw"])
    r["board"] = float(r["p_raw"])
T = (10220, 10221, 10222, 10223)
ZERO = ("fp32.hq", "fp32.aq", "fp16.hq", "fp16.aq")

print("[1] noise of neighbouring zero reads in the T clusters (offset per tile pair removed per pass-free mean), W a run: sd(difference)/sqrt(2)")
for arm in ("rail", "board"):
    diffs = {}
    for p in T:
        rr = sorted((r for r in rows if r["pass"] == p), key=lambda r: r["pos"])
        for a, b in zip(rr, rr[1:]):
            if a["item"] in ZERO and b["item"] in ZERO and a["segment"] != -1 and a["item"] != b["item"]:
                diffs.setdefault(tuple(sorted((a["item"], b["item"]))), []).append((b[arm] - a[arm]) * (1 if a["item"] < b["item"] else -1))
    pooled = []
    for k, v in diffs.items():
        m = st.mean(v)
        pooled += [x - m for x in v]
    print(f"  {arm}: {math.sqrt(sum(x * x for x in pooled) / max(len(pooled) - len(diffs), 1)) / math.sqrt(2):.3f} W a run, from {len(pooled)} neighbouring pairs of {len(diffs)} kinds")

print("[2] memory: T items, a read's departure from that item's mean over passes (after own-zero interpolation), against the previous run's mean step")
steps = {}
per = {}
for p in T:
    rr = sorted((r for r in rows if r["pass"] == p), key=lambda r: r["pos"])
    z = {}
    for r in rr:
        if r["item"] in tiles and tiles[r["item"]]["layout"] == "zero" and r["segment"] != -1:
            z.setdefault(r["item"], []).append(r)
    for r in rr:
        t = tiles.get(r["item"])
        if t and t["layout"] != "zero" and t["zero"] in z:
            for arm in ("rail", "board"):
                pts = sorted((q["t0"], q[arm]) for q in z[t["zero"]])
                zh = pts[0][1] if r["t0"] <= pts[0][0] else pts[-1][1]
                for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
                    if t1 <= r["t0"] <= t2:
                        zh = v1 + (v2 - v1) * (r["t0"] - t1) / (t2 - t1)
                r["step_" + arm] = r[arm] - zh
                per.setdefault((r["item"], arm), []).append(r["step_" + arm])
means = {k: st.mean(v) for k, v in per.items()}
for arm in ("rail", "board"):
    xs, ys = [], []
    for p in T:
        rr = sorted((r for r in rows if r["pass"] == p), key=lambda r: r["pos"])
        for a, b in zip(rr, rr[1:]):
            if "step_" + arm in b and (b["item"], arm) in means:
                prev = means.get((a["item"], arm), 0.0)
                xs.append(prev)
                ys.append(b["step_" + arm] - means[(b["item"], arm)])
    mx, my = st.mean(xs), st.mean(ys)
    sl = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    res = [y - my - sl * (x - mx) for x, y in zip(xs, ys)]
    print(f"  {arm}: slope {sl:+.3f} W per W of the previous run's step, over {len(xs)} reads; residual sd {st.pstdev(res):.3f} W, sd before {st.pstdev(ys):.3f} W")

print("[3] the warm-up the zeros follow: fp32.aq and fp32.hq at each read of each T pass, watts on the rail above that pass's last read of the tile, against seconds into the pass's measured part")
for z in ("fp32.aq", "fp32.hq"):
    for p in T:
        rr = sorted((r for r in rows if r["pass"] == p and r["item"] == z and r["segment"] != -1), key=lambda r: r["pos"])
        print(f"  {p} {z}: " + " ".join(f"{(r['t0'] - rr[0]['t0']) / 1000:4.0f}s:{r['rail'] - rr[-1]['rail']:+.2f}" for r in rr))
A, TAU = 2.2, 45.0     # board, the fit in check_e102.txt [M]
print(f"  a chord across a curve A exp(-t/tau), A = {A} W and tau = {TAU} s from check_e102.txt [M], at t seconds into the train, spacing h: the largest error is h^2/8 x A/tau^2 x exp(-t/tau)")
for h, name in ((62.0, "T: the same tile 13 runs apart"), (14.5, "A1: own zero every 2 items, 3 runs apart")):
    for t in (24.0, 60.0, 120.0):
        print(f"    {name}, at t = {t:.0f} s: {h * h / 8 * A / TAU / TAU * math.exp(-t / TAU):.3f} W")
