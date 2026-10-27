# Q126(b): what the multiply-add's toggle count really counts

*Mon 26 Oct 2026 (week 44), on the Intel. Settles recap gap 3, "the toggle count under every femtojoule,
disputed 2.9x", on the public RTL alone: no vault data, no card time, nothing private. The harness is
[`rtl-sim/fma_toggle`](../../../../rtl-sim/fma_toggle/), extended here with a settled counter
(`settle_count.cpp`, `scope_modules.py`, `recount.py`).*

## The answer, in one ladder

**21,331 toggles per random fp32 multiply-add reproduces only under the Verilator it was measured
with, and it was never a count of wires.** On aifoundry2's Verilator 5.042 it comes back to 0.2%; on a
current Verilator, on the same sources and the same card-dumped tiles, it is a third of that. Two separate
things sit between it and the number a power model wants, and they are now measured rather than argued.

| Per random multiply-add | | |
|---:|---|---|
| **21,331** | `nets`, as published 21 Sep | Verilator **5.042** on aifoundry2 |
| **21,379** | that same binary, re-run 26 Oct | the published figure does reproduce there |
| **7,014** | the same sources, the same card tiles, Verilator **5.052** | on the Intel |
| **7,109** | every value change in a VCD of that run, per RTL name | |
| **7,083** | changes between settled cycles, at most one per bit per cycle | |
| **3,968** | once per VCD identifier | Verilator's own alias merging |
| **1,301** | once per net, merging a name with its ancestor scope's name | **the figure to quote** |
| **1,007** | once per distinct waveform anywhere | a lower bound, see the caveat |

The first drop, 3.04x, is a simulator version — and it is the counter, not the circuit: traced under
5.042 itself, one run's coverage counter and its own VCD disagree by the same 2.94x (defect 1 below).
The second, 5.4x, is the RTL hierarchy naming the same wire at four levels. Together, **the count under
every fitted femtojoule is 8 to 16x too large** — 16x against the per-net count, which is a floor, and 8x
against the names-per-net route ("What the physical number is").

## The two defects

**1. The compressor cells were counted several times per cycle, and that is the tool, not the circuit.**
Between Verilator 5.042 and 5.052, on identical sources and identical card-dumped tiles, the total falls
3.04x — and **all of it is in two modules**:

| | 5.042 | 5.052 | ratio |
|---|---:|---:|---:|
| `txfma_csa` + `txfma_4_2_compressor` | 16,096 | 1,920 | 8.38 |
| every other module together | 5,236 | 5,094 | 1.03 |

Those two are the 4:2 compressor cell and the full adder inside it. `txfma_4_2_compressor_array` wires 64 of
them into a ripple-carry chain (`connect_carry[i]` into `connect_carry[i+1]`).

**The decisive measurement was then taken under 5.042 itself** (`verilator-5042-vcd.json`): the same
bench built with aifoundry2's Verilator 5.042, traced, so that one run carries both counters over the same
cycles. The coverage counter says **21,297** per multiply-add and **the VCD of that very run holds 7,233**
value changes per RTL name. The two counters disagree 2.94x *inside one simulation*, and again only in
those two modules:

| 5.042, one run, two counters | coverage | VCD, every value change | ratio |
|---|---:|---:|---:|
| `txfma_csa` + `txfma_4_2_compressor` | 16,101 | 1,904 | 8.45 |
| every other module together | 5,196 | 5,328 | 0.98 |
| **total** | **21,297** | **7,233** | **2.94** |

(The tracing build does not change what 5.042 counts: its coverage total, 21,297, and its compressor pair,
16,101, match the untraced 21 Sep binary's 21,379 and 16,096 — so tracing is not what moved the number.)

And the VCD's own contents barely move across the two releases — 7,233 against 7,084 raw, 7,205 against
7,059 settled, both 1.02x — so **the circuit's activity is the same under both; only the counter changed.**
Under 5.042 the counter scored about 14,000 assignments per multiply-add that the trace never recorded,
which is what a value taken while a cycle settles looks like: the trace writes the value a time step ends
on, the coverage counter scored each one on the way there. That is the defect the chip-diagram research
named — *"the coverage tool ... counts transient values while the model settles (30 counted where 2 changes
happened)"*, [`tensorfma32.json`](../2026-09-27-chip-diagram/research/tensorfma32.json), fact `tfma.lab` —
**confirmed by measurement, localised to two modules, and fixed upstream.** Under 5.052 the coverage count
and the settled VCD count differ by 1.0%, so nothing is left to remove.

