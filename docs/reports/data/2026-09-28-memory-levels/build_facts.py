#!/usr/bin/env python3
"""Build facts.json for "Anatomy of a memory access, interactively" (docs/reports/sources/memory-levels.*).

    python3 docs/reports/data/2026-09-28-memory-levels/build_facts.py

Inputs, in research/ next to this script (copied from the session that made them, 27 September 2026):
  facts-l1.json    the L1 data cache: latch RAM in the minion (list; steps have topic "sequence/<name>")
  facts-l2.json    the L2 part of the shire cache (list; steps have topic "access-sequence")
  facts-l3.json    the L3 across the mesh ({meta, facts, access_sequence, asks})
  facts-scp.json   the scratchpad ({meta, facts, access_sequence, unknowns})
  facts-dram.json  LPDDR4X behind the memory shires (list; steps have field "seq")
  build_facts_{l1,l2,l3,scp,dram}.py, the builders that read the repository and the manuals, kept as a record
  DESIGN.md        the page's design (structure, scales, accesses, labelling rules, the asks), kept as a record
and, since 28 September, the energy manual's manual.json (docs/reports/data/2026-09-23-energy-manual/): the rail splits of
an L1 hit, a read of the shire's own scratchpad and an L3 read through the mesh on every card it carries, and the energy
of a mesh hop, which l1.e-rails (until then l1.e-19sep), l2.e.rails and l3.energy-per-load give in place of the first
runs of 19 September (see "the rail splits of three cards" below).
Every row has a source (a repo file with a line or field, a manual PDF page, or an RTL file and line) and a kind:
et-spec, et-measured, et-derived, generic (textbook, drawn as an illustration) or unknown (an ask for the team). The
research copies say "the lab lead" where the session's notes named him; so does this page.

Output, facts.json (the page's D):
  meta      what it was built from, counts by level and kind, the chip tour's script it copied the engine from
  facts     every row of the five files, keyed "<level>:<id>" (the one id two files share, g.no-refresh, becomes
            l1:g.no-refresh and l3:g.no-refresh), with the kind shortened (spec, measured, derived, generic, unknown),
            its badge (documented, generic, unknown), the rest of a composite kind as kind_note, the lab cards it
            covers (a2, a3, a1c1), the report page that quotes it, and a caveat marker: reimpl (a fact whose only
            source is Ainekko's re-implementation, external/core-et-main) or spec-v1.1 (the Shire Cache Specification)
  steps     each level's accesses in one schema: {title, measured, steps: [{n, stage, block, action, latency, energy,
            kind, facts[], circuit: [{el, does, kind, kind_note}]}]}; the five files use five step formats
  num       every number the page prints outside a fact's own statement: {v, t, u, f}; the build checks that the text
            occurs in that fact's statement (or equals its value), or that the printed text rounds from it
  parts     the facts each details panel lists, by level and part
  asks      what would settle each unknown: the proposed new rows of the hub's improvement ladder and the existing
            rows that get a new effect; every unknown fact belongs to exactly one ask
  rungs     the hub rows the asks link to, read from the hub's own data; proposed rows are marked proposed
  layout    the chip tour's layout (the measured map, the die view, the memory shires), read only, for the chip-scale
            views of the L3, the scratchpad and the DRAM; the six chip-tour facts those views cite (the measured map,
            the grid, the memory shires' places and tie, the routers and, since 29 September, the routing order) are
            copied into facts as "chip:<id>"
  addr      the example addresses
  conflicts where the sources disagree and what the page does about it
The build refuses to write facts.json if a printed number has no source, a reference is missing, an unknown lacks an
ask, a generic fact is not labelled generic, a hub row an ask names does not exist, a step the page shows cites no fact,
or a statement or source carries a local path. A review of the page (28 September 2026) found facts to correct; the
corrections are applied to the research rows below (FIX, STEPFIX, L3STEPFIX, SCPSTEPFIX, NEW), each with its reason,
so that the research files stay the record of the session that made them.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, 'research')
REPORTS = os.path.normpath(os.path.join(HERE, '..', '..'))
LEVELS = ['l1', 'l2', 'l3', 'scp', 'dram']
LEVEL_NAME = {'l1': 'L1', 'l2': 'L2', 'l3': 'L3', 'scp': 'Scratchpad', 'dram': 'DRAM'}
# the chip tour's engine script this page's engine was copied from (docs/reports/sources/chip-diagram.script.js in
# the merge worktree), as it stood when copied
CHIP_TOUR = {'script_mtime': '2026-09-27 21:27', 'lines': 2715}

KIND = {'et-spec': 'spec', 'et-measured': 'measured', 'et-derived': 'derived', 'generic': 'generic', 'unknown': 'unknown'}
BADGE = {'spec': 'documented', 'measured': 'documented', 'derived': 'documented', 'generic': 'generic', 'unknown': 'unknown'}


def split_kind(k):
    """'generic (et-spec that the crossing exists)' -> ('generic', 'et-spec that the crossing exists')."""
    k = (k or '').strip()
    m = re.match(r'(et-spec|et-measured|et-derived|generic|unknown)\b\s*(.*)$', k)
    if not m:
        raise SystemExit('unknown kind: ' + repr(k))
    rest = m.group(2).strip()
    rest = re.sub(r'^\((.*)\)$', r'\1', rest).strip(' ;')
    return KIND[m.group(1)], rest or None


def lab_lead(s):
    """The page names the lab lead by role only (DESIGN.md §1.4, §13)."""
    if not isinstance(s, str):
        return s
    return (s.replace("what Roman meant", "what the lab lead meant").replace("Roman's", "the lab lead's")
            .replace("Roman said", "the lab lead said").replace("Roman", "the lab lead"))


# ---------------------------------------------------------------- the five files
def load(lv):
    p = os.path.join(R, 'facts-%s.json' % lv)
    d = json.load(open(p))
    return d


RAW = {lv: load(lv) for lv in LEVELS}

# ---------------------------------------------------------------- the review's corrections (28 September 2026)
# The research files are kept as the record of the session that made them. What a review of the built page found
# wrong or unsupported is corrected here, each with its reason, before anything else reads the rows.
PREFIXES = ('/home/yaroslavvb/claude/et-soc1-pages5/', '/home/yaroslavvb/claude/et-soc1-prototyping/')


def unlocal(s):
    """Sources are repository-relative: drop the worktree prefixes a research file carried."""
    if not isinstance(s, str):
        return s
    for p in PREFIXES:
        s = s.replace(p, '')
    return s


def row_of(lv, fid):
    for f in (RAW[lv] if isinstance(RAW[lv], list) else RAW[lv]['facts']):
        if f['id'] == fid:
            return f
    raise SystemExit(f'review: no row {lv}:{fid}')


FIX = {
    # the neighbourhood MAS speaks of the ICache data RAMs only; the extension to the shire cache's panels is ours
    ('l1', 'l1.why-latch'): {
        'statement': "Why latches: the data cache sits inside the minion, in the neighbourhood's LV region. The neighbourhood "
                     "document says that \"the memory cells used to implement the ICache data RAMs need to be placed in an HV "
                     "region\"; that the same holds for the shire cache's SRAM panels, and that the data cache is a latch array "
                     "because latches are ordinary logic that runs on the minion supply, is our inference.",
        'note': "The documents never state this rationale for the data cache (asked). A voltage argument is consistent with it "
                "but does not prove it, and it is about the listed Vmin of these macros only: the firmware limits the minion rail "
                "to 400-620 mV (400 mV nominal), while the 1PUHD data panels list 585 mV as their lowest Vmin (RM0) and the "
                "2PUHDRF tag-state RAM 540 mV (Shire Cache Specification pdf p.51 Tables 13-14).",
        'source': "combines l1.lram (external/core-et/docs/Minion DCache Description.pdf pdf p.29) and l1.lv-region "
                  "(external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf pdf p.14 §4.2); minion-rail limits docs/research/"
                  "power-telemetry.md:189-190 (bl2_pmic_controller.h:165-244); Vmin external/core-et/docs/"
                  "CORE-ET-Shire-Cache-Specification.pdf pdf p.51 Tables 13-14"},
    # the SRAM rail ran at a 705 mV set point in every measurement; 750 mV is the figure and the boot default
    ('l1', 'l1.voltage'): {
        'statement': "The latch arrays switch at the minion-rail voltage: 0.517 V at 600 MHz (0.568 V at 700, 0.618 V at 800). "
                     "The card's power tree gives the minion rail 400 mV nominal, and the firmware limits it to 400-620 mV.",
        'source': "docs/findings/16-dvfs-and-leakage.md:20; docs/research/power-telemetry.md:44 (ET-PCIe-Dev-Card-V3), "
                  ":189-190 (bl2_pmic_controller.h:165-244)"},
    ('l2', 'l2.rail.sram'): {
        'statement': "The card's VDD_SRAM regulator feeds the shire-cache SRAM arrays (L2/L3/scratchpad); it is one of the three "
                     "rails whose power the PMIC meters. In every measurement here its set point was 705 mV (703-707 mV read on "
                     "the die); 750 mV is the card's power-tree figure (20 A / 15 W) and the firmware's boot default.",
        'value': 705, 'unit': 'mV set point',
        'source': "docs/reports/data/2026-09-20-power-aifoundry2/horace-telemetry.jsonl and horace2-telemetry.jsonl "
                  "(reg_mv.sram = 705 in all 586 + 1,247 samples, die_mv.sram 704); docs/research/power-telemetry.md:46 (power "
                  "tree), :189-190 (boot defaults: 'SRAM 750'; thermal_pwr_mgmt.h; bl2_pmic_controller.h:165-244)"},
    # the vendor is an inference at every level; the macro-type expansions are naming conventions
    ('l3', 'l3.vendor'): {
        'kind': 'et-derived (inference)',
        'statement': "The macros' vendor is not named. Three hints point to Synopsys-compiled memories: Ainekko's translation "
                     "guide lists 'Synopsys ASIC SRAMs (saduls0g4l1p*, etc.)', the spec's BIST is 'a shared bus BIST, such as the "
                     "Synopsys SMS', and the BIST wrappers in the open build script are named sms_sram_wr_<macro>. That the "
                     "memories are Synopsys's is an inference, as at the L2."},
    ('l3', 'l3.macros'): {
        'statement': "The cache RAMs are compiled macros bought from a third party: tag-state mbs = "
                     "saculs0g4l2p1024x40m4b1w0c0p0d0s1rm0rw11 (type '2PUHDRF'; the spec says the state RAM is two-ported), tag "
                     "mbt = saduls0g4l1p1024x116m4b1w0c0p0d0s1rm0sdrw11 and data mbd = saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11 "
                     "(type '1PUHD'). The spec calls the data array 'SRAM memory panels'.",
        'source': "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf pdf p.48 §2.14.5 ('SRAM memory panels that are 144 "
                  "bits wide') and §2.14.6.1 ('Intellectual Property (IP) acquired from a third party vendor'), pdf p.51 §2.14.6.4, "
                  "pdf p.45 ('the state RAM is two-ported')"},
    ('l2', 'l2.macro.data'): {
        'statement': "The data panel is the compiled macro 'saduls0g4l1p4096x144m4b4w0c0p0d0s1rm0sdrw11', RAM type 1PUHD: 4,096 "
                     "words x 144 bits.",
        'note': "The spec gives the type code, not its meaning. Reading 1PUHD as single-port ultra-high-density follows common "
                "memory-compiler naming (GENERIC); no source states it."},
    ('l2', 'l2.macro.state'): {
        'statement': "The tag-state RAM is 'saculs0g4l2p1024x40m4b1w0c0p0d0s1rm0rw11', RAM type 2PUHDRF: 1,024 words x 40 bits. "
                     "The spec says the state RAM is two-ported (a read and a write per request).",
        'source': "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf (v1.1), pdf p.51 §2.14.6.4, pdf p.45",
        'note': "Reading 'RF' in 2PUHDRF as register file follows common memory-compiler naming (GENERIC); no source states it."},
    ('scp', 'scp.panel-others'): {
        'statement': "Other shire-cache macros: tag RAM 'saduls0g4l1p1024x116m4b1...' (1PUHD, 4 ways x (23-bit tag + 6 ECC)), "
                     "tag-state RAM 'saculs0g4l2p1024x40m4b1...' (2PUHDRF, two-ported by the spec), I-cache data "
                     "'saduls0g4l1p512x144m4b1...'. The scratchpad path uses only the data panels.",
        'source': "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.47 §2.14.2-2.14.3, p.51 Tables 13-14, p.45 "
                  "('the state RAM is two-ported')"},
    # a generic claim under a documented badge
    ('l1', 'l1.seq.refresh.1'): {'kind': 'generic'},
    ('l2', 'l2.seq.load-hit.09'): {'note': None},
    # the latch-RF write and read mechanism is the ET library's, assumed for the LRAM by the re-implementation's mapping
    ('l1', 'l1.seq.store-hit.4'): {
        'kind': 'et-derived (the write mechanism is the ET latch-RF pattern, assumed for the LRAM by the re-implementation\'s '
                'mapping; the silicon macro is asked)',
        'circuit_kind': 'et-derived (the ET latch-RF pattern, assumed for the LRAM; the silicon macro is asked)',
        'source': "external/core-et/docs/Minion DCache Description.pdf, pdf p.27 (§3.1.5); external/core-et/rtl/shire/minion/"
                  "dcache/dcache_top.v:3979-3980; the mechanism: external/core-et/rtl/libs/rf_latches/rf_latch_1r_1w_reg.v:88-136, "
                  "tied to the LRAM only by external/core-et-main/docs/latch_translation.md:55-56, 93-96 (re-implementation)"},
    ('l1', 'l1.seq.load-hit.3'): {
        'circuit_kind': 'et-derived (the registered read address is the ET latch-RF pattern, assumed for the LRAM; the silicon '
                        'macro is asked)'},
    # 91 cycles = a DRAM load minus an L3 hit at the same home: it holds the home's miss path as well
    ('dram', 'dram.lat.dram-chip-share'): {
        'statement': "Of the 91-cycle constant (152 ns), about 28 cycles are the DRAM's own timing: the activate (tRCD, 11 cycles) "
                     "and the read latency plus two 32-byte bursts (19.3 + 8.6 ns, 17 cycles). The rest, at most about 63 cycles "
                     "(~105 ns), is the L3 home's miss path and its To_Sys crossings (about 12 cycles by the spec: an L3 miss is 42 "
                     "shire clocks against 30 for a hit) plus the memory shire's port, clock crossing, controller and PHY.",
        'source': "anatomy page §4 ('Of the 91 cycles (152 ns), the DRAM chip itself accounts for about 28'); dram.ctl.tRCD, "
                  "dram.ctl.RL-WL, dram.ctl.burst; external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf pdf p.11 Table 1 "
                  "('L3 cache read hit 30', 'L3 cache read miss 42 + NoC & Mem latency')",
        'note': "The 91 is a DRAM load minus an L3 hit at the same home (dram.lat.model), so it includes the home's extra work on a "
                "miss, not only the memory shire. 'At most' because each hop further out that the memory shires might sit moves 12 "
                "cycles from the constant into the mesh legs."},
    ('dram', 'dram.lat.ms-internal'): {
        'statement': "How the ~63 cycles beyond the DRAM's own timing split between the L3 home's miss handling and To_Sys "
                     "crossings, the memory shire's NoC AXI port and clock crossing, the address strip, the controller's port, CAM "
                     "and scheduler, the DFI and the PHY's transmit and receive paths is not known."},
    # the shire cache's clock is documented (l2.clock, l3.clock); only the conversion fits a measurement
    ('scp', 'scp.u-clock'): {
        'id': 'scp.clock',
        'kind': 'et-derived',
        'statement': "The shire cache runs on shire_clock, the minion clock (the neighbourhood clock is shire_clock shifted 180 "
                     "degrees), so at 600 MHz on these cards: one shire-cache cycle is one minion cycle. The read buffer's measured "
                     "saving, 11 minion cycles (47 against 36), matches the spec's 21 against 10 shire clocks at 1:1.",
        'source': "external/core-et/docs/CORE-ET Minion Shire Description.pdf pdf p.12 Table 2; external/et-man/ET-SoC Errata.pdf "
                  "pdf p.42; external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.11 Table 1; scp.lat-own",
        'note': "As l2.clock and l3.clock state; the telemetry reports only the minion and NoC clocks."},
    # the MAS: 4 clocks for agents other than minions, 6 for minions
    ('scp', 'scp.lat-split'): {
        'statement': "Of the 47 cycles, the spec accounts for 21 shire clocks inside the shire cache including both crossbars; the "
                     "other ~26 are the minion pipeline, the L1 miss and the neighbourhood's request (at least 6 clocks for a "
                     "minion) and response (at least 6 clocks to a minion) paths."},
    # the re-implementation RTL settles full-line writes; partial writes stay open
    ('l2', 'l2.zero-state'): {
        'statement': "Each way's tag state has a 'zero' bit: the data RAM is not read and zeros are returned. REQ_Lock sets it (a "
                     "missing line is installed without a fill), and esr_sc_zero_state_enable (default 1) 'prevents "
                     "reading/writing from the data RAMs if the content of the data is all zeros'. A fill or a full-line write of "
                     "an all-zero line sets it (the bank computes the NOR of the 512 bits as the line arrives).",
        'source': "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf (v1.1), pdf p.47 Table 12, pdf p.78 §3.9, pdf p.101; "
                  "external/core-et-main/hw/ip/shirecache/rtl/shirecache_bank_mesh.sv:346 (zero_data = ~|data), "
                  "shirecache_pipe_sub_bank.sv:983-1001, 1051-1063 (re-implementation RTL)",
        'note': "Whether a partial write that leaves a line all zero sets the bit is not stated (asked). It matters for reading the "
                "zeros-vs-random energy gap."},
    ('l2', 'l2.partition.default'): {
        'source': "external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/minion_configuration.c:613-624; "
                  ".../driver/bl2_cache_control.c:650-751; external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf (v1.1), "
                  "pdf p.21-22 Table 6 and 'The chip will come out of reset in mode M0'; docs/reports/data/2026-09-22-cards/"
                  "driver_config.json (l2_kb 16384, l3_kb 32768, scp_kb 81920 on every card)",
        'note': "Every lab card's driver reports M0's sizes (docs/reports/data/2026-09-22-cards/driver_config.json). Latency "
                "plateaus up to 64 KB do not test the 512 KB edge."},
    # the energy manual's idle-rail points, one denominator (the 128 MB of the 32 compute shires)
    ('l2', 'l2.leak'): {
        'statement': "SRAM-rail power at idle: 2.00 W for the chip (about 16 mW per MB if split evenly over the 128 MB of L2, L3 and "
                     "scratchpad, the energy manual's denominator); 1.70 W at 67 C and 2.73 W at 82 C on aifoundry2; 0.051-0.066 W "
                     "per degree C on the other cards.",
        'source': "docs/findings/05-claims.md:184, 473; docs/findings/16-dvfs-and-leakage.md:141; docs/energy-manual/"
                  "04a-fine-grain.md:110 ('Measured: 1.70 W at 67 °C') and its table (67 °C 1.698 W, 82 °C 2.726 W)",
        'note': "The per-MB split assumes the rail feeds the 128 MB evenly; what else is on the rail is unknown (asked)."},
    ('l3', 'l3.leakage'): {
        'statement': "The SRAM rail at idle is 1.70 W at 67 C and 2.73 W at 82 C on aifoundry2 (slope 0.066 W/C on aifoundry3); at "
                     "80 C its 2.51 W is 19.6 mW per MB of the 128 MB of L2, L3 and scratchpad, an upper bound on the arrays' "
                     "leakage since cache logic shares the rail. The L3's 32 MB are then at most about 0.63 W.",
        'source': "docs/energy-manual/04a-fine-grain.md:106-111 and its table (67 °C 1.698 W, 82 °C 2.726 W); docs/findings/"
                  "05-claims.md:473"},
    ('dram', 'dram.lat.row-hit'): {
        'statement': "A load that finds its row open skips the activate and saves 11-12 cycles (about 19 ns, tRCD): 214 against 226 "
                     "cycles in the refresh series; the two clusters' means were 11.0-11.6 cycles apart on three cards."},
    ('l3', 'l3.energy'): {
        'statement': "An L3 byte costs 14.7 pJ above idle [7.1-20.5 over 18 passes] (1 KB tensor loads by every minion, 768 KB per "
                     "shire, 600 MHz): aifoundry2 12.3, aifoundry3 13.5, aifoundry1 card 1 18.4 pJ/B; 4.7x an L2 byte (3.11), "
                     "about an eighth of a DRAM byte (114.6). About 0.94 nJ per 64 B line."},
    # the ICache data RAM: one stand-in's comment is no better than the other's; the spec and the PRM are
    ('l1', 'l1.icache-sram'): {
        'statement': "Contrast at the same level: the neighbourhood's instruction-cache data RAM (mbi) is "
                     "'saduls0g4l1p512x144m4b1...', the same 1PUHD macro family as the shire cache's data panels, which the spec "
                     "calls 'SRAM memory panels'; the PRM calls the SADULS family SRAMs, and the neighbourhood document says its "
                     "memory cells must sit in an HV region. Its bitcell is as unknown as the shire cache's.",
        'source': "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf pdf p.51 Table 14 (icache_ram (mbi)), pdf p.48 "
                  "§2.14.5; external/et-man/ET Programmer's Reference Manual.pdf pdf p.346 ('Configuration bits for SADULS "
                  "SRAM's'); external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf pdf p.14 §4.2",
        'note': "external/core-et/rtl/libs/macros/icache_data_ram.v calls it a '512 x 144-bit synchronous SRAM', but that file is "
                "a behavioural stand-in (Ainekko, 2026), like the L1's dcache_128x32_1r1w_lram.v, and says nothing about the cell."},
    # LPDDR4: MR3 holds PU-CAL, PDDS and DBI; data mask is MR13 OP[5]; the ET source is the controller's DBICTL
    ('dram', 'dram.ctl.dbi'): {
        'statement': "Data-bus inversion is on for reads and writes, and data masking is enabled: the controller's DBICTL sets "
                     "rd_dbi_en, wr_dbi_en and dm_en.",
        'note': "The init also writes MR3 = 0xF1 (INIT4.emr2). In LPDDR4 (GENERIC) MR3 holds PU-CAL, PDDS and the DBI-RD/WR "
                "enables, and data masking is set by MR13 OP[5]."},
    ('dram', 'gen.jedec-match'): {
        'statement': "The programmed timings are close to JEDEC LPDDR4's limits for a 16 Gb-per-channel die at 3,733 MT/s, as "
                     "recalled from JESD209-4 and not checked against the standard: tRCD and tRPpb 18 ns minimum, tRAS 42 ns, tRRD "
                     "10 ns, tFAW 40 ns, tRFCab 280 ns; RL 36 (with read DBI) and WL 16 are the fixed read and write latencies for "
                     "this rate, and tREFI 3.875 us is just under the 3.904 us maximum interval.",
        'source': "GENERIC comparison: JEDEC JESD209-4 values recalled, not checked against the standard (no ET source); ET values "
                  "from dram.ctl.*"},
    # the lane rule rests on the re-implementation RTL alone
    ('l3', 'l3.lane'): {'_caveat': 'reimpl',
                        'note': "The lane rule rests on core-et-main alone, Ainekko's co-simulated translation of the CORE-ET RTL; spec "
                                "p.100 says only that the swizzle picks the bank at the incoming L3 side. Heat per millimetre's lane "
                                "rule (PA[7:6], chip fact L103) is right for its remote-scratchpad flows; for L3 lines the lane is the "
                                "home bank (to confirm)."},
    # the ET-SoC-1's own manual gives the scratchpad address format a minion uses
    ('scp', 'scp.addr'): {
        'statement': "Scratchpad address fields as a minion issues them (the PRM's format 0): [39:31] = 9'h1 (scratchpad region), "
                     "[30] = 0 (the format bit), [29:23] the shire ID, 0x7F meaning the requester's own shire; then [22:12] set "
                     "(bit 22 = 0 for a 4 MB build), [11:10] way, [9:8] sub-bank, [7:6] bank, [5:0] byte.",
        'source': "external/et-man/ET Programmer's Reference Manual.pdf pdf p.486 §15.3 ('Format 0: Bit [30] set to 0 ... Shire ID "
                  "is placed in bits [29:23]'; 'Shire ID[6:0] bits set to 7'b1111111 targets the local Shire'); "
                  "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.24 §1.4.1.3 (set, way, sub-bank, bank); "
                  "external/core-et-main/hw/ip/shirecache/rtl/shirecache_pkg.sv:118, 146-149, 907",
        'note': "The Shire Cache Specification v1.1 (p.24) gives the shire field as [30:23], all ones meaning local; the PRM says "
                "agents other than minions use that hardware format, with bit 30 a copy of bit 29."},
    # say which pairing the energy manual's 30x is
    ('dram', 'dram.e.vs-scp'): {
        'statement': "On random data DRAM is 30x the energy of the shire's own scratchpad per byte read (132.6 against 4.40 pJ/B) "
                     "and 17x per byte written; relaying a result through DRAM costs 12.9-13.1x handing it to the next shire.",
        'source': "docs/energy-manual/04-bytes-memory.md:37 ('DRAM is 30x the energy ...'), the random-data rows of its tables; "
                  "docs/findings/05-claims.md, row 'The relay (V3)' (E29)"},
}

# the steps of the L2, the L3 and the scratchpad that carry a claim the review corrected: (level, access, step) -> fields
STEPFIX = {
    # the fill figure is canonical at 238 pJ (three cards), as the conflicts table says
    ('l2', 'l2.seq.load-hit.13'): {
        'energy': "whole path ~199 pJ per line above idle (3.11 pJ/B, energy manual); 238 pJ random / 101 pJ zeros to fill an L1 "
                  "line from the scratchpad (three cards)",
        'source': "external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf pdf p.21-23; docs/energy-manual/04-bytes-memory.md:27; "
                  "docs/energy-manual/04a-fine-grain.md:44 (the L1 fill, three cards)"},
    ('l2', 'l2.seq.no-refresh.01'): {
        'energy': "SRAM rail at idle 1.70 W at 67 °C → 2.73 W at 82 °C (aifoundry2)",
        'source': "textbook SRAM (GENERIC); the idle rail: docs/energy-manual/04a-fine-grain.md:110 and its table (67 °C 1.698 W, "
                  "82 °C 2.726 W)"},
}
L3STEPFIX = {
    ('refresh', 1): {
        'action': "No refresh: the spec describes none for the shire-cache RAMs (only deep sleep and shutdown for idle shires). The "
                  "static cost is leakage, at most 19.6 mW per MB at 80 C.",
        'circuit': [{'element': 'a static (SRAM-type) cell, if that is what the panels hold', 'action': 'keeps its value with no '
                     'refresh while the rail is up; the bitcell itself is asked', 'kind': 'generic'}]},
    ('load_hit', 3): {'circuit_sub': ("705 mV-side signals dropped to the 485 mV NoC",
                                      "shire-cache-side signals (their rail is asked; the SRAM rail reads 705 mV) dropped to the 485 mV NoC")},
    ('load_hit', 5): {'circuit_sub': ("485 mV to 705 mV, NoC clock to shire clock",
                                      "485 mV up to the shire channel's rail (asked; the SRAM rail reads 705 mV), NoC clock to shire clock")},
}
SCPSTEPFIX = {
    ('load_own', 3): {'latency': 'at least 6 clocks for a minion (4 for other agents)'},
    ('load_own', 7): {'circuit_kind': ('sense-enable timing', 'generic (et-spec that the RM, RA and BC trims exist; their '
                                       'circuit effect is vendor-specific)')},
    ('atomic', 2): {'block': 'home bank: data panel read, atomic block, data panel write',
                    'does': "The sub-bank is held busy from the read through the write; the atomic block (a three-stage "
                            "pipeline in the re-implementation RTL) computes the result; the response goes back as an ESR write "
                            "over to_sys.",
                    'source_add': "external/core-et-main/hw/ip/shirecache/rtl/shirecache_pipe_atomic.sv:11 (three-stage "
                                  "pipeline, re-implementation RTL); external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.17 "
                                  "('atomic response data sent back as an ESR write to to_sys mesh')"},
    ('miss_refill_refresh', 1): {'does': "The scratchpad has no misses and no victims: every in-range address is a hit, and an "
                                         "out-of-range index returns an error (SC_PipeErr_ScpOpToNonEnRegion by p.25; the error "
                                         "list on p.111 names SC_PipeErr_ScpSetOutOfRange). Nothing is ever evicted.",
                                 'source_add': "external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.111"},
    ('miss_refill_refresh', 2): {'does': "No refresh if the cells are static (SRAM-type) storage; the only standing cost is "
                                         "leakage, at most 19.6 mW per MB at 80 C on this rail."},
}

# unknowns a fact's note raised that no ask covered; each joins an ask below
NEW = {
    'dram': [
        {'id': 'dram.u-ports', 'topic': 'controller', 'kind': 'unknown', 'value': None, 'unit': None, 'card': None, 'page_link': None,
         'statement': "Which traffic the memory shire steers to each controller's two AXI ports (priority 15 and 8).",
         'source': "none: dram.ctl.ports gives the ports' priorities (memshire_ddr_init_functions.c:4670-4680), not the steering",
         'note': None},
        {'id': 'dram.u-qos', 'topic': 'controller', 'kind': 'unknown', 'value': None, 'unit': None, 'card': None, 'page_link': None,
         'statement': "What esr_sc_axi_qos is set to on these cards, so whether the shire cache marks its memory requests high or "
                      "low priority.",
         'source': "none: external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf pdf p.97 §4.1 defines the field; no value "
                   "is read or written in the sources", 'note': None},
        {'id': 'dram.u-atomic', 'topic': 'controller', 'kind': 'unknown', 'value': None, 'unit': None, 'card': None, 'page_link': None,
         'statement': "When a global atomic on a DRAM address is done in the memory shire's atomic unit rather than at the L3 home.",
         'source': "none: dram.ctl.atomic-unit documents the unit (PRM pdf p.514; memshire_defines.vh:121), not when it is used",
         'note': None},
        {'id': 'dram.u-cam', 'topic': 'controller', 'kind': 'unknown', 'value': None, 'unit': None, 'card': None, 'page_link': None,
         'statement': "The controller's total transaction-store (CAM) depth, MEMC_NO_OF_ENTRY, a build parameter; the init code sets "
                      "only the 32 entries for low-priority reads.",
         'source': "none: external/et-platform/etsoc-hal/src/memshire_ddr_init_functions.c:4661 (SCHED) sets the split only",
         'note': None},
        {'id': 'dram.u-ms-clock', 'topic': 'memory shire', 'kind': 'unknown', 'value': None, 'unit': None, 'card': None,
         'page_link': None,
         'statement': "Where inside the memory shire the mesh-to-controller clock crossing sits, and whether the memory shire's logic "
                      "runs at the 933 MHz DFI clock.",
         'source': "none: dram.seq.load.03 infers it from the anatomy page's 'crossings between the 933 MHz DDR clock and the mesh'",
         'note': None},
        {'id': 'dram.u-temp', 'topic': 'refresh', 'kind': 'unknown', 'value': None, 'unit': None, 'card': None, 'page_link': None,
         'statement': "Whether the DRAM packages stay under 85 C under load. The firmware leaves temperature derating off, so refresh "
                      "stays at 3.875 us whatever their temperature; above 85 C LPDDR4 asks for refresh 2x or 4x as often "
                      "(GENERIC), so this is a data-retention question, not only a performance one.",
         'source': "none: external/et-platform/etsoc-hal/src/memshire_ddr_init_functions.c:4686-4688 (DERATEEN commented out); "
                   "nothing in the sources reads MR4", 'note': None},
        {'id': 'dram.u-vdd1', 'topic': 'power', 'kind': 'unknown', 'value': None, 'unit': None, 'card': None, 'page_link': None,
         'statement': "Which card rail feeds the LPDDR4X packages' VDD1 (1.8 V in JEDEC LPDDR4X, GENERIC).",
         'source': "none: the card's power tree (docs/research/power-telemetry.md:47-52) names VDD_DDR, VDD_QLP and VDD_Q only",
         'note': None},
    ],
    'l2': [
        {'id': 'l2.u-zero-partial', 'topic': 'zero lines', 'kind': 'unknown', 'value': None, 'unit': None, 'card': None,
         'page_link': None,
         'statement': "Whether a partial write that leaves a line all zero sets the tag state's zero bit (a fill or a full-line write "
                      "does, in the re-implementation RTL).",
         'source': "none: external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf pdf p.47 Table 12, p.101 do not say; "
                   "shirecache_bank_mesh.sv:346 covers whole lines only", 'note': None},
    ],
    # generic readings the review moved out of documented rows
    'l2g': [
        {'id': 'g.panel-read-count', 'topic': 'circuit', 'kind': 'generic', 'value': None, 'unit': None, 'card': None,
         'page_link': None,
         'statement': "GENERIC, if each panel is an ordinary compiled SRAM macro: a line read raises one wordline in each of the 4 "
                      "panels and fires 576 sense amplifiers (144 per panel); how many bitline pairs swing depends on the column "
                      "mux, which the macro datasheets would settle.",
         'source': "textbook (GENERIC); widths from l2.seq.load-hit.09; the column mux is l2.macro.name-decode (unknown)",
         'note': None},
    ],
}

# ---------------------------------------------------------------- the rail splits of three cards (28 September)
# Until 28 September three rows quoted the first runs of Anatomy of a memory access (19 September, one card: an L1 hit,
# an L2 hit and a local L3 hit, each split between the rails), two of them citing lines of
# workloads/memprobe/report_template.html that no longer hold those numbers. They now give the split that page's §6
# shows: the energy manual's catalogue on every card it carries (E46, 26 September), each metered rail's share of a
# path's power over idle and the rest on no metered rail, computed here from manual.json as
# workloads/memprobe/build_report.py computes it (rounded half away from zero, as it rounds). The rows and steps that
# compared themselves with those first runs follow them: the wire energy, the L2's power per shire and three steps.
MAN_SRC = 'docs/reports/data/2026-09-23-energy-manual/manual.json'
MAN = json.load(open(os.path.join(REPORTS, 'data', '2026-09-23-energy-manual', 'manual.json')))
MCC = MAN['catalogue']['cards']
MCARDS = [c for c in ('aifoundry2', 'aifoundry3', 'aifoundry1-c1') if c in MCC]   # the chart kit's registry order
MCARD_N = {2: 'two', 3: 'three', 4: 'four'}.get(len(MCARDS), str(len(MCARDS)))
MCARD_TXT = ', '.join({'aifoundry1-c1': 'aifoundry1 card 1'}.get(c, c) for c in MCARDS[:-1]) + ' and ' + \
    {'aifoundry1-c1': 'aifoundry1 card 1'}.get(MCARDS[-1], MCARDS[-1])
ANATOMY6 = 'https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#where-the-energy-goes'


def rnd(x):
    """Round half away from zero, as the anatomy page's builder does."""
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)


