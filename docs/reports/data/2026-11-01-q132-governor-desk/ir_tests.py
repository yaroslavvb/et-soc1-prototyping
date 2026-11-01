#!/usr/bin/env python3
"""Q132(g), item 10: the hits against the boundaries that were not hit, on every simple hypothesis the brief names. POST HOC, desk only, no card.

The population is every kernel boundary at which the clock could visibly fall: the kernel before ran at 800 MHz (mean clock 0.79 GHz or more). A
hit is a fall to 600 MHz right after that boundary (ir_hits.py, both rules). For a covariate the question is whether hits fall on one part of the
population more than its share. Monte Carlo over the hits' placement among the boundaries (multinomial with the exposure shares), 20,000 draws,
seed fixed. No correction for trying several covariates: all are reported.

    ir_tests.py <repo> <ir-hits.json> [--out ir-tests.json] > ir-tests.txt
"""
import argparse
import bisect
import json
import math
import os
import random
import statistics as st
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ir_lib as L

os.environ["TZ"] = "America/Los_Angeles"
time.tzset()
WINDOW_MS = 2.0     # the width of the zone the boundaries fall in (ir-lattice.txt)
HB_MS = 1000.01     # the lattice's period on the host clock


def table(rows, keyf, name, cats=None):
    """rows: boundary dicts with 'hit'. keyf gives a category."""
    exp, hit = {}, {}
    for r in rows:
        k = keyf(r)
        if k is None:
            continue
        exp[k] = exp.get(k, 0) + 1
        hit[k] = hit.get(k, 0) + (1 if r["hit"] else 0)
    keys = cats or sorted(exp)
    N, H = sum(exp.values()), sum(hit.values())
    shares = [exp.get(k, 0) / N for k in keys]
    stat0 = sum((hit.get(k, 0) - H * s) ** 2 / (H * s) for k, s in zip(keys, shares) if s > 0)
    rng = random.Random(132)
    ge = 0
    M = 20000
    for _ in range(M):
        c = [0] * len(keys)
        for k in rng.choices(range(len(keys)), weights=shares, k=H):
            c[k] += 1
        st_ = sum((c[i] - H * s) ** 2 / (H * s) for i, s in enumerate(shares) if s > 0)
        if st_ >= stat0 - 1e-12:
            ge += 1
    p = ge / M
    print(f"{name}: hits {H} of {N} boundaries; Monte Carlo p {p:.3f}")
    for k in keys:
        e = exp.get(k, 0)
        print(f"    {str(k):24s} boundaries {e:6d}  hits {hit.get(k, 0):3d}  rate {100 * hit.get(k, 0) / e if e else 0:.2f}%   expected {H * e / N:.1f}")
    return {"name": name, "p": p, "hits": H, "boundaries": N, "rows": {str(k): {"boundaries": exp.get(k, 0), "hits": hit.get(k, 0)} for k in keys}}


