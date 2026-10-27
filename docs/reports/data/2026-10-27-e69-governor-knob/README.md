# E69 data: the governor knob test (Q129, Tue 27 Oct 2026, aifoundry2 card 0)

**The first time this card's governor has been moved.** E64 (23 Oct) read the governor's own log through 43
runs and concluded that the board's power against the 65 W TDP level sets the Horace matmul's speed on a cool
die, and the 65 °C software threshold does on a hot one — but it never moved either limit, so every word of
that was a correlation. Q128 § 5 lists it as the first open item. E69 lowers the TDP level to 55, 45 and 35 W
and moves the software thermal threshold to 70 and 62 °C, re-runs E64's own operand patterns, and scores the
result against predictions frozen and pushed before the first launch.

Authorised by the owner on 27 Oct 2026, carried out under Roman's ET-SoC-1 firmware field manual. Every gate
is in [`CHANGE-RECORD.md`](../../../../tools/claims-v3/knob/CHANGE-RECORD.md); the pre-registration, the cells
and the frozen predictions are in [`tools/claims-v3/knob/`](../../../../tools/claims-v3/knob/README.md)
(pushed as `2d35d1b9` **before the first governor write and before the first launch**; the read-only identity
reads ran 13:55–13:58 PDT, about 22 minutes earlier — corrected in amendment A5. Amendments A1 and A2
`4e0522f1`, A3 `8fbc3c7f`, A4 `4f3da00b`, A5 the desk fix pass of 27 Oct 15:30 PDT).

## Results first

**The cap is the cause, not a correlate.** The governor's own log, which before today only ever printed
`tdp level: 65000`, now prints the level this experiment set and dithers around it — at a 45 W cap it logs
`Power throttle down event, current pwr 45780 tdp level: 45000` then `… up event, current pwr 43470 …`,
alternating on successive passes. Twelve cells, 24 runs:

| TDP | pattern | predicted MHz | measured MHz (2 runs) | band | in band | power-down steps | thermal steps |
|---:|---|---:|---|---|---|---:|---:|
| 65 (control) | zeros | 800.0 | 800, 800 | 775–800 | 2/2 | 0, 0 | 0, 0 |
| 65 (control) | ones | 800.0 | **756**, 800 | 775–800 | 1/2 | **0, 0** | 0, 0 |
| 65 (control) | a_ones_b_randn | 742.9 | 760, 768.6 | 718–768 | 1/2 | 9, 8 | 0, 0 |
| 65 (control) | randn | 704.8 | 712, 706 | 680–730 | 2/2 | 11, 10 | 0, 0 |
| 55 | zeros | 800.0 | 800, 800 | 775–800 | 2/2 | 0, 0 | 0, 0 |
| 55 | ones | 800.0 | 800, 800 | 775–800 | 2/2 | 0, 0 | 0, 0 |
| 55 | a_ones_b_randn | 681.0 | 705.9, 691.7 | 656–706 | 2/2 | 10, 10 | 0, 0 |
| 55 | randn | 633.3 | 646, 631.4 | 608–658 | 2/2 | 11, 11 | 0, 0 |
| 45 | zeros | 800.0 | 800, 800 | 775–800 | 2/2 | 0, 0 | 0, 0 |
| 45 | **ones** | **733.3** | **758, 739.6** | 708–758 | 2/2 | **10, 9** | 0, 0 |
| 45 | a_ones_b_randn | 600.0 | 608.3, 600 | 600–625 | 2/2 | 4, 2 | 0, 0 |
| 35 | zeros | 795.2 | 800, 800 | 770–800 | 2/2 | 0, 0 | 0, 0 |

- **A pattern that had never been limited became limited, at the predicted speed.** `ones` draws 51 W at
  800 MHz, so at the card's own 65 W cap it has never thrown a single power step — 0 in E64's two runs and 0
  in both of today's. Lower the cap to 45 W and it steps 10 and 9 times and settles at 758 and 739.6 MHz,
  against 733.3 predicted. That is the controlled result the top rung of the chain was missing.
- **The gap moves with the cap, monotonically, for every pattern that throttles.** `a_ones_b_randn`
  764.3 → 698.8 → 604.1 MHz at 65 → 55 → 45 W (predicted 742.9 → 681.0 → 600.0); `randn` 709 → 638.7 at
  65 → 55 W (predicted 704.8 → 633.3).
