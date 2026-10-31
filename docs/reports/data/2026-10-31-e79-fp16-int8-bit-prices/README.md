# E79 — the fp16 and int8 single-bit price lists (Q130, aifoundry3, 2026-10-31)

*Pre-registered in [`tools/claims-v3/hlp/README.md`](../../../../tools/claims-v3/hlp/README.md) with
[`predictions.json`](../../../../tools/claims-v3/hlp/predictions.json), committed as **`2a72d352`** at
**09:24:58 PDT — 1 min 56 s before the card was claimed** (09:26:54 PDT, from the Discord message's own
snowflake, id `1566126330142007489`) **and 3 min 24 s before the first measured launch** (09:28:22 PDT, pass
7910's `block_begin`). Amendments A1–A3 as `e66f7c1a` (09:31:52) and `270d2108` (09:32:31) during pass 7910; A4 as
`4216f1fb` at 09:49:45 PDT, during pass 7912 with 7910 and 7911 complete, 12 min 41 s before block B's first
launch; A5–A8 as `23197287` (10:13:39). Card runs 2026-10-31 **09:27:05–10:33:06 PDT** (the identity read, the
smoke at 09:27:38, then ten passes to the end of 7915), on **aifoundry3 card 0 only**, whose governor is latched
at 600 MHz by its boot-time TDP of 0, so every number here is a 600 MHz, 521.9 mV number — the same card, clock
and voltage as E65's fp32 B-side scan and E67's A-side scan, which is the point. Claimed in `#community-lab` at
09:26:54 PDT and released at 10:34:48 PDT by an edit of the same post. **One read-only probe opened the card's
management device before the registration and the claim, at 09:12:21 PDT** (departure D2, below).*

*__Corrected the same day after an adversarial verification__ ([§ Corrections](#corrections-after-verification-sat-31-oct-2026)).
The rule tally is **12 passed (two of them vacuous) / 8 failed / 5 not scored**, not the 15 / 10 / 0 first reported.
The first scorer moved four int8 verdicts at E71's leakage slope, and the int8 B balanced list does not survive
that slope. Results 3, 5 and 6 and the significand-width reading are restated to what was measured. A pre-claim
device probe and three smaller departures are now disclosed. No price, interval or pass changed: the corrections
are in the scorer, the text and two record files. The first version is `8d2fe956`.*

## Why it ran

The Horace hub's Status item 9 is "**fp16 and int8**". E65 priced all 32 bit positions of an **fp32 B** operand
(83–1,008 fJ per flipped bit) and E67 all 32 of **A** (153–1,440 fJ), on this card. The blog's claim — that the
*kind* of number you multiply sets the power — had nothing to say about the two formats a real inference workload
uses. This runs the same Hamming ladder on **fp16** (`TensorFMA16A32`) and **int8** (`TensorIMA8A32`), both
operand sides, every bit position, with the zeros and constant-operand anchors, a 2-bit and a 4-bit additivity
rung per format against E70's law, a layout control, and an **fp32 tie** at E65's dearest position so the port
can be checked against a published number on the same silicon.

## Results

Card aifoundry3 card 0, 546 / 546 / 318 cycles per fp32 / fp16 / int8 multiply-add, 600 MHz, 521.9 mV, TDP 0.
Passes kept [7910, 7911, 7913, 7915, 7920, 7921, 7922, 7923]; runs kept 348 of 480; leakage slope 0.0834 W/°C.
**Of the 25 scored rules, 12 passed (two of them, P3b and P3b_kg, vacuously), 8 failed and 5 were not scored**
(`scored.json` `tally`). Of the 22 rules registered before any data, 11 passed, 6 failed and 5 were not scored.
The five not scored are int8's P4, its three P5 rules and its P6. Each rests on two passes or divides by a price
whose interval contains zero, so the registered resolution rule takes it out of the tally. Every failure is in the
scored table below. **At E71's slope no verdict moves** (`tally_leak0.3803`: 12 / 8 / 5), but the int8 B `kg`
list does not survive that slope (Result 4).

Ten passes ran. **The registered drift gate set two aside**: 7912 (`anchor_pi` drift 0.411 W) and 7914
(0.527 W), against the 0.3 W bar. Each had **zero** failed runs, and **no single run failed any gate** in the whole
experiment. A3 had registered 7914 and 7915 as passes five and six, but the queue was started for four
(`go 7910 4`, 09:28:21). A8 ran the two after 7912 dropped out, and only 7915 survived. So the fp16 and int8 full
lists rest on **four** kept passes, and the order probe's shared items on up to eight. Nothing was reinstated, and
no pass was chosen after the fact.

**1. fp16's ten mantissa bits cost what fp32's top ten cost, and its exponent is cheap in this construction.** A
flipped bit of an fp16 **B** operand costs **205 fJ** [204, 206] at mantissa bit 0 and **494 fJ [465, 523]** at
mantissa bit 9. The price rises monotonically (Spearman ρ = 1.000, P1a PASS). On the **A** side it runs from 355 to
**620 fJ** [573, 667] at bit 9 (ρ = 0.855, P1a_A PASS).

In watts, the step at fp16 bit *j* is **0.89–1.06 of E65's step at fp32 bit *j* + 13** at all ten positions (mean
0.97). That is the same position counted down from the top of the significand. The same-session tie gives
0.94 ± 0.07 for bit 9 over bit 22, paired per pass. So fp16's whole mantissa sits in the rising part of fp32's list
and none of it in fp32's flat low-mantissa floor, as P1c predicted: bit 5's interval lies wholly above bit 0's
(PASS).

The five exponent bits cost 64–83 fJ and the sign bit 34 fJ [−22, 90], which is a bound. That is **cheaper than
every mantissa bit**, the opposite of fp32's order: there the exponent (174 fJ mean) sat *above* the flat 109 fJ
floor. But 1b says why that is only half a result.

What **fails** is the registered *span*: 2.41× end to end, against the ≥ 3.0 registered (P1b FAIL). That follows
from the alignment above: E65's top ten positions span only 2.60× (387 → 1,008 fJ). Its 9.2× span ran down into a
floor that fp16 does not have.

**1b. Why the cheap exponent is only half a result.** Every number in Result 1 comes from the `jg` construction,
which Result 5 shows is a composite at the position where it was tested. One mechanism would make an exponent flip
cheap *in that construction specifically*. With A = 1.0 the product is B, so flipping one exponent bit leaves the
two C accumulators a lane alternates between related by a **power of two**. They then share their mantissa bits
and the result bus barely swings, whereas a mantissa flip makes them differ in many low bits. The balanced layouts
were run only at the dearest *mantissa* position, so **this experiment cannot separate the two**. The exponent and
sign prices are reported as `jg` all-in numbers. A balanced-layout exponent scan is left open, and it is the
cheapest follow-up E79 names.

**2. The port reproduces E65 on the same silicon, and the width test passes without testing width.** The fp32 tie
`b32_22` reads **1052 fJ [984, 1120]**, against E65's published **1,008 ± 21 fJ** (SE) at the same position, card,
clock and voltage (P7 PASS).

The registered width tests pass as registered:
- fp16's dearest B bit is 0.470 of the tie (P2b, band [0.25, 0.80]) and 0.49 of E65's 1,008 fJ (P2b_e65);
- its dearest A bit is 0.431 of E67's 1,440 fJ (P2a).

**They do not test the significand-width model.** A per-bit ratio is the designed-count ratio times the watt ratio.
fp16 counts 8,192 B flips per multiply-add to fp32's 4,096, because two fp16 elements ride in each 32-bit word. So
0.470 = 0.5 × 0.94. The width model (11/24 per element) predicts a watt ratio of 0.917. "The same watts for the
same relative-significance flip of a word" predicts 1.0. The measured 0.94 ± 0.07 (paired, same session) and 0.97
(against E65, across ten positions) sit between the two and do not separate them.

The minion-rail arm, kept beside the board arm, reads 0.50–1.19 of it over the 52 resolved items. Over the 31
steps of 1 W or more it reads **0.754–0.987** (median 0.81; pooled 0.808), against Q129's measured rail ratio
0.825 [0.787, 0.856].

**3. int8 has four times the multipliers a cycle, and the card's power found the structure.** int8's registered
B-side `jg` ladder does not alternate. Its eight rungs read **−0.119 to +0.078 W** above their zero (bit 6:
0.012 W), where the identical construction reads 4.536 W in fp16 and 4.830 W in fp32.

The public RTL (`core-et@b38a1a3`, openhwfoundation/core-et) says why:
- `VPU_NUM_TIMA 2` integer tensor units a lane (`rtl/inc/vpu_defines.vh:210`, instantiated at `vpu_lane.v:408`);
- each with `TIMA_INT8_MUL_NUM 4` int8 multipliers on one 32-bit operand (`rtl/inc/tima_defines.vh:8`,
  `tima/tima_top.v` `F2_PROD`);
- so **8 lanes × 2 units × 4 multipliers = 64 int8 multiply-adds a cycle**;
- the float path has one unit a lane, whose B column selector is a single bit (`vpu_tensorfma.v:282`): 16 fp16
  or 8 fp32 MACs a cycle.

A 16×16×64 int8 op (16,384 MACs) is 256 cycles of work and 318 in all. A 16×16×32 fp16 op (8,192 MACs) or a
16×16×16 fp32 op (4,096 MACs) is 512 and 546. **Per op int8 is 546 / 318 = 1.72× as fast as fp16; per
multiply-add it is 3.43×** (`tools/claims-v3/hpl/surface_hpl.py` `OPS` 32,768 against 16,384 per op, `CYC` 318
against 546). The 4× of the raw multiplier count comes down to 3.43× because int8's fixed overhead is larger: 62
cycles against 34. This experiment does not explain that 28-cycle difference.

Because both column halves issue in the same cycle in int8, a (lane, unit) pair always drives the same C column.
So a flip on the column-half boundary never alternates in time. The `kg` layout, which carries the flip on the
line-group parity instead, does alternate (amendments A4 and A6).

**4. The int8 price lists: the A side resolves, and the B side does not survive the leakage slope.** Per flipped
**A** bit (B = 1, all-in against a constant partner), the seven magnitude positions cost **71–92 fJ** (mean 82)
and the two's-complement MSB **152 fJ [147, 157]**: 1.85× the magnitude mean. There is no rise across the magnitude
bits (P3a_A FAIL).

Those prices count one A element read per lane: 8,192 per multiply-add. In int8 one A read feeds both TIMA units of
a lane: `vpu_lane.v:435` passes the shared `tena_rd_data`, against the per-unit `tenb_rd_addr` at `:438`. The B
`kg` count is per unit: 1,024 = 16 line-group transitions × 8 lanes × 2 units × 4 elements. On that per-unit
footing every int8 A price halves: the MSB to **76 fJ** [74, 79], the magnitude bits to 36–46 fJ.

**The dear MSB is an A-side, all-in observation, and its mechanism is open.** The bit's weight cannot be the
reason, since the bits of weight 1 to 64 cost the same. Sign handling in the multiplier (a sign-extension or
correction term) is a hypothesis this experiment did not test.

On the **B** side, the `kg` layout reads 27 fJ [15, 40] at bit 0 up to **86 fJ [56, 116]** at bit 5 at the
fitted slope, with bit 7 a bound (17 [−146, 180]). Its whole step is about 0.1 W and it has four passes. **At E71's
slope every one of its eight positions becomes a bound**: bit 6 goes from 49 [27, 71] to 2 [−188, 192] (see the
per-list summary under the sensitivity table). So **the int8 B level is not established**, and neither is the
"balanced int8 49 fJ" of the first version.

The registered int8 B rules on the `jg` list, which measures nothing:
- P3a FAILs over seven bounds;
- P3b PASSes vacuously;
- P8 reads **0.0023** and FAILs, its numerator a bound.

The A4 re-scores on `kg` give P3a_kg FAIL (0.50), P8_kg FAIL (**0.081**) and P3b_kg PASS, vacuously.

**4b. A pattern in the int8 B list that is not established.** At the fitted slope its magnitude positions
alternate. The odd ones (1, 3, 5) average **73 fJ** and the even ones (0, 2, 4, 6) **37 fJ**, a ratio of 1.98, and
bit 3's interval [64, 81] is disjoint from both neighbours'. That is the shape a radix-4 Booth recoder would give:
its digits cover (b1,b0,b−1), (b3,b2,b1), (b5,b4,b3), (b7,b6,b5), so an odd-indexed bit enters two digits and an
even-indexed bit one.

It is **not established**, for four reasons:
- the list has four passes and a 0.1 W step;
- no such alternation appears in the fp16 B list (205, 224, 255, 295, 321, 334, 373, 386, 431, 494 fJ);
- none appears in the int8 A list either, though a recoder on the same operand should show it;
- **at E71's slope the pattern vanishes** (odd 19 fJ, even 22 fJ, ratio 0.85).

A follow-up should re-measure these positions with more passes and a leakage model fixed in advance.

**5. Most of a single-bit price measured this way is not the flip — at the two positions where that was tested.**
The same single-bit flip was run in three layouts, at one B position per float format (fp32 bit 22, fp16 bit 9)
and at int8 B bit 6:
- `jg` is E65's and E67's construction. The flip sits on the column-half boundary, so the two C accumulators a
  lane alternates between accumulate *different* products and diverge.
- `jgp` flips the same bit at 97% of the same rate, but swaps the halves with the line-group parity.
- `kg` carries the flip on the line-group parity alone, at 1/31 of the rate.

In `jgp` and `kg` every column sees the same mix.

| format | `jg` fJ/bit [95%] | `jgp` fJ/bit [95%] | `kg` fJ/bit [95%] | `jg` / `jgp` per bit | `jgp` / `jg` ΔW |
|---|---|---|---|---|---|
| fp32 (bit 22) | 1052 [984, 1120] | 150 [142, 159] | 159 [−328, 645] (bound) | **7.0×** | 0.136 ± 0.012 |
| fp16 (bit 9) | 494 [465, 523] | 88 [58, 117] | 134 [−75, 342] (bound) | **5.6×** | 0.175 ± 0.060 |
| int8 (bit 6) | 0 [−2, 3] (bound; does not alternate) | 44 [20, 68] at the 1,024 count A4/A6 imply (3 at the generic 15,872); a bound at E71's slope | 49 [27, 71]; a bound at E71's slope | — | — |

What the order probe establishes:

- **(a)** At those two positions the `jg` step per flipped bit is **7.0× (fp32) and 5.6× (fp16) the `jgp`
  step**. The order-free watt ratios say the same.
- **(b)** `kg` resolves neither price: both are bounds. They exclude `jg`'s per-bit price at 95% (`kg` is at most
  0.61 and 0.69 of it) and contain `jgp`'s, so they are *consistent* with `jgp`. But that the two balanced layouts
  agree "across a 31-fold change in count" is **not established**.
- **(c)** The registered layout control fails on exactly this: P6_fp16 FAILs at 0.181, and the fp32 control
  `b32p_22` reads 0.140.
- **(d)** The multi-bit rungs say the same from the other side: one flipped fp16 bit costs 4.536 W, two 5.228 W
  and four 6.260 W. The **marginal** cost of a further flipped bit between the 2-bit and 4-bit rungs is
  **56.2 ± 12.7 fJ**, against 373 and 386 fJ for the single-bit rungs of the two bits it adds (bits 6 and 7):
  **6.8×**. That is E67's amendment A13 algebra (`T + e·n·rate`) with `T` dominant. The marginal is
  *exploratory*: A4 defined it after two of its four block-A passes had been seen.

**What this means for E65's and E67's published lists.** What was measured: at fp32 B bit 22, E65's dearest
position, the published-style `jg` price is 7.0× the balanced one. What is inferred, not measured: that E65's
other 31 positions carry the same composite, and E67's A-side list too (no A-side balanced layout was run).

**So a bit price travels as a pair where both halves were measured.** One half is the all-in step in the `jg` /
A-side construction. It is what E65 and E67 published, and what a workload pays when that bit starts alternating
against a constant partner. The other half is the `jgp` balanced price: 150 fJ at fp32 bit 22, 88 fJ [58, 117] at
fp16 bit 9. Everywhere else a bit price travels as an all-in number with this caveat attached.

The fp16 `jgp` mean carries one low pass: 7921 reads 1.4 fJ, while the other seven read 96–108 fJ (without it,
100 ± 4.5 fJ). The minion-rail arm reads 73–80 fJ in every pass, 7921 included (75.9; all eight 77.4 ± 1.9), so
the low value is in that pass's board reading. The registered mean keeps it. Balanced fp16 over balanced fp32 is
0.58 [0.39, 0.78]. int8 has no balanced price that is robust to the leakage slope.

**None of this tests the width model.** P8 (0.0023) and P8_kg (0.081) fail as registered. The first version's
"0.58 and 0.33 against the 0.458 and 0.333 the widths imply" mixed footings: `jg`/`jg` for fp16 against
`kg`/`jgp` for int8. It also used int8's bit 6 rather than its dearest `kg` position, bit 5, which gives 0.57.
It is withdrawn.

**The registered consequence of a P6 failure** was "the registered stream order is wrong". For int8 that is what
happened: both halves issue in one cycle (A4, A6). int8's P6 itself is not scored, because its primary is a bound.
For fp16 and fp32 the failure does not by itself say the order is wrong. Under the registered order the two
layouts' designed counts differ by 3%, while their watts differ 5.6–7×. E79 reads the gap, as A4 did, as the
result path swinging between two diverging accumulators. That is a hypothesis it did not test. Every `jg` price is
reported with that caveat attached, as the registration requires (departure D5).

**6. What zeros buy, against a constant nonzero tile.** Replacing a constant nonzero tile with an all-zero one
saves **8.736 ± 0.054 W** in fp16 and **1.834 ± 0.113 W** in int8. Both figures are paired per pass and need no
idle bracket (A7). They are *exploratory*: A7 defined the quantity after three of its four passes had been seen.
Per operation that is 7.79 nJ against 0.95 nJ (8.2×); per multiply-add, 0.95 pJ against 0.058 pJ (16.4×).

The factor of 4.76 between the two watt figures is what the two formats' ungated constant-operand ops draw above
their all-zero state. It is not a measurement of how the zero gate works. An all-zero tile makes every 32-bit word
zero in every format, so it is gated alike under a one-test-per-word rule and a per-element rule, and it cannot tell
them apart. E79 also measured no fp32 zeros. **So E79 neither confirms nor tests Q130(g)'s zero-gate reading
(`d8d7e19e`).**

The first version said otherwise, and three things are withdrawn: its "Q130(g)'s RTL reading measured on silicon",
its "the price of a zero falls as the format narrows", and the last sentence of amendment A5. Testing the gate
needs a word that is only partly zero, one zero element per word, in each format.

The registered idle-bracketed form, P4, reads 0.204 for fp16 (FAIL against ≤ 0.20). For int8 it is not scored: it
rests on two passes, and would read 3.80. The bracket is the second before each launch, and in a dense pass it
still carries the previous run's tail.

## Corrections after verification (Sat 31 Oct 2026)

An adversarial verification (Q130, 10:42–11:10 PDT) re-derived every price, interval, pass count, the fitted
leakage slope and both drift set-asides from the raw telemetry, independently, and they all reproduced exactly.
It found the faults below. The fixes are desk-only: no card was touched and nothing was re-run. The first version
is `8d2fe956`; this section and the corrections are in the commit that carries them.

| | What was wrong | Corrected |
|---|---|---|
| **C1** | The rule tally, "15 passed, 10 failed, 0 not scored". `report_e79.py` applied the registered resolution rule to the price lists but not to the derived ratios that P4, P5 and P6 are scored on — although its own docstring said it did | The scorer now applies the rule to the derived ratios. **P4_int8** (FAIL), **P5_int8_2**, **P5_int8_4** and **P5_int8_mono** (PASS) and **P6_int8** (FAIL) become *not scored*: they rest on two passes or divide by bounds. **P3b** and **P3b_kg** are flagged *vacuous*: they would pass even if bit 7 cost nothing. **12 / 8 / 5 of 25**, and 11 / 6 / 5 of the 22 registered before the data. No band moved |
| **C2** | "Every price moves −8.7% to +5.0%; no registered verdict moves" (the E71-slope arm) | Under the first scorer, **four verdicts moved**: P5_int8_4 PASS → FAIL, P6_int8 FAIL → PASS, and P5_int8_2 and P5_int8_mono PASS → not scored (13 / 10 / 2). With C1 none move (12 / 8 / 5 at both slopes). Prices move −8.4% to 0% (fp16, fp32) and −1.3% to +3.6% (int8 A). The **int8 B `kg` list moves −96% to +19%, and all eight of its positions become bounds**; int8 B `jgp` becomes a bound too. So the int8 B level, any balanced int8 price, and 4b's odd/even pattern (ratio 1.98 → 0.85) are not robust to the leakage slope. The sensitivity table now prints intervals, marks bounds, and is followed by a per-list summary and the verdicts at both slopes |
| **C3** | The account of card access omitted a probe at 09:12:21 PDT that opened the management device before the registration and the claim. "Every device process under `timeout 10`" was not true of the management reads | Departures **D2** and **D3** |
| **C4** | Result 6 called the 4.76 zeros factor "Q130(g)'s RTL reading measured on silicon" and said "the price of a zero falls as the format narrows". An all-zero tile cannot tell a per-word gate from a per-element one, and no fp32 zeros were measured | Result 6 restated as what was measured. The confirmation, the "widest format" claim and A5's last sentence are withdrawn; the test that would decide it is named |
| **C5** | "The width prediction holds" (Result 1) and "the width law holds on both footings … 0.58 and 0.33" (Result 5) | P2a/P2b pass as registered but measure counting (Result 2). P8 and P8_kg fail, with no post hoc comparison set beside them. The 0.33 used a non-dearest position and mixed footings |
| **C6** | Result 3: "int8 is faster because it has twice the units"; the result's blog point said "1.7× faster … twice the arithmetic" | Per op 1.72×, per multiply-add **3.43×**; 64 against 16 MACs a cycle is 4× the multipliers |
| **C7** | Result 5's scope: "E65's and E67's published fp32 lists are composites, 6–7× in fp32 as much as fp16"; "`jgp` and `kg` … give the same per-bit price"; the marginal set against bit 9's 494 fJ | Measured at fp32 B bit 22 and fp16 B bit 9 only: **7.0× and 5.6×**. `kg` is a bound, consistent with `jgp` but not shown equal to it. E65's other positions and E67's A side are inferred. The marginal is set against bits 6 and 7, the bits it adds (6.8×, not 8.8×) |
| **C8** | "The minion-rail arm sits at 0.79–0.81 of the board arm on every item" (a block-A figure) | 0.50–1.19 over the 52 resolved items; **0.754–0.987** over the 31 steps of 1 W or more (Result 2) |
| **C9** | The amendment record (§ Amendments): stamps rewritten without a note; A4 and A7 called "before the data they touch"; A8 called "two more" passes; `predictions.json` `amendment_A4.dated` "09:58" | Notes added under § Amendments. The marginal and zeros − h0 quantities are labelled exploratory. A8 is restated as executing A3's plan. `predictions.json` is corrected, with the first value kept beside it (`dated_correction`); no rule or band in it changed |
| **C10** | Stale or wrong numbers: the int8 A MSB "1.95×" the magnitude mean; 4b's fp16 list "…344, 371, 372, 467, 491" (a three-pass draft); "every int8 B rung reads 0.012 W"; "card runs 09:27–10:3x PDT"; "P8 reads 0.081"; `ettelem config` "identical at every read"; int8 `jgp` "3 fJ" with no count caveat | **1.85×**; the table's list (…334, 373, 386, 431, 494); −0.119 to +0.078 W (bit 6 alone reads 0.012); **09:27:05–10:33:06**; P8 reads 0.0023 and P8_kg 0.081; minion_mv 522 at three of the 22 committed reads (end of 7912, 7915, 7920); int8 `jgp` 44 fJ at the 1,024 count A4/A6 imply |
| **C11** | The int8 A and B lists were counted on different footings: A per lane (8,192), B `kg` per TIMA unit (1,024), though one A read feeds both units | The convention is stated, and the per-unit A prices are given beside the per-lane ones (Result 4, § How a price is counted) |
| **C12** | Mechanisms stated as fact: the cheap fp16 exponent without 1b's caveat; the int8 MSB's "weight 128 and the sign correction" | 1b's caveat travels with Result 1. The MSB is an A-side all-in observation, and its mechanism is a hypothesis: weight cannot be it, since bits of weight 1–64 cost the same |
| **C13** | The registered consequence of a P6 failure ("the registered stream order is wrong") was replaced by the accumulator mechanism without naming the departure | Departure **D5**, per format (Result 5) |
| **C14** | RTL citations carried no commit; `ident/firmware.txt` kept the tool's ANSI colour codes | Cited at `core-et@b38a1a3`; the escape codes are stripped (text unchanged; the raw bytes are in `8d2fe956`) |

## Departures

- **D1** (registered, E60's): on aifoundry3 a user who is only logged in does not block. Other lab users kept idle
  logins there throughout. None held the card, a device node or the card lock at any point.
- **D2 — a read-only probe opened the card's management device before the registration and the claim.** At
  09:12:21 PDT the lane ran a probe on aifoundry3: 12 min 37 s before `2a72d352` was pushed and 14 min 33 s before
  the claim. The probe opened `/dev/et0_mgmt` three times:
  - `ettelem --help` and `ettelem version`, outside the card lock under `timeout 10`. Each printed the device's
    identity block, so each opened the device.
  - `ettelem config`, under `flock -w 60` and `timeout 20`. It read TDP 0, 65 °C, 600 MHz and 523 mV.

  All three were reads; nothing was written, and `et-who` had shown the card free at 09:10:33. The probe broke two
  etiquette rules: no device-opening command before the claim, and none outside `flock -n`. Its output is used
  nowhere here. It was missing from the first version of this README and from the lane's result. A future lane
  runs no device-opening command — `--help` and `version` included — before its claim, or outside `flock -n`.
- **D3 — the management reads ran under `timeout 20`, and the identity read under `flock -w 120`.** The
  registration (Protocol, Safety) and the first version said every device process ran under `timeout 10`. The
  launches did (`run_hlp.py`, `lib.sh` `hold10`). The `ettelem config` read at both ends of every pass did not
  (`block.sh` line 86: `timeout 20`, inside the pass's lock). Nor did the `ident` stage (`run_e79.sh`): it takes the
  card lock with a bounded wait, `flock -w 120`, rather than `-n`, and reads under `timeout 20`. The code is
  committed as it ran (`code.sha256`). A reuse should change both reads to `timeout 10` and `ident` to `flock -n`.
- **D4 — pass 7910 ran a `run_e79.sh` that was not yet committed.** Pass 7910 started at 09:28:21. Its
  `code.sha256` records the `run_e79.sh` that `e66f7c1a` committed later, at 09:31:52. The registered file listed
  the additivity rungs as `b16m` and `b8m`. Those select nothing: `run_hlp.py` takes an exact name or a prefix ending
  in `_`, and refuses a selector that matches no item. So the registered list could not have launched. The fix
  selects exactly the registered `b16m2`, `b16m4`, `b8m2` and `b8m4`, and passes the identity read's device as an
  index (`-n 0`) rather than a path. A1, committed with it, said "nothing else changes". The change touches no
  item, count, band or analysis.
- **D5 — the registered consequence of a P6 failure.** The registration said a P6 failure "means the registered
  stream order is wrong, and every price in this experiment is reported with that caveat attached". For int8 the
  order was wrong (A4, A6), though int8's P6 is not scored. For fp16 and fp32, E79 reads the failure as the result
  path (A4's hypothesis, untested), not as the order. The caveat is attached to every `jg` price, as the
  registration requires (Result 5).

## The tables — card aifoundry3, 600 MHz, 521.9 mV

Passes kept [7910, 7911, 7913, 7915, 7920, 7921, 7922, 7923] (8); runs kept 348 of 480; leakage slope 0.0834 W/°C from 310 runs; cycles per op {'fp16': 546.0024000000001, 'fp32': 546.0024000000001, 'int8': 318.00149999999996}.
Passes set aside: [{'pass': 7912, 'failed_runs': 0, 'pi_drift_W': 0.410499999999999}, {'pass': 7914, 'failed_runs': 0, 'pi_drift_W': 0.5274999999999963}].

### fp16, B side (A = 1.0), jg layout

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | mantissa | 1.881 ± 0.010 | **205** | [204, 206] | 1503.72 | 4.9e+06 | 4 |
| 1 | mantissa | 2.053 ± 0.032 | **224** | [220, 227] | 1641.30 | 5.35e+06 | 4 |
| 2 | mantissa | 2.344 ± 0.061 | **255** | [249, 262] | 1873.90 | 6.1e+06 | 4 |
| 3 | mantissa | 2.705 ± 0.050 | **295** | [289, 300] | 2162.63 | 7.05e+06 | 4 |
| 4 | mantissa | 2.948 ± 0.052 | **321** | [315, 327] | 2357.01 | 7.68e+06 | 4 |
| 5 | mantissa | 3.073 ± 0.310 | **334** | [301, 368] | 2455.57 | 8e+06 | 4 |
| 6 | mantissa | 3.429 ± 0.062 | **373** | [367, 380] | 2741.36 | 8.93e+06 | 4 |
| 7 | mantissa | 3.543 ± 0.960 | **386** | [281, 490] | 2833.14 | 9.23e+06 | 4 |
| 8 | mantissa | 3.956 ± 1.106 | **431** | [310, 551] | 3162.13 | 1.03e+07 | 4 |
| 9 | mantissa | 4.536 ± 0.268 | **494** | [465, 523] | 3626.17 | 1.18e+07 | 8 |
| 10 | exponent | 0.653 ± 0.040 | **71** | [67, 76] | 521.84 | 1.7e+06 | 4 |
| 11 | exponent | 0.616 ± 0.063 | **67** | [60, 74] | 492.31 | 1.6e+06 | 4 |
| 12 | exponent | 0.588 ± 0.033 | **64** | [60, 68] | 470.03 | 1.53e+06 | 4 |
| 13 | exponent | 0.762 ± 0.061 | **83** | [76, 90] | 609.31 | 1.98e+06 | 4 |
| 14 | exponent | 0.699 ± 0.268 | **76** | [47, 105] | 559.19 | 1.82e+06 | 4 |
| 15 | sign | 0.313 ± 0.516 | **34** | [-22, 90] | 249.87 | 8.14e+05 | 4 |

Significand Spearman ρ(bit, price) = **1.000**; span over the kept significand positions **2.4×** (205–494 fJ).

### fp16, A side (B = 1.0)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | mantissa | 1.631 ± 0.183 | **355** | [315, 395] | 2608.39 | 8.5e+06 | 4 |
| 1 | mantissa | 1.152 ± 0.489 | **251** | [144, 358] | 1842.33 | 6e+06 | 4 |
| 2 | mantissa | 2.093 ± 0.190 | **456** | [415, 497] | 3346.45 | 1.09e+07 | 4 |
| 3 | mantissa | 1.357 ± 0.779 | **296** | [126, 466] | 2171.19 | 7.07e+06 | 4 |
| 4 | mantissa | 2.203 ± 0.534 | **480** | [363, 596] | 3522.37 | 1.15e+07 | 4 |
| 5 | mantissa | 1.876 ± 0.280 | **408** | [347, 470] | 2998.83 | 9.77e+06 | 4 |
| 6 | mantissa | 2.535 ± 0.157 | **552** | [518, 586] | 4053.23 | 1.32e+07 | 4 |
| 7 | mantissa | 2.303 ± 0.743 | **502** | [340, 664] | 3683.74 | 1.2e+07 | 4 |
| 8 | mantissa | 2.391 ± 0.169 | **521** | [484, 558] | 3824.15 | 1.25e+07 | 4 |
| 9 | mantissa | 2.847 ± 0.214 | **620** | [573, 667] | 4552.26 | 1.48e+07 | 4 |
| 10 | exponent | 0.431 ± 0.204 | **94** | [49, 138] | 688.40 | 2.24e+06 | 4 |
| 11 | exponent | 0.373 ± 0.164 | **81** | [45, 117] | 596.51 | 1.94e+06 | 4 |
| 12 | exponent | 0.337 ± 0.262 | **73** | [16, 131] | 538.31 | 1.75e+06 | 4 |
| 13 | exponent | 0.427 ± 0.050 | **93** | [82, 104] | 683.02 | 2.23e+06 | 4 |
| 14 | exponent | 0.422 ± 0.267 | **92** | [34, 150] | 674.62 | 2.2e+06 | 4 |
| 15 | sign | 0.327 ± 0.258 | **71** | [15, 128] | 523.61 | 1.71e+06 | 4 |

Significand Spearman ρ(bit, price) = **0.855**; span over the kept significand positions **2.5×** (251–620 fJ).

### int8, B side (A = 1), jg layout - does not alternate (A4)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | magnitude | 0.046 ± 0.067 | **1** | [-1, 4] | 10.65 | 3.47e+04 | 4 |
| 1 | magnitude | -0.119 ± 0.286 | **-4** | [-13, 5] | -27.77 | -9.05e+04 | 4 |
| 2 | magnitude | -0.065 ± 0.368 | **-2** | [-14, 10] | -15.15 | -4.94e+04 | 4 |
| 3 | magnitude | 0.069 ± 0.103 | **2** | [-1, 5] | 16.06 | 5.23e+04 | 4 |
| 4 | magnitude | 0.044 ± 0.083 | **1** | [-1, 4] | 10.31 | 3.36e+04 | 4 |
| 5 | magnitude | 0.078 ± 0.125 | **2** | [-2, 6] | 18.05 | 5.88e+04 | 4 |
| 6 | magnitude | 0.012 ± 0.082 | **0** | [-2, 3] | 2.78 | 9.06e+03 | 8 |
| 7 | MSB (sign) | 0.028 ± 0.115 | **1** | [-3, 5] | 6.51 | 2.12e+04 | 4 |

Significand Spearman ρ(bit, price) = **0.286**; span over the kept significand positions **-0.6×** (-4–2 fJ).

### int8, B side (A = 1), kg layout - the int8 B price list (A4)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | magnitude | 0.053 ± 0.025 | **27** | [15, 40] | 199.02 | 6.48e+05 | 4 |
| 1 | magnitude | 0.121 ± 0.087 | **62** | [17, 106] | 452.03 | 1.47e+06 | 4 |
| 2 | magnitude | 0.062 ± 0.027 | **31** | [17, 45] | 229.28 | 7.47e+05 | 4 |
| 3 | magnitude | 0.143 ± 0.017 | **72** | [64, 81] | 530.88 | 1.73e+06 | 4 |
| 4 | magnitude | 0.080 ± 0.017 | **40** | [32, 49] | 297.06 | 9.68e+05 | 4 |
| 5 | magnitude | 0.169 ± 0.059 | **86** | [56, 116] | 628.52 | 2.05e+06 | 4 |
| 6 | magnitude | 0.097 ± 0.043 | **49** | [27, 71] | 360.94 | 1.18e+06 | 4 |
| 7 | MSB (sign) | 0.033 ± 0.321 | **17** | [-146, 180] | 122.98 | 4.01e+05 | 4 |

Significand Spearman ρ(bit, price) = **0.500**; span over the kept significand positions **3.2×** (27–86 fJ).

### int8, A side (B = 1)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | magnitude | 1.359 ± 0.112 | **86** | [79, 93] | 632.35 | 2.06e+06 | 4 |
| 1 | magnitude | 1.181 ± 0.428 | **75** | [48, 102] | 549.77 | 1.79e+06 | 4 |
| 2 | magnitude | 1.128 ± 0.324 | **71** | [51, 92] | 524.76 | 1.71e+06 | 4 |
| 3 | magnitude | 1.390 ± 0.041 | **88** | [86, 91] | 646.98 | 2.11e+06 | 4 |
| 4 | magnitude | 1.452 ± 0.042 | **92** | [89, 95] | 675.61 | 2.2e+06 | 4 |
| 5 | magnitude | 1.324 ± 0.070 | **84** | [79, 88] | 616.18 | 2.01e+06 | 4 |
| 6 | magnitude | 1.227 ± 0.208 | **78** | [65, 91] | 571.03 | 1.86e+06 | 4 |
| 7 | MSB (sign) | 2.399 ± 0.077 | **152** | [147, 157] | 1116.33 | 3.64e+06 | 4 |

Significand Spearman ρ(bit, price) = **0.143**; span over the kept significand positions **1.3×** (71–92 fJ).

### fp32 tie, B side (A = 1.0), jg layout

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 22 | mantissa | 4.830 ± 0.314 | **1052** | [984, 1120] | 7723.45 | 2.52e+07 | 8 |
### fp32, B side, jgp layout (A4 order probe)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 22 | mantissa | 0.669 ± 0.037 | **150** | [142, 159] | 1103.33 | 3.59e+06 | 4 |
### fp32, B side, kg layout (A4 order probe)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 22 | mantissa | 0.023 ± 0.070 | **159** | [-328, 645] | 1163.61 | 3.79e+06 | 4 |
### fp16, B side, jgp layout (the registered control)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 9 | mantissa | 0.781 ± 0.262 | **88** | [58, 117] | 644.82 | 2.1e+06 | 8 |
### fp16, B side, kg layout (A4 order probe)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 9 | mantissa | 0.038 ± 0.060 | **134** | [-75, 342] | 982.56 | 3.2e+06 | 4 |
### int8, B side, jgp layout

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 6 | magnitude | 0.088 ± 0.047 | **3** | [1, 4] | 21.02 | 6.85e+04 | 8 |
### The order probe: the same flip in three layouts (amendment A4)

The dW ratios divide by no designed count, so they are order-free.

| format | jg dW | jgp dW | kg dW | jgp/jg | kg/jg |
|---|---|---|---|---|---|
| fp16 | 4.536 | 0.781 | 0.038 | 0.175 | 0.008 |
| int8 | 0.012 | 0.088 | 0.097 | 0.286 | 0.604 |
| fp32 | 4.830 | 0.669 | 0.023 | 0.136 | 0.005 |

### The marginal price of a further flipped bit (amendment A4)

| format | from | dW per extra flipped bit | marginal fJ per bit | 95% | passes |
|---|---|---|---|---|---|
| fp16 | b16m2 - b16m4 | 0.516 | 56.2 | ± 12.7 | 4 |
| int8 | b8m2 - b8m4 | 0.035 | 1.1 | ± 1.3 | 4 |

### Switching over the idle bracket

A7: the **zeros − h0** column is paired per pass and needs no idle bracket, so it is the robust statement of what zeros buy. The idle-bracketed columns are kept because P4 is registered on them; the bracket is the second before each launch and in a dense pass it can still carry the previous run's tail, which is why its spread is wide.

| format | zeros − h0 (W, idle-free) | 95% | idle bracket W | h0 switching W | zeros switching W | zeros / h0 |
|---|---|---|---|---|---|---|
| fp16 | **-8.736** | ± 0.054 | 25.951 ± 0.141 | 9.581 ± 1.608 | 1.923 | 0.2037 |
| int8 | **-1.834** | ± 0.113 | 27.210 ± 3.707 | 2.473 ± 2.190 | 1.311 | 3.7974 |
| fp32 | **—** | ± 0.000 | 26.032 ± 0.000 | 10.516 ± 0.055 | — | — |

### Additivity (E70's law at low Hamming weight)

| rung | bits | ΔW | sum of its own single-bit ΔW ratio | 95% | fJ per bit |
|---|---|---|---|---|---|
| b16m2 | [8, 9] | 5.228 | 0.615 | ± 0.072 | 285 |
| b16m4 | [6, 7, 8, 9] | 6.260 | 0.404 | ± 0.036 | 170 |
| b8m2 | [5, 6] | 0.101 | 0.637 | ± 2.056 | 2 |
| b8m4 | [3, 4, 5, 6] | 0.172 | 0.596 | ± 1.772 | 1 |

### The layout control (the issue order)

| control | primary | bit | control fJ | primary fJ | ratio | 95% |
|---|---|---|---|---|---|---|
| b16p_9 | b16_9 | 9 | 88 | 494 | 0.181 | ± 0.062 |
| b8p_6 | b8_6 | 6 | 3 | 0 | 4.119 | ± 9.013 |
| b32p_22 | b32_22 | 22 | 150 | 1052 | 0.140 | ± 0.012 |

### The registered rules, scored

A rule is `not scored` when a derived ratio it tests rests on fewer than 3 passes or divides by a price (or an h0 switching figure) whose 95% interval contains zero — the registered resolution rule, applied to the derived quantities since the correction of 31 Oct (the first scoring applied it to the price lists only). A `vacuous` PASS compares a bound and would pass even if the price tested were zero.

| rule | leg | what | test | measured | verdict | note |
|---|---|---|---|---|---|---|
| **P1a** | primary | fp16's B-side mantissa prices rise with position | Spearman rho(bit, fJ) over fp16 B bits 0-9 >= 0.60 | 1 | **PASS** | 10 of 10 mantissa positions kept |
| **P1a_A** | secondary | the same on the A side | Spearman rho(bit, fJ) over fp16 A bits 0-9 >= 0.60 | 0.8545 | **PASS** | 10 of 10 mantissa positions kept |
| **P1b** | primary | the fp16 mantissa spans a factor, as fp32's does | fJ(dearest fp16 B mantissa bit) / fJ(cheapest fp16 B mantissa bit whose price exceeds its own 95% half-width) >= 3.0 | 2.411 | **FAIL** | bit 9 over bit 0 |
| **P1c** | primary | fp16 has no flat floor: its whole 10-bit mantissa is in fp32's rising regime, because fp32's floor ran from the LSB to 13 bits below the significand MSB and fp16's mantissa is only 10 bits deep | fJ(fp16 B bit 5) > fJ(fp16 B bit 0) with the two 95% intervals disjoint | bit5_lo 300.7, bit0_hi 206, gap_fJ 94.69 | **PASS** |  |
| **P2b** | primary | fp16's dearest significand bit costs less than fp32's by roughly the significand-width ratio, B side | fJ(dearest fp16 B mantissa bit) / fJ(this run's b32_22) in [0.25, 0.80] | 0.4695 | **PASS** | fp16 B bit 9 over this run's b32_22 |
| **P2b_e65** | secondary | the same against E65's published fp32 number instead of this run's tie | fJ(dearest fp16 B mantissa bit) / 1008 in [0.25, 0.80] | 0.49 | **PASS** |  |
| **P2a** | primary | the same on the A side, against E67's published 1440 fJ | fJ(dearest fp16 A mantissa bit) / 1440 in [0.25, 0.80] | 0.4306 | **PASS** | fp16 A bit 9 over E67's 1440 fJ |
| **P3a** | primary | int8 prices rise toward the high bits | Spearman rho(bit, fJ) over int8 B bits 0-6 >= 0.60 | 0.2857 | **FAIL** | 7 of 7 magnitude positions kept; inputs that are bounds: bits [0, 1, 2, 3, 4, 5, 6] |
| **P3a_A** | secondary | the same rise on the A side | Spearman rho(bit, fJ) over int8 A bits 0-6 >= 0.60 | 0.1429 | **FAIL** | 7 of 7 magnitude positions kept |
| **P3b** | primary | int8's sign bit 7 is not cheaper than bit 6 | fJ(int8 B bit 7) >= fJ(int8 B bit 6) - the 95% half-width of the per-pass paired difference | bit7_fJ 0.8867, bit6_fJ 0.3789, allowance_fJ 4.488 | **PASS (vacuous)** | inputs that are bounds: bits [6, 7]; vacuous: the allowance exceeds bit 6's price, so the test passes even if bit 7 cost nothing |
| **P4_fp16** | primary | the zeros rung costs at most 0.2x the h0 switching, fp16 | (P(z16) - P(idle)) / (P(h16q) - P(idle)) <= 0.20 | 0.2037 | **FAIL** | zeros 1.922776920062696 W, h0 9.581021106510887 W over idle 27.009974201606582 W, 4 passes |
| **P4_int8** | primary | the same for int8 | (P(z8) - P(idle)) / (P(h8q) - P(idle)) <= 0.20 | — (would read 3.797) | **not scored** | the ratio rests on 2 passes |
| **P5_fp16_2** | primary | two bits flipping together are sub-additive but not far from the sum (E70's saturating law at low Hamming weight) | dW(b16m2) / [dW(b16_8) + dW(b16_9)] in [0.55, 1.05] | 0.6146 | **PASS** | bits [8, 9] |
| **P5_fp16_4** | primary | four bits share more | dW(b16m4) / sum of dW(b16_6..b16_9) in [0.35, 1.00] | 0.4043 | **PASS** | bits [6, 7, 8, 9] |
| **P5_fp16_mono** | primary | the sharing grows with the Hamming weight | r4 <= r2 + 0.10 (fp16) | -0.2103 | **PASS** | r4 - r2 |
| **P5_int8_2** | primary | the same at two bits, int8 | dW(b8m2) / [dW(b8_5) + dW(b8_6)] in [0.55, 1.05] | — (would read 0.6374) | **not scored** | the ratio rests on 2 passes; its denominator sums single-bit prices that are bounds (bits [5, 6]) |
| **P5_int8_4** | primary | the same at four bits, int8 | dW(b8m4) / sum of dW(b8_3..b8_6) in [0.35, 1.00] | — (would read 0.5963) | **not scored** | the ratio rests on 2 passes; its denominator sums single-bit prices that are bounds (bits [3, 4, 5, 6]) |
| **P5_int8_mono** | primary | the same monotonicity, int8 | r4 <= r2 + 0.10 (int8) | — (would read -0.04105) | **not scored** | r2 or r4 is not scored |
| **P6_fp16** | primary | the registered issue order is the one the unit runs: the same flip in the group-parity layout costs the same per bit | fJ(b16p_9) / fJ(b16_9) in [0.80, 1.25] | 0.1808 | **FAIL** | control 87.83443754523032 fJ vs primary 493.9380153467443 fJ |
| **P6_int8** | primary | the same for int8 | fJ(b8p_6) / fJ(b8_6) in [0.80, 1.25] | — (would read 4.119) | **not scored** | its denominator, the primary b8_6, is a bound |
| **P3a_kg** | A4 re-score | P3a on the layout that does alternate in int8 (amendment A4): int8 prices rise toward the high bits | Spearman rho(bit, fJ) over int8 B kg bits 0-6 >= 0.60 | 0.5 | **FAIL** | 7 of 7 magnitude positions kept, kg layout |
| **P3b_kg** | A4 re-score | P3b on the kg layout: int8's sign bit 7 is not cheaper than bit 6 | fJ(int8 B kg bit 7) >= fJ(int8 B kg bit 6) - the 95% half-width of the difference | bit7_fJ 16.75, bit6_fJ 49.16, allowance_fJ 164.2 | **PASS (vacuous)** | inputs that are bounds: bits [7]; vacuous: the allowance exceeds bit 6's price, so the test passes even if bit 7 cost nothing |
| **P8_kg** | A4 re-score | P8 on the kg layout: int8's dearest position costs about the 8/24 width ratio of fp32's | fJ(dearest int8 B kg position) / fJ(this run's b32_22) in [0.15, 0.60] | 0.08138 | **FAIL** | int8 B kg bit 5 over this run's b32_22 |
| **P7** | primary | the port reproduces E65 on the same card at the one fp32 position it reruns | fJ(b32_22) in [756, 1260] (1008 fJ +- 25%) | 1052 | **PASS** | 95% [983.6606381112914, 1120.4381465942292] |
| **P8** | primary | int8's dearest position costs about the 8/24 width ratio of fp32's | fJ(dearest int8 B position) / fJ(this run's b32_22) in [0.15, 0.60] | 0.002337 | **FAIL** | int8 B bit 5 over this run's b32_22; the numerator (bit 5) is a bound, so the ratio lies in [-0.0014, 0.0061] |

12 passed (2 of them vacuous: P3b, P3b_kg), **8 failed**, 5 not scored, of 25; of the 22 registered before the data (A4's three re-scores left out): 11 passed, 6 failed, 5 not scored.

### The registered rules at E71's slope (the registered sensitivity arm)

At 0.3803 W/°C: 12 passed (2 of them vacuous: P3b, P3b_kg), **8 failed**, 5 not scored, of 25; of the 22 registered before the data (A4's three re-scores left out): 11 passed, 6 failed, 5 not scored.

No verdict moves between the two slopes.

### Sensitivity: every price at E71's measured idle slope 0.3803 W/°C

A **bound** is a price whose 95% interval contains zero. The change is quoted only for a price that is a coefficient at the fitted slope; a change in a bound means nothing.

| list | bit | fitted-slope fJ [95%] | E71-slope fJ [95%] | change |
|---|---|---|---|---|
| fp16_a | 0 | 355 [315, 395] | 338 [299, 377] | -4.8% |
| fp16_a | 1 | 251 [144, 358] | 240 [140, 341] | -4.2% |
| fp16_a | 2 | 456 [415, 497] | 439 [407, 470] | -3.7% |
| fp16_a | 3 | 296 [126, 466] | 278 [110, 446] | -6.0% |
| fp16_a | 4 | 480 [363, 596] | 444 [323, 566] | -7.4% |
| fp16_a | 5 | 408 [347, 470] | 398 [333, 463] | -2.6% |
| fp16_a | 6 | 552 [518, 586] | 509 [471, 548] | -7.8% |
| fp16_a | 7 | 502 [340, 664] | 471 [295, 647] | -6.1% |
| fp16_a | 8 | 521 [484, 558] | 487 [448, 526] | -6.5% |
| fp16_a | 9 | 620 [573, 667] | 585 [550, 619] | -5.7% |
| fp16_a | 10 | 94 [49, 138] | 91 [47, 136] | -2.6% |
| fp16_a | 11 | 81 [45, 117] | 81 [45, 117] | +0.0% |
| fp16_a | 12 | 73 [16, 131] | 73 [16, 131] | +0.0% |
| fp16_a | 13 | 93 [82, 104] | 88 [66, 110] | -5.2% |
| fp16_a | 14 | 92 [34, 150] | 90 [33, 147] | -1.8% |
| fp16_a | 15 | 71 [15, 128] | 71 [15, 128] | +0.0% |
| fp16_b | 0 | 205 [204, 206] | 191 [177, 206] | -6.5% |
| fp16_b | 1 | 224 [220, 227] | 205 [202, 208] | -8.3% |
| fp16_b | 2 | 255 [249, 262] | 236 [226, 247] | -7.4% |
| fp16_b | 3 | 295 [289, 300] | 273 [264, 282] | -7.4% |
| fp16_b | 4 | 321 [315, 327] | 296 [294, 298] | -7.9% |
| fp16_b | 5 | 334 [301, 368] | 309 [269, 348] | -7.7% |
| fp16_b | 6 | 373 [367, 380] | 348 [339, 356] | -6.9% |
| fp16_b | 7 | 386 [281, 490] | 358 [252, 463] | -7.3% |
| fp16_b | 8 | 431 [310, 551] | 401 [282, 521] | -6.8% |
| fp16_b | 9 | 494 [465, 523] | 464 [434, 494] | -6.1% |
| fp16_b | 10 | 71 [67, 76] | 69 [66, 72] | -3.4% |
| fp16_b | 11 | 67 [60, 74] | 61 [53, 69] | -8.4% |
| fp16_b | 12 | 64 [60, 68] | 63 [59, 67] | -1.3% |
| fp16_b | 13 | 83 [76, 90] | 77 [74, 80] | -7.3% |
| fp16_b | 14 | 76 [47, 105] | 75 [48, 102] | -1.6% |
| fp16_b | 15 | 34 [-22, 90] bound | 33 [-24, 90] bound | — |
| fp16_b_jgp | 9 | 88 [58, 117] | 84 [55, 112] | -4.8% |
| fp16_b_kg | 9 | 134 [-75, 342] bound | 134 [-75, 342] bound | — |
| fp32_b | 22 | 1052 [984, 1120] | 996 [925, 1066] | -5.4% |
| fp32_b_jgp | 22 | 150 [142, 159] | 149 [139, 160] | -0.6% |
| fp32_b_kg | 22 | 159 [-328, 645] bound | 159 [-328, 645] bound | — |
| int8_a | 0 | 86 [79, 93] | 85 [77, 94] | -1.1% |
| int8_a | 1 | 75 [48, 102] | 74 [44, 104] | -1.3% |
| int8_a | 2 | 71 [51, 92] | 74 [65, 83] | +3.6% |
| int8_a | 3 | 88 [86, 91] | 87 [82, 92] | -1.1% |
| int8_a | 4 | 92 [89, 95] | 95 [81, 110] | +3.3% |
| int8_a | 5 | 84 [79, 88] | 83 [77, 89] | -1.1% |
| int8_a | 6 | 78 [65, 91] | 77 [64, 89] | -1.2% |
| int8_a | 7 | 152 [147, 157] | 151 [144, 158] | -0.6% |
| int8_b | 0 | 1 [-1, 4] bound | -2 [-16, 11] bound | — |
| int8_b | 1 | -4 [-13, 5] bound | -4 [-17, 8] bound | — |
| int8_b | 2 | -2 [-14, 10] bound | -5 [-10, -0] bound | — |
| int8_b | 3 | 2 [-1, 5] bound | -1 [-14, 12] bound | — |
| int8_b | 4 | 1 [-1, 4] bound | -3 [-16, 10] bound | — |
| int8_b | 5 | 2 [-2, 6] bound | -1 [-7, 4] bound | — |
| int8_b | 6 | 0 [-2, 3] bound | -2 [-6, 2] bound | — |
| int8_b | 7 | 1 [-3, 5] bound | -5 [-11, 1] bound | — |
| int8_b_jgp | 6 | 3 [1, 4] | -1 [-4, 3] **bound** | -118.8% |
| int8_b_kg | 0 | 27 [15, 40] | 3 [-147, 153] **bound** | -90.3% |
| int8_b_kg | 1 | 62 [17, 106] | 13 [-140, 165] **bound** | -79.5% |
| int8_b_kg | 2 | 31 [17, 45] | 35 [-65, 135] **bound** | +12.0% |
| int8_b_kg | 3 | 72 [64, 81] | 5 [-96, 105] **bound** | -93.7% |
| int8_b_kg | 4 | 40 [32, 49] | 48 [-46, 142] **bound** | +18.6% |
| int8_b_kg | 5 | 86 [56, 116] | 39 [-196, 273] **bound** | -55.0% |
| int8_b_kg | 6 | 49 [27, 71] | 2 [-188, 192] **bound** | -95.7% |
| int8_b_kg | 7 | 17 [-146, 180] bound | -2 [-246, 242] bound | — |

Per list, over the positions that are coefficients at the fitted slope:

| list | positions | change at E71's slope | of them bounds at E71's slope |
|---|---|---|---|
| fp16_a | 16 | -7.8% to +0.0% | 0 |
| fp16_b | 15 | -8.4% to -1.3% | 0 |
| fp16_b_jgp | 1 | -4.8% to -4.8% | 0 |
| fp32_b | 1 | -5.4% to -5.4% | 0 |
| fp32_b_jgp | 1 | -0.6% to -0.6% | 0 |
| int8_a | 8 | -1.3% to +3.6% | 0 |
| int8_b_jgp | 1 | -118.8% to -118.8% | 1 |
| int8_b_kg | 7 | -95.7% to +18.6% | 7 |

## What the card had to tell us about itself first

**The host's tile layout per format, read from its own source.** `workloads/sparsity/host/main.cpp` —
`makeTiles` packs the tiles and `fillValues`'s `file:` branch reads 1,024 raw A bytes then 1,024 raw B bytes
**in the chosen type's layout, before the per-type value code and for every `--type`**, so one tile file gives
any kind of number in any format with no rebuild:

```
E    = 1 (fp32) | 2 (fp16) | 4 (int8)          elements of B per column per 64 B line
K    = 16 * E                                  the tile's depth: 16 | 32 | 64
A[i][k]      at byte  i * 64 + k * size        16 lines of 64 B; A row i = line i
B[p*E+e][j]  at byte  p * 64 + (j * E + e) * size
```

For **fp16** the two K-terms of one column sit adjacent inside a 32-bit group; for **int8** the four do. One
32-bit word holds E elements **of one column**, not of one row. A tile written in the fp32 layout and fed to
`--type fp16` flips entirely different bits, which is why `make_hlp.py` packs by format and `--check` reads every
file back through the same layout.

**The card's own state, read only, at both ends of every pass.** `ettelem config` ran before and after each of the
ten passes and the smoke (`config_start.json`, `config_end.json`: 22 committed reads, plus `ident/config.json`). It
read `tdp_w` 0, `temp_threshold_c` 65, `power_state_name` max_power and `minion_mhz` 600 at every read, and
`minion_mv` 523, except 522 at three end-of-pass reads (7912, 7915, 7920). So the governor stayed latched at 600 MHz
by its boot-time TDP of 0, and nothing in E79 wrote a knob. (The 09:12:21 probe, D2, read the same values.)

The **firmware**, which the Horace hub's Status item 7 says nobody re-read in Q129, was read from the read-only
`DM_CMD_GET_*` queries (`ident/firmware.txt`, 09:27:22):

| Field | Reading |
|---|---|
| release | **1.4.0** |
| BL1 / BL2 | **0.22.0** / **0.22.0** |
| PMIC | **1.5.0** |
| Master / Worker / Machine Minion | **0.25.1** |
| ASIC revision | **597** |
| module uptime | 4 d 18 h 9 m |
| TDP level | 0 |
| software temperature threshold | 65 °C |

That is **the same reading aifoundry2 gave E69 and E72**. So Q129's throttle-wrap gate conclusion at BL2 0.22.0
covers this card too, and `docs/findings/14-card-behaviour.md`'s three "aifoundry3 was not re-read" notes can
close. E79 does not edit that file: another lane owns it.

**The unit's own micro-op structure, measured rather than assumed.** The registered order is PRM 9.4's, as
`hl/make_hl.py` states it for fp32, generalised: for each B line group, for each A row, two micro-ops (C columns
0–7, then 8–15), with lane *l* taking column *l* and then column 8+*l*, and A broadcast to all eight lanes. That
holds for the 546-cycle formats. **It does not hold for int8**, and pass 7910 said so (Result 3).

## How a price is counted (the same rule E65 used)

A **designed flip** is an operand *element read* whose chosen bit differs from the previous read in the same
lane's stream, summed over the eight lanes and wrapped op to op. That is `make_hl.py:fma_flips`'s rule,
parameterised by format in `make_hlp.py:count_flips` and re-derived from every written file by `--check`. The
price is

```
e  =  (P(item) - P(its own zero))  /  (designed flips per op  x  ops per second)
```

It is computed **per pass** and then averaged over passes, and its interval is `t(0.975, n-1)` × the between-pass
SE. The unit of replication is the pass, never samples inside one burst. `P` is the mean board power over
[t0+1 s, t0+3 s), corrected to the launch reading with the card's leakage slope (21 Sep's `p80`). The **idle
bracket** is the second before each launch, with the card idle at the same 58 °C reading.

| | designed flips per multiply-add, 8 lanes, one bit per flipping element read |
|---|---|
| **B side, `jg` layout** | 16 rows × K × 16 columns = **4,096** (fp32) · **8,192** (fp16) · 16,384 (int8, *never reached — Result 3*) |
| **B side, `kg` layout** | **128** (fp32) · **256** (fp16) · **1,024** (int8, the closed form its 318-cycle structure implies, counted per TIMA unit) |
| **A side** | half the B side: **2,048** (fp32) · **4,096** (fp16) · **8,192** (int8, counted per lane) |

The A side is half the B side in every format, for E67's reason: the issue order holds an A word across both
micro-ops of a row, so an A word can change only every *second* cycle. The reduction divides each item by its
**own** manifest count.

**The int8 footing (C11).** In int8 the two TIMA units of a lane read their own B words (`tenb_rd_addr` per unit,
`vpu_lane.v:438`) but share one A read (`tena_rd_data`, `:435`). The int8 B `kg` count is per unit; the int8 A
count is per lane. To put int8 A on the B list's per-unit footing, double its count: every int8 A price halves
(MSB 76 fJ, magnitude 36–46 fJ). The tables keep the per-lane A count the registration used. The float formats
have one unit a lane, so for them the two footings coincide.

The fp16 and int8 `jgp` items carry the generic model's count (7,936; 15,872). In int8 the half index never
alternates in time, so `jgp` alternates only on the line-group parity, exactly like `kg`. At `kg`'s 1,024 count,
`b8p_6` reads 44 [20, 68] fJ beside `b8k_6`'s 49 [27, 71]. Both are bounds at E71's slope.

## Amendments

A1–A8 are dated in the registration README. None moves a registered band. A4 added items and reported quantities,
exactly as E67's A13 and A14 did.

| | What | Commit |
|---|---|---|
| **A1** | four more passes of exactly the registered item list, because a pass took 4.5 min rather than the budgeted 12 | `e66f7c1a`, 09:31:52 |
| **A2** | `collect_e79.sh`, the plumbing that reduces every finished pass and runs the registered E71-slope sensitivity arm | `e66f7c1a`, 09:31:52 |
| **A3** | A1's four extra passes cut to two, **7914 and 7915** (six passes in all). The measured pace is 8.7 s a run, so eight passes would be ~82 card-minutes, past the registered 75. The budget is the binding constraint and does not move | `270d2108`, 09:32:31 |
| **A4** | the `kg` layout and `b8k_0`…`b8k_7` (the int8 B price list); `b32p_22`, `b32k_22` and `b16k_9` (the order probe); the order-probe and marginal blocks in the reduction; and the A4 re-scoring of P3a / P3b / P8 on the `kg` list beside the registered scoring on `jg` | `4216f1fb`, 09:49:45 |
| **A5** | a citation correction: the zero gate is one 32-bit test (Q130(g), `d8d7e19e`), not the PRM's four-operand rule. Its last sentence ("E79's own P4 result is an independent silicon measurement of that conclusion") is **withdrawn** (C4) | `23197287`, 10:13:39 |
| **A6** | A4's structural wording replaced by the public RTL's (`core-et@b38a1a3`), its count unchanged | `23197287`, 10:13:39 |
| **A7** | P(zeros) − P(h0), paired per pass, reported beside the registered idle-bracketed P4 | `23197287`, 10:13:39 |
| **A8** | the two passes A3 had registered, 7914 and 7915, run after the gate set 7912 aside (restated below) | `23197287`, 10:13:39 |

**Notes on the record (C9), added with the corrections.**
- **Stamps.** The stamps of A1, A3 and A4 were first written as 09:33, 09:35 and 09:58 PDT, times later than their
  own commits (09:31:52, 09:32:31, 09:49:45). `23197287` replaced them with the commit times, without a note.
  A5–A8 were first stamped 10:08, 10:1x, 10:12 and 10:13, and `8d2fe956` replaced those with 10:13:39. The commit
  times are the record. `predictions.json`'s `amendment_A4.dated` kept "09:58" until this correction.
- **A4 and the data it had seen.** A4 was written during pass 7912, with 7910 and 7911 complete, and quotes pass
  7910's numbers. The items it added ran in block B, after it, so they were registered before their data. Its
  **marginal** block uses block-A rungs it had seen (two of the four kept passes), so the marginal is
  **exploratory**. The order probe's fp16 `jgp`/`jg` arm restates the registered P6 control; its fp32 and `kg` arms
  ran only after A4.
- **A7.** A7 defined zeros − h0 after seeing block A's passes, three of the four it uses: **exploratory**. A5 and
  A6 touch no data.
- **A8.** A8 called 7914 and 7915 "two more" passes, "driven by a gate outcome". They were A3's registered
  passes five and six. The queue had been started for four (`go 7910 4`, 09:28:21, before A1 and A3 existed), so A8
  executed A3's plan; it did not add to it. Its rule — every pass that passes the gates is used, and none is chosen
  after the fact — holds as written.

## Files

| File | What |
|---|---|
| `hlp.json`, `runs.csv`, `reduce.txt` | `hlp/reduce_hlp.py` over every pass that finished |
| `hlp-leak0.3803.json`, `runs-leak0.3803.csv`, `reduce-leak0.3803.txt` | the registered sensitivity arm: every price re-reduced at E71's measured aifoundry3 idle slope 0.3803 W/°C instead of the fitted one |
| `results.md`, `report.log`, `scored.json` | `hlp/report_e79.py`: the tables above and every registered rule scored, at the fitted slope (`rules`, `tally`) and at E71's (`rules_leak0.3803`, `tally_leak0.3803`). Regenerated by the corrected scorer (C1, C2); the prices in them are unchanged from `8d2fe956` |
| `manifest.json` | the operand set `build/hlp-gen2`: every item, its designed flip counts re-derived from the files, and each item's own zero |
| `code.sha256` | `tools/claims-v3/lib.sh` and every `tools/claims-v3/hlp/` file as the box ran them. `report_e79.py` was corrected on the desk afterwards (C1); the corrected file is in the commit that carries this section |
| `ident/` | the card's identity, read only: `et-lab-manifest`, `ettelem config` and the firmware revisions (`firmware.txt`, ANSI colour codes stripped, C14) |
| `aifoundry3/hlp/p791x`, `p792x` | per pass: `block.json`, `configs.json`, `config_start.json`, `config_end.json`, `gen.sha256`, `manifest.txt` (`et-lab-manifest`), `marks.jsonl`, `run.log`, `runs.jsonl`, `code.sha256`, `telemetry.jsonl.gz`, `tiles/` (the tiles the host dumped, byte-compared against the generated set) |
| `logs/` | the queue log |

**Operand set and code.** `build/hlp-gen2` was generated and `--check`ed on the box before the first block-B
launch. **Every one of the 62 operand files block A ran is byte-identical in it** (62 of 62, checked on the box).
Block A ran `make_hlp.py`, `run_hlp.py` and `block.sh` from commit `2a72d352`, and the `run_e79.sh` that
`e66f7c1a` committed (D4). Block B ran `4216f1fb`'s files, whose only change to block A's items is additive.
