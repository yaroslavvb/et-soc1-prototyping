#!/usr/bin/env python3
"""E222 (Q236): the card, its stops and peaks, the order and the card time, from points-e222.json (the rule's order and plan) and
forecast-e222.json (each run's predicted peak). Standard library only. Refuses (exit 3) a point whose PP32 reaches the drop line, or a plan
whose card time passes the rule.

    python3 -I -B tools/claims-v3/e222/plan_e222.py            writes plan-e222.json and plan-e222.txt
    python3 -I -B tools/claims-v3/e222/plan_e222.py --check    re-makes them and compares (exit 0 = SAME)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STOP_W, DIE_STOP_C, DROP_LINE_W = 70.0, 70.0, 67.0
CARD = {
    "card": ("aifoundry3 card 0 (the box's one card, its device nodes at index 0; the card's lock /run/lock/etsoc-shire0.lock, held for the session; "
             "one session of ours on aifoundry3 at a time)"),
    "clock": "600 MHz pinned (a boot-time TDP of 0 latches the governor), read, never set (E218: 27,078 of 27,078 samples at 600 MHz)",
    "start_config_gate": "TDP 0 W, temperature threshold 65 C, minion 600 MHz, as found (read, nothing set; E207, E211, E213 arm A, E215 arm A and E218 read the same)",
    "live_stops": ("70 W x3 / 70 C (E218's): the board strictly above 70 W on 3 samples in a row (counting the samples that carry a board reading); the "
                   "shires' mean die (minshire[0]) at or above 70 C; the hottest-sensor latch (minshire[2]) at or above 70 C once it has risen during "
                   "the session above the lowest value it read since the session's first sample; a stop touches the host's stop file, never a kill"),
    "die_gate": "min(60, the session's rest die + 4) C, waited at most 300 s, else that run is NO DATA (E207's, E213 arm A's, E215 arm A's and E218's)",
    "run_form": ("its die gate, 10 s at rest, one host process '--seconds 6 --budget 7.5' under a plain 'timeout 10' (never -k; no SIGKILL to a device "
                 "process, sent or arranged), a 4 s tail (E206's and E218's form); the kit sizes the plain timeout so that no frozen GEMM's check of C "
                 "is cut off (E218's R0 lesson: f04's run 77, a 1.31 s GEMM, hit the plain timeout 10)"),
    "measured_peaks_on_this_card": ("E218 59.02 W, 55 C, latch 61 C (session 03:11:24-03:56:36 PST Fri 20 Nov 2026, 45.2 card-minutes, no stop; 107 of "
                                    "107 runs); E215 arm A 59.34 W (its gemmLnc smoke s03), shires 55 C, latch 61 C; E213 arm A 64.22 W (a075, "
                                    "gemmLnc3x1x3 fp32), 58 C, latch 51 -> 61 C; E211 61.9 W, 59 C; E210 58.66 W, 59 C; E207 51.26 W, 56 C: all under "
                                    "the 70 W / 70 C stops"),
    "rest": ("the first card command at least 40 minutes after the last session on aifoundry3 card 0 ended (E218's ended 03:56:36 PST Fri 20 Nov 2026; "
             "any later session counts; simulator runs on aifoundry3 are not card sessions)"),
    "box": ("aifoundry3, its card the lab's (no claim of the model session's stands on it); the desk is aifoundry2 (THE CPU RULE: the desk host's "
            "1-minute load under 6; /usr/bin/python3 3.12.3); THE ONE-LAB RULE's spans as E218's")}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build():
    P = json.load(open(os.path.join(HERE, "points-e222.json")))
    F = json.load(open(os.path.join(HERE, "forecast-e222.json")))
    plan = P["plan"]
    pp = {pid: {"PP32_W": r["PP32_W"], "PP_all_W": r["PP_all_W"], "PP_all_by": r["PP_all_by"], "role": r["role"], "token": r["token"],
                "mask": r["mask"], "seconds_per_gemm_v32": (r["models"].get("MM1-v3.2") or {}).get("seconds_per_gemm")} for pid, r in F["points"].items()}
    bad = [pid for pid, v in pp.items() if v["role"] == "point" and (v["PP32_W"] is None or v["PP32_W"] >= DROP_LINE_W)]
    if bad:
        print("plan_e222: REFUSED, a point's PP32 reaches the 67.0 W drop line:", bad)
        sys.exit(3)
    if plan["card_minutes_planned"] > plan["rule_min"]:
        print("plan_e222: REFUSED, the plan passes the rule")
        sys.exit(3)
    longest = sorted(((v["seconds_per_gemm_v32"] or 0.0), pid, v["token"]) for pid, v in pp.items())[-6:][::-1]
    out = {"experiment": "E222", "request": "Q236", "what": "the card, its stops and peaks, the order and the card time (registered before any E222 datum)",
           "points_sha256": sha(os.path.join(HERE, "points-e222.json")), "forecast_sha256": sha(os.path.join(HERE, "forecast-e222.json")),
           "card": CARD, "stop_W": STOP_W, "die_stop_C": DIE_STOP_C, "drop_line_W": DROP_LINE_W,
           "every_point_PP32_W": {pid: v["PP32_W"] for pid, v in pp.items()}, "every_point_PP_all_W_REPORTED": {pid: [v["PP_all_W"], v["PP_all_by"]] for pid, v in pp.items()},
           "highest_PP32": max((v["PP32_W"], pid) for pid, v in pp.items() if v["role"] == "point"),
           "highest_PP_all_REPORTED": max((v["PP_all_W"], pid, v["PP_all_by"]) for pid, v in pp.items() if v["role"] == "point"),
           "extra_rows_PP32": {pid: v["PP32_W"] for pid, v in pp.items() if v["role"] != "point"},
           "longest_GEMMs_by_MM1_v32_s": [{"id": pid, "token": t, "seconds_per_gemm": s} for s, pid, t in longest],
           "order": {"runs": plan["runs"], "pass1": plan["pass1"], "pass2": plan["pass2"], "G_block": plan["G_block"], "G_block_reversed": plan["G_block_reversed"]},
           "n_runs_scored_and_ties": plan["n_runs_scored_and_ties"], "n_smoke": plan["n_smoke"], "pace_s_per_run": plan["pace_s_per_run"],
           "pace_source": plan["pace_source"], "card_minutes_planned": plan["card_minutes_planned"], "target_min": plan["target_min"],
           "rule_min": plan["rule_min"], "cap_min": plan["cap_min"], "thinned": plan["thinned"], "registered_subset_if_cut": plan["registered_subset_if_cut"],
           "window": ("G = the card lane's booking on its day; last start G + 1:30, last end G + 3:30, each rounded up to the whole minute, inside the "
                      "Pacific day; G at 20:29:00 PST or earlier (Fri 20 Nov 2026 or a later day by a dated note), else from 00:00:30 PST the next day"),
           "post": "waived (his words of 10:22:36 PST Sun 15 Nov 2026)", "package_counter": "not read",
           "reads_only": ("dmcmd_audit_v2 GO with every send site READ before the first device access; no statistics reset, no set of any kind (TDP, "
                          "threshold, clock, voltage, governor), no reset, no PCIe recovery, no driver reload, no power cycle, no firmware change; et-who, "
                          "who, uptime and ps read before the session; the card's lock held for the session")}
    txt = [f"E222's plan (plan-e222.json): {CARD['card']}", f"clock: {CARD['clock']}", f"start config gate (read): {CARD['start_config_gate']}",
           f"live stops: {CARD['live_stops']}", f"drop line: {DROP_LINE_W} W (PP32 by MM1-v3.2); highest PP32 {out['highest_PP32'][0]:.2f} W at "
           f"{out['highest_PP32'][1]}; highest PP_all (REPORTED) {out['highest_PP_all_REPORTED'][0]:.2f} W at {out['highest_PP_all_REPORTED'][1]} "
           f"({out['highest_PP_all_REPORTED'][2]})", f"die gate: {CARD['die_gate']}", f"a run: {CARD['run_form']}",
           f"measured peaks on this card: {CARD['measured_peaks_on_this_card']}",
           f"card time planned: {plan['card_minutes_planned']:.1f} card-minutes ({plan['n_runs_scored_and_ties']} runs at {plan['pace_s_per_run']:.2f} s a "
           f"run: {plan['pace_source']}); the target {plan['target_min']:.0f}, the rule {plan['rule_min']:.0f}, the cap {plan['cap_min']:.0f}; thinned: "
           f"{plan['thinned'] or 'nothing'}", f"the registered subset if cut: {plan['registered_subset_if_cut']['what']}: "
           f"{plan['registered_subset_if_cut']['runs']} runs, about {plan['registered_subset_if_cut']['card_minutes']:.1f} card-minutes",
           f"the longest GEMMs (MM1-v3.2's seconds a GEMM, for the kit's timeout): " +
           ", ".join(f"{x['id']} {x['token']} {x['seconds_per_gemm']:.3f} s" for x in out["longest_GEMMs_by_MM1_v32_s"]),
           f"the rest: {CARD['rest']}", f"the box: {CARD['box']}", f"the window: {out['window']}",
           "every point's PP32 (W): " + ", ".join(f"{pid} {v:.2f}" for pid, v in out["every_point_PP32_W"].items() if v is not None),
           "order: " + " ".join(f"{r['block'].split(' ')[0]}:{r['id']}" for r in plan["runs"])]
    return json.dumps(out, indent=1, sort_keys=True, default=float) + "\n", "\n".join(txt) + "\n"


def main():
    js, tx = build()
    if "--check" in sys.argv:
        same = open(os.path.join(HERE, "plan-e222.json")).read() == js and open(os.path.join(HERE, "plan-e222.txt")).read() == tx
        print("plan_e222 --check:", "SAME" if same else "DIFFER")
        sys.exit(0 if same else 1)
    open(os.path.join(HERE, "plan-e222.json"), "w").write(js)
    open(os.path.join(HERE, "plan-e222.txt"), "w").write(tx)
    print("plan-e222.json", sha(os.path.join(HERE, "plan-e222.json")), "plan-e222.txt", sha(os.path.join(HERE, "plan-e222.txt")))
    print(tx.splitlines()[4])
    print(tx.splitlines()[8])
    print(tx.splitlines()[11])


if __name__ == "__main__":
    main()
