# Builds facts-scp.json: the scratchpad (SCP) level of "Anatomy of a memory access".
# Every ET-specific number is read from a repo file here or quoted with file + line/page/field.
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "facts-scp.json")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))   # the repository root
EMR = "docs/reports/data/2026-09-23-energy-manual"   # as cited in sources
EM = os.path.join(REPO, EMR)

# ---------- numbers read from the repo (not typed) ----------
cat = json.load(open(EM + "/catalogue.json"))
man = json.load(open(EM + "/manual.json"))
lat = json.load(open(REPO + "/docs/reports/data/2026-09-25-claims-v3/results/lat.json"))

def m(x):
    return x["mean"] if isinstance(x, dict) else x

rails = {}
for card, blk in cat["cards"].items():
    for key in ["tload/scp/zeros", "tload/scp/random", "tstore/scp/zeros", "tstore/scp/random"]:
        e = blk["summary"][key]
        bps = m(e["bytes_per_s"])
        r = {k: m(v) for k, v in e["rails_over_w"].items()}
        rails[(card, key)] = dict(
            sram_pjB=r["sram_w"] / bps * 1e12, minion_pjB=r["minion_w"] / bps * 1e12,
            noc_pjB=r["noc_w"] / bps * 1e12, sram_w=r["sram_w"], over_idle=m(e["over_idle_w"]),
            board_pjB=m(e["pj_per_byte"]), gbs=bps / 1e9)

lv = man["reruns"]["levels_by_contents_pj_per_byte"]
relay = man["reruns"]["relay_pj_per_byte"]
def lvl(c, k):
    v = lv[c][k]; return v["mean"], v["lo"], v["hi"], {cc: round(x["mean"], 2) for cc, x in v["per_card"].items()}

s2 = {it["item"]: it for it in (lat["items"] if isinstance(lat, dict) else lat)}["LAT-S2"]["per_card"]
tl = {c: {k: s2[c]["pass_means"][k]["mean"] for k in ("scp4", "scp8", "scp16", "l24", "l216")} for c in s2}

A2 = "aifoundry2"; A3 = "aifoundry3"; A1 = "aifoundry1-c1"
ALL = "aifoundry2, aifoundry3, aifoundry1-c1"
r2l = rails[(A2, "tload/scp/random")]; r2z = rails[(A2, "tload/scp/zeros")]
r2sl = rails[(A2, "tstore/scp/random")]; r2sz = rails[(A2, "tstore/scp/zeros")]

U = "https://spacesheep.dev/@yaroslavvb/"
MH = U + "et-soc1-memory-hierarchy"; EMU = U + "et-soc1-energy-manual"; RL = U + "et-soc1-on-chip-relay"
HL = U + "et-soc1-hot-line"; PT = U + "et-soc1-power-temperature"; HX = U + "et-soc1-horace-experiment"
LO = U + "et-soc1-limits-of-observability"; RP = U + "et-soc1-ridge-points"; CD = U + "et-soc1-chip-diagram"

SCS = "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf"          # v1.1; pages are pdf pages
PRM = "external/et-man/ET Programmer's Reference Manual.pdf"
NMAS = "external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf"
SHD = "external/core-et/docs/CORE-ET Minion Shire Description.pdf"
DCD = "external/core-et/docs/Minion DCache Description.pdf"
ERR = "external/et-man/ET-SoC Errata.pdf"
RTLM = "external/core-et-main/hw/ip/shirecache/rtl/"   # Ainekko re-implementation, co-simulated against the original shire_cache (STATUS.md:87, 140)
RTLO = "external/core-et/rtl/"                          # the open drop: Erbium branch (README.md), shire cache itself not in it
EP = "external/et-platform/"
CLM = "docs/findings/05-claims.md"
EMB = "docs/energy-manual/04-bytes-memory.md"
EMF = "docs/energy-manual/04a-fine-grain.md"
RTLNOTE = ("From the Ainekko re-implementation of the shire cache (core-et-main), which STATUS.md reports co-simulated "
           "against the original shire_cache RTL; that original is not in this checkout, and the open core-et drop is "
           "the Erbium branch. Treat as the design's behaviour, not a silicon measurement.")

F = []
def f(id, topic, statement, value, unit, source, kind, card=None, page_link=None, note=None):
    assert kind in ("et-spec", "et-measured", "et-derived", "generic", "unknown"), kind
    F.append(dict(id="scp." + id, level="scp", topic=topic, statement=statement, value=value, unit=unit,
                  source=source, kind=kind, card=card, page_link=page_link, note=note))

# ======================= what the scratchpad is =======================
f("what", "definition",
  "The scratchpad is part of each shire's 4 MB shire cache configured as software-managed memory: no tags, never a miss, "
  "globally addressable by any agent; a request to another shire's slice leaves over the mesh and is served by that shire's L3-slave port.",
  None, None, SCS + " p.6 §1 (Overview), p.9-10 §1.1; " + PRM + " p.486 §15.3", "et-spec", page_link=MH + "#the-hierarchy-as-a-spec-sheet")
f("size", "capacity",
  "In mode M0, the reset mode and the one these cards run, each shire's scratchpad is 2.5 MB (640 of the 1,024 sets of every sub-bank), 80 MB over the 32 compute shires; the driver reports 81,920 KB on every card.",
  2.5, "MB per shire",
  SCS + " p.21-22 Tables 6-7 ('The chip will come out of reset in mode M0'); " + EP + "et-common-libs/include/system/layout.h:73 (0x280000); docs/reports/data/2026-09-22-cards/driver_config.json scp_kb",
  "et-spec", card=ALL + " (driver report)", page_link=MH + "#the-hierarchy-as-a-spec-sheet")
f("m0-rows", "partition",
  "M0 per sub-bank: scratchpad sets 0x000-0x27F (640), L2 sets 0x280-0x2FF (128), L3 sets 0x300-0x3FF (256). Scratchpad, L2 and L3 are row ranges of the same data panels, not separate memories: the scratchpad is the lowest 2,560 of each panel's 4,096 rows (set x 4 ways).",
  2560, "rows of 4,096 per data panel",
  SCS + " p.22 Table 7 (Mode 0 base/end); " + RTLM + "shirecache_pipe_sub_bank.sv:1613 (data RAM address = {set, way})",
  "et-derived", note="Row count derived: 640 sets x 4 ways. The base can be moved to skip faulty rows (" + SCS + " p.21), so 'rows 0-2559' assumes the M0 base 0x0.")
f("addr", "address decode",
  "Scratchpad address fields: [39:31] = 9'h1 (scratchpad region), [30:23] target shire, [22:12] set (bit 22 = 0 for a 4 MB build), [11:10] way, [9:8] sub-bank, [7:6] bank, [5:0] byte. All-ones in the shire field means the requester's own shire.",
  None, None, SCS + " p.24 §1.4.1.3; " + RTLM + "shirecache_pkg.sv:118, 146-149, 907; " + PRM + " p.486 (format 0, shire ID 0x7F = local)",
  "et-spec", page_link=MH + "#scratchpad-latency-across-the-mesh")
f("addr-row", "address decode",
  "So one 64 B scratchpad line lives at bank PA[7:6], sub-bank PA[9:8], panel row PA[21:10] of that sub-bank's four panels, 16 B per panel (quadword PA[5:4]). Consecutive lines rotate over the 4 banks and then the 4 sub-banks, so one 1 KB TensorLoad (16 consecutive lines) touches each of the shire cache's 16 sub-banks exactly once: 64 panel accesses.",
  64, "panel accesses per 1 KB TensorLoad",
  SCS + " p.24; " + RTLM + "shirecache_pipe_sub_bank.sv:1613; shirecache_pipe_data_ram_wrap.sv:83-108", "et-derived", note=RTLNOTE)
f("format1", "address decode",
  "Format 1 (address bit 30 = 1, minions only) puts the shire ID in bits [29:28] and [10:6], so consecutive 64 B lines land in different shires' scratchpads.",
  None, None, PRM + " p.486 §15.3", "et-spec")
f("banks", "organization",
  "Four banks per shire, each a quarter of the scratchpad, L2 and L3; each bank takes at most one request and returns at most one 512-bit line per cycle; each bank has four sub-banks.",
  4, "banks x 4 sub-banks", SCS + " p.6 §1, p.9 ('POR for the first SoC is 4M/Shire, 4 banks/Shire, 4 sub-banks/bank'), p.30 §2.1", "et-spec")
f("always-hit", "pipeline",
  "A scratchpad read is 'always a hit': the pipeline does not read the tag or tag-state RAMs for it (both reads are squashed), takes the way from PA[11:10], and writes no LRU or state afterwards; the tag and tag-state panels stay idle on a scratchpad access.",
  None, None,
  SCS + " p.57 Figures 15-17; " + RTLM + "shirecache_pipe_sub_bank.sv:155-159 (squash_tag_state_and_tag_rd_tap), 591-593, 843-853, 884-899",
  "et-derived", note=RTLNOTE)
