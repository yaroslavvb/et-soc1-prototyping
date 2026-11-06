#!/usr/bin/env python3
"""Toggle-coverage difference of two bench runs, by net (bits and directions summed): where a one-number kind's extra
switching sits.   python3 cdiff_e180.py <a.cov> <b.cov> [--top 40]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import re


def load(path):
    d = collections.Counter()
    for line in open(path, errors="replace"):
        if not line.startswith("C '"):
            continue
        key, count = line.rsplit("' ", 1)
        f = dict(kv.split("\x02", 1) for kv in key[3:].split("\x01") if "\x02" in kv)
        if f.get("t") != "toggle":
            continue
        o = re.sub(r"\[\d+\]", "", f.get("o", "")).split(":")[0]
        h = re.sub(r"VPU_LANES\[\d+\]", "VPU_LANES[*]", f.get("h", ""))
        d[(h, o)] += int(count)
    return d


ap = argparse.ArgumentParser()
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--top", type=int, default=40)
x = ap.parse_args()
A, B = load(x.a), load(x.b)
diff = collections.Counter({k: B[k] - A[k] for k in set(A) | set(B) if B[k] != A[k]})
print("total b - a:", sum(diff.values()))
for (h, o), v in sorted(diff.items(), key=lambda kv: -abs(kv[1]))[:x.top]:
    print(f"{v:+10d}  {h}  {o}")
