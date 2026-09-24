#!/usr/bin/env python3
"""Reduce the wire experiment (run_wire.py) to energy per bit per hop, per transition, and per millimetre.

    python3 workloads/enercat/analyze_wire.py DATA_A2 [DATA_A3 ...] --out wire.json [--pitch-x-mm X --pitch-y-mm Y]
                                              [--no-leak-correction]

Each (configuration, pass) burst is reduced the way the energy catalogue does it — board power over the mean of
the idle brackets on both sides, less the extra leakage of a burst that ran warmer than its brackets — except that
the brackets here exclude every prefill and heater window logged in marks.jsonl, and a burst is dropped if any of
its samples left 600 MHz. Then, per card and pooled over cards:

  slope per hop     least squares of pJ per payload byte against hop distance d = 1..6 (d = 0, the shire's own
                    scratchpad, is reported separately: leaving the shire is its own step);
  per transition    the slope against the toggle probability of the data, t = 2P(1-P) for independent bits:
                    slope(P) = s0 + e_t * t (+ e_1 * P to test whether ones rather than transitions cost);
  flit width        the slope for blocks of N bytes alternately 0x00 and 0xFF, against N;
  direction         x-only against y-only pairs;
  per millimetre    e_t and the slopes divided by the hop pitch, if given.

Board power is the primary measurement; the mesh (NoC) rail, which feeds the routers and links, is a second,
independent one (its per-burst reading is the SP's filtered average, taken from the burst's last 0.6 s, against the
idle before the burst, with no leakage correction).

Also computed, for the report's checks: link sharing of every configuration from its recorded reader>target map
(data flows target -> reader, dimension-ordered XY routing on the runner's logical map, and YX for comparison), the
per-reader bandwidth, board watts per mesh-rail watt against distance, how far the four-hop point sits off the line,
the step of leaving the shire, the 256 B block pattern's excess per hop, and the model refitted without the leakage
correction (the "sensitivity" block).
"""
import argparse
import collections
import gzip
import json
import math
import os
import re

import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_wire import MESH   # noqa: E402  the runner's logical map of the 32 minion shires, shire -> (x, y)

A_LEAK_80, T_L = 23.257, 36.0