def per_card(vals, unit='%'):
    """'69, 68 and 49%': each card's value in registry order, or one value when every card rounds to it; a share under
    1.5% on every card is '1% or less'."""
    if unit == '%' and max(vals) < 1.5:
        return '1% or less'
    r = [f'{rnd(v):,}' for v in vals]
    return (r[0] if len(set(r)) == 1 else ', '.join(r[:-1]) + ' and ' + r[-1]) + unit


def rail_split(cfg):
    """Per card, each metered rail's share of the path's power over idle and the rest's (no metered rail), in %."""
    out = {}
    for c in MCARDS:
        r = MCC[c]['summary'][cfg]
        if not r.get('all_600mhz'):
            raise SystemExit(f'{c} {cfg}: not every burst at 600 MHz')
        w = r['over_idle_w']['mean']
        s = {k: 100 * r['rails_over_w'][k + '_w']['mean'] / w for k in ('minion', 'sram', 'noc')}
        s['rest'] = 100 - sum(s.values())
        s['pjb'] = r['pj_per_byte']['mean'] if r.get('pj_per_byte') else None
        out[c] = s
    return out


SPL = {'l1': rail_split('flw.ps/random/h2'), 'scp': rail_split('tload/scp/random'), 'l3': rail_split('dramrow/stride8K/random')}
SC = lambda p, k: [SPL[p][c][k] for c in MCARDS]   # noqa: E731
# a mesh hop per 64 B line: the mean over the cards of the manual's straight line through another shire's scratchpad
HOP = {d: sum(MCC[c]['wire'][d]['slope_pj_per_byte_per_hop'] for c in MCARDS) / len(MCARDS) for d in ('zeros', 'random')}
HOPS = sorted(p['hops'] for p in MCC[MCARDS[0]]['wire']['random']['points'])
# the qualitative claims below, on every card: the L1 is the minion rail's, a scratchpad read the SRAM rail's, and an L3
# read through the mesh puts a large share on the mesh rail
for c in MCARDS:
    if not (SPL['l1'][c]['minion'] > 75 and SPL['l1'][c]['sram'] < 5):
        raise SystemExit(f'{c}: an L1 hit is no longer mostly on the minion rail')
    if max(('minion', 'sram', 'noc', 'rest'), key=lambda k: SPL['scp'][c][k]) != 'sram':
        raise SystemExit(f'{c}: the SRAM rail no longer carries most of a scratchpad read')
    if SPL['l3'][c]['noc'] < 25:
        raise SystemExit(f'{c}: an L3 read through the mesh no longer puts a quarter or more on the mesh rail')
# l2.e.rails's note: the card with the largest unmetered share of a scratchpad read is the one whose unmetered power
# rises most with its SRAM rail's
if max(MCARDS, key=lambda c: SPL['scp'][c]['rest']) != max(MCARDS, key=lambda c: MAN['unmetered'][c]['coef']['sram']):
    raise SystemExit("the scratchpad read's largest unmetered share is no longer on the card with the largest SRAM coefficient")
