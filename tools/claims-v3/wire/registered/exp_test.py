"""Pre-registered tests for the heat-per-mm experiments (written 2026-09-25, before any run).

    python3 exp_test.py exp1 A2_DIR A3_DIR      # run_wire.py --set v2 subset (wu p0/p0.5/p1, wsep p0/p0.5 d1-4), 6 passes
    python3 exp_test.py exp2 A2_DIR A3_DIR      # OPTIONAL, not in the plan: run_wire.py --set v1 subset (walt, wbern p0/p0.5/p1 at d 0,1,3,6, waxis x/y d1-2)

Each burst is reduced by the pipeline's own analyze_wire.bursts() (board power leakage-corrected over idle brackets,
mesh rail over the last 0.6 s; dropped if the clock left 600 MHz or the sampler starved). The unit of replication is
the pass; per card the statistic is computed per pass and a 99% t-interval (df = passes - 1) is formed. A test PASSES
when the interval excludes the null on EACH card and the per-card mean lies inside the predicted range; SIGN-ONLY when
the interval excludes the null on each card but a mean is outside the range (the page then states the new per-card
values); FAIL otherwise. Only the new data are used; nothing is pooled with E31/E32.
"""
import json, math, os, sys, collections
import numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_wire as aw
import tdist
NK, BK = "noc_pj_per_byte", "pj_per_byte"
fj = lambda pj: pj / 8 * 1000
L = 3.72

def load(d):
    h, bs, dr = aw.bursts(d)
    ix = collections.defaultdict(dict)
    for b in bs: ix[b["pass"]][b["cfg"]] = b
    return h, ix, dr

def line(xs, ys):
    A = np.vstack([np.asarray(xs, float), np.ones(len(xs))]).T
    c, *_ = np.linalg.lstsq(A, np.asarray(ys, float), rcond=None); return float(c[0]), float(c[1])

def v(ix, p, cfg, key):
    b = ix[p].get(cfg); return None if b is None else b[key]

def sl(ix, p, pre, key, hops):
    pts = [(d, v(ix, p, f"{pre}{d}", key)) for d in hops]; pts = [q for q in pts if q[1] is not None]
    return line([q[0] for q in pts], [q[1] for q in pts]) if len(pts) >= 3 else None

def ci(vals):
    x = np.array([q for q in vals if q is not None], float); n = len(x)
    if n < 2: return {"n": n}
    m, se = float(x.mean()), float(x.std(ddof=1) / math.sqrt(n)); t = tdist.ppf(0.995, n - 1)
    return {"n": n, "mean": m, "lo99": m - t * se, "hi99": m + t * se, "vals": [round(float(q), 4) for q in x]}

D6, D14 = (1, 2, 3, 4, 6), (1, 2, 3, 4)
def dpart(ix, p, fam, key, hops=D14): return fj(sl(ix,p,f"{fam}/p0.5/hop",key,hops)[0] - sl(ix,p,f"{fam}/p0/hop",key,hops)[0])
def zpart(ix, p, fam, key, hops=D14): return fj(sl(ix,p,f"{fam}/p0/hop",key,hops)[0])
def off4(ix, p, pre, key):
    s, i = sl(ix, p, pre, key, (1, 2, 3, 6)); l4 = 4 * s + i; return (v(ix, p, f"{pre}4", key) - l4) / l4

