# V3-KNOB: the governor knob test (E69, Q129)

Pre-registration. Written Tue 27 Oct 2026 (week 44), early afternoon PDT, on aifoundry2's card 0.
**Committed and pushed before the first card access**, as the lab's rules require.

E64 (Fri 23 Oct, [data](../../docs/reports/data/2026-10-23-e64-horace-power-limit/README.md)) read the
governor's own log through 43 runs and concluded that on a cool die the board's power against the 65 W TDP
level sets the Horace matmul's speed, and on a hot die the 65 °C software threshold does. Everything in that
conclusion is a **correlation**: the two limits were never moved. Q128 §5 lists this as the first open item,
and the model's extrapolated cap table (35–85 W) has never been tested at all.

E69 moves them. The owner authorised it on Tue 27 Oct 2026, under Roman's ET-SoC-1 firmware/OTA field manual;
the change record for the session is [`CHANGE-RECORD.md`](CHANGE-RECORD.md), filled gate by gate with
PASS / FAIL / UNKNOWN. **UNKNOWN is not PASS.**

## What is set, and what is never touched

Two fields, both of which live in service-processor RAM and return to their defaults at an SP reset:

| Knob | Command | Range the firmware accepts | Range E69 uses |
|---|---|---|---|
| static TDP level | `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26), `-l` | 0–75 W | **35–65 W** (never above the card's own default) |
| software thermal threshold | `DM_CMD_SET_MODULE_TEMPERATURE_THRESHOLDS` (22), `-e` | any `uint8`, no range check | **62–70 W** → °C |

Never, in this experiment: `SET_FREQUENCY`, `SET_MODULE_VOLTAGE`, `SET_MODULE_ACTIVE_POWER_MANAGEMENT`,
`SET_STATS_RUN_CONTROL` (so no `ettelem --reset-ms`, which disables the SP statistics trace), any trace reset,
any firmware update, any PMIC command, any card or SoC reset, any PCIe or driver action. `run_knob.py` refuses
a protocol whose governor cells fall outside the table above, before the planner ever reaches the card.

## Why these cells and no others

Each cell is one (TDP, threshold, operand pattern). Two filters cut the grid down before anything ran, both
from the Esperanto archive's own incident record (the E64 archive review, held outside this repository, read 27 Oct;
paraphrased, with no archive numbers or ids):

1. **The power loop's exit must be reachable.** The governor's power-down loop leaves only when the averaged
   board power falls under 1.05 × TDP (or the clock reaches 300 MHz, which this card's VMIN table has no point
   for). A cap at or below a pattern's own 600 MHz power therefore traps the loop: it is the mechanism that
   left aifoundry3's governor latched at a boot-time TDP of 0, and Esperanto filed two of their own incidents
   against it — a service-processor and master-minion hang during power throttling, and a case where the
   clocks dropped and stayed down through a hot reset. A cell is **dropped** unless its 600 MHz board power is
   at least 2 W below 1.05 × TDP. That drops `ones` at 35 W, and every `randn` below 55 W.
2. **The thermal loop's exit must stay as reachable as it already is.** A *lowered* threshold that puts a
   pattern's 600 MHz die above it would make the thermal loop spin for the whole run; cells like that are
   dropped (`ones` at 62 °C survives, `randn` does not, so the lowered-threshold arm is `ones` only). At the
   card's **default** 65 °C this condition already holds for `randn` every day — E64 measured it — so it is a
   baseline, not a new hazard, and those cells stay.

The cap is **never raised above 65 W**: the archive's service-processor hang was seen with card power pinned
just above the firmware's 75 W catastrophic threshold, and `randn` at 800 MHz on this card already draws 83 W.
Lowering is the safe direction and it answers the question, so lowering is all E69 does.

## The cells, and what the model predicts for each

Frozen in [`predictions.json`](predictions.json) by
`predict_knob.py --figures docs/reports/data/2026-10-23-e64-horace-power-limit/figures.json`
(sha256 of that file printed by the tool and recorded in the change record). **No E69 measurement enters any
number below**: they come from E64's fitted per-pattern power ladders, its governor (a first-order average of
board power, τ = 1.3 s, compared with the level once per 0.24 s pass, one VMIN point per pass) and its thermal
line (die = 41.88 + 0.4696 °C per W of board power).

### BURST — one 6 s launch from a cool die (≤ 55 °C), 1,024 minions, 2 passes per cell

The mean clock from 1.5 s to the end, which is what E64 measured and what its model was validated against
(3.3 MHz rms over 26 runs).

| cell | TDP | pattern | predicted mean MHz | band | predicted TFLOPS | E64 measured at 65 W |
|---|---:|---|---:|---|---:|---|
| B-tdp65-fp32-zeros | 65 | zeros | 800.0 | 775–800 | 12.29 | 800, 800 |
| B-tdp65-fp32-ones | 65 | ones | 800.0 | 775–800 | 12.29 | 800, 800 |
| B-tdp65-fp32-a_ones_b_randn | 65 | a_ones_b_randn | 742.9 | 718–768 | 11.41 | 740.4, 742.3 |
| B-tdp65-fp32-randn | 65 | randn | 704.8 | 680–730 | 10.83 | 706, 713.5 |
| B-tdp55-fp32-zeros | 55 | zeros | 800.0 | 775–800 | 12.29 | — |
| B-tdp55-fp32-ones | 55 | ones | 800.0 | 775–800 | 12.29 | — |
| B-tdp55-fp32-a_ones_b_randn | 55 | a_ones_b_randn | **681.0** | 656–706 | 10.46 | — |
| B-tdp55-fp32-randn | 55 | randn | **633.3** | 608–658 | 9.73 | — |
| B-tdp45-fp32-zeros | 45 | zeros | 800.0 | 775–800 | 12.29 | — |
| B-tdp45-fp32-ones | 45 | ones | **733.3** | 708–758 | 11.27 | — |
| B-tdp45-fp32-a_ones_b_randn | 45 | a_ones_b_randn | **600.0** | 600–625 | 9.22 | — |
| B-tdp35-fp32-zeros | 35 | zeros | **795.2** | 770–800 | 12.22 | — |

The three cells that carry the causal claim:

- **`ones` at 45 W.** At the card's own cap `ones` never throttles — 800 MHz in both E64 passes, 0 power
  steps. Lower the cap under its 800 MHz draw and the model says it must throttle, to 733 MHz. A pattern that
  has never once been limited becoming limited, with the predicted number, is the controlled result the top
  rung of the chain has been missing.
- **`a_ones_b_randn` and `randn` at 55 W.** Both already throttle at 65 W. The model says each loses a further
  62 and 72 MHz. A monotone, quantitative response of the gap to the cap.
- **`zeros` at 35 W.** The lowest-power pattern on the card draws 35.3 W at 800 MHz. Put the cap just under
  that and even `zeros` must give up a little speed, 795 MHz. If `zeros` holds 800 MHz here the model's power
  trigger is wrong about which number it compares.

### SUS — nine back-to-back 8 s launches, the mean over the last 40 s, 1 pass per cell

Sustained predictions use the ladder differently, because a sustained run settles at one or two VMIN points
and the die reaches equilibrium. Rule, fixed here: a clock is **reachable** when its own sustained board power
is at or under the cap and **cool** when its die on E64's thermal line is at or under the threshold; the
governor sits at the highest cool-and-reachable point `f_lo`, and the time-average is pulled toward the point
above it by the duty cycle `w = (threshold − die(f_lo)) / (die(f_hi) − die(f_lo))`, clipped to [0, 1], with
`w = 0` when `f_hi` is over the cap by more than 2 W and `w = 0.5` when it is over by less (the governor's
power branch has no hysteresis, so it dwells there on alternate passes). Sustained powers are the pattern's
cool-die ladder scaled by one ratio, its own sustained mean power over its sustained mean clock.

| cell | TDP | threshold | pattern | predicted mean MHz | band | shape | predicted die | predicted board |
|---|---:|---:|---|---:|---|---|---:|---:|
| S-tdp65-thr65-fp32-ones | 65 | 65 | ones | 736.5 | 700–800 | heat clamp 700↔800, duty 0.365 | 63.2 °C | 45.4 W |
| S-tdp65-thr65-fp32-randn | 65 | 65 | randn | 600.0 | 600–625 | no point is cool: the boot point | 67.4 °C | 54.4 W |
| S-tdp65-thr70-fp32-ones | 65 | **70** | ones | **800.0** | 775–800 | top point, cool and under the cap | 68.1 °C | 55.9 W |
| S-tdp65-thr70-fp32-randn | 65 | **70** | randn | 600.0 | 600–625 | held at 600: 700 is over the cap by 6.2 W | 67.4 °C | 54.4 W |
| S-tdp65-thr62-fp32-ones | 65 | **62** | ones | **649.8** | 600–700 | heat clamp 600↔700, duty 0.498 | 60.8 °C | 40.3 W |
| S-tdp50-thr65-fp32-ones | **50** | 65 | ones | **700.0** | 675–725 | held at 700: 800 is over the cap by 5.9 W | 63.2 °C | 45.4 W |

Q128 says of the sustained gap that it "is a clamp, right in order but with no number to test". These four
moved cells are the numbers:

- **`ones` at threshold 70 °C: 736 → 800 MHz, the whole sustained gap closes.** Its 800 MHz die sits at 68 °C,
  under the raised threshold, and its 800 MHz power at 56 W, under the cap. If the clamp is thermal this cell
  must run flat out; if the sustained gap has any other cause it cannot.
- **`randn` at threshold 70 °C: still 600 MHz, but for a different reason.** Its 600 MHz die, 67 °C, is now
  *under* the threshold, so the thermal branch should stop firing altogether — while 700 MHz still draws 6 W
  more than the cap. Same clock, cause flipped from heat to power: the registered test is that the thermal
  steps in the governor's log fall to 0 and power steps appear.
- **`ones` at threshold 62 °C: 736 → 650 MHz.** The clamp tightened by 3 °C should cost 86 MHz.
- **`ones` at cap 50 W: 736 → 700 MHz, by power rather than heat.** The same pattern, the same temperature, a
  lower cap: a heat clamp turned into a power cap, with the step kind in the log changing with it.

**Honest limitation, stated before the runs.** The sustained rule's level is anchored on each pattern's own
E64 sustained mean, so the two **control** cells are partly self-fitting and are not an independent test of
the rule (they do reproduce E64 to 1.4 MHz, which is a check that the card has not drifted, not that the rule
is right). The rule's force is entirely in the four moved cells, where the knob changes and the anchor does
not. The burst predictions carry no such circularity: `simulate()` is E64's own validated call and the control
cells are a genuine out-of-sample check of it against E64's measurements.

### SMOKE and BACK

`SMOKE` (two 2 s launches, `--only SMOKE`, not analysed) proves the set path and its read-back work before the
registered session. `BACK` is the return check: the originals restored, one 6 s `randn` burst, which must show
normal stepping and the default TDP in the governor's log.

## Decision rules (frozen)

| Rule | Statement | How it is scored |
|---|---|---|
| **K1** | *The cap moves the speed gap.* Across the BURST cells of one pattern, the mean clock is non-decreasing in the TDP level, strictly increasing wherever the model predicts a difference above 25 MHz. | pass/fail per pattern; the rule passes only if every pattern with more than one cell passes |
| **K2** | *A pattern that never throttled, throttles.* `ones` at 45 W has a mean clock below 775 MHz and at least one power step in the governor's log, where at 65 W it has 800 MHz and none. | pass/fail |
| **K3** | *The cap table is right.* At least 10 of the 12 BURST cells land inside their registered bands, and the signed error over all 12 has rms at most 25 MHz. | counts + rms |
| **K4** | *The sustained clamp is thermal.* `ones` at threshold 70 °C has a sustained mean clock of at least 775 MHz, against 736.5 predicted and about 738 measured at 65 °C. | pass/fail |
| **K5** | *The sustained cause can be switched.* `randn` at threshold 70 °C keeps a sustained mean within 25 MHz of 600 while its thermal steps fall to 0 and its power steps rise above 0; and `ones` at cap 50 W falls to 675–725 MHz with power steps appearing and thermal steps falling. | pass/fail per half |
| **K6** | *Restore.* After the last run the firmware reports exactly the TDP and threshold read before the first set, and the `BACK` burst shows the card stepping normally. | pass/fail; **a fail is reported as a fail and escalated** |

A rule that fails is reported as failed. Nothing here is re-derived after the fact: `reduce_knob.py` reads
`predictions.json` and scores what it finds.

## Abort rules (frozen)

The session stops, restores the originals and reports, on any of:

- a die mean at or above **72 °C**, or board power at or above **85 W**, on 3 consecutive samples
  (`safety` in `protocol.json`; both are below the lab's 90 °C rule and below the firmware's 75 W/75 °C
  catastrophic thresholds);
- a governor set whose read-back disagrees with what was asked (`governor_readback_mismatch`);
- the firmware's configuration drifting from the run's own target between the set and the run's end queries
  (`config_drifted`);
- the card's configuration becoming unreadable at any point (`governor_config_unreadable`);
- any other user appearing on the card or the host (`check_others`), two failed kernel launches, the sampler
  refusing to start, or the 110 card-minute cap.

On an abort the card lock is **kept** until the restore has been read back. If the restore fails or the card
stops answering: stop, keep the claim, write it up, and alert with `notify.py --unblock`. **No card reset** —
that is forbidden here even though it would restore the defaults.

## The restore procedure

1. `read_config()` before the first set records the originals and writes them to `gov.jsonl` as
   `{"event": "original"}`; if it cannot be read the session refuses to start.
2. Every set writes `{"event": "set", "asked", "before", "after", "sent": [{cmd, rc, timestamps}]}`.
3. The session's `finally` — on success, on an abort, on an unexpected exception — sends both originals back,
   reads them, and writes `{"event": "restore", "ok", "original", "after"}`. A restore that does not read back
   equal turns the session's exit into an error, whatever happened before it.
4. `BACK` then runs one 6 s `randn` burst at the restored settings and its governor log is read for normal
   stepping and the default TDP.
5. `end.json` carries `governor_original` and `governor_restore` so the final state is in the data, not only
   in a log line.

## Files

| Path | What |
|---|---|
| `predict_knob.py` | freezes the per-cell predictions from E64's model; read-only, no card |
| `predictions.json` | the frozen predictions, their bands, the dropped cells and why |
| `protocol.json` | the session as run: blocks, cells, each cell's governor target, safety, caps |
| `run_knob.py` | the runner: E64's `run_hpl.py` with the governor set, read-back, per-run guard and restore |
| `reduce_knob.py` | measured against predicted per cell, the six rules, the governor's log per run |
| `CHANGE-RECORD.md` | the field manual's change record, gate by gate, with the set/read-back log |

`run_knob.py` is a copy of `tools/claims-v3/hpl/run_hpl.py` (E64) with exactly these changes, dated 27 Oct
2026: the governor bounds and their constants; `Run.gov_tdp`/`gov_thr` from each cell's `governor` block, with
the bounds enforced in `Run.check()` so a bad protocol cannot reach the card; `read_config`, `set_governor` and
`restore_governor`; a set before each run's gate; the per-run configuration guard comparing against that run's
own target instead of a hard-coded 65; the originals read under the lock before the first set; the restore in
the session's `finally`; `iso_ms` for the change record's timestamps. E64's own tool is untouched, so E64's
data still rebuilds from it.

## Amendments

Anything that departs from the above is added here, dated, with its reason, and committed before it is relied
on.

### A1 — the abort temperature splits in two (27 Oct 2026, 14:25 PDT, after the first SMOKE attempt, before
any knob was moved)

**What happened.** The first `SMOKE` attempt ended on its first run with `safety:die 73 C >= 72 C`, before any
governor field had been changed (the only set was the card's own 65 W / 65 °C, and the restore read back
correct). The card was **not** hot: a 20 s idle sample under the card lock immediately afterwards read a die
**mean of 47 °C** in all 20 samples, board 22.0–22.3 W, 600 MHz. The 73 came from
`temp_c.minshire[2]`, the **high-water mark**, which runs since the last `pvt_hilo_reset` — the field manual
says so in as many words ("latched extrema span earlier jobs, not just the current test") — and this
experiment deliberately never sends a reset, because the only way to clear it (`ettelem --reset-ms`) also
silently disables the SP's statistics trace. Other stale latches read at the same time: io-shire high 71 °C,
`sp.minion_c` max 71 °C, `sp.board_max_w` **88.54 W**. All predate this session; the most recent heating on
this card was E66's cooling cycles.

**The change.** `abs_stop_c` (72 °C) now applies to the **die mean** — the number the governor itself
compares, the number E64 reported, and the number the lab's 90 °C rule is about. The latched high-water mark
gets its own bound, the new `high_stop_c` = **80 °C**: it is not a live reading and cannot serve as the live
abort, but a genuinely new single-sensor excursion past 80 is still worth stopping for. The board-power abort
is unchanged at 85 W on 3 consecutive samples.

**Said plainly:** on the mean this is *tighter* than E64, which used 85 °C; on the latch it is *looser* than
the 72 °C I registered an hour earlier. The loosening is confined to a field that reports history, and its
reason is the field manual's own warning about that field. Nothing about the predictions, the cells, the rules
or the restore changes.

### A2 — what an SP error event means here (27 Oct 2026, 14:29 PDT, before the registered session)

The pre-registration said *"any new `Error Event Detected` line during the session is treated as an abort"*.
Measurement before the session shows that rule would abort everything and measure nothing, so it is replaced
rather than quietly dropped.

**What was seen.** The host kernel log holds `ET 0000:02:00.0: Error Event Detected / Level Critical /
Desc SP Runtime Error / Count 0 / Syndrome Runtime Error Count Beyond Threshold: N` in bursts of six, N
counting up from 1. The first burst (N = 1…6) landed at host uptime 81,805 s (≈13:58 PDT), alongside a crash
of the owner's own one-off `lab-monitor` reader inside `libDM.so`. The second burst (N = 7…12) landed at
83,263 s (≈14:27 PDT) — during **this session's own 20 s `ettelem sample`**, with no kernel launched and no
governor field moved. So the events accompany ordinary host telemetry reads draining the service processor's
error queue; they are not caused by the knob and they are not caused by a workload. `Count` is 0 in every
one. `docs/findings/14-card-behaviour.md` records the same syndrome on this card and notes that its earlier
occurrences "did not stop the card, so the event need not be the hang's".

**The replacement rule.** The kernel log's error-event count is read before the first set and after the last
run and both are reported with the results, as a dated observation. The session aborts on an event whose
**description is anything other than `SP Runtime Error` with `Count 0`**, on any AER or link error, or on a
management query failing — not on another burst of the known one.
