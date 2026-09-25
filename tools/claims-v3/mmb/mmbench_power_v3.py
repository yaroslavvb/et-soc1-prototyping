#!/usr/bin/env python3
"""V3-MMB's patched copy of scripts/mmbench-power.py (matmul throughput and board power per workload).

    python3 tools/claims-v3/mmb/mmbench_power_v3.py run --root TREE --launcher L --kernel K --only W --seconds 6 \
        --out DIR --rundir RUNDIR          # on the card, inside the block's ettelem sampler
    python3 tools/claims-v3/mmb/mmbench_power_v3.py finish --out DIR --telemetry DIR/telemetry.jsonl --card CARD
    python3 scripts/mmbench-report-data.py DIR                      # the original report reducer, unchanged

What is the same as scripts/mmbench-power.py: the workload table, the idle baseline (--idle 8 s, median leaving out
its first second), the calibration launch and the iters/repeat rule (--launch_seconds 1.5, capped at max_exact_iters
for fp32/fp16), --seconds, --gap 5 s, --settle 1 s, every launcher under `timeout 10`, idle_before() and its window
(3.5 to 1.8 s before the first timed launch), and every number in results.json (the code below is copied).

What differs, and why:
 1. No power logger of its own. The original starts scripts/et-power-log.sh, a bash loop of dev_mngt_service queries
    that it stops with killpg(SIGTERM); a query killed mid-request leaves a reply queued and poisons the management
    node (lab notes, 24 Sep). Here the block holds lib.sh's ettelem sampler (start_sampler/stop_sampler: 10 Hz,
    SIGTERM-safe) around `run`, and `finish` writes the samples' board_w (DM_CMD_GET_MODULE_POWER / 100, the same
    reading et-power-log.sh prints) as the same power.csv (epoch_ms,watts).
 2. No dev_mngt_service queries before and after (clocks, temperatures): nothing else may open the management node
    while the sampler runs. `finish` fills results.json info.freqs / temp_before / temp_after from the telemetry in
    the original's text form, so mmbench-report-data.py still reads "Minion Shire: 600 Mhz".
 3. Split into `run` (card) and `finish` (no card).
 4. The launcher runs in --rundir: it writes an 8 MB traceKernels_dev0_0.bin into its working directory.
 5. --root: the tree root, chdir'd to explicitly (the copy sits two levels deeper than the original).
 6. The calibration launch's MMBENCH line is kept (cal.jsonl); a failed launcher is recorded in meta.json.
 7. V3_DRY=1 in the environment: print each launcher command (and skip the sleeps) instead of running anything.
 8. `finish` adds, per workload, the die temperature (temp_c.minshire[0]) at the start and end and over the power
    window, the set of mhz.minion values during the timed launches, and each launch's drop flags (implied_ghz outside
    0.595-0.605; on aifoundry2 any sample inside the launch with mhz.minion != 600): V3-MMB's registered drop rules.
    A sample without a clock or temperature block (ettelem leaves out a block whose query failed) is not a reading.
 9. Each launcher process's wall time and exit code go to meta.json and results.json (launcher_processes). If the
    calibration process's fixed cost (its wall time minus its launch) plus the planned launches would pass 9 s, the
    timed process runs fewer launches (repeat_planned is kept), so timeout 10 never kills it.
"""
import argparse
import gzip
import json
import math
import os
import statistics
import subprocess
import sys
import time

DRY = bool(os.environ.get("V3_DRY"))

# Window for a workload's own idle, in seconds before its first timed launch (as scripts/mmbench-power.py).
IDLE_BEFORE_S = (3.5, 1.8)

# name, mode, ntiles, private pools, calibration iters (as scripts/mmbench-power.py)
WORKLOADS = [
    ("fp32-tensor-L2", "fp32", 16, False, 2000),
    ("fp16-tensor-L2", "fp16", 16, False, 2000),
    ("int8-tensor-L2", "int8", 16, False, 2000),
    ("fp32-tensor-DRAM", "fp32", 64, True, 20),
]
GHZ_BAND = (0.595, 0.605)  # PLAN3 V3-MMB: drop launches with implied_ghz outside this band


def idle_before_window(t_first_ms, t_prev_end_ms=None):
    lo = t_first_ms - IDLE_BEFORE_S[0] * 1000
    if t_prev_end_ms is not None:
        lo = max(lo, t_prev_end_ms + 1000)
    return [lo, t_first_ms - IDLE_BEFORE_S[1] * 1000]


def idle_before(samples, t_first_ms, t_prev_end_ms=None):
    lo, hi = idle_before_window(t_first_ms, t_prev_end_ms)
    w = [x for t, x in samples if lo <= t <= hi]
    return statistics.mean(w) if w else float("nan")


class LaunchFailed(Exception):
    pass


