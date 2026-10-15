export const meta = {
  name: 'chip-diagram-check',
  description: 'In-depth correctness check of the ET-SoC-1 chip diagram: 11 slice checkers, each followed by an adversarial verifier',
  phases: [
    { title: 'Find', detail: 'one checker per slice of the page: facts, panels, drawing, flows, prose' },
    { title: 'Verify', detail: 'one skeptic per slice re-checks every finding and its fix' },
  ],
}

const W = '/home/yaroslavvb/claude/work/chip-check-1014'
const PRE = `Read the brief first, in full: ${W}/brief.md. It says what the page is, where its text comes from, what the ground truth is, what counts as a finding and the rules (read-only; never touch the cards; the Bash rules). Today is Wed 14 Oct 2026.`

const SLICES = [
  { name: 's01-die-mesh', title: 'the die, the mesh and the floorplan',
    focus: `The die scale and its drawing: the 8 x 6 grid (32 compute shires, master shire 32, spare 33, the PCIe and I/O shires, 8 memory shires, 4 cells without a compute shire), which shire is drawn in which cell (layout.mesh and layout.mesh_die in facts.json against the firmware's "default Shire Virtual ID Map" in external/et-platform and the measured logical map), the mesh (dimension-order routing, 12-cycle hops, the 3.72 mm hop pitch, 512-bit ports, routers per stop, the 0.485 V rail), the chip-level counts (1,093 cores = 1,088 minions + 4 ET-Maxions + the service processor; 34 minion shires; 2,176 harts), die area 570 mm2, die dimensions, TSMC 7 nm, transistor count, package (45 x 45 mm, balls, bumps), sensor placement, shire ID numbering (ESR IDs), the PCIe and I/O shire contents, and the public chip facts with ids et.* (process, transistors, masks, SRAM bytes, cores). Scales: die, mesh, pcie, io, die.metal, mesh.link.wire, package. Check the die screenshot (scale-*-die.png) cell by cell.` },
  { name: 's02-shire', title: 'the compute shire',
    focus: `A compute shire: 4 neighbourhoods of 8 minions; the 4 MB shire cache in 4 banks x 4 sub-banks; the M0 partition (2.5 MB scratchpad, 512 KB L2, 1 MB L3 slice) and the other modes; the L2 and L3 behaviour (private L2, L3 home by address, write-around, read buffer, latencies from the Shire Cache Specification); the scratchpad formats and offset 0; the crossbar, the UC block (FCC, FLB), the mesh stop and its routers and clock crossing; the neighbourhood (instruction cache, L0, PMU, page-table walker, cooperative TensorLoad, the fast local network's edges and latency); voltage domains, clocks; and the sizes and insides of the shire's blocks in the deep zoom (size.shire.*, in.shire.*, size.etlink, size.fln). Scales: shire, shire.meshstop, shire.meshstop.router, shire.meshstop.xing, shire.bank, shire.subbank, shire.panel, shire.uc, shire.xbar, shire.neigh. Check the shire screenshot: the number of neighbourhoods, minions, banks, what connects to what.` },
  { name: 's03-minion', title: 'the minion and its units',
    focus: `A minion: 2 harts (hart 0 issues tensor instructions; what hart 1 may do), the in-order integer core, the vector unit (8 lanes of fp32, 256-bit vectors, the register file, the pipeline, the peak vector rate), the tensor unit (TensorFMA shapes and rates, TensorLoad, TensorSend, TENB/TENC, the tensor CSRs, the "546" fact, the one ready bit), the L1 data cache (size, modes, port, scratchpad L1), the ET-Link width, no divide, sleep/awake power, ISA (RV64 and its extensions), the matmul peak and ridge levels; and the deep zoom of the minion's blocks (size.minion*, size.core*, size.vpu*, size.tensor*, size.l1d*, size.l1scp, in.minion/core/vpu/tensor/l1d.*). Scales: minion, core, tensor, vpu, vpu.lane, vpu.lane.fma, vpu.lane.fma.tree, fma.tree.col, l1d, l1d.cmp, l1d.block, l1d.row. The VPU and Minion Description documents and the PRM are your main sources.` },
  { name: 's04-memory', title: 'DRAM, the memory shires, the address map and the latency ladder',
    focus: `The DRAM (LPDDR4X: 16 channels of 16 bits, 4 packages, 32 GB, 3,733 MT/s on the cards against the datasheet's rate, 119 GB/s peak, 76 GB/s measured; the driver now reports ddr_mb_s 128000 for this card), the memory shires (two channels each, 512-bit NoC port, the controller policy, counters), the address map (PA bits selecting the memory shire, the controller, banks and rows; the L3 home), the whole-load latency model (110 + 12 per hop + 91 + 12 per hop) and its split, the latency and bandwidth of L1, L2, L3, scratchpad and DRAM, row conflicts and refresh, the gathers and scatters (gs-*), the global atomic. Flows 1 (Load to DRAM), 2 (Latency ladder), 5 (Gathers): every stage's caption, panel and chart numbers. Scales: memshire, memshire.phy, memshire.phy.dq, dram, dram.bank, dram.cell. Compare every number with the data file it cites (docs/reports/data/...) and the claims ledger.` },
  { name: 's05-messaging', title: 'messages between minions and shires',
    focus: `TensorSend (round trips inside a neighbourhood, a shire and across the mesh, the 150 + 12.02 per hop fit, credits, energy per pair), the fast local network, the relay against DRAM (bandwidth, pJ per byte, watts, the 13x), the hot line (a contended atomic: fair, the cliff at 22 requesters, its cost and energy), synchronisation (shire and chip barriers, the FCC and FLB, flag memory, the reduction tree's levels, allreduce 32 and 1024 minions), the broadcast facts (bc.*: TensorBroadcast, the 1 KB allreduce, ESR broadcast and IPI, the launch's multicast), the mesh's 1 KB knee and energy per bit per mm (mesh-bit-mm-*), and L70, L71, L86-L88, L91-L94. Flows 3 (TensorSend), 4 (Relay), 9 (Hot line), 0 (Allreduce), B (Broadcast): every stage's caption, panel and chart numbers against the data files they cite.` },
  { name: 's06-host-power', title: 'the host link, clocks, voltages, power and energy',
    focus: `The PCIe link (Gen4 x8, 16.0 GT/s on every card, DMA and staged bandwidth, small copies, polling, kernel launch time, where a host write lands, concurrent DMA), the board (regulators, meters), the clocks (600 MHz on the cards, the operating points, DVFS limits, design clocks), the rails (minion 0.517 V, SRAM, others; per-shire voltages L123), idle power and its rails, temperature sensors, heat (leakage, the race, fewer shires), the energy per instruction, per byte and per level (e-* facts), the matmul (9.51 TFLOP/s, 50-69 W at the board, GFLOP/s per watt, by data: zeros, ones, random). Flows 6 (Host / PCIe), 7 (Matmul), 8 (Data to watts): every stage's caption, panel and chart numbers. Scales: pcie.phy, pcie.lane, lib.buck, lib.powerfet, lib.strap, lib.pll. Check every number against docs/reports/data/2026-09-27-pcie/, 2026-09-29-pcie2/, the energy manual's manual.json, the Horace runs and the claims ledger.` },
  { name: 's07-memlevels', title: 'the memory system in the deep zoom (the memory levels drawings)',
    focus: `The 226 facts with ids ml:* (shared with the memory levels page): the L1 data cache down to an LRAM block, a row and its latches; the shire cache to a bank, a sub-bank, an SRAM panel and a 6T cell; the L3 and the scratchpad; the DRAM to a bank and its 1T1C cell (charge, refresh every 32 ms, cell sizes); generic circuits (sense amplifier, decoder, latch). Scales: lib.sram6t, lib.dramcell, lib.senseamp, lib.decoder, lib.latch, and the memory scales the other slices also look at where these facts appear. Pay special attention to electron counts, cell capacitances, voltages, refresh intervals, array sizes and the arithmetic that ties them to the chip's 4 MB per shire and 32 GB of DRAM.` },
  { name: 's08-circuits', title: 'the textbook circuits inside the blocks',
    focus: `The constructions labelled "textbook construction" and their facts (tb.*, st.*, in.lib.*, size.lib.*, size.fma.*): the fused multiply-add's datapath (radix-4 Booth encoding and its table, the compressor tree of 17 partial products, a 4:2 compressor, the full adder, the Kogge-Stone prefix adder, aligner and normaliser shifters, leading-zero counting and anticipation, rounding with guard, round and sticky), register files, decoders, FIFOs, counters, comparators, crossbars and arbiters, ECC, ROM, PLL, a differential amplifier, a clock gate, flip-flops and latches, and each gate drawn as transistors (NAND, NOR, AOI21, XOR, inverter, mux). Check that each drawing and statement is right as engineering (correct truth tables, transistor counts and topologies, the partial-product count for a 24-bit fp32 significand under radix-4 Booth, the compressor levels, the prefix tree depth), and that the sizes given are plausible for N7 cells. Scales: lib.xor, lib.inverter, lib.fa, lib.nand2, lib.cmp42, lib.booth, lib.mux2, lib.shifter, lib.adder, lib.lzd, lib.round, lib.icg, lib.aoi21, lib.nor2, lib.regfile, lib.rom, lib.flipflop, lib.logic, lib.counter, lib.cmpeq, lib.fifo, lib.xbar, lib.ecc, lib.diffamp. Look at their screenshots.` },
  { name: 's09-device-physics', title: 'the transistor, the silicon and the particles',
    focus: `The device and below (el.*, n7.*, si.*, dope.*, gate.*, wire.*, cu.*, p.*, size.p.*, in.lib.fin/finfet/si/gate/wire.*): TSMC N7's published numbers (contacted gate pitch 57 nm, fin pitch 30 nm, cell height 240 nm, fin 6 x 52 nm, gate length 16.5 nm), the gate stack, the channel's atom count (257,000), dopants, electrons in an on and off channel (85-120, 0.002), leakage of 10 billion electrons a second, SRAM node and DRAM cell electrons, the band gap, kT, the silicon lattice and density, the atom's 14 electrons, nucleus, proton and quarks, the Planck length, copper's lattice and resistivity, and the "How many electrons?" table in static.json. Recompute every derived number (atom counts from volume x density, electrons from C x V / q, leakage from the chip's measured leakage power at 80 C over its transistors). Scales: lib.finfet, lib.fin, lib.channel, lib.si, lib.wire, p.cu, p.atom, p.nucleus, p.nucleon, p.quark, p.electron, p.dopant, p.planck, p.wrap.` },
  { name: 's10-outside', title: 'outside the chip: package, card, host, rack, and the powers of ten',
    focus: `The levels outside the die (out.*, s45.*, card.*, host.*, pcie.gen4.*, b.*, e.*, ring.*, cmp.*, buck.*, size.<outside levels>, size.lib.buck/powerfet/strap): the package, the PCIe card (its regulators, boot switches, form factor, from ET-PCIe-Dev-Card-V3.pdf and the lab's records), the host (an ATX board drawn to scale; Intel 14 nm, DDR4), the rack, Studio 45 and its city, then the Earth, the Moon, the solar system, stars, the Milky Way, the Local Group, Laniakea, the observable universe, and the cosmic epochs (e.*); light-travel times counted in ticks of the 600 MHz clock, and fibre's group index. Check every size, distance, time and tick count (recompute them), and that nothing private is shown (no street address or host names). Scales: beyond, universe, laniakea, localgroup, milkyway, stars, solar, moon, earth, us, california, bayarea, sf, bernal, st29, studio45, rack, host, card. Look at the screenshots.` },
  { name: 's11-prose', title: 'the page\'s prose, the tour, the asks and the page-wide consistency',
    focus: `Everything a reader reads outside the parts' panels: ${W}/crawl/out/static.json (bodytext: "How to use it", "Turn the chip's smallest structures in 3D", "From the rack to the quarks", "How many electrons?", "Versions", "Related reports"; summary: "What the diagram shows"; honest: "What is measured, what is specified, what is inferred"; the asks table) and ${W}/crawl/out/tour.json (the 17 tour slides; slide 17 is the summary), with the source in docs/reports/sources/chip-diagram.body.html and the text builders in chip-diagram.script.js. Check every number and claim there against facts.json and the ground truth; the counts the page states about itself (facts by kind, eleven flows, seventeen slides, which flows the tour leaves out) against what the page does; the dates in "Versions" against git log and the space's history (spacesheep versions: 27 Sep first publish ... 14 Oct); the one-line descriptions of the related reports against those reports' own data in the repository; and consistency across the page: the same quantity must not be given two values (e.g. compare the summary, the tour, the panels, the flows and the facts for core counts, clocks, bandwidths, latencies, watts, die size). Your slice file has no facts; use facts.json and the crawl.` },
]

