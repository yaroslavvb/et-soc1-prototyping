#!/usr/bin/env python3
"""Facts for the L1 level (minion data cache + L1 scratchpad) of the memory-anatomy diagrams.

Output: ../facts-l1.json, a JSON list. Two kinds of rows share the list:
  - facts:            topic does not start with "sequence/"
  - access sequences: topic "sequence/<name>", with extra fields step, stage, block, action, circuit,
                      circuit_kind, latency, energy (all other fields as for facts).
kind: et-spec | et-measured | et-derived | generic | unknown.
Paths: "external/..." is under the et-soc1-prototyping checkout; "docs/..." and "workloads/..." are the
nekko repo (pages worktree). PDF pages are physical pdf pages; "text L" is the line in `pdftotext -layout` output.
"""
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'facts-l1.json')

DC = 'external/core-et/docs/Minion DCache Description.pdf'
MD = 'external/core-et/docs/Minion Description.pdf'
FEI = 'external/core-et/docs/FE-Intpipe-Description.pdf'
MAS = 'external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf'
SCS = 'external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf'
DS = 'external/et-man/ET Preliminary Datasheet Rev 1.0.pdf'
PRM = "external/et-man/ET Programmer's Reference Manual.pdf"
MOV = 'external/et-man/ET Minion Overview.pdf'
RTL = 'external/core-et/rtl/'
RTLM = 'external/core-et-main/'
EM4 = 'docs/energy-manual/04-bytes-memory.md'
EM4A = 'docs/energy-manual/04a-fine-grain.md'
LAT = 'docs/reports/data/2026-09-25-claims-v3/results/lat.json'

P_MH = 'https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy#the-hierarchy-as-a-spec-sheet'
P_EM = 'https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#reads-and-writes-measured-together'
P_EMG = 'https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual'
P_AN = 'https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#trace-one-load'
P_DV = 'https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'
P_HX = 'https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment'
P_CD = 'https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram'
P_LO = 'https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability'

CARDS3 = 'aifoundry2, aifoundry3, aifoundry1-c1'
rows = []


def F(id, topic, statement, value, unit, source, kind, card=None, page_link=None, note=None):
    assert kind in ('et-spec', 'et-measured', 'et-derived', 'generic', 'unknown'), kind
    rows.append(dict(id=id, level='L1', topic=topic, statement=statement, value=value, unit=unit, source=source,
                     kind=kind, card=card, page_link=page_link, note=note))


# ---------------------------------------------------------------- organisation
F('l1.size', 'organisation',
  'Each minion has a private 4 KB L1 data cache: 16 sets x 4 ways x 64-byte lines (set = PA[9:6]).',
  4, 'KB per minion',
  f'{DS}, pdf p.9 (§2.1.1.5, text L341-345); {DC}, pdf p.29 (§3.2, text L1266); '
  f'{RTL}inc/minion_defines.vh:125,143 (DCACHE_SETS 16, DCACHE_WAYS 4); {RTL}inc/dcache_defines.vh:27 (line 64 B)',
  'et-spec', page_link=P_MH)
F('l1.lram', 'array technology',
  'The data array is not SRAM: it is built from latch RAM, "4 LRAM (Latch-RAM) blocks of 128 rows and 64 bits per row", '
  'each block with a single read port and a single write port.',
  4, 'LRAM blocks of 128 x 64 bit',
  f'{DC}, pdf p.29 (§3.2, text L1269-1271) and glossary pdf p.61 ("LRAM Latch Random Access Memory"); '
  f'{DS}, pdf p.9 (§2.1.1.5, text L346)',
  'et-spec', page_link=None,
  note='Answers the lab lead\'s "not SRAM" for the L1: latch RAM. Both the design doc and the public datasheet say so.')
F('l1.lram-macros', 'array technology',
  'In the RTL each 128 x 64 block is a wrapper of two 128 x 32 one-read-one-write LRAM macros (low and high 32-bit '
  'halves) with their own read and write enables: 8 macros (dcache_128x32_1r1w_lram) per minion.',
  8, 'macros of 128 x 32 bit per minion',
  f'{RTL}shire/minion/dcache/dcache_data_ram_wrap.v:4-52; {RTL}shire/minion/dcache/dcache_data_array.v:119-136; '
  f'{RTL}inc/dcache_defines.vh:50-56',
  'et-spec')
F('l1.lram-model', 'array technology',
  'The released LRAM macro is only a behavioural model ("One-read, one-write register file ... synchronous write, '
  'synchronous read"); the cell-level design of the silicon macro is not in the open release.',
  None, None,
  f'{RTL}libs/macros/dcache_128x32_1r1w_lram.v:5-8, 44-64',
  'et-spec', note='See unknown l1.u-cell. The port list (clk, rd/wr enable, 7-bit rd/wr address, 32-bit data) is all '
  'the model fixes.')
F('l1.latch-rf', 'array technology',
  'The ET latch register-file library ("Latch based Register Files with registered read output") shows the write '
  'and read mechanism these arrays use: write data is captured by a low-phase latch clocked by a negative clock '
  'gate one phase before the write; the decoded write address enables one per-row clock gate; that row\'s latches '
  'are transparent while its gated clock is high; the read address is registered on the rising edge and the read '
  'is a combinational select rf[rd_addr_reg] (no bitline, no sense amplifier in the model).',
  None, None,
  f'{RTL}libs/rf_latches/rf_latch_1r_1w_reg.v:4-52 (timing diagram and notes), 88-96 (write-data latch), '
  f'101-136 (per-row clock gates and latches), 139-149 (registered read address, combinational read)',
  'et-spec',
  note=f'core-et-main maps the D-cache LRAM wrappers to exactly this contract, "preview-plus-registered-read RF" '
  f'({RTLM}docs/latch_translation.md:55-56, 93-96; {RTLM}hw/ip/minion/dcache/rtl/minion_dcache_128x64_1r1w_lram.sv:35-63). '
  f'Whether the silicon macro is this library cell-for-cell is unknown (l1.u-cell).')
