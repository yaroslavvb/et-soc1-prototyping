# ET-SoC-1 report set: review fix plan

Plan built from the verified review of the 19 pages linked from https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability. Machine-readable copy: PLAN.json (same content, full texts). The workflow's structured return is a condensed index of this file; the exact replacement texts are here and in PLAN.json.

## 1. Overall assessment

Accuracy. The arithmetic is mostly sound. Reviewers recomputed several hundred figures from the raw data, and most reproduce exactly: the idle law and 73 °C rail split, the catalogue tables, relay and hot-line timings, the thermal model, the cross-card transfer, the ridge-point arithmetic and the matmul rates. The problems are interpretation, freshness, attribution and navigation. Most important first:

1. Pages contradict each other on headline conclusions and never say why.
   - The L2-starvation brief states Ivan's unreproduced 6% / 17× owner penalty as measured and calls l3_yield 'the lever'. The same-day hot-line report measured the owner's share at 1.004, and it is the owner's other loads that stop.
   - Matmul efficiency says the chip is 3.4× more efficient than an A100. Why-low-power says the A100 is about 5× better per FLOP. The difference is fp32 CUDA-core spec against measured bf16 tensor cores, and neither page mentions the other.
   - The energy manual says mesh energy is 'roughly flat in distance'. Heat per millimetre measures about 2 pJ/B per hop.

2. Plain errors in published numbers or mechanisms.
   - The energy manual's L1-fill paragraph is 32× too small (a unit bug).
   - Memory anatomy splits a DRAM load as if the rows were open. They had closed, so the split is 25/66 cycles, not 14/77, and its explorer is shifted by 11 cycles.
   - The relay's 'next shire' is the next shire ID (3.5 mesh hops on average), not a neighbour.
   - The hub puts the rail filter in the service processor. It is the PMIC's own average.
   - DVFS says the governor runs every 10 ms; it runs once per ~133 ms pass. It explains thermal hunting as a power-guardband limit cycle, and presents Erbium RTL as ET-SoC-1 silicon.
   - Horace's long-run table joins the wrong model records.
   - '850 MHz' appears on five pages; the top operating point is 800.

3. Overstated claims.
   - Unmetered power: 'a fifth of any workload'. For DRAM traffic it is 60–75%.
   - The energy floor: 'a watt-hour'. It is a few joules.
   - The attribution: 'to 0.35 W'. It is 1.1–1.3 W on DRAM bursts, and the idle 15 W is not split at all.
   - The DDR droop meter responds to 'DRAM traffic alone'. Mesh traffic also moves it.
   - Horace: '±0.5 W including six patterns written down before they ran'. Those six were 1.3 W rms. Also 'fewer cores buy time in proportion': a quarter of the cores lasts 11–16× as long.
   - Energy manual: 'within a class the instructions cost the same'. They spread 1.2–5×.
   - DVFS: 'the silicon has per-minion sleep'. That is in the open RTL only.
   - Kanter's paraphrased words appear in quotation marks.

4. Stale material with no warning.
   - The 18–19 September energies per byte (memory hierarchy, memory anatomy, the ridge points' energy balance) are superseded by the energy manual.
   - The hot-line and relay energies are single-session values; the reruns' bars are not shown.
   - Power and temperature still has the '~2 s moving average', the 0.8 W/°C and 'what would unlock more'.
   - getting-started and the root README say the spaces are private. Following them would break the hub's links.
   - Stale counts: A1–A18, 19 rungs, 'fourth version'.
   - The DVFS firmware reading was done at et-platform 353f20e, but the card's own trace strings show an older build.

5. Hub index errors.
   - The per-shire voltage map is credited to the spatial brief in five places. It is Power and temperature §3.
   - Thermal time constants are credited to Power and temperature. They are in Horace §4 and §8.
   - Test drive is misdated (18 Sep, not 17).
   - Six report rows are misdescribed.
   - The list says 'newest first' but is not.
   - The sessions table misses E1 and the 18 September work, and misdescribes E7.
   - The reviewers were AI agents, and the method section does not say so.

6. Browseability.
   - 15 of 19 pages have no heading ids, so nothing can link to a section.
   - Only 3 pages end with a related-reports list.
   - Only the hub and Heat per millimetre have a table of contents.
   - Most pages name sibling reports without linking them.
   - Public pages use internal names: 'the nekko workspace', 'Finding: …', 'the brief', E25, bare repo file names.

7. Readability.
   - No page defines minion, hart, shire, scratchpad, SP, PMIC or TensorFMA.
   - Several pages open with a changelog byline or with a correction of an earlier edition the reader never saw.
   - Some charts lack units or legends.
   - The spatial brief shows raw LaTeX.
   - Some numbers are printed with more precision than they have (11939 nJ, 20929.8 pJ, 104.77 pJ/B).

8. Privacy. The hub publicly links a personal memo about a named third party, the David Kanter brief. This needs an owner decision.

Layout. Known: two published-only briefs overflow at phone width. New: the ridge-points and matmul tables clip their key columns at desktop width.

## 2. Cross-document decisions

CANONICAL VALUES (use this wording everywhere; every group's texts below already follow it)

D1 Operating points
- Three: 600, 700 and 800 MHz at 0.517, 0.568 and 0.618 V. Never write 850 MHz.
- The governor steps down when the whole-degree die reading is above 65 °C or board power is above 65 W.
- In practice the clock lifts to 700–800 MHz mid-burst below about 68 °C (ettelem's mean reading), so warm passes are preheated to 76 °C.
- aifoundry3 reports a TDP of 0 W and never leaves 600 MHz.

D2 The meters
- Board (12 V input) power: 10 mW steps, one new value per service-processor pass of about 133 ms.
- The three rails (minion, SRAM, NoC) are the PMIC's own running average, roughly first-order with τ ≈ 1 s: a step reaches 61% after 1 s and 88% after 2 s. The SP copies it each pass, with min and max since reset. The SP does no filtering.
- Never write 'a ~2 s moving average' or 'the SP's filter'.
- The governor runs once per ~133 ms pass. The 10 ms is only the sleep at the end of the pass.
- ettelem samples at 10 Hz. One sample is six management commands, about 22 ms; about 150 ms when an s ↔ s+16 ring starves the SP.
- Note (25 Sep): superseded by PLAN2 §2.1 D2′ (rails: 55–57% of a step after 1 s, 83–84% after 2 s, τ ≈ 1.15–1.22 s, from catalogue.json rail_filter; 133 ms is aifoundry2's, about 250 ms on aifoundry3); see PLAN2.md in this directory.

D3 Idle law and leakage slope
- P_idle = 12.6 W + 23.3 W·e^((T−80)/36) (aifoundry2). Slope: 0.52 W/°C at 72 °C, 0.65 at 80, 0.78 at 87.
- Canonical slope: '0.65 W/°C at 80 °C (the idle law)'.
- '0.81 W/°C' only as 'the drift of busy power within the hot 7 s runs (80–86 °C)'.
- '0.78 W/°C' only as 'the first, uncontrolled Horace session (20 Sep, superseded)'.
- Quote die temperature with every idle figure.
- Leakage is 64% of idle at 80 °C and 36% of a 64 W random-data matmul. The energy manual's 65% (of the law's 35.9 W) is also fine.
- Note (25 Sep): amended by PLAN2 §2.1 (D3 addendum): the DVFS page and the knowledge base now quote 65% (dvfs.json leak_fraction.idle_80c_law); see PLAN2.md in this directory.

D4 Energy per FLOP and the A100 comparison
- Dense random fp32 TensorFMA at 80 °C: 6.9–7.0 pJ at the launch temperature (63.4 W in E9, 63.9 W in E15, over 9.18 TFLOP/s). 7.3 pJ only when labelled 'averaged over the 7 s run'. fp16: 3.3 pJ.
- A100: 1.28 pJ per bf16 FLOP (Horace He: 257 TFLOPS at 330 W, i.e. 779 GFLOP/s per W, equal to the 312/400 spec ratio).
- Canonical framing, used on why-low-power, matmul efficiency, findings 13 and the README: 'The A100's bf16 tensor cores are 5.4× more efficient per FLOP than this card's fp32 and 2.6× more than its fp16. Against the A100's fp32 CUDA-core datasheet figure (19.5 TFLOPS at 400 W), this card is about 2.9× better on random data and 3.4× on the matmul benchmark's ±1/±2 operands.'
- Kernel variants: 529 cycles per op with B streamed through TenB (the matmul report) against 546 with A and B in the L1 scratchpad (Horace, sparse compute, why-low-power). int8: 280 against 318.
- Note (25 Sep): amended by PLAN2 §2.1 (D4 addendum) for the matmul page's 2.9×; see PLAN2.md in this directory.

D5 The A100 itself
- Clock under Horace He's 330 W cap: 1,160–1,410 MHz, probably about 1,230. So the V²f factor is 5–6×; 6.3× holds only at maximum boost.
- Memory: HBM2 at 1,555 GB/s (40 GB) or HBM2e at 1,935–2,039 GB/s (80 GB); 1.40 TB/s sustained (40 GB).

D6 Awake core and activity term
- The catalogue's addi loop: 2.1 mW per minion on one hart (5.5 pJ per instruction), 3.4 mW on both.
- The 21 September ablation's loop (four adds and a branch, half the issue rate): 1.4 mW and 8.1 pJ.
- The per-issue-slot floor is a nop or a fence: 4.5–5.3 pJ.
- Activity term under a random fp32 matmul: 25.6 mW per minion at 256 and 512 active, 26.2 at 768, 27.0 at 1,024 (27.6 W). A line through zero gives 26.5 mW.

D7 Energy per byte (reads)
- Canonical source: energy manual §4 (23 Sep, pinned 600 MHz, two cards). L1 0.77, L2 2.51, own scratchpad 2.52, remote scratchpad 6.65, L3 10.5, DRAM 122 [117–129] pJ/B, from memhier's streaming probe over buffers that were never written.
- Tensor loads on known data: DRAM 91 (zeros) to 129 (random), own scratchpad 2.0–4.2.
- The L2 cache and the local scratchpad cost the same.
- Wherever the 18 September (148 / 2.8 / 4.3), 19 September (anatomy: 79 on the trace, 92 on the host log) or ablation (142) figures appear, they are marked superseded.

D8 Bandwidth and latency at 600 MHz
- L1 6.2 TB/s. L2 2.45 TB/s (128 B per shire-cycle, 4.0 B per minion-cycle). Own scratchpad 2.46. L3 0.98. Remote scratchpad 0.96 TB/s. DRAM 76 GB/s on both cards.
- DRAM peak: 119 GB/s at the 3,733 MT/s implied by the 933 MHz DDR clock. The datasheet maximum is 136.5 GB/s at 4,266 MT/s. The runtime's '128 GB/s' is a firmware placeholder.
- DRAM latency: about 500 ns at 600 MHz (about 290–300 cycles; memory-anatomy median 299 cycles), about 440–460 ns in chases the governor ran at 800 MHz.
- Note (25 Sep): amended by PLAN2 §2.1 (D8 addendum): DRAM at 600 MHz is 479–495 ns in the memory-hierarchy chases; see PLAN2.md in this directory.

D9 The mesh
- Geometry: the 32 compute shires plus the master, spare, I/O and PCIe shires form a 6×6 grid. With the memory shires down two sides it is 8×6 mesh stops. One hop is 3.72 mm (3.73 × 3.70; range 3.64–3.74).
- marty1885's logical map is the die turned a quarter: in map orientation the memory shires sit above and below the grid; on the die they are west and east.
- Shire IDs do not follow the mesh. The next shire by ID is 1–10 hops away, 3.5 on average; s+16 is 2.1 on average.
- A TensorSend round trip is 150 + 12.02 × hops cycles; 20 ns per hop at any clock.
- Energy per hop, canonical source Heat per millimetre: 2.17 pJ/B on random data, board power, loaded mesh; 1.50 on the mesh rail; 1.4 and 1.1 on free links. On the mesh rail it splits into 98 fJ per bit that differs from the previous flit plus 129 fJ per one carried.
- The catalogue's 1.81 pJ/B per hop (fitted over 1–8 hops) is pulled low by the 8-hop point, reached by only 16 shires. Over 1–6 hops the same data give 2.1–2.3. Say 'flips plus ones carried', never 'toggling of the wires'.
- Cross-shire messaging: 9.3 + 1.7 pJ/B per mean hop.

D10 Unmetered power
- Half of idle (15.1 of 31.8 W at 73 °C) is on no sensor. Of what a workload adds above idle: about a sixth for arithmetic, three fifths to three quarters for DRAM traffic (70% of a DRAM read).
- The fit is to 392/386 configuration means, not bursts: 0.35 W rms, 1.1–1.3 W on the DRAM configurations. Minion-rail delivery loss is 18–20% (0.196 on a2, 0.177 on a3; the cards differ by 10%). DRAM off-rail: 73/68 pJ per byte. The idle 15 W is not split.
- DDR-rail droop: 0.84 mV per W of off-rail DRAM, rms 0.36 mV, refreshed every 133 ms. Heavy mesh and scratchpad traffic also droops it 1–1.7 mV, a phantom 0.8–1.8 W of DRAM.
- Note (25 Sep): superseded by PLAN2 §2.1 D10′ (the droop regenerated by fit_unmetered.py: 0.87 mV/W, rms 0.37 mV; the DRAM residual about a quarter; idle unsensed 12–16 W); see PLAN2.md in this directory.

D11 Two cards
- Catalogue ratio: median 0.95 (10–90%: 0.91–0.99) over 386 shared entries. Tensor-unit flip energies scale by 0.92 (0.924). Idle offset +0.73 W.
- aifoundry3 ran the 18 Sep sparsity runs and the test drive, E20–E27, E29, E31 and E32. For E23 that is the sweeps without power; for E24 the probe rows (verified: both onchip-*/sweep.jsonl files have 2 probe rows).
- E18, E19 and E28 ran on aifoundry2 only.
- Note (25 Sep): superseded by PLAN2 §2.1 D11′ (+0.73 W is the mean of the four temperature bins; the transfer wording 0.36 / 0.93 / 1.53 / 0.27 W); see PLAN2.md in this directory.

D12 Contention (the hot line)
- The host shire's share of a contended atomic is 1.004 (every shire 0.998–1.004). Its own loads fall to 0.02% (384 of 1,688,306).
- About 24 remote requesters are needed; 20 still leave the host at 98.9%.
- Pacing: 10,000 cycles gives the host 54%, 16,000 gives 95%, 100,000 gives 98%.
- Energy: 19.8 [16.9–23.6] nJ contended against 1.16 [1.01–1.37] spread, 17×, n = 7. 23.6 / 1.4 is the first session.
- Ivan's 6% / 17× owner penalty was not reproduced.
- Errata numbering: the TOC's 3.1 and 3.2 are the body's 4.1 (RTLMIN-6207) and 4.2 (RTLMIN-6214). l3_yield does not rescue same-address requests; whether it helps the owner's other traffic is untested.
- Note (25 Sep): superseded by PLAN2 §2.1 D12′ (chip barrier 4,995 cycles with one minion per shire, 5,018 with all 1,024, never 4,997; the ring reads 33–45% low; the bank rule is necessary, not sufficient); see PLAN2.md in this directory.

D13 The relay
- DRAM 105.7 [99.5–111.0], next shire 8.6 [7.8–9.2], own scratchpad 3.99 [3.90–4.25] pJ/B (n = 8, four per card). First run: 104.8 / 8.9 / 4.25.
- Speed-ups 12.3× / 12.4× and 30.7× / 31.2×: the two cards agree within 2%.
- The 18 September ring energies as published on the on-chip page read 2–20% (median 10%) above the reruns.
- Note (25 Sep): superseded by PLAN2 §2.1 D13′ (which shire receives the slab moved the bandwidth by up to a quarter, falling with the longest hand-off); see PLAN2.md in this directory.

D14 Thermal model (Horace)
- Flip budget: 3.1 W at the fitted 22.8 °C ambient of 21 September; 0.3–0.7 W under 22 September's conditions. 1.47 °C/W total resistance; loop gain 0.95.
- Time to 90 °C on held-out runs: 9% median, 23% worst on later runs of the same session; 7% and 65% on a different afternoon.
- Structured matrices: 0.92 W rms; 10 of 14 within 0.6 W (11 within 0.75 W).
- Power model: 0.50 W rms leave-one-out; the pre-registered predictions were off by 1.3 W rms.
- Thermal time constants are in Horace §4 and §8.
- Rises below about 0.5 °C (zeros, checkerboard, 75% zeros) are bounded, not measured.
- Flip energies for prediction: Horace §8 (3.18 / 0.025 / 0.80 / 15.5 fJ).

D15 Per-shire voltage map
- It is in Power and temperature §3: 517–521 mV current, lows to 513 mV, 34 shires read, 32 drawn. The spatial brief only mentions it.

D16 RTL and firmware
- RTL: 'core-et's Erbium branch at b38a1a3: the same Minion core lineage in a later MCU-class configuration, not the taped-out ET-SoC-1'.
- Firmware, until the owner resolves it: 'source read at et-platform 353f20e; the cards' own trace strings match an older build (before et-platform commit 60b40c10f, 24 Sep 2024)'.

D17 Gating
- Only clock gating works. The open RTL's per-minion sleep and isolation are tied off.
- Write 'clock-gated', never 'gated off'.

D18 SRAM
- The SRAM rail feeds 128 MB of shire SRAM (4 MB × 32 compute shires).
- 'Over 160 MB on die' is Esperanto's own figure (Hot Chips 33); keep it, with that attribution. The datasheet says 140 MB.

D19 Statistics words
- Write 'rms' (not '±') for fitted errors, and 'median' for median errors.
- 'mean [lo–hi]' means the range over passes.
- In the unmetered fit, write 'configuration means', not 'bursts'.

D20 Dates and times
- Test drive: 18 Sep. Horace: 20–22 Sep. The spatial and L2 briefs: 22 Sep. Ridge points: computed 18 Sep, published 24 Sep.
- The long idle: 'about 20.5 hours', with no workload since 15:08 on 21 Sep except E18's 4.9 s probe five minutes before the sample.
- Times in 03-experiments are UTC−7.
- Erratum (verified 25 Sep): dvfs.json idle_check gives 20.63 h; E16's last launch ended at 15:06 (telemetry to 15:08). Use about 20.6 hours and 15:06 wherever this plan says 20.5 or 15:08 as the end of the last workload (here in D20, and in the change lists below, for instance 'Set hours_idle to 20.5'); do not set hours_idle by hand. PLAN2 §2.1 D20′.

CROSS-LINKING SCHEME

X1 Every page ends with an h2 'Related reports' of at most 8 items, each '<link> — why read it', followed by '← All ET-SoC-1 measurement reports' (hub #reports). The template adds the footer and a contents list to source-built pages with 6 or more h2s; standalone pages get both by hand. Each group's own change lists its items.

X2 Anchors. All 15 pages without heading ids get them:
- the six patched source-built pages, by rebuilding with the current template;
- the 7 standalone pages and 2 briefs, by pasting the template's section-anchor script before </main>.
Links in this plan use the resulting slugs:
- hub: #reports #power #the-chain #the-unmetered-remainder-attributed #bits #improve #ladder #terms
- energy manual: #the-card-at-rest #a-core-that-is-awake #the-tensor-unit-per-multiply-add #bytes-through-the-memory-hierarchy #bytes-between-cores-and-shires #synchronisation
- Horace: #from-flips-to-watts #the-speed-effect-appears-on-a-cool-die #a-model-from-flips-to-temperature #a-second-card-and-what-transfers #strict-temperature-control
- Power and temperature: #the-per-shire-voltage-map (#vmap works today)
- DVFS: #the-same-firmware-on-three-cards #the-loop-as-measured
- Heat per millimetre: #die #ones #compare #meaning
- On-chip communication: #every-primitive-against-a-gpu #reduction-trees #a-trap-one-ready-flag-per-minion #energy-per-byte-moved
- Memory anatomy: #where-the-energy-goes #l3-110-cycles-plus-12-per-hop
Until a target page is rebuilt, link it without the fragment.

X3 Superseded material. An older page whose number was re-measured carries a short 'Later measurements' or 'Update' box under its lede, naming and linking the newer page: memory hierarchy, memory anatomy §7, on-chip communication energy, sparse compute power, the matmul A100 comparison, power and temperature, the L2 brief, ridge points' energy balance.

X4 Required links, both directions:
- L2 brief ↔ hot line
- matmul ↔ why-low-power (the two A100 verdicts)
- memory hierarchy, memory anatomy, ridge points → energy manual §4
- on-chip communication → energy manual §5 and Heat per millimetre
- relay ↔ Heat per millimetre
- hub E6 and the spatial brief → Power and temperature §3
- Horace ↔ sparse compute, why-low-power, DVFS, energy manual §3.2
- test drive → matmul
- DVFS ↔ the Kanter brief, only if it stays public

X5 Repository paths are GitHub links (https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/<path>). Public pages never say 'the nekko workspace', never cite a findings file by title ('Finding: …'), and never name an unpublished 'brief'.

CONVENTIONS

C1 Titles: '<Topic> · ET-SoC-1'; the hub is 'Limits of observability · ET-SoC-1 reports hub'. The h1 says what was found where possible. Keep every slug.

C2 Byline: 'D Month YYYY · card(s) · firmware/RTL where relevant · part of the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability'>ET-SoC-1 measurement reports</a>'. Version history goes on a 'Versions' line at the end of Method, never in the byline or at the start of a section. No 'first version of this brief' in body text.

C3 First-use definitions. The canonical 'chip in brief' text G below goes on the hub (card id='terms') and as '## Terms' in docs/findings/README.md. Every other page gets a 2–4 sentence 'Terms' paragraph drawn from G, ending 'more in the hub's glossary' (hub #terms), plus any page-specific terms.

C4 Experiment and request IDs (E12, Q4, A15, R8) do not appear bare on public pages. Where one is needed, write 'session E29 of the experiment register' linked to docs/findings/03-experiments.md. The hub sessions table keeps E-IDs, with that link in its intro.

C5 Numbers: thousands separators, en-dash ranges, a unit on every figure, '10¹²' not 'e+12', no more precision than the bar supports (12 µJ, not 11939 nJ).

C6 British spelling throughout (grey, neighbourhood, colour).

C7 Visibility: every hub-linked space is public (Q40), except as decided for the Kanter brief. docs/findings/04-artifacts.md is the record.

G, the canonical glossary text (paste, then trim per page):
'The chip in brief. The ET-SoC-1 is Esperanto's RISC-V accelerator, now open-sourced by AI Foundry. Its compute cores are minions: small in-order RISC-V cores, each with two hardware threads (harts), an 8-lane fp32 vector unit and a tensor unit whose matrix multiply-accumulate instruction is TensorFMA (one fp32 op multiplies 16×16×16 tiles: 4,096 multiply-adds). Only hart 0 issues tensor operations (hart 1 may only prefetch into the L2 scratchpad). Eight minions form a neighbourhood and 32 a shire. Each shire has 4 MB of SRAM, which these cards' firmware splits into a 512 KB L2 cache, a 1 MB slice of the chip-wide 32 MB L3 and a 2.5 MB scratchpad: software-managed memory that any shire can address. Each minion also sets aside 3 KB of its 4 KB L1 data cache as an L1 scratchpad for tensor operands. The chip has 34 minion shires (1,088 minions): 32 run kernels (1,024 minions), the master shire runs firmware and one is spare. With the I/O and PCIe shires they form a 6×6 grid on a mesh network-on-chip (NoC, 400 MHz); eight memory shires with the LPDDR4X controllers (32 GB) sit along two sides, making 8×6 mesh stops. A flit is the unit the mesh moves as a whole. The service processor (SP) is the on-die management core: its firmware reads the sensors, runs the clock and voltage governor (600, 700 or 800 MHz) and answers the host's management commands. The PMIC is the board's power-management controller: it meters the 12 V input and three regulators (the minion, SRAM and NoC rails). Moortec PVT monitors measure temperature and voltage on the die. Kernels run in user mode (U-mode) and firmware in machine mode (M-mode). The four Maxions are larger out-of-order RISC-V cores on their own 0.6 V rail. aifoundry2 and aifoundry3 (a2, a3) are the lab machines that hold the two cards measured. The Horace experiment is named after Horace He's post showing that GPU matrix multiplies run faster on predictable data.'

ORDER OF WORK
1. The shared template group lands first.
2. Each document group edits its own files, then rebuilds and redeploys its page.
3. The hub group applies its anchor fragments after the pages they point to are rebuilt; until then it links without fragments.
4. The findings group can run in parallel with everything else.
5. Published-only pages wait for the owner's decisions (open questions 1 and 4).

## 3. Fix list by file owner

Each group owns its files exclusively, so groups can be applied in parallel. Within each group, changes are ordered by severity. IDs refer to the reviewers' findings; where several findings touched the same text, they are merged into one change. Exact replacement text is given in quotes or HTML.

### 3.1 shared: report template

Files: `docs/reports/sources/report.template.html`

1. **[medium] nav-12** — *report.template.html, after the section-anchor script (lines ~110–128)*

   Add two blocks.
   (a) Contents: a script that runs when main has 6 or more h2 elements and no element with id 'toclist' exists. It inserts before the first h2 a <nav class='card'><b>Contents</b><ol>…</ol></nav> with one <li><a href='#<id>'> per h2, labelled with the heading text minus any leading section number.
   (b) Footer: before </main>, add <p class='small'><a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports'>← All ET-SoC-1 measurement reports</a></p>.
   The hub, Heat per millimetre and the energy manual build their own #toclist, so the guard skips them.

2. **[medium] nav-11** — *sequencing for every source-built page*

   Land the two template changes above first.

   Then each document group, after its own edits, rebuilds its page with scripts/build-report.py <name> <data.json> <out.html>. It redeploys to the existing space uuid (manifest.tsv or docs/findings/04-artifacts.md) and checks visibility with npx spacesheep list.

   Six pages were patched rather than rebuilt: dvfs-leakage, horace-experiment, hot-line, on-chip-relay, power-temperature and why-low-power. This rebuild gives them heading ids.

   The standalone pages get the same result by hand. That is memory anatomy (through its own template), memory hierarchy, on-chip communication, matmul efficiency, sparse compute, ridge points, the test drive, and the two published-only briefs. Copy the template's section-anchor script and the two blocks above before </main>.

   Keep every slug. Every Horace redeploy must include its GIF files.

3. **[low] nav-14** — *report.template.html, same script block*

   Add an inline-path linker. For every code element under main that is not inside pre and not already inside a link, and whose whole trimmed text matches ^(docs|workloads|tools|scripts|kernels|rtl-sim)/[\w./-]+$, wrap it in <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/<text>'>. Command blocks and shorthand such as '-aifoundry3/' stay unlinked.

### 3.2 et-soc1-limits-of-observability (hub)

Files: `docs/reports/sources/limits-of-observability.body.html`; `docs/reports/sources/limits-of-observability.script.js`; `docs/reports/sources/limits-of-observability.data.json`; `docs/reports/sources/limits-of-observability.meta.json`; `docs/reports/2026-09-20-et-soc1-limits-of-observability.html (rebuilt)`

1. **[high] hub-1, nl-6, nav-07, fr-6** — *body.html, lede, last sentence*

   Replace 'Half of the idle power and a fifth of any workload's is on no rail sensor at all' (with the rest of that sentence) with:
   'Half of the idle power is on no rail sensor; of what a workload adds, about a sixth for arithmetic and three fifths to three quarters for DRAM traffic. §4 says what that remainder is made of and §5 what would meter it.'

2. **[high] hub-8, nl-6** — *body.html, lede*

   'For energy, the floor is a watt-hour's worth of identical events' → 'For energy, the floor is a few joules' worth of identical events (at least 10⁹ a second for 3 s, repeated over passes and cards)'.

3. **[high] hub-2** — *body.html line ~20 (KPI 'Power on no sensor'), script.js line ~86, data.json ladder row 'Unmetered power, attributed', improvements rung 2, and the 'What each rung does to the unmetered watts' paragraph*

   KPI sub-line → 'of idle at 73 °C, unsplit; above idle, the unmetered part of a burst is attributed to 0.35 W rms (1.2 W rms on DRAM bursts)'.
   Fit-table label 'residual rms, bursts' → 'residual rms, configuration means'.
   Ladder gran → 'rms 0.35 W over 392 configuration means (1.1 W on the 17 DRAM ones); coefficients ±1.4% (minion), ±2% (DRAM), ±7–33% (NoC, SRAM)'.
   Rung 2 effect → 'Unmetered power above idle gets a name per configuration to rms 0.35 W (about 1.2 W on DRAM bursts): 18–20% delivery loss on the minion rail, 68–73 pJ per DRAM byte off-rail. The idle 15 W stays unattributed.'
   Paragraph → 'Today: 15 W of a 32 W idle and 4–7 W of a DRAM workload are on no sensor; the regression attributes the part above idle to rms 0.35 W across the catalogue (about 1.2 W on DRAM bursts) and leaves the idle 15 W unsplit (rungs 2 and 3, done).'

4. **[high] hub-3, em-26** — *body.html §4.3 paragraph after the droop table; script.js drooptext and line ~97 column header; data.json rung 3 and ladder row 'DDR-rail droop'*

   §4.3: replace 'but it responds to DRAM traffic alone, so it separates DRAM from everything else in a mixed burst and it does not drift with the die temperature the way the board's idle does' with:
   'and it responds mostly to DRAM traffic, but not only: heavy mesh and scratchpad traffic with no DRAM access droops it by 1–1.7 mV (tload/scp/random 1.74 mV and wire/hop6/random 1.05 mV in the table above), 0.6–1.5 mV more than the fit allows, which it would read as roughly 0.8–1.8 W of DRAM. So it separates DRAM from arithmetic in a mixed burst, but not from mesh traffic, and its idle reading moves by about 1 mV between 71 and 77 °C.'
   drooptext → '… with an rms of 0.36 mV over 386 configurations, an eighth of the smallest DRAM burst's droop (about 2.9 mV); the DRAM slope rests on 11 configurations, and the largest residuals, about +1 to +1.7 mV, are mesh and scratchpad bursts with no DRAM traffic.'
   Column 'DRAM W off-rail (fit)' → 'unmetered W less fitted rail losses'.
   Rung 3 effect → 'DRAM activity every 133 ms at 1 mV ≈ 1.2 W, confounded by heavy mesh traffic; a second witness for the DRAM term.'
   Ladder note: 'it moves with DRAM traffic alone' → 'it moves mostly with DRAM traffic (mesh traffic adds up to about 1.7 mV)'.

5. **[high] hub-4, hub-m2, hub-30** — *body.html §4.1 first and second paragraphs; data.json ladder rows 'Rail power' and 'Board power', rungs 4 and 7; §6 GPU table row 'Power'*

   §4.1, from 'For each of those three…' to the end of the paragraph:
   'For each of those three it holds voltage, current and power on both sides of the regulator, and its temperature, each as a current value, a minimum and maximum since the last reset, and a running average: 84 numbers. The service processor reads all 84 every loop pass and forwards to the host the PMIC's running average of each output-side power (roughly first-order, τ ≈ 1 s: a step reaches 61% after one second and 88% after two, which is why the Power and temperature report says the rails lag about 2 s), with its min and max, and the 12 V input power; ettelem samples them at 10 Hz. The SP's copy refreshes every 133 ms because its I2C driver waits a millisecond after each transaction; how often the PMIC itself updates is unknown.'
   §4.1 second paragraph: 'each command takes 150 ms instead of 22' → 'a telemetry sample of six management commands takes 150 ms instead of 22'; 'take each command to about a second' → 'take a sample to about a second'.
   Rail power gran → '1 mW; the PMIC's running average (τ ≈ 1 s) of each regulator's output power, copied by the SP every 133 ms; min and max since the last reset'.
   Board power note: 'The host can poll 60×/s but' → 'The host can poll much faster than the value changes (ettelem's six-command sample takes 22 ms), but'; 'from 22 ms to 150 ms per command' → 'from 22 ms to 150 ms per six-command telemetry sample'; 'reading at 10 Hz' → 'updating every 133 ms'.
   Rung 4: 'The SP's rail averages' → 'The PMIC's rail averages, as the SP forwards them,'.
   Rung 7: 'how long the management command took' → 'how long its six management commands took'.
   GPU table ET cell → 'Board power every 133 ms at 10 mW, plus three rails as the PMIC's ~1 s running average at 1 mW; no energy counter.'

6. **[high] hub-5** — *body.html, directly after the KPI cards*

   Insert <div class='card' id='terms'><b>The chip in brief.</b> …</div> containing glossary text G (decisions), plus: 'PShire is the PCIe shire; VDDQ is the DRAM I/O supply; MDI is the Minion Debug Interface the SP exposes to the host; DM_CMD_* are the host's management commands to the SP; BL1 and BL2 are the SP's boot stages; OTP is one-time-programmable fuse memory; PRM is Esperanto's Programmer's Reference Manual; sys_emu is the functional simulator; ettelem is this project's telemetry client.'

7. **[high] hub-12, nav-03, nl-19, hub-dvfs-1, sp-7, hub-inst-1** — *data.json ~56 (ladder 'Temperature and voltage'), ~739 (rung 5), ~906–913 (sessions E6), ~423/~424/~1070 (spatial brief entries), ~430/~1060 (Power and temperature entries); body.html §4.3 ~line 111*

   Ladder note: '(the spatial brief's IR-drop map)' → '(the per-shire voltage map in Power and temperature, §3)'.
   Rung 5: '(the spatial brief's map)' → '(the map in Power and temperature, §3)'.
   E6:
   - report → 'Power and temperature, §3';
   - url → https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature#the-per-shire-voltage-map (use #vmap until that page is rebuilt);
   - '(513–521 mV)' → '(517–521 mV at idle; low captures to 513)'.
   Spatial-brief entries: drop 'the per-shire IR-drop map from the DEBUG trace' (new wording is in the §1 rewrite below); instruments → 'none: firmware (353f20e) and RTL (b38a1a3) source reading'.
   Power and temperature entries: 'the card's thermal time constants' → 'the 34-shire voltage map from the SP's DEBUG trace'. The time constants are in Horace §4 and §8.
   §4.3: 'which the spatial brief turned into a per-shire IR-drop map from the SP's debug trace' → 'which <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature'>Power and temperature</a> (§3) mapped shire by shire at idle from the SP's debug trace'.
   Leave rung 12 (~809) unchanged.

8. **[high] hub-13, nav-01, hl-2, l2-3, nl-1** — *data.json reports row 'L2 mainline starvation' (~455–459)*

   title → 'L2 mainline starvation: a brief'.
   what → 'An argument written on 22 September, before the reproduction that afternoon, from a result Ivan reported in Discord and the shire-cache spec: move hot shared lines to a shire that does not compute, and why a two-dimensional TensorSend systolic array hangs. Its 6% owner penalty was not reproduced: see One hot line stops a shire.'
   instruments → 'none: the spec, the errata and a reported result'.
   File it under the 'Briefs' group in the §1 rewrite below.

9. **[high] hub-9** — *body.html lede and KPI 'Finest state on the card' (line ~18)*

   Lede: '…one clock cycle for time and one 64-bit register of a halted hart for state' → '…one clock cycle for time and, in principle, one 64-bit register of a halted hart for state (the debug interface is in the shipped firmware, but no client exists yet and it has not been tried on this card)'.
   KPI sub → 'one GPR, CSR or memory word of a halted hart per management round trip; in the firmware, untried (§2)'.

10. **[medium] hub-19, nav-06, hub-14, hub-nm-1, hub-15, relay-4, nl-16, hub-1 (ridge-matmul), hub-sgemm, hub-anat-td, hub-sparse-6, horace-28, hub-1 (lowpower), hub-1 (heat-relay), nl-41, hub-24, nl-40, em-18** — *body.html §1 intro (~line 26) and closing sentence; data.json reports[]; script.js reports renderer; data.json related[] texts*

   §1 intro → 'Everything measured on these cards so far, grouped by subject and newest first within each group.'

   Add a 'group' field to each report and render a group header row in script.js, as the improvements table already does. Groups:
   - 'Energy and power': Heat per millimetre, energy manual, DVFS, Horace, why low power, power and temperature.
   - 'Contention and moving data': hot line, hand it to the next shire.
   - 'Memory and compute baselines, 18–19 September': anatomy, memory hierarchy, on-chip communication, matmul, sparse compute, ridge points, test drive.
   - 'Briefs: analysis, no new measurements': spatial temperature, L2 mainline starvation.

   Delete the maintainer sentence that closes §1 ('This page is the index … change here').

   Row edits (what / date / instruments):
   • Heat per millimetre, what → 'The energy of moving one bit one millimetre across the mesh, with the data on the links chosen: per bit that differs from the previous flit, per one carried, and the part no data changes, on contended and uncontended links, against Dally's ~100 fJ/bit·mm.'
   • Energy manual: 'with a confidence bar on every entry' → 'with confidence bars from repeated passes on two cards'.
   • DVFS: append '; aifoundry3's firmware reports a TDP of 0 W, which pins it at 600 MHz; the open RTL's per-minion sleep controls are tied off and the card shows no array power gating'.
   • Horace: date → '20–22 Sep'. What → 'Same matmul, same FLOPs: 38 W on zeros, 47 on ones, 63 on random data; RTL flip counts predict the power to 0.5 W rms; a flips-to-temperature model; from a cool die zeros run 25% faster; 14 structured matrices priced before they ran; the model carries to a second card with one scale factor.'
   • Why low power, what → 'Esperanto's P = C·V²·f + leakage measured term by term through ablations at 80 °C and set against an A100: voltage and clock give 5–6× less switching power, 1,024 cores in an integer loop add 1.5 W, leakage is 23 W of the 36 W idle, and per FLOP the card still spends more energy than the A100's bf16 tensor cores.'
   • Power and temperature, what → 'The first look at the meters: every way to read power, voltage and temperature and what each resolves; board power every 133 ms and three rails behind the PMIC's ~1 s average; idle power that rises with die temperature; the 34-shire voltage map from the SP's DEBUG trace.' Instruments → 'board power, rails, die temperature, SP stats and DEBUG traces'.
   • Hand it to the next shire: '; hop distance is free' → '; which shire receives the slab makes no difference to bandwidth (the next shire by ID is 1–10 mesh hops away, 3.5 on average; what each hop costs in energy is in Heat per millimetre)'.
   • Anatomy of a memory access, what → 'One load taken apart to ±3 cycles for 97% of lines: the L3 home shire from PA[10:6], the memory shire from PA[8:6], DRAM banks, rows and refresh, and where the eight memory shires sit around the mesh; energy per load split by rail (since re-measured in the energy manual); the cycle counter's late-carry bug and its fix.' Instruments → 'evict_va + cycle counter, memory-shire read counters (syscall 10), board power, SP rail trace'.
   • Memory hierarchy, what → 'Latency and bandwidth of every level, with the governor free to move the clock: L1 8.8 ns, L2 78 ns, L3 ~280 ns, DRAM ~490 ns at 600 MHz, 76 GB/s streaming. Its energy per byte is superseded by the energy manual §4 (L1 0.77, L2 2.51, DRAM 122 pJ/B).' Link 'energy manual §4' to …et-soc1-energy-manual#bytes-through-the-memory-hierarchy.
   • On-chip communication, what → 'Where the 32 shires sit on the 6×6 mesh (a round trip costs 150 + 12 cycles per hop, 20 ns per hop at any clock); TensorSend/Recv, credits, barriers, reduction trees and rings: cycles per message, a 2.3 µs chip-wide allreduce, 7–34× less bandwidth between shires than inside one, and pJ per byte (re-measured in the energy manual §5).'
   • Matmul efficiency, what → 'A tensor-unit matmul loop on cached tiles, all 1,024 minions: 9.5 TFLOP/s fp32, 19.0 fp16 and 71.8 TOP/s int8 (91–97% of peak), board power under load and a spec-sheet comparison with the A100; also the first hello world. Its operands are ±1 and ±2; the Horace experiment later showed that random data draws more power. (The scalar SGEMM is in Test drive.)'
   • Sparse compute, what → 'What the tensor unit does with zeros: zero-skip saves power (86% in a TensorFMA loop on small integers) but never a cycle; masked loads and skipped empty slices take a batch-1 1024×4096 fp32 layer held in SRAM from 7.5 to 2.1 µs at 99% zeros; narrow lanes against divergence; six scenarios where the chip could beat an A100. Its power result is the one the Horace experiment later resolved into flips.' Instruments → 'cycle counter, board power polled through dev_mngt_service'.
   • Test drive: date → '18 Sep'. What → 'First contact: the toolchain built on a Mac, hello worlds on the sys_emu simulator, a scalar fp32 SGEMM on aifoundry3's card (127 GFLOP/s on 2,048 harts, no SIMD or tensor unit), and three upstream issues found on the way.' Instruments → 'host wall clock (kernelLaunch → waitForStream)'.
   • Spatial temperature: title → 'Spatial temperature: a brief'. What → 'The 35 Moortec temperature sensors on the 6×6 grid of minion, I/O and PCIe shires, the firmware's reduction to one whole-degree average, and the firmware changes a spatial heat map would need.'
   • Ridge points: keep date '18 Sep'.

   Related list: mirror these descriptions, and also:
   - Power and temperature: 'the card's thermal time constants' → 'the 34-shire voltage map';
   - Anatomy: 'the mesh's coordinates' → 'the memory shires' positions on the mesh';
   - Heat per millimetre: 'and why a one costs more than a flip' → 'and why ones cost energy even when they do not change from flit to flit'.

11. **[medium] hub-16, horace-28, hub-dvfs-1, hub-e10-850, nl-2, fr-16, hub-1 (lowpower), nav-05** — *data.json sessions row E10 (~line 929)*

   what → 'Cool-start runs: the governor stepping the clock among 600, 700 and 800 MHz (0.52, 0.57 and 0.62 V), re-read for the DVFS report'.

12. **[medium] nav-05, hub-25, fr-2, hub-26, hub-dvfs-1** — *data.json sessions[]; script.js sessions renderer; body.html §7 intro*

   1. Intro → 'Every registered session (E1 onward) that measured power or temperature, in order, with the report that uses it; the 18 September reports predate the register and are summarised in one row. The IDs are those of the experiment register, <a href='https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/docs/findings/03-experiments.md'>docs/findings/03-experiments.md</a>.'
   2. New first row. id '—'; when '18 Sep'; card 'aifoundry2; aifoundry3 for sparsity'; what 'Before the register: matmul power, energy per byte by memory level and by message ring, tensor-unit power against sparsity (board power polled through dev_mngt_service)'; data 2026-09-18-aifoundry2/, 2026-09-18-memhier-aifoundry2/, 2026-09-18-nocbench-aifoundry2/, 2026-09-18-sparsity-aifoundry3/; reports Matmul efficiency, Memory hierarchy, On-chip communication, Sparse compute.
   3. New row before E5. id 'E1'; when '19 Sep'; card 'aifoundry2'; what 'One memory access by stage and by rail: 46 pJ per L1 load to 5.1 nJ per DRAM load, from the SP's rail trace (re-measured in the energy manual)'; instruments 'cycle counter, SP stats trace'; data docs/reports/data/2026-09-19-memprobe-aifoundry2/; report Anatomy of a memory access.
   4. E7–E9 what → 'The Horace experiment in three versions: E7 uncontrolled (79–90 °C), E8 every run started at 80 °C, E9 strict (14 patterns, 46 runs); zeros 38 W, ones 47 W, random 63 W'. Data: 2026-09-20-power-aifoundry2/ (horace-*, horace2-*: E7, E8) and 2026-09-21-horace-aifoundry2/strict/ (E9).
   5. E26–E28 data: add 2026-09-23-enercat-aifoundry2/ and 2026-09-23-enercat-aifoundry3/ (E26), and list catalogue-aifoundry2/, catalogue-aifoundry3/ and catalogue-aifoundry2-rows/ as separate full paths.
   6. 'when' (UTC−7): E22/E23 → '22 Sep, 13:16–13:22'; E25 → '22 Sep, 15:52–15:59'; E26–E28 → '23 Sep, 07:48–11:21'.
   7. Store data as a list of {path, note}. Render each entry as <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/<path>'><code>path</code></a> followed by the note in parentheses, joined with <br>. Write E10's data as two full paths (…/cold1/ and …/cold2/).
   8. Replace the single report/url with reports: [{title, url}], one link each.
   - E20/E21: The Horace experiment → …et-soc1-horace-experiment#a-second-card-and-what-transfers; The DVFS loop → …et-soc1-dvfs-leakage#the-same-firmware-on-three-cards.
   - E30: 'This page, §4' → url '#power'.
   - E6: as in the voltage-map change above.

13. **[medium] hub-17, dvfs-fw** — *meta.json / body.html byline, lede, before §1, end of §1, §8*

   Byline → '24 September 2026 (first published 20 September; versions in §8) · aifoundry2 and aifoundry3 · firmware source read at et-platform 353f20e (the cards' own log strings point to an older build; see the DVFS report §8), RTL core-et b38a1a3 · the index of every ET-SoC-1 measurement report'.
   Move the edition list into a §8 bullet 'Versions: …'.
   Split the lede into one question sentence plus four bullets (time, state, energy, bit flips), keeping the lede texts from the three lede changes above.
   Insert before §1: <p class='card'><b>Start here.</b> §1 lists every report and what it found. For energy per instruction or byte, go to the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual'>energy manual</a>; for what a power number can and cannot mean, read §4 here; the chip's vocabulary is in the box above.</p>

