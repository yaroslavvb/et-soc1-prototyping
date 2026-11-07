# Dated note 1 beside README.md (Sat 7 Nov 2026, Q153(m10acc), the fix pass) - the verifier's five faults: F-P9 read in P8-M1's verdict words (BETTER for floats on card 1, WORSE for class S on both cards, not "NOT RESOLVED"), the entry rule's power stated, the nesting, E67's launch size and one citation; no number, rule or verdict changes, and neither term enters

*Sat 7 Nov 2026 (week 45), written about 12:30-13:00 PST on the Intel, desk only (no card, no lab box, no device command, no
Discord, no Modal), by Q153's fix pass for the lane m10acc. An independent verifier read the lane's four commits (`b5586759`,
`b48cf669`, `ceb643ca`, `d87bb417`), re-ran every output byte for byte, and held them **with fixes: two minor faults and three
nits**, none of which changes a number, a rule or a verdict. README.md, REGISTRATION.md, its dated amendment A1 and every committed
output stay as committed. This note corrects words and adds post hoc figures. **Neither M10-ACC nor A1's M10-ACC-L enters M10**, and
both stay reported arms for the next blind pool and for E182. Every figure below is computed from committed files by
[`../../../../tools/claims-v3/m10-acc/note1_m10acc.py`](../../../../tools/claims-v3/m10-acc/note1_m10acc.py) into
[`note1-m10acc.json`](note1-m10acc.json) and [`note1-m10acc.txt`](note1-m10acc.txt) beside this file, with the registered code
imported unchanged; the keys in parentheses are that json's.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read again Sat 7 Nov 2026 about 12:40 PST: public rows
   H20, H21 and H24 (opaque pointers). REGISTRATION.md's own block stands for everything else.
2. **Used.**
   - **This lane's committed rows and fit** (`d87bb417`): `rows-m10acc.json` and `rows-m10acc-a1.json` (each row's `e`, `e_prime`,
     `z`, `run`, `card`, `src`, `s_class`); `fit-m10acc.json` and `fit-m10acc-a1.json` (`families`, `forecasts_P9`, `posthoc`);
     `features-m10acc.json` and `-a1.json` (E67's features at its smallest, median and largest launch). *Check against the same
     quantity computed before:* the program first recomputes, from the rows, the leave-one-run-out errors, the frozen prices, R1's d
     and interval and every F-P9 interval, for both readings and both families. All equal the committed values, with a largest
     difference of 0 (`anchors`); otherwise it stops.
   - **The registered code, imported unchanged:** `tools/claims-v3/m10-acc/fit_m10acc.py` (`b48cf669`: `ols0`, `loro`, `design`,
     `rule`, `boot_d_runs`, `boot_d_kinds`; seeds 1532 and 1533; 2,000 draws).
   - **P8-M1's paired form** (H21, H24): `tools/claims-v3/p8-600/score_p8_600.py` › `paired()` (lines 163-177, `a518aa11`), imported;
     `tools/claims-v3/m10/pool8-registration.json` › `scoring` (`3e97f583`: 20,000 paired draws, seed 80000 plus the rule id's
     character codes); and the form's words in `docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8_a2.py` line 259,
     "BETTER if its upper end < 0, WORSE if its lower end > 0, else NOT RESOLVED".
   - **Q148(c)'s registration § 7** (`c71fbc7f`, `tools/claims-v3/m10-c/REGISTRATION.md`), the power template: the chance a rule
     reads BETTER at a true value, by simulation, "a figure of design, never a forecast or a verdict".
   - **Term S's data note 1 § 2** (H20; `aab4a5f9`, `docs/reports/data/2026-11-06-q145b-m10-s/README.md.dated-note-1.md`, with
     `note2-checks.json` › `by_list_and_A_99`), for N5.
   - **M10's rows** (H21; `6829c9ba`, `docs/reports/data/2026-11-04-q142m-m10/rows-m10.json` › `err_w`) and M10's README line 25
     ("leave one kind out"), for N3.
3. **Not used.** M10 refitted inside the term's 39 folds (N3 says why the verdict stands without it); any card, bench or trace run
   (no new feature is needed); the verifier's own scratch files (its figures appear here only where this note's program re-derives
   them).