**2. Every net inside a compressor carries two names, and the counter counts both.** This was the suspect
named for this job and it is exact, not approximate. `txfma_4_2_compressor` has nine nets — `x0`, `x1`, `x2`,
`x3`, `cin`, `cout`, `c`, `s` and the internal `s0` — and instantiates two `txfma_csa` positionally, so each
of the nine is also a port of a `txfma_csa`. One compressor instance declares 21 signals in the VCD; Verilator
gives them 19 identifiers, merging only the `bits` parameter and `csa0.sum` with `csa1.a`. Strip the parameter
and **18 identifiers carry 9 nets, each exactly twice**. Above them `txfma_4_2_compressor_array` names
six again (`x0..x3`, `c`, `s`) and `txfma_wallace1` names the array's ports again, so a wire in the tree is
counted up to four times. That is why `nets_ids` (3,968) is still
3.1x the per-net count: Verilator's alias merging does not cross a
module port.

The same research also said the coverage tool *"misses the compressor cells' input ports"*. **That half is
not confirmed.** Every one of `txfma_csa`'s five port names carries a toggle count, in the coverage file and
in the VCD alike. The tool counts those ports twice over; it does not miss them.

## What the physical number is

This is RTL, so no count here is a wire. Three routes, and they must be compared **on the same scope** —
two of them measure the whole multiply-add unit, the third measures the multiplier tree alone:

| | whole unit | the tree alone |
|---|---:|---:|
| the hierarchy merge, this file's own measurement | **1,301** (3,358 switching nets a lane) | **288** |
| settled RTL names ÷ the research's names-per-net (`tfma.names`: 2.55 for the unit, ~3.5 in the tree) | **2,778** | **906** (3,169 / 3.5) |
| that research's gate-level simulation of the chip's netlist, zero delay (`tfma.glitch`) | not measured | **1,244** (1,871 with gate delays) |

**On the two whole-unit routes the spread is 2.14x; on the tree, where all three can be compared, it is
4.3x** (288 to 1,244). The earlier draft of this file quoted a range of "1,200 to 2,800" for the whole
unit with 1,244 at its low end; that was a category error, since 1,244 is a tree-only figure. Scoped
properly the whole-unit range from the two routes that measure it is **1,300 to 2,800 per random
multiply-add**, against 21,331: a factor of **8 to 16**.

**Read 1,301 as a floor, not a best estimate.** A tree-only gate-level count of 1,244 sits just under a
whole-unit merged count of 1,301, which cannot both be right if the two designs were the same size — and
they are not. The netlist is the chip's own, larger design (its 1,851 multiply-add flip-flops against this
RTL's 838 register bits a lane; see the next section), and the hierarchy merge errs toward merging: two
nets that happen to carry the same waveform over the window and are named in nested scopes are counted
once. So the true whole-unit figure is at least 1,301 and plausibly nearer the 2,778 the names-per-net
route gives. Job (c) should fit against `nets_hier` as a total, treat the resulting energy per net as an
upper bound, and take its per-class split from `by_block_settled` rather than `by_block_hier` — see the
warning under "Files" for why the latter breaks a fit.

What is settled is the sign and the order: every per-toggle energy fitted against `nets` is an order of
magnitude too small per wire, and the correction is large enough to move the tree's fitted price into the
femtofarad-per-wire range of a standard-cell input, which is where the recap predicted it would land.

## The clocked-bit half of the dispute

