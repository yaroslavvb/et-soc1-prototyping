#!/usr/bin/env python3
"""Build facts-l3.json: the L3 level of 'Anatomy of a memory access', down to the circuit.

Paths in `source` are relative to one of these roots (named in meta.roots):
  repo:   the repository root                        (docs/..., workloads/...)
  ext:    the et-soc1-prototyping checkout's external/   (external/...)
PDF pages are pdf page numbers (pdftotext page breaks), not printed page numbers.
"""
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facts-l3.json")
SS = "https://spacesheep.dev/@yaroslavvb/"
ANAT = SS + "et-soc1-memory-anatomy"
HIER = SS + "et-soc1-memory-hierarchy"
MAN = SS + "et-soc1-energy-manual"
NOC = SS + "et-soc1-on-chip-communication"
HPM = SS + "et-soc1-heat-per-mm"
HOT = SS + "et-soc1-hot-line"
PT = SS + "et-soc1-power-temperature"
LOO = SS + "et-soc1-limits-of-observability"
RIDGE = SS + "et-soc1-ridge-points"

SCS = "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf"
MSD = "external/core-et/docs/CORE-ET Minion Shire Description.pdf"
DS = "external/et-man/ET Preliminary Datasheet Rev 1.0.pdf"
ERR = "external/et-man/ET-SoC Errata.pdf"
CEM = "external/core-et-main/hw/ip/shirecache/rtl/"
CLAIMS = "docs/findings/05-claims.md"
CARDS3 = "aifoundry2, aifoundry3, aifoundry1-c1"

F = []


def fact(id, topic, statement, value, unit, source, kind, card=None, page_link=None, note=None):
    assert kind in ("et-spec", "et-measured", "et-derived", "generic", "unknown"), kind
    F.append(dict(id=id, level="L3", topic=topic, statement=statement, value=value, unit=unit,
                  source=source, kind=kind, card=card, page_link=page_link, note=note))


# ---------------------------------------------------------------- what the L3 is
fact("l3.what", "organisation",
     "The L3 is memory-side and distributed: each of the 32 compute shires gives a 1 MB slice of its 4 MB shire cache "
     "to a chip-wide L3 of 32 MB. The datasheet calls all 140 MB of on-die storage SRAM, each 1 MB block usable as L2, "
     "a slice of the L3, or scratchpad.",
     32, "MB",
     f"{DS} pdf p.4 §1 (external/et-man/txt/ET Preliminary Datasheet Rev 1.0.txt:96-98) and pdf p.13 §2.1.3.1 (txt:564-571); "
     "docs/reports/data/2026-09-22-cards/driver_config.json `l3_kb` 32768 on every card",
     "et-spec", None, HIER + "#the-hierarchy-as-a-spec-sheet")

fact("l3.homes", "organisation",
     "Only the 32 compute shires are homes of the chip-wide L3: the home field is 5 bits (PA[10:6]) for a 32-shire "
     "configuration, so no line of the 32 MB L3 lives in the master, spare, PCIe or I/O shire (the I/O shire's own "
     "L2/L3 cache serves its Maxions).",
     32, "slices",
     f"{SCS} pdf p.26 §1.4.2.3 ('For a 32-Shire SoC, there are five ShireID bits ... bits [10:6]'); {CEM}shirecache_pkg.sv:142-143 (L3Shires 32)",
     "et-spec", None, HIER + "#the-hierarchy-as-a-spec-sheet")

fact("l3.partition-m0", "organisation",
     "The cards run cache mode M0: in every sub-bank, RAM sets 0-639 are scratchpad, 640-767 L2 and 768-1023 (base "
     "0x300, 256 sets, set mask 0xFF) the L3. The chip comes out of reset in M0 and the firmware computes the L3 base as "
     "scratchpad size + L2 size.",
     256, "sets per sub-bank",
     f"{SCS} pdf p.21-22 Tables 6-7 ('The chip will come out of reset in mode M0'); "
     "external/core-et/rtl/shire/esr/esr_cache_bank.v:104-113 (reset defaults: L3 base 24/32, size 8/32 of the sets for a 4 MB build); "
     "external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/bl2_cache_control.c:712-721; "
     "docs/reports/data/2026-09-22-cards/driver_config.json (l2_kb 16384, l3_kb 32768, scp_kb 81920: M0)",
     "et-spec", None, HIER + "#the-hierarchy-as-a-spec-sheet")

fact("l3.slice-arith", "organisation",
     "One slice = 4 banks x 4 sub-banks x 256 sets x 4 ways x 64 B = 1 MB (16,384 lines per shire, 4,096 per bank).",
     1048576, "bytes",
     f"arithmetic on {SCS} pdf p.20 Table 4 and pdf p.22 Table 7 (M0 L3: 256 sets per sub-bank)",
     "et-derived", None, None)

fact("l3.same-arrays", "storage",
     "The L3 is not a separate memory. It is the top quarter of the same arrays that hold the L2 and the scratchpad: in "
     "each data macro (4,096 words) the L3 lines are words 3,072-4,095 (address {set 768-1023, way}); in each tag and "
     "tag-state macro (1,024 rows) rows 768-1023. Per shire that is a quarter of 64 data, 16 tag and 16 tag-state macros.",
     0.25, "fraction of each macro",
     f"{SCS} pdf p.22 Table 7 (L3 base 0x300, end 0x3FF), pdf p.51 (macro sizes); {CEM}shirecache_pipe_sub_bank.sv:1613 "
     "(data RAM address = {pipe_set, tag_ram_hit_way}); "
     f"{CEM}shirecache_pipe.sv:1010 (one tag, tag-state and data RAM wrapper per sub-bank); {CEM}shirecache_pipe_data_ram_wrap.sv:83-107 (four quadword RAMs)",
     "et-derived", None, None,
     "Macro counts: 4 banks x 4 sub-banks x (1 tag + 1 tag-state + 4 data). The I-cache macro (mbi) and the dataq (mbq) are separate.")

# ---------------------------------------------------------------- address decode
fact("l3.decode", "address map",
     "L3 address decode (default swizzle0): offset PA[5:0], home shire PA[10:6], bank PA[12:11], sub-bank PA[14:13], set "
     "from PA[15] up (PA[22:15] for M0's 256 sets), 23-bit tag stored from PA[17] up. Consecutive 64 B lines rotate over "
     "the 32 homes; lines 2 KB apart change bank, 8 KB apart sub-bank.",
     None, None,
     f"{SCS} pdf p.24 §1.4.1.2 and pdf p.27 Table 8 (swizzle0); {CEM}shirecache_pkg.sv:104-112; "
     "external/core-et/rtl/shire/esr/esr_cache_bank.v:84-103 (swizzle reset = mode 0); docs/research/counters-and-dram.md:373-377 "
     "(sc_l3_shire_swizzle_ctl left at reset)",
     "et-spec", None, ANAT + "#trace-one-load")

fact("l3.home-measured", "address map",
     "The home-by-PA[10:6] rule holds on silicon: 1,498 of 1,500 random lines timed from shire 0 fall within 4 cycles of "
     "110 + 12 x hops(requester, PA[10:6]) (aifoundry2, 19 Sep), and 99.4-99.97% of lines on each of three cards (26 Sep).",
     1498, "of 1,500 lines",
     "workloads/memprobe/report_template.html:875-880; docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.l3_model_off (2); "
     f"{CLAIMS}:415 (V3R/mem.json [item=MEM-P1].per_card.<card>.tests.P1_l3_within4_frac)",
     "et-measured", CARDS3, ANAT + "#l3-110-cycles-plus-12-per-hop")

fact("l3.alias", "address map",
     "Default two-shire aliasing: the tag stores PA[10] (the home ID's top bit) in its lowest bit, so a dead shire's L3 "
     "lines can be redirected to the shire 16 IDs away and still be told apart. All-shire aliasing stores PA[10:6]; the "
     "firmware sets it only when reconfiguring the NoC for 8 or fewer shires.",
     None, None,
     f"{SCS} pdf p.25-26 §1.4.2.1-1.4.2.3; external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/noc_configuration.c:316-343",
     "et-spec", None, None)

# ---------------------------------------------------------------- the storage circuit
fact("l3.geometry", "storage",
     "Every sub-bank holds a tag RAM of 1,024 x 116 bits (4 ways x (23-bit tag + 6 ECC bits)), a tag-state RAM of "
     "1,024 x 40 (4 ways x {valid, locked, zero, qwen[3:0]} + 5-bit LRU code + 7 ECC bits) and four data RAMs of "
     "4,096 x 144 (128 data + 16 ECC bits: 8 per 64-bit doubleword). 4-way set-associative, 64 B lines, write-back, "
     "write-allocate, LRU.",
     None, None,
     f"{SCS} pdf p.8-9 §1.1, pdf p.47 §2.14.2-2.14.3 (Table 12), pdf p.48-49 §2.14.5-2.14.6.2, pdf p.51; {CEM}shirecache_pkg.sv:61-79",
     "et-spec", None, None,
     "The spec's feature list (pdf p.9) says 7 ECC bits per 33-bit tag and 6 per 33 bits of state; its storage chapter "
     "(pdf p.47-49) and the macro widths 116 and 40 say 6 per 23-bit tag and 7 per 33 bits of state. The macro widths "
     "decide it.")

