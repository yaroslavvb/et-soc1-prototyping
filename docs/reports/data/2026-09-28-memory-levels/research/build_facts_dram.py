#!/usr/bin/env python3
"""Build facts-dram.json: the DRAM level of 'Anatomy of a memory access', as sourced facts plus
ordered access sequences (a load, a row hit, a row conflict, a store, a refresh) down to the circuit.

Path conventions in `source`:
  external/...          = the et-soc1-prototyping checkout's external/ (et-platform at 836a4ab;
                          core-et erbium branch; et-man manuals, pdf page numbers from pdftotext)
  docs/..., workloads/  = the repo (worktree et-soc1-pages5, branch pages-v5, HEAD 09bf5df). Pages that another
                          workflow is editing are cited by section anchor or JSON field, not by line.
kind: et-spec | et-measured | et-derived | generic | unknown.
"""
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facts-dram.json")

ANAT = "https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy"
EM = "https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual"
MH = "https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy"
LOO = "https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability"
HPM = "https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm"
CHIP = "https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram"
RELAY = "https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay"
C3 = "aifoundry2, aifoundry3, aifoundry1-c1"

PRM = "external/et-man/ET Programmer's Reference Manual.pdf"
DS = "external/et-man/ET Preliminary Datasheet Rev 1.0.pdf"
ERR = "external/et-man/ET-SoC Errata.pdf"
CARD = "external/et-man/ET-PCIe-Dev-Card-V3.pdf"
INIT = "external/et-platform/etsoc-hal/src/memshire_ddr_init_functions.c"
MC = "external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c"
MCU = "external/et-platform/device-bootloaders/src/ServiceProcessorBL2/utils/mem_controller_utils.c"
UMCTL = "external/et-platform/etsoc-hal/include/etsoc_hal/inc/DWC_ddr_umctl2.html"
MSDEF = "external/core-et/rtl/inc/memshire_defines.vh"
SCSPEC = "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf"
CAD = "docs/research/counters-and-dram.md"
V3 = "docs/reports/data/2026-09-25-claims-v3/results"
MAN = "docs/reports/data/2026-09-23-energy-manual/manual.json"
MP = "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json"
CL = "docs/findings/05-claims.md"

facts = []


def F(id, topic, statement, source, kind, value=None, unit=None, card=None, page_link=None, note=None, **extra):
    assert kind in ("et-spec", "et-measured", "et-derived", "generic", "unknown"), kind
    d = dict(id=id, level="DRAM", topic=topic, statement=statement, value=value, unit=unit, source=source,
             kind=kind, card=card, page_link=page_link, note=note)
    d.update(extra)
    facts.append(d)


# ---------------------------------------------------------------- topology: memory shires, channels, packages
F("dram.topo.memshires", "topology",
  "Eight memory shires, four on the west side (0-3) and four on the east side (4-7) of the die, each driving two "
  "16-bit LPDDR4X channels: 16 channels in all.",
  f"{PRM} pdf p.17 §1.5 (txt line 544-548); {DS} pdf p.30 §7 and §7.1",
  "et-spec", 8, "memory shires", page_link=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop",
  note="West 0-3 / east 4-7 is the PRM's and the firmware's naming; the latency fit's logical map draws them above "
       "and below the grid (chip-diagram fact fw.memshires).")

F("dram.topo.packages", "topology",
  "Four LPDDR4X packages on the card, each with four 16-bit channels (64 bits per package, 256 bits in all); two "
  "memory shires share each package.",
  f"{PRM} pdf p.17 §1.5; {DS} pdf p.30 §7 ('Two Memshires communicate with each 64-bit LPDDR4X memory device'); "
  f"{CARD} pdf p.3 ('4 x LPDDR4x DRAM devices for a combined 256-bit memory interface')",
  "et-spec", 4, "packages",
  note="The datasheet's §2.2.2 (pdf p.16) calls each package a 'bank' ('four banks of LPDDR4X memory. Each bank is "
       "controlled by two Memory Shires'): not a DRAM bank. The diagram should say 'package'.")

F("dram.topo.pkg-pairing", "topology",
  "Which two memory shires share each LPDDR4X package is not documented; the chip diagram pairs neighbours (0-1, 2-3, "
  "4-5, 6-7) on an assumption.",
  f"{DS} pdf p.30 §7; docs/reports/data/2026-09-27-chip-diagram/facts.json facts['dram.pkg-pairing']; hub ask "
  "'ask-card-schematic' (docs/reports/sources/limits-of-observability.data.json improvements[24])",
  "unknown", page_link=CHIP)

F("dram.topo.controllers", "memory shire",
  "Each memory shire holds two Synopsys uMCTL2 DDR controller instances, one per 16-bit channel: the firmware "
  "programs controller blocks 0 and 1 of every memory shire, and the memory shire has separate mode-register "
  "read-back registers for 'memory controller 0' and 'memory controller 1'.",
  f"{PRM} pdf p.17 §1.5 ('connected to two memory controllers that each have a 16-bit LPPDR4X channel'); "
  f"{PRM} pdf p.515 Table 15-90 (ddrc_u0_mrr_data, ddrc_u1_mrr_data); {MCU}:83-88 (get_ddrc_address: block 1 at "
  f"+0x1000), :604-607 (ms_write_both_ddrc_reg); {ERR} pdf p.88 (errata 5.2 cites the uMCTL2 Databook v3.50a)",
  "et-spec", 2, "controllers per memory shire",
  note="The datasheet disagrees: 'two 16-bit LPDDR4X physical interfaces sharing a single 32-bit controller' "
       f"({DS} pdf p.30 §7). Firmware and PRM agree on two controllers; see dram.topo.phy and the ask.")

F("dram.topo.phy", "memory shire",
  "One DDR PHY per memory shire serves both channels: the firmware writes one PHY training message block per memory "
  "shire, with the DRAM's MR14 (VREF-DQ) set for 'Channel A' and 'Channel B'; the open RTL gives the memory shire's "
  "DDR subsystem 4 data-byte lanes (DBYTEs, 2 per 16-bit channel), 6 address/command blocks (ANIBs) and a 16-bit "
  "DRAM data width.",
  f"{MC}:190-192 (ms_patch_phy_ram_before_training); {MCU}:778-783 (ms_write_phy_ram: one PHY RAM window per memory "
  f"shire); {MSDEF}:40 (DDR_DRAM_DATA_SIZE 16), :48-49 (DDR_NUM_ANIBS 6, DDR_NUM_DBYTES 4); {PRM} pdf p.514 "
  "(ddrc_reset_ctl 'DDRC PUB reset')",
  "et-derived", 1, "PHY per memory shire (2 channels)",
  note="The PHY stores up to four PSTATEs of training values (errata 5.4, pdf p.90) and has a PUB: a Synopsys "
       "DesignWare LPDDR4-class PHY, product and version not named in any source. core-et is the Erbium-branch open "
       "drop; its memory-shire headers match the ET-SoC-1 firmware wherever both speak (see dram.addr.*).")

F("dram.topo.noc-port", "memory shire",
  "The NoC connects three ports to each memory shire (memory traffic, global-atomic responses, ESR accesses); the "
  "memory port is an AXI slave with a 512-bit data path (a whole 64-byte line per beat), and the NoC side delivers at "
  "most 32 GB/s per memory shire, almost twice the LPDDR4X side.",
  f"{DS} pdf p.30 §7.1.1 and §7.1.1.1",
  "et-spec", 32, "GB/s per memory shire (NoC side)")

F("dram.topo.floorplan", "topology",
  "On the die the memory shires and their LPDDR4X PHYs form a strip about 1.76 mm wide down each side (1.74 and "
  "1.80 mm); the 6-column shire grid between them spans about 22.2 mm.",
  "docs/reports/data/2026-09-27-chip-diagram/facts.json facts['L08'], facts['L09'] (from docs/reports/data/"
  "2026-09-24-wire-energy/report.json inputs.memshire_w_mm)",
  "et-derived", 1.76, "mm", page_link=HPM + "#die",
  note="Derived from the published die size and photo geometry, not from a floorplan document.")

F("dram.topo.pll", "clocks",
  "The boot firmware programs the memory PLL in memory shire 0 and memory shire 4 only: one PLL per side.",
  f"{MC}:134-172 (configure_memshire_plls: program_memshire_pll(0, ...), program_memshire_pll(4, ...))",
  "et-spec", 2, "memory PLLs",
  note="How the clock reaches memory shires 1-3 and 5-7 is not described; presumably distributed along each side.")

