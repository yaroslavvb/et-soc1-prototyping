#!/usr/bin/env python3
"""E100: the desk check behind "Corrections after verification". Every number those corrections quote, from committed files, with the frozen scorer's own definitions.
No card, no new data; no frozen file, data file or registered verdict changes. Section numbers are the corrections' own.

    python3 corrections-check.py > corrections-check.txt          (from this directory; Python 3, no third-party modules; about a minute)
"""
import bisect
import collections
import datetime as DT
import glob
import gzip
import json
import math
import os
import random
import statistics as st
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e100"))
import reduce_e100 as R  # noqa: E402

RES = json.load(open(os.path.join(HERE, "results.json")))
PH = json.load(open(os.path.join(HERE, "posthoc.json")))
runs = R.load(os.path.join(HERE, "s1"))
r1 = [r for r in runs if r["round"] == 1]
r2 = [r for r in runs if r["round"] == 2]
R1, R2 = R.Round(r1), R.Round(r2)
RA = R.Round(runs)
L1 = RES["rules"]["D3"]["lattice_round1"]
L2 = RES["rules"]["D3"]["lattice_round2"]
pa, qa = R.fit_lattice(R1)
pb, qb = R.fit_lattice(R2)
TEST = {3, 4}  # A20, A100, the registered test arms
print("E100 corrections-check. Inputs: s1/, results.json, posthoc.json, tools/claims-v3/e100/reduce_e100.py (frozen), the desk reading's ir-tests.json.")
print(f"the frozen scorer's fits reproduce results.json: round 1 p {pa} q {qa:.4f} (results {L1}), round 2 p {pb} q {qb:.4f} (results {L2})")

print("\n======== C1. 'Nothing to do with the numbers': E100 ran one kind")
IT = json.load(open(os.path.join(HERE, "..", "2026-11-01-q132-governor-desk", "ir-tests.json")))
print("E100's load in every arm: int8 zeros. The kinds come from the desk reading's 25 falls, post hoc: format p", IT["tests"]["format"]["p"], IT["tests"]["format"]["rows"], "; power p", IT["tests"]["power"]["p"], "; die p", IT["tests"]["die"]["p"])

print("\n======== C2. Every fall against the other round's lattice")
falls = []
for r in runs:
    for pr, pv in zip(r["procs"], R.process_view(r)):
        for f in pv["falls"]:
            falls.append(dict(run=r["run"], arm=r["arm"], round=r["round"], t600=f["t600"], at600=f["at600_s"], since=f["since_reset_ms"], kernels=pr["kernels"]))
print(f"falls {len(falls)}: {dict(collections.Counter(f['arm'] for f in falls))}")
rows = []
NAME = {1: "kernel", 2: "gap", 3: "edge"}
for f in falls:
    p, q, oth = (pb, qb, R1) if f["round"] == 1 else (pa, qa, R2)
    k = math.floor((f["t600"] - p) / q)
    pt = p + q * k
    lag = f["t600"] - pt
    if lag > 500:
        lag -= q
        pt += q
    i = int(pt - oth.t0)
    rows.append(dict(arm=f["arm"], run=f["run"], lag=round(lag, 1), scope=oth.scope[i] if 0 <= i < len(oth.scope) else None, exposed=oth.exposed[i] if 0 <= i < len(oth.exposed) else None, fell=oth.fell[i] if 0 <= i < len(oth.fell) else None, pt=pt, t600=f["t600"], since=f["since"], kernels=f["kernels"]))
lags = [x["lag"] for x in rows]
print(f"first 600 reading minus the other round's nearest lattice point: min {min(lags)} ms, median {st.median(lags)} ms, max {max(lags)} ms, over all {len(lags)} falls; more than 250 ms away: {sum(1 for v in lags if abs(v) > 250)}")
print("scope of that lattice point, by arm:", sorted(((a, NAME.get(s, str(s))), n) for (a, s), n in collections.Counter((x["arm"], x["scope"]) for x in rows).items()))
n_gap = sum(1 for x in rows if x["scope"] == 2 and x["exposed"] and x["fell"])
n_ker = sum(1 for x in rows if x["scope"] == 1 and x["exposed"] and x["fell"])
print(f"scored as the frozen table scores them: {n_gap} in a gap, {n_ker} inside a kernel, {len(rows) - n_gap - n_ker} left out (a point within 1 ms of a kernel's edge)")
for arm in ("A20", "A100"):
    v = [x for x in rows if x["arm"] == arm]
    t = sum(1 for x in v if x["scope"] == 2 and x["exposed"] and x["fell"])
    print(f"  {arm}: {len(v)} falls, {t} in the registered table, {len(v) - t} left out")
print("D3's table holds", RES["rules"]["D3"]["table_tp_fn_fp_tn"], "over A20 and A100, whose falls number", sum(1 for x in rows if x["arm"] in ("A20", "A100")))


