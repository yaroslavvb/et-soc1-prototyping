#!/usr/bin/env python3
"""E190 (Q169) desk: E136's process timings from its committed launch records (aifoundry2, Mon 2 Nov 2026), for plan_e190.py's process-time
estimates at 8,192^3. No card. Standard library only.

    python3 -I -B tools/claims-v3/e190/desk/timing_e136.py > tools/claims-v3/e190/desk/timing_e136.txt

Per work process: setup = the first launch's start - the process's start (device open, kernel load, the pools' fill and layout, the DMA of A and B,
C allocated); process = its end - its start; check launch = launch -3's wall; check = the host's read-back of C and its reference over 64 tiles;
tail = the process's end - launch -3's end. Medians [min, max] over runs, per GEMM, format and --seconds.
"""
import gzip
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "docs", "reports", "data", "2026-11-02-e136-large-gemm", "aifoundry2"))


def main():
    rows = []
    for sess in ("smoke", "s1"):
        for line in gzip.open(os.path.join(D, sess, "launches.jsonl.gz"), "rt"):
            if not line.startswith("{"):
                continue
            r = json.loads(line)
            if r.get("role") != "work":
                continue
            sp = r.get("sparsity") or []
            L = [x for x in sp if x.get("test") == "fma"]
            chk = [x for x in sp if x.get("test") == "check"]
            if not L:
                continue
            c3 = [x for x in L if x["launch"] == -3]
            rows.append({"arm": L[0]["arm"], "type": L[0]["type"], "secs": r["cmd"][r["cmd"].index("--seconds") + 1] if "--seconds" in r["cmd"] else None,
                         "setup_ms": min(x["t_start_ms"] for x in L) - r["t_start_ms"], "proc_ms": r["t_end_ms"] - r["t_start_ms"],
                         "c3_ms": (c3[0]["t_end_ms"] - c3[0]["t_start_ms"]) if c3 else None,
                         "check_ms": (chk[0]["t_end_ms"] - chk[0]["t_start_ms"]) if chk else None,
                         "tail_ms": (r["t_end_ms"] - c3[0]["t_end_ms"]) if c3 else None, "n_launch": len(L)})
    by = {}
    for x in rows:
        by.setdefault((x["arm"], x["type"], x["secs"]), []).append(x)
    print(__doc__.split("\n\n")[0])
    print("median [min, max] in ms over runs")
    for k in sorted(by):
        v = by[k]

        def f(key):
            a = [x[key] for x in v if x[key] is not None]
            return f"{st.median(a):.0f} [{min(a)}, {max(a)}]" if a else "-"
        print(f"{k[0]:11s} {k[1]:5s} --seconds {k[2]}: n {len(v)}; setup {f('setup_ms')}; process {f('proc_ms')}; check launch {f('c3_ms')}; "
              f"check {f('check_ms')}; tail {f('tail_ms')}; launches {f('n_launch')}")


if __name__ == "__main__":
    main()