The bench counts **602.5** register bits clocked per multiply-add; the chip's netlist
says 1,586 of 1,851 flip-flops. Most of that gap is the denominator. **This RTL has
838 register bits per lane**, not 1,851 — measured here directly as the bits the
unit's clock reaches each cycle (`ff_present`, added to `ff_acct.sv` for this job). In steady stream
595.2 of those 838 are enabled, so the fractions nearly
agree — **71%** here against 86% in the netlist — while the
absolute counts do not. (The bench's 602.5 is a whole-op average, fill and drain
included; 595.2 is the figure inside the stream.) So the clocked-bit term is not a
counting defect at all: it is the open Erbium RTL having fewer registers than the chip's own. A price fitted
on 602.5 and applied to a 1,851-flop unit is wrong by the register count, not by the gating model.

**The 838 is a complete count of this RTL's registers, and a third number is still unreconciled.**
Complete, because every register in `txfma_7s` is an instance of the `libs/registers` modules
`en_ff` (63), `rst_en_ff` (14) or `rst_ff` (6) — the three that `ff_acct.sv` replaces — and the directory
contains no `always_ff` and no `always @(posedge)` at all, so nothing clocks outside the counter.
Unreconciled, because the chip-diagram research's own note on fact `tfma.clocked` gives "the RTL view" as
**1,739 of 2,071** register bits, 2.5x this count, and its harness is not public. Either it counted more
than `txfma_top` (the lane's operand and bypass registers would do it) or one of the two counts is wrong.
Whoever owns Q124 should settle it; until then the clocked-bit price carries that 2.5x, and only the
*fraction* (71% here, 86% in the netlist) should be reused across designs.

## Method, and what would make it wrong

One tracing build of the same testbench, so the coverage counter and the VCD cover exactly the same cycles:
`+dump=<file>` opens a VCD at the start of the measured stream and ends the run after `+dump_uops` cycles.
`settle_count.cpp` reads the VCD and counts the five ways above; `scope_modules.py` resolves each VCD scope
(an instance path) to the RTL module it instantiates by reading the Verilog's own instantiation statements,
so the split is comparable with the coverage counter's split by file. The settled sample is the end of each
negedge step: the testbench drives operands at the negedge and clocks registers at the posedge, so the
combinational logic has settled there, and hardware evaluates once per cycle. Recipe, and how Verilator 5 was
put on the Intel: [`rtl-sim/fma_toggle/README.md`](../../../../rtl-sim/fma_toggle/README.md).

The 5.042 half of defect 1 is the same build and the same commands run on aifoundry2 against that box's
own Verilator 5.042 (`~/.local/verilator`), CPU only under `nice -n 19`, no card touched and nothing in
that box's checkout changed: randn, the 21 Sep card tiles, seed 1, three accumulator points, a 255-cycle
window, into `verilator-5042-vcd.json`.

**Caveats.**
- Both merges key on a bit's waveform over the window, so a stimulus that does not separate nets over-merges.
  The hierarchy merge only collapses a name with a name in an *ancestor* scope, which is why it is the one to
  quote; the unconstrained merge collapses badly whenever the operand stream has period 2, which is every
  rung of E60's ladder and `a_ones_b_randn` (it reports
  401 nets a lane, an artefact of the stimulus).
  Between a 16-cycle and a 512-cycle window the hierarchy merge moves from 943 to 1,325 toggles per multiply-add (2,495 to 3,445 nets a lane) and the unconstrained merge from 394 to 1,026 (908 to 2,449 nets). 
- Under the hierarchy merge a net is credited to the **outermost** module that names it, so the by-module
  split below answers "where is this wire first named", not "where does it switch". The tree's share falls
  from 45% of the name count to
  22% of the net count for that reason alone:
  `txfma_f1`, `txfmafrac_top` and `txfma_top` name the tree's wires through their ports before the tree does.
- Everything is zero delay, so glitches are absent here as they were before (`tfma.glitch` puts them at
  1.5x the toggles in the tree).
- **The merged counts themselves carry about 10% of tool version.** The same window and the same point
  measured under 5.042 (`verilator-5042-vcd.json`) give 1,427 per net against 5.052's 1,300, and 1,110
  distinct against 1,008 — 1.10x on both — because the two releases hand the VCD different identifier
  aliasing (`nets_ids` moves the other way, 3,339 against 3,953). The raw and settled name counts agree
  to 1.02x, so this is a property of the merge's input, not of the circuit.
