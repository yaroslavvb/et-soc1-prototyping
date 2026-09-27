#!/usr/bin/env python3
"""Research task B (physical layout): writes facts-layout.json and layout.json next to this script.
Every number is read from a repo file (paths relative to the worktree) or quoted from a cited manual page /
source line. Run from anywhere: python3 build_layout_facts.py"""
import importlib.util
import itertools
import json
import os
import re

REPO = "/home/yaroslavvb/claude/et-soc1-pages"
OUT = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(REPO, *a)

# ---- pages (docs/reports/MIRROR.md) ----
HPM = "https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm"
NOC = "https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication"
ANAT = "https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy"
MH = "https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy"
TEMP = "https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief"
RELAY = "https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay"
EM = "https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual"
HUB = "https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability"
LOWP = "https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power"
PWR = "https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature"

# ---- source data ----
WREP = json.load(open(P("docs/reports/data/2026-09-24-wire-energy/report.json")))
IN = WREP["inputs"]
PITCH = json.load(open(P("docs/reports/data/2026-09-24-wire-energy/research/geometry/pitch.json")))
SUMM = json.load(open(P("docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json")))
CARDS = json.load(open(P("docs/reports/data/2026-09-26-memprobe-3cards/cards.json")))
html = open(P("docs/reports/2026-09-18-et-soc1-on-chip-communication.html")).read()
NOCD = json.loads(re.search(r'<script type="application/json" id="nocbench-data">(.*?)</script>', html, re.S).group(1))

spec = importlib.util.spec_from_file_location("nocan", P("workloads/nocbench/analyze.py"))
nocan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nocan)
MARTY, EMPTY = nocan.MARTY, nocan.EMPTY
assert NOCD["layout"] == {str(k): list(v) for k, v in MARTY.items()}
assert IN["mesh_xy"]["value"] == {str(k): list(v) for k, v in MARTY.items()}

MS_POS = {int(k): tuple(v) for k, v in SUMM["decomp"]["ms_pos"].items()}
MS_CONST = SUMM["decomp"]["ms_const"]
MS_SQERR = SUMM["decomp"]["ms_fit_sqerr"]
dist = lambda p, q: abs(p[0] - q[0]) + abs(p[1] - q[1])

ET = "/home/yaroslavvb/claude/et-soc1-prototyping/external"  # read-only; cited as external/...

facts = []


def F(id_, component, topic, statement, value, unit, source, kind, card=None, note=None, page=None, rng=None):
    d = dict(id=id_, component=component, topic=topic, statement=statement, value=value, unit=unit, source=source,
             kind=kind, card=card, note=note, page=page)
    if rng is not None:
        d["range"] = rng
    facts.append(d)


R = "docs/reports/data/2026-09-24-wire-energy/report.json"
SYN = "docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md"
PJ = "docs/reports/data/2026-09-24-wire-energy/research/geometry/pitch.json"
CL = "docs/findings/05-claims.md"
ONC = "docs/reports/2026-09-18-et-soc1-on-chip-communication.html"
AN = "docs/reports/2026-09-19-et-soc1-memory-anatomy.html"
SB = "docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html"
DS = "external/et-man/ET Preliminary Datasheet Rev 1.0.pdf"
PRM = "external/et-man/ET Programmer's Reference Manual.pdf"

# ============ 1. Die and tile geometry ============
F("L01", "die", "die size", "Die area is 570 mm² (Esperanto, Hot Chips 33 slide 20 and IEEE Micro 42(3) 2022 p.37).",
  IN["die_mm2"]["value"], "mm²", R + " inputs.die_mm2", "spec", page=HPM + "#die",
  note="External vendor figure; the page cites it as the scale for the die plot.")
F("L02", "die", "die size", "Die width is about 25.6 mm (25.6–25.8), measured in pixels on Esperanto's die plot and scaled to 570 mm²; no source publishes the width.",
  IN["die_w_mm"]["value"], "mm", R + " inputs.die_w_mm (" + PJ + " scale_from_570mm2.B_symmetric_bottom.die_w_mm = %.2f)" % PITCH["scale_from_570mm2"]["B_symmetric_bottom"]["die_w_mm"],
  "derived", page=HPM + "#die", rng=IN["die_w_mm"]["range"],
  note="Estimate: IEEE Micro 2022 Fig. 7 die plot (same image as MPR Dec 2020 Fig. 1 and HC33 slide 20); bottom edge read by hand (research/geometry/README.md).")
F("L03", "die", "die size", "Die height is about 22.2 mm (22.1–22.2), from the same pixel measurement.",
  IN["die_h_mm"]["value"], "mm", R + " inputs.die_h_mm", "derived", page=HPM + "#die", rng=IN["die_h_mm"]["range"])
F("L04", "minion shire tile", "tile pitch", "Minion-shire tiles repeat every 3.73 mm east–west (254.7 px on the 1753 px-wide die plot).",
  IN["pitch_x_mm"]["value"], "mm", R + " inputs.pitch_x_mm; " + PJ + " micro22_fig7.pitch_x_px", "derived", page=HPM + "#die",
  note="3.75 mm if the 570 mm² covers only the black layout region (pitch.json scale A); 3.65 mm if it includes the drawn frame (C).")
F("L05", "minion shire tile", "tile pitch", "Minion-shire tiles repeat every 3.70 mm north–south (252.7 px).",
  IN["pitch_y_mm"]["value"], "mm", R + " inputs.pitch_y_mm; " + PJ + " micro22_fig7.pitch_y_px", "derived", page=HPM + "#die")
F("L06", "mesh link", "hop length", "One mesh hop is about 3.72 mm (3.64–3.74 depending on what the 570 mm² covers); tiles are square to within 1%, so direction does not matter.",
  IN["hop_mm"]["value"], "mm", R + " inputs.hop_mm", "derived", page=HPM + "#die", rng=IN["hop_mm"]["range"],
  note="Per mm of displacement between mesh stops; routed metal can only be longer.")
F("L07", "minion shire tile", "tile pitch", "Tile pitch ratio x/y is 1.008 on the die plot (outlines and content agree).",
  round(PITCH["micro22_fig7"]["pitch_ratio_x_over_y"], 4), "ratio", PJ + " micro22_fig7.pitch_ratio_x_over_y", "derived", page=HPM + "#die")
