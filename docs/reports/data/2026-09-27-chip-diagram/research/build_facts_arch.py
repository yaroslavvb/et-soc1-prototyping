#!/usr/bin/env python3
"""Build facts-arch.json: architecture facts for an interactive ET-SoC-1 chip schematic.

Every fact carries a source. Conventions in `source`:
- repo-relative paths are relative to the et-soc1-pages repository root (branch pages-v3b);
- `external/...` is the gitignored upstream clone (et-soc1-prototyping/external/); PDF pages are the PDF's own
  page index ("pdf p.N"), counted from the cover, with the section number where there is one;
- et-platform line numbers are at its checked-out HEAD 836a4ab (2026-07-17); core-et at b38a1a3.
"""
import json, sys

OUT = "/tmp/claude-1019/-home-yaroslavvb-claude/ed6d06d5-de26-4323-94f1-0dc808eafbda/scratchpad/chip/facts-arch.json"
B = "https://spacesheep.dev/@yaroslavvb/"
PAGES = {
    "hub": ("Limits of observability (reports hub)", B + "et-soc1-limits-of-observability"),
    "energy": ("The energy manual", B + "et-soc1-energy-manual"),
    "heat": ("Heat per millimetre", B + "et-soc1-heat-per-mm"),
    "dvfs": ("The DVFS loop and its leakage", B + "et-soc1-dvfs-leakage"),
    "power": ("Power and temperature telemetry", B + "et-soc1-power-temperature"),
    "horace": ("The Horace experiment", B + "et-soc1-horace-experiment"),
    "lowpower": ("Why is it low power?", B + "et-soc1-why-low-power"),
    "hotline": ("One hot line stops a shire", B + "et-soc1-hot-line"),
    "relay": ("Hand it to the next shire: on-chip relay vs DRAM", B + "et-soc1-on-chip-relay"),
    "anatomy": ("Anatomy of a memory access", B + "et-soc1-memory-anatomy"),
    "memhier": ("Memory hierarchy", B + "et-soc1-memory-hierarchy"),
    "onchip": ("On-chip communication", B + "et-soc1-on-chip-communication"),
    "matmul": ("Matmul efficiency", B + "et-soc1-matmul-efficiency"),
    "sparse": ("Sparse compute", B + "et-soc1-sparse-compute"),
    "ridge": ("Ridge points", B + "et-soc1-ridge-points"),
    "testdrive": ("Test drive", B + "et-soc1-testdrive"),
    None: (None, None),
}

CARDS3 = "aifoundry2, aifoundry3, aifoundry1-c1"
F = []


def fact(id, component, topic, statement, value, unit, source, kind, card=None, note=None, page=None, anchor=None):
    assert kind in ("spec", "measured", "derived", "inferred"), (id, kind)
    title, url = PAGES[page]
    if url and anchor:
        url = url + "#" + anchor
    F.append({"id": id, "component": component, "topic": topic, "statement": statement, "value": value,
              "unit": unit, "source": source, "kind": kind, "card": card, "note": note,
              "page": title, "page_url": url})


DS = "external/et-man/ET Preliminary Datasheet Rev 1.0.pdf"
PRM = "external/et-man/ET Programmer's Reference Manual.pdf"
MOV = "external/et-man/ET Minion Overview.pdf"
INTRO = "external/et-man/ET Introduction.pdf"
CARD = "external/et-man/ET-PCIe-Dev-Card-V3.pdf"
SCS = "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf"
MSD = "external/core-et/docs/CORE-ET Minion Shire Description.pdf"
NMAS = "external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf"
VPU = "external/core-et/docs/Minion VPU Specification.pdf"
MIND = "external/core-et/docs/Minion Description.pdf"
EP = "external/et-platform"
CL = "docs/findings/05-claims.md"
NOTES = "docs/et-soc1-notes.md"
CAD = "docs/research/counters-and-dram.md"
PT = "docs/research/power-telemetry.md"
V3R = "docs/reports/data/2026-09-25-claims-v3/results"
TEL = "docs/reports/data/2026-09-20-power-aifoundry2/horace-telemetry.jsonl (and horace2-, thermal-telemetry.jsonl: 3,681 samples, 20 Sep)"

# ---------------------------------------------------------------- chip: hierarchy and counts
fact("chip.cores-total", "chip", "hierarchy",
     "The ET-SoC-1 has 1,093 RISC-V cores: 1,088 ET-Minions, 4 ET-Maxions and 1 Minion-based service processor.",
     1093, "cores", f"{DS}, pdf p.4 (§1 Product Overview); {PRM}, pdf p.7 (§1)", "spec", page="hub", anchor="terms")
fact("chip.minion-shires", "chip", "hierarchy",
     "34 minion shires of 32 minions each = 1,088 minions. The hierarchy figure describes '34 Shires / 1,088 Minion cores and 4 Maxion cores in a 6 x 6 array'; with the PCIe and I/O shires (the Maxions sit in the I/O shire) that fills the 36 cells.",
     34, "minion shires", f"{DS}, pdf p.5 (§2.1) and Figure 2-1 on pdf p.6; {PRM}, pdf p.8-9 (§1.2, Figure 1-1)", "spec",
     page="hub", anchor="terms")
fact("chip.minions", "chip", "hierarchy", "1,088 minions on the chip (34 shires × 32).", 1088, "minions",
     f"{DS}, pdf p.15 (§2.2.1)", "spec", page="hub", anchor="terms")
fact("chip.compute-array", "chip", "hierarchy",
     "Typically 32 minion shires form the compute array and one more is the management (master) shire; the datasheet calls this a software convention, all minion shires being identical. The 34th is a yield-recovery spare, powered down in production.",
     32, "compute shires", f"{DS}, pdf p.5 (§2.1); {PRM}, pdf p.486 (§15.3: 'the 34th shire will be designated as a powered down yield recovery spare')",
     "spec", page="hub", anchor="terms")
fact("chip.minions-used", "chip", "hierarchy",
     "Kernels in these measurements run on 1,024 minions: the 32 compute shires × 32.", 1024, "minions",
     f"{CL}:30 (DATA/strict/runs.jsonl, field `minions`)", "measured", card="aifoundry2", page="horace")
fact("chip.cm-shire-mask", "chip", "hierarchy",
     "The driver reports compute shire mask 0xffffffff (shires 0-31) and sync (master) shire 32 on every card.",
     32, "compute shires",
     "docs/reports/data/2026-09-22-cards/driver_config.json, fields `cm_shire_mask`, `sync_shire`", "measured",
     card="aifoundry1 (both cards), aifoundry2, aifoundry3", page="dvfs")
fact("chip.harts", "chip", "hierarchy",
     "Software sees 2,048 harts on the 32 compute shires: hartid = shire × 64 + minion × 2 + thread (shire = hartid >> 6, neighbourhood = (hartid mod 64) >> 4, minion = hartid >> 1, thread = hartid & 1).",
     2048, "harts", f"{NOTES}:22; {EP}/et-common-libs/include/etsoc/isa/hart.h:50,62,74,86", "spec",
     page="onchip", anchor="every-primitive-against-a-gpu")
fact("chip.master-shire-id", "master shire", "hierarchy",
     "The master shire (which runs the master-minion firmware and schedules kernels) is shire 32 in the firmware; its 2.5 MB scratchpad at 0x9000_0000 holds the firmware's host-interface buffers.",
     32, "shire ID",
     f"{EP}/device-bootloaders/src/ServiceProcessorBL2/include/minion_configuration.h:48 (MM_MASTER_SHIRE_ID 32); {EP}/et-common-libs/include/system/layout.h:37,78-80; {INTRO}, pdf p.6",
     "spec", note="layout.h:45 also reserves MASTER_SHIRE_COMPUTE_HARTS 32; minion_configuration.h:53 MM_MASTER_SHIRE_NEIGH_NUM 2.",
     page="hub", anchor="terms")
fact("chip.spare-shire-id", "spare shire", "hierarchy",
     "The spare shire is bit 33 of the firmware's 34-shire mask; the NoC reconfiguration code remaps virtual shire IDs when the spare displaces a shire.",
     33, "shire ID",
     f"{EP}/device-bootloaders/src/ServiceProcessorBL2/include/noc_reconfigure.h:22-24,99-100", "spec",
     page="hub", anchor="terms")
fact("chip.maxions", "Maxion", "hierarchy",
     "Four ET-Maxion 64-bit RISC-V single-threaded superscalar out-of-order cores sit in the I/O shire with a system bus and coherency hub; they may be used for management tasks.",
     4, "cores", f"{DS}, pdf p.4 (§1) and pdf p.18 (§2.5.2)", "spec", page="hub", anchor="terms")
fact("chip.service-processor", "service processor", "hierarchy",
     "The service processor is a single ET-Minion core (one hart, no vector or tensor extension, no shire cache) in the I/O shire, with its own ROM and 1 MB scratchpad SRAM; it boots the chip, runs the power/clock governor and answers the host's management commands.",
     1, "core", f"{DS}, pdf p.5 (§2.1) and pdf p.18 (§2.4); {INTRO}, pdf p.7 ('Service Processor is a minion without vector/tensor extensions')",
     "spec", page="dvfs", anchor="the-loop-as-built")
fact("chip.io-shire", "I/O shire", "hierarchy",
     "The I/O shire holds the Maxion neighbourhood (4 Maxions) with a shared L2/L3 cache, the service processor with ROM and 1 MB SRAM, a hardware root of trust, five PVT controllers and the peripherals (USB, I2C, SPI, UART, eMMC).",
     None, None, f"{DS}, pdf p.5 (§2.1); {PRM}, pdf p.17 (§1.6, PVT controllers in the I/O shire)", "spec",
     note="Sources disagree on the Maxions' cache: the datasheet (pdf p.5) and PRM (pdf p.486) say 4 MB; the Shire Cache Specification (pdf p.22) says 'the IOShire has a cache total of 1 MB'.",
     page="hub", anchor="terms")
