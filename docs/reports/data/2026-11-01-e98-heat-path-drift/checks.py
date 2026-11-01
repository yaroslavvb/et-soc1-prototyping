#!/usr/bin/env python3
"""E98 (Q132): post-hoc checks K1-K7, written after the data. LABELLED: none of this is a registered rule or changes a verdict.

    python3 docs/reports/data/2026-11-01-e98-heat-path-drift/checks.py > docs/reports/data/2026-11-01-e98-heat-path-drift/checks.txt

Reads this directory's results.json and history/, and the committed results of E64, E80, E83, E87, E96. Standard library only.
"""
import glob
import gzip
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
R = json.load(open(os.path.join(HERE, "results.json")))
KLINE, WPC = 0.4573, 0.2315
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365}
P = {p["probe"]: p for p in R["probes"]}
FULL = ["P1", "P3", "P6", "P7"]
LATER = ["P3", "P6", "P7"]


def ols(xs, ys):
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pts)
    mx, my = st.mean(p[0] for p in pts), st.mean(p[1] for p in pts)
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    a = my - b * mx
    res = [y - a - b * x for x, y in pts]
    se = math.sqrt(sum(r * r for r in res) / (n - 2) / sxx) if n > 2 else None
    tq = T975.get(n - 2)
    return {"slope": round(b, 3), "lo": round(b - tq * se, 3) if se is not None else None, "hi": round(b + tq * se, 3) if se is not None else None,
            "se": round(se, 3) if se is not None else None, "n": n, "rms": round(math.sqrt(sum(r * r for r in res) / n), 3), "sxx": round(sxx, 4), "icpt": round(a, 3)}


def run(p, i):
    return P[p]["runs"].get(str(i)) or P[p]["runs"].get(i) or {}


def contrast(name, f, unit="C"):
    a, b = f("P1"), st.mean(f(p) for p in LATER)
    sd = st.stdev(f(p) for p in LATER)
    print(f"  {name:38s} P1 {a:8.3f}  later {' '.join(f'{f(p):8.3f}' for p in LATER)}  mean {b:8.3f}  P1 - later {a - b:+7.3f} {unit}  sd of the three {sd:.3f}")
    return a - b


print("K1. Every registered slope with four probes is one contrast: P1 against P3, P6, P7")
x = {p: P[p]["rest_die_w_derived"] for p in P}
sxx = sum((x[p] - st.mean(x[q] for q in FULL)) ** 2 for p in FULL for _ in [0])
for p in FULL:
    print(f"  leverage of {p} in R1 and R2: {1 / 4 + (x[p] - st.mean(x[q] for q in FULL)) ** 2 / sxx:.3f}  (x {x[p]:.3f})")
dx = contrast("rest die, W-derived", lambda p: x[p])
dw = contrast("rest W, 20 min of history", lambda p: P[p]["rest_w"], "W")
dr = contrast("rest die, raw history", lambda p: P[p]["rest20"]["die"])
contrast("rest W, the 60 s reading", lambda p: P[p]["rest60"]["w"], "W")
dl = contrast("the line (R1)", lambda p: R["R1"]["per_probe"][p])
dh = contrast("hold die (R2)", lambda p: P[p]["hold"]["die"])
dhi = contrast("hold ioshire", lambda p: P[p]["hold"]["io"])
dhw = contrast("hold fine W (S2)", lambda p: P[p]["hold"]["fine_w"], "W")
dm = contrast("fp16 ones MHz (S4)", lambda p: R["S4"]["per_probe"][p]["mhz"], "MHz")
dtw = contrast("fp16 ones W (S4)", lambda p: R["S4"]["per_probe"][p]["w"], "W")
print(f"  ratios to the rest die's {dx:+.3f} C: line {dl / dx:.2f}, hold die {dh / dx:.2f}, hold ioshire {dhi / dx:.2f}; hold fine W per rest W {dhw / dw:.2f}; trip {dm / dx:.1f} MHz/C, {dtw / dx:.2f} W/C")
print(f"  on the raw history die ({dr:+.3f} C): line {dl / dr:.2f}, hold die {dh / dr:.2f}")
print(f"  hold die minus rest die (raw history): " + ", ".join(f"{p} {P[p]['hold']['die'] - P[p]['rest20']['die']:.2f}" for p in FULL))
cal = [P[p]["hold"]["calibration"]["w_per_c"] for p in FULL]
print(f"  W per C inside each hold, by die step, after its first 60 s: {cal}, median {st.median(cal):.3f} (E64's 0.442); hold die from fine W: {dhw / 0.442:+.2f} C at 0.442")