def gap_table(arms):
    """Gap-centred: every gap of 3 ms or more between kernels with the clock above 600 MHz before it, against the other round's lattice and a 600 MHz reading up to 250 ms into the next kernel."""
    out = collections.Counter()
    lat = {1: (pb, qb), 2: (pa, qa)}
    for r in runs:
        if r["arm"] not in arms:
            continue
        p, q = lat[r["round"]]
        T = [x for x in r["tel"] if x[3] is not None]
        ts = [x[0] for x in T]
        for pr in r["procs"]:
            ks = pr["kernels"]
            for j in range(1, len(ks)):
                e, s = ks[j - 1]["t_end_ms"], ks[j]["t_start_ms"]
                if s - e < 3:
                    continue
                i = bisect.bisect_right(ts, e - 20) - 1
                if i < 0 or T[i][3] <= 600:
                    continue
                has = (p + q * math.ceil((e + 1 - p) / q)) <= s - 1
                fell = False
                for x in T[bisect.bisect_right(ts, e):]:
                    if x[0] > s + 250:
                        break
                    if x[3] == 600:
                        fell = True
                        break
                out[(has, fell)] += 1
                if fell and not has:
                    nx = p + q * math.ceil((e + 1 - p) / q)
                    off.append((r["arm"], s - e, round(min(abs(nx - s), abs(e - (nx - q)), abs(nx - e), abs(s - (nx - q))), 1)))
    return out


off = []
for arm in ("A100", "A20", "R", "A5"):
    o = gap_table({arm})
    print(f"  gap-centred, {arm}: point in gap, fell {o[(True, True)]}, stayed {o[(True, False)]}; no point, stayed {o[(False, False)]}, fell {o[(False, True)]}")
print("  the no-point falls, (arm, gap in ms, nearest lattice point's distance from the gap's edge in ms):", off)
print("what scores a lattice: moving each by a phase, cross-round table on A20 and A100, pooled (gap fell, gap no fall, kernel fell, kernel no fall):")
for dp in (-10, -5, -1, 0, 1, 5, 10, 500):
    a, b = R2.score(pa + dp, qa, TEST), R1.score(pb + dp, qb, TEST)
    print(f"  {dp:+4d} ms: {tuple(a[i] + b[i] for i in range(4))}")
rng = random.Random(5)
sens, spec = [], []
for _ in range(400):
    dp = rng.uniform(0, 1000)
    a, b = R2.score(pa + dp, qa, TEST), R1.score(pb + dp, qb, TEST)
    tp, fn, fp, tn = [a[i] + b[i] for i in range(4)]
    sens.append(tp / (tp + fn) if tp + fn else 0)
    spec.append(tn / (tn + fp) if tn + fp else 0)
print(f"random phases, 400 draws: sensitivity >= 0.9 in {100 * sum(1 for s in sens if s >= 0.9) / len(sens):.2f}%, specificity >= 0.95 in {100 * sum(1 for s in spec if s >= 0.95) / len(spec):.0f}%: specificity is cheap, the sensitivity carries it")

print("\n======== C4. The statistics reset: what carries 'no rise seen'")


def fisher(a, b, c, d):
    n = a + b + c + d
    p0 = math.comb(a + b, a) * math.comb(c + d, c) / math.comb(n, a + c)
    s = 0.0
    for x in range(0, a + c + 1):
        y = a + c - x
        if x <= a + b and y <= c + d:
            pp = math.comb(a + b, x) * math.comb(c + d, y) / math.comb(n, a + c)
            if pp <= p0 * (1 + 1e-9):
                s += pp
    return s


def pois_ci(k):
    def cdf(kk, m):
        s, t = 0.0, math.exp(-m)
        for i in range(kk + 1):
            s += t
            t *= m / (i + 1)
        return s
    lo = 0.0
    if k > 0:
        a, b = 0.0, k + 1.0
        for _ in range(60):
            m = (a + b) / 2
            if 1 - cdf(k - 1, m) < 0.025:
                a = m
            else:
                b = m
        lo = a
    a, b = float(k), k + 50.0
    for _ in range(60):
        m = (a + b) / 2
        if cdf(k, m) > 0.025:
            a = m
        else:
            b = m
    return lo, a


