# Q136(b): the rail ledger's off-rail row, re-cut on a drift-corrected footing

*This answers item 16, "The rail ledger's off-rail row", in the kinds page's
[section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), and
the work (a) of the final critic's item 7 (Q134(f), Mon 2 Nov 2026): re-cut the row on a drift-corrected footing from
E77's and E120's launches, attribute the footing difference to the window's heating with their measured board drift,
and check whether the September catalogue's raw files carry the die readings a refit needs. It is a desk lane, Mon 2 Nov
2026 (week 45, PST). Every number in it is post hoc: nothing was pre-registered, no card was touched, no device command
was sent and nothing was set. It reads only committed files: [E77](../2026-11-01-e77-rail-one-temperature/README.md),
[E120](../2026-11-01-e120-rail-redesign/README.md) (its correction CV1 is what this re-examines), the
[rail ledger](../2026-10-27-q129-rail-ledger/README.md) (Q129), the energy manual's
[`unmetered_fit.json`](../2026-09-23-energy-manual/unmetered_fit.json) and the catalogue it was fitted on.*

*Corrected after an independent verification the same morning (Mon 2 Nov 2026, about 08:05 PST), at the desk: no card
touched, nothing set, no device command sent. Wrong sentences are replaced in place, each marked;
[Corrections after verification](#corrections-after-verification-mon-2-nov-2026) lists F1–F8, and
[`corrections-check.txt`](corrections-check.txt) prints every new number from committed files
([`corrections-check.py`](corrections-check.py), on `recut.py`'s own functions and E77's registered reduction). No number
in `recut.json` or `recut.txt` changed. The two major ones: E77's post hoc conduction reading was given, in E120's form,
as a pass by the registered rules, where E77's own registered form does not resolve the term (F1); and the list of texts
this re-cut overturns left several out (F2).*

## Results first

1. **The row's coefficient was fitted on leakage-corrected board deltas, not on uncorrected ones.** The published
   minion coefficients, 0.18789 on aifoundry2 and 0.18098 on aifoundry3, reproduce from `catalogue.json` to 3e-17 with
   `tools/ettelem/fit_unmetered.py`'s formula, and the board delta that formula reads, `over_idle_w`, is corrected:
   `over_idle_raw_w` less the idle law's slope (23.257/36·e^((T−80)/36) W/°C, `workloads/enercat/analyze_catalogue.py`)
   times the burst's die rise over its idle. That slope is 0.547 W/°C at aifoundry2's median busy die of 74.0 °C and
   0.351 W/°C at aifoundry3's 58.0 °C (median correction 0.32 and 0.19 W). Only the rails are raw. So the fit sits on the
   ledger's *board_only* kind of footing at the catalogue's own temperatures. On the raw board the same fit gives **0.249
   and 0.216** (`recut.json` `catalogue.<card>.published`, `.uncorrected`, `.board_correction`). E120's CV1 and the final
   critic's item 7 say "fitted on uncorrected over-idle deltas"; the rail ledger's README had it right ("the published
   off-rail fit is calibrated against a *corrected* board").

2. **E120's "about 0.4 pJ" is the registered correction slope, not the window's heating.** E77's and E120's central
   footing (drift_split) takes **0.81 W/°C**, E38's aifoundry2 slope near 81 °C, times each window's die rise. These
   blocks launched at 52–55 °C. There their own body-window board drift is **0.267 ± 0.098** (E77) and **0.351 ± 0.119**
   (E120) W/°C, one s.e., so 0.81 is 3.0× and 2.3× theirs, 5.5 and 3.8 s.e. above; the card's idle law gives 0.30–0.32
   W/°C at these temperatures. A second estimator, free of the regression on whole-degree die readings (the board over
   [t1−1, t1] less over [t0+1, t0+2] across arm A's launches), puts both blocks well below 0.81: it agrees for E120,
   0.298 (bootstrap 95% 0.257–0.339; its 8 s rung 0.345), and runs higher for E77, 0.459 (0.386–0.592)
   (`recut.txt` B2). *(Corrected after verification, F4: the first version said the second estimator agrees.)* **Most of
   the excess is in how drift_split splits the slope, not in the temperature it was measured at.** On E38 near 81 °C,
   0.45 of the board's 0.73 W/°C was the metered rails' own drift and 0.275 ± 0.038 W/°C the off-rail's, about what these
   blocks' off-rails drift at 52–55 °C (0.204 ± 0.093 and 0.324 ± 0.086). drift_split hands the 0.81 out by each block's
   own shares, and here the rails barely drift, so 76% and 92% of it, 0.62 and 0.75 W/°C, came off the off-rail; split as
   E38's own drift was, it would have taken 0.31 (`corrections-check.txt` F5). *(Added after verification, F5: the first
   version put the excess down to the slope's temperature alone.)* Attributed with each block's own drift, the window's
   heating is **33% (E77) and 43% (E120)** of the gap between the uncorrected and central footings' in-step slopes
   (21–45% and 29–58% at one s.e.). The rest of the gap, 0.08 W per minion W in both blocks, is the registered slope's
   excess over the block's own drift.

3. **Re-cut on drift-corrected footings, the row is 0.75–1.05 pJ as a straight line and 0.82–1.16 pJ with a conduction
   term, so the published 0.875 pJ stands.** *(Corrected after verification, F3: the first version gave the straight
   line's band alone.)* The in-step coefficient is the off-rail watts that grow with the minion rail, per minion watt, at
   600 MHz (arm A, the row's own clock and voltage). The row is the ledger's own arithmetic (`rail_ledger.py`
   `apply_footing`, the central footing, carried onto Q128's 5.783 pJ board) with the coefficient replaced:

   | data, footing | coefficient, W per minion W | row, pJ |
   |---|---|---|
   | published (`unmetered_fit.json`) | 0.188 / 0.181 | **0.875** |
   | E120, its own drift (passes and drift s.e., approx. 95%) | 0.161 [0.129, 0.193] | 0.75 |
   | E77, its own drift | 0.193 [0.157, 0.229] | 0.90 |
   | **E77 and E120 combined** | **0.175 [0.151, 0.199]** | **0.82 [0.70, 0.93]** |
   | the same at the two-window drift (E120 / E77) | 0.170 / 0.165 | 0.79 / 0.77 |
   | the catalogue's own correction rule applied to E120 / E77 | 0.163 / 0.168 | 0.76 / 0.78 |
   | **the catalogue refitted on its die readings** (each element on its own window's rise, the rails' rise through their own filter) | **0.234 / 0.207** | **1.05** (1.04 with the rails' slopes scaled to its temperature) |
   | no heating attributed (E120 uncorrected / the catalogue's raw board) | 0.224 / 0.249, 0.216 | 1.04 / 1.10 |
   | E120's CV1 (registered drift_split, 0.81 W/°C) | 0.080 | 0.37 |
   | *added after verification (F3):* the models with a conduction term, at the row's own operating point (result 4) | — | **0.82** (E120), **0.98** (E77), **1.14–1.16** (the catalogue) |
   | E77 and E120, arm A through the origin (the published fit's no-intercept form; not used, below) | 0.149 (E120 0.132, E77 0.170) | 0.69 |
   | the catalogue with its heating free (checks, set aside below): the board's rise free; both rises free | 0.251 / 0.229; 0.267 / 0.248 | 1.14; 1.22 |

   The two blocks differ by 0.032 ± 0.025 W/W, within their errors. The catalogue refit on that footing also fits its
   392 configurations better than any other footing: rms 0.295 and 0.287 W, against the published 0.332 and 0.308
   (`recut.txt` C; the fits that add a conduction term reach 0.282). The ledger's off-rail on E38 is 1.017 pJ, so the
   fit's residual moves from 0.142 pJ to between −0.03 and +0.27 pJ (+0.20 at the combined coefficient), its upper end at
   the edge of the −0.23 to +0.26 pJ the ledger's three footings give it (`corrections-check.txt` F3). *(Corrected after
   verification, F3: the first version said "still consistent with zero as the ledger read it".)* **E120's CV1 reading,
   "the row itself is in question", does not survive.** (`recut.json` `instep_coefficient`, `row.cases`,
   `measured_split_uncertainty`)

   **Why a slope with an intercept, and which checks are set aside** *(added after verification, F3)*. The published fit
   has no intercept. Through the origin, E77's and E120's arm A give 0.170 and 0.132 W per minion W, rows of 0.79 and
   0.61 pJ, 0.69 combined. They come out lower because in all eight arm-A passes the rung means lie on a line with a
   negative intercept, −0.24 to −0.48 W, near the −0.46 (E77) and −0.37 W (E120) that each block's post hoc conduction
   term puts on a line over the same rungs: the off-rail curves up with the load, and a line forced through the origin
   folds that curve into its coefficient. The models that carry the curve as a conduction term pass through the origin
   themselves, and at the row's own operating point they come out above the straight line, not below it (0.82, 0.98 and
   1.14–1.16 pJ). So the slope with an intercept is the straight line's in-step coefficient, and the 0.69 pJ is reported,
   not used (`corrections-check.txt` F3). The two catalogue fits that let the heating be free give 1.14 and 1.22 pJ
   (`recut.txt` D). They are checks only. The die's rise grows with the load (its correlation with the minion rail across
   configurations is 0.78–0.80), so a free heating slope trades against the minion coefficient, whose standard error
   grows 3.5–4-fold. With the rails raw, the one free slope has to carry the rails' heating, which lowers the off-rail,
   as well as the board's, and comes out at −0.02 ± 0.10 and −0.13 ± 0.09 W/°C. With the rails' rise free too, the slopes
   take the expected signs (board +0.38 ± 0.13 and +0.24 ± 0.12, rails −0.39 ± 0.08 and −0.38 ± 0.08 W/°C), the board's 1.3
   and 1.0 s.e. under the idle law's 0.55 and 0.35 at the catalogue's temperatures, and heat they leave in the window
   raises the minion coefficient (`recut.txt` C). Both rows lie above the straight line's band, on the side the
   heating-timescale caveat below names.

4. **The regulators' conduction share is not settled; post hoc, a third to two thirds of the row.** The registered
   verdicts stand: E120 FAIL, not resolved, R_eff 0.55 mΩ, 99% [−0.06, +1.16], at most 0.69 pJ of the row; and E77 FAIL,
   provisional, 0.62 mΩ, 99% [−0.49, +1.73], in its own form. On each run's own drift (post hoc), in E120's registered
   offset form, the term is resolved in both blocks; in E77's registered form (SRAM and NoC free, no offset) it is not for
   E77, and only marginally for E120. The catalogue's curvature, at its single voltage, finds it too. *(Corrected after
   verification, F1: the first version said "the term is resolved in both blocks" and gave E77's reading in E120's form
   as a PASS by the registered rules, with E77's own verdict only "provisional".)* Both forms are read by the same rules
   (PASS: the 99% interval excludes 0 and the pooled rms falls by 30% or more; NEITHER: it excludes 0 but the rms falls
   less; FAIL: it holds 0; `corrections-check.txt` F1, which first reproduces E77's registered fit and E120's registered
   secondary in E77's form):

   | data, drift-corrected footing (post hoc) | R_eff, mΩ, 99% over passes | read by the registered rules |
   |---|---|---|
   | E120, in E120's offset form | 0.740 [0.313, 1.167] | NEITHER, resolved but not material (rms better by 6.0%) |
   | E120, in E77's registered form | 0.606 [0.040, 1.171] | NEITHER (rms better by 3.8%); FAIL at +1 s.e. of the board drift, and with the drift's s.e. added |
   | E77, in E120's offset form (E77 registered no offset) | 0.823 [0.394, 1.252] | PASS in that form (rms better by 40.8%); NEITHER at +2 s.e. of the board drift |
   | E77, in E77's registered form | 0.795 [−0.296, 1.887] | FAIL (rms better by 39.8%), as its registered verdict is: FAIL, provisional |
   | the catalogue, aifoundry2 / aifoundry3 | 0.637 ± 0.109 / 0.416 ± 0.113 (1 s.e.; 0.521 / 0.401 with the rails' slopes scaled) | — |
   | the catalogue on the published footing | 0.033 ± 0.120 / 0.167 ± 0.120 | — |

   On the published footing the catalogue sees no conduction term, which is why the ledger's square-term test found
   none. The term appears once each rail is corrected for its own heating. With its rails left raw (measured_board_only)
   it reads only 0.145 and 0.189 mΩ, so the catalogue's value rests on the ledger's rail slopes.

   **As a share of the row, at the row's own operating point.** That point is E38's idle minion rail, 13.54 W
   (aifoundry2) and 7.97 W (aifoundry3), and its step of about 21.5 W, where I²R weighs more than at E120's 6.75 W idle.

   | model | row, pJ | conduction, pJ |
   |---|---|---|
   | E120, its offset form | 0.82 | **0.57 (69%)**; 0.24–0.89 over R's 99% interval (33–98%) |
   | E77, in E120's offset form | 0.98 | **0.63 (64%)**; 0.30–0.96 (33–90%) |
   | the catalogue, its curvature's R | 1.14–1.16 | **0.36–0.41 (32–36%)** |

   At E120's own point, in B's conversion, the conduction term is 0.44 [0.19, 0.70] pJ (E120) and 0.49 [0.24, 0.75] pJ
   (E77, in E120's form), 99% over R. Read beside the registered B, 0.33 [−0.04, 0.69], 99%. *(Labels added after
   verification, F1 and F6.)* So, post hoc, **the regulators' conduction is probably there, at about 0.4–0.8 mΩ, a third
   to two thirds of the row**, though only E120's offset form resolves it in both runs: in E77's registered form neither
   run resolves it firmly. *(Qualified after verification, F1: the first version said "probably real".)* The rest of the
   row is not split between the regulators' current-proportional losses (switching) and off-rail logic in step: E120's
   design tests only the I² term (`recut.json` `conduction`, `at_the_rows_operating_point`,
   `catalogue.<card>.conduction_from_curvature`).

5. **The September catalogue's raw files carry the die readings a refit needs.** `unmetered_fit.json` itself holds
   none: its rows are configuration means of watts. But every burst in `catalogue.json` carries `die_c_busy`,
   `die_c_idle` and `die_c_before`. Every sample of its raw telemetry
   (`../2026-09-25-claims-v3/raw/<card>/catfull/p*/telemetry.jsonl.gz`, nine blocks per card) carries
   `temp_c.minshire`, in whole degrees at about 45 Hz. The raw files reproduce `die_c_busy` and `die_c_before` to
   within 5e-7 °C on both cards, every burst matched, and the 392-configuration refit of result 3 is made from them.

## What it changes

- **The Horace hub's Levels tab, stop 8.** Since the Q134 hub pass its Q129 sentence says the 1.009 pJ "is mostly the
  ledger's 0.875 pJ off-rail row … of which the regulators' conduction is at most 0.69 pJ". The final critic quoted the
  earlier "mostly the regulators' delivery loss". Suggested replacement for the bold Q129 sentence:

  > **Q129: the die's share is measured — the minion rail carries 4.774 pJ of the board's 5.783 per random fp32
  > multiply-add, a ratio of 0.825 [0.787–0.856], and most of the 1.009 pJ between them is the ledger's 0.875 pJ
  > off-rail row, power off every metered rail that grows with the minion rail (the regulators' delivery loss plus logic
  > in step); re-cut post hoc on drift-corrected footings (a desk re-cut, Q136(b)) it is 0.75–1.05 pJ as a straight line
  > and 0.82–1.16 pJ with a conduction term, so it stands. How much of it is the regulators' conduction is not settled:
  > neither registered test resolved it (E120: at most 0.69 pJ, 99%), and post hoc, on each run's own drift, E77, E120
  > and the catalogue each show a conduction term of about 0.4–0.8 mΩ, a third to two thirds of the row, though in E77's
  > registered form neither run resolves it firmly**

  *(Labels and the conduction models' band added after verification, F1, F3 and F6.)*
- **Every text that carries the premises this re-cut overturns** *(list completed after verification, F2)*. The
  premises are "one coefficient fitted on uncorrected deltas" (or "an uncorrected fit") and "its drift-corrected footing
  measures only about 0.4 pJ … so the row itself is in question" (or "less than half the row"). They stand in:
  - the kinds page: section 9's paragraph "What the rails do not carry, and the regulators' share of it", and section
    11's item 16;
  - the Horace hub: Levels stops 2 (its Missing column) and 8; in the Status tab, its opening paragraph, its account of
    what Q134 did to the list, both copies of item 16, the ranked item 7 (whose desk step this re-cut is: done) and
    Next's "a second governor move for the off-rail row". The Log stays as written: a new entry carries the re-cut;
  - the lab's records: `02-requests.md`'s Q134 row; `03-experiments.md`'s E120 entry (B's post hoc paragraph and What
    it changes) and its lesson 46; `05-claims.md`'s board-to-rail step row, its "E120's bound" row and the Q134
    section's row on Q129's ledger;
  - E120's README (below).

  Each gets the re-cut, labelled post hoc: the coefficient was fitted on board deltas corrected with the idle law's
  slope, the rails raw (result 1); the 0.4 pJ is drift_split putting E38's mostly-rail 0.81 W/°C onto the off-rail of
  runs whose own board drift is 0.27–0.35 W/°C (result 2); the row re-cut is 0.75–1.05 pJ as a straight line and
  0.82–1.16 pJ with a conduction term (result 3). Item 16 stays open, now for registering the conduction term and for
  the split of the rest of the row, and links this README.
- **E120's README:** dated notes, its frozen text unedited, on four passages: the Results head ("the row was fitted on
  uncorrected deltas … only about 0.4 pJ"), CV1, What it changes ("about 0.4 pJ, less than half the row … the row's
  uncorrected fit") and the CV1 row of its corrections table; its `corrections-check.py` and `.txt` label the coefficient
  "uncorrected deltas" too, and the notes cover them. They should say three things. The coefficient was fitted on
  corrected board deltas. The "0.08–0.10 W per minion W" uses the registered 0.81 W/°C, 2.3× the block's own board
  drift, which drift_split put almost all onto the off-rail. On the block's own drift the in-step slope is 0.161 (arm A)
  and 0.168 (arm B) W per minion W, and the row re-cuts at 0.75–1.05 pJ. *(Passages beyond CV1 added after verification,
  F2.)* Optionally, a dated note on E77's S-T paragraph: its registered drift_split takes 3.0× the block's own board
  drift at 55 °C.
- **For a re-run of E120 (the critic's item 7, work (b), which needs a governor move and his OK):** it would measure
  against an in-step coefficient of 0.175 [0.151, 0.199] W per minion W (approx. 95%; [0.147, 0.199] with t on the
  passes) and R_eff 0.74–0.82 mΩ in E120's offset form (0.61–0.80 in E77's) on the measured-drift footing. Register as
  the central footing the block's own drift (body windows, with the two-window estimator as its check), not 0.81 W/°C,
  and one form for the conduction term. A rung launched at two die temperatures would measure the off-rail's
  temperature coefficient at a fixed load directly.
- **For the blog material:** of the step between the board and the core rail, most is power off every meter that grows
  with the work. Re-cut post hoc, it stands at about 0.75–1.05 pJ of a 5.8 pJ random fp32 multiply-add as a straight
  line, 0.82–1.16 pJ with the regulators' square-law loss in the model. Probably a third to two thirds of it is that
  I²R loss (post hoc; no registered test resolved it), which grows with the square of the current, so a lower rail
  voltage at the same power costs more there.

## How it was done (`recut.py`)

- **E77 and E120.** Per kept work launch, `results.json`'s rows are re-footed six ways. Each footing takes a slope
  × the window's die rise (T_win − T_launch, the registered rise) off the board, or off each element:
  - uncorrected;
  - the registered drift_split and board_only (0.81 W/°C);
  - **measured_split**, the block's own body-window drift for the board and for each rail (`results.json` `drift`);
  - measured_board_only;
  - the catalogue's own rule (the idle law's slope at the launch's temperature, off the board alone).

  The rails keep their registered settling ratios. Rung means come next, then each arm's least-squares slope of
  off-rail on minion watts, per pass, the pass being the unit of replication. The measured_split slope is linear in the
  off-rail drift (`offrail_drift_sensitivity`), so the drift's standard error, from the per-launch off-rail drifts
  (0.204 ± 0.093 and 0.324 ± 0.086 W/°C), is propagated beside the pass spread. The registered offset form,
  offrail = a_m·Δm + c_B·[B] + R_eff·[((m₀ + Δm)/V)² − (m₀/V₀)²], is refitted on every footing. The registered numbers
  are reproduced first: E120's V (0.546 [−0.064, 1.157] mΩ, rms 2.9%), its uncorrected and board_only secondaries, CV1's
  0.0808 / 0.0991 and 0.2242 / 0.2341, E77's post hoc 0.210 [−0.076, 0.496] mΩ, and B's 0.327 / 0.693 pJ.
- **The catalogue.** `fit_unmetered.py`'s fit (configuration means over three passes, no intercept, DRAM bytes as
  published) is refitted per card on each footing:
  - The board's rise is `die_c_busy − die_c_idle`, the window its correction already uses.
  - The rails are read over [t_hi − 0.6, t_hi] against an idle before the burst (`analyze_catalogue.py`). Their rise
    is the die there less `die_c_before`, taken from the raw telemetry. In the *filtered* variant the die is first
    passed through the card's rail filter (τ 1.133 and 1.235 s, `catalogue.json` `rail_filter`), because a rail
    average lags its leakage as it lags its load. That moves the median rails' rise from 1.00 to 0.36 °C, and the
    heating is divided by the catalogue's 0.94 like the rest of the rail.
  - The slopes are each card's within-run drift from the rail ledger (`card_drift_w_per_c`: E38's heating runs,
    aifoundry2 near 81–84 °C, aifoundry3 near 57–60 °C). A variant scales the rails' slopes to the catalogue's median
    die with the idle law's e-folding, holding the off-rail's.
  - Two fits let the heating be free (the board's rise, then both rises) as checks.
  - The conduction regressor, with each configuration's own idle minion rail, is added to measure R_eff from the
    curvature.
- **The row.** Each card's minion coefficient is replaced in the ledger's central-footing row, keeping the published
  SRAM and NoC terms. The two-card mean is carried onto 5.783 pJ by the ledger's own scale, 1.0192. B's conversion
  (W × 0.875/(0.188 × 21)) agrees within 0.001 pJ. Models with a conduction term are evaluated at E38's own idle
  rail, window voltage and rail rows.

## What this does not settle

- **The heating's timescale.** The drift-corrected footings assume the off-rail power follows the window's whole die
  rise at the body window's per-°C slope. About two thirds of that rise comes in the launch's first 1.5 s, before the
  body window starts: arm A's window rise averages 2.25 °C in E120 and 1.53 °C in E77, of which 0.72 and 0.45 °C come
  later. If the off-rail's temperature dependence sits in something slower than the die (the regulators' or the
  board's own heating), less heat belongs in the window. The coefficient then lies nearer the uncorrected 0.22–0.23, a
  row near 1.05 pJ. This caveat moves the row up, not down.
- **Whole-degree die readings.** The body-window regressions run on a rise of about 1.2 °C in whole degrees. The
  two-window estimator, which avoids that, agrees for E120 and runs higher for E77. Both are inside the stated band.
- **The catalogue's rail slopes.** They come from E38's runs: aifoundry2's near 81 °C, about 7 °C hotter than its
  catalogue's 74 °C, which is why the scaled variant is shown. The catalogue's conduction term rests on them
  (result 4).
- **The drift's own uncertainty sets the lower edge.** At two standard errors of E120's off-rail drift the coefficient
  falls to 0.13 W/W, a row of 0.60 pJ. The combined interval's 0.70 pJ is the stated lower edge, not a floor.
- **The intervals are approximate** *(added after verification, F7)*. The in-step coefficients' approx. 95% intervals
  put 1.96 on a pass s.e. from three (E77) or five (E120) passes. With t on the pass part (4.30 and 2.78) they are
  [0.151, 0.235] and [0.128, 0.194], and the combined 0.173 [0.147, 0.199] W/W, a row of 0.81 [0.69, 0.93] pJ. The
  post hoc R_eff intervals are over passes alone and leave the drift's s.e. out. With the board drift's s.e. added in
  quadrature, E120's R in its own form is 0.740, 99% [0.292, 1.188] mΩ (still NEITHER) and in E77's form 0.606
  [−0.004, 1.215] (FAIL); E77's in E120's form [0.254, 1.392] (PASS in that form) and in its own [−0.377, 1.968]
  (FAIL). Moving the board drift by two s.e. either way leaves E120's own-form reading NEITHER (0.63–0.85 mΩ); E77's,
  in E120's form, reads NEITHER at +2 s.e. (`corrections-check.txt` F1, F7).
- **R_eff is taken as one number.** It is a regulator's effective resistance, assumed the same at 52 and 81 °C and
  for every pattern. A MOSFET's on-resistance rises with temperature, so the share at E38's point may be larger.
- **The pattern mix.** E77 and E120 run the row's own pattern, fp32 random FMA. The catalogue mixes 392
  configurations. Its in-step coefficient is higher, and the idle current alone predicts the opposite direction
  (−0.011 and −0.031 W/W, `conduction_transport`), so the gap is pattern or footing, not conduction.

## Corrections after verification (Mon 2 Nov 2026)

An independent verifier read this README, the four files and every record it draws on the same morning. It re-ran
`recut.py` from committed data, and `recut.txt` and `recut.json` came out byte-identical. It checked result 1 in the
catalogue's source and reproduced the registered numbers against the committed fits, among them E77's registered fit in
E77's own form, which `recut.py` had not run. Every number in `recut.json` holds, and so does the core finding: the row
stands (verdict: holds with fixes). It found eight faults, two major and six minor, all in the reading and the wording.
All eight hold against committed files ([`corrections-check.py`](corrections-check.py),
[`corrections-check.txt`](corrections-check.txt)). The corrections were made at the desk; no data file or number in
`recut.json` changed.

| | what was wrong | what changed |
|---|---|---|
| F1 (major) | **E77's post hoc conduction reading was called a PASS "by the registered rules", and the term "resolved in both blocks".** That reading uses E120's registered offset form (a_m, c_B, R). E77 registered another form (a_m, a_s, a_n, R: SRAM and NoC free, no offset), whose verdict is FAIL, provisional. In that form, on E77's own drift, the term is 0.795 mΩ, 99% [−0.296, 1.887], FAIL; and E120's is 0.606 [0.040, 1.171], NEITHER, FAIL at +1 s.e. of its board drift | Result 4 gives each block in both forms, labelled, with E77's registered verdict; "resolved in both blocks" now reads "in E120's offset form; in E77's registered form not for E77, and only marginally for E120"; the conduction-share table says which form each model is in; "probably real" became "probably there", qualified. `corrections-check.txt` F1 first reproduces E77's registered fit (0.622 mΩ, rms 22.6%, FAIL) and E120's registered secondary in E77's form (0.374 mΩ, FAIL) |
| F2 (major) | **The list of texts this re-cut overturns was incomplete.** Besides stop 2, stop 8, the two item 16s and E120's CV1, the premises also stand in the kinds page's section 9, more of the Horace hub's Status tab (its opening, what Q134 did, the short item 16, ranked item 7, Next), three findings files, and E120's Results head, What it changes and corrections table | What it changes lists every place, and what each should say |
| F3 | **The band 0.75–1.05 pJ is the straight-line re-cut's alone.** Left out: the models with a conduction term give 0.82–1.16 pJ at the row's own operating point; the two free-heating catalogue fits give 1.14 and 1.22 pJ; a line through the origin, the published fit's form, gives 0.69 pJ. And the residual's +0.27 pJ was called consistent with zero, where it sits at the edge of the ledger's −0.23 to +0.26 | Result 3's head and table name the band as the straight line's and add the conduction models' 0.82–1.16; a paragraph says why the slope with an intercept is used and why the free fits are checks; the residual is worded "at the edge of" |
| F4 | **"A second estimator agrees."** For E77 the two-window drift, 0.459 (bootstrap 95% 0.386–0.592), excludes the body windows' 0.267 | "It puts both blocks well below 0.81: it agrees for E120 and runs higher for E77" |
| F5 | **The over-correction was put down to the slope's temperature alone.** E38's own off-rail drift near 81 °C, 0.275 ± 0.038 W/°C, matches these blocks' at 52–55 °C. Most of the excess is drift_split handing E38's mostly-rail 0.81 W/°C out by the blocks' own off-rail shares, 0.62 and 0.75 W/°C off the off-rail | Result 2 says so; the blog wording no longer names temperature as the only cause |
| F6 | **The suggested public wording dropped labels.** The re-cut band had no "post hoc", [0.70, 0.93] and the conduction terms in B's conversion no interval kind; and the suggested item 16 dropped "E77's post hoc 0.30 pJ bound did not replicate" | Stop 8's suggested sentence says "post hoc (a desk re-cut, Q136(b))"; the intervals say "approx. 95%" or "99% over R"; the suggested item 16 (handed to the kinds page's integration) keeps the E77 sentence and links this README |
| F7 | **The intervals' approximations were not stated:** 1.96 on a pass s.e. from three or five passes, and R_eff's 99% intervals over passes alone | A caveat under What this does not settle, with t on the pass part and with the drift's s.e. added. No reading in E120's form changes |
| F8 | **"numpy (`/usr/bin/python3` on a stock Mac)".** A stock Mac's python ships no numpy; on the machine that ran this it comes from the user's site-packages | "Needs numpy (`pip3 install --user numpy`)", here and in `recut.py`'s docstring |

## Files

| file | what |
|---|---|
| `recut.py` | the whole re-cut, from committed files only. Needs numpy (`pip3 install --user numpy`; a stock Mac's `/usr/bin/python3` does not ship it): `/usr/bin/python3 docs/reports/data/2026-11-02-q136b-rail-row/recut.py` from the repo's root. About 20 s of CPU *(corrected after verification, F8)* |
| `recut.json` | every number above, per block, footing, arm and pass; per card and footing for the catalogue; the row cases; the conduction tables |
| `recut.txt` | the printed tables, sections A–D3 |
| `corrections-check.py` | *(after verification)* every new number in the corrections: E77's registered form on the re-cut's footings (through `tools/claims-v3/e77/reduce_e77.py`), both forms with the drift moved, the through-origin line, the intercepts, the free-heating fits, the residual, drift_split's split, the t intervals. It imports `recut.py`'s functions and reads `recut.json`; well under a second |
| `corrections-check.txt` | its printout, sections Checks, F1, F3, F5 and F7 |

## Device commands sent

None. This lane opened no device node, took no card lock and ran nothing on any lab host. Q136's write-command audit
(section 17 of the workflow brief) has nothing to list for it. The corrections ran local Python on committed files only.