fact("l3.macros", "storage",
     "The cache RAMs are compiled macros bought from a third party: tag-state mbs = saculs0g4l2p1024x40m4b1w0c0p0d0s1rm0rw11 "
     "(type '2PUHDRF', two-port), tag mbt = saduls0g4l1p1024x116m4b1w0c0p0d0s1rm0sdrw11 and data mbd = "
     "saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11 (type '1PUHD', single-port). The spec calls the data array 'SRAM memory "
     "panels'.",
     None, None,
     f"{SCS} pdf p.48 §2.14.5 ('SRAM memory panels that are 144 bits wide') and §2.14.6.1 ('Intellectual Property (IP) acquired from a third party vendor'), pdf p.51 §2.14.6.4",
     "et-spec", None, None,
     "Reading '1PUHD' as single-port ultra-high-density and 'm4'/'b4' as column mux 4 and 4 internal banks follows common "
     "memory-compiler naming; no source in the drop states it (see u.macro-geometry).")

fact("l3.vendor", "storage",
     "The macros are Synopsys SRAMs with Synopsys STAR Memory System BIST: Ainekko's translation guide lists 'Synopsys ASIC "
     "SRAMs (saduls0g4l1p*, etc.)', the spec's BIST is 'a shared bus BIST, such as the Synopsys SMS', and the BIST "
     "wrappers in the open build script are named sms_sram_wr_<macro>.",
     None, None,
     "external/core-et-main/AGENTS.md:609; " + f"{SCS} pdf p.49 §2.14.6.3; external/core-et/dv/common/scripts/gen_bist_br:45-49, 129-140",
     "et-spec", None, None,
     "AGENTS.md is a guide for translating the RTL, written in 2026, not a tape-out record. The gen_bist_br wrappers are "
     "the I/O shire's (its shire cache uses the same 4096x144 data-macro size); the minion shire's are not listed there. "
     "'Synopsys' for the vendor rests on these three sources, none of them a purchase record.")

fact("l3.trim-table", "circuit knobs",
     "Each macro has trim bits: read margin RM[3:0] (with enable RME), read assist RA[1:0], write assist WA[2:0] and write "
     "pulse WPULSE[2:0], set per logical RAM by ESR. For the tag and data macros (1PUHD) the spec's rows are RM mode 0: "
     "Vmin 585 mV, Vnom 650, WA 7, RA 1; RM1: 630/700, WA 7, RA 1; RM2: 650/722, WA 6, RA 0; up to RM5: 855/950. The "
     "default is RM0 'to allow nominal 650mV operation'.",
     650, "mV (default nominal)",
     f"{SCS} pdf p.50-51 §2.14.6.4, Tables 13-14; external/et-platform/etsoc-hal/include/hwinc/etsoc_shire_other_esr.h:3073-3364 (shire_cache_ram_cfg1/2 fields)",
     "et-spec", None, None)

fact("l3.trim-reset", "circuit knobs",
     "The emulator's reset values of shire_cache_ram_cfg1 (0xE800340) and cfg2 (0x03A0) decode to RME 0, RM 0, RA 1, WA 7, "
     "WPULSE 0 for the tag and data macros and RA 2, WA 6 for the tag-state macros: exactly the spec's RM0 rows. No "
     "firmware in the drop writes these registers.",
     None, None,
     "external/et-platform/sw-sysemu/esrs_et.cpp:46-47 decoded with etsoc_shire_other_esr.h:3073-3364; "
     "grep of external/et-platform/device-bootloaders finds no write to SHIRE_CACHE_RAM_CFG*",
     "et-derived", None, None,
     "The HAL header gives these fields no reset value (RESET_MASK 0xfffffff000000000 for cfg1), so what the silicon "
     "holds is not established: u.live-settings.")

fact("l3.sram-rail", "voltage",
     "The SRAM rail sits at 705 mV (703-707 mV on the die at idle, per shire), well above the minion rail (517-521 mV) "
     "and the mesh rail (483-486 mV).",
     705, "mV",
     f"{CLAIMS}:41 (docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json); telemetry fields reg_mv.sram, die_mv.sram",
     "et-measured", "aifoundry2", PT)

fact("l3.rail-vs-trim", "voltage",
     "At 705 mV the tag and data macros run between the spec's RM1 row (Vnom 700 mV) and RM2 row (722 mV), 55 mV above "
     "the RM0 row's 650 mV nominal that the reset trim selects.",
     55, "mV above RM0 nominal",
     f"l3.sram-rail against {SCS} pdf p.51 Table 14",
     "et-derived", "aifoundry2", None,
     "Whether RM0 or a higher row is programmed on these cards is u.live-settings.")

fact("l3.hv-region", "voltage",
     "The Shire Channel, which holds the shire cache, the UC block and the I-cache data memory, is a high-voltage region: "
     "the I-cache memory sits there 'because it has to be operated at high voltage'. The mesh routers sit on their own "
     "low-voltage rail, and the router side of each crossing is low voltage.",
     None, None,
     f"{MSD} pdf p.10 §3.1 and pdf p.18 §5; external/core-et/rtl/libs/mems_and_fifos/vcfifo_nsip_brdg2rtr.v:9 "
     "(via docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:74)",
     "et-spec", None, HPM + "#method",
     "Which rail feeds the shire-cache logic (the SRAM rail or another) is in the Power Spec, which is not in the drop: u.rail-of-logic.")

fact("l3.clock", "clocks",
     "The shire cache runs on shire_clock, the same clock as the minions (the neighbourhood clock is shire_clock shifted "
     "180 degrees; the errata: every area of a minion shire except the NoC uses the same clock), so 600 MHz on these "
     "cards; the mesh runs on clk__noc, 400 MHz.",
     600, "MHz",
     f"{MSD} pdf p.12 Table 2; {ERR} pdf p.42; clk__noc 400 MHz: telemetry mhz.noc (docs/reports/data/2026-09-20-power-aifoundry2/horace-telemetry.jsonl) and SYNTHESIS.md:72",
     "et-spec", CARDS3, HIER + "#load-latency-against-working-set-size")

fact("l3.clock-gating", "circuit",
     "Each data macro's clock is gated: an integrated clock gate (latch + AND) opens only while the pipeline accesses "
     "that sub-bank and for ram_delay cycles after; the spec asks that address and write-enable inputs stay unchanged "
     "when a RAM is not accessed.",
     None, None,
     f"{CEM}shirecache_pipe_data_ram_wrap.sv:52-72; external/core-et-main/AGENTS.md:100 (prim_clk_gate: 'latch + AND (ASIC ICG pattern)'); {SCS} pdf p.46 §2.14.1.5, §2.14.1.11",
     "et-spec", None, None)

fact("l3.panels", "circuit",
     "A read enables all four 144-bit data panels of the sub-bank; a write enables only the panels whose quadword enable "
     "is set ('a Partial Write that just changes three words does not need to activate more than three memory panels').",
     4, "panels per read",
     f"{CEM}shirecache_pipe_data_ram_wrap.sv:83-107 (qw_req, qw_we); {SCS} pdf p.48 §2.14.5",
     "et-spec", None, None)

fact("l3.zero-state", "circuit",
     "Zero lines skip the data array. When a fill or a full-line write brings an all-zero line (the bank computes the NOR "
     "of all 512 bits as the line arrives), the tag state's zero bit is set and the data macros are not written; a later "
     "read of that line does not read them either and returns zeros. Enabled by default (esr_sc_zero_state_enable = 1).",
     None, None,
     f"{SCS} pdf p.47 Table 12 ('zero ... cache memory must not be read') and pdf p.101 (esr_sc_zero_state_enable); "
     f"{CEM}shirecache_bank_mesh.sv:346 (zero_data = ~|data); {CEM}shirecache_pipe_sub_bank.sv:810 (no data RAM read on a zero hit), 983-1001, 1051-1063 (no data RAM write)",
     "et-spec", None, None,
     "The zeros still cross the mesh as 512 data bits. Whether the cards run with the feature on is u.live-settings.")

