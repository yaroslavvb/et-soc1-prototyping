#!/usr/bin/env python3
"""Count toggles per net in a VCD, between two times, grouped by the block each net is in.

    vcd_toggles.py <dump.vcd> --from <t> --to <t> --out toggles.json

A glitch is an extra transition inside a cycle, so the whole point is to count every edge, not
to sample. Multi-bit nets count a toggle per bit that changed.
"""
import argparse
import json
import re
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vcd")
    ap.add_argument("--from", dest="t0", type=int, default=0)
    ap.add_argument("--to", dest="t1", type=int, default=10 ** 18)
    ap.add_argument("--strip", default="tbt/dut")
    ap.add_argument("--block-depth", type=int, default=3)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    ids, scope = {}, []
    last, tog = {}, defaultdict(int)
    t = 0
    var = re.compile(r"^\$var\s+\S+\s+(\d+)\s+(\S+)\s+(.+?)\s*\$end")
    with open(a.vcd, errors="replace") as fh:
        indefs = True
        for line in fh:
            s = line.strip()
            if indefs:
                if s.startswith("$scope"):
                    scope.append(s.split()[2])
                    continue
                if s.startswith("$upscope"):
                    if scope:
                        scope.pop()
                    continue
                m = var.match(s)
                if m:
                    w, sid, nm = int(m.group(1)), m.group(2), m.group(3)
                    nm = nm.split()[0]
                    full = "/".join(scope + [nm])
                    if a.strip and full.startswith(a.strip + "/"):
                        full = full[len(a.strip) + 1:]
                    ids.setdefault(sid, (full, w))
                    continue
                if s.startswith("$enddefinitions"):
                    indefs = False
                    continue
                continue
            if not s:
                continue
            if s[0] == "#":
                try:
                    t = int(s[1:])
                except ValueError:
                    pass
                continue
            if s[0] in "bB":
                parts = s.split()
                if len(parts) < 2:
                    continue
                val, sid = parts[0][1:], parts[1]
            elif s[0] in "rR" or s[0] == "$":
                continue
            else:
                val, sid = s[0], s[1:]
            if sid not in ids:
                continue
            prev = last.get(sid)
            last[sid] = val
            if prev is None or not (a.t0 <= t <= a.t1):
                continue
            w = ids[sid][1]
            if w == 1:
                if prev != val and prev in "01" and val in "01":
                    tog[sid] += 1
            else:
                p = prev.rjust(w, prev[0] if prev[0] in "xzXZ" else "0")
                v = val.rjust(w, val[0] if val[0] in "xzXZ" else "0")
                n = sum(1 for x, y in zip(p[-w:], v[-w:])
                        if x != y and x in "01" and y in "01")
                tog[sid] += n

    by_net, by_block = {}, defaultdict(int)
    total = 0
    for sid, n in tog.items():
        nm = ids[sid][0]
        by_net[nm] = by_net.get(nm, 0) + n
        total += n
        p = nm.split("/")
        by_block["/".join(p[:a.block_depth]) if len(p) > a.block_depth else
                 ("/".join(p[:-1]) or "(top)")] += n
    out = {"vcd": a.vcd, "window": [a.t0, a.t1], "total_toggles": total,
           "nets": len(by_net),
           "blocks": dict(sorted(by_block.items(), key=lambda kv: -kv[1])),
           "top_nets": dict(sorted(by_net.items(), key=lambda kv: -kv[1])[:200])}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("total_toggles", "nets")}, indent=1))
    for b, n in list(out["blocks"].items())[:10]:
        print(f"  {b:52s} {n}")


if __name__ == "__main__":
    main()
