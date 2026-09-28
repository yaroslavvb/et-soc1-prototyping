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


def ladder_residuals(data, dec):
    """The DRAM rows of the ladder as {condition: {memory shire: [(measured, measured - closed-row model)]}}."""
    _, labels, r = load(data, "ladder")
    const, pos = dec["ms_const"], dec["ms_pos"]
    g_ = collections.defaultdict(lambda: collections.defaultdict(list))
    for lab, v in zip(labels, r):
        if lab[0] in ("ladder", "nofence", "nodelay") and lab[2] == 3 and v > -50:
            pa = ARENA_BASE + lab[1]
            s, ms = (pa >> 6) & 31, (pa >> 6) & 7
            g_[f"{lab[0]}:3"][ms].append((v, v - (110 + 12 * g.hops(0, s) + const + 12 * dist(s, pos[ms]))))
    return g_


def ladder_by_ms(data, dec):
    """The DRAM rows of the ladder by memory shire, against the closed-row model of decomp(): n, median, and the
    median of (measured - model). Shows whether a load issued behind an evict found its row open (below the model)
    or still waited for the evict at the memory shire (above it)."""
    g_ = ladder_residuals(data, dec)
    return {k: {ms: {"n": len(v), "med": st.median(x for x, _ in v), "resid_med": st.median(e for _, e in v),
                     "fast": sum(1 for _, e in v if e <= -6)} for ms, v in sorted(x.items())} for k, x in g_.items()}


