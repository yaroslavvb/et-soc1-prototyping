#!/usr/bin/env python3
"""Independent recomputation of the memory-anatomy page's latency claims from the committed raw data
(a copy under ./data, or --data DIR for a new pass). No card. Prints one JSON object with every number used in the
inventory. For a new pass: --l1-ref (reference to the build's own L1 hit), --fixed-model (no refit), --requester S.

    python3 recompute_latency.py > latency.json
"""
import collections
import json
import math
import os
import statistics as st
import struct
import sys

import argparse
HERE = os.path.dirname(os.path.abspath(__file__))
_ap = argparse.ArgumentParser(description=__doc__)
_ap.add_argument("--data", default=os.path.join(HERE, "data"), help="a folder of memprobe <name>.u32/<name>.json pairs")
_ap.add_argument("--requester", type=int, default=0, help="shire that issued the loads (memprobe_host --hart 64*s)")
_ap.add_argument("--fixed-model", action="store_true",
                 help="use the 19 Sep constant (91) and memory shire positions instead of refitting (out-of-sample test)")
_ap.add_argument("--l1-ref", action="store_true",
                 help="re-reference every latency so that this build's timed L1 hit (ladder) reads 5 cycles")
ARGS, _ = _ap.parse_known_args()
D = ARGS.data
REQ = ARGS.requester
sys.path.insert(0, os.path.join(HERE, "mp"))
import gen_ops as g  # noqa: E402

OVH = 5
BASE = 0x8040000000
OUT = {}
SHIFT = 0
if ARGS.l1_ref and os.path.exists(os.path.join(D, "ladder.json")):
    _m = json.load(open(os.path.join(D, "ladder.json")))
    _r = struct.unpack(f"<{len(_m['labels'])}I", open(os.path.join(D, "ladder.u32"), "rb").read())
    SHIFT = int(round(st.median(v for l, v in zip(_m["labels"], _r) if l[0] == "ladder" and l[2] in (-1, 0)) - 10))
OUT["l1_ref_shift"] = SHIFT


def load(name, raw=False, d=D):
    m = json.load(open(os.path.join(d, name + ".json")))
    r = struct.unpack(f"<{len(m['labels'])}I", open(os.path.join(d, name + ".u32"), "rb").read())
    if not raw:
        r = [(v if v < 2**31 else v - 2**32) - OVH - SHIFT for v in r]
    return m, [tuple(l) if isinstance(l, list) else l for l in m["labels"]], r


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))]


def binom_two_sided(k, n, p):
    """exact two-sided binomial p-value (sum of probabilities <= P(k))"""
    pk = math.comb(n, k) * p**k * (1 - p) ** (n - k)
    return min(1.0, sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(n + 1)
                        if math.comb(n, i) * p**i * (1 - p) ** (n - i) <= pk * (1 + 1e-9)))


def sign_test(x):
    pos = sum(1 for v in x if v > 0)
    neg = sum(1 for v in x if v < 0)
    n = pos + neg
    return {"pos": pos, "neg": neg, "zero": len(x) - n, "p_two_sided": binom_two_sided(pos, n, 0.5) if n else 1.0}


def hops(a, b):
    return g.hops(a, b)


def dist(s, p):
    return abs(g.MESH[s][0] - p[0]) + abs(g.MESH[s][1] - p[1])


def home(a):
    return ((BASE + a) >> 6) & 31


def msh(a):
    return ((BASE + a) >> 6) & 7


# ---------------- timer ----------------
_, _, r = load("t_raw", raw=True)
t0, t1 = r[0::4], r[1::4]
raw = collections.Counter(((b - a) % 2**32) for a, b in zip(t0, t1))
res = {}
for W in (10, 11, 12):
    fix = lambda v, W=W: v + 128 if (v & 0x7F) < W else v  # noqa: E731
    res[W] = collections.Counter((fix(b) - fix(a)) % 2**32 for a, b in zip(t0, t1))
OUT["timer"] = {"pairs": len(t0), "raw": {str(k if k < 2**31 else k - 2**32): n for k, n in raw.most_common()},
                "fixed_window_10": dict(res[10].most_common(4)), "fixed_window_11": dict(res[11].most_common(4)),
                "fixed_window_12": dict(res[12].most_common(4)),
                "expected_frac_each_sign": 10 / 128}