4. **Tiers.** Public tier only: the lab's committed data and code. No NDA-tier piece is used, so there is no sha256 line.
5. **Readiness:** this block is the note's own.

## N1. F-P9 in P8-M1's words (fault 1, minor)

REGISTRATION.md § 5 scores P9-ACC "paired, in P8-M1's form, BETTER / WORSE / NOT RESOLVED". That form has no resolution floor: it
reads BETTER when the paired interval's upper end is below 0 and WORSE when its lower end is above 0. README.md's Forecasts,
bullet 1, ends "under any card's resolution, so P9-ACC is forecast NOT RESOLVED". **Those words are withdrawn.**

Here are the committed F-P9 (REGISTRATION.md § 6's bootstrap over kinds: 2,000 draws, seed 1533; `fit-m10acc.json` ›
`forecasts_P9`) read in the form's words. Beside them is P8-M1's own `paired()` on the same rows, at 20,000 draws. It uses the seed of
P8-M1f for floats (80409) and of P8-M1i for int8 (80412), as a stand-in for P9's own seed (`N1.primary`).

| set (pool 8's rows, held out by run) | n | d, W | registered interval | in P8-M1's words | P8-M1's `paired()` |
|---|---:|---:|---|---|---|
| floats, aifoundry3 | 25 | −0.0024 | [−0.0070, +0.0005] | NOT RESOLVED | [−0.0070, +0.0006] NOT RESOLVED |
| floats, card 1 | 25 | −0.0044 | [−0.0082, −0.0013] | **BETTER** | [−0.0083, −0.0012] BETTER |
| floats, class S, aifoundry3 | 8 | +0.0011 | [+0.0010, +0.0013] | **WORSE** | [+0.0010, +0.0013] WORSE |
| floats, class S, card 1 | 8 | +0.0005 | [+0.0003, +0.0007] | **WORSE** | [+0.0003, +0.0007] WORSE |
| int8, aifoundry3 | 15 | +0.0027 | [−0.0013, +0.0061] | NOT RESOLVED | [−0.0011, +0.0061] NOT RESOLVED |
| int8, card 1 | 15 | +0.0004 | [−0.0020, +0.0025] | NOT RESOLVED | [−0.0020, +0.0026] NOT RESOLVED |

- **Class S reads WORSE by about a milliwatt.** The term moves each of those eight tiles by nearly the same small amount, so the
  paired interval over them is narrow.
- **A1's F-P9** (`fit-m10acc-a1.json` › `forecasts_P9`; README.md does not state it): NOT RESOLVED for floats and int8 on both cards,
  and WORSE for class S on both cards, at +0.0081 W [+0.0032, +0.0122] and +0.0056 W [+0.0012, +0.0100] (`N1.A1`).
- **What these are.** They are forecasts from held-out errors, not a test (REGISTRATION.md § 6), and pool 8 is post hoc for this
  term. Neither term entered, so P9-ACC is not a rule of the next blind pool (§ 5, "Otherwise"). There, M10-ACC and M10-ACC-L are
  reported arms, read in these same words.

**The headline's one exception.** README.md's title says the term carries "nothing M10 does not already price". Every held-out
reading R1-R3 use is worse with the term. Of the other committed held-out readings (by format, card and source, `fit-output.txt`),
one is better, and README.md's table does not show it: pool 8's 50 float rows (source b, both cards), held out by run, read
**0.1940 → 0.1906 W, d −0.0034** (bias +0.0975 → +0.0892 W; `fit-m10acc.json` › `families.float.readings_heldout.source b`). Its
card-1 half is the BETTER above, and it is post hoc for this term. int8's 30 pool-8 rows read 0.1306 → 0.1321 W (d +0.0016). With
A1, pool 8's rows read d −0.0008 W for floats and −0.0031 W for int8.

## N2. The rule's power (fault 2, minor)

The registration states no power for R1-R3 or P9-ACC; Q148(c)'s § 7, its template, did. Everything in N2 is post hoc (computed after
the fit) and decides nothing. A true price t enters as t × z, added to M10's committed errors, where z is the term's own regressor
(s × c × rate × x). The term's held-out errors e' do not change: the fit is linear in the response, so each fold's price moves by
exactly t. The program checks this to 5e-16 W (`N2.<reading>.linearity_check_max_abs_w`).