14. **[medium] nav-07** — *body.html §3, last paragraph (~line 78)*

   Replace 'The one place joules have been attached to flips is the tensor unit, by fitting four event energies to board power (the Horace experiment).' with:
   'Joules have been attached to flips in two places, both by fitting to measured power: the tensor unit, with four event energies (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment'>the Horace experiment</a>), and the mesh links, where a bit that differs from the previous flit costs about 98 fJ per hop and a one carried about 129 fJ on the mesh rail (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm#ones'>Heat per millimetre, §5</a>).'

15. **[medium] hub-6** — *script.js fittext; body.html §4.2 intro*

   fittext → 'Four coefficients, no intercept, fitted per card to the mean of each configuration's three passes (392 configurations on aifoundry2, which also ran six DRAM-row configurations, 386 on aifoundry3), on bursts of 0.8 to 26 W over idle. DRAM bytes are the bytes of the DRAM load, store and row configurations, streaming stores counted once. The minion coefficient is pinned to 1.5% on each card but differs by 10% between them, about the cards' spread elsewhere in the manual; the DRAM one differs by 7%. The SRAM and NoC coefficients are collinear with the minion one and uncertain to 7–33%.'
   §4.2 intro: '386 configurations' → '386 configurations (392 on aifoundry2)'.

16. **[medium] hub-7** — *data.json ladder row 'Energy per event', note*

   Replace the last sentence ('A single event is 10¹² times below the floor.') with 'One L1 load (≈50 pJ) is a million times below the floor and one DRAM line (≈8 nJ) ten thousand times; a single bit flip (~10⁻¹⁶ J) is 10¹² times below it.'

17. **[medium] hub-10** — *data.json ladder check fields; script.js CHECK legend; body.html §2 intro*

   Kernel trace buffer: check → 'disputed'; append to its note 'Stamps come from the neighbourhood's even- or odd-hart hpmcounter3, each reset separately at boot, so they compare only between harts sharing a counter.'
   Board power, Rail power, Energy per event, Cycle counter and Chosen counter events were rewritten after the 20 September review. Give them a new check value 'changed', rendered '†' with title 'rewritten after review'.
   Intro → '… rows added or rewritten after 20 September are unreviewed (· or †).'

18. **[medium] hub-11** — *body.html §8 Method, first bullet; script.js CHECK legend*

   Once the owner confirms (open question 3), replace with: 'Seven AI research agents each surveyed one layer: the manuals (external/et-man), the firmware at the card's commit, the RTL and DV trees, the installed tools in /opt/et, the GPU literature, the debug path, and the earlier reports. Each key claim was then given to two further AI agents told to refute it, one checking citations and one checking whether it would work from a user account on this card; 40 of the 73 verdicts corrected the claim as first stated. The ladder folds in their corrections; a person has not re-checked each row.'
   Legend → 'confirmed by two reviewing agents'.

19. **[medium] hub-18, nav-04, kanter-1, kanter-privacy** — *data.json related[] (~1098–1100)*

   Depends on open question 1.
   Default (option A): delete the related entry titled David Kanter's power brief.
   Option B (redacted republish): retitle it 'Notes from a conversation with David Kanter (20 Sep)', with text 'the six claims about DVFS loops and leakage that the DVFS report checks', and list it in §1's Briefs group.

20. **[medium] hub-20, nl-24** — *data.json improvements rung 8, 'What changes in the numbers'*

   'the bars on the awake core, the hot line and the DRAM relay go from ±20–30% to a few percent' → 'the widest bars (the hot line's −15/+19%, the remote scratchpad's ±16%) narrow toward the 1–2% pass-to-pass scatter; the awake core and the DRAM relay are already at ±5–7%'.

21. **[medium] hub-m1** — *data.json power.pvt; script.js line ~93; ladder 'Temperature and voltage' what; rung 13 adds*

   Add "pd_active": 35 to power.pvt. Render the process-detector cell as `${V.pd_active} live of ${V.controllers * V.pd_per_controller}`.
   Ladder: '40 process detectors' → '35 process detectors'.
   Rung 13: '40 ring-oscillator process detectors' → '35 ring-oscillator process detectors (one per minion shire and the IO shire)'.

22. **[low] hub-26, nav-30** — *body.html h3 id='related' (~line 135) inside §7*

   Make it <h2 id='related'>9. Related reports</h2> and move it after §8, so it appears in the contents.
   Intro → 'The reports behind the sessions above, each with what to read it for; the full index is §1.'
   Use each report's own h1 title. Keep the Anatomy entry (E1 is now in the table). Handle the Kanter entry as in the Kanter change above.
   Link docs/findings/ and the repository to GitHub.

23. **[low] horace-28** — *data.json improvements rung 6 (~749)*

   'fitting the heating that reproduces the steps gives ±0.03 °C (the Horace experiment)' → 'fitting the heating that reproduces the steps gives rises that repeat to ±0.03 °C for a pattern heating the die by a degree or more (the Horace experiment); below half a degree it only bounds the rise'.

24. **[low] anat-2, anat-6** — *data.json ladder rows 'Timed single access' and 'Cycle counter'*

   'to ±3 cycles' → 'to ±3 cycles for 97% of lines'.
   'fixcyc() repairs it.' → 'fixcyc() repairs host-corrected pairs; inside a kernel ~1.4% of timed intervals are still ±128 off, so reject those.'

25. **[low] hub-21** — *data.json rungs 16 and 18, group order; body.html §3 last paragraph*

   Rung 18 what → 'Verilator flow for the whole core-et bench'. Adds → 'Every flop every cycle of eight minions. Two single-unit benches already run: rtl-sim/pmu_carry explained the counter's carry bug, and rtl-sim/fma_toggle counts the multiply-add flips behind the Horace experiment.' Cost → 'days of build repair'.
   Rung 16 cost → 'written and verified in sys_emu (patches/0003); a signed firmware image'.
   Move the 'tooling against existing interfaces' group before 'firmware', or name it in the intro.
   §3: after 'the Horace experiment' add '; its flip counts come from rtl-sim/fma_toggle, the core's multiply-add RTL under Verilator'.

26. **[low] hub-22** — *data.json ladder sec fields; body.html under #gran*

   sec values: Shire-cache counters 3e-7; Fixed core counters null (table only); Rail power 1; Energy per event 3; Every flop every cycle null.
   Add a caption under #gran: 'Each dot is the finest time step the instrument resolves on the card; colour is what it takes to use it.'
   'coarsest to finest' → 'roughly coarsest to finest'.

27. **[low] hub-23** — *data.json §6 table 'Cycle timer' row and Sources; body.html below §6*

   GPU cell → 'clock64() per SM, 1 cycle; %globaltimer counts in 32 ns steps but updates about once a microsecond (NVIDIA forum; the PTX manual gives no resolution)'. Source → 'CUDA Programming Guide; NVIDIA developer forum'.
   Add a 'Sources' list under §6 giving full titles and links for Jia et al. 2018, Luo et al. 2024, Yang et al. SC'24, Lin et al. 2025, Khairy et al. 2020 (Accel-Sim, ISCA 2020) and GPUHammer. The URLs are in docs/reports/sources/2026-09-20-limits-of-observability/survey-findings.txt.

28. **[low] hub-27** — *data.json improvements rung 10*

   Adds → 'aifoundry3 repeats the catalogue, the reruns and the Horace protocol (not the DRAM-row runs).'
   Effect → 'The card factor: 0.95 over the catalogue (10–90%: 0.91–0.99); on the tensor unit's flip energies alone, 0.92 (the Horace experiment); bars that are mostly the card, not the day.'

29. **[low] hub-28** — *body.html §4.1 end of first paragraph; data.json ladder 'Rail power' note*

   '… have set-point registers in the PMIC and no telemetry at all' → '… have set-point registers in the PMIC and no current or power telemetry (their on-die voltages are reported, §4.3)'.
   Ladder: 'and no telemetry' → 'and no current or power telemetry'.

30. **[low] hub-29, fr-8** — *body.html §8 Method, second bullet*

   If the energy-manual group commits tools/ettelem/fit_unmetered.py: '… are in unmetered_fit.json, written by tools/ettelem/fit_unmetered.py from catalogue.json and the catalogue telemetry.'
   Otherwise: '… are in unmetered_fit.json; the fit was run inline and no committed script reproduces it yet.'

31. **[low] hub-30, nl-21** — *various (data.json notes, body.html, script.js PVT table)*

   'Other rails leak in at 0.03 mV per board watt' → '0.025 mV'.
   '35 live (5 controllers × 8)' → '35 live of 40 (5 controllers × 8)'.
   'The same sampler' → 'The master minion's statistics worker (MMST trace)'.
   Idle-table header → 'Idle at 73 °C after about 20.5 h, mean of 300 samples over 60 s (± sd)'.
   Method: 'Nothing here changed the card.' → 'Nothing done for this survey changed the card's firmware or configuration.'
   Lede: 'single modules of the original RTL' → 'single modules of the open core RTL (Erbium, a later chip of the same Minion core lineage; §8)'.
   First '6×6 mesh' mention → '6×6 grid of minion, IO and PCIe shires (8×6 counting the memory shires at the sides)'.

32. **[low] sp-2** — *data.json improvements rung 12 effect (~811)*

   'Heat maps at 0.06 °C on the 6×6 mesh' → 'Heat maps on the 6×6 mesh (0.06 °C only if the raw 12-bit codes are exported; the driver's own values are whole degrees)'.

33. **[low] nav-13, nav-11** — *meta.json title; rebuild*

   Title → 'Limits of observability · ET-SoC-1 reports hub'.
   Rebuild with scripts/build-report.py limits-of-observability, redeploy, check visibility.
   Add the anchor fragments above only once their target pages have been rebuilt.

### 3.3 et-soc1-energy-manual

Files: `docs/reports/sources/energy-manual.body.html`; `docs/reports/sources/energy-manual.script.js`; `docs/reports/sources/energy-manual.meta.json`; `tools/ettelem/build_energy_manual.py`; `tools/ettelem/render_energy_manual.py`; `tools/ettelem/render_catalogue.py`; `tools/ettelem/fit_unmetered.py (new, if reconstructed)`; `docs/energy-manual/*.md (README, 00, 02, 03, 04, 04a, 05, 07, 08, 09)`; `docs/reports/data/2026-09-23-energy-manual/manual.json (regenerated)`; `docs/reports/2026-09-23-energy-manual.html (rebuilt)`

1. **[high] em-1** — *script.js §4.3 '32 B loads through the L1' table (line ~299) and linetext (lines ~304–306)*

   Units bug: the table and text treat pJ per byte as pJ per load.
   Table: use cb(r[2]+'/zeros',32) and cb(r[2]+'/random',32), so the columns really are pJ per load (130.7, 193.1 / 181.0, 295.6 / 179.1, 295.6).
   Text: multiply by 32 (fillz = 2*32*(c64z.mean − c32z.mean), and the same for fillr and per()), and print per-byte values with toFixed(2). The sentence becomes: '…costs: 101 pJ on zeros, 205 pJ on random data (a2 211, a3 199) — 1.6 and 3.2 pJ per byte of line, about three quarters of the 2.0 and 4.2 pJ/B a tensor load pays for the same bytes from the same scratchpad. What random data adds over zeros is about 104 pJ for the fill's 512 bits, 204 fJ per bit on the path from the shire cache into the L1.'

2. **[high] em-3, man-rings-1, vnav-m2, nl-8** — *script.js commtext (line ~164); render_energy_manual.py line ~243; docs/energy-manual/05-bytes-between-cores.md line ~31; §5 ring table*

   Replace 'Inside a neighbourhood a byte costs under a picojoule; inside a shire about 2.1 pJ; across the mesh 12–18 pJ, roughly flat in distance. The step is leaving the shire, not the hops after that.' with:
   'Between the two minions of a pair a byte costs under a picojoule; around a neighbourhood or a shire about 2.1 pJ; across the mesh 12–18 pJ: about 9 pJ to leave the shire plus 1.7 pJ per mesh hop (a straight line through the six mesh rings against their mean hop distances of 1.6–4.7 on the shire map of <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>On-chip communication</a>, r² 0.95; <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm'>Heat per millimetre</a> measures 1.5–2.2 pJ/B per hop directly). Leaving the shire is the biggest single step, but the hops after it are not free.'
   Ring table: add a 'mean mesh hops' column (pair, neigh, shire 0; xshire8 1.6; xshire16 2.1; xshire1 3.5; xshire4 3.7; xshire2 4.5; xshire6 4.7; xshire1-c4 3.5) and sort the mesh rows by it.

3. **[high] em-4, em-1 (ridge-matmul), em-nm-1, nl-7, nl-14** — *script.js memcap (~131), 'Reads by level' caption (~144) and summary (~145); render_energy_manual.py ~196/~211; docs/energy-manual/04-bytes-memory.md ~21; build_energy_manual.py label recheck_600mhz.tload_scp_local*

   Caption:
   'L1: both harts of every minion re-reading a private 256 B buffer with 32 B vector loads, in memhier's own loop over a buffer whose contents it does not set; it reads 40% above the catalogue's L1 row in section 4 (0.54 pJ/B on random data), which is the figure to use. L2, L3, DRAM and the scratchpads: hart 0 of every minion streaming 1 KB tensor loads — which skip the L1 but are cached in the L2 and L3 — over a working set sized to each level. The probe does not set the memory's contents, so these rows sit between the zeros and random columns above and are not directly comparable to them. 3 passes on each card at a pinned 600 MHz (n = 6).'
   In the superseded-run note, 'the clock sat at 0.67–0.77 GHz on the larger sets' → 'its clock averaged 0.62–0.74 GHz across the levels'.
   Summary → 'Reads by level: the L1 by vector loads; the L2, L3, DRAM and scratchpads by 1 KB tensor loads (memhier, re-run at 600 MHz on both cards)'.
   memcap: 'Tensor loads and stores bypass the caches' → 'Tensor loads skip the L1 (the L2 and L3 cache them when the working set fits); tensor stores skip the L1 and L2'.
   Mirror all of this in render_energy_manual.py and 04-bytes-memory.md.
   build_energy_manual.py: relabel recheck_600mhz.tload_scp_local 'tensor load, L2 cache'.

4. **[high] em-5, em-1 (anatomy-testdrive missed)** — *body.html after the §2 table (~line 34); script.js line ~101 and awake-table rows (~63–73); body.html line ~121; render_energy_manual.py ~107/~138; docs/energy-manual/02-awake.md*

   Add under the §2 table:
   <p class='small'>The addi loop is not the floor: it increments seven registers, so its operands change on every instruction. With both harts a nop costs 5.3 pJ [4.7–5.9] and a fence 4.5 [4.3–4.8] per instruction (3.1), so the awake core is about 4.5–5.3 pJ per issue slot. The ablation in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power'>Why is the ET-SoC-1 low power?</a>, whose loop issued at half this rate on hart 0, measured 1.46 W (1.4 mW per minion, 8.1 pJ per instruction).</p>
   Awake table: add, before the hot-line row, <tr><td>The 21 September ablation's integer loop (4 adds and a branch), hart 0, 80 °C</td><td class='num'>8.1</td><td class='num small'>a2 only</td><td class='num'>1.46</td><td class='num'>1.43 mW</td></tr>.
   script ~101 → 'An integer add costs 5.7 pJ on zeros [5.2–6.4], barely more than a nop (5.3) or a fence (4.5): on zeros it is almost all the awake core.'
   body ~121 → '“Per instruction” includes the awake core that issued it (4.5–5.3 pJ per slot with both harts, what a fence or a nop costs).'
   Mirror in render_energy_manual.py, where 02-awake.md says 'a stalled one costs the same' (see the markdown-edition change).

5. **[high] em-2** — *script.js alltext (line ~272)*

   'Within a class the instructions cost the same to within a few percent — the energy is the unit's, not the opcode's — and the classes differ by an order of magnitude.' → 'Instructions that share a unit and a latency cost about the same on zeros — the 28 one-cycle integer ops span 5.3–6.4 pJ — but data and latency spread every class: on random data the same 28 span 5.4–10.2 pJ, a 64-bit divide costs 5× a mulw, and a global amoaddg 4× a local amoaddl. Across the catalogue the span is 310×.'

6. **[high] em-6** — *body.html after the $$E(…)$$ line; §6 and §4.3 first uses*

   Insert <div class='card small' id='terms'> holding glossary G (decisions), trimmed to: minion, hart, neighbourhood, shire and its SRAM split, scratchpad and L1 scratchpad, TensorFMA, mesh and memory shires, SP, PMIC and the three rails, and 'aifoundry2 and aifoundry3 (a2, a3) are the lab machines holding the two cards'. End it with a link to the hub's glossary (#terms).
   On first use, expand FLB (fast local barrier) and TensorReduce (the hardware reduction tree) in §6, and flit in §4.3.

7. **[medium] em-9, nl-23, nl-10, nar-16, nar-m3** — *script.js §7 comp (line ~187) and compcap (~196); docs/energy-manual/07-composition.md §7.1*

   Multiply-add segment: use the flip model's prediction, D.cards.patterns.find(p => p.values === 'randn').model − sm, which is 25.3 W.
   Label → 'predicted 63.1 W (fixed + leakage + the flip model's 27.2 W); measured 63.9 W'.
   Caption: compute from the measured total (t.idle_w + t.over_idle_w) and tb.mean/2 → 'Per flop that is 7.0 pJ loaded and 2.89 pJ marginal [2.62–3.01 over runs and cards]'.
   07-composition.md §7.1:
   - multiply-add row → 'Multiply-adds: 25.3 W, the flip model's 27.2 W less the state machines';
   - 'Measured (E9, p80 of randn)' → 'Measured (E15 ablation, fp32 random)';
   - call the table a decomposition checked against a measurement, not a prediction.

8. **[medium] em-7** — *script.js instrtext (~104–105); render_energy_manual.py ~141*

   After '…the tensor unit does the same multiply-add for 5.8 [5.2–6.0].', replace the rest with: 'Take out the vector instruction's issue — 4.5–5.3 pJ, what a fence or a nop costs (section 2) — and the lane is 6.3–6.4 pJ, about 10% above the tensor unit: the datapath energy is close, and what the tensor unit mostly saves is instruction issue.'

9. **[medium] em-8** — *script.js instrtext (~105) and alltext (~270); render_energy_manual.py ~143*

   'Transcendentals are the dearest instructions on the chip: fexp.ps is 159 pJ…' → 'Transcendentals are the dearest arithmetic: fexp.ps is 159 pJ and flog.ps 219 pJ for eight lanes, at a quarter of the rate; only loads and stores that bypass the L1 (290–392 pJ) and atomics (340–1,390 pJ) cost more.'
   Line ~270: use the pooled CB[`${n}/random/h2`].mean, giving 'The cheapest instruction is fence at 4.5 pJ and the dearest amoaddg.d at 1,393 pJ, a span of 310×.'

10. **[medium] em-10, nl-22** — *body.html line ~20 (KPI 4); docs/energy-manual/08-cards.md*

   KPI: 'Second card, 392 catalogue entries' → 'Second card, 386 catalogue entries'. Show the value as '0.950 (10–90%: 0.906–0.987)' so it is not read as a min–max bar.
   08-cards.md: 'For the catalogue's 386 shared entries'.

11. **[medium] em-11** — *build_energy_manual.py; script.js line ~37; body.html line ~117 and command block; docs/energy-manual/09-method.md*

   In build_energy_manual.py, add D.catalogue.leak_correction = {card: {median, max}} of |leak_correction_w| over catalogue.json's bursts, and read it at script.js line ~37.
   Text → 'a correction of 0.40 W in the median and 1.80 W at most over aifoundry2's 1,176 bursts (0.16 and 0.78 W over aifoundry3's 1,158)'.
   body ~117: 'with six seconds of idle either side' → 'with 4.5 s of idle either side (the catalogue; the reruns leave 10 s)'.
   Command block: 'run_catalogue.py DATA --passes 3 --burst 3 --gap 4.5   # 386 configurations, ~2.7 h per card' and 'analyze_catalogue.py DATA_A2 DATA_A3 DATA_A2_ROWS --out catalogue.json'.
   Make the same corrections in 09-method.md: the figures, 'six seconds' and 'three and a half hours'.

12. **[medium] em-12, nav-16, em-sec** — *body.html §4 (~lines 64–73); script.js line ~145*

   Insert <h3>4.1 Reads and writes, measured together</h3> before the 'Energy per byte by path' chart title.
   Replace the <details open><summary id='memoldsum'> wrapper (~lines 70–71) with <h3>4.2 Reads by level</h3> followed by the table.
   Delete the memoldsum line in script.js.
   The existing citations of sections 4.1 and 4.2 then resolve.

13. **[medium] em-13** — *body.html after the KPI div; end of script.js*

   Add <nav class='card'><b>Contents</b><ol id='toclist'></ol></nav>.
   Build it the way heat-per-mm.script.js (~173–174) does, but from 'main h2, main h3'. Label entries with the heading text including its section numbers (or strip with /^\d+(\.\d+)*\.?\s*/), indent h3 entries, and run it before the template adds its # anchors.

14. **[medium] em-14, heat-1, nl-8** — *script.js wiretext (~293) and wirecap (~291); render_catalogue.py (04a-fine-grain.md lines ~13–16); docs/energy-manual/README.md row 4.3*

   Keep the 1–8-hop fit. After its first sentence add: 'Fitted over 1–6 hops, leaving out d = 8 where only 16 shires have a partner and the point sits nearly level with d = 6, the same data give 2.29 and 2.09 pJ/B per hop on random data and 174 and 155 fJ per random bit per hop, which is what <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm'>Heat per millimetre</a> measures (2.17 pJ/B per hop on board power, loaded mesh): use its figures for wires.'
   Delete 'It is the one number here the cards agree on to a few percent, because…', keeping the rest of that sentence as '…the 0.75 pJ/B that a hop costs on all-zero data is clocking, arbitration and buffering'.
   Describe the 133 and 129 fJ as 'what random data adds over zeros (flips between flits plus ones carried)', not as toggling.
   wirecap → '1 KB tensor loads from a scratchpad exactly d hops away, all 32 shires reading up to 5 hops (31 at 6 hops, 16 at 8, so the 8-hop point has half the traffic), at most two readers per target.'
   Mirror in render_catalogue.py and the README's 4.3 row.

15. **[medium] em-15, nl-31** — *script.js SRAM caption (~350–357); render_catalogue.py line ~197*

   Caption → 'The rail feeding 128 MB of on-chip SRAM, at idle. Fitted with the idle law's 36 °C e-folding imposed: −0.32 W + 2.81 W·e^((T−80)/36); the negative constant says the rail rises faster than that shape. The whole rail at 80 °C is 2.48 W, 19.4 mW per MB, an upper bound on the arrays' leakage including the cache logic; aifoundry3's rail, fitted the same way, gives 27 mW/MB. At about 20 mW per MB, a byte held in scratchpad for one second leaks about 19 nJ — as much as reading it 4,000 times (4.3 pJ per read).'
   render_catalogue.py: '20929.8 pJ' → 'about 21 nJ'.

16. **[medium] em-16** — *body.html §1 first paragraph (~24–25)*

   'The fixed part — PCIe, the DDR PHY, the IO shire, regulators — does not answer to anything a kernel does.' → 'The fixed part — PCIe, the DDR PHY, the IO shire and the regulators at rest — does not change with temperature. What those blocks spend when a kernel uses them (DRAM traffic through the DDR PHY, the regulators' delivery loss) is counted in the per-event costs below; 4.3 attributes it.'

17. **[medium] em-v1, nar-m2** — *body.html §7 relay note (~105–107); script.js relaycheck rows (~202–208); docs/energy-manual/07-composition.md §7.2*

   Replace the note with: 'The relay reads with 32 B vector loads through the L1 and writes with tensor stores, and its “next shire” is on average 3.5 mesh hops away (shire s−1 by ID). Priced with the matching rows — the L1-fill read of 4.3 and the wire read at 3.5 hops — the brackets are 4.3…7.1 for the own scratchpad (the relay measures 4.0, a little below) and 5.1…11.2 for the next shire (8.6, inside). It is a consistency check to about 10–20%, not a prediction.'
   In script.js, compute the scp and hop rows from l1fill/stride32 and the 3.5-hop wire interpolation, and drop '(a little above: the add and the barrier)'.
   In 07-composition.md §7.2, replace the table with these brackets and the E29 measurements (105.7 [99.5–111.0], 3.99 [3.90–4.25], 8.59 [7.78–9.21]), say that the hop's read side is the wire read of 4.3, and mark §7.3 as a consistency check rather than a prediction.

18. **[medium] em-17** — *docs/energy-manual/README.md, 07-composition.md, 09-method.md, 00-structure.md, 03-instructions.md (through render_energy_manual.py ~120–160)*

   README row 3 → 'integer add 6 pJ on zeros (9 random), float add 23 pJ, 8-lane FMA 27 pJ on zeros and 56 on random data; a tensor multiply-add 0.4 pJ on zeros, 5.8 on random'.
   README row 2 → '2 mW per minion awake on one hart, 3.4 on two; one stalled on a contended atomic draws 1.4 mW'.
   README row 8 → 'the second card reads 0.95× the first in the median (10–90%: 0.91–0.99)'.
   README row 3.1 → 'cheapest fence at 4.5 pJ, dearest amoaddg.d at 1,393 pJ'.
   README Regenerating → 'run_catalogue.py measures (three shuffled passes), analyze_catalogue.py reduces'.
   09-method.md: V²f 1.41× and 1.91×; rails 'the PMIC's ~1 s first-order running averages'; delete the superseded 'Uncertainty, table by table' stub or fold it into 'Confidence bars'.
   03-instructions.md: rename '3.1 Scalar and vector units' to '3.0 Scalar and vector units', or match the HTML numbering.
   00-structure.md line ~18: delete the roofline sentence.

19. **[medium] em-19, nav-16, nl-11, nav-03, nl-19, em-2 (ridge-matmul missed), sparse-5, hl-2, em-1 (anatomy-testdrive missed)** — *body.html §10 Related reports (~146–160) and byline*

   Why low power item → '…an ablation of the dense matmul, term by term of C·V²·f plus leakage, against an A100; the source of the activity-term row of section 2, and of an earlier, slower integer loop (half the addi loop's instruction rate, 1.4 mW per minion).'
   Spatial item → '…how the firmware collapses them to one number, and what a spatial heat map would need.'
   Power and temperature item: 'the card's thermal time constants' → 'the 34-shire voltage map'.
   Add <li><a href='https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation'>L2 mainline starvation</a> — a same-day argument about the shire that hosts a hot line; the measurement is in One hot line stops a shire (section 6).</li>
   Add <li><a href='https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency'>Matmul efficiency</a> and <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute'>Sparse compute</a>: the 18 September tensor-unit rates and the first zero-skip power measurements that section 3.2 re-measures under temperature control.</li>
   Add <li><a href='https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points'>Ridge points</a>: the reuse each memory level demands, with energy balance points built from sections 3.2, 4.2 and 5.</li>
   Link both mentions of docs/energy-manual/ to https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/energy-manual.

20. **[medium] em-v3, reg-m1** — *body.html §9 'Confidence bars' (~137–138); render_energy_manual.py ~294 (08-cards.md 'How the bars split'); 02-awake.md*

   '…which is why the small-signal entries — the awake core, the hot line, the DRAM relay — carry the widest bars.' → '…which is why the smallest signal, the hot line (1.4 W over idle), carries the widest bar, ±17%; the awake core (±4–7%) and the DRAM relay (±5%) come out no wider than the catalogue.'
   02-awake.md: 'The bars here are the widest in the manual in relative terms' → 'The bars here are ±5–7%, about the catalogue's median'.

21. **[low] em-21, nl-25, nl-36, vnav-m4, em-5 (noc-memhier missed)** — *script.js §5 table footnote (~161); render_energy_manual.py ~226*

   '…the 18 September pair of runs, sampled without the die temperature, is not pooled and agrees to within 10%. The s ↔ s+16 ring starves the service processor's own management path — the sampler's latency triples…' → '…the 18 September pair of runs, sampled without the die temperature and so without a leakage correction, is not pooled; it reads 2–20% higher in every configuration (median 10%). The s ↔ s+16 ring starves the service processor's own management path — the sampler's latency rises from 22 ms to 75–150 ms and the board reading is held for seconds…'

22. **[low] em-20** — *script.js lines ~161 and ~180; body.html ~130–132; lede*

   Relay note → 'Relay: 22 September and three warm passes on aifoundry2, four passes on aifoundry3 (n = 8).'
   Hot line → 'Hot line: 22 September and three warm passes on aifoundry2, three passes on aifoundry3 (n = 7).'
   Method → 'the relay and the hot line (5, 6) are their 22 September measurement plus three passes on aifoundry2 with the die held above 76 °C and three or four on aifoundry3; the rings and the levels (4.2, 5) are three new passes on each card'.
   Lede: 'repeated warm passes on both cards' → 'repeated passes on both cards'.

23. **[low] em-18** — *body.html lede*

   → 'Every repeated measurement carries a confidence bar — the mean over every pass on every card and, in brackets, the range those passes spanned: three shuffled passes on each of two cards for the instructions and bytes, repeated passes on both cards for the relay, the hot line, the rings and the levels. Rows measured once, or derived, say so.'

