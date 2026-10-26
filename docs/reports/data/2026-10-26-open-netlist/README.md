# The multiply-add on an open 7 nm library — cell census (Q126)

26 October 2026, on aifoundry2. The flow and how to re-run it:
[`tools/open-flow/txfma/`](../../../../tools/open-flow/txfma/README.md).

**Why.** Every gate-level number this project has published about the multiply-add — cells,
transistors, flip-flops clocked per multiply-add, the glitch ratio — came from a netlist built with
a tape-out flow that is not public. A reader can neither check it nor extend it. This is the same
`txfma_top` RTL, from the public `core-et` Erbium branch, synthesized with **Yosys onto ASAP7**, the
BSD-3-Clause predictive 7 nm library. Nothing here needs a card, a licence or a private file.

**What it is not.** ASAP7 is not the process the chip was built in, and its cells are not the chip's
cells. An ASAP7 `x1` device has **3 fins**; the as-built census counts devices with 2. So the
transistor and area numbers are "what an open 7 nm library makes of this RTL", and the interesting
quantity is the *ratio* to the tape-out flow's, not the absolute.

## Census, against the tape-out flow's

The as-built figures are the Q124 chip-diagram facts `tfma.asbuilt.cells`, `tfma.regs.stage` and `tfma.clocked`, from a
netlist synthesized from the same RTL with the ET-SoC-1's own flow and library.

### One lane's multiplier — Booth rows, the Wallace tree, the product adder

| | cells | transistors |
| --- | ---: | ---: |
| This flow, ASAP7 RVT TT, hierarchy kept | **7,967** | **58,060** |
| Tape-out flow (`tfma.asbuilt.cells`) | 4,487 | 49,755 |
| ratio | 1.77× | 1.17× |

The open flow needs **1.77× the cells for 1.17× the transistors**: ASAP7's library is thinner in
compound gates, so Yosys builds the same logic out of more, smaller cells. Transistor count, the
quantity that actually sets the switched capacitance, lands within 17%.

Per block, from `census_keep.json`:

| Block | cells | transistors | fins | area µm² |
| --- | ---: | ---: | ---: | ---: |
| Booth rows (`f1/ppg`) | 2,644 | 16,828 | 65,104 | 246.5 |
| Wallace levels 1–2 (`f1/wallace1`) | 3,849 | 29,206 | 96,817 | 347.6 |
| Wallace levels 3–4 (`f2/wallace2`) | 1,283 | 9,734 | 32,265 | 115.8 |
| Product adder (`f2/prod_adder_64b`) | 191 | 2,292 | 7,766 | 28.8 |
| **multiplier total** | **7,967** | **58,060** | **201,952** | **738.7** |

The tape-out flow's split is Booth ≈ 21,300 transistors, the tree's four levels 22,110, the product
adder 5,718. The open flow puts more in the tree (38,940) and less in Booth (16,828): ASAP7 has a
`MAJx2` majority cell that Yosys uses 1,378 times across the unit, and no 4:2 compressor cell, so the tree is
built from AOI/OAI and majority gates rather than from the mirror and transmission-gate full adders
the as-built census counts (248 of them).

### The whole seven-stage unit

| | cells | transistors | fins | flip-flops | latches | area µm² | clock-pin cap fF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hierarchy kept (`census_keep.json`) | 19,822 | 185,502 | 591,718 | **2,071** | 13 | 2,451.3 | 991.1 |
| flattened (`census_flat.json`) | 16,087 | 157,726 | 496,688 | **1,953** | 13 | 2,124.9 | 935.0 |
| tape-out flow | — | — | — | 1,851 | — | — | — |

- **Flip-flops: 1,953 against the tape-out flow's 1,851, 5.5% apart.** The RTL declares 2,071
  register bits; keeping module boundaries keeps every one of them, because constants cannot be
  propagated across a boundary. Flattening prunes 118; the tape-out flow prunes 220. That the two
  independent flows agree to 5.5% is the first outside check any of the per-flip prices has had,
  and every one of them is a watt divided by a count like this.
- **13 latches = the unit's 13 `et_clk_gate` instances.** ORFS's asap7 flow forbids ASAP7's `ICG`
  cells, so each integrated clock gate becomes a latch plus a gate. The count of clock gates is the
  structural fact, and it is 13 for one lane.
- **Area 2,451 µm²** of standard cells at 1× (see the README's trap 3: the ORFS asap7 platform is
  already descaled, so ASAP7's 4× drawing scale must *not* be applied). For scale, the as-built
  note puts an earlier hand-placed significand datapath at 78 × 31 µm = 2,418 µm².
- The three top blocks: significand `txfmafrac0_top` 14,178 cells / 1,191 flops / 1,691.3 µm²;
  control `txfmactl0_top` 3,209 / 601 / 446.6; exponent `txfmaexp0_top` 2,097 / 187 / 258.8.

### How much the flip-flop choice moves the clock load

Yosys maps every flip-flop to `DFFHQx4_ASAP7_75t_R`, the library's only positive-Q flop, and it is a
4× drive. Forbidding it (`stat_hierqn.txt`, flattened) pushes the mapper onto `DFFHQNx1/x2/x3` plus
inverters: sequential area falls from 711.9 to 569.5 µm², 20% off, and total area from 2,124.9 to
2,033.6. So **the clock tree's share carries a ±20% choice that no RTL fact decides**, which is
worth remembering before any clock-share number from this flow is quoted to two digits.

## Files

| File | What |
| --- | --- |
| `census_keep.json` | the full census, hierarchy kept: totals, every cell type, 182 blocks |
| `census_flat.json` | the same for the flattened netlist |
| `stat_flat.txt` | Yosys `stat -liberty` for the flattened netlist (the cell-type table) |
| `stat_hierqn.txt` | the same with `DFFHQx4` forbidden, for the sensitivity above |
| `versions.txt` | every tool and repository commit used |

The netlists themselves (2.4 MB of Verilog each) are not committed: `tools/open-flow/txfma/synth.sh`
rebuilds them in about a minute from the commits in `versions.txt`.