PROC_BUDGET_S = 9.0  # V3: a timed process predicted longer than this gets fewer launches (timeout 10 would kill it)


def run_launcher(args, mode, ntiles, private, iters, repeat, procs=None):
    cmd = ["timeout", "10", args.launcher, "-k", args.kernel, "-d", args.device, "-s", args.shire_mask, "-m", mode,
           "-n", str(ntiles), "-i", str(iters), "-r", str(repeat), "-t", str(args.timeout)]
    if private:
        cmd.append("-p")
    if DRY:
        sys.stderr.write("DRY hold10: " + " ".join(cmd[2:]) + f"   (cwd {args.rundir})\n")
        return []
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=args.rundir, stdin=subprocess.DEVNULL)
    wall = time.time() - t0
    runs = [json.loads(l.split(" ", 1)[1]) for l in proc.stdout.splitlines() if l.startswith("MMBENCH ")]
    if procs is not None:  # V3: every launcher process's wall time and exit code (the 10 s margin, in meta.json)
        procs.append({"mode": mode, "ntiles": ntiles, "private": private, "iters": iters, "repeat": repeat,
                      "rc": proc.returncode, "proc_wall_s": round(wall, 3), "launches": len(runs),
                      "launch_wall_s": round(sum(r["wall_s"] for r in runs), 3)})
    if proc.returncode != 0 or not runs or any(r["check"] == "FAIL" for r in runs):
        sys.stderr.write(proc.stdout[-3000:] + proc.stderr[-3000:])
        raise LaunchFailed(f"launcher failed for {mode} (exit {proc.returncode}, {len(runs)} lines, {wall:.2f} s)")
    return runs


def nap(s):
    if DRY:
        sys.stderr.write(f"DRY sleep {s}\n")
    else:
        time.sleep(s)