RS = {
    'l1_min': per_card(SC('l1', 'minion')), 'l1_sram': per_card(SC('l1', 'sram')), 'l1_noc': per_card(SC('l1', 'noc')),
    'l1_rest': per_card(SC('l1', 'rest')),
    'scp_sram': per_card(SC('scp', 'sram')), 'scp_min': per_card(SC('scp', 'minion')), 'scp_noc': per_card(SC('scp', 'noc')),
    'scp_rest': per_card(SC('scp', 'rest')),
    'l3_sram': per_card(SC('l3', 'sram')), 'l3_noc': per_card(SC('l3', 'noc')), 'l3_min': per_card(SC('l3', 'minion')),
    'l3_rest': per_card(SC('l3', 'rest')), 'l3_line': per_card([64 * v for v in SC('l3', 'pjb')], ' pJ'),
    'l3_pjb': ', '.join(f'{v:.1f}' for v in SC('l3', 'pjb')[:-1]) + f' and {SC("l3", "pjb")[-1]:.1f} pJ/B',
    'hop_r': f"{rnd(64 * HOP['random'])} pJ per line on random data", 'hop_z': f"{rnd(64 * HOP['zeros'])} on zeros",
    'hop_rb': f"{rnd(64 * HOP['random'])} pJ", 'hop_pjb': f"{HOP['random']:.2f} and {HOP['zeros']:.2f} pJ/B",
    'hop_fit': f'{HOPS[0]}-{HOPS[-1]} hops',
}
FIRST_NOTE = ("Until 28 September this row gave the first measurement, on 19 September on aifoundry2 alone ({}); Anatomy of a "
              "memory access keeps those runs as one note, and its §6 shows this split.")
FIX[('l1', 'l1.e-19sep')] = {
    'id': 'l1.e-rails',
    'statement': f"Split by rail on {MCARD_N} cards (the energy manual's catalogue, 26 September): both harts of every minion "
                 f"re-reading the L1 with 32-byte vector loads (flw.ps, random data) put {RS['l1_min']} of the power above idle "
                 f"on the minion rail, {RS['l1_sram']} on the SRAM rail, {RS['l1_noc']} on the mesh and {RS['l1_rest']} on no "
                 f"metered rail ({MCARD_TXT}). An L1 hit is the minion rail's.",
    'value': rnd(SPL['l1'][MCARDS[0]]['minion']), 'unit': '% on the minion rail (' + MCARDS[0] + ')',
    'source': f"{MAN_SRC} catalogue.cards.<card>.summary['flw.ps/random/h2'] (rails_over_w, over_idle_w), as Anatomy of a "
              f"memory access §6 splits it (workloads/memprobe/build_report.py)",
    'card': ', '.join(MCARDS), 'page_link': ANATOMY6,
    'note': FIRST_NOTE.format("an 8-byte ld hitting the L1 in a power loop; docs/reports/data/2026-09-19-memprobe-aifoundry2/"
                              "power/summary.json summary.l1")}
FIX[('l2', 'l2.e.rails')] = {
    'statement': f"No L2 hit has been split between the rails on {MCARD_N} cards. Read as the shire's own scratchpad (1 KB "
                 f"tensor loads, no tag check, random data), the same arrays put {RS['scp_sram']} of the power above idle on "
                 f"the SRAM rail, {RS['scp_min']} on the minion rail, {RS['scp_noc']} on the mesh and {RS['scp_rest']} on no "
                 f"metered rail ({MCARD_TXT}; the energy manual's catalogue, 26 September).",
    'value': rnd(SPL['scp'][MCARDS[0]]['sram']), 'unit': '% on the SRAM rail (own-scratchpad read, ' + MCARDS[0] + ')',
    'source': f"{MAN_SRC} catalogue.cards.<card>.summary['tload/scp/random'] (rails_over_w, over_idle_w), as Anatomy of a "
              f"memory access §6 splits it (workloads/memprobe/build_report.py)",
    'card': ', '.join(MCARDS), 'page_link': ANATOMY6,
    'note': FIRST_NOTE.format("an L2 hit by 8-byte loads; docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json power.l2")
            + " The unmetered share is highest on the card whose unmetered power rises most with its SRAM rail's (the energy "
              "manual's fit of the unmetered power, §4.5: unmetered.<card>.coef.sram)."}
FIX[('l3', 'l3.energy-per-load')] = {
    'statement': f"Per 64 B line read from the L3 by 1 KB tensor loads through the mesh (a working set whose lines are homed "
                 f"across the chip), on random data: {RS['l3_line']} above idle ({RS['l3_pjb']}), of which {RS['l3_sram']} on "
                 f"the SRAM rail (the L2 miss, the L3 read and the L2 fill), {RS['l3_noc']} on the mesh rail, {RS['l3_min']} on "
                 f"the minion rail and {RS['l3_rest']} on no metered rail ({MCARD_TXT}). Each mesh hop adds {RS['hop_r']} and "
                 f"{RS['hop_z']} ({RS['hop_pjb']}, the mean of the energy manual's straight lines through another shire's "
                 f"scratchpad at {RS['hop_fit']}).",
    'value': rnd(SPL['l3'][MCARDS[0]]['sram']), 'unit': '% on the SRAM rail (L3 read through the mesh, ' + MCARDS[0] + ')',
    'source': f"{MAN_SRC} catalogue.cards.<card>.summary['dramrow/stride8K/random'] (rails_over_w, over_idle_w, pj_per_byte) "
              f"and catalogue.cards.<card>.wire.<zeros|random>.slope_pj_per_byte_per_hop, as Anatomy of a memory access §6 "
              f"gives them (workloads/memprobe/build_report.py)",
    'card': ', '.join(MCARDS), 'page_link': ANATOMY6,
    'note': FIRST_NOTE.format("one 8-byte ld per line, a local or a far home; docs/reports/data/2026-09-19-memprobe-aifoundry2/"
                              "summary.json power.l3near, .l3far")}
_w = row_of('l3', 'l3.wire-energy')['statement']
_old_tail = ', close to the 47-59 pJ per hop of l3.energy-per-load.'
if not _w.endswith(_old_tail):
    raise SystemExit('l3.wire-energy: its research statement changed; revisit the comparison with l3.energy-per-load')
FIX[('l3', 'l3.wire-energy')] = {
    'statement': _w[:-len(_old_tail)] + f"; on board power a hop measures {RS['hop_rb']} per line on random data and "
                                        f"{RS['hop_z']} (l3.energy-per-load)."}
# the L2's power per shire, split as the own scratchpad's read is (the SRAM rail's share on each card)
_s = row_of('l2', 'l2.e.shire')['statement']
_bw = row_of('l2', 'l2.bw.measured')['value']                       # TB/s
_mw = _bw * MAN['reruns']['levels_pj_per_byte']['l2']['mean'] / 32 * 1000   # mW per shire (TB/s x pJ/B = W; 32 shires)
_old = "If the 19 September rail split holds (61% on the SRAM rail), roughly 145 mW of that is on the SRAM rail"
if _old not in _s or f"about {rnd(_mw / 10) * 10} mW per shire" not in _s:
    raise SystemExit('l2.e.shire: its research statement or the L2 energy changed; revisit the split per shire')
_lo, _hi = (rnd(_mw * v / 100 / 5) * 5 for v in (min(SC('scp', 'sram')), max(SC('scp', 'sram'))))
FIX[('l2', 'l2.e.shire')] = {
    'statement': _s.replace(_old, f"If an L2 read puts as large a share on the SRAM rail as a read of the same arrays as the own "
                                  f"scratchpad does ({rnd(min(SC('scp', 'sram')))}-{rnd(max(SC('scp', 'sram')))}%, by card; "
                                  f"l2.e.rails), roughly {_lo}-{_hi} mW of that is on the SRAM rail")}
_e = row_of('l2', 'l2.seq.load-hit.09')['energy']
_old = "the SRAM rail carried ~112 pJ per L2 hit (19 Sep); how much of that is this data read"
if not _e.startswith(_old):
    raise SystemExit('l2.seq.load-hit.09: its research energy changed; revisit it')
STEPFIX[('l2', 'l2.seq.load-hit.09')] = {
    'energy': f"read as the own scratchpad, these arrays put {RS['scp_sram']} of the power on the SRAM rail, by card (l2.e.rails); "
              f"how much of an L2 hit's energy is this data read" + _e[len(_old):]}
_l3s = {s['n']: s for s in RAW['l3']['access_sequence']['load_hit']}
if _l3s[2]['energy'] != "part of 306 pJ SRAM rail per L3 load (l3.energy-per-load)":
    raise SystemExit('l3 load_hit step 2: its research energy changed; revisit it')
_old = "; 47-59 pJ measured (l3.energy-per-load)"
if not _l3s[8]['energy'].endswith(_old):
    raise SystemExit('l3 load_hit step 8: its research energy changed; revisit it')
L3STEPFIX[('load_hit', 2)] = {'energy': f"part of the SRAM rail's {RS['l3_sram']} of an L3 read through the mesh, by card "
                                        f"(l3.energy-per-load)"}
L3STEPFIX[('load_hit', 8)] = {'energy': _l3s[8]['energy'][:-len(_old)] + f"; {RS['hop_rb']} per line per hop measured on board "
                                                                         f"power, {RS['hop_z']} (l3.energy-per-load)"}

# ---------------------------------------------------------------- the routing order, measured (29 September)
# Until 29 September the dimension order was not known, and the chip views drew every route x first. E56 ("nocr", hub
# rung 32) measured it on aifoundry1's card 1 and, frozen, on aifoundry3 and aifoundry2: a request goes x first and a
# reply y first (the chip tour's fact L104, copied below as chip:L104). l3.route now says so, and u.noc-hop no longer
# asks for it.
_r = row_of('l3', 'l3.route')
_old = "whether a request turns x or y first, which of the nine router layers L3 traffic uses and how wide a link is are not documented in the drop."
if not _r['statement'].endswith(_old):
    raise SystemExit('l3.route: its research statement changed; revisit it')
FIX[('l3', 'l3.route')] = {
    'statement': _r['statement'][:-len(_old)] + "and in dimension order: a request goes x first, then y, and its reply y first, "
                 "then x, back along the request's links (measured on aifoundry1 card 1, aifoundry3 and aifoundry2 on "
                 "29 September, E56; chip:L104). Which of the nine router layers L3 traffic uses and how wide a link is are not documented in "
                 "the drop.",
    'source': _r['source'] + "; the order: docs/reports/data/2026-09-29-nocr (E56), the chip tour's fact L104",
    'card': "aifoundry2, aifoundry3, aifoundry1-c1",
    'note': "Until 29 September the order was not known and this page drew every route x first. E56 streamed tensor loads "
            "and stores between compute shires' scratchpads; that an L3 home's and a memory shire's replies take the same "
            "order is inferred."}
_u = row_of('l3', 'u.noc-hop')
_old = "which of the 9 main-NoC layers carries L3 requests and replies, the dimension order, and the flit width."
if not _u['statement'].endswith(_old):
    raise SystemExit('u.noc-hop: its research statement changed; revisit it')
FIX[('l3', 'u.noc-hop')] = {
    'statement': _u['statement'][:-len(_old)] + "which of the 9 main-NoC layers carries L3 requests and replies, and the flit "
                 "width. The dimension order, asked here until 29 September, is measured (l3.route).",
    'source': _u['source'] + "; the order: docs/reports/data/2026-09-29-nocr (E56)"}

for (lv, fid), upd in FIX.items():
    r = row_of(lv, fid)
    for k, v in upd.items():
        r[k] = v
for (lv, fid), upd in STEPFIX.items():
    r = row_of(lv, fid)
    r.update(upd)
for (acc, n), upd in L3STEPFIX.items():
    s = next(x for x in RAW['l3']['access_sequence'][acc] if x['n'] == n)
    if 'action' in upd:
        s['action'] = upd['action']
    if 'energy' in upd:
        s['energy'] = upd['energy']
    if 'circuit' in upd:
        s['circuit'] = (s.get('circuit') or []) + upd['circuit']
        if 'g.no-refresh' not in s['facts']:
            s['facts'].append('g.no-refresh')
    if 'circuit_sub' in upd:
        a, b = upd['circuit_sub']
        hit = [c for c in s.get('circuit') or [] if c.get('action') == a]
        if not hit:
            raise SystemExit(f'review: l3 {acc} {n}: no circuit "{a}"')
        hit[0]['action'] = b
for (acc, n), upd in SCPSTEPFIX.items():
    s = next(x for x in RAW['scp']['access_sequence'][acc]['steps'] if x['n'] == n)
    for k in ('latency', 'does', 'block'):
        if k in upd:
            s[k] = upd[k]
    if 'source_add' in upd:
        s['source'] = s['source'] + '; ' + upd['source_add']
    if 'circuit_kind' in upd:
        dev, kind = upd['circuit_kind']
        hit = [c for c in s.get('circuit') or [] if c.get('device', '').startswith(dev)]
        if not hit:
            raise SystemExit(f'review: scp {acc} {n}: no circuit "{dev}"')
        hit[0]['kind'] = kind
RAW['dram'].extend(NEW['dram'])
RAW['l2'].extend(NEW['l2'])
RAW['l3']['facts'].extend(NEW['l2g'])   # a generic panel fact, kept with the L3's shared circuit facts (l3:g.*)
ROWS = {}      # level -> list of fact rows (steps of L1, L2 and DRAM included: they are rows with ids and sources)
STEPROWS = {}  # level -> list of step rows, in the file's order
ROWS['l1'] = RAW['l1']
ROWS['l2'] = RAW['l2']
ROWS['l3'] = RAW['l3']['facts']
ROWS['scp'] = RAW['scp']['facts']
ROWS['dram'] = RAW['dram']

TITLE = {
    'et-soc1-memory-hierarchy': 'Memory hierarchy',
    'et-soc1-memory-anatomy': 'Anatomy of a memory access',
    'et-soc1-energy-manual': 'The energy manual',
    'et-soc1-horace-experiment': 'The Horace experiment',
    'et-soc1-dvfs-leakage': 'DVFS and leakage',
    'et-soc1-chip-diagram': 'The ET-SoC-1, interactively',
    'et-soc1-power-temperature': 'Power and temperature',
    'et-soc1-on-chip-communication': 'On-chip communication',
    'et-soc1-on-chip-relay': 'Hand it to the next shire',
    'et-soc1-hot-line': 'One hot line stops a shire',
    'et-soc1-heat-per-mm': 'Heat per millimetre',
    'et-soc1-limits-of-observability': 'Limits of observability',
    'et-soc1-matmul-efficiency': 'Matmul efficiency',
    'et-soc1-why-low-power': 'Why low power',
    'et-soc1-pcie-link': 'Over the PCIe link',
    'et-soc1-ridge-points': 'Ridge points',
}


def page_title(url):
    if not url:
        return None
    m = re.search(r'spacesheep\.dev/@yaroslavvb/([\w-]+)', url)
    if not m or m.group(1) not in TITLE:
        raise SystemExit('no title for page ' + url)
    return TITLE[m.group(1)]


CARD_PAT = (('a2', r'aifoundry2'), ('a3', r'aifoundry3'),
            ('a1c1', r'aifoundry1-c1|aifoundry1 card 1|aifoundry1 \(both cards\)|aifoundry1, |aifoundry1$'))


def cards_of(c):
    c = c or ''
    if re.search(r'all three|three cards|every card', c):
        return ['a2', 'a3', 'a1c1'], c
    cards = [k for k, pat in CARD_PAT if re.search(pat, c)]
    plain = re.fullmatch(r'(aifoundry2|aifoundry3|aifoundry1-c1)(, (aifoundry2|aifoundry3|aifoundry1-c1))*', c.strip())
    return cards, (None if (plain or not c) else c)


def caveat(src):
    s = src or ''
    parts = [p.strip() for p in re.split(r';', s) if p.strip()]
    if parts and all('core-et-main' in p for p in parts):
        return 'reimpl'
    if 'Shire-Cache-Specification' in s or 'Shire Cache Specification' in s:
        return 'spec-v1.1'
    return None


def is_step(lv, f):
    if lv == 'l1':
        return str(f.get('topic', '')).startswith('sequence/')
    if lv == 'l2':
        return f.get('topic') == 'access-sequence'
    if lv == 'dram':
        return 'seq' in f
    return False


FACTS = {}
for lv in LEVELS:
    STEPROWS[lv] = []
    for f in ROWS[lv]:
        key = lv + ':' + f['id']
        if key in FACTS:
            raise SystemExit('duplicate fact ' + key)
        kind, note = split_kind(f['kind'])
        cards, cards_txt = cards_of(f.get('card'))
        url = f.get('page_link')
        out = {'id': f['id'], 'level': lv, 'topic': f.get('topic'), 'statement': lab_lead(f['statement']),
               'value': f.get('value'), 'unit': f.get('unit'), 'source': unlocal(f.get('source')), 'kind': kind,
               'badge': BADGE[kind], 'kind_note': note, 'cards': cards, 'url': url, 'page': page_title(url),
               'note': lab_lead(f.get('note')), 'caveat': f.get('_caveat') or caveat(f.get('source'))}
        if cards_txt:
            out['cards_txt'] = cards_txt
        FACTS[key] = out
        if is_step(lv, f):
            STEPROWS[lv].append((key, f))

# the chip tour's facts that the chip-scale views of the L3, the scratchpad and the DRAM cite (the measured map, the
# memory shires' places, the routers), copied read-only under "chip:<id>"; the chip tour's "inferred" kind is kept as
# derived with a note
CHIP = json.load(open(os.path.join(REPORTS, 'data', '2026-09-27-chip-diagram', 'facts.json')))
CHIP_FACTS = ['mesh.logical-map', 'mesh.grid', 'L40', 'L42', 'L105', 'L104']   # L104: the routing order (E56, 29 Sep)
for cid in CHIP_FACTS:
    f = CHIP['facts'][cid]
    kind = {'inferred': 'derived'}.get(f['kind'], f['kind'])
    FACTS['chip:' + cid] = {'id': cid, 'level': 'chip', 'topic': f.get('topic'), 'statement': f['statement'], 'value': f.get('value'),
                            'unit': f.get('unit'), 'source': f.get('source'), 'kind': kind, 'badge': BADGE[kind],
                            'kind_note': 'inferred in the chip tour' if f['kind'] == 'inferred' else None, 'cards': f.get('cards') or [],
                            'url': f.get('url'), 'page': f.get('page'), 'note': f.get('note'), 'caveat': caveat(f.get('source')),
                            'from': 'docs/reports/data/2026-09-27-chip-diagram/facts.json'}

