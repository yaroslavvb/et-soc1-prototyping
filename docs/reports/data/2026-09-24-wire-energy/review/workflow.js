export const meta = {
  name: 'verify-heat-per-mm',
  description: 'Independently re-derive and adversarially check every claim of the heat-per-millimetre report before it is published',
  phases: [
    { title: 'Reanalyze', detail: 'two independent re-derivations from raw telemetry' },
    { title: 'Refute', detail: 'three skeptics, one lens each, over every claim' },
    { title: 'Synthesize', detail: 'verdicts and required corrections' },
  ],
}

const REPO = '/home/yaroslavvb/claude/et-soc1-prototyping'
const SCR = '/tmp/claude-1019/-home-yaroslavvb-claude/ed6d06d5-de26-4323-94f1-0dc808eafbda/scratchpad/verify-hpm'
const CTX = `Context: repository ${REPO}. An experiment measured the energy of moving data across the Esperanto ET-SoC-1's on-chip mesh on two cards (aifoundry2, aifoundry3), and a report ("Heat per millimetre") is about to be published. Do NOT touch the lab cards or run anything on them; work only on files. Put any scripts you write under ${SCR}/<your-label>/.

Raw data (one directory per card and run set): ${REPO}/docs/reports/data/2026-09-24-wire-aifoundry2, -wire-aifoundry3 (set v1), -wire2-aifoundry2, -wire2-aifoundry3 (set v2). Each has telemetry.jsonl (ettelem samples at 10 Hz: t_ms, took_ms, board_w, sp.{minion_w,sram_w,noc_w} as [avg,min,max] where avg is a ~1 s first-order filtered average, temp_c.minshire[0] die temperature, mhz.minion), runs.jsonl (one line per kernel launch: cfg, pass, t_start_ms, t_end_ms, bytes, cycles_max, participants, hop_distance, mean_hops, target_map, operands), marks.jsonl (prefill and heater windows that are not measured bursts). Configuration names: v1 wbern/p{P}/hop{d} (bits 1 with probability P, a 512 B image repeated), walt/n{N}/hop{d} (blocks of N bytes alternately 0x00/0xFF), waxis/{x|y}/hop{d}/p{P}, wlegacy/random/hop{d}; v2 wu/p{P}/hop{d} (every line unique, P and 1-P exact complements), wsep/p{P}/hop{d} (pairs chosen so no two flows share a link, one reader per target; hop_distance is recorded as 0, use mean_hops), wfrz/hop{d} (one random 64 B line everywhere: 244/512 bits ones, no two flits differ). hop0 = the shire reads its own scratchpad. Each burst: 3 s of back-to-back 1 KB tensor loads, with ~5 s idle before and ~4 s after. Three passes per card per set, shuffled order.

The pipeline: ${REPO}/workloads/enercat/run_wire.py (runner), ${REPO}/workloads/enercat/analyze_wire.py (analysis -> docs/reports/data/2026-09-24-wire-energy/wire.json), ${REPO}/tools/ettelem/build_wire_report.py (-> report.json with 'headline'), report sources ${REPO}/docs/reports/sources/heat-per-mm.{body.html,script.js}. Research inputs (die geometry, NoC, literature) with sources: ${REPO}/docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md.

The report's claims (numbers as the analysis gives them; 'per hop' is per payload bit per hop unless said; a hop is 3.72 mm):
C1. Energy per payload byte grows linearly with hop distance for every data pattern; on the mesh (NoC) rail the data-dependent part is ~0 at d = 0 and grows by a constant per hop; leaving the shire costs about one extra hop.
C2. Per-hop energy depends on the density of ones, not only on bit transitions between consecutive flits: all-ones data (no transitions) costs about as much per hop as random data; P and 1-P differ; the frozen line (ones 0.477, no transitions) fits. Model slope(P) = s0 + a*2P(1-P) + b*P fits every pattern with rms 0.008 pJ/B/hop on the NoC rail and ~0.04 on board power. v2: NoC rail a = 98 fJ per bit-transition per hop, b = 129 fJ per one-bit per hop; board a = 151, b = 192 (v1 agrees: NoC 95/131, board 139/197). Independent complement test on v2: slope(3/4)-slope(1/4) gives 132 fJ per one per hop (NoC), slope(1)-slope(0) 129.
C3. Contention costs energy: with link-disjoint flows (wsep, d = 1-5) the NoC-rail data-dependent part (random minus zeros) is 90 fJ/bit/hop (both cards 90.6/90.1) against 119 for the loaded all-pairs set (wu, d = 1-4, up to 72% of link-hops shared); the data-independent (zeros) per-hop part 43 against 76; at d = 1, where neither shares a link, they agree. Board: 107 against 186 (data), 56 against 103 (zeros).
C4. One hop = 3.72 mm (3.64-3.76), x and y pitches 3.73/3.70 mm from the published die plot scaled to 570 mm^2; x-only and y-only paths cost the same within 2% on the NoC rail over d = 1-3 (125 and 128 fJ per random bit per hop).
C5. Headline per random bit per mm at 0.485 V: uncontended 24 (data) + 12 (fixed) = 36 fJ on the NoC rail, 29 + 15 = 44 on board power; loaded mesh 31 + 20 = 50 (NoC rail), 46 + 27 = 73 (board). Scaled to 0.9 V by (0.9/0.485)^2 = 3.44 the data-dependent part is ~84-159 depending on meter and loading, bracketing Dally's ~100 fJ/b-mm and Keckler 2011's 121 (40 nm, 0.9 V). Interpretation offered: in capacitance per mm of mesh travel (routers included) the chip is where 40 nm wires were and its advantage is V^2; a bare 7 nm repeated wire would be 12-24 fJ per random bit·mm at 0.485 V from first principles.
C6. Lanes: blocks of 16-128 B cost the same per hop, 256 B blocks ~0.8 pJ/B/hop more on board power; explained by the shire's 4 mesh lanes chosen by PA[7:6] (on one lane consecutive lines are i and i+4, 256 B apart) and a flit of at least one 64 B line; the 256 B case is ~60% of the full-flip prediction.
C7. Practical: a random byte costs 1.5-2.2 pJ per hop (loaded, NoC rail to board, all parts); a 64 B line across 10 hops (~37 mm) costs 1.0-1.4 nJ vs 7.8 nJ to read it from DRAM (energy manual), so the farthest on-chip hand-off is 6-8x cheaper than DRAM; a 32-bit operand crossing one hop costs ~6-9 pJ, about one lane of an 8-lane fadd.ps on random data (5.3 pJ), 'an fp add is worth roughly a hop of movement'.
C8. Instrument caveats: some traffic (s<->s+16 rings; on aifoundry2 the y-only pairs 3 hops apart) starves the service processor's management path so telemetry reads take 0.8-1.6 s and those bursts are dropped; a sampler killed mid-request poisons the management queue.`