const FIND = {
  type: 'object',
  properties: {
    slice: { type: 'string' },
    checked: { type: 'object', properties: { facts: { type: 'integer' }, panels: { type: 'integer' }, flow_stages: { type: 'integer' }, screenshots: { type: 'integer' } }, required: ['facts', 'panels', 'flow_stages', 'screenshots'] },
    not_checked: { type: 'array', items: { type: 'string' } },
    findings: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' },
      severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
      category: { type: 'string', enum: ['wrong-value', 'wrong-statement', 'misattributed-source', 'wrong-kind', 'arithmetic', 'inconsistency', 'drawing', 'stale', 'physics', 'other'] },
      where: { type: 'string' },
      page_says: { type: 'string' },
      truth: { type: 'string' },
      evidence: { type: 'array', items: { type: 'object', properties: { path: { type: 'string' }, locator: { type: 'string' }, quote: { type: 'string' } }, required: ['path', 'locator', 'quote'] } },
      source_location: { type: 'string' },
      fix: { type: 'string' },
      confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
      card_check: { type: 'string' },
    }, required: ['key', 'severity', 'category', 'where', 'page_says', 'truth', 'evidence', 'source_location', 'fix', 'confidence'] } },
    notes: { type: 'string' },
  },
  required: ['slice', 'checked', 'not_checked', 'findings', 'notes'],
}

