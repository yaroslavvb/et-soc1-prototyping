#!/usr/bin/env python3
"""Measure matmul throughput and energy efficiency (FLOP/s per watt) on an ET-SoC-1 card.

Runs on the lab machine, next to the card:

    scripts/mmbench-power.py --launcher build/launchers/mmbench_launcher \
        --kernel build/kernels/nekko/mmbench.elf --out build/mmbench-power

1. Snapshots the chip clocks and temperatures, then starts scripts/et-power-log.sh,
   which reads board power from the service processor about 8 times a second.
2. Records an idle baseline.
3. For each workload, runs a short calibration launch, then enough launches of
   mmbench_launcher to keep the chip busy for --seconds. Iteration counts stay
   within the range where the fp32/fp16 results are exact, so every launch is checked.
   The cards are shared (CLAUDE.md, lab etiquette): every launcher process runs under
   `timeout 10`, so no single run holds the device for more than 10 s.
4. Averages the power samples inside each workload's launch windows. The first
   --settle seconds are skipped while power ramps up. Then prints throughput,
   watts, GFLOP/s per W (board), and GFLOP/s per W above idle.

The launcher only opens the ops node. The power logger needs the mgmt node, so
et-powertop must not be running.
"""
import argparse
import json
import math
import os
import signal
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DMS = os.path.join(os.environ.get("ET", "/opt/et"), "bin", "dev_mngt_service")

# name, mode, ntiles, private pools, calibration iters
WORKLOADS = [
    ("fp32-tensor-L2", "fp32", 16, False, 2000),
    ("fp16-tensor-L2", "fp16", 16, False, 2000),
    ("int8-tensor-L2", "int8", 16, False, 2000),
    ("fp32-tensor-DRAM", "fp32", 64, True, 20),
]


def dm_query(cmd):
    out = subprocess.run([DMS, "-m", cmd, "-n", "0", "-u", "5000"], capture_output=True, text=True)
    lines = [l.split("]: ", 1)[-1].strip() for l in (out.stdout + out.stderr).splitlines()
             if "verifyService" in l]
    return lines


def run_launcher(args, mode, ntiles, private, iters, repeat):
    cmd = ["timeout", "10", args.launcher, "-k", args.kernel, "-d", args.device, "-s", args.shire_mask, "-m", mode,
           "-n", str(ntiles), "-i", str(iters), "-r", str(repeat), "-t", str(args.timeout)]
    if private:
        cmd.append("-p")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    runs = [json.loads(l.split(" ", 1)[1]) for l in proc.stdout.splitlines() if l.startswith("MMBENCH ")]
    if proc.returncode != 0 or not runs or any(r["check"] == "FAIL" for r in runs):
        sys.stderr.write(proc.stdout[-3000:] + proc.stderr[-3000:])
        raise SystemExit(f"launcher failed for {mode} (exit {proc.returncode})")
    return runs


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--launcher", required=True)
    p.add_argument("--kernel", required=True)
    p.add_argument("--out", required=True, help="directory for power.csv, runs.jsonl, results.json")
    p.add_argument("--device", default="silicon")
    p.add_argument("--shire_mask", default="0xffffffff")
    p.add_argument("--seconds", type=float, default=6.0,
                   help="target busy time per workload; keep it under the lab's 10 s device limit")
    p.add_argument("--launch_seconds", type=float, default=1.5, help="target length of one launch")
    p.add_argument("--idle", type=float, default=8.0, help="idle baseline before the first workload")
    p.add_argument("--gap", type=float, default=5.0, help="idle time between workloads")
    p.add_argument("--settle", type=float, default=1.0, help="seconds skipped at the start of a workload")
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--only", default="", help="comma-separated workload names to run")
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    only = set(filter(None, args.only.split(",")))
    workloads = [w for w in WORKLOADS if not only or w[0] in only]

    info = {"freqs": dm_query("DM_CMD_GET_ASIC_FREQUENCIES"),
            "temp_before": dm_query("DM_CMD_GET_MODULE_CURRENT_TEMPERATURE")}

    power_csv = os.path.join(args.out, "power.csv")
    logger = subprocess.Popen([os.path.join(HERE, "et-power-log.sh"), "0", "0.1"],
                              stdout=open(power_csv, "w"), start_new_session=True)
    runs_path = os.path.join(args.out, "runs.jsonl")
    all_runs = []
    try:
        t_idle0 = time.time() * 1000
        time.sleep(args.idle)
        t_idle1 = time.time() * 1000
        for name, mode, ntiles, private, cal_iters in workloads:
            cal = run_launcher(args, mode, ntiles, private, cal_iters, 1)[0]
            per_iter = cal["wall_s"] / cal_iters
            iters = max(1, int(args.launch_seconds / per_iter))
            if mode != "int8":
                iters = min(iters, cal["max_exact_iters"])
            repeat = max(1, math.ceil(args.seconds / (iters * per_iter)))
            print(f"{name}: calibration {cal['tflops']:.3f} TFLOP/s; running iters={iters} x{repeat}", flush=True)
            runs = run_launcher(args, mode, ntiles, private, iters, repeat)
            for r in runs:
                r["workload"] = name
            all_runs += runs
            time.sleep(args.gap)
    finally:
        os.killpg(logger.pid, signal.SIGTERM)
        logger.wait()
    info["temp_after"] = dm_query("DM_CMD_GET_MODULE_CURRENT_TEMPERATURE")
    with open(runs_path, "w") as f:
        for r in all_runs:
            f.write(json.dumps(r) + "\n")

    samples = []
    for line in open(power_csv):
        t, _, w = line.strip().partition(",")
        if t.isdigit():
            samples.append((int(t), float(w)))
    idle = [w for t, w in samples if t_idle0 + 1000 <= t <= t_idle1]
    idle_w = statistics.median(idle) if idle else float("nan")

    results = []
    for name, mode, ntiles, private, _ in workloads:
        runs = [r for r in all_runs if r["workload"] == name]
        if not runs:
            continue
        first = runs[0]["t_start_ms"] + args.settle * 1000
        watts = [w for t, w in samples
                 if t >= first and any(r["t_start_ms"] <= t <= r["t_end_ms"] for r in runs)]
        busy_s = sum(r["wall_s"] for r in runs)
        flop = sum(r["total_flop"] for r in runs)
        tflops = flop / busy_s / 1e12
        mean_w = statistics.mean(watts) if watts else float("nan")
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
        })

    summary = {"idle_w": idle_w, "idle_samples": len(idle), "info": info, "results": results,
               "shire_mask": args.shire_mask, "device": args.device}
    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nidle board power: {idle_w:.2f} W (median of {len(idle)} samples)")
    print("| workload | TFLOP/s (TOP/s int8) | flop/minion/cycle | board W | GFLOP/s per W | per W above idle | check |")
    print("|---|---|---|---|---|---|---|")
    for r in results:
        above = f"{r['gflops_per_w_above_idle']:.0f}" if r["gflops_per_w_above_idle"] else "n/a"
        print(f"| {r['workload']} | {r['tflops']:.3f} | {r['flop_per_minion_cycle']:.2f} | {r['mean_w']:.1f} "
              f"({r['min_w']:.1f}-{r['max_w']:.1f}) | {r['gflops_per_w']:.0f} | {above} | {','.join(r['check'])} |")


if __name__ == "__main__":
    main()
