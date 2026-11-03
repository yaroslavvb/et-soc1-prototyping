# Q139(s): the clock/voltage term, refitted on every committed voltage read

*Tue 3 Nov 2026 (week 45), 04:00-04:50 PST, on the Intel. Desk only: no card, no ssh, no device command. Everything here
is **post hoc**: nothing was registered before it was computed. It answers the kinds page's
[section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 6** (a power
model across kinds: M7's clock-and-voltage term for aifoundry2's governed bursts) and Q138's final critic's **rank 13**
("s(f) rests on E64's three voltages; the telemetry voltages of E80, E83, E119, E126 and E136 were never re-read; there
is no prediction at other operating points"). Item 16 (the rail ledger's off-rail row: the regulator's conduction and
efficiency) waits on the owner's word and is not touched.*

## Results first

**The voltages are settled, and they are not where M7's governed error lies.** Every committed telemetry record that
carries the minion clock and a minion voltage was read: 4,374,148 records in 3,107 files over 113 data dirs (20 Sep - 2 Nov
2026), on all four cards. Each card's operating points sit at fixed voltages, the same to ±1 mV in every session, under
every load and across die readings of 50-84 °C:

| card | MHz | on-die PVT, busy median (mV) | PMIC set point (mV) | sessions (≥ 100 samples) | session medians (mV) | PVT samples |
|---|---:|---:|---:|---:|---|---:|
| aifoundry2 | 600 | **518** | 520 | 44 | 517-519 | 1,099,667 |
| aifoundry2 | 700 | **567** | 570 | 27 | 567-569 | 18,732 |
| aifoundry2 | 800 | **618** | 620 | 28 | 618-619 | 434,133 |
| aifoundry1 card 0 | 300 | 398 | 400 | 2 | 398 | 471 |
| aifoundry1 card 0 | 600 | **519** | 520 | 4 | 519 | 20,489 |
| aifoundry1 card 0 | 700 | 563 | 565 | 4 | 563-564 | 2,429 |
| aifoundry1 card 0 | 800 | **604** | 605 | 4 | 604 | 44,789 |
| aifoundry1 card 1 | 300 | 399 | 400 | 2 | 399 | 10,870 |
| aifoundry1 card 1 | 600 | **499** | 500 | 25 | 499 | 907,722 |
| aifoundry3 | 600 | **522** | 525 | 50 | 522-523 | 1,732,949 |

([`clock-voltage.txt`](clock-voltage.txt) section 1; [`clock-voltage.json`](clock-voltage.json) `voltage_table`.) The PVT
reading moves less than 2 mV from idle to full load (fitted slopes of −0.03 to +0.04 mV per A over 10-91 A of rail
current) and −0.10 to +0.09 mV per °C (card 1's idle 300 MHz point, over 61-63 °C only, −0.24). So the PMIC holds the
die's rail at its set point less a fixed 1-3 mV offset.

**s(f) refitted on the reads barely moves.** On aifoundry2, with the PVT busy means (E143's own data left out, so the fit
never saw the rows it is scored on), V = 0.5180 / 0.5679 / 0.6183 V and s(f) = (V_f/V_600)² f/600 = 1 / **1.4025** /
**1.8999**, against M7's frozen 1 / 1.4082 / 1.9052 (E64's 0.517 / 0.568 / 0.618 V): −0.40% and −0.27%. The set points give
1.4018 / 1.8955. M7's other voltage-based term, the transfer from aifoundry3's D to aifoundry2's c, xfer = (V_600,a3 /
V_600,a2)², reads 1.01538 against the frozen 1.01865 (−0.32%).

**E143's governed bursts, post hoc, with fits that never saw E143** (36 tiles, E143's registered groups;
measured − predicted; [`clock-voltage.txt`](clock-voltage.txt) section 4, [`d-split.txt`](d-split.txt)):