- **The extrapolated cap table holds.** Scored as registered — on the 12 cells, each the mean of its two
  runs — **all 12 landed inside their bands** (the bar was 10) and the signed error over the 12 cell means has
  rms **11.50 MHz** (the bar was ≤ 25). Per run, as a secondary statistic: 22 of 24 in band, rms 13.9 MHz. The
  bands were ±25 MHz, 7.5× E64's own 3.3 MHz model residual. The table was extrapolated from 65 W measurements
  alone; it predicted 45 W and 55 W behaviour it had never seen. *(The first write-up scored this rule on the
  24 runs, which applied the 10-of-12 bar to 24 — the permissive direction. Corrected in A5; the verdict is
  PASS under either scoring.)*
- **`zeros` at a 35 W cap did not give up its speed.** Predicted 795.2 MHz, measured 800 and 800, 0 power
  steps. Its peak board power in those runs was 32.8 and 34.6 W, under the cap, so the governor had nothing to
  act on: the prediction's 795 came from the model expecting a brief excursion above 35 W that the card did
  not make. The cell is in band (the band's floor is 770), but the *mechanism* it was built to test —
  throttling a pattern that nothing else can throttle — did not trigger, so it does not add evidence either
  way. A cap near 30 W would, and is not in this authorization.

**The sustained clamp is thermal, and raising the threshold closes the gap completely.** Four sustained cells
were measured, all `ones`, all 9 × 8 s back to back, the mean over the last 40 s:

| TDP | threshold | predicted MHz | measured MHz | die °C | board W | thermal steps | power steps | share at 800 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 65 | 65 (control) | 736.5 | 763.4 | **65.2** | 51.9 | **11** | 0 | 0.66 |
| 65 | **70** | 800.0 | **800.0** | 64.2 | 54.7 | **0** | 0 | **1.00** |
| 65 | **62** | 649.8 | 790.3 | 61.2 | 52.1 | 8 | 0 | 0.93 |
| **50** | 65 | 700.0 | 769.6 | 61.2 | 50.0 | **0** | **11** | 0.70 |

- **Raising the threshold closes the sustained gap, exactly as predicted.** At the card's own 65 °C the die is
  pinned **at 65 °C in every one of the last twenty 2 s bins** while the clock dithers 740–800 MHz: a textbook
  clamp, 11 thermal throttle-down events, 763.4 MHz. Raise the threshold five degrees and the same work holds
  **800 MHz in every bin for the whole 76 s with zero thermal steps**, the die settling at 63–66 °C under the
  new threshold. Q128 called the sustained gap "a clamp, right in order but with no number to test"; the number
  is **36.6 MHz of sustained clock, and it belongs to the threshold** — 800.0 − 763.4, between two cells that
  ran 20 s apart in the same session (14:28:51 and 14:30:27), so the session-to-session offset below is
  common-mode. Three caveats, none of them optional: each cell is **n = 1 with no interval**, neither was
  replicated; the raised-threshold cell sits **at the 800 MHz ceiling**, so 36.6 MHz is a **lower bound** on
  the threshold's effect at this work point; and this is a **measured 65 → 70 °C sensitivity**, not the Levels
  tab's "775 predicted vs 738 measured" model gap, which is a different quantity that E69 does not close (see
  "The control cells did not reproduce E64" below).
- **Lowering the cap switches the cause without changing the speed.** At a 50 W cap the same pattern runs
  769.6 MHz with **0 thermal steps and 11 power steps**, against the control's 11 thermal and 0 power. Same
  card, same work, nearly the same clock — and the governor's own log says the limiter changed from heat to
  power. The *speed* prediction for that cell (700 MHz) is **refuted by 70 MHz**, and why is a real model
  error: the sustained ladder put `ones`' 800 MHz power near 56 W, so the 50 W cap was expected to bite down
  at 700 MHz; the card actually drew 50.0 W at 770 MHz, so the cap bit much higher up the curve.
- **Lowering the threshold to 62 °C is inconclusive, and the bins say why.** Predicted 649.8, measured 790.3 —
  a 140 MHz miss, and not a fair test. That run gated at a 50 °C die (the control gated at 57 °C), and its
  last-40 s bins show the die still **climbing, 59 → 62 °C**, with the clock at 800 MHz for the first fourteen
  bins and only breaking up (775, 695, 800, 780, 765, 750) in the last ten seconds as the die finally reached
  62. The run never came to equilibrium against its own threshold inside 76 s, so its mean is dominated by the
  pre-clamp period. The registered prediction assumed equilibrium. **Reported as inconclusive, not as a
  result**: the cell needs a longer run or a hot start, which is not in this authorization.
