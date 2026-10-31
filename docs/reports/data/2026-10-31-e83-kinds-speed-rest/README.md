# E83 data: the speed of the 33 kinds E80 did not run, under aifoundry2's own governor (Q130, Sat 31 Oct 2026)

The 33 kinds of numbers in [`kinds.json`](../../../../tools/claims-v3/kinds/README.md) that
[E80](../2026-10-31-e80-kinds-speed/README.md) did not run, on aifoundry2 card 0 under the card's own governor:

- fp32 (13): zeros, ones, neg_ones, pi, randn_small, randn_large, uniform01, sparse50, pow2, fp16grid, a_randn_b_zeros,
  a_zeros_b_randn, randn_sorted;
- fp16 (10): neg_ones, randn_small, uniform01, sparse90, wsparse50, wsparse90, a_randn_b_zeros, a_zeros_b_randn,
  pair_half_zero, randn_sorted;
- int8 (10): ones, pos, ternary, sparse90, wsparse50, wsparse90, highbit, a_full_b_zeros, a_zeros_b_full, sorted.

E80's anchors ran again in the same session: fp32 randn, fp16 randn, int8 full, fp16 zeros and int8 zeros. Each kind
got a **burst on a cool die**, run twice, and a **sustained run** of about 76 s (fp32 ones, fp32 sparse50, fp16
wsparse50 and int8 ternary twice). **Nothing was set on the card**: the TDP and the threshold read 65 W and 65 °C at
all 118 per-run reads of `ettelem config`, the smoke's three, the session's start and end, and once more under the card
lock at about 15:08, before the release. With E80, **all 51 kinds now have a measured speed**, on one card in one
afternoon.

The pre-registration is [`tools/claims-v3/kspeed/e83/`](../../../../tools/claims-v3/kspeed/e83/README.md)
(`c253bd1c`, pushed 13:45:13 PDT). Its frozen predictions are
[`predictions.json`](../../../../tools/claims-v3/kspeed/e83/predictions.json), sha256 `97f58c89…`. The card was claimed
in `#community-lab` at 13:45:55 and released by editing the same post at 15:08. No amendment was made.

| session | PDT | what |
|---|---|---|
| `smoke/` | 13:46:04–13:46:25 | three 2 s `file:` launches of new tiles (fp32 a_zeros_b_randn, fp16 pair_half_zero, int8 highbit): 546.0 / 546.0 / 318.0 cycles per op, config 65 W / 65 °C; not analysed |
| `s1/` | 13:46:47–15:07:37 | the registered session, 118 runs, exit 0, **80.8 card-minutes** (81.1 with the smoke, of the 100 allowed): `BURST` 76 runs (13:46–14:02), `SUS` 42 runs (14:02–15:07) |

## Results first

### 1. Six of the eight registered rules pass

**The chain kind → watts → clock now works in both regimes.** E80's own measured relation between a kind's power and
its clock, fed Q130(c)'s predicted power for kinds it never saw, hit the 33 burst clocks to **11.8 MHz rms** and the 33
sustained clocks to **14.3 MHz rms**, and called 29 of the 33 sustained limits. On each kind's own measured power the
same relation reproduces the clocks to **7.9 and 7.5 MHz**. Q130(c)'s own frozen clocks, which used 23 October's heat
path, miss the sustained cells by 23.4 MHz rms.

**What fails is the power model**: it says a lane gated by a zero operand costs exactly what zeros cost (it costs
0.1–0.8 W more), it over-charges fp32 `sparse50` and `fp16grid`, and it under-charges fp32 `pow2`. Each verdict is scored exactly as registered
([`results.json`](results.json) `rules`, [`reduce.txt`](reduce.txt)).