24. **[low] em-30, em-v4** — *body.html lede (~7–8)*

   'A second card gives the same numbers to 5%.' → 'A second card reads about 5% lower (median 0.95; 80% of entries 1–9% lower).'
   'An integer add is 6 pJ, a float add 23, an eight-lane multiply-add 27 on zeros and 56 on random data.' → 'On zeros an integer add is 6 pJ, a float add 23 and an eight-lane multiply-add 27; on random data 9, 26 and 56.'

25. **[low] em-31, nl-31** — *body.html lede; script.js line ~177, pcs() (~25)*

   Lede: 'written back through the L1 to DRAM, 250–350' → '240–330'.
   'the two things it needs alongside them' → 'with the two things it needs alongside them: the idle power at a given temperature (section 1) and the cost of an awake core (section 2)'.
   Barrier row: '≈ 11939 nJ of waiting' → '≈ 12 µJ of waiting'.
   pcs(): print the standard error with one more decimal when it is below 0.05 (for example '5.8 ± 0.03').

26. **[low] em-24, wlp-8, nl-34** — *script.js awake table rows (~71–72); docs/energy-manual/02-awake.md line ~14*

   Activity row → '<tr><td>For scale: every minion running a random-data fp32 matmul (the activity term, section 3.2)</td>…<td>27.6</td><td>27.0 mW (25.6 per minion with 256 or 512 active, 26.2 with 768)</td>'.
   Hot-line row label → '1,024 minions stalled on one contended atomic (the hot line; each waits about 10,000 cycles for its turn)'.
   Make the same change in 02-awake.md.

27. **[low] em-26, hub-3, hub-12** — *script.js railstext (~340); render_catalogue.py lines ~272–274 (04a-fine-grain.md line ~161)*

   script ~340 → '…(rms 0.36 mV over the catalogue): 1 mV ≈ 1.2 W of DRAM, refreshed every 133 ms. It is a proxy calibrated against the fit, not a meter: heavy on-chip traffic moves it too (a scratchpad-read burst droops it 1.7 mV with no DRAM traffic).'
   render_catalogue.py: replace 'it responds to DRAM traffic alone … does not drift' with the hub's §4.3 wording ('responds mostly to DRAM traffic, but not only …, and its idle reading moves by about 1 mV between 71 and 77 °C').
   'the IR drop the spatial temperature brief mapped shire by shire' → 'the Power and temperature report (§3) maps each shire's rails at idle'.

28. **[low] hub-2** — *render_catalogue.py line ~263 (04a-fine-grain.md line ~154)*

   'residual rms, bursts' → 'residual rms, configuration means'.

29. **[low] em-22** — *body.html §9 third bullet (~124); §3 intro (~37–38)*

   → 'Everything is at 600 MHz; the minion rail reads 0.518 V on aifoundry2 and 0.523 V on aifoundry3. Thirteen instructions trap in U-mode (listed in 3.1), among them every float and vector divide and square root.'
   §3: write '0.52 V'.

30. **[low] em-23** — *script.js idle chart caption (~55) and tooltip (~54)*

   Caption → 'Ring: the other card, 13 °C below the coolest fitted bin, 0.6 W above the law.'
   Tooltip: compute the law at 51 °C instead of hard-coding it: 'the aifoundry2 law says 23.0 W'.

31. **[low] em-25** — *script.js §3.2 tensor table*

   Header → 'Tensor unit, one instruction per tile (fp32 16×16×16 = 4,096 MACs; fp16 8,192; int8 16,384), all 1,024 minions, 80 °C'.
   Add to the caption: 'Marginal: board power above idle per MAC. Loaded: total board power, idle included, per MAC — what a MAC costs when it is the only thing running.'
   Print the rate as '4.59 × 10¹²'.
   Caption: 'Bars on the fp32 rows: the envelope of ±1 sd around the ablation's two runs and the transfer's runs on both cards.'

32. **[low] em-v2** — *script.js line ~109*

   '…fp16 and int8 were run twice on aifoundry2, and their bar is ±1 sd of those two runs: under 1% on random data, 1.5% on int8 zeros, 5–6% on the ones patterns.'

33. **[low] em-27** — *script.js §5 and §6 tables (~142, ~159, ~178–179)*

   Drop '(E25)' and link the relay row to https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay.
   'nocbench' → 'On-chip communication, 18 September' (linked).
   Give the relay rows their own header, 'Handing a slab to the next shire'.
   '2 MB of the scratchpad 16 shires away' → '2 MB of the scratchpad 16 shire IDs away (about 2 mesh hops)'.
   '…the per-message overhead is a few hundred cycles of both harts' → '…the per-message overhead is 40–224 cycles of the sending and receiving harts (On-chip communication)'.

34. **[low] em-28** — *script.js commtext last sentence (~164); body.html ~105*

   '…the DRAM relay carries the widest bar of the three because…' → '…the three bars are ±4–8% because each is a 4–5 W signal over a board idle that drifts; the DRAM relay's power also rides on a path with no rail sensor.'
   'The relay of 22 September was not used to build any table' → 'No row of section 4 was derived from the relay, so this is an out-of-sample check'.

35. **[low] em-29** — *script.js instrcap and the 161-bar chart (~259)*

   '…issue at a quarter to an eighth of the rate' → '…issue at 0.4× (frcp.ps) down to an eighth (mul) of the one-cycle rate'.
   Label every bar: font-size 8 rotated −70°, or W = all.length*11.
   Open the <details> table by default, or add under the chart 'Every figure is in the table below, by execution unit.'

36. **[low] em-v5** — *script.js line ~68 (awake table header)*

   Headers → 'W over idle, 1,024 minions (a2)' and 'per minion (a2)', or compute both columns from the pooled mean.

37. **[low] nav-16** — *body.html under the §6 table*

   Add: 'Contended atomics: <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line'>One hot line stops a shire</a>; barriers and trees: <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>On-chip communication</a>.'

38. **[low] hub-29, fr-8** — *tools/ettelem/fit_unmetered.py (new)*

   Depends on open question 5. If approved, commit a script that rebuilds docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json from catalogue.json and the catalogue-aifoundry2, -aifoundry3 and -aifoundry2-rows telemetry. The verifiers' reconstruction: per-configuration means; DRAM bytes = bytes_per_s of configurations with 'dram' in the name except dramrow*/stride8K; no intercept; the droop regression over die_mv.ddr. Check that it reproduces coef 0.1956/0.0498/0.2860/72.906 and rms 0.346 on aifoundry2 before committing.

39. **[low] nl-21, nav-13, nav-11** — *body.html '6×6 mesh' mentions; meta.json title; rebuild*

   '6×6 mesh' → '6×6 grid of compute and I/O tiles (8 × 6 with the memory shires)'.
   Title → 'The energy manual · ET-SoC-1'.
   Regenerate manual.json (build_energy_manual.py) and the markdown (render_energy_manual.py, render_catalogue.py), rebuild with build-report.py, redeploy, check visibility.

### 3.4 et-soc1-horace-experiment

Files: `docs/reports/sources/horace-experiment.body.html`; `docs/reports/sources/horace-experiment.script.js`; `docs/reports/sources/horace-experiment.meta.json`; `tools/ettelem/flip_thermal_model.py`; `tools/ettelem/build_horace_report_data.py`; `tools/ettelem/finish_horace.sh`; `docs/reports/data/2026-09-21-horace-aifoundry2/report.json (regenerated)`; `docs/reports/2026-09-20-horace-experiment.html (rebuilt, folder deploy with GIFs)`

1. **[high] horace-1** — *§7 long-runs table (#long-tbl, script.js L192) and #long-curves (L183); flip_thermal_model.py / build_horace_report_data.py*

   Give every model.per_run record the long-session run number it came from. Match per_run.t0 to long.json t0_ms (constant offset about 30.8 s) in build_horace_report_data.py, or add the number where per_run is built in flip_thermal_model.py.
   Join on it:
   - L183: const pr = M.per_run.find(q => q.session.indexOf('long') >= 0 && q.run === r.run);
   - L192: const p = pr.find(q => q.run === r.run);
   Take 'end °C measured' from D.long (r.T_at['600'] for time-limited runs). Print 'not in the fit' in the model columns when a run has no record.
   Add under the table: 'The first run (zeros, no history before it) and the last two (after the cooling changed) are not in the fit.'

2. **[high] horace-2, nar-3** — *body.html §7 second bullet (L253–254)*

   → <li><b>Fewer minions buy time, far more than in proportion.</b> Removing a quarter of the flips (768 minions) stretches random normal from 19–26 s to 35 s; removing half (512 minions) to 84 s; three quarters (256 minions) to 276 and 315 s, 11 to 16 times as long; on 128 minions it sits at 81 to 82 °C for the whole ten minutes. Near the flip budget of section 8, each watt removed buys more time than the last.</li>

3. **[high] horace-3, horace-30** — *body.html lede L11–13 and §3 L140; script.js KPI L124, L128, L131*

   Lede → '…register bits clocked and nets toggled predict the board power of 14 patterns to <b>0.5 W rms</b>, each predicted by a fit that left it out; six of them had been predicted from the previous day's data before they first ran, to 1.3 W rms.'
   §3: 'The test that matters most is above.' → 'A first test before the fact is above.'
   After '…and by 7.3 W on the pattern that separates them best.' add: 'This comparison was then used to choose the model form, so it is not a clean test of the final model; section 9's structured matrices, priced with the final form before they ran, are.'
   KPIs:
   - L124 → f1(prim.loo_rms)+' W rms';
   - L128 → `${v.median_abs_pct.toFixed(0)}% median`;
   - L131 → `${f1(rms)} W rms`.

4. **[high] horace-4** — *body.html §10 closing paragraph (L417–418)*

   → 'A single random-data matmul on a new card calibrates both, after which the power predictions of sections 3 and 9 apply to it. The heat predictions also need that card's own thermal network, fitted from long runs on it: aifoundry2's does not transfer, since it is one card in one chassis, and aifoundry3 sheds heat visibly faster.' Delete the following sentence, 'What does not transfer is the thermal network…'.

5. **[high] horace-5, horace-16** — *body.html §8 L343–344; §10 L393 and L394–396*

   L343–344 → 'The budget belongs to this card, this desktop chassis and that day's room. The model's ambient is 22.8 °C, and every degree warmer takes 0.68 W off the budget. On 22 September the same card, idle for about 20 hours, sat at 73 °C instead of 62 °C. By these equations that is a room about 3.5 °C warmer, or airflow worse by the same measure, and a budget of 0.3 to 0.7 W. The flip energies and the leakage belong to the chip design, up to the per-card scale of section 10.'
   L393: 'it idles 25 °C cooler' → 'it idles at 51 °C (aifoundry2: 62 °C after a cool night, 73 °C after 20 hours on 22 September), too cool to hold at 80 °C between runs, so its runs launch at 55 °C'.
   L394–396 → 'Running the same strict protocol on it is the strongest out-of-sample test of the power model: different silicon, different heatsink…'.

6. **[medium] horace-8, horace-v1, horace-18** — *body.html lede (L9–10, L13–14) and §1 (L48–50); script.js zeros KPI (L121), perflop chart (L47–50) and #tbl (L52)*

   Lede → '…and heats the die in proportion to the watts above idle (12 and 30 W): <b>27 and 76 thousandths of a degree per trillion FLOPs</b> on ones and random values, while on zeros (2 W above idle) the rise stays below what the whole-degree sensor resolves (about 5 by the thermal network).'
   Lede L13–14: '…to about <b>0.3 °C</b>, the resolution of the sensor' → '…to about <b>0.3 °C</b> rms, which is what the sensor's rounding to whole degrees alone would leave'.
   §1 L48–50 → 'Averaged over the run, including the leakage its own heating adds, zeros add 2.0 W to that; the reading never leaves 81 °C, so the rise is only bounded (below about 0.5 °C; the thermal network driven by the measured power puts it at 0.3 °C, about 5 m°C per 10¹² FLOPs). Ones add 11.6 W: 27 m°C. Random normal adds 30.4 W: 76 m°C. (At the launch temperature the three add 2.0, 10.5 and 27.1 W.)'
   Zeros KPI sub → '< 0.5 °C in 7 s: below the sensor's resolution'.
   In the perflop chart and #tbl, print '< 7' for zeros, checkerboard and 75% zeros, or draw those bars hatched.

7. **[medium] horace-6, nar-m1** — *body.html §9 first bullet (L358)*

   'eleven of the fourteen to within 0.6 W' → 'ten of the fourteen to within 0.6 W (eleven within 0.8 W)'.

8. **[medium] horace-7** — *body.html §10 leakage paragraph (L409–411)*

   → 'The idle law, fitted here to idle readings from 64 to 88 °C (it also passes through the 62 °C overnight point) and extrapolated 7 to 14 °C below that onto the other card, which idled at 50 to 57 °C, predicts that card's idle power to <span id='leakoff'></span> out of 25 W.'

9. **[medium] horace-9** — *body.html lede L9–11; §3 L91*

   'because the RTL of its multiply-add unit is open' → 'because the RTL of its core family's multiply-add unit is open'.
   'Simulating the chip's own multiply-add RTL on the operands the card ran' → 'Simulating that RTL (core-et's Erbium branch: the same Minion core lineage in a later configuration, not the taped-out netlist) on the operands the card ran'.
   §3: after '(<code>core-et</code>)' insert ', Erbium branch at b38a1a3,'.

10. **[medium] horace-10, nl-12** — *body.html §2 L63–64; §8 L296*

   §2 → 'about 0.8 W per °C on the board while a hot pattern runs, measured from the drift of power within the hot 7 s runs (80–86 °C); the idle law's slope is 0.65 W/°C at 80 °C (section 8) (leakage)'.
   §8: after 'Each degree adds 0.65 W' insert ' at 80 °C (the slope of the idle law; sections 2 and 4 use 0.81 W per degree, the drift of busy power inside the hot 7 s runs. They are different measurements and differ by a quarter)'.

11. **[medium] horace-11, nav-11, nav-20, nav-12, sparse-5** — *whole page: rebuild; section references; 'brief' link (L394); lede; end of page*

   Rebuild with the current template: this gives heading ids and, through the shared template change, a contents list.
   Turn the ~24 in-text 'section N' references into <a href='#…'> links.
   'for a reason worth its own <a …>brief</a>' → 'because its firmware reports a TDP of 0 W, so the governor can only step down (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage#the-same-firmware-on-three-cards'>The ET-SoC-1's DVFS loop, and the leakage</a>)'.
   In §2, link 'about 0.8 W per °C' to https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature.
   Add to the lede: 'It follows the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute'>sparse compute report</a>, which found that zeros save the tensor unit power but never cycles.'
   Before Method add <h2 id='related'>Related reports</h2><ul> with:
   - Why is the ET-SoC-1 low power? (#ablations): this model splits the card's watts term by term
   - Sparse compute: the first sign, 18 Sep on aifoundry3, power falling from 17.3 to 2.4 W over idle as A goes to zeros
   - The energy manual §3.2 and §1: the event energies and the idle law as tables
   - The DVFS loop, and the leakage: the governor behind §6, aifoundry3's TDP
   - Power and temperature: the telemetry client and first thermal measurements
   - ← All ET-SoC-1 measurement reports
   Close with </ul>.

12. **[medium] horace-12, nav-20, nav-13** — *body.html byline (L3), lede (L5–19), §6 opening (L209–210), h1, Method end; meta.json title and description*

   Byline → '20–22 September 2026 · aifoundry2 and aifoundry3 · fp32 TensorFMA on all 1,024 minions · workloads/sparsity, tools/ettelem, rtl-sim/fma_toggle · part of the ET-SoC-1 measurement reports'.
   Lede: split into three paragraphs, breaking before 'Simulating…' and before 'Run for minutes…'. End it with 'On a second card the power model is off by a single factor, 0.92, which one calibration run recovers; the thermal network does not transfer.'
   §6: delete the first two sentences and start at 'The service processor runs a governor…'.
   Method: add at the end 'Versions: 20 Sep: uncontrolled and 80 °C-start runs, which said the clock never moves (corrected in section 6). 21 Sep: strict protocol, RTL model, cool starts, long runs, structured matrices. 22 Sep: second card.'
   h1 → 'The Horace experiment: the same matmul draws 38 to 63 W depending on the data'.
   meta title → 'The Horace experiment · ET-SoC-1'.
   meta description → 'Same matmul, same FLOPs: 38 W on zeros, 47 W on ones, 63 W on random data. RTL switching counts predict the power to 0.5 W rms; a flips-to-temperature model predicts the time from 80 to 90 °C of held-out runs to 9% in the median; 14 structured matrices were priced before they ran (0.9 W rms); one scale factor carries the power model to a second card; and from a cool die predictable data runs 25% faster.'

13. **[medium] horace-13** — *script.js L262 (structured table); body.html after that table; note under #tbl*

   Header 'rise in 7 s, °C' → 'end reading − launch, °C (whole degrees)', or drop the column.
   Add after the table: 'The last column is the raw whole-degree reading, not de-quantised like section 1's rises; differences under a degree are not resolved.'
   Under #tbl: 'Rises below about 0.5 °C (the three coolest patterns) are not resolved by the whole-degree sensor; see section 4.'

14. **[medium] horace-14** — *body.html lede L15–16; §7 L249*

   Lede → '<b>Run for minutes instead of seconds, only zeros hold a steady temperature at full load:</b>'.
   §7 → '<b>At full load only zeros hold a steady temperature.</b>'

15. **[medium] horace-15** — *body.html §1 L33, §6, Method, lede; script.js L171, L191, L207; body L241*

   §1 → 'All 1,024 minions (the chip's compute cores, 32 to a shire; the chip has 1,088 in 34 shires, and the two not used here are the master and spare shires) each run one 16×16×16 fp32 <code>TensorFMA</code> (the tensor unit's matrix multiply-add) over and over, on operands held in the L1 scratchpad (3 KB of each minion's 4 KB data cache).'
   Method: 'hart 0' → 'hart 0 (the first of each minion's two hardware threads)'.
   Lede: 'the RTL' → 'the RTL (the Verilog source)'.
   §6: 'The service processor runs a governor' → 'The service processor (the chip's on-die management core, which runs the power-management firmware) runs a governor'; 'the TDP level (65 W)' → 'the TDP level (the firmware's board power limit, 65 W)'.
   Say 'minions' in §7 too: script L171 ', ${r.minions} of 1,024 minions'; L191/L207 header 'active minions'; body L241 '384 of the 1,024 minions'; and the §7 bullets.

16. **[medium] fr-7** — *tools/ettelem/finish_horace.sh, before the 'scripts/build-report.py horace-experiment' line*

   Insert: python3 tools/ettelem/build_cards_data.py --cards docs/reports/data/2026-09-22-horace-aifoundry3/cards.json --transfer docs/reports/data/2026-09-22-horace-aifoundry3/transfer.json --leak docs/reports/data/2026-09-22-horace-aifoundry3/leakage_crosscard.json --config docs/reports/data/2026-09-22-cards/config.json --driver docs/reports/data/2026-09-22-cards/driver_config.json --sptrace docs/reports/data/2026-09-22-cards/sptrace-aifoundry3.bin --out docs/reports/data/2026-09-22-cards/cards-report.json --merge docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json "$D/report.json"
   Without it, a rerun silently drops section 10's chart, because the script opens with const C=D.cards;if(!C)return.

17. **[low] horace-17** — *body.html §9 L371*

   → 'Six of the structured matrices, with ones and random normal as references, then ran as long runs in a separate afternoon session… (The ones run opened the session, so the observer had fewer than three minutes of telemetry before it; it is not in the table.)'

18. **[low] horace-19** — *body.html §8 L288; under §3 #coef*

   L288 → 'The flip energies are close to section 3's, which used only seconds 1 to 3 of 46 short runs: 3.18 against 2.96 fJ per register bit and 0.80 against 0.78 fJ per other toggle; the operand-word energy is the loosest (15.5 against 12.5 fJ). These are the values the predictor and the energy manual use.'
   Under #coef add: 'Section 8 refits these on five hours of data; use its values for prediction.'

19. **[low] horace-v2** — *body.html §3 L129*

   → '2.47 million register bits clocked per op at 2.96 fJ each is 8.2 W; ones measure 8.4 W over zeros.'

20. **[low] horace-20** — *script.js L30, L83, L92, L228, L177, L284–285*

   Add y-axis labels:
   - L30: yl: key==='curve_T' ? 'die temperature, °C' : 'board power, W'
   - L83: yl 'die temperature, °C'
   - L92: yl 'rise since launch, °C'
   - L228: yl 'die temperature, °C'
   L177: add an <i> swatch per group (as cl-leg does) and give π its own colour (e.g. var(--c5)) in LCOL/COL.
   L284–285: label bars with SHORT[p.values], where SHORT = {zeros:'zeros', sparse50:'50% zeroed', ones:'ones', pi:'π', signs:'random sign', mant:'random mantissa', uniform:'uniform', randn:'normal'}.

21. **[low] horace-21** — *body.html §8 model table (L274–284) and L319*

   Split the table in two: 'Flip energies e_j' (kind, value, per) and 'Thermal stages' (τ_k, R_k in °C/W, summing to 1.47).
   L319 → '…but the slow resistance moves between stages: 0.60 → 0.86 °C/W at 400 s, 0.38 → 0 at 1,000 s and 0 → 0.08 at 2,500 s (the table lists only the stages the full fit kept)…'

22. **[low] horace-22** — *body.html after the §9 predict_heat <pre>*

   Add <p class='small'>The tool starts from a die at exactly 80.0 °C with a generic idle history. The protocol's runs launch at about 80.9 °C in the sensor's units, just after a pre-heat. Started at 80.9 °C the tool says 22 s, the launch-state prediction in the table above says 20 s, and the run took 19 s. Its 63.1 W is at 80 °C; the structured table's 63.7 W is at the 81 °C launch temperature.</p>

23. **[low] horace-23** — *body.html §11 Method, raw-data note and command block*

   Append: 'Section 10: <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-09-22-horace-aifoundry3'>docs/reports/data/2026-09-22-horace-aifoundry3/</a> (runs, starts, telemetry, tiles; cards.json, transfer.json, leakage_crosscard.json).'
   Add the E20 commands: tools/ettelem/run_horace_strict.sh build/strict3 55 60 2 3 1 7 "zeros ones pi sparse50 uniform randn" "signs mant" (on aifoundry3), and python3 tools/ettelem/compare_cards.py --card aifoundry2=… --card aifoundry3=… --model …/model.json --toggles … --out cards.json.

24. **[low] horace-24** — *body.html §4 L177*

   → 'For the three coolest patterns (2 to 5 W over idle) the reading moves by at most one whole degree during a run (one 75%-zero run read 82 °C from 6.8 s on).'

25. **[low] horace-25** — *body.html §1 L50–51, L58–59*

   'The ratio of the last two, 2.8, is the ratio of the added watts, 2.6, within the sensor's resolution.' → 'The ratio of the last two, 2.8, is close to the ratio of the added watts, 2.6; section 4 compares the two run by run.'
   '…the SRAM and mesh rails for 1.0 W between them (they run hotter)' → '…the SRAM and mesh rails for 1.0 W between them, about what a die 5 °C hotter adds to their leakage'.

26. **[low] horace-26** — *body.html §6 last paragraph*

   Append: 'The second card of section 10 cannot show it at all: its firmware reports a TDP of 0 W, so the governor only ever steps down and the clock never leaves 600 MHz.'

27. **[low] horace-29** — *body.html §7 L237, L261; §6 L231; §9 L364–366; Method L450, L463*

   L261 → 'under an unchanged workload (42.7 W at 84 °C, falling to 35.6 W as it cooled) the die fell from 84 to 72 °C in four minutes'.
   L237: 'up to six minutes' → 'up to seven minutes'.
   L231: 'for many minutes' → 'for hours'.
   L463 → 'then runs each started at 80 °C'.
   L450 comment → '# about an hour'.
   L364/L366: add '(both from the same afternoon session: +0.0 38.2 W, random normal 27.6 W over idle)'.

28. **[low] nav-11** — *rebuild*

   Regenerate report.json through finish_horace.sh (with the cards merge added above), rebuild with the current template, redeploy the folder including the three GIFs, check visibility.

### 3.5 et-soc1-why-low-power

Files: `docs/reports/sources/why-low-power.body.html`; `docs/reports/sources/why-low-power.script.js`; `docs/reports/sources/why-low-power.meta.json`; `docs/reports/2026-09-21-why-low-power.html (rebuilt)`

1. **[high] wlp-1, nar-1, nav-02, nl-15, fr-22** — *lede; KPI 5; script.js cmp table (note ~line 66, new row); §1 paragraph; body line ~65; §4 table header; meta.json description*

   Lede → '…and because it does 14 to 28 times fewer FLOPs per second (fp16 or fp32 here, against the A100's bf16). It is not more efficient per FLOP at dense matmul: the A100 spends 1.3 pJ per bf16 FLOP at the board, this card 3.3 pJ in fp16 and 7.0 pJ in fp32.'
   KPI 5: val '3.3–7.0 vs 1.3 pJ'; sub 'fp16–fp32 here against the A100's bf16 tensor cores: low power is not low energy per FLOP'.
   script.js: add after 'Dense matmul, measured': row('Dense matmul, 16-bit', '257 TFLOPS bf16 at 330 W', `${(2*C.fp16_randn.per_s/1e12).toFixed(1)} TFLOPS fp16 at ${f1(C.fp16_randn.p80)} W`, 'the closest like-for-like: 3.3 against 1.3 pJ per FLOP, 2.6×').
   Note 'the A100 is about five times better at dense matmul' → 'bf16 on the A100 against fp32 here: 5.4×; at 16 bits (fp16, 3.3 pJ) the A100 is about 2.6× better'.
   §1 → 'But also a twenty-eighth of the matmul throughput in fp32 (a fourteenth in fp16), so per FLOP the GPU wins by 5.4× against fp32 and 2.6× against fp16.' Then add: 'Against the A100's fp32 CUDA-core datasheet figure instead (19.5 TFLOPS at 400 W, 20.5 pJ per FLOP, no tensor cores), this card's 7.0 pJ is about three times better; the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency'>matmul efficiency report</a>, with its own kernel at 57 W, puts it at 3.4×. The verdict depends on which precision the GPU is allowed.'
   Body ~65: 'the one a GPU benchmark uses' → 'fp32 (Horace He's A100 run was bf16; this card's fp16 is 2.7 pJ)'.
   §4 header → 'ET-SoC-1 (fp32)'.
   meta description: '28 times fewer FLOPs per second' → '14–28 times fewer FLOPs per second'.

2. **[high] wlp-2, wlp-7** — *lede; KPI 1; script.js cmp rows 'Core voltage and clock' and V²×f; §4 paragraph and table rows; caveat 1; §4 closing paragraph*

   Lede: 'near 0.85 V and 1,400 MHz (a factor of 6 in switching power for the same capacitance)' → 'near 0.85 V and 1,160–1,410 MHz (a factor of 5 to 6 in switching power for the same capacitance)'.
   KPI 1: val '5–6× less'; sub '0.52 V and 600 MHz against about 0.85 V and 1,160–1,410 MHz: V² gives 2.7×, the clock 1.9–2.35×'.
   cmp 'Core voltage and clock':
   - A100 cell → `about ${A.volts} V · 1,160–1,410 MHz`;
   - note → 'Neither is published. 1,410 MHz is the maximum boost. Under He's 330 W cap on random data the clock is lower: 257 of the 312 peak TFLOPS needs at least 1,160 MHz, and if his zero-data run (295 TFLOPS) held 1,410 MHz, the random run was near 1,230. 0.75 V is nominal for 7 nm.'
   V²×f row: show '5.2–6.3×'.
   §4 paragraph → '…at about 0.85 V and 1,160–1,410 MHz: 237–288 nF of effective capacitance.'
   §4 table:
   - Switched capacitance: A100 '237–288 nF', ratio '1.4–1.7×'.
   - Clock: A100 '1,160–1,410 MHz', ratio '1.9–2.35×', note 'cycle counter against wall clock here; for the A100, 1,410 MHz is the maximum boost and the capped random-data run is at least 1,160 MHz (257/312 of peak), probably near 1,230 (257/295 of the zero-data run); the per-FLOP rows below do not depend on the clock'.
   Closing paragraph: 'So the ET-SoC-1's low power is three parts operating point and one part doing less.' → 'So of the 8.8× lower switching power, most is the operating point: 6.3× at the A100's maximum clock (2.7× from V², 2.35× from the clock), about 5.2–5.5× at the 1,160–1,230 MHz its capped random-data run implies. The rest, 1.4–1.7×, is switching less capacitance per cycle.' Change 'which is the 6.3× of the headline' → 'which is the 5–6× of the headline'.
   Caveat 1: append 'Nor is its clock under the 330 W cap: 1,410 MHz is an upper bound.'

3. **[medium] wlp-3** — *§2 second bullet; §2 table header and 'Esperanto's design target' row*

   Bullet → '<b>10 mW per core: the switching part fits for int8,</b> even at this card's higher voltage: 4 mW over idle on constant data and 10 mW on random data. But Esperanto's 10 mW was the whole budget, leakage included, and this card's minion rail alone reads 22 W under int8 random data at the end of a 7 s run (about 82 °C), 21.7 mW per minion. fp32 on random data switches 27 mW per core.'
   Table header → 'mW per minion, over idle'.
   Target row: mW cell '10 (total)'; last cell 'by P/(V²f), 10 mW at 0.425 V and 1 GHz is 0.055 nF; the slide's 0.040 nF would leave about 3 mW for the leakage its equation includes'.

4. **[medium] wlp-4, nl-13, nar-26** — *§2 third bullet; §3 'Voltage and clock' first bullet (body ~75)*

   §2 → 'Its lowest operating point is 0.52 V at 600 MHz. Below 65 °C die temperature and 65 W board power the firmware steps it up through 0.57 V at 700 MHz to 0.62 V at 800 MHz (see <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage#the-loop-as-measured'>the DVFS loop, and the leakage</a>).'
   §3: 'The card has two operating points, and they differ as CV²f says.' → '<b>The card has three operating points (600, 700 and 800 MHz); the two ends differ as CV²f says.</b>'

5. **[medium] wlp-5** — *lede; first TensorFMA/TensorLoad rows; chart title; '3. Ablations'; first 'governor'*

   Lede: after 'on all 1,024 cores' add '(Esperanto calls them minions: small in-order RISC-V cores, 32 to a shire, each shire with 4 MB of SRAM; more in the hub's glossary)'.
   First TensorFMA row → 'fp32 TensorFMA (the minion's matrix multiply-accumulate instruction), zeros: …'. First TensorLoad row → 'TensorLoad (a bulk load into the tensor unit) streaming from …'.
   Make the chart title's first 'the Horace experiment' a link: <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment'>the Horace experiment</a> (this repository's reproduction of Horace He's zeros-against-random matmul on this card).
   Heading '3. Ablations' → '3. Taking the terms away one at a time'.
   First 'governor' → 'the firmware's clock governor'.

6. **[medium] wlp-6, nav-21, nav-11** — *rebuild; §3 section references; §6 'Companion' bullet*

   Rebuild with the current template (heading ids and contents).
   Link 'sections 3 and 9' to …horace-experiment#from-flips-to-watts and #custom-workloads-structured-matrices, and 'section 8' to #a-model-from-flips-to-temperature. Link 'From a cool die the governor runs kernels at 800 MHz' to …dvfs-leakage#the-loop-as-measured.
   Replace the Companion bullet with <h2>7. Related reports</h2><ul>:
   - the Horace experiment (the flip model and thermal model used here)
   - The DVFS loop, and the leakage (the three operating points, the idle law re-checked after 20 hours, a second card that switches 8% less for the same work)
   - the energy manual (per-event costs with bars on two cards, including the awake core and DRAM bytes)
   - Matmul efficiency (the spec-sheet fp32 comparison)
   - Limits of observability, section 4 (…#power: what the three rails do not meter)
   - Memory hierarchy
   Add a caveat: 'One card; aifoundry3 switches about 8% less for the same work (DVFS report, section 7).'

7. **[low] wlp-8, nar-26, nl-34** — *§3 second bullet (body ~59)*

   → '<b>Power is close to linear in active cores:</b> 25.6 mW per minion at 256 and 512 active, 26.2 at 768 and 27.0 at 1,024; a line through zero fits 26.5 mW per minion.'

8. **[low] wlp-9, nl-11** — *KPI 2; §3 first bullet*

   KPI label → 'A core spinning in an integer loop'. Sub → '1,024 minions add 1.5 W (the energy manual's faster addi loop, twice the instruction rate, costs 2.1 mW); a gated tensor op 1.9 W; random fp32 27.6 W'.
   §3 bullet: after '1.4 mW per core, 8 pJ per instruction' add '(a four-add loop issuing about 0.3 instructions per cycle; the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#a-core-that-is-awake'>energy manual's</a> tighter addi loop draws 2.1 mW per minion on one hart and 3.4 mW on both)'.

9. **[low] wlp-10, nl-14, nav-21** — *§3 'Memory' first bullet; §2 TensorLoad rows*

   → 'Streaming tensors from LPDDR4x at 75 GB/s … adds 10.7 W: 142 pJ per byte (18 pJ per bit) end to end, on a buffer whose contents were never set; the energy manual's pinned-600 MHz rerun of the same stream gives 122 pJ/B, and tensor loads on known data give 91 (zeros) to 129 (random) pJ/B, 11–16 pJ per bit. Streaming from the shire's own L2 cache at 2.4 TB/s adds 6.2 W: 2.6 pJ per byte (0.3 pJ per bit), as the energy manual's L2 row (2.5 pJ/B) confirms. These are two 7 s strict-start runs per configuration at 80 °C (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy'>the energy manual, §4</a>).'

10. **[low] wlp-11** — *§3 'Voltage and clock', first bullet*

   → '…draw, over idle: zeros 3.9 against 1.9 W, ones 20.6 against 10.3 W, random fp32 about 52 against 27 W. The 800 MHz figures are the highest readings before the governor stepped down; random data held 800 MHz for at most 0.3 s. That is about 2.0× the switching power …'

11. **[low] wlp-12** — *§1 table 'Memory' row; §3 'Memory' second bullet; script.js transistor count*

   Memory row → 'HBM2 1,555 GB/s (40 GB) or HBM2e 2,039 GB/s (80 GB SXM4)'.
   Bullet → 'An A100 moves 1,555 to 2,039 GB/s, eleven to fifteen times more.'
   Transistors → '>24 B'.

12. **[low] wlp-13, nar-7** — *§5 second bullet (body ~135)*

   'regulators (about 7 W of the 28 W under random data never reaches the die)' → 'regulators (about 7 W of the 28 W under random data is on no rail sensor, some 4 W of it regulator delivery loss by the later fit in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed'>Limits of observability, section 4.2</a>)'.

13. **[low] wlp-14** — *§3 'Leakage and temperature' first bullet*

   → '…at 62 °C, where the card settled after the night of 20–21 September, 14 W in 27 W. After about 20 hours idle on 22 September, in a warmer room, it sat at 73 °C and 31.8 W, which this law predicts to 0.01 W.'

14. **[low] wlp-15** — *§3 'Voltage and clock' third bullet*

   → 'Esperanto's own model is in the same range: about 230 W at 0.85 V, 164 W at 0.75 V. This card's measured board power at 0.52 V, 47 W on ones and 64 W on random fp32, brackets the 49 W the curve gives there, although the curve is chip power at its own clock and workload.'

15. **[low] wlp-16** — *under the stacked chart; §1 'Power density' note*

   Add <p class='small'>Bars are the fitted model's split, so they differ from the measured table above by up to 0.8 W (random fp32: 63.1 W modelled, 63.9 W measured).</p>
   Power-density note → 'board power over die area; both include memory and regulators'.

16. **[low] fmt-1** — *lede; script.js cmp row*

   Lede: '1,400 MHz' → '1,410 MHz', unless the clock change above rewrites it to 1,160–1,410.
   script.js: `${A.mhz.toLocaleString('en-US')} MHz`.

17. **[low] nar-27** — *body lines ~10 and ~126*

   'whatever is not computing is gated off' → 'whatever is not computing is clock-gated (it stops switching but still leaks; nothing is power-gated)'.
   'everything idle is gated to nearly nothing' → 'everything idle is clock-gated to nearly no switching power'.

18. **[low] horace-5** — *body ~95 (flip budget)*

   'about 3 W' → 'about 3 W in 21 September's room (less on a warmer day)'.

19. **[low] nav-13** — *meta.json title; rebuild*

   Title → 'Why is it low power? · ET-SoC-1'.
   Rebuild, redeploy, check visibility.

### 3.6 et-soc1-dvfs-leakage

Files: `docs/reports/sources/dvfs-leakage.body.html`; `docs/reports/sources/dvfs-leakage.script.js`; `docs/reports/sources/dvfs-leakage.meta.json`; `tools/ettelem/analyze_dvfs.py`; `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json (regenerated)`; `docs/reports/2026-09-22-dvfs-leakage.html (rebuilt)`

1. **[high] dvfs-fw** — *byline; §8 bullet 1 ('the commit matching the card's firmware'); §1, §5 last bullet, §6 mechanism*

   Byline: 'firmware 353f20e' → 'firmware source read at et-platform 353f20e (the cards' own log strings show an older build; see §8)'.
   Add to §8: 'The service processor on aifoundry3 prints log lines that exist only in et-platform firmware before commit 60b40c10f (24 September 2024), which rewrote this governor. In that older governor the power guardband is used, throttle events are logged once per state change, and a step-up climbs to the top point in one go. Both cards report release 1.3.1, so §1 describes the current source, not necessarily the governor on these cards.'
   After open question 2 is answered, re-read §1, the §5 guardband bullet and §6 against 60b40c10f^ (or the release 1.3.1 tag). Until then, qualify every 'defined and never used' or 'the source says' statement with 'in the 353f20e source'.