fact("chip.pcie-shire", "PCIe shire", "hierarchy",
     "The PCIe shire contains two independent dual-mode PCIe controllers and an 8-lane PCIe Gen4 PHY, factory-configured as an endpoint; the dev card exposes a Gen4 x8 host interface.",
     8, "lanes", f"{DS}, pdf p.5 (§2.1) and pdf p.17 (§2.3, Figure 2-7)", "spec", page="ridge",
     anchor="other-limits-that-act-like-ridge-points")
fact("chip.memshires", "memory shire", "hierarchy",
     "Eight memory shires, four on the east side and four on the west side of the die, each driving two 16-bit LPDDR4X channels: 16 channels in all.",
     8, "memory shires", f"{DS}, pdf p.30 (§7); {PRM}, pdf p.17 (§1.5)", "spec", page="anatomy",
     anchor="the-memory-shire-leg-91-cycles-plus-12-per-hop")
fact("chip.sram-total", "chip", "memory",
     "140 MB of on-die SRAM (35 shire caches × 4 MB, counting the I/O shire's), each 1 MB block configurable as local L2, a slice of the chip-wide L3, or globally addressable scratchpad.",
     140, "MB", f"{DS}, pdf p.4 (§1); {PRM}, pdf p.486 (§15.3)", "spec",
     note="The I/O shire's cache is 1 MB in the Shire Cache Specification (pdf p.22), which would make it 137 MB.",
     page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("chip.process", "chip", "physical",
     "TSMC 7 nm, over 24 billion transistors, 89 mask layers (Esperanto, Hot Chips 33 and IEEE Micro 2022).",
     24e9, "transistors (lower bound)", f"{CL}:513; docs/findings/01-resources.md:91-104 (R6)", "spec",
     note="External, published by the vendor; not checked on these cards.", page="lowpower")
fact("chip.die-area", "chip", "physical", "Die area 570 mm².", 570, "mm²",
     f"{CL}:513; docs/findings/01-resources.md:234 (R14: Hot Chips 33 slide 20; IEEE Micro 42(3) p.37)", "spec",
     note="External, vendor-published.", page="heat", anchor="die")
fact("chip.die-dims", "chip", "physical",
     "Die about 25.6-25.8 mm east-west by 22.1-22.2 mm north-south (width/height 1.15-1.17), from the published die plot scaled to 570 mm²; the shire grid spans about 86% of the die's width, the rest being the memory shires and their DRAM PHYs down each side (about 1.76 mm per side).",
     25.7, "mm (width)",
     "docs/reports/data/2026-09-24-wire-energy/research/geometry/pitch.json, `scale_from_570mm2.A_black_layout_region` and `.B_symmetric_bottom` (`die_w_mm`, `die_h_mm`, `grid_w_mm`, `memshire_col_w_mm`); heat-per-mm page §'How long is a hop'",
     "inferred", note="Pixel measurement of a die plot; depends on what the 570 mm² covers. Use for proportions only.",
     page="heat", anchor="die")
fact("chip.hop-pitch", "mesh", "physical",
     "Shire tile pitch 3.73 mm east-west and 3.70 mm north-south, so one mesh hop is about 3.72 mm (3.64-3.74 over three readings).",
     3.72, "mm per hop", f"{CL}:340; docs/reports/data/2026-09-24-wire-energy/report.json `inputs.hop_mm`", "inferred",
     note="Kind A (estimate from the die plot) in the claims index.", page="heat", anchor="die")
fact("chip.die-revision", "chip", "physical",
     "The datasheet's package marking example gives die revision A0; the driver reports arch_rev 0 on every card. Whether the lab cards are A0 has not been confirmed by AI Foundry.",
     None, None, f"{DS}, pdf p.34 (Table 10-1); docs/reports/data/2026-09-22-cards/driver_config.json `arch_rev`; {NOTES}:342",
     "spec", card="aifoundry1, aifoundry2, aifoundry3 (arch_rev)", page=None)
fact("chip.advertised-range", "chip", "clocks",
     "Advertised operating range: 300-800 MHz and about 40 W for the open-sourced platform (AI Foundry); Esperanto's papers give 300 MHz to 2 GHz.",
     None, None, f"{INTRO}, pdf p.2; docs/findings/01-resources.md:101-103 (R6)", "spec",
     note="These cards' firmware only offers 600, 700 and 800 MHz (see clock.minion-opps).", page="lowpower")

# ---------------------------------------------------------------- mesh
fact("mesh.grid", "mesh", "topology",
     "The NoC is an 8 × 6 grid of mesh stops: 34 minion shires, 1 PCIe shire, 1 I/O shire and 8 memory shires; the four memory shires on each side leave the grid's corners empty, so there are 44 mesh stops.",
     44, "mesh stops", f"{DS}, pdf p.21 (§4 ET-SoC-1 Mesh Network on Chip)", "spec", page="onchip",
     anchor="where-the-shires-are-a-6-6-mesh")
fact("mesh.logical-map", "mesh", "topology",
     "Measured position of each compute shire on the 6 × 6 grid (marty1885's logical map, x across, y down): y=0: 0 24 9 25 2 11; y=1: 8 16 1 17 10 19; y=2: 3 4 13 14 18 27; y=3: _ 12 21 22 26 _; y=4: _ 20 29 30 15 23; y=5: _ 28 5 6 7 31.",
     None, None,
     "workloads/nocbench/analyze.py:52-60 (`MARTY`, `EMPTY`); " + f"{CL}:383, 412 (map recovered from latency alone in 12 of 12 search restarts on every card)",
     "measured", card=CARDS3,
     note="Built by marty1885's etTopoScan from bandwidth on another card; confirmed by TensorSend latency on all three lab cards. Shire IDs are the firmware's logical IDs.",
     page="onchip", anchor="where-the-shires-are-a-6-6-mesh")
fact("mesh.empty-cells", "mesh", "topology",
     "Four cells of the 6 × 6 map hold no compute shire: (0,3), (0,4), (0,5) and (5,3). They hold the master, spare, PCIe and I/O shires and route traffic too; which cell is which is not established.",
     4, "cells", "workloads/nocbench/analyze.py:60 (`EMPTY`); on-chip communication page §'Where the shires are'",
     "measured", card=CARDS3,
     note="The firmware's comment map (noc_reconfigure.h:76-90) puts PCIe/IO in one row and master/spare in another, but its shire placement matches the measured pairwise distances for only 254 of 1,024 shire pairs, so it cannot be used to label the cells.",
     page="onchip", anchor="where-the-shires-are-a-6-6-mesh")
fact("mesh.orientation", "mesh", "topology",
     "The logical map appears to be the die turned a quarter: in map orientation the memory shires sit above and below the grid, on the die (and in the firmware's naming, 0-3 west, 4-7 east) they are the two side columns.",
     None, None, f"{NOTES}:102-105; anatomy page §1 'Trace one load'", "inferred", page="anatomy",
     anchor="trace-one-load")
fact("mesh.memshire-positions", "memory shire", "topology",
     "Fitted memory-shire positions on the logical map: memory shires 0-3 one step off the top edge at x = 1-4 (y = -1), 4-7 one step off the bottom edge at x = 1-4 (y = 6). Memory shire 2's position is a tie-break (x = 3 or 5 above the grid, or (6,0), fit equally).",
     None, None,
     "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json `decomp.ms_pos`; workloads/memprobe/analyze.py:111-126",
     "measured", card="aifoundry2", note="A fit of DRAM latencies with one constant (91 cycles) and 12 cycles per hop.",
     page="anatomy", anchor="the-memory-shire-leg-91-cycles-plus-12-per-hop")
fact("mesh.grid-consistency", "mesh", "topology",
     "Fitted memory-shire positions (x = 1-4 in the rows above and below the 6 × 6 grid) leave exactly the four corner stops of the 8 × 6 grid empty, as the datasheet says; together they give 44 stops.",
     44, "mesh stops", "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json `decomp.ms_pos`; " + f"{DS}, pdf p.21 (§4)",
     "derived", page="anatomy", anchor="the-memory-shire-leg-91-cycles-plus-12-per-hop")
fact("l3.by-slice", "L3", "latency",
     "L3 hit latency from shire 0 to each of the 32 home slices is exactly 110 + 12 × hops for 0 to 10 hops (110, 122, ... 230 cycles), the median of every pass on each of three cards.",
     230, "cycles (10 hops)", "docs/reports/data/2026-09-26-memprobe-3cards/cards.json `cards.<card>.l3_by_slice.<home>.med` and `.hops`",
     "measured", card=CARDS3, note="Per-slice data the diagram can animate from directly (requester shire 0).",
     page="anatomy", anchor="l3-110-cycles-plus-12-per-hop")
fact("mesh.ring", "mesh", "topology",
     "A ring through all 32 compute shires moving one hop per step: 0 24 9 25 2 11 19 27 18 10 17 14 22 26 15 23 31 7 6 30 29 5 28 20 12 21 13 1 16 4 3 8 (then back to 0).",
     None, None, f"{NOTES}:108-109; on-chip communication page §'Where the shires are'", "derived",
     page="onchip", anchor="where-the-shires-are-a-6-6-mesh")
fact("mesh.id-vs-distance", "mesh", "topology",
     "Shire IDs do not follow the mesh: the next shire by ID is 1-10 hops away, 3.5 on average.",
     3.5, "hops (mean)", f"{NOTES}:105-106; docs/findings/18-on-chip-relay.md:9-10", "derived",
     page="relay", anchor="how-far-the-slab-moves-does-not-change-the-bandwidth")
fact("mesh.hop-latency", "mesh", "latency",
     "Each mesh hop adds 20 ns round trip: 12 minion cycles at 600 MHz (11.99-12.02 fitted on three cards), about 4 mesh cycles each way at 400 MHz, the same in both directions.",
     12, "minion cycles per hop (round trip, 600 MHz)", f"{CL}:381, 403, 411 ({V3R}/lat.json LAT-M3 `row0_slope`; mem.json MEM-P1 `P1_l3_slope`)",
     "measured", card=CARDS3, note="Fixed in ns, so 16 cycles at 800 MHz.", page="onchip",
     anchor="latency-grows-with-distance-except-through-memory")
fact("mesh.shortest-paths", "mesh", "routing",
     "Round trips fit a + b × Manhattan distance on the map over all 496 shire pairs (worst residual 1.1-1.4 cycles), so routes are shortest paths through all 36 cells, the four non-compute cells included. The order in which the mesh routes a request (x first or y first) was not measured.",
     None, None, f"{CL}:381, 412; on-chip communication page §'What the numbers say'; anatomy page §1 ('the order in which the mesh routes a request was not measured')",
     "measured", card=CARDS3, page="onchip", anchor="what-the-numbers-say")
fact("mesh.xy-assumption", "mesh", "routing",
     "The heat-per-mm analysis assumes dimension-ordered XY routing on the logical map (and checks YX); under it, links are shared by 0 / 22 / 32 / 55 / 72% of link-hops at 1 / 2 / 3 / 4 / 6 hops in the all-pairs traffic.",
     None, None, "workloads/enercat/analyze_wire.py:38, 149-176; " + f"{CL}:348 (WIRE `checks.link_sharing`)",
     "inferred", note="An analysis assumption, not a documented routing rule.", page="heat", anchor="contention")
fact("mesh.single-attach", "shire", "topology",
     "Each shire meets the mesh at a single point: minion 31 of each shire gives the same round trips as minion 0.",
     1, "mesh stop per shire", "on-chip communication page §'What the numbers say'", "measured", card=CARDS3,
     page="onchip", anchor="what-the-numbers-say")
fact("mesh.clock", "mesh", "clocks",
     "The NoC runs at 400 MHz on these cards (every telemetry sample). The design's NoC clock is 500 MHz (from PLL2 in the I/O shire), and the firmware's DVFS table allows 300-500 MHz.",
     400, "MHz", f"{TEL}, field `mhz.noc`; {MSD}, pdf p.12 (Table 2, clk__noc); {EP}/device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c:134-135",
     "measured", card="aifoundry2 (aifoundry3 set to 400 MHz by its boot service)", page="memhier",
     anchor="load-latency-against-working-set-size")
fact("mesh.voltage", "mesh", "voltages",
     "NoC rail: set point 485 mV, 484-485 mV on die (per-shire 483-486 mV at idle).",
     485, "mV", f"{TEL}, fields `reg_mv.noc`, `die_mv.noc`; {CL}:41", "measured", card="aifoundry2",
     page="heat", anchor="method")
fact("mesh.port-width", "mesh", "links",
     "The shire cache's mesh master port is 512 bits wide (one 64-byte line per beat); a shire has four mesh lanes and a line goes to lane PA[7:6], so consecutive lines on one lane are 256 bytes apart; a flit carries at least one 64-byte line.",
     512, "bits", "external/core-et/rtl/inc/axi_defines.vh:43 (`SC_MESH_MASTER_AXI_DATA_SIZE 512`); docs/findings/01-resources.md:238-239 (R14); docs/findings/20-heat-per-mm.md:117-122",
     "spec", note="The inter-router link width and flit size of the NoC itself are not documented in the sources.",
     page="heat", anchor="lanes")
fact("mesh.memshire-port", "memory shire", "links",
     "Each memory shire has three NoC ports (memory traffic, global-atomic responses, ESR accesses); the memory port is a 512-bit AXI slave, and the NoC delivers at most 32 GB/s to a memory shire, almost twice the sustained rate of its two LPDDR4X channels.",
     32, "GB/s per memory shire", f"{DS}, pdf p.30 (§7.1.1)", "spec", page="anatomy",
     anchor="the-memory-shire-leg-91-cycles-plus-12-per-hop")
fact("mesh.1kb-knee", "mesh", "latency",
     "With 1 KB messages a round trip adds 12 cycles per hop up to 5 hops and 36 cycles (27-36) per hop beyond, as if the sender had a limited number of packets in flight.",
     36, "cycles per hop beyond 5 hops", f"{CL}:382, 412 ({V3R}/lat.json LAT-N2 `c32_slope_to5`, `c32_slope_beyond5`)",
     "measured", card=CARDS3, page="onchip", anchor="message-size-and-bandwidth")
fact("mesh.hop-energy-wire", "mesh", "energy",
     "One mesh hop costs 0.67 pJ per byte on zeros [0.62-0.73] and 1.80 pJ/B on random data [1.72-1.91] on board power (fit over 1-8 hops).",
     1.80, "pJ/B per hop (random data)", "docs/energy-manual/04a-fine-grain.md:18", "measured", card=CARDS3,
     page="energy", anchor="finer-grain-wires-lines-rows-and-the-leakage-of-the-arrays")
fact("mesh.bit-mm", "mesh", "energy",
     "A random bit moved one mm across the mesh costs 37 fJ on the mesh rail (25 of it data-dependent) and 47 fJ on board power when links are free (0.485 V); 53 and 79 fJ on a loaded mesh where flows share links.",
     36.7, "fJ per bit·mm (mesh rail, free links)",
     "docs/reports/data/2026-09-24-wire-energy/report.json `headline[\"uncontended/noc_rail\"|\"uncontended/board\"|\"loaded/noc_rail\"|\"loaded/board\"].random_bit_total`; docs/findings/20-heat-per-mm.md:9-12; " + f"{CL}:444 (V3 free links per card)",
     "measured", card=CARDS3, page="heat", anchor="distance")
fact("mesh.debug-noc", "mesh", "topology",
     "A separate Debug NoC shares the main NoC's clock with its own reset.", None, None,
     f"{MSD}, pdf p.7 (Table 1) and pdf p.17", "spec", page=None)
fact("mesh.no-counters", "mesh", "observability",
     "There are no NoC performance counters in the PRM, the firmware or core-et; mesh transit is inferred from latency differences.",
     None, None, f"{CAD}:272-279", "spec", page="hub", anchor="ladder")

# ---------------------------------------------------------------- shire
fact("shire.composition", "shire", "hierarchy",
     "A minion shire is 4 neighbourhoods = 32 minions = 64 harts, a four-bank 4 MB shared L2/L3/scratchpad cache, a mesh stop, a crossbar between them, and an uncacheable (UC) block with fast local barriers, fast credit counters, inter-processor interrupts and global atomics.",
     32, "minions", f"{DS}, pdf p.5 (§2.1); {MOV}, pdf p.4 (slide 5)", "spec", page="hub", anchor="terms")
fact("shire.cache-geometry", "shire cache", "memory",
     "The shire cache is 4 MB: 4 banks × 1 MB, each bank 4 sub-banks; L2 and L3 are 4-way set-associative, 64-byte lines, write-back and write-allocate, with SECDED ECC on tags, data and state.",
     4, "MB per shire", f"{SCS}, pdf p.8-9 (§1.1: 'The POR for the first SoC is 4M/Shire, 4 banks/Shire, 4 sub-banks/bank'); {DS}, pdf p.13 (§2.1.3.1)",
     "spec", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("shire.partition-m0", "shire cache", "memory",
     "Mode M0, the reset mode and the one these cards run: per shire 2.5 MB scratchpad, 512 KB L2, 1 MB L3 slice; over 32 shires 80 MB scratchpad, 16 MB L2, 32 MB L3.",
     2.5, "MB scratchpad per shire",
     f"{SCS}, pdf p.21-22 (Tables 6-7, 'The chip will come out of reset in mode M0'); external/core-et/rtl/shire/esr/esr_cache_bank.v:106 ('default cache config mode = M0'); {MOV}, pdf p.4",
     "spec", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("shire.partition-measured", "shire cache", "memory",
     "The driver reports L2 16,384 KB, L3 32,768 KB and scratchpad 81,920 KB in total on every card, i.e. mode M0; line size 64 B, 4 L2 banks.",
     81920, "KB scratchpad (chip)", "docs/reports/data/2026-09-22-cards/driver_config.json, fields `l2_kb`, `l3_kb`, `scp_kb`, `line_b`, `l2_banks`",
     "measured", card="aifoundry1 (both cards), aifoundry2, aifoundry3", page="memhier",
     anchor="the-hierarchy-as-a-spec-sheet")
fact("shire.other-modes", "shire cache", "memory",
     "Other defined partitions (chip totals, scratchpad / L2 / L3): M1 0/64/64 MB, M2 0/124/4, M3 0/128/0, M4 128/0/0, M5 64/64/0; software can change mode only after evicting and stopping the minions.",
     None, None, f"{SCS}, pdf p.21-22 (Table 6)", "spec", page=None)
fact("shire.crossbar", "shire cache", "links",
     "A full request crossbar joins the 4 neighbourhoods and the RBOX to the 4 banks and the UC block; each bank has five 512-bit L2 input ET-Link buses, one 512-bit L3 input bus from the NoC, and two outputs toward the NoC: 'To L3' and 'To System' (main memory).",
     512, "bits per bus", f"{SCS}, pdf p.10 (§1.1) and pdf p.30 (§2.1)", "spec", page="anatomy", anchor="the-ladder-one-load-at-a-time")
fact("shire.neigh-link", "neighbourhood", "links",
     "The 8 minions of a neighbourhood share one 512-bit ET-Link bus to the shire cache and UC block; responses reach a minion over a 256-bit bus (a 512-bit line takes two cycles).",
     512, "bits", f"{MSD}, pdf p.11 (§3.2); {NMAS}, pdf p.22-23", "spec", page=None)
fact("shire.sc-latency-spec", "shire cache", "latency",
     "Idle shire-cache latencies in shire clocks, crossbars included: read-buffer hit 10, L2 read hit 21, L2 miss 34 + NoC and L3/memory, L3 read hit 30 (at the slave), L3 miss 42 + NoC and memory.",
     21, "shire clocks (L2 read hit)", f"{SCS}, pdf p.11 (Table 1)", "spec",
     note="Measured load-to-use is 36 (read buffer) and 47 (L2) minion cycles; the difference is the minion pipeline, L1 miss and neighbourhood path.",
     page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("shire.bank-queues", "shire cache", "microarchitecture",
     "Per bank: a 64-entry request queue (up to 21 entries reserved for L3-slave requests), an 8-entry read buffer and a 32-entry write-around coalescing buffer; L3-slave requests take priority over local L2 requests.",
     64, "request-queue entries per bank", f"{CAD}:458-465; {SCS}, pdf p.9 (coalescing buffer, 32 entries per bank) and pdf p.36 (arbitration)",
     "spec", page="hotline", anchor="the-thing-that-actually-starves")
fact("shire.l2-bw-spec", "L2", "bandwidth",
     "Spec L2 bandwidth: four banks × 64 B = 256 B per shire-cycle, i.e. 8 B per minion-cycle, 4.9 TB/s on 1,024 minions at 600 MHz.",
     256, "B per shire-cycle", f"{CL}:486; {NOTES}:249; {SCS}, pdf p.11 ('Read Bandwidth')", "derived",
     page="ridge", anchor="ridge-points-by-level")
fact("shire.l2-bw-measured", "L2", "bandwidth",
     "Measured L2 streaming bandwidth: 2.45 TB/s on 1,024 minions at 600 MHz = 128 B per shire-cycle = 4.0 B per minion-cycle, half the banks' 256 B.",
     2.45, "TB/s", f"{CL}:370, 486 (docs/reports/data/2026-09-18-memhier-aifoundry2/energy*/runs.jsonl, 600 MHz launches)",
     "measured", card="aifoundry2 (re-run on aifoundry2 and aifoundry3 on 23 Sep, within 1%)", page="memhier",
     anchor="the-hierarchy-as-a-spec-sheet")
fact("shire.clock", "shire", "clocks",
     "Each minion shire has its own PLL; the shire cache and minions run on the shire clock (the neighbourhood clock is the same clock shifted 180°), outside the NoC's clock domain. Design value 1,000 MHz.",
     1000, "MHz (design)", f"{MSD}, pdf p.4 and pdf p.12 (Table 2: o_clkpll_shire, o_clkpll_neigh)", "spec",
     note="Measured consequence: on-chip latencies (L1, L2, own scratchpad) stay fixed in cycles when the clock moves, while L3 and DRAM are fixed in ns.",
     page="memhier", anchor="load-latency-against-working-set-size")
fact("shire.voltage-domains", "shire", "voltages",
     "A shire spans several voltage domains separated by level shifters and FIFOs: minions on the low-voltage minion rail, the SRAM arrays (shire cache, and the I-cache data memory, placed in the shire channel because it must run at high voltage) on the SRAM rail, the mesh stop on the NoC rail.",
     None, None, f"{MSD}, pdf p.4, p.10 (§3.1) and p.18 (§5); docs/research/why-low-power.md:23-28 (R6)", "spec",
     page="lowpower")
fact("shire.sensors", "shire", "observability",
     "One temperature sensor and one process detector per minion shire (plus the I/O shire), and 3 voltage sense points per minion shire; the host sees only the mean temperature of the 34 minion-shire sensors, in whole degrees.",
     34, "temperature sensors averaged", f"{PRM}, pdf p.17 (§1.6: 36 TS and 36 PD); docs/findings/01-resources.md:212-215 (R13: 35 live); {CL}:36, 331",
     "spec", note="The PRM counts 36 sensors of each kind; the firmware has 35 live (34 minion shires + I/O shire). Per-shire temperature is not exported.",
     page="hub", anchor="power")

# ---------------------------------------------------------------- neighbourhood
fact("neigh.composition", "neighbourhood", "hierarchy",
     "A neighbourhood is 8 minions sharing a 32 KB L1 instruction cache (128 sets × 4 ways × 64 B), two L0 micro-I-caches (each shared by 4 minions, 16 fully associative 512-bit entries) and a 12-counter PMU.",
     8, "minions", f"{DS}, pdf p.11-13 (§2.1.2); {MOV}, pdf p.3 (slide 4)", "spec", page="hub", anchor="terms")
fact("neigh.pmu", "neighbourhood", "observability",
     "The neighbourhood PMU implements 12 counters: 6 shared by the even harts (hart 0 of each minion) and 6 by the odd harts; mcycle and minstret read 0.",
     12, "counters", f"{PRM}, pdf p.10 and p.12 (§1.3, §1.3.2)", "spec", page="hub", anchor="ladder")
fact("neigh.fln-edges", "neighbourhood", "fast local network",
     "The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.",
     7, "edges per neighbourhood", f"{NMAS}, pdf p.26 (§4.7 Fast Local Messaging Network)", "spec",
     page="onchip", anchor="inside-a-shire-only-the-tree-edges-are-fast")
fact("neigh.fln-rtt", "neighbourhood", "latency",
     "A 32 B TensorSend round trip takes 68 cycles (113 ns) on a fast-network edge (28 pairs per shire) and 114-115 cycles (190 ns) between any other two minions of a shire, same neighbourhood or not.",
     68, "cycles (round trip, 600 MHz)", f"{CL}:380 ({V3R}/lat.json; DATANOC/intra-pingpong*.jsonl)", "measured", card=CARDS3,
     page="onchip", anchor="inside-a-shire-only-the-tree-edges-are-fast")
fact("neigh.fln-latency-spec", "neighbourhood", "fast local network",
     "Messages on the fast local network see a 3-cycle response-path latency and take priority over regular fill responses; every other message leaves the neighbourhood and returns through the shire crossbar.",
     3, "cycles", f"{NMAS}, pdf p.22-23 and p.26", "spec", page="onchip", anchor="inside-a-shire-only-the-tree-edges-are-fast")
fact("neigh.coop-tload", "neighbourhood", "tensor",
     "Cooperative TensorLoad: identical tensor-load requests from minions (across the neighbourhoods of a shire) are synchronised and coalesced into one memory request; cooperative TensorStore combines pairs or quads of minions writing one line.",
     None, None, f"{PRM}, pdf p.273-274 (§9.3.1.1, §9.3.5.1); {MOV}, pdf p.3", "spec", page=None)
fact("neigh.ptw", "neighbourhood", "microarchitecture",
     "Two page-table walkers per neighbourhood are drawn in the architecture but not implemented in the first silicon revision.",
     2, "PTWs (not implemented)", f"{DS}, pdf p.11 (footnote 1)", "spec", page=None)

# ---------------------------------------------------------------- minion core
fact("minion.isa", "minion", "ISA",
     "The ET-Minion is a dual-threaded (2 harts), in-order, single-issue RV64IMFC core with Zicsr and Zifencei and machine/supervisor/user modes; kernels run in U-mode.",
     2, "harts per minion", f"{MIND}, pdf p.5 (§2); {DS}, pdf p.7 (§2.1.1); {INTRO}, pdf p.7", "spec",
     page="hub", anchor="terms")
fact("minion.no-divide", "minion", "ISA",
     "No hardware divide or square root in U-mode: fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, 64-bit float conversion and reading the cycle CSR; 161 of the instructions tried execute in U-mode, 13 trap.",
     13, "trapping instructions", f"{CL}:278, 296 (workloads/enercat/enercat_modes.json)", "measured",
     card="aifoundry2, aifoundry3", page="energy", anchor="every-instruction-the-core-executes")
fact("minion.vpu", "vector unit", "microarchitecture",
     "The vector unit has 8 identical 32-bit lanes in lockstep; the 32 FP registers f0-f31 are 256 bits wide (8 × fp32) per hart. Each lane has one FMA unit (one fp32 or two fp16 multiply-adds per cycle), two integer multiply-add units (four int8 multiply-accumulates each), one integer unit and one transcendental unit (exp2, log2, reciprocal).",
     8, "lanes", f"{DS}, pdf p.8 (§2.1.1.2); {VPU}, pdf p.11 (§2) and p.33 (§2.2.5.2: 16 TIMA lanes); {MOV}, pdf p.2 (slide 3)",
     "spec", page="ridge", anchor="the-compute-ceilings")
fact("minion.vpu-regs", "vector unit", "microarchitecture",
     "Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.",
     32, "vector registers per hart (32 B each)", f"{VPU}, pdf p.11; {DS}, pdf p.8-9", "spec", page="onchip",
     anchor="every-primitive-against-a-gpu")
fact("minion.vpu-pipeline", "vector unit", "microarchitecture", "The VPU pipeline has eight stages.", 8, "stages",
     f"{VPU}, pdf p.12 (§2.1)", "spec", page=None)
fact("minion.l1-port", "L1 data cache", "bandwidth",
     "The data cache can feed one register-file entry of all 8 VPU lanes (32 bytes) in a single cycle.",
     32, "B per cycle", f"{MIND}, pdf p.6", "spec", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("minion.peak", "tensor unit", "compute",
     "Tensor peak per minion-cycle: 16 fp32 FLOP, 32 fp16 FLOP, 128 int8 OP (int8 is 8× fp32 because the integer units are separate and twice as many).",
     16, "fp32 FLOP per minion-cycle", f"{CL}:485 (scripts/ridge-points.py `PEAK`; Minion VPU Specification §2)", "spec",
     page="ridge", anchor="the-compute-ceilings")
fact("minion.chip-peak-600", "chip", "compute",
     "Chip tensor peak on 1,024 minions at 600 MHz: 9.83 TFLOP/s fp32, 19.7 TFLOP/s fp16, 78.6 TOP/s int8.",
     9.83, "TFLOP/s fp32", f"{CL}:485; {NOTES}:244-245", "derived", page="ridge", anchor="the-compute-ceilings")
fact("minion.tensor-measured", "tensor unit", "compute",
     "A tensor-unit matmul on 1,024 minions at 600 MHz sustains 9.51 TFLOP/s fp32, 19.02 fp16 and 71.77 TOP/s int8: 529 cycles per 16×16×K op for fp32/fp16 (512 ideal) and 280.4 for int8 (256 ideal), every result exact.",
     9.51, "TFLOP/s fp32", f"{CL}:417 ({V3R}/mmb.json MMB-a, MMB-b)", "measured", card=CARDS3,
     page="matmul", anchor="three-card-table")
fact("minion.tensorfma-546", "tensor unit", "compute",
     "With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.",
     546, "cycles per op", f"{CL}:31-32, 414 ({V3R}/lat.json LAT-S1)", "measured", card=CARDS3, page="horace")
fact("minion.tensor-shape", "tensor unit", "ISA",
     "A TensorFMA computes C[M][N] += A[M][K] · B[K][N] with M, N ≤ 16 and K ≤ 64 / (bytes per element): A from the L1 scratchpad, B streamed through TenB, C accumulated in hart 0's vector registers (int8 in TenC). One fp32 op is 4,096 multiply-adds.",
     4096, "multiply-adds per fp32 op", f"{PRM}, pdf p.264 (§9); {NOTES}:292-294", "spec", page="matmul")
fact("minion.tenb-tenc", "tensor unit", "microarchitecture",
     "TenB is virtually 16 registers × 64 B (1 KiB), physically much smaller, and only streams loaded data to a consumer; TenC is 16 × 64 B (1 KiB) of int32 accumulators visible only to integer tensor multiplies.",
     1024, "bytes (each, logical)", f"{PRM}, pdf p.264", "spec", page=None)
fact("minion.tensor-hart0", "tensor unit", "ISA",
     "Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.",
     None, None, f"{PRM}, pdf p.264", "spec", page="hub", anchor="terms")
fact("minion.tensor-csrs", "tensor unit", "ISA",
     "Tensor instructions are CSR writes that run asynchronously: tensor_fma 0x801, tensor_load 0x83F, tensor_load_l2 (TensorLoadL2Scp) 0x85F, tensor_quant 0x806, tensor_store 0x87F, tensor_reduce 0x800 (TensorSend/Recv/Broadcast/Reduce), tensor_wait 0x830.",
     None, None, f"{PRM}, pdf p.272-274 (§9.3)", "spec", page=None)
fact("minion.tensorload", "tensor unit", "data path",
     "TensorLoad reads up to 16 rows of 64 contiguous bytes (64 B aligned, row stride in x31) from memory into consecutive L1-scratchpad lines, bypassing the L1 data cache; a mask can skip rows.",
     16, "rows of 64 B per instruction", f"{PRM}, pdf p.273 and p.275 (§9.3.1, TensorLoad)", "spec",
     page="sparse")
fact("minion.tensor-cache-path", "tensor unit", "data path",
     "Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.",
     None, None, "docs/energy-manual/04-bytes-memory.md:21, 38",
     "inferred", note="Stated by the energy manual; the PRM confirms only that TensorLoad bypasses the L1 data cache.",
     page="energy", anchor="reads-and-writes-measured-together")
fact("minion.tensorsend", "tensor unit", "messaging",
     "TensorSend moves COUNT consecutive vector registers (32 B each, up to 127, wrapping past f31: about 4 KB) from the issuing hart into hart 0 of a target minion anywhere on the chip; the receiver's TensorRecv can add, max or min the data into its registers at no extra cost.",
     127, "registers per message (max)", f"{PRM}, pdf p.272 and p.311-314; on-chip communication page (headline); {CL}:380-381",
     "spec", page="onchip", anchor="every-primitive-against-a-gpu")
fact("minion.tensorsend-rtt", "tensor unit", "latency",
     "TensorSend round trip between shires: 150 + 12.02 cycles per mesh hop (250 ns + 20 ns/hop at 600 MHz), r² 0.9999 over all 496 shire pairs.",
     150, "cycles + 12.02/hop", f"{CL}:381, 412 ({V3R}/lat.json LAT-N2 `pingpong_fit`)", "measured", card=CARDS3,
     page="onchip", anchor="latency-grows-with-distance-except-through-memory")
fact("minion.combine-free", "tensor unit", "messaging",
     "Combining on receive (fp32/int32 add, max, min) adds 0 cycles to a round trip.",
     0, "cycles", f"{NOTES}:114; on-chip communication page table", "measured", card=CARDS3, page="onchip",
     anchor="every-primitive-against-a-gpu")
fact("minion.one-ready-bit", "tensor unit", "messaging",
     "The hardware keeps one peer-to-peer ready bit per minion, not one per partner: a minion receiving from two TensorSend partners at once hangs its hart permanently (the card then needs a reset).",
     1, "ready bit per minion", f"{NOTES}:124-128 (core-et dcache_reduce.v `partner_ready_peer`); {CL}:257",
     "spec", note="sys_emu tracks every partner separately and does not reproduce the hang.", page="onchip",
     anchor="a-trap-one-ready-flag-per-minion")
fact("minion.msg-cost", "tensor unit", "latency",
     "A one-way message stream costs a fixed 40 / 86 / 135 / 224 cycles per message plus 2.3 / 4.0 / 3.0 / 4.6 cycles per 32 B register on the fast network / shire crossbar / mesh at 1 hop / mesh at 10 hops.",
     None, None, "on-chip communication page §'Message size and bandwidth'", "measured", card=CARDS3,
     page="onchip", anchor="message-size-and-bandwidth")
fact("minion.link-bw", "tensor unit", "bandwidth",
     "One link with 1 KB messages: 5.3 GB/s on the fast network, 2.9 through the shire crossbar, 2.7 over one mesh hop, 1.8 over ten (4 KB messages: 7.2 / 4.1 / 4.7 / 2.9).",
     5.3, "GB/s (fast network, 1 KB)", "on-chip communication page §'Message size and bandwidth'", "measured",
     card=CARDS3, page="onchip", anchor="message-size-and-bandwidth")
fact("minion.l1d", "L1 data cache", "memory",
     "Each minion has a private 4 KB L1 data cache: 16 sets × 4 ways × 64 B lines, not coherent with any other cache, writing back whole 64-byte lines.",
     4, "KB", f"{MOV}, pdf p.1 (slide 2); {DS}, pdf p.9 (§2.1.1.5)", "spec", page="memhier",
     anchor="the-hierarchy-as-a-spec-sheet")
fact("minion.l1-modes", "L1 data cache", "memory",
     "Three L1 modes (mcache_control D1Split, ScpEnable): shared (both harts, all sets); split (hart 0 sets 0-7, hart 1 sets 14-15); scratchpad (hart 0 sets 12-13, hart 1 sets 14-15, sets 0-11 become a 3 KB = 48-line tensor scratchpad).",
     3, "KB L1 scratchpad", f"{PRM}, pdf p.245-246 (§8.3.1, Table 8.4)", "spec",
     note="The Minion Overview slide draws split mode as 2 KB per hart; the PRM table is followed here.",
     page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("minion.l1-firmware", "L1 data cache", "memory",
     "The firmware puts every minion's L1 in scratchpad mode before each launch, leaving each hart 512 B of data cache (2 sets × 4 ways × 64 B).",
     512, "B per hart", f"{NOTES}:84-86; {CAD}:446-447 (fw MachineMinion/src/syscall.c:348-420)", "spec",
     page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("minion.miss-handlers", "L1 data cache", "microarchitecture",
     "Two miss handlers per minion, so at most 2 outstanding cacheable line misses; tensor loads keep up to 4 L2 transfers in flight; there is no prefetcher.",
     2, "outstanding misses", f"{CAD}:445-450 (core-et dcache_defines.vh)", "spec", page=None)
fact("minion.l1-latency", "L1 data cache", "latency",
     "L1 hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); hart 1 pays 3 more cycles on misses.",
     5.25, "cycles", f"{CL}:409 ({V3R}/lat.json LAT-M1)", "measured", card=CARDS3, page="memhier",
     anchor="the-hierarchy-as-a-spec-sheet")
fact("minion.l1-bw", "L1 data cache", "bandwidth",
     "L1 bandwidth on 1,024 minions at 600 MHz: 6.2 TB/s in the memory-hierarchy probe's loop, 14.5 TB/s with the catalogue's unrolled 32 B vector loads.",
     6.2, "TB/s", f"{CL}:370; docs/energy-manual/04-bytes-memory.md:11, 21", "measured",
     card="aifoundry2 (6.2); three cards (14.5)", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("minion.l1-energy", "L1 data cache", "energy",
     "An L1 hit costs 0.75 pJ per byte in the memory-hierarchy loop [0.62-0.88], 0.54 pJ/B on random data with unrolled 32 B loads.",
     0.75, "pJ/B", "docs/energy-manual/04-bytes-memory.md:25, 11 (docs/reports/data/2026-09-23-energy-manual/reruns.json `levels_pj_per_byte.l1`)",
     "measured", card=CARDS3, page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("minion.power-awake", "minion", "power",
     "An awake minion running an integer loop on one hart costs about 1.9 mW (both harts about 3.0 mW); on a random-data fp32 matmul a minion draws about 26.5 mW above idle (aifoundry2).",
     26.5, "mW per minion (fp32 matmul, random)", "docs/energy-manual/02-awake.md:9-14", "measured", card=CARDS3,
     page="energy", anchor="a-core-that-is-awake")
fact("minion.energy-mac", "tensor unit", "energy",
     "Energy per multiply-add above idle, random operands: fp32 5.78 pJ [5.35-6.13], fp16 2.59, int8 0.295 (TensorFMA); a vector fmadd.ps lane costs 7.0 pJ.",
     5.78, "pJ per fp32 MAC", "docs/energy-manual/03-instructions.md:31, 44, 48, 51", "measured", card=CARDS3,
     page="energy", anchor="the-tensor-unit-per-multiply-add")
fact("minion.vector-rate", "vector unit", "compute",
     "A simple vector-FMA loop reaches only about 1.5 lane-FMAs per cycle per minion; the best published vector-unit matmul is 2.94 TFLOP/s at 650 MHz (FOSDEM 2026), against the tensor unit's 9.5.",
     1.5, "lane-FMAs per cycle per minion", f"{NOTES}:152-153, 274; ridge-points page §'The compute ceilings'", "measured",
     card="aifoundry3 (the loop); FOSDEM figure external", page="sparse")
fact("minion.sleep-unused", "minion", "power",
     "The minion's sleep and isolation ports (nsleepin, iso_enable, nsleepout) are marked 'not used'; in the open Erbium RTL they are tied off and no firmware drives them. Idle cores are clock-gated, not power-gated.",
     None, None, f"{MIND}, pdf p.7 (interfaces table); {CL}:177-179", "spec", page="dvfs",
     anchor="the-leakage-suppression-transistors")

# ---------------------------------------------------------------- memory levels (published values)
fact("l2.latency", "L2", "latency",
     "L2 hit (and own-shire scratchpad hit): 47 cycles load-to-use, 78 ns at 600 MHz; L2 read-buffer hit 36 cycles (60 ns). On hart 1 the same loads take 50 and 39 cycles.",
     47, "cycles", f"{CL}:366, 409 ({V3R}/lat.json LAT-M1)", "measured", card=CARDS3, page="memhier",
     anchor="the-hierarchy-as-a-spec-sheet")
fact("l2.read-buffer", "L2", "microarchitecture",
     "Each L2 bank has an 8-line read buffer (2 KB per shire) that serves repeated reads of a clean line without touching the SRAM.",
     8, "lines per bank", f"{NOTES}:72; {SCS}, pdf p.9", "spec", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("l2.private", "L2", "memory",
     "The L2 partition is shared by the 32 minions of its shire and not by other shires: an independent L2 per shire (512 KB; 16 MB chip).",
     512, "KB per shire", f"{DS}, pdf p.13 (§2.1.3.1)", "spec", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("l2.decode", "L2", "address map",
     "L2 address decode: offset PA[5:0], bank PA[7:6], sub-bank PA[9:8], set from PA[10] up (L2 set bits are PA[19:10] on ET-SoC-1).",
     None, None, f"{SCS}, pdf p.23-24 (§1.4.1.1); {CAD}:378", "spec", page="anatomy", anchor="trace-one-load")
fact("l2.energy", "L2", "energy", "Reading from L2 costs 3.1 pJ per byte above idle [1.4-5.0].", 3.1, "pJ/B",
     "docs/energy-manual/04-bytes-memory.md:26 (reruns.json `levels_pj_per_byte.l2`)", "measured", card=CARDS3,
     page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("scp.local", "scratchpad", "latency",
     "Own-shire L2 scratchpad: 47 cycles like L2, 2.46 TB/s on 1,024 minions at 600 MHz, 2.25 pJ/B when it holds zeros and 4.40 pJ/B when it holds random data.",
     2.46, "TB/s", f"{CL}:366, 370; docs/energy-manual/04-bytes-memory.md:29-30", "measured", card=CARDS3,
     page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("scp.remote", "scratchpad", "latency",
     "Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns), the same in both directions; 0.96 TB/s streaming from the shire 16 IDs away (2.1 hops on average) at 5.1 pJ/B (zeros) to 11.8 pJ/B (random).",
     99.84, "cycles + 12.00/hop", f"{CL}:411 ({V3R}/lat.json LAT-M3), 370; docs/energy-manual/04-bytes-memory.md:31-32",
     "measured", card=CARDS3, page="memhier", anchor="scratchpad-latency-across-the-mesh")
fact("scp.format0", "scratchpad", "address map",
     "Scratchpad address, format 0 (bit 30 = 0): 0x80000000 + (shire << 23) + offset, shire ID in bits 29:23, offset in bits 22:0; shire ID 0x7F means the requester's own shire. A request whose shire field is not the local shire goes out over the to_l3 mesh interface to the target shire.",
     None, None, f"{PRM}, pdf p.486 (§15.3); {SCS}, pdf p.10, p.24 (§1.4.1.3); {EP}/et-common-libs/include/system/layout.h:71-76; {NOTES}:88",
     "spec", page="memhier", anchor="scratchpad-latency-across-the-mesh")
fact("scp.format1", "scratchpad", "address map",
     "Scratchpad address, format 1 (bit 30 = 1, minions only): the shire ID sits in bits 29:28 and 10:6, so consecutive 64-byte lines land in different shires' scratchpads.",
     None, None, f"{PRM}, pdf p.486 (§15.3)", "spec", page=None)
fact("scp.size", "scratchpad", "memory",
     "Each shire's scratchpad is 2.5 MB (0x280000 in the firmware); 80 MB over the 32 compute shires.",
     2.5, "MB per shire", f"{EP}/et-common-libs/include/system/layout.h:73; {SCS}, pdf p.22 (Mode 0)", "spec",
     page="relay")
fact("scp.offset0", "scratchpad", "traps",
     "Offset 0 of a shire's scratchpad faults; a global atomic through the local-scratchpad ID 0x7F is a bus error.",
     None, None, f"{CL}:231, 256", "measured", card="aifoundry2", page="relay",
     anchor="method-and-what-is-not-established")
fact("l3.latency", "L3", "latency",
     "L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.",
     110, "cycles + 12/hop", f"{CL}:367, 403, 410 ({V3R}/mem.json MEM-P1; lat.json LAT-M2)", "measured", card=CARDS3,
     page="anatomy", anchor="l3-110-cycles-plus-12-per-hop")
fact("l3.home", "L3", "address map",
     "A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).",
     None, None,
     f"{SCS}, pdf p.24 (§1.4.1.2) and p.26-27 (§1.4.3); external/core-et/rtl/shire/esr/esr_cache_bank.v:88-103; {CAD}:373-377; memprobe: 1,500 lines, all but 2 within ±4 cycles of 110 + 12·hops(requester, PA[10:6]) ({NOTES}:165)",
     "measured", card=CARDS3, note="The IDs are virtual shire IDs; a spare-shire remap would move them (NOC_Remap_Shires).",
     page="anatomy", anchor="trace-one-load")
fact("l3.bank", "L3", "address map",
     "Inside the home slice: L3 bank PA[12:11], sub-bank PA[14:13], set above.",
     None, None, f"{SCS}, pdf p.24 (§1.4.1.2) and p.27 (Table 8, swizzle0); {CAD}:375", "spec", page=None)
fact("l3.capacity", "L3", "memory",
     "The L3 is 32 MB: a 1 MB slice in each of the 32 compute shires, shared chip-wide and memory-side. The 5-bit home field means the master shire's cache is not an L3 home.",
     32, "MB", f"{DS}, pdf p.13; driver_config.json `l3_kb` 32768; {SCS}, pdf p.26 (five shire-ID bits for a 32-shire configuration)",
     "derived", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("l3.bw", "L3", "bandwidth", "L3 streaming bandwidth: 0.98 TB/s on 1,024 minions at 600 MHz.", 0.98, "TB/s",
     f"{CL}:370", "measured", card="aifoundry2 (re-run on aifoundry2 and aifoundry3, within 1%)", page="memhier",
     anchor="the-hierarchy-as-a-spec-sheet")
fact("l3.energy", "L3", "energy", "Reading from L3 costs 14.7 pJ per byte above idle [7.1-20.5].", 14.7, "pJ/B",
     "docs/energy-manual/04-bytes-memory.md:27 (reruns.json `levels_pj_per_byte.l3`)", "measured", card=CARDS3,
     page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("l3.writearound", "L3", "data path",
     "Write-around stores coalesce in the L2's buffer and flush to the L3 once all four 16-byte qwords of a line are written (or on an explicit flush).",
     4, "qwords per line", f"{SCS}, pdf p.9", "spec", page=None)
fact("mem.coherence", "chip", "memory model",
     "No coherence between caches: L1 data caches are not coherent; '…L' memory ops go straight to the local shire's L2, '…G' ops (and global atomics) go to the address's L3 home, and U-mode cache ops (EvictVA, FlushVA, PrefetchVA) move lines explicitly.",
     None, None, f"{NOTES}:44-60; {CAD}:484 (core-et dcache_miss_handler.v:492-511)", "spec", page="hotline")
fact("mem.global-atomic", "L3", "atomics",
     "A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.",
     10.0, "cycles per contended atomic", f"{CL}:221, 223; docs/findings/17-hot-line.md:10-16", "measured",
     card="aifoundry2, aifoundry3", page="hotline", anchor="the-thing-that-actually-starves")

# ---------------------------------------------------------------- DRAM
fact("dram.channels", "DRAM", "memory",
     "16 LPDDR4X channels of 16 bits (256 bits in all): each memory shire drives two channels, and four LPDDR4X packages of four channels (64 bits each) sit on the card.",
     16, "channels", f"{PRM}, pdf p.17 (§1.5); {CARD}, pdf p.3; {DS}, pdf p.4",
     "spec", note="The datasheet (pdf p.30) says two 16-bit PHYs share one 32-bit controller per memory shire; the firmware programs two uMCTL2 controller instances per memory shire (docs/research/counters-and-dram.md:286-287).",
     page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("dram.capacity", "DRAM", "memory",
     "32 GB of LPDDR4X on these V3 cards (Micron part): 2 GB per channel; the chip supports 8 to 32 GB.",
     32, "GB", f"{CARD}, pdf p.1; {CAD}:289; {PRM}, pdf p.342 and p.552; {DS}, pdf p.30", "spec", page="memhier",
     anchor="the-hierarchy-as-a-spec-sheet")
fact("dram.rate-datasheet", "DRAM", "bandwidth",
     "Datasheet rate: 4,266 MT/s, printed as 133 GB/s; 16 × 2 B × 4.266 GT/s is 136.5 GB/s (Esperanto's papers say 137).",
     136.5, "GB/s", f"{DS}, pdf p.4 (§1); {NOTES}:20; {CL}:514", "spec", page="ridge", anchor="ridge-points-by-level")
fact("dram.rate-card", "DRAM", "clocks",
     "The firmware hard-codes the 933 MHz DDR configuration on every card (controller clock 933 MHz, DRAM clock 1,866 MHz, 3,733 MT/s); telemetry reads mhz.ddr = 933 in every sample.",
     3733, "MT/s", f"{EP}/device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c:41-42, 114-116, 225-228; {CAD}:291-292; {TEL}, field `mhz.ddr`",
     "measured", card="aifoundry2", page="anatomy")
fact("dram.peak-card", "DRAM", "bandwidth", "At 3,733 MT/s the 16 channels carry 119 GB/s.", 119, "GB/s",
     f"{CAD}:293; memory-hierarchy page spec sheet", "derived", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("dram.bw", "DRAM", "bandwidth",
     "Measured DRAM streaming bandwidth: 76 GB/s (about 64% of 119) on 1,024 minions at 600 MHz.",
     76, "GB/s", f"{CL}:370, 488 (docs/reports/data/2026-09-18-memhier-aifoundry2/energy*/runs.jsonl config `dram`)",
     "measured", card="aifoundry2, aifoundry3", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("dram.placeholder", "DRAM", "observability",
     "The 128,000 MB/s DRAM bandwidth the runtime reports is a placeholder constant in the service-processor firmware, not a measurement.",
     128000, "MB/s (placeholder)", f"{EP}/device-bootloaders/src/ServiceProcessorBL2/include/mem_controller.h:37 (DDR_BANDWIDTH); {CL}:499; driver_config.json `ddr_mb_s`",
     "spec", page="memhier", anchor="the-hierarchy-as-a-spec-sheet")
fact("dram.latency", "DRAM", "latency",
     "DRAM load: 287-297 cycles at 600 MHz (479-495 ns) depending on the requesting shire; the typical load from shire 0 is 299 cycles (500 ns), in each of 15 passes on three cards.",
     299, "cycles", f"{CL}:368, 410; docs/reports/data/2026-09-26-memprobe-3cards/cards.json `cards.<card>.dram_med`",
     "measured", card=CARDS3, note="287-297 is the pointer-chase plateau (memory-hierarchy page, requesters 0/7/24/31); 299 is the median of single loads to random lines from shire 0 (anatomy page).", page="anatomy", anchor="the-ladder-one-load-at-a-time")
fact("dram.leg", "memory shire", "latency",
     "Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 25 of the 91 are the DRAM chip (activate 11, read and burst 14) and about 66 the memory shire. Only 25-28 of a ~300-cycle DRAM load are the DRAM's own timing.",
     91, "cycles + 12/hop", f"{NOTES}:166; docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json `decomp.ms_const`; cards.json `ms_const` (90-91 on three cards); {CL}:404",
     "measured", card=CARDS3, page="anatomy", anchor="the-memory-shire-leg-91-cycles-plus-12-per-hop")
fact("dram.memshire-select", "memory shire", "address map",
     "The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.",
     None, None,
     f"{EP}/device-minion-runtime/tools/zebumem.c:67-72, 120-121; {SCS}, pdf p.26-27 (§1.4.3: 'the Memory Shire is selected by the NoC using bits [8:6]'); confirmed by the memory shires' read counters (syscall 10), {NOTES}:166",
     "measured", card="aifoundry2", page="anatomy", anchor="trace-one-load")
fact("dram.row-bits", "DRAM", "address map",
     "Inside a channel: bank PA[12:10], column PA[17:13] (plus PA[5:1] within the line), row PA[18] and up (PA[34:18]); 8 banks, 2 KB page, one rank per channel.",
     8, "banks per channel", f"{NOTES}:167; {CAD}:289, 362-370", "measured", card="aifoundry2",
     note="Row/bank bits measured with one address bit flipped; the controller's ADDRMAP decode is the research agent's inference.",
     page="anatomy", anchor="which-address-bits-share-a-row")
fact("dram.row-timing", "DRAM", "latency",
     "Row state: an open-row hit saves 11 cycles (tRCD); a back-to-back conflict in the same bank, other row, adds about 37 cycles (36.5-37.4 on three cards). The controller runs an open-page policy: rows close at a refresh or another row's access, not on a timer.",
     37, "cycles (row conflict)", f"{CL}:406, 545-547; cards.json `closed_minus_open`", "measured", card=CARDS3,
     page="anatomy", anchor="inside-the-dram-rows-banks-and-refresh")
fact("dram.refresh", "DRAM", "latency",
     "Refresh every 2,325.4 cycles (3.88 µs at 600 MHz); a load caught in one waits up to 208 cycles. The firmware programs all-bank refresh (tRFCab 280.7 ns).",
     3.88, "µs", f"{CL}:407 ({V3R}/mem.json MEM-P5); {CAD}:311, 326", "measured", card=CARDS3, page="anatomy",
     anchor="refresh-caught-in-the-act")
fact("dram.controller-policy", "memory shire", "configuration",
     "Controller configuration as programmed: open page, no auto-precharge, no power-down or self-refresh, no automatic ZQ, ECC off; tRCD = tRP = 18.2 ns, read latency 19.3 ns. DDR controller registers are service-processor only.",
     18.2, "ns (tRCD)", f"{CAD}:290, 297-347 (fw etsoc-hal/src/memshire_ddr_init_functions.c:4407-4449, 5459)", "spec",
     page="anatomy", anchor="how-long-a-row-stays-open")
fact("dram.energy", "DRAM", "energy",
     "Reading from DRAM costs 114.6 pJ per byte above idle [89.0-141.3]; tensor loads of known data 94.6 pJ/B (zeros) and 132.6 pJ/B (random); a DRAM byte costs about 30× an own-scratchpad byte.",
     114.6, "pJ/B", "docs/energy-manual/04-bytes-memory.md:15, 28, 37", "measured", card=CARDS3, page="memhier",
     anchor="the-hierarchy-as-a-spec-sheet")
fact("dram.unmetered", "DRAM", "observability",
     "About 70% of a DRAM byte's energy lands on no metered rail (DDR PHY, I/O rail and the DRAM chips); no meter covers the memory shires or DRAM.",
     70, "% unmetered", f"{CL}:308; anatomy page headline tiles", "measured", card=CARDS3, page="anatomy",
     anchor="where-the-energy-goes")
fact("dram.counters", "memory shire", "observability",
     "Each memory shire has a perf monitor with a 40-bit cycle counter (933 MHz) and two event counters; the firmware sets them to count mesh reads and writes, which U-mode can sample through syscall 10.",
     None, None, f"{CAD}:381-420", "spec", page="anatomy", anchor="what-the-chip-lets-you-see")

# ---------------------------------------------------------------- address map
fact("addr.regions", "chip", "address map",
     "40-bit physical address space (1 TB): I/O 0x00_0000_0000 (1 GB), service processor 0x00_4000_0000 (1 GB), scratchpad 0x00_8000_0000 (2 GB), ESRs 0x01_0000_0000 (4 GB), PCIe 0x40_0000_0000 (256 GB), DRAM 0x80_0000_0000 (512 GB).",
     40, "address bits", f"{PRM}, pdf p.340 (Table 15-1); {DS}, pdf p.20 (§3)", "spec", page=None)
fact("addr.dram-region", "DRAM", "address map",
     "The DRAM region starts at 0x80_0000_0000; minions reach only the 'Low' view (M-mode low 8 MB, OS low to 0x80_FFFF_FFFF, memory low 0x81_0000_0000-0x87_FFFF_FFFF, 28 GB); device allocations come back as 0x80_xxxx_xxxx addresses.",
     None, None, f"{PRM}, pdf p.551 (Table 15-96) and p.553 (Table 15-98); {CAD}:348-350, 379-380", "spec", page=None)
fact("addr.esr-shire-ids", "chip", "address map",
     "ESR shire IDs (address bits 29:22): 0-33 minion shires, 232-239 memory shires 0-7, 253 the PCIe shire, 254 the I/O shire, 255 the local minion shire.",
     None, None, f"{PRM}, pdf p.487 (§15.4)", "spec", page=None)
fact("addr.load-path", "chip", "data flow",
     "Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.",
     None, None, f"{CAD}:478-482; {SCS}, pdf p.10, p.12-13", "spec",
     note="A synthesis of the Shire Cache Specification and the RTL by the repo's research notes; the measured latency model (next fact) agrees.",
     page="anatomy", anchor="trace-one-load")
fact("addr.load-model", "chip", "data flow",
     "Measured load-to-use model from any requesting shire at 600 MHz: L1 5; L2 47-48; L3 110 + 12·hops(requester, home = PA[10:6]); DRAM 110 + 12·hops(requester, home) + 91 + 12·hops(home, memory shire = PA[8:6]). The mesh round trip is paid twice on a DRAM load: to the L3 home, then on to the memory shire.",
     None, None, f"{NOTES}:164-166; anatomy page §1 'Trace one load' and headline tiles; {CL}:403-404 (V3 check: L3 within ±4 cycles for 99.4-99.97% of lines, DRAM within ±3 for 93-97%)",
     "measured", card=CARDS3, note="The route order inside the mesh was not measured.", page="anatomy",
     anchor="trace-one-load")

# ---------------------------------------------------------------- PCIe / board
fact("pcie.link", "PCIe shire", "bandwidth",
     "Host link: PCIe Gen4 x8 on an x16 card edge; the datasheet gives up to 128 Gbps each way (25.78 Gbit/s per lane PHY). 15.75 GB/s per direction is the Gen4 x8 figure; host transfer bandwidth was never measured here.",
     15.75, "GB/s (not measured)", f"{DS}, pdf p.4 (§1); {CARD}, pdf p.3; {CL}:489", "derived", page="ridge",
     anchor="other-limits-that-act-like-ridge-points")
fact("board.card", "board", "board",
     "The PCIe dev card V3: ET-SoC-1 soldered down, 4 LPDDR4x devices (256-bit), 64 GB eMMC, USB (device/debug, OTG, FTDI UART), JTAG, 12 V input metered by an LTC4218 hot-swap controller.",
     None, None, f"{CARD}, pdf p.3 (Features) and pdf p.6-7 (Power Measurement)", "spec", page="hub", anchor="the-chain")
fact("board.regulators", "board", "voltages",
     "Regulators: minion and NoC share a TI TPSM831D31 (minion on a 3-phase output, 120 A max; NoC single-phase, 40 A max); the SRAM rail is an LTM4680 (60 A max).",
     120, "A (minion rail max)", f"{CARD}, pdf p.5-6 (Key Voltage Regulators)", "spec", page="hub", anchor="the-chain")
fact("board.meters", "board", "observability",
     "The PMIC meters the 12 V input and three regulators (minion, NoC, SRAM); DDR, VDDQ, VDDQLP, PCIe logic, PCIe and Maxion rails have set points only. The service processor forwards a new value about every 133 ms (aifoundry2; 224 ms quiet pass on aifoundry3).",
     3, "metered rails", f"{CL}:330, 438 ({V3R}/tel.json TEL-P1); {PT}:39-56", "measured", card=CARDS3,
     page="hub", anchor="the-chain")
fact("board.thresholds", "board", "power",
     "Governor thresholds in the firmware: 65 °C software temperature threshold and 65 W TDP; hardware catastrophic 75 °C and 75 W.",
     65, "W (TDP)", f"{EP}/device-bootloaders/src/ServiceProcessorBL2/include/thermal_pwr_mgmt.h:41, 48; bl2_pmic_controller.h:262, 281; {CL}:44",
     "spec", note="aifoundry3's boot service sets its TDP to 0, pinning it at 600 MHz.", page="dvfs", anchor="the-loop-as-built")

# ---------------------------------------------------------------- clocks and voltages
fact("clock.minion-opps", "minion", "clocks",
     "Operating points the firmware uses: 600 MHz at 517 mV, 700 MHz at 568 mV, 800 MHz at 618 mV (measured on die); every table in the reports is at 600 MHz, where a warm card sits.",
     600, "MHz", f"{CL}:28-29, 171 (docs/reports/data/2026-09-21-horace-aifoundry2/cold1/telemetry.jsonl.gz `mhz.minion`, `die_mv.minion`)",
     "measured", card="aifoundry2 (aifoundry3 pinned at 600 MHz)", page="dvfs", anchor="the-loop-as-measured")
fact("clock.minion-boot", "minion", "clocks", "Boot minion clock 600 MHz on every card.", 600, "MHz",
     "docs/reports/data/2026-09-22-cards/driver_config.json `minion_boot_freq_mhz`", "measured",
     card="aifoundry1 (both cards), aifoundry2, aifoundry3", page="dvfs")
fact("clock.dvfs-limits", "minion", "clocks",
     "Firmware DVFS limits: minion 300-800 MHz, NoC 300-500 MHz; the minion PLL table covers 300-1,400 MHz in 25 MHz steps.",
     800, "MHz (minion max)", f"{EP}/device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c:130-135; {PT}:180-185",
     "spec", page="dvfs", anchor="the-loop-as-built")
fact("clock.design", "chip", "clocks",
     "Design clocks: shire PLL output 1,000 MHz; a step clock of 400-1,000 MHz from PLL4 in the I/O shire; NoC clock 500 MHz from PLL2 in the I/O shire; reference oscillators 24 MHz and 100 MHz; the RISC-V mtime timer ticks at 10 MHz.",
     1000, "MHz (shire PLL, design)", f"{MSD}, pdf p.12 (Table 2); {DS}, pdf p.16 (§2.2.6), p.22 (§5.1.1), p.29 (§6.6.2.1)",
     "spec", page=None)
fact("volt.minion", "minion", "voltages",
     "Minion rail: set point 520 mV, 516-518 mV on die under load at 600 MHz; per-shire 517-521 mV at idle. Firmware limits 400-620 mV (boot default 500).",
     518, "mV", f"{CL}:26-27, 41; {PT}:186-190", "measured", card="aifoundry2 (aifoundry3 523 mV)", page="power")
fact("volt.sram", "shire cache", "voltages",
     "SRAM rail (shire-cache arrays): set point 705 mV, 703-707 mV on die.",
     704, "mV", f"{TEL}, fields `reg_mv.sram`, `die_mv.sram`; {CL}:41", "measured", card="aifoundry2", page="power")
fact("volt.other", "chip", "voltages",
     "Other rails, set point / on die: DDR 800 / 762-768 mV, Maxion 600 / 583-586 mV, I/O shire - / 751-754 mV, PCIe shire - / 749-753 mV (PCIe logic set 775 mV), VDDQ 1,100 mV, VDDQLP 640 mV.",
     None, None, f"{TEL}, fields `reg_mv.*`, `die_mv.*`", "measured", card="aifoundry2",
     note="The firmware's boot default for the Maxion rail is 850 mV (thermal_pwr_mgmt.h:97); these cards run it at 600 mV.",
     page="hub", anchor="the-chain")
fact("volt.per-shire", "shire", "voltages",
     "Per-shire on-die voltages at idle for all 34 minion shires (minion rail, SRAM, mesh, each as now/low/high) are in one file, keyed by the firmware's shire number.",
     None, None, "docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json (`<shire>.mnn|sram|noc`)",
     "measured", card="aifoundry2",
     note="Whether the pattern is a per-monitor offset was not settled (V3 TEL-Q INSUFFICIENT, 05-claims.md:568-571).",
     page="power")

# ---------------------------------------------------------------- power (overlay)
fact("power.idle", "board", "power",
     "Idle card after 20.6 h with no workload: 31.79 W at 73 °C, of which minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W and 15.10 W on no sensor.",
     31.79, "W", f"{CL}:181, 183 (docs/reports/data/2026-09-22-dvfs-aifoundry2/idle_20h.jsonl.gz)", "measured",
     card="aifoundry2", page="dvfs")
fact("power.leakage", "chip", "power",
     "Leakage is 23.3 W of an idle card at 80 °C (65%) and 36% of a random-data matmul.",
     23.3, "W at 80 °C", f"{CL}:86, 184-185", "derived", card="aifoundry2",
     note="Fitted (kind F in the claims index).", page="dvfs", anchor="what-that-costs")
fact("power.matmul", "board", "power",
     "fp32 TensorFMA on all 1,024 minions at 600 MHz and 80 °C, 9.18 TFLOPS: 38.29 W with zero operands, 46.73 W with ones, 63.40 W with random-normal data.",
     63.40, "W (random normal)", f"{CL}:33, 53-56 (docs/reports/data/2026-09-21-horace-aifoundry2/horace3.json `patterns.*.p80`)",
     "measured", card="aifoundry2", page="horace")

# ---------------------------------------------------------------- synchronisation and on-chip traffic
fact("sync.flb", "shire", "synchronisation",
     "Fast local barrier: 32 barrier counters per shire, 8 bits wide (enough for all 64 harts), joined atomically with one CSR write (0x820) from user mode.",
     32, "barrier counters per shire", f"{PRM}, pdf p.327 (§10)", "spec", page="onchip", anchor="every-primitive-against-a-gpu")
fact("sync.fcc", "minion", "synchronisation",
     "Fast credit counters: two per hart (four per minion); any hart in any shire adds credits by writing a 64-bit mask to a shire's CREDINC0-3 ESRs; reading an empty counter blocks until a credit arrives.",
     2, "counters per hart", f"{PRM}, pdf p.328 (§11)", "spec", page="onchip", anchor="every-primitive-against-a-gpu")
fact("sync.measured", "chip", "synchronisation",
     "Measured at 600 MHz: shire barrier (FLB + credits, 32 minions) 232.5 cycles (388 ns); 32-minion allreduce 444 cycles (0.74 µs); 1,024-minion allreduce 1,393 cycles (2.3 µs); chip barrier from global atomics and credits 4,990-5,012 cycles (8.3 µs); credit round trip 140.2 + 14.4 cycles per hop (234 + 24 ns/hop), about 120 cycles blocking inside a shire.",
     1393, "cycles (1,024-minion allreduce)", f"{CL}:412-413 ({V3R}/lat.json LAT-N1, LAT-N2, LAT-N4)", "measured",
     card=CARDS3, page="onchip", anchor="every-primitive-against-a-gpu")
fact("sync.tree-levels", "chip", "synchronisation",
     "Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).",
     None, None, "on-chip communication page §'Reduction trees'", "measured", card=CARDS3, page="onchip",
     anchor="reduction-trees")
fact("sync.flag-memory", "L3", "synchronisation",
     "A flag handed through global atomics in memory costs 610-1,150 ns round trip (median 873), whatever the distance: it depends on which shire's L3 slice holds the flag's line.",
     873, "ns (median)", "on-chip communication page §'Latency grows with distance, except through memory'", "measured",
     card=CARDS3, page="onchip", anchor="latency-grows-with-distance-except-through-memory")
fact("onchip.aggregate-bw", "chip", "bandwidth",
     "Aggregate message bandwidth with every minion sending 1 KB messages: 2,992 GB/s on tree-edge pairs, 1,120 GB/s in neighbourhood or shire rings, 87-156 GB/s across the mesh (7-34× less).",
     2992, "GB/s (tree-edge pairs)", "on-chip communication page table 'The numbers in the chart'; " + f"{NOTES}:120",
     "measured", card="aifoundry2", page="onchip", anchor="energy-per-byte-moved")
fact("onchip.energy", "chip", "energy",
     "Messaging energy per byte: 0.69 pJ/B on tree-edge pairs, 2.16 in a neighbourhood ring, 2.22 in a shire ring, and 9.2 + 1.75 pJ/B per mean hop across the mesh (busy cores included).",
     1.75, "pJ/B per mean hop", f"{CL}:450; docs/reports/data/2026-09-23-energy-manual/reruns.json `rings_pj_per_byte`", "measured",
     card=CARDS3, page="onchip", anchor="energy-per-byte-moved")
fact("relay.speedup", "scratchpad", "data flow",
     "A multi-stage pipeline that hands each stage's output to the next shire's scratchpad runs about 12.4× faster than one that goes through DRAM (31× keeping it in the own scratchpad), at 116 / 8.9 / 4.3 pJ per byte moved (DRAM / next shire / own).",
     12.4, "× faster than DRAM", f"{CL}:416, 451; docs/reports/data/2026-09-23-energy-manual/reruns.json `relay_pj_per_byte`",
     "measured", card=CARDS3, page="relay", anchor="one-kernel-three-places-to-put-the-answer")
fact("ridge.levels", "chip", "compute",
     "Ridge points at 600 MHz (fp32 FLOP per byte fetched): own shire L2 or scratchpad 4, L3 or another shire's scratchpad 10, DRAM 130, PCIe 624 (unmeasured link).",
     130, "FLOP/B (DRAM, fp32)", f"{CL}:486-489", "derived", page="ridge", anchor="ridge-points-by-level")

# ---------------------------------------------------------------- validate and write
ids = [f["id"] for f in F]
dup = {i for i in ids if ids.count(i) > 1}
assert not dup, dup
for f in F:
    assert f["source"], f["id"]
    if f["kind"] == "measured":
        assert f["card"], f["id"]
json.dump(F, open(OUT, "w"), indent=1, ensure_ascii=False)
print(len(F), "facts ->", OUT)
from collections import Counter
print(Counter(f["kind"] for f in F))
print(Counter(f["component"] for f in F))
