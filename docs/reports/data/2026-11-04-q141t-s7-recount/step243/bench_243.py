#!/usr/bin/env python3
"""Q141(t2): the convergence rule's 243-point step (../REGISTRATION-step243.md), through rtl-sim/fma_toggle_v2's run_kinds.py
(unchanged), behind the build, tile and point checks. It runs where the bench is built: the mini, under a memory and time cap, for
the step; the Intel's hashed build for one check point.

    python3 -B bench_243.py record-build <bench dir> <out record.json>
    python3 -B bench_243.py run <bench dir> <out counts.json> --tiles <name>[,<name>...] (--part 1/2 | --part 2/2 | --points n0,...)
                            [--build-record <record.json>] [--jobs 4] [--nice 10] [--tmp <dir>]
    python3 -B bench_243.py points                      # print the step's point sets and their checks, run nothing

record-build  hashes the build's three binaries (obj_vpu/Vtb, accum, settle_count) and its four inputs that are not built
              (maps/unit_float.map, maps/unit_int8.map, maps/vpu.map, run_kinds.py), which must hash as Q140(m)'s
              bench-check/bench-sha256.txt; and reads obj_vpu/Vtb__verFiles.dat, Verilator's own record of every file the build
              read with its content hash, with paths cut to core-et/..., bench/... or verilator/... and the command line's
              paths cut the same way.
run           checks the build: the four inputs as bench-sha256.txt; the three binaries as bench-sha256.txt (the Intel's build), or,
              with --build-record, as that record (a build on another machine: its binaries differ by construction, so its counts are
              checked against the Intel's build before any is quoted, REGISTRATION-step243.md section 2). Checks each tile's bytes
              against bench-check/cal-tiles.json. Points: --part 1/2 and 2/2 are the 162 points of N = 243 that N = 81 does not
              hold (RECOUNT-RULE.md section 1), split by j mod 3 (part 1: j = 0 mod 3, part 2: j = 2 mod 3; 81 each, both spread
              over the whole launch); --points names op indices (the build checks). Then run_kinds.py at nice +<nice> with --jobs
              workers, C checked at every point (check_mismatch), writing <out> (run_kinds.py's own JSON) and
              <out minus .json>-run.json (wall time, jobs, points, the machine's architecture, never its name).
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
OPS = 0.5 * 600e6 / 546
BINARIES = ("obj_vpu/Vtb", "accum", "settle_count")
TILES8 = ("fp32.cal_third_b21", "fp32.cal_pi_b21", "fp32.cal_third_b20", "fp32.cal_w67_b21", "fp32.cal_w79_b21",
          "fp32.cal_w67_b20", "fp32.cal_w79_b20", "fp32.cal_pi_b20")
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731


def points(n):
    """RECOUNT-RULE.md section 1: the midpoints of n equal parts of a 0.5 s launch at 600 MHz (546 cycles an op)"""
    return [int(OPS * (2 * j + 1) / (2 * n)) for j in range(n)]


def step_points():
    """The 243-point step's two parts, with the nesting checked: points(243)[1::3] is exactly points(81)."""
    p243, p81 = points(243), points(81)
    if p243[1::3] != p81 or len(set(p243)) != 243:
        raise SystemExit("STOP: N = 81's points are not exactly every third point of N = 243")
    part = {1: p243[0::3], 2: p243[2::3]}
    if sorted(part[1] + part[2]) != sorted(set(p243) - set(p81)) or len(part[1]) != 81 or len(part[2]) != 81:
        raise SystemExit("STOP: the two parts are not the 162 new points of N = 243")
    return part


def ref_hashes():
    out = {}
    for line in open(os.path.join(BC, "bench-sha256.txt")):
        if line.strip():
            h, f = line.split()
            out[f] = h
    return out


def cut(path):
    """A path as the record keeps it: no machine's directories."""
    p = path.replace("\\", "/")
    if "/core-et/" in p:
        return "core-et/" + p.split("/core-et/", 1)[1]
    if p.endswith("/core-et"):
        return "core-et"
    if "/" not in p:
        return "bench/" + p
    return "verilator/" + p.rsplit("/", 1)[1]


def verfiles(bench):
    """obj_vpu/Vtb__verFiles.dat: Verilator's record of each file the build read, with its content hash"""
    files, cmd = {}, None
    for line in open(os.path.join(bench, "obj_vpu", "Vtb__verFiles.dat"), errors="replace"):
        if line.startswith("C "):
            words = []
            for w in line[2:].strip().strip('"').split():
                if w.startswith("+incdir+") and "/" in w:
                    w = "+incdir+" + cut(w[len("+incdir+"):])
                elif w.startswith("/"):
                    w = cut(w)
                words.append(w)
            cmd = " ".join(words)
        elif line.startswith("S "):
            q = line.split('"')
            if len(q) >= 4:
                files[cut(q[3])] = q[1]
    return files, cmd


