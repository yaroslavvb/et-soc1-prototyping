#!/usr/bin/env python3
"""E100, post hoc and labelled: never a verdict. Views written after the registered scoring, from the same session.

    python3 posthoc_e100.py <RUNDIR> <results.json> [--tools <dir of reduce_e100.py>] [--out posthoc.json] > posthoc.txt

1. What the gaps really were: per arm, the kernels' wall at 800 MHz, the measured gap (start stamp minus previous end stamp), the idle fraction, and falls per heartbeat against f(1 - f).
2. The lattice by arm: the two rounds' fits scored on every arm on the other round, R on its own.
3. The kernel-boundary falls of A0 and A5 against the lattice: x, the time at 800 MHz inside the hit kernel, and the distance from the lattice, as the desk reading did.
4. Gaps between processes, here 197 ms plus a random pause: a lattice point in the gap against a fall.
5. The climbs: first 800 reading from the first heartbeat inside a kernel, by arm, for processes starting at 600 MHz: does the statistics reset slow a climb?
6. The reset's place at R's falls against its place at every reading in R.
7. The card: highest die and board reading, configuration reads, the rings' alarm lines and POWER_IDLE lattice.
"""
import argparse
import json
import math
import os
import statistics as st
import sys

ap = argparse.ArgumentParser()
ap.add_argument("rundir")
ap.add_argument("results")
ap.add_argument("--tools", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "tools", "claims-v3", "e100"))
ap.add_argument("--hpl", default=None)
ap.add_argument("--out")
a = ap.parse_args()
sys.path.insert(0, os.path.abspath(a.tools))
import reduce_e100 as R  # noqa: E402

REPO = os.path.abspath(os.path.join(a.tools, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "hpl"))
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "dv2"))
import sptrace_full as spf  # noqa: E402

runs = R.load(a.rundir)
res = json.load(open(a.results))
rules = res["rules"]
ORDER = ["A0", "A5", "A20", "A100", "N", "R"]
CODES = {"A0": 1, "A5": 2, "A20": 3, "A100": 4, "N": 5, "R": 6}
out = {"note": "post hoc, labelled; never a verdict"}

# 1. the gaps
print("1. What the gaps were (per arm, kernels after the calibration one)")
print("arm    kernels  wall at 800 MHz, s  mean gap ms   max gap ms   idle share of the kernels' time   f(1-f)     falls per heartbeat")
gaps = {}
for arm in ORDER:
    g, w800, tot_k, tot_g = [], [], 0.0, 0.0
    for r in runs:
        if r["arm"] != arm:
            continue
        for pr in r["procs"]:
            ks = pr["kernels"]
            for j in range(len(ks)):
                ge = R.g_eff(ks[j])
                if ks[j].get("launch", -1) >= 0 and ge and ge >= 0.79:
                    w800.append(ks[j]["wall_s"])
                if j >= 2:
                    d = ks[j]["t_start_ms"] - ks[j - 1]["t_end_ms"]
                    g.append(d)
                    tot_g += d
                    tot_k += ks[j]["wall_s"] * 1000.0
    f = tot_g / (tot_g + tot_k) if tot_g + tot_k else 0.0
    # the hidden 0.7 ms between the host's stamps and the slot, the difference between the 2.0 ms zone and the 1.29 ms stamp gap, is added for the f(1-f) column
    f2 = (tot_g + 0.7 * len(g)) / (tot_g + 0.7 * len(g) + tot_k) if tot_k else 0.0
    A = res["arms"].get(arm, {})
    gaps[arm] = {"kernels": len(g) + 1, "wall_800_s": round(st.median(w800), 4) if w800 else None, "gap_mean_ms": round(st.mean(g), 2) if g else None, "gap_max_ms": max(g) if g else None, "idle_share": round(f2, 4), "f1f": round(f2 * (1 - f2), 4), "rate": A.get("rate")}
    print(f"{arm:6s} {len(g) + 1:7d} {gaps[arm]['wall_800_s']}          {gaps[arm]['gap_mean_ms']}      {gaps[arm]['gap_max_ms']}        {f2 * 100:6.2f}%                        {f2 * (1 - f2) * 100:5.2f}%     {(A.get('rate') or 0) * 100:5.2f}%")
