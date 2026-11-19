#!/usr/bin/env python3
"""E216 (Q227): the session's order, card time, planning peaks and stops, before any datum (E216.md section 6). Standard library; reads
points-e216.json and forecast-e216.json; writes plan-e216.json and plan-e216.txt.

THE ORDER (registered here; E209's form on this card, with the G block last): E208's three smoke arms (the kit's, as E209 ran them); A1 (E208's
anchor 4x8x8-int8-rnd, a burst) and N1 (a null run); PASS 1 = every point of families F, Y and Gt once, in the order of Python's
random.Random("E216|pass1") shuffle of their sorted ids, with an anchor after the 12th, 24th and 36th; PASS 2 = the 16 Y points again, in the
reverse of their pass-1 order; A5 and N2; then THE G BLOCK, the 10 gemmLnc points once each, ordered by their planning peak with the term
ascending (ties by id) - the last runs of the session. Every run is one E208-form burst (a 6 s burst under a plain timeout 10, its win view).
THE CARD TIME: E209's planning pace on this card (a burst 23 s, gates included; a null about 50 s) plus about 2.5 minutes for the opening rest,
the smoke and the stop-path test; no run starts after 45 card-minutes from the first card command; the session ends at 55 card-minutes, after
the run in progress (E209's rule and cap). THE REGISTERED SUBSET IF CUT: the smoke, A1, N1 and pass 1 with its anchors.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EST_S = {"burst": 23.0, "null": 50.0}
OVERHEAD_S = 150.0
RULE_MIN, CAP_MIN = 45.0, 55.0
LINE_W = 64.0
STOPS = {"board_W_strictly_above_on_3_samples_in_a_row": 70.0, "die_mean_minshire0_at_or_above_C": 70.0,
         "latch_minshire2_at_or_above_C_once_risen_in_session": 70.0}
ANCHOR = {"arm": "4x8x8-int8-rnd", "token": "gemmL4x8x8", "type": "int8", "shires": "0xffffffff", "est_peak_w": 50.0,
          "values": "gemmL4x8x8:randn:src/tiles/int8/full.bin", "source": "E208's anchor on this card (E209's A1-A5)"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    P = json.load(open(os.path.join(HERE, "points-e216.json")))["points"]
    FC = json.load(open(os.path.join(HERE, "forecast-e216.json")))["points"]
    byid = {p["id"]: p for p in P}
    pk = {p["id"]: FC[p["id"]]["799.0"]["planning_peak_W"] for p in P}
    pkby = {p["id"]: FC[p["id"]]["799.0"]["planning_peak_by"] for p in P}
    pass1 = sorted(p["id"] for p in P if p["family"] in ("F", "Y", "Gt"))
    random.Random("E216|pass1").shuffle(pass1)
    pass2 = [i for i in reversed(pass1) if byid[i]["family"] == "Y"]
    gblock = sorted((p["id"] for p in P if p["family"] == "G"), key=lambda i: (pk[i], i))
    order = [("SMOKE", "smoke", "start"), ("A1", "anchor", "start"), ("N1", "null", "start")]
    for k, i in enumerate(pass1):
        order.append((i, "arm", "pass1"))
        if k + 1 in (12, 24, 36):
            order.append((f"A{(k + 1) // 12 + 1}", "anchor", "pass1"))
    order += [(i, "arm", "pass2") for i in pass2] + [("A5", "anchor", "end"), ("N2", "null", "end")]
    order += [(i, "arm", "G block") for i in gblock]
    runs, t = [], OVERHEAD_S
    cut = None
    for n, (rid, role, block) in enumerate(order, 1):
        if role == "smoke":
            continue
        est = EST_S["null"] if role == "null" else EST_S["burst"]
        peak = ANCHOR["est_peak_w"] if role == "anchor" else (22.5 if role == "null" else pk[rid])
        runs.append({"n": n, "id": rid, "role": role, "block": block, "form": "null" if role == "null" else "burst", "est_s": est,
                     "planning_peak_W": round(peak, 3), "planning_peak_by": (pkby.get(rid) if role == "arm" else None),
                     "starts_by_card_min": round(t / 60.0, 2)})
        t += est
        if block == "pass1" or block == "start":
            cut = round(t / 60.0, 2)
    planned_min = round(t / 60.0, 2)
    over = [r["id"] for r in runs if r["role"] == "arm" and r["planning_peak_W"] > LINE_W]
    out = {"experiment": "E216", "what": "the session plan (registered order, card time, peaks, stops), before any datum",
           "card": "aifoundry2 card 0 under its own governor (read, never set)", "clock_forecast_mhz": 799.0,
           "order": runs, "pass1": pass1, "pass2": pass2, "g_block": gblock, "anchor": ANCHOR,
           "n_runs": len(runs), "n_point_runs": sum(1 for r in runs if r["role"] == "arm"), "n_anchors": sum(1 for r in runs if r["role"] == "anchor"),
           "n_nulls": sum(1 for r in runs if r["role"] == "null"), "planned_card_minutes": planned_min,
           "registered_subset_if_cut": {"what": "the smoke, A1, N1 and pass 1 with its anchors (F, Y and Gt once)", "card_minutes": cut},
           "rule_min": RULE_MIN, "cap_min": CAP_MIN, "line_W": LINE_W, "stops": STOPS, "points_over_line": over,
           "max_planning_peak_W": max(r["planning_peak_W"] for r in runs if r["role"] == "arm"),
           "max_planning_peak_G_W": max(pk[i] for i in gblock) if gblock else None,
           "inputs_sha256": {"points-e216.json": sha(os.path.join(HERE, "points-e216.json")), "forecast-e216.json": sha(os.path.join(HERE, "forecast-e216.json"))},
           "interpreter": "/usr/bin/python3 " + sys.version.split()[0]}
    json.dump(out, open(os.path.join(HERE, "plan-e216.json"), "w"), indent=1)
    L = [f"E216 plan: aifoundry2 card 0 under its governor; forecast clock 799.0 MHz; stops board > 70 W x 3, die or latch (once risen) >= 70 C; line {LINE_W} W",
         f"card time: {out['n_runs']} runs ({out['n_point_runs']} point runs, {out['n_anchors']} anchors, {out['n_nulls']} nulls) + smoke, planned "
         f"{planned_min} card-minutes; no run starts after {RULE_MIN} card-minutes; the session ends at {CAP_MIN}; cut subset {cut} card-minutes",
         f"max planning peak {out['max_planning_peak_W']:.2f} W (G block {out['max_planning_peak_G_W']:.2f} W); points over the line: {over or 'none'}",
         "n   id      role    block    planning peak W (by)   starts by card-min"]
    for r in runs:
        L.append(f"{r['n']:3d} {r['id']:7s} {r['role']:7s} {r['block']:8s} {r['planning_peak_W']:7.2f} ({r['planning_peak_by'] or '-'})  {r['starts_by_card_min']:6.2f}")
    open(os.path.join(HERE, "plan-e216.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:4]))


if __name__ == "__main__":
    main()