print("\nK2. How wide R1's interval really is. It has 2 df and P1's leverage leaves little to estimate from")
f1 = R["R1"]["fit"]
s_res = math.sqrt(sum((R["R1"]["per_probe"][p] - (f1["icpt"] + f1["slope"] * x[p])) ** 2 for p in FULL) / 2)
pos = R["arms"]["R1_by_position"]
sq = [v["rms"] ** 2 for v in pos.values()]
s_kind = math.sqrt(st.mean(sq) / len(sq))
print(f"  residual scatter of a probe in the frozen fit: {s_res:.3f} C; from the eight positions' own scatter, as if independent: {s_kind:.3f} C; planning noise: 0.15 C")
for name, s in (("the fit's own", s_res), ("the positions' scatter", s_kind), ("planning noise", 0.15)):
    hw = T975[2] * s / math.sqrt(sxx)
    print(f"  slope {f1['slope']:.3f}, half-width on {name:24s} {hw:.3f}: [{f1['slope'] - hw:.3f}, {f1['slope'] + hw:.3f}]; holds 0.25: {f1['slope'] - hw <= 0.25 <= f1['slope'] + hw}; holds 0: {f1['slope'] - hw <= 0 <= f1['slope'] + hw}")
f2 = R["R2"]["fit"]
s2 = st.stdev(P[p]["hold"]["die"] for p in LATER)
print(f"  R2: the hold's scatter among P3, P6, P7 is {s2:.3f} C (planning 0.40 C). slope {f2['slope']:.2f} [{f2['lo']:.2f}, {f2['hi']:.2f}]: holds the room's 1.12: {f2['lo'] <= 1.12 <= f2['hi']}; holds the path's 2.08: {f2['lo'] <= 2.08 <= f2['hi']}; holds 1:1: {f2['lo'] <= 1.0 <= f2['hi']}")

print("\nK3. Held and unheld runs: A2's expectation against the night, on the two rest readings")
x60 = {p: P[p]["rest60"]["w"] / WPC for p in P}
HELD, UNHELD = [5, 6, 7, 8], [1, 2, 3, 4]


def group(ids, field="line", probes=FULL):
    kinds = {}
    for p in probes:
        v = {}
        for i in ids:
            r = run(p, i)
            if r.get(field) is not None:
                v.setdefault(r["kind"], []).append(r[field])
        kinds[p] = {k: st.mean(q) for k, q in v.items()}
    allk = sorted({k for v in kinds.values() for k in v})
    centre = {k: st.mean(kinds[p][k] for p in probes if k in kinds[p]) for k in allk}
    return {p: st.mean(kinds[p][k] - centre[k] for k in kinds[p]) for p in probes if kinds[p]}


for name, ids, target in (("unheld, indexes 1-4", UNHELD, 0.89), ("held, indexes 5-8", HELD, 0.25)):
    g = group(ids)
    print(f"  {name}: A2 expected {target}; on the 20 min rest {ols([x[p] for p in FULL], [g[p] for p in FULL])}")
    print(f"     on the 60 s rest {ols([x60[p] for p in FULL], [g[p] for p in FULL])}")
print(f"  gate held, s, by index: " + "; ".join(f"{p}: " + " ".join(str(run(p, i).get('gate', {}).get('held_s')) for i in range(9)) for p in FULL))
print(f"  limit by index: " + "; ".join(f"{p}: " + " ".join(str(run(p, i).get('limit'))[0] for i in range(9)) for p in FULL))
print("  P2 kept what it ran (indexes 0-3). Not in R1 under the frozen rule, shown here. Indexes 1-3 on five probes:")
g5 = group([1, 2, 3], probes=["P1", "P2", "P3", "P6", "P7"])
gf = group([1, 2, 3], field="fine_w", probes=["P1", "P2", "P3", "P6", "P7"])
n5 = ["P1", "P2", "P3", "P6", "P7"]
print(f"     line on the 20 min rest {ols([x[p] for p in n5], [g5[p] for p in n5])}")
print(f"     line on the 60 s rest   {ols([x60[p] for p in n5], [g5[p] for p in n5])}")
print(f"     fine W on the 20 min rest W {ols([P[p]['rest_w'] for p in n5], [gf[p] for p in n5])}")
print(f"     fine W on the 60 s rest W   {ols([P[p]['rest60']['w'] for p in n5], [gf[p] for p in n5])}")
fr = {p: run(p, 0) for p in n5}
print(f"  the from-rest run, five probes: line on the 60 s rest {ols([x60[p] for p in n5], [fr[p]['line'] for p in n5])}; fine W on the 60 s rest W {ols([P[p]['rest60']['w'] for p in n5], [fr[p]['fine_w'] for p in n5])}")

