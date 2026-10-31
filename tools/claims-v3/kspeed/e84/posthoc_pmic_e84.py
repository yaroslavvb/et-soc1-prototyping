#!/usr/bin/env python3
"""E84, post hoc and labelled (written after the data; never a verdict): the PMIC's over-power alarm on card 0.

    python3 posthoc_pmic_e84.py <RUNDIR> [--out pmic.json]

The registered reduction knows two limits, the governor's thermal arm and its power arm. In fp32 random data on card 0
the trace ring holds a third: `Pmic_Controller_Handle_Pmic_Error_Event: (step 250 mW) power = <P> mW, alarm set point
= <S> mW`, followed by a power-status record in throttle state 3 (POWER_SAFE) and `New OP: Freq 300`, after which the
power arm climbs back one point a pass. This script reports, for every run, from the ring (it keeps only its last ~67
entries, so a long run is covered only at its end): the alarm lines, their power and set point, the time from each
safe state to the next, and the clock points the ring set; and from the sampler: the share of in-work samples at each
clock, and the kernel's own effective clock (cycles over wall) beside the sampled mean.
"""
import argparse
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "hpl"))
import reduce_hpl as R  # noqa: E402
import sptrace_full as spf  # noqa: E402

ALARM = re.compile(r"power = (\d+) mW, alarm set point = (\d+) mW")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--out")
    a = ap.parse_args()
    rd = a.rundir
    sess, rr, launches, q0 = R.load_session(rd)
    prev = spf.scan(open(os.path.join(rd, "sp", "start.bin"), "rb").read()) or []
    out = {"note": "post hoc, labelled; never a verdict", "runs": []}
    for r in rr:
        cur = spf.scan(open(os.path.join(rd, "sp", r["run"] + ".bin"), "rb").read()) or []
        new = spf.since(prev, cur)
        prev = cur
        alarms = []
        for e in new:
            m = ALARM.search(e.get("text") or "") if e["kind"] == "other" else None
            if m:
                alarms.append({"ts": e["ts"], "power_mw": int(m.group(1)), "set_point_mw": int(m.group(2))})
        safes = [e["ts"] for e in new if e["kind"] == "pstat" and e.get("throttle_state") == 3]
        ops = sorted({e.get("mhz") for e in new if e["kind"] == "new_op"})
        s = R.tel(os.path.join(rd, r["tel"]))
        L = [l for l in launches if l["run"] == r["run"] and l.get("role") == "work"]
        kl = [k for l in L for k in l.get("sparsity", []) if k.get("t_start_ms")]
        kw = [(k["t_start_ms"], k["t_end_ms"]) for k in kl]
        ws = [x for x in s if any(a0 <= x[0] <= b0 for a0, b0 in kw) and x[4] is not None]
        share = {f: round(sum(1 for x in ws if x[4] == f) / len(ws), 3) for f in sorted({x[4] for x in ws})} if ws else {}
        wall = sum(k.get("wall_s", 0) for k in kl)
        ghz = round(sum(k.get("cycles_max", 0) for k in kl) / wall / 1e9, 4) if wall else None
        span = (cur[-1]["ts"] - new[0]["ts"]) / 1e6 if new and cur else None
        rec = {"run": r["run"], "block": r["block"], "kind": r["values"].split("/")[-1].replace(".bin", ""),
               "type": r["type"], "alarms_in_ring": len(alarms), "safe_states_in_ring": len(safes),
               "ring_span_s": round(span, 2) if span else None, "clock_points_set": ops,
               "alarm_power_mw": sorted({x["power_mw"] for x in alarms}),
               "alarm_set_point_mw": sorted({x["set_point_mw"] for x in alarms}),
               "safe_to_safe_s": [round((safes[i + 1] - safes[i]) / 1e6, 3) for i in range(len(safes) - 1)],
               "work_clock_share": share, "sampled_mhz_mean": round(st.mean([x[4] for x in ws]), 1) if ws else None,
               "kernel_ghz_eff": ghz}
        out["runs"].append(rec)
    hit = [x for x in out["runs"] if x["alarms_in_ring"]]
    out["summary"] = {"runs": len(out["runs"]), "runs_with_alarm": [x["run"] for x in hit],
                      "set_points_mw": sorted({p for x in hit for p in x["alarm_set_point_mw"]}),
                      "alarm_powers_mw": sorted({p for x in hit for p in x["alarm_power_mw"]}),
                      "safe_to_safe_s_median": (round(st.median([d for x in hit for d in x["safe_to_safe_s"]]), 3)
                                                if any(x["safe_to_safe_s"] for x in hit) else None)}
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out["summary"], indent=1))
    for x in hit:
        print(x["run"], "alarms", x["alarms_in_ring"], "safe", x["safe_states_in_ring"], "ring span", x["ring_span_s"],
              "s; safe-to-safe", x["safe_to_safe_s"], "; clock share", x["work_clock_share"], "; sampled",
              x["sampled_mhz_mean"], "kernel", x["kernel_ghz_eff"])


if __name__ == "__main__":
    main()
