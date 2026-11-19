# Declared before any datum: MM1-v3's frozen forecasts of E212 aifoundry2 card 0 S3 (the re-run of Wed 18 Nov 2026), to be scored blind

Lane blind-v3-e212s3, round Q223, written on the lab box aifoundry2 on Wed 18 Nov 2026 between about 14:00 and 14:15 PST. The re-run of
E212's session a2c0-S3 was due to take the card from about 16:00 PST. When this was written, none of its data existed. At 14:08 PST there
was no claim for the session, no quiet-desk flag on the box, and no session folder for the re-run. S3's first try (Tue 17 Nov 15:44 PST),
cut short by the box's reboot, left no completed run. This file's sha256 goes into the lane's log, with the time, before the data are read.
Desk work only: nothing here is measured.

Labels: *frozen* means in a pushed commit; *blind* means scored on data that did not exist when the model was frozen; *REPORTED* means a
figure with no pass rule. A check that was not run is NOT RUN.

## 1. The forecasts and the predictor, frozen in b1493082

MM1-v3 landed as `b149308280a73396516937304037af57a5563c16`: committed 20:52:46 PST and pushed 20:52:51 PST on Tue 17 Nov 2026 (the land
lane's log; GitHub main read b1493082 at 20:52:52). It is an ancestor of main `fcbf60c4`, and no later commit touches
`tools/matmul/mm1/v3`, `tools/matmul/mm1/v2` or `tools/claims-v3/e212`. All files below were checked in a `git archive` of b1493082
(14:02:27 PST): MM1-v3's `SHA256SUMS` (`c24efc14...`) passes 170 of 170, and MM1-v2's (`eafb6558...`) passes 114 of 114.

| file (under tools/matmul/mm1/) | sha256 | role |
|---|---|---|
| `v3/out/mm1_v3_e212_s3s4.csv` | `002226651404b291739894cc187d528e68b741d4e4df8b8d53d37172f4933faf` | **the forecast file**: 46 a2c0-S3 rows (and 56 for S4), MM1-v3 and MM1-v2 columns, 799 MHz given; the same sha256 as README section 6 and `SHA256SUMS` |
| `v3/out/mm1_v3_params.json` | `1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db` | MM1-v3's frozen constants |
| `v3/mm1_v3.py` | `89c2e463e3527b379ed10557c2e595b294b289c0ba8cd2005481190c9555fe3c` | the predictor |
| `v3/engine_v3.py`, `v3/energy_v3.py`, `v3/mm1_core_v3.py`, `v3/kinds_v3.py` | `da621346...`, `49a577bc...`, `acebc705...`, `d87de33c...` | its code (full sha256 in `SHA256SUMS`) |
| `v3/inputs/census/census-v3.json` | `cad5250ccc2324c724fe2230093146aa6216779cf0c64003228b88fbd59d974f` | the operations census |
| `v3/data_v3.py` | `a5eb123bf1ba16fca51bf9474904a73919cacbf870e0f37bb5f78126236862be` | MM1-v3's loader (`mms_runs`, `e212_kind`, `cases`) |
| `v3/unread_v2_e212.py` | `916954ccaf477c3e4c858d1a6f68c2cb5d224339792e33bab4fa81908c7f2028` | MM1-v2's caller and its four pins (v2 at 3ca4b717) |
| `v3/out/holdout_v3.json`, `v3/fit_v3.py` | `c03309be...`, `6aff2317...` | v2form's all-data constants and form (shown beside only) |
| `v3/postcheck_v3.py` | `3fa0d07293d0ef1dd3f583703a5cdfb4011bbf5dadba1e10a84464c215c53172` | the configuration-twin rule (`cfg_t`, `cfg_e`, `rung_of`) |
| `v3/inputs/e212/sched__a2c0-S3.json` | `ea72bc7b908bc5ce8568ff01eca23371f88e13b0512ebbc3d370ef1a33937c95` | MM1-v3's copy of S3's registered schedule |

The registered schedule is `tools/claims-v3/e212/proposal/src/sched/a2c0-S3.json`, with the same sha256, `ea72bc7b...`. It belongs to
E212's registration, `c83a29d1`, whose `SHA256SUMS-e212-registration` (`a24285d9...`) passes 87 of 87 at main `fcbf60c4`. The model
session's #11.13 names the same schedule as `ea72bc7b908bc5ce`, unchanged for the re-run.

## 2. The arms against the registered schedule

- **The schedule:** 55 runs. 45 are arm runs (45 arms), 6 are anchor runs (one arm, `4x8x8-int8-rnd`) and 4 are nulls.
- **Non-null arms and forecasts match one for one.** The 46 non-null arms equal the forecast file's 46 a2c0-S3 rows. No arm lacks a
  forecast, and no forecast lacks an arm. Each row's key (arm, format, data kind, shire mask) equals the key MM1-v3's loader forms from the
  arm label.
- **Nulls** have no forecast and are not scored.
- **Energy** is forecast for 37 arms: random 10, zeros 20, ones 7. The other 9 arms are switch patterns, forecast for time only: lanes2 3,
  fld_sign 3, den8, den4, fld16_sign. MM1-v3 prices energy for random, zeros and ones only.
- **Cases:** a case is (card, arm, format, kind, mask), the mean of its runs, so at most 46 cases. The anchor's 6 runs make one case.
- **Desk record:** `s3-arms-twins.json` (`b8919725...`) lists every arm with its key, its frozen row and its twin flags.

## 3. The quantities, and how each model is called (MM1-v3's README section 5 form, as for E212 a2c0-S4)

- **Data:** MM1-v3's loader, `data_v3.mms_runs`, run with `data_v3.e212_kind` on the committed data file. It keeps one record a run, leaves
  nulls out and uses the primary view (`win`). A run counts only when it ran and has the view's T_op, cyc_op_max and at least one launch.
  No run is removed by hand. Runs the loader leaves out are listed.
- **How each model is called:** at the run's measured kernel clock, with the view's measured minion volts and the run's die at start.
  MM1-v3 goes through its predictor, `mm1_v3.Model`. On every case the score also checks that the predictor equals MM1-v3's fit code
  (`engine_v3`, `energy_v3`). MM1-v2 goes through `unread_v2_e212.call`.
- **The quantities:**
  - wall cycles an op (the slowest minion);
  - **the counter mean** (cycles an op, the average minion);
  - **W over idle given the measured seconds** (A + B / t_meas), scored at 3 W and above; below 3 W it is scored in watts;
  - **J over idle with t forecast**, at 3 W and above;
  - **J at rest**, given t and with t forecast, wherever MM1-v3 forecasts energy.
- **Each quantity is scored per run and per case.** Section 5 reports J at rest per run; this score adds it per case.

## 4. The metric

- **Error** is forecast / measured - 1.
- **Each quantity** gets its **rms in %** and its **signed mean (bias) in %**. W below 3 W gets rms and bias in watts.
- **The per-case table** has every case, with its twin flag and the error of each model.
- **Head to head, per case:** how often MM1-v3 is closer than MM1-v2, and the reverse. A tie is within 0.5% in cycles or 1% in W.
- **Configuration twins, split** by MM1-v3's own rule (`postcheck_v3`): a case is a twin when its configuration is in MM1-v3's all-data fit
  set. For time the configuration is card, kernel, arm, format, shire mask and clock to 25 MHz, ignoring the data kind; for energy the kind
  is added.
  - At 800 MHz, 29 of the 46 cases are time twins (10 of the 25 kind-blind configurations, as README section 6 says), and 16 of the 37
    energy cases are energy twins.
  - The scorer decides each flag again at the case's measured clock.
  - The split is reported for wall cycles (time configuration), W given t (time configuration) and W given t (energy configuration).

## 5. The comparisons

- **MM1-v2 as frozen**, on the same runs and cases, with the same calls MM1-v3's README section 5 uses.
- **v2form** (MM1-v2's form refitted on all of MM1-v3's data), shown beside, as in section 5.
- **Beside, the literal frozen numbers** of `mm1_v3_e212_s3s4.csv` at 799 MHz given, for MM1-v3 and MM1-v2. They are scored against the
  same cases for wall cycles, the counter mean and W given t (the CSV's A + B / t_meas). They show what freezing at 799 MHz gives, next to
  the section 5 form.

## 6. What is reported

No pass rule is registered for S3, so **every figure is REPORTED**. The score is labelled **BLIND** when both of these hold:

- (a) b1493082's push (20:52:51 PST Tue 17 Nov) is earlier than the re-run's first card command;
- (b) this declaration's sha256 is in the lane's log before that command.

The first card command is read from the committed session log. It is the earliest line at or after the session start that touches the card
(the configuration read). The session-start line (T0) is the conservative bound. If (b) fails, the figures are REPORTED and not blind, and
the result says so. MM1-v3's README calls S3 a weak blind test of time, because 10 of its 25 configurations are in the fit data at 800 MHz.
That is why the twins split is reported beside the pooled figures.

## 7. The data, and when they are read

- **The file:** only after data-e212s3's data commit is on GitHub main:
  `docs/reports/data/2026-11-18-e212-mmsweep2-a2c0-S3/data-e212-a2c0-S3.json`, the reduced file in the form of E212's nine committed data
  folders. Its sha256 and the commit are logged before scoring. If the folder or file name differs, the folder's single `data-e212-*S3*.json`
  is read and the difference recorded.
- **Order check:** before the score, the lane checks that no datum of the re-run is older than b1493082. It reads the session log's T0 and
  first card command, the data folder's meta, and the commit time.
- **The data lane's verdicts** (schedule equality, the -j1 rebuild departure, the power and load guards) are recorded beside the score and
  change nothing in it.
- **Gaps:** an arm with no scored run is listed as NOT RUN. If any arm is missing, the result is SCORED WITH GAPS. With no data commit by
  14:00 PST Thu 19 Nov, the result is NOT SCORED.

## 8. The scorer

- **The script:** `s03_score.py`, sha256 `45803a24eb73e20816467aaa672bb742909f14d1d6f5e18ec294f95b638112c6`. It runs as
  `/usr/bin/python3 -I -B` (Python 3.12.3, numpy 1.26.4, scipy 1.11.4), single-threaded inside the round's CPU slots, on the archive of
  b1493082.
- **Pins:** before anything is read, it checks the 15 pinned files above, all 170 lines of MM1-v3's `SHA256SUMS`, and MM1-v2's pins and
  `SHA256SUMS`.
- **The desk test on E212 a2c0-S4**, using MM1-v3's own vendored copy of the committed S4 data (`2e2ed24e...`), reproduces README section 5
  exactly:
  - wall cycles 4.75% (+0.61) against MM1-v2's 5.80% (-2.12);
  - counter mean 5.90% against 6.32%;
  - W given t 3.07% (-1.46) against 5.14% (+0.54);
  - J over idle with t forecast 4.06% against 5.68%;
  - per run, 4.52 / 2.96 / 1.13 / 3.91% against 5.57 / 5.09 / 2.06 / 4.77%;
  - head to head, 26 / 21 / 9 and 28 / 19 / 7;
  - twins, 38 and 18 cases (4.41% and 5.40%), and W 32 and 22 (3.24% and 2.81%). README's 4.42 and 3.25 are `postcheck_twins.json`'s
    4.415 and 3.245 rounded a second time; unrounded they are 4.4149 and 3.2447.
  - The predictor equals the fit code (time 0.0; W 7.1e-15 W).

## 9. No sealed number

The model session's sealed forecasts of S3 are E212's freeze lines. They include the v3.3 seal `6842eca5...`, which `fcbf60c4` registers.
They are known by sha256 only, and none is read or used here. This lane scores the lab's MM1-v3 against the lab's MM1-v2.
