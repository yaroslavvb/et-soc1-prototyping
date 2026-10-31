# E80 data: the speed of each kind of number under aifoundry2's own governor (Q130, Sat 31 Oct 2026)

Eighteen kinds of numbers on aifoundry2 card 0, under the card's own governor:

- fp16: zeros, ones, randn, sparse50, smallint, fp8grid, nn_like;
- int8: zeros, neg_ones, full, smallint, gauss_q, sparse50;
- fp32: randn, bf16trunc, sparse90, smallint, nn_like.

Each kind got a **burst on a cool die**, run twice, and a **sustained run** of about 76 s. **Nothing was set on the
card**: the TDP and the threshold read 65 W and 65 °C at all 57 per-run reads of `ettelem config` (and the smoke's
three), at the session's start and end, and once more at the close under the card lock, just before the release.

The pre-registration is [`tools/claims-v3/kspeed/`](../../../../tools/claims-v3/kspeed/README.md) (`10f58581`,
pushed 12:20:43 PDT). Its frozen predictions are
[`predictions.json`](../../../../tools/claims-v3/kspeed/predictions.json), sha256 `69a62b31…`, built from Q130(c)'s
freeze (`2bbe03dd`) and amendment A1 (`320f3fdd`) and the kinds spec (`7d9c0d9e`). E80's own amendment A1 (`075b691e`,
12:34:36) was written during the sustained block. The card was claimed in `#community-lab` at 12:21:13 and released by
editing the same post at 13:03.

