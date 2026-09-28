#!/usr/bin/env python3
"""Build facts-l2.json: the L2 (shire cache as L2) facts and access sequences for the
'anatomy of a memory access' diagrams.  Every item is a dict with the fields
{id, level, topic, statement, value, unit, source, kind, card, page_link, note};
access-sequence steps add {sequence, step, block, action, latency, energy, circuit}.
kind is one of et-spec | et-measured | et-derived | generic | unknown."""
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facts-l2.json")

# source shorthands (paths relative to the prototyping checkout's external/ or to the repo root)
SCS = "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf (v1.1)"
MSD = "external/core-et/docs/CORE-ET Minion Shire Description.pdf"
NMAS = "external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf"
DCD = "external/core-et/docs/Minion DCache Description.pdf"
DS = "external/et-man/ET Preliminary Datasheet Rev 1.0.pdf"
ERR = "external/et-man/ET-SoC Errata.pdf"
DEF = "external/core-et/rtl/inc/shire_cache_defines.vh"
ESRB = "external/core-et/rtl/shire/esr/esr_cache_bank.v"
CEM = "external/core-et-main/hw/ip"  # Ainekko 2026 reimplementation of CORE-ET
CLAIMS = "docs/findings/05-claims.md"
EM4 = "docs/energy-manual/04-bytes-memory.md"
ANAT_T = "workloads/memprobe/report_template.html"
MP = "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json"
LAT = "docs/reports/data/2026-09-25-claims-v3/results/lat.json"
HIER = "docs/reports/2026-09-18-et-soc1-memory-hierarchy.html"

U = "https://spacesheep.dev/@yaroslavvb/"
ANAT = U + "et-soc1-memory-anatomy"
MH = U + "et-soc1-memory-hierarchy"
EMAN = U + "et-soc1-energy-manual"
CHIP = U + "et-soc1-chip-diagram"
HUB = U + "et-soc1-limits-of-observability"
ALL3 = "aifoundry2, aifoundry3, aifoundry1-c1"

F = []


def f(id, topic, statement, value, unit, source, kind, card=None, page_link=None, note=None, level="L2"):
    assert kind in ("et-spec", "et-measured", "et-derived", "generic", "unknown"), kind
    F.append(dict(id=id, level=level, topic=topic, statement=statement, value=value, unit=unit,
                  source=source, kind=kind, card=card, page_link=page_link, note=note))


# ---------------------------------------------------------------- what the L2 is
f("l2.sc.what", "organisation",
  "Each minion shire has one 4 MB shire cache whose storage is split by ESRs into three partitions: L2 (private to the shire), a slice of the chip-wide L3, and scratchpad. The L2 part serves the shire's 4 neighbourhoods (32 minions) and its RBOX.",
  4, "MB per shire",
  SCS + ", pdf p.6 §1 and p.8 §1.1; " + DS + ", pdf p.13 §2.1.3.1", "et-spec", page_link=CHIP)
f("l2.sc.chip-total", "organisation",
  "The datasheet counts 140 MB of on-die SRAM, in 1 MB blocks each configurable as local L2, part of the chip-wide L3 or globally addressable scratchpad.",
  140, "MB per chip", DS + ", pdf p.4 §1", "et-spec", page_link=CHIP,
  note="35 x 4 MB counts the I/O shire's cache; the Shire Cache Specification (pdf p.22) gives the I/O shire only 1 MB, a conflict the hub already lists under ask-design-docs.")
f("l2.partition.default", "organisation",
  "Firmware default partition (Mode 0): 2.5 MB scratchpad, 0.5 MB L2, 1 MB L3 per shire (80 / 16 / 32 MB for the chip). The service processor reads the sizes from the card's flash configuration and writes them to every bank; the chip comes out of reset in M0.",
  0.5, "MB of L2 per shire",
  "external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/minion_configuration.c:613-624; .../driver/bl2_cache_control.c:650-751; " + SCS + ", pdf p.21-22 Table 6 and 'The chip will come out of reset in mode M0'",
  "et-spec", page_link=MH + "#the-hierarchy-as-a-spec-sheet",
  note="The lab cards' flash values were never read; every page assumes 512 KB (docs/et-soc1-notes.md:19). Latency plateaus up to 64 KB do not test the 512 KB edge.")
f("l2.partition.rows", "organisation",
  "In Mode 0 the L2 occupies sets 0x280-0x2FF (128 of the 1,024 physical sets) of every sub-bank, set mask 0x7F: 4 banks x 4 sub-banks x 128 sets x 4 ways x 64 B = 512 KB. The scratchpad sits in sets 0x000-0x27F and the L3 in 0x300-0x3FF of the same RAMs.",
  128, "sets per sub-bank", SCS + ", pdf p.22 Table 7 (Mode 0 rows); pdf p.25 §1.4.1.4 (physical set = region set + set_base)", "et-spec",
  note="So an L2 access lights only rows 640-767 of each tag/tag-state RAM and the matching {way,set} rows of the data RAMs; the other rows belong to scratchpad and L3.")
f("l2.private", "organisation",
  "The L2 is private to its shire and not coherent: it does not track ownership or sharing across the 32 minions it serves; software handles coherence.",
  None, None, SCS + ", pdf p.6 §1; " + DS + ", pdf p.13 §2.1.3.1", "et-spec", page_link=CHIP)
f("l2.assoc", "organisation",
  "The L2 is 4-way set associative with 64-byte lines, write-back and write-allocate, and uses LRU replacement stored as a 5-bit code per set (4! = 24 orders).",
  4, "ways", SCS + ", pdf p.8-9 §1.1; pdf p.47-48 §2.14.4", "et-spec")
f("l2.banks", "organisation",
  "The shire cache is four identical banks; each bank is an independent L2 cache with its own request queue, pipeline and next-level ports. A bank takes at most one request per cycle and returns at most one 512-bit line per cycle.",
  4, "banks per shire", SCS + ", pdf p.6 §1; pdf p.30 §2.1", "et-spec", page_link=CHIP)
f("l2.bank-select", "address",
  "L2 and scratchpad requests go to the bank chosen by PA[7:6], so consecutive 64 B lines rotate through banks 0-3.",
  None, None, SCS + ", pdf p.6 §1 and p.24 §1.4.1.1", "et-spec", page_link=CHIP)
f("l2.decode", "address",
  "L2 address fields: offset PA[5:0], bank PA[7:6], sub-bank PA[9:8], set from PA[10] (PA[19:10] for a full 4 MB L2; PA[16:10] with Mode 0's 7-bit set mask), tag above. The tag RAM stores 23 tag bits, which 'allows for down to 512k L2 allocation'.",
  23, "tag bits stored", SCS + ", pdf p.24 §1.4.1.1 and p.23; " + DEF + ":144-145", "et-spec", page_link=CHIP)
f("l2.subbanks", "organisation",
  "Each bank is four sub-banks. Each sub-bank has its own tag RAM, tag-state RAM, data RAM and ECC logic; the read buffer, atomic unit and coalescing buffer are shared by the bank's four sub-banks.",
  4, "sub-banks per bank", SCS + ", pdf p.35 §2.5; pdf p.9 ('4 sub-banks/bank' is the POR for the first SoC)", "et-spec")
f("l2.sets", "organisation",
  "A sub-bank holds 4,096 lines = 1,024 sets x 4 ways (4 MB / 64 B / 4 banks / 4 sub-banks).",
  1024, "sets per sub-bank", SCS + ", pdf p.20 Table 4", "et-spec")

# ---------------------------------------------------------------- the storage
f("l2.tag-ram", "storage",
  "Tag RAM: one row per set holding all four ways' tags, each 23 bits + 6 ECC bits, so the row is 116 bits and the four tags are read and compared in parallel.",
  116, "bits per row", SCS + ", pdf p.47 §2.14.2; " + DEF + ":241-246", "et-spec",
  note="The overview (pdf p.9) says '7 bits of ECC stored with each 33-bit tag'; §2.14.2, the defines and the 1024x116 macro all say 23 + 6.")
