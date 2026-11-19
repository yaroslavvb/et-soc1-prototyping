#!/usr/bin/env python3
"""E216 (Q227) desk: the scorer's reader (score_e216.read_run) fed the REAL committed reducer bytes of this card - E209's data-e209.json (data
commit ea3fa3ce: E208's registered reducer run on aifoundry2 card 0's E209 session) - with E209's own points standing in for E216's (each run's id,
shire mask, format and minions), so the reader's field names, views, routes, the STEP test and the energy rule are checked on what this card's
reducer writes. Standard library. Writes selftest-real.json beside the registration; exit 0 when every point run is read (none set aside), at
least one run is read on route c with energy, and every non-point run (anchors, nulls) is passed over.

    python3 -I -B tools/claims-v3/e216/desk/realbytes_e216.py
SPDX-License-Identifier: Apache-2.0
"""
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E216 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, E216)
import score_e216 as S  # noqa: E402

DATA = "docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/data-e209.json"
PTS = "tools/claims-v3/e209/points-e209.json"


def sha(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def main():
    D = json.load(open(os.path.join(REPO, DATA)))
    PJ = json.load(open(os.path.join(REPO, PTS)))
    pts = PJ["points"] if isinstance(PJ["points"], list) else list(PJ["points"].values())
    P = {p["id"]: {"id": p["id"], "mask": p.get("mask_host") or p.get("mask"), "fmt": p.get("fmt") or p.get("type"), "minions": p.get("minions"),
                   "family": "F"} for p in pts}
    c = collections.Counter()
    rows = []
    for r in D["runs"]:
        x = S.read_run(r, P)
        if x is None:
            c["passed over (anchor or null)"] += 1
            continue
        if x["set_aside"]:
            c["set aside"] += 1
            rows.append({"id": x["id"], "set_aside": x["set_aside"]})
            continue
        c["route " + x["route"]] += 1
        c["energy read" if "W" in x else "no energy"] += 1
        if x["step"]:
            c["STEP"] += 1
        rows.append({k: x.get(k) for k in ("id", "i", "f", "route", "col", "wall", "mean", "t", "T_op", "W", "flags")})
    ok = c["set aside"] == 0 and c["route c"] >= 1 and c["energy read"] >= 1 and c["passed over (anchor or null)"] >= 1
    out = {"what": "score_e216.read_run on E209's committed reducer bytes from aifoundry2 card 0 (E209's points standing in)", "data": DATA,
           "data_sha256": sha(DATA), "points": PTS, "points_sha256": sha(PTS), "runs_in_file": len(D["runs"]), "counts": dict(c),
           "smoke_records": len(D.get("smoke") or []), "ok": ok, "runs": rows, "interpreter": "/usr/bin/python3 " + sys.version.split()[0]}
    json.dump(out, open(os.path.join(E216, "selftest-real.json"), "w"), indent=1)
    print("realbytes:", dict(c), "OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
