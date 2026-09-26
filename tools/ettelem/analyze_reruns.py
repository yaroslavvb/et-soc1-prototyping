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

    analyze_reruns.py <rerun-dir> [...] --v3-rl docs/reports/data/2026-09-25-claims-v3/raw --out reruns.json

--v3-rl (26 September 2026) takes the relay, the rings and the levels from the version-3 check's V3-RL passes instead:
<dir>/<card>/rl/p<K>/ for every card directory present (aifoundry2, aifoundry3, aifoundry1-c1), a pass used when its
block.json says ok (never a p<K>.attempt-* directory, never a dry run), each of its three halves (A: rings, B: levels,
relay) reduced by reduce_dir() on its own, with the same burst rule; the card is the directory's name. Its two ABBA bursts
per level (l2-1 and l2-2, scp-local-1 and scp-local-2) give the level the mean of the kept ones, one value per pass, as
tools/claims-v3/rl/reduce.py does. Each V3-RL pass prefills the own scratchpad with zeros (odd passes) or random data (even
passes) before the scp-local bursts (pass.json "contents"), so levels_by_contents_pj_per_byte repeats the levels split by
that pass's contents. The rerun directories then supply the hot line only (and the 22 September hot line joins as before);
their relay and rl passes, and the 22 September relay, are not used, except that a ring or a level with no kept V3-RL burst
on any card keeps its rerun passes (on aifoundry2, aifoundry3 and aifoundry1-c1 the s <-> s+16 ring starved the sampler in
every V3-RL pass, 63-141 ms, so that ring keeps aifoundry3's 23 September passes).
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
        # rings): its command latency goes from 22 ms to 76-146 ms (per-pass medians) and the board reading takes a new
        # value about twice a second instead of six times, so the burst's power is not a measurement. Flag by the sampler's own latency.
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
    "hotline": ("docs/reports/data/2026-09-22-hotline-aifoundry2/power.json", "aifoundry2"),   # the same runs as hotline.json's power block
}
LEVELS = {"l1", "l2", "l3", "dram", "scp-local", "scp-remote"}
# V3-RL's ABBA labels, merged into their level (the mean of the kept bursts of a pass, as tools/claims-v3/rl/reduce.py)
V3_LABEL = {"l2-1": "l2", "l2-2": "l2", "scp-local-1": "scp-local", "scp-local-2": "scp-local"}