f("l2.tag-state-ram", "storage",
  "Tag-state RAM: one 40-bit row per set = 4 x {valid, locked, zero, qwen[3:0]} + 5-bit LRU code + 7-bit ECC. It is read and written on every L2 request, and it is two-ported, so the read and the LRU/dirty update happen in the same pass.",
  40, "bits per row", SCS + ", pdf p.47 §2.14.3 Table 12 and pdf p.45; " + DEF + ":231-237", "et-spec")
f("l2.data-ram", "storage",
  "Data RAM: each sub-bank is four 144-bit-wide panels, each holding one 128-bit quadword + 16 ECC bits (8 per 64 bits). A 64 B line is one row across the four panels (576 bits); a sub-bank's data RAM is 4,096 rows addressed by {way, set}.",
  576, "bits per line incl. ECC", SCS + ", pdf p.48 §2.14.5 and pdf p.48-49 §2.14.6.2; " + DEF + ":250-255", "et-spec")
f("l2.serial-lookup", "storage",
  "The lookup is serial (tag first, then data): the data-RAM address includes the way, and the data stages (dap..dc) start after the tag compare (tc), so a hit reads only the hit way's row, not all four ways.",
  None, None, DEF + ":253 (SC_DATA_RAM_ADDR_SIZE = way + set); " + SCS + ", pdf p.44 read-hit stage figure", "et-derived")
f("l2.panel-select", "storage",
  "Only the panels holding the addressed quadwords are enabled (a 3-quadword partial write activates 3 panels), and the RAM inputs, address bits included, are held unchanged in cycles with no access, to save power.",
  None, None, SCS + ", pdf p.48 §2.14.5; pdf p.46 §2.14.1.5 and §2.14.1.11", "et-spec")
f("l2.macro.data", "circuit",
  "The data panel is the compiled macro 'saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11', type 1PUHD (single-port, ultra-high-density): 4,096 words x 144 bits.",
  "4096x144", "words x bits", SCS + ", pdf p.51 §2.14.6.4", "et-spec")
f("l2.macro.tag", "circuit",
  "The tag RAM is 'saduls0g4l1p1024x116m4b1w0c0p0d0s1rm0sdrw11', type 1PUHD: 1,024 words x 116 bits.",
  "1024x116", "words x bits", SCS + ", pdf p.51 §2.14.6.4", "et-spec")
f("l2.macro.state", "circuit",
  "The tag-state RAM is 'saculs0g4l2p1024x40m4b1w0c0p0d0s1rm0rw11', type 2PUHDRF (two-port register file): 1,024 words x 40 bits.",
  "1024x40", "words x bits", SCS + ", pdf p.51 §2.14.6.4", "et-spec")
f("l2.macro.vendor", "circuit",
  "The tag-state, tag and data panels are 'IP acquired from a third party vendor'. They are tested with a shared-bus BIST 'such as the Synopsys SMS (STAR Memory System)'. The BIST's logical RAMs per bank are mbs (tag state), mbt (tag), mbd (data), mbq (dataq) and mbi (instruction cache, bank 0 only).",
  None, None, SCS + ", pdf p.48 §2.14.6.1 and pdf p.49 §2.14.6.3", "et-spec",
  note="The vendor and bitcell are not named. The Synopsys BIST and the name pattern point to a Synopsys-compiled memory, but that is an inference.")
f("l2.macro.count", "circuit",
  "Per shire there are 64 data macros (4 banks x 4 sub-banks x 4 panels), 16 tag macros and 16 tag-state macros.",
  96, "macros per shire", "derived from " + SCS + ", pdf p.48 §2.14.5, p.47 §2.14.2-3 and p.51", "et-derived")
f("l2.bits", "circuit",
  "Bits stored per shire, ECC included: data 64 x 4,096 x 144 = 37,748,736; tag 16 x 1,024 x 116 = 1,900,544; tag state 16 x 1,024 x 40 = 655,360; 40,304,640 in all (about 40.3 Mbit, of which 33.6 Mbit is the 4 MB of data).",
  40304640, "bits per shire", "derived from the macro sizes, " + SCS + ", pdf p.51", "et-derived")
f("l2.transistors", "circuit",
  "If the single-port data and tag macros use a 6-transistor cell and the two-port tag-state file an 8-transistor cell (the usual choice for such macros), one shire's cache arrays hold about 243 million cell transistors (39.6 Mbit x 6 + 0.66 Mbit x 8), before any periphery.",
  243e6, "transistors per shire (cells only)", "l2.bits x GENERIC 6T/8T bitcells", "generic",
  note="GENERIC assumption: the ET bitcell is not documented (see l2.storage-question).")
f("l2.macro.name-decode", "circuit",
  "Reading 'm4' and 'b4' in the data macro's name as a memory compiler's column-mux 4 and internal-bank 4 fields would make each 4096x144 panel about 1,024 wordlines by 576 bitline pairs, split into 4 banks, with each output bit chosen from 4 columns. No source defines the fields.",
  None, None, SCS + ", pdf p.51 (names only)", "unknown",
  note="This is naming-convention inference. The macro datasheet settles it.")
f("l2.trim", "circuit",
  "Each logical RAM group has ESR trim bits: RM (read margin), RME (RM enable), RA (read assist), WA (write assist) and WPULSE (write-pulse width). They default to 'RM0 mode to allow nominal 650mV operation'. For the 1PUHD tag and data macros the table gives RM0 = VMIN 585 mV, Vnom 650: RM 0, WA 7, RA 1, WPULSE 0. For the 2PUHDRF tag-state RAM it gives RM0 = VMIN 540 mV: WA 6, RA 2. The tables run up to RM5 at 855 mV VMIN.",
  650, "mV nominal at the default trim",
  SCS + ", pdf p.50-51 §2.14.6.4 Tables 13-14; field meanings " + CEM + "/ram_cfg/rtl/ram_cfg_pkg.sv:14-23",
  "et-spec")
f("l2.trim.reset", "circuit",
  "The simulator's reset values for shire_cache_ram_cfg1/2 (0xE800340, 0x03A0), decoded with the HAL's field layout, are exactly the tables' RM0 rows: tag and data RAMs RM=0, RA=1, WA=7, WPULSE=0 with RME=0; tag-state RA=2, WA=6. No firmware in et-platform at 836a4ab writes these registers.",
  None, None,
  "external/et-platform/sw-sysemu/esrs_et.cpp:46-47; external/et-platform/etsoc-hal/include/hwinc/etsoc_shire_other_esr.h:3070-3376 (field bit positions); grep of et-platform for RAM_CFG writes (none)",
  "et-derived",
  note="Whether the boot ROM or silicon reset programs something else is not known (ask). If they do not, the arrays run with the 650 mV assist settings at the rail's ~705 mV.")
f("l2.storage-question", "circuit",
  "What the storage circuit is on silicon is not settled. The Shire Cache Specification calls the data array 'SRAM memory panels' and the datasheet calls it 140 MB of SRAM, but the lab lead said the chip is 'not using SRAM'. No source gives the bitcell (6T, 8T or other) or confirms that the v1.1 macros are the ones taped out.",
  None, None, SCS + ", pdf p.40 §2.8 and p.48 §2.14.5; " + DS + ", pdf p.4 §1", "unknown",
  note="For contrast, the L1 data cache is documented as not SRAM: 4 LRAM (latch-RAM) blocks of 128 rows x 64 bits (" + DCD + ", pdf p.29). The remark may refer to the L1 and register files rather than the shire cache.")