print("\nK4. The night's readings across the boxes, 30 min bins, idle rows only, by the desk lane's filter (PST clock = UTC - 8)")
H = {}
for b in ("aifoundry1", "aifoundry2", "aifoundry3"):
    rows = []
    for f in glob.glob(os.path.join(HERE, "history", f"{b}-*.jsonl.gz")):
        rows += [json.loads(ln) for ln in gzip.open(f, "rt")]
    H[b] = sorted(rows, key=lambda r: r["t"])
BARS = {("aifoundry1", 0): 22.0, ("aifoundry1", 1): 34.0, ("aifoundry2", 0): 26.0, ("aifoundry3", 0): 27.0}


def idle(box, r, n):
    cs = {c["n"]: c for c in r.get("cards") or []}
    c = cs.get(n)
    if not c or c.get("die") is None or c.get("w") is None or (r.get("load") or 0) > 2 or c["w"] > BARS[(box, n)]:
        return None
    if any(x.get("held") for x in cs.values()):
        return None
    return c


def means(box, n, a, b):
    d, w, nic, nv = [], [], [], []
    for r in H[box]:
        if a <= r["t"] < b:
            c = idle(box, r, n)
            if c:
                d.append(c["die"]); w.append(c["w"])
                nic.append(r["temps"].get("nic")); nv.append(r["temps"].get("nvme"))
    return (st.mean(w), st.mean(d), st.mean(nic), st.mean(nv), len(w)) if len(w) >= 24 else None


