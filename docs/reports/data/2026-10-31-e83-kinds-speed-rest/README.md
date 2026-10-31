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
in `#community-lab` at 13:45:55 and released by editing the same post at 15:08. No amendment was made. The lane
looked twice at partial data while the session ran (14:06 and 14:26) and changed nothing on either look; that is
disclosed under Departures (D2). An independent verifier re-derived every registered number; the text it found wrong is
corrected in place, listed at the end (Corrections after verification), and no number or verdict changed.

| session | PDT | what |
|---|---|---|
| `smoke/` | 13:46:04–13:46:25 | three 2 s `file:` launches of new tiles (fp32 a_zeros_b_randn, fp16 pair_half_zero, int8 highbit): 546.0 / 546.0 / 318.0 cycles per op, config 65 W / 65 °C; not analysed |
| `s1/` | 13:46:47–15:07:37 | the registered session, 118 runs, exit 0, **80.8 card-minutes** (81.1 with the smoke, of the 100 allowed): `BURST` 76 runs (13:46–14:02), `SUS` 42 runs (14:02–15:07) |

## Results first

### 1. Six of the eight registered rules pass

**The chain kind → watts → clock now works in both regimes.** E80's own measured relation between a kind's power and
its clock, fed Q130(c)'s predicted power for kinds it never saw, hit the 33 burst clocks to **11.8 MHz rms** and the 33
sustained clocks to **14.3 MHz rms**, and called 29 of the 33 sustained limits. Those two figures include the cells it
puts at the 800 MHz cap (24 bursts, 15 sustained), which the cap makes easy: on the kinds it puts below 800 they are
**19.8 MHz** (9 bursts) and **18.3 MHz** (18 sustained). On each kind's own measured power the same relation reproduces
the clocks to **7.9 and 7.5 MHz** (10.6 and 8.4 on those kinds, post hoc). Q130(c)'s own frozen clocks, which used
23 October's heat path, miss the sustained cells by 23.4 MHz rms (31.1 on those 18;
[`corrections-check.txt`](corrections-check.txt) C4).

**What fails is the power model**: it says a lane gated by a zero operand costs exactly what zeros cost (it costs
0.1–0.8 W more), it over-charges fp32 `sparse50` and `fp16grid`, and it under-charges fp32 `pow2`. Each verdict is scored exactly as registered
([`results.json`](results.json) `rules`, [`reduce.txt`](reduce.txt)).

| rule | verdict | what the data say |
|---|---|---|
| **E83-R1** burst rms ≤ 25 MHz, (a) on Q130(c)'s power | **PASS** | **11.8 MHz** over the 33. Over the nine kinds (a) puts below 800, 19.8; on A1's reset-free cells 10.3. Q130(c)'s own 4–12 s numbers: 12.6 (21.6 on the nine); E64's governor on Q130(c)'s power: 12.4 |
| **E83-R2** sustained limit right for ≥ 80% | **PASS** | **29 of 33** (88%). The four misses are the kinds (a) put on the knife-edge, share at 800 predicted 0.59–0.76: fp32 ones and fp32 sparse50 (one run `none`, one `thermal`), fp16 neg_ones and fp16 wsparse50 (`none`, predicted `thermal`). Q130(c)'s two-way call: 27 of 33 |
| **E83-R3** sustained rms ≤ 25 MHz, (a) on Q130(c)'s power | **PASS** | **14.3 MHz**; 18.3 over the 18 kinds (a) puts below 800. The E64-T1 arm with E80's die line: 14.7 |
| **E83-R4** (a) beats (b) on the sustained rms | **PASS** | **14.3 against 23.4 MHz**; on the 18 kinds (a) puts below 800, 18.3 against 31.1 (post hoc). For the burst: 11.8 against 12.6 |
| **E83-R5** E80's anchors within 25 MHz | **PASS** | all ten rows; the largest is int8 zeros sustained, 788.8 against 800 (−11.2), a launch-ramp shortfall (§2) |
| **E83-S1** the relation on measured power, burst and sustained rms ≤ 15 MHz | **PASS** | burst **7.9** (5.5 reset-free), sustained **7.5 MHz**; on the kinds (a) puts below 800, 10.6 (9 kinds) and 8.4 MHz (18), post hoc ([`corrections-check.txt`](corrections-check.txt) C4) |
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

