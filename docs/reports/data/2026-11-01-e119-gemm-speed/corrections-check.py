#!/usr/bin/env python3
"""E119, corrections after verification (Sun 1 Nov 2026): print, from committed files only, every number that the
README's "Corrections after verification" section quotes and that no earlier file prints.

    python3 docs/reports/data/2026-11-01-e119-gemm-speed/corrections-check.py > corrections-check.txt

Post hoc; it decides nothing and changes no file. Standard library only; it runs from any directory. Section C5 also
asks git for the registration commit's time; without git it says so and prints the rest.
"""
import gzip
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REL = os.path.relpath(HERE, REPO)
E119 = os.path.join(REPO, "tools", "claims-v3", "e119")
E107_README = os.path.join(REPO, "docs", "reports", "data", "2026-11-01-e107-gemm-placement", "README.md")
ETTELEM_CPP = os.path.join(REPO, "tools", "claims-v3", "dv2", "ettelem-dv2", "ettelem.cpp")
HPL_README = os.path.join(REPO, "tools", "claims-v3", "hpl", "README.md")
REGISTRATION = "695cad4c"


def load(path):
    with open(path) as f:
        return json.load(f)


def jsonl(path):
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def tel(session, run):
    with gzip.open(os.path.join(HERE, "aifoundry2", session, "tel", run + ".jsonl.gz"), "rt") as f:
        return [json.loads(x) for x in f if x.strip()]


def base_label(label):
    return re.sub(r"-rep\d+$", "", label)  # as reduce_e119.py's base_label


def kind_of(label):
    return base_label(label).split("-", 2)[-1]


P = load(os.path.join(E119, "predictions-e119.json"))
RES = load(os.path.join(HERE, "results.json"))
EST = {k: v.get("fixed_p800_w") for k, v in P["admission"].items()}
RUNS = jsonl(os.path.join(HERE, "aifoundry2", "s1", "runs.jsonl"))


def c1():
    print("C1  The power rule: R6's burst medians against single board readings")
    r6 = RES["rules"]["R6"]
    ex = [c["excess_w"] for c in r6["cells"].values()]
    print(f"  R6 (results.json rules.R6): {len(ex)} cells, burst p800_w minus the estimate {min(ex):+.2f} to {max(ex):+.2f} W, "
          f"verdict {r6['verdict']}")
    print(f"  registered guards (predictions-e119.json rules): limit_p800_w {P['rules']['limit_p800_w']} W, "
          f"peak_lock_w {P['rules']['peak_lock_w']} W")
    sus, bur = [], []
    peak_all = (0.0, None)
    for r in RUNS:
        S = tel("s1", r["run"])
        bw = [s["board_w"] for s in S if s.get("board_w") is not None]
        if bw and max(bw) > peak_all[0]:
            peak_all = (max(bw), r["run"])
        if kind_of(r["label"]) == "zeros":
            continue
        t0, t1 = r["launches"][0]["t_start_ms"], r["t_last_ms"]
        i = max(range(len(S)), key=lambda j: S[j].get("board_w") if S[j].get("board_w") is not None else -1.0)
        in_load = [s for s in S if t0 <= s["t_ms"] <= t1]
        start = next(s for s in S if s["t_ms"] >= t0)
        e = EST[base_label(r["label"])]
        row = {
            "run": r["run"], "peak": S[i]["board_w"], "est": e, "over": round(S[i]["board_w"] - e, 2),
            "at": (S[i]["t_ms"] - t0) / 1000, "load": (t1 - t0) / 1000,
            "clocks": [S[j]["mhz"]["minion"] for j in range(max(0, i - 4), i + 1)],
            "die_peak": S[i]["temp_c"]["minshire"][0], "die_start": start["temp_c"]["minshire"][0],
            "die_lo": min(s["temp_c"]["minshire"][0] for s in in_load),
            "die_hi": max(s["temp_c"]["minshire"][0] for s in in_load),
            "n_over": sum(1 for s in in_load if (s.get("board_w") or 0) > e), "n": len(in_load),
        }
        (sus if r.get("processes", 1) >= 2 else bur).append(row)
    print(f"  sustained runs with a random kind (s1/runs.jsonl, processes >= 2): {len(sus)}")
    print("    run                          peak W  est W   over W  peak at s / load s  clocks of the 5 readings to the peak"
          "  die at load start, at peak  readings over est")
    for x in sus:
        print(f"    {x['run']:28s} {x['peak']:6.2f}  {x['est']:5.1f}  {x['over']:+6.2f}  {x['at']:5.1f} / {x['load']:4.1f}"
              f"         {str(x['clocks']):28s}         {x['die_start']}, {x['die_peak']}"
              f"                    {x['n_over']} of {x['n']}")
    over = [x for x in sus if x["over"] > 0]
    if over:
        print(f"  over the estimate: {len(over)} of {len(sus)}, by {min(x['over'] for x in over):.2f}-{max(x['over'] for x in over):.2f} W;"
              f" peaks {min(x['at'] for x in over):.1f}-{max(x['at'] for x in over):.1f} s into loads of"
              f" {min(x['load'] for x in over):.1f}-{max(x['load'] for x in over):.1f} s;"
              f" die at the peak {min(x['die_peak'] for x in over)}-{max(x['die_peak'] for x in over)} C,"
              f" at the load's start {min(x['die_start'] for x in over)}-{max(x['die_start'] for x in over)} C;"
              f" an 800 MHz reading at or within the 4 readings before each peak: {all(800 in x['clocks'] for x in over)}")
    bo = [x for x in bur if x["over"] > 0]
    print(f"  burst runs with a random kind (processes 1): {len(bur)}; whose highest reading exceeded the estimate: {len(bo)};"
          f" the closest {max(x['over'] for x in bur):+.2f} W; die over their loads"
          f" {min(x['die_lo'] for x in bur)}-{max(x['die_hi'] for x in bur)} C")
    print(f"  the session's highest board reading: {peak_all[0]} W ({peak_all[1]})")
    # the die: the instantaneous reading against the SP's maximum register
    seq = []
    for r in sorted(RUNS, key=lambda r: r["t_first_ms"]):
        seq += [s["temp_c"]["minshire"] for s in tel("s1", r["run"])]
    reg = [m[2] for m in seq]
    mono = all(b >= a for a, b in zip(reg, reg[1:]))
    print(f"  die (temp_c.minshire = current, min, max) over {len(seq)} s1 samples: highest current reading {max(m[0] for m in seq)} C;"
          f" the max field (the SP's running maximum) {reg[0]} C at the first sample, {reg[-1]} C at the last, never decreasing: {mono}")
    print()


