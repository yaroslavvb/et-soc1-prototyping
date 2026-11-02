#!/usr/bin/env bash
# E139 pipeline test, before any E139 pass: reduce_e139.sh run with E132's committed passes standing in for E139's (glob p1321?,
# warm-up 13210), into a scratch dir. It must reproduce E132's committed e132.json verdicts and headline contrasts exactly (the same
# reducer on the same passes); the pooled call then reads E132's six headline passes twice, which tests only that it runs. Nothing
# here is a measurement.   PY=<python3 with numpy> bash tools/claims-v3/e139/selftest_e139.sh <scratch dir>
set -eu
S=${1:?scratch}; D132=docs/reports/data/2026-11-02-e132-memory-split; PY=${PY:-python3}
mkdir -p "$S/data"; ln -sfn "$PWD/$D132/passes" "$S/data/passes"
E139_GLOB='p1321?' E139_WARMUP=13210 WORK=$S/w WORK132=$S/w132 PY=$PY bash tools/claims-v3/e139/reduce_e139.sh "$S/data" "$D132" > "$S/reduce.log" 2>&1
$PY - "$S/data/e139.json" "$D132/e132.json" "$S/data/e139-pooled.json" <<'PYEOF'
import json, sys
a, b, c = (json.load(open(f)) for f in sys.argv[1:4])
bad = 0
for r in sorted(b["verdicts"]):
    va, vb = a["verdicts"][r].get("verdict"), b["verdicts"][r].get("verdict"); ok = va == vb; bad += not ok
    print("%-22s stand-in %-12s E132 %-12s %s" % (r, va, vb, "ok" if ok else "DIFFERS"))
for m in b["headline"]["contrasts"]:
    for k, v in b["headline"]["contrasts"][m].items():
        w = a["headline"]["contrasts"][m][k]
        if json.dumps(v, sort_keys=True) != json.dumps(w, sort_keys=True): bad += 1; print("DIFFERS", m, k)
print("headline passes:", a["passes_headline"], "| pooled call headline passes:", c["passes_headline"])
print("SELFTEST", "PASS" if bad == 0 else "FAIL (%d differences)" % bad)
PYEOF