const REAN = { type: 'object', properties: {
  method: { type: 'string' },
  results: { type: 'array', items: { type: 'object', properties: { quantity: {type:'string'}, card: {type:'string'}, meter: {type:'string'}, value: {type:'number'}, spread: {type:'string'}, report_value: {type:'string'}, agrees: {type:'boolean'}, note: {type:'string'} }, required: ['quantity','value','agrees'] } },
  discrepancies: { type: 'array', items: { type: 'string' } },
  files: { type: 'array', items: { type: 'string' } },
}, required: ['method','results','discrepancies'] }

const VERD = { type: 'object', properties: {
  lens: { type: 'string' },
  verdicts: { type: 'array', items: { type: 'object', properties: { claim: {type:'string'}, verdict: {type:'string', enum:['holds','holds_with_changes','refuted','cannot_tell']}, evidence: {type:'string'}, required_change: {type:'string'} }, required: ['claim','verdict','evidence'] } },
  other_issues: { type: 'array', items: { type: 'string' } },
}, required: ['lens','verdicts'] }

phase('Reanalyze')
const A = [
  { key: 'reanalysis-A', prompt: `${CTX}

Independently re-derive the key numbers WITHOUT importing or copying analyze_wire.py (you may read it afterwards to compare). Method A: per burst (cfg, pass), board power over idle = mean of board_w over the burst (from 0.5 s after its first launch to its last launch's end) minus the mean of the idle samples in the 3.2 s before the burst and the 3.2 s after it, excluding samples inside any marks.jsonl window (padded by 0.2 s before and 0.6 s after); energy per byte = over-idle W x burst wall time / bytes. For the NoC rail use sp.noc_w[0] averaged over the burst's last 0.6 s minus its mean in the 2.5 s before the burst, divided by 0.94 (the filter), times wall / bytes. Skip the leakage correction the pipeline applies (it is small) and say how much it matters by comparing. Then per card: fit pJ/B against hop distance d (1,2,3,4,6 for wu and wbern; 1-5 for wsep using mean_hops) to get per-hop slopes for each P; fit slope(P) = s0 + a*2P(1-P) + b*P over the v2 wu patterns plus wfrz (ones 244/512, t=0); compute the uncontended (wsep) and loaded (wu d=1-4) random-minus-zeros slopes. Report every number with its card and meter and whether it agrees with the report's C1-C3 numbers within 5%.` },
  { key: 'reanalysis-B', prompt: `${CTX}

Independently re-derive the key numbers with a DIFFERENT method from the pipeline's, WITHOUT importing analyze_wire.py. Method B: work at the level of individual launches and samples rather than burst means. For each burst take the MEDIAN board power over the burst and the MEDIAN of the idle samples in the 3 s before it only (excluding marks.jsonl windows); use device time (sum of cycles_max / 600 MHz over launches) instead of wall time and the duty cycle to convert power to energy per byte; for the NoC rail, use the rail's filtered average but model the first-order filter explicitly (tau ~ 1 s) to recover the burst's step, rather than dividing by 0.94. Then compute per-hop slopes per P per card with a robust fit (e.g. Theil-Sen), the ones/transition model on v2 (wu + wfrz), the complement tests, and the uncontended (wsep) vs loaded (wu, d = 1-4) data-dependent parts. Report whether each of C1, C2, C3 survives your method (numbers within ~10%) and where it does not.` },
]
const rean = await parallel(A.map(t => () => agent(t.prompt, { label: t.key, phase: 'Reanalyze', schema: REAN })))