f("no-victims", "pipeline",
  "Scratchpad operations have no misses, no victims and no fills from below; Lock, Unlock, Flush and Evict to a local scratchpad address are not supported.",
  None, None, SCS + " p.87 §3.13 ('For Scratchpad operations, there are no victims'), p.14-15 Table 2", "et-spec")
f("xbar", "interconnect",
  "A full request crossbar joins the 4 neighbourhoods and the RBOX to the 4 banks and the UC block; an identical response crossbar returns lines; each bank has one catch FIFO per neighbourhood and a round-robin arbiter.",
  None, None, SCS + " p.30-32 §2.1-2.2", "et-spec")
f("reqq", "queues",
  "Per bank: a 64-entry request queue (up to 21 entries reserved for L3-slave requests), a dataq entry per reqq entry, an 8-entry read buffer and a 32-entry coalescing buffer. Per sub-bank, L3-slave (remote) requests win the arbitration over neighbourhood requests.",
  64, "reqq entries per bank",
  "docs/research/counters-and-dram.md:458-465; " + SCS + " p.34-36 §2.5-2.6 (three-step arbitration), p.9 (coalescing buffer)", "et-spec")
f("pipe-stages", "pipeline",
  "A read passes ag (reqq allocate), ad, rqa (arbitration), tap, ta, ta0, ta1, te, tc (tag pipeline), dap, da, da0, da1 (data panel access, 2 cycles), de (ECC check and fix), dc (data complete, OR'ed across sub-banks, to the response mux). The pipeline is non-stalling; a sub-bank is busy for the panel access time, so it accepts a request every other cycle at the default timing.",
  None, None, SCS + " p.44-46 §2.14-2.14.1, p.35-36", "et-spec")
f("ram-delay", "panel timing",
  "Tag, tag-state and data panel access time is 2, 3 or 4 shire-cache cycles, one control for all three (esr_sc_ram_delay); the design intends 2 and resets to 2 (reset value of sc_pipe_ctl 0x5C_FFFF_FFFF in the functional model decodes to ram_delay = 2, both read buffers and zero-state on).",
  2, "cycles per panel access (reset default)",
  SCS + " p.9, p.48 §2.14.6.1, p.101; " + RTLO + "inc/shire_cache_defines.vh:260; " + RTLO + "inc/esr_defines.vh:66; " + EP + "sw-sysemu/esrs_et.cpp:38; " + EP + "etsoc-hal/include/hwinc/etsoc_shire_cache_esr.h:839-845 (bits 39:37)",
  "et-spec", note="What the cards actually run is not recorded anywhere we can read: see unknown scp.u-trim.")
f("clock-gate", "power",
  "The data panels' inputs are held still when not accessed, and the panel clock is gated on only around an access (for ram_delay cycles); a partial write enables only the quadword panels it writes.",
  None, None, SCS + " p.46 (stages ta, da), p.48 §2.14.5; " + RTLM + "shirecache_pipe_data_ram_wrap.sv:52-66, 83-96", "et-spec")
f("rbuf", "read buffer",
  "Scratchpad reads install into the bank's 8-entry fully-associative read buffer (esr_sc_scp_rbuf_enable, on at reset), including reads that arrive from other shires; a repeat read of a clean line is served without touching the panels: 10 shire clocks against 21.",
  8, "lines per bank", SCS + " p.40 §2.8, p.101, p.11 Table 1; " + RTLO + "inc/esr_defines.vh:66", "et-spec", page_link=MH + "#the-hierarchy-as-a-spec-sheet")
f("zero-state", "power",
  "The shire cache's zero-state shortcut (no data-panel read or write when a line is all zeros, esr_sc_zero_state_enable) lives in the tag-state RAM, which scratchpad operations never read; so a scratchpad read of an all-zero line still reads the data panels, and a scratchpad write always writes them.",
  None, None,
  SCS + " p.101 (esr_sc_zero_state_enable), p.47 Table 12 ('zero' flag); " + RTLM + "shirecache_pipe_sub_bank.sv:155-159, 583-609, 810, 1055-1066",
  "et-derived", note=RTLNOTE + " Consequence for the diagram: the measured zeros-vs-random difference of the own scratchpad cannot come from skipping the panels.")
f("write-granule", "write",
  "A scratchpad write counts as partial only below 16 B; 16 B and larger writes go straight to the panels with per-quadword enables, with no read-modify-write (L2 writes, by contrast, are partial unless a full line).",
  16, "B minimum full write", RTLM + "shirecache_bank.sv:528-531; " + SCS + " p.48 §2.14.5 (128-bit granularity)", "et-derived", note=RTLNOTE)
f("idx-zero", "maintenance",
  "Each bank's index CacheOp state machine can walk a whole region, including 'SCP Zero' to clear the scratchpad, and gives debug read/write of any tag, state or data RAM word.",
  None, None, SCS + " p.10, p.52, p.88 §3.14; external/core-et-main/hw/ip/shirecache/README.md (idx_cop_sm: 'SCP Zero')", "et-spec")
f("deep-sleep", "power",
  "Tag-state, tag, data and dataq RAMs of a non-operational shire can be put in deep_sleep or shut_down by ESR (esr_sc_ram_deep_sleep / esr_sc_ram_shut_down, sc_pipe_ctl bits 41 and 40).",
  None, None, SCS + " p.101; " + EP + "etsoc-hal/include/hwinc/etsoc_shire_cache_esr.h:813-837", "et-spec")

# ======================= the circuit: panels =======================
f("panel", "memory macro",
  "Data storage is built from 144-bit-wide 'SRAM memory panels' (128 data bits + 16 ECC bits), four per sub-bank, one per quadword of the 512-bit line. The data panel is named 'saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11', RAM type 1PUHD: 4,096 words x 144 bits.",
  144, "bits per panel word",
  SCS + " p.48 §2.14.5 ('SRAM memory panels that are 144 bits wide'), p.51 (data_ram (mbd) = saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11 (1PUHD)); " + RTLO + "inc/shire_cache_defines.vh:362 (SC_MBD_DATA_SIZE = 576/4)",
  "et-spec", note="The spec is version 1.1 and also covers later chips (sections marked Nemi, Gepardo); the macro table is not labelled per chip. Its 4096x144 matches the 4 MB ET-SoC-1 geometry.")
f("panel-others", "memory macro",
  "Other shire-cache macros: tag RAM 'saduls0g4l1p1024x116m4b1...' (1PUHD, 4 ways x (23-bit tag + 6 ECC)), tag-state RAM 'saculs0g4l2p1024x40m4b1...' (2PUHDRF, a two-port register-file type), I-cache data 'saduls0g4l1p512x144m4b1...'. The scratchpad path uses only the data panels.",
  None, None, SCS + " p.47 §2.14.2-2.14.3, p.51 Tables 13-14", "et-spec")
f("panel-count", "memory macro",
  "Per shire 64 data panels (4 banks x 4 sub-banks x 4), each 589,824 bits; 37.7 Mbit per shire including ECC (32 Mbit data + 4 Mbit ECC); 2,048 data panels over the 32 compute shires.",
  64, "data panels per shire", SCS + " p.9, p.48, p.51", "et-derived",
  note="If each bit is a 6-transistor cell (GENERIC assumption, see scp.u-cell) that is 3.54 M transistors per panel array and about 226 M per shire, cells only.")
f("line-read-panels", "memory macro",
  "A full 64 B scratchpad read raises one row in each of the four quadword panels of one sub-bank and senses 576 bits (512 data + 64 ECC); the other 15 sub-banks, and the tag and tag-state panels, stay idle.",
  576, "bits sensed per line", SCS + " p.48 §2.14.5; " + RTLM + "shirecache_pipe_data_ram_wrap.sv:83-108; shirecache_pipe_sub_bank.sv:155-159", "et-derived", note=RTLNOTE)
f("vendor", "memory macro",
  "The panels are third-party IP; their memory test is a shared-bus BIST 'such as the Synopsys SMS (STAR Memory System)' with logical RAMs mbs (tag state), mbt (tag), mbd (data), mbq (dataq), mbi (I-cache). The RTL build files call them 'physical SRAM macros' and note 'Synopsis memories not available' for synthesis.",
  None, None,
  SCS + " p.48 §2.14.6.1, p.49 §2.14.6.3; " + RTLO + "inc/common_syn.f:12-13; " + RTLO + "inc/common_lint.f:14-16",
  "et-spec", note="No source names the memory compiler or the bitcell outright; the 'sa..ls0g4' prefix is a compiler naming convention we cannot decode from these sources (scp.u-macro).")
f("prm-sram-family", "memory macro",
  "The PRM calls the same macro families SRAMs: the Maxion shire has configuration registers 'sacrls_config', 'sadcls_config', 'saduls_config', 'sadrls_config' - 'Configuration bits for SADULS SRAM's. Bits 17:0 control read and write margins, bias control, etc.'",
  18, "trim bits per macro family", PRM + " p.346 Table 15-5 (R_MX_SRAM_RM)", "et-spec")
