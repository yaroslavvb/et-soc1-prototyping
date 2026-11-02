#!/usr/bin/env python3
"""E128 device-command audit, step 1 (desk, read-only git reads): the numeric ID of every DM command the run sends, in
every revision of the public device-api header, so the host's IDs can be checked against the firmware's.

    python3 enum_check.py <et-platform clone> [box header file ...]
"""
import re
import subprocess
import sys

REPO = sys.argv[1]
BOXES = sys.argv[2:]
PATH = "device-api/include/management-api/device_mgmt_api_spec.h"
SENT = ["DM_CMD_GET_MODULE_STATIC_TDP_LEVEL", "DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS", "DM_CMD_GET_MODULE_POWER_STATE",
        "DM_CMD_GET_ASIC_FREQUENCIES", "DM_CMD_GET_ASIC_VOLTAGE", "DM_CMD_GET_MODULE_POWER", "DM_CMD_GET_SP_STATS",
        "DM_CMD_GET_MODULE_CURRENT_TEMPERATURE", "DM_CMD_GET_MODULE_VOLTAGE"]
WATCH = SENT + ["DM_CMD_SET_STATS_RUN_CONTROL", "DM_CMD_GET_MODULE_FIRMWARE_REVISIONS", "DM_CMD_SET_MODULE_STATIC_TDP_LEVEL",
                "DM_CMD_SET_MODULE_TEMPERATURE_THRESHOLDS", "DM_CMD_GET_MODULE_RESIDENCY_POWER_STATES", "DM_CMD_SET_DM_TRACE_CONFIG"]


def ids(text):
    out = {}
    for m in re.finditer(r"^\s*(DM_CMD_[A-Z0-9_]+)\s*=\s*(\d+)\s*,", text, re.M):
        out[m.group(1)] = int(m.group(2))
    return out


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), check=True, capture_output=True, text=True).stdout


revs = git("log", "--format=%h %cs", "--", PATH).split("\n")
revs = [r.split() for r in revs if r.strip()]
table = {}
for h, d in revs:
    table[(h, d)] = ids(git("show", f"{h}:{PATH}"))
print(f"revisions of {PATH}: {len(revs)}")
base = table[tuple(revs[0])]
for name in WATCH:
    vals = sorted({t.get(name) for t in table.values()}, key=lambda v: -1 if v is None else v)
    print(f"  {name:45s} ids across all revisions: {vals}")
for b in BOXES:
    t = ids(open(b).read())
    diff = {n: (t.get(n), base.get(n)) for n in WATCH if t.get(n) != base.get(n)}
    print(f"box header {b}: {len(t)} DM_CMD ids; differs from HEAD on the watched names: {diff if diff else 'none'}")
    full = {n for n in set(t) | set(base) if t.get(n) != base.get(n)}
    print(f"  ...on any DM_CMD name: {sorted(full) if full else 'none'}")
