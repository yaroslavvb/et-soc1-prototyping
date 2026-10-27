# The multiply-add on an open 7 nm library — cell census (Q126)

26 October 2026, on aifoundry2. The flow and how to re-run it:
[`tools/open-flow/txfma/`](../../../../tools/open-flow/txfma/README.md).

Place and route, the parasitics and the switching power of this netlist are in
[`POWER.md`](POWER.md) beside it.

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

🛑 **Read the `mixed` row, not the `kept` one.** The first version of this file compared the
tape-out flow against a netlist that kept all 182 module boundaries, and reported 1.77× the cells.
Most of that was the boundaries, not the library: keeping a boundary blocks constant propagation
and resource sharing across it. `synth.sh` now also writes **`mixed`**, flattened everywhere
*except* the four multiplier blocks — the netlist a normal flow would hand on, with just enough
hierarchy left to count per block. On it the same multiplier is **4,989 cells**, and the ratio
falls from 1.77× to **1.11×**.

| | cells | transistors | area µm² |
| --- | ---: | ---: | ---: |
| **This flow, ASAP7 RVT TT, `mixed`** (the comparator) | **4,989** | **42,758** | 546.6 |
| Tape-out flow (`tfma.asbuilt.cells`) | 4,487 | 49,755 | — |
| **ratio** | **1.11×** | **0.86×** | — |
| the same, hierarchy fully kept (`census_keep.json`) | 7,967 | 58,060 | 738.7 |
| that ratio, for comparison | 1.78× | 1.17× | — |

So an open 7 nm library and an open synthesizer build this multiplier out of **11% more cells and
14% fewer transistors** than the ET-SoC-1's own flow did. Both of those are small enough that the
*structure* — how many gates a Booth-and-Wallace fp32 multiplier takes — is reproduced, which is
the thing worth checking, because every per-flip price in this project is a watt divided by a
count derived from that structure.

[Q126(d)](../2026-10-26-asap7-cell-energies/README.md) uses this netlist's **cell mix** from
`census_flat.json`, which is unchanged, but its caveat sentence still quotes the superseded
"7,967 against 4,487": on the comparable netlist that is **4,989 against 4,487**, so the mix it
borrows is closer to the silicon's than it says.

Even `mixed` is a slight **upper bound** on the cells: its four blocks still cannot be optimised
across their own boundaries, and the as-built figure was traced cone by cone out of a netlist that
had no such constraint.

Per block, from `census_mixed.json` (`census_keep.json` in brackets):

| Block | cells | transistors | fins | area µm² |
| --- | ---: | ---: | ---: | ---: |
| Booth rows (`f1/ppg`) | 2,210 (2,644) | 17,362 (16,828) | 54,290 | 219.7 |
| Wallace levels 1–2 (`f1/wallace1`) | 1,685 (3,849) | 14,466 (29,206) | 49,688 | 188.7 |
| Wallace levels 3–4 (`f2/wallace2`) | 903 (1,283) | 8,638 (9,734) | 29,266 | 109.4 |
| Product adder (`f2/prod_adder_64b`) | 191 (191) | 2,292 (2,292) | 7,766 | 28.8 |
| **multiplier total** | **4,989** (7,967) | **42,758** (58,060) | **141,010** | **546.6** |

The tape-out flow's split is Booth ≈ 21,300 transistors, the tree's four levels 22,110, the product
adder 5,718. The open flow puts a little less in both (Booth 17,362, the tree 23,104) and the same
in the adder. Where it differs structurally: ASAP7 has a `MAJx2` majority cell that Yosys leans on
and no 4:2 compressor cell, so the tree is built from AOI/OAI and majority gates rather than from
the mirror and transmission-gate full adders the as-built census counts (248 of them). The tree is
also where the hierarchy penalty was largest — 5,132 cells kept against 2,588 in `mixed`, a factor
of two — which is why **the per-block toggle counts in [`POWER.md`](POWER.md), which were measured
on the kept netlist, are upper bounds too**.

### The whole seven-stage unit

| | cells | transistors | fins | flip-flops | latches | area µm² | clock-pin cap fF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hierarchy kept (`census_keep.json`) | 19,822 | 185,502 | 591,718 | **2,071** | 13 | 2,451.3 | 991.1 |
| flattened (`census_flat.json`) | 16,087 | 157,726 | 496,688 | **1,953** | 13 | 2,124.9 | 935.0 |
| **four blocks kept** (`census_mixed.json`) | **15,805** | 159,896 | 497,997 | **1,974** | 13 | 2,126.1 | 945.0 |
| tape-out flow | — | — | — | 1,851 | — | — | — |