fact("l3.no-refresh", "circuit",
     "The shire-cache specification describes no refresh or retention circuit for its RAMs, only deep_sleep (a low-leakage "
     "retention mode) and shut_down (data lost) for the RAMs of shires that are not operational.",
     None, None,
     f"{SCS} pdf p.101 (esr_sc_ram_deep_sleep, esr_sc_ram_shut_down); external/core-et-main/hw/ip/ram_cfg/rtl/ram_cfg_pkg.sv:14-23",
     "et-spec", None, None,
     "A text search of the spec for 'refresh' finds nothing.")

fact("l3.ecc-scrub", "circuit",
     "A single-bit ECC error is corrected in the pipeline's ECC stages (te for tags, de for data) but not written back: "
     "the scrub pass is a reserved bit, for future chips.",
     None, None,
     f"{SCS} pdf p.46 §2.14.1.8, §2.14.1.14; pdf p.99 (esr_sc_ecc_scrub_enable: 'Future chips will implement this feature')",
     "et-spec", None, None)

# ---------------------------------------------------------------- pipeline and ports
fact("l3.ports", "ports",
     "Each shire meets the mesh with 4 L3-slave ports (incoming L3 and remote-scratchpad requests, 512 bits, one request "
     "per cycle each), 4 to_l3 master ports and 1 to_sys master port (to memory). AXI channels cross into the NoC through "
     "voltage-changing FIFOs with 2-stage synchronizers.",
     4, "L3 slave ports",
     f"{SCS} pdf p.8, pdf p.11 (VCFIFO, 2-stage synchronizers), pdf p.32-34 §2.3-2.4 ('four for the L3 mesh and one for the SYS mesh'); {CEM}shirecache_pkg.sv:138-139",
     "et-spec", None, HPM + "#lanes")

fact("l3.lane", "ports",
     "Which of the 4 lanes an L3 request takes is set by the bank it will use at the home, PA[12:11] under swizzle0, not by "
     "PA[7:6]; PA[7:6] picks the lane only for remote-scratchpad requests. At the home the request goes to bank PA[12:11].",
     None, None,
     f"{CEM}shirecache_mesh_master.sv:132-153 (req_bank_id = remote SCP ? PA[7:6] : L3 bank from shirecache_pipe_l3_swizzle_get); "
     f"{SCS} pdf p.100 (the swizzle fields are used 'by the incoming L3 distribute design to select the correct bank')",
     "et-spec", None, HPM + "#lanes",
     "core-et-main is Ainekko's co-simulated translation of the CORE-ET RTL. Heat per millimetre's lane rule (PA[7:6], chip "
     "fact L103) is right for its remote-scratchpad flows; for L3 lines the lane is the home bank.")

fact("l3.reqq", "pipeline",
     "Each bank has a 64-entry request queue, up to 21 entries of it reserved for L3-slave requests; two entries can be "
     "allocated per cycle, one for a neighbourhood request and one for an L3 request.",
     21, "entries reserved for L3",
     f"external/core-et/rtl/shire/esr/esr_cache_bank.v:81 (NUM_REQQ_ENTRIES/3); {SCS} pdf p.35 §2.6; docs/research/counters-and-dram.md:461-462",
     "et-spec", None, HOT + "#the-thing-that-actually-starves")

fact("l3.priority", "pipeline",
     "L3-slave requests win over the shire's own requests for a sub-bank (the second of three arbitration steps) unless "
     "esr_sc_l3_yield_priority_cnt is set; two errata record neighbourhood requests starved or hung behind L3-slave "
     "traffic.",
     None, None,
     f"{SCS} pdf p.36 §2.6 (Figure 8), pdf p.99; {ERR} pdf p.80-81 (§4.1, §4.2)",
     "et-spec", None, HOT + "#the-thing-that-actually-starves")

fact("l3.pipeline", "pipeline",
     "A read goes down the bank's non-stalling pipeline in two phases, tag then data: ag, ad (allocate), rqa (arbitrate), "
     "tap, ta, ta0, ta1 (tag and tag-state RAM access), te (tag ECC), tc (tag compare: hit, miss, victim), then dap, da, "
     "da0, da1 (data RAM access), de (data ECC), dc (data complete, OR'd from the sub-banks to the response mux).",
     None, None,
     f"{SCS} pdf p.44-46 §2.14-2.14.1",
     "et-spec", None, None)

fact("l3.hit-way-read", "pipeline",
     "Only the hit way is read: the data RAM address {set, hit way} is formed after the tag compare, so one 144-bit word "
     "per panel is read, not the four ways' data.",
     1, "way read",
     f"{CEM}shirecache_pipe_sub_bank.sv:1613; {SCS} pdf p.44 (pipeline diagram: data read after tag compare)",
     "et-spec", None, None)

fact("l3.ram-delay", "pipeline",
     "RAM access takes 2 cycles by default (esr_sc_ram_delay = 2; 3 or 4 possible), so a sub-bank accepts a request every "
     "2 cycles and a bank one per cycle across its 4 sub-banks; a fill that evicts a victim (read then write) holds a "
     "sub-bank for 4 cycles.",
     2, "cycles per RAM access",
     f"{SCS} pdf p.36 (busy rule 1), pdf p.44-45, pdf p.101; external/core-et/rtl/inc/shire_cache_defines.vh:260 (SC_RAM_DELAY_DEFAULT 2)",
     "et-spec", None, None,
     "No firmware in the drop writes sc_pipe_ctl; the live value is u.live-settings.")

fact("l3.mru-write", "pipeline",
     "An L3 read hit also writes: the LRU code is updated (the hit way becomes most recent) through the tag-state RAM's "
     "second port, which lets one pass read and write it.",
     None, None,
     f"{CEM}shirecache_pipe_sub_bank.sv:843-859 (update_mru_tc includes L3Read hits), 884-888; {SCS} pdf p.45 ('the state RAM is two-ported'), pdf p.47-48 §2.14.4",
     "et-spec", None, None)

fact("l3.no-rbuf", "pipeline",
     "L3 reads never use the bank's 8-entry read buffer, so every L3 hit reads the tag, tag-state and data macros (L2 and "
     "scratchpad reads can be served from the buffer).",
     None, None,
     f"{SCS} pdf p.11 Table 1 ('L3 does not access the Read buffer'), pdf p.40 §2.8",
     "et-spec", None, None)

fact("l3.spec-latency", "latency",
     "Designed idle latencies in shire clocks, crossbars included: L3 read hit 30 (from the L3-slave AXI read request to "
     "its response), L3 read miss 42 + NoC and memory, and at the requester an L2 read miss 34 + NoC and L3.",
     30, "shire clocks",
     f"{SCS} pdf p.11 Table 1",
     "et-spec", None, HIER + "#the-hierarchy-as-a-spec-sheet")

fact("l3.partial", "data path",
     "The L3, unlike the L2, can hold partial lines left by write-arounds; a read that hits one first evicts the partial "
     "line to memory and reads it back.",
     None, None,
     f"{SCS} pdf p.55 §3.2.2, pdf p.62 §3.4.3",
     "et-spec", None, None)

fact("l3.write", "data path",
     "L3 writes carry full lines, quadword enables or partials: a write that misses is installed with dirty bits for its "
     "quadwords (no fill for whole quadwords); one that hits a clean line marks all four quadwords dirty.",
     None, None,
     f"{SCS} pdf p.61 §3.4.3",
     "et-spec", None, None)

fact("l3.writearound", "data path",
     "Tensor stores reach the L3 as write-arounds: they coalesce in the requesting shire's L2 buffer (32 entries per bank) "
     "and go to the home when all four 16-byte quadwords of the line are written, or on a flush or eviction.",
     32, "coalescing entries per bank",
     f"{SCS} pdf p.9 §1.1, pdf p.62 §3.5",
     "et-spec", None, None)

fact("l3.miss-path", "data path",
     "An L3 miss leaves the home through its to_sys port to the memory shire PA[8:6]; the data returns as an L3 fill "
     "(which may evict a victim, written back over to_sys if dirty) and the home answers the requester.",
     None, None,
     f"{SCS} pdf p.55 §3.2.2 ('Misses and victims are directed to the to_sys mesh port'), Figure 14; docs/research/counters-and-dram.md:478-482",
     "et-spec", None, ANAT + "#trace-one-load")

fact("l3.dram-leg", "latency",
     "Past the L3 a DRAM load adds 91 + 12 cycles per hop from the home to the memory shire (the constant 90-91 on three "
     "cards).",
     91, "cycles + 12 per hop",
     "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.ms_const; docs/reports/data/2026-09-26-memprobe-3cards/cards.json ms_const",
     "et-measured", CARDS3, ANAT + "#the-memory-shire-leg-91-cycles-plus-12-per-hop")

