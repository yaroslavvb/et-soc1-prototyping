# Q139(s): the clock/voltage term, refitted on every committed voltage read

*Tue 3 Nov 2026 (week 45), 04:00-04:50 PST, on the Intel. Desk only: no card, no ssh, no device command. Everything here
is **post hoc**: nothing was registered before it was computed. It answers the kinds page's
[section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 6** (a power
model across kinds: M7's clock-and-voltage term for aifoundry2's governed bursts) and Q138's final critic's **rank 13**
("s(f) rests on E64's three voltages; the telemetry voltages of E80, E83, E119, E126 and E136 were never re-read; there
is no prediction at other operating points"). Item 16 (the rail ledger's off-rail row: the regulator's conduction and
efficiency) waits on the owner's word and is not touched.*

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 05:10-05:35 PST; desk only: no card, no device command).
An independent verifier re-derived the survey, the voltage table, s(f), xfer, E118's predictions and every E143 arm from the
committed files, with this lane's code and with its own, and found the voltage half sound. It found one major fault and six
minor ones. None changes a measured, frozen or registered number or verdict (nothing here was registered), and none is a
device command. Each is corrected by a dated note beside the text it concerns, the text itself left as it was, and set out
in full in [§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the end. The numbers they
quote are printed by [`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt)
([`corrections-numbers.json`](corrections-numbers.json)). **The main one, C1:** the board's exponent is **about 2.3**, not
2.45 ± 0.03. The ± is statistical only. The value moves with the leakage slope the 58 °C referral applies at 600 MHz:
2.26-2.31 at aifoundry2's measured 600 MHz slope (E66's 0.2936 W/°C), 2.42-2.45 with E60's 800 MHz slope (0.442) at every
clock, 2.13 with no referral. At n = 2.28 the steeper form improves E143's governed clock (6.64 → 4.82-4.83 MHz rms, post
hoc) and keeps its board totals within 0.07 W of M7's, so "alone it worsens the governed clock" holds only at 2.43-2.45.*

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

*(Dated note, Tue 3 Nov 2026, after verification, C2, C3 and C7.)* The fitted droop slopes run **−0.038 to +0.029 mV per A**
(the text above quotes the effective-resistance column, −0.03 to +0.04 mΩ, as mV per A), and their current is the SP's rail
statistic, which lags a step; the "under 2 mV" rests on the PVT distribution itself. "±1 mV in every session" holds for each
data dir's median (the "sessions" column counts data dirs). Single runs spread ±2 mV about the card's median, hot runs
reading up to 2 mV low (0.8% in V²). aifoundry2's 700 MHz point is a transit point, read at 567-569 mV. "Every committed
telemetry record" means every committed `.jsonl` / `.jsonl.gz` record and the `config*` reads. Details:
[§ Corrections, C2, C3, C7](#corrections-after-verification-tue-3-nov-2026).

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

*(Dated note, Tue 3 Nov 2026, after verification, C4 and C1.)* Card 0's voltages come from its **three** other data dirs
(`2026-10-21-dtf`, E84's and E114's; E60's and E118's left out), not four sessions. The V^2.45 row uses the referral's high
end: at the corrected n = 2.28 the prediction is **0.710** (registered row −0.2 SE, rail −1.6 SE; 0.707-0.711 over
2.26-2.31). [§ Corrections, C1, C4](#corrections-after-verification-tue-3-nov-2026).

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

*(Dated note, Tue 3 Nov 2026, after verification, C1, the major fault.)* **n = 2.45 ± 0.03 is overprecise and probably
high.** The ± is statistical only. The slopes rest on `surface_hpl.powers()`'s 58 °C referral, which corrects every clock's
samples with E60's **800 MHz** leakage slope (0.442 W/°C), while aifoundry2's own **600 MHz** slope is E66's 0.2936 W/°C. A
load's late 600 MHz samples sit on a die 4.7 °C warmer than its ramp samples. Re-reduced with E66's slope at 600 MHz (and
E60's at 800), the same 210 runs give **s(800) = 1.996 ± 0.009, n = 2.28 ± 0.03**, and the three sets of P_600 samples
agree (post-ramp 2.26, all 2.28, ramp-only runs 2.31); with 0.442 at every clock they differ (2.42 against 2.30). No
referral gives 2.13. The runs whose 600 MHz samples all lie in the ramp, near the reference temperature, give 2.29-2.31 for
any 600 MHz slope from 0.20 to 0.442 W/°C. So the board exponent is **about 2.3** (2.1-2.45 by the referral), and the
"meter lag" named above is not the main systematic; the referral's 600 MHz slope is. Through the chain at n = 2.28, E143's
governed clock improves to **4.82-4.83 MHz** rms (A0 6.64) and its board totals stay within 0.07 W of A0's, so "the
board total at the clock gets worse … governed clock 6.64 → 6.93-7.64" holds only at 2.43-2.45.
[§ Corrections, C1](#corrections-after-verification-tue-3-nov-2026).

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

*(Dated note, Tue 3 Nov 2026, after verification, C1 and C5.)* **The befores, and the exponent's effect, corrected.**
E143's registered scores are 6.63 MHz (F1), 1.60 W (W1), 1.01 MHz (F2) and 1.18 W (W2); the 6.64 MHz and 1.185 W above are
A0 re-scored on unrounded predictions (6.635 and 1.185). The exponent is about 2.3, not 2.4-2.5 (C1). At n = 2.28, post
hoc and through the same chain (E143 in no fit), **governed clock 6.64 → 4.82-4.83 MHz rms** (bias −4.97 → +1.44 to +1.46),
governed board 1.601 → 1.619-1.639 W, pinned board 1.185 → 1.184-1.257 W, the switching part D governed 2.57 → 2.17-2.25 W
and pinned 1.04 → 0.73 W, die rise 0.586 → 0.587-0.594 °C, and E118's ratio 0.710 (−0.2 SE). So at the exponent the
referral supports, the steeper form improves the governed clock by about a quarter at little cost in board W, rather than
worsening both. The value of n still rests on one card's ramps and on the referral; M8 (Q139(m), frozen at 04:57 PST)
kept M7's V² s(f), so n is for the refit after it, fitted on aifoundry2's own footing with its zeros level.
[§ Corrections, C1, C5](#corrections-after-verification-tue-3-nov-2026).

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
- *(Dated note, Tue 3 Nov 2026, after verification, C6.)* The work ran 04:00-04:30 PST (the commit `8c16ab2d` is 04:29:28
  PST), not to 04:50. No file shows what a first run scored: only the final fit's outputs were kept. So "A0-A3 were chosen
  before E143 was scored on them" is not evidenced. The work files do show the ramp slopes were read before the final fit,
  consistent with "A4 added after". Every arm is post hoc either way.
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
- *(Added after verification, Tue 3 Nov 2026.)* `corrections-numbers.py`, `corrections-numbers.json`,
  `corrections-numbers.txt`: every number the corrections quote (C1-C5).

## Corrections after verification (Tue 3 Nov 2026)

An independent verifier (Q139's, 04:35-05:05 PST) re-ran this lane's survey on a clean extract of `8c16ab2d` (identical
JSON: 3,107 files, 4,374,148 records, 113 data dirs), scanned every line of every file with its own code (the same files
and records), reproduced every cell of the voltage table, s(f), xfer, the cross-card V², E118's predictions and every E143
arm and D split with its own scorer, and checked the timing, the post hoc labels and the privacy of the nine files. Its
verdict: the voltage half holds; the exponent needs a fix (major), and six statements need fixes (minor). None is a
measured, frozen or registered number or verdict, and none is a device command. They are corrected here, desk only, by the
dated notes above and this section; the text above them is unedited. The numbers below are printed by
`corrections-numbers.py` (numpy; it reads committed files only and imports this lane's `fit_clock_voltage.py` and the
lab's `surface_hpl.py` unchanged). It checks itself first: its re-reduction equals `surface_hpl.powers()` and the
committed `p_ref` / `p_ref58_w` to 0.000 W at 0.442 W/°C, and its A0, A2 and A3 equal `clock-voltage.json`'s arms to
2e-7. None of its inputs changed between `e9421fab` (the survey's tree) and this commit. Rerun from the top of the lab
repo (about a minute): `python3 docs/reports/data/2026-11-03-q139s-clock-voltage/corrections-numbers.py . --out
docs/reports/data/2026-11-03-q139s-clock-voltage/corrections-numbers.json > docs/reports/data/2026-11-03-q139s-clock-voltage/corrections-numbers.txt`.

- **C1 (major): the board's exponent is about 2.3, and its ± was statistical only.** The README gives s(800) =
  2.056 ± 0.012, n = 2.45 ± 0.03 (§ The form, from board power; arm A4; § What this does). The value rests on the 58 °C
  referral in `surface_hpl.powers()`, which corrects every clock's samples with E60's 800 MHz leakage slope, 0.442 W/°C
  (`LEAK_W_PER_C`). aifoundry2's own 600 MHz slope is E66's **0.2936 W/°C**: 18 cooling cycles at 600 MHz and 519 mV,
  sd 0.0012 ([`../2026-10-27-e66-idle-long/README.md`](../2026-10-27-e66-idle-long/README.md), § Results). A load's late
  600 MHz samples sit on a die 4.7 °C warmer than its ramp samples (89 runs with both), so the slope applied at 600 MHz
  moves P_600 against P_800, and with it the fitted s(800). Re-reduced with one slope per clock, the same 210 runs give
  (one intercept per experiment; ± are least-squares standard errors; `corrections-numbers.txt` § C1):

  | leakage slope at 600 / 700 / 800 MHz (W/°C) | all 210 runs: s(800), n | P_600 from post-ramp samples (89 runs): n | runs whose P_600 is all in the ramp (107): n |
  |---|---|---|---|
  | 0.442 / 0.442 / 0.442 (E60's at every clock: the lane's) | 2.058 ± 0.012, **2.45 ± 0.03** (common intercept 2.056: as committed) | 2.42 ± 0.01 | 2.30 ± 0.08 |
  | **0.2936 (E66) / 0.368 (interpolated) / 0.442 (E60)** | **1.996 ± 0.009, 2.28 ± 0.03** | **2.26 ± 0.02** | **2.31 ± 0.07** |
  | none | 1.945 ± 0.016, 2.13 ± 0.05 | 2.04 ± 0.04 | 2.55 ± 0.07 |

  - **The 600 MHz slope is the main systematic.** Swept from 0.20 to 0.442 W/°C (700 MHz interpolated, 800 at 0.442), n
    over all runs goes from 2.15 to 2.45. The runs whose 600 MHz samples all lie in the ramp, where the referral at
    600 MHz is small, give 2.29-2.31 at every slope in that range.
  - **The sample sets agree at E66's slope** (2.26 / 2.28 / 2.31). With 0.442 at every clock they differ by 0.12 (2.42
    against 2.30, 1.5 SE).
  - **A meter lag and the busy slope are not separated.** The paired late-minus-ramp P_600 of the same 89 runs, against
    the run's load, is −0.012 ± 0.008 W/W at 0.442 and +0.020 ± 0.008 at 0.2936 (a lag in the ramp would read positive).
    So the data allow either no lag and a busy 600 MHz slope near 0.43 W/°C, or E66's slope and a small ramp lag. The
    lane named only the lag.
  - **So:** the board exponent is **about 2.3**. It is 2.26-2.31 at aifoundry2's measured 600 MHz slope, 2.42-2.45 only
    if the busy 600 MHz slope is as steep as E60's 800 MHz one, and 2.13 with no referral. The ±0.03 is statistical; the
    referral spans 2.1-2.45. A4's s(800) 2.056 is the referral's high end. At E66's slope s(700) is 1.454 ± 0.009
    (n 2.39 ± 0.06), not 1.476. The meter's dips are kept here, as in the lane's reduction: on governed traces E82 A2's
    dip rule also catches governor steps, so it needs a clock-step guard before it is used there (the verification's
    cross-lane note).
  - **Downstream, post hoc, through the lane's own chain (E143 in no fit;** `corrections-numbers.txt` § C1c**):**

  | arm | s(800) | governed clock (19) | governed board | pinned clock (17) | pinned board | die rise (36) | D governed / pinned |
  |---|---:|---|---|---|---|---:|---|
  | A0 M7 as frozen | 1.9052 | 6.64 MHz (−4.97) | 1.601 W (+1.17) | 1.01 (−0.15) | 1.185 (−0.80) | 0.586 °C | 2.57 / 1.04 W |
  | A2 V² from the reads | 1.8999 | 6.57 (−4.87) | 1.609 (+1.18) | 1.01 (−0.15) | 1.188 (−0.81) | 0.586 | 2.58 / 1.04 |
  | **A5 n = 2.28**, the chain on the committed 0.442-referred powers | 1.9965 | **4.82** (+1.46) | 1.639 (+1.07) | 1.08 (−0.05) | 1.257 (−1.06) | 0.594 | 2.25 / **0.73** |
  | **A5c n = 2.28**, the chain re-referred at E66's slope | 1.9965 | **4.83** (+1.44) | 1.619 (+1.06) | 1.07 (−0.06) | 1.184 (−0.98) | 0.587 | 2.17 / **0.73** |
  | A4c the ramp slopes at E66's slope, re-referred chain | 1.9946 | 4.93 (+1.90) | 1.587 (+1.02) | 1.07 (−0.06) | 1.242 (−1.05) | 0.590 | 2.20 / 0.73 |
  | A3 n = 2.43 (as committed) | 2.0503 | 6.93 (+5.01) | 1.646 (+1.02) | 1.18 (+0.04) | 1.372 (−1.20) | 0.599 | 2.09 / 0.86 |

  At the exponent the referral supports, the steeper form improves E143's governed clock by about a quarter (6.64 →
  4.82-4.93 MHz rms; bias −4.97 → +1.4 to +1.9 MHz) and the switching part D (governed 2.57 → 2.17-2.25 W, pinned 1.04 →
  0.73 W). It keeps the board totals within 0.04 W of A0's, except the pinned board in A5 (+0.07 W) and A4c (+0.06 W).
  The zeros-level miss shrinks from −1.1..−1.3 to −0.7..−1.0 W, and heat moves by at most 0.01 °C. "Alone it worsens the
  board total and the governed
  clock" holds at 2.43-2.45 only. E118's ratio at n = 2.28 on card 0's own reads is **0.710** (registered row −0.2 SE,
  rail −1.6 SE); 2.26-2.31 give 0.707-0.711, and the lane's 2.45 gives 0.692.
  - **For the next refit:** M8 (Q139(m), [`../2026-11-03-q139m-model/`](../2026-11-03-q139m-model/README.md), frozen at
    04:57 PST) kept M7's V² s(f) for aifoundry2, and quotes "Q139(s)'s board exponent 2.45" only in a sensitivity
    sentence of its "What this cannot say". The exponent is for the refit after it. Fit it on aifoundry2's own footing
    (a measured leakage slope at each clock, the dip rule guarded against governor steps), together with aifoundry2's
    zeros level, and don't take 2.45 ± 0.03 as given.
- **C2 (minor): the droop's sign, and its current.** "Fitted slopes of −0.03 to +0.04 mV per A" (Results first) quotes
  the effective-resistance column with mV per A's name. The fits run **−0.038 to +0.029 mV per A**, an effective
  resistance of −0.03 to +0.04 mΩ (`clock-voltage.json` › `voltage_table.*.droop_fit`; `corrections-numbers.txt` § C2).
  The current is the SP's rail statistic (`sp.minion_w`, GET_SP_STATS) over V, which, like `sp.minion_mv`, holds stale
  values for a pass or more after a step. Card 0's idle 300 MHz point spans 52.8-91.2 A (p05-p95): current left over from
  the load before. "Less than 2 mV from idle to full load" rests on the PVT distribution itself: p05-p95 within 1-2 mV at
  every point a card holds, wider only at the 700 MHz transit points (aifoundry2 566-569, card 0 552-564 mV).
- **C3 (minor): "±1 mV in every session" holds for data-dir medians, not per run.** The table's "sessions (≥ 100
  samples)" column counts data dirs, and ±1 mV is the spread of their medians. Per run (each telemetry file with at least
  20 steady PVT samples at a point; `corrections-numbers.txt` § C3), the medians sit within ±2 mV of the card's:
  - aifoundry2 at 800 MHz reads 616-620 mV. 108 of 1,127 files are 2 mV low, their die 61.7 °C on average against
    57.8 °C for the rest (in 16 data dirs, most of them E143's, E87's, E96's and E83's).
  - aifoundry2 at 600 MHz reads 516-519 mV. 3 of 1,449 files are 2 mV low, at 80.8 °C (25 Sep's claims-v3 runs).
  - aifoundry3 reads 520-524 mV. 6 of 639 files are 2 mV low, at 74.9 °C (28 Sep's overheating and heat-placement runs).
  - card 0 and card 1 stay within 1 mV.

  So hot runs read up to 2 mV low, 0.8% in V², still under the 1% the text claims. **aifoundry2's 700 MHz point is a
  transit point** (governed ramps and throttles):
  - Of its 18,732 steady samples (the lane's rule: the previous record at the same clock), only 1,712 also have the next
    record at the same clock.
  - Busy and outside E143's dir, those read a median of 569 mV, but 36% of them read above 571 mV, over the 570 mV set
    point (p75 578, p95 590 mV: the rail still falling from 800 MHz's 620).
  - The lane's busy samples read 566-569 mV (p05-p95; mean 567.9).

  So that point's voltage is known to about 2 mV (567-569 mV) and s(700) to about 0.4% (1.4025 at 567.9 mV, 1.4080 at
  569). The verification read the settled value as 569 mV; the both-sides-steady median is that, with the falling tail
  above it.
- **C4 (minor): card 0's E118 voltages come from three data dirs**, not "four other sessions": `2026-10-21-dtf`,
  `2026-10-31-e84-speed-aifoundry1-card0` and `2026-11-01-e114-card0-replicates` (`clock-voltage.json` ›
  `E118_ratio.card0_v_never_E118_E60.dirs_600`, `dirs_800`).
- **C5 (minor): which "before" is E143's.** E143's registered scores are F1 6.629 MHz, W1 1.601 W, F2 1.007 MHz, W2 1.184 W
  and H1 0.585 °C (`results.json` › `score.rules`), which the kinds page quotes as 6.63 MHz, 1.60 W, 1.01 MHz and 1.18 W.
  The 6.64 MHz and 1.185 W in § What this does are A0 re-scored on unrounded predictions (6.635 / 1.601 / 1.007 / 1.185 /
  0.586). Quote "registered 6.63 MHz (6.64 re-scored) → 6.57" and "registered 1.18 W → 1.19".
- **C6 (minor): the window and the arm order.** The work ran 04:00-04:30 PST: the commit `8c16ab2d` is 04:29:28 PST, so the
  header's "04:00-04:50" ends after it. "The arms were chosen before E143 was scored on them (A0-A3 in the first run …)" has
  no surviving evidence, because only the final fit's outputs were kept. The work files show the ramp slopes were read
  before the final fit, consistent with "A4 added after", but not what any first run scored. Every arm is post hoc either
  way.
- **C7 (minor): what was read.** "Every committed telemetry record that carries the minion clock and a minion voltage was
  read" holds for every committed `.jsonl` / `.jsonl.gz` telemetry record and the `config*` reads. Not read, by the
  verification's count (not re-derived here; immaterial):
  - about 136 one-sample snapshots kept in `.json` / `.out` files (before/after snapshots, probe outputs, idle snapshots);
  - about 1,000 config-shaped reads in files not named `config*`;
  - five `.jsonl.raw` files, which sit beside `.jsonl.gz` copies that were read.

  136 of 4.37 M records is 0.003%.