- **Both sustained `randn` cells are unmeasured.** See "The cells that aborted".

### The control cells did not reproduce E64 — the registered drift check FAILS

The pre-registration gave the two control cells exactly one job: *"they do reproduce E64 to 1.4 MHz, which is a
check that the card has not drifted"*. They do not.

| | E64, 23 Oct | E69, 27 Oct | difference |
|---|---:|---:|---:|
| sustained `ones`, TDP 65 / thr 65 (`SUS-01-fp32-ones` → `S-tdp65-thr65-fp32-ones`) | 737.9 MHz | **763.4 MHz** | **+25.5** |
| its board power over the same window | 49.38 W | **51.89 W** | **+2.51 W** |
| its die over the same window | 65.4 °C | 65.2 °C | −0.2 |
| its share of the window at 800 MHz | 0.478 | 0.660 | +0.18 |
| thermal / power throttle-down events | 10 / 0 | 11 / 0 | — |
| burst `a_ones_b_randn` at 65 W (2 runs) | 740.4, 742.3 | 760, **768.6** | +20 to +26 |

Both runs started from the same die (`die_start` 58 °C in each), so the ordering inside the session does not
explain it — and the control ran *after* the 70 °C cell, which if anything pushes its mean down. The direction
is the same in the burst control, and `B-tdp65-fp32-a_ones_b_randn-r2` at 768.6 MHz is one of the two
out-of-band runs. The physical reading is a **thermal-path change, not a governor change**: the die sits at the
same pinned temperature while the card carries 2.5 W more, which is about 1.4 °C less rise than E64's thermal
line (die = 41.88 + 0.4696 °C/W) gives for that power, i.e. roughly 3 W more dissipation at the same die
temperature. E69 did not measure ambient or airflow and cannot say more.

**What follows.** The drift check is reported as **FAILED** (25.5 MHz against the 1.4 MHz it was registered
to show), not as a 26.9 MHz prediction error — which is how the first write-up recorded it. Any E69-vs-E64
comparison carries at least this offset; the within-session comparisons (the 36.6 MHz above, the cause flip at
50 W) do not. No sustained cell in E69 was replicated: every sustained number here is **n = 1**.

## What was registered and what happened

| Rule | Verdict | Why |
|---|---|---|
| **K1** the mean clock is non-decreasing in the cap | **FAIL as registered** | it holds for `a_ones_b_randn` and `randn`; it fails for `ones`, whose 65 W pair averages 778 MHz against 800 at 55 W, entirely because of one run (below) |
| **K2** `ones` at 45 W throttles where at 65 W it did not | **FAIL as registered** | the causal half holds exactly — 0 power-down steps at 65 W in both runs, 10 and 9 at 45 W, and 758/739.6 MHz against 800 — but the rule also required both 65 W runs to read ≥ 775 MHz and one read 756 |
| **K3** the extrapolated cap table | **PASS** | as registered: **12 of 12 cells** in band (needed 10), rms of the 12 signed cell errors **11.50 MHz** (needed ≤ 25). Per run: 22 of 24, rms 13.9 |
| **K4** the sustained clamp is thermal | **PASS**, on the step counts | `ones` at threshold 70 °C held **800 MHz in every one of the last twenty bins** (800-share 1.00) with **0 thermal steps** against the control's **11**, at a die of 64.2 °C under the raised threshold. The rule's own test (≥ 775 MHz) is met — but 800 MHz is the top VMIN point, so "predicted 800.0, measured 800.0, error 0.0" is a **ceiling artefact** and carries no calibration information; the step counts and the 800-share are the content |
| **K5** the sustained cause can be switched | **FAIL as registered**, attribution confirmed | half A (`randn` at threshold 70) **aborted, unmeasured**; half B's attribution is exactly right — `ones` at a 50 W cap shows 0 thermal and 11 power steps against the control's 11 and 0 — but its clock read 769.6 MHz, outside the registered 675–725 band |
| **K6** restore | **PASS** | all five sessions read back TDP 65 W and threshold 65 °C, equal to the originals — and an independent agent's own card read at 14:58:09 PDT found the same |

### The one run that failed two rules, and what it actually was