out["gaps"] = gaps

# 2. the lattice by arm
r1 = [r for r in runs if r["round"] == 1]
r2 = [r for r in runs if r["round"] == 2]
R1, R2 = R.Round(r1), R.Round(r2)
pa, qa = rules["D3"]["lattice_round1"]["p_ms"], rules["D3"]["lattice_round1"]["q_ms"]
pb, qb = rules["D3"]["lattice_round2"]["p_ms"], rules["D3"]["lattice_round2"]["q_ms"]
print("\n2. Each round's lattice on the other round, by arm: gap and fell, gap no fall, kernel and fell, kernel no fall")
byarm = {}
for arm in ORDER:
    t12 = R2.score(pa, qa, {CODES[arm]})
    t21 = R1.score(pb, qb, {CODES[arm]})
    tot = [t12[i] + t21[i] for i in range(4)]
    byarm[arm] = tot
    print(f"  {arm:6s} {tot}")
out["lattice_by_arm"] = byarm

# a sharper lattice for the rest: every arm of the whole session, with a wider period range, starting from the rounds' fits (post hoc)
class Whole(R.Round):
    pass


W = R.Round(runs)
best = None
for dq in range(-40, 41):
    q = 1000.0 + dq * 0.0005
    for pp in range(0, 1000, 2):
        p = W.t0 + pp
        tp, fn, fp, tn = W.score(p, q)
        sc = tp - 3 * fp - fn
        if best is None or sc > best[0]:
            best = (sc, p, q, (tp, fn, fp, tn))
_, pw, qw, tw = best
for dq in range(-4, 5):
    for pp in range(-6, 7):
        q, p = qw + dq * 0.0001, pw + pp
        tp, fn, fp, tn = W.score(p, q)
        sc = tp - 3 * fp - fn
        if sc > best[0]:
            best = (sc, p, q, (tp, fn, fp, tn))
_, pw, qw, tw = best
print(f"\nOne lattice on the whole session (in sample): period {qw:.4f} ms, table {tw}")
out["whole_session_lattice"] = {"p_ms": pw, "q_ms": round(qw, 4), "table": tw}

# 3. the boundary falls
print("\n3. Every kernel-channel fall: arm, kernel, x (ms at 800 MHz inside the hit kernel, for the arms with no long gap), gap before it, distance of the kernel's start stamp from the whole-session lattice")
rows = []
for r in runs:
    for pr in r["procs"]:
        ks = pr["kernels"]
        for j in range(1, len(ks)):
            g0, g1 = R.g_eff(ks[j - 1]), R.g_eff(ks[j])
            if ks[j - 1].get("launch", -1) >= 0 and g0 and g1 and 0.55 <= g1 < 0.62 and g0 >= 0.69:
                w = ks[j]["wall_s"] - R.OVERHEAD_S
                x = (ks[j]["cycles_max"] - 0.6e9 * w) / 0.2e9 * 1000.0
                t0 = ks[j]["t_start_ms"]
                k = round((t0 - pw) / qw)
                rows.append({"arm": r["arm"], "round": r["round"], "run": r["run"], "launch": ks[j].get("launch"), "x_ms": round(x, 1), "gap_ms": t0 - ks[j - 1]["t_end_ms"], "d_ms": round(t0 - (pw + qw * k), 1), "prev_g": round(g0, 4)})
for arm in ("A0", "A5"):
    for x in [y for y in rows if y["arm"] == arm]:
        print("  ", x)
xs = [x["x_ms"] for x in rows if x["arm"] in ("A0",)]
print("   A0's and A5's falls at kernel starts: x", [x["x_ms"] for x in rows if x["arm"] in ("A0", "A5")], "ms; distance from the lattice", [x["d_ms"] for x in rows if x["arm"] in ("A0", "A5")], "ms")
print("   all kernel-channel falls by arm:", {arm: sum(1 for x in rows if x["arm"] == arm) for arm in ORDER}, "; x in A100 and A20, median:", st.median([x["x_ms"] for x in rows if x["arm"] in ("A100", "A20")]) if rows else None)
out["kernel_falls"] = rows