| arm | s(800) | governed clock (19) | governed board W | pinned clock (17) | pinned board W | die rise (36) | D at the clock, governed / pinned |
|---|---:|---|---|---|---|---:|---|
| **A0 M7 as frozen** (reproduces E143-F1/F2/W1/W2) | 1.9052 | 6.64 MHz (−4.97) | 1.601 W (+1.17) | 1.01 (−0.15) | 1.185 (−0.80) | 0.586 °C | 2.57 (+2.33) / 1.04 (+0.55) W |
| A1 s(f) from the reads, all else frozen | 1.8999 | 7.16 (−5.61) | 1.604 (+1.19) | 1.00 (−0.16) | 1.168 (−0.76) | 0.584 | 2.57 / 1.07 |
| **A2 s(f) from the reads, M7's chain refitted** | 1.8999 | **6.57** (−4.87) | **1.609** (+1.18) | **1.01** (−0.15) | **1.188** (−0.81) | **0.586** | 2.58 / 1.04 |
| A3 as A2, n = 2.43 (E72's board exponent) | 2.0503 | 6.93 (+5.01) | 1.646 (+1.02) | 1.18 (+0.04) | 1.372 (−1.20) | 0.599 | **2.09** (+1.65) / **0.86** (−0.55) |
| A4 as A2, s(f) measured from board power | 2.0559 | 7.64 (+5.98) | 1.620 (+0.98) | 1.20 (+0.06) | 1.447 (−1.29) | 0.603 | 2.10 (+1.66) / 0.88 (−0.59) |

"M7's chain refitted" means: B(f) by E64's `fit_linear` on E64's 103 committed rows with the new s(f); each E80/E83
kinds cell's c recomputed from its committed 58 °C-referred powers; the burst cap W* refitted on E80's and E83's 56 kinds
bursts with M7's golden-section fit; xfer from the reads; c_zeros from E64's zeros runs. At M7's own s(f) this chain
reproduces M7 exactly (B to 1e-6 W, c_zeros 1.440 / 1.394 / 2.123, every cell's c_w within 0.0007 W of the committed,
W* 65.580 W). A0 reproduces E143's registered figures to rounding (6.629 MHz, 1.601 W, 1.007 MHz, 1.184 W, 0.585 °C; the
registered predictions were rounded to 0.1 MHz and 0.01 W). The consistent refit from the reads (A2) changes E143's
scores by at most 0.07 MHz and 0.008 W. Swapping s(f) alone (A1) moves the governed clock by +0.5 MHz, because the cap
was fitted at M7's s(f). **M7's frozen s(f) did as well on the same rows as any refit from the reads.**

**E118's two-clock price ratio on aifoundry1 card 0 (600 over 800 MHz), with card 0's voltages from its four other
sessions (E60's and E118's own left out):** 0.5195 / 0.6038 V, so V² predicts **0.740**. E118 measured
0.697 ± 0.057 (registered row) and 0.683 ± 0.016 on the uncorrected rail
([`../2026-11-01-e118-two-clock-card0/posthoc_exponents.json`](../2026-11-01-e118-two-clock-card0/posthoc_exponents.json)):
V² reads 6% high, −0.8 SE on the board and −3.5 SE on the rail.

| prediction of E118's ratio | value | board, registered row | rail |
|---|---:|---|---|
| V², card 0's own reads (never E118 or E60) | 0.740 | −0.043 (−0.8 SE) | −0.057 (−3.5 SE) |
| V², E118's registered voltages | 0.737 | −0.040 (−0.7 SE) | −0.054 (−3.3 SE) |
| M7's frozen s(f) (aifoundry2's voltages: another card's table) | 0.700 | −0.003 | −0.017 (−1.0 SE) |
| V^2.43, E72's registered board exponent (aifoundry2) on card 0's reads | **0.694** | **+0.004 (+0.1 SE)** | −0.011 (−0.7 SE) |
| V^2.45, the board-power ramp exponent (aifoundry2, below) on card 0's reads | 0.692 | +0.005 (+0.1 SE) | −0.009 (−0.6 SE) |
| V^1.72, E72's rail exponent | 0.772 | −0.075 (−1.3 SE) | −0.089 (−5.4 SE) |
| energy scaling with f as well | 0.555 | +0.142 (+2.5 SE) | +0.128 (+7.8 SE) |

M7's frozen number lands on the measurement only by borrowing aifoundry2's table: card 0's 800 MHz point is 605 mV
against aifoundry2's 620.

**The form, from board power (labelled: power data, not a voltage read).** Under P_f = B_f + c s_f, the slope of each
run's P_800 on its P_600 measures s(800) with no B in it. Over E64's, E80's and E83's start ramps (210 runs, none from
E143) it is **s(800) = 2.056 ± 0.012** and s(700) = 1.476 ± 0.009, against V²'s 1.900 and 1.403. That is n = 2.45 ± 0.03
and 2.55 ± 0.07 ([`clock-voltage.txt`](clock-voltage.txt) section 2b; by session: E64 2.32 ± 0.17, E80 2.44 ± 0.05, E83
2.49 ± 0.02). The per-flip prices say the same on the board: E72 n = 2.43 ± 0.22, E118 2.36 ± 0.53. The rails disagree
with each other (E72 1.60-1.72, E118 2.50 ± 0.16). P_600 comes from the ramp's first pass or two, so a lag of the board
meter that grows with power would steepen these slopes; that is not excluded here, although the per-flip prices, read
over long pinned dwells, agree. Through M7's chain, the steeper form predicts the switching part better: D's error falls
16-19% (governed 2.57 → 2.09-2.10 W rms, pinned 1.04 → 0.86-0.88) and the zeros-level miss halves (−1.1 to −1.3 W → −0.6
to −0.9 W). But the board total at the clock gets worse (pinned 1.19 → 1.37-1.45 W; governed clock 6.64 → 6.93-7.64 MHz),
because under V² the D and zeros-level errors had partly cancelled. The cap is fitted on E80's and E83's bursts in every
arm, so those bursts cannot choose the form (their leave-one-kind-out clock rms is 8.57-8.59 MHz in every refitted arm).
E143's D can, post hoc.