EXP1 = [  # (id, claims, statistic, null, predicted range [lo, hi])
    ("P1", "heat-43", "mesh rail: wu - wsep data part over d=1-4, fJ/bit/hop", lambda ix,p: dpart(ix,p,"wu",NK)-dpart(ix,p,"wsep",NK), 0, (16, 40)),
    ("P2", "heat-43", "mesh rail: wu - wsep zeros slope over d=1-4, fJ/bit/hop", lambda ix,p: zpart(ix,p,"wu",NK)-zpart(ix,p,"wsep",NK), 0, (23, 43)),
    ("P3", "heat-32", "board: wsep data part over d=1-4, fJ/bit/hop", lambda ix,p: dpart(ix,p,"wsep",BK), 0, (75, 165)),
    ("P4", "heat-32", "board: wsep zeros slope over d=1-4, fJ/bit/hop", lambda ix,p: zpart(ix,p,"wsep",BK), 0, (22, 82)),
    ("P5a", "heat-48", "board: wu - wsep data part over d=1-4, fJ/bit/hop", lambda ix,p: dpart(ix,p,"wu",BK)-dpart(ix,p,"wsep",BK), 0, (24, 104)),
    ("P5b", "heat-48", "board: wu - wsep zeros slope over d=1-4, fJ/bit/hop", lambda ix,p: zpart(ix,p,"wu",BK)-zpart(ix,p,"wsep",BK), 0, (16, 86)),
    ("P6a", "heat-05b", "mesh rail: slope(all ones)/slope(random) - 1 over d=1-6", lambda ix,p: sl(ix,p,"wu/p1/hop",NK,D6)[0]/sl(ix,p,"wu/p0.5/hop",NK,D6)[0]-1, 0, (0.045, 0.125)),
    ("P6b", "heat-05b", "board: slope(all ones)/slope(random) - 1 over d=1-6", lambda ix,p: sl(ix,p,"wu/p1/hop",BK,D6)[0]/sl(ix,p,"wu/p0.5/hop",BK,D6)[0]-1, 0, (0.02, 0.12)),
    ("P7a", "heat-21a", "mesh rail: random, d=4 above the line through 1,2,3,6", lambda ix,p: off4(ix,p,"wu/p0.5/hop",NK), 0, (0.03, 0.09)),
    ("P7b", "heat-21a", "mesh rail: zeros, d=4 above the line", lambda ix,p: off4(ix,p,"wu/p0/hop",NK), 0, (0.035, 0.095)),
    ("P7c", "heat-21a", "mesh rail: all ones, d=4 above the line", lambda ix,p: off4(ix,p,"wu/p1/hop",NK), 0, (0.11, 0.19)),
    ("P7d", "heat-21a", "board: all ones, d=4 above the line", lambda ix,p: off4(ix,p,"wu/p1/hop",BK), 0, (0.07, 0.17)),
    ("P7e", "heat-21b", "board: random, d=4 above the line", lambda ix,p: off4(ix,p,"wu/p0.5/hop",BK), 0, (0.015, 0.075)),
    ("P7f", "heat-21b", "board: zeros, d=4 above the line", lambda ix,p: off4(ix,p,"wu/p0/hop",BK), 0, (-0.005, 0.055)),
    ("P8", "heat-23", "mesh rail: exit step, random, in hops (intercept over 1-6 less d=0, over slope)", lambda ix,p: (lambda s: (s[1]-v(ix,p,"wu/p0.5/hop0",NK))/s[0])(sl(ix,p,"wu/p0.5/hop",NK,D6)), 0, (0.35, 0.75)),
    ("P9", "heat-23", "board: exit step, random, in hops", lambda ix,p: (lambda s: (s[1]-v(ix,p,"wu/p0.5/hop0",BK))/s[0])(sl(ix,p,"wu/p0.5/hop",BK,D6)), 0, (0.7, 1.5)),
    ("P10", "heat-19", "mesh rail: data part at d=0 over its d=1 value", lambda ix,p: (v(ix,p,"wu/p0.5/hop0",NK)-v(ix,p,"wu/p0/hop0",NK))/(v(ix,p,"wu/p0.5/hop1",NK)-v(ix,p,"wu/p0/hop1",NK)), None, (-0.04, 0.04)),
    ("P11a", "heat-01", "mesh rail: free-link random bit, everything, fJ/mm", lambda ix,p: fj(sl(ix,p,"wsep/p0.5/hop",NK,D14)[0])/L, 0, (33, 39.5)),
    ("P11b", "heat-02", "board: free-link random bit, everything, fJ/mm", lambda ix,p: fj(sl(ix,p,"wsep/p0.5/hop",BK,D14)[0])/L, 0, (35, 58)),
    ("P12", "heat-06", "mesh rail: 1 - E(all ones, d=1)/E(random, d=1)", lambda ix,p: 1-v(ix,p,"wu/p1/hop1",NK)/v(ix,p,"wu/p0.5/hop1",NK), 0, (0.31, 0.41)),
    ("P13", "heat-75", "board: per-second bound on the link-disjoint fixed part (descriptive)", None, None, None),
]

def alt_mean(ix, p, key, sizes=(16, 64, 128)): return float(np.mean([sl(ix,p,f"walt/n{n}/hop",key,(1,3,6))[0] for n in sizes]))
def x_y(ix, p, key):
    g = lambda ax: (v(ix,p,f"waxis/{ax}/hop2/p0.5",key)-v(ix,p,f"waxis/{ax}/hop2/p0",key))-(v(ix,p,f"waxis/{ax}/hop1/p0.5",key)-v(ix,p,f"waxis/{ax}/hop1/p0",key))
    return 1 - g("y") / g("x")
def a_v1(ix, p, key):   # transition coefficient from P = 0, 1/2, 1 at d = 1, 3, 6 (t = 0, 1/2, 0; ones 0, 1/2, 1): a = 2*(s(1/2) - (s(0)+s(1))/2)
    s = {q: sl(ix,p,f"wbern/p{q}/hop",key,(1,3,6))[0] for q in ("0","0.5","1")}
    return 2 * (s["0.5"] - 0.5 * (s["0"] + s["1"]))