- **The two limits, again, for every kind.** On a cool die only the power test acts as a limit: the 11 kinds that
  stepped down in a burst (nine of the 33 and the two random anchors; p800 71.0–83.4 W) all logged a *power* step
  first, and none of the 76 bursts logged a thermal one first. The governor's idle reset (§5), which is not a limit,
  also dropped three burst passes straight to 600 MHz on a cool die.
  In sustained work only the thermal test acts: no sustained run's last 40 s carries a single power label, and every
  kind that settles below 800 does so at a die mean of 64.9–66.3 °C and a board 51.6–55.3 W. (a)'s burst limit was
  right for all 33.
- **Speed by kind.** fp32 sustains 600–628 MHz on full-entropy data (any scale, sorted or not, uniform), 649 on
  fp16-rounded values, 685 on powers of two, 767–782 on constants, 794 on 50%-sparse words, and 789–800 when either
  operand is zero. fp16 sustains 609–632 on full-entropy data (the randn anchor included), uniform values and pairs
  with one half zero, and 790–800 on constants, word-sparse and gated data. **int8 holds 786–800 MHz sustained on all
  16 of its kinds** (E80's six and these ten): its most costly data draws about 52 W, right at the trip (int8 full's
  run here spent 13.5% of its last 40 s thermal-limited). Its bursts read 800 MHz in 27 of the 16 kinds' 32 passes and
  796 in two (E80's smallint, this session's wsparse50). The other three, 751–758 MHz, are passes the idle reset hit
  (E80's neg_ones, this session's wsparse90 and sorted; [`corrections-check.txt`](corrections-check.txt) C9).
- **Cells (a) put at 800 read 788.8–800 sustained.** The shortfall is the governor's launch ramp, not a limit: on those
  17 runs (die means 57–65 °C, 35–51 W), 190 of the 204 readings below 800 in the registered window (the in-kernel
  readings of the last 40 s) sit within 1.5 s after one of the nine process starts, where some processes begin at
  600 MHz and take about 1.3 s to reach 800. Counting every reading of the last 40 s, the gaps between processes
  included, it is 211 of 225 ([`corrections-check.txt`](corrections-check.txt) C9). On the four such runs checked, the
  trace ring logs a POWER_IDLE record at each of those starts.
- **The interval.** A burst cell is two passes, run in two rounds: all 38 pass-1 bursts first, then all 38 pass-2
  bursts. They agree to 0–22 MHz except where an idle reset fell in one (§5), but they are not exchangeable
  replicates. Pass 2 launched from a die 1.3 °C warmer on average (54.55 against 53.24 °C), and on the ten
  power-limited kinds without an idle reset it ran 7.9 MHz slower (sd 10.6 MHz, t −2.35 on 9 df). So a burst pair's
  spread includes a pass-order effect of about 8 MHz on power-limited kinds. The random part is about 7.5 MHz per
  pass: 5.3 MHz for a cell's mean, and 7.5 MHz for a difference of two cells, where the order effect cancels.
  A sustained cell is one run, except the four replicates, whose two runs differ by 21.4 (fp32 ones), 12.8 (fp32
  sparse50), 5.6 (int8 ternary) and 2.0 MHz (fp16 wsparse50). Pooled with E80's three replicates, one run's 1σ is
  √2 times the rms half-spread of the pairs, since a pair's half-spread is each run's deviation from the pair's mean,
  σ/√2:
  - **±15.6 MHz on the slope.** Only two pairs sit there, and both are knife-edge cells (fp16 ones, fp32 ones), picked
    for replication because they sit at the edge of their limit class. That is 2 degrees of freedom, and probably
    high for a cell away from the edge: on the eight single-run slope cells, the out-of-sample S1 residual is
    11.2 MHz rms, noise and model error together.
  - **±5.6 MHz at or near a clamp** (≤ 615 or ≥ 790 MHz; five pairs).
  - **±0.8 W** of board power and **±0.8 °C** of die, over all seven pairs.

  These replace the ±11 and ±4 MHz given here before, which were the half-spreads themselves
  ([`corrections-check.txt`](corrections-check.txt) C3, C6).

### 3. What the kind of number does to the power

From the measured switching term c (`results.json` `cells.*.c_w`), and as a **derived** share of random data's
switching over zeros in the same format, with this session's own zeros and random cells ([`tables.md`](tables.md),
"share of random's switching").