| rule | verdict | what the data say |
|---|---|---|
| **E83-R1** burst rms ≤ 25 MHz, (a) on Q130(c)'s power | **PASS** | **11.8 MHz** over the 33. Over the nine kinds (a) puts below 800, 19.8; on A1's reset-free cells 10.3. Q130(c)'s own 4–12 s numbers: 12.6; E64's governor on Q130(c)'s power: 12.4 |
| **E83-R2** sustained limit right for ≥ 80% | **PASS** | **29 of 33** (88%). The four misses are the kinds (a) put on the knife-edge, share at 800 predicted 0.59–0.76: fp32 ones and fp32 sparse50 (one run `none`, one `thermal`), fp16 neg_ones and fp16 wsparse50 (`none`, predicted `thermal`). Q130(c)'s two-way call: 27 of 33 |
| **E83-R3** sustained rms ≤ 25 MHz, (a) on Q130(c)'s power | **PASS** | **14.3 MHz**; 18.3 over the 18 kinds (a) puts below 800. The E64-T1 arm with E80's die line: 14.7 |
| **E83-R4** (a) beats (b) on the sustained rms | **PASS** | **14.3 against 23.4 MHz**. For the burst: 11.8 against 12.6 |
| **E83-R5** E80's anchors within 25 MHz | **PASS** | all ten rows; the largest is int8 zeros sustained, 788.8 against 800 (−11.2), a launch-ramp shortfall (§2) |
| **E83-S1** the relation on measured power, burst and sustained rms ≤ 15 MHz | **PASS** | burst **7.9** (5.5 reset-free), sustained **7.5 MHz** |
| **E83-S2** measured c inside Q130(c)'s 95% interval for ≥ 70% of the out-of-sample kinds | **FAIL** | **22 of 32** (69%). Eight gated kinds read above their narrow intervals: all three `a_*_b_zeros` / `a_zeros_b_*` pairs, fp16 and int8 wsparse90. Two read below: fp32 sparse50 (8.52 W against 8.88–12.65) and fp32 fp16grid (20.65 against 21.21–28.69) |
| **E83-S3** fp32 fp16grid and pow2 below Q130(c)'s point | **FAIL** | fp16grid **20.65 W** against 24.95 (below, as E80 found for bf16trunc); pow2 **15.06** against 14.39 (above) |

### 2. The speeds: what each kind of number gets on this card

The burst is the mean clock from 1.5 to 6.5 s of a 6 s run from a die reading ≤ 55 °C; both passes are given. The
sustained figure is the last 40 s of nine back-to-back 8 s processes, about 76 s in all. Rates are the kernel's own
operations over its own wall time. p800 is the board's power at 800 MHz in the first second after reaching it. c is the
kind's switching term at 600 MHz and 517 mV (E64's method, referred to a 58 °C die). The last column is **derived**:
board pJ per operation is the sustained board W over the sustained kernel rate, whole-board energy. From
[`tables.md`](tables.md):