**(a) The price at which the rule holds on these data.** R1-R3 as registered, with the runs bootstrap at 2,000 draws and seed 1532,
read on a grid of 0.1 fJ for accumulator prices and 0.01 fJ for Booth prices (`N2.<reading>.detectable_price`):

| reading, price | registered 95% (jackknife) | R1 first holds at (+ / −) | the rule first enters at (+ / −) |
|---|---|---|---|
| M10-ACC floats, τ_acc | [−3.31, +3.55] fJ | +5.7 / −5.7 fJ | **+5.7** / −18.0 fJ |
| M10-ACC floats, τ_bth | [−0.14, +0.26] fJ | +0.33 / −0.42 fJ | **never, up to +4.0** / −0.42 fJ |
| M10-ACC int8, τ_acc | [−1.00, +0.83] fJ | +2.1 / −1.8 fJ | **+2.1** / −1.8 fJ |
| A1 floats, τ_L | [−1.07, +0.52] fJ | +1.5 / −1.3 fJ | **+1.5** / −5.2 fJ |
| A1 floats, τ_bth | [−0.05, +0.29] fJ | +0.27 / −0.41 fJ | **never, up to +4.0** / −3.98 fJ |
| A1 int8, τ_L | [−0.17, +0.53] fJ | +0.6 / −0.9 fJ | **+0.6** / −0.9 fJ |

**(b) The chance the rule lets the term in at a true price.** This is the template's form. Runs are resampled with replacement
1,000 times (numpy `default_rng(1534)`), and each resample is read by R1-R3 with its own 2,000-draw runs bootstrap. The program first
checks that, on the data as they are, its run sums give R1's committed d and interval to 1e-16 W (`N2.<reading>.chance`).

| reading, price | t = 0 | at the interval's upper end | at (a)'s price | at 1.5 × (a)'s | at 2 × (a)'s |
|---|---:|---:|---:|---:|---:|
| floats τ_acc | 0.000 | 0.26 (+3.55 fJ) | 0.58 (+5.7) | 0.86 (+8.55) | 0.97 (+11.4) |
| floats τ_bth | 0.000 | 0.011 (+0.265) | 0.016 (+0.33)* | 0.044 (+0.495)* | 0.051 (+0.66)* |
| int8 τ_acc | 0.000 | 0.07 (+0.83) | 0.56 (+2.1) | 0.89 (+3.15) | 0.98 (+4.2) |
| A1 floats τ_L | 0.000 | 0.001 (+0.52) | 0.54 (+1.5) | 0.85 (+2.25) | 0.97 (+3.0) |
| A1 int8 τ_L | 0.000 | 0.55 (+0.53) | 0.63 (+0.6) | 0.92 (+0.9) | 1.00 (+1.2) |

\* For τ_bth, (a)'s price is where R1 first holds. There, R1 holds in 0.55 of the resamples, rising to 0.99 at +0.66 fJ, but R3 holds
in only 0.05 of them at every positive Booth price; A1's R3 holds in none. At the intervals' lower ends the chance is 0.000 (floats
τ_acc, −3.31 fJ), 0.15 (int8, −1.00 fJ) and 0.000 (A1 floats, −1.07 fJ).

What (a) and (b) say:
- **For the floats' accumulator price**, the rule lets the term in with chance about a half only at +5.7 fJ a toggle, beyond the
  registered interval's upper end (+3.55 fJ), where its chance is 0.26. So a price the data allow was unlikely to enter. "Does not
  enter" says the price is not large; it does not say the price is 0. int8 is the same: 0.07 at its upper end (+0.83 fJ), and a half
  at +2.1 fJ. A1's int8 reading is the exception, at 0.55 at its interval's upper end (+0.53 fJ).
- **R3 makes the floats' rule blind to a Booth price.** The S class's tiles carry almost none of x_bth: at τ_bth's upper end
  (+0.265 fJ) the Booth part adds +0.0005 W to them on average, against +0.024 W on the other whole float tiles
  (`N2.primary.class_S_shift_at_interval_end`). So a Booth price barely moves M10's errors there, and R3 keeps reading the term's small
  S-class worsening (+0.0004 W, growing to +0.0035 W at +4 fJ). At every positive Booth price read, the rule enters with chance at
  most 0.051, and A1's never.