# ---------------------------------------------------------------- the accesses, in one schema
ACCESS = {
    'l1': [('load-hit', 'load-hit', 'Load hit'), ('store-hit', 'store-hit', 'Store hit'), ('miss-refill', 'miss', 'Miss → L2'),
           ('scratchpad-read', 'scp-read', 'VPU scratchpad read'), ('tensorload', 'tensorload', 'TensorLoad'),
           ('refresh', 'refresh', 'Refresh?')],
    'l2': [('load-hit', 'load-hit', 'Load hit'), ('load-rbuf-hit', 'rbuf-hit', 'Read-buffer hit'),
           ('store-writeback', 'write-back', 'Write-back'), ('miss-refill', 'miss', 'Miss → L3'),
           ('no-refresh', 'refresh', 'Refresh?')],
    'l3': [('load_hit', 'load-hit', 'Load hit'), ('store', 'write-around', 'Write-around'),
           ('miss_and_refill', 'miss', 'Miss → DRAM'), ('atomic', 'atomic', 'Atomic'), ('refresh', 'refresh', 'Refresh?')],
    'scp': [('load_own', 'own-load', 'Own load'), ('store_own', 'own-store', 'Own store'),
            ('load_remote', 'remote-load', 'Remote load'), ('store_remote', 'remote-store', 'Remote store'),
            ('fill', 'fill', 'Fill'), ('atomic', 'atomic', 'Atomic'), ('miss_refill_refresh', 'refresh', 'Miss? Refresh?')],
    'dram': [('load', 'load', 'Load (closed row)'), ('row-hit', 'row-hit', 'Row hit'), ('row-conflict', 'row-conflict', 'Row conflict'),
             ('store', 'store', 'Store'), ('refresh', 'refresh', 'Refresh')],
}


FACT_ID = re.compile(r'\b(?:l1|l2|l3|scp|dram|g|gen|u|chip)\.[a-z0-9][\w.-]*[a-z0-9]\b')


def tidy(t):
    """A step's text as the page shows it: arrows and degrees typeset, no 'GENERIC' shouting beside a generic badge, no
    fact ids in the prose (the step's facts carry them), the functional model's trims called that."""
    if not isinstance(t, str):
        return t
    t = t.replace('->', '→').replace('+-', '±')
    t = re.sub(r'(\d) C\b', '\\1 °C', t)
    t = t.replace('The ET trim at reset is', "The functional model's reset trim is").replace('ET trim at reset:', "The functional model's reset trim:")
    t = re.sub(r'\s*\(GENERIC(?: detail)?\)', '', t)
    t = t.replace('(GENERIC: static storage)', '(static storage)').replace('GENERIC for latch arrays; ', 'for latch arrays; ')
    t = t.replace('transistor detail GENERIC', 'transistor detail generic').replace('are GENERIC;', 'are generic;')
    t = t.replace('; their circuit is GENERIC', '; their circuit is generic')
    t = re.sub(r'bitcell is u\.bitcell', 'the bitcell is asked', t)
    t = re.sub(r'split is u\.[\w.-]+', 'split is asked', t)
    t = re.sub(r' in l3\.energy-rails', '', t)
    t = re.sub(r',\s*' + FACT_ID.pattern + r'\)', ')', t)          # "..., l1.u-cell)" -> "...)"
    t = re.sub(r'\s*\((?:' + FACT_ID.pattern + r'(?:,\s*)?)+\)', '', t)  # "(dram.e.per-byte, dram.e.unmetered)" -> ""
    if 'GENERIC' in t or FACT_ID.search(t):
        raise SystemExit('tidy: step text still has a marker or a fact id: ' + t)
    return t


def circ(items, el_key, does_key):
    out = []
    for c in items or []:
        k, kn = split_kind(c.get('kind'))
        out.append({'el': c.get(el_key), 'does': c.get(does_key) or '', 'kind': k,
                    'kind_note': ' · '.join(x for x in [kn, c.get('note')] if x) or None})
    return out


def first_latency_energy(f):
    return f.get('latency'), f.get('energy')


STEPS = {}
for lv in LEVELS:
    STEPS[lv] = {}
    for src_name, name, title in ACCESS[lv]:
        steps = []
        measured = None
        if lv == 'l1':
            for key, f in STEPROWS[lv]:
                if f['topic'] != 'sequence/' + src_name:
                    continue
                kind, kn = split_kind(f['kind'])
                ck, ckn = split_kind(f.get('circuit_kind') or 'generic')
                cl = [] if (f.get('circuit') or '-').strip() in ('-', '') else [{'el': f['circuit'], 'does': '', 'kind': ck, 'kind_note': ckn}]
                steps.append({'n': f['step'], 'stage': f.get('stage'), 'block': f.get('block'), 'action': f.get('action'),
                              'latency': f.get('latency'), 'energy': f.get('energy'), 'kind': kind, 'facts': [key],
                              'circuit': cl})
        elif lv == 'l2':
            for key, f in STEPROWS[lv]:
                if f.get('sequence') != src_name:
                    continue
                kind, kn = split_kind(f['kind'])
                steps.append({'n': f['step'], 'stage': None, 'block': f.get('block'), 'action': f.get('action'),
                              'latency': f.get('latency'), 'energy': f.get('energy'), 'kind': kind, 'facts': [key],
                              'circuit': circ(f.get('circuit'), 'element', 'switches')})
        elif lv == 'dram':
            for key, f in STEPROWS[lv]:
                if f['seq'] != src_name:
                    continue
                kind, kn = split_kind(f['kind'])
                steps.append({'n': f['step'], 'stage': None, 'block': f.get('block'), 'action': f.get('statement'),
                              'latency': f.get('latency'), 'energy': f.get('energy'), 'kind': kind, 'facts': [key],
                              'circuit': circ(f.get('circuit'), 'what', 'does')})
        elif lv == 'l3':
            for s in RAW['l3']['access_sequence'][src_name]:
                circuit = circ(s.get('circuit'), 'element', 'action')
                kinds = [c['kind'] for c in circuit]
                steps.append({'n': s['n'], 'stage': None, 'block': s.get('block'), 'action': s.get('action'),
                              'latency': s.get('latency'), 'energy': s.get('energy'),
                              'kind': 'spec' if not kinds or 'spec' in kinds else kinds[0],
                              'facts': ['l3:' + i for i in s.get('facts', [])], 'circuit': circuit})
        elif lv == 'scp':
            acc = RAW['scp']['access_sequence'][src_name]
            title = title if not acc.get('title') else title
            measured = acc.get('measured')
            for s in acc['steps']:
                kind, kn = split_kind(s.get('kind'))
                # each step is a fact with the step's own source, as the L1, L2 and DRAM steps are (the research file
                # kept the scratchpad's steps apart from its facts)
                fid = 'scp.seq.%s.%02d' % (name, s['n'])
                key = 'scp:' + fid
                if key in FACTS:
                    raise SystemExit('duplicate fact ' + key)
                tl = '; '.join(x for x in [('Time: ' + s['latency']) if s.get('latency') else None,
                                           ('Energy: ' + s['energy']) if s.get('energy') else None] if x)
                FACTS[key] = {'id': fid, 'level': 'scp', 'topic': 'access-sequence', 'statement': tidy(lab_lead(
                                  '%s: %s' % (s.get('block'), s.get('does')))), 'value': None, 'unit': None,
                              'source': unlocal(s.get('source')), 'kind': kind, 'badge': BADGE[kind], 'kind_note': kn,
                              'cards': [], 'url': None, 'page': None, 'note': tidy(lab_lead(tl)) or None,
                              'caveat': caveat(s.get('source'))}
                steps.append({'n': s['n'], 'stage': s.get('domain'), 'block': s.get('block'), 'action': s.get('does'),
                              'latency': s.get('latency'), 'energy': s.get('energy'), 'kind': kind, 'facts': [key],
                              'circuit': circ(s.get('circuit'), 'device', 'switches')})
        if not steps:
            raise SystemExit(f'{lv}: no steps for {src_name}')
        for s in steps:
            for k in ('block', 'action', 'latency', 'energy', 'stage'):
                s[k] = tidy(lab_lead(s.get(k)))
            for c in s['circuit']:
                c['el'], c['does'], c['kind_note'] = tidy(c['el']), tidy(c['does']), tidy(c['kind_note'])
            # a step the page shows must cite something: its facts carry the sources
            if not s['facts']:
                raise SystemExit(f'{lv}/{name} step {s["n"]}: no fact, so no source on the page')
        if measured is None:
            ms = [s['latency'] for s in steps if s.get('latency')] + [s['energy'] for s in steps if s.get('energy')]
            measured = '; '.join(ms[-2:]) if ms else None
        STEPS[lv][name] = {'title': title, 'measured': tidy(measured), 'steps': steps}

