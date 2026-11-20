#!/usr/bin/env python3
"""E220 (Q233) desk: each registered point's never-run verdict on its own arm's card, by its family's reading (desk/neverrun_e220.py's Never class,
imported unchanged: the point rule's hash covers that file), from the registration's literal scan. Standard library only. (neverrun_e220.py's own
'report' reads a 'mask' column; points-e220.csv names it 'shire_mask', so this file makes the report.)

    python3 -I -B tools/claims-v3/e220/desk/neverrun_report_e220.py [--scan desk/scan-e220-reg.json]   writes desk/neverrun-e220.json and .txt
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import neverrun_e220 as NR  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", default=os.path.join(HERE, "scan-e220-reg.json"))
    ap.add_argument("--points", default=os.path.join(HERE, "..", "points-e220.csv"))
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    S = json.load(open(a.scan))
    NV = NR.Never(S)
    rows = list(csv.DictReader(open(a.points)))
    res = []
    for r in rows:
        card = NR.ARM_CARD[r["arm"]]
        ok, ev = NV.verdict(r["neverrun_reading"], r["token"], r["shire_mask"], card)
        res.append({"arm": r["arm"], "id": r["id"], "family": r["family"], "token": r["token"], "mask": r["shire_mask"], "card": card,
                    "reading": r["neverrun_reading"], "never_run": bool(ok), "evidence": (None if ok else ev)})
    rec = {"what": "E220's never-run verdicts per registered point on its own arm's card (the literal scan, E218's form)",
           "scan_sha256": sha(a.scan), "points_csv_sha256": sha(a.points), "scan_window": [S["started"], S["ended"]], "lab_head": S["lab_head"],
           "files_read": S["files_read"], "n_points": len(res), "n_never_run": sum(1 for v in res if v["never_run"]),
           "ran": [v["arm"] + ":" + v["id"] for v in res if not v["never_run"]], "points": res}
    json.dump(rec, open(os.path.join(a.out, "neverrun-e220.json"), "w"), indent=1, sort_keys=True)
    lines = [f"E220 never-run report; scan {rec['scan_sha256'][:16]} ({S['files_read']} files, {S['started']} - {S['ended']}, lab {S['lab_head'][:12]})",
             f"points-e220.csv {rec['points_csv_sha256'][:16]}: {rec['n_never_run']} of {len(res)} never ran on their arm's card; ran: {rec['ran']}"]
    for v in res:
        lines.append(f"{v['arm']} {v['id']:6s} {v['family']:4s} {v['token']:18s} {v['mask']:10s} {v['reading']:6s} never_run={v['never_run']}")
    open(os.path.join(a.out, "neverrun-e220.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:2]))
    sys.exit(0 if rec["n_never_run"] == len(res) else 1)


if __name__ == "__main__":
    main()
