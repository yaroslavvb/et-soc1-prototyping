### Drawn, but not selectable today

- **The shire view's edge labels** (the owner's second request: "arrows like Shire 28 and shire 12 and shire 29 ...
  should be clickable"). `buildShire` draws them at `chip-diagram.script.js:323-334`: for each of N, S, W, E it looks up
  the die-orientation neighbour `BYDIE[(cell.r + dr) + ',' + (cell.c + dc)]`, names it with `cellName` (line 186: "shire
  N", "memory shire N", the master or spare, "PCIe shire", "I/O shire", or "die edge"), draws a `mlink` stub and a
  `T(...)` text ("↑ PCIe shire", "shire 12 ←", "→ shire 28", "↓ shire 29"; on a phone the side labels are rotated by
  `sideLab`). They are plain text inside the frame group `fr`, with no `comp` and no handler. Making them parts: wrap
  each in a `comp(fr, 'edge', {cell: c, dir: s}, ...)` (or a `<g role="link">`) when `c` is a compute shire and send
  `userNav({level: 1, sid: c.id})` on click and Enter; for a memory shire, the master, the PCIe or I/O shire, either
  zoom out to the die with that cell selected or (once the zoom tree covers them) zoom into that part. `P.edge.N/S/W/E`
  already holds each stub's end point.
- **The drawn sub-structures inside the parts**, all `pointer-events: none` today, which the deep zoom would make
  targets: in a shire, each bank's four sub-bank rectangles (`buildShire`, bank loop), the mesh stop's four lane boxes
  (`P.lane`), the neighbourhoods' fast-network tree edges (`fln-e`); in a minion, each hart's 32 register squares
  (`P.regs`: f0-f31, the vector registers), the vector unit's 8 lanes x 5 unit boxes (FMA, IMA, IMA, INT, TR; `P.units`), the tensor sequencer's
  TensorFMA box and TenB/TenC boxes, the L1's 16 set rectangles (sets 12-15 in `l1d`, sets 0-11 are the `l1scp` part).
  Their nodes in the tree: `shire.subbank`, `shire.meshstop.xing` (lanes), `fln`, `vpu.lane.vrf` (the register
  squares; the integer registers, `core.irf`, are not drawn), `vpu.lane`, `vpu.lane.fma`, `vpu.lane.tima`, `vpu.lane.trans`, `tensor.fsm`, `tensor.tenb`,
  `tensor.tenc`, `l1d.block`.
- **Chip-wide infrastructure no layer draws:** power delivery, clock distribution, the wiring stack (`die.power`,
  `die.clock`, `die.metal`), each shire's PLL, DLL and sensors (`shire.clock`, `shire.sensors`).

<!-- SPLIT:TREE -->
## 3. What the memory-levels page can give each part, and how

The memory-levels page (`docs/reports/sources/memory-levels.script.js`, data
`docs/reports/data/2026-09-28-memory-levels/`) already has three things the deep zoom needs.

**The engine.** A tree of scales per scene (`SCENES.<lv>.scales`: each node `{name, short, parent, def, tw, target(ap,
inst), build(L, ap, inst), label(inst)}`), built lazily into layers (`buildLayer`), with the camera's legs over any
chain depth (`legNew`, `legOpen`, `legDraw`, `legClose`, `legRetarget`, from "the camera's legs" to `zoomWorker`),
fades driven by coverage (`cover`, `COV0`) and a pause between the out and in legs. The chip diagram's own camera is
built for exactly three layers (`LAYERS[0..2]`, `segOpen` per level pair). The tree in section 2 maps onto one scale
tree: every node with a `size_m` is a scale whose `target` is the rectangle of its drawing in its parent's layer, and
`tw` (the target's width in the parent's units) follows from the sizes. Port the engine; keep the chip diagram's three
builders as the top three scales.

**The drawing kit** (all generic, `memory-levels.script.js:688-826`): `comp`, `part`, `frame` (with its badges
`tagPill`), `railBand`, `rail`, `gnd`, `netLab`, `mosV` and `mosH` (a transistor symbol with gate, drain, source),
`invSym`, `andSym`, `mux2`, `flopSym`, `icgSym`; the activation primitives (`lit`, `mos`, `idle`, `ringAround`,
`counter`) that light a path or a transistor.

**Scenes and circuits to reuse, by part** (scales named as in `SCENES.<lv>.scales`):

| Part (node) | memory-levels scene · scale | Builder(s) | Reuse |
|---|---|---|---|
| Compute shire, logical view (`shire`) | l2 · shire | `buildL2Shire` | the same 4 neighbourhoods x 8 minions over 4 banks, crossbars, UC, mesh stop, with the LV and HV bands; the neighbourhood's 2:1 and 13:1 arbiters and bank FIFOs |
| Mesh stop (`shire.meshstop`), mesh link (`mesh.link`) | l3 · hop; scp · hop | `buildL3Hop`, `buildHop` | to_l3 master, VC FIFO (level shifters, 2-flop synchroniser), a router of one of 9 layers, the 3.72 mm link, the next router, flit sizes, energy per hop |
| Wire segment, repeater (`mesh.link.wire`, `lib.repeater`, `lib.levelshift`) | l3 · rep; scp · rep | `buildL3Wire`, `buildWire` | a repeater and a level shifter transistor by transistor |
| Crossing (`shire.meshstop.xing`, `shire.neigh.req`, `lib.levelshift`) | l2 · xing | `buildL2Xing`, `buildXing` | a VC FIFO cell with a level shifter; relabel the rails per crossing (0.517 to 0.705 V; 0.705 to 0.485 V; 400 to 933 MHz in a memory shire) |
| Bank (`shire.bank`, comp `banks`) | l2 · bank; l3 · hbank | `buildL2Bank`, `buildL3Bank` | request queue, read buffer, coalescing buffer, atomic unit, the 15-stage pipeline strip, four sub-banks; `inst.bank` from the chip diagram's `ctx.bank` |
| Sub-bank (`shire.subbank`) | l2 · sub; l3 · sub; scp · bank | `buildL2Sub`, `buildL3Sub`, `buildScpBank` | tag RAM, tag-state RAM, four data panels, ECC, comparators |
| Data panel (`shire.panel` and its children) | l2/l3/scp · panel | `buildPanel` (via `buildL2Panel`, `buildL3Panel`, `buildScpPanel`) | the documented shell, the generic periphery and the dashed unknown geometry, with the band of the partition lit (L2 0x280-0x2FF, L3 768-1023, scratchpad 0-639) |
| Sense amplifier and trims (`shire.panel.colio`) | scp · vmin | `buildVmin` | the RM table against the three rails |
| 6T cell (`lib.sram6t`, `shire.panel.array`) | l2/l3/scp · cell | `buildCell`, `draw6T` | read, write, half-select, leakage, with the two badges (generic; the bitcell asked) |
| L2, L3 slice, scratchpad (`shire.l2`, `shire.l3`, `shire.scp`) | the whole l2, l3 (from home) and scp (from shire) scenes | `SCENES.l2`, `SCENES.l3`, `SCENES.scp` | each partition's inside is its scene; the l3 and scp chip scales (`buildL3Chip`, `buildScpChip`, `chipMap`) duplicate the die and can go |
| Minion, logical (`minion`) | l1 · minion | `buildL1Minion` | the pipeline strip ID-EX-TAG-MEM-WB, DCache, TLB, 2 miss handlers, replay queue, VPU port, TensorLoad unit, the rail band |
| L1 data cache and scratchpad (`l1d`, `l1scp`, `l1d.*`) | l1 · dcache, lram, row, latch, cmp | `buildL1Cache`, `buildL1Block`, `buildL1Row`, `drawReadTree`, `buildL1Latch`/`buildLatchCell`, `buildL1Cmp`/`buildComparator` | direct; for `l1scp` light sets 0-11 |
| Register files (`core.irf`, `vpu.lane.vrf`, `tensor.tenc`) | l1 · lram, row, latch | `buildL1Block`, `buildL1Row`, `drawReadTree`, `buildLatchCell` | the same latch register-file pattern (the ET library's `rf_latch_*`): new instances with 64 rows and 2 read trees (integer RF), 64 rows, 3 read trees and 2 write decoders (vector RF) |
| Tag comparators (`shire.subbank.cmp`, `l1d.cmp`, `lib.xor`) | l1 · cmp | `buildComparator` | 33 bits for the L1, 23 for the shire cache |
| Memory shire (`memshire`, `memshire.*`) | dram · ms, phy, dq | `buildMS`, `buildPHY`, `buildDQ` | direct |
| LPDDR4X (`dram`, `dram.*`, `lib.dram1t1c`) | dram · chip, chan, dbank, dcell | `buildDramChip`, `buildChan`, `buildDBank`, `buildDCell` | the chip diagram already draws the packages (skip `buildDramChip`); from the channel down, direct |
| Flip-flop, ICG, mux (`lib.flipflop`, `lib.icg`, `lib.mux2`) | symbols | `flopSym`, `icgSym`, `mux2` | symbols for the new datapath drawings |

**New drawings with no precedent in the repository:** the FMA's datapath (Booth selectors, the 4:2 compressor tree,
align, add, normalise, round: `vpu.lane.fma.*`; needs an XOR/majority symbol for the full adder and 4:2 compressor,
whose logic `r42cmp.v` gives), the int8 units, the transcendental ROM lookup, the integer ALU and iterative
multiplier, the front end, the UC block's counters, the router's insides beyond `buildHop`'s generic box, the clock
generation (DPLL, DLL, 25 ps delay lines) and tree, the PCIe controllers and a SerDes lane, the I/O shire's blocks,
and the device and material scales: the FinFET (top view at 57 nm gate pitch and 30 nm fin pitch), the fin in
cross-section with its gate stack, the channel, and the silicon crystal (diamond cubic, a = 0.5431 nm).

**Data.** memory-levels' `facts.json` holds 533 facts (namespaced `l1:`, `l2:`, `l3:`, `scp:`, `dram:`), 311 numbers,
the same `layout` as the chip diagram, and `parts` per scene; it already cites chip-diagram facts as `chip:<id>`. The
chip diagram's `build_facts.py` can merge the memory-levels facts the tree cites (every `ml:` tag in section 2) the way
memory-levels cites `chip:` ones, so a part's panel and tooltips work unchanged. The tree's new facts (RTL, outside
sources) have no ids yet: give them a `research/facts-inside.json` of the same shape (`id, component, statement,
source, kind`), with `kind` taking the labels above (`outside` and `generic` are new kinds for the chip diagram; the
memory-levels page already uses `generic` and `unknown`).

## 4. Inferred or unknown, and what would settle it

| Question | Where it matters | What would settle it |
|---|---|---|
| Does the ET-SoC-1 silicon match core-et's Erbium-branch RTL (latch register files, the TXFMA's structure, the mul/div loop counts, the ROM tables)? | every fact marked "Erbium RTL" (`caveat: erbium-rtl` in inside.json), in `core`, `vpu`, `tensor`, `lib.cmp42`, `lib.booth`, `lib.arbiter` | Esperanto's or AI Foundry's word that Erbium's minion is the ET-SoC-1's (the documents' revision tables date to 2018-2022); a timing test (the 8-cycle multiply and 65-cycle divide are measurable on a card) |
| Which bitcell the shire-cache macros use (6T HD? 8T?), and what "not using SRAM" meant | `shire.panel.array`, `lib.sram6t`, every size derived from 0.027 µm² | the macro datasheet or `.lib` (u.bitcell, scp.u-cell; the hub's ask for design documents) |
| The data panel's geometry (rows x columns, column mux, internal banks) | `shire.panel.*` sizes | the same macro datasheet (u.macro-geometry, l2.macro.name-decode) |
| Any floorplan below the die: where the banks, neighbourhoods, minions and mesh stop sit, and their areas | every sub-shire `size_m` | a die photo or floorplan from Esperanto (l2.floorplan, l1.u-floorplan, u.slice-floorplan); a better die plot would at least give the shire channel's and neighbourhoods' outlines |
| Which vector register file was taped out (ET-custom or sea of latches) | `vpu.lane.vrf` | the design team (VPU spec §2.2.2 leaves it a parameter) |
| TSMC N7's fin width and height, gate length, and metal stack | `lib.fin`, `lib.gate`, `lib.channel`, `die.metal` | a TechInsights (or similar) cross-section of an N7 part; the numbers here are inferred from 10 nm-generation cross-sections |
| The router's pipeline, flit width and layer use | `shire.meshstop.router.*` | the NetSpeed configuration or NoC reference manual (u.noc-hop; ask-noc-docs) |
| The PCIe PHY's and DDR PHY's circuits | `pcie.lane`, `memshire.phy.dq` | vendor documentation; the tree draws them generic |

## 5. Zoom ladders, with each step's magnification

Using the sizes in the tree (most below the shire are order-of-magnitude inferences). A step under about 2x is better
drawn as one scene; a step over about 30x wants an intermediate scale.

<!-- LADDERS -->

Suggested fixes from the ladders. Four steps are large: the data panel's array (137 µm) to one 6T cell (0.24 µm),
about 570x (memory-levels bridges it with the panel's "representative grid" of 8 x 12 cells, which can be its own
scale: a 16 x 16 patch of cells, about 4 µm); a wire segment (200 µm) to its repeater (1 µm), 200x (an intermediate
"repeater with its wire stubs", about 10-20 µm); an L1 row (32 µm) to one latch (0.5 µm), 64x (a few latches of the
row with their clock gate, about 3 µm); the compressor tree (40 µm) to one 4:2 compressor (1.5 µm), 27x (a column slice
of the tree, about 10 µm). The steps from a gate (0.3 µm) to the FinFET (57 nm), about 5x, and from the channel (6 nm)
to the crystal (0.54 nm), about 11x, are fine.

## 6. Sources

**In the repository** (paths from the worktree root; `external/` is in the main checkout):

- The chip diagram's source and data: `docs/reports/sources/chip-diagram.script.js` (1980ebb; `buildChip` 218-302,
  `buildShire` 311-437, `buildMinion` 440-541, `COMPS` and `LEADS` 1278-1404, `zoomInto` 1434-1439),
  `docs/reports/data/2026-09-27-chip-diagram/facts.json` and `research/`.
- The memory-levels page: `docs/reports/sources/memory-levels.script.js`, `docs/reports/data/2026-09-28-memory-levels/`
  (`facts.json`, `research/DESIGN.md` §2.6 and §4-§8).
- `docs/et-soc1-notes.md`, `docs/findings/01-resources.md` (R2, R6, R14), `docs/research/why-low-power.md`,
  `docs/energy-manual/03-instructions.md` (the flip model), `docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md`.
- core-et (Erbium branch) documents: `external/core-et/docs/` Minion Description, Minion VPU Specification, FE-Intpipe
  Description, Minion DCache Description, CORE-ET Minion Shire Description, CORE-ET-Neigborhood-MAS,
  Neighborhood-ICache-Description, CORE-ET-Shire-Cache-Specification, ET-Link-Specification, Minion Shire DLL Delay
  Control (text versions made with `pdftotext -layout` in `~/claude/work/chipzoom/txt/`).
- core-et RTL: `external/core-et/rtl/shire/minion/{intpipe,frontend,vpu,dcache}/`, `rtl/libs/{macros,rf_latches,
  compressors,floating_point,arbiters,mems_and_fifos}/`; the re-implementation `external/core-et-main/`.
- ET manuals: `external/et-man/` ET Preliminary Datasheet Rev 1.0, ET Programmer's Reference Manual (§1.5, §1.6, ch. 10
  and 11, the PLL allocation), ET Introduction, ET Minion Overview (text in `external/et-man/txt/`).

