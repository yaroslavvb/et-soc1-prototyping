#!/usr/bin/env python3
"""From a VCD of one TensorFMA op on zeros: every one-bit signal whose name says clock or enable or read enable, its rising edges in the op, per instance, with lane and unit numbers merged. Standard library only."""
import collections, json, re, sys
vcd, out = sys.argv[1], sys.argv[2]
want = re.compile(r"(clk|clock|_en\b|_en_|ren|wen|rd_en|wr_en|enable)", re.I)
names = {}
scope = []
ids = {}
with open(vcd, errors="replace") as f:
    for line in f:
        s = line.split()
        if not s:
            continue
        if s[0] == "$scope":
            scope.append(s[2])
        elif s[0] == "$upscope":
            scope.pop()
        elif s[0] == "$var":
            width, code, name = int(s[2]), s[3], s[4]
            if width == 1 and want.search(name):
                p = ".".join(scope + [name])
                if ".dut." in p or ".dut" in p:
                    ids.setdefault(code, []).append(p)
        elif s[0] == "$enddefinitions":
            break
    rises = collections.Counter()
    last = {}
    t = 0
    for line in f:
        if not line:
            continue
        c = line[0]
        if c == "#":
            t += 1
            continue
        if c in "01xz" and len(line) > 1:
            code = line[1:].strip()
            if code in ids:
                if c == "1" and last.get(code) != "1":
                    rises[code] += 1
                last[code] = c
agg = collections.defaultdict(list)
for code, paths in ids.items():
    for p in paths:
        q = p.split(".dut.", 1)[-1]
        q = re.sub(r"\[\d+\]", "", q)
        q = re.sub(r"\bVPU_LANES\.?", "", q)
        agg[q].append(rises.get(code, 0))
res = {k: {"instances": len(v), "rises_mean": sum(v) / len(v), "rises_max": max(v)} for k, v in sorted(agg.items())}
json.dump(res, open(out, "w"), indent=0)
print(len(res), "signals")