# ---------------------------------------------------------------- measured latency
fact("l3.lat-fit", "latency",
     "L3 hit, load to use: 110.5 + 11.99 cycles per mesh hop between the requester and the home shire, on each of three "
     "cards (5 passes each); within 4 cycles for 99.4-99.97% of lines.",
     110.5, "cycles + 11.99 per hop",
     f"{CLAIMS}:415 (docs/reports/data/2026-09-25-claims-v3/results/mem.json [item=MEM-P1].per_card.<card>.tests.P1_l3_intercept, .P1_l3_slope)",
     "et-measured", CARDS3, ANAT + "#l3-110-cycles-plus-12-per-hop")

fact("l3.lat-by-home", "latency",
     "From shire 0 (aifoundry2, 19 Sep, median of each home's lines): 109 cycles when the home is shire 0 itself, 121-122 "
     "at 1 hop, 133-134 at 2, 157-158 at 4, 181-182 at 6, 218 at 9 hops.",
     109, "cycles (home = requester)",
     "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.l3_by_slice (med, hops per home shire)",
     "et-measured", "aifoundry2", ANAT + "#l3-110-cycles-plus-12-per-hop")

fact("l3.lat-by-requester", "latency",
     "Averaged over all 32 homes (pointer chase over a 4 MB working set): 168.8-168.9 cycles from shires 0 and 31, "
     "160.6-160.7 from shire 7, 159.1-159.2 from shire 24, in every pass on three cards.",
     159.1, "cycles (best requester)",
     f"{CLAIMS}:422 (V3R/lat.json items[LAT-M2].per_card.<card>.passes[].L3)",
     "et-measured", CARDS3, HIER + "#scratchpad-latency-across-the-mesh")

fact("l3.lat-clock-split", "latency",
     "Chases at 600 and 800 MHz split the L3 constant: 72.2 cycles scale with the core clock and 61.4 ns do not, plus 20 ns "
     "per mesh hop (72.2 cycles + 61.4 ns = 109 cycles at 600 MHz).",
     61.4, "ns not scaling with the core clock",
     f"{CLAIMS}:379 (docs/reports/data/2026-09-18-memhier-aifoundry2, fits); workloads/memprobe/report_template.html:881-884",
     "et-measured", "aifoundry2", ANAT + "#l3-110-cycles-plus-12-per-hop")

fact("l3.lat-reconcile", "latency",
     "The spec's counts do not add up to the measured split: an L2 miss (34 shire clocks) plus an L3 hit at the home "
     "(30) is 64 clock-scaled cycles, and the L1 and neighbourhood path adds about 26 more (L2 hit 47 measured against "
     "21 in the spec), about 90 against the 72.2 measured. The anatomy page's split of the 110 (about 48 to miss the L1 "
     "and L2, about 62 for the home slice) is an estimate.",
     None, None,
     f"{SCS} pdf p.11 Table 1; {CLAIMS}:379, 421 (L2 hit 47); docs/research/counters-and-dram.md:476; workloads/memprobe/report_template.html:880-881",
     "et-derived", None, None,
     "Where the 61 ns go (four voltage-and-clock crossings, the NoC bridges, the mesh stops at 0 hops) is u.latency-split.")

fact("l3.hop", "mesh",
     "Each mesh hop adds 12 cycles to the round trip at 600 MHz: 20 ns, which is 16 cycles at 800 MHz. The same 12.00 per "
     "hop holds for L3 hits (11.99), remote scratchpad (12.00) and TensorSend (12.02).",
     20, "ns per hop, round trip",
     f"{CLAIMS}:415, 423, 392; workloads/memprobe/report_template.html:881-884",
     "et-measured", CARDS3, NOC + "#where-the-shires-are-a-6-6-mesh")

fact("l3.hop-noc-cycles", "mesh",
     "20 ns per hop round trip is 10 ns, or 4 cycles of the 400 MHz NoC clock, per hop each way, if request and reply "
     "take equal time.",
     4, "NoC cycles per hop each way",
     "l3.hop with l3.clock; docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:76",
     "et-derived", None, HPM + "#method",
     "A published measurement (Chang) reports 3 cycles per direction at an unstated clock; not reconciled.")

fact("l3.tsend-compare", "mesh",
     "For comparison, a 32 B TensorSend round trip between two shires is 150 + 12.02 cycles per hop: the same 12 per hop "
     "as an L3 hit but a larger fixed cost (register to register through both shires' message paths) than the L3's 110.",
     150, "cycles + 12.02 per hop",
     f"{CLAIMS}:392, 424",
     "et-measured", CARDS3, NOC + "#where-the-shires-are-a-6-6-mesh")

fact("l3.mean-hops", "mesh",
     "On the measured map a requester is on average 3.75 hops from a line's home (all 32 x 32 pairs, self included): "
     "2.81 from the best-placed shire, 5.00 from corner shires 0 and 31, 10 at most. By the fit an average L3 hit costs "
     "about 155 cycles (258 ns) chip-wide, 144-170 by requester, and 230 cycles (383 ns) at 10 hops.",
     3.75, "hops (chip mean)",
     "computed here from workloads/nocbench/analyze.py:52-60 (MARTY) and l3.lat-fit",
     "et-derived", None, NOC + "#where-the-shires-are-a-6-6-mesh",
     "The fit predicts 170.5, 162.2, 160.7 and 170.5 cycles for requesters 0, 7, 24 and 31, 1-2 cycles above l3.lat-by-requester's chases.")

fact("l3.route", "mesh",
     "Routes are minimal (latency is linear in Manhattan distance over all 496 pairs, through the four non-compute cells "
     "too); whether a request turns x or y first, which of the nine router layers L3 traffic uses and how wide a link is "
     "are not documented in the drop.",
     None, None,
     f"{CLAIMS}:392; docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:66-68, 75",
     "et-measured", CARDS3, NOC + "#what-the-numbers-say")

fact("l3.flits", "mesh",
     "A read request is about 75-85 bits (AXI AR); the reply is one 512-bit data beat plus RID/RRESP/RLAST (524-534 bits) "
     "and a NetSpeed header of unknown width. Only the reply carries the line.",
     512, "data bits per reply",
     "docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:64, 77 (external/core-et/rtl/inc/axi_defines.vh:39, 43, 61, 69)",
     "et-spec", None, HPM + "#lanes")

fact("l3.mesh-rail", "voltage",
     "The mesh (routers, links, NetSpeed bridges) runs at 485 mV set (484 at the die) and 400 MHz on these cards.",
     485, "mV",
     "SYNTHESIS.md:72-74 (telemetry reg_mv.noc, die_mv.noc, mhz.noc)",
     "et-measured", CARDS3, HPM + "#method")

# ---------------------------------------------------------------- measured bandwidth and energy
fact("l3.bw", "bandwidth",
     "Every minion streaming from the L3: 0.98 TB/s chip-wide at 600 MHz, 1.6 B per minion-cycle, about 30.7 GB/s per "
     "slice; the own L2 gives 2.45 TB/s.",
     0.98, "TB/s",
     f"{CLAIMS}:380 (docs/reports/data/2026-09-18-memhier-aifoundry2/energy*/runs.jsonl, config l3)",
     "et-measured", "aifoundry2, aifoundry3", RIDGE)

fact("l3.bw-tload", "bandwidth",
     "Tensor loads by all 1,024 minions (32 KB touched per hart, stride 8 KB, so the set fits the L3) read the L3 at "
     "1,072 GB/s on all three cards.",
     1072, "GB/s",
     "docs/reports/data/2026-09-23-energy-manual/catalogue.json cards.<card>.summary['dramrow/stride8K/<zeros|random>'].bytes_per_s; docs/energy-manual/04a-fine-grain.md:68",
     "et-measured", CARDS3, MAN)

fact("l3.energy", "energy",
     "An L3 byte costs 14.7 pJ above idle [7.1-20.5 over 18 passes] (1 KB tensor loads by every minion, 768 KB per shire, "
     "600 MHz): aifoundry2 12.3, aifoundry3 13.5, aifoundry1 card 1 18.4 pJ/B; 4.7x an L2 byte (3.11), a seventh of a "
     "DRAM byte (114.6). About 0.94 nJ per 64 B line.",
     14.7, "pJ/B",
     "docs/reports/data/2026-09-23-energy-manual/manual.json reruns.levels_pj_per_byte['l3'] (mean, lo, hi, per_card); docs/energy-manual/04-bytes-memory.md:27",
     "et-measured", CARDS3, MAN,
     "The probe did not set the L3's contents (04-bytes-memory.md:21).")

fact("l3.energy-contents", "energy",
     "With the contents set, L3 reads cost 2.5x more on random data than on zeros: 7.6 vs 19.3 pJ/B on aifoundry2, 7.5 vs "
     "18.8 on aifoundry3, 9.0 vs 22.8 on aifoundry1 card 1 (tensor loads at 1,072 GB/s).",
     19.3, "pJ/B (random, aifoundry2)",
     "docs/reports/data/2026-09-23-energy-manual/catalogue.json cards.<card>.summary['dramrow/stride8K/<zeros|random>'].pj_per_byte; docs/energy-manual/04a-fine-grain.md:68",
     "et-measured", CARDS3, MAN)