# ---------------------------------------------------------------- printed numbers
# (key, fact key, value, text as in the statement, unit[, the text printed instead: a rounding of it])
N = [
    # L1: size and structure
    ('l1_kb', 'l1:l1.size', 4, '4 KB', 'KB'),
    ('l1_geom', 'l1:l1.size', 16, '16 sets x 4 ways x 64-byte lines', ''),
    ('l1_sets', 'l1:l1.size', 16, '16 sets', ''),
    ('l1_blocks', 'l1:l1.lram', 4, '4 LRAM', '', '4'),
    ('l1_rows', 'l1:l1.lram', 128, '128 rows', ''),
    ('l1_rowbits', 'l1:l1.lram', 64, '64 bits per row', '', '64 bits'),
    ('l1_macros', 'l1:l1.lram-macros', 8, '8 macros', ''),
    ('l1_macro', 'l1:l1.lram-macros', 128, '128 x 32', ''),
    ('l1_rowaddr', 'l1:l1.lram-addr', 7, '7 bits, 128 rows', ''),
    ('l1_half', 'l1:l1.lram-addr', 32, '32 bytes', ''),
    ('l1_tagbits', 'l1:l1.metadata', 33, '33 bits', ''),
    ('l1_entry', 'l1:l1.metadata', 35, '35 bits', ''),
    ('l1_meta64', 'l1:l1.metadata', 64, '64 entries', ''),
    ('l1_rf16', 'l1:l1.metadata', 16, '16 entries', ''),
    ('l1_lru', 'l1:l1.lru', 16, '16 bits per set', ''),
    ('l1_lru44', 'l1:l1.lru', 4, '4 x 4 order matrix', ''),
    ('l1_cmp', 'l1:l1.phased', 4, '4', ''),
    ('l1_mh', 'l1:l1.mh', 2, '2', ''),
    ('l1_rq', 'l1:l1.rq', 8, '8 entries', ''),
    ('l1_tlb', 'l1:l1.tlb', 8, '8-entry TLB', '', '8 entries'),
    ('l1_vpu', 'l1:l1.vpu-port', 256, '256-bit', ''),
    ('l1_vpu_lat', 'l1:l1.vpu-scp-read', 2, '2', ''),
    ('l1_scp_kb', 'l1:l1.modes', 3, '3 KB', ''),
    ('l1_scp_sets', 'l1:l1.modes', 0, 'sets 0-11', ''),
    ('l1_h0sets', 'l1:l1.modes', 12, 'hart 0 sets 12-13', ''),
    ('l1_h1sets', 'l1:l1.modes', 14, 'hart 1 sets 14-15', ''),
    ('l1_hart', 'l1:l1.firmware-mode', 512, '512 B', ''),
    ('l1_knee_in', 'l1:l1.knee', 5.256, '5.256 at 512 B', '', '5.256 cycles at 512 B'),
    ('l1_knee_out', 'l1:l1.knee', 39.0, '39.0 at 768 B', '', '39.0 cycles at 768 B'),
    ('l1_lat', 'l1:l1.latency', 5.25, '5.25 cycles', ''),
    ('l1_ns', 'l1:l1.latency', 8.75, '8.75 ns', ''),
    ('l1_lat5', 'l1:l1.latency-5', 5, '5', ''),
    ('l1_e', 'l1:l1.e-vload', 17.3, '17.3 pJ', ''),
    ('l1_e_pjb', 'l1:l1.e-vload', 0.54, '0.54 pJ/B', ''),
    ('l1_e0', 'l1:l1.e-vload', 12.5, '12.5 pJ', ''),
    ('l1_flw', 'l1:l1.e-scalar', 14.0, 'flw 14.0 pJ', '', '14.0 pJ'),
    ('l1_fsw', 'l1:l1.e-scalar', 25.5, 'fsw 25.5 pJ', '', '25.5 pJ'),
    ('l1_vst', 'l1:l1.e-vstore', 23.0, '23.0 pJ', ''),
    ('l1_ratio', 'l1:l1.e-store-ratio', 1.82, '1.82x', ''),
    ('l1_fill', 'l1:l1.e-fill', 238, '238 pJ', ''),
    ('l1_fill0', 'l1:l1.e-fill', 101, '101 pJ', ''),
    ('l1_miss_rb', 'l1:l1.miss-l2', 36, '36 cycles', ''),
    ('l1_miss_l2', 'l1:l1.miss-l2', 47, '47', ''),
    ('l1_miss_h1', 'l1:l1.miss-l2', 3, 'hart 1 pays 3 more', ''),
    ('l1_tl', 'l1:l1.tl-latency', 160.4, '160.4 cycles', ''),
    ('l1_tl16', 'l1:l1.tl-latency', 16, '16 lines', ''),
    ('l1_tlrate', 'l1:l1.tl-rate', 10, 'About 10 cycles', '', 'about 10 cycles'),
    ('l1_tl4', 'l1:l1.tensorload', 4, 'up to 4 L2 transfers', ''),
    ('l1_v', 'l1:l1.voltage', 0.517, '0.517 V', ''),
    ('l1_rail', 'l1:l1.rail', 83, '83%', ''),
    ('l1_rail_sram', 'l1:l1.rail', 2, '2% on the SRAM rail', '', '2%'),
    ('l1_bw', 'l1:l1.bw', 14.5, '14.5 TB/s', ''),
    ('l1_tr', 'l1:l1.transistors', 0.33, '0.26-0.39 million', ''),
    ('l1_bits', 'l1:l1.bits', 32768, '32,768 data bits', ''),
    ('l1_s4', 'l1:l1.s4-arb', 7, '7', ''),
    ('l1_s0', 'l1:l1.s0-arb', 6, '6', ''),
    ('l1_stages', 'l1:l1.pipeline', 6, '6', ''),
    ('g_latch_t', 'l1:g.latch-cell', 10, 'about 8-12 transistors per bit', '', '8–12 transistors per bit'),
    ('g_mux', 'l1:g.latch-read', 128, '128:1 per output bit', ''),
    ('g_ff_t', 'l1:g.flipflop', 22, 'about 20-24 transistors', ''),
    ('g_6t', 'l1:g.sram-6t', 6, '6', ''),
    ('g_cmp33', 'l1:g.compare', 33, '33 bits', ''),
    ('g_xnor_t', 'l1:g.compare', 10, 'about 8-12 transistors', '', '8–12 transistors'),
    # L2
    ('l2_sc', 'l2:l2.sc.what', 4, '4 MB shire cache', '', '4 MB'),
    ('l2_nb', 'l2:l2.sc.what', 4, "4 neighbourhoods (32 minions)", ''),
    ('l2_part', 'l2:l2.partition.default', 2.5, '2.5 MB scratchpad, 0.5 MB L2, 1 MB L3', ''),
    ('l2_kb', 'l2:l2.partition.rows', 512, '512 KB', ''),
    ('l2_sets', 'l2:l2.partition.rows', 640, 'sets 0x280-0x2FF', ''),
    ('l2_128', 'l2:l2.partition.rows', 128, '128 of the 1,024 physical sets', ''),
    ('l2_banks', 'l2:l2.banks', 4, 'four identical banks', ''),
    ('l2_sub', 'l2:l2.subbanks', 4, 'four sub-banks', ''),
    ('l2_reqq', 'l2:l2.reqq', 64, '64-entry request queue', '', '64 entries'),
    ('l2_reqq_adj', 'l2:l2.reqq', 64, '64-entry request queue', '', '64-entry'),
    ('l2_reqq21', 'l2:l2.reqq', 21, '21', ''),
    ('l2_rbuf', 'l2:l2.rbuf', 8, '8-entry fully associative', '', '8 lines'),
    ('l2_rbuf_adj', 'l2:l2.rbuf', 8, '8-entry fully associative', '', '8-line'),
    ('l2_rbuf2k', 'l2:l2.rbuf', 2, '2 KB per shire', ''),
    ('l2_cbuf', 'l2:l2.cbuf', 32, '32-entry coalescing buffer', '', '32 entries'),
    ('l2_dataq', 'l2:l2.dataq', 64, '64 x 4 x 144 bits', ''),
    ('l2_stages', 'l2:l2.stages', 15, '15', ''),
    ('l2_tag', 'l2:l2.tag-ram', 116, '116 bits', ''),
    ('l2_tag23', 'l2:l2.tag-ram', 23, '23 bits + 6 ECC bits', ''),
    ('l2_state', 'l2:l2.tag-state-ram', 40, '40-bit row', ''),
    ('l2_line', 'l2:l2.data-ram', 576, '576 bits', ''),
    ('l2_panel_w', 'l2:l2.data-ram', 144, '144-bit-wide panels', '', '144 bits'),
    ('l2_rows', 'l2:l2.data-ram', 4096, '4,096 rows', ''),
    ('l2_mdata', 'l2:l2.macro.data', 4096, '4,096 words x 144 bits', ''),
    ('l2_mdata_adj', 'l2:l2.macro.data', 4096, '4,096 words x 144 bits', '', '4,096-word × 144-bit'),
    ('l2_mtag', 'l2:l2.macro.tag', 1024, '1,024 words x 116 bits', ''),
    ('l2_mstate', 'l2:l2.macro.state', 1024, '1,024 words x 40 bits', ''),
    ('l2_mdata_s', 'l2:l2.macro.data', 4096, '4,096 words x 144 bits', '', '4,096 × 144'),
    ('l2_mtag_s', 'l2:l2.macro.tag', 1024, '1,024 words x 116 bits', '', '1,024 × 116'),
    ('l2_mstate_s', 'l2:l2.macro.state', 1024, '1,024 words x 40 bits', '', '1,024 × 40'),
    ('l2_rm0', 'l2:l2.trim', 585, 'RM0 = VMIN 585 mV, Vnom 650', ''),
    ('l2_rm0n', 'l2:l2.trim', 650, 'nominal 650mV', '', '650 mV'),
    ('l2_trims', 'l2:l2.trim', 0, 'RM 0, WA 7, RA 1, WPULSE 0', ''),
    ('l2_rm5', 'l2:l2.trim', 855, 'RM5 at 855 mV', ''),
    ('l2_v', 'l2:l2.voltage.idle', 705, '705', 'mV'),
    ('l2_v_rng', 'l2:l2.voltage.idle', 705, '703-707 mV', ''),
    ('l2_vmin_rng', 'l2:l2.voltage.idle', 513, 'minion rail 513-522 mV', ''),
    ('l2_rail750', 'l2:l2.rail.sram', 750, '750 mV', ''),
    ('l2_set705', 'l2:l2.rail.sram', 705, '705 mV', '', '705 mV'),
    ('l1_vlim', 'l1:l1.voltage', 400, '400-620 mV', ''),
    ('l1_v800', 'l1:l1.voltage', 0.618, '0.618 V at 800', '', '0.618 V at 800 MHz'),
    ('l2_vmin_st', 'l2:l2.trim', 540, 'VMIN 540 mV', '', '540 mV'),
    ('l2_limits', 'l2:l2.voltage.limits', 660, '660-850 mV', ''),
    ('l2_lat', 'l2:l2.lat.measured', 47, '47.00 cycles', '', '47 cycles'),
    ('l2_lat_rb', 'l2:l2.lat.measured', 36, '36.00 cycles', '', '36 cycles'),
    ('l2_ns', 'l2:l2.lat.measured', 78, '78 ns', ''),
    ('l2_ns_rb', 'l2:l2.lat.measured', 60, '60 ns', ''),
    ('l2_spec', 'l2:l2.lat.spec', 21, '21', ''),
    ('l2_spec_rb', 'l2:l2.lat.spec', 10, '10', ''),
    ('l2_spec_miss', 'l2:l2.lat.spec', 34, '34', ''),
    ('l2_over', 'l2:l2.lat.overhead', 26, '26 cycles', ''),
    ('l2_nbr6', 'l2:l2.path.nbr-request', 6, '6 cycles', ''),
    ('l2_rsp6', 'l2:l2.nbr.response', 6, '6 cycles minimum', '', '6 cycles'),
    ('l2_link', 'l2:l2.path.widths', 512, '512 bits', ''),
    ('l2_req256', 'l2:l2.path.widths', 256, '256 bits wide', '', '256 bits'),
    ('l2_bw', 'l2:l2.bw.measured', 2.45, '2.45 TB/s', ''),
    ('l2_bw128', 'l2:l2.bw.measured', 128, '128 B per shire-cycle', ''),
    ('l2_bw256', 'l2:l2.bw.measured', 256, '256 B', ''),
    ('l2_e', 'l2:l2.e.level', 3.11, '3.11 pJ/B', ''),
    ('l2_e_line', 'l2:l2.e.level', 199, '199 pJ', ''),
    # the split of the same arrays read as the own scratchpad, on each card (computed above from manual.json, since 28 Sep)
    ('l2_rails_sram', 'l2:l2.e.rails', rnd(SC('scp', 'sram')[0]), RS['scp_sram'], ''),
    ('l2_rails_min', 'l2:l2.e.rails', rnd(SC('scp', 'minion')[0]), RS['scp_min'], ''),
    ('l2_e_scp', 'l2:l2.e.scp-contents', 144, 'about 144 vs 282 pJ', ''),
    ('l2_e_wr', 'l2:l2.e.tload-tstore', 8.58, '4.65 / 8.58 pJ/B', ''),
    ('l2_fsw', 'l2:l2.e.scalar', 774, '774 pJ', ''),
    ('l2_flw', 'l2:l2.e.scalar', 336, '336 pJ', ''),
    ('l2_leak', 'l2:l2.leak', 2.0, '2.00 W', ''),
    ('l2_leak67', 'l2:l2.leak', 1.70, '1.70 W at 67 C', '', '1.70 W at 67 °C'),
    ('l2_leak82', 'l2:l2.leak', 2.73, '2.73 W at 82 C', '', '2.73 W at 82 °C'),
    ('l2_tr', 'l2:l2.transistors', 243, '243 million', ''),
    ('l2_macros', 'l2:l2.macro.count', 64, '64 data macros', ''),
    ('l2_macros96', 'l2:l2.macro.count', 96, '96', ''),
    ('l2_ecc', 'l2:l2.ecc', 8, '8 per 64 data bits', ''),
    ('l2_ramdelay', 'l2:l2.ramdelay', 2, '2', ''),
    ('l2_sleep', 'l2:l2.sleep', 49.5, '49.5 cycles', ''),
    ('l2_mhz', 'l2:l2.freq', 600, '600 MHz', ''),
    ('l2_rbuf_plateau', 'l2:l2.rbuf.enabled', 36, '36-cycle plateau', ''),
    # the shared panel and cell (generic circuits; ET numbers only where a fact gives them)
    ('leak_mb', 'l3:l3.leakage', 19.6, '19.6 mW per MB', ''),
    ('scp_rows', 'scp:scp.m0-rows', 2560, 'lowest 2,560', '', '2,560'),
    ('l3_rows', 'l3:l3.same-arrays', 3072, 'words 3,072-4,095', ''),
    ('half4', 'scp:scp.g-half-select', 4, 'four bitline pairs swing', ''),
    # the ladder (DESIGN.md §2.7)
    ('lad_l3', 'l3:l3.lat-fit', 110.5, '110.5 + 11.99 cycles per mesh hop', '', '110.5 cycles + 12 a hop'),
    ('lad_dram', 'dram:dram.lat.typical', 299, '299 cycles', ''),
    ('lad_e_scp', 'scp:scp.e-own', 2.25, '2.25', ''),
    ('scp_vmin', 'scp:scp.vmin-table', 585, '585 mV', ''),
    ('lad_e_scp1', 'scp:scp.e-own', 4.40, '4.40', ''),
    ('lad_e_l3', 'l3:l3.energy', 14.7, '14.7 pJ', ''),
    ('lad_e_dram', 'dram:dram.e.per-byte', 114.6, '114.6 pJ', ''),
    ('lad_scp_lat', 'scp:scp.lat-own', 47, '47.00 cycles', '', '47 cycles'),
    # L3 (part 2)
    ('l3_mb', 'l3:l3.what', 32, '32 MB', ''),
    ('l3_fit_c', 'l3:l3.lat-fit', 110.5, '110.5 + 11.99 cycles per mesh hop', '', '110.5 + 12 cycles per mesh hop'),
    ('l3_fit_hop', 'l3:l3.lat-fit', 11.99, '11.99', ''),
    ('l3_109', 'l3:l3.lat-by-home', 109, '109 cycles', ''),
    ('l3_218', 'l3:l3.lat-by-home', 218, '218 at 9 hops', ''),
    ('l3_72', 'l3:l3.lat-clock-split', 72.2, '72.2 cycles', ''),
    ('l3_61', 'l3:l3.lat-clock-split', 61.4, '61.4 ns', ''),
    ('l3_20ns', 'l3:l3.lat-clock-split', 20, '20 ns per mesh hop', ''),
    ('l3_mean', 'l3:l3.mean-hops', 3.75, '3.75 hops', ''),
    ('l3_mean_c', 'l3:l3.mean-hops', 155, 'about 155 cycles (258 ns)', ''),
    ('l3_bw', 'l3:l3.bw', 0.98, '0.98 TB/s', ''),
    ('l3_home1498', 'l3:l3.home-measured', 1498, '1,498 of 1,500 random lines', ''),
    ('l3_home99', 'l3:l3.home-measured', 99.4, '99.4-99.97%', ''),
    ('l3_tsend', 'l3:l3.tsend-compare', 150, '150 + 12.02 cycles per hop', '', '150 + 12 cycles per hop'),
    ('l3_hopcyc', 'l3:l3.hop', 12, '12 cycles', ''),
    ('l3_hopns', 'l3:l3.hop', 20, '20 ns', ''),
    ('l3_hopmm', 'l3:l3.wire-energy', 3.72, '3.72 mm', ''),
    ('l3_fj', 'l3:l3.wire-energy', 36.2, '36.2 fJ', ''),
    ('l3_hop69', 'l3:l3.wire-energy', 69, 'about 69 pJ', '', '69 pJ'),
    # an L3 read through the mesh on each card, and a mesh hop per line (computed above from manual.json, since 28 Sep)
    ('l3_rails_sram', 'l3:l3.energy-per-load', rnd(SC('l3', 'sram')[0]), RS['l3_sram'], ''),
    ('l3_rails_mesh', 'l3:l3.energy-per-load', rnd(SC('l3', 'noc')[0]), RS['l3_noc'], ''),
    ('l3_rails_min', 'l3:l3.energy-per-load', rnd(SC('l3', 'minion')[0]), RS['l3_min'], ''),
    ('l3_hop_r', 'l3:l3.energy-per-load', rnd(64 * HOP['random']), RS['hop_r'], ''),
    ('l3_hop_z', 'l3:l3.energy-per-load', rnd(64 * HOP['zeros']), RS['hop_z'], ''),
    ('l3_hop_rb', 'l3:l3.wire-energy', rnd(64 * HOP['random']), RS['hop_rb'], ''),
    ('l3_e_line', 'l3:l3.energy', 0.94, '0.94 nJ', ''),
    ('l3_e_cont', 'l3:l3.energy-contents', 7.6, '7.6 vs 19.3 pJ/B', ''),
    ('l3_mesh_v', 'l3:l3.mesh-rail', 485, '485 mV', ''),
    ('l3_noc', 'l3:l3.mesh-rail', 400, '400 MHz', ''),
    ('l3_sram_v', 'l3:l3.sram-rail', 705, '705 mV', ''),
    ('l3_clk', 'l3:l3.clock', 600, '600 MHz', ''),
    ('l3_req_bits', 'l3:l3.flits', 80, 'about 75-85 bits', ''),
    ('l3_reply', 'l3:l3.flits', 512, 'one 512-bit data beat', ''),
    ('l3_ports_w', 'l3:l3.ports', 512, '512 bits, one request per cycle each', ''),
    ('l3_reqq21', 'l3:l3.reqq', 21, '21 entries', ''),
    ('l3_ram2', 'l3:l3.ram-delay', 2, '2 cycles by default', '', '2 cycles'),
    ('l3_spec30', 'l3:l3.spec-latency', 30, 'hit 30', '', '30 shire clocks'),
    ('l3_miss42', 'l3:l3.spec-latency', 42, 'miss 42', '', '42 shire clocks'),
    ('l3_slice', 'l3:l3.slice-arith', 1, '4 banks x 4 sub-banks x 256 sets x 4 ways x 64 B = 1 MB', '', '4 banks × 4 sub-banks × 256 sets × 4 ways × 64 B = 1 MB'),
    ('l3_lines', 'l3:l3.slice-arith', 16384, '16,384 lines per shire', ''),
    ('l3_bank_lines', 'l3:l3.slice-arith', 4096, '4,096 per bank', '', '4,096 lines per bank'),
    ('l3_rm55', 'l3:l3.rail-vs-trim', 55, "55 mV above the RM0 row's 650 mV nominal", ''),
    ('l3_leakW', 'l3:l3.leakage', 0.63, 'about 0.63 W', ''),
    ('l3_dram91', 'l3:l3.dram-leg', 91, '91 + 12 cycles per hop', ''),
    ('l3_atomic', 'l3:l3.atomic', 10.0, '10.00 cycles', '', '10 cycles'),
    ('l3_atom216', 'l3:l3.atomic', 216, '216 cycles round trip', ''),
    ('l3_atomW', 'l3:l3.atomic-rails', 3.99, '3.99 W', ''),
    ('l3_coal', 'l3:l3.writearound', 32, '32 entries per bank', ''),
    # the scratchpad (part 2)
    ('scp_size', 'scp:scp.size', 2.5, '2.5 MB', ''),
    ('scp_80', 'scp:scp.size', 80, '80 MB', ''),
    ('scp_rb36', 'scp:scp.lat-own', 36, 'read-buffer hit 36.00', '', '36 cycles'),
    ('scp_ns', 'scp:scp.lat-own', 78, '78 ns', ''),
    ('scp_split26', 'scp:scp.lat-split', 26, '~26', '', '~26 cycles'),
    ('scp_remote', 'scp:scp.lat-remote', 99.84, '99.84 + 12.00 cycles per mesh hop', '', '99.8 + 12 cycles per mesh hop'),
    ('scp_hop12', 'scp:scp.lat-remote', 12, '12.00 cycles per mesh hop', '', '12 cycles'),
    ('scp_rsplit', 'scp:scp.lat-remote-split', 65.95, '65.95 minion cycles + 56.48 ns + 20.00 ns per hop', ''),
    ('scp_leave', 'scp:scp.lat-leave', 52.84, 'about 53 cycles', ''),
    ('scp_tl', 'scp:scp.tl-one', 160.1, '16 lines 160.1', '', '16 lines in 160.1 cycles'),
    ('scp_tl10', 'scp:scp.tl-pipelining', 10, '10.0 cycles', ''),
    ('scp_tlrows', 'scp:scp.tensorload', 16, '16 rows of 64 B', ''),
    ('scp_bw', 'scp:scp.bw-own', 2.46, '2.46 TB/s', ''),
    ('scp_4b', 'scp:scp.bw-own', 4.0, '4.0 B per minion-cycle', ''),
    ('scp_128', 'scp:scp.bw-own', 128, '128 B per shire-cycle', ''),
    ('scp_50', 'scp:scp.bw-one-neigh', 50, 'about 50 B per shire-cycle', ''),
    ('scp_614', 'scp:scp.bw-bank-stride', 614, '614 GB/s', ''),
    ('scp_bw_st', 'scp:scp.bw-store', 1.23, '1.23 TB/s', ''),
    ('scp_bw_rem', 'scp:scp.bw-remote', 0.96, '0.96 TB/s', ''),
    ('scp_69', 'scp:scp.e-rails-load', 69, '69% SRAM rail', '', '69%'),
    ('scp_182', 'scp:scp.e-sram-line', 182, '182 and 92 pJ', '', '182 pJ (92 on zeros)'),
    ('scp_389', 'scp:scp.e-sram-write', 389, '389 and 209 pJ', '', '389 pJ (209 on zeros)'),
    ('scp_21x', 'scp:scp.e-sram-write', 2.1, '2.1x and 2.3x', ''),
    ('scp_90', 'scp:scp.e-data', 90, '90 pJ more per line', ''),
    ('scp_e_st', 'scp:scp.e-catalogue', 8.58, '4.65 / 8.58', ''),
    ('scp_rem0', 'scp:scp.e-remote', 5.10, '5.10 pJ/B', ''),
    ('scp_rem1', 'scp:scp.e-remote', 11.8, '11.8', ''),
    ('scp_hop_e', 'scp:scp.e-hop', 1.80, '0.67 pJ/B on zeros and 1.80', '', '0.67 / 1.80 pJ/B'),
    ('scp_relay', 'scp:scp.relay', 8.92, '116.2 / 8.92 / 4.34 pJ/B', ''),
    ('scp_relay_bw', 'scp:scp.relay', 592.5, '592.5 GB/s against 47.7', ''),
    ('scp_atomic', 'scp:scp.atomic', 10.0, '10.00 cycles', '', '10 cycles'),
    ('scp_starve', 'scp:scp.starve', 22, '22 or more minions', ''),
    ('scp_margin', 'scp:scp.rail-margin', 120, '120 mV above', ''),
    ('scp_panels64', 'scp:scp.panel-count', 64, '64 data panels', ''),
    ('scp_576', 'scp:scp.line-read-panels', 576, '576 bits (512 data + 64 ECC)', ''),
    ('scp_16B', 'scp:scp.write-granule', 16, '16 B', ''),
    ('scp_rm5', 'scp:scp.vmin-table', 855, 'Vmin 855 mV (Vnom 950)', '', '855 / 950'),
    ('scp_rm4', 'scp:scp.vmin-table', 765, '765 (850)', '', '765 / 850'),
    ('scp_rm3', 'scp:scp.vmin-table', 675, '675 (750)', '', '675 / 750'),
    ('scp_rm2', 'scp:scp.vmin-table', 650, '650 (722)', '', '650 / 722'),
    ('scp_rm1', 'scp:scp.vmin-table', 630, '630 (700)', '', '630 / 700'),
    ('scp_rm0', 'scp:scp.vmin-table', 585, '585 mV (650)', '', '585 / 650'),
    # DRAM (part 2)
    ('dr_gb', 'dram:dram.org.capacity', 32, '32 GB', ''),
    ('dr_ch', 'dram:dram.topo.memshires', 16, '16 channels', ''),
    ('dr_mts', 'dram:dram.ctl.clock', 3733, '3,733 MT/s', ''),
    ('dr_dfi', 'dram:dram.ctl.clock', 933, '933 MHz', ''),
    ('dr_dclk', 'dram:dram.ctl.clock', 1866, '1,866 MHz', ''),
    ('dr_peak', 'dram:dram.ctl.peak-bw', 119.5, '119.5 GB/s', ''),
    ('dr_peakch', 'dram:dram.ctl.peak-bw', 7.47, '7.47 GB/s', ''),
    ('dr_bw', 'dram:dram.ctl.measured-bw', 76, '76 GB/s', ''),
    ('dr_noc32', 'dram:dram.topo.noc-port', 32, '32 GB/s', ''),
    ('dr_500', 'dram:dram.lat.typical', 500, '500 ns', ''),
    ('dr_chase', 'dram:dram.lat.chase', 297, '296.6-297.1 cycles', ''),
    ('dr_clk', 'dram:dram.lat.clock-scaling', 86.3, '86.3 minion cycles + 344.8 ns', ''),
    ('dr_model', 'dram:dram.lat.model', 91, '110 + 12 x hops(requester -> L3 home) + 91 + 12 x hops(L3 home -> memory shire) cycles', '', '110 + 12 × hops(R → L3 home) + 91 + 12 × hops(L3 home → M) cycles'),
    ('dr_mshops', 'dram:dram.lat.ms-hops', 12, '12-84 cycles', ''),
    ('dr_share', 'dram:dram.lat.dram-chip-share', 28, 'about 28 cycles', ''),
    ('dr_rl17', 'dram:dram.lat.dram-chip-share', 17, '17 cycles', ''),
    ('dr_ms63', 'dram:dram.lat.dram-chip-share', 63, 'at most about 63 cycles (~105 ns)', ''),
    ('dr_ms63s', 'dram:dram.lat.dram-chip-share', 63, 'at most about 63 cycles', '', '≤ 63 cycles'),
    ('dr_c110', 'dram:dram.lat.model', 110, '110', ''),
    ('dr_fit97', 'dram:dram.lat.model', 97.0, '97.0%', ''),
    ('dr_fit93', 'dram:dram.lat.model', 92.9, '92.9%', ''),
    ('dr_trefw', 'dram:gen.refresh', 32, '32 ms', ''),
    ('dr_8192', 'dram:gen.refresh', 8192, '8,192 refresh commands per 32 ms', '', '8,192 REFab per 32 ms'),
    ('dr_rowhit', 'dram:dram.lat.row-hit', 11.6, '11-12 cycles', ''),
    ('dr_conf37', 'dram:dram.lat.row-conflict', 37, 'about +37 cycles', '', '37 cycles'),
    ('dr_seq10', 'dram:dram.lat.row-sequential', 10, 'about +9-10 cycles', '', '9–10 cycles'),
    ('dr_ref', 'dram:dram.lat.refresh-period', 2325.4, '2,325.4 cycles = 3.876 us', '', '2,325.4 cycles (3.876 µs)'),
    ('dr_ref208', 'dram:dram.lat.refresh-period', 208, 'up to 208 extra cycles (347 ns)', '', '208 cycles (347 ns)'),
    ('dr_duty', 'dram:dram.ctl.refresh-duty', 7.2, '7.2%', ''),
    ('dr_trcd', 'dram:dram.ctl.tRCD', 18.2, '18.2 ns', ''),
    ('dr_trcd_c', 'dram:dram.ctl.tRCD', 10.9, '10.9 minion cycles', ''),
    ('dr_trp', 'dram:dram.ctl.tRP', 18.2, '18.2 ns', ''),
    ('dr_trc', 'dram:dram.ctl.tRAS-tRC', 63.2, '63.2 ns', ''),
    ('dr_rl', 'dram:dram.ctl.RL-WL', 19.3, '19.3 ns', ''),
    ('dr_wl', 'dram:dram.ctl.RL-WL', 8.6, '8.6 ns', ''),
    ('dr_burst', 'dram:dram.ctl.burst', 4.3, '4.3 ns', ''),
    ('dr_nwr', 'dram:dram.ctl.tWR', 34, '34 DRAM clocks (18.2 ns)', ''),
    ('dr_trefi', 'dram:dram.ctl.refresh-mode', 3.875, '3.875 us', '', '3.875 µs'),
    ('dr_trfc', 'dram:dram.ctl.refresh-mode', 280.7, '280.7 ns', ''),
    ('dr_dfiupd', 'dram:dram.ctl.dfi-update', 70, '70-280 us', '', '70–280 µs'),
    ('dr_cam', 'dram:dram.ctl.cam', 32, '32 entries', ''),
    ('dr_runs', 'dram:dram.ctl.scheduling', 15, 'up to 15 transactions', ''),
    ('dr_p0', 'dram:dram.ctl.ports', 15, 'priority 15', '', '15'),
    ('dr_p1', 'dram:dram.ctl.ports', 8, 'priority 8', '', '8'),
    ('dr_perf', 'dram:dram.ctl.perfmon', 40, '40-bit cycle counter at 933 MHz', ''),
    ('dr_geom', 'dram:dram.org.geometry', 8, '8 banks x 131,072 rows x 2 KB pages', '', '8 banks × 131,072 rows × 2 KB pages'),
    ('dr_rows', 'dram:dram.org.geometry', 131072, '131,072 rows', ''),
    ('dr_16k', 'dram:dram.org.geometry', 16384, '16,384 bits', ''),
    ('dr_16k_n', 'dram:dram.org.geometry', 16384, '16,384 bits', '', '16,384'),
    ('dr_1_32', 'dram:dram.org.line-vs-page', 32, '1/32', ''),
    ('dr_512of', 'dram:dram.org.line-vs-page', 512, '512 of the 16,384 bits', ''),
    ('dr_256', 'dram:gen.column', 256, '256 bits', ''),
    ('dr_gen16', 'dram:gen.refresh', 16, '16 rows of each bank per REFab', ''),
    ('dr_e_line', 'dram:dram.e.per-byte', 7.3, '7.3 nJ', ''),
    ('dr_e0', 'dram:dram.e.data', 94.6, '94.6 pJ/B on zeros', '', '94.6 pJ/B'),
    ('dr_e1', 'dram:dram.e.data', 132.6, '132.6 on random data', '', '132.6 pJ/B'),
    ('dr_st0', 'dram:dram.e.data', 94.4, '94.4', ''),
    ('dr_st1', 'dram:dram.e.data', 141.9, '141.9', ''),
    ('dr_unmet', 'dram:dram.e.unmetered', 70, '70%', ''),
    ('dr_73', 'dram:dram.e.unmetered', 72.7, '72.7', ''),
    ('dr_rows_e', 'dram:dram.e.rows', 155.9, 'row hits 155.9, row misses 158.5', ''),
    ('dr_wb', 'dram:dram.e.writeback', 341.5, '341.5 pJ/B', ''),
    ('dr_vs', 'dram:dram.e.vs-scp', 30, '30x', ''),
    ('dr_vddr', 'dram:dram.pwr.rails', 0.8, '0.8 V set point', ''),
    ('dr_vddq', 'dram:dram.pwr.rails', 640, '640 mV set point', '', '640 mV'),
    ('dr_vmeas', 'dram:dram.pwr.droop', 767, '767-768 mV', ''),
    ('dr_droop', 'dram:dram.pwr.droop', 0.87, '0.86-1.01 mV per watt', ''),
    ('dr_vddq6', 'dram:gen.io', 0.6, '0.6 V VDDQ', '', '0.6 V'),
    ('g_trefi_max', 'dram:gen.jedec-match', 3.904, '3.904 us', '', '3.904 µs'),
]