f("l2.l1-context", "circuit",
  "Context for the 'not SRAM' question: the minion's L1 data cache is built from 4 LRAM (latch-based RAM) blocks of 128 rows x 64 bits, not SRAM; the reimplementation names its model dcache_128x32_1r1w_lram.",
  None, None, DCD + ", pdf p.29 and p.61 (glossary 'LRAM Latch Random Access Memory'); external/core-et/rtl/libs/macros/dcache_128x32_1r1w_lram.v:1-12",
  "et-spec", level="L1 (context for L2)")

# ---------------------------------------------------------------- voltage, clock, rails
f("l2.clock", "clock",
  "The shire cache runs on shire_clock from the shire's PLL. The neighbourhoods (minions) run on the same clock shifted by 180 degrees (a DLL), and the errata note that every area of a minion shire except the NoC uses the same clock. So one shire-cache cycle is one minion cycle.",
  None, None, MSD + ", pdf p.12 Table 2; " + NMAS + ", pdf p.39 Table 6; " + ERR + ", pdf p.42", "et-spec")
f("l2.freq", "clock",
  "The firmware reports the L2/SRAM frequency as equal to the minion frequency: 600 MHz at the governor's operating point used for every measurement here.",
  600, "MHz", "docs/research/power-telemetry.md:140 (perf_mgmt.c:201-207); docs/reports/data/2026-09-23-energy-manual/manual.json operating_point", "et-spec", page_link=EMAN)
f("l2.domain", "voltage",
  "The Shire Channel (shire cache, UC block, ESRs, instruction-cache memories) is a separate high-voltage (HV) region on the shire clock. The minions and most of each neighbourhood are a low-voltage (LV) region on the neighbourhood clock. Each neighbourhood's north ports are the HV interface. The instruction-cache data memory sits in the Shire Channel 'because it has to be operated at high voltage'.",
  None, None, MSD + ", pdf p.5 Figure 1 (legend 'HV Region'), pdf p.10 §3.1; " + NMAS + ", pdf p.6-7 §2, pdf p.45 §7", "et-spec")
f("l2.rail.sram", "voltage",
  "The card's VDD_SRAM regulator (750 mV set point, 20 A / 15 W in the card figure) feeds the shire-cache SRAM arrays (L2/L3/scratchpad). It is one of the three rails whose power the PMIC meters.",
  750, "mV boot set point", "docs/research/power-telemetry.md:14, 46, 189-190 (thermal_pwr_mgmt.h; bl2_pmic_controller.h:165-244)", "et-spec",
  page_link=HUB)
f("l2.rail.hv-logic", "voltage",
  "Whether VDD_SRAM also powers the rest of the HV region (request queues, crossbars, read buffers, ECC, the voltage-crossing FIFO cells, the instruction-cache memories) or only the RAM macros is not stated. The Power Spec that would say is not in the documents we have.",
  None, None, MSD + ", pdf p.18 §5 (refers to the Power Spec)", "unknown", page_link=HUB + "#ask-design-docs")
f("l2.voltage.idle", "voltage",
  "Measured on-die SRAM-rail voltage per shire at idle: 703-707 mV across the 34 minion shires (minion rail 513-522 mV, mesh 483-486 mV).",
  705, "mV", CLAIMS + ":41 (docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json)", "et-measured",
  card="aifoundry2", page_link=CHIP)
f("l2.voltage.limits", "voltage",
  "The firmware limits the SRAM rail to 660-850 mV, and DVFS moves the minion and L2/SRAM voltages together.",
  None, "mV", "docs/research/power-telemetry.md:175, 189-190 (thermal_pwr_mgmt.c; bl2_pmic_controller.h:165-244)", "et-spec")
f("l2.vc-fifo", "voltage",
  "The neighbourhood's per-bank output FIFOs double as the clock- and voltage-crossing elements: semi-synchronous VC FIFOs from the cell library, with level shifters built in at the HV/LV boundary. Their storage cells always sit in the HV region 'as performance and access time improve with the voltage'. Responses cross back through a VC FIFO at the neighbourhood's input.",
  None, None, NMAS + ", pdf p.18-19 §4.3.4, pdf p.20 §4.4.1, pdf p.45 §7.1 (Figure 16)", "et-spec")

# ---------------------------------------------------------------- the path to the bank
f("l2.path.miss", "path",
  "An L1 miss starts one of the minion's two miss handlers, which asks the L2 for the line. Loads leave on the miss interface (3 valid/ready pairs: regular, TensorLoad 0, TensorLoad 1). Stores, evicts, atomics and messages leave on the 256-bit evict interface.",
  2, "miss handlers per minion", NMAS + ", pdf p.15 Table 2; " + DCD + ", pdf p.34-36 §3.6; docs/research/counters-and-dram.md:448", "et-spec")
f("l2.path.nbr-request", "path",
  "Inside the neighbourhood a request passes the minion's Miss/Evict flip-flops, a 2:1 minion arbiter (evicts first), a flop, a two-stage 13:1 round-robin arbiter, a 1-cycle pre-processing stage and then one of five output FIFOs (four banks + UC, 3 entries each, with a 2-entry intermediate FIFO). Minimum latency for a minion's request is 6 cycles.",
  6, "cycles", NMAS + ", pdf p.16-20 §4.3.1-4.3.5", "et-spec")
f("l2.path.widths", "path",
  "The neighbourhood's request datapath is 256 bits wide (a 512-bit write takes two cycles and is re-joined before the bank FIFO); its response datapath and the ET-Link into each bank are 512 bits; the minion's own fill interface is 256 bits, so a 64 B line reaches the L1 in two beats.",
  512, "bits", NMAS + ", pdf p.14-15 §4.3, p.19 §4.3.5, p.20 §4.4, p.22-23 §4.4.3; " + SCS + ", pdf p.10 §1.1", "et-spec")
f("l2.xbar.req", "path",
  "req_xbar: a full crossbar from the 5 clients (4 neighbourhoods + RBOX) to the 4 banks + UC. Each bank has one catch FIFO per neighbourhood and a round-robin arbiter that skips entries whose bank is stalled. It lives in the shire-cache hierarchy 'so that it can be routed on top of all four banks'.",
  None, None, SCS + ", pdf p.30 §2.1, pdf p.30-31 §2.2 Figure 4", "et-spec")
f("l2.xbar.rsp", "path",
  "rsp_xbar: the same module in reverse (4 banks + UC to 4 neighbourhoods + RBOX). Neighbourhoods never back-pressure, since space for the response is reserved. It arbitrates only when two banks answer the same neighbourhood in one cycle.",
  None, None, SCS + ", pdf p.30 §2.1, pdf p.32 §2.2", "et-spec")
f("l2.nbr.response", "path",
  "Back in the neighbourhood a response goes through the VC FIFO (min 2 cycles), the Fill FIFO (a 4-entry buffer drained out of order by an LRU 4:1 arbiter, min 2 cycles) and the minion's Fill FF, which splits 512 bits into two 256-bit beats (min 2 cycles): 6 cycles minimum for a minion.",
  6, "cycles", NMAS + ", pdf p.20-23 §4.4.1-4.4.3", "et-spec")

# ---------------------------------------------------------------- inside a bank
f("l2.reqq", "bank",
  "Each bank has a 64-entry request queue (reqq), the equivalent of MSHRs. An entry lives from allocation through miss, mesh read, fill and any victim write-back. Two entries can be allocated per cycle (one neighbourhood, one L3-slave request), and 21 of the 64 are reserved for L3-slave requests by default.",
  64, "entries per bank", SCS + ", pdf p.34-35 §2.5-2.6; " + DEF + ":69; " + ESRB + ":81 (NUM_REQQ_ENTRIES/3)", "et-spec")
