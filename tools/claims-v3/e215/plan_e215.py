#!/usr/bin/env python3
"""E215 (Q224): the cards, their stops and predicted peaks, the card time per arm and its caps, and the refusal rule. Written before any E215
datum. Standard library only.

    python3 -I -B tools/claims-v3/e215/plan_e215.py            writes plan-e215.json and plan-e215.txt
    python3 -I -B tools/claims-v3/e215/plan_e215.py --check    rebuilds both and compares with the committed files (exit 0 = PASS)

THE PEAK of a point (planning, E213's form): MM1-v3.1's frozen W over idle at the point plus its rest law's rest power for that card (REPORTED by
MM1-v3.1) plus 2 W, E209's margin; the day's planning peak is the largest; the script REFUSES (exit 3) if any point's planning peak passes its
arm's line. BESIDE IT, for every gemmLnc point (E213's lesson), a BOUND: MM1-v3.1's W over idle x 1.85 - the largest measured / MM1-v3.1 ratio of
W over idle at the committed gemmLnc points (E211 and E213: 1.13-1.82, MM1-v3.1's points_energy_v31.csv, in sample) rounded up - plus the rest
plus 2 W, set against the arm's live board stop (REPORTED; such a point runs last in its arm, so a stop there ends only the gemmLnc block).
THE CARD TIME: the arm's runs at the pace E213 measured on that card in this run form (aifoundry3: E213 arm A, 105 runs in 42.83 card-minutes;
card 1: E213 arm B, 79 runs in 29.74 card-minutes; each including its smoke, gates and rests), the smoke and stop-path minutes added as E213
counted them (0.89 for four processes on aifoundry3; 1.0 for four on card 1, scaled by the count).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
MARGIN_W = 2.0
GEMMLNC_FACTOR = 1.85
LAND_JSON = "tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.json"
ARMS = {
    "A": {"card": "aifoundry3 card 0", "box": "aifoundry3", "devices": "the box's one card, its device nodes at index 0",
          "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "clock": "600 MHz pinned (a boot-time TDP of 0 latches the governor), read, never set",
          "config_gate": "TDP 0 W, temperature threshold 65 C, minion 600 MHz, as found (read, nothing set; E207, E211 and E213 arm A read the same)",
          "line_W": 65.0, "stop_W": 70.0,
          "stops": ("the board strictly above 70 W on 3 samples in a row (counting the samples that carry a board reading; a sample with none "
                    "neither counts nor breaks the row); the shires' mean die (minshire[0]) at or above 70 C; the hottest-sensor latch "
                    "(minshire[2]) at or above 70 C once it has risen during the session above the lowest value it read since the session's first "
                    "sample (E213 arm A's lines, E206.md A1 item 1)"),
          "die_gate": "min(60, the session's rest die + 4) C, waited at most 300 s, else that run is NO DATA (E207's and E213 arm A's)",
          "pace": {"source": "E213 arm A (docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3): 105 runs in 42.83 card-minutes, smoke included",
                   "s_per_run": 42.83 * 60 / 105},
          "smoke_min_per_process": 0.89 / 4, "rule_min": 60.0, "cap_min": 70.0,
          "measured_peaks": ("E213 arm A 64.22 W (a075, gemmLnc3x1x3 fp32), 58 C, latch 51 -> 61 C (session 06:37:09-07:19:59 PST Wed 18 Nov 2026); "
                             "E211 61.9 W, 59 C; E210 58.66 W, 59 C; E207 51.26 W, 56 C - all under this arm's 70 W / 70 C stops"),
          "rest": ("the first card command at least 40 minutes after our previous session on aifoundry3 ended (E213 arm A's ended 07:19:59 PST "
                   "Wed 18 Nov 2026; the simulator runs on aifoundry3 since are not card sessions)")},
    "B": {"card": "aifoundry1 card 1", "box": "aifoundry1", "devices": "the card's device nodes at index 1; ET_DEVICES=1 on every device process",
          "lock": "/run/lock/etsoc-shire1.lock", "et_devices": "1",
          "clock": "600 MHz as found (every sample since September; E213 arm B 17,817 of 17,817 samples), read, never set",
          "config_gate": "TDP 65 W, temperature threshold 65 C, minion 600 MHz, as found (read, nothing set; E206 arm B and E213 arm B read the same)",
          "line_W": 65.0, "stop_W": 72.0,
          "stops": ("the board strictly above 72 W on 3 samples in a row; the die at or above 80 C (the shires' mean, or the hottest-sensor latch once "
                    "it has risen during the session) - E206 and E213 arm B's lines on this card"),
          "die_gate": "min(63, the session's rest die + 3) C, waited at most 300 s, else that run is NO DATA (E206 and E213 arm B's)",
          "pace": {"source": "E213 arm B (docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1): 79 runs in 29.74 card-minutes, smoke included",
                   "s_per_run": 29.74 * 60 / 79},
          "smoke_min_per_process": 1.0 / 4, "rule_min": 42.0, "cap_min": 48.0,
          "measured_peaks": ("E213 arm B tripped its 72 W x3 stop at run 079 (k37, gemmLnc3x1x3 fp32: 72.24 W on 3 samples; its W over idle 1.69 x "
                             "MM1-v3.1's in sample); its smoke s14 (gemmLnc2x2x2) 66.1 W; its other runs under 66 W; latch 53 -> 59 C (session "
                             "15:15:28-15:45:12 PST Wed 18 Nov 2026); E206 arm B 59.34 W"),
          "rest": ("the first card command at least 40 minutes after the last session on aifoundry1 ended, either card, ours or the model session's "
                   "(E214 a1c1-S4 ended 21:01:51 PST Wed 18 Nov 2026, the model session's release #12.8.1; any later release counts)")},
}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def fnum(x):
    return None if x in ("", None, "NOT FORECAST") else float(x)


def build():
    P = json.load(open(os.path.join(HERE, "points-e215.json")))["arms"]
    land = {q["token"]: q for q in json.load(open(os.path.join(REPO, LAND_JSON)))["points"]}
    b31 = {r["id"]: r for r in csv.DictReader(open(os.path.join(HERE, "forecast-e215b-v31.csv"), newline=""))}
    refs = {(r["card"], r["id"]): r for r in csv.DictReader(open(os.path.join(HERE, "forecast-e215-refs.csv"), newline="")) if r["model"] == "MM1-v3.1"}
    out = {"experiment": "E215", "request": "Q224", "what": "the cards, stops, peaks and card time of E215 (frozen before any datum)", "arms": {},
           "gemmLnc_factor_REPORTED": GEMMLNC_FACTOR,
           "inputs_sha256": {rel: sha_rel(rel) for rel in ("tools/claims-v3/e215/points-e215.json", LAND_JSON, "tools/claims-v3/e215/forecast-e215b-v31.csv",
                                                           "tools/claims-v3/e215/forecast-e215-refs.csv")}}
    refuse = []
    for tag, a in ARMS.items():
        peaks, bounds = [], []
        for p in P[tag]["points"] + P[tag]["references"] + [P[tag]["tie"]]:
            if p["role"] == "point" and tag == "A":
                r = land[p["source_token"]]["v31"]
                W, rest = r.get("W_over_idle"), (r.get("rest_law") or {}).get("P_rest_W")
            elif p["role"] == "point":
                r = b31[p["id"]]
                W, rest = fnum(r.get("W_over_idle")), fnum(r.get("P_rest_W_REPORTED"))
            else:
                r = refs[(p["card"], p["id"])]
                W, rest = fnum(r.get("W_over_idle")), fnum(r.get("P_rest_W_REPORTED"))
            if W is None or rest is None:
                continue
            pk = W + rest + MARGIN_W
            peaks.append((pk, p["id"], W, rest))
            if pk > a["line_W"]:
                refuse.append(f"{tag} {p['id']} planning peak {pk:.2f} W over the line {a['line_W']} W")
            if p["loop"] == "rgm136 gemmLnc":
                bd = GEMMLNC_FACTOR * W + rest + MARGIN_W
                bounds.append({"point": p["id"], "W_over_idle_v31": round(W, 3), "bound_W": round(bd, 2), "stop_W": a["stop_W"],
                               "under_stop": bd <= a["stop_W"]})
        peaks.sort(reverse=True)
        od = P[tag]["order"]
        runs = od["runs"]
        n_smoke = len(P[tag]["smoke"])
        smoke_min = n_smoke * a["smoke_min_per_process"]
        planned = runs * a["pace"]["s_per_run"] / 60.0 + smoke_min
        first_pass_runs = 2 + len(od["pass1"])
        subset = first_pass_runs * a["pace"]["s_per_run"] / 60.0 + len(od["opening_smoke"]) * a["smoke_min_per_process"]
        out["arms"][tag] = dict(a, runs=runs, smoke_processes=n_smoke, smoke_min=round(smoke_min, 2), card_minutes_planned=round(planned, 1),
                                registered_subset_if_cut={"what": "the opening smoke, tie 1, pass 1 and tie 2: every point once but the gemmLnc block",
                                                          "runs": first_pass_runs, "card_minutes": round(subset, 1)},
                                planning_peak={"W": round(peaks[0][0], 2), "point": peaks[0][1], "W_over_idle": round(peaks[0][2], 2),
                                               "rest_W_REPORTED": round(peaks[0][3], 2), "margin_W": MARGIN_W},
                                top5_planning_peaks=[{"point": i, "W": round(pk, 2)} for pk, i, _, _ in peaks[:5]],
                                gemmLnc_bounds_REPORTED=bounds, points_over_line=[x for x in refuse if x.startswith(tag)],
                                within_cap=planned <= a["rule_min"])
        if planned > a["rule_min"]:
            refuse.append(f"{tag} planned {planned:.1f} card-minutes over the rule {a['rule_min']}")
    out["refusals"] = refuse
    return out


def text(out):
    L = []
    for tag, a in out["arms"].items():
        L += [f"ARM {tag}: {a['card']} ({a['devices']}; lock {a['lock']}{'; ET_DEVICES=' + a['et_devices'] if a['et_devices'] else ''})",
              f"  clock: {a['clock']}", f"  start config gate (read): {a['config_gate']}",
              f"  the line: {a['line_W']:.0f} W (no point runs whose planning peak passes it)", f"  live stops: {a['stops']}",
              f"  die gate: {a['die_gate']}",
              f"  planning peak: {a['planning_peak']['W']} W at {a['planning_peak']['point']} (MM1-v3.1's W over idle {a['planning_peak']['W_over_idle']} + its "
              f"rest law {a['planning_peak']['rest_W_REPORTED']} + {a['planning_peak']['margin_W']}); top five {a['top5_planning_peaks']}",
              f"  gemmLnc bounds (REPORTED; W over idle x {out['gemmLnc_factor_REPORTED']} + rest + 2 W against the {a['stop_W']:.0f} W stop): {a['gemmLnc_bounds_REPORTED']}",
              f"  measured peaks on this card: {a['measured_peaks']}",
              f"  card time planned: {a['card_minutes_planned']} card-minutes ({a['runs']} runs at {a['pace']['s_per_run']:.2f} s a run, {a['pace']['source']}; "
              f"{a['smoke_processes']} smoke processes and the stop-path test {a['smoke_min']} min); no run starts after {a['rule_min']:.0f} card-minutes; "
              f"the session ends at {a['cap_min']:.0f} after the run in progress", f"  registered subset if cut: {a['registered_subset_if_cut']}",
              f"  rest: {a['rest']}", ""]
    L.append(f"refusals: {out['refusals'] or 'none'}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = build()
    jp, tp = os.path.join(HERE, "plan-e215.json"), os.path.join(HERE, "plan-e215.txt")
    if a.check:
        same = json.load(open(jp)) == json.loads(json.dumps(out)) and open(tp).read() == text(out)
        print(f"plan_e215 --check: plan-e215.json and plan-e215.txt rebuilt == committed: {same}; refusals {out['refusals']}")
        print("PASS" if same and not out["refusals"] else "FAIL")
        sys.exit(0 if same and not out["refusals"] else 1)
    if out["refusals"]:
        print("plan_e215: REFUSED (exit 3):", out["refusals"])
        sys.exit(3)
    json.dump(out, open(jp, "w"), indent=1)
    open(tp, "w").write(text(out))
    print(text(out))


if __name__ == "__main__":
    main()
