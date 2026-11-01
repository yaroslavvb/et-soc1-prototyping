#!/usr/bin/env python3
"""Q132(g), item 1: does aifoundry2's power controller have card 0's 75 W alarm? POST HOC, desk only, no card.

E84's reader (tools/claims-v3/kspeed/e84/posthoc_pmic_e84.py) applied to every committed session, with the readings beside it. For each session:
rings, alarm lines, safe-state records and 300 MHz operating points in the rings; telemetry readings, how many at 300 MHz, and the power
controller's own numbers:
  board_w        the 10 Hz reading of the PMIC's instantaneous input power (`ettelem sample`, DM get-module-power)
  sp.board_max_w the SP's running maximum of that same instantaneous reading since its statistics were last reset
                 (update_module_soc_power, CALC_MIN_MAX on pmic_read_instantaneous_soc_power)
  sp.board_avg_w the PMIC's running average (about 1.1 s), which the governor's power arm acts on
and, for the runs that reached 75 W, whether the ring reaches back to the previous dump, so that an alarm could not have been overwritten.

    pmic_check.py <repo> [--out pmic-check.json] > pmic-check.txt
"""
import argparse
import gzip
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ir_lib as L

ALARM = re.compile(r"alarm set point")
OVER = re.compile(r"power = (\d+) mW, alarm set point = (\d+) mW")

SESS = [
    ("E64 s1", "aifoundry2", "2026-10-23-e64-horace-power-limit/s1"), ("E64 s2", "aifoundry2", "2026-10-23-e64-horace-power-limit/s2"),
    ("E69 s1", "aifoundry2", "2026-10-27-e69-governor-knob/s1"), ("E69 s2", "aifoundry2", "2026-10-27-e69-governor-knob/s2"), ("E69 s3", "aifoundry2", "2026-10-27-e69-governor-knob/s3"),
    ("E69 smoke", "aifoundry2", "2026-10-27-e69-governor-knob/smoke"), ("E69 smoke2", "aifoundry2", "2026-10-27-e69-governor-knob/smoke2"),
    ("E80 s1", "aifoundry2", "2026-10-31-e80-kinds-speed/s1"), ("E83 s1", "aifoundry2", "2026-10-31-e83-kinds-speed-rest/s1"), ("E87 s1", "aifoundry2", "2026-10-31-e87-real-tensors-speed/s1"),
    ("E84 s1", "aifoundry1 c0", "2026-10-31-e84-speed-aifoundry1-card0/s1"),
    ("E78 s1", "aifoundry3", "2026-10-31-e78-kinds-energy-matrix/s1"), ("E86 s1", "aifoundry3", "2026-10-31-e86-real-tensors-energy/s1"), ("E90 s1", "aifoundry3", "2026-10-31-e90-signs-spread/s1"),
    ("E82 s1", "aifoundry1 c1", "2026-10-31-e82-kinds-aifoundry1/s1"), ("E88 s1", "aifoundry1 c1", "2026-10-31-e88-result-path/s1"), ("E91 s1", "aifoundry1 c1", "2026-10-31-e91-real-tensors-aifoundry1/s1"),
]