# 4. gaps between processes
print("\n4. Gaps between processes in a run (197 ms plus the random pause): lattice point in the gap against a fall, for a process that ended above 600 MHz")
T4 = {"in_fell": 0, "in_no": 0, "out_fell": 0, "out_no": 0}
exc = []
glen = []
for r in runs:
    for i in range(1, len(r["procs"])):
        prev, cur = r["procs"][i - 1], r["procs"][i]
        if not prev["kernels"] or not cur["kernels"]:
            continue
        ta, tb = prev["kernels"][-1]["t_end_ms"], cur["kernels"][0]["t_start_ms"]
        before = [x for x in r["tel"] if x[0] <= ta and x[3] is not None]
        if not before or before[-1][3] <= 600:
            continue
        glen.append(tb - ta)
        k0, k1 = math.ceil((ta - 1 - pw) / qw), math.floor((tb + 1 - pw) / qw)
        inside = k1 >= k0
        S = [x for x in r["tel"] if ta <= x[0] <= tb + 400 and x[3] is not None]
        fell = any(x[3] == 600 for x in S)
        T4[("in_" if inside else "out_") + ("fell" if fell else "no")] += 1
        if inside != fell:
            exc.append({"run": r["run"], "gap_ms": tb - ta, "inside": inside, "fell": fell})
print("  ", T4, "; gap length median", st.median(glen) if glen else None, "ms; exceptions", exc[:8])
out["process_gaps"] = {"table": T4, "gap_ms_median": st.median(glen) if glen else None, "exceptions": exc}

# 5. the climbs
print("\n5. Processes starting at 600 MHz: first 800 reading from the first lattice point inside a kernel, s (no limit in reach)")
climb = {}
for r in runs:
    for pr in r["procs"]:
        ks = pr["kernels"]
        S = [x for x in r["tel"] if pr["t0"] <= x[0] <= pr["t1"] and x[3] is not None]
        if not ks or not S or S[0][3] != 600:
            continue
        t8 = next((x[0] for x in S if x[3] == 800), None)
        if t8 is None:
            continue
        k = math.ceil((ks[0]["t_start_ms"] - pw) / qw)
        tau = None
        for kk in range(k, k + 12):
            pt = pw + qw * kk
            if any(q0["t_start_ms"] + 1.2 <= pt <= q0["t_end_ms"] for q0 in ks):
                tau = pt
                break
        if tau is None:
            continue
        climb.setdefault(r["arm"], []).append((t8 - tau) / 1000.0)
for arm in ORDER:
    v = climb.get(arm)
    if v:
        print(f"  {arm:6s} n {len(v):3d} median {st.median(v):.3f} sd {st.pstdev(v):.3f} min {min(v):.3f} max {max(v):.3f}")
out["climbs"] = {arm: {"n": len(v), "median": round(st.median(v), 3), "sd": round(st.pstdev(v), 3)} for arm, v in climb.items() if v}

# 6. the reset's place
print("\n6. The statistics reset in R")
allv = [x[4] for r in runs if r["arm"] == "R" for x in r["tel"] if x[4] is not None and x[4] >= 0]
share = sum(1 for v in allv if v in (0, 100)) / len(allv) if allv else None
atf = rules["D5"].get("since_reset_ms_at_falls") or []
hit = sum(1 for v in atf if v in (0, 100))
n = len(atf)
p = sum(math.comb(n, i) * share ** i * (1 - share) ** (n - i) for i in range(hit, n + 1)) if share else None
print(f"   since_reset_ms 0 or 100 at {share:.3f} of R's readings; at {hit} of its {n} falls; one-sided binomial p {p:.3f}" if share else "   no reset readings")
out["reset"] = {"share_0_100": round(share, 3) if share else None, "falls_0_100": hit, "falls": n, "p": round(p, 3) if p is not None else None, "since_reset_at_falls": atf}