print(f"R 12 falls in 146.7 heartbeats against A20 10 in 146.6: two-sided Fisher p {fisher(12, 135, 10, 137):.2f}; R's 95% count {pois_ci(12)[0]:.1f}-{pois_ci(12)[1]:.1f}. So D5 passes and could not see a rise of less than about a factor of 2")
vr = sorted((x for x in rows if x["arm"] == "R"), key=lambda x: x["lag"])
print(f"R's falls against the other round's lattice: {dict(collections.Counter(NAME.get(x['scope']) for x in vr))}")
print("  (first 600 reading after the lattice point in ms, since_reset_ms at that reading):", [(x["lag"], x["since"]) for x in vr])
print("  the reset's phase against the lattice wanders: since_reset_ms takes", sorted(set(x["since"] for x in vr)))
print("  the late ones:")
for x in vr:
    if x["lag"] >= 100:
        k = next(q for q in x["kernels"] if q["t_start_ms"] <= x["t600"] <= q["t_end_ms"])
        print(f"   {x['run']} kernel {k.get('launch')}: clock {R.g_eff(k):.3f} GHz; lattice point {k['t_start_ms'] - x['pt']:.1f} ms before the kernel's start stamp, scope {NAME.get(x['scope'])}; the fall first read {x['lag']} ms after the point; since_reset_ms {x['since']}")
print("  n = 2, post hoc.")

print("\n======== C5. A0's one 'kernel and fell'")
wh = PH["whole_session_lattice"]
for x in rows:
    if x["arm"] == "A0" and x["scope"] == 1:
        k = next(q for q in x["kernels"] if q["t_start_ms"] <= x["t600"] <= q["t_end_ms"])
        ptw = wh["p_ms"] + wh["q_ms"] * round((k["t_start_ms"] - wh["p_ms"]) / wh["q_ms"])
        print(f"  {x['run']} kernel {k.get('launch')}: on the other round's lattice (period {qb:.3f}) the point is {x['pt'] - k['t_start_ms']:.1f} ms inside the kernel; on the whole-session lattice {ptw - k['t_start_ms']:.1f} ms inside")

print("\n======== C6. The two periods are tie-breaks")
qs = [1000.010 + d * 0.001 for d in range(-7, 8)]
for name, rnd, oth in (("round 1", R1, R2), ("round 2", R2, R1)):
    best, ties = None, []
    for q in qs:
        for pp in range(0, 1000, 2):
            p = rnd.t0 + pp
            tp, fn, fp, tn = rnd.score(p, q)
            sc = tp - 3 * fp - fn
            if best is None or sc > best:
                best, ties = sc, [(p, q)]
            elif sc == best:
                ties.append((p, q))
    tq = sorted({round(q, 3) for _, q in ties})
    tb = collections.Counter(oth.score(p, q, TEST) for p, q in ties)
    print(f"{name}: objective {best}, {len(ties)} ties at a 2 ms phase step, over periods {tq[0]}-{tq[-1]}; out-of-sample tables over the ties, (tp, fn, fp, tn), all of them: {tb.most_common()}")
    print(f"   over those ties: tp {min(t[0] for t in tb)}-{max(t[0] for t in tb)}, fn {min(t[1] for t in tb)}-{max(t[1] for t in tb)}, fp {min(t[2] for t in tb)}-{max(t[2] for t in tb)}, tn {min(t[3] for t in tb)}-{max(t[3] for t in tb)}; lowest specificity {min(t[3] / (t[3] + t[2]) for t in tb):.3f}; sensitivity {min(t[0] / (t[0] + t[1]) for t in tb):.3f} at its lowest; registered bars 0.90, 0.95")


def fit_clipped(rnd, qlo=1000.004, qhi=1000.016):
    """The frozen fit_lattice's scan, with its refinement held inside the registered text's period range."""
    best = None
    for dq in range(-6, 7):
        q = 1000.010 + dq * 0.001
        for pp in range(0, 1000, 4):
            p = rnd.t0 + pp
            tp, fn, fp, tn = rnd.score(p, q)
            sc = tp - 3 * fp - fn
            if best is None or sc > best[0]:
                best = (sc, p, q)
    _, p0, q0b = best
    for dq in range(-2, 3):
        q = q0b + dq * 0.0005
        if not qlo <= q <= qhi:
            continue
        for pp in range(-8, 9):
            p = p0 + pp
            tp, fn, fp, tn = rnd.score(p, q)
            sc = tp - 3 * fp - fn
            if sc > best[0]:
                best = (sc, p, q)
    return best[1], best[2]


pc, qc = fit_clipped(R1)
pd_, qd = fit_clipped(R2)
ta, tb2 = R2.score(pc, qc, TEST), R1.score(pd_, qd, TEST)
print(f"the registered text says within 0.006 ms of 1000.010; the scorer's refinement reaches 0.007 (its 1000.003). With the refinement held to 1000.004-1000.016: round 1 q {qc:.4f} {ta}, round 2 q {qd:.4f} {tb2}, pooled {tuple(ta[i] + tb2[i] for i in range(4))}")
print("the whole session, every period at a 1 ms phase step (a wider range, in sample): (period, objective, table)")
bestw = {}
for q in [1000.004 + i * 0.001 for i in range(9)]:
    b = None
    for pp in range(0, 1000):
        t = RA.score(RA.t0 + pp, q)
        sc = t[0] - 3 * t[2] - t[1]
        if b is None or sc > b[0]:
            b = (sc, t)
    bestw[round(q, 3)] = b
    print(f"  {q:.3f}: {b[0]} {b[1]}")
