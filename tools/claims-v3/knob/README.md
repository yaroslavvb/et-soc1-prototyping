# V3-KNOB: the governor knob test (E69, Q129)

Pre-registration. Written Tue 27 Oct 2026 (week 44), early afternoon PDT, on aifoundry2's card 0.
**Committed and pushed before the first governor write and before the first launch** (`2d35d1b9`,
14:19:40 PDT; first launch 14:20:45.103, first set 14:23:30.707), as the lab's rules require. It did **not**
precede the first *read-only* card access — identity, firmware and `ettelem config` reads ran 13:55–13:58 PDT,
about 22 minutes earlier, and are recorded under G0 of the change record. (Corrected in A5; the original
sentence said "before the first card access".)

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

1. **The power loop's exit must be reachable.** *As registered, and as implemented:* the governor's
   power-down loop leaves only when the averaged board power falls under 1.05 × TDP (or the clock reaches
   300 MHz, which this card's VMIN table has no point for). A cap at or below a pattern's own 600 MHz power
   therefore traps the loop: it is the mechanism that left aifoundry3's governor latched at a boot-time TDP of
   0, and Esperanto filed two of their own incidents against it — a service-processor and master-minion hang
   during power throttling, and a case where the clocks dropped and stayed down through a hot reset. A cell is
   **dropped** unless its 600 MHz board power is at least 2 W below 1.05 × TDP. That drops `ones` at 35 W, and
   every `randn` below 55 W.
   > ⚠️ **[A5, 27 Oct 15:30] This premise is BL2 0.20.0's, not this card's 0.22.0.** At 0.22.0 there is no
   > loop and no 1.05: the check is single-pass, called once per DM-task pass, and steps one VMIN point
   > (`thermal_pwr_mgmt.c:864-926`, `:1888-1907`; `rtos_task/dm_task.c:267`), with the clock simply **pinned
   > at the VMIN floor** once `minion_curr_frequency > minion_min_frequency` fails. The filter is left exactly
   > as it ran — it only ever *dropped* cells, so E69's grid is conservative either way — and the rationale
   > that survives on 0.22.0 is different: such a cell can only read the floor (no information about the cap)
   > while the firmware's power arm has no step left and the card sits over its cap. **Nothing about
   > aifoundry3 or about TDP 0 should be carried from this paragraph**; the corrected statement, and what it
   > means for E72, is in [`CHANGE-RECORD.md`](CHANGE-RECORD.md) § "The power branch at this build".
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
is right). *[A5: that drift check **failed** — the sustained control read 763.4 MHz against E64's 737.9, and
+2.5 W at the same pinned die temperature. See the data README, "The control cells did not reproduce E64".]* The rule's force is entirely in the four moved cells, where the knob changes and the anchor does
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

### A1 — the abort temperature splits in two (27 Oct 2026, written after the first SMOKE attempt ended at
14:20:46 and **committed at 14:23:04 PDT** in `4e0522f1`, before any knob was moved and before the registered
session's first set at 14:24:04. *The header first read "14:25 PDT", which is after its own commit — corrected
in A5.*)

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

### A2 — what an SP error event means here (27 Oct 2026, **committed at 14:23:04 PDT** in `4e0522f1`,
before the registered session. *The header first read "14:29 PDT", after its own commit — corrected in A5.*)

The pre-registration said *"any new `Error Event Detected` line during the session is treated as an abort"*.
Measurement before the session shows that rule would abort everything and measure nothing, so it is replaced
rather than quietly dropped.

