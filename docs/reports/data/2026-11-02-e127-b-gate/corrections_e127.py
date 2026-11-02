#!/usr/bin/env python3
"""E127, corrections after verification (Mon 2 Nov 2026), post hoc and labelled, never a verdict: the numbers the README's
"Corrections after verification" section quotes, from committed files only (scored.json, the tiles' bytes).

    python3 docs/reports/data/2026-11-02-e127-b-gate/corrections_e127.py > docs/reports/data/2026-11-02-e127-b-gate/corrections_e127.txt

1. q_blk (R5's tile): what "SHORT" leaves. Q4 measured and its excess, the tiles' D, and e(Q4) - e(Q3) paired inside each pass.
2. Lane position (R6's contrast): Q5 and e(Q5) with their 95% intervals, and R6 at every arm.
3. Lane position's share of the other contrasts, IF it adds per live lane-cycle (an assumption, not tested): from the tiles'
   bytes, the share of each tile's live lane-cycles on lanes 0-3 (make_kinds.issue_streams: lane l carries B[k][8h + l];
   a lane is off when its 32-bit B word is zero, every A word here being nonzero), so each contrast carries
   (share(plus) - share(minus)) x Q5. Netting that out of Q2 gives the per-flip price without it.
4. fp16 against fp32 with the data still: R3's ratio, and e(Q1) - e(F2) paired.
5. What the per-flip price is "beyond": Q2 measured, M5's price for it, and both per flip.
Every interval: t(4) x sd / sqrt(5) over the five kept passes, the registration's form. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import statistics as st
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
S = json.load(open(os.path.join(HERE, "scored.json")))
P = S["primary"]
C, T = P["contrasts"], P["table"]
T4 = 2.776                                    # t(0.975, 4), score_e127.py's T975[4]
RATE = 600e6 / 546 * 1024 * 0.9963            # ops a second, as posthoc_e127.py (fit_m5.RATE)
FLIPS = 4096                                  # gate flips an op in q_chk (e127-tiles.json)
N = 16


def c(k):
    return next(v for n, v in C.items() if n.startswith(k + ":"))


def ci(v):
    m = sum(v) / len(v)
    h = T4 * st.stdev(v) / math.sqrt(len(v))
    return m, m - h, m + h


def show(name, v, unit="W", f=1.0):
    m, lo, hi = ci([x * f for x in v])
    print(f"  {name:66s} {m:+.3f} [{lo:+.3f}, {hi:+.3f}] {unit}")
    return m, lo, hi


def exc(k):
    return c(k)["excess_per_pass_w"]


def meas(k):
    return c(k)["per_pass_w"]


print("1. q_blk, R5's tile (data still; lanes off 32 cycles, live 32, all eight together)")
show("Q4 = q_blk - q_steady, measured", meas("Q4"))
print(f"  M5's frozen point for Q4: {c('Q4')['M5_w']:+.3f} W")
show("e(Q4), its excess over M5", exc("Q4"))
show("e(Q3), the all-off part (q_alt - q_chk, equal flips)", exc("Q3"))
show("e(Q4) - e(Q3), paired inside each pass", [a - b for a, b in zip(exc("Q4"), exc("Q3"))])
for n in ("fp32.q_steady", "fp32.q_steady_hi", "fp32.q_blk"):
    print(f"  D {n:18s} {T[n]['D']:.3f} +- {T[n]['ci95']:.3f} W")
print(f"  the per-flip part at q_blk's 128 flips an op, at e(Q2)'s price: {c('Q2')['excess_w'] / FLIPS * 128:+.3f} W")

print("\n2. Lane position, R6's contrast (data still)")
show("Q5 = q_steady_hi - q_steady, measured", meas("Q5"))
show("e(Q5)", exc("Q5"))
r6 = P["rules"]["E127-R6"]
print(f"  R6 {r6['verdict']} on the primary (|Q5| + h = {abs(r6['measured_w']) + r6['ci95_w']:.3f} W <= 0.30); "
      f"at the arms: " + ", ".join(f"{a} {v['rules']['E127-R6']['verdict']}" for a, v in S["arms"].items()))

print("\n3. Lane position's share of the other contrasts, if it adds per live lane-cycle (assumed, not tested)")
TILES = {"fp32.q_steady": "tools/claims-v3/e127/tiles/fp32/q_steady.bin",
         "fp32.q_steady_hi": "tools/claims-v3/e127/tiles/fp32/q_steady_hi.bin",
         "fp32.q_chk": "tools/claims-v3/e127/tiles/fp32/q_chk.bin",
         "fp32.q_alt": "tools/claims-v3/e127/tiles/fp32/q_alt.bin",
         "fp32.q_blk": "tools/claims-v3/e127/tiles/fp32/q_blk.bin",
         "fp32.g_blanes_chk": "tools/claims-v3/e127/tiles/fp32/g_blanes_chk.bin",
         "fp32.g_blanes_steady": "tools/claims-v3/kinds/blind3/tiles/fp32/g_blanes_steady.bin",
         "fp32.g_blanes_alt": "tools/claims-v3/kinds/blind3/tiles/fp32/g_blanes_alt.bin"}
share = {}
for n, rel in TILES.items():
    raw = open(os.path.join(ROOT, rel), "rb").read()
    w = struct.unpack("<512I", raw)
    aw, bw = w[:256], w[256:]
    live_lo = live = 0
    for k in range(N):
        for i in range(N):
            a = aw[i * N + k]                              # A = Aword[i][k] broadcast (make_kinds.issue_streams)
            for h in (0, 1):
                for l in range(8):
                    on = a != 0 and bw[k * N + 8 * h + l] != 0
                    live += on
                    live_lo += on and l < 4
    share[n] = live_lo / live
    print(f"  {n:22s} live lane-cycles an op {live:4d}; on lanes 0-3: {share[n]:.3f}")
q5 = exc("Q5")
for k in ("Q1", "Q2", "Q3", "Q4", "B1", "B2", "B3"):
    v = c(k)
    f = share[v["plus"]] - share[v["minus"]]
    print(f"  {k}: carries {f:+.2f} x e(Q5) = {f * c('Q5')['excess_w']:+.3f} W of lane position" +
          (" (random data: only if lane position is the same there; no random q_steady_hi was run)" if k[0] == "B" else ""))
adj2 = [a - 0.5 * b for a, b in zip(exc("Q2"), q5)]
adj1 = [a - 0.5 * b for a, b in zip(exc("Q1"), q5)]
show("e(Q2) - 1/2 e(Q5): the per-lane part without lane position", adj2)
show("  the same per lane-gate flip", adj2, "fJ per flip", 1e15 / (FLIPS * RATE))
show("  e(Q2) per lane-gate flip, as posthoc_e127.txt section 2", exc("Q2"), "fJ per flip", 1e15 / (FLIPS * RATE))
show("e(Q1) - 1/2 e(Q5): the whole quiet miss without lane position", adj1)
print(f"  per-lane share of the quiet miss without lane position: {ci(adj2)[0] / ci(adj1)[0]:.3f} "
      f"(with it, posthoc_e127.txt: {c('Q2')['excess_w'] / c('Q1')['excess_w']:.3f})")
b1 = [a - 0.5 * b for a, b in zip(exc("B1"), q5)]
b3 = [a - 0.5 * b for a, b in zip(exc("B3"), q5)]
print(f"  random data, if the same term applies there: per-lane share {ci(b3)[0] / ci(b1)[0]:.3f} "
      f"(with it: {c('B3')['excess_w'] / c('B1')['excess_w']:.3f}); R2's ratio e(Q1)/e(B1) {ci(adj1)[0] / ci(b1)[0]:.3f} "
      f"(with it: {c('Q1')['excess_w'] / c('B1')['excess_w']:.3f})")
show("e(Q4) - 1/2 e(Q5) - e(Q3), paired", [a - 0.5 * b - d for a, b, d in zip(exc("Q4"), q5, exc("Q3"))])

print("\n4. fp16 against fp32, data still")
r3 = P["rules"]["E127-R3"]
print(f"  R3: e(F2) {r3['excess_w']:+.3f} [{r3['excess_lo95']:+.3f}, {r3['excess_hi95']:+.3f}] W against e(F1) "
      f"{r3['reference_excess_w']:+.3f}; ratio {r3['ratio']['ratio']:.3f} [{r3['ratio']['lo95']:.3f}, {r3['ratio']['hi95']:.3f}]")
r2 = P["rules"]["E127-R2"]
print(f"  R2: ratio {r2['ratio']['ratio']:.3f} [{r2['ratio']['lo95']:.3f}, {r2['ratio']['hi95']:.3f}]")
show("e(Q1) - e(F2), paired: the quiet miss in watts, fp32 against fp16", [a - b for a, b in zip(exc("Q1"), exc("F2"))])

print("\n5. What the per-flip price is beyond (Q2 = q_chk - q_steady)")
q2 = c("Q2")
pf = 1e15 / (FLIPS * RATE)
print(f"  Q2 measured {q2['measured_w']:+.3f} W = {q2['measured_w'] * pf:.0f} fJ a flip if all of it were the flips; "
      f"M5 prices {q2['M5_w']:+.3f} W of it (its bus and rest terms; M5 has no per-flip term); "
      f"the excess {q2['excess_w']:+.3f} W = {q2['excess_w'] * pf:.0f} fJ a flip, the post hoc price beyond M5")
