#!/bin/bash
cd ~/claude/et-soc1-prototyping/build/e126/runs || exit 9
python3 - <<'PY'
import json, glob
rc = {}
n = 0
for p in glob.glob("*/runs.jsonl") + glob.glob("*/queries.jsonl"):
    for ln in open(p):
        d = json.loads(ln)
        q = d.get("queries", d)
        if "residency_rc" in q:
            n += 1
            rc[str(q["residency_rc"])] = rc.get(str(q["residency_rc"]), 0) + 1
            if q.get("residency"):
                print("RESIDENCY RECORDS PRESENT in", p, q.get("tag"), q["residency"][:2])
print("residency queries:", n, "return codes:", rc)
PY