def tert(vals):
    v = sorted(vals)
    return v[len(v) // 3], v[2 * len(v) // 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("hits")
    ap.add_argument("--out")
    a = ap.parse_args()
    H = json.load(open(a.hits))["hits"]
    clean = [h for h in H if h.get("x_ms") is not None and -40 <= h["x_ms"] < 40 and h.get("prev_g") and h["prev_g"] >= 0.79]
    print(f"hits: {len(clean)} (flagged {len(H)}; left out: {[(h['exp'], h['run'][:28], h.get('x_ms'), h.get('prev_g')) for h in H if h not in clean]})")
    keyset = {(h["exp"], h["run"], h["proc"], h["kernel"]) for h in clean}
    rows = []
    sess = {}
    durations = []
    for exp, (box, card, dirs) in L.SESSIONS.items():
        rr = []
        for rel in dirs:
            rr += L.load_rundir(a.repo, rel)["runs"]
        if not rr:
            continue
        t_all = [p["t0"] for r in rr for p in r["procs"]] + [p["t1"] for r in rr for p in r["procs"]]
        s0, s1 = min(t_all), max(t_all)
        work_800 = 0.0
        for r in rr:
            T = r["tel"]
            times = [x[0] for x in T]
            for pr in r["procs"]:
                ks = pr["kernels"]
                for j in range(1, len(ks)):
                    g0 = L.g_eff(ks[j - 1])
                    if g0 is None or g0 < 0.79 or ks[j - 1].get("launch", -1) < 0:
                        continue
                    work_800 += ks[j - 1]["wall_s"]
                    t0 = ks[j]["t_start_ms"]
                    i = bisect.bisect_left(times, t0)
                    near = T[max(0, min(i, len(T) - 1))] if T else None
                    hit = (exp, r["run"], pr["proc"], ks[j].get("launch")) in keyset
                    fmt = (r.get("type") or "?")
                    rows.append({"exp": exp, "box": box, "t0": t0, "since_s": (t0 - pr["t0"]) / 1000.0, "frac": (t0 - s0) / max(1, s1 - s0),
                                 "die": near[1] if near else None, "w": near[3] if near else None, "fmt": fmt, "block": "".join(c for c in (r.get("block") or "?") if c.isalpha()),
                                 "hour": time.localtime(t0 / 1000.0).tm_hour, "kernel_wall": ks[j - 1]["wall_s"], "gap": t0 - ks[j - 1]["t_end_ms"], "hit": hit})
                    if hit and T:
                        # durations: first 600 reading after t0, first 700+ after it, first 800 after it
                        S = [x for x in T if x[0] >= t0 - 150 and x[0] <= pr["t1"] and x[4] is not None]
                        i6 = next((n for n, x in enumerate(S) if x[4] == 600), None)
                        if i6 is not None:
                            t6 = S[i6][0]
                            t7 = next((x[0] for x in S[i6:] if x[4] >= 700), None)
                            t8 = next((x[0] for x in S[i6:] if x[4] == 800), None)
                            durations.append({"exp": exp, "run": r["run"], "at600_s": (t7 - t6) / 1000.0 if t7 else None, "to800_s": (t8 - t6) / 1000.0 if t8 else None,
                                              "w_before": S[max(0, i6 - 1)][3], "w_in": S[min(len(S) - 1, i6 + 5)][3], "took_ms": S[i6][5], "took_before": S[max(0, i6 - 1)][5]})
        hs = [h for h in clean if h["exp"] == exp]
        exposed = sum(1 for x in rows if x["exp"] == exp)
        sess[exp] = {"box": box, "exposed": exposed, "hits": len(hs), "expected_at_window": round(exposed * WINDOW_MS / HB_MS, 1), "work_800_s": round(work_800, 1),
                     "per_heartbeat_pct": round(100.0 * len(hs) / work_800, 3) if work_800 else None}
    print("\nRates and the expectation from a 2 ms window on a 1 s heartbeat (exposed boundaries x 2 ms / 1000.01 ms)")
    print("session box         exposed  hits  expected  95% interval of the count   seconds at 800 MHz between kernels  hits per heartbeat")
    th, te = 0, 0.0
    for e, s in sess.items():
        lo, hi = L.poisson_ci(s["hits"])
        th += s["hits"]
        te += s["expected_at_window"]
        print(f"{e:7s} {s['box']:11s} {s['exposed']:7d} {s['hits']:5d} {s['expected_at_window']:9.1f}   {lo:5.1f}-{hi:5.1f}                  {s['work_800_s']:8.1f}   {s['per_heartbeat_pct']}%")
    lo, hi = L.poisson_ci(th)
    print(f"all                 {sum(s['exposed'] for s in sess.values()):7d} {th:5d} {te:9.1f}   {lo:5.1f}-{hi:5.1f}")
    out = {"sessions": sess, "tests": {}, "total_hits": th, "total_expected": round(te, 1)}
    print("\nEvery boundary's host gap (start stamp minus previous end stamp, ms) over the population, and at the hits:")
    g_all = [r["gap"] for r in rows]
    g_hit = [r["gap"] for r in rows if r["hit"]]
    print("   population: mean", round(st.mean(g_all), 3), "max", max(g_all), "| hits: mean", round(st.mean(g_hit), 3), "max", max(g_hit))
    out["gap"] = {"all_mean": round(st.mean(g_all), 3), "hit_mean": round(st.mean(g_hit), 3)}
    print("\nCovariates over the population")
    def bins(field, edges):
        def f(r):
            x = r.get(field)
            if x is None:
                return None
            for lo_, hi_ in zip(edges[:-1], edges[1:]):
                if lo_ <= x < hi_:
                    return f"{lo_}-{hi_}"
            return None
        return f, [f"{lo_}-{hi_}" for lo_, hi_ in zip(edges[:-1], edges[1:])]
    a2 = [r for r in rows]
    k, c = bins("since_s", [0, 1.5, 3, 5, 7, 9.5])
    out["tests"]["since_launch"] = table(a2, k, "time since the process started, s", c)
    k, c = bins("frac", [0, 0.25, 0.5, 0.75, 1.01])
    out["tests"]["session_position"] = table(a2, k, "position in the session (fraction)", c)
    k, c = bins("die", [40, 56, 58, 60, 62, 64, 70])
    out["tests"]["die"] = table(a2, k, "die at the boundary, C", c)
    k, c = bins("w", [20, 36, 40, 45, 50, 55, 62, 100])
    out["tests"]["power"] = table(a2, k, "board W at the boundary", c)
    out["tests"]["format"] = table(a2, lambda r: r["fmt"], "number format")
    out["tests"]["block"] = table(a2, lambda r: r["block"], "block (BURST, SUS, HOT...)")
    out["tests"]["session"] = table(a2, lambda r: r["exp"], "session (and so date and time of day)")
    k, c = bins("hour", [12, 14, 16, 18, 20, 21, 22])
    out["tests"]["hour"] = table(a2, k, "hour of day, PDT", c)
    k, c = bins("kernel_wall", [0.3, 0.37, 0.45, 0.6, 1.0])
    out["tests"]["kernel_len"] = table(a2, k, "length of the kernel before, s (all are at 800 MHz, so this is iteration count)", c)
    print("\nHow long a hit lasts: first 600 reading to first 700, and to first 800 (s), over the hits that recover inside their process")
    d6 = [x["at600_s"] for x in durations if x["at600_s"] is not None]
    d8 = [x["to800_s"] for x in durations if x["to800_s"] is not None]
    print(f"   at 600 MHz: median {st.median(d6):.2f}, range {min(d6):.2f}-{max(d6):.2f}, n {len(d6)}; to 800 MHz: median {st.median(d8):.2f}, range {min(d8):.2f}-{max(d8):.2f}, n {len(d8)}")
    print(f"   the sampler's command at the first 600 reading: {sorted(x['took_ms'] for x in durations if x['took_ms'] is not None)} ms; on the reading before: {sorted(x['took_before'] for x in durations if x['took_before'] is not None)} ms")
    out["durations"] = durations
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
