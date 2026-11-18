#!/usr/bin/env python3
"""E213 (Q216): the cards, their stops and predicted peaks, the card time per arm and its caps, and the refusal rule. Written before any E213
datum. Standard library only.

    python3 -I -B tools/claims-v3/e213/plan_e213.py            writes plan-e213.json and plan-e213.txt
    python3 -I -B tools/claims-v3/e213/plan_e213.py --check    rebuilds both and compares with the committed files (exit 0 = PASS)

THE PEAK of a point (planning): MM1-v3's frozen W over idle at the point plus its rest law's rest power for that card (REPORTED by MM1-v3) plus
2 W, the margin E209 used; the day's planning peak is the largest. The script REFUSES (exit 3) if any point's planning peak passes its arm's line.
Beside it, the cards' measured peaks in the lab's committed records (named). THE CARD TIME: the arm's runs at the pace measured on that card with
this run form (aifoundry3: E207, 109 runs in 47.16 card-minutes; card 1: E206 arm B, 229 runs in 84.81 card-minutes; each including its smoke,
gates and rests), the smoke and the stop-path test added as E207 counted them (arm A by Amendment A1: four smoke processes, s04 the family
'rgm211 gemmL''s own, so E207's 0.67 minutes for three x 4/3 = 0.89).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
MARGIN_W = 2.0
ARMS = {
    "A": {"card": "aifoundry3 card 0", "box": "aifoundry3", "devices": "the box's one card, its device nodes at index 0",
          "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "clock": "600 MHz pinned (a boot-time TDP of 0 latches the governor), read, never set",
          "config_gate": "TDP 0 W, temperature threshold 65 C, minion 600 MHz, as found (read, nothing set; E207 and E211 read the same)",
          "line_W": 65.0,
          "stops": ("the board strictly above 70 W on 3 samples in a row (counting the samples that carry a board reading; a sample with none "
                    "neither counts nor breaks the row); the shires' mean die (minshire[0]) at or above 70 C; the hottest-sensor latch "
                    "(minshire[2]) at or above 70 C once it has risen during the session above the lowest value it read since the session's first "
                    "sample (E206.md A1 item 1; E207's and E211's kits)"),
          "die_gate": "min(60, the session's rest die + 4) C, waited at most 300 s, else that run is NO DATA (E207's)",
          "pace": {"source": "E207 (docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3): 109 runs in 47.16 card-minutes, smoke included",
                   "s_per_run": 47.16 * 60 / 109},
          "smoke_min": 0.89, "rule_min": 60.0, "cap_min": 70.0,     # Amendment A1: four smoke processes (s04 added), E207's 0.67 for three x 4/3
          "measured_peaks": ("E207 51.26 W, 56 C (session 07:06:44-07:53:54 PST Tue 17 Nov 2026); E210 58.66 W, 59 C; E211 61.9 W, 59 C (rgm211 "
                             "and gemmLnc among its runs); E206 arm A 59.54 W, 61 C - all under this arm's 70 W / 70 C stops"),
          "rest": "the first card command at least 40 minutes after our previous session on aifoundry3 ended (E211's ended 13:39:35 PST Tue 17 Nov 2026)"},
    "B": {"card": "aifoundry1 card 1", "box": "aifoundry1", "devices": "the card's device nodes at index 1; ET_DEVICES=1 on every device process",
          "lock": "/run/lock/etsoc-shire1.lock", "et_devices": "1",
          "clock": "600 MHz as found (every sample since September, E137; E206 arm B 50,820 of 50,820 samples), read, never set",
          "config_gate": "TDP 65 W, temperature threshold 65 C, minion 600 MHz, as found (read, nothing set; E206 arm B read the same)",
          "line_W": 65.0,
          "stops": ("the board strictly above 72 W on 3 samples in a row; the die at or above 80 C (the shires' mean, or the hottest-sensor latch once "
                    "it has risen during the session) - E206 arm B's lines on this card"),
          "die_gate": "min(63, the session's rest die + 3) C, waited at most 300 s, else that run is NO DATA (E206 arm B's)",
          "pace": {"source": "E206 arm B (docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1): 229 runs in 84.81 card-minutes, smoke included",
                   "s_per_run": 84.81 * 60 / 229},
          "smoke_min": 1.0, "rule_min": 42.0, "cap_min": 48.0,
          "measured_peaks": ("E206 arm B 59.34 W, the shires' mean 60 C, the latch 66 C (session 00:13:26-01:38:14 PST Tue 17 Nov 2026); E212 "
                             "a1c1 sessions at or under 66.6 W planned - under this arm's 72 W / 80 C stops"),
          "rest": ("the first card command at least 40 minutes after the last session on aifoundry1 ended, either card, ours or the model session's "
                   "(E212 a1c1-S3 ended 14:22:13 PST Tue 17 Nov 2026, by the orchestrator's release record; any later release counts)")},
}
SRC = {"A": ("tools/matmul/mm1/v3/out/mm1_v3_e213.csv", "01a2fdaef0b506b218fad1975dacf397a2c728010a595c8b4dadcbf569c07a49"),
       "B": ("tools/claims-v3/e213/forecast-e213b-v3.csv", None)}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def build():
    P = json.load(open(os.path.join(HERE, "points-e213.json")))["arms"]
    out = {"experiment": "E213", "request": "Q216", "what": "the cards, stops, peaks and card time of E213 (frozen before any datum)", "arms": {},
           "inputs_sha256": {"tools/claims-v3/e213/points-e213.json": sha_rel("tools/claims-v3/e213/points-e213.json")}}
    refuse = []
    for tag, a in ARMS.items():
        rel, want = SRC[tag]
        got = sha_rel(rel)
        if want and got != want:
            print(f"plan_e213: REFUSED, {rel} is not the frozen file")
            sys.exit(4)
        out["inputs_sha256"][rel] = got
        rows = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, rel), newline=""))}
        peaks = []
        for p in P[tag]["points"] + [P[tag]["tie"]]:
            r = rows.get(p["id"])
            if r is None or r.get("W_over_idle") in ("", None):
                continue
            pk = float(r["W_over_idle"]) + float(r["P_rest_W_REPORTED"]) + MARGIN_W
            peaks.append((pk, p["id"], float(r["W_over_idle"]), float(r["P_rest_W_REPORTED"])))
            if pk > a["line_W"]:
                refuse.append(f"{tag} {p['id']} planning peak {pk:.2f} W over the line {a['line_W']} W")
        peaks.sort(reverse=True)
        od = P[tag]["order"]
        runs = od["runs"]
        planned = runs * a["pace"]["s_per_run"] / 60.0 + a["smoke_min"]
        first_pass_runs = 2 + len(od["pass1"])
        subset = first_pass_runs * a["pace"]["s_per_run"] / 60.0 + a["smoke_min"]
        out["arms"][tag] = dict(a, runs=runs, card_minutes_planned=round(planned, 1),
                                registered_subset_if_cut={"what": "the smoke, tie 1, pass 1 and tie 2: every point once",
                                                          "runs": first_pass_runs, "card_minutes": round(subset, 1)},
                                planning_peak={"W": round(peaks[0][0], 2), "point": peaks[0][1], "W_over_idle": round(peaks[0][2], 2),
                                               "rest_W_REPORTED": round(peaks[0][3], 2), "margin_W": MARGIN_W},
                                top5_planning_peaks=[{"point": i, "W": round(pk, 2)} for pk, i, _, _ in peaks[:5]],
                                points_over_line=[x for x in refuse if x.startswith(tag)])
    out["refusals"] = refuse
    return out


def text(out):
    L = []
    for tag, a in out["arms"].items():
        L += [f"ARM {tag}: {a['card']} ({a['devices']}; lock {a['lock']}{'; ET_DEVICES=' + a['et_devices'] if a['et_devices'] else ''})",
              f"  clock: {a['clock']}", f"  start config gate (read): {a['config_gate']}",
              f"  the line: {a['line_W']:.0f} W (no point runs whose planning peak passes it)", f"  live stops: {a['stops']}",
              f"  die gate: {a['die_gate']}",
              f"  planning peak: {a['planning_peak']['W']} W at {a['planning_peak']['point']} (MM1-v3's W over idle {a['planning_peak']['W_over_idle']} + its rest "
              f"law {a['planning_peak']['rest_W_REPORTED']} + {a['planning_peak']['margin_W']}); top five {a['top5_planning_peaks']}",
              f"  measured peaks on this card: {a['measured_peaks']}",
              f"  card time planned: {a['card_minutes_planned']} card-minutes ({a['runs']} runs at {a['pace']['s_per_run']:.2f} s a run, {a['pace']['source']}; "
              f"smoke and stop-path test {a['smoke_min']} min); no run starts after {a['rule_min']:.0f} card-minutes; the session ends at {a['cap_min']:.0f} "
              f"after the run in progress", f"  registered subset if cut: {a['registered_subset_if_cut']}", f"  rest: {a['rest']}", ""]
    L.append(f"refusals: {out['refusals'] or 'none'}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = build()
    jp, tp = os.path.join(HERE, "plan-e213.json"), os.path.join(HERE, "plan-e213.txt")
    if a.check:
        same = json.load(open(jp)) == json.loads(json.dumps(out)) and open(tp).read() == text(out)
        print(f"plan_e213 --check: plan-e213.json and plan-e213.txt rebuilt == committed: {same}; refusals {out['refusals']}")
        print("PASS" if same and not out["refusals"] else "FAIL")
        sys.exit(0 if same and not out["refusals"] else 1)
    if out["refusals"]:
        print("plan_e213: REFUSED (exit 3):", out["refusals"])
        sys.exit(3)
    json.dump(out, open(jp, "w"), indent=1)
    open(tp, "w").write(text(out))
    print(text(out))


if __name__ == "__main__":
    main()