def cmd_run(args):
    os.chdir(args.root)
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.rundir, exist_ok=True)
    only = set(filter(None, args.only.split(",")))
    workloads = [w for w in WORKLOADS if not only or w[0] in only]
    if only - {w[0] for w in WORKLOADS}:
        raise SystemExit(f"unknown workload(s) {sorted(only - {w[0] for w in WORKLOADS})}: use the full names")
    meta = {"args": vars(args), "workloads": [], "error": None, "dry": DRY, "procs": []}
    all_runs, cal_runs = [], []
    try:
        meta["t_idle0_ms"] = time.time() * 1000
        nap(args.idle)
        meta["t_idle1_ms"] = time.time() * 1000
        for name, mode, ntiles, private, cal_iters in workloads:
            cal = run_launcher(args, mode, ntiles, private, cal_iters, 1, meta["procs"])
            if DRY:
                meta["workloads"].append({"workload": name, "iters": None, "repeat": None})
                sys.stderr.write(f"DRY {name}: timed launches with iters and repeat from the calibration\n")
                run_launcher(args, mode, ntiles, private, "ITERS", "REPEAT")
                nap(args.gap)
                continue
            cal = cal[0]
            cal["workload"] = name
            cal_runs.append(cal)
            per_iter = cal["wall_s"] / cal_iters
            iters = max(1, int(args.launch_seconds / per_iter))
            if mode != "int8":
                iters = min(iters, cal["max_exact_iters"])
            repeat = max(1, math.ceil(args.seconds / (iters * per_iter)))
            # V3 guard (not in the original): the process's fixed cost (init, tile pools, teardown) is the calibration
            # process's wall time minus its launch; if that plus the planned launches would pass PROC_BUDGET_S, run fewer
            # launches, so timeout 10 never kills the timed process (the DRAM workload builds 256 MB of private tiles).
            overhead = meta["procs"][-1]["proc_wall_s"] - cal["wall_s"]
            planned = repeat
            while repeat > 1 and overhead + repeat * iters * per_iter > PROC_BUDGET_S:
                repeat -= 1
            print(f"{name}: calibration {cal['tflops']:.3f} TFLOP/s; running iters={iters} x{repeat}"
                  + (f" (planned x{planned}; process overhead {overhead:.2f} s)" if repeat != planned else ""), flush=True)
            meta["workloads"].append({"workload": name, "iters": iters, "repeat": repeat, "repeat_planned": planned,
                                      "proc_overhead_s": round(overhead, 3),
                                      "predicted_proc_s": round(overhead + repeat * iters * per_iter, 3)})
            runs = run_launcher(args, mode, ntiles, private, iters, repeat, meta["procs"])
            for r in runs:
                r["workload"] = name
            all_runs += runs
            nap(args.gap)
    except LaunchFailed as e:
        meta["error"] = str(e)
    meta["t_end_ms"] = time.time() * 1000
    with open(os.path.join(args.out, "runs.jsonl"), "w") as f:
        for r in all_runs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(args.out, "cal.jsonl"), "w") as f:
        for r in cal_runs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(args.out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    if meta["error"]:
        raise SystemExit(meta["error"])


def load_tel(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rt") as f:
                return [json.loads(l) for l in f if l.startswith("{")]
    return []


def cmd_finish(args):
    meta = json.load(open(os.path.join(args.out, "meta.json")))
    all_runs = [json.loads(l) for l in open(os.path.join(args.out, "runs.jsonl"))]
    if not all_runs:
        print("finish: no timed launches (dry run or failed workload): nothing to reduce")
        return 0
    tel = sorted(load_tel(args.telemetry), key=lambda r: r["t_ms"])
    samples = [(int(r["t_ms"]), float(r["board_w"])) for r in tel if "board_w" in r]
    with open(os.path.join(args.out, "power.csv"), "w") as f:
        f.write("epoch_ms,watts\n")
        for t, w in samples:
            f.write(f"{t},{w:.2f}\n")
    t_idle0, t_idle1 = meta["t_idle0_ms"], meta["t_idle1_ms"]
    settle = meta["args"]["settle"]
    idle = [w for t, w in samples if t_idle0 + 1000 <= t <= t_idle1]
    idle_w = statistics.median(idle) if idle else float("nan")

    # ettelem leaves out a block whose query failed (mhz, temp_c, ...): those samples count as "no reading", never crash
    def mhz_of(r):
        return (r.get("mhz") or {}).get("minion")

    def die_of(r):
        m = (r.get("temp_c") or {}).get("minshire")
        return m[0] if m else None

    def info_from(r):
        if r is None or "mhz" not in r:
            return []
        return [f"ASIC Frequency Minion Shire: {r['mhz']['minion']} Mhz", f"ASIC Frequency NOC: {r['mhz']['noc']} Mhz",
                f"ASIC Frequency DDR: {r['mhz']['ddr']} Mhz"]

    def temps_from(r):
        if r is None or "temp_c" not in r:
            return []
        return [f"PMIC SYS Temperature Output: {r['temp_c']['pmic']} c",
                f"MINSHIRE Current Temperature Output: {r['temp_c']['minshire'][0]} c",
                f"MINSHIRE Low Temperature Output: {r['temp_c']['minshire'][1]} c",
                f"MINSHIRE High Temperature Output: {r['temp_c']['minshire'][2]} c"]

    first_run = min(r["t_start_ms"] for r in all_runs)
    tel_f = [s for s in tel if "mhz" in s]
    tel_t = [s for s in tel if "temp_c" in s]
    info = {"freqs": info_from(([s for s in tel_f if s["t_ms"] <= first_run] or tel_f[:1] or [None])[-1]),
            "temp_before": temps_from(tel_t[0] if tel_t else None),
            "temp_after": temps_from(tel_t[-1] if tel_t else None),
            "source": "ettelem telemetry of the block's sampler (tools/claims-v3/mmb/mmbench_power_v3.py finish)"}

    # drop flags per launch (PLAN3 V3-MMB): implied_ghz outside 0.595-0.605; on aifoundry2 any mhz.minion != 600
    for r in all_runs:
        inside = [s for s in tel if r["t_start_ms"] <= s["t_ms"] <= r["t_end_ms"] and mhz_of(s) is not None]
        if not inside:  # a launch shorter than the sample interval: the samples on either side (with a clock reading)
            b = [s for s in tel_f if s["t_ms"] <= r["t_start_ms"]][-1:]
            inside = b + [s for s in tel_f if s["t_ms"] >= r["t_end_ms"]][:1]
        r["tel_mhz_minion"] = sorted({mhz_of(s) for s in inside})
        r["tel_samples"] = len(inside)
        drop = []
        if not GHZ_BAND[0] <= r["implied_ghz"] <= GHZ_BAND[1]:
            drop.append("implied_ghz")
        if args.card == "aifoundry2" and (not inside or r["tel_mhz_minion"] != [600]):
            drop.append("mhz_minion")
        r["drop"] = drop

    results = []
    prev_end = None
    for name, mode, ntiles, private, _ in WORKLOADS:
        runs = [r for r in all_runs if r["workload"] == name]
        if not runs:
            continue
        idle_b = idle_before(samples, runs[0]["t_start_ms"], prev_end)
        idle_b_window = idle_before_window(runs[0]["t_start_ms"], prev_end)
        prev_end = runs[-1]["t_end_ms"]
        first = runs[0]["t_start_ms"] + settle * 1000
        watts = [w for t, w in samples
                 if t >= first and any(r["t_start_ms"] <= t <= r["t_end_ms"] for r in runs)]
        busy_s = sum(r["wall_s"] for r in runs)
        flop = sum(r["total_flop"] for r in runs)
        tflops = flop / busy_s / 1e12
        mean_w = statistics.mean(watts) if watts else float("nan")
        win_die = [die_of(s) for s in tel_t if first <= s["t_ms"] <= runs[-1]["t_end_ms"]]
        s0 = ([s for s in tel_t if s["t_ms"] <= runs[0]["t_start_ms"]] or [None])[-1]
        s1 = ([s for s in tel_t if s["t_ms"] <= runs[-1]["t_end_ms"]] or [None])[-1]
        results.append({
            "workload": name, "mode": mode, "private_pools": private, "ntiles": ntiles,
            "launches": len(runs), "iters": runs[0]["iters"], "busy_s": busy_s, "tflops": tflops,
            "flop_per_minion_cycle": statistics.mean(r["flop_per_minion_cycle"] for r in runs),
            "implied_ghz": statistics.mean(r["implied_ghz"] for r in runs),
            "check": sorted({r["check"] for r in runs}),
            "power_samples": len(watts), "mean_w": mean_w,
            "min_w": min(watts) if watts else None, "max_w": max(watts) if watts else None,
            "gflops_per_w": tflops * 1000 / mean_w,
            "gflops_per_w_above_idle": tflops * 1000 / (mean_w - idle_w) if mean_w > idle_w else None,
            "idle_before_w": idle_b, "idle_before_window_ms": [round(t) for t in idle_b_window],
            "power_window_ms": [round(first), runs[-1]["t_end_ms"]],
            "gflops_per_w_above_idle_before": tflops * 1000 / (mean_w - idle_b) if mean_w > idle_b else None,
            # V3 additions (telemetry)
            "die_c_start": die_of(s0) if s0 else None,
            "die_c_end": die_of(s1) if s1 else None,
            "die_c_mean_power_window": statistics.mean(win_die) if win_die else None,
            "mhz_minion_launches": sorted({m for r in runs for m in r["tel_mhz_minion"]}),
            "dropped_launches": [r["launch"] for r in runs if r["drop"]],
        })
    summary = {"idle_w": idle_w, "idle_samples": len(idle), "idle_window_ms": [round(t_idle0 + 1000), round(t_idle1)],
               "info": info, "results": results, "shire_mask": meta["args"]["shire_mask"],
               "device": meta["args"]["device"], "card": args.card, "telemetry_samples": len(tel),
               "telemetry_samples_without": {"board_w": len(tel) - len(samples), "mhz": len(tel) - len(tel_f),
                                             "temp_c": len(tel) - len(tel_t)},
               "launcher_processes": meta.get("procs", []), "timed_workloads": meta.get("workloads", [])}
    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(args.out, "launch_flags.jsonl"), "w") as f:
        for r in all_runs:
            f.write(json.dumps({k: r[k] for k in ("workload", "launch", "t_start_ms", "t_end_ms", "implied_ghz",
                                                  "tel_mhz_minion", "tel_samples", "drop")}) + "\n")
    print(f"idle board power: {idle_w:.2f} W (median of {len(idle)} samples)")
    for r in results:
        print(f"{r['workload']}: {r['tflops']:.3f} T, {r['mean_w']:.2f} W ({r['power_samples']} samples), idle before "
              f"{r['idle_before_w']:.2f} W, die {r['die_c_start']}->{r['die_c_end']} C, mhz {r['mhz_minion_launches']}, "
              f"dropped launches {r['dropped_launches']}")
    return 5 if any(r["drop"] for r in all_runs) else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--root", required=True, help="tree root (this repository on aifoundry2, ~/nekko on aifoundry3)")
    r.add_argument("--launcher", required=True)
    r.add_argument("--kernel", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--rundir", required=True, help="working directory for the launcher (it writes trace dumps there)")
    r.add_argument("--device", default="silicon")
    r.add_argument("--shire_mask", default="0xffffffff")
    r.add_argument("--seconds", type=float, default=6.0)
    r.add_argument("--launch_seconds", type=float, default=1.5)
    r.add_argument("--idle", type=float, default=8.0)
    r.add_argument("--gap", type=float, default=5.0)
    r.add_argument("--settle", type=float, default=1.0)
    r.add_argument("--timeout", type=int, default=120)
    r.add_argument("--only", default="")
    f = sub.add_parser("finish")
    f.add_argument("--out", required=True)
    f.add_argument("--telemetry", required=True)
    f.add_argument("--card", required=True, choices=("aifoundry2", "aifoundry3"))
    a = p.parse_args()
    if a.cmd == "run":
        a.out, a.rundir = os.path.abspath(a.out), os.path.abspath(a.rundir)
        cmd_run(a)
        return 0
    return cmd_finish(a)


if __name__ == "__main__":
    sys.exit(main())