DASH = str.maketrans({'–': '-', '‑': '-', '−': '-', ' ': ' ', 'µ': 'u', 'μ': 'u', '×': 'x'})
NUMS = re.compile(r'\d[\d,]*(?:\.\d+)?')


def rounds_to(src, disp):
    """True when every number in disp is the matching number of src rounded to disp's decimals."""
    a, b = NUMS.findall(src), NUMS.findall(disp)
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        dec = len(y.split('.')[1]) if '.' in y else 0
        if abs(float(x.replace(',', '')) - float(y.replace(',', ''))) > 0.5 * 10 ** -dec + 1e-9:
            return False
    return True


num = {}
for row in N:
    key, fk, v, t, u = row[:5]
    shown = row[5] if len(row) > 5 else None
    if key in num:
        raise SystemExit('duplicate number ' + key)
    if fk not in FACTS:
        raise SystemExit(f'{key}: no fact {fk}')
    f = FACTS[fk]
    s = f['statement'].translate(DASH)
    val_ok = isinstance(f['value'], (int, float)) and abs(f['value'] - v) < 1e-9 and t == str(v)
    if t.translate(DASH) not in s and not val_ok:
        raise SystemExit(f'{key}: "{t}" not in {fk}: {f["statement"]}')
    if shown and not rounds_to(t.translate(DASH), shown.translate(DASH)):
        raise SystemExit(f'{key}: "{shown}" is not a rounding of "{t}"')
    disp = shown or t
    num[key] = {'v': v, 't': re.sub(r'(?<=\d)-(?=\d)', '–', disp), 'u': u, 'f': fk}
    if shown:
        num[key]['src_t'] = t

# ---------------------------------------------------------------- what each details panel lists
def L(lv, *ids):
    return [i if ':' in i else lv + ':' + i for i in ids]


PARTS = {
    'l1': {
        'overview': L('l1', 'l1.size', 'l1.lram', 'l1.voltage', 'l1.rail', 'l1.latency', 'l1.e-vload', 'l1.bw', 'l1.noncoherent',
                      'l1.no-sleep', 'l1.lv-region', 'l1.why-latch', 'l1.u-why', 'l1.u-floorplan'),
        'pipeline': L('l1', 'l1.pipeline', 'l1.s0-arb', 'l1.latency-5', 'l1.latency', 'l1.u-cycles'),
        'dcache': L('l1', 'l1.size', 'l1.metadata', 'l1.phased', 'l1.lram', 'l1.lram-macros', 'l1.write-policy', 'l1.store-rmw',
                    'l1.states', 'l1.noncoherent', 'l1.bits', 'l1.no-parity', 'l1.u-parity'),
        'tlb': L('l1', 'l1.tlb'),
        'mh': L('l1', 'l1.mh', 'l1.miss-l2', 'l1.write-policy', 'l1.u-cycles'),
        'rq': L('l1', 'l1.rq'),
        'vpu': L('l1', 'l1.vpu-port', 'l1.vpu-scp-read'),
        'tl': L('l1', 'l1.tensorload', 'l1.tl-latency', 'l1.tl-rate'),
        'ports': L('l1', 'l1.lv-region', 'l1.miss-l2', 'l1.write-policy', 'l2:l2.vc-fifo', 'l2:l2.path.nbr-request'),
        'rail': L('l1', 'l1.rail', 'l1.voltage', 'l1.lv-region', 'l1.why-latch', 'l1.u-why', 'l1.no-sleep'),
        'tags': L('l1', 'l1.metadata', 'l1.states', 'l1.latch-rf'),
        'valid': L('l1', 'l1.metadata', 'g.flipflop'),
        'lru': L('l1', 'l1.lru', 'g.flipflop'),
        'cmp': L('l1', 'l1.phased', 'g.compare'),
        'blocks': L('l1', 'l1.lram', 'l1.lram-macros', 'l1.bank-enables', 'l1.lram-addr', 'l1.lram-model', 'l1.u-cell'),
        's4arb': L('l1', 'l1.s4-arb', 'l1.store-rmw'),
        'setmap': L('l1', 'l1.modes', 'l1.scp-impl', 'l1.firmware-mode', 'l1.knee'),
        'lram': L('l1', 'l1.lram', 'l1.lram-macros', 'l1.lram-addr', 'l1.lram-model', 'l1.latch-rf', 'l1.icg-cells', 'l1.u-cell',
                  'l1.u-library'),
        'wdec': L('l1', 'l1.latch-rf', 'l1.icg-cells', 'g.latch-write', 'l1.u-library'),
        'wlatch': L('l1', 'l1.latch-rf', 'l1.icg-cells'),
        'rdreg': L('l1', 'l1.latch-rf', 'g.latch-read'),
        'rows': L('l1', 'l1.lram-addr', 'l1.lram', 'l1.bank-enables'),
        'row': L('l1', 'g.latch-read', 'g.latch-write', 'l1.lram', 'l1.latch-rf'),
        'muxtree': L('l1', 'g.latch-read', 'l1.latch-rf', 'l1.u-cell'),
        'latch': L('l1', 'g.latch-cell', 'g.latch-write', 'l1.transistors', 'l1.bits', 'l1.u-cell', 'l1.u-library'),
        'sram6t': L('l1', 'g.sram-6t', 'l1.icache-sram', 'l2:l2.storage-question'),
        'energy': L('l1', 'l1.e-vload', 'l1.e-vstore', 'l1.e-scalar', 'l1.e-store-ratio', 'l1.e-fill', 'l1.e-per-bit', 'l1.e-memhier',
                    'l1.e-rails', 'l1.u-energy'),
    },
    'l2': {
        'overview': L('l2', 'l2.sc.what', 'l2.partition.default', 'l2.partition.rows', 'l2.private', 'l2.assoc', 'l2.lat.measured',
                      'l2.lat.spec', 'l2.bw.measured', 'l2.e.level', 'l2.voltage.idle', 'l2.storage-question', 'l2.spec-version',
                      'l2.floorplan'),
        'nbr': L('l2', 'l2.path.miss', 'l2.path.nbr-request', 'l2.path.widths', 'l2.nbr.response'),
        'fifo': L('l2', 'l2.vc-fifo', 'l2.domain', 'l2.rail.hv-logic', 'l3:g.crossing'),
        'reqxbar': L('l2', 'l2.xbar.req'),
        'rspxbar': L('l2', 'l2.xbar.rsp', 'l2.nbr.response'),
        'banks': L('l2', 'l2.banks', 'l2.bank-select', 'l2.decode', 'l2.subbanks'),
        'uc': L('l2', 'l2.banks'),
        'meshstop': L('l2', 'l2.seq.miss-refill.02', 'l2.lat.miss'),
        'partition': L('l2', 'l2.partition.default', 'l2.partition.rows', 'l2.sets', 'scp:scp.m0-rows', 'l3:l3.same-arrays'),
        'rail': L('l2', 'l2.domain', 'l2.rail.sram', 'l2.voltage.idle', 'l2.voltage.limits', 'l2.rail.hv-logic', 'l2.leak',
                  'l2.clock', 'l2.freq'),
        'lvband': L('l2', 'l2.domain', 'l2.voltage.idle', 'l1:l1.voltage'),
        'reqq': L('l2', 'l2.reqq', 'l2.reqq.arb', 'l2.reqq.order'),
        'rbuf': L('l2', 'l2.rbuf', 'l2.rbuf.enabled', 'l2.rbuf.storage'),
        'dataq': L('l2', 'l2.dataq'),
        'cbuf': L('l2', 'l2.cbuf'),
        'atomic': L('l2', 'l2.atomic'),
        'perfmon': L('l2', 'l2.perfmon'),
        'hpf': L('l2', 'l2.hpf'),
        'pipe': L('l2', 'l2.stages', 'l2.stages.budget', 'l2.subbank-busy', 'l2.ramdelay', 'l2.throughput', 'l2.lat.spec'),
        'subbanks': L('l2', 'l2.subbanks', 'l2.sets', 'l2.decode'),
        'rspmux': L('l2', 'l2.seq.load-hit.12', 'l2.xbar.rsp'),
        'tagram': L('l2', 'l2.tag-ram', 'l2.macro.tag', 'l2.macro.vendor'),
        'stateram': L('l2', 'l2.tag-state-ram', 'l2.macro.state', 'l2.macro.vendor'),
        'data': L('l2', 'l2.data-ram', 'l2.macro.data', 'l2.panel-select', 'l2.serial-lookup', 'l2.macro.count', 'l3:g.panel-read-count'),
        'ecc': L('l2', 'l2.ecc', 'l3:g.ecc'),
        'cmp': L('l2', 'l2.serial-lookup', 'l2.tag-ram', 'l3:g.tag-compare'),
        'zero': L('l2', 'l2.zero-state', 'l2.u-zero-partial'),
        'icg': L('l2', 'l2.clock-gating', 'l2.panel-select', 'l3:g.icg'),
        'rowaddr': L('l2', 'l2.decode', 'l2.data-ram', 'l2.partition.rows'),
        'panel': L('l2', 'l2.macro.data', 'l2.macro.vendor', 'l2.macro.count', 'l2.bits', 'l2.spec-version', 'l2.macro.name-decode'),
        'trim': L('l2', 'l2.trim', 'l2.trim.reset', 'l2.voltage.idle', 'l2.voltage.limits', 'l2.rail.sram'),
        'geom': L('l2', 'l2.macro.name-decode', 'scp:scp.g-half-select'),
        'periph': L('l2', 'l3:g.read', 'l3:g.write', 'l3:g.assist', 'l2.panel-select'),
        'band': L('l2', 'l2.partition.rows', 'scp:scp.m0-rows', 'l3:l3.same-arrays'),
        'cell': L('l2', 'l3:g.6t-cell', 'l3:g.read', 'l3:g.write', 'l2.storage-question', 'l2.transistors', 'l2.l1-context'),
        'pre': L('l2', 'l3:g.read', 'scp:scp.g-read'),
        'sa': L('l2', 'l3:g.read', 'l3:g.assist', 'scp:scp.g-read-data'),
        'wd': L('l2', 'l3:g.write', 'l3:g.assist', 'scp:scp.g-write', 'l2.trim.reset'),
        'half': L('l2', 'scp:scp.g-half-select', 'l2.macro.name-decode'),
        'leak': L('l2', 'l3:g.leakage', 'l3:l3.leakage', 'l2.leak', 'l3:g.no-refresh'),
        'ls': L('l2', 'l3:g.crossing', 'scp:scp.g-level-shifter', 'l2.vc-fifo', 'l2.rail.hv-logic'),
        'energy': L('l2', 'l2.e.level', 'l2.e.rails', 'l2.e.scp-contents', 'l2.e.tload-tstore', 'l2.e.l2-minus-scp', 'l2.e.bit',
                    'l2.e.scalar', 'l2.e.gather-line', 'l2.e.shire', 'l2.e.l1fill', 'l2.power-goal', 'l2.leak'),
        'latency': L('l2', 'l2.lat.spec', 'l2.lat.measured', 'l2.lat.overhead', 'l2.lat.ladder', 'l2.lat.miss', 'l2.sleep'),
        'bw': L('l2', 'l2.bw.measured', 'l2.bw.per-bank', 'l2.bw.gather'),
    },
}
PARTS['l3'] = {
    'overview': L('l3', 'l3.what', 'l3.homes', 'l3.same-arrays', 'l3.lat-fit', 'l3.energy', 'l3.energy-contents', 'l3.lat-clock-split', 'l3.bw',
                  'l3.observe', 'l3.process', 'u.latency-split', 'u.bitcell'),
    'shire': L('l3', 'chip:mesh.logical-map', 'l3.homes', 'l3.home-measured', 'l3.lat-fit', 'l3.mean-hops', 'l3.alias'),
    'memshire': L('l3', 'chip:L40', 'chip:L42', 'l3.miss-path', 'l3.dram-leg'),
    'hop': L('l3', 'l3.hop', 'l3.hop-noc-cycles', 'l3.route', 'chip:L104', 'l3.tsend-compare', 'chip:mesh.grid', 'u.noc-hop'),
    'homebox': L('l3', 'l3.homes', 'l3.decode', 'l3.home-measured', 'l3.alias'),
    'fit': L('l3', 'l3.lat-fit', 'l3.lat-by-home', 'l3.lat-clock-split', 'l3.spec-latency', 'l3.lat-reconcile', 'l3.tsend-compare', 'u.latency-split'),
    'mean': L('l3', 'l3.mean-hops', 'l3.lat-by-requester', 'l3.bw', 'l3.bw-tload'),
    'rails': L('l3', 'l3.sram-rail', 'l3.mesh-rail', 'l3.clock', 'l3.hv-region', 'l3.ports', 'u.rail-of-logic'),
    'ports': L('l3', 'l3.ports', 'l3.lane', 'l3.flits'),
    'miss': L('l3', 'l3.miss-path', 'l3.dram-leg', 'l3.spec-latency'),
    'banks': L('l3', 'l3.slice-arith', 'l3.partition-m0', 'l3.same-arrays'),
    'priority': L('l3', 'l3.priority', 'l3.reqq'),
    'slice': L('l3', 'l3.slice-arith', 'l3.partition-m0', 'l3.what'),
    'floor': L('l3', 'u.slice-floorplan'),
    'reqq': L('l3', 'l3.reqq', 'l3.priority'),
    'rbuf': L('l3', 'l3.no-rbuf'),
    'atomic': L('l3', 'l3.atomic', 'l3.atomic-rails', 'l3.flag'),
    'write': L('l3', 'l3.write', 'l3.writearound', 'l3.partial', 'l3.panels', 'l3.zero-state'),
    'sub': L('l3', 'l3.geometry', 'l3.decode', 'l3.same-arrays', 'l3.clock-gating', 'l3.panels'),
    'pipe': L('l3', 'l3.pipeline', 'l3.hit-way-read', 'l3.ram-delay', 'l3.mru-write', 'l3.no-rbuf', 'l3.spec-latency'),
    'tagram': L('l3', 'l3.geometry', 'l3.macros', 'l3.vendor', 'l3.same-arrays'),
    'stateram': L('l3', 'l3.geometry', 'l3.macros', 'l3.mru-write'),
    'data': L('l3', 'l3.macros', 'l3.panels', 'l3.hit-way-read', 'l3.clock-gating', 'u.macro-geometry'),
    'ecc': L('l3', 'l3.ecc-scrub', 'g.ecc', 'l3.geometry'),
    'cmp': L('l3', 'g.tag-compare', 'l3.pipeline'),
    'zero': L('l3', 'l3.zero-state', 'l3.energy-contents', 'l3.energy-rails', 'u.zero-share'),
    'energy': L('l3', 'l3.energy', 'l3.energy-contents', 'l3.energy-rails', 'l3.energy-per-load', 'l3.wire-energy', 'l3.gather', 'l3.leakage',
                'l3.power-goal', 'u.zero-share'),
    'latency': L('l3', 'l3.lat-fit', 'l3.lat-clock-split', 'l3.spec-latency', 'l3.lat-reconcile', 'u.latency-split'),
    'lane': L('l3', 'l3.lane', 'l3.ports', 'l3.flits'),
    'xing': L('l3', 'l3.ports', 'g.crossing', 'l3.hv-region', 'l3.mesh-rail', 'l3.sram-rail', 'l2:l2.vc-fifo'),
    'router': L('l3', 'chip:L105', 'g.router', 'l3.route', 'chip:L104', 'u.noc-hop'),
    'wire': L('l3', 'l3.wire-energy', 'g.wire-energy', 'l3.energy-per-load', 'l3.mesh-rail'),
    'flits': L('l3', 'l3.flits', 'u.noc-hop'),
    'nochop': L('l3', 'u.noc-hop', 'l3.hop-noc-cycles', 'l3.hop'),
    'band': L('l3', 'l3.same-arrays', 'l3.partition-m0', 'scp:scp.m0-rows'),
    'periph': L('l3', 'g.read', 'g.write', 'g.assist'),
    'pre': L('l3', 'g.read', 'scp:scp.g-read'),
    'half': L('l3', 'scp:scp.g-half-select', 'u.macro-geometry'),
    'sa': L('l3', 'g.read', 'g.assist', 'scp:scp.g-read-data'),
    'cell': L('l3', 'g.6t-cell', 'g.read', 'g.write', 'u.bitcell', 'l3.vendor', 'l3.no-refresh', 'g.no-refresh'),
    'wd': L('l3', 'g.write', 'g.assist', 'l3.trim-table'),
    'leak': L('l3', 'g.leakage', 'l3.leakage', 'l3.no-refresh', 'g.no-refresh'),
    'icg': L('l3', 'l3.clock-gating', 'g.icg'),
    'trim': L('l3', 'l3.trim-table', 'l3.trim-reset', 'l3.rail-vs-trim', 'l3.sram-rail', 'u.live-settings'),
    'geom': L('l3', 'u.macro-geometry'),
    'panel': L('l3', 'l3.macros', 'l3.vendor', 'l3.same-arrays', 'l3.geometry', 'u.macro-geometry', 'l1:l1.icache-sram'),
}
PARTS['scp'] = {
    'overview': L('scp', 'scp.what', 'scp.size', 'scp.m0-rows', 'scp.lat-own', 'scp.lat-remote', 'scp.same-as-l2', 'scp.e-own', 'scp.e-catalogue',
                  'scp.e-rails-load', 'scp.e-l1fill', 'scp.e-neigh', 'scp.tl-dest', 'scp.u-cell', 'scp.u-bw'),
    'fmt': L('scp', 'scp.addr', 'scp.addr-row', 'scp.format1'),
    'own': L('scp', 'scp.lat-own', 'scp.lat-split', 'scp.same-as-l2', 'scp.tl-one', 'scp.tl-pipelining', 'scp.bw-own', 'scp.clock-ratio', 'scp.clock'),
    'remote': L('scp', 'scp.lat-remote', 'scp.lat-remote-split', 'scp.lat-leave', 'scp.bw-remote', 'scp.e-remote', 'scp.e-hop', 'scp.e-rails-remote',
                'scp.gather', 'chip:mesh.logical-map', 'scp.u-remote-split'),
    'size': L('scp', 'scp.size', 'scp.m0-rows', 'scp.always-hit', 'scp.no-victims', 'scp.panel-count', 'scp.banks'),
    'relay': L('scp', 'scp.relay', 'scp.relay-mech', 'scp.remote-write'),
    'shire': L('scp', 'chip:mesh.logical-map', 'scp.lat-remote'),
    'hop': L('scp', 'l3:l3.hop', 'scp.e-hop', 'l3:l3.route', 'chip:L104', 'l3:u.noc-hop'),
    'nbrpath': L('scp', 'scp.bw-spec-port', 'scp.hv-region', 'scp.xbar'),
    'tl': L('scp', 'scp.tensorload', 'scp.tl-dest', 'scp.tl-one', 'scp.tl-pipelining', 'scp.coop', 'scp.tl-l2scp'),
    'xbar': L('scp', 'scp.xbar', 'scp.coop'),
    'banks': L('scp', 'scp.banks', 'scp.addr-row'),
    'atomic': L('scp', 'scp.atomic', 'scp.starve'),
    'starve': L('scp', 'scp.starve', 'scp.reqq', 'scp.what'),
    'bneck': L('scp', 'scp.bw-own', 'scp.bw-one-neigh', 'scp.bw-bank-stride', 'scp.bw-spec-port', 'scp.bw-store', 'scp.u-bw'),
    'rail': L('scp', 'scp.rail', 'scp.rail-margin', 'scp.regulator', 'scp.hv-region', 'scp.e-rails-load', 'scp.power-goal', 'scp.vendor-virus', 'scp.leak',
              'scp.u-rail'),
    'reqq': L('scp', 'scp.reqq', 'scp.xbar'),
    'rbuf': L('scp', 'scp.rbuf', 'scp.lat-own'),
    'sub': L('scp', 'scp.always-hit', 'scp.line-read-panels', 'scp.clock-gate', 'scp.m0-rows'),
    'panel': L('scp', 'scp.panel', 'scp.panel-others', 'scp.vendor', 'scp.prm-sram-family', 'scp.line-read-panels', 'scp.u-macro'),
    'pipe': L('scp', 'scp.pipe-stages', 'scp.ram-delay', 'scp.always-hit', 'scp.same-as-l2', 'scp.clock-ratio'),
    'rules': L('scp', 'scp.no-victims', 'scp.write-granule', 'scp.zero-state', 'scp.ecc', 'scp.idx-zero', 'scp.deep-sleep', 'scp.offset0'),
    'trim': L('scp', 'scp.trim-knobs', 'scp.vmin-table', 'scp.trim-reset', 'scp.fw-no-trim', 'scp.rail', 'scp.u-trim'),
    'why': L('scp', 'scp.vmin-table', 'scp.rail-margin', 'l1:l1.voltage', 'l1:l1.why-latch', 'l1:l1.lv-region', 'l1:l1.u-why'),
    'cell': L('scp', 'scp.g-cell', 'scp.g-read', 'scp.g-read-data', 'scp.e-data', 'scp.e-sram-line', 'scp.e-sram-write', 'scp.zero-state', 'scp.u-cell'),
    'band': L('scp', 'scp.m0-rows', 'l3:l3.same-arrays', 'l2:l2.partition.rows'),
    'lane': L('scp', 'l3:l3.lane', 'l3:l3.ports'),
    'periph': L('scp', 'scp.g-read', 'scp.g-write', 'scp.g-assist'),
    'pre': L('scp', 'scp.g-read'),
    'half': L('scp', 'scp.g-half-select', 'scp.u-macro'),
    'sa': L('scp', 'scp.g-read', 'scp.g-read-data', 'scp.g-assist'),
    'wd': L('scp', 'scp.g-write', 'scp.g-assist', 'scp.trim-reset'),
    'leak': L('scp', 'scp.g-static', 'scp.leak'),
    'icg': L('scp', 'scp.clock-gate', 'l3:g.icg'),
    'geom': L('scp', 'scp.u-macro', 'scp.g-half-select'),
    'ports': L('scp', 'l3:l3.ports', 'l3:l3.flits'),
    'xing': L('scp', 'scp.g-level-shifter', 'l3:g.crossing', 'scp.hv-region'),
    'router': L('scp', 'chip:L105', 'l3:g.router', 'l3:u.noc-hop'),
    'wire': L('scp', 'l3:l3.wire-energy', 'l3:g.wire-energy', 'scp.e-hop'),
    'flits': L('scp', 'l3:l3.flits'),
    'nochop': L('scp', 'l3:u.noc-hop', 'l3:l3.hop-noc-cycles'),
}
PARTS['dram'] = {
    'overview': L('dram', 'dram.org.capacity', 'dram.topo.memshires', 'dram.ctl.clock', 'dram.ctl.peak-bw', 'dram.ctl.measured-bw', 'dram.lat.typical',
                  'dram.lat.dram-chip-share', 'dram.e.per-byte', 'dram.e.unmetered', 'dram.e.vs-scp', 'gen.cell', 'dram.org.part'),
    'chipmap': L('dram', 'chip:mesh.logical-map', 'dram.addr.memshire', 'dram.lat.model', 'dram.lat.ms-hops', 'chip:L104'),
    'memshire': L('dram', 'chip:L40', 'chip:L42', 'dram.topo.memshires', 'dram.addr.memshire', 'dram.topo.controllers', 'dram.topo.phy', 'dram.topo.floorplan'),
    'pkg': L('dram', 'dram.topo.packages', 'dram.topo.pkg-pairing', 'dram.org.capacity'),
    'model': L('dram', 'dram.lat.model', 'dram.lat.ms-hops', 'dram.lat.l3-miss', 'dram.lat.clock-scaling', 'dram.lat.typical', 'dram.lat.chase',
               'dram.lat.dram-chip-share', 'dram.lat.rows-closed', 'dram.refill.path'),
    'rate': L('dram', 'dram.ctl.clock', 'dram.ctl.peak-bw', 'dram.ctl.measured-bw', 'dram.ctl.noc-headroom', 'dram.topo.noc-port', 'dram.topo.pll'),
    'energy': L('dram', 'dram.e.per-byte', 'dram.e.data', 'dram.e.unmetered', 'dram.e.split-unknown', 'dram.e.rows', 'dram.e.store-vs-load',
                'dram.e.writeback', 'dram.e.gather', 'dram.e.vs-scp'),
    'addrmap': L('dram', 'dram.addr.memshire', 'dram.addr.channel', 'dram.addr.strip', 'dram.addr.addrmap', 'dram.addr.pa-map', 'dram.addr.interleave',
                 'dram.addr.region'),
    'rails': L('dram', 'dram.pwr.rails', 'dram.pwr.droop', 'dram.u-vdd1'),
    'mspath': L('dram', 'dram.topo.noc-port', 'dram.seq.load.03', 'dram.ctl.clock', 'dram.ctl.registers-sp-only', 'dram.u-ms-clock'),
    'settings': L('dram', 'dram.ctl.power-down', 'dram.ctl.zq', 'dram.ctl.ecc', 'dram.ctl.dfi-update', 'dram.ctl.atomic-unit', 'dram.u-atomic', 'dram.ctl.perfmon'),
    'ctl': L('dram', 'dram.topo.controllers', 'dram.ctl.ports', 'dram.u-ports', 'dram.u-qos', 'dram.ctl.cam', 'dram.u-cam', 'dram.ctl.scheduling',
             'dram.ctl.page-policy', 'dram.ctl.refresh-mode', 'dram.addr.addrmap'),
    'phy': L('dram', 'dram.topo.phy', 'dram.topo.controllers'),
    'part': L('dram', 'dram.org.part', 'dram.org.geometry', 'dram.org.capacity'),
    'lat63': L('dram', 'dram.lat.dram-chip-share', 'dram.lat.ms-internal', 'dram.lat.model'),
    'geom': L('dram', 'dram.org.geometry', 'dram.org.line-vs-page', 'dram.addr.interleave', 'dram.lat.row-life'),
    'cmd': L('dram', 'gen.commands', 'gen.jedec-match'),
    'column': L('dram', 'gen.column', 'dram.ctl.burst'),
    'io': L('dram', 'gen.io', 'dram.ctl.dbi', 'dram.pwr.rails'),
    'timings': L('dram', 'dram.ctl.tRCD', 'dram.ctl.tRP', 'dram.ctl.tRAS-tRC', 'dram.ctl.RL-WL', 'dram.ctl.burst', 'dram.ctl.tRRD-tFAW', 'dram.ctl.tWR',
                 'dram.ctl.refresh-mode', 'dram.ctl.refresh-duty', 'gen.jedec-match', 'dram.lat.row-hit', 'dram.lat.row-conflict',
                 'dram.lat.row-sequential', 'dram.lat.refresh-period'),
    'wordline': L('dram', 'gen.wordline', 'dram.org.die-internals'),
    'mat': L('dram', 'gen.wordline', 'gen.sense', 'dram.org.geometry', 'dram.org.die-internals'),
    'sense': L('dram', 'gen.sense', 'gen.precharge', 'dram.org.geometry'),
    'cell': L('dram', 'gen.cell', 'gen.refresh', 'gen.temp-refresh', 'dram.u-temp', 'dram.org.die-internals'),
    'eq': L('dram', 'gen.equalize', 'gen.precharge'),
    'write': L('dram', 'dram.seq.store.04', 'dram.ctl.tWR', 'dram.store.path'),
}