F('l1.icg-cells', 'array technology',
  'The clock gates of the latch arrays are standard cells when the ASIC cell switch is on: HDBULT08_CKGTPLT_V7Y2_2 '
  '(rising-edge gate, per row) and HDBULT08_CKGTNLT_V5Y2_2 (falling-edge gate, write-data latch). Other cells named '
  'in the RTL come from HDBULT08_* and HDBULT11_* families.',
  None, None,
  f'{RTL}libs/rf_latches/et_clk_gate.v:14-18; {RTL}libs/rf_latches/et_clk_gate_n.v:14-18; '
  f'{RTL}inc/libs_defines.vh:8-9 (switch off in the open release: "Standard cells not available")',
  'et-spec', note='Library vendor, track height and threshold flavour are not stated (l1.u-library).')
F('l1.lram-addr', 'organisation',
  'LRAM row address = {set[3:0], half-line bit, way[1:0]} = {addr[9:5], way[1:0]}: 7 bits, 128 rows. Address bits '
  '[4:3] choose the block (8 bytes each); one row across the 4 blocks is 32 bytes, half a line; a 64-byte line '
  'occupies 2 rows, and the 4 ways of a half-line sit in 4 adjacent rows.',
  128, 'rows per block',
  f'{DC}, pdf p.29-30 (§3.2, text L1276-1296, Figure 10); {DS}, pdf p.10 (Figure 2-3); '
  f'{RTL}shire/minion/dcache/dcache_data_array.v:46-50',
  'et-spec')
F('l1.bank-enables', 'organisation',
  'Only the blocks a load needs are read: a scalar load enables the one block whose addr[4:3] matches (both of its '
  '32-bit halves); a 32-byte packed-single (PS) vector load enables all four; a misaligned access also reads the next '
  'row in the following blocks.',
  None, None,
  f'{RTL}shire/minion/dcache/dcache_top.v:2123-2147; {DS}, pdf p.10 (text L352-361, worked examples)',
  'et-spec', note='A 4-byte flw still reads the whole 64-bit block row: valid_h = valid_l (dcache_top.v:2141; '
  'the RTL comment at :2459 reads "OPTIMIZE, check if it can be split").')
F('l1.phased', 'access pipeline',
  'Tag first, then data: in S1 the physical tag is compared with all 4 ways (four comparators) and the hit way is '
  'encoded; the S2 data read then reads only that way\'s row, because the way is part of the LRAM row address.',
  4, 'tag comparators per access',
  f'{RTL}shire/minion/dcache/dcache_top.v:2108-2121 ("CAM for the tags"), 2145; '
  f'{RTL}shire/minion/dcache/dcache_data_array.v:49-50; {DC}, pdf p.24-25 (§3.1.2-3.1.3)',
  'et-spec', note='GENERIC: a serial tag-then-data cache reads one way instead of four, at the cost of a pipeline stage.')
F('l1.metadata', 'organisation',
  'Metadata: 64 entries (16 sets x 4 ways) of tag PA[39:7] (33 bits) + 2-bit line state = 35 bits, held in four '
  'latch register files (one per way, 16 entries, read in the same cycle); the 64 valid bits are flip-flops.',
  35, 'bits per entry',
  f'{DC}, pdf p.31 (§3.3, text L1350-1361) and pdf p.57 (§3.12.1, text L2457-2458); '
  f'{RTL}shire/minion/dcache/dcache_metadata_array.v:39-65 (rf_latch_1r_1w per way, valid in RST_EN_FF); '
  f'{RTL}inc/dcache_types.vh:183-187; {RTL}libs/rf_latches/rf_latch_1r_1w.v:49-50 ("read latency = 0")',
  'et-spec')
F('l1.states', 'coherence',
  'Line states: invalid 00, shared 01 (never assigned: there is no coherence at this level), exclusive 10 (after a '
  'fill for a read), modified 11 (after a fill for a write, or a store to a clean line).',
  None, None, f'{DC}, pdf p.31 (text L1359-1361) and pdf p.35 (text L1491-1509)', 'et-spec')
F('l1.noncoherent', 'coherence',
  'The L1 data caches are not coherent: software moves lines with cache operations (EvictVA, FlushVA, PrefetchVA, '
  'lock/unlock) and fences.',
  None, None, f'{MOV}, pdf p.1 (text L7 "Non-coherent"); {DC}, pdf p.31 (text L1361); {PRM}, pdf p.243-244 (§8.1, '
  'text L5872-5923)', 'et-spec', page_link=P_MH)
F('l1.write-policy', 'write policy',
  'Write-back, write-allocate: a cacheable store that misses fetches the line (miss handler fill) and marks it '
  'modified; a dirty victim is evicted to the L2 as 512 bits in two 256-bit transfers, reading the LRAM 256 bits a '
  'cycle.',
  512, 'bits per evict',
  f'{DC}, pdf p.21 (text L776-781), pdf p.33 (§3.5, text L1404-1407), pdf p.35 (text L1491-1509)', 'et-spec')
F('l1.store-rmw', 'write policy',
  'Every store is a read-modify-write of the array: the row is read in S2, the new bytes are aligned and merged in '
  'S3, and the merged row is written through the write port in S4.',
  None, None, f'{DC}, pdf p.25 (text L955-957), pdf p.27 (§3.1.5, text L1116-1129)', 'et-spec')
F('l1.lru', 'replacement',
  'Replacement is LRU: 16 bits per set (a 4 x 4 order matrix), in flip-flops, updated in S2 on every cacheable access; '
  'hard- and soft-locked ways are excluded when choosing the victim.',
  16, 'LRU bits per set',
  f'{RTL}inc/dcache_defines.vh:31; {RTL}shire/minion/dcache/dcache_lru_array.v (RST_EN_FF per set); '
  f'{RTL}shire/minion/dcache/dcache_top.v:2722-2744, 3150-3159; {DC}, pdf p.25 (text L954)', 'et-spec')
F('l1.pipeline', 'access pipeline',
  'Six DCache stages, locked to the integer pipeline: pre-S0 = ID (arbitration bids), S0 = EX (address, grant), '
  'S1 = TAG (TLB, metadata read, tag match, PMA, data-array address), S2 = MEM (data-array read, hit/miss, replay '
  'queue, miss handler), S3 = WB (align, sign-extend, return to core or VPU), S4 (data-array write port), S5 (store '
  'data bypass to S3).',
  6, 'stages',
  f'{DC}, pdf p.22 (Figure 3), pdf p.23-28 (§3.1.1-3.1.6); {FEI}, pdf p.9 (§3.1, text L201-212), pdf p.12 (text '
  'L224-227)', 'et-spec')
