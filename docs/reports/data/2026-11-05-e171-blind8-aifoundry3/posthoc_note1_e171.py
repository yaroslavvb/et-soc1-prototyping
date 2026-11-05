#!/usr/bin/env python3
"""E171, dated note 1 (Thu 5 Nov 2026, PST): the figures the note quotes, read from this directory's committed files only.

Post hoc and reported: it imports no scorer, fits nothing and changes no verdict. It reads
  - scored.json            (the registered scorer's output: the primary and the seven arms E171.md line 75 names);
  - aifoundry3/e171-smoke/p17101/runs.jsonl and block.json   (the smoke's first kernel launch);
  - logs/session.log       (its first three lines);
and, only with --rerun <dir>, the output directory of the README's "How to reproduce" route, to say which files differ and how.

    python3 -I -B posthoc_note1_e171.py [--rerun <the route's build/e171-out/2026-11-05-e171-blind8-aifoundry3> [--label <where it ran>]]

SPDX-License-Identifier: Apache-2.0
"""
import datetime
import gzip
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TZ = datetime.timezone(datetime.timedelta(hours=-8), "PST")  # Thu 5 Nov 2026 is PST (UTC-8)

# The arms, in E171.md line 75's order and words ("Reported beside, never the verdict").
ARMS = [
    ("session_own", "the session-own footing (leakage fitted on the session, dips kept)"),
    ("auto_dips_removed", "leakage fitted on the session, dips removed"),
    ("kfrozen_dips_kept", "the frozen slope (Q139(u)'s), dips kept"),
    ("leak0.1994", "leakage 0.1994 W/C, dips removed"),
    ("leak0.3803", "leakage 0.3803 W/C, dips removed"),
    ("leak0", "leakage 0 W/C, dips removed"),
    ("gates_off", "E78's pass gates opened"),
]
ORDER = ["P8-KC", "P8-P1", "P8-P2", "P8-P3", "P8-B1", "P8-B2", "P8-C1", "P8-M1", "P8-M1f", "P8-M1i", "P8-A1", "P8-KA",
         "P8-H1", "P8-H2", "P8-H3", "P8-H4", "P8-LG", "P8-G", "P8-HM"]


def reading(rule, r):
    """The rule's reading in the fields the record carries (the arms record fewer fields than the primary)."""
    if r is None:
        return "not in this record"
    if r.get("d_rms") is not None:
        return f"d {r['d_rms']:+.4f} W [{r['lo95']:+.4f}, {r['hi95']:+.4f}]"
    if r.get("rms") is not None:
        u = "C" if rule in ("P8-H1", "P8-H2", "P8-H3") else "W"
        return f"rms {r['rms']:.4f} {u}, line [{r['line'][0]:.4f}, {r['line'][1]:.4f}]"
    if r.get("mean") is not None:
        return f"mean {r['mean']:+.4f} W, line [{r['line'][0]:+.4f}, {r['line'][1]:+.4f}]"
    if r.get("inside") is not None:
        return f"{r['inside']} of {r['n']} inside"
    if rule == "P8-KA" and r.get("sum_e_primary_sq") is not None:
        return f"sum e_p^2 {r['sum_e_primary_sq']:.4f} against sum e_0^2 {r['sum_e_a_priori_sq']:.4f} W^2"
    if rule == "P8-LG" and r.get("F_slope") is not None:
        return f"F_slope {r['F_slope']:.3f}, F_level {r['F_level']:.3f} (F point {r['F_point']:.3f})"
    return "verdict only (the record carries no figure)"