# ---------------------------------------------------------------- address mapping
F("dram.addr.memshire", "address mapping",
  "The memory shire that serves a line is picked by physical-address bits 8:6, so consecutive 64-byte lines rotate "
  "over the eight memory shires; the memory shire's read counter confirmed the bits for 64 of 64 lines in every one "
  "of 15 passes on three cards.",
  f"{MSDEF}:21 (`MEMSHIRE_SEL_ADDR_RANGE 8:6`); {SCSPEC} pdf p.26 §1.4.3 ('the Memory Shire is selected by the NoC "
  "using bits [8:6] by default'); external/et-platform/device-minion-runtime/tools/zebumem.c:68-72; "
  f"{V3}/mem.json [item=MEM-P3].per_card.<card>.tests.P3_msmap_match (64 of 64 lines per pass); anatomy page §4",
  "et-spec", "PA[8:6]", None, card=C3, page_link=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop",
  note="Measured as well as specified. PA[8:6] are the low three bits of the L3 home shire's PA[10:6], so memory "
       "shire m serves home shires m, m+8, m+16, m+24.")

F("dram.addr.channel", "address mapping",
  "Inside the memory shire, physical-address bit 9 picks the controller (the channel): the memory shire's control "
  "register resets with its controller-select bit field at 9 and both controllers enabled, and the default boot "
  "never rewrites it. The two channels alternate every 512 bytes.",
  f"{MSDEF}:22 (`MEMSHIRE_MCTL_SEL_ADDR_RANGE 9`); external/et-platform/etsoc-hal/include/hwinc/ms_regs.h:160 "
  "(MS_REGS_MS_MEM_CTL_RESET_VALUE 0x000307f1892481c6: esr_ms_addr_mc_bit_sel = 9, esr_ms_mc_en = 3; fields at "
  "ms_regs.h:489-600); external/core-et/rtl/inc/esr_defines.vh:149-158 (ESR_MS_MEM_CTL_RESET_VAL); only the "
  "reduced-memory-shire path writes ms_mem_ctl (external/et-platform/device-bootloaders/src/ServiceProcessorBL2/"
  "driver/noc_configuration.c:294-313); zebumem.c:72 ('addr[9] controller (0=even, 1=odd)')",
  "et-spec", "PA[9]",
  note="Upgrades the earlier inference from a tool comment (counters-and-dram.md §3.4, chip-diagram fact L50): the "
       "reset value is in the SoC's own register header. Latency cannot see this bit: flipping it, like flipping a "
       "bank bit, lets the second load ride along (memprobe summary.json bits['9'].b_minus_b0_med = 0).")

F("dram.addr.strip", "address mapping",
  "Before a request reaches its controller, the memory shire removes physical-address bits 9:6 (the memory-shire and "
  "channel bits), so each controller sees its own lines as one contiguous address space.",
  "external/et-platform/etsoc-hal/include/hwinc/ms_regs.h:160 (reset value decodes to esr_ms_addr_remove_bit_sel0..3 "
  "= 6, 7, 8, 9); external/core-et/rtl/inc/esr_defines.vh:149-158; external/core-et/rtl/inc/memshire_types.vh "
  "(memshire_esr_ctl_t)",
  "et-spec", "PA[9:6] removed")

F("dram.addr.addrmap", "address mapping",
  "The controllers' address map as programmed (ECC off): column bits 4:0 = HIF 4:0, bank bits 2:0 = HIF 7:5, column "
  "bits 9:5 = HIF 12:8, row bits 16:0 = HIF 29:13 (HIF is the controller's internal address in 16-bit words).",
  f"{INIT}:4639-4654 (ADDRMAP1 0x00030303, ADDRMAP2 0x03000000, ADDRMAP3 0x03030303, ADDRMAP5-6 0x07070707, "
  f"ADDRMAP7 0x00000f07); field meanings and internal bases from {UMCTL} (ADDRMAP1-7); {CAD} §3.4",
  "et-spec", None,
  note="Register values are from the firmware source; the running cards' registers have not been read back (the "
       "hub's ask-memshire). The 32 GB ECC branch (:4590-4626) is not taken: ECC is off.")

F("dram.addr.pa-map", "address mapping",
  "In physical-address terms, inside one channel: bank = PA[12:10] (8 banks), column = PA[17:13] and PA[5:1] (1,024 "
  "columns of 16 bits, a 2 KB page), row = PA[34:18] (17 bits). A 64-byte line is two 32-byte BL16 bursts from one "
  "row; PA[5] picks the half.",
  f"derived from dram.addr.strip and dram.addr.addrmap (HIF = controller byte address / 2 for a 16-bit channel); "
  f"measured by flipping one bit: {MP} bits['13'..'17'].b_minus_b0_med = -12 (same row), bits['18'..'29'] = +9 "
  f"(other row), bits['6'..'12'] ~ 0; {V3}/mem.json MEM-P4; anatomy page §5 #which-address-bits-share-a-row; {CAD} §3.4",
  "et-derived", None, card=C3, page_link=ANAT + "#which-address-bits-share-a-row",
  note="Bank and row bits are measured (a same-bank, other-row pair conflicts from bit 18 up on three cards); the "
       "split of PA[12:10] into bank rather than channel or column is from the programmed map. zebumem.c:74-111 "
       "prints a different swizzle, but only 'if using DDR DRAM models' (an emulation model), and silicon disagrees "
       "with it.")

F("dram.addr.interleave", "address mapping",
  "Consequences of the map: 64-byte lines rotate over the 8 memory shires, the 2 channels of each alternate every "
  "512 B, a channel sees one line per 1 KB and puts consecutive lines of its own in consecutive banks, a bank's row "
  "holds 32 lines spaced 8 KB apart, and a 256 KB aligned block touches one row in each of the 128 channel-banks.",
  f"{CAD}:352-371 (§3.4); docs/energy-manual/04a-fine-grain.md '## Rows' (sequential: next bank, 32 columns per row "
  "visit)",
  "et-derived", 128, "channel-banks")

F("dram.addr.region", "address mapping",
  "DRAM starts at physical address 0x80_0000_0000; minions reach only the 'Low' view, and device allocations come "
  "back as 0x80_xxxx_xxxx addresses.",
  f"{PRM} pdf p.551 (Table 15-96) and p.553 (Table 15-98); {CAD}:348-350, 379",
  "et-spec", "0x80_0000_0000")

# ---------------------------------------------------------------- DRAM organisation
F("dram.org.capacity", "DRAM organisation",
  "32 GB of LPDDR4X on the V3 cards (a Micron part): 2 GB, i.e. 16 Gbit, per channel; the chip supports up to 32 GB "
  "'using LPDDR4X at 16 Gbits per channel'.",
  f"{CARD} pdf p.1 ('32GB (Micron part) v3 card'); {DS} pdf p.30 §7.1; {MC}:389-398 (MR8 density decode to 32 GB)",
  "et-spec", 32, "GB")

F("dram.org.geometry", "DRAM organisation",
  "Each channel is one rank of 8 banks x 131,072 rows x 2 KB pages (1,024 columns of 16 bits): 8 x 131,072 x 2 KB = "
  "2 GB, matching the capacity. One activate therefore senses 16,384 bits into one bank's sense amplifiers.",
  f"{INIT}:4639-4654 (3 bank, 10 column, 17 row address bits); {MSDEF}:38 (`DDR_BANKS_SIZE 3`); {INIT}:4539 (ODTMAP "
  "rank 0 only); JEDEC JESD209-4 addressing for a 16 Gb-per-channel LPDDR4 die (8 banks, R0-R16, C0-C9, 2 KB page)",
  "et-derived", 16384, "bits sensed per activate",
  note="The geometry is what the programmed map and the capacity require and what JEDEC specifies for this density "
       "(GENERIC); the part's datasheet, which would confirm it, is not in the sources.")

F("dram.org.line-vs-page", "DRAM organisation",
  "A 64-byte line uses 512 of the 16,384 bits an activate senses: 1/32 of the open row. The other 31 lines of that "
  "row (8 KB apart in the address space) can then be read as row hits until the row closes.",
  "arithmetic on dram.org.geometry and dram.addr.pa-map",
  "et-derived", 32, "lines per open row")

F("dram.org.part", "DRAM organisation",
  "The exact LPDDR4X part (Micron part number), its die density, the number of dies per package and whether each "
  "channel is one x16 die or two byte-mode dies are not in any source. The firmware reads the vendor (MR5; Micron = "
  "0xFF) and density (MR8) at every boot and logs them, but no log has been captured.",
  f"{CARD} pdf p.1; {MC}:364-398 (ddr_config: 'DRAM vendor = MICRON', 'DRAM size = 32GB'); {MCU}:936-1027 "
  "(ms_verify_ddr_density; comment 'for the micron part it is 0x10 for 32gb and 0x18 for 64gb')",
  "unknown",
  note="The firmware labels MR8 density code 6 '64gb/32GB' (mem_controller_utils.c:1000-1004); in JEDEC LPDDR4 terms "
       "code 6 is 32 Gb per die, 16 Gb per channel (GENERIC), which fits 2 GB per channel.")

