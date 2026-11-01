#!/usr/bin/env python3
"""Q132(g): the desk check behind "Corrections after verification". Every number those corrections quote, from committed files. No card, no new data. Post hoc, labelled, never a verdict.

    python3 corrections-check.py > corrections-check.txt          (from this directory; Python 3, no third-party modules)
"""
import glob
import gzip
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
T975_2DOF = 4.303


def rd(p):
    with (gzip.open(p, "rt") if p.endswith(".gz") else open(p)) as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    yield json.loads(ln)
                except ValueError:
                    pass


PC0 = json.load(open(os.path.join(HERE, "pmic-check.json")))
D = json.load(open(os.path.join(HERE, "drift-paired.json")))
REST = {e: D["rest"][e]["aifoundry2"]["cards"]["0"]["die"] for e in ("E80", "E83", "E87", "E64", "E69", "E84")}
PAIR = {k: v for k, v in D["pairs"].items()}

print("Q132(g) corrections-check. Inputs: drift-paired.json, camera-lines.json, pmic-check.json, ir-lattice.json, ir-hits.json, ir-tests.json, the committed telemetry of E64, E69, E80, E83, E84, E87.")

print("\n======== C1. The split between the hour and the day: not unique, and 'most' does not stand")
e64_e80, e87_e80, e64_e87 = PAIR["E64-E80"], PAIR["E87-E80"], PAIR["E64-E87"]
drest = REST["E64"] - REST["E80"]
print(f"rest die at each session's start, 30-5 min before its first run: { {k: round(v, 2) for k, v in REST.items()} } (the rest die is a proxy: the room itself was never read)")
print(f"E64 - E80: line {e64_e80['mean_c']:+.3f} +- {e64_e80['se_c']:.3f} C on {e64_e80['n']} kinds, rest die {drest:+.2f} C")
print(f"same hour, different day, E64 - E87 (both about 20:00): line {e64_e87['mean_c']:+.3f} +- {e64_e87['se_c']:.3f} C = {100 * e64_e87['mean_c'] / e64_e80['mean_c']:.0f}% of E64 - E80; rest die {REST['E64'] - REST['E87']:+.2f} C = {100 * (REST['E64'] - REST['E87']) / drest:.0f}%")
print(f"same day, different hour, E87 - E80: line {e87_e80['mean_c']:+.3f} +- {e87_e80['se_c']:.3f} C = {100 * e87_e80['mean_c'] / e64_e80['mean_c']:.0f}%; rest die {REST['E87'] - REST['E80']:+.2f} C = {100 * (REST['E87'] - REST['E80']) / drest:.0f}%")
CAM = json.load(open(os.path.join(HERE, "camera-lines.json")))
noon = next(r["rest_die"] for r in CAM["rows"] if r["session"] == "E63-s1")
print(f"the other path, through 23 Oct's own noon (E63 s1, rest die {noon:.2f} C): 23 Oct noon to 23 Oct 20:37 is {REST['E64'] - noon:+.2f} C = {100 * (REST['E64'] - noon) / drest:.0f}% of the rest die, the day (31 Oct noon to 23 Oct noon) {noon - REST['E80']:+.2f} C = {100 * (noon - REST['E80']) / drest:.0f}%. No line was measured at 23 Oct noon on these kinds")
print("so the hour's share of the rest die is 42% on one path and 86% on the other: the split is not unique")

print("\n======== C2. The slope: what the interval is on four sessions")
x = [REST[e] for e in ("E80", "E83", "E87", "E64")]
y = [0.0, PAIR["E83-E80"]["mean_c"], PAIR["E87-E80"]["mean_c"], PAIR["E64-E80"]["mean_c"]]
sy = [PAIR["E83-E80"]["se_c"], PAIR["E87-E80"]["se_c"], PAIR["E64-E80"]["se_c"]]
dx = [v - x[0] for v in x[1:]]
dy = y[1:]
print("inputs: rest die", [round(v, 2) for v in x], "; shifts from E80", [round(v, 3) for v in y], "; their s.e.", sy)