def check_build(bench, record):
    ref = ref_hashes()
    bad = []
    for f, h in ref.items():
        p = os.path.join(bench, f)
        got = fsha(p) if os.path.exists(p) else "missing"
        want = h
        if f in BINARIES and record:
            want = record["binaries"][f]
        if got != want:
            bad.append(f"{f}: {got} (want {want})")
    if bad:
        raise SystemExit("STOP: the bench build differs: " + "; ".join(bad))
    return "bench-sha256.txt (the Intel's build)" if not record else "the build record (inputs as bench-sha256.txt)"


def cal_tiles(names):
    man = {m["name"]: m for m in json.load(open(os.path.join(BC, "cal-tiles.json")))["tiles"]}
    out = []
    for n in names:
        if n not in man:
            raise SystemExit(f"STOP: {n} is not a calibration tile")
        m = man[n]
        p = os.path.join(BC, m["file"])
        if fsha(p) != m["sha256"]:
            raise SystemExit(f"STOP: {n} does not hash as cal-tiles.json says")
        out.append((m["type"], n.split(".", 1)[1], p))
    return out


def machine():
    return {"system": platform.system(), "arch": platform.machine(), "python": platform.python_version()}


def record_build(bench, out):
    ref = ref_hashes()
    rec = {"_note": "Q141(t2): a build of rtl-sim/fma_toggle_v2 (Q133(b)'s bench sources) as bench_243.py record-build read it",
           "binaries": {f: fsha(os.path.join(bench, f)) for f in BINARIES},
           "inputs": {f: fsha(os.path.join(bench, f)) for f in ref if f not in BINARIES}, "machine": machine()}
    rec["inputs_match_bench_sha256"] = all(rec["inputs"][f] == ref[f] for f in rec["inputs"])
    rec["binaries_match_bench_sha256"] = {f: rec["binaries"][f] == ref[f] for f in BINARIES}
    files, cmd = verfiles(bench)
    rec["verilator_files_read"] = files
    rec["verilator_command"] = cmd
    rec["no_dfg"] = bool(cmd and "-fno-dfg" in cmd.split())
    json.dump(rec, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in ("binaries", "inputs_match_bench_sha256", "no_dfg", "machine")}, sort_keys=True))
    if not rec["inputs_match_bench_sha256"] or not rec["no_dfg"]:
        raise SystemExit("STOP: the build's inputs differ from bench-sha256.txt, or it was built without -fno-dfg")


def run(a):
    bench = os.path.abspath(a.bench)
    record = json.load(open(a.build_record)) if a.build_record else None
    which = check_build(bench, record)
    names = [x for x in a.tiles.split(",") if x]
    if not names:
        raise SystemExit("run needs --tiles")
    tiles = cal_tiles(names)
    if a.part:
        k = {"1/2": 1, "2/2": 2}.get(a.part)
        if not k:
            raise SystemExit("--part is 1/2 or 2/2")
        pts = step_points()[k]
    elif a.points:
        pts = sorted({int(x) for x in a.points.split(",") if x})
    else:
        raise SystemExit("run needs --part or --points")
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
    try:
        pri = os.getpriority(os.PRIO_PROCESS, 0)
    except OSError:
        pri = None
    run = {"step": "cal243" if a.part else "check", "part": a.part, "tiles": [f"{t}.{n}" for t, n, _ in tiles],
           "points": len(pts) * len(tiles), "points_per_tile": len(pts), "n0": pts, "jobs": a.jobs, "nice_increment": a.nice,
           "priority_of_driver": pri, "build_checked_against": which, "driver_sha256": fsha(os.path.abspath(__file__)),
           "build_record_sha256": fsha(a.build_record) if a.build_record else None, "machine": machine(),
           "start_epoch": int(t0), "end_epoch": int(t1), "wall_s": round(t1 - t0, 1), "exit": r.returncode}
    if r.returncode == 0:
        rows = json.load(open(a.out))["rows"]
        miss = {k: [p["n0"] for p in v["points"] if p.get("check_mismatch")] for k, v in rows.items()}
        run["rows"] = len(rows)
        run["check_mismatch_points"] = {k: v for k, v in miss.items() if v}
        run["points_returned"] = sum(len(v["points"]) for v in rows.values())
    base = a.out[:-5] if a.out.endswith(".json") else a.out
    json.dump(run, open(base + "-run.json", "w"), indent=1, sort_keys=True)
    print(json.dumps({k: run[k] for k in ("step", "part", "tiles", "points", "wall_s", "exit")}, sort_keys=True), flush=True)
    sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("record-build", "run", "points"))
    ap.add_argument("bench", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--tiles", default="")
    ap.add_argument("--part", default="")
    ap.add_argument("--points", default="")
    ap.add_argument("--build-record", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--nice", type=int, default=10)
    ap.add_argument("--tmp", default=None)
    a = ap.parse_args()
    if a.mode == "points":
        part = step_points()
        print(json.dumps({"tiles": list(TILES8), "part1": part[1], "part2": part[2], "n_new_per_tile": 162}, indent=0))
        return
    if not a.bench or not a.out:
        raise SystemExit(f"{a.mode} needs <bench dir> <out>")
    if a.mode == "record-build":
        record_build(os.path.abspath(a.bench), a.out)
    else:
        run(a)


if __name__ == "__main__":
    main()
