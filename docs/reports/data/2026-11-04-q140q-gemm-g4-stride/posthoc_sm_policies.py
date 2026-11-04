#!/usr/bin/env python3
"""Q140(q), POST HOC (written after stride_sm.py's registered result was read; nothing frozen depends on it): which replacement
policy would make the L3's public set mapping reproduce E158's ladder? SM as registered (true LRU) keeps almost none of a far B
panel past 32 MB, where the card kept about half. Two other policies on the same map, offsets and trace (stride_sm.py's, unchanged):

  RANDOM  on a miss into a full set, a uniformly random way is evicted (seeded; deterministic);
  LIP     LRU order, but a missing tile is inserted at the LRU end (a hit moves it to the MRU end): a line that is reused climbs,
          a line used once leaves first (a thrash-resistant insertion, as in Qureshi et al., ISCA 2007).

    nice -n 10 python3 -B posthoc_sm_policies.py > posthoc-sm-policies.txt     (writes posthoc-sm-policies.json; 4 workers)
SPDX-License-Identifier: Apache-2.0
"""
import collections
import json
import math
import os
import random
import sys
from multiprocessing import Pool

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stride_sm as SM  # noqa: E402  (the registered term's code, unchanged: offsets, dev_addr, split_from, tsplit, the shape lists)

D, D146, ME = SM.D, SM.D146, SM.ME
POLICIES = ("LRU", "RANDOM", "LIP")


def l3_flags_policy(shape, off, policy, seed=140):
    rng = random.Random(seed)
    sets = collections.defaultdict(list)
    memo = {}

    def touch(t):
        s = memo.get(t)
        if s is None:
            s = (SM.dev_addr(t, off) >> 10) & (SM.NSETS - 1)
            memo[t] = s
        L = sets[s]
        if t in L:
            if policy != "RANDOM":
                L.remove(t)
                L.append(t)
            return True
        if len(L) >= SM.WAYS:
            if policy == "RANDOM":
                del L[rng.randrange(len(L))]
            else:
                del L[0]
        if policy == "LIP":
            L.insert(0, t)
        else:
            L.append(t)
        return False
    flags = []
    hc = nc = 0
    for p in range(2):
        for a, b, c in D146.l3_steps(shape):
            if c is not None:
                for t in c:
                    h = touch(t)
                    if p == 1:
                        hc += h
                        nc += 1
                continue
            hit = set()
            for t in a + b:
                if touch(t):
                    hit.add(t)
            if p == 1:
                flags.append(hit)
    return flags, hc / nc


def work(item):
    lab, (MB, NB, KB) = item
    shape = ("large", MB, NB, KB)
    missed = []
    for s0, s1 in ((0, 0), (3, 5)):
        ops = D.shire_ops(shape, s0, s1, D146.A0, D146.B0)
        sets = collections.defaultdict(list)
        D.l2_pass(ops, sets, True)
        _, _, m = D.l2_pass(ops, sets, True)
        missed.append(m)
    out = {"label": lab}
    for pol in POLICIES:
        f, hc = l3_flags_policy(shape, SM.offsets(MB, NB, KB), pol)
        out[pol] = dict(SM.split_from(missed, f, f), h_C=hc)
    return out


def main():
    ab, c1 = ME.load_prices()
    desk = ME.load_desk()
    R158 = json.load(open(os.path.join(SM.REPO, "docs/reports/data/2026-11-03-e158-l3-retention/results.json")))
    R146 = json.load(open(os.path.join(SM.REPO, "docs/reports/data/2026-11-02-e146-gemm-stores/results.json")))
    shapes = [(k, v) for k, v in SM.SHAPES.items() if k in desk["shapes"] or k in SM.E169]
    with Pool(4) as pool:
        res = {r["label"]: r for r in pool.map(work, shapes, chunksize=1)}
    meas = {f"E158:{k}": v["T800"] for k, v in R158["per_shape"].items()}
    meas.update({f"E146:{k}": v["T800"] for k, v in R146["per_shape"].items()})
    rows = []
    for key, T8 in sorted(meas.items()):
        sess, cell = key.split(":")
        s, t = cell.split(".")
        if s not in res or T8 is None:
            continue
        row = {"session": sess, "cell": cell, "shape": s, "type": t, "T800_meas": round(T8, 4)}
        for pol in POLICIES:
            p = SM.tsplit(res[s][pol], ab, c1, t)["T800"]
            row[pol] = {"T800": round(p, 4), "rel": round(T8 / p - 1, 4)}
        rows.append(row)

    def rmsof(sel, pol):
        v = [r[pol]["rel"] for r in rows if sel(r)]
        return round(math.sqrt(sum(x * x for x in v) / len(v)), 4) if v else None
    ladder = [k for k in list(SM.SHAPES)[:23] if k != "K6n1"]
    subsets = {"E146_ladder_all24": lambda r: r["session"] == "E146" and r["shape"] != "F6",
               "E158_22_rungs_fp32": lambda r: r["session"] == "E158" and r["type"] == "fp32" and r["shape"] in ladder,
               "F6_both": lambda r: r["shape"] == "F6", "collapses_fp32": lambda r: r["type"] == "fp32" and r["shape"] in SM.COLLAPSES,
               "all": lambda r: True}
    scores = {k: {pol: rmsof(f, pol) for pol in POLICIES} for k, f in subsets.items()}
    shares = {}
    for s in ladder:
        rec = desk["shapes"][s]
        tf, tl, n = ME.share_axis(rec, ab, c1, "fp32")
        if not n:
            continue
        shares[s] = {"measured": round(ME.share_of(R158["per_shape"][f"{s}.fp32"]["T800"], rec, ab, c1, "fp32"), 3)}
        for pol in POLICIES:
            T8 = SM.tsplit(res[s][pol], ab, c1, "fp32")["T800"]
            shares[s][pol] = round((tf - T8) / (tf - tl), 3)
    e169 = {s: {pol: round(SM.tsplit(res[s][pol], ab, c1, "fp32")["T800"], 4) for pol in POLICIES} for s in SM.E169}
    out = {"what": "Q140(q) POST HOC: SM's map with three replacement policies (written after the registered SM result was read)",
           "rows": rows, "scores": scores, "shares_fp32": shares, "E169_fp32_T800": e169,
           "lines": {s: {pol: {k: round(v, 3) for k, v in res[s][pol].items()} for pol in POLICIES} for s in res}}
    json.dump(out, open(os.path.join(HERE, "posthoc-sm-policies.json"), "w"), indent=1)
    print("POST HOC: SM's public map with three replacement policies (rms of measured / predicted - 1)")
    for k, v in scores.items():
        print(f"  {k:22s} " + "  ".join(f"{p} {v[p]}" for p in POLICIES))
    print("far-B share (fp32), measured vs policy:")
    for s, v in shares.items():
        print(f"  {s:6s} measured {v['measured']:+.3f}  " + "  ".join(f"{p} {v[p]:+.3f}" for p in POLICIES))
    print("collapse and F6 cells:")
    for r in rows:
        if r["shape"] in SM.COLLAPSES + ("F6",) and r["type"] == "fp32":
            print(f"  {r['session']}:{r['cell']:10s} meas {r['T800_meas']:.4f} " + "  ".join(f"{p} {r[p]['T800']:.4f} ({r[p]['rel']:+.4f})" for p in POLICIES))
    print("E169's shapes, fp32 T800 by policy:", json.dumps(e169))


if __name__ == "__main__":
    main()
