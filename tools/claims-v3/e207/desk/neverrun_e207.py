#!/usr/bin/env python3
"""E207 (Q199) desk: which of E207's 53 points never ran - E206's own scanner's output (tools/claims-v3/e206/desk/neverrun_e206.py, run unchanged
over every data directory of ours) and the model session's planned sweep (E208, 1116-mmsweep, its arms.json: planned or run counts as run),
matched point by point and case by case. No card. Standard library only.

    python3 -I -B tools/claims-v3/e207/desk/neverrun_e207.py found.json [found.json ...] --e208-arms arms.json [--when TEXT]
        writes desk/neverrun-e207.json and prints desk/neverrun-e207.txt (redirect stdout)

A POINT NEVER RAN if no card record or host command matches its arm, format, data kind (as E206's scanner reads it from --values: randn ->
random, e37 -> e37, tiles of files other than zeros or the real2 set -> tiles:other), minions and shire mask, and E208 plans no arm with its shape,
format, kind and mask. A CASE (shape, format, mask) NEVER RAN if no record of any data kind matches it and E208 plans none. THE SHIRE MASK IS
COMPARED AS A NUMBER: the host prints "0x%llx" (0x0f0f0f0f as 0xf0f0f0f), a command line may carry either spelling, and MM1-v1's own never-run
record keyed b37 by the string 0x0f0f0f0f. A simulator record (E206's scanner's rule) is listed apart and never counts as a card run.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PTS = json.load(open(os.path.join(HERE, "..", "points-e207.json")))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pub(path):
    """a path as a public file may show it (E206's form): a lane's clone of the lab as LAB, the round's lane folders as OUT, the home folder as HOME"""
    path = re.sub(r"^.*/work/clone(?=/|$)", "LAB", path)
    path = re.sub(r"^.*?/out(?=/|$)", "OUT", path)
    path = path.replace(os.path.expanduser("~"), "HOME")
    return path.replace("~", "HOME")


def kind_scan(kind):
    return {"random": "random", "e37": "e37"}.get(kind, "tiles:other")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("found", nargs="+")
    ap.add_argument("--e208-arms", required=True)
    ap.add_argument("--when", default="")
    a = ap.parse_args()
    card, sim, scans = {}, {}, []
    for fp in a.found:
        d = json.load(open(fp))
        ss = d["scans"] if "scans" in d else {d.get("label", "one"): d}
        for lab, s in ss.items():
            scans.append({"label": s["label"], "box": s["box"], "default_card": s["default_card"], "roots": [pub(x) for x in s["roots"]],
                          "files_read": s["files_read"], "configurations": len(s["found"]),
                          "files_over_400MB_skipped": [pub(x) for x in s["files_over_400MB_skipped"]], "n_unreadable": s["n_unreadable"],
                          "found_file_sha256": sha(fp)})
            for key, rec in s["found"].items():
                arm, t, kd, mi, mk = key.split("|")
                k = (arm, t, kd, int(mi), int(mk, 16))
                for c, n in rec["cards"].items():
                    card.setdefault(k, {}).setdefault(c, 0)
                    card[k][c] += n
                if rec["sim"]:
                    sim[k] = sim.get(k, 0) + rec["sim"]
    planned = set()
    arms = json.load(open(a.e208_arms))["arms"]
    for x in arms:
        kd = {"rnd": "random"}.get(x["kind"], x["kind"])
        planned.add((f"gemmL{x['mb']}x{x['nb']}x{x['kb']}", x["type"], kd, int(x["shires"], 16)))
    rows = []
    for p in PTS["points"]:
        m = int(p["shire_mask"], 16)
        k = (p["arm"], p["format"], kind_scan(p["kind"]), p["minions"], m)
        cards = card.get(k, {})
        case_cards = {}
        for kk, v in card.items():
            if kk[0] == p["arm"] and kk[1] == p["format"] and kk[4] == m:
                for c, n in v.items():
                    case_cards[c] = case_cards.get(c, 0) + n
        e208_point = (p["arm"], p["format"], p["kind"], m) in planned
        e208_case = any(x[0] == p["arm"] and x[1] == p["format"] and x[3] == m for x in planned)
        rows.append({"id": p["id"], "case": p["case"], "key": f"{p['arm']}|{p['format']}|{kind_scan(p['kind'])}|{p['minions']}|0x{m:x}",
                     "card_records": sum(cards.values()), "cards": sorted(cards), "case_card_records_any_kind": sum(case_cards.values()),
                     "simulator_records": sim.get(k, 0), "e208_planned_point": e208_point, "e208_planned_case": e208_case,
                     "never_run_point": not cards and not e208_point, "never_run_case_any_kind": not case_cards and not e208_case,
                     "never_on_aifoundry3": "aifoundry3 card 0" not in cards})
    cnt = {"points": len(rows), "never_run_points": sum(r["never_run_point"] for r in rows),
           "cases": len({r["case"] for r in rows}), "never_run_cases": len({r["case"] for r in rows if r["never_run_case_any_kind"]}),
           "points_with_simulator_records": sum(1 for r in rows if r["simulator_records"])}
    out = {"what": "E207's points against every GEMM record of the lab's host in our data directories (E206's scanner) and E208's planned arms",
           "when": a.when, "scans": scans, "e208_arms": {"path": pub(a.e208_arms), "sha256": sha(a.e208_arms), "arms": len(arms)},
           "paths": "LAB = a clone of the lab at GitHub main; OUT = the round's lane folders on aifoundry2; HOME = the lab account's home folder on the box named",
           "not_searched": "aifoundry1's own folders (the model session's box, never touched by this round's lanes; its three released E208 sessions are in "
                           "the lab's committed data, searched)",
           "counts": cnt, "all_never_run": cnt["never_run_points"] == cnt["points"] and cnt["never_run_cases"] == cnt["cases"], "rows": rows}
    json.dump(out, open(os.path.join(HERE, "neverrun-e207.json"), "w"), indent=1)
    print(f"E207 never-run search ({a.when})")
    for s in scans:
        print(f"  {s['label']} on {s['box']}: {s['files_read']} files, {s['configurations']} GEMM configurations found, over 400 MB {len(s['files_over_400MB_skipped'])}, "
              f"unreadable {s['n_unreadable']}; roots {', '.join(s['roots'][:4])}{' ...' if len(s['roots']) > 4 else ''}")
    print(f"  E208's planned arms: {len(arms)} ({pub(a.e208_arms)}, sha256 {out['e208_arms']['sha256']})")
    print(f"  NOT SEARCHED: {out['not_searched']}")
    print(f"  points never run: {cnt['never_run_points']} of {cnt['points']}; cases never run (any data kind): {cnt['never_run_cases']} of {cnt['cases']}; "
          f"points with simulator records: {cnt['points_with_simulator_records']}")
    for r in rows:
        print(f"  {r['id']} {r['case']:33s} records {r['card_records']} (case, any kind: {r['case_card_records_any_kind']}); simulator {r['simulator_records']}; "
              f"E208 planned {r['e208_planned_point']}/{r['e208_planned_case']}; never run: point {r['never_run_point']}, case {r['never_run_case_any_kind']}")


if __name__ == "__main__":
    main()
