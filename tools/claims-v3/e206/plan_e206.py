#!/usr/bin/env python3
"""E206 (Q198): the registered plan - each arm's card, clock, gates, stops, line, predicted peaks, the order written out with each run's planned
seconds, the card-minute arithmetic, the cap and the 112-minute rule, the rests and the window form - and the refusal: the plan is REFUSED (exit 3,
no plan file) if a point on an arm has a predicted peak over that arm's line (F1's peak at its point, or the design's planning peak). Standard
library only.

    python3 -I -B tools/claims-v3/e206/plan_e206.py            writes plan-e206.json, prints plan-e206.txt (redirect stdout)
    python3 -I -B tools/claims-v3/e206/plan_e206.py --check    recomputes and compares with the committed plan-e206.json (exit 0 = PASS)

A RUN: its die gate (at most 300 s, else that run is NO DATA), 10 s read at rest (p_rest = the median of its last 5 s), ONE host process
`--seconds 6 --budget 7.5` under a plain `timeout 10` (never -k: no SIGKILL is sent or arranged to a device process), the 4 s tail. The planned
seconds of a run are the design's (desk/design-planning-e206.json: E190's measured 21-22 s a burst run plus a gate allowance by heat class); the
same arithmetic with F1's slowest seconds a GEMM is printed beside them as a check. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PTS = json.load(open(os.path.join(HERE, "points-e206.json")))
FC = json.load(open(os.path.join(HERE, "forecast-e206.json")))
DES = json.load(open(os.path.join(HERE, "desk", "design-planning-e206.json")))
ARMS = ("A", "B")
REST_READ_S, TAIL_S, OVERHEAD_S, SMOKE_S = 10.0, 4.0, 0.5, 90.0
GATE_ALLOW_S = {"hot": 6.0, "warm": 2.0, "cool": 0.5}
NO_NEW_RUN_MIN, CAP_MIN = 112.0, 120.0
REST_BETWEEN_SESSIONS_MIN = 40.0
S2_REL = 0.10


def both_can_pass(a, b, th):
    """two forecasts a and b can both lie within th of one measurement iff max / min <= (1 + th) / (1 - th) (verify5's test, ledger_v3.py)"""
    lo, hi = min(a, b), max(a, b)
    return hi / lo <= (1.0 + th) / (1.0 - th)


def f1_run_s(pid, arm):
    p = next(x for x in PTS["points"] if x["id"] == pid)
    fp = FC["points"][pid]
    gb = p["bytes_MB"]["all"] * 2 ** 20 / 1e9
    proc = 6.3 + 1.0 * gb + fp["F1_speed"]["t_gemm_s"]["band"][1] + 0.1
    wtop = fp["arms"][arm]["F1"]["W_over"]["band"][1]
    heat = "hot" if wtop > 25 else "warm" if wtop > 12 else "cool"
    return GATE_ALLOW_S[heat] + REST_READ_S + proc + TAIL_S + OVERHEAD_S, proc


def build():
    refused = []
    arms = {}
    for arm in ARMS:
        on = [p["id"] for p in PTS["points"] if p["on_arm"][arm]]
        over_f1 = [pid for pid in on if FC["points"][pid]["arms"][arm]["F1"]["peak_point_w"] > FC["constants"]["line_w"][arm]]
        over_des = [pid for pid in on if DES["points"][pid]["arms"][arm]["board_peak_w"] > DES["arms"][arm]["line_predicted_peak_w"]]
        if over_f1 or over_des:
            refused.append((arm, over_f1, over_des))
        seq = PTS["order"][arm]["sequence"]
        rows, t_des, t_f1 = [], SMOKE_S, SMOKE_S
        for s in seq:
            rs = DES["points"][s["id"]]["arms"][arm]["run_s"]
            rf, proc = f1_run_s(s["id"], arm)
            t_des += rs
            t_f1 += rf
            rows.append({"n": s["n"], "block": s["block"], "id": s["id"], "name": s["name"], "run_s_plan": rs, "run_s_f1_slow": round(rf, 2),
                         "proc_s_f1_slow": round(proc, 2), "cum_min_plan": round(t_des / 60.0, 2)})
        n_after = sum(1 for r in rows if r["cum_min_plan"] > NO_NEW_RUN_MIN)
        sep = {"S2_both_can_pass": 0, "S2_exclusive": 0, "not_priced": 0}
        for pid in on:
            c = FC["points"][pid]["arms"][arm]
            if not c["F2"]["priced"]:
                sep["not_priced"] += 1
                continue
            if both_can_pass(c["F1"]["J_over"]["point"], c["F2"]["J_over"]["point"], S2_REL):
                sep["S2_both_can_pass"] += 1
            else:
                sep["S2_exclusive"] += 1
        hi_f1 = max(on, key=lambda pid: FC["points"][pid]["arms"][arm]["F1"]["peak_point_w"])
        hi_f1b = max(on, key=lambda pid: FC["points"][pid]["arms"][arm]["F1"]["peak_band_top_w"])
        hi_des = max(on, key=lambda pid: DES["points"][pid]["arms"][arm]["board_peak_w"])
        a = DES["arms"][arm]
        arms[arm] = {
            "card": {"A": "aifoundry3 card 0 (/dev/et0_*; the card's lock /run/lock/etsoc-shire0.lock)",
                     "B": "aifoundry1 card 1 (ET_DEVICES=1 on every device process; the card's lock /run/lock/etsoc-shire1.lock); nothing on card 0; "
                          "never two sessions of ours on aifoundry1 at once"}[arm],
            "clock": a["clock"], "start_config_gate": {"A": "TDP 0 W, 65 C, 600 MHz as found (read, nothing set)",
                                                        "B": "TDP 65 W, 65 C, 600 MHz as found (read, nothing set)"}[arm],
            "line_w": a["line_predicted_peak_w"], "stop": a["stop"], "gate": a["gate"], "gate_max_wait_s": a["gate_max_wait_s"],
            "points": len(on), "runs": len(seq), "excluded_by_line": a["excluded_by_line"],
            "predicted_peak": {"F1_point": {"id": hi_f1, "w": FC["points"][hi_f1]["arms"][arm]["F1"]["peak_point_w"]},
                               "F1_band_top": {"id": hi_f1b, "w": FC["points"][hi_f1b]["arms"][arm]["F1"]["peak_band_top_w"]},
                               "design_planning": {"id": hi_des, "w": DES["points"][hi_des]["arms"][arm]["board_peak_w"],
                                                   "die_c": DES["points"][hi_des]["arms"][arm]["die_peak_c"]},
                               "max_planning_die_c": max(DES["points"][pid]["arms"][arm]["die_peak_c"] for pid in on)},
            "card_minutes": {"plan": round(t_des / 60.0, 1), "f1_slow_end_check": round(t_f1 / 60.0, 1), "no_new_run_after_min": NO_NEW_RUN_MIN,
                             "cap_min": CAP_MIN, "runs_planned_after_112_min": n_after,
                             "registered_subset_if_cut": "the smoke, tie 1, pass 1 and tie 2: every point once"},
            "separation_S2": sep, "rows": rows}
    if refused:
        return None, refused
    plan = {
        "experiment": "E206", "request": "Q198", "what": "the registered plan; the kit implements it; a departure is a dated amendment before the data it touches",
        "arms": arms,
        "smoke": "30 s at rest (the session's rest reading; the die gates from it); one checked 2 s process each of p001 (2,048^3 fp32), p046 (2,048^3 "
                 "fp16) and p021 (2,048^3 int8): each rc 0, every launch ok, the check of C exact or approx, its cycles an op 50-250% of F1's point, "
                 "the board 2 W or more over the rest, the host on the arm's own card; then the stop-path test on live samples (no launch)",
        "order": "tie (p001), pass 1 (tier 1, tier 2, tier 3, each in its seeded order), tie, pass 2 (pass 1 reversed), tie: points-e206.json order",
        "run": {"rest_read_s": REST_READ_S, "tail_s": TAIL_S, "process": "--seconds 6 --budget 7.5 under a plain timeout 10 (never -k)",
                "gate_allow_s": GATE_ALLOW_S, "overhead_s": OVERHEAD_S, "smoke_s": SMOKE_S},
        "rules": {"no_new_run_after_min": NO_NEW_RUN_MIN, "cap_min": CAP_MIN,
                  "text": "no run starts once the arm's card time (its first device access to now) passes 112 minutes; at 120 the session ends after the "
                          "run in progress (a started run is cut only by a stop); a stop touches the host's --stop-file (the host ends at its next "
                          "launch boundary), never a kill"},
        "rests": f"each arm's first card command at least {REST_BETWEEN_SESSIONS_MIN:.0f} minutes after our previous session on that box ended "
                 "(on aifoundry1, either card)",
        "window": "G = each arm's booking on its day; last start G + 1:30, last end G + 3:30, each rounded up to the whole minute, inside the Pacific day; "
                  "G at 20:29:00 PST or earlier",
        "boxes": "arm A on aifoundry3 after E202's card day there; arm B on aifoundry1 card 1 when aifoundry1 is the lab's (it was yielded to the model "
                 "session's own matmul sweeps at 11:04 PST Mon 16 Nov 2026; arm B runs only if aifoundry1 comes back to the lab before its window "
                 "closes, else its points are NO DATA); the two arms, on two boxes, may run at the same time",
        "reads_only": "dmcmd_audit_v2 GO with every send site READ before the first device access; no statistics reset, no set of any kind (TDP, "
                      "threshold, clock, voltage), no reset, no power cycle, no firmware change; et-who, who, uptime and ps read before each session; the "
                      "card's lock held for the session; every device process under a plain timeout 10; the host's package counter is not read; the "
                      "owner waived the Discord post (his words, Sun 15 Nov 2026 10:22:36 PST: \"don't worry about discord post, just use the machines\")",
    }
    return plan, []


def text(plan):
    L = []
    for arm in ARMS:
        a = plan["arms"][arm]
        pk = a["predicted_peak"]
        L.append(f"arm {arm}: {a['card']}; {a['clock']}; {a['points']} points, {a['runs']} runs; card time planned {a['card_minutes']['plan']} card-minutes "
                 f"(F1's slow end {a['card_minutes']['f1_slow_end_check']}), no run after 112, cap 120; runs planned after 112 min: "
                 f"{a['card_minutes']['runs_planned_after_112_min']}")
        L.append(f"  line {a['line_w']:.0f} W; stops: board above {a['stop']['board_w_above']:.0f} W on {a['stop']['samples_in_a_row']} samples, die at or above "
                 f"{a['stop']['die_c_at_or_above']:.0f} C; gate {a['gate']}, at most {a['gate_max_wait_s']} s")
        L.append(f"  predicted peaks: F1 at its point {pk['F1_point']['w']:.1f} W ({pk['F1_point']['id']}), F1 at its band's top {pk['F1_band_top']['w']:.1f} W "
                 f"({pk['F1_band_top']['id']}), the design's planning {pk['design_planning']['w']:.1f} W ({pk['design_planning']['id']}, die "
                 f"{pk['design_planning']['die_c']:.1f} C); highest planning die {pk['max_planning_die_c']:.1f} C; excluded by the line: "
                 f"{a['excluded_by_line'] or 'none'}")
        s = a["separation_S2"]
        L.append(f"  separation (S2, 10%): F1 and F2 can both pass at {s['S2_both_can_pass']} points, at most one at {s['S2_exclusive']}, F2 not priced at "
                 f"{s['not_priced']}")
        for r in a["rows"]:
            L.append(f"    {r['n']:3d} {r['block']:5s} {r['id']} {r['name']:34s} ~{r['run_s_plan']:5.1f} s (F1 slow end {r['run_s_f1_slow']:5.1f}); "
                     f"cum {r['cum_min_plan']:6.2f} min")
    L.append(f"rests: {plan['rests']}")
    L.append(f"window: {plan['window']}")
    L.append(f"boxes: {plan['boxes']}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    plan, refused = build()
    if plan is None:
        print(f"PLAN REFUSED: a predicted peak passes its arm's line: {refused}")
        sys.exit(3)
    path = os.path.join(HERE, "plan-e206.json")
    if a.check:
        same = json.load(open(path)) == json.loads(json.dumps(plan))
        ok = all(plan["arms"][x]["card_minutes"]["plan"] <= CAP_MIN for x in ARMS)
        print(f"plan_e206 --check: recomputed == committed: {same}; each arm's planned card time under the {CAP_MIN:.0f} min cap: {ok}; every point's peak "
              f"under its arm's line (F1 at the point and the design's planning): True")
        print("PASS" if (same and ok) else "FAIL")
        sys.exit(0 if (same and ok) else 1)
    json.dump(plan, open(path, "w"), indent=1)
    sys.stdout.write(text(plan))


if __name__ == "__main__":
    main()
