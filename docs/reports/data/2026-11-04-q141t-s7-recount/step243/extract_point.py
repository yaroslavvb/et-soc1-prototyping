#!/usr/bin/env python3
"""Q141(t2): write a counts file, in run_kinds.py's own form, holding one point of one tile taken from a chunk's counts, so that
compare_points.py can set that point beside another build's count of it (README, check D243).

    python3 -B extract_point.py <chunk counts.json> <tile> <n0> <out.json>
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import json
import sys

sys.dont_write_bytecode = True
src, tile, n0, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
d = json.load(open(src))
row = d["rows"][tile]
pts = [p for p in row["points"] if p["n0"] == n0]
if len(pts) != 1:
    raise SystemExit(f"{tile} n0={n0}: {len(pts)} points in {src}")
r = dict(row)
r["points"] = pts
r.pop("mean", None)
json.dump({"_note": f"one point of {tile} (n0 {n0}) taken from {src.rsplit('/', 1)[-1]}", "rows": {tile: r}}, open(out, "w"), indent=1)
print(f"wrote {out.rsplit('/', 1)[-1]}: {tile} n0={n0}")