**What was seen.** The host kernel log holds `ET 0000:02:00.0: Error Event Detected / Level Critical /
Desc SP Runtime Error / Count 0 / Syndrome Runtime Error Count Beyond Threshold: N` in bursts of six, N
counting up from 1. The first burst (N = 1…6) landed at host uptime 81,805 s, which is **13:56:28 PDT**
(`A5`: the amendment first said ≈13:58; the host booted 26 Oct 15:13:03, and 81,805 s after it is 13:56:28),
alongside a crash of the owner's own one-off `lab-monitor` reader inside `libDM.so`. The second burst
(N = 7…12) landed at 83,263 s, which is **14:20:46.6 PDT** (`A5`: the amendment first said ≈14:27 and placed
it in a 20 s `ettelem sample` — it is six minutes earlier than that and it is a different event). What was
happening at 14:20:46.6: the **first SMOKE attempt closing** — it had aborted at its temperature gate seconds
earlier, before any kernel launched, and its restore was writing the card's own 65 W / 65 °C back. So the
events accompany ordinary host management traffic draining the service processor's error queue; they are not
caused by the knob (the first set came three minutes later) and they are not caused by a workload.
The whole operation's 234 events, each with its wall clock, are committed as `err_events.txt` beside the
data: 37 bursts, one per run or session boundary, every one the same syndrome. `Count` is 0 in every
one. `docs/findings/14-card-behaviour.md` records the same syndrome on this card and notes that its earlier
occurrences "did not stop the card, so the event need not be the hang's".

**The replacement rule.** The kernel log's error-event count is read before the first set and after the last
run and both are reported with the results, as a dated observation. The session aborts on an event whose
**description is anything other than `SP Runtime Error` with `Count 0`**, on any AER or link error, or on a
management query failing — not on another burst of the known one.


### A3 — the `randn` cell at threshold 70 °C aborted on board power and is not retried (27 Oct 2026,
14:32 PDT)

**What happened.** Session `s1` ran 26 of its 31 runs and then ended on a registered abort rule, in the 27th:
`safety:board 85.2 W > 85 W on 3 samples`, in `SUS-03-tdp65-thr70-randn-r1`. The restore ran in the session's
`finally` and read back TDP 65 W and threshold 65 °C, equal to the originals. The card is healthy: firmware
identities unchanged, module uptime 23 h 19 m (so **no SP reset**), idle die mean 54 °C at 24 W and 600 MHz,
no AER, no link error, no new kind of error event.

**Why. ⚠️ The first reading of this, written at 14:34 PDT, was wrong and is corrected in A4 below.** It said
the abort showed that lifting the heat clamp let `randn`'s peak power overshoot. Session `s2` then aborted the
same way on the **control** cell, with nothing moved, which refutes that reading. What stands: the cell's
prediction (600 MHz, held by the 65 W cap) is **not tested**, because the run stopped before its sustained
window; the instantaneous overshoot above the cap is real and is consistent with an average-based trigger and
no hardware fast throttle, but it is a property of sustained `randn` on this card, not of the knob. The abort
bound is **not raised** to get the cell — field manual rule 11 — so the cell is closed unmeasured.

**What follows.** `s2` runs the three sustained cells the abort left and the `BACK` return check, under
`protocol_s2.json`, pre-registered by this amendment and committed before its first launch. Every one of them
*lowers* a limit relative to what has already run, so each reduces board power:
`tdp65-thr65-randn` (the control: the card's own everyday setting, which E64 measured at 600 MHz),
`tdp65-thr62-ones` (threshold lowered), `tdp50-thr65-ones` (cap lowered). The predictions for all three are
unchanged from `predictions.json`; nothing is re-derived. `S-tdp65-thr70-fp32-randn` is reported as
**ABORTED**, and K5's first half, which depended on it, is reported as **not established** rather than scored
either way.


### A4 — the two sustained `randn` aborts are the pattern's own peak power, not the knob (27 Oct 2026,
14:36 PDT)

Session `s2`'s second run, `SUS-00-tdp65-thr65-fp32-randn-r1`, aborted at **board 85.8 W > 85 W on 3
samples** — the **control** cell, governor at the card's own 65 W and 65 °C, nothing moved. So A3's reading of
the first abort is withdrawn: sustained `randn` on this card reaches 85 W of instantaneous board power at its
own default settings, and E69's 85 W bound — chosen below E64's 97 W — stops every sustained `randn` cell,
moved or not. E64 ran the same cell on 23 Oct under its wider bound and it completed at 600 MHz. **Neither
sustained `randn` cell is measured, and E69 concludes nothing about the threshold's effect on `randn`.** The
bound is not raised; `randn` is not retried.

