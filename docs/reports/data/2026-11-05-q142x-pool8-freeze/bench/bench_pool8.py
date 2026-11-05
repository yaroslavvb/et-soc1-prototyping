#!/usr/bin/env python3
"""Q142(x): pool 8's bench counts, term b's input for Q142(p)'s frozen predictor, through rtl-sim/fma_toggle_v2's run_kinds.py
(unchanged), behind the build, tile and C checks. From M10's bench_m10.py (docs/reports/data/2026-11-04-q142m-m10/bench/), as dated
note A1-4 beside tools/claims-v3/kinds/blind8/DESIGN.md says (lab ebf68c52, committed before any count). Changes from bench_m10.py:
(i) the tiles come from tools/claims-v3/kinds/blind8/blind8.json, each one's bytes checked against its sha256; (ii) no case-S
restriction: every fp32 and fp16 tile is counted at the points the convergence rule names (POOL8-REGISTRATION.md section 2);
(iii) int8 is counted only at run_kinds.py's own three launch points (--launch, 318 cycles an op), never at the float points;
(iv) a point whose check_mismatch is not 0 makes the run exit 5 after its record is written.

    python3 -B bench_pool8.py check-build <bench dir> [--build-record <record.json>]
    python3 -B bench_pool8.py points --n <N> --from <N0> [--part k/m]          # the points of a step (N0 = 0: all of N), run nothing
    python3 -B bench_pool8.py check-tiles --tiles <name>[,<name>...]            # the tiles' bytes against blind8.json, run nothing
    python3 -B bench_pool8.py run <bench dir> <out counts.json> --tiles <name>[,...]
                              (--n N --from N0 [--part k/m] | --points n0,... | --launch)
                              [--build-record <record.json>] [--jobs 4] [--nice 10] [--tmp <dir>]

Points (RECOUNT-RULE.md section 1): the midpoints of N equal parts of a 0.5 s launch at 600 MHz, 546 cycles an op; N = 3, 9, 27,
81 or 243, each set holding the one before. --n/--from and --points are for fp32 and fp16 tiles only; --launch is for int8 tiles
only (run_kinds.py --points launch: its three launch points at the type's cycles an op, as pool 6's and 7's counts were made). The
build check: the four unbuilt inputs as Q140(m)'s bench-check/bench-sha256.txt, and the three binaries as that file (the Intel's
build) or, with --build-record, as that record (a build on another machine, made with -fno-dfg). run_kinds.py runs at nice
+<nice> with --jobs workers, C checked at every point (check_mismatch), writing <out> (its own JSON) and <out minus .json>-run.json
(wall time, jobs, points, the tiles' and the manifest's sha256, the machine's architecture, never its name).
Standard library only. SPDX-License-Identifier: Apache-2.0
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
POOL = os.path.join(KINDS, "blind8", "blind8.json")
OPS = 0.5 * 600e6 / 546
CPO = {"fp32": 546, "fp16": 546, "int8": 318}
BINARIES = ("obj_vpu/Vtb", "accum", "settle_count")
NS = (3, 9, 27, 81, 243)
FLOATS = ("fp32", "fp16")
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731


def points(n):
    return [int(OPS * (2 * j + 1) / (2 * n)) for j in range(n)]


def launch_points(typ):
    """run_kinds.py's launch_points, for the record only (run_kinds.py computes its own with --points launch)"""
    ops = 0.5 * 600e6 / CPO[typ]
    return [int(ops * f) for f in (1 / 6, 1 / 2, 5 / 6)]


def step(n, n0, part=None):
    if n not in NS or (n0 != 0 and n0 not in NS) or n0 >= n:
        raise SystemExit(f"STOP: a step goes from 0 or one of {NS} to a larger one of {NS}")
    pn = points(n)
    p0 = set(points(n0)) if n0 else set()
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
    man = {m["name"]: m for m in json.load(open(POOL))["tiles"]}
    out = []
    for n in names:
        if n not in man:
            raise SystemExit(f"STOP: {n} is not in blind8.json")
        m = man[n]
        p = os.path.join(os.path.dirname(POOL), m["file"])
        h = fsha(p)
        if h != m["sha256"]["whole"]:
            raise SystemExit(f"STOP: {n} does not hash as blind8.json says")
        out.append((m["type"], n.split(".", 1)[1], p, h))
    return out


def machine():
    return {"system": platform.system(), "arch": platform.machine(), "python": platform.python_version()}


