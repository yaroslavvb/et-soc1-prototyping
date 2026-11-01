#!/usr/bin/env python3
"""E100: the smoke's check, before the session. Every process rc 0; the flags did what they say; the long kernel's one launch stayed under the host's 6 s; the card read 65 W and 65 C; no limit in reach.

    python3 smoke_ok.py <RUNDIR>         exit 0 when all of it holds; prints what it read
"""
import gzip
import json
import os
import sys


def jl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        return [json.loads(x) for x in gzip.open(path + ".gz", "rt") if x.startswith("{")]
    return [json.loads(x) for x in open(path) if x.startswith("{")]


def main():
    rd = sys.argv[1]
    bad = []
    L = [x for x in jl(os.path.join(rd, "launches.jsonl")) if x.get("role") == "work"]
    for x in L:
        ks = x.get("sparsity", [])
        walls = [round(k.get("wall_s", 0), 3) for k in ks]
        gaps = [ks[j]["t_start_ms"] - ks[j - 1]["t_end_ms"] for j in range(1, len(ks))]
        print(x["run"], "rc", x.get("rc"), "kernels", len(ks), "walls", walls[:5], "gaps ms", gaps[:6], "cycles per op", ks[-1].get("cycles_per_op") if ks else None)
        if x.get("rc") != 0 or not ks:
            bad.append(f"{x['run']}: rc {x.get('rc')}, {len(ks)} kernels")
        if "smoke-n" in x["run"]:
            if len(ks) != 1 or not (3.0 < ks[0]["wall_s"] < 5.7):
                bad.append(f"{x['run']}: expected one kernel of 3-5.7 s, got {walls}")
        if "smoke-a100" in x["run"] and gaps and max(gaps[1:] or [0]) < 20:
            bad.append(f"{x['run']}: no gaps seen: {gaps}")
        if "smoke-a0" in x["run"] and gaps and max(gaps) > 5:
            bad.append(f"{x['run']}: gaps too long: {gaps}")
    for r in jl(os.path.join(rd, "runs.jsonl")):
        cfg = (r.get("queries") or {}).get("config") or {}
        if cfg.get("tdp_w") != 65 or cfg.get("temp_threshold_c") != 65:
            bad.append(f"{r['run']}: config {cfg}")
        S = jl(os.path.join(rd, "tel", r["run"] + ".jsonl"))
        hot = [x for x in S if ((x.get("temp_c") or {}).get("minshire") or [0])[0] >= 65 or (x.get("board_w") or 0) >= 65]
        if hot:
            bad.append(f"{r['run']}: {len(hot)} readings at 65 C or 65 W")
    end = json.load(open(os.path.join(rd, "end.json")))
    print("end", end)
    if end.get("exit") != 0:
        bad.append(f"end {end}")
    print("smoke check:", "ok" if not bad else "FAILED: " + "; ".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
