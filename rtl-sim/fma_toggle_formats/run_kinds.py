#!/usr/bin/env python3
"""Replay the Q130(s) kinds tiles through the tensor multiply-add unit of each number format.

    run_kinds.py --kinds <tools/claims-v3/kinds> --out counts.json [--types fp32,fp16,int8] [--jobs 4]

For every kind it runs this directory's bench (obj_dir/Vtb) in that kind's own format, and - for fp32
only - a local build of rtl-sim/fma_toggle (its obj_dir/Vtb; obj_dir/ is gitignored, so it is built, not
committed) on the same tiles, as a cross-check of the new bench's fp32 path. The two agree on ungated kinds
and not on gated ones, and both fail a functional check (docs/reports/data/2026-10-31-q130-rtl-formats/
README.md section 0): until the bench passes one, every count it writes is PROVISIONAL.

A tile file is 2,048 bytes: the A tile then the B tile, 1,024 each, 16 lines of 64 bytes, one 32-bit
little-endian lane word per 4 bytes (tools/claims-v3/kinds/README.md section 2). The layout of a word is
the only thing that differs between formats, and the bench never looks inside a word, so one converter
serves all three.

Toggle authority: docs/reports/data/2026-10-26-toggle-recount/README.md. `nets` is the raw Verilator
toggle-coverage total. The recount's whole-unit factor (5.33 names per merged net) does NOT transfer to
this bench: settled VCD counts of its own runs give 4.62 (fp32 randn), 4.19 (fp16 randn) and 2.08 (int8
full), and 2.0-7.3 across kinds (that README, verification/hier-measured.json). Convert per format and kind.
"""
import argparse
import collections
import concurrent.futures
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "..", "fma_toggle", "obj_dir", "Vtb")
NEW = os.path.join(HERE, "obj_dir", "Vtb")


def write_hex(bin_path, hex_path):
    raw = open(bin_path, "rb").read()
    if len(raw) != 2048:
        raise SystemExit(f"{bin_path}: {len(raw)} bytes, expected 2048")
    words = struct.unpack("<512I", raw)
    with open(hex_path, "w") as f:
        for w in words:                      # A then B, row-major, 16 words a line
            f.write(f"{w:08x}\n")
        for _ in range(256):                 # the accumulators start at zero
            f.write("00000000\n")
    return hashlib.sha256(raw).hexdigest()


def parse_cov(path):
    """Verilator toggle coverage, by RTL source file, clocks and the bench's own files excluded."""
    by_block, clock = collections.Counter(), 0
    for line in open(path, errors="replace"):
        if not line.startswith("C '"):
            continue
        key, count = line.rsplit("' ", 1)
        fields = dict(kv.split("\x02", 1) for kv in key[3:].split("\x01") if "\x02" in kv)
        f = os.path.basename(fields.get("f", "?"))
        name = fields.get("o", "")
        if f in ("tb.sv", "tb_fmt.sv", "ff_acct.sv"):
            continue
        n = int(count)
        if re.search(r"clk|clock", name):
            clock += n
            continue
        by_block[f.replace(".v", "")] += n
    return by_block, clock


def run_one(binary, hexf, fmt, ops, warm, mul, gap, nogate, cov):
    cmd = [binary, f"+tiles={hexf}", f"+ops={ops}", f"+warm={warm}", f"+mul={mul}", f"+gap={gap}",
           f"+verilator+coverage+file+{cov}"]
    if binary == NEW:
        cmd.append(f"+fmt={fmt}")
    if nogate:
        cmd.append("+nogate=1")
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    acct = json.loads(next(l for l in out.splitlines() if l.startswith("ACCT"))[5:])
    cmat = {}
    for l in out.splitlines():
        if l.startswith("C "):
            _, i, j, v = l.split()
            cmat[f"{i},{j}"] = v
    by_block, clock = parse_cov(cov)
    n = acct["ops"]
    res = {k: v / n for k, v in acct.items() if isinstance(v, (int, float)) and k != "ops"}
    res["nets"] = sum(by_block.values()) / n
    res["clock_nets"] = clock / n
    res["by_block"] = {k: v / n for k, v in sorted(by_block.items(), key=lambda kv: -kv[1]) if v}
    res["ops"] = n
    return res, cmat


def job(args):
    typ, kind, path, a = args
    with tempfile.TemporaryDirectory() as d:
        hexf, cov = os.path.join(d, "t.hex"), os.path.join(d, "cov.dat")
        sha = write_hex(path, hexf)
        gap = 318 - 256 if typ == "int8" else 546 - 512
        new, cmat = run_one(NEW, hexf, typ, a.ops, 1, 1, gap, False, cov)
        row = {"type": typ, "kind": kind, "sha256": sha, "new_bench": new}
        if a.nogate:
            row["new_bench_nogate"] = run_one(NEW, hexf, typ, a.ops, 1, 1, gap, True, cov)[0]
        if typ == "fp32" and os.path.exists(OLD):
            row["old_bench"] = run_one(OLD, hexf, typ, a.ops, 1, 1, gap, False, cov)[0]
        if a.dump_c:
            row["C"] = cmat
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kinds", required=True, help="tools/claims-v3/kinds")
    p.add_argument("--out", required=True)
    p.add_argument("--types", default="fp32,fp16,int8")
    p.add_argument("--only", default="", help="comma-separated kind names, all of them if empty")
    p.add_argument("--ops", type=int, default=4)
    p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--nogate", action="store_true", help="also run each kind with the zero gate off")
    p.add_argument("--dump-c", action="store_true", help="keep the accumulator matrix (for the fp16 check)")
    a = p.parse_args()
    only = set(x for x in a.only.split(",") if x)
    jobs = []
    for typ in a.types.split(","):
        d = os.path.join(a.kinds, "tiles", typ)
        for f in sorted(os.listdir(d)):
            if f.endswith(".bin") and (not only or f[:-4] in only):
                jobs.append((typ, f[:-4], os.path.join(d, f), a))
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        rows = list(ex.map(job, jobs))
    res = {"_bench": "rtl-sim/fma_toggle_formats", "_ops_measured": a.ops, "rows": rows}
    json.dump(res, open(a.out, "w"), indent=1)
    for r in rows:
        n = r["new_bench"]
        print(f"{r['type']:5s} {r['kind']:18s} nets {n['nets']:10.0f}  ff_tog {n['ff_toggles']:9.0f}  "
              f"bus_ab {n['bus_ab']:8.0f}  slot_valid {n['slot_valid']:7.0f}  cyc {n['cycles']:6.0f}"
              + (f"  [old nets {r['old_bench']['nets']:10.0f}]" if "old_bench" in r else ""))


if __name__ == "__main__":
    main()