def fit(xs, ys, w=None):
    w = w or [1.0] * len(xs)
    W = sum(w)
    mx, my = sum(a * b for a, b in zip(w, xs)) / W, sum(a * b for a, b in zip(w, ys)) / W
    sxx = sum(a * (b - mx) ** 2 for a, b in zip(w, xs))
    b = sum(a * (u - mx) * (v - my) for a, u, v in zip(w, xs, ys)) / sxx
    c = my - b * mx
    return b, c, sxx, [v - (c + b * u) for u, v in zip(xs, ys)]


sw = sum(d * d / s ** 2 for d, s in zip(dx, sy))
sl = sum(d * e / s ** 2 for d, e, s in zip(dx, dy, sy)) / sw
print(f"through the origin, weighted, E80 held exact, the three shifts independent (what the README quoted; drift-paired.txt reads the same to rounding): {sl:.3f} +- {1 / math.sqrt(sw):.3f}, a formal 1 sigma")
b, c, sxx, res = fit(x, y)
se = math.sqrt(sum(r * r for r in res) / (len(x) - 2) / sxx)
print(f"free intercept, ordinary least squares on the four sessions: {b:.3f} +- {se:.3f} on 2 dof; 95% with t(2) = {T975_2DOF}: {b - T975_2DOF * se:.2f} to {b + T975_2DOF * se:.2f}; residuals {[round(r, 2) for r in res]} C")
# session-level noise: a shift's s.e. over a common baseline is sqrt(2) x a session's when the two are alike: E80, E83, E87 about 0.14, E64's the rest of 0.33
s0 = 0.14
sig = [s0, s0, s0, math.sqrt(max(sy[2] ** 2 - s0 ** 2, 0.0))]
b2, c2, sxx2, res2 = fit(x, y, [1 / s ** 2 for s in sig])
chi = sum(r * r / s ** 2 for r, s in zip(res2, sig))
print(f"free intercept, weighted with those s.e. split per session (E80, E83, E87 {s0}, E64 {sig[3]:.2f}): {b2:.3f}, s.e. {1 / math.sqrt(sxx2):.3f}, chi2 {chi:.2f} on 2 dof")
C = [[(sy[i] ** 2 if i == j else s0 ** 2) for j in range(3)] for i in range(3)]


def inv3(m):
    a, b0, c0, d, e, f, g, h, i = [m[r][k] for r in range(3) for k in range(3)]
    det = a * (e * i - f * h) - b0 * (d * i - f * g) + c0 * (d * h - e * g)
    return [[(e * i - f * h) / det, (c0 * h - b0 * i) / det, (b0 * f - c0 * e) / det], [(f * g - d * i) / det, (a * i - c0 * g) / det, (c0 * d - a * f) / det], [(d * h - e * g) / det, (b0 * g - a * h) / det, (a * e - b0 * d) / det]]


I = inv3(C)
den = sum(dx[i] * I[i][j] * dx[j] for i in range(3) for j in range(3))
num = sum(dx[i] * I[i][j] * dy[j] for i in range(3) for j in range(3))
print(f"through the origin, generalised least squares, E80's noise shared (s0 = {s0}): {num / den:.3f} +- {1 / math.sqrt(den):.3f}")
sw2 = sum(d * d / s ** 2 for d, s in zip(dx[:2], sy[:2]))
sl2 = sum(d * e / s ** 2 for d, e, s in zip(dx[:2], dy[:2], sy[:2])) / sw2
print(f"31 Oct alone (E83 and E87 over E80): {sl2:.3f} +- {1 / math.sqrt(sw2):.3f}, not separated from 0; it gives E64 {sl2 * dx[2]:+.2f} +- {dx[2] / math.sqrt(sw2):.2f} against {dy[2]:+.2f} +- {sy[2]:.2f}")
kinds = PAIR["E64-E80"]["by_kind"]
vals = list(kinds.values())
rest = [v for k, v in kinds.items() if k != "fp16/ones"]
print(f"E64 - E80 by kind: {kinds}; mean {st.mean(vals):.2f}, median {st.median(vals):.2f}, mean without fp16 ones {st.mean(rest):.2f}: one kind carries part of it")
ks = PAIR["E64-E87"]["by_kind"]
print(f"E64 - E87 by kind (the same-hour pair): {ks}; it has no fp16 ones")

