#!/usr/bin/env python3
"""Shrinks an ettelem sample log to the fields the Horace analyses read, gzipped, for keeping in the repo.

    compact_telemetry.py telemetry.jsonl out.jsonl.gz
"""
import gzip
import json
import sys

src, dst = sys.argv[1:3]
n = 0
with gzip.open(dst, "wt", compresslevel=9) as out:
    for line in open(src):
        try:
            s = json.loads(line)
        except Exception:
            continue  # the last line is cut when the sampler is killed
        out.write(json.dumps({
            "t_ms": s["t_ms"], "board_w": s["board_w"],
            "sp": {k: [s["sp"][k][0]] for k in ("minion_w", "sram_w", "noc_w")},
            "temp_c": {"pmic": s["temp_c"]["pmic"], "ioshire": [s["temp_c"]["ioshire"][0]], "minshire": [s["temp_c"]["minshire"][0]]},
            "die_mv": {"minion": s["die_mv"]["minion"]}, "mhz": {"minion": s["mhz"]["minion"]},
        }, separators=(",", ":")) + "\n")
        n += 1
print(n, "samples ->", dst)
