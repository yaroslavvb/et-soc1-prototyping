#!/usr/bin/env python3
"""Q142(m), M10's term (b): count pool 6's and pool 7's single-high-bit (case S) tiles at more launch points, through
rtl-sim/fma_toggle_v2's run_kinds.py (unchanged), behind the build, tile and point checks (tools/claims-v3/m10/REGISTRATION.md
section 3b, committed e9367b66 before this file). Adapted from Q141(t2)'s step243/bench_243.py: the same build checks; the tiles
are read from the pools' manifests instead of the calibration list; the points are any step of the convergence rule.

    python3 -B bench_m10.py check-build <bench dir> --build-record <record.json>
    python3 -B bench_m10.py points --n <N> --from <N0> [--part k/m]       # print the new points of a step, run nothing
    python3 -B bench_m10.py run <bench dir> <out counts.json> --tiles <name>[,<name>...] (--n N --from N0 [--part k/m] |
                            --points n0,...) [--build-record <record.json>] [--jobs 4] [--nice 10] [--tmp <dir>]

Points (RECOUNT-RULE.md section 1): the midpoints of N equal parts of a 0.5 s launch at 600 MHz, 546 cycles an op; N = 3, 9, 27,
81 or 243, each set holding the one before. A step N0 -> N counts the N - N0 points of N that N0 does not hold; --part k/m keeps
every m-th of them from the k-th (each part spread over the whole launch). The build check: the four unbuilt inputs as Q140(m)'s
bench-check/bench-sha256.txt, and the three binaries as bench-sha256.txt (the Intel's build) or, with --build-record, as that record
(a build on another machine). Each tile's bytes are checked against its pool manifest's sha256. run_kinds.py runs at nice +<nice>
with --jobs workers, C checked at every point (check_mismatch), writing <out> (its own JSON) and <out minus .json>-run.json (wall
time, jobs, points, the machine's architecture, never its name). Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
BC = os.path.join(TOP, "docs", "reports", "data", "2026-11-04-q140m-m9", "bench-check")
KINDS = os.path.join(TOP, "tools", "claims-v3", "kinds")
POOLS = (os.path.join(KINDS, "blind6", "blind6.json"), os.path.join(KINDS, "blind7", "blind7.json"))
OPS = 0.5 * 600e6 / 546
BINARIES = ("obj_vpu/Vtb", "accum", "settle_count")
NS = (3, 9, 27, 81, 243)
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731


def points(n):
    return [int(OPS * (2 * j + 1) / (2 * n)) for j in range(n)]


def step(n, n0, part=None):
    if n not in NS or n0 not in NS or n0 >= n:
        raise SystemExit(f"STOP: a step goes from one of {NS} to a larger one")
    pn, p0 = points(n), set(points(n0))
    if not p0 <= set(pn) or len(set(pn)) != n:
        raise SystemExit(f"STOP: N = {n0}'s points are not all among N = {n}'s")
    new = [p for p in pn if p not in p0]
    if len(new) != n - n0:
        raise SystemExit("STOP: the step's new points do not number N - N0")
    if part:
        k, m = (int(x) for x in part.split("/"))
        if not 1 <= k <= m:
            raise SystemExit("--part is k/m with 1 <= k <= m")
        new = new[k - 1::m]
    return new


def ref_hashes():
    out = {}
    for line in open(os.path.join(BC, "bench-sha256.txt")):
        if line.strip():
            h, f = line.split()
            out[f] = h
    return out


def check_build(bench, record):
    bad = []
    for f, h in ref_hashes().items():
        p = os.path.join(bench, f)
        got = fsha(p) if os.path.exists(p) else "missing"
        want = record["binaries"][f] if (f in BINARIES and record) else h
        if got != want:
            bad.append(f"{f}: {got} (want {want})")
    if bad:
        raise SystemExit("STOP: the bench build differs: " + "; ".join(bad))
    if record and not record.get("no_dfg"):
        raise SystemExit("STOP: the record's build was not made with -fno-dfg")
    return "bench-sha256.txt (the Intel's build)" if not record else "the build record (inputs as bench-sha256.txt)"


def pool_tiles(names):
    man = {}
    for pth in POOLS:
        for m in json.load(open(pth))["tiles"]:
            man[m["name"]] = (m, os.path.dirname(pth))
    out = []
    for n in names:
        if n not in man:
            raise SystemExit(f"STOP: {n} is in neither pool's manifest")
        m, d = man[n]
        if not (m.get("case") or "").startswith("S"):
            raise SystemExit(f"STOP: {n} is not a case-S tile")
        p = os.path.join(d, m["file"])
        if fsha(p) != m["sha256"]["whole"]:
            raise SystemExit(f"STOP: {n} does not hash as its manifest says")
        out.append((m["type"], n.split(".", 1)[1], p))
    return out


def machine():
    return {"system": platform.system(), "arch": platform.machine(), "python": platform.python_version()}


def run(a):
    bench = os.path.abspath(a.bench)
    record = json.load(open(a.build_record)) if a.build_record else None
    which = check_build(bench, record)
    tiles = pool_tiles([x for x in a.tiles.split(",") if x])
    if a.points:
        pts = sorted({int(x) for x in a.points.split(",") if x})
    elif a.n:
        pts = step(a.n, a.from_n, a.part)
    else:
        raise SystemExit("run needs --n and --from, or --points")
    spec = ",".join(f"{t}:{n}:{p}" for t, n, p in tiles)
    cmd = ["nice", "-n", str(a.nice), sys.executable, "-B", "run_kinds.py", "--bin", "obj_vpu/Vtb", "--accum", "./accum", "--settle",
           "./settle_count", "--maps", "maps", "--kinds", KINDS, "--only", "__none__", "--jobs", str(a.jobs),
           "--points", ",".join(str(x) for x in pts), "--out", os.path.abspath(a.out), "--extra-tiles", spec]
    if a.tmp:
        os.makedirs(a.tmp, exist_ok=True)
        cmd += ["--tmp", os.path.abspath(a.tmp)]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=bench)
    t1 = time.time()
    rec = {"step": f"{a.from_n}->{a.n}" if a.n else "check", "part": a.part, "tiles": [f"{t}.{n}" for t, n, _ in tiles],
           "points": len(pts) * len(tiles), "points_per_tile": len(pts), "n0": pts, "jobs": a.jobs, "nice_increment": a.nice,
           "build_checked_against": which, "driver_sha256": fsha(os.path.abspath(__file__)),
           "build_record_sha256": fsha(a.build_record) if a.build_record else None, "machine": machine(),
           "start_epoch": int(t0), "end_epoch": int(t1), "wall_s": round(t1 - t0, 1), "exit": r.returncode}
    if r.returncode == 0:
        rows = json.load(open(a.out))["rows"]
        miss = {k: [p["n0"] for p in v["points"] if p.get("check_mismatch")] for k, v in rows.items()}
        rec["rows"] = len(rows)
        rec["check_mismatch_points"] = {k: v for k, v in miss.items() if v}
        rec["points_returned"] = sum(len(v["points"]) for v in rows.values())
    base = a.out[:-5] if a.out.endswith(".json") else a.out
    json.dump(rec, open(base + "-run.json", "w"), indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in ("step", "part", "tiles", "points", "wall_s", "exit")}, sort_keys=True), flush=True)
    sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check-build")
    c.add_argument("bench")
    c.add_argument("--build-record")
    p = sub.add_parser("points")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--from", dest="from_n", type=int, required=True)
    p.add_argument("--part")
    r = sub.add_parser("run")
    r.add_argument("bench")
    r.add_argument("out")
    r.add_argument("--tiles", required=True)
    r.add_argument("--n", type=int)
    r.add_argument("--from", dest="from_n", type=int)
    r.add_argument("--part")
    r.add_argument("--points")
    r.add_argument("--build-record")
    r.add_argument("--jobs", type=int, default=4)
    r.add_argument("--nice", type=int, default=10)
    r.add_argument("--tmp")
    a = ap.parse_args()
    if a.cmd == "check-build":
        rec = json.load(open(a.build_record)) if a.build_record else None
        print("BUILD OK:", check_build(os.path.abspath(a.bench), rec))
    elif a.cmd == "points":
        pts = step(a.n, a.from_n, a.part)
        print(json.dumps({"n": a.n, "from": a.from_n, "part": a.part, "count": len(pts), "n0": pts}))
    else:
        run(a)


if __name__ == "__main__":
    main()
