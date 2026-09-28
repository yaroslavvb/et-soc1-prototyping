#!/usr/bin/env python3
"""Check the firmware's NoC-spec shire map, with the boot-time renaming applied, against the measured map.

    python3 docs/reports/data/2026-09-27-chip-diagram/research/firmware_map.py   # writes firmware_map.json beside it

Fact L37 (build_layout_facts.py) compared the comment "default Shire Virtual ID Map, based on the NOC spec"
(noc_reconfigure.h:76-82) with the measured logical map and found that only 111 of 496 pair distances agree. But the
IDs a kernel sees are not those default IDs: at boot the service processor's BL2 calls NOC_Remap_Shires()
(ServiceProcessorBL2/common/main.c:284, skipped only in FAST_BOOT or TEST_FRAMEWORK builds), which gives every shire
new_shire_virtual_id[g_displace][id] as its new ID (driver/noc_configuration.c:418-429); with the default fuse mask
(no shire displaced) g_displace stays SPARE_SHIRE_BIT_POSITION = 33 (noc_configuration.c:36, 380-387) and the table
used is the last one, "No displacement" (noc_reconfigure.h:398-406). The same ID goes into each shire's shire_config
ESR (minion_configuration.c:183-187, CONFIG_SHIRE_NEIGH with swap). This script applies that renaming to the comment's
map and compares the result with the measured map (workloads/nocbench/analyze.py MARTY, which fits all 496 pair
round trips on three cards). It also reads which of the four non-compute cells the firmware map puts where, and the
rows of the memory shires (mc0-mc7 in the comment) against the DRAM-latency fit (memprobe summary.json decomp.ms_pos).

Inputs are read from the files; nothing is typed in by hand except the line numbers cited above.
"""
import importlib.util
import itertools
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
ET = "/home/yaroslavvb/claude/et-soc1-prototyping/external"  # read-only; cited as external/...
NR = "et-platform/device-bootloaders/src/ServiceProcessorBL2/include/noc_reconfigure.h"
MAIN = "et-platform/device-bootloaders/src/ServiceProcessorBL2/common/main.c"

spec = importlib.util.spec_from_file_location("nocan", os.path.join(REPO, "workloads/nocbench/analyze.py"))
nocan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nocan)
MARTY, EMPTY = nocan.MARTY, nocan.EMPTY
SUMM = json.load(open(os.path.join(REPO, "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json")))
MS_POS = {int(k): tuple(v) for k, v in SUMM["decomp"]["ms_pos"].items()}

src = open(os.path.join(ET, NR)).read()
lines = src.split("\n")


def comment_grid(first_line):
    """The six rows under a '// This is the default ... Map' comment: [(west label, [six cells], east label)]."""
    rows = []
    for ln in lines[first_line:first_line + 6]:
        toks = ln.lstrip("/").split()
        west = toks[0] if toks and toks[0].startswith("mc") else None
        east = toks[-1] if toks and toks[-1].startswith("mc") else None
        cells = [t for t in toks if not t.startswith("mc")]
        assert len(cells) == 6, ln
        rows.append((west, cells, east))
    return rows


i_vid = next(i for i, ln in enumerate(lines) if "default Shire Virtual ID Map, based on the NOC spec" in ln)
i_bid = next(i for i, ln in enumerate(lines) if "default Shire Bridge ID Map, based on the NOC spec" in ln)
VID = comment_grid(i_vid + 1)
BID = comment_grid(i_bid + 1)
cell = {}  # default virtual ID -> (row, col) of the 6 x 6 compute area
for r, (_, cells, _) in enumerate(VID):
    for c, v in enumerate(cells):
        cell[int(v)] = (r, c)
