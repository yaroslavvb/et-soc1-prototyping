# The unpriced half of the open design's capacitance, priced (Q129)

27 October 2026, on aifoundry1 (desk compute only; no card was touched). Closes the first of the
three reasons [Q126(e)'s `POWER.md`](../2026-10-26-open-netlist/POWER.md) gives for its bottom-up
energy being a floor, and the matching leg of
[Q128 §5](../2026-10-27-matmul-to-transistor/README.md) item 4: *"49.5% of the open design's
capacitance (in farads) is unpriced — the 9,923 nets CTS and `repair_design` created after the
gate-level simulation."*

## The answer, first

**The unpriced half is worth 0.0880 pJ per random fp32 multiply-add** (switching), **0.101 pJ**
with the cells' own internal energy — not the "two to three times" `POWER.md` warned the figure
might be short by. The number the ledger *quotes* moves **+0.0802 pJ**, which is a different
quantity: correcting the join also takes **0.0078 pJ back out**, because the published number had
mis-priced it (§ [the arithmetic](#the-arithmetic-in-full-three-parts-not-two)).

🛑 **Every absolute on this page is priced on the global-route Steiner wire column**, which
[Q129(a)](../2026-10-27-q129-routed-netlist/README.md) measured ~20% **high** the same afternoon.
Every *ratio* here is unaffected by that; the absolutes are pending the per-net join named in
["Still a floor" item 1](#still-a-floor--four-things-this-does-not-fix).

| | published (Q126(e), Q128's ledger) | with every farad priced | change |
| --- | ---: | ---: | ---: |
| capacitance priced, in farads | 50.46% | **100%** (20,380 of 20,383 nets by direct simulation; 0.04% of farads) | |
| signal toggles / multiply-add | 3,623.36 | **3,795.58** | +4.8% |
| clock toggles / multiply-add | 476.60 | **476.60** | **unchanged** |
| switching pJ / multiply-add | 1.5159 | **1.5961** | **+0.0802 (+5.29%)** |
| + the cells' internal energy | 1.9465 | **2.0472** | **+0.1007 (+5.17%)** |
| clock's share of switching | 32.75% | **31.10%** | |

Against the board's 5.783 pJ for one random multiply-add over idle (E38/E39, three cards), and the
minion rail's 4.337 pJ at Q128's 0.75 rail ratio:

| | published | now |
| --- | ---: | ---: |
| accounted, bottom up | 1.9465 pJ | **2.0472 pJ** |
| unaccounted against the board | 3.8365 pJ | **3.7358 pJ** |
| unaccounted against the rail | 2.3908 pJ | **2.2901 pJ** |
| closure against the board | 33.66% | **35.40%** |
| closure against the rail | 44.88% | **47.20%** |

So 0.10 pJ of the 3.84 pJ gap moves from unaccounted to accounted: **2.6% of the gap**. This leg of
Q128 §5 item 4 is closed. Of the item's other two legs, "no timed pass, so no glitch factor"
stands; "no detailed route, so no SPEF and no coupling" was itself closed the same afternoon by
Q129(a) — which is where the 🛑 above comes from, and it moves the wire **down**.

## …and the gap was not what `POWER.md` said it was

`POWER.md`'s sentence, in full (`POWER.md`:232–237): *"The shortfall is not idle nets: every net
the simulation names and that the extractor knows is active here. It is the 9,923 nets CTS and
`repair_design` created after the netlist was simulated, **plus nets the simulator folded away**.
They switch, so leaving them out is an underestimate of the same order as the number itself."*
The folding clause is right — folded nets are part of the 414-net row below. The other four claims
are not:

1. *"the shortfall is not idle nets"* — **39.93% of the design's farads are idle nets the
   simulation already names** (8,888 nets, 18,806.0 fF). They read as "not in sim" only because
   `power.py:179` drops zero-activity nets after differencing the two SAIFs.
2. *"the 9,923 nets CTS and `repair_design` created"* — CTS and `repair_design` created **252**
   nets, 4.86% of the farads, and 236 of those were already priced.
3. *"they switch"* — **43.1 of the 49.5 percentage points carry no switching energy at all**
   (idle nets plus tied constants).
4. *"an underestimate of the same order as the number itself"* — it is **5.3%** (0.0802 of 1.5159).

Walking the pre-route netlist's own instance tree and the post-CTS netlist's structure:
**252 of the 20,383 extracted nets are what CTS and `repair_design` created** — 2,286.4 fF,
**4.86%** of the design's 47,093.2 fF, not 49.5% — and **236 of those (the clock tree, 1,837.5 fF)
were already priced**, by `power.py`'s own `clknet_<n>_<source>` name-strip rule, inside the
published 1.5159 pJ.

The 252 are **241 `clknet_*` nets** (CTS's tree, 1,899.7 fF) and **11 `net<n>` nets**
(`repair_design`'s buffers, 386.7 fF). The cell count moves 19,822 → 20,074, exactly +252, and
every added cell is a buffer: 190 `BUFx5` and 52 `BUFx2` (CTS's `-buf_list`) and 5 `BUFx24`,
4 `BUFx6f`, 1 `BUFx12f` (`repair_design`'s), with 20 clock inverters (`CKINVDC*`) swapped in on top.
Worth saying plainly, because it is the opposite of what "repair" sounds like: **on this design
`repair_design` is overwhelmingly a *downsize* pass** — 3,317 cells swapped **in** against 3,065
swapped **out** (a net gain of 252, not a reduction), and the traffic
runs `NOR2x1`→`NOR2xp33`, `XNOR2x2`→`XNOR2xp5`, `OAI21x1`→`OAI21xp33`, i.e. to *weaker* drives
(this netlist misses its 1250 ps SDC by 2×, so it has no slack to spend and plenty of drive to give
back). That is why the post-CTS netlist uses 100 cell types against the pre-route netlist's 37
while adding only 252 cells.

What the 9,923 nets and their 23,330.8 fF actually are, for `randn`:

| part | nets | fF | share of all farads | pJ / multiply-add it was worth |
| --- | ---: | ---: | ---: | ---: |
| named by the simulation, **zero** activity in the measured window | 8,888 | 18,806.0 | 39.93% | 0 |
| **constants** — driven by `TIELOx1`/`TIEHIx1`; one net carries 1,131 fF, the zero rail of stage f1's Wallace tree | 23 | 1,498.3 | 3.18% | 0 |
| the simulator's **bit renumbering** — Verilator renumbers a vector whose declared LSB is not 0 from 0 in its SAIF, so the extractor's `bus[32]` and the SAIF's `bus[0]` are one wire. The same renumbering made the published join price the **wrong** bit on those vectors' *overlapping* indices: [§ A second published error](#a-second-published-error-the-join-priced-the-wrong-bit-on-the-renumbered-buses) | 598 | 1,875.9 | 3.98% | **0.0857** |
| resolved from **the driver's input** — CTS's and `repair_design`'s own new nets, plus pre-route nets the simulator folded, each driven by a one-input cell (BUF/INV/CKINVDC), so at zero delay it toggles exactly as its input | 414 | 1,150.6 | 2.44% | **0.0022** |
| **total unpriced** | **9,923** | **23,330.8** | **49.54%** | **0.0880** |

**43.1 of the 49.5 percentage points carry no switching energy at all**: those nets do not toggle
in the window, and pricing them at zero is an answer, not a gap. The only thing they can still owe
is glitching, which this flow cannot measure, and leakage, which is not switching energy.

The field `coverage.cap_fraction_priced` counts a net as "not in sim" when its *differenced*
activity is zero, so it has always read low for a reason that is not a shortfall. The honest
version of that line is the table above.

## The stronger answer: simulate the netlist the capacitance table describes

The netlist OpenROAD writes after CTS and `repair_design` is **flat**, so its net names *are* the
extractor's names and the join needs no mapping at all. The same bench (`tb_gate.sv`), the same 13
operand files from `mktiles.sh`, the same Verilator 5.053 build, the published `power.py` unchanged,
and the repo's own committed capacitance table
([`net_cap_globalroute.txt.gz`](../2026-10-26-open-netlist/net_cap_globalroute.txt.gz), md5 of the
decompressed file `39815801324ebf2105be8825ba25c03b`) — driven into `txfma_pnr.v` instead of
`txfma_keep.v`:

- **20,380 of 20,383 extracted nets are named by the simulation.** The three that are not carry
  20.2 fF, 0.04% of the farads: 1-bit vectors (`...[0]`) that Verilator traces as scalars.
- the bench's own counters are identical to the pre-route run's, pattern by pattern (`randn`
  17,349 flipped bus bits, 547 cycles, 519 clock-on, 512 valid lane-cycles), so the post-CTS
  netlist is doing the same arithmetic on the same stimulus.
- `randn`: signal 3,795.58 toggles/multiply-add → **1.0997 pJ**; clock 476.60 → **0.4964 pJ**;
  **1.5961 pJ** switching, **2.0472 pJ** with the cells' internal energy.

**And the two routes agree net by net.** On every one of the 9,923 nets the published join left
unpriced, the activity the structural rules infer from the *pre-route* SAIF equals the activity the
post-CTS simulation measures **exactly** — 9,923 of 9,923 for `randn`, zero disagreement, and the
same for all 13 patterns (20,286 nets checked at `zeros`, 17,339 at `lb_h8`, …). The mapping is
right, and it is right for a reason: a buffer's output carries its input's toggle count, and a
vector's bits are the same wires under either numbering.

## A second published error: the join priced the wrong bit on the renumbered buses

The structural route's total for `randn` is 1.6038 pJ against the re-simulation's 1.5961. That
−0.0077 pJ sits on the 384 nets (of 10,224) that the two SAIFs **both** name and disagree about,
−20.01 toggles/multiply-add.

🛑 **Corrected here, 27 Oct 2026.** This page first called that residual "the scatter between two
simulations of logically identical netlists". It is not scatter. It is a **second error in the
published join**, on the *same* renumbered vectors whose high bits it was already missing:

- **362 of the 384 disagreeing nets** (−0.00748 pJ, **96.6%** of the residual) sit on **14 vector
  bases whose declared LSB is not 0** — 13 of them the very vectors in the `bitshift` row above.
- A vector declared `[63:12]` is named `bus[12]…bus[63]` by the extractor and `bus[0]…bus[51]` by
  Verilator. `bus[52]…bus[63]` have no SAIF name at all — that is the `bitshift` row, 598 nets
  never priced. But `bus[12]…bus[51]` **exist in both namespaces and mean different physical
  bits**, so `power.py` matched them by name and charged each wire the activity of the bit 12
  places up.
- The shift *predicts* the published value: for **349 of the 362**, the pre-route SAIF's value for
  `bus[i]` is bit-identical to the post-CTS value for `bus[i + lsb]`. The other 13 are the same
  two vectors, off by a few toggles.
- The signature is systematic, not noise. `zeros` disagrees by **exactly 0.0**; `ones` by
  −0.0002 pJ; and it grows with datapath activity on those vectors to −0.0229 pJ at `lq_h8`. It
  can run either way — `lb_h4` is **+0.0009 pJ** — which is what pricing the *wrong* bit does.
  **Across all 13 patterns nothing is left over**: the mis-join is 100% of the residual in twelve
  of them, and 96.6% at `randn` (`crosscheck/misjoin_per_pattern.json`, `code/misjoin.py`).
- The one exception, and it is not scatter either: at `randn` a further **−0.00026 pJ** is
  `txfmaexp0_top/txfma0_e2/_205_[0]`, 3.84 fF, 260 toggles. It is one of the **three** extracted
  nets the post-CTS run does not name (1-bit vectors Verilator traces as scalars), so the
  re-simulation prices it at zero where the published join had it right.

**Consequence for the cross-check.** The structural route reuses the pre-route SAIF for the nets
the published join already matched, so it inherits the same mis-join. It is therefore **not** an
independent check on the *total* — only on the 9,923 nets it infers, where it is exact.

## The arithmetic in full: three parts, not two

| | pJ / multiply-add |
| --- | ---: |
| the 9,923 nets the published join left unpriced, **priced** | **+0.0880** |
| the mis-join corrected: 362 overlapping indices of 14 renumbered vectors | **−0.0075** |
| one 1-bit vector the post-CTS run cannot name (`_205_[0]`) | **−0.0003** |
| published 1.5159 → complete **1.5961** | **+0.0802** |

**The unpriced half is worth 0.0880 pJ.** The post-CTS simulation reproduces the toggle count of
**every one of the 9,923 nets exactly**, so the two routes' totals for that half are identical by
construction — the strength of the cross-check is the per-net equality, not a second independent
measurement of the sum. The **+0.0802** the quoted number moves is that 0.0880 less the two
corrections above, and **0.0000 of it is simulator noise**.

## Which part is data-dependent and which is clocking

The waterfall is random over idle, so the split matters.

- **The whole correction is signal.** +0.0802 pJ on the signal nets, **+0.0000 pJ on the clock**:
  the clock tree was already complete in the published figure, because `power.py`'s `clknet_` rule
  reached all 236 of CTS's clock nets. Nothing in this directory changes the clock-tree arithmetic.
- `randn`'s 1.5961 pJ of switching is **signal 1.0997 pJ (68.9%) + clock 0.4964 pJ (31.1%)**.
- `randn` **over the `zeros` rung** — the shape the board figure has — is **1.3788 pJ**: of it
  **1.0997 pJ (79.8%) is data switching** and **0.2791 pJ (20.2%) is the 13 gated clock subtrees
  waking up**. The `zeros` rung itself, 0.2173 pJ, is the ungated root of this lane's clock tree,
  which on a card is already inside the idle the board measurement subtracts — `POWER.md`'s own
  caution, and the complete table does not move it (`zeros` is 0.2173 pJ before and after).

**The gating the RTL has**, since the task asks it stated: **13 `et_clk_gate` instances**, each a
`DLLx1` latch plus its AND, all of them in the fraction block, making 13 gated clocks —
`ctrl_f0…ctrl_f5_clk`, `ctrl_frf_clk`, `multype_f0_clk`, `multype_f1_clk`, `opa_frf_clk`,
`opb_frf_clk`, `opc_frf_clk`, `trans_frf_clk`. The exponent and control blocks' flops hang off the
ungated root. The clock regex matches **242 nets** in the table — **241 that CTS created**
(`clknet_*`) plus the pre-existing top-level `clock` root — and they split **95 on the ungated root
(802.1 fF, always toggling)** and **147 on the 13 gated branches (1,106.3 fF, of which 1,044.1 fF
toggles when the lane has valid data)**; 2,084 flop and latch clock pins sit on 200 distinct CLK
nets.

With every operand word zero the 13 gates stay shut and 802.1 of 1,846.2 fF of toggling clock
capacitance survives. That is a **56.6% capacitance-weighted** drop — and it is **not a new
measurement**: `POWER.md`'s "57%" is the same 1,846 → 802 fF ratio, and because the complete table
added nothing at all to the clock (the `clknet_` rule had already reached all 236 of CTS's clock
nets), the figure **stands exactly as published**. Named alongside its denominator, the same shut
measured three ways is **56.6% of the toggling clock capacitance, 56.2% of the clock energy
(0.4964 → 0.2173 pJ) and 59.6% of the clock toggles (476.6 → 192.6 per multiply-add)**.

## The Hamming ladder, refit on the complete capacitance

Same method as [`ladder.py`](../../../../tools/open-flow/txfma/ladder.py) and as E60's own reducer:
a line over h ≥ 1 with a free intercept, against the *designed* flip count.

| | published switching | complete switching | published + internal | complete + internal | E60 at the board | complete, switching / with internal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lq` per designed bit (A = 1.0) | 32.87 fJ | **36.18 fJ** | 46.27 fJ | **50.41 fJ** | 116.746 ± 0.613 fJ | **31.0% / 43.2%** |
| `lb` per designed bit (A = π) | 38.49 fJ | **40.78 fJ** | 54.86 fJ | **57.61 fJ** | 129.918 ± 0.480 fJ | **31.4% / 44.3%** |

So the per-designed-bit closure against E60 moves from 28% / 30% on switching alone to **31% / 31%**,
and from 40% / 42% with the cells' internal energy to **43% / 44%**. Every rung of both ladders is
in `power-postcts/`, and the per-pattern before/after is in the summary JSON.

Per pattern, switching pJ per multiply-add, published → complete:

| pattern | published | complete | | pattern | published | complete |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| `randn` | 1.5159 | **1.5961** (+5.29%) | | `lq_h0` | 0.5083 | **0.5089** (+0.10%) |
| `zeros` | 0.2173 | **0.2173** (+0.00%) | | `lq_h1` | 0.5704 | **0.5773** (+1.22%) |
| `ones` | 0.5069 | **0.5071** (+0.05%) | | `lq_h2` | 0.6046 | **0.6146** (+1.65%) |
| `lb_h0` | 0.5088 | **0.5094** (+0.12%) | | `lq_h4` | 0.6891 | **0.7077** (+2.70%) |
| `lb_h1` | 0.6869 | **0.7160** (+4.24%) | | `lq_h8` | 0.7998 | **0.8298** (+3.74%) |
| `lb_h2` | 0.7369 | **0.7659** (+3.94%) | | | | |
| `lb_h4` | 0.7897 | **0.8155** (+3.27%) | | | | |
| `lb_h8` | 0.9618 | **1.0066** (+4.66%) | | | | |

The correction is largest where the data moves most, and vanishes at `zeros`, which is what the
decomposition above predicts: the unpriced farads were mostly idle nets, and what was genuinely
missing was datapath activity on buses the join could not name.

## Still a floor — four things this does not fix

1. **Every wire capacitance here is the global-route Steiner estimate.**
   🛑 **Amended the same afternoon, 27 Oct 2026, by [Q129(a)](../2026-10-27-q129-routed-netlist/README.md).**
   This row first said "so the wire half of each net remains a lower bound", repeating the published
   pages. That is wrong, and Q129(a) measured it: detailed routing closes in a current OpenROAD,
   OpenRCX extracts the coupling, and the extracted wire capacitance at Miller k = 1 is **0.812 ×**
   the Steiner estimate — the estimator's 0.1658 fF/µm already has the neighbour coupling bundled in
   and grounded, so the estimate runs **20% high**, not low.

   🛑 **Corrected here, 27 Oct 2026: that 0.812 does not transport to this page.** This row first
   said Q129(a) measured it "on this same hierarchy-kept netlist". It is the same *synthesis*, but
   **a different place-and-route**: Q129(a)'s run has 20,570 extracted nets against this table's
   20,383, 350 clock nets against 242, **+10.5% pin capacitance and −7.6% Steiner wire**
   (15,532.8 fF against 16,801.7 fF). 0.812 is extracted ÷ **its own** Steiner column, and Q129(a)
   says as much itself ("this run's own Steiner estimate is lower than the published one").
   Three defensible scalars, none of them the right one:

   | wire scale | what it is | complete `randn` | the correction |
   | ---: | --- | ---: | ---: |
   | **0.812** | Q129(a)'s extracted ÷ its own Steiner, by capacitance | 1.478 pJ | 0.0789 pJ |
   | 0.768 | Q129(a)'s own within-run wire **energy** ratio on `keep` (0.4238 → 0.3252 pJ) | 1.451 pJ | 0.0767 pJ |
   | **0.750** | Q129(a)'s extracted wire (12,605.2 fF) ÷ **this** table's Steiner column | 1.440 pJ | 0.0759 pJ |

   54.8% of the 0.0880 pJ correction is wire capacitance, computed from the per-net wire column, so
   **the honest statement is a range: complete `randn` switching 1.44 – 1.48 pJ and the correction
   0.076 – 0.079 pJ**, not the single 1.4783 pJ this row first gave — which does not reproduce
   either: the per-net wire column is 39.135% of complete `randn` switching, which gives 1.4786 pJ
   at a 0.812 scale, not 1.4783. Q129(a)'s `reprice-keep/` holds
   the proper re-pricing at k = 0 / 1 / 2, and the clean number is this directory's complete activity
   on **Q129(a)'s own per-net extracted table** — one `power.py` invocation once both files sit in
   one tree, and run by neither agent. Nothing above changes in *ratio* (the clock share, the
   ladder's slope, the decomposition of the unpriced half), because the scale applies to both sides
   of every comparison.
2. **No timed pass, so no glitches.** Icarus's `$sdf_annotate` aborts on this design; the tape-out
   flow's 1.5× toggles / 1.4× energy in the multiplier tree is still the only measurement.
3. **The cells' internal energy is still signal-only.** Q126(d)'s census-weighted figure
   (0.1188 fJ per transition at 0.517 V) is applied to combinational output transitions; the
   clock-pin energy of this netlist's 2,071 flip-flops, 13 latches and CTS's 242 inserted buffers
   (190 `BUFx5` + 52 `BUFx2` — a coincidence with the 242 clock nets above) is in
   neither the published number nor the one above. Priced at that same figure it is **+0.0566 pJ
   per multiply-add**, which would take accounted to **2.1038 pJ** and closure against the board to
   **36.4%**. It is recorded in the summary JSON as a *labelled sensitivity, not a measurement*,
   because CTS's buffers (`BUFx2`, `BUFx5`) are larger than the mix it borrows. (A second, smaller
   caveat on that figure, noted here because this directory leans on it: the mix was taken on the
   **flat** netlist — its own census is 14,119 combinational + 1,953 flip-flops + 13 latches + 2 tie
   cells = 16,087 — while the netlist priced here is the hierarchy-kept one, 19,822 cells with 2,071
   flip-flops.)
4. **One lane's arithmetic.** The register-file read ports, the operand bus, the result path, the
   pipeline registers and leakage are outside this netlist and outside this directory.

## What ran, where, and what was reused

| Step | Where |
| --- | --- |
| Q126(e)'s flow tree (OpenROAD outputs, SAIFs, pinned oss-cad-suite, ORFS asap7 platform, core-et) | preserved on aifoundry2 from 26 Oct; copied to aifoundry1 over the lab LAN |
| the published `power.py` re-run on the preserved pre-route SAIFs | aifoundry1, `nice -n 19` |
| Verilator build of the **post-CTS** netlist and 26 runs (13 patterns × ops 0/1) | aifoundry1, `nice -n 19`, `-j 4` |
| the structural resolution and the cross-check | the desk Mac |
| any card | **none** — no claim, no card lock, no governor |

**`pnr.tcl` was not re-run.** The preserved Q126(e) tree was used instead, and the check that it is
the tree the published numbers came from is that re-running the published `power.py` on its
`randn` SAIF pair reproduces
[`power_gr_randn.json`](../2026-10-26-open-netlist/power/power_gr_randn.json) **bit for bit** —
coverage, totals, energy, clock share, the per-multiply-add block and the internal estimate all
identical (`structural/q129_syn_randn.json`'s `baseline_power_py` block carries the same figures,
computed independently). Every pattern's baseline in `structural/` likewise reproduces its row in
`POWER.md`'s own table.

### Departures from the plan, dated 27 Oct 2026

- **`pnr.tcl` not re-run** (the task allowed either route); the preserved outputs were used, with
  the bit-for-bit reproduction above as the check.
- **`code/resim_postcts.sh` is not `gatesim.sh`.** It builds the Verilator model **once** into a
  shared `obj_dir` and runs every pattern against it, where `gatesim.sh` rebuilds per `TAG`, and it
  passes `-j 4` instead of `-j 8` because the same box carried another agent's flow at the time.
  Every other Verilator flag, the cell models, the sequential stand-in and the bench are
  `gatesim.sh`'s own.
- **E60's reducer was not re-run.** The board figures in the ladder table are quoted from the
  committed `2026-10-20-bitflip-ladder/reduce.txt` by way of
  [`transistor-ledger.json`](../2026-10-27-transistor-ledger/transistor-ledger.json).
- Absolute paths in the committed `power-postcts/*.json` are rewritten to `$SCRATCH/…`; nothing
  else in those files is touched.

## Files

| File | What |
| --- | --- |
| `q129-unpriced-capacitance.json` | the summary: the decomposition, every pattern before and after, the two routes' agreement, the ladder refit, the waterfall, the clock-buffer sensitivity |
| `power-postcts/power_pnr_<pattern>.json` | the published `power.py`, unchanged, on the **post-CTS** netlist's own SAIFs against the committed capacitance table. 13 patterns |
| `structural/q129_syn_<pattern>.json` | the structural route: every extracted net resolved to a labelled activity from the **pre-route** SAIF, with `baseline_power_py` reproducing the published join |
| `structural/q129_syn_randn-nets.json.gz` | per net, for `randn`: capacitance, toggles, which rule resolved it, and whether CTS or `repair_design` created it |
| `crosscheck/cmp_<pattern>.json` | inferred against directly simulated, net by net, and the residual between the two routes on the nets both name |
| `crosscheck/misjoin_per_pattern.json` | that residual decomposed, all 13 patterns: the published join's mis-join on the renumbered vectors, the one net the post-CTS run cannot name, and what is left (nothing) |
| `crosscheck/misjoin_randn-nets.json` | the 384 disagreeing nets at `randn`, each with its declared LSB, both toggle counts, the shift-predicted bit and its count |
| `netlist/txfma_pnr_keep.v.gz` | the post-CTS, post-`repair_design` netlist OpenROAD wrote — the one the capacitance table describes (20,074 cells, 100 cell types against the pre-route netlist's 37: `repair_design` resized as well as buffered) |
| `netlist/txfma_syn_keep.v.gz` | the pre-route hierarchical netlist, which is where the alias classes and the vectors' declared LSBs come from |
| `code/nlparse.py` | the flat post-CTS netlist: wires, ports, instances, connections, and so each net's driver |
| `code/hierparse.py` | the hierarchical netlist: alias classes of one physical net, every net's flat name, and the declared LSB of every vector |
| `code/price_q129.py` | resolves every extracted net to a labelled activity and prices it at ½CV² per toggle, 0.517 V |
| `code/cmp_map.py` | the cross-check against the post-CTS simulation |
| `code/misjoin.py` | classifies every disagreeing net by the shift its vector's declared LSB predicts — the test that the residual is a mis-join and not simulator scatter |
| `code/saif_reduce.py` | a SAIF pair → a compact `{net: toggles}`, using `power.py`'s own reader |
| `code/resim_postcts.sh` | the re-simulation (see the departure above) |
| `code/structure.py` | the cell-count delta, the nets place-and-route created, and the clock tree split into the ungated root and the 13 gated branches |
| `code/summarise.py` | builds `q129-unpriced-capacitance.json` |

```bash
# the structural route, from the two netlists and a reduced SAIF pair
python3 code/saif_reduce.py <dir with power.py> randn_o1.saif randn_o0.saif 'tb/lane[0]/txfma' syn_randn.json.gz
python3 code/price_q129.py --netcap net_cap_globalroute.txt \
    --pnr-netlist txfma_pnr_keep.v --syn-netlist txfma_syn_keep.v \
    --toggles syn_randn.json.gz --pattern randn \
    --cell-energies ../2026-10-26-asap7-cell-energies/asap7-cell-energies.json \
    --out q129_syn_randn.json

# the stronger route: simulate the netlist the capacitance table describes, then price it unchanged
NET=$SCRATCH/work/pnr/txfma_pnr.v bash code/resim_postcts.sh
python3 tools/open-flow/txfma/power.py --saif pnrsim/randn_o1.saif --saif-base pnrsim/randn_o0.saif \
    --netcap $SCRATCH/work/pnr/net_cap_globalroute.txt --muladds 512 \
    --cell-energies ../2026-10-26-asap7-cell-energies/asap7-cell-energies.json \
    --out power_pnr_randn.json

# why the two routes' TOTALS differ: the published join's mis-join on the renumbered vectors
python3 code/misjoin.py <the working root with in/ and in/red/> <outdir>
```