F('l1.s0-arb', 'access pipeline',
  'Pre-S0 priority, high to low: cache-ops metadata read, debug, write-back unit (reads the data array), replay '
  'queue, cache-ops L1 prefetch, core intpipe. The VPU scratchpad read, Reduce, TensorLoad and cache-op prefetch '
  'can also take S0.',
  6, 'bidders',
  f'{DC}, pdf p.24 (§3.1.1, text L839-857)', 'et-spec')
F('l1.s4-arb', 'access pipeline',
  'One write port per block, static priority: stores in S4, fills from the SEND port, L2 fills from the miss '
  'handlers, TensorLoad transformation writes, configuration clear, cache-ops clear, debug. A fill may write only if '
  'there is no store and the read port was not granted in the previous cycle.',
  7, 'write-port clients',
  f'{DC}, pdf p.27 (§3.1.5, text L1116-1129)', 'et-spec')
F('l1.mh', 'miss handling',
  'Two miss handlers per minion (DCACHE_MH_FILE_SIZE = 2, the only verified value): at most two outstanding '
  'cacheable line misses; a later access to a line already being filled joins the same handler.',
  2, 'miss handlers',
  f'{DC}, pdf p.34-35 (§3.6, text L1449-1480); {RTL}inc/dcache_defines.vh:79', 'et-spec')
F('l1.rq', 'miss handling',
  'Replay queue of 8 entries, pre-allocated at ID; a missing or rejected instruction waits there and re-enters the '
  'pipeline; when it is full the core is told id_core_ready = 0.',
  8, 'entries',
  f'{DC}, pdf p.38 (§3.7, text L1634-1649); {RTL}inc/minion_defines.vh:151', 'et-spec')
F('l1.tlb', 'address translation',
  'An 8-entry TLB (a latch register file) translates in S1 (4 KB, 2 MB and 1 GB pages); the neighbourhood document '
  'notes that "Virtual Memory logic is unused in A0".',
  8, 'TLB entries',
  f'{RTL}inc/dcache_defines.vh:105; {RTL}shire/minion/tlb_top.v:277-285; {DC}, pdf p.15 (§2.4.1); {MAS}, pdf p.6 '
  '(footnote 1, text L143)', 'et-spec',
  note='workloads/memprobe/README.md treats kernel addresses as physical ("offset bits are physical address bits").')
F('l1.vpu-port', 'ports',
  'The array feeds one 256-bit register-file entry of all 8 VPU lanes per cycle (DCACHE_DATA_SIZE 256).',
  32, 'B per cycle',
  f'{MD}, pdf p.6 (text L84-85); {RTL}inc/minion_defines.vh:106', 'et-spec', page_link=P_MH)
F('l1.vpu-scp-read', 'ports',
  'The VPU reads the scratchpad directly: its request in S1 pre-empts any other S1 operation (sent to the replay '
  'queue), no tag check is made, and the 256 bits are delivered in S3, two cycles later (one extra register stage '
  'for timing).',
  2, 'cycles',
  f'{DC}, pdf p.12-13 (§2.3, §2.3.1, text L416-451, Figure 1)', 'et-spec')

# ---------------------------------------------------------------- modes and scratchpad
F('l1.modes', 'modes',
  'Three modes (mcache_control D1Split, ScpEnable): shared (both harts, all 16 sets); split (hart 0 sets 0-7, hart 1 '
  'sets 14-15, sets 8-13 unused); scratchpad (hart 0 sets 12-13, hart 1 sets 14-15, sets 0-11 = 48 lines = 3 KB of '
  'tensor scratchpad, hart 0 only).',
  3, 'KB scratchpad',
  f'{PRM}, pdf p.245-246 (§8.3.1, Table 8.4, text L5977-6010); {RTL}inc/dcache_defines.vh:130 (DCACHE_TL_SCP_MAX_IDX 48)',
  'et-spec', page_link=P_MH,
  note='The Minion Overview slide draws split mode as 2 KB per hart; the PRM table is followed here.')
F('l1.scp-impl', 'modes',
  'Scratchpad mode is implemented in the same array: two more tag bits are kept and the two set MSBs are forced to '
  '11, so the cache uses only sets 12-15; changing ScpEnable drains the pipeline, writes zeros into every line of '
  'sets 0-13 and invalidates their metadata.',
  None, None,
  f'{DC}, pdf p.30-31 (§3.2.1, text L1318-1347); {PRM}, pdf p.246 (text L6012-6019); '
  f'{RTL}shire/minion/dcache/dcache_metadata_array.v:92-108 (cfg_clear_low)', 'et-spec')
F('l1.firmware-mode', 'modes',
  'The firmware sets D1Split and ScpEnable before every launch, so a kernel runs with 512 B of L1 cache per hart '
  '(2 sets x 4 ways x 64 B) and a 3 KB scratchpad.',
  512, 'B per hart',
  'docs/et-soc1-notes.md:84-86; docs/research/counters-and-dram.md:447 (fw MachineMinion/src/syscall.c:348-420)',
  'et-spec', page_link=P_MH)
F('l1.knee', 'modes',
  'The measured knee confirms 512 B per hart: hart 1 reads 5.25 cycles at 256 B, 5.256 at 512 B and 39.0 at 768 B '
  '(a miss to the L2 read buffer), in every pass on three cards.',
  512, 'B',
  f'{LAT}: items[LAT-M1].per_card.<card>.passes[].hart1', 'et-measured', card=CARDS3, page_link=P_MH)
F('l1.tensorload', 'scratchpad',
  'TensorLoad (unit TL0) writes L2 responses straight into scratchpad rows through the write port; TensorLoadB (TL1) '
  'skips the array and fills a 4-entry VPU buffer under 4 (up to 6) credits; up to 4 L2 transfers are in flight; '
  'transposes and interleaves stage through a 128-byte buffer and write the LRAM in 8-byte chunks.',
  4, 'L2 transfers in flight',
  f'{DC}, pdf p.15 (§2.3.4), pdf p.40-43 (§3.9.1-3.9.2); {RTL}inc/dcache_defines.vh:108', 'et-spec', page_link=P_HX)
