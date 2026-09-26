#!/usr/bin/env python3
"""V3-RL pass quality: the 600 MHz rules and the idle clock of one pass. block.sh runs it after the relay, and
reduce.py uses the same windows. It reads files only, never the card, and needs no numpy.

    python3 tools/claims-v3/rl/quality.py <pass dir> [--scope all|busy|none]

Every telemetry sample of a half (A, B, relay; telemetry.jsonl[.gz] against runs.jsonl) falls in one window:
  busy     inside a burst's window, as reduce.py's reduce_dir takes it: [first run start + 0.5 s, last run end] of
           each label. There is one exception, the launch gaps. When two consecutive launches of a burst are more
           than 50 ms apart, the samples from the end of one launch to 50 ms after the start of the next are "gap"
           samples, not busy ones. Only the relay has such gaps (separate processes, about 190 ms apart on
           aifoundry2 and 230 ms on aifoundry3); ring and level kernels follow each other within 6 ms. The 50 ms
           covers the launch latency only (the host stamps t_start_ms just before the kernel launch): a kernel that
           still runs below 600 MHz after that is a busy sample off 600 MHz and counts (a card waking from a
           low-power state inside a kernel is caught, not excused; with 300 ms a third of every relay kernel went
           unchecked);
  gap      those launch gaps: the card between two processes, which on aifoundry1's card 0 may be its idle state;
  bracket  reduce_dir's idle brackets, [max(prev end + 3, start - 6), start - 0.3] and
           [end + 3, min(next start - 0.3, end + 8)];
  other    everything else: the lead and tail, the prefills, and each launch's first 0.5 s.

The pass-level 600 MHz rule (--scope), fixed per card (README "Cards"):
  all   any sample of the pass off 600 MHz fails the pass (aifoundry2, registered: PLAN3's common rule);
  busy  any busy sample off 600 MHz fails it (the governor-free cards added on 25 Sep, aifoundry1-c0 and -c1).
        The idle brackets and launch gaps are recorded, never counted: card 0 idles at 300 MHz;
  none  the count is recorded only (aifoundry3, pinned at 600 MHz; reduce.py's burst rule applies).
A sample with no clock field counts as off 600 MHz (as the block's grep count and reduce.py's count do).

Output on stdout: one JSON object. It has the counts, and for each window the clock (MHz -> samples) and the median
minion die voltage, per half and over the pass. It also has "idle_clock_mhz" (the brackets' most common clock),
"fail": true|false and "why".
"""
import argparse
import gzip
import json
import os
import sys

HALVES = ("A", "B", "relay")
GAP_S, SETTLE_S = 0.05, 0.05   # a launch gap: launches > 50 ms apart; it ends 50 ms after the next launch starts
WINDOWS = ("busy", "gap", "bracket", "other")


def read_half(hd):
    """(samples, runs) of one half; empty lists when a file is missing or empty (a dry run, a half that never ran)."""
    tp = os.path.join(hd, "telemetry.jsonl")
    tel, runs = [], []
    src = tp + ".gz" if os.path.exists(tp + ".gz") else tp if os.path.exists(tp) else None
    if src:
        with (gzip.open(src, "rt") if src.endswith(".gz") else open(src)) as f:
            for line in f:
                if line.startswith("{"):
                    try:
                        tel.append(json.loads(line))
                    except ValueError:
                        pass
    rp = os.path.join(hd, "runs.jsonl")
    if os.path.exists(rp):
        with open(rp) as f:
            for line in f:
                if line.startswith("{"):
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    if "t_start_ms" in r and "t_end_ms" in r and "label" in r:
                        runs.append(r)
    return tel, runs