def leak_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def jl(path):
    if os.path.exists(path + ".gz"):
        return [json.loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    if os.path.exists(path):
        return [json.loads(l) for l in open(path) if l.startswith("{")]
    return []


def host_of(d, runs):
    m = re.search(r"aifoundry\d", d)
    return m.group(0) if m else (runs[0]["host"] if runs else os.path.basename(d))


def bursts(d, leak=True):
    tel, runs, marks = jl(os.path.join(d, "telemetry.jsonl")), jl(os.path.join(d, "runs.jsonl")), jl(os.path.join(d, "marks.jsonl"))
    host = host_of(d, runs)
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    w = np.array([s["board_w"] for s in tel])
    T = np.array([s["temp_c"]["minshire"][0] for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    took = np.array([s.get("took_ms", 0) for s in tel])
    noc = np.array([s["sp"]["noc_w"][0] for s in tel])
    sram = np.array([s["sp"]["sram_w"][0] for s in tel])
    minion = np.array([s["sp"]["minion_w"][0] for s in tel])
    busy_other = np.zeros(len(t), bool)   # prefill and heater windows, padded
    for m in marks:
        busy_other |= (t >= m["t_start_ms"] / 1000.0 - 0.2) & (t <= m["t_end_ms"] / 1000.0 + 0.6)
    groups = collections.OrderedDict()
    for r in runs:
        groups.setdefault((r["cfg"], r["pass"]), []).append(r)
    bl = sorted(((k, rs, min(r["t_start_ms"] for r in rs) / 1000.0, max(r["t_end_ms"] for r in rs) / 1000.0)
                 for k, rs in groups.items()), key=lambda b: b[2])
    out, dropped = [], []
    for i, (k, rs, lo, hi) in enumerate(bl):
        prev_hi = bl[i - 1][3] if i else t[0]
        next_lo = bl[i + 1][2] if i + 1 < len(bl) else t[-1]
        busy = (t >= lo + 0.5) & (t <= hi)
        before = (t >= max(prev_hi + 2.0, lo - 3.5)) & (t <= lo - 0.3) & ~busy_other
        after = (t >= hi + 0.5) & (t <= min(next_lo - 0.3, hi + 3.8)) & ~busy_other
        rail_idle = (t >= max(prev_hi + 3.0, lo - 2.5)) & (t <= lo - 0.3) & ~busy_other
        win = (t >= lo) & (t <= hi)
        if win.sum() and np.median(took[win]) > 60:   # a starved service processor also leaves too few samples
            dropped.append({"cfg": k[0], "pass": k[1], "why": "service processor starved",
                            "median_took_ms": float(np.median(took[win])), "max_took_ms": float(took[win].max()), "samples": int(win.sum())})
            continue
        if busy.sum() < 5 or before.sum() < 4:
            dropped.append({"cfg": k[0], "pass": k[1], "why": "too few samples"})
            continue
        if not (mhz[busy | before | after] == 600).all():
            dropped.append({"cfg": k[0], "pass": k[1], "why": "clock left 600 MHz"})
            continue
        if np.median(took[busy]) > 60:
            dropped.append({"cfg": k[0], "pass": k[1], "why": "service processor starved"})
            continue
        idle_b = float(w[before].mean())
        idle_a = float(w[after].mean()) if after.sum() >= 4 else float("nan")
        idle = idle_b if np.isnan(idle_a) else 0.5 * (idle_b + idle_a)
        Tb = float(T[busy].mean())
        Ti = float(np.concatenate([T[before], T[after]]).mean()) if after.sum() >= 4 else float(T[before].mean())
        over_raw = float(w[busy].mean()) - idle
        over = over_raw - (leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti) if leak else 0.0)
        wall = hi - lo
        by = sum(r["bytes"] for r in rs)
        devs = sum(r["cycles_max"] for r in rs) / 0.6e9
        tail = (t >= hi - 0.6) & (t <= hi)
        rails = {}
        for name, v in (("noc_w", noc), ("sram_w", sram), ("minion_w", minion)):
            rails[name] = float((v[tail].mean() - v[rail_idle].mean()) / 0.94) if rail_idle.sum() >= 3 and tail.sum() else None
        r0 = rs[0]
        out.append({"host": host, "cfg": k[0], "pass": k[1], "operands": r0["operands"], "scp": r0["scp"],
                    # --pairs runs (wsep) record hop_distance 0; their pairs are all exactly mean_hops apart
                    "hop_distance": r0.get("hop_distance", 0) or int(round(r0.get("mean_hops", 0))),
                    "hop_axis": r0.get("hop_axis", "any"), "mean_hops": r0.get("mean_hops", 0),
                    "participants": r0["participants"], "shires": r0["shires"], "target_map": r0.get("target_map", ""),
                    "launches": len(rs), "wall_s": wall, "bytes": by, "bytes_per_s": by / devs if devs else 0.0,
                    "p_idle_w": idle, "idle_before_w": idle_b, "idle_after_w": idle_a, "over_idle_w": over,
                    "leak_correction_w": over_raw - over, "die_c": Tb,
                    "took_ms_median": float(np.median(took[busy])), "took_ms_max": float(took[busy].max()),
                    "pj_per_byte": over * wall / by * 1e12 if by else None,
                    "rails_over_w": rails,
                    "noc_pj_per_byte": rails["noc_w"] * wall / by * 1e12 if (by and rails["noc_w"] is not None) else None})
    return host, out, dropped


def route(t, r, order="xy"):
    """Directed links from shire t to shire r, dimension-ordered: 'xy' moves in x first."""
    (x, y), (x1, y1) = MESH[t], MESH[r]
    out = []
    for axis in order:
        if axis == "x":
            while x != x1:
                nx = x + (1 if x1 > x else -1)
                out.append(((x, y), (nx, y)))
                x = nx
        else:
            while y != y1:
                ny = y + (1 if y1 > y else -1)
                out.append(((x, y), (x, ny)))
                y = ny
    return out


def link_sharing(target_map, order="xy"):
    """Share of link-hops that sit on a directed link carrying more than one flow, for the data (target -> reader)."""
    flows, readers, per_target = [], set(), collections.Counter()
    for item in filter(None, (target_map or "").split(",")):
        rs, ts = item.split(">")
        r, t = int(rs), int(ts.split("/")[0])
        if r == t or r not in MESH or t not in MESH:
            continue
        flows.append(route(t, r, order))
        readers.add(r)
        per_target[t] += 1
    use = collections.Counter(l for f in flows for l in f)
    tot = sum(len(f) for f in flows)
    return {"shared_link_hop_fraction": (sum(1 for f in flows for l in f if use[l] > 1) / tot) if tot else 0.0,
            "flows": len(flows), "reader_shires": len(readers), "targets_with_two_readers": sum(1 for v in per_target.values() if v > 1)}


def toggles(operands):
    """Expected fraction of bits that differ between two consecutive flits, and the density of ones."""
    if operands.startswith("bern:"):
        p = float(operands[5:])
        return 2 * p * (1 - p), p
    return None, None


def fit_line(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    A = np.vstack([x, np.ones_like(x)]).T
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    n = len(x)
    if n > 2:
        s2 = float(((A @ coef - y) ** 2).sum() / (n - 2))
        cov = s2 * np.linalg.inv(A.T @ A)
        se = np.sqrt(np.diag(cov))
    else:
        se = np.array([float("nan"), float("nan")])
    return {"slope": float(coef[0]), "intercept": float(coef[1]), "slope_se": float(se[0]), "intercept_se": float(se[1]),
            "n": n, "rms": float(np.sqrt(((A @ coef - y) ** 2).mean()))}


def per_pass_slopes(bs, key, hops=(1, 2, 3, 4, 6)):
    """Slope of `key` against hop distance, fitted separately for each pass, so passes are the replicates."""
    by = collections.defaultdict(list)
    for b in bs:
        if b["hop_distance"] in hops and b[key] is not None:
            by[b["pass"]].append((b["hop_distance"], b[key]))
    out = []
    for p, pts in sorted(by.items()):
        if len({h for h, _ in pts}) >= 3:
            out.append(fit_line([h for h, _ in pts], [v for _, v in pts]) | {"pass": p})
    return out


def pool(vals_by_card):
    allv = [v for vs in vals_by_card.values() for v in vs]
    if not allv:
        return None
    per = {h: {"mean": float(np.mean(vs)), "se": float(np.std(vs, ddof=1) / math.sqrt(len(vs))) if len(vs) > 1 else 0.0, "n": len(vs)}
           for h, vs in vals_by_card.items() if vs}
    return {"mean": float(np.mean(allv)), "lo": float(min(allv)), "hi": float(max(allv)), "n": len(allv), "per_card": per}


def analyze(allb, dropped, a):
    hosts = sorted({b["host"] for b in allb})
    by_cfg = collections.defaultdict(list)
    for b in allb:
        by_cfg[b["cfg"]].append(b)

    def family(prefix):
        return {cfg: bs for cfg, bs in by_cfg.items() if cfg.startswith(prefix)}

    out = {"hosts": hosts, "dropped": dropped, "n_bursts": len(allb)}
    # ---- per-configuration summary, pooled and per card
    summ = {}
    for cfg, bs in by_cfg.items():
        summ[cfg] = {"pj_per_byte": pool({h: [b["pj_per_byte"] for b in bs if b["host"] == h] for h in hosts}),
                     "noc_pj_per_byte": pool({h: [b["noc_pj_per_byte"] for b in bs if b["host"] == h and b["noc_pj_per_byte"] is not None] for h in hosts}),
                     "gb_s": float(np.mean([b["bytes_per_s"] for b in bs]) / 1e9), "participants": bs[0]["participants"],
                     "hop_distance": bs[0]["hop_distance"], "operands": bs[0]["operands"], "hop_axis": bs[0]["hop_axis"],
                     "took_ms_max": {h: max(b["took_ms_max"] for b in bs if b["host"] == h) for h in hosts if any(b["host"] == h for b in bs)}}
    out["configs"] = summ

    # ---- slopes per hop for every data pattern: per card, per pass
    def slopes_for(prefix_of_pattern, key):
        res = {}
        for h in hosts:
            bs = [b for cfg, lst in by_cfg.items() if cfg.startswith(prefix_of_pattern) for b in lst if b["host"] == h]
            res[h] = per_pass_slopes(bs, key)
        return res

    patterns = {}
    for p in ("0", "0.1", "0.25", "0.5", "0.75", "0.9", "1"):
        pre = f"wbern/p{p}/"
        tgl, ones = toggles(f"bern:{p}")
        entry = {"p_ones": ones, "toggle": tgl}
        for key in ("pj_per_byte", "noc_pj_per_byte"):
            s = slopes_for(pre, key)
            entry[key] = {"slope": pool({h: [f["slope"] for f in s[h]] for h in hosts}),
                          "intercept": pool({h: [f["intercept"] for f in s[h]] for h in hosts}),
                          "fit_rms": pool({h: [f["rms"] for f in s[h]] for h in hosts})}
        loc = by_cfg.get(f"wbern/p{p}/hop0", [])
        entry["own_scratchpad_pj_per_byte"] = pool({h: [b["pj_per_byte"] for b in loc if b["host"] == h] for h in hosts})
        patterns[f"bern:{p}"] = entry
    for n in (16, 32, 64, 128, 256):
        pre = f"walt/n{n}/"
        entry = {"block_bytes": n}
        for key in ("pj_per_byte", "noc_pj_per_byte"):
            s = {}
            for h in hosts:
                bs = [b for cfg, lst in by_cfg.items() if cfg.startswith(pre) for b in lst if b["host"] == h]
                s[h] = per_pass_slopes(bs, key, hops=(1, 3, 6))
            entry[key] = {"slope": pool({h: [f["slope"] for f in s[h]] for h in hosts}),
                          "intercept": pool({h: [f["intercept"] for f in s[h]] for h in hosts})}
        patterns[f"alt:{n}"] = entry
    s = {}
    for key in ("pj_per_byte", "noc_pj_per_byte"):
        ss = {}
        for h in hosts:
            bs = [b for cfg, lst in by_cfg.items() if cfg.startswith("wlegacy/") for b in lst if b["host"] == h]
            ss[h] = per_pass_slopes(bs, key, hops=(1, 3, 6))
        s[key] = {"slope": pool({h: [f["slope"] for f in ss[h]] for h in hosts}),
                  "intercept": pool({h: [f["intercept"] for f in ss[h]] for h in hosts})}
    patterns["legacy:random"] = s
    out["patterns"] = patterns

    # ---- energy per transition: slope(P) = s0 + e_t * t, per card and pass, and with a ones term
    def transition_fit(key):
        res = {}
        for h in hosts:
            per_pass = collections.defaultdict(list)
            for p in ("0", "0.1", "0.25", "0.5", "0.75", "0.9", "1"):
                bs = [b for cfg, lst in by_cfg.items() if cfg.startswith(f"wbern/p{p}/") for b in lst if b["host"] == h]
                for f in per_pass_slopes(bs, key):
                    per_pass[f["pass"]].append((2 * float(p) * (1 - float(p)), float(p), f["slope"]))
            fits = []
            for pp, pts in sorted(per_pass.items()):
                if len(pts) < 4:
                    continue
                tt = np.array([q[0] for q in pts]); pr = np.array([q[1] for q in pts]); sl = np.array([q[2] for q in pts])
                A = np.vstack([tt, np.ones_like(tt)]).T
                c, *_ = np.linalg.lstsq(A, sl, rcond=None)
                A2 = np.vstack([tt, pr, np.ones_like(tt)]).T
                c2, *_ = np.linalg.lstsq(A2, sl, rcond=None)
                fits.append({"e_t_pj_per_byte_hop": float(c[0]), "s0": float(c[1]), "rms": float(np.sqrt(((A @ c - sl) ** 2).mean())),
                             "with_ones": {"e_t": float(c2[0]), "e_1": float(c2[1]), "s0": float(c2[2])}})
            res[h] = fits
        # per bit: a payload byte is 8 bits, so e_t per byte-hop / 8 is the energy per bit-transition per hop
        return {"e_t_fj_per_bit_transition_hop": pool({h: [f["e_t_pj_per_byte_hop"] / 8 * 1000 for f in res[h]] for h in hosts}),
                "s0_pj_per_byte_hop": pool({h: [f["s0"] for f in res[h]] for h in hosts}),
                "e_1_fj_per_bit_one_hop": pool({h: [f["with_ones"]["e_1"] / 8 * 1000 for f in res[h]] for h in hosts}),
                "e_t_with_ones_fj": pool({h: [f["with_ones"]["e_t"] / 8 * 1000 for f in res[h]] for h in hosts}),
                "fit_rms_pj_per_byte_hop": pool({h: [f["rms"] for f in res[h]] for h in hosts}),
                "per_pass": res}
    out["transition"] = {"board": transition_fit("pj_per_byte"), "noc_rail": transition_fit("noc_pj_per_byte")}

    # ---- the combined model: per-hop slope = s0 + a * (toggle rate) + b * (density of ones), fitted per card and pass
    # over every pattern whose bits are known. v1: wbern (a repeated 512 B image, so consecutive flits can repeat);
    # v2: wu (every line unique, P and 1-P exact complements) and wfrz (one line everywhere: ones, no toggles).
    FRZ_ONES = 244 / 512   # the frozen line's ones (std::mt19937_64 seed 1, 16 words; see run_wire.py)
    SETS = {"v1": [(f"wbern/p{q}/", 2 * float(q) * (1 - float(q)), float(q), (1, 2, 3, 4, 6)) for q in ("0", "0.1", "0.25", "0.5", "0.75", "0.9", "1")],
            "v2": [(f"wu/p{q}/", 2 * float(q) * (1 - float(q)), float(q), (1, 2, 3, 4, 6)) for q in ("0", "0.25", "0.5", "0.75", "1")]
                  + [("wfrz/", 0.0, FRZ_ONES, (1, 3, 6))]}

    def model_fit(defs, key):
        res = {}
        for h in hosts:
            per_pass = collections.defaultdict(list)
            for pre, tq, pq, hp in defs:
                bs = [b for cfg, lst in by_cfg.items() if cfg.startswith(pre) for b in lst if b["host"] == h]
                for f in per_pass_slopes(bs, key, hops=hp):
                    per_pass[f["pass"]].append((tq, pq, f["slope"], pre))
            fits = []
            for pp, pts in sorted(per_pass.items()):
                if len(pts) < 4:
                    continue
                tt = np.array([q[0] for q in pts]); pr = np.array([q[1] for q in pts]); sl = np.array([q[2] for q in pts])
                A = np.vstack([tt, pr, np.ones_like(tt)]).T
                c, *_ = np.linalg.lstsq(A, sl, rcond=None)
                fits.append({"pass": pp, "a": float(c[0]), "b": float(c[1]), "s0": float(c[2]),
                             "rms": float(np.sqrt(((A @ c - sl) ** 2).mean())),
                             "points": [{"pattern": q[3], "toggle": q[0], "ones": q[1], "slope": q[2], "fit": float(q[0] * c[0] + q[1] * c[1] + c[2])} for q in pts]})
            res[h] = fits
        conv = lambda v: v / 8 * 1000   # pJ per byte-hop -> fJ per bit-hop
        return {"toggle_fj_per_bit_transition_hop": pool({h: [conv(f["a"]) for f in res[h]] for h in hosts}),
                "ones_fj_per_one_bit_hop": pool({h: [conv(f["b"]) for f in res[h]] for h in hosts}),
                "s0_pj_per_byte_hop": pool({h: [f["s0"] for f in res[h]] for h in hosts}),
                "random_bit_fj_per_bit_hop": pool({h: [conv(0.5 * f["a"] + 0.5 * f["b"]) for f in res[h]] for h in hosts}),
                "rms_pj_per_byte_hop": pool({h: [f["rms"] for f in res[h]] for h in hosts}),
                "per_pass": res}
    out["model"] = {st: {"board": model_fit(defs, "pj_per_byte"), "noc_rail": model_fit(defs, "noc_pj_per_byte")} for st, defs in SETS.items()}
    # the complement test, v2: slope(3/4) - slope(1/4) has equal toggles and half a unit of ones; slope(1) - slope(0) a whole unit
    comp = {}
    for key in ("pj_per_byte", "noc_pj_per_byte"):
        d1, d2 = {}, {}
        for h in hosts:
            sl = {}
            for q in ("0", "0.25", "0.75", "1"):
                bs = [b for cfg, lst in by_cfg.items() if cfg.startswith(f"wu/p{q}/") for b in lst if b["host"] == h]
                sl[q] = {f["pass"]: f["slope"] for f in per_pass_slopes(bs, key)}
            d1[h] = [(sl["0.75"][k] - sl["0.25"][k]) / 0.5 / 8 * 1000 for k in sl["0.75"] if k in sl["0.25"]]
            d2[h] = [(sl["1"][k] - sl["0"][k]) / 8 * 1000 for k in sl["1"] if k in sl["0"]]
        comp[key] = {"ones_from_complements_fj": pool(d1), "ones_from_all_ones_vs_zeros_fj": pool(d2)}
    out["complement_test"] = comp
    # disjoint flows (wsep): the data-dependent part of the slope with no link shared, against the same from wu
    # disjoint flows (wsep): no two flows share a link, one reader per target; against the loaded all-pairs set (wu)
    # over the same distances 1-4, so the difference is contention, not distance
    sep = {}
    for key in ("pj_per_byte", "noc_pj_per_byte"):
        ent = {}
        for fam, hp in (("wsep", (1, 2, 3, 4, 5)), ("wu", (1, 2, 3, 4)), ("wsep_d1_4", (1, 2, 3, 4))):
            pre = "wsep" if fam.startswith("wsep") else "wu"
            v5, v0, vd = {}, {}, {}
            for h in hosts:
                s5 = {f["pass"]: f["slope"] for f in per_pass_slopes([b for cfg, lst in by_cfg.items() if cfg.startswith(f"{pre}/p0.5/") for b in lst if b["host"] == h], key, hp)}
                s0_ = {f["pass"]: f["slope"] for f in per_pass_slopes([b for cfg, lst in by_cfg.items() if cfg.startswith(f"{pre}/p0/") for b in lst if b["host"] == h], key, hp)}
                v5[h] = [x / 8 * 1000 for x in s5.values()]
                v0[h] = [x / 8 * 1000 for x in s0_.values()]
                vd[h] = [(s5[k] - s0_[k]) / 8 * 1000 for k in s5 if k in s0_]
            ent[fam] = {"random_fj_per_bit_hop": pool(v5), "zeros_fj_per_bit_hop": pool(v0), "random_minus_zeros_fj_per_bit_hop": pool(vd)}
        sep[key] = ent
    out["disjoint_flows"] = sep

    # ---- direction: x-only and y-only slopes, zeros and P = 0.5
    axes = {}
    for axis in ("x", "y"):
        for p in ("0", "0.5"):
            for key in ("pj_per_byte", "noc_pj_per_byte"):
                ss = {}
                for h in hosts:
                    bs = [b for cfg, lst in by_cfg.items() if cfg.startswith(f"waxis/{axis}/") and cfg.endswith(f"/p{p}") for b in lst if b["host"] == h]
                    ss[h] = per_pass_slopes(bs, key, hops=(1, 2, 3, 4))
                axes.setdefault(f"{axis}/p{p}", {})[key] = {"slope": pool({h: [f["slope"] for f in ss[h]] for h in hosts}),
                                                          "intercept": pool({h: [f["intercept"] for f in ss[h]] for h in hosts})}
    # data-dependent part per axis: slope(P=0.5) - slope(P=0) per random payload bit per hop, over d = 1..3 (at d = 4
    # the axis sets keep only 16-20 of 32 readers and half the bandwidth, and the per-byte difference gets noisy), and
    # the same from the all-pairs set over the same distances for comparison
    for axis, pre5, pre0 in (("x", "waxis/x/", "waxis/x/"), ("y", "waxis/y/", "waxis/y/"), ("all", "wbern/p0.5/", "wbern/p0/")):
        for key in ("pj_per_byte", "noc_pj_per_byte"):
            d = {}
            for h in hosts:
                if axis == "all":
                    b5 = [b for cfg, lst in by_cfg.items() if cfg.startswith(pre5) for b in lst if b["host"] == h]
                    b0 = [b for cfg, lst in by_cfg.items() if cfg.startswith(pre0) for b in lst if b["host"] == h]
                else:
                    b5 = [b for cfg, lst in by_cfg.items() if cfg.startswith(pre5) and cfg.endswith("/p0.5") for b in lst if b["host"] == h]
                    b0 = [b for cfg, lst in by_cfg.items() if cfg.startswith(pre0) and cfg.endswith("/p0") for b in lst if b["host"] == h]
                s5 = {f["pass"]: f["slope"] for f in per_pass_slopes(b5, key, (1, 2, 3))}
                s0 = {f["pass"]: f["slope"] for f in per_pass_slopes(b0, key, (1, 2, 3))}
                d[h] = [(s5[k] - s0[k]) / 8 * 1000 for k in s5 if k in s0]
            axes[f"{axis}/{key}/random_bit_fj_per_bit_hop_d1_3"] = pool(d)
    out["axes"] = axes

    # ---- per millimetre
    if a.pitch_x_mm and a.pitch_y_mm:
        px, py = a.pitch_x_mm, a.pitch_y_mm
        L = math.sqrt(px * py)   # x and y hops mix in the all-pairs sweep; the pitches differ by under 1%
        pm = {"pitch_x_mm": px, "pitch_y_mm": py, "hop_mm": L}
        for st in ("v1", "v2"):
            for src in ("board", "noc_rail"):
                m = out["model"][st][src]
                for k in ("toggle_fj_per_bit_transition_hop", "ones_fj_per_one_bit_hop", "random_bit_fj_per_bit_hop"):
                    if m[k]:
                        pm[f"{st}/{src}/{k.replace('_hop', '_mm')}"] = {q: m[k][q] / L for q in ("mean", "lo", "hi")}
                if m["s0_pj_per_byte_hop"]:
                    pm[f"{st}/{src}/s0_fj_per_bit_mm"] = {q: m["s0_pj_per_byte_hop"][q] / 8 * 1000 / L for q in ("mean", "lo", "hi")}
        out["per_mm"] = pm

    # ---- checks for the report ----------------------------------------------------------------------------------
    ck = {"link_sharing": {}, "per_reader_gb_s": {}, "board_per_rail_w": {}, "d4_off_line": {}, "exit_step_hops": {},
          "wsep_max_off_line": {}, "alt256": {}}
    for cfg, bs in by_cfg.items():
        tm = bs[0].get("target_map", "")
        if tm:
            xy, yx = link_sharing(tm, "xy"), link_sharing(tm, "yx")
            ck["link_sharing"][cfg] = xy | {"shared_link_hop_fraction_yx": yx["shared_link_hop_fraction"]}
            if xy["reader_shires"]:
                ck["per_reader_gb_s"][cfg] = summ[cfg]["gb_s"] / xy["reader_shires"]

    def pooled(cfg, key):
        c = summ.get(cfg)
        v = c.get(key) if c else None
        return v["mean"] if v else None

    # board energy per mesh-rail energy for the mesh's own share: (E(d) - E(0)) on both meters, loaded random set
    for d in (1, 2, 3, 4, 6):
        eb, en = pooled(f"wu/p0.5/hop{d}", "pj_per_byte"), pooled(f"wu/p0.5/hop{d}", "noc_pj_per_byte")
        eb0, en0 = pooled("wu/p0.5/hop0", "pj_per_byte"), pooled("wu/p0.5/hop0", "noc_pj_per_byte")
        if None not in (eb, en, eb0, en0) and en - en0:
            ck["board_per_rail_w"][f"wu/p0.5/hop{d}"] = (eb - eb0) / (en - en0)
    # how far the four-hop point sits off the line through the others, and the step of leaving the shire in hops
    # (intercept of the line over d = 1..6 less the d = 0 value, over the slope)
    for fam, pre in (("wu", "wu/p{}/hop"), ("wbern", "wbern/p{}/hop")):
        for q in ("0", "0.5", "1"):
            for key in ("pj_per_byte", "noc_pj_per_byte"):
                ds = (1, 2, 3, 4, 6)
                E = {dd: pooled(pre.format(q) + str(dd), key) for dd in (0,) + ds}
                if any(E[dd] is None for dd in ds):
                    continue
                ref = [dd for dd in ds if dd != 4]
                f = fit_line(ref, [E[dd] for dd in ref])
                line4 = f["slope"] * 4 + f["intercept"]
                ck["d4_off_line"][f"{fam}/p{q}/{key}"] = (E[4] - line4) / line4
                g = fit_line(ds, [E[dd] for dd in ds])
                if E[0] is not None and g["slope"]:
                    ck["exit_step_hops"][f"{fam}/p{q}/{key}"] = (g["intercept"] - E[0]) / g["slope"]
            if q == "0.5":
                for key in ("pj_per_byte", "noc_pj_per_byte"):
                    ds = (1, 2, 3, 4, 6)
                    E = {dd: (pooled(pre.format("0.5") + str(dd), key), pooled(pre.format("0") + str(dd), key)) for dd in (0,) + ds}
                    if any(None in E[dd] for dd in (0,) + ds):
                        continue
                    g = fit_line(ds, [E[dd][0] - E[dd][1] for dd in ds])
                    ck["exit_step_hops"][f"{fam}/random_minus_zeros/{key}"] = (g["intercept"] - (E[0][0] - E[0][1])) / g["slope"]
    # link-disjoint flows: straightness of the line over d = 1..5, and the exit step against the own-scratchpad read
    for q in ("0", "0.5"):
        for key in ("pj_per_byte", "noc_pj_per_byte"):
            ds = (1, 2, 3, 4, 5)
            E = {dd: pooled(f"wsep/p{q}/hop{dd}", key) for dd in ds}
            E0 = pooled(f"wu/p{q}/hop0", key)
            if any(v is None for v in E.values()):
                continue
            g = fit_line(ds, [E[dd] for dd in ds])
            ck["wsep_max_off_line"][f"wsep/p{q}/{key}"] = max(abs(E[dd] - (g["slope"] * dd + g["intercept"])) / (g["slope"] * dd + g["intercept"]) for dd in ds)
            if E0 is not None and g["slope"]:
                ck["exit_step_hops"][f"wsep/p{q}/{key}"] = (g["intercept"] - E0) / g["slope"]
    # the 256 B block pattern against the 16-128 B level (v1): its excess per hop, as a fraction of every bit flipping
    for key, src in (("pj_per_byte", "board"), ("noc_pj_per_byte", "noc_rail")):
        lv = [patterns[f"alt:{n}"][key]["slope"] for n in (16, 32, 64, 128)]
        top = patterns["alt:256"][key]["slope"]
        m = out["model"]["v1"][src]
        if not top or not all(lv) or not m["toggle_fj_per_bit_transition_hop"]:
            continue
        lvl = float(np.mean([x["mean"] for x in lv]))
        exc = {dd: pooled(f"walt/n256/hop{dd}", key) - float(np.mean([pooled(f"walt/n{n}/hop{dd}", key) for n in (16, 32, 64, 128)])) for dd in (1, 3, 6)}
        a_byte = m["toggle_fj_per_bit_transition_hop"]["mean"] * 8 / 1000
        ck["alt256"][src] = {"level_slope": lvl, "slope": top["mean"], "excess_per_hop": top["mean"] - lvl,
                             "fraction_of_full_flip_per_hop": (top["mean"] - lvl) / a_byte,
                             "excess_pj_per_byte_at_d": exc,
                             "increment_1_to_3": (exc[3] - exc[1]) / 2, "increment_3_to_6": (exc[6] - exc[3]) / 3}
    out["checks"] = ck
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pitch-x-mm", type=float, default=None)
    ap.add_argument("--pitch-y-mm", type=float, default=None)
    ap.add_argument("--no-leak-correction", action="store_true", help="reduce board power without the leakage correction")
    a = ap.parse_args()
    allb, dropped = [], {}
    for d in a.dirs:
        h, bs, dr = bursts(d, leak=not a.no_leak_correction)
        allb += bs
        dropped.setdefault(h, []).extend({**x, "dir": d} for x in dr)
    out = analyze(allb, dropped, a)
    if not a.no_leak_correction:
        # the same model without the leakage correction of board power: how much the method moves the coefficients
        nb = []
        for d in a.dirs:
            nb += bursts(d, leak=False)[1]
        alt = analyze(nb, {}, a)
        keys = ("toggle_fj_per_bit_transition_hop", "ones_fj_per_one_bit_hop", "s0_pj_per_byte_hop", "random_bit_fj_per_bit_hop")
        out["sensitivity"] = {"no_leak_correction": {st: {src: {k: ({q: alt["model"][st][src][k][q] for q in ("mean", "lo", "hi")}
                                                                    | {"per_card": {h: c["mean"] for h, c in alt["model"][st][src][k]["per_card"].items()}})
                                                                if alt["model"][st][src][k] else None for k in keys}
                                                          for src in ("board", "noc_rail")} for st in ("v1", "v2")}}
    json.dump(out, open(a.out, "w"), indent=1)
    patterns, axes = out["patterns"], out["axes"]

    # ---- printout
    print(f"bursts kept: {len(allb)}; dropped: " + ", ".join(f"{h} {len(v)}" for h, v in dropped.items()))
    for k, e in patterns.items():
        if k.startswith("bern:"):
            s_ = e["pj_per_byte"]["slope"]; n_ = e["noc_pj_per_byte"]["slope"]
            if s_:
                print(f"{k:9s} toggle {e['toggle']:.3f}  slope {s_['mean']:.3f} pJ/B/hop [{s_['lo']:.3f}-{s_['hi']:.3f}]"
                      + (f"   noc rail {n_['mean']:.3f}" if n_ else "") + "   " + "  ".join(f"{h} {c['mean']:.3f}±{c['se']:.3f}" for h, c in s_["per_card"].items()))
    for k, e in patterns.items():
        if k.startswith("alt:") and e["pj_per_byte"]["slope"]:
            s_ = e["pj_per_byte"]["slope"]
            print(f"{k:9s} slope {s_['mean']:.3f} pJ/B/hop [{s_['lo']:.3f}-{s_['hi']:.3f}]")
    lg = patterns["legacy:random"]["pj_per_byte"]["slope"]
    if lg:
        print(f"legacy random slope {lg['mean']:.3f} pJ/B/hop [{lg['lo']:.3f}-{lg['hi']:.3f}]")
    for src in ("board", "noc_rail"):
        tr = out["transition"][src]
        if tr["e_t_fj_per_bit_transition_hop"]:
            e = tr["e_t_fj_per_bit_transition_hop"]
            print(f"{src}: energy per bit-transition per hop {e['mean']:.1f} fJ [{e['lo']:.1f}-{e['hi']:.1f}]  "
                  + "  ".join(f"{h} {c['mean']:.1f}±{c['se']:.1f}" for h, c in e["per_card"].items())
                  + (f";  ones term {tr['e_1_fj_per_bit_one_hop']['mean']:.1f} fJ" if tr["e_1_fj_per_bit_one_hop"] else ""))
    for axis in ("x", "y", "all"):
        for key in ("pj_per_byte", "noc_pj_per_byte"):
            e = axes.get(f"{axis}/{key}/random_bit_fj_per_bit_hop_d1_3")
            if e:
                print(f"axis {axis:3s} {key:16s}: random - zeros {e['mean']:.1f} fJ per bit per hop [{e['lo']:.1f}-{e['hi']:.1f}] (d = 1-3)")
    for st in ("v1", "v2"):
        for src in ("board", "noc_rail"):
            m = out["model"][st][src]
            if m["toggle_fj_per_bit_transition_hop"]:
                a_, b_, r_ = m["toggle_fj_per_bit_transition_hop"], m["ones_fj_per_one_bit_hop"], m["random_bit_fj_per_bit_hop"]
                print(f"model {st} {src:8s}: per transition {a_['mean']:6.1f} fJ/hop [{a_['lo']:.0f}-{a_['hi']:.0f}]   per one {b_['mean']:6.1f} [{b_['lo']:.0f}-{b_['hi']:.0f}]"
                      f"   s0 {m['s0_pj_per_byte_hop']['mean']:.3f} pJ/B/hop   random bit {r_['mean']:.1f} fJ/hop   rms {m['rms_pj_per_byte_hop']['mean']:.3f}")
    for key, v in out["complement_test"].items():
        if v["ones_from_complements_fj"]:
            print(f"complements ({key}): per one {v['ones_from_complements_fj']['mean']:.1f} fJ/hop from 3/4 vs 1/4; {v['ones_from_all_ones_vs_zeros_fj']['mean']:.1f} from 1 vs 0")
    for key, v in out["disjoint_flows"].items():
        for fam, e in v.items():
            if e["random_minus_zeros_fj_per_bit_hop"]:
                print(f"{fam:10s} ({key:15s}): data {e['random_minus_zeros_fj_per_bit_hop']['mean']:6.1f} [{e['random_minus_zeros_fj_per_bit_hop']['lo']:.0f}-{e['random_minus_zeros_fj_per_bit_hop']['hi']:.0f}]"
                      f"  zeros {e['zeros_fj_per_bit_hop']['mean']:6.1f}  random {e['random_fj_per_bit_hop']['mean']:6.1f} fJ/bit/hop   "
                      + "  ".join(f"{h} {c['mean']:.1f}" for h, c in e['random_minus_zeros_fj_per_bit_hop']['per_card'].items()))
    if "per_mm" in out:
        for k, v in out["per_mm"].items():
            if isinstance(v, dict):
                print(f"per mm ({out['per_mm']['hop_mm']:.2f} mm/hop) {k}: {v['mean']:.1f} [{v['lo']:.1f}-{v['hi']:.1f}]")


if __name__ == "__main__":
    main()