# ---------------------------------------------------------------- the asks (DESIGN.md §13)
ASKS = [
    {'id': 'ask-not-sram', 'rung': 37, 'status': 'ask_team', 'group': 'AI Foundry ask',
     'title': "Which of the chip's memories are not SRAM, and what cells they use",
     'question': "Which memories the lab lead meant by \"not using SRAM\". The bitcell of the shire-cache macros (6T high-density, "
                 "8T, other), against the spec's \"SRAM memory panels\" (pdf p.48), the compiled 1PUHD/2PUHDRF macros "
                 "(pdf p.51; Synopsys by inference), the datasheet's 140 MB of SRAM (pdf p.4) and core-et-main/AGENTS.md:609. Inside "
                 "dcache_128x32_1r1w_lram: standard-cell latches placed like ET's rf_latch_1r_1w_reg library, or a custom or "
                 "compiled latch array; transistors per bit; a static mux-tree read or a precharged read bitline. The HDBULT08 and "
                 "HDBULT11 cell families and the \"MMI (hand-tuned)\" logic. Whether the L1 is latch RAM because the minion's LV "
                 "region (400-620 mV by the firmware's limits, 0.517 V measured) is below the SRAM panels' 585 mV Vmin (our "
                 "inference), and which other minion arrays (the VPU register file vpu_64x32_3r2w, the TLB) are latch arrays. The "
                 "neighbourhood's instruction-cache data RAM (mbi, saduls0g4l1p512x144, the same 1PUHD family as the data panels) "
                 "has the same open question.",
     'settles': "The transistor views of every on-chip level: the L1's latch cell and read path (now the generic latch template) "
                "and the L2, L3 and scratchpad cell (now a generic 6T marked unknown); whether a shire-cache cell needs refresh "
                "(which would add a refresh step); the \"why latches\" caption confirmed or corrected.",
     'facts': ['l1:l1.u-cell', 'l1:l1.u-why', 'l1:l1.u-library', 'l2:l2.storage-question', 'l3:u.bitcell', 'scp:scp.u-cell'],
     'also': [], 'l3_asks': ['ask-l3-bitcell']},
    {'id': 'ask-memory-macros', 'rung': 38, 'status': 'ask_team', 'group': 'AI Foundry ask',
     'title': 'Datasheets (or .lib summaries) of the memory macros',
     'question': "For saduls0g4l1p4096x144m4b4..., ...1024x116..., saculs0g4l2p1024x40... and dcache_128x32_1r1w_lram: rows x "
                 "columns, column mux and internal banks (is m4b4 a 4:1 mux and 4 banks?), sense-amplifier type, bitline length, "
                 "whether a global read bus is precharged, energy per read and per write at the running voltage, and leakage per "
                 "macro. The same need as the hub's rung 19 (a cell library and netlist), narrowed to the memories.",
     'settles': "The arrays and subarrays of the L1, L2, L3 and scratchpad drawn to scale instead of as illustrations; how many "
                "bitlines swing per access (half-select energy); the ledgers' energy split between array and periphery (now "
                "\"not split\").",
     'facts': ['l2:l2.macro.name-decode', 'l3:u.macro-geometry', 'scp:scp.u-macro', 'l1:l1.u-energy'],
     'also': ['rung19'], 'l3_asks': ['ask-l3-macro']},
    {'id': 'ask-cache-latency', 'rung': 39, 'status': 'ask_team', 'group': 'AI Foundry ask',
     'title': 'Where each cycle of a cache access goes',
     'question': "Stage-by-stage latencies for an L1 hit (is it ID-EX-TAG-MEM-WB plus one cycle, with no S3 to EX bypass, and "
                 "what costs hart 1 three extra cycles on every L1 miss?), an L2 hit (21 shire clocks inside and 26 outside, of "
                 "which only about 6 are placed), a read-buffer hit (10), an L3 hit (the 110-cycle constant: 72.2 clock-scaled "
                 "cycles + 61.4 ns, 109 at 600 MHz, against the spec's 34 + 30 shire clocks), and leaving and entering a shire for a remote scratchpad read (about "
                 "53 cycles), and the L3 home's extra cycles on a miss before the request leaves on To_Sys (the spec's 42 against 30 shire "
                 "clocks).",
     'settles': "Per-step cycle labels on every access of the L1, L2, L3 and scratchpad (now only the totals are measured).",
     'facts': ['l1:l1.u-cycles', 'l3:u.latency-split', 'scp:scp.u-remote-split'],
     'also': ['ask-noc-docs'], 'l3_asks': ['ask-l3-latency']},
    {'id': 'ask-silicon-config', 'rung': 40, 'status': 'ask_team', 'group': 'AI Foundry ask',
     'title': 'Which options of the open drop the silicon has',
     'question': "The open core-et is the Erbium branch, and the spec v1.1 also documents later chips. Does the taped-out L1 "
                 "carry parity or ECC, and can the minion arrays sleep? Is there an L2 hardware prefetcher "
                 "(shire_cache_bank_l2hpf)? What is the read buffer built from (flip-flops in the re-implementation)? Are the v1.1 "
                 "macros the taped-out ones? Does an L3 request pick its mesh lane by the home bank PA[12:11], as core-et-main's "
                 "shirecache_mesh_master.sv:132-153 does?",
     'settles': "Check bits drawn per L1 row or not; the prefetcher box drawn or removed; the read buffer's storage drawn; the "
                "L3 lane (and the correction to the chip tour's fact L103).",
     'facts': ['l1:l1.u-parity', 'l2:l2.hpf', 'l2:l2.rbuf.storage'], 'also': [], 'l3_asks': ['ask-l3-lane']},
    {'id': 'ask-cache-esrs', 'rung': 41, 'status': 'ask_team', 'group': 'AI Foundry ask (or firmware)',
     'title': 'The live shire-cache settings on these cards',
     'question': "sc_pipe_ctl (esr_sc_ram_delay, esr_sc_zero_state_enable, the read-buffer enables) and shire_cache_ram_cfg1-4 "
                 "(RM, RME, RA, WA, WPULSE, BC) on each card, at the 705 mV rail, and esr_sc_axi_qos (the priority the shire cache "
                 "gives its memory requests). The open firmware never writes the trims, and the functional model's reset values "
                 "are the spec's RM0 \"650 mV nominal\" row. One service-processor read of one shire per "
                 "card, or an M-mode read, would do.",
     'settles': "The panel access time drawn (2 cycles = 3.3 ns if 1:1); whether zero lines skip the panels on these cards; "
                "which read-assist and write-assist mode the cell animation shows.",
     'facts': ['l3:u.live-settings', 'scp:scp.u-trim', 'dram:dram.u-qos'], 'also': [], 'l3_asks': ['ask-l3-live-esrs']},
    {'id': 'ask-dram-part', 'rung': 42, 'status': 'ask_team', 'group': 'AI Foundry ask',
     'title': 'The DRAM part',
     'question': "The Micron part number, die density, dies per package, and x16 or byte-mode channels. The firmware reads MR5 "
                 "and MR8 at every boot and logs them (mem_controller_utils.c), but no log has been captured; a boot log or the "
                 "card's BOM line settles it. The part's datasheet gives whatever it publishes of the internal organisation. With "
                 "temperature derating off, also whether the packages stay under 85 C under load: a read of MR4 during a long "
                 "run would show it.",
     'settles': "The DRAM die scale drawn from the actual part instead of from the capacity and JEDEC; the generic die internals "
                "narrowed where the datasheet allows.",
     'facts': ['dram:dram.org.part', 'dram:dram.org.die-internals', 'dram:dram.u-temp'], 'also': [], 'l3_asks': []},
    {'id': 'exp-cache-bottleneck', 'rung': 43, 'status': 'needs_tooling', 'group': 'experiment on the cards',
     'title': 'What caps a shire at 128 B per cycle',
     'question': "Own-scratchpad and L2 streams reach exactly 4.0 B per minion-cycle, half the four banks' 256 B. Sweep the "
                 "tensor-load stride (64 B rotating banks, 256 B one bank rotating sub-banks, 1 KB one bank and one sub-bank) "
                 "and 1 to 4 neighbourhoods per shire, and ask the design team which block is the limit.",
     'settles': "Which block the diagram highlights when all 1,024 minions stream: sub-bank busy time, the response crossbar, "
                "the Fill FIFO, or the 256-bit minion port.",
     'facts': ['scp:scp.u-bw'], 'also': [], 'l3_asks': []},
    {'id': 'exp-zero-state', 'rung': 44, 'status': 'needs_fw_change', 'group': 'experiment on the cards',
     'title': 'How much the zero-line skip saves',
     'question': "Clear esr_sc_zero_state_enable on one card for one L3 run (an M-mode ESR write) and compare zeros against "
                 "random data; compare with the scratchpad, where the skip does not apply and zeros still save about 90 pJ per "
                 "line on the SRAM rail on aifoundry2. Also write a line's quadwords to zero one at a time and time a later read, to see "
                 "whether a partial write sets the zero bit.",
     'settles': "Whether the L3 view shows the data panels idle for zero lines, and where the rest of the data-dependent energy "
                "sits (datapath, ECC, crossings).",
     'facts': ['l3:u.zero-share', 'l2:l2.u-zero-partial'], 'also': [], 'l3_asks': ['ask-l3-zero']},
    # existing rows of the hub's ladder that get a new effect (no new row)
    {'id': 'ask-design-docs', 'extends': ['ask-design-docs'], 'title': 'The Power Spec: which rail feeds the shire-cache logic',
     'question': "Which rail feeds the shire-cache logic (pipeline, crossbars, queues, the high side of the VC FIFOs, the UC "
                 "block) against the macros alone.",
     'settles': "The rail band of each block and the split of SRAM-rail energy between arrays and logic.",
     'facts': ['l2:l2.rail.hv-logic', 'l3:u.rail-of-logic', 'scp:scp.u-rail'], 'also': [], 'l3_asks': ['ask-l3-rails']},
    {'id': 'ask-shire-floorplan', 'extends': ['ask-shire-floorplan'], 'title': "The minion's and the shire's floorplans",
     'question': "Add the minion's partition (where the 8 LRAM macros, tag register files and TLB sit, and their area) and the "
                 "placement of the banks, sub-banks and 96 macros relative to the mesh stop and the L3 slave ports.",
     'settles': "The physical layer of the L1, L2 and L3: the distances an access travels inside the tile.",
     'facts': ['l1:l1.u-floorplan', 'l2:l2.floorplan', 'l3:u.slice-floorplan'], 'also': [], 'l3_asks': ['ask-l3-floorplan']},
    # the dimension order, asked here until 29 September, was measured by E56 (rung 32, exp-route-order; l3.route)
    {'id': 'ask-noc-docs', 'extends': ['ask-noc-docs'], 'title': 'The router pipeline',
     'question': "The router pipeline per hop, which of the 9 main-NoC layers carry L3 requests and replies, and the flit "
                 "width (the dimension order was measured on 29 September: l3.route).",
     'settles': "The mesh-hop scale of the L3 and of the remote scratchpad.",
     'facts': ['l3:u.noc-hop'], 'also': [], 'l3_asks': ['ask-l3-noc']},
    {'id': 'ask-memshire', 'extends': ['ask-memshire'], 'title': "Where a DRAM load's last 63 cycles go, and the memory shire's rules",
     'question': "How the up-to-63 cycles beyond the DRAM's own timing split between the L3 home's miss path and To_Sys "
                 "crossings (about 12 cycles by the spec) and the memory shire's port and clock crossing, the controller's queues "
                 "and the PHY (PA[9], the channel, is the memory shire's reset value, ms_regs.h:160; the row bits, PA[18] and up, "
                 "are measured by one-bit flips on 3 cards; the bank bits PA[12:10] come from the programmed ADDRMAP, rung 33). Also: which traffic goes to each controller's two AXI ports; when a "
                 "global atomic on a DRAM address is done in the memory shire's atomic unit rather than at the L3 home; the "
                 "controller's total CAM depth; and where the memory shire's clock crossing sits.",
     'settles': "The grey bar at the memory-shire scale, split between the L3 home and the memory shire; the controller's "
                "ports, CAM and atomic unit drawn from the design instead of from the init code.",
     'facts': ['dram:dram.lat.ms-internal', 'dram:dram.u-ports', 'dram:dram.u-atomic', 'dram:dram.u-cam', 'dram:dram.u-ms-clock'],
     'also': ['exp-dram-rows', 'ask-cache-latency'], 'l3_asks': []},
    {'id': 'ask-card-schematic', 'extends': ['ask-card-schematic'], 'title': "The card schematic: the package pairing and the DRAM's rails",
     'question': "Already asked by the hub's row: the LPDDR4X package pairing. Also which card rail feeds the packages' VDD1 "
                 "(1.8 V in JEDEC LPDDR4X).",
     'settles': "The dashed pairing on the DRAM chip scale; the DRAM's supplies drawn complete.",
     'facts': ['dram:dram.topo.pkg-pairing', 'dram:dram.u-vdd1'], 'also': [], 'l3_asks': []},
    {'id': 'rung20', 'extends': ['rung20'], 'title': 'Current sensing below the regulators (not possible on silicon)',
     'question': "The DRAM's off-rail 73 pJ/B, split between the memory shire's logic, PHY I/O, DRAM core and DRAM I/O, and "
                 "refresh energy stay unmeasurable on the card.",
     'settles': "The DRAM ledger's grey energy cells; they stay open.",
     'facts': ['dram:dram.e.split-unknown', 'dram:dram.seq.refresh.04'], 'also': [], 'l3_asks': []},
]
LVL_OF = lambda k: k.split(':')[0]
for a in ASKS:
    a['levels'] = sorted({LVL_OF(k) for k in a['facts']}, key=LEVELS.index)
    a['state'] = 'open'
    a['question'] = lab_lead(a['question'])