def c2():
    print("C2  int8 random, sustained (results.json cells.*-int8-full)")
    cells = RES["cells"]
    for k in sorted(cells):
        if k.endswith("-int8-full") and cells[k].get("sus_mhz") is not None:
            c = cells[k]
            print(f"  {k:18s} sus_mhz {c['sus_mhz']}  sus_die {c['sus_die']} C  sus_w {c['sus_w']} W  sus_limit_runs {c['sus_limit_runs']}")
    top = max((c["sus_w"], k) for k, c in cells.items() if c.get("sus_w") is not None)
    print(f"  the highest sustained board power of any cell: {top[1]} {top[0]} W")
    print()


def c3():
    print("C3  The residency read")
    src = open(os.path.join(E119, "run_e119.py")).read()
    m = re.search(r"^RESIDENCY_STATES = (.*)$", src, re.M)
    print(f"  tools/claims-v3/e119/run_e119.py: RESIDENCY_STATES = {m.group(1) if m else '(not found)'}")
    print(f"  tools/claims-v3/e119/protocol.json tools.ettelem: {load(os.path.join(E119, 'protocol.json'))['tools']['ettelem']}")
    for n, line in enumerate(open(HPL_README), 1):
        if "ettelem-hpl" in line:
            print(f"  tools/claims-v3/hpl/README.md line {n}: {line.strip()}")
    lines = open(ETTELEM_CPP).read().splitlines()
    for n, line in enumerate(lines, 1):
        if "raw states 2-6 only (got" in line:
            print(f"  tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp line {n - 1}: {lines[n - 2].strip()}")
            print(f"  tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp line {n}: {line.strip()}")
            print(f"  tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp line {n + 1}: {lines[n].strip()}")
    rc, nonempty, n = {}, 0, 0
    for session in ("smoke", "s1"):
        for r in jsonl(os.path.join(HERE, "aifoundry2", session, "runs.jsonl")):
            q = r.get("queries", {})
            rc[q.get("residency_rc")] = rc.get(q.get("residency_rc"), 0) + 1
            nonempty += bool(q.get("residency"))
            n += 1
        qs = jsonl(os.path.join(HERE, "aifoundry2", session, "queries.jsonl"))
        for q in qs:
            rc[q.get("residency_rc")] = rc.get(q.get("residency_rc"), 0) + 1
            nonempty += bool(q.get("residency"))
            n += 1
    print(f"  residency_rc over smoke and s1 runs.jsonl and queries.jsonl: {n} queries, rc counts {rc}, non-empty results {nonempty}")
    print()


def c4():
    print("C4  E107's arms against E119's")
    lines = open(E107_README).read().splitlines()
    i = next(n for n, line in enumerate(lines) if line.startswith("| arm | what |"))
    arms107, t600 = [], {}
    for line in lines[i + 2:]:
        if not line.startswith("|"):
            break
        cols = [c.strip() for c in line.strip("|").split("|")]
        a = re.search(r"`(\w+)`", cols[0]).group(1)
        arms107.append(a)
        t600[a] = cols[3].strip("*")
    print(f"  E107 README arms table: {' '.join(arms107)} ({len(arms107)})")
    print(f"  E119 predictions-e119.json arms: {' '.join(P['arms'])} ({len(P['arms'])})")
    print(f"  not run in E119: {', '.join(a for a in arms107 if a not in P['arms'])}")
    print(f"  E107's T at 600 MHz, fp32: c4s {t600.get('c4s')}, c8s {t600.get('c8s')}, c8 {t600.get('c8')}, c16s {t600.get('c16s')}, "
          f"c16 {t600.get('c16')} us")
    print()