def samples(path):
    out = []
    for d in L.jl(path):
        try:
            sp = d.get("sp") or {}
            out.append((int(d["t_ms"]), d.get("board_w"), sp.get("board_max_w"), sp.get("board_avg_w"), (d.get("mhz") or {}).get("minion")))
        except (TypeError, ValueError, KeyError):
            pass
    out.sort()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--out")
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.repo, "tools/claims-v3/hpl"))
    sys.path.insert(0, os.path.join(a.repo, "tools/claims-v3/dv2"))
    import sptrace_full as spf
    data = os.path.join(a.repo, "docs/reports/data")
    out = {"sessions": {}}
    print("session     card           rings alarm  safe  op300 |  readings  at300 | max board_w  max sp.max  max sp.avg | readings>=75W  runs>=75W  seconds>=75W longest>=75W s | runs>=75W whose ring reaches the previous dump")
    for name, box, rel in SESS:
        d = os.path.join(data, rel)
        if not os.path.isdir(d):
            print(name, "missing", rel)
            continue
        runs = L.jl(os.path.join(d, "runs.jsonl"))
        prev = None
        sb = os.path.join(d, "sp", "start.bin")
        if os.path.exists(sb):
            prev = spf.scan(open(sb, "rb").read()) or []
        rings = alarm = safe = op300 = nread = at300 = 0
        mx = mxmax = mxavg = 0.0
        n75 = r75 = cov75 = 0
        sec75 = 0.0
        longest = 0.0
        over = []
        setp = set()
        rec_runs = []
        for r in runs:
            name_r = r["run"]
            p = os.path.join(d, "sp", name_r + ".bin")
            cover = None
            if os.path.exists(p):
                cur = spf.scan(open(p, "rb").read()) or []
                rings += 1
                new = spf.since(prev, cur) if prev is not None else cur
                cover = bool(prev) and bool(cur) and min(e["ts"] for e in cur) <= max(e["ts"] for e in prev)
                prev = cur
                for e in new:
                    t = e.get("text") or ""
                    if ALARM.search(t):
                        alarm += 1
                        m = OVER.search(t)
                        if m:
                            over.append(int(m.group(1)))
                            setp.add(int(m.group(2)))
                    if e["kind"] == "pstat" and e.get("throttle_state") == 3:
                        safe += 1
                    if e["kind"] == "new_op" and e.get("mhz") == 300:
                        op300 += 1
            S = samples(os.path.join(d, "tel", name_r + ".jsonl"))
            nread += len(S)
            at300 += sum(1 for x in S if x[4] == 300)
            run_n75 = 0
            streak = 0.0
            for i, x in enumerate(S):
                if x[1] is not None:
                    mx = max(mx, x[1])
                    if x[1] >= 75.0:
                        run_n75 += 1
                        sec75 += 0.1
                        streak += 0.1
                        longest = max(longest, streak)
                    else:
                        streak = 0.0
                if x[2] is not None:
                    mxmax = max(mxmax, x[2])
                if x[3] is not None:
                    mxavg = max(mxavg, x[3])
            n75 += run_n75
            if run_n75:
                r75 += 1
                if cover:
                    cov75 += 1
                rec_runs.append({"run": name_r, "readings_ge75": run_n75, "max_w": max(x[1] for x in S if x[1] is not None), "ring_full": cover})
        s = {"box": box, "rings": rings, "alarm_lines": alarm, "safe_records": safe, "op300": op300, "readings": nread, "readings_300": at300,
             "max_board_w": mx, "max_sp_board_max_w": mxmax, "max_sp_board_avg_w": mxavg, "readings_ge75": n75, "runs_ge75": r75, "seconds_ge75": round(sec75, 1),
             "longest_ge75_s": round(longest, 1), "runs_ge75_ring_full": cov75, "alarm_powers_mw": sorted(set(over)), "set_points_mw": sorted(setp), "top_runs": sorted(rec_runs, key=lambda x: -x["max_w"])[:5]}
        out["sessions"][name] = s
        print(f"{name:11s} {box:14s} {rings:5d} {alarm:5d} {safe:5d} {op300:5d} | {nread:8d} {at300:6d} | {mx:9.2f} {mxmax:10.2f} {mxavg:10.2f} | {n75:10d} {r75:10d} {sec75:10.1f} {longest:10.1f} | {cov75}")
    a2 = [v for k, v in out["sessions"].items() if v["box"] == "aifoundry2"]
    tot = {k: sum(v[k] for v in a2) for k in ("rings", "alarm_lines", "safe_records", "op300", "readings", "readings_300", "readings_ge75", "runs_ge75", "runs_ge75_ring_full")}
    tot["max_board_w"] = max(v["max_board_w"] for v in a2)
    tot["max_sp_board_max_w"] = max(v["max_sp_board_max_w"] for v in a2)
    tot["max_sp_board_avg_w"] = max(v["max_sp_board_avg_w"] for v in a2)
    print("\naifoundry2 in all:", json.dumps(tot))
    out["aifoundry2_total"] = tot
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
