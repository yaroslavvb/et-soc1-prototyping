#!/usr/bin/env python3
"""Board power and energy for the sparsity probes on all 1024 minions. Runs on the lab machine:

    python3 workloads/sparsity/run_energy.py --host-bin build/sparsity/host/sparsity_host --out build/sparsity-energy

A background thread reads board power, the minion clock and the minion voltage from the service processor
about 9 times a second (dev_mngt_service through /dev/et0_mgmt, so quit et-powertop first). Each
configuration runs as its own `timeout 10 sparsity_host ... --seconds S` process, so no run holds the shared
card for more than 10 s. Power is averaged over each configuration's launch windows after the first --settle
seconds. --only NAMES also sets the run order.

Reported per configuration: throughput from the device cycle counts, mean board power, power above idle
and above `spin` (the same harts in an integer loop), and energy per TensorFMA, per useful multiply-add
(one whose A and B elements are both nonzero), per layer or per byte, depending on the probe.
"""
import argparse
import json
import os
import re
import statistics
import subprocess
import threading
import time

DMS = os.path.join(os.environ.get("ET", "/opt/et"), "bin", "dev_mngt_service")
ALL = ["--shires", "0xFFFFFFFF", "--per-shire", "32"]

# name, sparsity_host arguments, what runs
CONFIGS = [
    ("spin", ["--test", "spin", *ALL], "hart 0 of every minion in an integer loop"),
    ("fma-dense", ["--test", "fma", "--type", "fp32", "--pattern", "elem", "--sweep", "0", *ALL],
     "TensorFMA32, A and B in L1 scratchpad, no zeros"),
    ("fma-50", ["--test", "fma", "--type", "fp32", "--pattern", "elem", "--sweep", "0.5", *ALL],
     "TensorFMA32, half of A's elements zero"),
    ("fma-875", ["--test", "fma", "--type", "fp32", "--pattern", "elem", "--sweep", "0.875", *ALL],
     "TensorFMA32, 7/8 of A's elements zero"),
    ("fma-zero", ["--test", "fma", "--type", "fp32", "--pattern", "elem", "--sweep", "1", *ALL],
     "TensorFMA32, A all zeros"),
    ("fma-col50", ["--test", "fma", "--type", "fp32", "--pattern", "col", "--sweep", "0.5", *ALL],
     "TensorFMA32, half of A's columns zero"),
    ("fma-rowmask", ["--test", "fma", "--type", "fp32", "--pattern", "none", "--sweep", "0", "--row-mask", "0x00FF", *ALL],
     "TensorFMA32, dense A, tensor_mask skips 8 of 16 rows"),
    ("gemv-dense-90", ["--test", "gemv", "--gemv", "dense", "--sweep", "0.9", *ALL],
     "1024x4096 layer, 90% zero x, every W line loaded"),
    ("gemv-skip-0", ["--test", "gemv", "--gemv", "skip", "--sweep", "0", *ALL], "same layer, dense x"),
    ("gemv-skip-90", ["--test", "gemv", "--gemv", "skip", "--sweep", "0.9", *ALL],
     "same layer, 90% zero x, only needed W lines loaded, empty slices skipped"),
    ("gemv-skip-99", ["--test", "gemv", "--gemv", "skip", "--sweep", "0.99", *ALL], "same, 99% zero x"),
]


def dm_query(cmd):
    out = subprocess.run([DMS, "-m", cmd, "-n", "0", "-u", "5000"], capture_output=True, text=True)
    return [l.split("]: ", 1)[-1].strip() for l in (out.stdout + out.stderr).splitlines() if "verifyService" in l]


class PowerLogger(threading.Thread):
    def __init__(self, interval):
        super().__init__(daemon=True)
        self.interval, self.samples, self.stop = interval, [], threading.Event()

    def run(self):
        def query(cmd, pattern):
            out = subprocess.run([DMS, "-m", cmd, "-n", "0", "-u", "2000"], capture_output=True, text=True)
            m = re.search(pattern, out.stdout + out.stderr)
            return float(m.group(1)) if m else None
        while not self.stop.is_set():
            t = time.time() * 1000
            w = query("DM_CMD_GET_MODULE_POWER", r"Module Power Output: ([0-9.]+) W")
            mhz = query("DM_CMD_GET_ASIC_FREQUENCIES", r"Minion Shire: ([0-9]+) Mhz")
            mv = query("DM_CMD_GET_ASIC_VOLTAGE", r"Voltage MINION: ([0-9]+) mV")
            if w is not None:
                self.samples.append((t, w, mhz, mv))
            self.stop.wait(self.interval)