def c5():
    print("C5  The registration's time")
    try:
        out = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%H %ci", REGISTRATION], capture_output=True, text=True,
                             timeout=20)
        print(f"  git log {REGISTRATION}: {out.stdout.strip() or '(no output: ' + out.stderr.strip() + ')'}")
    except (OSError, subprocess.SubprocessError) as e:
        print(f"  git unavailable ({e.__class__.__name__}); the commit time is not checked here")
    for n, line in enumerate(open(os.path.join(E119, "E119.md")), 1):
        if "19:45" in line:
            print(f"  tools/claims-v3/e119/E119.md line {n}: {line.strip()}")
    print()


def c6():
    print("C6  R5's registered order")
    text = P["rules"]["R5_gap_sus"]["text"]
    m = re.search(r"ORDER \(fp32\):[^:]*", text)
    print(f"  predictions-e119.json rules.R5_gap_sus: ...{m.group(0) if m else text}")
    g = RES["rules"]["R5"]["order_values"]
    c16 = RES["gaps"]["c16-fp32-randn"]["burst_rate"]
    print(f"  results.json rules.R5.order_values (c16r8, c16r4, c16r2): {g}; order_fp32 {RES['rules']['R5']['order_fp32']}")
    print(f"  results.json gaps.c16-fp32-randn.burst_rate: {c16}")
    print(f"  the full registered order {g[0]} > {g[1]} > {g[2]} > 1.02 >= {c16}: {g[0] > g[1] > g[2] > 1.02 >= c16}")
    print()


def c7():
    print("C7  The 600 MHz launches (the reducer's filter and window), by where they ran")
    lo, hi = P["rules"]["R2_clock_buys"]["lo_mhz"]
    byrun = {r["run"]: r for r in RUNS}
    pools = {}
    with gzip.open(os.path.join(HERE, "aifoundry2", "s1", "launches.jsonl.gz"), "rt") as f:
        for x in f:
            pr = json.loads(x)
            r = byrun.get(pr["run"])
            if r is None or pr.get("role") != "work" or r["label"] == "rest":
                continue
            arm, fmt = r["label"].split("-")[:2]
            sustained = r.get("processes", 1) >= 2
            for k in pr.get("sparsity", []):
                if not (k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("ok") and k.get("wall_s", 0) >= 0.1 and k.get("iters")):
                    continue
                f_mhz = k.get("cycles_max", 0) / k["wall_s"] / 1e6
                if not (lo <= f_mhz <= hi):
                    continue
                first = k.get("launch", 0) == 0 and pr.get("proc", 0) == 0
                tag = ("sustained" if sustained else "burst") + (" first" if first else " later")
                pools.setdefault(f"{arm}.{fmt}", {}).setdefault(tag, []).append(k["wall_s"] / k["iters"] * 1e6)
    mean = lambda v: sum(v) / len(v)
    print("    arm.format     n600 (results.json)  burst first  burst later  sustained first  sustained later"
          "  T first launches  T sustained later  difference")
    for key in sorted(pools):
        p = pools[key]
        n = sum(len(v) for v in p.values())
        firsts = p.get("burst first", []) + p.get("sustained first", [])
        later = p.get("sustained later", [])
        tf = mean(firsts) if firsts else None
        tl = mean(later) if later else None
        diff = f"{(tl / tf - 1) * 100:+.2f}%" if (tf and tl) else "-"
        print(f"    {key:13s} {n:4d} ({RES['per_arm'][key]['n600']:3d})            {len(p.get('burst first', [])):3d}"
              f"          {len(p.get('burst later', [])):3d}          {len(p.get('sustained first', [])):3d}"
              f"              {len(later):3d}            {tf if tf is None else round(tf, 4)!s:8s}"
              f"          {tl if tl is None else round(tl, 4)!s:8s}         {diff}")
    print()


def c9():
    print("C9  Blog wording (the lane's result only)")
    gaps = RES["gaps"]
    print("  burst gaps, fp32 (results.json gaps.<arm>-fp32-randn.burst_rate): " +
          ", ".join(f"{a} {gaps[a + '-fp32-randn']['burst_rate']}" for a in ("c16r8", "c16r4", "c16r2", "c8s")))
    m1 = RES["per_arm"]["c16.fp32"]["fit"]["M"]
    m32 = RES["per_arm"]["c16r32.fp32"]["fit"]["M"]
    print(f"  M fp32 (results.json per_arm.<arm>.fit.M): c16 {m1}, c16r32 {m32}; c16's M / 32 = {m1 / 32:.4f};"
          f" c16r32 reads {(m32 / (m1 / 32) - 1) * 100:+.0f}% above it")
    print()


print(f"E119 corrections after verification (Sun 1 Nov 2026): numbers from committed files, data {REL}")
print()
c1()
c2()
c3()
c4()
c5()
c6()
c7()
c9()
