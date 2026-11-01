#!/usr/bin/env python3
"""E98 (Q132): the desk check behind the README's "Corrections after verification". Every number that section quotes, recomputed from committed files only:
this directory, the earlier sessions' results, the desk lane's raw history (live-history/*.tgz) and the night's other experiments' telemetry. Labelled: nothing here
is a registered rule or changes a verdict. Standard library only. It needs no card.

    python3 docs/reports/data/2026-11-01-e98-heat-path-drift/corrections-check.py > docs/reports/data/2026-11-01-e98-heat-path-drift/corrections-check.txt
"""
import glob
import gzip
import io
import json
import math
import os
import re
import statistics as st
import tarfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
DESK = os.path.join(DATA, "2026-11-01-q132-governor-desk")
R = json.load(open(os.path.join(HERE, "results.json")))
P = {p["probe"]: p for p in R["probes"]}
FULL = ["P1", "P3", "P6", "P7"]
LATER = ["P3", "P6", "P7"]
ALL5 = ["P1", "P2", "P3", "P6", "P7"]
KLINE, WPC = 0.4573, 0.2315
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365}


def ols(xs, ys):
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pts)
    mx, my = st.mean(p[0] for p in pts), st.mean(p[1] for p in pts)
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    res = [y - my - b * (x - mx) for x, y in pts]
    s = math.sqrt(sum(r * r for r in res) / (n - 2)) if n > 2 else None
    se = s / math.sqrt(sxx) if s is not None else None
    tq = T975.get(n - 2)
    return {"b": round(b, 3), "lo": round(b - tq * se, 3) if se is not None else None, "hi": round(b + tq * se, 3) if se is not None else None,
            "s": round(s, 4) if s is not None else None, "n": n, "sxx": round(sxx, 4), "lev": [round(1 / n + (x - mx) ** 2 / sxx, 3) for x, _ in pts]}


def run(p, i):
    return P[p]["runs"].get(str(i)) or {}


def hm(ms):
    return time.strftime("%H:%M:%S", time.gmtime(ms / 1000))


x20 = {p: P[p]["rest_die_w_derived"] for p in P}
x60 = {p: P[p]["rest60"]["w"] / WPC for p in P}
xraw = {p: P[p]["rest20"]["die"] for p in P}
dx = x20["P1"] - st.mean(x20[p] for p in LATER)
hold = {p: P[p]["hold"]["die"] for p in FULL}
dh = hold["P1"] - st.mean(hold[p] for p in LATER)
end_ms = {p: [q for q in P[p]["queue"] if q.get("kind") == "end"][0]["t_ms"] for p in ALL5}
snap = {p: json.load(open(os.path.join(HERE, p, "snapshot-start.json")))["t_ms"] for p in ALL5}

# ---------------------------------------------------------------------------------------- the earlier sessions
SESS = [("E64", "2026-10-23-e64-horace-power-limit/results.json", 49.28), ("E80", "2026-10-31-e80-kinds-speed/results.json", 45.58),
        ("E83", "2026-10-31-e83-kinds-speed-rest/results.json", 46.42), ("E87", "2026-10-31-e87-real-tensors-speed/results.json", 47.15),
        ("E96", "2026-11-01-e96-real-tensors-speed/results.json", 46.79)]


def norm(r):
    t, v = r.get("type"), str(r.get("values")).split("/")[-1].replace(".bin", "")
    return f"{t}/{'full' if t == 'int8' and v == 'randn' else v}"


S = {}
for name, f, d in SESS:
    k = {}
    for r in json.load(open(os.path.join(DATA, f)))["runs"]:
        if str(r.get("block", "")).startswith("SUS") and r.get("sus_w_mean") is not None:
            k.setdefault(norm(r), []).append((r["sus_w_mean"], r["sus_die_mean"], r["sus_mhz_mean"]))
    S[name] = (d, k)
for p in FULL:
    k = {}
    for i in range(1, 9):
        r = run(p, i)
        k.setdefault(r["kind"], []).append((r["w"], r["die"], r["mhz"]))
    S[p] = (xraw[p], k)


def mean_of(name, kind, j):
    return st.mean(v[j] for v in S[name][1][kind])