The c watts below are not the power a kind draws while it runs. c is whole-board switching at 600 MHz and 517 mV,
referred to a 58 °C die, and it is measured over E64's fitted baseline B_f, not over idle. B_f is 25.46 / 28.24 /
33.61 W at 600 / 700 / 800 MHz, and each format's zeros read 1.72–2.36 W on it. At 700 and 800 MHz the same data
switch s_f = 1.41 and 1.91 times as much, so random fp32's c of 25.59 W stands for 48.8 W of switching at 800 MHz
([`corrections-check.txt`](corrections-check.txt) C2). The shares need none of this, which is why the blog quotes them
first.

- **The value of a constant hardly matters.** fp32 ones 9.60 W, neg_ones 9.63, pi (0x40490FDB, many 1 bits) 9.82; fp16
  neg_ones 9.66 against E80's fp16 ones 9.70. A constant costs a third of random data's switching in fp32 and fp16
  (0.33–0.37). int8 ones costs 0.21.
- **The scale of the numbers does not matter.** fp32 normal data with σ 2⁻¹⁰, 1 and 2¹⁰: 25.75, 25.59 and 25.55 W
  (shares 1.007, 1.000 and 0.998); fp16 with σ 2⁻⁶: 23.10 against 23.05. Only the bits that change cost.
- **Fewer random mantissa bits cost less.** fp32 rounded to the fp16 grid (the low 13 mantissa bits zero) costs 0.79
  of random: 20.65 W. Against this session's random fp32 that is worth 43 ± 7.5 MHz of burst clock and 37 ± 16.5 MHz
  of sustained clock (1σ; one sustained run each, one on the slope and one at the 600 MHz clamp; C3). E80's bf16
  truncation (16 bits zero) cost 0.73. Powers of two (all 23 mantissa bits zero, the exponent spread over 17 values)
  still cost 0.56.
- **Reordering the same numbers saves 5–7% in every format.** `randn_sorted`, `sorted`: the tile's own words permuted
  into a low-toggle stream order cost 0.947 (fp32), 0.942 (fp16) and 0.932 (int8) of the unsorted tile's switching.
- **Restricting the range saves little.** uniform [0, 1) costs 0.91 (fp32) and 0.88 (fp16); int8 0..127 (the sign
  always 0) costs 0.86.
- **A zero on either side gates the lane, almost for free.** One operand all zero, the other random: 0.02–0.04 of
  random in all three formats, or 0.1–0.8 W above zeros.
- **Which side is zero is not resolved.** With the broadcast side (A) zero and B random, each format reads more than
  the reverse orientation: +0.21 W (fp32), +0.33 W (fp16) and +0.10 W (int8). The sign is the same in all three, and
  in fp32 and fp16 the two passes do not overlap. With two passes each, none of the three is significant (pooled t
  1.5, 2.1 and 1.3 on 2 df; two-sided p 0.27, 0.17 and 0.34), and three of three by chance has p 0.25
  ([`corrections-check.txt`](corrections-check.txt) C5).
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
   7.5 MHz rms. On the kinds whose clock is free to move, below the 800 MHz cap, that is 10.6 MHz (9 bursts) and
   8.4 MHz (18 sustained cells). Two kinds with the same power get the same clock, to within about 8–11 MHz, whatever
   the numbers are.
2. **The two limits hold for all 51 kinds:** power on a cool die, heat in sustained work.
3. **Only changing bits cost.** Scale costs nothing, a constant's value almost nothing, and zeros on one side almost
   nothing; truncated mantissas, sorted streams and restricted ranges save 5–21%.
4. **A sustained prediction needs that day's heat path.** Measured the same afternoon, it closes to 14 MHz rms on new
   kinds (18 MHz on the 18 below the cap). Carried from another week, it misses by 23 MHz rms (31 MHz on those 18).

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
- **Timeouts.** Every launch and every `ettelem config` read ran under `timeout 10`. The 10 Hz sampler did not, by
  E64's design: it starts as `ettelem sample --seconds <plan + 900>` and runs for the whole run (`run_hpl.py`
  `run_one`). At the end of every run the runner stops it with SIGTERM. `ettelem` catches that, finishes the reading
  in flight and exits 0 (`tools/ettelem/ettelem.cpp`, above `sample()`). The runner sends SIGKILL and one
  management-queue drain only if a sampler ignores SIGTERM for 30 s. All 121 samplers (3 in the smoke, 118 in the
  session) started on attempt 1 and stopped 6.4–106.1 s later, each with rc 0. `marks.jsonl` has no `error` mark, no
  SIGKILL and no drain ([`corrections-check.txt`](corrections-check.txt) C8). The pre-registration's "it caps every
  device process at `timeout 10` and never signals one" was wrong about the sampler (D3).

