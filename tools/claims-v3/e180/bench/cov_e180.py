#!/usr/bin/env python3
"""Sum a Verilator toggle-coverage file by hierarchy: E180's all-nets count (every toggle point's count, clocks apart).

    python3 cov_e180.py <coverage.dat>     -> JSON {"vpu": n, "vpu_lanes": n, "txfma": n, "core": n, "clock": n, "points": n}

A toggle point is one bit of one net in one direction (0->1 or 1->0), so a count is that bit's transitions in that
direction over the window (the bench zeroes the coverage at the window's start, rtl-sim/fma_toggle_v2/acct.cpp). Nets
whose name holds clk/clock are summed apart, as rtl-sim/fma_toggle_v2/run_kinds.py parse_cov does.
SPDX-License-Identifier: Apache-2.0
"""
import json
import re
import sys


def parse(path):
    tot = {"vpu": 0, "vpu_lanes": 0, "txfma": 0, "vpu_rf_byp": 0, "core": 0, "frontend": 0, "intpipe": 0, "dcache": 0,
           "clock": 0, "points": 0, "other": 0}
    for line in open(path, errors="replace"):
        if not line.startswith("C '"):
            continue
        key, count = line.rsplit("' ", 1)
        fields = dict(kv.split("\x02", 1) for kv in key[3:].split("\x01") if "\x02" in kv)
        if fields.get("t") != "toggle":
            continue
        n = int(count)
        tot["points"] += 1
        h, o = fields.get("h", ""), fields.get("o", "")
        if re.search(r"clk|clock", o):
            tot["clock"] += n
            continue
        if h.startswith("tb.dut.vpu"):
            tot["vpu"] += n
            if ".VPU_LANES" in h:
                tot["vpu_lanes"] += n
            if "txfma" in h:
                tot["txfma"] += n
            if ".rf" in h or ".bypass" in h:
                tot["vpu_rf_byp"] += n
        elif h.startswith("tb.dut.core"):
            tot["core"] += n
            if ".frontend" in h:
                tot["frontend"] += n
            elif ".intpipe" in h:
                tot["intpipe"] += n
            elif ".dcache" in h:
                tot["dcache"] += n
        else:
            tot["other"] += n
    return tot


if __name__ == "__main__":
    print(json.dumps(parse(sys.argv[1])))
