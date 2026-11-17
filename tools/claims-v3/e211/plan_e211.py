#!/usr/bin/env python3
"""E211 (Q204): the registered card plan (plan-e211.json, plan-e211.txt): the card, its gates, stops, peaks, the order and the card time. The
kit implements it; a departure is a dated amendment before the data it touches. Desk; standard library.

    python3 -I -B tools/claims-v3/e211/plan_e211.py            writes plan-e211.json and plan-e211.txt (exit 3 if a point's planning peak passes the line)
    python3 -I -B tools/claims-v3/e211/plan_e211.py --check    re-makes both in memory and compares (exit 0 = PASS)
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FC = json.load(open(os.path.join(HERE, "forecast-e211.json")))
PTS = json.load(open(os.path.join(HERE, "points-e211.json")))
OUT_J, OUT_T = os.path.join(HERE, "plan-e211.json"), os.path.join(HERE, "plan-e211.txt")
LINE_W, RUN_S, SMOKE_S, READS_S = 65.0, 21.96, 90.0, 300.0
NO_NEW_RUN_MIN, CAP_MIN = 30.0, 35.0


def peaks():
    rows = {}
    for pid, rec in FC["points"].items():
        w = rec["MM1"]["W_over_idle"]
        row = {"MM1_planning_W": 26.0 + 1.10 * w + 1.0, "F1_peak_W": rec["F"]["F1_peak_point_W"]}
        if rec.get("C"):
            row["C1_planning_W"] = 26.0 + 1.10 * rec["C"]["C1"]["W_over_idle"] + 1.0
            row["C2_planning_W_REPORTED"] = 26.0 + 1.10 * rec["C"]["C2_REPORTED"]["W_over_idle"] + 1.0
        rows[pid] = row
    return rows


def build():
    pk = peaks()
    over = [p for p, r in pk.items() if max(v for k, v in r.items() if k != "F1_peak_W") > LINE_W]
    fam = {p["id"]: p["family"] for p in PTS["points"] + PTS["smoke"]}

    def top(f, key):
        c = [(p, r[key]) for p, r in pk.items() if fam[p] in f and key in r]
        return max(c, key=lambda x: x[1]) if c else None
    n_runs = PTS["counts"]["scored_runs"]
    card_min = (SMOKE_S + n_runs * RUN_S + READS_S) / 60.0
    plan = {"experiment": "E211", "request": "Q204", "what": "the registered plan; the kit implements it; a departure is a dated amendment before the data it touches",
            "card": "aifoundry3 card 0 (/dev/et0_*; the card's lock /run/lock/etsoc-shire0.lock); one session of ours on aifoundry3 at a time",
            "clock": "600 MHz pinned (a boot-time TDP of 0 latches the governor), nothing set",
            "start_config_gate": "TDP 0 W, 65 C, 600 MHz as found (read, nothing set)",
            "line_w": LINE_W,
            "stops": {"board_w_above": 70.0, "samples_in_a_row": 3, "die_c_at_or_above": 70.0,
                      "die_reading": "the shires' mean (minshire[0]) at or above 70 C, or the hottest-sensor latch (minshire[2]) once it has risen during the "
                                     "session above the lowest value it read since the session's first sample and reads at or above 70 C (E206 A1 item 1)",
                      "stop_words": "a stop touches the host's --stop-file (the host ends at its next launch boundary), never a kill; no run sends or "
                                    "arranges a SIGKILL to a device process; every device process under a plain timeout 10, never -k; a host hung past its "
                                    "TERM is reported and left (THE HUNG MARKER: stop, keep the booking, report to the owner, no session that day; no "
                                    "reset, no PCIe recovery, no driver reload, no power cycle)",
                      "kernel_stops": "any check of C wrong, tensor_error, walk check failed (walk_ok false), launch timeout or identity gate failure in "
                                      "a gemmLn or gemmLnc process stops the session: nothing more that day"},
            "die_gate": "min(60, the session's rest die + 4) C, at most 300 s, else that run is NO DATA",
            "run_form": "E206's: the die gate, 10 s at rest (p_rest = the median of its last 5 s), one host process --seconds 6 --budget 7.5 under a plain "
                        "timeout 10 (never -k), a 4 s tail",
            "identity": "before every process the runner gates its --kernel by its arm family (ident_e211.py --gate: gemmL and gemmLnc rgm136's .text and "
                        "whole ELF or loadable identity, gemmLn rgm211's) and records the gate's words with the run; gemmL runs rgm136's host (E206's "
                        "build), gemmLn and gemmLnc rgm211's host; rgm211's host is gated by its behaviour (its early refusals of a malformed arm, "
                        "before the device opens) and every launch's walk check",
            "smoke": "30 s at rest (the session's rest reading; the die gates from it); one checked short process each of s01 (gemmL2x2x2, rgm136), "
                     "s02 (gemmLn2x2x2, rgm211) and s03 (gemmLnc2x2x2, rgm211's host on rgm136's ELF): each rc 0, every launch ok, the check of C "
                     "exact or approx, walk_ok true on every launch (s02 nm, s03 mn), its cycles an op 50-250% of MM1's counter-mean forecast, the "
                     "board 2 W or more over the rest; then the stop-path test on live samples (no launch)",
            "order": "points-e211.json order: the smoke; family X; family W; family C (family C after family W, critic-kernel2 fix 4)",
            "predicted_peak": {"families_X_W_MM1_planning": top(("W", "X"), "MM1_planning_W"), "family_C_C1_planning": top(("C",), "C1_planning_W"),
                               "family_C_C2_planning_REPORTED": top(("C",), "C2_planning_W_REPORTED"), "smoke_C1_planning": top(("smoke",), "C1_planning_W"),
                               "smoke_C2_planning_REPORTED": top(("smoke",), "C2_planning_W_REPORTED"),
                               "F1_highest": max(((p, r["F1_peak_W"]) for p, r in pk.items()), key=lambda x: x[1]),
                               "how": "MM1-v1's blind-day planning form (26.0 W high-side rest + 1.10 x W over idle + 1 W); F1's (its rest + W + 4 W); "
                                      "E206 arm A on this card read board peaks up to about 6 W over F1's point (59.54 W at most); E101's gemmnc1 on this "
                                      "card read 56.1 W at the board (p80) at one block",
                               "points_over_the_line": over},
            "card_time": {"planned_card_minutes": round(card_min, 1), "how": f"the smoke ({SMOKE_S:.0f} s) + {n_runs} runs at E206 arm A's measured "
                          f"{RUN_S} s a run on this card + {READS_S:.0f} s of the session's reads and gates", "no_new_run_after_min": NO_NEW_RUN_MIN,
                          "cap_min": CAP_MIN, "rule": f"no run starts once the card time (the first device access to now) passes {NO_NEW_RUN_MIN:.0f} minutes; "
                          f"at {CAP_MIN:.0f} the session ends after the run in progress (a started run is cut only by a stop)",
                          "registered_subset_if_cut": "the smoke, family X and family W (35 processes): family C is NO DATA if the session ends before it"},
            "rest": "the first card command at least 40 minutes after our previous session on aifoundry3 ended",
            "window": "G = the card lane's booking on its day; last start G + 1:30, last end G + 3:30, each rounded up to the whole minute, inside the "
                      "Pacific day; G at 20:29:00 PST or earlier",
            "queue": "aifoundry3, after E207 (Q199) and E210 (Q202) there; E211 books no card, on any box, before E207's data commit (its twins 2x3x2, "
                     "3x3x4 and 6x6x6 fp32 are E207 blind points)",
            "go": "his standing words (Sun 15 Nov 2026: 10:05:42, 10:22:36, 17:21:16; at or before 21:51:09) and his matmul focus (Mon 16 Nov 2026, at "
                  "or before 09:48:24 PST); the model session's relayed words of 23:15:25 PST Mon 16 Nov 2026",
            "post": "waived (his words, Sun 15 Nov 2026 10:22:36 PST)",
            "package_counter": "not read",
            "reads_only": "dmcmd_audit_v2 GO with every send site READ before the first device access; no statistics reset, no set of any kind (TDP, "
                          "threshold, clock, voltage), no reset, no power cycle, no firmware change; et-who, who, uptime and ps read before the "
                          "session; the card's lock held for the session; the ops node's creation abort harmless on a card held alone",
            "peaks_per_point": {p: {k: round(v, 2) for k, v in r.items()} for p, r in pk.items()}}
    return plan, over


def text(plan):
    pp = plan["predicted_peak"]
    L = ["E211 card plan (registered; desk)", f"card: {plan['card']}", f"clock: {plan['clock']}", f"line {plan['line_w']} W; stops: board > 70 W on 3 "
         f"samples in a row, die >= 70 C; {plan['stops']['stop_words']}", f"die gate: {plan['die_gate']}", f"run form: {plan['run_form']}",
         f"smoke: {plan['smoke']}", f"order: {plan['order']}",
         "predicted peaks (planning): families X and W %.1f W (%s); family C (C1) %.1f W (%s), C2's draft rule %.1f W (%s, REPORTED); smoke (C1) %.1f W, "
         "(C2) %.1f W; F1 at most %.1f W (%s); points over the line: %s" % (
             pp["families_X_W_MM1_planning"][1], pp["families_X_W_MM1_planning"][0], pp["family_C_C1_planning"][1], pp["family_C_C1_planning"][0],
             pp["family_C_C2_planning_REPORTED"][1], pp["family_C_C2_planning_REPORTED"][0], pp["smoke_C1_planning"][1], pp["smoke_C2_planning_REPORTED"][1],
             pp["F1_highest"][1], pp["F1_highest"][0], pp["points_over_the_line"] or "none"),
         f"card time: {plan['card_time']['planned_card_minutes']} card-minutes planned ({plan['card_time']['how']}); {plan['card_time']['rule']}; "
         f"{plan['card_time']['registered_subset_if_cut']}", f"rest: {plan['rest']}", f"window: {plan['window']}", f"queue: {plan['queue']}",
         f"post: {plan['post']}; package counter: {plan['package_counter']}", f"reads only: {plan['reads_only']}"]
    return "\n".join(L) + "\n"


def main():
    plan, over = build()
    js = json.dumps(plan, indent=1, sort_keys=True) + "\n"
    tx = text(plan)
    if sys.argv[1:] == ["--check"]:
        ok = js == open(OUT_J).read() and tx == open(OUT_T).read()
        print("plan_e211 --check:", "PASS" if ok else "DIFFERS")
        return 0 if ok else 1
    if over:
        print("plan_e211: points over the line:", over)
        return 3
    open(OUT_J, "w").write(js)
    open(OUT_T, "w").write(tx)
    sys.stdout.write(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