| format | kind | burst MHz | burst rate | p800 W | burst limit | sustained MHz | sustained rate | board W | die °C | limit | c W | board pJ/op |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 | randn_small | 706.0 (704.2 / 707.8) | 10.64 TFLOPS | 83.4 | power | 600.5 | 9.21 TFLOPS | 54.0 | 66.3 | thermal | 25.75 | 5.86 |
| fp32 | randn_large | 703.0 (694.2 / 711.8) | 10.58 | 83.1 | power | 608.2 | 9.32 | 54.8 | 66.0 | thermal | 25.55 | 5.88 |
| fp32 | randn_sorted | 712.9 (717.6 / 708.2) | 10.75 | 80.3 | power | 603.1 | 9.25 | 52.8 | 66.0 | thermal | 24.32 | 5.71 |
| fp32 | uniform01 | 722.1 (732.0 / 712.2) | 10.90 | 78.6 | power | 627.6 | 9.56 | 55.2 | 65.8 | thermal | 23.50 | 5.77 |
| fp32 | fp16grid | 757.5 (766.0 / 749.0) | 11.45 | 72.3 | power | 648.7 | 9.84 | 54.6 | 65.6 | thermal | 20.65 | 5.55 |
| fp32 | pow2 | 800.0 (800 / 800) | 12.28 | 62.0 | none | 684.6 | 10.32 | 51.9 | 65.6 | thermal | 15.06 | 5.03 |
| fp32 | pi | 800.0 (800 / 800) | 12.28 | 51.6 | none | 780.1 | 11.90 | 53.3 | 64.9 | thermal | 9.82 | 4.47 |
| fp32 | neg_ones | 800.0 (800 / 800) | 12.27 | 51.4 | none | 767.3 | 11.65 | 52.0 | 65.1 | thermal | 9.63 | 4.46 |
| fp32 | ones | 800.0 (800 / 800) | 12.27 | 51.5 | none | 782.4 (771.7 / 793.1) | 11.94 | 53.3 | 65.0 | thermal / none | 9.60 | 4.47 |
| fp32 | sparse50 | 800.0 (800 / 800) | 12.28 | 48.6 | none | 793.6 (800.0 / 787.2) | 12.16 | 51.8 | 64.4 | none / thermal | 8.52 | 4.26 |
| fp32 | a_zeros_b_randn | 800.0 (800 / 800) | 12.28 | 35.3 | none | 795.4 | 12.20 | 36.7 | 57.0 | none | 2.41 | 3.01 |
| fp32 | a_randn_b_zeros | 800.0 (800 / 800) | 12.28 | 36.3 | none | 800.0 | 12.28 | 37.2 | 58.3 | none | 2.20 | 3.03 |
| fp32 | zeros | 800.0 (800 / 800) | 12.28 | 34.1 | none | 789.3 | 12.10 | 35.2 | 57.9 | none | 1.72 | 2.91 |
| fp16 | randn_small | 709.2 (720.4 / 698.0) | 21.51 TFLOPS | 77.9 | power | 614.3 | 18.79 TFLOPS | 52.8 | 65.9 | thermal | 23.10 | 2.81 |
| fp16 | randn_sorted | 734.0 (730.6 / 737.5) | 22.12 | 75.4 | power | 620.8 | 18.97 | 52.5 | 65.8 | thermal | 21.82 | 2.77 |
| fp16 | pair_half_zero | 737.7 (740.0 / 735.4) | 22.38 | 74.8 | power | 619.2 | 18.92 | 51.6 | 65.8 | thermal | 21.31 | 2.73 |
| fp16 | uniform01 | 769.2 (776.0 / 762.5) | 23.35 | 71.0 | power | 632.0 | 19.24 | 52.5 | 65.8 | thermal | 20.39 | 2.73 |
| fp16 | neg_ones | 800.0 (800 / 800) | 24.55 | 51.4 | none | 789.8 | 24.17 | 54.1 | 64.7 | none | 9.66 | 2.24 |
| fp16 | wsparse50 | 800.0 (800 / 800) | 24.55 | 48.2 | none | 793.9 (792.9 / 794.9) | 24.34 | 51.1 | 63.6 | none | 8.32 | 2.10 |
| fp16 | sparse90 | 800.0 (800 / 800) | 24.55 | 36.3 | none | 800.0 | 24.56 | 39.0 | 59.1 | none | 3.12 | 1.59 |
| fp16 | a_zeros_b_randn | 800.0 (800 / 800) | 24.55 | 35.4 | none | 794.4 | 24.38 | 36.7 | 57.0 | none | 2.53 | 1.50 |
| fp16 | wsparse90 | 800.0 (800 / 800) | 24.55 | 35.3 | none | 789.8 | 24.22 | 36.6 | 58.1 | none | 2.39 | 1.51 |
| fp16 | a_randn_b_zeros | 800.0 (800 / 800) | 24.55 | 35.9 | none | 794.9 | 24.39 | 36.9 | 58.3 | none | 2.20 | 1.51 |
| int8 | sorted | 775.5 (800.0 / 751.0) | 81.52 TOPS | 47.8 | none | 789.3 | 82.97 TOPS | 51.8 | 65.0 | none | 8.53 | 0.62 |
| int8 | pos | 800.0 (800 / 800) | 84.30 | 48.2 | none | 791.8 | 83.31 | 51.4 | 64.8 | none | 8.03 | 0.62 |
| int8 | ternary | 800.0 (800 / 800) | 84.30 | 46.2 | none | 797.2 (794.4 / 800.0) | 84.01 | 48.5 | 62.6 | none | 7.06 | 0.58 |
| int8 | highbit | 800.0 (800 / 800) | 84.31 | 41.4 | none | 789.8 | 83.08 | 44.0 | 61.9 | none | 5.51 | 0.53 |
| int8 | wsparse50 | 798.0 (796.1 / 800.0) | 84.31 | 42.2 | none | 789.7 | 83.16 | 43.7 | 61.4 | none | 4.67 | 0.53 |
| int8 | ones | 800.0 (800 / 800) | 84.30 | 39.2 | none | 800.0 | 84.32 | 40.5 | 59.0 | none | 3.75 | 0.48 |
| int8 | sparse90 | 800.0 (800 / 800) | 84.31 | 38.5 | none | 794.9 | 83.76 | 39.6 | 59.3 | none | 3.27 | 0.47 |
| int8 | wsparse90 | 779.1 (800.0 / 758.3) | 82.10 | 36.6 | none | 800.0 | 84.33 | 37.8 | 57.0 | none | 2.77 | 0.45 |
| int8 | a_zeros_b_full | 800.0 (800 / 800) | 84.30 | 36.2 | none | 794.9 | 83.74 | 37.1 | 57.2 | none | 2.58 | 0.44 |
| int8 | a_full_b_zeros | 800.0 (800 / 800) | 84.32 | 37.2 | none | 794.4 | 83.70 | 37.9 | 58.8 | none | 2.48 | 0.45 |