- **For the floats, a negative accumulator price enters only far outside its interval:** −18.0 fJ against −3.31 (A1: −5.2 against
  −1.07). M10's errors on the S class are biased positive, so a negative price makes them smaller, and R3 then reads the term worse.

**(c) The S class at the interval's end** (`N2.primary.class_S_shift_at_interval_end`):
- **At τ_acc's upper end (+3.553 fJ)** the term would add +0.041 W on average to the S class's 42 rows (+0.051 W at most) and
  +0.030 W to the other 702 whole float tiles: +0.011 W more on class S. On pool 8 it would add 0.005 W less to the class-S tiles than
  to pool 8's other float tiles.
- **With the Booth price at its upper end too,** class S gains 0.013 W less than the other tiles.
- **Against the excess:** the S class's held-out excess is +0.104 W over its 42 rows, and +0.195 / +0.138 W on pool 8's class S
  (`fit-m10acc.json` › `families.float.readings_heldout.S class`, `posthoc.pool8_class_S`).

So even at the edge of what the data allow, the term carries at most about a tenth of class S's excess (+0.011 against +0.104 W),
and none of pool 8's. README.md's post hoc conclusion stands: class S's miss is not in the accumulator beyond M10. A1 at its upper end (+0.518 fJ) gives +0.019 W against
+0.017 W, +0.003 W more on class S.

**(d) P9-ACC's chances on a pool drawn like pool 8.** This is the form the next blind pool would have used had the term entered.
Pools of pool 8's size are drawn with replacement from its held-out rows, 1,000 pools, each read in P8-M1's form at 2,000 draws with
the form's order statistics (`default_rng(1535)`; `N2.<reading>.P9_chances`):

| set (n) | t = 0: BETTER / WORSE / NOT RESOLVED | BETTER at the interval's upper end | BETTER at (a)'s price |
|---|---|---:|---:|
| floats, aifoundry3 (25) | 0.30 / 0.00 / 0.69 | 0.93 (+3.55 fJ) | 0.98 (+5.7) |
| floats, card 1 (25) | 0.87 / 0.00 / 0.13 | 0.97 | 1.00 |
| floats, class S, aifoundry3 (8) | 0.00 / 1.00 / 0.00 | 0.88 | 0.91 |
| floats, class S, card 1 (8) | 0.00 / 0.88 / 0.12 | 0.62 | 0.72 |
| int8, aifoundry3 (15) | 0.00 / 0.36 / 0.63 | 0.57 (+0.83) | 0.89 (+2.1) |
| int8, card 1 (15) | 0.01 / 0.08 / 0.91 | 0.22 | 0.61 |

- **The paired form is far more sensitive than the entry rule.** At the interval's upper end it would read BETTER on pool-8-like
  floats with chance 0.93-0.97, where R1-R3 let the term in with chance 0.26.
- **The same sensitivity reads the term's milliwatt differences at t = 0:** WORSE on class S, and BETTER on card 1's floats.
- **The chances are conditional on pool 8's rows.** M10's float errors there are biased +0.0975 W (`source b`), the sign a positive
  price adds to.
- **A1 at t = 0** reads NOT RESOLVED most often for floats (0.92 / 0.85) and int8 (0.72 / 0.92), and WORSE on class S (0.91 / 0.72)
  (`N2.A1.P9_chances`).

**For the next term's registration:** state the power before any data, in Q148(c)'s § 7 form: the price the rule detects, and its
chances under the rule and under the pool-level form. A class rule like R3 should read a class that the feature exercises.

## N3. The nesting (nit)

