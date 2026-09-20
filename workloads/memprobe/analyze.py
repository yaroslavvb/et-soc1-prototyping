#!/usr/bin/env python3
"""Reduce memprobe results to the numbers the report uses, as one JSON file.

    analyze.py --data docs/reports/data/2026-09-19-memprobe-aifoundry2 --out summary.json

--data holds the <experiment>.u32 / <experiment>.json pairs written by memprobe_host and gen_ops.py, plus
power/summary.json from analyze_power.py. Latencies are load-to-use cycles at 600 MHz: the timed value minus
the 5 cycles of timer overhead that a timed L1 hit shows beyond the 5-cycle L1 latency the pointer chase measured.
"""
import argparse
import collections
import json
import os
import statistics as st
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ops as g  # noqa: E402

OVERHEAD = 5
ARENA_BASE = 0x8040000000


def load(data, name, raw=False):
    m = json.load(open(os.path.join(data, name + ".json")))
    r = struct.unpack(f"<{len(m['labels'])}I", open(os.path.join(data, name + ".u32"), "rb").read())
    if not raw:
        r = [(v if v < 2**31 else v - 2**32) - OVERHEAD for v in r]
    return m, [tuple(l) if isinstance(l, list) else l for l in m["labels"]], r


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))]


def timer(data):
    _, _, r = load(data, "t_raw", raw=True)
    t0, t1 = r[0::4], r[1::4]
    raw = collections.Counter(((b - a) % 2**32) for a, b in zip(t0, t1))
    fix = lambda v: v + 128 if (v & 0x7F) < 11 else v  # noqa: E731
    fixed = collections.Counter(fix(b) - fix(a) for a, b in zip(t0, t1))
    return {"pairs": len(t0), "raw": {str(k if k < 2**31 else k - 2**32): n for k, n in raw.most_common()},
            "fixed": {str(k): n for k, n in fixed.most_common()}}


def ladder(data):
    _, labels, r = load(data, "ladder")
    g_ = collections.defaultdict(list)
    for lab, v in zip(labels, r):
        if lab[0] in ("ladder", "nofence", "nodelay", "tevict_clean", "tevict_dirty") and v > -50:
            g_[f"{lab[0]}:{lab[2]}"].append(v)
    return {k: {"n": len(v), "min": min(v), "p10": q(v, .1), "med": q(v, .5), "p90": q(v, .9), "max": max(v)}
            for k, v in g_.items()}