f("trim-knobs", "memory macro",
  "Each logical RAM group has trim bits set by ESR shire_cache_ram_cfg1-4 (cfg2 = data panels): RM[3:0] read margin, RME, RA[1:0] read assist, WA[2:0] write assist, WPULSE[2:0] write pulse, BC[2:0] (bias control), TEST1, TEST_RNM. 'The RAM macros have trim bits to allow them to operate at various voltage levels... The ESR settings default to RM0 mode to allow nominal 650mV operation.'",
  None, None, SCS + " p.50-51 §2.14.6.4; " + RTLO + "inc/esr_types_legacy.vh:70-79; " + EP + "et-common-libs/include/etsoc/isa/esr_defines.h:690-704 (regno 0x54-0x57, M-mode)", "et-spec")
f("vmin-table", "memory macro",
  "Data-panel (1PUHD) trim table: RM mode 5 Vmin 855 mV (Vnom 950), 4: 765 (850), 3: 675 (750), 2: 650 (722), 1: 630 (700), 0: 585 mV (650); WA 5-7, RA 0-1, WPULSE 0.",
  585, "mV Vmin at RM0", SCS + " p.51 Table 14", "et-spec")
f("trim-reset", "memory macro",
  "Data-panel trim at reset: WA = 7, RA = 1, RM = 0, RME = 0 (ESR value 0x3A0 in the functional model), i.e. the RM0 'nominal 650 mV' row of Table 14.",
  "0x3A0", "shire_cache_ram_cfg2 reset",
  RTLO + "inc/esr_defines.vh:112-117; " + EP + "sw-sysemu/esrs_et.cpp:47; " + SCS + " p.50-51", "et-spec")
f("fw-no-trim", "memory macro",
  "Nothing in the open firmware writes the RAM-trim ESRs or esr_sc_ram_delay: in et-platform they appear only in the register headers and the functional model's reset values. Unless closed boot code changes them, the panels run at reset trim and 2-cycle timing.",
  None, None, "grep of " + EP + " for ram_cfg / RAM_CFG / SC_PIPE_CTL / ram_delay: hits only in sw-sysemu/esrs_et.cpp, sw-sysemu/esrs.h, etsoc-hal/include/hwinc/etsoc_shire_cache_esr.h, et-common-libs/include/etsoc/isa/esr_defines.h",
  "et-derived", note="An absence in the open tree, not a reading from a card; see scp.u-trim.")
f("ecc", "ECC",
  "SECDED on everything: 8 ECC bits per 64-bit data word (576 bits stored per 512-bit line), checked and corrected in stage de; ECC scrubbing is a reserved bit on this chip ('Future chips will implement this feature').",
  8, "ECC bits per 64 data bits", SCS + " p.9, p.48-49 §2.14.6.2, p.99 (esr_sc_ecc_scrub_enable)", "et-spec")

# ======================= voltage, clocks, rails =======================
f("rail", "voltage",
  "The shire-cache arrays sit on their own SRAM rail: set point 705 mV, 701-707 mV on die, against 518-520 mV for the minions and 484-485 mV for the mesh (aifoundry2 telemetry).",
  705, "mV", "docs/reports/data/2026-09-20-power-aifoundry2/horace-telemetry.jsonl fields reg_mv.sram, die_mv.sram, sp.sram_mv; " + CLM + ":41",
  "et-measured", card=A2, page_link=PT)
f("rail-margin", "voltage",
  "The 705 mV rail is 120 mV above the data panels' RM0 Vmin (585 mV) and 55 mV above RM0's 650 mV nominal.",
  120, "mV above RM0 Vmin", SCS + " p.51 Table 14; telemetry reg_mv.sram", "et-derived", card=A2)
f("regulator", "voltage",
  "The SRAM rail ('SRAM, aka: SCW voltage regulator') is a Linear Technologies LTM4680 PMBus module rated 60 A; the PMIC meters it with the minion and NoC rails.",
  60, "A max", "external/et-man/ET-PCIe-Dev-Card-V3.pdf p.5-6 (Key Voltage Regulators); " + CLM + ":337; docs/findings/01-resources.md:202-211 (R13)", "et-spec")
f("hv-region", "voltage",
  "The Shire Channel (shire cache, UC block, I-cache data memory) runs at high voltage: the I-cache data memory sits there 'because it has to be operated at high voltage'. Each neighbourhood is split into a low-voltage region (minions, neighbourhood clock) and a high-voltage interface region on the shire clock, joined by a semi-synchronous interface; level shifters and voltage-crossing FIFOs separate the domains.",
  None, None, SHD + " p.4, p.10 §3.1, p.18 §5; " + NMAS + " p.6 §2; " + RTLO + "libs/mems_and_fifos/vclevel_shft_l2h.v, vcfifo_wr_hiv_gcd.v",
  "et-spec", note="Which regulator feeds the 'high voltage' region is not stated; the 705 mV SRAM rail is the only candidate among the metered ones (scp.u-rail).")
f("clocks", "clocks",
  "Shire logic runs on shire_clock from the shire's own PLL, the neighbourhoods on a DLL copy shifted 180 degrees; the mesh on clk__noc from PLL2 (design 500 MHz). Telemetry on these cards reports minion 600 MHz and NoC 400 MHz; it does not report the shire-cache clock.",
  400, "MHz NoC (measured)", SHD + " p.12 Table 2; horace-telemetry.jsonl mhz.minion, mhz.noc", "et-spec", card=A2)
f("clock-ratio", "clocks",
  "The read buffer saves 11 cycles in both units: the spec's 10 vs 21 shire clocks, and the measured 36 vs 47 minion cycles. That fits a shire-cache clock equal to the 600 MHz minion clock, which would make a 2-cycle panel access 3.3 ns.",
  3.3, "ns per panel access (if 1:1)", SCS + " p.11 Table 1; " + CLM + ":421 (LAT-M1)", "et-derived", card=ALL,
  note="An inference from a difference; see scp.u-clock.")

# ======================= measured: latency =======================
f("lat-own", "latency",
  "A load that misses the L1 and hits the shire's own scratchpad: 47.00 cycles load-to-use (78 ns at 600 MHz), the same as an L2 hit; a read-buffer hit 36.00; hart 1 pays 3 more (50 and 39). Identical on three cards.",
  47.0, "minion cycles", CLM + ":421; docs/reports/data/2026-09-25-claims-v3/results/lat.json items[LAT-M1].per_card.<card>.passes[].L2, .RB, .hart1",
  "et-measured", card=ALL, page_link=MH + "#the-hierarchy-as-a-spec-sheet")
f("lat-split", "latency",
  "Of the 47 cycles, the spec accounts for 21 shire clocks inside the shire cache including both crossbars; the other ~26 are the minion pipeline, the L1 miss and the neighbourhood's request (at least 4 clocks) and response (at least 6 clocks to a minion) paths.",
  26, "cycles outside the shire cache", "docs/research/counters-and-dram.md:466-476; " + SCS + " p.11 Table 1; " + NMAS + " p.20 §4.3.5, p.21 §4.4.2",
  "et-derived", card=ALL)
f("same-as-l2", "latency",
  "The scratchpad is the L2 without the tags: same 47-cycle latency, same read buffer, same 4.0 B per minion-cycle; pass by pass the L2-minus-scratchpad energy difference included zero on each of three cards. Skipping the tag panels saves no time because the pipeline stages are fixed.",
  None, None, "docs/reports/2026-09-18-et-soc1-memory-hierarchy.html:858; " + SCS + " p.44-46",
  "et-measured", card=ALL, page_link=MH + "#what-the-numbers-say", note="The latency and bandwidth parts are measured; 'saves no time because the stages are fixed' is derived from the spec's non-stalling pipeline.")
f("lat-remote", "latency",
  "Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within one cycle; a to b equals b to a within 0.032 cycles, on three cards.",
  99.84, "cycles + 12.00 per hop", CLM + ":423; lat.json items[LAT-M3].per_card.<card>.passes[] (row0_slope 11.998-12.002, frac_within_1 1.0)",
  "et-measured", card=ALL, page_link=MH + "#scratchpad-latency-across-the-mesh")
f("lat-remote-split", "latency",
  "Fitted over 600, 700 and 800 MHz, a remote scratchpad load is 65.95 minion cycles + 56.48 ns + 20.00 ns per hop: the part that scales with the core clock (both shires' pipelines) and a fixed part in other clock domains (mesh, clock crossings).",
  56.48, "ns fixed + 65.95 cycles", CLM + ":379 (E33, MH fits.scp_model)", "et-measured", card=A2, page_link=MH + "#scratchpad-latency-across-the-mesh")
f("lat-leave", "latency",
  "Leaving the shire costs about 53 cycles before the first hop (99.84 at zero hops against 47 locally); each hop then adds 12 minion cycles round trip = 20 ns = 8 cycles of the 400 MHz mesh clock, 4 each way.",
  52.84, "cycles", CLM + ":421, :423; telemetry mhz.noc", "et-derived", card=ALL)