def ladder_slow(data, dec):
    """Per condition, the loads that did not find their row open (measured - model > -6), pooled over the memory
    shires: n and the median of (measured - model). A per-shire median mixes these with the fast, open-row loads,
    whose share differs by memory shire; this separates the two."""
    g_ = ladder_residuals(data, dec)
    out = {}
    for k, x in g_.items():
        e = [e for v in x.values() for _, e in v if e > -6]
        out[k] = {"n": len(e), "resid_med": st.median(e), "above6": sum(1 for d in e if d > 6)}
    return out


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
    by_home, within3 = collections.defaultdict(list), 0
    for a, x in d.items():
        pa = ARENA_BASE + a
        s, ms = (pa >> 6) & 31, (pa >> 6) & 7
        pred = 110 + 12 * g.hops(0, s) + const + 12 * dist(s, pos[ms])
        model_err.append(min(x["mem"]) - pred)
        by_home[s].append((min(x["mem"]), pred))
        within3 += sum(1 for v in x["mem"] if abs(v - pred) <= 3)
    return {
        "lines": len(d),
        "l2": {"min": min(l2), "med": q(l2, .5), "hist": collections.Counter(l2).most_common(4)},
        "l3_by_slice": {s: {"med": st.median(v), "hops": g.hops(0, s), "n": len(v)} for s, v in sorted(slices.items())},
        "l3_model_off": sum(1 for s, v in slices.items() for x in v if abs(x - (110 + 12 * g.hops(0, s))) > 4),
        "mem": {"min": min(mem), "p10": q(mem, .1), "med": q(mem, .5), "p90": q(mem, .9), "max": max(mem)},
        "mem_hist": sorted(collections.Counter(v // 6 * 6 for v in mem).items()),
        "ms_const": const, "ms_pos": pos, "ms_fit_sqerr": best[0],
        "model_err_hist": sorted(collections.Counter(model_err).items()),
        # Per L3 home shire, from shire 0: the model (fitted to these same loads) and the median over the home's
        # lines of each line's fastest DRAM load.
        "mem_by_home": {s: {"model": v[0][1], "fast_med": st.median(f for f, _ in v), "n": len(v)}
                        for s, v in sorted(by_home.items())},
        # every single DRAM load (not each line's fastest of three) against the model
        "model_err_loads": {"within3": within3, "n": len(mem)},
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
                  "ab_p10": q(ab, .1), "ab_med": q(ab, .5), "ab_p90": q(ab, .9), "a_med": q(a, .5),
                  # B loaded on its own right after A (not back to back), against B alone: the median and
                  # quartiles, which a tail of refresh waits does not pull the way it pulls the mean
                  "b_minus_b0_med": st.median(diffs), "b_minus_b0_p25": q(diffs, .25), "b_minus_b0_p75": q(diffs, .75)}
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
    # What closes the row: each load against the one before it, split by whether a refresh started in between.
    # The refresh starts in the first curve bin whose 90th percentile is slow; loads that were themselves held up
    # by a refresh (>= 240) or glitched (< 150) are left out; a row hit reads <= 220 (open 215, closed 226).
    first = next(k for k in range(50) if curve[k]["p90"] >= 260)
    ref0 = ((peak - 2 + first) % 50) / 50 * period
    nref = lambda a, b: int((b - ref0) // period) - int((a - ref0) // period)  # noqa: E731
    un, off = [], 0
    for i, t in enumerate(ts):  # the stamps wrap at 2**32
        if i and t + off < un[-1] - 2**31:
            off += 2**32
        un.append(t + off)
    life = collections.defaultdict(lambda: [0, 0, 0, 0])
    phase_hits = collections.defaultdict(lambda: [0, 0])
    for i in range(1, len(un)):
        if not 150 <= lat[i] < 240:
            continue
        gap = un[i] - un[i - 1] - lat[i - 1]
        k = 2 if nref(un[i - 1], un[i]) else 0
        b = life[int(gap // 250) * 250]
        b[k] += lat[i] <= 220
        b[k + 1] += 1
        ph = phase_hits[(int((un[i] % period) / period * 50) - peak + 2) % 50]
        ph[0] += lat[i] <= 220
        ph[1] += 1
    r0_ = load(data, "refresh")[2]
    ts0, lat0 = [v + OVERHEAD for v in r0_[0::2]], r0_[1::2]
    # The probe's own time per op: the locked loop (evict, fence, stamp, timed load) spends its stamp-to-stamp
    # time minus the load on four op dispatches, each fetched from the L2 scratchpad.
    op = st.median((ts0[i + 1] - ts0[i]) % 2**32 - lat0[i] for i in range(len(ts0) - 1)) / 4
    # The locked loop's lock: each turn (stamp to stamp) is the probe's own ops plus its load, so a turn whose load
    # found the row open (< 220) has the loop's shortest period; four of them fall short of the refresh period, and
    # the slow load (>= 220: the first after a refresh) makes up the difference. Kept per series: the medians of the
    # open and slow loads and of the open turns, and how many gaps between consecutive slow loads are exactly four.
    per = [(ts0[i + 1] - ts0[i]) % 2**32 for i in range(len(ts0) - 1)]
    slow = [i for i, v in enumerate(lat0) if v >= 220]
    locked = {"n": len(lat0), "slow": len(slow), "in_refresh": sum(1 for v in lat0 if v >= 250), "max": max(lat0),
              "slow_med": st.median(lat0[i] for i in slow), "open_med": st.median(v for v in lat0 if v < 220),
              "period_med": st.median(per), "period_open_med": st.median(p for p, v in zip(per, lat0) if v < 220),
              "gaps": len(slow) - 1, "every4": sum(1 for a, b in zip(slow, slow[1:]) if b - a == 4)}
    # the jittered series' open- and closed-row clusters (as v3_cards reads them): the activate a refresh adds, and
    # the longest wait for a refresh, the slowest load over the closed-row median
    cl, opn = [x for x in lat if 220 <= x < 232], [x for x in lat if 208 <= x < 220]
    return {"period_cycles": period, "period_us": period / 600, "n": len(lat), "hist": sorted(collections.Counter(v // 10 * 10 for v in lat).items()),
            "curve": curve, "locked_hist": sorted(collections.Counter(v // 2 * 2 for v in lat0).items()),
            "in_refresh": sum(1 for v in lat if v >= 240) / len(lat),
            "op_cycles": op,
            "rowlife": [{"gap": g_, "hit_no_refresh": v[0], "n_no_refresh": v[1], "hit_refresh": v[2], "n_refresh": v[3]}
                        for g_, v in sorted(life.items())],
            "hit_by_phase": [{"phase": k, "hit": phase_hits[k][0], "n": phase_hits[k][1]} for k in range(50)],
            "closed_minus_open": st.mean(cl) - st.mean(opn), "closed_med": st.median(cl), "open_med": st.median(opn),
            "max_wait": max(lat) - st.median(cl), "locked": locked}


def pagetimeout(data, ref):
    """Pairs of loads to two lines of one row, A then B after a set delay. refresh_model assumes nothing but the
    delay between them; refresh_model_loop counts what else lies between A opening the row and B reaching it: A's
    own latency (+5 of timer overhead), the probe's two op dispatches (delay, timed load; refresh op_cycles each), and
    the share of loads that land inside a refresh. Averaged over the pairs, it is what refresh alone predicts."""
    _, labels, r = load(data, "pagetimeout")
    P, ovh, inr = ref["period_cycles"], 2 * ref["op_cycles"], ref["in_refresh"]
    d = collections.defaultdict(lambda: collections.defaultdict(dict))
    for lab, v in zip(labels, r):
        d[lab[1]][lab[0]][lab[2]] = v
    out = []
    for delay in sorted(d):
        A, B = d[delay]["A"], d[delay]["B"]
        pairs = [t for t in B if A[t] > 150 and B[t] > 150]
        diff = [B[t] - A[t] for t in pairs]
        hits = sum(1 for x in diff if -16 <= x <= -7)
        out.append({"delay": delay, "hit": hits / len(diff),
                    "median_saving": -st.median(diff), "refresh_model": max(0, 1 - (delay + 300) / 2325),
                    "hits": hits, "n": len(diff),
                    "refresh_model_loop": st.mean(max(0, 1 - (A[t] + OVERHEAD + ovh + delay + inr * P) / P) for t in pairs)})
    return out


def v3_cards(raw, passes_json, out_path, model_json):
    """The version-3 claims check's memprobe passes (tools/claims-v3/mem/README.md), every card, reduced with this
    file's own functions so the page can put them beside its 19 September session:

        analyze.py --v3 docs/reports/data/2026-09-25-claims-v3/raw \
            --v3-passes docs/reports/data/2026-09-25-claims-v3/results/mem.passes.json \
            --out docs/reports/data/2026-09-26-memprobe-3cards/cards.json

    The passes used are the reducer's (mem.passes.json "kept": each card's first five kept X1 passes). Each pass is
    copied to a scratch folder with its labels un-gzipped. The version-3 build's timed L1 hit reads 17 raw, not 10, so
    every latency is re-referenced to the pass's own L1 hit, as the reducer's recompute_latency.py --l1-ref does:
    OVERHEAD becomes 5 + (median raw L1 hit - 10), which leaves the time stamps raw. The refresh series' row
    clusters are read after that shift (the reducer's extra_values.py reads P5b and P6r without it). Per home shire it keeps each
    pass's L3 median (l3_by_slice) and the median of its lines' fastest DRAM loads (mem_by_home), for the page's
    memory-shire leg. The DRAM model
    error uses the 19 September model as it stands (model_json: that session's summary.json, its constant and memory
    shire positions, not refitted), each line's fastest of three loads, as the reducer's MEM-P2 does."""
    import gzip
    import shutil
    import tempfile
    global OVERHEAD
    meta = json.load(open(passes_json))
    m19 = json.load(open(model_json))["decomp"]
    const19, pos19 = m19["ms_const"], {int(k): v for k, v in m19["ms_pos"].items()}
    progs = ["ladder", "decomp", "refresh", "refresh_jit", "pagetimeout"]
    out = {"source": {"raw": raw, "passes": passes_json, "kept": meta["kept"],
                      "note": "every latency re-referenced to the pass's own timed L1 hit (= 5 cycles)"}, "cards": {}}
    for card in meta["cards"]:
        info = {p["pass"]: p for p in meta["passes"][card]}
        C = {"passes": [], "shift": [], "ladder": collections.defaultdict(list), "l3_by_slice": collections.defaultdict(list),
             "dram_med": [], "dram_hist": collections.Counter(), "ms_const": [], "period": [], "op_cycles": [],
             "rows": [0, 0, 0, 0], "closed_minus_open": [], "closed_mean": [], "open_mean": [],
             "pto": collections.defaultdict(lambda: [0, 0]), "model_err": collections.Counter(), "within3": [],
             "locked": [], "mem_by_home": collections.defaultdict(list)}
        for pk in meta["kept"][card]["x1"]:
            k = int(pk[1:])
            if info[k]["arena_bases"] != [hex(ARENA_BASE)]:
                raise SystemExit(f"{card} {pk}: arena base {info[k]['arena_bases']}, not {hex(ARENA_BASE)}")
            src, tmp = os.path.join(raw, card, "mem", pk), tempfile.mkdtemp(prefix="memprobe-v3-")
            try:
                for n in progs:
                    with gzip.open(os.path.join(src, n + ".json.gz"), "rt") as f, open(os.path.join(tmp, n + ".json"), "w") as fo:
                        shutil.copyfileobj(f, fo)
                    shutil.copy(os.path.join(src, n + ".u32"), os.path.join(tmp, n + ".u32"))
                OVERHEAD = 5
                _, labels, r = load(tmp, "ladder", raw=True)
                shift = int(round(st.median(v for lab, v in zip(labels, r) if lab[0] == "ladder" and lab[2] in (-1, 0)) - 10))
                OVERHEAD = 5 + shift
                lad, dec, ref = ladder(tmp), decomp(tmp), refresh(tmp)
                pto = pagetimeout(tmp, ref)
                _, _, rj = load(tmp, "refresh_jit")
                lat = rj[1::2]
                _, _, rl = load(tmp, "refresh")
                _, dl, dr = load(tmp, "decomp")
            finally:
                OVERHEAD = 5
                shutil.rmtree(tmp, ignore_errors=True)
            C["passes"].append(pk)
            C["shift"].append(shift)
            for key, v in lad.items():
                C["ladder"][key].append(v["med"])
            for s, v in dec["l3_by_slice"].items():
                C["l3_by_slice"][s].append(v["med"])
            C["dram_med"].append(dec["mem"]["med"])
            for s_, v in dec["mem_by_home"].items():  # per home shire: the median of its lines' fastest DRAM loads
                C["mem_by_home"][s_].append(v["fast_med"])
            C["dram_hist"].update(dict(dec["mem_hist"]))
            C["ms_const"].append(dec["ms_const"])
            C["period"].append(ref["period_cycles"])
            C["op_cycles"].append(ref["op_cycles"])
            for x in ref["rowlife"]:  # the page's split: gaps under 2,000 idle cycles
                if x["gap"] < 2000:
                    for i, key in enumerate(("hit_no_refresh", "n_no_refresh", "hit_refresh", "n_refresh")):
                        C["rows"][i] += x[key]
            # the open- and closed-row clusters of the refresh series (as extra_values.py's P5b windows)
            cl, op = [x for x in lat if 220 <= x < 232], [x for x in lat if 208 <= x < 220]
            C["closed_mean"].append(st.mean(cl))
            C["open_mean"].append(st.mean(op))
            C["closed_minus_open"].append(st.mean(cl) - st.mean(op))
            for p in pto:
                C["pto"][p["delay"]][0] += p["hits"]
                C["pto"][p["delay"]][1] += p["n"]
            # the 19 September DRAM model, not refitted: each line's fastest of three loads against it
            fast = collections.defaultdict(list)
            for lab, v in zip(dl, dr):
                if lab[0] == "mem" and v > 0:
                    fast[lab[1]].append(v)
            errs = []
            for a, v in fast.items():
                s_, ms_ = ((ARENA_BASE + a) >> 6) & 31, ((ARENA_BASE + a) >> 6) & 7
                errs.append(min(v) - (110 + 12 * g.hops(0, s_) + const19 + 12 * dist(s_, pos19[ms_])))
            C["model_err"].update(errs)
            C["within3"].append([sum(1 for e in errs if abs(e) <= 3), len(errs)])
            # the locked series (fixed loop period): its period, how many loads were slow, and how many waited in a refresh
            ts0, lat0 = [v + OVERHEAD for v in rl[0::2]], rl[1::2]
            per = [(ts0[i + 1] - ts0[i]) % 2**32 for i in range(len(ts0) - 1)]
            C["locked"].append({"period_med": st.median(per), "n": len(lat0), "slow": sum(1 for v in lat0 if v >= 220),
                                "in_refresh": sum(1 for v in lat0 if v >= 250), "max": max(lat0),
                                "slow_med": st.median(v for v in lat0 if v >= 220),
                                # the lock (refresh() above, on the same re-referenced series)
                                **{k: ref["locked"][k] for k in ("open_med", "period_open_med", "gaps", "every4")}})
            if any(C["locked"][-1][k] != ref["locked"][k] for k in ("period_med", "n", "slow", "in_refresh", "max", "slow_med")):
                raise SystemExit(f"{card} {pk}: the locked series reads differently in refresh() and here")
        C["ladder"] = dict(C["ladder"])
        C["l3_by_slice"] = {s: {"med": v, "hops": g.hops(0, s)} for s, v in sorted(C["l3_by_slice"].items())}
        C["mem_by_home"] = {s: v for s, v in sorted(C["mem_by_home"].items())}
        C["dram_hist"] = sorted(C["dram_hist"].items())
        C["pto"] = {d: v for d, v in sorted(C["pto"].items())}
        C["model_err"] = sorted(C["model_err"].items())
        out["cards"][card] = C
        print(f"{card}: passes {C['passes']}, L1 shift {C['shift']}, DRAM median {C['dram_med']}, "
              f"ladder DRAM {C['ladder']['ladder:3']}, closed - open {[round(x, 1) for x in C['closed_minus_open']]}, "
              f"rows {C['rows']}, within 3 of the 19 Sep model {C['within3']}, locked {C['locked'][0]}")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    json.dump(out, open(out_path, "w"), indent=1, default=str)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    ap.add_argument("--out", required=True)
    ap.add_argument("--v3", metavar="RAW_ROOT", help="reduce the version-3 passes of every card instead (see v3_cards)")
    ap.add_argument("--v3-passes", metavar="MEM_PASSES_JSON", help="the reducer's mem.passes.json (which passes are kept)")
    ap.add_argument("--v3-model", metavar="SUMMARY_JSON", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "reports", "data", "2026-09-19-memprobe-aifoundry2", "summary.json"),
        help="the 19 September summary.json, whose DRAM model (constant, memory shire positions) is tested as it stands")
    args = ap.parse_args()
    if args.v3:
        return v3_cards(args.v3, args.v3_passes, args.out, args.v3_model)
    if not args.data:
        ap.error("--data is required")
    dec, ref = decomp(args.data), refresh(args.data)
    out = {"timer": timer(args.data), "ladder": ladder(args.data), "decomp": dec,
           "msmap": msmap(args.data), "bits": bits(args.data), "refresh": ref,
           "pagetimeout": pagetimeout(args.data, ref),
           "power": json.load(open(os.path.join(args.data, "power", "summary.json")))["summary"],
           "far_hops": [g.hops(s, h) for s, h in sorted(g.far_homes().items())],
           "ladder_by_ms": ladder_by_ms(args.data, dec), "ladder_slow": ladder_slow(args.data, dec)}
    json.dump(out, open(args.out, "w"), indent=1, default=str)
    d = out["decomp"]
    print(f"L3 model off by >4 cycles: {d['l3_model_off']}; memory shire constant {d['ms_const']}, "
          f"positions {d['ms_pos']}, fit error {d['ms_fit_sqerr']}")
    print(f"msmap {out['msmap']['match']}/{out['msmap']['lines']}; refresh period {out['refresh']['period_us']:.3f} us")
    print("model error (DRAM min - model):", d["model_err_hist"][:20])


if __name__ == "__main__":
    main()