print("\n======== C3. The two cards' readings: not shown to be one quantity")
S = {"E80": "2026-10-31-e80-kinds-speed/s1", "E83": "2026-10-31-e83-kinds-speed-rest/s1", "E87": "2026-10-31-e87-real-tensors-speed/s1", "E84": "2026-10-31-e84-speed-aifoundry1-card0/s1"}
WANT = {("fp16", "zeros"), ("fp32", "zeros"), ("int8", "zeros"), ("int8", "neg_ones"), ("int8", "full"), ("fp16", "ones"), ("fp32", "ones"), ("fp32", "sparse90")}
tab = {}
for name, d in S.items():
    base = os.path.join(DATA, d)
    for r in rd(os.path.join(base, "runs.jsonl")):
        k = (r.get("type"), (r.get("values") or "").split("/")[-1].replace(".bin", ""))
        if k not in WANT or "SUS" not in r["run"]:
            continue
        fs = glob.glob(os.path.join(base, "tel", r["run"] + ".jsonl*"))
        if not fs:
            continue
        rows = [x for x in rd(fs[0]) if x.get("t_ms") and x.get("board_w") is not None]
        if not rows:
            continue
        tl = r.get("t_last_ms") or rows[-1]["t_ms"]
        for x in rows:
            if tl - 40000 <= x["t_ms"] <= tl and (x.get("mhz") or {}).get("minion") == 800:
                sp = x.get("sp") or {}
                tab.setdefault(k, {}).setdefault(name, []).append((x["board_w"], (sp.get("minion_w") or [None])[0], (sp.get("sram_w") or [None])[0], (sp.get("noc_w") or [None])[0]))


def med(L, i):
    v = [q[i] for q in L if q[i] is not None]
    return st.median(v) if v else None


print("last 40 s of sustained runs, readings at 800 MHz only, medians. kind: card 0 board W, rails sum | aifoundry2 per session board W, rails sum | a2 minus c0")
pairs = []
gaps = []
railgaps = []
for k in sorted(tab):
    if "E84" not in tab[k]:
        continue
    c0 = med(tab[k]["E84"], 0)
    r0 = sum(med(tab[k]["E84"], i) or 0 for i in (1, 2, 3))
    a2 = {n: med(v, 0) for n, v in tab[k].items() if n != "E84"}
    if not a2:
        continue
    a2m = st.median(a2.values())
    r2v = [sum(med(v, i) or 0 for i in (1, 2, 3)) for n, v in tab[k].items() if n != "E84"]
    r2 = st.median(r2v)
    pairs.append((c0, a2m))
    gaps.append(a2m - c0)
    railgaps.append(r2 - r0)
    print(f"  {k[0]}/{k[1]:9s} c0 {c0:6.2f} W, rails {r0:6.2f} | a2 { {n: round(v, 2) for n, v in a2.items()} }, rails {r2:6.2f} | board {a2m - c0:+.2f} W, rails {r2 - r0:+.2f} W")