f("l2.reqq.arb", "bank",
  "Choosing what enters the pipeline takes three steps: round-robin per sub-bank (neighbourhood and L3 separately), then L3 requests before neighbourhood requests, then masking out busy sub-banks and a round-robin across sub-banks. Errata RTLMIN-6207 and 6214 record that a neighbourhood request can starve behind L3-slave traffic.",
  None, None, SCS + ", pdf p.36 §2.6 Figure 8; " + ERR + ", pdf p.80-81 §4.1-4.2", "et-spec", page_link=U + "et-soc1-hot-line")
f("l2.reqq.order", "bank",
  "Requests to the same address keep their order through per-address linked lists in the reqq. A victim is inserted at the front, so a later read miss cannot fetch the line before its write-back is acknowledged.",
  None, None, SCS + ", pdf p.36-38 §2.6.1", "et-spec")
f("l2.dataq", "bank",
  "The dataq holds one 64 B line per reqq entry in a two-ported register file (one write and one read port, each shared by 5 sources). BIST sees it as logical RAM mbq (64 x 4 x 144 bits, 1-cycle access) plus mbb (64 x 72 bits). Read hits normally bypass it straight to the response mux.",
  64, "lines per bank", SCS + ", pdf p.35, pdf p.38-40 §2.7, pdf p.49; " + DEF + ":350-380", "et-spec")
f("l2.subbank-busy", "bank",
  "With 2-cycle RAMs a sub-bank accepts a new request only every other cycle (3-cycle RAMs: every third). Operations that need two RAM passes (a fill that may evict, an atomic) reserve bubble slots, because the pipeline never stalls once a request is scheduled.",
  2, "cycles between requests to one sub-bank", SCS + ", pdf p.35-36 §2.6, pdf p.35 §2.5", "et-spec")
f("l2.ramdelay", "bank",
  "RAM access time is 2, 3 or 4 cycles, one setting (esr_sc_ram_delay) for all three RAM types, set at boot. The design intends 2, which is the default.",
  2, "cycles", SCS + ", pdf p.9, pdf p.48 §2.14.6.1, pdf p.101; " + DEF + ":260", "et-spec",
  note="The value programmed on the cards has not been read.")
f("l2.stages", "pipeline",
  "Read-hit pipeline stages (2-cycle RAMs): ag (reqq allocate), ad (dependencies), rqa (reqq arbitration), tap, ta, ta0, ta1 (tag and tag-state RAM access), te (tag ECC), tc (tag compare: hit, victim), dap, da, da0, da1 (data RAM access), de (data ECC), dc (data complete: OR'd across the sub-banks, then to the response mux, or the dataq if the mux is busy).",
  15, "named stages", SCS + ", pdf p.44 figure, pdf p.45-46 §2.14.1", "et-spec")
f("l2.stages.budget", "pipeline",
  "If each named stage is one cycle, the 15 stages from reqq allocation to data complete account for 15 of the spec's 21-cycle L2 hit, leaving about 6 cycles for the request crossbar, response mux and response crossbar. The spec cites an 'L2 and L3 Pipeline stages Spreadsheet' that has the real budget, which we do not have.",
  6, "cycles (xbars + rspmux, inferred)", SCS + ", pdf p.11 Table 1, pdf p.44-46, pdf p.131 ref. 3", "et-derived",
  note="One cycle per stage is an assumption.")
f("l2.throughput", "pipeline",
  "Consecutive operations to different sub-banks can issue every cycle. Operations that can create a victim (fills, writes, write-arounds, locks) run at one per 4, 6 or 8 cycles per sub-bank (RAM delay 2, 3, 4), because read and write slots are both reserved. The tag is written 4 cycles after the victim is chosen (2-cycle RAMs).",
  None, None, SCS + ", pdf p.44-45 §2.14", "et-spec")
f("l2.rbuf", "read buffer",
  "Read buffer (RBUF): an 8-entry fully associative mini-cache of clean lines per bank (2 KB per shire). Lines are installed on L2 and scratchpad read hits. Requests are checked against it when they are allocated a reqq entry, and hits are served from it without touching the RAM panels, 'as these memory panels are slow and power hungry'. Anything that will change the data RAM clears the entry, and a 4-entry FIFO holds hit responses.",
  8, "lines per bank", SCS + ", pdf p.9 §1.1, pdf p.40 §2.8; " + DEF + ":273-275", "et-spec",
  page_link=MH + "#load-latency-against-working-set-size")
f("l2.rbuf.enabled", "read buffer",
  "The RBUF is on by default (esr_sc_l2_rbuf_enable = esr_sc_scp_rbuf_enable = 1 in the RTL's ESR init), and the cards show it: a 36-cycle plateau for working sets of 768 B to 2 KB, then 47 cycles from 4 KB, on all three cards.",
  2048, "bytes per shire", ESRB + ":311-312; " + LAT + " items[LAT-M1] (knees between 512/768 B and 2/4 KB)", "et-derived",
  card=ALL3, page_link=MH + "#load-latency-against-working-set-size")
f("l2.rbuf.storage", "read buffer",
  "What the RBUF is built from on silicon is not documented. The Ainekko reimplementation keeps it as 8 x 512-bit registers (flip-flops) holding ECC-corrected data, with an LRU replacement arbiter and a 7-stage pending-install pipeline.",
  None, None, CEM + "/shirecache/rtl/shirecache_pipe_rbuf.sv:1-20, 105, 416-419", "unknown")
f("l2.cbuf", "bank",
  "Each bank has a 32-entry coalescing buffer that merges write-arounds (TensorStores to L3 or a remote scratchpad) in the L2. It flushes a line once all four 128-bit quadwords are written, or on an explicit flush.",
  32, "entries per bank", SCS + ", pdf p.9 §1.1, pdf p.42 §2.10; " + DEF + ":282", "et-spec", page_link=CHIP)
f("l2.atomic", "bank",
  "Each bank has an atomic unit (32-, 64- and 256-bit operands: swap, add, and, or, xor, min/max signed and unsigned, float min/max). An atomic keeps its sub-bank busy from the read through the operation to the write.",
  None, None, SCS + ", pdf p.36 item 3, pdf p.40-41 §2.9", "et-spec")
f("l2.zero-state", "bank",
  "Each way's tag state has a 'zero' bit: the data RAM is not read and zeros are returned. REQ_Lock sets it (a missing line is installed without a fill), and esr_sc_zero_state_enable (default 1) 'prevents reading/writing from the data RAMs if the content of the data is all zeros'.",
  None, None, SCS + ", pdf p.47 Table 12, pdf p.78 §3.9, pdf p.101", "et-spec",
  note="Whether an ordinary write of all-zero data sets the bit is not stated (ask). It matters for reading the zeros-vs-random energy gap.")
f("l2.ecc", "bank",
  "All shire-cache RAMs have SECDED ECC (single-error correct, double-error detect): 6 bits per tag, 7 per tag-state row and 8 per 64 data bits, checked in stages te and de. On this chip ECC covers only the L2/L3/scratchpad SRAM and the instruction cache. Background ECC scrubbing is a reserved bit, 'implemented in Gepardo', a later chip.",
  8, "ECC bits per 64 data bits", SCS + ", pdf p.9, pdf p.48-49 §2.14.6.2, pdf p.99; docs/findings/15-earlier-findings.md:65-66", "et-spec")
f("l2.sleep", "power",
  "The RAMs can be put into deep sleep (low-leakage retention) or shut down only for shires that are not operational (esr_sc_ram_deep_sleep / esr_sc_ram_shut_down). The cards show no array wake-up: an L2 hit reads 49.5 cycles after any idle from 1.7 us to 27 ms.",
  0, "cycles of wake-up", SCS + ", pdf p.101; docs/findings/16-dvfs-and-leakage.md:123; " + CLAIMS + ":181, 420",
  "et-measured", card=ALL3, page_link=U + "et-soc1-dvfs-leakage")