Also measured in `s2` before the abort, and reported as a miss: **`S-tdp50-thr65-fp32-ones` read 770.2 MHz
against 700.0 predicted**, outside its 675–725 band, with a sustained board power of 49.73 W — *under* the
50 W cap. *[A5: those two figures came from an interim reduction run in scratch minutes after the session. The
committed reducer — E64's own `reduce_hpl.py` over the registered last-40 s window — gives **769.6 MHz and
49.95 W**, which is what `results.json` and the data README carry and what should be quoted. Neither the miss
nor its size changes.]* The cap never bound. The prediction assumed `ones` would be trying for 800 MHz in the sustained
regime, where it would draw about 56 W; in fact the heat clamp already holds it near 765 MHz, where it draws
under 50 W. The sustained ladder's one-ratio scaling over-stated `ones`' power by about 6 W, which is the
model error this cell exposes. A cap below about 48 W would bind, and is a cell for another experiment.

`protocol_s3.json` then runs the last registered sustained cell, `tdp65-thr62-ones` (the threshold lowered;
`ones` peaks near 52 W, far below the bound) and the `BACK` return check.


<a id="a5"></a>

### A5 — the correction pass after an independent adversarial review (27 Oct 2026, 15:30 PDT; desk only)

An independent agent of the same workflow reviewed this experiment between **14:44 and 15:05 PDT**: it
re-derived every burst and sustained clock from the committed traces, re-read the rule-8 source line by line,
parsed all five `gov.jsonl`, read the Discord claim back, and took one permitted read-only read of the card at
**14:58:09 PDT** (TDP 65 W, threshold 65 °C, `low_power`, 600 MHz, 519 mV — the originals, card free). Its
verdict: **holds-with-fixes**, with 17 faults, none of them fabrication and none of them a broken safety rule.

This amendment records what it found and what was done. **Nothing was re-run**: no card node was opened for
the fix pass (the one host access was a read-only `dmesg` at 15:14), no measurement changed, and the two
faults that would need a card are closed as open issues rather than fixed.

**Confirmed by the review, and unchanged:** the pre-registration precedes the claim, the first launch, the
first set and every data file; 24 of 24 burst clocks reproduce exactly from the raw traces; all four sustained
cells reproduce; the headline causal result (`ones` at 45 W: 758 and 739.6 MHz with 10 and 9 power-down events
against 0 and 0 at 65 W, 733.3 predicted) reproduces; 39 governor writes, all rc 0, zero read-back mismatches,
all inside the code-enforced bounds; the restore in all five sessions and on the card afterwards; the rule-8
flash-write argument; both corrections to the findings file; and that every failure is reported as a failure.