F('l1.tl-latency', 'scratchpad',
  'One minion\'s TensorLoad into its L1 scratchpad: 16 lines (1 KB) take 160.4 cycles from the L2 and 160.1 from '
  'the own scratchpad; 8 lines 80.1; 4 lines 41.9 cycles; the same on three cards.',
  160.4, 'cycles for 16 lines',
  f'{LAT}: items[LAT-S2].per_card.<card>.pass_means.l216, .l28, .l24, .scp16', 'et-measured', card=CARDS3,
  page_link=P_HX)
F('l1.tl-rate', 'scratchpad',
  'About 10 cycles per 64-byte line into the scratchpad (6.4 B per cycle): what 4 transfers in flight over a round trip '
  'of about 40 cycles allow.',
  10.0, 'cycles per line',
  f'derived from {LAT} LAT-S2 (160.4 / 80.1 / 41.9 cycles for 16 / 8 / 4 lines) and {RTL}inc/dcache_defines.vh:108',
  'et-derived', card=CARDS3,
  note='Little\'s law with the RTL constant; the round trip itself is not separately measured.')

# ---------------------------------------------------------------- physical / electrical
F('l1.lv-region', 'physical',
  'The eight minions of a neighbourhood sit in its low-voltage (LV) region with their own clock; the neighbourhood '
  'says the memory cells of its ICache data RAMs "need to be placed in an HV region", so those RAMs were moved out '
  'into the shire channel.',
  None, None,
  f'{MAS}, pdf p.6 (§2, text L108-112), pdf p.7 (§2.2, text L150-154), pdf p.14 (§4.2, text L511-518)', 'et-spec')
F('l1.why-latch', 'array technology',
  'Why latches: the data cache sits inside the minion, in the LV region, where by the neighbourhood document the '
  'chip\'s SRAM cells cannot be placed; a latch array is ordinary logic and runs on the minion supply.',
  None, None,
  f'combines l1.lram ({DC} pdf p.29) and l1.lv-region ({MAS} pdf p.14)', 'et-derived',
  note='The documents never state this rationale for the data cache; it is our inference (l1.u-why).')
F('l1.icache-sram', 'array technology',
  'Contrast at the same level: the neighbourhood\'s L1 instruction cache data RAM is modelled as a "512 x 144-bit '
  'synchronous SRAM", placed in the HV region; and the shire cache (L2/L3/scratchpad) is "SRAM memory panels that '
  'are 144 bits wide".',
  None, None,
  f'{RTL}libs/macros/icache_data_ram.v:4; {MAS}, pdf p.14 (text L511-518); {SCS}, pdf p.48 (text L1929)', 'et-spec')
F('l1.rail', 'power',
  'The L1 is powered from the minion rail (VDD_MNN), not the SRAM rail (VDD_SRAM, the shire-cache arrays): an L1-hit '
  'loop puts 83% of its power over idle on the minion rail and 2% on the SRAM rail; on 19 September an 8-byte ld '
  'L1 hit cost 40.7 pJ on the minion rail and 1.3 pJ on the SRAM rail.',
  83, '% on minion rail',
  f'{EM4A}:168; docs/reports/data/2026-09-19-memprobe-aifoundry2/power/summary.json: summary.l1.pj_per_load '
  f'(minion 40.74, sram 1.33, noc 0.56, board 56.47); docs/research/power-telemetry.md:14, 44, 46', 'et-measured',
  card='aifoundry2', page_link=P_EMG)
F('l1.voltage', 'power',
  'The latch arrays switch at the minion-rail voltage: 0.517 V at 600 MHz (0.568 V at 700, 0.618 V at 800); the '
  'card\'s nominal minion rail is 400 mV, and the SRAM rail is 750 mV.',
  0.517, 'V at 600 MHz',
  'docs/findings/16-dvfs-and-leakage.md:20; docs/research/power-telemetry.md:44, 46 (ET-PCIe-Dev-Card-V3)',
  'et-measured', card='aifoundry2, aifoundry3', page_link=P_DV)
F('l1.no-sleep', 'power',
  'The minion\'s sleep and isolation ports (nsleepin, iso_enable, nsleepout) are marked "not used", and no firmware '
  'drives them: the L1 arrays are always powered, with no retention or wake-up state.',
  None, None,
  f'{MD}, pdf p.7 (text L126-133); docs/findings/16-dvfs-and-leakage.md:23', 'et-spec', page_link=P_DV)
F('l1.no-parity', 'reliability',
  'No parity or ECC appears in the open data-cache RTL: each LRAM row is 64 data bits (core-et-main\'s 128 x 72 '
  'variant is instantiated nowhere).',
  0, 'check bits',
  f'{RTL}shire/minion/dcache/dcache_data_array.v:18-20; {RTLM}hw/ip/minion/dcache/rtl/minion_dcache_data_array.sv:85',
  'et-derived', note='Absence in the open RTL; the silicon is not confirmed (l1.u-parity).')
F('l1.bits', 'organisation',
  'Storage per minion: 32,768 data bits in latch RAM, 2,240 tag and state bits in latch register files, 64 valid and '
  '256 LRU flip-flops. Over 1,088 minions that is 35.7 Mbit (4.25 MB) of latch-RAM data.',
  32768, 'data bits per minion',
  'derived from l1.size, l1.metadata, l1.lru', 'et-derived')
F('l1.transistors', 'array technology',
  'Estimate: at 8-12 transistors per latch bit, the data array holds about 0.26-0.39 million storage transistors per '
  'minion (0.29-0.43 billion on the chip, 1.2-1.8% of its >24 billion), against 0.2 million for the same 4 KB in 6T '
  'SRAM.',
  0.33, 'million transistors per minion (mid)',
  'l1.bits x GENERIC transistors per bit; chip total from docs/findings/01-resources.md:101', 'generic',
  note='GENERIC count per bit; the real latch cell is unknown (l1.u-cell). Excludes decoders, clock gates and read muxes.')

# ---------------------------------------------------------------- latency and bandwidth (measured)
F('l1.latency', 'latency',
  'L1 hit: 5.25 cycles load-to-use in a dependent pointer chase (8.75 ns at 600 MHz), per-pass ranges 5.247-5.259, '
  'in every pass on three cards.',
  5.25, 'cycles',
  f'{LAT}: items[LAT-M1].per_card.<card>.passes[].L1; docs/findings/05-claims.md:421', 'et-measured', card=CARDS3,
  page_link=P_MH)