F("L08", "die", "floorplan", "The 6-column shire grid spans about 22.2 mm, 86% of the die width; the rest is the memory shires and their LPDDR4x PHYs down each side.",
  22.2, "mm", SYN + " §1a row 'Shire-grid span'; docs/reports/2026-09-24-heat-per-mm.html:269-276 (§2 text)", "derived", page=HPM + "#die",
  note="Tile outlines at x ≈ 139.5–1649.5 px. The heat-per-mm drawing places tiles at the 3.73 mm period, so its grid looks slightly wider than 86% (its caption says so).")
F("L09", "memory shire", "floorplan", "Each side strip (memory shires + LPDDR4x PHYs) is about 1.76 mm wide (1.74 and 1.80 mm for the two strips).",
  IN["memshire_w_mm"]["value"], "mm", R + " inputs.memshire_w_mm (" + PJ + " scale_from_570mm2.B_symmetric_bottom.memshire_col_w_mm)",
  "derived", page=HPM + "#die", rng=IN["memshire_w_mm"]["range"])
F("L10", "die", "floorplan", "The six shire rows fill the die height (margins 0–0.35 mm).",
  None, None, SYN + " §1a row 'Shire-grid span'", "derived", page=HPM + "#die")
F("L11", "minion shire tile", "area", "A minion-shire cell is about 13.8–13.95 mm²; the 34 minion shires take about 468–474 mm² (82–83% of the die).",
  None, "mm²", SYN + " §1a row 'Minion-shire cell area'", "derived", rng=[13.8, 13.95], page=HPM + "#die")
F("L12", "package", "package", "Package is 45.0 × 45.0 mm (lid 44.8) with 2,494 balls and over 30,000 bumps to the die; the package drawing shows no die outline.",
  45.0, "mm", SYN + " §1a row 'Package' (citing " + DS + " p.33 Fig. 9-1 and HC33 slide 20)", "spec")
F("L13", "die", "process", "The ET-SoC-1 has over 24 B transistors, 570 mm² and 89 mask layers (Esperanto's published figures).",
  24, "billion transistors", CL + " 'External numbers' row 'ET-SoC-1: transistors, die, mask layers' (R6)", "spec", page=LOWP)

# ============ 2. The mesh as the manuals give it ============
F("L20", "mesh", "grid", "The NoC is an 8 × 6 grid: 34 ET-Minion shires, 1 PCIe shire, 1 I/O shire and 8 memory shires. Only four memshires sit on each side, so the grid's corners are empty: 44 mesh stops.",
  44, "mesh stops", DS + " p.21 §4 'ET-SoC-1 Mesh Network on Chip'", "spec", page=HPM + "#die")
F("L21", "memory shire", "placement", "Eight memory shires: four on the west side of the die and four on the east.",
  8, "memory shires", PRM + " p.17 §1.5; " + DS + " p.30 §7", "spec", page=HPM + "#die")
F("L22", "die", "floorplan", "PRM Figure 1-3 draws a 6 × 6 array of shires with the PCIe shire and the I/O shire as the last two cells of the top row (PCIe fifth, I/O sixth, west to east), and four memory shires down each of the west and east sides; each shire carries a temperature sensor and a process monitor, and the eight voltage monitors (red) are drawn along the west and east edges beside the memory shires.",
  None, None, PRM + " p.18 Figure 1-3 'Voltage, Temperature, and Process Monitors in the ET-SoC-1'", "spec",
  note="Schematic, not to scale. The figure labels every other cell 'Minion Shire' (no IDs).")
F("L23", "die", "floorplan", "The datasheet block diagram (Figure 2-6) also puts the PCIe shire then the I/O shire at the east end of the top row, the memory shires on the west and east edges, and the LPDDR4X interfaces outside them: two LPDDR4X blocks per side, each beside two memory shires.",
  None, None, DS + " p.15 Figure 2-6 'ET-SoC-1 Block Diagram'", "spec",
  note="Read from the figure; the diagram is schematic (it draws the shire array 4 wide). Consistent with DS p.30: 'Two Memshires communicate with each 64-bit LPDDR4X memory device'.")
F("L24", "PCIe / I/O shire", "placement", "Top-row order conflicts between sources: PRM Fig. 1-3 has PCIe in the fifth column and I/O in the sixth; the die plot with its MPR caption has I/O (purple, Maxion) fifth and PCIe (orange) sixth. The two are mirror images.",
  None, None, SYN + " §1a row 'Top-row order'; docs/reports/sources/heat-per-mm.script.js:102 ('the two sources disagree on the order')", "spec",
  page=HPM + "#die", note="Unresolved; the heat-per-mm die drawing labels both cells 'PCIe or I/O'.")
F("L25", "shire IDs", "numbering", "ESR shire IDs: 0–33 are minion shires 0–33, 232–239 are memory shires 0–7, 253 is the PCIe shire, 254 the I/O shire, 255 means 'the local minion shire'.",
  None, None, PRM + " p.487 §15 (ESR address bits 29:22 encode the shire ID)", "spec")
F("L26", "master / spare shire", "numbering", "The master shire is shire 32 and the spare shire is shire 33 (the last of NUM_SHIRES = 34).",
  32, "shire ID", "external/et-platform/et-common-libs/include/system/layout.h:37 (MASTER_SHIRE 32); external/et-platform/device-bootloaders/src/ServiceProcessorBL2/include/noc_reconfigure.h:22-23 (SPARE_SHIRE_BIT_POSITION = NUM_SHIRES - 1 = 33)",
  "spec")
F("L27", "chip", "counts", "34 minion shires × 32 minions = 1,088 minions; 32 shires (1,024 minions) are the compute array, one is the master (management) shire and one a spare. PRM Figure 1-1 calls it '34 Shires / 1,088 Minion cores and 4 Maxion cores in a 6 x 6 array'.",
  1088, "minions", PRM + " p.8 §1.2 and p.9 Figure 1-1", "spec")
F("L28", "PCIe shire", "component", "The PCIe shire holds two independent PCI Express controllers and an 8-lane PCIe physical interface (Gen4, up to 25.78 Gb/s per lane).",
  8, "lanes", PRM + " p.8 §1.2; " + DS + " p.4 §1", "spec")
F("L29", "I/O shire", "component", "The I/O shire holds a Maxion neighbourhood of four ET-Maxion cores, another 4 MB L2/L3, the service processor with its ROM and 1 MB scratchpad SRAM, a hardware root of trust, USB, I2C, SPI and UARTs; the five PVT controllers also sit in it.",
  4, "Maxion cores", PRM + " p.8 §1.2 and p.17 §1.6", "spec")

# ============ 3. The logical map (measured) ============
rows_logical = []
for y in range(6):
    row = []
    for x in range(6):
        sid = next((s for s, p in MARTY.items() if p == (x, y)), None)
        row.append(sid if sid is not None else "grey")
    rows_logical.append(row)