f("l2.clock-gating", "power",
  "Module-level clock gaters (esr_sc_clk_gate_disable) stop the bank's clock when it has no outstanding requests (errata RTLMIN-6235, which is why the bank's cycle counter under-counts). The reimplementation gates each RAM's clock on only for the ram_delay cycles of an access.",
  None, None, SCS + ", pdf p.97 §4.1; " + ERR + ", pdf p.82 §4.3; " + CEM + "/shirecache/rtl/shirecache_pipe_data_ram_wrap.sv:1-7, 46-66", "et-spec",
  note="The per-access RAM clock enable is from the Ainekko reimplementation, not the ET-SoC-1 RTL.")
f("l2.power-goal", "energy",
  "The spec's power target is 'TBD. Goal is 100 MW for the entire Shire Cache running benchmark'. The unit is presumably mW.",
  100, "mW (goal, per shire cache)", SCS + ", pdf p.11", "et-spec")
f("l2.all-inv", "power",
  "At power-up the index CacheOp state machine runs Idx_All_Inv, which writes zeros to every way of the tag-state RAM, one index per cycle, starting about 256 clocks after reset (skipped if BIST is running).",
  256, "clocks after reset", SCS + ", pdf p.88-89 §3.14", "et-spec")
f("l2.spec-version", "provenance",
  "The Shire Cache Specification in hand is v1.1 from core-et's Erbium branch. It also documents later variants ('Atomic (with NEMI)', ECC scrub 'implemented in Gepardo'), while it calls '4M/Shire, 4 banks/Shire, 4 sub-banks/bank' the POR for the first SoC. Latencies measured on the cards match its Table 1 up to a constant (l2.lat.overhead).",
  None, None, SCS + ", pdf p.1, p.4 §3.8, p.9, p.99; " + HIER + ":915 (sources note)", "et-spec",
  note="Facts marked et-spec from this document are for the design; where silicon could differ (macros, trims, partition) the diagram should say so.")
f("l2.hpf", "provenance",
  "The original RTL had an L2 hardware-prefetcher interface (shire_cache_bank_l2hpf). The reimplementation stubs it out by default (L2HpfImplemented = 0; 'assumes shire cache bank read buffer not enabled'). No source says whether ET-SoC-1 silicon has an L2 prefetcher; the L1 has none.",
  None, None, CEM + "/shirecache/rtl/shirecache_bank_l2hpf.sv:1-18; " + CEM + "/shirecache/README.md:352-356; docs/research/counters-and-dram.md:450", "unknown")
f("l2.floorplan", "provenance",
  "Where the four banks, their sixteen sub-banks and 96 macros sit inside the shire tile, and how long the crossbar wires to each neighbourhood are, is in no source; Figure 1 of the Minion Shire Description is a logical diagram.",
  None, None, MSD + ", pdf p.5 Figure 1", "unknown", page_link=HUB + "#ask-shire-floorplan")
f("l2.perfmon", "observability",
  "Each bank has a performance monitor: a cycle counter and two 40-bit event counters, which can count RBUF hits, tag hits and misses, victims and opcodes. They are M-mode registers. A U-mode kernel can only read them (syscall 9) with the firmware's default qualifier, which counts all read-type requests and does not separate hits from misses.",
  3, "counters per bank", SCS + ", pdf p.104-109 §4.9; docs/research/counters-and-dram.md:186-191, 252, 259", "et-spec",
  page_link=ANAT + "#what-the-chip-lets-you-see")

# ---------------------------------------------------------------- latency
f("l2.lat.spec", "latency",
  "Idle-cache latencies in shire clocks, from the neighbourhood's ET-Link request to its response, crossbars included: L2 hit 21, read-buffer hit 10, L2 miss 34 + NoC and L3/memory latency.",
  21, "shire clocks (L2 hit)", SCS + ", pdf p.11 Table 1", "et-spec", page_link=MH + "#load-latency-against-working-set-size")
f("l2.lat.measured", "latency",
  "Load-to-use latency by pointer chase at 600 MHz: read-buffer hit 36.00 cycles (60 ns) and L2 or own-scratchpad hit 47.00 cycles (78 ns) on hart 0; hart 1 pays 3 more (39.0 and 50.0). Every pass on every card fell within 35.998-36.006 and 46.998-47.024.",
  47, "cycles", CLAIMS + ":421; " + LAT + " items[LAT-M1].per_card.<card>.passes[] (RB, L2, hart1)", "et-measured",
  card=ALL3, page_link=MH + "#load-latency-against-working-set-size")
f("l2.lat.overhead", "latency",
  "Measured minus spec is 26 cycles for both (47 - 21 = 36 - 10), so the path outside the shire cache is a constant and the 11-cycle read-buffer saving is all inside the bank. That is consistent with one shire clock being one minion cycle (l2.clock). Of the 26, the neighbourhood's request and response datapaths take at least 6 + 6, leaving about 14 for the minion's L1 miss detection, miss handler and fill-to-use.",
  26, "cycles outside the shire cache", "derived from " + SCS + ", pdf p.11 Table 1, " + CLAIMS + ":421 and " + NMAS + ", pdf p.20-21", "et-derived",
  page_link=MH + "#load-latency-against-working-set-size")
f("l2.lat.ladder", "latency",
  "Timing one load after an evict_va to L2 gives two populations: about 37 cycles when the line is still in the bank's read buffer and 48 from the array. The 19 September histogram has 37: 2,187, 38: 780, 48: 1,117, 49: 407 loads over 1,500 lines x 3. The version-3 ladder median is 49 cycles on every card.",
  48, "cycles (array)", MP + " decomp.l2.hist; " + ANAT_T + ":890-892; " + CLAIMS + ":417", "et-measured",
  card="aifoundry2 (19 Sep); all three (26 Sep)", page_link=ANAT + "#l3-110-cycles-plus-12-per-hop",
  note="memprobe's timer correction (workloads/memprobe/README.md:36-39: subtract 5 so a timed L1 hit reads 5) is not the pointer chase's method; its 37/48 correspond to the chase's 36/47.")
f("l2.lat.miss", "latency",
  "A local L3 hit costs 110 cycles, of which about 48 are the L1 and L2 lookups and the L2 miss (if a miss costs what a hit does) and about 62 are the home slice; each mesh hop adds 12 cycles.",
  48, "cycles (L1 + L2 lookup and miss)", ANAT_T + ":880-881", "et-measured", card="aifoundry2",
  page_link=ANAT + "#l3-110-cycles-plus-12-per-hop")

# ---------------------------------------------------------------- bandwidth
f("l2.bw.measured", "bandwidth",
  "With 1 KB tensor loads on every minion the L2 delivers 2.45 TB/s chip-wide: 4.0 B per minion-cycle = 128 B per shire-cycle, half the four banks' 256 B per shire-cycle. The own scratchpad gives the same (2.46 TB/s).",
  2.45, "TB/s", CLAIMS + ":380, 546; docs/findings/15-earlier-findings.md:98", "et-measured", card=ALL3,
  page_link=MH + "#the-hierarchy-as-a-spec-sheet")
f("l2.bw.per-bank", "bandwidth",
  "128 B per shire-cycle is one 64 B line every 2 cycles per bank (0.5 lines per bank-cycle). The rate is exact (3.999-4.000 B per minion-cycle, the same for L2 and scratchpad), which points to a structural 2-cycle limit rather than a latency or concurrency limit. The spec lets a bank return one line per cycle when successive requests go to different sub-banks, and 1 KB tensor loads do rotate sub-banks (PA[9:8]).",
  0.5, "lines per bank-cycle", "derived from l2.bw.measured and " + SCS + ", pdf p.6, p.44", "et-derived",
  note="Which block sets the 2-cycle limit is unknown (ask).")