- The window is 256 micro-op cycles (254 sampled transitions) inside a 512-micro-op op, at two accumulator
  points and two seeds, where
  21 Sep used four whole ops at three points and five seeds. The coverage column of `recount.json` can be
  checked against `toggles-5052.json`, which does use the full 21 Sep recipe.

## Files

| File | |
|---|---|
| `toggles-5052.json` | the 21 Sep bench re-run on the Intel with Verilator 5.052: same patterns, same card tiles, same seeds, `toggles.py`'s schema |
| `verilator-5042-aifoundry2.json` | the 21 Sep binary re-run on aifoundry2 on 26 Oct: 14 patterns, seed 1, accumulators at 1e3 ops |
| `verilator-5042-vcd.json` | the same bench **built and traced under 5.042** on aifoundry2: randn, seed 1, three accumulator points, a 255-cycle window — one run carrying both the coverage counter and the VCD counts, which is what shows the two disagreeing 2.94x inside one simulation |
| `recount.json` | the four VCD counts for the 14 fp32 patterns, `toggles.json`'s schema plus `nets_vcd_raw`, `nets_settled`, `nets_ids`, `nets_hier`, `nets_distinct`, `n_hier`, `n_distinct`, `ff_present` and their `by_block_*` siblings |
| `recount-hl.json` | the same for E60's 42 bit-flip ladder items (`tools/claims-v3/hl/make_hl.py`) |
| `window-convergence.json` | the merged counts against window length, 16 to 512 cycles, for four patterns |
| `hier-factors.json` | settled RTL names per merged net, by module, measured on randn at a 512-cycle window. **Attribution ratios, not names-per-net**: read its `_how_to_use` before dividing by anything |

**The counts file for a refit is `recount.json`**, key `<pattern>.mean.nets_hier`, per TensorFMA32 op on one
minion; divide by 4,096 for per multiply-add. `nets` is kept beside it so a refit can be run both ways.
`nets_hier` exists for every pattern and every ladder item measured here, so **a refit needs no factor at
all.**

🛑 **`nets_hier` is sound as a total. `by_block_hier` is not a per-block net count — do not split
price classes with it.** Under the hierarchy merge a net is credited to the **outermost** module that
names it, and the tree's wires are named by `txfma_f1`, `txfmafrac_top` and `txfma_top` through their
ports before the tree names them. So the multiplier's share of the activity reads 54.8% of the settled
name count but **22.8%** of `by_block_hier` on randn — and **0.0%** on `pow2` and `signs`, where the few
switching nets are all named from outside first. A least-squares fit over patterns whose multiplier share
jumps between 0% and 29% for an attribution reason has no multiplier column left to fit, which is the
likely source of the **negative** multiplier price (−1.769 fJ) the load model's per-net rung reports
([`2026-10-26-load-model/README.md`](../2026-10-26-load-model/README.md)). **To split classes, take the
shares from `by_block_settled` (names, attributed where they switch) and scale the whole unit by
`nets_hier / nets_settled`** — one factor for the unit, 5.33 on randn.

The same trap voids the per-module factors in `hier-factors.json`: 12 of the 40 switching modules hold no
merged nets and so have no factor at all (`txfma_csa` and `txfma_booth_ppg_32r4` among them, 22% of the
settled toggles between them), and 7 more carry factors above 10 — up to 274.6 for `txfma_adder` — that are
attribution artefacts, not names-per-net. The file's old `_note` said to divide `by_block_settled` by them
module by module; done literally that leaves the 12 undivided (name counts mixed into a net total) and
crushes the 7 to nothing. `hier-factors.json` now lists all 40, nulls the 12, flags the 7, and its
`_how_to_use` says to use the whole-unit factor instead.

### Per random multiply-add, pattern by pattern

`nets` is the bench's own counter (Verilator toggle coverage). *21 Sep* is the published file;
*5.042* is that same binary re-run on aifoundry2 on 26 Oct (seed 1, accumulators at 1e3 ops);
*5.052* is the Intel, same sources, same card tiles, same seeds as 21 Sep. The last four columns
are the VCD counts (seeds 1-2, a 254-cycle window at each of two accumulator points).

