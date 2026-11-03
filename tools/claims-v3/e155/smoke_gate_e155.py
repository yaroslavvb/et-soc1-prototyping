#!/usr/bin/env python3
"""E155's registered smoke gate (a copy of tools/claims-v3/e148/smoke_gate_e148.py with the names changed): tools/claims-v3/e109/smoke_gate_e109.py's rule with E155's smoke items (e155_common.SMOKE_ITEMS): every smoke item has
at least one launch record, and every record is ok with tensor_errors 0. It prints each item's median cycles per op and its shape (not scored). Exit 0
if the gate passes, 1 if not.
    python3 tools/claims-v3/e155/smoke_gate_e155.py <smoke pass dir>
SPDX-License-Identifier: Apache-2.0"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e155_common as e  # noqa: E402
d = sys.argv[1]
recs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl")) if l.strip()]
bad, seen = [], {}
for r in recs:
    seen.setdefault(r["item"], []).append(r)
    if not r.get("ok") or r.get("tensor_errors", 1) != 0:
        bad.append(f"{r['item']}: ok={r.get('ok')} tensor_errors={r.get('tensor_errors')} result={r.get('result')}")
miss = [n for n in e.SMOKE_ITEMS if n not in seen]
for n in e.SMOKE_ITEMS:
    rr = seen.get(n, [])
    cpo = sorted(r.get("cycles_per_op") for r in rr)
    print(f"smoke {n}: {len(rr)} launch records, cycles per op {cpo[len(cpo) // 2] if cpo else None}, arows {rr[0].get('arows') if rr else None}, "
          f"acols {rr[0].get('acols') if rr else None}, row_mask {rr[0].get('row_mask') if rr else None}")
print("SMOKE-GATE", "PASS" if not bad and not miss else "FAIL", {"bad": bad, "missing": miss})
sys.exit(0 if not bad and not miss else 1)