The anchors, as re-run here (E80's cells in brackets): fp32 randn burst 714.7 (711.9), sustained 612.0 (604.3); fp16
randn 724.8 (730.6) and 609.0 (609.5); int8 full 800 (800) and 786.5 (793.4); fp16 zeros 800 (800) and 800.0 (789.8);
int8 zeros 800 (800) and 788.8 (800). The all-51-kinds column, E80's 18 beside E83's 33, is the last table of
[`tables.md`](tables.md).

How to read it:

- **The two limits, again, for every kind.** On a cool die only the power test acts: the 11 kinds that stepped down
  in a burst (nine of the 33 and the two random anchors; p800 71.0–83.4 W) all logged a *power* step first, and none
  of the 76 bursts logged a thermal one first.
  In sustained work only the thermal test acts: no sustained run's last 40 s carries a single power label, and every
  kind that settles below 800 does so at a die mean of 64.9–66.3 °C and a board 51.6–55.3 W. (a)'s burst limit was
  right for all 33.
- **Speed by kind.** fp32 sustains 600–628 MHz on full-entropy data (any scale, sorted or not, uniform), 649 on
  fp16-rounded values, 685 on powers of two, 767–782 on constants, 794 on 50%-sparse words, and 789–800 when either
  operand is zero. fp16 sustains 609–632 on full-entropy data (the randn anchor included), uniform values and pairs
  with one half zero, and 790–800 on constants, word-sparse and gated data. **int8 holds 786–800 MHz sustained on all
  16 of its kinds** (E80's six and these ten): its most costly data draws about 52 W, right at the trip (int8 full's
  run here spent 13.5% of its last 40 s thermal-limited).
- **Cells (a) put at 800 read 788.8–800 sustained.** The shortfall is the governor's launch ramp, not a limit: on those
  17 runs (die means 57–65 °C, 35–51 W), 211 of the 225 samples below 800 in the window sit within 1.5 s after one of
  the nine process starts, where some processes begin at 600 MHz and take about 1.3 s to reach 800. On the four such
  runs checked, the trace ring logs a POWER_IDLE record at each of those starts.
- **The interval.** A burst cell is two independent passes, which agree to 0–22 MHz except where an idle reset fell in
  one (§5). A sustained cell is one run except the four replicates, whose two runs differ by 21.4 (fp32 ones), 12.8
  (fp32 sparse50), 5.6 (int8 ternary) and 2.0 MHz (fp16 wsparse50). Pooled with E80's three replicates, a single-run
  cell on the slope carries about ±11 MHz (the rms half-spread of the two replicated slope cells, fp16 ones and fp32
  ones) and a cell at or near a clamp (≤ 615 or ≥ 790 MHz) about ±4 MHz (five cells).

### 3. What the kind of number does to the power

From the measured switching term c (`results.json` `cells.*.c_w`), and as a **derived** share of random data's
switching over zeros in the same format, with this session's own zeros and random cells ([`tables.md`](tables.md),
"share of random's switching"):

- **The value of a constant hardly matters.** fp32 ones 9.60 W, neg_ones 9.63, pi (0x40490FDB, many 1 bits) 9.82; fp16
  neg_ones 9.66 against E80's fp16 ones 9.70. A constant costs a third of random data's switching in fp32 and fp16
  (0.33–0.37). int8 ones costs 0.21.
- **The scale of the numbers does not matter.** fp32 normal data with σ 2⁻¹⁰, 1 and 2¹⁰: 25.75, 25.59 and 25.55 W
  (shares 1.007, 1.000 and 0.998); fp16 with σ 2⁻⁶: 23.10 against 23.05. Only the bits that change cost.
- **Fewer random mantissa bits cost less.** fp32 rounded to the fp16 grid (the low 13 mantissa bits zero) costs 0.79
  of random: 20.65 W, worth 43 MHz of burst clock and 37 MHz of sustained clock. E80's bf16 truncation (16 bits zero)
  cost 0.73. Powers of two (all 23 mantissa bits zero, the exponent spread over 17 values) still cost 0.56.
- **Reordering the same numbers saves 5–7% in every format.** `randn_sorted`, `sorted`: the tile's own words permuted
  into a low-toggle stream order cost 0.947 (fp32), 0.942 (fp16) and 0.932 (int8) of the unsorted tile's switching.