def part_arms():
    s = json.load(open(os.path.join(HERE, "scored.json")))
    prim = s["primary"]
    pv = prim["verdicts"]
    print("== 1. The primary and the seven arms (scored.json; every arm 'reported beside, never the verdict', E171.md line 75)")
    print(f"primary: Q139(u)'s footing, leakage 0.20563713796102187 W/C, dips removed; kept {prim['kept_passes']}; "
          f"s {prim['scale']['s_float'] if 's_float' in prim['scale'] else '(see primary.scale)'}")
    print("  " + ", ".join(f"{k} {pv[k]}" for k in ORDER if k in pv))
    moved = {k: [] for k in ORDER}
    for name, words in ARMS:
        a = s["arms"][name]
        av = a["verdicts"]
        diff = [k for k in ORDER if k in av and av[k] != pv.get(k)]
        print(f"\n-- arm {name}: {words}; kept {a['kept_passes']}; s_float {a['s_float']:.5f}")
        if not diff:
            print("   every verdict as the primary's")
        for k in diff:
            moved[k].append(name)
            print(f"   {k}: {av[k]} (primary {pv[k]}); arm {reading(k, a['rules'].get(k))}; primary {reading(k, prim['rules'].get(k))}")
        same = [k for k in ORDER if k in av and av[k] == pv.get(k)]
        print(f"   as the primary: {', '.join(same)}")
        n_moved = [f"{k} n {a['rules'][k]['n']} (primary {prim['rules'][k].get('n')})" for k in ORDER
                   if k in a["rules"] and a["rules"][k].get("n") is not None and prim["rules"].get(k, {}).get("n") is not None
                   and a["rules"][k]["n"] != prim["rules"][k]["n"]]
        if n_moved:
            print(f"   scored on fewer tiles than the primary: {'; '.join(n_moved)}")
        absent = [k for k in ORDER if k not in av]
        if absent:
            print(f"   not scored in the arms: {', '.join(absent)} (the C check reads the launches, not the footing)")
    print("\n== 2. Per rule: the arms (of 7) whose verdict differs from the primary's")
    for k in ORDER:
        if moved[k]:
            vs = sorted({s['arms'][n]['verdicts'][k] for n in moved[k]})
            print(f"   {k} (primary {pv[k]}): {len(moved[k])} of 7: {', '.join(moved[k])} -> {' / '.join(vs)}")
    steady = [k for k in ORDER if not moved[k] and k in pv and k != "P8-KC"]
    print(f"   the same in all 7: {', '.join(steady)}")
    gs = {n: s["arms"][n]["verdicts"]["P8-G"] for n, _ in ARMS}
    print(f"   P8-G in the arms: {gs}")

    print("\n== 2b. The figures in every footing (W; P1-P3 rms, B1/B2 mean, M1/M1f/A1 d with its 95% interval; KA and LG as verdicts)")
    print("   (the leakage and the runs kept: the first line of each footing's committed reduce log)")
    logs = {"primary": "reduce.log", "session_own": "reduce-session.log", "auto_dips_removed": "reduce-auto-nodips.log",
            "kfrozen_dips_kept": "reduce-kfrozen-dips.log", "leak0.1994": "reduce-leak0.1994.log",
            "leak0.3803": "reduce-leak0.3803.log", "leak0": "reduce-leak0.log", "gates_off": "reduce-gatesoff.log"}
    cols = [("primary", prim)] + [(n, s["arms"][n]) for n, _ in ARMS]
    for name, rec in cols:
        r, v = rec["rules"], rec["verdicts"]
        sf = prim["scale"]["s_float"] if name == "primary" else rec["s_float"]
        head = open(os.path.join(HERE, logs[name])).readline()
        leak = head.split("leak ")[1].split(",")[0] if "leak " in head else "?"
        runs = head.split("runs kept ")[1].split(",")[0] if "runs kept " in head else "?"

        def d(k):
            return f"{r[k]['d_rms']:+.3f} [{r[k]['lo95']:+.3f}, {r[k]['hi95']:+.3f}] {v[k]}"
        g_fail = [k for k in ("P8-P1", "P8-P2", "P8-P3", "P8-B1", "P8-B2", "P8-C1") if v[k] != "PASS"]
        if v["P8-M1"] == "WORSE":
            g_fail.append("P8-M1 WORSE")
        print(f"   {name}: leak {leak}, runs kept {runs}, passes {rec['kept_passes']}, s {sf:.4f}; P1 {r['P8-P1']['rms']:.3f} {v['P8-P1']}; "
              f"P2 {r['P8-P2']['rms']:.4f} {v['P8-P2']}; P3 {r['P8-P3']['rms']:.3f} {v['P8-P3']}; "
              f"B1 {r['P8-B1']['mean']:+.3f} {v['P8-B1']}; B2 {r['P8-B2']['mean']:+.3f} {v['P8-B2']}; "
              f"C1 {r['P8-C1']['inside']} of {r['P8-C1']['n']}; M1 {d('P8-M1')}; M1f {d('P8-M1f')}; M1i {d('P8-M1i')}; A1 {d('P8-A1')}; "
              f"KA {v['P8-KA']}; H1-H3 {r['P8-H1']['rms']:.3f} / {r['P8-H2']['rms']:.3f} / {r['P8-H3']['rms']:.3f} C; "
              f"H4 {r['P8-H4']['inside']} of {r['P8-H4']['n']}; LG {v['P8-LG']}; G {v['P8-G']} (not PASS: {', '.join(g_fail) or 'none'})")


def ms(t):
    return datetime.datetime.fromtimestamp(t / 1000, TZ).strftime("%H:%M:%S.%f")[:-3] + " PST"


def part_smoke():
    p = os.path.join(HERE, "aifoundry3", "e171-smoke", "p17101")
    rows = [json.loads(l) for l in open(os.path.join(p, "runs.jsonl"))]
    first = min(rows, key=lambda r: r["t_start_ms"])
    b = json.load(open(os.path.join(p, "block.json")))
    print("\n== 3. The smoke's first kernel launch (aifoundry3/e171-smoke/p17101)")
    print(f"   runs.jsonl: {len(rows)} launch records; the first t_start_ms {first['t_start_ms']} = {ms(first['t_start_ms'])} "
          f"(item {first['item']}, launch {first['launch']}, {first['iters']} iterations, test {first['test']})")
    print(f"   block.json: t0_ms {b['t0_ms']} = {ms(b['t0_ms'])}; t1_ms {b['t1_ms']} = {ms(b['t1_ms'])}")
    for i, line in enumerate(open(os.path.join(HERE, "logs", "session.log")), 1):
        if "e171-smoke p17101 begins" in line:
            print(f"   logs/session.log line {i}: {line.split(' -> ')[0].strip()}")
            break