# the hub rows the asks link to, read from the hub's own data; the proposed new rows are marked
HUBD = json.load(open(os.path.join(REPORTS, 'sources', 'limits-of-observability.data.json')))
RUNGS = {}
for r in HUBD['improvements']:
    rid = r.get('id') or ('rung%d' % r['rung'])
    RUNGS[rid] = {'rung': r['rung'], 'what': r['what'], 'status': r['status'], 'anchor': r.get('id') or 'improve'}
top = max(r['rung'] for r in HUBD['improvements'])
for a in ASKS:
    if 'extends' not in a:
        if a['id'] in RUNGS:
            RUNGS[a['id']]['proposed'] = False
        else:
            RUNGS[a['id']] = {'rung': a['rung'], 'what': a['title'], 'status': a['status'], 'anchor': 'improve', 'proposed': True}
            if a['rung'] <= top:
                raise SystemExit(f'{a["id"]}: proposed rung {a["rung"]} is taken (the hub ends at {top})')
    for k in a.get('extends', []) + a.get('also', []):
        if k not in RUNGS:
            raise SystemExit(f'ask {a["id"]}: no hub row {k}')

# ---------------------------------------------------------------- checks (DESIGN.md §2.2)
# 2. references
for lv, acc in STEPS.items():
    for name, a in acc.items():
        for s in a['steps']:
            for k in s['facts']:
                if k not in FACTS:
                    raise SystemExit(f'{lv}/{name} step {s["n"]}: no fact {k}')
for lv, ps in PARTS.items():
    for p, ks in ps.items():
        for k in ks:
            if k not in FACTS:
                raise SystemExit(f'part {lv}/{p}: no fact {k}')
for a in ASKS:
    if not a['facts']:
        raise SystemExit(f'ask {a["id"]} names no fact')
    for k in a['facts']:
        if k not in FACTS:
            raise SystemExit(f'ask {a["id"]}: no fact {k}')
# 3. every unknown fact belongs to exactly one ask
owner = {}
for a in ASKS:
    for k in a['facts']:
        if FACTS[k]['kind'] != 'unknown':
            raise SystemExit(f'ask {a["id"]}: {k} is not an unknown ({FACTS[k]["kind"]})')
        if k in owner:
            raise SystemExit(f'{k} is in two asks: {owner[k]} and {a["id"]}')
        owner[k] = a['id']
for k, f in FACTS.items():
    if f['kind'] == 'unknown' and k not in owner:
        raise SystemExit(f'unknown fact {k} has no ask')
    if f['kind'] == 'unknown':
        f['ask'] = owner[k]
# 4. generic facts are labelled generic in their text or source
for k, f in FACTS.items():
    if f['kind'] != 'generic':
        continue
    text = ' '.join(str(x or '') for x in (f['statement'], f['source'], f['note']))
    # a step of a generic circuit may cite the generic facts it animates instead (dram.seq.load.06: gen.equalize, ...)
    cites_generic = re.search(r'(^|[\s;(,])(gen|g)\.[a-z]', f['source'] or '')
    if 'GENERIC' not in text and 'textbook' not in text.lower() and not cites_generic:
        raise SystemExit(f'generic fact {k} is not labelled GENERIC or textbook')
# 4b. no local path reaches the page: sources are repository-relative (external/... is the prototyping checkout's)
for k, f in FACTS.items():
    for fld in ('statement', 'source', 'note', 'kind_note'):
        if re.search(r'/home/|/tmp/', str(f.get(fld) or '')):
            raise SystemExit(f'{k}.{fld} has a local path: {f[fld]}')
for a in ASKS:
    for fld in ('question', 'settles', 'title'):
        if re.search(r'/home/|/tmp/', a[fld]):
            raise SystemExit(f'ask {a["id"]}.{fld} has a local path')
# 5. one canonical value per quantity: the L1 fill from the scratchpad is l1.e-fill (238 pJ, three cards); the
#    two-card 205 pJ (l2.e.l1fill) appears only in the facts table and its panel, never as a printed number
CANON = {'l2:l2.e.l1fill': 'l1:l1.e-fill'}
for key, x in num.items():
    if x['f'] in CANON:
        raise SystemExit(f'{key} prints {x["f"]}; the canonical fact is {CANON[x["f"]]}')

# ---------------------------------------------------------------- what the page keeps from the chip tour
chip = json.load(open(os.path.join(REPORTS, 'data', '2026-09-27-chip-diagram', 'facts.json')))
layout = chip.get('layout')

P40 = 2 ** 32
addr = {
    'line': 0x80 * P40 + 0x2468A * 2048 + 13 * 64,   # the chip tour's mkPA(13, 0x2468A): a DRAM-region line homed in shire 13
    'offset': 8,                                     # the L1's example load reads 8 bytes at byte 8 of the line
    'way_l1': 2, 'way_l2': 2,                        # the ways the line sits in (an example: no address bit picks a way)
    'note': 'The line is the chip tour\'s example (mkPA(13, 0x2468A)); the ways are an example.',
}

CONFLICTS = [
    {'what': 'Is the storage SRAM?', 'levels': ['l1', 'l2', 'l3', 'scp'],
     'sources': ["Shire Cache Specification pdf pp.48, 51; datasheet p.4; PRM p.346: SRAM for the shire cache",
                 "the lab lead: \"not using SRAM\" (relayed by the page's author; not recorded in the repository)"],
     'resolution': 'The documents are shown as documented and the bitcell as unknown, with the contradiction stated; the L1 is '
                   'documented as latch RAM (ask-not-sram).'},
    {'what': "The SRAM rail's voltage", 'levels': ['l2', 'l3', 'scp'],
     'sources': ["750 mV in the card's power-tree figure and the firmware's boot default (l2.rail.sram)",
                 '705 mV regulator set point in every measurement, 703-707 mV read on the die (l2.rail.sram, l2.voltage.idle)'],
     'resolution': 'The page prints the 705 mV set point (703-707 mV on the die), and 750 mV only as the power-tree figure and '
                   'boot default.'},
    {'what': 'Filling a 64 B line into the L1 from the scratchpad', 'levels': ['l1', 'l2'],
     'sources': ['238 pJ random, 101 zeros, three cards (l1.e-fill)', '205 / 101 with two cards pooled (l2.e.l1fill)'],
     'resolution': 'Canonical 238 pJ; 205 only in the facts table, as the earlier figure.'},
    {'what': 'Row order in the data panels', 'levels': ['l2', 'l3', 'scp'],
     'sources': ['l2.data-ram and its steps write "{way, set}"',
                 're-implementation RTL shirecache_pipe_sub_bank.sv:1613: data RAM address = {set, way} (l3.same-arrays, scp.m0-rows)'],
     'resolution': 'Drawn set-major, as the RTL line has it: the L2 is rows 2,560-3,071 of each panel (sets 640-767 times 4 ways).'},
    {'what': 'Which mesh lane an L3 request takes', 'levels': ['l2', 'l3'],
     'sources': ['the chip tour (fact L103) and the wire-energy synthesis: PA[7:6]',
                 'l3.lane: the home bank PA[12:11]; PA[7:6] only for a remote scratchpad (re-implementation RTL)'],
     'resolution': 'The L3 draws PA[12:11], marked re-implementation RTL, to confirm in silicon (ask-silicon-config); the '
                   'chip tour\'s fact L103 cites the same RTL file, whose lines 145-149 take PA[7:6] only for a remote '
                   'scratchpad, and needs the correction.'},
    {'what': 'The scratchpad address format', 'levels': ['scp'],
     'sources': ["Shire Cache Specification v1.1 p.24: the shire field is [30:23], all ones meaning the local shire",
                 "PRM pdf p.486: bit 30 picks the format; format 0 puts the shire ID in [29:23], 0x7F meaning the local shire; "
                 "agents other than minions use the hardware format with bit 30 a copy of bit 29"],
     'resolution': "The strip and the format bar draw the PRM's format 0, the one a minion issues (scp.addr)."},
    {'what': "Which L1 sets the issuing hart uses", 'levels': ['l1'],
     'sources': ["Minion DCache Description §3.2.1: the two set MSBs are forced to 11, so only sets 12-15 are used",
                 "PRM pdf p.246 Table 8.4: hart 0 has sets 12-13, hart 1 sets 14-15; the measured knee is 512 B per hart (l1.knee)"],
     'resolution': "The set is decoded as 12 + 2 x hart + PA[6], for the example's hart 0: the hart, not PA[7], picks the pair."},
    {'what': "The DRAM controllers and PHYs", 'levels': ['dram'],
     'sources': ["the datasheet: 'two 16-bit PHYs sharing a single 32-bit controller' per memory shire",
                 "the firmware and the PRM: two uMCTL2 controllers (u0, u1) and one PHY per memory shire (dram.topo.controllers, "
                 "dram.topo.phy)"],
     'resolution': "Drawn as the firmware programs it: two controllers, one PHY with two 16-bit channels."},
    {'what': "ECC bits of a tag", 'levels': ['l2', 'l3'],
     'sources': ["Shire Cache Specification p.9: 7 ECC bits per 33-bit tag", "p.47 and the macro widths: 23 tag bits + 6 ECC bits per "
                 "way, 4 x 29 = 116 bits (l2.tag-ram, l3.geometry)"],
     'resolution': "Drawn with the macro widths: 23 + 6 bits per way."},
    {'what': "Shire cache in the I/O shire", 'levels': ['l2'],
     'sources': ["the datasheet and the PRM: 35 shires x 4 MB (140 MB)", "Shire Cache Specification p.22: 1 MB for the I/O shire"],
     'resolution': "The page quotes the datasheet's 140 MB only as that document's count (l2.sc.chip-total) and otherwise "
                   "counts the 32 compute shires' 128 MB; the I/O shire is not drawn."},
    {'what': 'Open RTL against silicon', 'levels': LEVELS,
     'sources': ['external/core-et is the Erbium branch; the Shire Cache Specification v1.1 also documents later chips',
                 "external/core-et-main is Ainekko's re-implementation"],
     'resolution': 'Facts from the re-implementation carry "re-implementation RTL", facts from the specification "spec v1.1".'},
]

counts = {}
for f in FACTS.values():
    counts.setdefault(f['level'], {}).setdefault(f['kind'], 0)
    counts[f['level']][f['kind']] += 1
out = {
    'meta': {'built_from': ['research/facts-%s.json' % lv for lv in LEVELS]
                           + ['../../sources/limits-of-observability.data.json (the hub rows the asks link to)',
                              '../2026-09-27-chip-diagram/facts.json (.layout, read only)'],
             'counts': counts, 'n_facts': len(FACTS), 'n_num': len(num), 'chip_tour': CHIP_TOUR,
             'levels': LEVEL_NAME,
             'caveats': ['core-et in external/ is the Erbium branch; external/core-et-main is Ainekko\'s re-implementation of '
                         'the CORE-ET RTL, co-simulated against the original shire cache.',
                         'The Shire Cache Specification is v1.1 and also describes later chips (Nemi, Gepardo).']},
    'facts': FACTS, 'steps': STEPS, 'num': num, 'parts': PARTS, 'asks': ASKS, 'rungs': RUNGS,
    'layout': layout, 'addr': addr, 'conflicts': CONFLICTS,
}
# ---- the shared ladder (1 Oct 2026, part 2: the memory levels host the chip diagram's path camera,
# sources/memory-levels.ladder.js): the scales from the observable universe to the Planck length, the maps' outlines,
# the images' manifest, the numbers the outer scenes print, the ring of sizes and the lazily fetched facts, as the
# chip diagram's build wrote them (its facts.json; read after it is built); and the chip's own facts those scales cite
# by id (the rest of the ladder's facts are fetched from ladder-img/ladder-data.json, shared by both pages)
LAD = {k: CHIP[k] for k in ('scales', 'geo', 'img', 'onum', 'outside', 'ring', 'lazy') if k in CHIP}
cited = set()
for sc in LAD.get('scales', {}).values():
    if sc.get('f'):
        cited.add(sc['f'])
    cited.update(sc.get('facts') or [])
LAD['facts'] = {i: CHIP['facts'][i] for i in sorted(cited) if i in CHIP['facts']}
LAD['num'] = {}
out['ladder'] = LAD
out['meta']['built_from'].append('../2026-09-27-chip-diagram/facts.json (.scales, .geo, .img, .onum, .outside, .ring, .lazy and the facts '
                                 'they cite: the shared ladder)')
p = os.path.join(HERE, 'facts.json')
json.dump(out, open(p, 'w'), indent=None, separators=(',', ':'), ensure_ascii=False)
print('wrote', p, os.path.getsize(p), 'bytes;', len(FACTS), 'facts', {lv: counts[lv] for lv in LEVELS}, len(num), 'numbers,',
      sum(len(a['steps']) for acc in STEPS.values() for a in acc.values()), 'steps,', len(ASKS), 'asks')
