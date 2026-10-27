# Place, route, parasitics and switching power of the open netlist (Q126)

26 October 2026, on aifoundry2. Companion to [`README.md`](README.md) (the cell census). The flow:
[`tools/open-flow/txfma/`](../../../../tools/open-flow/txfma/README.md), scripts `pnr.tcl`,
`mktiles.sh`, `gatesim.sh`, `tb_gate.sv`, `power.py`, `ladder.py`.

> **Corrected the same day, after review.** The first version of this file made several claims it
> should not have, and they are restated below with the measurements that settle them:
> its headline toggle agreement ("3.5% apart") compared a Booth+tree+adder figure against a
> **tree-only** one; its 35.4 fJ per flipped bit was a two-point difference divided by counted bus
> bits and compared against the **quiet**-partner board price, while the run was the **busy**
> partner; it quoted "1250 ps (800 MHz)" as the operating point of a placed design that misses
> that target by about 2×; and it priced switching alone without saying that half the design's
> capacitance, by farads, is unpriced and that the cells' own internal energy is larger than the
> switching energy, not "a few per cent" of it. The ladder was re-run at h = 1, 2, 4, 8 for both
> partners so the slope is a fit rather than a difference. [What changed, and by how
> much](#what-the-first-version-got-wrong) is at the foot of this file.

**What this answers.** The project's per-flip prices are all a measured watt divided by a toggle
count that came from one bench, and the one gate-level recount that exists was made with a
tape-out flow nobody outside can run. Here the same stimulus is driven into the open netlist, the
capacitances come from an open extractor and an open 7 nm library, and the energy is arithmetic
anyone can repeat.

## What ran, and what did not

| Step | State |
| --- | --- |
| Floorplan, pin placement, global placement, `repair_design`, detailed placement | done |
| Clock-tree synthesis (`BUFx2/3/4/5`), propagated clock | done, 257 clock nets |
| Global route, Steiner parasitics, per-net capacitance for all 20,383 nets | done |
| **Timing closure against the 1250 ps SDC** | **not met: wns −1,219.14 ps, tns −44,409 ps** |
| SDF written for the timed pass | done, 18 MB |
| **Detailed route (TritonRoute), OpenRCX, SPEF with coupling caps** | **blocked** |
| The timed bench itself (`tb_timed.v`), and its zero-delay run under Icarus | done |
| **SDF annotation, and so the glitch ratio** | **blocked: Icarus aborts** |

**The operating point, stated honestly.** The SDC asks for **1250 ps (800 MHz)** and the placed
design does not meet it: the worst path, from `txfmafrac0_top/txfma0_f2`'s input register, arrives
2,772 ps after the launch edge against 1,553 ps required, so **this netlist would run near
400 MHz**, not 800 (`work/pnr/pnr.log`: `wns -1219.14`, `tns -44409.35`; the `mixed` netlist is
the same, `wns -1165.90`). Nothing was done about it — no `repair_timing`, no second pass — because
the question here is energy per toggle, not speed, and a slower netlist still tells you what a
toggle costs. But two consequences bear on the numbers below and neither was stated before:

- **the clock tree whose 1,846 fF and 32.7% share are quoted here is CTS's answer to a constraint
  the design misses by 2×.** A netlist that actually closed at 800 MHz would have a different
  (probably larger) tree;
- the energies are priced at **0.517 V**, the minion rail, while the liberty is ASAP7 RVT **TT at
  nominal 0.7 V, 25 °C** (`asap7sc7p5t_SEQ_RVT_TT_nldm_220123.lib`: `nom_voltage : 0.7`,
  `PVT_0P7V_25C`). That is deliberate: capacitance here is 30,291 fF of pin against 16,802 fF of
  wire, both geometry and very nearly voltage-independent, so ½CV² at the real rail is the right
  arithmetic — unlike an energy taken straight out of the liberty, which would need (V/0.7)². The cell
  **delays** at 0.7 V are not transferable to 0.517 V, which is a second reason the timing numbers
  above are only indicative.

Everything below therefore uses the **global-route Steiner estimate** of wire capacitance, not an
extraction: it has no coupling term, so it is a lower bound on the wire half of each net, while the
pin half comes from ASAP7's liberty and is exact.

> 🛑 **Corrected Tue 27 Oct 2026 (Q129(a)).** The second clause of that sentence is wrong. The
> estimate does carry a coupling term: the ORFS asap7 `setRC.tcl` hands the estimator **0.1658 fF
> per micron** for a signal wire, which is a layer's *total* capacitance at nominal spacing, with
> the neighbour coupling already bundled in and grounded. Detailed routing now closes
> ([`../2026-10-27-q129-routed-netlist/`](../2026-10-27-q129-routed-netlist/README.md)) and the
> extraction puts the Steiner estimate **20–23% above** it, not below: 14,427 fF against 12,006 fF
> on `mixed` at a Miller factor of 1 (**+20.2%**), and 15,533 against 12,605 on the kept netlist
> (**+23.2%**) — equivalently, the extraction reads **17–19% below** the estimate. The wire half
> below is therefore **not** a floor, and the between-cell wire energy of a random multiply-add
> falls by about a quarter when it is extracted. The pin half is exactly as described, and routing
> does not move it at all.
>
> *(Amended the same day: this block first said "17–20% above", which was the two
> below-percentages with the word "above" on them — a direction error. 12,006 ÷ 14,427 = 0.832 and
> 12,605 ÷ 15,533 = 0.812 are the ratios; their reciprocals, 1.202 and 1.232, are the "above".)*

## Toggles and energy per multiply-add

One lane, one TensorFMA32 op (512 micro-ops, 547 cycles), ASAP7 RVT TT, 0.517 V. Energy is
**switching only** — ½CV² per toggle, CV² per clock cycle — and § "What 1.516 pJ is not" says by
how much that is a floor. Activity is the difference of two runs of the same bench, one with the
measured op and one without, because a SAIF counts the whole simulation.

| Pattern | flipped input bits / mul-add | signal toggles / mul-add | pJ / mul-add (switching) | + cells' internal | clock's share |
| --- | ---: | ---: | ---: | ---: | ---: |
| `randn` (the 21 Sep random tile) | 33.9 | **3,623** | **1.516** | 1.946 | 32.7% |
| `lb_h8` (ladder, busy partner A = π, h = 8) | 13.0 | 1,759 | 0.962 | 1.171 | 51.6% |
| `lq_h8` (ladder, quiet partner A = 1.0, h = 8) | 13.6 | 1,068 | 0.800 | 0.927 | 62.1% |
| `lb_h0` / `lq_h0` (the ladders' own zero rungs) | 0.23 / 0.19 | 37 / 36 | 0.509 / 0.508 | 0.513 | 97.6% / 97.7% |
| `ones` | 0.06 | 31 | 0.507 | 0.511 | 97.9% |
| `zeros` | 0 | 0.008 | 0.217 | 0.217 | 100% |

"Flipped input bits" is the bench's own `bus_toggles` — every bit that changes on the in1/in2/in3
words presented to the lane, which includes the accumulator the bench writes back — in
`power/sim_acct.txt`. It is **not** the ladder's designed Hamming distance; the next section keeps
the two apart, because mixing them is what the first version of this file got wrong.

Three things fall out:

- **Zero gating shuts 57% of the clock tree.** With every operand word zero the lane gets no valid
  bit, the unit's 13 clock gates stay shut, and the clock capacitance that still toggles falls from
  1,846 fF to 802 fF. Four signal toggles survive in the whole op. The 0.217 pJ per multiply-add
  that remains is the ungated root of the tree, and it is the floor this unit cannot go below while
  its clock runs.
- **The clock tree is a third of a busy multiply-add and nearly all of an idle one.** At `randn`
  it is 32.7% of the switching energy; at `ones`, where the data barely moves, 97.9%. Any model
  that prices a load by its flipped bits alone is pricing the smaller half at low activity.
  (See the census page on how much of that is a mapper's choice: forbidding `DFFHQx4` moves
  sequential area 20%.)
- **The busy partner costs more at the same h, and the first flipped bit costs most.** At h = 8,
  A = π costs 0.962 pJ against A = 1.0's 0.800. The ladder is strongly non-linear: see below.

## The Hamming ladder: energy per flipped operand bit, against E60's measurement

The V3-HL ladder ([`tools/claims-v3/hl/`](../../../../tools/claims-v3/hl/README.md)) flips the low
`h` bits of a B mantissa between one multiply-add and the next, with the partner operand A held
either quiet (`lq`, A = 1.0) or busy (`lb`, A = π). E60 ran it on three cards; the open netlist now
runs the same operand files, on both netlists. All five rungs of both ladders, h = 0, 1, 2, 4, 8
(the hierarchy-kept netlist; `power-mixed/` holds the same ten runs on the `mixed` one):

| h | `lq` pJ / mul-add | `lq` clock share | `lb` pJ / mul-add | `lb` clock share |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0.5083 | 97.7% | 0.5088 | 97.6% |
| 1 | 0.5704 | 87.0% | 0.6869 | 72.3% |
| 2 | 0.6046 | 82.1% | 0.7369 | 67.4% |
| 4 | 0.6891 | 72.0% | 0.7897 | 62.9% |
| 8 | 0.7998 | 62.1% | 0.9618 | 51.6% |

**Fitted the way E60's own reducer fits it** — a line over h ≥ 1 with a free intercept, against
the *designed* flip count (`reduce_hl.py`, regressor `designed`) — and set beside the matching
card number from `docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt` (aifoundry3, 600 MHz,
521.8 mV, 4 passes):

| | open netlist, switching | + cells' internal | E60 at the board | switching as % of board |
| --- | ---: | ---: | ---: | ---: |
| `lq` per **designed** bit (A = 1.0) | **32.9 fJ** | 46.3 fJ | **116.7 ± 0.6 fJ** | 28% (40% with internal) |
| `lb` per **designed** bit (A = π) | **38.5 fJ** | 54.9 fJ | **129.9 ± 0.5 fJ** | 30% (42% with internal) |
| `lq` per counted **bus** bit | 20.0 fJ | 28.1 fJ | 74.7 fJ | 27% (38%) |
| `lb` per counted **bus** bit | 27.5 fJ | 39.2 fJ | 85.6 fJ | 32% (46%) |

The same four slopes on the `mixed` netlist (`power-mixed/`) are 34.8, 38.3, 21.1 and 27.4 fJ —
within 6% of these — so the hierarchy choice that halves the tree's cell count barely touches the
energy per flipped bit.

So **the arithmetic inside one lane's multiply-add is about 30% of what the board pays for a
flipped operand bit on switching alone, and about 40% once the cells' own internal energy is
added** — and that is still a floor, because half the capacitance is unpriced (below). The rest is
what the project has been calling transport: the register file's read ports, the operand bus, the
result path, plus leakage and everything outside the lane.

**Three things make this comparison delicate, and the first version of this file got all three
wrong.** They are worth stating because the same traps apply to any gate-level-versus-board
comparison:

1. **The denominator.** E60's price is per *designed* bit — the h bits the ladder was built to
   flip. The bench's `bus_toggles` counts more than that: at `lb_h8` it is 13.0 per multiply-add
   against 8 designed, the extra ≈ 4.8 being the accumulator word, which the bench writes back
   (`tb_gate.sv` l. 106: `C[...] <= out_data[l].data`). Dividing by the wrong one moves the answer
   38%. Both denominators are given above, each against its own E60 counterpart. The bench's live
   accumulator is **not** a difference from the card: V3-HL's "sources are never written and every
   sink is rewritten with the same value" describes its `ec` (instruction-catalogue) items, and the
   ladder's own amendment A2 says of the fma families that the primary regressor is "the
   RTL-counted operand-bus bits (A + B + C: the accumulator reads co-vary with h)". So the bus row
   above is a like-for-like comparison and the designed row is the cleaner one.
2. **The partner.** `lb` is the *busy* partner; the board's 116.7 fJ is the *quiet* one. Comparing
   `lb` against 116.7 fJ was an 11% error on top of the first. Both partners now ran.
3. **Slope, not difference.** The ladder is markedly non-linear — the free intercept is 141 fJ for
   `lb` and 34 fJ for `lq`, i.e. the first flipped bit costs several times the marginal one — so
   a two-point (h8 − h0) ÷ 8 reads 56.6 fJ where the fitted slope reads 38.5. E60's own reducer
   fits a slope, and the card ladder shows the same shape (`lb first flip: 1.954 W`, intercept
   +0.94 W, against `lq`'s 0.594 W and −0.42 W). The fitted slopes are what the table above
   quotes.

## Per block, random data

Toggles per multiply-add and the energy they cost, from `power/power_gr_randn.json`
(the hierarchy-kept netlist — see the scope note below it):

| Block | toggles / mul-add | pJ per op | fJ / mul-add |
| --- | ---: | ---: | ---: |
| Booth rows (`f1/ppg`) | 439.1 | 39.27 | 76.7 |
| Wallace tree (`f1/wallace1` + `f2/wallace2`) | 716.3 | 92.98 | 181.6 |
| Product adder (`f2/prod_adder_64b`) | 45.4 | 5.49 | 10.7 |
| **multiplier (the three together)** | **1,200.8** | **137.7** | **269.1** |
| normaliser (`f5/norm_shf`) | 226.6 | 24.77 | 48.4 |
| aligner (`f3/align_shf_48`) | 183.3 | 17.39 | 34.0 |
| leading-digit (`f4/lxd_ps_hi`) | 175.2 | 17.32 | 33.8 |
| exponent (`txfmaexp0_top`) | 46.3 | 8.90 | 17.4 |

### The toggle comparison, at matched scope

The first version of this file put the multiplier's **1,200.8** against the tape-out flow's
**1,244** and called them "3.5% apart". That was a scope error. `tfma.glitch` reads *"the multiplier
**tree** makes about 1.5 times as many toggles as at zero delay (1,871 against 1,244 physical
toggles per random multiply-add)"* — 1,244 is **tree only**, and the same facts file keeps "the
Booth path", "the tree's four levels" and "the product adder" apart in `tfma.asbuilt.cells`.
Q126(b) made the same correction in the same repo on the same day
([`../2026-10-26-toggle-recount/README.md`](../2026-10-26-toggle-recount/README.md): *"that was a
category error, since 1,244 is a tree-only figure"*). Scoped properly:

Both netlists were run, because the hierarchy-kept one carries twice the tree cells of the
normally optimised `mixed` one and so is an upper bound on its own toggle count:

| scope | kept hierarchy | **`mixed`** (the comparator) | the tape-out flow, zero delay | apart |
| --- | ---: | ---: | ---: | ---: |
| the Wallace tree alone | 716.3 | **628.2** | **1,244** (`tfma.glitch`) | **1.98×** |
| tree + product adder (the as-built "tree" folds the adder's first layer in) | 761.7 | 673.6 | 1,244 | 1.85× |
| Booth + tree + adder — *the figure first published against 1,244* | 1,200.8 | 945.9 | not that scope | — |
| the whole unit, unique physical nets | 3,623 | **3,299** | not measured by that flow; Q126(b)'s two whole-unit routes give **1,300–2,800** | 1.2–2.5× |

So the two flows agree on the *order* of the tree's toggle count and of the whole unit's, and
disagree by about **2×** on the tree. That is still the first outside check this count has had —
every per-toggle price in the project is a watt divided by a number like it — but it is a 2×
disagreement, not a 3.5% agreement. The direction is worth noting: the open flow makes **fewer**
tree toggles than the tape-out flow, on a tree with about the same transistor count, so the gap is
not "the open netlist is bigger".

Every `mixed` figure above comes from `power-mixed/`, the same bench and the same stimulus
driven into the netlist whose boundaries only the four multiplier blocks keep. Its per-net
capacitance covers 56.3% of the design's farads against the kept netlist's 50.5%, and it prices a
random multiply-add at 1.468 pJ against 1.516, with the clock at 32.0% against 32.7% — so none of
the conclusions in this file turn on the hierarchy choice, even though the cell counts do.

For the other disputed count: the RTL bench counts 21,331 toggles of *named RTL signals* per random
multiply-add; Q126(b)'s recount of the same RTL on the same stream gets 7,014–7,109 on a current
Verilator, and 1,301 once each physical net is counted once. The open netlist's whole unit, counted
on real wires with each one paid for once, gives **3,623** — between Q126(b)'s per-net floor
(1,301) and its names-per-net estimate (2,778), and a factor of 5.9 below the lab's 21,331.

## What 1.516 pJ is not

It is **switching energy on the half of the design the simulation can name**, and both halves of
that sentence push the same way.

- **Capacitance coverage, in farads, not net counts.** For `randn`, 10,460 of the 20,383 extracted
  nets are found in the simulation and priced — but those carry only **23,762 fF of the design's
  47,093 fF, so 50.5% of the capacitance is priced and 49.5% is not** (`coverage.cap_fraction_priced`
  = 0.5046 in `power/power_gr_randn.json`; `tools/open-flow/txfma/power.py:271` computes it as
  `cap_priced_fF / cap_all_fF`, so the field names what IS priced).
  🛑 **Corrected Mon 26 Oct 2026 (Q128(e)).** This sentence and the table row below read the field as
  the unpriced share. The arithmetic was always right — 23,762 ÷ 47,093 = 50.5% — and so was the
  conclusion, because the unpriced half is 49.5%; only the label was inverted. The shortfall is not idle nets: every net the simulation names and that the
  extractor knows is active here. It is the 9,923 nets CTS and `repair_design` created after the
  netlist was simulated, plus nets the simulator folded away. They switch, so leaving them out is
  an underestimate of the same order as the number itself.
- **The cells' own internal energy is larger than the switching energy, not a few per cent of it.**
  OpenROAD's `report_power` on this very netlist reads **internal 1.47e-02 W against switching
  1.20e-02 W** — internal is **55% of the dynamic power** — at its default activity
  (`work/pnr/pnr.log`; the `mixed` netlist reads 55.2 / 44.8). That build has no `read_saif`, so
  that split is not under this bench's activity. What *is* under this bench's activity is the
  `internal_estimate` block `power.py` now writes with `--cell-energies`: every signal transition
  priced at Q126(d)'s census-weighted internal energy from ASAP7's own liberty, 0.2179 fJ at 0.7 V
  and **0.1188 fJ at 0.517 V**, which adds **0.431 pJ** to `randn`'s 1.516 — a factor of 1.28. That
  is itself a floor, because Q126(d) prices the 14,119 combinational cells and skips the 1,953
  flip-flops' and 13 clock gates' own clock-pin energy, which on a design whose clock is a third of
  the switching is not small.

**So quote 1.516 pJ as a floor, and expect the true dynamic energy of one random fp32 multiply-add
in this netlist to be two to three times it.** The *ratios* — the ladder's slope, the clock share,
one block against another, one pattern against another — are much more robust than the absolute,
because both omissions scale with activity. Everything this directory concludes is a ratio.

## Files

| File | What |
| --- | --- |
| `power/power_gr_<pattern>.json` | the hierarchy-kept netlist: totals, coverage (nets and farads), the internal estimate, and every block at three levels of hierarchy. 13 patterns: `randn`, `ones`, `zeros`, and both ladders at h = 0, 1, 2, 4, 8 |
| `power-mixed/power_gr_<pattern>.json` | the same 13 on the `mixed` netlist (flattened except the four multiplier blocks) |
| `power/sim_acct.txt` | the bench's own counters per run (cycles, valid lane-cycles, flipped bus bits) |
| `net_cap_globalroute.txt.gz`, `net_cap_globalroute_mixed.txt.gz` | wire and pin capacitance, in farads, for all 20,383 (16,403) extracted nets |
| `power/toggles_zero_iverilog.json` | the zero-delay pin-transition count from the timed bench, waiting for its timed twin |

## The two blockers, and what would clear them

1. **Detailed routing does not close, so there is no SPEF and no coupling capacitance.**
   TritonRoute in the only OpenROAD binary installable without root (the litex-hub conda build,
   `f12e2f47`, a **2022** build) fails with `DRT-0255 Maze Route cannot find path` — and the nets
   it names are **top-level port nets at the die boundary**, never core logic: `clock`,
   `trans_coefficients[6/51]`, `in_data[4/33/48]`, `out_data_res[0/8/9/14/29]`. Every failing
   `routeBox` lies on an edge of the die (`( 0 15119 ) ( 3779 18899 )` and its siblings, x or y
   pinned to 0–3779, which is one routeBox width). **Ten configurations were run and the
   diagnosis survives all of them:**

   | # | netlist | util | core space | pins | global route | detailed route | result |
   | ---: | --- | ---: | ---: | --- | --- | --- | --- |
   | 1 | keep | 30 | 2 µm | M4/M5 | M2–M7, clk M4–M7 | M2–M9 | 8 × DRT-0255: `clock`, `trans_coefficients[51]` |
   | 2 | keep | 30 | 2 µm | M6/M7, `-min_distance 4` | M2–M7 | M2–M9 | 9 × DRT-0255: `clock`, `out_data_res[29]` |
   | 3 | keep | 40 | 2 µm | M4/M5 | M2–M7 | M2–M9 | 4 × DRT-0255: `clock`, `out_data_res[8]` |
   | 4 | keep | 22 | 2 µm | M4/M5 | M2–M7 | M2–M9 | 3 × DRT-0255: `trans_coefficients[6]` |
   | 5 | keep | 30 | 2 µm | M4/M5 | M2–M7 | **M2–M7 (matched)** | **DRT-0155**: the global route emitted an M8 guide for `in_data[48]` anyway |
   | 6 | keep | 30 | 2 µm | M4/M5 | M2–M7, **clk M2–M7** | M2–M7 | DRT-0155, the same guide |
   | 7 | keep | 30 | 2 µm | M4/M5 | **M2–M9** | M2–M9 | 8 × DRT-0255, unchanged |
   | 8 | keep | 30 | **6 µm** | M4/M5 | M2–M9 | M2–M9 | 7 × DRT-0255: `clock`, `in_data[33]`, `out_data_res[0]` |
   | 9 | keep | 30 | 2 µm | **M2/M3** | M2–M9 | M2–M9 | 13 × DRT-0255, worse |
   | 10 | **mixed** | 30 | 2 µm | M4/M5 | M2–M7 | M2–M9 | 2 × DRT-0255: `clock`, `in_data[4]` — the closest any run came |

   Rows 5 and 6 are the informative ones: matching the two layer ranges, which looks like the
   obvious fix, only trades the failure for a different one, because this GRT puts an I/O net's
   guide on a layer outside the range it was given. Utilisation moves the *count* of failures
   (4 at 40%, 3 at 22%) but never removes them, and at 30% the router had completed 20% of its
   first iteration with **zero violations** before the port nets failed, so this is pin access,
   not congestion. The one lever that helped was fewer nets at the boundary (row 10). **What
   would clear it:** a current OpenROAD (the ORFS Docker image, or a source build — neither was
   available: Docker is not running on the Intel and a source build needs root), or a floorplan
   that gives the I/O pins a proper ring instead of bare die-edge slots.
   `pnr.tcl` already runs `extract_parasitics` and `write_spef` and re-reads the SPEF once routing
   closes.

   ✅ **Cleared Tue 27 Oct 2026 (Q129(a))**, by the first of those two: the ORFS container
   `openroad/orfs:26Q4-229-g64939f371`, whose ORFS checkout is the **same commit this flow pins**
   (`64939f371`), so the platform files are identical and only the tool moved. On aifoundry1 it
   routes **both** netlists to **zero DRC violations** in 193 s each, with no floorplan change and
   no I/O ring — row 10's configuration exactly. OpenRCX then extracts 251,162 (`mixed`) and
   273,581 (`keep`) coupling capacitors, the SPEF is written and read back, and an SDF annotated
   with the extracted parasitics exists for the glitch bench. Results, the per-net capacitance
   tables, the Miller-factor band and the revised Q128 waterfall:
   [`../2026-10-27-q129-routed-netlist/`](../2026-10-27-q129-routed-netlist/README.md). New flow
   scripts: `tools/open-flow/txfma/{route_docker.sh,pnr_route.tcl,post_route.tcl,spef_caps.py,reprice.py}`.
2. **No timed pass, so no glitch number — but the bench for it now exists and runs.** Three
   obstacles were cleared and one was not.
   - Icarus will not compile `tb_gate.sv`: core-et's `rtl/inc` headers use SystemVerilog `inside`
     expressions (`uc_types.vh:104`) and assertion properties (`shire_assert.vh:104`).
     *Cleared* by `tb_timed.v`, a plain Verilog-2001 bench that replays a recording of the unit's
     pins (`tb_gate.sv +vectors=<file>`, one line per time step) instead of rebuilding the
     stimulus from those headers. `-DET_ASSERT_OFF` also silences the properties.
   - Icarus refuses ASAP7's sequential models (`sorry: ifnone with an edge-sensitive path is not
     supported`, `asap7sc7p5t_SEQ_RVT_TT_220101.v:83`). *Cleared* by `asap7_seq_behav.v`, the two
     cells this netlist uses written behaviourally; the combinational models keep their `specify`
     blocks, which is where the SDF delays land.
   - Without `-gspecify` Icarus ignores every `specify` block, `$sdf_annotate` changes nothing and
     the timed run comes out byte-identical to the zero-delay one. *Cleared.*
   - **Not cleared:** with `-gspecify`, `$sdf_annotate` on this design aborts —
     `ERROR: NULL handle passed to vpi_scan` / `vvp: vpi_iter.cc:71: Assertion 0 failed`, in
     Icarus 14.0 devel (`s20260301-713-gf9111a949`), both with an explicit scope argument and
     without one. The zero-delay half of the same bench runs to the end and its counts are in
     `power/toggles_zero_iverilog.json` (9,388,830 pin transitions over 39,259 traced signals in
     the measured op, every cell pin counted separately, so comparable only against its own timed
     twin). **What would clear it:** a different simulator with SDF (Verilator has no delay model
     at all), or a smaller SDF — annotating one block rather than all 19,822 cells would show
     whether the abort is a size problem or a structural one.

   ✅ **Cleared Tue 27 Oct 2026 (Q129(b))**, and that slicing test answers its own question: the
   abort is **structural, not a size problem** — twenty `(INTERCONNECT ...)` entries abort exactly
   as 42,525 do, while all 16,480 cell blocks with none of them run to the end. Two further faults
   were found alongside it: `-gspecify` was not the only missing flag (`-ginterconnect` is needed,
   and Icarus says so itself before asserting), and **`$sdf_annotate(sdf)` with no scope argument
   annotates nothing at all**, because it resolves instance names in the calling module — so the
   timed figure this bench would have produced was never going to be right. With
   `$sdf_annotate(sdf, dut)` and the interconnect and `(COND ...)` entries removed, Icarus does
   annotate 37,732 cell paths and runs. The measurement itself was made with a small event-driven
   simulator written for it, validated by reproducing Icarus's own zero-delay VCD **exactly, net
   by net, on both netlists**. The glitch factor, the Icarus diagnosis in full and two SDF traps:
   [`../2026-10-27-q129-glitch/`](../2026-10-27-q129-glitch/README.md). New flow scripts:
   `tools/open-flow/txfma/{gsim.py,glitch.py}`.

The glitch ratio in the record — 1.5× the toggles and 1.4× the energy in the multiplier tree — no
longer rests on the tape-out flow alone, and it does **not** transfer: measured on this netlist the
tree's factor is **×2.39 in toggles and ×2.33 in energy**, while the **whole unit**'s is ×1.57 and
×1.33. The two flows' *timed* tree counts are 1.25× apart where their zero-delay counts were 1.98×
apart, so counting the glitches is what brings them together. Applying the measured factors to this
file's ledger takes a random multiply-add's bottom-up total from Q129(a)'s 1.810 to **2.598 pJ** and
the closure against the board from 31.3% to **44.9%** — the largest single step these open-flow
measurements have made. The **ladder above moves too**: both partners were re-run at h = 0, 1, 2,
4, 8 with the delays, and the fitted slope per designed flipped bit goes 35.10 → 44.85 fJ (`lq`,
×1.278) and 36.81 → 49.18 fJ (`lb`, ×1.336) on switching alone, so this file's *"the arithmetic
inside one lane's multiply-add is about 30% of what the board pays for a flipped operand bit on
switching alone, and about 40% once the cells' own internal energy is added"* becomes about
**38%** and about **55%**. The glitch factor is strongly activity-dependent — ×1.00 at `h0`, where
the clock is 97.6% of the energy and the clock does not glitch, rising to ×1.23 at `h8` and ×1.57
at `randn` — so no single factor can be applied to this table as a whole.

## What the first version got wrong

| Claim, as first published | Corrected |
| --- | --- |
| "the multiplier's 1,200.8 physical toggles … stand against the tape-out flow's 1,244 — 3.5% apart" | scope error: 1,244 is tree-only. Tree against tree is **628.2 vs 1,244, 1.98× apart** on the comparable netlist (716.3, 1.74×, on the hierarchy-kept one) |
| "35.4 fJ per flipped operand bit … E60 measured 116.7 fJ … about 30%" | three errors (denominator, partner, two-point). The fitted slope per designed bit is **38.5 fJ busy / 32.9 fJ quiet**, against E60's **129.9 / 116.7**: **30% / 28%** on switching alone, **42% / 40%** with the cells' internal energy. The arithmetic of the answer barely moved; every step to it was wrong |
| "1250 ps (800 MHz), 0.517 V" as the operating point | the design **misses** 1250 ps by **wns −1,219 ps**, so it would run near **400 MHz**; and the liberty is TT at 0.7 V while the energy is priced at the 0.517 V rail |
| "leaving them out makes this an underestimate" (coverage, by net count) | **49.5% of the capacitance, in farads, is unpriced**; `coverage.cap_fraction_priced` = 0.5046 is the share that IS priced (corrected 26 Oct, Q128(e) — this row first stated it the other way round) |
| `power.py`: internal energy is "a few per cent of a delivered bit" | OpenROAD's own `report_power` on this netlist: **internal is 55% of the dynamic power**. The liberty's internal term adds **28%** to `randn` for the combinational cells alone |
| "DRT-0255 … on a block pin", fix suggested: "a `-exclude` region for the pins" | the failing nets are named — `clock`, `trans_coefficients[51]`, `out_data_res[0/29]` — and ten configurations are tabulated above, including the two that showed matching the layer ranges does not help |
| the flow could not be re-run: no tile generator, no pinned versions | `mktiles.sh` is committed with the exact flags; `setup.sh` pins every tool and fetches each sha by name |
| per-block counts read off the hierarchy-kept netlist | the whole bench was re-run on the `mixed` netlist and both are reported; the census page now compares on `mixed`, where the multiplier is 1.11× the tape-out flow's cells rather than 1.77× |
| the ladder ran two rungs of one partner | h = 0, 1, 2, 4, 8 of **both** partners, on **both** netlists: 52 simulations, all committed |