fact("l3.energy-rails", "energy",
     "Split by rail (aifoundry2, same runs): random data 7.5 pJ/B on the SRAM rail, 7.5 on the mesh rail, 1.4 on the "
     "minion rail (20.6 W over idle in all); zeros 2.9, 3.2 and 0.6 pJ/B (8.1 W). The SRAM rail falls 2.6x on zeros, the "
     "mesh rail 2.3x.",
     7.5, "pJ/B (SRAM rail, random)",
     "docs/reports/data/2026-09-23-energy-manual/catalogue.json cards.aifoundry2.summary['dramrow/stride8K/<op>'].rails_over_w "
     "(sram_w 8.08 / 3.16, noc_w 8.09 / 3.46, minion_w 1.51 / 0.67) over .bytes_per_s (1.072e12)",
     "et-derived", "aifoundry2", MAN,
     "aifoundry3: SRAM 7.92 / 3.15 W, mesh 7.87 / 3.39 W; aifoundry1-c1: SRAM 6.84 / 2.76 W, mesh 9.39 / 4.06 W. A zero line "
     "skips the data macros at both ends (l3.zero-state), which fits a large SRAM-rail drop; the share is u.zero-share.")

fact("l3.energy-per-load", "energy",
     "Per load of one 64 B line (19 Sep, one 8-byte ld per line): an L3 hit with a local home 643 pJ on board power, "
     "of it 306 on the SRAM rail (the L2 miss, the L3 read and the L2 fill), 120 mesh, 110 minion; an L2 hit 214 pJ "
     "(112 SRAM). Far homes (5.6 hops on average) raise the mesh rail to 385 pJ: about 59 pJ per line per hop, 47 of it "
     "on the mesh rail.",
     306, "pJ per L3 load on the SRAM rail",
     "docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json power.l3near / .l3far / .l2 .pj_per_load; workloads/memprobe/report_template.html:1093-1096",
     "et-measured", "aifoundry2", ANAT + "#where-the-energy-goes",
     "Superseded by the energy manual for totals; still the only per-load rail split with a local home.")

fact("l3.wire-energy", "energy",
     "A random bit costs 36.2 fJ per mm on the mesh rail over free links (46.7 on board power). A 64 B reply over one "
     "3.72 mm hop is then about 69 pJ on the mesh rail (1.1 pJ/B per hop), close to the 47-59 pJ per hop of l3.energy-per-load.",
     36.2, "fJ per random bit-mm",
     f"{CLAIMS}:350, 457 (docs/reports/data/2026-09-24-wire-energy/report.json headline['uncontended/noc_rail']); hop length docs/findings/05-claims.md:349",
     "et-derived", "aifoundry2, aifoundry3", HPM,
     "The per-hop product (512 bits x 36.2 fJ x 3.72 mm) is computed here and ignores the request and headers.")

fact("l3.gather", "energy",
     "A gather that goes straight to the home slice (fgwg.ps, random lines, 4 KB per hart) costs 1.53 nJ per 4-byte "
     "element at 6.46 G elements/s: each element fetches its own 64 B line, about 24 pJ per line byte.",
     1.53, "nJ per element",
     "docs/energy-manual/04-bytes-memory.md:58, 78 (docs/reports/data/2026-09-25-claims-v3/results/gs.json)",
     "et-measured", CARDS3, MAN)

fact("l3.atomic", "atomics",
     "Global atomics execute in the home bank's atomic block: one contended line retires an atomic every 10.00 cycles "
     "(about 60 M/s for the chip); an uncontended remote global atomic takes 216 cycles round trip. The sub-bank stays busy "
     "for the read, the operation and the write.",
     10.0, "cycles per contended atomic",
     f"{CLAIMS}:222, 224 (docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json); {SCS} pdf p.36 (busy rule 3), pdf p.40 §2.9, pdf p.72 §3.7.2",
     "et-measured", "aifoundry2, aifoundry3", HOT)

fact("l3.atomic-rails", "atomics",
     "Atomics on home-L3 lines draw 3.99 W over idle on aifoundry2: 26% minion rail, 24% SRAM, 33% mesh, 17% unmetered.",
     3.99, "W over idle",
     "docs/energy-manual/04a-fine-grain.md:171",
     "et-measured", "aifoundry2", MAN)

fact("l3.flag", "atomics",
     "A flag handed through global atomics costs 610-1,150 ns round trip (median 873) whatever the two shires' distance: it "
     "depends on which shire's L3 slice holds the flag's line.",
     873, "ns (median)",
     "docs/reports/2026-09-18-et-soc1-on-chip-communication.html §'Latency grows with distance, except through memory'",
     "et-measured", "aifoundry2", NOC + "#latency-grows-with-distance-except-through-memory")

fact("l3.leakage", "energy",
     "The SRAM rail at idle is 1.60 W at 67 C and 2.63 W at 82 C on aifoundry2 (slope 0.066 W/C on aifoundry3); at 80 C "
     "its 2.51 W is 19.6 mW per MB of the 128 MB of L2, L3 and scratchpad, an upper bound on the arrays' leakage since "
     "cache logic shares the rail. The L3's 32 MB are then at most about 0.63 W.",
     19.6, "mW per MB (upper bound, 80 C)",
     f"docs/energy-manual/04a-fine-grain.md:106-111; {CLAIMS}:312, 473",
     "et-measured", "aifoundry2, aifoundry3", MAN,
     "The 0.63 W for the L3 is a quarter of the rail, computed here.")

fact("l3.observe", "observability",
     "No counter a user-mode kernel can read reports L3 hits or misses; the shire cache has per-bank performance monitors "
     "(events chosen by ESR) that need firmware or a new syscall, and an index CacheOp can read one quadword of any tag, "
     "state or data RAM with its ECC bits from M-mode.",
     None, None,
     f"{SCS} pdf p.52 §2.15, pdf p.88-94 §3.14, pdf p.104 §4.9; workloads/memprobe/report_template.html:1063; docs/reports/sources/limits-of-observability.data.json ladder rows 'Chosen counter events', 'Raw SRAM row + ECC bits'",
     "et-spec", None, LOO + "#ladder")

fact("l3.power-goal", "energy",
     "The spec's power line reads 'Power: TBD. Goal is 100 MW for the entire Shire Cache running benchmark' (presumably "
     "mW, per shire).",
     100, "mW (design goal, as written 'MW')",
     f"{SCS} pdf p.11",
     "et-spec", None, None)

fact("l3.process", "technology",
     "TSMC 7 nm, 570 mm2, over 24 billion transistors (Esperanto's Hot Chips 33 slides and IEEE Micro 2022 paper).",
     7, "nm",
     "docs/findings/01-resources.md:90-102 (R6)",
     "et-spec", None, None)

# ---------------------------------------------------------------- generic circuit facts (labelled GENERIC on the page)
fact("g.6t-cell", "circuit (generic)",
     "GENERIC. A 6T SRAM cell stores a bit on two cross-coupled inverters (two PMOS pull-ups, two NMOS pull-downs) and "
     "connects to a bitline pair through two NMOS access transistors whose gates are the row's wordline.",
     6, "transistors per bit", "textbook (e.g. Rabaey, Digital Integrated Circuits, ch. 12)", "generic", None, None,
     "The ET-SoC-1 sources name the data array 'SRAM' but not its bitcell: u.bitcell.")

fact("g.read", "circuit (generic)",
     "GENERIC. A read: precharge/equalise PMOS hold both bitlines at the supply and switch off; the row decoder's NAND/NOR "
     "gates select one wordline driver, which raises that wordline across the row; in every cell of the row the access "
     "transistor on the side storing 0 pulls its bitline down through the pull-down NMOS, developing tens of mV; the "
     "column mux passes one pair per output bit to a latch-type sense amplifier, which fires on its enable and resolves to "
     "full rail into the output latch.",
     None, None, "textbook", "generic", None, None,
     "Every column of the selected row discharges one bitline whatever the data, so the array's read energy is roughly "
     "data-independent; data-dependent energy comes from the output datapath, ECC and wires.")

fact("g.write", "circuit (generic)",
     "GENERIC. A write: write drivers pull one bitline of each selected pair to ground, the wordline rises, and the access "
     "transistor overpowers the cell's PMOS pull-up so the cell flips. Write assist (for example a negative bitline or a "
     "lowered cell supply) and a longer write pulse make the flip reliable at low voltage.",
     None, None, "textbook", "generic", None, None,
     "The ET macros expose WA and WPULSE trims (l3.trim-table); which technique WA drives is not stated.")