# 8. where in its kernel each sampler fall lands, by arm: x, the time the kernel ran at 800 MHz (A20, R, A100: a fall in the gap reads x near 0)
print("\n8. Sampler falls by where they land: x in ms at 800 MHz inside the kernel holding the 600 reading, for falls straight from 800 MHz with the kernel before at 0.79 GHz or more")
land = {}
for r in runs:
    pvs = R.process_view(r)
    for pr, pv in zip(r["procs"], pvs):
        ks = pr["kernels"]
        for f in pv["falls"]:
            j = next((i for i, k in enumerate(ks) if k["t_start_ms"] <= f["t600"] <= k["t_end_ms"]), None)
            if j is None or j == 0:
                land.setdefault(r["arm"], []).append(None)
                continue
            g0 = R.g_eff(ks[j - 1])
            w = ks[j]["wall_s"] - R.OVERHEAD_S
            x = (ks[j]["cycles_max"] - 0.6e9 * w) / 0.2e9 * 1000.0
            if g0 and g0 >= 0.79 and f["from"] == 800:
                land.setdefault(r["arm"], []).append(round(x, 1))
                if x > 40:
                    print(f"   {r['arm']} {r['run']} kernel {ks[j].get('launch')}: x {x:.1f} ms, kernel's clock {R.g_eff(ks[j]):.3f} GHz, the sampler's since_reset_ms there {f['since_reset_ms']}")
            else:
                land.setdefault(r["arm"], []).append(None)
for arm in ORDER:
    v = [x for x in land.get(arm, []) if x is not None]
    if v:
        print(f"   {arm:6s} n {len(v):3d} of {len(land[arm])}: min {min(v)}, median {st.median(v)}, max {max(v)} ms")
out["landing"] = {arm: v for arm, v in land.items()}

# 7. the card
die_max = w_max = 0
n_read = 0
at300 = 0
for r in runs:
    for x in r["tel"]:
        n_read += 1
        if x[1] is not None:
            die_max = max(die_max, x[1])
        if x[2] is not None:
            w_max = max(w_max, x[2])
        at300 += 1 if x[3] == 300 else 0
qs = R.jl(os.path.join(a.rundir, "queries.jsonl"))
RR = R.jl(os.path.join(a.rundir, "runs.jsonl"))
cfg = [q.get("queries", q).get("config") for q in RR] + [q.get("config") for q in qs]
bad = [c for c in cfg if not c or c.get("tdp_w") != 65 or c.get("temp_threshold_c") != 65]
alarm = 0
marks = {}
last = None
for name in sorted(os.listdir(os.path.join(a.rundir, "sp"))):
    cur = spf.scan(open(os.path.join(a.rundir, "sp", name), "rb").read()) or []
    for e in cur:
        if "alarm set point" in (e.get("text") or ""):
            alarm += 1
        if e["kind"] == "pstat" and e.get("throttle_state") == 0:
            marks[e["ts"]] = 1
ts = sorted(t for t in marks if t > max(marks) - 3600 * 1e6)
bestq = None
for i in range(-300, 301):
    q = 1e6 + i * 2.0
    c = sum(math.cos(2 * math.pi * (t % q) / q) for t in ts)
    s = sum(math.sin(2 * math.pi * (t % q) / q) for t in ts)
    rr = math.hypot(c, s) / len(ts)
    if bestq is None or rr > bestq[0]:
        bestq = (rr, q)
print(f"\n7. The card: {n_read} readings, highest die {die_max} C, highest board {w_max} W, {at300} at 300 MHz; {len(cfg)} configuration reads, {len(bad)} not 65 W / 65 C; alarm lines in the rings {alarm}; POWER_IDLE records {len(ts)}, period {bestq[1] / 1e6:.6f} s on the SP's tick, R {bestq[0]:.4f}")
out["card"] = {"readings": n_read, "die_max": die_max, "board_max_w": w_max, "at_300": at300, "config_reads": len(cfg), "config_bad": len(bad), "alarm_lines": alarm, "power_idle_records": len(ts), "ring_period_s": round(bestq[1] / 1e6, 6), "ring_R": round(bestq[0], 4)}
print(f"   rules as scored: { {k: v['verdict'] for k, v in rules.items()} }; left out {res.get('left_out_limit')}; nonzero rc {res.get('nonzero_rc')}")
if a.out:
    json.dump(out, open(a.out, "w"), indent=1)