F("dram.org.die-internals", "DRAM organisation",
  "The die's internal organisation below the bank (subarrays or mats, cells per bitline, open or folded bitlines, "
  "sense-amplifier variant, wordline boost and array voltages, cell capacitance, process node) is vendor-proprietary "
  "and appears in no ET source; the diagram's transistor level is therefore JEDEC/textbook GENERIC.",
  "none (absence noted across external/et-man, external/core-et, external/et-platform)",
  "unknown")

# ---------------------------------------------------------------- controller configuration
F("dram.ctl.clock", "clocks",
  "The firmware hard-codes the '933 MHz' DDR mode on every card: the controller (DFI) clock is 933 MHz and runs 1:2 "
  "with the DRAM clock, so the DRAM clock is 1,866 MHz and the data rate 3,733 MT/s, not the datasheet's 4,266. "
  "Telemetry reads mhz.ddr = 933 in every sample.",
  f"{MC}:643-649 (DDR_FREQUENCY_933MHZ, '//TODO: decide ddr_mode'); {INIT}:768 (DfiFreqRatio_p0=1), :4536 (MSTR "
  "0x00080020: lpddr4=1, burst_rdwr=8 = BL16); docs/reports/data/2026-09-20-power-aifoundry2/horace2-telemetry.jsonl "
  "field mhz.ddr",
  "et-spec", 3733, "MT/s", card="aifoundry2", page_link=ANAT,
  note="One DFI clock = 1.071 ns, one DRAM clock tCK = 0.536 ns; timings below convert DFI clocks to ns. At 600 MHz "
       "one minion cycle is 1.667 ns.")

F("dram.ctl.peak-bw", "bandwidth",
  "At 3,733 MT/s a 16-bit channel peaks at 7.47 GB/s, a memory shire at 14.9 GB/s and the chip at 119.5 GB/s; at the "
  "datasheet's 4,266 MT/s the chip would reach 136.5 GB/s.",
  f"arithmetic: 2 B x 3.733 GT/s; {DS} pdf p.4 §1 (4,266 MT/s, printed '133 Gbytes/s')",
  "et-derived", 119.5, "GB/s")

F("dram.ctl.noc-headroom", "bandwidth",
  "Each memory shire's NoC side (32 GB/s) is 2.1x its DRAM side at the programmed rate (14.9 GB/s).",
  f"{DS} pdf p.30 §7.1.1; dram.ctl.peak-bw",
  "et-derived", 2.1, "x")

F("dram.ctl.measured-bw", "bandwidth",
  "Streaming from DRAM the whole chip reaches 76 GB/s at 600 MHz (64% of 119.5); tensor stores to DRAM also reach "
  "76 GB/s, stores through the L1 27 GB/s.",
  f"{CL}, row 'Bandwidth at 600 MHz, 1,024 minions' (E33, E29); docs/energy-manual/04-bytes-memory.md table rows "
  "'Tensor load from DRAM', 'fsw.ps stores to DRAM through the L1'",
  "et-measured", 76, "GB/s", card="aifoundry2, aifoundry3", page_link=MH + "#the-hierarchy-as-a-spec-sheet")

F("dram.ctl.page-policy", "controller policy",
  "Open-page policy: the controller keeps a bank's row open until it must close it (another row of that bank, or a "
  "refresh); no page-close timer, no auto-precharge.",
  f"{INIT}:4661-4664 (SCHED 0x00a01f01: pageclose=0; SCHED1 pageclose_timer=0), :4668 (PCCFG 0); {MC}:245 "
  f"(config_auto_precharge = 0); {PRM} pdf p.514 (ddrc_main_ctl: read/write auto-precharge, high/low priority); "
  f"meaning of pageclose=0 from {UMCTL} (SCHED.pageclose: 'the bank remains open until there is a need to close it "
  "... also known as open page policy')",
  "et-spec", page_link=ANAT + "#how-long-a-row-stays-open",
  note="Measured: 96% of loads whose previous load came after the last refresh were row hits, 4% across a refresh "
       "(anatomy §5; 95-96% vs 3-4% on three cards).")

F("dram.ctl.tRCD", "DRAM timing",
  "Activate-to-read delay tRCD = 17 DFI clocks = 18.2 ns (10.9 minion cycles at 600 MHz).",
  f"{INIT}:4430 (DRAMTMG4 0x11040a11: t_rcd=0x11); {CAD}:303",
  "et-spec", 18.2, "ns",
  note="Measured: an open-row hit saves 11-12 cycles (dram.lat.row-hit).")

F("dram.ctl.tRP", "DRAM timing",
  "Precharge time tRP = 17 DFI clocks = 18.2 ns (10.9 cycles).",
  f"{INIT}:4430 (DRAMTMG4 t_rp=0x11); {CAD}:304",
  "et-spec", 18.2, "ns",
  note="Measured: a load to another row of the bank just used pays about 9-10 cycles more (dram.lat.row-sequential).")

F("dram.ctl.tRAS-tRC", "DRAM timing",
  "Minimum row-open time tRAS = 40 DFI clocks = 42.9 ns; row cycle tRC (activate to activate in one bank) = 59 DFI "
  "clocks = 63.2 ns (37.9 cycles).",
  f"{INIT}:4415 (DRAMTMG0 0x1e261f28: t_ras_min=0x28), :4417 (DRAMTMG1 0x0007083b: t_rc=0x3b); {CAD}:305-306",
  "et-spec", 63.2, "ns (tRC)",
  note="tRC matches the measured back-to-back row-conflict penalty (+36.5 to +38.5 cycles, dram.lat.row-conflict).")

F("dram.ctl.RL-WL", "DRAM timing",
  "Read latency RL = 18 DFI clocks = 36 DRAM clocks = 19.3 ns (read DBI on); write latency WL = 8 DFI = 16 DRAM "
  "clocks = 8.6 ns.",
  f"{INIT}:4425 (DRAMTMG2 0x08121316: read_latency=0x12, write_latency=0x8), :4440 (INIT3 mr=0x64 (MR1), emr=0x36 "
  f"(MR2)); {CAD}:307",
  "et-spec", 19.3, "ns (RL)")

F("dram.ctl.burst", "DRAM timing",
  "Burst length 16 on a 16-bit channel: one READ returns 32 bytes in 8 DRAM clocks (4.3 ns, tCCD = 4 DFI clocks), so "
  "a 64-byte line takes two READs to the same row.",
  f"{INIT}:4536 (MSTR burst_rdwr=0x8 = BL16 per {UMCTL} MSTR.burst_rdwr), :4430 (t_ccd=0x4); {CAD}:308, 366",
  "et-spec", 4.3, "ns per 32-byte burst")

F("dram.ctl.tRRD-tFAW", "DRAM timing",
  "Activate-to-activate in different banks tRRD = 10 DFI = 10.7 ns; at most four activates per rolling tFAW = 38 DFI "
  "= 40.7 ns per channel.",
  f"{INIT}:4430 (t_rrd=0xa), :4415 (t_faw=0x26); {CAD}:309",
  "et-spec", 40.7, "ns (tFAW)")

F("dram.ctl.tWR", "DRAM timing",
  "Write recovery: MR1 = 0x64 sets nWR = 34 DRAM clocks (18.2 ns); write-to-precharge wr2pre = 30 DFI clocks, "
  "read-to-precharge rd2pre = 8.",
  f"{INIT}:4440 (INIT3 mr=0x64), :4415 (wr2pre=0x1e), :4417 (rd2pre=0x8); {CAD}:310, 322",
  "et-spec", 34, "DRAM clocks (nWR)")

F("dram.ctl.dbi", "I/O",
  "Data-bus inversion is on for reads and writes, and data masking is enabled (MR3 = 0xF1).",
  f"{INIT}:4522 (DBICTL 0x7: rd_dbi_en=1, wr_dbi_en=1, dm_en=1), :4398 (INIT4 emr2=0xf1 = MR3); {CAD}:322",
  "et-spec")