f("l2.bw.gather", "bandwidth",
  "Random-word gathers from the L2 (one line per element) reach 27.4 G lines/s chip-wide, 1.15x the bound set by two miss handlers per minion. A second hart adds nothing.",
  27.4, "G lines/s", CLAIMS + ":502, 504", "et-measured", card=ALL3, page_link=MH + "#irregular-access-gathers-and-scatters")

# ---------------------------------------------------------------- energy
f("l2.e.level", "energy",
  "Reading the L2 with 1 KB tensor loads on every minion at 600 MHz costs 3.11 pJ/B [1.42-4.99] above idle (per card: aifoundry2 2.64, aifoundry3 2.83, aifoundry1-c1 3.86). That is about 199 pJ per 64 B line for the whole path.",
  3.11, "pJ/B", EM4 + ":26; docs/reports/data/2026-09-23-energy-manual/manual.json reruns.levels_pj_per_byte.l2", "et-measured",
  card=ALL3, page_link=EMAN, note="The buffer's contents were not set; the scratchpad rows below control the data.")
f("l2.e.scp-contents", "energy",
  "The same arrays read as the shire's own scratchpad (no tag compare) cost 2.25 pJ/B [2.06-2.61] filled with zeros and 4.40 [3.94-5.08] filled with random data: about 144 vs 282 pJ per 64 B line, 2x for the data.",
  4.40, "pJ/B (random)", EM4 + ":29-30; " + CLAIMS + ":466", "et-measured", card=ALL3, page_link=EMAN)
f("l2.e.tload-tstore", "energy",
  "Tensor load from the own scratchpad: 2.12 (zeros) / 4.43 (random) pJ/B. Tensor store into it: 4.65 / 8.58 pJ/B. A scratchpad write costs about twice a read.",
  8.58, "pJ/B (store, random)", EM4 + ":13-14, 40", "et-measured", card=ALL3, page_link=EMAN)
f("l2.e.l2-minus-scp", "energy",
  "At a steady 600 MHz the L2 costs about what the scratchpad costs per byte: pass by pass, the L2-minus-scratchpad difference includes zero on each card. The tag lookup does not show up in board power.",
  None, None, HIER + ":858", "et-measured", card=ALL3, page_link=MH + "#the-hierarchy-as-a-spec-sheet")
f("l2.e.rails", "energy",
  "Split by rail (19 September, one card, 8-byte loads each moving a 64 B line): an L2 hit costs 112 pJ on the SRAM rail, 64 pJ on the minion rail and 2 pJ on the NoC rail, of 183 pJ on the rail trace (214 pJ by board power). 'An L2 hit is mostly SRAM.'",
  112, "pJ per line on the SRAM rail", MP + " power.l2.pj_per_load; " + ANAT_T + ":1091-1092", "et-measured",
  card="aifoundry2", page_link=ANAT + "#where-the-energy-goes",
  note="The page calls these values superseded by the energy manual's; it is the only per-rail split of an L2 hit.")
f("l2.e.bit", "energy",
  "Streaming TensorLoads from the L2 at 2.4 TB/s adds 6.2 W: 2.6 pJ/B = 0.3 pJ per bit, a switched capacitance of 0.038 nF per minion.",
  0.3, "pJ/bit", "docs/findings/13-why-low-power.md:62, 113-115; " + CLAIMS + ":144", "et-measured", card="aifoundry2",
  page_link=U + "et-soc1-why-low-power")
f("l2.e.l1fill", "energy",
  "Filling one 64 B line from the scratchpad into the L1: 101 pJ on zeros and 205 pJ on random data (both cards pooled).",
  205, "pJ per line (random)", CLAIMS + ":306", "et-measured", card="aifoundry2, aifoundry3", page_link=EMAN)
f("l2.e.scalar", "energy",
  "One random flw from the L2 (a line per load) costs 336 pJ [315-369] at 27.5 G/s. One fsw costs 774 pJ: the store allocates the line and writes it back.",
  336, "pJ per load", CLAIMS + ":509; " + EM4 + ":55", "et-measured", card=ALL3, page_link=EMAN)
f("l2.e.gather-line", "energy",
  "A gather from the L2 costs 104 pJ per instruction plus 338 pJ per line it fetches (least-squares fit over seven patterns).",
  338, "pJ per line", CLAIMS + ":512", "et-derived", card=ALL3, page_link=MH + "#irregular-access-gathers-and-scatters")
f("l2.e.shire", "energy",
  "At full L2 bandwidth (2.45 TB/s at 3.11 pJ/B), the whole path draws about 7.6 W above idle, about 240 mW per shire. If the 19 September rail split holds (61% on the SRAM rail), roughly 145 mW of that is on the SRAM rail, the same order as the spec's 100 mW goal.",
  240, "mW per shire above idle", "derived from l2.bw.measured, l2.e.level, l2.e.rails, l2.power-goal", "et-derived")
f("l2.leak", "power",
  "SRAM-rail power at idle: 2.00 W for the chip (about 59 mW per minion shire if split evenly over 34); 1.60 W at 67 C and 2.63 W at 82 C on aifoundry2; 0.051-0.066 W per degree C on the other cards.",
  2.0, "W (chip, idle)", CLAIMS + ":184, 312, 473; docs/findings/16-dvfs-and-leakage.md:141", "et-measured",
  card=ALL3, page_link=U + "et-soc1-dvfs-leakage",
  note="The per-shire split assumes the rail feeds only the 34 minion shires' caches evenly. What else is on the rail is unknown (l2.rail.hv-logic).")

# ---------------------------------------------------------------- access sequences
SEQ = []


def step(seq, n, block, action, kind, source, latency=None, energy=None, circuit=None, note=None):
    SEQ.append(dict(
        id="l2.seq.%s.%02d" % (seq, n), level="L2", topic="access-sequence", sequence=seq, step=n,
        block=block, action=action,
        statement="%s: %s" % (block, action), value=None, unit=None,
        latency=latency, energy=energy, circuit=circuit or [], source=source, kind=kind,
        card=None, page_link=None, note=note))


def c(element, switches, kind, note=None):
    d = dict(element=element, switches=switches, kind=kind)
    if note:
        d["note"] = note
    return d


# the transistor-level pieces reused by several steps (GENERIC unless stated)
SRAM_READ = [
    c("row decoder (predecoders + NAND/NOR gates)", "address bits select one row; one final decoder gate switches", "generic"),
    c("wordline driver", "one inverter-chain driver raises one wordline to VDD (a read-assist setting may lower it slightly)", "generic",
      "The ET trim at reset is RA=1 for tag/data macros (l2.trim.reset); what RA does electrically is vendor-specific"),
    c("bitline precharge PMOS", "turned off just before the wordline rises; bitline pairs float at VDD", "generic"),
    c("bitcell access transistors (2 NMOS per 6T cell)", "turn on for every cell in the selected row", "generic",
      "6T is an assumption; the ET bitcell is unknown (l2.storage-question)"),
    c("bitcell pull-down NMOS", "in each cell the side storing 0 discharges its bitline by ~100 mV", "generic"),
    c("column mux", "picks one of the muxed columns per output bit ('m4' may mean 4:1, unconfirmed)", "generic"),
    c("sense amplifier (cross-coupled latch)", "sense-enable fires and the latch resolves the small differential to full swing", "generic"),
    c("output latch / flops", "capture the macro's data out on the macro's read-delay edge", "generic"),
    c("bitline precharge PMOS (again)", "turn back on and restore the discharged bitlines to VDD: most of a read's array energy", "generic"),
]
SRAM_WRITE = [
    c("row decoder + wordline driver", "one wordline rises", "generic"),
    c("write drivers", "pull one bitline of each written column to 0 V and hold the other at VDD (write assist may drive it below 0 V)", "generic",
      "ET trim at reset: WA=7, WPULSE=0 for tag/data macros (l2.trim.reset)"),
    c("bitcell access NMOS + cross-coupled inverters", "the 0 bitline pulls the cell's 1 node below the inverter trip point and the cell flips (only cells whose value changes flip)", "generic"),
    c("bitline precharge PMOS", "restore the fully discharged bitlines: a write swings full rail, so it costs more than a read", "generic"),
]
LOGIC = lambda what: [c("static CMOS standard cells and flip-flops", what, "generic")]