fact("g.assist", "circuit (generic)",
     "GENERIC. Read assist usually lowers the wordline voltage so a read cannot flip a weak cell; read-margin settings "
     "delay the sense-amplifier enable so more bitline swing develops, slower but safer at low voltage.",
     None, None, "textbook; memory-compiler datasheets", "generic", None, None,
     "The ET macros expose RA and RM (l3.trim-table); their exact circuit effect is vendor-specific.")

fact("g.tag-compare", "circuit (generic)",
     "GENERIC. Tag compare: per way, 23 XNOR gates (one per tag bit) feed an AND tree (or a precharged match line pulled "
     "down by any mismatch); the four hit signals select the way and encode it.",
     None, None, "textbook", "generic", None, None)

fact("g.ecc", "circuit (generic)",
     "GENERIC. SECDED (72,64) Hamming code: 8 check bits per 64 data bits computed by XOR trees on write; on read a "
     "syndrome from the same XOR trees points at a single flipped bit, which an XOR corrects, and flags a double error.",
     8, "check bits per 64", "textbook (Hsiao code)", "generic", None, None,
     "That the shire cache uses 8 ECC bits per 64-bit doubleword is et-spec (l3.geometry).")

fact("g.icg", "circuit (generic)",
     "GENERIC. An integrated clock gate is a latch (transparent while the clock is low) holding the enable, ANDed with the "
     "clock: when the enable is low the macro's clock does not toggle, so its clock tree and flops draw no switching "
     "power.",
     None, None, "textbook", "generic", None, None)

fact("g.crossing", "circuit (generic)",
     "GENERIC. A voltage and clock crossing: a level shifter (cross-coupled PMOS over an NMOS differential input pair) "
     "lifts or drops the signal swing, and a 2-flip-flop synchroniser (as the spec's VCFIFO uses) samples it in the "
     "receiving clock, costing 2-3 receiving-clock cycles.",
     2, "synchroniser stages",
     f"textbook; the 2 stages are et-spec ({SCS} pdf p.11)", "generic", None, None)

fact("g.router", "circuit (generic)",
     "GENERIC. A mesh router stage: input virtual-channel buffers (flip-flop or register-file arrays), route computation, "
     "virtual-channel and switch allocators (arbiters), a crossbar of multiplexers, and output drivers onto the link; each "
     "link is a bundle of wires broken by repeaters (inverter pairs) every few hundred microns.",
     None, None, "textbook (Dally and Towles, Principles and Practices of Interconnection Networks)", "generic", None, None,
     "ET routers have 8 ports and 4 VC slots each, 9 main layers per stop (chip fact L105; SYNTHESIS.md:67-68).")

fact("g.wire-energy", "circuit (generic)",
     "GENERIC. A wire's switching energy is about C x V^2 per 0-to-1 transition (C about 0.2 pF/mm), so random data (a "
     "transition on about half the bits) costs several times zeros; repeaters add to it.",
     None, None, "textbook; docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:135-147 (literature table)", "generic", None, None)

fact("g.leakage", "circuit (generic)",
     "GENERIC. Every SRAM cell leaks all the time: sub-threshold current flows through its off transistors (one pull-up "
     "or pull-down per inverter and the access transistors), rising roughly exponentially with temperature.",
     None, None, "textbook", "generic", None, None,
     "Matches the measured SRAM rail at idle (l3.leakage).")

fact("g.no-refresh", "circuit (generic)",
     "GENERIC. A 6T SRAM cell holds its bit as long as it is powered and needs no refresh; a 1T1C DRAM or eDRAM cell "
     "stores charge on a capacitor that leaks and must be refreshed every few tens of microseconds to milliseconds.",
     None, None, "textbook", "generic", None, None,
     "Relevant to u.bitcell: the shire-cache spec describes no refresh (l3.no-refresh).")

# ---------------------------------------------------------------- unknowns (each is an ask below)
fact("u.bitcell", "storage (unknown)",
     "UNKNOWN. What bitcell the shire-cache macros use (6T high-density? 8T? another cell?), and what the lab lead meant by "
     "'not using SRAM'. The spec, the datasheet and the translation guide all call these arrays SRAM; the minion's L1 "
     "data array is a separate custom 1R1W macro (dcache_128x32_1r1w_lram) whose cell is not stated either.",
     None, None,
     f"{SCS} pdf p.48, p.51; {DS} pdf p.4; external/core-et-main/AGENTS.md:609; external/core-et/rtl/libs/macros/dcache_128x32_1r1w_lram.v:5-12 "
     "(behavioural stand-in); external/core-et/rtl/shire/minion/dcache/dcache_data_ram_wrap.v",
     "unknown", None, None, "The lab lead's remark is not recorded in the repo; the owner relayed it.")

fact("u.macro-geometry", "storage (unknown)",
     "UNKNOWN. The physical organisation of mbd (4096 x 144), mbt (1024 x 116) and mbs (1024 x 40): rows, columns, column "
     "mux, internal banks, sense-amplifier type. Common compiler naming would read 'm4b4' as a 4:1 column mux and 4 "
     "banks, i.e. 256 wordlines x 576 bitline pairs per bank in mbd; nothing in the drop confirms it.",
     None, None, f"{SCS} pdf p.51 (names only)", "unknown", None, None)

fact("u.live-settings", "circuit knobs (unknown)",
     "UNKNOWN. The live values on these cards of esr_sc_ram_delay (default 2), esr_sc_zero_state_enable (default 1) and "
     "the RAM trims shire_cache_ram_cfg1/2 (emulator reset = RM0 row) at the 705 mV SRAM rail.",
     None, None,
     f"{SCS} pdf p.50-51, p.101; external/et-platform/sw-sysemu/esrs_et.cpp:46-47; etsoc_shire_cache_esr.h:839-846, 879-880",
     "unknown", None, None)

fact("u.rail-of-logic", "voltage (unknown)",
     "UNKNOWN. Whether the shire cache's logic (pipeline, crossbars, request queues, the high side of the VCFIFOs) is on "
     "the metered SRAM rail with the macros, or on another rail.",
     None, None, f"{MSD} pdf p.10, p.18 (refers to the Power Spec)", "unknown", None, None)

fact("u.latency-split", "latency (unknown)",
     "UNKNOWN. Where the 110-cycle L3 constant goes stage by stage, in particular the 61 ns that do not scale with the core "
     "clock (VCFIFO synchronisers, NoC bridges, mesh-stop entry and exit at 0 hops) and why the spec's 34 + 30 shire "
     "clocks exceed the measured 72 clock-scaled cycles.",
     None, None, "l3.lat-clock-split, l3.lat-reconcile", "unknown", None, None)

fact("u.zero-share", "energy (unknown)",
     "UNKNOWN. How much of the L3's zeros-vs-random saving (SRAM rail 2.9 vs 7.5 pJ/B) is the zero-state skip of the data "
     "macros and how much is data-dependent switching in the datapath, ECC and crossings.",
     None, None, "l3.energy-rails, l3.zero-state", "unknown", None, None)

fact("u.noc-hop", "mesh (unknown)",
     "UNKNOWN. The router pipeline per hop (4 NoC cycles each way is derived), which of the 9 main-NoC layers carries L3 "
     "requests and replies, the dimension order, and the flit width.",
     None, None, "docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:66-68, 75-76", "unknown", None, None)

fact("u.slice-floorplan", "floorplan (unknown)",
     "UNKNOWN. Where the four banks (and so the L3 slice's quarters) sit in the 3.7 mm shire tile relative to the mesh "
     "stop and the four L3-slave ports.",
     None, None, f"{MSD} pdf p.5 Figure 1 (logical only)", "unknown", None, None)