F("dram.ctl.refresh-mode", "refresh",
  "All-bank refresh every tREFI = 113 x 32 = 3,616 DFI clocks = 3.875 us, each taking tRFCab = 262 DFI clocks = "
  "280.7 ns; per-bank refresh off; temperature derating not enabled.",
  f"{INIT}:4441 (RFSHCTL0 0x00210000: per_bank_refresh=0), :4443 (RFSHTMG 0x80710106: t_rfc_nom_x1_x32=0x71, "
  f"t_rfc_min=0x106), :5475 (RFSHCTL3=0: auto-refresh on after init), :4686-4688 (DERATEEN commented out: 'FUTURE "
  f"derate is not needed for bring-up'); {UMCTL} RFSHTMG.t_rfc_nom_x1_sel ('for ... per-bank refresh only'; unit "
  "'multiples of 32 DFI clock cycles')",
  "et-spec", 3.875, "us (tREFI)", page_link=ANAT + "#refresh-caught-in-the-act",
  note="counters-and-dram.md §3.2 had to guess the x32 reading because t_rfc_nom_x1_sel=1; the uMCTL2 register "
       "description says x1_sel applies only to per-bank refresh, and the measured period (dram.lat.refresh-period) "
       "confirms x32.")

F("dram.ctl.refresh-duty", "refresh",
  "All-bank refresh keeps each channel busy 280.7 / 3,875 ns = 7.2% of the time; 7.2% of loads issued at random phases "
  "landed inside a refresh.",
  f"arithmetic on dram.ctl.refresh-mode; {MP} refresh.in_refresh = 0.0721",
  "et-derived", 7.2, "%", card="aifoundry2", page_link=ANAT + "#refresh-caught-in-the-act")

F("dram.ctl.power-down", "controller policy",
  "No power-down and no self-refresh: the firmware disables both 'for performance reasons', so an idle channel stays "
  "in active standby with its clocks running.",
  f"{INIT}:5459 (PWRCTL 0x0), :4738; {CAD}:331",
  "et-spec",
  note="GENERIC consequence: the DRAM's active-standby current flows whenever the card is up; its share of the idle "
       "12-18 W unmetered power is unattributed (hub §4.2).")

F("dram.ctl.zq", "controller policy",
  "Automatic ZQ calibration (the periodic re-trim of the DRAM's output-driver and termination impedance) is disabled.",
  f"{INIT}:4446 (ZQCTL0 0xc3a50000: dis_auto_zq=1, dis_srx_zqcl=1); {CAD}:332",
  "et-spec")

F("dram.ctl.dfi-update", "controller policy",
  "The controller requests DFI controller updates (PHY re-trims) automatically every 64-255 x 1,024 DFI clocks "
  "(70-280 us).",
  f"{INIT}:4528-4531 (DFIUPD0 dis_auto_ctrlupd=0; DFIUPD1 interval min 64, max 255 x1024); {CAD}:333",
  "et-spec", None, None,
  note="That these cause rare latency blips is an inference (counters-and-dram.md), not measured.")

F("dram.ctl.ecc", "controller policy",
  "DRAM ECC is off.",
  f"{MC}:643-647 (ddr_mode .ecc = false); {INIT}:4557 (ECCCFG0 0x003f7f10 'disable ECC')",
  "et-spec")

F("dram.ctl.ports", "controller queues",
  "Each controller has two AXI ports with aging on: port 0 at priority 15 (commented 'lower priority') and port 1 at "
  "priority 8 ('higher priority'), for reads and writes alike; the memory shire keeps high/low request lines per "
  "controller, and the shire cache marks its to-memory requests high or low QoS from an ESR.",
  f"{INIT}:4670-4680 (PCFGR_0 0x100f, PCFGR_1 0x1008, PCFGW_0 0x100f, PCFGW_1 0x1008); {MSDEF}:95 "
  "(`MEMSHIRE_WRITE_CNT_SIZE`, 'one per priority'); external/core-et/rtl/inc/memshire_types.vh (ddrc_esr_ctl_t: "
  f"u0/u1 csysreq_hi/lo); {SCSPEC} pdf p.97 §4.1 (esr_sc_axi_qos: AXI_QOS_MEM_HIGH_PRIORITY / _LOW_PRIORITY)",
  "et-spec", 2, "AXI ports per controller",
  note="Which traffic is steered to which port, and what esr_sc_axi_qos is set to, is not in the sources (ask).")

F("dram.ctl.cam", "controller queues",
  "The controller's transaction store (CAM) gives 32 entries to low-priority reads (SCHED.lpr_num_entries = 0x1f, "
  "'this value + 1'); the total depth, a build parameter, is not in the sources.",
  f"{INIT}:4661 (SCHED 0x00a01f01); {UMCTL} SCHED.lpr_num_entries description",
  "et-spec", 32, "low-priority read entries",
  note="Total CAM depth (MEMC_NO_OF_ENTRY) unknown.")

F("dram.ctl.scheduling", "controller queues",
  "The scheduler serves up to 15 transactions of one kind (high-priority reads, low-priority reads, writes) before "
  "switching when another kind waits; low-priority reads and writes may be starved at most 127 clocks, high-priority "
  "reads 1.",
  f"{INIT}:4665-4667 (PERFHPR1 0x0f000001, PERFLPR1 0x0f00007f, PERFWR1 0x0f00007f)",
  "et-spec", 15, "transactions per run",
  note="Field meanings are the uMCTL2 register names (xact_run_length, max_starve); the scheduler's algorithm itself "
       "is Synopsys's and GENERIC here.")

F("dram.ctl.atomic-unit", "memory shire",
  "The memory shire contains an atomic unit with a small atomic cache (ms_atomic_sm_ctl bits 7:4 flag which entries "
  "hold dirty data; a 4-bit state), and the datasheet lists 'LPDDR4X support for global atomic operations'.",
  f"{PRM} pdf p.514 Table 15-90 (ms_atomic_sm_ctl); {MSDEF}:121 (`MEMSHIRE_ATOMIC_STATE_SIZE 4`), :268-271 "
  f"(memshire atomics); {DS} pdf p.30 §7.1",
  "et-spec", 4, "atomic-cache entries (bits 7:4)",
  note="When a global atomic on a DRAM address is done here rather than at the L3 home is not documented (ask).")

F("dram.ctl.registers-sp-only", "observability",
  "The memory-shire and DDR-controller registers are reachable only by the service processor.",
  f"{PRM} pdf p.512 §15.4.3.1; {CAD}:346",
  "et-spec")

F("dram.ctl.perfmon", "observability",
  "Each memory shire has a perf monitor (40-bit cycle counter at 933 MHz and two event counters). The firmware sets "
  "them to count mesh reads and writes, which a user kernel can sample through syscall 10; the same monitor can count "
  "controller commands (activate, precharge, refresh, per bank), but only M-mode can select that and the encodings "
  "are in a document not in the sources.",
  f"{CAD}:381-418 (§3.5); {MSDEF}:215-250 (MCOP qualifier: cmd bits 14:0, bank bits 27:20; MESHCNT qualifier)",
  "et-spec", page_link=ANAT + "#what-the-chip-lets-you-see",
  note="Hub rungs 13-14 and the missing 'Memory Shire Specification §5.4.22-29'.")

# ---------------------------------------------------------------- latency (measured)
F("dram.lat.typical", "latency",
  "A typical DRAM load, timed one at a time: 299 cycles (500 ns at 600 MHz), the median of 4,500 loads from shire 0 "
  "to random lines; 299 in each of 15 passes on three cards.",
  "docs/reports/2026-09-19-et-soc1-memory-anatomy.html headline tile 'A DRAM load, typical' (19 Sep: 4,500 loads; "
  "26 Sep: 15 passes on three cards)",
  "et-measured", 299, "cycles", card=C3, page_link=ANAT)

F("dram.lat.chase", "latency",
  "A DRAM pointer chase: 296.6-297.1 cycles from shires 0 and 31, 287.2-288.8 from shires 7 and 24 (479-495 ns at "
  "600 MHz), in every pass on every card.",
  f"{V3}/lat.json items[LAT-M2].per_card.<card>.passes[].DRAM; {CL}, row 'L3 and DRAM latency by requesting shire' "
  "(E36)",
  "et-measured", 297, "cycles", card=C3, page_link=MH,
  note="About 490 ns, a fifth more than an A100's HBM (405 ns).")

F("dram.lat.clock-scaling", "latency",
  "At 800 MHz the chase reads 352-368 cycles (440-460 ns): the mesh and DDR parts do not scale with the minion clock; "
  "fitted, a DRAM load is 86.3 minion cycles + 344.8 ns.",
  f"{CL}, rows 'DRAM' and 'Latency models' (E33)",
  "et-measured", 344.8, "ns (clock-independent part)", card="aifoundry2", page_link=MH)

