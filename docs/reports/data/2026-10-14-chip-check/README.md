# A correctness check of the chip diagram (14 October 2026)

Request Q115 ([`02-requests.md`](../../../findings/02-requests.md)). The owner, about 09:45 PDT: "Do the
in-depth check of the chip for correctness https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram and apply fixes",
with the AI Foundry hub for where the ground truth and the manuals are. At about 14:55: "I've had Codex make some
suggestions, and they're in the discussion tab ... Go through the suggestions/fixes and implement everything which is
appropriate." No card time beyond one read-only query of aifoundry2's static configuration (`tools/etcfg`), held under
the card's lock for under a second.

## What was checked, and against what

Every one of the page's 1,117 facts (the chip's 304 and the deep zoom's 813), the panels of all 103 scales (every part's
panel, read after a real click in headless Chrome, its "More detail and the sources" opened: 629 parts), every stage of
the eleven flows, the 17 tour slides, the page's prose, its tables and its drawings (a screenshot of every scale and stage).
The ground truth, most authoritative first: the vendor manuals in `external/et-man` (the datasheet, the Programmer's
Reference Manual, the introduction, the Minion overview, the PCIe card, the errata); the core-et design documents
(`external/core-et/docs`, the Erbium branch's: the shire cache, the minion shire, the neighbourhood, the VPU, the DCache,
ET-Link, the DLL); the RTL (`external/core-et` at `b38a1a3`, `external/core-et-main`); the firmware and runtime
(`external/et-platform` at `836a4ab`); this repository's measurements and ledger; and, for the generic physics and the
levels outside the chip, primary public references.

Eleven checkers took a slice each and reported what was wrong with exact quotes, the evidence and a fix; an independent
skeptic per slice then tried to refute every finding and corrected the fixes. 99 findings, **97 stand** (46 confirmed as
reported, 51 real with a corrected fix), **2 refuted**:

| Slice | Facts | Panels | Flow stages | Findings | Major | Minor | Refuted |
|---|---:|---:|---:|---:|---:|---:|---:|
| The die and the mesh | 132 | 92 | 0 | 15 | 1 | 14 | 0 |
| A shire | 95 | 133 | 0 | 10 | 2 | 8 | 0 |
| A minion | 92 | 110 | 0 | 9 | 1 | 8 | 0 |
| DRAM and the latency ladder | 70 | 80 | 19 | 7 | 1 | 6 | 0 |
| Messages between shires | 46 | 5 | 28 | 7 | 2 | 5 | 0 |
| Host link, clocks, power, energy | 63 | 44 | 20 | 5 | 2 | 3 | 0 |
| Memory cells (deep zoom) | 226 | 181 | 0 | 12 | 1 | 11 | 0 |
| Textbook circuits | 87 | 102 | 0 | 5 | 0 | 5 | 0 |
| Transistor, silicon, particles | 149 | 64 | 0 | 12 | 0 | 12 | 0 |
| Outside the chip | 157 | 87 | 0 | 12 | 1 | 9 | 2 |
| Prose, tour, page-wide | 101 | 19 | 67 | 5 | 0 | 5 | 0 |
| **All** | | | | **99** | **11** | **86** | **2** |

**The eleven major ones**, each now fixed:

- **The die plot is not the die view's mirror** (`die-plot-is-not-the-mirror`). The page called the published die plot a
  mirror image; it keeps the PCIe and I/O cells at the same east end and only swaps the two.
- **The shire's crossing into the mesh was drawn as another crossing** (`xing-drawing-is-the-wrong-crossing`). The
  mesh stop's scale drew the neighbourhood's semi-synchronous FIFO (same clock, half a cycle apart, no synchroniser); the
  crossing into the 400 MHz mesh is the shire cache's VCFIFO with two-stage synchronisers on its counts. Each now has its
  own scale (`shire.neigh.xing` is new).