# ---------------------------------------------------------------- access sequence
SEQ = {
    "conventions": "Latencies are minion cycles at 600 MHz unless stated; 'hops' = Manhattan distance on the measured map "
                   "between requester R and home H = PA[10:6]. Each circuit entry is marked et-spec (the ET sources say so) "
                   "or generic (textbook, drawn as an illustration). Fact ids point into `facts`.",
    "load_hit": [
        {"n": 1, "block": "minion L1 D-cache and miss handler (requester R)",
         "action": "The load misses the L1; one of the minion's two miss handlers sends an ET-Link read to the shire's cache bank PA[7:6].",
         "latency": "part of ~48 cycles to miss L1 and L2 (anatomy estimate)", "energy": None,
         "circuit": [{"element": "L1 tag compare and miss handler flops", "action": "switch", "kind": "et-spec (L1 level; not drawn here)"}],
         "facts": ["l3.lat-reconcile"]},
        {"n": 2, "block": "requester's L2 bank PA[7:6], sub-bank PA[9:8]",
         "action": "Request queue entry allocated; tag and tag-state macros read at the L2 set; ECC; compare: L2 miss. The entry stays to receive the fill.",
         "latency": "34 shire clocks for the L2-miss path in the spec, both directions (l3.spec-latency)", "energy": "part of 306 pJ SRAM rail per L3 load (l3.energy-per-load)",
         "circuit": [{"element": "ICG opens the macro clock", "action": "clock toggles for ram_delay cycles", "kind": "et-spec"},
                     {"element": "tag (1024x116) and tag-state (1024x40) macros", "action": "one row read: decoder, wordline driver, access transistors, bitline discharge, sense amps", "kind": "generic (cell); et-spec (macros)"},
                     {"element": "4 x 23-bit tag comparators", "action": "XNOR + AND tree: no match", "kind": "generic"}],
         "facts": ["l3.geometry", "l3.pipeline", "l3.clock-gating"]},
        {"n": 3, "block": "to_l3 mesh master (R)",
         "action": "Bank FIFO, crossbar to lane PA[12:11] (the home bank), converted to an AXI read (AR, ~75-85 bits), through a voltage-changing FIFO into the 400 MHz, 485 mV NoC.",
         "latency": "part of the 61 ns not scaling with the core clock (l3.lat-clock-split)", "energy": None,
         "circuit": [{"element": "level shifters", "action": "705 mV-side signals dropped to the 485 mV NoC", "kind": "generic (et-spec that the crossing exists)"},
                     {"element": "2-flip-flop synchronisers", "action": "sample into clk__noc", "kind": "et-spec (2 stages); generic (circuit)"}],
         "facts": ["l3.lane", "l3.ports", "l3.hv-region", "l3.flits"]},
        {"n": 4, "block": "mesh: routers and links, R to H",
         "action": "The request crosses hops(R, H) links on a minimal route (0-10 hops, 3.75 on average).",
         "latency": "about 10 ns (6 cycles) per hop each way; 12 cycles per hop round trip measured", "energy": "request only: small (the line travels back in step 8)",
         "circuit": [{"element": "router input buffers, allocators, crossbar muxes", "action": "latch/forward the flit", "kind": "generic"},
                     {"element": "repeated link wires, 3.72 mm per hop", "action": "toggle with the request bits", "kind": "generic"}],
         "facts": ["l3.hop", "l3.hop-noc-cycles", "l3.mean-hops", "l3.route"]},
        {"n": 5, "block": "home H: L3-slave port, crossbar, bank PA[12:11]",
         "action": "VCFIFO up to the shire clock; AXI to ET-Link; into the bank's L3-slave FIFO; request queue (up to 21 L3 entries); L3 requests win the sub-bank arbitration.",
         "latency": "within the 30 shire clocks of the spec's L3 hit", "energy": None,
         "circuit": [{"element": "level shifters and synchronisers", "action": "485 mV to 705 mV, NoC clock to shire clock", "kind": "generic"},
                     {"element": "request-queue flops and round-robin/priority arbiters", "action": "switch", "kind": "generic"}],
         "facts": ["l3.ports", "l3.reqq", "l3.priority"]},
        {"n": 6, "block": "home H: tag phase in sub-bank PA[14:13] (stages tap, ta, ta0, ta1, te, tc)",
         "action": "Tag macro row 768 + PA[22:15] read (4 tags, 116 bits) with the tag-state row (40 bits); ECC checked; four 23-bit compares give the hit way; LRU decoded.",
         "latency": "2-cycle macro access (default ram_delay) + ECC + compare", "energy": "part of the SRAM rail's 7.5 pJ/B (random) in l3.energy-rails",
         "circuit": [{"element": "ICG", "action": "opens the tag and tag-state macro clocks", "kind": "et-spec"},
                     {"element": "row predecoder and wordline driver", "action": "one wordline of 1,024 rises", "kind": "generic"},
                     {"element": "bitline precharge/equalise PMOS", "action": "switch off before the access, back on after", "kind": "generic"},
                     {"element": "6T cells of the row: access NMOS + pull-down NMOS", "action": "0-side bitline of each column discharges", "kind": "generic (bitcell is u.bitcell)"},
                     {"element": "column mux + latch-type sense amplifiers", "action": "116 + 40 outputs resolve to full rail", "kind": "generic"},
                     {"element": "SECDED XOR trees (6 bits per tag, 7 per state word)", "action": "syndrome = 0", "kind": "et-spec widths; generic circuit"},
                     {"element": "4 x 23-bit XNOR/AND comparators", "action": "one way matches", "kind": "generic"}],
         "facts": ["l3.decode", "l3.geometry", "l3.pipeline", "l3.ram-delay", "g.read", "g.tag-compare", "g.ecc"]},
        {"n": 7, "block": "home H: data phase (dap, da, da0, da1, de, dc) and LRU write",
         "action": "The 4 data macros (4096x144) read word {set, hit way}: one 144-bit word each, 576 bits; 8 SECDED checks; data OR'd out of the sub-bank to the L3-slave response mux. The tag-state macro's second port writes the new LRU code. If the line's zero bit is set, the data macros are not accessed at all.",
         "latency": "2-cycle macro access + ECC + complete; the spec's whole L3 hit at the slave is 30 shire clocks", "energy": "zero line: data macros idle (l3.zero-state)",
         "circuit": [{"element": "ICG on the 4 data panels", "action": "opens (all four panels on a read)", "kind": "et-spec"},
                     {"element": "wordline driver in each panel", "action": "one wordline rises (which of 4,096 words: row/column split is u.macro-geometry)", "kind": "generic"},
                     {"element": "6T cells, bitline pairs, column mux, sense amps", "action": "144 bits per panel sensed", "kind": "generic"},
                     {"element": "8 x SECDED(72,64) decoders", "action": "check and correct", "kind": "et-spec widths; generic circuit"},
                     {"element": "tag-state write port", "action": "write driver flips the LRU bits of one row", "kind": "et-spec (write happens); generic (circuit)"}],
         "facts": ["l3.hit-way-read", "l3.panels", "l3.mru-write", "l3.zero-state", "l3.no-rbuf", "l3.spec-latency"]},
        {"n": 8, "block": "home H to R: reply over the mesh",
         "action": "AXI read response (512 data bits + ~12-22 control) through the VCFIFO down to the NoC, hops(R, H) links back, VCFIFO up at R.",
         "latency": "about 10 ns per hop; the 12 cycles/hop round trip counts steps 4 and 8 together", "energy": "about 69 pJ per line per hop on the mesh rail for random data (l3.wire-energy); 47-59 pJ measured (l3.energy-per-load)",
         "circuit": [{"element": "link repeaters (inverter pairs)", "action": "toggle with the data; zeros do not toggle", "kind": "generic"},
                     {"element": "router buffers and crossbar", "action": "forward the 512-bit beat", "kind": "generic"}],
         "facts": ["l3.flits", "l3.wire-energy", "l3.mesh-rail"]},
        {"n": 9, "block": "requester's bank: return and L2 fill; L1 fill",
         "action": "The data goes to the neighbourhood through the response crossbar before the fill; the L2 fill writes tag, tag-state and 4 data panels (none if the line is all zeros), possibly evicting a victim over to_l3 to its own home; the L1 fills and the load retires.",
         "latency": "whole load: 110.5 + 11.99 x hops cycles (109 at 0 hops, 218 at 9)", "energy": "14.7 pJ/B for the whole L3 access (energy manual); 7.6 on zeros, 19.3 random (aifoundry2)",
         "circuit": [{"element": "data-panel write drivers + wordline", "action": "one bitline of each pair pulled low; cells flip where the bit changes", "kind": "generic (et-spec: WA/WPULSE trims exist)"}],
         "facts": ["l3.lat-fit", "l3.lat-by-home", "l3.energy", "l3.energy-contents", "g.write"]},
    ],
    "store": [
        {"n": 1, "block": "scalar store (L1 write-back)", "action": "A store miss fetches the line as a load does (L1 write-allocate); the dirty line leaves the L1 and then the L2 later as an eviction. The L2 victim goes over to_l3 to its home.",
         "circuit": [], "facts": ["l3.write"]},
        {"n": 2, "block": "tensor store (write-around)", "action": "Quadwords coalesce in the requester's L2 coalescing buffer (32 entries per bank); when all four quadwords are present, or on a flush or eviction, the line goes over to_l3 to the home.",
         "circuit": [], "facts": ["l3.writearound"]},
        {"n": 3, "block": "home H: L3 write", "action": "Tag and tag-state read; a miss installs the line with dirty bits for the written quadwords (no fill for whole quadwords); a hit on a clean line marks all four dirty; only the panels of written quadwords are enabled; an all-zero full line sets the zero bit and writes no data panel.",
         "circuit": [{"element": "data-panel write drivers, only for enabled quadwords", "action": "pull one bitline per column low; cell flips", "kind": "et-spec (panel select); generic (circuit)"},
                     {"element": "tag and tag-state write", "action": "one row each", "kind": "generic"}],
         "facts": ["l3.write", "l3.panels", "l3.zero-state"]},
    ],
    "miss_and_refill": [
        {"n": 1, "block": "home H: tag compare misses", "action": "The LRU code picks a victim way; the request queue sends a read over the single to_sys port to memory shire PA[8:6].",
         "latency": "spec: L3 miss 42 shire clocks + NoC and memory", "facts": ["l3.miss-path", "l3.spec-latency"]},
        {"n": 2, "block": "memory shire and DRAM", "action": "See the DRAM level.", "latency": "91 + 12 x hops(H, memory shire) cycles measured", "facts": ["l3.dram-leg"]},
        {"n": 3, "block": "home H: L3 fill", "action": "The fill reads the victim (if dirty it is written back over to_sys) and writes tag, tag-state and the 4 data panels in reserved bubble cycles; an all-zero line sets the zero bit instead of writing the panels. The home then answers the requester as in the load's step 8.",
         "latency": "a fill with a victim holds the sub-bank 4 cycles (2-cycle RAMs)",
         "circuit": [{"element": "data panels", "action": "read (victim) then write (new line)", "kind": "et-spec (sequence); generic (circuit)"}],
         "facts": ["l3.ram-delay", "l3.zero-state", "l3.miss-path"]},
        {"n": 4, "block": "partial line", "action": "A read that hits a partial line (left by write-arounds) first writes it to memory, then reads the full line back.",
         "facts": ["l3.partial"]},
    ],
    "atomic": [
        {"n": 1, "block": "home H: atomic block of bank PA[12:11]", "action": "Read the line, apply the operation (32/64/256-bit), write it back; the sub-bank is held busy across the three.",
         "latency": "10.00 cycles per contended atomic; 216-cycle uncontended round trip", "energy": "3.99 W over idle: 24% SRAM, 33% mesh", "facts": ["l3.atomic", "l3.atomic-rails"]},
    ],
    "refresh": [
        {"n": 1, "block": "none", "action": "No refresh: the spec describes none for the shire-cache RAMs (only deep sleep and shutdown for idle shires), and a 6T SRAM cell needs none. The static cost is leakage, at most 19.6 mW per MB at 80 C.",
         "facts": ["l3.no-refresh", "g.no-refresh", "l3.leakage"]},
    ],
}