_, labs, r = load("t_glitch", raw=True)
tn = [v for l, v in zip(labs, r) if l[0] == "n"]
c = collections.Counter(v if v < 2**31 else v - 2**32 for v in tn)
OUT["timer"]["tnop_corrected_kernel"] = dict(c.most_common(6))
OUT["timer"]["tnop_off_by_128"] = sum(n for k, n in c.items() if k in (138, -118))
# does the in-kernel miss depend on anything? show the low bits of the stamps before glitch nops
ts = [v for l, v in zip(labs, r) if l[0] == "s"]
OUT["timer"]["tnop_n"] = len(tn)

# ---------------- ladder ----------------
m, labs, r = load("ladder")
grp = collections.defaultdict(list)
for l, v in zip(labs, r):
    grp[(l[0], l[2] if len(l) > 2 else None)].append((v, l))
lad = {}
for k, xs in grp.items():
    v = [x for x, _ in xs]
    lad[f"{k[0]}:{k[1]}"] = {"n": len(v), "min": min(v), "p10": q(v, .1), "med": q(v, .5), "p90": q(v, .9), "max": max(v),
                             "n_glitch(<-50 or <0)": sum(1 for x in v if x < 0)}
OUT["ladder"] = lad
# tnop and stamp raw (timer overhead): raw tnop reading
_, labsr, rr = load("ladder", raw=True)
OUT["ladder_tnop_raw"] = dict(collections.Counter(v for l, v in zip(labsr, rr) if l[0] == "tnop").most_common(4))
OUT["ladder_L1_raw"] = dict(collections.Counter(v for l, v in zip(labsr, rr) if l[0] == "ladder" and l[2] == 0).most_common(4))
OUT["ladder_noevict_raw"] = dict(collections.Counter(v for l, v in zip(labsr, rr) if l[0] == "ladder" and l[2] == -1).most_common(4))

# ---------------- decomp: L3 ----------------
m, labs, r = load("decomp")
d = collections.defaultdict(lambda: collections.defaultdict(list))
for l, v in zip(labs, r):
    d[l[1]][l[0]].append((l[2], v))
l3med = {}
l3_resid = []
for a, x in d.items():
    v = [y for _, y in x["l3"] if y > 0]
    l3med[a] = st.median(v)
    l3_resid.append(l3med[a] - (110 + 12 * hops(REQ, home(a))))
OUT["l3"] = {"lines": len(l3med), "within4": sum(1 for e in l3_resid if abs(e) <= 4),
             "within2": sum(1 for e in l3_resid if abs(e) <= 2),
             "resid_hist": dict(sorted(collections.Counter(round(e) for e in l3_resid).items()))}
# least-squares fit of line medians against hops
xs = [hops(REQ, home(a)) for a in l3med]
ys = [l3med[a] for a in l3med]
n = len(xs)
mx, my = st.mean(xs), st.mean(ys)
sxx = sum((x - mx) ** 2 for x in xs)
b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
a0 = my - b * mx
res_ = [y - a0 - b * x for x, y in zip(xs, ys)]
# robust: drop |res| > 10 (glitches) and refit
keep = [(x, y) for x, y, e in zip(xs, ys, res_) if abs(e) < 10]
xs2, ys2 = zip(*keep)
mx2, my2 = st.mean(xs2), st.mean(ys2)
sxx2 = sum((x - mx2) ** 2 for x in xs2)
b2 = sum((x - mx2) * (y - my2) for x, y in zip(xs2, ys2)) / sxx2
a2 = my2 - b2 * mx2
s2 = math.sqrt(sum((y - a2 - b2 * x) ** 2 for x, y in zip(xs2, ys2)) / (len(xs2) - 2))
OUT["l3"]["fit"] = {"slope": b2, "intercept": a2, "slope_se": s2 / math.sqrt(sxx2), "resid_sd": s2, "n": len(xs2),
                    "note": "lines are separate addresses in one process; se is within-session, not a repeat-level interval"}