F("dram.lat.model", "latency",
  "Whole DRAM load = 110 + 12 x hops(requester -> L3 home) + 91 + 12 x hops(L3 home -> memory shire) cycles; left as "
  "fitted on aifoundry2, within +-3 cycles for 97.0% of lines on aifoundry2, 92.9% on aifoundry3, 94.4% on "
  "aifoundry1-c1.",
  f"anatomy page §4 (formula); {CL}, row 'DRAM latency against the 19 September model' (E35, {V3}/mem.json MEM-P2)",
  "et-measured", 91, "cycles (memory-shire leg constant)", card=C3,
  page_link=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop",
  note="Refitted pass by pass the constant reads 90-91 on all three cards "
       "(docs/reports/data/2026-09-26-memprobe-3cards/cards.json ms_const).")

F("dram.lat.ms-hops", "latency",
  "With the memory shires one hop outside the grid, the memory shire's position adds 12-84 cycles (1-7 hops from the "
  "L3 home, 2.6 on average).",
  "docs/reports/data/2026-09-27-chip-diagram/facts.json facts['L44']; anatomy page §1",
  "et-derived", None, "cycles", page_link=ANAT + "#trace-one-load")

F("dram.lat.dram-chip-share", "latency",
  "Of the 91-cycle memory-shire leg (152 ns), about 28 cycles are the DRAM's own timing: the activate (tRCD, 11 "
  "cycles) and the read latency plus two 32-byte bursts (19.3 + 8.6 ns, 17 cycles). At most about 63 cycles "
  "(~105 ns) are the memory shire itself: queues, controller, PHY and clock crossings.",
  "anatomy page §4 ('Of the 91 cycles (152 ns), the DRAM chip itself accounts for about 28'); dram.ctl.tRCD, "
  "dram.ctl.RL-WL, dram.ctl.burst",
  "et-derived", 28, "cycles", page_link=ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop",
  note="'At most' because each hop further out that the memory shires might sit moves 12 cycles from the constant "
       "into the mesh legs.")

F("dram.lat.ms-internal", "latency",
  "How the memory shire's ~63 cycles split between the NoC AXI port and clock crossing, the address strip, the "
  "controller's port, CAM and scheduler, the DFI and the PHY's transmit and receive paths is not known.",
  "none: no memory-shire description is in the sources (hub ask 'ask-memshire', "
  "docs/reports/sources/limits-of-observability.data.json improvements[25])",
  "unknown", 63, "cycles (upper bound, unsplit)")

F("dram.lat.row-hit", "row state",
  "A load that finds its row open skips the activate and saves 11-12 cycles (about 19 ns, tRCD): 215 against 226 "
  "cycles in the refresh series; the two clusters' means were 11.0-11.6 cycles apart on three cards.",
  f"{MP} refresh.open_med = 214, refresh.closed_med = 226, refresh.closed_minus_open = 11.6; anatomy page §5 "
  f"#refresh-caught-in-the-act; {CL}, row 'DRAM refresh and open rows' (E35)",
  "et-measured", 11.6, "cycles", card=C3, page_link=ANAT + "#refresh-caught-in-the-act",
  note="The registered three-card test read 5.3-6.6 cycles because it missed the later build's 7-cycle timer offset; "
       "re-referenced to each pass's own L1 hit it reads 11.0-11.6 (anatomy page, 'Checked on three cards').")

F("dram.lat.row-conflict", "row state",
  "Two loads to the same bank but different rows, issued together: the second pays about +37 cycles (36.9 on "
  "aifoundry2, 37.4 on aifoundry3, 36.5 on aifoundry1-c1; 38.5 on 19 September): it cannot activate its row until "
  "tRC (63.2 ns = 37.9 cycles) after the first activate.",
  f"{V3}/mem.json [item=MEM-P4].per_card.<card>.tests.P4_row_conflict_extra; {CL}, row 'DRAM bank timing (bits)' "
  "(E35); anatomy page §5",
  "et-measured", 36.9, "cycles", card=C3, page_link=ANAT + "#which-address-bits-share-a-row",
  note="The tRC explanation is et-derived: the penalty matches the programmed tRC within a cycle.")

F("dram.lat.row-sequential", "row state",
  "Issued one after the other: a second load to another row of the same bank pays about +9-10 cycles (the precharge, "
  "tRP = 11 cycles), one to the same row saves 11-12, one to another bank costs nothing extra.",
  f"{MP} bits['18'..'29'].b_minus_b0_med = 9, bits['13'..'17'] = -12; {V3}/mem.json MEM-P4 P4_seq_row, P4_seq_col, "
  "P4_seq_bank (+10, -11, 0 on every card)",
  "et-measured", 10, "cycles (other row, same bank)", card=C3, page_link=ANAT + "#which-address-bits-share-a-row")

F("dram.lat.rows-closed", "row state",
  "Every load of the latency decomposition found its row closed: each came 2,600 cycles or more after its row was "
  "last opened, longer than a refresh period; after up to 27 ms idle a DRAM load is 10.5 cycles slower, the row "
  "closure, and no other wake-up cost.",
  f"anatomy page §4 ('Every one of these loads found its row closed'); {CL}, row 'No array wake-up latency' (E18)",
  "et-measured", 10.5, "cycles", card="aifoundry2")

F("dram.lat.refresh-period", "refresh",
  "Folding 19,000 DRAM load times on their timestamps shows refresh every 2,325.4 cycles = 3.876 us on every card "
  "(15 passes); a load that arrives during a refresh waits up to 208 extra cycles (347 ns), and refresh closes the "
  "open row.",
  f"{MP} refresh.period_cycles = 2325.4, refresh.max_wait = 208; {V3}/mem.json [item=MEM-P5].per_card.<card>.tests."
  f"P5_refresh_period, .P5_max_extra; {CL}, row 'DRAM refresh and open rows' (E35)",
  "et-measured", 2325.4, "cycles", card=C3, page_link=ANAT + "#refresh-caught-in-the-act",
  note="Matches the programmed tREFI (3.875 us) to 0.02%. The 208-cycle wait is 347 ns against tRFCab 280.7 ns; the "
       "remaining ~66 ns is not attributed (a precharge-all before the refresh and the re-activate after it are the "
       "GENERIC candidates).")

F("dram.lat.row-life", "row state",
  "A row stays open until a refresh or a conflicting load closes it; no idle timer was seen: in the refresh series "
  "96% of loads with no refresh since the previous one were row hits (3,556 of 3,713, after 450-2,000 idle cycles), "
  "4% across a refresh.",
  "anatomy page §5 #how-long-a-row-stays-open; docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json "
  "refresh.rowlife",
  "et-measured", 96, "% row hits without a refresh between", card=C3, page_link=ANAT + "#how-long-a-row-stays-open")

F("dram.lat.l3-miss", "latency",
  "The DRAM leg starts when the L3 home's cache bank misses: the L3 miss costs 42 shire clocks (idle, excluding NoC and "
  "memory) and the bank sends the read through its 512-bit To_Sys port into the NoC.",
  f"{SCSPEC} pdf p.11 Table 1 ('L3 cache read miss 42 + NoC & Mem latency'), pdf p.8 ('it uses its 512b To_Sys port "
  "into the NoC to make the request to the memory'), pdf p.55 (misses and victims to the to_sys port)",
  "et-spec", 42, "shire clocks")

# ---------------------------------------------------------------- energy
F("dram.e.per-byte", "energy",
  "Reading DRAM costs 114.6 pJ per byte above idle [89.0-141.3 over 18 passes] with 1 KB tensor loads at 600 MHz "
  "(aifoundry2 111.5, aifoundry3 105.6, aifoundry1-c1 126.6): about 7.3 nJ per 64-byte line.",
  f"{MAN} reruns.levels_pj_per_byte['dram'] (mean, lo, hi, per_card); docs/energy-manual/04-bytes-memory.md table "
  "row 'DRAM'",
  "et-measured", 114.6, "pJ/B", card=C3, page_link=EM + "#bytes-through-the-memory-hierarchy")

F("dram.e.data", "energy",
  "Even DRAM is data-dependent: a tensor load from DRAM costs 94.6 pJ/B on zeros [86.2-105.7] and 132.6 on random data "
  "[117.9-145.4]; a tensor store 94.4 and 141.9.",
  f"{MAN} catalogue.combined['tload/dram/zeros'], ['tload/dram/random'], ['tstore/dram/zeros'], "
  "['tstore/dram/random']; docs/energy-manual/04-bytes-memory.md table rows",
  "et-measured", 132.6, "pJ/B (random, tensor load)", card=C3, page_link=EM + "#bytes-through-the-memory-hierarchy",
  note="With read and write DBI on and LVSTL I/O terminated to ground (GENERIC), driving ones costs current and zeros "
       "almost none; that is one plausible share of the gap, not measured separately.")