# A. load, L2 array hit ---------------------------------------------------------------
S = "load-hit"
step(S, 1, "minion L1 / miss handler (LV region, minion rail)",
     "The load misses the L1; one of the two miss handlers allocates and puts a line-fill request (REQ_Read, line address) on the miss interface into the neighbourhood's Miss FF.",
     "et-spec", NMAS + ", pdf p.15-16 §4.3.1; " + DCD + ", pdf p.34-36 §3.6",
     circuit=LOGIC("the miss handler's state machine and request flops toggle"))
step(S, 2, "neighbourhood request datapath -> bank FIFO (LV -> HV crossing)",
     "2:1 minion arbiter, 13:1 round-robin arbiter, pre-processing, then the output FIFO of the bank picked by PA[7:6]. That FIFO is a semi-synchronous VC FIFO whose cells sit in the HV region, with level shifters at the boundary.",
     "et-spec", NMAS + ", pdf p.16-20 §4.3, pdf p.45 §7.1",
     latency="min 6 cycles (minion request)",
     circuit=LOGIC("arbiter and mux trees; FIFO write") + [
         c("voltage level shifters (e.g. a cross-coupled PMOS pair over an NMOS differential input)",
           "each request bit crossing from the minion rail (~0.52 V) into the HV region (its voltage is not documented; the SRAM rail reads ~0.70 V) flips a level-shifter cell", "generic",
           "that level shifters exist inside the VC FIFO is et-spec (NMAS p.45); their circuit is GENERIC")])
step(S, 3, "request crossbar (req_xbar)",
     "The request enters its bank's catch FIFO for that neighbourhood, and the bank's round-robin arbiter admits it (one request per bank per cycle). The crossbar is routed on top of the four banks.",
     "et-spec", SCS + ", pdf p.30-31 §2.1-2.2",
     circuit=LOGIC("arbiter, mux") + [c("repeated wires over the banks", "address/control wires toggle across the bank area", "generic")])
step(S, 4, "reqq allocate (stages ag, ad)",
     "A reqq entry is allocated. The address is compared with every in-flight entry (ordering) and with the 8 RBUF tags. Here the RBUF misses, so the request is eligible for the pipeline.",
     "et-spec", SCS + ", pdf p.37 §2.6.1, pdf p.40 §2.8, pdf p.45 §2.14.1.1-2",
     circuit=LOGIC("XOR/XNOR comparator trees against 64 reqq addresses and 8 RBUF tags"))
step(S, 5, "reqq arbitration (stage rqa)",
     "Round-robin per sub-bank, L3 requests first, busy sub-banks masked; the winner's information is muxed out of the reqq.",
     "et-spec", SCS + ", pdf p.36 Figure 8, pdf p.45 §2.14.1.3", circuit=LOGIC("arbiters and a 64:1 mux"))
step(S, 6, "tag RAM + tag-state RAM of one sub-bank (stages tap, ta, ta0, ta1)",
     "The sub-bank chosen by PA[9:8] reads the set's row (a Mode 0 L2 set lives in rows 0x280-0x2FF): the 116-bit tag row (all four tags + ECC) from the 1024x116 single-port macro and the 40-bit state row from the 1024x40 two-port file. The other sub-banks' RAM inputs stay frozen.",
     "et-spec", SCS + ", pdf p.44-46, pdf p.47 §2.14.2-3, pdf p.51",
     latency="2 cycles (ram_delay = 2)",
     circuit=SRAM_READ + [c("two-port register file read port (tag state)",
                            "separate read wordline and single-ended read bitline (typical 8T RF: 2-transistor read stack)", "generic")])
step(S, 7, "tag ECC (stage te)", "SECDED check and repair of each way's 23+6-bit tag.",
     "et-spec", SCS + ", pdf p.46 §2.14.1.8, pdf p.48-49",
     circuit=LOGIC("XOR trees compute a 6-bit syndrome per way; correction muxes"))
step(S, 8, "tag compare (stage tc) + tag-state write",
     "Four 23-bit comparators find the hit way. The new LRU code (5 bits) and flags are written back through the tag-state file's write port in the same pass, and hit/victim status goes to the reqq.",
     "et-spec", SCS + ", pdf p.45 (state RAM two-ported), pdf p.46 §2.14.1.9, pdf p.47-48 §2.14.4",
     circuit=LOGIC("4 x 23-bit equality comparators, LRU encode/decode logic") + [
         c("two-port register file write port", "write wordline + write drivers flip the LRU bits that change", "generic")])
step(S, 9, "data RAM, 4 panels of one sub-bank (stages dap, da, da0, da1)",
     "Row {hit way, set} is read from the four 4096x144 panels: 4 x 144 = 576 bits (512 data + 64 ECC). Only this sub-bank's data macros are clocked; a partial access would enable fewer panels.",
     "et-spec", SCS + ", pdf p.44-46, pdf p.48 §2.14.5, pdf p.51; " + DEF + ":253",
     latency="2 cycles (ram_delay = 2)",
     energy="the SRAM rail carried ~112 pJ per L2 hit (19 Sep); how much of that is this data read, versus the tag/state reads, crossbars and periphery, is unknown",
     circuit=SRAM_READ, note="4 macros x one wordline each; 576 sense amplifiers fire")
step(S, 10, "data ECC (stage de)", "Eight SECDED checks, one per 64-bit dword (8 check bits each), correcting single-bit errors.",
     "et-spec", SCS + ", pdf p.46 §2.14.1.14, pdf p.48-49", circuit=LOGIC("8 XOR syndrome trees and correction muxes"))
step(S, 11, "data complete (stage dc) + RBUF install",
     "The line is OR'd with the other (idle) sub-banks' outputs and sent to the response mux (or parked in the dataq if the mux is busy). It is installed in the bank's read buffer.",
     "et-spec", SCS + ", pdf p.40 §2.8, pdf p.46 §2.14.1.15",
     circuit=LOGIC("OR tree across 4 sub-banks; 512 RBUF flops load the line (flops in the reimplementation; silicon unknown)"))
step(S, 12, "response mux (rspmux) + response crossbar",
     "Per-neighbourhood queue and arbiter, then rsp_xbar back to the requesting neighbourhood.",
     "et-spec", SCS + ", pdf p.43-44 §2.12, pdf p.32 §2.2",
     circuit=LOGIC("arbiters, 512-bit muxes") + [c("repeated 512-bit wires", "data wires toggle with the data: zeros toggle few, random data about half", "generic")])
step(S, 13, "neighbourhood response path (HV -> LV) -> L1 fill -> load completes",
     "VC FIFO (level shifters back down to the minion rail), Fill FIFO, the minion's Fill FF splits the line into two 256-bit beats, the DCache writes the line and the load returns its word.",
     "et-spec", NMAS + ", pdf p.20-23 §4.4",
     latency="min 6 cycles in the neighbourhood; whole load 47.00 cycles = 78 ns (measured)",
     energy="whole path ~199 pJ per line above idle (3.11 pJ/B, energy manual); 205 pJ random / 101 pJ zeros to fill an L1 line from the scratchpad",
     circuit=LOGIC("FIFO and fill flops") + [
         c("level shifters (HV -> LV)", "each response bit crosses back down", "generic"),
         c("L1 data array", "is latch-based RAM (LRAM), not SRAM: see the L1 diagram", "et-spec", DCD + ", pdf p.29")])

