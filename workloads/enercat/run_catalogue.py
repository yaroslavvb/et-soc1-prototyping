#!/usr/bin/env python3
"""The comprehensive instruction and memory energy catalogue: every configuration, three times, in a
different random order each pass, bracketed by idle, with telemetry throughout.

    python3 workloads/enercat/run_catalogue.py <out-dir> [--passes 3] [--burst 3] [--gap 5] [--only NAMES]

One line per launch in <out-dir>/runs.jsonl (with a "pass" and "cfg" field), telemetry in telemetry.jsonl.
Every host process holds the card for under 10 s. Scratchpad-read configurations are preceded by a short
untimed tensor-store burst that fills every shire's scratchpad with the operand pattern, so the bytes on the
wire are the zeros, the constant or the random data the configuration names.
"""
import argparse
import json
import os
import random
import socket
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(ROOT, "build", "enercat", "host", "enercat_host")
ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")

CONST_SUBSET = {"add", "fadd.s", "fmadd.s", "fadd.ps", "fmadd.ps", "fadd.pi", "fmul.pi", "fexp.ps", "ld", "flw.ps", "tload", "tstore"}


def configs():
    modes = json.load(open(os.path.join(ROOT, "workloads", "enercat", "enercat_modes.json")))
    cfgs = []
    # awake core
    cfgs.append({"cfg": "spin/zeros/h1", "args": ["--pattern", "spin", "--operands", "zeros", "--harts", "1"]})
    cfgs.append({"cfg": "spin/zeros/h2", "args": ["--pattern", "spin", "--operands", "zeros", "--harts", "2"]})
    # every generated instruction, zeros and random; a subset also on one constant
    for m in modes:
        for o in ("zeros", "random") + (("const",) if m["name"] in CONST_SUBSET else ()):
            cfgs.append({"cfg": f"{m['name']}/{o}/h2", "args": ["--pattern", m["name"], "--operands", o, "--harts", "2"]})
    # one-hart versions of a few, for the per-hart cost
    for n in ("fmadd.ps", "add", "fexp.ps"):
        cfgs.append({"cfg": f"{n}/random/h1", "args": ["--pattern", n, "--operands", "random", "--harts", "1"]})
    # bytes: the write and read paths, with the operand pattern in the slices
    for o in ("zeros", "random", "const"):
        cfgs.append({"cfg": f"tstore/dram/{o}", "args": ["--pattern", "tstore", "--operands", o, "--slice-bytes", "256K"]})
        cfgs.append({"cfg": f"tstore/scp/{o}", "args": ["--pattern", "tstore", "--operands", o, "--slice-bytes", "32K", "--scp"]})
        cfgs.append({"cfg": f"tload/dram/{o}", "args": ["--pattern", "tload", "--operands", o, "--slice-bytes", "256K"]})
        cfgs.append({"cfg": f"tload/scp/{o}", "args": ["--pattern", "tload", "--operands", o, "--slice-bytes", "32K", "--scp"], "prefill": o})
        cfgs.append({"cfg": f"st_stream/dram/{o}", "args": ["--pattern", "st_stream", "--operands", o, "--slice-bytes", "256K"]})
    # wires: 1 KB tensor loads from a scratchpad d hops away
    for o in ("zeros", "random"):
        for d in (1, 2, 3, 4, 5, 6, 8):
            cfgs.append({"cfg": f"wire/hop{d}/{o}", "prefill": o,
                         "args": ["--pattern", "tload_pat", "--operands", o, "--hop-distance", str(d), "--slice-bytes", "32K",
                                  "--stride", "1K", "--access-bytes", "1K", "--region", "32K"]})
        # scratchpad lines: 64 B loads at strides that cycle banks, alternate banks, or stay in one
        for st in ("64", "128", "256"):
            cfgs.append({"cfg": f"scpline/stride{st}/{o}", "prefill": o,
                         "args": ["--pattern", "tload_pat", "--operands", o, "--scp", "--slice-bytes", "32K",
                                  "--stride", st, "--access-bytes", "64", "--region", "32K"]})
        # L1 fills: 32 B loads through the L1 from the scratchpad, using all / half / a quarter of each line
        for st in ("32", "64", "128"):
            cfgs.append({"cfg": f"l1fill/stride{st}/{o}", "prefill": o,
                         "args": ["--pattern", "flw_pat", "--operands", o, "--scp", "--slice-bytes", "32K",
                                  "--stride", st, "--region", "16K"]})
        # DRAM rows: 1 KB loads next bank / same bank next column / same bank next row
        for st, reg in (("1K", "256K"), ("8K", "256K"), ("256K", "8M")):
            cfgs.append({"cfg": f"dramrow/stride{st}/{o}",
                         "args": ["--pattern", "tload_pat", "--operands", o, "--slice-bytes", reg,
                                  "--stride", st, "--access-bytes", "1K", "--region", reg]})
    # DRAM rows, done properly: 32 harts (minion 0 of every shire) with 64 MB each, so the touched set beats the
    # L3 even when each row visit is 1 KB. Sequential; same bank and row, next column; and a jump to the next
    # row after every 8 KB, so every bank sees a new row on every visit.
    for o in ("zeros", "random"):
        for name, st, je, jb in (("seq", "1K", "0", "0"), ("rowhit", "8K", "0", "0"), ("rowmiss", "1K", "8", "248K")):
            cfgs.append({"cfg": f"dramrow2/{name}/{o}",
                         "args": ["--pattern", "tload_pat", "--operands", o, "--shires", "0xffffffff", "--minions", "0x1",
                                  "--slice-bytes", "64M", "--region", "64M", "--stride", st, "--access-bytes", "1K",
                                  "--jump-every", je, "--jump-bytes", jb]})
    # neighbourhoods: which quarter of the shire reads its own scratchpad
    for k in range(4):
        cfgs.append({"cfg": f"neigh/{k}/random", "prefill": "random",
                     "args": ["--pattern", "tload", "--operands", "random", "--slice-bytes", "32K", "--scp",
                              "--minions", hex(0xFF << (8 * k))]})
    return cfgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--burst", type=float, default=3.0)
    ap.add_argument("--gap", type=float, default=5.0)
    ap.add_argument("--only", default="")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfgs = configs()
    if a.only:
        keep = a.only.split(",")
        cfgs = [c for c in cfgs if any(c["cfg"].startswith(k) for k in keep)]
    host = socket.gethostname()
    tel = open(os.path.join(a.out, "telemetry.jsonl"), "a")
    sampler = subprocess.Popen([os.path.join(ROOT, "build", "ettelem", "ettelem"), "sample", "--seconds",
                                str(int((len(cfgs) * a.passes * (a.burst + a.gap + 1.5)) + 120)), "--every-ms", "100"],
                               stdout=tel, stderr=subprocess.DEVNULL, env=ENV)
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    log = open(os.path.join(a.out, "run.log"), "a")
    print(f"{len(cfgs)} configurations x {a.passes} passes, about {len(cfgs)*a.passes*(a.burst+a.gap+1.2)/60:.0f} min", file=log, flush=True)
    time.sleep(10)
    try:
        for p in range(a.passes):
            order = list(range(len(cfgs)))
            random.Random(a.seed + p).shuffle(order)
            for i in order:
                c = cfgs[i]
                if c.get("prefill"):
                    subprocess.run(["timeout", "12", H, "--pattern", "tstore", "--operands", c["prefill"], "--slice-bytes", "32K",
                                    "--scp", "--seconds", "0.3", "--window", "60000000"], env=ENV, capture_output=True)
                time.sleep(a.gap)
                r = subprocess.run(["timeout", "12", H] + c["args"] + ["--seconds", str(a.burst), "--window", "240000000"],
                                   env=ENV, capture_output=True, text=True)
                n = 0
                for line in r.stdout.splitlines():
                    if line.startswith("ENERCAT {"):
                        runs.write(json.dumps({"host": host, "pass": p, "cfg": c["cfg"], **json.loads(line[8:])}) + "\n")
                        n += 1
                runs.flush()
                print(f"pass {p} {c['cfg']}: {n} launches", file=log, flush=True)
        time.sleep(a.gap + 3)
    finally:
        sampler.terminate()
    print("done", file=log, flush=True)


if __name__ == "__main__":
    main()