top = max(v[0] for v in bestw.values())
print("  best at", [q for q, v in bestw.items() if v[0] == top], "; the fits of 31 October: 1000.0098-1000.0105 ms (the desk reading's ir-lattice.txt). posthoc.json:", PH["whole_session_lattice"])

print("\n======== C7. N's process gaps, and what N alone can say")
ng = nf = 0
for r in runs:
    if r["arm"] != "N":
        continue
    T = [x for x in r["tel"] if x[3] is not None]
    P = sorted(r["procs"], key=lambda x: x["t0"])
    for a, b in zip(P, P[1:]):
        S = [x for x in T if a["t1"] - 200 <= x[0] <= b["t0"] + 300]
        ng += 1
        if any(S[i][3] == 600 and S[i - 1][3] > 600 for i in range(1, len(S))):
            nf += 1
print(f"N: {ng} gaps between processes, {nf} with a fall")
W = [k["wall_s"] for r in runs if r["arm"] == "N" for pr in r["procs"] for k in pr["kernels"]]
print(f"N: kernels {len(W)}, wall {min(W):.3f} to {max(W):.3f} s")
print(f"N 0 in 126.1 against A0 3 in 146.3: two-sided Fisher p {fisher(0, 126, 3, 143):.2f}; N's upper limit per heartbeat: one-sided 95% {2.996 / 126.1 * 100:.1f}%, two-sided 95% {3.689 / 126.1 * 100:.1f}%, against A0's {3 / 146.3 * 100:.2f}%. So N alone does not separate a long kernel from A0; the lattice table does (0 of 234 points inside a kernel)")
allb = at800 = 0
for r in runs:
    if r["arm"] != "A0":
        continue
    for pr in r["procs"]:
        ks = pr["kernels"]
        for j in range(1, len(ks)):
            if ks[j - 1].get("launch", -1) >= 0:
                allb += 1
                if (R.g_eff(ks[j - 1]) or 0) >= 0.79:
                    at800 += 1
lo, hi = pois_ci(3)
print(f"A0's boundaries: {allb} in all, {at800} with the kernel before at 800 MHz (the desk reading's denominator). 3 falls: 1 in {allb / 3:.0f} and 1 in {at800 / 3:.0f}; a Poisson 95% on 3 is {lo:.2f}-{hi:.2f}, so at 800 MHz about 1 in {at800 / hi:.0f} to 1 in {at800 / lo:.0f} (over all boundaries about 1 in {allb / hi:.0f} to 1 in {allb / lo:.0f})")

print("\n======== C8. The order of things")
claim = 1566355908076765257
t = (claim >> 22) + 1420070400000
z = DT.timezone(DT.timedelta(hours=-7))
print("the night's shared claim, from its snowflake:", DT.datetime.fromtimestamp(t / 1000, z).strftime("%H:%M:%S.%f")[:-3], "PDT")


def git(*a):
    try:
        return subprocess.run(["git", *a], capture_output=True, text=True, cwd=REPO, timeout=20).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"git not available: {e}"


print("E100's pre-registration 5e12c4bd, commit time:", git("log", "-1", "--format=%cI", "5e12c4bd"))
print("E98's pre-registration c8e84226, commit time:", git("log", "-1", "--format=%cI", "c8e84226"), "; lines naming E100 in its tree:", len(git("grep", "-n", "E100", "c8e84226", "--", "tools/claims-v3/kspeed/e98/").splitlines()))
print("the two pushes, from the origin reflog of the clone that made them (not in a fresh clone): 5e12c4bd 00:49:33 PDT, c8e84226 00:38:23 PDT")
L = R.jl(os.path.join(HERE, "smoke", "launches.jsonl"))
print("first launch of E100, smoke:", DT.datetime.fromtimestamp(min(x["t_start_ms"] for x in L) / 1000, z).strftime("%H:%M:%S"), "PDT; slot start", DT.datetime.fromtimestamp(1793521800, z).strftime("%H:%M:%S"), "PDT")
print("so the pre-registration came after the shared claim, whose lane's own pre-registration named E100 and its slot, and before E100's first launch")

print("\n======== C9. The die")
m0 = ma = 0
for f in glob.glob(os.path.join(HERE, "s1", "tel", "*")):
    with gzip.open(f, "rt") as h:
        for ln in h:
            ln = ln.strip()
            if ln.startswith("{"):
                ms = (json.loads(ln).get("temp_c") or {}).get("minshire")
                if ms:
                    m0 = max(m0, ms[0])
                    ma = max(ma, max(ms))
print(f"highest minshire[0] {m0} C, the array's highest {ma} C")