| pattern | 21 Sep | 5.042 re-run | 5.052 | settled | per VCD id | per net (hier) | distinct | lanes valid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zeros | 0.013 | 0.013 | 0.013 | 0.012 | 0.008 | 0.004 | 0.000 | 0 |
| ones | 7.5 | 7.7 | 0.765 | 0.325 | 0.258 | 0.191 | 0.016 | 4,096 |
| pi | 10.0 | 14.0 | 0.788 | 0.348 | 0.281 | 0.215 | 0.016 | 4,096 |
| sparse50 | 4,242 | 5,030 | 1,524 | 1,535 | 871 | 285 | 226 | 1,003 |
| uniform | 20,977 | 21,154 | 6,206 | 6,224 | 3,507 | 1,081 | 869 | 4,096 |
| randn | 21,331 | 21,379 | 7,014 | 7,083 | 3,968 | 1,301 | 1,007 | 4,096 |
| signs | 1,201 | 1,152 | 1,041 | 1,129 | 603 | 184 | 77.7 | 4,096 |
| pow2 | 1,511 | 1,465 | 1,418 | 1,516 | 895 | 288 | 210 | 4,096 |
| mant | 20,735 | 20,861 | 5,972 | 5,881 | 3,317 | 1,014 | 820 | 4,096 |
| a_randn_b_ones | 10,751 | 10,743 | 3,284 | 3,298 | 1,884 | 571 | 40.2 | 4,096 |
| a_ones_b_randn | 5,763 | 5,802 | 3,069 | 3,135 | 1,646 | 436 | 187 | 4,096 |
| ternary | 548 | 513 | 511 | 533 | 289 | 106 | 53.4 | 1,843 |
| sparse75 | 962 | 1,001 | 383 | 412 | 238 | 78.8 | 56.8 | 230 |
| checker | 5.3 | 5.2 | 3.6 | 2.8 | 1.4 | 0.813 | 0.044 | 1,024 |

### randn, block by block

| RTL module | 21 Sep (5.042) | 5.052 | 5.042/5.052 | VCD raw | settled | per id | per net (hier) | nets/lane |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| txfma_csa | 8,519 | 1,074 | 7.94 | 1,057 | 1,053 | 722 | 0 | 0 |
| txfma_4_2_compressor | 7,577 | 847 | 8.95 | 855 | 851 | 722 | 95.0 | 200 |
| txfma_4_2_compressor_array | 672 | 672 | 1.00 | 655 | 653 | 150 | 71.8 | 207 |
| txfma_wallace1 | 432 | 432 | 1.00 | 435 | 434 | 230 | 82.1 | 197 |
| txfma_f1 | 417 | 417 | 1.00 | 420 | 418 | 274 | 274 | 734 |
| txfma_f3 | 378 | 279 | 1.36 | 299 | 297 | 157 | 33.7 | 89 |
| txfmafrac_top | 349 | 348 | 1.00 | 346 | 345 | 298 | 240 | 575 |
| txfma_booth_ppg_32r4 | 342 | 342 | 1.00 | 344 | 343 | 130 | 0 | 0 |
| txfma_booth_ppg_32r4_norm | 341 | 341 | 1.00 | 344 | 343 | 17.6 | 8.6 | 54 |
| txfma_adder | 302 | 306 | 0.99 | 294 | 293 | 104 | 1.1 | 4 |
| txfma_f2 | 265 | 265 | 1.00 | 266 | 265 | 130 | 105 | 246 |
| txfma_f0 | 245 | 246 | 1.00 | 246 | 245 | 173 | 7.5 | 22 |
| txfma_wallace2 | 178 | 178 | 1.00 | 179 | 178 | 58.6 | 39.2 | 89 |
| txfma_f4 | 141 | 141 | 1.00 | 139 | 138 | 47.2 | 22.2 | 46 |
| txfma_top | 132 | 132 | 1.00 | 152 | 152 | 148 | 128 | 376 |
| txfma_f6 | 129 | 129 | 1.00 | 126 | 126 | 92.6 | 8.9 | 26 |
| txfma_f5 | 125 | 125 | 1.00 | 122 | 122 | 63.3 | 30.7 | 67 |
| txfma_lxd | 116 | 106 | 1.10 | 104 | 104 | 67.3 | 41.1 | 104 |
| txfma_trz2 | 111 | 100 | 1.11 | 98.5 | 98.1 | 71.2 | 37.5 | 81 |
| txfmaexp_top | 71.0 | 72.4 | 0.98 | 129 | 129 | 96.3 | 26.1 | 87 |
| txfma_norm_shf | 67.9 | 67.5 | 1.01 | 66.0 | 65.7 | 23.8 | 2.1 | 4 |
| txfmactl_top | 57.7 | 58.6 | 0.98 | 100 | 99.7 | 65.3 | 13.1 | 50 |
| txfma_align_shf | 53.9 | 21.9 | 2.46 | 0 | 0 | 0 | 0 | 0 |
| txfma_e2 | 49.6 | 49.6 | 1.00 | 60.8 | 60.6 | 22.5 | 11.9 | 31 |
| txfma_rnd_adder | 46.3 | 46.3 | 1.00 | 45.2 | 45.0 | 30.5 | 0 | 0 |
| txfma_trz | 39.4 | 39.5 | 1.00 | 39.4 | 39.3 | 11.4 | 0 | 0 |
| txfma_e5 | 38.7 | 42.4 | 0.91 | 52.9 | 52.6 | 27.7 | 13.5 | 38 |
| txfma_e1 | 26.3 | 26.3 | 1.00 | 25.3 | 25.2 | 7.0 | 2.7 | 10 |
| **total (all modules)** | **21,331** | **7,014** | **3.04** | **7,109** | **7,083** | **3,968** | **1,301** | **3,358** |