`BURST-01-tdp65-ones-r1` read 756 MHz where its pair read 800. It was **not throttled**: the governor logged
**zero** power-down and zero thermal-down events for it, and its board power never passed 51.6 W against a
65 W cap at a die of 58 °C. The service-processor ring shows what happened — at 1.5 s into the work it printed
`New OP: Freq 600 MNN 520 SRM 705` with `throttle_state 0, power_state 1` and **no throttle-down line above
it**, then climbed 600 → 700 → 800 over the next second on two `Power throttle up` events. That is the
governor's **idle reset**: the heater runs a stream of short kernels, the master minion reports idle between
two of them, the service processor drops the clock to the boot point, and the power branch climbs back.
`docs/findings/14-card-behaviour.md` already describes the shape.

So `mhz_steady` — the mean clock from 1.5 s to the end of a 6 s run — is contaminated by a third mechanism
that is neither of the two limits, and it bit one run in 24. K1 and K2 are reported as **failed**, because
that is what the registered rules say about this data. What the rules were built to detect is nonetheless
unambiguous in the same runs, from the governor's own event counts, which no idle reset can fake:

| pattern | cap | runs | power-down events | mean MHz |
|---|---:|---:|---|---:|
| ones | 65 W | 2 | **0, 0** | 756, 800 |
| ones | 45 W | 2 | **10, 9** | 758, 739.6 |

A tighter rule for the next experiment of this kind: score the burst cells on the governor's event counts and
on a mean clock computed over the samples outside idle-reset episodes, and register that episode definition in
advance. Scoring it that way *now* would be post-hoc, so it is written here as a lesson and not as a verdict.

### The cells that aborted, and the correction that followed

Two runs ended their session on the registered board-power rule, both of them sustained `randn`:

| Session | Run | Reason | Governor at the time |
|---|---|---|---|
| `s1` | `SUS-03-tdp65-thr70-fp32-randn-r1` | board **85.2 W** > 85 W on 3 samples | TDP 65 W, threshold **70 °C** |
| `s2` | `SUS-00-tdp65-thr65-fp32-randn-r1` | board **85.8 W** > 85 W on 3 samples | TDP 65 W, threshold 65 °C — **the card's own defaults, nothing moved** |

The first abort was written up (amendment A3) as evidence that lifting the heat clamp let `randn`'s peak power
overshoot. **The second abort refutes that, and the write-up is corrected** (amendment A4): the *control*
cell, with the governor untouched, does the same thing. Sustained `randn` on this card reaches 85 W of
instantaneous board power at its own default settings, and E69's 85 W bound — chosen below E64's 97 W —
therefore stops every sustained `randn` cell, moved or not. E64 ran the same cell on 23 Oct under its wider
bound and it completed at 600 MHz.

So: **neither sustained `randn` cell is measured, and E69 concludes nothing about the threshold's effect on
`randn`.** The instantaneous overshoot above the 65 W cap is real, is visible in both, and is consistent with
an average-based power trigger and no hardware fast throttle — but it is a property of the pattern, not of the
knob, and E69 did not test it. The bound was **not raised** to get the cells (field manual rule 11: a failed
gate is not bypassed), and `randn` was not retried.

Both restores ran in their session's `finally` and read back 65 W / 65 °C. After the first abort the card was
checked over: firmware identities unchanged, **module uptime 23 h 19 m so no service-processor reset**, idle
die mean 54 °C at 24 W and 600 MHz, no AER, no link error, no new kind of error event.

## The governor moves, as logged

