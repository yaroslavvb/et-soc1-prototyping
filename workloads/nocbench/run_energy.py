#!/usr/bin/env python3
"""Board power and energy per byte moved for nocbench's ring shifts. Runs on the lab machine:

    python3 workloads/nocbench/run_energy.py --host-bin build/nocbench/host/nocbench_host --out build/nocbench-energy

A background thread reads board power, the minion clock and the minion voltage from the service
processor about 4 times a second (dev_mngt_service through /dev/et0_mgmt, so quit et-powertop first).
Each configuration runs as its own `timeout 10 nocbench_host ... --seconds S` process, so no run holds
the shared card for more than 10 s. Power is averaged over each configuration's launch windows,
skipping the first --settle seconds. --only NAMES also sets the run order.

Every ring configuration keeps hart 0 of all 1024 minions busy sending and receiving, so they differ
only in how far each message travels: within a neighbourhood, across a shire, or over the mesh.
`spin` runs the same harts in an integer loop, a baseline for busy cores that move no data.
Energy per byte is (P - P_idle) / bandwidth. The card's idle power drifts with its temperature, so
besides the idle windows at the start and end, each configuration also gets a local idle: the median
of the samples in the gaps just before and after it.
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

# name, nocbench_host arguments, what moves
CONFIGS = [
    ("spin", ["--test", "spin"], "no messages: hart 0 of every minion in an integer loop"),
    ("pair", ["--test", "shift", "--rings", "pair", "--count", "32"],
     "1 KB messages between the two minions of each pair, inside a neighbourhood"),
    ("neigh", ["--test", "shift", "--rings", "neigh", "--count", "32"], "1 KB messages around rings of 8 (a neighbourhood)"),
    ("shire", ["--test", "shift", "--rings", "shire", "--count", "32"], "1 KB messages around rings of 32 (a shire)"),
    ("xshire1", ["--test", "shift", "--rings", "xshire:1", "--count", "32"],
     "1 KB messages from each minion to the same minion of the next shire ID"),
    ("xshire16", ["--test", "shift", "--rings", "xshire:16", "--count", "32"],
     "1 KB messages between shires s and s+16"),
    ("xshire8", ["--test", "shift", "--rings", "xshire:8", "--count", "32"],
     "1 KB messages around rings of 4 shires, 8 IDs apart"),
    ("xshire2", ["--test", "shift", "--rings", "xshire:2", "--count", "32"],
     "1 KB messages around rings of 16 shires, 2 IDs apart"),
    ("xshire4", ["--test", "shift", "--rings", "xshire:4", "--count", "32"],
     "1 KB messages around rings of 8 shires, 4 IDs apart"),
    ("xshire6", ["--test", "shift", "--rings", "xshire:6", "--count", "32"],
     "1 KB messages around rings of 16 shires, 6 IDs apart"),
    ("shire-c4", ["--test", "shift", "--rings", "shire", "--count", "4"], "128 B messages around rings of 32 (a shire)"),
    ("xshire1-c4", ["--test", "shift", "--rings", "xshire:1", "--count", "4"],
     "128 B messages from each minion to the same minion of the next shire ID"),
]


def dm_query(cmd):
    out = subprocess.run([DMS, "-m", cmd, "-n", "0", "-u", "5000"], capture_output=True, text=True)
    return [l.split("]: ", 1)[-1].strip() for l in (out.stdout + out.stderr).splitlines() if "verifyService" in l]


class PowerLogger(threading.Thread):
    def __init__(self, interval):
        super().__init__(daemon=True)
        self.interval, self.samples, self.stop = interval, [], threading.Event()

    def run(self):
        # The card runs a DVFS governor ("managed power", 65 W TDP) that moves the minion clock between
        # about 600 and 850 MHz, so every sample records the clock and minion voltage next to the power.
        def query(cmd, pattern):
            out = subprocess.run([DMS, "-m", cmd, "-n", "0", "-u", "2000"], capture_output=True, text=True)
            m = re.search(pattern, out.stdout + out.stderr)
            return float(m.group(1)) if m else None
        # Power every time; clock and voltage every fourth sample, so power is sampled about 3x as often.
        n, mhz, mv = 0, None, None
        while not self.stop.is_set():
            t = time.time() * 1000
            w = query("DM_CMD_GET_MODULE_POWER", r"Module Power Output: ([0-9.]+) W")
            if n % 4 == 0:
                mhz = query("DM_CMD_GET_ASIC_FREQUENCIES", r"Minion Shire: ([0-9]+) Mhz")
                mv = query("DM_CMD_GET_ASIC_VOLTAGE", r"Voltage MINION: ([0-9]+) mV")
            n += 1
            if w is not None:
                self.samples.append((t, w, mhz, mv))
            self.stop.wait(self.interval)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host-bin", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seconds", type=float, default=4.0, help="launch time per configuration (keep well under 10)")
    p.add_argument("--idle", type=float, default=6.0, help="idle baseline before and after the configurations")
    p.add_argument("--gap", type=float, default=5.0, help="idle time between configurations")
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
    runs, idle_windows, proc_windows = [], [], []
    try:
        t = time.time() * 1000
        time.sleep(args.idle)
        idle_windows.append((t + 1000, time.time() * 1000))
        for name, cli, _ in configs:
            cmd = ["timeout", "10", args.host_bin, *cli, "--seconds", str(args.seconds)]
            t_proc = time.time() * 1000
            proc = subprocess.run(cmd, capture_output=True, text=True)
            proc_windows.append((name, t_proc, time.time() * 1000))
            got = [json.loads(l.split(" ", 1)[1]) for l in proc.stdout.splitlines() if l.startswith("NOCBENCH ")]
            got = [r for r in got if r.get("kind") == "throughput"]
            if proc.returncode != 0 or not got or not all(r["ok"] for r in got):
                print(proc.stdout[-2000:], proc.stderr[-2000:])
                raise SystemExit(f"{name}: nocbench_host failed with exit {proc.returncode}")
            for r in got:
                r["config"] = name
            runs += got
            timed = [r for r in got if r["launch"] >= 0]
            gbps = sum(r["bytes"] for r in timed) / sum(r["wall_s"] for r in timed) / 1e9 if timed else 0
            print(f"{name}: {len(got)} launches, {gbps:.1f} GB/s", flush=True)
            time.sleep(args.gap)
        t = time.time() * 1000
        time.sleep(args.idle)
        idle_windows.append((t + 1000, time.time() * 1000))
    finally:
        logger.stop.set()
        logger.join()
    info["temp_after"] = dm_query("DM_CMD_GET_MODULE_CURRENT_TEMPERATURE")

    samples = logger.samples
    idle = [w for t, w, *_ in samples if any(a <= t <= b for a, b in idle_windows)]
    idle_w = statistics.median(idle)
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
        bytes_ = sum(r["bytes"] for r in timed)
        wall = sum(r["wall_s"] for r in timed)
        results[name] = {
            "what": what, "args": cli, "launches": len(timed), "seconds": wall, "bytes": bytes_,
            "gb_per_s": bytes_ / wall / 1e9 if bytes_ else 0.0,
            "gb_per_s_kernel": statistics.mean(r["gbps_kernel"] for r in timed),
            "ghz": statistics.mean(r["ghz"] for r in timed),
            "power_samples": len(watts), "mean_w": statistics.mean(watts) if watts else None,
            "mean_mhz": statistics.mean(mhz) if mhz else None, "mhz_values": sorted(set(mhz)),
            "mean_minion_mv": statistics.mean(mv) if mv else None,
            "min_w": min(watts) if watts else None, "max_w": max(watts) if watts else None,
        }
    # Local idle: samples in the gaps next to each configuration's process, skipping 1 s after a run ends.
    for i, (name, t0, t1) in enumerate(proc_windows):
        before_start = proc_windows[i - 1][2] + 1000 if i > 0 else t0 - (args.idle - 1) * 1000
        after_end = proc_windows[i + 1][1] if i + 1 < len(proc_windows) else t1 + args.idle * 1000
        gap = [w for t, w, *_ in samples if before_start <= t <= t0 or t1 + 1000 <= t <= after_end]
        if name in results and gap:
            results[name]["local_idle_w"] = statistics.median(gap)
            results[name]["local_idle_samples"] = len(gap)
    spin_w = results.get("spin", {}).get("mean_w")
    for name, r in results.items():
        r["above_idle_w"] = r["mean_w"] - idle_w if r["mean_w"] is not None else None
        r["pj_per_byte_vs_idle"] = r["above_idle_w"] / (r["gb_per_s"] * 1e9) * 1e12 if r["gb_per_s"] else None
        if r.get("local_idle_w") is not None:
            r["above_local_idle_w"] = r["mean_w"] - r["local_idle_w"]
            r["pj_per_byte_vs_local_idle"] = (r["above_local_idle_w"] / (r["gb_per_s"] * 1e9) * 1e12
                                              if r["gb_per_s"] else None)
        if spin_w is not None and r["gb_per_s"] and name != "spin":
            r["pj_per_byte_vs_spin"] = (r["mean_w"] - spin_w) / (r["gb_per_s"] * 1e9) * 1e12

    summary = {"idle_w": idle_w, "idle_samples": len(idle), "info": info, "results": results}
    json.dump(summary, open(os.path.join(args.out, "results.json"), "w"), indent=2)
    with open(os.path.join(args.out, "runs.jsonl"), "w") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(args.out, "power.csv"), "w") as f:
        f.write("epoch_ms,watts,minion_mhz,minion_mv\n")
        for t, w, mhz, mv in samples:
            f.write(f"{int(t)},{w},{mhz},{mv}\n")

    print(f"\nidle {idle_w:.2f} W (median of {len(idle)} samples)")
    print(f"{'config':11s} {'GB/s':>9s} {'MHz':>5s} {'W':>7s} {'+W':>6s} {'pJ/B':>8s} {'local':>7s} {'vs spin':>8s}  what")
    nan = float("nan")
    for name, r in results.items():
        pj = r["pj_per_byte_vs_idle"]
        pl = r.get("pj_per_byte_vs_local_idle")
        ps = r.get("pj_per_byte_vs_spin")
        print(f"{name:11s} {r['gb_per_s']:9.1f} {r['mean_mhz'] or 0:5.0f} {r['mean_w']:7.2f} {r['above_idle_w']:6.2f} "
              f"{pj if pj is not None else nan:8.2f} {pl if pl is not None else nan:7.2f} "
              f"{ps if ps is not None else nan:8.2f}  {r['what']}")


if __name__ == "__main__":
    main()