F("dram.e.writeback", "energy",
  "Stores to DRAM through the L1 write-back path (fsw.ps) cost 341.5 pJ/B on random data at 27 GB/s: each store "
  "allocates its line, so the byte pays a DRAM read and a DRAM write.",
  f"{MAN} catalogue.combined['st_stream/dram/random']; docs/energy-manual/04-bytes-memory.md table row 'fsw.ps stores "
  "to DRAM through the L1'",
  "et-measured", 341.5, "pJ/B", card=C3, page_link=EM)

F("dram.e.store-vs-load", "energy",
  "A tensor store to DRAM is not distinguishable from a tensor load in energy on any card (+8.4, +7.3 and +14.5 pJ/B, "
  "99% intervals all including 0).",
  f"{V3}/cat.json [item=CAT-e].per_card.<card>.tstore_minus_tload; {CL}, row 'A tensor store to DRAM against a tensor "
  "load, random' (E45)",
  "et-measured", 8.4, "pJ/B (aifoundry2)", card=C3)

F("dram.e.unmetered", "energy",
  "About 70% of a DRAM byte's energy lands on no metered rail: a DRAM tensor load splits 2% minion cores, 11% SRAM, "
  "18% mesh, 69% unmetered; the fit of the unmetered remainder puts 72.7 (aifoundry2), 72.7 (aifoundry3) and 81.6 "
  "(aifoundry1-c1) pJ per DRAM byte in the DDR PHY, the I/O rail and the DRAM chips.",
  f"docs/energy-manual/04a-fine-grain.md rail-split table row 'DRAM, tensor load' and unmetered-fit table row 'per "
  f"DRAM byte'; {MAN} unmetered.<card>.coef.dram_pj_per_byte; {CL}, row 'Rail split, DRAM read'",
  "et-measured", 72.7, "pJ/B off-rail", card=C3, page_link=LOO + "#the-unmetered-remainder-attributed")

F("dram.e.split-unknown", "energy",
  "How the ~73 pJ/B off-rail DRAM energy splits between the memory shires' logic, the PHY's I/O, the DRAM core "
  "(activate, sensing, column path) and the DRAM's own I/O is not measurable on the card: none of those rails has a "
  "current sensor.",
  "docs/findings/19-observability-and-the-unmetered.md ('The other rails — DDR core 0.8 V, VDDQ 1.1 V, VDDQLP ... have "
  "set points in the PMIC and no telemetry'); docs/research/power-telemetry.md:47-52, 255",
  "unknown", page_link=LOO + "#the-unmetered-remainder-attributed")

F("dram.e.rows", "energy",
  "The DRAM row pattern does not change the energy per byte: row hits 155.9, row misses 158.5, sequential 156.4 pJ/B "
  "on random data (120.4 / 118.5 / 120.6 on zeros), indistinguishable on every card; an activation costing 30 pJ/B on "
  "zeros or 50 on random data would have shown.",
  f"{MAN} catalogue.combined['dramrow2/rowhit/random'], ['dramrow2/rowmiss/random'], ['dramrow2/seq/random'] (and "
  f"/zeros); docs/energy-manual/04a-fine-grain.md '## Rows: does the DRAM row pattern matter?'; {CL}, row 'DRAM row "
  "walks (seq, rowhit, rowmiss) over a DRAM tensor load' (E45)",
  "et-measured", 158.5, "pJ/B (row miss, random)", card=C3, page_link=EM + "#finer-grain-wires-lines-rows-and-the-leakage-of-the-arrays",
  note="The manual's caveat: with 32 streams interleaved and a refresh every 2,325 cycles, every pattern may have paid "
       "an activation; so the activate energy is bounded, not measured. Per 64-byte line the bound is ~1.9 nJ (zeros) "
       "to ~3.2 nJ (random).")

F("dram.e.gather", "energy",
  "A random 4-byte element gathered from DRAM costs 9.8 nJ (a whole line fetched for 4 bytes), at 1.19 G elements/s "
  "chip-wide; a scatter into DRAM 23.8 nJ at 0.42 G/s.",
  "docs/energy-manual/04-bytes-memory.md table rows 'DRAM' (gathers and scatters); "
  f"{V3}/gs.json items['GS-RATE'].pooled",
  "et-measured", 9.8, "nJ per element", card=C3, page_link=EM)

F("dram.e.vs-scp", "energy",
  "DRAM is 30x the energy of the shire's own scratchpad per byte read and 17x per byte written; relaying a result "
  "through DRAM costs 12.9-13.1x handing it to the next shire.",
  f"docs/energy-manual/04-bytes-memory.md ('DRAM is 30x the energy ...'); {CL}, row 'The relay (V3)' (E29)",
  "et-derived", 30, "x", card=C3, page_link=RELAY)

# ---------------------------------------------------------------- rails
F("dram.pwr.rails", "power",
  "Three card rails serve the memory path: VDD_DDR (the memory shires, 0.8 V set point, 875 mV in the card's power-tree "
  "figure), VDD_QLP (the LPDDR4X I/O VDDQ; 640 mV set point read on aifoundry2, 620 mV in the figure) and VDD_Q (1.1 V: "
  "the LPDDR4X's VDDQ/VDD2 core supply, as the figure labels it). None reports current.",
  "docs/research/power-telemetry.md:47-52 (from the power-tree images, "
  f"{CARD} pdf pp.2-4); docs/reports/data/2026-09-20-power-aifoundry2/horace2-telemetry.jsonl fields reg_mv.ddr = "
  "800, reg_mv.vddqlp = 640, reg_mv.vddq = 1100",
  "et-spec", 0.8, "V (VDD_DDR)", card="aifoundry2",
  note="JEDEC LPDDR4X (GENERIC): VDD1 1.8 V, VDD2 1.1 V, VDDQ 0.6 V. Which card rail feeds the DRAM's VDD1 is not in "
       "the sources.")

F("dram.pwr.droop", "power",
  "The memory shires' own voltage monitors read the 0.8 V DDR rail at 767-768 mV at idle, and it droops 0.86-1.01 mV "
  "per watt of off-rail DRAM power (1 mV ~ 1.2 W of DRAM): a proxy DRAM meter, refreshed every service-processor pass.",
  f"{CL}, row 'DDR rail droop per off-rail DRAM watt' (E30, E46); docs/energy-manual/04a-fine-grain.md 'A droop meter "
  "for DRAM'; horace2-telemetry.jsonl die_mv.ddr",
  "et-measured", 0.87, "mV per W", card=C3, page_link=LOO + "#the-unmetered-remainder-attributed")

# ---------------------------------------------------------------- GENERIC circuit facts (JEDEC / textbook)
F("gen.cell", "circuit",
  "A DRAM bit is one 1T1C cell: an NMOS access transistor whose gate is the wordline and whose drain is the bitline, "
  "in series with a storage capacitor; the stored charge is the bit, it leaks away (hence refresh), and reading it is "
  "destructive until the sense amplifier restores it.",
  "GENERIC (textbook DRAM; no ET source describes the die)", "generic")

F("gen.equalize", "circuit",
  "Between accesses each bitline pair is held at half the array voltage by a precharge/equalize circuit (typically "
  "three NMOS: two tie BL and /BL to the half-voltage, one shorts them together); the equalize signal turns off just "
  "before a wordline rises.",
  "GENERIC (textbook DRAM)", "generic")

F("gen.wordline", "circuit",
  "Activate: the row address is decoded, and the selected (sub-)wordline driver pulls its wordline up to a boosted "
  "voltage above the array voltage, so every access NMOS on that row turns fully on and passes a full level.",
  "GENERIC (textbook DRAM)", "generic")

F("gen.sense", "circuit",
  "Each cell shares its charge with its bitline, nudging it slightly above or below the half-voltage; the bitline "
  "sense amplifier, a cross-coupled latch of two NMOS and two PMOS, is then fired (NMOS side pulled to ground, PMOS "
  "side to the array voltage) and drives the pair to full rail, which also rewrites the cell. The row of latched sense "
  "amplifiers is the open page ('row buffer').",
  "GENERIC (textbook DRAM)", "generic",
  note="On the ET-SoC-1's channels one activate latches 16,384 bits (dram.org.geometry).")

F("gen.column", "circuit",
  "Read: the column decoder raises a column-select line, turning on column-select NMOS pairs that connect the chosen "
  "sense amplifiers to local and then global I/O lines, where secondary sense amplifiers pick up the data; LPDDR4 "
  "fetches 16 bits per DQ per READ (16n prefetch), 256 bits for a x16 channel, and serialises them 16:1 onto each pin.",
  "GENERIC (JEDEC JESD209-4 LPDDR4 16n prefetch; array circuit textbook)", "generic", 256, "bits per READ per channel")