f("tl-one", "latency",
  "One minion's TensorLoad from its own scratchpad into its L1 scratchpad: 4 lines %.1f cycles, 8 lines %.1f, 16 lines %.1f (the L2: 41.9 and 160.4 for 4 and 16), on each of three cards." % (tl[A2]["scp4"], tl[A2]["scp8"], tl[A2]["scp16"]),
  round(tl[A2]["scp16"], 1), "cycles per 16-line (1 KB) TensorLoad", "lat.json items[LAT-S2].per_card.<card>.pass_means.scp4, .scp8, .scp16, .l24, .l216",
  "et-measured", card=ALL, page_link=HX)
f("tl-pipelining", "latency",
  "Each extra line costs 10.0 cycles ((%.1f - %.1f) / 8), which is 4 transfers in flight over a ~40-cycle round trip: the tensor-load unit keeps up to 4 L2 transfers outstanding." % (tl[A2]["scp16"], tl[A2]["scp8"]),
  10.0, "cycles per line (one minion)", "lat.json LAT-S2; docs/research/counters-and-dram.md:449", "et-derived", card=ALL)

# ======================= measured: bandwidth =======================
f("bw-own", "bandwidth",
  "All 1,024 minions tensor-loading their own shire's scratchpad: 2.46 TB/s, 4.0 B per minion-cycle = 128 B per shire-cycle = 2 lines per shire-cycle, half the four banks' 256 B per cycle.",
  2.46, "TB/s", CLM + ":380; ridge-data levels[scp].measured (bpc 4.000, gbps 2,456)", "et-measured", card=ALL, page_link=RP + "#ridge-points-by-level")
f("bw-one-neigh", "bandwidth",
  "With only one neighbourhood per shire reading, the chip still moves 966-967 GB/s: about 50 B per shire-cycle for 8 minions, where four neighbourhoods together get 128.",
  967, "GB/s (one neighbourhood per shire)", EMF + ":70-79 (neigh/* rows)", "et-measured", card=ALL, page_link=EMU + "#finer-grain-wires-lines-rows-and-the-leakage-of-the-arrays")
f("bw-bank-stride", "bandwidth",
  "64 B tensor loads striding 64 or 128 B stream at 923 GB/s; striding 256 B, which returns to the same bank every time, 614 GB/s (-33%) on every card; energy per byte indistinguishable.",
  614, "GB/s at stride 256 B", EMF + ":46-54", "et-measured", card=ALL, page_link=EMU + "#finer-grain-wires-lines-rows-and-the-leakage-of-the-arrays")
f("bw-store", "bandwidth",
  "Tensor stores into the own scratchpad: 1.23 TB/s, half the read rate.",
  1.23, "TB/s", EMB + ":14; ridge-data limits.write_gbps.tstore_scp", "et-measured", card=ALL, page_link=EMU + "#reads-and-writes-measured-together")
f("bw-remote", "bandwidth",
  "Every shire reading the scratchpad 16 shire IDs away (2.1 mesh hops on average): 0.96 TB/s, 1.56 B per minion-cycle.",
  0.96, "TB/s", CLM + ":380; ridge-data levels[scp_remote].measured (bpc 1.562, gbps 959.5)", "et-measured", card=ALL, page_link=RP)
f("bw-spec-port", "bandwidth",
  "Upstream of the bank, a neighbourhood's 8 minions share one 512-bit ET-Link; its Fill FIFO delivers at most one response per cycle and, to one agent, one every other cycle; each minion's response port is 256 bits, so a 64 B line takes it two cycles.",
  256, "bits per minion response port", NMAS + " p.6 §2, p.21 §4.4.2, p.22-23 §4.4.3", "et-spec")

# ======================= measured: energy =======================
mz = lvl("zeros", "scp-local"); mr = lvl("random", "scp-local")
f("e-own", "energy",
  "Reading the own scratchpad by 1 KB tensor loads at 600 MHz, above idle: %.2f pJ/B [%.2f-%.2f] when it holds zeros, %.2f [%.2f-%.2f] when it holds random data (three passes on each of three cards)." % (mz[0], mz[1], mz[2], mr[0], mr[1], mr[2]),
  round(mr[0], 2), "pJ/B (random)", EMR + "/manual.json reruns.levels_by_contents_pj_per_byte.{zeros,random}['scp-local']; " + EMB + ":29-30",
  "et-measured", card=ALL + " (per card random " + json.dumps(mr[3]) + ")", page_link=EMU + "#reads-by-level")
f("e-catalogue", "energy",
  "Catalogue: tensor load from the own scratchpad 2.12 / 4.43 pJ/B (zeros / random), tensor store into it 4.65 / 8.58: a scratchpad write costs about twice a read.",
  4.43, "pJ/B tensor load, random", EMB + ":13-14, :40", "et-measured", card=ALL, page_link=EMU + "#reads-and-writes-measured-together")
f("e-rails-load", "energy",
  "Where the power of an own-scratchpad tensor-load stream goes (aifoundry2, random, 10.19 W over idle): 69% SRAM rail, 24% minion rail, 1% mesh, 7% on no meter. Tensor store (9.83 W): 76% SRAM, 20% minions, 1% mesh, 3% unmetered.",
  69, "% on the SRAM rail", EMF + ":156-173", "et-measured", card=A2, page_link=EMU + "#where-the-current-flows")
f("e-sram-line", "energy",
  "On the SRAM rail alone, reading the own scratchpad costs %.2f pJ/B on random data and %.2f on zeros (aifoundry2; aifoundry3 %.2f / %.2f; aifoundry1-c1 %.2f / %.2f): %.0f and %.0f pJ per 64 B line, about %.0f and %.0f pJ per panel access, %.2f pJ per stored bit read on random data." % (
      r2l["sram_pjB"], r2z["sram_pjB"], rails[(A3, "tload/scp/random")]["sram_pjB"], rails[(A3, "tload/scp/zeros")]["sram_pjB"],
      rails[(A1, "tload/scp/random")]["sram_pjB"], rails[(A1, "tload/scp/zeros")]["sram_pjB"],
      r2l["sram_pjB"] * 64, r2z["sram_pjB"] * 64, r2l["sram_pjB"] * 16, r2z["sram_pjB"] * 16, r2l["sram_pjB"] * 64 / 576),
  round(r2l["sram_pjB"] * 64, 1), "pJ per 64 B line on the SRAM rail (random, aifoundry2)",
  EMR + "/catalogue.json cards.<card>.summary['tload/scp/{random,zeros}'].rails_over_w.sram_w / bytes_per_s", "et-derived", card=ALL,
  note="Rail watts over idle divided by bytes per second at 2,458 GB/s. Includes everything on that rail, which may be more than the arrays (scp.u-rail). The PMIC's running average reaches 0.94 of a step by the read window, so rail values may be up to 6% low (" + EMF + ":158). aifoundry1-c1 reads lower on this rail and higher on the minion rail.")
f("e-sram-write", "energy",
  "On the SRAM rail, writing the own scratchpad by tensor store costs %.2f pJ/B random and %.2f zeros (aifoundry2): %.0f and %.0f pJ per 64 B line, %.1fx and %.1fx a read of the same data." % (
      r2sl["sram_pjB"], r2sz["sram_pjB"], r2sl["sram_pjB"] * 64, r2sz["sram_pjB"] * 64, r2sl["sram_pjB"] / r2l["sram_pjB"], r2sz["sram_pjB"] / r2z["sram_pjB"]),
  round(r2sl["sram_pjB"] * 64, 1), "pJ per 64 B line on the SRAM rail (write, random, aifoundry2)",
  EMR + "/catalogue.json cards.aifoundry2.summary['tstore/scp/{random,zeros}'].rails_over_w.sram_w / bytes_per_s", "et-derived", card=A2,
  note="No read-modify-write is involved for writes of 16 B or more (scp.write-granule), so the factor is the write itself plus its request path.")
f("e-data", "energy",
  "Random data costs 2.0x zeros on the SRAM rail for a scratchpad read (%.2f vs %.2f pJ/B, aifoundry2): %.0f pJ more per line. Since the zero-state shortcut does not apply to the scratchpad (scp.zero-state), the panels are read either way; the difference is what toggles with the data." % (r2l["sram_pjB"], r2z["sram_pjB"], (r2l["sram_pjB"] - r2z["sram_pjB"]) * 64),
  round((r2l["sram_pjB"] - r2z["sram_pjB"]) * 64, 1), "pJ per line, random minus zeros (SRAM rail)", EMR + "/catalogue.json (as scp.e-sram-line)", "et-derived", card=A2,
  note="Where it toggles (bitcell array, macro read path, ECC, pipeline, crossbar) cannot be told from rail power: scp.u-rail and scp.u-macro.")
f("e-l1fill", "energy",
  "Filling one 64 B line from the scratchpad into the L1 costs 101 pJ on zeros and 238 pJ on random data (1.6 and 3.7 pJ per byte of line); what random data adds, about 138 pJ per line, is 269 fJ per bit on the path from the shire cache into the L1.",
  238, "pJ per line (random)", EMF + ":44; " + CLM + ":306", "et-measured", card=ALL, page_link=EMU + "#finer-grain-wires-lines-rows-and-the-leakage-of-the-arrays")