F('l1.latency-5', 'latency',
  'A dependent L1 load issues 5 cycles after the previous one: ID, EX, TAG, MEM, WB (data leaves S3 at WB) and the '
  'next ID. The 0.25 cycle in 5.25 fits 2 cycles of loop overhead per 8 unrolled loads; the anatomy page sets an L1 '
  'hit to 5 cycles.',
  5, 'cycles',
  f'{FEI}, pdf p.9 (text L201-208), pdf p.12 (text L234-235: "DCache data is available at the WB stage or later"); '
  'workloads/memhier/kernel/memhier.c:36-44; workloads/memprobe/README.md ("offset chosen so an L1 hit reads the 5 '
  'cycles")', 'et-derived', page_link=P_AN,
  note='Stage-by-stage timing is inferred from the documents; no probe times a single stage (l1.u-cycles).')
F('l1.miss-l2', 'latency',
  'When the load misses the L1: 36 cycles if the line is in the L2 read buffer, 47 if it is in the L2 or the own '
  'scratchpad; hart 1 pays 3 more (39 and 50).',
  47, 'cycles',
  f'{LAT}: items[LAT-M1].per_card.<card>.passes[] (RB, L2, hart1)', 'et-measured', card=CARDS3, page_link=P_MH,
  note='The L1\'s own share of these cycles (miss detection, miss handler, fill write, replay) is not measured apart.')
F('l1.bw', 'bandwidth',
  'L1 bandwidth: 14.5 TB/s over the chip with 32-byte vector loads on both harts (23.6 B per minion-cycle of the 32 '
  'designed); 6.2 TB/s in the memory-hierarchy probe\'s loop.',
  14.49, 'TB/s',
  f'{EM4}:11 (14,488 GB/s); docs/findings/05-claims.md:380 (6.2 TB/s)', 'et-measured', card=CARDS3, page_link=P_EM)

# ---------------------------------------------------------------- energy (measured, three cards)
F('l1.e-vload', 'energy',
  'One 32-byte vector load (flw.ps) that hits the L1: 0.54 pJ/B on random data [0.52-0.56] = 17.3 pJ per load '
  '(aifoundry2 17.6, aifoundry3 17.3, aifoundry1-c1 16.6); 0.39 pJ/B on zeros = 12.5 pJ per load. Above idle, '
  'including the instruction.',
  17.3, 'pJ per 32 B load',
  f'{EM4}:11', 'et-measured', card=CARDS3, page_link=P_EM)
F('l1.e-vstore', 'energy',
  'One 32-byte vector store (fsw.ps) that hits the L1: 0.72 pJ/B on random data [0.66-0.81] = 23.0 pJ per store '
  '(aifoundry2 23.4, aifoundry3 23.0, aifoundry1-c1 22.7); 0.41 pJ/B on zeros = 13.1 pJ.',
  23.0, 'pJ per 32 B store',
  f'{EM4}:12', 'et-measured', card=CARDS3, page_link=P_EM)
F('l1.e-scalar', 'energy',
  'Scalar 4-byte accesses that hit the L1 (512 B table per hart, all 1,024 minions): flw 14.0 pJ [13.4-14.5], fsw '
  '25.5 pJ [24.8-26.4]; the 8-lane gather fgw.ps 12.8 pJ and scatter fscw.ps 14.7 pJ per element.',
  14.0, 'pJ per scalar load',
  f'{EM4}:54, 67', 'et-measured', card=CARDS3, page_link=P_EMG)
F('l1.e-store-ratio', 'energy',
  'A store costs more than a load of the same size: 1.82x for scalar (25.5 / 14.0 pJ), 1.33x for 32-byte vectors '
  '(0.72 / 0.54 pJ/B), consistent with the store touching the array twice (S2 read, S4 write).',
  1.82, 'x (scalar store / load)',
  f'derived from {EM4}:11-12, 54 and l1.store-rmw', 'et-derived', card=CARDS3)
F('l1.e-memhier', 'energy',
  'L1 hits in the memory-hierarchy loop: 0.75 pJ/B [0.62-0.88] = 24.0 pJ per 32-byte load (aifoundry2 0.77, '
  'aifoundry3 0.75, aifoundry1-c1 0.72 pJ/B); the manual recommends the 0.54 figure.',
  0.75, 'pJ/B',
  f'{EM4}:21, 25; docs/reports/data/2026-09-23-energy-manual/manual.json (reruns.levels_pj_per_byte.l1)',
  'et-measured', card=CARDS3, page_link=P_EMG)
F('l1.e-19sep', 'energy',
  'First measurement, one card: an 8-byte ld that hits the L1 in the power loop cost 56.5 pJ at the board, 40.7 pJ '
  'on the minion rail, 1.3 on the SRAM rail, 0.6 on the mesh, at 11.0 cycles per load (superseded by the manual).',
  56.5, 'pJ per load (board)',
  'docs/reports/data/2026-09-19-memprobe-aifoundry2/power/summary.json: summary.l1', 'et-measured', card='aifoundry2',
  page_link=P_AN)
F('l1.e-fill', 'energy',
  'Filling one 64-byte line from the own scratchpad into the L1: 238 pJ on random data (aifoundry2 221, aifoundry3 '
  '223, aifoundry1-c1 271), 101 pJ on zeros; random data adds 269 fJ per bit on the path into the L1.',
  238, 'pJ per line',
  f'{EM4A}:44', 'et-derived', card=CARDS3, page_link=P_EMG,
  note='Difference of two measured stride rows, times 2.')
F('l1.e-per-bit', 'energy',
  'Per bit delivered, a 32-byte L1 load costs at most 68 fJ on random data and 49 fJ on zeros, of which random data '
  'adds 4.8 pJ per load, 19 fJ per bit; these bound the array from above (they include issue, pipeline and register '
  'write).',
  68, 'fJ per bit (upper bound)',
  f'derived from {EM4}:11', 'et-derived', card=CARDS3)

# ---------------------------------------------------------------- GENERIC circuit knowledge used by the diagrams
F('g.latch-cell', 'circuit',
  'A static CMOS D-latch (transmission-gate or clocked-inverter type) stores a bit on a pair of cross-coupled '
  'inverters with a clocked feedback path: about 8-12 transistors per bit, full-swing, no precharge, no sense '
  'amplifier, readable without disturbing the stored value.',
  10, 'transistors per bit (typical)', 'textbook CMOS (GENERIC)', 'generic')
