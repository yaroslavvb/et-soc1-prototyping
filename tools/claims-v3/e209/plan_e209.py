#!/usr/bin/env python3
"""E209 (Q202): the card, its conditions, its stops, the predicted peaks, the card time and the cap of THE BLIND MATMUL DAY ON aifoundry2's
CARD UNDER ITS GOVERNOR, with its refusal rule. Standard library only. Desk: nothing is measured or set.

    python3 -I -B tools/claims-v3/e209/plan_e209.py            writes plan-e209.json and plan-e209.txt beside this file
    python3 -I -B tools/claims-v3/e209/plan_e209.py --check    re-makes them in memory and compares byte for byte (PASS / FAIL)

REFUSES (exit 3) if any point's planning peak passes the line: MM1-v2's planning peak (its board power at the top point + 2 W) or F1@800's
board power (its rest at 50 C + its W over idle at 800 MHz) above 80 W, E208's planning line on this card.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V2 = "tools/matmul/mm1/v2"
S1R_CHECKS = "docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/checks-e208-a2c0-S1r.json"
INPUTS = ["tools/claims-v3/e209/points-e209.json", f"{V2}/out/mm1_v2_e209.csv", f"{V2}/out/f1f2_e209.csv", f"{V2}/out/summary_v2.json", S1R_CHECKS,
          "tools/claims-v3/e208/proposal/src/mms_common.py"]
LINE_W = 80.0
STOPS = {"board_cap_w": 85.0, "cap_consecutive": 3, "abs_stop_c": 80.0}
DIE_GATE_C = 55.0
RULE_MIN, CAP_MIN = 45.0, 55.0
OPEN_S = 60.0 + 3 * 10.0 + 60.0    # the opening rest, the smoke (three 2 s processes with their gates) and the stop-path test and identity read


def sha(p):
    return hashlib.sha256(open(os.path.join(REPO, p), "rb").read()).hexdigest()


def build():
    pts = json.load(open(os.path.join(HERE, "points-e209.json")))
    v2 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "out", "mm1_v2_e209.csv")))}
    f12 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "out", "f1f2_e209.csv")))}
    S = json.load(open(os.path.join(REPO, V2, "out", "summary_v2.json")))
    c1r = json.load(open(os.path.join(REPO, S1R_CHECKS)))["checks"]
    fl = lambda x: float(x) if x not in ("", None) else None
    rows, bad = [], []
    for p in pts["points"]:
        pid = p["id"]
        pv2 = p["planning_peak_w_mm1v2"]
        f1w = fl(f12[pid].get("F1_W_over@800"))
        f1b = fl(f12[pid]["F1_P_rest_W@50C"]) + f1w if f1w is not None else None
        peak = max(x for x in (pv2, f1b) if x is not None)
        rows.append({"id": pid, "planning_peak_w_mm1v2": pv2, "board_w_f1_800": round(f1b, 2) if f1b is not None else None,
                     "die_burst_c_mm1v2": None, "forecast_capped_mm1v2": p["forecast_capped_mm1v2"], "form": p["form"], "runs": p["runs_planned"], "peak_for_the_line": round(peak, 2)})
        if peak > LINE_W:
            bad.append(pid)
    # the die forecast over a burst, read from MM1-v2's points file (e209_points.csv: pred_die_peak_burst_c)
    pcsv = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "out", "e209_points.csv")))}
    for r in rows:
        r["die_burst_c_mm1v2"] = round(float(pcsv[r["id"]]["pred_die_peak_burst_c"]), 1)
    e208 = dict(S["e209"]["e208_measured_peaks_aifoundry2"])
    c5 = c1r["C5_stops"]
    e208["a2c0-S1r"] = {"board_max_w": c5["board_max_w"], "die_max_c": float(c5["die_max_c"]), "latch_first_max_c": c5["latch_first_max_c"]}
    order = pts["order"]
    est = {"burst": 23.0, "sus3": 70.0, "null": 50.0}
    P = {p["id"]: p for p in pts["points"]}
    secs = 0.0
    for o in order:
        if o["role"] == "arm":
            secs += est[P[o["id"]]["form"]]
        elif o["role"] == "anchor":
            secs += est["burst"]
        else:
            secs += est["null"]
    cut = 0.0
    for o in order:
        if o["block"] in ("start", "pass1"):
            cut += est[P[o["id"]]["form"]] if o["role"] == "arm" else (est["burst"] if o["role"] == "anchor" else est["null"])
    plan = {"experiment": "E209", "what": "the card, its conditions, stops, predicted peaks, card time and cap (desk; nothing measured or set)",
            "inputs_sha256": {p: sha(p) for p in INPUTS},
            "card": {"box": "aifoundry2", "card": "card 0 (/dev/et0_mgmt, /dev/et0_ops; ET_DEVICES unset: the box's one card)",
                     "lock": "/run/lock/etsoc-shire0.lock (root's; opened read-only, never created; flock -n; held for the whole session)",
                     "sessions": "one session of ours on aifoundry2 at a time; nothing of ours on the card meanwhile; no claim of the model session's on aifoundry2 "
                                 "(W/out/orch/claim-aifoundry2.txt absent)"},
            "clock": {"how": "under its own governor, as found: each process starts at the 600 MHz boot point and the governor steps it (600 / 700 / 800 MHz); "
                             "read from the run's launches (cycles max / wall) and its 10 Hz samples, never set",
                      "config_gate": {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz_at_rest": 600, "power_state": 3,
                                      "identity": "the config read's stderr names /dev/et0_mgmt and physical device ID 0 (E208's a2c0 gate)"}},
            "stops": dict(STOPS, how="aifoundry2's own lines in E194's and E200's kits (E190 arm A's on this card) and E208's kit on this card: the board strictly above "
                                     "85 W on 3 samples in a row (a sample with no board reading starts the count again); the shires' mean die (minshire[0]) at "
                                     "or above 80 C; the hottest-sensor latch (minshire[2]) at or above 80 C once it has risen during the session (a latch already "
                                     "high from before the session does not trip until it rises). E189's 65 W / 70 C lines, which E194's and E200's kits read "
                                     "first for their own programs, are not E209's: MM1-v2 puts E209's top point at 67.2 W and E208 read 71.5-71.9 W on this card",
                      trip="touches the hosts' --stop-file at once (a running host ends at its next launch boundary, about 0.5 s) and nothing further starts; "
                           "no process is killed"),
            "die_gate_c": DIE_GATE_C, "die_gate_how": "a run starts with the shires' mean die at or below 55 C, waited at most 180 s, else the session's rule "
                                                     "(E208's a2c0 gate)",
            "line_w": LINE_W, "line_how": "no point runs whose planning peak passes the line (E208's planning line on this card)",
            "peaks": {"mm1v2_planning_peak_max_w": max(r["planning_peak_w_mm1v2"] for r in rows),
                      "mm1v2_planning_peak_at": max(rows, key=lambda r: r["planning_peak_w_mm1v2"])["id"],
                      "f1_800_board_max_w": max(r["board_w_f1_800"] for r in rows if r["board_w_f1_800"] is not None),
                      "mm1v2_die_burst_max_c": max(r["die_burst_c_mm1v2"] for r in rows),
                      "e208_measured_on_this_card": e208,
                      "planning_bound": "E208's measured peaks on this card (board 71.49-71.86 W, die 58-60 C, hottest-sensor latch 61-62 C) sit above "
                                        "MM1-v2's forecast; both sit under the stops"},
            "card_time": {"runs": len(order), "point_runs": sum(1 for o in order if o["role"] == "arm"), "anchors": sum(1 for o in order if o["role"] == "anchor"),
                          "nulls": sum(1 for o in order if o["role"] == "null"), "seconds_a_run": est,
                          "planned_card_minutes": round((secs + OPEN_S) / 60.0, 1), "of_which_runs": round(secs / 60.0, 1), "opening_s": OPEN_S,
                          "rule": f"no run starts after {RULE_MIN:g} card-minutes from the first card command", "cap": f"the session ends at {CAP_MIN:g} card-minutes, "
                          "after the run in progress", "registered_subset_if_cut": "the smoke, A1, N1 and pass 1 with its anchors (every point once): "
                          f"{round((cut + OPEN_S) / 60.0, 1)} card-minutes"},
            "rest": "the first card command at least 40 minutes after the last session on aifoundry2 card 0 ended (ours or the model session's)",
            "window": "G = the card lane's booking on its day; last start G + 1:30, last end G + 3:30, each rounded up to the whole minute, inside the "
                      "Pacific day; G at 20:29:00 PST or earlier",
            "quiet_desk_flag": "W/locks/quiet-desk-aifoundry2 (one line '<lane> <time>'), raised by the card lane before its first card command and "
                               "removed after its last; while it stands no lane starts on aifoundry2 a process whose comm matches _host$, ^ettelem$, "
                               "^dev_mngt_servi, ^et-powertop$, ^mmbench_launch or ^sys_emu$, nor a script named session_eNNN*.sh or queue_eNNN*",
            "process": "every device process under a plain `timeout 10` (no -k, no -s): `sparsity_host ... --seconds 6 --budget 7.5`; a host alive 30 s "
                       "after it started gets SIGTERM on its wrapper, never SIGKILL; alive 30 s later it is a LEFTOVER: the session ends, makes no "
                       "closing read, and holds the card's lock until no device process of its login is left (E208's step 10); never a reset",
            "reads_only": "dmcmd_audit_v2 GO with every send site READ before the first device access; no statistics reset, no set of any kind (TDP, "
                          "threshold, clock, voltage), no reset, no PCIe recovery, no driver reload, no power cycle, no firmware change; et-who, who, uptime "
                          "and ps read before the session; the card's lock held for the session",
            "post": "waived (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines, nobody is using them\")",
            "package_counter": "not read",
            "points": rows, "refused": bad}
    lines = [f"E209 plan: aifoundry2 card 0 under its governor (config gate TDP 65 W, 65 C, 600 MHz at rest, power state 3); stops board > 85 W x 3, "
             f"die or latch >= 80 C; die gate 55 C; line 80 W",
             f"peaks: MM1-v2 planning {plan['peaks']['mm1v2_planning_peak_max_w']} W at {plan['peaks']['mm1v2_planning_peak_at']}; F1@800 board "
             f"{plan['peaks']['f1_800_board_max_w']} W; MM1-v2 die over a burst {plan['peaks']['mm1v2_die_burst_max_c']} C; E208 on this card: "
             + "; ".join(f"{k} {v['board_max_w']} W / {v['die_max_c']} C / latch {v['latch_first_max_c']}" for k, v in e208.items()),
             f"card time: {plan['card_time']['runs']} runs ({plan['card_time']['point_runs']} point runs, {plan['card_time']['anchors']} anchors, "
             f"{plan['card_time']['nulls']} nulls), planned {plan['card_time']['planned_card_minutes']} card-minutes; {plan['card_time']['rule']}; "
             f"{plan['card_time']['cap']}; cut: {plan['card_time']['registered_subset_if_cut']}",
             "id   form  runs  MM1-v2 planning peak W  F1@800 board W  MM1-v2 die burst C  capped (MM1-v2)"]
    for r in rows:
        lines.append(f"{r['id']}  {r['form']:5s} {r['runs']}     {r['planning_peak_w_mm1v2']:7.2f}               {str(r['board_w_f1_800']):>7s}          "
                     f"{r['die_burst_c_mm1v2']:5.1f}            {r['forecast_capped_mm1v2']}")
    lines.append("REFUSED: " + (", ".join(bad) if bad else "none (every point under the 80 W line by both)"))
    return json.dumps(plan, indent=1, sort_keys=True) + "\n", "\n".join(lines) + "\n", bad


def main():
    js, txt, bad = build()
    if "--check" in sys.argv[1:]:
        ok = (open(os.path.join(HERE, "plan-e209.json")).read() == js and open(os.path.join(HERE, "plan-e209.txt")).read() == txt)
        print("PLAN CHECK " + ("PASS" if ok and not bad else "FAIL"))
        sys.exit(0 if ok and not bad else 1)
    if bad:
        sys.stdout.write(txt)
        sys.exit(3)
    open(os.path.join(HERE, "plan-e209.json"), "w").write(js)
    open(os.path.join(HERE, "plan-e209.txt"), "w").write(txt)
    sys.stdout.write(txt)


if __name__ == "__main__":
    main()