EXP2 = [
    # revised 2026-09-25 (still before any run): like for like over d = 1,3,6 the existing data put the blocks within 1% of
    # the no-transition reference, so this is an equivalence test (the page's "3-6% below" compared hop sets 1,3,6 vs 1-6)
    ("Q1a", "heat-29", "mesh rail: 16-128 B blocks against (s(0)+s(1))/2 over d=1,3,6 (equivalence: 99% CI inside +-5%)", lambda ix,p: 1-alt_mean(ix,p,NK)/(0.5*(sl(ix,p,"wbern/p0/hop",NK,(1,3,6))[0]+sl(ix,p,"wbern/p1/hop",NK,(1,3,6))[0])), None, (-0.05, 0.05)),
    ("Q1b", "heat-29", "board: the same (equivalence: inside +-15%)", lambda ix,p: 1-alt_mean(ix,p,BK)/(0.5*(sl(ix,p,"wbern/p0/hop",BK,(1,3,6))[0]+sl(ix,p,"wbern/p1/hop",BK,(1,3,6))[0])), None, (-0.15, 0.15)),
    ("Q2a", "heat-61", "mesh rail: 256 B excess slope over 16-128 B, pJ/B/hop", lambda ix,p: sl(ix,p,"walt/n256/hop",NK,(1,3,6))[0]-alt_mean(ix,p,NK), 0, (0.33, 0.49)),
    ("Q2b", "heat-61", "board: 256 B excess slope, pJ/B/hop", lambda ix,p: sl(ix,p,"walt/n256/hop",BK,(1,3,6))[0]-alt_mean(ix,p,BK), 0, (0.5, 1.0)),
    ("Q3", "heat-60/63", "mesh rail: 16 B minus 64 B blocks slope, pJ/B/hop (equivalence: 99% CI inside +-0.1)", lambda ix,p: sl(ix,p,"walt/n16/hop",NK,(1,3,6))[0]-sl(ix,p,"walt/n64/hop",NK,(1,3,6))[0], None, (-0.1, 0.1)),
    ("Q4", "heat-64", "mesh rail: 256 B excess as a fraction of a full flip (a from P = 0, 1/2, 1)", lambda ix,p: (sl(ix,p,"walt/n256/hop",NK,(1,3,6))[0]-alt_mean(ix,p,NK))/a_v1(ix,p,NK), 1, (0.40, 0.70)),
    ("Q5", "heat-69", "mesh rail: y-only below x-only, data part increment d=1->2", lambda ix,p: x_y(ix,p,NK), 0, (0.03, 0.19)),
]

def run(exp, dirs):
    tests = EXP1 if exp == "exp1" else EXP2
    cards = {}
    for d in dirs:
        h, ix, dr = load(d); cards[h] = (ix, dr)
        print(f"{h}: {sum(len(x) for x in ix.values())} bursts kept over {len(ix)} passes, {len(dr)} dropped")
    res = {}
    for tid, claim, what, fn, null, rng in tests:
        if fn is None:
            continue
        per = {}
        for h, (ix, _) in cards.items():
            vals = []
            for p in sorted(ix):
                try: vals.append(fn(ix, p))
                except (TypeError, KeyError, ZeroDivisionError): pass
            per[h] = ci(vals)
        excl = all(c.get("n", 0) >= 3 and (null is None or c["lo99"] > null or c["hi99"] < null) for c in per.values())
        if null is None:   # equivalence: the whole interval must sit inside the range
            verdict = "PASS" if all(c.get("n", 0) >= 3 and rng[0] <= c["lo99"] and c["hi99"] <= rng[1] for c in per.values()) else "FAIL"
        else:
            inr = all(rng[0] <= c["mean"] <= rng[1] for c in per.values() if "mean" in c)
            verdict = "PASS" if excl and inr else ("SIGN-ONLY" if excl else "FAIL")
        res[tid] = {"claim": claim, "what": what, "null": null, "predicted": rng, "per_card": per, "verdict": verdict}
        print(f"{tid:5s} {verdict:9s} {what}: " + " | ".join(f"{h[-1]}: {c.get('mean', float('nan')):.4g} [{c.get('lo99', float('nan')):.4g}, {c.get('hi99', float('nan')):.4g}] n{c.get('n')}" for h, c in per.items()) + f"  predicted {rng}")
    return res

if __name__ == "__main__":
    exp, dirs = sys.argv[1], sys.argv[2:]
    out = run(exp, dirs)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{exp}_result.json"), "w"), indent=1)