### Register bits per multiply-add

`present` is every register bit the unit's clock reaches that cycle; `clocked` is the subset whose
enable is high, the bench's `ff_clocked`; `changed` is `ff_toggles`. Per lane.

| pattern | clocked | present | fraction | changed |
|---|---:|---:|---:|---:|
| zeros | 6.0 | 838.0 | 0.01 | 0.0 |
| ones | 595.2 | 838.0 | 0.71 | 0.1 |
| pi | 595.2 | 838.0 | 0.71 | 0.1 |
| sparse50 | 145.4 | 838.0 | 0.17 | 19.4 |
| uniform | 595.2 | 838.0 | 0.71 | 24.5 |
| randn | 595.2 | 838.0 | 0.71 | 62.1 |
| signs | 595.2 | 838.0 | 0.71 | 53.7 |
| pow2 | 595.2 | 838.0 | 0.71 | 59.0 |
| mant | 595.2 | 838.0 | 0.71 | 7.5 |
| a_randn_b_ones | 595.2 | 838.0 | 0.71 | 27.7 |
| a_ones_b_randn | 595.2 | 838.0 | 0.71 | 56.7 |
| ternary | 261.5 | 838.0 | 0.31 | 27.4 |
| sparse75 | 42.3 | 838.0 | 0.05 | 5.4 |
| checker | 156.0 | 838.0 | 0.19 | 0.1 |

### How the merged counts settle with the window

Both merges key on a bit's waveform over the window, so a short window merges nets that happen to
agree on it. Per multiply-add, randn seed 1, accumulators at 1e3 ops.

| window (cycles) | settled | per id | per net (hier) | nets/lane (hier) | distinct | nets/lane (distinct) |
|---|---:|---:|---:|---:|---:|---:|
| 16 | 6,314 | 3,538 | 943 | 2,495 | 394 | 908 |
| 32 | 6,625 | 3,699 | 1,154 | 3,092 | 763 | 1,868 |
| 64 | 6,972 | 3,896 | 1,263 | 3,255 | 917 | 2,194 |
| 128 | 7,075 | 3,960 | 1,313 | 3,387 | 1,003 | 2,368 |
| 256 | 7,054 | 3,951 | 1,319 | 3,423 | 1,023 | 2,428 |
| 512 | 7,058 | 3,955 | 1,325 | 3,445 | 1,026 | 2,449 |

