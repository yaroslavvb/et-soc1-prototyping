#!/usr/bin/env python3
"""E202's plan (E202.md section 8): the smoke gate, the R rule, the bursts and their order, the card time and its cap,
the stops, the window, and the refusal rule on the predicted peak.

    python3 -I -B tools/claims-v3/e202/plan_e202.py            # write plan-e202.json
    python3 -I -B tools/claims-v3/e202/plan_e202.py --check    # recompute and compare; exit 3 if the peak rule refuses

Reads forecast-e202.json (the frozen forecasts) for the seconds, the predicted peaks and the band ends. Writes nothing
else. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STOP_BOARD_W, STOP_DIE_C, GATE_DIE_C, LOW_DIE_C = 65.0, 70.0, 60.0, 52.0
R_ALLOWED = (16, 32, 48, 64, 80, 96)
R_DEFAULT = 96
R_MAX_KERNEL_S = 6            # the R rule's ceiling: a launch's predicted kernel seconds (the host's own --max-kernel-s)
GROUPS_PER_PASS, P_SHIRE, N_SHIRES = 3750, 32, 32
IDLE_BEFORE_S, IDLE_AFTER_S = 8.0, 10.0
PROCESS_OVERHEAD_S = 3.0      # runtime set-up, copies, read-back and checks around a launch (desk arithmetic)
CAP_MIN, LAST_START_MIN = 35.0, 33.0


def busiest(R):
    rounds = -(-GROUPS_PER_PASS * R // P_SHIRE)
    return -(-rounds // N_SHIRES)


def r_rule(work_cycles_max_r1, copy_cycles_max, f_hz=600e6):
    """The registered R rule (E202.md 8.2), as the kit applies it to an arm's R = 1 smoke: the per-round kernel time is
    the smoke's work_cycles.max over its busiest shire's 4 rounds; a launch of R passes is predicted at busiest(R)
    rounds plus the smoke's copy_cycles_max; R is 96 if that is at most 6 s, else the largest allowed R that is;
    None (no burst for that arm) if even R = 16 is not."""
    t_round = work_cycles_max_r1 / busiest(1) / f_hz
    pre = copy_cycles_max / f_hz
    ok = [R for R in R_ALLOWED if busiest(R) * t_round + pre <= R_MAX_KERNEL_S]
    return (max(ok) if ok else None), {R: busiest(R) * t_round + pre for R in R_ALLOWED}


def build():
    fc = json.load(open(os.path.join(HERE, "forecast-e202.json")))
    order_scored = ["trained", "random", "random", "trained", "trained", "random", "random", "trained"]
    order_reported = ["trained", "random", "random", "trained"]
    t_launch = {k: fc["configs"][k]["seconds"]["launch_R96"] for k in fc["configs"]}
    burst_s = {k: IDLE_BEFORE_S + PROCESS_OVERHEAD_S + v["band"][1] + IDLE_AFTER_S for k, v in t_launch.items()}
    parts = {"checks, the look, the dry listing, the stop-path test": 4,
             "smoke: five R = 1 processes (T-scp, Z-scp, T-dram, Z-dram with --debug-logits; T-scp on the test split)": 2.0,
             "two idle anchors of 2 minutes (start, end)": 4,
             "8 scored bursts at the slow end (%.1f s each) plus the die gate's waits (1 minute each, allowed)" % max(
                 burst_s.values()): round(8 * (max(burst_s.values()) + 60.0) / 60.0, 2),
             "4 REPORTED bursts (the dram pair, when the scp pair is scored)": round(4 * (max(burst_s.values()) + 60.0) / 60.0, 2),
             "closing reads and release": 2.0}
    burst_pt = {k: IDLE_BEFORE_S + PROCESS_OVERHEAD_S + v["point"] + IDLE_AFTER_S for k, v in t_launch.items()}
    at_point = {"fixed parts (checks, smoke, anchors, closing)": 12.0,
                "8 scored and 4 REPORTED bursts at the point (%.1f s each), no die-gate wait" % max(burst_pt.values()):
                    round(12 * max(burst_pt.values()) / 60.0, 2)}
    peak = fc["peak"]
    out = {
        "_what": "E202's plan (plan_e202.py), frozen with the registration; the kit runs it, never re-draws it",
        "card": "aifoundry3 card 0 (/dev/et0_*, /run/lock/etsoc-shire0.lock) at its pinned 600 MHz, reads only, nothing set",
        "smoke": {"processes": [
            {"arm": "T-scp", "args": "--card --stage scp --passes 1 --split train --debug-logits --weights trained"},
            {"arm": "Z-scp", "args": "--card --stage scp --passes 1 --split train --debug-logits --weights random"},
            {"arm": "T-dram", "args": "--card --stage dram --passes 1 --split train --debug-logits --weights trained"},
            {"arm": "Z-dram", "args": "--card --stage dram --passes 1 --split train --debug-logits --weights random"},
            {"arm": "ACC", "args": "--card --stage scp --passes 1 --split test --weights trained --true-labels (on-card test accuracy)"}],
            "gate": "an arm's smoke passes when its host result reads core_status PASS (every record, label line, checksum, "
                    "discard line and operation count; tensor_error 0); a logits_status FAIL with core_status PASS is a "
                    "debug-path defect, recorded, not a gate failure; the scored pair is scp when T-scp and Z-scp both "
                    "pass, else dram when T-dram and Z-dram both pass (the registered fallback), else no burst runs "
                    "(no data, never a failed forecast)",
            "accuracy_expected": "the ACC launch's labels equal the model's expected file (its core check); the "
                                 "trained network's test accuracy is then the model's, 98.49% (desk, measured)"},
        "R_rule": {"allowed": list(R_ALLOWED), "default": R_DEFAULT, "ceiling_kernel_s": R_MAX_KERNEL_S,
                   "words": "per arm, from that arm's R = 1 smoke: t_round = work_cycles.max / 4 (the busiest shire's "
                            "rounds at R = 1) / 600 MHz; predicted kernel seconds of R passes = busiest(R) x t_round + "
                            "copy_cycles_max / 600 MHz; R = 96 if that is at most 6 s, else the largest allowed R "
                            "that is; no burst for the arm if none is",
                   "at_the_forecast": {k: {"launch_s_R96": v} for k, v in t_launch.items()},
                   "busiest_rounds": {str(R): busiest(R) for R in (1,) + R_ALLOWED}},
        "bursts": {"scored": {"configs": "the scored pair's trained (T) and random (Z) configurations", "K": 4,
                              "order": order_scored},
                   "reported": {"configs": "the dram pair, only when the scp pair is scored", "K": 2,
                                "order": order_reported},
                   "coop4": "NOT BUILT: no arm (the design's REPORTED coop4 arm is dropped)",
                   "form": "each burst: the die gate, %.0f s at rest, ONE host process (one launch of R passes, under "
                           "timeout 10, never -k), %.0f s at rest; the sampler at 10 Hz throughout (no statistics reset)"
                           % (IDLE_BEFORE_S, IDLE_AFTER_S)},
        "die_gate": {"start_at_or_below_c": GATE_DIE_C, "wait_s_max": 600,
                     "below_c": LOW_DIE_C, "below_means": "not a block: scored given its own T0 and labelled so"},
        "stops": {"board_w_at_or_above": STOP_BOARD_W, "die_minshire_c_at_or_above": STOP_DIE_C,
                  "clock": "every sample 600 MHz: the first sample off it sets its burst aside, a second stops the session",
                  "stale_telemetry_s": 1.0,
                  "words": "a stop ends the queue: the running process finishes (a device process is never killed), "
                           "nothing further starts, the closing reads, release"},
        "predicted_peak": {"board_w_point_max": peak["board_w_point_max"], "board_w_band_top_max": peak["board_w_band_top_max"],
                           "stop_w": STOP_BOARD_W, "plan_stands": peak["board_w_band_top_max"] < STOP_BOARD_W,
                           "rule": "plan_e202.py refuses (exit 3) unless every configuration's band-top board watts lie "
                                   "under the 65 W stop"},
        "card_time_minutes": {"parts": parts, "total_about": round(sum(parts.values()), 1),
                              "at_the_point": at_point, "total_at_the_point": round(sum(at_point.values()), 1),
                              "cap": CAP_MIN,
                              "last_start": LAST_START_MIN,
                              "words": "no burst starts after %.0f card-minutes from the first card command; the "
                                       "session ends by %.0f" % (LAST_START_MIN, CAP_MIN)},
        "window": "G = the card lane's booking of aifoundry3 on its day; last start G + 1:30, last end G + 3:30, both "
                  "rounded up to the minute, inside that Pacific day; G at 20:29:00 PST or earlier; after E201 and its "
                  "40-minute rest; one session of ours on aifoundry3 at a time",
        "post": "waived: the owner's standing words of Sun 15 Nov 2026 10:22:36 PST",
        "package_counter": "not read (the lab's default)",
    }
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    out = build()
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    fp = os.path.join(HERE, "plan-e202.json")
    if not out["predicted_peak"]["plan_stands"]:
        print("REFUSED: a predicted band-top board power is at or above the 65 W stop")
        return 3
    if a.check:
        ok = open(fp).read() == js
        print(json.dumps({"check": "PASS" if ok else "FAIL", "recomputed_equals_committed": ok,
                          "card_minutes_about": out["card_time_minutes"]["total_about"], "cap": CAP_MIN}))
        return 0 if ok else 1
    open(fp, "w").write(js)
    print(json.dumps({"written": "plan-e202.json", "card_minutes_about": out["card_time_minutes"]["total_about"],
                      "peak_band_top_w": out["predicted_peak"]["board_w_band_top_max"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
