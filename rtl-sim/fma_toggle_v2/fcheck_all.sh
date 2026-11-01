#!/bin/bash
# The functional check that must pass before any count is quoted: writes fcheck-unit-fp32.json, fcheck-unit-fp16.json, fcheck-vpu.json
# into ${1:-.}. Exit 1 if fp32 or int8 has any mismatch, or fp16 any mismatch beyond its named residue, or a gate count differs.
set -u
OUT=${1:-.}
PY=${PY:-python3}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE" || exit 2
PYTHONPATH=. $PY fcheck_unit.py --bin obj_unit/Vtb --fmt fp32 --n 40000 --seed 1 --out "$OUT/fcheck-unit-fp32.json" > /dev/null || exit 2
PYTHONPATH=. $PY fcheck_unit.py --bin obj_unit/Vtb --fmt fp16 --n 40000 --seed 1 --out "$OUT/fcheck-unit-fp16.json" > /dev/null || exit 2
PYTHONPATH=. $PY fcheck_vpu.py --bin obj_vpu/Vtb --out "$OUT/fcheck-vpu.json" --ops 4 --seeds 3 --jobs "${JOBS:-8}" > /dev/null || exit 2
$PY - "$OUT" <<'PY'
import json, sys
o = sys.argv[1]
bad = 0
for f in ("fp32", "fp16"):
    r = json.load(open(f"{o}/fcheck-unit-{f}.json"))
    t = r["tally"]
    rest = {k: v for k, v in t.items() if k not in ("exact", "window_cancel")}
    print(f"unit {f}: {t.get('exact', 0)} of {r['n']} exact, named residue {t.get('window_cancel', 0)}, other {rest or 0}"
          + (f"; against exact rtz arithmetic {r['fp16_against_exact_rtz']}" if f == "fp16" else ""))
    bad += sum(rest.values())
r = json.load(open(f"{o}/fcheck-vpu.json"))
s = r["summary"]
for f in ("fp32", "fp16", "int8"):
    t = s["totals"][f]
    print(f"vpu  {f}: {t.get('exact', 0)} accumulator words exact over whole TensorFMA ops, {t.get('mismatch', 0)} mismatched")
    bad += t.get("mismatch", 0)
print(f"vpu  zero gate: {s['cases']} cases, valid column slots differ from the gate rule in {s['cases_where_valid_slots_differ']}")
bad += s["cases_where_valid_slots_differ"]
print("PASS" if not bad else f"FAIL: {bad}")
sys.exit(1 if bad else 0)
PY
