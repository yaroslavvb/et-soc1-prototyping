#!/usr/bin/env python3
"""E110's smoke gate: block.json "ok", every named item launched at least once with ok records and a nonzero line rate on the memory
items, and every telemetry sample carrying the three rails and die_mv.ddr the reducer reads.

    python3 tools/claims-v3/e110/smoke_gate_e110.py <pass dir> anchor_pi,wl_64,vl_64,l2_u8     (exit 0 = pass)
"""
import gzip
import json
import os
import sys


def jl(p):
    if not os.path.exists(p) and os.path.exists(p + ".gz"):
        p += ".gz"
    op = gzip.open if p.endswith(".gz") else open
    return [json.loads(x) for x in op(p, "rt") if x.startswith("{")]


def main():
    d, items = sys.argv[1], sys.argv[2].split(",")
    bad = []
    b = json.load(open(os.path.join(d, "block.json")))
    if b.get("status") != "ok":
        bad.append("block.json status %r" % b.get("status"))
    runs = jl(os.path.join(d, "runs.jsonl"))
    for it in items:
        rr = [r for r in runs if r.get("item") == it]
        if not rr:
            bad.append("%s never launched" % it)
            continue
        if not all(r.get("ok", True) for r in rr):
            bad.append("%s has a record that is not ok" % it)
        if it != "anchor_pi" and not any((r.get("ops") or 0) > 0 for r in rr):
            bad.append("%s moved no lines" % it)
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    miss = sum(1 for s in tel if not all(k in s.get("sp", {}) for k in ("noc_w", "sram_w", "minion_w")) or "ddr" not in s.get("die_mv", {}))
    if not tel or miss:
        bad.append("telemetry: %d samples, %d without the rails or die_mv.ddr" % (len(tel), miss))
    print("smoke gate %s: %s" % ("PASS" if not bad else "FAIL", "; ".join(bad) or "%d runs, %d telemetry samples" % (len(runs), len(tel))))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