f("e-neigh", "energy",
  "Which neighbourhood reads makes little difference: 4.14, 3.93, 4.25, 4.25 pJ/B for neighbourhoods 0-3 (random).",
  4.14, "pJ/B", EMF + ":70-79", "et-measured", card=ALL)
rz = lvl("zeros", "scp-remote"); rr = lvl("random", "scp-remote")
f("e-remote", "energy",
  "Another shire's scratchpad (16 IDs away, 2.1 hops on average): %.2f pJ/B [%.2f-%.2f] on zeros, %.1f [%.1f-%.1f] on random data." % (rz[0], rz[1], rz[2], rr[0], rr[1], rr[2]),
  round(rr[0], 1), "pJ/B (random)", EMR + "/manual.json reruns.levels_by_contents_pj_per_byte.{zeros,random}['scp-remote']; " + EMB + ":31-32",
  "et-measured", card=ALL, page_link=EMU + "#reads-by-level")
f("e-hop", "energy",
  "Each mesh hop adds 0.67 pJ/B on zeros and 1.80 on random data (1-8 hop fit; 2.2-2.4 on random over 1-6 hops): 142 fJ per random bit per hop. Leaving the shire costs about one more hop.",
  1.80, "pJ/B per hop (random)", EMF + ":9-22; " + CLM + ":303", "et-measured", card=ALL, page_link=EMU + "#finer-grain-wires-lines-rows-and-the-leakage-of-the-arrays")
f("e-rails-remote", "energy",
  "Rail split of a remote scratchpad read (aifoundry2, random): 1 hop 14% minions / 50% SRAM / 27% mesh / 10% unmetered; 3 hops 11/36/40/14; 6 hops 8/26/50/17. The mesh rail alone: 1.27 pJ/B per hop.",
  50, "% on the mesh rail at 6 hops", EMF + ":174-176, :181", "et-measured", card=A2, page_link=EMU + "#where-the-current-flows")
f("gather", "energy",
  "Random 4 B gathers (fgw.ps) from the own scratchpad: 27.4 G elements/s at 367.8 pJ each, the same rate as the L2 because each element fetches its own line and a minion has two miss handlers; from a scratchpad 2 hops away 10.2 G/s at 903 pJ.",
  367.8, "pJ per element", EMB + ":56, :59; " + CLM + ":502", "et-measured", card=ALL, page_link=MH + "#irregular-access-gathers-and-scatters")
f("leak", "leakage",
  "The SRAM rail at idle (all 128 MB of L2, L3 and scratchpad plus whatever else is on it): 2.51 W at 80 C on aifoundry2, 19.6 mW per MB, an upper bound on the arrays' leakage; a byte held for one second leaks at most ~19 nJ, as much as reading it 4,200 times. aifoundry3 and aifoundry1-c1 sit about 1 W higher.",
  19.6, "mW per MB at 80 C", EMF + ":104-115; " + CLM + ":312, :473", "et-measured", card=ALL, page_link=EMU + "#the-sram-arrays-at-rest")
f("power-goal", "energy",
  "The spec's power goal is '100 MW [sic] for the entire Shire Cache running benchmark'; streaming random data from the own scratchpad raises the SRAM rail %.2f W over idle on aifoundry2, %.0f mW per shire." % (r2l["sram_w"], r2l["sram_w"] / 32 * 1000),
  round(r2l["sram_w"] / 32 * 1000), "mW per shire (SRAM rail rise)", SCS + " p.11 ('Power: TBD. Goal is 100 MW'); " + EMR + "/catalogue.json aifoundry2 tload/scp/random", "et-derived", card=A2,
  note="The goal presumably means mW; its benchmark and clock are not stated.")
f("vendor-virus", "energy",
  "Esperanto's own worst case for the SRAM ('SCW') regulator is a scratchpad kernel: scw_power_virus streams random data between the L1 scratchpad and the local L2 scratchpad (0xBF800000, the 'self' shire) with TensorLoad and TensorStore on shires 0-31.",
  None, None, EP + "test-compute-kernels/src/scw_power_virus/scw_power_virus.c:18-21; kernel.h:23-27, 288-313", "et-spec")

# ======================= paths: TensorLoad, relay, fill, atomics =======================
f("tensorload", "path",
  "TensorLoad (CSR 0x83F, hart 0 only) reads up to 16 rows of 64 B (row stride in x31) and writes them into consecutive L1-scratchpad lines, bypassing the L1 data cache; TensorLoad Setup B streams lines into a 4-entry VPU buffer instead (TenB).",
  16, "rows of 64 B", PRM + " p.264, p.275; " + DCD + " p.40-43 §3.9", "et-spec", page_link=HX)
f("tl-dest", "path",
  "The destination of a TensorLoad is latch RAM, not SRAM: the minion's L1 data cache (and the L1 scratchpad carved from it) is 4 LRAM (latch-RAM) blocks of 128 rows x 64 bits.",
  4, "LRAM blocks of 128 x 64 b", DCD + " p.29-30 ('The physical memory of the DCache is made of 4 LRAM (Latch-RAM) blocks'); " + RTLO + "libs/macros/dcache_128x32_1r1w_lram.v", "et-spec",
  note="Relevant to the lab lead's 'not SRAM': the L1 is documented as latches, the shire cache as SRAM panels (scp.u-cell).")
f("coop", "path",
  "Cooperative TensorLoad: identical requests from minions across a shire's neighbourhoods are synchronised and sent as one ReadCoop; the bank's response mux broadcasts the line to every cooperating neighbourhood.",
  None, None, NMAS + " p.23-24 §4.5; " + SCS + " p.58 §3.3; " + PRM + " p.273 §9.3.1.1", "et-spec")
f("tl-l2scp", "path",
  "TensorLoadL2Scp (CSR 0x85F; hart 1 may issue it) copies up to 16 lines from memory into this shire's L2 scratchpad, bypassing the L1 and L2; in the bank it is REQ_ScpFill: a mesh read of the source (L3, DRAM or a remote scratchpad), then an SCP_Fill write. The source address must use the real shire ID, not the self ID (erratum RTLMIN-6579).",
  16, "lines", PRM + " p.264, p.289-290; " + SCS + " p.15, p.87 §3.13; " + ERR + " p.83 §4.4", "et-spec")
f("remote-write", "path",
  "Writes to another shire's scratchpad: a plain write goes from the dataq to the mesh without using the local pipeline; a TensorStore write-around is coalesced in the local L2 and sent when the line is full (a full-line write-around that misses bypasses the local data panels); the target shire's L3 slave writes its scratchpad through its pipeline. Such write-arounds are not ordered against other remote scratchpad accesses (erratum RTLMIN-6617).",
  None, None, SCS + " p.13 Table 2, p.40 §2.7, p.62 §3.4.5, §3.5; " + ERR + " p.84 §4.6; " + RTLM + "shirecache_pipe_sub_bank.sv:640-642, 810", "et-spec")
f("relay", "path",
  "Handing each stage's output to the next shire's scratchpad instead of DRAM: 592.5 GB/s against 47.7 (12.4x), own scratchpad 1,487 GB/s (31x); energy per byte moved 116.2 / 8.92 / 4.34 pJ/B (DRAM / next shire / own), DRAM over next shire 12.9-13.1x on every card.",
  8.92, "pJ/B (next shire)", CLM + ":464, :428; " + EMR + "/manual.json reruns.relay_pj_per_byte; docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json headline",
  "et-measured", card=ALL, page_link=RL + "#one-kernel-three-places-to-put-the-answer")
f("relay-mech", "path",
  "In the relay kernel, a 'next shire' stage reads the previous shire's scratchpad with 32 B vector loads through the L1 (remote scratchpad reads over the mesh) and writes its own scratchpad with TensorStores of 32 B rows.",
  32, "B per TensorStore row", "workloads/onchip/kernel/onchip.c:58-66, 167-184, 209-220", "et-spec")
f("atomic", "path",
  "A global atomic on a scratchpad word is performed by the home bank's atomic block (read, ALU, write; the sub-bank is held busy throughout) after arriving on the L3-slave port; the bank retires one every 10.00 cycles; an uncontended remote atomic takes 216 cycles round trip; an atomic through the self ID 0x7F is a bus error.",
  10.0, "cycles per atomic at the bank", SCS + " p.17 (L3 slave REQ_Atomic, local SCP), p.36, p.40 §2.9; " + CLM + ":232; docs/findings/17-hot-line.md:35-38; lat.json [item=LAT-H]",
  "et-measured", card=ALL, page_link=HL + "#the-atomic-itself-is-fair")
f("starve", "path",
  "Because remote (L3-slave) requests win each sub-bank's arbitration, 22 or more minions of one other shire hammering one scratchpad word stop the host shire's own scratchpad reads (0.02% of their rate); 21 leave it at 95.6%. Errata RTLMIN-6207 and -6214 describe it.",
  22, "remote requesters", CLM + ":427; docs/findings/17-hot-line.md:44-95; " + SCS + " p.36; " + ERR + " p.80", "et-measured", card=ALL, page_link=HL + "#the-thing-that-actually-starves")