const VERIFY = {
  type: 'object',
  properties: {
    slice: { type: 'string' },
    verdicts: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' },
      verdict: { type: 'string', enum: ['confirmed', 'refuted', 'partly'] },
      severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
      reason: { type: 'string' },
      evidence: { type: 'array', items: { type: 'object', properties: { path: { type: 'string' }, locator: { type: 'string' }, quote: { type: 'string' } }, required: ['path', 'locator', 'quote'] } },
      fix: { type: 'string' },
      fix_files: { type: 'array', items: { type: 'string' } },
      card_check: { type: 'string' },
    }, required: ['key', 'verdict', 'severity', 'reason', 'evidence', 'fix', 'fix_files'] } },
    missed: { type: 'array', items: { type: 'string' } },
  },
  required: ['slice', 'verdicts', 'missed'],
}

const findPrompt = s => `${PRE}

You are the checker for slice ${s.name}: ${s.title}.
Your slice file: ${W}/slices/${s.name}.json (its facts with their full records, the crawled panels of its scales, its flows).
Your scratch folder: ${W}/findings/${s.name}/ (create it; keep a notes.md of what you checked and how, as you go).

What to cover:
${s.focus}

Work through every fact in your slice and every panel, caption and drawing of your scales and flows. For each fact, open the source it cites and confirm it says what the fact says; then test the statement against the most authoritative ground truth you can reach (brief, "Ground truth"). Recompute every derived number. Look at the screenshots of your scales and flows. Grep the page sources to find where each wrong text is generated.

Return the structured result: what you checked (counts), what you could not check, and the findings, each with exact quotes, evidence with paths and line numbers or PDF pages, the generating source location and an exact fix. Only real errors, proven; no style notes.`

