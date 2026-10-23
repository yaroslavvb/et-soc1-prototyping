#!/usr/bin/env python3
"""E63: compare tile_check.sh's dumped tiles with what the protocol meant to run.

    python3 tile_compare.py <tree root> <tile_check outdir>

lq_h23, lq_h0, lq_h8: the dump must equal build/hl-gen2/tiles/<name>.bin byte for byte. ones, pi: every one
of the 512 floats (A then B) must be 1.0 / pi (float32). Prints one line each and the launch's own record
(the SPARSITY { json line: cycles per op, lanes valid); exits 1 on any mismatch.
"""
import json
import os
import struct
import sys

root, out = sys.argv[1], sys.argv[2]
bad = 0
for name in ("lq_h23", "lq_h0", "lq_h8", "ones", "pi"):
    dump = os.path.join(out, name + ".dump")
    if not os.path.isfile(dump) or os.path.getsize(dump) != 2048:
        print(f"{name}: no 2,048-byte dump")
        bad += 1
        continue
    got = open(dump, "rb").read()
    if name.startswith("lq_"):
        want = open(os.path.join(root, "build/hl-gen2/tiles", name + ".bin"), "rb").read()
        ok = got == want
        why = "byte for byte" if ok else f"{sum(a != b for a, b in zip(got, want))} bytes differ"
    else:
        vals = struct.unpack("<512f", got)
        ref = struct.unpack("<f", struct.pack("<f", 1.0 if name == "ones" else 3.14159274))[0]
        ok = all(v == ref for v in vals)
        why = f"all {ref!r}" if ok else f"{sum(v != ref for v in vals)} of 512 floats differ"
    rec = ""
    try:
        for line in open(os.path.join(out, name + ".out")):
            if line.startswith("SPARSITY {"):
                r = json.loads(line[len("SPARSITY "):])
                rec = " | " + ", ".join(f"{k} {r[k]}" for k in ("cycles_per_op", "lane_valid", "harts", "mhz")
                                         if k in r)
                break
    except OSError:
        pass
    print(f"{name}: {'OK' if ok else 'MISMATCH'} ({why}){rec}")
    bad += 0 if ok else 1
sys.exit(1 if bad else 0)