f("offset0", "traps",
  "Offset 0 of a shire's scratchpad faulted during development (card not recorded); the relay's buffers start at 256 KB.",
  0, "offset", CLM + ":257; docs/reports/2026-09-22-on-chip-relay.html:347; workloads/onchip/host/main.cpp:254", "et-measured", card="not recorded", page_link=RL + "#method-and-what-is-not-established")

# ======================= GENERIC circuit facts (textbook, not ET-specific) =======================
G = "GENERIC (textbook single-port 6T SRAM; not from an ET source)"
f("g-cell", "circuit",
  "GENERIC. A 6T SRAM cell stores a bit in two cross-coupled CMOS inverters (2 PMOS pull-ups, 2 NMOS pull-downs); two NMOS access (pass-gate) transistors, gated by the wordline, connect the two storage nodes to the bitline pair BL/BLB.",
  6, "transistors per bit", G, "generic")
f("g-read", "circuit",
  "GENERIC. A read: precharge PMOS and an equaliser hold BL and BLB at VDD, then release; the row decoder's wordline driver raises one wordline; on the side storing 0, the access and pull-down NMOS discharge that bitline by some tens of millivolts to ~100 mV; the column mux passes the selected pairs to sense amplifiers; sense-enable fires a latch-type amplifier (cross-coupled pair with an NMOS tail) that resolves the small difference to full swing into an output latch; the wordline falls and the precharge restores the bitlines.",
  None, None, G, "generic")
f("g-read-data", "circuit",
  "GENERIC. In a differential read exactly one bitline of each pair discharges whether the cell holds 0 or 1, so the array's read energy is to first order independent of the data; data dependence comes from what follows the sense amplifiers (outputs that toggle, buses, ECC) unless the macro uses a precharged single-ended global read line.",
  None, None, G, "generic")
f("g-half-select", "circuit",
  "GENERIC. With column multiplexing, every cell on the raised wordline discharges its bitline, not only the columns being read: with a 4:1 mux, four bitline pairs swing for every bit delivered (the unread three are 'half-selected').",
  4, "bitline pairs per bit (if 4:1 mux)", G, "generic", note="Whether the 'm4' in the ET macro name means a 4:1 column mux is unknown (scp.u-macro).")
f("g-write", "circuit",
  "GENERIC. A write: write drivers pull one bitline of each selected column fully to ground, the wordline rises, the access transistor overpowers the cell's pull-up and the cell flips; write assist (e.g. a negative bitline boost) and the wordline pulse width set the margin. Restoring a full-swing bitline costs more than a small-swing read.",
  None, None, G, "generic", note="The ET macros expose WA (write assist) and WPULSE knobs (scp.trim-knobs); what circuit each drives is not stated.")
f("g-assist", "circuit",
  "GENERIC. Read-margin trims adjust the self-timed sense-enable delay (often from a replica bitline); read assist lowers the wordline voltage to protect the cell from read upset. These are standard knobs of FinFET-era SRAM compilers.",
  None, None, G, "generic")
f("g-static", "circuit",
  "GENERIC. SRAM is static: no refresh, the bit holds as long as the rail is up; its standing cost is leakage through the off transistors, which rises steeply with temperature; retention (deep-sleep) modes lower the array voltage.",
  None, None, G, "generic")
f("g-ecc", "circuit",
  "GENERIC. A SECDED code with 8 check bits per 64 data bits (e.g. Hsiao (72,64)) corrects one bit and detects two; for linear codes, all-zero data has all-zero check bits.",
  8, "check bits per 64", "GENERIC (coding theory)", "generic", note="Which code the shire cache uses is not stated.")
f("g-level-shifter", "circuit",
  "GENERIC. A low-to-high level shifter (0.52 V minion domain to a higher domain) is typically a cross-coupled PMOS pair driven by NMOS input transistors.",
  None, None, "GENERIC", "generic", note="The ET RTL models its level shifter as a buffer (" + RTLO + "libs/mems_and_fifos/vclevel_shft_l2h.v); the physical cell is not given.")

# ======================= UNKNOWN facts (the asks) =======================
UNK = [
 ("u-cell", "What storage cell is in the shire-cache data panels on ET-SoC-1 silicon? The Shire Cache Specification calls them 'SRAM memory panels' (p.48) named saduls0g4l1p4096x144m4b4... type 1PUHD (p.51) and the PRM calls the SADULS family SRAMs (p.346), but the lab lead says the chip does not use SRAM. If not a 6T SRAM cell, what is it (8T or register-file cell, latch array, gain cell or eDRAM)? The L1 data cache is documented as latch RAM (DCache Description p.29) - is that what was meant?",
  "The transistor-level drawing of the scratchpad, L2 and L3 array: 6 transistors per bit with a differential bitline pair and a sense amplifier, or another cell; and whether reads are destructive or need refresh (which would add a refresh step to this level's sequence)."),
 ("u-macro", "What is the data panel's physical organisation? Decode the macro name saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11 (compiler, 'm4' column mux?, 'b4' internal banks?), and give rows x columns per sub-array, bitline length, and whether the read path uses a precharged global read bus. The macro datasheet or .lib would settle it (see rung 19, a cell library).",
  "How many wordlines, bitline pairs and sense amplifiers switch per 144-bit panel access (e.g. 576 bitline pairs swing for 144 bits read if 4:1), and where the data-dependent part of the read energy sits (array or periphery)."),
 ("u-rail", "Which circuits does the 705 mV SRAM ('SCW') regulator feed: only the memory macros, or the whole Shire Channel (the shire-cache pipeline, queues, crossbars, ECC, the UC block, the neighbourhoods' high-voltage interface region)? The Power Spec that the Shire Description cites (§5) would say (see ask-design-docs).",
  "How the measured 69% SRAM-rail share of a scratchpad read (182 pJ per line on random data) is split between the bitcell array and the logic around it: the colour of each block in the energy view, and whether the zeros-vs-random difference belongs to the array or to the datapath."),
 ("u-trim", "What panel timing and trim do the cards run? esr_sc_ram_delay (2, 3 or 4 cycles; resets to 2) and shire_cache_ram_cfg1-4 (reset for the data panels: RM 0, RME 0, WA 7, RA 1 = Table 14's RM0 '650 mV nominal' row). The open firmware never writes them; does boot ROM or BL1 change them for the 705 mV rail? A one-time M-mode read of ESR 0x55 on each card would also settle it.",
  "The panel access time drawn in the pipeline (2 cycles = 3.3 ns at 600 MHz) and which read-margin and write-assist mode the transistor animation shows."),
 ("u-clock", "What clock does the shire cache (shire_clock, o_clkpll_shire) run at on these cards, relative to the 600 MHz minion clock? Telemetry reports only the minion and NoC clocks.",
  "The conversion of the spec's shire-clock latencies (21-clock hit, 2-cycle panel access) into nanoseconds on the diagram's timeline; the 11-cycle read-buffer saving suggests 1:1 but does not prove it."),
 ("u-bw", "What limits the own-scratchpad stream to 128 B per shire-cycle (2.46 TB/s chip-wide), half of four banks x 64 B? The candidates are the sub-bank busy time, the response crossbar, the neighbourhood's Fill FIFO and 512-bit link, or the minions' 256-bit response ports; one neighbourhood alone reaches about 50 B per cycle.",
  "Which block the diagram highlights as the bottleneck when all 1,024 minions stream a TensorLoad."),
 ("u-remote-split", "Where do the ~53 extra cycles of a remote scratchpad read go (99.84 cycles at zero hops against 47 locally; 65.95 cycles + 56.48 ns): the to_l3 mesh master and its voltage-crossing FIFOs, the mesh stops, the target's L3-slave FIFO and reqq, the return path? The NoC reference manual (ask-noc-docs) and the shire cache's per-block latencies would split it.",
  "Per-block latency labels on the remote-read path, the one part of this level whose timing is drawn from a fit rather than from parts."),
]
for uid, q, settles in UNK:
    f(uid, "ask", q, None, None, "open question: not settled by any source in the repo, external/ or the published pages", "unknown", note="Settles: " + settles)