# the tables of new_shire_virtual_id, in file order; the last is commented "No displacement"
body = src[src.index("new_shire_virtual_id[NUM_SHIRES][NUM_SHIRES]"):]
body = body[body.index("{") + 1:]
tables = [[int(x) for x in re.findall(r"\d+", b)] for b in re.findall(r"\{([^{}]*)\}", body)]
tables = [t for t in tables if len(t) == 34]
assert len(tables) == 34
i_nodisp = next(i for i, ln in enumerate(lines) if "// No displacement" in ln)
t = tables[33]
assert sorted(t) == list(range(34))
REMAP = {old: t[old] for old in range(34)}  # default virtual ID -> the ID after NOC_Remap_Shires
pos = {REMAP[old]: cell[old] for old in range(34)}  # kernel-visible shire ID -> (row, col)
dist = lambda p, q: abs(p[0] - q[0]) + abs(p[1] - q[1])
pairs = list(itertools.combinations(range(32), 2))


def sym(k):
    sw, f0, f1 = k
    def g(p):
        a, b = p
        if sw:
            a, b = b, a
        return (5 - a if f0 else a, 5 - b if f1 else b)
    return g


syms = []
for k in itertools.product((False, True), repeat=3):
    g = sym(k)
    syms.append({"swap_axes": k[0], "flip_first": k[1], "flip_second": k[2],
                 "shires_at_same_cell": sum(1 for s, p in MARTY.items() if g(p) == pos[s])})
best = max(syms, key=lambda s: s["shires_at_same_cell"])
g = sym((best["swap_axes"], best["flip_first"], best["flip_second"]))
grid = [[None] * 6 for _ in range(6)]
for s, (r, c) in pos.items():
    grid[r][c] = s
grey = {}
for e in EMPTY:
    r, c = g(e)
    grey[str(tuple(e))] = {"firmware_cell_row_col": [r, c], "virtual_map_entry": VID[r][1][c], "bridge_map_entry": BID[r][1][c],
                           "kernel_shire_id": grid[r][c]}
# memory shires: the comment's west label on row r is mc(r-1) at logical (r, -1), the east label at (r, 6)
ms_fw = {}
for r, (w, _, e) in enumerate(VID):
    for lab, y in ((w, -1), (e, 6)):
        if lab:
            ms_fw[int(lab[2:])] = (r, y)
out = {
    "about": __doc__.strip().split("\n")[0],
    "sources": {
        "virtual_id_map_comment": f"external/{NR}:{i_vid + 1}-{i_vid + 7}",
        "bridge_id_map_comment": f"external/{NR}:{i_bid + 1}-{i_bid + 7}",
        "no_displacement_table": f"external/{NR}:{i_nodisp + 1}-{i_nodisp + 8}",
        "remap_call": f"external/{MAIN}:275-286 (Set_Displace_Shire_Id, then NOC_Remap_Shires unless FAST_BOOT or TEST_FRAMEWORK)",
        "measured_map": "workloads/nocbench/analyze.py MARTY, EMPTY",
        "memshire_fit": "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.ms_pos",
    },
    "remap_no_displacement": {str(k): v for k, v in REMAP.items()},
    "ids_unchanged_by_remap": sum(1 for k, v in REMAP.items() if k == v),
    "comment_map_as_written": {
        "pair_distances_equal": sum(1 for a, b in pairs if dist(MARTY[a], MARTY[b]) == dist(cell[a], cell[b])),
        "pairs": len(pairs)},
    "comment_map_after_remap": {
        "pair_distances_equal": sum(1 for a, b in pairs if dist(MARTY[a], MARTY[b]) == dist(pos[a], pos[b])),
        "pairs": len(pairs),
        "symmetries": syms,
        "best_symmetry": best,
        "grid_rows_kernel_ids": [[("pcie0" if BID[r][1][c] == "pcie0" else "io0" if BID[r][1][c] == "io0" else grid[r][c])
                                  for c in range(6)] for r in range(6)],
    },
    "grey_cells": grey,
    "memshires": {
        "firmware_rows": {str(m): list(p) for m, p in sorted(ms_fw.items())},
        "fit_positions": {str(m): list(p) for m, p in sorted(MS_POS.items())},
        "agree": sum(1 for m in range(8) if ms_fw.get(m) == MS_POS[m]),
    },
}
json.dump(out, open(os.path.join(HERE, "firmware_map.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("ids_unchanged_by_remap", "comment_map_as_written", "grey_cells", "memshires")}, indent=1))
print("after remap:", out["comment_map_after_remap"]["pair_distances_equal"], "of", len(pairs), "; best symmetry", best)