def run(a):
    bench = os.path.abspath(a.bench)
    record = json.load(open(a.build_record)) if a.build_record else None
    which = check_build(bench, record)
    tiles = pool_tiles([x for x in a.tiles.split(",") if x])
    types = {t for t, _, _, _ in tiles}
    if a.launch:
        if types != {"int8"}:
            raise SystemExit("STOP: --launch is for int8 tiles only (their own three points)")
        pts_arg, pts, mode = "launch", launch_points("int8"), "launch"
    else:
        if not types <= set(FLOATS):
            raise SystemExit("STOP: int8 tiles are counted only at their own three points (--launch)")
        if a.points:
            pts = sorted({int(x) for x in a.points.split(",") if x})
            allp = set(points(243))
            if not set(pts) <= allp:
                raise SystemExit("STOP: a point is not among the convergence rule's points (N = 243 holds every N's)")
        elif a.n:
            pts = step(a.n, a.from_n, a.part)
        else:
            raise SystemExit("run needs --n and --from, --points, or --launch")
        pts_arg, mode = ",".join(str(x) for x in pts), "list"
    spec = ",".join(f"{t}:{n}:{p}" for t, n, p, _ in tiles)
    cmd = ["nice", "-n", str(a.nice), sys.executable, "-B", "run_kinds.py", "--bin", "obj_vpu/Vtb", "--accum", "./accum", "--settle",
           "./settle_count", "--maps", "maps", "--kinds", KINDS, "--only", "__none__", "--jobs", str(a.jobs),
           "--points", pts_arg, "--out", os.path.abspath(a.out), "--extra-tiles", spec]
    if a.tmp:
        os.makedirs(a.tmp, exist_ok=True)
        cmd += ["--tmp", os.path.abspath(a.tmp)]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=bench)
    t1 = time.time()
    rec = {"step": (f"{a.from_n}->{a.n}" if a.n else ("launch" if a.launch else "points")), "part": a.part,
           "tiles": [f"{t}.{n}" for t, n, _, _ in tiles], "tile_sha256": {f"{t}.{n}": h for t, n, _, h in tiles},
           "pool_manifest": os.path.relpath(POOL, TOP), "pool_manifest_sha256": fsha(POOL),
           "points": len(pts) * len(tiles), "points_per_tile": len(pts), "points_mode": mode, "n0": pts, "jobs": a.jobs,
           "nice_increment": a.nice, "build_checked_against": which, "driver_sha256": fsha(os.path.abspath(__file__)),
           "build_record_sha256": fsha(a.build_record) if a.build_record else None, "machine": machine(),
           "start_epoch": int(t0), "end_epoch": int(t1), "wall_s": round(t1 - t0, 1), "exit": r.returncode}
    rc = r.returncode
    if r.returncode == 0:
        rows = json.load(open(a.out))["rows"]
        miss = {k: [p["n0"] for p in v["points"] if p.get("check_mismatch")] for k, v in rows.items()}
        rec["rows"] = len(rows)
        rec["check_mismatch_points"] = {k: v for k, v in miss.items() if v}
        rec["points_returned"] = sum(len(v["points"]) for v in rows.values())
        rec["n0_as_asked"] = all(sorted(p["n0"] for p in v["points"]) == sorted(pts) for v in rows.values()) and len(rows) == len(tiles)
        if rec["check_mismatch_points"] or rec["points_returned"] != rec["points"] or not rec["n0_as_asked"]:
            rc = 5
    rec["driver_exit"] = rc
    base = a.out[:-5] if a.out.endswith(".json") else a.out
    json.dump(rec, open(base + "-run.json", "w"), indent=1, sort_keys=True)
    print(json.dumps({k: rec.get(k) for k in ("step", "part", "points_mode", "points", "wall_s", "exit", "driver_exit",
                                              "check_mismatch_points")}, sort_keys=True), flush=True)
    sys.exit(rc)


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
    t = sub.add_parser("check-tiles")
    t.add_argument("--tiles", required=True)
    r = sub.add_parser("run")
    r.add_argument("bench")
    r.add_argument("out")
    r.add_argument("--tiles", required=True)
    r.add_argument("--n", type=int)
    r.add_argument("--from", dest="from_n", type=int)
    r.add_argument("--part")
    r.add_argument("--points")
    r.add_argument("--launch", action="store_true")
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
    elif a.cmd == "check-tiles":
        ts = pool_tiles([x for x in a.tiles.split(",") if x])
        print(json.dumps({"tiles_ok": len(ts), "pool_manifest_sha256": fsha(POOL), "types": sorted({x[0] for x in ts})}))
    else:
        if a.jobs > 4:
            raise SystemExit("STOP: at most 4 jobs")
        run(a)


if __name__ == "__main__":
    main()