| | |
|---|---|
| Originals, read under the card lock **before any set**, in every session | TDP **65 W**, software threshold **65 °C**, power state `low_power`, 600 MHz. The reads that precede the *first* set of all (smoke2, 14:23:30.707) are `smoke` 14:20:45.103 and `smoke2` 14:23:23.649; the registered session's own read is `s1` 14:24:04.235 |
| Distinct settings used | **seven**: (35, 65), (45, 65), (50, 65), (55, 65), (65, 62), (65, 65), (65, 70) W/°C |
| Set commands sent | **39 DM writes across all five sessions** — `smoke` 2, `smoke2` 3, `s1` 26, `s2` 4, `s3` 4, each count including that session's two restore commands. `s1`'s 26 are 24 from its 23 command-sending set events (one event moved both fields) plus the restore's 2; it had 27 set events in all, 4 of which were already at the target and sent nothing. **Every one of the 39 rc 0** |
| Read-back mismatches | **0** — every set was followed by `ettelem config` and compared, and the runner aborts the session on a mismatch or on drift from the run's own target at its end query |
| Restore | in **all five** sessions' `finally`, read back and equal to the originals (**TDP 65 W, threshold 65 °C, `ok: true`**): `smoke` 14:20:46.553, `smoke2` 14:23:37.509, `s1` 14:32:11.929, `s2` 14:35:06.826, `s3` 14:38:43.792 PDT |
| Firmware after | release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0, minions 0.25.1 — unchanged |
| Return check (`s3`, `BACK-00-back-randn-r1`) | at the restored defaults, one 6 s `randn` burst: the card stepped normally (706.3 MHz mean, 10 power-down and 12 power-up events, die 58 → 65 °C) and the governor's log printed `tdp level: 65000` again. `s3` exited **0 (done)**. Its board power **peaked at 86.61 W** with **12 samples ≥ 85 W** and a longest consecutive breach of 2, so the registered 3-sample abort did not fire — the highest board sample of all 29 reduced runs, on `randn` at the card's own settings, and the same property A4 records. The first write-up printed 84.4 W here, which was that run's `p800_w`, not a peak |
| Check after the **first abort** (≈14:32, before `s2` and `s3`) | `ettelem config` → TDP 65 W, threshold 65 °C; module uptime **23 h 19 m** |
| Independent check after the **last** run (14:42) | `ettelem config` → `{"tdp_w": 65, "temp_threshold_c": 65, "power_state_name": "low_power", "minion_mhz": 600}`; module uptime **23 h 29 m**, so the service processor never reset and the restore is a real write, not a reboot's default. An independent agent repeated the read at **14:58:09** and got the same four values |

Full log with per-command argv, rc and millisecond timestamps: `gov.jsonl` in each of the five session
directories (`smoke`, `smoke2`, `s1`, `s2`, `s3`).

## Three corrections to the record

- **This card's firmware build.** `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`, read fresh at 13:56:26 PDT, reports
  release **1.4.0**, BL1 and BL2 **0.22.0**, PMIC 1.5.0, minions **0.25.1**.
  `docs/findings/14-card-behaviour.md`'s card table still says release 1.3.1 / BL2 0.20.0 / minion 0.23.0,
  which was true before the 10 Oct thermal-v2 update. The driver's own version string is 0.20.0 and is a
  host-module version, not the firmware's; `et-lab-manifest` prints it, which is how the two got conflated.
  E64's manifest records the same driver string and never queried the firmware, so E64's governor behaviour
  was attributed to the 0.20.0 source while the card was already running 0.22.0. **E64's measurements are
  unaffected** — they are measurements — but its source citations point at the wrong build, and today's
  rule-8 source read was done against 0.22.0 for that reason.
- **The power trigger is an average, which fits 0.22.0 and not 0.20.0.** 0.20.0's trigger compares the PMIC's
  *instantaneous* reading; 0.22.0 compares `avg_soc_pwr_mW`, the average. E64 measured the governor's logged
  input behaving as a ~1.3 s running average (65.0–67.9 W while the board read 80–83 W), and today's rings
  show the same at every cap. The average trigger is the 0.22.0 behaviour, so the apparent conflict in the
  findings file resolves in favour of the build the card actually runs.

- **A third correction, to this experiment's own safety reasoning.** The cell-drop filter that shaped this
  grid (`predict_knob.py`, "the power-down loop leaves only when the averaged board power falls under
  1.05 × TDP") describes **BL2 0.20.0**, not the 0.22.0 this card runs. In the 0.22.0 source,
  `check_power_throttle_conditions` (`services/thermal_pwr_mgmt.c:864-926`) is a single-pass `if / else if`
  evaluated once per DM-task pass, with no loop, no re-read and no margin; `POWER_DOWN` dispatches to
  `reduce_minion_operating_point_and_update_pwr_status` (`:1888-1907`), which steps **one** VMIN point and
  returns; and the only floor is `minion_curr_frequency > minion_min_frequency`, which simply stops the
  branch notifying once the clock is at the VMIN LUT's lowest point. A grep for `105`, `TDP_MARGIN` or any
  arithmetic on `tdp_level_mW` over the whole BL2 tree finds nothing, and the same snapshot's changelog carries
  `[SW-21990] fix of retry logic in thermal power monitor to avoid infinite retries` under `[Unreleased]` —
  the loop was removed in this very window. The drop filter stays justified on 0.22.0, for a different reason:
  below a pattern's own 600 MHz power the cell can only ever read the floor (no information about where the
  cap sits) and the firmware's power arm has no step left while the card is over its cap, leaving the host's
  85 W abort as the only remaining guard. **The consequence for E72** (the 600 MHz pin at TDP 0) is in
  `CHANGE-RECORD.md` § "Unresolved risks": on 0.22.0, TDP 0 **pins** the clock at the VMIN floor — 600 MHz on
  this card — and restoring the TDP releases it; it is not a loop that cannot exit. Corrected in A5 after an
  adversarial review; the cells that ran are unaffected, because the filter only ever dropped cells.