def sample_windows(t, runs):
    """The window of every sample time t (seconds): 'busy', 'gap', 'bracket' or 'other' (see the module text)."""
    labels = []
    for r in runs:
        if r["label"] not in labels:
            labels.append(r["label"])
    spans = {lab: (min(r["t_start_ms"] for r in runs if r["label"] == lab) / 1000.0,
                   max(r["t_end_ms"] for r in runs if r["label"] == lab) / 1000.0) for lab in labels}
    cls = ["other"] * len(t)
    if not t:
        return cls
    for i, lab in enumerate(labels):
        lo, hi = spans[lab]
        prev_hi = spans[labels[i - 1]][1] if i else t[0]
        next_lo = spans[labels[i + 1]][0] if i + 1 < len(labels) else t[-1]
        b0, b1 = max(prev_hi + 3.0, lo - 6.0), lo - 0.3
        a0, a1 = hi + 3.0, min(next_lo - 0.3, hi + 8.0)
        for k, x in enumerate(t):
            if cls[k] == "other" and (b0 <= x <= b1 or a0 <= x <= a1):
                cls[k] = "bracket"
    for lab in labels:
        lo, hi = spans[lab]
        rs = sorted((r for r in runs if r["label"] == lab), key=lambda r: r["t_start_ms"])
        gaps = [(a["t_end_ms"] / 1000.0, b["t_start_ms"] / 1000.0 + SETTLE_S) for a, b in zip(rs, rs[1:])
                if (b["t_start_ms"] - a["t_end_ms"]) / 1000.0 > GAP_S]
        for k, x in enumerate(t):
            if lo + 0.5 <= x <= hi:
                cls[k] = "gap" if any(g0 < x <= g1 for g0, g1 in gaps) else "busy"
    return cls


def clock_of(s):
    try:
        return int(s["mhz"]["minion"])
    except (KeyError, TypeError, ValueError):
        return None


def mv_of(s):
    try:
        return int(s["die_mv"]["minion"])
    except (KeyError, TypeError, ValueError):
        return None


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else 0.5 * (xs[m - 1] + xs[m])


def summarize_half(hd):
    tel, runs = read_half(hd)
    t = [s.get("t_ms", 0) / 1000.0 for s in tel]
    cls = sample_windows(t, runs)
    out = {"samples": len(tel), "off600": sum(1 for s in tel if clock_of(s) != 600)}
    for w in WINDOWS:
        ss = [s for s, c in zip(tel, cls) if c == w]
        hist = {}
        for s in ss:
            k = str(clock_of(s))          # "None" for a sample without a clock field
            hist[k] = hist.get(k, 0) + 1
        out[w] = {"n": len(ss), "off600": sum(1 for s in ss if clock_of(s) != 600),
                  "clock_mhz": dict(sorted(hist.items())), "minion_mv_median": median(mv_of(s) for s in ss)}
    return out


def mode_clock(hist):
    hist = {k: v for k, v in hist.items() if k != "None"}
    return int(max(hist, key=lambda k: (hist[k], k))) if hist else None


def summarize(pd, scope="all"):
    halves = {h: summarize_half(os.path.join(pd, h)) for h in HALVES if os.path.isdir(os.path.join(pd, h))}
    tot = {"samples": sum(x["samples"] for x in halves.values()), "off600": sum(x["off600"] for x in halves.values())}
    for w in WINDOWS:
        hist, mvs = {}, []
        for x in halves.values():
            for k, v in x[w]["clock_mhz"].items():
                hist[k] = hist.get(k, 0) + v
        tot[w] = {"n": sum(x[w]["n"] for x in halves.values()), "off600": sum(x[w]["off600"] for x in halves.values()),
                  "clock_mhz": dict(sorted(hist.items())),
                  # the median of the halves' medians: enough to tell a 398 mV idle from a 518 mV one
                  "minion_mv_median": median(x[w]["minion_mv_median"] for x in halves.values())}
    fail, why = False, ""
    if scope == "all" and tot["off600"] > 0:
        fail, why = True, f"{tot['off600']} of {tot['samples']} samples off 600 MHz (rule: any sample)"
    elif scope == "busy" and tot["busy"]["off600"] > 0:
        fail, why = True, f"{tot['busy']['off600']} of {tot['busy']['n']} busy samples off 600 MHz (rule: busy samples)"
    return {"scope": scope, **tot, "idle_clock_mhz": mode_clock(tot["bracket"]["clock_mhz"]),
            "busy_clock_mhz": mode_clock(tot["busy"]["clock_mhz"]), "by_half": halves, "fail": fail, "why": why}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pass_dir")
    ap.add_argument("--scope", choices=("all", "busy", "none"), default="all")
    a = ap.parse_args()
    json.dump(summarize(a.pass_dir, a.scope), sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