- **Restricting the range saves little.** uniform [0, 1) costs 0.91 (fp32) and 0.88 (fp16); int8 0..127 (the sign
  always 0) costs 0.86.
- **A zero on either side gates the lane, almost for free.** One operand all zero, the other random: 0.02–0.04 of
  random in all three formats, or 0.1–0.8 W above zeros. With the broadcast side (A) zero and B random, each format
  reads 0.10–0.33 W above the reverse orientation, but that is within its two passes' spread (up to 0.31 W), so the
  orientation is not resolved.
- **Zero words gate, zero halves do not.** fp16 with half its 32-bit words zero costs 0.31; E80's fp16 with half its
  elements zero cost 0.61; fp16 pairs with exactly one half zero cost 0.92, as much as random data almost. At 90%:
  word-sparse 0.031, element-sparse 0.065 (fp16); int8 0.063 and 0.138. fp32 elements are words, and fp32 sparse50
  costs 0.29, less than a constant.
- **int8:** ternary weights (−1, 0, +1) cost 0.71, ±64 with the sign changing 0.48.

### 4. The heat path did not move between E80 and E83

The die line over E83's 42 sustained runs is **die = 40.76 + 0.4631 °C per W** (rms 0.70 °C,
`results.json` `posthoc.die_line_e83`). At E80's slope it sits **0.15 °C below E80's line**, and it reaches 65.5 °C at
**53.4 W** against E80's 53.5. The arm (a-adj) measured the drift on the five anchors as +0.01 °C, moved W* by 0.03 W,
and scored 14.3 MHz like (a). So a relation measured at 12:22–13:02 held at 13:47–15:08, and the sustained rules
passed. Across 8 days, by contrast, E80 found the line 1.38 °C lower than on 23 October.

### 5. The idle reset, again

