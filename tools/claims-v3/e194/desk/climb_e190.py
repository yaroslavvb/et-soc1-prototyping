#!/usr/bin/env python3
"""E194's desk read of E190 arm A's committed telemetry (aifoundry2 card 0 under its own governor, Fri 13 Nov 2026): how
long the governor takes to climb from its idle point (600 MHz) to 800 MHz after a process's first launch, whether the
clock leaves 800 MHz again before the process's launches end, and the die at each run's gate (E194.md sections 3.1, 5
and 8.2). It reads committed files only (docs/reports/data/2026-11-13-e190-large-gemm/aifoundry2/: telemetry.jsonl.gz,
runs/*/run.json, runs/*/proc-*.out, smoke/rest.json). A desk reading of another experiment's measured records, used for
E194's clock rule and its forecast die; nothing here is an E194 datum. Standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e194/desk/climb_e190.py     # its output is desk/climb-e190.txt
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
D = os.path.join(REPO, "docs/reports/data/2026-11-13-e190-large-gemm/aifoundry2")


def main():
    tel = []
    with gzip.open(os.path.join(D, "telemetry.jsonl.gz"), "rt") as f:
        for ln in f:
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            if "t_ms" in s:
                tel.append((s["t_ms"], (s.get("mhz") or {}).get("minion", -1), (s.get("temp_c") or {}).get("minshire",
                                                                                                           [None])[0]))
    tel.sort()
    print(f"E190 arm A telemetry: {len(tel)} samples")
    rest = json.load(open(os.path.join(D, "smoke", "rest.json")))
    print(f"the smoke's 30 s rest: board median {rest['board_w_median']} W, die median {rest['die_median_c']} C")
    rows = []
    gates = []
    for run in sorted(os.listdir(os.path.join(D, "runs"))):
        r = json.load(open(os.path.join(D, "runs", run, "run.json")))
        gates.append((run, r["kind"], r["gate"]["die"], r["gate"]["c"], r["gate"]["waited_s"]))
        for p in r.get("procs", []):
            lw = p.get("launch_window_ms")
            if not lw:
                continue
            a, b = lw
            inside = [x for x in tel if a <= x[0] <= b]
            first800 = next((x[0] for x in inside if x[1] == 800), None)
            off = [x for x in inside if first800 is not None and x[0] >= first800 and x[1] != 800]
            rows.append({"run": run, "kind": r["kind"], "proc": p["name"],
                         "climb_s": None if first800 is None else (first800 - a) / 1000.0,
                         "off_800_after_climb": len(off), "off_values": sorted(set(x[1] for x in off)),
                         "die_max": max((x[2] for x in inside if x[2] is not None), default=None)})
    print("\nrun gates (run, kind, die at the gate C, gate C, waited s):")
    for g in gates:
        print("  %-20s %-5s %3d %5.1f %5.1f" % g)
    dies = [g[2] for g in gates]
    print(f"  the die at the gate over {len(dies)} runs: median {statistics.median(dies):g} C, "
          f"range {min(dies)}-{max(dies)} C")
    print("\nprocesses (run, proc, climb s from the launch window's start to the first 800 MHz sample, samples off 800 "
          "MHz after it, their values, die max):")
    for x in rows:
        print("  %-20s %-7s %6s %3d %-10s %s" % (x["run"], x["proc"], "-" if x["climb_s"] is None else
                                                 f"{x['climb_s']:.3f}", x["off_800_after_climb"],
                                                 x["off_values"], x["die_max"]))
    cl = sorted(x["climb_s"] for x in rows if x["climb_s"] is not None)
    print(f"\nclimb over {len(cl)} processes: min {cl[0]:.3f} s, median {statistics.median(cl):.3f} s, "
          f"max {cl[-1]:.3f} s; above 1.0 s: {sum(1 for c in cl if c > 1.0)}; above 1.5 s: "
          f"{sum(1 for c in cl if c > 1.5)}")
    bursts = [x for x in rows if x["kind"] == "burst"]
    sus = [x for x in rows if x["kind"] != "burst"]
    print(f"bursts: {len(bursts)} processes, {sum(1 for x in bursts if x['off_800_after_climb'])} with a sample off 800 "
          f"MHz after the climb; die max {max(x['die_max'] for x in bursts)} C")
    off = [x for x in sus if x["off_800_after_climb"]]
    hot = [x for x in off if x["die_max"] is not None and x["die_max"] >= 66]
    print(f"sustained runs: {len(sus)} processes, {len(off)} with samples off 800 MHz after the climb: {len(hot)} reached "
          f"a shire mean of 66 C (the governor's thermal test, mean above 65 C), {len(off) - len(hot)} did not "
          f"({', '.join(x['run'] + ' ' + x['proc'] + ' die max ' + str(x['die_max']) + ' C' for x in off if x not in hot)}"
          f"; cause not read here)")
    print("CLIMB READ DONE")


if __name__ == "__main__":
    main()
