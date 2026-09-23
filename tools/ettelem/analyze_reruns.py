#!/usr/bin/env python3
"""Pool the repeated power measurements that had been made once into confidence bars.

    analyze_reruns.py <rerun-dir> [<rerun-dir> ...] --out reruns.json

Each rerun directory holds relay-pass<k>/, hotline-pass<k>/ (run_onchip_power.sh, run_hotline_power.sh) and
rl-pass<k>/ (run_rings_levels_power.sh: the nocbench rings and the memhier levels), one per pass, from one
card (the host is read from the directory name). Every pass is reduced on its own; the first measurements of 18 and 22
September on aifoundry2 join as passes of their own; then everything is pooled per card and over cards: mean,
the range every pass on every card spanned, each card's mean with its pass-to-pass standard error.

A burst is dropped when the minion clock left 600 MHz inside it (aifoundry2's governor does that below 65 C),
because the bars are meant to hold measurement scatter, not a change of operating point.
"""
import argparse
import glob
import importlib.util
import json
import math
import os
import re
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def stats(vals_by_card):
    allv = [v for vs in vals_by_card.values() for v in vs]
    per = {h: {"mean": float(np.mean(vs)), "se": float(np.std(vs, ddof=1) / math.sqrt(len(vs))) if len(vs) > 1 else 0.0, "n": len(vs)}
           for h, vs in vals_by_card.items() if vs}
    return {"mean": float(np.mean(allv)), "lo": float(min(allv)), "hi": float(max(allv)), "n": len(allv), "per_card": per} if allv else None


A_LEAK_80, T_L = 23.257, 36.0


def leak_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def complete(pd):
    """A pass counts only if its runner finished (its log ends with 'done') and its sampler ran: the sampler
    failed to start in about one pass in three before run_*_power.sh learnt to retry, leaving no telemetry."""
    import gzip
    log = pd + ".log"
    if not (os.path.exists(log) and open(log).read().rstrip().endswith("done")):
        return False
    tp = os.path.join(pd, "telemetry.jsonl")
    if not (os.path.exists(tp) or os.path.exists(tp + ".gz")):
        return False
    op = (lambda q: gzip.open(q + ".gz", "rt")) if os.path.exists(tp + ".gz") else open
    return sum(1 for _ in op(tp)) > 300


