#!/usr/bin/env python3
"""E96: the desk check behind the corrections after verification (Sun 1 Nov 2026). Desk only: it reads the committed session and the committed
reductions, and prints every number the README's "Corrections after verification" section quotes. Nothing registered is recomputed differently and no
verdict moves: the per-sample conventions are reduce_hpl.py's (E64's), and the registered numbers it starts from are read from results.json. Everything
here is post hoc and labelled. Standard library only.

    python3 corrections-check.py > corrections-check.txt
"""
import gzip
import json
import math
import os
import random
import statistics as st
import struct
import sys
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kspeed/e83"))
import predict_e83 as PE  # noqa: E402

R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/kspeed/e96/predictions.json")))
R87 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e87-real-tensors-speed/results.json")))
C, T, runs, post = R["cells"], P["tiles"], R["runs"], R["posthoc"]
B = {int(k): v for k, v in P["constants"]["B_registered_w"].items()}
S = {int(k): v for k, v in P["constants"]["s_f"].items()}
rel = PE.Rel(B)
Wb, sb = P["relation"]["burst"]["W_star_w"], P["relation"]["burst"]["sigma_w"]
Ws, ss = P["relation"]["sustained"]["W_star_w"], P["relation"]["sustained"]["sigma_w"]
T975 = P["t975"]
ARM_REF = "int8/full"
REALS = ["int8/l0_mlp_up", "int8/l6_mlp_down", "int8/l6_attn_qk"]
BYRUN = {}
for ln in gzip.open(os.path.join(HERE, "s1", "launches.jsonl.gz"), "rt"):
    L = json.loads(ln)
    if L.get("role") == "work":
        BYRUN.setdefault(L["run"], []).append(L)


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def last40(m):
    """The in-kernel trace samples of the last 40 s of the work: reduce_hpl.py's window."""
    pr = BYRUN[m["run"]]
    t0 = min(p["t_start_ms"] for p in pr)
    kw = [((k["t_start_ms"] - t0) / 1000.0, (k["t_end_ms"] - t0) / 1000.0) for p in pr for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
    t_end = m["work_s"]
    return [x for x in m["trace"] if x[0] >= t_end - 40.0 and any(a <= x[0] <= b for a, b in kw) and x[3] in (600, 700, 800)], kw


def shares(m):
    w, _ = last40(m)
    n = len(w)
    return {f: sum(1 for x in w if x[3] == f) / n for f in (600, 700, 800)}, n


SUS = sorted((m for m in runs if m["block"] == "SUS"), key=lambda m: m["t_first_ms"])
ARM = [m for m in SUS if m.get("round") is not None]
D = post["arm_rounds_detail"]
ROUNDS = sorted(D, key=int)

print("======== C1. The int8 arm sits near the cap")
lim = [m["limit"] for m in ARM]
print(f"  arm runs {len(ARM)}: limit none {sum(1 for x in lim if x == 'none')}, thermal {sum(1 for x in lim if x == 'thermal')}; at_the_cap as scored: {R['rules']['E96-I1']['at_the_cap']} (false by one run: round 3's int8 full)")
real = [m for m in ARM if m["kind"] in REALS]
at800 = [m for m in real if m["sus_mhz_mean"] == 800]
print(f"  real runs reading exactly 800.0: {len(at800)} of {len(real)}, every sample of the window at 800: {all(shares(m)[0][800] == 1.0 for m in at800)}: {[(m['round'], m['kind'].split('/')[1]) for m in at800]}")
full = {int(r): D[r][ARM_REF]["mhz"] for r in ROUNDS}
ceil_ = {r: round(800.0 - v, 1) for r, v in full.items()}
cm = st.mean(ceil_.values())
print(f"  a real tile cannot pass 800, so d_r <= 800 - F_r: by round {ceil_}, mean +{cm:.1f} MHz")
i1 = R["rules"]["E96-I1"]
print(f"  measured +{i1['mean']:.3f} MHz, {100 * i1['mean'] / cm:.0f}% of that ceiling; the interval's top +{i1['hi']:.3f} lies above it; DIFFERENT_BEYOND_BAR needs a lower end over +15, out of reach on these runs")
print("  the registered rule at this night's spreads, with the clamp (a run ~ min(800, N(mu, s)), four rounds; seed 9601, 20,000 draws, the verifier's parameter sets and order):")


def partition(lo, hi, bar=15.0):
    if lo > bar or hi < -bar:
        return "BEYOND"
    if lo <= 0 <= hi:
        return "SAME" if (-bar <= lo and hi <= bar) else "INCONCLUSIVE"
    return "SMALL" if (-bar <= lo and hi <= bar) else "DIFFERENT"


rng = random.Random(9601)


def sim(muF, sdF, sdT, delta, sdRound, N=20000):
    c = {}
    means = []
    for _ in range(N):
        dr = []
        for _r in range(4):
            e = rng.gauss(0, sdRound)
            F = min(800.0, rng.gauss(muF, sdF) + e)
            Ts = [min(800.0, rng.gauss(muF + delta, sdT) + e) for _t in range(3)]
            dr.append(sum(Ts) / 3.0 - F)
        m = sum(dr) / 4.0
        h = 3.182 * st.stdev(dr) / 2.0
        v = partition(m - h, m + h)
        c[v] = c.get(v, 0) + 1
        means.append(m)
    return {k: round(x / N, 3) for k, x in sorted(c.items())}, round(sum(means) / N, 1)


TAB = {}
for pset in ((790.0, 6.0, 5.0, 0.0), (790.0, 8.3, 5.1, 0.0), (793.0, 6.0, 5.0, 5.0)):
    for delta in (0, 6, 12, 21, 40, 80):
        v, md = sim(pset[0], pset[1], pset[2], delta, pset[3])
        TAB.setdefault(delta, []).append(v.get("SAME", 0.0))
        print(f"    full mean {pset[0]}, sd {pset[1]}, real sd {pset[2]}, round sd {pset[3]}, true difference {delta:3d}: {v}, mean reading {md}")
for delta in (0, 6, 12, 21, 40, 80):
    print(f"    P(SAME_WITHIN_BAR) at a true {delta}: {100 * min(TAB[delta]):.0f}-{100 * max(TAB[delta]):.0f}%")
print()

print("======== C2. The clocks of the seven gated float tiles: frozen from the tile's bytes first")
ZS = P["claims_e96"]["S2_gate_buys_speed"]["tiles"] + ["fp32/resnet18_l2c1"]
ref = {"fp32": "fp32/randn", "fp16": "fp16/randn"}
SLOPE = [k for k in ZS if C[k]["sus_last"][0]["800"] < 0.9]
print(f"  the sustained tiles under 90% at 800 MHz (the slope): {SLOPE}")


def row(name, fb, fs):
    db = [C[k]["burst_mhz"] - fb(k) for k in ZS]
    ds = [C[k]["sus_mhz"] - fs(k) for k in ZS]
    dq = [C[k]["sus_mhz"] - fs(k) for k in SLOPE]
    print(f"  {name:44s} burst rms {rms(db):6.2f} | sustained rms {rms(ds):6.2f}, mean {st.mean(ds):+6.1f} | the five on the slope {rms(dq):6.2f}")


row("frozen (a), from the tile's bytes", lambda k: T[k]["frozen"]["burst_mhz"], lambda k: T[k]["frozen"]["sus_mhz"])
row("frozen gate law, from the tile's bytes, no fit", lambda k: T[k]["gate_law"]["burst_mhz"], lambda k: T[k]["gate_law"]["sus_mhz"])
row("the relation on the same session's measured c", lambda k: C[k]["rel_on_measured_c_burst_mhz"], lambda k: C[k]["rel_on_measured_c_sus_mhz"])
row("real = random (same-session randn)", lambda k: C[ref[k.split("/")[0]]]["burst_mhz"], lambda k: C[ref[k.split("/")[0]]]["sus_mhz"])
print(f"  the relation's burst rms is one tile: {sum(1 for k in ZS if C[k]['burst_mhz'] == 800)} of 7 sit at the cap; resnet18_l2c1's miss {C['fp32/resnet18_l2c1']['burst_mhz'] - C['fp32/resnet18_l2c1']['rel_on_measured_c_burst_mhz']:+.1f}, over sqrt(7) = {abs(C['fp32/resnet18_l2c1']['burst_mhz'] - C['fp32/resnet18_l2c1']['rel_on_measured_c_burst_mhz']) / math.sqrt(7):.2f}")
print("  c is the mean of the tile's two bursts in this session: in the burst the relation is scored against the same two runs, sustained against other runs of the session")
print(f"  sustained, (a)'s miss, frozen - measured: { {k: round(T[k]['frozen']['sus_mhz'] - C[k]['sus_mhz'], 1) for k in ZS} }; high on {sum(1 for k in ZS if T[k]['frozen']['sus_mhz'] > C[k]['sus_mhz'])} of 7")
ds = rms([C[k]["sus_mhz"] - T[k]["frozen"]["sus_mhz"] for k in ZS])
dr_ = rms([C[k]["sus_mhz"] - C[k]["rel_on_measured_c_sus_mhz"] for k in ZS])
print(f"  in quadrature, (a)'s power error explains sqrt({ds:.2f}^2 - {dr_:.2f}^2) = {math.sqrt(ds * ds - dr_ * dr_):.1f} of the {ds:.1f}; {dr_:.1f} remains with the measured c")
print()

print("======== C3. Step-downs, and the die difference")


def stepdown(m):
    """below-800 samples of the window with a 66 C reading in the last 2 s: E64's recent_hot, from the sampler alone."""
    w, kw = last40(m)
    ws = [x for x in m["trace"] if any(a <= x[0] <= b for a, b in kw)]
    n = 0
    for x in w:
        if x[3] < 800 and any(y[1] is not None and y[1] >= 66 and x[0] - 2.0 <= y[0] <= x[0] for y in ws):
            n += 1
    return n, len(w)


for r in ROUNDS:
    row_ = []
    for k in [ARM_REF] + REALS:
        m = next(x for x in ARM if x["run"] == D[r][k]["run"])
        n, tot = stepdown(m)
        row_.append(f"{k.split('/')[1]} {n} ({m['sus_last']['thermal']}) die_max {m['die_max']}")
    print(f"  round {r}, samples below 800 with a 66 C reading in the last 2 s (the E64 label's share): " + "; ".join(row_))
fs = sum(1 for m in ARM if m["kind"] == ARM_REF and stepdown(m)[0] > 0)
rs = sum(1 for m in real if stepdown(m)[0] > 0)
print(f"  runs that stepped down: int8 full {fs} of 4, real tiles {rs} of 12; labelled thermal: 1 of 4, 0 of 12")
print(f"  post hoc, hypergeometric: 4 of 4 against 1 of 12, p = {comb(5, 4) * comb(11, 0) / comb(16, 4):.4f}; 1 of 4 against 0 of 12, p = {comb(1, 1) * comb(15, 3) / comb(16, 4):.2f}")
first = {}
for m in ARM:
    first.setdefault(m["round"], m["kind"])
for field, unit in (("die", "C"), ("w", "W"), ("mhz", "MHz")):
    ds_ = [st.mean(D[r][k][field] for k in REALS if k != first[int(r)]) - D[r][ARM_REF][field] for r in ROUNDS]
    m_, sd = st.mean(ds_), st.stdev(ds_)
    h = T975["3"] * sd / 2.0
    print(f"  each round's first run left out, {field}: {m_:+.3f} {unit} [{m_ - h:+.3f}, {m_ + h:+.3f}]; registered {R['rules']['E96-I3' if field == 'die' else ('E96-I2' if field == 'w' else 'E96-I1')]['mean']:+.3f}")
print()

print("======== C4. Not closed for speed: narrowed")
for k in ("fp32/t5small_l0_up", "fp32/vit_l11_down", "fp32/bert_l6_up", "fp16/vit_l5_down"):
    m = next(x for x in SUS if x["kind"] == k)
    sh, n = shares(m)
    print(f"  {k}: one run, {C[k]['sus_mhz']} MHz, {100 * sh[600]:.0f}% of the window at 600 MHz, {100 * sh[700]:.0f}% at 700, {100 * sh[800]:.0f}% at 800")
i8 = [k for k in T if T[k]["type"] == "int8"]
print(f"  every int8 burst: {len(i8)} real2 tiles, 16 passes, at 800.0: {sum(1 for k in i8 for x in C[k]['burst_mhz_runs'] if x == 800)}; int8 full {C['int8/full']['burst_mhz_runs']}, int8 zeros {C['int8/zeros']['burst_mhz_runs']}: a burst separates nothing in int8")
print(f"  int8 tiles with a sustained run among the real2 list: {[k for k in P['sus_core'] if k.startswith('int8')]}")
print()

print("======== C5. Which readings are limited by the cap or the floor")
atcap = [k for k in T if C[k]["burst_mhz"] == 800]
print(f"  bursts at exactly 800.0: {len(atcap)} of {len(T)}: {sum(1 for k in atcap if T[k]['type'] != 'int8')} gated float, {sum(1 for k in atcap if T[k]['type'] == 'int8')} int8; S2's +96.1 and +77.3 are 800 minus randn's two cells")
print("  sustained, share of the window at 800 / 600 MHz, by the frozen gate fraction:")
for f in ("fp32", "fp16"):
    ks = sorted((k for k in ZS if k.startswith(f)), key=lambda k: T[k]["gated_lane_frac"])
    for k in ks:
        m = next(x for x in SUS if x["kind"] == k)
        sh, _ = shares(m)
        print(f"    {k:24s} gate {T[k]['gated_lane_frac']:.3f} sustained {C[k]['sus_mhz']:6.1f} at 800 {100 * sh[800]:3.0f}% at 600 {100 * sh[600]:3.0f}% die {C[k]['sus_die']} limit {C[k]['sus_limit']} c {C[k]['c_w']}")
for k in ("fp32/randn", "fp16/randn"):
    ms = [x for x in SUS if x["kind"] == k]
    print(f"    {k:24s} sustained {[m['sus_mhz_mean'] for m in ms]} at 600 {[round(100 * shares(m)[0][600]) for m in ms]}%")
print(f"  across formats: fp16 resnet18_l3c1, gate {T['fp16/resnet18_l3c1']['gated_lane_frac']:.3f}, {C['fp16/resnet18_l3c1']['sus_mhz']} MHz, above fp32 resnet18_l3c1, gate {T['fp32/resnet18_l3c1']['gated_lane_frac']:.3f}, {C['fp32/resnet18_l3c1']['sus_mhz']} MHz; c {C['fp16/resnet18_l3c1']['c_w']} and {C['fp32/resnet18_l3c1']['c_w']}; one run's sigma 15.6 MHz")
print(f"  the top two tiles' deficit from 800 lies in launch ramps: { {k: C[k]['sus_mhz'] for k in ('fp32/t5small_l0_down', 'fp16/t5small_l0_down')} } (checks.txt K3)")
print()

print("======== C6. What a no-skill rule would score on S4 and S1")
lab = {k: C[k]["sus_limit"] for k in P["sus_core"]}
th = sum(1 for v in lab.values() if v == "thermal")
print(f"  S4: measured labels {lab}; a constant 'thermal' guess is right on {th} of {len(lab)}, {100 * th / len(lab):.1f}%, itself a PASS at >= 80%. The frozen labels score {R['rules']['E96-S4']['right']} of {len(lab)}")
fl = [k for k in T if T[k]["type"] != "int8"]
nb = sum(1 for k in fl if T[k]["frozen"]["burst_scoring_interval_mhz"][0] <= C[ref[k.split("/")[0]]]["burst_mhz"] <= T[k]["frozen"]["burst_scoring_interval_mhz"][1])
nd = sum(1 for k in P["sus_core"] if T[k]["frozen"]["sus_scoring_interval_mhz"][0] <= C[ref[k.split("/")[0]]]["sus_mhz"] <= T[k]["frozen"]["sus_scoring_interval_mhz"][1])
print(f"  S1 under 'real = random' (each tile at same-session randn): bursts inside {nb} of {len(fl)} float tiles, against the frozen points' {sum(1 for k in fl if T[k]['frozen']['burst_scoring_interval_mhz'][0] <= C[k]['burst_mhz'] <= T[k]['frozen']['burst_scoring_interval_mhz'][1])}; sustained inside {nd} of {len(P['sus_core'])}")
print()

print("======== C7. The carryover on resnet18_l2c1")
core = [m for m in SUS if m["kind"] in P["sus_core"]]
rows = []
for m in core:
    i = SUS.index(m)
    prev = SUS[i - 1]
    miss = m["sus_mhz_mean"] - C[m["kind"]]["rel_on_measured_c_sus_mhz"]
    rows.append((m["kind"], prev["kind"], prev["sus_w_mean"], m["gate"].get("held_s"), m["die_start"], round(miss, 1)))
    print(f"  {m['kind']:24s} after {prev['kind']:24s} {prev['sus_w_mean']:6.2f} W, gate held {m['gate'].get('held_s')} s, die at the launch {m['gate']['reading'][0]} C, first work die {m['die_start']} C, miss against the relation on measured c {miss:+6.1f} MHz")
sl = [x for x in rows if x[0] in SLOPE]
xs, ys = [x[2] for x in sl], [x[5] for x in sl]
mx, my = st.mean(xs), st.mean(ys)
r_ = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
print(f"  on the five slope tiles, the miss against the previous run's W: r = {r_:.2f}, n = {len(xs)}, post hoc")
c = C["fp32/resnet18_l2c1"]["c_w"]
per_w = 100.0 / ((B[700] + c * S[700]) - (B[600] + c * S[600]))
print(f"  resnet18_l2c1 at c {c}: {per_w:.1f} MHz per W on the relation; K7's carryover, +0.0427 C per W over about 17 W of previous run, is -0.73 C, which at 0.4573 C/W is +{0.73 / 0.4573:.1f} W of room at the trip, so about +{per_w * 0.73 / 0.4573:.0f} MHz of its +19.9")
print()

print("======== C8. The estimator on the float tiles: it moves no rule")


def p(m, f):
    return (m.get("p_ref58_w") or {}).get(str(f))


def c800(m):
    return (p(m, 800) - B[800]) / S[800]


def c68(m):
    pts = [f for f in (600, 800) if p(m, f) is not None]
    return sum(S[f] * (p(m, f) - B[f]) for f in pts) / sum(S[f] ** 2 for f in pts)


BUR = {}
for m in runs:
    if m["block"] == "BURST":
        BUR.setdefault(m["kind"], []).append(m)
for name, fn in (("c from the 800 MHz power alone", c800), ("c from 600 and 800 MHz", c68)):
    rb = rms([C[k]["burst_mhz"] - rel.f(st.mean(fn(m) for m in BUR[k]), Wb, sb)[0] for k in T])
    rs_ = rms([C[k]["sus_mhz"] - rel.f(st.mean(fn(m) for m in BUR[k]), Ws, ss)[0] for k in P["sus_core"]])
    rz = rms([C[k]["sus_mhz"] - rel.f(st.mean(fn(m) for m in BUR[k]), Ws, ss)[0] for k in ZS])
    print(f"  S5 with {name}: burst rms {rb:.2f}, sustained rms {rs_:.2f}; the seven's sustained rms {rz:.2f}")
print(f"  S5 as registered: burst rms {R['rules']['E96-S5']['burst_rms_mhz']}, sustained rms {R['rules']['E96-S5']['sus_rms_mhz']}")
hold = [k for k in ZS if C[k]["burst_mhz"] == 800]


def n700(m):
    tr = [x for x in m["trace"] if 0 <= x[0] <= m["work_s"] + 0.2 and x[2] is not None and x[3] in (600, 700, 800) and x[1] is not None]
    return sum(1 for i in range(1, len(tr)) if tr[i][3] == 700 and tr[i - 1][3] == 700)


print(f"  gated float tiles that hold 800 in the burst: {len(hold)} of 7; samples in their P700, pass by pass: { {k: [n700(m) for m in BUR[k]] for k in hold} }")
print(f"  their c against c800: { {k: (C[k]['c_w'], round(st.mean(c800(m) for m in BUR[k]), 3)) for k in ZS} }")
print(f"  largest |c - c800| over the seven: {max(abs(C[k]['c_w'] - st.mean(c800(m) for m in BUR[k])) for k in ZS):.2f} W; largest c800 pass to pass: {max(abs(c800(BUR[k][0]) - c800(BUR[k][1])) for k in ZS):.2f} W")
m8 = {k: st.mean(c800(m) for m in BUR[k]) for k in ZS}
near = sum(1 for k in ZS if abs(m8[k] - T[k]["gate_law"]["c_w"]) < abs(m8[k] - T[k]["frozen"]["c_w"]))
print(f"  on c800: nearer the gate law on {near} of 7, rms {rms([m8[k] - T[k]['gate_law']['c_w'] for k in ZS]):.2f} W against (a)'s {rms([m8[k] - T[k]['frozen']['c_w'] for k in ZS]):.2f} W; (a)'s mean miss {st.mean(m8[k] - T[k]['frozen']['c_w'] for k in ZS):+.2f} W (on the registered c, +0.79)")
v = "fp32/vgg16_fc2"
print(f"  S4's fp32 vgg16_fc2, the relation on its c by estimator: registered {rel.f(C[v]['c_w'], Ws, ss)[0]:.1f}, c800 {rel.f(st.mean(c800(m) for m in BUR[v]), Ws, ss)[0]:.1f}, c from 600 and 800 {rel.f(st.mean(c68(m) for m in BUR[v]), Ws, ss)[0]:.1f}; measured {C[v]['sus_mhz']}, one run's sigma 15.6")
E8 = {}
for m in R87["runs"]:
    if m["block"] == "BURST" and m.get("kind") in [ARM_REF] + REALS:
        E8.setdefault(m["kind"], []).append(c800(m))
a8 = st.mean(rel.f(st.mean(E8[k]), Ws, ss)[0] for k in REALS) - rel.f(st.mean(E8[ARM_REF]), Ws, ss)[0]
print(f"  the arm's expected clock difference on E87's c800: {a8:+.1f} MHz (frozen, on E87's registered c: {P['arm']['expected']['clock_difference_relation_mhz']:+.1f})")
print()

print("======== C9. The burst noise of this session, in fp16's and fp32's difference")
pl = [k for k in list(T) + ["fp32/randn", "fp16/randn"] if C[k].get("burst_limit") == "power"]
hs = [(C[k]["burst_mhz_runs"][0] - C[k]["burst_mhz_runs"][1]) / 2 for k in pl]
cell = rms(hs)
print(f"  a cell's random part in this session: {cell:.1f} MHz, over {len(pl)} power-limited tiles (E83 C6: 5.3)")
d16 = R["rules"]["E96-S3"]["rows"][1][3]
d32 = R["rules"]["E96-S3"]["rows"][0][3]
s16, s32 = cell * math.sqrt(1 / 3 + 1), cell * math.sqrt(1 / 4 + 1)
print(f"  fp16 {d16:+.1f} MHz: 1 sigma {s16:.1f}, {d16 / s16:+.2f} sigma; fp32 {d32:+.1f} MHz: 1 sigma {s32:.1f}, {d32 / s32:+.2f} sigma")
e87 = 5.3 * math.sqrt(1 / 3 + 1)
print(f"  two sessions, fp16: E87 +7.8 (1 sigma {e87:.1f}), E96 {d16:+.1f} (1 sigma {s16:.1f}): mean {(7.8 + d16) / 2:+.1f}, 1 sigma {math.sqrt(e87 ** 2 + s16 ** 2) / 2:.1f}")
print()

print("======== C10. The order of the registration, the claim and the first touch of the card, epoch s")
PUSH, CLAIM, TOUCH, LAUNCH = 1793520789, 1793518749.971, 1793527500.058, None
for ln in gzip.open(os.path.join(HERE, "smoke", "launches.jsonl.gz"), "rt"):
    x = json.loads(ln)
    LAUNCH = x["t_start_ms"] / 1000.0 if LAUNCH is None else min(LAUNCH, x["t_start_ms"] / 1000.0)
print(f"  the shared claim, E98's lane's message: {CLAIM} (00:39:09.971 PDT); the commit 0c187e12: {PUSH} (01:13:09 PDT), {(PUSH - CLAIM) / 60:.0f} min later")
print(f"  this lane's first card read: {TOUCH}, {(TOUCH - PUSH) / 3600:.2f} h after the commit; first launch: {LAUNCH}, {(LAUNCH - PUSH) / 3600:.2f} h after it")
print()

print("======== C11. Small wording: the numbers behind it")
print(f"  S2's tiles are those whose (a) D is under 15 W; two measured c are above it: { {k: (T[k]['D_w'], C[k]['c_w']) for k in ('fp32/resnet18_l3c1', 'fp16/resnet18_l3c1')} }")
tb = open(os.path.join(ROOT, "tools/claims-v3/kinds/real2/tiles/fp32/vit_l11_down.bin"), "rb").read()
words = struct.unpack("<256I", tb[:1024])
nz = sum(1 for x in words if x == 0x80000000)
print(f"  the fp32 ViT tile's A words that are -0.0: {nz} of 256, {100 * nz / 256:.1f}%; zero words {sum(1 for x in words if x == 0)}; the whole block's activations, 55% (tools/claims-v3/kinds/real2/README.md, result 3)")