### E60's bit-flip ladder (tools/claims-v3/hl/make_hl.py), per multiply-add

A = 1.0 for the `lq`/`ls`/`bit` families and pi for `lb`; the named bits of B flip every cycle, so
the stream has period 2 and the distinct-waveform merge collapses — read the hier column.

| item | 5.052 `nets` | settled | per id | per net (hier) | nets/lane |
|---|---:|---:|---:|---:|---:|
| bit_0 | 365 | 379 | 207 | 31.3 | 74 |
| bit_12 | 643 | 647 | 381 | 67.4 | 108 |
| bit_16 | 660 | 660 | 390 | 77.7 | 119 |
| bit_20 | 577 | 580 | 340 | 62.9 | 104 |
| bit_22 | 704 | 720 | 415 | 70.5 | 111 |
| bit_23 | 226 | 276 | 155 | 35.1 | 79 |
| bit_25 | 152 | 181 | 102 | 25.9 | 68 |
| bit_27 | 273 | 331 | 194 | 45.6 | 88 |
| bit_29 | 355 | 420 | 244 | 41.9 | 85 |
| bit_30 | 295 | 336 | 190 | 35.0 | 79 |
| bit_31 | 142 | 195 | 138 | 27.9 | 72 |
| bit_4 | 365 | 367 | 210 | 38.7 | 82 |
| bit_8 | 639 | 646 | 377 | 66.6 | 107 |
| lb_h0 | 0.833 | 0.359 | 0.292 | 0.225 | 45 |
| lb_h1 | 1,283 | 1,271 | 736 | 75.4 | 120 |
| lb_h12 | 4,228 | 4,200 | 2,348 | 240 | 285 |
| lb_h16 | 5,314 | 5,292 | 2,941 | 232 | 276 |
| lb_h2 | 1,666 | 1,653 | 958 | 104 | 148 |
| lb_h23 | 7,305 | 7,326 | 4,048 | 199 | 241 |
| lb_h4 | 2,157 | 2,139 | 1,224 | 123 | 168 |
| lb_h8 | 3,169 | 3,147 | 1,777 | 179 | 223 |
| lq_h0 | 0.828 | 0.354 | 0.287 | 0.220 | 44 |
| lq_h1 | 367 | 380 | 207 | 32.3 | 76 |
| lq_h12 | 1,989 | 2,002 | 1,029 | 168 | 209 |
| lq_h16 | 2,701 | 2,720 | 1,399 | 183 | 223 |
| lq_h2 | 492 | 504 | 269 | 42.6 | 86 |
| lq_h23 | 3,761 | 3,795 | 1,931 | 215 | 253 |
| lq_h4 | 811 | 823 | 433 | 69.0 | 112 |
| lq_h8 | 1,315 | 1,330 | 681 | 103 | 145 |
| ls_h12 | 2,472 | 2,497 | 1,331 | 153 | 193 |
| ls_h16 | 2,820 | 2,845 | 1,475 | 183 | 222 |
| ls_h2 | 888 | 900 | 512 | 78.0 | 119 |
| ls_h4 | 1,418 | 1,431 | 806 | 120 | 159 |
| ls_h8 | 2,018 | 2,033 | 1,108 | 153 | 192 |
| ord_binary_0 | 885 | 879 | 518 | 130 | 719 |
| ord_binary_19 | 1,456 | 1,460 | 863 | 221 | 1,016 |
| ord_gray_0 | 840 | 834 | 492 | 130 | 736 |
| ord_gray_19 | 1,317 | 1,323 | 783 | 216 | 1,044 |
| ord_maxflip_0 | 1,314 | 1,306 | 766 | 174 | 711 |
| ord_maxflip_19 | 1,627 | 1,641 | 961 | 256 | 1,039 |
| ord_shuffled_0 | 1,078 | 1,071 | 631 | 160 | 737 |
| ord_shuffled_19 | 1,496 | 1,506 | 887 | 241 | 1,044 |