**Outside:**

- D. Ditzel et al., "Accelerating ML Recommendation With Over 1,000 RISC-V/Tensor Processors on Esperanto's ET-SoC-1
  Chip", IEEE Micro 42(3), 2022 (https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf), and the Hot
  Chips 33 slides (docs/findings/01-resources.md R6).
- S.-Y. Wu et al. (TSMC), "A 7nm CMOS platform technology featuring 4th generation FinFET transistors with a 0.027um²
  high density 6-T SRAM cell for mobile SoC applications", IEDM 2016, paper 2.6.
- Wikipedia, "7 nm process" (comparison table: TSMC N7 gate pitch 57 nm, fin pitch 30 nm, minimum metal pitch 40 nm,
  91.2-96.5 MTr/mm², SRAM 0.027 µm²; IRDS 2021 gate length 20 nm), read 30 September 2026.
- WikiChip Fuse, "TSMC 7nm HD and HP Cells, 2nd Gen 7nm, And The Snapdragon 855 DTCO" (https://fuse.wikichip.org/?p=2408):
  HD cells 240 nm tall (6 tracks), HP 300 nm, about 91.2 and 65 MTr/mm². The site refused connections on 30 September;
  the values are as a search summary reported them, and should be re-read before publishing.
- D. James (Siliconics), "A Quick Look at 14-nm and 10-nm", AVS Joint Users Group, July 2018 (JTG718-4): TSMC 10 nm and
  Intel 10 nm cross-sections (https://nccavs-usergroups.avs.org/wp-content/uploads/JTG2018/JTG718-4-James-Siliconics.pdf;
  local copies of it and of the IEEE Micro paper, with text, in `~/claude/work/chipzoom/`).
- NIST CODATA 2018, lattice parameter of silicon, a = 543.1020511 pm.
- N. Weste and D. Harris, *CMOS VLSI Design*, 4th ed., 2011 (ch. 1-2 transistors and gates, 6 interconnect and
  repeaters, 9 combinational circuits, 10 latches and flip-flops, 11 datapath: adders, shifters, multipliers, 12 SRAM
  arrays, 13 clocks, PLLs, I/O and high-speed links); J. Rabaey, A. Chandrakasan, B. Nikolić, *Digital Integrated
  Circuits*, 2nd ed., 2003 (ch. 11, the mirror adder; ch. 12, memories); W. Dally and B. Towles, *Principles and
  Practices of Interconnection Networks* (routers; via ml:l3:g.router); JEDEC JESD209-4 (LPDDR4; via the ml:dram:gen.*
  facts); PCI Express Base Specification 4.0 (16 GT/s, 128b/130b).