Seven times in 454 work processes (1.5%), the clock fell from 800 MHz straight to 600 MHz while the work ran on: in
three bursts (fp32 randn_large pass 1, int8 wsparse90 pass 2, int8 sorted pass 2) and four sustained runs (int8
a_zeros_b_full, int8 highbit, fp32 a_zeros_b_randn, int8 pos). E80 counted 5 in 225 (2.2%); E63 8 in 360. Each of
the seven has a power-status record in throttle state 0 (POWER_IDLE) in the trace ring, within 0.05 s of the sampler's
fall for six of them (int8 wsparse90's sits 1.3 s earlier on the ring's clock), as E80 found; the fp32 randn_large one
came 50 ms after a power step. It costs a burst pass up to 49 MHz (int8 sorted, 751.0 against 800).
Without those samples (A1's view, labelled) the burst rms is 10.3 MHz and the relation-only burst rms 5.5 MHz.

### 6. Predicted against measured: where the misses come from

The full table, with each arm, is in [`tables.md`](tables.md) ("Predicted against measured"). The largest sustained
misses of (a) are the power model's, not the relation's:

| kind | sustained measured | (a) | miss | c measured | c predicted | the relation on measured c |
|---|---|---|---|---|---|---|
| fp32 fp16grid | 648.7 | 603.8 | +44.9 | 20.65 | 24.95 | 632.7 |
| fp32 sparse50 | 793.6 | 759.2 | +34.4 | 8.52 | 10.77 | 791.5 |
| fp16 uniform01 | 632.0 | 664.3 | −32.3 | 20.39 | 17.82 | 635.2 |
| fp16 wsparse50 | 793.9 | 767.0 | +26.9 | 8.32 | 10.27 | 793.3 |
| fp32 pow2 | 684.6 | 708.8 | −24.2 | 15.06 | 14.39 | 700.2 |

On the measured c the relation's worst sustained cells are fp32 uniform01 (+17.6), fp32 fp16grid (+16.0) and fp32
pow2 (−15.6); its worst burst cells are the two idle-reset passes and fp16 randn_small (−22.7: its passes, 720.4 and
698.0, began at 54 and 56 °C). Q130(c)'s own sustained clocks (b) miss most on the kinds near the trip, by +29 to
+66 MHz (fp32 sparse50, fp16 wsparse50, fp32 fp16grid, fp16 neg_ones, fp32 ones and pi, int8 ternary): its 23 October
heat path puts the cap 3 W too low, as E80 found, and its power for fp16grid and sparse50 is 2–4 W high.

## What it changes

**For the blog's kinds table:** every cell of burst MHz, sustained MHz, TFLOPS/TOPS, board W, die °C and the limiting
test for the 33 kinds, on one card in one session ([`cells.json`](cells.json)). With E80's 18, the speed column is
measured for all 51 kinds, and it is no longer a prediction anywhere.

**For the explanation:**

1. **What sets a matmul's speed is its power, and the kind of number sets the power.** One relation, fitted on 18
   kinds, turns each of 33 new kinds' measured power into its burst clock to 7.9 MHz and its sustained clock to
   7.5 MHz rms. Two kinds with the same power get the same clock, to within about 8 MHz, whatever the numbers are.
2. **The two limits hold for all 51 kinds:** power on a cool die, heat in sustained work.
3. **Only changing bits cost.** Scale costs nothing, a constant's value almost nothing, and zeros on one side almost
   nothing; truncated mantissas, sorted streams and restricted ranges save 5–21%.
4. **A sustained prediction needs that day's heat path.** Measured the same afternoon, it closes to 14 MHz rms on new
   kinds; carried from another week, it misses by 23 MHz rms.

**For the Horace hub:** Status "fp16 and int8" and the remaining kinds: measured, all 51. Levels stop 1 ("a temperature
term that closes"): out of sample now, with the heat path measured the same day before scoring (E83-R3 14.3 MHz,
E83-S1 7.5 MHz on measured power). The open part moves to the power model: the gated lanes' residual (0.1–0.8 W) and
pow2, uniform01 and fp16grid, which E78's pinned-clock matrix can calibrate.

## Card state and etiquette

- aifoundry2 card 0, release 1.4.0 / BL2 0.22.0 (E69's reading); `et-lab-manifest` in `s1/manifest.txt` (kernel module
  0.20.0, clock sync normal).
- At the start, `et-who` read *"No process holds an ET-SoC-1 device node or card lock"*, `who` showed no logins, and the
  die idled at 46 °C at 21.9 W.
- The runner held the card lock for each session. The lab dashboard's collector and keeper kept to it, as with E64,
  E69 and E80; nothing of theirs was stopped.
- The final read-only `ettelem config` under the lock, at about 15:08, gave `tdp_w 65`, `temp_threshold_c 65`,
  `low_power`, 600 MHz, 519 mV. `et-who` was free afterwards.
- Safety stops: none. The hottest die reading was 67 °C and the highest board sample 88.9 W, against stops of 85 °C and
  97 W.
- The box's lab checkout was fast-forwarded from `10f58581` to `c253bd1c`, and every file the session ran was checked
  by sha256 against the Intel's before the claim (`s1/kspeed.json`, `s1/e83.json`, `s1/session.json`).

## Departures, dated

- **None from the registered design.** All 118 runs ran in the registered order; no amendment was written.
- **Labelled additions, after the data:** the derived share table and the all-51 table in `tables.py` (formatting
  only), and the launch-ramp count of §2 (211 of 225 samples), read from `results.json` `runs.*.trace` and
  `proc_spans`. Neither changes a number in a rule.

## Files

| path | what |
|---|---|
| `s1/`, `smoke/` | the sessions as run (E64's layout): `session.json`, `kspeed.json` (every tile's sha256), `e83.json` (the wrapper's and the predictions' sha256), `runs.jsonl`, `launches.jsonl.gz`, `tel/<run>.jsonl.gz` (10 Hz, no `--reset-ms`), `sp/<run>.bin` (the trace ring, read with `tools/claims-v3/hpl/sptrace_full.py`), `queries.jsonl`, `marks.jsonl`, `manifest.txt`, `run.log`, `run.out`, `end.json` |
| `results.json`, `reduce.txt` | `reduce_e83.py`: per-run metrics (E64's `reduce_hpl.run_metrics`, E80's `burst_extra` and `sus_limit`, A1's `flags`), per-kind cells, every rule, the labelled arms |
| `tables.py`, `tables.md`, `cells.json` | formatting only: the README's tables, the derived share table, the all-51 speed column and the blog's kinds-table cells |

Rebuild (any machine with Python 3; no third-party modules):

```bash
cd docs/reports/data/2026-10-31-e83-kinds-speed-rest
python3 ../../../../tools/claims-v3/kspeed/e83/reduce_e83.py s1 --out results.json > reduce.txt
python3 tables.py results.json ../../../../tools/claims-v3/kspeed/e83/predictions.json \
    ../2026-10-31-e80-kinds-speed/results.json --cells cells.json > tables.md
```