F('g.latch-read', 'circuit',
  'A latch-array read is logic: the registered address drives a decoder or a mux tree (128:1 per output bit, e.g. '
  'seven 2:1 levels or four 4:1 levels), and only the nodes whose value changes spend energy, so read energy depends '
  'on the data.',
  None, None, 'textbook standard-cell memory design (GENERIC)', 'generic')
F('g.latch-write', 'circuit',
  'A latch-array write: the write-address decoder enables one row\'s integrated clock gate (a latch plus an AND, about '
  '10-16 transistors); its gated clock goes high and every latch in that row becomes transparent and takes the write '
  'bus, which an opposite-phase latch holds steady for the whole phase.',
  None, None, 'textbook latch register-file design (GENERIC); the opposite-phase write latch and per-row gates are '
  'the ET pattern in l1.latch-rf', 'generic')
F('g.sram-6t', 'circuit',
  'For contrast, a 6T SRAM cell: two cross-coupled inverters (4 transistors) and two NMOS access transistors on '
  'complementary bitlines. A read precharges the bitlines, the wordline driver raises one wordline, one bitline '
  'droops by a fraction of VDD and a sense amplifier resolves it through a column mux; the cell needs a minimum '
  'voltage for read stability and writability, which is why SRAM usually gets its own higher rail.',
  6, 'transistors per bit', 'textbook SRAM (GENERIC)', 'generic')
F('g.compare', 'circuit',
  'A tag comparator is one XNOR per bit (about 8-12 transistors) and an AND tree over the 33 bits; four run on every '
  'access, hit or miss.',
  None, None, 'textbook logic (GENERIC); four comparators and 33-bit tags from l1.phased, l1.metadata', 'generic')
F('g.flipflop', 'circuit',
  'The valid and LRU bits are edge-triggered flip-flops: two latches in master-slave, about 20-24 transistors each.',
  22, 'transistors per bit (typical)', 'textbook CMOS (GENERIC)', 'generic')
F('g.no-refresh', 'circuit',
  'Latches, like SRAM, hold data statically while powered: the L1 needs no refresh (unlike the DRAM level).',
  None, None, 'textbook (GENERIC)', 'generic')

# ---------------------------------------------------------------- unknowns (each becomes an ask)
U = []


def ASK(id, topic, question, settles, source):
    U.append(dict(question=question, settles=settles))
    F(id, topic, question, None, None, source, 'unknown', note='Settles: ' + settles)


ASK('l1.u-cell', 'array technology',
    'What is inside the dcache_128x32_1r1w_lram macro on silicon: standard-cell latches placed like the '
    'rf_latch_1r_1w_reg library, or a custom or compiled latch-array macro? Which latch cell (transistors per bit), '
    'and is the read a static mux tree or a precharged read bitline with a keeper or sense stage?',
    'the transistor-level panel of the L1 diagram, now drawn from the generic latch-RF template (l1.latch-rf, '
    'g.latch-cell, g.latch-read): cell topology, read path, and the transistor estimate l1.transistors.',
    f'{RTL}libs/macros/dcache_128x32_1r1w_lram.v:5-8 (behavioural model only)')
ASK('l1.u-why', 'array technology',
    'Is the data cache latch RAM because the minion sits in the neighbourhood\'s low-voltage region, where SRAM cells '
    'cannot be placed? Which other in-minion arrays are latch RAM or register files (VPU register file vpu_64x32_3r2w, '
    'tag arrays, TLB) and which, if any, are SRAM?',
    'the "latch RAM, not SRAM, because ..." caption on the L1 page and which blocks the diagram draws as latch arrays.',
    f'{DC} pdf p.29; {MAS} pdf p.14 (the reason is our inference, l1.why-latch)')
ASK('l1.u-library', 'array technology',
    'What are the HDBULT08 and HDBULT11 standard-cell families (vendor, track height, threshold voltage), and what is '
    'the "MMI (hand-tuned)" logic in the Minion Overview slides: does it include the LRAM or the tag compare?',
    'the cell names and drawing style on the circuit panel, and whether the L1 is drawn as hand-placed custom logic.',
    f'{RTL}libs/rf_latches/et_clk_gate.v:17; {MOV}, pdf p.1-2 (text L22, L44)')
ASK('l1.u-energy', 'energy',
    'What are the post-layout energies of the LRAM at 0.52 V: pJ per 64-bit read, per 64-bit write, per tag lookup '
    '(4 ways), and leakage per macro?',
    'splitting the measured 12.5-17.3 pJ per 32-byte load (l1.e-vload) into array, tag check, pipeline and register '
    'write on the diagram\'s energy bars, instead of one bar for the whole load.',
    f'{EM4}:11 (measured totals only)')
ASK('l1.u-floorplan', 'physical',
    'Where do the 8 LRAM macros, the tag register files and the TLB sit in the minion\'s physical partition, and how '
    'large are they (area of the 4 KB array against the minion)?',
    'the physical layer of the L1 diagram: where the arrays light up inside the minion tile.',
    f'{MAS}, pdf p.7 (§2.2: minions are an independent physical partition; no minion floorplan)')
ASK('l1.u-cycles', 'latency',
    'Is the 5-cycle load-to-use of an L1 hit ID -> EX -> TAG -> MEM -> WB plus one cycle to the dependent\'s ID, with '
    'no bypass from S3 into EX? What costs hart 1 three extra cycles on every L1 miss?',
    'the per-stage timeline annotations of the load-hit animation, and a hart-1 note on the miss path.',
    f'{FEI} pdf p.12; {LAT} LAT-M1 hart1')
ASK('l1.u-parity', 'reliability',
    'Does the taped-out L1 carry parity or ECC, and can the minion arrays be put to sleep or retention on silicon?',
    'whether the diagram shows check bits per row and sleep transistors on the arrays (the open RTL shows neither).',
    f'{RTL}shire/minion/dcache/dcache_data_array.v:18-20; {MD} pdf p.7')

# ---------------------------------------------------------------- access sequences
SEQ_SRC = f'{DC}, pdf p.22-28 (§3.1, Figure 3)'