def line_of(name, kind):
    return st.mean(v[1] - KLINE * v[0] for v in S[name][1][kind])


print("C1. fp16 ones across sessions, on the raw rest die: what E64 carries")
for lab, names in (("all six", ["E64", "E80"] + FULL), ("without E64", ["E80"] + FULL), ("the night alone", FULL)):
    xs = [S[n][0] for n in names]
    a, b = ols(xs, [mean_of(n, "fp16/ones", 2) for n in names]), ols(xs, [mean_of(n, "fp16/ones", 0) for n in names])
    print(f"  {lab:16s} {names} MHz/C {a['b']} [{a['lo']}, {a['hi']}]; W/C {b['b']} [{b['lo']}, {b['hi']}]; leverage {dict(zip(names, a['lev']))}")
d = S["E64"][0] - S["E80"][0]
m64, m80, w64, w80 = mean_of("E64", "fp16/ones", 2), mean_of("E80", "fp16/ones", 2), mean_of("E64", "fp16/ones", 0), mean_of("E80", "fp16/ones", 0)
print(f"  E64 to E80 alone: {m80 - m64:+.1f} MHz, {w80 - w64:+.2f} W over {d:.2f} C: {(m64 - m80) / d:.1f} MHz/C, {(w64 - w80) / d:.2f} W/C")
mp1, ml = st.mean(v[2] for v in S["P1"][1]["fp16/ones"]), st.mean(st.mean(v[2] for v in S[p][1]["fp16/ones"]) for p in LATER)
print(f"  the night's step: {mp1 - ml:+.2f} MHz for {xraw['P1'] - st.mean(xraw[p] for p in LATER):+.2f} C of raw rest die, {dx:+.3f} C W-derived; one probe against three")
txt = open(os.path.join(DESK, "drift-paired.txt")).read()
m = re.search(r"E69\s+Tue 27 Oct 14:24\s+([\d.]+)\s+([\d.]+)", txt)
e69 = open(os.path.join(DATA, "2026-10-27-e69-governor-knob/README.md")).read()
mm = re.search(r"sustained `ones`, TDP 65 / thr 65[^|]*\| ([\d.]+) MHz \| \*\*([\d.]+) MHz", e69)
mw = re.search(r"its board power over the same window \| ([\d.]+) W \| \*\*([\d.]+) W", e69)
de, dw, dt = float(mm.group(2)) - float(mm.group(1)), float(mw.group(2)) - float(mw.group(1)), 49.28 - float(m.group(2))
print(f"  E69 (held out of the fit) minus E64, fp32 ones, from E69's README: {de:+.1f} MHz, {dw:+.2f} W, for a rest die {dt:.2f} C cooler (the desk's {m.group(2)} C): {-de / dt:.1f} MHz/C, {-dw / dt:.2f} W/C. Against E64 again.")

print("\nC2. The rate. Like for like on the trip kinds, and what the rest die's own noise adds")
two = ["int8/full", "fp32/randn"]
tl = {n: st.mean(line_of(n, k) for k in two) for n in S}
a = ols([S[n][0] for n in FULL], [tl[n] for n in FULL])
b = ols([S[n][0] for n in ("E64", "E80", "E83", "E87", "E96")], [tl[n] for n in ("E64", "E80", "E83", "E87", "E96")])
print(f"  mean line of int8 full and fp32 randn on the raw rest die: the night {a['b']} [{a['lo']}, {a['hi']}], earlier five {b['b']} [{b['lo']}, {b['hi']}]")
print(f"  at {a['b']} E64's line would sit {a['b'] * d:.2f} C above E80's; it sits {tl['E64'] - tl['E80']:.2f} C above")
print(f"  frozen rates: line {R['R1']['fit']['slope']:.2f} against 0.25; hold {R['R2']['fit']['slope']:.2f} against the room's 1.12")
s_p1, s_l = 0.060 / WPC, 0.040 / WPC
print(f"  rest-die noise of the contrast: P1's 10 min of rows about 0.06 W, a 20 min mean about 0.04 W (tools/claims-v3/kspeed/e98/desk/rest_window.txt): {math.hypot(s_p1, s_l / math.sqrt(3)):.3f} C of {dx:.3f} C = {100 * math.hypot(s_p1, s_l / math.sqrt(3)) / dx:.0f}% at 1 sigma on every ratio")