F("L30", "mesh", "logical map", "The 32 compute shires sit on a logical 6 × 6 map (marty1885's coordinates, x across, y down). Rows y = 0…5: " +
  "; ".join(" ".join(str(v) for v in r) for r in rows_logical) + ". 'grey' cells hold no compute shire.",
  None, None, "workloads/nocbench/analyze.py:52-60 (MARTY, EMPTY); " + R + " inputs.mesh_xy", "measured",
  card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#where-the-shires-are-a-6-6-mesh",
  note="Inferred by marty1885 from shire-to-shire bandwidth (etTopoScan); this repo confirmed it from latency on all three cards (L71, L75). Distances fix the map only up to rotation/reflection.")
F("L31", "mesh", "grey cells", "The four grey cells of the logical map are (0,3), (0,4), (0,5) and (5,3). They hold the master shire, the spare shire, the PCIe shire and the I/O shire, which route traffic too; which is which was not measured.",
  4, "cells", "workloads/nocbench/analyze.py:50-51,60 (EMPTY); " + ONC + ":719; " + SB + ":786", "measured",
  page=NOC + "#where-the-shires-are-a-6-6-mesh",
  note="analyze.py:50-51: marty1885's bandwidth data shows (5,3) routes traffic.")
F("L32", "mesh", "grey cells", "Inferred identities: (0,4) and (0,5) are the I/O and PCIe shires (the two top-row cells beside each other on the die); (0,3) and (5,3) are the master and spare shires, in some order.",
  None, None, SYN + " §1a row 'Logical map vs die'; " + SB + ":765-786 (cells labelled 'master or spare' and 'I/O or PCIe', 'inferred')",
  "inferred", page=TEMP + "#mesh",
  note="By PRM Fig. 1-3's order (PCIe west of I/O) PCIe would be (0,4) and I/O (0,5); the MPR die plot is mirrored (L24).")
F("L33", "mesh", "orientation", "The logical map appears to be the die turned a quarter: in map orientation the memory shires sit above and below the grid; on the die (and in the firmware's naming, 0–3 west, 4–7 east) they are the two side columns. Logical x runs north–south (die rows) and y runs east–west (die columns).",
  None, None, ONC + ":719; " + AN + ":780-783; docs/et-soc1-notes.md:104-105; " + SYN + " §1a row 'Logical map vs die'",
  "inferred", page=NOC + "#where-the-shires-are-a-6-6-mesh",
  note="Derived note: mapping (x, y) to (die row = x, die column = y + 1 of 8) is a transpose (a quarter turn plus a mirror); distances cannot tell a rotation from a reflection, so the pages' 'turned a quarter' is about which axis is which, not handedness.")
die_rows = []
for x in range(6):
    row = []
    for c in range(8):
        if c in (0, 7):
            if 1 <= x <= 4:
                row.append("MS%d" % ((x - 1) if c == 0 else (x + 3)))
            else:
                row.append(None)
        else:
            y = c - 1
            sid = next((s for s, p in MARTY.items() if p == (x, y)), None)
            row.append(sid if sid is not None else "grey")
    die_rows.append(row)
F("L34", "mesh", "die orientation", "Die-orientation 8 × 6 view (north row first, west column first; MS = memory shire, None = empty corner): " +
  " | ".join(" ".join(str(v) for v in r) for r in die_rows) + ".",
  None, None, "derived from workloads/nocbench/analyze.py:52-60 (MARTY) with the mapping of " + SYN + " §1a ('Logical x runs N–S and y runs E–W'; '(0,3) = top row col 4, (0,4)/(0,5) = I/O and PCIe, (5,3) = bottom row col 4') and the memory-shire fit of " + AN + ":864",
  "inferred", page=HPM + "#die",
  note="Memory-shire rows follow the fit's order (0–3 at x = 1…4); the firmware comment in noc_reconfigure.h:78-81 also lists mc0…mc3 top to bottom on the west and mc4…mc7 on the east. Memory shire 2's row is a tie-break (L42).")
ring = [0, 24, 9, 25, 2, 11, 19, 27, 18, 10, 17, 14, 22, 26, 15, 23, 31, 7, 6, 30, 29, 5, 28, 20, 12, 21, 13, 1, 16, 4, 3, 8]
assert all(nocan.hops(ring[i], ring[(i + 1) % 32]) == 1 for i in range(32))
F("L35", "mesh", "ring", "A ring that visits all 32 compute shires one hop at a time: " + " ".join(map(str, ring)) + ", then back to 0.",
  None, None, ONC + " (ring-note, near line 723); docs/et-soc1-notes.md:108-109", "derived", page=NOC + "#where-the-shires-are-a-6-6-mesh",
  note="Checked here against MARTY: every step is 1 hop.")
nxt = [nocan.hops(i, (i + 1) % 32) for i in range(32)]
F("L36", "shire IDs", "numbering", "Shire IDs do not follow the mesh: the next shire by ID is 1–10 hops away, 3.5 on average.",
  sum(nxt) / 32, "hops", "docs/et-soc1-notes.md:105-106; " + CL + ":254", "derived", page=NOC + "#where-the-shires-are-a-6-6-mesh",
  note="Recomputed from MARTY: min %d, max %d, mean %.2f (ring i → i+1 mod 32)." % (min(nxt), max(nxt), sum(nxt) / 32))
FW = [[0, 16, 12, 4, 253, 254], [1, 8, 24, 28, 20, 5], [9, 17, 25, 29, 21, 13], [2, 18, 26, 30, 22, 6], [10, 3, 27, 31, 7, 14], [11, 19, 32, 33, 23, 15]]
FWp = {v: (r, c) for r, row in enumerate(FW) for c, v in enumerate(row)}
pairs = list(itertools.combinations(range(32), 2))
same = sum(1 for i, j in pairs if dist(MARTY[i], MARTY[j]) == dist(FWp[i], FWp[j]))
adj = [(i, j) for i, j in pairs if dist(MARTY[i], MARTY[j]) == 1]
adj_fw = sum(1 for i, j in adj if dist(FWp[i], FWp[j]) == 1)
F("L37", "mesh", "firmware map", "A firmware comment gives a 'default Shire Virtual ID Map, based on the NOC spec' in die orientation: rows " +
  " | ".join(" ".join(map(str, r)) for r in FW) + ", with mc0–mc3 on the west and mc4–mc7 on the east. It does NOT match the measured map: only %d of 496 shire pairs have the same Manhattan distance, and %d of the %d measured one-hop pairs are adjacent in it." % (same, adj_fw, len(adj)),
  None, None, "external/et-platform/device-bootloaders/src/ServiceProcessorBL2/include/noc_reconfigure.h:76-82 (comparison computed here against workloads/nocbench/analyze.py MARTY)",
  "derived", note="Its IDs are 'virtual IDs'; either they are not the kernel-visible shire IDs or the comment is stale. It agrees with the manuals on the top-row PCIe (253) then I/O (254) order and on memshire sides, but puts master 32 and spare 33 side by side in the bottom row, which the measured grey cells contradict. Do not use it to place compute shires.")

