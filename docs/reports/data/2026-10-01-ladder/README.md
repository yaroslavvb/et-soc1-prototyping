# The shared ladder's data (1 October 2026)

The owner's request of 1 October 2026: make the chip diagram and the memory levels consistent, give both the Up button
and the same scales, go down to transistors, atoms and quarks, close the ladder into a circle (past the observable
universe back to the smallest scales and up into a transistor or a memory cell), research TSMC's 7 nm process and
Esperanto's ET-SoC-1 and fill in the electronics. The design is in the session's work directory
(`/home/yaroslavvb/claude/work/ladder/DESIGN.md`, not committed); this file is what the repository keeps of it.

Part 1 (this commit series) builds the shared modules and the chip diagram's use of them. The memory levels move onto
them next (DESIGN B0-B4).

## Files

| File | What |
|---|---|
| `build_ladder.py` | writes `ladder.json` from the four research files; `--check` exits 1 if it is stale or a rule fails |
| `ladder.json` | the ladder's scales (name, short name, a beginner's lead, size with its kind and fact, or a bound, or none for the ring; `egg` for the levels above the rack), every fact, the facts the chip's existing scales gain (`more`), the numbers the drawings print (`num`, each checked against its fact's statement), the ring's ticks and epochs, and the Bernal Heights map |
| `research/build_process.py`, `process.json`, `research-process.md` | 99 facts: TSMC N7 (fin, gate and metal pitches, the fin's shape, the gate stack, contacts, cells, SRAM), the ET-SoC-1 from Hot Chips 33 and IEEE Micro 2022, and the electronics (switching, voltages, charges, leakage, band gap, dopants), with this chip's own measured rails and energies from the repository |
| `research/build_particles.py`, `particles.json`, `research-particles.md` | 93 facts: the silicon atom, its inner electrons, the nucleus, a proton, a quark, an electron, the Planck length, a dopant atom, the ring of sizes (the cosmic uroboros) and the early universe's epochs; the channel recomputed at N7's 6 x 16.5 x 52 nm (257,000 atoms) |
| `research/build_studio45.py`, `studio45.json`, `research-studio45.md` | 20 facts: Studio 45, Bernal Heights and 29th Street, from the owner's words and public data (the research note redacted: no link to a page that gives the address) |
| `research/make_bernal_geo.py`, `simplify_bernal_geo.py`, `bernal-geo.json` | the map: DataSF's neighbourhood outlines, the park, the main roads and the whole of 29th Street, clipped and simplified to 14 KB; the hill's summit (a public landmark) the one point |
| `research/build_circuits.py`, `circuits.json` | the textbook constructions (the owner's second update, 1 Oct 09:00: every part reaches a transistor, then the atoms): 20 facts, each a construction with its book or paper (Weste and Harris, Rabaey, Koren; Kogge and Stone, Booth, MacSorley, Oklobdzija, Schmookler and Nowka, Hamming, Hsiao, Montoye et al.), and 13 scales (a NOR and an AND-OR-INVERT gate, a shifter, a leading-zero counter, a decoder, a register file, control logic of standard cells, a counter, an equality comparator, a queue, a PLL, SECDED error correction, a ROM), with order-of-magnitude sizes (inferred, the reasoning in each note); short names and facts for the adder, the Booth encoder, the clock gate and the sense amplifier that `inside.json` names |
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
  studio; the AI Plumbers event held at the venue waits for the owner's answer.
- Textbook, and said so: where the ET-SoC-1's own circuit is not published (all of its gate-level design), a block opens
  onto the construction the textbooks give, tagged "textbook construction" and "this chip's own circuit: not published";
  every such scale leads on to a gate drawn as transistors, the FinFET at N7's pitches, its fin and channel, and the
  silicon atoms. The DRAM's parts lead to the DRAM cell's own transistor (a DRAM process, not N7), never to the FinFET.
- The easter egg (the owner, 1 Oct 2026, 07:25 PDT: "zoom out beyond the rack should be an Easter egg. Don't show it in
  any of the written hierarchies"): the levels above the rack carry `egg: true`; the pages name none of them in advance.