## Corrections after the first write-up (27 Oct, desk fix pass)

An adversarial review of this record the same afternoon returned **holds-with-fixes**: the governor move, the
restore, the rule-8 source read, every clock in the tables and the headline causal result all reproduce; 17
faults were raised against the write-up and the arithmetic. All of them are fixed here and in
[`CHANGE-RECORD.md`](../../../../tools/claims-v3/knob/CHANGE-RECORD.md), and the list with its evidence is
amendment **A5** in [the pre-registration](../../../../tools/claims-v3/knob/README.md#a5). No card was
touched, no run was repeated and no measurement changed. The ones that change a number a reader might quote:

| Was | Is | Where |
|---|---|---|
| K3: "22 of 24 in band, rms 13.9" | **12 of 12 cells, rms 11.50** (as registered); the per-run figures are secondary | `results.json .rules.K3` |
| the `BACK` return burst "peak 84.4 W" | **peak 86.61 W**, 12 samples ≥ 85 W, longest consecutive breach 2 (so the registered 3-sample abort correctly did not fire); 84.43 W is that run's `p800_w` | `results_hpl.json`, run `BACK-00-back-randn-r1` |
| "23 set commands" | **39 DM writes** across five sessions | the five `gov.jsonl` |
| "about 20 card-minutes" | **11.4** (8.1 + 1.5 + 1.6 + 0.0 + 0.2) | the five `end.json` |
| error events "6 before the first set" | 6 before the **session**, **18** before the first set, 222 by the last restore, 234 now — and every one of the 234 is the known syndrome, now committed as evidence | `err_events.txt`, `err_count_before.txt` |
| "the control reproduces E64" | the **drift check FAILS**: +25.5 MHz, +2.5 W | the section above |
| the sustained control's +26.9 MHz "prediction error" | a failed drift check, not a model miss | the same |
| the 50 W cell "770.2 MHz / 49.73 W" (A4) | **769.6 MHz / 49.95 W** — A4 quoted an interim reduction run in scratch minutes after the session; the committed reducer (E64's own `reduce_hpl.py`, over the registered last-40 s window) is authoritative | `results.json` |
| six distinct governor settings | **seven** — (65, 62) was used in `s3` | the table above |
| rule 8: "exactly four call sites" | **five**, all listed, none on either set path | `CHANGE-RECORD.md` |
| "pushed before the first card access" | before the first **write** and the first **launch**; read-only identity reads ran 13:55–13:58 | four places, all corrected |
| a Mac home path in `results.json` | the repo-relative path, plus the predictions file's own sha256 | `results.json:5-6` |

## Files

| Path | What |
|---|---|
| `s1/` | the registered session: SMOKE excluded, BURST 24 runs, SUS 2 runs, then the abort. 8.1 card-minutes |
| `s2/` | amendment A3: the sustained cells `s1`'s abort left. One cell measured (`tdp50-thr65-ones`), then the control `randn` cell aborted |
| `s3/` | amendment A4: the lowered-threshold cell and the `BACK` return check. **Exit 0** |
| `smoke2/` | the smoke that proved the set path and its read-back (TDP 65 → 55 → 65 W), before the session |
| `smoke/` | the first smoke attempt, which ended on the stale high-water latch and caused amendment A1 — kept, not deleted |
| `s*/gov.jsonl` | every governor event: the originals, each set with its command/rc/read-back, the restore |
| `s*/runs.jsonl`, `launches.jsonl`, `tel/<run>.jsonl`, `sp/<run>.bin`, `marks.jsonl`, `queries.jsonl` | as E64's, same runner lineage; the SP ring is dumped after **every** run because it holds only ~67 entries |
| `s*/session.json`, `end.json`, `manifest.txt`, `run.log` | the protocol as run, the tools' sha256, the git head, the stop reason, `governor_original` and `governor_restore` |
| `results_hpl.json`, `results.json`, `reduce.txt` | E64's reducer on these sessions, then `reduce_knob.py` scoring the cells and the six rules |
| `err_count_after.txt` | the host kernel log's SP-error-event count after the last run: `234` |
| `err_count_before.txt` | the same count at each gate of the operation (6 before the session, 18 before the first set, 36 before the registered session's first set, 222 by the last restore) |
| `err_events.txt` | **all 234 events**, descriptions and syndromes only, each with its kernel timestamp and wall clock, plus the burst table. Read read-only from the host's kernel ring buffer at 15:14 PDT in the fix pass (no card node opened); it is what makes A2's abort condition checkable rather than asserted |

**One substitution in the committed copies, named here because the field manual forbids quietly altering
evidence:** the lab host's absolute paths were replaced by `<repo>` and `<rundir>` in `*/session.json` and
`smoke2/launches.jsonl`, because this repository is public and those paths carry a lab login. Nothing else was
touched: no measurement, no timestamp, no command, no rc, no hash. The unsubstituted originals are on the lab
host where the runner wrote them. `.jsonl` telemetry over 60 KB is gzipped; the reducer reads `.gz`.

Rebuild (any machine with Python 3, no third-party modules):

```bash
cd docs/reports/data/2026-10-27-e69-governor-knob
python3 ../../../../tools/claims-v3/hpl/reduce_hpl.py s1 s2 s3 --out results_hpl.json > reduce_hpl.txt
python3 ../../../../tools/claims-v3/knob/reduce_knob.py results_hpl.json \
    --predictions ../../../../tools/claims-v3/knob/predictions.json \
    --end s1/end.json s2/end.json s3/end.json --out results.json > reduce.txt
```

## What it changes

- **Q128 § 1 and § 2, the burst gap.** The sentence "the cap causes the burst gap" stops being read off the
  governor's log and becomes a measured response: the gap moves with the cap, in the predicted direction and
  by the predicted amount (rms **11.50 MHz** over the 12 registered cells at four caps; 13.9 MHz over the 24
  runs), and a pattern with no gap at all acquires
  one when the cap goes under its draw.
- **Q128 § 4, the sustained gap.** "A clamp, right in order but with no number to test" now has its number:
  raising the software threshold from 65 to 70 °C takes sustained `ones` from 763.4 to 800.0 MHz and its
  thermal throttle-down events from 11 to 0, with the die moving off its pin at exactly 65 °C. And the cause
  is separately switchable: a 50 W cap leaves the clock near 770 MHz but moves the limiter from 11 thermal
  steps and 0 power steps to 0 and 11.
- **Q128 § 5 item 1** is closed for the cap, and for the threshold raised. Four pieces are left and named:
  the 35 W `zeros` cell did not trigger (a cap near 30 W would); the lowered-threshold cell never reached
  equilibrium in 76 s and needs a longer run or a hot start; both sustained `randn` cells are unmeasured
  because that pattern breaches an 85 W board bound at the card's own settings; and a sustained power-cap
  *speed* result needs a cap under about 48 W, since at 50 W the clock barely moved.
- **The sustained model needs a thermal time constant.** Its two equilibrium predictions that did not involve
  a duty cycle were right (the raised threshold, exactly) and its two duty-cycle predictions were 70 and
  140 MHz low. Both misses come from the same hole: the rule has no heating or cooling time, so it cannot say
  how long a run must be before the clamp is in charge, and it over-stated `ones`' power at 800 MHz by about
  6 W. That is the Levels tab's "temperature term in the governor's power curve" and "the camera's heat-path
  time constants", met from the governor's side.
- **The Levels tab, stop 1.** The top rung is a controlled result. The tab's "Missing" entry for a temperature
  term in the governor's power curve is also touched: the thr-70 cell shows `ones` holding 800 MHz at a die of
  64.2 °C and 54.7 W, which is a direct point on that curve at a known threshold.
- **No pJ moves from "unaccounted" to "accounted".** This experiment is about the governor, not the ledger:
  the 3.837 pJ per random fp32 multiply-add that the bottom-up count does not reach is untouched by it. What
  changes is the confidence in the chain's top rung, which was a correlation this morning and is a controlled
  measurement now.