- **Flip-flops: 1,953 flattened, 1,974 with the four blocks kept, against the tape-out flow's
  1,851 — 5.5% and 6.6% apart.** The RTL declares 2,071 register bits; keeping module boundaries
  keeps every one of them, because constants cannot be propagated across a boundary. Flattening
  prunes 118; the tape-out flow prunes 220. That the two independent flows agree to within 7% is
  the first outside check any of the per-flip prices has had, and every one of them is a watt
  divided by a count like this.
- **13 latches = the unit's 13 `et_clk_gate` instances.** ORFS's asap7 flow forbids ASAP7's `ICG`
  cells, so each integrated clock gate becomes a latch plus a gate. The count of clock gates is the
  structural fact, and it is 13 for one lane.
- **Area 2,126 µm²** of standard cells, in **drawn 7 nm square microns, needing no correction**:
  the ORFS asap7 platform ships the 1× LEF (`INVx1_ASAP7_75t_R` is `SIZE 0.162 BY 0.27` =
  0.04374 µm², exactly its liberty area), so ASAP7's 4× drawing scale has already been taken out.
  *(The first version of `census_keep.json` and `census_flat.json` carried a `note` saying to
  divide the area by 16. That was wrong, and following it turns 2,126 µm² into 133 µm²; the note
  is corrected in both files and in `census.py`, and no number changed.)* For scale, the as-built
  note puts an earlier hand-placed significand datapath at 78 × 31 µm = 2,418 µm².
- The three top blocks, hierarchy kept: significand `txfmafrac0_top` 14,178 cells / 1,191 flops /
  1,691.3 µm²; control `txfmactl0_top` 3,209 / 601 / 446.6; exponent `txfmaexp0_top` 2,097 / 187 /
  258.8.

### How much the flip-flop choice moves the clock load

Yosys maps every flip-flop to `DFFHQx4_ASAP7_75t_R`, the library's only positive-Q flop, and it is a
4× drive. Forbidding it (`stat_hierqn.txt`, flattened) pushes the mapper onto `DFFHQNx1/x2/x3` plus
inverters: sequential area falls from 711.9 to 569.5 µm², 20% off, and total area from 2,124.9 to
2,033.6. So **the clock tree's share carries a ±20% choice that no RTL fact decides**, which is
worth remembering before any clock-share number from this flow is quoted to two digits.

## Files

| File | What |
| --- | --- |
| `census_mixed.json` | **the comparator**: flattened except the four multiplier blocks, so each is counted on a netlist that got cross-boundary optimisation everywhere else |
| `census_keep.json` | the full census, hierarchy kept: totals, every cell type, 182 blocks. Its per-block counts carry the hierarchy penalty — see the warning above |
| `census_flat.json` | the same for the fully flattened netlist (no blocks) |
| `stat_flat.txt` | Yosys `stat -liberty` for the flattened netlist (the cell-type table) |
| `stat_hierqn.txt` | the same with `DFFHQx4` forbidden, for the sensitivity above |
| `versions.txt` | every tool and repository commit used; `setup.sh` now pins all of them |
| `POWER.md`, `power/`, `net_cap_globalroute.txt.gz` | place and route, per-net capacitance and the switching energy per multiply-add |

The netlists themselves (2.4 MB of Verilog each) are not committed: `tools/open-flow/txfma/synth.sh`
rebuilds all three in about three minutes from the pinned commits in `versions.txt`, and
`tools/open-flow/txfma/mktiles.sh` rebuilds every operand file the bench runs, with its seeds.

## Corrections, 26 October 2026, after review

Five things in the first version of this directory were wrong or missing, and all five are fixed
above and in [`POWER.md`](POWER.md). Listed so a reader who saw the first version knows what moved:

1. **The multiplier's cell ratio was 1.77×, measured on a netlist that kept all 182 boundaries.**
   On the `mixed` netlist it is **1.11×** (and 0.86× the transistors). The structural agreement is
   much better than the first version claimed.
2. **Both census files carried a `note` telling the reader to divide areas by 16.** The ORFS asap7
   platform is already at 1×; the note is corrected and no number changed.
3. **The toggle comparison in `POWER.md` put a Booth+tree+adder figure against a tree-only one.**
   Restated at matched scope there.
4. **The energy per flipped operand bit was divided by the wrong denominator and compared against
   the wrong partner.** Restated in `POWER.md` as a fitted slope per designed bit, for both the
   quiet and the busy partner, against the matching E60 figure.
5. **Neither page said the placed design misses its 1250 ps target by about 2×**, nor what
   fraction of the capacitance is priced. Both are now in `POWER.md`'s "What ran" table.
