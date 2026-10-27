#!/usr/bin/env python3
"""Strip ngspice's progress chatter from a run log, as Q126(d)'s committed logs
are stripped: the 'Reference value :' lines and the per-node initial-solution
dumps carry no information and are most of the bytes."""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
out = []
drop = re.compile(r'Reference value\s*:|^\s*$')
with open(src, errors="replace") as fh:
    for line in fh:
        line = re.sub(r'(Reference value\s*:\s*[-+0-9.eE]+\s*)+', '', line)
        if line.strip() == "":
            continue
        out.append(line.rstrip() + "\n")
open(dst, "w").writelines(out)
print(f"{src}: {sum(1 for _ in open(src, errors='replace'))} lines -> {len(out)}")