*Corrected the same day, after verification (desk only; nothing re-run, no registered number or verdict changed):
see [Corrections after verification](#corrections-after-verification-sat-31-oct-2026) at the end. The main one: int8
full-range random data did throttle in sustained work; its `none` label is the registered ≥ 90%-at-800 rule.*

| session | PDT | what |
|---|---|---|
| `smoke/` | 12:21:30–12:21:51 | three 2 s `file:` launches (fp16 ones, int8 full, fp32 randn): cycles per op 546.0 / 318.0 / 546.0, config 65 W / 65 °C; not analysed |
| `s1/` | 12:22:12–13:02:42 | the registered session, 57 runs, exit 0, **40.5 card-minutes** (40.8 with the smoke, of the 90 allowed): `BURST` 36 runs (12:22–12:29), `SUS` 21 runs (12:29–13:02) |

## Results first

### 1. One registered rule of nine passes

**What passes.** The cool-die burst prediction (E80-R1): kind → predicted watts → E64's governor holds within E69's
25 MHz bar.

**What fails.** Every sustained rule, the power check on aifoundry2 (S1), and the two that hang on the governor's
idle-reset glitch (R7's 800 MHz clause, and S2).

- **The card's heat path moved** since E64's 23 Oct session. This matters most: it moved the cells that sit near the
  thermal trip.
- The **power model over-predicts the low-entropy fp32 kinds**.
- The governor's **idle reset fired inside two bursts**.

Each failure is scored exactly as E80 registered it ([`results.json`](results.json) `rules`,
[`reduce.txt`](reduce.txt)). Q130(c)'s R7 and R8 depart in two ways from what Q130(c) itself registered; both are
named under Departures.

| rule | verdict | what the data say |
|---|---|---|
| **E80-R1** burst rms ≤ 25 MHz, against E64's registered governor fed Q130(c)'s predicted watts | **PASS** | **21.7 MHz** over 18 kinds. Eight of the 18 are predicted and measured at the 800 MHz cap; over the other 10 the rms is 29.2 MHz ([`corrections-check.txt`](corrections-check.txt) C3). Against E64-T1's burst it is 28.1, and against Q130(c)'s own 4–12 s numbers 27.0 |
| **E80-R2** the sustained limit (none / thermal / power) called right for ≥ 80% of kinds | **FAIL** | 13 of 18 (72%). Four int8 kinds (full, smallint, gauss_q, sparse50) were predicted thermal and held 789–797 MHz, `none`. That label is the registered ≥ 90%-at-800 rule: the thermal test still stepped int8 full down 6 and 7 times (§2). fp16 ones was predicted thermal: one run read `none` (with two thermal steps), one `thermal`. All 13 others were right |
| **E80-R3** fp16 ones sustained within 15 MHz of E64-T1 | **FAIL** | **781.6 MHz** (792.9 and 770.3), against **745.2** predicted: **+36.4 MHz**. E64 measured 737.1 on 23 Oct; E64-T1's out-of-sample number was 754.5 |
| **E80-R4** E64's own cells within 25 MHz (the drift check) | **FAIL** | the fp32 randn burst +2.1 MHz; sustained fp32 randn +4.3, fp16 zeros −4.6, fp16 randn +9.0, int8 zeros 0.0. But **fp16 ones +44.5** and **int8 full +30.2**: the two cells inside the clamp window |
| **R7** (Q130(c)) burst within 25 MHz for ≥ 70%, and every predicted-800 cell ≥ 790 | **FAIL** | 13 of 18 within 25 MHz (72%, passes), but int8 neg_ones read 777.5 (755.1 and 800). The 755.1 pass was an idle reset (§3d). Q130(c)'s numbers are 4–12 s means, scored against E80's 1.5–6.5 s window (Departures) |
| **R8** (Q130(c)) sustained thermal-vs-power right for every cell, and within 40 MHz for ≥ 70% | **FAIL** | 13 of 18 limits right (the five R2 misses); 13 of 18 within 40 MHz (72%, passes). Scored on the frozen die line, which Q130(c) asked E80 to re-read first (Departures) |
| **E80-S1** measured switching term c inside the converted 95% interval for ≥ 70% of out-of-sample kinds | **FAIL** | 8 of 12. **All four fp32 kinds fell outside**, three below and one above: bf16trunc 19.11 W (predicted 24.27, interval 20.70–27.85), smallint 15.18 (18.52, 16.07–20.96) and nn_like 14.04 (17.15, 14.24–20.06) below; sparse90 2.23 (1.89, 1.57–2.20) above, by 0.03 W, and one of its two passes (2.195 W) is inside. All eight fp16 and int8 kinds were inside their wider intervals |
| **E80-S2** E64's governor on each burst run's own measured powers, rms ≤ 10 MHz | **FAIL** | 15.7 MHz over 34 of the 36 bursts. The other two (int8 smallint pass 1, int8 sparse50 pass 2) read 700 MHz in a single sample on the way up, so they have no measured power at 700 MHz, and the simulation needs all three points (corrections-check.txt C10). Post hoc, with the idle-reset and slow-start samples set aside, it is 2.65 MHz (§3d) |
| **E80-S3** sustained rms against E64-T1 at γ 3 ≤ 15 MHz | **FAIL** | **35.8 MHz** over 18 cells. Sixteen of 18 cells read at or above the prediction; the two below are fp16 zeros (−10.2 MHz) and int8 neg_ones (−3.1), both predicted at 800. Their shortfalls are the climb at each process start and an idle reset (§2) |

### 2. The speeds: what each kind of number gets on this card

The burst is the mean clock from 1.5 to 6.5 s of a 6 s run from a die reading ≤ 55 °C; both passes are given. The
sustained figure is the last 40 s of nine back-to-back 8 s processes, about 76 s in all; where a kind ran twice, both
runs are given. Rates are the kernel's own operations over its own wall time. p800 is the board's power at 800 MHz in
the first second after reaching it. The sustained clock, W and die are means over the sampler's readings inside the
kernel launches of the last 40 s (E64's reduction: 390–392 of each run's 399–400 readings; the rest fall in the gaps
between the nine processes).

The last column is **derived**, not measured on its own: board pJ/op is the sustained board W over the sustained
kernel rate. It is whole-board energy, idle and lane power included. Both numbers cover the kernel only, so this is the
board's energy per operation while the kernel runs. Counting the gaps between processes too (every reading's W over
the wall-clock rate) adds 2.1–3.4%: random fp32 is then 5.97 pJ per FLOP ([`corrections-check.txt`](corrections-check.txt)
C4). The sustained limit is the registered per-run label; a `none` run that the thermal test still stepped down
carries the count. From [`tables.md`](tables.md):

| format | kind | burst MHz | burst rate | p800 W | burst limit | sustained MHz | sustained rate | board W | die °C | limit | board pJ/op |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 | randn | 711.9 (715.7 / 708.0) | 10.69 TFLOPS | 82.7 | power | 604.3 (608.4 / 600.3) | 9.27 TFLOPS | 54.2 | 66.0 | thermal | 5.85 |
| fp32 | bf16trunc | 774.0 (776.5 / 771.4) | 11.71 | 69.5 | power | 639.1 | 9.70 | 51.7 | 65.7 | thermal | 5.33 |
| fp32 | nn_like | 760.8 (721.6 / 800.0) | 11.65 | 59.8 | none | 700.0 | 10.56 | 52.5 | 65.5 | thermal | 4.97 |
| fp32 | smallint | 800.0 (800 / 800) | 12.28 | 61.3 | none | 690.8 | 10.44 | 52.5 | 65.5 | thermal | 5.03 |
| fp32 | sparse90 | 800.0 (800 / 800) | 12.28 | 35.5 | none | 800.0 | 12.28 | 36.8 | 58.0 | none | 3.00 |
| fp16 | randn | 730.6 (746.9 / 714.3) | 21.95 TFLOPS | 76.1 | power | 609.5 | 18.68 TFLOPS | 52.3 | 66.0 | thermal | 2.80 |
| fp16 | fp8grid | 773.2 (776.5 / 770.0) | 23.37 | 69.8 | power | 661.5 | 19.98 | 54.2 | 65.6 | thermal | 2.71 |
| fp16 | smallint | 782.7 (787.8 / 777.6) | 23.82 | 66.9 | power | 650.6 | 19.71 | 51.9 | 65.6 | thermal | 2.63 |
| fp16 | nn_like | 780.0 (784.0 / 776.0) | 23.70 | 68.0 | power | 665.2 | 20.12 | 54.7 | 65.6 | thermal | 2.72 |
| fp16 | sparse50 | 800.0 (800 / 800) | 24.55 | 59.9 | none | 717.1 | 21.62 | 54.9 | 65.5 | thermal | 2.54 |
| fp16 | ones | 800.0 (800 / 800) | 24.55 | 50.7 | none | 781.6 (792.9 / 770.3) | 23.83 | 53.2 | 64.8 | none (2 thermal steps) / thermal | 2.23 |
| fp16 | zeros | 800.0 (800 / 800) | 24.55 | 34.6 | none | 789.8 | 24.23 | 35.1 | 57.7 | none | 1.45 |
| int8 | full | 800.0 (800 / 800) | 84.30 TOPS | 48.9 | none | 793.4 (796.7 / 790.0) | 83.54 TOPS | 53.2 | 64.9 | none (6 and 7 thermal steps) | 0.64 |
| int8 | gauss_q | 800.0 (800 / 800) | 84.31 | 48.0 | none | 794.4 | 83.70 | 52.1 | 64.6 | none | 0.62 |
| int8 | smallint | 798.0 (800 / 796) | 84.31 | 46.2 | none | 795.4 | 83.80 | 51.0 | 64.4 | none | 0.61 |
| int8 | sparse50 | 800.0 (800 / 800) | 84.30 | 46.8 | none | 789.3 | 83.15 | 49.0 | 63.6 | none | 0.59 |
| int8 | neg_ones | 777.5 (755.1 / 800.0) | 81.68 | 39.4 | none | 796.9 | 83.98 | 41.0 | 60.0 | none | 0.49 |
| int8 | zeros | 800.0 (800 / 800) | 84.30 | 34.8 | none | 800.0 | 84.33 | 37.0 | 58.0 | none | 0.44 |

How to read it:

- **On a cool die only the power test acts.** Every burst the governor throttled logged a *power* throttle-down
  first, and no burst logged a thermal one. Those kinds are fp32 randn and bf16trunc and fp16 randn, fp8grid,
  smallint and nn_like. Their p800 is 66.9–82.7 W, against the 65 W level. The two idle-reset dips of §3d are not
  throttles: no limiter line sits at either.
- **In sustained work only the thermal test acts.** No sustained run's last 40 s carries a single power label
  ([`corrections-check.txt`](corrections-check.txt) C1). Every throttle-down the trace ring holds for a sustained run
  is thermal. Where the ring does not reach, every reading below 800 in a thermal-labelled run follows a 66 °C die
  reading within 2 s (`sus_tel_hot_share` 1.0). And the sustained board power, 35–55 W, sits under the 65 W at which
  the power test acts.
  - The thermal test holds nine fp32 and fp16 kinds, and fp16 ones' second run, below 800, at a die mean of
    65.2–66.0 °C.
  - It also clips two runs labelled `none`. It stepped int8 full down 6 and 7 times, so that 3.3% and 7.2% of the
    last 40 s are thermal-labelled. It stepped fp16 ones' first run down twice.
  - Every other sustained reading below 800 is either the climb at each of the nine process starts or an idle reset.
    The climb is 2.6–5.9% of the last 40 s for int8 smallint, gauss_q and sparse50 and fp16 zeros, which read
    800 MHz between process starts. The idle resets are in int8 neg_ones and fp16 ones' first run (§3d).
- **Speed by kind.** On the same matmul and clock table:
  - fp32 sustains 604 MHz on random normals, 639 on bf16-truncated mantissas, 691–700 on small integers and NN-like
    data, and 800 on 90%-sparse data.
  - fp16 sustains 610 on random, 651–665 on small-integer, fp8-grid and NN-like data, and 717 on 50%-sparse. On
    constants it sustains 782 on ones, which sit at the trip, and 790 on zeros, 800 between process starts.
  - int8 sustains 789–800 MHz on every kind, and **only full-range random int8 reaches the trip**. It draws about
    53 W. Its die read ≥ 65 °C in 84% and 91% of its last 40 s, and the thermal test stepped it down 13 times over
    its two runs: 796.7 and 790.0 MHz, 83.9 and 83.2 TOPS. int4-range and Gaussian int8 sat at 65 °C for 42% and
    58% of the last 40 s, a degree under the 66 °C reading at which the test steps, and were never stepped down. The
    other int8 kinds stayed cooler (hottest reading 64 °C).
- **The interval.** A burst cell is two passes run in one block, and **they are not replicates**.
  - Pass 2 started from a 54–56 °C die, against 47–56 °C for pass 1.
  - All six power-limited kinds read lower in pass 2, by 5.1–32.6 MHz. fp16 randn moved most: 746.9 MHz from a
    48 °C die, 714.3 from 56 °C. fp32 randn and bf16trunc started both passes from the same die reading and still
    read lower (corrections-check.txt C8).
  - So the 0–33 MHz spread is a pass-order effect (the heat the block carries) plus noise, not replicate noise.
    [`tables.md`](tables.md) gives each pass's start die.
  - An idle reset fell in one pass of int8 neg_ones and of fp32 nn_like (§3d). int8 smallint's 796.0 pass is one
    600 MHz reading at 6.43 s, as its work ended.
  - A sustained cell is one run except fp16 ones, fp32 randn and int8 full. Those three replicated to 22.6, 8.1 and
    6.7 MHz. fp16 ones sits right at the trip, so a small change in the die decides how much of the 40 s is spent
    at 800.

### 3. What the misses are made of (post hoc, labelled; no verdict changes)

**(a) The card's heat path moved since 23 October.** The post-hoc die line over E80's 21 sustained runs is
**die = 42.23 + 0.4349 °C per W** (rms 0.56 °C). It reaches 65.5 °C at **53.5 W**, against E64's 50.3 W. At E64's
own slope the line sits **1.38 °C lower** (`results.json` `posthoc.die_line_e80`). Idle, before any launch, the die
read 45 °C at 21.75 W at the day's first gate (`smoke/run.log`) and 47 °C at 22.06 W at the session's (`s1/run.log`),
against 50 °C at 22.88 and 22.58 W at E64's two (`smoke2/run.log`, `s1/run.log`; corrections-check.txt C5). What
moved the heat path was not measured: neither session holds an ambient, inlet or fan reading. The moved line is why
the cells inside the clamp window moved, while the clamped cells and the burst did not:

- fp16 ones moved +44.5 MHz and int8 full +30.2;
- fp32 randn's burst moved +2.1 MHz;
- the sustained clamps (fp32 and fp16 random at 600, the zeros at 800) moved by −4.6 to +9.0 MHz.

**This is E69's failed drift check showing up again**, and Q130(c) flagged it (its README, item 7).

**(b) The power model over-charges low-entropy fp32 data.** E80 measures the switching term c on aifoundry2 with
E64's own method, and for three of the four out-of-sample fp32 kinds Q130(c) predicted it too high:

| kind | measured c | predicted c | measured share of random's switching over zeros |
|---|---|---|---|
| fp32 bf16trunc | 19.11 W | 24.27 W | 0.733 |
| fp32 smallint | 15.18 | 18.52 | 0.570 |
| fp32 nn_like | 14.04 | 17.15 | 0.523 |

For bf16trunc, Q130(c)'s model saved 4% of random fp32's switching power above the zeros level (A1's E70 arm saved
7%, on the same basis). E80 measures **27%** on that basis, and 25% of the whole switching term (19.11 against
25.55 W; corrections-check.txt C11). fp16 smallint, fp8grid, nn_like and sparse50, and int8 smallint, gauss_q and
sparse50, are also all below their point predictions, by 0.7–3.4 W, but inside their wider intervals. fp32 sparse90
reads 0.34 W above its point, just over its interval. On the calibration kinds the model is right to within 0.35 W:

- fp16 randn 23.07 W against 23.28;
- fp16 ones 9.70 against 9.70;
- int8 full 8.98 against 9.10;
- fp32 randn 25.55 against 25.21.

int8 neg_ones (a constant) reads 3.54 W against the frozen 2.68: the int8 lanes-on cost is higher than frozen, in
E79's direction.

One caveat on every kind the power test never stepped down in its burst, which includes all six int8 kinds: its c
rests on the 800 MHz point plus one or two ramp samples at 600 and 700. So its two passes disagree by up to 1.4 W
(int8 gauss_q 8.48 and 7.09; int8 zeros 2.82 and 2.16). The power-limited fp16 and fp32 kinds dither through all
three points, and their passes agree to 0.2 W. The sustained board power corroborates the int8 ordering at a common
clock and die (about 795 MHz, 64.4–64.9 °C): smallint 51.0 W and gauss_q 52.1 W against full's 53.2 W, which its
thermal steps (3–7% of its samples below 800) can only have lowered. So int4-range data draws
about 2 W less than full-range int8 here, although the kinds spec counts as many operand-bit flips for it (kinds.json
`kinds.int8.smallint`). That is two passes and one sustained run; E78 measures it at a pinned clock.

**(c) Splitting the sustained miss.** E64-T1 at γ 3, re-run post hoc (`results.json` `posthoc`):

| E64-T1 run on | sustained rms over 18 cells |
|---|---|
| the frozen inputs (E80-S3) | 35.8 MHz |
| the measured c | 19.8 MHz |
| E80's own die line | 16.7 MHz |
| **both** | **9.2 MHz** |

E64-T1's out-of-sample figure on E64's own cells was 6.2 MHz. With both fixes it puts **fp16 ones at 779.6 MHz
against 781.6 measured (−2.0)**. That is the cell E64-T1 was said never to close. It closes once the session's own
thermal path is used. The int8 kinds come out at 793–800 MHz, against 789–800 measured.

So the governor-and-heat model itself holds up. What failed is its inputs: Q130(c)'s fp32 power for low-entropy
data, and a die line measured on another day. One caution on the 9.2 MHz: E80's die line is fitted on these same 21
sustained runs, so the thermal path in that row is in sample, and only the governor and the leakage law are being
tested out of sample there.

**(d) The governor's idle reset, inside a launch** (amendment A1, [`posthoc-idle.txt`](posthoc-idle.txt),
[`posthoc-idle.json`](posthoc-idle.json); checked against the trace ring and the kernel's counters in
[`corrections-check.txt`](corrections-check.txt) C6). At least five times in 225 work processes (2.2%), the clock fell
from 800 MHz straight to 600 MHz while the work ran on: the kernel's own cycle counters read 0.60 GHz through each
dip. It fell twice in bursts (int8 neg_ones and fp32 nn_like, pass 1 each) and three times in sustained runs (fp16
ones' first, fp16 sparse50, int8 neg_ones).

- **What the ring shows.** No power or thermal line sits at any of the five.
  - A POWER_IDLE power-status record (throttle state 0) sits at three: both bursts, and fp16 ones' run.
  - int8 neg_ones' sustained run holds one too. The session's clock fit places it 1.9 s before the dip, the same
    offset that run's start ramp shows, so it lands on the dip.
  - fp16 sparse50's dip, at 23.1 s, comes before the ring's coverage (from 61.6 s), so the ring cannot show it.
- **How long, and what it costs.** The clock was back at 800 MHz 1.2–1.3 s later in the four that recovered before
  their process ended. int8 neg_ones' sustained dip came 0.65 s before its work ended. Each dip cost its 6 s burst
  44.9 MHz (int8 neg_ones) and 43.1 MHz (fp32 nn_like) of mean clock.
- **How often.** Five is a lower bound. The detector sees a dip only at 800 MHz on a die under 65 °C, more than
  1.5 s into a process and 0.3 s before its end. That is 39% of E80's work readings: most thermal-limited time is out
  of its reach. E63 counted 8 in 360 launches, also 2.2% ([`14-card-behaviour.md`](../../../findings/14-card-behaviour.md)
  "A one-second idle reset inside a launch"). Its launches sat at 800 MHz on a 54–57 °C die throughout, so per second
  in which a dip can be seen, E80's rate is, if anything, higher. With five events it is not known better than that.
- **Late ramps.** The same view flags 14 processes whose first 800 MHz reading comes more than 1.2 s after their
  start (E63's maximum), on a die under 65 °C and a board under 65 W.
  - One is long. fp32 nn_like pass 1 waited 2.2 s at 600 MHz and first read 800 MHz at 2.53 s. That cost its burst
    another 35.3 MHz, 78.4 MHz with its dip.
  - The other 13 first read 800 MHz at 1.31–1.43 s, one or two readings late. None reaches into a burst's scored
    window, which starts at 1.5 s. One of them, a single reading, falls in a sustained run's last 40 s (fp16 zeros).

With the dip and late-ramp samples set aside (post hoc):

- the burst rms is 19.5 MHz;
- no predicted-800 cell reads below 790, so R7's second clause would hold;
- the governor-only rms (S2) is **2.65 MHz** over 34 runs. 21 of the 34 read 800 MHz in both the simulation and the
  measurement; over the other 13 it is 4.3 MHz (corrections-check.txt C10). The samples were set aside after the data
  were seen, so this is not comparable with E64's in-sample 3.3 MHz.

R2 is unchanged at 13 of 18 by this view: the limit misses are the heat path, not the glitch.

### 4. Predicted against measured

The full table, with E64-T1's burst, Q130(c)'s own numbers and c against its interval, is in [`tables.md`](tables.md)
("Predicted against measured"). Each kind's prediction and its sources are under `kinds.<type>/<kind>` in
[`predictions.json`](../../../../tools/claims-v3/kspeed/predictions.json).

## What it changes

**For the blog's kinds table:**

- every cell of burst MHz, sustained MHz, TFLOPS/TOPS, board W, die °C and the limiting test for these 18 kinds, on
  one card in one session, and the board's pJ per operation while the kernel runs, derived (`cells.json`);
- the two-limits story, confirmed across formats: on a cool die, the power test acts; in sustained work on this
  card's cooling, the thermal test acts;
- int8 barely throttles. Its kinds burst at 800 MHz, except two cells that read lower for reasons unrelated to the
  kind: int8 −1s (777.5, an idle reset in one pass) and int4-range (798.0, one reading as the work ended). They
  sustain 789–800 MHz, and only full-range random int8 reaches the thermal trip, which clips 3–7% of its last 40 s.

**Three new findings for the explanation:**

1. **Narrower precision buys real power.** fp32 with bf16-truncated mantissas draws 27% less switching power than
   random fp32 above the zeros level (25% of the whole switching term). It gets 62 MHz more burst clock and 35 MHz
   more sustained.
2. **The sustained speed of a borderline kind depends on the card's cooling that day** (its cause not measured).
   fp16 ones read 737 MHz on 23 Oct and 782 MHz on 31 Oct, while the power-limited burst anchor (fp32 randn) moved
   2 MHz. On 31 Oct the idle die read 45–47 °C against 50 °C at the sessions' first gates, and the loaded die line sat
   1.4 °C lower: 3.2 W more board power before the trip (§3a).
3. **The governor occasionally resets mid-launch** (at least 5 of 225 processes). Each reset cost a 6 s burst 43–45 MHz
   of mean clock, 78 MHz in the one burst that also started slowly.

**For the Horace hub:**

- Status item 9 ("fp16 and int8, and the fp16 all-ones sustained cell"): **measured.** The speeds of seven fp16 and
  six int8 kinds now exist, burst and sustained.
- The fp16 all-ones cell: E64-T1's frozen prediction missed by +36.4 MHz. Post hoc, the model closes the cell to −2.0 MHz on
  the measured power and the session's own die line (that line fitted on the same runs), so the open part is the
  drifting heat path, not the governor model.
- Levels stop 1 ("a temperature term that closes"): the same post-hoc reading, 9.2 MHz rms over 18 new cells. To
  make it a prediction, a future run must measure the die line in the same session, before scoring. E80 shows that
  23 Oct's line is 3 W off today.

## Card state and etiquette

- aifoundry2 card 0, release 1.4.0 / BL2 0.22.0 (E69's reading).
- At the start, `et-who` read *"No process holds an ET-SoC-1 device node or card lock"*, and `who` showed no
  logins.
- The runner held the card lock for each session. The lab dashboard's collector and keeper kept to it, as with
  E64 and E69: nothing of theirs was stopped.
- The final read-only `ettelem config` under the lock, at about 13:03, gave `tdp_w 65`, `temp_threshold_c 65`,
  `low_power`, 600 MHz, 519 mV. `et-who` was free afterwards.
- Safety stops: none. The hottest die-mean sample read 67 °C (hottest sensor 69 °C), and the highest board sample
  was 88.1 W, in the first seconds of a sustained fp32 randn run on a cool die. The stops are 85 °C and 97 W.

## Departures, dated

- **Registered at `10f58581`:** every kind's burst ran twice, not only the anchors'. The sustained replicates were
  fp16 ones, fp32 randn and int8 full.
- **A1 (`075b691e`, during the SUS block):** the idle-reset view of §3d, post hoc.
  [`posthoc_idle.py`](../../../../tools/claims-v3/kspeed/posthoc_idle.py) as committed at A1 lacked the S2 view that
  A1's text names. That view was added after the data were in; nothing else in the script changed. It is post hoc
  either way.
- **The box's checkout.** aifoundry2's lab checkout was at `20c4249f`. E73 had left untracked copies of
  `tools/claims-v3/hlf/` there, which blocked a fast-forward. They were **moved, not deleted**, into an ignored
  backup folder under `build/`. Six are byte-identical to the tracked files; `lockin_hlf.py` differs and is kept.
  The checkout was then pulled to `10f58581`, and the runner, tiles, binaries and predictions were verified by sha256
  there before the claim.
- **Named after verification (Sat 31 Oct 2026): two ways Q130(c)'s R7 and R8 depart from what Q130(c) registered.**
  The tool README says they are "scored exactly as Q130(c) registered them on its frozen numbers". Both departures
  were visible at registration but not named. The verdicts stand as scored on the frozen numbers.
  - *R7 compares two windows.* Q130(c)'s burst numbers are 4–12 s means, and a 6 s run has no 4–12 s window, so
    they are scored against E80's 1.5–6.5 s burst. The same model's 1.5–6.5 s numbers (E80's registered burst
    prediction) sit 4.8–18.3 MHz higher for the nine kinds it puts below 800. So the window shifts those nine
    residuals up by as much. On matched windows the 25 MHz clause reads 14 of 18 instead of 13. The 800 MHz clause
    fails either way (corrections-check.txt C7).
  - *R8 is scored on the frozen die line.* Q130(c)'s README (`2bbe03dd`, item 7) asks that "E80 should re-read the
    die line before scoring R8". E80 measured no die line before scoring. The only one from this session is fitted on
    the same 21 runs (§3a). On it, post hoc and in sample, R8 reads 14 of 18 limits right and 18 of 18 clocks within
    40 MHz: still FAIL, on fp16 ones and int8 full, smallint and gauss_q (corrections-check.txt C7).
- **The runner's timeouts, as the tool README should have said them** (corrected there in a dated note). Every
  launch and query process runs under `timeout 10`. The sampler (`ettelem sample`) runs for the whole run outside it
  and is stopped with SIGTERM, as `lib.sh` does, with SIGKILL and a queue drain only if it ignores that. None did:
  all 57 `sampler_stop` marks in `s1/marks.jsonl` read rc 0.

## Files

| path | what |
|---|---|
| `s1/`, `smoke/` | the sessions as run (E64's layout): `session.json` and `kspeed.json` (the code's and every tile's sha256), `runs.jsonl`, `launches.jsonl.gz`, `tel/<run>.jsonl.gz` (10 Hz, no `--reset-ms`), `sp/<run>.bin` (the trace ring, read with `tools/claims-v3/hpl/sptrace_full.py`), `queries.jsonl`, `marks.jsonl`, `manifest.txt`, `run.log`, `run.out`, `end.json` |
| `results.json`, `reduce.txt` | `reduce_kspeed.py`: per-run metrics (E64's `reduce_hpl.run_metrics`), per-kind cells, every rule, the post-hoc arms |
| `posthoc-idle.json`, `posthoc-idle.txt` | `posthoc_idle.py` (amendment A1) |
| `tables.py`, `tables.md`, `cells.json` | formatting only: the README's tables and the blog's kinds-table cells, read from `results.json` and `predictions.json` (and `posthoc-idle.json`, to name the idle resets in a burst cell) |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind the corrections after verification: every number they quote, from the committed session and reduction (it reproduces the registered in-kernel W and rates first) |

Rebuild (any machine with Python 3; no third-party modules):

```bash
cd docs/reports/data/2026-10-31-e80-kinds-speed
python3 ../../../../tools/claims-v3/kspeed/reduce_kspeed.py s1 --out results.json > reduce.txt
python3 ../../../../tools/claims-v3/kspeed/posthoc_idle.py results.json s1 --out posthoc-idle.json > posthoc-idle.txt
python3 tables.py results.json ../../../../tools/claims-v3/kspeed/predictions.json --cells cells.json \
    --posthoc posthoc-idle.json > tables.md
python3 corrections-check.py > corrections-check.txt
```

## Corrections after verification (Sat 31 Oct 2026)

An independent verifier re-derived every registered number from the raw telemetry and reproduced all nine verdicts.
It found the faults below in the text. They are corrected above, desk only: no card was touched, nothing was re-run,
and no registered prediction, rule, number or verdict changed. Each derived number cites
[`corrections-check.txt`](corrections-check.txt).

| # | what was wrong | what changed |
|---|---|---|
| C1 | "int8 holds 789–800 MHz on every kind … its die stays … under the trip": **false for int8 full**. The thermal test stepped it down 6 and 7 times in its two sustained runs. Its die read ≥ 65 °C in 84% and 91% of the last 40 s, and 66 °C in 8 and 7 readings. Its `none` is the registered ≥ 90%-at-800 rule, not an absence of throttling. "int8's whole range of kinds bursts at 800 MHz" was not literal either: int8 −1s read 777.5 (an idle reset) and int4-range 798.0 | §2's reading of the table, its int8 lines and the limit column; R2's row; What it changes. The sub-800 sustained readings of the unthrottled kinds are now said to be the climb at each process start (C1b) |
| C2 | the lane's summary said all four fp32 kinds draw less than predicted; fp32 sparse90 draws more (2.23 against 1.89 W, 0.03 W over its bound; one pass inside) | S1's row now gives the direction of each miss (C2) |
| C3 | E80-R1's 21.7 MHz leans on eight cells pinned at 800 in both prediction and measurement | R1's row adds the 29.2 MHz rms on the other 10. With the two idle-reset passes set aside, none of those 10 reads more than 2.0 MHz below its prediction (C3). The 9.2 MHz of §3c keeps its in-sample caveat wherever it is quoted |
| C4 | the verifier read board pJ/op as a 40 s board-W mean *with* the process gaps over a kernel-only rate, understating it by 2.8–3.1%. **Judged wrong in its premise.** `reduce_hpl.run_metrics` keeps only the readings inside kernel launches (390–392 of 399–400), so the published figure is in-kernel over in-kernel, consistent. The verifier's replacement, in-kernel W over the wall-clock rate, mixes the two | The definition is spelt out in §2 and in `tables.py`, and the whole-window figure (every reading over the wall-clock rate) is given beside it: 2.1–3.4% higher. pJ per op cells are added to `cells.json` (C4) |
| C5 | "depends on the room … 3 C cooler": the cause was never measured. 47/50 °C are idle first-gate readings, and the cited files did not hold them. §3a's "49–51 °C on 23 Oct" has no committed source either | §3a and What it changes cite the four first gates (45 and 47 °C against 50 and 50 °C) and the loaded line's 1.4 °C, and say the cause is not measured (C5) |
| C6 | the idle reset stated too firmly. POWER_IDLE sits at three of the five dips as placed. "Up to 80 MHz" included a slow start. "E63's rate" ignored the detector's smaller exposure. The 14 late ramps went unreported | §3d now gives the ring record per dip: a fourth lands on its dip once the clock-fit offset its run's start ramp shows is applied, and the fifth precedes the ring. It also gives the kernel's 0.60 GHz through every dip, the cost per dip (44.9 and 43.1 MHz; 78.4 with the slow start), the 39% exposure, and the late ramps (C6) |
| C7 | Q130(c)'s R7 and R8 were said to be scored exactly as Q130(c) registered them. R7 compares Q130(c)'s 4–12 s numbers with E80's 1.5–6.5 s window, and Q130(c) had asked for the die line to be re-read before R8 | Both named under Departures, with what each changes (nothing in either verdict; C7) |
| C8 | the two burst passes were called independent and "pass agreement". Pass 2 never started cooler than pass 1 (54–56 °C against 47–56 °C), and all six power-limited kinds read lower in it | §2's interval bullet; `cells.json` gives each pass with its start die (C8) |
| C9 | the tool README said the runner "caps every device process at `timeout 10` and never signals one". The sampler runs outside it and is stopped with SIGTERM, as `lib.sh` does | a dated note in the tool README; Departures |
| C10 | E80-S2's population of 34 had no reason given, and its post-hoc 2.65 MHz was called better than E64's in-sample 3.3 MHz | S2's row gives the reason (no 700 MHz power in two bursts). §3d gives 4.3 MHz over the 13 runs not at 800 in both, and drops the comparison (C10) |
| C11 | "27% less switching power" was set beside a pair of numbers (19.1 against 25.6 W) that gives 25% | Both bases are stated: 27% above the zeros level, as Q130(c)'s 4% and A1's 7% are, and 25% of the whole term (C11) |