2. **[high] dvfs-1** — *§2 paragraph under the limit-cycle chart; chart #cycle title; script.js (add tr.T); §5 last bullet*

   Paragraph → 'It hunts, and the missing hysteresis explains it. In this run the board never came near 65 W (it peaked at 56 W); what the loop kept crossing was the 65 °C line. At a reading of 66 °C the clock steps down; once the whole-degree reading is back at 65 °C the thermal test no longer fires, the power test sees 38 W < 65 W, and the clock steps back up. The clock changed seven times in 2.4 s, reaching 800 MHz twice, 1.6 s apart. Then, with the die settled at 66 °C, it stayed at 600 MHz for the last 4.5 s. Over the whole 7.4 s run it spent 5.6 s at the bottom point, 1.0 s at 700 MHz and 0.8 s at 800 MHz.'
   Chart title → 'One run of ones from a 64 °C die: the clock hunts across the 65 °C threshold, then stays at 600 MHz. Blue: minion clock. Orange: board power.' Add the die-temperature trace (tr.T) to the chart.
   §5 last bullet → '<b>The hunting measured here is at the thermal threshold</b>, which has no dead band in the source read (353f20e). The two power-guardband macros that source leaves unused would not damp it; damping it needs a temperature dead band.'

3. **[high] dvfs-2** — *§1 pseudo-code first line; §2 last paragraph; §5 bullet 2; §6 after the equation*

   Pseudo-code line → 'once per device-management pass, about every 133 ms (≈96 I2C reads, each followed by a 1 ms wait, then a DM_TASK_DELAY_MS = 10 ms sleep):'.
   §2: 'never in milliseconds, even though the task itself runs every 10 ms' → 'in three to seven passes of the ~133 ms loop'.
   'Once moving, it stepped at intervals at or below our 100 ms sampling period.' → 'Once moving, it stepped on successive passes; eight up-steps go straight from 600 to 800 MHz between two 100 ms samples, faster than one table point per pass. The 353f20e source does not explain that; the older governor the cards' logs point to (§8) climbs to the top point in one go.'
   §5: 'reads it every 10 ms' → 'reads it every pass, about every 133 ms'.
   §6: 'It runs every 10 ms, and every time it runs it throttles down.' is replaced by the aifoundry3 change below.

4. **[high] dvfs-3** — *script.js verdict table column 1 and header; leakfrac chart label; body.html lede*

   Header → 'What David Kanter said (paraphrased)'.
   Remove the “…” around all six column-1 strings.
   leakfrac label: 'Kanter: "typically 5–30%"' → 'Kanter: typically 5–30%'.
   Lede: 'He added a hedge: <q>maybe not on Esperanto's part, but on anything from a more mature company.</q>' → '"You actually have the instrumentation to do all of that," he said, and added a hedge: maybe not on Esperanto's part, but on anything from a more mature company.'
   Keep quotation marks only on words the brief itself marks as quotes.

5. **[high] dvfs-4** — *lede; verdict row 4 evidence; §3 'The hardware is there'; meta.json description*

   Verdict row 4 → 'The open RTL (Erbium, a later configuration of the same core, not the ET-SoC-1 chip) has per-minion sleep and isolation ports, tied off; no firmware line drives any power gating; and after 27 ms of idle no cache level shows a wake-up: …'.
   Lede: 'and its per-minion sleep transistors are real but tied off' → 'its open RTL has per-minion sleep controls that are tied off, and the card shows no sign of array power gating'.
   §3: '<b>The hardware is there.</b>' → '<b>The design has the ports.</b>'. After that paragraph add: 'That RTL is the Erbium configuration (one neighbourhood, no shire cache), so it says nothing about the L2/L3 arrays; for those, the wake-up probe below is the only evidence.'
   meta description: 'the sleep transistors exist but nothing drives them' → 'the open RTL has per-minion sleep controls, tied off, and the card shows no array power gating'.

6. **[medium] dvfs-5, nar-25, nl-26** — *§1 fourth bullet; §2 attribution paragraph and down-step table; analyze_dvfs.py lines ~61–64; dvfs.json*

   §1 bullet → '<b>The clock returns to the boot point when the master minion reports idle.</b> The service processor then sets the boot frequency (<code>go_to_idle_state_and_update_pwr_status()</code>). Back-to-back launches rarely trigger it: the zeros runs held 800 MHz across twelve and thirteen consecutive 0.37 s launches with 1–2 ms gaps.'
   §2 → '…and seven cannot be attributed from our telemetry: the die read 65 °C (once 64) and the board 34–56 W, so neither test fired on the values we sampled. One (the first zeros run, 6.0 s, 800→600 in a single step, 171 ms after a launch boundary) looks like the boot-point reset. The other six are single-point steps in pairs 0.4–0.5 s apart, which looks like the stepping loop, most likely thermal steps on passes where the service processor read 66 °C between our 10 Hz samples.'
   analyze_dvfs.py: rename the category 'kernel boundary' to 'unattributed (reading ≤65 °C)' and regenerate dvfs.json.
   Table: drop the 'ms from a kernel boundary' column, or add under it 'launches run back to back every 0.37–0.49 s'.

7. **[medium] dvfs-7** — *§6 paragraph after the TDP=0 equation; script.js #spcount*

   'So on aifoundry3 the loop is not disabled. It runs every 10 ms, and every time it runs it throttles down. The card can reach its lowest operating point and nothing can ever lift it off.' → 'So on aifoundry3 the loop is not disabled. Each kernel start logs a power throttle-down request and each kernel end an idle event, and the step-up request, the only way above 600 MHz, can never fire: the clock read 600 MHz in all 7,745 samples of the session.'
   #spcount → 'That 8 KB window of the card's trace buffer holds 26 throttle-down events alternating with 27 idle events, and 0 throttle-up events, every one printing tdp level: 0.'
   In §8, note that this log format belongs to firmware older than 353f20e. Do not claim a frequency floor below 600 MHz.

8. **[medium] dvfs-6, nl-27** — *§6 'The host cannot see this' paragraph*

   → 'It is simply held at 600 MHz for as long as its flashed TDP stays at zero, which on a workload that would otherwise run at 800 MHz gives up a quarter of the throughput (800 MHz is a third faster than 600), and nothing reports an error.'

9. **[medium] dvfs-8, nav-17, nl-26** — *§3 DRAM bullet of the wake-up results*

   → '<b>DRAM: +10 cycles</b>, and that one has a known cause. The controller closes the open row at each refresh (every 3.88 µs), and possibly after about 2 µs idle, so the next load pays an activate: 11 cycles (tRCD), as <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy'>Anatomy of a memory access</a> measured (§6); the +40 cycles in that report are a row conflict, a different case. Here 12 of the 20 paired differences are +9 to +14 cycles and the rest are near zero.'

10. **[medium] dvfs-9, nar-8** — *script.js verdict row 6 (line ~104)*

   Verdict → 'consistent, weakly tested'.
   Evidence → 'Every result checked in this work was correct: the matmul benchmark checks its outputs bit-exact against a host reference and the relay checks every element. The power sessions' launches were not compared with a reference (no launch raised the tensor unit's error flag). The 20-hour idle cannot show errors either way: nothing computed, DRAM ECC is compiled off and the SRAM ECC interrupt sources are never enabled.'

11. **[medium] dvfs-10** — *§6 last paragraph; §8 'Not established' bullet*

   'This also answers the question section 5 left open.' → 'This also settles what section 2 could not: whether the power branch works at all.'
   'The power branch of the loop, left open in the first version of this brief, is now established: it fires exactly as written, on aifoundry3, continuously.' → 'The power branch of the loop, which never fired on its own on aifoundry2, fires on aifoundry3 at every kernel start.'

12. **[medium] dvfs-11** — *§5 bullet 2*

   First sentence → '<b>Kanter's "measurement is expensive" argument is weaker for this card, though it does not vanish.</b>'
   Last sentence → 'The cost of reporting the card's own power here is one query. MLPerf's measured power is the whole system (host, power supply, cooling), which this meter does not see, and the card's meter updates every 133 ms, with the rails behind a one-second filter.'

13. **[medium] dvfs-12, nav-11** — *after the verdict table; §7 chart*

   Add a 'Terms' paragraph drawn from glossary G (decisions), covering: DVFS (dynamic voltage and frequency scaling); minion, shire and hart; the master minion, which dispatches kernels; the SP, which runs this loop; the PMIC, which meters power; PVT sensors; a VMIN-LUT point (one row of the firmware's frequency-to-voltage table); TDP (the firmware's power limit, 65 W); and the flip-counting model (the Horace experiment's model of power from the bits the multiply-add unit clocks and toggles). End it with a link to the hub's glossary.
   The rebuild gives heading ids and a contents list.
   Under the §7 chart: 'Operand patterns: all zeros; 50% zeros (sparse50); all ones; π; random signs only (signs); random mantissas only (mant); uniform [0,1); normal (randn).'

14. **[medium] dvfs-13, nav-17** — *byline; §2, §4, §5, §7; closing 'Companions'*

   §2: after 'cool-start session of 21 September' add '(<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment#the-speed-effect-appears-on-a-cool-die'>Horace experiment §6</a>)'.
   §5: link 'a model that counts four classes of switching event' to …horace-experiment#from-flips-to-watts.
   §4: after 'was fitted on 21 September' add '(<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment#a-model-from-flips-to-temperature'>the Horace experiment, §8</a>; tabulated in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#the-card-at-rest'>the energy manual, §1</a>)'.
   §7 start: 'The same comparison, with the transfer test in full, is §10 of <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment#a-second-card-and-what-transfers'>the Horace experiment</a>.'
   Byline: link 'a conversation with David Kanter' only if open question 1 keeps that page public.
   Replace the footer with a 'Related reports' list:
   - the Kanter brief (conditional)
   - the Horace experiment (flip model, thermal network, cool starts)
   - Why is the ET-SoC-1 low power? (V²f and the A100 comparison)
   - Anatomy of a memory access (DRAM row closure)
   - the energy manual (uses this idle law; every table at 600 MHz)
   - Power and temperature (the meters)
   - Limits of observability §4.1 (#the-chain: why the loop's input lags)
   - <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/findings'>docs/findings/</a>
   - back to the hub

15. **[low] dvfs-14, nar-26, wlp-8** — *§5 bullet 1 (body ~144)*

   → 'power over idle is close to linear in active minions: 25.6 mW per minion at 256 and 512 active, 26.2 at 768 and 27.0 at 1,024; a line through zero fits 26.5 mW per minion'.

16. **[low] dvfs-15** — *§2 attribution paragraph*

   'because on this card the only way to exceed 65 W is to be at 800 MHz, and by the time you get there the die is already through 65 °C' → 'because on this card only random data at 700–800 MHz exceeds 65 W, and it takes the die through 65 °C within half a second'.

17. **[low] dvfs-16** — *§4 last paragraph (~139)*

   → 'This card is above that range whether busy or idle: 36% of a 64 W random-data matmul, 64% of an idle card at 80 °C. Three things make it so, and only the third is the chip's own: (1) it runs at 0.52 V rather than the 0.4 V Esperanto designed for; (2) a desktop chassis idles it at 73–80 °C rather than in server airflow; (3) it carries 128 MB of shire SRAM (Esperanto quotes over 160 MB on die) with no array power gating in play.'

18. **[low] dvfs-17** — *§3 wake-up bullets and probe sentence; verdict row 4 cell; wake-up chart (script.js)*

   L2 bullet → '<b>L2: −11 cycles</b>, and this comes from the baseline, not the idle. With no idle at all the load reads 61 cycles, probably because the line was still settling after the asynchronous evict that placed it. At every idle from 1.7 µs to 27 ms it is a normal 49.5-cycle L2 hit. No wake-up.'
   Probe sentence → 'for a swept interval from zero to 27 ms (0, 1.7 µs, 17 µs … 27 ms)'.
   Chart: plot the zero-idle point at a tick labelled '0', or start at 1.7 µs and say that the baseline is zero idle.
   Verdict cell: use '−11' (a real minus sign) and '0', and write 'L1 (line left in place)' for 'L1 (no evict)'.

19. **[low] dvfs-18** — *§5 bullet 1; script.js scaletext; §4 check paragraph*

   §5 → '…predicts 1.91 for the switching-power ratio between the two points; the cool-start runs give 2.0 for ones (20.6 against 10.3 W over idle) and 2.05 for zeros, within 5–7%, from seven short uncontrolled runs.'
   scaletext: 'on a single aifoundry3 run and predicting the other seven' → 'on a single operand pattern and predicting the other seven'.
   §4: 'This brief opened by sampling the card cold on 22 September' → 'This brief opened by sampling the card after it had sat untouched for about 20.5 hours, on 22 September, in a warmer room'.

20. **[low] horace-16** — *body.html line ~224*

   'the first real out-of-sample test of the flip-counting model' → 'the strongest out-of-sample test of the flip-counting model'.

21. **[low] fr-18** — *body.html ~126; analyze_dvfs.py hours_idle (line 167)*

   '20.4 h' → 'about 20.5 h' (decision D20; no workload since 15:08 on 21 Sep apart from E18's 4.9 s probe). Set hours_idle to 20.5 and regenerate dvfs.json.

22. **[low] nav-13** — *meta.json title; rebuild*

   Title → 'The DVFS loop and its leakage · ET-SoC-1'.
   Regenerate dvfs.json, rebuild, redeploy, check visibility.

### 3.7 et-soc1-power-temperature

Files: `docs/reports/sources/power-temperature.body.html`; `docs/reports/sources/power-temperature.script.js`; `docs/reports/sources/power-temperature.meta.json`; `docs/reports/2026-09-20-et-soc1-power-temperature.html (rebuilt)`

1. **[medium] pt-2, nl-33, nl-12, horace-27, nav-19** — *after the lede; lede; KPIs 'Leakage slope' and 'Finest power record'; §1 table rows 2–3 (script.js M rows); §2 first and fourth bullets (L35); §5; meta.json*

   Banner after the lede: <div class='card'><b>Later work refines this page.</b> Leakage is now the idle law P<sub>idle</sub> = 12.6 W + 23.3 W·e<sup>(T−80)/36</sup>, whose slope is 0.52 W/°C at 72 °C, 0.65 at 80 °C and 0.79 at 87 °C. This page's own load step (57→65 W over 74→87 °C) is about 0.65 W/°C, as that law predicts; the 0.8 W/°C quoted below is the first Horace session's fit at 79–90 °C (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>DVFS and leakage</a>). The rail figures are the PMIC's own running average, roughly first-order with τ ≈ 1 s, which the service processor copies every 133 ms pass — not a 2 s moving average — and the unmetered remainder is now attributed (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#power'>hub §4</a>). The hub's <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#improve'>improvement ladder</a> supersedes §5 here.</div>
   Lede: 'the same work costs 0.8 W more per °C' → 'the same work costs about 0.65 W more per °C at 80 °C'.
   KPI 'Leakage slope' sub → 'board, under load (fit over the first Horace runs, 79–90 °C); 0.55 at idle at 72 °C; the idle law's slope is 0.65 W/°C at 80 °C'.
   KPI 'Finest power record' and §1 rows: '~2 s moving average' → 'the PMIC's running average (τ ≈ 1 s; 88% of a step after 2 s)'.
   §2 L35 → 'The first (20 September) version of the Horace experiment, over 22 runs without temperature control, gave 0.78 W/°C on the board and 0.38 W/°C on the minion rail; its strict runs give 0.81 W/°C within hot runs, and the idle law 0.65 W/°C at 80 °C.'
   §2 rail bullet: after 'lag a step by about 2 s' add '(read later from the firmware: the PMIC keeps each rail as a roughly first-order running average with τ ≈ 1 s, which the SP copies every pass; <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-chain'>Limits of observability, §4.1</a>)'.
   §5: under the heading add 'Superseded by the fuller <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#improve'>improvement ladder</a>.'
   meta.json: 'leakage of 0.8 W per °C' → 'leakage of about 0.65 W per °C at 80 °C'.

2. **[medium] pt-1, horace-27, nav-19** — *§2 last bullet (L54)*

   → 'From a cool die (62 °C after a night idle) the governor raises the same kernel from 600 to 800 MHz and 0.62 V within 0.4–1 s of launch, and steps it down as the die passes 65 °C: see §6 of <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment#the-speed-effect-appears-on-a-cool-die'>the Horace experiment</a>, and <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>the DVFS report</a>, which reads the governor's source and classifies every clock change. (Corrected 21 September; this bullet first said the governor never acts.)'

3. **[medium] pt-3** — *§3 caption and map; KPI 'Finest voltage map'; meta.json*

   Either place shires 32 and 33 in MESH, or change the caption to 'below are the 32 compute shires on the mesh; the other two minion shires (32 and 33) read 518 and 519 mV'. If you take the caption route, also change the KPI sub-line and meta description from '34-shire voltage map' to '34-shire voltage readings (32 drawn on the mesh)'.
   Under the map add: 'Stronger colour = higher voltage (516–521 mV).'

4. **[medium] pt-5, horace-27, nav-19** — *footer (L85–86); §1 'Energy per event' row (script.js); §2 memory-anatomy mention*

   Footer → 'Raw data: <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-09-20-power-aifoundry2'>docs/reports/data/2026-09-20-power-aifoundry2/</a>.' followed by <h2>Related reports</h2> with:
   - the Horace experiment (data-dependent matmul power, after Horace He's A100 post; same client)
   - the DVFS loop, and the leakage (the governor and the idle law)
   - Spatial temperature (per-shire temperature; the voltage map in §3 here is the one it cites)
   - Anatomy of a memory access
   - the energy manual (§1: the idle law this page's 0.8 W/°C became)
   - the hub's meter chain (#power)
   - sensor and firmware sources: <a href='https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/docs/research/power-telemetry.md'>docs/research/power-telemetry.md</a>
   Link 'memory-anatomy and Horace reports' in the §1 row the same way, and 'the memory-anatomy report' in §2 to …et-soc1-memory-anatomy#where-the-energy-goes.

5. **[low] pt-4** — *§2 fourth bullet*

   'For 2 s after a load starts the remainder reads 36 W (rails have not caught up), and for 2 s after it stops it reads 14 W, below idle.' → 'When the matmul starts, the remainder jumps to 39 W and decays to about 22 W within 2–3 s as the rails catch up. When it stops, the remainder goes briefly negative (−3.5 W: the rails' averages still include the load) and climbs back through 14 W over about 3 s.'

6. **[low] pt-6** — *after the lede*

   Add <p class='small'><b>Terms.</b> PMIC: the board's power-management controller, which meters the 12 V input power and three regulators. Minions are the chip's small RISC-V cores, 32 to a shire (the chip's tile). There are 34 minion shires, 32 of which (1,024 minions) run kernels. Memory shires hold the DRAM controllers. The Maxions are four larger out-of-order RISC-V cores on the die. The service processor (SP) is the on-card management CPU; the SPST trace is its per-pass stats log, and the MMST trace is the master minion's bandwidth log. MDI (the Minion Debug Interface) reads the registers and CSRs (control and status registers) of a halted hart, one hardware thread of a minion. More in the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#terms'>hub's glossary</a>.</p>

7. **[low] dvfs-fw, nav-13, nav-11** — *byline; meta.json title; rebuild*

   Byline: 'et-platform 353f20e firmware' → 'firmware source read at et-platform 353f20e (the cards' log strings point to an older build)'.
   Title → 'Power and temperature telemetry · ET-SoC-1'.
   Rebuild (this creates #the-per-shire-voltage-map, which the hub's E6 link targets), redeploy, check visibility.

### 3.8 et-soc1-hot-line

Files: `docs/reports/sources/hot-line.body.html`; `docs/reports/sources/hot-line.script.js`; `docs/reports/sources/hot-line.meta.json`; `docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json`; `docs/reports/2026-09-22-hot-line.html (rebuilt)`

1. **[medium] hl-1** — *§5 heading and paragraph after the errata; §9 'Not established'*

   Paragraph → 'That bears on both questions worth sending back. <b>Would setting <code>l3_yield</code> restore the host?</b> Not certainly. Erratum 4.1 says it does not when the host and the mesh want the same address. The case measured here is different addresses, which is what the yield was built for. But erratum 4.2 says the yield has no sub-bank granularity, so a host request to the sub-bank the hot line saturates can still be skipped indefinitely, and each host minion's stream reaches that sub-bank sooner or later. It was not tested. <b>Does it hold when the line is DRAM-backed …</b>' (keep the rest).
   Heading → '5. Esperanto knew: two errata describe it'.
   §9: 'and the erratum says it would not help here anyway' → 'and the errata suggest it would not fully help'.

2. **[medium] hl-2, nav-01, nav-22** — *byline; §9 (or Related reports)*

   Byline: after 'following up a benchmark result Ivan reported in Discord' add ' (first analysed, with his 6% taken at face value, in <a href='https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation'>L2 mainline starvation</a>)'.
   Add <li>The <a href='https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation'>L2 mainline starvation brief</a>, written the same day from Ivan's report and the shire-cache spec, is an argument, not a measurement. It takes his 6% as measured; the atomic here did not reproduce it (the host shire's share is 1.004). It calls <code>l3_yield</code> 'the lever, not a workaround' but advises against changing it; section 5 here reads errata 4.1 and 4.2 as limiting what the yield could do. Its practical advice, to home hot structures in a shire that does no compute or to replace one global counter with per-shire counters and a tree, agrees with section 8. Its warning about two-dimensional TensorSend arrays stands.</li>

3. **[medium] hl-3, nl-9** — *after the §7 energy table*

   Add: 'Re-measured for the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#synchronisation'>energy manual</a> on 23 September (the 22 September launches plus warm passes; n = 7, four on aifoundry2 and three on aifoundry3): 19.8 nJ [16.9–23.6] per contended atomic and 1.16 nJ [1.01–1.37] spread over 32 lines, still 17×. The table above is the first measurement and sits at the top of both ranges. The reading-only row's 0.07 W is inside the idle baseline's ±0.2 W, so its 0.4 nJ (0.37–0.82 over the reruns) is an order of magnitude, not a measurement.'

4. **[medium] hl-4** — *§4 lead-in, paragraph after the chart, chart title and caption (body + script.js)*

   Lead-in → 'It takes one other shire. Two shires run, the host and one other, each with the same number of minions n. The host's n minions read their own scratchpad, and the other shire's n hammer the line. The host's rate is compared with n times the per-minion rate of its 32-minion loop alone, which is why a single host minion reads 111%:'.
   Paragraph → 'From 2 to 20 remote requesters the host shire stays within about a percent of untouched (98.9–99.9%), …'.
   Chart title → 'Host shire's own memory throughput against the number of remote minions'.
   Caption: add 'The host runs as many minions as the remote shire. The right axis is inverted: higher means more often.'

5. **[medium] hl-5, hl-12** — *after the lede; byline; §2 first sentence; the 'repository's own note' sentence*

   Add <p class='small'><b>Terms.</b> The ET-SoC-1's 1,024 usable RISC-V cores (minions) sit in 32 shires of 32, each shire in four neighbourhoods of eight. Each shire has a 4 MB shire cache, split between its own L2, an L3 slice and a scratchpad (software-managed SRAM any shire can address; SCP in the errata). Every DRAM line is cached in the L3 slice of one home shire, chosen by physical-address bits 10:6. Requests from a shire's own minions are neighbourhood requests; requests arriving from other shires over the mesh are L3-slave requests. amoaddg.w is a global atomic add, performed at the line's home. The PRM is Esperanto's Programmer's Reference Manual. More in the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#terms'>hub's glossary</a>.</p>
   Byline: 'Ivan reported in Discord' → 'reported by Ivan (@ivanchernobyl) in the lab's Discord' (see open question 8).
   §2 first sentence → 'Spreading the same work over 32 lines, one per shire, changes everything:' (keep the rest of the sentence).
   'the repository's own note that a sub-bank accepts a request every two cycles' → 'a reading of the shire-cache spec in docs/research/counters-and-dram.md, not measured here, that a sub-bank accepts a request every two cycles,'.

6. **[medium] hl-6, nav-22, nav-11** — *rebuild; §8; §9; data paths; before Method*

   Rebuild: scripts/build-report.py hot-line docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json docs/reports/2026-09-22-hot-line.html (gives heading ids).
   §8: link 'a chip-wide barrier we measure at 4,997 cycles' to https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication#every-primitive-against-a-gpu (the 'Chip-wide barrier, 8.3 µs' row).
   §9: link 'PA[10:6]' to https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#l3-110-cycles-plus-12-per-hop.
   Link the docs/reports/data/… path to its GitHub tree.
   Add <h2>Related reports</h2> before Method:
   - Hand it to the next shire (share a slab through a scratchpad instead of one line)
   - the energy manual §6 (these energies with bars)
   - Anatomy of a memory access (how PA[10:6] picks the home shire)
   - On-chip communication (the chip-wide barrier, 8.3 µs with atomics and 2.3 µs on the hardware tree)
   - Spatial temperature (the per-shire sensors the 'not established' bullet needs)
   - the L2 mainline starvation brief (see above)

7. **[low] hl-7** — *lede; §9 fourth bullet*

   Lede: 'it is identical on both cards we have' → 'it reproduces on both cards we could run it on (aifoundry2 and aifoundry3)'.
   §9 → 'Every sweep ran on aifoundry2 and was repeated on aifoundry3; the energy table in section 7 is aifoundry2 only (both cards are in the 23 September reruns). The cards agree to the operation in most rows (384 and 384, 10.0 and 10.0 cycles). The host reading scratchpad under a DRAM-homed hot line differs, 208 against 240.'

8. **[low] hl-8** — *lede; meta.json description*

   Lede → 'The atomic is shared out to within half a percent (every shire between 0.998 and 1.004 of an even split), including with the shire that hosts it.'
   Meta → '…is served fairly, to within half a percent, and takes the whole memory path…'.

9. **[low] hl-9** — *§1 chart title and caption (script.js + body)*

   Chart title → '…line is a DRAM line homed in shire 0'.
   After the caption add: 'The same holds for Ivan's exact case, a scratchpad word in shire 0: host share 1.004, every shire 0.998–1.004.'

10. **[low] hl-10** — *hotline.json context.errata[1]*

   quote → '… when it's the neighborhood's turn to make a request due to l3_yield_priority. The neighborhood request uses a different sub-bank which satisfies l3_yield_priority. As a result a request to the over used sub-bank from a neighborhood may not make progress despite l3_yield_priority being non-zero.'
   impact → 'Low. It would have to be a pretty consistent and repeating pattern for the neighborhood request to a particular sub-bank to be skipped over and over.'
   workaround → 'Access patterns should be spread pretty evenly across sub-banks.'

11. **[low] hl-11** — *§8 third bullet*

   → '<b>If you must, pace it:</b> each requester should wait at least 10 cycles times the number of requesters. For the 992 here that is 10,000 cycles (about 17 µs), which gives the host shire back half its memory path for four percent of the hammering shires' rate; 12,000 gives it 86% for 20%.'

12. **[low] hl-13** — *script.js KPI 3 (k3); §4 paragraph*

   KPI value → a range: `${prev.remote_minions+1}–${req.remote_minions}` (21–24). Sub → '20 leave the host untouched, 24 stop it (the inequality in section 4 puts it at 22); one shire has 32'.
   §4 → 'By twenty-four, the first count tested above twenty, the measured cost reaches 10.0 cycles per atomic…'.

13. **[low] fmt-1** — *script.js placetab and pwrtab rate columns*

   Use Math.round(…).toLocaleString('en-US') on both rate columns, and add to the §7 caption that the rate there is timed by the power runs, so 1,919 against 1,920 is expected.

14. **[low] nav-13** — *meta.json title; redeploy*

   Title → 'One hot line stops a shire · ET-SoC-1'.
   Redeploy, check visibility.

### 3.9 et-soc1-on-chip-relay

Files: `docs/reports/sources/on-chip-relay.body.html`; `docs/reports/sources/on-chip-relay.script.js`; `docs/reports/sources/on-chip-relay.meta.json`; `workloads/onchip/analyze_onchip.py`; `docs/reports/2026-09-22-on-chip-relay.html (rebuilt)`

1. **[high] relay-1, vnav-m1, nav-23** — *lede (body ~4–8); §5 heading, intro, table (script.js ~121) and paragraph; §7 first bullet and 'not established'; meta.json; analyze_onchip.py*

   Lede: 'and the shire next door at about 1 TB/s' → 'and another shire's at about 1 TB/s'; 'hands each stage's output to a neighbouring shire,' → 'hands each stage's output to another shire (the next one in shire order, which on the mesh is 1 to 10 hops away, 3.5 on average),'.
   §5 heading → '5. How far the slab moves does not change the bandwidth'.
   Intro → 'The obvious worry about handing data to another shire is the network in between. Shire numbers do not follow the mesh: on the shire map of the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>on-chip communication report</a>, the next shire in the ring is on average 3.5 mesh hops away (1 to 10), two places on 4.5, and sixteen places on only 2.1 (1 to 6). Across offsets whose mean distance runs from 1.6 to 4.5 hops the bandwidth stays between 593 and 734 GB/s and does not follow the distance:'.
   Table: add a column 'Mesh hops, mean (range)' with 3.5 (1–10), 4.5 (2–7), 3.7 (1–8), 1.6 (1–7), 2.1 (1–6), computed in analyze_onchip.py from the MARTY map (workloads/nocbench/analyze.py). Rename 'Shires the slab moves per stage' → 'Shire IDs back round the ring' and 'Against handing it next door' → 'Against the next shire in ID order'.
   Paragraph: 'the per-hop latency of 12 cycles never appears' → 'the 12-cycle round trip per hop never appears'; 'that is the same wherever it is' → 'and it does not depend on where that shire is'.
   §7 first bullet: 'so a neighbouring shire cannot read a stale line' → 'so the shire that reads it next cannot read a stale line'. Add to 'not established': 'whether handing to a physical neighbour lowers the 8.9 pJ/B'.
   meta.json: 'a neighbouring shire's scratchpad' → 'another shire's scratchpad'.

2. **[medium] relay-4, nl-16, nav-23, nar-18** — *§5 last paragraph*

   End with: 'The practical consequence is that placement is free in bandwidth: a stage can be given to whichever shire suits. It is not free in energy: each mesh hop a byte travels costs 1.5–2.2 pJ on a loaded mesh (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm#meaning'>Heat per millimetre, §9</a>), about half of what reading the byte from the shire's own scratchpad costs, and the 8.9 pJ/B hand-off above averages 3.5 hops, so a stage placed on a physical neighbour should cost less. This relay's slabs hold one constant value per slab, which costs less than random data.'

3. **[medium] relay-2, nl-18, nar-9, nav-23** — *script.js §2 power table and powernote (~line 64)*

   Show pJ per byte with one decimal.
   powernote → 'Idle was 30.61 W. All three sit within a watt of each other while moving between 49.7 and 1502.5 GB/s, so the energy per byte differs by about 25× for the shire-local case and 12× for the hand-off. Re-measured on 23 September, three warm passes on each card (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-between-cores-and-shires'>the energy manual, §5</a>): DRAM 105.7 [99.5–111.0] pJ per byte moved, next shire 8.6 [7.8–9.2], own scratchpad 3.99 [3.90–4.25] — 12× and 26×. For comparison, the manual's per-byte reads at 600 MHz: DRAM 122 [117–129] pJ/B, own scratchpad 2.52, another shire's 6.65 (the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy'>memory-hierarchy report</a>'s 148, 2.8 and 6.3 were taken with the clock free).'

4. **[medium] relay-3, nl-17, nar-30** — *script.js §4 inttext (~112–117)*

   → 'One add per element is pure data movement and the hand-off is 12.2× ahead (this sweep's own run; the headline run gives 12.3×). The lead holds to about four adds per element (11.4×) and then falls faster with each quadrupling: 8.4× at 16, 4.1× at 64, 2.4× at 128 and 1.5× at 256 adds — 32 flops per byte moved, counting the byte read and the byte written (64 per byte read). For this vector-add kernel on-chip placement pays several-fold up to a few flops per byte moved and is still 1.5× at 32. The tensor unit does twice the fadd.ps rate; for it the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points'>ridge points</a> report puts the DRAM crossover near 130 FLOP per byte read.'

5. **[medium] relay-5, nav-23, nav-11** — *rebuild; end of page; inline mentions*

   Rebuild with the current template (heading ids and contents).
   Replace the final <p class='small'> with '<h2>8. Related reports</h2><ul>':
   - the energy manual §5 (#bytes-between-cores-and-shires): this relay's energy with bars from both cards
   - Heat per millimetre: what each hop costs
   - Memory hierarchy: the 2.5 TB/s, 1 TB/s and 76 GB/s of the lede
   - On-chip communication: the shire map, 12 cycles per hop, the barrier, the TensorSend hang
   - Ridge points: the roofline
   - One hot line stops a shire: the companion
   - the L2 mainline starvation brief, last section: why not a 2D systolic array
   - findings index <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/findings'>docs/findings/</a>
   Close with </ul>.
   In §6 link 'A chip-wide barrier costs about 5,000 cycles' and the systolic warning to on-chip communication (#reduction-trees and #a-trap-one-ready-flag-per-minion). Link 'the memory-hierarchy work' inline.

6. **[low] relay-6, nl-32** — *lede*

   'Both numbers reproduce on a second card to within 1%' → 'Both numbers reproduce on a second card to within 2%'.

7. **[low] relay-7** — *§6 first bullet; §7 second bullet*

   §6 → 'At 1 MB per shire a DRAM stage is 830,000 cycles, a hand-off stage 68,000 and an own-scratchpad stage 27,000, so the barrier is under a fifth of even the fastest case. From four stages to thirty-two the advantage is flat (12.0–12.5×); with one or two stages it is larger (15.3×, 13.4×), where the DRAM route reaches only 38 and 44 GB/s.'
   §7: 'an on-chip stage costs twenty-seven thousand cycles' → 'an on-chip stage costs 27,000–68,000 cycles'.

8. **[low] relay-8** — *lede; script.js §3 chart (~75)*

   Lede: 'below the 32 MB L3 there is almost nothing to win' → 'below the 32 MB L3 the hand-off wins at most 1.4× (the shire's own scratchpad 1.3–3.3×)'.
   Chart: move the dashed line to x(16) and label it 'footprint = 32 MB of L3'.

9. **[low] relay-9** — *§6 first bullet; §7 'Not established'*

   §6: 'which on this chip costs 48 GB/s' → 'which on this chip runs at 48 GB/s of reads and writes'.
   §7 → 'And the comparison is against this chip's DRAM, which streams 76 GB/s of plain reads and carries this relay's reads and writes at 48 GB/s, not against a memory system in general.'

10. **[low] relay-10** — *after the lede; §7; script.js line ~34 and idle row (~58)*

   Add <p class='small'><b>Terms.</b> The ET-SoC-1's cores are <i>minions</i>, 32 to a <i>shire</i>; each shire has 4 MB of SRAM, split on these cards into 0.5 MB of L2 cache, a 1 MB slice of the chip-wide 32 MB L3 and a 2.5 MB <i>scratchpad</i> that any shire can address. A <i>hart</i> is one of a minion's two hardware threads. A <i>tensor store</i> writes a block from a minion's registers straight to memory, past its caches. More in the hub's glossary.</p>
   §7: 'the PRM's format 0' → 'the Programmer's Reference Manual's (PRM) format 0'.
   Format GB/s with toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1}), and delete the 'idle card | 0 | — | —' row.

11. **[low] nav-13** — *meta.json title; redeploy*

   Title → 'Hand it to the next shire: on-chip relay vs DRAM · ET-SoC-1'.
   Redeploy, check visibility.

### 3.10 et-soc1-heat-per-mm

Files: `docs/reports/sources/heat-per-mm.body.html`; `docs/reports/sources/heat-per-mm.script.js`; `docs/reports/sources/heat-per-mm.meta.json`; `docs/reports/2026-09-24-heat-per-mm.html (rebuilt)`

1. **[medium] heat-1** — *§11 'Related: the energy manual, §4.3 (the first wire measurement)'*

   '(the first wire measurement)' → '(the first wire measurement: its 1.81 pJ/B per hop and 133 fJ per random bit per hop are lower than this page's because its fit runs to 8 hops, where only 16 shires have a partner and the point sits level with 6 hops; over 1–6 hops its data give 2.1–2.3 pJ/B per hop, as here)'.

2. **[medium] heat-2** — *after the lede; script.js §5 (~236); §7*

   Add <p class='small'><b>Terms.</b> The ET-SoC-1's cores are <i>minions</i> (two hardware threads, <i>harts</i>, each), 32 to a <i>shire</i>; part of each shire's 4 MB of SRAM is a 2.5 MB <i>scratchpad</i> any shire can address. Shires talk over a mesh network-on-chip (NoC), one mesh stop per shire; a <i>flit</i> is the unit the mesh moves as a whole — here at least one 64-byte line (§7). A <i>tensor load</i> is a minion's bulk load of up to 1 KB. Board power comes from the card's power-management IC (PMIC); the mesh rail's reading comes from the service processor (SP), the chip's management core. a2 and a3 are the cards aifoundry2 and aifoundry3. More in the hub's glossary.</p>
   §5: 'split by how often flits come back to back: the fitted b/a puts that at about 60%' → 'split by how often flits come back to back: if a fraction f of flits is followed directly by another, a = f·E_t and b = 2(1−f)·E_t, and the fitted b/a = 1.32 gives f ≈ 0.6'.
   §7: 'lane PA[7:6]' → 'lane PA[7:6] (bits 7–6 of the physical address)'.