# ======================= access sequence =======================
SEQ = {}
SEQ["load_own"] = dict(
  title="A TensorLoad (or an L1-missing load) from the shire's own scratchpad",
  measured="47 cycles load-to-use for an L1-missing load (78 ns); 160 cycles for a 16-line TensorLoad by one minion; 2.25 / 4.40 pJ/B (zeros / random) chip-wide at 2.46 TB/s, 69% of it on the SRAM rail",
  steps=[
   dict(n=1, block="minion: tensor-load unit (DCache TensorLoad 0 FSM)", domain="minion rail 0.52 V, minion clock 600 MHz",
        does="Hart 0 writes CSR 0x83F; the FSM expands it into up to 16 line reads (address + i x stride), keeping up to 4 in flight. A scalar or vector load instead misses the L1 and a miss handler (2 per minion) asks for the line.",
        latency="about 10 cycles per extra line with 4 in flight (measured)", energy=None, kind="et-spec",
        source=PRM + " p.275; " + DCD + " p.40-44; docs/research/counters-and-dram.md:448-449"),
   dict(n=2, block="address decode", domain="minion / neighbourhood",
        does="Bits [39:31] = 9'h1 mark the scratchpad; the shire field (0x7F or the own ID) makes it local; bank = PA[7:6].",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.24; " + PRM + " p.486"),
   dict(n=3, block="neighbourhood request path", domain="LV to HV crossing (level shifters, semi-synchronous)",
        does="The minion's 256-bit ET-Link request enters the neighbourhood arbiter and a 3-deep bank FIFO, crosses from the low-voltage minion region into the high-voltage region on the shire clock, and is up-converted onto the neighbourhood's one 512-bit ET-Link.",
        latency="at least 4 clocks", energy=None, kind="et-spec", source=NMAS + " p.6, p.15-20 §4.3"),
   dict(n=4, block="request crossbar", domain="shire channel (high voltage)",
        does="Per-neighbourhood catch FIFO at the target bank; a round-robin arbiter picks one source per bank per cycle.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.30-31"),
   dict(n=5, block="bank reqq (64 entries)", domain="shire channel",
        does="Allocate an entry (stages ag, ad); compare with the read buffer (a hit goes to the RBUF: 10 shire clocks, 36 minion cycles load-to-use); check the index against the scratchpad region (error if beyond 640 sets); per sub-bank, round-robin among neighbourhood requests, L3-slave requests first, masked by sub-bank busy (stage rqa).",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.24-25, p.35-36, p.40, p.44-45"),
   dict(n=6, block="tag pipeline stages (tap, ta, ta0, ta1, te, tc)", domain="shire channel",
        does="For a scratchpad address the tag and tag-state RAM reads are squashed: nothing is compared, the request is a hit by definition, way = PA[11:10], set = PA[21:12]. The stages still elapse, which is why the scratchpad is exactly as fast as an L2 hit.",
        latency="fixed stages (part of the 21 shire clocks)", energy="tag and tag-state panels idle", kind="et-derived",
        source=RTLM + "shirecache_pipe_sub_bank.sv:155-159, 591-593; " + SCS + " p.44-46, p.57"),
   dict(n=7, block="data panels of sub-bank PA[9:8] (four 4,096 x 144 macros, one per quadword)", domain="SRAM rail 0.705 V (the rail that carries 69% of the read's power)",
        does="Stages dap, da, da0, da1: the panel clock is gated on; row {set, way} = PA[21:10] is read in all four panels at once; 576 bits (512 data + 64 ECC) come out after the 2-cycle access.",
        latency="2 shire-cache cycles (3.3 ns if at 600 MHz)", energy="about 182 pJ per line on the SRAM rail with random data, 92 with zeros (aifoundry2)", kind="et-spec",
        source=SCS + " p.44-48, p.51; " + RTLM + "shirecache_pipe_data_ram_wrap.sv; catalogue.json (energy, et-derived)",
        circuit=[
          dict(device="address latches and row predecoder", switches="capture {set, way} on the clock edge; NAND/NOR predecode selects one row", kind="generic"),
          dict(device="bitline precharge PMOS and equaliser", switches="turn off just before the wordline rises", kind="generic"),
          dict(device="wordline driver (inverter chain, large PMOS pull-up)", switches="drives one wordline high in each of the four panels (in the selected internal bank)", kind="generic"),
          dict(device="access NMOS pair of every cell on the row", switches="turn on and connect both storage nodes to BL and BLB", kind="generic"),
          dict(device="pull-down NMOS on each cell's 0 side", switches="sinks read current: one bitline of every pair on the row (including half-selected columns) droops some tens of mV to ~100 mV", kind="generic"),
          dict(device="column mux (m4: 4:1, if that is what m4 means)", switches="pass-gates connect 144 of the row's bitline pairs per panel to the sense amplifiers", kind="unknown"),
          dict(device="sense-enable timing (RM[3:0] read-margin trim, replica path)", switches="fires after the self-timed delay; RA read assist and BC bias control are the other trims", kind="et-spec"),
          dict(device="latch-type sense amplifier (cross-coupled pair + NMOS tail)", switches="resolves the small differential to full swing, 144 per panel", kind="generic"),
          dict(device="output latch and driver", switches="drive Q[143:0]; toggles only where the data differs from the previous read", kind="generic"),
          dict(device="wordline falls, precharge PMOS on", switches="restore the discharged bitlines to VDD: most of the array's read energy", kind="generic")]),
   dict(n=8, block="ECC check (stage de)", domain="shire channel",
        does="SECDED over 8 x (64 + 8) bits: a single-bit error is corrected, a double reported; no scrubbing on this chip.",
        latency="1 stage", energy=None, kind="et-spec", source=SCS + " p.46, p.48-49, p.99"),
   dict(n=9, block="data complete (stage dc), read buffer, response mux", domain="shire channel",
        does="The line is OR'ed out of the sub-bank, installed in the 8-entry read buffer (esr_sc_scp_rbuf_enable) and sent to the response mux's per-neighbourhood FIFO, or parked in the dataq if the mux is busy.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.40, p.43-46, p.101"),
   dict(n=10, block="response crossbar and neighbourhood fill path", domain="HV to LV crossing",
        does="The 512-bit line crosses the response crossbar into the neighbourhood's 4-entry Fill FIFO (one response per cycle, one every other cycle per agent), back into the minion region, and down the minion's 256-bit port in two beats.",
        latency="Fill FIFO at least 2 clocks; minion response path at least 2; 6 in all for a minion", energy="the whole fill of a line into the L1: 101 pJ zeros, 238 pJ random (measured)", kind="et-spec",
        source=NMAS + " p.21-23; " + EMF + ":44"),
   dict(n=11, block="L1 scratchpad (latch RAM) or TenB buffer", domain="minion rail 0.52 V",
        does="The TensorLoad FSM writes the line into consecutive L1-scratchpad lines (latch RAM, 4 blocks of 128 x 64 b); TensorLoad Setup B puts it in the VPU's 4-entry buffer instead; an ordinary load fills an L1 line.",
        latency=None, energy=None, kind="et-spec", source=DCD + " p.29, p.40-43"),
  ])
SEQ["store_own"] = dict(
  title="A TensorStore into the shire's own scratchpad",
  measured="1.23 TB/s chip-wide; 4.65 / 8.58 pJ/B (zeros / random), 76% on the SRAM rail; about 389 pJ per line on the SRAM rail with random data (aifoundry2)",
  steps=[
   dict(n=1, block="minion: TensorStore (CSR 0x87F)", domain="minion rail",
        does="Reads rows of 16, 32, 48 or 64 B from the vector registers and sends them as ET-Link writes (256-bit datapath; a 64 B row is a two-beat transfer), bypassing the L1 and L2 caches.",
        latency=None, energy=None, kind="et-spec", source=PRM + " p.306; " + NMAS + " p.15-20"),
   dict(n=2, block="neighbourhood, request crossbar, bank reqq and dataq", domain="LV to HV",
        does="As a load, but the data rides along and waits in the dataq entry; a local scratchpad write-around is turned into a regular write before the shire cache.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.13, p.35, p.62"),
   dict(n=3, block="pipeline", domain="shire channel",
        does="Tag and tag-state reads squashed; writes of 16 B or more are full-quadword writes (no read-modify-write); any read-buffer copy of the line is cleared.",
        latency=None, energy=None, kind="et-derived", source=RTLM + "shirecache_bank.sv:528-531; shirecache_pipe_sub_bank.sv:1055-1066; " + SCS + " p.40"),
   dict(n=4, block="data panels (only the written quadwords' panels are clocked)", domain="SRAM rail 0.705 V",
        does="Per-quadword write enable: a 32 B row writes 2 of the 4 panels, a 64 B row all 4.",
        latency="2 cycles", energy="about 2.1x a read per byte on the SRAM rail", kind="et-spec",
        source=SCS + " p.48; " + RTLM + "shirecache_pipe_data_ram_wrap.sv:83-96",
        circuit=[
          dict(device="write drivers", switches="pull BL or BLB of each written column fully to ground (full swing); WA sets the write assist", kind="generic"),
          dict(device="wordline driver", switches="raises the row for a pulse set by WPULSE", kind="generic"),
          dict(device="access NMOS vs cell PMOS pull-up", switches="the access transistor overpowers the pull-up on the side being written low; the cross-coupled pair flips", kind="generic"),
          dict(device="precharge PMOS", switches="recharge the fully discharged bitline: why a write costs more than a read", kind="generic"),
          dict(device="half-selected cells on the same row", switches="see a read-like disturb on their bitlines", kind="generic")]),
   dict(n=5, block="acknowledgement", domain="HV to LV",
        does="REP_Ack back through the response crossbar; TensorWait retires the store.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.12 Table 2 (REQ_Write local SCP), p.58-59 §3.4; " + PRM + " p.25 (TensorWait), p.272-274 §9.3"),
  ])
SEQ["load_remote"] = dict(
  title="A load from another shire's scratchpad",
  measured="99.84 + 12.00 cycles per hop at 600 MHz (112-220 cycles over 1-10 hops); 0.96 TB/s chip-wide at 2.1 hops; 5.10 / 11.8 pJ/B at 2.1 hops, +0.67 / 1.80 pJ/B per hop",
  steps=[
   dict(n=1, block="requesting minion, neighbourhood, request crossbar, bank", domain="as the local load",
        does="The shire field does not match: the reqq sends a Mesh_Read instead of using the pipeline.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.56-57 Figure 16"),
   dict(n=2, block="to_l3 mesh master (4 ports)", domain="shire channel to NoC clock (VCFIFOs with 2-stage synchronisers)",
        does="Request xbar onto one of 4 ports, ET-Link converted to AXI AR, through a voltage-and-clock-crossing FIFO into the mesh.",
        latency="part of the ~53 cycles of leaving and entering shires", energy=None, kind="et-spec", source=SCS + " p.11, p.32-33 §2.3"),
   dict(n=3, block="mesh (NoC routers and links, 0.485 V, 400 MHz)", domain="NoC rail",
        does="The request and later the 64 B response cross the mesh: 12 minion cycles (20 ns, 8 mesh cycles) per hop, round trip.",
        latency="12.00 cycles per hop (measured)", energy="0.67 / 1.80 pJ/B per hop (zeros / random, board); mesh rail 1.27 pJ/B per hop", kind="et-measured",
        source=CLM + ":423; " + EMF + ":9-22, :181"),
   dict(n=4, block="target shire: mesh slave (L3-slave port, 4 ports) and bank L3 slave", domain="NoC to shire channel",
        does="AXI to ET-Link, onto the bank's L3-slave FIFO; up to 21 reqq entries are reserved for such requests and they beat local neighbourhood requests in each sub-bank's arbitration.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.33-36, p.44 §2.13"),
   dict(n=5, block="target bank: read buffer or pipeline and data panels", domain="target's SRAM rail",
        does="Exactly steps 6-9 of the local load (tags squashed, 4 panels read, ECC); an L3-slave scratchpad read may also hit and fill the read buffer.",
        latency="the pipeline", energy="rail split at 1 hop: 50% SRAM, 27% mesh, 14% minions", kind="et-spec", source=SCS + " p.57-58 Figure 17, p.40, p.44; " + EMF + ":174"),
   dict(n=6, block="return: rspmux_l3, mesh, requester's to_l3 port, bank response FIFO, response crossbar, neighbourhood", domain="back through the NoC",
        does="AXI R data back over the mesh to the requesting bank, which forwards it to the neighbourhood as for a local load.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.33, p.43-44"),
  ])
SEQ["store_remote"] = dict(
  title="A write into another shire's scratchpad",
  measured="the relay hands data to the next shire at 592.5 GB/s for 8.92 pJ/B moved (write + read), against 116.2 through DRAM",
  steps=[
   dict(n=1, block="local bank", domain="shire channel",
        does="A plain remote write goes from the dataq straight to the mesh; a TensorStore write-around is coalesced in the local L2 (a partial line occupies a local L2 line and the coalescing buffer) and sent when all four quadwords are present; a full-line write-around that misses bypasses the local panels.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.13, p.40, p.62-63; " + ERR + " p.84; " + RTLM + "shirecache_pipe_sub_bank.sv:640-642"),
   dict(n=2, block="mesh and target L3 slave", domain="NoC",
        does="AXI AW/W across the mesh into the target's L3-slave port.", latency="12 cycles per hop round trip", energy=None, kind="et-spec", source=SCS + " p.17, p.62"),
   dict(n=3, block="target pipeline and data panels", domain="target's SRAM rail",
        does="Written like a local scratchpad write (step 4 of store_own); acknowledged back to the L3 slave.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.62 §3.4.5"),
  ])
SEQ["fill"] = dict(
  title="The scratchpad's only 'refill': TensorLoadL2Scp (REQ_ScpFill)",
  measured="not measured separately",
  steps=[
   dict(n=1, block="minion (hart 0 or hart 1) -> bank", domain="as a store",
        does="CSR 0x85F; for each line the bank issues a Mesh_Read of the source (L3, DRAM or a remote scratchpad; never the local L2, whose dirty data it ignores).",
        latency=None, energy=None, kind="et-spec", source=PRM + " p.289-290; " + SCS + " p.87"),
   dict(n=2, block="bank pipeline, data panels", domain="SRAM rail",
        does="When the line returns, an SCP_Fill writes it into the local scratchpad row; no victim, no tag.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.87 Figure 43"),
  ])
SEQ["atomic"] = dict(
  title="A global atomic on a scratchpad word",
  measured="10.00 cycles per atomic at the home bank; 216 cycles uncontended round trip; 22 hammering minions of one shire stop the host shire's own scratchpad traffic",
  steps=[
   dict(n=1, block="minion -> UC block -> mesh -> home shire's L3 slave", domain="as a remote access",
        does="Atomics to the scratchpad are not accepted from a neighbourhood directly ('must go to UC block'); through the self ID 0x7F they are a bus error.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.13; " + CLM + ":232"),
   dict(n=2, block="home bank: data panel read, atomic block (3-stage ALU), data panel write", domain="SRAM rail",
        does="The sub-bank is held busy from the read through the write; the response goes back as an ESR write over to_sys.",
        latency="10.00 cycles per atomic (measured)", energy=None, kind="et-spec", source=SCS + " p.17, p.36, p.40 §2.9; " + CLM + ":427"),
  ])
SEQ["miss_refill_refresh"] = dict(
  title="Miss, refill, refresh",
  measured=None,
  steps=[
   dict(n=1, block="(none)", domain=None,
        does="The scratchpad has no misses and no victims: every in-range address is a hit, and an out-of-range index returns an error (SC_PipeErr_ScpOpToNonEnRegion). Nothing is ever evicted.",
        latency=None, energy=None, kind="et-spec", source=SCS + " p.24-25, p.57, p.87"),
   dict(n=2, block="(none)", domain=None,
        does="No refresh if the cells are SRAM (GENERIC: static storage); the only standing cost is leakage, at most 19.6 mW per MB at 80 C on this rail.",
        latency=None, energy="leakage <= 19 nJ per byte-second at 80 C", kind="generic",
        source="GENERIC; " + EMF + ":110-111", circuit=[dict(device="every cell on the 705 mV rail", switches="nothing switches; subthreshold and gate leakage through the off transistors", kind="generic")]),
   dict(n=3, block="(none)", domain=None,
        does="No ECC scrubbing on ET-SoC-1 (a reserved bit for future chips).", latency=None, energy=None, kind="et-spec", source=SCS + " p.99"),
  ])

meta = dict(
  level="scp", title="Scratchpad: the shire cache configured as software-managed memory, own and remote",
  file="facts-scp.json", built_by="build_facts_scp.py (beside this file)", date="2026-09-27",
  kinds={"et-spec": "stated by an ET document, RTL or firmware source", "et-measured": "measured on the cards (repo data)",
         "et-derived": "computed or inferred here from ET sources or measurements", "generic": "textbook or vendor-generic, not ET-specific: label GENERIC on the page",
         "unknown": "not settled by any source: an ask for the team"},
  paths="Source paths are relative to the et-soc1-prototyping checkout (external/...) or to the repository root (docs/, workloads/). PDF pages are pdf page numbers from pdftotext -layout (the Shire Cache Specification's printed page numbers coincide).",
  caveats=[
    "core-et in external/ is the Erbium branch; the shire cache RTL is not in it. RTL behaviour quoted for the scratchpad is from Ainekko's re-implementation (external/core-et-main), co-simulated against the original shire_cache (STATUS.md:87, 140).",
    "The Shire Cache Specification is v1.1 and also describes later chips (Nemi, Gepardo sections); its macro and trim tables are not labelled per chip.",
    "Rail energies are regulator-output powers over idle from the PMIC's running average (tau about 1.15 s); what else shares the SRAM rail is unknown.",
    "The chip tour's facts cite 05-claims.md at older line numbers (366, 409, 411); the current file has those rows at 376, 421, 423."],
  numbers_from_repo=dict(
    sram_rail_pj_per_byte={f"{c}|{k}": round(v["sram_pjB"], 3) for (c, k), v in rails.items()},
    tensorload_cycles=tl))

json.dump(dict(meta=meta, facts=F, access_sequence=SEQ,
               unknowns=[dict(id="scp." + u[0], question=u[1], settles=u[2]) for u in UNK]),
          open(OUT, "w"), indent=1, ensure_ascii=False)
print("facts", len(F), "kinds", {k: sum(1 for x in F if x["kind"] == k) for k in ("et-spec", "et-measured", "et-derived", "generic", "unknown")})