def decomp(data):
    _, labels, r = load(data, "decomp")
    d = collections.defaultdict(lambda: collections.defaultdict(list))
    for lab, v in zip(labels, r):
        if v > 0:
            d[lab[1]][lab[0]].append(v)
    l2 = [v for x in d.values() for v in x["l2"]]
    slices = collections.defaultdict(list)
    res = collections.defaultdict(list)
    mem = []
    model_err = []
    for a, x in d.items():
        pa = ARENA_BASE + a
        s, ms = (pa >> 6) & 31, (pa >> 6) & 7
        l3 = st.median(x["l3"])
        slices[s].append(l3)
        for v in x["mem"]:
            res[(ms, s)].append(v - l3)
            mem.append(v)
    # Memory shire positions: one step off the north / south edge, fitted jointly with one constant.
    p10 = {k: q(v, .1) for k, v in res.items()}
    edge = [(x, y) for x in range(-1, 7) for y in range(-1, 7) if x in (-1, 6) or y in (-1, 6)]
    best = None
    for c in range(30, 120):
        tot, pos = 0, {}
        for ms in range(8):
            items = [(s, v) for (m_, s), v in p10.items() if m_ == ms]
            e, pp = min((sum((v - c - 12 * dist(s, p)) ** 2 for s, v in items), p) for p in edge)
            tot += e
            pos[ms] = pp
        if best is None or tot < best[0]:
            best = (tot, c, pos)
    const, pos = best[1], best[2]
    if pos[4] == (0, 5):  # ties with (1, 6); take the one in line with memory shires 5-7
        pos[4] = (1, 6)
    for a, x in d.items():
        pa = ARENA_BASE + a
        s, ms = (pa >> 6) & 31, (pa >> 6) & 7
        pred = 110 + 12 * g.hops(0, s) + const + 12 * dist(s, pos[ms])
        model_err.append(min(x["mem"]) - pred)
    return {
        "lines": len(d),
        "l2": {"min": min(l2), "med": q(l2, .5), "hist": collections.Counter(l2).most_common(4)},
        "l3_by_slice": {s: {"med": st.median(v), "hops": g.hops(0, s), "n": len(v)} for s, v in sorted(slices.items())},
        "l3_model_off": sum(1 for s, v in slices.items() for x in v if abs(x - (110 + 12 * g.hops(0, s))) > 4),
        "mem": {"min": min(mem), "p10": q(mem, .1), "med": q(mem, .5), "p90": q(mem, .9), "max": max(mem)},
        "mem_hist": sorted(collections.Counter(v // 6 * 6 for v in mem).items()),
        "ms_const": const, "ms_pos": pos, "ms_fit_sqerr": best[0],
        "model_err_hist": sorted(collections.Counter(model_err).items()),
    }


def dist(s, p):
    return abs(g.MESH[s][0] - p[0]) + abs(g.MESH[s][1] - p[1])


def msmap(data):
    _, labels, r = load(data, "msmap", raw=True)
    v = dict(zip(labels, r))
    lines = sorted({lab[1] for lab in labels})
    rows, ok = [], 0
    for a in lines:
        dd = [(v[("after", a, ms)] - v[("before", a, ms)]) % 2**32 for ms in range(8)]
        pa = ARENA_BASE + a
        top = max(range(8), key=lambda i: dd[i])
        ok += top == (pa >> 6) & 7
        rows.append({"pa": hex(pa), "ms_bits": (pa >> 6) & 7, "deltas": dd})
    return {"lines": len(lines), "match": ok, "rows": rows[:16]}


def bits(data):
    _, labels, r = load(data, "bits")
    d = collections.defaultdict(lambda: collections.defaultdict(dict))
    for lab, v in zip(labels, r):
        d[lab[1]][lab[0]][lab[2]] = v
    out = {}
    for b in sorted(d):
        x = d[b]
        diffs = [x["B"][t] - x["B0"][t] for t in x["B"] if x["B"][t] > 0 and x["B0"].get(t, 0) > 0]
        ab = [v for v in x["AB"].values() if v > 0]
        a = [v for v in x["A"].values() if v > 0]
        out[b] = {"b_minus_b0": st.mean(diffs), "se": st.stdev(diffs) / len(diffs) ** .5,
                  "ab_p10": q(ab, .1), "ab_med": q(ab, .5), "ab_p90": q(ab, .9), "a_med": q(a, .5)}
    return out


def refresh(data):
    _, labels, r = load(data, "refresh_jit")
    ts = [v + OVERHEAD for v in r[0::2]]
    lat = r[1::2]
    ts = [(t - ts[0]) % 2**32 for t in ts]
    slow = [t for t, l in zip(ts, lat) if l >= 260]
    best = max(((max(collections.Counter(int((t % (P / 10)) / (P / 10) * 50) for t in slow).values()), P / 10)
                for P in range(22000, 24500, 2)))
    period = best[1]
    fold = collections.defaultdict(list)
    for t, l in zip(ts, lat):
        fold[int((t % period) / period * 50)].append(l)
    # Rotate so the refresh window starts at phase 0.
    peak = max(fold, key=lambda k: q(fold[k], .9))
    curve = [{"phase": k, "med": st.median(fold[(k + peak - 2) % 50]), "max": max(fold[(k + peak - 2) % 50]),
              "p90": q(fold[(k + peak - 2) % 50], .9)} for k in range(50)]
    _, _, r0 = load(data, "refresh")
    lat0 = r0[1::2]
    return {"period_cycles": period, "period_us": period / 600, "n": len(lat), "hist": sorted(collections.Counter(v // 10 * 10 for v in lat).items()),
            "curve": curve, "locked_hist": sorted(collections.Counter(v // 2 * 2 for v in lat0).items())}


def pagetimeout(data):
    _, labels, r = load(data, "pagetimeout")
    d = collections.defaultdict(lambda: collections.defaultdict(dict))
    for lab, v in zip(labels, r):
        d[lab[1]][lab[0]][lab[2]] = v
    out = []
    for delay in sorted(d):
        A, B = d[delay]["A"], d[delay]["B"]
        diff = [B[t] - A[t] for t in B if A[t] > 150 and B[t] > 150]
        out.append({"delay": delay, "hit": sum(1 for x in diff if -16 <= x <= -7) / len(diff),
                    "median_saving": -st.median(diff), "refresh_model": max(0, 1 - (delay + 300) / 2325)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = {"timer": timer(args.data), "ladder": ladder(args.data), "decomp": decomp(args.data),
           "msmap": msmap(args.data), "bits": bits(args.data), "refresh": refresh(args.data),
           "pagetimeout": pagetimeout(args.data),
           "power": json.load(open(os.path.join(args.data, "power", "summary.json")))["summary"],
           "far_hops": [g.hops(s, h) for s, h in sorted(g.far_homes().items())]}
    json.dump(out, open(args.out, "w"), indent=1, default=str)
    d = out["decomp"]
    print(f"L3 model off by >4 cycles: {d['l3_model_off']}; memory shire constant {d['ms_const']}, "
          f"positions {d['ms_pos']}, fit error {d['ms_fit_sqerr']}")
    print(f"msmap {out['msmap']['match']}/{out['msmap']['lines']}; refresh period {out['refresh']['period_us']:.3f} us")
    print("model error (DRAM min - model):", d["model_err_hist"][:20])


if __name__ == "__main__":
    main()