## What this does to predicting power and heat

**Term tested:** s(f), the clock/voltage scaling of the switching watts in M7's governed relation P(f) = B(f) + c s(f),
and the V² transfer xfer, both refitted on every committed voltage read. **Before → after, out of sample (post hoc):**

- On E143's bursts, with A0 → A2 refitted from the reads: governed clock 6.64 → 6.57 MHz rms, board 1.601 → 1.609 W;
  pinned clock 1.01 → 1.01 MHz, board 1.185 → 1.188 W; die rise (M7's frozen burst heat law on each arm's board W) 0.586
  → 0.586 °C. **No change.**
- On E118's ratio: M7's s(f) 0.700 (−0.003, by another card's table) → V² on the card's own reads 0.740 (−0.043, −6%) →
  V^2.43 0.694 (+0.004).

So the voltage half of the term is closed: for any operating point a card has visited, the reads give its voltage to
±1 mV (±0.3-0.4% in V²), and no model error at the 1% level comes from it. The open half is the exponent. On the board,
n is about 2.4-2.5, not 2: by two methods on aifoundry2 (E72's per-flip prices, 2.43 ± 0.22; the ramp slopes of three
sessions, 2.45 ± 0.03) and one on card 0 (E118's prices, 2.36 ± 0.53). That exponent predicts card 0's ratio to 0.5% and
E143's switching part 16-19% better, but on its own it does not improve E143's board total or clock.
To use it, M8 must take it together with aifoundry2's zeros level, which the critic's rank 2 already lists (E143's
"aifoundry2's zeros level, a cap term rising with overshoot and a D scale per format"). Heat follows the board watts
through the burst law, so it moves by at most 0.02 °C.

## What the reads support, and what they cannot

**They support:**

- Each card's voltage at each operating point it has run: the set point (GET_MODULE_VOLTAGE) and the on-die monitors
  (GET_ASIC_VOLTAGE), ±1 mV across sessions, loads and die temperature. The table above is the per-card operating-point
  table as the telemetry sees it.
- That the four cards' tables differ: at 600 MHz card 1 runs at 500 mV, aifoundry2 and card 0 at 520, aifoundry3 at
  525; at 800 MHz card 0 runs at 605 mV, aifoundry2 at 620.
- That the regulator holds the die. The PVT reading sits 1-3 mV under the set point at every load, so no IR-drop term is
  needed in s(f).

**They cannot support:**

- **The exponent.** A voltage read says what V is, not how energy scales with it. That takes power data (above).
- **The regulator's efficiency and conduction loss (item 16, the owner's word).** No read here is on the regulator's
  input side, and the minion-rail power the SP reports is a rail-side figure, so nothing splits board watts into rail
  power and conversion loss. A board exponent above 2 is what a loss rising with current would look like. The reads cannot
  tell that apart from a real switching-energy exponent; the rails' disagreement (1.6-1.7 against 2.5) leaves it open.
- **The card-to-card scale (rank 5).** V² at 600 MHz says card 1 / aifoundry3 = 0.913, aifoundry2 / aifoundry3 = 0.985,
  card 0 / aifoundry3 = 0.990. Card 1's measured scale is 0.971 (M7's fit) to 0.982 (the critic's X1 reading), so the
  voltage alone misses it by 6-7%. It is one cheap read for a card-scale predictor, not the predictor.
- **Operating points never visited.** aifoundry3 and card 1 have run only at 600 MHz (card 1 also idles at 300), so
  their 700 and 800 MHz voltages are unread. The firmware's operating-point table itself (DM_CMD_GET_VMIN_LUT) holds
  per-card calibration that E72 kept private; it is not read or published here.
- **Transients faster than a sample** (the sampler's 100 ms, the SP's 133-266 ms pass). The SP's own statistic (`sp.minion_mv`, GET_SP_STATS) is
  a running average that lags a change of operating point: it reads 519 mV at 700 MHz on aifoundry2 and 563 mV at 300
  MHz on card 0. Only `die_mv` and `reg_mv` are per-point reads. E118 read the statistic over long pinned dwells, where
  it equals the PVT reading.

## Method, and what was and was not registered

- [`survey_voltage_reads.py`](survey_voltage_reads.py) (standard library, 6 processes, 35 s) bins every record by card,
  data dir, session, clock, steady (the clock equal to the previous record's, within 1 s), set point, PVT reading, SP
  statistic and rail W to 0.5 W → [`voltage-reads.json.gz`](voltage-reads.json.gz) (the tree at `e9421fab`). Cards come
  from the path, else the nearest `session.json`, else a fixed list (eight aifoundry3 memory-path and Q129 dirs, E64,
  E69, E80, E83 on aifoundry2, E84 and E114 on card 0). No file is unplaced. E84's and E114's telemetry opens with a
  text line, which the survey skips. E118's telemetry used the no-PMIC-read profile, so it carries the SP statistic
  only. 1,210 `ettelem config` reads (minion MHz with GET_ASIC_VOLTAGE) are listed beside it. 1,208 agree within 1 mV
  with a card's PVT reading at their clock (77 of them are in config files the survey could not place on a card). One
  700 MHz read is 553 mV, taken during a step; one aifoundry2 600 MHz read is 523.
- [`fit_clock_voltage.py`](fit_clock_voltage.py) (numpy): sections 1-4 above. It imports the lab's frozen code unchanged
  (`tools/claims-v3/hpl/surface_hpl.py` `fit_linear`, `tools/claims-v3/e119/make_predictions_e119.py` `dither`) and reads
  M7 (`docs/reports/data/2026-11-02-q138m-model/m7.json`), E143's frozen D per tile
  (`tools/claims-v3/e143/predictions-e143.json`, `D600_a3_footing_w`) and E143's measured per-tile means
  (`results.json` `score.reported.tiles`). [`d_split.py`](d_split.py) splits each arm's board error into D and the
  zeros level.
- **Nothing was registered.** Every arm is post hoc and labelled so. E143's and E118's registered verdicts stand
  unchanged. The arms were chosen before E143 was scored on them (A0-A3 in the first run; A4 added after the ramp slopes
  were read, and its result is reported whatever it said). The fits that never saw the scored rows are E143's dir left
  out of every voltage (A1-A4), and E118's and E60's dirs left out for card 0.
- **Rerun** (from the lab repo's root, about 3 minutes):
  `python3 docs/reports/data/2026-11-03-q139s-clock-voltage/survey_voltage_reads.py . --out docs/reports/data/2026-11-03-q139s-clock-voltage/voltage-reads.json` and gzip it, then
  `python3 docs/reports/data/2026-11-03-q139s-clock-voltage/fit_clock_voltage.py . docs/reports/data/2026-11-03-q139s-clock-voltage/voltage-reads.json.gz --out docs/reports/data/2026-11-03-q139s-clock-voltage/clock-voltage.json > docs/reports/data/2026-11-03-q139s-clock-voltage/clock-voltage.txt`, then
  `python3 docs/reports/data/2026-11-03-q139s-clock-voltage/d_split.py docs/reports/data/2026-11-03-q139s-clock-voltage/clock-voltage.json docs/reports/data/2026-11-02-e143-blind5-aifoundry2/results.json docs/reports/data/2026-11-03-q139s-clock-voltage/d-split.json`.

## Device commands sent

None. This lane opened no device node and took no card lock. The reads it used were sent by earlier runs and are in
their committed telemetry, each a READ by Q136(w)'s classification: DM_CMD_GET_ASIC_FREQUENCIES (the clock),
DM_CMD_GET_ASIC_VOLTAGE (the on-die monitors), DM_CMD_GET_MODULE_VOLTAGE (the PMIC's voltage registers, read only:
the owner's rule of 2 November 2026), DM_CMD_GET_SP_STATS (the SP's statistics, rail power) and DM_CMD_GET_MODULE_POWER
(board W).

## Files

- `README.md`: this file.
- `survey_voltage_reads.py`, `voltage-reads.json.gz`: the survey and its bins.
- `fit_clock_voltage.py`, `clock-voltage.json`, `clock-voltage.txt`: the voltage table, s(f), the form check, E118 and E143.
- `d_split.py`, `d-split.json`, `d-split.txt`: E143's board error split into D and the zeros level, per arm.