phase('Refute')
const LENSES = [
  { key: 'artifact', prompt: 'Your lens: MEASUREMENT ARTIFACTS. Try to refute each claim by finding an artifact that could produce it: idle-bracket drift, the leakage correction, the rail filter, telemetry gaps or starvation, the clock, the order of configurations, the prefill contaminating brackets, participants or bandwidth varying with d, per-time costs masquerading as per-hop, and card-to-card differences. For C2 especially: could anything other than the mesh make all-ones cost per hop (e.g. data-dependent energy at the target SRAM or the reader that varies with d)? For C3: could the lower uncontended slope come from fewer readers / lower bandwidth at larger d rather than from link sharing? Check the data yourself.' },
  { key: 'physics', prompt: 'Your lens: PHYSICS AND INTERPRETATION. Try to refute the interpretations: that a per-one cost means return-to-zero or precharged circuits; that 2P(1-P) is the transition rate on the links for these patterns (lanes, interleaving of flows, idle cycles between flits, headers/parity, the request direction); that the lane explanation of C6 holds (check core-et-main shirecache_mesh_master.sv and the research NOC notes); that V^2 scaling to 0.9 V is legitimate for comparing with Dally/Keckler; that "per mm of mesh travel" is comparable to Dally\'s per-mm wire figure; that the chip is "where 40 nm wires were" in capacitance per mm; the first-principles 12-24 fJ estimate; and the bus-inversion suggestion in the report body. Say what the report should say instead where an interpretation overreaches.' },
  { key: 'arithmetic', prompt: 'Your lens: ARITHMETIC, UNITS AND SOURCES. Re-check every number and conversion in the report data (docs/reports/data/2026-09-24-wire-energy/report.json and wire.json) and the rendered text (build the page: python3 scripts/build-report.py heat-per-mm docs/reports/data/2026-09-24-wire-energy/report.json ${SCR}/arith/page.html, then read the body and script to see what numbers the text shows): pJ/B/hop -> fJ/bit/hop -> fJ/bit/mm, per transition vs per one vs per random bit, the pitch range folded into bars, the 3.44 V^2 factor, the practical comparisons of C7 (DRAM 7.8 nJ per line, the fadd.ps lane, 10 hops ~37 mm), and every literature number against research/SYNTHESIS.md and, where you can reach them, the original sources (Dally AHA 2023 slide text, Keckler 2011 Table 1, VLSI 2018, CACM 2020/2022). Flag any number in the text that does not follow from the data or the sources, and any unit error.' },
]
const verdicts = await parallel(LENSES.map(l => () => agent(`${CTX}

${l.prompt}

Independent re-analyses already done (use them as evidence, but check anything you rely on):
${JSON.stringify(rean.filter(Boolean), null, 1).slice(0, 60000)}

For EVERY claim C1-C8 give a verdict (holds / holds_with_changes / refuted / cannot_tell), the evidence, and the exact change the report needs if any. Default to skepticism: a claim holds only if you checked it.`, { label: `refute:${l.key}`, phase: 'Refute', schema: VERD })))

phase('Synthesize')
const synth = await agent(`${CTX}

Combine the re-analyses and the three skeptics' verdicts into one list of required corrections to the report, ordered by importance. For each: the claim, what is wrong or overstated, the evidence, and the exact replacement wording or number. Then list what was confirmed. Be concrete; the author will apply your corrections directly. Write the result as markdown to ${SCR}/VERDICT.md and return it as your final text.

RE-ANALYSES:
${JSON.stringify(rean.filter(Boolean), null, 1).slice(0, 50000)}

VERDICTS:
${JSON.stringify(verdicts.filter(Boolean), null, 1).slice(0, 60000)}`, { label: 'synthesize', phase: 'Synthesize' })

return { synthesis: synth, reanalyses: rean, verdicts }
