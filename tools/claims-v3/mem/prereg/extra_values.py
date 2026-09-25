#!/usr/bin/env python3
"""Pass-level values for the anat-X1 / anat-X2 predictions that crosscard_tests.py computes badly or not at all
(verifier, 25 Sep, written before any run). No card.

    extra_values.py --data PASS_DIR [--requester S] [--x2-only]

--x2-only: the folder holds only ladder + decomp (a req<S>/ folder of anat-X2).
Every latency is re-referenced to the folder's own timed L1 hit (ladder levels -1/0 read as 10 raw on 19 Sep).
The DRAM model is the 19 Sep one, not refitted: 110 + 12 hops(S, home) + 91 + 12 hops(home, memory shire),
memory shires 0-3 at (1..4, -1), 4-7 at (1..4, 6).
"""
import argparse, collections, json, os, struct, statistics as st

MESH = {0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0), 8: (0, 1), 16: (1, 1), 1: (2, 1),
        17: (3, 1), 10: (4, 1), 19: (5, 1), 3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
        12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3), 20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
        28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5)}
POS = {0: (1, -1), 1: (2, -1), 2: (3, -1), 3: (4, -1), 4: (1, 6), 5: (2, 6), 6: (3, 6), 7: (4, 6)}
OVH = 5


def hops(a, b):
    return abs(MESH[a][0] - MESH[b][0]) + abs(MESH[a][1] - MESH[b][1])


def dist(s, p):
    return abs(MESH[s][0] - p[0]) + abs(MESH[s][1] - p[1])


def load(d, name, shift):
    m = json.load(open(os.path.join(d, name + ".json")))
    raw = open(os.path.join(d, name + ".u32"), "rb").read()
    r = struct.unpack(f"<{len(raw) // 4}I", raw)
    labs = [tuple(l) for l in m["labels"]]
    assert len(labs) == len(r), name
    return m, labs, [(v if v < 2**31 else v - 2**32) - OVH - shift for v in r]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--requester", type=int, default=0)
    ap.add_argument("--base", type=lambda s: int(s, 0), default=0x8040000000,
                    help="arena base the pass ran at (the MEMPROBE line's arena_base); only bits 10:6 matter")
    ap.add_argument("--x2-only", action="store_true")
    a = ap.parse_args()
    S, D, B = a.requester, a.data, a.base
    _, labs, r = load(D, "ladder", 0)
    shift = int(round(st.median(v + OVH for l, v in zip(labs, r) if l[0] == "ladder" and l[2] in (-1, 0)) - 10))
    out = {"l1_shift": shift, "requester": S}
    home = lambda off: ((B + off) >> 6) & 31  # noqa: E731
    ms = lambda off: ((B + off) >> 6) & 7  # noqa: E731
    model = lambda off: 110 + 12 * hops(S, home(off)) + 91 + 12 * dist(home(off), POS[ms(off)])  # noqa: E731

    # decomp: L3 (median of 3 per line) and DRAM (fastest of 3 per line) against the fixed models
    _, labs, r = load(D, "decomp", shift)
    d = collections.defaultdict(lambda: collections.defaultdict(list))
    for l, v in zip(labs, r):
        d[l[1]][l[0]].append(v)
    l3 = [st.median(x["l3"]) - (110 + 12 * hops(S, home(off))) for off, x in d.items()]
    mem = [min(x["mem"]) - model(off) for off, x in d.items()]
    out["l3_within4_frac"] = sum(abs(e) <= 4 for e in l3) / len(l3)
    out["dram_within3_frac"] = sum(abs(e) <= 3 for e in mem) / len(mem)
    out["dram_median_resid"] = st.median(mem)
    if a.x2_only:
        print(json.dumps(out, indent=1))
        return

    # P8b / P8c: fence, no wait (ladder 'nodelay', evict to memory)
    _, labs, r = load(D, "ladder", shift)
    open_lo = collections.Counter()
    for l, v in zip(labs, r):
        if l[0] == "nodelay" and l[2] == 3 and v > -50:
            e = v - model(l[1])
            grp = "A" if ms(l[1]) in (0, 1, 2, 4) else "B"
            open_lo[(grp, "n")] += 1
            open_lo[(grp, "open")] += -14 <= e <= -6
            if e > -6:
                open_lo.setdefault("nonopen", [])
                out.setdefault("_nonopen", []).append(e)
    out["P8b_open_frac_ms0124"] = open_lo[("A", "open")] / open_lo[("A", "n")]
    out["P8b_open_frac_ms3567"] = open_lo[("B", "open")] / open_lo[("B", "n")]
    out["P8b_open_frac_diff"] = out["P8b_open_frac_ms0124"] - out["P8b_open_frac_ms3567"]
    out["P8c_nonopen_resid_median"] = st.median(out.pop("_nonopen"))

    # P6 (boundary-robust): row hits in the jittered refresh series, only for pairs whose two time stamps are both
    # more than 150 cycles from the estimated refresh start, so a one- or two-bin error in that estimate cannot move it
    _, labs, r = load(D, "refresh_jit", 0)
    ts = [v + OVH for v in r[0::2]]
    lat = r[1::2]
    ts = [t % 2**32 for t in ts]
    un, off = [], 0
    for i, t in enumerate(ts):
        if i and t + off < un[-1] - 2**31:
            off += 2**32
        un.append(t + off)
    slow = [t for t, x in zip(un, lat) if x >= 260 + 0]
    best = None
    P10 = 22000
    while P10 < 24500:  # period in tenths of a cycle, as analyze.py
        P = P10 / 10
        c = collections.Counter(int((t % P) / P * 50) for t in slow)
        s = max(c.values())
        if best is None or s > best[0]:
            best = (s, P)
        P10 += 2
    P = best[1]
    nb = 50
    bins = collections.defaultdict(list)
    for t, x in zip(un, lat):
        bins[int((t % P) / P * nb)].append(x)
    p90 = {k: sorted(v)[min(len(v) - 1, int(.9 * len(v)))] for k, v in bins.items()}
    peak = max(p90, key=p90.get)
    first = next(k for k in range(nb) if p90.get((k + peak - 2) % nb, 0) >= 260)
    ref0 = ((peak - 2 + first) % nb) / nb * P
    nref = lambda x, y: int((y - ref0) // P) - int((x - ref0) // P)  # noqa: E731
    far = lambda t: abs(((t - ref0 + P / 2) % P) - P / 2) > 150  # noqa: E731
    h = [0, 0, 0, 0]
    for i in range(1, len(un)):
        if not 150 <= lat[i] < 240 or not (far(un[i]) and far(un[i - 1])):
            continue
        k = 2 if nref(un[i - 1], un[i]) else 0
        h[k] += lat[i] <= 220
        h[k + 1] += 1
    out["P5_period_check"] = P
    # P5b: closed-row minus open-row time as the difference of the two clusters' means (the top single-cycle modes
    # 225/226/227 and 213/214/215 swap between passes, so a mode difference can read 10-14 for the same physics)
    cl = [x for x in lat if 220 <= x < 232]
    op = [x for x in lat if 208 <= x < 220]
    out["P5b_closed_minus_open_means"] = st.mean(cl) - st.mean(op) if cl and op else None
    out["P6r_hit_no_refresh"] = h[0] / h[1] if h[1] else None
    out["P6r_hit_refresh"] = h[2] / h[3] if h[3] else None
    out["P6r_counts"] = h
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
