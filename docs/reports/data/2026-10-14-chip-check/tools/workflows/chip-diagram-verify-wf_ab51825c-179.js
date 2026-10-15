export const meta = {
  name: 'chip-diagram-verify',
  description: 'Finish the chip diagram check: the two missing slice checkers, then an adversarial verifier for every slice',
  phases: [
    { title: 'Find', detail: 'the die-and-mesh and the prose checkers (the other nine slices are done)' },
    { title: 'Verify', detail: 'one skeptic per slice re-checks every finding and its fix' },
  ],
}

const W = '/home/yaroslavvb/claude/work/chip-check-1014'
const PRE = `Read the brief first, in full: ${W}/brief.md. It says what the page is, where its text comes from, what the ground truth is, what counts as a finding and the rules (read-only; never touch the cards; the Bash rules). Today is Wed 14 Oct 2026.`
const DONE = ['s02-shire', 's03-minion', 's04-memory', 's05-messaging', 's06-host-power', 's07-memlevels', 's08-circuits', 's09-device-physics', 's10-outside']

const SLICES = [
  { name: 's01-die-mesh', title: 'the die, the mesh and the floorplan',
    focus: `The die scale and its drawing: the 8 x 6 grid (32 compute shires, master shire 32, spare 33, the PCIe and I/O shires, 8 memory shires, 4 cells without a compute shire), which shire is drawn in which cell (layout.mesh and layout.mesh_die in facts.json against the firmware's "default Shire Virtual ID Map" in external/et-platform and the measured logical map), the mesh (dimension-order routing, 12-cycle hops, the 3.72 mm hop pitch, 512-bit ports, routers per stop, the 0.485 V rail), the chip-level counts (1,093 cores = 1,088 minions + 4 ET-Maxions + the service processor; 34 minion shires; 2,176 harts), die area 570 mm2, die dimensions, TSMC 7 nm, transistor count, package (45 x 45 mm, balls, bumps), sensor placement, shire ID numbering (ESR IDs), the PCIe and I/O shire contents, and the public chip facts with ids et.* (process, transistors, masks, SRAM bytes, cores). Scales: die, mesh, pcie, io, die.metal, mesh.link.wire, package. Check the die screenshot (scale-*-die.png) cell by cell. Known from other slices (do not re-report, but use): many facts cite docs/findings/05-claims.md and docs/et-soc1-notes.md by line numbers that were right on 26-30 Sep and have drifted since; the lane rule in L103 is reported by another slice.` },
  { name: 's02-shire', title: 'the compute shire' },
  { name: 's03-minion', title: 'the minion and its units' },
  { name: 's04-memory', title: 'DRAM, the memory shires, the address map and the latency ladder' },
  { name: 's05-messaging', title: 'messages between minions and shires' },
  { name: 's06-host-power', title: 'the host link, clocks, voltages, power and energy' },
  { name: 's07-memlevels', title: 'the memory system in the deep zoom (the memory levels drawings)' },
  { name: 's08-circuits', title: 'the textbook circuits inside the blocks' },
  { name: 's09-device-physics', title: 'the transistor, the silicon and the particles' },
  { name: 's10-outside', title: 'outside the chip: package, card, host, rack, and the powers of ten' },
  { name: 's11-prose', title: 'the page\'s prose, the tour, the asks and the page-wide consistency',
    focus: `Everything a reader reads outside the parts' panels: ${W}/crawl/out/static.json (bodytext: "How to use it", "Turn the chip's smallest structures in 3D", "From the rack to the quarks", "How many electrons?", "Versions", "Related reports"; summary: "What the diagram shows"; honest: "What is measured, what is specified, what is inferred"; the asks table) and ${W}/crawl/out/tour.json (the 17 tour slides; slide 17 is the summary), with the source in docs/reports/sources/chip-diagram.body.html and the text builders in chip-diagram.script.js. Check every number and claim there against facts.json and the ground truth; the counts the page states about itself (facts by kind, eleven flows, seventeen slides, which flows the tour leaves out) against what the page does; the dates in "Versions" against git log and the space's history (first publish 27 Sep; versions on 28, 29, 30 Sep, 1-2 Oct, 14 Oct); the one-line descriptions of the related reports against those reports' own data in the repository; and consistency across the page: the same quantity must not be given two values (compare the summary, the tour, the panels, the flows and the facts for core counts, clocks, bandwidths, latencies, watts, die size). Your slice file has no facts; use facts.json and the crawl. Known from other slices (do not re-report): the memory-shire fit is per line not per load (L45, ms-fit-3cards, tour slide 4, the honest text); the DRAM chip's share is about 28 cycles, not 25-28; gathers and scatters (E48) are published; the routing order was measured on three cards; the electrons table's rows 2 and 8 are mislabelled; the relay's energy is per byte moved.` },
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

const HOWBUILT = `How the page is built (for judging where a fix must go): the whole chain is reproducible and at a fixed point at bd8e731a (checked today: rebuilding every step reproduces the committed pages byte for byte), in this order: the ladder's research/build_process.py, build_particles.py, build_studio45.py, build_circuits.py, then build_ladder.py (docs/reports/data/2026-10-01-ladder); the memory levels' research/build_facts_{l1,l2,l3,dram,scp}.py (docs/reports/data/2026-09-28-memory-levels; build_facts_l1.py writes its output one folder up, identical to research/facts-l1.json); the chip's research/build_layout_facts.py, build_facts_v2.py, make_asks.py; then twice: research/build_inside.py, research/build_outside.py, the chip's build_facts.py, the memory levels' build_facts.py; then scripts/build-report.py for both pages. research/build_facts_arch.py and research/build_facts_numbers.py are records only (their OUT is an old scratchpad): fixes to those facts go in research/facts-arch.json and research/facts-numbers.json directly (and the record .py kept in step). docs/reports/sources/circuitkit.js is generated from the memory levels page's kit by research/make_circuitkit.py (--check fails if they differ): a fix to it goes in docs/reports/sources/memory-levels.script.js and is copied. Facts with ids ml:* come from the memory levels' research files and are shared with that page.`

const verifyPrompt = (s, embedded) => `${PRE}

You are the skeptic for slice ${s.name} (${s.title}). A checker reported findings; ${embedded ? 'its result (JSON) is at the end of this prompt' : `its result (JSON) is in ${W}/findings/${s.name}/find-result.json: read it in full first`}. Your job is to try to REFUTE each finding, independently: re-open the page's text (the crawl in ${W}/crawl/out/, the slice file ${W}/slices/${s.name}.json, the sources in the repo) and the ground truth yourself; do not trust the checker's quotes until you have seen them. A finding survives only if the page really says what it is said to say, the ground truth really says otherwise, and the ground truth outranks or postdates what the page relied on.

For each finding return a verdict: confirmed (as reported), partly (real but the claim, severity or fix needs correcting: give the corrected fix), or refuted (with the reason). Check the fix itself: is the new text right and complete, does it go in the file that actually generates the text, and would it break another number that depends on it (the N table in build_facts.py checks displayed numbers against their facts' statements; build_ladder.py's num table does the same for the ladder; the memory levels page shares the ml facts, circuitkit.js and the ladder)? List in fix_files every file the fix must touch. Default to refuted when you cannot reproduce the evidence. For a finding about line-number citations, check a sample of at least ten of its old and new line numbers yourself with sed -n; say in the reason how many you checked.

${HOWBUILT}

If, while checking, you see a clear error in this slice that the checker missed, add a one-line description to "missed" (with the evidence path and line).${embedded ? `\n\nThe checker's result (JSON):\n${JSON.stringify(embedded)}` : ''}`

const results = await pipeline(
  SLICES,
  s => DONE.includes(s.name) ? { precomputed: true } : agent(findPrompt(s), { label: `find:${s.name}`, phase: 'Find', schema: FIND }),
  (r, s) => {
    if (!r) return { slice: s.name, find: null, verify: null }
    if (!r.precomputed && (!r.findings || r.findings.length === 0)) return { slice: s.name, find: r, verify: { slice: s.name, verdicts: [], missed: [] } }
    return agent(verifyPrompt(s, r.precomputed ? null : r), { label: `verify:${s.name}`, phase: 'Verify', schema: VERIFY })
      .then(v => ({ slice: s.name, find: r.precomputed ? 'file' : r, verify: v }))
  },
)
const out = results.filter(Boolean)
log(`verified ${out.filter(x => x.verify).length} of ${SLICES.length} slices`)
return out
