#!/usr/bin/env python3
"""Board power and energy per byte for the memhier bandwidth probes. Runs on the lab machine:

    python3 workloads/memhier/run_energy.py --host-bin build/memhier/host/memhier_host --out build/memhier-energy

A background thread reads board power, the minion clock and the minion voltage from the service
processor about 4 times a second (dev_mngt_service through /dev/et0_mgmt, so quit et-powertop first).
The card's DVFS governor changes the clock during runs, so every sample records it. --only NAMES
also sets the run order.
Each configuration runs as its own `timeout 10 memhier_host ... --seconds S` process, so no run holds
the shared card for more than 10 s. Power is averaged over each configuration's launch windows,
skipping the first --settle seconds. Energy per byte is (P - P_idle) / bandwidth. For L1 it is also
reported against the spin loop, (P_l1 - P_spin) / bandwidth, which removes the cost of a busy core.
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

# name, memhier_host arguments, what the working set is sized to hit
CONFIGS = [
    ("spin", ["--test", "spin"], "no data: busy cores only"),
    ("l1", ["--test", "l1"], "L1 hits: 256 B per hart, 2048 harts"),
    ("l2", ["--test", "stream", "--where", "dram", "--bytes-per-minion", "8K"], "256 KB per shire (L2 is 512 KB)"),
    ("l3", ["--test", "stream", "--where", "dram", "--bytes-per-minion", "24K"],
     "768 KB per shire > L2, 24 MB in total < 32 MB of L3"),
    ("dram", ["--test", "stream", "--where", "dram", "--bytes-per-minion", "256K"], "256 MB in total"),
    ("scp-local", ["--test", "stream", "--where", "scp-local", "--bytes-per-minion", "64K"],
     "2 MB of the shire's own L2 scratchpad"),
    ("scp-remote", ["--test", "stream", "--where", "scp-remote", "--bytes-per-minion", "64K", "--scp-shift", "16"],
     "2 MB of the scratchpad 16 shires away"),
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
        while not self.stop.is_set():
            t = time.time() * 1000
            w = query("DM_CMD_GET_MODULE_POWER", r"Module Power Output: ([0-9.]+) W")
            mhz = query("DM_CMD_GET_ASIC_FREQUENCIES", r"Minion Shire: ([0-9]+) Mhz")
            mv = query("DM_CMD_GET_ASIC_VOLTAGE", r"Voltage MINION: ([0-9]+) mV")
            if w is not None:
                self.samples.append((t, w, mhz, mv))
            self.stop.wait(self.interval)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host-bin", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seconds", type=float, default=4.0, help="launch time per configuration (keep well under 10)")
    p.add_argument("--idle", type=float, default=6.0, help="idle baseline before and after the configurations")
    p.add_argument("--gap", type=float, default=4.0, help="idle time between configurations")
    p.add_argument("--settle", type=float, default=0.7, help="seconds skipped at the start of each configuration")
    p.add_argument("--only", default="", help="comma-separated configuration names")
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    only = [n for n in args.only.split(",") if n]  # also the run order
    by_name = {c[0]: c for c in CONFIGS}
    configs = [by_name[n] for n in only] if only else CONFIGS

    info = {"freqs": dm_query("DM_CMD_GET_ASIC_FREQUENCIES"),
            "cache_config": dm_query("DM_CMD_GET_SHIRE_CACHE_CONFIG"),
            "temp_before": dm_query("DM_CMD_GET_MODULE_CURRENT_TEMPERATURE")}
    logger = PowerLogger(0.05)
    logger.start()
    runs, idle_windows = [], []
    try:
        t = time.time() * 1000
        time.sleep(args.idle)
        idle_windows.append((t + 1000, time.time() * 1000))
        for name, cli, _ in configs:
            cmd = ["timeout", "10", args.host_bin, *cli, "--seconds", str(args.seconds)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            got = [json.loads(l.split(" ", 1)[1]) for l in proc.stdout.splitlines() if l.startswith("MEMHIER ")]
            if proc.returncode != 0 or not got:
                print(proc.stdout[-2000:], proc.stderr[-2000:])
                raise SystemExit(f"{name}: memhier_host failed with exit {proc.returncode}")
            for r in got:
                r["config"] = name
            runs += got
            print(f"{name}: {len(got)} launches, {statistics.mean(r['gbps_wall'] for r in got if r['launch'] >= 0):.1f} GB/s",
                  flush=True)
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
    for name, _, what in configs:
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
            "what": what, "launches": len(timed), "seconds": wall, "bytes": bytes_,
            "gb_per_s": bytes_ / wall / 1e9 if bytes_ else 0.0,
            "bytes_per_cycle_per_hart": statistics.mean(r["bytes_per_cycle_per_hart"] for r in timed),
            "implied_ghz": statistics.mean(r["implied_ghz"] for r in timed),
            "power_samples": len(watts), "mean_w": statistics.mean(watts) if watts else None,
            "mean_mhz": statistics.mean(mhz) if mhz else None, "mhz_values": sorted(set(mhz)),
            "mean_minion_mv": statistics.mean(mv) if mv else None,
            "min_w": min(watts) if watts else None, "max_w": max(watts) if watts else None,
        }
    for name, r in results.items():
        r["above_idle_w"] = r["mean_w"] - idle_w if r["mean_w"] is not None else None
        r["pj_per_byte_vs_idle"] = r["above_idle_w"] / (r["gb_per_s"] * 1e9) * 1e12 if r["gb_per_s"] else None
        if name == "l1" and "spin" in results:
            r["pj_per_byte_vs_spin"] = (r["mean_w"] - results["spin"]["mean_w"]) / (r["gb_per_s"] * 1e9) * 1e12

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
    print(f"{'config':11s} {'GB/s':>9s} {'MHz':>5s} {'mV':>4s} {'W':>7s} {'+W':>6s} {'pJ/B':>8s}  working set")
    for name, r in results.items():
        pj = r["pj_per_byte_vs_idle"]
        extra = f"  ({r['pj_per_byte_vs_spin']:.2f} pJ/B above spin)" if "pj_per_byte_vs_spin" in r else ""
        print(f"{name:11s} {r['gb_per_s']:9.1f} {r['mean_mhz'] or 0:5.0f} {r['mean_minion_mv'] or 0:4.0f} {r['mean_w']:7.2f} "
              f"{r['above_idle_w']:6.2f} {pj if pj is not None else float('nan'):8.2f}  {r['what']}{extra}")


if __name__ == "__main__":
    main()
