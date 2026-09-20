#!/usr/bin/env python3
"""Energy per memory access, per level and DRAM pattern, on a lab card.

For each pattern, hart 0 of all 1,024 minions runs memprobe_host --loop for --seconds, with idle gaps in
between. Board power is logged the whole time (scripts/et-power-log.sh, as fast as the service processor
answers). At the end the service processor's stats trace (per-rail minion / SRAM / NoC power, one record per
~133 ms loop pass) is extracted. Every card launch is its own `timeout 10` process.

    run_power.py --host-bin build/memprobe/host/memprobe_host --tables build/memprobe-data --out build/memprobe-power

Quit et-powertop first: the power logger and the trace extract need /dev/et0_mgmt, which allows one opener.
"""
import argparse
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DMS = "/opt/et/bin/dev_mngt_service"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_ops import STRIDED  # noqa: E402

PATTERNS = ["l1", "l2", "l3near", "l3far", "dram_seq", "dram_row"]


def card_busy():
    out = subprocess.run(["lsmod"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        f = line.split()
        if f and f[0] == "et_soc1":
            return int(f[2]) > 0
    return False


def extract_trace(out):
    """Copy out the service processor's stats trace (per-rail power, one record per ~133 ms). It is a 1 MB
    ring (~15 min), and an extract returns only the records since the last wrap, so extract often; the
    analysis merges the files. The extract does not reset the stats."""
    d = os.path.join(out, "trace")
    os.makedirs(d, exist_ok=True)
    subprocess.run(["timeout", "10", DMS, "-n", "0", "-t", "SPST:extract"], cwd=d, capture_output=True)
    for f in os.listdir(d):
        if f.startswith("dev0_sp_stats") and not f.endswith(".done"):
            os.rename(os.path.join(d, f), os.path.join(d, f"{time.time():.3f}-{f}.bin.done"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host-bin", required=True)
    ap.add_argument("--tables", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--gap", type=float, default=2.5)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--patterns", default=",".join(PATTERNS))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    wanted = args.patterns.split(",")
    if card_busy():
        sys.exit("the card has open handles; someone else is using it")

    logger = subprocess.Popen(["bash", os.path.join(REPO, "scripts/et-power-log.sh"), "0", "0"],
                              stdout=open(os.path.join(args.out, "power.csv"), "w"), stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    extract_trace(args.out)
    runs = open(os.path.join(args.out, "runs.jsonl"), "w")
    try:
        time.sleep(args.gap + 1)
        for rep in range(args.reps):
            for pat in PATTERNS:
                if pat not in wanted:
                    continue
                level, stride, lines = STRIDED[pat]
                cmd = ["timeout", "10", args.host_bin, "--loop", "--table", os.path.join(args.tables, pat + ".tbl"),
                       "--level", str(level), "--stride", str(stride), "--lines", str(lines),
                       "--seconds", str(args.seconds), "--budget", "8"]
                r = subprocess.run(cmd, capture_output=True, text=True)
                for line in r.stdout.splitlines():
                    if line.startswith("MEMPROBE "):
                        rec = json.loads(line[len("MEMPROBE "):])
                        rec["pattern"], rec["rep"] = pat, rep
                        runs.write(json.dumps(rec) + "\n")
                runs.flush()
                if r.returncode:
                    print(f"{pat}: exit {r.returncode}\n{r.stderr[-2000:]}", file=sys.stderr)
                    return 1
                print(f"{pat} rep {rep}: ok", flush=True)
                time.sleep(args.gap)
                extract_trace(args.out)
    finally:
        logger.terminate()
        logger.wait()
        runs.close()
    time.sleep(1)  # let the logger's last query release the management node
    extract_trace(args.out)
    print("done:", os.listdir(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