# B. load, read-buffer hit ---------------------------------------------------------------
S = "load-rbuf-hit"
step(S, 1, "minion -> neighbourhood -> req_xbar", "As load-hit steps 1-3.", "et-spec",
     NMAS + ", pdf p.16-20; " + SCS + ", pdf p.30-31", latency="min 6 cycles in the neighbourhood")
step(S, 2, "reqq allocate: RBUF tag match",
     "The address matches one of the bank's 8 RBUF entries at allocation, so the request goes to the RBUF instead of the pipeline. No tag, tag-state or data macro is accessed.",
     "et-spec", SCS + ", pdf p.9, pdf p.40 §2.8",
     circuit=LOGIC("8 address comparators hit; RBUF valid bit tracked in the reqq entry"))
step(S, 3, "RBUF read -> RBUF FIFO -> rspmux",
     "The entry's 512 bits are read out (an 8:1 mux over registers in the reimplementation) into the 4-entry RBUF FIFO, then the response mux.",
     "et-spec", SCS + ", pdf p.40, pdf p.43 item 6; " + DEF + ":273-275",
     circuit=LOGIC("8:1 x 512-bit mux, FIFO write") + [c("RBUF storage", "flip-flops in the reimplementation; silicon unknown", "unknown")])
step(S, 4, "rsp_xbar -> neighbourhood -> L1", "As load-hit steps 12-13.", "et-spec", SCS + ", pdf p.32; " + NMAS + ", pdf p.20-23",
     latency="spec 10 shire clocks inside the cache; whole load 36.00 cycles = 60 ns (measured)",
     energy="not measured (the RBUF exists to save the ~100+ pJ array read; no experiment isolates it)")

# C. store = full-line write from the L1 --------------------------------------------------
S = "store-writeback"
step(S, 1, "minion L1 evict (dirty line)",
     "The L1 is write-back: a store stays in the L1 until its line is evicted. The eviction is a full-line REQ_Write sent as two 256-bit transfers on the evict interface, re-joined in the Evict FF (+1 cycle, 3 in all).",
     "et-spec", DCD + ", pdf p.33; " + NMAS + ", pdf p.16-17 §4.3.1",
     circuit=LOGIC("evict flops capture 2 x 256 bits"))
step(S, 2, "neighbourhood -> req_xbar (512-bit request takes 2 cycles)",
     "The same path as a load, but with data: 512-bit requests are served every other cycle.", "et-spec", NMAS + ", pdf p.19-20",
     circuit=LOGIC("512 data wires toggle with the line's data") + [c("level shifters (LV -> HV)", "every data bit crosses up", "generic")])
step(S, 3, "reqq + dataq write", "A reqq entry is allocated and the 64 B of data are written into its dataq entry (one of the 5 dataq write sources).",
     "et-spec", SCS + ", pdf p.38-39 §2.7, pdf p.58 §3.4.1",
     circuit=[c("dataq register file (logical RAM mbq, 1-cycle)", "one row written: write wordline + write drivers", "generic")])
step(S, 4, "pipeline L2_Write: tag + tag-state read, compare", "As load-hit steps 6-8. The dirty bits (qwen = 0xF) and LRU are updated in the state write.",
     "et-spec", SCS + ", pdf p.47, pdf p.58-59", circuit=SRAM_READ)
step(S, 5, "data RAM write (hit way)",
     "The data comes back out of the dataq and is written to row {way, set} of the four panels (only panels with written quadwords are enabled). If the tag missed, the LRU way is the victim: a clean victim is dropped silently, and a dirty one is read in a reserved slot, then overwritten and sent to L3 on to_l3. A full-line write needs no fill.",
     "et-spec", SCS + ", pdf p.44-45, pdf p.48, pdf p.58-59 §3.4.1 Figure 18",
     circuit=SRAM_WRITE, energy="a scratchpad write is ~2x a read (tensor store 4.65 zeros / 8.58 random pJ/B)")
step(S, 6, "REP_Ack back to the minion", "Sent as soon as the cache write completes; the reqq entry frees when any victim's mesh write is acknowledged.",
     "et-spec", SCS + ", pdf p.59",
     energy="a random fsw through the L1 to the L2 costs 774 pJ per store (allocate + write-back)")

# D. miss, refill, victim ------------------------------------------------------------------
S = "miss-refill"
step(S, 1, "tag compare misses (stage tc)", "As load-hit steps 1-8. No way matches, so tc reports a miss to the reqq and the data stages are skipped for this pass.",
     "et-spec", SCS + ", pdf p.54-55 Figure 13", circuit=SRAM_READ)
step(S, 2, "bank mesh (to_l3 master) -> NoC",
     "The reqq issues Mesh_Read on the bank's 512-bit to_l3 port. It is arbitrated with the other banks onto 4 mesh lanes and crosses to the NoC clock and voltage through a VCFIFO with 2-stage synchronizers. The read goes to the line's home L3 slice (see the L3 diagram).",
     "et-spec", SCS + ", pdf p.8, pdf p.11 (VCFIFO), pdf p.32-33 §2.3, pdf p.43 §2.11",
     latency="spec: 34 shire clocks + NoC and L3/memory latency; measured local L3 hit 110 cycles in all")
step(S, 3, "fill data returns", "The mesh response goes straight to the neighbourhood (lowest latency) and is also written into the reqq entry's dataq line.",
     "et-spec", SCS + ", pdf p.43 §2.11, pdf p.54")
step(S, 4, "L2_Fill through the pipeline",
     "The tag-state read picks the LRU way (never a locked way). If that way is dirty (qwen != 0), its data row is read first in a reserved slot, becoming the victim. Then the new tag, state and 576-bit data row are written. The pipeline reserves both slots, so a fill runs at one per 4 cycles per sub-bank.",
     "et-spec", SCS + ", pdf p.44-45, pdf p.47-48, pdf p.54-55",
     circuit=SRAM_READ + SRAM_WRITE)
step(S, 5, "victim write-back", "A dirty victim goes to to_l3 as a write (straight from the pipeline if the mesh is free, else via the dataq). Later reads of that address queue behind it; the entry frees when the write is acknowledged.",
     "et-spec", SCS + ", pdf p.37 (victims head the linked list), pdf p.54-55")

# E. what stands in for refresh ------------------------------------------------------------
S = "no-refresh"
step(S, 1, "static storage", "SRAM cells hold their data as long as the rail is up: no refresh cycles, unlike DRAM. The cost of keeping them is leakage through every cell's off transistors, which grows with temperature.",
     "generic", "textbook SRAM", energy="SRAM rail at idle 1.60 W at 67 C -> 2.63 W at 82 C (aifoundry2)",
     note="Applies only if the arrays are SRAM (l2.storage-question).")
step(S, 2, "no scrub, no sleep in service", "ET-SoC-1 has no background ECC scrub (a reserved bit, 'implemented in Gepardo'). Deep sleep and shut-down are only for non-operational shires, and the cards show no wake-up latency after idle. The only whole-array sweep is the power-up Idx_All_Inv of the tag-state RAM.",
     "et-spec", SCS + ", pdf p.99, pdf p.101, pdf p.88-89; docs/findings/16-dvfs-and-leakage.md:123")

ALLITEMS = F + SEQ
ids = [x["id"] for x in ALLITEMS]
assert len(ids) == len(set(ids)), "duplicate ids"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as fh:
    json.dump(ALLITEMS, fh, indent=1, ensure_ascii=False)
from collections import Counter
print(len(F), "facts,", len(SEQ), "sequence steps ->", OUT)
print(Counter(x["kind"] for x in ALLITEMS))
