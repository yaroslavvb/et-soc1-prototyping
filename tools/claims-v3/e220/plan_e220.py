#!/usr/bin/env python3
"""E220 (Q233): the cards, their stops and peaks, the order and the card time per arm, from points-e220.json (the rule's order and plan) and
forecast-e220.json (each run's predicted peak). Standard library only. Refuses (exit 3) a point whose PP32 reaches its arm's drop line, or a plan
whose card time passes its arm's rule.

    python3 -I -B tools/claims-v3/e220/plan_e220.py            writes plan-e220.json and plan-e220.txt
    python3 -I -B tools/claims-v3/e220/plan_e220.py --check    re-makes them and compares (exit 0 = SAME)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
CARD = {
    "A": {"card": "aifoundry1 card 1 (the card's device nodes at index 1; ET_DEVICES=1 on every device process); the card's lock "
                  "/run/lock/etsoc-shire1.lock, held for the session; one session of ours on aifoundry1 at a time; nothing on card 0 but A2's one "
                  "firmware read (fwgate, below)",
          "clock": "600 MHz as found (every sample since September; E215 arm B 17,106 of 17,106 samples at 600 MHz), read, never set",
          "start_config_gate": "TDP 65 W, temperature threshold 65 C, minion 600 MHz, as found (read, nothing set; E213 arm B and E215 arm B read the same)",
          "live_stops": ("the board strictly above 72 W on 3 samples in a row; the die at or above 80 C (the shires' mean, or the hottest-sensor latch "
                         "minshire[2] once it has risen during the session above the lowest value it read) - E215 arm B's lines on this card"),
          "stop_W": 72.0, "die_stop_C": 80.0,
          "die_gate": "min(63, the session's rest die + 3) C, waited at most 300 s, else that run is NO DATA (E206's, E213 arm B's and E215 arm B's)",
          "run_form": ("its die gate, 10 s at rest, one host process '--seconds 6 --budget 7.5' under a plain 'timeout 10' (never -k; no SIGKILL to a "
                       "device process, sent or arranged), a 4 s tail (E215 arm B's form); the kit sizes the timeout so that no frozen GEMM's check "
                       "of C is cut off (E218's R0 lesson: f04 run 77)"),
          "measured_peaks_on_this_card": ("E215 arm B 66 W (its gemmLnc smoke s14 at 14:09:57), its gemmLnc point b013 55.13 W, latch 59 C (session "
                                          "13:42:22-14:10:55 PST Thu 19 Nov 2026, 28.55 card-minutes, no stop); E213 arm B TRIPPED its 72 W x3 stop "
                                          "at run 079 (k37, gemmLnc3x1x3 fp32: 72.24 W on 3 samples; its W over idle 1.69 x MM1-v3.1's) - "
                                          "MM1-v3.2's gemmLnc term was fitted with it; E217's card-1 sessions 62.1-67.8 W at gemmL1x1x1 fp32"),
          "rest": ("the first card command at least 40 minutes after the last session on aifoundry1 ended, either card, ours or the model session's, "
                   "and THE REST RULE: no write under the model session's ~/claude/work/ee-*/ on aifoundry1 within the last 40 minutes (E215 arm B's "
                   "second booking: its first was refused by that rule)"),
          "window_box": "aifoundry1 (no claim of the model session's may stand on it: while one stands the queue reads CANCELLED and arm A waits)"},
    "B": {"card": "aifoundry2 card 0 (/dev/et0_mgmt, /dev/et0_ops; the box's one card); the card's lock /run/lock/etsoc-shire0.lock, held for "
                  "the session; one session of ours on aifoundry2 at a time",
          "clock": ("under its own governor, as found (each process from the 600 MHz boot point, stepped to 800 MHz within about 1.5 s while the board "
                    "stays under its 65 W TDP; 600 / 700 / 800 MHz), read never set; the forecasts' registered clock 799.0 MHz (route c)"),
          "start_config_gate": ("TDP 65 W, temperature threshold 65 C, minion 600 MHz at rest, power state 3; the config read names /dev/et0_mgmt and "
                                "physical device ID 0 (E208's, E209's and E216's gate on this card)"),
          "live_stops": ("the board strictly above 70 W on 3 samples in a row; the shires' mean die (minshire[0]) at or above 70 C; the hottest-sensor "
                         "latch (minshire[2]) at or above 70 C once it has risen during the session - E216's lines on this card"),
          "stop_W": 70.0, "die_stop_C": 70.0,
          "die_gate": "the shires' mean at or below 55 C, waited at most 180 s (E208's, E209's and E216's gate on this card)",
          "run_form": ("E216's run form (E208's runner and schedule form, the plain 'timeout 10', never -k; no SIGKILL to a device process, sent or "
                       "arranged); the kit sizes the timeout so that no frozen GEMM's check of C is cut off"),
          "measured_peaks_on_this_card": ("E216 62.25 W board, die 53 C, latch 54-56 C (session 16:55:55-17:23:32 PST Thu 19 Nov 2026, 27.55 "
                                          "card-minutes, no stop; 69 of 69 runs); E209 69.55 W (e44, planned 69.21 W), 55 C; E212 a2c0-S3 re-run "
                                          "61.28 W, 52 C; E208 a2c0-S1r 71.49 W, 58 C (E208's sessions ran under 85 W x3 / 80 C)"),
          "governor_note": ("a point planned with PP32 above 64.0 W (E216's governor line: at or above it the governor may hold the clock under 800 "
                            "MHz) may read route m (scored against the 700 or 600 MHz column, REPORTED); listed below"),
          "rest": ("the first card command at least 40 minutes after the last session on aifoundry2 card 0 ended (ours or the model session's; E216's "
                   "ended 17:23:32 PST Thu 19 Nov 2026; any later session counts)"),
          "window_box": ("aifoundry2, the round's desk and this card's host: no claim of the model session's may stand on it; THE QUIET DESK FLAG "
                         "(W/locks/quiet-desk-aifoundry2) is raised by arm B's card lane only after arm A's launch line has been seen, before arm B's "
                         "first card command, and removed after its last, on every path; THE CPU RULE (the host's 1-minute load under 6)")}}


D1 = {
    "what": ("D1 (safety, before any datum; a departure from POINT-RULE-e220.md section 5's smoke rows only - no point, forecast or rule changes): "
             "MM1-v3.2's planning peaks of the rule's smoke rows pass their arms' drop lines (arm A s03 gemmLnc2x2x2 73.07 W against 69 W; arm B s01 "
             "gemmL2x2x2 70.02 W and s03 gemmLnc2x2x2 91.01 W against 67 W, forecast-e220.json), so each smoke row is replaced by a configuration that "
             "ran on that card under its stop, from the card's committed record"),
    "A": {"s01": {"run": "gemmL2x2x2 fp32 random, the full chip (kept: PP32 58.35 W, under the line)", "kept": True},
          "s03": {"run": "gemmLnc2x1x37 fp32 random, the full chip (E215 arm B's b013 on this card: board peak 55.13 W, Thu 19 Nov 2026, data 4f648f24)",
                  "replaces": "gemmLnc2x2x2 (E213 arm B's and E215 arm B's s14 on this card: 66.1 W and 66 W measured; PP32 73.07 W)"}},
    "B": {"s01": {"run": ("E216's opening smoke on this card: E208's three smoke arms 1x1x4-fp16-ones, 1x1x4-fp32-zeros and 1x1x4-int8-rnd "
                          "(gemmL1x1x4 in fp16 ones, fp32 zeros, int8 random; measured rises 10.37, 7.47 and 14.52 W, E216 data a8ce142d)"),
                  "replaces": "gemmL2x2x2 fp32 (PP32 70.02 W at 799.0 MHz)"},
          "s03": {"run": ("gemmLnc6x5x10 fp32 random, the full chip (E216's g10 on this card at 799 MHz: the session's board never above 62.25 W, "
                          "data a8ce142d)"),
                  "replaces": "gemmLnc2x2x2 fp32 (PP32 91.01 W at 799.0 MHz)"}}}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build():
    P = json.load(open(os.path.join(HERE, "points-e220.json")))
    F = json.load(open(os.path.join(HERE, "forecast-e220.json")))
    out = {"experiment": "E220", "request": "Q233", "points_sha256": sha(os.path.join(HERE, "points-e220.json")),
           "forecast_sha256": sha(os.path.join(HERE, "forecast-e220.json")), "arms": {}}
    for arm in ("A", "B"):
        a = P["arms"][arm]
        plan = a["plan"]
        line = a["drop_line_W"]
        fc = F["arms"][arm]["points"]
        pts = {p["id"]: p for p in P["points"][arm]}
        bad = [i for i, p in pts.items() if p["PP32_W"] is None or p["PP32_W"] >= line]
        if bad:
            print(f"plan_e220: REFUSED, arm {arm} points at or above the drop line {line} W: {bad}")
            sys.exit(3)
        if plan["card_minutes_planned"] > plan["rule_min"]:
            print(f"plan_e220: REFUSED, arm {arm} plans {plan['card_minutes_planned']:.1f} card-minutes, over the rule {plan['rule_min']}")
            sys.exit(3)
        runs = []
        for r in plan["runs"]:
            x = fc.get(r["id"]) or {}
            row = {"n": r["n"], "block": r["block"], "id": r["id"], "token": x.get("token"), "fmt": x.get("fmt"), "mask": x.get("mask"),
                   "PP32_W": x.get("PP32_W"), "PP_all_W": x.get("PP_all_W"), "PP_all_by": x.get("PP_all_by")}
            d1 = D1[arm].get(r["id"]) if r["block"] == "smoke" else None
            if d1 and not d1.get("kept"):
                row = {"n": r["n"], "block": "smoke", "id": r["id"], "D1": d1["run"], "replaces": d1["replaces"],
                       "PP_from": "the card's committed measured record (D1), not a forecast"}
            runs.append(row)
        top = sorted(((p["PP32_W"], i) for i, p in pts.items()), reverse=True)[:5]
        gov = sorted(i for i, p in pts.items() if arm == "B" and p["PP32_W"] >= 64.0)
        out["arms"][arm] = dict(CARD[arm])
        out["arms"][arm].update({
            "drop_line_W": line, "drop_rule": f"no point whose PP32 (MM1-v3.2's planning peak) is at or above the {CARD[arm]['stop_W']:.0f} W stop less 3 W",
            "highest_PP32": [{"id": i, "PP32_W": v} for v, i in top],
            "highest_PP_all_W": max(p["PP_all_W"] for p in pts.values() if p["PP_all_W"] is not None),
            "points_PP32_at_or_above_64W_route_m_risk_REPORTED": gov,
            "every_point_PP32_W": {i: round(p["PP32_W"], 2) for i, p in pts.items()},
            "n_points": len(pts), "counts": a["counts"], "x_dropped": [{"id": c["e218_id"], "why": c["dropped"]} for c in a["x_dropped"]],
            "order": {"pass1": plan["pass1"], "pass2": plan["pass2"], "G_block": plan["G_block"], "G_block_reversed": plan["G_block_reversed"],
                      "how": ("s01; t01; pass 1 (every non-gemmLnc point once, random.Random('E220|" + arm + "|pass1')'s shuffle of the sorted ids); t01; "
                              "pass 2 (the L3 and Y2 points again, pass 1's order reversed); t01; the G block last: s03, every gemmLnc point once by "
                              "PP32 ascending, then the G2 points again in reverse")},
            "runs": runs, "n_runs": plan["n_runs_scored_and_ties"], "n_smoke": plan["n_smoke"],
            "card_time": {"planned_card_minutes": round(plan["card_minutes_planned"], 2), "pace_s_per_run": round(plan["pace_s_per_run"], 2),
                          "pace_source": plan["pace_source"], "rule_card_minutes": plan["rule_min"], "cap_card_minutes": plan["cap_min"],
                          "rule_how": "no run starts after the rule from the first card command; the session ends at the cap, after the run in progress"},
            "registered_subset_if_cut": plan["registered_subset_if_cut"],
            "departure_D1_smoke": {"what": D1["what"], "rows": D1[arm]}})
    return out


def text(out):
    L = []
    for arm in ("A", "B"):
        a = out["arms"][arm]
        L.append(f"=== arm {arm}: {a['card']}")
        for k in ("clock", "start_config_gate", "live_stops", "die_gate", "run_form", "measured_peaks_on_this_card", "rest", "window_box"):
            L.append(f"{k}: {a[k]}")
        if arm == "B":
            L.append(f"governor_note: {a['governor_note']}: {a['points_PP32_at_or_above_64W_route_m_risk_REPORTED']}")
        L.append(f"drop line {a['drop_line_W']} W ({a['drop_rule']}); highest PP32: {a['highest_PP32']}; highest PP_all {a['highest_PP_all_W']:.2f} W")
        L.append(f"points {a['n_points']} {a['counts']}; X dropped {a['x_dropped']}")
        ct = a["card_time"]
        L.append(f"card time: {a['n_runs']} runs (ties and points) + {a['n_smoke']} smoke at {ct['pace_s_per_run']} s a run ({ct['pace_source']}) = "
                 f"{ct['planned_card_minutes']} card-minutes; rule {ct['rule_card_minutes']}, cap {ct['cap_card_minutes']}")
        s = a["registered_subset_if_cut"]
        L.append(f"registered subset if cut: {s['what']}: {s['runs']} runs, about {s['card_minutes']:.1f} card-minutes")
        L.append("D1 (the smoke rows): " + "; ".join(f"{k}: {v['run']}" + (f" (replaces {v['replaces']})" if v.get("replaces") else "") for k, v in a["departure_D1_smoke"]["rows"].items()))
        L.append("runs: " + " ".join(f"{r['n']}:{r['id']}" for r in a["runs"]))
    return "\n".join(L) + "\n"


def main():
    out = build()
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    tx = text(out)
    if "--check" in sys.argv:
        same = open(os.path.join(HERE, "plan-e220.json")).read() == js and open(os.path.join(HERE, "plan-e220.txt")).read() == tx
        print("plan_e220 --check:", "SAME" if same else "DIFFER")
        sys.exit(0 if same else 1)
    open(os.path.join(HERE, "plan-e220.json"), "w").write(js)
    open(os.path.join(HERE, "plan-e220.txt"), "w").write(tx)
    for arm in ("A", "B"):
        a = out["arms"][arm]
        print(f"arm {arm}: {a['n_points']} points, {a['n_runs']} runs, {a['card_time']['planned_card_minutes']} card-minutes; highest PP32 "
              f"{a['highest_PP32'][0]}; line {a['drop_line_W']} W")


if __name__ == "__main__":
    main()