| # | Fault | What was done |
|---:|---|---|
| M1 | the 1.05 × TDP loop-trap premise behind the cell filter is **BL2 0.20.0**, not the 0.22.0 this card reports — and it was being handed to E72 | the premise is marked where it appears (above, and `predict_knob.py`'s docstring); the 0.22.0 behaviour is derived from source in `CHANGE-RECORD.md` § "The power branch at this build", with the corrected TDP-0 statement for E72 (**pin at the VMIN floor, released by restoring the TDP**, not an inescapable loop) and aifoundry3's latch demoted to an observation whose mechanism is unestablished. The filter itself is untouched: it only dropped cells |
| M2 | the before/after error-event evidence the record promised was half-missing, so A2's abort condition was unverifiable across 228 new events | all 234 events committed as `err_events.txt` (descriptions and syndromes only, with wall clocks and the burst table) plus `err_count_before.txt`; the counts corrected (6 → **18** before the first set, 222 by the last restore); **A2's abort condition shown never met**; A2's own "≈14:27, during a 20 s sample" corrected to 14:20:46.6 at the first SMOKE attempt's close |
| M3 | the `BACK` return burst's "peak 84.4 W" was its `p800_w`; the real peak was 86.61 W with 12 samples at or above E69's own 85 W bound | corrected in the change record and the result, with the 12 samples and the longest consecutive breach (2, so the 3-sample abort correctly did not fire) stated beside the rule. It is the highest board sample of all 29 reduced runs |
| M4 | K3 was scored on the 24 runs, not the 12 registered cells — the permissive direction, undated | `reduce_knob.py` now scores K3 **as registered** (12 cells, cell means) with the per-run figures as a secondary statistic; `results.json` regenerated. **12/12 in band, rms 11.50 MHz**; PASS either way |
| m1 | the sustained control did not reproduce E64 (+25.5 MHz, +2.5 W) and this was logged as a prediction error, not as the registered drift check | a new section in the data README reports the **drift check as FAILED**, with the burst control's matching shift, the identical `die_start`, and the thermal-path reading; every sustained cell is marked **n = 1, no interval** |
| m2 | A1 and A2 are headed 14:25 and 14:29 but both entered in a commit timed 14:23:04; A2's uptime→clock arithmetic was ~6 min out | both headers corrected to the commit time with the original wording named; both conversions redone against the host's own boot time (13:56:28 and 14:20:46.6) |
| m3 | "about 20 card-minutes" | **11.4** (8.1 + 1.5 + 1.6 + 0.0 + 0.2), corrected in both places it was used |
| m4 | "23 set commands" was `s1`'s set-*event* count | **39 DM writes across five sessions** (2 / 3 / 26 / 4 / 4), with `s1`'s breakdown kept |
| m5 | "the originals read before the first set at 14:24:04.235" named the wrong read | the first set of all was `smoke2` 14:23:30.707; the reads preceding it (14:20:45.103, 14:23:23.649, both 65/65) are now named |
| m6 | "committed and pushed before the first card access" was false in four committed places | all corrected to "before the first write and before the first launch", with the 13:55–13:58 read-only access recorded separately |
| m7 | a Mac home path in `results.json` | `reduce_knob.py` records the repo-relative path and the predictions file's sha256; `results.json` regenerated |
| m8 | K4's "predicted 800.0, measured 800.0" sits at the clock ceiling | K4 is presented on the thermal-step count (11 → 0) and the 800-share (1.00), with the 0.0 MHz error named a ceiling artefact |
| m9 | numbers disagreeing between committed files | A4's 770.2 MHz / 49.73 W reconciled to the reducer's 769.6 / 49.95 and dated; the governor table's six settings corrected to **seven**; the "uptime 23 h 19 m" row relabelled as the post-abort ≈14:32 reading, with the 14:42 one (23 h 29 m) separate; rule 8's "exactly four call sites" corrected to **five** |
| m10 | K1's ±5 MHz tolerance and K2's `≥ 775` are looser than the registered text | named as departures at their call sites in `reduce_knob.py` and here. Both rules **FAIL under either reading**, so no verdict turns on them; the implementations are left as they ran |
| m11 | "the number is 36.6 MHz" was identified with the Levels tab's 775-vs-738 *model* gap | the 36.6 MHz is now stated as the **measured 65 → 70 °C sensitivity**, within-session, n = 1 per cell, a **lower bound** because the top cell is at the ceiling — and explicitly not the model gap, which E69 does not close |
| m12 | the required Discord `lockf` wrapper is not visible in the artefacts | recorded as **UNKNOWN, not PASS**, in the change record's "Card lock and claim". The scripts are not edited after the fact — a wrapper added now would prove nothing about what ran then; the lesson is that the wrapper belongs inside the post/edit scripts, where it is auditable |
| m13 | archive-derived paraphrase in a public repo — declared, id-free, number-free, but a judgement call | left in place and **flagged for the hardware owner's ruling** in the change record's final handoff; the editing artefact at the paraphrase ("its own ticket one of their tickets") fixed |

**Not fixed here, and recorded as open because each needs a card:** both sustained `randn` cells remain
unmeasured (the pattern breaches the 85 W bound at the card's own defaults, and the bound was not raised), and
the 62 °C cell remains inconclusive (it never reached equilibrium inside 76 s). K1, K2 and K5 remain
**FAILED as registered**.

**One thing the fix pass found on its own:** `predict_knob.py` prints the digest of the predictions JSON
*without* the trailing newline it writes, so the digest in the change record
(`2894d778…`) is not the committed file's (`7de3fd8f…`). Both are now recorded, and `git log` confirms
`predictions.json` has not been touched since the pre-registration commit.
