#!/usr/bin/env python3
"""Reproduce every [derived] number in feasibility.md from committed repo data (no card access).

    python3 derive_feasibility.py [/path/to/et-soc1-pages]

D1  per card, all version-3 telemetry: minion clock histogram, the SP's since-boot max clock, lowest mean reading,
    busy samples (board > 45 W) at a mean reading <= 65 C, and cool+under-TDP samples (mean <= 64, 45 < board < 63 W)
D2  per card: die reading at block start / end over every version-3 block.json
D3  per card, V3-IDLE cycles: start reading, time to first mean > 65 C, bursts and seconds to the heat target,
    highest mean and peak-hold high, max board W, reading after 900 s of cooling
D4  per card, V3-IDLE heater processes: duration, gap, return codes
D5  E10 (21 Sep, aifoundry2): per run, first sample above 650 MHz and first down-step after it
D6  aifoundry2's hottest version-3 block (cat p11)
D7  sp.system_c (the PMIC system-temperature slot) over all version-3 telemetry
"""
import collections
import glob
import gzip
import json
import os
import statistics
import sys

R = sys.argv[1] if len(sys.argv) > 1 else "/home/yaroslavvb/claude/et-soc1-pages"
V3 = os.path.join(R, "docs/reports/data/2026-09-25-claims-v3/raw")
H = os.path.join(R, "docs/reports/data/2026-09-21-horace-aifoundry2")
CARDS = ["aifoundry2", "aifoundry3", "aifoundry1-c1"]


def samples(path):
    try:
        with gzip.open(path, "rt") as fh:
            for line in fh:
                if line.startswith("{"):
                    try:
                        yield json.loads(line)
                    except ValueError:
                        pass
    except (OSError, EOFError):
        return


def d1_d7():
    for card in CARDS:
        mhz, spmax, sysc = collections.Counter(), collections.Counter(), collections.Counter()
        busy_cool, cool_under = collections.Counter(), collections.Counter()
        tmin = None
        n = 0
        for f in glob.glob(f"{V3}/{card}/**/*.jsonl.gz", recursive=True):
            for d in samples(f):
                m = d.get("mhz", {}).get("minion")
                t = d.get("temp_c", {}).get("minshire", [None])[0]
                w = d.get("board_w")
                s = d.get("sp", {})
                if s.get("system_c") is not None:
                    sysc[tuple(s["system_c"])] += 1
                if m is None:
                    continue
                n += 1
                mhz[m] += 1
                if s.get("minion_mhz"):
                    spmax[s["minion_mhz"][2]] += 1
                if t is not None:
                    tmin = t if tmin is None else min(tmin, t)
                    if w is not None and t <= 65 and w > 45:
                        busy_cool[m] += 1
                    if w is not None and t <= 64 and 45 < w < 63:
                        cool_under[m] += 1
        print(f"D1 {card}: samples {n}, mhz.minion {dict(mhz)}, sp.minion_mhz max {dict(spmax)}, lowest mean {tmin}, "
              f"busy at <=65 C {dict(busy_cool)}, <=64 C and 45-63 W {dict(cool_under)}")
        print(f"D7 {card}: sp.system_c {dict(sysc.most_common(3))}")


def d2():
    for card in CARDS:
        st, en = [], []
        for f in glob.glob(f"{V3}/{card}/*/*/block.json"):
            b = json.load(open(f))
            if isinstance(b.get("die_c_start"), (int, float)):
                st.append(b["die_c_start"])
            if isinstance(b.get("die_c_end"), (int, float)):
                en.append(b["die_c_end"])
        print(f"D2 {card}: {len(st)} blocks, start {min(st)}-{max(st)} C, end {min(en)}-{max(en)} C")


def d3_d4():
    for card in CARDS:
        durs, gaps, rcs = [], [], collections.Counter()
        for p in sorted(glob.glob(f"{V3}/{card}/idle/p*")):
            marks = {m["ev"]: m for m in map(json.loads, open(p + "/marks.jsonl"))}
            heat = [json.loads(x) for x in open(p + "/heat.jsonl")]
            tel = list(samples(p + "/telemetry.jsonl.gz"))
            t0, cs, ce = marks["cycle_start"]["t_ms"], marks["cool_start"]["t_ms"], marks["cool_end"]["t_ms"]
            cool = [d for d in tel if cs <= d["t_ms"] <= ce]
            cross = [d["t_ms"] for d in tel if d["t_ms"] >= t0 and d["temp_c"]["minshire"][0] > 65]
            tc = (cross[0] - t0) / 1000 if cross and heat[0]["die_c"] <= 65 else None
            he = marks["heat_end"]
            print(f"D3 {card} {os.path.basename(p)}: start {heat[0]['die_c']} C, to >65 C {tc} s, "
                  f"{he['bursts']} bursts / {he['heat_s']} s ({he['reason']}), max mean "
                  f"{max(d['temp_c']['minshire'][0] for d in tel)}, max high {max(d['temp_c']['minshire'][2] for d in tel)}, "
                  f"max board {max(d['board_w'] for d in tel)} W, after cooling {cool[-1]['temp_c']['minshire'][0]} C")
            L = [json.loads(x) for x in open(p + "/launches.jsonl")]
            durs += [a["t_end_ms"] - a["t_start_ms"] for a in L]
            gaps += [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(L, L[1:])]
            rcs.update(a["rc"] for a in L)
        print(f"D4 {card}: {len(durs)} heater processes, median {statistics.median(durs)} ms (max {max(durs)}), "
              f"median gap {statistics.median(gaps)} ms, rc {dict(rcs)}")


def d5():
    for sess in ["cold1", "cold2"]:
        tel = list(samples(f"{H}/{sess}/telemetry.jsonl.gz"))
        starts = [json.loads(x) for x in open(f"{H}/{sess}/starts.jsonl")]
        for i, s in enumerate(starts):
            t0 = s["t_ms"]
            t1 = starts[i + 1]["t_ms"] if i + 1 < len(starts) else t0 + 12000
            w = [d for d in tel if t0 <= d["t_ms"] < min(t1, t0 + 9000)]
            up = next((d for d in w if d["mhz"]["minion"] > 650), None)
            down, prev = None, None
            if up:
                prev = up["mhz"]["minion"]
                for d in w[w.index(up) + 1:]:
                    if d["mhz"]["minion"] < prev:
                        down = d
                        break
                    prev = d["mhz"]["minion"]
            msg = f"D5 {sess} run {s['run']} {s['values']} start {s['start_temp']} C (waited {s['waited_s']} s)"
            if up:
                msg += f": >650 MHz at {(up['t_ms'] - t0) / 1000:.2f} s"
            if down:
                msg += (f", first down-step at {(down['t_ms'] - t0) / 1000:.2f} s, {prev}->{down['mhz']['minion']} MHz, "
                        f"mean {down['temp_c']['minshire'][0]} C, board {down['board_w']} W")
            print(msg)


def d6():
    p = f"{V3}/aifoundry2/cat/p11"
    b = json.load(open(p + "/block.json"))
    best = max(samples(p + "/telemetry.jsonl.gz"), key=lambda d: d["temp_c"]["minshire"][0])
    print(f"D6 aifoundry2 cat p11: block {b['die_c_start']}->{b['die_c_end']} C; hottest sample mean "
          f"{best['temp_c']['minshire'][0]} C, high {best['temp_c']['minshire'][2]} C, board {best['board_w']} W, "
          f"{best['mhz']['minion']} MHz")


if __name__ == "__main__":
    d1_d7()
    d2()
    d3_d4()
    d5()
    d6()