print("\nC3. S4's other readings, and its width")
mhz = {p: st.mean(run(p, i)["mhz"] for i in (5, 8)) for p in FULL}
wt = {p: st.mean(run(p, i)["w"] for i in (5, 8)) for p in FULL}
for lab, xm in (("20 min, W-derived (registered)", x20), ("raw history die", xraw), ("60 s rest", x60)):
    a, b = ols([xm[p] for p in FULL], [mhz[p] for p in FULL]), ols([xm[p] for p in FULL], [wt[p] for p in FULL])
    print(f"  {lab:32s} MHz/C {a['b']} [{a['lo']}, {a['hi']}], residual {a['s']} MHz; W/C {b['b']} [{b['lo']}, {b['hi']}]")
sx = math.sqrt(ols([x20[p] for p in FULL], [mhz[p] for p in FULL])["sxx"])
print(f"  half-width on the registered 16 MHz a probe (README, S4's line): +-{T975[2] * 16 / sx:.0f} MHz/C")

print("\nC4. R1's interval, the positions' scatter on n - 2 (checks.txt K2 used rms over n), and how near the label sits to its edge")
pos = []
for i in range(1, 9):
    f = ols([x20[p] for p in FULL], [run(p, i)["line"] for p in FULL])
    pos.append(f["s"])
s_pos = math.sqrt(st.mean(v * v for v in pos) / 8)
f1 = R["R1"]["fit"]
sxx = ols([x20[p] for p in FULL], [0.0, 1.0, 2.0, 3.0])["sxx"]
hw = T975[2] * s_pos / math.sqrt(sxx)
print(f"  per position s (n - 2): {[round(v, 3) for v in pos]}; a probe's s, as if independent: {s_pos:.4f} C; half-width {hw:.3f}: [{f1['slope'] - hw:.3f}, {f1['slope'] + hw:.3f}] (a lower bound: positions within a probe are not independent)")


def r1_with(field):
    per = {}
    for p in FULL:
        ks = {}
        for i in range(1, 9):
            ks.setdefault(run(p, i)["kind"], []).append(field(p, i))
        per[p] = {k: st.mean(v) for k, v in ks.items()}
    c = {k: st.mean(per[p][k] for p in FULL) for k in per["P1"]}
    return ols([x20[p] for p in FULL], [st.mean(per[p][k] - c[k] for k in c) for p in FULL])


for k in (0.40, KLINE, 0.50):
    f = r1_with(lambda p, i: run(p, i)["die"] - k * run(p, i)["w"])
    print(f"  R1 at k {k}: {f['b']} [{f['lo']}, {f['hi']}]")
allw = {}
for p in FULL:
    laun = {}
    for ln in gzip.open(os.path.join(HERE, p, "launches.jsonl.gz"), "rt"):
        L = json.loads(ln)
        if L.get("role") == "work":
            laun.setdefault(L["run"], []).append(L)
    for i in range(1, 9):
        name = run(p, i)["run"]
        t1 = max(L["t_end_ms"] for L in laun[name])
        rows = [json.loads(s) for s in gzip.open(os.path.join(HERE, p, "tel", name + ".jsonl.gz"), "rt") if s.startswith("{")]
        v = [r for r in rows if t1 - 40000 <= r["t_ms"] <= t1]
        allw[(p, i)] = st.mean(r["temp_c"]["minshire"][0] for r in v) - KLINE * st.mean(r["board_w"] for r in v)
f = r1_with(lambda p, i: allw[(p, i)])
print(f"  R1 with every sample of the window, not only those inside kernels: {f['b']} [{f['lo']}, {f['hi']}]")
print("  the sessions' own k: " + ", ".join(f"{a} {b}" for a, b in re.findall(r"^(E\d+)\s+aifoundry2.*?\+ ([\d.]+) W, rms", open(os.path.join(DESK, "die-lines.txt")).read(), re.M)) + "; E96 0.4539 (its README); the frozen k 0.4573")