3. **[low] heat-5, nav-15** — *body.html lines ~130 and ~145; script.js §9 energy-manual link (~293)*

   Line 130: href → https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed; text 'observability report, §4.2'.
   Line 145: href → …#the-chain.
   §9 energy-manual link → https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy.

4. **[low] heat-6, nav-15** — *byline; §1; §11 Related*

   Byline: link the repository as <a href='https://github.com/yaroslavvb/et-soc1-prototyping'>yaroslavvb/et-soc1-prototyping</a>. Link SYNTHESIS.md, VERDICT.md and the data directories to their tree/main paths.
   §11 Related:
   - hand it to the next shire: rewrite its description as 'a computation that hands its intermediate to another shire's scratchpad instead of DRAM: 12× faster at a twelfth of the energy, with bandwidth independent of which shire'.
   - Add on-chip communication: 'the shire map behind these hop counts, and the first estimate from 1 KB messages, 1.9 pJ per byte per hop'.
   - Add anatomy of a memory access: 'the first per-hop energy, ~0.9 pJ/B from 64 B L3 loads'.
   - Add the energy manual §5 (#bytes-between-cores-and-shires): 'messages between shires'.
   - Add spatial temperature: 'the 35 temperature sensors on the same grid of 3.72 mm tiles'.

5. **[low] nav-15** — *lede*

   'on the ET-SoC-1's 8 × 6 mesh' → 'on the ET-SoC-1's mesh (the 6 × 6 grid of shires plus a column of memory shires down each side: 8 × 6 stops)'.

6. **[low] heat-3** — *script.js §2 die caption (~52); body §2*

   Caption → '… 8 × 6 mesh stops: 34 minion shires (blue) — the 32 compute shires (1,024 minions) that the other reports count, plus the master shire, which runs the firmware, and a spare — the PCIe and I/O shires (pink, top row), and four memory shires with their LPDDR4x PHYs down each side (amber); the corners are empty. The 6 × 6 grid of the other reports is the inner six columns.'
   §2: after 'on the logical map' add '(marty1885's shire coordinates, which the on-chip communication report confirmed from latency)'.

7. **[low] heat-4** — *script.js §9 last sentence (~296)*

   → '…so on this chip one lane of a vector float add is worth 0.6 of a hop — about 2.3 mm — of movement, 230 times Dally's 10 µm, because an instruction here costs far more than the adder's own 1 fJ per bit; a scalar fadd.s (25.5 pJ) is worth about three hops.'

8. **[low] nl-35** — *script.js §9 DRAM comparison*

   Use X.tload_dram_random_pj_per_byte (129.1) for the DRAM line → '8.3 nJ to read the same line from DRAM'. Print the hand-off ratio with f1 (about 4.6×). Add '(random-data tensor loads)' after 'the energy manual, board power'.

9. **[low] heat-7** — *script.js §8 chart row (~155)*

   Label → 'ET-SoC-1 mesh rail, everything, loaded mesh, at 0.9 V'.

10. **[low] heat-8** — *script.js §9 (~293)*

   'A 64-byte line carried across the whole die — 10 hops, about 37 mm corner to corner' → 'A 64-byte line carried between the two farthest shires — 10 hops, about 37 mm of mesh travel, extrapolated from the 1–6 hops measured —'.

11. **[low] heat-9** — *body.html line ~12*

   '<b>What costs is surprising</b>' → '<b>What costs energy is surprising</b>'.

12. **[low] nav-13** — *meta.json title; rebuild*

   Title → 'Heat per millimetre · ET-SoC-1'.
   Rebuild, redeploy, check visibility.

### 3.11 et-soc1-memory-anatomy

Files: `workloads/memprobe/report_template.html`; `workloads/memprobe/build_report.py (only if needed)`; `workloads/memprobe/README.md (optional line)`; `docs/reports/2026-09-19-et-soc1-memory-anatomy.html (rebuilt from the template)`

1. **[high] anat-1** — *§5 first and last paragraphs; §2 explorer parts(); §9 first bullet*

   §5: '(row still open, no contention)' → '(each load at least 1,000 idle cycles after the row was last used, so the row had closed and every load paid an activate; no contention)'.
   Last paragraph, first two sentences → 'Of the 91 cycles (152 ns), the DRAM chip itself accounts for about 25: an activate (tRCD, 11 cycles = 18 ns, §6) plus the 19.3 ns read latency and a 4.3 ns burst (14 cycles), from the controller's timing registers. The remaining ~66 cycles (~110 ns) are the memory shire: controller queue, PHY, and the crossings between the 933 MHz memory clock and the mesh.'
   §9: '77 cycles in the memory shire' → '66 cycles in the memory shire'.
   parts(): memory-shire segment 77 → 66. Row-state lines:
   - if (st.dstate !== 'open') P.push(['activate (tRCD)', 11, 'c6']);
   - if (st.dstate === 'conflict') P.push(['wait for the other row + precharge', 40, 'c6']);
   - if (st.dstate === 'refresh') P.push(['wait for refresh (worst case)', 210, 'c7']);
   That makes open = model − 11 (214 for home 0, matching the measured 213–216) and closed = the model; refresh's worst case becomes 435 (measured maximum 434).

2. **[high] anat-3, nl-20, nav-24** — *§7, after the energy table (new last bullet)*

   Add: 'Later measurements put DRAM higher. The energy manual (§4, 23 September, both cards, pinned 600 MHz, host board power) gives 122 pJ/B [117–129] for plain loads from DRAM, and 91 pJ/B on zeros against 129 on random data for tensor loads. This page's 79 pJ/B uses the service processor's trace, whose rise above idle is 14–20% smaller than the host meter's for every pattern here (with the host meter it is 92 pJ/B; <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature'>Power and temperature</a> §2 explains the difference). It was also measured on an arena that was never initialised, so the bit pattern of the loaded data is unknown. Per mesh hop the manual gives 0.70 pJ/B on zeros and 1.74 on random data, against ~0.9 here; the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm'>heat-per-millimetre report</a> measures 1.5–2.2 pJ/B per hop and splits it into flips and ones carried.'
   Link 'energy manual (§4)' to https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy.

3. **[high] anat-2** — *KPI 'Latency model'; lede; §5 after the formula; §2 intro*

   KPI sub → 'for 1,450 of 1,500 random lines (±5 for 1,490), from address bits alone.'
   Lede → '…predicts each line's DRAM latency to within ±3 cycles for 97% of lines'.
   §5 → 'and the model's error is within ±3 cycles for 1,450 of 1,500 lines and within ±5 for 1,490. The other ten are outliers: seven read about 128 cycles short (counter glitches the correction missed, §8), two are 44 and 71 cycles slow (probably refresh), and one is 29 cycles fast.'
   §2 intro: 'which matches measured loads to ±3 cycles' → 'which matches 97% of measured loads to ±3 cycles'.

4. **[medium] anat-m1** — *§3 paragraph after the ladder table; §1 'Where a line lives' notes*

   §3 paragraph → 'Evicts keep working after the instruction retires, but none of the 256 loads timed straight after an evict to memory came back in L3 time: every one went to DRAM. What changes is the timing. With no fence, the load queues behind the evict (median 365, about 58 cycles above the §5 model). With a fence but no wait, a third of the loads find the row that the previous load of the same line opened still open, and read 11 cycles fast (minimum 213, on a line whose closed-row time is 225). Waiting a few hundred cycles after the fence lets the row close, so every timed DRAM load pays the same activate.'
   §1: 'Asynchronous: a load issued straight after can still hit (§3).' → 'Asynchronous: a load issued straight after queues behind it, and may find its DRAM row still open (§3).'

5. **[medium] anat-4** — *§4 first paragraph*

   'within ±2 cycles for 1,498 of 1,500 lines' → 'within ±4 cycles for 1,498 of 1,500 lines (the median of three loads per line; 1,309 are within ±2)'.

6. **[medium] anat-5** — *§8 first paragraph*

   '8% of back-to-back read pairs differed by 138 or −118 cycles instead of 10.' → '16% of back-to-back read pairs (320 by +138 and 314 by −118, of 4,000) differed from the expected 10 cycles.'

7. **[medium] anat-6** — *§1 table 'Time' row; §8; workloads/memprobe/README.md*

   §1: replace 'With the correction, a timed no-op reads exactly 10 cycles in 4,000 of 4,000 tries.' with 'Correcting the 4,000 raw read pairs afterwards makes every pair read exactly 10. Applied on the card, inside timed code, the correction still misses about 1 interval in 70 (57 of 4,000 corrected timed no-ops read 138 or −118), so reject results that are ±128 off, or take the median of repeated loads rather than the fastest.'
   §8: after 'for all 4,000 pairs.' add 'Inside a running kernel it catches most but not all of them (see §1); the seven lines about 128 cycles fast in §5 are such misses, picked out by taking the fastest of three loads.'
   Optional, memprobe README: 'corrected timed no-ops (always 10 cycles)' → 'corrected timed no-ops (10 cycles in 3,943 of 4,000)'.

8. **[medium] anat-7** — *§7 chart axis label, table header, L1 row, caption (~681), §7 bullet*

   Axis label → 'pJ per load (one 8-byte ld; below L1 each brings a 64-byte line)'.
   Table header 'pJ/B' → 'pJ per byte of line'. L1 row prints '—': `${k === 'l1' ? '—' : fmt(e.sp_total / 64, 1)}`.
   Caption: 'pJ per 64-byte load above idle' → 'pJ per load (one 8-byte ld, which below L1 moves a 64-byte line) above idle'. Append 'An L1 hit moves no line; per byte the ld returns it costs 46/8 ≈ 5.7 pJ.'
   §7 bullet: 'about 59 pJ per 64-byte load' → 'about 59 pJ per load (per 64-byte line moved)'.

9. **[medium] anat-8** — *§7 intro; legend; KPI 'Energy of one DRAM load'*

   §7 intro: '(memory shires, DRAM, PHY, I/O)' → '(mostly the memory shires, DRAM, PHY and I/O, but also the regulators' delivery losses on the three metered rails: later work puts them at about 18–20% of the minion rail's power and 5–6% of the SRAM rail's, and part of the 26–29% it attributes to the mesh rail; see the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed'>hub's §4.2</a>)'.
   Legend → 'rest (board − rails; mostly DDR)'.
   KPI sub → '67% off the metered rails (mostly DDR), 18% mesh, 10% SRAM, 5% cores.'

10. **[medium] anat-9, nav-24** — *§1 'Out of reach' row; §9 third bullet*

   §1 → 'The first three need an M-mode syscall to choose events. One has since been written (about 60 lines) and works in the simulator, but the firmware images are signed, neither the signing tool nor a test key is available, and whether this card would boot a rebuilt image is untested, so it has not run on silicon; see the hub's <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#improve'>firmware caveat</a>.'
   §9 last sentence → 'A user-mode syscall that sets them has been written and works in sys_emu; running it on the card needs a signed firmware image, which is not available.'

11. **[medium] anat-10, nl-21, occ-m3** — *§2 map caption; §5 fit sentence*

   Caption → 'Map: marty1885's logical shire layout, as in the on-chip communication report. Grey cells are not compute shires (the master and spare shires and the PCIe and I/O shires). In this map memory shires 0–3 sit above the grid and 4–7 below it. The map appears to be the die turned a quarter: on the die (heat-per-millimetre report) and in the firmware's naming (0–3 west, 4–7 east) they are the two side columns.'
   §5 → 'Assuming each memory shire hangs one hop outside the grid (the only positions the fit tried; moving all eight one hop further out fits equally well with a constant of 79), the best fit puts memory shires 0–3 above the grid and 4–7 below it, at x = 1…4.'

12. **[medium] anat-11** — *KPI 'A DRAM load, typical'; end of §3*

   KPI sub → '500 ns at 600 MHz: median of 4,500 loads from shire 0 to random lines. Only ~25 cycles are DRAM timing; the rest is on-chip paths.'
   End of §3: 'The <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy'>memory-hierarchy report</a>'s pointer chase gave ~440 ns (421–486) for DRAM. The two are not directly comparable: that run's clock was not pinned (the governor moved it between 600 and 800 MHz) and its cycles were converted at the measured clock, while here every load ran at a steady 600 MHz (the refresh period in §6 folds to tREFI only at that clock).'

13. **[medium] anat-12, nav-24** — *§2 caption; §3; §8; §4; new section before §10*

   Link 'the on-chip communication report' to https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication, and 'the pointer chase measured before' and 'Manhattan distance on the mesh' likewise (memory hierarchy and on-chip communication).
   §8: after 'the carry into bit 7 lands 11 cycles late.' add 'The RTL shows why: twelve counters share one adder that folds overflows in round-robin, and a read ignores the pending overflow (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#bits'>hub §3</a>).'
   Add before §10 '<h2 id='related'>Related reports</h2><ul>':
   - Limits of observability, the hub: every instrument used here and what would extend it
   - Memory hierarchy: the pointer chase and bandwidth by level
   - On-chip communication: the shire map and 20 ns per hop for every shire pair
   - Energy manual §4: energy per byte at every level, with confidence bars, on two cards
   - Heat per millimetre: the energy of one mesh hop, split into flips and ones carried
   - One hot line stops a shire: uses the PA[10:6] home found here
   Close with </ul>.

14. **[medium] anat-13** — *after the lede; §6*

   Add <p class='small card'><b>The chip in one paragraph.</b> The ET-SoC-1's 32 compute <i>shires</i> sit on a 6×6 mesh network (the NoC). Each shire has 32 <i>minion</i> cores, each running two hardware threads (<i>harts</i>) and owning a small L1. Each shire's SRAM serves as its own L2 (512 KB), a scratchpad (2.5 MB) and a 1 MB slice of the chip-wide 32 MB L3. Every cache line has one L3 <i>home shire</i>, chosen by address bits, and DRAM sits behind eight <i>memory shires</i> (LPDDR4X controllers) at the edge of the mesh. Kernels run in user mode (U-mode); machine mode (M-mode) is the firmware's. The service processor (SP) is the management core that reads the power sensors. More in the hub's glossary.</p>
   §6: 'tRCD' → 'tRCD, the activate-to-read delay'; 'tREFI' → 'tREFI, the refresh interval'.

15. **[medium] anat-15, fr-11, nav-11, nav-12** — *workloads/memprobe/report_template.html (headings, byline, end of page)*

   Copy the byline's ' · part of the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability'>measurement reports</a>' into the template. It exists only in the built HTML, so a rebuild would drop it.
   Paste the shared template's section-anchor script, contents block and footer before </main>. Use its slugs rather than custom ids, because other pages link #where-the-energy-goes and #l3-110-cycles-plus-12-per-hop.

16. **[low] anat-14** — *§7 last bullet*

   → 'Totals from the host's board-power log are 16–25% higher than the trace's own board average for every pattern (16–19% for L2, own-shire L3 and both DRAM patterns; 23% for L1 and 25% for far L3).'

17. **[low] anat-16** — *§6 'How long a row stays open'*

   → 'That is about twice as fast as refresh alone would close rows (after 1,000 idle cycles, 23% hits against 44%). The controller's registers set an open-page policy with no idle-close timer (docs/research/counters-and-dram.md), so something else closes rows; this experiment cannot say what.'

18. **[low] anat-17** — *§5; ladder table dirty-evict row; §1*

   §5: 'The other seven shires' counts didn't move.' → 'The other seven shires' counts didn't move (one stray count of 1 in 448).'
   Table: min cell → `${D.ladder['tevict_dirty:3'].min}*`; row label → 'cost of evicting a dirty line + fence (not a load)'. Add under the table: '*One of 128 dirty evicts took 16 cycles, as fast as a clean one (no write-back); the rest took 112–480.'
   §1: 'Evicting a dirty line and fencing costs 150–480 cycles, the write-back.' → '…costs 112–480 cycles (median 241), the write-back.'

19. **[low] anat-18** — *§3 first paragraph*

   → 'Values are load-to-use cycles: the raw reading minus 5, an offset chosen so an L1 hit reads the 5 cycles the pointer chase measured. (A timed no-op and a timed L1 hit both read 10 raw; the offset moves every absolute number but none of the differences between levels.)'

20. **[low] anat-19** — *§2 explorer intro*

   Append: 'All loads were timed from shire 0; other requesting shires use the same 12 cycles per hop, which the on-chip communication report measured between every pair of shires.'

21. **[low] anat-20** — *§8 timer chart; §2 latency bar (drawFlame) and map*

   Before the timer chart add <div class='chart-title'>Cycles between two back-to-back counter reads, 4,000 pairs (dot size = count)</div>.
   Under the latency bar, render a legend of the segments (colour chip + name + cycles) built in drawFlame() from P.
   Map: draw a 7-swatch ramp legend (110, 130, …, 230+ cycles) and add to the caption 'each shade is 20 cycles of L3 latency'.

22. **[low] anat-21** — *§9 first two bullets*

   First bullet: add 'The hop cost is already known to be on the mesh clock: 20 ns per hop at 600, 700 and 800 MHz (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>on-chip communication report</a>), so only the 110- and 91-cycle constants remain to split.' Use 66 in place of 77 (see the DRAM-split change).
   Second bullet: add 'The <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>DVFS report</a> has since separated static from dynamic power another way, as a leakage law in temperature (23.3 W at 80 °C).'

23. **[low] anat-22** — *§1 'Board power' row; §8*

   'new value every ~130 ms' → 'new value every 133 ms'.
   'This isn't erratum RTLMIN-6496' → 'This isn't erratum 1.23 (RTLMIN-6496, two harts reading counters at once)'.

24. **[low] anat-23** — *§10 Reproduce*

   Add 'python3 ../../workloads/memprobe/gen_ops.py refresh --out . --n 24000 --start 0x1000' after the refresh_jit line.
   Replace the memprobe_host line with: for p in t_raw t_glitch ladder decomp msmap bits refresh refresh_jit pagetimeout; do timeout 10 ../memprobe/host/memprobe_host --program $p.ops; done   # each run < 0.2 s of card time
   Insert 'cd ../..   # back to the repo root' before run_power.py.
   Replace the last two lines with:
   - mkdir -p build/memprobe-data/power && python3 workloads/memprobe/analyze_power.py build/memprobe-power --json build/memprobe-data/power/summary.json
   - python3 workloads/memprobe/analyze.py --data build/memprobe-data --out build/memprobe-data/summary.json
   - python3 workloads/memprobe/build_report.py build/memprobe-data/summary.json docs/reports/2026-09-19-et-soc1-memory-anatomy.html

25. **[low] anat-m2** — *§2 explorer, L3 level rail cell (drawFlame)*

   For st.lvl === 'L3', add the per-hop rail increments to the cell (NoC += 47·h1, and the other rails from (l3far − l3near)/5.625 per hop). Otherwise label the cell 'Cores / SRAM / NoC / rest, own-shire L3 (each hop adds ~59 pJ, 47 of it NoC)'.

26. **[low] nav-13** — *template <title>; rebuild*

   Title → 'Anatomy of a memory access · ET-SoC-1'.
   Rebuild with build_report.py, redeploy to 2bf74fd1-fd7f-4e19-8e35-6168ae42657c, check visibility.

### 3.12 et-soc1-memory-hierarchy

Files: `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html`; `workloads/memhier/analyze.py`

1. **[high] mh-4, nl-4, nav-25, mh-3** — *under the byline / ET-SoC-1 spec-sheet table; lede; table energy and bandwidth columns; CMP['cmp-en']; 'What the numbers say' item 3*

   Insert under the byline:
   <p class='small card'><b>Update, 23–24 September.</b> This page averaged launches taken at 600–800 MHz, with the governor free. At a pinned 600 MHz the cycle counters give L1 about 6.2 TB/s, L2 2.45 TB/s (128 B per shire-cycle, not about 144), local scratchpad 2.46 TB/s, and L3 and remote scratchpad 0.96–0.98 TB/s (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points'>Ridge points</a>). Energy per byte was re-measured at 600 MHz on both cards in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy'>the energy manual, §4</a>: L1 0.77, L2 2.51, local scratchpad 2.52, remote scratchpad 6.65, L3 10.5, DRAM 122 pJ/B. At 600 MHz the L2 cache and the local scratchpad cost the same. The 128 GB/s the runtime reports is a placeholder constant in the service-processor firmware.</p>
   Lede: 'at 7–9× less energy per byte' → 'at about 15× less energy per byte (the energy manual's 600 MHz values)'; 'at roughly 1.4× the energy per byte' → 'at roughly 1.2× the energy per byte'.
   Put the 600 MHz values in the table and in CMP['cmp-en'] (1.76 → 0.77, 4.28 → 2.51, 2.83 → 2.52, 10.8 → 10.5, 148 → 122; tooltip 'energy manual, 600 MHz, two cards'), or strike the old ones through.
   Item 3 → 'The L2 scratchpad is the L2 without the tags. It has the same 47-cycle latency, goes through the read buffer and L1, streams at the same 4.0 B per minion-cycle, and at a pinned 600 MHz costs the same energy per byte (2.51 against 2.52 pJ/B, energy manual §4). The 4.3 against 2.8 pJ/B these runs showed came from the governor running the L2 runs at a higher clock.'
   Table note for local scratchpad → 'Same SRAM, latency and bandwidth as L2; also cached in L1 and the read buffer.'

2. **[high] mh-1** — *spec-sheet row 'L2 scratchpad, remote'; 'What the numbers say' item 4; heat-map caption and tooltip (renderHeat)*

   Latency cell → '112–220 cyc at 600 MHz · 186–366 ns'. Note → '20 ns per mesh hop (12 cycles at 600 MHz, 16 at 800 MHz), the same in both directions.'
   Item 4 → 'Distance on the mesh is visible. A remote scratchpad load costs 66 minion cycles plus 56 ns plus 20 ns per mesh hop: 186–366 ns at 600 MHz over 1–10 hops (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>on-chip communication</a> maps the hops). Row 31 → 0 reads 271 cycles against 220 for 0 → 31 only because the governor ran that row at 800 MHz. The L3 hides distance by spreading lines over every shire, so an L3 hit pays an average trip of about 280 ns.'
   Caption → 'The diagonal is the local scratchpad at 47 cycles. The governor ran rows 0 and 7 at 600 MHz, row 31 at 800 MHz, and row 24 at 600, then 700, then 800 MHz, so compare colours within a row. Each row steps 20 ns per mesh hop (12 cycles at 600 MHz, 16 at 800).'
   renderHeat tooltip: drop the ' ns at 600 MHz' conversion, or use each row's clock.

