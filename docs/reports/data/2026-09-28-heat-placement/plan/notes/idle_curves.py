#!/usr/bin/env python3
"""Heating and cooling timings from the V3-IDLE blocks (zero card time), for DESIGN2's budget and the L8 check.
Run from R/docs/reports/data/2026-09-25-claims-v3/raw."""
import gzip, json, sys, statistics as st
for card in ("aifoundry3", "aifoundry1-c1", "aifoundry2"):
    for p in (1, 2, 3):
        d = f"{card}/idle/p{p}"
        try:
            marks = [json.loads(l) for l in open(f"{d}/marks.jsonl")]
        except FileNotFoundError:
            continue
        ev = {m["ev"]: m["t_ms"] for m in marks}
        S = [json.loads(l) for l in gzip.open(f"{d}/telemetry.jsonl.gz", "rt") if l.startswith("{")]
        T = [(s["t_ms"], s["temp_c"]["minshire"][0], s["board_w"]) for s in S]
        t0 = ev["cycle_start"]; th = ev["heat_end"]
        # heating: first time mean reads each level after cycle start
        heat = [x for x in T if t0 <= x[0] <= th]
        first = {}
        for t, m, w in heat:
            for lvl in range(50, 95):
                if m >= lvl and lvl not in first:
                    first[lvl] = (t - t0) / 1000
        cool = [x for x in T if x[0] >= th]
        down = {}
        for t, m, w in cool:
            for lvl in range(50, 95):
                if m <= lvl and lvl not in down:
                    down[lvl] = (t - th) / 1000
        idle_w = st.median([w for t, m, w in T if t < t0]) if any(t < t0 for t, m, w in T) else None
        end_w = st.median([w for t, m, w in cool[-50:]])
        hs = " ".join(f"{l}:{first[l]:.1f}" for l in range(55, 70) if l in first)
        cs = " ".join(f"{l}:{down[l]:.0f}" for l in (75, 70, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55) if l in down)
        print(f"{card} p{p}: start {heat[0][1]} C idle_w {idle_w} end_w {end_w:.2f} end_T {cool[-1][1]}")
        print(f"   heat first-read s: {hs}")
        print(f"   cool first-read s after heat_end: {cs}")
# Rise times from each block's own start (the same curves): time until the mean first reads start + k.
# Used in DESIGN2 section 5.1 to compare card 1's heating speed with aifoundry3's at the same rise.
print("rise times from the block's start reading (s):")
for card, p in (("aifoundry3", 1), ("aifoundry3", 2), ("aifoundry3", 3), ("aifoundry1-c1", 1)):
    d = f"{card}/idle/p{p}"
    ev = {json.loads(l)["ev"]: json.loads(l)["t_ms"] for l in open(f"{d}/marks.jsonl")}
    S = [json.loads(l) for l in gzip.open(f"{d}/telemetry.jsonl.gz", "rt") if l.startswith("{")]
    t0, th = ev["cycle_start"], ev["heat_end"]
    h = [((s["t_ms"] - t0) / 1000, s["temp_c"]["minshire"][0], s["board_w"]) for s in S if t0 <= s["t_ms"] <= th]
    T0 = h[0][1]
    ks = " ".join(f"+{k}:{next((t for t, m, w in h if m >= T0 + k), float('nan')):.0f}" for k in (3, 5, 8, 10, 12, 15, 20, 25))
    wl = [w for t, m, w in h if 3 < t < 8]
    print(f"   {card} p{p} start {T0} C, board 3-8 s {sum(wl) / len(wl):.1f} W: {ks}")
