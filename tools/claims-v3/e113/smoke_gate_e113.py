#!/usr/bin/env python3
"""E113 (Q133): the smoke gate. PASS (exit 0) when the smoke pass's block.json says ok and every run in runs.jsonl is ok,
ran on all 1,024 minions, and every fma run's cycles per op is within 0.5% of 546 (E78's fp32 count): the new tiles load and
run as the kernel's own. Anything else exits 1 and no registered pass runs.
    python3 tools/claims-v3/e113/smoke_gate_e113.py <pass dir>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

d = sys.argv[1]
why = []
try:
    b = json.load(open(os.path.join(d, "block.json")))
    if b.get("status") != "ok":
        why.append(f"block status {b.get('status')}")
except (OSError, ValueError) as e:
    why.append(f"block.json: {e}")
runs = []
try:
    runs = [json.loads(x) for x in open(os.path.join(d, "runs.jsonl")) if x.strip().startswith("{")]
except OSError as e:
    why.append(f"runs.jsonl: {e}")
items = sorted({r.get("item") for r in runs})
if not {"anchor_pi", "als_h8", "alq_h8"} <= set(items):
    why.append(f"items run {items}")
for r in runs:
    if not r.get("ok"):
        why.append(f"{r.get('item')} not ok")
    if r.get("minions") != 1024:
        why.append(f"{r.get('item')} minions {r.get('minions')}")
    c = r.get("cycles_per_op")
    if c is None or abs(c / 546.0 - 1) > 0.005:
        why.append(f"{r.get('item')} cycles/op {c}")
print("SMOKE GATE", "PASS" if not why else "FAIL", f"({len(runs)} runs, items {items})", "; ".join(why))
sys.exit(0 if not why else 1)
