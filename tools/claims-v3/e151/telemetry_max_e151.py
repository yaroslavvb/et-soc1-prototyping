#!/usr/bin/env python3
"""E151 (desk): the telemetry's extremes per block - board power, the current minion-shire reading (minshire[0], the field the die stop
reads), the latched high entry (minshire[2], reported only), the minion rail and its running-maximum field, the clock and the
statistics-reset counter - from the raw copy of E151's blocks (e151/, e151-smoke/, e151-stoptest/), to show the registered stops' margin.
Reported only; no rule reads it. Standard library only.

    python3 tools/claims-v3/e151/telemetry_max_e151.py <raw root>
SPDX-License-Identifier: Apache-2.0"""
import glob
import gzip
import json
import os
import sys


def main():
    raw = sys.argv[1]
    out = {}
    for d in sorted(glob.glob(os.path.join(raw, "e151*", "p151*"))):
        f = os.path.join(d, "telemetry.jsonl.gz")
        if not os.path.exists(f):
            continue
        rows = [json.loads(x) for x in gzip.open(f, "rt") if x.startswith("{")]
        if not rows:
            continue
        b = [r["board_w"] for r in rows if isinstance(r.get("board_w"), (int, float))]
        cur = [r["temp_c"]["minshire"][0] for r in rows]
        latch = [r["temp_c"]["minshire"][-1] for r in rows]
        rail = [r["sp"]["minion_w"][0] for r in rows]
        rmax = sorted({r["sp"]["minion_w"][2] for r in rows})
        mhz = sorted({r["mhz"]["minion"] for r in rows})
        out[os.path.basename(os.path.dirname(d)) + "/" + os.path.basename(d)] = {
            "samples": len(rows), "board_w_max": max(b), "board_w_min": min(b), "die_minshire0_c_min": min(cur),
            "die_minshire0_c_max": max(cur), "minshire_last_entry_c": sorted(set(latch)), "rail_w_min": min(rail), "rail_w_max": max(rail),
            "rail_running_max_field_w": rmax, "minion_mhz": mhz, "since_reset_ms": sorted({r.get("since_reset_ms") for r in rows})}
    allb = [v["board_w_max"] for v in out.values()]
    alld = [v["die_minshire0_c_max"] for v in out.values()]
    print(json.dumps({"blocks": out, "board_w_max": max(allb) if allb else None, "die_minshire0_c_max": max(alld) if alld else None},
                     indent=1))


if __name__ == "__main__":
    main()