F("gen.io", "circuit",
  "LPDDR4X signals use LVSTL: each DQ driver pulls up to a 0.6 V VDDQ or down to ground, and the receiver terminates "
  "to ground, so a driven 1 draws current through the termination and a 0 almost none; DBI inverts a byte that holds "
  "more than four ones. (LPDDR4's LVSTL pull-up is usually an NMOS, N-over-N; the transistor choice is the vendor's.)",
  "GENERIC (JEDEC LPDDR4/LPDDR4X)", "generic", 0.6, "V (VDDQ, LPDDR4X)",
  note="ET has read and write DBI on (dram.ctl.dbi); the card's VDD_QLP set point is 620-640 mV (dram.pwr.rails).")

F("gen.precharge", "circuit",
  "Precharge: the wordline falls (access transistors off, the restored cells isolated), the sense amplifiers are "
  "disabled and the equalizers turn back on, returning every bitline pair to the half-voltage for the next activate.",
  "GENERIC (textbook DRAM)", "generic")

F("gen.commands", "protocol",
  "LPDDR4 commands travel on a 6-bit single-data-rate command/address bus: an ACTIVATE is two 2-clock parts (ACT-1, "
  "ACT-2), a READ or WRITE is RD-1/WR-1 plus CAS-2 (4 clocks), a PRECHARGE 2 clocks.",
  "GENERIC (JEDEC JESD209-4)", "generic")

F("gen.refresh", "circuit",
  "All-bank refresh: the die's internal counter supplies the row addresses and each REFab activates and precharges a "
  "batch of rows in every bank at once; JEDEC LPDDR4 asks for 8,192 refresh commands per 32 ms retention window at "
  "normal temperature, which with 131,072 rows per bank means 16 rows of each bank per REFab.",
  "GENERIC (JEDEC JESD209-4 tREFW 32 ms, 8,192 REF); rows per bank from dram.org.geometry",
  "generic", 16, "rows per bank per REFab",
  note="ET's tREFI 3.875 us is slightly shorter than JEDEC's 3.904 us, so 8,192 refreshes take 31.7 ms.")

F("gen.temp-refresh", "refresh",
  "LPDDR4 needs refresh 2x or 4x as often above 85 C, signalled in its MR4 register. The ET firmware leaves derating "
  "off, so refresh stays at 3.875 us whatever the DRAM temperature; nothing in the sources reads the DRAM's "
  "temperature.",
  f"GENERIC (JEDEC JESD209-4 MR4 refresh-rate field); {INIT}:4686-4688 (DERATEEN commented out)",
  "generic",
  note="Whether the packages stay under 85 C under load is an ask; the die itself idles at 72 C and reaches 80-90 C "
       "under load on these cards.")

F("gen.jedec-match", "DRAM timing",
  "The programmed timings sit at JEDEC LPDDR4 minimums for a 16 Gb-per-channel die at 3,733 MT/s: tRCD and tRPpb "
  "18 ns, tRAS 42 ns, tRRD 10 ns, tFAW 40 ns, tRFCab 280 ns, RL 36 with read DBI, WL 16, nWR 34, tREFI 3.9 us.",
  "GENERIC comparison: values quoted from JEDEC JESD209-4 from memory of the standard, not from an ET source; "
  "ET values from dram.ctl.*",
  "generic",
  note="tRFCab = 280 ns is the JEDEC value for 12-16 Gb per channel, a cross-check on the die density.")

# ---------------------------------------------------------------- store and refill paths
F("dram.store.path", "store",
  "A store reaches DRAM only when its dirty line leaves the L3: the L3 bank sends the victim as a write through its "
  "To_Sys port to the memory shire PA[8:6] names; the controller queues it in its write store and drains writes in runs "
  "of up to 15.",
  f"{SCSPEC} pdf p.8 (L3 evicts via To_Sys), p.55 (misses and victims to the to_sys port), pp.79-83 (Flush/"
  f"FlushToMem); {INIT}:4667 (PERFWR1)",
  "et-spec")

F("dram.refill.path", "refill",
  "The line comes back the way the request went: the memory shire answers the L3 home over the mesh, the L3 installs "
  "it and returns it to the requester; the latency model counts 12 cycles per hop on both legs.",
  f"{SCSPEC} pdf p.54-55 (misses to to_sys; data returned and installed), p.8; anatomy page §4 (model)",
  "et-spec", page_link=ANAT + "#trace-one-load")

# ---------------------------------------------------------------- access sequences
seq = []


def S(seqname, step, block, action, kind, source, latency=None, energy=None, circuit=None, note=None):
    d = dict(id=f"dram.seq.{seqname}.{step:02d}", level="DRAM", topic=f"access sequence: {seqname}",
             statement=action, value=latency, unit=None, source=source, kind=kind, card=None, page_link=None,
             note=note, seq=seqname, step=step, block=block, latency=latency, energy=energy,
             circuit=circuit or [])
    facts.append(d)


def C(what, kind):
    return {"what": what, "kind": kind}


# A load, the common case: row closed (refresh closed it), as every load of the decomposition found it.
S("load", 1, "L3 home shire: shire-cache bank (L3 slave reqq, To_Sys master port)",
  "The L3 home misses and sends a 64-byte read with its QoS over the 512-bit To_Sys port.",
  "et-spec", f"{SCSPEC} pdf p.8, p.11 Table 1, p.97 (esr_sc_axi_qos)",
  latency="42 shire clocks L3-miss handling (idle, spec)",
  circuit=[C("SRAM tag lookup and request-queue flops: belongs to the L3 diagram", "generic")])
S("load", 2, "Mesh (NoC, 400 MHz): L3 home -> memory shire PA[8:6]",
  "The request crosses 1-7 mesh hops to the memory shire that PA[8:6] names.",
  "et-measured", "dram.lat.model, dram.lat.ms-hops; anatomy page §4",
  latency="12 cycles per hop, round trip (both directions counted here)",
  circuit=[C("router flops and repeated wires: belongs to the mesh diagram", "generic")])
S("load", 3, "Memory shire: 512-bit NoC AXI slave port, clock crossing, address strip",
  "The memory shire accepts the read, crosses from the mesh clock into its own domain, uses PA[9] to pick controller "
  "u0 or u1 (the channel) and strips PA[9:6] from the address.",
  "et-spec", f"{DS} pdf p.30 §7.1.1.1; external/et-platform/etsoc-hal/include/hwinc/ms_regs.h:160 (ms_mem_ctl "
  f"reset); {MSDEF}:21-22; clock crossing: anatomy page §4 ('the crossings between the 933 MHz DDR clock and the mesh')",
  latency="part of the memory shire's <=63 cycles; split unknown",
  note="Where inside the memory shire the clock crossing sits, and whether its logic runs at 933 MHz, is inferred, "
       "not documented.",
  circuit=[C("synchroniser flip-flops and FIFO SRAM/flops at the clock crossing", "generic"),
           C("a 2:1 steering mux on PA[9]", "et-derived")])
S("load", 4, "uMCTL2 controller: AXI port (high or low priority), address map, read CAM, scheduler",
  "The controller maps the address to bank PA[12:10], row PA[34:18], columns PA[17:13] and PA[5:1], queues the read "
  "and finds the bank closed (open-page policy, but the last refresh closed it).",
  "et-spec", f"{INIT}:4639-4680 (ADDRMAP, SCHED, PCFGR/W); dram.addr.pa-map",
  latency="part of the memory shire's <=63 cycles",
  circuit=[C("standard-cell comparators in the CAM match bank and row against open pages", "generic")])
S("load", 5, "DFI -> PHY command path -> 6-bit CA bus",
  "The controller issues ACTIVATE (ACT-1, ACT-2) with bank and row; the PHY drives it onto the channel's CA pins at "
  "1,866 MHz.",
  "et-spec", f"{INIT}:4536 (lpddr4=1), dram.ctl.clock; gen.commands",
  latency="4 DRAM clocks on the bus (2.1 ns)",
  circuit=[C("PHY CA drivers (LVSTL pull-up/pull-down) switch", "generic"),
           C("DRAM CA receivers and command decoder latch ACT", "generic")])
S("load", 6, "DRAM die, bank PA[12:10]: row decoder and wordline driver",
  "The bank's equalizers let go of the bitlines and the selected wordline rises to its boosted level: 16,384 access "
  "transistors (one 2 KB page) turn on.",
  "generic", "gen.equalize, gen.wordline; dram.org.geometry (16,384 bits)",
  circuit=[C("bitline equalize/precharge NMOS turn off", "generic"),
           C("row-decoder gates select one row of 131,072", "generic"),
           C("sub-wordline driver PMOS pulls the wordline to the boosted voltage", "generic"),
           C("16,384 cell access NMOS turn on; each cell capacitor shares charge with its bitline", "generic")])