# ============ 4. Memory shires: where the latency fit puts them ============
F("L40", "memory shire", "placement", "Fitting DRAM latency with one shared constant plus 12 cycles per hop, and each memory shire one hop outside the grid, puts memory shires 0–3 above the grid and 4–7 below it at x = 1…4 (logical frame): " +
  ", ".join("MS%d (%d,%d)" % (m, *MS_POS[m]) for m in range(8)) + "; total squared error %d cycles² over 32 home/memory-shire pairs." % MS_SQERR,
  MS_SQERR, "cycles²", "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.ms_pos, decomp.ms_fit_sqerr; workloads/memprobe/analyze.py:111-127; " + AN + ":862-865",
  "measured", card="aifoundry2", page=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop",
  note="The fit tried only positions one hop outside the grid; moving all eight one hop further out fits equally with a constant of 79.")
F("L41", "memory shire", "latency", "The memory-shire leg is 91 cycles plus 12 per hop between the L3 home shire and the memory shire (fitted constant); refitted pass by pass on three cards the constant reads 90–91.",
  MS_CONST, "cycles", "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.ms_const; docs/reports/data/2026-09-26-memprobe-3cards/cards.json cards.<card>.ms_const (%s)" % {c: CARDS["cards"][c]["ms_const"] for c in CARDS["cards"]},
  "measured", card="aifoundry2 (fit); aifoundry2, aifoundry3, aifoundry1-c1 (refit)", page=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop", rng=[90, 91])
F("L42", "memory shire", "placement", "Memory shire 2's position is a tie-break: its four home shires all sit in column x = 4, so x = 3 or x = 5 above the grid, or (6, 0) beside it, fit equally.",
  None, None, AN + ":778-780; " + ONC + ":719", "measured", card="aifoundry2", page=ANAT + "#trace-one-load")
F("L43", "memory shire", "address map", "The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).",
  None, None, AN + ":834, 858-861; docs/research/counters-and-dram.md:66-69", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1",
  page=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop", note="'m, m+8, m+16, m+24' is derived from the two bit fields (bits 8:6 are the low three bits of 10:6).")
hs = [dist(MARTY[h], MS_POS[h & 7]) for h in range(32)]
F("L44", "memory shire", "distance effect", "With the memory shires one hop outside the grid, the memory shire's position adds 12–84 cycles to a DRAM load (1–7 hops from the L3 home).",
  None, "cycles", AN + ":743", "derived", page=ANAT + "#trace-one-load", rng=[12, 84],
  note="Recomputed from MARTY and ms_pos: home→memory-shire distance is %d–%d hops, mean %.3f." % (min(hs), max(hs), sum(hs) / 32))
F("L45", "memory path", "latency model", "Whole DRAM load: latency = 110 + 12·hops(requester → L3 home) + 91 + 12·hops(L3 home → memory shire). Left as fitted, the model is within ±3 cycles for 97% of loads on aifoundry2, 93% on aifoundry3 and 94% on aifoundry1's card 1.",
  None, "cycles", AN + ":866-873", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop")
F("L46", "memory path", "latency split", "Of the 91-cycle memory-shire constant (152 ns), the DRAM chip accounts for about 25–28 cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, one or two 4.3 ns bursts); at most ~63–66 cycles (~105–110 ns) are the memory shire itself: controller queue, PHY and the crossings between the 933 MHz DDR clock and the mesh.",
  None, "cycles", AN + ":888-893", "derived", page=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop",
  note="'At most' because each hop further out moves 12 cycles from the constant into the mesh legs.")
F("L47", "memory shire", "component", "Each memory shire drives two 16-bit LPDDR4X channels (16 in all, four external LPDDR4X chips of four 16-bit channels = 64 bits each); two memory shires share each 64-bit LPDDR4X device, at up to 4,266 Mb/s per pin.",
  16, "channels", PRM + " p.17 §1.5; " + DS + " p.30 §7 and §7.1", "spec",
  note="The manuals differ on controllers: PRM p.17 'two memory controllers that each have a 16-bit LPDDR4X channel'; DS p.30 'two 16-bit LPDDR4X physical interfaces sharing a single 32-bit controller'. docs/research/counters-and-dram.md:286 follows the PRM (2 uMCTL2 per memshire).")
F("L48", "memory shire", "component", "Each memory shire has a 512-bit NoC memory port; the datasheet gives the NoC side a maximum of 32 GB/s per memory shire, almost twice the sustained LPDDR4X throughput behind it.",
  32, "GB/s", DS + " p.30 §7.1.1 and §7.1.1.1", "spec")
F("L49", "memory", "bandwidth", "Sixteen 16-bit LPDDR4X controllers at up to 4,266 MT/s (datasheet: 133 GB/s); these cards run the DDR clock at 933 MHz (119 GB/s) and 1,024 minions reached 76 GB/s from DRAM at 600 MHz.",
  76, "GB/s", DS + " p.4 §1; docs/et-soc1-notes.md:20 (933 MHz, 119 GB/s); " + CL + " row 'Bandwidth at 600 MHz, 1,024 minions' (E33, E29)",
  "measured", card="aifoundry2, aifoundry3", page=MH,
  note="docs/et-soc1-notes.md:20 gives 136.5 GB/s for 16 × 16 bit × 4,266 MT/s; the datasheet prints 133.")
F("L50", "memory shire", "address map", "Inferred DRAM address map: PA[9] selects the controller (channel) within the memory shire, PA[12:10] the DRAM bank (8 banks), PA[34:18] the row; the page policy is open-page.",
  None, None, "docs/research/counters-and-dram.md:66-85", "inferred",
  note="From a tool comment, NoC mask values and ADDRMAP registers, not a programmed-register readback (the doc says so).")

# ============ 5. Measured spatial facts: latency ============
m18 = NOCD["matrices"]["matrix-pingpong"]
v3 = {c: NOCD["v3"]["cards"][c]["matrices"]["matrix-pingpong"] for c in NOCD["v3"]["cards"]}
F("L70", "mesh", "hop latency", "TensorSend 32 B round trip between shires = 150 + 12.02 × (Manhattan hops) cycles at 600 MHz, worst residual 1.1–1.4 cycles over all 496 pairs, on each of three cards.",
  12.02, "cycles per hop", ONC + ":725 and embedded nocbench-data v3.cards.<card>.matrices['matrix-pingpong'].b; " + CL + ":412", "measured",
  card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#where-the-shires-are-a-6-6-mesh",
  note="Per card: " + "; ".join("%s %.2f + %.3f (worst %.2f)" % (c, v["a"], v["b"], v["worst"]) for c, v in v3.items()) +
       ". First session (aifoundry2, 18 Sep): %.2f + %.3f, worst %.2f." % (m18["a"], m18["b"], m18["worst"]))
F("L71", "mesh", "hop latency", "Intercept of the between-shire round trip: 150 cycles (the fixed cost of leaving and re-entering shires).",
  150, "cycles", ONC + ":725; " + CL + ":412 (149.96–150.08 over passes)", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1",
  page=NOC + "#where-the-shires-are-a-6-6-mesh", rng=[149.96, 150.08])
F("L72", "mesh", "hop latency", "Each mesh hop adds 20 ns round trip: 12 minion cycles at 600 MHz, 16 at 800; a hop is 20 ns at either clock. In time, 250 ns + 20 ns per hop across shires, r² 0.9999 over 496 pairs.",
  20, "ns per hop (round trip)", ONC + ":709 (KPI); " + AN + ":841-844; docs/et-soc1-notes.md:90-91", "measured",
  card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC)
F("L73", "mesh", "hop latency", "At the NoC's 400 MHz a 20 ns round-trip hop is about 4 NoC cycles each way; Chang reports 3 cycles per direction (clock unstated), not reconciled.",
  4, "NoC cycles per hop each way", SYN + " §1b row 'Per-hop latency'", "derived")
F("L74", "mesh", "hop latency", "Loads from another shire's scratchpad: 99.84 + 12.00 cycles per hop; all 124 points within 1 cycle in every pass; a→b equals b→a within 0.032 cycles.",
  12.00, "cycles per hop", CL + ":411 (V3R/lat.json LAT-M3); docs/reports/2026-09-18-et-soc1-memory-hierarchy.html (scratchpad-latency-across-the-mesh)",
  "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=MH + "#scratchpad-latency-across-the-mesh")
F("L75", "mesh", "map check", "A search from random layouts, without marty1885's map, recovered the same distances in 12 of 12 restarts in every pass on every card.",
  12, "restarts of 12", CL + ":383, 412; " + ONC + ":725", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#where-the-shires-are-a-6-6-mesh")
F("L76", "mesh", "hop latency", "With 1 KB messages the round trip rises 12.0 cycles per hop up to 5 hops and 36.0 beyond.",
  36.0, "cycles per hop beyond 5 hops", CL + ":382, 412", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#latency-grows-with-distance-except-through-memory")
F("L77", "mesh", "hop latency", "Credit (FCC) round trips across shires: 140.2 + 14.4 cycles per hop (about 234 ns + 24 ns per hop), against a prediction of 148 + 12.2.",
  14.4, "cycles per hop", CL + ":412; " + ONC + ":729", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#latency-grows-with-distance-except-through-memory", rng=[14.42, 14.44])
F("L78", "L3", "hop latency", "L3 hit = 110 + 12 × hops(requester → L3 home shire) cycles; on three cards 110.5–110.6 + 11.99 × hops, 99.4–100% of lines within ±4 cycles. ~48 cycles are the L1/L2 lookup and miss, ~62 the home slice.",
  11.99, "cycles per hop", AN + ":833-843; " + CL + ":403 (V3R/mem.json MEM-P1)", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1",
  page=ANAT + "#l3-110-cycles-plus-12-per-hop")
F("L79", "L3", "requester position", "Where the requester sits matters: L3 (4 MB working set) 168.8–168.9 cycles from shires 0 and 31, 160.6–160.7 from 7, 159.1–159.2 from 24; DRAM (256 MB) 296.6–297.1 from 0 and 31, 287.2–288.8 from 7 and 24. L3(0) − L3(24) = 9.69–9.73 cycles on the three cards.",
  9.7, "cycles", CL + ":410 (V3R/lat.json LAT-M2)", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=MH + "#scratchpad-latency-across-the-mesh")
mh = {r: sum(nocan.hops(r, s) for s in MARTY) / 32 for r in (0, 7, 24, 31)}
F("L80", "L3", "requester position", "Why: the mean distance to the 32 L3 slices is %.3f hops from shire 0, %.4f from 7, %.4f from 24 and %.3f from 31 (0 and 31 sit in opposite corners of the map); the difference 0 − 24 is %.4f hops × 12 = %.2f cycles, matching the measured 9.7." % (mh[0], mh[7], mh[24], mh[31], mh[0] - mh[24], 12 * (mh[0] - mh[24])),
  round(12 * (mh[0] - mh[24]), 2), "cycles", "computed here from workloads/nocbench/analyze.py MARTY (hops) and the 12 cycles/hop of " + AN + ":837",
  "derived", page=MH + "#scratchpad-latency-across-the-mesh")

# ============ 6. Measured spatial facts: energy and bandwidth ============
mf, pc = NOCD["reruns"]["mesh_fit"], NOCD["reruns"]["mesh_fit_per_card"]
F("L85", "mesh", "hop energy", "Messaging across the mesh costs %.1f + %.2f pJ per byte per mean hop (1 KB TensorSend rings, board power over idle), pooled over three cards, five rings with mean distances of 1.6–4.7 hops." % (mf["a"], mf["b"]),
  round(mf["b"], 2), "pJ/B per hop", ONC + ":783 and embedded nocbench-data reruns.mesh_fit (a %.3f, b %.4f, r² %.3f, n %d)" % (mf["a"], mf["b"], mf["r2"], mf["n"]),
  "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#energy-per-byte-moved",
  note="Per card: " + "; ".join("%s %.1f + %.2f" % (c, v["a"], v["b"]) for c, v in pc.items()) + ". The intercept is the fit's value at zero mean hops; rings inside a shire cost 0.7–2.2 pJ/B (L87).")
F("L86", "mesh", "hop energy", "Ring energy slope per mean hop by card: aifoundry2 1.78 [1.31–2.25], aifoundry3 1.73 [0.48–2.97], aifoundry1 card 1 1.74 [0.95–2.53] pJ/B (99% intervals, 6 passes each); no pair of cards differs; pooled 1.75 (the page gives ±50%).",
  1.75, "pJ/B per hop", CL + ":450 (V3R/rl.json RL-a)", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#energy-per-byte-moved")
F("L87", "shire", "energy", "Inside a shire, messaging costs 0.7–2.2 pJ per byte with 1 KB messages, busy cores included; a byte costs 6–26× more once it crosses the shire boundary.",
  None, "pJ/B", ONC + ":703 (lede), :711 (KPI), :783", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#energy-per-byte-moved", rng=[0.7, 2.2])
F("L88", "mesh link", "energy per mm", "A random bit moved 1 mm over free links at 0.485 V: mesh rail 36.1 [35.2–37.0] (aifoundry2), 35.8 [35.1–36.5] (aifoundry3), 38.1 [26.3–49.9] fJ (aifoundry1 card 1); board power 46.7, 44.4, 51.1 fJ.",
  36.2, "fJ per bit·mm (mesh rail)", CL + ":341, 444 (V3R/wire.json WIRE-P1-16/P11a, P11b); " + R + " headline", "measured",
  card="aifoundry2, aifoundry3, aifoundry1-c1", page=HPM, note="36.2 fJ is the two-card (E32) mesh-rail value: 24.6 data + 11.7 fixed.")
F("L89", "mesh link", "energy per mm", "On a loaded mesh (flows sharing links) a random bit costs 50.4 fJ per mm on the mesh rail (30.6 data + 19.8 fixed) and 72.9 fJ on board power.",
  50.4, "fJ per bit·mm (mesh rail)", CL + ":342 (" + R + " headline['v2/noc_rail'], ['v2/board'])", "measured", card="aifoundry2, aifoundry3", page=HPM + "#contention")
F("L90", "mesh link", "energy per hop", "The four-hop step: on the mesh rail, random data at four hops costs 6.5–8.0% more than the line through 1, 2, 3 and 6 hops predicts (all ones 14.5–15.4%); link-disjoint flows at four hops sit on their line (0.1–0.6% off).",
  None, "%", CL + ":448 (V3R/wire.json WIRE-P1-16/P7a, P7c, P14a)", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=HPM + "#contention",
  note="Consistent with link sharing: 0/22/32/55/72% of link-hops shared at 1/2/3/4/6 hops under XY routing (" + CL + ":348).")
F("L91", "mesh", "bandwidth", "The shire boundary is a bandwidth cliff: with every minion sending 1 KB messages the chip moves 1.1–3.0 TB/s inside shires but 0.09–0.16 TB/s between them (7–34× less); a TensorLoad from a remote scratchpad does %.2f TB/s at 600 MHz." % (NOCD["scp_remote_gbps_600"] / 1000),
  round(NOCD["scp_remote_gbps_600"] / 1000, 2), "TB/s (remote-scratchpad TensorLoad)", ONC + ":703, 775, 816; embedded nocbench-data scp_remote_gbps_600",
  "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#message-size-and-bandwidth")
F("L92", "mesh", "bandwidth", "A per-reader tensor load over one hop on a link it uses alone moved at least 46.8 GB/s: at least 117 B per 400 MHz NoC cycle per link direction, more than one 512-bit layer (25.6 GB/s); the link was not saturated.",
  46.8, "GB/s (lower bound)", SYN + " §1b row 'Measured data per link direction' (docs/reports/data/2026-09-23-energy-manual/catalogue.json wire/hop1)", "measured",
  note="Card not stated in SYNTHESIS (E27 ran on aifoundry2 and aifoundry3).")
F("L93", "memory path", "relay", "Handing a result to the next shire instead of through DRAM: aifoundry2 111.3 vs 8.61 pJ/B, aifoundry3 107.5 vs 8.27, aifoundry1 card 1 129.9 vs 9.89; DRAM ÷ next shire 12.9–13.1× on every card; own scratchpad 4.05–4.86 pJ/B.",
  12.97, "× (pooled DRAM ÷ next shire)", CL + ":451 (V3R/rl.json)", "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=RELAY)
F("L94", "mesh", "relay distance", "In the relay, which shire receives the slab moves bandwidth by up to a quarter: 593 GB/s to the next shire by ID (3.5 hops on average, longest hand-off 10) to 733 GB/s at 16 shire IDs (2.1, longest 6); bandwidth falls with the longest hand-off (r = −0.99), about 3,200–3,300 cycles of stage time per hop of it.",
  None, "GB/s", CL + ":254 (DATAO/onchip.json distance[])", "measured", card="aifoundry2, aifoundry3", page=RELAY + "#how-far-the-slab-moves-does-not-change-the-bandwidth",
  note="A correlation over five offsets, not a controlled test (the claims row says so).")
lv = NOCD["reruns"]["levels"]
F("L95", "memory path", "energy", "Reference energies per byte read at 600 MHz (three cards): L2 %.1f, another shire's scratchpad %.1f (zeros %.1f, random %.1f), DRAM %.1f pJ/B." % (lv["l2"]["mean"], lv["scp-remote"]["mean"], lv["scp-remote"]["by_contents"]["zeros"]["mean"], lv["scp-remote"]["by_contents"]["random"]["mean"], lv["dram"]["mean"]),
  round(lv["dram"]["mean"], 1), "pJ/B (DRAM)", "embedded nocbench-data reruns.levels in " + ONC + " (source V3-RL); " + R + " context.dram_read_pj_per_byte",
  "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=EM + "#bytes-through-the-memory-hierarchy",
  rng=[round(lv["dram"]["lo"], 1), round(lv["dram"]["hi"], 1)])

# ============ 7. NoC parameters ============
F("L100", "mesh", "NoC clock", "The mesh runs at 400 MHz on these cards (design point 500 MHz).",
  IN["noc_mhz"]["value"], "MHz", R + " inputs.noc_mhz (telemetry mhz.noc; firmware main.c 'NOC frequency modes (400MHz)')", "measured",
  card="aifoundry2, aifoundry3, aifoundry1-c1", page=HPM + "#method")
F("L101", "mesh", "NoC voltage", "The mesh (routers, links, NetSpeed bridges) is on its own low-voltage rail at 0.485 V (0.484 V at the die).",
  IN["noc_v"]["value"], "V", R + " inputs.noc_v (telemetry reg_mv.noc 485 / die_mv.noc 484); " + SYN + " §1b 'Voltage domain'", "measured", page=HPM + "#method")
F("L102", "mesh", "port width", "Every shire's NoC port is 512 bits wide: one 64 B line per beat, single-beat only.",
  IN["port_bits"]["value"], "bits", R + " inputs.port_bits (core-et rtl/inc/axi_defines.vh:43 SC_MESH_MASTER_AXI_DATA_SIZE 512)", "spec", page=HPM + "#lanes")
F("L103", "shire", "NoC lanes", "A shire has 4 to_l3 master and 4 L3 slave lanes to the mesh; the lane is chosen by PA[7:6], so lines i and i+4 share a lane (a 1 KB load puts 4 of its 16 lines on each).",
  IN["lanes"]["value"], "lanes", R + " inputs.lanes (core-et-main shirecache_mesh_master.sv:141-153); " + SYN + " §1b 'Lanes'", "spec", page=HPM + "#lanes")
F("L104", "mesh", "routing", "Routing is minimal (latency is linear in Manhattan distance), but the dimension order was not measured; the analyses assume x first (XY). Chang infers XY.",
  None, None, SYN + " §1b 'Routing'; docs/reports/sources/heat-per-mm.script.js:521; " + AN + ":784-785", "inferred", page=HPM + "#contention")
F("L105", "mesh", "structure", "Each mesh stop has 9 main-NoC routers (layers 0–8) plus one debug-NoC router; routers have 8 ports (H, E, S, W, N, I, J, K) with 4 VC slots each; route info, packet, sideband and data are parity-protected (no ECC).",
  9, "main-NoC routers per stop", SYN + " §1b rows 'Main-NoC layers', 'Router ports and VCs', 'Error protection' (etsoc_shire_other_esr.h:3877-3981; noc_esr.h)", "spec",
  note="SYNTHESIS marks these 'U' (not independently re-verified); router-to-router flit width is unknown.")

# ============ 8. Inside a shire ============
F("L110", "shire", "structure", "A minion shire = four neighbourhoods of eight minions (32 minions, 64 harts), a four-bank 4 MB shared L2/L3 cache, a mesh stop and a crossbar joining them; each neighbourhood shares a 32 KB instruction cache.",
  32, "minions per shire", PRM + " p.8 §1.2; external/core-et/docs/CORE-ET Minion Shire Description.pdf p.4 §1", "spec", page=NOC + "#inside-a-shire-only-the-tree-edges-are-fast")
F("L111", "shire", "cache banks", "The shire cache is 4 MB in 4 banks × 4 sub-banks (the POR for the first SoC); 64 B lines everywhere.",
  4, "banks", "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.9 §1 ('4M/Shire, 4 banks/Shire, 4 sub-banks/bank'); docs/research/counters-and-dram.md:458", "spec")
F("L112", "shire", "SRAM split", "The 4 MB is split between L2 cache, a slice of the chip-wide L3, and scratchpad; the typical split is 512 KB L2, 1 MB L3 slice (of 32 MB), 2.5 MB scratchpad any shire can address.",
  2.5, "MB scratchpad", "docs/et-soc1-notes.md:19; " + ONC + ":714 (terms)", "spec", page=NOC)
F("L113", "shire", "address map", "Inside a shire the L2 bank is PA[7:6] and sub-bank PA[9:8]; for L3 the home shire is PA[10:6] (64 B interleave over 32 shires), bank PA[12:11], sub-bank PA[14:13].",
  None, None, "docs/research/counters-and-dram.md:66-68, 372-378 (SCspec §1; core-et esr_cache_bank.v:89-103)", "spec",
  note="The home-shire bits were confirmed on silicon (" + AN + ":834-837); the bank bits are from the spec.")
F("L114", "shire", "block diagram", "Shire top level: the main NoC interface (ports to_l3 ×4, to_sys, l3_slave ×4, uc_to_l3, uc_to_sys, sys_slave) sits above the shire channel (shire cache with 4 banks, UC block, RBOX, ESR, I$ memories), which feeds the four neighbourhoods; clock domains CLOCK_NOC, SHIRE_CLOCK, NEIGH_CLOCK, with the PLL/DLL, sensors and debug NoC bridge below.",
  None, None, "external/core-et/docs/CORE-ET Minion Shire Description.pdf p.5 Figure 1", "spec",
  note="A logical block diagram, not a floorplan: no source gives where the four neighbourhoods and four banks sit physically inside the 3.7 mm tile.")
F("L115", "neighbourhood", "physical layout", "Neighbourhood floorplan: two columns of four minions either side of a central 'neighbourhood channel'; left column M2, M0, M4, M6 and right column M3, M1, M5, M7 (north to south); all ports and the high-voltage region are at the north end, where it meets the shire channel.",
  None, None, "external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf pp.7-8 §2.2, Figure 2 'Neighborhood Physical Layout'", "spec",
  note="Placed to shorten the fast local messaging network: its tree edges 0–1, 2–3, 4–5, 6–7 cross the channel and 0–2, 0–4, 4–6 are vertical neighbours (L116).")
tp = NOCD["primitives"]
F("L116", "neighbourhood", "fast network", "Inside a shire only the reduction-tree edges are fast: 68 cycles (113 ns) round trip for 28 pairs per shire (in every neighbourhood 0–1, 0–2, 0–4, 2–3, 4–5, 4–6, 6–7) and 114–115 cycles (190 ns) for all 468 others, in every pass on three cards.",
  68, "cycles", ONC + ":735-742; embedded nocbench-data primitives.tree_pairs, tree_hop (%.1f), other_hop (%.1f)" % (tp["tree_hop"], tp["other_hop"]),
  "measured", card="aifoundry2, aifoundry3, aifoundry1-c1", page=NOC + "#inside-a-shire-only-the-tree-edges-are-fast")

# ============ 9. Sensors and per-shire readings ============
F("L120", "sensors", "placement", "One temperature sensor and one process detector in each minion shire and the I/O shire (36 each), 8 voltage-monitor blocks with up to 128 remote sense points, read by five PVT controllers in the I/O shire.",
  36, "temperature sensors", PRM + " p.17 §1.6 and p.18 Figure 1-3, Table 1-6", "spec", page=TEMP + "#sensors")
F("L121", "sensors", "placement", "35 sensors are read: TS0–TS31 for the compute shires (TSn in shire n), TS32 master, TS33 spare, TS34 I/O; the PCIe shire has no sensor.",
  35, "sensors", SB + ":786 (caption) and :789-790", "spec", page=TEMP + "#mesh")
F("L122", "sensors", "resolution", "The firmware reports die temperature as one number in whole degrees: the mean of the 34 minion-shire sensors, so no per-shire thermal map comes out of the standard path.",
  1, "°C resolution", CL + ":36 (telemetry temp_c.minshire[0])", "measured", card="aifoundry2", page=TEMP + "#bottleneck")
F("L123", "shire", "voltage", "Per-shire on-die voltage at idle (34 minion shires): minion rail 517–521 mV, lows 513 (shires 0, 1, 2, 18) to 520, highs to 522; SRAM 703–707 mV; mesh 483–486 mV.",
  None, "mV", CL + ":41 (docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json)", "measured", card="aifoundry2", page=PWR, rng=[517, 521])

json.dump(facts, open(os.path.join(OUT, "facts-layout.json"), "w"), indent=1, ensure_ascii=False)

# ================= layout.json =================
ms_die = {m: {"side": "west" if m < 4 else "east", "die_col": 0 if m < 4 else 7, "die_row": MS_POS[m][0]} for m in range(8)}
layout = {
    "mesh": rows_logical,
    "mesh_orientation": "logical map, x across (index within a row) and y down (row index), as drawn on the on-chip communication, memory anatomy and spatial temperature pages; 'grey' = no compute shire",
    "mesh_grey_labels": {"(0,3)": "master or spare", "(5,3)": "master or spare", "(0,4)": "I/O or PCIe", "(0,5)": "I/O or PCIe"},
    "mesh_die": die_rows,
    "mesh_die_orientation": "INFERRED die view: 6 rows north→south = logical x 0..5; 8 columns west→east: column 0 memory shires 0–3, columns 1..6 = logical y 0..5, column 7 memory shires 4–7; None = empty corner",
    "memshires": [
        {"id": m, "esr_shire_id": 232 + m, "pos": list(MS_POS[m]), "pos_frame": "logical (x, y); y = -1 above the grid, y = 6 below",
         "die": ms_die[m], "tie_break": m == 2,
         "source": "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.ms_pos['%d'] (fit, aifoundry2); die side: docs/research/counters-and-dram.md:69 and PRM p.17; die row: inferred (logical x), matching noc_reconfigure.h:78-81 mc order" % m}
        for m in range(8)],
    "special": [
        {"name": "master shire", "shire_id": 32, "logical_pos": "(0,3) or (5,3)", "die_pos": "top row column 4 or bottom row column 4 (of 0..7)",
         "source": "ID: external/et-platform/et-common-libs/include/system/layout.h:37; position: workloads/nocbench/analyze.py:60 EMPTY + " + SYN + " §1a (inferred; which of the two is not measured)"},
        {"name": "spare shire", "shire_id": 33, "logical_pos": "(0,3) or (5,3)", "die_pos": "top row column 4 or bottom row column 4",
         "source": "ID: external/et-platform/device-bootloaders/src/ServiceProcessorBL2/include/noc_reconfigure.h:22-23; position as above"},
        {"name": "PCIe shire", "shire_id": 253, "logical_pos": "(0,4) or (0,5)", "die_pos": "top row column 5 or 6",
         "source": "ID: PRM p.487; position: " + SYN + " §1a (inferred); order: PRM p.18 Fig. 1-3 puts PCIe at column 5, the MPR die-plot caption at column 6"},
        {"name": "I/O shire", "shire_id": 254, "logical_pos": "(0,4) or (0,5)", "die_pos": "top row column 5 or 6",
         "source": "as PCIe"},
        {"name": "empty corners", "die_pos": "row 0 and row 5 of columns 0 and 7", "source": DS + " p.21 §4"},
        {"name": "grey cell that routes traffic", "logical_pos": "(5,3)", "source": "workloads/nocbench/analyze.py:50-51 (marty1885's bandwidth data)"},
    ],
    "die_mm": {"w": IN["die_w_mm"]["value"], "h": IN["die_h_mm"]["value"], "w_range": IN["die_w_mm"]["range"], "h_range": IN["die_h_mm"]["range"],
               "area_mm2": IN["die_mm2"]["value"], "source": R + " inputs.die_w_mm, die_h_mm, die_mm2 (pixel estimate from IEEE Micro 2022 Fig. 7 scaled to 570 mm²)"},
    "pitch_mm": {"x": IN["pitch_x_mm"]["value"], "y": IN["pitch_y_mm"]["value"], "hop": IN["hop_mm"]["value"], "hop_range": IN["hop_mm"]["range"],
                 "source": R + " inputs.pitch_x_mm, pitch_y_mm, hop_mm"},
    "memshire_strip_mm": {"w": IN["memshire_w_mm"]["value"], "range": IN["memshire_w_mm"]["range"], "source": R + " inputs.memshire_w_mm"},
    "grid_span_mm": {"w": 22.2, "fraction_of_die_width": 0.86, "source": SYN + " §1a row 'Shire-grid span'"},
    "neighbourhood_floorplan": {"left_column_n_to_s": ["M2", "M0", "M4", "M6"], "right_column_n_to_s": ["M3", "M1", "M5", "M7"],
                                "centre": "neighbourhood channel; ports and HV region at the north end",
                                "fast_tree_edges": tp["tree_pairs"],
                                "source": "external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf pp.7-8 Fig. 2; tree edges: embedded nocbench-data primitives.tree_pairs in " + ONC},
    "one_hop_ring": ring,
    "source": {
        "mesh": "workloads/nocbench/analyze.py:52-60 (MARTY, EMPTY) = " + R + " inputs.mesh_xy = embedded nocbench-data layout in " + ONC,
        "mesh_grey_labels": SB + ":765-786 (labels marked 'inferred')",
        "mesh_die": "derived here from MARTY with " + SYN + " §1a 'Logical map vs die' (inferred)",
        "memshires": "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.ms_pos (workloads/memprobe/analyze.py:111-127)",
        "special": "see each entry",
        "die_mm": R + " inputs",
        "pitch_mm": R + " inputs; " + PJ,
        "one_hop_ring": ONC + " ring-note",
    },
    "pages": {"heat_per_mm_die": HPM + "#die", "on_chip_mesh": NOC + "#where-the-shires-are-a-6-6-mesh",
              "memory_anatomy_memshire_fit": ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop",
              "spatial_temperature_mesh": TEMP + "#mesh", "memory_hierarchy_mesh": MH + "#scratchpad-latency-across-the-mesh",
              "on_chip_relay": RELAY, "energy_manual_bytes_between_shires": EM + "#bytes-between-cores-and-shires"},
}
json.dump(layout, open(os.path.join(OUT, "layout.json"), "w"), indent=1, ensure_ascii=False)
print(len(facts), "facts")