b3, a3, _, _ = fit([p[0] for p in pairs], [p[1] for p in pairs])
print(f"a2 = {a3:.2f} + {b3:.3f} x c0 over {len(pairs)} kinds; board gap {min(gaps):.1f} to {max(gaps):.1f} W, rails gap {min(railgaps):+.2f} to {max(railgaps):+.2f} W")
print(f"card 0's 75 W on aifoundry2's reading: {a3 + b3 * 75:.1f} W; 76.75 W: {a3 + b3 * 76.75:.1f} W; aifoundry2's 88.88 W on card 0's reading: {(88.88 - a3) / b3:.1f} W; aifoundry2's 75 W on card 0's: {(75 - a3) / b3:.1f} W (if the offset is the instrument; nothing here says whether it is real input power or a calibration)")
P800 = [(29.6, 34.1), (42.2, 48.9), (68.6, 76.1), (73.0, 82.7)]
b4, a4, _, _ = fit([p[0] for p in P800], [p[1] for p in P800])
print(f"E84's README, p800, the median in a run's first second at 800 MHz, card 0 against aifoundry2: fp32 zeros 29.6, 34.1; int8 full 42.2, 48.9; fp16 randn 68.6, 76.1; fp32 randn 73.0, 82.7; and its text gives 4.5-9.8 W over all kinds, zeros 4.5-5.1 W. Fit on those four: a2 = {a4:.2f} + {b4:.3f} x c0, so card 0's 75 W is {a4 + b4 * 75:.1f} W on aifoundry2's")
print(f"the register's top, 78.75 W, on card 0's reading, is {a3 + b3 * 78.75:.1f} W on aifoundry2's, and the setter's cap, 78 W, is {a3 + b3 * 78:.1f} W: so 'a set point above 88.88 W cannot be written' rules out 'set higher' only if the two readings are one quantity")
E84 = next(v for k, v in PC0["sessions"].items() if k.startswith("E84")) if isinstance(PC0.get("sessions"), dict) else None
print("card 0 in E84, from pmic-check.json:", {k: E84.get(k) for k in ("readings", "readings_ge75", "runs_ge75", "longest_ge75_s", "board_w_max") if k in E84} if E84 else "see pmic-check.txt")

print("\n======== C4, C5. Counts by threshold, every telemetry file of aifoundry2's sessions (three E69 runs have telemetry and no row in runs.jsonl)")
SESS = {"E64": ["2026-10-23-e64-horace-power-limit/s1", "2026-10-23-e64-horace-power-limit/s2"],
        "E69": [f"2026-10-27-e69-governor-knob/{x}" for x in ("s1", "s2", "s3", "smoke", "smoke2")],
        "E80": ["2026-10-31-e80-kinds-speed/s1"], "E83": ["2026-10-31-e83-kinds-speed-rest/s1"], "E87": ["2026-10-31-e87-real-tensors-speed/s1"]}
TH = (75, 85, 86, 88)
allc = {t: [0, 0, 0.0] for t in TH}
post = {t: [0, 0, 0.0] for t in TH}
tot = 0
at300 = 0
for e, dirs in SESS.items():
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(DATA, d, "tel", "*"))):
            rows = sorted([x for x in rd(f) if x.get("t_ms") and x.get("board_w") is not None], key=lambda x: x["t_ms"])
            tot += len(rows)
            at300 += sum(1 for x in rows if (x.get("mhz") or {}).get("minion") == 300)
            for t in TH:
                n, cur, lng = 0, 0, 0
                for x in rows:
                    if x["board_w"] >= t:
                        n += 1
                        cur += 1
                        lng = max(lng, cur)
                    else:
                        cur = 0
                if n:
                    for tgt in ([allc] if e == "E64" else [allc, post]):
                        tgt[t][0] += n
                        tgt[t][1] += 1
                        tgt[t][2] = max(tgt[t][2], lng * 0.1)
print(f"readings {tot}, at 300 MHz {at300}")
print("all five sessions: " + "; ".join(f">= {t} W: {allc[t][0]} readings in {allc[t][1]} runs, longest {allc[t][2]:.1f} s" for t in TH))
print("since aifoundry2's boot of 26 Oct, which the driver's counter covers (E69, E80, E83, E87; not E64): " + "; ".join(f">= {t} W: {post[t][0]} in {post[t][1]} runs, longest {post[t][2]:.1f} s" for t in TH))
PC = json.load(open(os.path.join(HERE, "pmic-check.json")))
T = PC["aifoundry2_total"]
print(f"pmic-check.json counts only runs with a row in runs.jsonl: {T['readings']} readings, {T['readings_ge75']} >= 75 W, {T['runs_ge75']} runs; of those runs the ring reaches back to the previous dump in {T['runs_ge75_ring_full']}")
print("driver counter PmicCeEvent on aifoundry2: host/err-aifoundry2.txt reads 0, since its boot of 26 Oct 15:13 PDT")

print("\n======== C6. What tests the idle-reset lattice out of sample")
IL = json.load(open(os.path.join(HERE, "ir-lattice.json")))
for e in ("E80", "E83", "E87"):
    s = IL["sessions"][e]
    print(f"{e}: {s['n_hits']} falls fix the lattice, residuals {s['host_res_ms']} ms; leave-one-out {s['host_loo_ms']} ms; within 1.2 ms {s['within_1p2ms']}; beyond {s['beyond_1p2ms']}")
