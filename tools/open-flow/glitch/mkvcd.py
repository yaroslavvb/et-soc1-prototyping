#!/usr/bin/env python3
"""One E130 tile through one Q133(a) bench binary at one launch point, as run_kinds.py's VCD run does it
(accum.c's C at n0, one warm op, one dumped op). Writes <out>.vcd. Q138(g)."""
import os, struct, subprocess, sys, tempfile
binp, accum, tile, n0, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
warm, ops = 1, 1
d = tempfile.mkdtemp(dir=os.path.dirname(out))
pts = [n0, n0 + warm + ops]
subprocess.run([accum, "int8", os.path.abspath(tile)] + [str(p) for p in pts], check=True, cwd=d)
c0 = open(os.path.join(d, f"accum_{n0}.bin"), "rb").read()
words = struct.unpack("<512I", open(tile, "rb").read()) + struct.unpack("<256I", c0)
hexf = os.path.join(d, "t.hex")
open(hexf, "w").write("\n".join(f"{w:08x}" for w in words) + "\n")
base = [binp, f"+tiles={hexf}", "+fmt=int8", f"+warm={warm}", "+first=0", "+loadc=1"]
cov = os.path.join(d, "cov.dat")
r = subprocess.run(base + ["+ops=1", f"+dump={out}", "+dump_ops=1", f"+verilator+coverage+file+{cov}"], capture_output=True, text=True, check=True)
for f in os.listdir(d):
    os.remove(os.path.join(d, f))
os.rmdir(d)
print("ok", out, os.path.getsize(out))