def S(seq, step, stage, block, action, circuit, circuit_kind, source, latency=None, energy=None, kind='et-spec',
      card=None, note=None):
    rows.append(dict(id=f'l1.seq.{seq}.{step}', level='L1', topic=f'sequence/{seq}', step=step, stage=stage,
                     block=block, action=action, circuit=circuit, circuit_kind=circuit_kind, latency=latency,
                     energy=energy, statement=f'{stage}: {block}. {action}', value=None, unit=None, source=source,
                     kind=kind, card=card, page_link=None, note=note))


# one scalar load that hits (8-byte ld, aligned, hart 0, scratchpad mode as the firmware leaves it)
seq = 'load-hit'
S(seq, 1, 'cycle 0, intpipe ID = DCache pre-S0', 'integer pipeline ID stage; DCache replay queue; pre-S0 arbiter',
  'Reads the base register, checks the scoreboard, pre-allocates a replay-queue entry and bids for the DCache '
  '(the core is the lowest of six bidders).',
  'Register-file read ports and flip-flops switch (GENERIC).', 'generic',
  f'{FEI}, pdf p.12 (§3.2.1); {DC}, pdf p.23-24 (§3.1.1), pdf p.38 (text L1647-1649)')
S(seq, 2, 'cycle 1, EX = S0', 'ALU; S0 request mux',
  'Adds base + offset into the virtual address; the granted request (address, destination register, command, '
  'size) is registered into S1.',
  '64-bit adder and request flip-flops (GENERIC).', 'generic',
  f'{FEI}, pdf p.13 (text L276-281); {DC}, pdf p.23 (text L796-799)')
S(seq, 3, 'cycle 2, TAG = S1', 'TLB (8-entry latch RF); metadata array (4 tag latch RFs + valid flip-flops); 4 tag '
  'comparators; PMA; LRU read',
  'Set = PA[9:6] with the mode\'s forced MSBs; each of the 4 way-RFs puts out its 35-bit entry for that set in the '
  'same cycle; four 33-bit comparisons give a one-hot hit, encoded to the way; the PMA checks cacheability; the '
  'data-array row address {set, half, way} and the one block enable (addr[4:3]) are formed and captured by the '
  'LRAM\'s read-address register at the clock edge.',
  'Tag latches are only read (their clocks stay gated off); their outputs pass a 16:1 select per bit; XNOR + AND trees '
  'switch; the LRAM address flip-flops toggle on the edge. Select and compare are GENERIC; the registered read '
  'address is ET (rf_latch_1r_1w_reg.v:139-149).', 'et-spec',
  f'{RTL}shire/minion/dcache/dcache_top.v:2108-2147; {RTL}shire/minion/dcache/dcache_metadata_array.v:55-80, 114-119; '
  f'{DC}, pdf p.24-25 (§3.1.2, Figure 5)')
S(seq, 4, 'cycle 3, MEM = S2', 'data array: 1 of 4 blocks = 2 macros of 128 x 32 (LRAM); hit logic; LRU flip-flops',
  'In the enabled block the 7-bit row address selects the hit way\'s row; its 64 latches drive the read select to '
  'the 64-bit output, which is registered into the S2->S3 data registers; the other 3 blocks stay idle. The hit is '
  'confirmed and the set\'s LRU matrix is rewritten.',
  'The stored latches are not disturbed; the row-select/mux-tree transistors and output wires switch in proportion '
  'to the data. No wordline boost, no bitline precharge, no sense amplifier if the macro is the latch-RF pattern '
  '(GENERIC for latch arrays; the silicon macro is unknown, l1.u-cell).', 'generic',
  f'{DC}, pdf p.25 (§3.1.3, text L930-957); {RTL}shire/minion/dcache/dcache_data_array.v:66-75, 119-136; '
  f'{RTL}shire/minion/dcache/dcache_top.v:3150-3159')
S(seq, 5, 'cycle 4, WB = S3', 'byte aligner, sign/zero extension, store bypass; integer register file',
  'Picks the 8 bytes out of the data registers, sign- or zero-extends, merges data from older stores still in S4/S5, '
  'and returns the value on s3_core_resp; the integer register file is written in WB.',
  'Mux and register-file write transistors (GENERIC).', 'generic',
  f'{DC}, pdf p.26 (§3.1.4, text L1016-1027); {FEI}, pdf p.15 (§3.2.6)')
S(seq, 6, 'cycle 5, next ID', 'dependent instruction',
  'A dependent load can read the value: 5 cycles issue to issue, measured as 5.25 in the unrolled chase on three '
  'cards; about 17 pJ per 32-byte load above idle on random data, including the instruction.',
  '-', 'generic', f'{LAT} LAT-M1; {EM4}:11', latency='5.25 cycles load-to-use (measured)',
  energy='17.3 pJ per 32 B flw.ps (random), 12.5 (zeros); 14.0 pJ per scalar flw', kind='et-measured', card=CARDS3)

# one store that hits
seq = 'store-hit'
S(seq, 1, 'ID to S1', 'as a load',
  'Address, tag lookup and hit way exactly as a load; the store data is sent in the TAG stage (S1) and aligned into '
  'the S2 store-data register.',
  'As load-hit steps 1-3.', 'generic', f'{FEI}, pdf p.14 (§3.2.4); {DC}, pdf p.24-25')
S(seq, 2, 'S2', 'data array read port',
  'Reads the row being written (the store is a read-modify-write).', 'As load-hit step 4.', 'generic',
  f'{DC}, pdf p.25 (text L955-957)')
S(seq, 3, 'S3', 'store merge / atomic unit',
  'Merges the new bytes into the row read in S2.', 'Mux logic (GENERIC).', 'generic', f'{DC}, pdf p.26-27 (§3.1.4, Figure 7)')
S(seq, 4, 'S4', 'write-port arbiter; LRAM write port',
  'Stores have the highest write priority. The per-block, per-half write enables and the 7-bit row address go to the '
  'macro; the write data was captured half a cycle earlier by the low-phase write-data latch; the decoded row\'s '
  'clock gate fires and that row\'s 64 latches turn transparent and take the new value.',
  'One row clock gate + 64 latch cells per written block switch; the write-data latch toggles only on changed bits. '
  'The per-row gate and opposite-phase write latch are the ET latch-RF pattern (rf_latch_1r_1w_reg.v:88-136); '
  'transistor detail GENERIC.', 'et-spec',
  f'{DC}, pdf p.27 (§3.1.5); {RTL}shire/minion/dcache/dcache_top.v:3979-3980; '
  f'{RTL}libs/rf_latches/rf_latch_1r_1w_reg.v:88-136')
