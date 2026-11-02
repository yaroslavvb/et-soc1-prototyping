#!/usr/bin/env python3
"""E125 (Q134): card 1's board-meter launch-gap dips, removed as E82's amendment A2 defines them (the primary frame on this card
since E82: E88, E91, E93 and E124 reduce with it). Standard library only.

    python3 tools/claims-v3/e125/dips_e125.py <out-dir> <pass dir> [<pass dir> ...]

A dip is a board_w sample i with board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W (posthoc_dips_e95.py's test, unchanged).
For each pass it writes <out-dir>/passes/<pass>/ holding the four files hl/reduce_hl.py reads (configs.json, runs.jsonl,
marks.jsonl, block.json copied byte for byte) and telemetry.jsonl.gz without the dip samples, and <out-dir>/dips.json: per pass the
samples, the dips, how many fall inside a run, and how many inside a run's registered power window [t0 + 1 s, t0 + 3 s).
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import shutil
import sys

DIP_W = 4.0
COPY = ("configs.json", "runs.jsonl", "marks.jsonl", "block.json")


def load_lines(d):
    p = os.path.join(d, "telemetry.jsonl.gz")
    if os.path.exists(p):
        return [x for x in gzip.open(p, "rt") if x.startswith("{")]
    return [x for x in open(os.path.join(d, "telemetry.jsonl")) if x.startswith("{")]


def jl(path):
    return [json.loads(x) for x in open(path) if x.strip().startswith("{")]


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    os.makedirs(os.path.join(out, "passes"), exist_ok=True)
    summary = {}
    for d in dirs:
        name = os.path.basename(d.rstrip("/"))
        lines = load_lines(d)
        tel = [json.loads(x) for x in lines]
        B = [s["board_w"] for s in tel]
        dips = [i for i in range(2, len(B) - 2) if B[i] < min(B[i - 2], B[i + 2]) - DIP_W]
        marks = [m for m in jl(os.path.join(d, "marks.jsonl")) if m.get("kind") == "run"]
        recs = jl(os.path.join(d, "runs.jsonl"))
        t0 = {}
        for r in recs:
            k = (r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))
            t0[k] = min(t0.get(k, r["t_start_ms"]), r["t_start_ms"])
        rows = []
        for i in dips:
            t = tel[i]["t_ms"]
            where, in_win = "between", False
            for m in marks:
                if m["t_start_ms"] <= t <= m["t_end_ms"]:
                    where = f"run {m['item']}"
                    k = (m["block"], m["item"], m.get("pos", 0), m.get("attempt", 1))
                    if k in t0:
                        in_win = t0[k] + 1000 <= t < t0[k] + 3000
                    break
            rows.append({"t_ms": t, "board_w": B[i], "neighbours_w": [B[i - 2], B[i + 2]], "where": where,
                         "in_power_window": in_win})
        summary[name] = {"samples": len(B), "dips": len(dips), "in_runs": sum(1 for r in rows if r["where"] != "between"),
                         "in_power_windows": sum(1 for r in rows if r["in_power_window"]), "rows": rows}
        c = os.path.join(out, "passes", name)
        if os.path.isdir(c):
            shutil.rmtree(c)
        os.makedirs(c)
        for f in COPY:
            if os.path.exists(os.path.join(d, f)):
                shutil.copy2(os.path.join(d, f), os.path.join(c, f))
        drop = set(dips)
        with gzip.open(os.path.join(c, "telemetry.jsonl.gz"), "wt") as g:
            for i, x in enumerate(lines):
                if i not in drop:
                    g.write(x if x.endswith("\n") else x + "\n")
        print(f"{name}: {len(B)} samples, {len(dips)} dips ({summary[name]['in_power_windows']} in a power window)")
    json.dump({"definition": f"board_w[i] < min(board_w[i-2], board_w[i+2]) - {DIP_W} W (E82 amendment A2; card 1's frame)",
               "passes": summary,
               "totals": {k: sum(v[k] for v in summary.values()) for k in ("samples", "dips", "in_runs", "in_power_windows")}},
              open(os.path.join(out, "dips.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