## Departures, dated

- **D1 — none from the registered design.** All 118 runs ran in the registered order; no amendment was written.
- **D2 — two interim looks at partial data, not registered (Sat 31 Oct, 14:06 and 14:26 PDT; disclosed after
  verification, C1).**
  - *What the lane did.* While the session ran, it twice copied the box's `s1/` directory to its scratch on the
    Intel (rsync over ssh) and ran the registered `reduce_e83.py` on the copy.
  - *First look, issued 14:06:39.* The copy held 78 runs: all 76 bursts and two sustained runs. The lane read the
    burst cells and E83-R1, S2 and S3. Those three depend only on the bursts (c comes from the burst powers), so their
    verdicts were known from then.
  - *Second look, issued 14:26:17.* The copy held 90 runs, 14 of them sustained. The lane read the sustained cells so
    far; R2–R4 and the sustained half of S1 were still incomplete. `tables.py` (formatting only) was drafted on this
    copy at 14:28.
  - *Nothing was changed or decided on either look.* The session ran all 118 runs in its frozen order (seed 83), and
    no amendment was written. The runner, protocol, predictions and reducers that ran are the registered files by
    sha256: the hashes the session recorded, and those at `c253bd1c`.
  - *What the copies overlapped.* Each copy's few seconds of box I/O fell inside the last-40-s window of the run then
    in progress:
    - fp32 pow2 (SUS-09): its 10 s from the copy read 691.8 MHz, against 682.2 for the rest of its window. Without
      those 10 s its cell, 684.6 MHz, would read 682.2.
    - fp32 a_randn_b_zeros (SUS-11): the copy came 1.7 s before the window ended, at 800 MHz throughout.

  Neither copy slowed a cell ([`corrections-check.txt`](corrections-check.txt) C1). The copy times are the lane's own
  command log; the second copy's telemetry ends at 14:26:18.8, which dates its transfer.
- **D3 — the runner's timeouts were described wrongly at registration (inherited, as E80's C9; corrected after
  verification, C8).** The sampler runs outside `timeout 10` and is stopped by SIGTERM; Card state says how, and that
  none needed more.
- **Labelled additions, after the data:**
  - the derived share table and the all-51 table in `tables.py` (formatting only);
  - the launch-ramp count of §2, read from `results.json` `runs.*.trace` and `proc_spans`;
  - after verification: `corrections-check.py` and the uncertainty-only `interval` in `cells.json` (C3, C7).

  None of them changes a number in a rule.

## Files

