#!/usr/bin/env python3
"""E190 (Q169): the registered plan - formats, runs per cell, repeats, the order written out, the gates, the stops, the card-minute arithmetic,
and the refusal: the plan is REFUSED (exit 3, no plan file) unless every predicted board peak sits under its arm's line. Standard library only.

    python3 -I -B tools/claims-v3/e190/plan_e190.py            writes plan-e190.json, prints the order
    python3 -I -B tools/claims-v3/e190/plan_e190.py --check    recomputes and compares with the committed plan-e190.json (exit 0 = PASS)

Process times are desk estimates from E136's own committed launch records (aifoundry2, gemmL4x8x8 with 128 MB of A and B: 0.25-0.29 s from the
process start to the first launch, 0.12-0.23 s after the check launch) scaled by bytes to 8,192^3 (512 / 256 / 128 MB of A and B; 256 MB of C
read back), and the forecast's seconds a GEMM. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FC = json.load(open(os.path.join(HERE, "forecast-e190.json")))
FMTS = ("fp32", "fp16", "int8")
AB_MB = {"fp32": 512, "fp16": 256, "int8": 128}
C_MB = 256
# E136's records (tools: reg-e190's s08_e136_timing.py over docs/reports/data/2026-11-02-e136-large-gemm/aifoundry2/*/launches.jsonl.gz):
SETUP_FIXED_S, SETUP_PER_MB_S = 0.167, 0.00095      # g2k 12 MB -> 0.178 s, g4k 128 MB -> 0.288 s (medians, --seconds 8)
TAIL_FIXED_S, TAIL_PER_MB_S = 0.05, 0.0015          # g4k: 0.12-0.23 s with 64 MB of C read back and the reference; x4 C and a margin
SECONDS_BURST, SECONDS_SUS_PROC, SUS_PROCS, BUDGET_S, TIMEOUT_S = 6.0, 6.0, 12, 7.5, 10
QUERY_S, REST_READ_S = 4.0, 10.0
COOL_AFTER_BURST_S = {"A": 20.0, "B": 10.0}
COOL_AFTER_SUS_S = {"A": 120.0, "B": 60.0}
CAP_MIN, BUDGET_RULE_MIN, PLAN_TARGET_MIN = 40.0, 35.0, 30.0


def proc_seconds(t, seconds):
    setup = SETUP_FIXED_S + SETUP_PER_MB_S * AB_MB[t]
    tg = FC["speed"][t]["t800_s"]["band"][1]                       # the slow end: one GEMM is the loop's overshoot and the check launch
    tail = TAIL_FIXED_S + TAIL_PER_MB_S * C_MB
    return setup + seconds + tg + tg + tail


ORDER = [("SMOKE", None, None),
         ("P1", "burst", "fp32"), ("P1", "burst", "fp16"), ("P1", "burst", "int8"), ("S1", "sus", "fp32"),
         ("P2", "burst", "int8"), ("P2", "burst", "fp32"), ("P2", "burst", "fp16"), ("S2", "sus", "fp16"),
         ("P3", "burst", "fp16"), ("P3", "burst", "int8"), ("P3", "burst", "fp32"), ("S3", "sus", "int8"),
         ("P4", "burst", "fp32"), ("P4", "burst", "fp16"), ("P4", "burst", "int8"),
         ("S4", "sus", "fp32"), ("S5", "sus", "fp16"), ("S6", "sus", "int8")]


def build():
    refuse = [arm for arm, p in FC["peaks"].items() if not p["under_line"]]
    if refuse:
        return None, refuse
    arms = {}
    for arm in ("A", "B"):
        rows, tmin = [], 0.0
        for i, (blk, kind, t) in enumerate(ORDER):
            if blk == "SMOKE":
                dur = 30.0 + sum(proc_seconds(x, 2.0) + QUERY_S for x in FMTS) + 30.0
                rows.append({"i": i, "block": "SMOKE", "what": "30 s rest reading; one 2 s process per format (fp32, fp16, int8 random), each with its check of C; "
                             "R0's cycles-per-op tie; the board and die stop tests on live samples first (the kit's)", "est_s": round(dur, 1)})
            elif kind == "burst":
                dur = REST_READ_S + proc_seconds(t, SECONDS_BURST) + QUERY_S + COOL_AFTER_BURST_S[arm]
                rows.append({"i": i, "block": blk, "kind": "burst", "format": t, "values": FC["gemm"][t]["values"], "processes": 1, "seconds": SECONDS_BURST,
                             "budget_s": BUDGET_S, "timeout_s": TIMEOUT_S, "proc_est_s": round(proc_seconds(t, SECONDS_BURST), 2), "est_s": round(dur, 1)})
            else:
                dur = REST_READ_S + SUS_PROCS * (proc_seconds(t, SECONDS_SUS_PROC) + 0.3) + QUERY_S + COOL_AFTER_SUS_S[arm]
                rows.append({"i": i, "block": blk, "kind": "sus", "format": t, "values": FC["gemm"][t]["values"], "processes": SUS_PROCS,
                             "seconds": SECONDS_SUS_PROC, "budget_s": BUDGET_S, "timeout_s": TIMEOUT_S, "window_s": 40.0,
                             "proc_est_s": round(proc_seconds(t, SECONDS_SUS_PROC), 2), "est_s": round(dur, 1)})
            tmin += dur / 60.0
            rows[-1]["cum_min"] = round(tmin + 1.0, 2)       # + 1 min of session start and end reads
        arms[arm] = {"rows": rows, "est_card_min": round(tmin + 1.0, 1)}
    plan = {
        "experiment": "E190", "request": "Q169", "what": "the registered plan; the kit implements it, a departure is a dated amendment before the data",
        "arms": {
            "A": {"host": "aifoundry2", "card": "card 0, /dev/et0_*, lock /run/lock/etsoc-shire0.lock", "clock": "its own governor, nothing set",
                  "gate": {"burst_die_max_c": 55, "sus_die_max_c": 57, "max_wait_s": 300},
                  "stops": {"board_w": FC["constants"]["stop_A"]["board_w"], "board_samples": 3, "die_c": FC["constants"]["stop_A"]["die_c"],
                            "watcher_keys": "board_cap_w, cap_consecutive, abs_stop_c (the keys run_hpl.py's watcher reads; E146's finding)"},
                  "line_w": FC["peaks"]["A"]["line_w"], "predicted_peak_w": FC["peaks"]["A"]},
            "B": {"host": "aifoundry1", "card": "card 1: ET_DEVICES=1 / V3_DEVICE=1, lock /run/lock/etsoc-shire1.lock",
                  "clock": "as found (600 MHz in every sample since September); nothing set",
                  "gate": {"burst_die_max_c": "min(63, the session's rest die + 3)", "sus_die_max_c": "min(64, the session's rest die + 4)", "max_wait_s": 300},
                  "stops": {"board_w": FC["constants"]["stop_B"]["board_w"], "board_samples": 3, "die_c": FC["constants"]["stop_B"]["die_c"],
                            "watcher_keys": "as arm A"},
                  "line_w": FC["peaks"]["B"]["line_w"], "predicted_peak_w": FC["peaks"]["B"], "rule": "never two of our sessions on aifoundry1 at once"}},
        "kind": "random, E136's: fp32 and fp16 --values gemmL...:randn:<format>/randn.bin, int8 :randn:int8/full.bin; --seed 1; rgm105's generator "
                "(std::mt19937_64 seeded 1; fp32 normal(0, 1) floats, fp16 the same rounded to half, int8 uniform -128..127); pair 0 is the file's; at most "
                "8,192 distinct 1 KB tiles a pool, repeated (8 MB period)",
        "runs_per_cell": {"burst": 4, "sus": 2}, "order": [r[:3] for r in ORDER],
        "budget": {"plan_target_min": PLAN_TARGET_MIN, "budget_rule_min": BUDGET_RULE_MIN, "cap_min": CAP_MIN,
                   "rule": "no run starts once the arm's card time (first device access to now) passes 35 min, so S6, S5, S4 go first (they are last); "
                           "a started run is never cut except by a stop; at 40 min the session ends"},
        "process": {"seconds_burst": SECONDS_BURST, "sus_processes": SUS_PROCS, "seconds_sus_proc": SECONDS_SUS_PROC, "budget_s": BUDGET_S, "timeout_s": TIMEOUT_S,
                    "est_s": {t: round(proc_seconds(t, SECONDS_BURST), 2) for t in FMTS},
                    "how": "setup 0.167 s + 0.95 ms a MB of A and B (E136: g2k 0.178, g4k 0.288 s); the loop's overshoot and the check launch at the slow end of "
                           "a GEMM each; tail 0.05 s + 1.5 ms a MB of C (E136 g4k: 0.12-0.23 s for 64 MB). Desk estimates; the smoke measures them first."},
        "arms_est": arms,
        "reads_only": "dmcmd_audit GO with every send site READ; no statistics reset, no firmware-revisions query, no set of any kind, no reset, no power "
                      "cycle; et-who, who, uptime and ps read before each session; the card's lock held for the session; timeout 10 a process; the owner "
                      "waived the day's Discord post (his words, Fri 13 Nov 2026 ~11:30 PST)",
    }
    return plan, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    plan, refused = build()
    if plan is None:
        print(f"PLAN REFUSED: a predicted peak passes its line on arm(s) {refused}")
        sys.exit(3)
    path = os.path.join(HERE, "plan-e190.json")
    if a.check:
        same = json.load(open(path)) == json.loads(json.dumps(plan))
        ok = all(plan["arms_est"][x]["est_card_min"] <= CAP_MIN for x in ("A", "B"))
        print(f"plan_e190 --check: recomputed == committed: {same}; each arm's estimate under the {CAP_MIN:.0f} min cap: {ok}; "
              f"peaks under the lines: A {FC['peaks']['A']['band_top_w']:.1f} <= {FC['peaks']['A']['line_w']:.0f} W, "
              f"B {FC['peaks']['B']['band_top_w']:.1f} <= {FC['peaks']['B']['line_w']:.0f} W")
        print("PASS" if (same and ok) else "FAIL")
        sys.exit(0 if (same and ok) else 1)
    json.dump(plan, open(path, "w"), indent=1)
    for arm in ("A", "B"):
        print(f"arm {arm}: {plan['arms'][arm]['host']}, {plan['arms'][arm]['card']}; estimate {plan['arms_est'][arm]['est_card_min']} card-minutes (target 30, rule 35, cap 40)")
        for r in plan["arms_est"][arm]["rows"]:
            what = r.get("what") if r["block"] == "SMOKE" else f"{r['kind']:5s} {r['format']}: {r['processes']} x {r['seconds']:.0f} s (one process ~{r['proc_est_s']} s)"
            print(f"  {r['i']:2d} {r['block']:5s} {what[:150]}  ~{r['est_s']:.0f} s, cum {r['cum_min']} min")


if __name__ == "__main__":
    main()