Rows (a)'s responses are M10's committed held-out errors, `rows-m10.json` › `err_w`: all 959 are equal, exactly (`N3`). Those errors
are leave one kind out (M10's README line 25). Each of those M10 fits left out one kind, not one run, so run R's measurements of the
other kinds were inside the M10 fits that made the other runs' responses. The term's fold that leaves run R out is fitted on those
responses, so run R's measurements reach τ_(−R) through M10's fits. REGISTRATION.md § 9 names only the fold-scale point. A clean nesting would refit M10 inside each of the term's 39 folds, and that is not done here. Any such leak would flatter the
term's held-out errors, and the term fails its rule anyway, so "does not enter" stands.

## N4. E67's launch size (nit)

REGISTRATION.md § 9 says "the launch-size sensitivity of the frozen term is stated", but README.md gives only E67's x_acc steps. Here
it is, with E67's four steps at its smallest, median and largest launch (269,962 / 456,502 / 543,669 ops) (`N4`):
- **M10-ACC:** the frozen float prices read τ_acc +0.1242 / +0.1236 / +0.1235 fJ, and τ_bth +0.0647 fJ throughout. d stays +0.0013 W,
  and the rule does not enter at any of the three.
- **A1:** τ_L reads −0.2779 / −0.2778 / −0.2777 fJ, τ_bth +0.1201 fJ and d +0.0008 W.

E67's launch size does not matter to either term.

## N5. The by-A-word table's citation (nit)

REGISTRATION.md cites "term S's dated note 2 § 2" for M10's step error by A word, A = π −0.438 W over 5 steps against A = 1.0's
−0.066 W over 70 (its Builds on, lines 66-67; and § 1, line 123). That table is in
`docs/reports/data/2026-11-06-q145b-m10-s/README.md.dated-note-1.md` § 2 (`aab4a5f9`). Its source is `note2-checks.json` ›
`by_list_and_A_99` › `by_A`: `fp32 A 40490fdb`, n 5, bias −0.4377 W; `fp32 A 3f800000`, n 70, bias −0.0656 W.

Term S's `tools/claims-v3/m10-s/REGISTRATION.md.dated-note-2.md` § 2 is about E1's interval and holds no such table; its § 1 points
to the data note for the figures (`N5`). Read both citations as the data note's § 2. The reason they give for the Booth feature is
unchanged.

## For the records round

- **F-P9, quote:** "F-P9, read in P8-M1's form (no resolution floor): floats BETTER on card 1 (d −0.0044 W [−0.0082, −0.0013]) and
  NOT RESOLVED on aifoundry3; class S WORSE on both cards (+0.0011 and +0.0005 W); int8 NOT RESOLVED on both. Neither term entered,
  so these are readings of reported arms, not rule verdicts." Never "P9-ACC is forecast NOT RESOLVED".
- **The headline, quote:** "M10-ACC fails its entry rule in both families; its one held-out gain is on pool 8's 50 float rows,
  0.1940 → 0.1906 W (post hoc)." Never "carries nothing M10 does not already price" without that clause.
- **The power, quote:** "R1-R3 would let a float accumulator price in with chance about 0.6 at +5.7 fJ a toggle, and 0.26 at the
  registered interval's upper end (+3.55 fJ); 'does not enter' bounds the price, it does not set it to 0. R3 makes the floats' rule
  blind to a Booth price."
- **Labels:**
  - **registered:** N1's verdict words, which apply the registered form (§ 5) to the registered forecast (§ 6), with pool 8 post hoc
    for this term;
  - **post hoc:** N2's figures (design figures, deciding nothing), N3's check and N4;
  - **correction:** N5;
  - **blind:** nothing.

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| [`note1-m10acc.json`](note1-m10acc.json) | every figure above, by section, with the inputs' sha256 |
| [`note1-m10acc.txt`](note1-m10acc.txt) | the same, as text |
| [`../../../../tools/claims-v3/m10-acc/note1_m10acc.py`](../../../../tools/claims-v3/m10-acc/note1_m10acc.py) | the program |
| [`../../../../tools/claims-v3/m10-acc/REGISTRATION.md.dated-note-1.md`](../../../../tools/claims-v3/m10-acc/REGISTRATION.md.dated-note-1.md) | a pointer to this note, beside the registration |
| [`SHA256SUMS-note1`](SHA256SUMS-note1) | these five files and the program's 20 inputs |

**Re-run.** From the top of the tree, with `/usr/bin/python3` (3.9.6, numpy 1.26.4, scipy 1.13.1):
`python3 -B tools/claims-v3/m10-acc/note1_m10acc.py run --out <dir>`. It takes about 85 s on one core and refuses to write over a
file. Two runs gave byte-identical files.

SPDX-License-Identifier: Apache-2.0