| path | what |
|---|---|
| `s1/`, `smoke/` | the sessions as run (E64's layout): `session.json`, `kspeed.json` (every tile's sha256), `e83.json` (the wrapper's and the predictions' sha256), `runs.jsonl`, `launches.jsonl.gz`, `tel/<run>.jsonl.gz` (10 Hz, no `--reset-ms`), `sp/<run>.bin` (the trace ring, read with `tools/claims-v3/hpl/sptrace_full.py`), `queries.jsonl`, `marks.jsonl`, `manifest.txt`, `run.log`, `run.out`, `end.json` |
| `results.json`, `reduce.txt` | `reduce_e83.py`: per-run metrics (E64's `reduce_hpl.run_metrics`, E80's `burst_extra` and `sus_limit`, A1's `flags`), per-kind cells, every rule, the labelled arms |
| `tables.py`, `tables.md`, `cells.json` | formatting only: the README's tables, the derived share table, the all-51 speed column and the blog's kinds-table cells. In `cells.json`, `interval` holds only an uncertainty since the corrections (C7) |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind the corrections after verification: every number they quote, from the committed session and reductions, and C1's code-identity check |

Rebuild (any machine with Python 3; no third-party modules):

```bash
cd docs/reports/data/2026-10-31-e83-kinds-speed-rest
python3 ../../../../tools/claims-v3/kspeed/e83/reduce_e83.py s1 --out results.json > reduce.txt
python3 tables.py results.json ../../../../tools/claims-v3/kspeed/e83/predictions.json \
    ../2026-10-31-e80-kinds-speed/results.json --cells cells.json > tables.md
python3 corrections-check.py > corrections-check.txt
```

## Corrections after verification (Sat 31 Oct 2026)

An independent verifier checked E83 after the data commit. It re-derived every registered number from the raw
telemetry with its own code, and it reproduced `predictions.json`, `results.json` and `reduce.txt` byte for byte. It
found nine minor faults in how the numbers were stated. Each is corrected above, desk only: no card was touched,
nothing was re-run, and no registered prediction, rule, number or verdict changed. The verdicts stay R1–R5 and S1 PASS,
S2 and S3 FAIL. Every number below is printed by [`corrections-check.py`](corrections-check.py) into
[`corrections-check.txt`](corrections-check.txt), under the section named.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **The interim looks were not disclosed.** There were two: at 14:06:39 (78 runs) and at 14:26:17 (90 runs). The verifier found both copies and the second reduction; the first reduction is in the lane's own command log | Departures D2 says what was read, that nothing was changed or decided, that the code that ran is the code registered, and what each copy overlapped: neither slowed a cell |
| C2 | **c was quoted as bare watts** in the blog points this lane handed on. It is a switching term at 600 MHz and 517 mV over E64's fitted baseline, not the power drawn at 700–800 MHz | §3 says what c is, gives B_f, the zeros level on it and the s_f factors, and leads with the shares; the corrected blog points do too, with c qualified. `cells.json`'s c unit says the same |
| C3 | **One sustained run's interval was √2 too small.** §2 gave the replicate pairs' rms half-spread (±11 / ±4 MHz), which estimates σ/√2 | §2 gives σ for one run: ±15.6 MHz on the slope (two knife-edge pairs, 2 df), ±5.6 MHz at a clamp (five pairs), ±0.8 W and ±0.8 °C. §3's fp16grid gains carry their uncertainty |
| C4 | **The rms figures in the summary leaned on capped cells.** 24 of the 33 bursts and 15 of the 33 sustained cells sit at the 800 MHz cap in (a) | §1 and What it changes give the rms on the kinds (a) puts below 800 beside the 33-kind figure: R1 19.8, R3 18.3, (b) 21.6 and 31.1, S1 10.6 and 8.4 MHz |
| C5 | **The orientation effect was "within its two passes' spread".** In fp16 the difference, 0.33 W, exceeds the largest pass spread, 0.31 W. In fp32 and fp16 the passes do not overlap | §3: the same sign in all three formats (+0.21 / +0.33 / +0.10 W), and not significant with two passes each |
| C6 | **The burst passes were called "two independent passes".** All pass-1 bursts ran before all pass-2 bursts. Pass 2 launched 1.3 °C warmer and, on the ten power-limited kinds without a reset, ran 7.9 MHz slower | §2's interval bullet, and `cells.json`'s burst cells, name the pass-order effect |
| C7 | **`interval` held other quantities** in the returned table cells and in `cells.json`: "one run", the wall-clock rate, the per-pass first-down lines and the label shares | `interval` now holds only the runs or one run's σ. The limits have none, and the other strings moved to `unit` or `conditions` (`tables.py`). `tables.md` is byte-identical |
| C8 | **The pre-registration said the runner "never signals" a device process.** The sampler runs outside `timeout 10` and is stopped with SIGTERM | Card state and Departures D3 say how. All 121 exited rc 0 after the SIGTERM. A dated note is in the tool README |
| C9 | **Three phrases were imprecise** (in the blog points, and the third in §2). "Only the power test ever stepped the clock down": the idle reset also dropped three cool-die passes. "int8 bursts at 800 apart from idle-reset passes": two int8 passes read 796 without a reset. The launch-ramp count gave no window | §2 says "acts as a limit", names the idle reset, and gives int8's burst passes: 27 of 32 at 800, two at 796, three hit by the idle reset. The ramp count is 190 of 204 in the registered window (211 of 225 over every reading) |

Two of the verifier's proposed fixes were not taken as written:

- **C4: the slope rms goes in `corrections-check.txt`, not `results.json`.** `results.json` is the registered reducer's
  output, and the verifier itself reproduced it byte for byte from `s1/`. A hand-added entry would break that check.
- **C8: the samplers did not exit "on their own `--seconds` bound".** The bound is the run's plan plus 900 s, so it
  never came within 13 minutes of acting. Every run ended its sampler 6.4–106.1 s after it started, by SIGTERM, which
  `ettelem` handles by exiting 0.
