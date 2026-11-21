#!/usr/bin/env python3
"""E224 (Q237): the cards, their stops and predicted peaks, the order and the card time per arm, from points-e224.json (the rule's order and
plan) and forecast-e224.json (each run's predicted peak by MM1-v3.2 and by every forecaster). Standard library only. Refuses (exit 3) a point whose
PP32 reaches its arm's drop line, a plan whose card time passes its arm's rule, or a GEMM MM1-v3.2 prices over the 0.40 s cap.

    python3 -I -B tools/claims-v3/e224/plan_e224.py            writes plan-e224.json and plan-e224.txt
    python3 -I -B tools/claims-v3/e224/plan_e224.py --check    re-makes them and compares (exit 0 = SAME)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POINTS = ("points-e224.json", "44c790ffa5bc619029dd3f16c1cd8cf269c91f45d6681b9642ddd133ac30e340")
FORECAST = ("forecast-e224.json", "31b1202ca8156604f5fa51c51a6bf430926e5dced2dec4bf4b9ac4620f1d2d41")
REG = {"A": "600.0", "B": "799.0"}
SEC_CAP_S = 0.40
CARD = {
    "A": {"card": ("aifoundry1 card 1 (the card's device nodes at index 1; ET_DEVICES=1 on every device process); the card's lock "
                   "/run/lock/etsoc-shire1.lock, held for the session; one session of ours on aifoundry1 at a time; nothing on card 0 but fwgate's one "
                   "firmware read (E213's Amendment A2 form)"),
          "clock": "600 MHz as found (read, never set; E215 arm B 17,106 of 17,106 samples at 600 MHz)",
          "start_config_gate": "TDP 65 W, temperature threshold 65 C, minion 600 MHz, as found (read, nothing set; E213 arm B's and E215 arm B's reads)",
          "live_stops": ("the board strictly above 72 W on 3 samples in a row; the die at or above 80 C (the shires' mean, or the hottest-sensor latch "
                         "minshire[2] once it has risen during the session above the lowest value it read) - E215 arm B's and E220 arm A's lines"),
          "stop_W": 72.0, "die_stop_C": 80.0, "drop_line_W": 69.0,
          "die_gate": "min(63, the session's rest die + 3) C, waited at most 300 s, else that run is NO DATA (E215 arm B's, E220 arm A's)",
          "run_form": ("its die gate, 10 s at rest, one host process '--seconds 6 --budget 7.5' under a plain 'timeout 10' (never -k; no SIGKILL to a "
                       "device process, sent or arranged), a 4 s tail (E215 arm B's and E220 arm A's form); the kit sizes the timeout so that no "
                       "frozen GEMM's check of C is cut off (E218's R0 lesson)"),
          "measured_peaks_on_this_card_quoted": ("E215 arm B 66 W (its gemmLnc smoke s14), its gemmLnc point b013 55.13 W, latch 59 C (Thu 19 Nov 2026, "
                                                 "data 4f648f24, no stop); E213 arm B TRIPPED its 72 W x3 stop at k37 (gemmLnc3x1x3 fp32, 72.24 W); "
                                                 "E217's card-1 sessions 62.1-67.8 W at gemmL1x1x1 fp32"),
          "rest": ("the first card command at least 40 minutes after the last session on aifoundry1 ended, either card, ours or the model session's "
                   "(E220 arm A's session this afternoon counts), and THE REST RULE: no write under the model session's ~/claude/work/ee-*/ on "
                   "aifoundry1 within the last 40 minutes"),
          "box": "aifoundry1 (no claim of the model session's may stand on it: while one stands the queue reads CANCELLED and arm A waits)"},
    "B": {"card": ("aifoundry2 card 0 (/dev/et0_mgmt, /dev/et0_ops; the box's one card); the card's lock /run/lock/etsoc-shire0.lock, held for "
                   "the session; one session of ours on aifoundry2 at a time"),
          "clock": ("under its own governor, as found (each process from the 600 MHz boot point, stepped to 800 MHz within about 1.5 s while the board "
                    "stays under its 65 W TDP), read never set; the forecasts' registered clock 799.0 MHz (route c), 700 and 600 MHz columns (route m)"),
          "start_config_gate": ("TDP 65 W, temperature threshold 65 C, minion 600 MHz at rest, power state 3; the config read names /dev/et0_mgmt and "
                                "physical device ID 0 (E208's, E209's, E216's and E220 arm B's gate on this card)"),
          "live_stops": ("the board strictly above 70 W on 3 samples in a row; the shires' mean die (minshire[0]) at or above 70 C; the hottest-sensor "
                         "latch (minshire[2]) at or above 70 C once it has risen during the session - E216's and E220 arm B's lines"),
          "stop_W": 70.0, "die_stop_C": 70.0, "drop_line_W": 67.0,
          "die_gate": "the shires' mean at or below 55 C, waited at most 180 s (E208's, E209's, E216's and E220 arm B's gate on this card)",
          "run_form": ("E216's run form (E208's runner and schedule form, the plain 'timeout 10', never -k; no SIGKILL to a device process, sent or "
                       "arranged); the kit sizes the timeout so that no frozen GEMM's check of C is cut off"),
          "measured_peaks_on_this_card_quoted": ("E216 62.25 W board, die 53 C, latch 54-56 C (Thu 19 Nov 2026, data a8ce142d, no stop); E209 69.55 W "
                                                 "(e44), 55 C; E212 a2c0-S3 re-run 61.28 W, 52 C; E208 a2c0-S1r 71.49 W, 58 C (under 85 W x3 / 80 C)"),
          "governor_note": ("a point planned with PP32 above 64.0 W (E216's governor line: at or above it the governor may hold the clock under 800 "
                            "MHz) may read route m (scored against the 700 or 600 MHz column, REPORTED); listed in governor_route_m_risk"),
          "rest": ("the first card command at least 40 minutes after the last session on aifoundry2 card 0 ended (ours or the model session's: E220 "
                   "arm B's this afternoon and E221's a2c0-S3 after it count)"),
          "box": ("aifoundry2, the round's desk and this card's host: no claim of the model session's may stand on it; THE QUIET DESK FLAG "
                  "(W/locks/quiet-desk-aifoundry2) is raised by arm B's card lane only after arm A's launch line has been seen, before arm B's first "
                  "card command, and removed after its last, on every path; THE CPU RULE (the host's 1-minute load under 6)")}}
SMOKE_NOTE = {
    "A": {"s01": "gemmL2x2x2 fp32 random, the full chip (E220 arm A's s01, kept there: PP32 58.35 W)",
          "s03": ("gemmLnc2x1x37 fp32 random, the full chip (E220 arm A's s03 by its departure D1: E215 arm B's b013 on this card, board peak 55.13 W, "
                  "data 4f648f24)")},
    "B": {"s01": ("E216's opening smoke on this card (E220 arm B's s01 by its D1): E208's three smoke arms 1x1x4-fp16-ones, 1x1x4-fp32-zeros, "
                  "1x1x4-int8-rnd (gemmL1x1x4; measured rises 10.37, 7.47 and 14.52 W, data a8ce142d)"),
          "s03": ("gemmLnc6x5x10 fp32 random, the full chip (E220 arm B's s03 by its D1: E216's g10 on this card at 799 MHz, in a session whose board "
                  "never passed 62.25 W, data a8ce142d); its PP32 by MM1-v3.2 (x (1 + 2 eps_G)) reads over the 67 W line: the smoke is never a point "
                  "and the committed record on this card is the registered basis, as in E220")}}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def make():
    for n, h in (POINTS, FORECAST):
        if sha(os.path.join(HERE, n)) != h:
            print(f"plan_e224: REFUSED, {n} is not its frozen file")
            sys.exit(4)
    P = json.load(open(os.path.join(HERE, POINTS[0])))
    F = json.load(open(os.path.join(HERE, FORECAST[0])))
    out = {"experiment": "E224", "request": "Q237", "points_sha256": POINTS[1], "forecast_sha256": FORECAST[1], "arms": {}}
    L = []
    for arm in ("A", "B"):
        c = dict(CARD[arm])
        pl = P["plan"][arm]
        pts = {p["id"]: p for p in P["points"][arm]}
        fa = F["arms"][arm]["points"]
        every = {}
        for pid, p in pts.items():
            x = fa[pid]
            s = x["clocks"]["600.0" if arm == "A" else "600.0"]["MM1-v3.2"]["seconds_per_gemm"]
            every[pid] = {"PP32_W": x["PP32_W"], "PP_all_W": x["PP_all_W"], "PP_all_by": x["PP_all_by"], "seconds_per_gemm_at_600MHz_v32": s,
                          "token": p["token"], "format": p["format"], "kind": p["kind"], "mask": p["shire_mask"]}
            if x["PP32_W"] >= c["drop_line_W"]:
                print(f"plan_e224: REFUSED, {arm}:{pid} PP32 {x['PP32_W']:.2f} W at or over the {c['drop_line_W']} W line")
                sys.exit(3)
            if s is None or s > SEC_CAP_S:
                print(f"plan_e224: REFUSED, {arm}:{pid} MM1-v3.2's seconds a GEMM {s} over the {SEC_CAP_S} s cap")
                sys.exit(3)
        if pl["card_minutes_planned"] > pl["rule_min"]:
            print(f"plan_e224: REFUSED, arm {arm}'s plan {pl['card_minutes_planned']:.1f} card-minutes over its rule {pl['rule_min']}")
            sys.exit(3)
        extra = {i: {"token": x["token"], "format": x["format"], "kind": x["kind"], "PP32_W": x["PP32_W"], "PP_all_W": x["PP_all_W"],
                     "note": SMOKE_NOTE[arm].get(i[:3], "the tie t01: gemmL2x4x4 fp32 random, the full chip (E206's and E218's; a bridge on all three cards)")}
                 for i, x in F["extra_rows"][arm].items()}
        runs = []
        for r in pl["runs"]:
            pid = r["id"]
            if pid in pts:
                runs.append(dict(r, PP32_W=fa[pid]["PP32_W"], token=pts[pid]["token"], format=pts[pid]["format"], kind=pts[pid]["kind"],
                                 mask=pts[pid]["shire_mask"]))
            else:
                runs.append(dict(r))
        hi = max(every.items(), key=lambda kv: kv[1]["PP32_W"])
        hia = max(every.items(), key=lambda kv: kv[1]["PP_all_W"])
        longest = max(every.items(), key=lambda kv: kv[1]["seconds_per_gemm_at_600MHz_v32"])
        c.update({"points": len(pts), "runs_scored_and_ties": pl["n_runs_scored_and_ties"], "smoke_processes": pl["n_smoke"],
                  "pace_s_per_run": pl["pace_s_per_run"], "pace_source": pl["pace_source"], "card_minutes_planned": pl["card_minutes_planned"],
                  "target_min": pl["target_min"], "rule_min": pl["rule_min"], "cap_min": pl["cap_min"], "thinned": pl["thinned"],
                  "registered_subset_if_cut": pl["registered_subset_if_cut"], "highest_PP32": {"id": hi[0], **hi[1]},
                  "highest_PP_all_REPORTED": {"id": hia[0], **hia[1]}, "longest_gemm_v32_600MHz": {"id": longest[0], **longest[1]},
                  "every_point": every, "extra_rows": extra, "runs": runs,
                  "governor_route_m_risk": (sorted(pid for pid, v in every.items() if v["PP32_W"] > 64.0) if arm == "B" else [])})
        out["arms"][arm] = c
        L.append(f"arm {arm}: {c['card'].split(' (')[0]}; {len(pts)} points; {pl['n_runs_scored_and_ties']} runs + {pl['n_smoke']} smoke; "
                 f"{pl['card_minutes_planned']:.1f} card-minutes planned at {pl['pace_s_per_run']} s a run (target {pl['target_min']}, rule "
                 f"{pl['rule_min']}, cap {pl['cap_min']}); stops {c['stop_W']} W x3 / {c['die_stop_C']} C; drop line {c['drop_line_W']} W; highest "
                 f"PP32 {hi[1]['PP32_W']:.2f} W ({hi[0]}), PP_all {hia[1]['PP_all_W']:.2f} W ({hia[0]}, {hia[1]['PP_all_by']}); longest GEMM "
                 f"{longest[1]['seconds_per_gemm_at_600MHz_v32']:.4f} s ({longest[0]}, MM1-v3.2 at 600 MHz)")
        if arm == "B":
            L.append(f"  route m risk (PP32 over 64.0 W): {c['governor_route_m_risk']}")
        for i, x in extra.items():
            L.append(f"  {i}: {x['token']} {x['format']} {x['kind']} PP32 {x['PP32_W']:.2f} W - {x['note']}")
        L.append("  order: " + " ".join(f"{r['id']}" for r in pl["runs"]))
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    return js, "\n".join(L) + "\n"


def main():
    js, tx = make()
    paths = [os.path.join(HERE, "plan-e224.json"), os.path.join(HERE, "plan-e224.txt")]
    if "--check" in sys.argv:
        same = all(open(p).read() == t for p, t in zip(paths, (js, tx)))
        print("plan_e224 --check:", "SAME" if same else "DIFFER")
        sys.exit(0 if same else 1)
    for p, t in zip(paths, (js, tx)):
        open(p, "w").write(t)
    print(tx)
    for p in paths:
        print(os.path.basename(p), sha(p))


if __name__ == "__main__":
    main()
