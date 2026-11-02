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
   (E120) W/°C, one s.e., so 0.81 is 3.0× and 2.3× theirs, 5.5 and 3.8 s.e. above. A second estimator agrees, free of
   the regression on whole-degree die readings: the board over [t1−1, t1] less over [t0+1, t0+2] across arm A's launches.
   It gives 0.459 (bootstrap 95% 0.386–0.592) for E77 and 0.298 (0.257–0.339) for E120, and E120's 8 s rung gives 0.345
   (`recut.txt` B2). Attributed with each block's own drift, the window's heating is **33% (E77) and 43% (E120)** of the
   gap between the uncorrected and central footings' in-step slopes (21–45% and 29–58% at one s.e.). The rest of the
   gap, 0.08 W per minion W in both blocks, is the registered slope's excess over the block's own drift.

3. **Re-cut on drift-corrected footings, the row is 0.75–1.05 pJ, so the published 0.875 pJ stands.** The in-step
   coefficient is the off-rail watts that grow with the minion rail, per minion watt, at 600 MHz (arm A, the row's own
   clock and voltage). The row is the ledger's own arithmetic (`rail_ledger.py` `apply_footing`, the central footing,
   carried onto Q128's 5.783 pJ board) with the coefficient replaced:

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

   The two blocks differ by 0.032 ± 0.025 W/W, within their errors. The catalogue refit on that footing also fits its
   392 configurations best: rms 0.295 and 0.287 W, against the published 0.332 and 0.308 (`recut.txt` C). The ledger's
   off-rail on E38 is 1.017 pJ, so the fit's residual moves from 0.142 pJ to between −0.03 and +0.27 pJ, still
   consistent with zero as the ledger read it. **E120's CV1 reading, "the row itself is in question", does not
   survive.** (`recut.json` `instep_coefficient`, `row.cases`, `measured_split_uncertainty`)

4. **The regulators' conduction share is not settled; post hoc, a third to two thirds of the row.** E120's registered
   verdict stands: FAIL, not resolved, R_eff 0.55 mΩ, 99% [−0.06, +1.16], at most 0.69 pJ of the row. On each run's
   own drift (post hoc, the registered offset form), the term is resolved in both blocks, and the catalogue's curvature,
   at its single voltage, finds it too:

   | data, drift-corrected footing | R_eff, mΩ | by the registered rules |
   |---|---|---|
   | E120 | 0.740, 99% [0.313, 1.167] | NEITHER, resolved but not material (rms better by 6.0%) |
   | E77 | 0.823, 99% [0.394, 1.252] | PASS (rms better by 40.8%); E77's own verdict is provisional |
   | the catalogue, aifoundry2 / aifoundry3 | 0.637 ± 0.109 / 0.416 ± 0.113 (1 s.e.; 0.521 / 0.401 with the rails' slopes scaled) | — |
   | the catalogue on the published footing | 0.033 ± 0.120 / 0.167 ± 0.120 | — |

   On the published footing the catalogue sees no conduction term, which is why the ledger's square-term test found
   none. The term appears once each rail is corrected for its own heating. With its rails left raw (measured_board_only)
   it reads only 0.145 and 0.189 mΩ, so the catalogue's value rests on the ledger's rail slopes.

   **As a share of the row, at the row's own operating point.** That point is E38's idle minion rail, 13.54 W
   (aifoundry2) and 7.97 W (aifoundry3), and its step of about 21.5 W, where I²R weighs more than at E120's 6.75 W idle.

   | model | row, pJ | conduction, pJ |
   |---|---|---|
   | E120 | 0.82 | **0.57 (69%)**; 0.24–0.89 over R's 99% interval (33–98%) |
   | E77 | 0.98 | **0.63 (64%)**; 0.30–0.96 (33–90%) |
   | the catalogue | 1.14–1.16 | **0.36–0.41 (32–36%)** |

   At E120's own point, in B's conversion, the conduction term is 0.44 [0.19, 0.70] pJ (E120) and 0.49 [0.24, 0.75] pJ
   (E77). Read beside the registered B, 0.33 [−0.04, 0.69]. So **the regulators' conduction is probably real, at about
   0.4–0.8 mΩ, and is a third to two thirds of the row.** The rest of the row is not split between the regulators'
   current-proportional losses (switching) and off-rail logic in step: E120's design tests only the I² term
   (`recut.json` `conduction`, `at_the_rows_operating_point`, `catalogue.<card>.conduction_from_curvature`).

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
  > in step); re-cut on drift-corrected footings it is 0.75–1.05 pJ (Q136(b)), so it stands. How much of it is the
  > regulators' conduction is not settled: E120's registered test did not resolve it (at most 0.69 pJ, 99%), and post
  > hoc, on each run's own drift, E77, E120 and the catalogue each show a conduction term of 0.4–0.8 mΩ, a third to two
  > thirds of the row**

