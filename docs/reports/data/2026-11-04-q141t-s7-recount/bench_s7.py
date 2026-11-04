#!/usr/bin/env python3
"""Q141(t): the bench runs of REGISTRATION.md, through rtl-sim/fma_toggle_v2's run_kinds.py (unchanged), behind two checks.

    python3 -B bench_s7.py <bench dir> s27 <out counts.json> [--jobs 4] [--tmp <dir>]
    python3 -B bench_s7.py <bench dir> cal81 <out counts.json> --tiles fp32.cal_third_b17,fp32.cal_third_b20 [--jobs 4] [--tmp <dir>]

<bench dir> is a build of rtl-sim/fma_toggle_v2 (Q133(b)'s build): its seven files must hash as Q140(m)'s
bench-check/bench-sha256.txt, else the run stops before it starts. Every tile file must hash as its manifest says (pool 7's
MANIFEST for s27, Q140(m)'s bench-check/cal-tiles.json for cal81), else it stops.

  s27    pool 7's eight S tiles (the seven priority-1 and fp32.b_onebit_b20_third_a1p5) at all 27 points of
         RECOUNT-RULE.md section 1 (the three standard points counted again, as a determinism check)
  cal81  the named calibration tiles at the 54 points of N = 81 that N = 27 does not hold (RECOUNT-RULE.md section 4's step)

The bench runs at nice 10 (on top of this process's niceness) with --jobs workers; C is checked at every point by run_kinds.py
(check_mismatch). Writes <out> (run_kinds.py's own JSON) and <out minus .json>-run.json (wall time, jobs, points, nice, exit).
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
M9D = os.path.join(TOP, "docs", "reports", "data", "2026-11-04-q140m-m9")
BC = os.path.join(M9D, "bench-check")
POOL7 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind7")
KINDS = os.path.join(TOP, "tools", "claims-v3", "kinds")
OPS = 0.5 * 600e6 / 546
S_TILES = ("fp32.b_onebit_b20_one", "fp32.b_onebit_b20_full", "fp32.b_onebit_b20_pi", "fp32.b_onebit_b20_seventh",
           "fp32.b_onebit_b22_third", "fp16.b_onebit_b9_one", "fp16.b_onebit_b8_pi", "fp32.b_onebit_b20_third_a1p5")
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731


def points(n):
    """RECOUNT-RULE.md section 1: the midpoints of n equal parts of a 0.5 s launch at 600 MHz (546 cycles an op)"""
    return [int(OPS * (2 * j + 1) / (2 * n)) for j in range(n)]


def check_bench(bench):
    bad = []
    for line in open(os.path.join(BC, "bench-sha256.txt")):
        if not line.strip():
            continue
        h, f = line.split()
        p = os.path.join(bench, f)
        got = fsha(p) if os.path.exists(p) else "missing"
        if got != h:
            bad.append(f"{f}: {got} (want {h})")
    if bad:
        raise SystemExit("STOP: the bench build differs from Q140(m)'s bench-sha256.txt: " + "; ".join(bad))


def s_tiles():
    man = {}
    for line in open(os.path.join(POOL7, "MANIFEST")):
        f = line.split()
        if len(f) >= 4:
            man[f[2]] = (f[0], os.path.join(POOL7, f[1]), f[3])
    out = []
    for n in S_TILES:
        h, p, t = man[n]
        if fsha(p) != h:
            raise SystemExit(f"STOP: {n} does not hash as pool 7's MANIFEST says")
        out.append((t, n.split(".", 1)[1], p))
    return out


def cal_tiles(names):
    man = {m["name"]: m for m in json.load(open(os.path.join(BC, "cal-tiles.json")))["tiles"]}
    out = []
    for n in names:
        m = man[n]
        p = os.path.join(BC, m["file"])
        if fsha(p) != m["sha256"]:
            raise SystemExit(f"STOP: {n} does not hash as cal-tiles.json says")
        out.append((m["type"], n.split(".", 1)[1], p))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bench")
    ap.add_argument("step", choices=("s27", "cal81"))
    ap.add_argument("out")
    ap.add_argument("--tiles", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--tmp", default=None)
    a = ap.parse_args()
    bench = os.path.abspath(a.bench)
    check_bench(bench)
    if a.step == "s27":
        tiles, pts = s_tiles(), points(27)
    else:
        names = [x for x in a.tiles.split(",") if x]
        if not names:
            raise SystemExit("cal81 needs --tiles")
        tiles, pts = cal_tiles(names), sorted(set(points(81)) - set(points(27)))
    spec = ",".join(f"{t}:{n}:{p}" for t, n, p in tiles)
    cmd = ["nice", "-n", "10", sys.executable, "-B", "run_kinds.py", "--bin", "obj_vpu/Vtb", "--accum", "./accum", "--settle",
           "./settle_count", "--maps", "maps", "--kinds", KINDS, "--only", "__none__", "--jobs", str(a.jobs),
           "--points", ",".join(str(x) for x in pts), "--out", os.path.abspath(a.out), "--extra-tiles", spec]
    if a.tmp:
        os.makedirs(a.tmp, exist_ok=True)
        cmd += ["--tmp", os.path.abspath(a.tmp)]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=bench)
    t1 = time.time()
    run = {"step": a.step, "tiles": [f"{t}.{n}" for t, n, _ in tiles], "points": len(pts) * len(tiles), "points_per_tile": len(pts),
           "jobs": a.jobs, "nice_increment": 10, "nice_of_driver": os.nice(0), "start_epoch": int(t0), "end_epoch": int(t1),
           "wall_s": round(t1 - t0, 1), "exit": r.returncode}
    if r.returncode == 0:
        rows = json.load(open(a.out))["rows"]
        miss = {k: [p["n0"] for p in v["points"] if p.get("check_mismatch")] for k, v in rows.items()}
        run["rows"] = len(rows)
        run["check_mismatch_points"] = {k: v for k, v in miss.items() if v}
    base = a.out[:-5] if a.out.endswith(".json") else a.out
    json.dump(run, open(base + "-run.json", "w"), indent=1, sort_keys=True)
    print(json.dumps(run, sort_keys=True))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