# per home shire medians (the chart)
byh = collections.defaultdict(list)
for a, v in l3med.items():
    byh[home(a)].append(v)
OUT["l3"]["by_home"] = {h: {"hops": hops(REQ, h), "med": st.median(v), "n": len(v), "model": 110 + 12 * hops(REQ, h)}
                        for h, v in sorted(byh.items())}
# per-rep: is the L3 result the same in each of the three reps (a within-process repeat)?
per_rep = {}
for rep in range(3):
    e = []
    for a, x in d.items():
        v = [y for rp, y in x["l3"] if rp == rep and y > 0]
        if v:
            e.append(v[0] - (110 + 12 * hops(REQ, home(a))))
    per_rep[rep] = {"median_resid": st.median(e), "within4": sum(1 for z in e if abs(z) <= 4), "n": len(e)}
OUT["l3"]["per_rep"] = per_rep

# L2 bimodality
l2 = [y for x in d.values() for _, y in x["l2"] if y > 0]
OUT["l2"] = {"hist": dict(collections.Counter(l2).most_common(6)), "n": len(l2)}
# is the 37-cycle L2 hit tied to rep or address bits?
l2rep = collections.defaultdict(collections.Counter)
for a, x in d.items():
    for rp, y in x["l2"]:
        l2rep[rp][37 if y <= 40 else (48 if 44 <= y <= 52 else "other")] += 1
OUT["l2"]["by_rep"] = {k: dict(v) for k, v in l2rep.items()}

# ---------------- l3map (8,192 consecutive lines, separate process) ----------------
m, labs, r = load("l3map")
l3m = [(l[1], v) for l, v in zip(labs, r) if l[0] == "l3"]
e = [v - (110 + 12 * hops(REQ, home(a))) for a, v in l3m]
OUT["l3map"] = {"n": len(e), "within4": sum(1 for z in e if abs(z) <= 4), "5to6_above": sum(1 for z in e if 5 <= z <= 6),
                "glitch_<-100": sum(1 for z in e if z < -100), "other": sum(1 for z in e if not (abs(z) <= 4 or 5 <= z <= 6 or z < -100)),
                "median_resid": st.median(e)}