- **Stop 2's Missing column, the Status list's item 16 and the kinds page's item 16** carry two premises this re-cut
  overturns: "one coefficient fitted on uncorrected deltas", and "its drift-corrected footing measures only about
  0.4 pJ … so the row itself is in question". The coefficient was fitted on board deltas corrected with the idle law's
  slope (result 1). The 0.4 pJ is E38's 0.81 W/°C applied to runs whose own board drift is 0.27–0.35 W/°C (result 2).
  The row re-cut is 0.75–1.05 pJ (result 3). Item 16 stays open, now for registering the conduction term and for the
  split of the rest of the row.
- **E120's README:** a dated note under CV1 (its frozen text unedited). It should say three things. The coefficient was
  fitted on corrected board deltas. The "0.08–0.10 W per minion W" uses the registered 0.81 W/°C, 2.3× the block's own
  board drift. On the block's own drift the in-step slope is 0.161 (arm A) and 0.168 (arm B) W per minion W.
- **For a re-run of E120 (the critic's item 7, work (b), which needs a governor move and his OK):** it would measure
  against an in-step coefficient of 0.175 [0.151, 0.199] W per minion W and R_eff 0.74–0.82 mΩ on the measured-drift
  footing. Register as the central footing the block's own drift (body windows, with the two-window estimator as its
  check), not 0.81 W/°C. A rung launched at two die temperatures would measure the off-rail's temperature coefficient
  at a fixed load directly.
- **For the blog material:** of the step between the board and the core rail, most is power off every meter that grows
  with the work. It stands at about 0.75–1.05 pJ of a 5.8 pJ random fp32 multiply-add. Probably a third to two thirds of
  it is the regulators' I²R loss, which grows with the square of the current, so a lower rail voltage at the same power
  costs more there.

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
- **R_eff is taken as one number.** It is a regulator's effective resistance, assumed the same at 52 and 81 °C and
  for every pattern. A MOSFET's on-resistance rises with temperature, so the share at E38's point may be larger.
- **The pattern mix.** E77 and E120 run the row's own pattern, fp32 random FMA. The catalogue mixes 392
  configurations. Its in-step coefficient is higher, and the idle current alone predicts the opposite direction
  (−0.011 and −0.031 W/W, `conduction_transport`), so the gap is pattern or footing, not conduction.

## Files

| file | what |
|---|---|
| `recut.py` | the whole re-cut, from committed files only; numpy (`/usr/bin/python3` on a stock Mac): `/usr/bin/python3 docs/reports/data/2026-11-02-q136b-rail-row/recut.py` from the repo's root. About 20 s of CPU |
| `recut.json` | every number above, per block, footing, arm and pass; per card and footing for the catalogue; the row cases; the conduction tables |
| `recut.txt` | the printed tables, sections A–D3 |

## Device commands sent

None. This lane opened no device node, took no card lock and ran nothing on any lab host. Q136's write-command audit
(section 17 of the workflow brief) has nothing to list for it.
