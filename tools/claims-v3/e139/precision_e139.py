#!/usr/bin/env python3
"""E139 precision, before any E139 pass: from E132's six headline passes (its committed e132.json, per_pass), each unresolved
quantity's per-pass mean and sd, the projected 95% half-width at E139's headline n, and the chance (normal draws at E132's mean and
sd, 20,000 sessions, seed 139) that R3's and R4's registered classes resolve. Desk only; nothing here is a measurement.

    python3 tools/claims-v3/e139/precision_e139.py docs/reports/data/2026-11-02-e132-memory-split/e132.json tools/claims-v3/e132/predictions.json
"""
import json, math, random, statistics, sys

T = {3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306, 10: 2.262, 11: 2.228, 12: 2.201, 13: 2.179, 14: 2.160}
d = json.load(open(sys.argv[1])); P = json.load(open(sys.argv[2]))
heads = [str(p) for p in d["passes_headline"]]
def series(meter, key): return [d["per_pass"][p]["contrasts"][meter][key] for p in heads]
Q = [("board", "E56"), ("board", "E448"), ("ddr_mv", "el_64z"), ("ddr_mv", "RE64"), ("ddr_mv", "eh_64z"), ("ddr_mv", "wl_64z")]
stats = {}
print("E132 headline passes:", ",".join(heads))
for m, k in Q:
    v = series(m, k); mu = statistics.mean(v); sd = statistics.stdev(v); stats[(m, k)] = (mu, sd)
    print("%-7s %-7s mean %+.4f sd %.4f  hw n=6 %.4f" % (m, k, mu, sd, T[5] * sd / math.sqrt(6)) +
          "".join("  n=%d %.4f" % (n, T[n - 1] * sd / math.sqrt(n)) for n in (7, 8, 13, 14)))
def ci(v):
    n = len(v); mu = statistics.mean(v); h = T[n - 1] * statistics.stdev(v) / math.sqrt(n); return mu - h, mu + h
mv, st = P.get("ddr_moves_mV", 0.30), P.get("ddr_still_half_mV", 0.30)
def ddr(lo, hi, mu):
    if mu <= -mv and hi < 0: return "moves"
    if lo >= -st and hi <= st: return "still"
    return "unresolved"
rng = random.Random(139)
print("constants: ddr moves at mean <= -%.2f mV with the interval below 0, still inside +-%.2f mV; E56/E448 present when the interval is above 0" % (mv, st))
for n in (7, 8, 13, 14):
    r3 = r4 = e56 = el = 0; N = 20000
    for _ in range(N):
        draw = {q: [rng.gauss(stats[q][0], stats[q][1]) for _ in range(n)] for q in stats}
        c = {q: ci(draw[q]) + (statistics.mean(draw[q]),) for q in stats}
        cl = {q[1]: ddr(*c[q]) for q in stats if q[0] == "ddr_mv"}
        if cl["wl_64z"] == "moves" and cl["RE64"] == "moves" and cl["el_64z"] == "still": r3 += 1
        if cl["el_64z"] == "still": el += 1
        a = c[("board", "E56")][0] > 0; b = c[("board", "E448")][0] > 0
        e56 += a; r4 += a and b
    print("n=%2d: R3 ENCODED %.1f%% (el_64z still %.1f%%); R4 PAYS %.1f%% (E56 present %.1f%%)" % (n, 100 * r3 / N, 100 * el / N, 100 * r4 / N, 100 * e56 / N))