print("\nC5. What ran beside the probes, and what the boxes' history says it could do to this card's idle reading")
LIVE = {}
for b in ("aifoundry1", "aifoundry2", "aifoundry3"):
    rows = []
    with tarfile.open(os.path.join(DESK, "live-history", b + ".tgz")) as t:
        for m in t.getmembers():
            if m.isfile():
                for ln in io.TextIOWrapper(t.extractfile(m)):
                    try:
                        rows.append(json.loads(ln))
                    except ValueError:
                        pass
    for f in glob.glob(os.path.join(HERE, "history", b + "-*.jsonl.gz")):
        rows += [json.loads(s) for s in gzip.open(f, "rt")]
    LIVE[b] = sorted(rows, key=lambda r: r["t"])
print(f"  rows: {[(b, len(v)) for b, v in LIVE.items()]}, {hm(LIVE['aifoundry2'][0]['t'])} on the first day to {hm(LIVE['aifoundry2'][-1]['t'])} on the last")


def card(r, n):
    return next((c for c in (r.get("cards") or []) if c.get("n") == n), {})


def minutes(rows, f):
    dd = {}
    for r in rows:
        v = f(r)
        if v is not None:
            dd.setdefault(r["t"] // 60000, []).append(v)
    return {k: sum(v) / len(v) for k, v in dd.items()}


A2 = minutes(LIVE["aifoundry2"], lambda r: card(r, 0).get("w") if not card(r, 0).get("held") else None)
A2h = minutes(LIVE["aifoundry2"], lambda r: 1.0 if card(r, 0).get("held") else 0.0)
A1h = minutes(LIVE["aifoundry1"], lambda r: 1.0 if card(r, 0).get("held") or card(r, 1).get("held") else 0.0)
A3h = minutes(LIVE["aifoundry3"], lambda r: 1.0 if card(r, 0).get("held") else 0.0)


def wm(dd, a, b):
    v = [dd[k] for k in range(a, b) if k in dd]
    return (sum(v) / len(v), len(v)) if v else (None, 0)


def solve(XtX, Xty):
    n = len(XtX)
    M = [row[:] + [y] for row, y in zip(XtX, Xty)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[piv] = M[piv], M[i]
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]
                for c in range(i, n + 1):
                    M[r][c] -= f * M[i][c]
    return [M[i][n] / M[i][i] for i in range(n)]


keys = sorted(A2)
X, Y = [], []
k = keys[0] + 200
while k < keys[-1]:
    a = k - 10
    b = a - 60
    ya, na = wm(A2, a, a + 10)
    yb, nb = wm(A2, b, b + 10)
    if na >= 7 and nb >= 7 and not any(A2h.get(i, 0) > 0.5 for i in range(b - 15, b + 10)) and not any(A2h.get(i, 0) > 0.5 for i in range(a - 15, a + 10)):
        h1a, h1b = wm(A1h, a - 30, a + 10)[0], wm(A1h, b - 30, b + 10)[0]
        h3a, h3b = wm(A3h, a - 30, a + 10)[0], wm(A3h, b - 30, b + 10)[0]
        if None not in (h1a, h1b, h3a, h3b):
            hod = (k * 60 % 86400) / 86400 * 2 * math.pi
            X.append([1.0, h1a - h1b, h3a - h3b, math.sin(hod), math.cos(hod), math.sin(2 * hod), math.cos(2 * hod)])
            Y.append(ya - yb)
    k += 60
pp = len(X[0])
XtX = [[sum(x[i] * x[j] for x in X) for j in range(pp)] for i in range(pp)]
Xty = [sum(x[i] * y for x, y in zip(X, Y)) for i in range(pp)]
bb = solve(XtX, Xty)
res = [y - sum(u * v for u, v in zip(bb, x)) for x, y in zip(X, Y)]
s2 = sum(r * r for r in res) / (len(Y) - pp)
Cinv = [solve(XtX, [1.0 if i == j else 0.0 for i in range(pp)]) for j in range(pp)]
se = [math.sqrt(s2 * Cinv[i][i]) for i in range(pp)]
print(f"  60 min differences of a2's idle W (rested 15 min at both ends) on each box's held share (30 min before), with the hour of day, n {len(Y)}:")
extra = dh - dx
ub1, ub3 = (bb[1] + 2 * se[1]) / WPC, (bb[2] + 2 * se[2]) / WPC
print(f"    aifoundry1 held +1: {bb[1]:+.3f} W [{bb[1] - 2 * se[1]:+.3f}, {bb[1] + 2 * se[1]:+.3f}], {bb[1] / WPC:+.2f} C [{(bb[1] - 2 * se[1]) / WPC:+.2f}, {ub1:+.2f}]")
print(f"    aifoundry3 held +1: {bb[2]:+.3f} W [{bb[2] - 2 * se[2]:+.3f}, {bb[2] + 2 * se[2]:+.3f}], {bb[2] / WPC:+.2f} C [{(bb[2] - 2 * se[2]) / WPC:+.2f}, {ub3:+.2f}]")
print(f"    P1's extra degree (hold's lead minus the rest die's): {dh:.2f} - {dx:.2f} = {extra:.2f} C. Upper limits at P1's hold's end, aifoundry1 alone {ub1:.2f} C = {100 * ub1 / extra:.0f}%; both {ub1 + max(ub3, 0):.2f} C = {100 * (ub1 + max(ub3, 0)) / extra:.0f}%. Best estimates are both below 0.")
DIRS = {"E92": "2026-11-01-e92-sign-split", "E93": "2026-11-01-e93-zero-gate-silicon", "E94": "2026-11-01-e94-tile-spread", "E95": "2026-11-01-e95-real-tensors-energy",
        "E97": "2026-11-01-e97-heat-low-power-steady", "E99": "2026-11-01-e99-dram-mechanism"}
wins = {}
for p in FULL:
    wins[p + " work"] = (P[p]["t_rest_ms"], end_ms[p])
    wins[p + " hold's last 2 min"] = (end_ms[p] - 130000, end_ms[p] - 10000)
tot = {}
for e, dn in DIRS.items():
    files = set(glob.glob(os.path.join(DATA, dn, "**", "tel", "*"), recursive=True)) | set(glob.glob(os.path.join(DATA, dn, "**", "*tel*.jsonl*"), recursive=True))
    for f in files:
        if not os.path.isfile(f):
            continue
        try:
            op = gzip.open if f.endswith(".gz") else open
            for s in op(f, "rt"):
                if not s.startswith("{"):
                    continue
                r = json.loads(s)
                w, t = r.get("board_w"), r.get("t_ms")
                if w is None or t is None:
                    continue
                for lab, (a, b) in wins.items():
                    if a <= t < b:
                        q = tot.setdefault((e, lab), [0, 0.0])
                        q[0] += 1
                        q[1] += w
        except (OSError, ValueError, EOFError):
            pass
for (e, lab), q in sorted(tot.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    print(f"    {lab:22s} {e}: mean board {q[1] / q[0]:.1f} W over {q[0]} samples")
print("    idle: aifoundry1 card 1 about 30 W, aifoundry3 about 23.5 W (K4). Hold die: " + ", ".join(f"{p} {hold[p]:.2f}" for p in FULL))

print("\nC6. aifoundry2's own NIC and NVMe through the hold's last 2 min (self-heated, one contrast)")
H2 = LIVE["aifoundry2"]
rd = {}
for p in FULL:
    v = [r for r in H2 if end_ms[p] - 130000 <= r["t"] < end_ms[p] - 7000]
    rd[p] = (P[p]["rest20"]["nic"], P[p]["rest20"]["nvme"], st.mean(r["temps"]["nic"] for r in v), st.mean(r["temps"]["nvme"] for r in v), P[p]["rest_w"], P[p]["hold"]["w"])
    print(f"  {p}: rest NIC {rd[p][0]:.2f} NVMe {rd[p][1]:.2f}; hold's end NIC {rd[p][2]:.2f} NVMe {rd[p][3]:.2f} (n {len(v)})")
lead = [rd["P1"][j] - st.mean(rd[p][j] for p in LATER) for j in range(4)]
perw = st.median((rd[p][2] - rd[p][0]) / (rd[p][5] - rd[p][4]) for p in FULL)
dhw = P["P1"]["hold"]["fine_w"] - st.mean(P[p]["hold"]["fine_w"] for p in LATER)
print(f"  P1 minus the later probes: NIC {lead[0]:+.2f} at rest, {lead[2]:+.2f} at the hold's end; NVMe {lead[1]:+.2f}, {lead[3]:+.2f}. The NIC's extra {lead[2] - lead[0]:+.2f} C; the NIC rises {perw:.3f} C per card W, so the card's extra {dhw:.2f} W is worth {perw * dhw:.2f} C; left over {lead[2] - lead[0] - perw * dhw:.2f} C of the die's extra {extra:.2f} C")

print("\nC7. The shared fall, on rows clean of aifoundry1's own run")
H1 = [r for r in LIVE["aifoundry1"] if r["t"] >= 1793516400000]
iv, cur, last = [], None, None
for r in H1:
    h = card(r, 0).get("held") or card(r, 1).get("held")
    if h:
        cur = r["t"] if cur is None else cur
        last = r["t"]
    elif cur is not None:
        if last - cur > 30000:
            iv.append((cur, last))
        cur = None
merged = []
for a, b in iv:
    if merged and a - merged[-1][1] < 180000:
        merged[-1] = (merged[-1][0], b)
    else:
        merged.append((a, b))
print("  aifoundry1's held intervals, UTC, gaps under 3 min merged: " + ", ".join(f"{hm(a)}-{hm(b)} ({(b - a) / 60000:.0f} min)" for a, b in merged))
for p in ("P2", "P3"):
    prev = [q for q in merged if q[1] < snap[p] - 300000][-1]
    print(f"  before {p}'s rest window ends at {hm(snap[p])}: its last run {hm(prev[0])}-{hm(prev[1])}, {(prev[1] - prev[0]) / 60000:.0f} min long, ended {(snap[p] - prev[1]) / 60000:.0f} min before")
print(f"  rows with card 0 held tonight: {sum(1 for r in H1 if card(r, 0).get('held'))} of {len(H1)}")


def a1_rows(p, skip_min):
    a, b = snap[p] - 1200000, snap[p]
    out = []
    for r in H1:
        if a <= r["t"] < b:
            c0, c1 = card(r, 0), card(r, 1)
            if c0.get("held") or c1.get("held") or c0.get("die") is None or (r.get("load") or 0) > 2:
                continue
            if any(r["t"] - e < skip_min * 60000 and r["t"] > e for _, e in iv):
                continue
            out.append(r)
    return out


for skip in (0, 15):
    rows = {p: a1_rows(p, skip) for p in ALL5}
    print(f"  skip {skip} min after aifoundry1's own held rows: rows per probe {[(p, len(v)) for p, v in rows.items()]}")
    if skip:
        have = [p for p in ALL5 if len(rows[p]) >= 60]
        for lab, f in (("a1 card 0 die", lambda r: card(r, 0)["die"]), ("a1 card 0 W", lambda r: card(r, 0)["w"]), ("a1 card 1 W", lambda r: card(r, 1)["w"]), ("a1 NIC", lambda r: r["temps"]["nic"])):
            v = {p: st.mean(f(r) for r in rows[p]) for p in have}
            fit = ols([x20[p] for p in have], [v[p] for p in have])
            print(f"    {lab:14s} {[(p, round(v[p], 3)) for p in have]} on the rest die {fit['b']} [{fit['lo']}, {fit['hi']}], n {fit['n']}")
early = [r for r in LIVE["aifoundry1"] if 1793512800000 <= r["t"] < 1793516400000 and not card(r, 0).get("held") and not card(r, 1).get("held") and card(r, 0).get("w") is not None]
print(f"  a1 card 0, 06:00-07:00 UTC, nothing held: {st.mean(card(r, 0)['w'] for r in early):.2f} W, {st.mean(card(r, 0)['die'] for r in early):.1f} C, n {len(early)}")

print("\nC8. Words: what the runs before the hold did, the gate, the trip labels, int8 full")
for p in FULL:
    gates = [run(p, i)["gate"]["held_s"] for i in range(5, 9)] + [P[p]["hold"]["gate"]["held_s"]]
    print(f"  {p}: indexes 5-8 mean W {st.mean(run(p, i)['w'] for i in range(5, 9)):.2f}; gate held {gates} = {sum(gates):.1f} s; limit, indexes 5-8: {[run(p, i)['limit'] for i in range(5, 9)]}")
print("  int8 full clock on the raw rest die: " + ", ".join(f"{n} {st.mean(v[2] for v in S[n][1]['int8/full']):.1f} at {S[n][0]:.2f}" for n in ("E80", "P7", "P3", "P6", "E83", "E96", "P1", "E87", "E64")))

print("\nC9. fp16 ones by index")
for p in FULL:
    print(f"  {p}: index 5 {run(p, 5)['mhz']:.1f} MHz ({run(p, 5)['limit']}), index 8 {run(p, 8)['mhz']:.1f} MHz ({run(p, 8)['limit']})")

print("\nC10. E96, the only other warm session of the night, against P1 on the same two trip kinds")
print(f"  rest die: E96 {S['E96'][0]}, P1 {S['P1'][0]:.2f}. Line: E96 {tl['E96']:.2f} (int8 full {line_of('E96', 'int8/full'):.2f} on {len(S['E96'][1]['int8/full'])} runs, fp32 randn {line_of('E96', 'fp32/randn'):.2f} on {len(S['E96'][1]['fp32/randn'])}); P1 {tl['P1']:.2f}. Difference {tl['P1'] - tl['E96']:.2f} C; one run's rms 0.42 C, so about {0.42 * math.sqrt(1 / 2 + (1 / 4 + 1 / 2) / 4):.2f} C on this difference, {(tl['P1'] - tl['E96']) / (0.42 * math.sqrt(1 / 2 + (1 / 4 + 1 / 2) / 4)):.1f} sigma")

print("\nC11. The discriminator's 1.12 and 2.08 assume one R")


def g(Rv, sl):
    return 1 / (1 - Rv * sl)


for Rr, Rh in ((0.4573, 0.4573), (1.1, 0.65), (1.47, 1.47)):
    room = g(Rh, 0.442) / g(Rr, WPC)
    print(f"  R {Rr} at rest, {Rh} in the hold: room {room:.2f}, path {room * 41 / 22.1:.2f}")

print("\nC12. Leave one probe out, and whether being first is carryover")
line = R["R1"]["per_probe"]
for dr in FULL:
    keep = [p for p in FULL if p != dr]
    print(f"  without {dr}: R1 {ols([x20[p] for p in keep], [line[p] for p in keep])['b']}, R2 {ols([x20[p] for p in keep], [hold[p] for p in keep])['b']}, S4 MHz {ols([x20[p] for p in keep], [mhz[p] for p in keep])['b']}; x range {max(x20[p] for p in keep) - min(x20[p] for p in keep):.2f} C")
iv2, cur, last = [], None, None
for r in H2:
    if r["t"] < 1793491200000:
        continue
    if card(r, 0).get("held"):
        cur = r["t"] if cur is None else cur
        last = r["t"]
    elif cur is not None:
        if last - cur > 30000:
            iv2.append((cur, last))
        cur = None
print("  aifoundry2's held intervals from 31 Oct 17:00 PDT, UTC: " + ", ".join(f"{hm(a)}-{hm(b)}" for a, b in iv2))
print("  P2's lead over P3, P6, P7 on the runs it has, against P1's: " + ", ".join(f"index {i}: {run('P2', i)['line'] - st.mean(run(p, i)['line'] for p in LATER):+.2f}, {run('P1', i)['line'] - st.mean(run(p, i)['line'] for p in LATER):+.2f}" for i in range(0, 3)))

print("\nC13. The open test: a probe at E64's own idle die")
txt = open(os.path.join(DESK, "room-proxies.txt")).read()
hours = {int(a): float(b) for a, b in re.findall(r"^(\d\d): die ([\d.]+)", txt, re.M)}
print(f"  nine-day hour means of the idle die, PDT: {[(h, hours[h]) for h in (11, 16, 17, 18, 19, 20)]}; range to the 11:00 low {max(hours[h] for h in range(16, 21)) - hours[11]:.1f} C, against the night's {R['R0']['range_c']:.2f} C. E64's rest 49.28 C, E64's fp16 ones {m64:.1f} MHz, {w64:.2f} W; 31 Oct's evening only reached 47.15 C (E87)")
