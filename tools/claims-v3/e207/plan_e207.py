#!/usr/bin/env python3
"""E207 (Q199): the registered plan of THE BLIND MATMUL DAY - the card, its clock, the start config gate, the die gate, the stops, the line, the
predicted peaks, the order written out with each run's planned seconds, the card-minute arithmetic, the cap, the rest and the window form - and
the refusal: the plan is REFUSED (exit 3, no plan file) if a point's predicted peak passes the line (MM1-v1's planning peak, or F1's peak at its
point where F1 prices the point). Standard library only.

    python3 -I -B tools/claims-v3/e207/plan_e207.py            writes plan-e207.json, prints plan-e207.txt (redirect stdout)
    python3 -I -B tools/claims-v3/e207/plan_e207.py --check    recomputes and compares with the committed plan-e207.json (exit 0 = PASS)

A RUN (E206's form, unchanged): its die gate (at most 300 s, else that run is NO DATA), 10 s read at rest (p_rest = the median of its last 5 s),
ONE host process `--seconds 6 --budget 7.5` under a plain `timeout 10` (never -k: no SIGKILL is sent or arranged to a device process), the 4 s
tail. THE PLANNED SECONDS come from E206 arm A's own session on this card (its committed session.log, sha256 pinned): the mean seconds a run of its
241 runs and its smoke's seconds; the same arithmetic at the slowest run E206 saw is printed beside as a check. The peaks: MM1-v1's planning peak
(its frozen file's plan_peak_W: aifoundry3's high-side rest 26.0 W + 1.10 x W over idle + 1 W; mm-synth's planning form) and F1's (its rest + its
W + 4 W, E206's margin; at its point and at its band's top). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PTS = json.load(open(os.path.join(HERE, "points-e207.json")))
MM1_CSV = ("tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv", "90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6")
F12 = ("tools/matmul/mm1/v1/out/f1f2_blind_day.json", "2f252ebdfd0ada66684a71adceb2f227ca559818b1bfb188322378296641a3d0")
E206_LOG = ("docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/session/session.log",
            "55687f4ca8347ed3e4191d66f9f7845f65370b63f06dae16bcadb531183822f0")
LINE_W = 65.0
STOP = {"board_w_above": 70.0, "samples_in_a_row": 3, "samples": "counting the samples that carry a board reading; a sample with none neither counts nor breaks the row",
        "die_c_at_or_above": 70.0,
        "die_reading": "the shires' mean (minshire[0]) at or above 70 C, or the hottest-sensor latch (minshire[2]) once it has risen during the session "
                       "above the lowest value it read since the session's first sample and reads at or above 70 C (E206.md amendment A1 item 1)"}
GATE = "min(60, the session's rest die + 4) C"
GATE_MAX_WAIT_S = 300
PEAK_MARGIN_W = 4.0
NO_NEW_RUN_MIN, CAP_MIN = 60.0, 70.0
REST_BETWEEN_SESSIONS_MIN = 40.0
K_BURST = 0.1445          # E136's burst law carried to aifoundry3 (E206's F1 step 6): die = 50 + 0.1445 (P_work - 21.5), REPORTED only


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def pinned(pair):
    if sha_rel(pair[0]) != pair[1]:
        print(f"plan_e207: REFUSED, {pair[0]} is not the pinned file")
        sys.exit(4)
    return os.path.join(REPO, pair[0])


def e206_timing():
    lines = open(pinned(E206_LOG)).read().splitlines()

    def tm(s):
        return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
    start = next(tm(x) for x in lines if "session start" in x)
    gate = next(tm(x) for x in lines if "smoke gate passed" in x)
    end = next(tm(x) for x in lines if "session end" in x)
    begins, dones = {}, {}
    for x in lines:
        m = re.search(r" run (\d{3}-\S+): ", x)
        if m:
            begins[m.group(1)] = tm(x)
        m = re.search(r" run (\d{3}-\S+) done: ", x)
        if m:
            dones[m.group(1)] = tm(x)
    durs = sorted((dones[k] - begins[k]).total_seconds() for k in dones if k in begins)
    first_run = min(begins.values())
    last_done = max(dones.values())
    return {"runs": len(durs), "mean_run_s": (last_done - first_run).total_seconds() / len(durs), "max_run_s": durs[-1], "median_run_s": durs[len(durs) // 2],
            "smoke_s": (gate - start).total_seconds(), "after_last_run_s": (end - last_done).total_seconds(),
            "session_min": (end - start).total_seconds() / 60.0}


def build():
    v1 = {r["id"]: r for r in csv.DictReader(open(pinned(MM1_CSV), newline=""))}
    f12 = {r["id"]: r for r in json.load(open(pinned(F12)))["rows"]}
    tmg = e206_timing()
    peaks, refused = {}, []
    for p in PTS["points"]:
        pid = p["id"]
        pp = float(v1[pid]["plan_peak_W"])
        f = f12[pid]
        f1p = f1b = None
        if f.get("F1_W_over_idle") is not None:
            f1p = f["F1_P_rest_W"] + f["F1_W_over_idle"] + PEAK_MARGIN_W
            rest_top = json.load(open(pinned(F12)))["rest_A"]["band"][1]
            f1b = rest_top + f["F1_W_band"][1] + PEAK_MARGIN_W
        peaks[pid] = {"mm1_v1_planning_w": pp, "F1_point_w": f1p, "F1_band_top_w": f1b,
                      "die_c_reported": 50.0 + K_BURST * (max(x for x in (pp, f1p) if x is not None) - 21.5)}
        if pp > LINE_W or (f1p is not None and f1p > LINE_W):
            refused.append(pid)
    if refused:
        return None, refused
    seq = PTS["order"]["sequence"]
    t = tmg["smoke_s"]
    t_slow = tmg["smoke_s"]
    rows = []
    for s in seq:
        t += tmg["mean_run_s"]
        t_slow += tmg["max_run_s"]
        rows.append({"n": s["n"], "block": s["block"], "id": s["id"], "name": s["name"], "run_s_plan": round(tmg["mean_run_s"], 2),
                     "cum_min_plan": round(t / 60.0, 2)})
    plan_min = (t + tmg["after_last_run_s"]) / 60.0
    slow_min = (t_slow + tmg["after_last_run_s"]) / 60.0
    cut = next(r for r in rows if r["block"] == "tie" and r["n"] > 1)
    hi = max(peaks, key=lambda k: peaks[k]["mm1_v1_planning_w"])
    hi1 = max((k for k in peaks if peaks[k]["F1_point_w"] is not None), key=lambda k: peaks[k]["F1_point_w"])
    hib = max((k for k in peaks if peaks[k]["F1_band_top_w"] is not None), key=lambda k: peaks[k]["F1_band_top_w"])
    plan = {
        "experiment": "E207", "request": "Q199", "what": "the registered plan; the kit implements it; a departure is a dated amendment before the data it touches",
        "card": "aifoundry3 card 0 (/dev/et0_*; the card's lock /run/lock/etsoc-shire0.lock)",
        "clock": "600 MHz pinned (a boot-time TDP of 0 latches the governor), nothing set",
        "start_config_gate": "TDP 0 W, 65 C, 600 MHz as found (read, nothing set; E206 arm A read the same at both ends)",
        "line_w": LINE_W, "stop": STOP, "gate": GATE, "gate_max_wait_s": GATE_MAX_WAIT_S,
        "points": PTS["n_points"], "cases": PTS["n_cases"], "runs": len(seq),
        "predicted_peak": {"mm1_v1_planning": {"id": hi, "w": peaks[hi]["mm1_v1_planning_w"]},
                           "F1_point": {"id": hi1, "w": peaks[hi1]["F1_point_w"]}, "F1_band_top": {"id": hib, "w": peaks[hib]["F1_band_top_w"]},
                           "die_c_reported": max(v["die_c_reported"] for v in peaks.values()),
                           "e206_measured_reference": "E206 arm A on this card: board peak 59.54 W, the shires' mean 61 C (its committed README), against "
                                                      "F1's 53.4 W at its hottest point: peaks ran up to about 6 W over F1's point there",
                           "per_point": peaks},
        "timing_source": {"what": "E206 arm A's committed session.log on this card (sha256 pinned)", **{k: round(v, 3) for k, v in tmg.items()}},
        "card_minutes": {"plan": round(plan_min, 1), "slow_check_at_e206_slowest_run": round(slow_min, 1), "no_new_run_after_min": NO_NEW_RUN_MIN,
                         "cap_min": CAP_MIN, "runs_planned_after_no_new_run": sum(1 for r in rows if r["cum_min_plan"] > NO_NEW_RUN_MIN),
                         "registered_subset_if_cut": f"the smoke, tie 1, pass 1 and tie 2 (runs 1-{cut['n']}): every point once, about "
                                                     f"{cut['cum_min_plan']:.1f} card-minutes"},
        "smoke": "30 s at rest (the session's rest reading; the die gate from it); one checked 2 s process each of b01, b02 and b03 (gemmL1x3x2 in fp32, "
                 "int8 and fp16): each rc 0, every launch ok, the check of C exact or approx, its cycles an op (the counter's mean) 50-250% of MM1-v1's "
                 "counter-mean forecast, the board 2 W or more over the rest, the host on card 0; then the stop-path test on live samples (no launch)",
        "order": "tie (t01 = E206's p001), pass 1 (tier 1, tier 2, tier 3, each in its seeded order), tie, pass 2 (pass 1 reversed), tie: points-e207.json",
        "run": {"rest_read_s": 10.0, "tail_s": 4.0, "process": "--seconds 6 --budget 7.5 under a plain timeout 10 (never -k)"},
        "rules": {"text": f"no run starts once the card time (the first device access to now) passes {NO_NEW_RUN_MIN:.0f} minutes; at {CAP_MIN:.0f} the "
                          "session ends after the run in progress (a started run is cut only by a stop); a stop touches the host's --stop-file (the host "
                          "ends at its next launch boundary), never a kill; a host hung past its TERM is reported and left"},
        "rests": f"the first card command at least {REST_BETWEEN_SESSIONS_MIN:.0f} minutes after our previous session on aifoundry3 ended",
        "window": "G = the card lane's booking on its day; last start G + 1:30, last end G + 3:30, each rounded up to the whole minute, inside the "
                  "Pacific day; G at 20:29:00 PST or earlier",
        "box": "aifoundry3 (kept for the lab by the owner's coordination thread, post #2.6.2 and its reply, Mon 16 Nov 2026 11:01 PST), after E202 and E206 arm A there (both ran on Mon 16 Nov 2026); one session of ours on the "
               "box at a time; the model session's own sweeps run on aifoundry1 and aifoundry2, never on aifoundry3",
        "reads_only": "dmcmd_audit_v2 GO with every send site READ before the first device access; no statistics reset, no set of any kind (TDP, "
                      "threshold, clock, voltage), no reset, no power cycle, no firmware change; et-who, who, uptime and ps read before the session; the "
                      "card's lock held for the session; every device process under a plain timeout 10; the host's package counter is not read; the "
                      "owner waived the Discord post (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines\")",
        "rows": rows}
    return plan, []


def text(plan):
    pk = plan["predicted_peak"]
    cm = plan["card_minutes"]
    L = [f"E207: {plan['card']}; {plan['clock']}; {plan['points']} points ({plan['cases']} cases), {plan['runs']} runs",
         f"card time planned {cm['plan']} card-minutes (at E206's slowest run throughout: {cm['slow_check_at_e206_slowest_run']}); no run after "
         f"{cm['no_new_run_after_min']:.0f}, cap {cm['cap_min']:.0f}; runs planned after {cm['no_new_run_after_min']:.0f} min: {cm['runs_planned_after_no_new_run']}; "
         f"{cm['registered_subset_if_cut']}",
         f"timing from E206 arm A's session on this card: {plan['timing_source']['runs']} runs, mean {plan['timing_source']['mean_run_s']} s a run, "
         f"slowest {plan['timing_source']['max_run_s']} s, smoke {plan['timing_source']['smoke_s']} s, session {plan['timing_source']['session_min']} min",
         f"line {plan['line_w']:.0f} W; stops: board above {plan['stop']['board_w_above']:.0f} W on {plan['stop']['samples_in_a_row']} samples, die at or "
         f"above {plan['stop']['die_c_at_or_above']:.0f} C; gate {plan['gate']}, at most {plan['gate_max_wait_s']} s",
         f"predicted peaks: MM1-v1's planning {pk['mm1_v1_planning']['w']:.1f} W ({pk['mm1_v1_planning']['id']}), F1 at its point "
         f"{pk['F1_point']['w']:.1f} W ({pk['F1_point']['id']}), F1 at its band's top {pk['F1_band_top']['w']:.1f} W ({pk['F1_band_top']['id']}); "
         f"die (E136's burst law, REPORTED) {pk['die_c_reported']:.1f} C; {pk['e206_measured_reference']}"]
    for r in plan["rows"]:
        L.append(f"  {r['n']:3d} {r['block']:5s} {r['id']} {r['name']:36s} ~{r['run_s_plan']:5.2f} s; cum {r['cum_min_plan']:6.2f} min")
    L.append(f"rests: {plan['rests']}")
    L.append(f"window: {plan['window']}")
    L.append(f"box: {plan['box']}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    plan, refused = build()
    if plan is None:
        print(f"PLAN REFUSED: a predicted peak passes the {LINE_W:.0f} W line: {refused}")
        sys.exit(3)
    path = os.path.join(HERE, "plan-e207.json")
    if a.check:
        same = json.load(open(path)) == json.loads(json.dumps(plan))
        ok = plan["card_minutes"]["plan"] <= NO_NEW_RUN_MIN and plan["card_minutes"]["slow_check_at_e206_slowest_run"] <= CAP_MIN
        print(f"plan_e207 --check: recomputed == committed: {same}; planned card time under the {NO_NEW_RUN_MIN:.0f} min rule and the slow check under "
              f"the {CAP_MIN:.0f} min cap: {ok}; every point's peak under the {LINE_W:.0f} W line: True")
        print("PASS" if (same and ok) else "FAIL")
        sys.exit(0 if (same and ok) else 1)
    json.dump(plan, open(path, "w"), indent=1)
    sys.stdout.write(text(plan))


if __name__ == "__main__":
    main()