print("so 16 of the 18 near-lattice falls fixed the lattice. Out of sample: leave-one-out residuals (largest 1.77 ms), the two kernel-rule falls not in any fit, and the process gaps: ir-gaps.json")
G = json.load(open(os.path.join(HERE, "ir-gaps.json")))
tt = {"True_True": 0, "True_False": 0, "False_True": 0, "False_False": 0}
for e, v in G.items():
    for k in tt:
        tt[k] += v["gaps"]["table"][k]
print(f"process gaps: point in gap and fell {tt['True_True']}, in gap no fall {tt['True_False']}, no point and fell {tt['False_True']}, no point no fall {tt['False_False']}: {tt['True_True'] + tt['False_False']} of {sum(tt.values())}")

print("\n======== C7. The 25 falls' x")
H = json.load(open(os.path.join(HERE, "ir-hits.json")))["hits"]
clean = [h for h in H if h.get("x_ms") is not None and -40 <= h["x_ms"] < 40 and h.get("prev_g") and h["prev_g"] >= 0.79]
xs = sorted(h["x_ms"] for h in clean)
print(f"{len(clean)} falls, x {xs} ms: {sum(1 for v in xs if -1 <= v <= 14)} within -1 to 14 ms; the other: {[(h['exp'], h['run'], h['kernel'], h['x_ms'], h['k_g']) for h in clean if not -1 <= h['x_ms'] <= 14]}")

print("\n======== C8. No dependence visible, from 25 falls; E100's A0 beside the rate")
IT = json.load(open(os.path.join(HERE, "ir-tests.json")))
print("Monte Carlo p:", {k: v["p"] for k, v in IT["tests"].items()})
print("format:", IT["tests"]["format"]["rows"])
print(f"all six sessions: {IT['total_hits']} falls in {sum(v['exposed'] for v in IT['sessions'].values())} boundaries, 1 in {sum(v['exposed'] for v in IT['sessions'].values()) / IT['total_hits']:.0f}")
E100 = os.path.join(DATA, "2026-11-01-e100-idle-reset", "corrections-check.txt")
print("E100's A0, its corrections-check.txt says:", next((x.strip() for x in open(E100) if x.startswith("A0's boundaries")), "(not found)") if os.path.exists(E100) else "(run that first)")
print("compatible with about 1 in 500, and no further support")
print("\n======== C9. Near-steady blocks against the 76 s line: unexplained")
m = CAM["means_192"]
s1 = [r for r in CAM["rows"] if r["session"] == "E63-s1"]
off0 = st.mean(r["off"] for r in s1)
for e in ("E73", "E85"):
    print(f"{e}: offset {m[e]['off']:.2f} at rest {m[e]['rest_die']:.2f}; against E63 s1 ({off0:.2f} at {s1[0]['rest_die']:.2f}): {(m[e]['off'] - off0) / (m[e]['rest_die'] - s1[0]['rest_die']):.2f} C per C")

print("\n======== C10. Horace He's pair: the arithmetic (the post and the gist as read on 1 Nov 2026; neither is committed here, the gist's numbers are in README section d)")
print(f"the post's text, 295 / 257 = {295 / 257:.3f}; 258 / 312 = {258 / 312:.3f}, the post's '83% flop utilization' on the A100's 16-bit peak of 312")
print(f"the gist's two comment images: 292.30 / 239.41 = {292.30 / 239.41:.3f}; 291.63 / 240.43 = {291.63 / 240.43:.3f}")
print(f"the post's chart, from horace-chart.txt: 287.69 / 236.47 = {287.69 / 236.47:.4f}")
print("in the post: no format is named anywhere; the story opens \"It's 2022\"; its first run is 8192 x 8192 x 8192 (python mm_bench.py, not public); the pair's snippet that follows has a bare N. The post does not link the gist; the gist's description is the post's title and link")
print("formats: bf16 has 8 exponent and 7 mantissa bits, fp16 5 and 10")