const verifyPrompt = (s, r) => `${PRE}

You are the skeptic for slice ${s.name} (${s.title}). A checker reported the findings below. Your job is to try to REFUTE each one, independently: re-open the page's text (the crawl in ${W}/crawl/out/, the slice file ${W}/slices/${s.name}.json, the sources in the repo) and the ground truth yourself; do not trust the checker's quotes until you have seen them. A finding survives only if the page really says what it is said to say, the ground truth really says otherwise, and the ground truth outranks or postdates what the page relied on.

For each finding return a verdict: confirmed (as reported), partly (real but the claim, severity or fix needs correcting: give the corrected fix), or refuted (with the reason). Check the fix itself: is the new text right and complete, does it go in the file that actually generates the text (facts.json is generated: fixes go in research/*.json, build_facts.py's dicts, deepzoom.py, inside.json/outside.json, the ladder's research json, or the page sources), and would it break another number that depends on it (the N table in build_facts.py checks displayed numbers against their sources; the memory levels page shares facts.json's ml facts, circuitkit.js and the ladder)? List in fix_files every file the fix must touch. Default to refuted when you cannot reproduce the evidence.

If, while checking, you see a clear error in this slice that the checker missed, add a one-line description to "missed" (with the evidence path and line).

The checker's result (JSON):
${JSON.stringify(r)}`

phase('Find')
const results = await pipeline(
  SLICES,
  s => agent(findPrompt(s), { label: `find:${s.name}`, phase: 'Find', schema: FIND }),
  (r, s) => {
    if (!r) return { slice: s.name, find: null, verify: null }
    if (!r.findings || r.findings.length === 0) return { slice: s.name, find: r, verify: { slice: s.name, verdicts: [], missed: [] } }
    return agent(verifyPrompt(s, r), { label: `verify:${s.name}`, phase: 'Verify', schema: VERIFY })
      .then(v => ({ slice: s.name, find: r, verify: v }))
  },
)
const out = results.filter(Boolean)
let nf = 0, nc = 0
for (const x of out) {
  nf += x.find ? x.find.findings.length : 0
  nc += x.verify ? x.verify.verdicts.filter(v => v.verdict !== 'refuted').length : 0
}
log(`findings ${nf}, surviving verification ${nc}`)
return out
