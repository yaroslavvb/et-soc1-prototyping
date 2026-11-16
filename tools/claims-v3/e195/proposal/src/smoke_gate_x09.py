#!/usr/bin/env python3
"""x09's smoke gate: the public lab repo's E110 gate (tools/claims-v3/e110/smoke_gate_e110.py: block.json "ok", every
named item launched with ok records and lines moved, every telemetry sample carrying the three rails and the DDR die
reading), and three of this request's own run gates on the smoke's runs: every launch record reports 1,024
participants, the memory shires' counters were read on the memory arms (not asked of an item the runner ran with the
host's --no-ms, as its configs.json shows: make_x09.py --no-ms; nor of any item with --ms-off), and the median sampler
time over each run is at most 60 ms (the meter keeps up with this request's write and paced traffic).

    python3 tools/claims-v3/x09/smoke_gate_x09.py <pass dir> anchor_pi,x9_rd_rnd,x9_wr_u4,x9_wrh_rnd,x9_wrh_nst [--ms-off]
    (exit 0 = pass)
"""
import gzip
import json
import os
import statistics
import sys


def jl(p):
    if not os.path.exists(p) and os.path.exists(p + ".gz"):
        p += ".gz"
    if not os.path.exists(p):
        return []
    op = gzip.open if p.endswith(".gz") else open
    return [json.loads(x) for x in op(p, "rt") if x.startswith("{")]


def no_ms_items(d):
    """The items the runner ran with the host's --no-ms (its configs.json holds every item as it ran it)."""
    try:
        cfg = json.load(open(os.path.join(d, "configs.json")))
    except (OSError, ValueError):
        return set()
    return {it.get("name") for it in cfg.get("items", []) if "--no-ms" in [str(x) for x in it.get("args") or []]}


def main():
    d, items = sys.argv[1], sys.argv[2].split(",")
    ms_off = "--ms-off" in sys.argv[3:]
    no_ms = no_ms_items(d)
    bad = []
    try:
        b = json.load(open(os.path.join(d, "block.json")))
    except (OSError, ValueError):
        b = {}
    if b.get("status") != "ok":
        bad.append("block.json status %r" % b.get("status"))
    runs = jl(os.path.join(d, "runs.jsonl"))
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    for it in items:
        rr = [r for r in runs if r.get("item") == it]
        if not rr:
            bad.append("%s never launched" % it)
            continue
        if not all(r.get("ok", True) for r in rr):
            bad.append("%s has a record that is not ok" % it)
        if it == "anchor_pi":
            continue
        if not any((r.get("ops") or 0) > 0 for r in rr):
            bad.append("%s moved nothing" % it)
        if any(int(r.get("participants", 0) or 0) != 1024 for r in rr):
            bad.append("%s: a launch without 1,024 participants" % it)
        memory_arm = not it.endswith(("_l1", "_scp", "_nst"))
        if memory_arm and not ms_off and it not in no_ms and not all(r.get("ms") and not r.get("ms_bad") for r in rr):
            bad.append("%s: the memory shires' counters were not read" % it)
        t0, t1 = min(r["t_start_ms"] for r in rr), max(r["t_end_ms"] for r in rr)
        took = [s.get("took_ms") for s in tel if t0 <= s.get("t_ms", -1) <= t1 and s.get("took_ms") is not None]
        if took and statistics.median(took) > 60:
            bad.append("%s: median sampler time %.0f ms over 60" % (it, statistics.median(took)))
    miss = sum(1 for s in tel if not all(k in s.get("sp", {}) for k in ("noc_w", "sram_w", "minion_w")) or
               "ddr" not in s.get("die_mv", {}))
    if not tel or miss:
        bad.append("telemetry: %d samples, %d without the rails or die_mv.ddr" % (len(tel), miss))
    off = sorted(i for i in items if i in no_ms)
    note = "; the memory shires' counters not asked (--no-ms): %s" % ",".join(off) if off else ""
    print("smoke gate %s: %s%s" % ("PASS" if not bad else "FAIL",
                                   "; ".join(bad) or "%d runs, %d telemetry samples" % (len(runs), len(tel)), note))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
