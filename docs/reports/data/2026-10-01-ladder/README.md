# The shared ladder's data (1 October 2026)

The owner's request of 1 October 2026: make the chip diagram and the memory levels consistent, give both the Up button
and the same scales, go down to transistors, atoms and quarks, close the ladder into a circle (past the observable
universe back to the smallest scales and up into a transistor or a memory cell), research TSMC's 7 nm process and
Esperanto's ET-SoC-1 and fill in the electronics. The design is in the session's work directory
(`/home/yaroslavvb/claude/work/ladder/DESIGN.md`, not committed); this file is what the repository keeps of it.

Part 1 (this commit series) builds the shared modules and the chip diagram's use of them. Part 2 puts the memory levels
on them (DESIGN B0-B4; below, "Part 2: the memory levels").

## Files

| File | What |
|---|---|
| `build_ladder.py` | writes `ladder.json` from the four research files; `--check` exits 1 if it is stale or a rule fails |
| `ladder.json` | the ladder's scales (name, short name, a beginner's lead, size with its kind and fact, or a bound, or none for the ring; `egg` for the levels above the rack), every fact, the facts the chip's existing scales gain (`more`), the numbers the drawings print (`num`, each checked against its fact's statement), the ring's ticks and epochs, and the Bernal Heights map |
| `research/build_process.py`, `process.json`, `research-process.md` | 99 facts: TSMC N7 (fin, gate and metal pitches, the fin's shape, the gate stack, contacts, cells, SRAM), the ET-SoC-1 from Hot Chips 33 and IEEE Micro 2022, and the electronics (switching, voltages, charges, leakage, band gap, dopants), with this chip's own measured rails and energies from the repository |
| `research/build_particles.py`, `particles.json`, `research-particles.md` | 93 facts: the silicon atom, its inner electrons, the nucleus, a proton, a quark, an electron, the Planck length, a dopant atom, the ring of sizes (the cosmic uroboros) and the early universe's epochs; the channel recomputed at N7's 6 x 16.5 x 52 nm (257,000 atoms) |
| `research/build_studio45.py`, `studio45.json`, `research-studio45.md` | 20 facts: Studio 45, Bernal Heights and 29th Street, from the owner's words and public data (the research note redacted: no link to a page that gives the address) |
| `research/make_bernal_geo.py`, `simplify_bernal_geo.py`, `bernal-geo.json` | the map: DataSF's neighbourhood outlines, the park, the main roads and the whole of 29th Street, clipped and simplified to 14 KB; the hill's summit (a public landmark) the one point |
| `research/build_circuits.py`, `circuits.json` | the textbook constructions (the owner's second update, 1 Oct 09:00: every part reaches a transistor, then the atoms): 20 facts, each a construction with its book or paper (Weste and Harris, Rabaey, Koren; Kogge and Stone, Booth, MacSorley, Oklobdzija, Schmookler and Nowka, Hamming, Hsiao, Montoye et al.), and 13 scales (a NOR and an AND-OR-INVERT gate, a shifter, a leading-zero counter, a decoder, a register file, control logic of standard cells, a counter, an equality comparator, a queue, a PLL, SECDED error correction, a ROM), with order-of-magnitude sizes (inferred, the reasoning in each note); short names and facts for the adder, the Booth encoder, the clock gate and the sense amplifier that `inside.json` names ; since part 1b (the last dead ends, found by walking every scene by its path) also a PCIe lane's SerDes (W&H ch. 13; PCIe 4.0's equalisers from MathWorks' model of the specification, its 28 dB loss budget from Teledyne LeCroy; the StrongARM latch, Razavi 2015; the bang-bang phase detector, Alexander 1975), a differential pair and the CTLE made of it (Razavi's textbook and SSC Magazine 2021), a crossbar (Dally and Towles), rounding to nearest even (IEEE 754-2019, Koren), the copper wiring and a copper atom (NIST; the free-electron density from N7's copper lattice and Kittel), a buck converter (Erickson and Maksimović; the card's TI TPSM831D31 and ADI LTM4680 from their makers' pages), a trench power MOSFET (Baliga), a boot-strap pin (Horowitz and Hill; the card's DIP switches and the chip's 11 boot-pin status bits from Esperanto's manuals), Intel's 14 nm pitches for the hosts' processors (Natarajan et al., IEDM 2014) and their DDR4 (Intel); 65 facts, 24 scales and the numbers the new drawings print (`num`, merged by build_ladder.py) |
| `research/epqs_29th.py`, `epqs_29th.out`, `epqs_summit.py`, `epqs_summit.out` | 29th Street's elevation profile and the summit's height, from the USGS 3DEP lidar model (distances and heights only) |
| `motion/` | the motion check against `bb0eb78` at CPU 1x and 4x, the scales' build times, and the scripts that made them (its README) |

## Rebuilding

```bash
cd docs/reports/data/2026-10-01-ladder
python3 research/build_process.py && python3 research/build_particles.py && python3 research/build_studio45.py && python3 research/build_circuits.py
# the map: the raw downloads (not committed) in a directory of your own
LADDER_RAW=/path/to/raw python3 research/make_bernal_geo.py /path/to/raw
python3 research/simplify_bernal_geo.py /path/to/raw
python3 build_ladder.py && python3 build_ladder.py --check
# then the chip diagram (docs/reports/MIRROR.md, its row): its build_facts.py reads ladder.json through
# research/deepzoom.py and writes the page's facts.json and the lazily fetched docs/reports/ladder-img/ladder-data.json
```

## Rules the build keeps

- Every fact has one of the nine kinds (measured, spec, derived, inferred, outside, generic, owner, hypothesis,
  unknown); outside, spec and generic facts name their source; derived and inferred ones say how (their arithmetic or
  assumption, in the source or the note).
- Every number a drawing prints is a `(fact, text)` pair and the text occurs in the fact's statement.
- The superseded fin, gate and channel numbers (a fin 6-7 by 45-50 nm, a 20 nm gate, 270,000 atoms) appear nowhere: N7's
  fin is 6 by 52 nm and its effective gate length 16.5 nm (WikiChip Fuse; Dick James on TSMC's IEDM 2016 paper).
- Privacy (AGENT.md §10, and the owner's words, which give only the street and the neighbourhood): no house number, block,
  point or coordinates of the studio, no ZIP code, no link to a listing that gives its address, nothing in the map called a
  studio; anything about events at the venue waits for the owner's answer.
- Textbook, and said so: where the ET-SoC-1's own circuit is not published (all of its gate-level design), a block opens
  onto the construction the textbooks give, tagged "textbook construction" and "this chip's own circuit: not published";
  every such scale leads on to a gate drawn as transistors, the FinFET at N7's pitches, its fin and channel, and the
  silicon atoms. The DRAM's parts lead to the DRAM cell's own transistor (a DRAM process, not N7), never to the FinFET.
- The easter egg (the owner, 1 Oct 2026, 07:25 PDT: "zoom out beyond the rack should be an Easter egg. Don't show it in
  any of the written hierarchies"): the levels above the rack carry `egg: true`; the pages name none of them in advance.

## Part 2: the memory levels (1 October 2026)

The page "Anatomy of a memory access, interactively" now has the chip diagram's Up bar, breadcrumb and readout, and the
same ladder: out from a chip level's map to the package, the card, the host and the rack (and on, as an easter egg, to
the universe and round the ring of sizes), in from every part of its drawings to a transistor, its fin and channel, the
crystal, an atom, its nucleus, a proton, a quark and the Planck length. Its data needs nothing new from this directory:
`docs/reports/data/2026-09-28-memory-levels/build_facts.py` copies the chip diagram's `scales`, `geo`, `img`, `onum`,
`outside`, `ring` and `lazy` blocks (built from `ladder.json` by the chip's build) into its `ladder` block, with the
chip's facts that those scales cite; both pages fetch the same `docs/reports/ladder-img/ladder-data.json`.

**Two cameras, one ladder.** The design asked for one camera (DESIGN D2), with "B1-lite" (the Up bar over the levels'
own camera, the outer and inner scales left to the chip page) as the fallback. The page takes a third way: the levels
keep their own camera for their own scenes (the level tabs, the 28 accesses and their Dive, the phone's sideways window,
the cross-fades between the maps and the level moves the owner asked smooth on 30 September), and the chip diagram's
path camera runs beside it, in a scope of its own (`sources/memory-levels.ladder.js`), on its own SVG stacked over the
levels' in the same box, for every scale outside their scenes. The two hand over at rest on a scene both draw the same
way: the path camera draws a level's scene with the level's own builder (the same code, the same example address) where
the levels' camera shows it (on a phone, the same sideways window), so the hand-over is not seen (measured: the two
pictures coincide to the pixel, the remaining 1-3% of pixels differing by anti-aliasing only). Why: the levels' camera
draws a move in its root's coordinates and cannot span 45 decades (code-audit §3.3), and moving 28 accesses, Dive, the
phone window and the tuned level moves onto the path camera risked the smoothness the owner asked for.

**What each part of the levels' drawings opens** (`sources/memory-levels.links.js`): its own scale where the levels draw
one (their camera), else the chip diagram's scene for it, the same table the chip uses for the same drawings (the
textbook constructions where the chip's circuit is not published), down to a transistor and its atoms; a box of numbers
or a note beside a map or chart is a key, and its panel says so. A rail's band opens the wiring stack. The ring's way back
in is the reader's level's own cell (the L1's latch, a 6T cell of the L2, the L3 or the scratchpad, the DRAM's cell and
the DRAM process's transistor, never N7's).

**The levels' own suites, again.** The suites that checked the level moves of 30 September (the porter's and the two
reviewers': the keys, the 28 accesses, the tour, the level tabs, races, the phone's taps and swipes, five fuzzers with
thirteen seeds and a leak test; 43 runs, about 21 minutes; their scripts stay in the work directory, the results side by
side in `motion/regress-p2.txt`) were run on the new page and on the committed one. They differ only where the page
changed by design: the levels' mini-map of the scale above is not drawn (the Up bar names that scale and goes there, as
on the chip diagram; the suites' invariant "pip" fails wherever it looks for the mini-map), a tap selects and a
double-tap zooms (three checks of the phone suite, and the parts suites, expect one tap to zoom), and the scale control
is gone (the phone fuzzers' "scale" taps find nothing). One fuzzer's burst failed otherwise: the state the tests read,
`__memState().zooming`, did not count the ladder's moves, so that the fuzzer, waiting for the camera to rest, looked in
the middle of a hand-over (traced frame by frame: the camera was on its way, not stuck). Tracing it found a fault of the
same kind: a move of the ladder that starts in the levels' scenes waits for their camera to rest before it takes the
stage, and a level's tab clicked meanwhile lost its level to it (the ladder took the stage when the tab's move ended).
Fixed, with two more found while checking the fixes: `zooming` is true while either camera moves, a hand-over included;
a move asked of the levels' camera (a tab, a link, an access, the tour) cancels a hand-over still on its way; a link
clicked while the ladder holds the stage first brings it to the link's level, as a tab does (under reduced motion, where
a link is drawn at once, the stage had stayed with the ladder); and on the ladder's copy of a levels' scene that is not
their place (another bank, another shire, reached by the breadcrumb's menu or a glide) the panel is that scale's own (it
had kept the panel of the place left: at bank 0, the L1 cache's). `ml_ladder_test.mjs` T23, T7 and T24 check them; the
build before the fixes fails T23's two checks and T7's link.

**Tests on the final build** (served over http from the work directory, one run at a time; `tools/pagemotion/`):
`ml_ladder_test.mjs` 108 of 108 on the desktop and on a phone. Among them T13, against the chip diagram built from the
same sources: at ten shared places the breadcrumb up to the place, the Up button and the panel's title are the same on
both pages; T17: from the L3's cell the ring is 27 presses of Up away and a lap is 32, landing on the same atom; T18:
106 scales reached from the top and from the ring, every zoom seated in the drawing it starts from, every glide with its
way back; T19: a walk of 454 scenes from every level's scenes and from the rack, every part leading in but the keys
beside the maps and charts and the Planck length's ruler, every scene reaching a transistor and then an atom, the DRAM's
chains never the N7 FinFET. `ml_access_test.mjs --dive`: the 28 accesses play to their end, go out to the package and
play again from their level. `ui_test.mjs`: the player bar as on the committed page. The chip diagram: `zoom_test.mjs`
667 of 667 on the desktop and 504 of 504 on a phone, and its pictures unchanged to the pixel at seven places, light,
dark and on a phone. `zoom_static.py` 0 failed on both (the memory levels' page 1.90 MB of 2.0, its script 1,016 KB of
1,050, its data 760 KB of 800); `check_page.sh` OK on both, light and dark, at 1280 and 390 px; `guard_test.py` 0
failed; the other 15 pages of MIRROR.md rebuild byte for byte with the changed `build-report.py`; `build_ladder.py
--check` and both pages' `build_facts.py` are fixed points. Motion: `motion/README.md`, part 2.

**Links between the two pages carrying a place (DESIGN §3.8, B4): not made.** The check the design asked for, run on 1
October against the public pages in headless Chrome (read only): the spacesheep viewer passes neither `?at=` (dropped
from the address) nor `#at=` (kept in the outer address, not forwarded into the framed page; `#l2/bank` likewise) to
the page it frames, so a link could not land at the same scale. Both pages read `?at=` (and the memory levels `#at=`)
when opened directly.


## Part 3: the four reviews of 1 October evening, fixed

Four reviews of 290cb9c (facts, consistency and interaction, visuals, navigation and code) were checked one by one and
the real findings fixed; main (the loop of UPDATE 3, links, replay speed) was merged first, so that both pages run the
same ladder-core.js. What changed in this directory's data:

- `research/build_circuits.py`: the bang-bang (Alexander) phase detector's early and late were reversed (an edge sample
  equal to the bit before means the change had not yet come: the clock is early); PCIe 3.0 and 4.0 define eleven
  transmitter presets, P0 to P10 (Teledyne LeCroy, 10 Nov 2014; MathWorks' page says ten).
- `research/build_particles.py`: the inner electrons' binding is the X-Ray Data Booklet's core levels (Si 1s 1839 eV,
  some 230 times an outer electron's 8.15; 2s and 2p 150 and 99 eV), not the ionisation energies of stripped ions
  (2,673 eV is the last electron of Si¹³⁺); the atom against its nucleus is one ratio, diameter to diameter, about 29,000
  (0.2352 nm against the 8.06 fm the page draws); the channel's facts cite N7's published fin and gate (process.json)
  and the dense cells' two fins; the oldest light "about 380,000 years (372,600 in Planck's fit)"; the electron's mass
  sets the atoms' spacing, not the transistors' size; the chip's silicon "more than 4,567 million years ago", its protons
  formed "some 14 to 24 microseconds" after the Big Bang; Kittel's table, Krane's rule, Steigman, Schramm and Gunn, and
  Leconte-Chevillard marked as not read for the page (their values as widely quoted, or the Crossref record).
- `research/build_process.py`: the DRAM's 1.1 V and 0.64 V rails are set points, not on-die readings, and named as the
  card's "VDDQ" (the LPDDR4X's VDD2) and VDDQLP (its I/O VDDQ); the leakage per transistor is an average at 80 °C; the
  54 nm gate pitch was Scotten Jones's guess, which Dick James reports; HfO₂ cuts the tunnelling leak by orders of
  magnitude rather than stopping it; the source and drain hold one phosphorus atom in 29, only one in thirteen of them
  active (Applied Materials); the PMOS source's boron spans the patent's range; dynamic power without the overclaim.
- `research/build_studio45.py`, `research-studio45.md`: the chert's 0.5-1.5 mm is the Presidio page's (the Chert FAQ
  says 0.5-1 mm); the guard refuses any link but the public-data sources' (no site or slug spelled out); the research
  note no longer narrows the studio to blocks, gives the lot's size and zoning, or describes an event at the venue (until
  the owner answers). Earlier commits of this branch, and of main since f6cd2cf, still hold the old note.
- `build_ladder.py`: the Bernal Heights lead says chip silicon is refined from silica like the hill's (not from the hill);
  the fin's and the gate's notes cite WikiChip's production pitches and Dick James without an "earlier drawing" readers
  never saw; the latch's electrons have their unit; new numbers for the drawings (65 mV, the dopants' one in 29 and one
  in thirteen, the electron's 4.1 × 10⁻³² m).

Not done in this round, each said where it stands: the circuit scenes on a phone are still drawn whole at about 5-7 px
type (a phone layout or a sideways window for the textbook constructions is a design of its own); the camera math and the
panel helpers the memory levels' scope repeats (the code review's ladder-base.js and a free-name check in the build) are
not moved; the levels' maps are not yet in the die's orientation (DESIGN B0), so the arrows go to other neighbours than
on the chip diagram; the memory levels write and read `#at=` but have no Copy link button, and their scenes no drawn edge
links (the panel's "Next to it" row moves sideways); the breadcrumbs' fold loop is unchanged (a width cache made the
folding depend on the history).

## The final check (2 October)

An independent check of `11b6e45` before the merge. Both pages rebuild from their sources byte for byte (the whole data
chain, `build_process.py` to both `build_facts.py`, with the fixed points holding; the other 15 pages of MIRROR.md
too); `check_page.sh` OK at 1280 and 390 px, light and dark; over http: `zoom_test.mjs` 783/783 on the desktop and
620/620 on a phone, `ml_ladder_test.mjs --chip` 150/150 and 137/137, `ml_access_test.mjs` 28/28 (and with Dive 28/28),
`ui_test.mjs` the same states as the page of `bb0eb78`, `zoom_static.py` and `guard_test.py` 0 failed. Scripted tours by
real input, clicks on a desktop and taps on a phone, with a screenshot at every step: on both pages Up from the die (the
memory levels: from the L2) out past "?" to the top, straight round to the Planck length and up again, twice (40 presses
a lap on the chip; 35 from the L3's cell on the memory levels, and through the DRAM's own cell when the DRAM's map was
the last chip-level map shown); the dive to a quark by double-clicks (double-taps) on both pages; the vector add by
double-clicks through the multiply-add's prefix adder and an AND-OR-INVERT gate to an atom; in shire 7's row of the
die, Left to memory shire 3, Right across the die to memory shire 7, back by its "← shire 7" link and Left again to
memory shire 3 (by the arrow keys on the desktop, by the edge links on a phone); the level tabs and the access
`#dram/load`; and 40 random descents by double-clicks from the die and the rack, of which 39 reach a transistor and
then an atom and one the copper wiring's atom.

Two things fixed:
- `tools/publish-gh-pages.sh` copied `ladder-img/` beside the chip diagram only, so the memory levels on GitHub Pages
  would have fetched `memory-levels/ladder-img/ladder-data.json` and the outer levels' images in vain (404). It is now
  copied beside both pages (the dry run's site, served: both pages fetch their lazy data, 200).
- The chip diagram's address writer (`chip-diagram.links.js`, from main's links of 1 Oct) checked each candidate
  anchor with `atPath`, whose seat check draws every scene on the way: after the loop's jump to the Planck length it drew
  the whole chain down from the die in one task, about 100 ms at 1x and 350 ms at 4x, 400 ms after the arrival, so that
  an Up pressed then waited, and the scenes it left in the document slowed every move after. It now resolves the
  candidates without the seat check, as the memory levels' `atPrefix` does since `11b6e45` (a string read from the
  address still goes through `atPath`). Up five times from the top (round the loop, a quark, a proton, the nucleus, the
  atom): at 4x 48-52 of 272 frames late, the longest 333-367 ms, before; 3-6 of 327-331, the longest 50-133 ms, after;
  at 1x 3-6 late before, none after. `zoom_test.mjs` on the fixed build: 783/783 and 620/620.

Motion against `bb0eb78`: `motion/README.md`, "The final check".