def part_log():
    print("\n== 4. logs/session.log, lines 1-3")
    with open(os.path.join(HERE, "logs", "session.log")) as f:
        for i in range(3):
            print(f"   {i + 1}: {f.readline().rstrip()}")


def part_rerun(r, label):
    """Which files of the route's output differ from this directory, and how. Prints relative names only."""
    print("\n== 5. The README's 'How to reproduce' route, against this directory")
    if label:
        print(f"   (the route's output: {label})")
    differ, only_here, only_there = [], [], []
    for dirpath, _, files in os.walk(HERE):
        for f in files:
            rel = os.path.relpath(os.path.join(dirpath, f), HERE)
            if rel.startswith("posthoc") or rel.startswith("README.md"):
                continue  # this note's own files and the READMEs are not the collector's
            there = os.path.join(r, rel)
            if not os.path.exists(there):
                only_here.append(rel)
            elif open(os.path.join(HERE, rel), "rb").read() != open(there, "rb").read():
                differ.append(rel)
    for dirpath, _, files in os.walk(r):
        for f in files:
            rel = os.path.relpath(os.path.join(dirpath, f), r)
            if not os.path.exists(os.path.join(HERE, rel)):
                only_there.append(rel)
    n_same = sum(len(fs) for _, _, fs in os.walk(r)) - len(differ) - len(only_there)
    print(f"   files the same byte for byte: {n_same}; differing: {len(differ)}; only here: {sorted(only_here)}; "
          f"only in the route's output: {sorted(only_there)}")

    def leaves(a, b, p, out):
        if type(a) != type(b):
            out.append((p, a, b))
        elif isinstance(a, dict):
            for k in sorted(set(a) | set(b), key=str):
                leaves(a.get(k, "<absent>"), b.get(k, "<absent>"), f"{p}/{k}", out)
        elif isinstance(a, list):
            if len(a) != len(b):
                out.append((p + "[len]", len(a), len(b)))
            for i, (x, y) in enumerate(zip(a, b)):
                leaves(x, y, f"{p}[{i}]", out)
        elif a != b:
            out.append((p, a, b))

    for rel in sorted(differ):
        a_b = open(os.path.join(HERE, rel), "rb").read()
        b_b = open(os.path.join(r, rel), "rb").read()
        if rel.endswith(".json"):
            out = []
            leaves(json.loads(a_b), json.loads(b_b), "", out)
            print(f"   {rel}: {len(out)} differing leaves")
            for p, x, y in out:
                print(f"      {p}: here {x!r}, the route {y!r}")
        elif rel.endswith(".gz"):
            ca, cb = gzip.decompress(a_b), gzip.decompress(b_b)
            ta, tb = struct.unpack("<I", a_b[4:8])[0], struct.unpack("<I", b_b[4:8])[0]
            rest_same = a_b[:4] + a_b[8:] == b_b[:4] + b_b[8:]
            print(f"   {rel}: gzip header time {ms(ta * 1000)[:8]} here, {ms(tb * 1000)[:8]} in the route; every other byte "
                  f"{'the same' if rest_same else 'NOT the same'}; content sha256 {hashlib.sha256(ca).hexdigest()[:16]} "
                  f"{'equal' if ca == cb else 'DIFFERENT'}")
        else:
            la, lb = a_b.decode().splitlines(), b_b.decode().splitlines()
            for i, (x, y) in enumerate(zip(la, lb), 1):
                if x != y:
                    j = next(k for k in range(min(len(x), len(y))) if x[k] != y[k])  # the first differing character
                    tail = 0  # the common suffix's length
                    while tail < min(len(x), len(y)) - j and x[len(x) - 1 - tail] == y[len(y) - 1 - tail]:
                        tail += 1
                    print(f"   {rel} line {i}: the same but for characters {j}-{len(x) - tail - 1}: "
                          f"here '...{x[max(0, j - 40):len(x) - tail + 1]}...', the route '...{y[max(0, j - 40):len(y) - tail + 1]}...'")
            if len(la) != len(lb):
                print(f"   {rel}: {len(la)} lines here, {len(lb)} in the route")


if __name__ == "__main__":
    part_arms()
    part_smoke()
    part_log()
    if "--rerun" in sys.argv:
        lab = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else ""
        part_rerun(sys.argv[sys.argv.index("--rerun") + 1], lab)
