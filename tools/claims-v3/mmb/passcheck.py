#!/usr/bin/env python3
"""End-of-block check for one V3-MMB pass (no card access): did every component produce its data, and does the pass
have to be re-run under the registered drop rules?

    python3 tools/claims-v3/mmb/passcheck.py <pass dir> --card aifoundry2|aifoundry3 [--smoke] > passcheck.json

Exit 0: the pass is complete and nothing in it is dropped. Exit 4: re-run the pass (reasons printed), because a
component is missing or failed, or a registered drop rule hit: an E1 or ridge-X1 launch with implied_ghz outside
0.595-0.605, an E1 launch on aifoundry2 with a sample off 600 MHz, or an aifoundry2 load step (pt X1) with any
mhz.minion != 600, or a load step that the registered reducer (x1_reduce.py) cannot reduce. The smoke tests' results
are reported, never a reason to re-run (they are data for MMB-b).
"""
import argparse
import gzip
import json
import os
import sys

GHZ = (0.595, 0.605)


def mmbench_lines(path):
    out = []
    if os.path.exists(path):
        for l in open(path, errors="replace"):
            if l.startswith("MMBENCH "):
                try:
                    out.append(json.loads(l.split(" ", 1)[1]))
                except ValueError:
                    pass
    return out


def load_jsonl(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rt") as f:
                return [json.loads(l) for l in f if l.startswith("{")]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--card", required=True)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    d = a.dir
    order = json.load(open(os.path.join(d, "order.json")))
    rep = {"card": a.card, "smoke": a.smoke, "rerun": [], "notes": [], "components": {}}

    # smoke tests (data for MMB-b; never a re-run reason)
    sm = load_jsonl(os.path.join(d, "smoke", "smoke.jsonl"))
    rep["components"]["smoke"] = {"tests": len(sm), "failed": [s["test"] + " " + s.get("args", "") for s in sm if s["rc"] != 0]}
    if rep["components"]["smoke"]["failed"]:
        rep["notes"].append("smoke failed: " + "; ".join(rep["components"]["smoke"]["failed"]))

    # E1
    e1 = {}
    for w in order["e1"]:
        wd = os.path.join(d, "e1", w)
        res = os.path.join(wd, "results.json")
        if not os.path.exists(res):
            rep["rerun"].append(f"e1 {w}: no results.json")
            e1[w] = None
            continue
        r = json.load(open(res))["results"]
        if not r:
            rep["rerun"].append(f"e1 {w}: no timed launches")
            continue
        res_all = json.load(open(res))
        r = r[0]
        procs = res_all.get("launcher_processes", [])
        e1[w] = {"launches": r["launches"], "tflops": round(r["tflops"], 4), "mean_w": round(r["mean_w"], 2),
                 "idle_before_w": round(r["idle_before_w"], 2), "die_c_start": r["die_c_start"],
                 "mhz": r["mhz_minion_launches"], "dropped": r["dropped_launches"], "check": r["check"],
                 "power_samples": r["power_samples"], "proc_wall_s": [p["proc_wall_s"] for p in procs],
                 "timed": res_all.get("timed_workloads", [])}
        if procs and max(p["proc_wall_s"] for p in procs) > 9.3:
            rep["notes"].append(f"e1 {w}: a launcher process took {max(p['proc_wall_s'] for p in procs):.2f} s (timeout 10)")
        for tw in res_all.get("timed_workloads", []):
            if tw.get("repeat_planned") and tw["repeat"] != tw["repeat_planned"]:
                rep["notes"].append(f"e1 {w}: {tw['repeat']} timed launches instead of {tw['repeat_planned']} "
                                    f"(process overhead {tw['proc_overhead_s']} s)")
        if not r["power_samples"]:
            rep["rerun"].append(f"e1 {w}: no power samples inside the launches")
        if r["dropped_launches"]:  # in a smoke block (no heater on aifoundry2) a note only
            rep["notes" if a.smoke else "rerun"].append(f"e1 {w}: dropped launches {r['dropped_launches']} (clock)")
        if r["check"] != ["exact"]:
            rep["notes"].append(f"e1 {w}: check {r['check']}")
    rep["components"]["e1"] = e1

    # ridge-X1
    x1 = {}
    want = 1 if a.smoke else 3
    for kind in ("private", "shared"):
        for m in order["x1"]:
            L = mmbench_lines(os.path.join(d, "x1", f"{kind}-{m}.out"))
            if not L:
                continue
            cyc = [r["cycles_max"] / r["ops_per_minion"] for r in L]
            off = [r["launch"] for r in L if not GHZ[0] <= r["implied_ghz"] <= GHZ[1]]
            x1[f"{kind}-{m}"] = {"launches": len(L), "cycles_per_op": [round(min(cyc), 2), round(max(cyc), 2)],
                                 "implied_ghz": sorted({r["implied_ghz"] for r in L}), "off_clock": off,
                                 "check": sorted({r["check"] for r in L})}
            if len(L) < want:
                rep["rerun"].append(f"x1 {kind}-{m}: {len(L)} launches (want {want})")
            if off:
                rep["notes" if a.smoke else "rerun"].append(f"x1 {kind}-{m}: launches {off} off 0.595-0.605 GHz")
    for kind in ("private", "shared"):
        for m in order["x1"]:
            if f"{kind}-{m}" not in x1:
                rep["rerun"].append(f"x1 {kind}-{m}: no MMBENCH line")
    for q in load_jsonl(os.path.join(d, "x1", "rc.jsonl")):
        if q["rc"] != 0:
            rep["notes"].append(f"x1 {q['kind']}-{q['mode']}: launcher rc {q['rc']} (a failed check; cycle counts kept)")
    rep["components"]["x1"] = x1

    # pt X1 load step
    td = os.path.join(d, "thermal")
    tel = load_jsonl(os.path.join(td, "thermal-telemetry.jsonl"))
    loads = open(os.path.join(td, "thermal-loads.log")).read().splitlines() if os.path.exists(os.path.join(td, "thermal-loads.log")) else []
    mm = sum(1 for l in loads if l.startswith("MMBENCH")); mp = sum(1 for l in loads if l.startswith("MEMPROBE"))
    want_mm, want_mp = (1, 1) if a.smoke else (8, 4)
    mhz = sorted({r["mhz"]["minion"] for r in tel if "mhz" in r})
    incomplete = sum(1 for r in tel if not all(k in r for k in ("board_w", "sp", "temp_c", "die_mv", "mhz")))
    rep["components"]["thermal"] = {"telemetry": len(tel), "mmbench": mm, "memprobe": mp, "mhz_minion": mhz,
                                    "samples_missing_a_block": incomplete}
    if not tel:
        rep["rerun"].append("thermal: no telemetry")
    if mm != want_mm or mp != want_mp:
        rep["rerun"].append(f"thermal: {mm} MMBENCH and {mp} MEMPROBE lines (want {want_mm} and {want_mp})")
    if a.card == "aifoundry2" and tel and mhz != [600]:
        rep["notes" if a.smoke else "rerun"].append(f"thermal: mhz.minion {mhz} on aifoundry2 (the pass is dropped)")
    # The registered load-step reducer (x1_reduce.py, the plan's copy) on this pass, off the card: a pass it cannot reduce
    # (a sample without a block, a phase too short) would be lost at reduction time, so it is re-run now instead.
    # x1_reduce (via summarize_power_session.py) reads the edges in fixed windows, 15-35 s and 73-95 s after the idle0
    # mark, and bins only up to 175 s (E5: stop at 78.0 s, cool2 at 152.1 s): a pass whose stop edge or DRAM phase falls
    # outside would be reduced silently wrong (P7, P8), so it is re-run and the shift shows in block.json.
    ph = load_jsonl(os.path.join(td, "thermal-phases.jsonl"))
    if ph and not a.smoke:
        rel = {x["phase"]: (x["t_ms"] - ph[0]["t_ms"]) / 1000 for x in ph}
        rep["components"]["thermal"]["phases_s"] = {k: round(v, 1) for k, v in rel.items()}
        if not 75.0 <= rel.get("cool1", -1) <= 92.0:
            rep["rerun"].append(f"thermal: matmul stop edge at {rel.get('cool1')} s, outside the reducer's stop window "
                                "73-95 s (needs 75-92 s)")
        if not rel.get("cool2", 999) <= 174.0:
            rep["rerun"].append(f"thermal: DRAM phase ends at {rel.get('cool2')} s, past the reducer's last bin (175 s)")
    if tel and not a.smoke:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            sys.dont_write_bytecode = True
            import x1_reduce
        except Exception as e:  # the tree lacks summarize_power_session.py or the dvfs.json idle law: reduce elsewhere
            rep["notes"].append(f"thermal: x1_reduce not importable here ({type(e).__name__}: {e}); not checked")
        else:
            try:
                o = x1_reduce.reduce_pass(td, "a2" if a.card == "aifoundry2" else "a3")
                rep["components"]["thermal"]["x1_reduce"] = {k: o[k] for k in (
                    "valid", "busy_slope_board", "idle_after_minus_before_w", "dram_rest_rise_w", "cool_drop_40s_c",
                    "edge_tau_card", "board_avg_minus_board_steady_median")}
            except Exception as e:
                rep["rerun"].append(f"thermal: x1_reduce failed on this pass ({type(e).__name__}: {e})")

    json.dump(rep, sys.stdout, indent=1)
    print()
    for x in rep["rerun"]:
        print("RERUN:", x, file=sys.stderr)
    for x in rep["notes"]:
        print("NOTE:", x, file=sys.stderr)
    return 4 if rep["rerun"] else 0


if __name__ == "__main__":
    sys.exit(main())
