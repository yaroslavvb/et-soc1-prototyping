#!/usr/bin/env python3
"""E145 (desk): the telemetry's extremes per block - board power, the hottest minion-shire reading, the shires' mean, the minion rail and
the clock - from the raw copy of E145's blocks (kinds/, kinds-smoke/, kinds-stoptest/), to show the registered stops' margin. Reported
only; no rule reads it. Standard library only.

    python3 tools/claims-v3/e145/telemetry_max_e145.py <raw root>
SPDX-License-Identifier: Apache-2.0"""
import glob
import gzip
import json
import os
import sys


def main():
    raw = sys.argv[1]
    out = {}
    for d in sorted(glob.glob(os.path.join(raw, "kinds*", "p145*"))):
        f = os.path.join(d, "telemetry.jsonl.gz")
        if not os.path.exists(f):
            continue
        rows = [json.loads(x) for x in gzip.open(f, "rt") if x.startswith("{")]
        if not rows:
            continue
        b = [r["board_w"] for r in rows if isinstance(r.get("board_w"), (int, float))]
        hot = [max(r["temp_c"]["minshire"]) for r in rows]
        mean = [r["temp_c"]["minshire"][0] for r in rows]
        rail = [r["sp"]["minion_w"][0] for r in rows]
        mhz = sorted({r["mhz"]["minion"] for r in rows})
        out[os.path.basename(os.path.dirname(d)) + "/" + os.path.basename(d)] = {
            "samples": len(rows), "board_w_max": max(b), "board_w_min": min(b), "hottest_shire_c_max": max(hot),
            "shire_mean_c_min": min(mean), "shire_mean_c_max": max(mean), "rail_w_min": min(rail), "rail_w_max": max(rail),
            "minion_mhz": mhz, "since_reset_ms": sorted({r.get("since_reset_ms") for r in rows})}
    allb = [v["board_w_max"] for v in out.values()]
    allh = [v["hottest_shire_c_max"] for v in out.values()]
    print(json.dumps({"blocks": out, "board_w_max": max(allb) if allb else None, "hottest_shire_c_max": max(allh) if allh else None},
                     indent=1))


if __name__ == "__main__":
    main()