3. **[high] mh-2** — *'What the numbers say' item 6; DRAM row note*

   Item 6 → '<b>Being awake inflated these energy figures.</b> At a pinned 600 MHz, keeping all 1,024 minions busy adds about 2.2 W over idle with one hart running and 3.5 W with both (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#a-core-that-is-awake'>energy manual §2</a>; the on-chip communication report's one-hart spin loop on this card, the same day, added 2.7 W). In these runs the governor lifted the clock to 700–800 MHz and the minion voltage to about 0.6 V, and the die warmed against a single idle reading, so this page's two-hart spin loop added 12 W, and that floor is inside every energy per byte on this page. Re-measured at 600 MHz on two cards (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy'>energy manual §4</a>), a byte costs 0.77 pJ from L1, 2.5 from L2 or the local scratchpad, 10.5 from L3 and 122 from DRAM. The busy-core floor is then most of an L1 read, but only a fifth to a third of an L2, L3 or DRAM stream.'
   DRAM note → 'Energy is card power above idle, including the busy cores: about 2 W at 600 MHz, about 11 W at the 700–800 MHz the governor chose here.'

4. **[medium] mh-5, nl-3, vnav-m3, nl-2** — *DRAM KPI; L3 KPI; lede; 'What the numbers say' item 5 (line ~150); chart label 'DRAM ~440 ns'; CMP['cmp-lat'] DRAM row*

   DRAM KPI: value '~490 ns'; sub '287–297 cycles at 600 MHz; 420–455 ns when the governor ran at 800 MHz; 76 GB/s streaming'.
   L3 KPI sub → '159–169 cycles at 600 MHz (265–285 ns), depending on the requesting shire'.
   Lede → 'DRAM latency is about 490 ns at the 600 MHz base clock, a fifth more than the A100's HBM (405 ns), but the card streams 76 GB/s …'.
   Item 5: replace 'During the runs the telemetry showed the minion clock moving between 600 and 700 MHz (518–595 mV), and wall times imply up to about 850 MHz… That is why DRAM measured 287–368 cycles but a steadier 421–486 ns' with 'The chases were not accompanied by clock telemetry (a single poll during a separate spin saw 600–700 MHz at 518–595 mV), and the firmware's highest operating point is 800 MHz (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>the DVFS report</a>). The DRAM chases fall into two groups, 287–297 cycles (600 MHz) and 352–368 cycles (the governor's 800 MHz on a cool card). On-chip latencies are fixed in cycles. L3 and DRAM latency is part minion cycles and part fixed time in the 400 MHz mesh and 933 MHz memory domains: shire 24's L3 chases at 600 and 800 MHz fit 72 cycles + 147 ns, and all 18 DRAM chases fit 94 cycles + 323 ns. At 600 MHz that is 265–285 ns for L3 (depending on the requesting shire) and about 490 ns for DRAM; at 800 MHz about 238 and 440 ns. <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy'>Anatomy of a memory access</a> splits a 600 MHz DRAM load (299 cycles) into its parts.'
   Chart label and the cmp-lat DRAM row → ~490.

5. **[medium] mh-6, nl-4** — *spec-sheet bandwidth column and L2 note; CMP['cmp-bw']; Caveats 'The clock was not pinned'*

   Column → 'Bandwidth, whole chip, at 600 MHz': L1 '6.2 TB/s (5.2 B per hart-cycle)', L2 '2.45 TB/s (4.0 B per minion-cycle)', local scratchpad '2.46 TB/s (4.0 B per minion-cycle)', remote scratchpad '0.96 TB/s', L3 '0.98 TB/s', DRAM '76 GB/s'.
   L2 note → '128 B per shire-cycle by the cycle counters, half the four banks' 256 B/cycle.'
   Add to the caveat: 'The table uses only the launches that ran at 600 MHz. Averaged over all launches (0.62–0.74 GHz), the rates were 2–22% higher: L1 7.55, L2 2.80, local scratchpad 2.57, L3 1.03 TB/s.'
   Update CMP['cmp-bw'] to the same values.

6. **[medium] mh-7** — *workloads/memhier/analyze.py point_ghz() (lines ~31–40); #lat caption*

   Lower the threshold from wall_s >= 0.03 to >= 0.01, then re-run analyze.py --embed. This removes shire 24's false 314 ns L3 plateau.
   Caption → 'L3 and DRAM points use the clock implied by each chase's cycle count and wall time (600–800 MHz; the governor moved it), so a line can step within a level where the clock changed. At 600 MHz, L3 is 265–285 ns and DRAM about 490 ns.'
   Also fix the analyze.py comment '600-850 MHz' → '600-800 MHz'.

7. **[medium] mh-9** — *spec-sheet DRAM row (Notes, Capacity)*

   Notes → 'About 64% of the 119 GB/s that 16 × 16-bit channels carry at the 3,733 MT/s implied by the 933 MHz DDR clock. The 128,000 MB/s the runtime reports is a placeholder constant in the service-processor firmware.'
   Capacity → '32 GB LPDDR4X, 16 × 16-bit channels, 933 MHz DDR clock (3,733 MT/s)'.

8. **[medium] mh-8, nav-25, both-3, nav-14** — *before Sources; byline; heat-map caption; item 5*

   Add '<h2 id='related'>Related reports</h2>':
   - On-chip communication (the mesh map; 20 ns per hop at any clock; why scratchpad rows 24 and 31 read higher)
   - Anatomy of a memory access (L3 = 110 + 12 cycles per hop; a 600 MHz DRAM load of 299 cycles taken apart)
   - Energy manual §4 (these levels re-measured at 600 MHz, superseding the energy here)
   - Ridge points (the bandwidths at 600 MHz, per cycle)
   - The DVFS loop, and the leakage (the governor that moved the clock here)
   - Hand it to the next shire (the scratchpads used as a pipeline)
   - ← all reports
   Link 'mesh hops' in the heat-map caption to the on-chip page.
   Byline: 'Code: workloads/memhier in the nekko workspace.' → 'Code: <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/workloads/memhier'>workloads/memhier</a>; raw data: <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-09-18-memhier-aifoundry2'>docs/reports/data/2026-09-18-memhier-aifoundry2</a>.'
   In Reproduce, add one line: 'nekko is the lab-side checkout of this repository.'

9. **[medium] both-1** — *after the lede*

   Add a 'Terms' paragraph from glossary G (decisions): minion, hart, neighbourhood, shire and its SRAM split, scratchpad, mesh at 400 MHz, memory shires. Add 'The minions run at 600 MHz unless the power governor raises the clock.' End with a link to the hub's glossary.

10. **[low] both-2, nav-11, nav-12** — *all h2; before </main>*

   Paste the shared template's section-anchor script, contents block and footer.

11. **[low] mh-10** — *spec-sheet L3 note; item 4*

   'Lines are homed across all shires, so every L3 hit crosses the mesh.' → 'Lines are spread over all 32 shires, so 31 of every 32 L3 hits cross the mesh.' Item 4 wording as in the asymmetry change above.

12. **[low] mh-11** — *latency chart caption; dumbbell caption*

   'Gray segments' → 'Grey segments'; '(gray)' → '(grey)'.

13. **[low] nl-39** — *'What the numbers say', '27 W idle'*

   Give the die temperature with the idle figure (from the run's telemetry, e.g. '27 W idle at N °C') and add 'idle power follows 12.6 W + 23.3 W·e^((T−80)/36) (DVFS report)'.

14. **[low] nav-13** — *<title>; redeploy*

   Title → 'Memory hierarchy · ET-SoC-1'.
   Redeploy to 4b6e0a37-808d-4fc9-8001-555125733c46, check visibility.

### 3.13 et-soc1-on-chip-communication

Files: `docs/reports/2026-09-18-et-soc1-on-chip-communication.html`

1. **[high] noc-1, noc-8** — *'Energy per byte moved' caption; 'What the numbers say' items 6 and 7; KPI 'Energy per byte moved'; lede*

   Append to the energy caption: 'Every ring drew less power (1.5–2.5 W over idle) than the same cores spinning with no messages (2.7 W). So these figures are the cost of 1,024 cores kept busy by messaging, divided by the bytes they moved. The step at the shire boundary mostly mirrors the 7–34× drop in bandwidth, not costlier wires. The per-hop slope, 1.9 pJ/B, is close to the mesh's own cost measured with chosen bit patterns in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm'>Heat per millimetre</a> (1.4–2.2 pJ per byte per hop on board power); the ~10 pJ intercept is the cores.'
   Item 6: 'at 6–20× the energy per byte' → 'at 6–26× the energy per byte, mostly because the same ~2 W of busy cores moves 7–34× fewer bytes'.
   Item 7: 'A byte costs 0.8–20 pJ to move' → 'Messaging costs 0.8–20 pJ per byte, busy cores included'.
   KPI sub → '0.8–2.3 pJ inside a shire, busy cores included; ~10 + 1.9 pJ per hop across the mesh'.
   Lede: 'moving a byte costs 0.8–2.3 pJ inside a shire' → 'messaging costs 0.8–2.3 pJ per byte inside a shire, busy cores included'; '7–30× less message bandwidth' → '7–34× less message bandwidth'.

2. **[medium] noc-2** — *'What it means for systolic and wavefront designs', first bullet*

   Append: 'Over TensorSend a minion may have only one partner's ready outstanding (see the trap above). At shire grain that is easy to respect: give each neighbour link its own minion of the shire (a shire has 32), so no minion sends to or receives from two partners. A single minion that exchanges with two neighbours must take the directions in separate, barrier-separated phases; bulk tiles can go through the scratchpads instead (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay'>Hand it to the next shire</a>).'

3. **[medium] noc-3, nav-26** — *end of 'Energy per byte moved'; bandwidth table 'For comparison' row; energy chart reference bars (script rows.push); item 6*

   Add <p class='small'>Re-measured on 23 September with the die temperature in the idle bracket, three passes on each of two cards: pairs 0.67, rings in a shire 2.08, to the next shire ID 14.9 pJ/B; the 18 September values here read 2–20% higher (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-between-cores-and-shires'>the energy manual, §5</a>).</p>
   Reference rows → ['ET L2 read (energy manual, 600 MHz)', 2.51], ['ET scratchpad, 16 IDs away', 6.65], ['ET DRAM read (energy manual, 600 MHz)', 122]. Update the caption's 'from the memory-hierarchy report' to match.
   'For comparison' row → '0.96 TB/s' and '6.7 pJ'. Item 6 → '(0.96 TB/s at 6.7 pJ/B)'.

4. **[medium] noc-4, nav-26, both-3, nav-14** — *bandwidth table footnote; energy caption; item 2; trap section; systolic section; byline; before Sources*

   Wrap each 'memory-hierarchy report' / 'memory-hierarchy runs' in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy'>.
   Trap section: add 'The consequence for 2D systolic designs: <a href='https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation'>L2 mainline starvation</a>, last section.'
   Byline: 'Code: workloads/nocbench in the nekko workspace.' → a GitHub link to workloads/nocbench plus a raw-data link to docs/reports/data/2026-09-18-nocbench-aifoundry2.
   Add '<h2 id='related'>Related reports</h2>' before Sources:
   - Memory hierarchy (scratchpad and L3 rates, and the chase rows used in item 2)
   - Energy manual §5 (#bytes-between-cores-and-shires: these rings re-measured with bars on two cards) and §6 (#synchronisation: the energy of atomics and barriers)
   - Heat per millimetre (a hop's wire energy, 3.72 mm per hop)
   - Anatomy of a memory access (the same map; L3 = 110 + 12 cycles per hop; where the memory shires sit)
   - Hand it to the next shire (bulk data between shires through scratchpads, measured)
   - One hot line stops a shire (what a contended global-atomic flag does)
   - Ridge points
   - ← all reports

5. **[medium] both-1** — *after the lede*

   Add a 'Terms' paragraph from glossary G (decisions), plus: 'Minions are written shire.minion, so 0.0 → 0.1 is minion 0 of shire 0 sending to minion 1 of shire 0.' On first use, expand FCC ('fast credit counter') and CREDINC ('the register a core writes to add a credit to another core's counter'). End with a link to the hub's glossary.

6. **[low] noc-6, occ-1, nav-26** — *Sources, 'Energy' bullet*

   Replace the mesh-pitch sentence with: 'One hop is 3.72 mm (measured from the die plot in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm#die'>Heat per millimetre</a>), so 1.9 pJ per byte per hop is about 64 fJ/bit·mm. Measured since, with the bits on the links chosen: 47–73 fJ per random bit·mm on board power, the meter used here, and 36–50 on the mesh rail alone (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm#compare'>Heat per millimetre, §8</a>).'

7. **[low] noc-15, occ-m3** — *mesh map caption*

   'Each square is one physical position on the mesh' → 'Each square is one position on the mesh in marty1885's logical map (which appears to be the die turned a quarter)'.
   'The datasheet's full 8 × 6 mesh also has four memory shires on each side, not shown.' → 'The datasheet's full 8 × 6 mesh adds eight memory shires, not shown: in this map's orientation four sit above the top row and four below the bottom row, at x = 1–4 (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy'>Anatomy of a memory access</a>, §5).'

8. **[low] noc-7** — *lede first sentence; primitives table TensorSend GPU cell*

   Lede → 'An A100's SMs can reach each other only through L2; Hopper adds direct shared-memory access, but only within a cluster of up to 16 SMs.'
   Table → 'H800 (Hopper): a remote read of another SM's shared memory takes 103–121 ns, but only inside a cluster of up to 16 SMs.'

9. **[low] noc-9** — *'Latency grows with distance…' caption; primitives table 'Flag through memory atomics'*

   Use '590–1,150 ns (median 870 across shires)' in both places.

10. **[low] noc-10** — *systolic section, first bullet*

   'That sets the grain k ≈ t<sub>msg</sub>/t<sub>cell</sub>' → 'That sets the grain k ≈ 10·t<sub>msg</sub>/t<sub>cell</sub> cells per message for wavefront DP or lattice updates.'

11. **[low] noc-11** — *lede*

   'can send up to a full vector register file (1 KB) straight into another minion's registers' → 'can send up to 127 × 32 B (about 4 KB, cycling through its 32 vector registers) straight into another minion's registers'.

12. **[low] noc-12** — *energy caption; Caveats*

   'they agree within 5% for all but one configuration (13%)' → 'they agree within 6% for all but one configuration: the ring between shires s and s+16 (13%), which later work found slows the service processor that reads the meter on this card (see the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-chain'>hub, §4.1</a>)'.

13. **[low] noc-13** — *'What the numbers say' item 6*

   Nothing in the repo supports the marty1885 FlashAttention claim, so cut the sentence to: 'Across shires, bulk data moves better as TensorLoads from the other shire's scratchpad than as messages.' Keep the original only if the owner supplies the quote from Chang's post; it would then also need adding to docs/reports/sources/2026-09-18-gpu-on-chip-communication.md (findings group).

14. **[low] noc-14** — *'How it was measured', Lab etiquette; systolic section third bullet*

   'The chip was reset with the user's approval' → 'The chip was reset with the card owner's approval, and a health check passed before any further runs'.
   'Registers-to-registers messages' → 'Register-to-register messages'.

15. **[low] both-2, nav-11, nav-12, nav-13** — *all h2; before </main>; <title>*

   Paste the shared template's section-anchor script, contents block and footer.
   Title → 'On-chip communication · ET-SoC-1'.
   Redeploy to ab8e1b2b-de17-44f4-8645-006fa960e349, check visibility.

### 3.14 et-soc1-matmul-efficiency

Files: `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html`; `scripts/mmbench-power.py (optional)`

1. **[high] matmul-1, matmul-2, nav-02, nl-15** — *lede; new note under the lede; 'Inputs and checking'; 'Energy efficiency against the A100' caption; Caveats first bullet*

   Lede: '3.4× more energy-efficient at full fp32 precision' → '3.4× more energy-efficient at full fp32 precision on these ±1/±2 operands (about 2.9× in a later random-data measurement of the tensor unit at 80 °C)'.
   Insert after the lede:
   <p class='small'><b>Later measurements.</b> These operands favour low power: every input is ±1 or ±2, whose mantissa bits are all zero, and the die was at 71–77 °C. <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment'>The Horace experiment</a> later showed how much the data matters. At 80 °C the tensor unit draws 38 W on zeros, 47 W on ones, 51–53 W with only the signs or only the exponents random, and 63 W on random-normal values; random mantissas are the costliest bits. In a variant of this loop with both operands in the L1 scratchpad (546 cycles per op rather than 529), random-normal fp32 at 80 °C gave 9.18 TFLOP/s at 63.9 W. That is 144 GFLOP/s per W, and fp16 gave 301 (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#the-tensor-unit-per-multiply-add'>energy manual §3.2</a>): about 2.9× the A100 SXM4's fp32 spec ratio rather than 3.4×. <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power'>Why is the ET-SoC-1 low power?</a> sets this card's fp32 against an A100 running bf16 on its tensor cores and finds the A100 about five times better per FLOP; the 3.4× here is fp32 against the A100's fp32 datasheet figure, and against its tensor cores the table below gives 0.41–0.75×.</p>
   Inputs and checking: append 'Small powers of two keep the multipliers' mantissa bits at zero, so these operands draw less power than random data would.'
   Caption: replace 'which flatters the A100: real GEMMs run below peak while drawing close to TDP' with 'One measured A100 run lands on the same ratio: Horace He's 8192³ bf16 matmul on random data ran at 257 TFLOPS under a 330 W power limit, 779 GFLOP/s per W against the spec sheet's 780.'
   Caveat 1: replace 'Large GEMMs on an A100 typically reach 80–90% of peak while running near the power limit, so its delivered efficiency is lower than these ratios. The ratios here are a best case for the A100.' with 'The one measured A100 matmul these reports use (Horace He: bf16, random data, 257 TFLOPS under a 330 W limit) matches peak ÷ TDP. For the tensor cores these ratios are therefore a fair estimate, not a best case; no A100 fp32 CUDA-core GEMM was measured. Like for like on random data, this card's fp16 TensorFMA costs 3.3 pJ per FLOP at the board (energy manual §3.2, 80 °C) against the A100's 1.3 pJ in bf16, 2.6×, close to the 2.4× above.'

2. **[medium] matmul-3, nl-39** — *results table 'Per W above idle' column and note; Idle KPI sub; Caveats second bullet; scripts/mmbench-power.py*

   Per W above idle → 366 / 711 / 2,571 / 38.
   Table note: 'Above idle subtracts the idle measured in the gap just before each workload (30.6, 32.5, 33.8 and 35.2 W): the die warmed from 71 to 77 °C over the session, and its leakage with it.'
   Caveat → 'Board power includes the whole card. Of the 30.6 W idle, about 12.6 W is fixed (DRAM, PCIe, I/O, regulators) and the rest is die leakage, which grows with temperature. The idle law in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>The DVFS loop, and the leakage</a> predicts 30.8 W at the 71 °C this run started at and 34.0 W at 77 °C. The above-idle column still carries the leakage added as the die warms within each run, so it is not the compute alone.'
   KPI sub: 'more than half of the load power' → 'about half of the load power, mostly die leakage at 71 °C'.
   Optional: make mmbench-power.py record the idle before each workload.

3. **[medium] matmul-4, nav-02, nav-14** — *before 'Reproduce'; Next steps; byline*

   Add <h2>Related reports</h2><ul>:
   - The Horace experiment: the same TensorFMA's power on 14 operand patterns at 80 °C
   - Why is the ET-SoC-1 low power?: energy per FLOP against a measured A100
   - Energy manual §3.2: pJ per multiply-add by type and data
   - The DVFS loop, and the leakage: why idle power depends on temperature
   - Ridge points: the reuse each memory level demands to keep this loop fed
   - Sparse compute: what the tensor unit skips
   - Test drive: the first scalar SGEMM and the laptop setup
   Close with </ul>.
   Next steps, third bullet → 'A vector-unit fp32 baseline (its energy per lane is now in the energy manual §3.1; its speed is FOSDEM's 2.94 TFLOP/s). The clock/voltage points were measured later in The DVFS loop, and the leakage.'
   Byline: link kernels/mmbench to https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/kernels/mmbench, and 'the nekko workspace' → 'the project repository'.

4. **[low] matmul-5** — *h1; section order; 'The loop' bullet*

   h1 → 'ET-SoC-1 matmul on silicon: 91–97% of the tensor unit's peak, and its energy against the A100'. Keep <title> as 'Matmul efficiency · ET-SoC-1'.
   Move 'How the benchmark works' above 'What I did'. Rename 'What I did' to 'Setup notes (for running it yourself)', with a lead-in linking Test drive.
   In 'The loop' add: 'minions are the chip's small RISC-V cores, 32 to a shire; hart 0 is the first of each minion's two hardware threads; the L1 scratchpad is part of the minion's 4 KB L1 cache; TenB streams the B operand from memory'.

5. **[low] matmul-10** — *Caveats 'One clock point'*

   First sentence → 'One clock point. This run stayed at 600 MHz (0.52 V) because the die started at 71 °C: aifoundry2's governor raises the clock to 700 or 800 MHz (0.57 or 0.62 V) only when the die starts below 65 °C (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>The DVFS loop, and the leakage</a>). Other operating points change both speed and efficiency.'

6. **[low] matmul-6** — *'A100 reference' table*

   Move the '÷ 250 W (PCIe 40 GB)' column into the table note: 'On the 250 W PCIe card the A100 ratios are 1.6× higher: 78, 624, 1,248, 2,496.'
   Shorten headers to 'A100 peak', 'A100 per W (SXM4)', 'ET per W', 'ET ÷ A100 efficiency', 'A100 ÷ ET speed'. Give the first column min-width 150px.

7. **[low] matmul-7** — *A100 reference table note*

   'The A100 also has 1.6–2.0 TB/s of HBM, about 20× the ET card's LPDDR4X.' → 'The A100 sustains 1.4–1.8 TB/s from HBM (40 and 80 GB cards; 1.6–2.0 TB/s peak), about 20× the 76 GB/s this card streams from LPDDR4X.'

8. **[low] matmul-8** — *'Board power during the benchmark' caption*

   'minion shires went from 71 °C to 77 °C, peaking at 85 °C' → 'minion-shire temperature (the sensors' average) went from 71 °C to 77 °C; the hottest sensor's high-water mark read 85 °C afterwards'.

9. **[low] matmul-9** — *'The loop'*

   'only hart 0 may issue tensor ops, so hart 1 idles' → 'only hart 0 may issue TensorFMA and TensorLoads into the L1 scratchpad, so hart 1 idles'.

10. **[low] nav-11, nav-12, nav-13** — *all h2; before </main>; <title>*

   Paste the shared template's section-anchor script and footer.
   Title → 'Matmul efficiency · ET-SoC-1'.
   Redeploy to 590752c1-17a8-4f5d-97ef-bcf33fd6a3e7; it must stay public (Q40).

### 3.15 et-soc1-sparse-compute

Files: `docs/reports/2026-09-18-et-soc1-sparsity.html`

1. **[high] sparse-1** — *lede; KPI 'Power saved by zero-skip'; §1 intro and note; 'What these measurements change' bullet 1; Caveats bullet 3*

   Lede: after 'in a loop of TensorFMAs' insert ' on small-integer operands (on random data the same loop draws about 25 W above idle; see the note under the power chart)'.
   KPI sub → '+17.3 W → +2.4 W above idle in a TensorFMA-only loop, operands −3…3 (3.8 → 0.5 pJ per multiply slot); 80–92% for constant to random data in later runs'.
   'In this loop about 86% of the op's dynamic power follows the nonzero count.' → 'In this loop about 86% of the power above idle follows the nonzero count (96% of the tensor unit's own 15.6 W).'
   'Inputs were small integers' → 'Inputs were nonzero integers from −3 to 3, plus the zeros under test'.
   After the §1 intro paragraph insert:
   <p class='note'><b>Later measurements.</b> Power depends on the operand values, not only on how many are zero. On this same card and loop (546 cycles per op, B in the L1 scratchpad), temperature-controlled runs four days later measured +1.9 W over idle with every operand zero, +9.7 W on all ones and +24.9 W on random normal data (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment#a-second-card-and-what-transfers'>the Horace experiment</a>, §10). Per multiply-add that is 0.41, 2.1 and 5.4 pJ (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#the-tensor-unit-per-multiply-add'>energy manual §3.2</a>). So zero-skip saves 80–92% of the loop's power above idle, depending on the data, and the Horace experiment traces the rest to register clocking and bit flips. This page's all-zero point (+2.4 W) zeroed only A and was read without the later runs' temperature correction, so the two zero figures are not directly comparable.</p>
   Bullet 1 and caveat 3: 'about 86%' → 'about 86% here, 80–92% from constant to random operands'.

2. **[medium] sparse-2** — *paragraph after the masked-load chart; 'Where the A100 wins' bullet 1; 'What these measurements change' bullet 3; Caveats bullet 4*

   'The loads therefore hit memory in a sparse, regular pattern that apparently costs nearly as much as reading every line. The cause is not established here (see Caveats).' → 'These masks keep the same low rows of every block, so every kept line is homed in the same few shires' L3 slices (see Caveats). Masks that vary from block to block were not tested.'
   Caveats bullet 4 → 'The flat DRAM time under a mask is probably caused by which lines the masks kept. A line's L3 home shire is physical-address bits 10:6 (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy'>Anatomy of a memory access</a>), and these masks keep the same low lines of every 1 KB block, so all 1,024 minions' misses land on 16, 8 and 2 of the 32 home shires (and at 4 and 1 lines on 4 and 1 of the 8 memory shires). Per home shire the chip streams 2.3–2.6 GB/s at every mask. A mask that rotates from block to block would test this.'
   'Where the A100 wins': 'Masked loads do not help once the whole chip streams from DRAM, as measured above.' → 'Masks that keep the same rows of every block did not help once the whole chip streamed from DRAM, and even a perfect mask cannot lift 76 GB/s.'
   Bullet 3: after 'but not when the whole chip streams from DRAM' add '(with the same rows kept in every block)'.

3. **[medium] sparse-3** — *'Divergence' paragraph under the charts; Caveats*

   'The loop is limited by instruction issue and by the mask-to-branch round trip; hand-tuning might give 2×, not 10×.' → 'What limits the loop was not measured, and the shared work queue may be part of it. A contended global atomic retires one operation every 10 cycles (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line'>One hot line stops a shire</a>). The 16,384 chunk grabs plus each hart's final empty grab need about 184,000 cycles of it, more than the average hart's whole run without divergence (173,000 cycles) and over 80% of it at α = 3, but only about half at α = 1.5–1.2. An 8-lane iteration also costs 84 cycles against 33 for a one-lane scalar iteration, so mask bookkeeping costs too. The scalar variant, which uses the queue at a third of the rate, held 0.30 T/s at every α. Larger chunks or one queue per shire would separate the two.'
   Add a caveat: 'All divergence runs draw work from one global atomic counter. Without divergence and near α = 3 it was busy for most of the run at the ceiling later measured for a contended atomic, so the 0.9 T/s peak may be partly the queue's.'

4. **[medium] sparse-4** — *batch-1 layer chart legend and 'Against the A100' paragraph*

   Legend → 'A100: one isolated launch + empty kernel (measured)'.
   'so the reference lines are bounds' → 'so the reference lines are rough references, not bounds'.
   After the sentence on the 1.44 µs kernel add: 'Kernels queued back to back in a stream cost less, about 1.5 µs each on an A100 (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>on-chip communication report</a>).'
   Bold clause → '<b>ET-SoC-1 reaches A100-class latency on one layer. It beats a single isolated A100 launch (3.7 µs) only at very high sparsity, and never gets under the ~1.5 µs of a queued A100 kernel except when x is all zeros.</b>'

5. **[medium] sparse-5, nav-27, nav-14** — *byline; first mentions of companion reports; before Sources*

   Byline: 'Code: <code>workloads/sparsity</code> in the <code>nekko</code> workspace.' → 'Code: <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/workloads/sparsity'>workloads/sparsity</a>; raw data: <a href='https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-09-18-sparsity-aifoundry3'>docs/reports/data/2026-09-18-sparsity-aifoundry3</a>.' Point the hub link at …#reports.
   Link the first mention of each companion: 'the matmul report' → et-soc1-matmul-efficiency; 'the memory-hierarchy report' → et-soc1-memory-hierarchy; 'on-chip communication report' (each) → et-soc1-on-chip-communication.
   'measured on the sister card' → 'measured on aifoundry2'.
   Add <h2 id='related'>Related reports</h2>:
   - The Horace experiment (why the tensor unit's power depends on operand values, not only zeros)
   - Energy manual §3.2 (temperature-corrected pJ per multiply-add, two cards)
   - On-chip communication (sync, allreduce and messaging costs used in the scenarios)
   - Memory hierarchy (76 GB/s DRAM; L2, L3 and scratchpad sizes)
   - Anatomy of a memory access (the address map behind the masked-DRAM result)
   - Matmul efficiency (tensor ops with B streamed through TenB, 9.5 TFLOP/s)
   - Ridge points (where this layer sits against the bandwidth ceilings)
   - One hot line stops a shire (the global-atomic ceiling behind the divergence queue)
   - Why is the ET-SoC-1 low power?

6. **[medium] sparse-7, nav-27** — *§3 and §4 first sentences; section 'What these measurements change in the starting brief'*

   'This is the case the brief ranked as most relevant to ML' → 'This is the case most relevant to ML'.
   'The second brief proposed a divergence sweep.' → 'The second question is divergence.'
   Heading → <h2 id='answers'>Answers to the questions this work started from</h2>, opened with 'The work began from two research briefs (not published); these are their questions and what the measurements say.'
   Delete ', as the brief suspected'.
   'The brief's per-step budget of ≤ 10 µs' → 'A per-step budget of ≤ 10 µs'.
   'the fact-checked literature' → 'the published literature'.
   Delete the whole 'Literature corrections found by the fact-check' sub-list, or replace it with the single line 'Every literature figure in the scenario table was checked against its paper.' If RTLflow is no longer cited, drop it from Sources.
   TensorSend bullet → 'TensorSend works across shires (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>on-chip communication report</a>, "A trap: one ready flag per minion"). A hang in that work came from a minion changing partners without a barrier: …'

7. **[medium] sparse-8** — *after the KPI cards; 'A per-memshire sweep'; first 'GPop/s'*

   Add <p class='small'><b>Terms.</b> The chip's 1,024 compute cores are <i>minions</i>. Each has two hardware threads (<i>harts</i>), an 8-lane vector unit and a tensor unit. 32 minions form a <i>shire</i>, which shares 4 MB of SRAM: a 512 KB L2 cache, a 2.5 MB scratchpad and a 1 MB slice of the chip-wide 32 MB L3. Shires talk over a 6×6 mesh, and 8 <i>memory shires</i> drive the DRAM. <i>TensorFMA</i> is the tensor unit's matrix multiply-accumulate (16×16×16 in fp32, 16×16×32 in fp16, 16×16×64 in int8). <i>TensorLoad</i> fills the minion's L1 scratchpad, and <i>TenB</i> is the path that streams the B matrix from L2 instead. A <i>multiply slot</i> is one of an fp32 op's 4,096 multiply-adds, zero or not. More in the hub's glossary.</p>
   'A per-memshire sweep' → 'A sweep per memory shire'.
   First 'GPop/s' → 'GPop/s (GP node evaluations per second)'.

8. **[low] sparse-10, nav-11, nav-12** — *headings; lede; scenario table (table.wide min-width 780px)*

   Paste the shared template's section-anchor script, contents block and footer.
   Retitle the first h2 'Zeros save power, never cycles'.
   Split the lede into a two-sentence lede plus three bullets: zero-skip; the layer; where it wins and loses.
   Turn the scenario table into six h3 subsections, each with four labelled lines: why a GPU struggles, published baseline, ET estimate, benchmark.

9. **[low] sparse-11, nl-2** — *Caveats bullet 2*

   → 'One card, one day. aifoundry3 held 600 MHz throughout; later work found why: its firmware reports a TDP of 0 W, so its governor can never raise the clock (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>The DVFS loop, and the leakage</a>). Its sister card aifoundry2 runs at 600, 700 or 800 MHz depending on die temperature. Cycle counts carry over between the cards; switching power on aifoundry3 runs about 8% below aifoundry2's for the same work (Horace experiment §10), and idle power differs with die temperature.'

10. **[low] sparse-12, nl-37** — *note under the TensorFMA chart; 'What these measurements change' last-but-one bullet*

   Note → 'One minion, A and B held in the L1 scratchpad. With B streamed from L2 through TenB, as in the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency'>matmul report</a>, an fp32 op takes 529 cycles, also flat (that report's int8 op takes 280 that way, against 318 here). All 1,024 minions at once: 546.1.'
   Bullet parenthesis → '(9.2 TFLOP/s with B held in L1 as here; 9.5 TFLOP/s with B streamed through TenB in the matmul report)'.

11. **[low] sparse-13** — *caption under the layer table*

   Append: 'The slowest of the 64 blocks averaged 7.62 µs dense and 2.22 µs at 99% zeros, and a layer is not finished until its slowest block is. Results stay in each block's root registers; writing y out is not included.'

12. **[low] sparse-14** — *'Three effects add up' paragraph*

   After 'about 12%' add ' (the dense-x point is the masked kernel, which with no zeros also loads every row; the plain kernel at 0% was not in the energy run)'.

13. **[low] sparse-15** — *scenario table header*

   'A100 baseline (published)' → 'Published baseline (A100 where one exists)'.

14. **[low] sparse-16** — *'Where the A100 wins' bullet 2; §1 intro; §3*

   Bullet → '2:4 structured sparsity also favours the A100: it doubles tensor-core math (1.5–1.9× measured on large GEMMs), but it needs pre-pruned static weights and does nothing for dynamic activation zeros at batch 1.'
   'The manual describes three sparsity hooks.' → 'The manual describes three sparsity hooks: zero-skip in TensorFMA, and tensor_mask on TensorFMA and on TensorLoad. The table adds fp16 and int8, which behave differently.'
   '(16 MB of weights)' → '(16.8 MB of weights)'.

15. **[low] sparse-9** — *paragraph after the zeros charts (erratum parenthesis)*

   → '(On A0 silicon, erratum 1.29 type D rules out some small fp32 and fp16 ops whose ACOLS field is nonzero: 4-row ops with B in the L1 scratchpad, and 1- to 4-row ops with B streamed through TenB. AROWS and ACOLS are the op's row and column counts minus one.)'

16. **[low] sparse-17** — *renderGemv row list*

   Add ["dense", "Every row loaded, compute only"] after the 'Masked + skip, compute only' entry. The table then shows the 6.78 µs that Ridge points quotes.

17. **[low] sparse-tl-caption** — *caption under the all-1,024-minion TensorLoad table*

   → 'Cycles per load, mean over the 1,024 minions. In brackets, the bytes the mask let through per second over the whole chip, using the slowest minion's total time at 600 MHz (so they are a few percent below what the mean cycle count implies).'

18. **[low] sparse-18** — *Sources*

   Make each arXiv ID a link (https://arxiv.org/abs/<id>): 2504.11750, 2411.01137, 2402.13499, 2310.17157, 2408.14690, 2104.08378, 2301.00774, 2008.08478, 2301.09413, 2403.04714, 2503.06757, 2310.17274, 2501.17168. Add https://hazyresearch.stanford.edu/blog/2025-05-27-no-bubbles. Cite QuickScorer, Lettich et al. and Parendi in the scenario text, or drop them.

19. **[low] nav-13** — *<title>; redeploy*

   Title → 'Sparse compute · ET-SoC-1'.
   Redeploy to 5abf6014-8de0-4e82-8744-5676bac6453e, check visibility.

### 3.16 et-soc1-ridge-points

Files: `docs/reports/2026-09-18-et-soc1-ridge-points.html`; `scripts/ridge-points.py`

1. **[high] ridge-1, nl-38, nav-28, ridge-energy** — *'Energy balance points' intro, table t-energy, caption and following paragraph; byline; scripts/ridge-points.py (e_flop, e_byte)*

   In ridge-points.py:
   - e_flop from docs/reports/data/2026-09-23-energy-manual/manual.json tensor.bars.fp32_randn.mean/2 (2.889) and tensor.bars.int8_randn.mean/2 (0.158); not tensor.rows, which is aifoundry2 only;
   - e_byte from reruns.json levels_pj_per_byte.<level>.mean and rings_pj_per_byte (pair 0.67, shire 2.08, cross-shire 11.87–17.77).
   Then re-run with --embed. Table (pJ/B · fp32 · int8):
   - L1 0.77 · 0.27 · 4.9
   - own scratchpad 2.52 · 0.87 · 16
   - L2 2.51 · 0.87 · 16
   - remote scratchpad 6.65 · 2.3 · 42
   - L3 10.5 · 3.6 · 66
   - DRAM 122 · 42 · 771
   - TensorSend fast local network 0.67 · 0.23 · 4.2
   - TensorSend inside a shire 2.08 · 0.72 · 13
   - TensorSend between shires 11.9–17.8 · 4.1–6.2 · 75–112
   Intro, last sentence → 'On random-normal operands held in the L1 scratchpad, the fp32 tensor unit costs 2.89 pJ per FLOP above idle [2.62–3.01] and int8 0.158 pJ per OP (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#the-tensor-unit-per-multiply-add'>energy manual §3.2</a>, both cards, pinned 600 MHz). The data matters as much as the level: on all-ones operands fp32 costs 1.11 pJ per FLOP and on zeros 0.21, so every balance point below moves by up to 14× with the operands.'
   'That does not hold at the spec rates: the L2 cache's 2.3 FLOP/B is above its spec ridge of 2.0, and L3's 5.7 is above 3.0.' → 'At the spec rates only L3's 3.6 FLOP/B lies above its ridge of 3.0.'
   Replace the caption and the sentences from 'The two sides also come from different runs' to 'Treat these as rough.' with: 'Energy per byte for memory is the energy manual's §4.2: the same 1 KB TensorLoad probes as the bandwidths above, re-run at a pinned 600 MHz on both cards on 23 September. For TensorSend it is §5. The 18 September figures (memory-hierarchy report, clock free, busy-core floor of about 12 W) are superseded. The §4.2 probes read whatever the buffers held, not random data. On random data a TensorLoad costs 4.21 pJ/B from the shire's own scratchpad and 129 pJ/B from DRAM (§4.1), which puts those balance points at 1.5 and 45 FLOP/B.'
   Byline: keep 'Computed 18 Sep 2026' and add '; published 24 September 2026'. Change 'from existing data, with no new runs' to 'from the 18 September measurements and the 23 September energy manual, with no new runs'.

2. **[medium] ridge-2** — *'Ridge points by level' DRAM and own-shire bullets; 'A lone minion'; Caveats bullets 3–4*

   DRAM → 'Measured at 76 GB/s on both cards (75.8–76.0 GB/s in the 23 September reruns at a pinned 600 MHz; the sparsity report's shorter probe read 72 GB/s on aifoundry3).'
   Own shire → 'The 23 September reruns of the same probe at a pinned 600 MHz gave 4.00 B per cycle for both on aifoundry3 as well; only the sparsity report's shorter L2 probe read 3.3–3.5.'
   Lone minion: 'at least 86–90 minions … the chip's 72–76 GB/s' → 'at least 90 minions … the chip's 76 GB/s'.
   Caveat 3, second sentence → 'The levels beyond the shire use the 600 MHz launches of the 18 September runs; the 23 September reruns at a pinned 600 MHz on both cards reproduce every level to within 0.3%.'
   Caveat 4 → 'Both cards give the same bandwidth at every level with the same probe; aifoundry3 also supplied the sparsity report's TensorLoad-size and batch-1 measurements.'

3. **[medium] ridge-8** — *Caveats, second bullet*

   → 'These are read ridge points. Writes were measured later (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy'>energy manual §4.1</a>, both cards): tensor stores reach 1.23 TB/s into the shire's own scratchpad, half the read rate, and 76 GB/s to DRAM, the same as reads; stores through the L1 reach DRAM at only 27 GB/s. A kernel that writes as much as it reads needs more reuse than these tables show.'

4. **[medium] ridge-3, nav-28, sparse-5, nav-14** — *byline; notes; Sources items 1–7; new section before Sources*

   Link first mentions: 'the matmul report' → et-soc1-matmul-efficiency; 'the memory-hierarchy report' → et-soc1-memory-hierarchy; 'the sparsity report' (all mentions, lines ~143, ~166) → et-soc1-sparse-compute; 'the on-chip communication report' → et-soc1-on-chip-communication.
   Byline: 'in the nekko workspace' → 'in the project repository (<a href='https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/scripts/ridge-points.py'>scripts/ridge-points.py</a>)'. Link the A100 source path to its GitHub blob URL.
   Sources: link et-man (https://github.com/aifoundry-org/et-man; the datasheet ships there), core-et (https://github.com/openhwfoundation/core-et/tree/erbium), and the Hot Chips 33, IEEE Micro, FOSDEM and A100 datasheet PDFs; sibling pages already carry these URLs. For M. Chang's blog use the clehaxze.tw original.
   Add <h2>Related reports</h2>:
   - Matmul efficiency
   - Memory hierarchy, On-chip communication, Sparse compute
   - Energy manual §3.2, §4.2, §5
   - The Horace experiment (why energy per FLOP depends on the data)
   - Hand it to the next shire (the remote-scratchpad ridge in practice)

5. **[medium] ridge-4** — *after the KPI note*

   Add <p class='small'><b>The chip in brief.</b> The ET-SoC-1 has 1,088 <i>minions</i>: small in-order RISC-V cores, each with two hardware threads (<i>harts</i>), an 8-lane vector unit and a tensor unit. 1,024 of them run user kernels. Eight minions form a <i>neighbourhood</i> and four neighbourhoods a <i>shire</i>. Each shire has 4 MB of SRAM, split into a 512 KB L2 cache, a 1 MB slice of the chip-wide L3 and a 2.5 MB software-managed L2 scratchpad. Shires are joined by a mesh network on chip (NoC), clocked at 400 MHz on these cards; DRAM is 32 GB of LPDDR4X on 16 channels. A TensorLoad copies up to 1 KB into the minion's L1 scratchpad (carved out of its 4 KB L1 data cache). A TensorFMA multiplies a 16×K A tile from there by a B tile streamed through the TenB buffer, accumulating a 16×16 C tile in the vector registers (int8 accumulates in a separate buffer, TenC). TensorSend moves data register to register between minions.</p>

6. **[medium] ridge-5** — *table t-ridge (table.ridge min-width 980px) and t-energy*

   Split t-ridge into 'Measured' (Level, Size, Bandwidth, fp32, fp16, int8) and 'Spec and clock' (Level, Bandwidth spec, Spec ridge fp32 · fp16 · int8, Does the ridge grow with the minion clock?). Set table.ridge min-width to 0.
   Shorten t-energy headers to 'pJ/B', 'fp32 balance', 'int8 balance', 'fp32 time ridge' so it fits 908 px.

7. **[low] ridge-6, nav-11, nav-12** — *all headings; before </main>*

   Paste the shared template's section-anchor script, contents block and footer. This gives ids and a contents list for the 10 h2s.

8. **[low] ridge-7** — *'Inference that streams its weights'; t-ridge bandwidth cells and headers*

   → 'A layer that reads its weights once per batch of N inputs does 2N operations per weight, or 2N/e per byte (e = bytes per element). It is compute-bound when that reaches the ridge, so it needs N ≥ e × ridge / 2.' Update 'H/s' and 's·K·(m + n)' to 'H/e' and 'e·K·(m + n)'.
   Format bandwidth cells as '4.00 B/cycle · 2.45 TB/s'.
   Header → 'Does the ridge grow with the minion clock?'.
   Best measured → '15.49 FLOP/cycle (97%)'.

9. **[low] matmul-9** — *'The compute ceilings'*

   → 'Only hart 0 of a minion may issue TensorFMA (hart 1 can only prefetch into the L2 scratchpad), and the vector unit's fmadd.ps runs on the same FMA units.'

10. **[low] nav-13** — *<title>; redeploy*

   Title → 'Ridge points · ET-SoC-1'.
   Redeploy to dd341b0b-a52e-4e23-b8b3-101a83119133, check visibility.

### 3.17 et-soc1-testdrive

Files: `docs/report/index.html`

1. **[medium] td-1, nav-29** — *'Next' section; step 3 of 'What I did'*

   Rename 'Next' → 'Next (as planned on 18 September)'.
   After it add '<h2>What came next</h2><ul>':
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency'>Matmul efficiency</a>: the tensor unit on all 1,024 minions (aifoundry2), 9.5 TFLOP/s fp32 (97% of the fp32 peak at 600 MHz), 19.0 fp16 and 71.8 TOP/s int8, and energy against the A100
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy'>Memory hierarchy</a> and <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>On-chip communication</a>: what the next kernels have to live with
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay'>Hand it to the next shire</a>: the scratchpads used as a pipeline
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports'>All the measurement reports</a>
   Close with </ul>.
   Step 3: append '(gp-sdk was later built in the workspace on the lab machines with scripts/deploy-lab-gpsdk.sh; /opt/et itself still has none.)'

2. **[low] td-2** — *after the lede; footer*

   Add <p class='secondary'>The ET-SoC-1 is Esperanto's 1,088-core RISC-V accelerator, now open-sourced by AI Foundry. Kernels run on 32 compute <i>shires</i> of 32 <i>minion</i> cores; each minion runs two hardware threads (<i>harts</i>), so a full launch is 2,048 harts.</p>
   Footer → 'aifoundry3 used its /opt/et: et-platform 353f20e (December 2025), runtime 0.19.0, GCC 15.1; that card runs its minions at 600 MHz.'

3. **[low] nav-13, nav-14, nav-11** — *<title>; byline; headings*

   Title → 'Test drive · ET-SoC-1'.
   Move the hub link into the byline as '· part of the ET-SoC-1 measurement reports'.
   Paste the section-anchor script and footer.
   Redeploy to 16732875-c03e-434d-a643-7a432586c7f7.

### 3.18 findings: docs/findings/*.md, docs/getting-started.md and other repo notes

Files: `docs/findings/README.md`; `docs/findings/01-resources.md`; `docs/findings/02-requests.md`; `docs/findings/03-experiments.md`; `docs/findings/04-artifacts.md`; `docs/findings/05-claims.md`; `docs/findings/10-data-dependent-power.md`; `docs/findings/11-thermal-model.md`; `docs/findings/12-heat-management.md`; `docs/findings/13-why-low-power.md`; `docs/findings/14-card-behaviour.md`; `docs/findings/15-earlier-findings.md`; `docs/findings/16-dvfs-and-leakage.md`; `docs/findings/17-hot-line.md`; `docs/findings/18-on-chip-relay.md`; `docs/findings/19-observability-and-the-unmetered.md`; `docs/findings/20-heat-per-mm.md`; `docs/getting-started.md`; `README.md (repo root)`; `docs/et-soc1-notes.md`; `docs/research/why-low-power.md`; `docs/reports/sources/2026-09-18-gpu-on-chip-communication.md`

1. **[high] fr-1, nav-08** — *getting-started.md §5 (lines ~245–249), §8 'Publishing', lines ~72 and ~81; README.md (root) lines 25, 29, 33, 38, 57, 82, 110, 120 and 87–88*

   getting-started §5: replace the share line with 'npx --yes spacesheep share 590752c1-17a8-4f5d-97ef-bcf33fd6a3e7 --visibility public' and the comment with '# confirm the visibility column still says public (Q40: every space the hub links is public)'.
   getting-started §8 → 'Publishing. Every space the hub links is public (Q40). Update one in place with its uuid from docs/findings/04-artifacts.md … Afterwards run npx spacesheep list and check the visibility against docs/findings/04-artifacts.md.'
   getting-started lines 72 and 81: 'published privately at' → 'published at'.
   Root README: every 'private space' / 'Private space' → 'public space'.
   Root README lines 87–88 → 'After any spacesheep deploy, check the visibility column of npx spacesheep list against docs/findings/04-artifacts.md, which is the record: folder deploys have changed visibility in both directions.' Leave line 72, which describes the failure mode.
   Kanter brief: follow open question 1.

2. **[high] fr-2, fr-29** — *03-experiments.md preamble and headers of E22, E23, E24, E25, E26, E28*

   Headers:
   - E22 '(2026-09-22; recorded sweeps 13:22 on both cards)'
   - E23 '(2026-09-22; power runs 13:16–13:17 on aifoundry2, sweeps 13:22 on both cards)'
   - E24 '(2026-09-22, about 15:52 on aifoundry2 and 15:59 on aifoundry3, the first rows of E25's sweeps; the rows carry no timestamps)'
   - E25 '(2026-09-22; aifoundry2 sweep ending 15:52, power bursts 15:57–15:58, aifoundry3 sweep 15:59; committed 16:04)'
   - E26 '(2026-09-23, 07:48–07:59, both cards at once)'
   - E28 '(2026-09-23, 11:18–11:21, aifoundry2)'
   Preamble, add: 'Times are the lab machines' local time (UTC−7), from the first and last recorded sample.'
   Preamble: 'the minion clock was a steady 600 MHz at 516–518 mV on the die' → '…at 516–518 mV on aifoundry2 (521–523 mV on aifoundry3), verified in every telemetry sample of the session'.

3. **[high] nar-1, fr-22, wlp-1, fr-20** — *13-why-low-power.md (Short answer, Side by side, 'Precision is the biggest lever', 'Putting the terms together', line ~29); README.md item 5; getting-started.md line ~68; 01-resources.md R7 and R8*

   13, Short answer: 'It is **not** more efficient per FLOP at dense matmul.' → 'It is **not** more efficient per FLOP at dense 16-bit matmul: 3.3 pJ per FLOP in fp16 against the A100's 1.28 in bf16, and 7.0 pJ in fp32. Against the A100's fp32 spec-sheet peak ÷ TDP it is 3.4× better (matmul-efficiency report, R4); that comparison sets this card's measurement against the A100's datasheet.'
   13, row 'Dense matmul, measured', note → 'A100: R8's 8192³ **bf16** tensor-core run on random data. ET: fp32 TensorFMA …'.
   13, add row: '| Board energy per FLOP, 16-bit inputs (fp16 here, bf16 on the A100) | 1.28 pJ | 3.3 pJ (fp16, 61.1 W at 18.4 TFLOPS, E15) | like for like, the A100 is ~2.6× better |'.
   13: 'the one a GPU benchmark uses' → 'fp32 (the A100 figure here is bf16; this card's fp16 costs 2.70 pJ)'.
   13, after the 'Putting the terms together' table: 'At 16 bits the capacitance per FLOP is 5.0 pF against 1.3 (3.9×), not 11 against 1.3.'
   13 line ~29 (A100 memory): 'HBM2e, 1,555 GB/s' → 'HBM2 1,555 GB/s (40 GB; the 80 GB HBM2e part is 1,935–2,039)'.
   README item 5 → 'It is **not** more efficient per FLOP at dense matmul: 7.0 pJ in fp32 and 3.3 pJ in fp16, against 1.28 for the A100 in bf16 (it clock-gates everything idle, which stops switching but still leaks).'
   getting-started ~68 → '3.4× the A100's fp32 CUDA-core efficiency by spec sheet (not its tensor cores; see docs/findings/13-why-low-power.md)'.
   01-resources R8: add 'bf16'.
   01-resources R7 → '… 624 TOPS int8, HBM2 at 1,555 GB/s (40 GB; the 80 GB HBM2e part is 1,935–2,039 GB/s), 1,410 MHz maximum boost clock; transistor count and die area from the Ampere architecture whitepaper, p. 14.'
   05-claims line ~359: 'HBM2e' → 'HBM2 (40 GB)'.

4. **[high] horace-2, nar-2, nar-3, horace-5, horace-16, horace-29, nar-5, nar-24** — *12-heat-management.md: table row 'random uniform | 512'; 'Three things fall out' bullet 1; lever 3; lines ~53–67; ~66–67; ~116–119; 'Pricing a workload' code block and last paragraph*

   Delete the row '| random uniform | 512 | 12.8 W | 165 s |'. It is the run after the cooling change, which the next paragraph says is left out.
   Bullet 1 → '**Fewer cores buy much more time than the flips they remove**, because leakage feeds back: three quarters of the cores (20.4 W) lasts 35 s instead of 19–26, half (13.6 W) 84 s, three eighths (10.2 W) 119 s, a quarter (6.8 W) 276–315 s, and an eighth (3.4 W) never reaches 90 °C. What sets the time is the switching power, not where it comes from.'
   Lever 3 → '**Use fewer cores.** Power is linear in active minions, with no floor and no cliff, and the time to the cap grows much faster than that: a quarter of the chip ran about 14 times as long (276–315 s against 19–26 s), and an eighth never reached it.'
   Lines ~53–67: 'about 3 W' → 'about 3 W in 21 September's room (less on a warmer day)'.
   Lines ~66–67 → 'The flip energies and the leakage belong to the chip design, up to a per-card scale of about 8% (11-thermal-model.md); the thermal resistance does not.'
   Line ~116: 'Allow six minutes' → 'Allow seven minutes'. Lines ~118–119: 'constant 42 W' → 'an unchanged workload (42.7 W at 84 °C, falling to 35.6 W as it cooled)'.
   'and 3–5 °C optimistic at ten minutes' → 'and 3–5 °C too hot at ten minutes (pessimistic: it wrongly had two of the five ten-minute held-out runs reaching 90 °C)'.
   After the code block add: 'predict_heat.py starts from a die that has sat idle at 80 °C. The strict protocol heats to 84 °C and cools to 80, which leaves the heatsink warmer, so under the protocol the same pair reached 90 °C in 19 s, not 27 (validate_flip_model.py, which estimates the start state from telemetry, predicted 19.6 s). The accuracy below is for that start state.' Replace DATA/model.json with docs/reports/data/2026-09-21-horace-aifoundry2/model.json.

5. **[medium] fr-3, nav-09, fr-13, nar-20, fr-5, fr-6, hub-1, reg-m1, fr-34, fr-14, kb-1, fr-33, horace-7, hl-8, fr-36** — *findings README.md*

   Opening: '(aifoundry2, and aifoundry3 for the cross-card work) between 19 and 24 September 2026' → '(aifoundry2; aifoundry3 for the 18 September sparsity runs, the cross-card sessions E20–E21, and repeats of E22–E27, E29, E31 and E32) between 18 and 24 September 2026'.
   After the first paragraph add: 'The published reports are indexed on the public hub, [Limits of Observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports); [04-artifacts.md](04-artifacts.md) maps each to its sources and space.'
   After 'If you have five minutes', add '## Terms' with glossary text G (decisions). Rename the section 'The findings in brief'.
   Item 5: see the bf16 change above.
   Item 10 → '±17% on the hot line, where a 1.4 W signal rides on a drifting 30 W idle, and ±5% on the DRAM relay'.
   Item 11 → 'Half of idle is on no rail sensor, as is about a sixth of what an arithmetic workload adds and 60–75% of what DRAM traffic adds (70% of a DRAM read).'
   Item 12: 'sharing a link adds 40–45%' → 'sharing a link adds 40–45% on the mesh rail and 55–65% on board power'.
   Item 13 → 'On the later runs of the same session, which it was not fitted to, the time-to-90 °C error is 9% in the median and 23% at worst. On a different afternoon with new matrices it is 7% in the median but 65% at worst: the DFT pair, whose power the flip model got 2.8 W low. It also runs 3–5 °C hot at ten minutes.'
   Where to look: kinds '(measured / simulated / fitted / predicted / derived / external / read from source / **assumed**)'. Instruments row → '[19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md) and the hub's ladder (https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#ladder); [15-earlier-findings.md](15-earlier-findings.md) for the first survey'.
   Provenance table: 'Q1–Q42' → 'Q1–Q43'; 'A1–A18' → 'A1–A19 (A9 and A10 are unused)'.
   Line ~36 → 'The leakage law extrapolated 7–14 °C below its fitted range lands within 0.73 W'.
   Line ~42: 'perfectly fairly' → 'fairly, to within half a percent'.
   What is not established: 'aifoundry3 contributed only the cross-card session: its thermal network…' → 'aifoundry3 repeated the strict protocol (E20), the hot-line sweeps (E22–E23), the scratchpad probe and relay sweep (E24–E25), the catalogue (E26–E27), the reruns (E29) and the wire runs (E31–E32), but its thermal network…'.
   'No GPU was measured. Every A100 number is from a datasheet or one public blog post.' → '**No GPU was measured.** Every A100 number is from published sources: the datasheet (R7), the Ampere whitepaper, the sourced notes in docs/reports/sources/2026-09-18-a100-*.md, and one blog post (R8).'

6. **[medium] fr-4, fr-7, fr-8, hub-2, hub-m2, fr-18, fr-19, fr-27, fr-28, fr-30, fr-37, horace-7, horace-29, hl-7, relay-1** — *03-experiments.md: preamble; E14, E18, E19, E20, E22–E25, E27, E29, E30, E31; lines ~169/~172*

   Preamble: 'Rebuild every analysis, model, GIF and report … with a single script: tools/ettelem/finish_horace.sh' → 'Rebuild the Horace line (E9–E17 and the E20 transfer): every analysis, the model, the GIFs and the Horace and why-low-power pages, with tools/ettelem/finish_horace.sh. Every other entry gives its own command.'
   E14 → '**Written to disk at 13:08:33; the first of those matrices (butterfly) launched 36 s later, at 13:09:09.**'
   E18: '(0 to 16.7 M cycles, i.e. up to 27 ms)' → '(0 to 16.0 M cycles, i.e. up to 26.7 ms)'.
   E19 Method → 'no workload since E16 ended at 15:08 on 21 September, about 20.5 hours, apart from E18's 4.9-second single-hart probe a few minutes earlier; sampled … with no workload during the sample.'
   E20: 'extrapolated 25 °C below its fitted range' → 'extrapolated 7–14 °C below its 64–88 °C fitted range'.
   E22/E23: state that aifoundry3 repeated the sweeps only; the power runs are aifoundry2 only; the host-reading-scratchpad row differs (208 against 240).
   E23 raw data → {telemetry.jsonl.gz,runs.jsonl,marks.jsonl}. E25 → (sweep.jsonl, telemetry.jsonl.gz, runs.jsonl, marks.jsonl, onchip.json).
   E23 energy sentence: append '(re-measured in E29: 19.8 [16.9–23.6] nJ against 1.16 nJ)'. E25: append '(E29: 105.7, 8.6 and 3.99 pJ/B)'.
   E25 '**Distance:**' → 'the next shire by ID is 1–10 mesh hops away (3.5 on average) and s+16 only 2.1; bandwidth does not follow the distance'.
   E27: 'the difference of the slopes, 1.06 pJ/B per hop, is the toggling of the wires' → 'the difference of the slopes, 1.06 pJ/B per hop (133 fJ per bit per hop), is what random data adds over zeros on the wires: bits that change between flits plus ones carried (E31–E32 separate the two)'. Caveat: 'the die drifted from 74 to 87 °C' → 'the die drifted between 71 and 85 °C over the aifoundry2 session'.
   E29: 'command latency 22 → 150 ms' → 'sample latency (six management commands) 22 → 150 ms'. Turn the Result into a table (Entry | mean [range over passes] | aifoundry2 mean ± se | aifoundry3 mean ± se | n). Define once: 'a2/a3 = aifoundry2/aifoundry3; [lo–hi] = the full range over every pass on both cards; pair = the two minions of a pair in a neighbourhood, shire = a ring of all 32 minions of a shire, xshire1 = each minion to the same minion of the next shire ID (not necessarily a mesh neighbour)'.
   E30: 'rms 0.35 W over 392 bursts' → 'rms 0.35 W over 392 configuration means'. Raw data → 'catalogue-aifoundry2/, -aifoundry3/ and -aifoundry2-rows/ telemetry.jsonl.gz, and catalogue.json (392 configurations on aifoundry2 including E28's rows, 386 on aifoundry3)'. Command: 'none committed. The fit was run inline in the session; the model and inputs are above, and the result is unmetered_fit.json.' Replace with the real command if the energy-manual group commits fit_unmetered.py.
   E31 → 'on the mesh rail a = 95 fJ per bit that differs from the previous flit, per hop; b = 131 per one carried; s0 = 74 fixed (on board power: a = 139, b = 197, s0 = 103). A random bit's data-dependent part is 113 fJ per hop on the rail, 188 fJ with s0 (board: 168 and 271).'
   Line ~169: 'up to six minutes' → 'up to seven minutes'. Line ~172: 'under a constant 42 W the die fell' → 'under an unchanged workload (42.7 W at 84 °C, falling to 35.6 W as it cooled) the die fell'.
   Add a '**Report:**' line to every entry (e.g. 'E22–E23 → A13, One hot line stops a shire').

7. **[medium] horace-6, nar-m1, horace-7, horace-29, relay-1, relay-3, dvfs-1, dvfs-2, dvfs-5, dvfs-14, wlp-8, nar-26, wlp-10, ridge-2, heat-1, nar-11, nar-6, nar-7, nar-12, nar-16, nar-17, nar-18, nar-31, fr-33, nar-m2, fr-18, dvfs-fw** — *05-claims.md (legend and the rows named)*

   Legend: add '· `D` derived: arithmetic on measured numbers, no new measurement · `R` read from source code (firmware or RTL) · combined kinds (e.g. `M, F`) mean a measured input and a fitted slope; `P→M` a prediction later measured'. Add under it: 'Where a later session re-measured a number, the older row says so and points to the newer one.'
   Rows:
   - line ~22 (minion clock) verify note → 'constant in every sample of E9, E12, E15 and E16 (launched at 80 °C); below about 68 °C it can lift mid-burst (E29)'.
   - rows ~48–49 → 'Board energy per FLOP, run average (p_mean): zeros / ones / random' and 'Same, over the idle card, run average'; add '| Random normal, at the launch temperature (p80) | 6.9 pJ board, 2.95 over idle | M | E9 |'.
   - line ~51 → '~7 W on no rail, ~4.4 W of it minion-regulator delivery loss by the E30 fit, ~2.6 W unattributed'.
   - line ~93: '11 of 14 within 0.6 W' → '10 of 14 within 0.6 W (11 within 0.75 W)'.
   - line ~95: '2.8 and 4.2 W' → '2.7 and 4.2 W'.
   - line ~128 → '25.6 mW per minion at 256 and 512 active, 26.2 at 768 and 27.0 at 1,024: linear to within 5%'.
   - line ~151: 'checked every 10 ms' → 'checked once per ~133 ms pass'.
   - line ~158 and ~151–155: rename 'Kernel boundary' → 'unattributed (reading ≤65 °C)', with W range 34–56.
   - line ~161 'Limit-cycle period on constant data | about 2 s' → 'Thermal hunting on ones from a 64 °C die | 7 clock changes in 2.4 s, 800 MHz peaks 1.6 s apart, then 600 MHz'.
   - line ~166: '20.4 h' → 'about 20.5 h'.
   - line ~192: row label → 'aifoundry2's idle law extrapolated onto aifoundry3, 7–14 °C below its 64–88 °C fitted range'.
   - line ~209 (hot line 23.6 vs 1.4): append '(first run; the E29 reruns give 19.8 [16.9–23.6] vs 1.16 [1.01–1.37] nJ, below: quote those)'.
   - line ~226 (relay 104.8/8.9/4.3): append '(first run; the E29 bars, below: 105.7 [99.5–111.0] / 8.6 [7.8–9.2] / 3.99)'.
   - line ~230 → 'about 32 flops per byte moved (64 per byte read)'.
   - line ~231: '593 GB/s next door' → '593 GB/s at the next shire in ID order, 3.5 hops on average'. The 'Cost of hop distance' row → 'no bandwidth cost: 593 GB/s at the next shire by ID, 734 at 16 shire IDs (energy per hop is in the E31/E32 rows)'.
   - line ~259 (relay predicted) → 'DRAM 90–133 vs 105.7 [99.5–111.0]; own scratchpad 4.3–7.1 vs 3.99; next shire at 3.5 hops 5.1–11.2 vs 8.59 [7.78–9.21]', kind 'P (out of sample, made after the measurement)'.
   - 'Dense fp32 matmul at 80 °C, predicted from the tables' → '… rebuilt from the tables | 63.5 W against 63.9 measured (E15; E9's random normal is 63.4); 57% static | D (a decomposition: the 6.02 pJ per MAC comes from the same run, so agreement is by construction)'.
   - lines ~272–273 → '| Energy of one mesh hop per byte (board) | **0.70 [0.64–0.75] pJ/B on zeros, 1.74 [1.67–1.81] on random data**, both cards, fitted over 1–8 hops (aifoundry2 alone 0.750 / 1.812; over 1–6 hops 0.89 / 2.29) | F | E27 |' and '| Data-dependent energy of the mesh (random − zeros), per bit per hop | 131 [129–133] fJ over 1–8 hops (174 / 155 over 1–6): flips between flits plus ones carried, split in the E31/E32 rows | F | E27 |'.
   - line ~294 (streaming DRAM 142): add '(ablation, buffer unwritten; E29 levels 122, tensor loads on known data 91–129)'.
   - ridge DRAM row → '76 GB/s on both cards (23 Sep reruns)'.
   - rows citing 353f20e for governor behaviour: add '(source at 353f20e; the card runs an older build, see 01-resources R3)'.

8. **[medium] dvfs-1, dvfs-2, dvfs-4, dvfs-5, dvfs-7, dvfs-8, dvfs-9, nar-8, dvfs-11, dvfs-16, dvfs-17, dvfs-fw, nar-17, nar-25, nar-28, fr-18** — *16-dvfs-and-leakage.md*

   Mirror the DVFS page changes.
   - 'It hunts' paragraph and the 'fix is already in the source' bullet: the thermal-threshold texts from the DVFS group.
   - Lines ~25, ~68, ~139: 'every 10 ms' → 'once per ~133 ms management pass'.
   - Line ~151: the aifoundry3 text from the DVFS group (one throttle-down per kernel start, no floor below 600 MHz).
   - Verdict cell 'Per-minion sleep and isolation exist in the RTL' → 'exist in the open (Erbium) RTL'.
   - Table row 'Kernel boundary, not throttling at all' → 'Unattributed (reading ≤65 °C)', with signature '12–186 ms from a launch boundary, 64–65 °C, 34–56 W'.
   - DRAM row → '+10 cycles: the row closing, an 11-cycle activate (tRCD)'.
   - Line ~98 (L2 −11) → 'comes from the zero-idle baseline (61 cycles), not the idle'.
   - Last verdict row → '| Leakage costs power, not correctness | **Consistent, weakly tested** | Every result checked in this work was correct (matmul results bit-exact against a host reference; every relay element checked). The 20-hour idle is no evidence either way: nothing computed, DRAM ECC is compiled off and the SRAM ECC interrupt sources are never enabled ([15](15-earlier-findings.md)) |'. Line 7 → 'Three hold, one is consistent with everything seen but was never tested where it could fail, one is wrong for this part, and one is a capability that ships switched off.'
   - Kanter 'measurement is expensive' consequence: 'weaker for this card, though it does not vanish (MLPerf power is whole-system)'.
   - Lines ~124–127: the three causes, enumerated, 36% of a 64 W matmul, 128 MB of shire SRAM (over 160 MB on die per Esperanto).
   - Bullet 2 of 'Four consequences': the 65/68 °C wording (preheat to 76 °C).
   - 'what this brief could not' / 'the brief listed it' → 'what the first version of the DVFS brief (A11) could not' / 'that version listed it'.
   - Lines 17 and 108: 'about 20.5 hours', with the E18 caveat.
   - Add the firmware-build caveat (older than 60b40c10f) to 'Not established'.

9. **[medium] nar-13, hub-4, nar-17, nar-29, dvfs-2, dvfs-6, dvfs-7, horace-29, fr-12, dvfs-fw** — *14-card-behaviour.md: telemetry table rails row; governor section; 'three lab machines' table; lines ~90, ~113, ~120*

   Rails row Gotcha → '**the PMIC's first-order running average, τ ≈ 1 s** (61% of a step after 1 s, 88% after 2 s, 95% after 3 s; E27), copied by the SP each pass; not a moving average. Skip 2–3 s after any change before averaging, or use ettelem sample --reset-ms window means.'
   Governor advice → '…and preheat to about 76 °C: the firmware's test is > 65 on a whole-degree reading, and E29 saw the clock lift to 700–800 MHz mid-burst below about 68 °C (19-observability-and-the-unmetered.md).'
   'a card that has been busy idles above 65 °C' → 'a card that has been busy usually idles above 65 °C (72–80 °C on 20–22 September; about 65 °C on 23 September, when the governor did intervene)'.
   Machines table: 'no, ever' → 'never seen (10 Hz telemetry)'; '23.6 W at 51 °C' → '23.6 W at 50 °C (25.1 W at 56 °C under the runs)'.
   Line ~113: 'throttles down every 10 ms' → 'logs a throttle-down at every kernel start, and nothing can ever step it up'.
   Line ~120: 'capped for life' → 'held at 600 MHz for as long as its flashed TDP stays at zero'.
   Line ~90: 'up to six minutes' → 'up to seven minutes'.
   Add the firmware-build caveat where 353f20e is cited for the governor.

10. **[medium] fr-9, fr-12, fr-15, fr-16, hub-1, fr-17, fr-38, fr-22** — *getting-started.md*

   Line ~4: '19-22 September 2026' → '18–24 September 2026'.
   Heading 'Where things stood on 2026-09-18' → '## Earlier work (18–21 September), and where it stood'.
   Horace: '(fourth version, 2026-09-21 …)' → '(sixth version, 2026-09-22: … and the same experiment on aifoundry3)'.
   §1: '# private repo' → '# public repo'.
   §6 aifoundry3 → '~/nekko (deployed for E20 onward) and the workloads/sgemm build.'
   §2 machine table:
   - aifoundry1 | 2 | Not usable: its kernel module differs from the other machines and libDM.so refuses both cards (E21). Do not reinstall the driver; ask the lab admin.
   - aifoundry2 | 1 | The main card for this work. 600 MHz above 65 °C (up to 800 MHz below), 32 GB LPDDR4X, idle 27 W cold, 31–36 W after load.
   - aifoundry3 | 1 | Flashed TDP 0 W, so the governor never leaves 600 MHz (E21). Idles about 51 °C. Compare switching power over idle, not absolute watts. ~/nekko is deployed.
   Add 'See docs/findings/14-card-behaviour.md.'
   'What the bars taught us' → 'small signals carry the widest bars because a 1–5 W signal rides on a 30 W idle that drifts: ±17% on the hot line, ±5–15% on the levels and rings, ±5% on the DRAM relay'.
   Line ~313 (§8): 'the governor moves between 600 and 850 MHz' → 'the governor moves between 600 and 800 MHz (three points: 600, 700, 800)'.
   §8 'Reproducing each report', intro → 'Reports from 18–19 September are hand-written HTML whose charts read JSON an analysis script embeds. Later reports are assembled by scripts/build-report.py from docs/reports/sources/ (see docs/findings/04-artifacts.md), and several compute every number from their data.' Add rows:
   - Memory anatomy: workloads/memprobe/analyze.py, then build_report.py summary.json HTML
   - Horace and why low power: tools/ettelem/finish_horace.sh
   - Hot line, relay and heat per mm: their E22–E25 and E31–E32 commands in 03-experiments.md
   - DVFS: tools/ettelem/analyze_dvfs.py
   In the catalogue row, '1.5 h each' → '2.6 h each' and 'analyze_catalogue.py A2 A3' → 'analyze_catalogue.py A2 A3 A2_ROWS'.
   Line ~94 → 'board power rises about 0.8 W per °C under load (E5, measured; the fitted leakage slope at 80 °C is 0.65 W/°C, E17)'.
   Line ~38 → '... needs a die above 68 °C or the governor moves the clock mid-burst (the firmware threshold is 65 °C, but on ettelem's mean die reading the clock still stepped up at readings up to 67 °C in E10); the cool-card reruns of 23 September, at 64–66 °C, were discarded for that reason.'

11. **[medium] fr-10, nav-10, fr-11, anat-15, fr-14, fr-23, fr-31, nar-21, fr-35, reg-m2, relay-1** — *04-artifacts.md*

   Header: 'Cite as **A1**...**A18**' → 'Cite as **A1**...**A19** (A9 and A10 were never assigned)'. Add an index line: 'A1–A5, A11, A13–A15, A17, A19 reports · A6–A8 images · A12 math rendering · A16 rerun tools · A18 wire tools'. Put A17 before A19 in the table.
   Intro → 'Reports A2–A5, A11, A13–A15 and A17 are assembled by scripts/build-report.py <name> <data.json> <out.html> from docs/reports/sources/<name>.{meta.json,body.html,script.js} (A2 also keeps its data in limits-of-observability.data.json). Edit the sources, not the HTML. A1 is generated by workloads/memprobe/build_report.py <summary.json> <out.html> from workloads/memprobe/report_template.html. A19 and the four 2026-09-18 reports are hand-written HTML whose embedded JSON is rewritten by their --embed scripts. The 2026-09-18 test drive (docs/report/index.html) is plain hand-written HTML. For these, edit the prose in the HTML.'
   Add a table 'Other spaces the hub links (not built by this line of work)', columns Report | Source | Space | Visibility:
   - Matmul efficiency (R4) | docs/reports/2026-09-18-et-soc1-matmul-efficiency.html | 590752c1-17a8-4f5d-97ef-bcf33fd6a3e7 | public (Q40)
   - Memory hierarchy (R4) | … | 4b6e0a37-808d-4fc9-8001-555125733c46 | public (Q40)
   - On-chip communication (R4) | … | ab8e1b2b-de17-44f4-8645-006fa960e349 | public (Q40)
   - Sparse compute (R4) | … | 5abf6014-8de0-4e82-8744-5676bac6453e | public (Q40)
   - Test drive | docs/report/index.html | 16732875-c03e-434d-a643-7a432586c7f7 | public
   - Spatial temperature brief | published page only | bc391cfe-64e2-4f36-884c-9bbfcb267de8 | public (Q40)
   - L2 mainline starvation brief (R12) | published page only | 49ca367f-886f-4c0a-b472-12d8fc449300 | public (Q40)
   - David Kanter power brief (R9) | published page only | f3533740-5ad9-45e1-927c-098dbbe5c210 | per open question 1
   Then drop the 'Earlier reports' footnote.
   A2 row: '(19 rungs)' → '(20 rungs)'.
   A4 versions: version 6 commit '(this commit)' → '9df563e'.
   Commits: add 8d17612 (ridge points), 6f8fba9 (index ridge points in the hub), d04b29a (link every report back to the hub). Copy the subjects of 17a1aa5, b36acd6 and 9df563e verbatim from git log --format=%s.
   Cross-links: add "David Kanter's power brief (f3533740…, no source here) is also published-only and was not patched: it has no link back to the hub, and its '(spatial-temperature brief, 22 Sep)' link points to the repository root." Update this once open question 1 is settled.
   A14 row: 'neighbouring shire' → 'the next shire by ID'.

12. **[medium] dvfs-fw, fr-24, fr-25, fr-3, hl-8, fr-21, fr-32, nav-04** — *01-resources.md R1, R2, R3, R5, R9, R10, R11, R14*

   R3 heading → '(external/et-platform/, at 836a4ab after clone-upstream.sh; the card was assumed to run 353f20e, and device-bootloaders/src/ServiceProcessorBL2/ is identical at both)'.
   R3: replace 'The commit that matches the firmware running on aifoundry2's card' with 'The source read for the firmware; the cards' own trace strings match an older build (before 60b40c10f, 24 Sep 2024; both cards report release 1.3.1). Which commit the cards run is not established.'
   R2 paths: prefix rtl/, e.g. rtl/shire/minion/vpu/txfma_7s/txfma_top.v, rtl/shire/neigh/neigh_pmu.v, rtl/libs/registers/{ff,en_ff,rst_ff,rst_en_ff}.v.
   R2 Authoritative for: add 'the per-cycle compute peaks in docs/Minion VPU Specification.pdf (A19)'.
   Used by:
   - R1 → 'E1, E11, E13, E22–E24, E31–E32 (via R14), A13'
   - R2 → 'E2, E11, E13, E31–E32, A11, A19'
   - R3 → add 'E4, E21'
   R10 → 'Authoritative for: … for aifoundry3, everything measured in E20–E27, E29, E31 and E32 (E23 without power, E28 not at all).' Used by → 'E20–E27, E29, E31, E32.'
   R11: 'within one part in a thousand' → 'within half a percent'.
   R14: '3.64–3.76' → '3.64–3.74'.
   R5 → '… every other session kept each kernel process under 10 s; the telemetry sampler (ettelem sample) held the single-opener management node for whole sessions (up to 2.6 h in E27).'
   R9: if the Kanter brief is unpublished, change the link line to 'written up as a private research brief (space f3533740…)'.

13. **[medium] horace-6, nar-m1, fr-4, nar-6, nar-7, nar-19, nar-20, nar-23** — *10-data-dependent-power.md*

   Line ~102: 'and 11 of the 14 within 0.6 W' → 'and 10 of the 14 within 0.6 W (11 within 0.75 W)'.
   Line ~83: 'starting at 13:16' → 'starting at 13:09'.
   Main table: rename the last two headers 'pJ/FLOP, run average' and 'pJ/FLOP over idle, run average'. Add under the table: 'The pJ/FLOP columns divide each run's mean power over all 7.3 s (horace3.json p_mean), which includes the leakage the run's own heating adds; the W column is the launch-temperature value. At 80 °C random normal is 6.9 pJ per FLOP (2.95 over idle), and the 7.0 pJ in 13-why-low-power.md is the 63.9 W E15 ablation run on the same basis.'
   Bullet 3 → '**Over the idle card the data decides a factor of 14–15** in energy per FLOP (0.22 against 2.95 pJ at 80 °C, 3.31 on the run average).'
   'Only the core rail moves' bullet: 'and about 7 W never reaches the die at all (regulator loss, which grows with current)' → 'and about 7 W is on no rail sensor: by the later attribution (19-observability-and-the-unmetered.md, E30) about 4.4 W of it is the minion regulator's delivery loss (19.6% of the 21.5 W delivered); the remaining ~2.6 W is not attributed.' Retitle the bullet 'The minion rail carries almost all of it.'
   Link the first use of hart, minion, TensorFMA and L1 scratchpad (line ~10) to README.md#terms.
   Header and Related lines: see the narrative-navigation change below.

14. **[medium] wlp-2, wlp-3, wlp-4, wlp-7, nar-4, wlp-8, nar-26, wlp-10, wlp-13, nar-7, nar-27** — *13-why-low-power.md (other than the bf16 edits above)*

   Mirror the why-low-power page:
   - the A100 clock range 1,160–1,410 MHz and the 5–6× V²f;
   - the 10 mW total-budget bullet;
   - three operating points;
   - 'three parts operating point' → the 5–6× / 1.4–1.7× split;
   - line ~67: the linearity sentence (25.6 / 25.6 / 26.2 / 27.0 mW; 26.5 through zero);
   - the Memory bullet (142 pJ/B unwritten; 122 and 91–129 in the energy manual);
   - line ~120 → '(about 7 W of the 28 W under random data is on no rail sensor, some 4 W of it regulator delivery loss)';
   - 'gated off' / 'gated to nearly nothing' → clock-gated wording.
   Caveats: 'Over 0.75–0.95 V the V² ratio runs from 2.1× to 3.3×, so the 8.8× switching ratio is really 7–11×.' → 'Over 0.75–0.95 V the V² ratio runs from 2.1× to 3.3×, so the V²f factor is 4.9–7.9× instead of 6.3× and the capacitance ratio 1.1–1.8× instead of 1.4×. The 8.8× switching-power ratio is measured (242 W against 27.6 W) and does not move; capacitance per FLOP moves from 0.12× to 0.09–0.15×.'
   Sources: 'E10 (the two operating points)' → 'E10 (the 600 and 800 MHz operating points)'.

15. **[medium] anat-4, anat-7, nar-14, nar-15, noc-5, nar-23** — *15-earlier-findings.md*

   Line ~27: 'all within ±2 cycles of the model but two' → 'all within ±4 cycles of the model but two'.
   'Energy per 64 B load' → 'Energy per load (8-byte ld; a 64 B line moved below L1)'.
   L2 row → '| L2 hit | 48 cycles from the array; 37 when the line is still in the bank's 8-entry read buffer |'.
   After the energy sentence add: '(From the rail trace, which reads 15–20% below the host log. The energy manual re-measured the levels at 600 MHz on both cards (E29): L1 0.77, L2 2.51, L3 10.5 (lines homed across the whole chip, so several mesh hops on average, not the local slice) and DRAM 122 [117–129] pJ/B, i.e. about 49 pJ, 161 pJ, 0.67 nJ and **7.8 nJ** per 64 B line. For DRAM, quote the E29 figure.)'
   Memory-hierarchy bullet → '**Memory hierarchy:** per-level latency, bandwidth and energy per byte. Its bandwidth column averages launches at 600–800 MHz; at 600 MHz L2 is 2.45 TB/s and 128 B per shire-cycle, not 2.80 TB/s and 144 (05-claims.md, "Two corrections").'
   Line ~80 (on-chip) → '**On-chip communication:** 20 ns per mesh hop in both directions at any clock (12 cycles at 600 MHz); inside a shire 68 cycles on reduction-tree edges and 114 elsewhere; a 1,024-minion allreduce in 2.3 µs; energy per byte 0.8 pJ on tree edges, 2.3 pJ within a shire, ~10 + 1.9 pJ per hop across the mesh, busy cores included (re-measured in E29).'
   After the A2 table add: 'The second edition (23–24 September) made A2 the hub; its meter chain, unmetered remainder and improvement ladder are in [19](19-observability-and-the-unmetered.md).'

16. **[medium] hl-1, hl-3, nar-10, hl-8, hot-pace-1** — *17-hot-line.md*

   l3_yield: mirror the hot-line page (erratum 4.1 covers the same-address case; the measured case is different addresses; untested).
   Under the Energy table add: 'Re-run for the energy manual (E29): contended 19.8 [16.9–23.6] nJ, spread 1.16 [1.01–1.37] nJ, n = 7. Still 17×; about 1.2 W over idle for the stalled chip. The table above is the first run.' Change 'about 1.4 W' → 'about 1.2–1.4 W'.
   'perfectly fairly' / 'one part in a thousand' → 'to within half a percent'.
   'The workaround, priced': host column → '16,000 | 95% | 61%' and '100,000 | 98% | 10%'.

17. **[medium] relay-1, relay-2, nar-9, relay-3, nar-30, nar-18, vnav-m1** — *18-on-chip-relay.md*

   Line ~6: 'to a neighbouring shire's' → 'to the next shire's (in ID order, 3.5 mesh hops away on average)'.
   Heading at line ~74, 'Distance across the mesh is free' → 'How far the slab moves does not change the bandwidth'. Append to the section: 'It does cost energy: each hop adds about 1.5–2.2 pJ per byte (20-heat-per-mm.md), roughly half of an own-scratchpad read, which this bandwidth sweep does not see.'
   The memory-hierarchy sentence → 'The energy figures are in line with the energy manual's levels, re-measured at 600 MHz on both cards (E29): 122 [117–129] pJ/B from DRAM, 2.5 from the own scratchpad, 6.7 from another shire's. The 18 September memory-hierarchy report printed 148 / 2.8 / 6.3, a mean of two runs taken at mixed clocks.'
   Rule of thumb → 'on-chip placement pays several-fold up to a few flops per byte moved (read plus written) and is still 1.5× at 32 flops per byte moved (64 per byte read); for the tensor unit, see the ridge points'.
   Last 'Not established' bullet → '**Scaling with the number of shires is not measured.** A sweep that used fewer shires also shrank the working set back inside the L3, so it cannot be read as a scaling curve.'

18. **[medium] hub-2, hub-3, hub-4, hub-12, hub-m1, nar-21, nar-22, fr-31** — *19-observability-and-the-unmetered.md*

   Opening → 'The measurement side of the energy manual, as of 24 September 2026 … Sources: E29–E32, R13.'
   '0.35 W over 392 bursts' → '0.35 W over 392 configuration means (1.1–1.3 W on the DRAM configurations); the idle 15 W is not split'.
   Meter chain: 'as a first-order filtered average (τ ≈ 1 s)' kept by the SP → 'the PMIC's own running average (τ ≈ 1 s), which the SP copies each pass'.
   Line ~39: '40 process detectors' → '35 process detectors'.
   Line ~44: 'responds to DRAM traffic alone' → the hub §4.3 wording (mostly DRAM; mesh and scratchpad traffic droop it 1–1.7 mV; idle moves ~1 mV between 71 and 77 °C).
   Line ~45: the IR-drop attribution → 'the Power and temperature report (§3) maps each shire's rails at idle'. Link the spatial temperature brief once, to https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief.
   Line ~82: 'Nineteen rungs in the observability report' → 'Twenty rungs in the observability report'. Turn the one-sentence ladder into a table (Group | Rungs | Status):
   - software on the card's own data | bracketed bursts (1), attribution (2), droop meter (3), sub-degree temperature by step timing (6), meter latency and queue checks (7) | done
   - software, not yet | deconvolving the rails' filter (4), calibrating the per-shire IR-drop map into current (5) | tooling
   - lab hardware | PCIe shunt riser (8), IR camera (9), second card (10) | tooling; 10 done
   - firmware | PMIC input-side readings (11), 35 temperature sensors (12), process detectors and analog inputs (13), faster unfiltered power (14), ECC sources (15), counter-select syscall (16) | signed image
   - tooling | libDM Minion Debug Interface client (17), Verilator bench and flame graphs (18) | tooling
   - research | cell library (19), current sensing below the regulators (20) | research / not on silicon

19. **[medium] nar-19, nar-23** — *every narrative 10–20 (first line after the H1; end of file)*

   First line after the H1 in every narrative: '[← Findings index](README.md) · published as [<title>](<url>) (A<n>) · numbers and sources: [05-claims.md](05-claims.md)'. The published pages are:
   - 10, 11, 12: Horace (A4)
   - 13: why-low-power (A5)
   - 14: none, index only
   - 15: memory anatomy (A1) and the hub (A2)
   - 16: DVFS (A11)
   - 17: hot line (A13)
   - 18: relay (A14)
   - 19: hub (A2)
   - 20: heat per mm (A17)
   End every file with a '## Related' list:
   - 13: 10 and 11 (flip model, leakage law), 16 (governor, three operating points)
   - 10: 11 (the model), 12 (long runs), 13 (against an A100)
   - 14: 16 (governor), 19 (what the meters miss)
   - 17: 19 (the E29 bar), 18 (the barrier lesson)
   - 18: 20 (the energy of each hop), 17
   - 19: 17, 18, 20
   - 20: 19, 18

20. **[low] fr-14, kb-1, fr-26, fr-32, fr-36** — *02-requests.md header, Q31, Q33, Q41, Q43, scope decisions*

   Header → 'Q1–Q42 come from one long session on aifoundry2 (18–24 September); Q43 comes from a separate session and is listed in the order it was recorded. Cite as **Q1**...**Q43**.'
   Q43 Produced → 'A19; the hub's index row (6f8fba9); every report's link back to the hub (d04b29a); no card time'.
   Q33: 'docs/getting-started.md "Where things stand (2026-09-23)"' → 'docs/getting-started.md "Where things stand"'.
   Q31: '… E29 → A15 third edition, A16'. Q41: '… E31, E32 → A17, A18'.
   Scope decisions: 'kept individual processes under 10 seconds' → 'kept each kernel process under 10 seconds (the telemetry sampler held the management node for whole sessions)'. 'Every A100 number in this work is from R7 or R8' → 'from R7, R8, the Ampere whitepaper and the sourced notes in docs/reports/sources/2026-09-18-a100-*.md'.

21. **[low] horace-7, nar-28, nar-19** — *11-thermal-model.md*

   Lines ~121–122 → 'Fitted on aifoundry2's idle samples between 64 and 88 °C (plus the 62 °C overnight anchor) and extrapolated 7–14 °C below that range onto aifoundry3, which idled at 50–57 °C'.
   'Where it breaks': '(0.106 and 0.050 °C/W at 1.5 and 4 s in both …)' → '(0.10 and 0.05 °C/W at 1.5 and 4 s in both fits)'.
   Under the model block add: '22.8 °C is the fitted intercept of the main session, not the room temperature; each session has its own (the afternoon's is 28.0 °C).'
   'The first published version of this report' → 'Version 4 of the Horace report (A4, commit 07f7d04)'.

22. **[low] anat-4, anat-7, noc-5, hub-1 (lowpower)** — *docs/et-soc1-notes.md lines ~78, ~80, ~148*

   Line ~148: 'all within ±2 cycles but 2' → 'all within ±4 cycles but 2'. Change any 'Energy per 64 B load' wording as in 15.
   Line ~78 → '- **A mesh hop costs 20 ns round trip** (12 minion cycles at 600 MHz, 16 at 800), the same in both directions; the 18 September scratchpad rows that looked asymmetric ran at different clocks (row 0 at 600 MHz, row 31 at 800).'
   Line ~80: '~850 MHz' → '800 MHz (three points: 600, 700, 800)'.

23. **[low] wlp-17** — *docs/research/why-low-power.md top; lines ~41–44*

   Add at the top: "The measured numbers under 'What this card measures' are from the 20 September draft (idle fit, 63.4/46.7 W, 26 mW, 0.16 nF); the report and docs/findings/13-why-low-power.md supersede them." Or update lines 41–44 to 12.6 W + 23.3 W·e^((T−80)/36); 38.2 / 46.9 / 63.9 W; 1.9 / 10.3 / 27.0 mW; 0.012 / 0.064 / 0.168 nF. Leave line 33 (HBM2e 1.6–2.0 TB/s) unchanged.

24. **[low] noc-5** — *docs/reports/sources/2026-09-18-gpu-on-chip-communication.md line ~415*

   'it gives 12–16 cycles per mesh hop for remote scratchpad loads, a different operation (a round trip, at 600–800 MHz)' → 'it gives 20 ns (12 minion cycles at 600 MHz) per mesh hop for a round trip, a different operation'.

25. **[low] fr-5, fr-15, fr-31** — *README.md (repo root): Horace bullet (~line 64), line ~45*

   Horace bullet: '(fourth version, 21 September)' → '(sixth version, 22 September; section 10 repeats it on aifoundry3)'.
   'on held-out runs the time to 90 °C is predicted to 9% in the median and 23% at worst' → 'on the later runs of the same session, which it was not fitted to, the time to 90 °C is predicted to 9% in the median and 23% at worst; on a different afternoon with new matrices, 7% and 65% (the DFT pair, whose power it put 2.8 W low)'.
   Line ~45: '19-rung improvement ladder' → '20-rung improvement ladder'.

### 3.19 published-only:2026-09-22-et-soc1-l2-mainline-starvation

Files: `live HTML: scratchpad/audit/live/2026-09-22-et-soc1-l2-mainline-starvation/index.html (no repo source), space 49ca367f-886f-4c0a-b472-12d8fc449300`

1. **[high] l2-1, nl-1, nav-01, l2-2** — *directly after <p class='lede'>; KPI 1; heading 'What he measured…'; fignote; card mc-1; card rc-2*

   Depends on open question 4: this is the plan if the brief stays up.
   Insert: <div class='q'><b>Update, 22 Sep, later the same day.</b> We reproduced this on two cards (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line'>One hot line stops a shire</a>). The ~60 M atomics/s aggregate and the even split among the 31 remote shires hold. The 6% does not: the owner's share of the atomic is 1.004 of an even split, because a global atomic cannot take the local path (through the self ID 0x7F it is a bus error), so the owner's atomics queue at the same L3-slave port as everyone else's. What starves is the owner shire's <i>other</i> memory traffic: its own scratchpad and DRAM loads fall to 0.01–0.05% of normal for as long as the line is hammered. Errata 4.1 (RTLMIN-6207) and 4.2 (RTLMIN-6214) describe the mechanism. The placement advice and the systolic sections below still stand. The 17× figure and the l3_yield ask do not.</div>
   KPI 1: lab 'What stops when 31 shires hammer one line'; num '0.02%'; foot 'the owner shire's own loads, of normal; its share of the atomic is fair (1.004)'.
   Heading → 'What he reported, and what reproduced'.
   Fignote → 'As reported in Discord, 22 Sep, 02:30 PT. Reproduced the same afternoon: the aggregate and the remotes' even split hold; the owner's 6% does not — its share is 1.004 (One hot line stops a shire, §1).'
   Card mc-1: title 'The owner's atomics were not last; its loads stopped'; text 'In the reproduction the owner's atomics finish alongside everyone else's. Its ordinary loads are what stop: 384 operations in a window where the mesh retires six million atomics.'
   Card rc-2: title 'Hot structure → the owner's other work stops, invisibly'; text 'A barrier counter, lock, queue head or reduction root hammered by about 24 or more concurrent remote requesters (20 still leave the owner at 99%) saturates its home bank; the owner shire's own scratchpad and DRAM loads drop to 0.01–0.05% of normal and nothing reports an error.'
   Placement tier: 'that is his measurement, not a guess' → 'the hot-line report measured this: every requester gets its fair share to within 0.1%'.

2. **[high] l2-2** — *card mc-2 'It's the design, not Errata 3.2'; table row 'Is it fixable?'; fix step fs-4*

   Card mc-2: title 'The vendor wrote it down'; text 'Errata 3.1 and 3.2 (RTLMIN-6207, RTLMIN-6214; numbered 4.1 and 4.2 in the errata body, both Postponed) describe the shire cache favouring L3-slave requests. They say l3_yield_priority does not rescue a neighbourhood request to the same scratchpad address, and has no sub-bank granularity. The workaround they give is to slow the remote polling.'
   'Is it fixable?' → '<b>Not reliably by l3_yield.</b> The errata say it does not rescue a neighbourhood request to the same scratchpad address (RTLMIN-6207) and has no sub-bank granularity (RTLMIN-6214); whether it would help the owner's other traffic is untested. Placement fixes it, and so does pacing the remote shires: at 10,000 cycles between atomics the owner gets back 54% of its memory throughput, at 16,000 about 95% (One hot line stops a shire, §6).'
   Step fs-4: title 'Pacing — also today, no permissions'; text 'If the hot line must live in a computing shire, make each remote wait at least 10,000 cycles between atomics: the owner gets 54% of its throughput back at 10,000 (the hammering shires keep 96% of theirs) and about 95% at 16,000 (they keep 61%). Exposing l3_yield_priority through a syscall is not a reliable fix per the errata, and is untested for this case.'

3. **[medium] l2-4** — *KPI 2; table row 'What's the practical impact?'; note under 'When it bites'*

   KPI 2: lab 'Earlier measurements this invalidates'; num '0'; foot 'all were uncontended; the contended case is now measured (E22–E23)'.
   Practical impact → '<b>Small, if nothing polls a hot line from many shires.</b> It bites when about 24 or more requesters in other shires hammer one line (20 still leave the home shire at 99%): the home shire's own loads stop. The first relay kernel hit exactly this with 32 shire leaders spinning on one barrier counter, and hung (Hand it to the next shire).'
   Note: 'Nothing is invalidated; nothing predicts the contended case either.' → 'Nothing earlier is invalidated; the contended case is measured in One hot line stops a shire.' 'nocbench runs one pair at a time with a barrier between' → 'nocbench's latency test runs one pair at a time with a barrier between'.

4. **[medium] l2-3, nav-01, nav-11, nav-12** — *before </main>; headings*

   Add <section><h2>Related reports</h2><ul>:
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line'>One hot line stops a shire</a> — the reproduction: the atomic is fair; the owner's own loads stop
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay'>Hand it to the next shire</a> — shire-to-shire hand-off through the scratchpad, built this way because of the TensorSend hazard
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>On-chip communication</a> — the source of the latency, bandwidth and energy numbers above, and the one-ready-flag trap
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy'>Anatomy of a memory access</a> — which shire homes which line (PA[10:6])
   - <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability'>All ET-SoC-1 measurement reports</a>
   Close with </ul></section>.
   Link 'the allreduce tree is 3.7× faster…' and the landmine section to on-chip communication (#reduction-trees, #a-trap-one-ready-flag-per-minion). Link 'memprobe' → et-soc1-memory-anatomy and 'nocbench' → et-soc1-on-chip-communication.
   Paste the section-anchor script.

5. **[medium] l2-5, nav-13** — *byline, lede, headings, throughout*

   Byline → 'An analysis, written on 22 Sep before the reproduction that afternoon, of a result Ivan (@ivanchernobyl, AI Foundry Discord) reported. At a shire's cache, requests arriving from other shires over the mesh ("L3-slave" requests) outrank the shire's own ("L2") requests; the rule is stated in <a href='https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/docs/research/counters-and-dram.md'>counters-and-dram.md §5</a>. Part of the ET-SoC-1 measurement reports.'
   After the lede add <p class='sub'><b>Terms.</b> Shire: 32 minion cores sharing a 4 MB L2/L3 cache and scratchpad. Hart: hardware thread. U-mode/M-mode: user and machine privilege; kernels run in U-mode. amoaddg: global atomic add. FLB: fast local barrier. AINekko: the company (AI Foundry) that maintains the open ET platform and its firmware.</p>
   Rename 'The four answers' → 'Five questions, answered'.
   Replace 'your' with 'the' throughout (e.g. 'It costs current work nothing', 'Nothing in the published suite does that', '— docs/et-soc1-notes.md in the repository').
   Subtitle under the h1: 'L2 mainline starvation on the ET-SoC-1, and the systolic path around it'. <title> → 'L2 mainline starvation: a brief · ET-SoC-1'. Keep the slug.

6. **[medium] l2-6** — *lede*

   'but has a separate hazard that bricks the card' → 'but has a separate hazard: a 2D array hangs a hart until the card is power-cycled'.

7. **[low] l2-7, l2-8, l2-9, l2-bar-1** — *systolic section heading and bar sb-4 and fignote; card 'So a global atomic costs ~10 cycles of bank'; note under primitives table; chart bar mb-1*

   Heading → 'The systolic array: immune, and ~10× faster for messages kept inside a shire'.
   Bar label 'TensorSend across the mesh', value '0.09–0.16 TB/s'.
   Fignote → 'Aggregate bandwidth, 1 KB messages, 600 MHz, from nocbench (18 Sep). For register-to-register messages, staying in a shire is ~10× crossing the mesh; bulk data crosses the mesh at 0.6–1.0 TB/s by tensor load and store (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay'>Hand it to the next shire</a>).'
   '(14 cycles if the governor is at 850 MHz.)' → '(Measured directly that afternoon: 10.00 cycles per atomic; One hot line stops a shire.)'
   Primitives note → 'Natural unit: one shire (32 minions). Inside a neighbourhood only the tree's pairs (0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7) get the 68-cycle path; a chain through all eight needs at least one 114-cycle hop.'
   If the 'As reported' chart is kept: mb-1 value '103%' (bar width 100%) and scale mb-2 to 5.8%, or label the bars 'as Ivan reported: even split among the 31' with no percentage.

8. **[low] known: phone overflow** — *whole page CSS*

   Fix the known 15–22 px sideways overflow at 390 px width (widest table or pre gets overflow-x:auto; long words break) while republishing.

### 3.20 published-only:et-soc1-spatial-temperature-brief

Files: `live HTML: scratchpad/audit/live/et-soc1-spatial-temperature-brief/index.html (no repo source), space bc391cfe-64e2-4f36-884c-9bbfcb267de8`

1. **[high] sp-2** — *lede; KPIs 'Hardware Sensor Resolution' and 'Host Observability Today'; §1 RUN_1 formula; §3 rows 1–2*

   Lede: 'into a single 34-shire average rounded to whole degrees Celsius' → 'into a 34-shire average plus two peak-hold extremes, all in whole degrees: the firmware's integer conversion truncates every sensor's reading to 1 °C before it is averaged'.
   KPI 'Hardware Sensor Resolution' sub → 'Moortec PVT IP; the firmware keeps whole °C'.
   KPI 'Host Observability Today' sub → 'Current mean + since-reset extremes, truncated to 1 °C'.
   After the formula: 'The firmware evaluates this in integer arithmetic (pvt_ts_conversion), so every per-shire value it holds is already whole degrees; the 0.061 °C step exists only in the raw 12-bit code in TS_SDIF_DATA.'
   §3 row 2: append 'Whichever option is used, export the raw 12-bit code (or millidegrees computed before the /1000), not sample.current, which is already truncated to 1 °C.'
   Row 1: 'at 12-bit resolution' → 'at 12-bit resolution in hardware (the firmware then truncates to 1 °C)'.

2. **[high] sp-1, nl-5, nav-18** — *KPI 'Physical Spatial Topology'; §1 intro*

   KPI sub → '1 sensor per tile (~3.7 mm grid)'.
   '(~1.2 mm on a side)' → '(about 3.7 mm on a side: the tile pitch measured on Esperanto's die plot and scaled to the 570 mm² die; see <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm#die'>Heat per millimetre §2</a>)'.

3. **[medium] sp-3, spatial-1** — *§1 sensor list third bullet; §2 code excerpt*

   Move the PMIC bullet out of the list of 35 on-die sensors. After the list add: <p>The host also receives a field named <code>pmic_sys</code>, but it is not a board sensor: the firmware fills it from <code>pvt_get_minion_avg_temperature()</code>, the same 34-shire average (the two were equal in all 586 samples of the 20 Sep telemetry). The PMIC reads its regulators' temperatures over PMBus, but the SP does not forward them.</p>
   In the excerpt: 'temperature->pmic_sys = ...;' → 'temperature->pmic_sys = pmic_temperature;  // the same minion-shire average, not a PMIC reading'.

4. **[medium] sp-4** — *§2 code comments; KPI 'Host Observability Today'*

   Comments:
   - '// Highest shire' → '// highest value any shire's peak-hold register captured since the last reset'
   - '// Lowest shire' → '// lowest value … since the last reset'
   - '// Arithmetic mean of all 34 shires' → '// integer mean of the 34 shires' whole-degree readings'
   Under the code: 'So the host never sees the current spread between shires: min and max are peak-hold values (in the 20 Sep telemetry, the low stayed at 62 °C all session while the average ran 79–90 °C).'

5. **[medium] sp-5** — *§2 card 'The Voltage vs. Temperature Discrepancy'; §3 Option C; §2 prototype listing*

   Card: 'For temperature, however, no per-shire logging was enabled in the background loop' → 'For temperature the firmware already has the matching DEBUG line (MS %2d Temp [C]: %d [%d, %d], in pvt_print_min_shire_temperature_sampled_values()), but it is reached only through pvt_print_all(), which nothing calls'.
   Option C → 'Option C (no protocol change): call the existing pvt_print_temperature_sampled_values(PVTC_MINION_SHIRE) from the SP's per-pass loop, one line, and parse the trace like the voltage map (whole degrees; see the resolution note above). It also writes a CRITICAL "MinShire Average Temp" line on every call.'
   Second prototype → 'int pvt_get_and_print(uint8_t print_ts, uint8_t print_vm, PVT_PRINT_e print_select /* e.g. PVT_PRINT_MINSHIRE_ALL */, uint16_t *data, uint32_t *num_bytes);  // exists, no caller'.

6. **[medium] sp-6, nl-21** — *§1 heading, intro, the four grey cells, caption*

   Heading → 'The 6×6 shire mesh, as the latency measurements place it'.
   Intro: 'verified that the compute shires form a 6×6 2D mesh where inter-shire round-trip latency strictly follows 150 + 12.0 × (Manhattan distance) cycles' → 'place the 32 compute shires on a 6×6 mesh (marty1885's map): every TensorSend round trip between two shires is 150 + 12.02 × (Manhattan distance) cycles, worst residual 1.1 cycles over all 496 pairs (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'>On-chip communication</a>)'.
   Relabel the grey cells: (0,4) and (0,5) 'I/O or PCIe (inferred)'; (0,3) and (5,3) 'master or spare (inferred)'. List TS32/TS33/TS34 in the caption.
   Caption → 'The mesh as latency places it (x across, y down). In this frame the eight memory shires sit one step beyond the top row (0–3, at x = 1–4) and the bottom row (4–7); the PRM calls those sides west and east, so this drawing is the die turned a quarter. The grey cells hold the master, spare, PCIe and I/O shires; which is which is not measured (the heat-per-mm die study infers I/O and PCIe at (0,4) and (0,5)). TS32 (master), TS33 (spare) and TS34 (I/O) are read like the others.'

7. **[medium] sp-7, spatial-1, nav-18** — *§2 card, first two sentences; §4 intro reference*

   → 'The <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature'>Power and temperature</a> report (20 Sep, §3 The per-shire voltage map) reads per-shire voltages this way: with the SP's log level at DEBUG, the firmware prints one line per shire per pass (MS %2d Voltage [mV]: VDD_MNN: %d [%d, %d] …). At idle the minion rail read 517–521 mV across the 34 shires, in whole millivolts; the monitors' low/high captures span 513–522 mV.'
   '(see Finding: a three-line model from transistor flips to die temperature)' → '(see <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment'>the Horace experiment</a>, §8, A model from flips to temperature)'.
   'experimental work in this workspace relies on' → 'the measurements so far rely on'.

8. **[medium] sp-8** — *§3 row 5*

   Chip 'Solved in Math' (ok) → 'Not yet fitted' (action). Text → 'The fitted thermal model is lumped: six RC stages, 1.47 °C/W in total, one card in one chassis, driven by the chip-wide average. A 2D model (∂T/∂t = α∇²T + P(x,y)/C − (T − T_amb)/τ) needs lateral conductances and per-cell capacitances that only per-shire readings could fit.'

9. **[medium] sp-9** — *§3 row 3; §4 intro*

   Chip → 'Untested'. Text → 'BL1 and BL2 verify a certificate and signature against a public-key hash in OTP (crypto_rot.c / VaultIP) unless an OTP chicken bit is set, and neither the signing tool nor a test key is in the open tree. Whether these lab cards accept a rebuilt image is unknown until someone tries, and a bad image can brick the boot path, so reflashing is a lab-admin decision (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#improve'>the firmware caveat</a>).'
   §4 intro: 'Until custom SP firmware can be signed and flashed' → 'Until a modified SP firmware can be flashed (whether these cards require a signed image is untested)'.

10. **[medium] sp-10, nl-28** — *§1 register list; §4 items 1 and 3*

   Replace the raw LaTeX: '($0$ to $4095$)' → '(0 to 4095)'; '$0.061\ ^\circ\text{C}$' → '0.061 °C'; '$T \to T+1\ ^\circ\text{C}$' → 'T to T + 1 °C'; '$+0.65\text{ W}/^\circ\text{C}$' → '+0.65 W/°C'.

11. **[medium] sp-11, sp-14, nav-18, nav-11, nav-13** — *after the KPI row; byline; References footer; end of page*

   Add <p class='small'><b>Terms.</b> A <b>shire</b> is a tile of 32 <b>minion</b> cores (small RISC-V cores with vector and tensor units) sharing 4 MB of SRAM (L2, an L3 slice and scratchpad). The 34 minion shires, the I/O and PCIe shires and 8 memory shires sit on the chip's mesh network. The <b>service processor (SP)</b> is the on-chip management core; its second-stage firmware (<b>BL2</b>) reads the sensors and answers the host. The <b>PMIC</b> is the board's power controller; <b>PVT</b> = process, voltage and temperature monitors. More in the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#terms'>hub's glossary</a>.</p>
   Byline → 'Technical brief · 22 September 2026 · firmware source et-platform 353f20e, open RTL core-et b38a1a3 · part of the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability'>ET-SoC-1 measurement reports</a>'.
   References: state the commits ('external/ holds local clones of the vendor trees'). Link docs/findings/11-thermal-model.md to its GitHub blob URL.
   Add a Related reports list:
   - the hub §4.3 (#what-the-moortec-sensors-can-and-cannot-do-for-power)
   - Power and temperature §3
   - the Horace experiment §8
   - The DVFS loop and the leakage (the governor reads the averaged sensor)
   - On-chip communication (the mesh map)
   - Heat per millimetre (#die)
   Paste the section-anchor script. Title → 'Spatial temperature: a brief · ET-SoC-1'.

12. **[low] sp-12** — *§3 row 4*

   'Extend tools/ettelem (which already queries libDM and reads the SP binary trace at 45 Hz)' → 'Extend tools/ettelem (which samples libDM at 10 Hz, about 45 Hz at most, and dumps the SP trace buffer on demand with ettelem sptrace)'.

13. **[low] sp-13** — *§4 'Current Best Workaround: Temporal Reconstruction'*

   Item 1 → '…recovers the rise to about 0.03 °C on repeated runs, and the heating power to about 1 W of the electrical measurement.'
   Item 2 → 'Counting operand-driven toggles in the open FMA RTL (the Erbium branch, same Minion core lineage) predicts board power over idle to 0.5 W rms leave-one-pattern-out, and 0.9 W rms on 14 matrices predicted before they ran.'
   After the list: 'All three sharpen the chip-wide average; none says where on the die the heat is.'

14. **[low] known: phone overflow** — *whole page CSS*

   Fix the known 15–22 px sideways overflow at 390 px width while republishing.

### 3.21 published-only:david-kanter-power-brief

Files: `live HTML: scratchpad/audit/live/david-kanter-power-brief/index.html (no repo source), space f3533740-5ad9-45e1-927c-098dbbe5c210`

1. **[high] kan-1, kanter-1, kanter-privacy, nav-04, hub-18** — *whole page (visibility decision); title, lede, §1, §2 heading/column, §3, §4, closing*

   Owner decision (open question 1).
   Option A, recommended: set the space private (npx spacesheep share f3533740-5ad9-45e1-927c-098dbbe5c210 --visibility private). The hub group removes its Related entry; the findings group updates 01-resources R9 and 04-artifacts. The DVFS report remains the public account of his claims. Nothing else in this group applies.
   Option B, redacted republish:
   - title and h1 → 'Notes from a conversation with David Kanter: power, leakage and MLPerf';
   - eyebrow → 'Conversation notes · 20 September 2026 · part of the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability'>ET-SoC-1 measurement reports</a>';
   - lede → 'Notes from a ~25-minute conversation with David Kanter (MLPerf / MLCommons) on 20 September 2026, written up on 22 September and cross-read against the ET-SoC-1 power findings. His words are paraphrased from memory and were not reviewed by him; short quotes are marked. Six of his statements were then checked against the firmware, the RTL and the card in <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>The DVFS loop, and the leakage</a>.';
   - delete the party/venue clause, the sentences beginning 'Context he volunteered:', all of §4, and the 'Tied to the north star' paragraph;
   - in §3 bullet 2, delete 'That distinction is the sentence to lead with when you write to him.';
   - §2 heading → '2. Eight points from the conversation, and what the ET-SoC-1 data says'; column 'What you said or assumed' → 'What was said or assumed';
   - replace 'you/your' with 'the asker' or 'this work' throughout;
   - keep the noindex meta only if the owner wants it.
   The changes below apply under option B only.

2. **[medium] kan-2** — *one-line version; §2 row 8 third column*

   Row 8 → 'What he adds, for a mature chip: its internal power estimator counts switching activity. The ET-SoC-1 has none; its loop reads the PMIC's measured board power once per ~133 ms pass (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>DVFS report §1</a>), so there is no activity counter to expose.'
   One-line version: after 'that a chip's power estimator already lives inside its DVFS loop' add ' (true of mature parts; on this chip the loop reads a meter instead, as the DVFS report found)'.

3. **[medium] kan-3, kanter-2, reg-m2, kan-6, nav-04** — *header; after the one-line version; §2 references; spatial link*

   After the one-line version add <p><b>What checking found</b> (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>The DVFS loop, and the leakage</a>): DVFS loop — confirmed (600/700/800 MHz at 0.517/0.568/0.618 V); activity-based power estimate — not on this chip; thermal sensors in the loop — confirmed, and thermal wins; leakage-suppression hardware — in the open RTL, tied off; leakage 5–30% — this card is worse (36% busy, 64% idle at 80 °C); leakage costs power, not correctness — consistent, weakly tested.</p>
   The link 'spatial-temperature brief, 22 Sep' → href https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief.
   '13-why-low-power.md' → <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power'>Why is the ET-SoC-1 low power?</a>.
   '15-earlier-findings.md' → <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#bits'>Limits of observability §3</a>.
   'Monday's fit' → 'the 21 Sep leakage fit (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment#a-model-from-flips-to-temperature'>The Horace experiment §8</a>)'.

4. **[medium] kan-4** — *§2 row 1 third column*

   'A provisioned-power view would add a host CPU and overhead factor to both, and shrink the ratio.' → 'A provisioned-power view adds a host CPU, network and overhead factor to both. A multiplicative overhead leaves the ~5× unchanged, and a fixed host share widens it, since the ET-SoC-1 has 28× fewer FLOPs per second to spread it over.'

5. **[medium] kan-5** — *§2 row 2 third column*

   → 'Reading this card's power is cheap: the PMIC meter the governor already uses is one query away (<a href='https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'>DVFS report §5</a>). A <i>repeatable</i> number is what is expensive: pre-heat to 80 °C, wait out the rails' one-second filter, keep a single telemetry opener, correct whole-degree rounding by step times. A competition must either supply that protocol or normalise by provisioned power.'

6. **[medium] kan-7** — *§2 row 3 third column*

   Delete 'The MNIST-joules result that >99% of a run's energy is idle power is the same fact.' unless the owner supplies a source and the hardware it ran on (open question 9).

7. **[medium] sp-9** — *§2 row 6; §3 last bullets*

   'and the firmware is signed' → 'and changing that needs a reflash whose signing requirements on these cards are untested'.
   'Park it until a signing key or an unlocked engineering card exists' → 'Park it until a reflash is cleared with the lab admin'.
   'Thermal placement is a firmware-signing problem.' → 'Thermal placement is a firmware problem: it needs a reflash that is the lab admin's call.'

8. **[low] kan-9, dvfs-16, nl-14, wlp-8, dvfs-14** — *§2 rows 3 and 5; 'Two things were not misconceptions' paragraph*

   Row 5: '37% of a 63 W random-data run, 64% of idle' → '36% of a 64 W random-data run, 64% of idle'.
   Row 3: '25.6 mW/minion at 256–768' → '25.6 mW per minion at 256 and 512 active, 26.2 at 768, 27.0 at 1,024'.
   Replace '(your memory anatomy: L2 SRAM 0.3 pJ/bit against LPDDR4x 18 pJ/bit, L1 46 pJ to DRAM 5.1 nJ per 64 B load)' with '(the <a href='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy'>energy manual</a>, at 600 MHz on both cards: L1 0.77, L2 2.51, L3 10.5 and DRAM 122 pJ per byte, a 160× span)'.

9. **[low] kan-8, kan-10, kan-threads-1** — *§2 row 7; §1 paragraphs 1–3; §1 intro*

   Row 7: 'the per-shire voltage map you pulled from the SP debug log is the MSR-equivalent' → 'the nearest thing to MSRs here are the service processor's PMIC and PVT readings, which the host reads through the management library, and the CSR/ESR performance counters; per-shire voltages reach the host only as SP debug-log lines'.
   §1: append '(his figure; not checked)' after 'Only two of 27 submitters filed MLPerf Power results last round'. '8–9 kW, not 7.5' → '8–9 kW, not 7.5 (his numbers; "only a third" would put it nearer 10 kW)'. Leave the MLPerf Endpoints / PR #87 sentence as it is.
   'Six threads, in the order they came up.' → 'Eight threads, in the order they came up.'

## 4. Do not change, and open questions

### 4.1 Do not change

REFUTED FINDINGS (do not apply)
- nl-29: the leakage shares 65% (energy manual, of the law's 35.9 W), 64% (DVFS, of 36.3 W measured) and 37% (Kanter brief, of 63 W) each match their stated denominator; do not homogenise them. The Kanter row still changes to '36% of a 64 W run' (kan-9), but only because the run was 63.9 W.
- nl-30: '160 MB of on-die SRAM' is Esperanto's own sourced figure (Hot Chips 33; the GPU notes record 160 against the datasheet's 140). Keep it, attributed; the SRAM rail feeds 128 MB of shire SRAM.

PARTS OF CONFIRMED FINDINGS THAT WERE REJECTED (the proposed text was wrong)

The hub:
- nav-28: ridge points was computed 18 Sep (Q43 is dated 09-18). Keep '18 Sep' in the hub and 04-artifacts; only add 'published 24 September'.
- nav-06: do not write 'hop distance costs no bandwidth'. The relay varied the shire-ID offset, not the hop count.
- hub-30: do not change '60×/s' to '45×/s'; 45 Hz is ettelem's six-command sample, not one poll.
- nav-19, nav-17, nav-26 and the original pt-2 banner said 'the service processor keeps each rail as a first-order average'. The firmware shows the SP only copies the PMIC's average (hub-4). Use the PMIC wording.
- hub-5: Horace He's post is about GPU matmuls running faster on predictable data, not about 'matmul power'.

The energy manual:
- em-11: do not use the per-configuration 0.33/1.52 W leak corrections. Use the burst-level 0.40/1.80 W (a2) and 0.16/0.78 W (a3).
- em-14, heat-1, nl-8: keep the catalogue's 1–8-hop wire fit as published, and add the 1–6-hop sentence, unless the owner asks for a refit (open question 6). Do not keep 'the one number the cards agree on': refit over 1–6 hops, the cards differ by 11%.
- em-5: EC_SPIN increments seven registers at 0.386 instructions per hart per cycle, not 'eight registers every cycle'.
- em-7: the vector lane minus issue is 6.3–6.4 pJ (with the nop/fence floor), not 6.1–6.3.
- em-29: frcp.ps issues at 0.4× the one-cycle rate, not 'a half'.

The Horace experiment:
- horace-4: no data shows that 'a couple of long runs' would fit a new card's thermal network.
- horace-5: the model cannot tell a warmer room from worse airflow, so name no single cause.
- horace-7: the leakage law's fitted range is 64–88 °C (62 °C is the thermal anchor), and the extrapolation is 7–14 °C, not 5–12.
- horace-12: the '9%' is the time to 90 °C on held-out runs, not 'ten-minute runs'.
- horace-15: the service processor is an on-die management core, not 'the card's management microcontroller'.
- hub-7: the reviewer summary's '10⁶–10⁸' is wrong; the fix sentence (a million, ten thousand, 10¹²) is right.

Why low power:
- wlp-3: 'the slide's 0.040 nF excludes leakage' is an inference; say what P/(V²f) gives instead.
- wlp-8: do not add 'the last rising as the die warms' (analyze_ablation.py already corrects to the launch temperature).
- wlp-17: the research note's 'HBM2e 1.6–2.0 TB/s' (line 33) is correct; leave it.

The DVFS report:
- dvfs-1: the time split is 5.6 / 1.0 / 0.8 s in a 7.4 s run, not '6.5 of 7.4 s'.
- dvfs-5: back-to-back launches 'rarely' trigger the reset, not 'do not'.
- dvfs-7: do not claim aifoundry3's frequency floor is below 600 MHz. The throttle-log format comes from older firmware (dvfs-fw).
- dvfs-8: do not state as fact that the controller closes idle rows after 2 µs (the source hedges).
- dvfs-9: '1,773 launches' is not all of them; say 'every launch record'.
- nar-8: the DVFS verdict is 'consistent, weakly tested', not 'not tested'. The matmul and relay results were checked.

Power and temperature:
- pt-2: the 0.8 W/°C is the first Horace session's fit at 79–90 °C, not 'the slope in the upper 80s where this matmul ran'.

The hot line and the L2 brief:
- hl-2, nav-01: the L2 brief does not recommend flipping l3_yield ('Should it be fixed? No'); do not say it does.
- l2-1, l2-4: the threshold is about 24 remote requesters; 20 still leave the host at 98.9%.
- l2-2: the pacing figures are 54% at 10,000 cycles and 95% at 16,000, not 96%. 17-hot-line.md's table is wrong there (hot-pace-1).

The relay and Heat per millimetre:
- nav-23: the relay's hand-off is not 'one hop'; it averages 3.5 hops.
- heat-2: a flit is not 'what one link carries in one cycle'; say 'at least one 64-byte line'.
- heat-3: the master shire is enabled (it runs the firmware); only the spare is idle.

Memory anatomy:
- anat-3: the SP trace does not read '16–25% below' the host meter in absolute terms; its rise above idle is 14–20% smaller.
- anat-6: do not advise 'take the fastest of repeated loads' (that picks the −128 glitches); take the median.
- anat-8: the 26–29% NoC coefficient is not all regulator loss.
- anat-11: do not assert why the memory-hierarchy chase ran faster in ns.
- anat-17: the dirty-evict minimum of 16 cycles is a single outlier; footnote it.

Memory hierarchy and on-chip communication:
- mh-2: memhier's spin (both harts) and nocbench's spin (hart 0) are different loops.
- mh-9: do not assert a '933 MHz controller clock'; say 'the 933 MHz DDR clock'.
- nl-3: the 800 MHz chases give 440–460 ns, so ~440 was not 'unsupported'; the page's '600–700 MHz telemetry during the runs' claim is the false part.
- noc-2: 2D arrays at shire grain are safe when each neighbour link gets its own minion. The fix adds that, not a blanket warning.
- noc-3: the energy manual's 'agrees within 10%' footnote is itself wrong; do not quote it.
- noc-4: energy manual §6 does not re-measure barriers 'with bars'.

Matmul efficiency and ridge points:
- matmul-1: '2.9×' is a different kernel at 80 °C; do not call it 'this benchmark on random data'. ±1/±2 is not the 'best case' (zeros and ones draw less).
- matmul-2: do not import 'about five times' into the matmul page without saying it is bf16 against fp32.
- ridge-1: manual.json tensor.rows are aifoundry2 only; use tensor.bars. L2's '4.28 measures the floor' is unsupported; the reason to replace it is the supersession.

Sparse compute:
- sparse-1: do not say the 18 Sep zero point 'reads 25% high'. It zeroed only A, so it is not comparable with Horace's all-zeros.
- sparse-3: the shared queue explains part of the 0.9 T/s ceiling, not the whole α range.
- sparse-7: do not keep a 'Figures often misquoted' list; delete the fact-check corrections.

The findings knowledge base:
- kb-1: 05-claims' 'E15, R4' citation for 546/318 cycles is correct (R4 includes the sparsity report); leave it.
- nav-09: E24 did run on aifoundry3. Both onchip-*/sweep.jsonl files have 2 'probe' rows (verified), so use fr-3's list, not nav-09's.
- fr-8: do not add a 'Command:' line for a script that does not exist.
- fr-15: the findings README now says 18–24 September, so getting-started says 18–24 too.
- fr-38: the 68 °C evidence is E10 (clock stepped up at readings up to 67 °C), not the discarded reruns.
- fr-11: the test drive has no embedded JSON.

The spatial brief:
- sp-6: the TensorSend round trip does fit 150 + 12.02 × distance within 1.1 cycles over all 496 pairs. The 12–16-cycle 'asymmetry' is the memory-hierarchy chase artefact (mh-1). Keep the precise fit, not a hedge.

KEEP AS IS
- Every slug, including the date-prefixed 2026-09-22-et-soc1-l2-mainline-starvation.
- Every space uuid.
- The embedded 18 Sep memhier data in the memory-hierarchy page, until ridge-points.py stops reading it (ridge-1 switches it to the manual's data).
- Numbers the reviewers recomputed and found exact, which need no edit: the idle law, the 73 °C rail split (31.79 W, 15.10 W unmetered), the unmetered-fit coefficients, the droop regression, the relay and hot-line timings and shares, Horace's 14-pattern table, the Foster fit, the 0.924 transfer, the ridge-point arithmetic, the matmul rates, the sparse-compute timings, the heat-per-mm coefficients, the on-chip fits (150 + 12.02 × distance), and memory anatomy's ladder, refresh period, row conflict and PA mapping.
- Horace redeploys must include the GIFs that were just restored.

### 4.2 Open questions for the repo owner

1. The David Kanter brief. It is a personal memo about a named person (party hosts, his career plans, friends' employers, the author's to-dos), and the hub links it publicly. It carries a noindex tag, and Q40 appears to have made it public as a side effect. Should it be set private and removed from the hub (recommended), or republished in the redacted form in its group? The hub, DVFS, findings (R9, 04-artifacts) and Kanter groups all wait on this.

2. Firmware version. The DVFS report reads the governor at et-platform 353f20e, but aifoundry3's trace strings exist only before et-platform commit 60b40c10f (24 Sep 2024), and both cards report release 1.3.1. Which commit do the cards run? Should DVFS §1, §5 and §6, and findings 14 and 16, be re-read against 60b40c10f^ or the 1.3.1 tag? The plan adds a caveat only.

3. Method disclosure on the hub. Were the seven 'scouts' and the 'two independent reviewers' AI agents? The trail (scratchpad paths, Claude co-author trailers) suggests so. If yes, approve the rewording in hub-11.

4. The L2 mainline-starvation brief. Keep it, corrected in place with the 'Update' banner (the plan's default), or unpublish it and drop its hub row, since the hot-line report supersedes its headline?

5. The unmetered fit (E30). No committed script writes unmetered_fit.json. Should the 30-line reconstruction the verifiers used be committed as tools/ettelem/fit_unmetered.py, or should the repo record 'run inline, not reproducible'?

6. The energy manual's wire slope. Keep the 1–8-hop fit (1.81 pJ/B per hop) with a 1–6-hop note pointing to Heat per millimetre (the default), or refit analyze_catalogue.py over 1–6 hops (2.29 / 2.09) and regenerate the manual?

7. Ridge points. Regenerate the energy-balance table from the manual's data by changing scripts/ridge-points.py (the default), or only add a note that the 18 September energies are superseded?

8. Naming. Is it fine to name Ivan as @ivanchernobyl on the hot-line page (the L2 brief already does), and to keep naming 'marty1885' for the shire map?

9. Sources for two third-party claims. The Kanter brief's 'MNIST-joules result that >99% of a run's energy is idle' has no source in the repo; supply one or delete the sentence. On-chip communication's 'marty1885 found that systolic matmul and FlashAttention ran no faster': cite Chang's post, or cut the sentence (the default).

10. Data files. May the plan regenerate docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json (category rename, hours_idle) and edit hotline.json's errata text? These change 'raw' analysis outputs.

11. Visibility. Confirm that every hub-linked space should be public. The root README and getting-started still tell maintainers to make eight spaces, and matmul efficiency, private. After each redeploy, compare npx spacesheep list with 04-artifacts.md.

12. The long idle. The plan writes 'about 20.5 h' (E16 ended 15:08 on 21 Sep; the idle sample was at 11:44 on 22 Sep; E18's 4.9 s probe ran just before it) in six places that now say 20.4 h. OK, or is there a source for 20.4?