t0 = 1793516400000
print("  UTC    | a2 W     die   nic   nvme  n  | a1c0 W   die   a1 nic nvme  n  | a1c1 W   die")
for k in range(0, 17):
    a, b = t0 + k * 1800000, t0 + (k + 1) * 1800000
    q = means("aifoundry2", 0, a, b)
    q1 = means("aifoundry1", 0, a, b)
    q2 = means("aifoundry1", 1, a, b)
    fmt = lambda v: " ".join(f"{u:6.2f}" for u in v[:4]) + f" {v[4]:4d}" if v else "   -      -      -      -      -"   # noqa: E731
    h = (a // 1000 % 86400) // 3600
    m = (a // 1000 % 3600) // 60
    print(f"  {h:02d}:{m:02d}  | {fmt(q)} | {fmt(q1)} | {(f'{q2[0]:6.2f} {q2[1]:6.2f}') if q2 else '   -      -'}")

print("\nK5. Was the room moving during a probe? aifoundry1's idle readings, not heated by this card, over each probe's rest window, its work, and the hold's last 2 min")
spans = {}
for p in P:
    rs = [v for v in P[p]["runs"].values()]
    spans[p] = {"rest_end": P[p]["t_rest_ms"], "end": P[p]["queue"][-1]["t_ms"] if P[p]["queue"] else None, "hold_end": None}
for p in FULL:
    q = [x for x in P[p]["queue"] if x.get("kind") == "end"][0]
    end = q["t_ms"]
    t = P[p]["t_rest_ms"]
    for tag, a, b in (("rest window", t - 1200000, t), ("the work", t + 120000, end), ("last 2.5 min", end - 150000, end)):
        v0, v1 = means("aifoundry1", 0, a, b), means("aifoundry1", 1, a, b)
        print(f"  {p} {tag:13s} a1c0 W {v0[0] if v0 else float('nan'):6.3f} die {v0[1] if v0 else float('nan'):6.2f} a1 nic {v0[2] if v0 else float('nan'):6.2f} nvme {v0[3] if v0 else float('nan'):6.2f} n {v0[4] if v0 else 0:4d} | a1c1 W {v1[0] if v1 else float('nan'):6.3f}")

print("\nK6. The same reading across sessions: the kinds the sessions share, against the rest (desk lane's table; E96 from its own README section 5; E98 from this file)")
SESS = [("E64", "2026-10-23-e64-horace-power-limit/results.json", 22.693, 49.28), ("E80", "2026-10-31-e80-kinds-speed/results.json", 21.762, 45.58),
        ("E83", "2026-10-31-e83-kinds-speed-rest/results.json", 22.025, 46.42), ("E87", "2026-10-31-e87-real-tensors-speed/results.json", 22.174, 47.15),
        ("E96", "2026-11-01-e96-real-tensors-speed/results.json", 22.145, 46.79)]


def norm(r):
    t, v = r.get("type"), str(r.get("values"))
    v = v.split("/")[-1].replace(".bin", "")
    if t == "int8" and v == "randn":
        v = "full"
    return f"{t}/{v}"


rows = []
for name, f, w, d in SESS:
    Q = json.load(open(os.path.join(DATA, f)))
    k = {}
    for r in Q["runs"]:
        if str(r.get("block", "")).startswith("SUS") and r.get("sus_w_mean") is not None:
            k.setdefault(norm(r), []).append((r["sus_w_mean"], r["sus_die_mean"], r.get("sus_mhz_mean")))
    rows.append((name, w, d, k))
for p in FULL:
    k = {}
    for i in HELD:
        r = run(p, i)
        k.setdefault(r["kind"], []).append((r["w"], r["die"], r["mhz"]))
    rows.append((p, P[p]["rest_w"], P[p]["rest20"]["die"], k))


def line_of(v):
    return st.mean(d - KLINE * w for w, d, _ in v)


print("  session  rest W  raw rest die | int8 full line  fp32 randn line  mean | fp16 ones W, MHz, line")
xs, ys, xm, ym, yw = [], [], [], [], []
for name, w, d, k in rows:
    a, b = k.get("int8/full"), k.get("fp32/randn")
    fo = k.get("fp16/ones")
    la, lb = (line_of(a) if a else None), (line_of(b) if b else None)
    m = st.mean([la, lb]) if a and b else None
    if m is not None:
        xs.append(d); ys.append(m)
    ft = ""
    if fo:
        fw, fm = st.mean(x[0] for x in fo), st.mean(x[2] for x in fo)
        ft = f"{fw:6.2f} {fm:6.1f} {line_of(fo):6.2f}"
        xm.append(d); ym.append(fm); yw.append(fw)
    print(f"  {name:5s}  {w:6.3f}  {d:6.2f}       | {la if la is None else round(la, 2)}  {lb if lb is None else round(lb, 2)}  {m if m is None else round(m, 2)} | {ft}")
print(f"  the mean line on the raw rest die, all sessions: {ols(xs, ys)}")
print(f"  the same without E64: {ols(xs[1:], ys[1:])}")
print(f"  the same, earlier sessions only (E64, E80, E83, E87, E96): {ols(xs[:5], ys[:5])}")
print(f"  fp16 ones' clock on the raw rest die (E64, E80, P1, P3, P6, P7): {ols(xm, ym)}")
print(f"  fp16 ones' W on the raw rest die: {ols(xm, yw)}")
SESS_ROWS = list(rows)

print("\nK7. Idle-reset dips and other flags, per probe (kept in the registered numbers)")
for p in P:
    runs = list(P[p]["runs"].values())
    print(f"  {p}: dips in the 40 s windows {sum(len(r['dips']) for r in runs)} of {len(runs)} runs; hold window {len((P[p].get('hold') or {}).get('dips') or [])}; dips anywhere in the work {sum(r.get('dips_in_work', 0) for r in runs) + (P[p].get('hold') or {}).get('dips_in_work', 0)}; rest_ok {P[p]['rest_ok']}; since busy {P[p]['rest20']['since_busy_min']} min, rows {P[p]['rest20']['rows']}")
print(f"  R1 with dips left out: {R['arms']['R1_dips_left_out']}")
print(f"  binaries the same in every probe: {R['binaries_same_in_every_probe']}")

print("\nK8. P1 minus the later probes by position (the line, then board W and die), and the rest of the night's shape")
for i in range(9):
    a = run("P1", i)
    b = [run(p, i) for p in LATER]
    print(f"  index {i} {a['kind']:14s} line {a['line'] - st.mean(r['line'] for r in b):+.2f}  W {a['w'] - st.mean(r['w'] for r in b):+.2f}  die {a['die'] - st.mean(r['die'] for r in b):+.2f}  MHz {a['mhz'] - st.mean(r['mhz'] for r in b):+.1f}")
print(f"  hold, int8 neg_ones     line {P['P1']['hold']['line'] - st.mean(P[p]['hold']['line'] for p in LATER):+.2f}  W {P['P1']['hold']['w'] - st.mean(P[p]['hold']['w'] for p in LATER):+.2f}  die {dh:+.2f}  MHz {P['P1']['hold']['mhz'] - st.mean(P[p]['hold']['mhz'] for p in LATER):+.1f}")
E = json.load(open(os.path.join(os.path.dirname(HERE), "..", "..", "..", "tools", "claims-v3", "kspeed", "e98", "predictions.json")))["expected_rest"]
print("  rest W, expected at the freeze against measured: " + ", ".join(f"{p} {E[p]['rest_w']} / {P[p]['rest_w']:.3f}" for p in P))

print("\nK9. The hold by minute: die and fine W, reset samples left out (is 5.5 min near steady?)")
for p in FULL:
    rows = []
    op = gzip.open(os.path.join(HERE, p, "tel", "HOLD-00-int8-neg_ones-hold-r1.jsonl.gz"), "rt")
    for ln in op:
        if ln.startswith("{"):
            d = json.loads(ln)
            rows.append((d["t_ms"], d["temp_c"]["minshire"][0], d["board_w"], d["mhz"]["minion"]))
    t0 = None
    for ln in gzip.open(os.path.join(HERE, p, "launches.jsonl.gz"), "rt"):
        L = json.loads(ln)
        if L["run"].startswith("HOLD") and L.get("role") == "work":
            t0 = L["t_start_ms"] if t0 is None else min(t0, L["t_start_ms"])
    out = []
    for m in range(6):
        v = [r for r in rows if t0 + m * 60000 <= r[0] < t0 + (m + 1) * 60000 and r[3] == 800]
        if v:
            out.append(f"{m}: {st.mean(r[1] for r in v):.2f} C {st.mean(r[2] for r in v):.2f} W")
    print(f"  {p}  " + "; ".join(out))

print("\nK10. Nothing was set: every config read of the night")
n, bad = 0, 0
for p in P:
    for c in P[p]["config_reads"]:
        n += 1
        bad += 0 if c == [65, 65] else 1
    for tag in ("start", "end"):
        c = json.load(open(os.path.join(HERE, p, f"snapshot-{tag}.json"))).get("config") or {}
        n += 1
        bad += 0 if (c.get("tdp_w"), c.get("temp_threshold_c")) == (65, 65) else 1
print(f"  {n} reads across the probes' runs and both ends of each probe; {bad} not 65 W / 65 C")

print("\nK11. What else ran in the room: the share of each box's rows with a card held, over each probe's rest window and its work")


def held_share(box, a, b):
    rows = [r for r in H[box] if a <= r["t"] < b]
    return sum(1 for r in rows if any(c.get("held") for c in r.get("cards") or [])) / len(rows) if rows else float("nan")


for p in FULL:
    q = [x for x in P[p]["queue"] if x.get("kind") == "end"][0]
    t, end = P[p]["t_rest_ms"], q["t_ms"]
    print(f"  {p}: rest window aifoundry1 {held_share('aifoundry1', t - 1200000, t):.2f}, aifoundry3 {held_share('aifoundry3', t - 1200000, t):.2f}; the work aifoundry1 {held_share('aifoundry1', t, end):.2f}, aifoundry3 {held_share('aifoundry3', t, end):.2f}; the hold's last 2.5 min aifoundry1 {held_share('aifoundry1', end - 150000, end):.2f}, aifoundry3 {held_share('aifoundry3', end - 150000, end):.2f}; hold die {P[p]['hold']['die']:.2f}")

print("\nK12. Int8 full, the kind that lands on either side of the trip: its sustained clock and limit against the rest, every session")
xi, yi = [], []
for name, w, d, k in SESS_ROWS:
    v = k.get("int8/full")
    if v:
        m = st.mean(x[2] for x in v)
        xi.append(d); yi.append(m)
        print(f"  {name:5s} raw rest die {d:6.2f}  rest W {w:6.3f}  clock {m:6.1f} MHz, {len(v)} run(s), each {[round(x[2], 1) for x in v]}")
print(f"  clock on the raw rest die, all: {ols(xi, yi)}")
print(f"  the same without E64: {ols(xi[1:], yi[1:])}")
print(f"  the night alone (P1, P3, P6, P7): {ols(xi[-4:], yi[-4:])}")

print("\nK13. The proxies against the rest die: the nine-day relation (desk lane's room-proxies.txt: W of aifoundry2's idle per unit of the reading, so 0.2315 / that = the reading's C per C of rest die) and the night")
DESK = {"a1c0-die": 0.2607, "a1c1-die": 0.2100, "a1c1-w": 0.4858, "a1c0-w": 1.0332, "a1-nic": 0.2505, "a1-nvme": 0.2551, "a2-nic": 0.2560, "a2-nvme": 0.2727}
for k, u in DESK.items():
    f = R["proxies"][k]["it_on_rest_die"]
    print(f"  {k:9s} nine days {WPC / u:5.2f}; the night {f['slope']:5.2f} [{f['lo']:5.2f}, {f['hi']:5.2f}], n {f['n']}; values {R['proxies'][k]['values']}")
print("  a3: " + json.dumps(R["proxies"].get("a3-nic")))