def v3_rl_passes(root):
    """(card, pass, contents, pass dir) for every used V3-RL pass under root/<card>/rl/p<K>/ (block.json ok)."""
    out = []
    for card in sorted(os.listdir(root)):
        base = os.path.join(root, card, "rl")
        if not os.path.isdir(base):
            continue
        for name in os.listdir(base):
            m = re.fullmatch(r"p(\d+)", name)
            if not m:
                continue                       # p<K>.attempt-*: set aside by the queue, never used
            pd = os.path.join(base, name)
            try:
                bj = json.load(open(os.path.join(pd, "block.json")))
                pj = json.load(open(os.path.join(pd, "pass.json")))
            except (OSError, ValueError):
                continue
            if bj.get("status") != "ok" or pj.get("dry"):
                continue
            out.append((card, int(m.group(1)), pj.get("contents"), pd))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-first", action="store_true", help="leave out the 18 and 22 September measurements")
    ap.add_argument("--v3-rl", help="the version-3 raw directory: relay, rings and levels from its V3-RL passes")
    a = ap.parse_args()
    relay, hot, rings, levels = {}, {}, {}, {}
    by_contents = {}                   # V3-RL only: contents -> level -> card -> [pass values]
    per_card_passes = {}               # V3-RL only: section -> card -> passes used
    hotw = {}   # the hot line's watts over idle, per label: the stalled power the energy manual quotes
    dropped, passes = [], {"relay": 0, "hotline": 0, "rings": 0, "levels": 0}
    fb_rings, fb_levels = {}, {}       # the rerun directories' rings and levels, kept only where V3-RL has none
    if a.v3_rl:
        for card, k, contents, pd in v3_rl_passes(a.v3_rl):
            for half, sec in (("relay", "relay"), ("A", "rings"), ("B", "levels")):
                hd = os.path.join(pd, half)
                vals = {}
                for lab, b in reduce_dir(hd).items():
                    if b["clock_moved_frac"] > 0.02 or b["sampler_median_ms"] > 60:
                        dropped.append({"pass": hd, "burst": lab, "clock_moved_frac": b["clock_moved_frac"],
                                        "sampler_median_ms": b["sampler_median_ms"]})
                        continue
                    total = sum(r["bytes"] for r in b["runs"])
                    if not total:
                        continue                      # the spin brackets move no bytes
                    key = V3_LABEL.get(lab, lab)
                    vals.setdefault(key, []).append(b["over_idle_w"] * b["wall_s"] / total * 1e12)
                passes[sec] += 1
                per_card_passes.setdefault(sec, {}).setdefault(card, []).append(k)
                store = {"relay": relay, "rings": rings, "levels": levels}[sec]
                for key, v in vals.items():
                    store.setdefault(key, {}).setdefault(card, []).append(float(np.mean(v)))
                    if sec == "levels" and contents:
                        by_contents.setdefault(contents, {}).setdefault(key, {}).setdefault(card, []).append(float(np.mean(v)))
    for d in a.dirs:
        host = host_of(d)
        for pd in ([] if a.v3_rl else sorted(glob.glob(os.path.join(d, "relay-pass*[0-9]")))):
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
                hotw.setdefault(lab, {}).setdefault(host, []).append(b["over_idle_w"])
        for pd in sorted(glob.glob(os.path.join(d, "rl-pass*[0-9]"))):   # rings and levels, ettelem-sampled
            if not complete(pd):
                continue
            if not a.v3_rl:
                passes["rings"] += 1; passes["levels"] += 1
            for lab, b in reduce_dir(pd).items():
                if b["clock_moved_frac"] > 0.02 or b["sampler_median_ms"] > 60:
                    dropped.append({"pass": pd, "burst": lab, "clock_moved_frac": b["clock_moved_frac"], "sampler_median_ms": b["sampler_median_ms"]})
                    continue
                total = sum(r["bytes"] for r in b["runs"])
                if not total:
                    continue
                store = (fb_levels if lab in LEVELS else fb_rings) if a.v3_rl else (levels if lab in LEVELS else rings)
                store.setdefault(lab, {}).setdefault(host, []).append(b["over_idle_w"] * b["wall_s"] / total * 1e12)
    fallback = {}
    if a.v3_rl:   # a ring or level with no kept V3-RL burst on any card keeps its rerun passes
        for store, fb, sec in ((rings, fb_rings, "rings"), (levels, fb_levels, "levels")):
            for lab, v in fb.items():
                if not store.get(lab):
                    store[lab] = v
                    fallback[lab] = {"section": sec, "cards": sorted(v), "from": "the rerun directories (23 September)",
                                     "why": "no kept V3-RL burst on any card"}
    if not a.no_first:
        if not a.v3_rl:
            p, h = FIRST["relay"]
            for m in json.load(open(os.path.join(ROOT, p)))["power"]["media"]:
                relay.setdefault(m["medium"], {}).setdefault(h, []).append(m["pj_per_byte"])
        p, h = FIRST["hotline"]
        for r in json.load(open(os.path.join(ROOT, p)))["runs"]:
            hot.setdefault(r["label"], {}).setdefault(h, []).append(r["nj_per_op"])
            hotw.setdefault(r["label"], {}).setdefault(h, []).append(r["over_idle_w"])
        passes["hotline"] += 1
        if not a.v3_rl:
            passes["relay"] += 1
    out = {"relay_pj_per_byte": {m: stats(v) for m, v in relay.items()},
           "hotline_nj_per_op": {l: stats(v) for l, v in hot.items()},
           "hotline_over_idle_w": {l: stats(v) for l, v in hotw.items()},
           "rings_pj_per_byte": {c: stats(v) for c, v in rings.items()},
           "levels_pj_per_byte": {c: stats(v) for c, v in levels.items()},
           "passes": passes, "dropped": dropped, "dirs": a.dirs,
           "first_included": not a.no_first,
           **({"v3_rl": a.v3_rl,
               "levels_by_contents_pj_per_byte": {c: {k: stats(v) for k, v in lv.items()} for c, lv in sorted(by_contents.items())},
               "passes_per_card": {sec: {c: sorted(ks) for c, ks in d.items()} for sec, d in per_card_passes.items()},
               "fallback_23sep": fallback} if a.v3_rl else {}),
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