# ---------------------------------------------------------------- asks for the hub
ASKS = [
    {"id": "ask-l3-bitcell", "facts": ["u.bitcell", "l3.macros", "l3.vendor"],
     "question": "The lab lead said the chip does not use SRAM. The Shire Cache Specification (pdf p.48: 'SRAM memory panels'; pdf p.51: Synopsys-named 1PUHD/2PUHDRF macros) and the datasheet (140 MB of on-die SRAM) say the L2/L3/scratchpad arrays are SRAM. Which memories did he mean are not SRAM (the minion L1's custom 1R1W 'lram' arrays? the latch-based register files? Ainekko's FPGA build?), and what bitcell do the shire-cache macros use (6T high-density, 8T, something else)?",
     "settles": "Whether the L3 diagram's storage cell is drawn as a 6T SRAM cell (now GENERIC) or as something else, with its own read and write sequence.",
     "hub_overlap": "ask-design-docs (a new document: the memory-compiler datasheet or a one-line answer)"},
    {"id": "ask-l3-macro", "facts": ["u.macro-geometry"],
     "question": "For the data macro saduls0g4l1p4096x144m4b4 (and the tag 1024x116 and tag-state 1024x40 macros): how many wordlines and bitline pairs, what column-mux ratio, how many internal banks, and what sense amplifier? Is 'm4b4' a 4:1 mux and 4 banks?",
     "settles": "How many wordlines, bitlines and sense amplifiers one L3 access switches, so the array view can be drawn to scale instead of as an illustration.",
     "hub_overlap": None},
    {"id": "ask-l3-live-esrs", "facts": ["u.live-settings", "l3.trim-reset", "l3.rail-vs-trim"],
     "question": "What do sc_pipe_ctl (esr_sc_ram_delay, esr_sc_zero_state_enable) and shire_cache_ram_cfg1/2 (RM, RME, RA, WA, WPULSE) hold on these cards at the 705 mV SRAM rail? A service-processor read of one shire would do.",
     "settles": "The number of cycles each macro access is drawn with (2 by default), whether zero lines skip the data array on these cards, and which assist settings the circuit view shows.",
     "hub_overlap": "ask-lab-root / a management command (these are M-mode ESRs)"},
    {"id": "ask-l3-rails", "facts": ["u.rail-of-logic", "l3.hv-region"],
     "question": "Which rail feeds the shire cache's logic (pipeline, crossbars, request queues, high side of the VCFIFOs): the metered 705 mV SRAM rail with the macros, or another? (The Power Spec's minion-shire section.)",
     "settles": "The colour of each block in the L3 diagram and how the SRAM rail's energy per byte is split between arrays and logic.",
     "hub_overlap": "ask-design-docs (Power Spec)"},
    {"id": "ask-l3-latency", "facts": ["u.latency-split", "l3.lat-reconcile", "l3.lat-clock-split"],
     "question": "Stage by stage, where do the 110 cycles of a local L3 hit go, in particular the 61 ns that do not scale with the core clock (VCFIFO synchronisers, NoC bridges, mesh-stop entry and exit)? The spec's Table 1 (34 + 30 shire clocks) is about 18 cycles more than the 72 clock-scaled cycles measured.",
     "settles": "The latency label on each step of the L3 access animation (now only the total and the per-hop cost are measured).",
     "hub_overlap": "ask-noc-docs"},
    {"id": "ask-l3-lane", "facts": ["l3.lane"],
     "question": "Does the taped-out RTL pick an L3 request's to_l3 lane by the home bank (PA[12:11] under swizzle0), as core-et-main's shirecache_mesh_master.sv:132-153 does, with PA[7:6] only for remote scratchpad?",
     "settles": "Which of the four mesh lanes an L3 access is drawn on (and corrects chip fact L103 for L3 traffic).",
     "hub_overlap": None},
    {"id": "ask-l3-noc", "facts": ["u.noc-hop", "l3.hop-noc-cycles", "l3.route"],
     "question": "Per hop, how many NoC cycles does a router take, which of the nine main-NoC layers carry L3 read requests and replies, and do they route x first?",
     "settles": "The mesh-hop animation: router pipeline stages, layer and path of the request and the reply.",
     "hub_overlap": "ask-noc-docs, exp-route-order"},
    {"id": "ask-l3-zero", "facts": ["u.zero-share", "l3.energy-rails", "l3.zero-state"],
     "question": "Is the L3's 2.6x lower SRAM-rail energy on zeros mostly the zero-state skip of the data macros? Could we clear esr_sc_zero_state_enable on one card for one run (needs an M-mode ESR write) to measure it?",
     "settles": "Whether the diagram shows the data array idle for zero lines and puts the rest of the data-dependent energy in the datapath and wires.",
     "hub_overlap": "a new experiment rung (needs a firmware or debug path)"},
    {"id": "ask-l3-floorplan", "facts": ["u.slice-floorplan"],
     "question": "Where do the four cache banks sit in the shire tile relative to the mesh stop and its four L3-slave ports?",
     "settles": "The distance an L3 request travels inside the home shire, drawn to scale.",
     "hub_overlap": "ask-shire-floorplan"},
]

out = {
    "meta": {
        "level": "L3",
        "built": "2026-09-27",
        "builder": "build_facts_l3.py (beside this file)",
        "roots": {"docs/, workloads/": "the repository root",
                  "external/": "the et-soc1-prototyping checkout's external/"},
        "pdf_pages": "pdf page numbers from pdftotext page breaks",
        "kinds": {},
        "n_facts": 0,
        "caveat": "core-et-main (external/core-et-main/hw/ip/shirecache) is Ainekko's 2026 co-simulated translation of the CORE-ET RTL; facts citing it are et-spec with that caveat.",
    },
    "facts": F,
    "access_sequence": SEQ,
    "asks": ASKS,
}
ids = [f["id"] for f in F]
assert len(ids) == len(set(ids)), "duplicate ids"
known = set(ids)
for part in SEQ.values():
    if isinstance(part, list):
        for s in part:
            for fid in s.get("facts", []):
                assert fid in known, fid
for a in ASKS:
    for fid in a["facts"]:
        assert fid in known, fid
from collections import Counter
out["meta"]["kinds"] = dict(Counter(f["kind"] for f in F))
out["meta"]["n_facts"] = len(F)
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print(OUT, len(F), out["meta"]["kinds"])