- **An L3 request takes the lane of its home bank, PA[12:11], not PA[7:6]** (`mesh-lane-is-not-pa76-for-l3`): PA[7:6] picks
  the lane only for a remote-scratchpad request, by the RTL L103 itself cites; an aligned 1 KB L3 load uses one lane.
- **The TensorSend ready bit is the sender's** (`ready-bit-direction`): the hang is a minion sending to two partners
  whose readies arrive before it used the first, not one receiving from two.
- **The DRAM model's 93-97% is of lines, not loads** (`dram-model-within3-lines-not-loads`): each line scored by its fastest
  of three loads; of single loads, 83% on aifoundry2.
- **The relay's pJ/B is per byte moved, each byte counted written and read** (`relay-energy-per-byte-moved-not-per-handoff`):
  a hand-off costs 17.8 pJ per byte, not 8.9.
- **In the relay the next shire pulls** (`relay-mechanism-pull-not-push`): it reads the previous shire's scratchpad, so the
  data cross the mesh as load replies, y first; the page drew a push, x first.
- **Flow 8's matmul runs at about 9.2 TFLOP/s on the device, not 9.51** (`flow8-horace-device-rate`): it holds B in the L1
  scratchpad (546 cycles an op); 9.51 is flow 7's benchmark, which streams B through TenB (529).
- **The 90 °C cap was the run script's, not the firmware's** (`heat-race-firmware-cap`).
- **JEDEC's all-bank refresh for 16 Gb per channel is 380 ns** (`dram-jedec-trfc-280`): the programmed 280.7 ns is
  Micron's own rating for its die, not a cross-check on the density.
- **The card's 88 W is a budget, not a ceiling it keeps** (`card-power-88w-stale`): an overheating idle card drew 134 W.

The other 86 are smaller: a number misquoted from its source, a stale caveat newer data settled, a citation to the wrong
page of a manual, a mislabelled kind, a drawing detail (the textbook adder ignored its carry-in; the west memory shires'
drawing faced the wrong edge), arithmetic (four 4:1 mux levels are 256:1, not 128:1) and physics (the electron's charge
limit, the FinFET's work function). Every one, with the page's words, the evidence, the fix and the skeptic's reasoning, is
in `findings.json`; the table at the end lists them.

## The line citations

Many facts cite this repository by line ("`docs/findings/05-claims.md:366`"), and the cited files had grown since 26-30
September: 416 such citations, of which about 250 no longer pointed at what they cited. `tools/citecheck.py` scored each
citation against its fact at HEAD and in every committed version of the file and proposed where the text went; four
readers then settled every flagged citation by reading the lines (the tool was right most of the time, wrong where a
ledger row was duplicated or superseded): **181 remapped, 72 confirmed as they were**, and 15 more found outside the
facts' sources. All 181 are in the rebuilt facts (two superseded by findings that rewrote their facts). `citations.json`
has every one, with the text at the new lines.

## Codex's audit

Codex's review of the same page (Discussion topic 2 on the space; its report https://spacesheep.dev/@yaroslavvb/et-soc1-diagram-audit)
made 68 observations. Each was checked against the sources as the findings were: **40 implemented**, **7 already covered**
by the findings, **4 rejected** with evidence (L07, L14, L22, L27), and **17 left for the owner**, being redesigns or
changes of the page's conventions (the readable explorer for phones, a new notation for evidence, named destinations for
the easter egg's levels, and so on). Among the implemented: the teaching circuits' broken connections (the 6T cell's and
sense amplifiers' drain joins, the full adder's taps, the ECC's overall parity, the Booth selector's zero), the electron's
charge sign, electrons against conventional current in the transistor views, five fixes to the 3D companion (the
cutaway that announced a change it did not make, browser shortcuts the canvas swallowed, "Reset view", a mislabelled live
line, carriers that moved while paused), and **aifoundry1's card 1 has 16 GB of DRAM, not 32** (its error log reports
17,085,497,344 bytes against 34,265,366,528 on the other two cards). `codex-triage.json` has every decision and its
reason.