def work(r):
    """(unit, amount) done by one launch record, for energy per unit."""
    if r["test"] == "fma":
        ops = r["iters"] * r["minions"]
        return "tensorfma", ops
    if r["test"] == "gemv":
        return "layer", r["iters"]
    if r["test"] == "tload":
        return "byte", r["bytes_requested"]
    return None, 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host-bin", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seconds", type=float, default=4.0, help="launch time per configuration (keep well under 10)")
    p.add_argument("--idle", type=float, default=6.0, help="idle baseline before and after the configurations")
    p.add_argument("--gap", type=float, default=3.0, help="idle time between configurations")
    p.add_argument("--settle", type=float, default=0.7, help="seconds skipped at the start of each configuration")
    p.add_argument("--only", default="", help="comma-separated configuration names")
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    only = [n for n in args.only.split(",") if n]  # also the run order
    by_name = {c[0]: c for c in CONFIGS}
    configs = [by_name[n] for n in only] if only else CONFIGS

    info = {"freqs": dm_query("DM_CMD_GET_ASIC_FREQUENCIES"),
            "temp_before": dm_query("DM_CMD_GET_MODULE_CURRENT_TEMPERATURE")}
    logger = PowerLogger(0.05)
    logger.start()
    runs, idle_windows = [], []
    try:
        t = time.time() * 1000
        time.sleep(args.idle)
        idle_windows.append((t + 1000, time.time() * 1000))
        for name, cli, _ in configs:
            cmd = ["timeout", "10", args.host_bin, *cli, "--seconds", str(args.seconds), "--budget", "8"]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            got = [json.loads(l.split(" ", 1)[1]) for l in proc.stdout.splitlines() if l.startswith("SPARSITY ")]
            if proc.returncode != 0 or not got or not all(r["ok"] for r in got):
                print(proc.stdout[-2000:], proc.stderr[-2000:])
                raise SystemExit(f"{name}: sparsity_host failed with exit {proc.returncode}")
            for r in got:
                r["config"] = name
            runs += got
            print(f"{name}: {len(got)} launches", flush=True)
            time.sleep(args.gap)
        t = time.time() * 1000
        time.sleep(args.idle)
        idle_windows.append((t + 1000, time.time() * 1000))
    finally:
        logger.stop.set()
        logger.join()
    info["temp_after"] = dm_query("DM_CMD_GET_MODULE_CURRENT_TEMPERATURE")

    samples = logger.samples
    # Raw data first, so a bug below cannot lose a measurement.
    with open(os.path.join(args.out, "runs.jsonl"), "w") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(args.out, "power.csv"), "w") as f:
        f.write("epoch_ms,watts,minion_mhz,minion_mv\n")
        for t, w, mhz, mv in samples:
            f.write(f"{int(t)},{w},{mhz},{mv}\n")
    idle_w = statistics.median([w for t, w, *_ in samples if any(a <= t <= b for a, b in idle_windows)])
    results = {}
    for name, cli, what in configs:
        timed = [r for r in runs if r["config"] == name and r["launch"] >= 0]  # launch -1 is calibration
        if not timed:
            continue
        first = timed[0]["t_start_ms"] + args.settle * 1000
        inwin = [s for s in samples if s[0] >= first and any(r["t_start_ms"] <= s[0] <= r["t_end_ms"] for r in timed)]
        watts = [s[1] for s in inwin]
        mhz = [s[2] for s in inwin if s[2] is not None]
        mv = [s[3] for s in inwin if s[3] is not None]
        wall = sum(r["wall_s"] for r in timed)
        unit, amount = None, 0
        for r in timed:
            u, a = work(r)
            unit, amount = u, amount + a
        res = {"what": what, "args": cli, "launches": len(timed), "seconds": wall, "unit": unit, "amount": amount,
               "per_s": amount / wall if wall else 0, "power_samples": len(watts),
               "mean_w": statistics.mean(watts) if watts else None, "mean_mhz": statistics.mean(mhz) if mhz else None,
               "mhz_values": sorted(set(mhz)), "mean_minion_mv": statistics.mean(mv) if mv else None,
               "min_w": min(watts) if watts else None, "max_w": max(watts) if watts else None,
               "cycles_per_op": statistics.mean(r.get("cycles_per_op", 0) or 0 for r in timed),
               "cycles_per_layer": statistics.mean(r.get("cycles_per_layer_mean", 0) or 0 for r in timed),
               "nnz_a": timed[0].get("nnz_a"), "a_elems": timed[0].get("a_elems"),
               "row_mask": timed[0].get("row_mask", "0xffff")}
        results[name] = res
    spin_w = results.get("spin", {}).get("mean_w")
    for name, r in results.items():
        r["above_idle_w"] = r["mean_w"] - idle_w
        r["above_spin_w"] = r["mean_w"] - spin_w if spin_w is not None else None
        if r["per_s"]:
            r["j_per_unit"] = r["mean_w"] / r["per_s"]
            r["j_per_unit_above_idle"] = r["above_idle_w"] / r["per_s"]
            if r["unit"] == "tensorfma" and r["a_elems"]:
                # One TensorFMA32 has 16 x 16 x 16 multiply-add slots: each A element meets 16 B columns. The
                # useful ones have a nonzero A element in a row that tensor_mask leaves on (B is dense here).
                rows_on = bin(int(r["row_mask"], 16)).count("1") / 16.0
                useful = 16.0 * r["nnz_a"] * rows_on
                if useful:
                    r["pj_per_useful_fma_above_idle"] = r["j_per_unit_above_idle"] / useful * 1e12
                r["pj_per_fma_slot_above_idle"] = r["j_per_unit_above_idle"] / 4096 * 1e12

    summary = {"idle_w": idle_w, "info": info, "results": results}
    json.dump(summary, open(os.path.join(args.out, "results.json"), "w"), indent=2)

    print(f"\nidle {idle_w:.2f} W")
    for name, r in results.items():
        extra = ""
        if "pj_per_fma_slot_above_idle" in r:
            extra = (f"  {r['pj_per_fma_slot_above_idle']:.2f} pJ/FMA slot, "
                     f"{r.get('pj_per_useful_fma_above_idle', float('nan')):.2f} pJ/useful FMA (above idle)")
        elif r.get("j_per_unit_above_idle"):
            extra = f"  {r['j_per_unit_above_idle'] * 1e6:.3f} uJ/{r['unit']} above idle"
        print(f"{name:14s} {r['mean_w']:6.2f} W  +{r['above_idle_w']:5.2f}  {r['mean_mhz'] or 0:4.0f} MHz  "
              f"{r['per_s']:.4g} {r['unit']}/s{extra}")


if __name__ == "__main__":
    main()