S("load", 7, "DRAM die: bitline sense amplifiers",
  "The sense amplifiers fire and latch the whole row, restoring every cell; the bank is open once tRCD has passed.",
  "et-spec", "dram.ctl.tRCD; gen.sense", latency="tRCD 18.2 ns = 11 cycles (measured: a row hit saves 11-12)",
  circuit=[C("NMOS-side enable (sense-amp sink) pulls low, then PMOS-side enable (source) pulls high", "generic"),
           C("16,384 cross-coupled latches (2 NMOS + 2 PMOS each) resolve to full rail and rewrite the cells", "generic")])
S("load", 8, "DFI -> CA bus: READ #1, then READ #2 one tCCD later",
  "Two READs (RD-1 + CAS-2 each) fetch the line's two 32-byte halves from the open row: same columns PA[17:13], "
  "PA[5] = 0 then 1.",
  "et-spec", "dram.ctl.burst, dram.addr.pa-map; gen.commands", latency="tCCD 4.3 ns between the two READs",
  circuit=[C("column decoder raises a column-select line for each READ", "generic"),
           C("column-select NMOS pairs connect 256 sense amplifiers to local then global I/O lines", "generic"),
           C("secondary (I/O) sense amplifiers and a 16:1 serialiser per DQ load the prefetch", "generic")])
S("load", 9, "DRAM DQ drivers -> 16 DQ pins + DQS -> PHY receivers",
  "After the read latency the DRAM drives two BL16 bursts, 32 bytes each, at 3,733 MT/s with read DBI; the PHY's "
  "trained receivers capture them on the strobe.",
  "et-spec", "dram.ctl.RL-WL, dram.ctl.burst, dram.ctl.dbi; gen.io",
  latency="RL 19.3 ns + 2 x 4.3 ns bursts = 17 cycles",
  circuit=[C("DRAM LVSTL output drivers pull each DQ up to VDDQ (~0.6 V) or down to ground, per bit per beat", "generic"),
           C("DBI logic inverts a byte with more than four ones", "generic"),
           C("PHY DQS-gated receivers (VREF comparators), deserialiser, read FIFO", "generic")])
S("load", 10, "PHY -> DFI -> controller -> memory-shire AXI read response",
  "The line goes back through the controller and the memory shire's clock crossing onto the 512-bit NoC port. The row "
  "stays open: no precharge follows (open page, no auto-precharge).",
  "et-spec", "dram.ctl.page-policy; dram.topo.noc-port",
  latency="rest of the memory shire's <=63 cycles; the whole memory-shire leg is 91 cycles + 12 per hop",
  circuit=[C("the open row's sense amplifiers keep holding the page (they draw no column current until the next READ)",
             "generic")])
S("load", 11, "Mesh: memory shire -> L3 home -> requester",
  "The response returns to the L3 home, which installs the line and forwards it to the requesting shire.",
  "et-measured", "dram.refill.path; dram.lat.model",
  latency="whole load ~297-299 cycles (~490-500 ns); DRAM chip ~28 of them",
  energy="114.6 pJ/B above idle, ~7.3 nJ per 64-byte line; ~70% off the metered rails (dram.e.per-byte, dram.e.unmetered)")

# Variants
S("row-hit", 1, "uMCTL2 scheduler + DRAM column path",
  "If the row is still open (no refresh and no other row of the bank since), the controller skips steps 5-7 and issues "
  "the READs at once.",
  "et-measured", "dram.lat.row-hit, dram.lat.row-life", latency="-11 to -12 cycles against a closed row",
  circuit=[C("no wordline, bitline or sense-amplifier switching; only the column path of steps 8-9", "generic")])
S("row-conflict", 1, "uMCTL2 scheduler: PRECHARGE, then ACTIVATE",
  "If another row of the bank is open, the controller first precharges it, then activates the new row; an ACT to the "
  "same bank cannot follow the previous ACT sooner than tRC.",
  "et-measured", "dram.lat.row-conflict, dram.lat.row-sequential, dram.ctl.tRP, dram.ctl.tRAS-tRC",
  latency="+9-10 cycles issued after (tRP), +37 cycles issued together (tRC 63.2 ns)",
  energy="not separable from a row hit: row hits and misses cost the same per byte within +-5 pJ/B (dram.e.rows)",
  circuit=[C("wordline driver NMOS pulls the old wordline down: its 16,384 access NMOS turn off", "generic"),
           C("sense-amplifier enables release; equalize/precharge NMOS turn on, bitlines return to half-voltage",
             "generic"),
           C("then steps 6-7 for the new row", "generic")])

# A store (a dirty line written back)
S("store", 1, "L3 home: victim or flush -> To_Sys write",
  "A dirty line leaves the L3 (eviction, flush to memory, or a tensor store that bypasses the caches) as a 64-byte "
  "write to the memory shire PA[8:6] names.",
  "et-spec", f"{SCSPEC} pdf p.8, pp.79-83; dram.store.path",
  note="A store through the L1 (fsw.ps) first reads its line from DRAM: that byte pays a read and a write.")
S("store", 2, "Memory shire + uMCTL2 write store",
  "The write is queued with its data; the scheduler drains writes in runs of up to 15 and pays read/write turnarounds.",
  "et-spec", f"{INIT}:4665-4667, :4425 (rd2wr, wr2rd)")
S("store", 3, "DFI -> PHY -> CA + DQ: (ACT if closed), WRITE",
  "WRITE (WR-1 + CAS-2); 16 DRAM clocks later the PHY drives 32 bytes on DQ with write DBI and data mask available.",
  "et-spec", "dram.ctl.RL-WL, dram.ctl.dbi", latency="WL 8.6 ns, 4.3 ns per burst",
  circuit=[C("PHY LVSTL DQ drivers switch per bit per beat", "generic"),
           C("DRAM DQ receivers and 1:16 deserialiser", "generic")])
S("store", 4, "DRAM die: write drivers -> column-select -> sense amplifiers -> cells",
  "The DRAM's write drivers overpower the selected sense amplifiers through the column-select transistors; the latches "
  "flip and, through the still-open access transistors, charge or discharge the cell capacitors.",
  "generic", "gen.column, gen.sense", latency="write recovery nWR 34 DRAM clocks (18.2 ns) before any precharge",
  circuit=[C("global/local I/O write drivers (strong CMOS) drive the I/O lines", "generic"),
           C("column-select NMOS pairs on; sense-amplifier latches forced to the new value", "generic"),
           C("cell access NMOS (wordline still high) pass the new level into each capacitor", "generic")])
S("store", 5, "Measured cost",
  "Tensor stores to DRAM run at 76 GB/s and cost 94.4 pJ/B on zeros, 141.9 on random data, indistinguishable from "
  "tensor loads; stores through the L1 cost 341.5 pJ/B at 27 GB/s.",
  "et-measured", "dram.e.data, dram.e.store-vs-load, dram.e.writeback")

# A refresh
S("refresh", 1, "uMCTL2 refresh timer",
  "Every tREFI (3,616 DFI clocks = 3.875 us) the controller closes the channel's open rows and issues an all-bank "
  "REFRESH; no per-bank refresh and no temperature derating.",
  "et-spec", "dram.ctl.refresh-mode", latency="measured period 2,325.4 cycles = 3.876 us on every card")
S("refresh", 2, "DRAM die: internal refresh counter, all 8 banks",
  "The die activates and precharges a batch of rows in every bank (about 16 per bank per REFab for this density), "
  "with no column access: the same wordline, charge-sharing, sense and restore, and precharge switching as an "
  "activate, times the batch.",
  "generic", "gen.refresh; dram.ctl.refresh-mode", latency="tRFCab 280.7 ns",
  circuit=[C("wordline drivers of the refreshed rows rise and fall", "generic"),
           C("all sense amplifiers of each refreshed bank fire and restore, then equalize", "generic")])
S("refresh", 3, "Effect on loads",
  "A load that meets the refresh waits up to 208 cycles (347 ns); 7.2% of random-phase loads do; the next load after "
  "it finds its row closed and pays an activate (+11-12 cycles).",
  "et-measured", "dram.lat.refresh-period, dram.ctl.refresh-duty, dram.lat.row-hit")
S("refresh", 4, "Energy",
  "Refresh energy is part of the idle power, which the card's meters do not split; it is not measured.",
  "unknown", "dram.e.split-unknown; dram.ctl.power-down")

json.dump(facts, open(OUT, "w"), indent=1, ensure_ascii=False)
kinds = {}
for f in facts:
    kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
print(OUT, len(facts), kinds)