S(seq, 5, 'S4 (first store to a clean line)', 'miss handler, metadata array',
  'A store to an exclusive (clean) line has the miss handler rewrite its metadata to modified (one 35-bit latch-RF '
  'write).', 'Row clock gate + 35 latches of the way\'s tag RF (GENERIC detail).', 'et-spec',
  f'{DC}, pdf p.35 (text L1493-1495)')
S(seq, 6, 'S5', 'store bypass',
  'Keeps the store data one more cycle so a younger load of the same bytes in S3 gets it.', '-', 'generic',
  f'{DC}, pdf p.28 (§3.1.6)', energy='23.0 pJ per 32 B fsw.ps (random); 25.5 pJ per scalar fsw', card=CARDS3)

# one load that misses, and the refill
seq = 'miss-refill'
S(seq, 1, 'S1', 'tag comparators; LRU',
  'No way matches. The LRU matrix picks the victim way (locked ways excluded).', 'As load-hit step 3.', 'generic',
  f'{RTL}shire/minion/dcache/dcache_top.v:2744')
S(seq, 2, 'S2', 'miss handler (1 of 2); replay queue (8 entries)',
  'A free miss handler takes the miss (a second miss to the same line joins it); the load parks in the replay '
  'queue and the core carries on; the destination register is scoreboarded.',
  'FSM flip-flops; replay-queue entry written (latch RF).', 'et-spec',
  f'{DC}, pdf p.34-35 (§3.6), pdf p.38-39 (§3.7-3.8); {RTL}shire/minion/dcache/dcache_replay_queue.v:218-241')
S(seq, 3, 'if the victim is dirty', 'miss handler Acquire_Wb; write-back unit',
  'The write-back unit reads the victim\'s two rows (256 bits a cycle) and sends a 512-bit write on the evict '
  'interface to the L2.',
  'Two full-row LRAM reads (4 blocks each).', 'et-spec', f'{DC}, pdf p.33 (text L1404-1407), pdf p.36 (Table 11)')
S(seq, 4, 'Fill_Req', 'miss interface to the neighbourhood',
  'Sends the line read to the L2 bank chosen by PA[7:6] (the L2 page takes over from here).', '-', 'et-spec',
  f'{DC}, pdf p.36 (Table 11); docs/research/counters-and-dram.md:479')
S(seq, 5, 'Fill_Resp', 'neighbourhood fill FIFO; LRAM write port',
  'The 512-bit response reaches the minion (at least 6 cycles through the neighbourhood\'s response path) and is '
  'written into the victim way\'s two rows through the write port, when no store holds it.',
  'Two row writes across all 4 blocks: 8 row clock gates, 512 latch cells.', 'et-derived',
  f'{DC}, pdf p.27 (text L1128-1129), pdf p.33 (text L1437-1439); {MAS}, pdf p.21 (text L826-834)',
  note='Two writes follow from the 256-bit row width; the documents do not state the count.')
S(seq, 6, 'Meta_Write_Req, Meta_Hazard', 'metadata latch RF; valid flip-flop',
  'Writes the new tag and state (exclusive for a load) and sets valid; waits one hazard cycle.',
  'One tag-RF row write (35 latches).', 'et-spec', f'{DC}, pdf p.35-36 (§3.6.2, Table 11)')
S(seq, 7, 'replay', 'replay queue -> S0 -> ... -> S3',
  'The waiting load re-enters (the replay queue outranks new core requests), now hits, and returns its data.',
  'As load-hit steps 2-5.', 'generic', f'{DC}, pdf p.38-39 (text L1676-1688)',
  latency='47 cycles load-to-use when the line is in the L2 (36 from its read buffer); hart 1 +3',
  energy='238 pJ to fill a 64 B line from the own scratchpad (random data)', kind='et-measured', card=CARDS3)

# the VPU reads its A operand from the scratchpad
seq = 'scratchpad-read'
S(seq, 1, 'S1', 'VPU scratchpad request',
  'The VPU sends way + address; any other S1 operation is cancelled into the replay queue; no TLB or tag check.',
  '-', 'et-spec', f'{DC}, pdf p.12-13 (§2.3.1)')
S(seq, 2, 'S2', 'data array, all 4 blocks',
  'Reads one 256-bit row (8 lanes x 32 bits) from sets 0-11.', 'All 8 macros read the same row.', 'et-spec',
  f'{RTL}shire/minion/dcache/dcache_top.v:2425-2437')
S(seq, 3, 'S3', 's3_vpu_scp_data',
  'Delivers the 256 bits to the VPU two cycles after the request.', '-', 'et-spec', f'{DC}, pdf p.13 (text L447-448)')

# TensorLoad fills the scratchpad
seq = 'tensorload'
S(seq, 1, 'CSR write', 'TensorLoad unit TL0',
  'A tensor_load CSR write starts the FSM: per line, the address goes through S0/S1 for TLB and PMA checks.',
  '-', 'et-spec', f'{DC}, pdf p.15 (§2.3.4), pdf p.46 (§3.9.5)')
S(seq, 2, 'L2I FSMs', 'miss interface',
  'Up to 4 line requests in flight to the L2.', '-', 'et-spec', f'{RTL}inc/dcache_defines.vh:108')
S(seq, 3, 'fill', 'LRAM write port',
  'Each 512-bit response is written into the scratchpad line (the TensorLoad client of the write port).',
  'Two full-row writes per line.', 'et-derived', f'{DC}, pdf p.33 (text L1440-1442), pdf p.40 (§3.9.1)',
  latency='16 lines: 160.4 cycles from the L2, 10.0 cycles per line', kind='et-measured', card=CARDS3)

# no refresh
seq = 'refresh'
S(seq, 1, 'never', 'latch arrays',
  'Nothing: latches hold their value while the minion rail is up, so the L1 has no refresh (the DRAM level does).',
  'Static storage (GENERIC).', 'generic', 'textbook (GENERIC); l1.no-sleep')

with open(OUT, 'w') as f:
    json.dump(rows, f, indent=1, ensure_ascii=False)
    f.write('\n')
kinds = {}
for r in rows:
    kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
print(os.path.abspath(OUT), len(rows), 'rows', kinds)
print(json.dumps(U, indent=1))
