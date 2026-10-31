#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E82 amendment A2's labelled POST-HOC view (not a rule; it moves no verdict): card 1's board reading sometimes
lands on the 1-2 ms gap between two of a run's launches and reads low for one service-processor pass. This script
counts those dips per pass and re-runs the registered reduction (reduce_e82.py, i.e. reduce_e78.py unchanged) on a
copy of each pass whose telemetry has the dip samples removed, every gate unchanged.

    python3 tools/claims-v3/kinds/posthoc_dips_e82.py <out dir> <pass dir> [<pass dir> ...]

A dip (A2's definition, on the recorded series): board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W.
Writes <out>/dips.json (per pass: dips, where they fall, the gap to the nearest launch boundary) and
<out>/e82-nodips.json (+ .txt, .csv) from the filtered copies. The copies live under <out>/passes/.
"""
import bisect
import gzip
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIP_W = 4.0


def load(d):
    p = os.path.join(d, "telemetry.jsonl.gz")
    op = gzip.open if os.path.exists(p) else open
    p = p if os.path.exists(p) else os.path.join(d, "telemetry.jsonl")
    return [line for line in op(p, "rt") if line.startswith("{")]


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    os.makedirs(os.path.join(out, "passes"), exist_ok=True)
    summary, copies = {}, []
    for d in dirs:
        name = os.path.basename(d.rstrip("/"))
        lines = load(d)
        tel = [json.loads(x) for x in lines]
        B = [s["board_w"] for s in tel]
        dips = [i for i in range(2, len(B) - 2) if B[i] < min(B[i - 2], B[i + 2]) - DIP_W]
        marks = sorted((json.loads(x) for x in open(os.path.join(d, "marks.jsonl"))), key=lambda m: m["t_start_ms"])
        recs = sorted((json.loads(x) for x in open(os.path.join(d, "runs.jsonl"))), key=lambda r: r["t_start_ms"])
        bounds = sorted(b for r in recs for b in (r["t_start_ms"], r["t_end_ms"]))
        rows = []
        for i in dips:
            t = tel[i]["t_ms"]
            where, in_window = "between", False
            for m in marks:
                if m["t_start_ms"] <= t <= m["t_end_ms"]:
                    where = f"{m['kind']} {m['item']}"
                    if m["kind"] == "run":
                        rr = [r for r in recs if r["item"] == m["item"] and r.get("pos") == m.get("pos")]
                        if rr:
                            t0 = min(r["t_start_ms"] for r in rr)
                            in_window = t0 + 1000 <= t < t0 + 3000
                    break
            j = bisect.bisect_right(bounds, t)
            after = t - bounds[j - 1] if j else None
            rows.append({"t_ms": t, "board_w": B[i], "neighbours_w": [B[i - 2], B[i + 2]], "where": where,
                         "in_power_window": in_window, "ms_after_launch_boundary": after})
        summary[name] = {"samples": len(B), "dips": len(dips), "in_runs": sum(1 for r in rows if r["where"].startswith("run")),
                         "in_power_windows": sum(1 for r in rows if r["in_power_window"]), "rows": rows}
        # the filtered copy: every file linked, the telemetry rewritten without the dip samples
        c = os.path.join(out, "passes", name)
        if os.path.isdir(c):
            shutil.rmtree(c)
        os.makedirs(c)
        for f in os.listdir(d):
            if f.startswith("telemetry.jsonl"):
                continue
            src = os.path.join(d, f)
            (shutil.copytree if os.path.isdir(src) else shutil.copy2)(src, os.path.join(c, f))
        drop = set(dips)
        with gzip.open(os.path.join(c, "telemetry.jsonl.gz"), "wt") as g:
            for i, x in enumerate(lines):
                if i not in drop:
                    g.write(x if x.endswith("\n") else x + "\n")
        copies.append(c)
    json.dump({"definition": f"board_w[i] < min(board_w[i-2], board_w[i+2]) - {DIP_W} W (E82 amendment A2)",
               "passes": summary,
               "totals": {"dips": sum(v["dips"] for v in summary.values()),
                          "in_runs": sum(v["in_runs"] for v in summary.values()),
                          "in_power_windows": sum(v["in_power_windows"] for v in summary.values())}},
              open(os.path.join(out, "dips.json"), "w"), indent=1)
    r = subprocess.run([sys.executable, os.path.join(HERE, "reduce_e82.py"), *copies, "--no-refit",
                        "--out", os.path.join(out, "e82-nodips.json"), "--txt", os.path.join(out, "e82-nodips.txt"),
                        "--csv", os.path.join(out, "runs-nodips.csv")], capture_output=True, text=True)
    print(r.stdout[-1500:], r.stderr[-1500:])
    for name, v in summary.items():
        print(f"{name}: {v['dips']} dips, {v['in_runs']} in runs, {v['in_power_windows']} in power windows")
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