The 17 left for the owner, with what each would take:

| Codex | What it asks | Why it waits for the owner |
|---|---|---|
| I06 | a readable layout for the deep diagrams on a phone (its explorer proposal) | a redesign; the page's own choice is pinch to enlarge, or tap a part for its details |
| I07 | a keyboard-operable evidence drawer for every number | a new interaction model |
| I08 | tour links that keep the tour's context | a link-format feature |
| I09 | one vocabulary for the evidence kinds on both pages | a change of convention across both pages |
| I13 | page scrolling that starts over the 3D canvas on a phone | the canvas takes every gesture by design, and says so |
| I14 | larger tour dots or a labelled step navigator | a style change (the dots are labelled for screen readers) |
| I16 | no animation work while the stage is off screen | a performance change, not a defect |
| L13 | Studio 45's outside dimensions told from its rooms' | a small ambiguity the labels mostly handle |
| L15 | one visual language for enlarged and schematic markers | a style change |
| L26 | every size labelled as a width, height, spacing, diameter or bound | a change of the page's size convention |
| L28 | dates on hardware states and recorded maxima | the concrete errors are fixed (the 88 W, the idle range, Voyager's date) |
| L29 | pinned primary links with assumptions and confidence limits | a sourcing policy |
| R02 | named zoom destinations by default | against the owner's decision of 1 Oct: the levels above the rack are an easter egg |
| R03 | a legend for each scene | a layout convention since the first version |
| T10 | binary units for capacities, decimal for bandwidths, written out | the page already follows one convention, the lab's reductions' |
| T11 | a scope line always visible in each frame | a frame convention |
| T12 | reproducible permalinks for every source | a new feature of the fact system |

## How the fixes were made and checked

Six fixers, each owning a disjoint set of source files, applied the findings and the citations; a second pass applied
Codex's; every fix went into the file that generates the text (the research builders and their JSON, `build_facts.py`'s
tables, the page scripts, the memory levels' kit, the ladder's research), never a generated file. Then the whole chain
was rebuilt (`tools/buildchain.sh`: the ladder, the memory levels' research, the chip's research, then the inside,
outside and both pages' facts three times to their fixed point, then both pages); before any edit the same chain
reproduced the committed pages byte for byte, so every change after is a fix's. The page was crawled again and
`tools/crawldiff.py` listed every text a reader sees that changed: 656 of the 1,859 texts a reader sees changed between the morning's crawl and the final one (`crawl-diff.md`), the rest byte for byte the same. Five auditors then checked that
every fix landed, that every changed text is explained by a fix, and that no new text is wrong: 144 of the fixes in their scopes landed and are right, one had landed in part (the summary slide's legend overran its box at 23 px labels) and one with a misworded note (E57's 14 of 15 conditions); they found ten new small errors in the rewritten texts (a citation to "process.json beside this file", the memory levels page still filing the relay under remote stores, the 2 GB channel geometry not scoped to the 32 GB cards, a relay price given two ways in the summary, the NoC bridges' counters overstated, an MR8 value the cards never reported, among them) and six changes they first could not place, all benign. The ten were fixed and the page crawled once more: eleven texts changed, each the intended fix, and nothing else.

**The suites, on the final build** (served locally with a favicon, so a missing one is not counted as a page error): `tools/pagemotion/zoom_test.mjs` 783/783, `ml_ladder_test.mjs --chip` 150/150, `ml_access_test.mjs` 28 accesses of 28, and `zoom_static.py` clean on both pages (sizes, privacy, the images' hashes). Before any change: 779 + 4 "errors" that were the test server's missing favicon (783 with it) and 150/150. The 3D companion's build was checked to reproduce its committed page from its committed sources before its five fixes; its `quality-test.mjs` now opens the metal scene's cutaway after its dielectric, as the corrected control does.

## Files

| File | What |
|---|---|
| `findings.json` | the 99 findings: slice, key, severity, the skeptic's verdict, what the page said, what is true, the evidence, the fix, the skeptic's reasoning |
| `citations.json` | the settled line citations: fact, field, file, old and new lines, the text at the new lines, why |
| `codex-triage.json` | Codex's 68 observations: the decision, its reason and evidence, the fix |
| `fixes.json` | what each fixer reported: every item, its status and the file:line of each change |
| `crawl-diff.md` | every text a reader sees that changed, before and after, as a word diff |
| `tools/` | the check's own scripts, as they ran (their paths point at the session's work folder, `~/claude/work/chip-check-1014`, not committed): `crawl.mjs` and `shots.mjs` (what a reader sees, through `tools/pagemotion/cdp.mjs`), `partition.py` (the slices), `citecheck.py`, `crawldiff.py`, `splitdiff.py`, `buildchain.sh`, `postfix.sh`, the routing and merging scripts, and the checkers' and fixers' briefs |

## The full lists

| Finding | Slice | Severity | Verdict |
|---|---|---|---|
| `die-plot-is-not-the-mirror` | s01-die-mesh | major | partly |
| `mesh-lane-is-not-pa76-for-l3` | s02-shire | major | partly |
| `xing-drawing-is-the-wrong-crossing` | s02-shire | major | partly |
| `ready-bit-direction` | s03-minion | major | confirmed |
| `dram-model-within3-lines-not-loads` | s04-memory | major | confirmed |
| `relay-energy-per-byte-moved-not-per-handoff` | s05-messaging | major | partly |
| `relay-mechanism-pull-not-push` | s05-messaging | major | confirmed |
| `flow8-horace-device-rate` | s06-host-power | major | partly |
| `heat-race-firmware-cap` | s06-host-power | major | confirmed |
| `dram-jedec-trfc-280` | s07-memlevels | major | partly |
| `card-power-88w-stale` | s10-outside | major | partly |
| `cdyn-target-ie-arithmetic` | s01-die-mesh | minor | confirmed |
| `flit-width-stated-as-spec` | s01-die-mesh | minor | confirmed |
| `free-link-bit-energy-two-values` | s01-die-mesh | minor | partly |
| `grey-cells-called-unidentified` | s01-die-mesh | minor | partly |
| `harts-formula-minion-two-meanings` | s01-die-mesh | minor | confirmed |
| `link-bit-sync-panel-and-label` | s01-die-mesh | minor | partly |
| `link-capacitance-mixes-board-power` | s01-die-mesh | minor | partly |
| `map-to-die-is-a-transpose-not-a-turn` | s01-die-mesh | minor | confirmed |
| `measured-facts-card-not-recorded` | s01-die-mesh | minor | partly |
| `memshire-stops-have-7-router-layers` | s01-die-mesh | minor | partly |
| `mesh-scale-size-is-the-whole-grid` | s01-die-mesh | minor | confirmed |
| `noc-bridges-do-have-counters` | s01-die-mesh | minor | confirmed |
| `pvt-36th-sensor-is-drawn-in-pcie` | s01-die-mesh | minor | partly |
| `transistor-upper-bound-rounded-down` | s01-die-mesh | minor | confirmed |
| `dll-delay-lines-misdescribed` | s02-shire | minor | confirmed |
| `parts-open-another-parts-panel` | s02-shire | minor | confirmed |
| `path-widths-rejoin` | s02-shire | minor | confirmed |
| `rbuf-misquote` | s02-shire | minor | confirmed |
| `stale-tab-reference` | s02-shire | minor | partly |
| `uc-fast-credit-counters-not-in-uc` | s02-shire | minor | confirmed |
| `wrong-line-citations` | s02-shire | minor | partly |
| `xing-blurb-every-bit-two-flops` | s02-shire | minor | confirmed |
| `fma6-kind-measured` | s03-minion | minor | confirmed |
| `int-regfile-latches-ports` | s03-minion | minor | partly |
| `l1d-writeback-source` | s03-minion | minor | confirmed |
| `no-divide-64bit-float` | s03-minion | minor | confirmed |
| `prm-store-bypass` | s03-minion | minor | partly |
| `stale-line-citations` | s03-minion | minor | confirmed |
| `tenb-tenc-placement` | s03-minion | minor | partly |
| `tensor-shape-B-path` | s03-minion | minor | confirmed |
| `dram-capacity-8-to-32` | s04-memory | minor | partly |
| `dram-chip-share-stale-25-28` | s04-memory | minor | partly |
| `e48-not-published-stale` | s04-memory | minor | partly |
| `jedec-trfcab-16gb` | s04-memory | minor | partly |
| `memshire-west-drawing-mirrored` | s04-memory | minor | partly |
| `stale-line-citations` | s04-memory | minor | partly |
| `L86-stale-plus-minus-50` | s05-messaging | minor | partly |
| `L94-733-stale` | s05-messaging | minor | partly |
| `relay-bw-note-below-L3` | s05-messaging | minor | confirmed |
| `routing-order-measured-on-two-cards` | s05-messaging | minor | confirmed |
| `stale-line-citations` | s05-messaging | minor | partly |
| `e-fexp-ps-no-divide` | s06-host-power | minor | confirmed |
| `stale-claims-line-citations` | s06-host-power | minor | partly |
| `temp-sensors-prm-citation` | s06-host-power | minor | confirmed |
| `dram-91-cycle-split-inconsistent` | s07-memlevels | minor | partly |
| `example-line-drawn-in-wrong-instance` | s07-memlevels | minor | partly |
| `l103-lane-rule-vs-l3-lane` | s07-memlevels | minor | partly |
| `l2-data-ram-way-set-order` | s07-memlevels | minor | partly |
| `l3-clock-gating-kind` | s07-memlevels | minor | confirmed |
| `latch-read-mux-levels` | s07-memlevels | minor | confirmed |
| `out-latch-panel-is-sense-amp` | s07-memlevels | minor | partly |
| `pa-map-pa17-aifoundry2-e57` | s07-memlevels | minor | confirmed |
| `rbuf-enabled-cites-commented-code` | s07-memlevels | minor | confirmed |
| `scp-panel-count-mbit-units` | s07-memlevels | minor | partly |
| `stale-line-refs-28-facts` | s07-memlevels | minor | partly |
| `s08-adder-brent-kung-levels` | s08-circuits | minor | partly |
| `s08-decoder-size-note-few-um` | s08-circuits | minor | confirmed |
| `s08-ipart-default-kind-documented` | s08-circuits | minor | confirmed |
| `s08-ks-adder-cin-only-to-s0` | s08-circuits | minor | partly |
| `s08-rom-trans-tables-not-nor-rom` | s08-circuits | minor | partly |
| `el.bus-bit-note-inverted-bound` | s09-device-physics | minor | confirmed |
| `electrons-table-labels` | s09-device-physics | minor | partly |
| `gate.metals-finfet-work-function` | s09-device-physics | minor | confirmed |
| `in.lib-stale-kinds-and-sources` | s09-device-physics | minor | partly |
| `nucleus-million-times-a-bond` | s09-device-physics | minor | confirmed |
| `p.dopant.7-patent-wells` | s09-device-physics | minor | partly |
| `planck-ruler-diameter-radius` | s09-device-physics | minor | confirmed |
| `planck-sixteen-vs-fifteen-decades` | s09-device-physics | minor | partly |
| `quark-under-a-two-thousandth` | s09-device-physics | minor | confirmed |
| `si.mobility-vsat-source` | s09-device-physics | minor | confirmed |
| `siliconics-slide-numbers` | s09-device-physics | minor | confirmed |
| `wikichip-wiki-claims-cited-to-other-sources` | s09-device-physics | minor | partly |
| `devcard-pdf-page-citations` | s10-outside | minor | partly |
| `host-board-models-stale` | s10-outside | minor | partly |
| `intel14-gate-pitch-rocket-lake` | s10-outside | minor | partly |
| `localgroup-diameter-misattributed` | s10-outside | minor | confirmed |
| `package-section-height` | s10-outside | minor | confirmed |
| `ring-arrival-note-wrong-scale` | s10-outside | minor | partly |
| `stale-line-citations` | s10-outside | minor | confirmed |
| `universe-radius-source-this-script` | s10-outside | minor | confirmed |
| `us-map-arc-hidden` | s10-outside | minor | confirmed |
| `card-dram-75` | s11-prose | minor | confirmed |
| `card-idle-range` | s11-prose | minor | partly |
| `electrons-intro-about` | s11-prose | minor | partly |
| `tour17-fact-count` | s11-prose | minor | partly |
| `versions-stale-14-oct` | s11-prose | minor | confirmed |
| `oldest-light-two-ages` | s10-outside | minor | refuted |
| `s45-mezzanine-length` | s10-outside | minor | refuted |

| Codex note | Decision | Covered by / reason, first sentence |
|---|---|---|
| I01 | implement | Two parts |
| I02 | implement | Confirmed in the current sources (the 3D companion was rebuilt on 14 Oct, Q113, after the audited snapshot; the defect survived) |
| I03 | implement | Confirmed in the current viewer.js: keyDown handles + = - _ R Home and the arrows and calls preventDefault with no modifier check, so with the canvas focused Ctrl/Cmd with + or - zooms the model and b |
| I04 | implement | tour17-fact-count (partly; applied in main): the Summary now counts as the honest text and the table do (the easter egg's 117 facts left out) and draws all kinds, the four named plus 'other', so its c |
| I05 | implement | Confirmed: the die.metal drawing's first group has six rows (the crawl's screenshot shows six) under the label 'M0-M4: the finest wires', which names five levels |
| I06 | owner-decision | A mobile redesign, against a documented choice: the page's 'On a phone' text says 'A minion's labels, and those of the circuits inside it, are small there: pinch to enlarge them, or tap a part for its |
| I07 | owner-decision | A new interaction model for provenance |
| I08 | owner-decision | A link-format feature for a documented limitation (Codex agrees) |
| I09 | owner-decision | A vocabulary and convention change across both pages |
| I10 | implement | Confirmed in the current sources: the Reset button calls viewer.reset() only, which restores the zoom and the perspective view and stops the orbit; the slider, cutaway, dielectric, selected material a |
| I11 | implement | Two parts |
| I12 | implement | Confirmed by running the real models.js on a stand-in for Three.js (IR-work/carriers-test.mjs, mock-three.mjs) |
| I13 | owner-decision | Intentional and stated on the canvas ('Drag to rotate · pinch or scroll to zoom'): the viewer sets touch-action none on the canvas and consumes every wheel event |
| I14 | owner-decision | A style change |
| I15 | implement | Three parts |
| I16 | owner-decision | A performance change, not a defect (Codex: 'a performance/battery recommendation, not a measured latency claim') |
| L01 | implement | Real, and none of our 97 findings has it |
| L02 | covered | planck-ruler-diameter-radius |
| L03 | covered | planck-sixteen-vs-fifteen-decades |
| L04 | implement | Real, and none of our findings has it |
| L05 | implement | Partly real |
| L06 | covered | localgroup-diameter-misattributed |
| L07 | reject | Codex is wrong |
| L08 | implement | Real, and the cited source contradicts the fact |
| L09 | implement | Real |
| L10 | implement | package-section-height |
| L11 | implement | Real, and a stale value in the ring's data |
| L12 | implement | Real, and a consistency fix the page's own conventions call for |
| L13 | owner-decision | The ambiguity is real, but small, and the labels already handle most of it |
| L14 | reject | Nothing drawn here is wrong |
| L15 | owner-decision | Codex calls this a visual-language improvement, not an error, and I agree |
| L16 | implement | Real |
| L17 | implement | Real, as an inconsistency on one panel |
| L18 | implement | Real, as an inconsistency between a drawing and its own fact |
| L19 | implement | Real, as a hidden switch of convention |
| L20 | implement | Real, as a contradiction on one panel |
| L21 | implement | electrons-table-labels (rows 2 and 8 of the electrons table and the lib.channel note, already applied in the working tree); electrons-intro-about (the table's intro); si.mobility-vsat-source (the 0.2  |
| L22 | reject | The page already keeps the two apart, and to scale |
| L23 | implement | Real |
| L24 | implement | Real |
| L25 | implement | Half real |
| L26 | owner-decision | A redesign of the page's size convention, not an error |
| L27 | reject | Codex's premise does not hold: every time on the stage already names its medium, and the network caveat is there |
| L28 | owner-decision | card-power-88w-stale and card-idle-range (out.card.6, out.host.5, the card subtitle, the host processor part: the 87.8 W and 88 W wording) |
| L29 | owner-decision | A general sourcing and badge policy, not a specific error |
| R01 | implement | versions-stale-14-oct (the Versions list and the byline; applied in main) |
| R02 | owner-decision | Against the owner's decision: the levels above the rack are an easter egg, never named in advance (ladder-core.js, 'the owner, 1 Oct 2026, 07:25'); Codex itself calls it a preference, not a broken rou |
| R03 | owner-decision | A layout convention: the die's key has sat under the panel on the chip's own three levels (die, shire, minion) since the first version, and the deep zoom (1 Oct) hid it only off them |
| T01 | covered | card-power-88w-stale (with card-idle-range merged into the same sentence) |
| T02 | implement | The fact is not strictly wrong, since 'latches' can mean 'holds', but it is ambiguous, and its natural reading (the latch is open while the clock is high) describes the glitchy circuit that a clock ga |
| T03 | covered | harts-formula-minion-two-meanings |
| T04 | covered | fma6-kind-measured |
| T05 | implement | routing-order-measured-on-two-cards (the two 'measured on two cards' panels: the mesh panel, script.js:1090, and flow 3's TensorSend detail, script.js:1803; applied in the main checkout) |
| T06 | covered | dram-chip-share-stale-25-28 and dram-91-cycle-split-inconsistent (merged) |
| T07 | implement | Codex is right, and no verified finding fixes it: stale-claims-line-citations only remaps mm-perw's source line, :419 to :454, and that is applied |
| T08 | implement | Codex's arithmetic is right, and no verified finding fixes this |
| T09 | implement | Codex is right that the page both asserts the DRAM's maker and says it is unknown |
| T10 | owner-decision | Not an error: the page follows one consistent convention, which the lab's reductions state |
| T11 | owner-decision | A change of the page's frame convention, not an error |
| T12 | owner-decision | measured-facts-card-not-recorded (only the card on the deep zoom's measured facts) |
| T13 | implement | Confirmed physics error; no fixer's finding covers it (searched the 97 for source/drain, current direction and the power FET) |
| T14 | implement | electrons-table-labels (only the lib.channel off-state leak line, ladder-inner.js:360) |
| T15 | implement | Confirmed in the source and in renders |
| T16 | implement | s08-ks-adder-cin-only-to-s0 (the carry-in, already applied in the live tree) |
| T17 | implement | Each of Codex's seven examples checked against the kit's pin geometry and in renders |
| T18 | implement | Confirmed by exhaustive check (codex/TB-work/ecc_check.py, rerun today) |
| T19 | implement | Confirmed |
| T20 | implement | xing-drawing-is-the-wrong-crossing and link-bit-sync-panel-and-label (the synchroniser part, already applied in the live tree) |

