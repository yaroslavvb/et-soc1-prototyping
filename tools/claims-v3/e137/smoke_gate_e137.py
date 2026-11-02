#!/usr/bin/env python3
"""E137's registered smoke gate (E137.md, Protocol): on the smoke pass (E137's six smoke items, e137_common.SMOKE_ITEMS, 2 s runs):
every item has launch records; every record is ok, with tensor_errors 0; each item's median cycles per op (launch records, launch >= 0) is
within 0.5% of E78's 546 (fp32, fp16) or 318 (int8), E78's own run gate; every launch record's clock reads 0.595-0.605 GHz (600 MHz);
the block's two config reads (config_start.json, config_end.json) read card 1's TDP 65 W, threshold 65 C and 600 MHz. Exit 0 if the
gate passes, 1 if not. Standard library only.

    python3 tools/claims-v3/e137/smoke_gate_e137.py <smoke pass dir>
SPDX-License-Identifier: Apache-2.0"""
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e137_common as e137  # noqa: E402

CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}


def main():
    d = sys.argv[1]
    recs = [json.loads(x) for x in open(os.path.join(d, "runs.jsonl")) if x.strip()]
    bad, seen = [], {}
    for r in recs:
        seen.setdefault(r["item"], []).append(r)
        if not r.get("ok") or r.get("tensor_errors", 0) != 0:
            bad.append(f"{r['item']}: ok={r.get('ok')} tensor_errors={r.get('tensor_errors')} result={r.get('result')}")
    miss = [n for n in e137.SMOKE_ITEMS if n not in seen]
    for n in e137.SMOKE_ITEMS:
        rr = [r for r in seen.get(n, []) if r.get("launch", 0) >= 0]
        if not rr:
            continue
        ty = rr[0]["type"]
        cpo = statistics.median(r["cycles_per_op"] for r in rr)
        ghz = sorted({r.get("ghz") for r in rr})
        okc = abs(cpo / CPO[ty] - 1) <= 0.005
        okg = all(isinstance(g, (int, float)) and 0.595 <= g <= 0.605 for g in ghz)
        if not okc:
            bad.append(f"{n}: median cycles per op {cpo} not within 0.5% of {CPO[ty]}")
        if not okg:
            bad.append(f"{n}: clock {ghz} GHz outside 0.595-0.605")
        print(f"smoke {n}: {len(rr)} launch records, median cycles per op {cpo}, ghz {ghz[0]}-{ghz[-1]}")
    for nm in ("config_start", "config_end"):
        try:
            c = json.load(open(os.path.join(d, nm + ".json")))
        except (OSError, ValueError):
            c = None
        if not (isinstance(c, dict) and c.get("tdp_w") == 65 and c.get("temp_threshold_c") == 65 and c.get("minion_mhz") == 600):
            bad.append(f"{nm}: {c} is not card 1's 65 W / 65 C / 600 MHz")
        print(f"smoke {nm}: {c}")
    ok = not bad and not miss
    print("SMOKE-GATE", "PASS" if ok else "FAIL", {"bad": bad, "missing": miss})
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