l2m = [v for l, v in zip(labs, r) if l[0] == "l2"]
OUT["l3map"]["l2_hist"] = dict(collections.Counter(l2m).most_common(6))
# L2 37-cycle hits by line index within 8-line group (the read buffer story)
cnt = collections.defaultdict(collections.Counter)
for l, v in zip(labs, r):
    if l[0] == "l2":
        idx = (l[1] // 64)
        cnt[idx % 8][37 if v <= 40 else 48 if 44 <= v <= 52 else "o"] += 1
OUT["l3map"]["l2_by_line_mod8"] = {k: dict(v) for k, v in sorted(cnt.items())}

# ---------------- decomp: memory-shire leg fit ----------------
res = collections.defaultdict(list)
mem = []
for a, x in d.items():
    for rp, v in x["mem"]:
        if v > 0:
            res[(msh(a), home(a))].append(v - l3med[a])
            mem.append(v)
OUT["dram"] = {"n_loads": len(mem), "median": q(mem, .5), "median_ns": q(mem, .5) / 0.6,
               "p10": q(mem, .1), "p90": q(mem, .9)}
p10 = {k: q(v, .1) for k, v in res.items()}
edge = [(x, y) for x in range(-1, 7) for y in range(-1, 7) if x in (-1, 6) or y in (-1, 6)]
edge2 = [(x, y) for x in range(-2, 8) for y in range(-2, 8) if x in (-2, 7) or y in (-2, 7)]


def fit(edges, crange):
    best = None
    for c in crange:
        tot, pos, ties = 0, {}, {}
        for ms in range(8):
            items = [(s, v) for (m_, s), v in p10.items() if m_ == ms]
            errs = sorted((sum((v - c - 12 * dist(s, p)) ** 2 for s, v in items), p) for p in edges)
            tot += errs[0][0]
            pos[ms] = errs[0][1]
            ties[ms] = [p for e_, p in errs if e_ == errs[0][0]]
        if best is None or tot < best[0]:
            best = (tot, c, pos, ties)
    return best


b1 = fit(edge, range(30, 120))
b2_ = fit(edge2, range(30, 120))
OUT["ms_fit"] = {"const": b1[1], "sqerr": b1[0], "pos": b1[2], "ties": {k: v for k, v in b1[3].items() if len(v) > 1},
                 "one_hop_further": {"const": b2_[1], "sqerr": b2_[0], "pos": b2_[2]}}
# second-best total with the constant fixed: how much worse is the best alternative position for each ms?
alt = {}
c = b1[1]
for ms in range(8):
    items = [(s, v) for (m_, s), v in p10.items() if m_ == ms]
    errs = sorted((sum((v - c - 12 * dist(s, p)) ** 2 for s, v in items), p) for p in edge)
    alt[ms] = {"best": errs[0], "second": errs[1], "homes": sorted(s for s, _ in items)}
OUT["ms_fit"]["alternatives"] = alt
# null model: the leg does not depend on the home shire (a constant per memory shire)
sse_null = 0
for ms in range(8):
    v = [val for (m_, s), val in p10.items() if m_ == ms]
    mu = st.mean(v)
    sse_null += sum((x - mu) ** 2 for x in v)
OUT["ms_fit"]["null_const_per_ms_sse"] = sse_null
# alternative: request goes requester -> memory shire directly (leg depends on hops(0, ms) not home->ms): per ms constant
# absorbs it, so its SSE equals the null's. Report the within-ms spread of the leg.
OUT["ms_fit"]["within_ms_leg_p10"] = {ms: sorted((s, p10[(ms, s)]) for (m_, s) in p10 if m_ == ms) for ms in range(8)}
pos = b1[2]
const = b1[1]
if ARGS.fixed_model:
    const = 91
    pos = {0: (1, -1), 1: (2, -1), 2: (3, -1), 3: (4, -1), 4: (1, 6), 5: (2, 6), 6: (3, 6), 7: (4, 6)}
OUT["model_used"] = {"const": const, "pos": pos, "fixed": ARGS.fixed_model, "requester": REQ}
model = lambda a: 110 + 12 * hops(REQ, home(a)) + const + 12 * dist(home(a), pos[msh(a)])  # noqa: E731
err_line = [min(v for _, v in x["mem"]) - model(a) for a, x in d.items()]
OUT["model"] = {"lines": len(err_line), "within3": sum(1 for e in err_line if abs(e) <= 3),
                "within5": sum(1 for e in err_line if abs(e) <= 5),
                "outliers_gt6": sorted(e for e in err_line if abs(e) > 6),
                "single_loads_within3": sum(1 for a, x in d.items() for _, v in x["mem"] if abs(v - model(a)) <= 3),
                "single_loads": sum(len(x["mem"]) for x in d.values()),
                "hist": dict(sorted(collections.Counter(err_line).items()))}
# per rep (within one process): model error of each rep's single load
OUT["model"]["per_rep_within3"] = {rep: sum(1 for a, x in d.items() for rp, v in x["mem"] if rp == rep and abs(v - model(a)) <= 3) for rep in range(3)}
# per home: median fastest vs model
byh = collections.defaultdict(list)
for a, x in d.items():
    byh[home(a)].append(min(v for _, v in x["mem"]))
OUT["model"]["by_home_dev"] = {h: st.median(v) - (110 + 12 * hops(REQ, h) + const + 12 * dist(h, pos[h & 7])) for h, v in byh.items()}
OUT["model"]["home31"] = {"n": len(byh[31]), "fast_med": st.median(byh[31]),
                          "model": 110 + 12 * hops(REQ, 31) + const + 12 * dist(31, pos[7])}
OUT["model"]["home0"] = {"n": len(byh[0]), "fast_med": st.median(byh[0]),
                         "all_loads_med": st.median(v for a, x in d.items() if home(a) == 0 for _, v in x["mem"])}
legs = [12 * dist(h, pos[h & 7]) for h in range(32)]
OUT["model"]["ms_leg_span"] = [min(legs), max(legs)]
OUT["model"]["no_line_11_fast"] = sum(1 for e in err_line if -14 <= e <= -7)

# cross-validation: fit ms positions on reps 0, test on reps 1-2 (same process, different loads) and split lines
# into halves by address: fit on one half, predict the other.
import random
rng = random.Random(0)
lines = sorted(d)
rng.shuffle(lines)
half = set(lines[: len(lines) // 2])
res_h = collections.defaultdict(list)
for a in half:
    for rp, v in d[a]["mem"]:
        if v > 0:
            res_h[(msh(a), home(a))].append(v - l3med[a])
p10h = {k: q(v, .1) for k, v in res_h.items()}
bestH = None
for c_ in range(30, 120):
    tot, pp = 0, {}
    for ms in range(8):
        items = [(s, v) for (m_, s), v in p10h.items() if m_ == ms]
        e_, p_ = min((sum((v - c_ - 12 * dist(s, p)) ** 2 for s, v in items), p) for p in edge)
        tot += e_
        pp[ms] = p_
    if bestH is None or tot < bestH[0]:
        bestH = (tot, c_, pp)
cH, posH = bestH[1], bestH[2]
test = [min(v for _, v in d[a]["mem"]) - (110 + 12 * hops(REQ, home(a)) + cH + 12 * dist(home(a), posH[msh(a)])) for a in lines[len(lines) // 2:]]
OUT["model"]["holdout"] = {"fit_const": cH, "same_positions": posH == pos, "n_test": len(test),
                           "within3": sum(1 for e in test if abs(e) <= 3)}

# ---------------- ladder against the §4 model (out of sample: different lines) ----------------
lmodel = {}
for l, v in zip(labs_ := load("ladder")[1], load("ladder")[2]):
    pass
m, labs, r = load("ladder")
lad_mem = collections.defaultdict(list)
for l, v in zip(labs, r):
    if l[0] in ("ladder", "nofence", "nodelay") and len(l) > 2 and l[2] == 3 and v > -50:
        a = l[1]
        lad_mem[l[0]].append((v, v - model(a), msh(a), a))
OUT["ladder_model"] = {}
for k, xs in lad_mem.items():
    e = [x[1] for x in xs]
    OUT["ladder_model"][k] = {"n": len(e), "within6": sum(1 for z in e if abs(z) <= 6), "fast_le-6": sum(1 for z in e if z <= -6),
                              "above6": sum(1 for z in e if z > 6), "resid_med": st.median(e),
                              "fast_resid_range": [min((z for z in e if z <= -6), default=None), max((z for z in e if z <= -6), default=None)],
                              "fast_resid_med": st.median([z for z in e if z <= -6]) if any(z <= -6 for z in e) else None,
                              "min": min(x[0] for x in xs)}
    byms = collections.defaultdict(list)
    for v, z, ms, a in xs:
        byms[ms].append(z)
    OUT["ladder_model"][k]["by_ms"] = {ms: {"n": len(v), "resid_med": st.median(v), "slow_gt6": sum(1 for z in v if z > 6),
                                            "sign": sign_test([z for z in v if z > -6])}
                                       for ms, v in sorted(byms.items())}
# min of nodelay: its line and its closed-row time
xs = lad_mem["nodelay"]
mn = min(xs, key=lambda x: x[0])
OUT["ladder_model"]["nodelay_min_line"] = {"lat": mn[0], "model": model(mn[3])}
# the 256 loads after an evict: any at L3 time?
l3t = [x[0] - (110 + 12 * hops(REQ, home(x[3]))) for k in ("nofence", "nodelay") for x in lad_mem[k]]
OUT["ladder_model"]["after_evict_min_above_L3"] = min(l3t)
# ladder L3 and memory: spread explained by distance?
for lvl, name in ((2, "L3"), (3, "MEM")):
    vals = [(v, l[1]) for l, v in zip(labs, r) if l[0] == "ladder" and l[2] == lvl and v > -50]
    raw_sd = st.pstdev(v for v, _ in vals)
    if lvl == 2:
        rs = [v - (110 + 12 * hops(REQ, home(a))) for v, a in vals]
    else:
        rs = [v - model(a) for v, a in vals]
    rs_c = [z for z in rs if abs(z) < 60]
    OUT["ladder_model"][f"spread_{name}"] = {"raw_sd": raw_sd, "resid_sd_(|r|<60)": st.pstdev(rs_c), "n": len(vals),
                                             "within6": sum(1 for z in rs if abs(z) <= 6)}
# tevict / tfence
for k in ("tevict_clean", "tevict_dirty", "tfence"):
    v = [x for l, x in zip(labs, r) if l[0] == k]
    OUT["ladder_model"][k] = {"n": len(v), "min": min(v), "med": q(v, .5), "max": max(v), "le20": sum(1 for x in v if x <= 20)}

# ---------------- msmap ----------------
_, labs, r = load("msmap", raw=True)
vv = dict(zip(labs, r))
lines_ = sorted({l[1] for l in labs})
match, d16, d15, stray, other = 0, 0, 0, 0, collections.Counter()
for a in lines_:
    dd = [(vv[("after", a, ms)] - vv[("before", a, ms)]) % 2**32 for ms in range(8)]
    top = max(range(8), key=lambda i: dd[i])
    match += top == msh(a)
    d16 += dd[msh(a)] == 16
    d15 += dd[msh(a)] == 15
    for i in range(8):
        if i != msh(a):
            other[dd[i]] += 1
OUT["msmap"] = {"lines": len(lines_), "match": match, "rose16": d16, "rose15": d15, "others": dict(other)}

# ---------------- bits ----------------
m, labs, r = load("bits")
bd = collections.defaultdict(lambda: collections.defaultdict(dict))
for l, v in zip(labs, r):
    bd[l[1]][l[0]][l[2]] = v
bits = {}
for bb in sorted(bd):
    x = bd[bb]
    ab = [v for v in x["AB"].values() if v > 0]
    diffs = [x["B"][t] - x["B0"][t] for t in x["B"] if x["B"][t] > 0 and x["B0"].get(t, 0) > 0]
    ab_minus_a = [x["AB"][t] - x["A"][t] for t in x["AB"] if x["AB"][t] > 0 and x["A"].get(t, 0) > 0]
    bits[bb] = {"ab_med": q(ab, .5), "ab_p10": q(ab, .1), "ab_p90": q(ab, .9), "n": len(ab),
                "b_minus_b0_med": st.median(diffs), "n_diff": len(diffs), "b_minus_b0_sign": sign_test(diffs)}
OUT["bits"] = bits
low = [bits[b]["ab_med"] for b in range(6, 18)]
high = [bits[b]["ab_med"] for b in range(18, 30)]
OUT["bits_summary"] = {"ab_med_bits6_17_median": st.median(low), "ab_med_bits18_29_median": st.median(high),
                       "row_conflict_extra": st.median(high) - st.median(low),
                       "row_conflict_extra_range": [min(high) - st.median(low), max(high) - st.median(low)],
                       "seq_row_bits18_29": st.median(bits[b]["b_minus_b0_med"] for b in range(18, 30)),
                       "seq_col_bits13_17": st.median(bits[b]["b_minus_b0_med"] for b in range(13, 18)),
                       "seq_bank_bits6_12": {b: bits[b]["b_minus_b0_med"] for b in range(6, 13)},
                       "baseline_-1": bits[-1]["ab_med"]}
# per-trial pooled test: AB latency bits 18+ minus the same trial's AB for bits 13-17 (paired within trial t)
pair = []
for t in range(150):
    h = [bd[b]["AB"].get(t, 0) for b in range(18, 30)]
    lo = [bd[b]["AB"].get(t, 0) for b in range(13, 18)]
    h = [v for v in h if v > 0]
    lo = [v for v in lo if v > 0]
    if h and lo:
        pair.append(st.median(h) - st.median(lo))
OUT["bits_summary"]["trial_paired_row_minus_col"] = {"n": len(pair), "median": st.median(pair), "sign": sign_test(pair)}
pair_c, pair_r = [], []
for t in range(150):
    c_ = [bd[b]["B"][t] - bd[b]["B0"][t] for b in range(13, 18) if bd[b]["B"].get(t, 0) > 0 and bd[b]["B0"].get(t, 0) > 0]
    r_ = [bd[b]["B"][t] - bd[b]["B0"][t] for b in range(18, 30) if bd[b]["B"].get(t, 0) > 0 and bd[b]["B0"].get(t, 0) > 0]
    if c_:
        pair_c.append(st.median(c_))
    if r_:
        pair_r.append(st.median(r_))
OUT["bits_summary"]["seq_col_trial_medians"] = {"n": len(pair_c), "median": st.median(pair_c), "sign": sign_test(pair_c)}
OUT["bits_summary"]["seq_row_trial_medians"] = {"n": len(pair_r), "median": st.median(pair_r), "sign": sign_test(pair_r)}
bank = []
for t in range(150):
    k_ = [bd[b]["B"][t] - bd[b]["B0"][t] for b in range(6, 13) if bd[b]["B"].get(t, 0) > 0 and bd[b]["B0"].get(t, 0) > 0]
    if k_:
        bank.append(st.median(k_))
OUT["bits_summary"]["seq_bank_trial_medians"] = {"n": len(bank), "median": st.median(bank), "sign": sign_test(bank)}

# ---------------- refresh ----------------
_, labs, r = load("refresh_jit")
tsj = [v + OVH for v in r[0::2]]
lat = r[1::2]
tsj = [(t - tsj[0]) % 2**32 for t in tsj]
slow = [t for t, l_ in zip(tsj, lat) if l_ >= 260]
scores = []
for P in range(22000, 24500, 2):
    Pp = P / 10
    scores.append((max(collections.Counter(int((t % Pp) / Pp * 50) for t in slow).values()), Pp))
scores.sort(reverse=True)
OUT["refresh"] = {"n": len(lat), "best_period": scores[0][1], "top5": scores[:5],
                  "clock_if_tREFI_3.87us_MHz": scores[0][1] / 3.87, "hist": dict(sorted(collections.Counter(v // 5 * 5 for v in lat if 200 <= v < 240).items())),
                  "max": max(lat), "max_minus_226": max(lat) - 226, "in_refresh_ge240": sum(1 for v in lat if v >= 240) / len(lat)}
# half-split stability of the period (first and second half of the series)
for nm, sl in (("first_half", slice(0, len(tsj) // 2)), ("second_half", slice(len(tsj) // 2, None))):
    tt = [t for t, l_ in zip(tsj[sl], lat[sl]) if l_ >= 260]
    sc = max((max(collections.Counter(int((t % (P / 10)) / (P / 10) * 50) for t in tt).values()), P / 10) for P in range(22000, 24500, 2))
    OUT["refresh"][nm + "_period"] = sc[1]
# locked series
_, labs, r = load("refresh")
ts0 = [v + OVH for v in r[0::2]]
lat0 = r[1::2]
per = [(ts0[i + 1] - ts0[i]) % 2**32 for i in range(len(ts0) - 1)]
OUT["refresh_locked"] = {"n": len(lat0), "period_med": st.median(per), "period_hist": dict(collections.Counter(per).most_common(4)),
                         "lat_hist": dict(collections.Counter(lat0).most_common(8)), "max": max(lat0),
                         "frac_ge_220": sum(1 for v in lat0 if v >= 220) / len(lat0),
                         "op_cycles": st.median(per[i] - lat0[i] for i in range(len(per))) / 4}
# the slow every-fourth pattern
slow_idx = [i for i, v in enumerate(lat0) if 222 <= v <= 232]
gaps = collections.Counter(slow_idx[i + 1] - slow_idx[i] for i in range(len(slow_idx) - 1))
OUT["refresh_locked"]["slow_gap_hist"] = dict(gaps.most_common(4))
# the row-hit / closed values in the jitter series, outside refresh
OUT["refresh"]["open_closed_modes"] = dict(collections.Counter(v for v in lat if 205 <= v <= 235).most_common(6))

# row life, recomputed as in analyze.refresh with a sensitivity check on the refresh-start estimate
fold = collections.defaultdict(list)
period = scores[0][1]
for t, l_ in zip(tsj, lat):
    fold[int((t % period) / period * 50)].append(l_)
peak = max(fold, key=lambda k: q(fold[k], .9))
curve = [q(fold[(k + peak - 2) % 50], .9) for k in range(50)]
first = next(k for k in range(50) if curve[k] >= 260)
un, off = [], 0
for i, t in enumerate(tsj):
    if i and t + off < un[-1] - 2**31:
        off += 2**32
    un.append(t + off)


def rowlife(shift_bins=0):
    ref0 = ((peak - 2 + first + shift_bins) % 50) / 50 * period
    nref = lambda a, b: int((b - ref0) // period) - int((a - ref0) // period)  # noqa: E731
    life = collections.defaultdict(lambda: [0, 0, 0, 0])
    for i in range(1, len(un)):
        if not 150 <= lat[i] < 240:
            continue
        gap = un[i] - un[i - 1] - lat[i - 1]
        k = 2 if nref(un[i - 1], un[i]) else 0
        bb = life[int(gap // 250) * 250]
        bb[k] += lat[i] <= 220
        bb[k + 1] += 1
    return life


life = rowlife()
rows = [(g_, v) for g_, v in sorted(life.items())]
lt2000 = [v for g_, v in rows if g_ < 2000]
tot = [sum(v[i] for v in lt2000) for i in range(4)]
OUT["rowlife"] = {"no_refresh": [tot[0], tot[1]], "refresh": [tot[2], tot[3]],
                  "by_gap": {g_: {"hit_nr": v[0], "n_nr": v[1], "frac_nr": (v[0] / v[1] if v[1] else None),
                                  "hit_r": v[2], "n_r": v[3]} for g_, v in rows}}
for sh in (-1, 1):
    lf = rowlife(sh)
    lt = [v for g_, v in sorted(lf.items()) if g_ < 2000]
    OUT["rowlife"][f"shift{sh}"] = [sum(v[i] for v in lt) for i in range(4)]
# trend of hit rate (no refresh) against the gap: logistic-free check, compare 450-1000 vs 1000-2000
a_ = [v for g_, v in rows if 250 <= g_ < 1000]
b_ = [v for g_, v in rows if 1000 <= g_ < 1750]
ha, na = sum(v[0] for v in a_), sum(v[1] for v in a_)
hb, nb = sum(v[0] for v in b_), sum(v[1] for v in b_)
OUT["rowlife"]["short_vs_long_gap_no_refresh"] = {"250-1000": [ha, na, ha / na if na else None], "1000-1750": [hb, nb, hb / nb if nb else None]}

# ---------------- pagetimeout ----------------
m, labs, r = load("pagetimeout")
pt = collections.defaultdict(lambda: collections.defaultdict(dict))
for l, v in zip(labs, r):
    pt[l[1]][l[0]][l[2]] = v
P = period
ovh = 2 * OUT["refresh_locked"]["op_cycles"]
inr = OUT["refresh"]["in_refresh_ge240"]
rows = []
z_sum, var_sum = 0, 0
for dly in sorted(pt):
    A, B = pt[dly]["A"], pt[dly]["B"]
    prs = [t for t in B if A[t] > 150 and B[t] > 150]
    diff = [B[t] - A[t] for t in prs]
    hits = sum(1 for x in diff if -16 <= x <= -7)
    pred = st.mean(max(0, 1 - (A[t] + OVH + ovh + dly + inr * P) / P) for t in prs)
    pbin = binom_two_sided(hits, len(prs), pred) if 0 < pred < 1 else None
    rows.append({"delay": dly, "hits": hits, "n": len(prs), "meas": hits / len(prs), "pred": pred, "p_binom": pbin})
    if 0 < pred < 1:
        z_sum += hits - len(prs) * pred
        var_sum += len(prs) * pred * (1 - pred)
OUT["pagetimeout"] = {"rows": rows, "pooled_obs_minus_exp": z_sum, "pooled_z": z_sum / math.sqrt(var_sum),
                      "late_hits": [sum(x["hits"] for x in rows if x["delay"] >= 3000), sum(x["n"] for x in rows if x["delay"] >= 3000)]}

print(json.dumps(OUT, indent=1, default=str))