def reduce_dir(pd):
    """Bursts of one pass: label -> over-idle W (bracketing idle, corrected for the warmer burst's leakage), rate."""
    import gzip
    tp = os.path.join(pd, "telemetry.jsonl")
    op = (lambda q: gzip.open(q + ".gz", "rt")) if os.path.exists(tp + ".gz") else open
    tel = [json.loads(l) for l in op(tp) if l.startswith("{")]
    runs = [json.loads(l) for l in open(os.path.join(pd, "runs.jsonl"))]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    w = np.array([s["board_w"] for s in tel])
    T = np.array([s["temp_c"]["minshire"][0] for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    took = np.array([s.get("took_ms", 0) for s in tel])
    labels = []
    for r in runs:
        if r["label"] not in labels:
            labels.append(r["label"])
    spans = {lab: (min(r["t_start_ms"] for r in runs if r["label"] == lab) / 1000.0,
                   max(r["t_end_ms"] for r in runs if r["label"] == lab) / 1000.0) for lab in labels}
    out = {}
    for i, lab in enumerate(labels):
        lo, hi = spans[lab]
        busy = (t >= lo + 0.5) & (t <= hi)
        prev_hi = spans[labels[i - 1]][1] if i else t[0]
        next_lo = spans[labels[i + 1]][0] if i + 1 < len(labels) else t[-1]
        before = (t >= max(prev_hi + 3.0, lo - 6.0)) & (t <= lo - 0.3)
        after = (t >= hi + 3.0) & (t <= min(next_lo - 0.3, hi + 8.0))
        if busy.sum() < 5 or before.sum() < 5:
            continue
        moved = float((mhz[busy | before | after] != 600).mean())
        # The service processor itself can be starved by mesh traffic through the IO shire's row (the s <-> s+16
        # rings): its command latency goes from 22 ms to 150 ms and the board reading is held for seconds at a
        # time, so the burst's power is not a measurement. Flag by the sampler's own latency.
        starved = float(np.median(took[busy])) if busy.sum() else 0.0
        idle = float(w[before].mean()) if after.sum() < 5 else 0.5 * (float(w[before].mean()) + float(w[after].mean()))
        Tb = float(T[busy].mean())
        Ti = float(np.concatenate([T[before], T[after]]).mean()) if after.sum() >= 5 else float(T[before].mean())
        over = float(w[busy].mean()) - idle - leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti)
        rs = [r for r in runs if r["label"] == lab]
        out[lab] = {"over_idle_w": over, "wall_s": hi - lo, "runs": rs, "die_c": Tb, "clock_moved_frac": moved, "sampler_median_ms": starved}
    return out


def host_of(d):
    m = re.search(r"aifoundry\d", d)
    return m.group(0) if m else os.path.basename(d)


# The first measurements of the relay and the hot line, one pass each, which the manual's first edition
# printed alone: the same bursts sampled the same way, so they pool with the reruns. The rings and levels of
# 18 September were sampled without the die temperature (run_energy.py) and are not pooled: run_rings_levels_power.sh
# repeats them the manual's way.
FIRST = {
    "relay": ("docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json", "aifoundry2"),
    "hotline": ("docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json", "aifoundry2"),
}
LEVELS = {"l1", "l2", "l3", "dram", "scp-local", "scp-remote"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-first", action="store_true", help="leave out the 18 and 22 September measurements")
    a = ap.parse_args()
    relay, hot, rings, levels = {}, {}, {}, {}
    dropped, passes = [], {"relay": 0, "hotline": 0, "rings": 0, "levels": 0}
    for d in a.dirs:
        host = host_of(d)
        for pd in sorted(glob.glob(os.path.join(d, "relay-pass*[0-9]"))):
            if not complete(pd):
                continue
            passes["relay"] += 1
            for lab, b in reduce_dir(pd).items():
                if b["clock_moved_frac"] > 0.02 or b["sampler_median_ms"] > 60:
                    dropped.append({"pass": pd, "burst": lab, "clock_moved_frac": b["clock_moved_frac"], "sampler_median_ms": b["sampler_median_ms"]})
                    continue
                total = sum(r["bytes"] for r in b["runs"])
                relay.setdefault(lab, {}).setdefault(host, []).append(b["over_idle_w"] * b["wall_s"] / total * 1e12)
        for pd in sorted(glob.glob(os.path.join(d, "hotline-pass*[0-9]"))):
            if not complete(pd):
                continue
            passes["hotline"] += 1
            for lab, b in reduce_dir(pd).items():
                if b["clock_moved_frac"] > 0.02 or b["sampler_median_ms"] > 60:
                    dropped.append({"pass": pd, "burst": lab, "clock_moved_frac": b["clock_moved_frac"], "sampler_median_ms": b["sampler_median_ms"]})
                    continue
                rate = sum(r["total_ops"] for r in b["runs"]) / sum(r["wall_s"] for r in b["runs"])
                hot.setdefault(lab, {}).setdefault(host, []).append(b["over_idle_w"] / rate * 1e9)
        for pd in sorted(glob.glob(os.path.join(d, "rl-pass*[0-9]"))):   # rings and levels, ettelem-sampled
            if not complete(pd):
                continue
            passes["rings"] += 1; passes["levels"] += 1
            for lab, b in reduce_dir(pd).items():
                if b["clock_moved_frac"] > 0.02 or b["sampler_median_ms"] > 60:
                    dropped.append({"pass": pd, "burst": lab, "clock_moved_frac": b["clock_moved_frac"], "sampler_median_ms": b["sampler_median_ms"]})
                    continue
                total = sum(r["bytes"] for r in b["runs"])
                if not total:
                    continue
                store = levels if lab in LEVELS else rings
                store.setdefault(lab, {}).setdefault(host, []).append(b["over_idle_w"] * b["wall_s"] / total * 1e12)
    if not a.no_first:
        p, h = FIRST["relay"]
        for m in json.load(open(os.path.join(ROOT, p)))["power"]["media"]:
            relay.setdefault(m["medium"], {}).setdefault(h, []).append(m["pj_per_byte"])
        p, h = FIRST["hotline"]
        for r in json.load(open(os.path.join(ROOT, p)))["power"]["runs"]:
            hot.setdefault(r["label"], {}).setdefault(h, []).append(r["nj_per_op"])
        passes["relay"] += 1; passes["hotline"] += 1
    out = {"relay_pj_per_byte": {m: stats(v) for m, v in relay.items()},
           "hotline_nj_per_op": {l: stats(v) for l, v in hot.items()},
           "rings_pj_per_byte": {c: stats(v) for c, v in rings.items()},
           "levels_pj_per_byte": {c: stats(v) for c, v in levels.items()},
           "passes": passes, "dropped": dropped, "dirs": a.dirs,
           "first_included": not a.no_first,
           "method": "each pass reduced on its own (bracketing idle, leakage-corrected); bursts with the minion clock off 600 MHz, or with the service processor starved (sampler median latency > 60 ms), dropped; pooled over passes and cards"}
    json.dump(out, open(a.out, "w"), indent=1)
    for sec, unit in (("relay_pj_per_byte", "pJ/B"), ("hotline_nj_per_op", "nJ"), ("rings_pj_per_byte", "pJ/B"), ("levels_pj_per_byte", "pJ/B")):
        for k, v in out[sec].items():
            if v:
                print(f"{sec.split('_')[0]:7s} {k:14s} {v['mean']:8.2f} {unit} [{v['lo']:.2f}-{v['hi']:.2f}] n={v['n']}  " +
                      "  ".join(f"{h} {c['mean']:.2f}±{c['se']:.2f} (n={c['n']})" for h, c in v["per_card"].items()))
    print("passes", passes, "dropped", len(dropped))


if __name__ == "__main__":
    main()
